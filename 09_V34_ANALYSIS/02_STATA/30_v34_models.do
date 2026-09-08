* ==============================================================================
* 30_v34_models.do
*   v34 analysis set: independent reproduction of the eight reconciliation
*   models, plus five additional protocol-supported models.
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 (authoritative inferential engine)
*   Master: TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx
* ==============================================================================
*
* ESTIMATOR RULES (unchanged from the v34 reconciliation, applied consistently)
*   REML throughout.
*   k >= 3 : Hartung-Knapp adjusted CI on a t reference distribution.
*   k = 2  : REML with a normal CI. Hartung-Knapp on two studies gives an
*            interval driven almost entirely by a single degree of freedom.
*   k = 1  : no pooled estimate is produced at all.
*
* STRATIFICATION
*   Every model is a single modality against a single comparator type. TEAS and
*   EA are never combined; sham and usual care are never combined. This is the
*   correction the v34 reconciliation applied to the secondary analyses, and it
*   is applied to the new models here for the same reason.
*
* WHAT THIS FILE DOES NOT DO
*   It does not re-fit the strict primary opioid model, which is unchanged at
*   k=7 and is produced by 06_FINAL_ANALYSIS_V26/02_STATA/01_opioid24_primary.do.
*   It reproduces the primary here only as a numerical consistency check.
* ==============================================================================

clear all
set more off
capture log close
log using "09_V34_ANALYSIS/02_STATA/logs/30_v34_models.log", replace

di as txt "=================================================================="
di as txt "30: v34 ANALYSIS SET"
di as txt "Engine : StataNow `c(stata_version)'  edition=`c(edition)'  flavor=`c(flavor)'"
di as txt "=================================================================="

tempname R
postfile `R' str48 model_id str10 measure double(k estimate ci_low ci_high ///
    p_value tau2 i2) str24 estimator str16 phase ///
    using "09_V34_ANALYSIS/03_RESULTS/v34_models.dta", replace

* ------------------------------------------------------------------------------
* Helper: fit one model from a prepared CSV and post the result.
*   k >= 3 -> Hartung-Knapp; k = 2 -> normal CI.
* ------------------------------------------------------------------------------
capture program drop fitmodel
program define fitmodel
    args path mid measure eslabel
    preserve
    import delimited "`path'", clear varnames(1) case(preserve) encoding("utf-8")
    quietly count
    local k = r(N)
    di as txt _n "------------------------------------------------------------------"
    di as txt "`mid'   (k = `k', measure = `measure')"
    di as txt "------------------------------------------------------------------"
    list study n_i n_c effect se, clean noobs

    if `k' < 2 {
        di as error "k < 2: no pooled estimate produced."
        restore
        exit
    }

    meta set effect se, studylabel(study) eslabel("`eslabel'")
    if `k' >= 3 {
        meta summarize, random(reml) se(kh)
        local est "REML + Hartung-Knapp"
    }
    else {
        meta summarize, random(reml)
        local est "REML normal CI"
    }
    matrix M = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2))
    global M_est  = M[1,1]
    global M_lo   = M[1,2]
    global M_hi   = M[1,3]
    global M_p    = M[1,4]
    global M_k    = M[1,5]
    global M_tau2 = M[1,6]
    global M_i2   = M[1,7]
    global M_model "`est'"

    if `k' >= 3 {
        di as txt _n "Leave-one-out:"
        meta summarize, random(reml) se(kh) leaveoneout
    }
    restore
end

* ==============================================================================
* PART A -- five additional protocol-supported models
* ==============================================================================
di as txt _n "=================================================================="
di as txt "PART A: additional models supported by the expanded v34 data"
di as txt "=================================================================="

foreach spec in ///
    "gi_first_flatus_TEAS_Sham MD Mean_difference_hours" ///
    "gi_first_flatus_EA_Usual_care MD Mean_difference_hours" ///
    "gi_first_bowel_sounds_TEAS_Sham MD Mean_difference_hours" ///
    "pain_vas_24h_TEAS_Sham MD Mean_difference_VAS" ///
    "ponv_24h_TEAS_Sham logRR Log_risk_ratio" {

    local mid    : word 1 of `spec'
    local meas   : word 2 of `spec'
    local lab    : word 3 of `spec'
    fitmodel "09_V34_ANALYSIS/01_DATA/`mid'.csv" "`mid'" "`meas'" "`lab'"
    post `R' ("`mid'") ("`meas'") ($M_k) ($M_est) ($M_lo) ($M_hi) ($M_p) ///
             ($M_tau2) ($M_i2) ("$M_model") ("NEW")
}

* ==============================================================================
* PART B -- independent reproduction of the eight reconciliation models
* Reproduced from the reconciliation's own prepared datasets so the numbers on
* the dashboard are ones this pipeline has fitted, not ones it has copied.
* ==============================================================================
di as txt _n "=================================================================="
di as txt "PART B: independent reproduction of the v34 reconciliation models"
di as txt "=================================================================="

local RD "TEAS EA Verification/v34_reconciliation/data"

foreach spec in ///
    "v34_intraop_remifentanil_TEAS_Sham MD Mean_difference_ug" ///
    "v34_intraop_sufentanil_TEAS_Sham MD Mean_difference_ug" ///
    "v34_qor40_24h_TEAS_Sham MD Mean_difference_points" ///
    "v34_gi_first_defecation_TEAS_Sham MD Mean_difference_hours" ///
    "v34_gi_first_defecation_EA_Usual_care MD Mean_difference_hours" ///
    "v34_primary_24h_mme_TEAS_Sham MD Mean_difference_mgMME" ///
    "v34_primary_24h_mme_EA_Usual_care MD Mean_difference_mgMME" ///
    "v34_primary_24h_mme_ALL_AUDIT MD Mean_difference_mgMME" {

    local mid    : word 1 of `spec'
    local meas   : word 2 of `spec'
    local lab    : word 3 of `spec'
    fitmodel "`RD'/`mid'.csv" "`mid'" "`meas'" "`lab'"
    post `R' ("`mid'") ("`meas'") ($M_k) ($M_est) ($M_lo) ($M_hi) ($M_p) ///
             ($M_tau2) ($M_i2) ("$M_model") ("REPRODUCED")
}

* ==============================================================================
* EXPORT
* ==============================================================================
postclose `R'
use "09_V34_ANALYSIS/03_RESULTS/v34_models.dta", clear
gen master = "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
order model_id phase measure k estimate ci_low ci_high p_value tau2 i2 estimator
export delimited "09_V34_ANALYSIS/03_RESULTS/v34_models.csv", replace
save "09_V34_ANALYSIS/03_RESULTS/v34_models.dta", replace
list model_id k estimate ci_low ci_high p_value, clean noobs

di as txt _n "SUCCESS: v34 analysis set complete."
log close
