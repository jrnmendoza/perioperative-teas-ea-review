# Locked calibration-round-2 screening rules — 23 July 2026

## Role and stopping rule

Codex acts only as an independent machine-assisted second reviewer. It is not the human primary reviewer, final eligibility decision-maker, conflict adjudicator, or full-text reviewer. Round 2 must stop after exactly 50 successfully registered title-and-abstract votes and must not reopen or alter round-1 decisions.

## Sensitive-screening rule

- Vote **Yes** when the title and abstract clearly or strongly support eligibility and show no definitive exclusion.
- Vote **Maybe** when eligibility is plausible but any important detail is unclear.
- Vote **No** only when the visible citation establishes a definitive exclusion that full text could not plausibly overturn.
- Missing information is not an exclusion unless the report is explicitly a protocol, methods/design paper, amendment, or registry record without participant outcome results.

## Core eligibility

- Adults aged 18 years or older undergoing operative surgery under general anaesthesia, alone or with balanced regional or neuraxial techniques.
- TEAS delivered through surface electrodes at recognized or explicitly defined body acupuncture points, or needle-based EA delivering electrical current through acupuncture needles at such points.
- At least one eligible stimulation session before the end of the first 24 postoperative hours.
- Randomized controlled trials, including eligible randomized companion or secondary results publications.
- Any clinically interpretable perioperative outcome; 0–24-hour opioid consumption is not required at title-and-abstract screening.
- No language restriction.

## Protocols without results

Study protocols, trial protocols, methods-only publications, protocol amendments, registry records without results, and design papers without participant outcome results receive **No — EXCLUDE_PROTOCOL_NO_RESULTS**. When visible, the trial name, registration number, or acronym is recorded in private notes for later linkage.

## Intervention separability and comparators

Normal balanced perioperative care is allowed. TEAS or EA must be the only systematically different therapeutic component in at least one independently extractable comparison.

Eligible comparisons include sham stimulation, usual care, no stimulation, attention control, and active non-acupoint electrical stimulation. Balanced co-interventions are allowed.

Use **EXCLUDE_INSEPARABLE_INTERVENTION** when several treatment components differ or the independent TEAS/EA effect cannot be isolated. Use **UNCERTAIN_INTERVENTION_SEPARABILITY** when the abstract does not establish whether co-interventions were identical.

Exclude head-to-head comparisons only against a pharmacological treatment, manual acupuncture, regional block, aromatherapy, rehabilitation, or another active non-electrical treatment without a common balanced background using **EXCLUDE_INELIGIBLE_ACTIVE_COMPARATOR**. Use **UNCERTAIN_COMPARATOR** when balance is unclear.

## Definitive exclusions

- Animal/veterinary, paediatric-only, non-surgical, chronic non-perioperative pain, or procedures explicitly performed without general anaesthesia.
- Manual, auricular, battlefield, press-tack, intradermal, wrist–ankle, buccal, dry/trigger-point/injection/laser acupuncture; moxibustion, cupping, acupressure alone; non-acupoint TENS/PENS; measurement, monitoring, or nerve-localization stimulation.
- Inseparable multimodal interventions, ineligible active comparators, or stimulation clearly initiated only after postoperative hour 24.
- Clearly non-randomized or quasi-randomized studies; reviews, editorials, commentaries, letters without original trial results, case reports/series; and protocols without results.
- Exclusively mechanistic, biomarker, imaging, or physiological outcomes without any eligible clinical perioperative outcome.

## Ambiguity codes

Use Maybe with the appropriate code for unclear general anaesthesia, randomization, intervention, intervention separability, comparator, timing, outcome, missing abstract, translation need, or possible companion-report status.

## Decision order

1. Actual participant results rather than a protocol?
2. Human operative surgical population?
3. Could general anaesthesia have been used?
4. Eligible TEAS or EA?
5. Independently separable TEAS or EA effect?
6. Eligible comparator?
7. Could allocation be randomized?
8. Clinical perioperative outcome present or plausible?
9. Stimulation delivered by postoperative hour 24?

Before every No vote, ask whether full-text information could plausibly overturn the exclusion. If yes, vote Maybe.

## Operational controls

- Read the complete visible title, abstract, publication type, and citation information.
- Write each private audit row before registering its Covidence vote.
- Register one vote at a time and verify acceptance before moving forward.
- Do not inspect history, another reviewer’s vote, conflicts, or full text.
- Do not search external databases, DOI pages, publisher sites, registries, or local PDFs.
- Do not import, export, delete, deduplicate, merge, tag, comment, or change review settings.
- After every 10 votes, reconcile Covidence counters, CSV rows, sequence continuity, current record, stage, and conflict status.
- Stop immediately for an uncertain vote, wrong click, citation/log mismatch, interface change, visible other-reviewer decision, repeated citation, or connection failure.
