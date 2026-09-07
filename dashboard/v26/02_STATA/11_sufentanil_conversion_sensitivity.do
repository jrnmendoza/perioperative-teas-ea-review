* ==============================================================================
* 11_sufentanil_conversion_sensitivity.do
*   Sensitivity analysis across the plausible sufentanil:morphine conversion range
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 BE
* ==============================================================================
*
* BACKGROUND
*   06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv documents that the
*   sufentanil-to-morphine factor previously used throughout this project's Stata
*   pipeline (0.1 mg MME per ug, i.e. a 100:1 potency ratio, hardcoded in
*   00_prep_data.do with no citation) was NOT supportable:
*
*     - it is identical to the FENTANYL ratio used elsewhere in the same file
*     - no located source places IV sufentanil at 100:1
*     - every located source places sufentanil at 5-10x fentanyl:
*         * BC Ministry of Health equianalgesic table: sufentanil 0.01-0.04 mg
*           (10-40 ug) = morphine 10 mg parenteral, i.e. 250:1 to 1000:1
*         * FDA/Pfizer sufentanil citrate label: "as much as 10 times as potent
*           as fentanyl" in balanced general anaesthesia
*
*   The factor was therefore CORRECTED to 1.0 mg MME per ug (1000:1) in
*   00_prep_data.do on 2026-09-07, which is the value the dashboard methods page
*   had always stated and the upper bound of the sourced BC range. That corrected
*   factor is now the prespecified primary. See the audit CSV for the full trail.
*
* PURPOSE OF THIS SCRIPT
*   The sourced range (250:1 to 1000:1) is wide, so the choice of point within it
*   is a genuine methodological uncertainty rather than a settled constant. This
*   script recomputes the strict primary and the Target A broader-window pooled
*   MDs across the full range so that uncertainty is reported explicitly instead
*   of being absorbed silently into a single number.
*
*   Chen 2020 (sufentanil) is 1 of the 6 strict primary trials. Zhang 2025 and
*   Xie 2014 (Target A) are the other sufentanil-converted rows. Factor 1.0 in
*   the loops below reproduces the primary analysis exactly; factor 0.1
*   reproduces the superseded pre-correction result and is retained only so the
*   magnitude of the correction is auditable.
*
*   This script alters no locked classification, no primary specification, and no
*   strict/conditional assignment. It is a reporting sensitivity only.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/11_sufentanil_conversion_sensitivity.log", replace

di as txt "=================================================================="
di as txt "11: SUFENTANIL CONVERSION FACTOR SENSITIVITY"
di as txt "    Primary = 1.0 mg MME per ug (1000:1). Range audited: 0.1 to 1.0."
di as txt "=================================================================="

* ------------------------------------------------------------------------------
* PART 1: STRICT PRIMARY (k=6) UNDER ALTERNATIVE SUFENTANIL FACTORS
*   Only Chen 2020 is sufentanil-converted within the strict primary set.
* ------------------------------------------------------------------------------
foreach factor in 0.1 0.25 0.5 1.0 {
    use "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.dta", clear
    keep if inc_primary == 1

    replace mean_i_mme = mean_i * `factor' if unit == "µg sufentanil"
    replace sd_i_mme   = sd_i   * `factor' if unit == "µg sufentanil"
    replace mean_c_mme = mean_c * `factor' if unit == "µg sufentanil"
    replace sd_c_mme   = sd_c   * `factor' if unit == "µg sufentanil"
    replace md_mme = mean_i_mme - mean_c_mme if unit == "µg sufentanil"
    replace se_mme = sqrt((sd_i_mme^2/n_i) + (sd_c_mme^2/n_c)) if unit == "µg sufentanil"

    meta set md_mme se_mme, studylabel(study_unit) eslabel("Mean Difference (mg IV MME)")
    meta summarize, random(reml) se(kh)

    di as txt _n "Sufentanil factor = `factor' mg MME per ug | Strict primary k=6:"
    di as txt "  MD = " %6.3f r(theta) "  95% KH CI [" %6.3f r(ci_lb) ", " %6.3f r(ci_ub) "]  p = " %6.4f r(p) "  I2 = " %5.2f r(I2) "%"
}

* ------------------------------------------------------------------------------
* PART 2: TARGET A BROADER WINDOW (INCL. XIE 2014) UNDER ALTERNATIVE FACTORS
*   Chen 2020 and Xie 2014 are both sufentanil-converted in this set.
* ------------------------------------------------------------------------------
foreach factor in 0.1 0.25 0.5 1.0 {
    use "06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.dta", clear
    * Matches 02_targetA_48h.do's TA_INCL_XIE sample exactly: one Xie 2014
    * contrast only (EAS vs Sham), not both duplicated comparison rows.
    keep if include_strict == 1 | comparison_id == "XIE14_EAS_vs_SHAM_TOTALSUF"

    replace mean_i_mme = mean_i * `factor' if unit == "µg sufentanil"
    replace sd_i_mme   = sd_i   * `factor' if unit == "µg sufentanil"
    replace mean_c_mme = mean_c * `factor' if unit == "µg sufentanil"
    replace sd_c_mme   = sd_c   * `factor' if unit == "µg sufentanil"
    replace md_mme = mean_i_mme - mean_c_mme if unit == "µg sufentanil"
    replace se_mme = sqrt((sd_i_mme^2/n_i) + (sd_c_mme^2/n_c)) if unit == "µg sufentanil"

    meta set md_mme se_mme, studylabel(study) eslabel("Mean Difference (mg IV MME)")
    meta summarize, random(reml) se(kh)

    di as txt _n "Sufentanil factor = `factor' mg MME per ug | Target A broader (incl. Xie 2014), k=4:"
    di as txt "  MD = " %6.3f r(theta) "  95% KH CI [" %6.3f r(ci_lb) ", " %6.3f r(ci_ub) "]  p = " %6.4f r(p) "  I2 = " %5.2f r(I2) "%"
}

di as txt _n "=================================================================="
di as txt "INTERPRETATION"
di as txt "=================================================================="
di as txt "A higher sufentanil:morphine ratio makes the sufentanil trials' opioid-"
di as txt "sparing effect LARGER in mg IV MME terms, because the same raw microgram"
di as txt "difference is scaled by a bigger factor. The correction from 0.1 to 1.0"
di as txt "therefore increases effect magnitude and widens confidence intervals; it"
di as txt "does not manufacture statistical significance. Under the corrected primary"
di as txt "factor the strict primary remains non-significant, and the Target A broader"
di as txt "window moves from significant to non-significant. Conclusions are reported"
di as txt "at factor 1.0 with this full range disclosed as a sensitivity."
di as txt ""
di as txt "Standardized (SMD / Hedges' g) analyses in this project are computed from"
di as txt "NATIVE units and are therefore invariant to every factor in this loop."

log close
