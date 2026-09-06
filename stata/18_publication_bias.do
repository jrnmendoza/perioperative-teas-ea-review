* ==============================================================================
* STATA DO-FILE 18: SMALL-STUDY EFFECTS & PUBLICATION BIAS AUDIT
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Authoritative Engine: StataNow 19.5 SE (Standard Edition)
* Input: stata/stata_consensus_synthesis_data.csv (k=11 trials)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/18_publication_bias.log", replace text

di as txt "=================================================================="
di as txt "18: PUBLICATION BIAS & SMALL-STUDY EFFECTS INVESTIGATION"
di as txt "Caveat: In the presence of extreme between-study heterogeneity (I2 > 90%),"
di as txt "funnel asymmetry tests have elevated type I error rates and must be interpreted cautiously."
di as txt "=================================================================="

use "stata/stata_consensus_synthesis_data.dta", clear
describe
meta set md_mme se_mme, studylabel(canonical_name)

* 1. Funnel Plot
meta funnelplot, title("Funnel Plot: Primary 24-h Opioid Consumption", size(medium)) ///
    subtitle("StataNow 19.5 SE: Pseudo 95% Confidence Limits (k=11 Trials)", size(small)) ///
    ytitle("Standard Error (SE)") xtitle("Treatment Effect (MD IV MME mg)")
graph export "stata/results/funnel_plot_24h_opioid.png", width(1800) replace

* 2. Egger-Type Linear Regression Test for Funnel Asymmetry
di as txt _n "------------------------------------------------------------------"
di as txt "EGGER LINEAR REGRESSION TEST FOR FUNNEL ASYMMETRY"
di as txt "------------------------------------------------------------------"
meta bias, egger

* 3. Begg-Type Rank Correlation Test
di as txt _n "------------------------------------------------------------------"
di as txt "BEGG RANK CORRELATION TEST"
di as txt "------------------------------------------------------------------"
meta bias, begg

di as txt _n "METHODOLOGICAL SUMMARY:"
di as txt "With k = 11 studies and substantial between-study variance (tau2 = 30.01),"
di as txt "funnel asymmetry can reflect genuine clinical heterogeneity across surgical"
di as txt "specialties rather than selective non-reporting alone."

log close
