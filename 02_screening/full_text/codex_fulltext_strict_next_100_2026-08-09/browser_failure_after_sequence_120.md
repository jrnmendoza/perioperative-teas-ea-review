# Browser failure after sequence 120

- Timestamp: 2026-08-09T19:59:17+02:00
- Authoritative decision count: 120.
- Last successfully registered decision: screening sequence 120, Covidence #860, INCLUDE.
- The lightweight sequence-120 audit passed after correcting sequence 105's source-type vocabulary from `complete_repository_html` to the allowed equivalent `complete_pmc_html`; no eligibility evidence or vote changed.
- Audit results: 120 JSONL objects; sequences 1–120 consecutive; 120 unique Covidence numbers; all votes registered; all sequences 101–120 have approved complete-full-text source types, verified identity and evidence; zero abstract-only or registry-only votes.
- Last confirmed live Covidence state before the failure: review 799962, vote-required queue, Resolve conflicts 0, Awaiting other reviewer 113, Screen references 169; Covidence #860 had left the active queue.
- Chrome became unavailable during a read-only attempt to locate Covidence #2409. No Covidence action was in progress and no Include, Exclude or exclusion-reason control was clicked.
- Covidence #2409 was fully read in complete PMC HTML (PMCID PMC9659983) and identity-verified. The report is a randomized crossover beverage-ingestion experiment in healthy volunteers and positively establishes no operative surgery. It is prepared as `EXCLUDE_NON_SURGICAL`, but remains unvoted and has no screening sequence.
- Resume only after reconnecting Chrome, reconciling the live queue/conflict state, and confirming #2409 is still unvoted. The next successfully registered decision must be sequence 121.
