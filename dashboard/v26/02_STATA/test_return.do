capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/test_return.log", replace
use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
meta set md_mme se_mme if inc_primary == 1
meta summarize, random(reml) se(kh)
return list
log close
