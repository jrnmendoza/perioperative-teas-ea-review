# Superseded dashboard artifacts (pre-v26)

These files were served from `dashboard/` (and therefore from the live site) up to
the v26 reconciliation. They are **retained for reproducibility and audit only**.
Nothing here is a current analysis output, and nothing here is linked from the
dashboard any more.

**Current authoritative outputs live in `06_FINAL_ANALYSIS_V26/`.**

Archived on 2026-09-07, branch `claude-v26-dashboard-final`.

## Why each group was superseded

| Group | Files | Reason |
| --- | --- | --- |
| Consensus primary pool | `stata_consensus_synthesis_data.csv`, `stata_audited_synthesis.{do,log}` | 11-trial pool (Chen 1998, El-Rakshy 2009, Seevaunnamtum 2016, Chen 2020, Yang 2024, He 2026, Sim 2002, Coura 2011, both Chen 2015 reports, Zhang 2025). The v26 strict primary set is k=6; Sim 2002, Coura 2011, the Chen 2015 pair and Zhang 2025 are conditional, not primary. |
| Old 48-h synthesis | `stata_48h_opioid_synthesis.{do,log}`, `stata_48h_opioid_synthesis_data.csv`, `stata_forest_48h_opioid_*.png` | Five-study set: Chen 2020, **He 2026**, Zhang 2023, An 2014, **Wong 2006**. v26 Target A strict is Chen 2020 / Zhang 2023 / An 2014 only; He 2026 (breast/WJCO) and Wong 2006 are explicit `EXCLUDE` rows in `AF_Result_Lock` (A-005, A-006). |
| Old 72-h synthesis | `stata_72h_opioid_synthesis.{do,log}`, `stata_72h_opioid_synthesis_data.csv`, `stata_forest_72h_opioid_*.png` | v26 Target B strict is Yang 2024 alone (k=1, **NOT POOLED**); Zhang 2025 (POD1) and Xie 2014 (48 h) are `EXCLUDE` rows (B-003, B-004). |
| Meta-regression | `stata_meta_regression_execution.{do,log}`, `stata_moderator_meta_regression.do`, `stata_meta_reg_*.png`, `stata_*_bubble.png`, `stata_extended_moderators.csv` | Fitted to the withdrawn 11-trial pool, which counted Yeh 2010 and Yeh 2011 as independent trials. v26 fits one meta-regression only (modality, k=6, p=0.807), explicitly logged as underpowered. |
| Secondary pool | `stata_secondary_synthesis_data.csv`, `stata_forest_{flatus,pain,ponv}.png` | Single broad pools. v26 stratifies PONV into six separate strata and restricts pain to results measured **at rest**. |
| TEAS-only outputs | `stata_forest_teas_*.png`, `results__stata_teas_leave_one_out_results.*` | Superseded by the v26 modality subgroup analysis and `08_sensitivity.do` leave-one-out. |
| Duplicated master results | `results__stata_master_results.{csv,json}` | Byte-identical to `master_reconciled_results_v26.{csv,json}`; the legacy filename was ambiguous about which version it held. |
| Misc | `stata_test_data.csv`, `stata_strategy_synthesis.{do,log}` | Development scratch / search-strategy synthesis, never part of the outcome analysis. |

## Replacement map

| Was | Now |
| --- | --- |
| `stata_audited_synthesis.do` | `06_FINAL_ANALYSIS_V26/02_STATA/00_master.do`, `01_opioid24_primary.do` |
| `stata_audited_synthesis.log` | `06_FINAL_ANALYSIS_V26/02_STATA/logs/01_opioid24_primary.log` |
| `stata_consensus_synthesis_data.csv` | `06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv` |
| `stata_secondary_synthesis_data.csv` | `06_FINAL_ANALYSIS_V26/01_DATA/target_{C,D,E,F}_*.csv` |
| `stata_48h_opioid_synthesis*` | `06_FINAL_ANALYSIS_V26/02_STATA/02_targetA_48h.do`, `01_DATA/target_A_48h.csv`, `02_STATA/logs/02_targetA_48h.log` |
| `stata_72h_opioid_synthesis*` | `06_FINAL_ANALYSIS_V26/02_STATA/03_targetB_72h.do`, `01_DATA/target_B_72h.csv` |
| `stata_meta_regression_execution*` | `06_FINAL_ANALYSIS_V26/02_STATA/09_subgroups_metareg.do` + `logs/09_subgroups_metareg.log` |
| `stata_master_results.csv` | `06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv` |
