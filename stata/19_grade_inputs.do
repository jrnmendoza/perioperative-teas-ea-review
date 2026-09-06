* ==============================================================================
* STATA DO-FILE 19: GRADE EVIDENCE PROFILE INPUT GENERATION
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/19_grade_inputs.log", replace text

di as txt "=================================================================="
di as txt "19: GRADE EVIDENCE PROFILE INPUTS & DOWNGRADE AUDIT"
di as txt "Principle: RCT evidence starts at HIGH certainty. No upgrading."
di as txt "Downgrading domains: RoB, Inconsistency, Indirectness, Imprecision, Publication Bias."
di as txt "=================================================================="

clear
input str35 outcome_comparison int k int n str25 pooled_effect str20 certainty str35 downgrade_reasons
"TEAS vs Sham: 24h Opioid" 8 725 "MD -5.35 mg [-10.87, +0.17]" "Moderate" "Inconsistency (-1: I2=99.8%)"
"EA vs Sham: 24h Opioid" 2 72 "MD -15.66 mg [-30.12, -1.20]" "Low" "Inconsistency (-1), Imprecision (-1: small N)"
"All Modalities: 24h Opioid" 11 945 "MD -5.04 mg [-9.78, -0.29]" "Moderate" "Inconsistency (-1: tau2=30.01)"
"TEAS vs Sham: 48h Opioid" 3 370 "MD -2.14 mg [-3.75, -0.52]" "Moderate" "Imprecision (-1: 3 trials)"
"EA: 48h Opioid" 2 108 "MD -6.24 mg [-11.89, -0.59]" "Low" "Imprecision (-2: very small N=108)"
"All Modalities: 48h Opioid" 5 478 "MD -2.71 mg [-4.40, -1.02]" "Moderate" "Inconsistency (-1: I2=89%)"
"All Modalities: 72h Opioid" 4 324 "MD -8.76 mg [-19.05, +1.52]" "Very Low" "Inconsistency (-1), Imprecision (-2: PI crosses 0)"
"Postoperative Pain at 24h" 15 1332 "MD -0.63 VAS [-0.94, -0.32]" "Moderate" "Inconsistency (-1: I2=98%)"
"PONV Incidence" 17 1974 "RR 0.58 [0.46, 0.73]" "Moderate" "Inconsistency (-1: I2=72%)"
"Time to First Flatus" 10 1328 "MD -3.42 h [-5.45, -1.39]" "Moderate" "Inconsistency (-1: I2=94%)"
end

describe
list outcome_comparison k n pooled_effect certainty downgrade_reasons

di as txt _n "SUCCESS: GRADE Summary of Findings profile inputs tabulated."
log close
