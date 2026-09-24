# Unresolved decisions requiring reviewer action (v36, 16 September 2026)

Each item says what is unresolved, the conservative rule currently applied (so analyses run without inventing a resolution), and what evidence or decision would close it. **Blocks lock** means data lock must not be declared until it is closed.

## A. Blocks data lock

| # | Decision | Current conservative handling | Needed to close |
|---|---|---|---|
| A1 | **Evidence-base completeness.** 122 full texts were excluded as "wrong outcomes" (108 on the registration date), although registered eligibility admits any eligible outcome. Triage flags 84 for priority re-screening. | Current 70-report base used as-is; GRADE notes a review-level selection problem, not publication bias | Dual independent re-screen of `02_DECISIONS/exclusion_rescreen_triage.csv` (84 priority + 29 secondary) against the 20 Aug 2026 criteria; extract any new trials; rerun the full chain |
| A2 | **PRISMA record-level provenance.** Six registry reports are "excluded" in Covidence (Gao 2022, Liu 2015, Zhang 2018, Oztas 2019, Song 2020, Szmit 2021); Wu 2016 has no Covidence record; PRISMA reasons do not match Covidence (language 0 vs 12; not retrieved 14 vs 2) | Registry retained; crosswalk documents the discrepancy | Dated reviewer decision for each re-inclusion (update Covidence or document outside it); confirm Wu 2016 as the citation-search addition; rebuild the PRISMA figure from records |
| A3 | **Registration identifier.** Supplied PDF shows no identifier of its own; CRD420251090635 is a similar broader review | No identifier assigned. The dashboard still displays CRD420251090635 (19 `_site` files), which is stale. | External confirmation from PROSPERO of this record's CRD number |
| A4 | **Human sign-off of GRADE.** All 38 rows are ASTRA recommendations | Labelled as recommendations | Reviewer approval or revision, with names and dates. Explicitly revisit: `bowelsounds_TEAS_sham` downgraded Low→Very low in v36 (Zheng 2025 contradiction); `nausea48_TEAS_sham` has an exact High RoB assessment but only a serious downgrade |
| A5 | **RoB 2 coverage and sign-off.** 97 of 761 results have exact assessments; many members of non-sensitivity bodies are UNLINKED (e.g., all 5 vomiting24_TEAS_sham contrasts, all bowel-sound/defecation TEAS contrasts, Szmit usual-care opioid). No linked record carries a sign-off date. | Unlinked shown as UNLINKED, never imputed | Result-specific RoB 2 for unlinked members of non-sensitivity bodies; record assessor/date for existing ones |
| A6 | **Dashboard.** `dashboard/` and `_site/` still present the superseded k=4 TEAS/sham (−13.99), the k=7 combined TEAS+EA (−9.91) and the old registration ID | Not rebuilt; provisional banner deployed 17 Sep 2026 (`dcd8f23`) | Rebuild from `06_REPORTS/model_analysis_manifest.csv` only after A1–A5; semantic claim audit |

## B. Source contradictions (disposition applied; external clarification outstanding)

| # | Item | Current handling | Needed |
|---|---|---|---|
| B1 | **Chen 2020:** printed 48-h sufentanil totals (118.5/140.2 µg) are below the stated basal infusion (144 µg) | Sensitivity only, printed values unchanged, with/without Chen, factors 0.25/0.5/1 | Author query (pump interruption, concentration, demand-only mode) |
| B2 | **He 2026 hepatectomy:** author MME (eTable 1, `sm8843`) has an unknown IV/oral basis | Unit-assumption sensitivity only | Author query on conversion formula and denominator |
| B3 | **El-Rakshy 2009:** arm labels and denominators conflict across flow, baseline and abstract | Table 2 values retained, High RoB, leave-out diagnostic | Author query or reviewer decision to demote to sensitivity |
| B4 | **Zheng 2025 (new in v36):** printed mean (SD) for flatus, borborygmus and remifentanil gives z ≈ 9.6, 12.8 and 7.7 (P far below 10⁻¹⁰), but P=0.003/0.035/0.031 is printed; reading them as SEs does not reproduce the P values either | Printed values retained; three leave-out diagnostics added. Bowel sounds loses significance without Zheng (k=2). Membership not changed on P values. | Author query; reviewer decision on whether to hold Zheng's continuous outcomes |
| B5 | **He 2026 breast:** repeated identical tiny pain SDs conflict with threshold counts | Diagnostic only | Author query |
| B6 | **Yeh 2010/2011:** probable same cohort; route and schedule differ | One unit, counted once, excluded from models | Send drafted author query |
| B7 | **Jin 2023:** general anaesthesia not established; PCIA volume without concentration | HOLD | Source check / author query |
| B8 | **Long 2025:** "needle OR patch" wording prevents a modality decision | HOLD | Author query |

## C. v36 corrections that need reviewer confirmation

Each correction follows existing documented rules and is quoted from source, but it changes evidence-body membership and needs a reviewer's confirmation.

| # | Correction | Source basis | Impact |
|---|---|---|---|
| C1 | Pan 2023 → TEAS/usual care (vomiting 24 h; intraop remifentanil) | "Patients in Group C did not undergo TEAS." No sham described, although the paper calls itself double-blind. | vomiting24_TEAS_sham k 5→4, RR 0.643 (0.396–1.044) → 0.680 (0.345–1.342); new vomiting24_TEAS_usual k=1 |
| C2 | Liang 2021 → TEAS/usual care (intraop remifentanil); removed from sham PONV point-window sensitivity | "in control group, the patients received no stimulation." No electrode placement described. | intraop_remifentanil_TEAS_sham k 8→6, −94.4 (−174.1 to −14.8) → −114.8 (−199.7 to −29.9); new intraop_remifentanil_TEAS_usual k=2 |
| C3 | Xiong 2021 → TEAS/sham (PONV 48 h) | "gel electrodes applied and connected to an acupuncture instrument without stimulation" | ponv48_TEAS_usual renamed ponv48_TEAS_sham; estimate unchanged. Existing RoB record describes the comparison as "antiemetics alone", so reviewer should confirm D2. |
| C4 | Registry comparator labels for Pan, Liang, Huang 2025, Liu 2021, Xiong, Zhou 2025, Song 2020 | Quotes in `studies.json` → `comparator_source_status` | Descriptive only; 63 other study-level labels remain LEGACY (result-level class governs) |
| C5 | Three RoB links added (Pan and Liang remifentanil; Song 24-h pain) | Identical study/outcome/window/denominators/arm statistics; only the ID scheme differs. v26 labelled Song pain "rest", but the source does not specify a setting. | 94 → 97 exact links |
| C6 | Huang 2017 EA → TEAS (user's edit, uncommitted at the start of v36; retained and committed as `dbb15df`) | Title "transcutaneous electrical acupoint stimulation", surface electrodes, HANS-200A, "non-invasive" | Fixes HEAD registry/results inconsistency; Huang 2017 contributes to no model |

## D. Standing policy choices (documented; approval not recorded)

Sufentanil central factor 0.5 mg IV morphine/µg with 0.25 and 1.0 sensitivities; Song 2020 non-acupoint active stimulation classified active control rather than sham (broad-sham sensitivity provided); flatus effect measure hours MD with SMD diagnostic (post hoc 12 Sep change); El-Rakshy retained in the supportive body; Chen 1998, Yang 2024 and Lin 2002 limited to sensitivity because rescue is unquantified. Every analysis decision in this adjudication was made after results were known and must be disclosed as such; none may be described as prospective.
