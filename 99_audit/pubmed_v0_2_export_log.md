# PubMed v0.2 export log

Append-only. Corrections must be added as new entries.

## 2026-07-21 - EXP-001 - Narrowing decision

- Parent strategy: PubMed v0.1.
- Change: removed only `operation*[tiab]` from the surgery/perioperative component.
- Diagnostic effect: combined count 1,170 to 1,009; indexed sentinel recall unchanged at 24/25.
- TEAS line: 572; EA line: 701; combined unique result: 1,009.
- No general-anaesthesia, adult, date, language, outcome, comparator, or other mandatory restriction was added.

## 2026-07-21 - EXP-002 - Initial conversion stop

- ESearch and EFetch completed for 1,009 records.
- The initial converter stopped because the XML contained one `PubmedBookArticle` in addition to 1,008 `PubmedArticle` records.
- No record was omitted and no partial RIS was released.
- The raw partial-run ESearch and EFetch XML were preserved under `99_audit/failed_runs/pubmed_v0_2_initial_book_record_stop/`.
- The converter was updated to map PubMed book articles explicitly to RIS type `CHAP`.

## 2026-07-21T21:08:16+0200 - EXP-003 - Successful Covidence RIS export

- Strategy: PubMed v0.2.
- Query SHA-256: `13828be90c898a43bfe8b5fc31bdd0ff97434d24cb623b2f3bd79c855793fa90`.
- NCBI API key status: available; value not printed or stored.
- ESearch count: 1,009.
- Raw XML records: 1,009 (1,008 journal articles; 1 book article).
- Unique PMIDs: 1,009.
- RIS records: 1,009.
- RIS file size: 2,872,694 bytes.
- RIS SHA-256: `aa0bc86658a67adb340608542f86e75992a0c68e5d8c3125ea9f99f4fd5446bc`.
- Indexed sentinel recall: 24/25; missed PMID 29391879.
- Validation: PASS for balanced TY/ER markers, one AN PMID per record, unique PMID set, exact XML/PMID/RIS order agreement, UTF-8 decoding, CRLF line endings, and manifest checksums.
- Covidence upload: not performed by Codex.

