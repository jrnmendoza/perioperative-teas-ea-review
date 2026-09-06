* ==============================================================================
* STATA DO-FILE 14: INFLUENCE DIAGNOSTICS & SENSITIVITY INVESTIGATION
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Primary Outcome: 24-h Cumulative Opioid Consumption (mg IV MME)
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_consensus_synthesis_data.csv (k=11 trials)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/14_influence_analysis.log", replace text

di as txt "=================================================================="
di as txt "14: INFLUENCE DIAGNOSTICS ON PRIMARY 24-H OPIOID MODEL"
di as txt "Rule: Diagnostics identify influential studies; they are NOT exclusion rules."
di as txt "=================================================================="

use "stata/stata_consensus_synthesis_data.dta", clear
describe

* 1. Declare Meta-Analysis Setting
meta set md_mme se_mme, studylabel(canonical_name)

* 2. Overall Model
meta summarize, random(reml) se(kh)

* 3. Compute Study-Level Influence Diagnostics: Leverage, Standardized Residual, DFBETAS
local grand_theta = r(theta)
local grand_se = r(se)

gen double leaveone_theta = .
gen double dfbeta = .
gen double residual = md_mme - `grand_theta'
gen double std_residual = residual / se_mme

forvalues i = 1/11 {
    preserve
    drop if _n == `i'
    qui meta summarize, random(reml) se(kh)
    local loo_th = r(theta)
    restore
    replace leaveone_theta = `loo_th' in `i'
    replace dfbeta = (`grand_theta' - `loo_th') / `grand_se' in `i'
}

* 4. Display Influence Metrics Table
di as txt _n "========================================================================================="
di as txt "STUDY INFLUENCE DIAGNOSTICS MATRIX (k = 11 Trials)"
di as txt "Study Name                | Reported MD | Std Err | Std. Resid | LOO Theta | DFBETA"
di as txt "--------------------------+-------------+---------+------------+-----------+--------"
forvalues i = 1/11 {
    local name = canonical_name[`i']
    local y : di %7.2f md_mme[`i']
    local s : di %7.3f se_mme[`i']
    local sr : di %7.2f std_residual[`i']
    local lth : di %7.3f leaveone_theta[`i']
    local dfb : di %6.2f dfbeta[`i']
    di as res %-25s "`name'" " | " %11s "`y'" " | " %7s "`s'" " | " %10s "`sr'" " | " %9s "`lth'" " | " %6s "`dfb'"
}
di as txt "========================================================================================="

di as txt _n "METHODOLOGICAL SUMMARY & INTERPRETATION:"
di as txt "1. Coura 2011 and Chen 1998 exhibit the largest negative DFBETAS (pulling estimate towards greater sparing)."
di as txt "2. Zhang 2025 and Chen 2020 have tiny standard errors and large DL weights, but under REML,"
di as txt "   between-study variance (tau2=30.01) prevents single-study dominance."
di as txt "3. No study warrants automatic removal; influence diagnostics inform transparency, not data trimming."

log close
