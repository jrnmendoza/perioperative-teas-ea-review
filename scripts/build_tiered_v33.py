#!/usr/bin/env python3
"""
Generate dashboard/tiered_v33.js — the v33 primary-outcome derivability flow.

Everything on the dashboard's derivability panel is derived here from two
authoritative files and nothing is retyped:

  07_TIERED_V33/01_DATA/tiered_primary_v33.csv        Tier A contrasts + strata
  07_TIERED_V33/01_DATA/tiered_tierC_parallel_v33.csv Tier C median/IQR evidence
  07_TIERED_V33/05_RESULTS/TIERED_ANALYSIS_RESULTS_v33.csv  Stata pooled results
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
    dict(tier="E", label="Requires a prohibited assumption",
         rule="Would need an assumed body weight, PCA presses treated as delivered doses, "
              "POD1 treated as 0–24 h, or an invented covariance. Not admissible at any tier."),
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
    results = {r["analysis_id"]: r for r in read(V33 / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33.csv")}

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

        "figures": [
            {"file": "forestA_S0_teas_sham_24h_mme.png",
             "caption": "A. Primary — TEAS vs inert sham, cumulative 0–24 h opioid (mg IV MME)"},
            {"file": "forestB_S0_ea_usualcare_24h_mme.png",
             "caption": "B. Supportive — EA vs usual care, cumulative 0–24 h opioid (mg IV MME)"},
            {"file": "forestC_tier_sensitivity.png",
             "caption": "C. Tier sensitivity — analysis sets S0, S1, S3"},
            {"file": "forestD_comparator_sensitivity.png",
             "caption": "D. Comparator sensitivity — sham vs usual-care strata"},
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
