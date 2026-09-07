capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_af_targets.log", replace

import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_AF_Long") firstrow clear

di "=== TARGET A ==="
list lock_id study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "A", clean

di "=== TARGET B ==="
list lock_id study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "B", clean

di "=== TARGET C ==="
list lock_id study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if target == "C", clean

di "=== TARGET D ==="
list lock_id study endpoint_stratum include_strict include_sensitivity n_i events_i n_c events_c if target == "D", clean

di "=== TARGET E ==="
list lock_id study data_type include_strict include_sensitivity n_i mean_i sd_i median_i q1_i q3_i n_c mean_c sd_c median_c q1_c q3_c unit if target == "E", clean

di "=== TARGET F (Summary of strata and includes) ==="
tab endpoint_stratum include_strict if substr(target,1,1) == "F"
tab endpoint_stratum include_sensitivity if substr(target,1,1) == "F"

log close
