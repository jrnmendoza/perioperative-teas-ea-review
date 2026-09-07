# Dashboard ↔ v26 Reconciliation Audit

**Review:** Perioperative TEAS and EA for postoperative opioid sparing
**PROSPERO:** CRD420251090635
**Authoritative data:** `TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx`
**Authoritative statistics:** `06_FINAL_ANALYSIS_V26/` — StataNow 19.5 SE
**Branch:** `claude-v26-dashboard-final`
**Date:** 2026-09-07

---

## 0. Scope and method

The live dashboard mixed v26 data with pre-v26 analysis outputs. This audit
replaces every non-reproducible claim rather than restating it, per the standing
instruction to optimise for scientific correctness and traceability rather than
for preserving previously displayed numbers.

Method:

1. Determined what GitHub Pages actually serves (§1).
2. Re-ran the full v26 Stata pipeline and confirmed byte-identical outputs, so
   the pooled results used below are demonstrably reproducible (§2).
3. Audited each dashboard claim against `AF_Result_Lock`, the locked analysis
   datasets in `01_DATA/`, and the result tables in `03_RESULTS/`.
4. Replaced the presence-only validator with an adversarial one (§13) and drove
   the dashboard in a browser across all tabs and both locales (§14).

**One finding is unresolved and is recorded as such** (Issue 15). Everything
else is closed.

---

## 1. Deployment pipeline

| Field | Value |
| --- | --- |
| **ISSUE** | It was not established which of `dashboard/`, `docs/`, or `gh-pages` is live; all three were being edited. |
| **OLD STATE** | Four byte-identical copies (`dashboard/`, `docs/`, `gh-pages` root, and nested `gh-pages:docs/` + `gh-pages:dashboard/`). No `.github/workflows`. Identical content made the drift invisible. |
| **V26 CORRECT STATE** | GitHub Pages serves the **root of the `gh-pages` branch**. Proven by live probing: `/06_FINAL_ANALYSIS_V26/00_README.md` → 200 (exists only at `gh-pages` root), `/docs/index.html` → 200 (a nested copy), `/README.md` → 404 (`gh-pages` root has none, `main` root does). |
| **ACTION TAKEN** | Declared `dashboard/` the single source of truth, `docs/` a generated mirror, `gh-pages` the deployment target. Added `scripts/sync_dashboard.sh`. |
| **FILE(S) CHANGED** | `06_FINAL_ANALYSIS_V26/06_AUDIT/deployment_pipeline.md` (new), `scripts/sync_dashboard.sh` (new) |
| **VERIFICATION** | Validator enforces `dashboard/` ≡ `docs/` byte parity. |
| **STATUS** | **RESOLVED** |

---

## 2. Reproducibility of the v26 statistics

| Field | Value |
| --- | --- |
| **ISSUE** | The dashboard asserted "StataNow 19.5 SE verified" without evidence on `main` that the pipeline reproduces. Execution logs existed only on `gh-pages`. |
| **OLD STATE** | `06_FINAL_ANALYSIS_V26/02_STATA/logs/` absent from `main` (gitignored by `*.log`), though the dashboard linked to files in it. |
| **V26 CORRECT STATE** | The pipeline reproduces exactly. |
| **ACTION TAKEN** | Ran `/Users/ryan/bin/stata-se -b do 06_FINAL_ANALYSIS_V26/02_STATA/00_master.do` from the locked workbook. All **17 pipeline-written CSVs** (8 locked analysis datasets + 9 result tables) are **byte-identical** to the committed outputs. Note that `master_reconciled_results_v26.csv` is an aggregate that no do-file writes; it was unchanged by the run rather than regenerated, and the two new broader-sensitivity rows were appended to it explicitly (see §22). Regenerated `.dta`/`.png` differ only by embedded run timestamps and were restored to HEAD. Un-ignored and committed the 11 execution logs. |
| **FILE(S) CHANGED** | `.gitignore`, `06_FINAL_ANALYSIS_V26/02_STATA/logs/*.log` (11 new) |
| **VERIFICATION** | `diff` of every CSV in `01_DATA/` and `03_RESULTS/` against a pre-run snapshot: identical. |
| **STATUS** | **RESOLVED** |

---

## 3. Primary 24-h opioid analysis

| Field | Value |
| --- | --- |
| **ISSUE** | Headline primary analysis had to be confirmed against the final Stata run, not the historical k=11 / N=945 / MD ≈ −5.04 mg values. |
| **OLD STATE** | Prior releases displayed k=11, N=945, MD ≈ −5.04 mg. Subnav and KPI had already been moved to k=6 by an earlier pass, but downstream text had not. |
| **V26 CORRECT STATE** | `OP24_PRIM_COMB`: **k=6, N=628, MD = −4.6839 mg IV MME, 95% KH CI [−12.2566, +2.8888], p = 0.17271, τ² = 31.4862, I² = 98.29%**, REML + Hartung-Knapp. Study set: Chen 1998, Chen 2020, He 2026 (hepatectomy/JIS), El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024. Modality strata: TEAS k=3 (−6.70, p=0.381), EA k=3 (−3.94, p=0.397). SMD Hedges g = −0.89. |
| **ACTION TAKEN** | Confirmed every displayed statistic against `03_RESULTS`. Corrected residual "k = 11" / "11 trials" text in the forest-plot hub and the derivations section. |
| **FILE(S) CHANGED** | `dashboard/index.html` |
| **VERIFICATION** | Validator recomputes k and N from `01_DATA/opioid_24h_primary.csv` and requires MD, both CI bounds, p and I² to appear in the HTML. |
| **STATUS** | **RESOLVED** |

---

## 4. Target A — 0–48 h cumulative opioid

| Field | Value |
| --- | --- |
| **ISSUE** | A five-study 48-h result including He 2026 (breast/WJCO) and Wong 2006 was still being served. |
| **OLD STATE** | `stata_48h_opioid_synthesis_data.csv` held Chen 2020, **He 2026**, Zhang 2023, An 2014, **Wong 2006**, and was offered as an active download. Narrative reported N = 2,077. |
| **V26 CORRECT STATE** | `TA_STRICT`: **k=3, N=1,999** (Chen 2020 40/40, Zhang 2023 922/916, An 2014 41/40), MD = −2.8084 [−5.9857, +0.3688], p = 0.0627, I² = 49.79%. Xie 2014 is **sensitivity/broader only** (`TA_INCL_XIE`, k=4). He 2026 (breast/WJCO) and Wong 2006 are `EXCLUDE` rows A-005 and A-006 in `AF_Result_Lock`. Mandatory sensitivity excluding An 2014 (`TA_EXCL_AN`, k=2) present. |
| **ACTION TAKEN** | Archived the five-study dataset and its do-file/log; repointed downloads to `02_targetA_48h.do` / `target_A_48h.csv` / `logs/02_targetA_48h.log`. Corrected N 2,077 → 1,999 in both locales. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/translations.js`, `99_audit/superseded_dashboard_artifacts/` |
| **VERIFICATION** | Validator asserts strict membership, Xie-2014-sensitivity-only, and that neither the retired dataset nor its links survive. |
| **STATUS** | **RESOLVED** |

---

## 5. Target B — 0–72 h cumulative opioid

| Field | Value |
| --- | --- |
| **ISSUE** | Risk of a forced 72-h meta-analysis and of misclassifying Zhang 2025 / Xie 2014 as 72 h. |
| **OLD STATE** | `stata_72h_opioid_synthesis_data.csv` predated the not-pooled decision. |
| **V26 CORRECT STATE** | `TB_STRICT_EXACT`: **Yang 2024 alone, k=1, N=180, MD = −0.50 mg [−4.078, +3.078], p = 0.784 — NOT POOLED**. Wong 2006 is the approximate "first three postoperative days" sensitivity case (`TB_BROADER_SENS`, k=2). Zhang 2025 (POD1) and Xie 2014 (48 h) are `EXCLUDE` rows B-003 and B-004. |
| **ACTION TAKEN** | Confirmed the dashboard states NOT POOLED; archived the superseded 72-h artifacts. |
| **FILE(S) CHANGED** | `99_audit/superseded_dashboard_artifacts/` |
| **VERIFICATION** | Validator asserts k=1, model contains "Not pooled", "NOT POOLED" appears in the HTML, and Zhang 2025 / Xie 2014 appear nowhere in the Target B dataset. |
| **STATUS** | **RESOLVED** |

---

## 6. Target C — pain at rest ~24 h

| Field | Value |
| --- | --- |
| **ISSUE** | Generic/movement/cough/unspecified POD1 pain must not enter the rest-pain analysis. |
| **OLD STATE** | A single broad pain pool (`stata_forest_pain.png`, `stata_secondary_synthesis_data.csv`). |
| **V26 CORRECT STATE** | `TC_REST_PAIN24`: **k=2, N=158** (Xing 2022 29/29, Liu 2021 50/50), MD = −0.1765 VAS [−0.6828, +0.3298], p = 0.14135, I² = 0.0%. Both results are explicitly "at rest"; both carry **High** result-specific RoB. Seven other candidates are `EXCLUDE` rows C-003…C-009. |
| **ACTION TAKEN** | Confirmed against `AF_Result_Lock`; archived the broad pain pool. |
| **FILE(S) CHANGED** | `99_audit/superseded_dashboard_artifacts/` |
| **VERIFICATION** | Validator inspects every Target C row for the token "rest" and rejects "movement", "cough", "ambulation", "activity". |
| **STATUS** | **RESOLVED** |

---

## 7. Target D — PONV stratification

| Field | Value |
| --- | --- |
| **ISSUE** | One broad PONV pool would conflate nausea-only with vomiting-only, and 24 h with 48 h. |
| **OLD STATE** | A single `stata_forest_ponv.png` pool. The RoB selector exposed only `ponv_24h`, `ponv_48h`, `nausea_24h`, `vomiting_24h` — the 0–48 h nausea and vomiting strata existed in `data.js` (Luo 2026) but were unreachable in the UI. |
| **V26 CORRECT STATE** | Six discrete strata: composite PONV 0–24 h (`TD_PONV_0_24H`, k=2, N=463, RR 0.5604); composite PONV 0–48 h (`TD_PONV_0_48H`, k=2, N=120, RR 0.5234); nausea 0–24 h (k=2, RR 0.6205); nausea 0–48 h (Luo 2026 alone, k=1, RR 0.4561, not pooled); vomiting 0–24 h (k=2, RR 0.5755); vomiting 0–48 h (Luo 2026 alone, k=1, RR 0.3357, not pooled). |
| **ACTION TAKEN** | Added the missing `nausea_48h` and `vomiting_48h` options to the RoB/outcome selector. |
| **FILE(S) CHANGED** | `dashboard/index.html` |
| **VERIFICATION** | Validator requires all six strata in `target_D_ponv.csv`, requires all six as selector options, and fails if any pooled analysis labelled "composite" draws on a nausea-only or vomiting-only record. Browser check confirmed the matrix returns 2/1/2/1 assessed studies for the four nausea/vomiting strata respectively. |
| **STATUS** | **RESOLVED** |

---

## 8. Target E — time to first flatus, and the Yu Wang exclusion

| Field | Value |
| --- | --- |
| **ISSUE** | Yu Wang et al., *JAMA Surgery* 2023 (DOI 10.1001/jamasurg.2022.5674) must not be added; it is excluded at full text for wrong outcomes and must not be confused with Jun Wang et al., *Pain Therapy* 2023. |
| **OLD STATE** | No incorrect inclusion, but the dashboard's PICOS wording implied any trial reporting flatus was eligible — which contradicts the exclusion (see Issue 9). |
| **V26 CORRECT STATE** | `TE_FLATUS_MD_REML_KH`: **k=6, N=596** (Zhou 2025, Yang 2020, Yang 2024, Xing 2022, Lu 2022, Ng 2013), MD = −2.0039 h [−3.1419, −0.8659], p = 0.00624, I² = 0.0%. `AF_Result_Lock` E-005 (Wang 2023) is `EXCLUDE — wrong outcomes`. Sensitivities: excluding Ng 2013 (originally reported in days) and excluding High-RoB. |
| **ACTION TAKEN** | Confirmed E-005 is absent from the analysis dataset; stated the exclusion explicitly in the PICOS table with the DOI. |
| **FILE(S) CHANGED** | `dashboard/index.html` |
| **VERIFICATION** | Validator checks `AF_Result_Lock` E-005 status is EXCLUDE, that E-005 is absent from `target_E_flatus.csv`, that no pooled analysis stratum names Yu Wang, and that the DOI appears in the dashboard. |
| **STATUS** | **RESOLVED** |

---

## 9. Eligibility / PRISMA wording

| Field | Value |
| --- | --- |
| **ISSUE** | PICOS implied that reporting a secondary outcome alone conferred eligibility, contradicting the Yu Wang exclusion. |
| **OLD STATE** | The Outcomes row listed pain, PONV, rescue analgesia, flatus, QoR-40/15 and PCA demands together with no distinction; the exclusion read "Studies reporting no quantifiable postoperative outcome within 0–72 hours". A trial reporting flatus alone therefore appeared eligible. |
| **V26 CORRECT STATE** | Eligibility is conferred by a perioperative **analgesic** outcome (0–24/48/72 h opioid consumption, postoperative pain intensity, rescue analgesia, or intraoperative opioid requirement). PONV, GI recovery, QoR, PCA demands, length of stay and sleep quality are extracted from otherwise-eligible trials and do **not** confer eligibility. |
| **ACTION TAKEN** | Split the PICOS Outcomes row accordingly, rewrote the exclusion, and named the Yu Wang decision inline as the worked example. **No inclusion decision was changed.** |
| **FILE(S) CHANGED** | `dashboard/index.html` |
| **VERIFICATION** | Read back in the browser; the DOI-level exclusion statement is present. |
| **STATUS** | **RESOLVED** |

---

## 10. Target F — estimand separation

| Field | Value |
| --- | --- |
| **ISSUE** | No single "opioid-related" pool; PCA presses must never be pooled with opioid dose, rescue incidence with rescue count, non-opioid with opioid rescue, or fixed with titrated intraoperative exposure. |
| **OLD STATE** | Separation was already correct in the v26 Stata layer. |
| **V26 CORRECT STATE** | Seven `AF_Result_Lock` strata kept apart: `F_intraop_titrated_requirement`, `F_intraop_fixed_or_unclear_exposure`, `F_postop_delivered_dose_or_solution`, `F_PCA_behavior`, `F_rescue_opioid`, `F_rescue_nonopioid`, `F_rescue_mixed_or_undefined`. Pooled analyses: titrated remifentanil (k=7, MD −114.21 µg); delivered morphine (k=2); strict binary rescue (k=4, RR 0.5047); all binary rescue (k=5); PCA demands reported as **SMD only** (k=8, g = −1.2686), never as a dose. |
| **ACTION TAKEN** | Verified; no change required. Added machine checks so it cannot regress. |
| **FILE(S) CHANGED** | `scripts/validate_dashboard.py` |
| **VERIFICATION** | Validator requires all seven strata and fails if any Target F analysis mixes titrated with fixed exposure, reports a PCA outcome in mg/µg/MME, or merges rescue incidence with rescue counts. |
| **STATUS** | **RESOLVED** |

---

## 11. Result-specific RoB 2

| Field | Value |
| --- | --- |
| **ISSUE** | RoB 2 must be a property of a *result*, not a study. The Study Explorer must not label a study "Low RoB" when the selected result differs, and Pending/absent must not render as High. |
| **OLD STATE** | The RoB matrix was result-specific, but every other consumer read the single study-level `s.rob2.*`: the Study Explorer badge, the study drawer header, the RoB filter, the meta-lab RoB subgrouping, and the CSV export. The drawer additionally collapsed **High** into the same amber badge as **Some concerns**. The CSV exported per-outcome effect data beside a study-level RoB column. |
| **V26 CORRECT STATE** | `AF_Result_Lock` governs; judgments are keyed by study × result × window. **15 result-specific judgments differ from their study-level label**, e.g. Chen 2020 study-level *Some concerns* → PCA behaviour **High**; Yang 2024 study-level *Some concerns* → flatus **High**; Xing 2022 study-level *High* → flatus **Some concerns**. |
| **ACTION TAKEN** | Added a single shared resolver `resultRob(study, outcomeKey)` plus `robState()`. Every consumer now routes through it. Study Explorer gained a result-context selector (default: primary 24-h) with an "n/63 assessed" caption. Drawer header badge is result-specific and the study-level block is relabelled as such. CSV export now emits `exported_outcome`, `rob2_result_specific` and `rob2_study_level_overview` as separate columns. Five states render distinctly: Low / Some concerns / High / Pending / Not assessed. |
| **FILE(S) CHANGED** | `dashboard/app.js`, `dashboard/index.html` |
| **VERIFICATION** | Direct test over 63 studies × 16 result keys: **zero** absent or pending judgments render as High. `robState()` maps `null`, `undefined`, `""`, `"NR"`, `"Not Reported"`, `"unmeasured"`, em-dash, unrecognised strings, `0` and objects to `not-assessed`. Browser: switching the Explorer context from study-level to PCA behaviour to flatus changes the column, showing exactly the divergences above. Validator parses `robState()` and fails if its default branch can return `'high'`. |
| **STATUS** | **RESOLVED** |

---

## 12. Methods / metadata / outcome hierarchy

| Field | Value |
| --- | --- |
| **ISSUE** | Obsolete PROSPERO ID; outcome hierarchy must not imply 24 h and 48 h are co-primary. |
| **OLD STATE** | `CRD42024560773` had already been removed from the dashboard by an earlier pass; it survives only in audit documents as a recorded correction. Hierarchy labels were already correct. |
| **V26 CORRECT STATE** | **CRD420251090635**. 24 h = PRIMARY, 48 h = KEY SECONDARY, 72 h = EXPLORATORY. No "Primary Analgesic Domain (Dual Timepoints)" or co-primary phrasing anywhere. |
| **ACTION TAKEN** | Verified; added machine checks. The PROSPERO absence check deliberately exempts `06_AUDIT/*.md`, since an audit trail must be able to name the superseded ID as a corrected OLD STATE. |
| **FILE(S) CHANGED** | `scripts/validate_dashboard.py` |
| **VERIFICATION** | Validator scans all HTML/JS/JSON/CSV under `dashboard/` and `docs/` for the obsolete ID and for co-primary phrasing. |
| **STATUS** | **RESOLVED** |

---

## 13. GRADE

| Field | Value |
| --- | --- |
| **ISSUE** | GRADE must follow the final v26 set, final Stata result and result-specific RoB; stale ratings must not be retained. |
| **OLD STATE** | The GRADE SoF table had already been recomputed on v26 (12 outcomes), **but the overview KPI card contradicted it**: it showed "⊕⊕⊕◯ Moderate — downgraded 1 level for high heterogeneity (I² = 99.7%)" and "7 Outcomes Synthesized", while the SoF table rated the combined primary **Low**, downgraded 2 levels (I² = 98.3%). Both were on screen at once. |
| **V26 CORRECT STATE** | Primary 24-h combined = **Low** (⊕⊕◯◯), downgraded 2 levels for inconsistency (I² = 98.3%, τ² = 31.49) and imprecision (95% KH CI crosses zero; PI −22.28 to +12.91 mg). 12 outcomes in the SoF table: TEAS Low, EA Very Low, combined Low, SMD Low, Target A Moderate, Target B Very Low, Target C Low, PONV 0–24 h Low, PONV 0–48 h Low, flatus Moderate, intraoperative remifentanil Moderate, rescue opioid Moderate. |
| **ACTION TAKEN** | Corrected the KPI card and both locale strings. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/translations.js` |
| **VERIFICATION** | Validator parses the SoF object, rejects any rating outside {High, Moderate, Low, Very Low, Pending}, and fails if the KPI card disagrees with the `PRIMARY COMBINED` row. |
| **STATUS** | **RESOLVED** |

---

## 14. Meta-regression and subgroups

| Field | Value |
| --- | --- |
| **ISSUE** | The dashboard presented an inferential meta-regression apparatus that the v26 pipeline does not reproduce, including a multivariable model, and used k=11. |
| **OLD STATE** | Univariable baseline opioid demand (β = −0.170, p = 0.0186, R² = 49.08%); publication year (β = +0.471, p = 0.0287, R² = 82.81%); sex composition (β = −0.013, p = 0.8746); multivariable **MD = 0.0204 − 0.1876 × BaselineDemand + 1.4895 × EA**; five interactive bubble plots; a slider-driven effect predictor returning a point estimate and CI. Moderator matrix headed "k = 11 Primary RCTs"; bubble buttons "TEAS Stratum (k=8)" / "EA Stratum (k=3)". |
| **V26 CORRECT STATE** | `09_subgroups_metareg.do` fits **exactly one** meta-regression: modality, k=6, β = −1.7938 mg [−20.9161, +17.3285], **p = 0.80737**, logged verbatim as *"severely underpowered ... extreme risk of false-positive / false-negative conclusions"*. Authoritative presentation is the stratified subgroup pair (TEAS k=3, EA k=3) with Hartung-Knapp. Egger-type testing is not performed (k < 10). |
| **WHY WITHDRAWN** | The 11-trial pool is not the v26 primary set. It mixed conditional, proxy-endpoint and excluded records (Sim 2002, Coura 2011, both Chen 2015 reports, Zhang 2025), and **counted the overlapping Yeh 2010 / Yeh 2011 lumbar-spine reports as two independent trials**, which the v26 lock forbids. Its stated EA stratum (Sim 2002, Coura 2011, El-Rakshy 2009) is not the v26 EA stratum (El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024). The predictor's interval was produced by an approximation rather than the model covariance matrix. |
| **ACTION TAKEN** | Removed the bubble-plot studio (replaced by the authoritative modality subgroup forest plot plus a withdrawal notice naming each removed model), removed the interactive predictor outright, set all moderator-matrix coefficients to "Not estimated" with the reason, corrected k=11/11 → k=6/6 and TEAS (k=8) → TEAS (k=3), and repointed the Stata console to `logs/09_subgroups_metareg.log`. Fixed the same numbers in `translations.js` (EN + SV), which would otherwise have re-injected "k = 11 Primary RCTs" through `data-i18n` at runtime. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/app.js`, `dashboard/translations.js` |
| **VERIFICATION** | Validator fails on any live occurrence of k=11, N=945, or the withdrawn coefficients outside explicitly-labelled withdrawal prose; requires exactly one meta-regression in `master_reconciled_results_v26.csv`; fails if any bubble-plot asset is still served; and fails if an Egger-type test is reported with a p-value while k < 10. |
| **STATUS** | **RESOLVED** |

---

## 15. Clinical Importance (MCID) paired cohort

| Field | Value |
| --- | --- |
| **ISSUE** | The paired opioid + pain cohort had to be the v26 set, and must not count Yeh 2010 and Yeh 2011 independently. |
| **OLD STATE** | `data.js` already carried the correct k=6 cohort, so runtime counts were right — but the **static prose beneath contradicted it**: 3/5/3 trials at 27.3%/45.5%/27.3% (i.e. k=11), naming Coura 2011, Ntritsou 2014, Sim 2002, Wong 2006, Zhou 2021, Zhang 2025 and **both "Yeh 2010" and "Yeh 2010 ATHM"**. The section header said k=6 while the prose said 11. The downloadable `paired_mcid_dataset.csv` was the k=11 file, listing Wong 2006 at "24 h" (its v26 result is a first-3-days total) and Zhou 2021 as a continuous 24-h MD (its v26 record is binary "any opioid use", window undefined). |
| **V26 CORRECT STATE** | k=6, N=628 analysed: Chen 1998 (−21.0 mg, −0.80 VAS), Seevaunnamtum 2016 (−12.56, −0.03), Chen 2020 (−2.82, −0.65), El-Rakshy 2009 (−1.60, −0.40), He 2026 (−0.60, −0.20), Yang 2024 (−0.30, −0.15). At the ≥10 mg threshold: Q1 = 2 (33.3%), Q2 = 0, Q3 = 4 (66.7%), Q4 = 0. All six pain point estimates fall on the pain-reduction side. |
| **ACTION TAKEN** | Rewrote each quadrant description to name the actual v26 trials and to state plainly that Q2 is empty. Regenerated `paired_mcid_dataset.csv`/`.json` (and the served `results/` copies) from the v26 cohort with result-specific RoB and a provenance block. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/paired_mcid_dataset.{csv,json}`, `dashboard/results/paired_mcid_dataset.{csv,json}` |
| **VERIFICATION** | Validator requires the downloadable cohort to equal the rendered cohort and the paired N to equal the Stata primary N (628 = 628). Browser confirms 2/0/4/0. |
| **STATUS** | **RESOLVED (with a caveat — see §21)** |

---

## 16. Author contacts and unresolved status

| Field | Value |
| --- | --- |
| **ISSUE** | The dashboard implied dozens of author replies were needed to finalise the review. |
| **OLD STATE** | "60 formal author inquiries have been cataloged … our highest-yield ongoing activity"; "60 Studies with targeted Author Contacts"; roster headed "(60 Trials)"; **35 studies stamped with an amber "Inquiry Pending" badge**. |
| **V26 CORRECT STATE** | `AF_P1_Disposition`: **19/19 P1 issues dispositioned, 0 global final-lock blockers.** 18 resolved analytically — by source hierarchy (1), raw-data rule (2), native-data rule (1), exclusion (6), partial exclusion (1), field exclusion (1), timepoint exclusion (1), screening exclusion (1), sensitivity (1), mandatory sensitivity (1), stratification (1), narrative-only (1). **One hard hold**: P1-01, the Yeh 2010 / Yeh 2011 cohort-overlap question, handled by excluding both from pooling rather than by awaiting correspondence. |
| **ACTION TAKEN** | Rewrote the outreach section to state that no author reply is required to finalise. Badges now render the recorded disposition class (Dispositioned / Complete / Hard hold) instead of a blanket "Pending". Roster reframed as a provenance record. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/app.js` |
| **VERIFICATION** | Validator fails on "60 formal author inquiries", on any "Inquiry Pending" badge, and on any P1 row whose `Globalfinallockblocker` is not `NO`. |
| **STATUS** | **RESOLVED** |

---

## 17. Downloads and stale files

| Field | Value |
| --- | --- |
| **ISSUE** | Active downloads pointed at pre-v26 outputs. |
| **OLD STATE** | The primary tab served `stata_audited_synthesis.{do,log}`, `stata_consensus_synthesis_data.csv` (the 11-trial pool), `stata_secondary_synthesis_data.csv`, and the three `stata_48h_opioid_synthesis.*` files. The in-page Stata terminal fetched `stata_audited_synthesis.log`. 41 further pre-v26 artifacts sat in `dashboard/` unreferenced but publicly served. |
| **V26 CORRECT STATE** | All downloads resolve to `06_FINAL_ANALYSIS_V26` equivalents. |
| **ACTION TAKEN** | Repointed every active download and the terminal fetch. Archived **45** superseded artifacts to `99_audit/superseded_dashboard_artifacts/` with a README recording, per group, why it was retired and its replacement. Nothing was deleted. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `dashboard/app.js`, `99_audit/superseded_dashboard_artifacts/` (46 files incl. README) |
| **VERIFICATION** | Validator fails if any active download names a retired artifact, and confirms the 12 served forest/LOO PNGs are byte-identical to `04_FIGURES`. Confirmed the `PRIMARY_LOO_DATA` table matches `logs/08_sensitivity.log` exactly (−1.752, −5.779, −5.746, −6.162, −1.747, −6.196). |
| **STATUS** | **RESOLVED** |

---

## 18. Deployment portability of asset links

| Field | Value |
| --- | --- |
| **ISSUE** | Found during local QA: every `06_FINAL_ANALYSIS_V26/...` link was repo-root-relative. |
| **OLD STATE** | Those 12 links resolved on the live site **only** because `gh-pages` puts the dashboard at the site root *and* carries its own copy of the analysis package. Served from `docs/` or any subdirectory they 404 silently — confirmed empirically: 12 of 26 assets broken when served at `/dashboard/index.html`. |
| **V26 CORRECT STATE** | Links must be page-relative so they survive any mount point. |
| **ACTION TAKEN** | `sync_dashboard.sh` now mirrors `06_FINAL_ANALYSIS_V26/` into `dashboard/v26/`; links rewritten to `v26/...`. The dashboard is now a self-contained reproducibility bundle. |
| **FILE(S) CHANGED** | `scripts/sync_dashboard.sh`, `dashboard/index.html`, `dashboard/app.js`, `dashboard/v26/**` |
| **VERIFICATION** | 26/26 assets return 200 when served from a subdirectory. Validator rejects any reappearance of a repo-root-relative link and requires the `v26/` mirror to be current. |
| **STATUS** | **RESOLVED** |

---

## 19. Analysed denominators

| Field | Value |
| --- | --- |
| **ISSUE** | Found during local QA: the MCID subtitle reported N = 562 directly beneath a header reading N = 628. |
| **OLD STATE** | Audit of all 63 `population` blocks against `Outcome_Data_AF_LOCK`: 54 held **analysed** denominators while the UI labelled them "randomized"; **7 matched neither source**. Worst case: **He 2026 (hepatectomy/JIS) — one of the six strict primary trials — displayed "86 randomized (43 / 43)" for a trial that randomised 161 and analysed 159**, a remnant of the superseded fabricated payload. |
| **V26 CORRECT STATE** | El-Rakshy 2009 42/53; Yeh 2010 33/30; Yeh 2011 30/30 (it had been holding Yeh 2010's numbers); Lee 2011 12/12; Grech 2016 11/9 (the study total had been placed in arm 1); Gu 2019 58/59 (arms transposed); He 2026 (hep) 80/79 with randomised 81/80. Wang 2024 (68/70) is a legitimate two-cohort aggregate and is exempt. |
| **IMPACT** | The meta-analysis itself was **unaffected** — `outcomes.opioid_24h` already carried the correct 80/79 — but every displayed sample size for those trials was wrong. |
| **ACTION TAKEN** | Corrected the seven blocks, relabelled the UI from "randomized" to "analysed", carried randomised n separately and shown in the drawer when it differs. |
| **FILE(S) CHANGED** | `dashboard/data.js`, `dashboard/app.js`, `dashboard/index.html` |
| **VERIFICATION** | Validator requires every denominator to trace to `Outcome_Data_AF_LOCK` and the paired cohort N to equal the primary N. Browser confirms He 2026 now reads "159 (80 / 79)" with "Randomised: 161 (81 vs 80)" in the drawer, and the MCID tab shows 628 in both places. |
| **STATUS** | **RESOLVED** |

---

## 20. Provenance statement and build integrity

| Field | Value |
| --- | --- |
| **ISSUE** | No visible provenance statement; cache-buster was hand-maintained. |
| **OLD STATE** | Provenance existed only as a `window.DATA_PROVENANCE` object in `data.js`, invisible to readers. The cache token `?v=20260906_rob2_locked` was edited by hand; during QA the browser served a cached `data.js` after the denominator fix, still showing the pre-fix values — exactly what a returning visitor would have seen. |
| **V26 CORRECT STATE** | A visible footer on every tab naming the data source, the statistical source, and the registration; a token that changes if and only if the assets change. |
| **ACTION TAKEN** | Added the `#dashboard-provenance` footer (data source: the v26 lock workbook; statistical source: StataNow 19.5 SE, reproduced byte-identically; registration: CRD420251090635; plus a note that non-reproducible analyses are shown as withdrawn rather than restated). Cache token is now a SHA-256 of the concatenated JS/CSS assets. |
| **FILE(S) CHANGED** | `dashboard/index.html`, `scripts/sync_dashboard.sh` |
| **VERIFICATION** | Validator requires all three provenance elements and the footer element. Rebuild after the data fix moved the token to `ff18218daf78` and the browser picked up corrected values. |
| **STATUS** | **RESOLVED** |

---

## 21. Remaining scientific note (not a defect, recorded for transparency)

**The MCID paired cohort is not derivable from the strict v26 sets alone.**

The strict primary 24-h opioid set (k=6) and the strict rest-pain set (k=2: Xing
2022, Liu 2021) have **zero overlap**. The paired cohort in `data.js` therefore
pairs each primary trial's 24-h opioid result with a pain estimate that is not
itself part of the strict Target C analysis (Target C admits only pain
explicitly measured **at rest**, which is why it is k=2).

This is defensible as an exploratory trade-off display — and it is now labelled
as study-level and confined to the six strict primary trials — but the pain axis
does not carry the same estimand discipline as Target C. Two options for the
manuscript team:

1. Keep it as an exploratory display and state in the caption that the pain
   values are the trial-reported ~24-h pain estimates, not the strict at-rest
   estimand of Target C. *(Current behaviour.)*
2. Restrict the plot to trials contributing to **both** strict sets — which
   would empty it — and drop the quadrant analysis.

No dashboard number is wrong as a result; the caveat is about estimand purity on
the pain axis. Flagging for a human decision rather than resolving unilaterally.

---

## 22. Primary outcome contribution pathway

Added 2026-09-07 so collaborators can answer "why is my paper not in the main
forest plot?" from the dashboard rather than from the reconciliation workbook.

### Totals (all derived, none hardcoded)

| Bucket | Count | N |
| --- | --- | --- |
| RCTs included in the systematic review | **63** | — |
| Publications reporting potentially relevant ~24-h opioid information | **16** (15 study units) | — |
| — **strict primary contributors** | **6** | **628** |
| — conditional / sensitivity only | **5** | **317** |
| — pending author clarification | **4** | — |
| Included trials contributing to other outcomes | **30** | — |
| Included trials contributing to narrative / evidence map only | **17** | — |

16 + 30 + 17 = 63. The builder raises `SystemExit` if this does not reconcile.

The row count (62) is lower than the study count (63) because the **Yeh 2010 /
Yeh 2011 publication family is one study unit covering two reports**. Catching
that was the reconciliation guard's first catch: both Yeh publications were
initially double-counted in the remaining bucket.

### The five studies explaining k=6 → k=11

| Study | Reported as | Why not strict |
| --- | --- | --- |
| Chen 2015 | mg IV morphine, Median/IQR | Dose derived from fixed 2-mg rescue boluses; source reports counts, not dose |
| Chen 2015 (Hyperalgesia) | µg/kg sufentanil, Median/IQR | Derived from fixed 0.05 µg/kg boluses; weight-normalised |
| Coura 2011 | µg/kg fentanyl | Weight-normalised; 10/32 post-randomisation exclusions; High RoB |
| Sim 2002 | mg/kg morphine | Weight-normalised; multi-arm with a shared placebo comparator |
| Zhang 2025 | µg sufentanil | POD1 rather than an explicitly clock-defined 0–24 h window; High RoB |

These are valid randomised trials. The judgement is about **reporting
compatibility with the primary estimand**, not study quality.

### There is no k=11 pooled mean difference

| Field | Value |
| --- | --- |
| **ISSUE** | A broader 24-h analysis was requested at k=11, N=945. |
| **VERIFIED** | The **composition** verifies exactly: 6 strict + 5 conditional, N = 945. |
| **BUT** | Only **7 of 11** have an estimable MD in mg IV MME; **9 of 11** have an estimable Hedges' g. |
| **WHY** | `Sim 2002` — *"do not reconstruct absolute dose from group mean weight"*; `Coura 2011` — *"do not convert to absolute µg/MME using group-average weight"*; both Chen 2015 reports are Median/IQR with no derived mean/SD. |
| **PRE-V26 BEHAVIOUR** | The retired `stata_consensus_synthesis_data.csv` did exactly what those rows forbid, back-solving absolute doses from assumed body weights — implying **60 kg in one arm of Sim 2002 and 59 kg in the other**, and a flat **70 kg** for Coura 2011. |
| **ACTION** | No k=11 MD is fitted or displayed. The broader analysis uses the scale-free SMD, which pools weight-normalised with absolute-dose endpoints legitimately. The two Chen 2015 reports remain outside **both** pooled models and are reported narratively. |
| **STATUS** | **RESOLVED — k=11 MD withdrawn, k=9 SMD substituted** |

### Pooled results (`10_broader24h_sensitivity.do`)

| Analysis | k | N | Estimate | 95% KH CI | CI width | p | I² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Strict primary — MD | 6 | 628 | −4.68 mg | [−12.26, +2.89] | 15.15 | 0.173 | 98.29% |
| Strict primary — SMD | 6 | 628 | g = −0.890 | [−2.259, +0.479] | 2.74 | 0.156 | 97.24% |
| Broader sensitivity — SMD | 9 | 803 | g = −0.880 | [−1.699, −0.060] | 1.64 | 0.038 | 95.19% |

The strict SMD row reproduces the pre-existing `OP24_PRIM_SMD` exactly, which
cross-validates the new do-file against the established pipeline.

**Interpretation shown on the dashboard:** the point estimate moves by 0.010
while the interval narrows from 2.74 to 1.64 units. The significance flip is a
**precision** effect, not an effect-size effect, and the dashboard warns
explicitly against reading it as the effect becoming real — the broader model
buys precision by accepting weaker assumptions about what the added trials
measured. The strict analysis remains the prespecified primary result.

### Author-contact candidates

Included only where the trial carries potentially relevant 24-h opioid
information **and** a documented reporting gap.

| Study | Available | Missing | Requested | Contact status |
| --- | --- | --- | --- | --- |
| **Jin 2023** | PCIA solution volume at 24 h (n=53/52) | Article does not report fentanyl concentration | Concentration of fentanyl in the PCIA solution (µg/mL or total µg in total volume) | CONTACT PREPARED |
| **Luo 2026** | Published "sufentanil equivalents", perioperative window (n=138/139) | Unit/definition unresolved; window not 0–24 h | Cumulative 24-h systemic opioid consumption (mean ± SD, IV MME) | CONTACT PREPARED |
| **Zhou 2021** | Any postoperative opioid use, binary (n=41/40) | Exact window not stated; conversion rule differs between Methods and Table footnote (P1-09) | 24-h cumulative opioid separated from whole-stay consumption | CONTACT PREPARED |
| **Yeh family** | 24-h IV morphine PCA dose (n=30/30) | Cohort overlap with the companion report unadjudicated (P1-01, HARD HOLD) | *Prepared letter requests PONV counts and a registration number* | CONTACT PREPARED — **but see note** |

**Note on Yeh.** The prepared letter does **not** request the cohort-overlap
clarification that actually blocks the 24-h result. Sending it as drafted would
not, on its own, make the trial strictly usable. The dashboard states this
rather than implying the contact is sufficient. Flagged by a keyword check
(`addresses_primary_blocker`) that is reported, never used to change a category.

**Contact status is never inferred.** The project holds no sent/response field
anywhere — `author_inquiries.json` has `data_needed`, `draft_letter` and
`priority` only. A candidate with a draft letter is therefore **CONTACT
PREPARED**; one without any record would be **STATUS NOT DOCUMENTED**. The
validator fails on any status implying contact occurred.

### Classification rule

Applied to the 24-h candidate rows in `opioid_24h_primary.csv`:

- **strict** — `inc_primary == 1`
- **conditional** — `inc_sens == 1 and inc_primary == 0`
- **candidate** — neither, but the trial carries potentially relevant 24-h
  opioid information and has a documented reporting gap

### Data sources

`opioid_24h_primary.csv`, `target_{A..F}*.csv`,
`master_reconciled_results_v26.csv`, `AF_P1_Disposition.csv`,
`AF_Unresolved.csv`, `author_inquiries.json`, `data.js`.

Generated by `scripts/build_primary_pathway.py` → `dashboard/primary_pathway.js`.

### Terminology

The other included trials are **never** described as "excluded from the review".
They are included RCTs that do not contribute to *this* estimand, and the
section names what they do contribute to. A validator check fails on any
non-negated "excluded from the review" and on a "57 studies excluded" framing.

### Validation

Eight new checks (37/37 total): counts derive from array lengths; buckets
reconcile to 63; categories mutually exclusive; no candidate silently counted as
strict; N equals summed analysed denominators; pooled results match Stata
exactly; no MD fabricated across the candidate pool; contact status documented
with a source reason; wording rule; markup contains no hardcoded counts.

Verified the k=11 guard still bites by injecting a fake pooled MD — it trips
four checks.

---

## Validation

`scripts/validate_dashboard.py` — **29/29 checks passing**, exits 1 on any failure.

The previous validator reported 14/14 green while the dashboard still served
k=11, N=945, the withdrawn multivariable model, a contradictory GRADE headline
and 60 "pending" inquiries. It asserted only that correct strings were
*present*, which is satisfiable while stale values sit beside them. Every check
is now ABSENCE, DERIVED (from the v26 CSVs) or STRUCTURAL (a property of the
code). Running it immediately caught a live claim the old suite missed.

## Commits

| Commit | Scope |
| --- | --- |
| `8dbb022` | Pages source identified; canonical pipeline established |
| `f2a1fee` | Stata pipeline reproduced byte-for-byte; execution logs committed |
| `c703e78` | k=11 meta-regression apparatus withdrawn |
| `126dccc` | MCID cohort, GRADE headline, author-contact status |
| `d744aea` | Result-specific RoB 2 across the whole dashboard |
| `8fd9a9a` | Downloads retired, eligibility wording, provenance footer |
| `1891355` | Adversarial validator |
| `a58c3d8` | Analysed denominators; portable asset links |
| `e2f132f` | Content-derived cache buster |
