# Placeholder values in the secondary outcome register — 2026-09-10

Permanent remediation record. PROSPERO CRD420251090635.
Branch `claude/festive-jennings-0689c3`, base commit `c528f01`.

## What was wrong

Fifteen arm-bearing outcome records in `dashboard/data.js` held values that
appear in no source publication and in no locked dataset:

| Outcome | Records wrong | Records total |
|---|---|---|
| `intraop_opioid` | 7 | 7 |
| `flatus_time` | 5 | 6 |
| `rescue_analgesia` | 3 | 4 |

The signature was consistent: **the study skeleton was correct and the numbers
inside it were invented.** Arm sizes were right in 10 of the 15; units, study,
comparator and timepoint were right. Only the quantities were wrong, and they
were always plausible ones — which is why they survived review.

Two records also carried fabricated *provenance*. `Ng 2013` claimed
"Originally reported in days (1.33 ± 0.36 vs 1.34 ± 0.37 days); converted to
hours (×24)" — figures that appear nowhere in the paper, which reports
2.0 ± 0.9 vs 2.3 ± 1.1 days in 55 patients per arm. A fabricated note is more
dangerous than a bare wrong number because it reads as diligence.

## What was NOT affected

**No pooled estimate ever changed, and no published result was ever wrong.**

`dashboard/app.js` rebuilds `s.outcomes[key]` from the *generated*
`window.BROWSER_TARGETS` (and `window.PRIMARY_BROWSER`) at boot, so the Meta Lab
forest plots, the study modal and the CSV export all consumed the correct,
lock-derived values throughout. The contaminated numbers sat in the committed
register as a **latent hazard**, not a live error — they would have gone live the
moment that overwrite was relaxed.

Pooled estimates before and after remediation are identical:

| Outcome | k | Pooled estimate | 95% CI | I² |
|---|---|---|---|---|
| `opioid_24h` (**primary**) | 7 | −9.7261 mg MME | −19.02 to −0.4322 | 97.6% |
| `intraop_opioid` | 7 | −109.194 µg | −199.093 to −19.295 | 73.8% |
| `flatus_time` | 6 | −2.2667 h | −3.720 to −0.8134 | 23.4% |
| `rescue_analgesia` | 4 | RR 0.5047 | 0.3468 to 0.7345 | 0% |
| `opioid_48h` | 3 | −10.27 mg MME | −35.341 to 14.801 | 97.2% |
| `ponv_24h` | 2 | RR 0.5604 | 0.4291 to 0.7320 | 0% |

The primary outcome was verified 12/12 against the lock and is **unchanged**.

## Root cause

`scripts/validate_dashboard.py` described `dashboard/` as the "canonical,
hand-edited source". A hand-maintained file held a second copy of numbers the
locked datasets already owned, and nothing forced the two to agree. The lock
layers (v26 target CSVs, v34 master workbook) never disagreed with each other —
only the hand-maintained copy drifted.

## Remediation

1. **All 15 records verified against the source PDF**, not merely against the
   lock. In every case the lock was already correct. See `source_audit.csv`.
2. **`data.js` is now generated.** `scripts/sync_dashboard_outcomes.py` derives
   the outcome records from the same lock `browser_targets.js` is built from.
   `scripts/build_site.py` refuses to build if the two disagree.
3. **Direction is derived, never authored.** `favors` is computed from the sign
   of the observed effect. Liang 2021 shipped as intervention-favouring on a
   stored MD of −49 when its true effect is **+56.8 µg** — the source states
   intraoperative dosing did not differ between groups.
4. **Stale denominators removed.** `meta_engine.js` reads `arm1_total ?? arm1_n`;
   Tu 2024 carried `arm1_total: 77` against an analysed 57. Now lock-owned.
5. **Unit labels corrected.** Ng 2013's flatus record was labelled "days" while
   carrying hour values. Four non-pooled `opioid_24h` records were labelled
   "mg IV MME" while holding raw statistics (Jin 2023's 39.31 is *mL of PCIA
   solution*); they now carry the master's own unit and say they are not pooled.
6. **Validation generalised** to every outcome — see `scripts/validate_dashboard.py`
   section "outcome register integrity": lock-generation, effect recomputation
   from arms, direction, events ≤ denominator, unit consistency, banned
   placeholder values, and quarantine-registry honesty.
7. **17 mutation tests** in `scripts/mutation_test_outcomes.py`, covering the 12
   failure modes required by the remediation brief plus regressions for
   Liang 2021, Ng 2013, Tu 2024 and Zheng 2025.

## 48-hour ambiguities

- **Zhang 2023** — recoverable. Reported as median [IQR] (110.0 [80–110] vs
  110.0 [90–110] mg MME); the lock's values are the Wan et al. transformation,
  exact to the digit. The earlier "unverifiable" flag came from reading `mean_i`
  rather than the derived `mean_i_mme` column. **No change.**
- **Xie 2014** — not a value conflict. The two lock rows are two different
  comparators of a three-arm trial (EAS vs sham 133±7.0; EAS vs control
  134±5.9), both `include_strict=0`. `data.js` had presented one of them as a
  pooled 48 h record; that record is removed.

## Residual items

- **Resolved 2026-09-11.** All five out-of-pool `opioid_24h` records were checked
  against their source PDFs. Four are correct as recorded: Sim 2002
  (0.52 ± 0.19 mg/kg morphine at 24 h), Coura 2011 (13.1 ± 2.2 vs 16.3 ± 1.6
  µg/kg fentanyl, n = 13/9), Jin 2023 (39.31 mL PCIA solution) and Zhang 2025
  (50.53 ± 4.46 vs 53.79 ± 5.14 µg sufentanil, Table 4, P = 0.002).
  **Luo 2026 is mis-bucketed**: its 15.86 vs 15.18 "sufentanil equivalents (mg)"
  appears in the paper's BASELINE characteristics table beside sex, smoking and
  Apfel score with P = 0.27 — a baseline balance variable, not a 0–24 h
  postoperative outcome. It is now labelled as such; re-classifying it in the
  register is a review-team decision.

- **Resolved 2026-09-11.** Sim 2002 and Jin 2023 were recorded above as having
  "two master rows with different intervention means… the choice is unresolved".
  That framing was wrong. Both are three-arm trials with a shared control, and
  **both rows are correct**: Sim 2002 compares preoperative EA (0.52 ± 0.19) and
  postoperative EA (0.58 ± 0.27) against the same placebo-EA arm (0.68 ± 0.38);
  Jin 2023 compares 2-Hz EA (39.31) and 20/100-Hz EA (45.72) against the same
  sham (56.54). Pooling both against the shared control would need a
  shared-control adjustment; neither is currently pooled.

- **CORRECTION, 2026-09-11.** This report previously flagged Xiong 2021 as a
  data-quality concern — "BMI 39.1/39.9 with mean age 27.5/27.3 … but its
  surgery_procedure is the generic 'Elective surgical procedure under general
  anesthesia'". **That was my error.** The generic string sits in an unused
  `data.js` field that `dashboard/app.js` overwrites at boot from
  STUDY_CHARACTERISTICS; the procedure actually displayed is **"Laparoscopic
  sleeve gastrectomy"**, which explains a BMI of 39 at age 27 completely. Xiong
  2021 is not anomalous. The related claim that "seven studies share that generic
  procedure string" was measured against the same dead field; on screen only
  Wu 2016 was generic, and it now reads "Thoracotomy for lung cancer", recovered
  from its source PDF.

- Five `note` fields still state that values are figure-only, or a deliberately
  unconverted median/IQR (Wu 2016, Liu 2015, Zhang 2018 ×2, Gao 2022). These are
  honest non-extraction statements rather than numerical claims. Digitising them
  remains open.

- Zhang 2023's 48 h record now carries an interpretation caveat: its median
  equals Q3 in both arms, so the Wan et al. transformation's symmetry assumption
  is strained and the derived SD is likely understated. Values unchanged.

## Files

- `source_audit.csv` — machine-readable record of all 17 audited cells:
  old value, verified value, unit, analysed n, PDF, table/location, direct vs
  derived, derivation formula, date, status, reason.
