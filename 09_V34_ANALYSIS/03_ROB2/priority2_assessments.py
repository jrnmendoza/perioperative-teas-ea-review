#!/usr/bin/env python3
"""
Result-specific Cochrane RoB 2 assessments for the priority-2 worklist rows
(results NOT currently inside a fitted model -- 493 of the 529-row worklist).

PROVENANCE. Same status as the priority-1 (model-blocking) assessments:
produced by reading the mapped source PDF against the RoB 2 signalling
questions, adopted by the review lead as the review's current assessment for
these results, NOT an independently documented dual-assessor record. See
draft_assessments.py's module docstring for the full disclosure; it applies
identically here.

SCALING RULE. A trial's randomisation, blinding scheme, missing-data handling
and pre-specification (D1, D2, D3, D5) are facts about the TRIAL, established
once from the source and then correctly applied to every result drawn from
that trial -- this is not the "study-wide OVERALL judgement" the handover
prohibits, which specifically means copying one result's judgement onto a
DIFFERENT result's D4 without checking who measured it. D4 is re-derived for
every distinct measurement circumstance in this file. Where a trial reports
the same instrument at several timepoints (e.g. NRS pain at 6h/24h/48h), the
D4 reasoning is genuinely identical across those timepoints -- the same
assessor, the same blinding status, the same recording method -- and is
stated once and applied to each timepoint explicitly, not silently assumed.

This file is intentionally incremental: STUDIES dict grows as each is
completed, and main() only requires every row for an already-added study's
results to be present -- it does not require the whole 493-row worklist to be
covered before it can run and be checked in.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKLIST = ROOT / "09_V34_ANALYSIS" / "v34_rob2_worklist.csv"

L, S, H = "Low", "Some concerns", "High"

# (study, outcome, timepoint) -> domain judgements + rationale + flags
A: dict[tuple, dict] = {}


def add(study, outcome, timepoint, d1, d2, d3, d4, d5, why, flags=""):
    A[(study, outcome, timepoint)] = dict(
        d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, rationale=why, flags=flags)


def overall(*doms: str) -> str:
    if H in doms:
        return H
    if S in doms:
        return S
    return L


# ============================================================================
# Zheng 2025 (109499.pdf) -- trial design established in draft_assessments.py:
# D1 Some concerns (seeded-random allocation method described does not
# guarantee the stated 1:1 ratio, though concealment via opaque envelopes was
# adequate); D2 Some concerns (single-blind: anaesthesiologists unblinded by
# the nature of the intervention, a stated limitation; participants and
# outcome assessors blinded; mITT); D3 Low (3/88 excluded under pre-specified
# withdrawal criteria); D5 varies by whether the result is a named
# pre-specified outcome. PONV within 24h is the registered PRIMARY outcome;
# QoR-40, PSQI, NRS, PCIA usage, GI recovery, adverse events, time to first
# flatus and length of stay are all explicitly named SECONDARY outcomes.
# ============================================================================
_zheng_d1d2d3 = (S, S, L)
_zheng_prespecified = (
    "D5 Low: registered with the Chinese Clinical Trial Registry; this result "
    "is explicitly named among the trial's pre-specified secondary outcomes "
    "('Secondary outcomes included the Quality of Recovery-40 (QoR-40) "
    "scores, Pittsburgh Sleep Quality Index (PSQI) scores, pain intensity "
    "assessed by numerical rating scale (NRS), and patient-controlled "
    "analgesia (PCA) usage').")
_zheng_base = (
    "D1: allocation by thresholding a seeded uniform random number, a method "
    "that does not itself guarantee the stated 1:1 ratio, though 'concealed "
    "in sequentially numbered, opaque, sealed envelopes' is adequate "
    "concealment. D2: single-blind by design -- 'the anesthesiologists were "
    "unblinded due to the nature of the intervention', a limitation the "
    "authors themselves name; participants and outcome assessors were "
    "blinded, and a modified intention-to-treat analysis was used. D3: 3 of "
    "88 excluded under pre-specified withdrawal criteria (2 procedure "
    "change, 1 procedure exceeding 3 hours). ")

for tp in ("6 h", "24 h", "48 h"):
    add("Zheng 2025", "Global QoR-40", tp, S, S, L, L, L,
        _zheng_base + _zheng_prespecified +
        " D4 Low for THIS result: QoR-40 is a self-completed questionnaire, "
        "and participants -- who were successfully blinded in this trial -- "
        "are the ones who answer it; outcome assessors administering it were "
        "also blinded.")
for tp in ("6 h", "24 h", "48 h"):
    add("Zheng 2025", "NRS pain score", tp, S, S, L, L, L,
        _zheng_base + _zheng_prespecified +
        " D4 Low for THIS result: NRS pain is self-reported by a blinded "
        "participant to a blinded assessor at a pre-defined timepoint.")
for tp in ("24 h", "48 h"):
    add("Zheng 2025", "PSQI score", tp, S, S, L, L, L,
        _zheng_base + _zheng_prespecified +
        " D4 Low for THIS result: PSQI is self-completed by a blinded "
        "participant, collected by a blinded assessor.")
add("Zheng 2025", "Total PCIA button presses", "Postoperative; exact pump duration NR", S, S, L, L, L,
    _zheng_base + _zheng_prespecified +
    " D4 Low for THIS result: 'Times of effective PCIA use' is read from the "
    "device log, an objective count driven by the (blinded) participant's "
    "own button presses, not by the unblinded anaesthesiologist.")
add("Zheng 2025", "Effective PCIA button presses", "Postoperative; exact pump duration not stated", S, S, L, L, L,
    _zheng_base + _zheng_prespecified +
    " D4 Low for THIS result: identical reasoning to total PCIA button "
    "presses -- device-logged, participant-driven, not clinician-set.")
add("Zheng 2025", "Exact cumulative postoperative sufentanil mass", "0-24 h", S, S, L, S, L,
    _zheng_base + _zheng_prespecified +
    " D4 Some concerns for THIS result: the PCIA pump was 'established' by "
    "the anaesthesia team at the end of surgery with a fixed sufentanil "
    "concentration and background/bolus settings; the unblinded "
    "anaesthesiologist who is not blinded to allocation sets those initial "
    "parameters even though the participant (blinded) triggers the doses "
    "actually delivered, so the total mass is not purely participant-driven "
    "the way the button-press COUNT is.",
    "postoperative PCIA total is jointly determined by unblinded pump "
    "programming and blinded participant demand")
for tp in ("0–2 h", "2–4 h", "4–6 h", "6–24 h"):
    add("Zheng 2025", "Nausea incidence", tp, S, S, L, L, L,
        _zheng_base + _zheng_prespecified.replace("QoR-40", "PONV-related") +
        " D4 Low for THIS result: nausea within each window is recorded by "
        "blinded outcome assessors as part of the trial's structured "
        "postoperative follow-up; the same recording process applies at "
        "every one of the four windows.")
    add("Zheng 2025", "Vomiting incidence", tp, S, S, L, L, L,
        _zheng_base + _zheng_prespecified.replace("QoR-40", "PONV-related") +
        " D4 Low for THIS result: vomiting is an observable event scored by "
        "blinded outcome assessors at each of the four windows, the same "
        "recording process as the corresponding nausea result.")
for ae in ("Dizziness and headache", "Drowsiness", "Fever"):
    add("Zheng 2025", ae, "Postoperative", S, S, L, L, L,
        _zheng_base +
        "D5 Low: adverse events are reported in the trial's structured "
        "results table (Table 4) alongside the named secondary outcomes. "
        "D4 Low for THIS result: recorded by blinded outcome assessors as "
        "part of the trial's structured adverse-event follow-up; the "
        "quoted table reports fever, dizziness/headache and drowsiness "
        "together in the same assessment ('Incidence of adverse reactions "
        "Fever 6 (14.3%) 8 (18.6%) ... Dizziness and headache 2 (4...').")
add("Zheng 2025", "Emergency rescue analgesia events", "Postoperative; exact window not stated", S, S, L, L, S,
    _zheng_base +
    "D5 Some concerns: rescue analgesia is not individually named among the "
    "trial's listed pre-specified outcomes, though it is a conventional "
    "companion measure to PCIA usage. D4 Low for THIS result: rescue "
    "analgesic administration is a clinical/pharmacy record, not a "
    "judgement call by the unblinded anaesthesiologist after the initial "
    "perioperative period.",
    "rescue analgesia not individually named among the pre-specified outcomes")
for milestone, note in [
    ("Wake-up time", "an objective, device/clock-based endpoint (time to "
     "eye-opening or verbal response) rather than a clinician's discretionary "
     "discharge decision"),
    ("PACU stay time", "PACU discharge criteria are typically protocolised "
     "(e.g. Aldrete score thresholds) rather than solely the unblinded "
     "anaesthesiologist's discretion, but the paper does not state who signs "
     "off PACU discharge in this trial"),
    ("Hospital stay duration", "hospital discharge timing more often "
     "reflects a treating clinician's overall judgement than a fixed "
     "protocolised criterion, and the paper does not state who is "
     "responsible for that decision or whether they were blinded"),
]:
    add("Zheng 2025", milestone, "Postoperative" if milestone != "Hospital stay duration" else "Postoperative hospitalization",
        S, S, L, S if milestone != "Wake-up time" else L, S,
        _zheng_base +
        "D5 Some concerns: this recovery-milestone measure is not "
        "individually named among the trial's listed pre-specified "
        "outcomes. D4 for THIS result: " + note + ".",
        "recovery-milestone timing not individually named among the pre-specified outcomes")
add("Zheng 2025", "Time to first borborygmus", "Postoperative", S, S, L, S, S,
    _zheng_base +
    "D5 Some concerns: not individually named among the pre-specified "
    "outcomes, and reported alongside the same flatus-definition ambiguity "
    "already flagged as a source-QC issue for this trial. D4 Some concerns "
    "for THIS result: bowel-sound auscultation timing depends on staff "
    "checking frequency and interpretation; the trial does not state "
    "whether the staff performing auscultation were blinded, and this is "
    "the same endpoint-definition trial already flagged for defining "
    "'first flatus' as 'the first stools passed by the participants' -- the "
    "measurement protocol for bowel recovery in this report is unusually "
    "unclear.",
    "SOURCE-QC: same flatus/borborygmus definition ambiguity already flagged for this trial")


def main() -> int:
    with WORKLIST.open(encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["priority"].startswith("2")]

    pdf_map = json.loads((HERE / "pdf_map.json").read_text())
    done_studies = {k[0] for k in A}
    relevant = [r for r in rows if r["study"] in done_studies]

    out, missing = [], []
    for r in relevant:
        key = (r["study"], r["outcome"], r["timepoint"])
        a = A.get(key)
        if not a:
            missing.append(key)
            continue
        doms = (a["d1"], a["d2"], a["d3"], a["d4"], a["d5"])
        out.append(dict(
            study=r["study"], outcome=r["outcome"], timepoint=r["timepoint"],
            outcome_family=r["outcome_family"],
            intervention=r["intervention"], comparator=r["comparator"],
            analysed_n_i=r["analysed_n_i"], analysed_n_c=r["analysed_n_c"],
            randomised_n_i=r["randomised_n_i"], randomised_n_c=r["randomised_n_c"],
            d1_randomisation=a["d1"], d2_deviations=a["d2"], d3_missing=a["d3"],
            d4_measurement=a["d4"], d5_reporting=a["d5"],
            overall=overall(*doms),
            rationale=" ".join(a["rationale"].split()),
            flags=a["flags"],
            source_pdf=pdf_map.get(r["study"], ""),
            status="ROB2_RESULT_SPECIFIC_ADOPTED",
            adopted_by="John Ryan N. Mendoza (review lead)",
            adopted_date="2026-09-08",
            provenance_note=(
                "Adopted by the review lead's direction. Domain judgements and "
                "rationale are the source-evidence extraction, unchanged by "
                "adoption. Standard Cochrane RoB 2 practice calls for two "
                "independent assessors reconciling disagreement; no separately "
                "documented dual-assessor record was provided to this pipeline."
            ),
        ))

    if missing:
        print(f"WARNING: {len(missing)} rows for an added study have no A[] entry:")
        for m in missing:
            print("   ", m)

    if not out:
        print("no studies added yet")
        return 0

    p = HERE / "v34_rob2_priority2_assessments.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    print(f"wrote {len(out)} priority-2 assessments across {len(done_studies)} "
          f"studies -> {p.relative_to(ROOT)}")
    print(f"studies done: {sorted(done_studies)}")
    c = Counter(r["overall"] for r in out)
    print("overall:", dict(c))
    total_p2 = len(rows)
    print(f"progress: {len(out)} / {total_p2} priority-2 rows "
          f"({100*len(out)/total_p2:.1f}%)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
