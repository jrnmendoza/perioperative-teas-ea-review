* 03_models.do -- fit every model with the canonical specification in official Stata -meta-.
*   k >= 2 : random effects, REML tau^2, truncated (safeguarded) Knapp-Hartung SE: se(khartung, truncated)
*            REML is maximised with tight tolerances (tolerance/nrtolerance 1e-14): with Stata's defaults the optimiser
*            stops at tau^2 ~ 1e-7 where the REML optimum is the boundary tau^2 = 0 (see STATA_RECONCILIATION.md).
*   k == 1 : single-study estimate with a normal 95% CI -- NOT pooled
*   k == 0 : no eligible data
* Prediction intervals: Stata's -predinterval- uses t(k-2) (Higgins et al. 2009). The canonical pipeline and
* metafor use t(k-1) and report PIs only when k >= 5; both are recorded so the difference is explicit.
log using "$STATA/logs/03_models.log", text replace name(mod)
use "$STATA/work/models.dta", clear
local nm = _N
forvalues i = 1/`nm' {
    local set`i' = analysis_set[`i']
    local mid`i' = model_id[`i']
}
tempname post
postfile `post' str16 analysis_set str80 model_id int k long N double(theta se ci_lb ci_ub tau2 I2 Q hk_q ///
    pi_lb_stata pi_ub_stata pi_lb_k1 pi_ub_k1 alt_theta alt_ci_lb alt_ci_ub) str40 status using "$STATA/work/results.dta", replace
forvalues i = 1/`nm' {
    use "$STATA/work/inputs_es.dta", clear
    keep if analysis_set == "`set`i''" & model_id == "`mid`i''"
    local k = _N
    if `k' == 0 {
        post `post' ("`set`i''") ("`mid`i''") (0) (0) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ("no eligible data")
        continue
    }
    quietly summarize n_i
    local ni = r(sum)
    quietly summarize n_c
    local N = `ni' + r(sum)
    if `k' == 1 {
        local th = s_yi[1]
        local se = s_se[1]
        post `post' ("`set`i''") ("`mid`i''") (1) (`N') (`th') (`se') (`th' - invnormal(.975)*`se') (`th' + invnormal(.975)*`se') ///
            (0) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ("single study - not pooled")
        continue
    }
    meta set s_yi s_se, studylabel(study) random(reml)
    local opt se(khartung, truncated) tolerance(1e-14) nrtolerance(1e-14) iterate(1000)
    if `k' >= 3 quietly meta summarize, `opt' predinterval
    else        quietly meta summarize, `opt'
    assert r(converged) == 1
    local th = r(theta)
    local se = r(se)
    local lb = r(ci_lb)
    local ub = r(ci_ub)
    local t2 = r(tau2)
    local i2 = r(I2)
    local q  = r(Q)
    local pl = cond(`k' >= 3, r(pi_lb), .)
    local pu = cond(`k' >= 3, r(pi_ub), .)
    * Knapp-Hartung scale q = sum w(y - theta)^2 / (k - 1), w = 1/(v + tau^2); the truncated SE uses max(1, q).
    tempvar w r2
    quietly gen double `w' = 1/(s_se^2 + `t2')
    quietly gen double `r2' = `w'*(s_yi - `th')^2
    quietly summarize `r2'
    local hq = r(sum)/(`k' - 1)
    * Canonical-convention PI (t with k-1 df, only when k >= 5).
    local p1l = cond(`k' >= 5, `th' - invttail(`k'-1, .025)*sqrt(`t2' + `se'^2), .)
    local p1u = cond(`k' >= 5, `th' + invttail(`k'-1, .025)*sqrt(`t2' + `se'^2), .)
    * SMD models only: refit with Stata's default hedgesg SE to report the size of that convention difference.
    local at = .
    local al = .
    local au = .
    if measure[1] == "SMD" {
        meta clear
        meta set s_yi s_se_default, studylabel(study) random(reml)
        quietly meta summarize, `opt'
        local at = r(theta)
        local al = r(ci_lb)
        local au = r(ci_ub)
    }
    post `post' ("`set`i''") ("`mid`i''") (`k') (`N') (`th') (`se') (`lb') (`ub') (`t2') (`i2') (`q') (`hq') ///
        (`pl') (`pu') (`p1l') (`p1u') (`at') (`al') (`au') ("REML + truncated Knapp-Hartung")
    meta clear
}
postclose `post'
use "$STATA/work/results.dta", clear
format theta-alt_ci_ub %21.16g
export delimited using "$STATA/output/stata_model_results.csv", replace datafmt
log close mod
