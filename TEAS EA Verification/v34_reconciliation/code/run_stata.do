clear all
set more off
capture log close
log using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_analysis.log", replace
tempname OUT
postfile `OUT' str100 analysis_id str20 phase str10 measure double(k estimate ci_low ci_high p_value tau2 i2) str25 model using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_model_results.dta", replace
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_intraop_remifentanil_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("intraop_remifentanil_TEAS_Sham") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_intraop_remifentanil_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("intraop_remifentanil_TEAS_Sham") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_intraop_sufentanil_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml)
post `OUT' ("intraop_sufentanil_TEAS_Sham") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML normal CI")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_qor40_24h_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml)
post `OUT' ("qor40_24h_TEAS_Sham") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML normal CI")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_qor40_24h_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml)
post `OUT' ("qor40_24h_TEAS_Sham") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML normal CI")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_gi_first_defecation_EA_Usual_care.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("gi_first_defecation_EA_Usual_care") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_gi_first_defecation_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("gi_first_defecation_TEAS_Sham") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_gi_first_defecation_EA_Usual_care.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("gi_first_defecation_EA_Usual_care") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_gi_first_defecation_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("gi_first_defecation_TEAS_Sham") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_primary_24h_mme_EA_Usual_care.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_EA_Usual_care") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_primary_24h_mme_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_TEAS_Sham") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_primary_24h_mme_EA_Usual_care.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_EA_Usual_care") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_primary_24h_mme_TEAS_Sham.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_TEAS_Sham") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v34_primary_24h_mme_ALL_AUDIT.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_ALL_AUDIT") ("v34") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
import delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/data/v33_matched_primary_24h_mme_ALL_AUDIT.csv", clear varnames(1) encoding("utf-8")
assert !missing(effect,se) & se>0
meta set effect se, studylabel(study)
meta summarize, random(reml) se(kh)
post `OUT' ("primary_24h_mme_ALL_AUDIT") ("v33_matched") ("MD") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML + Hartung-Knapp")
postclose `OUT'
use "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_model_results.dta", clear
export delimited "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/v34_reconciliation/results/v34_model_results.csv", replace
display "V34_ANALYSIS_SUCCESS"
log close
