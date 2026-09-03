# Project initialization log

Append-only. Do not edit or delete prior entries; add a dated correction if an entry later proves incomplete or wrong.

## 2026-07-21T20:19:31+0200 - INIT-001 - Repository boundary

- Repository: `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026`
- Initialized as a new review repository; pre-existing content was Git metadata only.
- Previous broad review inspected read-only: `/Users/ryan/Documents/Perioperative_Acupuncture_Review_2026_Pro`.
- No previous raw search export was copied, renamed, overwritten, or reused.

## 2026-07-21T20:19:31+0200 - INIT-002 - Protocol source provenance

- Original path: `/Users/ryan/Documents/Perioperative_Acupuncture_Review_2026_Pro/00_protocol/PROSPERO/submitted_record/PROSPERO TEAS EA.pdf`
- Original filename: `PROSPERO TEAS EA.pdf`
- Original file size: 128505 bytes
- Original filesystem modification date: `2026-07-21T20:09:59+0200`
- Original SHA-256: `aca44f5fd8f1923e6e0e8f34febd8ea90cb919f6ffc1cd3498f98336ab885ca9`
- Repository copy: `00_protocol/source/PROSPERO TEAS EA.pdf`
- Copy method: metadata-preserving file copy (`cp -p`)
- Copy file size: 128505 bytes
- Copy filesystem modification date: `2026-07-21T20:09:59+0200`
- Copy SHA-256: `aca44f5fd8f1923e6e0e8f34febd8ea90cb919f6ffc1cd3498f98336ab885ca9`
- Integrity result: PASS; byte identity demonstrated by matching SHA-256.

## 2026-07-21T20:19:31+0200 - INIT-003 - Protocol inspection

- PDF metadata: 10 pages, A4, unencrypted, PDF 1.4.
- Text was extracted with `pypdf` and the eligibility/search sections were checked against rendered page images.
- Locked operational summary created at `00_protocol/protocol_scope_locked.md`.

## 2026-07-21T20:19:31+0200 - INIT-004 - PubMed tooling and credential presence

- Entrez Direct command found at `/Users/ryan/edirect/esearch`.
- `NCBI_API_KEY` environment status: available.
- The key value was not printed, logged, or written to the repository.
- Planned execution is count-only plus targeted known-report intersection testing; no full result retrieval.

## 2026-07-21T20:27:00+0200 - RUN-001 - PubMed v0.1 execution-method failure

- Attempt: three count-only ESearch calls and one targeted sentinel-intersection call using `run_pubmed_pilot_test.py`.
- Result: stopped on the first call with HTTP 414 (request URI too long); no PubMed count or recall result was produced.
- Interpretation: transport failure caused by using HTTP GET for a long query, not a query-syntax failure or sentinel miss.
- Action: changed the script to HTTP POST; strategy v0.1 text was not changed.

## 2026-07-21T20:26:27+0200 - COR-001 - RUN-001 timestamp correction

- The timestamp in the RUN-001 heading was entered prospectively/approximately and is later than the successful run that followed; it must not be used for event ordering.
- Correct ordering: GET-based HTTP 414 failure occurred first; HTTP POST method change occurred second; successful count/recall execution at `2026-07-21T20:25:37+02:00` occurred third.
- The original entry is retained because this audit is append-only.

## 2026-07-21T20:25:37+0200 - RUN-002 - PubMed v0.1 pilot count and sentinel recall

- Execution: NCBI ESearch by HTTP POST using `run_pubmed_pilot_test.py`.
- Credential handling: `NCBI_API_KEY` was available and used without exposing or storing its value.
- TEAS line count: 661.
- EA line count: 858.
- Combined unique PubMed count: 1170.
- PubMed-indexed sentinel recall: 24/25 (96%).
- TEAS sentinel recall: 22/22.
- EA sentinel recall: 2/3.
- Missed PMID: 29391879.
- Full result retrieval: not performed.
- PubMed syntax errors: none.
- PubMed warnings: four quoted phrases not found; documented in `01_search_strategy/pubmed/pubmed_v0_1_explanation.md`.
- Disposition: acceptable pilot for PRESS-style review; not a formal search and not approved for full retrieval.

## 2026-07-21T20:26:27+0200 - QA-001 - Repository validation

- Required repository directories and files: PASS.
- Source protocol size and SHA-256: PASS.
- Known-report CSV parse and row count: PASS (26 rows; 25 in PubMed recall denominator).
- Sentinel-recall CSV parse and row count: PASS (26 rows).
- Transport strategy equals whitespace-normalized multiline strategy: PASS.
- Complete PubMed result export present: no.
- Deduplication performed: no.
- Screening performed: no.
- Full-text download performed for this review: no.
- PDF-render QA intermediates were moved out of the repository to `/tmp/Perioperative_TEAS_EA_Review_2026_pdf_qa_20260721`.

## 2026-07-21T21:08:16+0200 - RUN-003 - User-requested PubMed v0.2 Covidence export

- Authorization: user explicitly requested a RIS file for Covidence following the narrowing diagnostic.
- Strategy change: removed only `operation*[tiab]`; preserved exact v0.1 and saved exact v0.2 multiline/transport files.
- PubMed results retrieved: 1,009.
- Raw ESearch and EFetch XML preserved under `02_search_exports/raw/pubmed/2026-07-21_v0_2/`.
- Covidence-ready RIS created under `02_search_exports/derived/pubmed/2026-07-21_v0_2/`.
- Complete manifest: `02_search_exports/manifests/PubMed_TEAS_EA_v0_2_2026-07-21_manifest.json`.
- Import into Covidence: not performed.

## 2026-07-22T18:52:03+0200 - RUN-004 - CENTRAL Search Manager execution and Covidence RIS export

- Authorization: user explicitly requested the CENTRAL RIS file and approved bypassing the unavailable personal-search save.
- Platform: Cochrane Library through Lund University Libraries institutional access.
- Search Manager strategy: 16 lines entered and counted individually on 2026-07-21.
- Final counts: #14 EA 1,109; #15 TEAS 1,038; #16 combined 1,706.
- Content breakdown: 1,698 CENTRAL Trials and 8 Cochrane Reviews.
- Export: all 1,698 CENTRAL Trials in RIS (EndNote) format with abstracts; reviews excluded.
- RIS QA: 1,698 `TY` records, 1,698 `ER` terminators, and 1,698 CENTRAL accession numbers.
- Sentinel recall: 5/5 prespecified TEAS reports found by exact DOI.
- Repository file: `01_search_strategy/cochrane/2026-07-21/CENTRAL_TEAS_EA_2026-07-21.ris`.
- SHA-256: `4f288276ab7a477f3f03bb4fb01821c90c57f2bc43ac882425bd1075e1758459`.
- Limitation: personal Cochrane authentication failed, so `Perioperative_TEAS_EA_CENTRAL_2026-07-21` was not saved to an account. The complete session strategy was used directly for the export.
- Import into Covidence: not performed.

## 2026-07-22T20:34:39+0200 - RUN-005 - Embase revised search and RIS export

- Authorization: user requested the revised Embase search and then explicitly requested an account-free alternative when personal sign-in failed.
- Platform and access: Embase.com through active Lund University institutional access; personal Embase account not signed in.
- Emtree validation: eight requested headings verified exactly; all existed and were explodable; no heading substitution.
- Search execution: lines #1–#55 entered and counted separately in Advanced Search/Search History; Quick Search broad mapping and Embase AI were not used.
- Syntax correction: requested nested proximity line #9 was rejected; it was expanded into two OR-connected proximity chains without changing fields or proximity distances.
- Key counts: #15 EA 3,831; #16 TEAS 1,942; #17 unfiltered combined 5,357; #53 randomized EA 1,487; #54 randomized TEAS 682; #55 final combined 1,928.
- Modality overlap: 241 records between #53 and #54.
- Known-study validation: seven candidate electrical-intervention reports found in both #17 and #55; none lost to the RCT filter. Six excluded-modality candidates were present in Embase by DOI but absent from #17/#55 as expected.
- Saved-search limitation: `Perioperative_TEAS_EA_EMBASE_2026-07-22` was not saved because Save required personal sign-in.
- Export workaround: #55 exported in four sequential institutional-access batches (500, 500, 500, 428), with originals retained and mechanically concatenated after range and identifier checks.
- Final RIS: `01_search_strategy/embase/2026-07-22/EMBASE_TEAS_EA_2026-07-22.ris`.
- RIS QA: 1,928 `ER` records, 1,928 `TY` records, 1,928 unique `U2` identifiers, no duplicated identifier across batches.
- Final RIS SHA-256: `df095489600339a0674e3ac24c64208b278c5a27c0b1cc2a7b0514fdad1ae27a`.
- Deduplication: not performed.
- Covidence import: not performed.

## 2026-07-23T11:14:31+0200 - RUN-006 - CINAHL revised search and RIS export

- Authorization: user requested the revised CINAHL search, explicitly authorized CINAHL Ultimate when Lund did not expose CINAHL Complete, and requested an account-free alternative because MyEBSCO sign-in was unavailable.
- Platform and access: EBSCOhost through active Lund University institutional access; CINAHL Ultimate alone selected; personal MyEBSCO account not signed in.
- Heading validation: 20 requested CINAHL headings checked. Material substitutions were `Transcutaneous Electric Nerve Stimulation` for the expected “Electrical” wording and omission of artificial plus signs where Explode was unavailable.
- Search execution: the final clean S1–S50 strategy was entered and counted separately in Proximity search mode; no full-text field or interface limits were used.
- Corrective rerun: an 88-line temporary execution inherited earlier server-side line references and produced impossible combinations. Only those temporary current-run lines were deleted; the exact strategy was rerun cleanly from S1. No saved search or unrelated history was altered.
- Key counts: S4/I4 EA 2,552; S15/I15 TEAS 9,598; S21/P6 perioperative 1,301,499; S22/U1 462; S23/U2 1,008; S24/U3 1,437; S47/R23 1,110,026; S48/F1 155; S49/F2 333; S50/F3 465.
- Modality overlap: 23 records between F1 and F2.
- Seed validation: Chen 2020, Yu 2020, and Lam 2022 were present in both U3 and F3; none was lost to the trial filter. Four indexed excluded-modality records were absent from U3 as expected. Six candidates remain uncertain for CINAHL indexing because exact DOI/title checks were zero and the third author/distinctive-words check was not completed.
- Saved-search limitation: `Perioperative_TEAS_EA_CINAHL_2026-07-23` was not saved because MyEBSCO personal authentication was unavailable.
- Export workaround: the 25,000-record export required MyEBSCO. F3 was exported account-free as ten sequential RIS batches (50 × 9; 15 × 1), with originals retained and mechanically concatenated after range, count, hash, and accession-number checks.
- Final RIS: `01_search_strategy/cinahl/2026-07-23/CINAHL_TEAS_EA_2026-07-23.ris`.
- RIS QA: 465 `ER` records, 465 titles, 465 unique CINAHL accession numbers, no repeated batch hash, and no missing or repeated range.
- Final RIS SHA-256: `92d4e9375696891a1818a24cacc322b5ca7b23266d424f83e3827e4a3c244e42`.
- Warning: the prespecified `TEAS` acronym retrieved substantial false positives involving thoracic epidural anesthesia/analgesia (`TEA`); this should be considered at PRESS review.
- Deduplication: not performed.
- Covidence import: not performed.
