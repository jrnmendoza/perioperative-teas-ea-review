# Current state — adjudication v38

20 September 2026 · PROSPERO CRD420261452908 · current analytical release adopted under user delegation. All decisions are posthoc with results known.

## Completed

- Wu2016 citation route recorded; all 225 full-text/citation records reconciled locally. 70 included reports / 69 operational families.
- 94 fresh exact-result RoB assessments across 40 reports, including all 90 currently non-sensitivity component results. Unique v38 IDs and source locators; historical records preserved.
- All 38 GRADE recommendations reviewed: 11 Low, 4 Not rated — insufficient evidence, 18 Very low, 5 Moderate.
- Methodological choices adopted; no further reviewer approval awaited. Prior human completion is user-reported; new decisions are AI-conducted.
- Zheng continuous data held from main models; Wu2025 pre-intervention dose removed from causal synthesis and retained as diagnostic.
- Local dashboard now reads canonical v38 data; article-figure assets preserved. No publication/deployment authorized.

## Primary conclusion unchanged

| Body | k | N | MD mg IV MME (95% CI) | Certainty |
|---|---:|---:|---|---|
| opioid24_TEAS_sham | 1 | 48 | -7.70 (-10.62, -4.78) | Low |
| opioid24_EA_sham | 0 | 0 | No eligible data | Not rated — insufficient evidence |
| opioid24_TEAS_usual | 1 | 47 | -8.00 (-10.92, -5.08) | Low |
| opioid24_EA_usual | 2 | 159 | -6.83 (-76.39, 62.73) | Very low |

No body establishes the registered joint criterion (≥10mg sparing with paired ~24h pain upper CI <+1). Szmit has discharge rather than eligible fixed-24h pain; separate pain studies do not provide the missing pairing.

## What remains a limitation, not an approval queue

The 12-reference import gap lacks record-level mapping; upstream deduplication can be reconciled arithmetically but not fully replayed. Historical outcome-focused exclusions leave review-wide completeness uncertain. The user withdrew re-screening; no screening package or reviewer approval is awaited. Source ambiguities remain explicit holds/diagnostics. These limitations prevent claiming that numerical reproducibility certifies source truth or exhaustive evidence selection.

Eleven author queries were SENT on 2026-09-22 by the review author (Jin 2023, Xie 2014, Yeh 2010/2011, Ntritsou 2014, Chen 1998, Lee 2011, Lin 2002, Sim 2002, Coura 2011); Coura 2011 hard-bounced (undelivered); four drafted queries remain UNSENT (El-Rakshy 2009, Zheng 2025, He 2026 breast, Long 2025). No reply recorded; no analysis depends on one. Log: `10_FINAL_ADJUDICATION/02_DECISIONS/v38/author_query_log.csv`. Covidence was not edited. No commit, push or public deployment performed. Any submission manuscript must disclose AI-assisted adjudication, posthoc choices, selection chronology and source holds.

## Current files

`10_FINAL_ADJUDICATION/03_CANONICAL`, `04_MODELS`, the root FINAL result/membership/participant tables, `02_DECISIONS/v38`, and dashboard/current_review data are authoritative. Earlier v26–v37 snapshots/reports remain historical. v38 baseline preserves pre-existing user dashboard/article-figure work.

74 estimands defined; 69 fitted, 33 pooled, five empty (four non-sensitivity plus one sensitivity). 761 canonical results; 177 model inputs. 12,103 is an operational randomized count, not an analysed efficacy population. Analyzed N is model-specific.

Numerical/integrity verification: `10_FINAL_ADJUDICATION/06_REPORTS/REPRODUCIBILITY_REPORT.md`. Full change comparison: `model_comparison_v38.csv`.

## Outcome-coverage addendum — 20 September 2026

The available-source coverage check covers all 70 included report texts. It identifies 16 QoR reports, 9 satisfaction/willingness reports, 2 additional quality-of-life reports and 2 additional acceptability reports. The 32 safety-relevant entries distinguish nonzero reactions, explicit zero statements, limited reporting and all-cause outcomes without established intervention attribution. No eligible opioid-use result beyond 30 days was located.

See [outcome coverage report](10_FINAL_ADJUDICATION/07_OUTCOME_COVERAGE/OUTCOME_COVERAGE_REPORT.md). The subsequent QoR analytical addendum below completes three approximately-24-hour bodies and their exact-result RoB/GRADE; the coverage report preserves its earlier audit status. The v38 74-model/38-GRADE analytical state above is unchanged. Its verification does not certify this new addendum; separate source/hash checks accompany the coverage report.

## QoR analytical addendum — 20 September 2026

Frozen v38 core unchanged: 74 models, 38 GRADE bodies, 94 assessments. This addendum adds 3 main models, 9 diagnostics, 3 grades and 8 exact-result assessments.

| Comparison (~24 h) | k | Reported analysis N | MD (95% CI), points | I² | Certainty |
|---|---:|---:|---|---:|---|
| QoR-40: TEAS versus sham, ~24 h | 2 | 131 | 10.19 (-13.26 to 33.63) | 0.0% | Very low |
| QoR-40: TEAS versus usual care, 24 h | 2 | 175 | 4.34 (-19.12 to 27.81) | 78.5% | Very low |
| QoR-15: TEAS versus sham, ~24 h | 4 | 327 | 7.49 (-0.71 to 15.68) | 80.1% | Very low |

Very low certainty for all three comparisons. A clinically important improvement is not established; absence of benefit is not demonstrated. Wu 2025: reported ITT n=50/50, observed completers 48/49; missing-data handling unexplained. Omission and denominator-only diagnostics provided.

Later QoR windows, unavailable supplements, median/range-only reports and source conflicts remain separate; no pooled EA or all-instrument effect.

Source: [QoR analysis report](10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/QOR_ANALYSIS_REPORT.md). The registered joint opioid/pain conclusion is unchanged.

## Deliverable status — corrected 20 September 2026

An earlier version of this section claimed completion of several deliverables
that had not been produced. It was corrected after a read-only verification
pass. The record below states what exists on disk.

**Completed**

- **Later-window QoR synthesis.** Six models in `08_QOR_ANALYSIS/qor_models_later.csv`:
  QoR-40 TEAS/sham POD2 (k=1, N=60); QoR-40 TEAS/usual care 48 h (k=1, N=70);
  QoR-15 TEAS/sham POD2 (k=1, N=97); QoR-15 TEAS/sham POD3 (k=2, N=130) with two
  leave-one-out diagnostics. Instrument, modality, comparator and window are kept
  separate; single-study bodies use normal intervals and are not described as
  pooled. Five exact-result RoB assessments, 110 signalling answers and 25 source
  locators accompany them.
- **Manuscript Results, Discussion, Abstract and Conclusions** drafted in
  `manuscript/`, corrected 20 September 2026 to report k and N for every body, to
  include the ~24-hour pain co-outcome, and to cover the additional outcome
  families that the first draft omitted.
- **24-hour QoR and v38 core preserved unchanged.** 74 models, 38 GRADE bodies,
  94 assessments; the three 24-hour QoR estimates are byte-identical to the
  handover record.

**Not completed — outstanding**

- **GRADE for the four new later-window QoR bodies.** `qor_grade.csv` covers only
  the three 24-hour bodies. The later-window results are reported in the
  manuscript as ungraded, and must not be presented as certainty-rated evidence
  until domain judgements exist.
- **Structured length-of-stay, PACU, extubation and mobilisation tables.**
  `10_FINAL_ADJUDICATION/los_audit.md` and `los_exact.md` contain located source
  excerpts only. They are not structured narrative tables: they do not separate
  total hospital stay from postoperative stay from PACU stay, carry no
  definition/unit/time-point/comparator columns, and do not distinguish
  reported-but-unusable outcomes from outcomes not located.
- **Finalised harms and satisfaction tables.** No new harms/satisfaction
  deliverable was produced. The dispositions — including the Gu 2019 count/prose
  conflict and the Liu 2026 ESD mean-rank ambiguity — remain where they were
  already documented, in `07_OUTCOME_COVERAGE/OUTCOME_COVERAGE_REPORT.md` and
  `safety_evidence.csv`. No composite adverse-event risk ratio was calculated,
  and none should be.
- **Reference registry and claim-citation audit extension.**
  `references/reference_registry.csv` and `claim_citation_audit.csv` are
  unchanged by this work; placeholders in the manuscript are unresolved.

**Holds retained, not resolved.** Chen 2015, Gao 2022, Grech 2016, He 2026
hepatectomy, Lu 2022, Huang 2025, Zheng 2025 and Zhu 2022 remain held from
quantitative QoR synthesis on the grounds recorded in
`08_QOR_ANALYSIS/QOR_ANALYSIS_REPORT.md`. None contributed to any model. A hold
is a completed disposition; it is not a resolved data gap.
