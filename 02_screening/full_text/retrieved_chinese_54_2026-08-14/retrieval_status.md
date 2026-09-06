# Retrieval status for 54 Chinese-language records — 2026-08-14

## Scope

- Covidence records: the 54 records at screening sequences 219–272 in `codex_fulltext_decisions_200.csv`.
- All 54 have PubMed/Covidence abstracts.
- Identifiers: 54/54 have PMIDs; 30 have DOIs and 24 have no DOI.
- No PDF has yet been saved or uploaded from this retrieval pass.

## Journal distribution

| Journal | Records | Current retrieval finding |
|---|---:|---|
| *Zhongguo Zhen Jiu / Chinese Acupuncture & Moxibustion* | 40 | Official article pages located; tested full-text endpoint redirects to CNKI and exposes no public PDF. |
| *Chinese Journal of Integrated Traditional and Western Medicine* | 7 | PubMed abstracts located; no lawful open full text found in the source audit. |
| *Zhen Ci Yan Jiu / Acupuncture Research* | 4 | Official article/issue pages located; all four tested PDF endpoints return a 51-byte `attachment empty` response rather than an article PDF. |
| *Zhongguo Gu Shang / China Journal of Orthopaedics and Traumatology* | 2 | Official full-text/download links located. The site presents a slider security verification before serving the files. |
| *Journal of Traditional Chinese Medicine* | 1 | PubMed labels the record free, but the historical journal PDF link is now dead (404) and no archived copy was located. |

## Open-access and institutional checks

- Europe PMC returned exact records for all 54 PMIDs, but none was flagged as open access or present as a full-text Europe PMC article.
- Lund's CNKI database page lists licensed subject sections in humanities, social sciences, education, politics/law, and economics. Medical/science journal sections containing these records are not listed in Lund's subscription.
- The official *Chinese Acupuncture & Moxibustion* article API returned abstract metadata and a CNKI destination, but no PDF URL.
- Systematic or automated downloading from CNKI was not attempted; Lund's licence does not cover the relevant medical sections and licensed databases restrict systematic downloading.

## Two official full-text links requiring security verification

1. Covidence #405 — Ge M, Zhai XJ, Li Y. *Clinical efficacy of adductor canal blockade combined with transcutaneous electrical acupoint stimulation for total knee arthroplasty.* DOI: 10.12200/j.issn.1003-0034.2021.08.011. Official page: http://www.zggszz.com/zggszzcn/ch/reader/view_abstract.aspx?file_no=20210811
2. Covidence #220 — Li QY, Li SM, Du JX. *Clinical study of electroacupuncture therapy on postoperative rehabilitation of patients with knee fractures.* DOI: 10.12200/j.issn.1003-0034.20220156. Official page: http://www.zggszz.com/zggszzcn/ch/reader/view_abstract.aspx?file_no=20240408

The journal's PDF request is currently paused at a visible slider CAPTCHA. User confirmation is required before attempting that verification.

## File-integrity note

Two 59-byte HTML security-check responses were initially returned with `.pdf` filenames. Validation showed that they were not PDFs, so they were removed and were not uploaded to Covidence.

## Recommended next step

- After the user authorizes solving the journal's slider CAPTCHA, retry and validate the two *Zhongguo Gu Shang* PDFs.
- Submit the remaining unresolved records to Medicinska fakultetens bibliotek for interlibrary loan, using PMID as the primary identifier. Their quoted fee is SEK 80 per supplied article and SEK 0 when they locate a free copy.
