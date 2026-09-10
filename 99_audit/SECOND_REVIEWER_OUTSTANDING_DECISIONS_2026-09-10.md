# Second reviewer report

Perioperative TEAS/EA review | Outstanding decisions | 10 September 2026

**Assessment: revisions required before these results are manuscript-ready.** I recommend reporting the nausea and vomiting components, but I do not endorse the existing mixed-modality pooled estimates. The protocol requires separation by modality and comparator. This is the most consequential finding from checking the brief against its sources.

Prepared in the requested second-reviewer role.  Repository examined: `b036a3b`; the supplied brief references `ee5f8f1`. No analysis datasets, frozen workbooks, RoB decisions, or dashboard files were changed.

## Recommended decisions to return

| Item | Second-reviewer recommendation |
| --- | --- |
| 1. Nausea and vomiting | **Option (a), with corrected grouping.** Report all available prespecified component outcomes, including single-study evidence. Prepare outcome- and comparison-specific GRADE assessments; finalize after source issues and result-specific RoB are resolved. |
| 2. Target A-F | **Rename reader-facing labels.** Preserve analysis IDs. Do not downgrade pain at approximately 24 hours to a secondary outcome: it is also a protocol main outcome. |
| 3. Szmit 2021 | **Strict reading for the exact-window analysis.** Preserve the nausea result in a separately labelled uncertain-window/sensitivity presentation. Do not pool Yang and Ma as a supposedly compliant k = 2 replacement. |
| 4. Incomplete label | **Correct it, including the generating Stata code.** Identify all three studies in the historical k = 3 result. Label correction does not validate the pool. |
| 5. v33 upstream | **Option (b).** Preserve v33; integrate an explicit, versioned, repeatable correction stage before validation and output. |
| 6. PRISMA process statements | **Factual confirmation remains necessary.** Use the fill-in text below; disclose actual human/AI roles and independence. Do not close the outstanding process items on this report alone. |

Two additional checks are needed: the zero-cell implementation differs from its stated correction, and Luo 2026 has an apparent discrepancy between its vomiting incidence and severity tables. Both are explained below.

Sources: protocol pp. 6-7; locked scope and amendment; analysis data and code [S1-S4]. The recommendations apply to the six-item brief, not a fresh audit of every included study.

---

## 1. Report component outcomes in the correct strata

**Decision: option (a), with a substantive correction to the proposed implementation.** Nausea and vomiting are within the registered additional outcomes. The word "or" does not establish a prespecified hierarchy allowing the team to suppress available components after seeing their results. Report each distinct outcome and window. A single study prevents meta-analysis, not reporting. Audit the longest reported interval as well; do not manufacture cumulative risks by adding interval counts when participants may recur. [S1, S5]

The current 0-24-hour component pools cross prohibited modality boundaries. The nausea pool also mixes sham and no-stimulation controls. The Stata command filters by endpoint only. Source and extraction checks establish these contributing comparisons:

| Study and window | Actual comparison | Nausea, intervention/control | Vomiting, intervention/control |
| --- | --- | --- | --- |
| Yang 2024, 0-24 h | EA versus usual care | 24/90 versus 40/90 | 12/90 versus 25/90 |
| Ma 2026, 0-24 h | TEAS versus no TEAS | 6/17 versus 8/16 | 6/17 versus 7/16 |
| Szmit 2021, uncertain observation window | TEAS versus sham | 0/24 versus 4/24 | Not established for this analysis |
| Luo 2026, 0-48 h | TEAS versus sham | 24/138 versus 53/139 | 9/138 versus 27/139 |

Ma's relevant randomized comparison is T versus S; its non-randomized Group C is not a substitute control. The source explicitly says Groups C and S received neither TEAS nor sham. [S6-S9]

**Reporting consequence:** retain RR 0.6035 (95% CI 0.3027-1.2030; nausea, k = 3) and RR 0.5755 (0.0248-13.3696; vomiting, k = 2) as historical audit outputs, with an explanation of why they are superseded. Do not present them as protocol-compliant pooled conclusions. Rebuild the eligible inventory by endpoint, window, modality, and comparator before deciding whether any stratum is poolable. Within the named 0-24-hour rows, each distinct stratum contains only one study. [S1, S3-S4]

**Correction to the brief:** the 0-48-hour vomiting estimate is present: RR 0.3357 (95% CI 0.1640-0.6875), Luo alone. Nausea is RR 0.4561 (0.2994-0.6947). I reproduced these approximately using the stored counts and log-RR Wald intervals. These are Table 2-based single-study estimates, not newly fitted meta-analyses; Luo's source discrepancy still needs resolution. [S3, S9]

**GRADE:** prepare separate assessments for each important outcome/window/comparison, including single-study evidence. GRADE requires documented judgments across risk of bias, inconsistency, indirectness, imprecision, and publication bias; it is not simply a computation from k or statistical significance. Final ratings are not assigned in this report. Obtain result-specific assessments rather than copying opioid RoB judgments to nausea. [S1, S10]

---

## 2. Rename outcomes without changing their hierarchy

**Decision: endorse manuscript-facing renaming, with one correction.** The main-outcome section of PROSPERO includes pain at approximately 24 hours, separately at rest and during movement where available. Its repetition under additional outcomes does not remove that main-outcome status. The 14 August amendment explicitly retains two primary outcome domains. [S1-S2]

| Internal label | Reader-facing wording and role |
| --- | --- |
| Target A | Cumulative postoperative opioid consumption, 0-48 h; secondary |
| Target B | Cumulative postoperative opioid consumption, 0-72 h; secondary |
| Target C | Postoperative pain at approximately 24 h, at rest; main outcome domain. Present movement separately. |
| Target D | Postoperative nausea, vomiting, and composite PONV; separate secondary outcomes and windows |
| Target E | Time to first flatus; secondary gastrointestinal recovery outcome |
| Target F | Intraoperative remifentanil consumption; secondary. Need for rescue analgesia; separate secondary outcome. |

Preserve internal IDs and add a mapping for traceability. Use plain outcome names on the dashboard too, retaining "Target" only as an optional identifier. Specify whether rescue treatment was opioid-only or any analgesia; those definitions are not interchangeable.

## 3. Szmit: strict main analysis, transparent sensitivity

**Decision: choose the strict reading.** Table 2 confirms nausea in 0/24 TEAS and 4/24 sham participants. Page 5 establishes that PCA and stimulation ended at 24 hours. Sections 2.6.2 and 2.8 refer to postoperative observation, but do not explicitly define the nausea observation stop-time. Treatment cessation supports an inferred 24-hour window; it does not prove that adverse-event surveillance ended then. Replace the brief's claim of a "demonstrably bounded" observation period with an explicit inference. [S8]

Exclude this result from an exact 0-24-hour set unless better source evidence establishes the endpoint window. Retain it in the review with the reported timing and counts. Present its inclusion under a broader window assumption as a dated sensitivity decision; do not silently reclassify the source wording.

I support the sensitivity check, but its structure must respect modality and comparator. Excluding Szmit leaves Yang (EA/usual care) and Ma (TEAS/no TEAS), which still cannot be pooled together. If the eligible inventory yields no second comparable TEAS/sham study, present Szmit descriptively as a single-study uncertain-window result. A k = 3 versus k = 2 mixed-modality comparison may document historical behavior, but cannot establish robustness of a protocol-compliant synthesis.

This is an outcome-level timing decision, not exclusion of the whole Szmit trial. No new pooled sensitivity estimate was calculated for this report.

---

## 4. Correct the label and its source

**Decision: endorse correction.** The historical nausea k = 3 row should identify Yang 2024, Ma 2026, and Szmit 2021. The error is also present in `05_ponv.do`, line 150. Editing only `results_targetD_ponv.csv` would allow the next run to restore the incomplete label. [S3-S4]

Correct the generating label and its corresponding historical exports in a documented change. Keep numerical values unchanged for that label-only correction. Use distinct versioned outputs for the methodological regrouping recommended in item 1, so the audit distinguishes a metadata correction from a changed analysis. Check agreement across CSV, DTA, JSON, and reader-facing copies where applicable.

## 5. Preserve v33 and integrate the errata

**Decision: option (b).** The frozen v33 source should retain its existing hash. Add an explicit correction stage before the existing errata assertion and before any outputs are written. The assertion currently guards the output-writing block; I inspected this logic but did not rerun the full reconciliation or mutation tests. [S11]

The existing register specifies checks, but its missing-row entry is not a complete reconstruction payload: it omits denominators, intervention/comparator fields, and other required metadata. Reuse the source-verified full row from the existing correction implementation, or extend the register with a complete validated payload. Do not insert a partially populated row merely to satisfy the guard.

The implementation should verify input hashes; identify rows uniquely; distinguish expected old values, already-correct values, and unexpected conflicts; apply each correction once; and record the before/after values and source. A second run must not duplicate the Yang nausea row. Validate the complete result before replacing outputs, and retain the independent downstream checks. Existing one-off correction scripts are supporting material, not evidence that reproducible integration is already complete.

## Additional findings that affect release

**Zero-cell arithmetic:** `05_ponv.do` says it adds 0.5 to all four cells, but increases each arm total by only 0.5. Adding 0.5 to events and non-events increases each total by 1.0. For Szmit, equal denominators leave the corrected RR unchanged, but the variance differs. Correct and verify this before reusing any zero-cell analysis; do not describe it as a label-only change. [S4]

**Luo vomiting source discrepancy:** at 0-2 h, Table 2 reports vomiting in 7/138 and 18/139. Table 3's category-zero counts are 116/138 and 91/139, implying 22 and 48 participants in nonzero severity categories if these describe the same endpoint. Table 3 is titled vomiting severity. Clarify the scale/definition or obtain a correction before treating the vomiting counts as adjudicated. This report does not select one table as correct. [S9]

---

## 6. Complete process statements from actual conduct

**Decision: keep factual verification open.** The protocol describes planned extraction and RoB assessment by at least two people or a person/machine combination. It does not prove what happened. The later handover records a pending adjudication workflow; this report does not satisfy that workflow or convert draft assessments into final ones. [S1, S12]

The following are fill-in drafts, not manuscript-ready assertions. Replace every bracketed field with verified facts. If practice differed between batches, say so rather than imposing a single description.

**PRISMA 8 - selection:** "Each title/abstract was screened by [number and human/AI roles], and each full text by [number and roles]; assessments were [independent or sequential], with disagreements resolved by [actual process]."

**PRISMA 9 - extraction:** "Data from each report were extracted by [number and human/AI roles], using [independent extraction or extraction followed by checking]; discrepancies were resolved by [actual process], and [scope] was checked against source reports."

**PRISMA 11 - RoB:** "Result-specific RoB 2 assessments were prepared by [number and human/AI roles], [independently or sequentially], with disagreements resolved by [actual process]; [scope/status] remains pending."

**PRISMA 23c - limitations:** "Review-process limitations included [verified limitations], which may have affected [specific selection, extraction, or judgment errors]; mitigation consisted of [documented checks], with [remaining gaps] unresolved."

For automation, add the tools/versions, their tasks, and the actual validation or human checking undertaken. Record whether exclusions and critical numerical fields were checked comprehensively or by sampling. A later review of another assessor's answers is checking/adjudication; it should not be retrospectively described as an independent first assessment. [S5]

## Corrections to the brief's methodological framing

PRISMA item 21 concerns assessments of bias from missing results within syntheses. For omission of this review's own outcomes, items 10a, 19, 20b, and 24c provide more direct reporting anchors. Explain changes in outcome selection and analyses, present available study results, and distinguish legacy outputs from the final synthesis. [S5]

I would describe the present issue as incomplete reporting with a risk of selective reporting, rather than infer result-driven intent from the omission alone. Favorable findings neither excuse omission nor establish its cause. Single-study status and the existence of a composite are insufficient reasons to conceal available prespecified component evidence.

**Disposition:** the report resolves the methodological recommendations for items 1-5. Implementation, final GRADE, the Luo clarification, and factual process declarations remain outstanding. These are explicitly identified follow-up actions, not completed work.

---

## Evidence index and verification record

All local paths below are relative to the project root. Source locators identify the evidence used; this was a targeted review rather than a full re-extraction.

**[S1] Protocol.** `00_protocol/source/PROSPERO TEAS EA.pdf`, pp. 6-7: planned extraction/RoB processes, GRADE, outcome hierarchy, and synthesis separation. Relevant pages were text-extracted and visually checked. This is the supplied PROSPERO preview, not verification of the current online registration.

**[S2] Locked scope and amendment.** `00_protocol/protocol_scope_locked.md`, Outcomes and synthesis boundary; `00_protocol/amendments/2026-08-14_primary_outcome_screening_focus.md`, Change and Reason. Both preserve approximately 24-hour pain as a primary/main outcome.

**[S3] Historical results and inputs.** `06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv`, four nausea/vomiting rows; `results_targetD_ponv.csv` in the same folder; `06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.csv`, comparison IDs for Yang, Ma, Szmit, and Luo.

**[S4] Generating code.** `06_FINAL_ANALYSIS_V26/02_STATA/05_ponv.do`, lines 27-41 (zero correction), 65-88 (component pools), and 149-150 (label); `00_prep_data.do` in the same folder, Szmit post-lock addition and inherited RoB comments.

**[S5] Reporting guidance.** [PRISMA 2020 expanded checklist](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf), items 8-11, 19-21, 23c, and 24c. Accessed 10 September 2026.

**[S6] Yang 2024.** `TEAS EA Verification/Source PDFs/covidence_1930_full_article.pdf`, Table 3, PDF p. 4 / journal p. 453. Explicit 0-24-hour component counts were visually checked against the extraction rows.

**[S7] Ma 2026.** `TEAS EA Verification/Source PDFs/117210.pdf`, p. 3 (randomized T/S comparison), p. 4 (no TEAS or sham in S/C and 24-hour endpoint), p. 8, Table 3 (counts). Pages 4 and 8 visually checked. Comparator resolution also recorded in `09_V34_ANALYSIS/v34_comparator_resolution.csv`.

**[S8] Szmit 2021.** `szmit_2021.pdf`, pp. 5-7 and 9; cessation of treatment, outcome/adverse-event methods, Table 2, and follow-up text visually checked. Reported counts verified; exact nausea observation stop-time remains uncertain.

**[S9] Luo 2026.** `TEAS EA Verification/Source PDFs/covidence_35_verified.pdf`, p. 5, Tables 2-3 visually checked. Table 2-based 48-hour RR calculations reproduced; the apparent cross-table vomiting discrepancy remains unresolved.

**[S10] Certainty guidance.** [Cochrane Handbook, Chapter 14](https://training.cochrane.org/handbook/current/chapter-14), GRADE and Summary of Findings guidance. Accessed 10 September 2026. No final certainty judgments were issued.

**[S11] Reconciliation safeguards.** Under `TEAS EA Verification/v34_reconciliation/`: `code/reconcile.py`, lines 435-482; `data/post_lock_errata.json`; `POST_LOCK_ERRATA_v34.md`; and existing `code/apply_post_lock_errata.py` / `code/apply_errata_to_csv.py`. Inspected without execution or mutation.

**[S12] Current process evidence.** `HANDOVER_TO_CODEX_ROB2.md`, draft-status and adjudication sections; `TEAS EA Verification/v34_reconciliation/data/v34_outcome_data.csv`, relevant component rows with result-specific RoB pending. Neither document establishes completed independent human assessments.

**Verification limit:** the historical component estimates and named rows were checked; no pooled analyses, full pipeline checks, registry updates, or complete risk-of-bias assessments were performed. The source brief and production artifacts remain unchanged.
