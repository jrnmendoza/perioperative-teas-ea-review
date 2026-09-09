#!/usr/bin/env python3
"""
Result-specific Cochrane RoB 2 assessments for the 36 priority-1 results.

PROVENANCE. Each judgement was produced by reading the mapped source PDF
against the RoB 2 signalling questions; nothing here is copied from an earlier
study-wide judgement. Standard Cochrane RoB 2 practice calls for two
independent assessors reconciling any disagreement. On 2026-09-08 the review
lead (John Ryan N. Mendoza) directed, in this repository's working session,
that these source-evidence-derived judgements be adopted as the review's
current result-specific RoB 2 assessment; that direction is recorded in
ADOPTED_BY / ADOPTED_DATE below. No separately documented independent
dual-assessor record was provided to this pipeline to verify against, so that
should not be inferred from the ADOPTED status. Nothing here is written into
the frozen v34 workbook.

Each judgement is anchored to quoted text with a page locator in
evidence.json, extracted by extract_evidence.py from the mapped source in
pdf_map.json. Domains are judged for THIS result, not for the study: D4 in
particular turns on who measured this specific outcome and whether they were
blinded, and no study-wide judgement is copied onto a different result.

Overall risk follows the RoB 2 algorithm: High if any domain is High;
Some concerns if any domain is Some concerns and none is High; Low only if
every domain is Low.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKLIST = ROOT / "09_V34_ANALYSIS" / "v34_rob2_worklist.csv"

L, S, H = "Low", "Some concerns", "High"

# (study, outcome, timepoint) -> domains + rationale.
# Rationale strings quote the source; the page locator is in evidence.json.
A: dict[tuple, dict] = {}


def add(study, outcome, timepoint, d1, d2, d3, d4, d5, why, flags=""):
    A[(study, outcome, timepoint)] = dict(
        d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, rationale=why, flags=flags)


# ── Chen 2015 (thyroidectomy) ─────────────────────────────────────────────
add("Chen 2015", "PONV incidence", "0-24 h", L, L, L, L, L,
    "D1: 'assigned ... by a table of computer-generated random numbers', 1:1, "
    "'sealed in sequentially numbered opaque envelopes'; baseline comparable (Table 1). "
    "D2: 'The patients, attending anesthesiologist, surgeons and data collector were blinded "
    "to group assignment'; placebo-controlled with a no-stimulation device. "
    "D3: 1 of 84 excluded for protocol breach (1.2%), 83 analysed. "
    "D4: PONV recorded by the blinded data collector; no measurement difference between arms. "
    "D5: registered NCT02333747; PONV named as a pre-specified secondary outcome in Methods.")

# ── Chen 2015 (hyperalgesia) ──────────────────────────────────────────────
add("Chen 2015 (Hyperalgesia)", "PONV incidence", "0-24 h", L, L, L, L, S,
    "D1: 'randomization was performed in a 1:1 ratio according to a computer-generated list'; "
    "'Group assignments were concealed in sealed envelopes'. "
    "D2: 'All study personnel including the patients, investigator, attending anesthetist, "
    "surgeons, recovery ward nurses, and the person who performed the statistical analysis "
    "were blinded'. D3: 1 of 60 excluded for protocol breach (1.7%). "
    "D4: PONV recorded within a blinded 24-h follow-up. "
    "D5 SOME CONCERNS: no trial registration or protocol identified in the report — only IRB "
    "approval (Ref: K2014-07-003) — so the paper's own statement that PONV was a pre-specified "
    "secondary outcome cannot be verified against an external record.",
    "no trial registration identified")

# ── Gao 2021 ──────────────────────────────────────────────────────────────
_gao_common = (
    "D1: 'SPSS software was used for block randomization in a 1:1 ratio with block size of 4'; "
    "'the central randomization administrator opened the sealed envelope and made the group "
    "allocation'. D2 SOME CONCERNS: participant blinding was not achieved — 'patients could not "
    "be blinded to the treatment due to the nature of the intervention, because they can sense "
    "the acupoint stimuli in the TEAS group compared to no treatment in the sham group'; "
    "'Intention-to-treat analysis was used for all enrolled patients' (all 610). "
    "D3: ITT, all 610 randomised analysed. "
    "D5: registered NCT03086304 with the protocol available as Appendix 1; the GI recovery "
    "times are named pre-specified secondary outcomes.")
add("Gao 2021", "Time to first bowel sounds", "Postoperative", L, S, L, L, L,
    _gao_common + " D4 LOW for THIS result: bowel sounds are established by auscultation by "
    "study personnel who 'were blinded to the patient's group allocation', so the measurement "
    "does not depend on the unblinded participant.")
add("Gao 2021", "Time to first defecation", "Postoperative", L, S, L, S, L,
    _gao_common + " D4 SOME CONCERNS for THIS result: the timing of first defecation is "
    "established from the participant's own report, and participants were not successfully "
    "blinded, so knowledge of assignment could influence when the event is reported.")
add("Gao 2021", "Time to first flatus", "Postoperative", L, S, L, S, L,
    _gao_common + " D4 SOME CONCERNS for THIS result: first flatus is entirely self-reported "
    "and participants were not successfully blinded; this is the outcome most exposed to "
    "reporting influenced by awareness of assignment.")

# ── Gu 2019 ───────────────────────────────────────────────────────────────
_gu_common = (
    "D1 SOME CONCERNS: 'randomized according to a computer-generated random numbers table', "
    "but no allocation-concealment mechanism is described anywhere in the report. "
    "D2: 'All patients were unaware of the group allocations'; interventionist, data collector "
    "and statistician separated and blinded; placebo C-TEAS comparator. "
    "D3: 117 of 120 completed (2.5% missing). "
    "D5 SOME CONCERNS: no trial registration and no protocol are reported — only ethics "
    "approval (RMYY-YWLL-2017-0120) — and the report never names its primary outcome, "
    "referring only to 'the primary outcome from a pilot study', so pre-specification of any "
    "reported result cannot be verified.")
add("Gu 2019", "Time to first bowel sounds", "Postoperative", S, L, L, L, S,
    _gu_common + " D4 LOW for THIS result: 'Bowel sounds were blindly noted every hour "
    "postoperatively by a surgical ICU nurse', with four-quadrant auscultation for over four "
    "minutes — assessor-measured, not self-reported.",
    "no trial registration identified")
add("Gu 2019", "Time to first defecation", "Postoperative", S, L, L, S, S,
    _gu_common + " D4 SOME CONCERNS for THIS result: 'The patients were instructed to "
    "self-record the first postoperative flatus and defecation' — self-reported timing, "
    "although participants were blinded to allocation.",
    "no trial registration identified")
add("Gu 2019", "VAS pain intensity", "24 h", S, L, L, L, S,
    _gu_common + " D4 LOW for THIS result: VAS is self-reported but participants were blinded "
    "to allocation and scores were collected by a blinded investigator at fixed timepoints; "
    "all pre-specified timepoints (4, 8, 16, 24, 36 h) are reported, so no within-outcome "
    "selection is evident.",
    "no trial registration identified")

# ── Guo 2023 ──────────────────────────────────────────────────────────────
add("Guo 2023", "Remifentanil consumption", "Intraoperative", L, L, S, L, S,
    "D1: 'A randomization sequence was generated by ... SPSS 25.0 ... and the allocation code "
    "was performed by an independent technician'; baseline well matched (Table 1). "
    "D2: 'The patients, anesthesiologists, surgeons, and observers were blinded to group "
    "assignment'; 'a standardized anesthetic protocol was elaborated and performed throughout "
    "the surgery'. "
    "D3 SOME CONCERNS: 18 of 128 randomised (14%) dropped out and only completers (55/55) were "
    "analysed, even though intraoperative remifentanil would have been recorded for every "
    "randomised patient; mitigated by the reported finding of 'No significant difference in "
    "baseline characteristics ... between the dropped patients and the completed patients'. "
    "D4: remifentanil was titrated to BIS 40-60 by a blinded anaesthetist and taken from records. "
    "D5 SOME CONCERNS: intraoperative remifentanil is not among the registered primary outcome "
    "(POCD by MoCA) or the listed secondary outcomes (MMSE, NRS pain and sleep, EORTC-QLQ-C30, "
    "chronic pain); it is reported as a perioperative anaesthetic characteristic.",
    "result not among pre-specified outcomes")

# ── He 2026 ───────────────────────────────────────────────────────────────
add("He 2026 (hepatectomy/JIS)", "PONV incidence", "0-24 h", L, L, L, L, L,
    "D1: allocation 1:1 'through a secure web-based randomization system'; 'The randomization "
    "sequence was generated using permuted blocks, stratified by treatment center'; the "
    "assignment was revealed by 'an independent investigator (uninvolved in anesthesia "
    "administration or outcome assessment)'. "
    "D2: genuine double-blinding — 'the beginning of the intervention after anesthesia "
    "induction ... ascertained the blinding of the participants', 'The stimulator was then "
    "placed inside an opaque box', and 'The patients, anesthesiologists, outcome assessors, "
    "and ward staff remained unaware of treatment assignments'; analysed as mITT. "
    "D3: 2 of 161 excluded (one cancelled surgery, one withdrew consent); PP sensitivity "
    "analysis agreed with mITT. "
    "D4: PONV ascertained by blinded assessors and ward staff on a defined scale. "
    "D5: registered NCT05396716; this is the pre-specified PRIMARY outcome, reported with "
    "predefined subgroups and a PP sensitivity analysis.")

# ── Huang 2025 ────────────────────────────────────────────────────────────
add("Huang 2025", "Time to first defecation", "Postoperative", L, H, S, H, L,
    "D1: 'A centralized randomization system ensured allocation concealment'; sequence "
    "'computer-generated by an independent statistician'. "
    "D2 HIGH: the comparator is standard care alone with no sham, so the report's claim that "
    "'Patients were blinded to their treatment allocation' is not credible for an intervention "
    "delivered by needling — the paper itself proposes that 'Future studies could incorporate a "
    "sham EA group ... to help control for placebo effects and improve blinding'; analysis is "
    "completers only, not ITT. A second, independent reviewer reached the same conclusion on "
    "2026-09-09 after reading the source directly, which reinforces rather than substitutes for "
    "this pipeline's own judgement. "
    "D3 SOME CONCERNS: 13 of 101 randomised (12.9%) are missing from the analysis (51->43 EA, "
    "50->45 control) with dropout criteria that include protocol violation and postoperative "
    "complications, and no ITT or sensitivity analysis. "
    "D4 HIGH for THIS result: 'The primary outcomes were the time ... to first flatus and bowel "
    "movement, as recorded by patients, family members, or caregivers' — self-reported timing by "
    "unblinded participants and their families. "
    "D5 LOW: registered (MR-51-24-038798) with defecation as a co-primary, correctly reported. "
    "An earlier reading of this source flagged an apparent internal numeric inconsistency between "
    "a flatus value pair quoted in different sections (36.4+/-8.0 vs 36.20+/-8.20 and 42.2+/-8.5 "
    "vs 42.72+/-8.76); a second independent reviewer confirmed on 2026-09-09 that the '36.20/8.20, "
    "42.72/8.76' pair belongs to a distinct 2023 pilot study cited for the sample-size "
    "calculation, not a competing estimate of this trial's own flatus outcome — so this is not an "
    "unresolved reporting inconsistency for the defecation result assessed here, and this "
    "pipeline's own separately-extracted flatus and defecation rows (36.4/42.2 and 46.0/51.3 "
    "respectively) already match the confirmed trial values with no correction needed.",
    "SOURCE-QC: apparent numeric inconsistency between abstract/Results and p.4 text, resolved "
    "2026-09-09 as pilot-study data (2023) vs this trial's own data, not a live inconsistency")

# ── Lee 2011 ──────────────────────────────────────────────────────────────
add("Lee 2011", "VAS pain intensity", "24 h", S, S, H, L, H,
    "D1 SOME CONCERNS: 'A random number table was used for grouping', but the report also states "
    "'each subject was assigned to a treatment group in numbered order, as they became "
    "available', which describes sequential assignment; no allocation-concealment mechanism is "
    "described and no by-group baseline table is presented. "
    "D2 SOME CONCERNS: described as double-blind and 'group assignments were kept fully blinded "
    "from the subjects and data collectors', with a no-stimulation sham SSP electrode; but no "
    "ITT and no protocol. "
    "D3 HIGH for THIS result: 'Two of the subjects from Group 4 were excluded from the analysis "
    "due to the inability to carry out the VAS' — 2 of 12 (17%) missing from the intervention "
    "arm only, and the missingness is in the very outcome being assessed; no sensitivity analysis. "
    "D4: VAS is self-reported but subjects were blinded to allocation. "
    "D5 HIGH: no trial registration, no protocol, no sample size calculation and no stated "
    "primary outcome; multiple pain and PCA endpoints across many time intervals are reported "
    "with no pre-specified analysis plan.",
    "no trial registration identified; outcome-related missing data")

# ── Liang 2021 ────────────────────────────────────────────────────────────
_liang_common = (
    "D1: 'randomly distributed into two groups, with the help of a computer-generated table of "
    "random numbers by an independent statistician'; that statistician 'created identical sealed "
    "envelopes before surgery'. "
    "D2: 'An anesthesiologist (LDD), who was not aware of the allocation, performed general "
    "anesthesia and all intraoperative data recording, and another investigator (WL), in charge "
    "of all postoperative assessments, was also blinded to the group identity'. "
    "D3: 5 of 75 randomised lost (surgical procedure change n=3; blood-sample loss), 6.7%, with "
    "documented reasons unrelated to the outcome; CONSORT reports none excluded from analysis "
    "of those followed up.")
add("Liang 2021", "Global QoR-40", "24 h (T11)", L, L, L, L, L,
    _liang_common + " D4 LOW for THIS result: the validated Chinese QoR-40 was administered at "
    "pre-defined timepoints (T0, T11, T12) by the blinded postoperative investigator to blinded "
    "participants. D5: registered ChiCTR1800019951; QoR-40 at T11 is defined in Methods 2.7 as a "
    "pre-specified assessment and is reported in full across all its five subscales.")
for _op in ("Remifentanil consumption", "Sufentanil consumption"):
    add("Liang 2021", _op, "Intraoperative", L, L, L, L, S,
        _liang_common + f" D4 LOW for THIS result: {_op.split()[0].lower()} was recorded "
        "intraoperatively by the anaesthesiologist who was explicitly 'not aware of the "
        "allocation'. D5 SOME CONCERNS: the trial's stated outcomes centre on catheter-related "
        "bladder discomfort, MMSE, PONV, pain and QoR-40; intraoperative opioid consumption "
        "appears in Table 1 as an anaesthetic characteristic rather than as a named "
        "pre-specified outcome.",
        "result not among pre-specified outcomes")

# ── Lu 2021 ───────────────────────────────────────────────────────────────
add("Lu 2021", "Total remifentanil", "Intraoperative", L, L, L, L, L,
    "D1: randomised 1:1:1 'using a secured web-based system that was stratified according to "
    "permuted blocks' across six centres; baseline characteristics did not differ. "
    "D2: 'We performed all the analyses in an intention-to-treat population'; although 'The "
    "patients and investigators who participated in the intervention were not masked', 'The "
    "stimulator was placed in an opaque box to blind the surgical team and anesthesiologist', "
    "and protocol adherence was audited by an independent observer. "
    "D3: this is an intraoperative measurement with no missing data — all 190/188 randomised "
    "patients contribute. "
    "D4: remifentanil was administered and recorded by the anaesthesia team, who were blinded by "
    "the opaque-box arrangement. "
    "D5: registered NCT02741726 with the protocol supplied; 'The secondary endpoints included "
    "remifentanil consumption during general anesthesia' — explicitly pre-specified.")

# ── Lu 2022 ───────────────────────────────────────────────────────────────
_lu22_common = (
    "D1: 'randomly assigned ... in a ratio of 1:1 using a computer-generated random allocation "
    "sequence'; 'The randomization code for each patient was put in sealed envelope and not "
    "opened until allocation'; multicentre. "
    "D2 SOME CONCERNS: participants were not blinded — 'For logistic reasons, blinding the "
    "patients was hard to perform' and 'The patient may tell the investigator who did the "
    "follow-up that he/she felt a stimuli'; the mITT population excludes 6 randomised patients, "
    "one of them 'due to rejection to TEAS', which is an exclusion related to a deviation from "
    "the intended intervention. "
    "D3: 6 of 100 (6%) excluded post-randomisation with documented reasons (5 conversions to "
    "open surgery, 1 refusal). "
    "D5: registered NCT02921529; 'The secondary outcomes included time to flatus, time to first "
    "defecation' — both explicitly pre-specified.")
add("Lu 2022", "Time to first flatus", "Postoperative", L, S, L, S, L,
    _lu22_common + " D4 SOME CONCERNS for THIS result: first flatus is self-reported by "
    "unblinded participants; the authors themselves note that 'flatus is sometimes regarded as "
    "an insensitive index' and chose defecation instead precisely because it is more objective.")
add("Lu 2022", "Time to first defecation", "Postoperative", L, S, L, L, L,
    _lu22_common + " D4 LOW for THIS result: the authors adopted 'time to defecation as one "
    "secondary endpoint, because [it is] more objective and can be recorded by the assessor "
    "without bias', and 'Investigators involved in the follow-up were blinded to the group "
    "allocation'.")

# ── Ng 2013 ───────────────────────────────────────────────────────────────
add("Ng 2013", "Time to first bowel motion / defecation", "Postoperative", S, L, L, L, L,
    "D1 SOME CONCERNS: 'Patients were randomized (using simple randomization)' and 'A sealed "
    "nonopaque envelope ... was opened to determine the limb of entry' — the report states "
    "explicitly that the concealment envelopes were NOT opaque, so allocation could in principle "
    "be foreseen. "
    "D2: 'the patients randomized to the EA/SA groups and the outcome assessor were blinded to "
    "the treatment allocation'; the assessed contrast is EA vs sham acupuncture, both blinded "
    "arms. D3: 'There was no withdrawal or dropout, and all recruited patients were available "
    "for analysis of primary and secondary outcomes'. "
    "D4: 'the time to defecation ... from the time the laparoscopic surgery ended until the first "
    "observed passage of stool', recorded by the blinded assessor; the authors adopted it "
    "'because it is more objective and can be recorded readily by the assessor without bias'. "
    "D5: registered NCT00464425; this is the single pre-specified primary outcome.")

# ── Ntritsou 2014 ─────────────────────────────────────────────────────────
add("Ntritsou 2014", "Remifentanil consumption", "Intraoperative", L, S, S, H, S,
    "D1: 'randomly divided into two groups using a computer-generated randomisation sequence'; "
    "'The randomisation was concealed by the director of the anaesthesiology department'. "
    "D2 SOME CONCERNS: the trial is single-blind by design — 'The study was single blind because "
    "the patients were anaesthetised during the initial application of the EA intervention' — "
    "and the theatre team delivering anaesthesia was not blinded to the presence of needles. "
    "D3 SOME CONCERNS: 'Three patients from the control group and two patients from the EA group "
    "were excluded during the study' (5 of 75, 6.7%) with no reasons reported. "
    "D4 HIGH for THIS result: intraoperative remifentanil is titrated by the anaesthetist, and "
    "'anaesthesia was conducted by one of a team of five anaesthetists' who were not blinded to "
    "the EA intervention — the person deciding and recording the dose is aware of allocation. "
    "The blinding that is described covers postoperative assessment, not intraoperative dosing. "
    "D5 SOME CONCERNS: remifentanil consumption is not among the trial's stated outcomes (NRS "
    "and SF-MPQ pain, algometry, cortisol, rescue analgesia, STAI); it appears in Table 1 as an "
    "anaesthetic characteristic.",
    "result not among pre-specified outcomes; unblinded dose-setter is the outcome recorder")

# ── Pan 2023 ──────────────────────────────────────────────────────────────
_pan_common = (
    "D1 SOME CONCERNS: 'Patients were assigned to TEAS group (Group T) and control group "
    "(Group C) using random number tables', with no allocation-concealment mechanism described. "
    "D2 SOME CONCERNS: described as a 'double-blind randomized control-group clinical trial', but "
    "the comparator is a control group and the report does not describe a sham device, so "
    "successful participant blinding is not established. "
    "D3 LOW: 105 patients were randomised (52 / 53) and 105 were analysed; the 15 documented "
    "exclusions (6 non-protocol analgesics, 6 different surgical procedure, 2 PCIA use, "
    "1 intraoperative bleeding) occur in the enrolment flow before randomisation. "
    "D5: registered ChiCTR2100045173; QoR-40 at 24 h is the stated primary outcome and "
    "'dosage of remifentanil, propofol, any vasoactive drugs' is listed among the secondary "
    "outcome measures.")
add("Pan 2023", "Intraoperative remifentanil", "Intraoperative", S, S, L, S, L,
    _pan_common + " D4 SOME CONCERNS for THIS result: the report documents blinding for the PACU "
    "nurse who collected NRS scores but does not state that the anaesthetist who titrated and "
    "recorded intraoperative remifentanil was blinded.")
add("Pan 2023", "Total QoR-40 score", "24 h after operation", S, S, L, S, L,
    _pan_common + " D4 SOME CONCERNS for THIS result: QoR-40 is a participant-completed "
    "questionnaire and successful participant blinding is not established, so the respondent may "
    "have been aware of the assigned intervention.")

# ── Song 2020 ─────────────────────────────────────────────────────────────
add("Song 2020", "Total intraoperative sufentanil consumption", "Intraoperative", L, L, L, L, S,
    "D1: 'divided to the TEAS group or control group randomly in a 1:1 ratio using a "
    "computer-generated randomization number sequence'; 'Seal the group assignments in "
    "sequentially numbered opaque envelopes'. "
    "D2: 'Patients, attending anesthesiologists, surgeons and data collectors ... were all "
    "blinded to the group assignment', and the comparator is active non-acupoint stimulation at "
    "a matched 2/10 Hz so that 'the low-frequency stimuli were set to the same frequency ... "
    "resulting in the patients believing that they were undergoing real TEAS therapy' — an "
    "unusually strong blind; 'All analyses were based on the intention-to-treat (ITT) population'. "
    "D3: ITT includes all 85 randomised participants (42/43). "
    "D4: intraoperative sufentanil was administered and recorded by a blinded anaesthesiologist. "
    "D5 SOME CONCERNS: prospectively registered NCT04124679, with the Athens Insomnia Scale as "
    "the primary outcome and postoperative pain/adverse effects/PCA presses as the reported "
    "secondary outcomes; total intraoperative sufentanil is not among them and is reported in "
    "Table 1 as an anaesthetic characteristic.",
    "result not among pre-specified outcomes")

# ── Wang 2023 ─────────────────────────────────────────────────────────────
add("Wang 2023", "Time to first flatus", "Postoperative", L, L, S, L, S,
    "D1: 'Patients were assigned to either the TEAS group or the Sham group by a table of "
    "computer-generated random numbers'; 'Group assignments were sealed in sequentially numbered "
    "opaque envelopes'; two-step screening with randomisation at final enrolment. "
    "D2: 'Patients, attending surgeons, operating room nurses, data collectors and individuals "
    "who performed the final statistical analysis were blinded to group assignment'; multicentre "
    "double-blind with a no-current sham. "
    "D3 SOME CONCERNS: 5 of 88 randomised were excluded post-randomisation 'because of a "
    "protocol breach' and only the 83 completers were analysed; for this outcome 40/43 of the "
    "randomised 43/45 contribute, with no ITT or sensitivity analysis. "
    "D4: first flatus is self-reported, but participants were blinded by a credible no-current "
    "sham and the data collectors were blinded. "
    "D5 SOME CONCERNS: registered ChiCTR2100054971 with postoperative sleep quality as the "
    "primary outcome; the listed secondary outcomes are VAS scores, rescue analgesia, abdominal "
    "distension, dizziness and PONV — time to first flatus is reported among the postoperative "
    "recovery data without being individually named in the pre-specified outcome list.",
    "pre-specification of this outcome not clearly established")

# ── Wang 2024 ─────────────────────────────────────────────────────────────
add("Wang 2024", "Total sufentanil", "Intraoperative", L, S, S, L, S,
    "D1: 'A random allocation sequence was generated by using computer-generated random "
    "numbers'; '140 sequentially numbered envelopes containing the allocations were prepared' by "
    "'A physician independent of the study'; the OD vs ODT contrast is randomised within the "
    "SNVP stratum. "
    "D2 SOME CONCERNS: 'This was a double-blinded study' and 'Patients and other clinical staff, "
    "including anesthesiologists, surgeons, and ward staff, were unaware of this allocation', but "
    "'The investigator who administered the interventions was not blinded' and the report does "
    "not describe a sham device for the OD arm. "
    "D3 SOME CONCERNS: 33 of the 35 randomised to SNVP-ODT contribute to this result; the report "
    "gives no reason for the two missing participants. "
    "D4: intraoperative sufentanil was administered and recorded by anaesthesiologists who were "
    "explicitly 'unaware of this allocation'. "
    "D5 SOME CONCERNS: prospectively registered on 28 November 2021 (ChiCTR2100053752) with "
    "'The primary outcome was the incidence of PONV within 36 h' and 'The secondary outcome was "
    "the serum GDF-15 level'; total intraoperative sufentanil is not among them and appears in "
    "Table 1 as an anaesthetic characteristic.",
    "result not among pre-specified outcomes")

# ── Wu 2022 ───────────────────────────────────────────────────────────────
add("Wu 2022", "Cumulative remifentanil", "Intraoperative", S, L, S, L, L,
    "D1 SOME CONCERNS: 'All patients (n = 90) were randomized using a computer-generated "
    "number', with no allocation-concealment mechanism described; baseline characteristics were "
    "similar. "
    "D2: 'All researchers involved in this study were blinded to these groupings' and 'The "
    "acupoint of the pTEAS device was given on patients' legs or hands that were fully covered "
    "by the materials to ensure the pTEAS device was out of sight of blinded researchers'. "
    "D3 SOME CONCERNS: 6 of 90 (6.7%) excluded, and the loss is differential — 5 from the "
    "Control arm versus 1 from pTEAS (2 massive haemorrhage, one in each arm; 1 serious "
    "postoperative complication in Control; 3 with incomplete data collection). Excluding a "
    "patient for a POSTOPERATIVE complication discards an intraoperative value that had already "
    "been measured, and no ITT or sensitivity analysis is reported. "
    "D4: remifentanil was recorded from intraoperative records by a blinded team. "
    "D5: registered ChiCTR1800014634 (25/01/2018) and 'The consumption of remifentanil' is named "
    "as a primary outcome; note the report cites the registry inconsistently as "
    "'clinicaltrials.gov (chiCTR1800014634)' and declares three co-primary outcomes without "
    "multiplicity adjustment.",
    "differential attrition; three declared co-primaries without adjustment")

# ── Xing 2022 ─────────────────────────────────────────────────────────────
_xing_common = (
    "D1: 'We randomized patients ... using computer-generated random numbers'; 'Randomization "
    "codes were kept in a sealed envelope and relayed to an independent nurse'. "
    "D2: 'The allocation was blinded for all patients, surgeons, the leading anesthesiologist, "
    "physician in the post-anesthesia care unit, and follow-up observers until the end of the "
    "study', and 'The TEAS stimulator was obscured by an opaque cloth throughout the experiment'; "
    "the comparator is sham TEAS with the same TAP block. "
    "D3: 1 participant lost to follow-up in each of the two relevant arms (29/29 of 30/30, 3.3%). "
    "D5 SOME CONCERNS: registered ChiCTR2100042119 with QoR-15 as the primary outcome; both "
    "results here are reported under 'Other secondary outcomes ... shown in Table 3' without "
    "being individually named in a pre-specified list. The report also states an allocation "
    "ratio of '1:1:1' when describing the three arms (general anesthesia, TAPB, TEAS combined "
    "with TAPB) but '1:1:1:1' in the Randomization section; a second independent reviewer "
    "confirmed on 2026-09-09 that this is an apparent typo rather than an unreported fourth arm "
    "— the abstract, the sample-size calculation (30x3=90), the intervention matrix, the analysed "
    "n (29+29+29=87), and every results table are all consistent with a genuine three-arm design. "
    "D5 remains Some concerns for the separate, unaffected reason that these outcomes are not "
    "individually pre-specified.")
add("Xing 2022", "Time to first flatus", "Postoperative", L, L, L, L, S,
    _xing_common + " D4 LOW for THIS result: first flatus is self-reported but participants were "
    "blinded by an active sham, and 'The researchers who conducted data collection and performed "
    "the outcome assessment were blinded to group allocation'.",
    "1:1:1 vs 1:1:1:1 allocation ratio wording; resolved 2026-09-09 as an apparent typo, not an "
    "unreported fourth arm")
add("Xing 2022", "Total remifentanil consumption", "Intraoperative", L, L, L, L, S,
    _xing_common + " D4 LOW for THIS result: 'Remifentanil and propofol consumption ... were "
    "recorded' by an anaesthesia team blinded by the opaque-cloth arrangement.",
    "1:1:1 vs 1:1:1:1 allocation ratio wording; resolved 2026-09-09 as an apparent typo, not an "
    "unreported fourth arm")

# ── Yang 2020 ─────────────────────────────────────────────────────────────
add("Yang 2020", "Time to first defecation", "Postoperative", L, S, L, S, S,
    "D1: 'Group allocation was concealed using a sealed envelope containing the allocation "
    "sequence generated by SPSS in a 1:1 ratio'. "
    "D2 SOME CONCERNS: 'This study was a single-center, randomized and open-label trial' and "
    "'Participants and the acupuncture provider were not blind to the groups because of the "
    "specificity of EA treatment'; the comparator is usual care with no sham. "
    "D3: 2 of 59 randomised lost (1 excluded for absence of PVB, 1 withdrew before surgery), "
    "3.4%, with documented reasons. "
    "D4 SOME CONCERNS for THIS result: 'The assessors, anesthetists, and statisticians were "
    "unaware of study-group assignments' and times to defecation 'were checked regularly', which "
    "limits detection bias; but participants were unblinded and the event timing still depends "
    "in part on participant report. "
    "D5 SOME CONCERNS: registered ChiCTR1800014461 with time to first defecation among the "
    "stated primary outcomes; however this is explicitly a feasibility study in which 'The "
    "sample size of 60 was not determined by calculation but was the total number of patients we "
    "could recruit', and the between-group efficacy comparisons are nonetheless presented as "
    "findings.",
    "under-powered feasibility design reporting efficacy comparisons")

# ── Yang 2024 ─────────────────────────────────────────────────────────────
_yang24_common = (
    "D1: 'Patients were randomly assigned to either usual care (UC) or EA group by "
    "computer-generated codes and sequentially numbered, opaque envelopes'. "
    "D2 SOME CONCERNS: open-label against usual care — 'Given the characteristic of EA, the "
    "acupuncturist and patients were aware of the treatment allocation' — though 'anesthetists, "
    "assessors, the data collector as well as statisticians were blinded' and 'We conducted our "
    "analyses using the intention-to-treat principles'. "
    "D3 LOW: ITT with 90 per group; 3 documented withdrawals (declined further EA, no PVB, "
    "conversion to open surgery). "
    "D5 LOW: registered ChiCTR1900024840; 'Primary outcomes of this study were time to first "
    "flatus and first defecation' — both are the pre-specified co-primary outcomes.")
_yang24_d4 = (
    " D4 HIGH for THIS result: 'Times to first flatus and defecation measured in hours were "
    "recorded by the patients and then reported to our research assistant' — the timing is "
    "self-reported by participants who knew their allocation, and the authors concede that "
    "'Because sham EA was not used in this study, the inadvertent interaction between assessors "
    "and patient in the UC group may affect the results'. Blinding the downstream assessor does "
    "not remedy an unblinded self-report.")
add("Yang 2024", "Time to first defecation", "Postoperative", L, S, L, H, L,
    _yang24_common + _yang24_d4 +
    " Specific to defecation: the authors further note that 'time to first defecation might "
    "simply reflect rectal emptying and provide no reliable information on the recovery of "
    "whole gut', and participants without flatus by 72 h were instructed to use laxatives, a "
    "co-intervention that acts directly on the timing of this endpoint.")
add("Yang 2024", "Time to first flatus", "Postoperative", L, S, L, H, L,
    _yang24_common + _yang24_d4 +
    " Specific to flatus: this endpoint has no external corroboration at all — unlike "
    "defecation it leaves no observable trace for a nurse to confirm — and the authors "
    "acknowledge that 'time to first flatus is difficult to assess accurately'. The reported "
    "between-group difference is 1.6 h on a self-reported timing.")

# ── Zheng 2025 ────────────────────────────────────────────────────────────
_zheng_common = (
    "D1 SOME CONCERNS: allocation was by thresholding a seeded uniform random number — "
    "'A fixed seed number (eg, 12345) was preset to generate random numbers ranging between 0 "
    "and 1. Participants with a random number <=0.5 were assigned to the experimental group' — "
    "a method that cannot guarantee the stated 1:1 ratio, yet exactly 44 and 44 were allocated; "
    "the described method and the reported allocation are inconsistent. Concealment itself is "
    "adequate: 'concealed in sequentially numbered, opaque, sealed envelopes, which were opened "
    "only at the time of anesthesia induction'. "
    "D2 SOME CONCERNS: single-blind by design — 'the anesthesiologists were unblinded due to the "
    "nature of the intervention', which the authors list as a limitation ('the single-blind "
    "design may introduce performance bias'); participants and outcome assessors were blinded "
    "and a mITT analysis was used. "
    "D3 LOW: 3 of 88 excluded under pre-specified withdrawal criteria (2 procedure change, "
    "1 procedure exceeding 3 hours).")
add("Zheng 2025", "Time to first flatus", "Postoperative", S, S, L, S, L,
    _zheng_common + " D4 SOME CONCERNS for THIS result: participants and outcome assessors were "
    "blinded, which protects the measurement; but the report defines the endpoint incorrectly — "
    "'The time to first flatus was the time between the end of surgery and the first stools "
    "passed by the participants' — while separately tabulating time to first borborygmus, so "
    "what was actually measured under this label is uncertain. A second, independent reviewer "
    "confirmed on 2026-09-09 that this endpoint-identity problem cannot be resolved from the "
    "published report alone and recommended the review team decide, from the registry or by "
    "contacting the authors, whether this result should be held out of flatus-specific pooling "
    "pending clarification; that pooling decision is a team call, not one this pipeline makes "
    "unilaterally. "
    "D5 LOW: registered with the Chinese Clinical Trial Registry; 'time to first flatus' is "
    "explicitly named among the secondary outcomes.",
    "endpoint defined as 'first stools passed' under a flatus label; independently confirmed "
    "2026-09-09 as unresolved from the source alone")
add("Zheng 2025", "Total intraoperative remifentanil consumption", "Intraoperative", S, S, L, H, S,
    _zheng_common + " D4 HIGH for THIS result: intraoperative remifentanil is titrated and "
    "recorded by the anaesthesiologist, and the anaesthesiologists are precisely the personnel "
    "the report states were NOT blinded — the outcome is set by an unblinded clinician's own "
    "dosing decisions. The blinding of 'outcome assessors and data analysts' does not reach an "
    "intraoperative dose determined by the unblinded treating clinician. "
    "D5 SOME CONCERNS: the pre-specified primary outcome is PONV within 24 h and the named "
    "secondary outcomes are QoR-40, PSQI, NRS, PCIA usage, gastrointestinal function recovery, "
    "adverse events, time to first flatus and length of stay; intraoperative remifentanil "
    "consumption is not among them.",
    "result not among pre-specified outcomes; unblinded dose-setter is the outcome recorder")

# ── Zhou 2025 ─────────────────────────────────────────────────────────────
add("Zhou 2025", "Time to first flatus", "Postoperative", L, L, L, L, L,
    "D1: 'randomization into either the TEAS or Sham group at a 1:1 ratio, utilizing a "
    "computer-generated randomization sequence'; 'Allocation was concealed using sequentially "
    "numbered, sealed, opaque envelopes'. "
    "D2: 'single-center, randomized, double-blinded, sham-controlled trial'; 'Patients, "
    "anesthesiologists, surgeons, and data collectors remained blinded to group allocation'; the "
    "acupuncturist could not be blinded but 'adhered to a standardized interaction protocol for "
    "both groups', with 'scripted explanations, identical application of electrodes and device "
    "operation, and neutral responses to inquiries'. "
    "D3: 97 of 100 randomised completed (3%), 48/49 analysed. "
    "D4: participants were blinded by a credible sham and 'time to first flatus' was collected "
    "by blinded data collectors as one of the pre-defined recovery times. "
    "D5: registered ChiCTR2200055338 on 7 January 2022; QoR-15 is the primary outcome and time "
    "to first flatus is explicitly listed under the secondary 'Recovery times'.")

# ── Zhu 2022 ──────────────────────────────────────────────────────────────
_zhu_common = (
    "D1 SOME CONCERNS: the sequence was sound — 'randomly assigned to one of the following four "
    "groups using a computer-generated randomization sequence and secure code', 'printed and "
    "stored in sequentially numbered, opaque, sealed envelopes' — but the allocation step "
    "defeats it: 'Eligible participants chose one envelope, which was opened by the "
    "acupuncturist'. Letting the participant select an envelope from a set abandons the "
    "sequential order the concealment depends on. "
    "D2 SOME CONCERNS: assessor-blinded only, with a usual-care comparator and no sham, so "
    "participants and the acupuncturist were aware of allocation; 'All clinical outcome measures "
    "were conducted by a research nurse who was blinded to group allocation' and an ITT analysis "
    "is reported alongside the per-protocol one. "
    "D3 LOW: 13 of 413 (3.1%) excluded with documented reasons (3 lost to follow-up, 2 did not "
    "complete the intervention, 8 converted to open surgery); missing data handled by an "
    "expectation-maximization procedure. "
    "D4 LOW for THIS result: 'Neither the anesthetists/surgeons nor the assessors were aware of "
    "the group allocation', so the intraoperative opioid dose was set and recorded by blinded "
    "clinicians. "
    "D5 SOME CONCERNS: registered ChiCTR-INR-16010035 with a published protocol; 'The primary "
    "outcome measures were the incidence of PON and POV at 6-24 h after surgery, and pain on "
    "movement at 24 h', and the secondary outcomes are itemised — intraoperative remifentanil "
    "and sufentanil are not among either list and appear in Table 1 as anaesthetic "
    "characteristics.")
add("Zhu 2022", "Intraoperative remifentanil", "Intraoperative", S, S, L, L, S,
    _zhu_common + " Specific to remifentanil: it is the infused intraoperative opioid, "
    "titrated continuously by the blinded anaesthetist against depth of anaesthesia, so the "
    "recorded total reflects that clinician's titration over the whole case rather than a "
    "single discrete dosing decision.",
    "result not among pre-specified outcomes")
add("Zhu 2022", "Intraoperative sufentanil", "Intraoperative", S, S, L, L, S,
    _zhu_common + " Specific to sufentanil: it is given as bolus doses at induction and during "
    "maintenance, so the recorded total is a small number of discrete decisions by the blinded "
    "anaesthetist and is correspondingly more sensitive to case-mix than to the intervention. "
    "As with remifentanil, it is tabulated in Table 1 as an anaesthetic characteristic.",
    "result not among pre-specified outcomes")


# ── assemble against the worklist ─────────────────────────────────────────
def overall(*doms: str) -> str:
    if H in doms:
        return H
    if S in doms:
        return S
    return L


def main() -> int:
    with WORKLIST.open(encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["priority"].startswith("1")]

    pdf_map = json.loads((HERE / "pdf_map.json").read_text())
    out, missing = [], []
    for r in rows:
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
            adopted_date=(
                "2026-09-09" if r["study"] in ("Huang 2025", "Xing 2022", "Zheng 2025")
                else "2026-09-08"
            ),
            provenance_note=(
                (
                    "Adopted by the review lead's direction on 2026-09-08 and "
                    "re-confirmed on 2026-09-09 after a second, independent "
                    "reviewer re-read the mapped source PDF against this "
                    "study's pre-existing source-QC flag and reported back "
                    "findings, which this pipeline verified against its own "
                    "extracted data before updating the rationale above. "
                    "Domain judgements remain the source-evidence extraction; "
                    "standard Cochrane RoB 2 practice calls for two independent "
                    "assessors reconciling disagreement, and this second "
                    "reading is recorded as that reconciliation step."
                )
                if r["study"] in ("Huang 2025", "Xing 2022", "Zheng 2025")
                else (
                    "Adopted by the review lead's direction on 2026-09-08. Domain "
                    "judgements and rationale are the source-evidence extraction, "
                    "unchanged by adoption."
                )
            ),
        ))

    if missing:
        print("UNASSESSED priority-1 rows -- refusing to write a partial file:")
        for m in missing:
            print("   ", m)
        return 1
    if len(out) != len(rows):
        print(f"count mismatch: {len(out)} assessments for {len(rows)} rows")
        return 1

    p = HERE / "v34_rob2_draft_assessments.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    print(f"drafted {len(out)} result-specific assessments -> {p.relative_to(ROOT)}\n")
    for dom in ("d1_randomisation", "d2_deviations", "d3_missing",
                "d4_measurement", "d5_reporting", "overall"):
        c = Counter(r[dom] for r in out)
        print(f"  {dom:<18} " + "  ".join(f"{k}={v}" for k, v in
                                          sorted(c.items(), key=lambda x: -x[1])))
    print()
    for r in sorted(out, key=lambda r: ({H: 0, S: 1, L: 2}[r["overall"]], r["study"])):
        print(f"  {r['overall']:<14} {r['study']:<26} {r['outcome'][:42]:<42} @ {r['timepoint'][:18]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
