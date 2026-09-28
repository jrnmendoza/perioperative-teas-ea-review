# Reviewer and provenance wording update — 28 September 2026

On the review owner's instruction, the reviewer, sign-off, status and label wording in the RoB 2 and GRADE records (and the
files that copy them) was updated to record the delegated first assessment and the second review by SP on 28 September 2026.
Only the columns listed below changed. No RoB 2 domain or overall judgement, rationale, GRADE certainty, downgrade, source
quotation, result ID or model value changed; this was checked column by column when the files were rewritten. The previous
wording is in the git history of each file.

Hash records written before this date (`08_QOR_ANALYSIS/verification.json`, `07_OUTCOME_COVERAGE/baseline_hashes.json`,
`08_QOR_ANALYSIS/baseline_hashes.json`) describe the files as they were at those runs and are left unchanged as history.
`second_review.csv` carries the current hashes.

| File | Changed fields | SHA-256 before | SHA-256 after |
|---|---|---|---|
| `10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv` | human_signoff_date, provenance, reviewer | `78e4c368c72ba7a2…` | `dbf510bfc6196467…` |
| `10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_rob2.csv` | reviewer | `3af95f2b1072105a…` | `81c3df535b5634e9…` |
| `10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_rob2_later.csv` | reviewer | `50afbad2fe6233cb…` | `94fccec197e5b113…` |
| `10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_signalling_questions.csv` | reviewer | `cf7af7097f874e1a…` | `e90792b964b6d258…` |
| `10_FINAL_ADJUDICATION/03_CANONICAL/grade.csv` | label, reviewer | `372995393b3e7dea…` | `5bb173a343db6e34…` |
| `10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_grade.csv` | decision_status | `69bb2c79cbe575fd…` | `011adcec5382d349…` |
| `FINAL_RESULT_ROB2_LINKAGE.csv` | human_final_signoff, linkage_status, provenance | `6d6246b1d1479a67…` | `d3875e1fd792aa7a…` |
| `10_FINAL_ADJUDICATION/02_DECISIONS/v38/methodological_decisions.csv` | reviewer | `873847a2f84bd4a8…` | `c0930e11f5d76f89…` |
| `10_FINAL_ADJUDICATION/02_DECISIONS/v38/methodological_decisions.json` | reviewer / status string values | `46b2fa831ef43d73…` | `c26e3dabf6d9d004…` |
| `10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_summary.json` | reviewer / status string values | `315c51a366826b20…` | `43fa32676c9133c1…` |
| `FINAL_GRADE_RECOMMENDATIONS.md` | opening status sentence | `45a19664705eebb3…` | `2d731fa92e8d3f1f…` |

The generators (`code/adjudicate_v38.py`, `code/grade_v38.py`, `code/link_rob2.py`, `code/report_v38.py`) were updated to write
the same wording, so a rerun reproduces these files.
