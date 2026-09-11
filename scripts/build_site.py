#!/usr/bin/env python3
"""
Build the deployable Pages artifact into _site/.

Single authoritative build path for GitHub Pages. Replaces the old manual
flow (sync_dashboard.sh -> docs/ -> hand-pushed gh-pages branch) with one
script that a GitHub Actions workflow runs on every push, producing a fresh,
uniquely-versioned artifact each time.

Steps:
  1. Copy dashboard/ -> _site/ (the canonical dashboard source).
  2. Mirror 06_FINAL_ANALYSIS_V26/ -> _site/v26/ (so download links, which are
     repo-root-relative, resolve when served from the site root).
  3. Derive build metadata (git commit, UTC timestamp, canonical_studies,
     strict_primary_opioid_k, source_normalized_outcome_rows) from the
     repo's own current outputs -- never hardcoded -- and write
     _site/build-meta.json.
  4. Bake a visible build badge into _site/index.html's static HTML (not only
     into a JS-rendered element), so it is visible to non-JS-executing
     crawlers/retrieval systems -- the actual cause of the stale-snapshot
     complaint this script exists to fix.
  5. Cache-bust every internal JS/CSS asset reference and the two live-log
     fetch() calls using the short git SHA, so each deployment's asset URLs
     are guaranteed distinct from the previous one (not a static "?v=32").

Usage:  python3 scripts/build_site.py [--out _site] [--commit <sha>]
Exit:   0 on success, 1 on any failure (verification, missing source, etc.)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
V26 = ROOT / "06_FINAL_ANALYSIS_V26"
V33 = ROOT / "07_TIERED_V33"
RESULTS = V26 / "03_RESULTS"
MASTER_XLSX = (
    ROOT / "TEAS EA Verification"
    / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
)

CACHE_BUSTED_ASSETS = (
    "styles.css", "primary_pathway.js", "tiered_v33.js", "v33_data.js", "v34_data.js",
    "pdf_extracted.js", "outcome_quarantine.js",
    "interpretation_layer.js", "computed_not_reported.js", "prior_evidence.js", "limitations.js", "prisma_checklist.js", "stratum_purity.js", "forest_context.js", "rob2_source_links.js", "data.js",
    "translations.js", "ui_translations.js", "reader_assist.js", "meta_engine.js", "app.js", "findings.js",
    "author_inquiries.js", "search_strategies.js", "meta_outcomes.js",
    "primary_browser.js",
    "browser_targets.js",
    "study_characteristics.js",
)
CACHE_BUSTED_FETCH_PATHS = (
    "v26/02_STATA/logs/01_opioid24_primary.log",
    "v26/02_STATA/logs/09_subgroups_metareg.log",
)
CACHE_BUSTED_DOWNLOAD_PATTERNS = (
    re.compile(r'href="((?:results|v26/01_DATA|v26/03_RESULTS)/[^"?]+\.(?:csv|json))"'),
)


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def git_commit(explicit: str | None) -> str:
    if explicit:
        return explicit
    try:
        return run(["git", "rev-parse", "HEAD"])
    except Exception as exc:  # pragma: no cover - CI always has git
        raise RuntimeError("could not determine git commit; pass --commit explicitly") from exc


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def canonical_studies_count() -> int:
    """Parse window.STUDIES_DATA out of data.js without a JS engine."""
    text = (DASH / "data.js").read_text(encoding="utf-8")
    start = text.index("window.STUDIES_DATA = [") + len("window.STUDIES_DATA = ")
    depth, i, in_str, esc = 0, start, False, False
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return len(json.loads(text[start:i + 1]))
        i += 1
    raise RuntimeError("could not parse window.STUDIES_DATA out of data.js")


def strict_primary_opioid_k() -> int:
    rows = read_csv_rows(RESULTS / "master_reconciled_results_v26.csv")
    by_id = {r["analysis_id"]: r for r in rows}
    return int(by_id["OP24_PRIM_COMB"]["k"])


def source_normalized_outcome_rows() -> int:
    """
    Read the v32 workbook's own Summary sheet rather than hardcoding this --
    it is a source-workbook QC figure with no other materialized copy in the
    repo's generated outputs.
    """
    import openpyxl  # local import: only needed for this one derivation

    if not MASTER_XLSX.exists():
        raise RuntimeError(f"master workbook not found at {MASTER_XLSX}")
    wb = openpyxl.load_workbook(MASTER_XLSX, data_only=True)

    # Count the Outcome_Data rows directly rather than trusting the Summary
    # sheet's stored figure. The stored figure is written by hand and was found
    # carrying v32's 364 inside the v33 workbook while Outcome_Data held 382 --
    # exactly the hardcoded-count drift this build is supposed to eliminate.
    actual = wb["Outcome_Data"].max_row - 1

    for row in wb["Summary"].iter_rows(values_only=True):
        if row and row[0] == "Source-normalized outcome rows":
            stated = row[1]
            if stated is not None and int(stated) != actual:
                raise RuntimeError(
                    f"master workbook is internally inconsistent: Summary sheet says "
                    f"{stated} source-normalized outcome rows, Outcome_Data has {actual}"
                )
            break
    return actual


def build_metadata(commit: str) -> dict:
    return {
        "master_version": "v34",
        "master_file": MASTER_XLSX.name,
        "canonical_studies": canonical_studies_count(),
        "source_normalized_outcome_rows": source_normalized_outcome_rows(),
        "strict_primary_opioid_k": strict_primary_opioid_k(),
        "git_commit": commit,
        "build_timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def copy_site(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(DASH, out, ignore=shutil.ignore_patterns(".DS_Store", "*.bak"))
    v26_out = out / "v26"
    if v26_out.exists():
        shutil.rmtree(v26_out)
    shutil.copytree(V26, v26_out, ignore=shutil.ignore_patterns(".DS_Store", "*.bak"))
    shutil.copytree(ROOT / '08_V33_MASTER/04_FIGURES', out / 'secondary', dirs_exist_ok=True)

    # The v33 tiered figures are referenced as v33/<file>.png by renderTieredV33(),
    # and the do-file, data and results are linked as downloadable provenance.
    # Mirrored from 07_TIERED_V33/ here rather than committed into dashboard/,
    # so the deployed artifact can never inherit a stale hand-copied figure --
    # the same drift class already fixed once for the v26 forest plots below.
    v33_out = out / "v33"
    if v33_out.exists():
        shutil.rmtree(v33_out)
    v33_out.mkdir(parents=True)
    for png in sorted((V33 / "04_FIGURES").glob("*.png")):
        shutil.copyfile(png, v33_out / png.name)
    for sub in ("01_DATA", "02_STATA", "05_RESULTS", "03_DIGITIZATION"):
        src = V33 / sub
        if src.exists():
            shutil.copytree(src, v33_out / sub,
                            ignore=shutil.ignore_patterns(".DS_Store", "*.bak"))
    for doc in sorted(V33.glob("*.md")) + sorted(V33.glob("*.csv")) + sorted(V33.glob("*.xlsx")):
        shutil.copyfile(doc, v33_out / doc.name)

    # dashboard/*.png (root-level forest/LOO figures the page embeds directly,
    # e.g. <img src="forest_opioid24_primary_mme.png">) is a committed
    # convenience copy for local preview without running this script, and can
    # go stale relative to the true Stata output whenever the pipeline is
    # re-run without a matching manual copy -- a real drift class found and
    # fixed once already this project (see dashboard_v26_reconciliation.md
    # section 25.8). Always overwrite from 06_FINAL_ANALYSIS_V26/04_FIGURES/
    # here so the deployed artifact can never inherit that staleness even if
    # dashboard/'s own committed copies are behind.
    figures_src = V26 / "04_FIGURES"
    for png in out.glob("forest_*.png"):
        twin = figures_src / png.name
        if twin.exists():
            shutil.copyfile(twin, png)
    for png in out.glob("loo_*.png"):
        twin = figures_src / png.name
        if twin.exists():
            shutil.copyfile(twin, png)


def apply_cache_busting(out: Path, short_sha: str) -> None:
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")

    for asset in CACHE_BUSTED_ASSETS:
        html = re.sub(
            rf'({re.escape(asset)})(\?v=[A-Za-z0-9_]+)?"',
            rf'\1?v={short_sha}"',
            html,
        )
    for pat in CACHE_BUSTED_DOWNLOAD_PATTERNS:
        html = pat.sub(lambda m: f'href="{m.group(1)}?v={short_sha}"', html)
    index.write_text(html, encoding="utf-8")

    app_js = out / "app.js"
    js = app_js.read_text(encoding="utf-8")
    for path in CACHE_BUSTED_FETCH_PATHS:
        js = js.replace(f"fetch('{path}')", f"fetch('{path}?v={short_sha}')")
    app_js.write_text(js, encoding="utf-8")


def inject_build_badge(out: Path, meta: dict) -> None:
    """
    Bake the build indicator directly into static HTML (not only a JS-set
    element) so it is visible to crawlers/retrieval systems that do not
    execute JavaScript -- the actual mechanism behind stale external
    snapshots even when the deployed commit and CDN are current.
    """
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    short_sha = meta["git_commit"][:8]
    badge_html = (
        f'<div id="build-badge" style="position:fixed;right:6px;bottom:6px;'
        f'z-index:2147483647;font:9px/1.3 monospace;background:rgba(15,23,42,0.7);'
        f'color:#64748b;padding:2px 6px;border-radius:3px;pointer-events:none;'
        f'opacity:0.7;max-width:60vw;overflow:hidden;text-overflow:ellipsis;'
        f'white-space:nowrap;">'
        f'Data {meta["master_version"]} &bull; build {short_sha} &bull; '
        f'{meta["build_timestamp_utc"]}</div>'
    )
    marker = "<!--BUILD_BADGE-->"
    if marker not in html:
        raise RuntimeError(
            f"{index} has no {marker} placeholder; add one before </body> in dashboard/index.html"
        )
    html = html.replace(marker, badge_html, 1)
    index.write_text(html, encoding="utf-8")


def write_build_meta(out: Path, meta: dict) -> None:
    (out / "build-meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--commit", default=None, help="override git commit (default: current HEAD)")
    args = ap.parse_args()
    out = Path(args.out)

    run([sys.executable, "scripts/build_reference_data.py"])
    # scripts/extract_baseline_from_pdfs.py is deliberately NOT run here. It reads
    # all 70 source PDFs and needs pypdf, which the deploy workflow does not
    # install; its output (dashboard/pdf_extracted.js) is committed, so the site
    # builds from that. Re-run it by hand when a source PDF or the extraction
    # rules change, and commit the regenerated file.
    # scripts/validate_dashboard.py checks that file's integrity either way.
    # The dashboard's outcome register is generated from the lock, not authored.
    # Refuse to build a site whose data.js has been hand-edited away from it --
    # that drift is what the 2026-09-10 placeholder incident was.
    sync = subprocess.run([sys.executable, "scripts/sync_dashboard_outcomes.py", "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    if sync.returncode != 0:
        print(sync.stdout.strip() or sync.stderr.strip(), file=sys.stderr)
        print("\nBUILD REFUSED: dashboard/data.js no longer matches the locked datasets.\n"
              "Run  python3 scripts/sync_dashboard_outcomes.py  to regenerate it, or fix the\n"
              "lock if the lock is what changed. Do not hand-edit the outcome records.",
              file=sys.stderr)
        return 1

    commit = git_commit(args.commit)
    meta = build_metadata(commit)

    print("Build metadata:")
    for k, v in meta.items():
        print(f"  {k}: {v}")

    copy_site(out)
    apply_cache_busting(out, commit[:8])
    inject_build_badge(out, meta)
    write_build_meta(out, meta)

    print(f"\nBuilt site at {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
