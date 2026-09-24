# E2 results — post-hoc sensitivity analysis (E1 retained as primary)

**Status: post-hoc sensitivity analysis.** After this run, the review author retained the registered outcome (E1) as primary (decision recorded in `02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md`).

**Run 23 September 2026**, after the E2 definition (commit `95fcf66`) and Amendment
E2.1 with the full classification (commit `9fa94d6`) were fixed. Produced by
`run_e2.py`. **No canonical output was modified**; these results sit alongside
v38.

## Validation

The E2 script uses the estimator copied verbatim from `code/fit_models.py` and
the arm-combination logic from `code/build_results.py`. Before reporting anything
new, it reproduces four canonical v38 models exactly:

| Canonical model | v38 | E2 code | Max difference |
|---|---:|---:|---:|
| opioid24_TEAS_sham | −7.700000 | −7.700000 | 0 |
| opioid24_TEAS_sham_expanded_suf0.5 | −9.763694 | −9.763694 | 0 |
| opioid24_EA_usual | −6.831993 | −6.831993 | 0 |
| opioid24_EA_usual_expanded | −3.935834 | −3.935834 | 0 |

## E2 main analysis, alongside the registered primary E1 (mg IV MME, sufentanil 0.5 mg/µg)

| Body | E1 k (N) | E1 MD (95% CI) | **E2 k (N)** | **E2 MD (95% CI)** | E2 I² | E2 95% PI |
|---|---|---|---|---|---:|---|
| TEAS vs sham | 1 (48) | −7.70 (−10.62, −4.78) | **7 (581)** | **−6.17 (−12.47, 0.14)** | 98.0% | −22.12, 9.78 |
| TEAS vs usual care | 1 (47) | −8.00 (−10.92, −5.08) | 1 (47) | −8.00 (−10.92, −5.08) | — | — |
| EA vs sham | 0 | no eligible data | **1 (75)** | **−11.80 (−18.52, −5.08)** | — | — |
| EA vs usual care | 2 (159) | −6.83 (−76.39, 62.73) | **4 (414)** | **−8.14 (−23.06, 6.77)** | 90.4% | not shown (k<5) |

## TEAS vs sham — sensitivity analyses

| Analysis | k | MD (95% CI) |
|---|---:|---|
| **E2 main** | 7 | **−6.17 (−12.47, 0.14)** |
| Sufentanil 0.25 | 7 | −4.27 (−9.14, 0.60) |
| Sufentanil 1.0 | 7 | −9.24 (−18.97, 0.49) |
| Without E2.1 admissions (Zhang 2025, Gu 2019) | 5 | −8.43 (−17.78, 0.91) |
| Leave out Gu 2019 (figure–text contradiction) | 6 | −7.11 (−14.68, 0.46) |
| Leave out Lee 2011 (Table 8 contradiction) | 6 | −6.67 (−14.53, 1.18) |
| Without known unquantified rescue (Chen 1998, Lee 2011) | 5 | −5.07 (−12.23, 2.10) |
| Without unstated-route equivalents (He 2026) | 6 | −7.25 (−14.58, 0.08) |
| Restricted to E1-eligible (= registered primary) | 1 | −7.70 (−10.62, −4.78) |
| Leave-one-out, range | 6 | −3.92 (without Chen 2020) to −7.25 (without He 2026) |

**Every E2 TEAS-versus-sham analysis crosses zero, and none reaches −10 mg.** The
most favourable, sufentanil at 1.0 mg/µg, gives −9.24 (−18.97, 0.49).

## EA vs usual care — sensitivity analyses

| Analysis | k | MD (95% CI) |
|---|---:|---|
| **E2 main** | 4 | **−8.14 (−23.06, 6.77)** |
| Leave out El-Rakshy 2009 | 3 | −10.35 (−35.85, 15.14) |
| Without known unquantified rescue (= E1 body) | 2 | −6.83 (−76.39, 62.73) |
| Leave-one-out, range | 3 | −3.94 to −11.26 |

## Joint criterion (≥10 mg sparing and paired pain upper 95% limit < +1)

| Body | Opioid limb | Pain limb | Joint criterion |
|---|---|---|---|
| TEAS vs sham | Not met (−6.17) | — | **Not met** |
| TEAS vs usual care | Not met (−8.00) | — | **Not met** |
| **EA vs sham** | **Met by point estimate (−11.80), k = 1** | **Cannot be evaluated:** Lin 2002 reports pain only in a figure (Fig. 1), and it has no eligible ~24-h pain result. Pain from other trials cannot supply the pairing (Methods). | **Cannot be evaluated** |
| EA vs usual care | Not met (−8.14) | — | **Not met** |

EA versus sham rests on one 2002 trial at high risk of bias. It was admitted on a
boundary reading of DP1, with PCA starting at hour 1, and on DP4, with IM
pethidine first-hour rescue that was unfactored and unquantified. **Digitising
Lin 2002's Fig. 1 to supply the pain limb would extend Amendment E2.1 to the pain
outcome after the opioid limb is known to pass. It has not been done**, and would
be a further post-hoc decision.

## Not yet done

- GRADE for the E2 bodies.
- Additional file 12 updated for E2.
- PROSPERO revision text, the manuscript "Changes from the protocol" section, and
  Results, Abstract and Discussion.
