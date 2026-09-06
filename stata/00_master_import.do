* ==============================================================================
* STATA DO-FILE 00: MASTER IMPORT & DATA INTEGRITY VERIFICATION
* Review: Perioperative TEAS & EA Systematic Review & Meta-Analysis
* Engine: StataNow 19.5 SE (Standard Edition)
* ==============================================================================

clear all
set more off
capture log close
log using "stata/logs/00_master_import.log", replace text

di as txt "=================================================================="
di as txt "00: AUDITING AND IMPORTING ALL SYSTEMATIC REVIEW DATASETS"
di as txt "=================================================================="

* 1. Check Primary 24-h Opioid Dataset (k=11)
import delimited "stata/stata_consensus_synthesis_data.csv", clear varnames(1)
describe
di as txt "Primary 24h opioid observations: " _N
assert _N == 11
list canonical_name modality comparator md_mme se_mme
save "stata/stata_consensus_synthesis_data.dta", replace

* 2. Check Key Secondary 48-h Opioid Dataset (k=5)
import delimited "stata/stata_48h_opioid_synthesis_data.csv", clear varnames(1)
describe
di as txt "Key Secondary 48h opioid observations: " _N
assert _N == 5
list canonical_name modality comparator md_mme se_mme
save "stata/stata_48h_opioid_synthesis_data.dta", replace

* 3. Check Exploratory 72-h Opioid Dataset (k=4)
import delimited "stata/stata_72h_opioid_synthesis_data.csv", clear varnames(1)
describe
di as txt "Exploratory 72h opioid observations: " _N
assert _N == 4
list canonical_name modality comparator md_mme se_mme
save "stata/stata_72h_opioid_synthesis_data.dta", replace

* 4. Check Secondary Outcomes Dataset (Pain, Flatus, PONV)
import delimited "stata/stata_secondary_synthesis_data.csv", clear varnames(1)
describe
di as txt "Secondary outcomes observations: " _N
tab outcome_domain
save "stata/stata_secondary_synthesis_data.dta", replace

* 5. Check Intraoperative Remifentanil Dataset (k=11)
import delimited "stata/stata_intraop_remifentanil_data.csv", clear varnames(1)
describe
di as txt "Intraoperative remifentanil observations: " _N
assert _N == 11
list canonical_name arm1_mean arm1_sd arm2_mean arm2_sd md se
save "stata/stata_intraop_remifentanil_data.dta", replace

* 6. Check Rescue Analgesia Dataset (k=9)
import delimited "stata/stata_rescue_analgesia_data.csv", clear varnames(1)
describe
di as txt "Rescue analgesia observations: " _N
assert _N == 9
list canonical_name arm1_events arm1_n arm2_events arm2_n rescue_drug is_opioid
save "stata/stata_rescue_analgesia_data.dta", replace

* 7. Check Extended Moderators Dataset
import delimited "stata/stata_extended_moderators.csv", clear varnames(1)
describe
di as txt "Extended moderators observations: " _N
save "stata/stata_extended_moderators.dta", replace

di as txt _n "SUCCESS: All master datasets imported, verified, and converted to Stata .dta."
log close
