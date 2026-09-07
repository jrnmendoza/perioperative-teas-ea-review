capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_af.log", replace

di "=== INSPECTING Stata_AF_Long ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_AF_Long") firstrow clear
describe
count
tab endpoint_stratum
tab provisional_status
list study_unit endpoint_stratum provisional_status in 1/30, clean

di "=== INSPECTING AF_Result_Lock ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("AF_Result_Lock") firstrow clear
describe
count

log close
