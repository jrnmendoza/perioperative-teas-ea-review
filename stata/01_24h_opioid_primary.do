* ==============================================================================
* STATA DO-FILE 01: PRIMARY OPIOID OUTCOME (0-24 H CUMULATIVE IV MME)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_consensus_synthesis_data.csv (k=11 trials, N=945)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/01_24h_opioid_primary.log", replace text

di as txt "=================================================================="
di as txt "01: PRIMARY OPIOID OUTCOME: 0-24 H CUMULATIVE POSTOPERATIVE OPIOID"
di as txt "Primary Model: Random-Effects REML + Knapp-Hartung Adjustment"
di as txt "=================================================================="

use "stata/stata_consensus_synthesis_data.dta", clear
describe

* 1. Declare Meta-Analysis Setting
meta set md_mme se_mme, studylabel(canonical_name)

* 2. PRIMARY MODEL: All 11 Analyzable Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. PRIMARY SYNTHESIS: ALL 11 TRIALS (REML + Knapp-Hartung)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. ESTIMATOR SENSITIVITY: DerSimonian-Laird (Explains -5.04 vs -2.03 discrepancy)
di as txt _n "------------------------------------------------------------------"
di as txt "2. ESTIMATOR SENSITIVITY: DerSimonian-Laird Model"
di as txt "Note: Explains the -5.04 vs -2.03 discrepancy due to weight concentration."
di as txt "------------------------------------------------------------------"
meta summarize, random(dl) se(kh)
meta summarize, random(dl)

* 4. PRINCIPAL COMPARISON 1: TEAS vs Sham (k=8 Trials, N=725)
di as txt _n "------------------------------------------------------------------"
di as txt "3. PRINCIPAL STRATUM 1: TEAS vs Sham (k=8 Trials, N=725)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) predinterval

* 5. PRINCIPAL COMPARISON 2: EA vs Sham/Control (k=3 Trials, N=220)
di as txt _n "------------------------------------------------------------------"
di as txt "4. PRINCIPAL STRATUM 2: EA vs Control / Sham (k=3 Trials, N=220)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 6. SUBGROUP A: 6 Directly Reported Trials
di as txt _n "------------------------------------------------------------------"
di as txt "5. SUBGROUP A: 6 Directly Reported Trials"
di as txt "------------------------------------------------------------------"
meta summarize if opioid_status == "Primary Direct", random(reml) se(kh)

* 7. SUBGROUP B: 5 Derived Conditional Trials
di as txt _n "------------------------------------------------------------------"
di as txt "6. SUBGROUP B: 5 Derived Conditional Trials"
di as txt "------------------------------------------------------------------"
meta summarize if opioid_status == "Derived Conditional", random(reml) se(kh)

* 8. SENSITIVITY: Exclude High Risk of Bias (El-Rakshy 2009)
di as txt _n "------------------------------------------------------------------"
di as txt "7. SENSITIVITY: Exclude High Risk of Bias (El-Rakshy 2009)"
di as txt "------------------------------------------------------------------"
meta summarize if is_high_rob == 0, random(reml) se(kh)

* 9. Generate and Export Forest Plot (IV MME)
meta forestplot, subgroup(opioid_status) ///
    title("PRIMARY OPIOID OUTCOME: 0-24h Cumulative Consumption (mg IV MME)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=11, N=945)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_24h_opioid_mme.png", width(1800) replace
capture copy "stata/results/forest_24h_opioid_mme.png" "dashboard/stata_forest_teas_mme.png", replace

* 10. Standardized Effect Size: Hedges' g SMD
meta set hedges_g hedges_se, studylabel(canonical_name)
di as txt _n "------------------------------------------------------------------"
di as txt "8. STANDARDIZED MEAN DIFFERENCE (Hedges' g SMD): All 11 Trials"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

meta forestplot, subgroup(opioid_status) ///
    title("Standardized Mean Difference (Hedges' g): All 11 Analyzable Trials", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_24h_opioid_smd.png", width(1800) replace
capture copy "stata/results/forest_24h_opioid_smd.png" "dashboard/stata_forest_teas_smd.png", replace

di as txt _n "SUCCESS: Primary 24-h opioid outcome verified and exported."
log close
