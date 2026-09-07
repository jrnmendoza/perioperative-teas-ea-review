capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_af_details.log", replace

import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_AF_Long") firstrow clear
tab target
tab endpoint_stratum
tab include_strict
tab include_sensitivity
tab narrative_only

di "--- Stata_AF_Long for Target A ---"
list study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "Target A", clean

di "--- Stata_AF_Long for Target B ---"
list study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "Target B", clean

di "--- Stata_AF_Long for Target C ---"
list study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "Target C", clean

di "--- Stata_AF_Long for Target D ---"
list study endpoint_stratum include_strict include_sensitivity n_i events_i n_c events_c if target == "Target D", clean

di "--- Stata_AF_Long for Target E ---"
list study data_type include_strict include_sensitivity n_i mean_i sd_i median_i q1_i q3_i n_c mean_c sd_c median_c q1_c q3_c unit if target == "Target E", clean

di "--- AF_Result_Lock describe ---"
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("AF_Result_Lock") firstrow clear
describe
count

log close
