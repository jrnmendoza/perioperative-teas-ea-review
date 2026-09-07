* ==============================================================================
* 06_flatus.do: Target E (Time to First Postoperative Flatus)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/06_flatus.log", replace

di as txt "=================================================================="
di as txt "06: TARGET E: TIME TO FIRST POSTOPERATIVE FLATUS"
di as txt "Model: Random-Effects REML + Hartung-Knapp (se(kh))"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.dta", clear
describe

* List Target E studies
di as txt _n "=== TARGET E STUDIES (TIME TO FLATUS, k=6) ==="
list lock_id study comparison_id n_i mean_i sd_i n_c mean_c sd_c unit md_hours se_hours result_rob, clean

* ------------------------------------------------------------------------------
* 1. PRINCIPAL MODEL: MEAN DIFFERENCE IN HOURS (k=6) [REML + KH]
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. PRINCIPAL MODEL: MD IN HOURS (k=6) [REML + KH]"
di as txt "Note: Ng 2013 converted from days (2.0+-0.9 vs 2.3+-1.1 d) to hours."
di as txt "------------------------------------------------------------------"
meta set md_hours se_hours, studylabel(study) eslabel("Mean Difference (Hours)")
meta summarize, random(reml) se(kh)
matrix res_flatus_md = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* Prediction Interval
capture meta summarize, random(reml) se(kh) predint

* ------------------------------------------------------------------------------
* 2. STANDARDIZED MEAN DIFFERENCE (HEDGES' G SMD, k=6) [REML + KH]
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. STANDARDIZED MEAN DIFFERENCE (HEDGES' G, k=6) [REML + KH]"
di as txt "------------------------------------------------------------------"
meta set hedges_g hedges_se, studylabel(study) eslabel("Standardized Mean Difference (Hedges' g)")
meta summarize, random(reml) se(kh)
matrix res_flatus_smd = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 3. SENSITIVITY ANALYSIS: EXCLUDING NG 2013 (STUDIES REPORTED IN HOURS ONLY, k=5)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. SENSITIVITY: EXCLUDING NG 2013 (ORIGINALLY IN DAYS, k=5) [REML + KH]"
di as txt "------------------------------------------------------------------"
meta set md_hours se_hours, studylabel(study) eslabel("Mean Difference (Hours)")
meta summarize if study != "Ng 2013", random(reml) se(kh)
matrix res_sens_no_ng = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 4. SENSITIVITY ANALYSIS: EXCLUDING HIGH RoB STUDIES [REML + KH]
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "4. SENSITIVITY: EXCLUDING HIGH RoB [REML + KH]"
di as txt "------------------------------------------------------------------"
count if result_rob == "High"
local n_high = r(N)
if `n_high' > 0 {
    meta summarize if result_rob != "High", random(reml) se(kh)
    matrix res_sens_rob = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
}
else {
    matrix res_sens_rob = res_flatus_md
}

* ------------------------------------------------------------------------------
* 5. ESTIMATOR SENSITIVITY: DER SIMONIAN-LAIRD (DL) MODEL (k=6)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "5. ESTIMATOR SENSITIVITY: DL MODEL [WITH & WITHOUT KH]"
di as txt "------------------------------------------------------------------"
meta summarize, random(dl) se(kh)
matrix res_flatus_dl_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

meta summarize, random(dl)
matrix res_flatus_dl_wald = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 6. GENERATE AND EXPORT FOREST PLOTS
* ------------------------------------------------------------------------------
meta set md_hours se_hours, studylabel(study) eslabel("Mean Difference (Hours)")
meta forestplot, ///
    title("TARGET E: Time to First Flatus (Hours)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp (k=6)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetE_flatus.png", width(1800) replace

* ------------------------------------------------------------------------------
* 7. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 5

gen analysis_id = ""
gen outcome = "Time to first flatus"
gen model_spec = ""
gen k = .
gen estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen q_stat = .
gen notes = ""

* Row 1: MD in hours (REML + KH)
replace analysis_id = "TE_FLATUS_MD_REML_KH" in 1
replace model_spec = "MD Hours (REML + KH)" in 1
replace k = res_flatus_md[1,5] in 1
replace estimate = res_flatus_md[1,1] in 1
replace ci_low = res_flatus_md[1,2] in 1
replace ci_high = res_flatus_md[1,3] in 1
replace p_value = res_flatus_md[1,4] in 1
replace tau2 = res_flatus_md[1,6] in 1
replace i2 = res_flatus_md[1,7] in 1
replace q_stat = res_flatus_md[1,8] in 1
replace notes = "Primary analysis (k=6, Ng 2013 converted from days)" in 1

* Row 2: SMD Hedges' g (REML + KH)
replace analysis_id = "TE_FLATUS_SMD_REML_KH" in 2
replace model_spec = "SMD Hedges g (REML + KH)" in 2
replace k = res_flatus_smd[1,5] in 2
replace estimate = res_flatus_smd[1,1] in 2
replace ci_low = res_flatus_smd[1,2] in 2
replace ci_high = res_flatus_smd[1,3] in 2
replace p_value = res_flatus_smd[1,4] in 2
replace tau2 = res_flatus_smd[1,6] in 2
replace i2 = res_flatus_smd[1,7] in 2
replace q_stat = res_flatus_smd[1,8] in 2
replace notes = "Standardized Mean Difference (Hedges g)" in 2

* Row 3: Sensitivity excluding Ng 2013
replace analysis_id = "TE_FLATUS_EXCL_NG" in 3
replace model_spec = "MD Hours excl. Ng 2013 (REML + KH)" in 3
replace k = res_sens_no_ng[1,5] in 3
replace estimate = res_sens_no_ng[1,1] in 3
replace ci_low = res_sens_no_ng[1,2] in 3
replace ci_high = res_sens_no_ng[1,3] in 3
replace p_value = res_sens_no_ng[1,4] in 3
replace tau2 = res_sens_no_ng[1,6] in 3
replace i2 = res_sens_no_ng[1,7] in 3
replace q_stat = res_sens_no_ng[1,8] in 3
replace notes = "Excluding Ng 2013 (originally reported in days)" in 3

* Row 4: Sensitivity excluding High RoB
replace analysis_id = "TE_FLATUS_EXCL_HIGH_ROB" in 4
replace model_spec = "MD Hours excl. High RoB (REML + KH)" in 4
replace k = res_sens_rob[1,5] in 4
replace estimate = res_sens_rob[1,1] in 4
replace ci_low = res_sens_rob[1,2] in 4
replace ci_high = res_sens_rob[1,3] in 4
replace p_value = res_sens_rob[1,4] in 4
replace tau2 = res_sens_rob[1,6] in 4
replace i2 = res_sens_rob[1,7] in 4
replace q_stat = res_sens_rob[1,8] in 4
replace notes = "Sensitivity excluding High RoB" in 4

* Row 5: Estimator sensitivity DL
replace analysis_id = "TE_FLATUS_DL_WALD" in 5
replace model_spec = "MD Hours (DL Wald unadjusted)" in 5
replace k = res_flatus_dl_wald[1,5] in 5
replace estimate = res_flatus_dl_wald[1,1] in 5
replace ci_low = res_flatus_dl_wald[1,2] in 5
replace ci_high = res_flatus_dl_wald[1,3] in 5
replace p_value = res_flatus_dl_wald[1,4] in 5
replace tau2 = res_flatus_dl_wald[1,6] in 5
replace i2 = res_flatus_dl_wald[1,7] in 5
replace q_stat = res_flatus_dl_wald[1,8] in 5
replace notes = "Unadjusted DerSimonian-Laird model" in 5

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetE_flatus.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetE_flatus.csv", replace
list, clean

di as txt _n "SUCCESS: Target E analyses completed and exported."
log close
