# V33 Analysis Changelog

Perioperative TEAS & EA systematic review · PROSPERO CRD420251090635
Date: 2026-09-08
Authoritative engine: **StataNow 19.5**

---

## 1. Pipeline repointed to v33

| File | Change |
|---|---|
| `06_FINAL_ANALYSIS_V26/02_STATA/00_prep_data.do` | `master_xlsx` now resolves to `TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx` |
| `scripts/build_site.py` | Master reference and `master_version` → v33; outcome-row count now derived from `Outcome_Data`, not the Summary cell |
| `scripts/build_primary_pathway.py` | Provenance → v33 |
| `scripts/validate_dashboard.py` | Provenance → v33 |
| `07_TIERED_V33/build_derivability_audit.py` | Provenance → v33 |

**All analyses were re-run from scratch.** No numerical result was carried over
from the previous dashboard or reused from a cached file.

---

## 2. Primary outcome — unchanged, as required

The strict primary model was re-fitted from the v33 master and is numerically
identical to the v32 run:

| Analysis | k | Estimate (mg IV MME) | 95% KH CI | p | I² |
|---|---:|---:|---|---:|---:|
| `OP24_PRIM_COMB` | 7 | −9.90700 | −20.0794 to +0.2654 | 0.0545 | 98.57% |
| `OP24_TEAS_SHAM` | 4 | −13.99527 | −34.1808 to +6.1903 | 0.1145 | 98.59% |
| `OP24_EA_CTRL` | 3 | −3.93583 | −19.7732 to +11.9016 | 0.3969 | 77.15% |
| `OP24_LOWROB_ONLY` | 6 | −11.27296 | −23.1816 to +0.6357 | 0.0591 | — |
| `OP24_PRIM_SMD` | 7 | −0.96675 | −2.0862 to +0.1527 | 0.0790 | 96.50% |

Strict primary **k = 7** — the assertion held, so no adjudication STOP was
raised. All v33 additions were correctly ineligible for this estimand.

The v33 tiered architecture (S0 primary = TEAS vs sham k = 4; EA vs usual care
k = 3 supportive) is unchanged and was re-fitted on the v33 master with
identical results.

---

## 3. New and expanded secondary analyses

Fitted by `08_V33_MASTER/02_STATA/20_v33_secondary.do`, random-effects REML with
Hartung–Knapp intervals.

| Analysis | k | Measure | Estimate | 95% CI | p | I² |
|---|---:|---|---:|---|---:|---:|
| Binary rescue opioid use, 0–24 h / POD1 | 3 | Risk ratio | 0.519 | 0.370 to 0.727 | 0.014 | 0.0% |
| Intraoperative remifentanil | 9 | MD (µg) | −104.42 | −158.55 to −50.28 | 0.002 | 52.6% |
| Intraoperative remifentanil | 9 | Hedges' g | −0.486 | −0.836 to −0.136 | 0.013 | 81.6% |
| Intraoperative sufentanil | 6 | MD (µg) | −0.114 | −1.935 to +1.707 | 0.879 | 26.8% |
| Global QoR-40 at ~24 h | 3 | MD (points) | +7.34 | −4.60 to +19.28 | 0.118 | 82.5% |
| Time to first defecation | 8 | MD (hours) | −10.31 | −18.45 to −2.18 | 0.020 | 88.6% |

### What the supplement enabled

- **Binary rescue opioid use is a new analysis.** It exists only because
  Yu 2020's 13/30 vs 24/30 was added. Without it, k = 2.
- **Intraoperative remifentanil grew** from 7 to 9 contrasts (Pan 2023 and
  Zhu 2022 added).
- **Intraoperative sufentanil grew** to 6 contrasts (Zhu 2022 added).
- **QoR-40 grew** from 2 to 3 contrasts (Liang 2021 added).
- **Time to first defecation grew** to 8 contrasts (Yang 2020 added).

### Fragility of the new rescue-opioid result

The rescue-opioid RR is nominally significant with I² = 0%, but **Yu 2020
carries 80.8% of the weight**, and leave-one-out shows the result does not
survive omission of either of the two larger contributors:

| Omitted | RR | 95% CI | p |
|---|---:|---|---:|
| Tu 2024 | 0.520 | 0.119 to 2.268 | 0.112 |
| Liu 2026 (burn) | 0.538 | 0.424 to 0.684 | 0.019 |
| Yu 2020 | 0.433 | 0.063 to 2.995 | 0.114 |

This is reported as a hypothesis-generating secondary result, not as evidence of
opioid sparing. A k = 3 model in which one newly added trial supplies four
fifths of the weight is not a robust finding, and the I² of 0% reflects three
similar point estimates rather than a well-estimated between-study variance.

### Time to first defecation is not driven by the new study

Excluding the newly added Yang 2020 contrast gives −11.95 h (−21.52 to −2.38),
p = 0.022, k = 7 — the effect was already present and the addition did not
create it.

---

## 4. Estimand separation enforced

The following were kept in separate models and never pooled with one another:

- binary rescue opioid **use** vs opioid **dose**
- rescue administration **counts** vs opioid dose (and counts in different
  units — Yao 2015 administrations vs Chen 2015 boluses — not pooled with
  each other either)
- **intraoperative** opioid requirement vs **postoperative** consumption
- PCA presses / attempts / deliveries vs drug consumption
- opioid rescue vs **non-opioid** rescue (flurbiprofen, dexketoprofen,
  ketorolac, metoclopramide)
- QoR-40 vs QoR-15 (different instruments)

Unit harmonisation was limited to exact same-drug rescaling (mg → µg, ×1000).
**No equianalgesic MME conversion was applied to any intraoperative outcome**,
because the review's sourced MME factors are defined for the postoperative
estimand.

The complete not-pooled register (11 entries, each with its reason) is published
at `08_V33_MASTER/01_DATA/v33_not_pooled_register.csv` and rendered on the
dashboard.

---

## 5. Multi-arm handling

| Trial | Arms | Contrast used | Rationale |
|---|---|---|---|
| Zhu 2022 | 3 active vs 1 shared usual care (n=101) | Combined EA (day before + 30 min) | Most-intensive active arm, chosen a priori; the other two are dropped so the shared control is not counted three times |
| Lu 2021 | 2 active vs 1 shared sham | Combined PC6+CV17 TEAS | Same rule |
| Wang 2024 | 2 strata (SNVP, MNVP) | Both retained | Different patients with their own control arms — independent contrasts, not a shared control |

The choice is recorded in `MULTIARM_PICK` in `build_v33_analysis_sets.py` so it
is auditable rather than implicit.

---

## 6. Analyses deliberately not run

- **Meta-regression** on the new secondary outcomes. At k = 3–9 no covariate
  meets the Cochrane 10:1 guidance; running one because a variable exists would
  be an underpowered fishing exercise.
- **Prediction intervals at k = 3** (rescue opioid, QoR-40). τ² is too poorly
  estimated at k = 3 for the interval to carry meaning.
- **Funnel plots / small-study tests** on any new analysis. All have k < 10.

---

## 7. Holds respected

- **Yeh 2010 / Yeh 2011 publication family** — still one unresolved study unit;
  no v33 change.
- **Zhang 2025** — remains excluded from all 0–24 h analyses (POD1 ≠ clock
  window), including the scale-free broader SMD (k = 9).
- **Gu 2019** — digitization remains rejected; still graph-only.
- All source-QC holds carried forward from v32 are unchanged.
