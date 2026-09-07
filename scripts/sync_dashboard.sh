#!/usr/bin/env bash
# Build the deployable dashboard, then mirror it into the generated copy.
#
# Canonical source of truth : dashboard/
# Generated copy            : docs/         (never hand-edit)
# Deployment target         : gh-pages branch root
#
# Step 1 mirrors the authoritative v26 analysis package into dashboard/v26/ so
# that every download link is RELATIVE TO THE PAGE. Without this the links only
# resolve when the dashboard happens to sit at the site root (as it does on
# gh-pages, which also carries its own copy of 06_FINAL_ANALYSIS_V26). Served
# from docs/ or any subdirectory they 404 silently.
#
# See 06_FINAL_ANALYSIS_V26/06_AUDIT/deployment_pipeline.md
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/dashboard"
DST="$REPO_ROOT/docs"
V26="$REPO_ROOT/06_FINAL_ANALYSIS_V26"

[ -d "$SRC" ] || { echo "FATAL: $SRC not found" >&2; exit 1; }
[ -d "$V26" ] || { echo "FATAL: $V26 not found" >&2; exit 1; }

# 1. Mirror the authoritative analysis package into the dashboard.
rsync -a --delete \
  --exclude '.DS_Store' \
  "$V26/" "$SRC/v26/"
echo "Mirrored 06_FINAL_ANALYSIS_V26/ -> dashboard/v26/"

# 2. Mirror the whole dashboard into the generated copy.
mkdir -p "$DST"
rsync -a --delete \
  --exclude '.DS_Store' \
  "$SRC/" "$DST/"

echo "Synced dashboard/ -> docs/"
diff -rq "$SRC" "$DST" >/dev/null && echo "Parity verified: dashboard/ == docs/"

# 3. Derive the cache-busting token from the CONTENT of the assets it guards.
#    A hand-maintained token silently serves stale JS to returning visitors
#    whenever someone edits data.js but forgets to bump it.
HASH="$(cat "$SRC/data.js" "$SRC/app.js" "$SRC/translations.js" \
             "$SRC/meta_engine.js" "$SRC/reader_assist.js" "$SRC/styles.css" \
        | shasum -a 256 | cut -c1-12)"
/usr/bin/sed -i '' -E "s/\?v=[A-Za-z0-9_]+/?v=${HASH}/g" "$SRC/index.html"
echo "Cache buster set from content hash: ${HASH}"

# Re-mirror so docs/ picks up the rewritten index.html.
rsync -a --delete --exclude '.DS_Store' "$SRC/" "$DST/"
diff -rq "$SRC" "$DST" >/dev/null && echo "Parity re-verified after cache-buster rewrite"
