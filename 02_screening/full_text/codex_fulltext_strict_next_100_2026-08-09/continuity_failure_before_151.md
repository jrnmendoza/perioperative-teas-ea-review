# Continuity failure before strict full-text sequence 151

- Date: 2026-08-09
- Expected by batch protocol: 150 existing registered full-text decisions, consecutive sequences 1-150
- Local authoritative JSONL found: `../codex_fulltext_next_100_2026-08-09/codex_fulltext_decisions_150.jsonl`
- Local JSONL validation: 100 objects; sequences 1-100; 100 unique sequences; 100 unique Covidence numbers; 100 records with `vote_registered = yes`
- Covidence review ID: 799962
- Reviewer indicator: JM / JR Mendoza
- Stage: Full text review
- Covidence dashboard: 100 screened so far; 100 One Vote; 182 No Votes; 0 conflicts; 0 excluded
- Other reviewer decision visible: no
- Conflict page open: no

The required starting state of 150 registered decisions does not reconcile with either the local authoritative audit or Covidence. Per the protocol's continuity and stop rules, no report was reviewed or voted, sequence 151 was not assigned, and no decisions/audit CSVs for the proposed 151-250 batch were created.

Screenshot: `screenshots/continuity_failure_expected_150_actual_100.png`
