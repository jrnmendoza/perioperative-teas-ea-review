#!/usr/bin/env python3
"""
Resolve what can be resolved about result-specific RoB 2, and produce an
assessment worklist for what cannot.

RoB 2 is a judgement made by assessors, not a value that can be derived from the
data. This script therefore does exactly two things, and refuses the third:

  1. VERIFIED MATCH. Where a row is the *same result* as one that already has a
     result-specific assessment -- same study, same outcome, same timepoint --
     that existing assessment genuinely applies. Linking it is verification, not
     inheritance, and is what the v34 handover permits.

  2. WORKLIST. For everything else, it produces the prioritised list of study x
     result pairs that need assessment, with the domain-relevant evidence
     already pulled out of the data (analysis population, allocation, source
     location) so a human assessor starts from the evidence rather than from a
     blank form.

  3. It does NOT invent domain judgements. Cochrane RoB 2 requires two
     independent assessors reaching consensus, and this review reports their
     judgements under their names. Generating 668 assessments here would be
     fabricating the review's central quality appraisal.

A study-wide judgement is never copied onto a different result: that is the
specific error the handover names.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
OUTCOME = DATA / "v34_outcome_data.csv"
MANIFEST = ROOT / "09_V34_ANALYSIS" / "01_DATA" / "v34_model_manifest.csv"
OUT = ROOT / "09_V34_ANALYSIS"


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def norm(v) -> str:
    return " ".join((v or "").split()).strip().lower()


def main() -> int:
    rows = read(OUTCOME)
    status_col = "V34 RoB2 status"

    assessed, pending = [], []
    for r in rows:
        s = (r.get(status_col) or "").strip()
        if s.startswith("EXISTING"):
            assessed.append(r)
        elif "PENDING" in s:
            pending.append(r)

    print(f"outcome rows            : {len(rows)}")
    print(f"already assessed        : {len(assessed)}")
    print(f"pending assessment      : {len(pending)}\n")

    # ── 1. verified exact matches ─────────────────────────────────────────
    # Key on study + outcome + timepoint. Outcome family alone is far too
    # coarse: "GI recovery" covers flatus, defecation and bowel sounds, which
    # are different results with different measurement problems.
    index = {}
    for r in assessed:
        key = (norm(r.get("Canonical study")), norm(r.get("Outcome/result")),
               norm(r.get("Timepoint/window")))
        index[key] = r

    matched, unmatched = [], []
    for r in pending:
        key = (norm(r.get("Canonical study")), norm(r.get("Outcome/result")),
               norm(r.get("Timepoint/window")))
        src = index.get(key)
        if src:
            matched.append(dict(
                study=r.get("Canonical study"), outcome=r.get("Outcome/result"),
                timepoint=r.get("Timepoint/window"),
                matched_status=(src.get(status_col) or "").strip(),
                basis="exact study + outcome + timepoint match to an existing "
                      "result-specific assessment"))
        else:
            unmatched.append(r)

    print(f"verified exact matches  : {len(matched)}")
    print(f"still needing assessment: {len(unmatched)}\n")

    # ── 2. worklist, prioritised by whether the result is actually analysed ──
    # The set that actually blocks GRADE is the rows INSIDE a fitted model, not
    # every row belonging to a study that happens to appear in one. Read the
    # model datasets directly so the priority reflects the real dependency.
    in_model = set()
    for ds in sorted((ROOT / "09_V34_ANALYSIS" / "01_DATA").glob("*.csv")):
        if ds.name == "v34_model_manifest.csv":
            continue
        for r in read(ds):
            in_model.add((norm(r.get("study")), norm(r.get("outcome")),
                          norm(r.get("window"))))
    for ds in sorted(DATA.glob("v34_primary_24h_mme_*.csv")) + \
              sorted(DATA.glob("v34_intraop_*.csv")) + \
              sorted(DATA.glob("v34_qor40_24h_*.csv")) + \
              sorted(DATA.glob("v34_gi_first_defecation_*.csv")):
        for r in read(ds):
            in_model.add((norm(r.get("study")), norm(r.get("outcome")),
                          norm(r.get("window"))))

    work = defaultdict(lambda: dict(rows=0, records=[]))
    for r in unmatched:
        study = r.get("Canonical study") or ""
        key = (study, r.get("Outcome/result") or "", r.get("Timepoint/window") or "")
        w = work[key]
        w["rows"] += 1
        w["records"].append(r)

    out = []
    for (study, outcome, tp), w in work.items():
        r0 = w["records"][0]
        contributes = (norm(study), norm(outcome), norm(tp)) in in_model
        out.append(dict(
            priority="1 - inside a fitted model" if contributes else "2 - not currently pooled",
            study=study, outcome=outcome, timepoint=tp,
            outcome_family=r0.get("Outcome family", ""),
            rows=w["rows"],
            data_type=r0.get("Data type", ""),
            analysed_n_i=r0.get("Analyzed n intervention", ""),
            analysed_n_c=r0.get("Analyzed n comparator", ""),
            randomised_n_i=r0.get("Randomized n intervention", ""),
            randomised_n_c=r0.get("Randomized n comparator", ""),
            intervention=r0.get("Intervention arm", ""),
            comparator=r0.get("Comparator arm", ""),
            source_location=r0.get("Source location", ""),
            source_qc=r0.get("Source-QC issue", ""),
            eligibility=r0.get("V34 eligibility", ""),
            status="ROB2_RESULT_SPECIFIC_PENDING",
        ))

    out.sort(key=lambda r: (r["priority"], r["study"], r["outcome"]))
    p = OUT / "v34_rob2_worklist.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    if matched:
        mp = OUT / "v34_rob2_verified_matches.csv"
        with mp.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(matched[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(matched)
        print(f"wrote {mp.relative_to(ROOT)}")

    p1 = [r for r in out if r["priority"].startswith("1")]
    print(f"distinct study x result pairs needing assessment: {len(out)}")
    print(f"  priority 1 (contributes to a fitted model)    : {len(p1)}")
    print(f"  priority 2 (not currently pooled)             : {len(out) - len(p1)}\n")

    print("PRIORITY 1 -- rows inside a fitted model; these block GRADE:")
    for r in p1:
        print(f"  {r['study']:<26} {r['outcome'][:44]:<44} @ {r['timepoint'][:20]}")

    print(f"\nby outcome family (all priorities):")
    for fam, n in Counter(r["outcome_family"] for r in out).most_common(10):
        print(f"  {n:>4}  {fam}")

    print(f"\nwrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
