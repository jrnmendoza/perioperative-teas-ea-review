# Results

> **Draft status.** Corrected 20 September 2026 against adjudication **v38** plus
> the QoR addendum. Every effect, interval, I² and certainty rating below is
> transcribed from `04_MODELS/model_outputs.csv`, `03_CANONICAL/grade.csv` or
> `08_QOR_ANALYSIS/`. The earlier draft of this section omitted k and N for the
> primary bodies, omitted the ~24-hour pain co-outcome entirely, and did not
> report the nausea/vomiting, gastrointestinal, intraoperative-opioid or
> rescue-analgesia families.

## Study selection

Searches returned 5,100 references (Embase 1,928; CENTRAL 1,698; PubMed 1,009;
CINAHL 465). Historical import records total 5,088; the 12-reference difference
could not be mapped to individual records and is reported as an unexplained
import gap rather than as duplicate removal. After 2,160 recorded upstream
removals, 2,928 records were screened and 2,704 excluded at title and abstract,
leaving 224 reports sought. Two were not retrieved and six were late exact
duplicates, leaving 216 distinct reports assessed, of which 147 were excluded.
Sixty-nine database reports were included, plus one report identified by
citation searching (Wu 2016), giving **70 included reports representing 69
operational trial families**. Yeh 2010 and Yeh 2011 are treated as one probable
overlapping family, counted once and held out of every model.

Full-text exclusion reasons were: no perioperative analgesia outcome found, 113;
publication language, 12; setting, 8; intervention, 7; comparator, 3;
population, 2; design, 1; abstract only, 1. Six reports previously recorded as
excluded were reinstated by later source-verified adjudication, among them Szmit
2021, which is the sole contributor to the principal primary-outcome estimate.
No re-screening of excluded records was undertaken.

Across the 70 reports, 12,103 participants were randomised. This is an
operational count, not an analysed or efficacy denominator; analysed N is
body-specific and is given for every estimate below.

## Characteristics of included reports

Reports span 1998 to 2026. By modality, 49 are TEAS, 20 are EA and one (Long
2025) could not be classified from the source. By modality and comparator: TEAS
versus sham 45, TEAS versus usual care 3, TEAS versus active electrical control
1, EA versus sham 12, EA versus usual care 8. Fifty-four reports are from China,
four from Taiwan, two each from the USA and Hong Kong, and one each from Poland,
the United Kingdom, Greece, Turkey, Malaysia, Singapore and Brazil; one country
was not verified. Forty-eight of the 70 reports contribute to at least one
model.

## Risk of bias

At study level, 31 reports were judged at high risk of bias and 39 at some
concerns. **No report was at low risk of bias across all domains**, so a
low-risk-only sensitivity analysis was not possible.

Ninety-four fresh result-specific RoB 2 assessments were made across 40 reports,
covering all 90 non-sensitivity component results; 78 were some concerns, 15
high and one low. The entire principal primary-outcome body rests on a single
result judged at some concerns.

## Primary outcome: systemic opioid, end of surgery to 24 hours

**No evidence body establishes the registered joint criterion** (≥10 mg IV MME
sparing together with paired ~24-hour pain evidence whose upper 95% confidence
limit lies below +1 point). No point estimate reaches −10 mg, and the single
trial supplying the principal opioid estimate does not supply eligible ~24-hour
pain data: its VAS is adjudicated as discharge pain. Pain evidence from other
trials cannot supply the missing pairing.

| Body | Role | k | N | MD (95% CI), mg IV MME | Certainty |
|---|---|---:|---:|---|---|
| TEAS versus sham | Principal | **1** | **48** | −7.70 (−10.62 to −4.78) | Low |
| EA versus sham | Principal | **0** | **0** | No eligible data | Not rated |
| TEAS versus usual care | Supportive | **1** | **47** | −8.00 (−10.92 to −5.08) | Low |
| EA versus usual care | Supportive | 2 | 159 | −6.83 (−76.39 to 62.73), I² 72.5% | Very low |

Both TEAS bodies are **single-study contrasts from one three-arm trial (Szmit
2021, laparoscopic inguinal hernia repair)** reported with within-study normal
confidence intervals. They are not pooled random-effects estimates, and no
heterogeneity statistic or prediction interval is defined for them. The EA
versus usual care interval spans −76 to +63 mg and is uninformative.

**No sham-controlled electroacupuncture result met the registered construct.**
This is an explicit empty cell for the registered outcome rather than an
unreported analysis. One sham-controlled trial with incomplete capture is
reported in the post-hoc broadened analysis below.

### Sensitivity analyses

Admitting results whose systemic capture is incomplete or uncertain does not
change the conclusion.

**Post-hoc broadened estimand (E2).** Applied uniformly, E2 admitted seven
TEAS-versus-sham trials (N=581): −6.17 mg IV MME (−12.47 to 0.14), I² 98.0%,
95% prediction interval −22.12 to 9.78. That is smaller and less precise than the
registered single-study contrast. **Every E2 sensitivity analysis crossed the
null, and none reached −10 mg:**

| Analysis | k | MD (95% CI), mg IV MME |
|---|---:|---|
| Sufentanil factor 0.25 mg per µg | 7 | −4.27 (−9.14 to 0.60) |
| Sufentanil factor 1.0 mg per µg | 7 | −9.24 (−18.97 to 0.49) |
| Without the two reports admitted by amendment E2.1 | 5 | −8.43 (−17.78 to 0.91) |
| Omitting Gu 2019 (figure–text contradiction) | 6 | −7.11 (−14.68 to 0.46) |
| Omitting Lee 2011 (tabular contradiction) | 6 | −6.67 (−14.53 to 1.18) |
| Omitting results with known unquantified rescue | 5 | −5.07 (−12.23 to 2.10) |
| Omitting equivalents of unstated route | 6 | −7.25 (−14.58 to 0.08) |
| Leave-one-out, range | 6 | −3.92 to −7.25 |

The two reports admitted by amendment were Zhang 2025, whose postoperative-day-1
total was taken as 24 hours, and Gu 2019, whose 24-hour value was digitised.
In Gu 2019's figure, the control-arm bars exceed the control means printed in the
text by 1.85 to 3.90 mL at each time point where both are reported. The digitised
24-hour control value may therefore be overstated.

E2 admitted one sham-controlled electroacupuncture trial (Lin 2002, N=75):
−11.80 (−18.52 to −5.08). This is a single-study contrast from a trial at high
risk of bias. Its PCA began at the first postoperative hour, and a first-hour
intramuscular pethidine rescue, which has no registered conversion factor, was not
quantified. The trial reports pain only graphically and contributes no eligible
~24-hour pain result, so the joint criterion could not be evaluated. EA versus
usual care under E2 (k=4, N=414) gave −8.14 (−23.06 to 6.77), I² 90.4%.
TEAS versus usual care was unchanged. **No E2 body met the joint criterion.**

An earlier and narrower expansion (k=4) gave −7.36, −9.76 and −14.00 across the
three sufentanil factors, all crossing the null. It is retained in Additional
file 9. Omitting the high-risk contributor from the registered EA usual-care
body leaves a single study, −12.56 (−21.16 to −3.96). All of these are
sensitivity analyses and are not primary results.

## Co-primary outcome: pain at approximately 24 hours

| Body | k | N | MD (95% CI), 0–10 points | Certainty |
|---|---:|---:|---|---|
| Rest, TEAS versus sham | 3 | 218 | **−0.213 (−0.754 to 0.327)**, I² 0.0% | **Moderate** |
| Movement, TEAS versus sham | 1 | 100 | 0.040 (−0.206 to 0.286) | Moderate |
| Movement, EA versus sham | 1 | 114 | −0.338 (−0.728 to 0.052) | Moderate |
| Rest, EA versus sham | 0 | 0 | No eligible data | Not rated |
| Rest, TEAS versus usual care | 0 | 0 | No eligible data | Not rated |

The rest-pain comparison is the **only moderate-certainty body in the review**,
and it indicates little or no difference. Imprecision was not downgraded because
the whole confidence interval lies within the registered −1 to +1 margin. This
supports a statement about average 24-hour rest pain only: it is not paired
opioid/pain evidence, and it is not a formal non-inferiority result.

## Additional outcomes

### Nausea, vomiting and composite PONV

| Body | k | N | RR (95% CI) | Certainty |
|---|---:|---:|---|---|
| Composite PONV 0–24 h, TEAS vs sham | 10 | 3,447 | 0.640 (0.517 to 0.793), I² 47.5% | Low |
| Nausea 0–24 h, TEAS vs sham | 3 | 735 | 0.668 (0.287 to 1.553), I² 35.1% | Very low |
| Vomiting 0–24 h, TEAS vs sham | 4 | 2,390 | 0.680 (0.345 to 1.342), I² 55.3% | Very low |
| Persistent nausea >5 min 0–24 h, TEAS vs sham | 1 | 1,655 | 0.429 (0.249 to 0.739) | Low |
| Composite PONV 0–48 h, TEAS vs sham | 1 | 62 | 0.542 (0.343 to 0.854) | Low |
| Nausea 0–48 h, TEAS vs sham | 1 | 277 | 0.456 (0.299 to 0.695) | Low |
| Vomiting 0–48 h, TEAS vs sham | 1 | 277 | 0.336 (0.164 to 0.687) | Low |
| Vomiting 0–24 h, TEAS vs usual care | 1 | 105 | 0.483 (0.241 to 0.967) | Very low |
| Nausea 0–24 h, EA vs usual care | 2 | 237 | 0.660 (0.059 to 7.441) | Very low |
| Vomiting 0–24 h, EA vs usual care | 2 | 237 | 0.529 (0.017 to 16.691) | Very low |
| Nausea 6–24 h, EA vs usual care | 1 | 400 | 0.500 (0.325 to 0.772) | Moderate |
| Vomiting 6–24 h, EA vs usual care | 1 | 400 | 0.338 (0.196 to 0.583) | Moderate |
| Composite PONV 0–24 h, TEAS vs active electrical | 1 | 85 | 0.307 (0.091 to 1.038) | Very low |

The composite favours TEAS at low certainty, but its separated components at 24
hours both cross the null. The two moderate-certainty EA bodies come from a
single 400-participant trial within a narrower 6–24 hour window than registered
and should not be read as the review's headline.

### Gastrointestinal recovery

| Body | k | N | MD (95% CI), hours | Certainty |
|---|---:|---:|---|---|
| First flatus, TEAS vs sham | 7 | 1,420 | −4.983 (−9.507 to −0.459), I² 83.1% | Very low |
| First flatus, EA vs sham | 1 | 110 | −7.200 (−16.215 to 1.815) | Very low |
| First flatus, EA vs usual care | 4 | 725 | −2.888 (−5.387 to −0.388), I² 56.0% | Low |
| First flatus, TEAS vs usual care | 0 | 0 | No eligible data | Not rated |
| First bowel sounds, TEAS vs sham | 2 | 727 | −6.086 (−20.323 to 8.150), I² 0.0% | Very low |
| First defecation, TEAS vs sham | 4 | 1,182 | −7.769 (−17.468 to 1.930), I² 52.3% | Very low |
| First defecation, EA vs sham | 1 | 110 | −21.600 (−37.095 to −6.105) | Low |
| First defecation, EA vs usual care | 4 | 435 | −10.106 (−32.890 to 12.678), I² 97.6% | Very low |

A negative mean difference denotes an earlier event; it does not demonstrate
improved global recovery. Three continuous results from Zheng 2025 were removed
from all main analyses because the printed means and standard deviations cannot
generate the trial's own printed P values and the flatus/stool endpoint is
ambiguous. That removal reduced the flatus body from k=8 to k=7 and changed
bowel sounds from a significant −7.191 (−11.618 to −2.763) to the null estimate
above. Readers should weigh this accordingly.

### Intraoperative opioid, rescue analgesia, and later opioid windows

| Body | k | N | Effect (95% CI) | Certainty |
|---|---:|---:|---|---|
| Intraoperative remifentanil, TEAS vs sham | 4 | 828 | −175.70 µg (−289.87 to −61.54), I² 0.0% | Low |
| Intraoperative remifentanil, TEAS vs usual care | 2 | 175 | −25.28 µg (−1108.96 to 1058.40) | Very low |
| Intraoperative remifentanil, EA vs sham | 1 | 70 | −38.30 µg (−309.98 to 233.38) | Very low |
| Intraoperative remifentanil, EA vs usual care | 1 | 400 | −16.76 µg (−74.25 to 40.74) | Low |
| Rescue pethidine 0–24 h, TEAS vs usual care | 1 | 31 | −12.46 mg (−37.69 to 12.77) | Very low |
| Rescue pethidine 0–24 h, TEAS vs active electrical | 1 | 31 | −13.09 mg (−44.19 to 18.01) | Very low |
| PCA opioid 0–48 h, EA vs usual care | 1 | 81 | −6.00 mg IV MME (−10.63 to −1.37) | Very low |
| PCA opioid 0–72 h, EA vs sham | 1 | 25 | −8.40 mg IV morphine (−22.32 to 5.52) | Very low |

The intraoperative TEAS versus sham body is the most internally consistent
pooled opioid result in the review (I² 0.0%). Two exclusions produced that
consistency and are disclosed: the Zheng 2025 continuous results above, and the
Wu 2025 intraoperative dose, which preceded randomisation and treatment on
arrival in the recovery unit and is retained only as a pre-intervention negative
control. The 48- and 72-hour opioid outcomes are additional, not co-primary.

### Quality of recovery

Three approximately 24-hour bodies were synthesised. Positive values favour
TEAS.

| Body (~24 h) | k | Analysis N | MD (95% CI), points | I² | Certainty |
|---|---:|---:|---|---:|---|
| QoR-40, TEAS vs sham | 2 | 131 | 10.19 (−13.26 to 33.63) | 0.0% | Very low |
| QoR-40, TEAS vs usual care | 2 | 175 | 4.34 (−19.12 to 27.81) | 78.5% | Very low |
| QoR-15, TEAS vs sham | 4 | 327 | 7.49 (−0.71 to 15.68) | 80.1% | Very low |

A clinically important improvement is not established, and absence of benefit is
not demonstrated. One contributing trial reports intention-to-treat denominators
of 50 and 50 against 48 and 49 observed completers with unexplained missing-data
handling; omission and denominator stress diagnostics are provided.

Later-window results are reported separately and **are not certainty-rated**:
QoR-40 TEAS versus sham at POD2, 3.67 (0.83 to 6.51), k=1, N=60; QoR-40 TEAS
versus usual care at 48 h, 2.00 (0.82 to 3.18), k=1, N=70; QoR-15 TEAS versus
sham at POD2, 3.86 (−0.09 to 7.81), k=1, N=97; QoR-15 TEAS versus sham at POD3,
11.54 (−40.70 to 63.78), k=2, N=130. GRADE judgements for these four bodies have
not yet been made, and they should not be presented as certainty-rated evidence
until they are.

Eight further reports with located QoR data were held from synthesis and
contributed to no model: Chen 2015 and Lu 2022 (median-based data), He 2026
hepatectomy (dispersion labelled as range), Gao 2022 (unavailable supplement and
global variance), Grech 2016 (subgroup and graph-derived denominators), Huang
2025 (EA at discharge rather than TEAS at 24 hours), Zheng 2025 (unresolved
dispersion and contrast conflicts) and Zhu 2022 (unspecified timing and a shared
control across three EA arms). No median was converted to a mean and no
dispersion was inferred to admit any of them.

### Length of stay, PACU stay and mobilisation

Source statements were located across the included reports but have **not yet
been assembled into structured tables**, and no synthesis was attempted.
Constructs are not interchangeable — total hospital stay, postoperative stay and
PACU stay are distinct, as are extubation time and time to first ambulation —
and definitions, units and time origins differ across reports. Pooling them
would create an outcome the protocol does not define. Individual trials report
shorter PACU stay and earlier ambulation with TEAS, but these are isolated
uncontrolled-for comparisons that have not been assessed for risk of bias or
certainty here, and counting statistically significant trials is not a synthesis.
This coverage remains incomplete and is recorded as such.

### Harms

Harms were inconsistently reported and **no pooled comparative safety estimate
was computed**; definitions, ascertainment windows and denominators differ too
widely. A blanket statement of no adverse events would be false. Located reports
include electrode dermatitis, electrical discomfort, needle-related and
tolerance incidents, needling-site pain and itching, and withdrawals attributed
to skin reactions. Explicit statements of no events were recorded as such and
distinguished from absent reporting; reports without a safety statement were not
assigned zero events. All-cause postoperative events were not relabelled as
device-related, withdrawal denominators were taken as randomised rather than
analysed arm sizes, and separately tabulated event types were not summed into
counts of unique affected patients. One trial reports two deaths in the TEAS arm
and none in control at six months; the article does not establish intervention
causation, and this is neither presented as intervention-caused mortality nor
erased by a claim of no serious events.

### Satisfaction and acceptability

Nine reports assessed satisfaction or willingness to repeat treatment, using
instruments that are not interchangeable: 10-point and 0–100 scores, ordered
categories, a 6-point Likert scale, a 5-point "extremely satisfied" endpoint,
and willingness to repeat. Several give only narrative or overall percentages.
No pooled satisfaction estimate is justified. Two source conflicts are retained
rather than resolved: Gu 2019's narrative percentages conflict with its own
category counts, and Liu 2026 ESD labels values as mean and standard deviation
in its table while describing them as mean ranks in prose, with unclear timing.

### Persistent postoperative opioid use

No included report supplied an eligible result for persistent postoperative
opioid use beyond 30 days in the available source material. Later pain outcomes,
30-day complication counts and a trial's total study duration are not measures of
persistent opioid use. This review therefore cannot determine whether
perioperative TEAS or EA affects persistent opioid use.

## Outcomes with no eligible evidence

Four non-sensitivity estimands are explicitly empty: systemic opioid 0–24 h for
EA versus sham; rest pain at ~24 h for EA versus sham; rest pain at ~24 h for
TEAS versus usual care; and time to first flatus for TEAS versus usual care.
These are reported as findings, not omissions.

## Source contradictions and holds

Eight source contradictions were identified and dispositioned without altering
any printed value: opioid totals below a trial's own stated basal infusion;
author-reported morphine equivalents of unestablished oral or intravenous basis;
conflicting arm labels and denominators across a report's flow diagram, baseline
table and abstract; printed dispersions that cannot generate the report's own
printed P values; repeated implausibly small dispersion estimates; probable
cohort overlap between companion reports; unestablished anaesthetic technique;
and an intervention description that does not distinguish needle from surface
stimulation. Each was handled as a hold, a diagnostic-only admission, or a
leave-out analysis, and each is itemised with its disposition in Additional file
10. Author queries were drafted for these contradictions and for the sham-controlled
results held on classification grounds; eleven were sent on 22 September 2026 and
**no reply had been received at the time of writing**. No
result depends on a response.
