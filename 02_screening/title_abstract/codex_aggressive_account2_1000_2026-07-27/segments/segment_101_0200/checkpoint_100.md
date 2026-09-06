# Segment 2 completion checkpoint with decision-error stop

- Completion timestamp: 2026-07-27T09:52:29Z
- Global sequences: 101–200
- Segment sequences: 1–100
- First Covidence number: 741
- Last Covidence number: 843
- Registered votes: 100
- Segment decisions: 14 Yes, 4 Maybe, 82 No
- Combined decisions: 42 Yes, 9 Maybe, 149 No
- Combined registered votes: 200
- Unique Covidence numbers: 200
- Unique timestamps: 200
- Maybe structural validation: passed
- Numbering gaps logged: 14
- JSONL validation: passed
- CSV validation: passed
- Checkpoint screenshot: `screenshots/covidence_checkpoint_0200.png`
- Other reviewer decisions viewed: no
- Conflicts opened or resolved: no

## Required stop

- Sequence 197, Covidence #840, was registered as `MAYBE`.
- The abstract explicitly reports routine sedation and local anaesthesia.
- The decision should have been `NO — EXCLUDE_NO_GENERAL_ANAESTHESIA`.
- The registered vote and append-only audit row were not altered.
- The discrepancy was recorded in the incident ledger.
- Screening stopped before sequence 201.
