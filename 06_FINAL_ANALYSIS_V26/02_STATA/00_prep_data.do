* ==============================================================================
* 00_prep_data.do: Prepare and Export Clean Analysis Datasets from v26 Lock
* Systematic Review: Perioperative TEAS and EA for Opioid Sparing
* Source: TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx
* Authoritative Engine: StataNow 19.5 BE
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/00_prep_data.log", replace

di as txt "=================================================================="
di as txt "00: PREPARING CLEAN ANALYSIS DATASETS FROM AUTHORITATIVE V26 WORKBOOK"
di as txt "Source: TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx"
di as txt "=================================================================="

local master_xlsx "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx"

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

gen comparator_type = ""
replace comparator_type = "Sham" if strpos(comparator, "Sham") > 0 | strpos(comparator, "Placebo") > 0 | strpos(comparator, "No-current") > 0
replace comparator_type = "Usual Care / Control" if comparator_type == ""

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
