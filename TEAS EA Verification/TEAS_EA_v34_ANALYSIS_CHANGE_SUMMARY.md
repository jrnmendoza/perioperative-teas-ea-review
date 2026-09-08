# TEAS/EA v34 analysis change summary

**Primary unchanged; secondary source data expanded, with incompatible windows and unresolved records kept separate.**

## A–Q requested reconciliation report

| Item | Result |
| --- | --- |
| A. v33 outcome rows | 382 |
| B. v34 outcome rows | 757 |
| C. Net rows added | 375 |
| D. Existing source rows updated | 25 |
| E. Metadata corrections | 11 allocation rows, Tu 6–24h window, Sim IQR-width representation; generated status/ID fields also added to existing rows |
| F. Duplicates rejected | 1 |
| G. Graph-only rows added | 38 |
| H. NOT REPORTED rows added | 16 |
| I. SOURCE NOT ACCESSED | 2 outcome records; 7 studies with source-access gaps |
| J. Unresolved source conflicts | 24 unresolved records across 12 studies; 27 total conflict/correction records |
| K. New analysis-eligible secondary results | 215 native numeric candidates; 3 newly selected contrasts; all new candidates have result-specific RoB pending |
| L. Studies newly entering any secondary meta-analysis | 0 relative to the five existing v33 secondary datasets; Liang already contributed QoR, Pan already contributed remifentanil |
| M. Strict primary k before/after | 7 → 7 |
| N. Primary pooled estimate changed? | No; exact matched Stata reruns agree |
| O. Secondary analyses changed | Intraoperative remifentanil and sufentanil expand; exact-window QoR and rescue sets corrected; defecation strata unchanged |
| P. Author clarification | Gu 2019, Huang 2025, Jiang 2026, Liang 2021, Long 2025, Lu 2021, Lu 2022, Pan 2023, Tu 2024, Yu 2020, Zheng 2025, Zhu 2022 |
| Q. Output files | Exact paths at the end of this report |

## Strict primary opioid analysis

Combined historical audit estimate: MD -9.907002 mg IV MME; 95% CI -20.079361 to 0.265357; P=0.05453838. Both the combined audit and separate TEAS/sham (k=4) and EA/usual-care (k=3) estimates are unchanged. Total analyzed N=676. The same prespecified v33 conversion factors were applied to regenerated source values.

No binary rescue use, PCA press count, multimodal PCIA solution, author-defined intraoperative conversion, median, percentage or graph-only result was promoted into this strict primary model.

## Secondary selection changes

- **Remifentanil:** selected contrasts 8→9; Liang 2021 adds 521.5±206.8 vs 464.7±156.0 µg, analyzed 35/35. TEAS/sham k=5→6. Matched REML+Hartung–Knapp MD changes from −149.89 µg (95% CI −254.71 to −45.08) to −117.78 µg (−242.51 to 6.95). EA and usual-care strata are retained separately; single-study strata are not pooled.
- **Sufentanil:** selected contrasts 5→6, representing 4→5 unique studies because Wang 2024 has two risk strata within one trial. Liang adds 21.4±3.1 vs20.0±2.9 µg. TEAS/sham now has k=2, MD −9.44 µg (95% CI −32.40 to13.52), REML normal CI. Wang SNVP and MNVP are retained in separate stratum files and are never counted as two independent RCTs in one model.
- **QoR-40:** the former three-row ~24h set contained Yu POD1. That result is now kept separately. The exact 24h set contains Yao, Liang and newly extracted Pan global QoR-40; subscales are excluded from the global-score set. TEAS/sham remains Yao+Liang (k=2); Pan is a separate usual-care k=1 result. Thus the old mixed-window pooled estimate is not relabelled as an exact-24h estimate.
- **Rescue opioid incidence:** the former k=3 0–24h/POD1 set is withdrawn as an exact-window model. Tu is 6–24h; Liu burn is through POD1; Yu is exact0–24h. The strict 0–24h set now has k=1 and is not meta-analyzed. This affects a secondary rescue endpoint, not the strict primary opioid-dose k=7.
- **First defecation:** the seven selected independent study records are unchanged. TEAS/sham k=3 and EA/usual-care k=3 estimates are unchanged; Ng EA/sham is separate k=1. Sun adds three source results to the native data but they remain unpooled until an endpoint-specific shared-control selection is adjudicated.
- **Other families:** data preparation was regenerated for postoperative opioid other windows, rescue frequency, time to first rescue, pain, PONV, nausea, vomiting, antiemetics, QoR15/40, GI recovery, LOS, functional recovery, adverse events/cognition, and analgesic proxies/non-opioid rescue. These files retain native definitions, modalities, comparators and holds; no automatic new pooled estimate is claimed for every added outcome.
- **No GRADE update:** new extraction and provisional secondary analyses do not constitute completed result-specific RoB or certainty assessment.

## Current Stata estimates

| Analysis / stratum | k | Estimate | 95% CI | P | Model |
| --- | --- | --- | --- | --- | --- |
| intraop_remifentanil_TEAS_Sham | 6 | -117.7771 | -242.5056 to 6.9513 | 0.05958 | REML + Hartung-Knapp |
| intraop_sufentanil_TEAS_Sham | 2 | -9.4356 | -32.3953 to 13.5242 | 0.42055 | REML normal CI |
| qor40_24h_TEAS_Sham | 2 | 6.7163 | -2.1609 to 15.5935 | 0.13811 | REML normal CI |
| gi_first_defecation_EA_Usual_care | 3 | -4.0811 | -6.0671 to -2.0950 | 0.01255 | REML + Hartung-Knapp |
| gi_first_defecation_TEAS_Sham | 3 | -10.3982 | -23.1249 to 2.3285 | 0.07226 | REML + Hartung-Knapp |
| primary_24h_mme_EA_Usual_care | 3 | -3.9358 | -19.7732 to 11.9016 | 0.39689 | REML + Hartung-Knapp |
| primary_24h_mme_TEAS_Sham | 4 | -13.9953 | -34.1808 to 6.1903 | 0.11448 | REML + Hartung-Knapp |
| primary_24h_mme_ALL_AUDIT | 7 | -9.9070 | -20.0794 to 0.2654 | 0.05454 | REML + Hartung-Knapp |

Models are REML; Hartung–Knapp when k≥3, normal CI when k=2, no pooled estimate when k=1. These sparse secondary results are provisional. Exact group-value P conflicts are preserved and do not get silently repaired. Numeric native binary exports use a documented 0.5 correction to all four cells when needed; double-zero contrasts have no estimated logRR. None of the selected rerun models required that correction.

## Study-level reconciliation

| Study | Added | Existing source rows corrected | New native numeric candidates | Comment |
| --- | --- | --- | --- | --- |
| Zhu 2022 | 66 | 6 | 63 | Drive search did not return a standalone supplementary file. Main article references Supplemental Tables 1–2 for ITT PON/POV analyses. Main-table extraction is per-protocol. Randomized arm sizes conflict between abstract and CONSORT figure. |
| Yang 2020 | 27 | 0 | 14 | 59 randomized (30/29), 57 completed/analyzed (29/28). Rescue medication defined as bucinnazine 100 mg IM if VAS >3; exact rescue time window not attached to Table 3. |
| Pan 2023 | 26 | 0 | 15 | Paper has a participant-flow inconsistency: Methods mention 120 women, while abstract/results report 105 in the final study cohort (52/53). NRS is described in Results as measured in the mobile state. Table 7 parenthetical NRS statistic is not explicitly defined. |
| Lu 2022 | 17 | 0 | 4 | Main paper references multiple Supplemental Digital Contents; no standalone supplement was located in Drive in the current search. Major internal 24-h QoR-15 conflict between Results prose and Table 3; table values retained and conflict flagged. |
| Li 2021 | 12 | 0 | 12 | All six requested VAS≥4/PONV assessment timepoints are printed in Table 5. Analysis population is not explicitly labelled ITT/per-protocol in the publication. |
| Gu 2019 | 10 | 4 | 6 | 117/120 completed (L-TEAS 58, C-TEAS 59). Exact VAS at 4/8/24 h is printed; 16/36 h are graph-only. Figure 5 gives PONV counts 7 vs 19. Satisfaction prose conflicts with Table 4. The 24-h PCIA point is graph-only and represents multimodal PCIA solution volume, not a printed exact sufentanil mass. |
| Huang 2025 | 12 | 0 | 5 | Randomized 51 vs 50; analyzed 43 vs 45. Source directly reports VAS and I-FEED at 24/48/72 h, QoR-40 at discharge, LOS, vomiting, additional ketorolac use and bowel obstruction. Results prose says QoR-40 was lower with EA, but Table 4 shows 196 vs 192; the table direction is preserved and the conflict is flagged. |
| Gao 2021 | 7 | 0 | 2 | 610 randomized/analyzed (303 TEAS, 307 sham). Table III provides bowel-sound recovery plus abdominal pain, distention, nausea and vomiting-episode data. The main paper states no difference in 30-day complications or total LOS but directs exact values to Supplementary Table S4; those exact supplemental values are therefore SOURCE NOT ACCESSED, not NOT REPORTED. |
| Jiang 2026 | 10 | 0 | 6 | Secondary outcomes use PP n=294 vs 293; first-flatus ITT also exists separately. First defecation, abdominal distention, hospital cost, LOS and adverse events are directly printed. One NRS summary is printed without identifying whether it is the planned 6-, 24- or 48-h assessment; retained as AMBIGUOUS. Printed effect direction/CI oddities are preserved verbatim. |
| Wang 2023 | 11 | 0 | 5 | Randomized 43 vs 45; analyzed 40 vs 43. POD3 PSQI/AIS and rest/activity VAS trajectories are graph-only where exact values are not printed; no visual digitization was performed. LOS and adverse-event counts are directly tabulated. |
| Tu 2024 | 10 | 2 | 5 | 120 randomized; 115 analyzed (57 TEAS, 58 sham). Actual PDF confirms missing 0–2 h vomiting, nausea severity at all three intervals, early pain, metoclopramide rescue and zero TEAS AEs. The Results prose contains a typo for 2–6 h vomiting (P=0.47) while Table 3 and abstract report P=0.047; table value is authoritative for extraction. |
| Sun 2017 | 51 | 1 | 15 | 380 randomized (95/arm); 361 analyzed: SSS 90, TSS 91, TTS 91, TST 89. Exact 1/6/48 h pain values are not printed and are retained GRAPH ONLY. Table 2 provides percentage/95%CI data for nausea, vomiting, rescue antiemetic and satisfaction; raw event counts were not reconstructed. Table 2 also gives arm-specific intraoperative opioid, extubation, PACU, flatus and defecation results. |
| Sim 2002 | 24 | 1 | 2 | 90 randomized/analyzed (30/group). Table 2 gives mean VAS over 24 h plus PONV/drowsiness/pruritus percentages. Individual 6-hourly VAS values are not numerically printed. Figure 3 gives interval morphine trajectories; exact non-6–12 h values are graph-only. Source provides exact Group III 6–12 h morphine and alfentanil values missing from v33. |
| Lu 2021 | 24 | 0 | 14 | Three-arm multicenter trial: sham 188, single-PC6 198, combined PC6+CV17 190. Main PDF directly supplies 24-h rest/cough NRS, rescue parecoxib, nausea, vomiting, PONV severity, satisfaction, immediate recovery, and 3/6-month pain data. There are internal P-value conflicts between Table 3 and Results prose for rest NRS, cough NRS and rescue analgesia; both are preserved. |
| Long 2025 | 12 | 3 | 10 | 60 randomized, 53 analyzed. Table 7 gives 48-h VAS and LOS; Tables 5–6 give recovery and adverse-event data; Table 2 gives POD7 PND. Important source inconsistency: abstract reports 24-h EA VAS 2.65±0.94, whereas Table 7 reports 2.78±0.97; v33 uses the Table 7 value. PND percentages imply different denominators from the study-level analyzed group sizes and must remain flagged. |
| Wang 2024 | 12 | 0 | 7 | 140 randomized by NVP-risk stratum; analyzed SNVP-ODT 33/35 and SNVP-OD 35/35, MNVP 35/35 per subgroup. Table 3 supplies all interval PONV counts. A combined 0–6 h vomiting comparison is printed for the SNVP stratum. Pain VAS was prespecified at the same postoperative assessment times but numerical pain results are not reported. |
| Zheng 2025 | 26 | 0 | 20 | 88 randomized, 85 completed (42 TEAS, 43 control). Source directly reports interval nausea/vomiting, remifentanil, PCIA use, pain, PSQI, GI recovery, LOS and adverse reactions. QoR-40 6/24 h is figure-only; 48-h means are printed but exact SDs are not. Internal conflict: 24-h pain P=0.042 in prose but bP=0.422 in Table 4 footnote. |
| Yu 2020 | 5 | 2 | 5 | 60 randomized/analyzed, 30/group. POD2 QoR-40, PONV, rescue tropisetron and MMSE are missing from v33. Internal source conflicts: abstract gives TEAS pain SD 1.41/0.88 whereas Table 2 gives 1.53/0.98; Results prose says POD2 pain P=0.26 while Table 2 marks *P<0.05 and abstract calls both timepoints significant. |
| Liang 2021 | 13 | 6 | 5 | 80 assessed, 75 randomized (TEAS 37, control 38), 70 analyzed (35/group). v33 has reversed randomized-arm counts in its CRBD rows (38/37 instead of TEAS37/control38). Table 1 supplies intraoperative sufentanil/remifentanil. Table 4 supplies PONV, an ambiguously defined pain-event row, MMSE, QoR and extra analgesia. Major source conflict: abstract reports 48-h CRBD 4/35 vs7/35, whereas Table 2 prints 4/35 vs19/35; v33 currently uses the table value 19. |

## Remaining adjudication work

Prioritize Yu pain dispersion/significance; Long pain and PND denominators; Liang 48h CRBD and undefined analgesia/pain events; Lu2022 QoR15; Zhu QoR15 timing; Pan undefined NRS statistic/flow; Jiang unidentified NRS timepoint; and the missing supplements/protocols. Source conflicts with an existing table hierarchy remain visible even when table values are retained. Numeric-candidate status does not remove these restrictions.

## Exact output paths

- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v33_to_v34_RECONCILIATION_LOG.csv`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v34_QC_REPORT.md`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v34_ANALYSIS_CHANGE_SUMMARY.md`

Analysis CSVs and manifests: `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data`.
Stata result CSV: `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_model_results.csv`.
Reproducible code and Stata do-file: `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/code`.
