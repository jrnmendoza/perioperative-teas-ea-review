* ==============================================================================
* STATA DO-FILE 07: PCA OUTCOMES & PUMP PARAMETERS AUDIT
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/07_pca_outcomes.log", replace text

di as txt "=================================================================="
di as txt "07: PCA OUTCOMES & PUMP PARAMETERS AUDIT"
di as txt "Rule: PCA presses are NOT opioid consumption. Avoid double counting."
di as txt "=================================================================="

clear
input str20 canonical_name str15 drug str15 bolus_dose str12 lockout str15 basal_rate str20 max_limit str25 outcome_type
"Chen 1998" "Hydromorphone" "0.2 mg" "6 min" "None" "None reported" "PCA deliveries & demands"
"Sim 2002" "Morphine" "1 mg" "5 min" "None" "None reported" "PCA demands & deliveries"
"Coura 2011" "Fentanyl" "20 ug" "10 min" "None" "None reported" "PCA boluses"
"Jin 2023" "Sufentanil" "2 ug" "15 min" "2 ug/h" "None reported" "PCA pump compressions"
"Lu 2022" "Sufentanil" "2 ug" "15 min" "1.5 ug/h" "None reported" "PCA demand attempts"
"Zhang 2023" "Sufentanil" "2 ug" "10 min" "1.5 ug/h" "None reported" "PCA bolus count"
end

describe
list canonical_name drug bolus_dose lockout basal_rate outcome_type

di as txt _n "METHODOLOGICAL SUMMARY:"
di as txt "1. Trials vary widely in pump lockout intervals (5 min to 15 min) and basal infusion."
di as txt "2. PCA press counts reflect patient-perceived pain behavior, not actual mg exposure."
di as txt "3. PCA-delivered dose is already integrated into 24-h/48-h cumulative MME where valid."
di as txt "4. Double-counting PCA dose as both an independent outcome and within total MME is prevented."

log close
