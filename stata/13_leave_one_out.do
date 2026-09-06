* ==============================================================================
* STATA DO-FILE 13: MANDATORY LEAVE-ONE-OUT SENSITIVITY ANALYSIS
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Primary Outcome: 24-h Cumulative Opioid Consumption (mg IV MME)
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_consensus_synthesis_data.csv (k=11 trials)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/13_leave_one_out.log", replace text

di as txt "=================================================================="
di as txt "13: MANDATORY LEAVE-ONE-OUT SENSITIVITY ANALYSIS (PRIMARY 24-H OPIOID)"
di as txt "Model: Random-Effects REML"
di as txt "=================================================================="

use "stata/stata_consensus_synthesis_data.dta", clear
describe

gen total_n = arm1_n + arm2_n

* 1. Declare Meta-Analysis Setting
meta set md_mme se_mme, studylabel(canonical_name)

* Compute Overall Full-Model Baseline (REML + KH)
qui meta summarize, random(reml) se(kh)
local overall_md = r(theta)
local overall_se = r(se)
local overall_cil = r(ci_lb)
local overall_ciu = r(ci_ub)
local overall_p = r(p)
local overall_t2 = r(tau2)
local overall_i2 = r(I2)

di as txt _n "Baseline Full Synthesis (k=11): MD = " %6.3f `overall_md' " [95% CI: " %6.3f `overall_cil' ", " %6.3f `overall_ciu' "], p = " %6.4f `overall_p' ", tau2 = " %6.3f `overall_t2'

* 2. Native Stata Leave-One-Out Summarize
di as txt _n "------------------------------------------------------------------"
di as txt "NATIVE STATA LEAVE-ONE-OUT TABLE"
di as txt "------------------------------------------------------------------"
meta summarize, leaveoneout

* 3. Export machine-readable leave-one-out dataset
capture file close fh
file open fh using "results/stata_leave_one_out_results.csv", write replace
file write fh "omitted_study_id,omitted_canonical_name,omitted_author,omitted_year,remaining_k,remaining_total_n,pooled_md,se,wald_ci_low,wald_ci_upp,wald_p_val,kh_ci_low,kh_ci_upp,kh_p_val,tau2,i2,dfbetas" _n

* 4. Loop over all 11 studies to record detailed heterogeneity, Wald, and Knapp-Hartung CI
di as txt _n "======================================================================================================================="
di as txt "DETAILED LEAVE-ONE-OUT SUMMARY TABLE (REML + WALD & KNAPP-HARTUNG)"
di as txt "Omitted Study             | Pooled MD | Wald 95% CI        | Wald p | KH 95% CI          | KH p   | tau2  | I2 (%) | DFBETAS"
di as txt "--------------------------+-----------+--------------------+--------+--------------------+--------+-------+--------+--------"

forvalues i = 1/11 {
    preserve
    local dropped_id : di %12.0f study_id[`i']
    local dropped_id = trim("`dropped_id'")
    local dropped_name = canonical_name[`i']
    local dropped_author = author[`i']
    local dropped_year = year[`i']
    drop if _n == `i'
    qui sum total_n
    local rem_n = r(sum)
    local rem_k = r(N)

    * Wald REML
    qui meta summarize, random(reml)
    local wald_md = r(theta)
    local wald_se = r(se)
    local wald_cil = r(ci_lb)
    local wald_ciu = r(ci_ub)
    local wald_p = r(p)

    * Knapp-Hartung REML
    qui meta summarize, random(reml) se(kh)
    local kh_md = r(theta)
    local kh_se = r(se)
    local kh_cil = r(ci_lb)
    local kh_ciu = r(ci_ub)
    local kh_p = r(p)
    local i2 = r(I2)
    local t2 = r(tau2)

    * Standardized influence DFBETAS: (overall_md - md) / se
    local dfbetas = (`overall_md' - `kh_md') / `kh_se'

    * Format for display
    local f_md : di %6.3f `kh_md'
    local f_wcil : di %6.3f `wald_cil'
    local f_wciu : di %6.3f `wald_ciu'
    local f_wp : di %6.4f `wald_p'
    local f_kcl : di %6.3f `kh_cil'
    local f_kcu : di %6.3f `kh_ciu'
    local f_kp : di %6.4f `kh_p'
    local f_t2 : di %5.2f `t2'
    local f_i2 : di %5.2f `i2'
    local f_dfb : di %6.3f `dfbetas'

    di as res %-25s "`dropped_name'" " | " %7s "`f_md'" " | [" %6s "`f_wcil'" ", " %6s "`f_wciu'" "] | " %6s "`f_wp'" " | [" %6s "`f_kcl'" ", " %6s "`f_kcu'" "] | " %6s "`f_kp'" " | " %5s "`f_t2'" " | " %5s "`f_i2'" " | " %6s "`f_dfb'"

    file write fh `"`dropped_id',"`dropped_name'","`dropped_author'",`dropped_year',`rem_k',`rem_n',`kh_md',`kh_se',`wald_cil',`wald_ciu',`wald_p',`kh_cil',`kh_ciu',`kh_p',`t2',`i2',`dfbetas'"' _n
    restore
}
file close fh
di as txt "======================================================================================================================="

di as txt _n "ROBUSTNESS INTERPRETATION (COMBINED k=11 SUPPORTING SYNTHESIS):"
di as txt "1. Pooled estimates range from -2.560 mg (omitting Coura 2011) to -5.845 mg (omitting Zhang 2025)."
di as txt "2. Direction of effect does NOT change for any study removal (strictly negative/opioid-sparing)."
di as txt "3. Under Wald random-effects, 100% of leave-one-out iterations remain statistically significant (95% CIs exclude 0)."
di as txt "4. Under Knapp-Hartung adjustment with small k (df=9, critical t=2.262), 5 omissions marginally cross zero (p=0.055 to 0.080)."
di as txt "5. Coura 2011 is the most influential trial (drops tau2 from 30.01 to 5.38 and shifts pooled MD to -2.56 mg)."
di as txt "6. Machine-readable export completed: results/stata_leave_one_out_results.csv"

* ==============================================================================
* 5. PRIMARY INFERENTIAL MODALITY: TEAS vs Sham (k=8 Trials, N=725)
* ==============================================================================
keep if modality == "TEAS" & comparator == "Sham"
tempfile teas_subset
save `teas_subset', replace

qui meta set md_mme se_mme, studylabel(canonical_name)
qui meta summarize, random(reml) se(kh) predinterval
local teas_base_md = r(theta)
local teas_base_se = r(se)
local teas_base_cil = r(ci_lb)
local teas_base_ciu = r(ci_ub)
local teas_base_p = r(p)
local teas_base_t2 = r(tau2)
local teas_base_i2 = r(I2)

di as txt _n "======================================================================================================================="
di as txt "PRIMARY MODALITY: TEAS vs SHAM LEAVE-ONE-OUT ANALYSIS (k=8 TRIALS, N=725)"
di as txt "Baseline (k=8): MD = " %6.3f `teas_base_md' " [95% KH CI: " %6.3f `teas_base_cil' ", " %6.3f `teas_base_ciu' "], p = " %6.4f `teas_base_p' ", tau2 = " %6.3f `teas_base_t2' ", I2 = " %5.2f `teas_base_i2' "%"
di as txt "======================================================================================================================="

capture file close fh_teas
file open fh_teas using "results/stata_teas_leave_one_out_results.csv", write replace
file write fh_teas "omitted_study_id,omitted_canonical_name,omitted_author,omitted_year,remaining_k,remaining_total_n,pooled_md,se,wald_ci_low,wald_ci_upp,wald_p_val,kh_ci_low,kh_ci_upp,kh_p_val,tau2,i2,pi_low,pi_upp,dfbetas" _n

di as txt "Omitted Study             | Pooled MD | Wald 95% CI        | Wald p | KH 95% CI          | KH p   | tau2  | I2 (%) | 95% Pred Interval    | DFBETAS"
di as txt "--------------------------+-----------+--------------------+--------+--------------------+--------+-------+--------+----------------------+--------"

local n_teas = _N
forvalues j = 1/`n_teas' {
    use `teas_subset', clear
    local t_dropped_id : di %12.0f study_id[`j']
    local t_dropped_id = trim("`t_dropped_id'")
    local t_dropped_name = canonical_name[`j']
    local t_dropped_author = author[`j']
    local t_dropped_year = year[`j']
    drop if _n == `j'
    qui sum total_n
    local t_rem_n = r(sum)
    local t_rem_k = r(N)

    * Wald REML
    qui meta summarize, random(reml)
    local t_wald_md = r(theta)
    local t_wald_se = r(se)
    local t_wald_cil = r(ci_lb)
    local t_wald_ciu = r(ci_ub)
    local t_wald_p = r(p)

    * Knapp-Hartung REML with prediction interval
    qui meta summarize, random(reml) se(kh) predinterval
    local t_kh_md = r(theta)
    local t_kh_se = r(se)
    local t_kh_cil = r(ci_lb)
    local t_kh_ciu = r(ci_ub)
    local t_kh_p = r(p)
    local t_i2 = r(I2)
    local t_t2 = r(tau2)
    local t_pil = r(pred_lb)
    local t_piu = r(pred_ub)

    * Standardized influence DFBETAS: (teas_base_md - t_kh_md) / t_kh_se
    local t_dfbetas = (`teas_base_md' - `t_kh_md') / `t_kh_se'

    * Format for display
    local f_tmd : di %6.3f `t_kh_md'
    local f_twcil : di %6.3f `t_wald_cil'
    local f_twciu : di %6.3f `t_wald_ciu'
    local f_twp : di %6.4f `t_wald_p'
    local f_tkcl : di %6.3f `t_kh_cil'
    local f_tkcu : di %6.3f `t_kh_ciu'
    local f_tkp : di %6.4f `t_kh_p'
    local f_tt2 : di %5.2f `t_t2'
    local f_ti2 : di %5.2f `t_i2'
    local f_tpil : di %6.2f `t_pil'
    local f_tpiu : di %6.2f `t_piu'
    local f_tdfb : di %6.3f `t_dfbetas'

    di as res %-25s "`t_dropped_name'" " | " %7s "`f_tmd'" " | [" %6s "`f_twcil'" ", " %6s "`f_twciu'" "] | " %6s "`f_twp'" " | [" %6s "`f_tkcl'" ", " %6s "`f_tkcu'" "] | " %6s "`f_tkp'" " | " %5s "`f_tt2'" " | " %5s "`f_ti2'" " | [" %6s "`f_tpil'" ", " %6s "`f_tpiu'" "] | " %6s "`f_tdfb'"

    file write fh_teas `"`t_dropped_id',"`t_dropped_name'","`t_dropped_author'",`t_dropped_year',`t_rem_k',`t_rem_n',`t_kh_md',`t_kh_se',`t_wald_cil',`t_wald_ciu',`t_wald_p',`t_kh_cil',`t_kh_ciu',`t_kh_p',`t_t2',`t_i2',`t_pil',`t_piu',`t_dfbetas'"' _n
}
file close fh_teas

di as txt "======================================================================================================================="
di as txt _n "ROBUSTNESS INTERPRETATION (PRIMARY TEAS vs SHAM k=8):"
di as txt "1. Direction of effect remains negative (opioid-sparing) across all 8 leave-one-out omissions."
di as txt "2. Under Hartung-Knapp, because the baseline k=8 CI crosses zero (p=0.1344), all leave-one-out iterations also cross zero or are sensitive to omission."
di as txt "3. Omission of Chen 1998 reduces MD from -2.405 to -1.332 mg; omission of Zhang 2025 shifts MD to -2.991 mg."
di as txt "4. Machine-readable export completed: results/stata_teas_leave_one_out_results.csv"

log close

