#!/usr/bin/env python3
"""
Build the Stata-ready v33 Tier E scale-free SMD dataset.

Tier E in PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv holds results that report
the exact 0-24 h cumulative postoperative opioid estimand as a mean/SD, but in
a unit that cannot be converted to absolute IV MME without an assumption this
review's protocol prohibits (an assumed body weight for a weight-normalized
dose, or an assumed drug concentration for a volume proxy). That blocks the
ABSOLUTE-MME estimand, not the WITHIN-STUDY standardized effect: a Hedges' g
(SMD) divides the between-arm difference by the pooled SD, so the unit cancels
and the same weight-normalized or volume-proxy value is usable there.

This file is the source of truth for which Tier E rows are actually admitted
to that SMD synthesis and why. Every value here is read from
PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv (itself PDF-verified per its own
OVERRIDES dict in build_derivability_audit.py) -- nothing is re-derived from
the source PDFs in this file; it only decides admission and performs the two
deterministic transforms the audit already flags as necessary (multi-arm
combining, and one explicitly-labelled median/IQR approximation).

ADMITTED (mean/SD, native units, no distributional assumption):
  Coura 2011                 EA   vs Sham/placebo  (ug/kg fentanyl)
  Sim 2002 (combined)        EA   vs Placebo       (mg/kg morphine) -- two
      correlated active arms (preop-EA, postop-EA) sharing one placebo control
      are combined into ONE contrast via the Cochrane Handbook 6.5.2.10
      "combining groups" formula, the same multi-arm discipline this review
      already applies to Chen 1998 / Szmit 2021 (count each trial once).
  Jin 2023 (combined)        EA   vs Sham          (mL PCIA solution proxy)
      -- same combining treatment for its two correlated frequency arms
      sharing one sham arm.
  Oztas 2019                 TEAS vs Usual care     (mg tramadol)

SENSITIVITY ONLY (median/IQR, Cochrane Handbook 6.5.2.5 approximation:
mean ~= median, SD ~= IQR / 1.35, assuming approximate symmetry -- distinct
from Gao 2022's Tier C case, which is NOT approximated anywhere in this
review because its 25th percentile is exactly 0 in both arms, a zero-inflated
distribution the same approximation would badly misrepresent):
  Chen 2015 (Hyperalgesia)   TEAS vs Sham          (ug/kg sufentanil)

EXCLUDED (a problem the SMD metric does not fix -- listed here, not silently
dropped, so the audit's full denominator stays visible):
  Zhang 2025      window mismatch (POD1 is not a 0-24 h clock window)
  Ntritsou 2014   wrong estimand (protocol-mandated background dosing included)
  Oztas 2019 combined-opioid row   unrecoverable combined-total variance
  Oztas 2019 TEAS-vs-TENS arm      comparator eligibility unresolved ("Check"
                                    in the audit) -- excluded pending a decision,
                                    not assumed either way
  Song 2020       assumption-dependent derivation (PCA presses != deliveries)

v32/the audit CSV remain read-only.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "07_TIERED_V33" / "01_DATA"
AUDIT = ROOT / "07_TIERED_V33" / "PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv"


def read_audit() -> dict[str, dict]:
    with AUDIT.open(encoding="utf-8-sig") as f:
        return {r["comparison_id"]: r for r in csv.DictReader(f)}


def f(row: dict, key: str) -> float:
    return float(row[key])


def combine_two_arms(n1, m1, sd1, n2, m2, sd2):
    """Cochrane Handbook 6.5.2.10: combine two correlated intervention groups
    that share one control, into a single group, before computing one
    pairwise contrast. Avoids double-counting the shared control (a
    unit-of-analysis error) and avoids arbitrarily discarding one arm."""
    n = n1 + n2
    m = (n1 * m1 + n2 * m2) / n
    var = ((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2 +
           (n1 * n2 / n) * (m1 - m2) ** 2) / (n - 1)
    return n, m, var ** 0.5


def hedges_g(n_i, mean_i, sd_i, n_c, mean_c, sd_c):
    s_pooled = (((n_i - 1) * sd_i ** 2 + (n_c - 1) * sd_c ** 2) / (n_i + n_c - 2)) ** 0.5
    d = (mean_i - mean_c) / s_pooled
    j = 1 - (3 / (4 * (n_i + n_c) - 9))
    g = d * j
    se = (((n_i + n_c) / (n_i * n_c)) + (g ** 2) / (2 * (n_i + n_c))) ** 0.5
    return round(g, 6), round(se, 6)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    a = read_audit()
    rows = []

    # -- Coura 2011: EA vs sham/placebo, native ug/kg fentanyl ----------------
    r = a["COURA11_EA_vs_SHAM"]
    n_i, sd_i, n_c, sd_c = int(f(r, "n_intervention")), f(r, "variance_intervention"), \
        int(f(r, "n_comparator")), f(r, "variance_comparator")
    mean_i, mean_c = f(r, "value_intervention"), f(r, "value_comparator")
    g, se = hedges_g(n_i, mean_i, sd_i, n_c, mean_c, sd_c)
    rows.append(dict(
        study="Coura 2011", year=2011, comparison_id="COURA11_EA_vs_SHAM_SMD",
        modality="EA", comparator="Sham/placebo", stratum="ea_sham",
        n_i=n_i, n_c=n_c, mean_i_src=mean_i, sd_i_src=sd_i, mean_c_src=mean_c, sd_c_src=sd_c,
        unit_src="ug/kg fentanyl", combine_note="",
        hedges_g=g, hedges_se=se, sensitivity_only=0,
        multiarm_note="",
        caveat="Supplementary morphine/fentanyl was permitted per-protocol, so reported "
               "fentanyl is not complete opioid exposure; weight-normalized (no sourced "
               "absolute-MME factor) -- admissible on SMD only.",
        source_locator="covidence_819_full_article.pdf: Table 2, 13.1+/-2.2 vs 16.3+/-1.6 ug/kg",
    ))

    # -- Sim 2002: two correlated EA-timing arms, one shared placebo ----------
    pre = a["SIM02_PREOP_vs_PLACEBO_MORPH24"]
    post = a["SIM02_POSTOP_vs_PLACEBO_MORPH24"]
    n1, m1, sd1 = int(f(pre, "n_intervention")), f(pre, "value_intervention"), f(pre, "variance_intervention")
    n2, m2, sd2 = int(f(post, "n_intervention")), f(post, "value_intervention"), f(post, "variance_intervention")
    n_c, mean_c, sd_c = int(f(pre, "n_comparator")), f(pre, "value_comparator"), f(pre, "variance_comparator")
    n_comb, m_comb, sd_comb = combine_two_arms(n1, m1, sd1, n2, m2, sd2)
    g, se = hedges_g(n_comb, m_comb, sd_comb, n_c, mean_c, sd_c)
    rows.append(dict(
        study="Sim 2002 (preop + postop EA combined)", year=2002,
        comparison_id="SIM02_COMBINED_EA_vs_PLACEBO_SMD",
        modality="EA", comparator="Placebo EA", stratum="ea_sham",
        n_i=round(n_comb, 4), n_c=n_c,
        mean_i_src=round(m_comb, 6), sd_i_src=round(sd_comb, 6),
        mean_c_src=mean_c, sd_c_src=sd_c,
        unit_src="mg/kg morphine",
        combine_note=f"Combined via Cochrane Handbook 6.5.2.10 from preop-EA "
                     f"(n={n1}, {m1}+/-{sd1}) and postop-EA (n={n2}, {m2}+/-{sd2}), "
                     f"both vs the same placebo arm (n={n_c}, {mean_c}+/-{sd_c}).",
        hedges_g=g, hedges_se=se, sensitivity_only=0,
        multiarm_note="Two correlated active arms sharing one placebo control; combined "
                      "into one contrast per Cochrane Handbook 6.5.2.10, never pooled as "
                      "two independent studies.",
        caveat="Weight-normalized (mg/kg); absolute-dose reconstruction via an assumed "
               "body weight is prohibited -- admissible on SMD only.",
        source_locator="v32 Opioid_24h_Candidates (mg/kg morphine, 0-24 h); PDF not "
                       "re-verified this pass",
    ))

    # -- Jin 2023: two correlated frequency arms, one shared sham -------------
    a2 = a["JIN23_2HZ_vs_SHAM_VOL24"]
    a3 = a["JIN23_20100_vs_SHAM_VOL24"]
    n1, m1, sd1 = int(f(a2, "n_intervention")), f(a2, "value_intervention"), f(a2, "variance_intervention")
    n2, m2, sd2 = int(f(a3, "n_intervention")), f(a3, "value_intervention"), f(a3, "variance_intervention")
    n_c, mean_c, sd_c = int(f(a2, "n_comparator")), f(a2, "value_comparator"), f(a2, "variance_comparator")
    n_comb, m_comb, sd_comb = combine_two_arms(n1, m1, sd1, n2, m2, sd2)
    g, se = hedges_g(n_comb, m_comb, sd_comb, n_c, mean_c, sd_c)
    rows.append(dict(
        study="Jin 2023 (2Hz + 20/100Hz combined)", year=2023,
        comparison_id="JIN23_COMBINED_EA_vs_SHAM_SMD",
        modality="EA", comparator="Sham nonpenetrating EA/no current", stratum="teas_sham",
        n_i=round(n_comb, 4), n_c=n_c,
        mean_i_src=round(m_comb, 6), sd_i_src=round(sd_comb, 6),
        mean_c_src=mean_c, sd_c_src=sd_c,
        unit_src="mL PCIA solution (proxy)",
        combine_note=f"Combined via Cochrane Handbook 6.5.2.10 from the 2Hz arm "
                     f"(n={n1}, {m1}+/-{sd1}) and the 20/100Hz arm (n={n2}, {m2}+/-{sd2}), "
                     f"both vs the same sham arm (n={n_c}, {mean_c}+/-{sd_c}).",
        hedges_g=g, hedges_se=se, sensitivity_only=0,
        multiarm_note="Two correlated frequency arms sharing one sham arm; combined into "
                      "one contrast per Cochrane Handbook 6.5.2.10.",
        caveat="No sourced solution concentration, so absolute fentanyl mass is not "
               "recoverable; the unknown concentration is a common constant for both arms "
               "and cancels in a standardized effect -- admissible on SMD only. Modality is "
               "labelled EA in the audit (electroacupuncture); this row is placed in the "
               "'teas_sham' stratum here as the only sham-controlled EA-family SMD candidate "
               "outside the ea_sham (placebo) stratum built from Sim 2002/Coura 2011 -- see "
               "the generator's stratum notes.",
        source_locator="v32 Opioid_24h_Candidates; concentration absent from main article "
                       "per v32 QC",
    ))

    # -- Oztas 2019: TEAS vs usual care, native mg tramadol -------------------
    r = a["OZT19_TAES_vs_CTRL_TRAM24"]
    n_i, sd_i = int(f(r, "n_intervention")), f(r, "variance_intervention")
    n_c, sd_c = int(f(r, "n_comparator")), f(r, "variance_comparator")
    mean_i, mean_c = f(r, "value_intervention"), f(r, "value_comparator")
    g, se = hedges_g(n_i, mean_i, sd_i, n_c, mean_c, sd_c)
    rows.append(dict(
        study="Oztas 2019", year=2019, comparison_id="OZT19_TEAS_vs_UC_SMD",
        modality="TEAS", comparator="Usual care", stratum="teas_usual",
        n_i=n_i, n_c=n_c, mean_i_src=mean_i, sd_i_src=sd_i, mean_c_src=mean_c, sd_c_src=sd_c,
        unit_src="mg tramadol", combine_note="",
        hedges_g=g, hedges_se=se, sensitivity_only=0,
        multiarm_note="",
        caveat="Tramadol alone is not complete opioid exposure (rescue pethidine was also "
               "given, reported separately and not combinable -- see the excluded "
               "OZT19_TAES_vs_CTRL_TOTALOP24 row); no sourced tramadol:morphine IV MME "
               "factor exists in this review's reference tables -- admissible on SMD only. "
               "Overall RoB 2 for this study is High. Only comparison in this review's "
               "TEAS-vs-usual-care stratum: k=1, cannot be pooled.",
        source_locator="covidence_505_full_article.pdf: Tramadol HCl (0-24 h) "
                       "228.40+/-87.89 (TEAS) vs 357.81+/-123.70 (control) mg",
    ))

    # -- Chen 2015 (Hyperalgesia): median/IQR, SENSITIVITY ONLY ---------------
    r = a["CHEN15H_TEAS_vs_SHAM_SUFKG24"]
    n_i, n_c = int(f(r, "n_intervention")), int(f(r, "n_comparator"))
    # variance_intervention/comparator hold the IQR bounds as "lo–hi" text for
    # this one median/IQR row (every other row above is Mean/SD, a plain
    # number) -- parse the bounds and the median from the audit's own fields.
    med_i = f(r, "value_intervention")
    q_lo_i, q_hi_i = (float(x) for x in r["variance_intervention"].split("–"))
    med_c = f(r, "value_comparator")
    q_lo_c, q_hi_c = (float(x) for x in r["variance_comparator"].split("–"))
    mean_i_approx, sd_i_approx = med_i, (q_hi_i - q_lo_i) / 1.35
    mean_c_approx, sd_c_approx = med_c, (q_hi_c - q_lo_c) / 1.35
    g, se = hedges_g(n_i, mean_i_approx, sd_i_approx, n_c, mean_c_approx, sd_c_approx)
    rows.append(dict(
        study="Chen 2015 (Hyperalgesia)", year=2015,
        comparison_id="CHEN15H_TEAS_vs_SHAM_SMD_APPROX",
        modality="TEAS", comparator="Electrodes/no-current sham", stratum="teas_sham",
        n_i=n_i, n_c=n_c,
        mean_i_src=round(mean_i_approx, 6), sd_i_src=round(sd_i_approx, 6),
        mean_c_src=round(mean_c_approx, 6), sd_c_src=round(sd_c_approx, 6),
        unit_src="ug/kg sufentanil (median/IQR, Cochrane 6.5.2.5-approximated to mean/SD)",
        combine_note=f"Approximated from published median (IQR): intervention "
                     f"{med_i} ({q_lo_i}-{q_hi_i}), comparator {med_c} ({q_lo_c}-{q_hi_c}), "
                     f"via mean~=median and SD~=IQR/1.35 (Cochrane Handbook 6.5.2.5, assumes "
                     f"approximate symmetry). NOT the same case as Gao 2022 (Tier C): that "
                     f"distribution's 25th percentile is exactly 0 in both arms (zero-"
                     f"inflated), which this review has already ruled makes the same "
                     f"approximation indefensible; Chen 2015 (Hyperalgesia)'s IQR bounds are "
                     f"both strictly positive.",
        hedges_g=g, hedges_se=se, sensitivity_only=1,
        multiarm_note="",
        caveat="SENSITIVITY ONLY: median/IQR approximated to mean/SD, not a native mean/SD "
               "value like every other row in this file. Reported alongside, never silently "
               "merged into, the main Tier E SMD estimate.",
        source_locator="040_chen_2015_hyperalgesia_lund.pdf: T5 = 24 h after surgery",
    ))

    cols = list(rows[0].keys())
    p = OUT / "tiered_tierE_smd_v33.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for x in rows:
            w.writerow(x)
    print(f"wrote {p}  ({len(rows)} rows)")
    print("\nstrata:")
    print("  ea_sham (Coura 2011, Sim 2002 combined) ...... k=2, poolable")
    print("  teas_sham main (Jin 2023 combined) ............ k=1, standalone")
    print("  teas_sham sensitivity (+ Chen 2015 Hyperalgesia) k=2, poolable, sensitivity-only")
    print("  teas_usual (Oztas 2019) ........................ k=1, standalone")
    print("\nexcluded (audit rows NOT admitted here, unrelated to reporting format):")
    print("  Zhang 2025      window mismatch")
    print("  Ntritsou 2014   wrong estimand")
    print("  Oztas 2019 combined-opioid row   unrecoverable variance")
    print("  Oztas 2019 TEAS-vs-TENS arm      unresolved eligibility (audit: 'Check')")
    print("  Song 2020       assumption-dependent derivation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
