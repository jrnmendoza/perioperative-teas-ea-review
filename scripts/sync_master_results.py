#!/usr/bin/env python3
"""
Sync master_reconciled_results_v26.csv from the Stata-written result tables.

master_reconciled_results_v26.csv is the aggregate the dashboard reads, but no
do-file writes it -- historically it was maintained by hand, which is exactly
the drift class that let a superseded k=10 broader-SMD row survive a pipeline
re-run that produced k=9.

This script closes that gap. For every analysis_id present in BOTH the master
aggregate and a Stata result table, it overwrites the numeric fields from the
Stata table; then it appends the v33 tiered rows. Rows with no Stata twin
(narrative or hand-curated entries) are left untouched, and the script reports
exactly which those are so the gap stays visible.

Usage:  python3 scripts/sync_master_results.py [--check]
        --check exits 1 if the file is out of sync instead of rewriting it.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS"
MASTER = RESULTS / "master_reconciled_results_v26.csv"
V33_RESULTS = ROOT / "07_TIERED_V33" / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33.csv"

# Stata tables that carry an analysis_id keyed to the master aggregate.
STATA_TABLES = [
    "results_opioid24_primary.csv",

    "results_broader24h_sensitivity.csv",
    "results_sensitivity_estimators_grid.csv",
    "results_subgroups_metareg.csv",
    "results_targetA_48h.csv",
    "results_targetB_72h.csv",
    "results_targetC_pain24h.csv",
    "results_targetD_ponv.csv",
    "results_targetE_flatus.csv",
    "results_targetF_exploratory.csv",
]

# The estimator/CI grid has no analysis_id column; the master keys its rows as
# "SENS_<estimator>_<first four characters of se_adj>". Reconstructing that key
# here brings those 7 rows under the same drift check as everything else.
GRID_TABLE = "results_sensitivity_estimators_grid.csv"

# Fields copied from the Stata table when both sides have them.
SYNCED = ("k", "effect_measure", "estimate", "ci_low", "ci_high",
          "p_value", "tau2", "i2", "q_stat", "model")

# v33 rows appended to the aggregate, sourced from TIERED_ANALYSIS_RESULTS_v33.csv.
# target/stratum/notes are supplied here; every number comes from the Stata file.
V33_APPEND = {
    "V33_S0_TEAS_SHAM": dict(
        target="Primary (v33)",
        outcome="Cumulative 0-24 h postoperative opioid consumption",
        stratum="S0 Tier A: TEAS vs inert sham",
        notes="v33 PRIMARY. Supersedes OP24_PRIM_COMB as the headline estimate: "
              "that row pooled TEAS-vs-sham and EA-vs-usual-care evidence across "
              "two different comparators.",
    ),
    "V33_S0_EA_USUAL": dict(
        target="Supportive (v33)",
        outcome="Cumulative 0-24 h postoperative opioid consumption",
        stratum="S0 Tier A: EA vs usual care",
        notes="v33 SUPPORTIVE. Not sham-controlled; no sham-controlled EA trial "
              "reports this outcome (k=0).",
    ),
    "V33_SENS_C1_SZMIT_ALT": dict(
        target="Sensitivity (v33)",
        outcome="Cumulative 0-24 h postoperative opioid consumption",
        stratum="TEAS vs sham, Szmit 2021 usual-care arm substituted",
        notes="Comparator sensitivity. Szmit 2021 contributes exactly one "
              "contrast: swapped, never added.",
    ),
    "V33_SENS_C2_REML_WALD": dict(
        target="Sensitivity (v33)",
        outcome="Cumulative 0-24 h postoperative opioid consumption",
        stratum="S0 primary, REML + Wald CI",
        notes="Estimator/CI sensitivity. Wald intervals are anticonservative at "
              "k=4; the pre-specified primary remains Hartung-Knapp.",
    ),
    "V33_SENS_C2_DL_KH": dict(
        target="Sensitivity (v33)",
        outcome="Cumulative 0-24 h postoperative opioid consumption",
        stratum="S0 primary, DerSimonian-Laird + Hartung-Knapp",
        notes="Estimator/CI sensitivity.",
    ),
}

# Rows the v33 tiering supersedes. The row is kept -- a withdrawn headline must
# stay visible -- but its notes field is rewritten to say so.
SUPERSEDED_NOTES = {
    "OP24_PRIM_COMB":
        "SUPERSEDED by V33_S0_TEAS_SHAM. This row pools TEAS-vs-sham and "
        "EA-vs-usual-care trials in one model; v33 reports the two comparator "
        "strata separately and does not treat their combination as the primary "
        "result. Retained for transparency, not as a headline estimate.",
}


def values_agree(master_val: str, stata_val: str) -> bool:
    """
    True when the master cell is a correctly rounded rendering of the Stata value.

    The master aggregate is written for humans and stores e.g. "-0.1765" where
    Stata holds -.17651609. Rewriting every such cell to full precision would
    churn ~120 rows and destroy the readable formatting without correcting
    anything. A cell counts as drift only when it disagrees beyond the precision
    it is displayed at -- which is what caught the k=10 -> k=9 broader-SMD row.
    """
    m, s = master_val.strip(), stata_val.strip()
    if m == s:
        return True
    try:
        mf, sf = float(m), float(s)
    except ValueError:
        return False
    decimals = len(m.partition(".")[2].rstrip()) if "." in m else 0
    tol = 0.5 * (10 ** -decimals) if decimals else 0.5
    return abs(mf - sf) <= tol


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_stata_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for name in STATA_TABLES:
        path = RESULTS / name
        if not path.exists():
            print(f"  ! missing Stata table: {name}", file=sys.stderr)
            continue
        for row in read_rows(path):
            aid = (row.get("analysis_id") or "").strip()
            if aid:
                index[aid] = row

    grid = RESULTS / GRID_TABLE
    if grid.exists():
        for row in read_rows(grid):
            est = (row.get("estimator") or "").strip()
            adj = (row.get("se_adj") or "").strip()
            if est and adj:
                index[f"SENS_{est}_{adj[:4]}"] = row
    else:
        print(f"  ! missing Stata table: {GRID_TABLE}", file=sys.stderr)
    return index


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 instead of rewriting")
    args = ap.parse_args()

    master = read_rows(MASTER)
    fieldnames = list(master[0].keys())
    stata = load_stata_index()

    changed: list[str] = []
    unmatched: list[str] = []

    for row in master:
        aid = row["analysis_id"].strip()
        src = stata.get(aid)
        if src is None:
            # v33 rows have their own refresh path below, so they are not
            # "unmatched" -- only genuinely hand-curated rows belong in that list.
            if aid not in V33_APPEND:
                unmatched.append(aid)
        else:
            for field in SYNCED:
                if field in row and field in src and src[field] != "":
                    if not values_agree(row[field], src[field]):
                        changed.append(f"{aid}.{field}: {row[field]!r} -> {src[field]!r}")
                        row[field] = src[field]
        if aid in SUPERSEDED_NOTES and row.get("notes") != SUPERSEDED_NOTES[aid]:
            changed.append(f"{aid}.notes: marked superseded")
            row["notes"] = SUPERSEDED_NOTES[aid]

    # Append / refresh v33 rows.
    if not V33_RESULTS.exists():
        print(f"ERROR: {V33_RESULTS} not found; run 13_tiered_primary_v33.do first",
              file=sys.stderr)
        return 1
    v33 = {r["analysis_id"]: r for r in read_rows(V33_RESULTS)}
    existing = {r["analysis_id"].strip() for r in master}

    for aid, meta in V33_APPEND.items():
        src = v33.get(aid)
        if src is None:
            print(f"ERROR: {aid} missing from {V33_RESULTS.name}", file=sys.stderr)
            return 1
        new = {fn: "" for fn in fieldnames}
        new["analysis_id"] = aid
        new["target"] = meta["target"]
        new["outcome"] = meta["outcome"]
        new["stratum"] = meta["stratum"]
        new["notes"] = meta["notes"]
        new["k"] = src["k"]
        new["effect_measure"] = "MD (mg IV MME)"
        new["estimate"] = src["estimate"]
        new["ci_low"] = src["ci_low"]
        new["ci_high"] = src["ci_high"]
        new["p_value"] = src["p_value"]
        new["tau2"] = src["tau2"]
        new["i2"] = src["i2"]
        new["q_stat"] = src["q_stat"]
        new["model"] = f'{src["estimator"]} + {src["ci_method"]}'

        if aid in existing:
            for i, row in enumerate(master):
                if row["analysis_id"].strip() == aid:
                    if row != new:
                        changed.append(f"{aid}: refreshed from v33 results")
                        master[i] = new
                    break
        else:
            changed.append(f"{aid}: appended")
            master.append(new)

    print(f"Master aggregate: {len(master)} rows")
    print(f"Rows with a Stata twin  : {len(master) - len(unmatched)}")
    print(f"Rows with NO Stata twin : {len(unmatched)}")
    for aid in unmatched:
        print(f"    (hand-curated) {aid}")

    if not changed:
        print("\nIn sync: no changes needed.")
        return 0

    print(f"\n{len(changed)} change(s):")
    for line in changed:
        print(f"    {line}")

    if args.check:
        print("\n--check: master aggregate is OUT OF SYNC with the Stata outputs.",
              file=sys.stderr)
        return 1

    with MASTER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(master)
    print(f"\nRewrote {MASTER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
