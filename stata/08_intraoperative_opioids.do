* ==============================================================================
* STATA DO-FILE 08: INTRAOPERATIVE OPIOID EXPOSURE (REMIFENTANIL DOSE IN µG)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_intraop_remifentanil_data.csv (k=11 trials, N=760)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/08_intraoperative_opioids.log", replace text

di as txt "=================================================================="
di as txt "08: INTRAOPERATIVE OPIOID EXPOSURE: TOTAL REMIFENTANIL DOSE (µg)"
di as txt "Note: Kept strictly separate from postoperative opioid consumption."
di as txt "=================================================================="

use "stata/stata_intraop_remifentanil_data.dta", clear
describe
list canonical_name modality arm1_mean arm1_sd arm2_mean arm2_sd md se

* 1. Declare Meta-Analysis Setting
meta set md se, studylabel(canonical_name)

* 2. PRIMARY REMIFENTANIL SYNTHESIS: All 11 Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 11 TRIALS: Intraoperative Remifentanil Dose (µg)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. STRATUM 1: TEAS vs Sham (k=7 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "2. STRATUM 1: TEAS vs Sham (k=7 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS", random(reml) se(kh)

* 4. STRATUM 2: EA vs Sham (k=4 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "3. STRATUM 2: EA vs Sham (k=4 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 5. Generate and Export Forest Plot
meta forestplot, subgroup(modality) ///
    title("Intraoperative Remifentanil Dose Consumed (µg)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=11, N=760)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_intraop_remifentanil.png", width(1800) replace

di as txt _n "SUCCESS: Intraoperative remifentanil synthesis completed and exported."
log close
