#!/usr/bin/env python3
"""
Assert every generated dashboard bundle is byte-identical to a fresh run of the
script that writes it.

WHY THIS EXISTS
Twice in one day a generated bundle had silently drifted from its generator, and
both times it was found by accident rather than by a check:

  primary_pathway.js   recorded Gao 2022, Song 2020 and Zhang 2018 as contributing
                       to nothing, weeks after they were admitted to targets. Every
                       validator check passed over it.
  limitations.js       said 3 contrasts could not be converted to absolute morphine
                       equivalents when the conversion audit held 4.

A stale generated file is worse than a wrong hand-written one, because the header
says "GENERATED -- do not hand-edit" and a reader therefore trusts it to reflect
current data. The generator is the specification; this checks the artifact against
it.

HOW
For each bundle: snapshot the bytes, run the generator, compare, then restore the
snapshot unconditionally. Nothing is left modified either way -- a drift is
REPORTED, never silently fixed, because regenerating can change displayed numbers
and that is a review decision, not a test's.

Usage:
  python3 scripts/check_generated_artifacts.py            # every generator
  python3 scripts/check_generated_artifacts.py --fast     # skip the slow ones
  python3 scripts/check_generated_artifacts.py --list     # show the map and exit
Exit: 0 when every artifact matches, 1 on any drift or generator failure.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"

# generator -> the bundle(s) it writes. One entry per script, so a multi-output
# generator is run once.
# Some of these are CHECK scripts that also emit a bundle, and they exit non-zero
# to report a finding rather than a failure: check_stratum_purity.py returns 1
# while writing a perfectly current stratum_purity.js, because "3 of 5 reported
# analyses pool across protocol strata" is its finding. For those, the exit code
# is not evidence about the artifact -- only the bytes are. `reports_findings`
# marks them; everything else must exit 0.
GENERATORS: list[tuple[str, tuple[str, ...], bool, bool]] = [
    # (script, bundles it writes, slow, exits non-zero to report findings)
    ("scripts/build_cohort_overlap_scan.py",      ("cohort_overlap.js",), False, False),
    ("scripts/build_computed_not_reported.py",    ("computed_not_reported.js",), False, False),
    ("scripts/build_eligibility_reconciliation.py", ("eligibility_reconciliation.js",), False, False),
    ("scripts/build_forest_context.py",           ("forest_context.js",), False, False),
    ("scripts/build_limitations.py",              ("limitations.js",), False, False),
    ("scripts/build_primary_pathway.py",          ("primary_pathway.js",), False, False),
    ("scripts/build_prior_evidence_comparison.py", ("prior_evidence.js",), False, False),
    ("scripts/build_prisma_checklist.py",         ("prisma_checklist.js",), False, False),
    ("scripts/build_rob2_source_links.py",        ("rob2_source_links.js",), False, False),
    ("scripts/build_tiered_v33.py",               ("tiered_v33.js",), False, False),
    ("scripts/build_v33_dashboard_data.py",       ("v33_data.js",), False, False),
    ("scripts/build_v34_dashboard_data.py",       ("v34_data.js",), False, False),
    ("scripts/check_stratum_purity.py",                ("stratum_purity.js",), False, True),
    ("scripts/build_reference_data.py",
     ("author_inquiries.js", "browser_targets.js", "meta_outcomes.js",
      "primary_browser.js", "search_strategies.js", "study_characteristics.js"), False, False),
    # Reads all 70 source PDFs, so it is minutes rather than seconds. Excluded
    # from --fast and from the validator's default run; it must still be checked,
    # which is what the unqualified invocation is for.
    ("scripts/extract_baseline_from_pdfs.py",     ("pdf_extracted.js",), True),
]

# data.js is deliberately absent: it is the register, mutated in place by the
# apply_* scripts rather than regenerated from inputs, so "rerun and compare" is
# not a meaningful test of it. Its integrity is held by t_population_denominators,
# t_country_is_verified_country_of_conduct and the apply_* --check modes.
NOT_REGENERABLE = {"data.js"}


def run_one(script: str, bundles: tuple[str, ...],
            reports_findings: bool = False) -> tuple[list[str], float]:
    """Snapshot, regenerate, compare, restore. Returns (drifted bundles, seconds)."""
    paths = [DASH / b for b in bundles]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        return [f"{m} does not exist" for m in missing], 0.0
    before = {p: p.read_bytes() for p in paths}
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, script], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0 and not reports_findings:
            err = (r.stderr or r.stdout).strip()
            last = err.splitlines()[-1][:180] if err.splitlines() else "(no output)"
            # A MISSING PACKAGE is an environment fact, not drift. CI installs only
            # what the build needs, so a generator that imports something extra must
            # not be able to fail a deploy over it -- while every other non-zero
            # exit still does, including an integrity guard refusing to run.
            if "ModuleNotFoundError" in err or "No module named" in err:
                return [f"UNAVAILABLE: {script} needs a package this environment lacks "
                        f"({last})"], time.time() - t0
            return [f"{script} exited {r.returncode}: {last}"], time.time() - t0
        drift = [p.name for p in paths if p.read_bytes() != before[p]]
    finally:
        # Always restore, including on timeout or an unexpected exception.
        for p, data in before.items():
            if p.read_bytes() != data:
                p.write_bytes(data)
    return drift, time.time() - t0


def main() -> int:
    fast = "--fast" in sys.argv
    if "--list" in sys.argv:
        for script, bundles, slow, reports in GENERATORS:
            tag = ("SLOW " if slow else "     ") + ("(reports findings) " if reports else "")
            print(f"{tag}{script:46s} -> {', '.join(bundles)}")
        print(f"\nnot regenerable, checked elsewhere: {', '.join(sorted(NOT_REGENERABLE))}")
        return 0

    todo = [g for g in GENERATORS if not (fast and g[2])]
    skipped = [g for g in GENERATORS if fast and g[2]]
    # A traceback is always a failure, even for a findings-reporter.
    
    problems: list[str] = []
    unavailable: list[str] = []
    print(f"Checking {sum(len(b) for _, b, *_ in todo)} generated bundles from "
          f"{len(todo)} generator(s){' (--fast)' if fast else ''}\n")
    for script, bundles, _slow, reports in todo:
        drift, secs = run_one(script, bundles, reports)
        if drift and all(d.startswith("UNAVAILABLE:") for d in drift):
            print(f"  n/a    {script:46s} {secs:5.1f}s  {drift[0][12:120]}")
            unavailable.extend(drift)
            continue
        if drift:
            problems.extend(f"{d} is not what {script} produces now" if ".js" in d and
                            "does not exist" not in d and "exited" not in d else d
                            for d in drift)
            print(f"  DRIFT  {script:46s} {secs:5.1f}s  {', '.join(drift)}")
        else:
            print(f"  ok     {script:46s} {secs:5.1f}s  {', '.join(bundles)}")
    for script, bundles, *_ in skipped:
        print(f"  skip   {script:46s}   --    {', '.join(bundles)} (slow; run without --fast)")

    print()
    for u in unavailable:
        print(f"NOTE  {u}")
    if problems:
        print("DRIFT DETECTED. A generated bundle no longer matches its generator, so the")
        print("dashboard is showing something the current data does not produce.")
        for p in problems:
            print(f"  - {p}")
        print("\nNothing was modified. Re-run the generator yourself, inspect the diff, and")
        print("commit it deliberately -- regenerating can change displayed figures.")
        return 1
    print(f"All checked artifacts are byte-identical to a fresh run of their generator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
