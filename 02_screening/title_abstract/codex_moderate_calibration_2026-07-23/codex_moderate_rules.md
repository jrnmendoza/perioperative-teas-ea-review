# Locked moderately selective calibration rules — 23 July 2026

## Role and stopping rule

Codex acts only as an independent machine-assisted second reviewer. It is not the human primary reviewer, final eligibility decision-maker, conflict adjudicator, or full-text reviewer. Screening must stop after exactly 50 successfully registered votes and must not alter earlier decisions.

## Moderately selective decision rule

- Vote **Yes** when eligibility is clearly or strongly supported by the record as a whole.
- Vote **Maybe** only when one important unresolved issue creates a realistic, specific full-text scenario in which the study would be eligible.
- Vote **No** when an explicit exclusion is present or the complete title and abstract strongly indicate ineligibility.
- Do not use Maybe merely because every eligibility detail is not recited.
- Do not use No solely because reporting is incomplete.

## Core eligibility

- Adults undergoing operative surgery under general anaesthesia, including general anaesthesia combined with balanced regional or neuraxial techniques.
- TEAS delivered through surface electrodes at recognized or explicitly described acupuncture points, or EA delivered through inserted acupuncture needles at such points.
- At least one eligible treatment before the end of the first 24 postoperative hours.
- Randomized controlled trials, including eligible companion or secondary results reports.
- Clinically interpretable perioperative outcomes; 0–24-hour opioid consumption is not mandatory at this stage.
- No language restriction.

## General anaesthesia

Vote Yes or Maybe when general anaesthesia is explicit or highly plausible from the operation and methods. Use Maybe when the procedure could reasonably use general or non-general anaesthesia and this is the only major uncertainty. Vote No when non-general anaesthesia is explicit, strongly indicated, or general anaesthesia is unclear alongside another strongly unsupported core criterion.

## Protocols and non-results reports

Protocols, amendments, design/methods papers, trial registrations, and planned or ongoing trials without participant outcomes receive **No — EXCLUDE_PROTOCOL_NO_RESULTS**. Visible trial names, acronyms, and registration numbers are recorded privately for later linkage.

## Intervention, timing, and separability

Eligible TEAS and EA must meet the body-acupoint definitions. Exclude manual, auricular, press-needle, intradermal, wrist–ankle, laser, dry-needling, moxibustion, cupping, non-acupoint TENS, and measurement/monitoring stimulation.

At least one session must occur by postoperative hour 24. Treatment beginning days or weeks later, rehabilitation-only treatment, and chronic postoperative treatment are excluded with **EXCLUDE_TIMING**.

Normal balanced perioperative care is allowed, but the independent TEAS/EA effect must be estimable. Explicitly unequal multimodal packages receive **EXCLUDE_INSEPARABLE_INTERVENTION**. Use **UNCERTAIN_INTERVENTION_SEPARABILITY** only when a plausible balanced or extractable comparison may exist.

Eligible comparators include sham, inactive/minimal stimulation, usual care, no stimulation, attention control, and active non-acupoint electrical stimulation analyzed separately. Head-to-head comparison only against an unbalanced medication or active non-electrical treatment receives **EXCLUDE_INELIGIBLE_ACTIVE_COMPARATOR**.

## Study design and outcomes

Eligible randomized parallel, cluster, and interpretable crossover trials are retained. Explicitly or strongly observational, retrospective, uncontrolled, single-arm, quasi-randomized, case, review, editorial, commentary, and protocol records are excluded using the direct primary reason.

Randomization must be stated or realistically supported; “prospective” or “clinical trial” alone is insufficient.

Eligible outcomes include opioid use, pain, rescue analgesia, PONV, recovery quality, delirium/cognition, gastrointestinal recovery, mobilization/function, stay, satisfaction, complications, and adverse events. Exclusively mechanistic, biomarker, imaging, physiological, or anaesthetic-depth outcomes receive **EXCLUDE_NO_ELIGIBLE_OUTCOME**.

## Missing abstracts, language, and companion reports

A missing abstract does not automatically require Maybe. Use the title and citation information to decide. Do not exclude solely because of language. Retain realistically plausible companion, secondary, conference, or follow-up reports using **POSSIBLE_COMPANION_REPORT** where appropriate.

## Decision hierarchy

1. Results publication or protocol?
2. Human operative surgical population?
3. General anaesthesia eligible or reasonably plausible?
4. Eligible TEAS or EA?
5. Eligible timing?
6. Independently separable effect?
7. Eligible comparator?
8. Randomized design supported or plausible?
9. Eligible clinical outcome present or plausible?

Stop after one sufficiently strong exclusion reason.

## Operational controls

- Read the full visible title, abstract, publication type, and citation information.
- Base decisions on the whole record, not highlights or Covidence’s RCT label.
- Write the private audit row before registering its vote.
- Register one vote at a time and verify acceptance.
- Do not search external databases, DOI pages, registries, publisher sites, or local PDFs.
- Do not inspect history, another reviewer’s decision, conflicts, or full text.
- Do not import, export, delete, merge, tag, comment, or change review settings.
- After each 10 votes, reconcile the queue, CSV rows, sequence, stage, and conflict status.
- Stop immediately for an uncertain registration, wrong click, citation/log mismatch, visible other-reviewer decision, uncertain navigation, or network/interface failure.
