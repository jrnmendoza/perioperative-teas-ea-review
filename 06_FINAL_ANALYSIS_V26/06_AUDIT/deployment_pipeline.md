# Deployment Pipeline — Determination and Canonical Source

**Determined:** 2026-09-07
**Branch:** `claude-v26-dashboard-final`
**Live site:** https://jrnmendoza.github.io/perioperative-teas-ea-review/

---

## 1. What GitHub Pages actually serves

**Answer: the root of the `gh-pages` branch.**

Evidence:

| Probe | Result | Interpretation |
| --- | --- | --- |
| `.github/workflows/` | does not exist | No GitHub Actions deployment. Pages is configured from a branch. |
| `GET /index.html` | 200 | Site root serves the dashboard. |
| `GET /06_FINAL_ANALYSIS_V26/00_README.md` | 200 | This path exists **only** at `gh-pages` root. `docs/` on `main` has no such folder. |
| `GET /docs/index.html` | 200 | `gh-pages` root contains a nested `docs/` copy. If `docs/` on `main` were the Pages root, this would be `docs/docs/` → 404. |
| `GET /dashboard/index.html` | 200 | `gh-pages` root also contains a nested `dashboard/` copy. |
| `GET /README.md` | 404 | `gh-pages` root has no `README.md` (confirmed by `git ls-tree gh-pages`). `main` root does. |

The `06_FINAL_ANALYSIS_V26` + `docs/` + missing `README.md` combination is unique to the `gh-pages` tree, so Pages is publishing `gh-pages` at `/`.

## 2. Copy inventory (all four were byte-identical at the start of this work)

`md5` of `index.html`, `app.js`, `data.js` was identical across:

1. `dashboard/` on `main`
2. `docs/` on `main`
3. `gh-pages` root
4. `gh-pages:docs/` and `gh-pages:dashboard/` (nested duplicates)

`dashboard/` additionally carries three `.log` files that `docs/` lacks
(`stata_48h_opioid_synthesis.log`, `stata_72h_opioid_synthesis.log`,
`stata_meta_regression_execution.log`).

## 3. Canonical decision

| Role | Location |
| --- | --- |
| **Source of truth (edit here)** | `dashboard/` on `main`-line branches |
| **Generated copy (never hand-edit)** | `docs/` — synced from `dashboard/` |
| **Deployment target** | `gh-pages` branch root |
| **Sync mechanism** | `scripts/sync_dashboard.sh` |

Rationale: commit history labels feature work `feat(dashboard)` and deployment work
`feat(gh-pages)`; `dashboard/` is the superset (extra logs). Editing three copies
independently is what allowed the current drift, so all edits now go to `dashboard/`
and propagate mechanically.

## 4. Deployment-coupling caveat (recorded, not yet fixed)

The dashboard links to `06_FINAL_ANALYSIS_V26/...` with **repo-root-relative** paths
(e.g. `06_FINAL_ANALYSIS_V26/02_STATA/logs/01_opioid24_primary.log`). These resolve on
`gh-pages` only because that branch's root contains a copy of the whole analysis
package. They **404 when `docs/` is served or previewed standalone**. Any future move
of Pages to `docs/` on `main` must also relocate those assets.

## 5. Safest update path

1. Edit `dashboard/`.
2. `bash scripts/sync_dashboard.sh` → mirrors into `docs/`.
3. `python3 scripts/validate_dashboard.py` → must exit 0.
4. Commit on `claude-v26-dashboard-final`.
5. Only after validation passes: publish `gh-pages` (not done automatically).
