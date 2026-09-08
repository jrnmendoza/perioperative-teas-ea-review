#!/usr/bin/env python3
"""
Build TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx.

v33 = v32 (unchanged, byte-for-byte preserved on disk) + source-audited
supplementary outcomes that were missing or under-extracted.

Design rules enforced here
--------------------------
* v32 is opened read-only and never written back. Its sha256 is asserted
  before and after so an accidental write cannot pass unnoticed.
* Every appended Outcome_Data row is source-verified against a local PDF.
  No value is copied from the supplement without opening the source.
* Nothing is promoted into the strict 0-24 h opioid primary analysis.
  `Primary opioid meta-analysis eligible?` is "No" on every appended row.
* Median/IQR stays median/IQR. Binary stays binary. Counts are never
  multiplied by a dose to manufacture MME.
* Multi-arm contrasts carry an explicit shared-control flag.
* Conflicting source values are recorded as conflicts, not silently resolved.

Usage: python3 08_V33_MASTER/build_v33_master.py [--check]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
VER = ROOT / "TEAS EA Verification"
V32 = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx"
SUP = VER / "TEAS_EA_v32_SUPPLEMENTARY_MISSED_OUTCOMES_FOR_CLAUDE_CODE.xlsx"
V33 = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx"

# v32 integrity baseline, captured from the committed git blob.
V32_SHA256 = "74fda7d176fae15af4aa5bbff318514f998adcf957a2f9cad67e8de55ab7b12f"

TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# Source-verified additions. Every entry below was read out of the PDF named in
# `src_pdf`; `src_loc` names the exact table or passage.
# ---------------------------------------------------------------------------
# Shorthand keys map onto Outcome_Data columns in append_outcome_rows().
A = "ADD"

ADDITIONS = [
    # ---------------- Yu 2020 -- Trials 2020;21:43 -------------------------
    dict(add=A, study="Yu 2020", cid="YU20_TEAS_vs_CTRL_RESCUEOP24",
         iv="Preoperative TEAS", cm="Control/no current (electrodes applied)",
         fam="Rescue opioid use", res="Participants requiring rescue sufentanil",
         tp="0-24 h postoperative", dtype="Events/total",
         rni=30, rnc=30, ani=30, anc=30,
         ei=13, ec=24, unit="participants", p="<0.01",
         other="Eligible for binary rescue-opioid meta-analysis (RR)",
         shared="No",
         qc="Binary incidence of rescue analgesia, NOT cumulative opioid dose. "
            "Rescue dose/number of administrations not reported, so no MME is derivable.",
         src_pdf="s13063-019-3892-4.pdf", src_loc="Table 3 (Cases of remedial analgesia)"),

    dict(add=A, study="Yu 2020", cid="YU20_TEAS_vs_CTRL_PAIN_POD1",
         iv="Preoperative TEAS", cm="Control/no current (electrodes applied)",
         fam="Pain", res="Resting pain VAS", tp="POD1 (~24 h)", dtype="Mean/SD",
         rni=30, rnc=30, ani=30, anc=30,
         mi=3.70, sdi=1.53, mc=4.73, sdc=1.53, unit="VAS 0-10", p="0.042",
         other="CONFLICTED - not eligible for pooling until the source SD conflict is resolved",
         shared="No",
         qc="SOURCE CONFLICT: Table 2 reports TEAS 3.70 (1.53); the abstract reports "
            "3.70 +/- 1.41 for the same result. Table 2's TEAS SD is also identical to the "
            "control SD (1.53), which is itself suspicious. Table 2 value recorded here as the "
            "primary transcription because a table outranks an abstract; the conflict is "
            "unresolved and this row must NOT be pooled. Author contact required.",
         src_pdf="s13063-019-3892-4.pdf", src_loc="Table 2 (VAS scores); abstract Results"),

    dict(add=A, study="Yu 2020", cid="YU20_TEAS_vs_CTRL_PAIN_POD2",
         iv="Preoperative TEAS", cm="Control/no current (electrodes applied)",
         fam="Pain", res="Resting pain VAS", tp="POD2 (~48 h)", dtype="Mean/SD",
         rni=30, rnc=30, ani=30, anc=30,
         mi=1.83, sdi=0.98, mc=2.30, sdc=0.95, unit="VAS 0-10", p="CONFLICTED (0.26 vs <0.05)",
         other="CONFLICTED - not eligible for pooling until the source conflicts are resolved",
         shared="No",
         qc="TWO SOURCE CONFLICTS. (1) SD: Table 2 gives TEAS 1.83 (0.98); the abstract gives "
            "1.83 +/- 0.88. (2) P value: the Results text states 'P = 0.042 and P = 0.26 for T1 "
            "and T2 respectively', i.e. POD2 non-significant, while Table 2 stars this result as "
            "P < 0.05 and the abstract claims P < 0.05 for both timepoints. Unresolved; do not pool. "
            "Author contact required.",
         src_pdf="s13063-019-3892-4.pdf", src_loc="Table 2; Results 'Pain assessment'; abstract"),

    # ---------------- Yao 2015 -- Evid Based Complement Alternat Med 2015 ----
    dict(add=A, study="Yao 2015", cid="YAO15_TEAS_vs_CTRL_RESCUECOUNT24",
         iv="Preoperative TEAS", cm="Control/no current",
         fam="Rescue opioid use", res="Cumulative number of rescue analgesia administrations",
         tp="0-24 h postoperative", dtype="Median/IQR",
         rni=35, rnc=36, ani=35, anc=36,
         medi=1, q1i=1, q3i=3, medc=3.5, q1c=2, q3c=7.8,
         unit="administrations", p="0.004",
         other="Eligible for rescue-opioid frequency synthesis (median/IQR); NOT an opioid dose",
         shared="No",
         qc="Rescue was IV sufentanil 0.05 ug/kg per administration. Do NOT multiply the median "
            "count by 0.05 ug/kg and a mean body weight to manufacture cumulative MME: the "
            "product of a median count and a mean weight is not the median or mean of the "
            "individual-level product, and no patient-level data are available.",
         src_pdf="039_yao_2015.pdf", src_loc="Table 3 (Cumulative number of rescue analgesia)"),

    dict(add=A, study="Yao 2015", cid="YAO15_TEAS_vs_CTRL_TIMETORESCUE",
         iv="Preoperative TEAS", cm="Control/no current",
         fam="Rescue analgesia", res="Time to first rescue analgesia",
         tp="0-24 h postoperative", dtype="Median/range",
         rni=35, rnc=36, ani=35, anc=36,
         medi=59, q1i=31, q3i=1440, medc=47, q1c=13, q3c=196,
         unit="minutes", p="0.039",
         other="Narrative / time-to-event secondary; dispersion is a reported range, not an IQR",
         shared="No",
         qc="The intervention arm's upper bound of 1440 min is the full 24-h observation window, "
            "i.e. censoring at end of follow-up. Treating this as an IQR bound would be wrong; "
            "it is a range. Not pooled as a mean difference.",
         src_pdf="039_yao_2015.pdf", src_loc="Table 3 (Time to first rescue analgesia)"),

    dict(add=A, study="Yao 2015", cid="YAO15_TEAS_vs_CTRL_NAUSEA24",
         iv="Preoperative TEAS", cm="Control/no current",
         fam="PONV", res="Postoperative nausea", tp="0-24 h postoperative",
         dtype="Events/total", rni=35, rnc=36, ani=35, anc=36,
         ei=17, ec=26, unit="participants", p="0.041",
         other="Eligible for nausea meta-analysis (RR)", shared="No",
         qc="Reported as 17 (48.6%) vs 26 (72.2%); denominators confirmed from Table 3 headers.",
         src_pdf="039_yao_2015.pdf", src_loc="Table 3 (Nausea)"),

    dict(add=A, study="Yao 2015", cid="YAO15_TEAS_vs_CTRL_VOMIT24",
         iv="Preoperative TEAS", cm="Control/no current",
         fam="PONV", res="Postoperative vomiting", tp="0-24 h postoperative",
         dtype="Events/total", rni=35, rnc=36, ani=35, anc=36,
         ei=7, ec=19, unit="participants", p="0.004",
         other="Eligible for vomiting meta-analysis (RR)", shared="No",
         qc="Source-extracted during verification of the supplementary nausea row; the "
            "supplement did not list it. Reported as 7 (20.0%) vs 19 (52.8%).",
         src_pdf="039_yao_2015.pdf", src_loc="Table 3 (Vomiting)"),

    # ---------------- Zhu 2022 -- Acupunct Med 2022;40(5):415-424 -----------
    # Multi-arm: three active arms share ONE usual-care comparator (n=101).
    dict(add=A, study="Zhu 2022", cid="ZHU22_PRE_vs_USUAL_INTRAOPSUF",
         iv="EA day before surgery", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative sufentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=103, rnc=103, ani=101, anc=101,
         mi=38.1, sdi=4.97, mc=37.8, sdc=4.87, unit="ug sufentanil", p="0.892 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="Reported in Table 1 among baseline/anaesthesia parameters, with a single 4-group "
            "omnibus P (0.892); no pairwise contrast is reported. Do not enter more than one "
            "Zhu 2022 contrast into a pairwise model without splitting the shared control.",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative sufentanil)"),

    dict(add=A, study="Zhu 2022", cid="ZHU22_30MIN_vs_USUAL_INTRAOPSUF",
         iv="EA 30 min before surgery", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative sufentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=104, rnc=103, ani=98, anc=101,
         mi=39.1, sdi=4.83, mc=37.8, sdc=4.87, unit="ug sufentanil", p="0.892 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="See ZHU22_PRE_vs_USUAL_INTRAOPSUF.",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative sufentanil)"),

    dict(add=A, study="Zhu 2022", cid="ZHU22_COMB_vs_USUAL_INTRAOPSUF",
         iv="EA day before + 30 min before", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative sufentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=103, rnc=103, ani=100, anc=101,
         mi=39.0, sdi=5.12, mc=37.8, sdc=4.87, unit="ug sufentanil", p="0.892 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="See ZHU22_PRE_vs_USUAL_INTRAOPSUF.",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative sufentanil)"),

    dict(add=A, study="Zhu 2022", cid="ZHU22_PRE_vs_USUAL_INTRAOPREMI",
         iv="EA day before surgery", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative remifentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=103, rnc=103, ani=101, anc=101,
         mi=0.58, sdi=0.23, mc=0.57, sdc=0.26, unit="mg remifentanil", p="0.948 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="Table 1 baseline/anaesthesia parameter with a single 4-group omnibus P (0.948).",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative remifentanil)"),

    dict(add=A, study="Zhu 2022", cid="ZHU22_30MIN_vs_USUAL_INTRAOPREMI",
         iv="EA 30 min before surgery", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative remifentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=104, rnc=103, ani=98, anc=101,
         mi=0.58, sdi=0.23, mc=0.57, sdc=0.26, unit="mg remifentanil", p="0.948 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="See ZHU22_PRE_vs_USUAL_INTRAOPREMI.",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative remifentanil)"),

    dict(add=A, study="Zhu 2022", cid="ZHU22_COMB_vs_USUAL_INTRAOPREMI",
         iv="EA day before + 30 min before", cm="Usual care alone",
         fam="Intraoperative opioid", res="Intraoperative remifentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=103, rnc=103, ani=100, anc=101,
         mi=0.50, sdi=0.25, mc=0.57, sdc=0.26, unit="mg remifentanil", p="0.948 (4-group omnibus)",
         other="Eligible for intraoperative-opioid synthesis ONLY with multi-arm handling",
         shared="Yes - shared usual-care comparator (n=101) across three active arms",
         qc="See ZHU22_PRE_vs_USUAL_INTRAOPREMI.",
         src_pdf="covidence_381_full_article.pdf", src_loc="Table 1 (Intraoperative remifentanil)"),

    # ---------------- Pan 2023 -- J Pain Res 2023;16 ------------------------
    dict(add=A, study="Pan 2023", cid="PAN23_TEAS_vs_CTRL_INTRAOPREMI",
         iv="TEAS", cm="Control/usual care",
         fam="Intraoperative opioid", res="Intraoperative remifentanil",
         tp="Intraoperative", dtype="Mean/SD",
         rni=53, rnc=52, ani=52, anc=53,
         mi=740.1, sdi=276.9, mc=854.0, sdc=287.5, unit="ug remifentanil", p="0.04",
         other="Eligible for intraoperative-opioid meta-analysis (MD)", shared="No",
         qc="Analysis Ns taken from the Table 2 column headers (Group T N=52, Group C N=53) "
            "against 105 randomized, i.e. post-randomization exclusions occurred. Existing RoB 2 "
            "concern for this trial is retained and NOT downgraded by this addition.",
         src_pdf="getfile.php-4.pdf", src_loc="Table 2 (Duration Remifentanil, ug)"),

    # ---------------- Yang 2020 -- Med Sci Monit 2020 -----------------------
    dict(add=A, study="Yang 2020", cid="YANG20_EA_vs_UC_DEFECATION",
         iv="EA + usual care", cm="Usual care",
         fam="GI recovery", res="Time to first defecation", tp="Postoperative",
         dtype="Mean/SD", rni=30, rnc=29, ani=29, anc=28,
         mi=53.9, sdi=6.0, mc=57.5, sdc=7.2, unit="hours", p="0.046",
         other="Eligible for GI-recovery meta-analysis (MD)", shared="No",
         qc="Analysis Ns mirror the existing v32 first-flatus row for this trial (29/28 of 30/29 "
            "randomized; 57 of 59 completed). Open-label design; existing RoB concern retained.",
         src_pdf="covidence_464_verified.pdf", src_loc="Abstract Results; GI recovery table"),

    # ---------------- Liang 2021 -- Evid Based Complement Alternat Med ------
    dict(add=A, study="Liang 2021", cid="LIANG21_TEAS_vs_CTRL_QOR40_24H",
         iv="Preoperative TEAS", cm="Control/no stimulation",
         fam="Quality of recovery", res="Global QoR-40", tp="24 h (T11)",
         dtype="Mean/SD", rni=37, rnc=38, ani=35, anc=35,
         mi=191.7, sdi=4.4, mc=189.1, sdc=4.3, unit="QoR-40 points", p="0.007",
         other="Eligible for QoR-40 meta-analysis (MD)", shared="No",
         qc="T11 is defined in the source as postoperative 24 hours. Analysis N 35/35 taken from "
            "the CONSORT flow diagram (Figure 2), against 37/38 allocated.",
         src_pdf="014_liang_2021.pdf", src_loc="Table 4; Results 3.3; Methods 2.7 (T11 definition)"),

    dict(add=A, study="Liang 2021", cid="LIANG21_TEAS_vs_CTRL_QOR40_48H",
         iv="Preoperative TEAS", cm="Control/no stimulation",
         fam="Quality of recovery", res="Global QoR-40", tp="48 h (T12)",
         dtype="Mean/SD", rni=37, rnc=38, ani=35, anc=35,
         mi=195.3, sdi=1.9, mc=193.3, sdc=3.0, unit="QoR-40 points", p="<0.001",
         other="Eligible for QoR-40 meta-analysis (MD) at 48 h", shared="No",
         qc="T12 is defined in the source as postoperative 48 hours.",
         src_pdf="014_liang_2021.pdf", src_loc="Table 4; Results 3.3; Methods 2.7 (T12 definition)"),

    dict(add=A, study="Liang 2021", cid="LIANG21_TEAS_vs_CTRL_ANALGREQ",
         iv="Preoperative TEAS", cm="Control/no stimulation",
         fam="Rescue analgesia", res="Postoperative analgesia requirement (metric undefined)",
         tp="Early postoperative period - exact window not stated",
         dtype="Reported as value (dispersion); statistic type ambiguous",
         rni=37, rnc=38, ani=35, anc=35,
         mi=3.8, sdi=1.9, mc=5.0, sdc=2.9, unit="UNRESOLVED - source does not define the metric",
         p="0.045",
         other="HOLD - narrative only. Not eligible for any pooled analysis.",
         shared="No",
         qc="HOLD. The source describes this as 'the number of patients who required extra "
            "analgesia', but 3.8 (1.9) and 5.0 (2.9) cannot be a count of patients out of 35 - "
            "the wording and the statistic are mutually inconsistent. Unit, metric and time "
            "window are all unresolved. Do NOT interpret as mg morphine or MME. Author contact "
            "required.",
         src_pdf="014_liang_2021.pdf", src_loc="Table 4; Results 3.3; abstract"),
]

# Supplement rows judged ALREADY PRESENT in v32 (verified identical).
ALREADY_PRESENT = [
    ("Yao 2015", "Global QoR-40", "24 h", "176.5 (10.2) vs 164.8 (14.7) - identical to v32"),
    ("Huang 2025", "Time to first flatus", "Postoperative", "36.4 (8.0) vs 42.2 (8.5) - identical to v32"),
    ("Huang 2025", "Time to first defecation", "Postoperative", "46.0 (8.0) vs 51.3 (9.4) - identical to v32"),
    ("Gao 2021", "Postoperative paralytic ileus", "Through POD5", "98/303 vs 126/307 - identical to v32"),
    ("Gao 2021", "Time to first flatus", "Postoperative", "63.4 (29.0) vs 76.3 (37.9) - identical to v32"),
    ("Gao 2021", "Time to first defecation", "Postoperative", "106.7 (65.6) vs 121.5 (65.6) - identical to v32"),
]

# Extraction-target rows: outcome confirmed to exist, exact values not supplied.
EXTRACTION_TARGETS = [
    "Zhu 2022", "Yang 2020", "Pan 2023", "Lu 2022", "Li 2021", "Gu 2019",
    "Huang 2025", "Gao 2021", "Jiang 2026", "Wang 2023", "Tu 2024", "Sun 2017",
    "Sim 2002", "Lu 2021", "Long 2025", "Wang 2024", "Zheng 2025",
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_v32_intact(stage: str) -> None:
    got = sha256(V32)
    if got != V32_SHA256:
        raise SystemExit(
            f"ABORT ({stage}): v32 master has changed.\n"
            f"  expected {V32_SHA256}\n  found    {got}\n"
            "v32 must remain byte-identical. Restore it from git before continuing."
        )


def row_value(cols: list[str], spec: dict) -> list:
    """Map an ADDITIONS entry onto the Outcome_Data column order."""
    m = {
        "Canonical study": spec["study"],
        "Comparison ID": spec["cid"],
        "Intervention arm": spec["iv"],
        "Comparator arm": spec["cm"],
        "Outcome family": spec["fam"],
        "Outcome/result": spec["res"],
        "Timepoint/window": spec["tp"],
        "Data type": spec["dtype"],
        "Randomized n intervention": spec.get("rni"),
        "Randomized n comparator": spec.get("rnc"),
        "Analyzed n intervention": spec.get("ani"),
        "Analyzed n comparator": spec.get("anc"),
        "Mean intervention": spec.get("mi"),
        "SD intervention": spec.get("sdi"),
        "Median intervention": spec.get("medi"),
        "Q1 intervention": spec.get("q1i"),
        "Q3 intervention": spec.get("q3i"),
        "Events intervention": spec.get("ei"),
        "Mean comparator": spec.get("mc"),
        "SD comparator": spec.get("sdc"),
        "Median comparator": spec.get("medc"),
        "Q1 comparator": spec.get("q1c"),
        "Q3 comparator": spec.get("q3c"),
        "Events comparator": spec.get("ec"),
        "Unit/scale": spec["unit"],
        "Reported P": spec.get("p"),
        "Directly reported?": "Yes",
        "Derived/converted?": "No",
        "Derived effect measure": "",
        "Derived effect": "",
        "Exact 0-24 h postoperative opioid?": "No",
        "Primary opioid meta-analysis eligible?": "No",
        "Other analysis eligibility": spec["other"],
        "Shared-control / multi-arm issue": spec["shared"],
        "Source-QC issue": spec["qc"],
        "Source location": spec["src_loc"],
        "Source PDF URL": f"local: TEAS EA Verification/Source PDFs/{spec['src_pdf']}",
        "Record status": "SOURCE-VERIFIED (v33 supplementary integration)",
    }
    return [m.get(c, "") for c in cols]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()

    for p in (V32, SUP):
        if not p.exists():
            raise SystemExit(f"ABORT: required input missing: {p}")

    assert_v32_intact("before build")
    print(f"v32 integrity OK  sha256={V32_SHA256[:16]}...")
    print(f"  v32: {V32}")
    print(f"  sup: {SUP}")

    if args.check:
        print(f"\n--check: {len(ADDITIONS)} additions staged, nothing written.")
        return 0

    # Work on a copy so v32 itself is never opened for write.
    shutil.copyfile(V32, V33)
    wb = openpyxl.load_workbook(V33)

    # v32 carries 596 formula cells (Outcome_Data 522, Study_Master 63,
    # Summary 11). openpyxl cannot evaluate formulas and discards Excel's
    # cached results on save, so a naive copy would hand every downstream
    # consumer reading with data_only=True a None for those cells -- silently
    # emptying 190 of the 364 v32 outcome rows. Materialise the cached values
    # from a data_only read before writing, so v33 is self-contained and does
    # not depend on Excel recalculating it.
    cached = openpyxl.load_workbook(V32, data_only=True)
    frozen = 0
    for ws in wb.worksheets:
        if ws.title not in cached.sheetnames:
            continue
        src = cached[ws.title]
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    cell.value = src.cell(row=cell.row, column=cell.column).value
                    frozen += 1
    print(f"Materialised {frozen} formula cells to their cached values")

    od = wb["Outcome_Data"]
    cols = [c.value for c in od[1]]
    before = od.max_row - 1

    for spec in ADDITIONS:
        od.append(row_value(cols, spec))
    after = od.max_row - 1
    print(f"\nOutcome_Data: {before} -> {after} rows (+{after - before})")

    # ---- v33_Change_Log ----------------------------------------------------
    if "v33_Change_Log" in wb.sheetnames:
        del wb["v33_Change_Log"]
    cl = wb.create_sheet("v33_Change_Log")
    hdr = ["Study", "Outcome", "Timepoint", "Change type", "Old v32 status/value",
           "New v33 status/value", "Source", "Reason", "Analysis consequence"]
    cl.append(hdr)
    for spec in ADDITIONS:
        if spec.get("ei") is not None:
            newv = f"{spec['ei']}/{spec['ani']} vs {spec['ec']}/{spec['anc']}"
        elif spec.get("medi") is not None:
            newv = (f"med {spec['medi']} ({spec['q1i']}-{spec['q3i']}) vs "
                    f"{spec['medc']} ({spec['q1c']}-{spec['q3c']})")
        else:
            newv = f"{spec['mi']}+/-{spec['sdi']} vs {spec['mc']}+/-{spec['sdc']}"
        hold = spec["other"].startswith(("HOLD", "CONFLICTED"))
        cl.append([
            spec["study"], spec["res"], spec["tp"], "ADDED (source-verified)",
            "Absent from v32 Outcome_Data", f"{newv} {spec['unit']}",
            f"{spec['src_pdf']} - {spec['src_loc']}",
            "Identified by the supplementary missed-outcome audit; verified against the local source PDF.",
            "Held / narrative only - not pooled" if hold else spec["other"],
        ])
    for study, res, tp, note in ALREADY_PRESENT:
        cl.append([study, res, tp, "NO CHANGE (already present)", note,
                   "unchanged", "v32 Outcome_Data",
                   "Supplement row duplicates an existing source-verified v32 row.",
                   "None - no duplicate row created"])

    # ---- v33_Supplement_Reconciliation ------------------------------------
    if "v33_Supplement_Reconciliation" in wb.sheetnames:
        del wb["v33_Supplement_Reconciliation"]
    sr = wb.create_sheet("v33_Supplement_Reconciliation")
    sr.append(["Supplement row", "Study", "Outcome family", "Outcome/result",
               "Timepoint/window", "Data readiness (supplement)", "Match class",
               "Disposition", "Basis"])

    swb = openpyxl.load_workbook(SUP, data_only=True)
    sup_rows = list(swb["Missed_Data_v32"].iter_rows(values_only=True))[1:]

    added_keys = {(a["study"], a["res"]) for a in ADDITIONS}
    present_keys = {(s, r) for s, r, _, _ in ALREADY_PRESENT}

    counts = {"ADDED": 0, "ALREADY PRESENT": 0, "HELD": 0,
              "SOURCE VERIFICATION NEEDED": 0, "NOT ANALYSIS ELIGIBLE": 0}

    for i, r in enumerate(sup_rows, 1):
        study = (r[0] or "").strip()
        fam = (r[1] or "").strip()
        res = (r[2] or "").strip()
        tp = (r[3] or "").strip()
        readiness = (r[14] or "").strip()

        if readiness.startswith("SOURCE-EXTRACT"):
            cls, disp = "G. requires source verification", "SOURCE VERIFICATION NEEDED"
            basis = ("Supplement supplies no numerical values; recorded as an unresolved "
                     "extraction target. No value invented.")
        elif "HOLD" in readiness:
            cls, disp = "C. present but incomplete/undefined", "HELD"
            basis = "Metric/unit/window undefined in the source; added as a HOLD row, not pooled."
        elif any(study == s and res.lower().startswith(pr.split()[0].lower())
                 for s, pr in present_keys):
            cls, disp = "B. already present identically", "ALREADY PRESENT"
            basis = "Matches an existing source-verified v32 Outcome_Data row; no duplicate created."
        else:
            matched = any(study == s for s, _ in added_keys)
            if matched:
                cls, disp = "A. genuinely missing from v32", "ADDED"
                basis = "Verified against the local source PDF and appended to Outcome_Data."
            else:
                cls, disp = "G. requires source verification", "SOURCE VERIFICATION NEEDED"
                basis = "Not verifiable from a locally available source; left unresolved."

        # exact overrides for the six duplicate rows
        for s, pres, ptp, note in ALREADY_PRESENT:
            if study == s and res.lower().startswith(pres.split()[0].lower()) and pres.split()[-1].lower() in res.lower():
                cls, disp = "B. already present identically", "ALREADY PRESENT"
                basis = note
        counts[disp] = counts.get(disp, 0) + 1
        sr.append([i, study, fam, res, tp, readiness, cls, disp, basis])

    # ---- README / Summary version stamps -----------------------------------
    rm = wb["README"]
    rm.append([])
    rm.append(["v33 INTEGRATION", TODAY])
    rm.append(["Base master", V32.name])
    rm.append(["Base master sha256", V32_SHA256])
    rm.append(["Supplement", SUP.name])
    rm.append(["Outcome rows (v32)", before])
    rm.append(["Outcome rows (v33)", after])
    rm.append(["Canonical studies", wb["Study_Master"].max_row - 1])
    rm.append(["Primary-outcome protection",
               "No appended row is eligible for the strict 0-24 h cumulative opioid primary "
               "analysis. Strict primary k remains 7."])
    rm.append(["New sheets", "v33_Change_Log; v33_Supplement_Reconciliation"])

    for ws in (cl, sr):
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="1F2937")
        ws.freeze_panes = "A2"

    wb.save(V33)
    assert_v32_intact("after build")

    print(f"\nWrote {V33.name}")
    print(f"  sheets: {len(wb.sheetnames)}")
    print(f"  Outcome_Data rows: {after}")
    print(f"  v33_Change_Log rows: {cl.max_row - 1}")
    print(f"  v33_Supplement_Reconciliation rows: {sr.max_row - 1}")
    print("\nSupplement disposition:")
    for k, v in counts.items():
        print(f"    {k:<28} {v}")
    print(f"\nv32 integrity re-verified after write: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
