# Discussion

> **Draft status.** Corrected 20 September 2026. The earlier draft described the
> primary result as "minor statistically significant reductions… observed",
> which reads as pooled evidence when both TEAS estimates are single-study
> contrasts from one trial; and stated that EA "did not meet" the joint
> criterion when in fact no eligible sham-controlled EA evidence existed to evaluate.
> Conclusions have been moved to `CONCLUSIONS.md`.

## Principal findings

Across 70 reports representing 69 trial families, **no evidence body established
the registered joint criterion** for clinically meaningful opioid sparing. The
principal comparison — TEAS versus credible sham for all delivered systemic
opioid over the first 24 postoperative hours — rests on **a single trial of 48
analysed participants** (Szmit 2021), which reported about 7.7 mg less
intravenous morphine equivalent. That is a single-study contrast with a
within-study confidence interval, not a pooled meta-analytic estimate, and it
does not reach the registered 10 mg threshold.

The criterion has two limbs, and neither is satisfied. The opioid limb falls
short of 10 mg. The pain limb cannot be evaluated at all for the trial that
supplies the opioid estimate, because its pain assessment is adjudicated as
discharge pain rather than a fixed ~24-hour measurement, and pain evidence drawn
from other trials cannot supply the missing pairing.

For **electroacupuncture versus sham, no eligible evidence exists** for this
outcome. This is an empty cell, not a negative result: the comparison could not
be evaluated rather than having been evaluated and failed. The distinction
matters for anyone designing the next trial.

## Why so little evidence survives

Seventy reports yielded one eligible principal contrast, and the reason is
definitional rather than a failure of retrieval. Many trials report an opioid
quantity that resembles the registered outcome without being it: a different
time window, a weight-normalised dose, a pump volume without a verified
concentration, a count of analgesia demands, a patient-controlled analgesia
total that omits separately administered rescue, or an author-defined
"morphine equivalent" of unstated basis. Admitting these requires assumptions of
varying defensibility, and any pooled estimate inherits the weakest of them.
Classifying them explicitly, and reporting what each classification costs, is
this review's principal methodological contribution — and it is why our estimate
is sparser, not weaker, than its predecessors.

Broader definitions do not rescue the result. Under a post-hoc broadened
definition that admits incomplete capture, applied uniformly to every included
report, the TEAS-versus-sham body grows from one trial to seven, but its estimate
shrinks to −6.17 mg (−12.47 to 0.14), with I² 98%. Every broadened variant of that
analysis crosses the null and none reaches 10 mg. Admitting weaker constructs buys
heterogeneity, not signal.

## The most robust finding is an absence of difference

The only moderate-certainty body in the review concerns rest pain at
approximately 24 hours, where TEAS and sham differed by −0.213 points on a 0–10
scale (k=3, N=218), with the entire confidence interval inside the registered
±1-point margin. This licenses a statement about average 24-hour rest pain and
nothing more: it is not paired opioid/pain evidence, and it is not a formal
non-inferiority result. It is, nonetheless, the most reliable thing this review
can say.

## Other outcomes

Composite postoperative nausea and vomiting favours TEAS at low certainty
(k=10, RR 0.640), but its separated nausea and vomiting components at 24 hours
both cross the null, and the composite is an additional rather than a primary
outcome. Gastrointestinal recovery estimates are mostly of very low certainty
and are sensitive to the removal of one trial with irreconcilable printed
statistics — a removal that changed bowel sounds from a significant benefit to a
null. Quality-of-recovery syntheses are uniformly of very low certainty and
establish neither benefit nor its absence. Intraoperative remifentanil shows the
most internally consistent pooled result in the review, which should be read in
light of the two disclosed exclusions that produced that consistency.

## Comparison with previous reviews

Earlier syntheses that examined opioid or analgesic consumption reported
reductions [@wu2016review; @tahmasbi2025]. One of them found the reduction in
opioid use on the first postoperative day confined to TEAS, with no benefit for
conventional acupuncture or electroacupuncture [@wu2016review], which supports
treating the two modalities as separate questions. Our more restrictive
conclusion reflects different rules: separating TEAS from EA, separating sham
from usual care, and declining to pool opioid quantities that measure different
things. Within our own data, relaxing only the last of these rules enlarged the
TEAS-versus-sham body from one trial to seven without producing an estimate that
excluded no effect. We did not formally compare our trial set with those of
earlier reviews, so a contribution from differing evidence bases cannot be
excluded. Where a prior review reports a pooled benefit across modalities or
comparators [@wu2016review; @lu2023review], it is answering a question the
registered protocol here treats as unanswerable.

## Strengths

Modality and comparator were treated as part of the estimand rather than as
study characteristics, and were never pooled. Candidate results were classified
against the registered construct before synthesis rather than after. Risk of
bias was assessed at the level of the individual result, with complete coverage
of every non-sensitivity body. Analyses regenerate deterministically and were
independently recomputed in R with metafor from arm-level statistics; all source
reports are hash-pinned. Empty cells, source contradictions and holds are
reported rather than omitted.

## Limitations

**Completeness of the evidence base.** A screening amendment narrowed full-text
eligibility to the two primary outcomes six days before the registered record
admitted any eligible outcome; 113 records were excluded on that basis. The
reviewer re-screening package was withdrawn and no dual independent re-screen
was undertaken, so review-wide completeness remains uncertain. A 12-reference
import gap could not be mapped to individual records, and upstream deduplication
reconciles arithmetically but cannot be replayed record by record.

**How decisions were made.** Result-specific risk-of-bias assessment, GRADE
judgements, estimand classification and the methodological adjudications were
**AI-conducted under the review team's delegation**; prior human review is
reported by the team. They do not constitute two independent human assessments.
**Every adjudication decision was made after the results of the contributing
trials were known** and none should be read as prospective. Registration
followed the recorded review start date, so this review is not described as
prospectively registered.

**Sparse and uncertain bodies.** The principal and supportive opioid bodies are
k=1 and k=2. Wide intervals at k=2 are expected and were not narrowed by
substituting a more favourable method.

**Unresolved source material.** Eight source contradictions remain open,
including printed statistics that cannot generate their own reported P values.
Author queries were drafted for each; eleven were sent on 22 September 2026 and
four remain unsent. **No reply had been received at the time of writing, and no analysis
assumes a response.** Eight further reports with located quality-of-recovery data were held
from synthesis rather than converted onto assumed distributions.

**Incomplete coverage.** Length of stay, PACU stay and mobilisation were located
in source reports but have not been assembled into structured tables or
synthesised. GRADE judgements for the four later-window quality-of-recovery
bodies have not been made. No eligible result for persistent opioid use beyond
30 days was located, so this review cannot address it. Harms and satisfaction
are reported descriptively only; no pooled safety estimate was computed, and
absence of a pooled estimate is not evidence of safety.

**Language and geography.** Eligibility was restricted to English full texts,
and twelve records were excluded on language. Most included reports are from
China. Both bear on generalisability and on the risk that relevant evidence lies
outside the review.

## Implications for research

The registered question — whether protocol characteristics such as timing,
repetition, cumulative stimulation, frequency and intensity explain variation in
effect — **could not be answered**, because no moderator met the registered
minimum of ten independent estimates per predictor and four per level. That is
itself the most actionable finding. Trials should report all delivered systemic
opioid including rescue, in absolute units with a stated conversion basis, at a
fixed 24-hour clock window; report pain at the same fixed window in both rest
and movement settings; and characterise stimulation parameters to STRICTA
standards [@macpherson2010]. No sham-controlled electroacupuncture trial captures all delivered
systemic opioid over the first 24 hours in absolute units: those reporting a
24-hour total give it per kilogram, as a pump volume, or without a first-hour
rescue. Such trials are the clearest gap.
