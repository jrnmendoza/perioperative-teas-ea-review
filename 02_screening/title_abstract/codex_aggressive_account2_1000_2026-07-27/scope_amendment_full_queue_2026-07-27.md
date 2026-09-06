# Screening scope amendment: complete current queue

- Date: 2026-07-27
- Reviewer account: JR Mendoza
- Review ID: 799962
- Original batch target: 1,000 newly registered title-and-abstract votes.
- User amendment: continue through all 1,941 references shown as remaining at the sequence-500 checkpoint.
- Effect on endpoint: the batch now targets the full starting queue of 2,441 newly registered votes, subject to reconciliation if Covidence rehydrates or changes the active queue.
- Amendment received after sequence 550 had been completed.
- Registered and audited at amendment: 550.
- Expected remaining after sequence 550: 1,891.
- Next screening sequence: 551.
- First displayed active citation: Covidence #1314.

The existing append-only audit files retain their original `1000` filenames for continuity. No prior decision or audit row is overwritten by this amendment.

## Count-reconciliation addendum

- At the formal sequence-600 reload, Covidence still displayed 1,941 Screen references even though 50 votes had been registered since the user expanded the endpoint after sequence 550.
- The earlier arithmetic target of 2,441 is therefore superseded.
- The nominal expanded target is 2,491 registered votes (550 already completed plus the 1,941 references the user instructed the reviewer to finish).
- The controlling completion condition is an empty active screening queue, not the nominal arithmetic target, because the displayed header count did not decrement at sequence 600.
- This discrepancy is retained for reconciliation at later checkpoints; no vote was repeated or altered.

## Queue-rehydration resolution

- During the first post-reload transition, the active queue finished rehydrating and the header displayed 1,841 Screen references after 600 registered votes.
- This exactly matches the original starting queue of 2,441 minus 600 completed votes.
- The transient 1,941 display during reload was stale and is not the controlling count.
- The nominal full-queue target is therefore restored to 2,441 registered votes, while an empty active screening queue remains the controlling completion condition.
- At the sequence-675 checkpoint, the arithmetic remaining count is 1,766; the live header was not reloaded at this checkpoint to avoid another rehydration transition.
