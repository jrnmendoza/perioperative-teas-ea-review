* ==============================================================================
* STATA DO-FILE 17: EXPLORATORY STUDY-LEVEL META-REGRESSIONS
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_consensus_synthesis_data.csv (k = 11 Primary RCTs)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/17_meta_regression.log", replace text

di as txt "=================================================================="
di as txt "17: EXPLORATORY STUDY-LEVEL RANDOM-EFFECTS META-REGRESSION"
di as txt "WARNING: Study-level associations are hypothesis-generating and"
di as txt "do not establish causality or individual-patient treatment effects."
di as txt "R2 reflects proportion of tau2 explained, not individual patient variance."
di as txt "=================================================================="

import delimited "stata/stata_consensus_synthesis_data.csv", clear varnames(1)

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
meta set md_mme se_mme, studylabel(canonical_name) studysize(arm1_n)

* 1. MODEL 1: BASELINE CONTROL-GROUP OPIOID CONSUMPTION (mg IV MME)
di as txt _n "------------------------------------------------------------------"
di as txt "MODEL 1: Baseline Control Opioid Requirement (arm2_mean_mme)"
di as txt "------------------------------------------------------------------"
meta regress arm2_mean_mme, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Baseline Surgical Opioid Requirement", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 49.08%)", size(small)) ///
    xtitle("Control Group 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = -0.170 (95% CI: -0.304, -0.036), t(9) = -2.87, p = 0.019", size(vsmall))
graph export "stata/results/meta_reg_baseline_mme.png", width(1800) replace
capture copy "stata/results/meta_reg_baseline_mme.png" "dashboard/stata_meta_reg_baseline_mme.png", replace

* 2. MODEL 2: PUBLICATION YEAR (TEMPORAL MODERATOR)
di as txt _n "------------------------------------------------------------------"
di as txt "MODEL 2: Publication Year (year)"
di as txt "Note: Secular trends in perioperative practice / ERAS may contribute."
di as txt "------------------------------------------------------------------"
meta regress year, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Publication Year", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 82.81%)", size(small)) ///
    xtitle("Publication Year", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = +0.471 (95% CI: +0.062, +0.881), t(9) = +2.60, p = 0.029", size(vsmall))
graph export "stata/results/meta_reg_year.png", width(1800) replace
capture copy "stata/results/meta_reg_year.png" "dashboard/stata_meta_reg_year.png", replace

* 3. MODEL 3: DEMOGRAPHIC SEX (% FEMALE PARTICIPANTS)
di as txt _n "------------------------------------------------------------------"
di as txt "MODEL 3: Patient Sex (% Female Participants)"
di as txt "ECOLOGICAL FALLACY WARNING: Study-level proportion female does NOT"
di as txt "represent individual-patient sex differences."
di as txt "------------------------------------------------------------------"
meta regress pct_female, random(reml) se(kh)
estat bubbleplot, title("Meta-Regression: Trial Sex Composition (% Female)", size(medium)) ///
    subtitle("Random-effects REML with Knapp–Hartung adjustment (k = 11, R² = 0.00%)", size(small)) ///
    xtitle("Proportion of Female Participants (% Female)", size(small)) ///
    ytitle("Mean Difference in 24-h Opioid Consumption (mg IV MME)", size(small)) ///
    note("Slope β = -0.013 (95% CI: -0.191, +0.165), t(9) = -0.16, p = 0.875", size(vsmall))
graph export "stata/results/meta_reg_sex.png", width(1800) replace
capture copy "stata/results/meta_reg_sex.png" "dashboard/stata_meta_reg_sex.png", replace

* 4. MODEL 4: STIMULATION TIMING (MULTI-PHASE VS PREOPERATIVE ONLY)
di as txt _n "------------------------------------------------------------------"
di as txt "MODEL 4: Stimulation Timing (Multi-phase vs Preoperative only)"
di as txt "------------------------------------------------------------------"
meta regress is_multiphase, random(reml) se(kh)

* 5. MODEL 5: ELECTRICAL FREQUENCY (DENSE-DISPERSE 2/100 HZ VS FIXED)
di as txt _n "------------------------------------------------------------------"
di as txt "MODEL 5: Electrical Frequency (Dense-Disperse 2/100 Hz vs Fixed)"
di as txt "------------------------------------------------------------------"
meta regress freq_dd, random(reml) se(kh)

di as txt _n "SUCCESS: Meta-regression models executed and bubble plots exported."
log close
