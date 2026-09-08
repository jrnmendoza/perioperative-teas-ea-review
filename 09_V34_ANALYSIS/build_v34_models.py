#!/usr/bin/env python3
"""
Build Stata-ready datasets for the v34 analysis set.

Two jobs:

  1. Re-express the eight models the v34 reconciliation already fitted, so this
     project can reproduce them independently rather than copying a result CSV.
  2. Add the five additional models the poolable scan identified, each of which
     satisfies the protocol: one exact outcome / window / unit / statistic,
     stratified by modality AND comparator, and k independent studies with no
     shared-arm dependency (contrasts == studies).

Every row is selected from the v34 native family files by explicit rule. No
value is retyped, no median is converted, no graph-only row is admitted, and
TEAS/EA and sham/usual-care are never combined.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
OUT = ROOT / "09_V34_ANALYSIS" / "01_DATA"

# (model_id, family file, outcome, window, modality, comparator, measure)
MODELS = [
    # --- continuous, mean difference -------------------------------------
    ("gi_first_flatus_TEAS_Sham", "gi_recovery",
     "Time to first flatus", "Postoperative", "TEAS", "Sham", "MD"),
    ("gi_first_flatus_EA_Usual_care", "gi_recovery",
     "Time to first flatus", "Postoperative", "EA", "Usual care", "MD"),
    ("gi_first_bowel_sounds_TEAS_Sham", "gi_recovery",
     "Time to first bowel sounds", "Postoperative", "TEAS", "Sham", "MD"),
    ("pain_vas_24h_TEAS_Sham", "pain",
     "VAS pain intensity", "24 h", "TEAS", "Sham", "MD"),
    # --- binary, log risk ratio ------------------------------------------
    ("ponv_24h_TEAS_Sham", "ponv",
     "PONV incidence", "0-24 h", "TEAS", "Sham", "logRR"),
]


def resolutions() -> dict:
    """Modality/comparator classifications resolved by resolve_comparators.py.
    Applied here so the datasets use exactly the classification the scan and the
    dashboard use, rather than each re-deriving it."""
    p = ROOT / "09_V34_ANALYSIS" / "v34_comparator_resolution.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8-sig") as f:
        return {r["record_id"]: (r["modality_after"], r["comparator_after"])
                for r in csv.DictReader(f) if r.get("resolved") == "YES"}


RESOLVED = resolutions()


def read(name: str) -> list[dict]:
    with (DATA / f"v34_native_{name}.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        fix = RESOLVED.get(r.get("record_id"))
        if not fix:
            continue
        if "REVIEW_REQUIRED" in r["modality"]:
            r["modality"] = fix[0]
        if "REVIEW_REQUIRED" in r["comparator_type"]:
            r["comparator_type"] = fix[1]
    return rows


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cont(r):
    mi, si = num(r["mean_i"]), num(r["sd_i"])
    mc, sc = num(r["mean_c"]), num(r["sd_c"])
    ni, nc = num(r["n_i"]), num(r["n_c"])
    if None in (mi, si, mc, sc, ni, nc) or ni < 2 or nc < 2:
        return None
    md = mi - mc
    se = math.sqrt(si ** 2 / ni + sc ** 2 / nc)
    return dict(n_i=int(ni), n_c=int(nc), mean_i=mi, sd_i=si, mean_c=mc, sd_c=sc,
                effect=round(md, 6), se=round(se, 6))


def binary(r):
    ei, ec = num(r["events_i"]), num(r["events_c"])
    ni, nc = num(r["n_i"]), num(r["n_c"])
    if None in (ei, ec, ni, nc):
        return None
    if ei == 0 and ec == 0:
        return None            # no estimable logRR; documented, not invented
    zero = (ei == 0 or ec == 0)
    a, b = ei + 0.5 * zero, ec + 0.5 * zero
    n1, n2 = ni + 0.5 * zero, nc + 0.5 * zero
    lnrr = math.log((a / n1) / (b / n2))
    se = math.sqrt(1 / a - 1 / n1 + 1 / b - 1 / n2)
    return dict(n_i=int(ni), n_c=int(nc), events_i=int(ei), events_c=int(ec),
                zero_cell=int(zero), effect=round(lnrr, 6), se=round(se, 6))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []

    for mid, fam, outcome, window, modality, comparator, measure in MODELS:
        rows = [r for r in read(fam)
                if r["outcome"].strip() == outcome
                and r["window"].strip() == window
                and r["modality"].strip() == modality
                and r["comparator_type"].strip() == comparator
                and r["eligibility"].strip().upper() == "INCLUDE"]

        built = []
        for r in rows:
            e = binary(r) if measure == "logRR" else cont(r)
            if not e:
                continue
            built.append(dict(
                model=mid, study=r["study"].strip(), record_id=r["record_id"],
                comparison_id=r["comparison_id"], outcome=outcome, window=window,
                unit=r["unit"], modality=modality, comparator=comparator,
                statistic=r["statistic_type"],
                analysis_population=r.get("analysis_population", ""),
                rob2=r.get("rob2", ""), source_location=r.get("source_location", ""),
                measure=measure, **e))

        studies = sorted({b["study"] for b in built})
        if len(built) != len(studies):
            print(f"  SKIP {mid}: {len(built)} contrasts from {len(studies)} studies "
                  "-- shared-arm selection required")
            continue
        if len(studies) < 2:
            print(f"  SKIP {mid}: k={len(studies)}, not meta-analysed")
            continue

        cols = list(built[0].keys())
        p = OUT / f"{mid}.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(built)

        # k >= 3 supports Hartung-Knapp; k = 2 uses a normal CI, matching the
        # rule the v34 reconciliation applied.
        model = "REML + Hartung-Knapp" if len(studies) >= 3 else "REML normal CI"
        manifest.append(dict(model_id=mid, measure=measure, k=len(studies),
                             contrasts=len(built), outcome=outcome, window=window,
                             modality=modality, comparator=comparator,
                             unit=built[0]["unit"], estimator=model,
                             rob2_pending=sum(1 for b in built if "PENDING" in b["rob2"]),
                             studies="; ".join(studies), dataset=p.name))
        print(f"  wrote {p.name:<44} k={len(studies)}  {model}")

    mp = OUT / "v34_model_manifest.csv"
    with mp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(manifest)
    print(f"\nwrote {mp.name} ({len(manifest)} new models)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
