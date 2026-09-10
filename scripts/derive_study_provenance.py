#!/usr/bin/env python3
"""
Derive how each of the 70 canonical studies entered the review.

WHY THIS EXISTS
The dashboard states the PRISMA identification split as "69 via database search
+ 1 via citation searching" without naming the citation-searched study, so the
claim could not be checked by a reader or by this pipeline. This re-derives the
split from the review's own screening records and names the study.

METHOD
Every canonical study in the locked workbook's Study_Master is matched against
the Covidence screening exports (63 included + 161 excluded records) by, in
order, Covidence internal id, unique_index, then study_id -- Study_Master stores
both Covidence id formats, so a single-key match undercounts. A study that
resolves to a Covidence record was identified by the database search, whether it
was ultimately included or excluded there. A study that resolves to nothing was
not retrieved by the search at all.

WHAT IT FINDS
69 resolve (63 included, 6 excluded and later reinstated); exactly one does not.

Usage:  python3 scripts/derive_study_provenance.py [--json]
Exit:   0 if the derived split matches the dashboard's claim, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = (ROOT / "TEAS EA Verification" /
          "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx")
INCLUDED = ROOT / "covidence_all_63_included.json"
EXCLUDED = ROOT / "covidence_all_161_excluded.json"

EXPECTED_DATABASE = 69
EXPECTED_CITATION = 1


def load_screening() -> list[tuple[dict, str]]:
    pool = [(r, "INCLUDED") for r in json.loads(INCLUDED.read_text(encoding="utf-8"))]
    pool += [(r, "EXCLUDED") for r in json.loads(EXCLUDED.read_text(encoding="utf-8"))]
    return pool


def derive() -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)
    rows = [list(r) for r in wb["Study_Master"].iter_rows(values_only=True)]
    header, records = rows[0], rows[1:]
    studies = [dict(zip(header, r)) for r in records]

    pool = load_screening()
    # Study_Master stores Covidence's long internal id for some studies and the
    # short reference number (unique_index) for others; study_id is the fallback
    # for rows whose id was lost during an identity correction.
    by_id, by_uidx, by_sid = {}, {}, {}
    for rec, status in pool:
        by_id.setdefault(str(rec.get("id")), (status, rec))
        by_uidx.setdefault(str(rec.get("unique_index")), (status, rec))
        by_sid.setdefault(str(rec.get("study_id")), (status, rec))

    database, citation = [], []
    for s in studies:
        name = s["Canonical study"]
        cid = (s.get("Covidence internal ID") or "").strip()
        hit = by_id.get(cid) or by_uidx.get(cid) or by_sid.get(name)
        if hit is None:
            citation.append({"study": name,
                             "batch": s.get("Reconciliation batch"),
                             "identity_note": s.get("Identity correction")})
        else:
            status, rec = hit
            database.append({"study": name, "covidence_status": status,
                             "covidence_ref": rec.get("unique_index"),
                             "batch": s.get("Reconciliation batch")})

    reinstated = [d for d in database if d["covidence_status"] == "EXCLUDED"]
    return {"total": len(studies), "database_search": database,
            "citation_searching": citation, "reinstated_after_exclusion": reinstated}


def main() -> int:
    out = derive()
    n_db, n_cite = len(out["database_search"]), len(out["citation_searching"])

    if "--json" in sys.argv:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print(f"canonical studies ......... {out['total']}")
    print(f"via database search ....... {n_db} "
          f"({n_db - len(out['reinstated_after_exclusion'])} included in Covidence, "
          f"{len(out['reinstated_after_exclusion'])} excluded there and reinstated)")
    print(f"via citation searching .... {n_cite}")
    for c in out["citation_searching"]:
        print(f"    -> {c['study']}  ({c['batch']})")
    print("\nreinstated after full-text exclusion in Covidence:")
    for r in sorted(out["reinstated_after_exclusion"], key=lambda x: x["study"]):
        print(f"    Cov #{r['covidence_ref']:<6} {r['study']}")

    ok = (n_db == EXPECTED_DATABASE and n_cite == EXPECTED_CITATION)
    print(f"\nderived split {n_db} + {n_cite} "
          f"{'matches' if ok else 'DOES NOT MATCH'} the stated "
          f"{EXPECTED_DATABASE} + {EXPECTED_CITATION}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
