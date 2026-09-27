#!/bin/sh
# Run the Stata analysis layer from the repository root in batch mode, then drop Stata's batch log
# (it repeats the licence banner); the do-files write their own logs to 13_STATA/logs/.
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
STATA_BIN=${STATA_BIN:-/Applications/StataNow/StataSE.app/Contents/MacOS/stata-se}
cd "$ROOT"
"$STATA_BIN" -b do 10_FINAL_ADJUDICATION/13_STATA/do/99_run_all.do
status=0; grep -q '^r([0-9]*);' 99_run_all.log && status=1
[ $status -ne 0 ] && { echo "Stata reported an error:"; grep -n -B5 '^r([0-9]*);' 99_run_all.log | tail -20; }
rm -f 99_run_all.log
exit $status
