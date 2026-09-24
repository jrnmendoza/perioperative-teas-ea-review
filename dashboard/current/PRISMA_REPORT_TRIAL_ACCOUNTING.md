# PRISMA reconciliation — v38

Wu 2016: citation search, user-confirmed 20 September 2026; no historical discovery date invented. Raw exports unchanged. Local adjudication does not imply that Covidence itself was edited.

## Database branch

- Raw RIS references: 5100 (Embase 1928, CENTRAL 1698, CINAHL 465, PubMed 1009).
- Historical imported records: 5088; **12-reference import difference unmapped**, not asserted as verified duplicate removal.
- Recorded upstream removals: 1651 automatic duplicates + 1 manual duplicate + 508 automation exclusions = 2160.
- 5088 − 2160 = 2928 screened; 2928 − 2704 title/abstract exclusions = 224 reports sought.
- Saved exports: 224 sought − 2 not retrieved = 222 retrieved records; six exact DOI/title duplicates removed late, leaving 216 distinct reports assessed.
- 216 distinct reports assessed − 147 excluded = 69 included database reports.
- Late duplicate removal: Chung, Tian, Tong, Tu, Wang and Yang (six records). Zhang’s distinct conference abstract remains an Abstract only exclusion.

## Other-methods branch

One citation report sought, retrieved, assessed and included: Wu 2016. Therefore 69 + 1 = **70 reports, 69 operational trial families** (Yeh probable overlap counted once; both held out of models).

## Full-text exclusion reasons

| Reason | Records |
|---|---:|
| no perioperative analgesia outcome found | 113 |
| Wrong intervention | 7 |
| Wrong comparator | 3 |
| Publication language | 12 |
| Wrong setting | 8 |
| Wrong patient population | 2 |
| Wrong study design | 1 |
| Abstract only | 1 |

Six source-verified canonical reports formerly marked excluded are reinstated by this delegated adjudication: Gao2022, Liu2015, Oztas2019, Song2020, Szmit2021 and Zhang2018. The Zhang conference abstract is a distinct report (different DOI), excluded as Abstract only, not an exact duplicate publication. The original 161 exclusions reconcile as 6 reinstatements + 2 not retrieved + 6 exact duplicates + 147 substantive exclusions. The 122 original Wrong outcomes entries become 113 retained reason-labelled records after six reinstatements and three duplicate removals. Tu’s two exports disagree on the reason; the lowest-ID original reason is retained only as an administrative count convention, not a new validation of that clinical exclusion.

The requested label **no perioperative analgesia outcome found** replaces the display wording, not the immutable original reason field. Re-screening is no longer a requested deliverable. The historical outcome-focused exclusion rule versus broader registered eligibility remains an evidence-completeness limitation; the label does not retrospectively validate every exclusion.

Record-level ledger: `02_DECISIONS/v38/prisma_record_ledger.csv` (225 rows). Upstream deduplication numbers are historical aggregates; absent event logs prevent exact replay. The six late exact duplicates are fully mapped in `02_DECISIONS/v38/late_duplicate_register.csv`. The unrelated 12-reference import gap is not explained away by those six late discoveries.
