# TEAS/EA v34 reconciliation QC report

**PASS — reconciliation and export integrity. The workbook retains explicit source/adjudication holds; this is not a claim that every secondary result is ready for final pooling.**

The supplied consolidated source-PDF audit was reconciled against the frozen v33 master. The PDFs were not independently re-extracted in this run. New result-specific RoB assessments were not invented.

## Required PASS/FAIL checks

| Check | Status | Evidence |
| --- | --- | --- |
| Duplicate check | PASS | No new exact normalized composite duplicates; Li 2021 6-hour alias rejected independently. Full reviewed matching register retained. |
| Outcome-row reconciliation | PASS | 382 + 374 - 1 duplicate + 2 supplement-dependent endpoints = 757 |
| Canonical IDs | PASS | 70 canonical studies/reports; no original study disappeared; original comparison IDs retained. |
| Analysis_Readiness row agreement | PASS | 757 records in each; exact record ID links. |
| Strict primary k | PASS | 7 across all primary sheets; summary computed; TEAS 4 / EA 3; N=676. |
| Strict primary estimate unchanged | PASS | Stata matched source rerun identical for combined audit and both protocol strata. |
| Liang randomized/analyzed N | PASS | 4 CRBD rows; randomized 37/38, analyzed 35/35. |
| Gu no invented opioid mass | PASS | 24-h graph-only multimodal PCIA volume; no mass conversion. |
| Graph-only numeric protection | PASS | 38 new graph-only rows, no invented means/SDs. |
| Percentage protection | PASS | 19 percentage-only rows; no reconstructed events. |
| Median/range protection | PASS | 20 source ranges mapped to min/max, never Q1/Q3 or means. |
| Source-not-accessed distinction | PASS | 7 study-level supplement/protocol access gaps; 2 explicit Gao outcome rows. No replacement with NOT REPORTED. |
| Source-conflict preservation | PASS | 27 visible conflict/correction records, including all 11 required studies; raw source notes and quotations retained. |
| New result-specific RoB | PASS | No newly eligible outcome inherits study-wide Low/Some concerns/High. |
| Formula check (source/staging) | PASS | Inputs have no formulas/named ranges. No error-value cells introduced; exported XLSX is separately validated. |
| Stata consistency | PASS | 15 successful Stata model runs, native values rebuilt from current source; every selected model has independent study units. |
| Exported workbook cell round-trip | PASS | 0 substantive cell differences; empty strings and Excel blanks considered equivalent. All unchanged sheets checked against frozen v33. |
| Exported formula/error check | PASS | 0 error cells; 0 formulas; summaries regenerated as typed values, matching the source architecture. |
| Frozen v33 hash | PASS | 64ef683c58a1faa2bf408f415d03d96dd6622abf8ded24a72f43db9c47a82a2a |
| Original sheet preservation | PASS | All 31 original sheet names retained; 48 total sheets. |
| History snapshot V33_Outcome_Data_AF_LOCK | PASS | Every original value preserved in explicit history snapshot. |
| History snapshot V33_Stata_AF_Long | PASS | Every original value preserved in explicit history snapshot. |
| Readiness identities/values | PASS | 757 exact Outcome_Data-linked rows. |
| Set/readiness consistency | PASS | 0 discrepancies across all five Set_* sheets. |
| Active AF/Stata values | PASS | 0 numeric/endpoint discrepancies in regenerated Stata_AF_Long. |
| Workbook/CSV Stata consistency | PASS | AF long, primary native, selected secondary and full Outcome_Data exports all agree: [True, True, True, True] |
| Existing-cell change-log coverage | PASS | 0 unlogged changes; 2184 CSV/workbook log entries. |
| Change-log workbook/CSV consistency | PASS | Exact matching row count, headers and values. |
| Audit disposition completeness | PASS | Every audit row 2–375 has one disposition and target result ID. |
| Liang all-record allocation consistency | PASS | All original and new Liang records use randomized 37/38, including the unavailable-opioid row; analyzed 35/35 retained. |
| Printed mean with missing SD preserved | PASS | Zheng QoR-40 48h mean 184 vs181 retained; exact SD blank, HOLD. |
| New source-range and IQR bounds | PASS | No range inversion or median-to-mean conversion. |
| Numeric cell typing | PASS | Summary counts are numeric Excel cells, not formatted strings. |

## Inventory and reconciliation counts

| Metric | Result |
| --- | --- |
| v33 Outcome_Data | 382 |
| v34 Outcome_Data | 757 |
| Net additions | 375 |
| Existing source rows updated (original 38 columns) | 25 |
| Allocation metadata corrections | 11 rows: five Liang + six Zhu; analyzed denominators unchanged |
| Other metadata corrections | Tu rescue window; Sim IQR width representation |
| Audit duplicate rejected | 1 |
| New graph-only rows | 38 |
| New NOT REPORTED rows | 16 |
| SOURCE NOT ACCESSED outcome rows | 2 |
| Study-level supplement/protocol access gaps | 7 |
| Visible conflict/correction records | 27 |
| Unresolved records requiring author clarification | 24 |
| New numerically extractable secondary results | 215 |
| New eligible results with result-specific RoB pending | 215 |
| Canonical studies/reports | 70 |
| Strict primary before / after | 7 / 7 |
| Total workbook sheets | 48 |
| Change-log entries | 2184 |

The 374 audit records contribute 373 distinct outcome rows; Li 2021 VAS≥4 at 6h already matches v33. Two additional Gao outcomes are sourced from the reconciliation/source-access findings rather than All_Gapfill. All 382 original outcome rows remain in order; no source rows were deleted. An existing Sun aggregate placeholder remains visible but is excluded as superseded by three separate timing-arm records.

INCLUDE means numerically extractable in its native endpoint, unit, window, population and statistic. It does not authorize pooling across incompatible definitions. The 215 new candidates are not 215 independent trials or completed RoB assessments.

## Dispositions and active readiness

| Audit disposition | Rows |
| --- | --- |
| ADDED | 217 |
| ALREADY_PRESENT | 1 |
| AMBIGUOUS_HOLD | 33 |
| CONFLICT_HOLD | 1 |
| GRAPH_ONLY_ADDED | 38 |
| NOT_ANALYSIS_ELIGIBLE | 68 |
| NOT_REPORTED_ADDED | 16 |

| Active readiness | Rows |
| --- | --- |
| CONDITIONAL | 4 |
| DUPLICATE HOLD | 4 |
| EXCLUDE | 4 |
| GRAPH ONLY | 63 |
| HOLD | 62 |
| INCLUDE | 464 |
| NARRATIVE ONLY | 99 |
| NOT REPORTED | 55 |
| SOURCE NOT ACCESSED | 2 |

## Source access and author clarification

Unaccessed supplements/protocols: Zhu 2022, Lu 2022, Gao 2021, Jiang 2026, Tu 2024, Lu 2021, Zheng 2025. Gao has two explicit missing outcome records (total LOS and 30-day complications). The other generic access gaps remain in V34_Source_PDF_Audit; no unspecified outcomes were invented.

Studies with unresolved conflict/definition records for author clarification: Gu 2019, Huang 2025, Jiang 2026, Liang 2021, Long 2025, Lu 2021, Lu 2022, Pan 2023, Tu 2024, Yu 2020, Zheng 2025, Zhu 2022. Additional requests for exact graph values, missing numerical outcomes and unclear source definitions are listed row by row in V34_Not_Pooled. No author messages were sent.

## Preservation and reproducibility

- Frozen v33 SHA-256: `64ef683c58a1faa2bf408f415d03d96dd6622abf8ded24a72f43db9c47a82a2a`.
- Audit SHA-256: `dd1ee3542121c30fb5de6e520a05fbb2c61e1f9ba9d1d7b8c7477c620b3b879a`.
- v34 SHA-256: `985dc26a943cf30e1bbdac552a5eb69a6fb2d73fd252d0bc194abbdb8538d6f3`.
- Original formulas: 0; named ranges: 0. Exported formula errors: 0. No formula-derived result was replaced with an assumed value.
- AF_Result_Lock and AF_P1_Disposition remain historical adjudications. V33_Outcome_Data_AF_LOCK and V33_Stata_AF_Long preserve original values; corrected active layers and regenerated exports carry v34 changes.
- Native Excel table/filter ranges were expanded to full current extents, including previously truncated master/RoB tables. Existing sheets were retained; summary body merges were removed where they would hide current counts.
- Reproducible Python reconciliation/data-preparation and JavaScript artifact-tool workbook builder are in `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/code`. Python/openpyxl was used for reading and QA, not workbook authoring.
- StataNow 19.5 completed 15 matched/current runs. Log: `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_analysis.log`.
- Rendered previews of summary, QA, Liang corrections, source conflicts and audit dispositions were visually checked.

## Study-level summary

| Study | v33 | v34 | Added | Existing updated | New numeric candidates | New graph | New NR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Zhu 2022 | 12 | 78 | 66 | 6 | 63 | 0 | 0 |
| Yang 2020 | 2 | 29 | 27 | 0 | 14 | 0 | 0 |
| Pan 2023 | 2 | 28 | 26 | 0 | 15 | 0 | 2 |
| Lu 2022 | 6 | 23 | 17 | 0 | 4 | 0 | 0 |
| Li 2021 | 5 | 17 | 12 | 0 | 12 | 0 | 0 |
| Gu 2019 | 8 | 18 | 10 | 4 | 6 | 3 | 0 |
| Huang 2025 | 3 | 15 | 12 | 0 | 5 | 0 | 0 |
| Gao 2021 | 5 | 12 | 7 | 0 | 2 | 0 | 0 |
| Jiang 2026 | 5 | 15 | 10 | 0 | 6 | 0 | 0 |
| Wang 2023 | 5 | 16 | 11 | 0 | 5 | 6 | 0 |
| Tu 2024 | 5 | 15 | 10 | 2 | 5 | 0 | 0 |
| Sun 2017 | 8 | 59 | 51 | 1 | 15 | 21 | 0 |
| Sim 2002 | 4 | 28 | 24 | 1 | 2 | 6 | 8 |
| Lu 2021 | 7 | 31 | 24 | 0 | 14 | 0 | 0 |
| Long 2025 | 7 | 19 | 12 | 3 | 10 | 0 | 0 |
| Wang 2024 | 9 | 21 | 12 | 0 | 7 | 0 | 5 |
| Zheng 2025 | 4 | 30 | 26 | 0 | 20 | 2 | 1 |
| Yu 2020 | 4 | 9 | 5 | 2 | 5 | 0 | 0 |
| Liang 2021 | 8 | 21 | 13 | 6 | 5 | 0 | 0 |

## Outputs

- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v33_to_v34_RECONCILIATION_LOG.csv`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v34_QC_REPORT.md`
- `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v34_ANALYSIS_CHANGE_SUMMARY.md`
