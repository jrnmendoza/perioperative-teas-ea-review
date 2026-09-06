* ==============================================================================
* STATA DO-FILE 12: PATIENT-REPORTED & RECOVERY OUTCOMES (GI FLATUS & PROMS)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_secondary_synthesis_data.csv (k=10 trials for Flatus Time)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/12_patient_reported_outcomes.log", replace text

di as txt "=================================================================="
di as txt "12: PATIENT-REPORTED & RECOVERY OUTCOMES: TIME TO FIRST FLATUS (HOURS)"
di as txt "Note: Keep under Secondary Postoperative Recovery Outcomes."
di as txt "=================================================================="

use "stata/stata_secondary_synthesis_data.dta", clear
keep if outcome_domain == "Flatus_Time"
describe
list canonical_name modality comparator effect se arm1_mean arm1_sd arm2_mean arm2_sd

* 1. Declare Meta-Analysis Setting
meta set effect se, studylabel(canonical_name)

* 2. PRIMARY FLATUS SYNTHESIS: All 10 Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 10 TRIALS: Time to First Postoperative Flatus (Hours)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. STRATUM 1: TEAS vs Sham (k=5 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "2. STRATUM 1: TEAS vs Sham (k=5 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS", random(reml) se(kh)

* 4. STRATUM 2: EA Trials (k=5 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "3. STRATUM 2: EA Trials (k=5 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 5. Generate and Export Forest Plot
meta forestplot, subgroup(modality) ///
    title("Gastrointestinal Recovery: Time to First Flatus (Hours)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=10, N=1328)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_flatus.png", width(1800) replace
capture copy "stata/results/forest_flatus.png" "dashboard/stata_forest_flatus.png", replace

* 6. Audit of Validated PROMs (QoR-15, QoR-40, Patient Satisfaction)
di as txt _n "=================================================================="
di as txt "PATIENT-REPORTED OUTCOMES (PROMS) REPORTING FREQUENCY AUDIT"
di as txt "=================================================================="
di as txt "Total included studies: 63 RCTs (N = 5,089)"
di as txt "QoR-15 / QoR-40 reported: 4 / 63 trials (6.3%)"
di as txt "Patient satisfaction reported: 12 / 63 trials (19.0%)"
di as txt "Postoperative sleep quality (PSQI / sleep efficiency): 3 / 63 trials (4.8%)"
di as txt _n "EVIDENCE GAP CONCLUSION:"
di as txt "Patient-reported global recovery outcomes were infrequently reported"
di as txt "across the included evidence base, representing a key priority for future trials."

log close
