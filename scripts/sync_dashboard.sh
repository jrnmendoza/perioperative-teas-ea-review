#!/usr/bin/env bash
# Mirror the canonical dashboard source (dashboard/) into the generated copy (docs/).
#
# Canonical source of truth : dashboard/
# Generated copy            : docs/         (never hand-edit)
# Deployment target         : gh-pages branch root
#
# See 06_FINAL_ANALYSIS_V26/06_AUDIT/deployment_pipeline.md
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/dashboard"
DST="$REPO_ROOT/docs"

[ -d "$SRC" ] || { echo "FATAL: $SRC not found" >&2; exit 1; }
mkdir -p "$DST"

rsync -a --delete \
  --exclude '.DS_Store' \
  "$SRC/" "$DST/"

echo "Synced dashboard/ -> docs/"
diff -rq "$SRC" "$DST" >/dev/null && echo "Parity verified: dashboard/ == docs/"
