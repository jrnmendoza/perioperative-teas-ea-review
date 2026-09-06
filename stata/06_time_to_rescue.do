* ==============================================================================
* STATA DO-FILE 06: TIME TO FIRST RESCUE ANALGESIA (REPORTED FORMAT AUDIT)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/06_time_to_rescue.log", replace text

di as txt "=================================================================="
di as txt "06: TIME TO FIRST RESCUE ANALGESIA: FORMAT AUDIT & INCOMPATIBILITY CHECK"
di as txt "Rule: Do not pool incompatible effect measures (mean vs median vs HR)."
di as txt "=================================================================="

clear
input str25 canonical_name str10 modality str10 comparator str20 format str30 reported_value str35 notes
"Sun 2017" "TEAS" "Sham" "Mean ± SD (min)" "TEAS: 48.2±14.5 vs Sham: 28.5±11.2" "Statistically prolonged time (P<0.01)"
"Hou 2023" "TEAS" "Sham" "Median (IQR) (h)" "TEAS: 6.5 (4-12) vs Sham: 2.5 (1-5)" "Prolonged time to first request (P=0.003)"
"Tu 2024" "TEAS" "Sham" "Kaplan-Meier curve" "Log-rank P = 0.042" "Significantly delayed first request"
end

describe
list canonical_name modality comparator format reported_value

di as txt _n "CRITICAL METHODOLOGICAL EVALUATION:"
di as txt "Because Sun 2017 reports mean ± SD in minutes, Hou 2023 reports skewed median (IQR) in hours,"
di as txt "and Tu 2024 reports Kaplan-Meier survival curves, statistical pooling into a single effect"
di as txt "estimate is METHODOLOGICALLY INAPPROPRIATE. Narrative synthesis must be retained."

di as txt _n "SUCCESS: Time-to-rescue format classification completed."
log close
