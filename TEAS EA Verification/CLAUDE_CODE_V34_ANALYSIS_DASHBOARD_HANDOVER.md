# Claude Code: continue v34 analyses and update the dashboard

You are continuing the Perioperative TEAS / Electroacupuncture systematic review. Implement the work, validate it, and update the existing dashboard. Do not stop after producing a plan or an audit. Preserve current working-tree changes and the recent dashboard usability improvements.

## Project and authoritative inputs

Repository:
`/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026`

Read these files first, in order, under `TEAS EA Verification/`:

1. `TEAS_EA_v34_QC_REPORT.md`
2. `TEAS_EA_v34_ANALYSIS_CHANGE_SUMMARY.md`
3. `TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx`
4. `TEAS_EA_v33_to_v34_RECONCILIATION_LOG.csv`

Then inspect `TEAS EA Verification/v34_reconciliation/`:

- `code/reconcile.py`, `prepare_analysis.py`, `finalize_stage.py`, `build_workbook.mjs`, `verify_and_report.py`, and `run_stata.do`.
- `data/`: native outcome data, audit dispositions, selected secondary datasets, primary datasets, manifests and not-pooled register.
- `results/v34_model_results.csv` and `results/v34_analysis.log`.

Also inspect the repository instructions, registered protocol/statistical analysis plan, existing analysis scripts, dashboard builders, test setup and deployment configuration. Discover the actual current dependency chain; do not assume that replacing one JSON file updates every dashboard component.

v34 is the current reconciled source master. Frozen v33 and historical A–F locks must remain unchanged. Preserve v34 as the handover baseline; if further source corrections are necessary, create a separately versioned derivative with a correction log. Do not silently edit away conflicts or repair the scientific data in dashboard JavaScript.

## What is completed—and what remains

The v34 reconciliation contains 757 Outcome_Data rows, 70 canonical studies/reports, and dispositions for all 374 supplied audit records. There are 215 new native numeric secondary candidates, 38 newly added graph-only rows, 16 newly added NOT REPORTED rows, and two explicit SOURCE NOT ACCESSED outcome records. Seven studies have supplement/protocol access gaps. The conflict sheet contains 27 conflict/correction records, 24 unresolved.

The reconciliation passed 33 checks. However, it used the supplied PDF audit; it was not a fresh independent extraction of every source PDF. Treat derived readiness classifications and candidate selections as reviewable—not infallible scientific adjudications.

Only the established five secondary datasets and primary models were selectively rerun. Native preparation files exist for the other families, but those files have not all been turned into valid pooled analyses. Your job includes evaluating the entire expanded dataset for additional protocol-supported analyses, not merely copying the existing v34 result CSV to the site.

## Analysis work

1. Map each dashboard result to its source dataset, inclusion rules, statistical script, output and displayed interpretation. Build a before/after analysis manifest identifying what changes and why.
2. Review all relevant v34 native outcome families: postoperative opioid other windows, intraoperative opioids, binary rescue opioid use, rescue frequency, time to rescue, pain, PONV, nausea, vomiting, rescue antiemetics, QoR-15, QoR-40, GI recovery, LOS, functional recovery and adverse events.
3. For every potentially poolable group, check outcome definition, time window, arm comparison, modality, population, unit, statistic, variance, independence and source holds. Apply the existing protocol. Document exclusions and shared-arm selections. Where the protocol does not settle a consequential choice, retain an explicit adjudication hold and continue independent work.
4. Regenerate analysis inputs from the reconciled source data. Use Stata as the authoritative inferential engine, as in the existing project. Re-run every affected valid model and associated forest plots, sensitivity analyses, heterogeneity measures, confidence/prediction intervals and interpretations. Run additional analyses only when supported by the protocol and available independent studies.
5. Preserve TEAS/EA and comparator stratification. Do not pool every row labelled INCLUDE. INCLUDE denotes native numerical extractability, not blanket pooling eligibility. Do not run meta-regression merely because a tab exists; apply protocol requirements for sufficient independent studies.
6. Review the existing estimator, small-k inference, zero-cell handling and prediction-interval rules against the protocol. Document any necessary methodological correction and its impact instead of silently changing the method or carrying forward an error.
7. Export reproducible datasets, do-files, logs, results, plots and a model manifest. Count independent trials separately from contrasts and reports. Trace every selected result to its workbook record ID and source location.

### Required protections and known changes

- Strict primary: exact cumulative systemic postoperative opioid consumption from end of surgery through 24h, using the prespecified IV MME conversions. Expected k=7, N=676; TEAS/sham k=4 and EA/usual-care k=3. The combined historical audit estimate is MD −9.907002 mg IV MME, 95% CI −20.079361 to 0.265357. Preserve the distinction between protocol strata and the combined cross-stratum audit. If a genuinely qualifying new primary result would change k, produce a specific source/variance/unit/window/comparator audit and hold that primary change for adjudication; do not silently promote it.
- Liang 2021 adds intraoperative remifentanil and sufentanil. Randomized counts are 37/38 and analyzed counts 35/35. Its undefined analgesia requirement, ambiguous pain-event rows, PONV-definition issue and 48h CRBD conflict remain visible and appropriately held.
- Gu 2019’s 24h result is graph-only multimodal PCIA solution volume, not printed exact opioid mass. Do not turn it into primary MME.
- Tu 2024 rescue tramadol is 6–24h. Liu 2026 burn rescue is through POD1. Yu 2020 provides exact 0–24h rescue incidence. The old mixed-window k=3 rescue estimate must not survive as an exact 0–24h model; the current exact-window set has k=1 and no pooled estimate.
- Yu POD1 QoR-40 stays separate from exact24h. Pan’s global QoR-40 is separate from its subscales. QoR15 and QoR40 cannot share a raw-MD model.
- Wang 2024 SNVP/MNVP are distinct strata within one trial, not two independent RCTs. Sun, Zhu, Lu 2021 and Sim have shared-arm dependencies. Use protocol-supported arm handling; never count shared participants twice.
- Sim’s mean VAS over 24h is not an exact24h point. Preserve point versus interval versus mean-over-window, POD1 versus exact24h, rest versus movement versus cough, and analysis-population differences.
- Keep opioid dose, binary rescue use, rescue counts, PCA presses, successful deliveries, solution volume and non-opioid rescue distinct.
- Do not estimate graph values, convert medians to means, infer events from rounded percentages, invent SDs, or derive opioid mass from ambiguous proxy endpoints. Preserve ranges separately from quartiles and IQR widths.
- NOT REPORTED and SOURCE NOT ACCESSED must remain distinct. Use available local source PDFs or an available Drive connection if a specific check needs them. Do not claim that an inaccessible source has been verified. Do not send author-contact messages.
- New results have ROB2_RESULT_SPECIFIC_PENDING unless a genuinely matching result-specific assessment is verified. Do not inherit a study-wide judgment. Do not present old GRADE as current for a materially changed synthesis; reassess with the necessary evidence or clearly mark certainty reassessment pending.

## Dashboard implementation

Update the existing dashboard to use verified current analyses and v34 study/outcome data throughout. Preserve and complete the recent navigation improvements.

- Overview: accurate counts, primary estimates, SMD and certainty labels, with clear plain-language interpretation and visible population/window/comparator scope.
- Filters/presets: displayed results must reflect the actual selected analysis. If a card represents a fixed overall model, label that scope clearly. Never let filtered study counts imply an unchanged overall effect is a subgroup estimate. Show an explicit unavailable/not-estimable state when a selection has no supported analysis. Filtering must not silently recompute GRADE.
- Studies: updated explorer, study characteristics, surgical specialties, modality/comparator details, outcome availability and source links. Keep PRISMA counts tied to the actual selection records; added outcome rows are not added RCTs.
- Results: replace outdated estimates/plots and regenerate affected conclusions, including clinical-importance interpretations. Show k, participant N where valid, units, time window, modality/comparator stratum, model and uncertainty. Do not present k=1 as a meta-analysis. Do not leave the withdrawn mixed-window rescue model as current evidence.
- Evidence: result-specific RoB matrix and GRADE/Summary of Findings must distinguish assessed results, pending assessments, outcomes not measured, graph-only results, unavailable sources and conflicts. Verify the Szmit 2021 primary morphine result is correctly matched; it is in the seven-study strict primary set and must not be labelled not measured because of a spelling/key mismatch.
- Limitations/inquiries: show actual unresolved source conflicts, missing supplements, graph-only data and pending assessments, with links to provenance and clear effects on analysis eligibility.
- Methods, glossary and downloads: ensure they render and describe the actual analysis methods. Replace stale downloads and manifests with the current deliverables. Provide clear reasons for unavailable meta-regression or other unsupported analyses; no blank panels.
- Translation: audit all visible UI, tooltips, dynamic result summaries, table headings, empty states and export labels in English and Swedish. Preserve proper bibliographic titles/quotes when appropriate, clearly identified as source text.
- Navigation: main tabs/subtabs must open the intended visible content, with active states and reliable back/forward/deep-link behavior. Audit direct entry and refresh, keyboard navigation, mobile layout, overflow, filter scope and reset behavior.
- Versioning: show the data/analysis version and update date. Ensure caches and generated assets cannot leave an apparently updated page showing v33 results.

## Validation and delivery

Run relevant programmatic tests and browser checks. Compare dashboard values directly with authoritative Stata outputs and manifests. Verify every main tab/subtab, filters/presets, language switch, source links, downloads, plots and empty/held states. Check fresh/incognito loading and direct URLs, not only an already-open browser session. Verify that missing/held data never display as zero or as a previous selection’s result.

Use the existing deployment workflow and target for the dashboard update after successful validation. Preserve unrelated changes; do not create a new hosting destination or change access settings. Verify the deployed version and representative live numbers. If deployment is genuinely unavailable, deliver the fully tested local build and state the exact blocker; do not claim the live dashboard was updated.

Provide a concise final report with:

1. Analyses rerun/newly supported/unchanged/withdrawn, with old versus new k and estimates.
2. Primary k and numerical consistency checks.
3. Newly eligible studies/contrasts by model and shared-arm handling.
4. Remaining source, RoB and GRADE holds.
5. Dashboard sections corrected and browser/test evidence.
6. Exact output paths, commit/build identification and verified deployment URL/status.

Continue autonomously with routine implementation choices. Ask only for consequential scientific adjudication or genuinely missing access that blocks dependent work, while completing all unaffected work.
