#!/usr/bin/env python3
"""
Which identity convention does each file use for the Yeh lumbar-spine pair?

WHY
Study_Master.csv and Outcome_Data_AF_LOCK.csv disagree about which register key
names which publication (see 05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md).
Resolving that means re-cutting one side to match the other -- and the only way to
choose safely is to know how many files, and which ones, sit on each side.

This script answers exactly that and nothing else. It does not edit anything.

HOW A FILE IS CLASSIFIED
The two publications are separable by their own numbers, so no filename or label
is trusted:

  Altern Ther Health Med 2010  arms 33 / 30 / 31, AES mean 18.6, PCA pushes 25.3,
                               Table 4, route printed as epidural
  Int J Nurs Stud 2011         arms 30 / 30 / 30, AES mean 19.3, PCA pushes 24.9,
                               control 28.0, Table 3, route mg IV morphine

A file is "AF_LOCK convention" when its rows labelled Yeh 2010 carry the Altern
Ther Health Med numbers, and "Study_Master convention" when they carry the Int J
Nurs Stud numbers.

Usage:  python3 scripts/audit_yeh_identity_convention.py [--json]
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Numbers unique to one paper or the other. Deliberately narrow: a token that
# could plausibly appear in either paper's rows is not a discriminator.
ATHM = (re.compile(r"\b18\.6\b|\b25\.3\b|\b27\.2\b|\bTable 4\b|epidural", re.I), "ATHM")
IJNS = (re.compile(r"\b19\.3\b|\b24\.9\b|\b28\.0\b|\b76\.9\b|\bTable 3\b|mg IV morphine", re.I), "IJNS")

SEARCH = ("06_FINAL_ANALYSIS_V26/**/*.csv", "07_TIERED_V33/**/*.csv",
          "TEAS EA Verification/**/*.csv", "dashboard/**/*.csv")


def classify(path: Path) -> dict | None:
    try:
        rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    except (UnicodeDecodeError, csv.Error, OSError):
        return None
    per_label: dict[str, set] = {}
    for r in rows:
        blob = " ".join(str(v) for v in r.values() if v)
        m = re.search(r"\bYeh 20(10|11)\b|\bYEH(10|11)_", blob)
        if not m:
            continue
        label = "Yeh 20" + (m.group(1) or m.group(2))
        for rx, name in (ATHM, IJNS):
            if rx.search(blob):
                per_label.setdefault(label, set()).add(name)
    if not per_label:
        return None
    # A file takes a side when either label's rows are unambiguously one paper.
    # Some files carry only one of the two (the primary-analysis extracts hold the
    # Yeh 2011 row alone, under a family-level study_unit), so checking Yeh 2010
    # by itself left them undecided when they are not.
    y10, y11 = per_label.get("Yeh 2010", set()), per_label.get("Yeh 2011", set())
    af = y10 == {"ATHM"} or y11 == {"IJNS"}
    sm = y10 == {"IJNS"} or y11 == {"ATHM"}
    if af and not sm:
        side = "AF_LOCK convention (Yeh 2010 = Altern Ther Health Med)"
    elif sm and not af:
        side = "Study_Master convention (Yeh 2010 = Int J Nurs Stud)"
    else:
        side = "indeterminate"
    return {"file": str(path.relative_to(ROOT)), "side": side,
            "labels": {k: sorted(v) for k, v in sorted(per_label.items())}}


def main(as_json: bool) -> int:
    seen, results = set(), []
    for pat in SEARCH:
        for f in glob.glob(str(ROOT / pat), recursive=True):
            p = Path(f)
            if p in seen:
                continue
            seen.add(p)
            c = classify(p)
            if c:
                results.append(c)
    results.sort(key=lambda c: (c["side"], c["file"]))

    # Study_Master's identity fields are the reason this question exists; quote them.
    sm = ROOT / "06_FINAL_ANALYSIS_V26/01_DATA/authoritative_sheets/Study_Master.csv"
    identity = {}
    if sm.exists():
        for r in csv.DictReader(sm.open(encoding="utf-8-sig")):
            if (r.get("Canonicalstudy") or "").startswith("Yeh"):
                identity[r["Canonicalstudy"]] = {
                    k: r.get(k) for k in ("Antigravitystudylabel", "Antigravitystudykey",
                                          "CovidenceinternalID", "Identitycorrection")
                    if r.get(k)}

    payload = {"study_master_identity_fields": identity, "files": results,
               "tally": {s: sum(1 for c in results if c["side"] == s)
                         for s in sorted({c["side"] for c in results})}}
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Study_Master identity fields for the pair:")
    for k, v in identity.items():
        print(f"  {k}: {v}")
    print()
    for side in sorted({c["side"] for c in results}):
        members = [c for c in results if c["side"] == side]
        print(f"{side}  — {len(members)} file(s)")
        for c in members:
            print(f"    {c['file']}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main("--json" in sys.argv))
