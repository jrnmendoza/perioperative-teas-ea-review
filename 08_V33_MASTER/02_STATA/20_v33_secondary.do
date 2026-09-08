* ==============================================================================
* 20_v33_secondary.do
*   v33 secondary analyses enabled/expanded by the supplementary source audit
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 (authoritative inferential engine)
*   Master: TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx
* ==============================================================================
*
* SCOPE
*   This file does NOT touch the primary 0-24 h cumulative opioid analysis.
*   That model is unchanged at k=7 and is produced by 01_opioid24_primary.do.
*
*   Analyses here are deliberately kept apart from one another:
*     - binary rescue opioid USE is never pooled with opioid DOSE
*     - rescue administration COUNTS are never converted to a dose
*     - INTRAOPERATIVE opioid is never pooled with POSTOPERATIVE opioid
*     - PCA presses are never pooled with drug consumption
*     - non-opioid rescue (NSAIDs) is never pooled with opioid rescue
*
* MODEL
*   Random effects, REML. Hartung-Knapp is applied where k >= 3.
*   Prediction intervals are requested only where k >= 4: at k = 3 the
*   between-study variance is too poorly estimated for the interval to carry
*   meaning, and printing one would overstate what the data support.
* ==============================================================================

clear all
set more off
capture log close
log using "08_V33_MASTER/02_STATA/logs/20_v33_secondary.log", replace

di as txt "=================================================================="
di as txt "20: v33 SECONDARY ANALYSES"
di as txt "Engine : StataNow `c(stata_version)'  edition=`c(edition)'  flavor=`c(flavor)'"
di as txt "=================================================================="

tempname RES
postfile `RES' str40 analysis_id str60 outcome str28 measure double(k estimate ///
    ci_low ci_high p_value tau2 i2 q_stat pi_low pi_high) str24 model ///
    using "08_V33_MASTER/03_RESULTS/results_v33_secondary.dta", replace

* ------------------------------------------------------------------------------
* 1. BINARY RESCUE OPIOID USE, 0-24 h / POD1  (risk ratio)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "1. BINARY RESCUE OPIOID USE (0-24 h / POD1) -- log risk ratio"
di as txt "   Opioid rescue only. NSAID rescue is a different estimand."
di as txt "------------------------------------------------------------------"
import delimited "08_V33_MASTER/01_DATA/v33_rescue_opioid_binary_24h.csv", ///
    clear varnames(1) case(preserve) encoding("utf-8")
list study intervention comparator events_i n_i events_c n_c zero_cell, clean noobs
count
local k1 = r(N)

meta set lnrr se_lnrr, studylabel(study) eslabel("Log risk ratio")
meta summarize, random(reml) se(kh) eform(Risk ratio)
matrix R1 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
post `RES' ("V33_RESCUE_OPIOID_RR_24H") ("Binary rescue opioid use, 0-24 h/POD1") ///
    ("Risk ratio") (R1[1,5]) (exp(R1[1,1])) (exp(R1[1,2])) (exp(R1[1,3])) ///
    (R1[1,4]) (R1[1,6]) (R1[1,7]) (R1[1,8]) (.) (.) ("REML + Hartung-Knapp")

meta forestplot, eform(Risk ratio) ///
    title("Binary rescue opioid use, 0-24 h / POD1", size(medium)) ///
    subtitle("Random-effects REML + Hartung-Knapp (k=`k1')", size(vsmall)) ///
    nullrefline nonotes
graph export "08_V33_MASTER/04_FIGURES/forest_v33_rescue_opioid_rr.png", width(1800) replace

di as txt _n "Leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout eform(Risk ratio)

* ------------------------------------------------------------------------------
* 2. INTRAOPERATIVE REMIFENTANIL (ug)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. INTRAOPERATIVE REMIFENTANIL -- mean difference, ug"
di as txt "   mg rescaled to ug by an exact factor of 1000. No MME conversion."
di as txt "   Rate metrics (ug/kg/min) excluded as a different estimand."
di as txt "------------------------------------------------------------------"
import delimited "08_V33_MASTER/01_DATA/v33_intraop_remifentanil.csv", ///
    clear varnames(1) case(preserve) encoding("utf-8")
list study unit_src scale_factor n_i n_c md se, clean noobs
count
local k2 = r(N)

meta set md se, studylabel(study) eslabel("Mean difference (ug remifentanil)")
meta summarize, random(reml) se(kh) predinterval
matrix R2 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
local pil2 = r(pi_lb)
local piu2 = r(pi_ub)
post `RES' ("V33_INTRAOP_REMI_MD") ("Intraoperative remifentanil") ("MD (ug)") ///
    (R2[1,5]) (R2[1,1]) (R2[1,2]) (R2[1,3]) (R2[1,4]) (R2[1,6]) (R2[1,7]) ///
    (R2[1,8]) (`pil2') (`piu2') ("REML + Hartung-Knapp")

meta forestplot, ///
    title("Intraoperative remifentanil requirement", size(medium)) ///
    subtitle("Mean difference in ug; random-effects REML + Hartung-Knapp (k=`k2')", size(vsmall)) ///
    nullrefline nonotes
graph export "08_V33_MASTER/04_FIGURES/forest_v33_intraop_remifentanil.png", width(1800) replace

di as txt _n "Leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout

di as txt _n "SMD (scale-free) cross-check:"
meta set hedges_g hedges_se, studylabel(study) eslabel("Hedges g")
meta summarize, random(reml) se(kh)
matrix R2s = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
post `RES' ("V33_INTRAOP_REMI_SMD") ("Intraoperative remifentanil") ("Hedges g") ///
    (R2s[1,5]) (R2s[1,1]) (R2s[1,2]) (R2s[1,3]) (R2s[1,4]) (R2s[1,6]) (R2s[1,7]) ///
    (R2s[1,8]) (.) (.) ("REML + Hartung-Knapp")

* ------------------------------------------------------------------------------
* 3. INTRAOPERATIVE SUFENTANIL (ug)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. INTRAOPERATIVE SUFENTANIL -- mean difference, ug"
di as txt "------------------------------------------------------------------"
import delimited "08_V33_MASTER/01_DATA/v33_intraop_sufentanil.csv", ///
    clear varnames(1) case(preserve) encoding("utf-8")
list study intervention n_i n_c mean_i mean_c md se, clean noobs
count
local k3 = r(N)

meta set md se, studylabel(study) eslabel("Mean difference (ug sufentanil)")
meta summarize, random(reml) se(kh) predinterval
matrix R3 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
local pil3 = r(pi_lb)
local piu3 = r(pi_ub)
post `RES' ("V33_INTRAOP_SUF_MD") ("Intraoperative sufentanil") ("MD (ug)") ///
    (R3[1,5]) (R3[1,1]) (R3[1,2]) (R3[1,3]) (R3[1,4]) (R3[1,6]) (R3[1,7]) ///
    (R3[1,8]) (`pil3') (`piu3') ("REML + Hartung-Knapp")

meta forestplot, ///
    title("Intraoperative sufentanil requirement", size(medium)) ///
    subtitle("Mean difference in ug; random-effects REML + Hartung-Knapp (k=`k3')", size(vsmall)) ///
    nullrefline nonotes
graph export "08_V33_MASTER/04_FIGURES/forest_v33_intraop_sufentanil.png", width(1800) replace

di as txt _n "Leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout

* ------------------------------------------------------------------------------
* 4. GLOBAL QoR-40 AT ~24 h
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "4. GLOBAL QoR-40 AT ~24 h -- mean difference, QoR-40 points"
di as txt "   QoR-15 is a different instrument and is not pooled here."
di as txt "------------------------------------------------------------------"
import delimited "08_V33_MASTER/01_DATA/v33_qor40_24h.csv", ///
    clear varnames(1) case(preserve) encoding("utf-8")
list study window n_i n_c mean_i sd_i mean_c sd_c md se, clean noobs
count
local k4 = r(N)

meta set md se, studylabel(study) eslabel("Mean difference (QoR-40 points)")
meta summarize, random(reml) se(kh)
matrix R4 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
post `RES' ("V33_QOR40_24H_MD") ("Global QoR-40 at ~24 h") ("MD (points)") ///
    (R4[1,5]) (R4[1,1]) (R4[1,2]) (R4[1,3]) (R4[1,4]) (R4[1,6]) (R4[1,7]) ///
    (R4[1,8]) (.) (.) ("REML + Hartung-Knapp")

meta forestplot, ///
    title("Global QoR-40 at ~24 h", size(medium)) ///
    subtitle("Mean difference in QoR-40 points; REML + Hartung-Knapp (k=`k4')", size(vsmall)) ///
    nullrefline nonotes
graph export "08_V33_MASTER/04_FIGURES/forest_v33_qor40_24h.png", width(1800) replace

di as txt _n "Leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout

* ------------------------------------------------------------------------------
* 5. TIME TO FIRST DEFECATION (h)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "5. TIME TO FIRST DEFECATION -- mean difference, hours"
di as txt "------------------------------------------------------------------"
import delimited "08_V33_MASTER/01_DATA/v33_gi_first_defecation.csv", ///
    clear varnames(1) case(preserve) encoding("utf-8")
list study n_i n_c mean_i sd_i mean_c sd_c md se, clean noobs
count
local k5 = r(N)

meta set md se, studylabel(study) eslabel("Mean difference (hours)")
meta summarize, random(reml) se(kh) predinterval
matrix R5 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))
local pil5 = r(pi_lb)
local piu5 = r(pi_ub)
post `RES' ("V33_GI_DEFECATION_MD") ("Time to first defecation") ("MD (hours)") ///
    (R5[1,5]) (R5[1,1]) (R5[1,2]) (R5[1,3]) (R5[1,4]) (R5[1,6]) (R5[1,7]) ///
    (R5[1,8]) (`pil5') (`piu5') ("REML + Hartung-Knapp")

meta forestplot, ///
    title("Time to first postoperative defecation", size(medium)) ///
    subtitle("Mean difference in hours; REML + Hartung-Knapp (k=`k5')", size(vsmall)) ///
    nullrefline nonotes
graph export "08_V33_MASTER/04_FIGURES/forest_v33_gi_defecation.png", width(1800) replace

di as txt _n "Leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout

di as txt _n "Sensitivity: exclude the newly added Yang 2020 contrast"
meta summarize if study != "Yang 2020", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 6. EXPORT
* ------------------------------------------------------------------------------
postclose `RES'
use "08_V33_MASTER/03_RESULTS/results_v33_secondary.dta", clear
gen master = "TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx"
order analysis_id outcome measure k estimate ci_low ci_high p_value tau2 i2 q_stat
export delimited "08_V33_MASTER/03_RESULTS/results_v33_secondary.csv", replace
save "08_V33_MASTER/03_RESULTS/results_v33_secondary.dta", replace
list analysis_id k estimate ci_low ci_high p_value i2, clean noobs

di as txt _n "SUCCESS: v33 secondary analyses complete."
log close
