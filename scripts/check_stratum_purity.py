#!/usr/bin/env python3
"""
Check that no pooled analysis crosses the protocol's modality or comparator
boundaries.

WHY THIS EXISTS
The locked protocol scope is explicit on both points:

    "TEAS and EA analyses are stratified by modality."
    "Usual perioperative care, standard multimodal analgesia, no stimulation,
     waiting-list control, and attention control are supportive comparisons and
     remain separate from sham-controlled evidence."

and PROSPERO's synthesis strategy says "TEAS and electroacupuncture (EA) will
not be combined in a pooled estimate."

Several v26 analyses pool on `endpoint_stratum` alone -- see the `meta summarize
if endpoint_stratum == ...` lines in 05_ponv.do and the unfiltered pool in
06_flatus.do -- which applies no modality or comparator condition at all. A
second-reviewer report raised this for the unreported nausea/vomiting
components; checking it showed the same pattern in reported, GRADE-rated
analyses.

WHAT IT DOES
Reads the studies each analysis ACTUALLY pooled out of the Stata logs -- not the
candidate pool, and not a label -- then resolves each contributing contrast's
modality and comparator class and reports any analysis containing more than one
(modality, comparator) combination.

Modality is a property of the trial. Comparator is a property of the CONTRAST:
a three-arm trial contributes a sham contrast to one analysis and a usual-care
contrast to another, so comparator is read per stratum-and-study, never per
study.

Usage:  python3 scripts/check_stratum_purity.py [--json]
Exit:   0 if every pooled analysis is pure, 1 otherwise.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V26 = ROOT / "06_FINAL_ANALYSIS_V26"
LOGS = V26 / "02_STATA" / "logs"
LOCKED = V26 / "01_DATA" / "analysis_dataset_locked.csv"
OUTCOME = (ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data" /
           "v34_outcome_data.csv")

# Reported analyses, the log that produced each, the stratum whose comparators
# apply, and WHICH forest block in that log is the headline analysis.
#
# The block index matters: 05_ponv.do fits four analyses into one log, in
# do-file order, and later blocks in other logs are leave-one-out or
# sensitivity re-fits of the same set rather than new analyses. Taking the
# first block everywhere made AN-06 read AN-05's members and report itself
# clean.
REPORTED = {
    "AN-02-TARGET-A":    ("02_targetA_48h.log", "A_0-48h_cumulative_opioid", 0),
    "AN-04-TARGET-C":    ("04_pain.log",        "C_rest_pain_~24h",          0),
    "AN-05-TARGET-D-24": ("05_ponv.log",        "D_PONV_0-24h",              0),
    "AN-06-TARGET-D-48": ("05_ponv.log",        "D_PONV_0-48h",              1),
    "AN-07-TARGET-E":    ("06_flatus.log",      "E_time_to_first_flatus",    0),
}


def comparator_class(text: str) -> str:
    t = (text or "").lower()
    if "sham" in t or "placebo" in t or "no current" in t or "nonpenetrating" in t:
        return "Sham"
    if any(w in t for w in ("usual", "no teas", "no stim", "standard", "control",
                            "pca alone", "no acupuncture")):
        return "Usual care"
    return f"UNCLASSIFIED ({text})"


def modality_by_study() -> dict:
    mod = {}
    with OUTCOME.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            s, m = r.get("Canonical study"), r.get("V34 modality")
            if s and m and s not in mod:
                mod[s] = m
    return mod


def contrasts_by_stratum() -> dict:
    """(endpoint_stratum, study) -> comparator text, from the locked dataset."""
    out = {}
    with LOCKED.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = (r.get("endpoint_stratum"), r.get("study"))
            out.setdefault(key, r.get("comparator"))
    return out


def pooled_members(log: Path, block: int) -> list[str]:
    """Studies in the Nth forest block of a Stata log (0-indexed)."""
    text = log.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r"Study \|.*?theta", text, re.S)
    if block >= len(blocks):
        return []
    names = re.findall(r"^\s*([A-Za-z][A-Za-z0-9 '()/\-]*?)\s*\|", blocks[block], re.M)
    return [n.strip() for n in names if n.strip() and n.strip() != "Study"]


def audit() -> dict:
    mod = modality_by_study()
    contrasts = contrasts_by_stratum()
    findings = []
    for aid, (logname, stratum, block) in sorted(REPORTED.items()):
        log = LOGS / logname
        if not log.exists():
            findings.append({"analysis_id": aid, "error": f"log not found: {logname}"})
            continue
        members = pooled_members(log, block)
        rows = []
        for s in members:
            comp = contrasts.get((stratum, s))
            if comp is None:  # log labels can differ slightly from the dataset
                comp = next((v for (st, st_s), v in contrasts.items()
                             if st == stratum and st_s.startswith(s.split(" (")[0])), None)
            rows.append({"study": s,
                         "modality": mod.get(s, "UNRESOLVED"),
                         "comparator": comparator_class(comp) if comp else "UNRESOLVED"})
        combos = {(r["modality"], r["comparator"]) for r in rows}
        findings.append({
            "analysis_id": aid, "k": len(rows), "stratum": stratum,
            "contributors": rows,
            "distinct_strata": sorted(f"{m} vs {c}" for m, c in combos),
            "pure": len(combos) <= 1 or len(rows) <= 1,
        })
    impure = [f for f in findings if not f.get("pure", True)]
    return {"findings": findings, "impure": impure}


OUT = ROOT / "dashboard" / "stratum_purity.js"

PROTOCOL_QUOTES = [
    ("Locked protocol scope, Outcomes and synthesis boundary",
     "TEAS and EA analyses are stratified by modality. Principal sham-controlled "
     "and supportive non-sham comparisons remain separate."),
    ("Locked protocol scope, Comparators and analytic separation",
     "Usual perioperative care, standard multimodal analgesia, no stimulation, "
     "waiting-list control, and attention control are supportive comparisons and "
     "remain separate from sham-controlled evidence."),
    ("PROSPERO, Strategy for data synthesis",
     "TEAS and electroacupuncture (EA) will not be combined in a pooled estimate. "
     "Analyses will be stratified by modality."),
]


def write_payload(result: dict) -> None:
    payload = {
        "generated_by": "scripts/check_stratum_purity.py",
        "protocol": [{"source": s, "quote": q} for s, q in PROTOCOL_QUOTES],
        "note": ("Each analysis's contributing studies are read from the Stata log that "
                 "produced it, then each contrast's modality and comparator class are "
                 "resolved. An analysis containing more than one (modality, comparator) "
                 "combination pools across a boundary the protocol keeps separate."),
        "findings": result["findings"],
        "impure_ids": [f["analysis_id"] for f in result["impure"]],
    }
    OUT.write_text(
        "// GENERATED by scripts/check_stratum_purity.py -- do not hand-edit.\n"
        "// Contributing studies are read from the Stata logs, not from labels.\n"
        "window.STRATUM_PURITY = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")


def main() -> int:
    result = audit()
    write_payload(result)
    for f in result["findings"]:
        if f.get("error"):
            print(f"  {f['analysis_id']}: {f['error']}")
            continue
        mark = "OK   " if f["pure"] else "MIXED"
        print(f"{mark} {f['analysis_id']:22s} k={f['k']}  "
              f"{len(f['distinct_strata'])} stratum/strata")
        if not f["pure"]:
            for r in f["contributors"]:
                print(f"          {r['study']:26s} {r['modality']:5s} vs {r['comparator']}")
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    n = len(result["impure"])
    print(f"\n{n} of {len(result['findings'])} reported analyses pool across "
          f"protocol strata.")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
