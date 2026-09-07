* ==============================================================================
* 03_targetB_72h.do: Target B (0-72 h Cumulative Postoperative Opioid Consumption)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_B_72h.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/03_targetB_72h.log", replace

di as txt "=================================================================="
di as txt "03: TARGET B: 0-72 H CUMULATIVE POSTOPERATIVE OPIOID CONSUMPTION"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_B_72h.dta", clear
describe

* List all Target B entries
di as txt _n "=== ALL TARGET B STUDIES ==="
list lock_id study comparison_id include_strict include_sensitivity n_i mean_i sd_i n_c mean_c sd_c md se unit rob_overall, clean

* ------------------------------------------------------------------------------
* 1. STRICT EXACT 0-72 H (k=1: Yang 2024) -> NOT POOLED
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. STRICT EXACT 0-72 H SET (k=1): NOT POOLED (Single study report)"
di as txt "Yang 2024: MD = -0.50 mg morphine (95% CI: -4.08 to 3.08)"
di as txt "------------------------------------------------------------------"

* ------------------------------------------------------------------------------
* 2. SENSITIVITY: Pooled Broader Target B (Yang 2024 + Wong 2006, k=2) [REML + KH]
* ------------------------------------------------------------------------------
meta set md se, studylabel(study) eslabel("Mean Difference (mg IV morphine)")

di as txt _n "------------------------------------------------------------------"
di as txt "2. SENSITIVITY POOLED BROADER MODEL (Yang 2024 + Wong 2006, k=2)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh)
matrix res_b_pool = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 3. GENERATE AND EXPORT FOREST PLOT
* ------------------------------------------------------------------------------
meta forestplot, ///
    title("TARGET B: 72h Cumulative Postoperative Opioid Consumption", size(medium)) ///
    subtitle("Sensitivity Model (Yang 2024 exact 72h + Wong 2006 first 3 days, k=2)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetB_72h_mme.png", width(1800) replace

* ------------------------------------------------------------------------------
* 4. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 2
gen analysis_id = ""
gen outcome = "0-72 h Cumulative Postoperative Opioid"
gen stratum = ""
gen k = .
gen estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen q_stat = .
gen model = ""

replace analysis_id = "TB_STRICT_EXACT" in 1
replace stratum = "Strict Exact 0-72h (Yang 2024 alone)" in 1
replace estimate = -0.50 in 1
replace ci_low   = -4.078 in 1
replace ci_high  = 3.078 in 1
replace p_value  = 0.784 in 1
replace k        = 1 in 1
replace tau2     = . in 1
replace i2       = . in 1
replace q_stat   = . in 1
replace model    = "Single study (Not pooled)" in 1

replace analysis_id = "TB_BROADER_SENS" in 2
replace stratum = "Sensitivity: Exact + First 3 Days (Yang + Wong)" in 2
replace estimate = res_b_pool[1,1] in 2
replace ci_low   = res_b_pool[1,2] in 2
replace ci_high  = res_b_pool[1,3] in 2
replace p_value  = res_b_pool[1,4] in 2
replace k        = res_b_pool[1,5] in 2
replace tau2     = res_b_pool[1,6] in 2
replace i2       = res_b_pool[1,7] in 2
replace q_stat   = res_b_pool[1,8] in 2
replace model    = "REML + Hartung-Knapp" in 2

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetB_72h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetB_72h.csv", replace
list, clean

di as txt _n "SUCCESS: Target B analyses completed and exported."
log close
