#!/usr/bin/env python3
"""
Pre-deployment integrity gate. Runs after scripts/build_site.py, before the
build output is uploaded as a Pages artifact. Exits non-zero (aborting
deployment) if the built site does not carry the current analytical
state, or if it still carries specific superseded claims.

Historical/changelog prose that explicitly discusses a withdrawn or
superseded value (e.g. this audit report describing the v26-era numbers it
replaced) is exempt -- only text outside such blocks is checked, using the
same withdrawal-prose stripper as scripts/validate_dashboard.py.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WITHDRAWAL_MARKERS = (
    "Withdrawn", "withdrawn", "Earlier releases", "previously displayed",
    "previously offered", "previously let readers", "Not modelled in v26",
    "came from the withdrawn", "has been withdrawn", "Removed", "superseded",
    "Superseded", "no k = 11", "not estimable", "is NOT estimable",
    "no pooled result exists", "under reconciliation", "pre-existing",
)


def strip_withdrawal_prose(text: str) -> str:
    out = []
    for para in re.split(r"(?=<(?:li|p|div|td|h2|h3|h4)\b)", text):
        if any(m in para for m in WITHDRAWAL_MARKERS):
            continue
        out.append(para)
    return "".join(out)


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)
    print(f"FAIL: {msg}")


def main() -> int:
    ap_out = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else str(ROOT / "_site")
    site = Path(ap_out)
    failures: list[str] = []

    meta_path = site / "build-meta.json"
    if not meta_path.exists():
        print(f"FAIL: {meta_path} does not exist")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    print("Checking build-meta.json against required values...")

    # Derive the expected outcome-row count and master version from the
    # workbook the build actually used, rather than restating them here. A
    # hardcoded expectation is the same drift hazard as a hardcoded value: this
    # check previously asserted v32/364 and would have blocked every correct
    # v33 deployment while silently blessing a stale one.
    import re as _re
    import openpyxl as _op
    master_file = meta.get("master_file", "")
    m = _re.search(r"_v(\d+)_", master_file)
    expected_version = f"v{m.group(1)}" if m else None
    master_path = ROOT / "TEAS EA Verification" / master_file
    if not master_path.exists():
        fail(f"build-meta names a master that does not exist: {master_file}", failures)
        expected_rows = None
    else:
        expected_rows = _op.load_workbook(master_path, data_only=True)["Outcome_Data"].max_row - 1

    required = {
        "master_version": expected_version,
        "canonical_studies": 70,
        "source_normalized_outcome_rows": expected_rows,
        "strict_primary_opioid_k": 7,
    }
    for key, expected in required.items():
        got = meta.get(key)
        if got != expected:
            fail(f"build-meta.json[{key}] = {got!r}, expected {expected!r}", failures)
        else:
            print(f"  OK  {key} = {got}")

    for key in ("git_commit", "build_timestamp_utc"):
        if not meta.get(key):
            fail(f"build-meta.json[{key}] is missing or empty", failures)

    index_path = site / "index.html"
    app_path = site / "app.js"
    trans_path = site / "translations.js"
    if not index_path.exists():
        fail(f"{index_path} does not exist", failures)
        print(f"\n{len(failures)} integrity check(s) failed. Aborting deployment.")
        return 1

    html = index_path.read_text(encoding="utf-8")
    app_js = app_path.read_text(encoding="utf-8") if app_path.exists() else ""
    trans_js = trans_path.read_text(encoding="utf-8") if trans_path.exists() else ""

    print("\nChecking for superseded claims in live (non-changelog) content...")
    live_html = strip_withdrawal_prose(html).replace("−", "-").replace("&minus;", "-")

    banned_exact = {
        "Reconciled Master v26": "stale v26 branding string",
    }
    for needle, why in banned_exact.items():
        if needle in live_html:
            fail(f"index.html live content contains {needle!r} ({why})", failures)
        else:
            print(f"  OK  {needle!r} absent from live content")

    # An active primary result claiming k=6 (as opposed to a k=6 reference to
    # an unrelated, correct analysis such as Target E's own k=6) is checked
    # narrowly: the specific phrase this project's k=6-era primary synthesis
    # used, "Supporting Combined Synthesis (k=6" / "STRICT DIRECT k=6", must
    # not appear anywhere live.
    banned_context = (
        "Supporting Combined Synthesis (k=6",
        "STRICT DIRECT k=6",
        "Strict Direct Trials (k = 6)",
        "k = 6 RCTs (N = 628",
    )
    for needle in banned_context:
        if needle in live_html or needle in app_js or needle in trans_js:
            fail(f"a k=6-era primary-result phrase is still live: {needle!r}", failures)
        else:
            print(f"  OK  {needle!r} absent from live content")

    build_badge_present = 'id="build-badge"' in html and meta["git_commit"][:8] in html
    if not build_badge_present:
        fail("static build badge (id=\"build-badge\") not found in index.html, or does not "
             "contain the short commit SHA -- crawlers that do not execute JS would see no "
             "build indicator at all", failures)
    else:
        print("  OK  static build badge present with current short SHA")

    if failures:
        print(f"\n{len(failures)} integrity check(s) failed. Aborting deployment.")
        return 1

    print("\nAll deployment integrity checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
