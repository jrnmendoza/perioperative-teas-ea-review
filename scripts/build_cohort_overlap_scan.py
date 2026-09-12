#!/usr/bin/env python3
"""
Scan every included report for evidence that it shares a randomised cohort with
another report, and record what the register says about each candidate.

WHY
PRISMA 2020 separates reports from studies, and this review has one confirmed
pair (Yeh 2010 / Yeh 2011 -- see the 2026-09-11 unit-of-analysis amendment). A
single declared pair is only trustworthy if the same test was applied to the
other 68 reports. This script applies it, so "69 studies from 70 reports" is a
scanned conclusion rather than an assumption that nothing else overlaps.

WHAT IT DOES NOT DO
It does not merge anything. A candidate is emitted for manual review with the
fields that made it a candidate; the decision to call two reports one study
stays with the review team and lives in 05_study_linkage/cohorts/.

It also records arm-level denominators that contradict the report's own source
publication. Those are data-quality flags for the descriptive display only --
no effect estimate, RoB 2 judgment or GRADE rating reads these fields.

Usage:  python3 scripts/build_cohort_overlap_scan.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "dashboard" / "data.js"
CHARS_JS = ROOT / "dashboard" / "study_characteristics.js"
PDF_JS = ROOT / "dashboard" / "pdf_extracted.js"
OUT_JS = ROOT / "dashboard" / "cohort_overlap.js"
SHEETS = ROOT / "06_FINAL_ANALYSIS_V26" / "01_DATA" / "authoritative_sheets"

# RESOLVED 2026-09-12. Kept here, not deleted: a question this review asked three
# times deserves a standing record of how it was answered.
#
# The defect was that the two locked sheets named different publications for the
# same register key. Study_Master filed the Int J Nurs Stud paper under Yeh 2010
# on the strength of an "Identity correction" annotation; Outcome_Data_AF_LOCK and
# every other file holding arm-level data filed the Altern Ther Health Med paper
# there. dashboard/data.js mirrored both, so each of its two rows carried one
# paper's citation beside the other paper's arm denominators.
#
# scripts/audit_yeh_identity_convention.py counted the sides by each file's own
# numbers and found 15 to 1. The review team adopted the majority convention on
# 2026-09-12 and scripts/apply_yeh_identity_correction.py applied it to the one
# file on the other side, plus the register's citation metadata:
#
#     Yeh 2010 = Altern Ther Health Med 2010;16(6):10-18  (Covidence 823)
#     Yeh 2011 = Int J Nurs Stud 2011;48(6):703-709       (Covidence 828)
#
# No arm denominator, mean, SD, effect estimate, RoB 2 judgement or GRADE rating
# was touched; both records remain on DUPLICATE-OVERLAP HOLD and contribute to no
# synthesis, and the study count of 69 is unchanged.
#
# The two screens below now enforce the result rather than describe the problem:
# locked_sheet_disagreements() no longer reports the pair, and it fails the build
# if they ever diverge again.
ATTRIBUTION_CONFLICTS: list[dict] = []

RESOLVED_ATTRIBUTION = [{
    "studies": ["Yeh 2010", "Yeh 2011"],
    "resolved": "2026-09-12",
    "verdict": "Yeh 2010 = Altern Ther Health Med 2010;16(6):10-18 (Covidence 823); "
               "Yeh 2011 = Int J Nurs Stud 2011;48(6):703-709 (Covidence 828).",
    "why": "Two locked sheets disagreed about which key named which paper. Counted by each "
           "file's own numbers, 15 files already used this convention \u2014 "
           "Outcome_Data_AF_LOCK, every Stata input, all five v34_reconciliation extracts, "
           "the mirror of the locked workbook's Outcome_Data sheet and the 07_TIERED_V33 "
           "working set. One file, Study_Master, used the other, on the strength of an "
           "Identity correction annotation that had been propagated nowhere.",
    "applied_by": "scripts/apply_yeh_identity_correction.py",
    "audited_by": "scripts/audit_yeh_identity_convention.py",
    "record": "05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md",
    "not_touched": "No arm denominator, mean, SD, effect estimate, RoB 2 judgement or GRADE "
                   "rating. Both records stay on DUPLICATE-OVERLAP HOLD "
                   "(include_strict = include_sensitivity = 0 on every row), so no synthesis "
                   "reads either, and the study count of 69 is unchanged.",
    "superseded_findings": [
        "First reading: transposed arm denominators, naming arm1_n as the defective field.",
        "Second reading: inverted citation, naming the arm denominators as the reliable half.",
        "Both were partial. The lock disagreed with itself, so no single dashboard field "
        "was the wrong one.",
    ],
}]


# Baseline rows found wrong against the source PDF, and what the paper says instead.
#
# Two kinds have turned up so far. An "arm_swap" has the right study's values on the
# wrong arms. A "foreign_block" has another study's values entirely -- caught by
# duplicate_baseline_blocks() below, which compares every record's baseline row
# against every other's.
#
# The denominator screen below flags any sex count whose denominator is not that
# arm's analysed N. Most of its hits are explicable. These are the ones that were
# read against the paper and turned out to be a genuine arm swap.
#
# Only descriptive baseline fields are affected -- age, BMI, sex. The analysed
# denominators are NOT in question here and are not touched: for Gu 2019 they are
# confirmed three ways over (the paper's Table 1, the arm labels in the register,
# and Outcome_Data_AF_LOCK, which records Long-duration TEAS n = 58 against
# Sham/no-current TEAS n = 59 on all eight of its outcome rows).
BASELINE_CORRECTIONS = [{
    "kind": "arm_swap",
    "study": "Gu 2019",
    "status": "corrected",
    "corrected_on": "2026-09-12",
    "applied_by": "scripts/apply_baseline_arm_corrections.py",
    "summary": "Age, BMI and sex are each recorded against the opposite arm.",
    "source": "TEAS EA Verification/Source PDFs/covidence_1471_full_article.pdf",
    "source_location": "Table 1, Characteristics of patients (p4)",
    "quote": "Characteristics C-TEAS(n = 59) L-TEAS(n = 58) | Age (mean \u00b1 SD, year) "
             "56.67 \u00b1 6.23  57.59 \u00b1 7.32 | Sex Male 29  31 | Female 30  27 | "
             "BMI(mean \u00b1 SD, kg/m2) 21.84 \u00b1 2.78  22.71 \u00b1 2.54",
    "arm_assignment_confirmed_by": [
        "The paper: the intervention is the long-duration TEAS group (L-TEAS, n = 58); the "
        "comparator is C-TEAS (n = 59), whose stimulator output wires were broken so no "
        "current was delivered \u2014 a true sham, as the register's comparator_type says.",
        "Outcome_Data_AF_LOCK: all eight Gu 2019 rows record Intervention arm "
        "\u201cLong-duration TEAS\u201d with analysed n = 58 against Comparator arm "
        "\u201cSham/no-current TEAS\u201d with analysed n = 59.",
        "The register's own arm_n values (58 for the TEAS group, 59 for the Sham group) "
        "already match both.",
    ],
    "fields": [
        {"field": "arm1_age",    "register": "56.67 ± 6.23",  "source_says": "57.59 ± 7.32"},
        {"field": "arm2_age",    "register": "57.59 ± 7.32",  "source_says": "56.67 ± 6.23"},
        {"field": "arm1_bmi",    "register": "21.84 ± 2.78",  "source_says": "22.71 ± 2.54"},
        {"field": "arm2_bmi",    "register": "22.71 ± 2.54",  "source_says": "21.84 ± 2.78"},
        {"field": "arm1_female", "register": "30/59 (50.8%)", "source_says": "27/58 (46.6%)"},
        {"field": "arm2_female", "register": "27/58 (46.6%)", "source_says": "30/59 (50.8%)"},
    ],
    "also": "asa_status read \u201cASA I: 20 (33.9%), ASA II: 39 (66.1%)\u201d, which sums to "
            "59 and is the SHAM arm's distribution presented as if it were study-wide. The "
            "paper gives ASA I 23 / II 35 for the 58 patients in the TEAS arm. Both arms are "
            "now given.",
    "asa_status": {
        "register": "ASA I: 20 (33.9%), ASA II: 39 (66.1%)",
        "source_says": "TEAS arm \u2014 ASA I: 23/58 (39.7%), ASA II: 35/58 (60.3%); "
                       "Sham arm \u2014 ASA I: 20/59 (33.9%), ASA II: 39/59 (66.1%)",
    },
    "affects": "Descriptive baseline display only. No analysed denominator, effect estimate, "
               "risk-of-bias judgement or GRADE rating reads these fields.",
    "resolution": "Corrected 2026-09-12 on review-team sign-off: the six values were moved "
                  "back to the arms the paper reports them for, and asa_status was rewritten to "
                  "give both arms instead of the sham arm's distribution alone. The analysed "
                  "denominators were not touched. The 'register' column above records what the "
                  "register held BEFORE the correction; 'source_says' is what it holds now.",
}]


BASELINE_CORRECTIONS.append({
    "kind": "foreign_block",
    "study": "He 2026 (hepatectomy/JIS)",
    "status": "corrected",
    "corrected_on": "2026-09-12",
    "applied_by": "scripts/apply_baseline_arm_corrections.py",
    "summary": "The whole baseline row belonged to a different trial.",
    "source": "TEAS EA Verification/Source PDFs/covidence_25_verified.pdf",
    "source_location": "TABLE 1, Baseline characteristics of study population",
    "quote": "Characteristic TEAS (n = 80) Control (n = 79) | sex, no. (%) female 28 (35.0) "
             "26 (32.9) | age, mean \u00b1 SD, yrs 52.3 \u00b1 9.1  54.3 \u00b1 10.9 | "
             "BMI, mean \u00b1 SD, kg/m2 23.4 \u00b1 3.3  23.7 \u00b1 4.9 | ASA grade, no. (%) "
             "I 2 (2.5) 1 (1.3)  II 74 (92.5) 72 (91.1)  III 4 (5) 6 (7.6)",
    "arm_assignment_confirmed_by": [
        "Every value the register held was Liu 2026 (burn)'s, byte for byte \u2014 ages "
        "42.0 \u00b1 9.8 / 39.5 \u00b1 11.3, BMI 24.6 \u00b1 3.5 / 24.9 \u00b1 3.2, female "
        "9/43 and 10/43, ASA I 11 (25.6%) / II 32 (74.4%). Liu 2026's own Table 1 reports "
        "exactly those for its T and C groups of 43 each, so that record is correct and this "
        "one was carrying a copy.",
        "The denominator 43 appears nowhere in this paper as a group size; its only two "
        "occurrences are inside confidence intervals (0.43).",
        "The paper's own text corroborates its Table 1: \u201cThe mean (SD) age of "
        "participants was 53.3 (9.2) years; 54 patients were women (34.0%)\u201d. "
        "28 + 26 = 54, and 54/159 = 34.0%; the arm means weight to 53.3 years.",
        "The analysed denominators in the register (80 and 79) already matched the paper and "
        "Outcome_Data_AF_LOCK, and were not touched.",
    ],
    "fields": [
        {"field": "arm1_age",    "register": "42.0 ± 9.8",    "source_says": "52.3 ± 9.1"},
        {"field": "arm2_age",    "register": "39.5 ± 11.3",   "source_says": "54.3 ± 10.9"},
        {"field": "arm1_bmi",    "register": "24.6 ± 3.5",    "source_says": "23.4 ± 3.3"},
        {"field": "arm2_bmi",    "register": "24.9 ± 3.2",    "source_says": "23.7 ± 4.9"},
        {"field": "arm1_female", "register": "9/43 (20.9%)",  "source_says": "28/80 (35.0%)"},
        {"field": "arm2_female", "register": "10/43 (23.3%)", "source_says": "26/79 (32.9%)"},
    ],
    "asa_status": {
        "register": "ASA I: 11 (25.6%), ASA II: 32 (74.4%)",
        "source_says": "TEAS arm \u2014 ASA I: 2/80 (2.5%), ASA II: 74/80 (92.5%), "
                       "ASA III: 4/80 (5.0%); Sham arm \u2014 ASA I: 1/79 (1.3%), "
                       "ASA II: 72/79 (91.1%), ASA III: 6/79 (7.6%)",
    },
    "also": "The comparator classification was checked at the same time and is right: the paper "
            "says \u201cFor control group participants, electrodes were similarly placed but "
            "remained inactive\u201d, which is a sham, not usual care. The abstract's shorthand "
            "\u201ccontrol group (no stimulation)\u201d describes the current, not the "
            "electrodes.",
    "affects": "Descriptive baseline display only. No analysed denominator, effect estimate, "
               "risk-of-bias judgement or GRADE rating reads these fields.",
    "resolution": "Corrected 2026-09-12 on review-team sign-off, from the paper's own Table 1. "
                  "The 'register' column above records what the register held BEFORE the "
                  "correction; 'source_says' is what it holds now.",
})


BASELINE_CORRECTIONS.append({
    "kind": "wrong_denominator",
    "study": "Grech 2016",
    "status": "corrected",
    "corrected_on": "2026-09-12",
    "applied_by": "scripts/apply_baseline_arm_corrections.py",
    "summary": "The EA arm carried the whole trial's figures instead of its own.",
    "source": "TEAS EA Verification/Source PDFs/030_grech_2016_lund.pdf",
    "source_location": "Table 2, Distribution of the patients",
    "quote": "n Age (y) Weight (kg) T P F | All 20 48.15 \u00b1 2.45 81.16 \u00b1 4.27 11 9 18 | "
             "Control 9 52.33 \u00b1 4.08 85.00 \u00b1 6.22 5 4 9 | "
             "EA 11 44.73 \u00b1 2.68 77.70 \u00b1 5.97 6 5 9",
    "arm_assignment_confirmed_by": [
        "Table 2 gives the EA arm (n = 11) a mean age of 44.73 and the whole trial (n = 20) "
        "48.15. The register held 48.15 \u2014 the all-patients figure \u2014 on the EA arm. "
        "The control arm's 52.33 was already right.",
        "Table 2's dispersions are standard ERRORS, not SDs: 2.45 for n = 20 against ages "
        "spanning 32-72 is a standard error, and 2.45 \u00d7 \u221a20 = 10.96, which is exactly "
        "the figure the register carried. The control arm had already been converted the same "
        "way (4.08 \u00d7 \u221a9 = 12.24), so the EA arm follows it: 2.68 \u00d7 \u221a11 = 8.89.",
        "Sex: Table 2 records 9 female in each arm. With n = 11 that is 9/11 in the EA arm, not "
        "the 9/20 the register held \u2014 9 is the EA arm's own numerator over the whole "
        "trial's denominator. Table 1's per-patient listing shows the two men (patients 10 and "
        "12) are both EA, and the text confirms it: \u201cthe heterogeneous group (with both "
        "men and women) of EA was compared with the control group (with women only)\u201d.",
        "The control arm's 9/9 (100%) was already right and is unchanged.",
    ],
    "fields": [
        {"field": "arm1_age",    "register": "48.15 ± 10.96", "source_says": "44.73 ± 8.89"},
        {"field": "arm1_female", "register": "9/20 (45.0%)",  "source_says": "9/11 (81.8%)"},
    ],
    "also": "The arm ± values are SDs converted from the paper's standard errors, following the "
            "conversion already applied to the control arm. The source prints mean ± SEM.",
    "affects": "Descriptive baseline display only. No analysed denominator, effect estimate, "
               "risk-of-bias judgement or GRADE rating reads these fields.",
    "resolution": "Corrected 2026-09-12 on review-team sign-off. The 'register' column records "
                  "what the register held BEFORE the correction; 'source_says' is what it holds "
                  "now.",
})

BASELINE_CORRECTIONS.append({
    "kind": "wrong_denominator",
    "study": "Lee 2011",
    "status": "corrected",
    "corrected_on": "2026-09-12",
    "applied_by": "scripts/apply_baseline_arm_corrections.py",
    "summary": "Sex was reported over a denominator the trial never had, and a whole-trial age "
               "was shown as if it were each arm's.",
    "source": "TEAS EA Verification/Source PDFs/049_lee_2011.pdf",
    "source_location": "Abstract and Table 2, Description of subjects",
    "quote": "47 women were randomly allocated to four different groups. Except for those in the "
             "control group (Group 1, n = 13), a course of treatment was given of either sham "
             "(Group 2, n = 12), high-frequency stimulation (Group 3, n = 12), or low-frequency "
             "stimulation (Group 4, n = 10). [...] Table 2: Description of subjects. "
             "N Minimum Maximum Mean SD | Age (years old) 47 14.00 59.00 42.02 8.31",
    "arm_assignment_confirmed_by": [
        "Every participant was a woman: \u201c47 women were randomly allocated to four "
        "different groups\u201d, all undergoing hysterectomy. Each arm of the review's "
        "12-vs-12 contrast is therefore 12/12 (100%). The 20 the register used as a denominator "
        "is not a group size anywhere in this four-arm trial (13 / 12 / 12 / 10).",
        "Age is reported once, for the whole trial: Table 2 gives N = 47, mean 42.02, SD 8.31. "
        "The paper reports no per-arm age, so the register was showing a whole-trial mean on "
        "both arms as though it were arm-specific. It now says so on its face rather than being "
        "silently dropped, because the value itself is real and reported.",
        "The contrast the review uses is Group 3 (high-frequency, n = 12) against Group 2 "
        "(sham, n = 12); the register's arm denominators of 12 and 12 already matched.",
        "The whole trial's randomised N of 47 is already carried separately, read from this "
        "same paper, and is shown in the study drawer.",
    ],
    "fields": [
        {"field": "arm1_female", "register": "20/20 (100%)", "source_says": "12/12 (100%)"},
        {"field": "arm2_female", "register": "20/20 (100%)", "source_says": "12/12 (100%)"},
        {"field": "arm1_age", "register": "42.02 ± 8.31",
         "source_says": "42.02 ± 8.31 (whole trial, N = 47; per-arm age not reported)"},
        {"field": "arm2_age", "register": "42.02 ± 8.31",
         "source_says": "42.02 ± 8.31 (whole trial, N = 47; per-arm age not reported)"},
    ],
    "affects": "Descriptive baseline display only. No analysed denominator, effect estimate, "
               "risk-of-bias judgement or GRADE rating reads these fields.",
    "resolution": "Corrected 2026-09-12 on review-team sign-off. The age is kept rather than "
                  "marked not-reported, because the trial does report it \u2014 just not per "
                  "arm \u2014 and the value now carries that qualification with it.",
})


# Candidate pairs the review team has adjudicated against their source PDFs. An
# adjudication does not remove the pair from the scan -- the detection rule still
# has to find it, or the rule has quietly stopped working -- it records what the
# reading concluded and the evidence it rested on. "separate" pairs keep counting
# as two studies; a pair found to be one cohort would instead be declared in the
# register via duplicate_report_of, the way the Yeh pair is.
ADJUDICATED = {
    frozenset(("Chen 2015", "Chen 2015 (Hyperalgesia)")): {
        "verdict": "separate",
        "date": "2026-09-12",
        "record": "05_study_linkage/cohorts/chen_2015_thyroidectomy_pair.md",
        "summary": "Two separate trials by one group at one centre, run back to back.",
        "evidence": [
            "Separate ethics approvals from the same board: Chen 2015 cites "
            "\u201cethical approval from Fujian Provincial Hospital (Ref: K2014-12-003)\u201d; "
            "Chen 2015 (Hyperalgesia) cites \u201cthe Institutional Review Board of Fujian "
            "Provincial Hospital (Ref: K2014-07-003)\u201d.",
            "Non-overlapping recruitment: \u201cfrom January 2015 to May 2015\u201d versus "
            "\u201cfrom August 2014 to December 2014\u201d \u2014 the second trial had finished "
            "recruiting before the first began.",
            "Independent screening funnels: 91 assessed \u2192 3 ineligible, 4 declined "
            "\u2192 84 enrolled \u2192 83 analysed; versus 73 assessed \u2192 7 ineligible, "
            "6 declined \u2192 60 enrolled \u2192 59 analysed.",
            "Chen 2015 is prospectively registered as ClinicalTrials.gov NCT02333747; "
            "Chen 2015 (Hyperalgesia) states no registration.",
            "Different primary outcomes (QoR-40 at 24 h versus mechanical pain threshold), "
            "partly different author teams, and separate funding grants "
            "(2015J01373 versus 2012Y0012).",
        ],
        "shared_but_not_probative":
            "Same first author, centre, procedure, sex restriction, ASA and age eligibility, "
            "device and stimulation parameters \u2014 one group running a consistent protocol "
            "across consecutive trials, which is what made this a candidate worth reading.",
    },
}


# The two papers also disagree with each other about the size of the cohort they
# describe. That is recorded as a property of the linked pair, not of either report.
COHORT_SIZE_DISAGREEMENTS = [{
    "studies": ["Yeh 2010", "Yeh 2011"],
    "status": "adjudicated",
    "adjudicated_on": "2026-09-12",
    "summary": "The two reports of this trial state different cohort sizes, and one of them "
               "disagrees with itself.",
    "detail": "Yeh 2011 (Int J Nurs Stud 2011) shows 99 assessed for eligibility, 90 meeting "
              "inclusion criteria, and randomisation to 30 / 30 / 30. Yeh 2010 (Altern Ther "
              "Health Med 2010) states \"Ninety-nine patients undergoing lumbar spinal surgery "
              "were randomly assigned to one of three groups\" \u2014 but its own Table 2 gives "
              "groups of 33 / 30 / 31, which sum to 94, not 99. So the 99 is contradicted "
              "inside the paper that prints it, and 90 is contradicted by the companion.",
    "verdict": "Unresolvable from the two publications, and deliberately left so. Whether 90, 94 "
               "or 99 were randomised cannot be established without the trial's own records, and "
               "choosing one would be inventing it.",
    "why_nothing_depends_on_it": "No whole-trial randomised N is published for this trial in "
                                 "either record, so nothing in the review rests on the figure. "
                                 "Yeh 2011 carries a randomised denominator of 30 / 30 for the "
                                 "pairwise contrast the review uses, which its flow diagram "
                                 "states directly and which is not in dispute; Yeh 2010 carries "
                                 "none. Both records are on DUPLICATE-OVERLAP HOLD in the lock "
                                 "(include_strict = include_sensitivity = 0 on every row), so no "
                                 "synthesis reads either.",
    "affects": "Descriptive participant totals only, and not even those: the review's analysed "
               "total counts this trial once, through Yeh 2010's 63.",
    "record": "05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md",
}]


def _load(path: Path, marker: str):
    raw = path.read_text(encoding="utf-8")
    return json.JSONDecoder().raw_decode(raw.split(marker, 1)[1])[0]


def _surname(key: str) -> str:
    return re.sub(r"^#\d+\s*-\s*", "", key).split()[0].lower()


def build() -> dict:
    studies = _load(DATA_JS, "window.STUDIES_DATA = ")
    chars = _load(CHARS_JS, "window.STUDY_CHARACTERISTICS = ")
    pdf = _load(PDF_JS, "window.PDF_EXTRACTED = ")

    by_key = {s["key"]: s for s in studies}

    # --- declared links: what the register already asserts ---------------------
    declared = []
    for s in studies:
        if s.get("duplicate_report_of"):
            primary = s["duplicate_report_of"]
            if primary not in by_key:
                raise ValueError(f"{s['key']}: duplicate_report_of points at unknown {primary!r}")
            if by_key[primary].get("companion_report") != s["key"]:
                raise ValueError(f"{primary}: companion_report does not point back at {s['key']!r}")
            declared.append({
                "study_record": primary,
                "companion_report": s["key"],
                "note": s.get("unit_of_analysis_note") or "",
                "linkage_record": "05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md",
            })

    # --- the scan: every report pair sharing a first author -------------------
    # Shared first author is the screen; country, specialty, modality and the
    # reported denominators decide whether a pair is worth a human look. A pair
    # already declared as one study is reported as confirmed, not as a candidate.
    declared_pairs = {frozenset((d["study_record"], d["companion_report"])) for d in declared}
    candidates = []
    for i, a in enumerate(studies):
        for b in studies[i + 1:]:
            if _surname(a["key"]) != _surname(b["key"]):
                continue
            pair = frozenset((a["key"], b["key"]))
            shared = []
            if a.get("country") and a["country"] == b.get("country"):
                shared.append("country of conduct")
            if a.get("surgery_category") == b.get("surgery_category"):
                shared.append("surgical specialty")
            if a.get("modality") == b.get("modality"):
                shared.append("modality")
            pa, pb = chars.get(a["key"], {}), chars.get(b["key"], {})
            # Compared on content words, not on the exact string: the two Yeh
            # reports describe the same population as "nontraumatic lumbar spine
            # injury/disorders" and "non-traumatic lumbar spine disorders", and a
            # rule that required byte equality would have missed the one link the
            # review has already confirmed.
            proc_a, proc_b = _proc_words(pa, a), _proc_words(pb, b)
            if proc_a and proc_a == proc_b:
                shared.append("same surgical population")
            same_journal = _journal(a) and _journal(a) == _journal(b)
            if same_journal:
                shared.append("journal")
            if abs(a["year"] - b["year"]) <= 1:
                shared.append("publication year within 1")

            # Denominators are the discriminator: two reports of one cohort tend to
            # share at least one arm size, and two separate trials rarely do.
            arms_a = {a["population"]["arm1_n"], a["population"]["arm2_n"]}
            arms_b = {b["population"]["arm1_n"], b["population"]["arm2_n"]}
            shared_arm_n = sorted(arms_a & arms_b)
            same_total = a["population"]["total_n"] == b["population"]["total_n"]

            # Threshold: one author, one country, one specialty and one modality,
            # plus either the same surgical population or a shared arm denominator.
            # Looser than that and the scan returns same-surname coincidences from
            # a literature dominated by a few large Chinese centres; tighter and it
            # misses the Yeh pair, whose two papers analyse 63 and 60 participants.
            context = {"country of conduct", "surgical specialty", "modality"} <= set(shared)
            overlap = "same surgical population" in shared or bool(shared_arm_n)
            if not (context and overlap) and not (same_total and shared_arm_n):
                continue
            adj = ADJUDICATED.get(pair)
            if pair in declared_pairs:
                status = "confirmed"
            elif adj and adj["verdict"] == "separate":
                status = "adjudicated_separate"
            else:
                status = "flagged_for_review"
            candidates.append({
                "studies": sorted(pair),
                "status": status,
                "adjudication": adj,
                "shared": shared,
                "analysed_n": {a["key"]: a["population"]["total_n"],
                               b["key"]: b["population"]["total_n"]},
                "arm_n": {a["key"]: [a["population"]["arm1_n"], a["population"]["arm2_n"]],
                          b["key"]: [b["population"]["arm1_n"], b["population"]["arm2_n"]]},
                "shared_arm_n": shared_arm_n,
                "citations": {a["key"]: a["citation"], b["key"]: b["citation"]},
                "procedure": pa.get("surgery_procedure") or a.get("surgery_procedure"),
            })

    found_pairs = {frozenset(c["studies"]) for c in candidates}
    for pair, adj in ADJUDICATED.items():
        if pair not in found_pairs:
            raise ValueError(
                f"adjudication recorded for {sorted(pair)} but the scan no longer finds that "
                "pair; either the register changed or the detection rule drifted -- re-read "
                "the sources before deleting the adjudication")
        if not (ROOT / adj["record"]).exists():
            raise ValueError(f"{sorted(pair)}: adjudication record {adj['record']} is missing")

    for d in declared:
        if not any(set(c["studies"]) == {d["study_record"], d["companion_report"]}
                   for c in candidates):
            raise ValueError(
                f"scan did not re-find the declared link {d['study_record']} / "
                f"{d['companion_report']}; the detection rule has drifted and would no longer "
                "catch the duplication it was written for")

    # --- participant totals, counted once per study ---------------------------
    companions = {d["companion_report"] for d in declared}
    analysed_reports = sum(s["population"]["total_n"] for s in studies)
    analysed_studies = sum(s["population"]["total_n"] for s in studies
                           if s["key"] not in companions)
    # Randomised denominators come from two channels that are NOT additive: the
    # register records the randomised N of the pairwise contrast the review uses,
    # while the PDF extractor records the whole trial's randomised N, which for a
    # multi-arm trial is larger. Coverage is reported per channel and no
    # review-wide randomised total is published, because most studies record
    # neither and the two channels cannot be added together.
    contrast_randomised = [s["key"] for s in studies
                           if s["key"] not in companions and s["population"].get("randomized_total_n")]
    trial_randomised = [s["key"] for s in studies
                        if s["key"] not in companions
                        and (pdf.get(s["key"]) or {}).get("randomised_n")]
    either = sorted(set(contrast_randomised) | set(trial_randomised))

    return {
        "generated_by": "scripts/build_cohort_overlap_scan.py",
        "reports": len(studies),
        "studies": len(studies) - len(companions),
        "declared_links": declared,
        "candidates": sorted(candidates, key=lambda c: (
            {"flagged_for_review": 0, "adjudicated_separate": 1, "confirmed": 2}[c["status"]],
            c["studies"])),
        "attribution_conflicts": ATTRIBUTION_CONFLICTS,
        "baseline_corrections": BASELINE_CORRECTIONS,
        "duplicate_baseline_blocks": duplicate_baseline_blocks(studies),
        "resolved_attribution": RESOLVED_ATTRIBUTION,
        "denominator_mismatches": denominator_mismatches(studies),
        "locked_sheet_disagreements": locked_sheet_disagreements(),
        "cohort_size_disagreements": COHORT_SIZE_DISAGREEMENTS,
        "participants": {
            "analysed_across_reports": analysed_reports,
            "analysed_across_studies": analysed_studies,
            "deduplicated_by": sorted(companions),
            "randomised_contrast_recorded": sorted(contrast_randomised),
            "randomised_whole_trial_recorded": sorted(trial_randomised),
            "randomised_any_channel": either,
            "randomised_total_publishable": False,
            "randomised_total_reason":
                "The register records a randomised denominator for the pairwise contrast in "
                f"{len(contrast_randomised)} of the {len(studies) - len(companions)} studies, and "
                f"the source-PDF extraction records a whole-trial randomised N in "
                f"{len(trial_randomised)}. The two are different quantities and are not additive, "
                "and neither covers the review. A review-wide randomised participant total is "
                "therefore not reported; the analysed total is.",
        },
    }


def locked_sheet_disagreements() -> list[dict]:
    """
    Where Study_Master describes a study with arm sizes Outcome_Data_AF_LOCK does
    not have.

    Study_Master carries a prose result summary per study; AF_LOCK carries the
    arm-level data the analyses read. Every "(n = ...)" in the summary should be an
    arm size AF_LOCK also knows about. When one is not, the two sheets are
    describing different things under one key.

    MULTI-ARM AWARE. An earlier version took the FIRST TWO "(n = ...)" as an
    intervention/comparator pair and required that exact pair in AF_LOCK. For a
    multi-arm trial the summary lists the active arms consecutively, so the first
    two are two interventions, and the check flagged four perfectly consistent
    trials: Zhu 2022 (four groups), Lu 2021 and Jin 2023 (three each) and Wang 2024
    (two risk strata, pooled in the summary). All four were verified against their
    source publications on 2026-09-12 and are correct.

    Pooled figures are allowed too: Wang 2024's summary reports 68 and 70 for
    strata AF_LOCK holds as 33 + 35 and 35 + 35.

    Reported, never reconciled here: choosing which sheet is right is a decision
    about the locked master.
    """
    import csv
    sm_path, af_path = SHEETS / "Study_Master.csv", SHEETS / "Outcome_Data_AF_LOCK.csv"
    if not sm_path.exists() or not af_path.exists():
        return []

    arms: dict[str, set[int]] = {}
    pairs: dict[str, set] = {}
    for r in csv.DictReader(af_path.open(encoding="utf-8-sig")):
        key = r["Canonicalstudy"]
        got = []
        for field in ("Analyzednintervention", "Analyzedncomparator",
                      "Randomizednintervention", "Randomizedncomparator"):
            try:
                got.append(int(float(r[field])))
            except (ValueError, TypeError, KeyError):
                pass
        arms.setdefault(key, set()).update(got)
        try:
            pairs.setdefault(key, set()).add(
                (int(float(r["Analyzednintervention"])), int(float(r["Analyzedncomparator"]))))
        except (ValueError, TypeError, KeyError):
            pass

    summaries: dict[str, list[int]] = {}
    for r in csv.DictReader(sm_path.open(encoding="utf-8-sig")):
        key = r.get("Canonicalstudy") or ""
        ns = [int(x) for x in
              re.findall(r"\(n\s*=\s*(\d+)\)", r.get("Candidatesourceresultsummary") or "")]
        if ns:
            summaries[key] = ns

    # An unaccounted figure is the signal; a matching exchange is the EXPLANATION
    # for one. Exchange on its own is not evidence -- two trials with the same arm
    # sizes match by coincidence, and testing for it alone flagged eleven unrelated
    # pairs. The Yeh split was found by the conjunction, and one row naming both
    # studies is enough to act on.
    out = []
    for key, ns in summaries.items():
        known = arms.get(key)
        if not known:
            continue
        # A summary figure is accounted for if AF_LOCK has it as an arm, or if it is
        # the sum of two arms it does have (a pooled stratum).
        sums = {a + b for a in known for b in known}
        unaccounted = sorted({n for n in ns if n not in known and n not in sums})
        if not unaccounted:
            continue
        swapped_with = sorted(k for k, other in summaries.items()
                              if k != key and tuple(ns[:2]) in pairs.get(k, set())
                              and tuple(other[:2]) in pairs.get(key, set()))
        out.append({
            "study": key,
            "study_master_summary_arms": ns,
            "af_lock_arm_sizes": sorted(known),
            "unaccounted": unaccounted,
            "exchanged_with": swapped_with,
            "kind": "identity_split" if swapped_with else "arm_figures_differ",
        })
    return sorted(out, key=lambda d: (d["kind"] != "identity_split", d["study"]))


# Denominator mismatches that have already been adjudicated and are NOT going to be
# corrected, with the reason. These stay in the screen's output, flagged as
# explained, rather than being deleted: the screen should be able to show that it
# has been worked through, not merely that it is quiet.
EXPLAINED_DENOMINATORS = {
    ("El-Rakshy 2009", "arm1"): "The source cannot be reconciled with itself.",
    ("El-Rakshy 2009", "arm2"): "The source cannot be reconciled with itself.",
}
EXPLAINED_DETAIL = {
    "El-Rakshy 2009":
        "Confirmed 2026-09-09 by an independent re-read of the primary source: the "
        "publication's intervention-group denominators are irreconcilable across its flow "
        "diagram, Results text, Table 1, abstract and Table 3. There is no correct value to "
        "restore, and choosing one would be inventing it. The finding is already carried where "
        "it belongs \u2014 it is the basis of this trial's High RoB 2 Domain 3 judgement, which "
        "in turn drives a GRADE downgrade, so the analysis already reflects it.",
}


def duplicate_baseline_blocks(studies: list[dict]) -> list[dict]:
    """
    Records sharing an identical baseline row with another record.

    Two trials do not independently produce the same ages, BMIs, sex counts and
    ASA distribution. When they appear to, one record is carrying the other's
    block -- which is how He 2026 (hepatectomy/JIS) came to hold Liu 2026 (burn)'s
    baselines, denominators of 43 and all, for a trial that analysed 80 and 79.

    A block has to carry at least three real values before it is compared, so a
    row that is mostly "not reported" cannot match another by being empty.
    """
    fields = ("arm1_age", "arm2_age", "arm1_bmi", "arm2_bmi",
              "arm1_female", "arm2_female", "asa_status")
    nr = {"", "not reported", "nr", "n/a", "none"}
    groups: dict[tuple, list[str]] = {}
    for s in studies:
        pop = s.get("population") or {}
        block = tuple(str(pop.get(f) or "").strip() for f in fields)
        if sum(1 for v in block if v.lower() not in nr) < 3:
            continue
        groups.setdefault(block, []).append(s["key"])
    return [{"studies": sorted(keys), "block": dict(zip(fields, block))}
            for block, keys in groups.items() if len(keys) > 1]


def denominator_mismatches(studies: list[dict]) -> list[dict]:
    """
    Every record whose reported female count is out of N people, where N is not
    that arm's analysed denominator.

    This is the rule that catches an inverted attribution WITHOUT reading a PDF:
    the Yeh pair shows up here because each row's female fraction is consistent
    with the other row's arm size. It is a screen, not a verdict -- a trial that
    reported sex over its RANDOMISED set lands here legitimately, and so does one
    whose analysed denominator was later corrected while the baseline row was not.
    Each hit is emitted with both numbers and no judgement attached.
    """
    out = []
    for s in studies:
        pop = s.get("population") or {}
        for arm in (1, 2):
            raw = pop.get(f"arm{arm}_female")
            n = pop.get(f"arm{arm}_n")
            if not isinstance(raw, str) or not isinstance(n, int):
                continue
            m = re.match(r"\s*(\d+)\s*/\s*(\d+)", raw)
            if not m or int(m.group(2)) == n:
                continue
            rand = pop.get(f"randomized_arm{arm}_n")
            explained = EXPLAINED_DENOMINATORS.get((s["key"], f"arm{arm}"))
            out.append({
                "study": s["key"],
                "arm": f"arm{arm}",
                "explained_by": explained,
                "explained_detail": EXPLAINED_DETAIL.get(s["key"]) if explained else None,
                "arm_name": pop.get(f"arm{arm}_name"),
                "female": raw,
                "female_denominator": int(m.group(2)),
                "analysed_n": n,
                "randomised_n": rand,
                "explained_by_randomised": rand == int(m.group(2)),
            })
    return out


def _proc_words(ch: dict, s: dict) -> frozenset:
    """Content words of a trial's surgical population, for comparing two reports."""
    text = (ch.get("surgery_procedure") or s.get("surgery_procedure") or "").lower()
    if not text or "elective surgical procedure under general" in text:
        return frozenset()
    text = text.replace("-", " ")
    stop = {"patients", "patient", "undergoing", "surgery", "for", "the", "of", "and", "or",
            "with", "without", "elective", "a", "an", "to"}
    return frozenset(w for w in re.findall(r"[a-z]+", text) if w not in stop) or frozenset()


def _journal(s: dict) -> str:
    m = re.search(r"\*([^*]+)\*", s.get("citation", ""))
    return m.group(1).strip().lower() if m else ""


def main(check_only: bool) -> int:
    payload = build()
    text = ("// Generated by scripts/build_cohort_overlap_scan.py; do not edit.\n"
            "// Report-to-study reconciliation, the duplicate-cohort scan behind it, and the\n"
            "// arm-level denominators that disagree with their own source publication.\n"
            "window.COHORT_OVERLAP = "
            + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n")
    if check_only:
        if not OUT_JS.exists() or OUT_JS.read_text(encoding="utf-8") != text:
            print("OUT OF DATE: dashboard/cohort_overlap.js differs from the scan", file=sys.stderr)
            return 1
        print("cohort_overlap.js is current")
        return 0
    OUT_JS.write_text(text, encoding="utf-8")
    flagged = [c for c in payload["candidates"] if c["status"] == "flagged_for_review"]
    adjudicated = [c for c in payload["candidates"] if c["status"] == "adjudicated_separate"]
    print(f"{payload['reports']} reports -> {payload['studies']} studies "
          f"({len(payload['declared_links'])} declared link(s), "
          f"{len(adjudicated)} adjudicated separate, "
          f"{len(flagged)} candidate(s) still flagged for review)")
    for c in adjudicated:
        print(f"  RESOLVED {' / '.join(c['studies'])}: separate cohorts "
              f"({c['adjudication']['date']})")
    for c in flagged:
        print(f"  FLAG {' / '.join(c['studies'])}: shared {', '.join(c['shared'])}")
    for d in payload["locked_sheet_disagreements"]:
        note = (f"exchanged with {', '.join(d['exchanged_with'])}" if d["exchanged_with"]
                else "figures differ")
        print(f"  LOCK {d['study']}: Study_Master cites {d['unaccounted']}, which AF_LOCK "
              f"does not have among {d['af_lock_arm_sizes']} ({note})")
    for s in payload["baseline_corrections"]:
        tag = "CORRECTED" if s.get("status") == "corrected" else s.get("kind", "?").upper()
        print(f"  {tag} {s['study']}: {s['summary']} "
              f"({len(s['fields'])} field(s), source-verified)")
    for d in payload["duplicate_baseline_blocks"]:
        print(f"  DUPLICATE BASELINE {' == '.join(d['studies'])}")
    dm = payload["denominator_mismatches"]
    unexplained = [d for d in dm
                   if not d["explained_by_randomised"] and not d.get("explained_by")]
    settled = [d for d in dm if d.get("explained_by")]
    print(f"  {len(dm)} female-count denominator(s) differ from the arm's analysed N "
          f"({len(settled)} adjudicated, {len(unexplained)} open)")
    for d in unexplained:
        print(f"    {d['study']} {d['arm']}: {d['female']} vs analysed n={d['analysed_n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
