* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: META-REGRESSION & MODERATOR ANALYSIS
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* Output Log: dashboard/stata_moderator_meta_regression.log
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_moderator_meta_regression.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD AUDITED CONSENSUS SYNTHESIS DATASET
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)

describe
count

* ------------------------------------------------------------------------------
* 2. DECLARE META-ANALYSIS FOR CONTINUOUS PRIMARY OUTCOME (24-H OPIOID CONSUMPTION)
* ------------------------------------------------------------------------------
meta set md_mme se_mme, studylabel(study_key)

* ------------------------------------------------------------------------------
* 3. BASELINE RANDOM-EFFECTS META-ANALYSES (UNMODERATED TAU-SQUARED)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "BASELINE MODEL: TEAS vs Sham Primary Random-Effects (REML + HK)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "BASELINE MODEL: EA vs Sham Primary Random-Effects (REML + HK)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Sham", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 4. TEAS VS SHAM: PRESPECIFIED PROTOCOL MODERATORS
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "TEAS MODEL 1 (PRESPECIFIED): Cumulative Stimulation Duration (per 30-min increment)"
di as txt "=================================================================="
meta regress duration_30min if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_teas_duration_bubble.png", replace

di as txt _n "=================================================================="
di as txt "TEAS MODEL 2 (PRESPECIFIED): Stimulation Timing Category"
di as txt "=================================================================="
encode timing_cat, gen(timing_num)
* Setting Preoperative only as reference category
recode timing_num (3=1 "Preoperative only") (1=2 "Multi-phase (Perioperative)") (2=3 "Postoperative only"), gen(timing_factor)
label values timing_factor timing_lbl
meta regress b1.timing_factor if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 5. TEAS VS SHAM: HIGH-PRIORITY ADDITIONAL MODERATORS
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "TEAS MODEL 3 (HIGH-PRIORITY): Control-Group 24-h Opioid Consumption (IV MME)"
di as txt "Scientific Question: Are larger absolute opioid-sparing effects observed"
di as txt "in surgical settings with higher baseline opioid requirement?"
di as txt "=================================================================="
meta regress arm2_mean if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_teas_control_mme_bubble.png", replace

di as txt _n "=================================================================="
di as txt "TEAS MODEL 4 (DATA PROVENANCE): Data Derivation Method (Exact vs Converted)"
di as txt "0 = Exact unconverted (Category A), 1 = Converted/derived (Category B)"
di as txt "=================================================================="
meta regress b0.is_converted if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "TEAS MODEL 5 (TEMPORAL): Publication Year (Continuous)"
di as txt "=================================================================="
meta regress year if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_teas_year_bubble.png", replace

* ------------------------------------------------------------------------------
* 6. TEAS VS SHAM: MULTIVARIABLE MODEL (MAX 2 PREDICTORS, STRICT RATIONALE)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "TEAS MODEL 6 (MULTIVARIABLE): Cumulative Duration (30-min) + Control Opioid (MME)"
di as txt "Checking joint moderation of dose and baseline surgical opioid demand"
di as txt "=================================================================="
meta regress duration_30min arm2_mean if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 7. EA VS SHAM: EXPLORATORY UNIVARIABLE MODERATORS (k=11, NO MULTIVARIABLE)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "EA MODEL 1 (EXPLORATORY): Cumulative Stimulation Duration (per 30-min increment)"
di as txt "=================================================================="
meta regress duration_30min if modality == "EA" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_ea_duration_bubble.png", replace

di as txt _n "=================================================================="
di as txt "EA MODEL 2 (EXPLORATORY): Control-Group 24-h Opioid Consumption (IV MME)"
di as txt "=================================================================="
meta regress arm2_mean if modality == "EA" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_ea_control_mme_bubble.png", replace

di as txt _n "=================================================================="
di as txt "EA MODEL 3 (EXPLORATORY): Publication Year (Continuous)"
di as txt "=================================================================="
meta regress year if modality == "EA" & comparator == "Sham", random(reml) se(kh)
estat bubbleplot
graph export "dashboard/stata_ea_year_bubble.png", replace

di as txt _n "=================================================================="
di as txt "END OF META-REGRESSION EXECUTION"
di as txt "=================================================================="

log close
