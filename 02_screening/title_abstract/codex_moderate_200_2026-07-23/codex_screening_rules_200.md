# Locked screening rules — moderate 200-record batch

- Screen independently as the machine-assisted second reviewer.
- Register exactly 200 votes, then stop before record 201.
- Work only in Covidence review 799962, Title and abstract screening, under the designated machine-assisted reviewer account.
- Maintain Covidence ID ascending order and process one record at a time.
- Before every click, write an audit row with `vote_registered_yes_no = no`; after confirmed removal of that citation card, update it to `yes` with the unique actual timestamp.
- Use a moderately selective threshold: Yes when eligibility is strongly supported, Maybe for one specific realistic eligibility uncertainty, and No for explicit or strongly supported ineligibility.
- Apply decision order: publication type; human operative population; general anaesthesia; eligible TEAS or needle EA; timing at or before 24 postoperative hours; intervention separability; comparator; randomized design; clinical outcome.
- Exclude protocols and non-results publications, non-human or paediatric-only studies, non-operative procedures, non-general anaesthesia, wrong electrical interventions, late treatment, inseparable bundles, isolated ineligible active comparators, and non-randomized designs.
- Treat treatment described only as postoperative day 1 as `UNCERTAIN_TIMING` unless an exact start at or before 24 hours is available.
- Retain eligible surrogate-focused trials as Maybe when clinical outcomes or adverse events remain plausible; exclude only clearly exclusive mechanistic records.
- Do not inspect history or another reviewer’s decision, resolve conflicts, enter full text, change settings, tag/comment, import/export, merge, or delete.
- Log stable unexplained Covidence-number gaps as `UNEXPLAINED_NUMBERING_GAP`; stop only for a visible bypass, repeated citation, count mismatch, order change, or unreconciled interface behavior.
- Run quality control every 25 votes and formal checkpoints at 50, 100, 150, and 200.
- Stop immediately for authentication, CAPTCHA/MFA, selector ambiguity, uncertain registration, wrong click, queue instability, conflict exposure, network failure, or unsafe audit persistence.
