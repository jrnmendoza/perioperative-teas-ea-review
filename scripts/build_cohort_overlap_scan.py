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

# Reports whose arm denominators disagree with the publication they were read
# from. Each entry carries the source file and the verbatim line, so the
# disagreement can be checked without reopening the PDF. Nothing is corrected
# here: the register is the locked master and these fields feed no analysis.
ARM_N_CONFLICTS = {
    "Yeh 2010": {
        "field": "population.arm1_n",
        "register": 33,
        "source_says": 30,
        "source": "TEAS EA Verification/astra_audit/source_text/covidence_828_full_article.txt",
        "quote": "n = 30 in each group; F-test for numerical data or chi-square test for "
                 "categorical data.",
        "note": "Register key Yeh 2010 is the Int J Nurs Stud 2011 report "
                "(covidence_828_full_article.pdf), whose flow diagram randomises 30 / 30 / 30 "
                "and whose baseline table footnote states n = 30 in each group. The register's "
                "arm1_n of 33 is the EG1 denominator of the companion Altern Ther Health Med "
                "report, not this one.",
    },
    "Yeh 2011": {
        "field": "population.arm1_n",
        "register": 30,
        "source_says": 33,
        "source": "TEAS EA Verification/astra_audit/source_text/015_PainATHM-2.txt",
        "quote": "Variables EGl(n=33) EG2(n=30) CG(n=31)",
        "note": "Register key Yeh 2011 is the Altern Ther Health Med 2010 report "
                "(015_PainATHM-2.pdf), whose Table 2 gives EG1 n = 33. The register's arm1_n "
                "of 30 is the companion Int J Nurs Stud figure. The same row's female count "
                "(22/33) and ages do come from this paper, so the two reports' arm "
                "denominators appear to have been transposed during extraction.",
    },
}

# The two papers also disagree with each other about the size of the cohort they
# describe. That is recorded as a property of the linked pair, not of either report.
COHORT_SIZE_DISAGREEMENTS = [{
    "studies": ["Yeh 2010", "Yeh 2011"],
    "summary": "The two reports of this trial state different cohort sizes.",
    "detail": "Int J Nurs Stud 2011 (key Yeh 2010) shows 99 assessed for eligibility, 90 "
              "meeting inclusion criteria, and randomisation to 30 / 30 / 30. Altern Ther "
              "Health Med 2010 (key Yeh 2011) states \"Ninety-nine patients undergoing lumbar "
              "spinal surgery were randomly assigned to one of three groups\" with group sizes "
              "33 / 30 / 31. Whether 90 or 99 were randomised cannot be settled from the two "
              "papers, so neither figure is used as the trial's randomised N.",
    "affects": "Descriptive participant totals only. Neither report contributes arm-level "
               "data to any synthesis, so no effect estimate depends on this.",
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
            candidates.append({
                "studies": sorted(pair),
                "status": "confirmed" if pair in declared_pairs else "flagged_for_review",
                "shared": shared,
                "analysed_n": {a["key"]: a["population"]["total_n"],
                               b["key"]: b["population"]["total_n"]},
                "arm_n": {a["key"]: [a["population"]["arm1_n"], a["population"]["arm2_n"]],
                          b["key"]: [b["population"]["arm1_n"], b["population"]["arm2_n"]]},
                "shared_arm_n": shared_arm_n,
                "citations": {a["key"]: a["citation"], b["key"]: b["citation"]},
                "procedure": pa.get("surgery_procedure") or a.get("surgery_procedure"),
            })

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
        "candidates": sorted(candidates, key=lambda c: (c["status"] != "flagged_for_review",
                                                        c["studies"])),
        "arm_n_conflicts": ARM_N_CONFLICTS,
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
    print(f"{payload['reports']} reports -> {payload['studies']} studies "
          f"({len(payload['declared_links'])} declared link(s), "
          f"{len(flagged)} candidate(s) flagged for review)")
    for c in flagged:
        print(f"  FLAG {' / '.join(c['studies'])}: shared {', '.join(c['shared'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
