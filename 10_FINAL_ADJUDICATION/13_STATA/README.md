# Stata analysis layer

Stata (StataNow/SE 19.5, official `meta` suite) reproduces every canonical model and produces the publication figures.
It reads only canonical data, exported deterministically; no study values are typed into do-files.

```
canonical data (04_MODELS, 09_E2_ANALYSIS, 08_QOR_ANALYSIS, 14_CHARACTERISTICS)
  -> code/export_stata_inputs.py      input/stata_model_inputs.csv, stata_models.csv, figure_specs.csv (+ sha256)
  -> run_stata.sh -> do/99_run_all.do
       00_setup.do            paths, scheme, software record (output/stata_run_info.csv)
       01_import_canonical.do import the exported CSVs
       02_effect_sizes.do     meta esize from arm data; row-level check vs canonical yi/vi
       03_models.do           REML + truncated Knapp-Hartung (k >= 2); single-study estimates (k = 1)
       04_figures.do          forest, leave-one-out and funnel figures (SVG, PDF, PNG)
       05_descriptives.do     evidence-base figures and table from the harmonised characteristics
  -> code/compare_stata.py            comparison with canonical (Python) and R/metafor, figure register,
                                      manifest, STATA_RECONCILIATION.md, METHODS_STATEMENT.md
```

Run from the repository root:

```
python3 10_FINAL_ADJUDICATION/code/build_characteristics.py
python3 10_FINAL_ADJUDICATION/code/export_stata_inputs.py
sh 10_FINAL_ADJUDICATION/13_STATA/run_stata.sh
python3 10_FINAL_ADJUDICATION/code/compare_stata.py
```

Key outputs: `output/stata_verification_summary.csv` (one status per model), `output/stata_canonical_comparison.csv`
(every compared field), `output/figure_register.csv`, `output/stata_manifest.csv`, `STATA_RECONCILIATION.md`.
Canonical results are the reference; Stata never overwrites them.
