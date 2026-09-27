* 02_effect_sizes.do -- Stata computes every study effect size from arm-level data with official -meta esize-,
* then checks it against the canonical yi/vi row by row.
*   MD : esize(mdiff, unequal)   SE = sqrt(sd_i^2/n_i + sd_c^2/n_c)   (arm means are stored after unit conversion)
*   SMD: esize(hedgesg, exact)   exact small-sample correction J, as the canonical pipeline. The SE follows the canonical
*        specification (Hedges-Olkin large-sample variance, as metafor): (n_i+n_c)/(n_i*n_c) + g^2/(2(n_i+n_c)).
*        Stata's default hedgesg SE (J x SE of d) is kept in s_se_default and fitted as a reported alternative.
*   RR : esize(lnrratio)         log risk ratio from 2x2 counts; no zero cells occur (asserted)
log using "$STATA/logs/02_effect_sizes.log", text replace name(es)
use "$STATA/work/inputs.dta", clear
gen double s_yi = .
gen double s_se = .
foreach spec in "MD|mdiff, unequal" "SMD|hedgesg, exact" {
    gettoken meas es : spec, parse("|")
    local es = substr("`es'", 2, .)
    count if measure == "`meas'"
    if r(N) {
        meta esize n_i mean_i sd_i n_c mean_c sd_c if measure == "`meas'", esize(`es')
        replace s_yi = _meta_es if measure == "`meas'"
        replace s_se = _meta_se if measure == "`meas'"
        meta clear
        capture drop _meta_*
    }
}
gen double a = events_i
gen double b = n_i - events_i
gen double c = events_c
gen double dd = n_c - events_c
assert a > 0 & b > 0 & c > 0 & dd > 0 if measure == "RR"
meta esize a b c dd if measure == "RR", esize(lnrratio)
replace s_yi = _meta_es if measure == "RR"
replace s_se = _meta_se if measure == "RR"
meta clear
capture drop _meta_*
drop a b c dd
gen double s_se_default = s_se if measure == "SMD"
replace s_se = sqrt((n_i + n_c)/(n_i*n_c) + s_yi^2/(2*(n_i + n_c))) if measure == "SMD"
assert !missing(s_yi, s_se)
gen double diff_yi = s_yi - canonical_yi
gen double diff_se = s_se - sqrt(canonical_vi)
summarize diff_yi diff_se
save "$STATA/work/inputs_es.dta", replace
format canonical_yi s_yi diff_yi canonical_vi s_se diff_se %21.16g
export delimited analysis_set model_id row study result_id measure canonical_yi s_yi diff_yi canonical_vi s_se diff_se ///
    using "$STATA/output/stata_effect_size_check.csv", replace datafmt
log close es
