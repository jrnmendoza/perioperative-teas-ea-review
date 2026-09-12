#!/usr/bin/env python3
"""
Adopt one identity convention for the Yeh lumbar-spine pair, across every artefact.

THE DECISION (review team, 2026-09-12)
    Yeh 2010 = Altern Ther Health Med 2010;16(6):10-18   (Covidence 823, PMID 21280458)
    Yeh 2011 = Int J Nurs Stud 2011;48(6):703-709        (Covidence 828, PMID 21084087,
                                                          DOI 10.1016/j.ijnurstu.2010.10.009)

WHY THIS DIRECTION
Study_Master carried an "Identity correction" reading "Yeh 2010 (ATHM) -> Yeh 2011"
that was never propagated anywhere else. scripts/audit_yeh_identity_convention.py
counts the sides by each file's own numbers: 15 files -- every file holding
arm-level data, including Outcome_Data_AF_LOCK, every Stata input, the
v34_reconciliation extracts and the 07_TIERED_V33 working set -- already used
Yeh 2010 = Altern Ther Health Med. One file, Study_Master itself, used the other.
Correcting the one is a documentation fix; re-cutting the fifteen would mean
re-cutting the analytical data layer, including inputs to Stata runs whose logs
are committed and cannot be regenerated here.

WHAT THIS TOUCHES
Only identity metadata. No arm denominator, mean, SD, effect estimate, RoB 2
judgement or GRADE rating is read or written. Both Yeh records are on
DUPLICATE-OVERLAP HOLD in the lock (include_strict = include_sensitivity = 0 on
every row), so no synthesis reads either, and the study count of 69 is unchanged
because the pair counts once whichever way it resolves.

  Study_Master, both in the v34 workbook and in the exported CSV
      Identity correction, Antigravity study label, Antigravity study key,
      Covidence internal ID, Candidate source result summary
  dashboard/data.js
      citation, doi, pmid, country_evidence, population.arm1_female,
      unit_of_analysis_note

The workbook is edited by replacing the affected cell values inside its XML and
rewriting the archive with every other part byte-identical. It is a 48-sheet
2.2 MB lock with tables and drawings; an openpyxl load/save round-trip would
rewrite all of it.

Usage:  python3 scripts/apply_yeh_identity_correction.py [--check]
"""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "TEAS EA Verification" / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
SM_CSV = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets" / "Study_Master.csv"
DATA_JS = ROOT / "dashboard" / "data.js"
SHEET_PART = "xl/worksheets/sheet2.xml"   # Study_Master; asserted below

PROVENANCE = ("Re-assigned 2026-09-12 to match Outcome_Data_AF_LOCK and the 14 other "
              "files holding arm-level data; see "
              "05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md")

# Study_Master identity fields, by our canonical key, in the adopted direction.
SM_TARGET = {
    "Yeh 2010": {   # Altern Ther Health Med 2010
        "Identitycorrection": f"Antigravity \"Yeh 2010 (ATHM)\" (Covidence 823) -> Yeh 2010. "
                              f"{PROVENANCE}",
        "Antigravitystudylabel": "Yeh 2010 (ATHM)",
        "Antigravitystudykey": "823",
        "CovidenceinternalID": "1879897273",
        "Candidatesourceresultsummary":
            "**Cumulative postoperative systemic opioid consumption at 24h (PRIMARY)**: EG1 "
            "True AES (n=33) 18.6 ± 9.7 mg vs EG2 Sham AES (n=30) 21.6 ± 13.1 mg "
            "(P = 0.364...",
    },
    "Yeh 2011": {   # Int J Nurs Stud 2011
        "Identitycorrection": f"Antigravity \"Yeh 2010\" (Covidence 828, Int J Nurs Stud 2011) "
                              f"-> Yeh 2011. {PROVENANCE}",
        "Antigravitystudylabel": "Yeh 2010",
        "Antigravitystudykey": "828",
        "CovidenceinternalID": "1879897280",
        "Candidatesourceresultsummary":
            "**Cumulative postoperative systemic opioid consumption at 24h (PRIMARY)**: AES "
            "(n=30) 19.3 ± 9.7 mg vs Sham AES (n=30) 21.6 ± 13.1 mg (P = 0.443) "
            "[MD -2.30 m...",
    },
}

# CSV header -> workbook header (the workbook spaces its column names).
SM_COLUMNS = {
    "Identitycorrection": "Identity correction",
    "Antigravitystudylabel": "Antigravity study label",
    "Antigravitystudykey": "Antigravity study key",
    "CovidenceinternalID": "Covidence internal ID",
    "Candidatesourceresultsummary": "Candidate source-result summary",
}

REGISTER_TARGET = {
    "Yeh 2010": {
        "citation": "Yeh ML, et al. *Altern Ther Health Med*. 2010;16(6):10-18. PMID: 21280458",
        "journal": "Altern Ther Health Med",
        "doi": "",
        "pmid": "21280458",
        "country_evidence": "carried out by the orthopedic departments of a 4000-bed medical "
                            "center in northern Taiwan",
        "arm1_female": "22/33 (66.7%)",
        "unit_of_analysis_note":
            "Trial record for the study also reported as Yeh 2011. This record is the Altern "
            "Ther Health Med 2010;16(6):10-18 report (three arms, EG1 33 / EG2 30 / CG 31); "
            "Yeh 2011 is the Int J Nurs Stud 2011;48(6):703-709 report of the same cohort "
            "(30 per arm). Review team decision 2026-09-11: count once. Identity re-assigned "
            "2026-09-12 so that this key names the same publication here as it does in "
            "Outcome_Data_AF_LOCK and every other file holding arm-level data.",
    },
    "Yeh 2011": {
        "citation": "Yeh ML, et al. *Int J Nurs Stud*. 2011;48(6):703-709. "
                    "DOI: 10.1016/j.ijnurstu.2010.10.009. PMID: 21084087",
        "journal": "Int J Nurs Stud",
        "doi": "10.1016/j.ijnurstu.2010.10.009",
        "pmid": "21084087",
        "country_evidence": "Nursing Department, Veterans General Hospital, Taipei, Taiwan, ROC",
        "arm1_female": "20/30 (66.7%)",
        "unit_of_analysis_note":
            "Same trial as Yeh 2010. This record is the Int J Nurs Stud 2011;48(6):703-709 "
            "report (30 per arm); Yeh 2010 is the Altern Ther Health Med 2010;16(6):10-18 "
            "report of the same three-arm cohort by the same author team. Review team "
            "decision 2026-09-11: COUNT ONCE, with Yeh 2010 retained as the trial record. "
            "This record is its companion publication and must not contribute independently "
            "to any synthesis. Identity re-assigned 2026-09-12 so that this key names the "
            "same publication here as it does in Outcome_Data_AF_LOCK.",
    },
}

ARM_FIELDS = ("arm1_n", "arm2_n", "total_n")   # must NOT move; asserted below


def _sheet_xml() -> tuple[str, str]:
    """Return (part name, xml) for Study_Master, refusing to guess which sheet it is."""
    with zipfile.ZipFile(WORKBOOK) as z:
        wb = z.read("xl/workbook.xml").decode("utf-8")
        rid = re.search(r'name="Study_Master"[^>]*r:id="([^"]+)"', wb).group(1)
        rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
        # Attribute order is writer-dependent; accept either.
        m = (re.search(rf'Id="{rid}"[^>]*?Target="([^"]+)"', rels)
             or re.search(rf'Target="([^"]+)"[^>]*?Id="{rid}"', rels))
        if not m:
            raise SystemExit("could not resolve the Study_Master relationship target")
        target = m.group(1).lstrip("/")
        if target != SHEET_PART:
            raise SystemExit(f"Study_Master is {target}, expected {SHEET_PART}; refusing to edit")
        return target, z.read(target).decode("utf-8")


def _col_letters(header_row_xml: str) -> dict[str, str]:
    """Map workbook column name -> column letter, from the header row."""
    out = {}
    for c in re.finditer(r'<x:c r="([A-Z]+)\d+"[^>]*>\s*<x:v>(.*?)</x:v>', header_row_xml, re.S):
        out[_unescape(c.group(2))] = c.group(1)
    return out


def _unescape(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
             .replace("&apos;", "'").replace("&amp;", "&"))


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _rows(xml: str) -> list[tuple[int, int, str]]:
    """(row number, start, end) for every <x:row> in document order."""
    return [(int(m.group(1)), m.start(), m.end())
            for m in re.finditer(r'<x:row r="(\d+)".*?</x:row>', xml, re.S)]


def _cell_value(row_xml: str, letter: str) -> str | None:
    m = re.search(rf'<x:c r="{letter}\d+"[^>]*?(?:/>|>(.*?)</x:c>)', row_xml, re.S)
    if not m:
        return None
    inner = m.group(1)
    if not inner:
        return ""
    v = re.search(r"<x:v>(.*?)</x:v>", inner, re.S)
    return _unescape(v.group(1)) if v else ""


def _set_cell(row_xml: str, letter: str, value: str) -> str:
    """Replace one cell's value, keeping its style; write an empty cell for ''."""
    pat = re.compile(rf'(<x:c r="{letter}\d+"([^>]*?))(?:/>|>(.*?)</x:c>)', re.S)
    m = pat.search(row_xml)
    if not m:
        raise SystemExit(f"cell {letter} not present in row; refusing to invent one")
    attrs = m.group(2)
    style = re.search(r'\s+s="\d+"', attrs)
    style = style.group(0) if style else ""
    ref = re.search(rf'r="({letter}\d+)"', m.group(1)).group(1)
    if value == "":
        new = f'<x:c r="{ref}"{style} />'
    else:
        new = f'<x:c r="{ref}"{style} t="str"><x:v>{_escape(value)}</x:v></x:c>'
    return row_xml[:m.start()] + new + row_xml[m.end():]


def workbook_state() -> dict:
    _, xml = _sheet_xml()
    rows = _rows(xml)
    header = xml[rows[0][1]:rows[0][2]]
    cols = _col_letters(header)
    key_col = cols["Canonical study"]
    out = {}
    for _, s, e in rows[1:]:
        row = xml[s:e]
        key = _cell_value(row, key_col)
        if key in SM_TARGET:
            out[key] = {f: _cell_value(row, cols[SM_COLUMNS[f]]) for f in SM_TARGET[key]}
    return out


def apply_workbook() -> list[str]:
    part, xml = _sheet_xml()
    rows = _rows(xml)
    cols = _col_letters(xml[rows[0][1]:rows[0][2]])
    key_col = cols["Canonical study"]
    changed, pieces, last = [], [], 0
    for _, s, e in rows[1:]:
        row = xml[s:e]
        key = _cell_value(row, key_col)
        if key not in SM_TARGET:
            continue
        new_row = row
        for field, value in SM_TARGET[key].items():
            letter = cols[SM_COLUMNS[field]]
            if _cell_value(new_row, letter) != value:
                changed.append(f"workbook Study_Master[{key}].{field}")
            new_row = _set_cell(new_row, letter, value)
        pieces.append((s, e, new_row))
    if not pieces:
        raise SystemExit("no Yeh rows found in the workbook's Study_Master sheet")

    new_xml, cursor = [], 0
    for s, e, row in pieces:
        new_xml.append(xml[cursor:s]); new_xml.append(row); cursor = e
    new_xml.append(xml[cursor:])
    new_xml = "".join(new_xml)

    # Rewrite the archive, copying every other part byte-for-byte.
    buf = io.BytesIO()
    with zipfile.ZipFile(WORKBOOK) as src, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = new_xml.encode("utf-8") if item.filename == part else src.read(item.filename)
            dst.writestr(item, data)
    shutil.copyfile(WORKBOOK, WORKBOOK.with_suffix(".xlsx.bak"))
    WORKBOOK.write_bytes(buf.getvalue())
    return changed


def csv_state() -> dict:
    rows = list(csv.DictReader(SM_CSV.open(encoding="utf-8-sig")))
    return {r["Canonicalstudy"]: {f: (r.get(f) or "") for f in SM_TARGET[r["Canonicalstudy"]]}
            for r in rows if r["Canonicalstudy"] in SM_TARGET}


def apply_csv() -> list[str]:
    with SM_CSV.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields, rows = reader.fieldnames, list(reader)
    changed = []
    for r in rows:
        key = r.get("Canonicalstudy")
        if key not in SM_TARGET:
            continue
        for field, value in SM_TARGET[key].items():
            if (r.get(field) or "") != value:
                changed.append(f"Study_Master.csv[{key}].{field}")
            r[field] = value
    with SM_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return changed


def _register() -> tuple[str, list, str]:
    raw = DATA_JS.read_text(encoding="utf-8")
    head, body = raw.split("window.STUDIES_DATA = ", 1)
    studies, end = json.JSONDecoder().raw_decode(body)
    return head, studies, body[end:]


def register_state() -> dict:
    _, studies, _ = _register()
    out = {}
    for s in studies:
        if s["key"] in REGISTER_TARGET:
            got = {f: s.get(f, "") for f in REGISTER_TARGET[s["key"]] if f != "arm1_female"}
            got["arm1_female"] = s["population"].get("arm1_female", "")
            out[s["key"]] = got
    return out


def apply_register() -> list[str]:
    head, studies, tail = _register()
    changed = []
    for s in studies:
        want = REGISTER_TARGET.get(s["key"])
        if not want:
            continue
        # The arm denominators are the half that is NOT in dispute. Assert they
        # are untouched, so this correction can never quietly move a denominator.
        before = {f: s["population"].get(f) for f in ARM_FIELDS}
        for field, value in want.items():
            if field == "arm1_female":
                if s["population"].get(field) != value:
                    changed.append(f"data.js[{s['key']}].population.arm1_female")
                s["population"][field] = value
            else:
                if s.get(field, "") != value:
                    changed.append(f"data.js[{s['key']}].{field}")
                s[field] = value
        after = {f: s["population"].get(f) for f in ARM_FIELDS}
        if before != after:
            raise SystemExit(f"{s['key']}: arm denominators moved ({before} -> {after}); "
                             "this correction must never touch them")
    DATA_JS.write_text(head + "window.STUDIES_DATA = "
                       + json.dumps(studies, ensure_ascii=False, indent=2) + tail,
                       encoding="utf-8")
    return changed


def main(check_only: bool) -> int:
    if check_only:
        stale = []
        for label, state, target in (("workbook", workbook_state(), SM_TARGET),
                                     ("Study_Master.csv", csv_state(), SM_TARGET),
                                     ("data.js", register_state(), REGISTER_TARGET)):
            for key, want in target.items():
                got = state.get(key)
                if got is None:
                    stale.append(f"{label}: {key} not found")
                    continue
                for field, value in want.items():
                    if got.get(field, "") != value:
                        stale.append(f"{label}[{key}].{field} is not the adopted value")
        if stale:
            print("OUT OF DATE:", file=sys.stderr)
            for s in stale:
                print(f"  {s}", file=sys.stderr)
            return 1
        print("Yeh identity is the adopted convention in the workbook, the exported "
              "Study_Master CSV and the register")
        return 0

    changed = apply_workbook() + apply_csv() + apply_register()
    print(f"applied {len(changed)} identity change(s)")
    for c in changed:
        print(f"  {c}")
    print(f"workbook backup written to {WORKBOOK.with_suffix('.xlsx.bak').name}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
