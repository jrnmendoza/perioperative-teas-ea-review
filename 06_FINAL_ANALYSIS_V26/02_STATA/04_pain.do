* ==============================================================================
* 04_pain.do: Target C (Pain Intensity at Rest ~24 h)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_C_pain24h.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/04_pain.log", replace

di as txt "=================================================================="
di as txt "04: TARGET C: PAIN INTENSITY AT REST AROUND 24 H POSTOPERATIVELY"
di as txt "Model: Random-Effects REML + Hartung-Knapp (se(kh))"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_C_pain24h.dta", clear
describe

* List Target C studies
di as txt _n "=== TARGET C STUDIES (STRICT AT REST ~24 H, k=2) ==="
list lock_id study comparison_id include_strict n_i mean_i sd_i n_c mean_c sd_c md se unit result_rob, clean

* Declare Meta-Analysis Setting for Pain VAS 0-10
meta set md se, studylabel(study) eslabel("Mean Difference (VAS 0-10)")

* ------------------------------------------------------------------------------
* 1. PRINCIPAL TARGET C MODEL (k=2: Xing 2022, Liu 2021) [REML + KH]
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. PRINCIPAL TARGET C MODEL: STRICT AT REST ~24 H (k=2) [REML + KH]"
di as txt "Note: Both studies evaluated on 0-10 VAS; both have High result-level RoB."
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh)
matrix res_pain = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ------------------------------------------------------------------------------
* 2. ESTIMATOR SENSITIVITY: DL Model
* ------------------------------------------------------------------------------
meta summarize, random(dl) se(kh)
meta summarize, random(dl)

* ------------------------------------------------------------------------------
* 3. GENERATE AND EXPORT FOREST PLOT
* ------------------------------------------------------------------------------
meta forestplot, ///
    title("TARGET C: Postoperative Pain Intensity at Rest (~24 h)", size(medium)) ///
    subtitle("Strict At-Rest Pain (StataNow 19.5 BE: REML + Hartung-Knapp, k=2)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetC_pain24h.png", width(1800) replace

* ------------------------------------------------------------------------------
* 4. EXPORT SUMMARY ESTIMATES TO STATA DATASET & CSV
* ------------------------------------------------------------------------------
clear
set obs 1
gen analysis_id = "TC_REST_PAIN24"
gen outcome = "Pain at rest ~24 h (VAS 0-10)"
gen stratum = "Strict Pain at Rest ~24h (Xing 2022, Liu 2021)"
gen k = res_pain[1,5]
gen estimate = res_pain[1,1]
gen ci_low = res_pain[1,2]
gen ci_high = res_pain[1,3]
gen p_value = res_pain[1,4]
gen tau2 = res_pain[1,6]
gen i2 = res_pain[1,7]
gen q_stat = res_pain[1,8]
gen model = "REML + Hartung-Knapp"

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetC_pain24h.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetC_pain24h.csv", replace
list, clean

di as txt _n "SUCCESS: Target C analyses completed and exported."
log close
