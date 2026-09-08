#!/usr/bin/env python3
"""
Scan every v34 native outcome family for groups that are genuinely poolable
under the review protocol, and say why each rejected group was rejected.

INCLUDE in the v34 workbook means "numerically extractable in its native
endpoint, unit, window, population and statistic". It does NOT mean poolable.
This script applies the pooling rules the project already enforces elsewhere:

  * stratify by modality AND comparator type -- TEAS and EA are never combined,
    and sham is never combined with usual care
  * one exact outcome, window, unit and statistic type per model
  * count INDEPENDENT STUDIES, not contrasts: a multi-arm trial contributing
    two arms against one shared control is one study, not two
  * k >= 2 to pool at all; k >= 3 before a Hartung-Knapp interval is meaningful
  * an effect and its standard error must both exist

Output is a candidate register, not an instruction to run anything: every
candidate still needs the shared-arm decision and the source holds checked.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
OUT = ROOT / "09_V34_ANALYSIS"

FAMILIES = sorted(DATA.glob("v34_native_*.csv"))

# Groups already fitted and published by the v34 reconciliation run.
ALREADY_RUN = {
    ("intraoperative_opioid", "remifentanil", "TEAS", "Sham"),
    ("intraoperative_opioid", "sufentanil", "TEAS", "Sham"),
    ("qor40", "qor40", "TEAS", "Sham"),
    ("gi_recovery", "defecation", "TEAS", "Sham"),
    ("gi_recovery", "defecation", "EA", "Usual care"),
}


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def norm(v) -> str:
    return (v or "").strip()


def has_effect(r: dict) -> bool:
    try:
        float(r.get("effect", ""))
        float(r.get("se", ""))
        return True
    except (TypeError, ValueError):
        return False


def resolutions() -> dict:
    """Modality/comparator classifications resolved by resolve_comparators.py,
    keyed by record_id. Applying them here means the scan sees the same
    classification the analysis will, rather than re-deriving it."""
    p = OUT / "v34_comparator_resolution.csv"
    if not p.exists():
        return {}
    out = {}
    for r in read(p):
        if r.get("resolved") == "YES":
            out[r["record_id"]] = (r["modality_after"], r["comparator_after"])
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    res = resolutions()
    rows_all = []
    applied = 0
    for f in FAMILIES:
        fam = f.stem.replace("v34_native_", "")
        for r in read(f):
            r["_family_file"] = fam
            fix = res.get(r.get("record_id"))
            if fix:
                if "REVIEW_REQUIRED" in r["modality"]:
                    r["modality"] = fix[0]
                if "REVIEW_REQUIRED" in r["comparator_type"]:
                    r["comparator_type"] = fix[1]
                applied += 1
            rows_all.append(r)
    if applied:
        print(f"applied {applied} resolved modality/comparator classifications\n")
    print(f"native rows scanned: {len(rows_all)} across {len(FAMILIES)} family files\n")

    # ── group on the full estimand key ────────────────────────────────────
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows_all:
        key = (
            r["_family_file"],
            norm(r.get("outcome")),
            norm(r.get("window")),
            norm(r.get("unit")),
            norm(r.get("statistic_type")),
            norm(r.get("modality")),
            norm(r.get("comparator_type")),
        )
        groups[key].append(r)

    candidates, rejected = [], []
    for key, rs in sorted(groups.items()):
        fam, outcome, window, unit, stat, modality, comparator = key
        incl = [r for r in rs if norm(r.get("eligibility")).upper() == "INCLUDE"]
        usable = [r for r in incl if has_effect(r)]
        studies = sorted({norm(r.get("study")) for r in usable})
        contrasts = len(usable)
        k = len(studies)

        rec = dict(family=fam, outcome=outcome, window=window, unit=unit,
                   statistic=stat, modality=modality, comparator=comparator,
                   rows=len(rs), include_rows=len(incl), usable_contrasts=contrasts,
                   independent_studies=k, studies="; ".join(studies))

        if not modality or not comparator:
            rec["verdict"] = "REJECT - modality or comparator not resolved"
        elif "REVIEW_REQUIRED" in comparator or "REVIEW_REQUIRED" in modality:
            rec["verdict"] = "HOLD - comparator type needs adjudication"
        elif k < 2:
            rec["verdict"] = f"NOT POOLED - only {k} independent study"
        elif contrasts > k:
            rec["verdict"] = (f"HOLD - {contrasts} contrasts from {k} studies; "
                              "shared-arm selection required before pooling")
        else:
            rec["verdict"] = f"CANDIDATE - k={k} independent studies"

        (candidates if rec["verdict"].startswith("CANDIDATE") else rejected).append(rec)

    cols = ["family", "outcome", "window", "unit", "statistic", "modality",
            "comparator", "rows", "include_rows", "usable_contrasts",
            "independent_studies", "verdict", "studies"]
    allrecs = sorted(candidates + rejected,
                     key=lambda r: (not r["verdict"].startswith("CANDIDATE"),
                                    r["family"], r["outcome"]))
    p = OUT / "v34_poolable_scan.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(allrecs)

    print(f"groups examined      : {len(groups)}")
    print(f"pooling candidates   : {len(candidates)}")
    print(f"not pooled / held    : {len(rejected)}\n")

    print("POOLING CANDIDATES (k >= 2 independent studies, one exact estimand):")
    for c in sorted(candidates, key=lambda r: -r["independent_studies"]):
        already = "  [already fitted in v34]" if any(
            a[0] in c["family"] and a[1] in c["outcome"].lower()
            and a[2] == c["modality"] and a[3] == c["comparator"]
            for a in ALREADY_RUN) else ""
        print(f"  k={c['independent_studies']}  {c['family']}/{c['outcome'][:38]:<38} "
              f"{c['window'][:16]:<16} {c['modality']}/{c['comparator']}{already}")
        print(f"         {c['studies'][:110]}")

    holds = [r for r in rejected if r["verdict"].startswith("HOLD")]
    print(f"\nSHARED-ARM / ADJUDICATION HOLDS ({len(holds)}):")
    for h in holds[:14]:
        print(f"  {h['family']}/{h['outcome'][:36]:<36} {h['modality']}/{h['comparator'][:26]:<26}"
              f" {h['usable_contrasts']} contrasts / {h['independent_studies']} studies")

    print(f"\nwrote {p.relative_to(ROOT)}")
    (OUT / "v34_poolable_scan.json").write_text(
        json.dumps({"candidates": candidates, "rejected": rejected}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
