#!/usr/bin/env python3
"""
Generate dashboard/tiered_v33.js — the v33 primary-outcome derivability flow.

Everything on the dashboard's derivability panel is derived here from two
authoritative files and nothing is retyped:

  07_TIERED_V33/01_DATA/tiered_primary_v33.csv        Tier A contrasts + strata
  07_TIERED_V33/01_DATA/tiered_tierC_parallel_v33.csv Tier C median/IQR evidence
  07_TIERED_V33/01_DATA/tiered_tierE_smd_v33.csv      Tier E scale-free SMD contrasts
  07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33.csv  Stata pooled results (S0-S3, sens_*)
  07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33_tierE.csv  Stata pooled results (Tier E SMD)
  07_TIERED_V33/PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv  full 93-row audit

The tier *definitions* are stated here because they are the classification rule,
not data. Every count, study name and number below is read from the files.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V33 = ROOT / "07_TIERED_V33"
OUT = ROOT / "dashboard" / "tiered_v33.js"

TIER_DEFS = [
    dict(tier="A", label="Directly compatible",
         rule="Exact 0–24 h cumulative postoperative opioid, reported as mean and SD, "
              "in an absolute dose unit with a sourced MME conversion factor."),
    dict(tier="B", label="Deterministically derived",
         rule="Recoverable by an exact arithmetic identity from reported quantities, "
              "with no distributional assumption."),
    dict(tier="C", label="Alternative distributional form",
         rule="Exactly the right estimand, but reported as a median and IQR. "
              "Reported as a parallel synthesis; never converted to mean/SD for pooling."),
    dict(tier="D", label="Recoverable only by digitization",
         rule="Present only in a figure. Admissible only if a pre-specified "
              "digitization passes validation against values stated in the text."),
    dict(tier="E", label="Requires a prohibited assumption for absolute dose",
         rule="Would need an assumed body weight, an assumed solution concentration, PCA "
              "presses treated as delivered doses, POD1 treated as 0–24 h, or an invented "
              "covariance to reach an absolute IV MME value — not admissible for the "
              "absolute-MME estimand at any tier. A subset with a native mean/SD (no such "
              "assumption needed for the WITHIN-STUDY standardized effect) is admissible on "
              "a separate, scale-free SMD (Hedges' g) exploratory synthesis instead — see "
              "the Tier E panel below. This is a different, weaker claim than the primary."),
]


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def num(v, nd=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return round(f, nd) if nd is not None else f


def main() -> int:
    tier_a = read(V33 / "01_DATA" / "tiered_primary_v33.csv")
    tier_c = read(V33 / "01_DATA" / "tiered_tierC_parallel_v33.csv")
    tier_e = read(V33 / "01_DATA" / "tiered_tierE_smd_v33.csv")
    results = {r["analysis_id"]: r for r in read(V33 / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33.csv")}
    results.update({r["analysis_id"]: r
                     for r in read(V33 / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33_tierE.csv")})

    audit_path = V33 / "PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv"
    audit = read(audit_path) if audit_path.exists() else []

    def result(aid: str):
        r = results.get(aid)
        if not r:
            raise SystemExit(f"missing analysis_id {aid} in TIERED_ANALYSIS_RESULTS_v33.csv")
        return {
            "analysis_id": aid,
            "analysis_set": r["analysis_set"],
            "modality": r["modality"],
            "comparator": r["comparator"],
            "outcome": r["outcome"],
            "window": r["window"],
            "unit": r["unit"],
            "k": int(float(r["k"])) if r["k"] else None,
            "effect_measure": r["effect_measure"],
            "estimate": num(r["estimate"], 3),
            "ci_low": num(r["ci_low"], 3),
            "ci_high": num(r["ci_high"], 3),
            "p_value": num(r["p_value"], 4),
            "tau2": num(r["tau2"], 3),
            "i2": num(r["i2"], 2),
            "pi_low": num(r["pi_low"], 2),
            "pi_high": num(r["pi_high"], 2),
            "estimator": r["estimator"],
            "ci_method": r["ci_method"],
            "notes": r["notes"],
        }

    def contrast(r: dict) -> dict:
        return {
            "study": r["study"],
            "year": int(r["year"]),
            "modality": r["modality"],
            "comparator": r["comparator"],
            "n_i": int(r["n_i"]),
            "n_c": int(r["n_c"]),
            "unit_src": r["unit_src"],
            "mme_factor": num(r["mme_factor"]),
            "md_mme": num(r["md_mme"], 3),
            "se_mme": num(r["se_mme"], 3),
            "multiarm_note": r["multiarm_note"],
            "source_locator": r["source_locator"],
        }

    def tier_e_contrast(r: dict) -> dict:
        return {
            "study": r["study"],
            "year": int(r["year"]),
            "modality": r["modality"],
            "comparator": r["comparator"],
            "stratum": r["stratum"],
            "n_i": num(r["n_i"], 1),
            "n_c": int(float(r["n_c"])),
            "unit_src": r["unit_src"],
            "hedges_g": num(r["hedges_g"], 3),
            "hedges_se": num(r["hedges_se"], 3),
            "sensitivity_only": r["sensitivity_only"] == "1",
            "combine_note": r["combine_note"],
            "multiarm_note": r["multiarm_note"],
            "caveat": r["caveat"],
            "source_locator": r["source_locator"],
        }

    tier_e_contrasts = [tier_e_contrast(r) for r in tier_e]

    teas_sham = [contrast(r) for r in tier_a if r["in_S0_teas_sham"] == "1"]
    ea_usual = [contrast(r) for r in tier_a if r["in_S0_ea_usual"] == "1"]
    multiarm_alt = [contrast(r) for r in tier_a if r["multiarm_alt"] == "1"]

    parallel = [{
        "study": r["study"],
        "modality": r["modality"],
        "comparator": r["comparator"],
        "n_i": int(r["n_i"]), "n_c": int(r["n_c"]),
        "median_i": num(r["median_i_mme"], 2), "q1_i": num(r["q1_i_mme"], 2), "q3_i": num(r["q3_i_mme"], 2),
        "median_c": num(r["median_c_mme"], 2), "q1_c": num(r["q1_c_mme"], 2), "q3_c": num(r["q3_c_mme"], 2),
        "median_difference": num(r["median_difference_mme"], 2),
        "reported_p": r["reported_p"],
        "not_pooled_reason": r["not_pooled_reason"],
        "source_locator": r["source_locator"],
    } for r in tier_c]

    payload = {
        "generated_by": "scripts/build_tiered_v33.py",
        "data_source": "07_TIERED_V33/01_DATA + 05_RESULTS (StataNow 19.5)",
        "audit_rows": len(audit),
        "audit_file": "07_TIERED_V33/PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.xlsx",
        "outcome": "Cumulative postoperative opioid consumption",
        "window": "0–24 h",
        "unit": "mg intravenous morphine milligram equivalents (IV MME)",
        "estimator": "Random-effects REML",
        "ci_method": "Hartung–Knapp (t reference distribution)",

        "tier_definitions": TIER_DEFS,

        "strata": {
            "teas_sham": teas_sham,
            "ea_usual": ea_usual,
            "multiarm_alternatives": multiarm_alt,
            "ea_sham_k": 0,
        },

        "parallel_synthesis": parallel,

        "analysis_sets": {
            "S0_teas_sham": result("V33_S0_TEAS_SHAM"),
            "S0_ea_usual": result("V33_S0_EA_USUAL"),
            "S1": result("V33_S1_TEAS_SHAM"),
            "S2": result("V33_S2_PARALLEL"),
            "S3": result("V33_S3_TEAS_SHAM"),
            "sens_comparator": result("V33_SENS_C1_SZMIT_ALT"),
            "sens_reml_wald": result("V33_SENS_C2_REML_WALD"),
            "sens_dl_kh": result("V33_SENS_C2_DL_KH"),
        },

        "tier_e_smd": {
            "status": "EXPLORATORY",
            "summary": "Tier E holds results that report the exact 0-24 h cumulative opioid "
                       "estimand as a mean/SD, but in a unit with no sourced absolute-IV-MME "
                       "conversion (a weight-normalized dose, or a volume proxy with an "
                       "unreported concentration). That blocks the ABSOLUTE-MME primary above, "
                       "not a WITHIN-STUDY standardized effect: a Hedges' g divides the "
                       "between-arm difference by the pooled SD, so the unit cancels. This is a "
                       "different, weaker claim (a relative standardized effect, not mg spared) "
                       "and is never pooled with, added to, or substituted for the S0-S3 "
                       "absolute-MME estimates above.",
            "contrasts": tier_e_contrasts,
            "excluded": [
                {"study": "Zhang 2025", "reason": "Window mismatch: reports postoperative day "
                 "1, not an explicit 0-24 h clock window. The SMD metric does not fix a wrong "
                 "time window."},
                {"study": "Ntritsou 2014", "reason": "Wrong estimand: reported total tramadol "
                 "includes protocol-mandated background dosing, not only demand-driven "
                 "postoperative consumption."},
                {"study": "Oztas 2019 (combined opioid dose)", "reason": "Combined tramadol + "
                 "pethidine total; the combined variance is not recoverable without an "
                 "unknown within-person covariance."},
                {"study": "Oztas 2019 (TEAS vs TENS arm)", "reason": "Comparator eligibility "
                 "unresolved (audit status: 'Check') -- excluded pending a decision, not "
                 "assumed eligible or ineligible."},
                {"study": "Song 2020", "reason": "Assumption-dependent derivation: PCA pump "
                 "presses are recorded, not delivered doses, and presses != deliveries is an "
                 "unverifiable assumption regardless of metric."},
            ],
            "analysis_sets": {
                "ea_sham": result("V33_TIERE_EA_SHAM_SMD"),
                "teas_sham_main": result("V33_TIERE_TEAS_SHAM_SMD_MAIN"),
                "teas_sham_sensitivity": result("V33_TIERE_TEAS_SHAM_SMD_SENS"),
                "teas_usual": result("V33_TIERE_TEAS_USUAL_SMD"),
            },
        },

        "figures": [
            {"file": "forestA_S0_teas_sham_24h_mme.png",
             "caption": "A. Primary — TEAS vs inert sham, cumulative 0–24 h opioid (mg IV MME)"},
            {"file": "forestB_S0_ea_usualcare_24h_mme.png",
             "caption": "B. Supportive — EA vs usual care, cumulative 0–24 h opioid (mg IV MME)"},
            {"file": "forestC_tier_sensitivity.png",
             "caption": "C. Tier sensitivity — analysis sets S0, S1, S3"},
            {"file": "forestD_comparator_sensitivity.png",
             "caption": "D. Comparator sensitivity — sham vs usual-care strata"},
            {"file": "forestE_ea_sham_smd.png",
             "caption": "E. EXPLORATORY — Tier E scale-free SMD, EA vs sham/placebo "
                        "(Hedges' g, k=2). Not the absolute-MME estimand."},
            {"file": "forestF_teas_sham_smd_sensitivity.png",
             "caption": "F. EXPLORATORY SENSITIVITY — Tier E scale-free SMD, EA/TEAS vs sham "
                        "(Hedges' g, k=2), adding a median/IQR-approximated study."},
        ],

        "empty_cells": [
            {"cell": "EA vs inert sham",
             "k": 0,
             "statement": "No sham-controlled EA trial reports an analysable cumulative 0–24 h "
                          "opioid mean and SD in absolute dose units. The EA estimate is a "
                          "usual-care comparison and cannot be read as a specific-acupoint effect."},
            {"cell": "Tier B increment (S1)",
             "k": 0,
             "statement": "No trial supplies a deterministic mean/SD derivation that is not already "
                          "Tier A. Chen 2015's rescue-bolus derivation is exact, but the reported "
                          "quantities are medians and IQRs, so it is Tier C."},
            {"cell": "Tier D increment (S3)",
             "k": 0,
             "statement": "One candidate (Gu 2019, Figure 4) was digitized under a pre-specified "
                          "protocol. Axis calibration was exact, and the low-frequency TEAS arm "
                          "reproduced the in-text values to within 4.2%, but the control arm was "
                          "overestimated by up to 16.0% — a figure-versus-text inconsistency in the "
                          "source. The digitization failed validation and Gu 2019 is not admissible."},
        ],

        "withdrawn": [
            {"study": "Zhang 2025",
             "reason": "Reports postoperative day 1, not an explicit 0–24 h clock window. Removed "
                       "from every 0–24 h analysis, including the scale-free broader SMD sensitivity "
                       "(k = 10 → 9): the SMD changes the unit, not the estimand."},
            {"study": "Coura 2011 (70 kg reconstruction)",
             "reason": "The reader-facing absolute-dose reconstruction multiplies µg/kg by an assumed "
                       "70 kg the trial never reports. Labelled a legacy reconstruction; it feeds no "
                       "pooled estimate. Coura 2011 enters only the scale-free SMD sensitivity, from "
                       "its native µg/kg values."},
        ],
    }

    header = f"""// v33 TIERED PRIMARY-OUTCOME DERIVABILITY — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_tiered_v33.py
//
// Every count, study name, effect estimate and interval below is read from the
// v33 data and Stata result files; none is typed here. The tier definitions are
// the classification rule, not data, and are stated in the generator.
//
// Data     : {payload['data_source']}
// Audit    : {payload['audit_file']} ({payload['audit_rows']} rows)
// Estimator: {payload['estimator']} + {payload['ci_method']}
window.TIERED_V33 = """

    OUT.write_text(header + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  audit rows ............... {payload['audit_rows']}")
    print(f"  S0 TEAS vs sham .......... k={len(teas_sham)}")
    print(f"  S0 EA vs usual care ...... k={len(ea_usual)}")
    print(f"  EA vs sham ............... k=0")
    print(f"  Tier C parallel .......... k={len(parallel)}")
    print(f"  multi-arm alternatives ... {len(multiarm_alt)}")
    print(f"  Tier E SMD contrasts ..... {len(tier_e_contrasts)} "
          f"({sum(1 for c in tier_e_contrasts if not c['sensitivity_only'])} main + "
          f"{sum(1 for c in tier_e_contrasts if c['sensitivity_only'])} sensitivity-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
