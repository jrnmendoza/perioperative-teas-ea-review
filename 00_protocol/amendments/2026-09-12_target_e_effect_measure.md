# Amendment — effect measure reported for Target E (time to first flatus)

**Date:** 2026-09-12
**Status:** adopted
**Raised by:** review lead, on the data-integrity pass that followed the post-lock admissions
**Scope:** which of two already-computed estimates is reported as this outcome's
headline measure. **Post hoc.** No eligibility criterion, outcome definition,
model, estimator or computed value is changed by this amendment.

## What changed

For Target E (time to first postoperative flatus) the review now reports the
**standardised mean difference** as the headline measure:

- **Reported:** Hedges' g = -0.55 [95% CI -0.88 to -0.22],
  p = 0.0065, I² = 39.2%
- **Also reported, no longer as the headline:** MD = -6.79 hours
  [-14.84 to 1.27], p = 0.0848,
  **I² = 97.3%**

The protocol prespecified the mean difference in hours. Both estimates were
computed by the same locked Stata run; neither was recomputed for this
amendment, and the mean difference remains visible everywhere the outcome is
reported.

## Why

Admitting Zhang 2018 on 2026-09-12 took this stratum from k = 6 to k = 7 and
raised I² from 0.0% to 97.3%. At that heterogeneity a pooled
mean difference in hours is not interpretable as a single effect.

The reason for preferring the standardised scale is a property of the data, not
of the new p value:

- Time to flatus varies about five-fold across these surgical contexts
  (control-arm means 15.9 h to 80.1 h).
- The absolute treatment effect scales with it: the correlation between a trial's
  control-arm mean and its absolute mean difference is **r = 0.91** across all
  seven trials.
- Expressed as a percentage of control, the effect is about twice as consistent
  as the effect in hours (coefficient of variation 0.56 versus 1.22).

A mean difference in hours is therefore the wrong scale on which to pool this
outcome, and that was true before Zhang 2018 was admitted — the k = 6 set simply
did not span a wide enough range of surgical contexts for it to show.

## What this amendment does NOT claim

The scale effect does **not** explain Zhang 2018 away. It remains an outlier on
the relative scale too (-0.55 overall, but Zhang 2018 at −35.9%
against −9.4% to −18.6% for the other six), which is why the standardised model's
I² is 39.2% rather than near zero: **reduced heterogeneity,
not resolved.** Zhang 2018 is the only open-surgery trial in a set that is
otherwise laparoscopic or thoracoscopic.

Nor does the change rescue a conclusion. Both prespecified sensitivity analyses
lost statistical significance in the same re-run:

| Sensitivity analysis | Before (k = 5) | Now |
|---|---|---|
| Excluding Ng 2013 (reported in days) | p = 0.0115, significant | k = 6, MD -6.94 h [-17.03, 3.14], **p = 0.1369**, I² = 98.2% |
| Excluding High risk-of-bias trials | p = 0.0199, significant | k = 6, MD -7.96 h [-17.79, 1.88], **p = 0.0921**, I² = 95.2% |

The hours-scale result is not robust to either exclusion, and both exclusions sit
above I² = 95%.

## Effect on the rating

None. Target E was already **GRADE Very Low** and is at the floor, so no
downgrade or upgrade follows from this amendment. The GRADE rationale was
extended on the same date to record the two sensitivity results, because they are
the evidence the existing rating rests on.

## How this is disclosed

- Every place the dashboard reports Target E states that the change is **post
  hoc** and dated, and shows the superseded k = 6 figures as history rather than
  deleting them.
- The mean difference is reported alongside the standardised measure, with its
  I² = 97.3% and the explicit statement that it should not be
  read as a single effect.
- A validator check (`t_no_stale_pre_admission_figures_presented_as_current`)
  fails the build if a superseded Target E figure is ever presented without being
  marked as past.

## This amendment is not prospective, and that is a deviation

`00_protocol/protocol_scope_locked.md` requires that "any later change must be
prospective, dated, justified, and recorded under `00_protocol/amendments/`".
This amendment is dated, justified and recorded, but it is **not prospective**:
the decision was made after the heterogeneity was seen. It therefore does not
meet the protocol's own standard for an amendment, and is recorded anyway rather
than made silently. A reader should treat the choice of reported measure for this
one outcome as a post hoc analytical decision and weigh it accordingly; the
prespecified mean difference remains published alongside it so that the
prespecified analysis can still be read directly.

## Reason this is an amendment and not a correction

Nothing was wrong. The prespecified measure was computed correctly and is still
published. What changed is the judgement about which scale this outcome can
honestly be pooled on, made after seeing the heterogeneity — which is the
definition of a post hoc decision and is recorded as one so that a reader can
discount it accordingly.

## Related

- `06_FINAL_ANALYSIS_V26/02_STATA/06_flatus.do` — the locked run producing both estimates
- `06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv` — `TE_FLATUS_MD_REML_KH`, `TE_FLATUS_SMD_REML_KH`
- `dashboard/eligibility_reconciliation.js` — Zhang 2018's admission record
- `00_protocol/amendments/2026-09-11_unit_of_analysis_companion_reports.md`
