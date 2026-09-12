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

# CORRECTED TWICE ON 2026-09-12. The reading that stands is the third one, and it
# is the only one that explains every artefact instead of half of them.
#
# The dashboard is not the source of this defect and cannot fix it: the TWO LOCKED
# SHEETS CONTRADICT EACH OTHER about which register key names which publication,
# and dashboard/data.js faithfully mirrors both, which is why each of its two Yeh
# rows ends up crossed within itself.
#
#   Study_Master.csv          Yeh 2010 -> Covidence 828, internal ID 1879897280,
#                                        result summary "AES (n=30) 19.3 +/- 9.7 vs
#                                        Sham AES (n=30) 21.6 +/- 13.1"   = IJNS
#                             Yeh 2011 -> Covidence 823, Identitycorrection
#                                        "Yeh 2010 (ATHM) -> Yeh 2011", summary
#                                        "EG1 (n=33) 18.6 vs EG2 (n=30) 21.6" = ATHM
#
#   Outcome_Data_AF_LOCK.csv  Yeh 2010 -> Table 4, arms 33/30 and 33/31, mean 18.6,
#                                        "mg morphine; source explicitly calls PCA
#                                        epidural"                          = ATHM
#                             Yeh 2011 -> Table 3, arms 30/30, mean 19.3, control
#                                        28.0, "mg IV morphine"             = IJNS
#
# The same three numbers (19.3 +/- 9.7 vs 21.6 +/- 13.1, MD -2.30) are filed under
# Yeh 2010 in Study_Master and under Yeh 2011 in Outcome_Data_AF_LOCK. That is a
# direct, provable contradiction inside the locked master, not an inference.
#
# Study_Master carries an Identitycorrection field recording that the ATHM paper was
# renamed from "Yeh 2010 (ATHM)" to "Yeh 2011". Outcome_Data_AF_LOCK never had that
# rename applied, which is the most likely origin of the split.
#
# NOTHING IS CORRECTED HERE, and correcting dashboard/data.js would be worse than
# leaving it: aligning it with either sheet just changes which locked sheet it
# contradicts. Resolving this means re-cutting one of the two sheets, which is a
# review-team decision about the locked master.
ATTRIBUTION_CONFLICTS = [{
    "studies": ["Yeh 2010", "Yeh 2011"],
    "summary": "The two locked sheets disagree about which register key names which "
               "publication, and the dashboard mirrors both.",
    "papers": [
        {"label": "Altern Ther Health Med 2010;16(6):10-18",
         "pdf": "015_PainATHM-2.pdf",
         "pmid": "21280458",
         "authors": "Yeh, Chung, Chen K-M, Tsou M-Y, Chen H-H (five authors, includes Tsou)",
         "setting": "orthopedic departments of a 4000-bed medical center in northern Taiwan",
         "arms": "EG1 33 / EG2 30 / CG 31",
         "female": "EG1 22/33 (66.7%), EG2 21/30 (70.0%), CG 15/31 (48.4%)",
         "opioid_24h": "EG1 18.6 \u00b1 9.7 vs EG2 21.6 \u00b1 13.1 vs CG 27.2 \u00b1 12.5 mg "
                       "(Table 4; the paper calls the PCA route epidural)"},
        {"label": "Int J Nurs Stud 2011;48(6):703-709",
         "pdf": "covidence_828_full_article.pdf",
         "pmid": "21084087",
         "doi": "10.1016/j.ijnurstu.2010.10.009",
         "authors": "Yeh, Chung, Chen K-M, Chen H-H (four authors, no Tsou)",
         "setting": "3000-bed medical center in northern Taiwan",
         "arms": "AES 30 / Sham 30 / Control 30",
         "female": "AES 20/30 (66.7%), Sham 21/30 (70.0%), Control 15/30 (50.0%)",
         "opioid_24h": "AES 19.3 \u00b1 9.7 vs sham 21.6 \u00b1 13.1 vs control 28.0 \u00b1 12.1 "
                       "mg IV (Table 3)"},
    ],
    "evidence": [
        "Study_Master.csv files the Int J Nurs Stud trial under key Yeh 2010: Covidence "
        "study key 828, internal ID 1879897280, and a result summary of \u201cAES (n=30) "
        "19.3 \u00b1 9.7 mg vs Sham AES (n=30) 21.6 \u00b1 13.1 mg (P = 0.443) [MD -2.30]\u201d.",
        "Outcome_Data_AF_LOCK.csv files those same three numbers under key Yeh 2011 \u2014 "
        "arms 30/30, mean 19.3, sham 21.6, derived MD -2.30, Table 3, mg IV morphine \u2014 "
        "and files the Altern Ther Health Med figures (33/30 and 33/31, mean 18.6, Table 4, "
        "\u201cmg morphine; source explicitly calls PCA epidural\u201d) under Yeh 2010.",
        "So one locked sheet says Yeh 2010 is the Int J Nurs Stud paper and the other says "
        "it is the Altern Ther Health Med paper. Both cannot be right, and this is visible "
        "from the two sheets alone without opening either PDF.",
        "Study_Master's Yeh 2011 row carries an Identitycorrection field reading "
        "\u201cYeh 2010 (ATHM) \u2192 Yeh 2011\u201d and an Antigravitystudylabel still "
        "reading \u201cYeh 2010 (ATHM)\u201d. A deliberate rename was applied to "
        "Study_Master and never applied to Outcome_Data_AF_LOCK, which is the most likely "
        "origin of the split.",
        "dashboard/data.js mirrors both sheets faithfully, which is exactly why each of its "
        "rows is crossed: the citation, DOI and PMID follow Study_Master, while the arm "
        "denominators follow Outcome_Data_AF_LOCK. Its baseline sex counts follow the "
        "citation \u2014 Yeh 2010 holds 20/30 (the Int J Nurs Stud figure) and Yeh 2011 "
        "holds 22/33 (the Altern Ther Health Med figure) \u2014 so within each row the sex "
        "denominator and the arm denominator name different papers.",
        "A sweep of Study_Master's result summaries against Outcome_Data_AF_LOCK's analysed "
        "arms across all 63 rows that carry both finds six disagreements; the Yeh pair is "
        "the only one where the two sheets' figures are exactly exchanged between two keys. "
        "The others (Zhu 2022, Wang 2024, Lu 2021, Jin 2023) are arm-order or multi-cohort "
        "differences, listed separately below.",
    ],
    "affects": "Which publication each register row names. No pooled estimate depends on it: "
               "both Yeh records are on DUPLICATE-OVERLAP HOLD in the lock itself "
               "(AFincludestrict = 0, AFincludesensitivity = 0 on every row), so neither "
               "contributes to any synthesis, and the study count of 69 is unaffected "
               "because the pair counts once either way.",
    "not_affected": "The numbers themselves. Both publications' arm data are present and "
                    "internally coherent in the lock; what is in dispute is only which key "
                    "each set is filed under.",
    "decision_needed": "This cannot be fixed in the dashboard. Aligning dashboard/data.js "
                       "with either locked sheet would simply change which sheet it "
                       "contradicts. Resolving it means re-cutting Study_Master or "
                       "Outcome_Data_AF_LOCK so the two agree, which is a decision about the "
                       "locked master and belongs to the review team. The Identitycorrection "
                       "field suggests the intended direction was Yeh 2010 = Int J Nurs Stud "
                       "and Yeh 2011 = Altern Ther Health Med, which would mean re-cutting "
                       "Outcome_Data_AF_LOCK \u2014 but that sheet is the one the analyses "
                       "read, so it is not a change to make casually.",
    "superseded_finding": "Two earlier readings on 2026-09-12 were wrong and are recorded so "
                          "they are not mistaken for separate open issues. The first called "
                          "it a transposition of arm denominators and named the arm Ns as the "
                          "defective field. The second called it an inverted citation and "
                          "said the arm Ns were the half that traces to the lock. Neither is "
                          "right: the lock disagrees with itself, so no single field in the "
                          "dashboard can be named as the wrong one.",
}]


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
    "summary": "The two reports of this trial state different cohort sizes.",
    "detail": "Int J Nurs Stud 2011 shows 99 assessed for eligibility, 90 meeting inclusion "
              "criteria, and randomisation to 30 / 30 / 30. Altern Ther Health Med 2010 "
              "states \"Ninety-nine patients undergoing lumbar spinal surgery were randomly "
              "assigned to one of three groups\" with group sizes 33 / 30 / 31. Whether 90 or "
              "99 were randomised cannot be settled from the two papers, so neither figure is "
              "used as the trial's randomised N. Stated by paper rather than by register key, "
              "because which key names which paper is itself in question \u2014 see the "
              "attribution conflict above.",
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
    Where the two locked sheets describe the same study with different arm sizes.

    Study_Master carries a prose result summary per study; Outcome_Data_AF_LOCK
    carries the arm-level data the analyses actually read. When the "(n=NN)"
    figures in the summary match no analysed pair in AF_LOCK, the two sheets are
    describing different things under one key. That is how the Yeh identity split
    became visible without opening a PDF, and it is cheap to keep watching.

    Reported, never reconciled here: choosing which sheet is right is a decision
    about the locked master.
    """
    import csv
    sm_path, af_path = SHEETS / "Study_Master.csv", SHEETS / "Outcome_Data_AF_LOCK.csv"
    if not sm_path.exists() or not af_path.exists():
        return []
    analysed: dict[str, set] = {}
    for r in csv.DictReader(af_path.open(encoding="utf-8-sig")):
        try:
            analysed.setdefault(r["Canonicalstudy"], set()).add(
                (int(float(r["Analyzednintervention"])), int(float(r["Analyzedncomparator"]))))
        except (ValueError, TypeError, KeyError):
            pass

    out = []
    summaries = {}
    for r in csv.DictReader(sm_path.open(encoding="utf-8-sig")):
        key = r.get("Canonicalstudy") or ""
        ns = [int(x) for x in re.findall(r"\(n\s*=\s*(\d+)\)", r.get("Candidatesourceresultsummary") or "")][:2]
        if len(ns) == 2:
            summaries[key] = tuple(ns)
    for key, pair in summaries.items():
        if key not in analysed or pair in analysed[key]:
            continue
        # Exchanged with another key, or merely different? The first is an identity
        # split; the second is usually arm order or a multi-cohort aggregation.
        swapped_with = [k for k, p in summaries.items()
                        if k != key and pair in analysed.get(k, set())
                        and summaries.get(k) in analysed.get(key, set())]
        out.append({
            "study": key,
            "study_master_summary_arms": list(pair),
            "af_lock_analysed_arms": sorted(list(x) for x in analysed[key]),
            "exchanged_with": swapped_with,
            "kind": "identity_split" if swapped_with else "arm_figures_differ",
        })
    return sorted(out, key=lambda d: (d["kind"] != "identity_split", d["study"]))


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
            out.append({
                "study": s["key"],
                "arm": f"arm{arm}",
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
        print(f"  LOCK {d['study']}: Study_Master says {d['study_master_summary_arms']}, "
              f"AF_LOCK says {d['af_lock_analysed_arms']} ({note})")
    dm = payload["denominator_mismatches"]
    unexplained = [d for d in dm if not d["explained_by_randomised"]]
    print(f"  {len(dm)} female-count denominator(s) differ from the arm's analysed N "
          f"({len(unexplained)} not explained by a randomised denominator)")
    for d in unexplained:
        print(f"    {d['study']} {d['arm']}: {d['female']} vs analysed n={d['analysed_n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
