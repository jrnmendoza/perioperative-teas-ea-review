# Deployment Pipeline — Canonical Source and Build Path

**Current as of:** 2026-09-07 (deployment hardening pass, superseding §1-5 below)
**Branch:** `claude-v26-dashboard-final`
**Live site:** https://jrnmendoza.github.io/perioperative-teas-ea-review/

---

## Current architecture (2026-09-07 onward)

**One authoritative build path.** GitHub Actions (`.github/workflows/deploy-pages.yml`)
builds and deploys on every push to `claude-v26-dashboard-final`:

1. `scripts/build_site.py` copies `dashboard/` (the only hand-edited source) into a
   fresh `_site/`, mirrors `06_FINAL_ANALYSIS_V26/` into `_site/v26/`, refreshes the
   root-level `forest_*.png`/`loo_*.png` figures from `06_FINAL_ANALYSIS_V26/04_FIGURES/`
   (so a stale committed copy in `dashboard/` can never reach production), writes
   `_site/build-meta.json` (git commit, UTC build timestamp, and `canonical_studies`
   / `strict_primary_opioid_k` / `source_normalized_outcome_rows` derived from the
   current data.js / results CSV / v32 workbook — never hardcoded), bakes a static
   `id="build-badge"` element into `_site/index.html` (visible to crawlers that do not
   execute JavaScript — see rationale below), and cache-busts every internal JS/CSS
   asset reference and the two live-log `fetch()` calls with the short git SHA.
2. `scripts/deploy_integrity_check.py` asserts the built site's `build-meta.json`
   matches the current v32 state and that specific superseded claims (e.g.
   `"Reconciled Master v26"`, an active `k=6` primary result) are absent from live
   content before anything is uploaded. Aborts the workflow on failure.
3. `actions/upload-pages-artifact` + `actions/deploy-pages` publish `_site/` directly
   as the Pages artifact — GitHub Pages source is configured as **"GitHub Actions"**,
   not a branch.
4. `scripts/verify_deployment.py` fetches the live public URL and `build-meta.json`
   (both cache-busted with `?build=<commit-sha>`) after deployment and fails the
   workflow if the returned content does not match the commit that was just deployed.

`dashboard/v26/` and `docs/` (described in §1-5 below) were **retired and removed**
from the repository in this pass — see rationale below. `scripts/sync_dashboard.sh`
(the manual mirror-and-push tool they depended on) was deleted; `build_site.py` is
its replacement for both CI and local preview (`python3 scripts/build_site.py --out
_site`, then serve `_site/` locally).

### Why the old branch-based deployment left stale content for external crawlers

Confirmed via `gh api repos/.../pages`: GitHub Pages' legacy branch-based build type
serves every response with a fixed `Cache-Control: max-age=600` that cannot be
overridden by any file in the repository — this is GitHub's own CDN (Fastly)
configuration, not something `<meta>` tags or repo settings can change for that
build type. Separately, and more directly responsible for the reported staleness:
several static HTML elements were only ever corrected by JavaScript at page-load
time (e.g. a hero KPI's placeholder text, a subnav pill's study count). A browser
always ran that JS and saw the corrected value; a crawler or retrieval system that
does not execute JavaScript read the *raw, uncorrected* static placeholder directly
out of the page source. This pass found and fixed every such placeholder (subnav
pill study count, hero patient-count text, an orphaned `PRISMA_DATA` object in
`data.js` carrying pre-migration numbers, two more hardcoded study-count strings) so
the raw HTML is correct on its own, without relying on JavaScript execution.

Switching to Actions-based Pages deployment additionally means each deployment is a
new, atomic artifact rather than a commit pushed onto a long-lived branch whose CDN
cache entries persist across deployments — GitHub documents this as invalidating the
CDN cache on each Actions-based deployment, which the legacy branch-based path does
not guarantee.

### Why `dashboard/v26/` and `docs/` were removed

Both were committed, hand-synced duplicates (`scripts/sync_dashboard.sh` mirrored
`dashboard/` → `docs/`, and separately `06_FINAL_ANALYSIS_V26/` → `dashboard/v26/`)
with no automated guarantee any two of `main`'s `dashboard/`, `main`'s `docs/`, and
the `gh-pages` branch actually matched at any given time — exactly the ambiguity
this hardening pass was asked to eliminate. `build_site.py` now generates both
mirrors fresh, in-memory, on every build; there is no persisted copy left to drift.

---

## Historical record: pre-2026-09-07 architecture (superseded, kept for audit trail)

### 1. What GitHub Pages actually served (legacy branch-based)

**Answer: the root of the `gh-pages` branch.**

Evidence:

| Probe | Result | Interpretation |
| --- | --- | --- |
| `.github/workflows/` | did not exist | No GitHub Actions deployment. Pages was configured from a branch. |
| `GET /index.html` | 200 | Site root served the dashboard. |
| `GET /06_FINAL_ANALYSIS_V26/00_README.md` | 200 | This path existed **only** at `gh-pages` root. `docs/` on `main` had no such folder. |
| `GET /docs/index.html` | 200 | `gh-pages` root contained a nested `docs/` copy. |
| `GET /dashboard/index.html` | 200 | `gh-pages` root also contained a nested `dashboard/` copy. |
| `GET /README.md` | 404 | `gh-pages` root had no `README.md`; `main` root did. |

Confirmed authoritatively later via `gh api repos/jrnmendoza/perioperative-teas-ea-review/pages`:
`{"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}`.

### 2. Copy inventory (all four were byte-identical at the start of that work)

`md5` of `index.html`, `app.js`, `data.js` was identical across `dashboard/` on
`main`, `docs/` on `main`, `gh-pages` root, and `gh-pages:docs/` /
`gh-pages:dashboard/` (nested duplicates).

### 3. Canonical decision (superseded)

| Role | Location |
| --- | --- |
| Source of truth (edit here) | `dashboard/` on `main`-line branches |
| Generated copy (never hand-edit) | `docs/` — synced from `dashboard/` |
| Deployment target | `gh-pages` branch root |
| Sync mechanism | `scripts/sync_dashboard.sh` |

### 4. Deployment-coupling caveat (recorded, now resolved)

The dashboard linked to `06_FINAL_ANALYSIS_V26/...` with repo-root-relative paths,
which resolved on `gh-pages` only by accident of that branch's root containing a
full copy of the analysis package. Resolved by `build_site.py` always mirroring
`06_FINAL_ANALYSIS_V26/` into `v26/` at the site root of whatever it builds.

### 5. Safest update path (superseded by the GitHub Actions workflow)

1. Edit `dashboard/`.
2. `bash scripts/sync_dashboard.sh` → mirrors into `docs/`.
3. `python3 scripts/validate_dashboard.py` → must exit 0.
4. Commit on `claude-v26-dashboard-final`.
5. Manually build a `gh-pages` worktree, commit, and push.
