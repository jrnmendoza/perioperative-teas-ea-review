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
    guards = ("not ", "never", "forbid", "withdrawn", "hard hold", "excluding",
              "overlap", "superseded", "must not", "one study unit", "cohort-overlap")
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
    for bad in re.finditer(r"EA vs (?:Control/Sham|Sham/Control|Sham)", LIVE_UI):
        probs.append(f"live UI mislabels the EA stratum: {bad.group(0)!r}")
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


# ── draft result-specific RoB 2 ───────────────────────────────────────────
def _rob2_drafts():
    rows = read_csv(ROOT / "09_V34_ANALYSIS" / "03_ROB2" /
                    "v34_rob2_draft_assessments.csv")
    return rows


def t_rob2_drafts_cover_the_worklist():
    """
    Every priority-1 row -- the results inside a fitted model -- must have a
    draft, and every draft must correspond to a real priority-1 row.

    A partial set would leave some pooled estimates with an unstated
    risk-of-bias basis while the panel implies all of them are covered.
    """
    work = [r for r in read_csv(ROOT / "09_V34_ANALYSIS" / "v34_rob2_worklist.csv")
            if r["priority"].startswith("1")]
    want = {(r["study"], r["outcome"], r["timepoint"]) for r in work}
    got = {(r["study"], r["outcome"], r["timepoint"]) for r in _rob2_drafts()}
    probs = []
    for k in sorted(want - got):
        probs.append(f"no draft for {k[0]} / {k[1]} @ {k[2]}")
    for k in sorted(got - want):
        probs.append(f"draft for a row that is not priority-1: {k[0]} / {k[1]} @ {k[2]}")
    check("Draft RoB 2 judgements cover exactly the results inside a fitted model",
          not probs, "\n".join(probs))


def t_rob2_drafts_are_labelled_draft():
    """
    A draft must never be presented as an adjudicated judgement.

    Cochrane RoB 2 is the review's central quality appraisal and is reported
    under named assessors. If the dashboard showed these as settled, the review
    would be claiming an appraisal that no assessor has made.
    """
    probs = []
    for r in _rob2_drafts():
        if r["status"] != "ROB2_RESULT_SPECIFIC_DRAFT_PENDING_ADJUDICATION":
            probs.append(f"{r['study']} / {r['outcome']}: status is {r['status']!r}")
    v34 = (ROOT / "dashboard" / "v34_data.js").read_text(encoding="utf-8")
    if '"rob2_drafts"' in v34:
        if "ROB2_RESULT_SPECIFIC_DRAFT_PENDING_ADJUDICATION" not in v34:
            probs.append("v34_data.js carries drafts without the pending-adjudication status")
        if "two independent human assessors" not in v34:
            probs.append("v34_data.js drafts do not state that two assessors are required")
    app = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    if "v34RobDraftsHtml" in app and "DRAFT — not adjudicated" not in app:
        probs.append("the drafts panel does not carry a visible DRAFT label")
    check("Draft RoB 2 judgements are labelled as drafts, not as adjudicated judgements",
          not probs, "\n".join(probs))


def t_rob2_drafts_do_not_release_grade():
    """
    Drafting the outstanding assessments must not release the GRADE hold.

    The v34 handover is explicit that a materially changed synthesis does not
    inherit an earlier GRADE rating, and an unadjudicated draft is not a basis
    for issuing a new one.
    """
    v34 = (ROOT / "dashboard" / "v34_data.js").read_text(encoding="utf-8")
    probs = []
    if '"certainty_note"' in v34:
        note = v34.split('"certainty_note"', 1)[1][:800]
        if "pending" not in note.lower():
            probs.append("certainty_note no longer says the assessments are pending")
        if "draft" not in note.lower():
            probs.append("certainty_note does not distinguish a draft from an adjudicated judgement")
    check("Draft RoB 2 judgements do not release the GRADE hold",
          not probs, "\n".join(probs))


def t_rob2_drafts_are_result_specific():
    """
    A study contributing several results must be judged per result, not once.

    The specific failure this guards against is a study-wide judgement copied
    across that study's results: the v34 handover names it, and it would hide
    exactly the differences -- who measured this outcome, and were they blinded
    -- that make D4 result-specific.
    """
    rows = _rob2_drafts()
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
    check("Draft RoB 2 judgements are made per result, not copied study-wide",
          not probs, "\n".join(probs))


def t_rob2_draft_overall_follows_algorithm():
    """
    Overall risk must follow the RoB 2 algorithm, not be assigned by impression.
    """
    rank = {"Low": 0, "Some concerns": 1, "High": 2}
    probs = []
    for r in _rob2_drafts():
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
    check("Draft overall risk follows the RoB 2 algorithm from its own domains",
          not probs, "\n".join(probs))


def t_rob2_model_rollup_is_complete():
    """
    Every model must have a risk-of-bias basis for all of its contributing
    results -- drafted here or already adjudicated. A rollup that silently
    omits a contributor would understate what a pooled estimate inherits.
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
                                     t_target_b_not_pooled]),
        ("Study-set composition", [t_target_a_membership, t_no_old_five_study_48h,
                                   t_target_b_membership, t_pain_at_rest_only,
                                   t_yu_wang_excluded, t_yeh_not_double_counted]),
        ("Estimand separation", [t_ponv_strata_separate, t_target_f_estimands_separate]),
        ("Risk of bias", [t_rob_pending_not_high, t_rob_result_specific]),
        ("Draft result-specific RoB 2", [t_rob2_drafts_cover_the_worklist,
                                         t_rob2_drafts_are_labelled_draft,
                                         t_rob2_drafts_do_not_release_grade,
                                         t_rob2_drafts_are_result_specific,
                                         t_rob2_draft_overall_follows_algorithm,
                                         t_rob2_model_rollup_is_complete]),
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
                                       t_locale_pooled_numbers_agree]),
        ("v33 evidence base", [t_v33_layer_matches_master,
                               t_v33_contribution_map_reconciles,
                               t_v33_map_panel_is_dynamic,
                               t_no_stale_master_in_live_code]),
        ("v33 tiered primary outcome", [t_v33_matches_stata, t_v33_strata_not_combined,
                                        t_v33_panel_is_dynamic,
                                        t_v33_zhang_withdrawn_everywhere,
                                        t_v33_legacy_reconstructions_labelled]),
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
