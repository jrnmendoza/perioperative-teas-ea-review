* ==============================================================================
* 11_sufentanil_conversion_sensitivity.do
*   Sensitivity analysis for the unresolved sufentanil:morphine conversion factor
*   Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
*   PROSPERO: CRD420251090635
*   Engine: StataNow 19.5 BE
* ==============================================================================
*
* PURPOSE
*   06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv documents that the
*   sufentanil-to-morphine conversion factor actually used throughout this
*   project's Stata pipeline (0.1 mg MME per ug, i.e. a 100:1 potency ratio,
*   hardcoded in 00_prep_data.do with no citation) is UNRESOLVED:
*
*     - it equals the FENTANYL ratio, not a documented sufentanil-specific ratio
*     - the dashboard's own methods page separately and inconsistently claims
*       a 1000:1 ratio for sufentanil, citing sources not held in this repo
*     - published equianalgesic literature places IV sufentanil:morphine
*       potency at approximately 500:1 to 1000:1, with acute-postoperative
*       ratios reported to vary with duration (e.g. 267:1 to 791:1 in one
*       cited study)
*
*   Chen 2020 (sufentanil, strict primary) is 1 of the 6 strict primary trials.
*   Zhang 2025 and Xie 2014 (Target A) are sufentanil-converted conditional
*   rows. This script does NOT change the primary analysis. It quantifies, as
*   an explicit sensitivity check, how much the strict primary MD and the
*   Target A broader-window MD would move under alternative factors drawn from
*   the audited literature range, so the uncertainty is visible rather than
*   silently absorbed into a single unverified number.
*
*   No primary or locked conditional/strict classification is altered by this
*   script. It only recomputes the pooled MD with Chen 2020 / Zhang 2025 /
*   Xie 2014's sufentanil arms re-expressed at alternative factors.
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/11_sufentanil_conversion_sensitivity.log", replace

di as txt "=================================================================="
di as txt "11: SUFENTANIL CONVERSION FACTOR SENSITIVITY (UNRESOLVED - AUDIT ONLY)"
di as txt "=================================================================="

* ------------------------------------------------------------------------------
* PART 1: STRICT PRIMARY (k=6) UNDER ALTERNATIVE SUFENTANIL FACTORS
*   Only Chen 2020 is sufentanil-converted within the strict primary set.
* ------------------------------------------------------------------------------
foreach factor in 0.1 0.5 1.0 {
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
foreach factor in 0.1 0.5 1.0 {
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
di as txt "AUDIT CONCLUSION"
di as txt "=================================================================="
di as txt "The direction of any correction is unambiguous: a higher sufentanil:morphine"
di as txt "ratio makes Chen 2020's (and Xie 2014's) opioid-sparing effect LARGER in mg"
di as txt "MME terms, not smaller, because the same raw microgram difference is scaled"
di as txt "by a bigger factor. Whether the true ratio is 100:1, 500:1, or 1000:1 remains"
di as txt "UNRESOLVED per opioid_conversion_audit.csv. No factor is adopted as primary"
di as txt "by this script. The locked primary analysis (01_opioid24_primary.do, factor"
di as txt "= 0.1) is UNCHANGED and remains the reported strict primary result pending"
di as txt "independent pharmacological verification."

log close
