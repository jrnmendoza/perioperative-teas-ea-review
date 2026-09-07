capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_opioid_primary_sheet.log", replace

di "=== INSPECTING Opioid_Primary_StudyLevel ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Opioid_Primary_StudyLevel") firstrow clear
describe
list, clean

di "=== INSPECTING Outcome_Data_AF_LOCK for Target A ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Outcome_Data_AF_LOCK") firstrow clear
describe
list if target == "A", clean

log close
