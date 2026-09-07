clear all
set more off
local xls "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx"
local sheets README Study_Master AF_Result_Lock AF_Unresolved AF_P1_Disposition AF_Priority_QA Scope_Exclusion_Audit Stata_Opioid24_Primary Stata_AF_Long Stata_Manifest Outcome_Data_AF_LOCK

foreach s of local sheets {
    di as txt "Exporting `s'..."
    capture import excel using "`xls'", sheet("`s'") firstrow clear
    if _rc == 0 {
        export delimited "06_FINAL_ANALYSIS_V26/01_DATA/authoritative_sheets/`s'.csv", replace
    }
    else {
        di as err "Failed to export `s'"
    }
}
di as txt "ALL SHEETS EXPORTED."
