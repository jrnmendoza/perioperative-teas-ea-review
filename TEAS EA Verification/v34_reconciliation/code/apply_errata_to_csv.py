#!/usr/bin/env python3
"""
Mirror the post-lock errata into v34_outcome_data.csv.

WHY THIS IS A SURGICAL PATCH AND NOT A RE-EXPORT
POST_LOCK_ERRATA_v34.md step 2 says to "re-export the CSV from the workbook's
Outcome_Data sheet". Doing that literally rewrites 2,006 cells that did not
change: the CSV was written with integers rendered as "103", while openpyxl
reads the same stored values back as floats and renders them "103.0". The data
is identical; only the text differs. A 749-line diff would bury the two lines
that actually changed and would make the correction unreviewable -- the exact
failure mode the XLSX patcher was written to avoid.

So this edits the two affected lines and leaves the other 756 byte-identical,
then proves the result still mirrors the workbook cell for cell.

WHERE THE NEW ROW'S VALUES COME FROM
The workbook, not this file. Re-typing them here would create a second place
for the CSV and the workbook to disagree, which is the defect class this whole
errata register exists to close.

FORMAT
The file is UTF-8 with a BOM and CRLF line endings. Both are preserved
deliberately: a previous edit in this repository silently rewrote a sibling CSV
to LF and turned a two-value correction into a whole-file diff.

USAGE
    python3 "TEAS EA Verification/v34_reconciliation/code/apply_errata_to_csv.py" --dry-run
    python3 "TEAS EA Verification/v34_reconciliation/code/apply_errata_to_csv.py" --apply
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[3]
VER = ROOT / "TEAS EA Verification"
MASTER = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
CSV_PATH = VER / "v34_reconciliation" / "data" / "v34_outcome_data.csv"

VOMIT_ID = "YANG24_EA_vs_UC_VOMIT"
NAUSEA_ID = "YANG24_EA_vs_UC_NAUSEA24"
WINDOW_FIXES = {
    "Timepoint/window": ("Within 72 h", "0-24 h after surgery"),
    "V34 time class": ("within 72h", "0-24h"),
}


def read_csv_lines() -> list[str]:
    """Split on CRLF ourselves so we can rebuild the file byte-for-byte."""
    text = CSV_PATH.read_text(encoding="utf-8-sig", newline="")
    if "\r\n" not in text:
        raise SystemExit("CSV is not CRLF-delimited -- refusing to guess its format")
    lines = text.split("\r\n")
    if lines[-1] != "":
        raise SystemExit("CSV does not end with a line terminator")
    return lines[:-1]


def parse_line(line: str) -> list[str]:
    return next(csv.reader(io.StringIO(line)))


def format_line(fields: list[str]) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(fields)
    return buf.getvalue()


def workbook_rows() -> tuple[list[str], list[list]]:
    wb = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)
    ws = wb["Outcome_Data"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    return [str(c) for c in rows[0]], rows[1:]


def render(value) -> str:
    """Match the CSV's own convention: whole floats are written without .0."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def norm(s: str) -> str:
    """Compare CSV text to workbook values ignoring int/float rendering only."""
    s = s.strip()
    try:
        f = float(s)
    except (TypeError, ValueError):
        return s
    return str(int(f)) if f == int(f) else repr(round(f, 10))


def main() -> int:
    apply = "--apply" in sys.argv
    header_x, data_x = workbook_rows()
    lines = read_csv_lines()
    header_c = parse_line(lines[0])
    if header_c != header_x:
        raise SystemExit("CSV and workbook headers differ -- refusing to patch")

    idx = {name: i for i, name in enumerate(header_c)}
    id_col = idx["Comparison ID"]

    if any(parse_line(l)[id_col] == NAUSEA_ID for l in lines[1:]):
        raise SystemExit(f"{NAUSEA_ID} is already in the CSV -- nothing to add")

    # -- erratum 2: both window fields on the Yang vomiting line --------------
    hits = [i for i, l in enumerate(lines) if i and parse_line(l)[id_col] == VOMIT_ID]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one {VOMIT_ID} line, found {len(hits)}")
    i = hits[0]
    fields = parse_line(lines[i])
    for col, (old, new) in WINDOW_FIXES.items():
        if fields[idx[col]] != old:
            raise SystemExit(f"{col} is {fields[idx[col]]!r}, expected {old!r}")
        fields[idx[col]] = new
    lines[i] = format_line(fields)

    # -- erratum 1: append the new row, taken from the workbook ---------------
    new_rows = [r for r in data_x if r[id_col] == NAUSEA_ID]
    if len(new_rows) != 1:
        raise SystemExit(f"expected exactly one {NAUSEA_ID} row in the workbook, "
                         f"found {len(new_rows)} -- run the XLSX patcher first")
    lines.append(format_line([render(v) for v in new_rows[0]]))

    out = "﻿" + "\r\n".join(lines) + "\r\n"

    # -- verification: does the patched CSV still mirror the workbook? --------
    patched = [parse_line(l) for l in lines[1:]]
    if len(patched) != len(data_x):
        raise SystemExit(f"CSV has {len(patched)} data rows, workbook has {len(data_x)}")
    mismatches = []
    for r, (cr, xr) in enumerate(zip(patched, data_x), start=2):
        for c, name in enumerate(header_c):
            if norm(cr[c]) != norm(render(xr[c])):
                mismatches.append((r, name, cr[c][:40], render(xr[c])[:40]))
    if mismatches:
        for m in mismatches[:10]:
            print(f"  line {m[0]} {m[1]}: CSV {m[2]!r} vs workbook {m[3]!r}")
        raise SystemExit(f"{len(mismatches)} cell(s) diverge from the workbook")

    print(f"  verified: {len(patched)} rows mirror the workbook cell for cell")
    print(f"            line {i + 1} window fields corrected, 1 row appended,")
    print(f"            {len(lines) - 3} other lines untouched, CRLF + BOM preserved")

    if apply:
        CSV_PATH.write_text(out, encoding="utf-8", newline="")
        print(f"\nwritten: {CSV_PATH.relative_to(ROOT)}")
    else:
        print("\n(dry run: the CSV was NOT modified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
