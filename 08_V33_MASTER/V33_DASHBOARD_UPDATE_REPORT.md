# V33 Dashboard Update Report

Perioperative TEAS & EA systematic review · PROSPERO CRD420251090635
Date: 2026-09-08

---

## 1. Principle

**No dashboard result is copied from previous HTML or JS.** The analytical layer
is generated from the v33 master and the Stata result files, and the markup
contains containers only — the validator fails the build if a count or estimate
is written into the HTML.

Generation chain:

```
TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx
        └─ 00_prep_data.do ─────────► locked analysis datasets (.dta/.csv)
                └─ Stata analyses ──► 03_RESULTS/*.csv
                        └─ scripts/build_v33_dashboard_data.py ──► dashboard/v33_data.js
                        └─ scripts/build_primary_pathway.py ─────► dashboard/primary_pathway.js
                        └─ scripts/build_tiered_v33.py ──────────► dashboard/tiered_v33.js
                                └─ scripts/build_site.py ────────► _site/
```

---

## 2. New feature: Study Contribution Map

Added to the Primary tab as **"How the Included Trials Contribute"**. It answers
one question directly: why do 70 included RCTs produce a primary meta-analysis
of 7?

Every one of the 70 canonical studies is mapped across 11 outcome families,
derived from the 382 v33 outcome rows. A study may appear in several families.

| Outcome family | Studies |
|---|---:|
| Primary 0–24 h opioid | 7 |
| Other postoperative opioid | 30 |
| Intraoperative opioid | 18 |
| Rescue analgesia / opioid | 11 |
| PCA demand / presses | 13 |
| Pain | 28 |
| PONV / nausea / vomiting | 26 |
| Quality of recovery | 5 |
| GI recovery | 14 |
| LOS / recovery | 5 |
| Other / narrative only | 8 |

The panel states plainly that the 63 non-contributing trials were fully
screened, extracted and RoB-assessed, and that their absence from the primary
model is a **reporting** limitation, not an exclusion. It also names the trials
(Grech 2016, Zhan 2020) whose every outcome is graph-only or unreported, so they
remain visible rather than silently vanishing from the map.

### Two mapper bugs found and fixed during construction

1. **Prefix matching credited the wrong trial.** `He 2026 (breast/WJCO)` and
   `He 2026 (hepatectomy/JIS)` are different trials; a stem match on "He 2026"
   credited the breast trial with the hepatectomy trial's primary contribution
   and reported 8 primary contributors against a locked k of 7. Matching is now
   exact. This is precisely the failure mode the integration brief warned about
   ("Do not match only by study name").
2. **Studies with only graph-only rows disappeared.** Grech 2016 and Zhan 2020
   have outcome rows but no analysable numbers anywhere, so they mapped to no
   family and dropped out of the display — losing the clearest illustration of
   the map's own point. They are now surfaced explicitly.

---

## 3. Also added

- **v33 secondary results table** — the six regenerated secondary analyses with
  k, estimate, CI, p and I², read from `results_v33_secondary.csv`.
- **Not-pooled register** — 11 outcomes that exist in the evidence base but are
  deliberately excluded from every model, each with its reason on the face of
  the dashboard rather than buried in a file.

---

## 4. Version metadata

`_site/build-meta.json` now reports:

| Field | Value | Source |
|---|---|---|
| `master_version` | `v33` | build script constant |
| `master_file` | `TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx` | build script constant |
| `canonical_studies` | 70 | parsed from `data.js` |
| `source_normalized_outcome_rows` | 382 | **counted from v33 `Outcome_Data`** |
| `strict_primary_opioid_k` | 7 | parsed from the Stata result table |

The outcome-row count was previously read from the workbook's `Summary` cell,
which still held v32's 364 inside the v33 workbook. `build_site.py` now counts
`Outcome_Data` directly and raises if the workbook's own stated figure
disagrees, so the "do not hard-code 364" requirement is enforced mechanically
rather than by habit.

---

## 5. Stale-version audit

| Token | Live analytical use | Historical mention |
|---|---|---|
| `v26` | none — directory name only | changelogs, audit trail |
| `v31` | none | none |
| `v32` | none in analytical code | changelogs, provenance history, v33 build script (correctly, as the base) |
| `v33` | all live analysis | — |
| `63 RCT` | none | historical reconciliation notes |
| `69 RCT` | none | none |
| `k=6` | none | withdrawal prose |
| `364` | none | v33 integration report (as the v32 figure) |

Historical documentation legitimately mentions previous versions; the check is
that no *live analytical asset* derives from them. The directory
`06_FINAL_ANALYSIS_V26/` retains its name for path stability but its
`00_prep_data.do` reads the v33 master.

---

## 6. Validation

- `scripts/validate_dashboard.py` — 56 checks passing.
- `08_V33_MASTER/qc_v33_master.py` — 26 checks passing.
- `scripts/deploy_integrity_check.py` — passing.
- Browser QA on the built artifact: panels render, figures load, no console
  errors.
