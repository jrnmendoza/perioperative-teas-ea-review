# Full-text review checkpoint — sequence 160

Timestamp: 2026-08-10T07:54:45+02:00

## Authoritative decision audit

- JSONL decision objects: 160
- Registered votes in JSONL: 160
- Screening sequences: exactly 1–160, consecutive
- Unique Covidence numbers: 160
- Missing page/section evidence: 0
- Exclusions without a definite primary reason and supporting evidence: 0
- Missing locally saved PDFs where `pdf_saved = yes`: 0
- Sequence 121 `full_text_identity_verified`: yes

## Live Covidence validation

- Screen references: 122
- Awaiting other reviewer: 160
- Resolve conflicts: 0
- Covidence #930 no longer appears in the vote-required queue after reload

## Derived files regenerated programmatically

- `codex_fulltext_decisions_200.csv`: 160 data rows
- `codex_fulltext_needs_human_review_200.csv`: 39 data rows; includes Covidence #83 and #137
- `codex_fulltext_companion_reports_200.csv`: 32 data rows
- `codex_fulltext_retrieval_summary_200.csv`: 123 data rows
- All four generated previews were rendered and visually checked.

## Retrieval incidents and quality control

- Valid retrieval-incident objects: 64
- Incident objects missing Covidence number, title, incident type, or timestamp: 0
- Covidence #851 remains unvoted and recorded as `FULL_TEXT_UNAVAILABLE`; its incident field was normalized to the authoritative `incident_type` schema at this checkpoint.
- Covidence #1299 quality-control incident remains recorded as `PRIOR_VOTE_REQUIRES_HUMAN_CORRECTION` with the complete participant-results article retrieved; the registered vote was not silently altered.

Checkpoint audit passed. Continue at `screening_sequence = 161` and stop after sequence 200; do not review or vote sequence 201.
