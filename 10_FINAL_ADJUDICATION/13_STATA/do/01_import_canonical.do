* 01_import_canonical.do -- read the exported canonical inputs (code/export_stata_inputs.py). No values are entered by hand.
log using "$STATA/logs/01_import_canonical.log", text replace name(imp)
import delimited using "$STATA/input/stata_models.csv", clear varnames(1) bindquote(strict) stringcols(_all)
destring k, replace
gen int model_order = _n
save "$STATA/work/models.dta", replace
import delimited using "$STATA/input/stata_model_inputs.csv", clear varnames(1) bindquote(strict) stringcols(_all)
destring row n_i mean_i sd_i events_i n_c mean_c sd_c events_c canonical_yi canonical_vi, replace
merge m:1 analysis_set model_id using "$STATA/work/models.dta", keepusing(measure) assert(match using) keep(match) nogenerate
sort analysis_set model_id row
save "$STATA/work/inputs.dta", replace
log close imp
