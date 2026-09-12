* ==============================================================================
* 00_prep_data.do: Prepare and Export Clean Analysis Datasets from v32 Lock
* Systematic Review: Perioperative TEAS and EA for Opioid Sparing
* Source: TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx
* Authoritative Engine: StataNow 19.5 BE
*
* MIGRATED 2026-09-07 from v26 to v32 (v32 = v31 base + Zhang 2018 append; v31
* itself is not held in this repo, only described in v32's own README). Schema
* of every sheet this script reads (Stata_Opioid24_Primary, AF_Result_Lock,
* Stata_AF_Long) is byte-identical to v26. Row-by-row diff against v26 found:
*   - AF_Result_Lock, Stata_AF_Long: 0 rows added/removed/changed -> Targets
*     A-F, which are sourced entirely from these two sheets, are unaffected.
*   - Stata_Opioid24_Primary: +1 row (Szmit 2021, TEAS vs sham, direct-reported
*     mean/SD IV morphine, provisional_primary_include=1, hard_hold=0) versus
*     v26's 6 studies. Included under the same unfiltered
*     provisional_primary_include rule already applied to the other 6, per
*     project decision 2026-09-07. Strict primary moves from k=6 to k=7.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/00_prep_data.log", replace

di as txt "=================================================================="
di as txt "00: PREPARING CLEAN ANALYSIS DATASETS FROM AUTHORITATIVE V32 WORKBOOK"
di as txt "Source: TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx"
di as txt "=================================================================="

local master_xlsx "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx"

* ------------------------------------------------------------------------------
* PART 1: PRIMARY 24-H OPIOID CONSUMPTION
* ------------------------------------------------------------------------------
import excel using "`master_xlsx'", sheet("Stata_Opioid24_Primary") firstrow clear

* Standardize variable names
rename provisional_primary_include inc_primary
rename provisional_sensitivity_include inc_sens

* ------------------------------------------------------------------------------
* MME CONVERSION FACTORS (IV morphine milligram equivalents)
*
* Prespecified equianalgesic conversion framework. Uncertainty in the sufentanil
* factor is carried explicitly into 11_sufentanil_conversion_sensitivity.do.
* Full per-drug audit: 06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv
*
*   morphine        1.0 mg MME per mg    reference standard, self-referential
*   hydromorphone   5.0 mg MME per mg    BC Ministry of Health palliative
*                                        equianalgesic table: hydromorphone 2 mg
*                                        parenteral = morphine 10 mg parenteral.
*                                        (Some tables use 1.5 mg -> 6.67:1; the
*                                        published parenteral range is 5:1-6.67:1.)
*   sufentanil      1.0 mg MME per ug    1000:1. BC table: sufentanil 0.01-0.04 mg
*                                        (10-40 ug) = morphine 10 mg parenteral,
*                                        i.e. 250:1-1000:1. FDA/Pfizer sufentanil
*                                        label: "as much as 10 times as potent as
*                                        fentanyl" in balanced general anaesthesia
*                                        (5-7x as sole agent), and IV fentanyl is
*                                        100:1 vs morphine -> 500:1-1000:1.
*                                        Balanced general anaesthesia is the
*                                        setting of the contributing trials.
*
* CORRECTED 2026-09-07. This factor was previously 0.1 (100:1), identical to the
* fentanyl ratio and unsupported by any located source, since every source places
* sufentanil at 5-10x fentanyl's potency. See opioid_conversion_audit.csv for the
* full record of the discrepancy and the sensitivity analysis across 0.1/0.25/
* 0.5/1.0 that quantifies the conversion's influence on every affected result.
*
* NOTE: Hedges' g below is computed from NATIVE units (mean_i, sd_i), so every
* standardized (SMD) analysis in this project is invariant to these factors.
* Only mean-difference-in-MME analyses are affected.
* ------------------------------------------------------------------------------
gen mme_factor = .
replace mme_factor = 1.0 if unit == "mg morphine" | unit == "mg IV morphine" | unit == "mg MME"
replace mme_factor = 5.0 if unit == "mg hydromorphone"
replace mme_factor = 1.0 if unit == "µg sufentanil"

gen mean_i_mme = mean_i * mme_factor
gen sd_i_mme   = sd_i   * mme_factor
gen mean_c_mme = mean_c * mme_factor
gen sd_c_mme   = sd_c   * mme_factor

* Calculate Mean Difference and SE in MME
gen md_mme = mean_i_mme - mean_c_mme
gen se_mme = sqrt((sd_i_mme^2 / n_i) + (sd_c_mme^2 / n_c))
gen ci_low_mme = md_mme - invnormal(0.975) * se_mme
gen ci_upp_mme = md_mme + invnormal(0.975) * se_mme

* Calculate Hedges' g (SMD) and SE
gen s_pooled = sqrt( ((n_i - 1)*sd_i^2 + (n_c - 1)*sd_c^2) / (n_i + n_c - 2) )
gen d = (mean_i - mean_c) / s_pooled
gen j_corr = 1 - (3 / (4 * (n_i + n_c) - 9))
gen hedges_g = d * j_corr
gen hedges_se = sqrt( ((n_i + n_c) / (n_i * n_c)) + (hedges_g^2 / (2 * (n_i + n_c))) )

* Classify intervention modality and comparator
gen modality = ""
replace modality = "TEAS" if strpos(intervention, "TEAS") > 0 | strpos(intervention, "TENS") > 0
replace modality = "EA"   if strpos(intervention, "EA") > 0 & modality == ""

* ------------------------------------------------------------------------------
* COMPARATOR CLASSIFICATION (corrected 2026-09-08, v33 tiered audit)
*
* The previous rule matched "Sham"/"Placebo"/"No-current" CASE-SENSITIVELY, which
* silently misfiled four rows whose source text uses lower-case "sham":
*     Chen 2015                "Electrodes/device with no stimulation"  -> was Usual Care
*     Chen 2015 (Hyperalgesia) "Electrodes/no-current sham"             -> was Usual Care
*     Zhang 2025               "Sub-sensory sham"                       -> was Usual Care
*     Yeh (lumbar-spine family) "Electrical sham/nonacupoint AES"       -> was Usual Care
* None of these has inc_primary==1, so no published estimate was affected, but the
* error would corrupt any comparator-stratified analysis.
*
* Three categories are now distinguished, because they are not interchangeable:
*   Sham              inert control: device applied, no current delivered
*   Active electrical real current delivered at a control site (non-acupoint /
*                     non-meridian / incision-periphery TENS). NOT an inert sham.
*   Usual Care        no device at all
*
* Order matters. Inert-sham markers are tested BEFORE device names: Chen 1998's
* control is "Sham ST36 TENS (0 mA)", i.e. a TENS device at ZERO current, which is
* an inert sham. Matching the device name "TENS" first would misfile a genuine
* sham-controlled trial as an active electrical comparator.
* ------------------------------------------------------------------------------
gen comparator_lc = lower(comparator)
gen comparator_type = ""

* 1. Inert sham (tested first)
replace comparator_type = "Sham" if ///
      strpos(comparator_lc, "0 ma") > 0            ///
    | strpos(comparator_lc, "zero-current") > 0    ///
    | strpos(comparator_lc, "zero current") > 0    ///
    | strpos(comparator_lc, "no-current") > 0      ///
    | strpos(comparator_lc, "no current") > 0      ///
    | strpos(comparator_lc, "no stimulation") > 0  ///
    | strpos(comparator_lc, "nonpenetrating") > 0  ///
    | strpos(comparator_lc, "sub-sensory sham") > 0 ///
    | strpos(comparator_lc, "placebo") > 0

* 2. Active electrical control (real current at a control site)
replace comparator_type = "Active Electrical" if comparator_type == "" & ( ///
      strpos(comparator_lc, "nonacupoint") > 0     ///
    | strpos(comparator_lc, "non-acupoint") > 0    ///
    | strpos(comparator_lc, "nonmeridian") > 0     ///
    | strpos(comparator_lc, "incision-periphery tens") > 0 )

* 3. Remaining explicit sham wording
replace comparator_type = "Sham" if comparator_type == "" & strpos(comparator_lc, "sham") > 0

* 4. Everything else is usual care / no device
replace comparator_type = "Usual Care / Control" if comparator_type == ""
drop comparator_lc

* Study label for plots
gen study_label = study_unit

sort inc_primary study_unit
save "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv", replace

di as txt "Saved 01_DATA/opioid_24h_primary.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 2: IMPORT RESULT-SPECIFIC ROB FROM AF_Result_Lock FOR MERGING
* ------------------------------------------------------------------------------
import excel using "`master_xlsx'", sheet("AF_Result_Lock") firstrow clear
rename LockID lock_id
rename OverallRoB result_rob
rename D1 rob_d1
rename D2 rob_d2
rename D3 rob_d3
rename D4 rob_d4
rename D5 rob_d5
keep lock_id result_rob rob_d1 rob_d2 rob_d3 rob_d4 rob_d5 Sourceverifiedresult KeyQCnote
tempfile af_rob
save `af_rob', replace

* ------------------------------------------------------------------------------
* PART 3: STATA_AF_LONG MASTER IMPORT AND MERGE
* ------------------------------------------------------------------------------
import excel using "`master_xlsx'", sheet("Stata_AF_Long") firstrow clear
merge m:1 lock_id using `af_rob', keep(master match) nogenerate

* ------------------------------------------------------------------------------
* POST-LOCK ADDITION 2026-09-07: Szmit 2021, Target D nausea 0-24h
*
*   Szmit 2021 is a post-lock source-direct addition (v32 workbook); it has no
*   row in the frozen AF_Result_Lock/Stata_AF_Long sheets. Its per-outcome flags
*   in Outcome_Data_AF_LOCK were checked directly (comparison_id
*   SZMIT21_TEAS_vs_SHAM_NAUSEA24): AF include strict = 1, AF target = D,
*   AF endpoint stratum = D_nausea_0-24h -- the workbook's own curator marked
*   this ready for the same D_nausea_0-24h pool 05_ponv.do already computes
*   (previously k=2: Yang 2024, Ma 2026). Every other new-study row surfaced by
*   this migration (Gao 2022, Song 2020, and Szmit's own alternate PCA-only and
*   pain rows) is flagged include_strict=0 AND include_sensitivity=0 or held for
*   unresolved QC/digitization, and is deliberately NOT added here or anywhere
*   else in the pipeline. See 06_AUDIT/dashboard_v26_reconciliation.md for the
*   full per-study readiness audit.
*
*   RoB 2 (D1-D5, overall) is copied from Corrected_RoB2's Szmit 2021 row, the
*   only RoB 2 assessment the workbook records for this study (result-specific
*   RoB is normally one assessment per study in this workbook, applied across
*   the study's contributing results per this project's existing convention).
* ------------------------------------------------------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "SZMIT21-POSTLOCK" in `n'
replace target = "D" in `n'
replace endpoint_stratum = "D_nausea_0-24h" in `n'
replace study = "Szmit 2021" in `n'
replace comparison_id = "SZMIT21_TEAS_vs_SHAM_NAUSEA24" in `n'
replace intervention = "Postoperative TEAS: bilateral LI4 + ipsilateral peri-incisional ashi points; alternating 2/100 Hz; 30 min every 2 h through 24 h" in `n'
replace comparator = "Sham TEAS: identical devices/placement with no electrical stimulation + PCA" in `n'
replace outcome = "Nausea incidence" in `n'
replace time_window = "Postoperative observation period; PCA/TEAS discontinued at 24 h" in `n'
replace data_type = "Events/total" in `n'
replace n_i = 24 in `n'
replace n_c = 24 in `n'
replace events_i = 0 in `n'
replace events_c = 4 in `n'
replace unit = "participants with nausea" in `n'
replace reported_p = "0.116 (3-group overall)" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace shared_control_issue = "Alternative comparator exists (TEAS-vs-PCA-only, SZMIT21_TEAS_vs_CTRL_NAUSEA24); do not double count." in `n'
replace source_qc = "Zero events in TEAS; use events/denominators directly rather than the non-significant three-group overall P value (P=0.116)." in `n'
replace record_status = "SOURCE-VERIFIED" in `n'
replace source_url = "https://drive.google.com/file/d/1SbgHRO4KEP9X0Unz75vDMFCvlkDTEgk3/view?usp=drivesdk" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Low" in `n'
replace rob_d2 = "Low" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Low" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "Nausea 0/24 (TEAS) vs 4/24 (sham) during postoperative observation through 24 h; three-group overall P=0.116" in `n'

* ------------------------------------------------------------------------------
* POST-LOCK ADMISSIONS 2026-09-12, following the dedicated eligibility
* reconciliation pass (scripts/build_eligibility_reconciliation.py) and a
* review-team ruling on each.
*
* The Szmit 2021 comment above says Gao 2022 and Song 2020 were "deliberately
* NOT added". That was accurate under the flags as they then stood. The
* reconciliation pass revisited both:
*
*   Song 2020  -- the hold was "pending resolution of the ITT (85) vs
*                 per-protocol (78) denominator inconsistency". There is no
*                 inconsistency: the paper defines both populations, reconciles
*                 them exactly (3 allergic + 2 ICU + 2 delayed drain = 7;
*                 85 - 7 = 78) and states "All analyses were based on the
*                 intention-to-treat (ITT) population". The register's
*                 42/43 = 85 IS that ITT population. The control is a sham in
*                 the paper's own words ("The control group also underwent this
*                 sham treatment").
*
*   Gao 2022   -- the hold was that "patients could not be fully blinded to real
*                 stimulation". That is a risk-of-bias concern, and this review
*                 handles those through result-specific RoB 2 feeding GRADE, not
*                 through exclusion. Applying exclusion here while pooling every
*                 other sham-controlled stimulation trial -- all of which share
*                 the same limitation -- was inconsistent. Review-team ruling
*                 2026-09-12: the concern belongs in RoB 2 Domain 2, which this
*                 study's Some-concerns judgement already carries.
*                 NOTE ITS WEIGHT: at n = 1,655 it dominates both pools it joins.
*
*   Zhang 2018 -- graph-only until 2026-09-12, when Figure 2a was formally
*                 digitised from the PDF's VECTOR path coordinates (not visually
*                 inferred, which the workbook forbids). The extraction
*                 reproduces all seven percentage reductions the paper reports,
*                 this outcome's to 0.02 pp. The paper prints mean +/- SE, so
*                 SD = SE x sqrt(21). See
*                 07_TIERED_V33/03_DIGITIZATION/figure_only_values_QC_2026-09-12.md
*
* Zhang 2018's POD 1 pain is deliberately NOT admitted to Target C: POD 1 is a
* day label, treatment ran "daily from POD 1 to POD 3" so the score falls on the
* first treatment day, and the same rule already excludes Liu 2015's POD 1 PONV.
*
* RoB 2 (D1-D5, overall) is copied from each study's Corrected_RoB2 row, the
* same convention the Szmit block above uses.
* ------------------------------------------------------------------------------

* --- Song 2020: Target C, rest pain VAS at 24 h --------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "SONG20-POSTLOCK-C" in `n'
replace target = "C" in `n'
replace endpoint_stratum = "C_rest_pain_~24h" in `n'
replace study = "Song 2020" in `n'
replace comparison_id = "SONG20_TEAS_vs_SHAM_PAIN24" in `n'
replace intervention = "TEAS at bilateral PC6/HT7; 30 min the night before surgery, at the end of surgery, and before sleep on postoperative nights 2 and 3" in `n'
replace comparator = "Sham stimulation: identical electrode placement and 2/10 Hz setting, patients blinded" in `n'
replace outcome = "Rest pain VAS" in `n'
replace time_window = "24 h" in `n'
replace data_type = "Mean/SD" in `n'
replace n_i = 42 in `n'
replace n_c = 43 in `n'
replace mean_i = 2.76 in `n'
replace sd_i = 1.1 in `n'
replace mean_c = 3.23 in `n'
replace sd_c = 1.1 in `n'
replace unit = "VAS 0-10" in `n'
replace reported_p = "0.053" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace source_qc = "ITT population (85 = 42 + 43), the paper's stated primary analysis set; the 78-patient per-protocol set is an additional analysis and reconciles exactly (3 allergic + 2 ICU + 2 delayed drain)." in `n'
replace record_status = "SOURCE-VERIFIED / POST-LOCK ADMITTED 2026-09-12" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Low" in `n'
replace rob_d2 = "Low" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Low" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "24-h VAS 2.76+/-1.1 (TEAS) vs 3.23+/-1.1 (sham), P=0.053; VAS 0-10 where 0 = no pain and 10 = severe pain, measured at 2, 4, 6 and 24 h after surgery" in `n'

* --- Song 2020: Target D, composite PONV 0-24 h --------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "SONG20-POSTLOCK-D" in `n'
replace target = "D" in `n'
replace endpoint_stratum = "D_PONV_0-24h" in `n'
replace study = "Song 2020" in `n'
replace comparison_id = "SONG20_TEAS_vs_SHAM_PONV24" in `n'
replace intervention = "TEAS at bilateral PC6/HT7 (see the Target C row)" in `n'
replace comparator = "Sham stimulation, patients blinded" in `n'
replace outcome = "Any PONV" in `n'
replace time_window = "0-24 h" in `n'
replace data_type = "Events/total" in `n'
replace n_i = 42 in `n'
replace n_c = 43 in `n'
replace events_i = 3 in `n'
replace events_c = 10 in `n'
replace unit = "participants" in `n'
replace reported_p = "0.039" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace source_qc = "Same ITT population as the Target C row." in `n'
replace record_status = "SOURCE-VERIFIED / POST-LOCK ADMITTED 2026-09-12" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Low" in `n'
replace rob_d2 = "Low" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Low" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "24-h PONV 3/42 (TEAS) vs 10/43 (sham), P=0.039" in `n'

* --- Gao 2022: Target C, pain VAS at 24 h --------------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "GAO22-POSTLOCK-C" in `n'
replace target = "C" in `n'
replace endpoint_stratum = "C_rest_pain_~24h" in `n'
replace study = "Gao 2022" in `n'
replace comparison_id = "GAO22_TEAS_vs_SHAM_PAIN24" in `n'
replace intervention = "TEAS at PC6 and ST36" in `n'
replace comparator = "Sham TEAS" in `n'
replace outcome = "Rest pain VAS" in `n'
replace time_window = "24 h" in `n'
replace data_type = "Mean/SD" in `n'
replace n_i = 827 in `n'
replace n_c = 828 in `n'
replace mean_i = 2.0 in `n'
replace sd_i = 1.7 in `n'
replace mean_c = 2.2 in `n'
replace sd_c = 1.8 in `n'
replace unit = "VAS 0-10" in `n'
replace reported_p = "0.006" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace source_qc = "Source table row reads '24 h pain VAS score 2.0 (1.7) 2.2 (1.8) 0.006', presented as mean (SD) and distinct from the PONV-severity VAS rows above it. The paper does not print the pain VAS range; 0-10 is taken from convention and from the magnitude of the values. The blinding limitation is carried in RoB 2 Domain 2 rather than by exclusion (review-team ruling 2026-09-12). At n=1,655 this trial dominates the pool." in `n'
replace record_status = "SOURCE-VERIFIED / POST-LOCK ADMITTED 2026-09-12" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Some concerns" in `n'
replace rob_d2 = "Low" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Low" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "24 h pain VAS 2.0 (1.7) vs 2.2 (1.8), P=0.006, mean (SD)" in `n'

* --- Gao 2022: Target D, composite PONV 0-24 h ---------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "GAO22-POSTLOCK-D" in `n'
replace target = "D" in `n'
replace endpoint_stratum = "D_PONV_0-24h" in `n'
replace study = "Gao 2022" in `n'
replace comparison_id = "GAO22_TEAS_vs_SHAM_PONV24" in `n'
replace intervention = "TEAS at PC6 and ST36" in `n'
replace comparator = "Sham TEAS" in `n'
replace outcome = "Any PONV" in `n'
replace time_window = "0-24 h" in `n'
replace data_type = "Events/total" in `n'
replace n_i = 827 in `n'
replace n_c = 828 in `n'
replace events_i = 243 in `n'
replace events_c = 283 in `n'
replace unit = "participants" in `n'
replace reported_p = "0.036" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace source_qc = "The blinding limitation is carried in RoB 2 Domain 2 rather than by exclusion (review-team ruling 2026-09-12). At n=1,655 this trial dominates the pool." in `n'
replace record_status = "SOURCE-VERIFIED / POST-LOCK ADMITTED 2026-09-12" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Some concerns" in `n'
replace rob_d2 = "Low" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Low" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "24 h composite PONV 243/827 (TEAS) vs 283/828 (sham), P=0.036" in `n'

* --- Zhang 2018: Target E, time to first flatus --------------------------------
local n = _N + 1
set obs `n'
replace lock_id = "ZHANG18-POSTLOCK-E" in `n'
replace target = "E" in `n'
replace endpoint_stratum = "E_time_to_first_flatus" in `n'
replace study = "Zhang 2018" in `n'
replace comparison_id = "ZHANG18_TEA_vs_SHAM_FLATUS" in `n'
replace intervention = "Needleless transcutaneous electrical acustimulation at ST36/PC6; 25 Hz, 0.5 ms, 2-10 mA, 1 h twice daily POD1-3" in `n'
replace comparator = "Sham-TEA at non-acupoints (active electrical sham)" in `n'
replace outcome = "Time to first flatus" in `n'
replace time_window = "Postoperative" in `n'
replace data_type = "Mean/SD" in `n'
replace n_i = 21 in `n'
replace n_c = 21 in `n'
replace mean_i = 51.330 in `n'
replace sd_i = 12.740 in `n'
replace mean_c = 80.051 in `n'
replace sd_c = 20.145 in `n'
replace unit = "hours" in `n'
replace reported_p = "<0.001 (reported as a 35.9% reduction)" in `n'
replace rob_overall = "Some concerns" in `n'
replace include_strict = 1 in `n'
replace include_sensitivity = 0 in `n'
replace source_qc = "Graph-derived: formally digitised 2026-09-12 from Figure 2a VECTOR path coordinates, not visually inferred. Calibration residual 0.28% of axis; the extraction reproduces all seven percentage reductions the paper reports, this one to 0.02 pp. The source prints mean +/- SE, so SD = SE x sqrt(21). See 07_TIERED_V33/03_DIGITIZATION/figure_only_values_QC_2026-09-12.md" in `n'
replace record_status = "GRAPH-DERIVED (VALIDATED) / POST-LOCK ADMITTED 2026-09-12" in `n'
replace result_rob = "Some concerns" in `n'
replace rob_d1 = "Some concerns" in `n'
replace rob_d2 = "Some concerns" in `n'
replace rob_d3 = "Low" in `n'
replace rob_d4 = "Some concerns" in `n'
replace rob_d5 = "Some concerns" in `n'
replace Sourceverifiedresult = "Time to first flatus, digitised Figure 2a: TEA 51.33 +/- 2.78 SE vs sham-TEA 80.05 +/- 4.40 SE hours, n=21 per arm; the paper reports a 35.9% reduction, P<0.001" in `n'

* Save Master Locked Dataset
save "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.csv", replace
di as txt "Saved 01_DATA/analysis_dataset_locked.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 4: SUBSET TARGET A (0-48 H CUMULATIVE OPIOID)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if target == "A"

* MME Conversion (same prespecified framework as PART 1; see header there):
* Chen 2020: sufentanil ug -> MME (factor 1.0, 1000:1)   [CORRECTED from 0.1]
* An 2014: fentanyl mg -> MME (factor 100.0, i.e. 100:1 per ug)
* Zhang 2023: Median/IQR 110 (80-110) vs 110 (90-110) mg IV MME -> Wan et al. conversion:
*   arm_i: mean = (80 + 110 + 110)/3 = 100.0, sd = (110 - 80)/1.34898 = 22.239
*   arm_c: mean = (90 + 110 + 110)/3 = 103.333, sd = (110 - 90)/1.34898 = 14.826
* Xie 2014: sufentanil ug -> MME (factor 1.0, 1000:1)     [CORRECTED from 0.1]

gen mme_factor = .
replace mme_factor = 1.0 if unit == "µg sufentanil"
replace mme_factor = 100.0 if unit == "mg fentanyl"
replace mme_factor = 1.0 if unit == "mg IV morphine-equivalent"

gen mean_i_mme = mean_i * mme_factor
gen sd_i_mme   = sd_i   * mme_factor
gen mean_c_mme = mean_c * mme_factor
gen sd_c_mme   = sd_c   * mme_factor

* Apply Wan et al. for Zhang 2023
replace mean_i_mme = (80 + 110 + 110) / 3 if study == "Zhang 2023"
replace sd_i_mme   = (110 - 80) / 1.34898 if study == "Zhang 2023"
replace mean_c_mme = (90 + 110 + 110) / 3 if study == "Zhang 2023"
replace sd_c_mme   = (110 - 90) / 1.34898 if study == "Zhang 2023"
gen is_median_converted = (study == "Zhang 2023")

gen md_mme = mean_i_mme - mean_c_mme
gen se_mme = sqrt((sd_i_mme^2 / n_i) + (sd_c_mme^2 / n_c))

save "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.csv", replace
di as txt "Saved 01_DATA/target_A_48h.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 5: SUBSET TARGET B (0-72 H CUMULATIVE OPIOID)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if target == "B"

gen md = mean_i - mean_c
gen se = sqrt((sd_i^2 / n_i) + (sd_c^2 / n_c))

save "06_FINAL_ANALYSIS_V26/01_DATA/target_B_72h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_B_72h.csv", replace
di as txt "Saved 01_DATA/target_B_72h.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 6: SUBSET TARGET C (PAIN AT REST ~24 H)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if target == "C"

gen md = mean_i - mean_c
gen se = sqrt((sd_i^2 / n_i) + (sd_c^2 / n_c))

save "06_FINAL_ANALYSIS_V26/01_DATA/target_C_pain24h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_C_pain24h.csv", replace
di as txt "Saved 01_DATA/target_C_pain24h.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 7: SUBSET TARGET D (PONV STRATIFIED)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if target == "D"

save "06_FINAL_ANALYSIS_V26/01_DATA/target_D_ponv.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_D_ponv.csv", replace
di as txt "Saved 01_DATA/target_D_ponv.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 8: SUBSET TARGET E (TIME TO FIRST FLATUS)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if target == "E"

* Note: Ng 2013 is in days; others are in hours.
* Convert Ng 2013 to hours (days * 24):
gen mean_i_hours = mean_i
gen sd_i_hours   = sd_i
gen mean_c_hours = mean_c
gen sd_c_hours   = sd_c

replace mean_i_hours = mean_i * 24 if study == "Ng 2013"
replace sd_i_hours   = sd_i   * 24 if study == "Ng 2013"
replace mean_c_hours = mean_c * 24 if study == "Ng 2013"
replace sd_c_hours   = sd_c   * 24 if study == "Ng 2013"

gen md_hours = mean_i_hours - mean_c_hours
gen se_hours = sqrt((sd_i_hours^2 / n_i) + (sd_c_hours^2 / n_c))

* Standardized Mean Difference (Hedges' g) on native scale
gen s_pooled = sqrt( ((n_i - 1)*sd_i^2 + (n_c - 1)*sd_c^2) / (n_i + n_c - 2) )
gen d = (mean_i - mean_c) / s_pooled
gen j_corr = 1 - (3 / (4 * (n_i + n_c) - 9))
gen hedges_g = d * j_corr
gen hedges_se = sqrt( ((n_i + n_c) / (n_i * n_c)) + (hedges_g^2 / (2 * (n_i + n_c))) )

save "06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.csv", replace
di as txt "Saved 01_DATA/target_E_flatus.dta (N = " _N ")"

* ------------------------------------------------------------------------------
* PART 9: SUBSET TARGET F (EXPLORATORY RESCUE / PCA / EXPOSURE)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/analysis_dataset_locked.dta", clear
keep if substr(target, 1, 1) == "F"

save "06_FINAL_ANALYSIS_V26/01_DATA/target_F_exploratory.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/01_DATA/target_F_exploratory.csv", replace
di as txt "Saved 01_DATA/target_F_exploratory.dta (N = " _N ")"

di as txt _n "SUCCESS: All analysis datasets cleanly prepared and exported."
log close
