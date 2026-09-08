#!/usr/bin/env python3
"""
Generate dashboard/primary_pathway.js — the PRIMARY OUTCOME CONTRIBUTION PATHWAY.

Answers, from the authoritative v26 sources only: why do 63 included RCTs become
6 studies in the strict 24-h opioid meta-analysis?

EVERY count and category is derived. Nothing about the pathway is hardcoded here
except the classification RULE itself, which is stated explicitly below and
documented in 06_AUDIT/dashboard_v26_reconciliation.md.

Sources
-------
  06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv      24-h candidate rows + flags
  06_FINAL_ANALYSIS_V26/01_DATA/target_{A..F}*.csv          other-outcome contributions
  06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv   pooled results
  06_FINAL_ANALYSIS_V26/01_DATA/authoritative_sheets/AF_P1_Disposition.csv
  06_FINAL_ANALYSIS_V26/01_DATA/authoritative_sheets/AF_Unresolved.csv
  dashboard/author_inquiries.json                           prepared author letters
  dashboard/data.js                                         canonical study list (63)

Classification rule (applied to the 24-h candidate rows)
--------------------------------------------------------
  strict       inc_primary == 1
                 directly reported, or defensibly harmonisable to a common dose
                 metric, cumulative systemic opioid at ~/exactly 24 h
  conditional  inc_sens == 1 and inc_primary == 0
                 relevant 24-h information that enters only under a broader
                 assumption (proxy timing, weight-normalised dose, derived
                 rescue-dose reconstruction)
  candidate    neither of the above, i.e. the row is held or excluded from the
                 continuous-dose model but the trial does carry potentially
                 relevant 24-h opioid information; author clarification could
                 make it strictly usable

Contact status is NEVER inferred. The project records no sent/response field
anywhere, so a candidate with a prepared draft letter is reported as
CONTACT PREPARED and one without any inquiry record as STATUS NOT DOCUMENTED.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA"
SHEETS = DATA / "authoritative_sheets"
RESULTS = ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS"
DASH = ROOT / "dashboard"
OUT = DASH / "primary_pathway.js"


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def num(v, nd=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return round(f, nd) if nd is not None else f


# ── canonical 63-study list ──────────────────────────────────────────────────
def studies_data() -> list[dict]:
    src = (DASH / "data.js").read_text(encoding="utf-8")
    start = src.index("window.STUDIES_DATA = [") + len("window.STUDIES_DATA = ")
    depth = 0; i = start; in_str = False; esc = False
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
        elif ch == '"': in_str = True
        elif ch == "[": depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(src[start:i + 1])
        i += 1
    raise RuntimeError("could not parse window.STUDIES_DATA")


STUDIES = studies_data()
CAND = read_csv(DATA / "opioid_24h_primary.csv")
MASTER = {r["analysis_id"]: r for r in read_csv(RESULTS / "master_reconciled_results_v26.csv")}

# ── other-outcome contributions, so nothing is called "excluded" ─────────────
OTHER_TARGETS = {
    "Target A — 0–48 h opioid": "target_A_48h.csv",
    "Target B — 0–72 h opioid": "target_B_72h.csv",
    "Target C — pain at rest ~24 h": "target_C_pain24h.csv",
    "Target D — PONV": "target_D_ponv.csv",
    "Target E — time to first flatus": "target_E_flatus.csv",
    "Target F — exploratory opioid outcomes": "target_F_exploratory.csv",
}

contributes: dict[str, set] = {}
for label, fname in OTHER_TARGETS.items():
    for r in read_csv(DATA / fname):
        if r.get("include_strict") == "1" or r.get("include_sensitivity") == "1":
            contributes.setdefault(r["study"].strip(), set()).add(label)

# ── author-contact records (prepared letters) ────────────────────────────────
inq_raw = json.loads((DASH / "author_inquiries.json").read_text(encoding="utf-8"))
inq_list = inq_raw if isinstance(inq_raw, list) else list(inq_raw.values())[0]
INQ_BY_COVID = {str(x.get("cov_id")): x for x in inq_list}

# ── documented unresolved / P1 dispositions ──────────────────────────────────
P1 = read_csv(SHEETS / "AF_P1_Disposition.csv")
UNRES = read_csv(SHEETS / "AF_Unresolved.csv")


def documented_issue(study_key: str):
    """Return the documented P1/unresolved record for a study, or None."""
    stem = study_key.split("(")[0].strip().split()[0]
    for r in P1:
        if stem and stem in r.get("Studyresult", ""):
            return {
                "issue_id": r.get("IssueID", ""),
                "issue": r.get("OriginalP1issue", ""),
                "disposition_class": r.get("Dispositionclass", ""),
                "quantitative_action": r.get("Quantitativeaction", ""),
                "author_need": r.get("Remainingsourceauthorneed", ""),
                "status": r.get("Dispositionstatus", ""),
                "blocker": r.get("Globalfinallockblocker", ""),
                "source_sheet": "AF_P1_Disposition",
            }
    for r in UNRES:
        if stem and stem in r.get("Studyresult", ""):
            return {
                "issue_id": f"{r.get('Priority','')} / {r.get('Target','')}",
                "issue": r.get("Unresolvedissue", ""),
                "disposition_class": r.get("Dispositionclass", ""),
                "quantitative_action": r.get("Datasetactionnow", ""),
                "author_need": r.get("Resolutionneeded", ""),
                "status": r.get("Dispositionstatus", ""),
                "blocker": r.get("Globalfinallockblocker", ""),
                "source_sheet": "AF_Unresolved",
            }
    return None


def study_ids_for(unit: str) -> list[str]:
    """
    Map a Stata study_unit to the canonical study id(s) it represents.

    Usually 1:1. The exception is a publication-family unit: the v26 lock treats
    Yeh 2010 + Yeh 2011 as ONE study unit pending overlap adjudication, so that
    single 24-h candidate row covers two of the 63 included reports. Resolved by
    author stem rather than by hardcoding the names, so a future family unit is
    handled the same way.
    """
    for s in STUDIES:
        if s["key"] == unit:
            return [s["id"]]
    stem = unit.split("(")[0].strip()
    exact = [s["id"] for s in STUDIES if s["key"].split("(")[0].strip() == stem]
    if exact:
        return exact
    author = unit.split()[0].strip()
    fam = [s["id"] for s in STUDIES if s["key"].split()[0].strip() == author]
    return fam


# ── classify the 24-h candidate rows ─────────────────────────────────────────
strict, conditional, candidates = [], [], []

for r in CAND:
    unit = r["study_unit"].strip()
    sids = study_ids_for(unit)
    sid = sids[0] if len(sids) == 1 else None
    n_i, n_c = int(r["n_i"]), int(r["n_c"])
    base = {
        "study_unit": unit,
        "study_id": sid,
        "study_ids": sids,
        "covers_publications": len(sids),
        "comparison_id": r["comparison_id"],
        "n_i": n_i, "n_c": n_c, "n_total": n_i + n_c,
        "data_type": r["data_type"],
        "unit": r["unit"],
        "time_window": r["time_window"],
        "outcome": r["outcome"],
        "result_rob": r["rob_overall"],
        "md_mme": num(r["md_mme"], 4),
        "se_mme": num(r["se_mme"], 4),
        "hedges_g": num(r["hedges_g"], 4),
        "hedges_se": num(r["hedges_se"], 4),
        "v26_decision": r["v20_primary_decision"],
        "source_qc": r["source_qc"],
        "conversion_note": r["conversion_needed"],
        "sensitivity_note": r["sensitivity_flag"],
        "source_url": r["source_url"],
        "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
        "also_contributes_to": sorted(contributes.get(unit, set())),
    }

    if r["inc_primary"] == "1":
        base["category"] = "strict"
        base["qualifies_because"] = r["v20_primary_decision"]
        strict.append(base)
    elif r["inc_sens"] == "1":
        base["category"] = "conditional"
        base["not_strict_because"] = r["v20_primary_decision"]
        base["estimable_md"] = base["md_mme"] is not None
        base["estimable_smd"] = base["hedges_g"] is not None
        conditional.append(base)
    else:
        base["category"] = "candidate"
        base["hard_hold"] = r["hard_hold"] == "1"
        doc = documented_issue(unit)
        base["documented_issue"] = doc
        inq = next((INQ_BY_COVID[str(x)] for x in sids if str(x) in INQ_BY_COVID), None)
        # Does the PREPARED letter actually ask for what blocks the 24-h result?
        # Keyword check, reported as such - never used to change a category.
        need_txt = (inq or {}).get("data_needed", "").lower()
        addresses = bool(re.search(
            r"opioid|morphine|fentanyl|sufentanil|concentration|consumption|mme|dose",
            need_txt))
        if inq:
            base["author_contact"] = {
                "status": "CONTACT PREPARED",
                "status_basis": "A drafted inquiry letter exists in author_inquiries.json. "
                                "The project records no sent/response field, so no further "
                                "status can be asserted.",
                "roster_label": inq.get("study_label", ""),
                "data_needed": inq.get("data_needed", ""),
                "impact": inq.get("impact", ""),
                "priority": inq.get("priority", ""),
                "addresses_primary_blocker": addresses,
                "gap_note": ("" if addresses else
                             "The prepared letter does not request the information that "
                             "blocks this trial's 24-h opioid result. Contacting the author "
                             "as drafted would not, on its own, make the trial strictly usable."),
            }
        else:
            base["author_contact"] = {
                "status": "STATUS NOT DOCUMENTED",
                "status_basis": "No inquiry record exists for this study in author_inquiries.json.",
                "data_needed": "", "impact": "", "priority": "",
            }
        candidates.append(base)

for lst in (strict, conditional, candidates):
    lst.sort(key=lambda x: x["study_unit"])

covered_ids = {i for grp in (strict, conditional, candidates) for r in grp for i in r["study_ids"]}

# ── the remaining included trials: what they DO contribute to ────────────────
other_contributors, no_pooled_model = [], []
for s in STUDIES:
    if s["id"] in covered_ids:
        continue
    tgts = sorted(contributes.get(s["key"], set()))
    row = {"study_unit": s["key"], "study_id": s["id"], "also_contributes_to": tgts}
    (other_contributors if tgts else no_pooled_model).append(row)

# ── pooled results, read from the Stata master table ─────────────────────────
def result(aid: str):
    r = MASTER.get(aid)
    if not r:
        return None
    return {
        "analysis_id": aid,
        "k": int(float(r["k"])) if r["k"] else None,
        "effect_measure": r["effect_measure"],
        "estimate": num(r["estimate"], 4),
        "ci_low": num(r["ci_low"], 4),
        "ci_high": num(r["ci_high"], 4),
        "p_value": num(r["p_value"], 5),
        "tau2": num(r["tau2"], 4),
        "i2": num(r["i2"], 2),
        "model": r["model"],
        "stratum": r["stratum"],
    }


strict_n = sum(r["n_total"] for r in strict)
cond_n = sum(r["n_total"] for r in conditional)
# v33: Zhang 2025 reports postoperative day 1, not an explicit 0-24 h clock
# window. Treating POD1 as 0-24 h is a prohibited assumption (Tier E), and the
# SMD changes the metric, not the estimand -- so a scale-free analysis does not
# rescue it. It is excluded from the broader SMD set here, matching
# 06_FINAL_ANALYSIS_V26/02_STATA/10_broader24h_sensitivity.do.
TIER_E_WINDOW_MISMATCH = {"Zhang 2025"}

broad_smd_units = [
    r for r in strict + conditional
    if r["hedges_g"] is not None and r["study_unit"] not in TIER_E_WINDOW_MISMATCH
]
unpoolable = [r for r in strict + conditional if r["hedges_g"] is None]

# ── reconciliation: every included RCT lands in exactly one bucket ──────────
_total = len(covered_ids) + len(other_contributors) + len(no_pooled_model)
if _total != len(STUDIES):
    raise SystemExit(
        f"PATHWAY DOES NOT RECONCILE: {len(covered_ids)} with 24-h info + "
        f"{len(other_contributors)} other-outcome + {len(no_pooled_model)} no-pooled-model "
        f"= {_total}, expected {len(STUDIES)} included RCTs"
    )
payload_reconciles = True

payload = {
    "generated_by": "scripts/build_primary_pathway.py",
    "data_source": "TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx",
    "statistical_source": "StataNow 19.5 BE — 06_FINAL_ANALYSIS_V26 + 07_TIERED_V33",
    "prospero": "CRD420251090635",

    "review_included_rcts": len(STUDIES),
    "candidate_rows": len(CAND),
    "publications_with_24h_info": len(covered_ids),

    "primary_strict": strict,
    "primary_conditional": conditional,
    "primary_author_contact_candidates": candidates,
    "other_outcome_contributors": other_contributors,
    "no_pooled_model": no_pooled_model,
    "reconciles": payload_reconciles,

    "counts": {
        "included_rcts": len(STUDIES),
        "reporting_relevant_24h_info": len(covered_ids),
        "candidate_rows": len(CAND),
        "strict": len(strict),
        "strict_n": strict_n,
        "conditional": len(conditional),
        "conditional_n": cond_n,
        "candidate_pool": len(strict) + len(conditional),
        "candidate_pool_n": strict_n + cond_n,
        "author_contact_candidates": len(candidates),
        "other_outcome_contributors": len(other_contributors),
        "no_pooled_model": len(no_pooled_model),
        "broader_smd_k": len(broad_smd_units),
        "broader_smd_n": sum(r["n_total"] for r in broad_smd_units),
    },

    "results": {
        "strict_md": result("OP24_PRIM_COMB"),
        "strict_smd": result("OP24_STRICT_SMD") or result("OP24_PRIM_SMD"),
        "broader_smd": result("OP24_BROADER_SMD"),
    },

    "md_pool_estimability": {
        "candidate_pool_k": len(strict) + len(conditional),
        "candidate_pool_n": strict_n + cond_n,
        "with_estimable_md": len([r for r in strict + conditional if r["md_mme"] is not None]),
        "with_estimable_smd": len(broad_smd_units),
        "unpoolable_units": [r["study_unit"] for r in unpoolable],
        "verdict": (
            "A pooled mean difference across the full candidate pool is NOT estimable. "
            "Sim 2002 and Coura 2011 report weight-normalised doses and the v26 lock "
            "prohibits reconstructing absolute dose from group-mean body weight; the two "
            "Chen 2015 reports are Median/IQR with no derived mean/SD. The broader "
            "sensitivity analysis therefore uses the scale-free standardized mean "
            "difference, which legitimately pools weight-normalised with absolute-dose "
            "endpoints."
        ),
    },

    "estimand": {
        "statement": (
            "Between-group difference in cumulative systemic postoperative opioid "
            "consumption during the first 24 postoperative hours, harmonised to a common "
            "opioid-dose metric where a prespecified and source-supported conversion is "
            "possible."
        ),
        "not_equivalent": [
            ["POD1", "is not necessarily an exact 0–24 h clock window"],
            ["mg/kg or µg/kg", "is not absolute mg without a defensible individual-level conversion"],
            ["rescue-administration count", "is not cumulative dose unless the reconstruction is fully justified"],
            ["PCA button presses", "are analgesic-seeking behaviour, not opioid dose"],
            ["mixed analgesic rescue", "is not opioid consumption"],
            ["a graph-derived value", "is not an exact source-reported number"],
        ],
    },
}

header = f"""// PRIMARY OUTCOME CONTRIBUTION PATHWAY — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_primary_pathway.py
//
// Every count is derived from the v26 lock and the final Stata run; none is
// hardcoded. If an author supplies usable data and the locked dataset is
// updated, re-running this script moves the study between categories and the
// dashboard counts follow automatically.
//
// Source workbook : {payload['data_source']}
// Statistics      : {payload['statistical_source']}
// PROSPERO        : {payload['prospero']}
"""

OUT.write_text(header + "window.PRIMARY_PATHWAY = " +
               json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
               encoding="utf-8")

c = payload["counts"]
print(f"wrote {OUT.relative_to(ROOT)}")
print(f"  included RCTs .............. {c['included_rcts']}")
print(f"  report relevant 24-h info .. {c['reporting_relevant_24h_info']}")
print(f"    strict ................... {c['strict']}  (N={c['strict_n']})")
print(f"    conditional .............. {c['conditional']}  (N={c['conditional_n']})")
print(f"    author-contact candidates  {c['author_contact_candidates']}")
print(f"  candidate pool ............. k={c['candidate_pool']}  N={c['candidate_pool_n']}")
print(f"  broader SMD estimable ...... k={c['broader_smd_k']}  N={c['broader_smd_n']}")
print(f"  other-outcome contributors . {c['other_outcome_contributors']}")
print(f"  no pooled model ............ {c['no_pooled_model']}")
