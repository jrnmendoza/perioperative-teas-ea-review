# Manuscript text — v33 tiered primary-outcome analysis

Perioperative TEAS & EA systematic review and meta-analysis · PROSPERO CRD420251090635
Generated 2026-09-08. Every number below is read from
`07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33.csv` and
`06_FINAL_ANALYSIS_V26/03_RESULTS/`, both written by StataNow 19.5.

---

## Methods

### Primary outcome and estimand

The primary outcome was cumulative postoperative opioid consumption over the
0–24 hour period following the end of surgery, expressed in milligrams of
intravenous morphine milligram equivalents (IV MME). Conversion to IV MME used
published equianalgesic factors only; each factor and its source is recorded in
`06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv`. Where no sourced
factor could be located for a reported opioid, the trial was not converted and
contributed no IV MME value rather than being converted on an assumed ratio.

### Tiered derivability classification

Trials frequently report an opioid quantity that resembles the primary outcome
but is not, in fact, the same estimand — a different time window, a
weight-normalised dose, a count of patient-controlled analgesia demands, or a
median rather than a mean. Pooling these together requires assumptions of
varying defensibility, and the resulting estimate inherits whichever assumption
is weakest. We therefore classified every candidate outcome row against the
primary estimand before any synthesis, in a pre-specified audit of 93 candidate
rows (`PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.xlsx`):

- **Tier A — directly compatible.** Exact 0–24 hour cumulative opioid
  consumption, reported as mean and standard deviation, in an absolute dose unit
  with a sourced IV MME conversion factor.
- **Tier B — deterministically derived.** Recoverable by an exact arithmetic
  identity from reported quantities, with no distributional assumption.
- **Tier C — alternative distributional form.** Exactly the right estimand, but
  reported as a median with interquartile range.
- **Tier D — recoverable only by graph digitization.**
- **Tier E — requires a prohibited assumption.** Would need an assumed body
  weight, PCA demands treated as delivered doses, postoperative day 1 treated as
  a 0–24 hour clock window, or an invented between-outcome covariance.

Four nested analysis sets were pre-specified: **S0** (Tier A only), **S1**
(S0 plus Tier B), **S2** (Tier C, reported as a parallel synthesis), and **S3**
(S0 plus Tier D).

### Synthesis

Analyses were stratified by modality (TEAS, EA) and by comparator (inert sham,
usual care / no stimulation). TEAS and EA were never combined to increase power,
and sham- and usual-care-controlled evidence was never pooled without
stratification. Multi-arm trials contributed exactly one contrast to any single
model; where an alternative contrast from the same trial existed it was used
only by substitution in a sensitivity analysis, never added alongside its
sibling.

Random-effects models were fitted by restricted maximum likelihood (REML) with
Hartung–Knapp adjusted confidence intervals on a *t* reference distribution, and
95% prediction intervals. Heterogeneity is reported as τ², I², and Cochran's Q.
All inferential results were produced in **StataNow 19.5** using `meta set` and
`meta summarize, random(reml) se(kh) predinterval`; the do-file is
`07_TIERED_V33/02_STATA/13_tiered_primary_v33.do` and the full execution log is
published with the review.

Median/IQR evidence was **not** converted to mean and standard deviation for
pooling. The Wan (2014) and Luo (2018) transformations assume approximate
symmetry, which is not tenable for the trials concerned here, so Tier C evidence
is reported in its original units alongside the primary model rather than inside
it.

### Digitization protocol

Where the primary outcome was recoverable only from a figure, digitization was
attempted under a pre-specified protocol: calibrate the axis against labelled
gridlines, extract the plotted values, and **validate the extraction against any
values stated in the trial's own text**. A digitization that failed this
validation was not admitted, regardless of how internally consistent the
extraction appeared.

---

## Results

### Primary analysis: TEAS versus inert sham (S0)

Four trials contributed directly compatible 0–24 hour data on TEAS versus an
inert sham (Chen 1998, Chen 2020, He 2026, Szmit 2021; n = 169 intervention,
168 control). TEAS was associated with a reduction of **13.99 mg IV MME**
(95% CI −34.18 to +6.19; *p* = 0.114) over the first 24 postoperative hours.
Heterogeneity was extreme (τ² = 156.9, I² = 98.6%, Q = 232.9 on 3 df,
*p* < 0.001) and the 95% prediction interval spanned −74.4 to +46.4 mg IV MME —
that is, the interval within which a future trial's true effect would be
expected to fall includes a large benefit, no effect, and a large harm.

Leave-one-out analysis gave pooled estimates between −8.41 and −18.77 mg IV MME,
and the result remained non-significant with every trial omitted in turn
(*p* = 0.095 to 0.281). No single trial drives the finding, and none rescues it.

### Supportive analysis: EA versus usual care (S0)

Three trials contributed directly compatible data on EA versus usual care or
no-stimulation control (El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024;
n = 164 intervention, 175 control): **−3.94 mg IV MME** (95% CI −19.77 to
+11.90; *p* = 0.397; τ² = 28.5, I² = 77.2%; prediction interval −86.3 to +78.4).

This estimate is reported separately, not merged with the sham-controlled TEAS
model, because a usual-care comparator answers a different question.

### An empty cell that must be stated

**No sham-controlled EA trial reports an analysable cumulative 0–24 hour opioid
mean and standard deviation in absolute dose units (k = 0).** The EA estimate
above is therefore an open-label comparison against usual care and cannot be
read as evidence of a specific acupoint effect. One sham-controlled EA candidate
exists in the wider 24-hour pool (Coura 2011), but it reports weight-normalised
fentanyl (µg/kg) and cannot be expressed in absolute dose without reconstructing
body weight, which the protocol prohibits.

### Tiered sensitivity analyses (S1, S2, S3)

**S1 added nothing.** No trial supplies a deterministic mean/SD derivation that
is not already Tier A. Chen 2015's rescue-bolus derivation is itself exact —
multiplying a bolus count by a fixed 2 mg of intravenous morphine is
order-preserving, so quantiles transform without assumption — but the reported
quantities are medians and IQRs, which places it in Tier C.

**S2 is reported in parallel, in the trials' own units.** Gao 2022 (n = 827 vs
828) reported 24-hour analgesic-pump sufentanil of 33.0 µg (IQR 0.0–50.0) versus
30.0 µg (IQR 0.0–60.0), *p* = 0.197. Chen 2015 (n = 41 vs 42) reported rescue
morphine of 2.0 mg (IQR 2.0–6.0) versus 7.0 mg (IQR 4.0–14.0), *p* = 0.004.
Neither was converted to a mean and standard deviation. In Gao 2022 the 25th
percentile is exactly zero in **both** arms, so the distribution is
zero-inflated and strongly non-normal; a symmetry-assuming recovery of the mean
and SD is not defensible there, and the large sample size would have given that
recovered value substantial weight in any pooled model.

**S3 is empty.** One trial (Gu 2019) reported cumulative analgesic consumption
only in a figure. Digitization was attempted: the y-axis calibrated exactly
against nine labelled gridlines (maximum residual 0.0000), and the
low-frequency TEAS arm reproduced the values stated in the trial's text to
within 4.2%. The control arm, however, was systematically overestimated by up to
16.0%, indicating an inconsistency between the figure and the text of the source
publication rather than an extraction error. Under the pre-specified protocol
the digitization failed validation, and Gu 2019 was not admitted. The extracted
values are recorded for provenance in
`07_TIERED_V33/03_DIGITIZATION/gu2019_digitization_QC.md` and are used in no
analysis. Author contact has been prepared.

S1 and S3 are therefore numerically identical to S0.

### Comparator, estimator and interval-method sensitivity

Substituting Szmit 2021's patient-controlled-analgesia-only arm for its sham arm
(a swap, not an addition) gave −14.07 mg IV MME (95% CI −34.18 to +6.04;
*p* = 0.112) — indistinguishable from the primary result.

Under a DerSimonian–Laird estimator with Hartung–Knapp intervals the estimate was
−14.02 mg IV MME (95% CI −34.19 to +6.14; *p* = 0.114). Under REML with
unadjusted Wald intervals it was −13.99 mg IV MME (95% CI −26.64 to −1.36;
*p* = 0.030). **This last result is not treated as a finding.** At k = 4 the
Wald interval is markedly anticonservative relative to the Hartung–Knapp
interval that was pre-specified; the shift to *p* < 0.05 reflects the choice of
reference distribution, not additional evidence.

### Broader scale-free sensitivity analysis

A standardized mean difference is scale-free, so weight-normalised endpoints can
legitimately be pooled with absolute-dose endpoints. Across the seven strict
trials plus Coura 2011 and Sim 2002 (k = 9), Hedges' *g* was **−0.97**
(95% CI −1.80 to −0.14; *p* = 0.028; I² = 95.0%), essentially identical in point
estimate to the strict-set SMD (*g* = −0.97, 95% CI −2.09 to +0.15,
*p* = 0.079). The interval is narrower because there are more studies, not
because the effect is larger; at I² ≈ 95% the nominal significance carries little
weight on its own.

Zhang 2025 was removed from this analysis in v33 (k = 10 → 9). It reports
postoperative day 1 rather than an explicit 0–24 hour clock window measured from
the end of surgery, which places it in Tier E. A scale-free metric changes the
unit, not the estimand, so the SMD does not rescue a window mismatch. The
superseded k = 10 model (*g* = −0.93, 95% CI −1.67 to −0.20, *p* = 0.018) is
retained in the results file as `OP24_BROADER_SMD_WITH_ZHANG` so the effect of
the exclusion is visible, but it is not a headline result. **The decision to
exclude Zhang 2025 was made on estimand grounds and recorded before the k = 9
model was fitted.**

---

## Discussion

### What the evidence supports

Across every analysis set, the direction of effect favours perioperative
transcutaneous electrical acupoint stimulation over inert sham for 24-hour
opioid consumption, and the point estimate is stable — approximately 14 mg IV
MME — under leave-one-out omission, comparator substitution, and change of
between-study variance estimator. That stability is worth something.

### What it does not support

It does not support a claim of demonstrated efficacy. The pre-specified primary
analysis rests on **four trials**, its confidence interval includes no effect,
and its prediction interval spans a large benefit through a large harm. I² of
98.6% indicates that these four trials are not estimating a common effect; the
pooled mean is a summary of a heterogeneous set, not an estimate of a single
underlying quantity that a clinician could expect to obtain.

Three findings deserve particular emphasis:

1. **The sham-controlled evidence base for EA on this outcome is empty.** Every
   EA trial contributing to the 24-hour opioid estimate used an open-label
   usual-care control. Expectation effects and clinician behaviour are not
   controlled in such designs, and opioid consumption is a behaviourally
   mediated outcome.

2. **Most of the apparently relevant literature is not analysable for this
   estimand.** Of 93 audited candidate rows, seven trials supplied directly
   compatible data. The remainder differ in window, unit, distributional form,
   or reporting completeness. This is a reporting problem, not an absence of
   trials, and it is the single most actionable finding for future investigators:
   report cumulative opioid consumption over an explicit clock window, in an
   absolute dose unit, as a mean with a standard deviation, alongside whatever
   other summary the data's distribution warrants.

3. **Statistical significance in this body of evidence is fragile in a specific,
   diagnosable way.** Two analyses here cross *p* = 0.05: the broader scale-free
   SMD, and the primary model re-fitted with unadjusted Wald intervals. Neither
   changes the conclusion. The first carries I² ≈ 95% and mixes estimands loosely
   enough that its precision is not credible; the second differs from the
   pre-specified analysis only in the reference distribution used to construct
   the interval. Reporting either as the headline would be a choice of method
   made after seeing the result.

### Limitations

The primary analysis is small (k = 4) and severely heterogeneous, so both the
pooled estimate and the τ² on which its interval depends are imprecisely
estimated; Hartung–Knapp intervals mitigate but do not remove this. The tiered
classification itself involves judgement at its boundaries — particularly the
Tier B/Tier C line — although the classification of every row is published for
inspection. Publication and reporting bias could not be formally assessed: with
k < 10 in every stratum, funnel-plot asymmetry tests are uninformative and none
was performed. Finally, the Gu 2019 figure–text inconsistency and the several
trials awaiting author clarification mean the evidence base characterised here
may change; the tiered structure is designed so that any such clarification
moves a trial between tiers and the analysis follows, without renegotiating the
protocol.
