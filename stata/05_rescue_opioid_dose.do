* ==============================================================================
* STATA DO-FILE 05: RESCUE OPIOID DOSE (CONTINUOUS EXPOSURE IN IV MME)
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/05_rescue_opioid_dose.log", replace text

di as txt "=================================================================="
di as txt "05: RESCUE OPIOID DOSE OUTCOME: CONTINUOUS OPIOID CONSUMPTION (IV MME)"
di as txt "=================================================================="

* Load trials reporting quantified continuous rescue opioid dose
clear
input str25 canonical_name str10 modality str10 comparator double md_mme double se_mme str20 native_drug
"Chen 2015 (Hyperalgesia)" "TEAS" "Sham" -1.122 0.128 "IV sufentanil"
"Chen 2015 (Thyroidectomy)" "TEAS" "Sham" -5.000 1.234 "IV morphine"
"Wang 2023" "TEAS" "Sham" -2.250 0.880 "IV tramadol (conv)"
end

describe
list

meta set md_mme se_mme, studylabel(canonical_name)
di as txt _n "------------------------------------------------------------------"
di as txt "1. RESCUE OPIOID DOSE: Random-Effects REML Synthesis (IV MME mg)"
di as txt "------------------------------------------------------------------"
meta summarize, random(reml) se(kh)

meta forestplot, ///
    title("Postoperative Rescue Opioid Dose Consumed (mg IV MME)", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Knapp-Hartung", size(small)) ///
    nullrefline nonotes
graph export "stata/results/forest_rescue_opioid_dose.png", width(1800) replace

di as txt _n "SUCCESS: Rescue opioid dose analysis executed."
log close
