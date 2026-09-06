* ==============================================================================
* STATA DO-FILE 04: RESCUE ANALGESIA INCIDENCE (BINARY OUTCOME)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_rescue_analgesia_data.csv (k=9 trials, N=880)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/04_rescue_analgesia.log", replace text

di as txt "=================================================================="
di as txt "04: RESCUE ANALGESIA OUTCOME FAMILY: INCIDENCE OF REQUIRING RESCUE"
di as txt "Effect Measure: Risk Ratio (RR), REML Random-Effects + Knapp-Hartung"
di as txt "=================================================================="

use "stata/stata_rescue_analgesia_data.dta", clear
describe
list canonical_name arm1_events arm1_n arm2_events arm2_n rescue_drug is_opioid

* 1. Declare Meta-Analysis for Binary Event Rates (Risk Ratio)
meta esize arm1_events arm1_n arm2_events arm2_n, esize(lnrr) studylabel(canonical_name)

* 2. PRIMARY SYNTHESIS: All 9 Trials Reporting Rescue Analgesia Incidence
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 9 TRIALS: Incidence of Requiring Rescue Analgesia (RR)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) transform(exp) predinterval

* 3. SUBGROUP: Specific Opioid Rescue Only (Tu 2024, Sun 2017, Pan 2023, Liu 2026, Hou 2023)
di as txt _n "------------------------------------------------------------------"
di as txt "2. SUBGROUP: Explicit Opioid Rescue (Morphine/Tramadol) Only (k=5)"
di as txt "------------------------------------------------------------------"
meta summarize if is_opioid == 1, random(reml) se(kh) transform(exp)

* 4. SUBGROUP: Non-Opioid Rescue (NSAID/Acetaminophen) Only (k=4)
di as txt _n "------------------------------------------------------------------"
di as txt "3. SUBGROUP: Non-Opioid Rescue Only (k=4)"
di as txt "------------------------------------------------------------------"
meta summarize if is_opioid == 0, random(reml) se(kh) transform(exp)

* 5. Generate and Export Forest Plot
meta forestplot, subgroup(is_opioid) ///
    title("Incidence of Postoperative Rescue Analgesia Requirement", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects Risk Ratio (k=9 Trials, N=880)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_rescue_analgesia_rr.png", width(1800) replace

di as txt _n "SUCCESS: Rescue analgesia incidence verified and exported."
log close
