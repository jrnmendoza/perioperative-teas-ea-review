# Stata reproduction and reconciliation

Software: StataNow/SE 19.5 (revision 12 Aug 2026), Unix Mac (Apple Silicon). Official `meta` suite only; no community packages. Do-files: `13_STATA/do/`; run with `sh 10_FINAL_ADJUDICATION/13_STATA/run_stata.sh` from the repository root.

## Specification reproduced

- Effect sizes computed in Stata from arm-level canonical data with `meta esize`: MD `esize(mdiff, unequal)`, SMD `esize(hedgesg, exact)`, RR `esize(lnrratio)`. All 327 study rows equal the canonical yi to ≤3e-14 and SE to ≤6e-16 (after the SMD variance convention below).

- k ≥ 2: `meta set ..., random(reml)` then `meta summarize, se(khartung, truncated)`, i.e. REML τ² with the truncated (safeguarded) Knapp–Hartung SE, max(1, q). k = 1: single-study normal 95% CI, not pooled. k = 0: no model.

## Result

117 models (core 74, E2 25, QoR ~24 h 12, QoR later 6):

- **NO ELIGIBLE DATA**: 5
- **STATA VERIFIED**: 64
- **STATA VERIFIED (single study, not pooled)**: 48

Largest relative difference among verified models: 9e-07. Tolerances: estimate, SE, CI, τ², q 1e-6 and I² 1e-4 (scaled by max(1, |value|)); k and N exact.

R/metafor (existing reproduction runs): agrees 87, not run 30. No metafor run exists for E2; E2 is checked against its own canonical code and now Stata.

## Discrepancies

None: every model with data reproduces within tolerance.

## Convention differences (documented, not errors)

1. **Prediction interval degrees of freedom.** Stata's `predinterval` uses t with k−2 df (Higgins et al. 2009). The canonical pipeline and metafor use t with k−1 df and report PIs only when k ≥ 5. The Stata layer computes the canonical-convention PI explicitly (θ ± t(k−1) √(τ² + SE²)) and it matches in every model with a canonical PI; Stata's native PI is listed for 51 models in `stata_verification_summary.csv` for reference.

2. **SMD variance.** Stata's `hedgesg` SE is J × SE(d); the canonical pipeline and metafor use the Hedges–Olkin large-sample variance (n₁+n₂)/(n₁n₂) + g²/(2(n₁+n₂)). The Stata layer uses the canonical formula (the estimates themselves are identical). With Stata's default SE the 2 SMD sensitivity models would read: flatus_TEAS_sham_SMD_sensitivity -0.3698; flatus_EA_usual_SMD_sensitivity -0.4877 (canonical: -0.3692; -0.4871).

3. **REML convergence at the τ² = 0 boundary (investigated).** With Stata's default maximisation tolerances, seven models first differed by up to 5e-6: six whose canonical REML optimum is the boundary τ² = 0 (Stata stopped at τ² ≈ 1e-7, I² ≈ 0.001%) and one E2 leave-one-out with τ² 13.46598 vs 13.46596. Tightening `tolerance()` and `nrtolerance()` to 1e-14 moves Stata to the same optimum (τ² ≈ 1e-15 at the boundary); the do-file uses these tolerances. This was an optimiser stopping rule, not a specification difference; no canonical value changed.

4. **Knapp–Hartung truncation.** Stata's `se(khartung, truncated)` is the same safeguard as the canonical max(1, q); the untruncated `se(khartung)` gives narrower intervals when q < 1 and is not used.

## Files

- `output/stata_model_results.csv`: Stata estimates for all models.
- `output/stata_effect_size_check.csv`: row-level effect-size check.

- `output/stata_canonical_comparison.csv`: every compared field with canonical, Stata and metafor values.
- `output/stata_verification_summary.csv`: one status per model.
