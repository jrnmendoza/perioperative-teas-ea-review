# Mandatory stop: wrong Covidence reason registered outside counted full-text queue

- Date: 2026-08-09
- Last authoritative registered full-text sequence: 100
- Covidence dashboard after stop: 100 screened; 182 full-text studies to screen; 100 One Vote; 0 conflicts
- Authoritative JSONL after reconciliation: 100 objects, consecutive sequences 1-100, 100 unique Covidence numbers, 90 INCLUDE and 10 EXCLUDE

## Trigger

While attempting to continue with Covidence #307 in a single-citation search view, the intended decision was EXCLUDE for definite ineligible timing: the full report states that the five-session EA course began on postoperative day 3 and continued through postoperative day 7.

Covidence instead recorded an `Excluded vote` with the reason `Wrong setting`. The History dialog visibly attributes that reason to JR Mendoza on 9 Aug 2026. This is a wrong registered reason and therefore a mandatory stop condition under the run instructions.

The Covidence review dashboard continued to show exactly 100 screened full-text studies, confirming that the single-citation search interactions after checkpoint 100 did not become counted full-text decisions. Provisional JSONL records 101-104 were removed from the authoritative ledger; sequence 101 remains unassigned.

Single-citation search interactions requiring human audit/correction in Covidence: #32, #238, #267 and #295 were toggled to Include in that view; #307 was toggled to Exclude with the wrong reason `Wrong setting`. No further citation was reviewed or voted after detecting the mismatch.

## Evidence

- `screenshots/fulltext_wrong_reason_105_history.png` — Covidence History showing #307 `Excluded vote — Wrong setting`
- `screenshots/fulltext_interrupted_dashboard_100.png` — review dashboard showing 100 screened / 182 to screen / 100 One Vote
- `screenshots/fulltext_interrupted_wrong_reason_105_counters.png` — full-text screen state captured immediately after the mismatch

Derived needs-human-review and companion-report CSVs were regenerated programmatically from the restored 100-object authoritative JSONL.
