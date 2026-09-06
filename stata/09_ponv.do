* ==============================================================================
* STATA DO-FILE 09: POSTOPERATIVE NAUSEA AND VOMITING (PONV)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_secondary_synthesis_data.csv (k=17 trials reporting PONV)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/09_ponv.log", replace text

di as txt "=================================================================="
di as txt "09: POSTOPERATIVE NAUSEA AND VOMITING (PONV) INCIDENCE"
di as txt "Note: Reduced PONV does not prove an opioid-mediated mechanism;"
di as txt "TEAS/EA may have direct antiemetic actions at PC6 / ST36."
di as txt "=================================================================="

use "stata/stata_secondary_synthesis_data.dta", clear
keep if outcome_domain == "PONV"
describe
list canonical_name modality comparator arm1_events arm1_n arm2_events arm2_n

* 1. Declare Binary Meta-Analysis
meta esize arm1_events arm1_n arm2_events arm2_n, esize(lnrr) studylabel(canonical_name)

* 2. PRIMARY PONV SYNTHESIS: All 17 Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 17 TRIALS: PONV Incidence Risk Ratio (RR)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) transform(exp) predinterval

* 3. STRATUM 1: TEAS vs Sham (k=13 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "2. STRATUM 1: TEAS vs Sham (k=13 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) transform(exp)

* 4. STRATUM 2: EA Trials (k=4 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "3. STRATUM 2: EA Trials (k=4 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh) transform(exp)

* 5. Generate and Export Forest Plot
meta forestplot, subgroup(modality) ///
    title("Postoperative Nausea & Vomiting (PONV) Incidence", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects Risk Ratio (k=17 Trials)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_ponv.png", width(1800) replace
capture copy "stata/results/forest_ponv.png" "dashboard/stata_forest_ponv.png", replace

di as txt _n "SUCCESS: PONV synthesis verified and exported."
log close
