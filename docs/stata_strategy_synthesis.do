* ==============================================================================
* PERIOPERATIVE TEAS & EA SYSTEMATIC REVIEW: STATA DATA SYNTHESIS STRATEGY
* Principal Investigator: John Ryan N. Mendoza, RN, MSc (Lund University)
* Software: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "dashboard/stata_strategy_synthesis.log", replace text

* ------------------------------------------------------------------------------
* 1. LOAD AND PREPARE AUDITED DATASET
* ------------------------------------------------------------------------------
import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)

describe
count

* ------------------------------------------------------------------------------
* 2. DECLARE META-ANALYSIS DATA VIA INVERSE-VARIANCE CONTINUOUS OUTCOMES
* ------------------------------------------------------------------------------
* Primary Outcome: Continuous 24-h cumulative opioid consumption in IV MME
meta set md_mme se_mme, studylabel(study_key)

* ------------------------------------------------------------------------------
* 3. STRATIFIED ANALYSES BY MODALITY (TEAS & EA WILL NOT BE COMBINED)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 1: TEAS vs Sham-Controlled TEAS (REML + Hartung-Knapp)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "PRIMARY STRATUM 2: EA vs Sham-Controlled EA (REML + Hartung-Knapp)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Sham", random(reml) se(kh) predinterval

di as txt _n "=================================================================="
di as txt "SUPPORTIVE STRATUM 1: TEAS vs Usual Care (No Stimulation / Open-Label)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Usual Care", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SUPPORTIVE STRATUM 2: EA vs Usual Care (No Stimulation / Open-Label)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Usual Care", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 4. PROTOCOL MODERATOR META-REGRESSION (SEPARATE FOR TEAS AND EA)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "META-REGRESSION (TEAS): Cumulative Stimulation Duration (per 30-min increment)"
di as txt "=================================================================="
meta regress duration_30min if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "META-REGRESSION (TEAS): Timing Category"
di as txt "=================================================================="
encode timing_cat, gen(timing_num)
meta regress i.timing_num if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "META-REGRESSION (TEAS): Frequency Category"
di as txt "=================================================================="
encode frequency_cat, gen(freq_num)
meta regress i.freq_num if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "META-REGRESSION (TEAS): Number of Treatment Sessions (Single vs Repeated)"
di as txt "=================================================================="
encode sessions_cat, gen(sess_num)
meta regress i.sess_num if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "META-REGRESSION (EA): Cumulative Stimulation Duration (per 30-min increment)"
di as txt "=================================================================="
meta regress duration_30min if modality == "EA" & comparator == "Sham", random(reml) se(kh)

* ------------------------------------------------------------------------------
* 5. SENSITIVITY ANALYSES & ESTIMATOR COMPARISONS
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS 1: Alternative Variance Estimator (DerSimonian-Laird)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(dl)

di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS 2: Alternative Variance Estimator (Paule-Mandel)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(pm)

di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS 3: Exclude Converted/Imputed Data (Category A Only)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham" & is_converted == 0, random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS 4: Restrict to Low Risk of Bias (RoB 2)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham" & rob2_overall == "Low", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SENSITIVITY ANALYSIS 5: Leave-One-Out Sensitivity Analysis (TEAS vs Sham)"
di as txt "=================================================================="
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) leaveoneout

di as txt _n "=================================================================="
di as txt "CLINICAL THRESHOLDS: 5 mg MME, 8 mg MME, and 30% Relative Reduction"
di as txt "=================================================================="
tabulate reaches_5mg if modality == "TEAS" & comparator == "Sham"
tabulate reaches_8mg if modality == "TEAS" & comparator == "Sham"
summarize pct_reduction if modality == "TEAS" & comparator == "Sham", detail

* ------------------------------------------------------------------------------
* 6. SECONDARY OUTCOMES (PAIN AT REST, PAIN ON MOVEMENT, PONV RISK RATIO)
* ------------------------------------------------------------------------------
di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 1: 24-h VAS Pain at Rest (TEAS vs Sham)"
di as txt "=================================================================="
meta set pain_rest_md pain_rest_se if !missing(pain_rest_md) & !missing(pain_rest_se), studylabel(study_key)
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 2: 24-h VAS Pain at Rest (EA vs Sham)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 3: 24-h VAS Pain on Movement (TEAS vs Sham)"
di as txt "=================================================================="
meta set pain_mov_md pain_mov_se if !missing(pain_mov_md) & !missing(pain_mov_se), studylabel(study_key)
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 4: 24-h VAS Pain on Movement (EA vs Sham)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Sham", random(reml) se(kh)

di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 5: 24-h PONV (Risk Ratio, TEAS vs Sham)"
di as txt "=================================================================="
meta esize ponv_arm1_ev ponv_arm1_tot ponv_arm2_ev ponv_arm2_tot if !missing(ponv_arm1_ev) & !missing(ponv_arm2_ev), esize(lnrr) studylabel(study_key)
meta summarize if modality == "TEAS" & comparator == "Sham", random(reml)

di as txt _n "=================================================================="
di as txt "SECONDARY OUTCOME 6: 24-h PONV (Risk Ratio, EA vs Sham)"
di as txt "=================================================================="
meta summarize if modality == "EA" & comparator == "Sham", random(reml)

log close
