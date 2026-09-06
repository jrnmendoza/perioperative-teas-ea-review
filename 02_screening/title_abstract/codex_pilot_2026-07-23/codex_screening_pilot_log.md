# Codex title-and-abstract screening calibration pilot

## Session controls

- Date: 23 July 2026
- Role: machine-assisted second reviewer
- Pilot limit: exactly 50 successfully registered votes
- Review ID: Covidence 799962
- Review title displayed: *Protocol characteristics associated with clinically meaningful 24-hour opioid sparing from perioperative transcutaneous electrical acupoint stimulation and electroacupuncture: a systematic review*
- Reviewer account displayed: John Ryan Nual Mendoza (JM)
- Stage: Title and abstract screening
- Initial Screen references count: 3,292
- Initial Resolve conflicts count: 0
- Initial Awaiting other reviewer count: 0
- Initial Irrelevant references count: 0
- Sort: Covidence ID
- Display: 50 studies
- First unscreened Covidence number: 2
- External searching: prohibited and not performed
- Team-visible tags/comments: prohibited and not used
- History inspection: prohibited and not used
- Conflict resolution: prohibited and not used

## Block audit

Block-level quality-control entries will be appended after each 10 successfully registered votes.

### Block 1 — votes 1–10

- Successfully registered: 10
- Screen references after reload: 3,282 (expected 3,282)
- Awaiting other reviewer: 10
- Resolve conflicts: 0
- Stage and queue: Title and abstract screening; Screen references
- Local decision rows: 10
- Interface note: the header counter did not refresh dynamically after the first vote. Registration was confirmed by removal of the voted record from the queue and a reload showing the expected server-backed count. Subsequent block checks use a reload before reading counters.

### Block 2 — votes 11–20

- Successfully registered: 20 cumulative
- Screen references after reload: 3,272 (expected 3,272)
- Awaiting other reviewer: 20
- Resolve conflicts: 0
- Stage and queue: Title and abstract screening; Screen references
- Local decision rows: 20 cumulative

### Block 3 — votes 21–30

- Successfully registered: 30 cumulative
- Screen references after reload: 3,262 (expected 3,262)
- Awaiting other reviewer: 30
- Resolve conflicts: 0
- Stage and queue: Title and abstract screening; Screen references
- Local decision rows: 30 cumulative

### Block 4 — votes 31–40

- Successfully registered: 40 cumulative
- Screen references after reload: 3,252 (expected 3,252)
- Awaiting other reviewer: 40
- Resolve conflicts: 0
- Stage and queue: Title and abstract screening; Screen references
- Local decision rows: 40 cumulative

### Block 5 — votes 41–50

- Successfully registered: 50 cumulative
- Screen references after reload: 3,242 (expected 3,242)
- Awaiting other reviewer: 50
- Resolve conflicts: 0
- Stage and queue: Title and abstract screening; Screen references
- Local decision rows: 50 cumulative
- Last screened Covidence number: 68
- First untouched reference now displayed: Covidence number 69
- Stopping rule: satisfied; no 51st vote cast

## Pilot summary

- Total votes: 50
- Yes: 8
- Maybe: 5
- No: 37
- Initial Screen references: 3,292
- Final Screen references: 3,242
- Net decrease: 50
- Final Awaiting other reviewer: 50
- Final Resolve conflicts: 0
- External searching performed: no
- Tags/comments added: no
- History opened: no
- Conflict resolution opened: no
- Full-text screening opened: no

## Interface and file verification

- Interface issue: Covidence’s Screen references counter did not refresh dynamically after the first vote. A page reload showed 3,291 and the next record in sequence, confirming that the vote was registered.
- Automation issue: transient selector timeouts occurred while the reloaded page was still settling and while using a brittle card-class selector. No unverified vote was added to the local log. Screening continued only after the queue and server-backed counts were reconciled; subsequent voting used exact accessible headings and vote buttons.
- Duplicate or missing vote evidence: none. The final queue decrease (50) and Awaiting other reviewer count (50) both match the 50 local decision rows.
- Decision CSV validation: 50 consecutive sequences; first Covidence number 2; last Covidence number 68; no blank decision fields.
- Before screenshot: `screenshots/covidence_before_pilot.png`
- After screenshot: `screenshots/covidence_after_pilot.png`
- Screenshot visual check: before shows Screen references 3,292 and first record 2; after shows Screen references 3,242, Awaiting other reviewer 50, conflicts 0, and first untouched record 69.
