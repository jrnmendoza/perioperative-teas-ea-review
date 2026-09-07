capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_target_F_all.log", replace

import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_AF_Long") firstrow clear

di "=== TARGET F: F_intraop_titrated_requirement ==="
list lock_id study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if endpoint_stratum == "F_intraop_titrated_requirement", clean

di "=== TARGET F: F_postop_delivered_dose_or_solution ==="
list lock_id study comparison_id include_strict include_sensitivity n_i n_c mean_i sd_i mean_c sd_c unit if endpoint_stratum == "F_postop_delivered_dose_or_solution", clean

di "=== TARGET F: F_rescue_opioid ==="
list lock_id study comparison_id include_strict include_sensitivity n_i events_i n_c events_c data_type unit if endpoint_stratum == "F_rescue_opioid", clean

di "=== TARGET F: F_PCA_behavior ==="
list lock_id study outcome include_strict include_sensitivity n_i mean_i sd_i median_i q1_i q3_i n_c mean_c sd_c median_c q1_c q3_c unit if endpoint_stratum == "F_PCA_behavior", clean

di "=== TARGET F: F_intraop_fixed_or_unclear_exposure ==="
list lock_id study outcome include_strict include_sensitivity unit if endpoint_stratum == "F_intraop_fixed_or_unclear_exposure", clean

di "=== TARGET F: F_rescue_nonopioid ==="
list lock_id study outcome include_strict include_sensitivity unit events_i n_i events_c n_c if endpoint_stratum == "F_rescue_nonopioid", clean

di "=== TARGET F: F_rescue_mixed_or_undefined ==="
list lock_id study outcome include_strict include_sensitivity unit events_i n_i events_c n_c if endpoint_stratum == "F_rescue_mixed_or_undefined", clean

log close
