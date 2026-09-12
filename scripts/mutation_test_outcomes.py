#!/usr/bin/env python3
"""
Mutation tests for the outcome-register guards (incident 2026-09-10).

A validator that has never been shown to fail is not evidence of anything. Each
mutation below corrupts dashboard/data.js in one specific way that this incident
proved is possible, runs scripts/validate_dashboard.py, and requires that it
fails AND that the failure text names the right problem. The file is restored
after every case and the suite verifies the restored tree still passes.

Cases 1-12 are the failure modes required by the remediation brief. Cases 13-16
are regressions for the specific studies this incident turned up.

Usage:  python3 scripts/mutation_test_outcomes.py [-v]
Exit:   0 every mutation was caught, 1 otherwise
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "dashboard" / "data.js"
VERBOSE = "-v" in sys.argv

GREEN, RED, DIM, BOLD, RESET = "\033[92m", "\033[91m", "\033[2m", "\033[1m", "\033[0m"


def load():
    raw = DATA_JS.read_text(encoding="utf-8")
    head, body = raw.split("window.STUDIES_DATA = ", 1)
    studies, end = json.JSONDecoder().raw_decode(body)
    return head, studies, body[end:]


def write(head, studies, tail):
    DATA_JS.write_text(
        head + "window.STUDIES_DATA = "
        + json.dumps(studies, ensure_ascii=False, indent=2) + tail,
        encoding="utf-8")


def rec(studies, key, bucket):
    for s in studies:
        if s["key"] == key:
            return s["outcomes"][bucket]
    raise KeyError(f"{key}/{bucket} not found")


def run_validator() -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(ROOT / "scripts/validate_dashboard.py")],
                       capture_output=True, text=True, cwd=ROOT)
    return p.returncode, re.sub(r"\033\[[0-9;]*m", "", p.stdout + p.stderr)


# Each case: (name, mutate(studies) -> None, expected substring in the failure)
def _set(key, bucket, field, value):
    def go(studies):
        rec(studies, key, bucket)[field] = value
    return go


CASES = [
    ("1. wrong mean",
     _set("Guo 2023", "intraop_opioid", "arm1_mean", 871.0),
     "generated from the lock"),
    ("2. wrong SD",
     _set("Pan 2023", "intraop_opioid", "arm1_sd", 300.0),
     "generated from the lock"),
    ("3. wrong n",
     _set("Wu 2022", "intraop_opioid", "arm1_n", 30),
     "generated from the lock"),
    ("4. wrong event count",
     _set("Yu 2020", "rescue_analgesia", "arm1_events", 5),
     "generated from the lock"),
    ("5. wrong denominator",
     _set("Tu 2024", "rescue_analgesia", "arm1_n", 77),
     "generated from the lock"),
    ("6. wrong unit",
     _set("Ng 2013", "flatus_time", "unit", "days"),
     "is not the pooled unit"),
    ("7. wrong timepoint (comparison_id swapped)",
     _set("Xing 2022", "flatus_time", "comparison_id", "XING22_NTG_vs_G_FLATUS"),
     "generated from the lock"),
    ("8. reversed intervention/control",
     lambda studies: rec(studies, "Lu 2022", "flatus_time").update(
         arm1_mean=42.4, arm1_sd=22.9, arm2_mean=34.5, arm2_sd=16.7),
     "generated from the lock"),
    ("9. stale mean_diff",
     _set("Zheng 2025", "intraop_opioid", "mean_diff", -70.0),
     "!= "),
    ("10. wrong favors",
     _set("Liang 2021", "intraop_opioid", "favors", "Intervention"),
     "contradicts mean_diff"),
    ("11. unsupported record where the lock has none",
     lambda studies: rec(studies, "Xie 2014", "opioid_48h").update(
         arm1_mean=115.0, arm1_sd=6.0, arm1_n=20, arm2_mean=133.5,
         arm2_sd=7.0, arm2_n=20, mean_diff=-18.5, se=2.06),
     "generated from the lock"),
    ("12. placeholder-like tuple restored",
     lambda studies: rec(studies, "Yang 2024", "flatus_time").update(
         arm1_mean=83.0, arm1_sd=12.0, arm1_n=90, arm2_mean=85.0,
         arm2_sd=12.0, arm2_n=90, mean_diff=-2.0, se=1.7889,
         ci_low=-5.5062, ci_upp=1.5062),
     "superseded placeholder"),
    # ── incident regressions ────────────────────────────────────────────────
    ("13. Liang 2021 direction reversal",
     lambda studies: rec(studies, "Liang 2021", "intraop_opioid").update(
         arm1_mean=464.7, arm1_sd=156.0, arm2_mean=521.5, arm2_sd=206.8,
         mean_diff=-56.8, favors="Intervention"),
     "generated from the lock"),
    ("14. Ng 2013 fabricated day->hour narrative",
     _set("Ng 2013", "flatus_time", "converted_from",
          "1.33 ± 0.36 vs 1.34 ± 0.37 days (x24)"),
     "generated from the lock"),
    ("15. Tu 2024 randomised-vs-analysed denominator mix-up",
     lambda studies: rec(studies, "Tu 2024", "rescue_analgesia").update(
         arm1_n=77, arm2_n=76, arm1_events=9, arm2_events=17),
     "generated from the lock"),
    ("16. Zheng 2025 magnitude discrepancy",
     lambda studies: rec(studies, "Zheng 2025", "intraop_opioid").update(
         arm1_mean=750.0, arm1_sd=180.0, arm2_mean=820.0, arm2_sd=190.0),
     "superseded placeholder"),
    ("17. events exceed their denominator",
     lambda studies: rec(studies, "Xie 2014", "rescue_analgesia").update(arm1_events=99),
     "exceed denominator"),
]


def main() -> int:
    original = DATA_JS.read_text(encoding="utf-8")
    print("=" * 78)
    print(f"{BOLD}  OUTCOME-REGISTER MUTATION TESTS{RESET}")
    print("=" * 78)

    rc, out = run_validator()
    if rc != 0:
        print(f"{RED}ABORT{RESET} | the tree fails validation before any mutation")
        print(out[-1500:])
        return 1
    print(f"{GREEN}BASE{RESET} | clean tree passes validation\n")

    failures = []
    try:
        for name, mutate, expect in CASES:
            head, studies, tail = load()
            try:
                mutate(studies)
            except KeyError as exc:
                failures.append(f"{name}: could not apply ({exc})")
                print(f"{RED}ERROR{RESET}| {name}: {exc}")
                continue
            write(head, studies, tail)
            rc, out = run_validator()
            DATA_JS.write_text(original, encoding="utf-8")

            if rc == 0:
                failures.append(f"{name}: NOT CAUGHT")
                print(f"{RED}MISS{RESET} | {name}")
            elif expect not in out:
                failures.append(f"{name}: caught but message lacks {expect!r}")
                print(f"{RED}MSG{RESET}  | {name} — expected {expect!r}")
                if VERBOSE:
                    print(DIM + "\n".join(l for l in out.splitlines()
                                          if "FAIL" in l or l.startswith("       "))[:900] + RESET)
            else:
                print(f"{GREEN}CAUGHT{RESET}| {name}")
                if VERBOSE:
                    line = next((l for l in out.splitlines() if expect in l), "")
                    print(f"       {DIM}{line.strip()[:150]}{RESET}")
    finally:
        DATA_JS.write_text(original, encoding="utf-8")

    rc, _ = run_validator()
    print()
    if rc != 0:
        print(f"{RED}RESTORE FAILED{RESET} | data.js did not return to a passing state")
        return 1
    print(f"{GREEN}RESTORED{RESET} | clean tree passes validation again")

    print("=" * 78)
    if failures:
        print(f"{RED}{BOLD}FAILED{RESET}  {len(CASES) - len(failures)}/{len(CASES)} mutations caught")
        for f in failures:
            print(f"  {RED}x{RESET} {f}")
        return 1
    print(f"{GREEN}{BOLD}ALL {len(CASES)} MUTATIONS CAUGHT{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
