# Quality of recovery at approximately 24 hours

20 September 2026. Additive analytical release, following the 70-report coverage audit.

## Conclusion

The three identified mean/SD bodies have now been synthesized, with eight fresh exact-result RoB assessments and three adopted GRADE judgments. Positive mean differences favor TEAS. All three pooled 95% confidence intervals include zero and all three bodies have **Very low certainty**. These results do not establish a clinically important recovery benefit and do not demonstrate absence of benefit.

| Comparison (~24 h) | k | Reported analysis N | MD (95% CI), points | I² | Certainty |
|---|---:|---:|---|---:|---|
| QoR-40: TEAS versus sham, ~24 h | 2 | 131 | 10.19 (-13.26 to 33.63) | 0.0% | Very low |
| QoR-40: TEAS versus usual care, 24 h | 2 | 175 | 4.34 (-19.12 to 27.81) | 78.5% | Very low |
| QoR-15: TEAS versus sham, ~24 h | 4 | 327 | 7.49 (-0.71 to 15.68) | 80.1% | Very low |

N is the reported analysis population for each result, not the operational randomized review total. Wu 2025 reports ITT n=50/50 but 48/49 observed completers. The four-study QoR-15 N=327 therefore includes three incompletely explained missing observations; it is not 327 verified observed scores.

## Membership, comparability and estimand

- QoR-40/sham: Yao 2015 and Yu 2020, both gynecological laparoscopy, preoperative TEAS and no-current electrode controls.
- QoR-40/usual care: Liang 2021 (TURP) and Pan 2023 (laparoscopic myomectomy). Their no-stimulation/no-TEAS comparators remain usual care, not silently relabelled sham. Different surgery/sex and recovery levels limit a single common-effect interpretation; random-effects pooling estimates an average within the registered broad surgical scope.
- QoR-15/sham: Hou 2023 (living-donor nephrectomy), Wu 2025 (thoracoscopic wedge resection), Xing 2022 (older gastric-cancer surgery patients), Zhou 2025 (mixed laparoscopic gynecological procedures). Instruments, global-score direction and early postoperative windows match. Operations, treatment schedules and baseline analgesia vary; heterogeneity is reported and downgraded rather than treating all protocols as equivalent.
- Xing uses NTG versus NG, with TAP block in both arms. The G arm is excluded from this contrast because it would confound TEAS with the block. Hou also has balanced TAP block, and Wu balanced paravertebral block.
- Hou D2 means postoperative day 1. POD1 is treated as approximately 24 h, not asserted to be exactly 24 clock-hours for every participant. Each family contributes once per body. No repeated timepoints, domains or shared controls are counted as independent trials.
- All eight contributors are distinct operational trial families in the existing registry. Five result IDs link to existing global-score records; three newly located results are additive records. The frozen 761-row canonical table is not overwritten.

## Statistical method

Unadjusted endpoint mean difference = intervention mean minus comparator mean. Sampling variance = SD_intervention²/n_intervention + SD_control²/n_control. Scales remain separate; there is no combined QoR-15/QoR-40 SMD headline. No median-to-mean conversions, invented SDs or domain-SD sums were used.

Random-effects REML, with safeguarded Hartung–Knapp standard error sqrt(max(1,q)/sum(weights)) and a t interval with k−1 degrees of freedom, follows the existing project policy. A single-study leave-one-out remainder uses a normal 95% CI and is explicitly not pooled. No prediction interval is supplied for k<5; no funnel test or meta-regression is attempted for k=2–4.

The very wide two-study intervals are a consequence of the adopted small-sample method, not a transcription error. They were not replaced by a narrower normal interval after seeing the result. Individual study intervals can exclude zero while the corresponding sparse random-effects pooled interval includes it. See [metafor documentation](https://wviechtb.github.io/metafor/reference/rma.uni.html).

## Risk of bias and certainty

Assessments target assignment to intervention and are AI-conducted under the user's delegation, not a newly claimed independent human review. All 22 signalling responses and five domain rationales per result are recorded. Ratings are manual source-informed judgments, not asserted outputs from validated RoB software. For self-reported QoR, the patient is the outcome assessor; a masked interviewer does not alone establish low measurement bias. See [Cochrane RoB guidance](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-08).

Seven results have Some concerns; Pan 2023 is High because recovery-related exclusions and probable awareness could bias recovery reporting. Sham descriptions were checked against actual stimulation and timing, not accepted solely from the phrase double blind. Wu's pre-intervention opioid assessment was not reused for its post-treatment QoR result.

### QoR-40: TEAS versus sham, ~24 h — Very low

- Risk of bias (−1): Serious: both trials have uncertain patient masking, with additional allocation/missing-data/analysis-plan concerns. All weight comes from Some-concerns results.
- Inconsistency (−0): No downgrade: the two effects (11.70 and 9.26) are similar with overlapping intervals, I2=0%. With two trials heterogeneity is imprecisely estimated; zero is not proof of homogeneity.
- Indirectness (−0): No downgrade for the defined adult general-anesthesia TEAS comparison and ~24-hour global recovery endpoint. Applicability remains limited to represented operations and protocols; this is not EA evidence or an opioid-sparing endpoint.
- Imprecision (−2): Very serious: safeguarded-HK 95% interval crosses both -6.3 and +6.3 points, admitting important harm, no effect and important benefit. Downgrade two levels for decision uncertainty, not simply k=2.
- Publication bias (−0): No additional downgrade: too few trials for informative funnel/asymmetry tests. Publication bias cannot be excluded. Other located QoR reports lack compatible statistics or have source holds; available-case synthesis is not a claim of complete recovery evidence.

### QoR-40: TEAS versus usual care, 24 h — Very low

- Risk of bias (−1): Serious: Pan (47.1% random-effects weight) is High for recovery-related exclusions and unmasked self-report; Liang has unresolved missingness/masking. One body-level downgrade; source reporting limitations retained.
- Inconsistency (−1): Serious: effects 2.60 versus 6.30, I2=78.5%, differ relative to the important-benefit benchmark; different procedures and baseline recovery leave variation unexplained.
- Indirectness (−0): No downgrade for the defined adult general-anesthesia TEAS comparison and ~24-hour global recovery endpoint. Applicability remains limited to represented operations and protocols; this is not EA evidence or an opioid-sparing endpoint.
- Imprecision (−2): Very serious: safeguarded-HK 95% interval crosses both -6.3 and +6.3 points, admitting important harm, no effect and important benefit. Downgrade two levels for decision uncertainty, not simply k=2.
- Publication bias (−0): No additional downgrade: too few trials for informative funnel/asymmetry tests. Publication bias cannot be excluded. Other located QoR reports lack compatible statistics or have source holds; available-case synthesis is not a claim of complete recovery evidence.

### QoR-15: TEAS versus sham, ~24 h — Very low

- Risk of bias (−1): Serious: all four subjective results have unresolved patient masking/analysis-plan concerns. Wu has unexplained ITT handling of three missing 24-hour observations; Xing has incompletely explained losses.
- Inconsistency (−1): Serious: effects range 4.38 to 14.90, I2=80.1%; Wu exceeds the other three. Clinical populations, treatment timing and blocks vary. Leave-one-out analysis identifies influence, not a proven explanatory subgroup.
- Indirectness (−0): No downgrade for the defined adult general-anesthesia TEAS comparison and ~24-hour global recovery endpoint. Applicability remains limited to represented operations and protocols; this is not EA evidence or an opioid-sparing endpoint.
- Imprecision (−1): Serious: 95% interval crosses zero and both the 6-point contextual benchmark and historical 8-point benchmark for important benefit. It does not cross -6; downgrade one level. Benchmark choice does not change this judgment.
- Publication bias (−0): No additional downgrade: too few trials for informative funnel/asymmetry tests. Publication bias cannot be excluded. Other located QoR reports lack compatible statistics or have source holds; available-case synthesis is not a claim of complete recovery evidence.

GRADE starts at High for randomized evidence and is floored at Very low after the documented downgrades. Imprecision judgments use the interval and decision thresholds, not an automatic small-k penalty. No precision claim relies on an arbitrary participant-count cutoff. Methods follow the [Cochrane certainty framework](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-14).

For contextual interpretation, QoR-40 uses 6.3 points from the original [Myles 2016 measurement study](https://pubmed.ncbi.nlm.nih.gov/27159009/). QoR-15 is considered against 6 points and the historical 8-point benchmark; both lead to the same imprecision downgrade. The [2021 update](https://pubmed.ncbi.nlm.nih.gov/34543410/) was bibliographically verified; the 6-point value is corroborated in the [trial authors' published methodological reply](https://onlinelibrary.wiley.com/doi/full/10.1002/ejp.2089). The original update's full text was not retrieved here. These are posthoc interpretive benchmarks, not newly claimed registered decision rules, universal patient-level responder thresholds, or evidence of opioid sparing.

## Source limitations and sensitivity analyses

Wu 2025's PDF flowchart explicitly shows 50/50 randomized, 48/49 completing, and 50/50 included in ITT. The three 24-hour losses were discharged early; no imputation method is described in the available report. The source's ITT result is retained with this uncertainty and a D3 concern. The denominator-only stress test uses 48/49 in the variance while retaining the printed means/SDs; it is hypothetical, **not** a recovered complete-case result or correction to the paper.

- QoR-15: TEAS versus sham, ~24 h; omit Wu 2025: k=3, N=227, MD 4.91 (-0.80 to 10.62). Leave-one-out diagnostic; not a new independent evidence body or certainty rating.
- QoR-15: Wu denominator-only stress test: k=4, N=324, MD 7.48 (-0.70 to 15.65). Hypothetical variance stress test: Wu n=48/49 while retaining printed means/SDs. Not observed complete-case data and not a correction to the source.
- QoR-40: TEAS versus usual care, 24 h; omit Pan 2023: k=1, N=70, MD 2.60 (0.56 to 4.64). Leave-one-out diagnostic; not a new independent evidence body or certainty rating.

All eight leave-one-out models are retained, not only those that change the conclusion. The smaller QoR-15 estimate without Wu indicates influence, not proof that Wu is wrong or that a specific surgical subgroup explains heterogeneity. The variance-only stress test cannot address bias from unreported imputation or missing outcomes.

Pan's analyzed table denominators are retained despite flow/exclusion-accounting limitations, and its High-risk influence is transparent. Yu's published adjusted/repeated-measures tests differ from the unadjusted endpoint contrast; these are not substituted for calculated confidence intervals. Zhou's POD3 P-value inconsistency remains a separate later-timepoint hold; the verified POD1 global means/SDs are used unchanged.

## Other located QoR evidence and scope boundary

Chen 2015 (QoR-40) and Lu 2022 (QoR-15) have median-based data; He 2026 hepatectomy labels dispersion as range, not SD. Gao 2022 requires an unavailable supplement/global variance; Grech 2016 has a subgroup/graph denominator problem; Huang 2025 is EA at discharge, not TEAS at 24 h; Zheng 2025 has unresolved global dispersion/contrast conflicts; Zhu 2022 has unspecified QoR timing and shared-control issues. These eight other reports are not silently counted as quantitative trials or assumed to show benefit. Their source findings remain in the coverage report.

POD2, POD3, POD7 and discharge evidence from contributing trials also remains separate. This release completes the three identified approximately-24-hour mean/SD syntheses, **not every possible recovery timepoint or missing-supplement investigation**. It does not newly analyze satisfaction, harms, length of stay, mobilisation, or persistent opioid use, and does not reopen screening.

## Manuscript-ready results

“Eight reports contributed to three separate approximately 24-hour global quality-of-recovery syntheses. The mean difference for TEAS versus sham was 10.19 points on QoR-40 (95% CI −13.26 to 33.63; two trials, reported analysis N=131) and 7.49 points on QoR-15 (95% CI −0.71 to 15.68; four trials, reported analysis N=327). For TEAS versus usual care, the QoR-40 mean difference was 4.34 points (95% CI −19.12 to 27.81; two trials, N=175). Certainty was very low for all three comparisons. Patient masking, missing-data/reporting limitations, substantial heterogeneity in two bodies, and imprecision prevented a confident conclusion of clinically important benefit. Wu 2025's reported ITT denominator included three patients without observed 24-hour follow-up; omission and denominator-only analyses were examined.”

These findings do not change the registered joint opioid/pain conclusion. They neither demonstrate clinically important opioid sparing nor establish absence of recovery benefit.

## Reproduction and integrity

The Python REML/HK implementation is cross-checked against R/metafor, which recalculates effects and variances from arm means/SDs/n. `qor_metafor_comparison.csv` supplies field-level comparisons. `verification.json` supplies source/core hashes, assessment completeness and numerical checks. Source PDF pages for Wu flow/table, Pan total-score table and Zhou total-score table were visually inspected; all eight source-text excerpts and immutable hashes were validated.

The frozen v38 core retains 74 models, 38 GRADE bodies and 94 assessments. This addendum adds three main models, nine diagnostics, three GRADE judgments and eight exact-result assessments. Core and addendum are displayed separately to avoid silently rewriting a previously validated release. No new reports/families are added, no external database is edited, and no author response, commit, push or public deployment is claimed.

Rebuild from the project root: run `build_qor_analysis.py`, `reproduce_qor.R`, then `finalize_qor_analysis.py`, using the same scipy/R environments recorded in the existing project and `R_session.txt`. Build the dashboard afterward and run `scripts/check_current_dashboard.py`.
