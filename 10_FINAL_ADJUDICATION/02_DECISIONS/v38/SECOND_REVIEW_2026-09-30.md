# Second review recorded — 30 September 2026

On 30 September 2026 the review owner reported that SP had reviewed the second-review worksheet
(`second_review_worksheet.csv` as generated at `2b39655`: 888 items) and confirmed every item without changes, and had
also confirmed all RoB 2 signalling-question responses (core v38 2,068; QoR ~24 h 176; QoR later windows 110), which
were not on the worksheet. This record carries that report; no judgement, value, quotation or rationale changed.

What was recorded:

- `second_review` column set to `SP, 2026-09-30: confirmed` on every reviewed row of the baseline/protocol extraction
  (714) and of the narrative tables (92 recovery milestones, 50 harms rows with data, 28 satisfaction/acceptability rows).
  The 38 harms rows recording "no intervention-harm result located (not a zero)" were not on the worksheet; they stay
  `pending` and form the regenerated worksheet.
- `decision_status` of the four later-window QoR GRADE bodies: "second review pending" → "second review SP, 2026-09-30 (confirmed)".
- `reviewer` of the core signalling record: "Delegated assessor" → "Delegated assessor; second review SP, 2026-09-30 (confirmed)";
  `code/rob_signals_v38.py` writes the same wording. The QoR signalling files have no reviewer column and are pinned by hash only.
- Eight entries appended to `second_review.csv`, each with the reviewed file's current SHA-256 (the dashboard contract fails
  if a reviewed file changes afterwards, or if any row's review mark disagrees with its entry).

Only the named columns changed; every other column was asserted unchanged row by row when the files were rewritten.

| File | Rows marked | Changed column | SHA-256 before | SHA-256 after |
|---|---:|---|---|---|
| `10_FINAL_ADJUDICATION/14_CHARACTERISTICS/baseline_protocol_extraction.csv` | 714 | second_review | `4dfbb0cb6523c4c7…` | `0c5546b62ef9edf1…` |
| `10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES/recovery_milestones.csv` | 92 | second_review | `8312e2db7f6be43e…` | `b942c8ee90cf9ec4…` |
| `10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES/harms_structured.csv` | 50 | second_review | `70f5102d1aef5a68…` | `36afb3f39b4a74f9…` |
| `10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES/satisfaction_acceptability.csv` | 28 | second_review | `cd4c4273a826d3f6…` | `a5ce226a62457b60…` |
| `10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_grade_later.csv` | 4 | decision_status | `f7dd7d21401c0b9f…` | `354457b707544267…` |
| `10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_signalling_questions.csv` | 2068 | reviewer | `e90792b964b6d258…` | `d6359cad20b533f8…` |

`qor_grade_later.csv` was rewritten once more to restore its LF line endings; its final SHA-256 is `5532d1017e063b90…`, the value pinned in `second_review.csv`.

Generated outputs rebuilt from these records: `report_characteristics.csv` (877 values now "Verified (PDF quote, second reviewer)"),
`second_review_worksheet.csv` (38 items), `NARRATIVE_OUTCOMES_REPORT.md`, `FINAL_CURRENT_STATE_REPORT.md` and the dashboard payload.

## Deployment

| Item | Value |
|---|---|
| Pull request | [jrnmendoza/perioperative-teas-ea-review#57](https://github.com/jrnmendoza/perioperative-teas-ea-review/pull/57): check "Dashboard checks (no deploy)" passed; merged 30 September 2026 |
| Commit deployed | `becc943f02f3b54c1873f8fda7b0253807ddb4e8` (merge of PR #57; tree identical to `e63db09`) |
| Deployment branch | `claude-v26-dashboard-final` fast-forwarded `2b39655` → `becc943` |
| Pages run | 36757699659: build, deploy and verify jobs all succeeded |
| Live URL | <https://jrnmendoza.github.io/perioperative-teas-ea-review/> |
| Cache-busting URL | <https://jrnmendoza.github.io/perioperative-teas-ea-review/?build=becc943f> |
| Live `build-meta.json` | `git_commit` `becc943…`, built 2026-09-30T18:19:15Z, content fingerprint `aafb81f6f675` |
| Live verification | `scripts/verify_deployment.py --commit becc943…`: all live verification checks passed (79 downloads hash-match their sources; the live `second_review.csv` carries the 14 entries). `scripts/check_current_dashboard_ui.cjs` against the live URL: 19/19 browser checks passed. |
