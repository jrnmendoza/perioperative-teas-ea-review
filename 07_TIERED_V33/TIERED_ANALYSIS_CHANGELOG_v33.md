# Tiered Primary-Outcome Analysis — Changelog (v33)

## v33.0 — 2026-09-07 — Derivability audit (audit only; no analysis regenerated)

**Provenance:** `TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx` treated as
immutable and read-only. All v33 artifacts live in `07_TIERED_V33/` and derive from it.
Nothing was written back to v32; no pipeline dataset, dashboard value, or published
estimate was modified in this pass.

### Added
- `build_derivability_audit.py` — generates the audit from v32 with explicit,
  reviewable classification rules plus PDF-verified per-study overrides.
- `PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv` / `.xlsx` — 93 contrast rows across
  63 studies, with per-row transformation, assumptions, conversion factor + source,
  tier, comparator category, and PDF locator.
- `TIERED_ANALYSIS_QC_REPORT_v33.md` — findings, per-study QC table, proposed
  architecture, unresolved items.
- `00_WORKING/` — raw v32 extracts used as audit input.

### Classification decisions (all PDF-verified this pass)
- **Gao 2022 → Tier C.** Exact 0–24 h pump sufentanil IS reported, as median (IQR)
  33.0 (0.0, 50.0) vs 30.0 (0.0, 60.0), P=0.197, n=827/828. Must not be described as
  "primary outcome unavailable"; must not be transformed to mean/SD (25th percentile
  is 0.0 in both arms → zero-inflated, non-normal).
- **Chen 2015 → Tier B+C.** Rescue count × fixed 2 mg IV morphine is exact and
  order-preserving: 2 (2–6) vs 7 (4–14) mg IV morphine.
- **Gu 2019 → Tier D.** PCIA 100 µg/100 mL = exactly 1 µg/mL (conversion valid), but
  24 h value appears only in Fig. 4; text reports 4 h, 8 h, 36 h. Fixed 2 mL/h basal
  infusion noted.
- **Zhang 2025 → Tier E, REMOVED from all 0–24 h analyses.** Source defines "PODs 0
  (day of surgery), 1, and 2"; POD 1 is a separate calendar day, not the first 24 h.
- **Song 2020 → Tier E** on two independent grounds: press-vs-delivery ambiguity with
  a documented 15-min lockout, and no sourced IV MME factor for butorphanol.
- **Oztas 2019 → Tier E.** No sourced tramadol/pethidine factor; combined-total SD
  unrecoverable without covariance.
- **Coura 2011 → Tier E for absolute MME** (µg/kg, no weights) but SMD-eligible;
  additionally supplementary morphine/fentanyl was permitted, so reported fentanyl is
  not complete opioid exposure.
- **Chen 2015 (Hyperalgesia) → Tier E for absolute MME**, deterministic in µg/kg only.

### Methodological refinement introduced
Tiers are assigned per-metric: `tier_mme` (absolute IV MME) is separate from
`smd_eligible` (scale-invariant). This resolves why Coura 2011 / Sim 2002 / Jin 2023
are legitimately usable on the SMD metric while genuinely ineligible for absolute MME.

### Defect recorded (not yet fixed)
`00_prep_data.do` assigns `comparator_type` with a case-sensitive `"Sham"` match,
misfiling 4 rows (Chen 2015, Chen 2015 Hyperalgesia, Zhang 2025 → should be Sham;
Yeh family → active electrical). No published estimate is affected (all have
`inc_primary = 0`), but it must be fixed before comparator-stratified analyses.

### Pending (next stage, not started)
Stata verification datasets and `.do`, tiered results tables, forest plots,
sensitivity plots, dashboard update, Methods/Results/Discussion text.

---

# Stage 2 — execution (2026-09-08)

The movements proposed at the end of Stage 1 were approved and executed. This
section records what actually ran and what changed.

## Code changes

| File | Change |
|---|---|
| `06_FINAL_ANALYSIS_V26/02_STATA/00_prep_data.do` | **Comparator classifier rewritten.** Case-sensitivity defect fixed by lower-casing before matching, and rule order corrected so inert-sham markers (`0 mA`, `zero-current`, `no stimulation`, `nonpenetrating`, `placebo`) are tested **before** device names. Matching `TENS` first would have misfiled a genuine sham-controlled trial such as "Sham ST36 TENS (0 mA)" as an active electrical comparator. Post-fix classification: 11 Sham, 1 Active Electrical, 4 Usual Care / Control. |
| `06_FINAL_ANALYSIS_V26/02_STATA/10_broader24h_sensitivity.do` | Zhang 2025 excluded from the broader SMD set (Tier E, POD1 ≠ 0–24 h clock window). k = 10 → 9. The superseded k = 10 model is still fitted and exported as `OP24_BROADER_SMD_WITH_ZHANG` so the effect of the exclusion is visible. |
| `06_FINAL_ANALYSIS_V26/02_STATA/00_master.do` | New STEP 14 runs the v33 tiered analysis. |
| `07_TIERED_V33/build_tiered_dataset.py` | **New.** Builds the Stata-ready v33 datasets. Every row carries its source value, unit, sourced conversion factor, tier and stratum. |
| `07_TIERED_V33/02_STATA/13_tiered_primary_v33.do` | **New.** S0/S1/S2/S3, comparator and estimator sensitivity, LOO, figures A–D. |
| `scripts/sync_master_results.py` | **New.** Syncs the master aggregate from the Stata result tables. `--check` fails on drift. |
| `scripts/build_tiered_v33.py` | **New.** Generates `dashboard/tiered_v33.js`. |
| `scripts/build_primary_pathway.py` | Zhang 2025 removed from the broader-SMD set; provenance updated to v32. |
| `scripts/build_site.py` | Mirrors `07_TIERED_V33/` into the deployed artifact as `v33/`; `tiered_v33.js` added to cache-busting. |
| `scripts/validate_dashboard.py` | Six new checks (below). |

## Integrity gates in the do-file

`13_tiered_primary_v33.do` refuses to pool rather than pooling something
prohibited. It exits non-zero if a correlated multi-arm alternative contrast is
flagged into S0, if an S0 row has a missing MD or SE, if a row falls into zero or
both comparator strata, or if any MD/SE fails to reproduce from the arm-level
MME means and SDs. All four gates passed.

## Results

| Analysis | k | Estimate (mg IV MME) | 95% CI | p | I² |
|---|---|---|---|---|---|
| **S0 primary — TEAS vs inert sham** | 4 | −13.995 | −34.18 to +6.19 | 0.114 | 98.59% |
| **S0 supportive — EA vs usual care** | 3 | −3.936 | −19.77 to +11.90 | 0.397 | 77.15% |
| S1 (adds Tier B) | 4 | identical to S0 | — | — | — |
| S2 (Tier C) | 2 | not pooled — medians reported in parallel | — | — | — |
| S3 (adds Tier D) | 4 | identical to S0 | — | — | — |
| Sensitivity: Szmit usual-care arm swapped in | 4 | −14.071 | −34.18 to +6.04 | 0.112 | 98.59% |
| Sensitivity: REML + Wald | 4 | −13.995 | −26.64 to −1.36 | 0.030 | 98.59% |
| Sensitivity: DerSimonian–Laird + HK | 4 | −14.024 | −34.19 to +6.14 | 0.114 | 98.71% |

Prediction intervals: S0 primary [−74.40, +46.41]; S0 supportive [−86.30, +78.43].

Broader scale-free SMD, k = 9: Hedges' g = −0.969 (−1.801 to −0.137), p = 0.028,
I² = 94.99%. Superseded k = 10 model: g = −0.934 (−1.665 to −0.203), p = 0.018.

**Independent reproduction.** S0's two strata reproduce `OP24_TEAS_SHAM` and
`OP24_EA_CTRL` from the v32 pipeline to every printed digit, from a separately
constructed dataset built from the source PDFs rather than from the locked
`.dta`. The agreement is a genuine cross-check, not a re-read of the same file.

## Empty cells, stated rather than filled

- **EA vs inert sham: k = 0.** No sham-controlled EA trial reports an analysable
  0–24 h cumulative opioid mean/SD in absolute dose units.
- **Tier B increment: none.** Chen 2015's exact rescue-bolus derivation yields
  medians, so it is Tier C, not Tier B.
- **Tier D increment: none.** Gu 2019 failed digitization validation (below).

## Gu 2019 digitization — attempted, validated, rejected

Figure 4 was digitized under the pre-specified protocol. The y-axis calibrated
exactly against nine labelled gridlines (`value = −0.2083333 × row + 101.9792`,
maximum residual 0.0000; implied y = 0 at row 489.50 against a detected baseline
of 488.5). T1–T5 were confirmed from the source text as 4, 8, 16, 24 and 36 h.

Validation against the values stated in the trial's own text **failed**: the
low-frequency TEAS arm reproduced to within 0.8% / −4.2% / −0.0%, but the control
arm was overestimated by +16.0% / +12.1% / +5.1%. A one-armed systematic error of
this size after an exact axis calibration indicates a figure-versus-text
inconsistency in the source, not an extraction fault. Gu 2019 is **not
admissible**; the extracted values are recorded for provenance only and are used
in no analysis. Author contact prepared.

## Defects found and fixed during execution

1. **Figures C and D were initially drawn with `meta forestplot`,** which treats
   each row as a study and redraws its interval as estimate ± 1.96·SE on a *z*
   scale. For a k = 4 Hartung–Knapp interval on t(3) that narrows the interval by
   roughly a factor of 1.6 — the plot rendered the primary result as
   −14.00 [−26.43, −1.56] and printed a pooled "p = 0.02" across three
   separately fitted models. Both panels are now drawn directly from the fitted
   `ci_low`/`ci_high` bounds, with no overall diamond and no pooled test.
2. **The master aggregate had silently drifted.** `master_reconciled_results_v26.csv`
   is read by the dashboard but written by no do-file. Its seven estimator-grid
   rows were still at k = 6 after the v32 migration moved the strict primary to
   k = 7, and its broader-SMD row was still at k = 10. `sync_master_results.py`
   now regenerates it from the Stata tables and fails on drift.
3. **Per-stratum denominators were wrong on the dashboard.** TEAS was quoted as
   N = 342 and EA as N = 334. Both are incorrect (337 and 339); they summed to
   the correct 676, which is why the existing total-denominator check passed. A
   reconciling total is not evidence that its parts reconcile.

## Dashboard changes

- New **"Which 0–24 Hour Evidence Can Actually Be Pooled"** panel on the Primary
  tab: tier ladder, analysis sets S0–S3, sensitivity analyses, empty-cell
  statements, withdrawals, and figures A–D. Rendered entirely from
  `tiered_v33.js`; no number is written into the markup.
- Coura 2011's and Sim 2002's body-weight reconstructions relabelled **"LEGACY
  RECONSTRUCTION — excluded from the current locked analysis"**, with the
  assumed 70 kg named as an assumption the trial never reports.
- Zhang 2025's derivation card relabelled **"WITHDRAWN IN v33"**.
- Chen 2015's Wan-transformation card relabelled **"TIER C — reported as a
  parallel synthesis, not converted for pooling"**, now showing the medians.
- Broader-SMD narrative corrected to k = 9 with the current estimate.
- Comparator-hierarchy caveat updated: the two strata are no longer combined
  into a single headline estimate.

## Validator

56 checks, all passing. Six are new and each was mutation-tested — a deliberate
corruption trips that check and only that check:

| Check | Mutation that trips it |
|---|---|
| v33 panel numbers match the Stata tiered results | Alter an estimate in `tiered_v33.js` |
| v33 comparator strata stay separate | Move a sham row into the usual-care stratum |
| v33 panel is generated from data | Hardcode `k = 4` into the markup |
| Zhang 2025 is withdrawn everywhere | Revert `broader_smd_k` to 10 |
| Body-weight reconstructions are labelled legacy | Remove the LEGACY label from the Coura card |
| Per-stratum denominators equal the summed arms | Restore N = 342 for TEAS |

## Conclusion unchanged

Two analyses cross p = 0.05 (the broader scale-free SMD at I² ≈ 95%, and the
primary model re-fitted with unadjusted Wald intervals). Neither changes the
review's conclusion, and neither is reported as a headline. Per the pre-specified
rule, these analyses exist to test robustness and completeness, not to find
significance.
