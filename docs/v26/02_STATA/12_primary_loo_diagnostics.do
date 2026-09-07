* ==============================================================================
* 12_primary_loo_diagnostics.do
*   Full leave-one-out influence diagnostic table for the strict primary 24-h
*   opioid pool (dashboard/app.js's PRIMARY_LOO_DATA).
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 BE
* ==============================================================================
*
* PURPOSE
*   PRIMARY_LOO_DATA in dashboard/app.js is a hand-maintained JSON-literal array
*   carrying, per omitted study: the KH-adjusted pooled MD/CI/p, the unadjusted
*   Wald MD/CI/p, tau2, I2, and a DFBETAS-style influence statistic. No do-file
*   in this pipeline generated it -- 08_sensitivity.do's `meta summarize,
*   leaveoneout` only reproduces the KH-adjusted column. This script closes
*   that provenance gap by computing every column directly, added when Szmit
*   2021 moved the strict primary pool from k=6 to k=7 (2026-09-07) made manual
*   transcription of a 7th row impractical to verify by hand.
*
*   DFBETAS_i = (theta_full - theta_(-i)) / SE_KH(theta_(-i))
*   -- the standard leave-one-out influence statistic (Viechtbauer & Cheung
*   2010), using this project's primary KH-adjusted SE convention throughout.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/12_primary_loo_diagnostics.log", replace

di as txt "=================================================================="
di as txt "12: PRIMARY 24-H OPIOID -- FULL LEAVE-ONE-OUT DIAGNOSTIC TABLE (k=7)"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
keep if inc_primary == 1
meta set md_mme se_mme, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

meta summarize, random(reml) se(kh)
local theta_full = r(theta)
di as txt "Full-model theta = " %6.4f `theta_full'

levelsof study_unit, local(studies)

tempname results
tempfile out
postfile `results' str40 study double(remaining_k remaining_n pooled_md se_kh ///
    wald_lo wald_hi wald_p kh_lo kh_hi kh_p tau2 i2 dfbetas) using `out', replace

foreach s of local studies {
    preserve
    quietly count if study_unit == "`s'"
    local sN = r(N)
    drop if study_unit == "`s'"
    quietly count
    local rk = r(N)
    quietly summarize n_i
    local rn_i = r(sum)
    quietly summarize n_c
    local rn_c = r(sum)
    local rn = `rn_i' + `rn_c'

    meta set md_mme se_mme, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")

    quietly meta summarize, random(reml)
    local w_lo = r(ci_lb)
    local w_hi = r(ci_ub)
    local w_p  = r(p)
    local md   = r(theta)
    local tau2 = r(tau2)
    local i2   = r(I2)

    quietly meta summarize, random(reml) se(kh)
    local k_lo = r(ci_lb)
    local k_hi = r(ci_ub)
    local k_p  = r(p)
    local se_kh = (r(ci_ub) - r(theta)) / invttail(r(df), 0.025)

    local dfbetas = (`theta_full' - `md') / `se_kh'

    post `results' ("`s'") (`rk') (`rn') (`md') (`se_kh') (`w_lo') (`w_hi') (`w_p') ///
        (`k_lo') (`k_hi') (`k_p') (`tau2') (`i2') (`dfbetas')

    restore
}

postclose `results'

use `out', clear
gen wald_sig = (wald_lo > 0 | wald_hi < 0)
gen kh_sig   = (kh_lo > 0 | kh_hi < 0)

format pooled_md se_kh wald_lo wald_hi kh_lo kh_hi tau2 dfbetas %9.3f
format wald_p kh_p %9.4f
format i2 %9.2f

di as txt _n "=== FULL LEAVE-ONE-OUT DIAGNOSTIC TABLE ==="
list study remaining_k remaining_n pooled_md se_kh wald_lo wald_hi wald_p ///
    kh_lo kh_hi kh_p tau2 i2 dfbetas wald_sig kh_sig, clean noobs

export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_primary_loo_diagnostics.csv", replace

di as txt _n "Saved 03_RESULTS/results_primary_loo_diagnostics.csv"

log close
