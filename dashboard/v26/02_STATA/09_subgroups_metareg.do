* ==============================================================================
* 09_subgroups_metareg.do: Subgroup Analyses and Meta-Regression Methodological Audit
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/09_subgroups_metareg.log", replace

di as txt "=================================================================="
di as txt "09: SUBGROUP ANALYSES AND META-REGRESSION METHODOLOGICAL AUDIT"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
keep if inc_primary == 1

meta set md_mme se_mme, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

* ------------------------------------------------------------------------------
* 1. MODALITY SUBGROUP ANALYSIS: TEAS VS EA (k=7)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. MODALITY SUBGROUP ANALYSIS: TEAS vs EA (k=7) [REML + Hartung-Knapp]"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) subgroup(modality)

* Subgroup forest plot
meta forestplot, subgroup(modality) ///
    title("Primary 24-h Opioid Consumption by Modality (mg IV MME)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp (k=7)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_subgroup_modality_primary.png", width(1800) replace

* ------------------------------------------------------------------------------
* 2. COMPARATOR TYPE SUBGROUP: SHAM VS USUAL CARE (k=7)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. COMPARATOR TYPE SUBGROUP: SHAM vs USUAL CARE (k=7)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) subgroup(comparator_type)

* ------------------------------------------------------------------------------
* 3. META-REGRESSION METHODOLOGICAL ASSESSMENT
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. META-REGRESSION METHODOLOGICAL ASSESSMENT & POWER AUDIT"
di as txt "According to Cochrane Handbook (Section 10.11.4), meta-regression"
di as txt "should generally NOT be considered unless there are at least 10 studies"
di as txt "for each study-level covariate. Here, k=7 (TEAS k=4, EA k=3)."
di as txt "Executing exploratory meta-regression on modality for completeness:"
di as txt "------------------------------------------------------------------"

* Capture each modality stratum FROM THE DATA rather than transcribing it.
* These rows were previously hardcoded literals (estimate = -6.69786 etc.), which
* silently failed to track the underlying dataset - exposed when the sufentanil
* conversion factor was corrected on 2026-09-07 and OP24_TEAS_SHAM moved while
* SUB_MODALITY_TEAS did not. Now computed, so the two can never diverge again.
meta summarize if modality == "TEAS", random(reml) se(kh)
matrix res_teas = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

meta summarize if modality == "EA", random(reml) se(kh)
matrix res_ea = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))

encode modality, gen(modality_code)
* 1=EA, 2=TEAS
meta regress i.modality_code, random(reml) se(kh)
matrix res_metareg = (r(table)[1,2], r(table)[2,2], r(table)[5,2], r(table)[6,2], r(table)[4,2], r(N), r(tau2), r(I2))

di as txt _n "AUDIT CONCLUSION: Meta-regression with k=7 is severely underpowered"
di as txt "and subject to extreme risk of false-positive / false-negative conclusions."
di as txt "Stratified subgroup presentation with Hartung-Knapp adjustment is authoritative."

* ------------------------------------------------------------------------------
* 4. EXPORT SUBGROUP AND META-REGRESSION AUDIT SUMMARY
* ------------------------------------------------------------------------------
clear
set obs 3

gen analysis_id = ""
gen analysis_type = ""
gen subgroup_variable = ""
gen k = .
gen estimate = .
gen ci_low = .
gen ci_high = .
gen p_value = .
gen tau2 = .
gen i2 = .
gen notes = ""

* Row 1: TEAS Stratum
replace analysis_id = "SUB_MODALITY_TEAS" in 1
replace analysis_type = "Subgroup" in 1
replace subgroup_variable = "Modality: TEAS (Chen 1998, Chen 2020, He 2026)" in 1
replace k = res_teas[1,5] in 1
replace estimate = res_teas[1,1] in 1
replace ci_low = res_teas[1,2] in 1
replace ci_high = res_teas[1,3] in 1
replace p_value = res_teas[1,4] in 1
replace tau2 = res_teas[1,6] in 1
replace i2 = res_teas[1,7] in 1
replace notes = "REML + Hartung-Knapp (t df=2)" in 1

* Row 2: EA Stratum
replace analysis_id = "SUB_MODALITY_EA" in 2
replace analysis_type = "Subgroup" in 2
replace subgroup_variable = "Modality: EA (El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024)" in 2
replace k = res_ea[1,5] in 2
replace estimate = res_ea[1,1] in 2
replace ci_low = res_ea[1,2] in 2
replace ci_high = res_ea[1,3] in 2
replace p_value = res_ea[1,4] in 2
replace tau2 = res_ea[1,6] in 2
replace i2 = res_ea[1,7] in 2
replace notes = "REML + Hartung-Knapp (t df=2)" in 2

* Row 3: Meta-regression on Modality
replace analysis_id = "METAREG_MODALITY" in 3
replace analysis_type = "Meta-regression" in 3
replace subgroup_variable = "Modality: TEAS vs EA (reference: EA)" in 3
replace k = res_metareg[1,6] in 3
replace estimate = res_metareg[1,1] in 3
replace ci_low = res_metareg[1,3] in 3
replace ci_high = res_metareg[1,4] in 3
replace p_value = res_metareg[1,5] in 3
replace tau2 = res_metareg[1,7] in 3
replace i2 = res_metareg[1,8] in 3
replace notes = "Difference between TEAS and EA; underpowered (k=7 < 10)" in 3

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_subgroups_metareg.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_subgroups_metareg.csv", replace
list, clean

di as txt _n "SUCCESS: Subgroup and meta-regression analyses completed and exported."
log close
