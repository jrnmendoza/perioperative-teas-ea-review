* ==============================================================================
* STATA DO-FILE 02: KEY SECONDARY OPIOID OUTCOME (0-48 H CUMULATIVE IV MME)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_48h_opioid_synthesis_data.csv (k=5 trials, N=478)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/02_48h_opioid_secondary.log", replace text

di as txt "=================================================================="
di as txt "02: KEY SECONDARY OPIOID OUTCOME: 0-48 H CUMULATIVE POSTOPERATIVE OPIOID"
di as txt "Note: NOT Co-Primary. Explicitly labeled Key Secondary."
di as txt "=================================================================="

use "stata/stata_48h_opioid_synthesis_data.dta", clear
describe
list canonical_name modality comparator md_mme se_mme

* 1. Declare Meta-Analysis Setting
meta set md_mme se_mme, studylabel(canonical_name)

* 2. KEY SECONDARY SYNTHESIS: All 5 Analyzable Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 5 ANALYZABLE 48-H TRIALS (REML + Knapp-Hartung)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. ESTIMATOR SENSITIVITY: DerSimonian-Laird
di as txt _n "------------------------------------------------------------------"
di as txt "2. ESTIMATOR SENSITIVITY: DerSimonian-Laird"
di as txt "------------------------------------------------------------------"
meta summarize, random(dl) se(kh)

* 4. STRATUM 1: TEAS vs Sham (k=3 Trials: Chen 2020, He 2026, Zhang 2023; N=370)
di as txt _n "------------------------------------------------------------------"
di as txt "3. STRATUM 1: TEAS vs Sham (k=3 Trials, N=370)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS", random(reml) se(kh)

* 5. STRATUM 2: EA vs Controls (k=2 Trials: An 2014, Wong 2006; N=108)
di as txt _n "------------------------------------------------------------------"
di as txt "4. STRATUM 2: EA vs Controls (k=2 Trials, N=108)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 6. Generate and Export Forest Plot (IV MME)
meta forestplot, subgroup(modality) ///
    title("KEY SECONDARY OPIOID OUTCOME: 0-48h Cumulative Consumption (mg IV MME)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=5, N=478)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_48h_opioid_mme.png", width(1800) replace
capture copy "stata/results/forest_48h_opioid_mme.png" "dashboard/stata_forest_48h_opioid_mme.png", replace

* 7. Standardized Effect Size: Hedges' g SMD
meta set hedges_g hedges_se, studylabel(canonical_name)
di as txt _n "------------------------------------------------------------------"
di as txt "5. STANDARDIZED MEAN DIFFERENCE (Hedges' g SMD): All 5 48-h Trials"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

meta forestplot, subgroup(modality) ///
    title("Standardized Mean Difference (Hedges' g): 48-h Opioid Consumption", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=5)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_48h_opioid_smd.png", width(1800) replace
capture copy "stata/results/forest_48h_opioid_smd.png" "dashboard/stata_forest_48h_opioid_smd.png", replace

di as txt _n "SUCCESS: Key secondary 48-h opioid outcome verified and exported."
log close
