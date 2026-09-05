* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: STATA AUDITED DATA SYNTHESIS
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* Input Datasets: 
*   1. dashboard/stata_consensus_synthesis_data.csv (11 Analyzable Trials, N=945)
*   2. dashboard/stata_secondary_synthesis_data.csv (Secondary Endpoints)
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_audited_synthesis.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD AUDITED PRIMARY OPIOID DATASET (11 TRIALS: 6 DIRECT + 5 DERIVED)
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)

describe
list canonical_name modality comparator md_mme se_mme hedges_g hedges_se opioid_status rob2_overall

* ------------------------------------------------------------------------------
* 2. PRIMARY OUTCOME SYNTHESIS: CONTINUOUS 24-H OPIOID CONSUMPTION (IV MME mg)
* ------------------------------------------------------------------------------
meta set md_mme se_mme, studylabel(canonical_name)

di as txt _n "=================================================================="
di as txt "PRIMARY SYNTHESIS 1: ALL 11 ANALYZABLE TRIALS (6 DIRECT + 5 DERIVED)"
di as txt "Random-Effects REML + Hartung-Knapp-Sidik-Jonkman (HKSJ) Adjustment"
di as txt "=================================================================="
meta summarize, random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "PRIMARY SYNTHESIS 1B: ALL 11 TRIALS — DerSimonian-Laird Random Effects"
di as txt "=================================================================="
meta summarize, random(dl) se(kh)

di as txt _n "=================================================================="
di as txt "SUBGROUP A: 6 DIRECTLY REPORTED TRIALS"
di as txt "=================================================================="
meta summarize if opioid_status == "Primary Direct", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SUBGROUP B: 5 DERIVED CONDITIONAL TRIALS"
di as txt "=================================================================="
meta summarize if opioid_status == "Derived Conditional", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 1: TEAS vs Sham (k=8 Trials, N=725)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 2: EA vs Control / Sham (k=3 Trials, N=220)"
di as txt "=================================================================="
meta summarize if modality == "EA", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS: Exclude High Risk of Bias (El-Rakshy 2009)"
di as txt "=================================================================="
meta summarize if is_high_rob == 0, random(reml) se(kh)

* Generate MME Forest Plot for All 11 Trials Subgrouped by Data Reporting Status
meta forestplot, subgroup(opioid_status) ///
    title("Cumulative 0-24h Opioid Sparing (IV MME mg): All 11 Analyzable Trials", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Hartung-Knapp (k=11, N=945)", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_teas_mme.png", width(1600) replace

* ------------------------------------------------------------------------------
* 3. STANDARDIZED MEAN DIFFERENCE (HEDGES' G SMD) — SCALE-INDEPENDENT
* ------------------------------------------------------------------------------
meta set hedges_g hedges_se, studylabel(canonical_name)

di as txt _n "=================================================================="
di as txt "STANDARDIZED EFFECT SIZE: All 11 Analyzable Trials (Hedges' g SMD)"
di as txt "=================================================================="
meta summarize, random(reml) se(kh) predinterval

meta forestplot, subgroup(opioid_status) ///
    title("Standardized Mean Difference (Hedges' g): All 11 Analyzable Trials", size(medium)) ///
    subtitle("StataNow 19.5 SE: Scale-Free Random Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_teas_smd.png", width(1600) replace

* ------------------------------------------------------------------------------
* 4. SECONDARY OUTCOMES: PAIN, FLATUS TIME, AND PONV
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_secondary_synthesis_data.csv", clear varnames(1)

* A) PAIN AT 24 HOURS
preserve
keep if outcome_domain == "Pain_24h"
di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME: Pain Intensity at ~24 Hours (Resting VAS/NRS)"
di as txt "=================================================================="
meta set effect se, studylabel(canonical_name)
meta summarize, random(reml) se(kh)

meta forestplot, ///
    title("Secondary Outcome: Resting Pain at ~24h (VAS/NRS 0-10)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_pain.png", width(1600) replace
restore

* B) TIME TO FIRST FLATUS (GI RECOVERY)
preserve
keep if outcome_domain == "Flatus_Time"
di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME: Time to First Postoperative Flatus (Hours)"
di as txt "=================================================================="
meta set effect se, studylabel(canonical_name)
meta summarize, random(reml) se(kh)

meta forestplot, ///
    title("Secondary Outcome: Time to First Flatus (Hours)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_flatus.png", width(1600) replace
restore

* C) POSTOPERATIVE NAUSEA & VOMITING (PONV)
preserve
keep if outcome_domain == "PONV"
di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME: Postoperative Nausea & Vomiting (Risk Ratio)"
di as txt "=================================================================="
meta esize arm1_events arm1_n arm2_events arm2_n, esize(lnrr) studylabel(canonical_name)
meta summarize, random(reml) se(kh) eform

meta forestplot, ///
    title("Secondary Outcome: Postoperative Nausea & Vomiting (Risk Ratio)", size(medium)) ///
    subtitle("Random-Effects REML + Hartung-Knapp (Exponentiated RR)", size(small)) ///
    nullrefline nonotes eform
graph export "dashboard/stata_forest_ponv.png", width(1600) replace
restore

di as txt _n "=================================================================="
di as txt "STATA AUDITED SYNTHESIS EXECUTION COMPLETED SUCCESSFULLY"
di as txt "=================================================================="
capture log close
exit
