clear all
set more off
use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
keep if inc_primary == 1
meta set md_mme se_mme, studylabel(study_unit)
levelsof study_unit, local(studies)
foreach s of local studies {
    preserve
    drop if study_unit == "`s'"
    di "=== OMITTING: `s' ==="
    qui meta summarize, random(reml)
    di "REML Wald: theta = " r(theta) " [" r(ci_lb) ", " r(ci_ub) "] p = " r(p) " tau2 = " r(tau2) " I2 = " r(I2) " se = " r(se)
    qui meta summarize, random(reml) se(kh)
    di "REML KH:   theta = " r(theta) " [" r(ci_lb) ", " r(ci_ub) "] p = " r(p) " se = " r(se)
    restore
}
exit, STATA
