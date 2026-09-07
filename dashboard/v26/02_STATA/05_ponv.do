* ==============================================================================
* 05_ponv.do: Target D (Postoperative Nausea and Vomiting - Stratified)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_D_ponv.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/05_ponv.log", replace

di as txt "=================================================================="
di as txt "05: TARGET D: STRATIFIED POSTOPERATIVE NAUSEA AND VOMITING (PONV)"
di as txt "Model: Binary Risk Ratio (RR), REML + Hartung-Knapp"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_D_ponv.dta", clear
describe

* List all Target D studies and strata
di as txt _n "=== ALL TARGET D STUDIES AND STRATA ==="
list lock_id study endpoint_stratum include_strict include_sensitivity events_i n_i events_c n_c result_rob, clean

* Calculate log RR and SE
gen p_i = events_i / n_i
gen p_c = events_c / n_c
gen rr = p_i / p_c
gen lnrr = ln(rr)
gen se_lnrr = sqrt((1/events_i - 1/n_i) + (1/events_c - 1/n_c))

* Declare meta setting
meta set lnrr se_lnrr, studylabel(study) eslabel("Risk Ratio (log scale)")

* ------------------------------------------------------------------------------
* 1. STRATUM 1: COMPOSITE PONV 0-24 H (k=2: Zheng 2025, Lu 2021)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. COMPOSITE PONV 0-24 H (k=2: Zheng 2025, Lu 2021)"
di as txt "------------------------------------------------------------------"
meta summarize if endpoint_stratum == "D_PONV_0-24h", random(reml) se(kh) eform
matrix res_ponv24 = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 2. STRATUM 2: COMPOSITE PONV 0-48 H (k=2: Xiong 2021, Xing 2022)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. COMPOSITE PONV 0-48 H (k=2: Xiong 2021, Xing 2022)"
di as txt "------------------------------------------------------------------"
meta summarize if endpoint_stratum == "D_PONV_0-48h", random(reml) se(kh) eform
matrix res_ponv48 = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 3. STRATUM 3: NAUSEA 0-24 H (k=2: Yang 2024, Ma 2026)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. NAUSEA ALONE 0-24 H (k=2: Yang 2024, Ma 2026)"
di as txt "------------------------------------------------------------------"
meta summarize if endpoint_stratum == "D_nausea_0-24h", random(reml) se(kh) eform
matrix res_naus24 = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 4. STRATUM 4: NAUSEA 0-48 H (k=1: Luo 2026) -> Single study
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "4. NAUSEA ALONE 0-48 H (k=1: Luo 2026): NOT POOLED (Single Study)"
di as txt "------------------------------------------------------------------"
list study events_i n_i events_c n_c rr if endpoint_stratum == "D_nausea_0-48h", clean

* ------------------------------------------------------------------------------
* 5. STRATUM 5: VOMITING 0-24 H (k=2: Yang 2024, Ma 2026)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "5. VOMITING ALONE 0-24 H (k=2: Yang 2024, Ma 2026)"
di as txt "------------------------------------------------------------------"
meta summarize if endpoint_stratum == "D_vomiting_0-24h", random(reml) se(kh) eform
matrix res_vom24 = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 6. STRATUM 6: VOMITING 0-48 H (k=1: Luo 2026) -> Single study
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "6. VOMITING ALONE 0-48 H (k=1: Luo 2026): NOT POOLED (Single Study)"
di as txt "------------------------------------------------------------------"
list study events_i n_i events_c n_c rr if endpoint_stratum == "D_vomiting_0-48h", clean

* ------------------------------------------------------------------------------
* 7. GENERATE AND EXPORT FOREST PLOT
* ------------------------------------------------------------------------------
meta forestplot if include_strict == 1, subgroup(endpoint_stratum) eform ///
    title("TARGET D: Postoperative Nausea & Vomiting (Stratified)", size(medium)) ///
    subtitle("Strict Stratified Strata (StataNow 19.5 BE: REML + Hartung-Knapp)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetD_ponv.png", width(1800) replace

* ------------------------------------------------------------------------------
* 8. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 6
gen analysis_id = ""
gen outcome = "Postoperative Nausea & Vomiting (PONV)"
gen stratum = ""
gen k = .
gen rr_estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen q_stat = .
gen model = ""

replace analysis_id = "TD_PONV_0_24H" in 1
replace stratum = "Composite PONV 0-24h (Zheng 2025, Lu 2021)" in 1
replace rr_estimate = res_ponv24[1,1] in 1
replace ci_low      = res_ponv24[1,2] in 1
replace ci_high     = res_ponv24[1,3] in 1
replace p_value     = res_ponv24[1,4] in 1
replace k           = res_ponv24[1,5] in 1
replace tau2        = res_ponv24[1,6] in 1
replace i2          = res_ponv24[1,7] in 1
replace q_stat      = res_ponv24[1,8] in 1
replace model       = "REML + Hartung-Knapp" in 1

replace analysis_id = "TD_PONV_0_48H" in 2
replace stratum = "Composite PONV 0-48h (Xiong 2021, Xing 2022)" in 2
replace rr_estimate = res_ponv48[1,1] in 2
replace ci_low      = res_ponv48[1,2] in 2
replace ci_high     = res_ponv48[1,3] in 2
replace p_value     = res_ponv48[1,4] in 2
replace k           = res_ponv48[1,5] in 2
replace tau2        = res_ponv48[1,6] in 2
replace i2          = res_ponv48[1,7] in 2
replace q_stat      = res_ponv48[1,8] in 2
replace model       = "REML + Hartung-Knapp" in 2

replace analysis_id = "TD_NAUSEA_0_24H" in 3
replace stratum = "Nausea 0-24h (Yang 2024, Ma 2026)" in 3
replace rr_estimate = res_naus24[1,1] in 3
replace ci_low      = res_naus24[1,2] in 3
replace ci_high     = res_naus24[1,3] in 3
replace p_value     = res_naus24[1,4] in 3
replace k           = res_naus24[1,5] in 3
replace tau2        = res_naus24[1,6] in 3
replace i2          = res_naus24[1,7] in 3
replace q_stat      = res_naus24[1,8] in 3
replace model       = "REML + Hartung-Knapp" in 3

replace analysis_id = "TD_NAUSEA_0_48H" in 4
replace stratum = "Nausea 0-48h (Luo 2026 alone)" in 4
replace rr_estimate = (24/138) / (53/139) in 4
replace ci_low      = exp(ln((24/138)/(53/139)) - 1.96*sqrt(1/24 - 1/138 + 1/53 - 1/139)) in 4
replace ci_high     = exp(ln((24/138)/(53/139)) + 1.96*sqrt(1/24 - 1/138 + 1/53 - 1/139)) in 4
replace p_value     = . in 4
replace k           = 1 in 4
replace model       = "Single study (Not pooled)" in 4

replace analysis_id = "TD_VOMIT_0_24H" in 5
replace stratum = "Vomiting 0-24h (Yang 2024, Ma 2026)" in 5
replace rr_estimate = res_vom24[1,1] in 5
replace ci_low      = res_vom24[1,2] in 5
replace ci_high     = res_vom24[1,3] in 5
replace p_value     = res_vom24[1,4] in 5
replace k           = res_vom24[1,5] in 5
replace tau2        = res_vom24[1,6] in 5
replace i2          = res_vom24[1,7] in 5
replace q_stat      = res_vom24[1,8] in 5
replace model       = "REML + Hartung-Knapp" in 5

replace analysis_id = "TD_VOMIT_0_48H" in 6
replace stratum = "Vomiting 0-48h (Luo 2026 alone)" in 6
replace rr_estimate = (9/138) / (27/139) in 6
replace ci_low      = exp(ln((9/138)/(27/139)) - 1.96*sqrt(1/9 - 1/138 + 1/27 - 1/139)) in 6
replace ci_high     = exp(ln((9/138)/(27/139)) + 1.96*sqrt(1/9 - 1/138 + 1/27 - 1/139)) in 6
replace p_value     = . in 6
replace k           = 1 in 6
replace model       = "Single study (Not pooled)" in 6

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetD_ponv.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetD_ponv.csv", replace
list, clean

di as txt _n "SUCCESS: Target D analyses completed and exported."
log close
