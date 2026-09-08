* ==============================================================================
* 13_tiered_primary_v33.do
*   Tiered primary-outcome analysis: cumulative 0-24 h postoperative opioid
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 (authoritative inferential engine)
*   Input:  07_TIERED_V33/01_DATA/tiered_primary_v33.csv
*           07_TIERED_V33/01_DATA/tiered_tierC_parallel_v33.csv
* ==============================================================================
*
* TIER DEFINITIONS (see PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.xlsx)
*   Tier A  Directly compatible: exact 0-24 h cumulative opioid, mean/SD,
*           absolute dose, sourced MME conversion factor.
*   Tier B  Deterministically derived: an exact arithmetic identity from
*           reported quantities (no distributional assumption).
*   Tier C  Exact estimand but an alternative distributional form
*           (median/IQR). Reported as a PARALLEL synthesis, never converted.
*   Tier D  Recoverable only by graph digitization.
*   Tier E  Requires an assumption the protocol prohibits (body weight, PCA
*           presses as deliveries, POD1 = 0-24 h, invented covariance).
*
* ANALYSIS SETS
*   S0  Tier A only, stratified by modality AND comparator (no cross-stratum pool)
*   S1  S0 + Tier B                      -> empty increment (no pure Tier B case)
*   S2  Tier C parallel synthesis        -> reported as medians, NOT pooled with S0
*   S3  S0 + Tier D                      -> empty (Gu 2019 digitization failed
*                                            its validation-against-text check)
*
* PRE-SPECIFIED PROHIBITIONS ENFORCED HERE
*   - TEAS and EA are NOT combined merely to increase power.
*   - Sham and usual-care comparators are NOT combined without stratification.
*   - Multi-arm trials contribute ONE contrast to any single model
*     (Szmit 2021's sham and PCA-only contrasts are never pooled together).
*   - No median/IQR study is converted to mean/SD for pooling.
* ==============================================================================

clear all
set more off
capture log close
log using "07_TIERED_V33/02_STATA/logs/13_tiered_primary_v33.log", replace

di as txt "=================================================================="
di as txt "13: TIERED PRIMARY OUTCOME -- 0-24 h CUMULATIVE OPIOID (mg IV MME)"
di as txt "Model: Random-effects REML + Hartung-Knapp (se(kh)), predinterval"
di as txt "=================================================================="

di as txt _n "Stata version / flavor used for these results:"
di as txt "  c(stata_version) = " c(stata_version)
di as txt "  c(version)       = " c(version)
di as txt "  c(edition)       = " c(edition)
di as txt "  c(flavor)        = " c(flavor)

import delimited "07_TIERED_V33/01_DATA/tiered_primary_v33.csv", clear varnames(1) case(preserve)
describe
list study modality comparator n_i n_c mean_i_mme sd_i_mme mean_c_mme sd_c_mme ///
     md_mme se_mme in_S0 multiarm_alt, clean noobs

* ------------------------------------------------------------------------------
* 0. INTEGRITY GATES -- fail loudly rather than pooling something prohibited
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "0. INTEGRITY GATES"
di as txt "------------------------------------------------------------------"

* (a) No multi-arm alternative contrast may enter S0.
count if in_S0 == 1 & multiarm_alt == 1
if r(N) > 0 {
    di as error "GATE FAIL: a correlated multi-arm alternative contrast is flagged in_S0."
    exit 459
}

* (b) Every S0 row must carry a complete MD and SE.
count if in_S0 == 1 & missing(md_mme, se_mme)
if r(N) > 0 {
    di as error "GATE FAIL: an S0 row has a missing MD or SE."
    exit 459
}

* (c) S0 strata must be mutually exclusive and exhaustive.
count if in_S0 == 1 & (in_S0_teas_sham + in_S0_ea_usual) != 1
if r(N) > 0 {
    di as error "GATE FAIL: an S0 row is in zero or both strata."
    exit 459
}

* (d) Reproduce each MD and SE from the arm-level MME values.
gen double md_check = mean_i_mme - mean_c_mme
gen double se_check = sqrt(sd_i_mme^2/n_i + sd_c_mme^2/n_c)
count if abs(md_check - md_mme) > 1e-4 | abs(se_check - se_mme) > 1e-4
if r(N) > 0 {
    di as error "GATE FAIL: MD/SE do not reproduce from arm-level means and SDs."
    list study md_mme md_check se_mme se_check, clean noobs
    exit 459
}
di as txt "All integrity gates passed."

* ==============================================================================
* S0 -- PRIMARY: TEAS vs INERT SHAM
* ==============================================================================
di as txt _n "=================================================================="
di as txt "S0 PRIMARY: TEAS vs inert sham"
di as txt "  Outcome  : cumulative 0-24 h postoperative opioid consumption"
di as txt "  Window   : 0-24 h post-operation"
di as txt "  Unit     : mg intravenous morphine milligram equivalents (IV MME)"
di as txt "  Estimator: random-effects REML"
di as txt "  CI method: Hartung-Knapp (Knapp-Hartung), t reference distribution"
di as txt "=================================================================="
count if in_S0_teas_sham == 1
local k_teas = r(N)
list study n_i n_c md_mme se_mme if in_S0_teas_sham == 1, clean noobs

meta set md_mme se_mme if in_S0_teas_sham == 1, studylabel(study) ///
    eslabel("Mean difference (mg IV MME)")
meta summarize, random(reml) se(kh) predinterval
matrix S0_teas = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
local pi_lb_teas = r(pi_lb)
local pi_ub_teas = r(pi_ub)

di as txt _n "Study weights (REML, random-effects):"
meta summarize, random(reml) se(kh)

meta forestplot, ///
    title("A. Primary: TEAS vs inert sham, 0-24 h opioid", size(medium)) ///
    subtitle("Mean difference in mg IV MME; random-effects REML + Hartung-Knapp (k=`k_teas')", size(vsmall)) ///
    nullrefline nonotes
graph export "07_TIERED_V33/04_FIGURES/forestA_S0_teas_sham_24h_mme.png", width(1800) replace

* Leave-one-out for the primary model
di as txt _n "S0 PRIMARY leave-one-out (REML + Hartung-Knapp):"
meta summarize, random(reml) se(kh) leaveoneout

* ==============================================================================
* S0 -- SUPPORTIVE: EA vs USUAL CARE
* ==============================================================================
di as txt _n "=================================================================="
di as txt "S0 SUPPORTIVE: EA vs usual care / no-stimulation control"
di as txt "  Same outcome, window, unit, estimator and CI method as above."
di as txt "  Reported SEPARATELY: a different comparator answers a different question."
di as txt "=================================================================="
count if in_S0_ea_usual == 1
local k_ea = r(N)
list study n_i n_c md_mme se_mme if in_S0_ea_usual == 1, clean noobs

meta set md_mme se_mme if in_S0_ea_usual == 1, studylabel(study) ///
    eslabel("Mean difference (mg IV MME)")
meta summarize, random(reml) se(kh) predinterval
matrix S0_ea = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
local pi_lb_ea = r(pi_lb)
local pi_ub_ea = r(pi_ub)

meta forestplot, ///
    title("B. Supportive: EA vs usual care, 0-24 h opioid", size(medium)) ///
    subtitle("Mean difference in mg IV MME; random-effects REML + Hartung-Knapp (k=`k_ea')", size(vsmall)) ///
    nullrefline nonotes
graph export "07_TIERED_V33/04_FIGURES/forestB_S0_ea_usualcare_24h_mme.png", width(1800) replace

di as txt _n "S0 SUPPORTIVE leave-one-out (REML + Hartung-Knapp):"
meta summarize, random(reml) se(kh) leaveoneout

* ==============================================================================
* EMPTY CELL: sham-controlled EA
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "EMPTY CELL: EA vs inert sham"
di as txt "------------------------------------------------------------------"
count if modality == "EA" & comparator == "Sham" & !missing(md_mme)
di as txt "Sham-controlled EA trials reporting an analysable 0-24 h cumulative"
di as txt "opioid mean/SD in absolute dose units: k = " r(N)
di as txt "No sham-controlled EA estimate is available for this outcome."
di as txt "The EA result above is therefore NOT sham-controlled and cannot be"
di as txt "read as a specific-acupoint effect."

* ==============================================================================
* S1 -- Tier A + Tier B
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "S1: Tier A + Tier B (deterministically derived mean/SD)"
di as txt "------------------------------------------------------------------"
di as txt "No trial supplies a deterministic mean/SD derivation that is not"
di as txt "already Tier A. Chen 2015's rescue-bolus derivation is exact, but the"
di as txt "reported quantities are medians and IQRs, so it lands in Tier C, not"
di as txt "Tier B. S1 is therefore identical to S0 -- no separate model is fitted."

* ==============================================================================
* S2 -- Tier C PARALLEL SYNTHESIS (medians; NOT pooled with S0)
* ==============================================================================
di as txt _n "=================================================================="
di as txt "S2: Tier C parallel synthesis -- median/IQR evidence"
di as txt "=================================================================="
preserve
import delimited "07_TIERED_V33/01_DATA/tiered_tierC_parallel_v33.csv", clear varnames(1) case(preserve)
list study modality comparator n_i n_c median_i_mme q1_i_mme q3_i_mme ///
     median_c_mme q1_c_mme q3_c_mme median_difference_mme reported_p, clean noobs
di as txt _n "These are NOT pooled and NOT converted to mean/SD:"
list study not_pooled_reason, clean noobs
restore

* ==============================================================================
* S3 -- Tier D (digitized)
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "S3: Tier A + Tier D (graph-digitized)"
di as txt "------------------------------------------------------------------"
di as txt "One candidate (Gu 2019, Figure 4) was digitized under a pre-specified"
di as txt "validation protocol. Axis calibration was exact (max residual 0.0000)"
di as txt "and the low-frequency TEAS arm reproduced the in-text values to within"
di as txt "4.2%, but the control arm was systematically overestimated by up to"
di as txt "16.0%, indicating a figure-versus-text inconsistency in the source."
di as txt "The digitization therefore FAILED its validation check and Gu 2019 is"
di as txt "not admissible. S3 is empty and identical to S0; no model is fitted."
di as txt "See 07_TIERED_V33/03_DIGITIZATION/gu2019_digitization_QC.md."

* ==============================================================================
* COMPARATOR SENSITIVITY -- Szmit 2021 alternative arm
* ==============================================================================
di as txt _n "=================================================================="
di as txt "SENSITIVITY C1: TEAS primary using Szmit 2021's PCA-only (usual-care)"
di as txt "arm in place of its sham arm. The two contrasts are correlated and are"
di as txt "NEVER pooled together; this swaps one for the other."
di as txt "=================================================================="
preserve
drop if study == "Szmit 2021"
replace in_S0_teas_sham = 1 if study == "Szmit 2021 (PCA-only arm)"
count if in_S0_teas_sham == 1
local k_c1 = r(N)
list study comparator md_mme se_mme if in_S0_teas_sham == 1, clean noobs
meta set md_mme se_mme if in_S0_teas_sham == 1, studylabel(study) ///
    eslabel("Mean difference (mg IV MME)")
meta summarize, random(reml) se(kh) predinterval
matrix SENS_C1 = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
restore

* ------------------------------------------------------------------------------
* SENSITIVITY C2: estimator / CI-method grid on the primary model
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "SENSITIVITY C2: estimator and CI-method grid, S0 primary (TEAS vs sham)"
di as txt "=================================================================="
meta set md_mme se_mme if in_S0_teas_sham == 1, studylabel(study) ///
    eslabel("Mean difference (mg IV MME)")

di as txt _n "REML + Hartung-Knapp (pre-specified primary):"
meta summarize, random(reml) se(kh)
matrix G_reml_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

di as txt _n "REML + Wald:"
meta summarize, random(reml)
matrix G_reml_wald = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

di as txt _n "DerSimonian-Laird + Hartung-Knapp:"
meta summarize, random(dlaird) se(kh)
matrix G_dl_kh = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

di as txt _n "DerSimonian-Laird + Wald:"
meta summarize, random(dlaird)
matrix G_dl_wald = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))

* ==============================================================================
* EXPORT
* ==============================================================================
clear
set obs 8
gen analysis_id    = ""
gen analysis_set   = ""
gen modality       = ""
gen comparator     = ""
gen outcome        = ""
gen window         = ""
gen unit           = ""
gen k              = .
gen effect_measure = ""
gen estimate       = .
gen ci_low         = .
gen ci_high        = .
gen p_value        = .
gen tau2           = .
gen i2             = .
gen q_stat         = .
gen p_q            = .
gen pi_low         = .
gen pi_high        = .
gen estimator      = ""
gen ci_method      = ""
gen notes          = ""

replace analysis_id    = "V33_S0_TEAS_SHAM" in 1
replace analysis_set   = "S0 (Tier A only)" in 1
replace modality       = "TEAS" in 1
replace comparator     = "Inert sham" in 1
replace outcome        = "Cumulative postoperative opioid consumption" in 1
replace window         = "0-24 h" in 1
replace unit           = "mg IV MME" in 1
replace k              = S0_teas[1,5] in 1
replace effect_measure = "Mean difference" in 1
replace estimate       = S0_teas[1,1] in 1
replace ci_low         = S0_teas[1,2] in 1
replace ci_high        = S0_teas[1,3] in 1
replace p_value        = S0_teas[1,4] in 1
replace tau2           = S0_teas[1,6] in 1
replace i2             = S0_teas[1,7] in 1
replace q_stat         = S0_teas[1,8] in 1
replace p_q            = S0_teas[1,9] in 1
replace pi_low         = `pi_lb_teas' in 1
replace pi_high        = `pi_ub_teas' in 1
replace estimator      = "REML" in 1
replace ci_method      = "Hartung-Knapp" in 1
replace notes          = "PRIMARY analysis. Tier A only; single comparator stratum." in 1

replace analysis_id    = "V33_S0_EA_USUAL" in 2
replace analysis_set   = "S0 (Tier A only)" in 2
replace modality       = "EA" in 2
replace comparator     = "Usual care / no stimulation" in 2
replace outcome        = "Cumulative postoperative opioid consumption" in 2
replace window         = "0-24 h" in 2
replace unit           = "mg IV MME" in 2
replace k              = S0_ea[1,5] in 2
replace effect_measure = "Mean difference" in 2
replace estimate       = S0_ea[1,1] in 2
replace ci_low         = S0_ea[1,2] in 2
replace ci_high        = S0_ea[1,3] in 2
replace p_value        = S0_ea[1,4] in 2
replace tau2           = S0_ea[1,6] in 2
replace i2             = S0_ea[1,7] in 2
replace q_stat         = S0_ea[1,8] in 2
replace p_q            = S0_ea[1,9] in 2
replace pi_low         = `pi_lb_ea' in 2
replace pi_high        = `pi_ub_ea' in 2
replace estimator      = "REML" in 2
replace ci_method      = "Hartung-Knapp" in 2
replace notes          = "SUPPORTIVE. Not sham-controlled; no sham-controlled EA trial reports this outcome." in 2

replace analysis_id    = "V33_S1_TEAS_SHAM" in 3
replace analysis_set   = "S1 (Tier A + Tier B)" in 3
replace modality       = "TEAS" in 3
replace comparator     = "Inert sham" in 3
replace outcome        = "Cumulative postoperative opioid consumption" in 3
replace window         = "0-24 h" in 3
replace unit           = "mg IV MME" in 3
replace k              = S0_teas[1,5] in 3
replace effect_measure = "Mean difference" in 3
replace estimate       = S0_teas[1,1] in 3
replace ci_low         = S0_teas[1,2] in 3
replace ci_high        = S0_teas[1,3] in 3
replace p_value        = S0_teas[1,4] in 3
replace tau2           = S0_teas[1,6] in 3
replace i2             = S0_teas[1,7] in 3
replace estimator      = "REML" in 3
replace ci_method      = "Hartung-Knapp" in 3
replace notes          = "Identical to S0: no pure Tier B case exists. Chen 2015's exact derivation yields medians, so it is Tier C." in 3

replace analysis_id    = "V33_S2_PARALLEL" in 4
replace analysis_set   = "S2 (Tier C parallel synthesis)" in 4
replace modality       = "TEAS" in 4
replace comparator     = "Sham / usual care" in 4
replace outcome        = "Cumulative postoperative opioid consumption" in 4
replace window         = "0-24 h" in 4
replace unit           = "mg IV MME (medians)" in 4
replace k              = 2 in 4
replace effect_measure = "Median difference (not pooled)" in 4
replace estimator      = "None (narrative parallel synthesis)" in 4
replace ci_method      = "None" in 4
replace notes          = "Gao 2022 and Chen 2015 report medians/IQRs. Gao 2022 is zero-inflated (Q1=0 in both arms), so Wan/Luo recovery is indefensible. Presented as medians alongside S0, never pooled with it." in 4

replace analysis_id    = "V33_S3_TEAS_SHAM" in 5
replace analysis_set   = "S3 (Tier A + Tier D)" in 5
replace modality       = "TEAS" in 5
replace comparator     = "Inert sham" in 5
replace outcome        = "Cumulative postoperative opioid consumption" in 5
replace window         = "0-24 h" in 5
replace unit           = "mg IV MME" in 5
replace k              = S0_teas[1,5] in 5
replace effect_measure = "Mean difference" in 5
replace estimate       = S0_teas[1,1] in 5
replace ci_low         = S0_teas[1,2] in 5
replace ci_high        = S0_teas[1,3] in 5
replace p_value        = S0_teas[1,4] in 5
replace tau2           = S0_teas[1,6] in 5
replace i2             = S0_teas[1,7] in 5
replace estimator      = "REML" in 5
replace ci_method      = "Hartung-Knapp" in 5
replace notes          = "Identical to S0: the sole digitization candidate (Gu 2019) failed its pre-specified validation-against-text check (control arm error up to 16.0%)." in 5

replace analysis_id    = "V33_SENS_C1_SZMIT_ALT" in 6
replace analysis_set   = "Comparator sensitivity" in 6
replace modality       = "TEAS" in 6
replace comparator     = "Sham, with Szmit 2021 usual-care arm substituted" in 6
replace outcome        = "Cumulative postoperative opioid consumption" in 6
replace window         = "0-24 h" in 6
replace unit           = "mg IV MME" in 6
replace k              = SENS_C1[1,5] in 6
replace effect_measure = "Mean difference" in 6
replace estimate       = SENS_C1[1,1] in 6
replace ci_low         = SENS_C1[1,2] in 6
replace ci_high        = SENS_C1[1,3] in 6
replace p_value        = SENS_C1[1,4] in 6
replace tau2           = SENS_C1[1,6] in 6
replace i2             = SENS_C1[1,7] in 6
replace estimator      = "REML" in 6
replace ci_method      = "Hartung-Knapp" in 6
replace notes          = "Swap, not addition: Szmit 2021 contributes exactly one contrast." in 6

replace analysis_id    = "V33_SENS_C2_REML_WALD" in 7
replace analysis_set   = "Estimator/CI sensitivity" in 7
replace modality       = "TEAS" in 7
replace comparator     = "Inert sham" in 7
replace outcome        = "Cumulative postoperative opioid consumption" in 7
replace window         = "0-24 h" in 7
replace unit           = "mg IV MME" in 7
replace k              = G_reml_wald[1,5] in 7
replace effect_measure = "Mean difference" in 7
replace estimate       = G_reml_wald[1,1] in 7
replace ci_low         = G_reml_wald[1,2] in 7
replace ci_high        = G_reml_wald[1,3] in 7
replace p_value        = G_reml_wald[1,4] in 7
replace tau2           = G_reml_wald[1,6] in 7
replace i2             = G_reml_wald[1,7] in 7
replace estimator      = "REML" in 7
replace ci_method      = "Wald (z)" in 7
replace notes          = "Shown for comparison only. Wald intervals are anticonservative at k=4; the pre-specified primary remains Hartung-Knapp." in 7

replace analysis_id    = "V33_SENS_C2_DL_KH" in 8
replace analysis_set   = "Estimator/CI sensitivity" in 8
replace modality       = "TEAS" in 8
replace comparator     = "Inert sham" in 8
replace outcome        = "Cumulative postoperative opioid consumption" in 8
replace window         = "0-24 h" in 8
replace unit           = "mg IV MME" in 8
replace k              = G_dl_kh[1,5] in 8
replace effect_measure = "Mean difference" in 8
replace estimate       = G_dl_kh[1,1] in 8
replace ci_low         = G_dl_kh[1,2] in 8
replace ci_high        = G_dl_kh[1,3] in 8
replace p_value        = G_dl_kh[1,4] in 8
replace tau2           = G_dl_kh[1,6] in 8
replace i2             = G_dl_kh[1,7] in 8
replace estimator      = "DerSimonian-Laird" in 8
replace ci_method      = "Hartung-Knapp" in 8
replace notes          = "Shown for comparison only." in 8

save "07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33.dta", replace
export delimited "07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33.csv", replace
list analysis_id k estimate ci_low ci_high p_value i2, clean noobs

* ==============================================================================
* FIGURE C -- tier sensitivity (analysis sets S0/S1/S2/S3)
* FIGURE D -- comparator sensitivity
*
* These are summary plots over ANALYSIS MODELS, not over studies. Each row is a
* separately fitted pooled estimate with its own Hartung-Knapp t interval on
* k-1 df. `meta forestplot' cannot draw them: it treats each row as a study and
* redraws the interval as estimate +/- 1.96*SE on a z scale, which for k=4
* silently narrows a t(3) interval by roughly a factor of 1.6 -- enough to
* redraw this non-significant primary result as significant. These panels are
* therefore drawn directly from the fitted ci_low / ci_high bounds, so nothing
* is recomputed and no interval is misrepresented. No overall diamond and no
* pooled significance test is shown, because pooling separately fitted models
* of the same trials would be meaningless.
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "FIGURES C and D: summary plots over analysis models"
di as txt "------------------------------------------------------------------"

capture program drop v33summaryplot
program define v33summaryplot
    syntax , OUTfile(string) TItle(string) ///
             [NOTEA(string) NOTEB(string) NOTEC(string)]

    * Row labels, drawn top-to-bottom in the order the caller numbered them.
    quietly count
    local nrows = r(N)
    local ylabs ""
    forvalues i = 1/`nrows' {
        local r  = row[`i']
        local lb = panel[`i']
        local ylabs `"`ylabs' `r' "`lb'""'
    }

    * Annotate each row with the exact fitted estimate and interval, so the
    * numbers a reader takes away are the fitted ones, not read off the axis.
    quietly gen str48 v33lbl = string(estimate, "%6.2f") + " (" + ///
        string(ci_low, "%6.2f") + " to " + string(ci_high, "%6.2f") + ")"
    quietly replace v33lbl = subinstr(v33lbl, "  ", "", .)

    quietly summarize ci_low
    local xlo = r(min)
    quietly summarize ci_high
    local xhi = r(max)
    local span = `xhi' - `xlo'
    local xtxt = `xhi' + 0.18 * `span'
    quietly gen double v33txtx = `xtxt'

    twoway ///
        (rspike ci_low ci_high row, horizontal lcolor(navy) lwidth(medthick)) ///
        (scatter row estimate, msymbol(square) msize(medium) mcolor(navy)) ///
        (scatter row v33txtx, msymbol(none) mlabel(v33lbl) ///
             mlabposition(0) mlabsize(small) mlabcolor(black)) ///
        , ///
        xline(0, lcolor(gs8) lpattern(dash)) ///
        ylabel(`ylabs', angle(horizontal) labsize(small) noticks nogrid) ///
        yscale(reverse range(0.6 `=`nrows' + 0.4')) ///
        ytitle("") ///
        xtitle("Pooled mean difference (mg IV MME) with 95% Hartung-Knapp CI", size(small)) ///
        xlabel(, labsize(small)) ///
        xscale(range(`=`xlo' - 0.05 * `span'' `=`xhi' + 0.52 * `span'')) ///
        title("`title'", size(medsmall) justification(left) position(11)) ///
        note(`"`notea'"' `"`noteb'"' `"`notec'"', size(vsmall) span) ///
        legend(off) graphregion(color(white) margin(l+2 r+2)) ///
        plotregion(margin(l+2 r+2)) xsize(9) ysize(2.9)
    graph export "`outfile'", width(2200) replace
    quietly drop v33lbl v33txtx
end

* --- C: tier sensitivity -------------------------------------------------
preserve
keep if inlist(analysis_id, "V33_S0_TEAS_SHAM", "V33_S1_TEAS_SHAM", "V33_S3_TEAS_SHAM")
gen str64 panel = ""
gen byte row = .
replace panel = "S0  Tier A only (k=4)"          if analysis_id == "V33_S0_TEAS_SHAM"
replace row   = 1                                if analysis_id == "V33_S0_TEAS_SHAM"
replace panel = "S1  + Tier B derived (k=4)"     if analysis_id == "V33_S1_TEAS_SHAM"
replace row   = 2                                if analysis_id == "V33_S1_TEAS_SHAM"
replace panel = "S3  + Tier D digitized (k=4)"   if analysis_id == "V33_S3_TEAS_SHAM"
replace row   = 3                                if analysis_id == "V33_S3_TEAS_SHAM"
list panel k estimate ci_low ci_high p_value, clean noobs
v33summaryplot, ///
    outfile("07_TIERED_V33/04_FIGURES/forestC_tier_sensitivity.png") ///
    title("C. Tier sensitivity: TEAS vs inert sham, cumulative 0-24 h opioid") ///
    notea("Each row is a separately fitted random-effects REML model with a Hartung-Knapp t interval; rows are not pooled with one another.") ///
    noteb("S1 and S3 add no trial: no pure Tier B case exists, and the sole Tier D candidate (Gu 2019) failed its digitization validation check.") ///
    notec("Tier C evidence (Gao 2022, Chen 2015) is median/IQR and is reported as a parallel synthesis, never converted to mean/SD or pooled here.")
restore

* --- D: comparator sensitivity -------------------------------------------
preserve
keep if inlist(analysis_id, "V33_S0_TEAS_SHAM", "V33_SENS_C1_SZMIT_ALT", "V33_S0_EA_USUAL")
gen str64 panel = ""
gen byte row = .
replace panel = "TEAS vs inert sham (k=4)"                 if analysis_id == "V33_S0_TEAS_SHAM"
replace row   = 1                                          if analysis_id == "V33_S0_TEAS_SHAM"
replace panel = "TEAS vs sham, Szmit usual-care arm (k=4)" if analysis_id == "V33_SENS_C1_SZMIT_ALT"
replace row   = 2                                          if analysis_id == "V33_SENS_C1_SZMIT_ALT"
replace panel = "EA vs usual care (k=3)"                   if analysis_id == "V33_S0_EA_USUAL"
replace row   = 3                                          if analysis_id == "V33_S0_EA_USUAL"
list panel k estimate ci_low ci_high p_value, clean noobs
v33summaryplot, ///
    outfile("07_TIERED_V33/04_FIGURES/forestD_comparator_sensitivity.png") ///
    title("D. Comparator sensitivity: cumulative 0-24 h opioid") ///
    notea("Each row is a separately fitted random-effects REML model with a Hartung-Knapp t interval; rows are not pooled with one another.") ///
    noteb("Szmit 2021 contributes exactly one contrast: its usual-care arm is swapped in for its sham arm, never added alongside it.") ///
    notec("No sham-controlled EA trial reports this outcome (k=0), so the EA row is not sham-controlled and is not a specific-acupoint estimate.")
restore

di as txt _n "SUCCESS: tiered primary-outcome analysis complete."
log close
