* ==============================================================================
* 01_opioid24_primary.do: Primary 24-h Postoperative Opioid Consumption Analysis
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/01_opioid24_primary.log", replace

di as txt "=================================================================="
di as txt "01: PRIMARY OPIOID OUTCOME: 24-H CUMULATIVE POSTOPERATIVE OPIOID"
di as txt "Model: Random-Effects REML + Hartung-Knapp (se(kh))"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
describe

* List the 6 Strict Primary Studies
di as txt _n "=== STRICT PRIMARY STUDIES (k = 6) ==="
list study_unit modality comparator_type n_i mean_i_mme sd_i_mme n_c mean_c_mme sd_c_mme md_mme se_mme rob_overall if inc_primary == 1, clean

* Declare Meta-Analysis Setting for MME
meta set md_mme se_mme if inc_primary == 1, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

* ------------------------------------------------------------------------------
* 1. PRINCIPAL PRIMARY MODEL: Strict Direct k=6 Trials (REML + Hartung-Knapp)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. PRINCIPAL PRIMARY MODEL: STRICT DIRECT k=6 (REML + Hartung-Knapp)"
di as txt "------------------------------------------------------------------"
meta summarize if inc_primary == 1, random(reml) se(kh) predinterval
matrix res_prim = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 2. MODALITY STRATIFIED: TEAS vs Sham (k=3 Trials)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. MODALITY STRATUM: TEAS vs Sham (k=3 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if inc_primary == 1 & modality == "TEAS", random(reml) se(kh) predinterval
matrix res_teas = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 3. MODALITY STRATIFIED: EA vs Control / Sham (k=3 Trials)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. MODALITY STRATUM: EA vs Control / Sham (k=3 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if inc_primary == 1 & modality == "EA", random(reml) se(kh) predinterval
matrix res_ea = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 4. SENSITIVITY: Exclude High Risk of Bias (El-Rakshy 2009) -> k=5 Trials
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "4. SENSITIVITY: Exclude High RoB (El-Rakshy 2009) -> k=5 Trials"
di as txt "------------------------------------------------------------------"
meta summarize if inc_primary == 1 & rob_overall != "High", random(reml) se(kh) predinterval
matrix res_lowrob = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 5. ESTIMATOR SENSITIVITY: DerSimonian-Laird (DL) Model (k=6)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "5. ESTIMATOR SENSITIVITY: DerSimonian-Laird (DL) Model (k=6)"
di as txt "------------------------------------------------------------------"
meta summarize if inc_primary == 1, random(dl) se(kh)
meta summarize if inc_primary == 1, random(dl)

* ------------------------------------------------------------------------------
* 6. STANDARDIZED MEAN DIFFERENCE (Hedges' g SMD): Strict k=6 Trials
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "6. STANDARDIZED MEAN DIFFERENCE (Hedges' g): Strict k=6 Trials"
di as txt "------------------------------------------------------------------"
meta set hedges_g hedges_se if inc_primary == 1, studylabel(study_unit) eslabel("Standardized Mean Difference (Hedges' g)")
meta summarize if inc_primary == 1, random(reml) se(kh) predinterval
matrix res_smd = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 7. GENERATE AND EXPORT FOREST PLOTS
* ------------------------------------------------------------------------------
* Reset to MME
meta set md_mme se_mme if inc_primary == 1, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

meta forestplot if inc_primary == 1, subgroup(modality) ///
    title("PRIMARY OPIOID OUTCOME: 24-h Cumulative Consumption", size(medium)) ///
    subtitle("Authoritative v26 Lock (StataNow 19.5 BE: REML + Hartung-Knapp, k=6)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_opioid24_primary_mme.png", width(1800) replace

* Export SMD Forest Plot
meta set hedges_g hedges_se if inc_primary == 1, studylabel(study_unit) eslabel("Standardized Mean Difference (Hedges' g)")
meta forestplot if inc_primary == 1, subgroup(modality) ///
    title("PRIMARY OPIOID OUTCOME (SMD): 24-h Cumulative Consumption", size(medium)) ///
    subtitle("Authoritative v26 Lock (StataNow 19.5 BE: REML + Hartung-Knapp, k=6)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_opioid24_primary_smd.png", width(1800) replace

* ------------------------------------------------------------------------------
* 8. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 5
gen analysis_id = ""
gen outcome = "24-h Cumulative Postoperative Opioid"
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

replace analysis_id = "OP24_PRIM_COMB" in 1
replace stratum = "Combined Strict Primary (TEAS + EA)" in 1
replace estimate = res_prim[1,1] in 1
replace ci_low   = res_prim[1,2] in 1
replace ci_high  = res_prim[1,3] in 1
replace p_value  = res_prim[1,4] in 1
replace k        = res_prim[1,5] in 1
replace tau2     = res_prim[1,6] in 1
replace i2       = res_prim[1,7] in 1
replace q_stat   = res_prim[1,8] in 1

replace analysis_id = "OP24_TEAS_SHAM" in 2
replace stratum = "TEAS vs Sham" in 2
replace estimate = res_teas[1,1] in 2
replace ci_low   = res_teas[1,2] in 2
replace ci_high  = res_teas[1,3] in 2
replace p_value  = res_teas[1,4] in 2
replace k        = res_teas[1,5] in 2
replace tau2     = res_teas[1,6] in 2
replace i2       = res_teas[1,7] in 2
replace q_stat   = res_teas[1,8] in 2

replace analysis_id = "OP24_EA_CTRL" in 3
replace stratum = "EA vs Control/Sham" in 3
replace estimate = res_ea[1,1] in 3
replace ci_low   = res_ea[1,2] in 3
replace ci_high  = res_ea[1,3] in 3
replace p_value  = res_ea[1,4] in 3
replace k        = res_ea[1,5] in 3
replace tau2     = res_ea[1,6] in 3
replace i2       = res_ea[1,7] in 3
replace q_stat   = res_ea[1,8] in 3

replace analysis_id = "OP24_LOWROB_ONLY" in 4
replace stratum = "Sensitivity: Low/Some Concerns RoB only" in 4
replace estimate = res_lowrob[1,1] in 4
replace ci_low   = res_lowrob[1,2] in 4
replace ci_high  = res_lowrob[1,3] in 4
replace p_value  = res_lowrob[1,4] in 4
replace k        = res_lowrob[1,5] in 4
replace tau2     = res_lowrob[1,6] in 4
replace i2       = res_lowrob[1,7] in 4
replace q_stat   = res_lowrob[1,8] in 4

replace analysis_id = "OP24_PRIM_SMD" in 5
replace stratum = "Standardized Mean Difference (Hedges g)" in 5
replace estimate = res_smd[1,1] in 5
replace ci_low   = res_smd[1,2] in 5
replace ci_high  = res_smd[1,3] in 5
replace p_value  = res_smd[1,4] in 5
replace k        = res_smd[1,5] in 5
replace tau2     = res_smd[1,6] in 5
replace i2       = res_smd[1,7] in 5
replace q_stat   = res_smd[1,8] in 5

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_opioid24_primary.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_opioid24_primary.csv", replace
list, clean

di as txt _n "SUCCESS: Primary 24-h opioid analyses completed and exported."
log close
