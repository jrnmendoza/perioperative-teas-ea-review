* ==============================================================================
* STATA DO-FILE 11: POSTOPERATIVE PAIN INTENSITY AT ~24 HOURS (RESTING VAS/NRS)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_secondary_synthesis_data.csv (k=15 trials, N=1332)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/11_pain.log", replace text

di as txt "=================================================================="
di as txt "11: POSTOPERATIVE PAIN INTENSITY AT ~24 HOURS (RESTING VAS/NRS 0-10)"
di as txt "Rule: Exactly ONE effect per trial at ~24h (no correlated repeats)."
di as txt "=================================================================="

use "stata/stata_secondary_synthesis_data.dta", clear
keep if outcome_domain == "Pain_24h"
describe
list canonical_name modality comparator effect se arm1_mean arm1_sd arm2_mean arm2_sd

* 1. Declare Meta-Analysis Setting
meta set effect se, studylabel(canonical_name)

* 2. PRIMARY PAIN SYNTHESIS: All 15 Trials (REML + Knapp-Hartung)
di as txt _n "------------------------------------------------------------------"
di as txt "1. ALL 15 TRIALS: 24-h Pain Intensity at Rest (VAS 0-10)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh) predinterval

* 3. STRATUM 1: TEAS vs Sham (k=11 Trials)
di as txt _n "------------------------------------------------------------------"
di as txt "2. STRATUM 1: TEAS vs Sham (k=11 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

* 4. STRATUM 2: EA vs Sham (k=3 Trials: Ng 2013, Huang 2024, He 2026 breast)
di as txt _n "------------------------------------------------------------------"
di as txt "3. STRATUM 2: EA vs Sham (k=3 Trials)"
di as txt "------------------------------------------------------------------"
meta summarize if modality == "EA", random(reml) se(kh)

* 5. Generate and Export Forest Plot
meta forestplot, subgroup(modality) ///
    title("Postoperative Pain Intensity at ~24h at Rest (VAS/NRS 0-10)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung (k=15, N=1332)", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_pain.png", width(1800) replace
capture copy "stata/results/forest_pain.png" "dashboard/stata_forest_pain.png", replace

di as txt _n "SUCCESS: Pain synthesis verified and exported."
log close
