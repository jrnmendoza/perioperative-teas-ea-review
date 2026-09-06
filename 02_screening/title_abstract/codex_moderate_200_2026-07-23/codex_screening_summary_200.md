# Codex moderate 200-record screening batch

## Continuity

- Date: 23 July 2026
- Review: Covidence 799962
- Stage: Title and abstract screening
- Reviewer profile: John Ryan Nual Mendoza
- Dual-reviewer behavior: active
- Sort: Covidence ID ascending
- Last successfully registered prior record: Covidence number 268
- First displayed unscreened record: Covidence number 269
- Initial queue: 3,092 Screen; 200 Awaiting other reviewer; 0 Resolve conflicts
- Target: exactly 200 successfully registered votes
- Continuity established: yes

## Checkpoint plan

- Internal quality control every 25 registered votes.
- Formal checkpoint summaries and screenshots at 50, 100, 150, and 200 votes.
- No human approval pause at checkpoints 50–150 when checks pass.

## Interrupted after the 25-vote quality-control check

- Successfully registered votes: 25
- First and last registered Covidence numbers: 269 and 300
- Decisions: 6 Yes; 4 Maybe; 15 No
- Decision rows with `vote_registered_yes_no = yes`: 25
- Unique Covidence numbers: 25
- Unique screening-sequence values: 25
- Unique valid post-vote timestamps: 25
- Numbering gaps logged: 5
- Queue after reload: 3,067 Screen; 225 Awaiting other reviewer; 0 Resolve conflicts
- Next displayed citation: Covidence number 301
- Vote registered for Covidence number 301: no
- Attempted citations without a registered vote: 0
- Browser-interface incidents: 0
- Conflicts opened or resolved: none
- Formal 50-vote checkpoint reached: no

The initial local CSV check found one surplus `not_applicable` field in each of two protocol rows, which shifted their registration fields. No Covidence vote was uncertain or missing. The two rows were corrected using the already captured unique timestamps, and the repeated check passed with 25 valid rows, 25 registered votes, 25 unique IDs, 25 unique timestamps, no malformed rows, and no gap rows lacking timestamps. Screening was nevertheless stopped at this quality-control boundary as required after detecting the data-integrity failure.

## Resumption point

Resume with Covidence number 301. Do not repeat or alter the 25 votes already registered in this batch.

## Combined checkpoint 050

- Successfully registered votes in combined batch: 50
- Votes added during resumption: 25
- Resumption screening sequences: 26–50
- Resumption Covidence-number span: 301–331
- Combined decisions: 12 Yes; 8 Maybe; 30 No
- Valid decision rows: 50
- Unique Covidence numbers: 50
- Unique screening-sequence values: 50
- Unique post-vote timestamps: 50
- Malformed, shifted, duplicated, incomplete, or pending rows: 0
- Numbering gaps logged: 10
- Gap rows lacking timestamps: 0
- Queue after reopening the Screen references view: 3,042 Screen; 250 Awaiting other reviewer; 0 Resolve conflicts
- Next displayed citation: Covidence number 332
- Conflicts opened or resolved: none

The first refresh attempt left cached sidebar totals visible. Reopening the Screen references view
updated the totals to the expected 25-vote change and confirmed continuity.

## Internal quality-control boundary 075

- Successfully registered votes in combined batch: 75
- Votes added during resumption: 50
- Valid decision rows: 75
- Unique Covidence numbers, sequences, and post-vote timestamps: 75 each
- Malformed, shifted, duplicated, incomplete, or pending rows: 0
- Numbering gaps logged: 18
- Gap rows lacking timestamps: 0
- Queue after reopening the Screen references view: 3,017 Screen; 275 Awaiting other reviewer; 0 Resolve conflicts
- Next displayed citation: Covidence number 367
- Conflicts opened or resolved: none

## Combined checkpoint 100

- Successfully registered votes in combined batch: 100
- Votes added during resumption: 75
- Resumption screening sequences: 26–100
- Resumption Covidence-number span: 301–400
- Combined decisions: 24 Yes; 15 Maybe; 61 No
- Valid decision rows: 100
- Unique Covidence numbers: 100
- Unique screening-sequence values: 100
- Unique post-vote timestamps: 100
- Malformed, shifted, duplicated, incomplete, or pending rows: 0
- Numbering gaps logged: 25
- Gap rows lacking timestamps: 0
- Queue after reopening the Screen references view: 2,992 Screen; 300 Awaiting other reviewer; 0 Resolve conflicts
- Next displayed citation: Covidence number 401
- Conflicts opened or resolved: none
- Screenshot: `screenshots/covidence_checkpoint_100.png`
