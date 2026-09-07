* ==============================================================================
* 02_targetA_48h.do: Target A (0-48 h Cumulative Postoperative Opioid Consumption)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/02_targetA_48h.log", replace

di as txt "=================================================================="
di as txt "02: TARGET A: 0-48 H CUMULATIVE POSTOPERATIVE OPIOID CONSUMPTION"
di as txt "Model: Random-Effects REML + Hartung-Knapp (se(kh))"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta", clear
describe

* List all Target A entries
di as txt _n "=== ALL TARGET A STUDIES ==="
list lock_id study comparison_id include_strict include_sensitivity n_i mean_i_mme sd_i_mme n_c mean_c_mme sd_c_mme md_mme se_mme unit rob_overall, clean

* Declare Meta-Analysis Setting for MME
meta set md_mme se_mme, studylabel(study) eslabel("Mean Difference (mg IV MME)")

* ------------------------------------------------------------------------------
* 1. PRINCIPAL STRICT TARGET A MODEL (k=3: Chen 2020, Zhang 2023, An 2014)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. STRICT TARGET A (k=3: Chen 2020, Zhang 2023, An 2014) [REML + KH]"
di as txt "------------------------------------------------------------------"
meta summarize if include_strict == 1, random(reml) se(kh) predinterval
matrix res_strict = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 2. MANDATORY SENSITIVITY: Exclude An 2014 (PCA plausibility concern) -> k=2
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. MANDATORY SENSITIVITY: Exclude An 2014 -> k=2 (Chen 2020, Zhang 2023)"
di as txt "------------------------------------------------------------------"
meta summarize if include_strict == 1 & study != "An 2014", random(reml) se(kh) predinterval
matrix res_noan = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 3. SENSITIVITY: Exclude Median/IQR Converted Study (Zhang 2023) -> k=2
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. SENSITIVITY: Exclude Converted Median/IQR (Zhang 2023) -> k=2"
di as txt "------------------------------------------------------------------"
meta summarize if include_strict == 1 & is_median_converted == 0, random(reml) se(kh) predinterval
matrix res_noconv = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 4. SENSITIVITY: Broader 48-h Window (Including Xie 2014 Sham Contrast) -> k=4
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "4. SENSITIVITY: Broader 48-h Window Including Xie 2014 (vs Sham) -> k=4"
di as txt "------------------------------------------------------------------"
* Keep one contrast for Xie 2014 (EAS vs Sham)
meta summarize if include_strict == 1 | comparison_id == "XIE14_EAS_vs_SHAM_TOTALSUF", random(reml) se(kh) predinterval
matrix res_broader = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 5. GENERATE AND EXPORT FOREST PLOT
* ------------------------------------------------------------------------------
meta forestplot if include_strict == 1, ///
    title("TARGET A: 0-48h Cumulative Postoperative Opioid Consumption", size(medium)) ///
    subtitle("Strict Set (StataNow 19.5 SE: REML + Hartung-Knapp, k=3)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetA_48h_mme.png", width(1800) replace

* ------------------------------------------------------------------------------
* 6. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 4
gen analysis_id = ""
gen outcome = "0-48 h Cumulative Postoperative Opioid"
gen stratum = ""
gen k = .
gen estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen q_stat = .
gen model = "REML + Hartung-Knapp"

replace analysis_id = "TA_STRICT" in 1
replace stratum = "Strict Target A (Chen, Zhang, An)" in 1
replace estimate = res_strict[1,1] in 1
replace ci_low   = res_strict[1,2] in 1
replace ci_high  = res_strict[1,3] in 1
replace p_value  = res_strict[1,4] in 1
replace k        = res_strict[1,5] in 1
replace tau2     = res_strict[1,6] in 1
replace i2       = res_strict[1,7] in 1
replace q_stat   = res_strict[1,8] in 1

replace analysis_id = "TA_EXCL_AN" in 2
replace stratum = "Mandatory Sensitivity: Exclude An 2014" in 2
replace estimate = res_noan[1,1] in 2
replace ci_low   = res_noan[1,2] in 2
replace ci_high  = res_noan[1,3] in 2
replace p_value  = res_noan[1,4] in 2
replace k        = res_noan[1,5] in 2
replace tau2     = res_noan[1,6] in 2
replace i2       = res_noan[1,7] in 2
replace q_stat   = res_noan[1,8] in 2

replace analysis_id = "TA_EXCL_ZHANG" in 3
replace stratum = "Sensitivity: Exclude Converted (Zhang 2023)" in 3
replace estimate = res_noconv[1,1] in 3
replace ci_low   = res_noconv[1,2] in 3
replace ci_high  = res_noconv[1,3] in 3
replace p_value  = res_noconv[1,4] in 3
replace k        = res_noconv[1,5] in 3
replace tau2     = res_noconv[1,6] in 3
replace i2       = res_noconv[1,7] in 3
replace q_stat   = res_noconv[1,8] in 3

replace analysis_id = "TA_INCL_XIE" in 4
replace stratum = "Sensitivity: Broader Window (Include Xie 2014)" in 4
replace estimate = res_broader[1,1] in 4
replace ci_low   = res_broader[1,2] in 4
replace ci_high  = res_broader[1,3] in 4
replace p_value  = res_broader[1,4] in 4
replace k        = res_broader[1,5] in 4
replace tau2     = res_broader[1,6] in 4
replace i2       = res_broader[1,7] in 4
replace q_stat   = res_broader[1,8] in 4

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetA_48h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetA_48h.csv", replace
list, clean

di as txt _n "SUCCESS: Target A analyses completed and exported."
log close
