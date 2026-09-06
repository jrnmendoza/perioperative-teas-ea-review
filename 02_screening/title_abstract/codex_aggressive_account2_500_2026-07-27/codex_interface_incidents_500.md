# Interface incidents

## 2026-07-27 — interruption after sequence 104

- Citation acted on: Covidence #133 — Clinical Study on the Application of Acupuncture in the Postoperative Rehabilitation of Dogs Affected by Acute Thoracolumbar Disc Herniation.
- Intended decision: No (`EXCLUDE_ANIMAL`).
- Incident: the browser reported an interaction timeout during the vote workflow.
- Repeat click: no.
- Registration check: the citation left the active queue, Covidence #134 became the first displayed citation, sequence 104 was appended after the registered vote, and the refreshed Screen references count reconciled to 2837.
- Unregistered attempted records: 0.
- Action: screening stopped under the mandatory browser-failure stop condition.

## 2026-07-27 — resume interruption after sequence 105

- Citation acted on: Covidence #134 — Electroacupuncture in the treatment of gastrointestinal dysfunction after laparoscopic nephrectomy: a retrospective analysis.
- Intended decision: No (`EXCLUDE_NON_RANDOMIZED`).
- Incident: the immediate post-click verification did not yet observe the citation leaving the active queue.
- Repeat click: no.
- Registration check: read-only follow-up showed #134 absent and #135 first; after refresh, Screen references decreased from 2837 to 2836.
- Audit action: sequence 105 was appended only after registration was confirmed; JSONL and CSV validation passed at 105 records.
- Unregistered attempted records: 0.
- Action: screening stopped under the interaction-integrity stop rule.

## 2026-07-27 — requested metadata correction

- Target: Covidence #3, screening sequence 2.
- Field corrected: `actual_results_reported` from `yes` to `no`.
- Registered Covidence vote changed: no.
- Decision and reason code remain: No — `EXCLUDE_PROTOCOL_NO_RESULTS`.
- CSV and numbering-gap files regenerated from the validated JSONL.

## 2026-07-27 — delayed transition after sequence 141

- Citation acted on: Covidence #185.
- Intended decision: No (`EXCLUDE_WRONG_INTERVENTION`).
- Incident: the browser operation timed out after the single vote click.
- Repeat click: no.
- Registration check: read-only reconciliation showed #185 had left the active queue, its Undo state was present, and #186 was current.
- Audit action: sequence 141 was appended only after registration was confirmed and was marked `delayed_transition_confirmed`.

## 2026-07-27 — local audit correction after sequence 168

- Citation acted on: Covidence #220.
- Intended decision: Maybe (`UNCERTAIN_GENERAL_ANAESTHESIA`).
- Browser registration: confirmed after one click; #220 left the active queue.
- Repeat click: no.
- Incident: the first local append failed because two uncertainty labels violated the one-primary-uncertainty rule.
- Audit action: metadata was corrected to the single primary uncertainty, general anaesthesia, and sequence 168 was appended without another browser interaction.

## 2026-07-27 — completion reconciliation

- Final registered votes: 500.
- Unregistered attempted records: 0.
- Final active unscreened citation: Covidence #630.
- Sequence 501 attempted: no.
- Live queue after refresh: 2441, matching 2941 − 500.
- Unresolved browser interaction failures: none.
