* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: 48-HOUR OPIOID SYNTHESIS
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* Dataset: dashboard/stata_48h_opioid_synthesis_data.csv (k=5 Trials, N=2,183)
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_48h_opioid_synthesis.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD 48-H OPIOID CONSUMPTION DATASET
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_48h_opioid_synthesis_data.csv", clear varnames(1)

describe
list canonical_name modality comparator md_mme se_mme hedges_g hedges_se opioid_status rob2_overall

* ------------------------------------------------------------------------------
* 2. CONTINUOUS 48-H OPIOID CONSUMPTION (IV MME mg)
* ------------------------------------------------------------------------------
meta set md_mme se_mme, studylabel(canonical_name)

di as txt _n "=================================================================="
di as txt "48-H OPIOID SYNTHESIS: ALL 5 TRIALS (TEAS + EA, N=2,183)"
di as txt "Random-Effects REML + Hartung-Knapp-Sidik-Jonkman (HKSJ) Adjustment"
di as txt "=================================================================="
meta summarize, random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 1: TEAS vs Sham at 48 Hours (k=3 Trials, N=2,077)"
di as txt "=================================================================="
meta summarize if modality == "TEAS", random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 2: EA vs Control / Sham at 48 Hours (k=2 Trials, N=106)"
di as txt "=================================================================="
meta summarize if modality == "EA", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SUBGROUP: DIRECTLY REPORTED ONLY (k=4 Trials, N=345)"
di as txt "=================================================================="
meta summarize if opioid_status == "Primary Direct", random(reml) se(kh)

* Generate 48-h MME Forest Plot Subgrouped by Modality (Protocol Standard)
meta forestplot, subgroup(modality) ///
    title("Cumulative 0-48h Opioid Sparing (IV MME mg): Modality Stratified", size(medium)) ///
    subtitle("StataNow 19.5 SE: Random-Effects REML + Hartung-Knapp (k=5, N=2,183)", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_48h_opioid_mme.png", width(1600) replace

* ------------------------------------------------------------------------------
* 3. STANDARDIZED MEAN DIFFERENCE (HEDGES' G SMD) — SCALE-INDEPENDENT
* ------------------------------------------------------------------------------
meta set hedges_g hedges_se, studylabel(canonical_name)

di as txt _n "=================================================================="
di as txt "STANDARDIZED EFFECT SIZE: 48-h Opioid Consumption (Hedges' g SMD)"
di as txt "=================================================================="
meta summarize, random(reml) se(kh) predinterval

meta forestplot, subgroup(modality) ///
    title("Standardized Mean Difference (Hedges' g): 0-48h Opioid Consumption", size(medium)) ///
    subtitle("StataNow 19.5 SE: Scale-Free Random Effects REML + Hartung-Knapp", size(small)) ///
    nullrefline nonotes
graph export "dashboard/stata_forest_48h_opioid_smd.png", width(1600) replace

di as txt _n "=================================================================="
di as txt "STATA 48-H OPIOID SYNTHESIS COMPLETED SUCCESSFULLY"
di as txt "=================================================================="
capture log close
exit
