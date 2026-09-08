* ==============================================================================
* 00_master.do: Master Pipeline Orchestrator for Locked v26 Analysis
* Systematic Review: Perioperative TEAS & EA for Postoperative Opioid Sparing
* PROSPERO: CRD420251090635
* Engine: StataNow 19.5 BE (c(edition)=BE, flavor IC)
* ==============================================================================

clear all
set more off
capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/00_master.log", replace

di as txt "=================================================================="
di as txt "STARTING MASTER VERIFICATION & ANALYSIS PIPELINE (LOCKED v26 DATA)"
di as txt "Date/Time: `c(current_date)' `c(current_time)'"
di as txt "Stata Version: `c(stata_version)' `c(edition)'"
di as txt "=================================================================="

* 1. Data Preparation & Harmonization
di as txt _n ">>> STEP 1: Running 00_prep_data.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/00_prep_data.do"

* 2. Primary 24-h Opioid Consumption
di as txt _n ">>> STEP 2: Running 01_opioid24_primary.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/01_opioid24_primary.do"

* 3. Target A: 0-48 h Cumulative Opioid
di as txt _n ">>> STEP 3: Running 02_targetA_48h.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/02_targetA_48h.do"

* 4. Target B: 0-72 h Cumulative Opioid
di as txt _n ">>> STEP 4: Running 03_targetB_72h.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/03_targetB_72h.do"

* 5. Target C: Pain Intensity at Rest ~24 h
di as txt _n ">>> STEP 5: Running 04_pain.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/04_pain.do"

* 6. Target D: Postoperative Nausea & Vomiting (Stratified)
di as txt _n ">>> STEP 6: Running 05_ponv.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/05_ponv.do"

* 7. Target E: Time to First Flatus
di as txt _n ">>> STEP 7: Running 06_flatus.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/06_flatus.do"

* 8. Target F: Exploratory Outcomes (Titrated, Delivered, Rescue, PCA)
di as txt _n ">>> STEP 8: Running 07_targetF.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/07_targetF.do"

* 9. Comprehensive Sensitivity & Leave-One-Out Analyses
di as txt _n ">>> STEP 9: Running 08_sensitivity.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/08_sensitivity.do"

* 10. Subgroup Analyses & Meta-Regression Audit
di as txt _n ">>> STEP 10: Running 09_subgroups_metareg.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/09_subgroups_metareg.do"

* 11. Broader 24-h Sensitivity & Estimability Audit
di as txt _n ">>> STEP 11: Running 10_broader24h_sensitivity.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/10_broader24h_sensitivity.do"

* 12. Sufentanil Conversion Factor Sensitivity (primary = 1.0; range 0.1-1.0)
di as txt _n ">>> STEP 12: Running 11_sufentanil_conversion_sensitivity.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/11_sufentanil_conversion_sensitivity.do"

* 13. Full Leave-One-Out Diagnostic Table for the Strict Primary Pool
di as txt _n ">>> STEP 13: Running 12_primary_loo_diagnostics.do ..."
do "06_FINAL_ANALYSIS_V26/02_STATA/12_primary_loo_diagnostics.do"

* 14. v33 tiered primary-outcome analysis (S0/S1/S2/S3 + sensitivity)
di as txt _n ">>> STEP 14: Running 07_TIERED_V33/02_STATA/13_tiered_primary_v33.do ..."
do "07_TIERED_V33/02_STATA/13_tiered_primary_v33.do"

di as txt _n "=================================================================="
di as txt "MASTER VERIFICATION & ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!"
di as txt "All models executed under StataNow 19.5 BE."
di as txt "All datasets, logs, tables, and figures updated in 06_FINAL_ANALYSIS_V26/"
di as txt "Date/Time: `c(current_date)' `c(current_time)'"
di as txt "=================================================================="

log close
