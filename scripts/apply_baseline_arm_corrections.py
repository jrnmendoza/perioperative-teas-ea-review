#!/usr/bin/env python3
"""
Apply the source-verified baseline corrections recorded by the cohort-overlap scan.

WHAT IT DOES
scripts/build_cohort_overlap_scan.py records baseline rows found, against the
source publication, to sit on the wrong arm. Each entry names the field, what the
register held, and what the paper says. This applies the paper's value to every
entry marked "corrected", and nothing else.

WHAT IT REFUSES TO DO
Only descriptive baseline fields may move -- age, BMI, sex, ASA. An analysed or
randomised denominator is never written, and the script aborts if one would
change. Those are the values the syntheses read, they trace to
Outcome_Data_AF_LOCK, and a baseline correction has no business touching them.

An entry still marked "open" is left alone: it has not been signed off.

Usage:  python3 scripts/apply_baseline_arm_corrections.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "dashboard" / "data.js"
SCAN_JS = ROOT / "dashboard" / "cohort_overlap.js"

ALLOWED = re.compile(r"^(arm[12]_(age|bmi|female)|asa_status)$")
FROZEN = ("arm1_n", "arm2_n", "total_n",
          "randomized_arm1_n", "randomized_arm2_n", "randomized_total_n")


def _corrections() -> list[dict]:
    raw = SCAN_JS.read_text(encoding="utf-8")
    scan = json.JSONDecoder().raw_decode(raw.split("window.COHORT_OVERLAP = ", 1)[1])[0]
    return [s for s in scan.get("baseline_corrections", []) if s.get("status") == "corrected"]


def _register():
    raw = DATA_JS.read_text(encoding="utf-8")
    head, body = raw.split("window.STUDIES_DATA = ", 1)
    studies, end = json.JSONDecoder().raw_decode(body)
    return head, studies, body[end:]


def _targets(entry: dict) -> dict[str, str]:
    out = {f["field"]: f["source_says"] for f in entry.get("fields", [])}
    if entry.get("asa_status"):
        out["asa_status"] = entry["asa_status"]["source_says"]
    return out


def main(check_only: bool) -> int:
    head, studies, tail = _register()
    by_key = {s["key"]: s for s in studies}
    entries = _corrections()
    if not entries:
        print("no signed-off baseline corrections to apply")
        return 0

    stale, changed = [], []
    for entry in entries:
        rec = by_key.get(entry["study"])
        if rec is None:
            stale.append(f"{entry['study']}: not in the register")
            continue
        pop = rec["population"]
        before = {f: pop.get(f) for f in FROZEN}
        for field, value in _targets(entry).items():
            if not ALLOWED.match(field):
                raise SystemExit(f"{entry['study']}.{field} is not a baseline field; refusing")
            if pop.get(field) != value:
                if check_only:
                    stale.append(f"{entry['study']}.{field} is {pop.get(field)!r}, "
                                 f"expected the source value {value!r}")
                else:
                    changed.append(f"{entry['study']}.{field}: {pop.get(field)!r} -> {value!r}")
                    pop[field] = value
        after = {f: pop.get(f) for f in FROZEN}
        if before != after:
            raise SystemExit(f"{entry['study']}: a denominator moved ({before} -> {after}); "
                             "a baseline correction must never touch one")

    if check_only:
        if stale:
            print("OUT OF DATE:", file=sys.stderr)
            for s in stale:
                print(f"  {s}", file=sys.stderr)
            return 1
        print(f"{len(entries)} signed-off baseline correction(s) are applied in the register")
        return 0

    DATA_JS.write_text(head + "window.STUDIES_DATA = "
                       + json.dumps(studies, ensure_ascii=False, indent=2) + tail,
                       encoding="utf-8")
    print(f"applied {len(changed)} baseline value(s)")
    for c in changed:
        print(f"  {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
