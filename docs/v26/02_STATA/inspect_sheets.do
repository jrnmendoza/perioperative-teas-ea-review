capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_sheets.log", replace

di "=== INSPECTING Stata_Opioid24_Primary ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_Opioid24_Primary") firstrow clear
describe
list, clean noobs

di "=== INSPECTING Stata_Manifest ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Stata_Manifest") firstrow clear
describe
list, clean noobs

di "=== INSPECTING AF_P1_Disposition ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("AF_P1_Disposition") firstrow clear
describe
list, clean noobs

log close
