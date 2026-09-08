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


# ============================================================================
# Yang 2020 (covidence_464_verified.pdf) -- trial design established in
# draft_assessments.py: D1 Low ('Group allocation was concealed using a
# sealed envelope containing the allocation sequence generated by SPSS');
# D2 Some concerns (open-label -- 'Participants and the acupuncture provider
# were not blind to the groups because of the specificity of EA treatment',
# but 'The assessors, anesthetists, and statisticians were unaware of
# study-group assignments throughout the entire trial'); D3 Low (2 of 59
# lost, documented reasons). This is explicitly a FEASIBILITY study with no
# formal sample-size calculation.
# ============================================================================
_yang20_base = (
    "D1: 'Group allocation was concealed using a sealed envelope containing "
    "the allocation sequence generated by SPSS in a 1:1 ratio'. D2 Some "
    "concerns: open-label -- 'Participants and the acupuncture provider were "
    "not blind to the groups because of the specificity of EA treatment' -- "
    "but 'The assessors, anesthetists, and statisticians were unaware of "
    "study-group assignments throughout the entire trial', and 'An "
    "independent observer assessed PONV and pain intensity at 24, 48, and "
    "72 hours after surgery'. D3: 2 of 59 randomised lost (1 excluded for "
    "absence of PVB, 1 withdrew before surgery), with documented reasons. ")
_yang20_prespecified_secondary = (
    "D5 Low: registered ChiCTR1800014461; this result is explicitly named "
    "among the stated secondary outcomes ('Secondary outcomes included "
    "postoperative nausea and vomiting (PONV), pain intensity, and duration "
    "of hospital stay' / 'Secondary outcomes included PONV, pain scores, "
    "time to out-of-bed activity and length of hospital stay'), though this "
    "is explicitly a feasibility study with no formal sample-size "
    "calculation for these secondary comparisons.")

add("Yang 2020", "Abdominal distension incidence", "Postoperative; assessment window not separately stated",
    L, S, L, S, L,
    _yang20_base +
    "D5 Low: abdominal distension (AD) incidence and degree is named among "
    "the trial's stated PRIMARY outcomes. D4 Some concerns for THIS result: "
    "the report does not state whether AD is scored by an independent "
    "observer from an objective sign (e.g. girth) or from the patient's own "
    "report of bloating/discomfort; given participants were not blinded and "
    "the ambiguity is unresolved, this is treated cautiously as susceptible "
    "to participant awareness of allocation.",
    "unclear whether AD is assessor-observed or patient-reported")
for grade in range(5):
    add("Yang 2020", f"Abdominal distension severity grade {grade}",
        "Postoperative; assessment window not separately stated", L, S, L, S, L,
        _yang20_base +
        "D5 Low: AD severity grading is part of the same named primary "
        "outcome as AD incidence. D4 Some concerns for THIS result: "
        "identical reasoning to AD incidence -- the severity grade for this "
        "same instrument carries the same unresolved ambiguity about "
        "whether it is assessor-observed or patient-reported.",
        "unclear whether AD severity is assessor-observed or patient-reported")
for tp in ("0–24 h after surgery", "24–48 h after surgery", "48–72 h after surgery"):
    add("Yang 2020", "Dynamic pain VAS", tp, L, S, L, S, L,
        _yang20_prespecified_secondary.replace("PONV", "pain") + " " + _yang20_base +
        "D4 Some concerns for THIS result: VAS pain is the participant's own "
        "subjective rating; although an independent, blinded observer "
        "elicits and records it, the unblinded participant's own awareness "
        "of allocation can still influence the rating they give.")
    add("Yang 2020", "Static pain VAS", tp, L, S, L, S, L,
        _yang20_prespecified_secondary.replace("PONV", "pain") + " " + _yang20_base +
        "D4 Some concerns for THIS result: identical reasoning to dynamic "
        "pain VAS at the same timepoint -- a participant self-rating, not "
        "protected from the participant's own unblinding by the observer's "
        "blinding.")
    add("Yang 2020", "Nausea incidence", tp, L, S, L, S, L,
        _yang20_prespecified_secondary + " " + _yang20_base +
        "D4 Some concerns for THIS result: nausea is an internal sensation "
        "only the participant can report; the 4-point PONV scale is "
        "completed via the participant's own account even though the "
        "observer recording it is blinded.")
    add("Yang 2020", "Nausea severity score", tp, L, S, L, S, L,
        _yang20_prespecified_secondary + " " + _yang20_base +
        "D4 Some concerns for THIS result: identical reasoning to nausea "
        "incidence at the same timepoint -- the severity grade for the same "
        "subjective sensation.")
    add("Yang 2020", "Vomiting incidence", tp, L, S, L, L, L,
        _yang20_prespecified_secondary + " " + _yang20_base +
        "D4 Low for THIS result: unlike nausea, vomiting is an objectively "
        "observable event -- the independent, blinded observer can score "
        "whether it occurred without depending on the unblinded "
        "participant's own account of an internal sensation.")
    add("Yang 2020", "Vomiting severity score", tp, L, S, L, L, L,
        _yang20_prespecified_secondary + " " + _yang20_base +
        "D4 Low for THIS result: vomiting severity in this scale reflects "
        "the number/frequency of observed vomiting episodes, an objective "
        "count rather than a self-reported sensation, recorded by the "
        "blinded independent observer.")
add("Yang 2020", "Hospital stay", "Postoperative hospitalization", L, S, L, S, L,
    _yang20_prespecified_secondary + " " + _yang20_base +
    "D4 Some concerns for THIS result: the report does not state who makes "
    "the discharge decision or whether that person was blinded; hospital "
    "discharge timing more often reflects a treating clinician's overall "
    "judgement than a fixed, purely objective criterion.",
    "unclear who decides hospital discharge or whether they were blinded")
add("Yang 2020", "Time to out-of-bed activity", "Postoperative", L, S, L, S, L,
    _yang20_prespecified_secondary + " " + _yang20_base +
    "D4 Some concerns for THIS result: getting out of bed depends in part "
    "on the unblinded participant's own motivation and willingness, not "
    "purely on objective physiological readiness observed by staff.")
add("Yang 2020", "Participants given rescue medication", "Postoperative; exact window not stated",
    L, S, L, S, S,
    _yang20_base +
    "D5 Some concerns: rescue medication is not itself individually named "
    "among the stated secondary outcomes, though the trigger for giving it "
    "('If the Visual Analogue Scale (VAS) exceeded 3/10, an additional "
    "intramuscular injection of bucinnazine 100 mg was administered as a "
    "rescue medication') is protocol-defined. D4 Some concerns for THIS "
    "result: because rescue medication is triggered by the participant's "
    "own VAS report, whether it was given at all inherits the same "
    "participant-unblinding risk as the VAS score driving it.",
    "rescue medication not individually named among the pre-specified outcomes")


# ============================================================================
# Pan 2023 (getfile.php-4.pdf) -- trial design established in
# draft_assessments.py: D1 Some concerns ('Patients were assigned ... using "
# random number tables', no concealment mechanism described); D2 Some
# concerns (described as 'double-blind' but no sham device is described, so
# participant blinding is not established; 'a PACU nurse, who was unaware of
# the group of each patient, assisted patients to evaluate their pain level'
# is the only confirmed blinded assessor); D3 Low (105 randomised, 105
# analysed; 15 documented pre-randomisation exclusions occurred before
# randomisation).
# ============================================================================
_pan23_base = (
    "D1 Some concerns: 'Patients were assigned to TEAS group (Group T) and "
    "control group (Group C) using random number tables', with no "
    "allocation-concealment mechanism described. D2 Some concerns: described "
    "as a 'double-blind randomized control-group clinical trial', but the "
    "report does not describe a sham device, so successful participant "
    "blinding is not established; the only confirmed blinded assessor "
    "statement in this report is specific to pain scoring ('a PACU nurse, "
    "who was unaware of the group of each patient, assisted patients to "
    "evaluate their pain level'). D3 Low: 105 randomised, 105 analysed. ")
_pan23_not_prespecified = (
    "D5 Some concerns: this result is not individually named among the "
    "trial's formally listed secondary outcome measures ('the general "
    "patient condition, dosage of remifentanil, propofol, any vasoactive "
    "drugs ... incidence of pain caused by propofol injection ... and the "
    "incidence of cough induced by sufentanil'); it is reported in the "
    "paper's results tables but was not one of the outcomes named in the "
    "Methods.")
_pan23_qor40_subscale = (
    "D5 Low: this is one of the five QoR-40 subscales, the trial's stated "
    "primary outcome instrument.")

for sub in ("Emotional state", "Physical comfort", "Physical independence",
           "Psychological support", "Pain subscale"):
    add("Pan 2023", sub, "24 h after operation", S, S, L, S, L,
        _pan23_base + _pan23_qor40_subscale +
        " D4 Some concerns for THIS result: like the QoR-40 total score, "
        "this subscale is completed by the participant, whose blinding was "
        "not established.")
for tp in ("1 h after operation", "24 h after operation"):
    add("Pan 2023", "NRS in the mobile state", tp, S, S, L, S, S,
        _pan23_base + _pan23_not_prespecified +
        " D4 Some concerns for THIS result: NRS is the participant's own "
        "pain rating; a blinded PACU nurse elicits it, but the unblinded "
        "participant's own awareness of allocation can still influence the "
        "rating given.")
add("Pan 2023", "PACU highest NRS score", "PACU", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: identical reasoning to NRS in the "
    "mobile state -- a participant self-rating, elicited by a blinded nurse "
    "but not protected from the participant's own unblinding.")
add("Pan 2023", "Resting pain", "Postoperative", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: another participant-reported pain "
    "measure with the same unresolved participant-blinding limitation.")
add("Pan 2023", "Nausea incidence", "Within 24 h after operation", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: nausea is an internal sensation "
    "only the participant can report, and no blinded-assessor statement "
    "specific to nausea/vomiting recording is given (unlike the explicit "
    "statement for pain scoring).")
for tp in ("1 h after operation", "Within 24 h after operation"):
    add("Pan 2023", "Vomiting incidence", tp, S, S, L, L, S,
        _pan23_base + _pan23_not_prespecified +
        " D4 Low for THIS result: unlike nausea, vomiting is an objectively "
        "observable event that does not depend on the unblinded "
        "participant's own account of an internal sensation.")
add("Pan 2023", "Participants using analgesic drugs", "Within 24 h after operation", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: analgesic administration in this "
    "trial is triggered by the participant's own pain report, so whether it "
    "was given inherits the same participant-unblinding risk as the pain "
    "score driving it.")
add("Pan 2023", "Participants using antiemetic drugs", "Within 24 h after operation", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: antiemetic administration is "
    "similarly triggered by the participant's own report of nausea, "
    "inheriting the same limitation.")
add("Pan 2023", "Utilization of remedial drugs in PACU", "PACU", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: PACU remedial drug use follows the "
    "same participant-report-triggered pattern as postoperative analgesic "
    "and antiemetic use.")
for milestone in ("PACU Aldrete score", "PACU retention time", "Time of conscious",
                  "Time of extubation", "Time of respiratory recovery"):
    add("Pan 2023", milestone, "PACU" if "PACU" in milestone else "PACU/recovery", S, S, L, S, S,
        _pan23_base + _pan23_not_prespecified +
        " D4 Some concerns for THIS result: this is an anaesthesia-recovery "
        "milestone typically judged by the treating anaesthetic team; the "
        "report does not state whether that team was blinded when making "
        "this assessment.",
        "assessor blinding not confirmed for this specific recovery milestone")
for gi in ("First postoperative implantation activity time", "First postoperative water intake time",
          "First solid food tolerance time", "Removing the catheter time"):
    add("Pan 2023", gi, "Postoperative", S, S, L, S, S,
        _pan23_base + _pan23_not_prespecified +
        " D4 Some concerns for THIS result: this recovery milestone depends "
        "in part on the unblinded participant's own report of readiness "
        "(e.g. tolerating food or water) or on a clinician's discretionary "
        "timing (catheter removal), and the report does not confirm blinded "
        "assessment for it.",
        "recovery-milestone timing not confirmed as blinded-assessor-determined")
add("Pan 2023", "Postoperative hospitalization time", "Postoperative hospitalization", S, S, L, S, S,
    _pan23_base + _pan23_not_prespecified +
    " D4 Some concerns for THIS result: hospital discharge timing more "
    "often reflects a treating clinician's overall judgement than a fixed, "
    "purely objective criterion, and the report does not state who decided "
    "or whether they were blinded.",
    "unclear who decides hospital discharge or whether they were blinded")


# ============================================================================
# Song 2020 (getfile.php-6.pdf) -- trial design established in
# draft_assessments.py: D1 Low (computer-generated sequence, sequentially
# numbered opaque envelopes); D2 Low (unusually strong active-sham blind --
# 'the low-frequency stimuli were set to the same frequency (2/10 HZ),
# resulting in the patients believing that they were undergoing real TEAS
# therapy'; patients, anaesthesiologists, surgeons and data collectors all
# blinded; ITT); D3 Low (all 85 randomised included in the ITT analysis).
# ============================================================================
_song20_base = (
    "D1 Low: 'divided to the TEAS group or control group randomly in a 1:1 "
    "ratio using a computer-generated randomization number sequence'; 'Seal "
    "the group assignments in sequentially numbered opaque envelopes'. "
    "D2 Low: an unusually strong active-sham blind -- 'the low-frequency "
    "stimuli were set to the same frequency (2/10 HZ), resulting in the "
    "patients believing that they were undergoing real TEAS therapy' -- and "
    "'Patients, attending anesthesiologists, surgeons and data collectors "
    "... were all blinded to the group assignment'; 'All analyses were "
    "based on the intention-to-treat (ITT) population'. D3 Low: all 85 "
    "randomised participants (42/43) are included in the ITT analysis. ")
_song20_primary_sleep = (
    "D5 Low: sleep quality is the trial's stated primary outcome -- "
    "'Comparison of Perioperative Sleep Quality Between the Two Groups' "
    "reports the AIS score and sleep efficiency together as the primary "
    "outcome comparison; this result is a component measure of the same "
    "polysomnographic sleep-quality assessment.")

for tp in ("First night before surgery after preoperative stimulation",
          "First postoperative night", "Third postoperative night"):
    for measure, note in [
        ("AIS score", "AIS is a self-assessment questionnaire, but "
         "participants were successfully blinded by the active-sham design, "
         "so their own awareness of allocation cannot differentially bias "
         "the rating."),
        ("REM sleep", "'The following sleep variables were evaluated by "
         "physicians in the sleep laboratory, who w[ere blinded]' -- an "
         "objective polysomnographic measure scored by blinded physicians."),
        ("Sleep efficiency", "identical reasoning to REM sleep -- an "
         "objective polysomnographic measure scored by blinded sleep-"
         "laboratory physicians, and explicitly part of the named primary "
         "outcome comparison."),
        ("Stable sleep", "identical reasoning to REM sleep -- 'stable "
         "sleep' (Stages 3-4) is scored by the same blinded sleep-"
         "laboratory physicians from the same polysomnographic record."),
        ("Unstable sleep", "identical reasoning to REM sleep -- 'unstable "
         "sleep' (Stages 1-2) is scored by the same blinded sleep-"
         "laboratory physicians from the same polysomnographic record."),
    ]:
        add("Song 2020", measure, tp, L, L, L, L, L,
            _song20_base + _song20_primary_sleep + " D4 Low for THIS result: " + note)

for tp in ("2 h after surgery", "4 h after surgery", "6 h after surgery", "24 h after surgery"):
    add("Song 2020", "Postoperative VAS pain score", tp, L, L, L, L, L,
        _song20_base +
        "D5 Low: pain is one of the trial's stated secondary outcomes "
        "('postoperative pain and adverse effects' were reported as "
        "secondary outcomes alongside PCA presses). D4 Low for THIS result: "
        "VAS is self-reported, but participants were successfully blinded "
        "by the active-sham design and data collectors recording the score "
        "were also blinded.")

for ae in ("Bradycardia", "Dizziness", "Nausea and vomiting adverse event", "Respiratory depression"):
    add("Song 2020", ae, "0-24 h", L, L, L, L, L,
        _song20_base +
        "D5 Low: adverse effects are named among the trial's stated "
        "secondary outcomes, and this adverse event is explicitly listed in "
        "the protocol's own adverse-reaction tracking ('appropriately treat "
        "the adverse reactions within 24 hours after surgery, such as "
        "hypotension, bradycardia, nausea and vomiting'). D4 Low for THIS "
        "result: an observable adverse event recorded by data collectors "
        "who were blinded to group assignment.")


# ============================================================================
# Zhu 2022 (covidence_381_full_article.pdf) -- trial design established in
# draft_assessments.py: D1 Some concerns (sound sequence, but concealment
# defeated by letting the participant choose their own envelope); D2 Some
# concerns (assessor-blinded only -- usual-care comparator, no sham, so
# participants and the acupuncturist were aware of allocation; 'Neither the
# anesthetists/surgeons nor the assessors were aware of the group
# allocation'); D3 Low (13/413 excluded, documented reasons, EM imputation
# for the rest). This trial has an unusually comprehensive published outcome
# list, so most results here ARE pre-specified.
# ============================================================================
_zhu22_base = (
    "D1 Some concerns: the sequence was sound -- 'randomly assigned ... "
    "using a computer-generated randomization sequence and secure code', "
    "'printed and stored in sequentially numbered, opaque, sealed "
    "envelopes' -- but 'Eligible participants chose one envelope, which was "
    "opened by the acupuncturist', which defeats the sequential concealment "
    "the envelope numbering was meant to provide. D2 Some concerns: "
    "assessor-blinded only -- a usual-care comparator with no sham means "
    "participants and the acupuncturist were aware of allocation -- but "
    "'Neither the anesthetists/surgeons nor the assessors were aware of the "
    "group allocation'. D3 Low: 13 of 413 (3.1%) excluded with documented "
    "reasons; missing data handled by an expectation-maximisation "
    "procedure. ")
_zhu22_primary = (
    "D5 Low: 'The primary outcome measures were the incidence of PON and "
    "POV at 6-24 h after surgery, and pain on movement at 24 h.'")
_zhu22_secondary = (
    "D5 Low: explicitly named among the secondary outcomes -- 'The "
    "secondary outcomes included severity of PON and POV; number of "
    "patients requiring postoperative rescue antiemetics and analgesics at "
    "0-6 h, 6-24 h, 24-48 h and 48-72 h after surgery; and incidence of PON "
    "and POV' at the remaining windows.")

add("Zhu 2022", "Postoperative nausea", "6-24 h postoperatively", S, S, L, S, L,
    _zhu22_base + _zhu22_primary +
    " D4 Some concerns for THIS result: nausea is an internal sensation "
    "only the unblinded participant can report.")
for tp in ("0–6 h after surgery", "24–48 h after surgery", "48–72 h after surgery"):
    add("Zhu 2022", "Postoperative nausea incidence", tp, S, S, L, S, L,
        _zhu22_base + _zhu22_secondary +
        " D4 Some concerns for THIS result: identical reasoning to the "
        "primary-window nausea result -- a subjective sensation reported by "
        "an unblinded participant.")
    add("Zhu 2022", "Postoperative vomiting incidence", tp, S, S, L, L, L,
        _zhu22_base + _zhu22_secondary +
        " D4 Low for THIS result: unlike nausea, vomiting is an objectively "
        "observable event, scored by assessors who were blinded to "
        "allocation.")
for tp in ("0–6 h after surgery", "6–24 h after surgery", "24–48 h after surgery"):
    add("Zhu 2022", "Nausea severity score", tp, S, S, L, S, L,
        _zhu22_base + _zhu22_secondary +
        " D4 Some concerns for THIS result: severity of the same subjective "
        "sensation as nausea incidence, rated on the trial's 4-point scale "
        "by the unblinded participant.")
    add("Zhu 2022", "Vomiting severity score", tp, S, S, L, L, L,
        _zhu22_base + _zhu22_secondary +
        " D4 Low for THIS result: vomiting severity on this scale reflects "
        "the observed frequency/character of an objective event, scored by "
        "blinded assessors.")
    add("Zhu 2022", "Participants requiring metoclopramide rescue antiemetic", tp, S, S, L, S, L,
        _zhu22_base + _zhu22_secondary +
        " D4 Some concerns for THIS result: 'metoclopramide 10 mg was "
        "infused as an antiemetic \"rescue\" therapy to any patient who "
        "experienced nausea [or] vomiti[ng]' -- triggered by the "
        "participant's own (partly subjective, nausea-inclusive) symptom "
        "report, even though the threshold is applied by a blinded "
        "assessor.")
for tp in ("6–24 h", "0–6 h", "24–48 h", "48–72 h"):
    d5 = _zhu22_primary if tp == "6–24 h" else _zhu22_secondary.replace(
        "severity of PON and POV", "severity of postoperative pain")
    add("Zhu 2022", "Pain on movement (NRS)", tp, S, S, L, S, L,
        _zhu22_base + d5 +
        " D4 Some concerns for THIS result: NRS pain on movement is "
        "self-reported by the unblinded participant; 'Flurbiprofen 100 mg "
        "was administered when the numerical rating scale (NRS) pain score "
        "was >3', so the participant's own awareness of allocation can "
        "influence both the score and, downstream, the rescue trigger.")
add("Zhu 2022", "Participants requiring postoperative analgesics", "0–48 h after surgery", S, S, L, S, L,
    _zhu22_base + _zhu22_secondary.replace("rescue antiemetics and analgesics",
                                           "rescue antiemetics AND analgesics") +
    " D4 Some concerns for THIS result: identical reasoning to the "
    "metoclopramide-rescue result -- triggered by the participant's own NRS "
    "pain report.")
add("Zhu 2022", "Time to passage of first flatus", "From end of surgery to first flatus", S, S, L, S, L,
    _zhu22_base +
    "D5 Low: 'time to passage of first flatus after surgery' is explicitly "
    "listed among the paper's reported secondary results. D4 Some concerns "
    "for THIS result: as in every other trial in this review reporting this "
    "endpoint, the timing of first flatus depends in part on the "
    "(unblinded) participant noticing and reporting it.")
add("Zhu 2022", "Overall QoR-15", "AMBIGUOUS", S, S, L, S, S,
    _zhu22_base +
    "D5 Some concerns: QoR-15 is named among the secondary outcomes ('and "
    "quality of recovery (QoR)-15 scores after surgery'), but no specific "
    "assessment timepoint is stated in the extracted data, which the "
    "worklist itself flags as ambiguous. D4 Some concerns for THIS result: "
    "QoR-15 is a self-completed questionnaire, and participants were not "
    "blinded.",
    "assessment timepoint for QoR-15 is not stated (AMBIGUOUS)")


# ============================================================================
# Lu 2022 (getfile.php-3.pdf) -- trial design established in
# draft_assessments.py: D1 Low (computer-generated allocation, sealed
# envelopes not opened until allocation); D2 Some concerns ('For logistic
# reasons, blinding the patients was hard to perform', but 'Investigators
# involved in the follow-up were blinded to the group allocation'); D3 Low (6
# of 100 excluded post-randomisation, documented reasons). Every result in
# this study's priority-2 set is explicitly named in one comprehensive
# secondary-outcomes sentence.
# ============================================================================
_lu22_base2 = (
    "D1 Low: 'randomly assigned to the TEAS or Control group in a ratio of "
    "1:1 using a computer-generated random allocation sequence'; 'The "
    "randomization code for each patient was put in sealed envelope and not "
    "opened until allocation'. D2 Some concerns: 'For logistic reasons, "
    "blinding the patients was hard to perform', but 'Investigators involved "
    "in the follow-up were blinded to the group allocation'. D3 Low: 6 of "
    "100 (6%) excluded post-randomisation with documented reasons (5 "
    "conversions to open surgery, 1 refusal). ")
_lu22_secondary2 = (
    "D5 Low: explicitly named in the trial's secondary-outcomes sentence -- "
    "'time to flatus, time to first defecation, and time to first oral "
    "intake; pain intensity assessed by visual analogue scale (VAS), "
    "attempts and deliveries of patient-controlled analgesia (PCA), "
    "postoperative nausea and vomiting (PONV), quality of sleeping (QoS) "
    "and quality of recovery (QoR) evaluated at 24h, 48h and 72h after "
    "surgery'.")

add("Lu 2022", "Exact cumulative PCA opioid consumption", "0-24 h", L, S, L, L, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Low for THIS result: cumulative PCA consumption is read from the "
    "device log, an objective record of the (unblinded) participant's own "
    "button presses, not a clinician's judgement call.")
for tp in ("48 h after surgery", "72 h after surgery"):
    add("Lu 2022", "PCA attempts", tp, L, S, L, L, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Low for THIS result: PCA attempts are counted directly from "
        "the device log.")
    add("Lu 2022", "Successful PCA deliveries", tp, L, S, L, L, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Low for THIS result: identical reasoning to PCA attempts -- an "
        "objective device count.")
add("Lu 2022", "PCA attempts", "24 h", L, S, L, L, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Low for THIS result: PCA attempts are counted directly from the "
    "device log.")
add("Lu 2022", "Successful PCA deliveries", "24 h", L, S, L, L, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Low for THIS result: identical reasoning to PCA attempts -- an "
    "objective device count.")
add("Lu 2022", "PONV incidence", "24 h after surgery", L, S, L, S, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Some concerns for THIS result: PONV in this trial is reported as a "
    "single combined incidence rather than split into nausea and vomiting; "
    "because a positive case can be driven purely by the subjective nausea "
    "component, and participants were not blinded, this combined measure "
    "is treated cautiously rather than assumed objective.",
    "PONV reported as one combined measure rather than split nausea/vomiting")
add("Lu 2022", "QoR-15 score", "24 h after surgery", L, S, L, S, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Some concerns for THIS result: QoR-15 is a self-completed "
    "questionnaire, and participants were not blinded.")
add("Lu 2022", "VAS at cough", "24 h after surgery", L, S, L, S, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Some concerns for THIS result: VAS is self-reported by the "
    "unblinded participant.")
add("Lu 2022", "VAS at rest", "24 h after surgery", L, S, L, S, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Some concerns for THIS result: identical reasoning to VAS at "
    "cough -- self-reported by the unblinded participant.")

for tp in ("48 h after surgery", "72 h after surgery"):
    add("Lu 2022", "PONV incidence", tp, L, S, L, S, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Some concerns for THIS result: PONV in this trial is reported "
        "as a single combined incidence rather than split into nausea and "
        "vomiting; because a positive case can be driven purely by the "
        "subjective nausea component, and participants were not blinded, "
        "this combined measure is treated cautiously rather than assumed "
        "objective.",
        "PONV reported as one combined measure rather than split nausea/vomiting")
    add("Lu 2022", "QoR-15 score", tp, L, S, L, S, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Some concerns for THIS result: QoR-15 is a self-completed "
        "questionnaire, and participants were not blinded.")
    add("Lu 2022", "VAS at cough", tp, L, S, L, S, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Some concerns for THIS result: VAS is self-reported by the "
        "unblinded participant.")
    add("Lu 2022", "VAS at rest", tp, L, S, L, S, L,
        _lu22_base2 + _lu22_secondary2 +
        " D4 Some concerns for THIS result: identical reasoning to VAS at "
        "cough -- self-reported by the unblinded participant.")
add("Lu 2022", "Time to first oral intake of water", "Postoperative", L, S, L, S, L,
    _lu22_base2 + _lu22_secondary2 +
    " D4 Some concerns for THIS result: the trial's own authors identify "
    "this as a limitation -- 'the time to resume oral intake can be "
    "influenced by the patient's perception and the clinician' -- which is "
    "exactly the D4 concern this domain is meant to capture.",
    "authors themselves flag this endpoint as influenced by patient perception")


# ============================================================================
# Sun 2017 (sun2017-2.pdf) -- a genuinely well-blinded 4-arm trial. D1 Low:
# 'a SPSS-generated random number table was used to allocate the patients';
# 'The TEAS operators were informed the group allocation ... by a sealed
# opaque envelope and they were the only individuals aware of the treatment
# allocation, while patients, anesthes[iologist evaluators were blinded]'.
# D2 Low: 'randomized, patient and anesthesiologist evaluator blinded ...
# sham TEAS-controlled design'; 'Patients' blinding was achieved by using
# electrodes and being stimulated with the minimal current that the patient
# could feel' -- a genuine active-sensation sham, not a silent no-current
# control. D3 Low: 19 of 380 (5%) withdrawn with fully documented reasons
# (8 lost to follow-up, 6 change of surgery, 2 prolonged surgery, 3
# intraoperative complications).
# ============================================================================
_sun17_base = (
    "D1 Low: 'a SPSS-generated random number table was used to allocate the "
    "patients into 1 of the 4 groups in a 1:1:1:1 ratio'; 'The TEAS "
    "operators were informed the group allocation of the patient by a "
    "sealed opaque envelope and they were the only individuals aware of the "
    "treatment allocation'. D2 Low: 'randomized, patient and "
    "anesthesiologist evaluator blinded, controlled clinical trial'; "
    "'Patients' blinding was achieved by using electrodes and being "
    "stimulated with the minimal current that the patient could feel in the "
    "same therapeutic setting' -- a genuine active-sensation sham rather "
    "than a silent no-current control. D3 Low: 19 of 380 (5%) withdrawn, "
    "all with documented reasons (8 lost to follow-up, 6 change of surgery, "
    "2 prolonged surgery time, 3 intraoperative complications). ")
_sun17_primary = (
    "D5 Low: 'The primary outcomes were resting and activity pain intensity "
    "evaluated by VAS at 1, 6, 24, and 48 hours after surgery.'")
_sun17_secondary = (
    "D5 Low: explicitly named among the secondary outcomes -- 'intraoperative "
    "propofol and opioid consumption, incidence of postoperative nausea and "
    "vomiting, supplementary analgesic and antiemetic requirements within 48 "
    "hours, extubation time, length of stay in PACU, time of the first "
    "postoperative flatus and defecation, and patient satisfaction'.")
_sun17_d4_blinded = (
    " D4 Low for THIS result: both the participant and the anaesthesiologist "
    "evaluator were successfully blinded in this trial, so neither the "
    "self-reported nor the clinician-assessed component of this outcome is "
    "exposed to differential awareness of allocation.")

for tp in ("1 h", "6 h", "24 h", "48 h"):
    if tp != "24 h":
        add("Sun 2017", "Activity-evoked VAS during coughing", tp, L, L, L, L, L,
            _sun17_base + _sun17_primary + _sun17_d4_blinded)
    add("Sun 2017", "Resting VAS", tp, L, L, L, L, L,
        _sun17_base + _sun17_primary + _sun17_d4_blinded)
add("Sun 2017", "Nausea", "Within 48 h after surgery", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Vomiting", "Within 48 h after surgery", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Additional antiemetic requirement", "Within 48 h after surgery", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Supplemental flurbiprofen axetil requirement", "Within 48 h", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Postoperative opioid consumption", "0-24 h", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Author-defined intraoperative morphine-equivalent exposure", "Intraoperative",
    L, L, L, L, S,
    _sun17_base +
    "D5 Some concerns: 'intraoperative propofol and opioid consumption' is "
    "the named secondary outcome, but this specific morphine-equivalent "
    "conversion is the review's own construct rather than a number the "
    "paper itself reports, so it is not literally the pre-specified "
    "outcome even though it is derived from one that is." +
    _sun17_d4_blinded,
    "morphine-equivalent value is a review-derived conversion, not the paper's own reported metric")
add("Sun 2017", "Extubation time", "Postoperative", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Length of stay in PACU", "Postoperative", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Time to first postoperative defecation", "Postoperative", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Time to first postoperative flatus", "Postoperative", L, L, L, L, L,
    _sun17_base + _sun17_secondary + _sun17_d4_blinded)
add("Sun 2017", "Patient satisfaction — extremely satisfied",
    "Postoperative assessment; exact clock time not separately stated", L, L, L, L, L,
    _sun17_base + _sun17_secondary +
    " D4 Low for THIS result: 'Patient satisfaction was evaluated with a "
    "5-point scale', self-reported but by a genuinely blinded participant.")
add("Sun 2017", "TEAS-related side effects", "0–48 h postoperative", L, L, L, S, S,
    _sun17_base +
    "D5 Some concerns: device-related side effects are mentioned narratively "
    "('No side effect related to ...') but are not individually itemised "
    "among the trial's named primary or secondary outcomes. D4 Some "
    "concerns for THIS result: the report does not describe how or by whom "
    "TEAS-related side effects were ascertained, so the measurement process "
    "for this specific safety outcome is unclear despite the trial's "
    "otherwise strong blinding.",
    "TEAS-related side effects not individually named as a pre-specified outcome; ascertainment method unclear")


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
