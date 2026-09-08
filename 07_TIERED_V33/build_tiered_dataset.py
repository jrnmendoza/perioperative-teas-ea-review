#!/usr/bin/env python3
"""
Build the Stata-ready v33 tiered analysis dataset.

Every row carries its source value, unit, sourced conversion factor, tier, and
comparator/modality stratum, so any pooled estimate can be traced back to the
source PDF without leaving this file.

v32 remains read-only.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "07_TIERED_V33" / "01_DATA"

# IV MME conversion factors, all sourced (BC Ministry of Health palliative
# equianalgesic table; FDA/Pfizer sufentanil label). See
# 06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv
F_MORPHINE = 1.0
F_HYDROMORPHONE = 5.0
F_SUFENTANIL = 1.0      # mg MME per ug (1000:1)

# ---------------------------------------------------------------------------
# TIER A -- exact 0-24 h cumulative postoperative opioid, mean/SD,
# sourced absolute IV MME conversion. Multi-arm trials contribute ONE contrast.
# ---------------------------------------------------------------------------
TIER_A = [
    dict(study="Chen 1998", year=1998, modality="TEAS", comparator="Sham",
         comparison_id="CHEN98_ACU_vs_SHAM",
         n_i=25, n_c=25, mean_i=6.5, sd_i=3.5, mean_c=10.7, sd_c=5.0,
         unit="mg hydromorphone", factor=F_HYDROMORPHONE,
         multiarm="4-arm; acupoint contrast only; shares one sham arm with the "
                  "dermatomal and non-acupoint contrasts",
         source="covidence_969_chen_1998.pdf; v32 Opioid_24h_Candidates"),
    dict(study="Chen 2020", year=2020, modality="TEAS", comparator="Sham",
         comparison_id="CHEN20_TEAS_vs_SHAM",
         n_i=40, n_c=40, mean_i=72.43, sd_i=4.78, mean_c=100.62, sd_c=10.2,
         unit="ug sufentanil", factor=F_SUFENTANIL, multiarm="",
         source="Thoracic Cancer 2020 Chen; v32 Opioid_24h_Candidates"),
    dict(study="He 2026 (hepatectomy/JIS)", year=2026, modality="TEAS", comparator="Sham",
         comparison_id="HEJIS26_TEAS_vs_CTRL_MME24",
         n_i=80, n_c=79, mean_i=20.0, sd_i=2.5, mean_c=20.6, sd_c=4.5,
         unit="mg MME", factor=1.0, multiarm="",
         source="J Invest Surg 2026 eTable 1 (reports MME directly)"),
    dict(study="Szmit 2021", year=2021, modality="TEAS", comparator="Sham",
         comparison_id="SZMIT21_TEAS_vs_SHAM_MORPH24",
         n_i=24, n_c=24, mean_i=7.5, sd_i=3.8, mean_c=15.2, sd_c=6.24,
         unit="mg IV morphine", factor=F_MORPHINE,
         multiarm="3-arm; sham contrast used; PCA-only arm is the correlated alternative",
         source="pdf-3.pdf (J Clin Med 2021;10:146)"),
    dict(study="El-Rakshy 2009", year=2009, modality="EA", comparator="Usual Care",
         comparison_id="ELR09_EA_vs_CTRL_MORPH24",
         n_i=42, n_c=53, mean_i=35.3, sd_i=18.0, mean_c=36.9, sd_c=18.0,
         unit="mg IV morphine", factor=F_MORPHINE, multiarm="",
         source="Acupunct Med 2009; Table 2 (n=42/53)"),
    dict(study="Seevaunnamtum 2016", year=2016, modality="EA", comparator="Usual Care",
         comparison_id="SEEVA16_EA_vs_UC",
         n_i=32, n_c=32, mean_i=21.38, sd_i=14.38, mean_c=33.94, sd_c=20.24,
         unit="mg morphine", factor=F_MORPHINE, multiarm="",
         source="Anesth Pain Med 2016;6(6):e40106"),
    dict(study="Yang 2024", year=2024, modality="EA", comparator="Usual Care",
         comparison_id="YANG24_EA_vs_UC_MORPH24",
         n_i=90, n_c=90, mean_i=43.7, sd_i=4.7, mean_c=44.0, sd_c=4.9,
         unit="mg morphine", factor=F_MORPHINE, multiarm="",
         source="Explore (NY) 2024;20(3):450-455"),
]

# Correlated alternative contrasts from already-counted multi-arm trials.
# Used ONLY in the comparator-sensitivity analysis, never alongside their
# sibling contrast.
MULTIARM_ALT = [
    dict(study="Szmit 2021 (PCA-only arm)", year=2021, modality="TEAS", comparator="Usual Care",
         comparison_id="SZMIT21_TEAS_vs_CTRL_MORPH24",
         n_i=24, n_c=23, mean_i=7.5, sd_i=3.8, mean_c=15.5, sd_c=6.1,
         unit="mg IV morphine", factor=F_MORPHINE,
         multiarm="correlated with SZMIT21_TEAS_vs_SHAM_MORPH24 - never pool both",
         source="pdf-3.pdf (J Clin Med 2021;10:146)"),
]

# ---------------------------------------------------------------------------
# TIER C -- exact estimand, alternative distributional form (median/IQR).
# Reported as a PARALLEL synthesis. Never converted to mean/SD.
# ---------------------------------------------------------------------------
TIER_C = [
    dict(study="Gao 2022", year=2022, modality="TEAS", comparator="Sham",
         comparison_id="GAO22_TEAS_vs_SHAM_SUFPUMP24",
         n_i=827, n_c=828,
         median_i=33.0, q1_i=0.0, q3_i=50.0,
         median_c=30.0, q1_c=0.0, q3_c=60.0,
         unit="ug sufentanil", factor=F_SUFENTANIL, reported_p="0.197",
         note="25th percentile is exactly 0.0 in BOTH arms: zero-inflated, strongly "
              "non-normal. Wan/Luo mean-SD recovery is not defensible here.",
         source="pdf-2.pdf Table: '24 h analgesic pump, ug 33.0 (0.0, 50.0) vs 30.0 (0.0, 60.0)'"),
    dict(study="Chen 2015", year=2015, modality="TEAS", comparator="Sham",
         comparison_id="CHEN15Q_TEAS_vs_CTRL_RESCUEMORPH24",
         n_i=41, n_c=42,
         median_i=2.0, q1_i=2.0, q3_i=6.0,
         median_c=7.0, q1_c=4.0, q3_c=14.0,
         unit="mg IV morphine", factor=F_MORPHINE, reported_p="0.004",
         note="Tier B derivation: rescue count x fixed 2 mg IV morphine. Multiplication by a "
              "positive constant is order-preserving, so quantiles transform exactly. "
              "Rescue morphine was the only postoperative opioid.",
         source="037_chen_2015_thyroidectomy_lund.pdf: counts 1 (1-3) vs 3.5 (2-7) x 2 mg"),
]


def mme(v, f):
    return round(v * f, 6)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for r in TIER_A + MULTIARM_ALT:
        mi, si = mme(r["mean_i"], r["factor"]), mme(r["sd_i"], r["factor"])
        mc, sc = mme(r["mean_c"], r["factor"]), mme(r["sd_c"], r["factor"])
        md = round(mi - mc, 6)
        se = round(((si ** 2) / r["n_i"] + (sc ** 2) / r["n_c"]) ** 0.5, 6)
        sp = (((r["n_i"] - 1) * si ** 2 + (r["n_c"] - 1) * sc ** 2) /
              (r["n_i"] + r["n_c"] - 2)) ** 0.5
        d = (mi - mc) / sp
        J = 1 - (3 / (4 * (r["n_i"] + r["n_c"]) - 9))
        gg = d * J
        gse = (((r["n_i"] + r["n_c"]) / (r["n_i"] * r["n_c"])) +
               (gg ** 2) / (2 * (r["n_i"] + r["n_c"])))** 0.5
        is_alt = r in MULTIARM_ALT
        rows.append(dict(
            study=r["study"], year=r["year"], comparison_id=r["comparison_id"],
            modality=r["modality"], comparator=r["comparator"], tier="A",
            n_i=r["n_i"], n_c=r["n_c"],
            mean_i_src=r["mean_i"], sd_i_src=r["sd_i"],
            mean_c_src=r["mean_c"], sd_c_src=r["sd_c"],
            unit_src=r["unit"], mme_factor=r["factor"],
            mean_i_mme=mi, sd_i_mme=si, mean_c_mme=mc, sd_c_mme=sc,
            md_mme=md, se_mme=se, hedges_g=round(gg, 6), hedges_se=round(gse, 6),
            in_S0=0 if is_alt else 1,
            in_S0_teas_sham=1 if (not is_alt and r["modality"] == "TEAS"
                                  and r["comparator"] == "Sham") else 0,
            in_S0_ea_usual=1 if (not is_alt and r["modality"] == "EA"
                                 and r["comparator"] == "Usual Care") else 0,
            multiarm_alt=1 if is_alt else 0,
            multiarm_note=r["multiarm"], source_locator=r["source"],
        ))

    cols = list(rows[0].keys())
    p = OUT / "tiered_primary_v33.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for x in rows: w.writerow(x)
    print(f"wrote {p}  ({len(rows)} rows)")

    # Tier C parallel-synthesis table (medians; never converted)
    crows = []
    for r in TIER_C:
        crows.append(dict(
            study=r["study"], year=r["year"], comparison_id=r["comparison_id"],
            modality=r["modality"], comparator=r["comparator"], tier="C",
            n_i=r["n_i"], n_c=r["n_c"],
            median_i_src=r["median_i"], q1_i_src=r["q1_i"], q3_i_src=r["q3_i"],
            median_c_src=r["median_c"], q1_c_src=r["q1_c"], q3_c_src=r["q3_c"],
            unit_src=r["unit"], mme_factor=r["factor"],
            median_i_mme=mme(r["median_i"], r["factor"]),
            q1_i_mme=mme(r["q1_i"], r["factor"]), q3_i_mme=mme(r["q3_i"], r["factor"]),
            median_c_mme=mme(r["median_c"], r["factor"]),
            q1_c_mme=mme(r["q1_c"], r["factor"]), q3_c_mme=mme(r["q3_c"], r["factor"]),
            median_difference_mme=round(mme(r["median_i"], r["factor"]) -
                                        mme(r["median_c"], r["factor"]), 6),
            reported_p=r["reported_p"], not_pooled_reason=r["note"],
            source_locator=r["source"],
        ))
    ccols = list(crows[0].keys())
    pc = OUT / "tiered_tierC_parallel_v33.csv"
    with pc.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ccols); w.writeheader()
        for x in crows: w.writerow(x)
    print(f"wrote {pc}  ({len(crows)} rows)")

    print("\nS0 strata:")
    print("  TEAS vs Sham :", [r["study"] for r in rows if r["in_S0_teas_sham"]])
    print("  EA vs Usual  :", [r["study"] for r in rows if r["in_S0_ea_usual"]])
    print("  multi-arm alt:", [r["study"] for r in rows if r["multiarm_alt"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
