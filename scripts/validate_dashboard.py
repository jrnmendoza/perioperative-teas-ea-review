#!/usr/bin/env python3
"""
Dashboard <-> v26 lock consistency validator.

Fails loudly when the published dashboard disagrees with the authoritative
sources:

  workbook   TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx
  analysis   06_FINAL_ANALYSIS_V26/{01_DATA,03_RESULTS}
  dashboard  dashboard/  (canonical)  ->  docs/  (generated mirror)

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
DOCS = ROOT / "docs"
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
    )
    out = []
    for para in re.split(r"(?=<(?:li|p|div|td|h2|h3|h4)\b)", text):
        if any(m in para for m in markers):
            continue
        out.append(para)
    return "".join(out)


LIVE_UI = strip_withdrawal_prose(ALL_UI)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Provenance and identifiers
# ─────────────────────────────────────────────────────────────────────────────

def t_prospero():
    obsolete = "CRD42024560773"
    correct = "CRD420251090635"
    hits = []
    for p in list(DASH.rglob("*")) + list(DOCS.rglob("*")):
        if p.is_file() and p.suffix in {".html", ".js", ".json", ".csv", ".md"}:
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
        "StataNow 19.5 SE",
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
    banned = {
        "k = 11 / k=11 primary pool": r"k\s*=\s*11|k=11",
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
        if (DASH / h).exists() or (ROOT / h).exists():
            continue
        probs.append(f"unresolvable download/asset: {h}")
    check(f"All {len(hrefs)} download and image targets resolve", not probs, "\n".join(probs))


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


def t_dashboard_docs_parity():
    a = {p.relative_to(DASH): p for p in DASH.rglob("*") if p.is_file()}
    b = {p.relative_to(DOCS): p for p in DOCS.rglob("*") if p.is_file()}
    only_a = sorted(str(x) for x in (set(a) - set(b)))
    only_b = sorted(str(x) for x in (set(b) - set(a)))
    diff = sorted(str(k) for k in (set(a) & set(b)) if a[k].read_bytes() != b[k].read_bytes())
    check("dashboard/ (source) and docs/ (generated mirror) are identical",
          not (only_a or only_b or diff),
          f"only in dashboard: {only_a}\nonly in docs: {only_b}\ndiffering: {diff}")


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

def main() -> int:
    print("=" * 78)
    print(f"{BOLD}  DASHBOARD <-> v26 LOCK CONSISTENCY VALIDATOR{RESET}")
    print("  workbook: TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx")
    print("  analysis: 06_FINAL_ANALYSIS_V26 | PROSPERO: CRD420251090635")
    print("=" * 78)

    sections = [
        ("Provenance & identifiers", [t_prospero, t_no_v20_source_label, t_provenance_block]),
        ("Pooled results vs Stata", [t_primary_matches_stata, t_displayed_k_and_n,
                                     t_target_b_not_pooled]),
        ("Study-set composition", [t_target_a_membership, t_no_old_five_study_48h,
                                   t_target_b_membership, t_pain_at_rest_only,
                                   t_yu_wang_excluded, t_yeh_not_double_counted]),
        ("Estimand separation", [t_ponv_strata_separate, t_target_f_estimands_separate]),
        ("Risk of bias", [t_rob_pending_not_high, t_rob_result_specific]),
        ("Withdrawn analyses", [t_no_withdrawn_metareg, t_small_study_effects]),
        ("GRADE", [t_grade_consistent]),
        ("Downloads & deployment", [t_downloads_resolve, t_downloads_are_current,
                                    t_forest_matches_table, t_dashboard_docs_parity]),
        ("Wording & i18n", [t_outcome_hierarchy, t_translations_do_not_contradict,
                            t_author_contacts_not_stale]),
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
