# V33 Analysis QC Report

Perioperative TEAS & EA systematic review · PROSPERO CRD420251090635
Date: 2026-09-08 · Engine: StataNow 19.5

---

## 1. Assertions required by the integration brief

| Assertion | Result |
|---|---|
| `canonical studies == 70` | **PASS** — Study_Master holds 70 rows, no duplicates |
| `strict primary opioid k == 7` | **PASS** — `OP24_PRIM_COMB` k = 7; no adjudication STOP raised |
| no NaN | **PASS** |
| no undefined | **PASS** |
| no duplicated contrasts | **PASS** — composite-key check over all 382 rows |
| no duplicated shared controls | **PASS** — Zhu 2022 and Lu 2021 contribute one contrast per model |
| no silent median→mean conversion | **PASS** — statistic-type integrity asserted per row |
| no PCA reservoir→consumption conversion | **PASS** |
| no rescue incidence→MME conversion | **PASS** |
| no graph-only numerical promotion | **PASS** |
| no POD1→exact 24-h relabeling | **PASS** — Zhang 2025 still excluded from 0–24 h analyses |

---

## 2. Gate results

| Gate | Checks | Result |
|---|---:|---|
| `08_V33_MASTER/qc_v33_master.py` | 26 | all pass |
| `scripts/validate_dashboard.py` | 60 | all pass |
| `scripts/deploy_integrity_check.py` | 12 | all pass |
| Stata error scan across all logs | 20 logs | zero `r(nnn);` |

### In-Stata integrity gates

`13_tiered_primary_v33.do` refuses to fit rather than fitting something
prohibited, and exits non-zero if a correlated multi-arm alternative enters S0,
if an S0 row has a missing MD or SE, if a row falls into zero or both comparator
strata, or if any MD/SE fails to reproduce from arm-level values. All passed.

---

## 3. Reproduction checks

**Primary outcome, v32 run vs v33 run** — identical to every printed digit:

| | k | MD | 95% KH CI | p | τ² | I² |
|---|---:|---:|---|---:|---:|---:|
| v32 | 7 | −9.90700 | −20.0794, +0.2654 | 0.054538 | 113.911 | 98.57% |
| v33 | 7 | −9.90700 | −20.0794, +0.2654 | 0.054538 | 113.911 | 98.57% |

This is the expected result: nothing in the supplement was primary-eligible, so
a change here would have signalled contamination.

**Dashboard vs Stata** — the validator recomputes every published secondary
estimate against `results_v33_secondary.csv` and every tiered estimate against
`TIERED_ANALYSIS_RESULTS_v33.csv`, to 1e-6. All agree.

**Arithmetic** — every MD and SE in the derived analysis sets is recomputed
inside Stata from the arm-level means, SDs and Ns before use.

---

## 4. Mutation testing

A check that never fails is not a check. Each new guard was deliberately broken
and confirmed to trip — and to trip alone.

| Guard | Mutation | Result |
|---|---|---|
| No appended row is primary-eligible | Flag one appended row `Yes` | FAIL, correctly |
| No duplicated outcome contrasts | Duplicate an existing row | FAIL, correctly |
| v33 layer matches Stata | Corrupt a secondary estimate in `v33_data.js` | FAIL, correctly |
| Contribution map reconciles | Set primary family to 8 | FAIL, correctly |
| Live code reads v33 | Revert `00_prep_data.do` to v32 | FAIL, correctly |
| Deploy integrity | Set `source_normalized_outcome_rows` to 364 | FAIL, correctly |

---

## 5. Defects found and fixed during this pass

**D1 — Formula cache loss (would have corrupted 190 rows).**
v32 holds 596 formula cells. openpyxl discards Excel's cached results on save,
so a naive copy-and-append would have given every consumer reading with
`data_only=True` a `None` for the derived-effect columns of 190 of the 364 v32
rows. The build now materialises all 596 cached values, and the QC gate asserts
v33 has no more blanks than v32 did.

**D2 — Stale outcome-row count inside the authoritative workbook.**
The v33 `Summary` sheet inherited v32's "Source-normalized outcome rows = 364"
while `Outcome_Data` held 382, and `build_site.py` read that cell.
`build_site.py` now counts `Outcome_Data` directly and raises if the workbook's
own stated figure disagrees.

**D3 — Name-prefix match credited the wrong trial.**
The contribution map matched studies to the strict primary set by author-year
stem, so `He 2026 (breast/WJCO)` inherited `He 2026 (hepatectomy/JIS)`'s
contribution and the map reported 8 primary contributors against a locked k of
7. Matching is now exact, and a validator check asserts map ⇄ k agreement.

**D4 — Studies with only graph-only rows vanished from the map.**
Grech 2016 and Zhan 2020 have outcome rows but no analysable numbers, so they
mapped to no family and disappeared — losing the clearest illustration of the
map's own argument. They are now surfaced explicitly, and the validator fails
if any study maps to nothing.

**D5 — Deploy gate hardcoded v32/364 as expectations.**
It would have blocked every correct v33 deployment while blessing a stale one.
Expectations are now derived from the workbook the build actually used.

**D6 — Validator function-name collision.**
A new `t_v33_panel_is_dynamic` shadowed the existing tiered-panel check of the
same name, silently removing it while the suite still reported all-pass. Caught
by counting definitions; the new one was renamed.

---

## 6. Honest statement on the new significant results

Three v33 analyses reach *p* < 0.05. None changes the review's conclusion, and
each is reported with its limitation on the face of the dashboard.

**Binary rescue opioid use (RR 0.52, p = 0.014, I² = 0%, k = 3) is fragile.**
Yu 2020 — the trial this analysis was newly built around — carries 80.8% of the
weight. Leave-one-out shows the result does not survive omission of either
Yu 2020 (p = 0.114) or Tu 2024 (p = 0.112). An I² of 0% at k = 3 reflects three
similar point estimates, not a well-estimated between-study variance. This is
hypothesis-generating.

**Intraoperative remifentanil (MD −104 µg, p = 0.002, k = 9)** is a different
estimand from postoperative opioid consumption and says nothing about opioid
sparing after surgery. Intraoperative dosing is titrated by the anaesthetist,
so the outcome is exposed to performance bias wherever blinding was imperfect.

**Time to first defecation (MD −10.3 h, p = 0.020, I² = 88.6%, k = 8)** is not
an artefact of the new data: excluding the newly added Yang 2020 contrast gives
−11.95 h (p = 0.022). Heterogeneity remains severe.

The primary outcome is unchanged and remains non-significant.

---

## 7. Open items requiring human decision

1. **Result-specific RoB 2** for the 16 newly added analysable outcomes. They
   are published as source-verified data with provenance, not as RoB-rated
   evidence, and must not be GRADE-rated until assessed.
2. **Yu 2020 author contact** — SD and P-value contradictions between Table 2,
   the Results text and the abstract.
3. **Liang 2021 author contact** — definition, unit and window of the
   "postoperative analgesia requirement" outcome.
4. **17 remaining extraction targets** — several PDFs are present locally and
   could be extracted in a scoped follow-up pass.
5. **Yeh 2010/2011** publication-family overlap remains unadjudicated.
6. Whether the intraoperative-opioid analyses should be reported at all, given
   that they answer a different question from the review's primary aim.
