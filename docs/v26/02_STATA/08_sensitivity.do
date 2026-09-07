* ==============================================================================
* 08_sensitivity.do: Comprehensive Sensitivity & Leave-One-Out Analyses
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/08_sensitivity.log", replace

di as txt "=================================================================="
di as txt "08: SENSITIVITY ANALYSES & LEAVE-ONE-OUT INFLUENCE DIAGNOSTICS"
di as txt "=================================================================="

* ------------------------------------------------------------------------------
* PART 1: LEAVE-ONE-OUT FOR PRIMARY 24-H OPIOID (k=6)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
keep if inc_primary == 1

meta set md_mme se_mme, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

di as txt _n "=== FULL PRIMARY 24-H MODEL (k=6) [REML + KH] ==="
meta summarize, random(reml) se(kh)

di as txt _n "=== LEAVE-ONE-OUT ANALYSIS: PRIMARY 24-H OPIOID ==="
* Stata meta leaveoneout
meta summarize, random(reml) se(kh) leaveoneout

* Export leave-one-out forest plot / graph
meta forestplot, leaveoneout ///
    title("Leave-One-Out Influence: Primary 24-h Opioid (mg IV MME)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/loo_opioid24_primary.png", width(1800) replace

* ------------------------------------------------------------------------------
* PART 2: ESTIMATOR SENSITIVITY GRID FOR PRIMARY 24-H OPIOID
* ------------------------------------------------------------------------------
di as txt _n "=== ESTIMATOR SENSITIVITY GRID: PRIMARY 24-H OPIOID ==="

* 1. REML + KH (Reference)
meta summarize, random(reml) se(kh)
matrix est_reml_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 2. REML Wald (unadjusted)
meta summarize, random(reml)
matrix est_reml_wald = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 3. DL + KH
meta summarize, random(dl) se(kh)
matrix est_dl_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 4. DL Wald (unadjusted)
meta summarize, random(dl)
matrix est_dl_wald = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 5. Empirical Bayes (EB) + KH
meta summarize, random(ebayes) se(kh)
matrix est_eb_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 6. Paule-Mandel (PM) + KH
meta summarize, random(pmandel) se(kh)
matrix est_pm_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

* 7. Fixed-effect (common effect) model
meta summarize, common
matrix est_fixed = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), 0, 0)

* ------------------------------------------------------------------------------
* PART 3: LEAVE-ONE-OUT FOR TARGET A (0-48 H CUMULATIVE OPIOID, k=3)
* ------------------------------------------------------------------------------
use "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta", clear
keep if include_strict == 1

meta set md_mme se_mme, studylabel(study) eslabel("Mean Difference (mg IV MME)")

di as txt _n "=== FULL TARGET A MODEL (k=3) [REML + KH] ==="
meta summarize, random(reml) se(kh)

di as txt _n "=== LEAVE-ONE-OUT ANALYSIS: TARGET A ==="
meta summarize, random(reml) se(kh) leaveoneout

meta forestplot, leaveoneout ///
    title("Leave-One-Out Influence: Target A (0-48 h Cumulative Opioid)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/loo_targetA_48h.png", width(1800) replace

* ------------------------------------------------------------------------------
* PART 4: EXPORT ESTIMATOR SENSITIVITY GRID TABLE
* ------------------------------------------------------------------------------
clear
set obs 7

gen estimator = ""
gen se_adj = ""
gen k = .
gen estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen note = ""

replace estimator = "REML" in 1
replace se_adj = "Hartung-Knapp (KH)" in 1
replace k = est_reml_kh[1,5] in 1
replace estimate = est_reml_kh[1,1] in 1
replace ci_low = est_reml_kh[1,2] in 1
replace ci_high = est_reml_kh[1,3] in 1
replace p_value = est_reml_kh[1,4] in 1
replace tau2 = est_reml_kh[1,6] in 1
replace i2 = est_reml_kh[1,7] in 1
replace note = "PRIMARY AUTHORITATIVE BENCHMARK" in 1

replace estimator = "REML" in 2
replace se_adj = "Wald (unadjusted)" in 2
replace k = est_reml_wald[1,5] in 2
replace estimate = est_reml_wald[1,1] in 2
replace ci_low = est_reml_wald[1,2] in 2
replace ci_high = est_reml_wald[1,3] in 2
replace p_value = est_reml_wald[1,4] in 2
replace tau2 = est_reml_wald[1,6] in 2
replace i2 = est_reml_wald[1,7] in 2
replace note = "Unadjusted standard errors" in 2

replace estimator = "DerSimonian-Laird (DL)" in 3
replace se_adj = "Hartung-Knapp (KH)" in 3
replace k = est_dl_kh[1,5] in 3
replace estimate = est_dl_kh[1,1] in 3
replace ci_low = est_dl_kh[1,2] in 3
replace ci_high = est_dl_kh[1,3] in 3
replace p_value = est_dl_kh[1,4] in 3
replace tau2 = est_dl_kh[1,6] in 3
replace i2 = est_dl_kh[1,7] in 3
replace note = "DL moments estimator with KH" in 3

replace estimator = "DerSimonian-Laird (DL)" in 4
replace se_adj = "Wald (unadjusted)" in 4
replace k = est_dl_wald[1,5] in 4
replace estimate = est_dl_wald[1,1] in 4
replace ci_low = est_dl_wald[1,2] in 4
replace ci_high = est_dl_wald[1,3] in 4
replace p_value = est_dl_wald[1,4] in 4
replace tau2 = est_dl_wald[1,6] in 4
replace i2 = est_dl_wald[1,7] in 4
replace note = "Demonstrates artificial significance under unadjusted DL" in 4

replace estimator = "Empirical Bayes (EB)" in 5
replace se_adj = "Hartung-Knapp (KH)" in 5
replace k = est_eb_kh[1,5] in 5
replace estimate = est_eb_kh[1,1] in 5
replace ci_low = est_eb_kh[1,2] in 5
replace ci_high = est_eb_kh[1,3] in 5
replace p_value = est_eb_kh[1,4] in 5
replace tau2 = est_eb_kh[1,6] in 5
replace i2 = est_eb_kh[1,7] in 5
replace note = "Iterative empirical Bayes estimator" in 5

replace estimator = "Paule-Mandel (PM)" in 6
replace se_adj = "Hartung-Knapp (KH)" in 6
replace k = est_pm_kh[1,5] in 6
replace estimate = est_pm_kh[1,1] in 6
replace ci_low = est_pm_kh[1,2] in 6
replace ci_high = est_pm_kh[1,3] in 6
replace p_value = est_pm_kh[1,4] in 6
replace tau2 = est_pm_kh[1,6] in 6
replace i2 = est_pm_kh[1,7] in 6
replace note = "Paule-Mandel estimator" in 6

replace estimator = "Fixed-effect (Common)" in 7
replace se_adj = "None (Common effect)" in 7
replace k = est_fixed[1,5] in 7
replace estimate = est_fixed[1,1] in 7
replace ci_low = est_fixed[1,2] in 7
replace ci_high = est_fixed[1,3] in 7
replace p_value = est_fixed[1,4] in 7
replace tau2 = 0 in 7
replace i2 = 0 in 7
replace note = "Common-effect inverse-variance model" in 7

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_sensitivity_estimators_grid.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_sensitivity_estimators_grid.csv", replace
list, clean

di as txt _n "SUCCESS: Sensitivity analyses completed and exported."
log close
