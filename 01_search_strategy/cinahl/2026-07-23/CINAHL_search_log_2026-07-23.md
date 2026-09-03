# CINAHL revised search log — 23 July 2026

## Database and access

- Requested database: CINAHL Complete.
- Database executed: **CINAHL Ultimate**, alone.
- Platform: EBSCOhost.
- Access route: Lund University institutional authentication.
- Institutional access: active.
- Database substitution: Lund's database selector exposed CINAHL Ultimate but not CINAHL Complete. Work paused and the user explicitly authorized CINAHL Ultimate before the strategy was executed. The substitution is visible in `screenshots/CINAHL_database_selection_blocker.png`.
- Personal MyEBSCO status: not signed in (`Sign in` was displayed).
- Search date: 23 July 2026.
- Search mode: Proximity search, the current interface mode supporting Boolean operators, quoted phrases, and `N`/`W` proximity. SmartText, natural-language search, “Find all my search terms,” and “Find any of my search terms” were not used.
- Limits: none. Full Text, Peer Reviewed, date, language, age, country, specialty, anesthesia, outcomes, abstract availability, publication type, and nursing-subset limits were not applied.
- Major Concept: not selected for any heading.
- Multiple databases: not selected.

## CINAHL Heading validation

All 20 requested headings were checked in CINAHL Headings before the final clean execution. The complete table is in `CINAHL_heading_validation_2026-07-23.csv`.

Material differences from the expected wording were:

- `Electroacupuncture` existed but had no narrower headings or Explode option, so EBSCO generated `MH "Electroacupuncture"` rather than an artificial plus form.
- The preferred physical-intervention heading was `Transcutaneous Electric Nerve Stimulation` (Electric, not Electrical). It had no Explode option, so `MH "Transcutaneous Electric Nerve Stimulation"` was used.
- `Acupuncture Points` had no Explode option, so the non-plus form was used.
- `Pretest-Posttest Design`, `Cluster Sample`, and `Comparative Studies` offered Explode, but the May 2023 Cochrane filter specifies the non-exploded headings; the filter was executed as specified.
- `Surgery, Operative`, `Anesthesia`, `Perioperative Care`, `Randomized Controlled Trials`, `Acupuncture`, and `Animals` were exploded.

## Exact strategy, mapping, and counts

The exact executed 50-line strategy is preserved in `CINAHL_search_strategy_2026-07-23.txt`; a machine-readable conceptual-to-EBSCO mapping and count for every line is in `CINAHL_line_counts_2026-07-23.csv`.

Key sets:

| Concept | EBSCO line | Description | Count |
|---|---:|---|---:|
| I4 | S4 | EA intervention set | 2,552 |
| I15 | S15 | TEAS intervention set | 9,598 |
| P6 | S21 | Perioperative set | 1,301,499 |
| U1 | S22 | Unfiltered perioperative EA | 462 |
| U2 | S23 | Unfiltered perioperative TEAS | 1,008 |
| U3 | S24 | Unfiltered combined | 1,437 |
| R23 | S47 | Cochrane CINAHL controlled-trial filter | 1,110,026 |
| F1 | S48 | Final randomized perioperative EA | 155 |
| F2 | S49 | Final randomized perioperative TEAS | 333 |
| F3 | S50 | Final combined retrieval | 465 |

Consistency checks passed:

- F1 (155) was no larger than U1 (462).
- F2 (333) was no larger than U2 (1,008).
- F3 (465) was no larger than U3 (1,437).
- `155 + 333 - 465 = 23`, so 23 records occurred in both modality sets.

## Session and syntax audit

An initial execution accumulated 88 temporary lines across a server-persisted EBSCO history. Set references in the later lines resolved against earlier temporary lines, producing impossible combinations (for example, a combined set larger than both parents). No saved search was affected. The 88 temporary lines were selected and deleted after their counts and the failure were recorded, and the complete strategy was rerun in a clean history numbered S1–S50. The clean rerun reproduced all independent concept counts and produced internally consistent combined sets. This was an execution-state correction, not a scientific search revision.

The final S1–S50 history was reviewed for database, mode, fields, parentheses, quotation marks, proximity operators, Major Concept, and interface limits. The final-history screenshot is `screenshots/CINAHL_search_history_final.png`.

DOI validation initially tested the generic `DO` field code. The CINAHL-specific DOI field code `DI` was then used for definitive seed checks. These diagnostic lines were added after S50 and are not part of the review strategy.

## Seed-study validation

The definitive table is `CINAHL_seed_validation_2026-07-23.csv`.

- Clearly indexed by exact DOI or exact title: Baldawi 2022, Chen 2020, Wang 2022, Shah 2020, Yu 2020, Lam 2022, and Zhang 2024.
- Present in both U3 and F3: Chen 2020, Yu 2020, and Lam 2022.
- Chen intersected both the EA and TEAS intervention sets in CINAHL; it should be treated as TEAS during screening.
- Yu was retrieved by the TEAS set.
- Lam was retrieved by the EA set but remains potentially ineligible if EA cannot be separated from its auricular component.
- Indexed but absent from U3 as expected for excluded interventions: Baldawi (battlefield/auricular), Wang (auricular/intradermal), Shah (auricular/battlefield), and Zhang (manual acupuncture).
- Exact DOI and exact-title checks were both zero for Maurer 2024, Ao 2021, Zhu 2024, Gu 2019, Zhou 2021, and Szmit 2021. Because the requested first-author-plus-distinctive-title-words check was not separately completed, their indexing status is recorded as **uncertain**, not definitively absent.
- No report present in U3 was lost at F3; therefore no known retrieved report failed the RCT filter.
- Cao 2023 was not treated as a required seed.

No strategy change was made merely to retrieve a report that may not be indexed in CINAHL.

## Search saving

The intended name was `Perioperative_TEAS_EA_CINAHL_2026-07-23`. The strategy was not saved to MyEBSCO because no personal account was signed in and account saving requires personal authentication. The complete exact strategy, counts, and screenshots are preserved locally instead. No credentials were entered or requested, and no earlier saved search was overwritten.

## Export

F3 contained 465 records. The one-click `Export results (Up to 25,000)` control opened a MyEBSCO personal-sign-in requirement. Because the user had already stated that personal sign-in was unavailable and requested an alternative, the account-free citation export was used:

1. Results were displayed 50 per page.
2. Each consecutive page was selected in preserved relevance order.
3. Each selection was exported using **Cite → Export citation → Export in RIS format**.
4. Ten original, non-overlapping batches were retained: nine batches of 50 and one batch of 15.
5. The batches were mechanically concatenated only after range and record-count verification.

Batch ranges, filenames, sizes, hashes, and record counts are in `CINAHL_export_manifest_2026-07-23.csv`. No EBSCO folder was created or modified.

The RIS export contains the most complete metadata that EBSCO's citation-manager RIS route supplied. Across the merged file it contains:

- 465 titles;
- 3,302 author fields;
- 423 abstracts where available;
- 421 DOI fields;
- 465 CINAHL accession numbers;
- 452 journal/source fields;
- 9,212 subject/keyword fields;
- publication years/dates, language, source details, publication-type notes, and EBSCO permalinks where supplied.

The RIS route did not offer a separate “include search query” or field-customization checkbox.

## RIS verification

- F3 platform count: 465.
- Selected/exported ranges: 1–50, 51–100, 101–150, 151–200, 201–250, 251–300, 301–350, 351–400, 401–450, 451–465.
- Sum selected: 465.
- Sum of `ER  -` terminators in original batches: 465.
- Merged RIS `ER  -` count: 465.
- Merged RIS accession numbers: 465, all unique.
- Duplicate batch hashes: zero.
- Missing or repeated ranges: none.
- Final file size: 1,399,954 bytes.
- Final SHA-256: `92d4e9375696891a1818a24cacc322b5ca7b23266d424f83e3827e4a3c244e42`.
- Final RIS: `CINAHL_TEAS_EA_2026-07-23.ris`.
- Cross-database deduplication: not performed.
- Covidence import: not performed.

## Warnings and unresolved decisions

- This is a CINAHL **Ultimate** search, not CINAHL Complete. The substitution was user-authorized but should remain visible in reporting.
- The unqualified acronym `TEAS` generated substantial irrelevant retrieval. Visual inspection showed false positives where `TEA` referred to thoracic epidural anesthesia/analgesia, apparently affected by EBSCO term-variant handling. The exact prespecified line was retained; consider a documented PRESS revision before calling this the definitive CINAHL strategy.
- Six seeds have unresolved indexing status because the third requested author-plus-distinctive-title-words check was not completed.
- The saved-search name was not created because MyEBSCO personal sign-in was unavailable.

The RIS is structurally valid and count-matched, and is ready for a **new** Covidence import after the user reviews these warnings. It has not been imported.
