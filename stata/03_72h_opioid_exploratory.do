* ==============================================================================
* STATA DO-FILE 03: EXPLORATORY EXTENDED OPIOID OUTCOME (0-72 H IV MME)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_72h_opioid_synthesis_data.csv (k=4 trials, N=324)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/03_72h_opioid_exploratory.log", replace text

di as txt "=================================================================="
di as txt "03: EXPLORATORY EXTENDED POSTOPERATIVE OPIOID OUTCOME: 0-72 H CUMULATIVE"
di as txt "Note: Strictly exploratory; sparse data; not confirmatory evidence."
di as txt "=================================================================="

use "stata/stata_72h_opioid_synthesis_data.dta", clear
describe
list canonical_name modality comparator md_mme se_mme

* 1. Declare Meta-Analysis Setting
meta set md_mme se_mme, studylabel(canonical_name)

* 2. EXPLORATORY SYNTHESIS: All 4 Trials Reporting 72-h Continuous Consumption
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 4 EXPLORATORY 72-H TRIALS (REML + Knapp-Hartung)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. MODALITY EVALUATION: TEAS vs Sham (k=1: Zhang 2025; N=90)
di as txt _n "------------------------------------------------------------------"
di as txt "2. TEAS vs Sham at 72h: Only 1 trial contributed (Zhang 2025)"
di as txt "CRITICAL METHODOLOGICAL RULE: No pooled estimate was possible because"
di as txt "only one eligible study contributed. Do NOT call this a meta-analysis."
di as txt "------------------------------------------------------------------"
list canonical_name md_mme se_mme if modality == "TEAS"

* 4. MODALITY EVALUATION: EA Trials (k=3: Xie 2014, Wong 2006, Yang 2024; N=234)
di as txt _n "------------------------------------------------------------------"
di as txt "3. EA Trials at 72h (k=3 Trials, N=234)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 5. Generate and Export Forest Plot (IV MME)
meta forestplot, subgroup(modality) ///
    title("EXPLORATORY EXTENDED OPIOID OUTCOME: 0-72h Cumulative (mg IV MME)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=4, N=324)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_72h_opioid_mme.png", width(1800) replace
capture copy "stata/results/forest_72h_opioid_mme.png" "dashboard/stata_forest_72h_opioid_mme.png", replace

* 6. Standardized Effect Size: Hedges' g SMD
meta set hedges_g hedges_se, studylabel(canonical_name)
di as txt _n "------------------------------------------------------------------"
di as txt "4. STANDARDIZED MEAN DIFFERENCE (Hedges' g SMD): All 4 72-h Trials"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

meta forestplot, subgroup(modality) ///
    title("Standardized Mean Difference (Hedges' g): 72-h Opioid Consumption", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=4)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_72h_opioid_smd.png", width(1800) replace
capture copy "stata/results/forest_72h_opioid_smd.png" "dashboard/stata_forest_72h_opioid_smd.png", replace

di as txt _n "SUCCESS: Exploratory 72-h opioid outcome verified and exported."
log close
