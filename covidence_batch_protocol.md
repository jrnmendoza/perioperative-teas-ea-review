# Controlled Covidence Batch Extraction Protocol

## Authorized scope

- Review ID: `799962`.
- Target batch: the first 20 studies shown in Covidence's **Ready for extraction** queue at the moment the queue is frozen.
- Preserve that displayed order in `covidence_batch_20/manifest.md` before opening any target extraction form.
- Work only on those 20 frozen study IDs.
- Assignment of the signed-in Google/Covidence account as Reviewer 1 and creation of an in-progress draft are authorized for those targets.
- Populate saved draft extractions only. Never click **Complete** or submit an extraction.

## Non-negotiable safeguards

- Do not enable YOLO, automatic approval, persistent approval, or conversation-wide approval.
- Do not create or use an API key.
- Never modify the extraction template, review settings, quality-assessment template, study citation, tags, notes, PDFs, user assignments other than the authorized Reviewer 1 assignment caused by opening a target draft, consensus data, conflicts, or another review.
- Never accept or reject an automated Covidence suggestion merely because it exists. Verify it against the PDF first and record the evidence.
- Never infer a value. Use only information supported by the target study's full text, tables, figures, supplements available in Covidence, and the extraction form's instructions.
- If a field cannot be supported, use an allowed explicit status such as `not reported`, `unclear`, `not measured`, `measured-not-reported`, or `graph-only` only when the form permits it and the evidence justifies it.
- Never fabricate a page number, quotation, statistic, variance, group size, unit conversion, or intervention detail.
- Stop the affected study on login failure, CAPTCHA, inaccessible or mismatched PDF, companion-report ambiguity, duplicate-cohort ambiguity, unclear arm mapping, unresolved numeric inconsistency, or any required unsupported judgment. Continue with other frozen studies only if doing so cannot affect the blocked record.

## Required study-by-study workflow

Process one study at a time.

1. Confirm the Covidence study ID, citation, DOI/identifier, and PDF filename match the frozen manifest.
2. Inspect all seven extraction sections without changing values.
3. Read the complete PDF, including tables, figures, footnotes, appendices, and relevant supplements available in the record.
4. Create `covidence_batch_20/studies/<order>_<study-id>_evidence.md` containing:
   - citation and identifiers;
   - every proposed field value;
   - exact supporting quotation or table/figure cell description;
   - PDF page number and printed page number when different;
   - status of `supported`, `not reported`, `unclear`, `graph-only`, `measured-not-reported`, or `not measured`;
   - any calculation, conversion, formula, factor, source, and version;
   - all ambiguities and consistency checks.
5. Validate before browser entry:
   - randomized totals equal arm totals or explain the discrepancy;
   - analyzed totals and withdrawals are internally consistent;
   - arm names map unambiguously to the permitted intervention modalities;
   - outcome timepoints, activity condition, units, denominator, statistic type, and variance are explicit;
   - cumulative 24-hour outcomes are not confused with point estimates or shorter intervals;
   - opioid conversions are never performed without documenting the original drug, route, dose, conversion factor, source, and version;
   - values derived from figures are labeled `graph-derived` and not presented as directly reported;
   - adverse-event denominators and rescue-treatment definitions are retained.
6. Enter only validated values into the matching Covidence fields. Select intervention arms and outcomes only when supported by the PDF and required to render their corresponding result tables.
7. Allow Covidence autosave, but do not click **Complete**. Do not navigate away until the page visibly reports `Saved`.
8. Re-snapshot all seven sections and compare the saved draft against the evidence file.
9. Update `covidence_batch_20/manifest.md` with one of:
   - `draft_saved_verified`
   - `blocked_needs_human_review`
   - `already_completed_current_reviewer_no_action`
   - `not_started`
10. Record every unresolved issue. Never mark a blocked study as verified.

If the signed-in account already completed Reviewer 1 extraction for a frozen study, do not reopen, edit, overwrite, or act as Reviewer 2. Mark it `already_completed_current_reviewer_no_action` and inspect it only if a read-only verification is possible without entering comparison or consensus.

## Batch completion condition

The batch is finished only when all 20 frozen records are `draft_saved_verified`, `blocked_needs_human_review`, or `already_completed_current_reviewer_no_action`, and `covidence_batch_20/batch_report.md` lists:

- the frozen queue order and study IDs;
- per-study status;
- fields left blank or uncertain;
- calculations and conversions performed;
- any record that needs human review;
- confirmation that no extraction was completed/submitted.
