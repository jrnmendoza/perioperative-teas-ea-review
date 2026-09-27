* 05_descriptives.do -- descriptive figures and table of the evidence base from the harmonised characteristics
* (14_CHARACTERISTICS/report_characteristics_wide.csv, built by code/build_characteristics.py).
* Counts are REPORTS (70 reports from 69 operational trial families), not independent patients.
log using "$STATA/logs/05_descriptives.log", text replace name(desc)
import delimited using "$ROOT/10_FINAL_ADJUDICATION/14_CHARACTERISTICS/report_characteristics_wide.csv", clear varnames(1) bindquote(strict) stringcols(_all)
destring year randomized_n randomized_n_counted, replace
assert _N == 70
quietly levelsof trial_family
local nfam = r(r)
local src "Source: 14_CHARACTERISTICS/report_characteristics.csv (harmonised; surgical category source-traced)."
local sw "StataNow/SE `c(stata_version)', 13_STATA/do/05_descriptives.do."
local unit "Counts are reports (`=_N' reports from `nfam' operational trial families), not independent patients."
local ex "xsize(8) ysize(4.8)"
program drop _all
program define export3
    args id
    graph export "$STATA/figures/`id'.svg", replace
    graph export "$STATA/figures/`id'.pdf", replace
    graph export "$STATA/figures/`id'.png", replace width(2400)
end
* Publication year
graph bar (count), over(year, label(angle(90) labsize(small))) ytitle("Reports") title("Included reports by publication year", size(medium)) ///
    note("`unit'" "`src'" "`sw'", size(vsmall)) `ex' name(year, replace)
export3 fig_desc_publication_year
* Surgical category
graph hbar (count), over(surgical_category, sort(1) descending) ytitle("Reports") title("Included reports by surgical category", size(medium)) ///
    note("`unit'" "`src'" "`sw'", size(vsmall)) `ex' name(surg, replace)
export3 fig_desc_surgical_category
* Country
graph hbar (count), over(country, sort(1) descending) ytitle("Reports") title("Included reports by country", size(medium)) ///
    note("`unit'" "`src'" "`sw'", size(vsmall)) `ex' name(ctry, replace)
export3 fig_desc_country
* Randomised sample size per report
quietly summarize randomized_n, detail
local med = r(p50)
local q1 = r(p25)
local q3 = r(p75)
histogram randomized_n, frequency width(25) start(0) xtitle("Randomised participants per report") ytitle("Reports") ///
    title("Randomised sample size per report", size(medium)) subtitle("Median `med' (IQR `q1'-`q3')", size(small)) ///
    note("`unit'" "`src'" "`sw'", size(vsmall)) `ex' name(size, replace)
export3 fig_desc_sample_size
* Modality by comparator class (study-level label)
graph bar (count), over(comparator_class) over(modality) asyvars ytitle("Reports") legend(rows(1) size(small) position(6)) ///
    title("Modality and comparator class", size(medium)) subtitle("Study-level labels; result-level comparator classes govern model membership", size(small)) ///
    note("`unit'" "`src'" "`sw'", size(vsmall)) `ex' name(modcmp, replace)
export3 fig_desc_modality_comparator
* Combined evidence-base panel (manuscript candidate): dedicated components without per-panel notes.
graph hbar (count), over(surgical_category, sort(1) descending label(labsize(small))) ytitle("Reports") title("A. Surgical category", size(medium)) nodraw name(p1, replace)
histogram randomized_n, frequency width(50) start(0) xtitle("Randomised participants per report") ytitle("Reports") ///
    title("B. Randomised sample size", size(medium)) subtitle("Median `med' (IQR `q1'-`q3')", size(small)) nodraw name(p2, replace)
graph bar (count), over(comparator_class) over(modality) asyvars ytitle("Reports") legend(rows(1) size(small) position(6)) ///
    title("C. Modality and comparator class", size(medium)) nodraw name(p3, replace)
graph bar (count), over(year, label(angle(90) labsize(vsmall))) ytitle("Reports") title("D. Publication year", size(medium)) nodraw name(p4, replace)
graph combine p1 p2 p3 p4, cols(2) xsize(12) ysize(9) iscale(.6) imargin(small) title("Evidence base: `=_N' reports from `nfam' trial families", size(medium)) ///
    note("`unit'" "Panel C uses study-level comparator labels; result-level comparator classes govern model membership." "`src'" "`sw'", size(vsmall)) name(panel, replace)
export3 fig_desc_evidence_base
* Summary table
tempname fh
file open `fh' using "$STATA/tables/characteristics_summary.csv", write replace text
file write `fh' "characteristic,category,reports" _n
foreach v in modality comparator_class surgical_category country {
    quietly levelsof `v', local(cats)
    foreach c of local cats {
        quietly count if `v' == `"`c'"'
        file write `fh' `"`v',"`c'",`r(N)'"' _n
    }
}
quietly summarize randomized_n, detail
file write `fh' "randomized_n,median,`r(p50)'" _n "randomized_n,p25,`r(p25)'" _n "randomized_n,p75,`r(p75)'" _n "randomized_n,total (reported),`r(sum)'" _n
quietly summarize randomized_n_counted
file write `fh' "randomized_n_counted,total (operational count),`r(sum)'" _n
file write `fh' "trial_family,distinct,`nfam'" _n
file close `fh'
log close desc
