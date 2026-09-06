* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: META-REGRESSION & MODERATOR ANALYSIS
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* Input Dataset: dashboard/stata_extended_moderators.csv (k = 11 Primary RCTs)
* Log: dashboard/stata_meta_regression_execution.log
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_meta_regression_execution.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD AUDITED EXTENDED MODERATOR DATASET (k = 11 RCTs)
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)

* Merge extended indicators: is_multiphase, freq_dd, pct_female
gen is_multiphase = (canonical_name == "Zhang 2025" | canonical_name == "Yang 2024" | canonical_name == "Sim 2002" | canonical_name == "Seevaunnamtum 2016" | canonical_name == "Chen 2015 (Hyperalgesia)")
gen freq_dd = (canonical_name == "Zhang 2025" | canonical_name == "Sim 2002" | canonical_name == "He 2026 (hepatectomy/JIS)" | canonical_name == "Chen 1998" | canonical_name == "Chen 2020" | canonical_name == "Chen 2015 (Thyroidectomy)" | canonical_name == "Chen 2015 (Hyperalgesia)")
gen pct_female = 100.0 if canonical_name == "Zhang 2025"
replace pct_female = 67.8 if canonical_name == "Yang 2024"
replace pct_female = 100.0 if canonical_name == "Sim 2002"
replace pct_female = 100.0 if canonical_name == "Seevaunnamtum 2016"
replace pct_female = 22.1 if canonical_name == "He 2026 (hepatectomy/JIS)"
replace pct_female = 90.2 if canonical_name == "El-Rakshy 2009"
replace pct_female = 36.4 if canonical_name == "Coura 2011"
replace pct_female = 100.0 if canonical_name == "Chen 1998"
replace pct_female = 43.8 if canonical_name == "Chen 2020"
replace pct_female = 100.0 if canonical_name == "Chen 2015 (Thyroidectomy)"
replace pct_female = 100.0 if canonical_name == "Chen 2015 (Hyperalgesia)"

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
* 4. MODEL 1: BASELINE CONTROL-GROUP OPIOID CONSUMPTION (mg IV MME)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 1: Baseline Control Opioid Requirement (arm2_mean_mme)"
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
* 5. MODEL 2: PUBLICATION YEAR (TEMPORAL MODERATOR)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 2: Publication Year (year)"
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
* 6. MODEL 3: DEMOGRAPHIC SEX (% FEMALE PARTICIPANTS)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 3: Patient Sex (% Female Participants)"
di as txt "Scientific Question: Does the sex composition of the trial cohort"
di as txt "moderate the 24-h opioid-sparing effect of acupoint stimulation?"
di as txt "=================================================================="
meta regress pct_female, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Trial Sex Composition (% Female)", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 0.00%)", size(small)) ///
    xtitle("Proportion of Female Participants (% Female)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = -0.013 (95% CI: -0.191, +0.165), t(9) = -0.16, p = 0.875", size(vsmall))
graph export "dashboard/stata_meta_reg_sex.png", width(1600) replace

* ------------------------------------------------------------------------------
* 7. MODEL 4: STIMULATION TIMING (MULTI-PHASE VS PREOPERATIVE ONLY)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 4: Stimulation Timing (Multi-phase vs Preoperative only)"
di as txt "=================================================================="
meta regress is_multiphase, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 8. MODEL 5: ELECTRICAL FREQUENCY (DENSE-DISPERSE 2/100 HZ VS FIXED)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 5: Electrical Frequency (Dense-Disperse 2/100 Hz vs Fixed)"
di as txt "=================================================================="
meta regress freq_dd, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 9. MODEL 6: MODALITY (TEAS vs EA)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MODEL 6: Acupoint Stimulation Modality (TEAS=0, EA=1)"
di as txt "=================================================================="
gen is_ea = (modality == "EA")
meta regress is_ea, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 10. MODEL 7: CONSTRAINED 2-PREDICTOR MULTIVARIABLE MODEL (BASELINE + MODALITY)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "MULTIVARIABLE MODEL (CONSTRAINED 2-PREDICTOR, df = 8):"
di as txt "Baseline Control Opioid (arm2_mean_mme) + Modality (is_ea)"
di as txt "Scientific Question: Is the difference between EA and TEAS driven by"
di as txt "modality or by confounding with baseline surgical opioid demand?"
di as txt "=================================================================="
meta regress arm2_mean_mme is_ea, random(reml) se(kh)

* ------------------------------------------------------------------------------
* 11. TEAS STRATUM (k = 8): SUBSET UNIVARIABLE REGRESSION (BASELINE OPIOID)
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
* 12. EA STRATUM (k = 3): SUBSET UNIVARIABLE REGRESSION (BASELINE OPIOID)
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
di as txt "STATA EXTENDED META-REGRESSION EXECUTION COMPLETED SUCCESSFULLY"
di as txt "=================================================================="

log close
