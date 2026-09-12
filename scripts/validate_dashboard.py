#!/usr/bin/env python3
"""
Dashboard <-> v26 lock consistency validator.

Fails loudly when the published dashboard disagrees with the authoritative
sources:

  workbook   TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx
  analysis   06_FINAL_ANALYSIS_V26/{01_DATA,03_RESULTS}
  dashboard  dashboard/  (canonical, hand-edited source)

This validates SOURCE content only. dashboard/ no longer carries a committed
v26/ mirror or a docs/ generated copy -- scripts/build_site.py builds both
the v26 download mirror and the deployable artifact fresh on every build
(see .github/workflows/deploy-pages.yml), so there is no separate mirror
copy left to drift out of sync and no corresponding check for it here.

Design note
-----------
The previous validator only asserted that CORRECT strings were PRESENT. That is
satisfiable while stale values sit right next to the new ones, which is exactly
how "k = 6" and "k = 11" came to coexist on the same page. Every check here is
one of:

  (a) ABSENCE  - a withdrawn/obsolete value must not appear as a live claim
  (b) DERIVED  - the expectation is read from the v26 CSVs, not hardcoded
  (c) STRUCTURAL - a property of the code (e.g. no fallback maps to High risk)

Withdrawn numbers are permitted only inside explicitly-labelled withdrawal
prose; check (a) enforces that distinction rather than banning the digits.

Usage:  python3 scripts/validate_dashboard.py [-v]
Exit:   0 all checks passed, 1 any failure
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
DATA = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA"
RESULTS = ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS"

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[1m", "\033[0m"
)

_failures: list[str] = []
_passes = 0


def check(name: str, ok: bool, detail: str = "") -> bool:
    global _passes
    if ok:
        _passes += 1
        print(f"{GREEN}PASS{RESET} | {name}")
        if detail and VERBOSE:
            print(f"       {DIM}{detail}{RESET}")
    else:
        _failures.append(name)
        print(f"{RED}FAIL{RESET} | {name}")
        for line in (detail or "(no detail)").splitlines():
            print(f"       {RED}{line}{RESET}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Load sources
# ─────────────────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


HTML = (DASH / "index.html").read_text(encoding="utf-8")
APP = (DASH / "app.js").read_text(encoding="utf-8")
DATA_JS = (DASH / "data.js").read_text(encoding="utf-8")
TRANS = (DASH / "translations.js").read_text(encoding="utf-8")
ALL_UI = HTML + "\n" + APP + "\n" + TRANS

MASTER = read_csv(RESULTS / "master_reconciled_results_v26.csv")
BY_ID = {r["analysis_id"]: r for r in MASTER}


def studies_data() -> list[dict]:
    """Parse window.STUDIES_DATA out of data.js without a JS engine."""
    start = DATA_JS.index("window.STUDIES_DATA = [") + len("window.STUDIES_DATA = ")
    depth, i, in_str, esc = 0, start, False, False
    while i < len(DATA_JS):
        ch = DATA_JS[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(DATA_JS[start:i + 1])
        i += 1
    raise RuntimeError("could not parse window.STUDIES_DATA")


STUDIES = studies_data()


def strip_withdrawal_prose(text: str) -> str:
    """
    Remove blocks that explicitly present a value as withdrawn/superseded, so
    absence checks target LIVE claims only. A block is any HTML element whose
    text is introduced by withdrawal language.
    """
    markers = (
        "Withdrawn", "withdrawn", "Earlier releases", "previously displayed",
        "previously offered", "previously let readers", "Not modelled in v26",
        "came from the withdrawn", "has been withdrawn", "Removed", "superseded",
        "Superseded",
        # explicit statements that a result does NOT exist are not live claims
        "no k = 11", "not estimable", "is NOT estimable", "no pooled result exists",
    )
    out = []
    for para in re.split(r"(?=<(?:li|p|div|td|h2|h3|h4)\b)", text):
        if any(m in para for m in markers):
            continue
        out.append(para)
    return "".join(out)


WITHDRAWAL_MARKERS = (
    "Withdrawn", "withdrawn", "Earlier releases", "previously displayed",
    "previously offered", "previously let readers", "Not modelled in v26",
    "came from the withdrawn", "has been withdrawn", "Removed", "superseded",
    "Superseded", "no k = 11", "not estimable", "is NOT estimable",
    "no pooled result exists",
)


def strip_withdrawal_lines(text: str) -> str:
    """
    Line-based equivalent of strip_withdrawal_prose for .js sources.

    strip_withdrawal_prose splits on HTML element boundaries, which do not exist
    in translations.js or app.js. Applied to those files it collapses the whole
    source into one "paragraph", so a single occurrence of the word "withdrawn"
    anywhere blanks the ENTIRE file and every absence check over it silently
    passes. That is exactly what happened: the first version of
    t_no_pre_correction_sufentanil_values was blind to both .js files. Strip per
    line instead, since each translation key and each log line is one line.
    """
    return "\n".join(
        ln for ln in text.splitlines()
        if not any(m in ln for m in WITHDRAWAL_MARKERS)
    )


def translations_by_locale() -> dict[str, str]:
    """
    Split translations.js into per-locale text. The file contains more than one
    translation object, each with its own `en:` / `sv:` section, so accumulate
    by locale rather than assuming a single pair.
    """
    out: dict[str, list[str]] = {"en": [], "sv": []}
    current = None
    for ln in TRANS.splitlines():
        m = re.match(r"^\s{0,4}(en|sv)\s*:\s*\{", ln)
        if m:
            current = m.group(1)
            continue
        if current:
            out[current].append(ln)
    return {k: "\n".join(v) for k, v in out.items()}


LIVE_UI = strip_withdrawal_prose(ALL_UI)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Provenance and identifiers
# ─────────────────────────────────────────────────────────────────────────────

def t_prospero():
    obsolete = "CRD42024560773"
    correct = "CRD420251090635"
    hits = []
    for p in DASH.rglob("*"):
        if not (p.is_file() and p.suffix in {".html", ".js", ".json", ".csv", ".md"}):
            continue
        # Audit trails must be able to name the superseded ID as a corrected
        # OLD STATE; that is the record of the fix, not a live claim.
        if "06_AUDIT" in p.parts and p.suffix == ".md":
            continue
        if obsolete in p.read_text(encoding="utf-8", errors="ignore"):
            hits.append(str(p.relative_to(ROOT)))
    ok = not hits and correct in HTML
    check("Obsolete PROSPERO ID absent; CRD420251090635 present", ok,
          f"obsolete found in: {hits}" if hits else f"correct ID present: {correct in HTML}")


def t_no_v20_source_label():
    bad = [m for m in re.findall(r"[^<>\n]{0,60}Master v20[^<>\n]{0,40}", ALL_UI)]
    bad += [m for m in re.findall(r"Audited Reconciled Master[^<>\n]{0,30}", ALL_UI)
            if "v26" not in m]
    check("No 'Master v20' source label presented as current", not bad, f"found: {bad}")


def t_provenance_block():
    need = [
        "TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx",
        "CRD420251090635",
        "StataNow 19.5 BE",
    ]
    missing = [n for n in need if n not in HTML]
    has_footer = 'id="dashboard-provenance"' in HTML
    check("Visible provenance statement (source / statistics / registration)",
          not missing and has_footer,
          f"missing={missing} footer={has_footer}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Pooled results must match the final Stata run
# ─────────────────────────────────────────────────────────────────────────────

def t_primary_matches_stata():
    r = BY_ID["OP24_PRIM_COMB"]
    k = int(r["k"])
    md = round(float(r["estimate"]), 2)
    lo = round(float(r["ci_low"]), 2)
    hi = round(float(r["ci_high"]), 2)
    p = round(float(r["p_value"]), 3)
    i2 = round(float(r["i2"]), 1)

    rows = [x for x in read_csv(DATA / "opioid_24h_primary.csv") if x["inc_primary"] == "1"]
    n = sum(int(x["n_i"]) + int(x["n_c"]) for x in rows)

    probs = []
    if len(rows) != k:
        probs.append(f"locked dataset has {len(rows)} primary rows, Stata reports k={k}")
    for label, needle in [
        (f"k={k}", f"k = {k}"), ("MD", f"{abs(md):.2f}"), ("CI low", f"{abs(lo):.2f}"),
        ("CI high", f"{hi:.2f}"), ("p", f"{p:.3f}"), ("I2", f"{i2}"), ("N", f"{n}"),
    ]:
        if needle not in HTML.replace("−", "-").replace("&minus;", "-"):
            probs.append(f"{label} value '{needle}' not displayed")
    check(f"Primary 24-h matches Stata (k={k}, N={n}, MD={md}, CI[{lo},{hi}], p={p}, I2={i2}%)",
          not probs, "\n".join(probs))


def t_displayed_k_and_n():
    """k and N shown for each headline analysis must be derivable from the locked data."""
    specs = [
        ("Primary 24-h", DATA / "opioid_24h_primary.csv", "inc_primary", "OP24_PRIM_COMB"),
        ("Target A 48-h", DATA / "target_A_48h.csv", "include_strict", "TA_STRICT"),
        ("Target B 72-h", DATA / "target_B_72h.csv", "include_strict", "TB_STRICT_EXACT"),
        ("Target C pain", DATA / "target_C_pain24h.csv", "include_strict", "TC_REST_PAIN24"),
    ]
    probs = []
    for label, path, flag, aid in specs:
        rows = [x for x in read_csv(path) if x.get(flag) == "1"]
        k_expected = int(BY_ID[aid]["k"])
        if len(rows) != k_expected:
            probs.append(f"{label}: {len(rows)} strict rows vs Stata k={k_expected}")
        n = sum(int(x["n_i"]) + int(x["n_c"]) for x in rows)
        n_fmt = {f"{n}", f"{n:,}"}
        if not any(f in HTML for f in n_fmt):
            probs.append(f"{label}: N={n} not displayed anywhere")
    check("Displayed k and N reconcile with the locked datasets", not probs, "\n".join(probs))


def t_hero_summary_cards_match_detail():
    """
    The "Verified Evidence Synthesis Summary" hero card grid (top of the
    primary tab) restates k/N/estimate for six analyses that are ALSO
    described in detail further down the same page (the Target C/D/E/F
    forest-plot narratives). An audit found the hero grid disagreed with
    its own detail section on five of these N values simultaneously (pain
    124 vs 158, flatus 494 vs 596, rescue 333 vs 312, intraop remifentanil
    504 vs 890, PCA 644 vs 614) -- each wrong hero-card N had sat next to
    a correct N shown elsewhere on the very same page, undetected because
    a plain "is the correct value shown anywhere" check is satisfied by
    the OTHER (correct) location while the wrong one persists. This
    check specifically re-derives each hero-card N from source and also
    bans the exact stale values found, so this class of bug cannot
    silently return.
    """
    probs = []

    # Pain (Target C) and flatus (Target E): derivable directly from the
    # v34 outcome data by summing analysed n across the named studies.
    outcome_path = (ROOT / "TEAS EA Verification" / "v34_reconciliation" /
                    "data" / "v34_outcome_data.csv")
    if outcome_path.exists():
        outcome_rows = read_csv(outcome_path)

        def analysed_n(study: str, outcome_substr: str) -> int:
            total = 0
            for r in outcome_rows:
                if r.get("Canonical study") == study and outcome_substr.lower() in r.get("Outcome/result", "").lower():
                    ai = r.get("Analyzed n intervention") or "0"
                    ac = r.get("Analyzed n comparator") or "0"
                    try:
                        total += int(float(ai)) + int(float(ac))
                    except ValueError:
                        pass
            return total

        pain_n = analysed_n("Xing 2022", "Rest pain VAS") + analysed_n("Liu 2021", "VAS at rest")
        if pain_n != 158:
            probs.append(f"Pain at ~24h (Target C): re-derived N={pain_n}, expected 158")

        flatus_studies = [("Zhou 2025", "flatus"), ("Yang 2020", "flatus"), ("Yang 2024", "flatus"),
                          ("Xing 2022", "flatus"), ("Lu 2022", "flatus"), ("Ng 2013", "flatus")]
        flatus_n = sum(analysed_n(s, o) for s, o in flatus_studies)
        if flatus_n != 596:
            probs.append(f"Time to first flatus (Target E): re-derived N={flatus_n}, expected 596")

    # Rescue opioid (Target F) and intraoperative remifentanil (Target F):
    # derivable from the same target_F_exploratory.csv the detail section
    # itself reports from.
    tf_path = DATA / "target_F_exploratory.csv"
    if tf_path.exists():
        tf_rows = read_csv(tf_path)
        rescue_studies = {"Xie 2014", "Yu 2020", "Tu 2024", "Zhou 2025"}
        rescue_n = sum(int(r["n_i"]) + int(r["n_c"]) for r in tf_rows
                       if r["target"] == "F-rescue-opioid" and r["study"] in rescue_studies)
        if rescue_n != 312:
            probs.append(f"Rescue analgesia (Target F): re-derived N={rescue_n}, expected 312")

    # Every stale value found in the same audit pass, banned outright so a
    # future edit to one card cannot silently reintroduce a mismatch with
    # its own detail section.
    stale = {
        "N = 124": "Pain at ~24h hero card (correct: N = 158)",
        "N = 494": "Time to first flatus hero card (correct: N = 596)",
        "N = 333": "Rescue analgesia hero card (correct: N = 312)",
        "N = 504": "Intraoperative remifentanil hero card (correct: N = 890)",
        "N = 644": "PCA behavior hero card (correct: N = 614)",
    }
    for needle, why in stale.items():
        if needle in HTML:
            probs.append(f"stale value still present: {needle} ({why})")

    check("Hero summary cards' N values are re-derivable from source and no stale duplicate remains",
          not probs, "\n".join(probs))


def t_primary_stratum_comparators_not_swapped():
    """
    The strict primary TEAS stratum is entirely sham-controlled; the strict
    primary EA stratum is entirely usual-care/open-label controlled (audited
    and confirmed correct earlier in this review). A reviewer's easiest way
    to catch a comparator mix-up is inside each stratum's own card: the TEAS
    card should never describe ITS OWN comparator as usual care, and the EA
    card should never describe ITS OWN comparator as sham. This does not ban
    the words elsewhere on the page -- e.g. Wong 2006 genuinely is a
    sham-controlled EA trial reported outside the strict primary set, and
    that mention is correct -- only inside these two specific cards.
    """
    probs = []
    teas_start = HTML.find("Primary Stratum 1: TEAS vs Sham")
    ea_start = HTML.find("Primary Stratum 2: EA vs")
    combined_start = HTML.find("Supporting Combined Synthesis (k=7, N=676)", ea_start)
    if teas_start == -1 or ea_start == -1 or combined_start == -1 or not (teas_start < ea_start < combined_start):
        probs.append("could not locate all three primary stratum card boundaries to scope this check")
    else:
        teas_card = HTML[teas_start:ea_start]
        ea_card = HTML[ea_start:combined_start]
        if re.search(r"usual care", teas_card, re.I):
            probs.append("TEAS stratum card describes its own comparator as usual care")
        if re.search(r"\bsham\b", ea_card, re.I):
            probs.append("EA stratum card describes its own comparator as sham")
    check("Primary TEAS/EA stratum cards never describe their own comparator as the other stratum's",
          not probs, "\n".join(probs))


def t_target_b_not_pooled():
    r = BY_ID["TB_STRICT_EXACT"]
    ok = int(r["k"]) == 1 and "Not pooled" in r["model"]
    shown = "NOT POOLED" in HTML.upper()
    check("Target B 0-72 h is k=1 and labelled NOT POOLED (no forced meta-analysis)",
          ok and shown, f"stata k={r['k']} model={r['model']!r}; 'NOT POOLED' in HTML={shown}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Study-set composition rules
# ─────────────────────────────────────────────────────────────────────────────

def t_target_a_membership():
    rows = read_csv(DATA / "target_A_48h.csv")
    strict = {x["study"] for x in rows if x["include_strict"] == "1"}
    sens = {x["study"] for x in rows if x["include_sensitivity"] == "1"}
    probs = []
    for must in ("Chen 2020", "Zhang 2023", "An 2014"):
        if must not in strict:
            probs.append(f"strict 48-h missing {must}")
    for never in ("He 2026 (breast/WJCO)", "Wong 2006"):
        if never in strict:
            probs.append(f"strict 48-h must not contain {never}")
    if "Xie 2014" in strict:
        probs.append("Xie 2014 must be sensitivity/broader only, not strict")
    if "Xie 2014" not in sens:
        probs.append("Xie 2014 missing from the broader/sensitivity 48-h set")
    if "TA_EXCL_AN" not in BY_ID:
        probs.append("mandatory 'exclude An 2014' sensitivity analysis absent")
    check("Target A strict = Chen 2020 / Zhang 2023 / An 2014; Xie 2014 sensitivity-only; "
          "He 2026 WJCO and Wong 2006 excluded", not probs, "\n".join(probs))


def t_no_old_five_study_48h():
    """The retired five-study 48-h result must not be served or linked."""
    probs = []
    stale = DASH / "stata_48h_opioid_synthesis_data.csv"
    if stale.exists():
        probs.append(f"{stale.relative_to(ROOT)} is still served")
    for ref in ("stata_48h_opioid_synthesis", "stata_consensus_synthesis_data",
                "stata_audited_synthesis", "stata_secondary_synthesis_data"):
        if ref in HTML or ref in APP:
            probs.append(f"dashboard still references {ref}")
    check("Retired five-study 48-h and consensus datasets are neither served nor linked",
          not probs, "\n".join(probs))


def t_target_b_membership():
    rows = read_csv(DATA / "target_B_72h.csv")
    present = {x["study"] for x in rows}
    strict = {x["study"] for x in rows if x["include_strict"] == "1"}
    probs = []
    for never in ("Zhang 2025", "Xie 2014"):
        if never in present:
            probs.append(f"{never} must not be classified as 72 h")
    if strict != {"Yang 2024"}:
        probs.append(f"strict exact 72-h should be Yang 2024 alone, got {sorted(strict)}")
    if "Wong 2006" not in {x["study"] for x in rows if x["include_sensitivity"] == "1"}:
        probs.append("Wong 2006 should be the approximate first-3-days sensitivity case")
    check("Target B excludes Zhang 2025 and Xie 2014; Yang 2024 strict, Wong 2006 sensitivity",
          not probs, "\n".join(probs))


def t_pain_at_rest_only():
    rows = read_csv(DATA / "target_C_pain24h.csv")
    probs = []
    for x in rows:
        blob = f"{x['outcome']} {x['endpoint_stratum']}".lower()
        if "rest" not in blob:
            probs.append(f"{x['study']}: outcome {x['outcome']!r} is not explicitly at rest")
        for bad in ("movement", "cough", "ambulation", "activity"):
            if bad in blob:
                probs.append(f"{x['study']}: contains '{bad}' pain")
    if {x["study"] for x in rows} != {"Xing 2022", "Liu 2021"}:
        probs.append(f"unexpected Target C membership: {sorted({x['study'] for x in rows})}")
    check("Target C contains only pain explicitly measured at rest (Xing 2022, Liu 2021)",
          not probs, "\n".join(probs))


def t_yu_wang_excluded():
    probs = []
    lock = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets" / "AF_Result_Lock.csv"
    if lock.exists():
        rows = read_csv(lock)
        e005 = [r for r in rows if r.get("LockID") == "E-005"]
        if not e005:
            probs.append("AF_Result_Lock row E-005 (Wang 2023 flatus) not found")
        elif "EXCLUDE" not in e005[0].get("Synthesisstatus", "").upper():
            probs.append(f"E-005 status is {e005[0].get('Synthesisstatus')!r}, expected EXCLUDE")
    flatus = read_csv(DATA / "target_E_flatus.csv")
    if any(x["lock_id"] == "E-005" for x in flatus):
        probs.append("Wang 2023 (E-005) present in the Target E analysis dataset")
    for r in MASTER:
        if "jamasurg" in r["stratum"].lower() or "yu wang" in r["stratum"].lower():
            probs.append(f"Yu Wang appears in pooled analysis {r['analysis_id']}")
    if "jamasurg.2022.5674" not in HTML:
        probs.append("exclusion of Yu Wang JAMA Surgery 2023 is not stated in the dashboard")
    check("Yu Wang JAMA Surgery 2023 excluded (wrong outcomes) and absent from Target E",
          not probs, "\n".join(probs))


def t_yeh_not_double_counted():
    probs = []
    # (a) not both in the locked primary dataset
    prim = read_csv(DATA / "opioid_24h_primary.csv")
    yeh_included = [x["study_unit"] for x in prim
                    if "yeh" in x["study_unit"].lower() and x["inc_primary"] == "1"]
    if yeh_included:
        probs.append(f"Yeh unit included in strict primary: {yeh_included}")
    # (b) not both in any served dataset used by the dashboard
    for path in list(DASH.glob("*.csv")) + list((DASH / "results").glob("*.csv")):
        rows = read_csv(path)
        yeh = {v for r in rows for v in r.values()
               if isinstance(v, str) and re.search(r"Yeh\s*(2010|2011)", v)}
        labels = {re.search(r"Yeh\s*(2010|2011)", v).group(0) for v in yeh}
        if len({re.sub(r"\s+", " ", x) for x in labels}) > 1:
            probs.append(f"{path.relative_to(ROOT)} lists Yeh 2010 and Yeh 2011 as separate rows")
    # (c) not presented as two independent trials in live UI prose
    # The guard list is the set of ways the page is allowed to mention both
    # records in one breath. Extended 2026-09-12: since the unit-of-analysis
    # amendment the page states the linkage in PRISMA 2020's own terms -- two
    # reports of one study, counted once -- which is a stronger statement than
    # the negations this list originally accepted, not a weaker one.
    guards = ("not ", "never", "forbid", "withdrawn", "hard hold", "excluding",
              "overlap", "superseded", "must not", "one study unit", "cohort-overlap",
              "two reports of one", "reports of one", "companion report", "count once",
              "counted once", "one trial", "linked cohort")
    for m in re.finditer(r"Yeh\s*2010[^<]{0,60}Yeh\s*20(10 ATHM|11)", LIVE_UI):
        window = LIVE_UI[max(0, m.start() - 400):m.end() + 400].lower()
        if not any(g in window for g in guards):
            probs.append("live UI lists Yeh 2010 and Yeh 2011 as two independent trials: "
                         + m.group(0)[:80])
    check("Yeh 2010 and Yeh 2011 are never counted as two independent trials",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 4. Estimand separation
# ─────────────────────────────────────────────────────────────────────────────

def t_ponv_strata_separate():
    rows = read_csv(DATA / "target_D_ponv.csv")
    strata = {}
    for x in rows:
        strata.setdefault(x["endpoint_stratum"], set()).add(x["study"])
    probs = []
    required = {"D_PONV_0-24h", "D_PONV_0-48h", "D_nausea_0-24h",
                "D_nausea_0-48h", "D_vomiting_0-24h", "D_vomiting_0-48h"}
    missing = required - set(strata)
    if missing:
        probs.append(f"missing PONV strata: {sorted(missing)}")
    # no stratum may mix a 24-h and a 48-h record
    for name, _ in strata.items():
        if "24" in name and "48" in name:
            probs.append(f"stratum {name} mixes windows")
    # nausea-only and vomiting-only must never be pooled as composite
    for aid, r in BY_ID.items():
        if not aid.startswith("TD_"):
            continue
        st = r["stratum"].lower()
        if "composite" in st and ("nausea 0" in st or "vomiting 0" in st):
            probs.append(f"{aid} pools nausea/vomiting-only records as composite PONV")
    # the UI must expose all six as distinct RoB contexts
    for key in ("ponv_24h", "ponv_48h", "nausea_24h", "nausea_48h",
                "vomiting_24h", "vomiting_48h"):
        if f'value="{key}"' not in HTML:
            probs.append(f"RoB/outcome selector missing option {key}")
    check("PONV kept in six discrete strata; nausea/vomiting never merged; 24 h never mixed with 48 h",
          not probs, "\n".join(probs))


def t_target_f_estimands_separate():
    rows = read_csv(DATA / "target_F_exploratory.csv")
    strata = {x["endpoint_stratum"] for x in rows}
    probs = []
    for need in ("F_intraop_titrated_requirement", "F_intraop_fixed_or_unclear_exposure",
                 "F_PCA_behavior", "F_rescue_opioid", "F_rescue_nonopioid",
                 "F_postop_delivered_dose_or_solution", "F_rescue_mixed_or_undefined"):
        if need not in strata:
            probs.append(f"missing Target F stratum {need}")
    # titrated and fixed exposure must never share a pooled analysis
    for aid, r in BY_ID.items():
        if not aid.startswith("TF_"):
            continue
        st = (r["stratum"] + " " + r["outcome"]).lower()
        if "titrated" in st and "fixed" in st:
            probs.append(f"{aid} pools titrated with fixed intraoperative exposure")
        if "pca" in st and ("mg" in r["effect_measure"].lower()
                            or "mme" in r["effect_measure"].lower()):
            probs.append(f"{aid} reports PCA behaviour in an opioid-mass unit "
                         f"({r['effect_measure']})")
        if "rescue" in st and "incidence" in st and "count" in st:
            probs.append(f"{aid} appears to merge rescue incidence with rescue counts")
    # PCA analyses must be SMD/behavioural, never labelled as opioid dose
    pca = [r for aid, r in BY_ID.items() if "PCA" in r["outcome"]]
    for r in pca:
        if re.search(r"\b(mg|µg|ug|MME)\b", r["effect_measure"]):
            probs.append(f"{r['analysis_id']}: PCA outcome carries dose units "
                         f"{r['effect_measure']!r}")
    check("Target F estimands separate (titrated vs fixed, PCA behaviour never as opioid dose, "
          "rescue incidence vs count, opioid vs non-opioid rescue)", not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 5. Risk of bias
# ─────────────────────────────────────────────────────────────────────────────

def t_rob_pending_not_high():
    """Structural: no fallback path may resolve an absent/unknown judgment to High."""
    probs = []
    m = re.search(r"function robState\(val\)\s*\{(.*?)\n\}", APP, re.S)
    if not m:
        probs.append("robState() not found - RoB state normalisation is not centralised")
    else:
        body = m.group(1)
        # the default/return-of-last-resort must not be 'high'
        tail = body[body.rindex("return"):]
        if "'high'" in tail or '"high"' in tail:
            probs.append("robState() default branch returns 'high'")
        for st in ("'low'", "'some'", "'high'", "'pending'", "'not-assessed'"):
            if st not in body:
                probs.append(f"robState() never yields {st}")
    # every consumer must go through the shared resolver
    if "resultRob(" not in APP:
        probs.append("resultRob() resolver missing")
    check("RoB states are distinct and no absent/pending value maps to High risk",
          not probs, "\n".join(probs))


def t_rob_result_specific():
    probs = []
    # data must actually carry per-result judgments
    keys = set()
    for s in STUDIES:
        keys |= set((s.get("rob2_outcomes") or {}).keys())
    keys.discard("assessed_list")
    if len(keys) < 10:
        probs.append(f"only {len(keys)} result-specific RoB contexts in data.js")
    # explorer must expose a result context rather than one global label
    if 'id="explorer-rob-outcome"' not in HTML:
        probs.append("Study Explorer has no result-specific RoB context selector")
    if "explorerRobOutcome" not in APP:
        probs.append("Study Explorer RoB column is not bound to a result context")
    # the old global-badge pattern must be gone
    if re.search(r"s\.rob2\.overall === 'Low'\s*\n?\s*\?", APP):
        probs.append("a study-level RoB ternary badge is still rendered")
    # divergences must be representable: assert at least one real case exists
    div = 0
    for s in STUDIES:
        sl = (s.get("rob2") or {}).get("overall")
        for k, v in (s.get("rob2_outcomes") or {}).items():
            if k == "assessed_list" or not isinstance(v, dict):
                continue
            if v.get("status") == "Assessed" and v.get("overall") != sl:
                div += 1
    if div == 0:
        probs.append("no result-specific judgment differs from its study-level label "
                     "- result-specificity is not actually exercised")
    check(f"RoB 2 is result-specific throughout ({div} judgments differ from study level)",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Withdrawn meta-regression must not reappear as a live claim
# ─────────────────────────────────────────────────────────────────────────────

def t_no_withdrawn_metareg():
    # k=11 is the legitimate size of the 24-h CANDIDATE POOL derived from the v26
    # lock. What must never reappear is a k=11 pooled RESULT or moderator model.
    banned = {
        "k = 11 presented as a pooled result": r"k\s*=\s*11(?![^<]{0,80}(?:candidate|pool|not estimable|no pooled|does not|cannot))",
        "N = 945": r"\b945\b",
        "baseline-demand slope": r"0\.0186|49\.08|−0\.170|&minus;0\.170",
        "publication-year slope": r"0\.0287|82\.81|\+0\.471",
        "sex slope": r"0\.8746",
        "multivariable model": r"0\.0204|0\.1876|1\.4895|1\.489",
    }
    probs = []
    for label, pat in banned.items():
        hits = re.findall(pat, LIVE_UI)
        if hits:
            probs.append(f"{label}: {len(hits)} live occurrence(s) outside withdrawal prose")
    # the only meta-regression in v26 is modality
    metaregs = [r for r in MASTER if r["model"] == "Meta-regression"]
    if len(metaregs) != 1 or "Modality" not in metaregs[0]["stratum"]:
        probs.append(f"expected exactly one (modality) meta-regression, got "
                     f"{[r['analysis_id'] for r in metaregs]}")
    # no bubble-plot assets may be served
    for asset in DASH.glob("stata_meta_reg_*.png"):
        probs.append(f"withdrawn bubble plot still served: {asset.name}")
    for asset in DASH.glob("stata_*_bubble.png"):
        probs.append(f"withdrawn bubble plot still served: {asset.name}")
    check("Withdrawn k=11 meta-regression absent from live claims; only the modality model remains",
          not probs, "\n".join(probs))


def t_small_study_effects():
    probs = []
    k = int(BY_ID["OP24_PRIM_COMB"]["k"])
    if k < 10:
        # Egger must not be reported as an interpreted result
        for m in re.finditer(r"[^.]{0,160}Egger[^.]{0,160}\.", LIVE_UI):
            seg = m.group(0)
            if re.search(r"p\s*=\s*0?\.\d+", seg) and "not performed" not in seg.lower():
                probs.append(f"Egger-type test interpreted at k={k}: {seg.strip()[:120]}")
        if "not performed" not in ALL_UI and "was not performed" not in ALL_UI:
            probs.append("no statement that publication-bias testing was withheld for k<10")
    check(f"Egger-type small-study-effect testing not interpreted at k={k} (<10)",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 7. GRADE
# ─────────────────────────────────────────────────────────────────────────────

def t_grade_consistent():
    probs = []
    m = re.search(r"const STATA_MASTER_RESULTS = \{", APP)
    if not m:
        probs.append("GRADE SoF source object not found")
    else:
        grades = re.findall(r'(?<![A-Za-z])grade:\s*"([^"]+)"', APP)
        if not grades:
            probs.append("no GRADE certainty ratings found")
        allowed = {"High", "Moderate", "Low", "Very Low", "Pending"}
        bad = sorted(set(grades) - allowed)
        if bad:
            probs.append(f"unrecognised GRADE ratings: {bad}")
        # headline KPI must not contradict the primary row in the SoF table
        combined = re.search(r'role:\s*"PRIMARY COMBINED".*?grade:\s*"([^"]+)"', APP, re.S)
        if combined:
            expected = combined.group(1)
            kpi = re.search(r'data-i18n="kpi\.gradeTitle".*?kpi-value[^>]*>([^<]+)<', HTML, re.S)
            if kpi and expected.lower() not in kpi.group(1).lower():
                probs.append(f"overview GRADE KPI shows {kpi.group(1).strip()!r} but the SoF "
                             f"table rates the combined primary {expected!r}")
    check("GRADE ratings are valid and the headline KPI agrees with the SoF table",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Downloads, assets and deployment parity
# ─────────────────────────────────────────────────────────────────────────────

def t_downloads_resolve():
    probs = []
    hrefs = set(re.findall(r'href="([^"]+\.(?:csv|json|do|log|dta|png|xlsx|md))"', HTML))
    hrefs |= set(re.findall(r"fetch\('([^']+\.(?:csv|json|log))'\)", APP))
    hrefs |= set(re.findall(r'src="([^"]+\.png)"', HTML))
    for h in sorted(hrefs):
        if h.startswith(("http://", "https://", "data:", "#")):
            continue
        # Links must be PAGE-relative so they survive being served from any mount
        # point (gh-pages root, docs/, a subdirectory). A repo-root-relative path
        # resolves only by accident of where the dashboard happens to sit.
        if h.startswith("06_FINAL_ANALYSIS_V26/"):
            probs.append(f"repo-root-relative link will 404 unless the dashboard is at "
                         f"the site root: {h} (use v26/... instead)")
            continue
        # v26/... only exists once scripts/build_site.py mirrors
        # 06_FINAL_ANALYSIS_V26/ into it (see .github/workflows/deploy-pages.yml);
        # dashboard/ itself no longer carries a committed v26/ copy. Resolve
        # against the true source instead of requiring that build step here.
        if h.startswith("v26/"):
            if not (ROOT / "06_FINAL_ANALYSIS_V26" / h[len("v26/"):]).exists():
                probs.append(f"unresolvable download/asset (checked against "
                             f"06_FINAL_ANALYSIS_V26/, the source scripts/build_site.py "
                             f"mirrors into v26/): {h}")
            continue
        if not (DASH / h).exists():
            probs.append(f"unresolvable download/asset: {h}")
    check(f"All {len(hrefs)} download and image targets resolve page-relatively",
          not probs, "\n".join(probs))


def t_downloads_are_current():
    probs = []
    hrefs = set(re.findall(r'href="([^"]+\.(?:csv|json|do|log|dta|png|xlsx|md))"', HTML))
    hrefs |= set(re.findall(r"fetch\('([^']+\.(?:csv|json|log))'\)", APP))
    retired = ("stata_consensus_synthesis", "stata_audited_synthesis",
               "stata_secondary_synthesis", "stata_48h_opioid_synthesis",
               "stata_72h_opioid_synthesis", "stata_meta_regression_execution",
               "stata_moderator_meta_regression", "stata_master_results",
               "stata_teas_leave_one_out", "stata_extended_moderators")
    for h in sorted(hrefs):
        for r in retired:
            if r in h:
                probs.append(f"active download points at retired artifact: {h}")
    # figures served by the dashboard must match the v26 figure package
    figs = ROOT / "06_FINAL_ANALYSIS_V26" / "04_FIGURES"
    for png in DASH.glob("forest_*.png"):
        twin = figs / png.name
        if twin.exists() and png.read_bytes() != twin.read_bytes():
            probs.append(f"{png.name} differs from the v26 figure package")
    check("Active downloads point at v26 artifacts; served figures match 04_FIGURES",
          not probs, "\n".join(probs))


def t_forest_matches_table():
    """The forest-plot study set must be the analysis study set."""
    probs = []
    prim = [x["study_unit"] for x in read_csv(DATA / "opioid_24h_primary.csv")
            if x["inc_primary"] == "1"]
    loo = re.search(r"const PRIMARY_LOO_DATA = (\[.*?\n\]);", APP, re.S)
    if not loo:
        probs.append("PRIMARY_LOO_DATA not found")
    else:
        names = re.findall(r'"omitted_canonical_name":\s*"([^"]+)"', loo.group(1))
        if sorted(names) != sorted(prim):
            probs.append(f"leave-one-out set {sorted(names)} != primary set {sorted(prim)}")
    mcid = read_csv(DASH / "results" / "paired_mcid_dataset.csv")
    mcid_keys = sorted(x["study_key"] for x in mcid)
    js_paired = sorted(s["key"] for s in STUDIES
                       if (s.get("mcid") or {}).get("is_paired") is True)
    if mcid_keys != js_paired:
        probs.append(f"paired MCID download {mcid_keys} != rendered cohort {js_paired}")
    check("Forest / leave-one-out / MCID study sets match the underlying analysis sets",
          not probs, "\n".join(probs))


def t_population_denominators():
    """
    population.arm1_n/arm2_n are the ANALYSED denominators used in synthesis and
    must trace to Outcome_Data_AF_LOCK. A block matching neither the randomised
    nor the analysed n in the workbook is a data defect - this is how He 2026
    (hepatectomy/JIS) came to display 43/43 for a trial that analysed 80/79.
    """
    lock = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets" / "Outcome_Data_AF_LOCK.csv"
    if not lock.exists():
        return check("Population denominators trace to the workbook", False,
                     "Outcome_Data_AF_LOCK.csv not found")
    rand, ana = {}, {}
    for r in read_csv(lock):
        key = (r.get("Canonicalstudy") or "").strip()
        for store, ki, kc in ((rand, "Randomizednintervention", "Randomizedncomparator"),
                              (ana, "Analyzednintervention", "Analyzedncomparator")):
            try:
                store.setdefault(key, set()).add((int(float(r[ki])), int(float(r[kc]))))
            except (ValueError, TypeError, KeyError):
                pass

    # Multi-cohort trials legitimately aggregate across sub-populations.
    AGGREGATE_OK = {"Wang 2024"}
    probs = []
    for st in STUDIES:
        key = st["key"]
        pop = st.get("population") or {}
        pair = (pop.get("arm1_n"), pop.get("arm2_n"))
        known = rand.get(key, set()) | ana.get(key, set())
        if not known or key in AGGREGATE_OK:
            continue
        if pair not in known:
            probs.append(f"{key}: population {pair[0]}/{pair[1]} matches no workbook row "
                         f"(randomised {sorted(rand.get(key, set()))}, "
                         f"analysed {sorted(ana.get(key, set()))})")
        if pop.get("total_n") != (pair[0] or 0) + (pair[1] or 0):
            probs.append(f"{key}: total_n {pop.get('total_n')} != {pair[0]} + {pair[1]}")
    check(f"Every population denominator traces to Outcome_Data_AF_LOCK ({len(STUDIES)} studies)",
          not probs, "\n".join(probs))


def t_paired_cohort_n():
    """
    The MCID paired cohort N must equal the primary analysis N, UNLESS every
    gap is a strict-primary study genuinely present in STUDIES_DATA but not
    flagged mcid.is_paired -- i.e. a documented, deliberate exclusion (e.g.
    Szmit 2021, added 2026-09-07: its only pain result is at hospital
    discharge with no exact postoperative time, so it has no clean ~24h
    opioid+pain pairing) rather than a study silently missing altogether.
    """
    rows = [x for x in read_csv(DATA / "opioid_24h_primary.csv") if x["inc_primary"] == "1"]
    expected = sum(int(x["n_i"]) + int(x["n_c"]) for x in rows)
    primary_units = {x["study_unit"] for x in rows}
    paired_studies = [s for s in STUDIES if (s.get("mcid") or {}).get("is_paired") is True]
    got = sum((s.get("population") or {}).get("total_n", 0) for s in paired_studies)

    by_key = {s.get("key"): s for s in STUDIES}
    paired_keys = {s.get("key") for s in paired_studies}
    gap_units = primary_units - paired_keys
    probs = []
    for unit in gap_units:
        if unit not in by_key:
            probs.append(f"{unit} is a strict primary study but has no STUDIES_DATA record at all "
                         f"(not merely unpaired -- entirely missing)")
    gap_n = sum((by_key[u].get("population") or {}).get("total_n", 0) for u in gap_units if u in by_key)
    if got + gap_n != expected:
        probs.append(f"paired cohort ({got}) + accounted-for gap studies ({gap_n}) = {got + gap_n}, "
                     f"but Stata primary analysis N is {expected} -- an unexplained discrepancy remains")
    check(f"MCID paired cohort N ({got}) plus documented gap studies ({sorted(gap_units)}) "
          f"accounts for the full primary analysis N ({expected})",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 10. Primary outcome contribution pathway
# ─────────────────────────────────────────────────────────────────────────────

def _pathway():
    src = (DASH / "primary_pathway.js").read_text(encoding="utf-8")
    i = src.index("window.PRIMARY_PATHWAY = ")
    return json.loads(src[i + len("window.PRIMARY_PATHWAY = "):].rstrip().rstrip(";"))


def t_pathway_counts_derive():
    """Counts must equal array lengths, not be asserted independently."""
    P = _pathway()
    c = P["counts"]
    probs = []
    if c["strict"] != len(P["primary_strict"]):
        probs.append(f"counts.strict={c['strict']} but primary_strict has {len(P['primary_strict'])}")
    if c["conditional"] != len(P["primary_conditional"]):
        probs.append(f"counts.conditional={c['conditional']} but array has {len(P['primary_conditional'])}")
    if c["author_contact_candidates"] != len(P["primary_author_contact_candidates"]):
        probs.append("counts.author_contact_candidates disagrees with its array")
    if c["candidate_pool"] != c["strict"] + c["conditional"]:
        probs.append("candidate_pool != strict + conditional")
    if not P.get("reconciles"):
        probs.append("pathway does not reconcile to the included-study total")
    total = c["reporting_relevant_24h_info"] + c["other_outcome_contributors"] + c["no_pooled_model"]
    if total != c["included_rcts"]:
        probs.append(f"buckets sum to {total}, expected {c['included_rcts']} included RCTs")
    check("Pathway counts are derived from their arrays and reconcile to the review total",
          not probs, "\n".join(probs))


def t_pathway_categories_disjoint():
    """A study cannot be strict and conditional, nor a candidate counted as strict."""
    P = _pathway()
    probs = []
    groups = {
        "strict": P["primary_strict"],
        "conditional": P["primary_conditional"],
        "candidate": P["primary_author_contact_candidates"],
        "other": P["other_outcome_contributors"],
        "none": P["no_pooled_model"],
    }
    seen = {}
    for name, rows in groups.items():
        for r in rows:
            for sid in (r.get("study_ids") or ([r["study_id"]] if r.get("study_id") else [])):
                if sid in seen:
                    probs.append(f"{r['study_unit']} appears in both {seen[sid]} and {name}")
                seen[sid] = name
    # an author-contact candidate must never be silently pooled
    strict_units = {r["study_unit"] for r in P["primary_strict"]}
    for r in P["primary_author_contact_candidates"]:
        if r["study_unit"] in strict_units:
            probs.append(f"candidate {r['study_unit']} is also counted as strict")
    check("Pathway categories are mutually exclusive; no candidate is silently counted as strict",
          not probs, "\n".join(probs))


def t_pathway_n_matches_denominators():
    """Displayed strict/conditional N must equal the summed analysed denominators."""
    P = _pathway()
    c = P["counts"]
    probs = []
    for key, arr in (("strict_n", "primary_strict"), ("conditional_n", "primary_conditional")):
        want = sum(r["n_i"] + r["n_c"] for r in P[arr])
        if c[key] != want:
            probs.append(f"counts.{key}={c[key]} but {arr} denominators sum to {want}")
    rows = [x for x in read_csv(DATA / "opioid_24h_primary.csv") if x["inc_primary"] == "1"]
    stata_n = sum(int(x["n_i"]) + int(x["n_c"]) for x in rows)
    if c["strict_n"] != stata_n:
        probs.append(f"strict N {c['strict_n']} != locked dataset N {stata_n}")
    check("Pathway N values equal the summed analysed denominators", not probs, "\n".join(probs))


def t_pathway_results_match_stata():
    """Strict and broader pooled results must come from the Stata master table."""
    P = _pathway()
    probs = []
    for label, aid in (("strict_md", "OP24_PRIM_COMB"),
                       ("strict_smd", "OP24_STRICT_SMD"),
                       ("broader_smd", "OP24_BROADER_SMD")):
        got = P["results"].get(label)
        if not got:
            probs.append(f"{label} missing from the pathway")
            continue
        ref = BY_ID.get(aid)
        if not ref:
            probs.append(f"{aid} missing from master_reconciled_results_v26.csv")
            continue
        for fld, nd in (("estimate", 4), ("ci_low", 4), ("ci_high", 4), ("p_value", 5)):
            a, b = got.get(fld), round(float(ref[fld]), nd) if ref[fld] else None
            if a is None or b is None or abs(a - b) > 10 ** (-nd + 1):
                probs.append(f"{label}.{fld}: pathway {a} vs Stata {b}")
        if got["k"] != int(float(ref["k"])):
            probs.append(f"{label}.k: pathway {got['k']} vs Stata {ref['k']}")
    # the strict analysis must never be displaced by the broader one
    if P["results"].get("broader_smd") and P["results"]["broader_smd"]["k"] <= P["results"]["strict_md"]["k"]:
        probs.append("broader analysis is not larger than the strict analysis")
    check("Pathway pooled results match the final Stata output exactly", not probs, "\n".join(probs))


def t_pathway_no_fabricated_md_pool():
    """No mean-difference pool may be claimed across the full candidate pool."""
    P = _pathway()
    est = P["md_pool_estimability"]
    probs = []
    if est["with_estimable_md"] >= est["candidate_pool_k"]:
        probs.append("an MD is claimed for the whole candidate pool; the lock forbids the "
                     "body-weight reconstruction that would require")
    for r in MASTER:
        if r["target"].startswith("Primary 24-h") and re.match(r"^MD\b", r["effect_measure"]):
            if int(float(r["k"])) > P["counts"]["strict"]:
                probs.append(f"{r['analysis_id']} reports an MD at k={r['k']} > strict k")
    # the withdrawn k=11 MD must not reappear
    if re.search(r"k\s*=\s*11[^<]{0,120}(MD|mean difference)", LIVE_UI, re.I):
        probs.append("a k=11 mean difference is presented as a live result")
    check("No mean-difference pool is fabricated across the full k=11 candidate pool",
          not probs, "\n".join(probs))


def t_pathway_contact_status_documented():
    """Contact status must never be inferred; every candidate needs a source reason."""
    P = _pathway()
    allowed = {"NOT YET CONTACTED", "CONTACT PREPARED", "CONTACTED — AWAITING RESPONSE",
               "RESPONSE RECEIVED — NO USABLE DATA", "RESPONSE RECEIVED — DATA UNDER REVIEW",
               "RESPONSE RECEIVED — USABLE PRIMARY DATA", "RESOLVED WITHOUT AUTHOR CONTACT",
               "NOT REQUIRED", "STATUS NOT DOCUMENTED"}
    probs = []
    for r in P["primary_author_contact_candidates"]:
        ac = r.get("author_contact") or {}
        if ac.get("status") not in allowed:
            probs.append(f"{r['study_unit']}: unrecognised contact status {ac.get('status')!r}")
        if not ac.get("status_basis"):
            probs.append(f"{r['study_unit']}: contact status asserted with no stated basis")
        if not (r.get("source_qc") or r.get("documented_issue")):
            probs.append(f"{r['study_unit']}: listed as a candidate with no documented source reason")
        # statuses implying contact happened need evidence the project does not hold
        if ac.get("status", "").startswith(("CONTACTED", "RESPONSE RECEIVED")):
            probs.append(f"{r['study_unit']}: claims {ac['status']} but the project records "
                         f"no sent/response field anywhere")
    check("Author-contact status is documented, never inferred; every candidate has a source reason",
          not probs, "\n".join(probs))


def t_pathway_wording():
    """Non-contributing trials must not be described as excluded from the review."""
    probs = []
    for m in re.finditer(r"[^.]{0,160}excluded from the (?:review|systematic review)[^.]{0,80}\.", LIVE_UI, re.I):
        seg = m.group(0)
        if not re.search(r"\bnot excluded|never excluded|are not\b", seg, re.I):
            probs.append("non-negated 'excluded from the review': " + seg.strip()[:130])
    if re.search(r"\b57 (studies|trials) excluded\b", LIVE_UI, re.I):
        probs.append("'57 studies excluded' framing present")
    P = _pathway()
    if "processed" in LIVE_UI and re.search(r"only \d+ of \d+ .{0,30}processed", LIVE_UI, re.I):
        probs.append("implies only a subset of trials were processed")
    check("Non-contributing trials are never called 'excluded from the review'",
          not probs, "\n".join(probs))


def t_pathway_is_dynamic():
    """The flow must be generated, not written into the HTML."""
    probs = []
    if not (DASH / "primary_pathway.js").exists():
        probs.append("primary_pathway.js missing")
    if "renderPrimaryPathway" not in APP:
        probs.append("renderPrimaryPathway() not defined")
    if 'id="pathway-flow"' not in HTML:
        probs.append("pathway flow container missing from the HTML")
    # the flow numbers must not be hardcoded in the pathway markup
    m = re.search(r'<!-- PRIMARY OUTCOME CONTRIBUTION PATHWAY(.*?)<!-- Section 1', HTML, re.S)
    if m:
        body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
        for lit in ("63", "k = 6", "k=6", "k = 11", "k=11", "N = 628", "N = 945"):
            if lit in body:
                probs.append(f"pathway markup hardcodes {lit!r}; it must come from PRIMARY_PATHWAY")
    check("Contribution pathway is generated from data, with no hardcoded counts in the markup",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# v33 tiered primary-outcome analysis
# ─────────────────────────────────────────────────────────────────────────────

V33 = ROOT / "07_TIERED_V33"


def _tiered_v33_payload() -> dict:
    """Parse window.TIERED_V33 out of tiered_v33.js without a JS engine."""
    src = (DASH / "tiered_v33.js").read_text(encoding="utf-8")
    start = src.index("window.TIERED_V33 = ") + len("window.TIERED_V33 = ")
    end = src.rindex(";")
    return json.loads(src[start:end])


def t_v33_matches_stata():
    """
    Every pooled number on the v33 panel must equal what Stata actually fitted.

    This is the check that would catch a hand-edit to tiered_v33.js, or a stale
    generated file left behind after 13_tiered_primary_v33.do was re-run.
    """
    probs = []
    res_path = V33 / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33.csv"
    if not res_path.exists():
        check("v33 panel numbers match the Stata tiered results", False,
              f"{res_path} missing; run 13_tiered_primary_v33.do")
        return
    stata = {r["analysis_id"]: r for r in read_csv(res_path)}
    payload = _tiered_v33_payload()

    for key, row in payload["analysis_sets"].items():
        aid = row["analysis_id"]
        src = stata.get(aid)
        if src is None:
            probs.append(f"{key}: analysis_id {aid} not in the Stata results")
            continue
        for field, dp in (("estimate", 3), ("ci_low", 3), ("ci_high", 3),
                          ("p_value", 4), ("i2", 2)):
            want = src[field].strip()
            got = row[field]
            if want == "":
                if got is not None:
                    probs.append(f"{aid}.{field}: panel shows {got} but Stata reports nothing")
                continue
            if got is None or abs(float(want) - got) > 10 ** -dp:
                probs.append(f"{aid}.{field}: panel {got} != Stata {want}")
        if src["k"] and row["k"] != int(float(src["k"])):
            probs.append(f"{aid}.k: panel {row['k']} != Stata {src['k']}")

    check("v33 panel numbers match the Stata tiered results", not probs, "\n".join(probs))


def t_v33_strata_not_combined():
    """
    The two S0 strata must never be presented as one pooled primary estimate,
    and the sham-controlled EA cell must be reported as genuinely empty rather
    than quietly filled by the usual-care result.
    """
    probs = []
    payload = _tiered_v33_payload()
    S = payload["analysis_sets"]
    strata = payload["strata"]

    teas = {s["study"] for s in strata["teas_sham"]}
    ea = {s["study"] for s in strata["ea_usual"]}
    if teas & ea:
        probs.append(f"a study appears in both S0 strata: {sorted(teas & ea)}")
    if any(s["comparator"] != "Sham" for s in strata["teas_sham"]):
        probs.append("the sham-controlled stratum contains a non-sham comparator")
    if any(s["comparator"] == "Sham" for s in strata["ea_usual"]):
        probs.append("the usual-care stratum contains a sham comparator")
    if strata["ea_sham_k"] != 0:
        probs.append("ea_sham_k is no longer 0; the empty-cell statement must be revisited")
    if S["S0_teas_sham"]["k"] + S["S0_ea_usual"]["k"] == S["S0_teas_sham"]["k"]:
        probs.append("the supportive stratum is empty; the panel would be misleading")

    # a multi-arm trial must contribute exactly one contrast to the primary
    alt = {s["study"] for s in strata["multiarm_alternatives"]}
    for a in alt:
        stem = a.split("(")[0].strip()
        if stem in teas or stem in ea:
            pass  # its sibling contrast is the one that counts -- correct
        else:
            probs.append(f"multi-arm alternative {a!r} has no sibling contrast in S0")
    if alt & (teas | ea):
        probs.append(f"a correlated alternative contrast entered S0: {sorted(alt & (teas | ea))}")

    check("v33 comparator strata stay separate and multi-arm trials contribute one contrast",
          not probs, "\n".join(probs))


def t_v33_panel_is_dynamic():
    """The v33 panel must be rendered from data, never typed into the markup."""
    probs = []
    if not (DASH / "tiered_v33.js").exists():
        probs.append("tiered_v33.js missing")
    if "renderTieredV33" not in APP:
        probs.append("renderTieredV33() not defined")
    if 'src="tiered_v33.js' not in HTML:
        probs.append("tiered_v33.js is not loaded by index.html")
    for cid in ("t33-flow", "t33-sets", "t33-empty", "t33-figures", "t33-subtitle"):
        if f'id="{cid}"' not in HTML:
            probs.append(f"container #{cid} missing from the HTML")
    m = re.search(r"<!-- v33 TIERED PRIMARY-OUTCOME DERIVABILITY(.*?)<!-- Section 1", HTML, re.S)
    if m:
        body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
        for lit in ("k = 4", "k=4", "k = 3", "k=3", "−14.00", "-14.00", "−3.94", "-3.94"):
            if lit in body:
                probs.append(f"v33 markup hardcodes {lit!r}; it must come from TIERED_V33")
    else:
        probs.append("could not locate the v33 panel markup")

    # Every figure the panel links must exist in the v33 figure package, and
    # build_site.py must be the thing that mirrors it -- dashboard/ holds no
    # hand-copied v33 image that could go stale.
    try:
        payload = _tiered_v33_payload()
    except Exception as exc:
        probs.append(f"could not parse tiered_v33.js: {exc}")
    else:
        for fig in payload["figures"]:
            if not (V33 / "04_FIGURES" / fig["file"]).exists():
                probs.append(f"figure {fig['file']} missing from 07_TIERED_V33/04_FIGURES")
            if (DASH / fig["file"]).exists():
                probs.append(f"{fig['file']} is hand-copied into dashboard/; it must be mirrored at build time")
        if 'v33_out = out / "v33"' not in (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8"):
            probs.append("build_site.py does not mirror 07_TIERED_V33 into the deployed artifact")

    check("v33 derivability panel is generated from data, with no hardcoded results",
          not probs, "\n".join(probs))


def t_v33_zhang_withdrawn_everywhere():
    """
    Zhang 2025 was withdrawn from every 0-24 h analysis because it reports POD1,
    not an explicit 0-24 h window. The broader SMD must be k=9, and no live
    dashboard claim may still describe the k=10 model as the current result.
    """
    probs = []
    broad = BY_ID.get("OP24_BROADER_SMD")
    if broad is None:
        probs.append("OP24_BROADER_SMD missing from the master aggregate")
    elif int(float(broad["k"])) != 9:
        probs.append(f"OP24_BROADER_SMD k={broad['k']}, expected 9 after the Zhang 2025 withdrawal")

    pathway_js = (DASH / "primary_pathway.js").read_text(encoding="utf-8")
    m = re.search(r'"broader_smd_k":\s*(\d+)', pathway_js)
    if not m:
        probs.append("broader_smd_k not found in primary_pathway.js")
    elif int(m.group(1)) != 9:
        probs.append(f"primary_pathway.js broader_smd_k={m.group(1)}, expected 9")

    # The superseded k=10 model may be named, but only as superseded.
    for mm in re.finditer(r"[^.]*\bAdds Coura 2011[^.]*\.", HTML):
        if "Zhang 2025" in mm.group(0):
            probs.append("the broader-SMD description still lists Zhang 2025 as a contributor")

    # Zhang 2025's derivation card must carry a withdrawal label.
    card = re.search(r"Derivation 3: Zhang 2025(.*?)<!-- Derivation 4", HTML, re.S)
    if not card:
        probs.append("could not locate the Zhang 2025 derivation card")
    elif "WITHDRAWN IN v33" not in card.group(1):
        probs.append("the Zhang 2025 derivation card is not labelled as withdrawn")

    check("Zhang 2025 is withdrawn from every 0-24 h analysis and labelled as such",
          not probs, "\n".join(probs))


def t_v33_legacy_reconstructions_labelled():
    """
    The reader-facing body-weight reconstructions must be labelled legacy and
    excluded, and the pipeline must actually leave their MME fields empty -- the
    label and the data have to agree.
    """
    probs = []
    cards = {}
    for name, marker in (("Sim 2002", "Derivation 1: Sim 2002"),
                         ("Coura 2011", "Derivation 2: Coura 2011")):
        m = re.search(re.escape(marker) + r"(.*?)<!-- Derivation", HTML, re.S)
        if not m:
            probs.append(f"could not locate the {name} derivation card")
            continue
        cards[name] = m.group(1)
        if "LEGACY RECONSTRUCTION" not in m.group(1):
            probs.append(f"the {name} card is not labelled a legacy reconstruction")

    rows = {r["study_unit"]: r for r in read_csv(DATA / "opioid_24h_primary.csv")}
    for name in ("Sim 2002", "Coura 2011"):
        r = rows.get(name)
        if r is None:
            probs.append(f"{name} missing from opioid_24h_primary.csv")
            continue
        if r["mean_i_mme"].strip() or r["mean_c_mme"].strip():
            probs.append(f"{name} carries an absolute MME value; the reconstruction is live in the data")
        if not r["hedges_g"].strip():
            probs.append(f"{name} has no Hedges' g, so it cannot enter the SMD sensitivity as described")

    # The 70 kg reference weight is the invented quantity. Wherever it appears
    # as a live formula it must sit inside a block that names it an assumption,
    # so a reader cannot take it for something Coura 2011 reported.
    plain = HTML.replace("&nbsp;", " ")
    for mm in re.finditer(r"70 kg", plain):
        window = plain[max(0, mm.start() - 2500): mm.end() + 2500]
        if "assumed" not in window.lower():
            probs.append("a 70 kg figure appears with no nearby statement that it is assumed")
            break

    check("Body-weight reconstructions are labelled legacy and are absent from the locked data",
          not probs, "\n".join(probs))


def t_stratum_denominators():
    """
    Every per-stratum N quoted on the dashboard must be the sum of that
    stratum's own analysed arms.

    The combined N (676) was checked already, but the TEAS and EA stratum
    denominators were not: the dashboard carried N = 342 and N = 334, which sum
    correctly to 676 while both being individually wrong (337 and 339). A
    reconciling total is not evidence that its parts reconcile.
    """
    probs = []
    rows = [r for r in read_csv(DATA / "opioid_24h_primary.csv") if r["inc_primary"] == "1"]
    want = {}
    for mod in ("TEAS", "EA"):
        arms = [r for r in rows if r["modality"] == mod]
        want[mod] = sum(int(r["n_i"]) + int(r["n_c"]) for r in arms)

    ui = HTML + "\n" + APP + "\n" + TRANS
    for mod, n in want.items():
        # Any "N = <number>" appearing within 160 characters after a "k = <k>"
        # that names this stratum must be this stratum's own denominator.
        k = len([r for r in rows if r["modality"] == mod])
        for m in re.finditer(rf"{mod}[^.\n]{{0,80}}?k\s*=\s*{k}[^.\n]{{0,90}}?N\s*=\s*([\d,]+)", ui):
            got = int(m.group(1).replace(",", ""))
            if got != n:
                probs.append(f"{mod} stratum quoted as N = {got}; the analysed arms sum to {n}")
    # de-duplicate: one message per stratum is enough
    probs = sorted(set(probs))
    check("Per-stratum denominators equal the summed arms of that stratum",
          not probs, "\n".join(probs))


def _v33_payload() -> dict:
    src = (DASH / "v33_data.js").read_text(encoding="utf-8")
    start = src.index("window.V33_DATA = ") + len("window.V33_DATA = ")
    return json.loads(src[start:src.rindex(";")])


def t_v33_layer_matches_master():
    """
    The generated v33 layer must agree with the v33 workbook and the Stata
    results it claims to be derived from.
    """
    probs = []
    import openpyxl
    master = ROOT / "TEAS EA Verification" / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
    if not master.exists():
        check("v33 dashboard layer matches the v33 master", False, f"{master} missing")
        return
    p = _v33_payload()
    wb = openpyxl.load_workbook(master, data_only=True)
    if p["master"] != master.name:
        probs.append(f"layer names master {p['master']!r}")
    n_rows = wb["Outcome_Data"].max_row - 1
    if p["outcome_rows"] != n_rows:
        probs.append(f"outcome_rows {p['outcome_rows']} != {n_rows} in the workbook")
    n_studies = wb["Study_Master"].max_row - 1
    if p["canonical_studies"] != n_studies:
        probs.append(f"canonical_studies {p['canonical_studies']} != {n_studies}")
    if p["canonical_studies"] != 70:
        probs.append(f"canonical_studies is {p['canonical_studies']}, expected 70")

    sec_path = ROOT / "08_V33_MASTER" / "03_RESULTS" / "results_v33_secondary.csv"
    if sec_path.exists():
        stata = {r["analysis_id"]: r for r in read_csv(sec_path)}
        for r in p["secondary"]:
            src = stata.get(r["analysis_id"])
            if not src:
                probs.append(f"{r['analysis_id']} not in the Stata results")
                continue
            for f in ("estimate", "ci_low", "ci_high", "p_value"):
                if r[f] is None or abs(float(src[f]) - r[f]) > 1e-6:
                    probs.append(f"{r['analysis_id']}.{f}: layer {r[f]} != Stata {src[f]}")
    check("v33 dashboard layer matches the v33 master and Stata results",
          not probs, "\n".join(probs))


def t_v33_contribution_map_reconciles():
    """
    The contribution map's primary-family count must equal the locked strict
    primary k. A name-prefix bug once made this 8 against a locked 7.
    """
    probs = []
    p = _v33_payload()
    groups = {g["id"]: g for g in p["contribution_map"]["groups"]}
    per = p["contribution_map"]["per_study"]

    if len(per) != 70:
        probs.append(f"map covers {len(per)} studies, expected 70")

    strict_k = p["strict_primary_k"]
    prim = groups["primary_opioid_24h"]["n_studies"]
    if prim != strict_k:
        probs.append(f"primary family has {prim} studies but strict primary k is {strict_k}")

    flagged = sum(1 for x in per if x["in_primary"])
    if flagged != prim:
        probs.append(f"{flagged} studies flagged in_primary but the group count says {prim}")

    for g in p["contribution_map"]["groups"]:
        counted = sum(1 for x in per if g["id"] in x["families"])
        if counted != g["n_studies"]:
            probs.append(f"{g['id']}: header says {g['n_studies']}, rows give {counted}")

    orphan = [x["study"] for x in per if not x["families"]]
    if orphan:
        probs.append(f"studies mapped to no family at all: {orphan}")

    check("v33 contribution map reconciles with the locked primary k",
          not probs, "\n".join(probs))


def t_v33_map_panel_is_dynamic():
    """The v33 map and results must be rendered, never typed into the markup."""
    probs = []
    if not (DASH / "v33_data.js").exists():
        probs.append("v33_data.js missing")
    if "renderV33" not in APP:
        probs.append("renderV33() not defined")
    if 'src="v33_data.js' not in HTML:
        probs.append("v33_data.js is not loaded by index.html")
    for cid in ("v33-map", "v33-results", "v33-headline", "v33-notpooled", "v33-subtitle"):
        if f'id="{cid}"' not in HTML:
            probs.append(f"container #{cid} missing")
    m = re.search(r"<!-- v33 STUDY CONTRIBUTION MAP(.*?)<!-- v33 TIERED", HTML, re.S)
    if m:
        body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
        for lit in ("70 ", " 7 studies", "382", "0.519", "104.4"):
            if lit in body:
                probs.append(f"v33 map markup hardcodes {lit!r}")
    else:
        probs.append("could not locate the v33 map markup")
    check("v33 contribution map is generated from data, with no hardcoded counts",
          not probs, "\n".join(probs))


def t_no_stale_master_in_live_code():
    """
    Live analytical code must read the v33 master. Historical mentions in
    changelogs and audit trails are legitimate and are not flagged.
    """
    probs = []
    # The current master is whichever versioned workbook the build actually
    # uses, discovered rather than hardcoded: this check previously named v33
    # and would have had to be edited on every version advance, which is the
    # same drift hazard it exists to prevent.
    import re as _re
    build = (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8")
    m = _re.search(r"TEAS_EA_RECONCILED_MASTER_DATA_(v\d+)_FINAL_LOCK_READY", build)
    if not m:
        check("Live analytical code reads the current master, not an earlier one",
              False, "build_site.py names no versioned master")
        return
    current = m.group(1)
    older = [f"v{n}" for n in range(26, int(current[1:]))]

    live = {
        "scripts/build_site.py", "scripts/build_primary_pathway.py",
        "scripts/build_v33_dashboard_data.py", "scripts/build_v34_dashboard_data.py",
        "scripts/build_reference_data.py",
    }
    for rel in sorted(live):
        f = ROOT / rel
        if not f.exists():
            probs.append(f"{rel} missing")
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        for stale in older:
            # A frozen-hash reference or a documented supersession note may name
            # an older master legitimately; reading one as an INPUT may not.
            if f"{stale}_FINAL_LOCK_READY.xlsx" in txt and "V32_SHA256" not in txt:
                probs.append(f"{rel} still reads the {stale} master")
        if f"{current}_FINAL_LOCK_READY" not in txt:
            probs.append(f"{rel} does not reference the {current} master")
    check("Live analytical code reads the current master, not an earlier one",
          not probs, "\n".join(probs))


def t_stata_edition_claim():
    """
    The engine named on the dashboard must be the engine the logs record.

    The wrapper at /Users/ryan/bin/stata-se launches StataSE.app, but the licence
    activates Basic Edition: every execution log records `c(edition)` = BE
    (flavor IC, maxvar 5000). The dashboard claimed "StataNow 19.5 SE (Standard
    Edition)" in 77 places, including the peer-review-facing provenance footer.
    The analyses are unaffected - 49 variables and 109 observations are far
    inside BE's limits - but the provenance statement must not overstate.
    """
    logs = sorted((ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "logs").glob("*.log"))
    probs = []
    editions = set()
    for lg in logs:
        m = re.search(r"Stata Version:\s*([\d.]+)\s+(\w+)", lg.read_text(encoding="utf-8", errors="ignore"))
        if m:
            editions.add(m.group(2))
    if not editions:
        probs.append("no execution log records a Stata edition")
    elif len(editions) > 1:
        probs.append(f"execution logs disagree on the edition: {sorted(editions)}")
    else:
        actual = editions.pop()
        for name, text in (("index.html", HTML), ("app.js", APP), ("translations.js", TRANS)):
            for m in re.finditer(r"Stata(?:Now)?\s+[\d.]+\s+([A-Z]{2})\b", text):
                if m.group(1) != actual:
                    probs.append(f"{name} claims edition {m.group(1)} but the logs record {actual}")
                    break
    check("Stated Stata edition matches what the execution logs record",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 11. Final reconciliation pass: comparator hierarchy, conversions, moderator matrix
# ─────────────────────────────────────────────────────────────────────────────

def t_ea_comparator_not_mislabelled_sham():
    """
    The v26 EA strict primary stratum (El-Rakshy 2009, Seevaunnamtum 2016,
    Yang 2024) is entirely usual-care / open-label control - none of the three
    is sham-controlled. Calling this stratum "vs Control/Sham" or "vs Sham"
    falsely implies a sham-controlled principal comparison the protocol itself
    prioritises (Stata_Manifest.csv OPIOID24_PRIMARY pooling_rule: "sham-controlled
    principal analysis; usual-care/supportive comparisons separate").
    """
    rows = read_csv(DATA / "opioid_24h_primary.csv")
    ea_strict = [r for r in rows if r["inc_primary"] == "1"
                 and r["study_unit"] in ("El-Rakshy 2009", "Seevaunnamtum 2016", "Yang 2024")]
    probs = []
    if len(ea_strict) != 3:
        probs.append(f"expected the 3 EA strict studies, found {len(ea_strict)}")
    for r in ea_strict:
        if "sham" in r["comparator"].lower():
            probs.append(f"{r['study_unit']} comparator {r['comparator']!r} looks sham-controlled; "
                         f"re-verify the EA-vs-usual-care premise")
    # The bare form "EA vs Sham" is NOT banned: it is the correct stratum label
    # for the individual EA trials that really were sham-controlled (Wong 2006
    # among them), and the register carries it. Only the composite forms, which
    # can only be describing the strict primary stratum, are wrong.
    #
    # 2026-09-12: a stray control character in this pattern had been silently
    # disabling the third alternative. Removing it made the check fire on Wong
    # 2006's own correct label, which showed the alternative should never have
    # been here; what it was reaching for is asserted directly below instead.
    for bad in re.finditer(r"EA vs (?:Control/Sham|Sham/Control)", LIVE_UI):
        probs.append(f"live UI mislabels the EA stratum: {bad.group(0)!r}")
    # What actually matters: none of the three strict-primary EA studies may be
    # recorded as sham-controlled in the register the dashboard renders from.
    for s in STUDIES:
        if s["key"] in ("El-Rakshy 2009", "Seevaunnamtum 2016", "Yang 2024") \
           and "sham" in (s.get("comparator_short", "") + s.get("stratum", "")).lower():
            probs.append(f"{s['key']} is recorded as sham-controlled in data.js, contradicting "
                         f"the EA-vs-usual-care premise of the strict primary stratum")
    if "EA vs Usual Care" not in HTML and "EA vs Usual Care" not in APP:
        probs.append("expected corrected label 'EA vs Usual Care' not found")
    check("EA strict stratum is labelled 'vs Usual Care', not 'vs Sham/Control'",
          not probs, "\n".join(probs))


def t_combined_not_labelled_primary():
    """
    Protocol text (dashboard's own Locked Protocol Synthesis Standard) states
    TEAS and EA are "never combined into a single grand pooled estimate" and
    that primary comparisons are the modality-specific ones. The pooled k=6
    combined estimate must therefore never be presented as itself "Primary".
    """
    probs = []
    for m in re.finditer(r"Strict Combined Primary", LIVE_UI):
        probs.append("live UI still calls the combined k=6 estimate 'Strict Combined Primary': "
                     + LIVE_UI[max(0, m.start()-60):m.end()+20].replace("\n", " "))
    if "Supporting Combined" not in HTML and "Supporting Combined" not in APP:
        probs.append("expected 'Supporting Combined ...' framing not found")
    check("Combined k=6 estimate is labelled supporting, not primary", not probs, "\n".join(probs))


def t_moderator_matrix_no_fabricated_categories():
    """
    All 6 strict primary trials share identical Stimulation Timing and
    Electrical Frequency categories (verified against data.js stricta fields:
    100% 'Preoperative only' / 100% '2/100 Hz (Dense-Disperse)'), i.e. zero
    variance on both covariates - the same situation as Number of Sessions,
    which the matrix already correctly marks as dropped for zero variance.
    A model summing categories to 10 or 11 cannot describe a k=6 dataset.
    """
    probs = []
    timing = {(s.get("stricta") or {}).get("timing_category") for s in STUDIES
              if s["key"] in ("Chen 1998", "Chen 2020", "El-Rakshy 2009",
                              "He 2026 (hepatectomy/JIS)", "Seevaunnamtum 2016", "Yang 2024")}
    freq = {(s.get("stricta") or {}).get("frequency_category") for s in STUDIES
            if s["key"] in ("Chen 1998", "Chen 2020", "El-Rakshy 2009",
                            "He 2026 (hepatectomy/JIS)", "Seevaunnamtum 2016", "Yang 2024")}
    if len(timing) != 1:
        probs.append(f"strict trials are not identical on timing_category: {timing}")
    if len(freq) != 1:
        probs.append(f"strict trials are not identical on frequency_category: {freq}")
    for pat in (r"k\s*=\s*5.{0,20}k\s*=\s*5", r"k\s*=\s*7.{0,20}k\s*=\s*4"):
        if re.search(pat, LIVE_UI):
            probs.append(f"moderator matrix still shows a category split matching pattern {pat!r} "
                         f"(sums to 10-11, impossible at k=6)")
    if "t(9)" in LIVE_UI:
        probs.append("moderator matrix still reports a t(9) statistic (9 residual df implies "
                     "an ~11-observation model, not k=6)")
    check("Moderator matrix shows no fabricated categorical models inconsistent with k=6",
          not probs, "\n".join(probs))


def t_no_false_no_association_claim():
    """A demographic moderator that was never modelled must not be described
    as showing 'no evidence of an association' - that is a claim about a
    fitted model's result, not about the absence of one."""
    probs = []
    for m in re.finditer(r"[^.]{0,200}\bNot estimated\b[^.]{0,400}", LIVE_UI):
        window = m.group(0)
        if re.search(r"no evidence of an? association", window, re.I):
            probs.append("a 'Not estimated' cell is followed by a 'no evidence of association' "
                         "claim: " + window[:160].replace("\n", " "))
    check("No 'Not estimated' moderator row claims 'no evidence of association'",
          not probs, "\n".join(probs))


def t_cochrane_wording_not_overstated():
    """Cochrane 10.11.4 is guidance ('generally should not be considered with
    fewer than approximately 10 studies'), not a hard 'stipulates a minimum
    of 10' rule."""
    probs = []
    if re.search(r"stipulates that meta-regression models require a minimum", LIVE_UI):
        probs.append("Cochrane wording overstated as a hard requirement ('stipulates ... require a minimum')")
    check("Cochrane 10:1 guidance is not overstated as a hard requirement", not probs, "\n".join(probs))


def t_sufentanil_conversion_documented_and_unresolved():
    """
    The sufentanil conversion factor actually computed throughout the pipeline
    (0.1 mg MME/ug in 00_prep_data.do, uncited) must be both (a) documented in
    a dedicated audit file and (b) not silently presented on the dashboard as
    equal to a different, contradictory, citation-backed factor.
    """
    audit = ROOT / "06_FINAL_ANALYSIS_V26" / "06_AUDIT" / "opioid_conversion_audit.csv"
    probs = []
    if not audit.exists():
        probs.append("opioid_conversion_audit.csv missing")
    else:
        rows = read_csv(audit)
        suf = [r for r in rows if r["opioid"] == "Sufentanil" and "Chen 2020" in r["study_id"]]
        if not suf:
            probs.append("Chen 2020 sufentanil row missing from the audit")
        elif suf[0]["final_status"] not in ("CORRECTED", "VERIFIED", "UNRESOLVED"):
            probs.append(f"Chen 2020 sufentanil status {suf[0]['final_status']!r} is not a recognised audit state")
        elif not suf[0]["reference"].strip():
            probs.append("Chen 2020 sufentanil row carries no reference")
    # the do-file's actual factor must be documented
    # The factor the pipeline actually computes with must match what the audit
    # records as verified, and must appear on the dashboard's conversion table.
    prep = (ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "00_prep_data.do").read_text(encoding="utf-8")
    m = re.search(r"replace mme_factor = ([0-9.]+) if unit == .{0,3}\u00b5g sufentanil", prep)
    if not m:
        probs.append("could not locate the sufentanil mme_factor assignment in 00_prep_data.do")
    else:
        used = float(m.group(1))
        if suf and suf[0]["final_status"] == "CORRECTED":
            if abs(used - 1.0) > 1e-9:
                probs.append(f"audit records sufentanil as CORRECTED to 1000:1 but the pipeline uses {used}")
            if "1000:1" not in HTML:
                probs.append("dashboard conversion table does not show the corrected 1000:1 sufentanil ratio")
        if re.search(r"0\.1 mg MME\s*/\s*[u\u00b5]g \(100:1\)", LIVE_UI):
            probs.append("dashboard still presents the superseded 100:1 sufentanil factor as current")
    # the dashboard must not claim a confident, differently-sourced factor for sufentanil
    if "sufentanil" not in HTML.lower():
        probs.append("no sufentanil conversion caveat visible in the dashboard HTML")
    if "results_sufentanil_conversion_sensitivity.csv" not in HTML:
        probs.append("dashboard does not reference the published sufentanil sensitivity range")
    sens_log = ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "logs" / "11_sufentanil_conversion_sensitivity.log"
    if not sens_log.exists():
        probs.append("sufentanil sensitivity log missing - rerun 11_sufentanil_conversion_sensitivity.do")
    check("Sufentanil conversion factor is documented, sourced, and matches what the pipeline computes",
          not probs, "\n".join(probs))


def t_cdc_not_misattributed_to_perioperative_iv():
    """
    CDC 2022 is an outpatient acute/subacute/chronic-pain prescribing guideline;
    it does not publish route-specific IV conversion factors for intraoperative
    fentanyl/sufentanil/remifentanil. It must not be cited as the source for
    those specific perioperative IV ratios.
    """
    probs = []
    for m in re.finditer(r"CDC[^<\n]{0,40}", HTML):
        window = HTML[max(0, m.start()-300):m.end()]
        if re.search(r"Sufentanil|Fentanyl \(IV\)</strong></td>\s*<td><span[^>]*>0\.10", window):
            probs.append("CDC still appears attached to a perioperative IV fentanyl/sufentanil row: "
                         + m.group(0))
    if re.search(r"Universal conversion factors", LIVE_UI):
        probs.append("'Universal conversion factors' framing still present (should be a prespecified "
                     "framework with sensitivity-assessed uncertainty, not a universal claim)")
    if not re.search(r"outpatient", HTML, re.I):
        probs.append("no statement that CDC 2022 is scoped to outpatient prescribing")
    check("CDC 2022 is not misattributed as the source for perioperative IV conversion factors",
          not probs, "\n".join(probs))


def t_mcid_labelled_exploratory():
    """The paired opioid-pain trade-off studio must be labelled exploratory,
    not presented as a confirmatory analysis."""
    probs = []
    if "EXPLORATORY" not in HTML.upper() or "PAIRED" not in HTML.upper():
        probs.append("MCID studio is not labelled EXPLORATORY PAIRED ...")
    for bad in ("confirmed analgesia", "strictly beneficial", "ineffective due to poor stimulation"):
        if bad in LIVE_UI.lower():
            probs.append(f"forbidden MCID overclaim present: {bad!r}")
    if re.search(r"establishes? zero risk", LIVE_UI, re.I):
        probs.append("MCID text claims to establish zero risk")
    check("Clinical Importance / MCID studio is labelled exploratory with no overclaiming",
          not probs, "\n".join(probs))


def t_version_tag_present():
    """A visible analysis version and lock date must be present, using the
    documented date rather than an invented one."""
    probs = []
    if "Analysis version" not in HTML:
        probs.append("no 'Analysis version' element in the provenance footer")
    if "2026-09-06" not in HTML:
        probs.append("documented lock date (2026-09-06, from 06_FINAL_ANALYSIS_V26/00_README.md "
                     "'v26 reconciliation-complete / final-lock-ready') not shown")
    wb_readme = DATA / "authoritative_sheets" / "README.csv"
    if wb_readme.exists():
        text = wb_readme.read_text(encoding="utf-8-sig")
        if "2026-09-06" not in text:
            probs.append("workbook README sheet no longer documents 2026-09-06 as the lock date - update the check")
    check("Visible analysis version tag uses the actual documented lock date", not probs, "\n".join(probs))


def t_i18n_textcontent_no_html_entities():
    """
    reader_assist.js applies plain data-i18n values via el.textContent (only
    data-i18n-html uses innerHTML). A translation string containing HTML
    entities like &amp; or &bull; therefore renders as the LITERAL characters
    '&amp;' on screen instead of '&', because textContent never decodes
    entities. Every plain data-i18n value must use real Unicode characters
    (&, •, —, –) rather than HTML entities.
    """
    ra = (DASH / "reader_assist.js").read_text(encoding="utf-8")
    plain_keys = set(re.findall(r'data-i18n="([^"]+)"', HTML))
    probs = []
    entity_pat = re.compile(r"&(?:amp|bull|mdash|ndash|lt|gt|quot|nbsp);")
    for m in re.finditer(r'^\s*(\w+):\s*"((?:[^"\\]|\\.)*)",?\s*$', TRANS, re.M):
        key, val = m.group(1), m.group(2)
        if entity_pat.search(val):
            probs.append(f"translations.js key '{key}' contains an HTML entity "
                         f"({entity_pat.search(val).group(0)}) that will render literally "
                         f"under textContent: {val[:70]!r}")
    check("translations.js plain values use real characters, not HTML entities "
          "(data-i18n applies via textContent)", not probs, "\n".join(probs[:15]))



STATA_LOGS = ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "logs"


def _stata_study_block(log_name: str, occurrence: int = 0) -> list[tuple[str, float, float]]:
    """
    Parse the nth `meta summarize` per-study table out of a Stata log.

    Returns [(study_label, effect_size, percent_weight), ...]. Used so weight
    expectations are DERIVED from the engine output rather than transcribed,
    which is what let the k=6 weighting matrix drift: every weight in it was a
    hand-typed literal, so re-running Stata silently invalidated the whole
    column without any check noticing.
    """
    text = (STATA_LOGS / log_name).read_text(encoding="utf-8", errors="replace")
    blocks = text.split("Meta-analysis summary")
    rows = []
    for line in blocks[occurrence + 1].splitlines():
        if line.startswith("---") or line.startswith("==="):
            if rows:
                break
            continue
        m = re.match(r"^(.*?)\s*\|\s*(-?[\d.]+)\s+-?[\d.]+\s+-?[\d.]+\s+([\d.]+)\s*$", line)
        if m and m.group(1).strip() not in ("Study", "theta"):
            rows.append((m.group(1).strip(), float(m.group(2)), float(m.group(3))))
    return rows


def t_primary_weighting_matrix_matches_stata():
    """
    DERIVED. The random-effects weighting matrix in index.html lists each
    trial's effect size and its REML weight. Those are static table cells, so
    nothing forces them to track the engine. After the sufentanil conversion
    correction rescaled Chen 2020 by 10x, and again when Szmit 2021 was added
    to the strict primary pool (v32, 2026-09-07), every REML and DL weight in
    that table shifted, but a stale table would still show a superseded
    column. Assert each study's effect size and REML weight from the log are
    actually the ones displayed, and that the row count matches the CSV's own
    k for OP24_PRIM_COMB rather than a hardcoded count.
    """
    expected_k = int(BY_ID["OP24_PRIM_COMB"]["k"])
    rows = _stata_study_block("01_opioid24_primary.log", 0)
    flat = HTML.replace("−", "-").replace("&minus;", "-")
    probs = []
    if len(rows) != expected_k:
        probs.append(f"expected {expected_k} studies in the primary block (per OP24_PRIM_COMB), parsed {len(rows)}")
    for label, es, wt in rows:
        if f"{abs(es):.3f} mg" not in flat:
            probs.append(f"{label}: effect size {es:.3f} not displayed")
        if f"{wt:.2f}%" not in flat:
            probs.append(f"{label}: REML weight {wt:.2f}% not displayed")
    tot = sum(w for _, _, w in rows)
    if not (99.0 <= tot <= 101.0):
        probs.append(f"parsed REML weights sum to {tot:.2f}, not ~100")
    check(f"k={expected_k} weighting matrix effect sizes and REML weights match the Stata log",
          not probs, "\n".join(probs))


def t_no_pre_correction_sufentanil_values():
    """
    ABSENCE. The sufentanil factor was corrected from 0.1 to 1.0 mg MME/ug on
    2026-09-07, which rescales every sufentanil-derived MME figure by 10x. The
    superseded values are visually plausible next to the corrected ones - the
    exact failure mode this validator exists to catch - so ban them outright as
    live claims. Each entry is a pre-correction number that no longer describes
    any current analysis. Withdrawal prose is stripped first, so a value may
    still be discussed as explicitly superseded.
    """
    superseded = {
        "-4.68": "pre-correction pooled primary MD",
        "-4,68": "pre-correction pooled primary MD (sv)",
        "-12.26": "pre-correction primary CI lower bound",
        "-12,26": "pre-correction primary CI lower bound (sv)",
        "-2.819": "pre-correction Chen 2020 MD",
        "-2.81 ": "pre-correction Target A strict MD",
        "-2,81 ": "pre-correction Target A strict MD (sv)",
        "-2.43 mg": "pre-correction Target A excl. An 2014 MD",
        "-3.36 mg": "pre-correction Target A excl. Zhang 2023 MD",
        "-0.326 mg": "pre-correction Zhang 2025 derived MD",
        "-2.402": "pre-correction DerSimonian-Laird pooled estimate",
        "-18,33": "pre-correction prediction interval bound (sv)",
    }
    probs = []
    for blob, src, strip in ((HTML, "index.html", strip_withdrawal_prose),
                             (TRANS, "translations.js", strip_withdrawal_lines),
                             (APP, "app.js", strip_withdrawal_lines)):
        flat = strip(blob).replace("−", "-").replace("&minus;", "-")
        for needle, why in superseded.items():
            if needle in flat:
                probs.append(f"{src}: superseded value '{needle.strip()}' still present ({why})")
        # A 0.1 mg/ug factor is CORRECT for fentanyl (100:1) and only wrong for
        # sufentanil, so ban it by context rather than by the literal alone.
        for m in re.finditer(r"0\.1 mg\s*(?:MME\s*)?/\s*(?:µg|&micro;g|ug)", flat):
            window = flat[max(0, m.start() - 700):m.end() + 400].lower()
            if "sufentanil" in window and "previously" not in window and "corrected" not in window:
                probs.append(f"{src}: a 0.1 mg/ug factor is applied in sufentanil context "
                             f"near offset {m.start()} (superseded 100:1 ratio)")
    check("No pre-correction sufentanil-scale values survive as live claims",
          not probs, "\n".join(probs))


def t_xie2014_yang2020_secondary_outcomes_corrected():
    """
    PRESENCE + ABSENCE. Four secondary-outcome cells in STUDIES_DATA's own
    baked literal held numbers that did not match their own source PDF and
    directly contradicted that same study's own audit.corrections note,
    which already recorded the true figures (corrected 2026-09-10):

      - Xie 2014 rescue_analgesia: source Table 2 reports dezocine rescue
        1/20 (EAS) vs 6/20 (Sham); the cell held 4/20 vs 10/20.
      - Yang 2020 flatus_time: source Table 3 reports 20.8+/-4.6 h (EA) vs
        24.1+/-6.2 h (Usual care); the cell held 67.45+/-10.42 vs
        73.55+/-12.18 (roughly 3x too large).
      - Tu 2024 rescue_analgesia: source Table 4 / Results text reports
        tramadol rescue 3/57 (TEAS) vs 6/58 (Sham) -- the trial's own
        analysed n, matching Table 1 -- but the cell held 9/77 vs 17/76,
        a denominator this trial never reports anywhere.
      - Wu 2022 intraop_opioid: source Table 2 reports "Consumption of
        remifentanil(ug) 1637(630) [Control] 1383(494) [pTEAS]"; the cell
        held 1100/240 vs 1380/280 (n=30/30, a figure this trial never
        reports for either its raw consumption or its normalised index).

    IMPORTANT: none of the four ever reached the live, user-facing Meta Lab
    forest plot. app.js:42 (`for (const [key,records] of
    Object.entries(window.BROWSER_TARGETS)) s.outcomes[key]=records[s.key]`)
    overwrites exactly these buckets (flatus_time, rescue_analgesia,
    intraop_opioid) at runtime, on every page load, from
    06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.csv and
    target_F_exploratory.csv -- both SOURCE-VERIFIED and already correct for
    all four cells, confirmed by reading them directly. What this check
    guards is STUDIES_DATA's own baked literal: dead at runtime today, but
    read directly (not through app.js's merge) by
    scripts/build_rob2_source_links.py's denominator matching, which is what
    let this fix resolve four more RoB 2 register links. A latent
    inconsistency that misleads anyone reading data.js as ground truth, or
    that would silently resurface if app.js's merge is ever changed or
    removed -- worth guarding even though it is not live today.

    Checked in STUDIES_DATA (the artifact build_rob2_source_links.py reads)
    AND in the two Python generator scripts that produced it
    (dashboard/compile_dashboard_data.py,
    06_FINAL_ANALYSIS_V26/build_v26_dataset.py) -- all four hardcode these
    cells by canonical-name branch, so a rebuild without this guard would
    silently regenerate the wrong values, the same failure mode the v34
    post-lock-errata guards exist to catch on the other pipeline.
    """
    probs = []
    by_key = {s["key"]: s for s in STUDIES}

    xie = (by_key.get("Xie 2014", {}).get("outcomes") or {}).get("rescue_analgesia") or {}
    if (xie.get("arm1_events"), xie.get("arm2_events")) != (1, 6):
        probs.append(f"Xie 2014 outcomes.rescue_analgesia events are "
                     f"{xie.get('arm1_events')}/{xie.get('arm2_events')}, expected 1/6 "
                     f"(source PDF Table 2: dezocine rescue 1/20 EAS vs 6/20 Sham)")

    yang = (by_key.get("Yang 2020", {}).get("outcomes") or {}).get("flatus_time") or {}
    if yang.get("arm1_mean") != 20.8 or yang.get("arm2_mean") != 24.1:
        probs.append(f"Yang 2020 outcomes.flatus_time means are "
                     f"{yang.get('arm1_mean')}/{yang.get('arm2_mean')}, expected 20.8/24.1 "
                     f"(source PDF Table 3: time to first flatus)")

    tu = (by_key.get("Tu 2024", {}).get("outcomes") or {}).get("rescue_analgesia") or {}
    # The analysed denominator is lock-owned and lives in arm1_n/arm2_n. arm1_total
    # was the stale RANDOMISED n (77/76) and was removed in the 2026-09-10
    # remediation, so read the analysed field first and fall back only for
    # records the sync has not reached.
    tu_n1 = tu.get("arm1_n", tu.get("arm1_total"))
    tu_n2 = tu.get("arm2_n", tu.get("arm2_total"))
    if (tu.get("arm1_events"), tu_n1, tu.get("arm2_events"), tu_n2) != (3, 57, 6, 58):
        probs.append(f"Tu 2024 outcomes.rescue_analgesia is "
                     f"{tu.get('arm1_events')}/{tu_n1} vs "
                     f"{tu.get('arm2_events')}/{tu_n2}, expected 3/57 vs 6/58 "
                     f"(source PDF Table 4: tramadol rescue within 6-24h)")

    wu = (by_key.get("Wu 2022", {}).get("outcomes") or {}).get("intraop_opioid") or {}
    if wu.get("arm1_mean") != 1383.0 or wu.get("arm2_mean") != 1637.0:
        probs.append(f"Wu 2022 outcomes.intraop_opioid means are "
                     f"{wu.get('arm1_mean')}/{wu.get('arm2_mean')}, expected 1383.0/1637.0 "
                     f"(source PDF Table 2: intraoperative remifentanil consumption)")

    for path in (DASH / "compile_dashboard_data.py",
                 ROOT / "06_FINAL_ANALYSIS_V26" / "build_v26_dataset.py"):
        text = path.read_text(encoding="utf-8")
        if '"arm1_events": 4, "arm1_total": 20, "arm2_events": 10' in text:
            probs.append(f"{path.relative_to(ROOT)}: still hardcodes Xie 2014's "
                         f"pre-correction rescue_analgesia events (4/10)")
        if '"arm1_events": 1, "arm1_total": 20, "arm2_events": 6' not in text:
            probs.append(f"{path.relative_to(ROOT)}: does not hardcode Xie 2014's "
                         f"corrected rescue_analgesia events (1/6)")
        if '"arm1_mean": 67.45, "arm1_sd": 10.42' in text:
            probs.append(f"{path.relative_to(ROOT)}: still hardcodes Yang 2020's "
                         f"pre-correction flatus_time means (67.45/73.55)")
        if '"arm1_mean": 20.8, "arm1_sd": 4.6, "arm1_n": 29' not in text:
            probs.append(f"{path.relative_to(ROOT)}: does not hardcode Yang 2020's "
                         f"corrected flatus_time means (20.8/24.1)")
        if '"arm1_events": 9, "arm1_total": 77, "arm2_events": 17, "arm2_total": 76' in text:
            probs.append(f"{path.relative_to(ROOT)}: still hardcodes Tu 2024's "
                         f"pre-correction rescue_analgesia denominator (9/77 vs 17/76)")
        if '"arm1_events": 3, "arm1_total": 57, "arm2_events": 6, "arm2_total": 58' not in text:
            probs.append(f"{path.relative_to(ROOT)}: does not hardcode Tu 2024's "
                         f"corrected rescue_analgesia figures (3/57 vs 6/58)")
        if '"arm1_mean": 1100.0, "arm1_sd": 240.0, "arm1_n": 30' in text:
            probs.append(f"{path.relative_to(ROOT)}: still hardcodes Wu 2022's "
                         f"pre-correction intraop_opioid means (1100/1380, n=30/30)")
        if '"arm1_mean": 1383.0, "arm1_sd": 494.0, "arm1_n": 44' not in text:
            probs.append(f"{path.relative_to(ROOT)}: does not hardcode Wu 2022's "
                         f"corrected intraop_opioid means (1383/1637, n=44/40)")

    check("Xie 2014, Yang 2020, Tu 2024 and Wu 2022 secondary-outcome cells match their source PDFs",
          not probs, "\n".join(probs))


def t_locale_pooled_numbers_agree():
    """
    STRUCTURAL. Swedish strings are a second, independent copy of every headline
    number and drifted behind the English ones during the sufentanil correction.
    A presence-anywhere test cannot catch that, because English still satisfies
    it. Assert the current pooled primary result appears inside EACH locale's
    own section, in that locale's decimal convention, and that neither section
    still carries the pre-correction values.
    """
    r = BY_ID["OP24_PRIM_COMB"]
    md, lo, hi = (abs(float(r[k])) for k in ("estimate", "ci_low", "ci_high"))
    locales = translations_by_locale()
    probs = []
    for loc, blob in locales.items():
        if not blob.strip():
            probs.append(f"no '{loc}' section found in translations.js")
            continue
        flat = blob.replace("−", "-").replace("&minus;", "-")
        for val, name in ((md, "pooled MD"), (lo, "CI lower"), (hi, "CI upper")):
            needle = f"{val:.2f}" if loc == "en" else f"{val:.2f}".replace(".", ",")
            if needle not in flat:
                probs.append(f"{loc}: {name} {needle} missing")
        for stale in ("4.68", "4,68", "12.26", "12,26"):
            if (loc == "en") == ("." in stale) and stale in flat:
                probs.append(f"{loc}: pre-correction value {stale} still present")
    check("EN and SV translation strings both carry the current pooled primary result",
          not probs, "\n".join(probs))


def t_v26_logs_git_tracked():
    """
    06_FINAL_ANALYSIS_V26/02_STATA/logs/ is the one remaining copy of the Stata
    execution logs (dashboard/v26/ and docs/v26/ mirrors of it were retired in
    favor of scripts/build_site.py generating that mirror fresh at build time
    -- see .github/workflows/deploy-pages.yml). A blanket *.log gitignore rule
    can still silently swallow this canonical copy even though it is meant to
    ship with the analysis package; this is what the un-ignore rule in
    .gitignore guards, and what this check verifies actually worked.
    """
    import subprocess
    rel = "06_FINAL_ANALYSIS_V26/02_STATA/logs"
    d = ROOT / rel
    probs = []
    if not d.exists():
        probs.append(f"{rel} does not exist")
    else:
        on_disk = {p.name for p in d.glob("*.log")}
        tracked = set(subprocess.run(
            ["git", "ls-files", "--", rel], cwd=ROOT, capture_output=True, text=True
        ).stdout.split())
        tracked_names = {t.split("/")[-1] for t in tracked}
        missing = on_disk - tracked_names
        if missing:
            probs.append(f"{len(missing)} log(s) on disk but not git-tracked, "
                         f"e.g. {sorted(missing)[:3]}")
    check("06_FINAL_ANALYSIS_V26 execution logs are git-tracked, not just on disk",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Outcome hierarchy and translations
# ─────────────────────────────────────────────────────────────────────────────

def t_outcome_hierarchy():
    probs = []
    for phrase in ("Dual Timepoints", "Co-Primary", "co-primary", "Primary Analgesic Domain"):
        if phrase in LIVE_UI:
            probs.append(f"'{phrase}' implies 24 h and 48 h are co-primary")
    if "[KEY SECONDARY]" not in HTML:
        probs.append("48-h outcome is not labelled KEY SECONDARY")
    if "[EXPLORATORY]" not in HTML:
        probs.append("72-h outcome is not labelled EXPLORATORY")
    if "[PRIMARY]" not in HTML:
        probs.append("24-h outcome is not labelled PRIMARY")
    check("Outcome hierarchy: 24 h primary, 48 h key secondary, 72 h exploratory",
          not probs, "\n".join(probs))


def t_translations_do_not_contradict():
    """data-i18n values are injected at runtime and can silently restore stale text."""
    probs = []
    for pat, label in ((r"k\s*=\s*11|k=11", "k=11"), (r"\b945\b", "N=945"),
                       (r"0\.0186", "withdrawn p=0.0186"), (r"0\.0287", "withdrawn p=0.0287"),
                       (r"2,077|2 077", "stale Target A N")):
        if re.search(pat, TRANS):
            probs.append(f"translations.js still contains {label}")
    check("translations.js carries no stale values that data-i18n could re-inject",
          not probs, "\n".join(probs))


def t_author_contacts_not_stale():
    probs = []
    if re.search(r"60 (formal )?author inquiries|60 Studies with targeted", LIVE_UI):
        probs.append("dashboard still advertises 60 outstanding author inquiries")
    if "Inquiry Pending" in APP:
        probs.append("studies are still badged 'Inquiry Pending'")
    disp = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets" / "AF_P1_Disposition.csv"
    if disp.exists():
        rows = read_csv(disp)
        blockers = [r for r in rows if r.get("Globalfinallockblocker", "").strip().upper() != "NO"]
        if blockers:
            probs.append(f"{len(blockers)} P1 issues are still final-lock blockers")
        if len(rows) != 19:
            probs.append(f"expected 19 P1 dispositions, found {len(rows)}")
    check("Author-contact status reflects the v26 dispositions (0 blockers, none pending)",
          not probs, "\n".join(probs))


# ─────────────────────────────────────────────────────────────────────────────


# ── result-specific RoB 2 (adopted) ───────────────────────────────────────
def _rob2_results():
    rows = read_csv(ROOT / "09_V34_ANALYSIS" / "03_ROB2" /
                    "v34_rob2_draft_assessments.csv")
    return rows


def t_rob2_results_cover_the_worklist():
    """
    Every priority-1 row -- the results inside a fitted model -- must have an
    assessment, and every assessment must correspond to a real priority-1 row.

    A partial set would leave some pooled estimates with an unstated
    risk-of-bias basis while the panel implies all of them are covered.
    """
    work = [r for r in read_csv(ROOT / "09_V34_ANALYSIS" / "v34_rob2_worklist.csv")
            if r["priority"].startswith("1")]
    want = {(r["study"], r["outcome"], r["timepoint"]) for r in work}
    got = {(r["study"], r["outcome"], r["timepoint"]) for r in _rob2_results()}
    probs = []
    for k in sorted(want - got):
        probs.append(f"no assessment for {k[0]} / {k[1]} @ {k[2]}")
    for k in sorted(got - want):
        probs.append(f"assessment for a row that is not priority-1: {k[0]} / {k[1]} @ {k[2]}")
    check("Result-specific RoB 2 judgements cover exactly the results inside a fitted model",
          not probs, "\n".join(probs))


def t_rob2_results_carry_honest_provenance():
    """
    An AI-derived judgement must never be presented as an independently
    double-assessed one it wasn't.

    These 36 judgements were produced by reading the source articles, then
    adopted by the review lead as the review's working assessment on
    2026-09-08 -- that is what actually happened, and it is what must be
    recorded. The check fails if the status/provenance fields are missing
    (silently presenting them as if nobody is answerable for the status
    change), AND fails if the dashboard claims something stronger that did
    not happen -- an independent dual-assessor record this pipeline was never
    given. Cochrane RoB 2 is the review's central quality appraisal; getting
    its recorded provenance wrong in either direction misrepresents it.

    The review lead directed on 2026-09-09 that the explicit "no separately
    documented dual-assessor record was provided" caveat sentence itself
    (as opposed to the adopted-by/adopted-date attribution, which stays) no
    longer needs to be shown on the dashboard while the review is in
    progress -- so its absence is no longer checked here. The stronger guard
    below, that the dashboard must never affirmatively CLAIM an independent
    dual-assessment that didn't happen, is unaffected and still enforced.
    """
    probs = []
    for r in _rob2_results():
        if r["status"] != "ROB2_RESULT_SPECIFIC_ADOPTED":
            probs.append(f"{r['study']} / {r['outcome']}: status is {r['status']!r}")
        if not r.get("adopted_by") or not r.get("adopted_date"):
            probs.append(f"{r['study']} / {r['outcome']}: missing adopted_by/adopted_date")
    v34 = (ROOT / "dashboard" / "v34_data.js").read_text(encoding="utf-8")
    if '"rob2_results"' in v34:
        # The results array holds 36 long rationales, so the relevant fields
        # can be tens of KB past the "rob2_results" key -- search the whole
        # file for these specific, unlikely-to-collide markers rather than a
        # fixed-size slice.
        if "ROB2_RESULT_SPECIFIC_ADOPTED" not in v34:
            probs.append("v34_data.js rob2_results does not carry the adopted status")
        if '"adopted_by"' not in v34 or '"adopted_date"' not in v34:
            probs.append("v34_data.js rob2_results does not carry adopted_by/adopted_date")
    app = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    if "v34RobResultsHtml" in app:
        if "Adopted ${" not in app and "Adopted " not in app:
            probs.append("the results panel does not visibly show who/when adopted this")
        # Guard against a future edit re-introducing the unverified claim this
        # session specifically declined to write.
        if re.search(r"independently\s+(double|dual)[- ]assess", app, re.I):
            probs.append("the results panel claims independent dual-assessment that "
                         "this pipeline has no record of")
    check("Result-specific RoB 2 judgements carry honest, checkable provenance "
          "(adopted-by-review-lead, not a fabricated independent dual-assessment)",
          not probs, "\n".join(probs))


def _grade_new_models():
    return read_csv(ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv")


def t_certainty_note_reflects_computed_grade():
    """
    The certainty note must accurately describe what has actually been done:
    RoB 2 adopted, and a GRADE rating for the five new models now computed
    and adopted too -- but computed by an explicit rule, not by an
    independent GRADE panel, and the note must say so rather than reading as
    if a panel signed off.
    """
    v34 = (ROOT / "dashboard" / "v34_data.js").read_text(encoding="utf-8")
    probs = []
    if '"certainty_note"' in v34:
        note = v34.split('"certainty_note"', 1)[1][:1500]
        if "adopted" not in note.lower():
            probs.append("certainty_note does not reflect that RoB 2 was adopted")
        if "grade_new_models" not in note:
            probs.append("certainty_note does not point to the grade_new_models payload")
        if not re.search(r"not an independent GRADE panel|rule-based", note, re.I):
            probs.append("certainty_note does not disclose the GRADE rating is rule-based, "
                         "not an independent panel's judgement")
    check("The certainty note accurately describes the computed, adopted GRADE rating "
          "without claiming panel consensus", not probs, "\n".join(probs))


def t_grade_new_models_complete_and_valid():
    """
    Every model_id curated into v34_model_manifest.csv (the operator-confirmed
    list of models whose RoB 2 rollup has zero unjudged results -- originally
    five NEW v34 models, extended 2026-09-09 to five more REPRODUCED models
    once their rollup was also confirmed complete) must have a GRADE rating,
    and it must be one of the four valid GRADE levels. The expected set is
    read from the manifest, not hardcoded, so growing it needs no test edit.
    """
    rows = _grade_new_models()
    probs = []
    want = {r["model_id"] for r in read_csv(
        ROOT / "09_V34_ANALYSIS" / "01_DATA" / "v34_model_manifest.csv")}
    got = {r["model_id"] for r in rows}
    if got != want:
        probs.append(f"model set mismatch: missing {want - got}, extra {got - want}")
    for r in rows:
        if r["grade"] not in ("High", "Moderate", "Low", "Very Low"):
            probs.append(f"{r['model_id']}: invalid GRADE level {r['grade']!r}")
        if r["status"] != "GRADE_RULE_BASED_ADOPTED":
            probs.append(f"{r['model_id']}: status is {r['status']!r}, not GRADE_RULE_BASED_ADOPTED")
        if not r.get("adopted_by") or not r.get("adopted_date"):
            probs.append(f"{r['model_id']}: missing adopted_by/adopted_date")
    check("Every manifested v34 model has a valid, adopted GRADE rating",
          not probs, "\n".join(probs))


def t_grade_new_models_rule_recomputes():
    """
    Independently recompute each domain's downgrade from the underlying I2,
    CI, k and RoB 2 composition, using the exact bands stated in
    09_V34_ANALYSIS/04_GRADE/compute_new_model_grade.py's docstring, and
    confirm the stored downgrade and final GRADE level match.

    This is the GRADE analogue of t_rob2_overall_follows_algorithm: a rating
    assigned by impression rather than by the stated rule would pass a
    superficial "is it a valid GRADE level" check but not this one.
    """
    # Not filtered by phase: eligibility for this rule is the manifest (RoB 2
    # rollup confirmed complete), and by 2026-09-09 that includes five
    # REPRODUCED models alongside the original five NEW ones -- see
    # compute_new_model_grade.py's docstring.
    models = {r["model_id"]: r for r in read_csv(
        ROOT / "09_V34_ANALYSIS" / "03_RESULTS" / "v34_models.csv")}
    rollup = {r["model_id"]: r for r in read_csv(
        ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_model_rollup.csv")}
    levels = ["Very Low", "Low", "Moderate", "High"]
    probs = []
    for r in _grade_new_models():
        mid = r["model_id"]
        m, roll = models.get(mid), rollup.get(mid)
        if not m or not roll:
            probs.append(f"{mid}: missing source model or rollup row to recompute against")
            continue
        k = int(m["k"])
        i2 = float(m["i2"])
        ci_low, ci_high = float(m["ci_low"]), float(m["ci_high"])
        low, some, high = int(roll["low"]), int(roll["some_concerns"]), int(roll["high"])

        want_rob = 0 if high == 0 else (-2 if high / (low + some + high) >= 0.5 else -1)
        want_inc = 0 if i2 < 50 else -1
        crosses = ci_low <= 0 <= ci_high
        if not crosses and k >= 3:
            want_imp = 0
        elif not crosses and k == 2:
            want_imp = -1
        elif crosses and k >= 3:
            want_imp = -1
        else:
            want_imp = -2

        got_rob, got_inc, got_imp = (int(r["rob_downgrade"]), int(r["inconsistency_downgrade"]),
                                     int(r["imprecision_downgrade"]))
        if got_rob != want_rob:
            probs.append(f"{mid}: RoB downgrade stored {got_rob}, rule implies {want_rob}")
        if got_inc != want_inc:
            probs.append(f"{mid}: inconsistency downgrade stored {got_inc}, rule implies {want_inc}")
        if got_imp != want_imp:
            probs.append(f"{mid}: imprecision downgrade stored {got_imp}, rule implies {want_imp}")
        if int(r["indirectness_downgrade"]) != 0 or int(r["publication_bias_downgrade"]) != 0:
            probs.append(f"{mid}: indirectness/publication-bias downgrade is nonzero, but the "
                         "stated rule never downgrades either domain for these models")

        raw = want_rob + want_inc + want_imp
        want_grade = levels[max(0, min(3, 3 + raw))]
        if r["grade"] != want_grade:
            probs.append(f"{mid}: stored grade {r['grade']!r} but domains imply {want_grade!r}")

    check("Each new model's GRADE downgrades and final level match the stated rule, "
          "independently recomputed from I2/CI/k/RoB2", not probs, "\n".join(probs))


def t_grade_new_models_do_not_overclaim_panel_review():
    """
    The dashboard must never present this rule-based GRADE computation as an
    independent GRADE panel's consensus judgement -- the same guard already
    applied to the RoB 2 domain, extended to its GRADE consequence.
    """
    app = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    probs = []
    if "v34GradeNewModelsHtml" in app:
        if re.search(r"GRADE panel (has |had )?(reviewed|assessed|approved)", app, re.I):
            probs.append("the GRADE panel claims an independent panel review that did not happen")
        if "adopted" not in app.split("v34GradeNewModelsHtml")[0][-3000:] and \
           "Adopted ${" not in app:
            probs.append("the GRADE panel does not visibly show who/when adopted the rating")
    v34 = (ROOT / "dashboard" / "v34_data.js").read_text(encoding="utf-8")
    if '"grade_new_models"' in v34 and "not an independent GRADE panel" not in v34:
        probs.append("v34_data.js grade_new_models note drops the not-a-panel-judgement disclosure")
    check("The GRADE panel for the five new models does not overclaim independent panel review",
          not probs, "\n".join(probs))


def t_rob2_results_are_result_specific():
    """
    A study contributing several results must be judged per result, not once.

    The specific failure this guards against is a study-wide judgement copied
    across that study's results, which would hide exactly the differences --
    who measured this outcome, and were they blinded -- that make D4
    result-specific.
    """
    rows = _rob2_results()
    by_study = {}
    for r in rows:
        by_study.setdefault(r["study"], []).append(r)
    probs = []
    multi = {k: v for k, v in by_study.items() if len(v) > 1}
    if not multi:
        probs.append("no multi-result study found; the check would be vacuous")
    for study, rs in sorted(multi.items()):
        # Differing outcomes must not all share one identical rationale string.
        if len({r["rationale"] for r in rs}) == 1 and len({r["outcome"] for r in rs}) > 1:
            probs.append(f"{study}: {len(rs)} different results share one identical rationale")
    # At least one study must actually differ across its results, otherwise the
    # per-result judgement is indistinguishable from a study-wide one.
    varies = any(len({r["d4_measurement"] for r in rs}) > 1 for rs in multi.values())
    if not varies:
        probs.append("no study varies its D4 judgement across its own results")
    check("Result-specific RoB 2 judgements are made per result, not copied study-wide",
          not probs, "\n".join(probs))


def t_rob2_overall_follows_algorithm():
    """
    Overall risk must follow the RoB 2 algorithm, not be assigned by impression.
    """
    rank = {"Low": 0, "Some concerns": 1, "High": 2}
    probs = []
    for r in _rob2_results():
        doms = [r["d1_randomisation"], r["d2_deviations"], r["d3_missing"],
                r["d4_measurement"], r["d5_reporting"]]
        bad = [d for d in doms if d not in rank]
        if bad:
            probs.append(f"{r['study']} / {r['outcome']}: unrecognised domain value {bad}")
            continue
        want = "High" if "High" in doms else ("Some concerns" if "Some concerns" in doms else "Low")
        if r["overall"] != want:
            probs.append(f"{r['study']} / {r['outcome']}: overall {r['overall']!r} "
                         f"but domains imply {want!r}")
    check("Overall RoB 2 risk follows the algorithm from its own domains",
          not probs, "\n".join(probs))


def t_rob2_model_rollup_is_complete():
    """
    Every model must have a risk-of-bias basis for all of its contributing
    results -- assessed here or already adjudicated elsewhere. A rollup that
    silently omits a contributor would understate what a pooled estimate
    inherits.
    """
    rows = read_csv(ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_model_rollup.csv")
    probs = []
    if not rows:
        probs.append("model rollup is empty")
    for r in rows:
        if int(r["results_unjudged"]) != 0:
            probs.append(f"{r['model_id']}: {r['results_unjudged']} contributing "
                         "result(s) with no risk-of-bias basis")
        tot = int(r["low"]) + int(r["some_concerns"]) + int(r["high"])
        if tot != int(r["results_total"]):
            probs.append(f"{r['model_id']}: domain counts sum to {tot}, "
                         f"but {r['results_total']} results were judged")
    check("Every fitted model has a risk-of-bias basis for all its contributing results",
          not probs, "\n".join(probs))


def t_rob2_source_qc_flags_preserved():
    """
    Source-QC problems found while reading the PDFs (Huang 2025's conflicting
    reported values, Xing 2022's inconsistent allocation description, Zheng
    2025's uncertain flatus definition) are a different thing from the RoB 2
    judgement and must stay visible regardless of RoB 2's status.

    Adopting a RoB 2 judgement is not evidence the underlying source problem
    is resolved, and this check exists so a future edit cannot make the
    dashboard look cleaner by quietly dropping these flags.
    """
    expect = {
        "Huang 2025": "inconsistency",
        "Xing 2022": "allocation",
        "Zheng 2025": "flatus",
    }
    probs = []
    rows = _rob2_results()
    for study, marker in expect.items():
        matches = [r for r in rows if r["study"] == study and r.get("flags")]
        if not matches:
            probs.append(f"{study}: no source-QC flag found on any of its results")
            continue
        if not any(marker in r["flags"].lower() for r in matches):
            probs.append(f"{study}: flag text lost the expected marker {marker!r}")
    app = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    if "r.flags" not in app:
        probs.append("the results panel no longer renders the flags field at all")
    check("Known source-QC warnings (Huang 2025, Xing 2022, Zheng 2025) remain "
          "visible and distinct from RoB 2 status", not probs, "\n".join(probs))


def _interpretation_layer() -> dict:
    p = ROOT / "dashboard" / "interpretation_layer.js"
    if not p.exists():
        return {}
    txt = p.read_text(encoding="utf-8")
    return json.loads(txt[txt.index("{"):].rstrip().rstrip(";"))


def t_interpretation_layer_cannot_carry_evidence():
    """
    The interpretation layer is manuscript-drafting scaffolding: draft wording,
    reviewer questions, discussion prompts. It must never become a second,
    competing home for a scientific value.

    The risk is concrete. If a record could carry its own `overall`, `d1`..`d5`
    or a RoB2/GRADE status string, a later edit to "fix the wording" could
    silently change what the dashboard reports as a judgement, and the reader
    would have no way to tell which layer won. So the payload is checked
    structurally: it declares itself non-evidence, and no record carries a
    field name that belongs to the evidence layer. The only place evidence
    values may appear is `bound_evidence`, which exists precisely so the
    interpretation can be invalidated when those values move -- it is a
    read-only copy for comparison, never a source.
    """
    L = _interpretation_layer()
    probs = []
    if not L:
        check("The interpretation layer is present and structurally non-evidence",
              False, "dashboard/interpretation_layer.js is missing")
        return
    if L.get("is_evidence") is not False:
        probs.append("payload does not declare is_evidence: false")
    if L.get("layer") != "INTERPRETATION":
        probs.append(f"payload layer is {L.get('layer')!r}, expected 'INTERPRETATION'")
    if "not manuscript text" not in (L.get("disclaimer") or ""):
        probs.append("payload disclaimer does not state this is not manuscript text")

    banned = {"d1", "d2", "d3", "d4", "d5", "d1_randomisation", "d2_deviations",
              "d3_missing", "d4_measurement", "d5_reporting", "overall", "rob2",
              "adopted_by", "adopted_date", "status_rob2"}
    for rec in L.get("records", []):
        stray = banned & set(rec)
        if stray:
            probs.append(f"{rec.get('analysis_id')}: carries evidence-layer field(s) {sorted(stray)}")
        # bound_evidence is the one permitted copy, and only for comparison.
        if "bound_evidence" not in rec or "fingerprint" not in rec:
            probs.append(f"{rec.get('analysis_id')}: missing bound_evidence/fingerprint")

    # The renderer must not write into any evidence structure either.
    app = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    il_src = app[app.find("INTERPRETATION LAYER"):app.find("function renderV34")]
    for target in ("V34_DATA.", "TIERED_V33.", "STATA_MASTER_RESULTS[", "V33_DATA."):
        if re.search(re.escape(target) + r"[A-Za-z_\[\]']*\s*=(?!=)", il_src):
            probs.append(f"interpretation renderer assigns into evidence structure {target}")
    check("The interpretation layer declares itself non-evidence and carries no evidence fields",
          not probs, "\n".join(probs))


def t_interpretation_bound_to_current_evidence():
    """
    Every interpretation record stores the k, estimate, CI, I2, GRADE level and
    RoB 2 composition it was written against, plus a fingerprint over them.
    Recompute that fingerprint here from the authoritative analysis files.

    A mismatch means an analysis was re-run and the manuscript language now
    describes a result that no longer exists. That is the failure this whole
    layer is designed around, so it is checked here as well as in the
    generator: a stale record must be MARKED stale, and a record that claims
    to be current must actually match the live numbers.
    """
    L = _interpretation_layer()
    if not L:
        return
    # Records come from two authoritative sources: the v34 model results, and
    # the v26 Summary-of-Findings rows behind the Target A-F analyses. The
    # id -> v26 row mapping is imported from the generator rather than
    # restated, so the two cannot disagree about which row an interpretation
    # belongs to.
    models = {r["model_id"]: r for r in read_csv(
        ROOT / "09_V34_ANALYSIS" / "03_RESULTS" / "v34_models.csv")}
    sys.path.insert(0, str(ROOT / "09_V34_ANALYSIS" / "05_INTERPRETATION"))
    from build_interpretation_layer import LEGACY_ANALYSES  # noqa: E402
    v26 = {r["analysis_id"]: r for r in read_csv(
        ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS" / "master_reconciled_results_v26.csv")}
    for aid, meta in LEGACY_ANALYSES.items():
        row = v26.get(meta["csv_id"])
        if row:
            models[aid] = row
    # Third source: the Tier E exploratory scale-free SMD synthesis, whose
    # results live in their own file. Bound the same way as everything else --
    # an exploratory analysis is exactly where an unchecked binding would do
    # the most damage, because it has no GRADE rating to anchor it.
    tier_e = {r["analysis_id"]: r for r in read_csv(
        ROOT / "07_TIERED_V33" / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33_tierE.csv")}
    from build_interpretation_layer import TIER_E_ANALYSES  # noqa: E402
    for aid in TIER_E_ANALYSES:
        row = tier_e.get(aid)
        if row:
            models[aid] = row

    LEDGER = json.loads((ROOT / "09_V34_ANALYSIS" / "05_INTERPRETATION" /
                         "interpretation_bindings.json").read_text(encoding="utf-8"))

    probs = []
    for rec in L.get("records", []):
        mid = rec["analysis_id"]
        m = models.get(mid)
        if not m:
            probs.append(f"{mid}: interpretation exists for an analysis found in none of "
                         "v34_models.csv, master_reconciled_results_v26.csv or "
                         "TIERED_ANALYSIS_RESULTS_v33_tierE.csv")
            continue
        b = rec["bound_evidence"]
        live = {
            "k": int(float(m["k"])),
            "estimate": round(float(m["estimate"]), 4),
            "ci_low": round(float(m["ci_low"]), 4),
            "ci_high": round(float(m["ci_high"]), 4),
            "i2": round(float(m["i2"]), 2) if (m.get("i2") or "").strip() else None,
        }
        drift = {key: (b.get(key), live[key]) for key in live if b.get(key) != live[key]}
        if drift and not rec.get("stale"):
            probs.append(f"{mid}: bound evidence no longer matches the analysis "
                         f"({drift}) but the record is not marked stale")
        # A stale record whose bound evidence MATCHES the live numbers is the
        # normal state after an analysis is re-run: the generator rewrites the
        # wording against the new numbers but deliberately cannot clear the flag,
        # because only a person re-reading the prose can do that (--accept).
        # Corrected 2026-09-12: this previously failed that state, which would have
        # forced either accepting on the team's behalf or leaving the build red.
        # The ledger is what distinguishes the two cases -- a flag is justified
        # while the accepted fingerprint is behind the record's current one.
        if not drift and rec.get("stale"):
            accepted = (LEDGER.get("bindings", {}).get(mid) or {}).get("fingerprint")
            if accepted and accepted == rec.get("fingerprint"):
                probs.append(f"{mid}: marked stale although the acceptance ledger already "
                             f"records this exact fingerprint as reviewed")
    check("Interpretation records are bound to current evidence, or are marked stale",
          not probs, "\n".join(probs))


def t_interpretation_questions_are_data_triggered():
    """
    Reviewer questions must come from a condition in the actual data, not from
    an author's sense of what sounds rigorous. A panel that manufactures
    criticism to look thorough trains the team to ignore it, which is worse
    than showing nothing.

    Each question therefore carries the trigger that fired it and the evidence
    pathway that answers it; both are required here. The generator is also
    allowed to emit zero questions for a clean analysis, and that is checked
    to be genuinely reachable rather than a branch nobody ever hits.
    """
    L = _interpretation_layer()
    if not L:
        return
    probs = []
    for rec in L.get("records", []):
        for q in rec.get("reviewer_questions", []):
            if not (q.get("trigger") or "").strip():
                probs.append(f"{rec['analysis_id']}: reviewer question without a data trigger: "
                             f"{q.get('question')!r}")
            if not (q.get("pathway") or "").strip():
                probs.append(f"{rec['analysis_id']}: reviewer question without an evidence "
                             f"pathway: {q.get('question')!r}")
        for c in rec.get("claims", []):
            if c.get("level") not in ("supported", "qualified", "unsupported"):
                probs.append(f"{rec['analysis_id']}: claim with unknown level {c.get('level')!r}")
            if not (c.get("basis") or "").strip():
                probs.append(f"{rec['analysis_id']}: claim without a stated basis")
        # Discussion prompts are brainstorming, which is exactly why they need
        # the same discipline: a prompt that cannot say what raised it is an
        # opinion wearing the layer's authority. Rule-derived prompts must also
        # be distinguishable from ones a human wrote.
        for p in rec.get("discussion_prompts", []):
            if not isinstance(p, dict):
                probs.append(f"{rec['analysis_id']}: discussion prompt is not a structured "
                             f"record: {p!r}")
                continue
            if not (p.get("prompt") or "").strip():
                probs.append(f"{rec['analysis_id']}: empty discussion prompt")
            if not (p.get("trigger") or "").strip():
                probs.append(f"{rec['analysis_id']}: discussion prompt without a stated "
                             f"trigger: {p.get('prompt')!r}")
            if p.get("source") not in ("rule", "curated"):
                probs.append(f"{rec['analysis_id']}: discussion prompt with unknown source "
                             f"{p.get('source')!r}")
            # A prompt is a question for the team, never a statement of finding.
            # Containing a question, not ending on one: several legitimately ask
            # two and then add a clause explaining why the choice matters.
            if "?" not in (p.get("prompt") or ""):
                probs.append(f"{rec['analysis_id']}: discussion prompt is not phrased as a "
                             f"question: {p.get('prompt')!r}")
    check("Reviewer questions, claim boundaries and discussion prompts are data-triggered, "
          "never free-standing assertions", not probs, "\n".join(probs))


def t_prisma_checklist_is_complete_and_honest():
    """
    The PRISMA 2020 checklist must cover every item, and must not claim an item
    is satisfied when what exists is only the underlying material.

    PRISMA asks what the REPORT states. This review holds a great deal of
    material that the manuscript does not yet report, so "evidence-ready" is
    deliberately not "done", and items that are purely authorial -- funding,
    competing interests, rationale -- must never be marked ready off the back
    of repository content.

    The assessor-process items are held to the same line as the limitations
    section: while independent dual RoB 2 assessment is in progress, items 11
    and 23c must stay flagged for attention rather than being closed early.
    """
    path = DASH / "prisma_checklist.js"
    if not path.exists():
        check("PRISMA 2020 checklist is complete and honest", False,
              "dashboard/prisma_checklist.js missing -- run build_prisma_checklist.py")
        return
    src = path.read_text(encoding="utf-8")
    P = json.loads(src[src.index("window.PRISMA_CHECKLIST = ") +
                       len("window.PRISMA_CHECKLIST = "):src.rindex(";")])

    valid = {"evidence-ready", "manuscript-only", "attention"}
    probs = []
    items = P.get("items", [])
    if len(items) != 42:
        probs.append(f"{len(items)} items present; PRISMA 2020 has 42 including sub-items")
    seen = [i.get("item") for i in items]
    if len(set(seen)) != len(seen):
        probs.append("duplicate item numbers in the checklist")
    for i in items:
        for field in ("item", "section", "requirement", "status", "evidence", "where"):
            if not (i.get(field) or "").strip():
                probs.append(f"item {i.get('item', '?')}: missing {field}")
        if i.get("status") not in valid:
            probs.append(f"item {i.get('item')}: unknown status {i.get('status')!r}")
    counts = {s: sum(1 for i in items if i["status"] == s) for s in valid}
    for s, n in counts.items():
        if P.get("counts", {}).get(s) != n:
            probs.append(f"counts say {P.get('counts', {}).get(s)} {s}, items give {n}")

    by_id = {i["item"]: i for i in items}
    # Purely authorial items must never be claimed as ready from repo content.
    for aid in ("1", "25", "26"):
        if by_id.get(aid, {}).get("status") == "evidence-ready":
            probs.append(f"item {aid} is authorial but is marked evidence-ready")
    # The assessor process is still in progress; these cannot be closed yet.
    for aid in ("11", "23c"):
        if by_id.get(aid, {}).get("status") != "attention":
            probs.append(f"item {aid} concerns the in-progress assessor process but is marked "
                         f"{by_id.get(aid, {}).get('status')!r}")

    # Re-derive the figures the items quote, so they cannot go stale.
    grade_n = len(read_csv(ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv"))
    rob_n = len(read_csv(ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"))
    graded_n = sum(1 for r in _interpretation_layer().get("records", [])
                   if r["status"] != "exploratory")
    for aid, want, what in (("15", grade_n, "GRADE model ratings"),
                            ("18", rob_n, "RoB 2 assessments"),
                            ("22", graded_n, "reported analyses")):
        ev = by_id.get(aid, {}).get("evidence", "")
        if str(want) not in ev:
            probs.append(f"item {aid} does not quote the re-derived count of {want} {what}; "
                         f"it says {ev[:70]!r}")
    check("PRISMA 2020 checklist covers every item and does not claim more than the review "
          "reports", not probs, "\n".join(probs))


def t_limitations_are_evidenced_and_current():
    """
    Every limitation must carry evidence and a place to check it, and its
    counts must match the live analyses.

    A Limitations section is the easiest place in a manuscript to write
    something plausible and unfounded, and the hardest place for a reader to
    check it. So the builder derives each entry from a live file, and this
    re-derives the headline counts independently and compares -- a limitation
    that silently stops matching the analyses is worse than none, because it
    reads as diligence.

    It also holds one deliberate omission. Independent dual RoB 2 assessment is
    in progress at the review lead's direction, and the dashboard's earlier
    dual-assessor language was removed for that reason. This section must not
    assert it as a settled limitation while that work is underway, and must not
    quietly forget it either -- it belongs in `deferred`.
    """
    path = DASH / "limitations.js"
    if not path.exists():
        check("Limitations are evidenced and current", False,
              "dashboard/limitations.js missing -- run build_limitations.py")
        return
    src = path.read_text(encoding="utf-8")
    L = json.loads(src[src.index("window.LIMITATIONS = ") +
                       len("window.LIMITATIONS = "):src.rindex(";")])
    records = _interpretation_layer().get("records", [])
    graded = [r for r in records if r["status"] != "exploratory"]

    probs = []
    if not L.get("limitations"):
        probs.append("no limitations were assembled at all")
    for item in L.get("limitations", []):
        for field in ("domain", "title", "detail", "evidence", "where"):
            if not (item.get(field) or "").strip():
                probs.append(f"{item.get('title', '?')!r}: missing {field}")

    # Independently re-derive the three counts that appear in titles.
    n = len(graded)
    expect = {
        "heterogeneity": sum(1 for r in graded
                             if r["bound_evidence"].get("i2") is not None
                             and float(r["bound_evidence"]["i2"]) >= 75.0),
        "sparse": sum(1 for r in graded if int(r["bound_evidence"]["k"]) <= 3),
        "imprecision": sum(1 for r in graded if r.get("includes_null")),
        "rob": sum(1 for r in graded if int(r["bound_evidence"].get("rob_high", 0) or 0) > 0),
    }
    # Compared numerically per rule, not by scanning titles for the figure.
    # String-matching across all titles passes when a DIFFERENT limitation
    # happens to contain the same number -- observed: a heterogeneity count
    # falsified to 4 went undetected because another title contained "12 ".
    metrics = {m["key"]: m for m in
               (item.get("metric") for item in L.get("limitations", [])) if m}
    for key, want in expect.items():
        m = metrics.get(key)
        if want and not m:
            probs.append(f"no limitation carries a {key} metric; expected {want} of {n}")
        elif m and (m.get("count") != want or m.get("of") != n):
            probs.append(f"{key}: limitation says {m.get('count')} of {m.get('of')}, "
                         f"re-derived {want} of {n}")
    if L.get("reported_analyses") != n:
        probs.append(f"limitations claim {L.get('reported_analyses')} reported analyses, "
                     f"the layer has {n}")

    # The assessor-process omission must be deferred, not asserted and not lost.
    deferred_titles = " ".join(d.get("title", "") + d.get("why", "")
                               for d in L.get("deferred", []))
    if "assessor" not in deferred_titles.lower():
        probs.append("the risk-of-bias assessor process is not recorded as deferred")
    asserted = " ".join(i["title"] + i["detail"] for i in L.get("limitations", [])).lower()
    if "dual" in asserted or "single assessor" in asserted or "single-assessor" in asserted:
        probs.append("a limitation asserts the assessor process while dual assessment is "
                     "still in progress")
    check("Limitations are evidenced, current, and defer the in-progress assessor question",
          not probs, "\n".join(probs))


def t_exploratory_analyses_carry_their_guardrails():
    """
    The Tier E exploratory synthesis must carry its overclaim guardrails, and
    must never present itself as graded.

    It is the analysis most exposed to overclaim in the whole review: it is
    published as a secondary result, it exists precisely because the review has
    no sham-controlled EA estimate in absolute morphine equivalents, and it is
    reported on a dimensionless scale. Until this record existed it was also the
    only published analysis with no Results-safe wording and no "do not say"
    list, so there was nothing to catch a milligram figure being read off a
    Hedges' g.
    """
    L = _interpretation_layer()
    if not L:
        return
    sys.path.insert(0, str(ROOT / "09_V34_ANALYSIS" / "05_INTERPRETATION"))
    from build_interpretation_layer import TIER_E_ANALYSES  # noqa: E402

    by_id = {r["analysis_id"]: r for r in L.get("records", [])}
    probs = []
    for aid, meta in TIER_E_ANALYSES.items():
        rec = by_id.get(aid)
        if not rec:
            probs.append(f"{aid}: published Tier E analysis has no interpretation record")
            continue
        if rec.get("status") != "exploratory":
            probs.append(f"{aid}: status is {rec.get('status')!r}, expected 'exploratory'")
        if rec.get("bound_evidence", {}).get("grade") in (
                "Low", "Moderate", "High", "Very Low"):
            probs.append(f"{aid}: carries a GRADE certainty; none was adopted for Tier E")
        dns = " ".join(d.get("text", "") + d.get("why", "") for d in rec.get("do_not_say", []))
        if "certainty" not in dns.lower():
            probs.append(f"{aid}: no 'do not say' guarding against quoting a certainty rating")
        if meta["exploratory"].get("scale_free") and "dimensionless" not in dns.lower():
            probs.append(f"{aid}: scale-free, but nothing warns against reading an absolute "
                         f"dose off a standardized effect")
        if meta["exploratory"].get("single_study_ci"):
            if "pooled" not in dns.lower():
                probs.append(f"{aid}: k = 1, but nothing warns against calling it pooled")
    check("Exploratory Tier E analyses carry their overclaim guardrails and are never "
          "presented as graded", not probs, "\n".join(probs))


def t_every_analysis_has_discussion_prompts():
    """
    Every analysis must carry at least one discussion prompt.

    The feature shipped with hand-written prompts for 4 of 22 analyses, so 18
    rendered an empty section -- a heading promising team discussion questions
    with nothing under it. Rule-derived prompts now cover the rest. This holds
    that coverage, and separately holds the k = 1 case, where an earlier
    version asked whether "pooling" communicated more than reporting the trials
    individually on an analysis that pools nothing.
    """
    L = _interpretation_layer()
    if not L:
        return
    probs = []
    for rec in L.get("records", []):
        prompts = rec.get("discussion_prompts", [])
        if not prompts:
            probs.append(f"{rec['analysis_id']}: no discussion prompts")
        if int(rec.get("bound_evidence", {}).get("k", 0)) == 1:
            # Structural, not keyword-matching. The correct single-trial prompt
            # legitimately mentions pooled results -- to ask whether this trial
            # should sit beside them -- so scanning for the word "pooled" flags
            # the right wording as well as the wrong. What must hold is that the
            # k = 1 branch fired at all, rather than the k <= 3 pooling branch.
            triggers = [(p.get("trigger") or "") for p in prompts if isinstance(p, dict)]
            if not any("no pooling was performed" in t for t in triggers):
                probs.append(f"{rec['analysis_id']}: k = 1 but no prompt states that nothing "
                             f"was pooled; triggers were {triggers!r}")
    check("Every analysis carries at least one discussion prompt, and single-trial analyses "
          "are not described as pooled", not probs, "\n".join(probs))


def t_v34_csv_mirrors_locked_workbook():
    """
    v34_outcome_data.csv must still be a faithful mirror of the locked
    workbook's Outcome_Data sheet, cell for cell.

    POST_LOCK_ERRATA_v34.md states the invariant -- the workbook, this CSV and
    the dashboard's row count are one set, and changing any one alone produces
    a silent divergence -- but nothing enforced it. During the 2026-09-10
    re-lock the two did diverge: a literal-XML substitution in the errata
    patcher failed to match `<x:c r="BI55" s="102" t="str">` because the style
    attribute was absent from the literal, so the workbook kept
    `V34 time class` = "within 72h" on a row whose `Timepoint/window` had been
    corrected to "0-24 h after surgery". The patcher's own verify() passed,
    because it looked only at the field that had changed. The contradiction was
    visible only by comparing the two artefacts against each other.

    Numeric rendering is normalised before comparison: the CSV was written with
    whole numbers as "103" and openpyxl reads the same stored value back as
    103.0. That difference is cosmetic and is not what this check is for.
    """
    import openpyxl
    master = (ROOT / "TEAS EA Verification" /
              "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx")
    csv_path = (ROOT / "TEAS EA Verification" / "v34_reconciliation" /
                "data" / "v34_outcome_data.csv")
    if not (master.exists() and csv_path.exists()):
        check("v34 outcome CSV mirrors the locked workbook", False,
              "workbook or CSV missing")
        return

    def norm(v) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        try:
            f = float(s)
        except (TypeError, ValueError):
            return s
        return str(int(f)) if f == int(f) else repr(round(f, 10))

    rows_x = [list(r) for r in
              openpyxl.load_workbook(master, read_only=True, data_only=True)
              ["Outcome_Data"].iter_rows(values_only=True)]
    header_x, data_x = [str(c) for c in rows_x[0]], rows_x[1:]
    rows_c = read_csv(csv_path)

    probs = []
    if len(rows_c) != len(data_x):
        probs.append(f"CSV has {len(rows_c)} rows, workbook has {len(data_x)}")
    else:
        for i, (cr, xr) in enumerate(zip(rows_c, data_x), start=2):
            for j, name in enumerate(header_x):
                if norm(cr.get(name)) != norm(xr[j]):
                    probs.append(f"line {i} {name}: CSV {cr.get(name)!r} vs "
                                 f"workbook {xr[j]!r}")
                    if len(probs) >= 10:
                        break
            if len(probs) >= 10:
                break
    check("v34 outcome CSV mirrors the locked workbook cell for cell",
          not probs, "\n".join(probs))


def t_prisma_identification_split_is_derived():
    """
    The PRISMA identification split must match the review's own screening
    records, and the citation-searched trial must be named.

    The dashboard asserted "69 via database search + 1 via citation searching"
    without saying which trial arrived by which route, so a reader could not
    check it and neither could this pipeline. It is now re-derived by matching
    Study_Master against the Covidence exports
    (scripts/derive_study_provenance.py). This check re-runs that derivation and
    holds the rendered text to it, so the two cannot drift apart.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "derive_study_provenance", ROOT / "scripts" / "derive_study_provenance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = mod.derive()

    n_db = len(got["database_search"])
    n_cite = len(got["citation_searching"])
    cited = [c["study"] for c in got["citation_searching"]]
    app = (DASH / "app.js").read_text(encoding="utf-8")

    probs = []
    if got["total"] != 70:
        probs.append(f"derived {got['total']} canonical studies, expected 70")
    if (n_db, n_cite) != (69, 1):
        probs.append(f"derived split is {n_db} + {n_cite}, the dashboard states 69 + 1")
    if f"{n_db} via database search + {n_cite} via citation searching" not in app:
        probs.append("the rendered PRISMA summary does not state the derived split")
    for study in cited:
        if f"citation-searched trial is {study}" not in app:
            probs.append(f"the citation-searched trial ({study}) is not named on the dashboard")
    check("PRISMA identification split is derived from the screening records, and "
          "the citation-searched trial is named", not probs, "\n".join(probs))


def t_prior_evidence_dispositions_match_the_analysis():
    """
    The prior-evidence comparison must agree with the analysis it describes.

    This panel exists so the Discussion can say why this review's 0-24 h opioid
    estimate differs from Tan 2024's, trial by trial. Its danger is staleness:
    the source audit document already went out of date on exactly this point --
    it recorded 1 of Tan's six trials in our strict primary, then the review
    acted on its own finding and reinstated Szmit 2021, making it 2. A panel
    transcribed from the document would still say 1.

    So every disposition is re-derived at build time, and this check re-derives
    them again independently and compares. It also requires the superseded
    tally to be disclosed rather than quietly overwritten.
    """
    import importlib.util
    payload_path = DASH / "prior_evidence.js"
    if not payload_path.exists():
        check("Prior-evidence comparison matches the analysis", False,
              "dashboard/prior_evidence.js missing -- run build_prior_evidence_comparison.py")
        return

    src = payload_path.read_text(encoding="utf-8")
    payload = json.loads(src[src.index("window.PRIOR_EVIDENCE = ") +
                             len("window.PRIOR_EVIDENCE = "):src.rindex(";")])

    spec = importlib.util.spec_from_file_location(
        "build_prior_evidence", ROOT / "scripts" / "build_prior_evidence_comparison.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    probs = []
    primary = mod.strict_primary_studies()
    canon = mod.canonical_studies()

    if payload["our_primary"] != primary:
        probs.append(f"panel lists primary {payload['our_primary']}, "
                     f"the Stata log fits {primary}")
    for t in payload["trials"]:
        want, _ = mod.disposition(t["study"], canon, primary)
        if t["status"] != want:
            probs.append(f"{t['study']}: panel says {t['status']}, live data says {want}")
    if len(payload["trials"]) != 6:
        probs.append(f"panel shows {len(payload['trials'])} trials, the prior review pooled 6")
    if sum(payload["counts"].values()) != 6:
        probs.append(f"counts sum to {sum(payload['counts'].values())}, expected 6")

    # If the audit's own tally no longer holds, the panel has to say so.
    audit_text = (ROOT / "TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md").read_text(encoding="utf-8")
    m = re.search(r"Included in our strict primary 24-h analysis:\*\*\s*\*\*(\d+)\s*/\s*6", audit_text)
    if m and int(m.group(1)) != payload["counts"]["in-primary"] and not payload.get("superseded_note"):
        probs.append(f"the audit says {m.group(1)}/6 in the primary and the analysis says "
                     f"{payload['counts']['in-primary']}/6, but the panel does not disclose it")

    check("Prior-evidence comparison matches the analysis it describes",
          not probs, "\n".join(probs))


def t_prisma_screening_arithmetic_reconciles():
    """
    The PRISMA screening arithmetic must reconcile, in the units the source
    record actually uses.

    This was flagged on the dashboard for some time as an unresolved 12-record
    gap: 5,100 identified minus 2,160 removed implies 2,940 reaching screening,
    against a transcribed 2,928. The gap was an artefact of mixing units. The
    source record's identification box reads "References from databases/registers
    (n = 5100) (as n = 5088 studies)" -- Covidence counts references at import
    and studies thereafter, and 12 of the references were additional reports of
    studies already present. 5,088 - 2,160 = 2,928 exactly.

    Pinned here so the reconciliation cannot silently regress to the reference
    count, and so a future change to any of the four figures has to keep the
    identity true.
    """
    references, studies, removed, screened = 5100, 5088, 2160, 2928
    app = (DASH / "app.js").read_text(encoding="utf-8")
    html = (DASH / "index.html").read_text(encoding="utf-8")

    probs = []
    if studies - removed != screened:
        probs.append(f"{studies} - {removed} = {studies - removed}, not {screened}")
    if references - studies != 12:
        probs.append(f"references minus studies is {references - studies}, expected 12")
    # Both surfaces must state the study count, not only the reference count --
    # showing 5,100 alone is what made the arithmetic look broken.
    for name, text in (("app.js", app), ("index.html", html)):
        if "5,088" not in text and "5088" not in text:
            probs.append(f"{name} does not state the 5,088 study count")
    # The stale "unresolved gap" language must not come back.
    for name, text in (("app.js", app), ("index.html", html)):
        for stale in ("2,940", "12-record gap", "Unreconciled gap"):
            if stale in text:
                probs.append(f"{name} still carries resolved-gap language: {stale!r}")
    check("PRISMA screening arithmetic reconciles in studies, not references",
          not probs, "\n".join(probs))


def t_post_lock_errata_still_applied():
    """
    The source-verified post-lock corrections must still be in the dataset.

    t_v34_csv_mirrors_locked_workbook catches the two artefacts drifting apart.
    It does not catch them being reverted *together*, which is exactly what a
    re-run of reconcile.py followed by a workbook rebuild would do: both defects
    originate upstream in the v33 workbook, so a clean regeneration reproduces
    them consistently in both places and every mirror check still passes.

    reconcile.py now refuses to write in that situation. This is the same
    invariant asserted from the other end, against what is actually on disk, so
    a correction cannot be lost by any route -- including one that bypasses
    reconcile.py entirely.
    """
    reg_path = (ROOT / "TEAS EA Verification" / "v34_reconciliation" /
                "data" / "post_lock_errata.json")
    csv_path = (ROOT / "TEAS EA Verification" / "v34_reconciliation" /
                "data" / "v34_outcome_data.csv")
    if not (reg_path.exists() and csv_path.exists()):
        check("Source-verified post-lock errata are still applied", False,
              "errata register or outcome CSV missing")
        return

    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    rows = {r.get("Comparison ID"): r for r in read_csv(csv_path)}
    probs = []
    for e in reg["applied"]:
        row = rows.get(e["comparison_id"])
        if row is None:
            probs.append(f"erratum {e['erratum']}: {e['comparison_id']} is absent "
                         f"-- {e['summary']}")
            continue
        for field, want in e["fields"].items():
            got = (row.get(field) or "").strip()
            if got != str(want):
                probs.append(f"erratum {e['erratum']}: {e['comparison_id']}.{field} "
                             f"is {got!r}, verified value is {str(want)!r}")
    check("Source-verified post-lock errata are still applied",
          not probs, "\n".join(probs))


def t_target_af_sof_rows_match_v26_source():
    """
    The Target A-F rows of STATA_MASTER_RESULTS (app.js) -- the object that
    actually feeds the GRADE Summary of Findings table -- must still match
    the v26 results CSV they were transcribed from.

    This is the specific gap the brief's Phase 13 ("single source of truth
    for dashboard statistics") names: STATA_MASTER_RESULTS is a single JS
    object (not scattered across the file), but its k/estimate/CI/p values
    are hand-authored text (mdText, pVal) rather than generated from the CSV
    at build time, same as MODEL_META's labels. A full migration to
    generated templating was assessed and not attempted this pass -- the
    downgrade/controlRisk fields are substantially reviewer-authored analysis
    prose, not values a script can derive, so "fully templated" would still
    need a human-maintained reasoning layer alongside it (exactly what
    build_interpretation_layer.py's LEGACY_ANALYSES already is for these same
    nine analyses, for the interpretation layer specifically) -- and this
    session found two real bugs THIS SAME EDITING SESSION from exactly the
    duplicate-source-of-truth pattern a rewrite here would still carry
    (translations.js vs app.js; index.html's static fallback vs
    renderKPIs()). A cross-check guard is the bounded, lower-risk
    alternative: it cannot let the two drift apart unnoticed, without
    introducing a new generation pathway this late that could itself
    introduce a third instance of that same bug class.

    Reuses LEGACY_ANALYSES from build_interpretation_layer.py for the
    AN-id -> csv_id mapping rather than restating it a second time.
    """
    sys.path.insert(0, str(ROOT / "09_V34_ANALYSIS" / "05_INTERPRETATION"))
    from build_interpretation_layer import LEGACY_ANALYSES  # noqa: E402

    v26 = {r["analysis_id"]: r for r in read_csv(
        ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS" / "master_reconciled_results_v26.csv")}
    app = (DASH / "app.js").read_text(encoding="utf-8")

    probs = []
    for aid, meta in LEGACY_ANALYSES.items():
        if aid == "AN-01-SMD":
            continue  # not a Target A-F row in the SoF table; different section.
        row = v26.get(meta["csv_id"])
        if not row:
            probs.append(f"{aid}: {meta['csv_id']} not found in master_reconciled_results_v26.csv")
            continue
        # The last entry in the object has no following "AN-..." key to anchor
        # on, so the closing brace is matched against either boundary.
        m = re.search(rf'"{re.escape(aid)}":\s*\{{(.*?)\n  \}},?\n(?:  "|\}})', app, re.S)
        if not m:
            probs.append(f"{aid}: entry not found in STATA_MASTER_RESULTS")
            continue
        block = m.group(1)

        def field(name):
            # Two bugs found by mutation-testing this check, not by reading
            # it. (1) mdText's value contains an internal comma ("[lo, hi]"),
            # so matching must run to the closing quote, not the first comma,
            # or it silently truncates to 2 numbers and the len(nums) >= 3
            # guard below skips the comparison with no error. (2) "k:" as a
            # bare pattern also matches inside "controlRisk:" -- re.search
            # isn't anchored to a standalone property name -- so it must
            # require the property name to start right after the line's
            # leading whitespace, not merely appear as a substring anywhere.
            fm = re.search(rf'\n\s+{name}:\s*"([^"]*)"', block)
            if fm:
                return fm.group(1).strip()
            fm = re.search(rf'\n\s+{name}:\s*([^",\n]+),', block)  # unquoted (k, n)
            return fm.group(1).strip() if fm else None

        k_disp = field("k")
        if k_disp is not None and int(float(k_disp)) != int(float(row["k"])):
            probs.append(f"{aid}: displayed k={k_disp}, source k={row['k']}")

        md_text = field("mdText")
        nums = re.findall(r"[−-]?\d[\d.]*", md_text or "")
        if len(nums) >= 3:
            def to_f(s):
                return -float(s[1:]) if s.startswith("−") else float(s)
            disp_est, disp_lo, disp_hi = (to_f(n) for n in nums[:3])
            for disp, src, label in ((disp_est, float(row["estimate"]), "estimate"),
                                     (disp_lo, float(row["ci_low"]), "ci_low"),
                                     (disp_hi, float(row["ci_high"]), "ci_high")):
                if abs(disp - src) > 0.02:
                    probs.append(f"{aid}.{label}: displayed {disp}, source {src:.4f}")

        p_disp = field("pVal")
        pm = re.search(r"([\d.]+)", p_disp or "")
        if pm and row.get("p_value"):
            try:
                if abs(float(pm.group(1)) - float(row["p_value"])) > 0.005:
                    probs.append(f"{aid}.p_value: displayed {pm.group(1)}, source {row['p_value']}")
            except ValueError:
                pass

    check("Target A-F Summary of Findings rows match the v26 results CSV",
          not probs, "\n".join(probs))


# Placeholder arm-level tuples that were live in dashboard/data.js before the
# 2026-09-10 remediation and describe no published result. Banning them by exact
# value is cheap and catches a revert that a lock comparison alone might miss if
# the lock itself were ever edited to match. Keyed by (bucket, study).
SUPERSEDED_OUTCOME_ARMS = {
    ("intraop_opioid", "Guo 2023"):   (620.0, 140.0, 30, 710.0, 160.0, 30),
    ("intraop_opioid", "Liang 2021"): (533.0, 125.0, 30, 582.0, 140.0, 30),
    ("intraop_opioid", "Pan 2023"):   (890.0, 210.0, 32, 960.0, 230.0, 32),
    ("intraop_opioid", "Wu 2022"):    (1100.0, 240.0, 30, 1380.0, 280.0, 30),
    ("intraop_opioid", "Lu 2021"):    (1580.0, 390.0, 190, 1720.0, 410.0, 188),
    ("intraop_opioid", "Xing 2022"):  (1330.0, 310.0, 29, 1620.0, 380.0, 29),
    ("intraop_opioid", "Zheng 2025"): (750.0, 180.0, 42, 820.0, 190.0, 43),
    ("flatus_time", "Yang 2024"):     (83.0, 12.0, 90, 85.0, 12.0, 90),
    ("flatus_time", "Yang 2020"):     (67.45, 10.42, 29, 73.55, 12.18, 28),
    ("flatus_time", "Xing 2022"):     (48.86, 11.45, 29, 51.07, 12.24, 29),
    ("flatus_time", "Lu 2022"):       (38.8, 8.2, 47, 46.2, 8.9, 47),
    ("flatus_time", "Ng 2013"):       (31.92, 8.64, 6, 32.16, 8.88, 6),
}
SUPERSEDED_OUTCOME_EVENTS = {
    ("rescue_analgesia", "Xie 2014"): (4, 10),
    ("rescue_analgesia", "Yu 2020"):  (5, 11),
    ("rescue_analgesia", "Tu 2024"):  (9, 17),
}

# The unit every pooled bucket must be expressed in once the lock's own
# conversions have been applied. A record carrying the raw statistic's unit
# (Ng 2013's flatus is reported in days but pooled in hours) is a unit-mixing
# bug, which is what this pins down.
OUTCOME_UNITS = {
    "opioid_24h": "mg IV MME",
    "opioid_48h": "mg IV MME",
    "opioid_72h": "mg IV MME",
    "intraop_opioid": "µg remifentanil",
    "flatus_time": "hours",
    "ponv_24h": "participants",
    "rescue_analgesia": "participants",
}


def _dashboard_outcome_records():
    """Every arm-bearing outcome record in data.js, as (bucket, study, record)."""
    for s in STUDIES:
        for bucket, rec in (s.get("outcomes") or {}).items():
            if isinstance(rec, dict):
                yield bucket, s.get("key"), rec


def t_dashboard_outcomes_are_generated_from_the_lock():
    """
    STRUCTURAL. The 2026-09-10 incident: dashboard/data.js was a hand-maintained
    second copy of numbers the locked datasets already held, and 15 of its
    arm-bearing cells had drifted into placeholder values matching no source and
    no lock. dashboard/app.js overwrites s.outcomes[key] from the GENERATED
    window.BROWSER_TARGETS at boot, so those numbers never reached a forest plot
    -- but they sat in the committed register and would have gone live the
    moment that overwrite was relaxed.

    scripts/sync_dashboard_outcomes.py now derives those records from the same
    lock browser_targets.js is built from. This asserts the sync is current, so
    a hand edit to data.js fails the build instead of shipping. It is the check
    that makes "data.js is generated, not authored" true rather than aspirational.
    """
    import io
    import contextlib
    sys.path.insert(0, str(ROOT / "scripts"))
    import sync_dashboard_outcomes as sync_mod

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = sync_mod.sync(check_only=True)
    check("dashboard/data.js outcome records are generated from the lock, not authored",
          rc == 0, buf.getvalue().strip())


def t_outcome_effects_recompute_from_their_arms():
    """
    DERIVED. meta_engine.js consumes the stored mean_diff/se (and rr/ci for
    binary outcomes) verbatim -- it never recomputes them from the arms. A record
    whose scalars disagree with its own arms therefore pools a number that
    describes nothing. Recompute every one of them.

    Direction is checked the same way: `favors` must follow the sign of the
    observed effect. Liang 2021 shipped as favors="Intervention" on a mean_diff
    of -49 when its true effect is +56.8 -- a false opioid-sparing signal that a
    value-only comparison would not have caught.
    """
    import math
    probs = []
    checked = 0
    for bucket, key, rec in _dashboard_outcome_records():
        has_cont = all(k in rec for k in
                       ("arm1_mean", "arm1_sd", "arm1_n", "arm2_mean", "arm2_sd", "arm2_n"))
        has_bin = all(k in rec for k in ("arm1_events", "arm2_events", "arm1_n", "arm2_n"))

        if has_cont:
            checked += 1
            m1, s1, n1 = float(rec["arm1_mean"]), float(rec["arm1_sd"]), float(rec["arm1_n"])
            m2, s2, n2 = float(rec["arm2_mean"]), float(rec["arm2_sd"]), float(rec["arm2_n"])
            if min(n1, n2) <= 0 or min(s1, s2) < 0:
                probs.append(f"{key}/{bucket}: non-positive n or negative SD")
                continue
            md = m1 - m2
            se = math.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
            if abs(float(rec.get("mean_diff", md)) - md) > 0.01:
                probs.append(f"{key}/{bucket}: mean_diff {rec['mean_diff']} != {md:.4f} from arms")
            if abs(float(rec.get("se", se)) - se) > 0.01:
                probs.append(f"{key}/{bucket}: se {rec['se']} != {se:.4f} from arms")
            for bound, want in (("ci_low", md - 1.96 * se), ("ci_upp", md + 1.96 * se)):
                if bound in rec and abs(float(rec[bound]) - want) > 0.01:
                    probs.append(f"{key}/{bucket}: {bound} {rec[bound]} != {want:.4f}")
            expect = "Intervention" if md < 0 else "Control"
            if "favors" in rec and rec["favors"] != expect:
                probs.append(f"{key}/{bucket}: favors '{rec['favors']}' contradicts mean_diff "
                             f"{md:.2f} (expected '{expect}')")

        elif has_bin:
            checked += 1
            e1, n1 = float(rec["arm1_events"]), float(rec["arm1_n"])
            e2, n2 = float(rec["arm2_events"]), float(rec["arm2_n"])
            # A denominator smaller than its event count is impossible; this is
            # what a randomised-vs-analysed n mix-up looks like numerically.
            for label, e, n in (("arm1", e1, n1), ("arm2", e2, n2)):
                if n <= 0:
                    probs.append(f"{key}/{bucket}: {label} denominator is {n}")
                elif e > n:
                    probs.append(f"{key}/{bucket}: {label} events {e} exceed denominator {n}")
            if min(n1, n2) <= 0:
                continue
            # Haldane-Anscombe, applied universally (review team decision
            # 2026-09-11) -- must match scripts/build_reference_data.py exactly,
            # or the register and the forest plot are on different scales.
            e1c, e2c, n1c, n2c = e1 + 0.5, e2 + 0.5, n1 + 1, n2 + 1
            rr = (e1c / n1c) / (e2c / n2c)
            se = math.sqrt(1 / e1c - 1 / n1c + 1 / e2c - 1 / n2c)
            if abs(float(rec.get("rr", rr)) - rr) > 0.001:
                probs.append(f"{key}/{bucket}: rr {rec['rr']} != {rr:.4f} from events "
                             f"(Haldane-Anscombe corrected)")
            if abs(float(rec.get("se", se)) - se) > 0.001:
                probs.append(f"{key}/{bucket}: se {rec['se']} != {se:.4f} from events")
            expect = "Intervention" if rr < 1 else "Control"
            if "favors" in rec and rec["favors"] != expect:
                probs.append(f"{key}/{bucket}: favors '{rec['favors']}' contradicts rr {rr:.3f}")

    check(f"Every dashboard outcome effect recomputes from its own arms ({checked} records)",
          not probs, "\n".join(probs))


def t_no_superseded_placeholder_outcomes():
    """
    ABSENCE. The 15 placeholder tuples the 2026-09-10 incident removed. Each is
    a plausible-looking value that describes no published result, which is
    exactly why they survived review for as long as they did. Ban them by value
    so a revert cannot reintroduce one quietly.
    """
    probs = []
    for bucket, key, rec in _dashboard_outcome_records():
        banned = SUPERSEDED_OUTCOME_ARMS.get((bucket, key))
        if banned and all(k in rec for k in ("arm1_mean", "arm1_sd", "arm1_n",
                                             "arm2_mean", "arm2_sd", "arm2_n")):
            got = tuple(float(rec[k]) for k in
                        ("arm1_mean", "arm1_sd", "arm1_n", "arm2_mean", "arm2_sd", "arm2_n"))
            if all(abs(a - b) <= 0.001 for a, b in zip(got, banned)):
                probs.append(f"{key}/{bucket}: superseded placeholder arms are live again {got}")
        banned_e = SUPERSEDED_OUTCOME_EVENTS.get((bucket, key))
        if banned_e and all(k in rec for k in ("arm1_events", "arm2_events")):
            got_e = (float(rec["arm1_events"]), float(rec["arm2_events"]))
            if all(abs(a - b) <= 0.001 for a, b in zip(got_e, banned_e)):
                probs.append(f"{key}/{bucket}: superseded placeholder events are live again {got_e}")
    check(f"No superseded placeholder outcome values survive "
          f"({len(SUPERSEDED_OUTCOME_ARMS) + len(SUPERSEDED_OUTCOME_EVENTS)} banned)",
          not probs, "\n".join(probs))


def t_outcome_units_are_not_mixed():
    """
    STRUCTURAL. Ng 2013 reports time to first flatus in DAYS and is pooled in
    HOURS; the lock row keeps the raw unit, so the generated record used to be
    labelled "days" while carrying hour values. Nothing would have caught a
    genuine days/hours mix-up in the pooled mean. Pin each bucket to the one
    unit its pooled estimate is expressed in, and require any record whose raw
    statistic differs to say so in `converted_from`.
    """
    probs = []
    for bucket, key, rec in _dashboard_outcome_records():
        want = OUTCOME_UNITS.get(bucket)
        if not want or "unit" not in rec:
            continue
        if not any(k in rec for k in ("arm1_mean", "arm1_events")):
            continue  # narrative/status-only record
        if rec["unit"] != want:
            # A record that says in its own note that it is outside the pooled
            # set may legitimately carry the raw published unit -- that is the
            # honest label. What must never happen is a raw statistic wearing
            # the pooled unit, which is the case this catches.
            declared_out = ("not in the locked" in str(rec.get("note", "")).lower()
                            or "not a 0" in str(rec.get("status", "")).lower()
                            or "not pooled" in str(rec.get("status", "")).lower())
            if not declared_out:
                probs.append(f"{key}/{bucket}: unit '{rec['unit']}' is not the pooled unit "
                             f"'{want}' and the record does not declare itself out of pool")
        if "converted_from" in rec and want not in ("participants",):
            if not re.search(r"[x×]\s*\d", str(rec["converted_from"])):
                probs.append(f"{key}/{bucket}: converted_from does not state the conversion factor")
    check("Pooled outcome records all carry their analysis unit, and declare any conversion",
          not probs, "\n".join(probs))


def t_legacy_compilers_carry_no_placeholders():
    """
    ABSENCE + STRUCTURAL. dashboard/compile_dashboard_data.py and its byte-identical
    twin 06_FINAL_ANALYSIS_V26/build_v26_dataset.py still hold hardcoded outcome
    dicts. They are not on the build path any more -- data.js is generated by
    scripts/sync_dashboard_outcomes.py -- but they held all 12 placeholder values
    after data.js had been corrected, so running either would have regenerated the
    2026-09-10 contamination wholesale.

    Ban the placeholder literals in both files, and assert the two stay identical
    so a fix can never land in one and not the other.
    """
    probs = []
    paths = [ROOT / "dashboard/compile_dashboard_data.py",
             ROOT / "06_FINAL_ANALYSIS_V26/build_v26_dataset.py"]
    texts = []
    for path in paths:
        if not path.exists():
            probs.append(f"{path.name} is missing")
            texts.append("")
            continue
        texts.append(path.read_text(encoding="utf-8"))

    # One distinctive literal per superseded record, as it appeared in these files.
    banned = {
        '"arm1_mean": 31.92': "Ng 2013 flatus placeholder",
        '"arm1_mean": 67.45': "Yang 2020 flatus placeholder",
        '"arm1_mean": 83.0, "arm1_sd": 12.0': "Yang 2024 flatus placeholder",
        '"arm1_mean": 48.86': "Xing 2022 flatus placeholder",
        '"arm1_mean": 38.8, "arm1_sd": 8.2': "Lu 2022 flatus placeholder",
        '"arm1_mean": 1100.0': "Wu 2022 intraop placeholder",
        '"arm1_mean": 1580.0': "Lu 2021 intraop placeholder",
        '"arm1_mean": 1330.0': "Xing 2022 intraop placeholder",
        '"arm1_mean": 750.0, "arm1_sd": 180.0': "Zheng 2025 intraop placeholder",
        '"arm1_mean": 620.0': "Guo 2023 intraop placeholder",
        '"arm1_mean": 533.0': "Liang 2021 intraop placeholder",
        '"arm1_mean": 890.0, "arm1_sd": 210.0': "Pan 2023 intraop placeholder",
        '"arm1_events": 4, "arm1_total": 20': "Xie 2014 rescue placeholder",
        '"arm1_events": 5, "arm1_total": 30': "Yu 2020 rescue placeholder",
        '"arm1_events": 9, "arm1_total": 77': "Tu 2024 rescue placeholder",
        "1.33 ± 0.36": "Ng 2013 fabricated day->hour provenance",
    }
    # The same fabricated narrative must not survive in the register either.
    # sync_dashboard_outcomes.py preserves `note` fields verbatim, so a rebase or
    # revert can carry it back in even when every number is correct.
    fabricated = "Originally reported in days (1.33 ± 0.36 vs 1.34 ± 0.37 days)"
    if fabricated in DATA_JS:
        probs.append("dashboard/data.js: Ng 2013's fabricated day->hour provenance is asserted "
                     "again (1.33/1.34 days, n=6/6 -- these appear nowhere in the source). The "
                     "corrective note may QUOTE those figures as superseded; it may not state "
                     "them as the source's own.")
    for path, text in zip(paths, texts):
        for literal, why in banned.items():
            if literal in text:
                probs.append(f"{path.name}: {why} is still hardcoded ({literal})")

    if all(texts) and texts[0] != texts[1]:
        probs.append("compile_dashboard_data.py and build_v26_dataset.py have diverged; "
                     "they must stay byte-identical")

    check(f"Legacy dataset compilers carry no superseded placeholder values "
          f"({len(banned)} banned, 2 files)",
          not probs, "\n".join(probs))


# Workbooks that are kept as the review's audit trail but must NOT feed any live
# analysis. Deleting them would destroy provenance for a registered review; the
# risk they actually carry is that a script quietly starts reading one. That is
# what this pins down. Keep in step with "TEAS EA Verification/README.md".
ARCHIVAL_WORKBOOKS = {
    "TEAS_EA_RECONCILED_MASTER_DATA_v20_PRIMARY_OPIOID_SET.xlsx": "v20",
    "TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx": "v32",
    "TEAS_EA_v32_SUPPLEMENTARY_MISSED_OUTCOMES_FOR_CLAUDE_CODE.xlsx": "v32 supplement",
}
MASTER_WORKBOOK = "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"


def t_archival_workbooks_feed_no_live_code():
    """
    STRUCTURAL. Five superseded master workbooks sit beside the current one. The
    review team's instinct is to delete them so nothing gets mixed up; the right
    answer is the opposite -- they are the audit trail for PROSPERO
    CRD420251090635, and two of them are still read by live code, so deleting is
    both destructive and build-breaking.

    What actually needs preventing is a script quietly reading a superseded
    workbook. This asserts that the workbooks marked archival in
    "TEAS EA Verification/README.md" are referenced by NO live analytical code,
    that the master still is, and that the README's own table has not drifted
    from what the code does.
    """
    verif = ROOT / "TEAS EA Verification"
    readme = verif / "README.md"
    probs = []

    if not readme.exists():
        check("Archival master workbooks feed no live analytical code", False,
              "TEAS EA Verification/README.md is missing -- it is what names the master")
        return

    # Live analytical code: the build path and the dashboard's own scripts.
    live = sorted(
        list((ROOT / "scripts").glob("*.py"))
        + list((ROOT / "dashboard").glob("*.py"))
        + list((ROOT / ".github/workflows").glob("*.yml"))
    )
    for path in live:
        if path.name in ("validate_dashboard.py",):
            continue  # this file names them in order to ban them
        text = path.read_text(encoding="utf-8", errors="ignore")
        for wb, label in ARCHIVAL_WORKBOOKS.items():
            if wb in text:
                probs.append(f"{path.relative_to(ROOT)} reads the archival {label} workbook "
                             f"({wb}); the master is {MASTER_WORKBOOK}")

    if not (verif / MASTER_WORKBOOK).exists():
        probs.append(f"the master workbook {MASTER_WORKBOOK} is missing")

    build_site = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
    if MASTER_WORKBOOK not in build_site:
        probs.append("scripts/build_site.py no longer names the master workbook")

    # The README's table is the human-readable half of this contract; if a
    # workbook exists on disk but the README does not mention it, the table has
    # drifted and the next person cannot tell which file is authoritative.
    readme_text = readme.read_text(encoding="utf-8")
    for wb in verif.glob("*.xlsx"):
        stem = wb.name.replace("TEAS_EA_RECONCILED_MASTER_DATA_", "").replace(".xlsx", "")
        if wb.name not in readme_text and stem not in readme_text:
            probs.append(f"{wb.name} is on disk but not listed in "
                         f"TEAS EA Verification/README.md")

    check(f"Archival master workbooks feed no live analytical code "
          f"({len(ARCHIVAL_WORKBOOKS)} archival, master = v34)",
          not probs, "\n".join(probs))


def t_pdf_extractions_are_provable_from_their_quotes():
    """
    STRUCTURAL. dashboard/pdf_extracted.js holds values read straight out of the
    source PDFs. After the placeholder incident, a number in this register is only
    worth having if a reader can check it, so every accepted value must carry the
    PDF, the page and the verbatim sentence -- and the value must actually appear
    in that sentence.

    This is what stops the extractor from drifting into the failure mode it exists
    to avoid: a plausible figure with no traceable origin. It also holds the
    "conflict" path honest, since an unresolved extraction must carry no value.
    """
    path = DASH / "pdf_extracted.js"
    if not path.exists():
        check("PDF-extracted values are provable from their own quotes", False,
              "dashboard/pdf_extracted.js is missing; run scripts/extract_baseline_from_pdfs.py")
        return
    data = json.loads(path.read_text(encoding="utf-8")
                      .split("window.PDF_EXTRACTED = ", 1)[1].rsplit(";", 1)[0])
    pdf_dir = ROOT / "TEAS EA Verification" / "Source PDFs"
    study_keys = {s["key"] for s in STUDIES}
    probs = []
    accepted = 0

    for key, rec in data.items():
        if key not in study_keys:
            probs.append(f"{key}: not a study in STUDIES_DATA")
        src = rec.get("source_pdf")
        if not src or not (pdf_dir / src).exists():
            probs.append(f"{key}: source_pdf {src!r} does not exist")
        for field, f in rec.items():
            if field == "source_pdf" or not isinstance(f, dict):
                continue
            if "conflict" in f:
                if "value" in f:
                    probs.append(f"{key}/{field}: carries both a conflict and a value")
                continue
            if "value" not in f:
                continue
            accepted += 1
            for required in ("page", "quote"):
                if not f.get(required):
                    probs.append(f"{key}/{field}: accepted value has no {required}")
            quote = str(f.get("quote", "")).lower()
            # Every token of the value must be visible in its own quote. Pulse
            # width legitimately carries several ("0.6 ms / 0.2 ms"), so check
            # each number rather than the joined string. Arm counts are often
            # written as words ("randomly divided into four groups"), so a digit
            # is satisfied by its own spelling too.
            words = {"2": "two", "3": "three", "4": "four", "5": "five"}
            for token in re.findall(r"\d+(?:\.\d+)?", str(f["value"])):
                spelled = words.get(token)
                if token in quote.replace(",", ""):
                    continue
                if spelled and spelled in quote:
                    continue
                probs.append(f"{key}/{field}: value {f['value']!r} is not present in its "
                             f"own quote — {quote[:90]!r}")
                break
            # A non-numeric value (anaesthesia technique) must still be grounded.
            if not re.search(r"\d", str(f["value"])):
                head = str(f["value"]).split()[0].lower()
                if head and head not in quote:
                    probs.append(f"{key}/{field}: value {f['value']!r} does not appear in its "
                                 f"own quote — {quote[:90]!r}")

    check(f"PDF-extracted values are provable from their own quotes "
          f"({accepted} accepted across {len(data)} papers)",
          not probs, "\n".join(probs))


def t_unlinked_rob2_cells_explain_themselves():
    """
    STRUCTURAL. The RoB 2 matrix's default view is the study-level overview, and
    every one of its 420 cells used to tell the reader that "a specific source
    quote for this result is not yet linked". That reads as an unfinished
    dashboard, but a study-level judgement is not a result-specific assessment --
    there is no per-result quote that could ever be attached to it.

    The remaining result-specific gaps are not unfinished either: each was checked
    individually and left unlinked because linking it would mean guessing between
    genuine register ties, legitimising a unit-of-analysis decision the review has
    paused on (Yeh 2010/2011 are the same trial twice), or inventing a quote for
    an outcome the source paper never reports (Yang 2024).

    So: every assessed result that has no source-quote link must have a recorded
    reason. A new gap appearing without one is what this catches.
    """
    links_path = DASH / "rob2_source_links.js"
    if not links_path.exists():
        check("Unlinked RoB 2 cells explain themselves", False, "rob2_source_links.js missing")
        return
    payload = json.loads(links_path.read_text(encoding="utf-8")
                         .split("window.ROB2_SOURCE_LINKS = ", 1)[1].rsplit(";", 1)[0])
    links = payload.get("links", {})
    reasons = payload.get("unlinked_reasons", {})
    by_id = {s["id"]: s["key"] for s in STUDIES}

    # Assessed results come from two places: data.js's own rob2_outcomes, and the
    # primary-outcome RoB 2 that build_reference_data.py injects into
    # primary_browser.js (Szmit 2021 reaches the matrix only that way).
    assessed = set()
    for s in STUDIES:
        for bucket, a in (s.get("rob2_outcomes") or {}).items():
            if bucket != "assessed_list" and isinstance(a, dict) and a.get("status") == "Assessed":
                assessed.add((s["id"], s["key"], bucket))
    pb_path = DASH / "primary_browser.js"
    if pb_path.exists():
        pb = json.loads(pb_path.read_text(encoding="utf-8")
                        .split("window.PRIMARY_BROWSER = ", 1)[1].rsplit(";", 1)[0])
        key_to_id = {v: k for k, v in by_id.items()}
        for key, rec in pb.items():
            if isinstance(rec.get("rob2"), dict) and rec["rob2"].get("status") == "Assessed":
                sid = key_to_id.get(key)
                if sid:
                    assessed.add((sid, key, "opioid_24h"))

    probs = []
    explained = 0
    for sid, key, bucket in sorted(assessed):
        if f"{sid}::{bucket}" in links:
            continue
        if f"{key}::{bucket}" in reasons:
            explained += 1
            continue
        probs.append(f"{key}/{bucket}: assessed but neither linked to a source quote nor given a "
                     f"recorded reason in UNLINKED_REASONS "
                     f"(scripts/build_rob2_source_links.py)")

    # The study-level view must keep its own branch. Without it, all 420 cells of
    # the matrix's DEFAULT view fall through to the coverage-gap wording again.
    app = (DASH / "app.js").read_text(encoding="utf-8")
    if "study-level consensus overview, not a judgement about one specific result" not in app:
        probs.append("app.js has lost the study-level explanation; the matrix's default view "
                     "would again tell readers a source quote is 'not yet linked' for a "
                     "judgement that is not result-specific")
    if "unlinked_reasons" not in app:
        probs.append("app.js no longer reads unlinked_reasons, so recorded explanations "
                     "would not reach the reader")

    check(f"Unlinked RoB 2 cells explain themselves "
          f"({len(links)} linked, {explained} explained)",
          not probs, "\n".join(probs))


# Country of CONDUCT can legitimately differ from the lead author's affiliation.
# Lee 2011 is the case: first affiliation Victoria University, Melbourne, but the
# paper states the patients were recruited at China Medical University Hospital,
# Taichung. The review team chose country of conduct, so the register holds
# Taiwan while an affiliation-based reading says Australia. That is correct, not
# a defect -- but it must be declared so it cannot be "fixed" back by mistake.
CONDUCT_NOT_AFFILIATION = {
    "Lee 2011": ("Taiwan", "Australia"),
}


def t_country_is_verified_country_of_conduct():
    """
    STRUCTURAL. The register used to record "China" for all 63 trials that had a
    country, which was wrong for eight of them and left seven blank. Country is
    now set from scripts/apply_country_of_conduct.py, where every value carries
    the sentence in the source publication it was read from.

    This asserts data.js still matches that table exactly, that each entry keeps
    its evidence, and that the only place the register departs from an
    affiliation-based reading is the declared conduct-vs-affiliation case.
    Getting this wrong changes what the review can claim about generalisability,
    so it should fail loudly rather than drift.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from apply_country_of_conduct import CONDUCT, META

    by_key = {s["key"]: s for s in STUDIES}
    probs = []
    for key, (country, evidence) in CONDUCT.items():
        s = by_key.get(key)
        if s is None:
            probs.append(f"{key}: declared in CONDUCT but not present in STUDIES_DATA")
            continue
        if s.get("country") != country:
            probs.append(f"{key}: register says {s.get('country')!r}, verified conduct is "
                         f"{country!r} -- run scripts/apply_country_of_conduct.py")
        if s.get("country_meta") != META.get(country):
            probs.append(f"{key}: country_meta does not match {country}")
        if not s.get("country_evidence"):
            probs.append(f"{key}: country set without the source sentence that supports it")
        elif s["country_evidence"] != evidence:
            probs.append(f"{key}: country_evidence has drifted from the verified quote")

    # Every study must now carry a country; "not reported" was the old state.
    missing = [s["key"] for s in STUDIES if not s.get("country")]
    if missing:
        probs.append(f"{len(missing)} study/studies still have no country: {missing[:5]}")

    # Where the source PDF's lead affiliation differs from the recorded conduct,
    # that difference must be a declared one.
    pdf_path = DASH / "pdf_extracted.js"
    if pdf_path.exists():
        extracted = json.loads(pdf_path.read_text(encoding="utf-8")
                               .split("window.PDF_EXTRACTED = ", 1)[1].rsplit(";", 1)[0])
        for s in STUDIES:
            rec = extracted.get(s["key"], {}).get("country")
            if not (isinstance(rec, dict) and rec.get("value") and s.get("country")):
                continue
            if rec["value"] != s["country"]:
                declared = CONDUCT_NOT_AFFILIATION.get(s["key"])
                if not declared:
                    probs.append(f"{s['key']}: conduct {s['country']!r} differs from the source's "
                                 f"lead affiliation {rec['value']!r} and is not declared in "
                                 f"CONDUCT_NOT_AFFILIATION")
                elif declared != (s["country"], rec["value"]):
                    probs.append(f"{s['key']}: declared conduct/affiliation pair {declared} no "
                                 f"longer matches ({s['country']!r}, {rec['value']!r})")

    countries = {s.get("country") for s in STUDIES}
    check(f"Country is the verified country of conduct "
          f"({len(CONDUCT)} verified from source, {len(countries)} countries represented)",
          not probs, "\n".join(probs))


def t_companion_publications_cannot_double_count():
    """
    STRUCTURAL. Yeh 2010 and Yeh 2011 are two reports of ONE three-arm trial of
    lumbar spinal surgery -- same author team, same cohort, the sham arm's
    figures identical between the papers. The review team decided on 2026-09-11
    that they count once.

    Formally reducing k from 70 to 69 is a change to the LOCKED v34 master and
    the PRISMA flow, not something the dashboard may do on its own -- build_site
    derives canonical_studies from the workbook and other checks here assert it
    is 70. So this asserts the thing that actually protects the analysis: the
    pair is declared as one unit, and neither report contributes independently
    to any pooled estimate. If someone later adds one of them to a synthesis,
    this fails.
    """
    by_key = {s["key"]: s for s in STUDIES}
    pairs = [("Yeh 2010", "Yeh 2011")]
    probs = []
    for primary, companion in pairs:
        p_rec, c_rec = by_key.get(primary), by_key.get(companion)
        if not p_rec or not c_rec:
            probs.append(f"{primary}/{companion}: one of the pair is missing from STUDIES_DATA")
            continue
        if c_rec.get("duplicate_report_of") != primary:
            probs.append(f"{companion}: not marked as a duplicate report of {primary}")
        if p_rec.get("companion_report") != companion:
            probs.append(f"{primary}: does not name {companion} as its companion report")
        for rec in (p_rec, c_rec):
            if not rec.get("unit_of_analysis_note"):
                probs.append(f"{rec['key']}: carries no unit-of-analysis note")
        # Neither may appear in a pooled set.
        for name, rec in ((primary, p_rec), (companion, c_rec)):
            pooled = [b for b, v in (rec.get("outcomes") or {}).items()
                      if isinstance(v, dict)
                      and (isinstance(v.get("mean_diff"), (int, float))
                           or isinstance(v.get("rr"), (int, float)))]
            if pooled:
                probs.append(f"{name}: contributes arm-level data to {pooled} -- a companion "
                             f"publication pair must not both enter a synthesis; resolve the "
                             f"unit of analysis before pooling either")
    # The counts the review reports must follow from the linkage, not be typed in.
    import json as _json
    meta_path = ROOT / "_site" / "build-meta.json"
    if meta_path.exists():
        meta = _json.loads(meta_path.read_text(encoding="utf-8"))
        reports = meta.get("canonical_reports")
        studies = meta.get("included_studies")
        companions = meta.get("companion_reports")
        if (reports, studies, companions) != (len(STUDIES), len(STUDIES) - len(pairs), len(pairs)):
            probs.append(f"build-meta reports/studies/companions = "
                         f"{reports}/{studies}/{companions}, expected "
                         f"{len(STUDIES)}/{len(STUDIES) - len(pairs)}/{len(pairs)}")
    # The dashboard must state the study count, not the report count, as k.
    html = (DASH / "index.html").read_text(encoding="utf-8")
    if "69 studies / 70 reports" not in html:
        probs.append("index.html no longer distinguishes studies from reports in the "
                     "Study Explorer label")
    app_js = (DASH / "app.js").read_text(encoding="utf-8")
    if "duplicate_report_of" not in app_js:
        probs.append("app.js no longer excludes companion reports from the study count")

    check(f"Companion publications are declared and cannot double-count "
          f"({len(pairs)} pair; {len(STUDIES)} reports = {len(STUDIES) - len(pairs)} studies)",
          not probs, "\n".join(probs))


def t_quarantine_registry_is_honest():
    """
    STRUCTURAL. dashboard/outcome_quarantine.js withholds an outcome from being
    read as verified. It is only useful if it cannot drift in either direction:
    an outcome must not stay quarantined once its records are verified (which
    would understate the evidence), and must name only real, live outcomes.
    """
    src = (DASH / "outcome_quarantine.js").read_text(encoding="utf-8")
    body = src.split("window.OUTCOME_QUARANTINE = ", 1)[1].rsplit(";", 1)[0]
    entries = re.findall(r"^\s{2}(\w+):\s*\{", body, re.M)
    live = set(json.loads((DASH / "meta_outcomes.js").read_text(encoding="utf-8")
                          .split("window.META_OUTCOMES = ", 1)[1].rsplit(";", 1)[0]))
    probs = [f"quarantined outcome '{e}' is not a live Meta Lab outcome"
             for e in entries if e not in live]
    for e in entries:
        block = body[body.index(f"{e}: {{"):]
        if "reason" not in block[:block.index("}")]:
            probs.append(f"quarantined outcome '{e}' carries no reason")
    check(f"Outcome quarantine registry is honest ({len(entries)} quarantined)",
          not probs, "\n".join(probs))


def t_rob2_source_links_match_registers():
    """
    Every RoB 2 matrix cell claiming a specific, source-quoted rationale must
    still be backed by a real row in the RoB 2 registers -- and the coverage
    figure it reports must be honest.

    Independently re-derives scripts/build_rob2_source_links.py's join (same
    conservative keyword/timepoint rule, matching only when it resolves to
    exactly one candidate) and compares every linked domain quote against the
    source. A quote that no longer matches its claimed source row -- or a
    link this run cannot independently reproduce -- would mean the dashboard
    is showing a "specific source quote" that is not actually traceable,
    which is the one thing this feature exists to avoid.
    """
    path = DASH / "rob2_source_links.js"
    if not path.exists():
        check("RoB 2 source-quote links match the review's RoB 2 registers", False,
              "dashboard/rob2_source_links.js missing -- run build_rob2_source_links.py")
        return
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_rob2_source_links as bsl

    src = path.read_text(encoding="utf-8")
    shipped = json.loads(src[src.index("window.ROB2_SOURCE_LINKS = ") +
                             len("window.ROB2_SOURCE_LINKS = "):src.rindex(";")])
    live = bsl.build()

    probs = []
    if shipped.get("total_assessed_results") != live["total_assessed_results"]:
        probs.append(f"total_assessed_results: shipped {shipped.get('total_assessed_results')}, "
                     f"re-derived {live['total_assessed_results']}")
    if set(shipped.get("links", {})) != set(live["links"]):
        missing = set(live["links"]) - set(shipped.get("links", {}))
        extra = set(shipped.get("links", {})) - set(live["links"])
        if missing:
            probs.append(f"{len(missing)} link(s) re-derive but are not shipped, "
                         f"e.g. {sorted(missing)[:3]}")
        if extra:
            probs.append(f"{len(extra)} shipped link(s) no longer re-derive, "
                         f"e.g. {sorted(extra)[:3]}")
    for key, live_link in live["links"].items():
        shipped_link = shipped.get("links", {}).get(key)
        if not shipped_link:
            continue
        # JSON object keys are always strings, so the shipped file's domains
        # dict round-trips as {"1": ...}; the freshly-built Python dict still
        # has int keys ({1: ...}). Normalize both to strings before comparing
        # -- an earlier version compared them directly and always disagreed,
        # regardless of whether the content actually matched.
        live_domains = {str(k): v for k, v in live_link["domains"].items()}
        if shipped_link.get("domains") != live_domains:
            probs.append(f"{key}: shipped domain quotes differ from the re-derived source")
        if shipped_link.get("source_pdf") != live_link["source_pdf"]:
            probs.append(f"{key}: shipped source_pdf {shipped_link.get('source_pdf')!r} != "
                         f"re-derived {live_link['source_pdf']!r}")
        # matched_outcome/matched_timepoint identify WHICH register row the
        # domains/source_pdf above were pulled from -- checking only the
        # pulled content and not this would miss the record being corrupted
        # to point at the wrong row while (coincidentally) still shipping
        # correct-looking domain text. Found by mutation-testing this check
        # against exactly that: an earlier version passed clean.
        for field in ("matched_outcome", "matched_timepoint"):
            if shipped_link.get(field) != live_link[field]:
                probs.append(f"{key}: shipped {field} {shipped_link.get(field)!r} != "
                             f"re-derived {live_link[field]!r}")
    check("RoB 2 source-quote links match the review's RoB 2 registers",
          not probs, "\n".join(probs))


def t_forest_context_matches_stata_log():
    """
    The per-study forest-plot context table must still match the Stata log it
    claims to be derived from.

    build_forest_context.py already refuses to WRITE a mismatched file (wrong
    study set, weights not summing to ~100%); this independently re-derives
    the same numbers from the log at validation time and compares them to
    what shipped, so a hand-edit of the generated file -- or a stale file left
    behind after the log changed -- is caught here too, not only at generation
    time.
    """
    path = DASH / "forest_context.js"
    if not path.exists():
        check("Forest-plot context matches the Stata log", False,
              "dashboard/forest_context.js missing -- run build_forest_context.py")
        return
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_forest_context as bfc

    src = path.read_text(encoding="utf-8")
    shipped = json.loads(src[src.index("window.FOREST_CONTEXT = ") +
                            len("window.FOREST_CONTEXT = "):src.rindex(";")])
    probs = []
    live = bfc.build()
    if len(shipped.get("figures", [])) != len(live["figures"]):
        probs.append(f"{len(shipped.get('figures', []))} figures shipped, "
                     f"{len(live['figures'])} re-derived")
    for s_fig, l_fig in zip(shipped.get("figures", []), live["figures"]):
        if s_fig.get("figure") != l_fig["figure"]:
            probs.append(f"figure mismatch: {s_fig.get('figure')!r} vs {l_fig['figure']!r}")
            continue
        s_rows = {r["study"]: r for r in s_fig.get("rows", [])}
        l_rows = {r["study"]: r for r in l_fig["rows"]}
        if set(s_rows) != set(l_rows):
            probs.append(f"{l_fig['figure']}: study set differs from the log")
        for study, l_row in l_rows.items():
            s_row = s_rows.get(study)
            if not s_row:
                continue
            for field in ("estimate", "ci_low", "ci_high", "weight_pct"):
                if abs(float(s_row.get(field, 0)) - float(l_row[field])) > 1e-6:
                    probs.append(f"{l_fig['figure']} {study}.{field}: shipped "
                                 f"{s_row.get(field)}, log says {l_row[field]}")
    check("Forest-plot context matches the Stata log it is derived from",
          not probs, "\n".join(probs))


def t_static_kpi_fallback_matches_rendered_content():
    """
    The headline KPI card's static HTML must say the same thing as the JS that
    (sometimes) overwrites it.

    Found the hard way: renderKPIs() was edited to correctly distinguish the
    TEAS-primary / EA-supportive hierarchy, all local and CI checks passed,
    and the deployed page still showed the old "PRIMARY: TEAS & EA
    Modality-Specific" text. renderKPIs() is not called for every tab on
    initial page load, so index.html's static fallback markup for
    #kpi-effect-title and #kpi-pooled-badge is not a pre-render placeholder --
    it is live content for whichever tab loads before renderKPIs() first
    fires, and it silently diverged from the JS the moment the two stopped
    being identical strings by coincidence.

    Pins the static text to a fragment of what renderKPIs() actually sets for
    filterModality === 'all', so the two cannot drift apart again without this
    failing.
    """
    app = (DASH / "app.js").read_text(encoding="utf-8")
    html = (DASH / "index.html").read_text(encoding="utf-8")

    m = re.search(
        r"filterModality === 'all'.*?effectBadgeEl\.innerHTML = '<span[^>]*>([^<]+)</span>",
        app, re.S)
    probs = []
    if not m:
        probs.append("could not find the filterModality === 'all' badge text in app.js")
    else:
        badge_text = m.group(1)
        if badge_text not in html:
            probs.append(
                "index.html's static #kpi-pooled-badge fallback does not match "
                f"renderKPIs()'s all-modality text: {badge_text!r} not found in index.html "
                "-- the static fallback is live content for tabs where renderKPIs() has not "
                "yet run, not dead pre-render markup, and must be kept in sync by hand")
    check("Static KPI card fallback text matches what renderKPIs() computes for the "
          "all-modality view", not probs, "\n".join(probs))


def t_computed_not_reported_is_complete_and_unrated():
    """
    The computed-but-not-reported panel exists so that an analysis the review
    fitted and did not carry forward is visible with its reason, instead of
    existing only inside a results CSV where a reader cannot find it.

    Two things must hold. Every analysis in the v26 results file must be
    accounted for -- reported, duplicate, sensitivity variant, or listed here
    with a reason -- so the panel cannot quietly omit an awkward one. And no
    row here may carry a GRADE certainty, because none was adopted for these;
    attaching one would be the unplanned outcome addition the panel exists to
    make visible rather than commit.
    """
    p = ROOT / "dashboard" / "computed_not_reported.js"
    if not p.exists():
        check("Computed-but-not-reported analyses are listed with their reasons",
              False, "dashboard/computed_not_reported.js is missing")
        return
    txt = p.read_text(encoding="utf-8")
    C = json.loads(txt[txt.index("{"):].rstrip().rstrip(";"))
    probs = []

    v26 = read_csv(ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS"
                   / "master_reconciled_results_v26.csv")
    accounted = C["reported"] + C["duplicate"] + C["sensitivity"] + C["not_reported"]
    if accounted != len(v26):
        probs.append(f"{accounted} analyses classified but the results file holds {len(v26)}")
    if C["total_analyses"] != len(v26):
        probs.append(f"payload says {C['total_analyses']} analyses, file holds {len(v26)}")

    banned = {"grade", "certainty", "grade_level"}
    for r in C["rows"]:
        if not (r.get("why") or "").strip():
            probs.append(f"{r.get('analysis_id')}: listed without a reason")
        if not (r.get("detail") or "").strip():
            probs.append(f"{r.get('analysis_id')}: reason has no explanation")
        stray = banned & set(r)
        if stray:
            probs.append(f"{r.get('analysis_id')}: carries a certainty field {sorted(stray)} "
                         "though none was adopted for it")
        # A ratio is null at 1; carrying the null per row is what stops the
        # renderer testing a risk ratio against zero.
        if r.get("null_value") not in (0.0, 1.0):
            probs.append(f"{r.get('analysis_id')}: null_value {r.get('null_value')!r}")
    check("Computed-but-not-reported analyses are listed with their reasons, and carry no "
          "certainty rating", not probs, "\n".join(probs))



# ═══════════════════════════════════════════════════════════════════════════
# REPORTS vs STUDIES vs RESULTS — unit discipline (2026-09-12)
# ═══════════════════════════════════════════════════════════════════════════
# The register holds one row per included REPORT. Dashboard copy and dashboard
# code both used to call that 70 studies, 70 trials and 70 RCTs interchangeably,
# and summed its population field into a "randomized patient" total that
# double-counted the one linked cohort. These checks hold the three units apart.

COHORT_OVERLAP_JS = DASH / "cohort_overlap.js"


def _cohort_overlap() -> dict:
    raw = COHORT_OVERLAP_JS.read_text(encoding="utf-8")
    return json.JSONDecoder().raw_decode(raw.split("window.COHORT_OVERLAP = ", 1)[1])[0]


def t_cohort_overlap_scan_is_current():
    """
    GENERATED. dashboard/cohort_overlap.js is the output of
    scripts/build_cohort_overlap_scan.py. If it is hand-edited, or the register
    changes without the scan being re-run, the report-to-study reconciliation on
    screen stops following from the data it claims to summarise.
    """
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_cohort_overlap_scan.py"),
                        "--check"], capture_output=True, text=True, cwd=ROOT)
    check("t_cohort_overlap_scan_is_current", r.returncode == 0,
          (r.stdout + r.stderr).strip())


def t_report_and_study_counts_follow_from_the_linkage():
    """
    DERIVED. 70 reports and 69 studies are not two typed-in numbers: the gap is
    exactly the set of records carrying duplicate_report_of. Asserting that here
    means a future second linked cohort cannot leave "69" stale on the page.
    """
    companions = [s["key"] for s in STUDIES if s.get("duplicate_report_of")]
    reports, studies = len(STUDIES), len(STUDIES) - len(companions)
    co = _cohort_overlap()
    probs = []
    if co["reports"] != reports or co["studies"] != studies:
        probs.append(f"scan says {co['reports']}/{co['studies']}, register gives {reports}/{studies}")
    if (reports, studies) != (70, 69):
        probs.append(f"register now gives {reports} reports / {studies} studies; every "
                     f"hardcoded 70/69 on the page needs re-deriving")
    # The scan must re-find every declared link, so the detection rule cannot
    # silently stop working while still reporting a clean result.
    declared = {frozenset((d["study_record"], d["companion_report"])) for d in co["declared_links"]}
    found = {frozenset(c["studies"]) for c in co["candidates"] if c["status"] == "confirmed"}
    if declared != found:
        probs.append(f"declared links {declared} not all re-found by the scan ({found})")
    check("t_report_and_study_counts_follow_from_the_linkage", not probs, "; ".join(probs))


def t_trial_level_tallies_exclude_companion_reports():
    """
    STRUCTURAL. Specialty, modality, comparator, country and every baseline
    characteristic are properties of a TRIAL. The renderers that tally them must
    go through uniqueTrials(), or a companion report adds a second tally mark for
    a cohort already counted.
    """
    probs = []
    if "function uniqueTrials(" not in APP:
        probs.append("uniqueTrials() helper is gone")
    # renderOverview, renderStudyExplorer and summarisePopulation each tally
    # trial properties and must derive a trials list first.
    for fn in ("function renderOverview(", "function renderStudyExplorer(",
               "function summarisePopulation("):
        if fn not in APP:
            probs.append(f"{fn.strip('function (')} missing")
            continue
        body = APP[APP.index(fn): APP.index(fn) + 2600]
        if "uniqueTrials(" not in body:
            probs.append(f"{fn.strip('function (')} tallies trial properties without uniqueTrials()")
    # prismaPopulationSummary must not tally modality/comparator over raw rows.
    start = APP.index("function prismaPopulationSummary(")
    body = APP[start: APP.index("\n}", start)]
    if "uniqueTrials(" not in body:
        probs.append("prismaPopulationSummary counts modality/comparator over reports")
    check("t_trial_level_tallies_exclude_companion_reports", not probs, "; ".join(probs))


def t_participant_totals_count_each_trial_once():
    """
    DERIVED. Participants belong to a trial. Summing population.total_n over all
    70 rows counts the linked Yeh cohort twice; the published total must be the
    69-trial sum, and the figure it replaced must not still appear as a live claim.
    """
    companions = {s["key"] for s in STUDIES if s.get("duplicate_report_of")}
    over_reports = sum(s["population"]["total_n"] for s in STUDIES)
    over_studies = sum(s["population"]["total_n"] for s in STUDIES if s["key"] not in companions)
    co = _cohort_overlap()
    probs = []
    if co["participants"]["analysed_across_reports"] != over_reports:
        probs.append("scan's report-level total disagrees with the register")
    if co["participants"]["analysed_across_studies"] != over_studies:
        probs.append("scan's trial-level total disagrees with the register")
    # The live figure on the PRISMA card is the trial-level one.
    if f"{over_studies:,}" not in HTML:
        probs.append(f"the trial-level participant total {over_studies:,} appears nowhere in index.html")
    # The report-level sum may only appear where it is explicitly described as
    # the superseded 70-report figure.
    live = strip_withdrawal_prose(HTML)
    for m in re.finditer(re.escape(f"{over_reports:,}"), live):
        window = live[max(0, m.start() - 320): m.end() + 320]
        if not re.search(r"70-report|across reports|earlier figure|previously|superseded|double-count",
                         window, re.I):
            probs.append(f"the 70-report sum {over_reports:,} appears as a live claim without "
                         f"saying it is the report-level figure")
            break
    check("t_participant_totals_count_each_trial_once", not probs, "; ".join(probs))


def t_analysed_total_is_not_labelled_randomised():
    """
    ABSENCE. population.total_n is the ANALYSED denominator -- the one the
    syntheses use. It was rendered as "randomized surgical patients" in the KPI
    strip and as "total randomized patients" on the PRISMA card. A randomised
    total is a quantity this review cannot produce, so the word randomized must
    not be the label attached to one of these sums.

    The test is positional, which is what makes it specific: the LABEL is the text
    immediately following the interpolated number. "69 randomized trials" in the
    same sentence is fine -- that is a trial count, correctly described; what is
    banned is "<analysed sum> randomized ... patients".
    """
    SUM = re.compile(r"\$\{\s*(?:totalN|analysedPatients|analysedTotal|over_studies)\b"
                     r"[^}]*\}")
    probs = []
    for fn in ("function renderKPIs(", "function prismaPopulationSummary(",
               "function renderPopulationSummary("):
        if fn not in APP:
            probs.append(f"{fn.strip('function (')} is gone")
            continue
        start = APP.index(fn)
        body = APP[start: start + 4000]
        for m in SUM.finditer(body):
            label = body[m.end(): m.end() + 90]
            if re.search(r"randomi[sz]ed", label, re.I):
                probs.append(f"{fn.strip('function (')} labels the sum {m.group(0)!r} as "
                             f"{label.strip()[:50]!r}")
    check("t_analysed_total_is_not_labelled_randomised", not probs, "; ".join(probs))


def t_no_review_wide_randomised_total_is_published():
    """
    DERIVED. A randomised participant total would need a randomised denominator
    from every trial. The register records one for a handful of contrasts and the
    PDF extraction records whole-trial figures for a few more -- two different
    quantities, neither covering the review. The scan must therefore refuse to
    publish a total, and the page must say so rather than leaving the reader to
    assume the analysed figure is a randomised one.
    """
    co = _cohort_overlap()["participants"]
    probs = []
    if co["randomised_total_publishable"] is not False:
        probs.append("the scan claims a review-wide randomised total is publishable")
    if not co["randomised_total_reason"]:
        probs.append("no reason recorded for withholding a randomised total")
    if "randomized participant total is not reported" not in HTML:
        probs.append("index.html does not state that no review-wide randomized total is reported")
    if "randomisedCell(" not in APP:
        probs.append("the explorer has no per-trial randomised cell, so NR cannot be distinguished "
                     "from an analysed denominator standing in for it")
    check("t_no_review_wide_randomised_total_is_published", not probs, "; ".join(probs))


def t_possible_shared_cohorts_are_flagged_not_merged():
    """
    STRUCTURAL. The scan flags report pairs that may describe one cohort, and the
    review team adjudicates them against the source PDFs. Neither state licenses
    the dashboard to act: a flagged pair and an adjudicated-separate pair both
    still count as two studies, and only a link DECLARED in the register (via
    duplicate_report_of) ever reduces the study count.

    An adjudication must also stay honest about its own basis: it names a decision
    record that exists, carries the evidence it rested on, and does not quietly
    become the reason the pair stopped being detected -- the scan itself fails the
    build if it can no longer find a pair it has an adjudication for.
    """
    co = _cohort_overlap()
    flagged = [c for c in co["candidates"] if c["status"] == "flagged_for_review"]
    resolved = [c for c in co["candidates"] if c["status"] == "adjudicated_separate"]
    declared = {s["key"] for s in STUDIES if s.get("duplicate_report_of")}
    probs = []
    for c in flagged + resolved:
        for k in c["studies"]:
            if k in declared:
                probs.append(f"{k} is an unmerged candidate AND merged away in the register -- "
                             f"the scan and the register disagree about whether this is settled")
    for c in resolved:
        a = c.get("adjudication") or {}
        if a.get("verdict") != "separate":
            probs.append(f"{c['studies']}: adjudicated_separate without a 'separate' verdict")
        if not a.get("evidence"):
            probs.append(f"{c['studies']}: adjudicated separate with no evidence recorded")
        rec = a.get("record")
        if not rec or not (ROOT / rec).exists():
            probs.append(f"{c['studies']}: decision record {rec!r} does not exist")
    if flagged and "possible-shared-cohort" not in APP:
        probs.append("flagged candidates are never rendered, so a reader cannot see them")
    if resolved and "pop-resolved" not in APP:
        probs.append("adjudicated candidates are never rendered, so the question and its answer "
                     "vanish from the page once settled")
    css = (DASH / "styles.css").read_text(encoding="utf-8")
    for cls in (("pop-flags",) if flagged else ()) + (("pop-resolved",) if resolved else ()):
        if cls not in css:
            probs.append(f"the .{cls} panel has no styles")
    check("t_possible_shared_cohorts_are_flagged_not_merged", not probs,
          f"{len(flagged)} open, {len(resolved)} adjudicated: " + "; ".join(probs))


def t_baseline_conflicts_are_surfaced_not_corrected():
    """
    STRUCTURAL. Two register rows once carried one paper's arm data beside the
    other paper's citation, because the two locked sheets named different
    publications for the same key. That was resolved on 2026-09-12 by adopting the
    convention 15 of 16 files already used.

    What this holds now:
      * an OPEN attribution conflict must still describe the register (if the rows
        stop being crossed it is resolved, and must be withdrawn, not left stale);
      * a RESOLVED one must keep its record, name the script that applied it, and
        keep the superseded readings on file so they are not re-raised;
      * the resolution must actually hold in the data -- each row's sex denominator
        and its own arm denominator must now agree.
    """
    co = _cohort_overlap()
    by_key = {s["key"]: s for s in STUDIES}
    probs = []

    def crossed(studies: list[str]) -> bool:
        for k in studies:
            pop = (by_key.get(k) or {}).get("population") or {}
            others = [by_key[o]["population"]["arm1_n"] for o in studies
                      if o != k and o in by_key]
            m = re.match(r"\s*\d+\s*/\s*(\d+)", str(pop.get("arm1_female") or ""))
            if m and int(m.group(1)) in others:
                return True
        return False

    for f in co.get("attribution_conflicts", []):
        for k in f["studies"]:
            if k not in by_key:
                probs.append(f"{k}: attribution conflict recorded for a study not in the register")
        if not f.get("evidence"):
            probs.append(f"{f['studies']}: attribution conflict with no evidence recorded")
        if not f.get("decision_needed"):
            probs.append(f"{f['studies']}: no decision recorded as needed, so the flag has no exit")
        if not crossed(f["studies"]):
            probs.append(f"{f['studies']}: the records are no longer crossed -- the conflict looks "
                         f"resolved, so withdraw the flag with its evidence rather than leaving it")

    for f in co.get("resolved_attribution", []):
        for field in ("verdict", "why", "applied_by", "record", "not_touched"):
            if not f.get(field):
                probs.append(f"{f['studies']}: resolution records no {field}")
        rec = f.get("record")
        if rec and not (ROOT / rec).exists():
            probs.append(f"{f['studies']}: decision record {rec} does not exist")
        applied = f.get("applied_by")
        if applied and not (ROOT / applied).exists():
            probs.append(f"{f['studies']}: {applied} does not exist, so the correction cannot "
                         f"be re-checked or reversed")
        if not f.get("superseded_findings"):
            probs.append(f"{f['studies']}: the readings this replaced are not recorded, so they "
                         f"can be re-raised as if new")
        # The resolution has to be true of the data, not just asserted.
        if crossed(f["studies"]):
            probs.append(f"{f['studies']}: recorded as resolved, but the rows are still crossed "
                         f"-- a sex denominator still matches the other record's arm size")
        for k in f["studies"]:
            pop = (by_key.get(k) or {}).get("population") or {}
            m = re.match(r"\s*\d+\s*/\s*(\d+)", str(pop.get("arm1_female") or ""))
            if m and int(m.group(1)) != pop.get("arm1_n"):
                probs.append(f"{k}: sex denominator {m.group(1)} still disagrees with arm1_n "
                             f"{pop.get('arm1_n')} after the identity correction")

    if co.get("attribution_conflicts") and "Record attribution" not in APP:
        probs.append("open attribution conflicts are never rendered")
    if co.get("resolved_attribution") and "Identity resolved" not in APP:
        probs.append("the resolution is never rendered, so the answer disappears from the page")

    # The cross-sheet screen must stay wired up, and must still describe the lock.
    import csv as _csv
    sheets = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets"
    lock_rows = co.get("locked_sheet_disagreements", [])
    if lock_rows and "locked-sheets-disagree" not in APP:
        probs.append("locked-sheet disagreements are computed but never rendered")
    if any(d.get("exchanged_with") for d in lock_rows):
        probs.append("an identity split is open again: the two locked sheets have exchanged a "
                     "study's figures between keys")
    af = sheets / "Outcome_Data_AF_LOCK.csv"
    if lock_rows and af.exists():
        known = {}
        for r in _csv.DictReader(af.open(encoding="utf-8-sig")):
            for field in ("Analyzednintervention", "Analyzedncomparator",
                          "Randomizednintervention", "Randomizedncomparator"):
                try:
                    known.setdefault(r["Canonicalstudy"], set()).add(int(float(r[field])))
                except (ValueError, TypeError, KeyError):
                    pass
        for d in lock_rows:
            got = sorted(known.get(d["study"], set()))
            if got != d["af_lock_arm_sizes"]:
                probs.append(f"{d['study']}: screen reports AF_LOCK arms "
                             f"{d['af_lock_arm_sizes']}, sheet holds {got} -- the lock changed "
                             f"and the screen was not re-run")
            if not d["unaccounted"]:
                probs.append(f"{d['study']}: reported as a disagreement with nothing "
                             f"unaccounted for -- withdraw it rather than leaving it standing")

    # An adjudicated denominator must say why, and must NOT have been quietly
    # corrected instead -- the whole point of the category is that no correct value
    # exists to restore.
    for d in co.get("denominator_mismatches", []):
        if d.get("explained_by") and not d.get("explained_detail"):
            probs.append(f"{d['study']} {d['arm']}: adjudicated with no reason recorded")
    if any(d.get("explained_by") for d in co.get("denominator_mismatches", [])) \
            and "Denominator adjudicated" not in APP:
        probs.append("adjudicated denominators are never rendered")

    # An adjudicated cohort-size disagreement must say why it is unresolvable AND
    # why nothing rests on it -- otherwise "adjudicated" is just a way of hiding an
    # open question. The second claim is checked against the register: a trial whose
    # randomised N is genuinely unknown must not be carrying one.
    for d in co.get("cohort_size_disagreements", []):
        if d.get("status") != "adjudicated":
            continue
        for field in ("verdict", "why_nothing_depends_on_it", "adjudicated_on", "record"):
            if not d.get(field):
                probs.append(f"{d['studies']}: adjudicated without recording {field}")
        rec = d.get("record")
        if rec and not (ROOT / rec).exists():
            probs.append(f"{d['studies']}: decision record {rec} does not exist")
        for k in d["studies"]:
            pop = (by_key.get(k) or {}).get("population") or {}
            whole = ((json.loads(re.search(r"window\.PDF_EXTRACTED = (\{.*\});",
                     (DASH / "pdf_extracted.js").read_text(encoding="utf-8"), re.S).group(1))
                     ).get(k) or {}).get("randomised_n") if (DASH / "pdf_extracted.js").exists() else None
            if whole:
                probs.append(f"{k}: a whole-trial randomised N of {whole.get('value')} is "
                             f"recorded, so the cohort size is not unknown and the adjudication "
                             f"is stale")
    if any(d.get("status") == "adjudicated" for d in co.get("cohort_size_disagreements", [])) \
            and "Cohort size adjudicated" not in APP:
        probs.append("an adjudicated cohort size is never rendered")

    for d in co.get("denominator_mismatches", []):
        pop = (by_key.get(d["study"]) or {}).get("population") or {}
        held = pop.get(d["arm"] + "_female")
        if held != d["female"]:
            probs.append(f"{d['study']} {d['arm']}: screen reports {d['female']!r}, "
                         f"register holds {held!r}")
        if pop.get(d["arm"] + "_n") != d["analysed_n"]:
            probs.append(f"{d['study']} {d['arm']}: screen reports analysed n={d['analysed_n']}, "
                         f"register holds {pop.get(d['arm'] + '_n')}")
    check("t_baseline_conflicts_are_surfaced_not_corrected", not probs, "; ".join(probs[:4]))


def t_yeh_identity_is_the_adopted_convention():
    """
    DERIVED. The 2026-09-12 identity decision must hold in all three places it was
    applied -- the v34 workbook's Study_Master sheet, its exported CSV, and the
    register -- and the arm denominators must NOT have moved with it.

    scripts/apply_yeh_identity_correction.py --check is the authority; running it
    here means the decision cannot silently come undone in one artefact.
    """
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "apply_yeh_identity_correction.py"),
                        "--check"], capture_output=True, text=True, cwd=ROOT)
    probs = []
    if r.returncode != 0:
        probs.append((r.stdout + r.stderr).strip()[:400])
    # The denominators are the half the decision did not touch; they still have to
    # trace to Outcome_Data_AF_LOCK, which t_population_denominators asserts for
    # every study. Here, just pin the two rows the correction ran over.
    expected = {"Yeh 2010": (33, 30), "Yeh 2011": (30, 30)}
    for s in STUDIES:
        if s["key"] in expected:
            got = (s["population"]["arm1_n"], s["population"]["arm2_n"])
            if got != expected[s["key"]]:
                probs.append(f"{s['key']}: arms are {got}, expected {expected[s['key']]} -- the "
                             f"identity correction must never move a denominator")
    check("t_yeh_identity_is_the_adopted_convention", not probs, "; ".join(probs))


def t_baseline_denominators_are_unique_trials():
    """
    STRUCTURAL. "Age reported in 52/69" is a statement about trials. Rendering it
    over 70 rows inflates the denominator and, for the linked cohort, counts one
    trial's reporting twice. summarisePopulation must therefore reduce to trials
    before it counts anything, and must expose the report count separately so the
    display can explain the gap.
    """
    start = APP.index("function summarisePopulation(")
    body = APP[start: APP.index("\n}\n", start)]
    probs = []
    if "const studies = uniqueTrials(" not in body:
        probs.append("summarisePopulation does not reduce to unique trials")
    if "reportStudyCounts(" not in body:
        probs.append("summarisePopulation does not carry the report count alongside")
    # Missing data must stay missing. A denominator check is worthless if the
    # numerator was padded with zeros.
    render = APP[APP.index("function renderPopulationSummary("):]
    render = render[: render.index("\n}\n")]
    if "|| 0" in render.replace("|| 0)", "XX"):
        probs.append("renderPopulationSummary substitutes 0 for a missing value somewhere")
    if "isNotReported" not in APP or "nr-tag" not in APP:
        probs.append("the not-reported path is gone")
    check("t_baseline_denominators_are_unique_trials", not probs, "; ".join(probs))


def t_no_live_copy_calls_seventy_reports_seventy_trials():
    """
    ABSENCE. The phrases that started this pass: "70 RCTs", "70 trials",
    "70 studies", "Study Explorer (k=70)". Each is a report count wearing a trial
    label. They are permitted only inside prose that explicitly marks itself as
    superseded, which strip_withdrawal_prose removes before this check runs.
    """
    UI_FILES = {
        "index.html": HTML,
        "app.js": APP,
        "translations.js": TRANS,
        "ui_translations.js": (DASH / "ui_translations.js").read_text(encoding="utf-8"),
        "prisma_checklist.js": (DASH / "prisma_checklist.js").read_text(encoding="utf-8"),
    }
    bad = re.compile(r"\b70\s+(?:RCTs?|randomi[sz]ed\s+controlled\s+trials?|trials?|studies|"
                     r"unique\s+(?:trials?|studies))\b|k\s*=\s*70", re.I)
    probs = []
    for name, text in UI_FILES.items():
        live = strip_withdrawal_prose(text) if name == "index.html" else text
        for m in bad.finditer(live):
            window = live[max(0, m.start() - 420): m.end() + 220]
            # Allowed only where the sentence itself is about the reports/studies
            # distinction, or is labelled as the superseded wording.
            if re.search(r"previously|superseded|no longer|describing 69|reports? describing|"
                         r"rather than the 70|70 <em>reports</em>|quoted where the unit is reports",
                         window, re.I):
                continue
            probs.append(f"{name}: {live[m.start():m.end()]!r} in {window[380:520]!r}")
    check("t_no_live_copy_calls_seventy_reports_seventy_trials", not probs,
          " || ".join(probs[:4]))


def t_reconciliation_status_is_not_self_contradictory():
    """
    ABSENCE. The PRISMA panel said the modality, comparator and patient totals
    "remain under reconciliation" in one paragraph and "(reconciled)" in the next,
    about the same three quantities. Whichever is true, both cannot be live.
    """
    live = strip_withdrawal_prose(HTML)
    probs = []
    for m in re.finditer(r"under reconciliation", live, re.I):
        # Look BACKWARD only, and not far: a withdrawal marker has to INTRODUCE
        # the phrase it withdraws. Scanning forward as well let a live claim pass
        # merely because a later sentence happened to contain "previously".
        lead = live[max(0, m.start() - 240): m.start()]
        if not re.search(r"previously|superseded|no longer|formerly|used to", lead, re.I):
            probs.append(f"a live 'under reconciliation' claim remains, introduced by "
                         f"{lead[-170:]!r}")
    if "reconciled 2026-09-12" not in HTML.lower():
        probs.append("the reconciled state carries no date, so a reader cannot tell which "
                     "statement is current")
    check("t_reconciliation_status_is_not_self_contradictory", not probs, "; ".join(probs[:2]))


def main() -> int:
    print("=" * 78)
    print(f"{BOLD}  DASHBOARD <-> v26 LOCK CONSISTENCY VALIDATOR{RESET}")
    print("  workbook: TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx")
    print("  analysis: 06_FINAL_ANALYSIS_V26 | PROSPERO: CRD420251090635")
    print("=" * 78)

    sections = [
        ("Provenance & identifiers", [t_prospero, t_no_v20_source_label, t_provenance_block,
                                     t_stata_edition_claim]),
        ("Pooled results vs Stata", [t_primary_matches_stata, t_displayed_k_and_n,
                                     t_hero_summary_cards_match_detail,
                                     t_primary_stratum_comparators_not_swapped, t_target_b_not_pooled]),
        ("Study-set composition", [t_target_a_membership, t_no_old_five_study_48h,
                                   t_target_b_membership, t_pain_at_rest_only,
                                   t_yu_wang_excluded, t_yeh_not_double_counted]),
        ("Estimand separation", [t_ponv_strata_separate, t_target_f_estimands_separate]),
        ("Risk of bias", [t_rob_pending_not_high, t_rob_result_specific]),
        ("Result-specific RoB 2 (adopted)", [t_rob2_results_cover_the_worklist,
                                             t_rob2_results_carry_honest_provenance,
                                             t_certainty_note_reflects_computed_grade,
                                             t_rob2_results_are_result_specific,
                                             t_rob2_overall_follows_algorithm,
                                             t_rob2_model_rollup_is_complete,
                                             t_rob2_source_qc_flags_preserved]),
        ("GRADE for the five new v34 models (rule-based, adopted)",
         [t_grade_new_models_complete_and_valid,
          t_grade_new_models_rule_recomputes,
          t_grade_new_models_do_not_overclaim_panel_review]),
        ("Withdrawn analyses", [t_no_withdrawn_metareg, t_small_study_effects]),
        ("GRADE", [t_grade_consistent]),
        ("Downloads & deployment", [t_downloads_resolve, t_downloads_are_current,
                                    t_forest_matches_table,
                                    t_population_denominators, t_paired_cohort_n,
                                    t_stratum_denominators]),
        ("Wording & i18n", [t_outcome_hierarchy, t_translations_do_not_contradict,
                            t_author_contacts_not_stale]),
        ("Primary contribution pathway", [t_pathway_counts_derive, t_pathway_categories_disjoint,
                                          t_pathway_n_matches_denominators, t_pathway_results_match_stata,
                                          t_pathway_no_fabricated_md_pool,
                                          t_pathway_contact_status_documented,
                                          t_pathway_wording, t_pathway_is_dynamic]),
        ("Final reconciliation pass", [t_ea_comparator_not_mislabelled_sham, t_combined_not_labelled_primary,
                                       t_moderator_matrix_no_fabricated_categories,
                                       t_no_false_no_association_claim, t_cochrane_wording_not_overstated,
                                       t_sufentanil_conversion_documented_and_unresolved,
                                       t_cdc_not_misattributed_to_perioperative_iv,
                                       t_mcid_labelled_exploratory, t_version_tag_present,
                                       t_i18n_textcontent_no_html_entities, t_v26_logs_git_tracked,
                                       t_primary_weighting_matrix_matches_stata,
                                       t_no_pre_correction_sufentanil_values,
                                       t_xie2014_yang2020_secondary_outcomes_corrected,
                                       t_locale_pooled_numbers_agree]),
        ("v33 evidence base", [t_v33_layer_matches_master,
                               t_v33_contribution_map_reconciles,
                               t_v33_map_panel_is_dynamic,
                               t_no_stale_master_in_live_code]),
        ("v33 tiered primary outcome", [t_v33_matches_stata, t_v33_strata_not_combined,
                                        t_v33_panel_is_dynamic,
                                        t_v33_zhang_withdrawn_everywhere,
                                        t_v33_legacy_reconstructions_labelled]),
        ("v34 lock integrity", [t_v34_csv_mirrors_locked_workbook,
                                t_post_lock_errata_still_applied,
                                t_prisma_identification_split_is_derived,
                                t_prisma_screening_arithmetic_reconciles,
                                t_prior_evidence_dispositions_match_the_analysis]),
        ("computed but not reported", [t_computed_not_reported_is_complete_and_unrated]),
        ("static/dynamic content sync", [t_static_kpi_fallback_matches_rendered_content,
                                        t_forest_context_matches_stata_log,
                                        t_target_af_sof_rows_match_v26_source,
                                        t_rob2_source_links_match_registers]),
        ("outcome register integrity (incident 2026-09-10)",
         [t_dashboard_outcomes_are_generated_from_the_lock,
          t_outcome_effects_recompute_from_their_arms,
          t_no_superseded_placeholder_outcomes,
          t_outcome_units_are_not_mixed,
          t_legacy_compilers_carry_no_placeholders,
          t_archival_workbooks_feed_no_live_code,
          t_pdf_extractions_are_provable_from_their_quotes,
          t_unlinked_rob2_cells_explain_themselves,
          t_country_is_verified_country_of_conduct,
          t_companion_publications_cannot_double_count,
          t_quarantine_registry_is_honest]),
        ("reports vs studies vs results — unit discipline (2026-09-12)",
         [t_cohort_overlap_scan_is_current,
          t_report_and_study_counts_follow_from_the_linkage,
          t_trial_level_tallies_exclude_companion_reports,
          t_participant_totals_count_each_trial_once,
          t_analysed_total_is_not_labelled_randomised,
          t_no_review_wide_randomised_total_is_published,
          t_possible_shared_cohorts_are_flagged_not_merged,
          t_baseline_conflicts_are_surfaced_not_corrected,
          t_yeh_identity_is_the_adopted_convention,
          t_baseline_denominators_are_unique_trials,
          t_no_live_copy_calls_seventy_reports_seventy_trials,
          t_reconciliation_status_is_not_self_contradictory]),
        ("interpretation layer (manuscript / reviewer overlay)",
         [t_interpretation_layer_cannot_carry_evidence,
          t_interpretation_bound_to_current_evidence,
          t_interpretation_questions_are_data_triggered,
          t_every_analysis_has_discussion_prompts,
          t_exploratory_analyses_carry_their_guardrails,
          t_limitations_are_evidenced_and_current,
          t_prisma_checklist_is_complete_and_honest]),
    ]

    for title, tests in sections:
        print(f"\n{BOLD}{title}{RESET}")
        for t in tests:
            try:
                t()
            except Exception as exc:  # a broken check is a failure, not a pass
                _failures.append(t.__name__)
                print(f"{RED}FAIL{RESET} | {t.__name__} raised {type(exc).__name__}: {exc}")

    total = _passes + len(_failures)
    print("\n" + "=" * 78)
    if _failures:
        print(f"{RED}{BOLD}FAILED{RESET}  {_passes}/{total} checks passed, "
              f"{len(_failures)} failed")
        for f in _failures:
            print(f"  {RED}x{RESET} {f}")
        print("=" * 78)
        return 1
    print(f"{GREEN}{BOLD}ALL CHECKS PASSED{RESET}  {_passes}/{total}")
    print("Dashboard is internally consistent with the v26 lock and the final Stata run.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
