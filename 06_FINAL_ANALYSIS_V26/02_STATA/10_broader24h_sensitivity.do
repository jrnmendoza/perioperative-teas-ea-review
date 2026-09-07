* ==============================================================================
* 10_broader24h_sensitivity.do
*   Broader 24-h opioid sensitivity analysis and estimability audit
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================
*
* PURPOSE
*   The strict primary analysis (01_opioid24_primary.do) pools k=6 trials whose
*   24-h cumulative opioid results are directly reported or defensibly
*   harmonisable to a common dose metric.
*
*   Five further trials in opioid_24h_primary.dta carry potentially relevant
*   24-h opioid information but were flagged CONDITIONAL in the v26 lock
*   (inc_sens==1 & inc_primary==0):
*
*       Chen 2015                 derived from fixed 2-mg rescue boluses; Median/IQR
*       Chen 2015 (Hyperalgesia)  derived from fixed 0.05 ug/kg boluses; Median/IQR
*       Coura 2011                weight-normalised ug/kg fentanyl
*       Sim 2002                  weight-normalised mg/kg morphine
*       Zhang 2025                POD1 rather than an explicit 0-24 h clock window
*
*   Strict + conditional = 11 study units, N = 945.
*
* WHY THERE IS NO k=11 MEAN-DIFFERENCE POOL
*   A pooled MD in mg IV MME across all 11 is NOT estimable without breaking
*   prohibitions recorded in the lock itself:
*
*     Sim 2002    "Do not convert mg/kg to absolute mg using group mean body
*                  weight; aggregate means cannot reconstruct individual
*                  absolute dose."
*     Coura 2011  "Do not convert to absolute ug/MME using group-average weight."
*     Chen 2015 x2  Median/IQR only; no mean/SD is derived in the locked data.
*
*   A pre-v26 dashboard release did exactly this, back-solving absolute doses
*   from assumed body weights (Sim 2002 implied 60 kg in one arm and 59 kg in
*   the other; Coura 2011 implied a flat 70 kg). That pooled MD is withdrawn and
*   is NOT reproduced here.
*
* WHAT IS ESTIMABLE
*   A standardized mean difference is scale-free, so weight-normalised endpoints
*   pool legitimately with absolute-dose endpoints. Hedges' g is available in the
*   locked data for the 6 strict trials plus Coura 2011, Sim 2002 and Zhang 2025,
*   giving a defensible BROADER SMD sensitivity analysis at k=9.
*
*   The two Chen 2015 reports remain outside both pooled models: they are
*   Median/IQR and the locked data derives no mean/SD or g for them. They are
*   counted in the 11-study candidate pool and reported narratively only.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/10_broader24h_sensitivity.log", replace

di as txt "=================================================================="
di as txt "10: BROADER 24-H OPIOID SENSITIVITY & ESTIMABILITY AUDIT"
di as txt "=================================================================="

use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear

* ------------------------------------------------------------------------------
* 1. CANDIDATE POOL COMPOSITION
* ------------------------------------------------------------------------------
gen byte strict      = (inc_primary == 1)
gen byte conditional = (inc_sens == 1 & inc_primary == 0)
gen byte broadpool   = (strict == 1 | conditional == 1)
gen int  n_total     = n_i + n_c

di as txt _n "------------------------------------------------------------------"
di as txt "1. CANDIDATE POOL COMPOSITION"
di as txt "------------------------------------------------------------------"
count if strict == 1
local k_strict = r(N)
summarize n_total if strict == 1, meanonly
local n_strict = r(sum)

count if conditional == 1
local k_cond = r(N)
summarize n_total if conditional == 1, meanonly
local n_cond = r(sum)

count if broadpool == 1
local k_pool = r(N)
summarize n_total if broadpool == 1, meanonly
local n_pool = r(sum)

di as txt "Strict primary contributors      : k = `k_strict', N = `n_strict'"
di as txt "Conditional (broader assumptions): k = `k_cond', N = `n_cond'"
di as txt "Combined candidate pool          : k = `k_pool', N = `n_pool'"

di as txt _n "Conditional study units:"
list study_unit unit data_type if conditional == 1, clean noobs

* ------------------------------------------------------------------------------
* 2. ESTIMABILITY AUDIT
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "2. ESTIMABILITY AUDIT ACROSS THE CANDIDATE POOL"
di as txt "------------------------------------------------------------------"

count if broadpool == 1 & !missing(md_mme, se_mme)
local k_md = r(N)
count if broadpool == 1 & !missing(hedges_g, hedges_se)
local k_smd = r(N)

di as txt "Pool members with an MD in mg IV MME : `k_md' of `k_pool'"
di as txt "Pool members with Hedges' g          : `k_smd' of `k_pool'"

di as txt _n "Members with NO estimable MD (weight-normalised or Median/IQR):"
list study_unit unit data_type if broadpool == 1 & missing(md_mme), clean noobs
di as txt _n "Members with NO estimable SMD (Median/IQR, no derived mean/SD):"
list study_unit unit data_type if broadpool == 1 & missing(hedges_g), clean noobs

di as txt _n "CONCLUSION: a k=`k_pool' mean-difference pool is NOT estimable without"
di as txt "reconstructing absolute doses from group-mean body weights, which the"
di as txt "v26 lock explicitly prohibits. No such model is fitted."

* ------------------------------------------------------------------------------
* 3. BROADER SMD SENSITIVITY ANALYSIS (scale-free; k=9)
* ------------------------------------------------------------------------------
di as txt _n "------------------------------------------------------------------"
di as txt "3. BROADER SMD SENSITIVITY (REML + Hartung-Knapp)"
di as txt "------------------------------------------------------------------"

gen byte broad_smd = (broadpool == 1 & !missing(hedges_g, hedges_se))
count if broad_smd == 1
local k_broadsmd = r(N)
summarize n_total if broad_smd == 1, meanonly
local n_broadsmd = r(sum)
di as txt "Broader SMD set: k = `k_broadsmd', N = `n_broadsmd'"
list study_unit unit if broad_smd == 1, clean noobs

meta set hedges_g hedges_se if broad_smd == 1, studylabel(study_unit) ///
    eslabel("Standardized Mean Difference (Hedges' g)")
meta summarize, random(reml) se(kh)
matrix res_broad = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))

meta forestplot, ///
    title("BROADER 24-h SENSITIVITY (SMD): strict + conditional trials", size(medium)) ///
    subtitle("Random-effects REML + Hartung-Knapp (k=`k_broadsmd')", size(small)) ///
    nullrefline nonotes
graph export "06_FINAL_ANALYSIS_V26/04_FIGURES/forest_opioid24_broader_smd.png", width(1800) replace

* Strict SMD on the identical metric, for a like-for-like comparison.
di as txt _n "------------------------------------------------------------------"
di as txt "4. STRICT SMD REFERENCE (same metric, k=`k_strict')"
di as txt "------------------------------------------------------------------"
meta set hedges_g hedges_se if strict == 1, studylabel(study_unit) ///
    eslabel("Standardized Mean Difference (Hedges' g)")
meta summarize, random(reml) se(kh)
matrix res_strictsmd = (r(theta), r(ci_lb), r(ci_ub), r(p), r(N), r(tau2), r(I2), r(Q))

* ------------------------------------------------------------------------------
* 5. EXPORT
* ------------------------------------------------------------------------------
clear
set obs 2
gen analysis_id      = ""
gen analysis_type    = ""
gen stratum          = ""
gen k                = .
gen n_participants   = .
gen effect_measure   = ""
gen estimate         = .
gen ci_low           = .
gen ci_high          = .
gen p_value          = .
gen tau2             = .
gen i2               = .
gen q_stat           = .
gen model            = ""
gen notes            = ""

replace analysis_id    = "OP24_STRICT_SMD" in 1
replace analysis_type  = "Strict primary (SMD reference)" in 1
replace stratum        = "Strict primary 24-h opioid, Hedges g" in 1
replace k              = res_strictsmd[1,5] in 1
replace n_participants = `n_strict' in 1
replace effect_measure = "Hedges g (SMD)" in 1
replace estimate       = res_strictsmd[1,1] in 1
replace ci_low         = res_strictsmd[1,2] in 1
replace ci_high        = res_strictsmd[1,3] in 1
replace p_value        = res_strictsmd[1,4] in 1
replace tau2           = res_strictsmd[1,6] in 1
replace i2             = res_strictsmd[1,7] in 1
replace q_stat         = res_strictsmd[1,8] in 1
replace model          = "REML + Hartung-Knapp" in 1
replace notes          = "Strict set on the SMD metric; comparator for the broader SMD model" in 1

replace analysis_id    = "OP24_BROADER_SMD" in 2
replace analysis_type  = "Broader sensitivity (SMD)" in 2
replace stratum        = "Strict + conditional 24-h opioid, Hedges g" in 2
replace k              = res_broad[1,5] in 2
replace n_participants = `n_broadsmd' in 2
replace effect_measure = "Hedges g (SMD)" in 2
replace estimate       = res_broad[1,1] in 2
replace ci_low         = res_broad[1,2] in 2
replace ci_high        = res_broad[1,3] in 2
replace p_value        = res_broad[1,4] in 2
replace tau2           = res_broad[1,6] in 2
replace i2             = res_broad[1,7] in 2
replace q_stat         = res_broad[1,8] in 2
replace model          = "REML + Hartung-Knapp" in 2
replace notes          = "Adds Coura 2011, Sim 2002, Zhang 2025. Chen 2015 x2 remain unpoolable (Median/IQR). A k=11 MD pool is not estimable without prohibited body-weight reconstruction." in 2

save "06_FINAL_ANALYSIS_V26/03_RESULTS/results_broader24h_sensitivity.dta", replace
export delimited "06_FINAL_ANALYSIS_V26/03_RESULTS/results_broader24h_sensitivity.csv", replace
list analysis_id k n_participants estimate ci_low ci_high p_value i2, clean noobs

di as txt _n "SUCCESS: broader 24-h sensitivity analysis complete."
log close
