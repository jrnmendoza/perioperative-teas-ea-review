clear all
set more off
use "06_FINAL_ANALYSIS_V26/01_DATA/target_F_exploratory.dta", clear
tab target
di as txt _n "=== TARGET F DETAILED LISTING ==="
list target study comparison_id n_i mean_i sd_i n_c mean_c sd_c e_i e_c unit timepoint result_rob, clean
