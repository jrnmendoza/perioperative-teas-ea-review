* ==============================================================================
* 14_tiered_tierE_smd_v33.do
*   Tier E scale-free SMD secondary/exploratory analysis: cumulative 0-24 h
*   postoperative opioid consumption, standardized mean difference (Hedges' g)
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 (authoritative inferential engine)
*   Input:  07_TIERED_V33/01_DATA/tiered_tierE_smd_v33.csv
* ==============================================================================
*
* WHY THIS EXISTS
*   Tier E of the derivability audit (PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv)
*   holds results that report the exact 0-24 h cumulative opioid estimand as a
*   mean/SD, but in a unit with no sourced absolute-IV-MME conversion (a
*   weight-normalized dose, or a volume proxy with unreported concentration).
*   That blocks the ABSOLUTE-MME primary (S0-S3 in 13_tiered_primary_v33.do),
*   not a WITHIN-STUDY standardized effect: Hedges' g divides the between-arm
*   difference by the pooled SD, so the unit cancels. This file computes that
*   secondary, scale-free synthesis. It is EXPLORATORY and is never pooled
*   with, added to, or averaged against the absolute-MME S0 estimates: they
*   answer different questions on different scales.
*
* THIS IS NOT A NEW ESTIMAND
*   A Hedges' g pooled across studies with different comparators/drugs answers
*   "how large is the relative between-arm difference on a common standardized
*   scale", not "how many mg of opioid are spared". It cannot substitute for
*   the absolute-MME primary and is labelled EXPLORATORY everywhere it appears.
*
* PRE-SPECIFIED PROHIBITIONS ENFORCED HERE (same as 13_tiered_primary_v33.do)
*   - TEAS and EA are NOT combined merely to increase power.
*   - Sham/placebo and usual-care comparators are NOT combined without
*     stratification.
*   - Multi-arm trials contribute ONE contrast to any single model (Sim 2002's
*     two EA-timing arms and Jin 2023's two frequency arms were already
*     combined into one contrast each in build_tier_e_smd_dataset.py, per
*     Cochrane Handbook 6.5.2.10 -- verify that gate below).
*   - The one median/IQR row (Chen 2015, Hyperalgesia) is approximated to
*     mean/SD (Cochrane Handbook 6.5.2.5) and is SENSITIVITY ONLY: it is
*     reported as an addition to, never a silent replacement of, the
*     native-mean/SD main estimate.
* ==============================================================================

clear all
set more off
capture log close
log using "07_TIERED_V33/02_STATA/logs/14_tiered_tierE_smd_v33.log", replace

di as txt "=================================================================="
di as txt "14: TIER E SCALE-FREE SMD -- 0-24 h CUMULATIVE OPIOID (Hedges' g)"
di as txt "Model: Random-effects REML + Hartung-Knapp (se(kh)) where k>=2"
di as txt "Status: SECONDARY / EXPLORATORY -- not pooled with the absolute-MME primary"
di as txt "=================================================================="

di as txt _n "Stata version / flavor used for these results:"
di as txt "  c(stata_version) = " c(stata_version)
di as txt "  c(version)       = " c(version)
di as txt "  c(edition)       = " c(edition)
di as txt "  c(flavor)        = " c(flavor)

import delimited "07_TIERED_V33/01_DATA/tiered_tierE_smd_v33.csv", clear varnames(1) case(preserve)
describe
list study stratum n_i n_c hedges_g hedges_se sensitivity_only, clean noobs

* ------------------------------------------------------------------------------
* 0. INTEGRITY GATES
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "0. INTEGRITY GATES"
di as txt "------------------------------------------------------------------"

* (a) No row may be a raw, uncombined half of a correlated multi-arm pair.
*     (build_tier_e_smd_dataset.py already combined Sim 2002 and Jin 2023;
*     this gate fails if a future edit ever feeds this file a raw arm.)
count if strpos(study, "SIM02_PREOP") > 0 | strpos(study, "SIM02_POSTOP") > 0 ///
      | strpos(study, "2HZ") > 0 | strpos(study, "20100") > 0
if r(N) > 0 {
    di as error "GATE FAIL: an uncombined multi-arm half-contrast is present."
    exit 459
}

* (b) Every row must carry a complete Hedges' g and SE.
count if missing(hedges_g, hedges_se)
if r(N) > 0 {
    di as error "GATE FAIL: a row has a missing Hedges' g or SE."
    exit 459
}

* (c) Reproduce each Hedges' g and SE from the arm-level means/SDs/n's, so
*     nothing pooled below depends on a value this log cannot itself verify.
gen double s_pooled = sqrt(((n_i-1)*sd_i_src^2 + (n_c-1)*sd_c_src^2) / (n_i+n_c-2))
gen double d_check  = (mean_i_src - mean_c_src) / s_pooled
gen double j_check  = 1 - (3 / (4*(n_i+n_c) - 9))
gen double g_check  = d_check * j_check
gen double se_check = sqrt((n_i+n_c)/(n_i*n_c) + g_check^2/(2*(n_i+n_c)))
count if abs(g_check - hedges_g) > 1e-4 | abs(se_check - hedges_se) > 1e-4
if r(N) > 0 {
    di as error "GATE FAIL: Hedges' g/SE do not reproduce from arm-level means, SDs and n."
    list study hedges_g g_check hedges_se se_check, clean noobs
    exit 459
}
di as txt "All integrity gates passed."

* ==============================================================================
* EA vs SHAM/PLACEBO -- poolable (k=2): Coura 2011 + Sim 2002 (combined)
* ==============================================================================
di as txt _n "=================================================================="
di as txt "EA vs sham/placebo, scale-free SMD (Hedges' g)"
di as txt "  Studies  : Coura 2011; Sim 2002 (preop+postop EA combined)"
di as txt "  Estimator: random-effects REML; CI: Hartung-Knapp"
di as txt "=================================================================="
count if stratum == "ea_sham" & sensitivity_only == 0
local k_easham = r(N)
list study n_i n_c hedges_g hedges_se if stratum == "ea_sham" & sensitivity_only == 0, clean noobs

meta set hedges_g hedges_se if stratum == "ea_sham" & sensitivity_only == 0, ///
    studylabel(study) eslabel("Hedges' g (SMD)")
meta summarize, random(reml) se(kh) predinterval
matrix EA_SHAM_SMD = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
local pi_lb_easham = r(pi_lb)
local pi_ub_easham = r(pi_ub)

meta forestplot, ///
    title("Tier E exploratory: EA vs sham/placebo, scale-free SMD", size(medium)) ///
    subtitle("Hedges' g; random-effects REML + Hartung-Knapp (k=`k_easham')", size(vsmall)) ///
    nullrefline nonotes
graph export "07_TIERED_V33/04_FIGURES/forestE_ea_sham_smd.png", width(1800) replace

di as txt _n "EA vs sham/placebo SMD leave-one-out:"
meta summarize, random(reml) se(kh) leaveoneout

di as txt _n "NOTE: this is the first sham/placebo-controlled EA estimate this review"
di as txt "reports for the 24-h opioid outcome on ANY metric -- 13_tiered_primary_v33.do's"
di as txt "S0 has k=0 sham-controlled EA trials for the absolute-MME estimand. This does"
di as txt "NOT fill that empty cell: it is a different, weaker, scale-free claim (relative"
di as txt "standardized effect, not mg spared), built from weight/volume-normalized doses"
di as txt "that cannot be read as absolute opioid-sparing. It answers 'is there a relative"
di as txt "signal', not 'how many mg', and must not be substituted for the missing"
di as txt "absolute-dose sham-controlled EA estimate anywhere this is presented."

* ==============================================================================
* TEAS vs SHAM -- Jin 2023 (combined) alone, k=1, cannot be pooled
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "TEAS/EA vs sham, scale-free SMD -- Jin 2023 (2Hz+20/100Hz combined)"
di as txt "  k=1: a single study cannot be meta-analysed. Reported standalone with a"
di as txt "  normal-approximation 95% CI (g +/- 1.96 x SE), not a Hartung-Knapp interval,"
di as txt "  which requires k>=2 degrees of freedom."
di as txt "------------------------------------------------------------------"
summarize hedges_g if comparison_id == "JIN23_COMBINED_EA_vs_SHAM_SMD", meanonly
local jin_g = r(mean)
summarize hedges_se if comparison_id == "JIN23_COMBINED_EA_vs_SHAM_SMD", meanonly
local jin_se = r(mean)
local jin_lo = `jin_g' - 1.95996398454005*`jin_se'
local jin_hi = `jin_g' + 1.95996398454005*`jin_se'
di as txt "Jin 2023 (combined): g = " %6.3f `jin_g' ", 95% CI [" %6.3f `jin_lo' ", " %6.3f `jin_hi' "]"

* ==============================================================================
* TEAS vs SHAM -- SENSITIVITY: add Chen 2015 (Hyperalgesia), median/IQR-approx
* ==============================================================================
di as txt _n "=================================================================="
di as txt "SENSITIVITY: TEAS/EA vs sham SMD, Jin 2023 (combined) + Chen 2015 (Hyperalgesia)"
di as txt "  Chen 2015 (Hyperalgesia) is median/IQR, approximated to mean/SD (Cochrane"
di as txt "  Handbook 6.5.2.5: mean~=median, SD~=IQR/1.35). Shown ONLY as a named"
di as txt "  sensitivity addition, never merged silently into the k=1 main estimate above."
di as txt "=================================================================="
count if stratum == "teas_sham"
local k_teassham_sens = r(N)
list study n_i n_c hedges_g hedges_se sensitivity_only if stratum == "teas_sham", clean noobs

meta set hedges_g hedges_se if stratum == "teas_sham", studylabel(study) ///
    eslabel("Hedges' g (SMD)")
meta summarize, random(reml) se(kh) predinterval
matrix TEAS_SHAM_SMD_SENS = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q), r(p_Q))
local pi_lb_ts = r(pi_lb)
local pi_ub_ts = r(pi_ub)

meta forestplot, ///
    title("Tier E exploratory SENSITIVITY: EA/TEAS vs sham SMD (+ median/IQR approx.)", size(medium)) ///
    subtitle("Hedges' g; random-effects REML + Hartung-Knapp (k=`k_teassham_sens')", size(vsmall)) ///
    nullrefline nonotes
graph export "07_TIERED_V33/04_FIGURES/forestF_teas_sham_smd_sensitivity.png", width(1800) replace

* ==============================================================================
* TEAS vs USUAL CARE -- Oztas 2019 alone, k=1, cannot be pooled
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "TEAS vs usual care, scale-free SMD -- Oztas 2019"
di as txt "  k=1: a single study cannot be meta-analysed. Reported standalone with a"
di as txt "  normal-approximation 95% CI. Overall RoB 2 for this study is High."
di as txt "------------------------------------------------------------------"
summarize hedges_g if comparison_id == "OZT19_TEAS_vs_UC_SMD", meanonly
local ozt_g = r(mean)
summarize hedges_se if comparison_id == "OZT19_TEAS_vs_UC_SMD", meanonly
local ozt_se = r(mean)
local ozt_lo = `ozt_g' - 1.95996398454005*`ozt_se'
local ozt_hi = `ozt_g' + 1.95996398454005*`ozt_se'
di as txt "Oztas 2019: g = " %6.3f `ozt_g' ", 95% CI [" %6.3f `ozt_lo' ", " %6.3f `ozt_hi' "]"

* ==============================================================================
* EXCLUDED FROM EVERY MODEL ABOVE (listed, not silently dropped)
* ==============================================================================
di as txt _n "------------------------------------------------------------------"
di as txt "EXCLUDED from every Tier E SMD model above (a problem the SMD metric does"
di as txt "not fix -- not a reporting-format issue):"
di as txt "  Zhang 2025      window mismatch (POD1, not an explicit 0-24 h clock window)"
di as txt "  Ntritsou 2014   wrong estimand (protocol-mandated background dosing included)"
di as txt "  Oztas 2019 combined-opioid row   unrecoverable combined-total variance"
di as txt "  Oztas 2019 TEAS-vs-TENS arm      comparator eligibility unresolved (audit: Check)"
di as txt "  Song 2020       assumption-dependent derivation (PCA presses != deliveries)"
di as txt "------------------------------------------------------------------"

* ==============================================================================
* EXPORT
* ==============================================================================
clear
set obs 4
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

replace analysis_id    = "V33_TIERE_EA_SHAM_SMD" in 1
replace analysis_set   = "Tier E exploratory SMD" in 1
replace modality       = "EA" in 1
replace comparator     = "Sham/placebo" in 1
replace outcome        = "Cumulative postoperative opioid consumption (standardized, Hedges' g)" in 1
replace window         = "0-24 h" in 1
replace unit           = "Hedges' g (SMD, dimensionless)" in 1
replace k              = EA_SHAM_SMD[1,5] in 1
replace effect_measure = "Standardized mean difference (Hedges' g)" in 1
replace estimate       = EA_SHAM_SMD[1,1] in 1
replace ci_low         = EA_SHAM_SMD[1,2] in 1
replace ci_high        = EA_SHAM_SMD[1,3] in 1
replace p_value        = EA_SHAM_SMD[1,4] in 1
replace tau2           = EA_SHAM_SMD[1,6] in 1
replace i2             = EA_SHAM_SMD[1,7] in 1
replace q_stat         = EA_SHAM_SMD[1,8] in 1
replace p_q            = EA_SHAM_SMD[1,9] in 1
replace pi_low         = `pi_lb_easham' in 1
replace pi_high        = `pi_ub_easham' in 1
replace estimator      = "REML" in 1
replace ci_method      = "Hartung-Knapp" in 1
replace notes          = "EXPLORATORY. Coura 2011 + Sim 2002 (two correlated EA-timing arms combined per Cochrane Handbook 6.5.2.10). Weight-normalized native units (ug/kg, mg/kg); not convertible to absolute IV MME. Not a substitute for the missing sham-controlled EA absolute-MME estimate (k=0 in the S0 primary)." in 1

replace analysis_id    = "V33_TIERE_TEAS_SHAM_SMD_MAIN" in 2
replace analysis_set   = "Tier E exploratory SMD" in 2
replace modality       = "EA" in 2
replace comparator     = "Sham nonpenetrating EA/no current" in 2
replace outcome        = "Cumulative postoperative opioid consumption (standardized, Hedges' g)" in 2
replace window         = "0-24 h" in 2
replace unit           = "Hedges' g (SMD, dimensionless)" in 2
replace k              = 1 in 2
replace effect_measure = "Standardized mean difference (Hedges' g)" in 2
replace estimate       = `jin_g' in 2
replace ci_low         = `jin_lo' in 2
replace ci_high        = `jin_hi' in 2
replace estimator      = "Single study (no pooling)" in 2
replace ci_method      = "Normal approximation (g +/- 1.96 x SE)" in 2
replace notes          = "EXPLORATORY, k=1 (Jin 2023, two correlated frequency arms combined per Cochrane Handbook 6.5.2.10). Volume (mL PCIA solution) proxy for fentanyl mass; concentration unreported, so the unit cancels in SMD but is not convertible to absolute dose. Cannot be meta-analysed with k=1; CI is a normal approximation, not Hartung-Knapp." in 2

replace analysis_id    = "V33_TIERE_TEAS_SHAM_SMD_SENS" in 3
replace analysis_set   = "Tier E exploratory SMD sensitivity" in 3
replace modality       = "EA/TEAS" in 3
replace comparator     = "Sham" in 3
replace outcome        = "Cumulative postoperative opioid consumption (standardized, Hedges' g)" in 3
replace window         = "0-24 h" in 3
replace unit           = "Hedges' g (SMD, dimensionless)" in 3
replace k              = TEAS_SHAM_SMD_SENS[1,5] in 3
replace effect_measure = "Standardized mean difference (Hedges' g)" in 3
replace estimate       = TEAS_SHAM_SMD_SENS[1,1] in 3
replace ci_low         = TEAS_SHAM_SMD_SENS[1,2] in 3
replace ci_high        = TEAS_SHAM_SMD_SENS[1,3] in 3
replace p_value        = TEAS_SHAM_SMD_SENS[1,4] in 3
replace tau2           = TEAS_SHAM_SMD_SENS[1,6] in 3
replace i2             = TEAS_SHAM_SMD_SENS[1,7] in 3
replace q_stat         = TEAS_SHAM_SMD_SENS[1,8] in 3
replace p_q            = TEAS_SHAM_SMD_SENS[1,9] in 3
replace pi_low         = `pi_lb_ts' in 3
replace pi_high        = `pi_ub_ts' in 3
replace estimator      = "REML" in 3
replace ci_method      = "Hartung-Knapp" in 3
replace notes          = "SENSITIVITY, not the main Tier E estimate. Adds Chen 2015 (Hyperalgesia) to Jin 2023 (combined). Chen 2015 (Hyperalgesia) is median/IQR approximated to mean/SD (Cochrane Handbook 6.5.2.5); this is a materially weaker evidentiary basis than every other row in this file, which are all native mean/SD. Reported as a named addition, never merged silently into V33_TIERE_TEAS_SHAM_SMD_MAIN." in 3

replace analysis_id    = "V33_TIERE_TEAS_USUAL_SMD" in 4
replace analysis_set   = "Tier E exploratory SMD" in 4
replace modality       = "TEAS" in 4
replace comparator     = "Usual care" in 4
replace outcome        = "Cumulative postoperative opioid consumption (standardized, Hedges' g)" in 4
replace window         = "0-24 h" in 4
replace unit           = "Hedges' g (SMD, dimensionless)" in 4
replace k              = 1 in 4
replace effect_measure = "Standardized mean difference (Hedges' g)" in 4
replace estimate       = `ozt_g' in 4
replace ci_low         = `ozt_lo' in 4
replace ci_high        = `ozt_hi' in 4
replace estimator      = "Single study (no pooling)" in 4
replace ci_method      = "Normal approximation (g +/- 1.96 x SE)" in 4
replace notes          = "EXPLORATORY, k=1 (Oztas 2019). Native mg tramadol; no sourced tramadol:morphine IV MME factor, and tramadol alone is not complete opioid exposure (rescue pethidine reported separately). Overall RoB 2 High. Cannot be meta-analysed with k=1; CI is a normal approximation, not Hartung-Knapp." in 4

save "07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33_tierE.dta", replace
export delimited "07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33_tierE.csv", replace
list analysis_id k estimate ci_low ci_high p_value i2, clean noobs

di as txt _n "SUCCESS: Tier E scale-free SMD exploratory analysis complete."
log close
