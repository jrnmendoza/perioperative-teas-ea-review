* ==============================================================================
* 15_stratum_compliant_diagnostic.do
*   DIAGNOSTIC ONLY -- what the protocol-compliant strata would give
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
* ==============================================================================
*
* WHY THIS EXISTS
*   scripts/check_stratum_purity.py reports that three reported analyses pool
*   across protocol strata: Target A, Target D 0-48 h and Target E. The locked
*   protocol stratifies by modality (TEAS vs EA) and does not combine
*   sham/placebo with usual-care comparators; 06_flatus.do and its siblings
*   apply no such condition.
*
*   The review team asked what splitting them would actually give, so this fits
*   each protocol-compliant stratum that has k >= 2 and records it.
*
* WHAT THIS IS NOT
*   Not a finding, not a replacement, not an alternative headline. It changes no
*   locked dataset and writes to its own results file. The reported analyses and
*   their "pools across protocol strata" warnings are untouched. Whether to
*   report stratified results instead is a review-team decision this file exists
*   to inform, not to pre-empt.
*
* MEMBERSHIP (from the stratum screen; Zhang 2018 read as TEAS on the source --
* "Needleless Transcutaneous Electrical Acustimulation", surface electrodes at
* ST36 and PC6 -- because the v34 outcome register leaves its modality unfilled)
*   Target E  TEAS vs Sham ........ k=3  Xing 2022, Zhang 2018, Zhou 2025
*             EA vs Usual care .... k=2  Yang 2020, Yang 2024
*             EA vs Sham ......... k=1  Ng 2013            (not estimable)
*             TEAS vs Usual care . k=1  Lu 2022            (not estimable)
*   Target A  TEAS vs Sham ........ k=2  Chen 2020, Zhang 2023
*             EA vs Usual care ... k=1  An 2014            (not estimable)
*   Target D 0-48 h: both strata are k=1 -- nothing is estimable at all.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/15_stratum_compliant_diagnostic.log", replace

di as txt "=================================================================="
di as txt "15: PROTOCOL-COMPLIANT STRATUM DIAGNOSTIC  (NOT A REPORTED FINDING)"
di as txt "=================================================================="

tempfile out
postfile h str44 stratum k double(est lo hi pval i2 tau2) using `out', replace

* ---------- Target E: time to first flatus, mean difference in hours ----------
use "06_FINAL_ANALYSIS_V26/01_DATA/target_E_flatus.dta", clear
meta set md_hours se_hours, studylabel(study) eslabel("Mean Difference (Hours)")

di as txt _n "--- Target E / TEAS vs Sham (k=3) ---"
meta summarize if inlist(study, "Xing 2022", "Zhang 2018", "Zhou 2025"), random(reml) se(kh)
scalar kk = r(N) 
 scalar pp = r(p)
post h ("TE_FLATUS_TEAS_SHAM") (kk) (r(theta)) (r(ci_lb)) (r(ci_ub)) ///
       (pp) (r(I2)) (r(tau2))

di as txt _n "--- Target E / EA vs Usual care (k=2) ---"
meta summarize if inlist(study, "Yang 2020", "Yang 2024"), random(reml) se(kh)
scalar kk = r(N) 
 scalar pp = r(p)
post h ("TE_FLATUS_EA_USUAL") (kk) (r(theta)) (r(ci_lb)) (r(ci_ub)) ///
       (pp) (r(I2)) (r(tau2))

* ---------- Target A: 48-h opioid, mean difference in mg IV MME --------------
use "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta", clear
capture confirm variable md_mme
if !_rc {
    meta set md_mme se_mme, studylabel(study) eslabel("Mean Difference (mg IV MME)")
    di as txt _n "--- Target A / TEAS vs Sham (k=2) ---"
    meta summarize if inlist(study, "Chen 2020", "Zhang 2023"), random(reml) se(kh)
    scalar kk = r(N) 
    scalar pp = r(p)
    post h ("TA_48H_TEAS_SHAM") (kk) (r(theta)) (r(ci_lb)) (r(ci_ub)) ///
           (pp) (r(I2)) (r(tau2))
}
else {
    di as error "target_A_48h.dta has no md_mme; Target A stratum not fitted"
}

postclose h
use `out', clear
list, noobs sep(0)
export delimited using ///
  "06_FINAL_ANALYSIS_V26/03_RESULTS/results_stratum_compliant_diagnostic.csv", replace

di as txt _n "=================================================================="
di as txt "DIAGNOSTIC ONLY. Target D 0-48 h has no stratum with k>=2 and is"
di as txt "therefore absent from this file entirely."
di as txt "=================================================================="
log close
