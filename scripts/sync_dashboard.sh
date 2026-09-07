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
