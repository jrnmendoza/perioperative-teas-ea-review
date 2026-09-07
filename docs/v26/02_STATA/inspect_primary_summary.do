capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_primary_summary.log", replace

di "=== INSPECTING Opioid_Primary_Summary ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Opioid_Primary_Summary") firstrow clear
describe
list, clean

di "=== INSPECTING Set_Opioid_24h ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Set_Opioid_24h") firstrow clear
describe
list, clean

di "=== INSPECTING Analysis_Summary ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Analysis_Summary") firstrow clear
describe
list, clean

log close
