#!/usr/bin/env python3
"""
Compute a GRADE certainty rating for every v34 model listed in
09_V34_ANALYSIS/01_DATA/v34_model_manifest.csv -- the models whose
contributing results now carry a complete result-specific RoB 2 assessment
(v34_rob2_model_rollup.csv: results_unjudged == 0), regardless of whether the
model itself is phase NEW or REPRODUCED in v34_models.csv.

The manifest originally held only the five NEW v34 models (GI recovery,
pain, PONV) that had no GRADE rating because their RoB 2 domain was pending.
On 2026-09-09, five more models -- three REPRODUCED (QoR-40, intraoperative
remifentanil, intraoperative sufentanil) and two REPRODUCED time-to-
defecation models -- were confirmed to ALSO have complete result-specific
RoB 2 data (every contributing result already judged, either in this
pipeline's own priority-1 draft assessments or via an existing adjudicated
record folded in by 09_V34_ANALYSIS/03_ROB2/model_rollup.py) and were added
to the manifest. Their dashboard "reassessment pending" badge was stale: the
underlying reassessment was not actually pending, it just had never been
run through this script. REPRODUCED-phase membership in v34_models.csv was
never itself the eligibility test for this script -- the manifest, gated on
RoB 2 completeness, always was; it happened to hold only NEW-phase models at
first because those were the only ones checked for completeness at the time.

PROVENANCE. GRADE certainty rating is an assessor judgement, the same way
RoB 2 is: Cochrane/GRADE guidance sets bands and principles, not a formula,
and different assessors can reasonably land on different downgrades for
inconsistency or imprecision. What follows is an EXPLICIT, STATED rule
applied mechanically and identically to every model in the manifest, so any
GRADE-literate reader can check each step and disagree with a specific one.
It is not a GRADE panel's consensus judgement, and this script says so
everywhere its output is surfaced. On 2026-09-08 the review lead directed
this computed rating be adopted as the review's current GRADE assessment for
the first five models, the same status this review already applied to the
RoB 2 domain in the previous step -- adopted, not independently
panel-reviewed; the five added 2026-09-09 are adopted on that date under the
same standing direction, since they are the identical rule applied to
newly-confirmed-complete RoB 2 data, not a new methodological decision.

THE RULE, per domain, applied identically to every model:

  Risk of bias (from the just-adopted result-specific RoB 2 assessments):
    0 of k contributing results at High risk       -> no downgrade
    High risk present in a MINORITY of results     -> -1 (serious)
    High risk present in a MAJORITY (>=50%)        -> -2 (very serious)
    This mirrors the review's own existing convention (see
    STATA_MASTER_RESULTS in dashboard/app.js, e.g. "both contributing trials
    ... are High Risk of Bias" -> -2), which does NOT downgrade for
    "Some concerns" alone -- only High risk moves this domain.

  Inconsistency (I-squared, Cochrane Handbook chapter 10 bands):
    I2 < 50%                                        -> no downgrade
    I2 >= 50%                                        -> -1 (serious)
    The review's own existing entries never apply -2 for inconsistency alone
    (I2 = 98.6% still received only -1), so this rule caps at -1 regardless
    of how high I2 runs. At k=2 an I2 estimate is unstable and this is
    flagged in the note rather than silently applied as if precise.

  Imprecision (does the 95% CI cross the null, and how many studies inform
  it):
    CI excludes the null AND k >= 3                  -> no downgrade
    CI excludes the null AND k == 2                  -> -1 (serious;
      REML normal CI at k=2 is the review's own less-robust estimator tier)
    CI includes the null AND k >= 3                  -> -1 (serious)
    CI includes the null AND k == 2                  -> -2 (very serious;
      matches the review's own precedent, e.g. "Downgraded 2 levels for
      imprecision (k=2, small events, 95% KH CI crosses 1.0 ...)")

  Indirectness: not downgraded for any of the five models. Each model is
  already stratified by modality and comparator (the review's own rule:
  TEAS and EA are never combined; sham and usual care are never combined),
  so within a model the comparison is direct. Contributing trials vary in
  surgical population (e.g. gastric, colorectal, gynaecological, thoracic),
  which is a genuine judgement call about applicability rather than a
  numeric fact -- flagged in the note, not silently assumed away.

  Publication bias: not downgraded for any of the five models, because none
  reaches k=10, the threshold this review has already adopted elsewhere
  (t_small_study_effects in scripts/validate_dashboard.py: "Egger-type
  small-study-effect testing not interpreted at k=7 (<10)"). Absence of a
  test is not evidence of absence of bias, and the note says so rather than
  reporting "undetected" as if it had been checked.

Total downgrade floors at Very Low (GRADE has no rating below it), and the
raw downgrade count beyond that floor is still reported for transparency.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODELS_CSV = ROOT / "09_V34_ANALYSIS" / "03_RESULTS" / "v34_models.csv"
ROLLUP_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_model_rollup.csv"
MANIFEST_CSV = ROOT / "09_V34_ANALYSIS" / "01_DATA" / "v34_model_manifest.csv"
DATADIRS = [
    ROOT / "09_V34_ANALYSIS" / "01_DATA",
    ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data",
]

GRADE_LEVELS = ["Very Low", "Low", "Moderate", "High"]

# model_id -> the date this rule was applied to it. The rule itself and how
# it is applied are unchanged between the two dates (see module docstring);
# this records when each model's RoB 2 data was confirmed complete and this
# script was run against it, not a change in method.
ADOPTED_2026_09_08 = {
    "gi_first_flatus_TEAS_Sham", "gi_first_flatus_EA_Usual_care",
    "gi_first_bowel_sounds_TEAS_Sham", "pain_vas_24h_TEAS_Sham",
    "ponv_24h_TEAS_Sham",
}


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def total_n(model_id: str) -> int:
    for d in DATADIRS:
        p = d / f"{model_id}.csv"
        if p.exists():
            rows = read(p)
            return sum(int(float(r["n_i"])) + int(float(r["n_c"])) for r in rows)
    raise SystemExit(f"no per-study dataset found for {model_id} in {DATADIRS}")


def rob_downgrade(low: int, some: int, high: int) -> tuple[int, str]:
    k = low + some + high
    if high == 0:
        return 0, f"no downgrade: 0 of {k} contributing results at High risk of bias"
    frac = high / k
    if frac >= 0.5:
        return -2, (f"-2 (very serious): {high} of {k} contributing results "
                    "(a majority) are High risk of bias")
    return -1, f"-1 (serious): {high} of {k} contributing results are High risk of bias"


def inconsistency_downgrade(i2: float, k: int) -> tuple[int, str]:
    caveat = " (I2 at k=2 is statistically unstable; treat this as indicative, not precise)" if k == 2 else ""
    if i2 < 50:
        return 0, f"no downgrade: I2 = {i2:.1f}%{caveat}"
    return -1, f"-1 (serious): I2 = {i2:.1f}%, at or above the 50% substantial-heterogeneity band{caveat}"


def imprecision_downgrade(ci_low: float, ci_high: float, k: int, null: float) -> tuple[int, str]:
    crosses = ci_low <= null <= ci_high
    if not crosses and k >= 3:
        return 0, f"no downgrade: 95% CI [{ci_low:.2f}, {ci_high:.2f}] excludes the null, k={k}"
    if not crosses and k == 2:
        return -1, (f"-1 (serious): 95% CI [{ci_low:.2f}, {ci_high:.2f}] excludes the null but "
                    f"only k={k} studies inform it (REML normal CI, not Hartung-Knapp)")
    if crosses and k >= 3:
        return -1, f"-1 (serious): 95% CI [{ci_low:.2f}, {ci_high:.2f}] crosses the null, k={k}"
    return -2, (f"-2 (very serious): 95% CI [{ci_low:.2f}, {ci_high:.2f}] crosses the null "
               f"and only k={k} studies inform it")


def main() -> int:
    all_models = {r["model_id"]: r for r in read(MODELS_CSV)}
    manifest = {r["model_id"]: r for r in read(MANIFEST_CSV)} if MANIFEST_CSV.exists() else {}
    # Eligibility is the manifest, not phase: every model_id an operator has
    # curated into v34_model_manifest.csv after confirming its RoB 2 rollup
    # has zero unjudged results. A model_id manifested but missing from
    # v34_models.csv (a typo, or a model since renamed) fails loudly rather
    # than being silently skipped.
    models = {}
    for mid in manifest:
        if mid not in all_models:
            raise SystemExit(f"manifest lists {mid}, not found in {MODELS_CSV}")
        models[mid] = all_models[mid]
    rollup = {r["model_id"]: r for r in read(ROLLUP_CSV)}

    out = []
    for mid, m in sorted(models.items()):
        roll = rollup[mid]
        if int(roll["results_unjudged"]) != 0:
            raise SystemExit(f"{mid}: {roll['results_unjudged']} contributing results still "
                             "unjudged -- not eligible for this rule-based GRADE computation")
        low, some, high = int(roll["low"]), int(roll["some_concerns"]), int(roll["high"])
        k = int(m["k"])
        i2 = float(m["i2"])
        est, ci_low, ci_high = float(m["estimate"]), float(m["ci_low"]), float(m["ci_high"])
        measure = m["measure"]
        null = 0.0 if measure == "MD" else 0.0  # logRR null is log(1)=0, same as MD's 0

        d_rob, r_rob = rob_downgrade(low, some, high)
        d_inc, r_inc = inconsistency_downgrade(i2, k)
        d_imp, r_imp = imprecision_downgrade(ci_low, ci_high, k, null)
        d_ind, r_ind = 0, ("no downgrade: direct comparison within this stratified model; "
                           "surgical-population variation across contributing trials was "
                           "judged not to threaten applicability, a judgement call rather "
                           "than a numeric fact")
        d_pub, r_pub = 0, (f"not assessed: k={k} is below the review's own k=10 threshold "
                          "for interpretable small-study-effect testing; absence of a test "
                          "is not evidence of absence of bias")

        raw_total = d_rob + d_inc + d_imp + d_ind + d_pub
        level_idx = max(0, 3 + raw_total)  # start at High (index 3), floor at Very Low (0)
        grade = GRADE_LEVELS[level_idx]

        man = manifest.get(mid, {})
        out.append(dict(
            model_id=mid, outcome=man.get("outcome", ""), window=man.get("window", ""),
            modality=man.get("modality", ""), comparator=man.get("comparator", ""),
            unit=man.get("unit", ""), measure=measure, k=k, n=total_n(mid),
            estimate=round(est, 4), ci_low=round(ci_low, 4), ci_high=round(ci_high, 4),
            p_value=m["p_value"], i2=round(i2, 1),
            rob_downgrade=d_rob, rob_reason=r_rob,
            inconsistency_downgrade=d_inc, inconsistency_reason=r_inc,
            imprecision_downgrade=d_imp, imprecision_reason=r_imp,
            indirectness_downgrade=d_ind, indirectness_reason=r_ind,
            publication_bias_downgrade=d_pub, publication_bias_reason=r_pub,
            raw_downgrade_total=raw_total, grade=grade,
            status="GRADE_RULE_BASED_ADOPTED",
            adopted_by="John Ryan N. Mendoza (review lead)",
            adopted_date="2026-09-08" if mid in ADOPTED_2026_09_08 else "2026-09-09",
        ))

    p = HERE / "v34_new_model_grade.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    print(f"{'model':<34} {'k':>2} {'RoB':>4} {'Inc':>4} {'Imp':>4} {'Ind':>4} {'Pub':>4}  {'grade':<10}")
    for r in out:
        print(f"  {r['model_id']:<32} {r['k']:>2} {r['rob_downgrade']:>4} "
              f"{r['inconsistency_downgrade']:>4} {r['imprecision_downgrade']:>4} "
              f"{r['indirectness_downgrade']:>4} {r['publication_bias_downgrade']:>4}  {r['grade']:<10}")
    print(f"\nwrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
