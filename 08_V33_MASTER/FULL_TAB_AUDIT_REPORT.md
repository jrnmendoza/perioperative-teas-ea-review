# Dashboard tab audit — 2026-09-08

## Follow-up: filter placement and surgical characteristics

The study toolbar now appears only on Overview, Study Explorer and the RoB matrix. It is hidden on PRISMA, GRADE, Results, Methods, Limitations and More. Its selections are retained when returning to the study views but do not restrict other tabs. Results keep their own outcome/subgroup controls. The regression suite now tests this isolation, rather than the previous cross-tab filtering behavior.

The surgery investigation found that all 70 browser records had defaulted to “Other General Surgery,” with generic procedure descriptions for most earlier studies. `scripts/build_study_characteristics.py` restores 61 descriptions from preserved reconciled extraction documents, two from preserved Chen 2015 source text files, and retains the explicit descriptions/caveats for seven post-lock additions. Wu 2016 lacks a specific procedure in the available characteristics record and is labelled “Not documented.” Eleven display categories now feed the Overview distribution, Study Explorer summary, procedure column, drawer and surgery selector. Every generated record retains its source excerpt and location. The frozen masters and Stata results were not changed; these are descriptive display groupings, not new Stata covariates.

RoB filters now include High, Pending and No Assessment Available. Browser checks exercise three result contexts against all six risk selections, including empty states. Changing the target outcome refreshes the matching matrix and counts. Tests also verify surgery-filtered study rows, restored filter state on return, and absence of hidden surgery filters on Results. CI verifies source excerpts and rejects a mutation collapsing every specialty to the old generic category.

## Follow-up: navigation and RoB correction

The user's Chrome review exposed a gap in the initial audit: populated panel content did not prove correct visible page structure. Two excess closing tags ended the Primary panel early, leaving five large results cards visible on every tab. Later panels were pushed below those cards. The HTML containment is repaired. Navigation now returns to the top, the overview KPI block appears only on Overview, and panel switching no longer fades through a blank view.

`scripts/check_navigation_ui.cjs` clicks the actual navigation controls for all 14 tabs after scrolling to the page bottom. It checks exactly one visible panel, panel position in the viewport, top-of-page reset, and card ownership. Both browser and CI structural guards reject a deliberately escaped-card mutation. GRADE, Limitations, Glossary and Downloads are tested as visible destinations, not merely nonempty DOM nodes.

Meta-regression now begins with an explicit statement that multivariable meta-regression and an interactive prediction tool are unavailable, followed by the existing saved modality analyses. Limitations now begins with an explanation of its clarification roster and hypothetical sensitivity tool.

Szmit 2021's source assessment is present in the v33 workbook, `Corrected_RoB2` row 70: total IV PCA morphine, postoperative 0–24 h, TEAS versus no-current sham. Domains 1–4 are Low, Domain 5 and overall are Some concerns. The browser's missing result-specific mapping is generated from that exact row; no new assessment was invented. All seven strict primary trials now have a mapped result-specific judgment. Other absent mappings no longer claim that the outcome was unmeasured: unavailable assessment and unavailable outcome data are different things. The workbooks remain unchanged.

Scope: all 14 dashboard tabs, their intended content, source-backed displays, navigation, filters, generated tables, plots, calculators, clipboard actions and downloads. This is a dashboard audit against the preserved review records, not a new PDF extraction or scientific adjudication. The frozen v32/v33 workbooks and saved Stata analyses were not edited.

## Tab-by-tab result

| Tab | Intended display and audit result |
|---|---|
| Executive Summary | Review scope, objectives, saved summary and surgical distribution. Distribution count now follows filters; explicit empty state. Saved results are labelled as fixed in the filter scope message. |
| Study Selection / PRISMA | Preserved flow record and copyable summary. Render and copy checked; existing reconciliation caveats remain visible. |
| Search Strategies | Four verbatim executed strategies with source metadata. All four selectors and source-file identity pass. |
| Study Explorer | 70 study records, STRICTA, result-specific RoB context and details. All 70 drawers checked. Corrected duration and RoB reference field mappings, binary denominators and missing-value displays. Search/reset and empty state corrected. |
| Risk of Bias | Study-level and result-specific matrix. Pending assessments are no longer labelled as unreported outcomes. Filtered counts corrected. Added all 26 current secondary result-coverage records without promoting drafts to adjudicated judgments. |
| Secondary & Other Outcomes | Six saved Stata analyses, plus a separately labelled exploratory browser forest. Restored omitted individual study rows; primary selector now uses exactly the locked seven studies (TEAS 4, EA 3). Fixed subgroup header layout, sorting, modality separation and missing-data handling. All saved plot assets load. |
| Clinical Importance | Six paired opioid–pain records with four selectable thresholds. Corrected counts, trial names and copied report to use the same classification. Relative mode now plots percentages against a 30% threshold; axes include every point and numerical ticks. Point estimates do not establish non-inferiority. |
| Primary Opioid | Contribution map, pathway, tiered sets, saved Stata figures and leave-one-out results. Renderer targets and panel order checked. Leave-one-out narrative now follows the displayed rows instead of claiming all intervals cross zero. Influence badge uses the displayed DFBETAS criterion. Failed log requests show an error instead of manufactured output. |
| Meta-Regression | Saved moderator analyses and execution log. Removed simulator remains explicitly withdrawn. Log retrieval checked, including failed-request behavior. |
| Limitations & Inquiries | Preserved 60-inquiry roster, filters and hypothetical sensitivity. Presets now apply their labelled −10/−5/0 mg values to existing primary trials using observed SEs. Simulation cannot alter forest data or CSV exports. Empty selections no longer display a zero effect. |
| Extraction & Conversions | Five methodology panes and research calculator. Invalid/missing doses and quartiles rejected. Median/IQR check preserves reported statistics, consistent with this review's no-conversion rule. Unresolved conversion-factor notes remain explicit. |
| GRADE | Saved established-target assessments and copyable table. Explicitly states that ratings do not transfer to newly added secondary sets awaiting RoB adjudication. |
| Glossary | Statistical definitions and reader assistance. Render, language toggle and explain-statistics switch checked. |
| Export & Downloads | Filtered inspection CSV and actual replication entry points. Removed invented arm sizes/zeros, retained missing fields as blank, included binary fields and outcome/status labels, escaped CSV correctly. Replaced incompatible Stata/R snippets with repository pipeline instructions and R results inspection. |

## Cross-tab corrections

- Browser calculation is DerSimonian–Laird with approximate inference, not the authoritative Stata REML pipeline. The labels now distinguish them.
- The primary browser payload is generated from `opioid_24h_primary.csv`, with locked membership, contrast identifiers, units and numeric values independently checked.
- The other seven browser selectors now also come from the established locked target datasets. This removes broader 48/72-hour records from strict selections and separates composite 24-hour PONV from 48-hour PONV and nausea-only records. Counts are 48h opioid 3, 72h opioid 1, resting pain 2, composite 24h PONV 2, flatus 6, remifentanil mass 7 and strict rescue incidence 4. Single-study results are labelled as such. The newer six supplementary Stata analyses remain separately selectable.
- Global filter scope is stated. “All Studies” clears surgery, search, study exclusions and sample/year restrictions. Outcome-context counts refresh with navigation.
- Current provenance names the v33 master; the v26 path/lock references are identified as historical or stable pipeline paths.
- Missing statistics are not silently replaced by guessed variances, sample sizes or event counts.

## Reproducible verification

- `scripts/check_tabs_ui.cjs`: 14 tabs; 1,080 outcome × modality × subgroup × sort combinations; all 70 drawers; 26 secondary RoB coverage rows; four MCID thresholds; three simulator presets and isolation; CSV download; five conversion panes and all drug options; invalid inputs; GRADE/PRISMA copy; language and reader controls; both log failure states; subgroup geometry.
- `scripts/check_handover_ui.cjs`: reference filters, four exact strategies, primary renderer targets, six saved secondary analyses and their available images.
- `scripts/audit_tabs.cjs`: tab inventory, broken local download links, image loading and JavaScript errors.
- `scripts/check_tab_data.py`: six locked browser-data checks and six isolated mutations rejected. Added to deployment CI.
- Existing checks retained: v33 master QC (26), dashboard validator (60), handover regression (12 plus 12 mutations), deployment integrity, 45-row Stata result synchronization and live deployment verification.
- Browser tests use Chrome through Playwright. Local and deployed runs can be selected with `DASHBOARD_URL`; bundled Playwright can be supplied with `PLAYWRIGHT_MODULE`.

## Remaining review work, distinct from dashboard defects

The dashboard cannot supply missing source extractions, resolve pharmacological conversion factors, or adjudicate draft RoB judgments. Those pending items remain identified. Historical established-target analyses and additional v33 secondary sets have different documented analysis sets; their results and certainty ratings must not be treated as interchangeable. External literature sites and email delivery were not exercised; no outreach was sent.
