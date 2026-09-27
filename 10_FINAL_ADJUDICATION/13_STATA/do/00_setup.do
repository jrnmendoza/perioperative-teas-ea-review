* 00_setup.do -- common settings for the Stata analysis layer.
* Run everything through 99_run_all.do from the repository root (run_stata.sh does this).
version 19.5
clear all
set more off
set varabbrev off
set linesize 120
global ROOT "`c(pwd)'"
global STATA "$ROOT/10_FINAL_ADJUDICATION/13_STATA"
confirm file "$STATA/input/stata_model_inputs.csv"
foreach d in output figures tables logs work {
    capture mkdir "$STATA/`d'"
}
set scheme stcolor
graph set svg fontface "Helvetica"
* Record the exact software used; compare_stata.py copies this into the manifest.
tempname fh
file open `fh' using "$STATA/output/stata_run_info.csv", write replace text
file write `fh' "stata_version,edition,born_date,os,machine" _n
file write `fh' "`c(stata_version)',`c(edition_real)',`c(born_date)',`c(os)',`c(machine_type)'" _n
file close `fh'
