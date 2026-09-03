# PubMed v0.2 narrowed export strategy

Status: reproducible PubMed export prepared for manual Covidence upload  
Parent: PubMed pilot v0.1

## Change from v0.1

Removed only:

```text
operation*[tiab]
```

Rationale: `operation*` retrieved many non-surgical uses of “operation.” Its removal reduced the combined count from 1,170 to 1,009 during diagnostic testing without changing indexed sentinel recall (24/25). All other TEAS, EA, surgery/perioperative, randomized-trial, and animal-only logic is unchanged.

## Preserved safeguards

- TEAS and EA remain separate concepts before OR combination.
- `anesthe*` and `anaesthe*` remain optional surgery/perioperative synonyms; general anaesthesia is not mandatory.
- No opioid, pain, analgesia, PONV, recovery, postoperative-outcome, language, date, or adult restriction was added.
- The complete Cochrane sensitivity-maximizing randomized-trial component is retained.
- Modality MeSH headings are retained.

## Exact files

- `pubmed_v0_2_multiline.txt`: exact readable query.
- `pubmed_v0_2_transport.txt`: whitespace-normalized transport query.
- `pubmed_v0_2_surgery_line.txt`: narrowed surgery/perioperative component.

The TEAS, EA, and randomized-trial component files remain identical to their v0.1 counterparts.

## Executed counts

- TEAS line: 572.
- EA line: 701.
- Combined unique PubMed records: 1,009.
- Indexed sentinel recall: 24/25; the unchanged miss is PMID 29391879, whose PubMed metadata contains no searchable electrical/EA signal.

The complete citation set was exported on 2026-07-21 after the user requested a RIS for Covidence. It is not labelled a formal search and was not uploaded by Codex.

