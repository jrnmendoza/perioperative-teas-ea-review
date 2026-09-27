* 04_figures.do -- publication figures from input/figure_specs.csv (generated from the canonical model list by rule).
* Same specification as 03_models.do: REML, truncated Knapp-Hartung, tight tolerances; k = 1 is shown unpooled.
* The x axis always covers study CIs, the pooled CI, the prediction interval (k >= 5), the null and any threshold.
* Each figure is exported as SVG (web), PDF (vector, manuscript) and PNG (2400 px). Values in notes are computed here.
log using "$STATA/logs/04_figures.log", text replace name(fig)

capture program drop fmtnum
program define fmtnum, rclass
    * Trimmed number with a leading zero ("0.034", "-0.9").
    args x fmt
    local s = strtrim(string(`x', "`fmt'"))
    if substr("`s'", 1, 1) == "." local s "0`s'"
    if substr("`s'", 1, 2) == "-." local s = "-0" + substr("`s'", 2, .)
    return local s "`s'"
end

capture program drop fmtp
program define fmtp, rclass
    * "p < 0.001" or "p = 0.034" (three decimals, leading zero).
    args x
    if `x' < .001 return local s "p < 0.001"
    else {
        fmtnum `x' %5.3f
        return local s "p = `r(s)'"
    }
end

capture program drop niceaxis
program define niceaxis, rclass
    * Axis range and labels for [lo, hi] (log scale when ef == 1; values then exponentiated for -eform- plots).
    args lo hi ef
    local pad = (`hi' - `lo')*.05
    local lo = `lo' - `pad'
    local hi = `hi' + `pad'
    if "`ef'" == "1" {
        * First label set with 2-8 labels that spans at least half the axis (no crowded or bunched labels).
        foreach set in ".25 .5 .75 1 1.5 2 3" ".1 .2 .5 1 2 5 10" ".05 .1 .2 .5 1 2 5 10 20" ".01 .1 1 10 100" ".001 .01 .1 1 10 100 1000" {
            local labs ""
            local n = 0
            local cmin = .
            local cmax = 0
            foreach c of local set {
                if ln(`c') >= `lo' & ln(`c') <= `hi' {
                    fmtnum `c' %9.0g
                    local labs `"`labs' `c' "`r(s)'""'
                    local ++n
                    local cmin = min(`cmin', `c')
                    local cmax = max(`cmax', `c')
                }
            }
            if `n' <= 8 & `n' >= 2 & ln(`cmax') - ln(`cmin') >= .5*(`hi' - `lo') continue, break
        }
        return local range = "`=exp(`lo')' `=exp(`hi')'"
        return local labels `"`labs'"'
    }
    else {
        local raw = (`hi' - `lo')/5
        local p = 10^floor(log10(`raw'))
        local step ""
        foreach m in 1 2 2.5 5 10 {
            if "`step'" == "" & `m'*`p' >= `raw' local step = `m'*`p'
        }
        local a = floor(`lo'/`step')*`step'
        local b = ceil(`hi'/`step')*`step'
        return local range "`a' `b'"
        return local labels "`a'(`step')`b'"
    }
end

import delimited using "$STATA/input/figure_specs.csv", clear varnames(1) bindquote(strict) stringcols(_all)
local nf = _N
foreach v in figure_id kind analysis_set model_id title subtitle xtitle eform threshold {
    forvalues j = 1/`nf' {
        local `v'`j' = `v'[`j']
    }
}
tempname reg sst
postfile `reg' str60 figure_id str8 kind str16 analysis_set str80 model_id int k long N double(theta ci_lb ci_ub tau2 I2 pi_lb pi_ub) ///
    using "$STATA/work/figure_values.dta", replace
postfile `sst' str80 model_id int k str20 test double(stat p) using "$STATA/work/small_study.dta", replace
local opt se(khartung, truncated) tolerance(1e-14) nrtolerance(1e-14) iterate(1000)
forvalues j = 1/`nf' {
    use "$STATA/work/inputs_es.dta", clear
    keep if analysis_set == "`analysis_set`j''" & model_id == "`model_id`j''"
    local k = _N
    assert `k' >= 1
    quietly summarize n_i
    local N = r(sum)
    quietly summarize n_c
    local N = `N' + r(sum)
    local isrr = "`eform`j''" == "1"
    local ef = cond(`isrr', "eform", "")
    local xl = cond("`threshold`j''" != "", "xline(`threshold`j'', lpattern(shortdash) lcolor(orange) lwidth(medthick))", "")
    local esname = cond(`isrr', "Risk ratio", "Mean difference")
    meta set s_yi s_se, studylabel(study) random(reml)
    local th = s_yi[1]
    local lb = s_yi[1] - invnormal(.975)*s_se[1]
    local ub = s_yi[1] + invnormal(.975)*s_se[1]
    local t2 = 0
    local i2 = .
    local pl = .
    local pu = .
    if `k' >= 2 {
        quietly meta summarize, `opt'
        local th = r(theta)
        local lb = r(ci_lb)
        local ub = r(ci_ub)
        local t2 = r(tau2)
        local i2 = r(I2)
        local q = r(Q)
        local qdf = r(df_Q)
        local qp = r(p_Q)
        if `k' >= 5 {
            local pl = r(theta) - invttail(`k'-1, .025)*sqrt(r(tau2) + r(se)^2)
            local pu = r(theta) + invttail(`k'-1, .025)*sqrt(r(tau2) + r(se)^2)
        }
    }
    post `reg' ("`figure_id`j''") ("`kind`j''") ("`analysis_set`j''") ("`model_id`j''") (`k') (`N') (`th') (`lb') (`ub') (`t2') (`i2') (`pl') (`pu')
    * Axis extent (log scale for risk ratios).
    tempvar sl su
    quietly gen double `sl' = s_yi - invnormal(.975)*s_se
    quietly gen double `su' = s_yi + invnormal(.975)*s_se
    quietly summarize `sl'
    local xlo = min(r(min), `lb', 0)
    quietly summarize `su'
    local xhi = max(r(max), `ub', 0)
    if `pl' < . local xlo = min(`xlo', `pl')
    if `pu' < . local xhi = max(`xhi', `pu')
    if "`threshold`j''" != "" {
        local xlo = min(`xlo', `threshold`j'')
        local xhi = max(`xhi', `threshold`j'')
    }
    if "`kind`j''" == "loo" {
        quietly meta summarize, leaveoneout `opt'
        matrix L = r(leaveoneout)
        forvalues r = 1/`=rowsof(L)' {
            local xlo = min(`xlo', L[`r', "ci_lb"])
            local xhi = max(`xhi', L[`r', "ci_ub"])
        }
    }
    niceaxis `xlo' `xhi' `isrr'
    local axis `"xscale(range(`r(range)')) xlabel(`r(labels)')"'
    * Notes: what was fitted, with the values Stata computed.
    * Summary rows under the pooled estimate replace Stata's defaults: heterogeneity with Q and a formatted p,
    * and the prediction interval in the canonical t(k-1) convention (Stata's own PI uses k-2). No test of theta = 0.
    local tr = cond(`isrr', "exp", "")
    fmtnum `t2' %9.3g
    local t2s "`r(s)'"
    local studies = cond(`k' == 1, "1 study", "`k' studies")
    local PIs ""
    if `pl' < . {
        fmtnum `tr'(`pl') %9.2f
        local a "`r(s)'"
        fmtnum `tr'(`pu') %9.2f
        local PIs "95% prediction interval: `a' to `r(s)'"
    }
    * Short lines (Stata sizes the label column to its widest text).
    local HET ""
    local HOM ""
    if `k' >= 2 {
        fmtp `qp'
        local HET "Heterogeneity: {&tau}{superscript:2} = `t2s', I{superscript:2} = `: display %4.1f `i2''%"
        local HOM "Test of homogeneity: Q(`qdf') = `: display %4.2f `q'', `r(s)'"
    }
    local THR ""
    if "`threshold`j''" != "" local THR "Dotted line: -10 mg IV MME registered clinical-importance threshold."
    if `k' == 1 local L1 "k = 1 study; N = `N' participants. Single study: estimate with normal 95% CI; not pooled."
    else        local L1 "k = `studies'; N = `N' participants. Random effects: REML, truncated Knapp-Hartung 95% CI (t, k-1 df)`=cond(`pl' < ., "; prediction interval t, k-1 df", "")'."
    local L2 "`THR'"
    local summ noosigtest
    if `k' == 1 local summ noohetstats noohomtest noosigtest
    else if "`PIs'" == "" local summ ohetstatstext("`HET'") ohomtesttext("`HOM'") noosigtest
    else local summ ohetstatstext("`HET'") ohomtesttext("`HOM'") osigtesttext("`PIs'")
    local esci columnopts(_esci, supertitle("`esname'"))
    local L3 "Model `model_id`j'' (`analysis_set`j''). StataNow/SE `c(stata_version)', 13_STATA/do/04_figures.do."
    local ys = max(3.6, 2.4 + 0.34*`k')
    local base title("`title`j''", size(medium)) subtitle("`subtitle`j''", size(small)) xtitle("`xtitle`j''") xsize(9) ysize(`ys') name(g, replace)
    if "`kind`j''" == "funnel" {
        gen double a = events_i
        gen double b = n_i - events_i
        gen double c = events_c
        gen double dd = n_c - events_c
        meta clear
        meta esize a b c dd, esize(lnrratio) studylabel(study) random(reml)
        quietly meta bias, harbord
        local hz = r(z)
        local hp = r(p)
        post `sst' ("`model_id`j''") (`k') ("Harbord") (`hz') (`hp')
        local F1 "k = `k' studies; contours mark two-sided p-value regions around no effect; vertical line: inverse-variance (common-effect) estimate."
        fmtp `hp'
        local F2 "Harbord test for small-study effects: z = `: display %5.2f `hz'', `r(s)'. Low power at k = 10; exploratory, not used for GRADE."
        meta funnelplot, contours(1 5 10) `base' note(`"`F1'"' `"`F2'"' `"`L3'"', size(vsmall))
    }
    else {
        if "`L2'" == "" local notes note(`"`L1'"' `"`L3'"', size(vsmall))
        else            local notes note(`"`L1'"' `"`L2'"' `"`L3'"', size(vsmall))
        if "`kind`j''" == "loo" {
            * Leave-one-out: no p-value column; the solid line is the estimate with all k studies (stated in the notes).
            fmtnum `tr'(`th') %9.2f
            local e0 "`r(s)'"
            fmtnum `tr'(`lb') %9.2f
            local e1 "`r(s)'"
            fmtnum `tr'(`ub') %9.2f
            local LA "Each row re-fits the random-effects model (REML, truncated Knapp-Hartung) without the named study."
            local LB "Solid line: estimate with all `k' studies, `e0' [`e1', `r(s)']. `HET'; `HOM'."
            local LC = cond("`PIs'" == "", "", "`PIs' (t, k-1 df)")
            if "`THR'" != "" & "`LC'" != "" local LC "`LC'. `THR'"
            else if "`THR'" != "" local LC "`THR'"
            if "`LC'" == "" local notes note(`"`LA'"' `"`LB'"' `"`L3'"', size(vsmall))
            else            local notes note(`"`LA'"' `"`LB'"' `"`LC'"' `"`L3'"', size(vsmall))
            meta forestplot _id _plot _esci, leaveoneout `opt' nullrefline `ef' `xl' `axis' `esci' `base' `notes'
            preserve
            clear
            svmat double L, names(col)
            gen str80 model_id = "`model_id`j''"
            quietly ds, has(type numeric)
            format `r(varlist)' %21.16g
            export delimited using "$STATA/output/leaveoneout_`model_id`j''.csv", replace datafmt
            restore
        }
        else if `k' == 1 meta forestplot _id _plot _esci, nooverall `summ' nullrefline `ef' `xl' `axis' `esci' `base' `notes'
        else             meta forestplot _id _plot _esci _weight, `opt' `summ' nullrefline `ef' `xl' `axis' `esci' `base' `notes'
    }
    graph export "$STATA/figures/`figure_id`j''.svg", replace
    graph export "$STATA/figures/`figure_id`j''.pdf", replace
    graph export "$STATA/figures/`figure_id`j''.png", replace width(2400)
    meta clear
}
postclose `reg'
postclose `sst'
use "$STATA/work/figure_values.dta", clear
format theta-pi_ub %21.16g
export delimited using "$STATA/output/figure_values.csv", replace datafmt
use "$STATA/work/small_study.dta", clear
format stat p %21.16g
export delimited using "$STATA/output/small_study_tests.csv", replace datafmt
log close fig
