#!/usr/bin/env python3
"""
Apply the source-verified post-lock errata to the v34 master workbook.

WHAT THIS DOES
Errata 1 and 2 from POST_LOCK_ERRATA_v34.md, both verified against
covidence_1930_full_article.pdf (Yang 2024) before being written here:

  1. Adds the missing Yang 2024 postoperative nausea 0-24 h result
     (24/90 EA vs 40/90 usual care, P = 0.013) as a new Outcome_Data row.
     The pooled TD_NAUSEA_0_24H analysis already used these values; the row
     was absent from the extraction dataset.
  2. Corrects the Yang 2024 vomiting row's window from "Within 72 h" to
     "0-24 h after surgery". The stored counts (12/25) and P (0.016) match
     Table 3's 0-24 h interval exactly -- the 24-48 h interval is 6/10 with
     P = 0.295 -- so only the label was wrong, never the values.
  3. Updates the workbook's own Summary sheet count 757 -> 758, because the
     dashboard reads source_normalized_outcome_rows from that sheet rather
     than counting rows itself.

WHY IT EDITS THE XML DIRECTLY INSTEAD OF USING openpyxl
The workbook carries 2 charts and 6 drawings. openpyxl silently drops those
on load/save, which would destroy content in a master research artefact as a
side effect of a two-cell correction. This rewrites the package part by part,
substituting only the two sheet XML streams and copying the other 141 parts
byte-for-byte, then verifies that is exactly what happened.

WHY THIS IS A SCRIPT AND NOT A COMMITTED .xlsx
The correction stays reviewable: anyone can read what is being changed and
re-derive the result, rather than being asked to trust a binary diff of a
locked file.

THIS BREAKS THE PIN ON PURPOSE
The workbook is pinned by SHA-256 in scripts/build_v34_dashboard_data.py,
which aborts on mismatch. That guard is doing its job -- it exists so the
locked dataset cannot change unnoticed. Running this therefore REQUIRES a
deliberate follow-up, and the script prints the new hash and the exact
remaining steps rather than trying to complete them itself.

USAGE
    python3 "TEAS EA Verification/v34_reconciliation/code/apply_post_lock_errata.py" --dry-run
    python3 "TEAS EA Verification/v34_reconciliation/code/apply_post_lock_errata.py" --apply

--dry-run (default) writes a candidate copy next to the original and verifies
it, changing nothing in place.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VER = ROOT / "TEAS EA Verification"
MASTER = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
CANDIDATE = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v34_CORRECTED_CANDIDATE.xlsx"
CSV = VER / "v34_reconciliation" / "data" / "v34_outcome_data.csv"
BACKUP = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v34_PRE_ERRATA_BACKUP.xlsx"

EXPECTED_SHA = "985dc26a943cf30e1bbdac552a5eb69a6fb2d73fd252d0bc194abbdb8538d6f3"
OUTCOME_SHEET = "xl/worksheets/sheet7.xml"   # Outcome_Data
SUMMARY_SHEET = "xl/worksheets/sheet6.xml"   # Summary
NEW_ROW = 759

SOURCE_QUOTE = (
    'Table 3, "0-24 h after surgery": Incidence of Nausea [n(%)] 24(26.7) EA vs '
    '40(44.4) UC, P=0.013. Methods: "Incidence of PON and POV ... were recorded at '
    '0-24 h, 24-48 h and 48-72 h after surgery."'
)

TEXT = {
    "A": "Yang 2024", "B": "YANG24_EA_vs_UC_NAUSEA24",
    "C": "Perioperative EA + usual care", "D": "Usual care", "E": "PONV",
    "F": "Postoperative nausea", "G": "0-24 h after surgery", "H": "Events/total",
    "Y": "participants", "Z": "0.013", "AA": "Yes", "AB": "No", "AC": "RR",
    "AE": "No", "AF": "No",
    "AG": "Eligible for dichotomous nausea analysis at 0-24 h", "AH": "No",
    "AI": ("No sham acupuncture; nausea is a subjective endpoint reported by "
           "unblinded participants"),
    "AJ": "Table 3 (0-24 h after surgery); Methods (recording windows); Results text",
    "AK": "https://drive.google.com/file/d/160N3psd5tLEphwXHJzUEZ3uJfaIXcs5V/view?usp=drivesdk",
    "AL": "SOURCE-VERIFIED", "AM": "V34-OD-0759",
    "AZ": "Intention-to-treat (90/90 retained)",
    "BA": "covidence_1930_full_article.pdf", "BB": SOURCE_QUOTE, "BC": "INCLUDE",
    "BD": ("Numerically extractable in its native endpoint/time/statistic; pooling "
           "still requires compatible stratum, comparator and independent-arm selection."),
    # No result-specific RoB 2 judgement exists for this result. It is recorded as
    # pending rather than inheriting one from the study's other outcomes.
    "BE": "ROB2_RESULT_SPECIFIC_PENDING",
    "BF": "Nausea", "BG": "EA", "BH": "Usual care", "BI": "0-24h",
}
NUMS = {"I": 90, "J": 90, "K": 90, "L": 90, "R": 24, "X": 40, "AD": 0.6}
COLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
        "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF",
        "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT",
        "AU", "AV", "AW", "AX", "AY", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cell(ref: str, val, numeric=False) -> str:
    if val is None or val == "":
        return f'<x:c r="{ref}" />'
    t = "n" if numeric else "str"
    return f'<x:c r="{ref}" t="{t}"><x:v>{esc(val)}</x:v></x:c>'


def patch(out_path: Path) -> None:
    zin = zipfile.ZipFile(MASTER)
    od = zin.read(OUTCOME_SHEET).decode("utf-8")
    summ = zin.read(SUMMARY_SHEET).decode("utf-8")

    # -- erratum 2: window label on the existing Yang vomiting row ------------
    m = re.search(r'<x:row r="55">.*?</x:row>', od, re.S)
    if not m:
        raise SystemExit("row 55 (Yang 2024 vomiting) not found -- workbook layout changed")
    row55 = m.group(0)
    if "YANG24_EA_vs_UC_VOMIT" not in row55:
        raise SystemExit("row 55 is not the Yang 2024 vomiting row -- refusing to edit blindly")
    fixed = row55.replace(
        '<x:c r="G55" t="str"><x:v>Within 72 h</x:v></x:c>',
        '<x:c r="G55" t="str"><x:v>0-24 h after surgery</x:v></x:c>'
    ).replace(
        '<x:c r="BI55" t="str"><x:v>within 72h</x:v></x:c>',
        '<x:c r="BI55" t="str"><x:v>0-24h</x:v></x:c>')
    if fixed == row55:
        raise SystemExit("window cells not found on row 55 -- already corrected?")
    od = od[:m.start()] + fixed + od[m.end():]

    # -- erratum 1: append the missing nausea row -----------------------------
    if "YANG24_EA_vs_UC_NAUSEA24" in od:
        raise SystemExit("the nausea row is already present -- nothing to add")
    cells = "".join(
        cell(f"{c}{NEW_ROW}", NUMS[c], numeric=True) if c in NUMS
        else cell(f"{c}{NEW_ROW}", TEXT.get(c))
        for c in COLS)
    i = od.rfind("</x:sheetData>")
    od = od[:i] + f'<x:row r="{NEW_ROW}">{cells}</x:row>' + od[i:]

    # -- erratum 3: the workbook's own row-count figure -----------------------
    j = summ.find("Outcome_Data rows")
    if j < 0:
        raise SystemExit("Summary sheet has no 'Outcome_Data rows' figure to update")
    seg = summ[j:j + 300]
    if "<x:v>757</x:v>" not in seg:
        raise SystemExit("Summary count is not 757 -- refusing to guess")
    summ = summ[:j] + seg.replace("<x:v>757</x:v>", "<x:v>758</x:v>", 1) + summ[j + 300:]

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == OUTCOME_SHEET:
                data = od.encode("utf-8")
            elif item.filename == SUMMARY_SHEET:
                data = summ.encode("utf-8")
            zout.writestr(item, data)
    zin.close()


def verify(out_path: Path) -> None:
    """Prove only the two intended parts changed, and that the charts survived."""
    a, b = zipfile.ZipFile(MASTER), zipfile.ZipFile(out_path)
    if set(a.namelist()) != set(b.namelist()):
        raise SystemExit("package parts were added or lost")
    changed = [n for n in sorted(a.namelist()) if a.read(n) != b.read(n)]
    if changed != sorted([OUTCOME_SHEET, SUMMARY_SHEET]):
        raise SystemExit(f"unexpected parts changed: {changed}")
    for n in a.namelist():
        if ("chart" in n or "drawing" in n) and a.read(n) != b.read(n):
            raise SystemExit(f"chart/drawing content changed: {n}")
    a.close(); b.close()

    import openpyxl
    wb = openpyxl.load_workbook(out_path)
    od = wb["Outcome_Data"]
    if od.max_row - 1 != 758:
        raise SystemExit(f"Outcome_Data has {od.max_row - 1} rows, expected 758")
    hdr = [c.value for c in od[1]]
    row = dict(zip(hdr, [c.value for c in od[NEW_ROW]]))
    checks = {"Canonical study": "Yang 2024", "Outcome/result": "Postoperative nausea",
              "Timepoint/window": "0-24 h after surgery", "Events intervention": 24,
              "Events comparator": 40}
    for k, want in checks.items():
        if row.get(k) != want:
            raise SystemExit(f"new row {k}={row.get(k)!r}, expected {want!r}")
    vom = dict(zip(hdr, [c.value for c in od[55]]))
    if vom.get("Timepoint/window") != "0-24 h after surgery":
        raise SystemExit("vomiting window was not corrected")
    print("  verified: 141 parts byte-identical, charts intact, 48 sheets, 758 rows,")
    print("            nausea row present, vomiting window corrected")


def main() -> int:
    apply = "--apply" in sys.argv
    if not MASTER.exists():
        raise SystemExit(f"master workbook not found: {MASTER}")
    current = sha256(MASTER)
    print(f"current master SHA-256: {current}")
    if current != EXPECTED_SHA:
        print("  NOTE: this is not the SHA this script was written against")
        print(f"        expected {EXPECTED_SHA}")
        print("        the errata may already be applied, or the workbook has moved on.")
        return 1

    target = MASTER if apply else CANDIDATE
    if apply:
        shutil.copy2(MASTER, BACKUP)
        print(f"backup written: {BACKUP.name}")
        patch(CANDIDATE)
        verify(CANDIDATE)
        shutil.move(str(CANDIDATE), str(MASTER))
    else:
        patch(CANDIDATE)
        verify(CANDIDATE)

    new = sha256(target)
    print(f"\ncorrected workbook: {target.name}")
    print(f"new SHA-256: {new}")
    print("\nREMAINING STEPS (not done by this script, deliberately):")
    print(f"  1. set V34_SHA256 = \"{new}\" in scripts/build_v34_dashboard_data.py")
    print(f"  2. re-export {CSV.relative_to(ROOT)} from the workbook's Outcome_Data sheet")
    print("  3. update the one hardcoded row count: scripts/check_usability_ui.cjs:405")
    print("     (757 -> 758). build_site.py and deploy_integrity_check.py both count")
    print("     Outcome_Data directly and need no edit; the workbook's Summary sheet")
    print("     figure is updated by this script.")
    print("  4. re-run: build_v34_dashboard_data.py, 03_ROB2/model_rollup.py,")
    print("             04_GRADE/compute_new_model_grade.py,")
    print("             05_INTERPRETATION/build_interpretation_layer.py")
    print("  5. re-run validate_dashboard.py, check_tab_data.py, check_handover.py,")
    print("             build_site.py, deploy_integrity_check.py and the Playwright suites")
    print("  NOTE: the new Yang 2024 nausea row carries ROB2_RESULT_SPECIFIC_PENDING, so")
    print("        model_rollup.py will report one unjudged result for any model it feeds.")
    if not apply:
        print("\n(dry run: the locked workbook was NOT modified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
