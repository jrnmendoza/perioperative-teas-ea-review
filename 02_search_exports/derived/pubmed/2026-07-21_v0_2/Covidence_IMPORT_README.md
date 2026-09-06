# Covidence import instructions - PubMed v0.2

Primary upload file:

`Covidence_PubMed_TEAS_EA_v0_2_2026-07-21_N-1009.ris`

## Expected import

- Source database: PubMed.
- Search date: 2026-07-21.
- Strategy: PubMed v0.2 (v0.1 with `operation*[tiab]` removed).
- Expected submitted RIS records: 1,009.
- Unique PMIDs in RIS: 1,009.
- RIS encoding: UTF-8 with CRLF line endings.
- RIS SHA-256: `aa0bc86658a67adb340608542f86e75992a0c68e5d8c3125ea9f99f4fd5446bc`.

Upload only the RIS file. Do not also upload the XML or PMID list, because that would submit the same PubMed records more than once.

After Covidence processes the file, record the number imported, the number Covidence marks as duplicates, any rejected records, the import timestamp, and the Covidence review name in a new append-only audit entry. A difference between 1,009 submitted and the final number entering screening may be expected after cross-database deduplication, but it must be reconciled.

The RIS includes one PubMed book-style record represented as RIS type `CHAP`; all other 1,008 records use `JOUR`. This preserves all 1,009 PubMed results rather than silently omitting the book record.

