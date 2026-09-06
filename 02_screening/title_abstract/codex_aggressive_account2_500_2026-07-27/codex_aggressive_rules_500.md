# Aggressive account-2 title-and-abstract screening rules

- Date: 2026-07-27
- Target: exactly 500 successfully registered votes
- Queue: the account's own `Screen references` queue, sorted by Covidence ID
- Blinding: do not view or infer another reviewer's decisions, history, conflicts, comments, or tags

## Core eligibility criteria

1. Primary participant-results publication.
2. Adult human operative surgical population.
3. General anaesthesia.
4. Therapeutic TEAS or needle-based electroacupuncture at recognized or explicitly defined acupuncture points.
5. At least one eligible treatment session begins at or before 24 postoperative hours.
6. Eligible intervention effect is separable.
7. Eligible comparator.
8. Randomized design.
9. Eligible clinical perioperative outcome.

## Decision threshold

- `YES`: all or nearly all core criteria are clearly or strongly supported.
- `MAYBE`: exactly one essential criterion is genuinely uncertain, all others are supported, and a realistic eligible full-text scenario remains.
- `NO`: any explicit exclusion; two or more essential criteria are uncertain or absent; one criterion is strongly inconsistent; or no realistic eligibility basis exists.

Missing abstracts do not automatically justify `MAYBE`. General anaesthesia must be supported. Ambiguous allocation wording does not establish randomization. Surrogate-only studies require a realistic indication that a clinical perioperative outcome was collected.

## Primary exclusion codes

- `EXCLUDE_PROTOCOL_NO_RESULTS`
- `EXCLUDE_PUBLICATION_TYPE`
- `EXCLUDE_TRIAL_REGISTRATION`
- `EXCLUDE_ANIMAL`
- `EXCLUDE_POPULATION`
- `EXCLUDE_NON_SURGICAL`
- `EXCLUDE_NO_GENERAL_ANAESTHESIA`
- `EXCLUDE_WRONG_INTERVENTION`
- `EXCLUDE_NON_ACUPOINT_TENS`
- `EXCLUDE_TIMING`
- `EXCLUDE_INSEPARABLE_INTERVENTION`
- `EXCLUDE_INELIGIBLE_ACTIVE_COMPARATOR`
- `EXCLUDE_NON_RANDOMIZED`
- `EXCLUDE_NO_ELIGIBLE_OUTCOME`
- `EXCLUDE_MISSING_ABSTRACT`

## Quality controls

- Screen one citation at a time.
- Append one JSON object only after a vote is visibly registered and the citation leaves the active queue.
- Validate JSONL and regenerate CSV every 25 registered votes.
- Write checkpoints every 50 registered votes.
- Stop immediately on any unreconciled vote, record, queue, order, duplicate, conflict, browser, network, or audit inconsistency.
