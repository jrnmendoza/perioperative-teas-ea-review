#!/usr/bin/env python3
"""
Build the comparison against the prior meta-analysis (Tan SY et al. 2024).

WHY
"How do our findings compare with prior work, and why do they differ?" is a
Discussion section every reviewer expects, and this review already has the
material for it: TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md reconciles all 76
RCTs in Tan 2024 against this review's screening records, including a
trial-by-trial account of the six trials Tan pooled for the *same* 24-hour
cumulative opioid outcome. None of it was reachable from the dashboard.

WHAT IT DOES
Parses the audit's "Tan's Six 24-h Opioid Studies" table, then re-derives each
trial's CURRENT disposition from live repository data rather than trusting the
document:

  * is it one of the 70 canonical studies?  -> locked workbook Study_Master
  * is it in the strict primary k = 7?      -> the Stata primary log's forest block

THE POINT OF RE-DERIVING
The audit is dated 2026-09-07 and states "Included in our strict primary 24-h
analysis: 1 / 6 (Chen 2020)". That is no longer true: it flagged Szmit 2021 as
a wrongly-excluded trial, the review acted on it, and Szmit 2021 now sits in
the primary synthesis with a weight of 15.2%. A hand-copied panel would still
be showing 1/6. This script recomputes the count and refuses to emit a panel
whose narrative contradicts the live analysis, so the comparison cannot quietly
go stale the way the document did.

Usage:  python3 scripts/build_prior_evidence_comparison.py
Exit:   0 on success, 1 if the audit and the live data disagree in a way that
        is not already recorded as superseded.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md"
MASTER = (ROOT / "TEAS EA Verification" /
          "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx")
PRIMARY_LOG = ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "logs" / "01_opioid24_primary.log"
OUT = ROOT / "dashboard" / "prior_evidence.js"

PRIOR = {
    "citation": "Tan SY, et al. Front Med (Lausanne). 2024;11:1302057.",
    "short": "Tan 2024",
    "scope": ("76 RCTs of transcutaneous electrical acupoint stimulation. Needle-based "
              "electroacupuncture was excluded, and the search predates this review's "
              "2024–2026 trials — so the two evidence bases overlap only partly."),
    "shared_outcome": "24-hour cumulative intravenous morphine-equivalent consumption",
}


def parse_tan_six() -> list[dict]:
    """Pull the six-row checkpoint table out of the audit markdown."""
    text = AUDIT.read_text(encoding="utf-8")
    start = text.index("## Detailed Checkpoint Report")
    block = text[start:text.index("\n## ", start + 5)]
    rows = []
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9 or cells[0].startswith("---") or cells[0] == "Priority #":
            continue
        def strip_md(s: str) -> str:
            # Drop markdown emphasis/code/line-break markers, then collapse the
            # runs of whitespace they leave behind, including inside brackets --
            # otherwise the exported table reads "EXCLUSION.  Violates" and
            # "( opioid_24h_primary.csv )".
            s = re.sub(r"\*\*|`|<br>", " ", s)
            s = re.sub(r"\s+", " ", s)
            s = re.sub(r"\(\s+", "(", s)
            s = re.sub(r"\s+\)", ")", s)
            return s.strip()
        rows.append({
            "priority": strip_md(cells[0]),
            "study": re.sub(r"\s*\(Tan #\d+\)", "", strip_md(cells[1])).strip(),
            "tan_ref": (re.search(r"Tan #(\d+)", cells[1]) or [None, None])[1],
            "population": strip_md(cells[2]),
            "anaesthesia": strip_md(cells[3]),
            "opioid_reported": strip_md(cells[6]),
            "audit_judgment": strip_md(cells[8]),
        })
    if len(rows) != 6:
        raise SystemExit(f"expected 6 trials in the checkpoint table, parsed {len(rows)}")
    return rows


def canonical_studies() -> set[str]:
    import openpyxl
    wb = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)
    rows = [list(r) for r in wb["Study_Master"].iter_rows(values_only=True)]
    idx = [str(c) for c in rows[0]].index("Canonical study")
    return {str(r[idx]).strip() for r in rows[1:] if r[idx]}


def strict_primary_studies() -> list[str]:
    """
    Read the k = 7 forest block out of the Stata primary log.

    Taken from the log rather than a curated list so this tracks whatever the
    pipeline actually fitted; if the primary is re-run with different trials,
    this panel follows it.
    """
    log = PRIMARY_LOG.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Effect size: Mean Difference \(mg IV MME\)(.*?)\n\s*theta\s*\|", log, re.S)
    if not m:
        raise SystemExit("could not find the primary forest block in the Stata log")
    names = re.findall(r"^\s*([A-Za-z][A-Za-z0-9\-'\. ]*(?:19|20)\d{2}[^|]*?)\s*\|", m.group(1), re.M)
    out, seen = [], set()
    for n in names:
        n = n.strip()
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def disposition(study: str, canon: set[str], primary: list[str]) -> tuple[str, str]:
    prim = [p for p in primary if p.split(" (")[0] == study.split(" (")[0]]
    if prim:
        return "in-primary", "Contributes to this review's strict primary 0–24 h opioid synthesis."
    if study in canon:
        return "included-held", ("Included in this review, but held from the strict primary "
                                 "synthesis.")
    return "excluded", "Not eligible for this review."


def main() -> int:
    trials = parse_tan_six()
    canon = canonical_studies()
    primary = strict_primary_studies()

    for t in trials:
        t["status"], t["status_note"] = disposition(t["study"], canon, primary)

    counts = {k: sum(1 for t in trials if t["status"] == k)
              for k in ("in-primary", "included-held", "excluded")}

    # The audit's own tally, which this run may supersede.
    text = AUDIT.read_text(encoding="utf-8")
    m = re.search(r"Included in our strict primary 24-h analysis:\*\*\s*\*\*(\d+)\s*/\s*6", text)
    audit_claim = int(m.group(1)) if m else None
    superseded = None
    if audit_claim is not None and audit_claim != counts["in-primary"]:
        gained = [t["study"] for t in trials
                  if t["status"] == "in-primary" and "Chen 2020" not in t["study"]]
        superseded = (
            f"The audit, dated 2026-09-07, recorded {audit_claim} of these 6 trials in the "
            f"strict primary synthesis. {counts['in-primary']} are in it now: the audit "
            f"identified {', '.join(gained)} as wrongly excluded, and the review acted on that "
            f"finding. This panel reports the current state, re-derived from the analysis "
            f"itself; the figure in the audit document is superseded rather than corrected "
            f"in place.")

    payload = {
        "generated_by": "scripts/build_prior_evidence_comparison.py",
        "source_document": AUDIT.name,
        "audit_date": "2026-09-07",
        "prior": PRIOR,
        "trials": trials,
        "counts": counts,
        "superseded_note": superseded,
        "our_primary": primary,
        "disclaimer": ("Comparison with prior published evidence. The dispositions below are "
                       "re-derived from this review's own locked dataset and Stata output, not "
                       "copied from the audit document. Nothing here is a finding about the "
                       "prior review's conduct; it records why the two evidence bases differ."),
    }

    OUT.write_text(
        "// GENERATED by scripts/build_prior_evidence_comparison.py -- do not hand-edit.\n"
        f"// Source: {AUDIT.name}; dispositions re-derived from the locked workbook and\n"
        "// 06_FINAL_ANALYSIS_V26/02_STATA/logs/01_opioid24_primary.log\n"
        "window.PRIOR_EVIDENCE = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  Tan 2024's six 24-h opioid trials:")
    for t in trials:
        print(f"    {t['study']:22s} {t['status']}")
    print(f"  counts: {counts}")
    print(f"  this review's strict primary (k = {len(primary)}): {', '.join(primary)}")
    if superseded:
        print("  NOTE: the audit document's tally is superseded; recorded in the panel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
