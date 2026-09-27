* 99_run_all.do -- full Stata analysis layer. Run from the repository root:  sh 10_FINAL_ADJUDICATION/13_STATA/run_stata.sh
do "10_FINAL_ADJUDICATION/13_STATA/do/00_setup.do"
do "$STATA/do/01_import_canonical.do"
do "$STATA/do/02_effect_sizes.do"
do "$STATA/do/03_models.do"
do "$STATA/do/04_figures.do"
do "$STATA/do/05_descriptives.do"
