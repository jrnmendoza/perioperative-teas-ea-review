#!/usr/bin/env python3
"""
Post-deployment live verification. Fetches the PUBLIC GitHub Pages URL
(cache-busted) after deployment and confirms the returned content actually
carries the current analytical state -- never assume a deployment
succeeded merely because the workflow step that pushed it returned 0.

Usage:
  python3 scripts/verify_deployment.py --commit <sha> \
      [--base-url https://jrnmendoza.github.io/perioperative-teas-ea-review]

Exit: 0 if all checks pass, 1 otherwise. Retries with backoff since GitHub
Pages' CDN can take a short time to reflect a just-completed deployment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from urllib.error import URLError, HTTPError

DEFAULT_BASE = "https://jrnmendoza.github.io/perioperative-teas-ea-review"
# Presence checks against the raw HTML. The master version is NOT checked by
# literal here -- it is derived from the deployed build-meta below, so this file
# never has to be edited when the master advances.
REQUIRED_TEXT = ()

# Values that must hold for any deployment of this review, whatever the master
# version. Version-specific values are derived from the deployed metadata.
REQUIRED_META = {
    "canonical_studies": 70,
    "strict_primary_opioid_k": 7,
}


def fetch(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        headers = dict(resp.headers.items())
        return resp.status, body, headers



def commit_matches(reported: str | None, wanted: str) -> bool:
    """True when the deployed commit is the one asked for.

    build-meta.json records the full 40-character SHA while --commit is usually
    given as the short SHA that git and the build badge print, so a plain string
    comparison fails a correct deployment. Match on prefix, in whichever
    direction is longer, and require at least 7 characters so a stray short
    string cannot pass.
    """
    if not reported or not wanted:
        return False
    a, b = reported.strip().lower(), wanted.strip().lower()
    if min(len(a), len(b)) < 7:
        return False
    return a.startswith(b) or b.startswith(a)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="commit SHA that was just deployed")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--retries", type=int, default=6)
    ap.add_argument("--retry-delay", type=int, default=20)
    args = ap.parse_args()

    short = args.commit[:8]
    index_url = f"{args.base_url}/index.html?build={args.commit}"
    meta_url = f"{args.base_url}/build-meta.json?build={args.commit}"

    failures: list[str] = []
    meta = None
    headers_index = {}

    for attempt in range(1, args.retries + 1):
        print(f"[attempt {attempt}/{args.retries}] fetching {meta_url}")
        try:
            status, body, headers = fetch(meta_url)
            if status == 200:
                meta = json.loads(body)
                if commit_matches(meta.get("git_commit"), args.commit):
                    print(f"  build-meta.json reports git_commit={meta.get('git_commit')} -- matches")
                    break
                print(f"  build-meta.json reports git_commit={meta.get('git_commit')} "
                      f"(waiting for {args.commit})")
            else:
                print(f"  HTTP {status}")
        except (URLError, HTTPError) as exc:
            print(f"  fetch failed: {exc}")
        if attempt < args.retries:
            time.sleep(args.retry_delay)

    if meta is None or not commit_matches(meta.get("git_commit"), args.commit):
        failures.append(
            f"build-meta.json never reported git_commit={args.commit} after "
            f"{args.retries} attempts (got {meta.get('git_commit') if meta else None!r})"
        )

    if meta:
        for key, expected in REQUIRED_META.items():
            got = meta.get(key)
            if got != expected:
                failures.append(f"build-meta.json[{key}] = {got!r}, expected {expected!r}")
            else:
                print(f"  OK  build-meta.json[{key}] = {got}")

        # Version-specific fields: check them for internal consistency rather
        # than against a literal. Hardcoding "v32" here would have blocked
        # every correct later deployment while silently blessing a stale one --
        # which is exactly what it did on the v33 deploy.
        master_file = str(meta.get("master_file", ""))
        m = re.search(r"_v(\d+)_", master_file)
        if not m:
            failures.append(f"build-meta.json[master_file] = {master_file!r}: no version found")
        elif meta.get("master_version") != f"v{m.group(1)}":
            failures.append(
                f"build-meta.json[master_version] = {meta.get('master_version')!r} "
                f"disagrees with master_file {master_file!r}"
            )
        else:
            print(f"  OK  master_version {meta['master_version']} matches master_file")

        rows = meta.get("source_normalized_outcome_rows")
        if not isinstance(rows, int) or rows <= 0:
            failures.append(f"build-meta.json[source_normalized_outcome_rows] = {rows!r}")
        else:
            print(f"  OK  build-meta.json[source_normalized_outcome_rows] = {rows}")

    print(f"\nfetching {index_url}")
    try:
        status, html, headers_index = fetch(index_url)
        if status != 200:
            failures.append(f"index.html returned HTTP {status}")
        else:
            for needle in REQUIRED_TEXT:
                if needle not in html:
                    failures.append(f"index.html does not contain required text {needle!r}")
                else:
                    print(f"  OK  index.html contains {needle!r}")
            if short not in html:
                failures.append(f"index.html does not contain the deployed short SHA {short!r} "
                                 f"(build badge missing or stale)")
            else:
                print(f"  OK  index.html contains build badge with short SHA {short}")
            for banned in ("Reconciled Master v26", "Supporting Combined Synthesis (k=6"):
                if banned in html:
                    failures.append(f"index.html still contains superseded text {banned!r}")
                else:
                    print(f"  OK  index.html does not contain {banned!r}")
    except (URLError, HTTPError) as exc:
        failures.append(f"could not fetch index.html: {exc}")

    print("\nResponse headers (index.html):")
    for h in ("cache-control", "age", "etag", "last-modified"):
        print(f"  {h}: {headers_index.get(h, headers_index.get(h.title(), '(not present)'))}")

    if failures:
        print(f"\n{len(failures)} live verification check(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll live verification checks passed.")
    print(f"\nCache-busting review URL for external reviewers/crawlers:")
    print(f"  {args.base_url}/?build={short}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
