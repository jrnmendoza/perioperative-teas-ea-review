* ==============================================================================
* 07_targetF.do: Target F (Exploratory Outcomes)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: 06_FINAL_ANALYSIS_V26/01_DATA/target_F_exploratory.dta
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/07_targetF.log", replace

di as txt "=================================================================="
di as txt "07: TARGET F: EXPLORATORY AND OTHER OUTCOMES"
di as txt "Stratified Analyses: Intraoperative Titrated, Postop Delivered, Rescue Opioid"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/target_F_exploratory.dta", clear
describe

* ==============================================================================
* PART 1: INTRAOPERATIVE TITRATED OPIOID REQUIREMENTS (F-intra)
* ==============================================================================
preserve
keep if target == "F-intra"

* Harmonize remifentanil to ug
gen mean_i_ug = mean_i
gen sd_i_ug   = sd_i
gen mean_c_ug = mean_c
gen sd_c_ug   = sd_c

replace mean_i_ug = mean_i * 1000 if unit == "mg remifentanil"
replace sd_i_ug   = sd_i   * 1000 if unit == "mg remifentanil"
replace mean_c_ug = mean_c * 1000 if unit == "mg remifentanil"
replace sd_c_ug   = sd_c   * 1000 if unit == "mg remifentanil"

gen md_remi = mean_i_ug - mean_c_ug
gen se_remi = sqrt((sd_i_ug^2 / n_i) + (sd_c_ug^2 / n_c))

* Subset to studies reporting total remifentanil in ug/mg
gen is_remi_mass = (unit == "µg remifentanil" | unit == "mg remifentanil") & md_remi != .

di as txt _n "=== INTRAOPERATIVE REMIFENTANIL MASS STUDIES (ug) ==="
list study comparison_id n_i mean_i_ug sd_i_ug n_c mean_c_ug sd_c_ug md_remi se_remi result_rob if is_remi_mass == 1, clean

meta set md_remi se_remi if is_remi_mass == 1, studylabel(study) eslabel("Mean Difference (µg remifentanil)")
meta summarize, random(reml) se(kh)
matrix res_f_intra_remi = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* Forest plot for intraoperative remifentanil
meta forestplot, ///
    title("TARGET F: Intraoperative Titrated Remifentanil (µg)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetF_intraop_remi.png", width(1800) replace

restore

* ==============================================================================
* PART 2: POSTOPERATIVE DELIVERED MORPHINE DOSE (F-postop-dose)
* ==============================================================================
preserve
keep if target == "F-postop-dose"

di as txt _n "=== POSTOPERATIVE DELIVERED MORPHINE STUDIES ==="
list study comparison_id n_i mean_i sd_i n_c mean_c sd_c unit result_rob include_strict, clean

* Strict delivered morphine (Seevaunnamtum 2016, Lee 2011 High, Lee 2011 Low)
* Note: Lee 2011 has two intervention arms sharing the same control group.
* To avoid double-counting, evaluate Lee 2011 High vs Sham + Seevaunnamtum 2016:
gen md_postop = mean_i - mean_c
gen se_postop = sqrt((sd_i^2 / n_i) + (sd_c^2 / n_c))

gen include_postop_strict = (study == "Seevaunnamtum 2016" | comparison_id == "LEE11_HIGH_vs_SHAM_MORPH24")

meta set md_postop se_postop if include_postop_strict == 1, studylabel(study) eslabel("Mean Difference (mg IV morphine)")
meta summarize, random(reml) se(kh)
matrix res_f_postop_dose = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

restore

* ==============================================================================
* PART 3: RESCUE OPIOID REQUIREMENTS (BINARY INCIDENCE) (F-rescue-opioid)
* ==============================================================================
preserve
keep if target == "F-rescue-opioid" & unit == "participants" & events_i != . & events_c != .

di as txt _n "=== RESCUE OPIOID REQUIREMENT STUDIES (BINARY) ==="
list study comparison_id events_i n_i events_c n_c result_rob include_strict, clean

* Calculate log RR and SE
gen p_i = events_i / n_i
gen p_c = events_c / n_c
gen rr = p_i / p_c
gen lnrr = ln(rr)
gen se_lnrr = sqrt((1/events_i - 1/n_i) + (1/events_c - 1/n_c))

* Model 3A: Strict Rescue Opioid (k=4: Xie 2014, Yu 2020, Tu 2024, Zhou 2025)
meta set lnrr se_lnrr if include_strict == 1, studylabel(study) eslabel("Risk Ratio (log scale)")
meta summarize, random(reml) se(kh) eform
matrix res_f_rescue_strict = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* Model 3B: All available rescue opioid binary trials (k=5, including Liu 2026 burn)
meta set lnrr se_lnrr, studylabel(study) eslabel("Risk Ratio (log scale)")
meta summarize, random(reml) se(kh) eform
matrix res_f_rescue_all = (exp(r(theta)), exp(r(ci_lb)), exp(r(ci_ub)), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* Forest plot for rescue opioid
meta forestplot, ///
    title("TARGET F: Postoperative Rescue Opioid Requirement (RR)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp (k=5)", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_targetF_rescue_opioid.png", width(1800) replace

restore

* ==============================================================================
* PART 4: PCA DEMAND / BUTTON PRESSES (F-PCA)
* ==============================================================================
preserve
keep if target == "F-PCA" & mean_i != . & mean_c != .

di as txt _n "=== PCA DEMANDS / BUTTON PRESSES ==="
list study comparison_id n_i mean_i sd_i n_c mean_c sd_c unit result_rob, clean

gen md_pca = mean_i - mean_c
gen se_pca = sqrt((sd_i^2 / n_i) + (sd_c^2 / n_c))

* Standardized Mean Difference (Hedges' g) for PCA demands
gen s_pooled = sqrt( ((n_i - 1)*sd_i^2 + (n_c - 1)*sd_c^2) / (n_i + n_c - 2) )
gen d = (mean_i - mean_c) / s_pooled
gen j_corr = 1 - (3 / (4 * (n_i + n_c) - 9))
gen hedges_g = d * j_corr
gen hedges_se = sqrt( ((n_i + n_c) / (n_i * n_c)) + (hedges_g^2 / (2 * (n_i + n_c))) )

* Restrict to non-overlapping studies (Chen 2020 PCA attempts, He 2026, Liu 2021, Long 2025, Zheng 2025, Lee 2011 High, Lin 2002 High, Yeh 2010)
gen include_pca_synth = 0
replace include_pca_synth = 1 if comparison_id == "CHEN20_TEAS_vs_SHAM_PCAATT48"
replace include_pca_synth = 1 if comparison_id == "HEJIS26_TEAS_vs_CTRL_PCAATT24"
replace include_pca_synth = 1 if comparison_id == "LIU21_TEAS_vs_CTRL_PCAPRESS24"
replace include_pca_synth = 1 if comparison_id == "LONG25_TEAS_vs_CTRL_PCIAPRESS48"
replace include_pca_synth = 1 if comparison_id == "ZHENG25_TEAS_vs_SHAM_PCA_PRESS"
replace include_pca_synth = 1 if comparison_id == "LEE11_HIGH_vs_SHAM_PCADEMAND24"
replace include_pca_synth = 1 if comparison_id == "LIN02_HIGH_vs_SHAM_PCADEMAND24"
replace include_pca_synth = 1 if comparison_id == "YEH10_AES_vs_SHAM_PCAPUSH24"

meta set hedges_g hedges_se if include_pca_synth == 1, studylabel(study) eslabel("Standardized Mean Difference (Hedges' g)")
meta summarize, random(reml) se(kh)
matrix res_f_pca_smd = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

restore

* ==============================================================================
* PART 5: COMPILE AND EXPORT TARGET F SUMMARY ESTIMATES
* ==============================================================================
clear
set obs 5

gen analysis_id = ""
gen outcome = ""
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
gen notes = ""

* Row 1: Intraoperative Remifentanil (ug)
replace analysis_id = "TF_INTRA_REMI_UG" in 1
replace outcome = "Intraoperative titrated remifentanil" in 1
replace stratum = "Titrated remifentanil mass (µg) (Wu, Xing, Lu, Zheng, Guo, Liang, Pan)" in 1
replace k = res_f_intra_remi[1,5] in 1
replace estimate = res_f_intra_remi[1,1] in 1
replace ci_low = res_f_intra_remi[1,2] in 1
replace ci_high = res_f_intra_remi[1,3] in 1
replace p_value = res_f_intra_remi[1,4] in 1
replace tau2 = res_f_intra_remi[1,6] in 1
replace i2 = res_f_intra_remi[1,7] in 1
replace q_stat = res_f_intra_remi[1,8] in 1
replace model = "MD µg, REML + Hartung-Knapp" in 1
replace notes = "Intraoperative remifentanil requirement" in 1

* Row 2: Postop Delivered Morphine (mg)
replace analysis_id = "TF_POSTOP_DELIVERED_MORPH" in 2
replace outcome = "Postoperative delivered morphine" in 2
replace stratum = "Strict delivered IV morphine (Seevaunnamtum 2016, Lee 2011 High)" in 2
replace k = res_f_postop_dose[1,5] in 2
replace estimate = res_f_postop_dose[1,1] in 2
replace ci_low = res_f_postop_dose[1,2] in 2
replace ci_high = res_f_postop_dose[1,3] in 2
replace p_value = res_f_postop_dose[1,4] in 2
replace tau2 = res_f_postop_dose[1,6] in 2
replace i2 = res_f_postop_dose[1,7] in 2
replace q_stat = res_f_postop_dose[1,8] in 2
replace model = "MD mg, REML + Hartung-Knapp" in 2
replace notes = "Strict delivered morphine mass" in 2

* Row 3: Rescue Opioid Strict (RR)
replace analysis_id = "TF_RESCUE_OPIOID_STRICT" in 3
replace outcome = "Rescue opioid requirement" in 3
replace stratum = "Strict binary rescue (Xie 2014, Yu 2020, Tu 2024, Zhou 2025)" in 3
replace k = res_f_rescue_strict[1,5] in 3
replace estimate = res_f_rescue_strict[1,1] in 3
replace ci_low = res_f_rescue_strict[1,2] in 3
replace ci_high = res_f_rescue_strict[1,3] in 3
replace p_value = res_f_rescue_strict[1,4] in 3
replace tau2 = res_f_rescue_strict[1,6] in 3
replace i2 = res_f_rescue_strict[1,7] in 3
replace q_stat = res_f_rescue_strict[1,8] in 3
replace model = "RR, REML + Hartung-Knapp" in 3
replace notes = "Strict binary rescue requirement" in 3

* Row 4: Rescue Opioid All (RR)
replace analysis_id = "TF_RESCUE_OPIOID_ALL" in 4
replace outcome = "Rescue opioid requirement" in 4
replace stratum = "All binary rescue (including Liu 2026 burn)" in 4
replace k = res_f_rescue_all[1,5] in 4
replace estimate = res_f_rescue_all[1,1] in 4
replace ci_low = res_f_rescue_all[1,2] in 4
replace ci_high = res_f_rescue_all[1,3] in 4
replace p_value = res_f_rescue_all[1,4] in 4
replace tau2 = res_f_rescue_all[1,6] in 4
replace i2 = res_f_rescue_all[1,7] in 4
replace q_stat = res_f_rescue_all[1,8] in 4
replace model = "RR, REML + Hartung-Knapp" in 4
replace notes = "All reported binary rescue" in 4

* Row 5: PCA Demands SMD
replace analysis_id = "TF_PCA_DEMANDS_SMD" in 5
replace outcome = "PCA demands / button presses" in 5
replace stratum = "PCA button presses/demands across trials (SMD)" in 5
replace k = res_f_pca_smd[1,5] in 5
replace estimate = res_f_pca_smd[1,1] in 5
replace ci_low = res_f_pca_smd[1,2] in 5
replace ci_high = res_f_pca_smd[1,3] in 5
replace p_value = res_f_pca_smd[1,4] in 5
replace tau2 = res_f_pca_smd[1,6] in 5
replace i2 = res_f_pca_smd[1,7] in 5
replace q_stat = res_f_pca_smd[1,8] in 5
replace model = "SMD Hedges g, REML + Hartung-Knapp" in 5
replace notes = "Standardized mean difference in PCA demands" in 5

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetF_exploratory.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetF_exploratory.csv", replace
list, clean

di as txt _n "SUCCESS: Target F analyses completed and exported."
log close
