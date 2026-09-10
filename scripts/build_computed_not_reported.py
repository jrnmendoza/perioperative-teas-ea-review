#!/usr/bin/env python3
"""
Generate dashboard/computed_not_reported.js — the analyses this review
computed but does not report as findings, and why.

WHY THIS PANEL EXISTS
The review fitted 45 analyses in the v26 results file. Twelve are presented as
Summary-of-Findings entries with an adopted GRADE certainty. The rest are
sensitivity permutations, duplicates under another id, or endpoints that were
computed and then not carried forward — and until now that last group appeared
NOWHERE on the dashboard.

That is the gap this closes. A reader who asks "you report composite PONV at
0-24 h, so what about nausea and vomiting separately?" could previously find no
answer, because the analyses exist only inside a results CSV. Silence reads as
"we didn't look", when the truth is "we looked, and here is why it is not a
reported finding". The review already applies this standard elsewhere -- the
v33 tiered panel states its empty cells explicitly rather than omitting them.

WHAT THIS IS NOT
These are not findings and are not presented as such. Every row carries the
reason it is not reported, and none carries a GRADE certainty, because none has
one. Attaching a certainty here would be exactly the selective outcome addition
the panel is meant to make visible rather than commit.

THE RULES, applied to every analysis_id in master_reconciled_results_v26.csv

  reported            the analysis is a Summary-of-Findings entry on the
                      dashboard (mapped in the interpretation layer's
                      LEGACY_ANALYSES) or is one of the three primary opioid
                      analyses shown under their v34 model ids.
  duplicate           the same fitted analysis under a second id.
  sensitivity         an estimator, CI-method, inclusion or subgroup variant of
                      a reported analysis; part of that analysis's story rather
                      than a separate endpoint.
  not-reported        everything else: a distinct endpoint that was computed and
                      not carried forward. These are the rows this panel shows.

For each not-reported row the panel states WHY, again by rule:

  single trial            k == 1; the review labels these "Not pooled".
  component of a
    reported composite    nausea/vomiting split out of a composite PONV
                          endpoint that IS reported and rated at the same window.
  inclusion variant       a broader/narrower inclusion set for an endpoint that
                          is already reported (kept here rather than hidden,
                          because the difference between the two sets is itself
                          a reviewer question).
  no adopted certainty    computed, but no GRADE rating was adopted, so the
                          review does not present it as a finding.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V26 = ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS" / "master_reconciled_results_v26.csv"
OUT = ROOT / "dashboard" / "computed_not_reported.js"

sys.path.insert(0, str(ROOT / "09_V34_ANALYSIS" / "05_INTERPRETATION"))
from build_interpretation_layer import LEGACY_ANALYSES  # noqa: E402

# The three primary opioid analyses are shown under their v34 model ids.
PRIMARY_EQUIVALENTS = {"OP24_TEAS_SHAM", "OP24_EA_CTRL", "OP24_PRIM_COMB",
                       "V33_S0_TEAS_SHAM", "V33_S0_EA_USUAL"}
DUPLICATES = {"OP24_STRICT_SMD",          # identical row to OP24_PRIM_SMD (reported)
              "SUB_MODALITY_TEAS",        # same fit as the TEAS primary
              "SUB_MODALITY_EA"}          # same fit as the EA primary

SENSITIVITY_MARKERS = ("SENS_", "_EXCL_", "EXCL_", "METAREG", "BROADER", "LOWROB",
                       "INCL_", "_DL_WALD", "_SMD_REML_KH")

# Why each not-reported endpoint is not a finding. Keyed by analysis_id so the
# reason is auditable per row rather than inferred from a category.
WHY_NOT_REPORTED = {
    "TD_NAUSEA_0_24H": ("component of a reported composite",
        "Composite PONV 0–24 h is reported and rated (Low certainty). Nausea is one "
        "component of that composite at the same window; the review reports the "
        "composite rather than grading its parts separately."),
    "TD_VOMIT_0_24H": ("component of a reported composite",
        "Composite PONV 0–24 h is reported and rated (Low certainty). Vomiting is the "
        "other component at the same window."),
    "TD_NAUSEA_0_48H": ("single trial",
        "One trial (Luo 2026). The review labels this 'Single study (Not pooled)'; a "
        "single trial is not presented as a pooled finding."),
    "TD_VOMIT_0_48H": ("single trial",
        "One trial (Luo 2026), 'Single study (Not pooled)'."),
    "TF_POSTOP_DELIVERED_MORPH": ("no adopted certainty",
        "Computed under Target F (exploratory). No GRADE certainty was adopted for it, "
        "so it is not presented as a finding."),
    "TF_PCA_DEMANDS_SMD": ("no adopted certainty",
        "PCA button presses/demands as a standardized effect — a proxy for opioid "
        "demand rather than a delivered dose. Computed under Target F (exploratory) "
        "with no adopted GRADE certainty."),
    "TF_RESCUE_OPIOID_ALL": ("inclusion variant",
        "The same endpoint as the reported rescue-opioid analysis (k = 4, RR 0.50, "
        "Moderate certainty) with Liu 2026 (burn) added. Shown because the difference "
        "between the strict and broader inclusion sets is itself a reasonable question."),
}


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def num(v, nd=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return round(f, nd) if nd is not None else f


def classify(aid: str) -> str:
    if aid in {m["csv_id"] for m in LEGACY_ANALYSES.values()} or aid in PRIMARY_EQUIVALENTS:
        return "reported"
    if aid in DUPLICATES:
        return "duplicate"
    if any(k in aid for k in SENSITIVITY_MARKERS):
        return "sensitivity"
    return "not-reported"


def main() -> int:
    rows = read(V26)
    buckets = {"reported": 0, "duplicate": 0, "sensitivity": 0}
    shown = []
    for r in rows:
        aid = r["analysis_id"]
        kind = classify(aid)
        if kind != "not-reported":
            buckets[kind] += 1
            continue
        if aid not in WHY_NOT_REPORTED:
            raise SystemExit(
                f"{aid} is not reported and has no stated reason. Add one to "
                "WHY_NOT_REPORTED -- an analysis must not appear in this panel "
                "without saying why it is not a finding.")
        why, detail = WHY_NOT_REPORTED[aid]
        est = num(r["estimate"], 4)
        is_ratio = "Risk Ratio" in r["effect_measure"] or r["effect_measure"].strip() == "RR"
        shown.append({
            "analysis_id": aid,
            "target": r["target"],
            "outcome": r["outcome"],
            "stratum": r["stratum"],
            "k": int(float(r["k"])) if r["k"] else None,
            "measure": r["effect_measure"],
            "estimate": est,
            "ci_low": num(r["ci_low"], 4),
            "ci_high": num(r["ci_high"], 4),
            "p_value": num(r["p_value"], 4),
            "i2": num(r["i2"], 2),
            "model": r["model"],
            "null_value": 1.0 if is_ratio else 0.0,
            "why": why,
            "detail": detail,
        })

    payload = {
        "generated_by": "scripts/build_computed_not_reported.py",
        "source": "06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv",
        "total_analyses": len(rows),
        "reported": buckets["reported"],
        "duplicate": buckets["duplicate"],
        "sensitivity": buckets["sensitivity"],
        "not_reported": len(shown),
        "note": (
            "Analyses this review computed but does not report as findings. They are "
            "shown so that a question like \"you report composite PONV — what about "
            "nausea and vomiting separately?\" has an answer other than silence. None "
            "carries a GRADE certainty rating, because none was adopted for it; adding "
            "one here would be exactly the unplanned outcome addition this panel exists "
            "to make visible rather than commit. Each row states why it is not reported."
        ),
        "rows": shown,
    }

    header = f"""// COMPUTED BUT NOT REPORTED — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_computed_not_reported.py
//
// Analyses the review fitted but does not present as findings, each with the
// reason it is not one. Not findings; no GRADE certainty is attached, because
// none was adopted.
//
// Source : {payload['source']}
// Of {payload['total_analyses']} analyses: {payload['reported']} reported, """ \
        f"""{payload['duplicate']} duplicates, {payload['sensitivity']} sensitivity variants,
// {payload['not_reported']} computed-but-not-reported (shown here).
window.COMPUTED_NOT_REPORTED = """

    OUT.write_text(header + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  of {len(rows)} analyses: {buckets['reported']} reported, "
          f"{buckets['duplicate']} duplicate, {buckets['sensitivity']} sensitivity, "
          f"{len(shown)} not reported")
    for s in shown:
        print(f"  {s['analysis_id']:<28} k={s['k']:<2} {s['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
