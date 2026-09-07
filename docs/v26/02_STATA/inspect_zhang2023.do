capture log close
log using "06_FINAL_ANALYSIS_V26/02_STATA/logs/inspect_zhang2023.log", replace

di "=== INSPECTING Zhang 2023 in AF_Result_Lock ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("AF_Result_Lock") firstrow clear
list if Canonicalmast == "Zhang 2023", clean

di "=== INSPECTING Zhang 2023 in Outcome_Data_AF_LOCK ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("Outcome_Data_AF_LOCK") firstrow clear
list if Canonicalstudy == "Zhang 2023", clean

di "=== INSPECTING Zhang 2023 in AF_P1_Disposition ==="
import excel using "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx", sheet("AF_P1_Disposition") firstrow clear
list if regexm(Studyresult, "Zhang 2023"), clean

log close
