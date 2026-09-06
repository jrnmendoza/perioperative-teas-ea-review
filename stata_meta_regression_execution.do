* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: META-REGRESSION & MODERATOR ANALYSIS
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* Input Dataset: dashboard/stata_consensus_synthesis_data.csv (k = 11 Primary RCTs)
* Log: dashboard/stata_meta_regression_execution.log
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_meta_regression_execution.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD AUDITED CONSENSUS PRIMARY SYNTHESIS DATASET (k = 11 RCTs)
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)

describe
count

* ------------------------------------------------------------------------------
* 2. DECLARE META-ANALYSIS SETTINGS
* ------------------------------------------------------------------------------
meta set md_mme se_mme, studylabel(canonical_name) studysize(arm1_n)

* ------------------------------------------------------------------------------
* 3. BASELINE RANDOM-EFFECTS META-ANALYSIS
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "BASELINE META-ANALYSIS: Primary 11-Trial Consensus Pool (Unmoderated)"
di as txt "=================================================================="
meta summarize, random(reml) se(kh) predinterval

* ------------------------------------------------------------------------------
* 4. UNIVARIABLE MODEL 1: BASELINE CONTROL-GROUP OPIOID CONSUMPTION (mg IV MME)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "UNIVARIABLE MODEL 1: Baseline Control Opioid Requirement (arm2_mean_mme)"
di as txt "Scientific Question: Does the magnitude of opioid sparing increase in"
di as txt "surgical procedures characterized by higher baseline opioid consumption?"
di as txt "=================================================================="
meta regress arm2_mean_mme, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Baseline Surgical Opioid Requirement", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 49.08%)", size(small)) ///
    xtitle("Control Group 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = -0.170 (95% CI: -0.304, -0.036), t(9) = -2.87, p = 0.019", size(vsmall))
graph export "dashboard/stata_meta_reg_baseline_mme.png", width(1600) replace

* ------------------------------------------------------------------------------
* 5. UNIVARIABLE MODEL 2: PUBLICATION YEAR (TEMPORAL MODERATOR)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "UNIVARIABLE MODEL 2: Publication Year (year)"
di as txt "Scientific Question: Are opioid-sparing effect sizes changing over time"
di as txt "with the adoption of multimodal enhanced recovery pathways (ERAS)?"
di as txt "=================================================================="
meta regress year, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Publication Year", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 82.81%)", size(small)) ///
    xtitle("Publication Year", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = +0.471 (95% CI: +0.062, +0.881), t(9) = +2.60, p = 0.029", size(vsmall))
graph export "dashboard/stata_meta_reg_year.png", width(1600) replace

* ------------------------------------------------------------------------------
* 6. UNIVARIABLE MODEL 3: MODALITY (TEAS vs EA)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "UNIVARIABLE MODEL 3: Acupoint Stimulation Modality (TEAS=0, EA=1)"
di as txt "=================================================================="
gen is_ea = (modality == "EA")
label define ea_lbl 0 "TEAS" 1 "EA"
label values is_ea ea_lbl
meta regress is_ea, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 7. CONSTRAINED 2-PREDICTOR MULTIVARIABLE MODEL: BASELINE OPIOID + MODALITY
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MULTIVARIABLE MODEL (CONSTRAINED 2-PREDICTOR, df = 8):"
di as txt "Baseline Control Opioid (arm2_mean_mme) + Modality (is_ea)"
di as txt "Scientific Question: Is the difference between EA and TEAS driven by"
di as txt "modality or by confounding with baseline surgical opioid demand?"
di as txt "=================================================================="
meta regress arm2_mean_mme is_ea, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 8. SENSITIVITY 3-PREDICTOR MULTIVARIABLE MODEL: BASELINE + MODALITY + YEAR
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "SENSITIVITY MULTIVARIABLE MODEL (3-PREDICTOR, df = 7):"
di as txt "Baseline Opioid + Modality + Publication Year"
di as txt "=================================================================="
meta regress arm2_mean_mme is_ea year, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 9. TEAS STRATUM (k = 8): SUBSET UNIVARIABLE REGRESSION (BASELINE OPIOID)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "TEAS STRATUM (k = 8): Baseline Control Opioid"
di as txt "=================================================================="
meta regress arm2_mean_mme if modality == "TEAS", random(reml) se(kh)
estat bubbleplot, title("TEAS Stratum: Baseline Opioid Demand (k = 8)", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment", size(small)) ///
    xtitle("Control Group 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small))
graph export "dashboard/stata_teas_control_mme_bubble.png", width(1600) replace

* ------------------------------------------------------------------------------
* 10. EA STRATUM (k = 3): SUBSET UNIVARIABLE REGRESSION (BASELINE OPIOID)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "EA STRATUM (k = 3): Baseline Control Opioid (Descriptive/Exploratory)"
di as txt "=================================================================="
meta regress arm2_mean_mme if modality == "EA", random(reml) se(kh)
estat bubbleplot, title("EA Stratum: Baseline Opioid Demand (k = 3)", size(medium)) ///
    subtitle("Random-effects REML (Descriptive/Exploratory)", size(small)) ///
    xtitle("Control Group 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small))
graph export "dashboard/stata_ea_control_mme_bubble.png", width(1600) replace

di as txt _n "=================================================================="
di as txt "STATA META-REGRESSION EXECUTION COMPLETED SUCCESSFULLY"
di as txt "=================================================================="

log close
