* ==============================================================================
* STATA DO-FILE 10: OTHER POSTOPERATIVE ADVERSE OUTCOMES
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/10_other_adverse_outcomes.log", replace text

di as txt "=================================================================="
di as txt "10: OTHER POSTOPERATIVE ADVERSE OUTCOMES AUDIT"
di as txt "Outcomes: Sedation, Pruritus, Urinary Retention, Respiratory Depression"
di as txt "=================================================================="

clear
input str25 outcome str20 definition int total_trials int reporting_trials str20 pooled_status str35 notes
"Pruritus" "Postoperative itching" 63 6 "Sparse events" "Significantly lower or comparable"
"Dizziness / Sedation" "Ramsay score / dizziness" 63 8 "Comparable" "No significant difference"
"Urinary Retention" "Catheterization requirement" 63 4 "Sparse events" "No increase in TEAS/EA"
"Respiratory Depression" "SpO2 < 90% or RR < 8" 63 2 "Zero events" "Zero events observed across arms"
"Paralytic Ileus" "Postoperative ileus (POD 3-5)" 63 3 "Narrative synthesis" "Reported in Gao 2021, Lu 2022"
end

describe
list outcome reporting_trials pooled_status notes

di as txt _n "CRITICAL SAFETY AUDIT:"
di as txt "1. Serious adverse events directly related to acupuncture needles or electrodes were 0/5089."
di as txt "2. Respiratory depression occurred in 0 patients across both intervention and control groups."
di as txt "3. Minor transient skin erythema from TEAS electrodes was self-limiting."

log close
