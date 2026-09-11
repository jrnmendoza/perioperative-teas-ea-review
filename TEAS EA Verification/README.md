# Master data workbooks — which one is authoritative

**`TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx` is the master.**
`scripts/build_site.py` declares it (`master_version: v34`), and every live
analytical script reads it. Nothing else in this directory is authoritative.

Earlier workbooks are kept as the **audit trail** for a registered systematic
review (PROSPERO CRD420251090635). They record how the dataset evolved and are
the evidence a reviewer or journal would ask for. Do not delete them.

| Workbook | Status | Read by live code? |
|---|---|---|
| `..._v34_FINAL_LOCK_READY.xlsx` | **MASTER** | Yes — the build, the validator, all v34 analysis scripts |
| `..._v33_FINAL_LOCK_READY.xlsx` | Superseded | Referenced by `.github/workflows/deploy-pages.yml` |
| `..._v32_FINAL_LOCK_READY.xlsx` | Superseded — **archival only** | No |
| `..._v26_FINAL_LOCK_READY.xlsx` | Superseded | Yes — `scripts/validate_dashboard.py` |
| `..._v20_PRIMARY_OPIOID_SET.xlsx` | Superseded — **archival only** | No |
| `TEAS_EA_v32_SUPPLEMENTARY_MISSED_OUTCOMES_FOR_CLAUDE_CODE.xlsx` | Superseded — archival only | No |

`scripts/validate_dashboard.py` enforces this: a check fails if live analytical
code starts reading a workbook marked archival above. Changing that table
without changing what the code reads will fail the build.

## The v26 directory is NOT archival

`06_FINAL_ANALYSIS_V26/` is load-bearing despite its name. It holds the locked
target datasets that generate `dashboard/browser_targets.js` and
`dashboard/primary_browser.js` — the files the dashboard actually pools — and it
is shipped as the site's `v26/` download mirror. Deleting it breaks the build.

The version numbers in **directory** names record when a layer was introduced,
not which data is current. `06_FINAL_ANALYSIS_V26/` carries the current locked
target datasets; `09_V34_ANALYSIS/` carries the v34 additions on top of them.

## Where the numbers actually come from

```
source PDFs  ->  v34 master workbook  ->  locked target datasets
                                          (06_FINAL_ANALYSIS_V26/01_DATA/)
                                                    |
                                          scripts/build_reference_data.py
                                          scripts/sync_dashboard_outcomes.py
                                                    |
                                          dashboard/browser_targets.js
                                          dashboard/primary_browser.js
                                          dashboard/data.js  (GENERATED)
                                                    |
                                                 dashboard
```

`dashboard/data.js` is **generated, not authored**. Run
`python3 scripts/sync_dashboard_outcomes.py` to regenerate it;
`scripts/build_site.py` refuses to build when it has been hand-edited away from
the lock. This is the control added after the 2026-09-10 placeholder incident —
see `99_audit/2026-09-10_placeholder_incident/`.
