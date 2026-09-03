# Embase search log — 22 July 2026

## Identification and access

- Database: Embase.
- Platform: Embase.com, Elsevier.
- Access route: Lund University institutional access.
- Institutional access: active; the interface displayed “Brought to you by Lund University, Library”.
- Personal Embase sign-in: not active.
- Search date: 22 July 2026.
- Search name requested: `Perioperative_TEAS_EA_EMBASE_2026-07-22`.
- Saved-search status: not saved to a personal account. Embase requested personal sign-in when Save was selected. The complete executed strategy, line counts, screenshots, and exports were preserved locally instead.
- Embase AI: not used.
- Quick Search broad mapping: not used; Advanced Search and Search History were used, with broad mapping disabled.

## Emtree validation

All eight requested headings existed exactly as entered and were available for explosion. No heading substitution was made. The exact checks are in `EMBASE_Emtree_validation_2026-07-22.csv`.

## Syntax correction

The requested #9 was rejected by Embase with “Missing bracket at”:

```text
((transcutaneous NEAR/3 electric*) NEAR/5 (acupoint* OR (acupunctur* NEAR/2 point*))):ti,ab,kw
```

An attempted field-distributed equivalent was also rejected with “Proximity operands cannot contain any field codes.” The accepted line expanded the nested proximity expression into two OR-connected chains:

```text
((transcutaneous NEAR/3 electric* NEAR/5 acupoint*):ti,ab,kw) OR ((transcutaneous NEAR/3 electric* NEAR/5 acupunctur* NEAR/2 point*):ti,ab,kw)
```

This correction did not change the specified field restrictions or proximity distances. No other scientific or syntax change was made. Embase made display-only normalizations, including distributing field tags, lowercasing TEAS/TAES, and displaying hyphenated wildcard phrases as quoted space-separated phrases.

## Exact executed strategy and line counts

The following is the exact strategy as displayed in Search History. Commas in counts are thousands separators.

```text
#1  'electroacupuncture'/exp                                                            12,814
#2  electroacupunctur*:ti,ab,kw OR 'electro-acupunctur*':ti,ab,kw OR 'electro acupuncture':ti,ab,kw OR 'electric acupuncture':ti,ab,kw OR 'electrical acupuncture':ti,ab,kw    11,600
#3  #1 OR #2                                                                            14,502
#4  'transcutaneous electrical nerve stimulation'/exp                                  13,194
#5  'acupuncture'/exp                                                                   71,753
#6  'acupuncture point'/exp                                                             10,036
#7  #4 AND (#5 OR #6)                                                                    2,741
#8  teas:ti,ab,kw OR taes:ti,ab,kw OR 'transcutaneous electrical acupoint stimulation':ti,ab,kw OR 'transcutaneous electric acupoint stimulation':ti,ab,kw OR 'transcutaneous acupoint electrical stimulation':ti,ab,kw OR 'transcutaneous electrical acupuncture point stimulation':ti,ab,kw OR 'transcutaneous electrical acupuncture stimulation':ti,ab,kw OR 'transcutaneous acupoint stimulation':ti,ab,kw OR 'transcutaneous electrical acustimulation':ti,ab,kw OR electroacustimulation:ti,ab,kw    5,385
#9  ((transcutaneous NEAR/3 electric* NEAR/5 acupoint*):ti,ab,kw) OR ((transcutaneous NEAR/3 electric* NEAR/5 acupunctur* NEAR/2 point*):ti,ab,kw)    822
#10 #7 OR #8 OR #9                                                                       7,836
#11 'surgery'/exp                                                                    7,414,767
#12 'anesthesia'/exp                                                                   531,563
#13 surg*:ti,ab,kw OR operat*:ti,ab,kw OR perioperat*:ti,ab,kw OR 'peri operat*':ti,ab,kw OR intraoperat*:ti,ab,kw OR 'intra operat*':ti,ab,kw OR postoperat*:ti,ab,kw OR 'post operat*':ti,ab,kw OR preoperat*:ti,ab,kw OR 'pre operat*':ti,ab,kw OR anesthe*:ti,ab,kw OR anaesthe*:ti,ab,kw    6,112,954
#14 #11 OR #12 OR #13                                                               9,868,341
#15 #3 AND #14                                                                          3,831
#16 #10 AND #14                                                                         1,942
#17 #15 OR #16                                                                          5,357
#18 'randomized controlled trial'/exp                                                1,225,102
#19 'controlled clinical trial'/de                                                     463,138
#20 random*:ti,ab,tt                                                                 2,694,468
#21 'randomization'/de                                                                 102,619
#22 'intermethod comparison'/de                                                        322,339
#23 placebo:ti,ab,tt                                                                   490,485
#24 compare:ti,tt OR compared:ti,tt OR comparison:ti,tt                                744,272
#25 (evaluated:ab OR evaluate:ab OR evaluating:ab OR assessed:ab OR assess:ab) AND (compare:ab OR compared:ab OR comparing:ab OR comparison:ab)    3,636,128
#26 (open NEXT/1 label):ti,ab,tt                                                       207,221
#27 ((double OR single OR doubly OR singly) NEXT/1 (blind OR blinded OR blindly)):ti,ab,tt    390,572
#28 'double blind procedure'/de                                                        334,668
#29 (parallel NEXT/1 group*):ti,ab,tt                                                   58,043
#30 crossover:ti,ab,tt OR 'cross over':ti,ab,tt                                       165,451
#31 ((assign* OR match OR matched OR allocation) NEAR/6 (alternate OR group OR groups OR intervention OR interventions OR patient OR patients OR subject OR subjects OR participant OR participants)):ti,ab,tt    610,066
#32 assigned:ti,ab,tt OR allocated:ti,ab,tt                                           661,019
#33 (controlled NEAR/8 (study OR design OR trial)):ti,ab,tt                            703,741
#34 volunteer:ti,ab,tt OR volunteers:ti,ab,tt                                         335,012
#35 'human experiment'/de                                                             764,066
#36 trial:ti,tt                                                                       622,296
#37 #18 OR #19 OR #20 OR #21 OR #22 OR #23 OR #24 OR #25 OR #26 OR #27 OR #28 OR #29 OR #30 OR #31 OR #32 OR #33 OR #34 OR #35 OR #36    8,112,891
#38 ((random* NEXT/1 sampl* NEAR/8 ('cross section*' OR questionnaire* OR survey OR surveys OR database OR databases)):ti,ab,tt) NOT ('comparative study'/de OR 'controlled study'/de OR 'randomised controlled':ti,ab,tt OR 'randomized controlled':ti,ab,tt OR 'randomly assigned':ti,ab,tt)    4,150
#39 'cross-sectional study'/de NOT ('randomized controlled trial'/exp OR 'controlled clinical trial'/de OR 'controlled study'/de OR 'randomised controlled':ti,ab,tt OR 'randomized controlled':ti,ab,tt OR 'control group':ti,ab,tt OR 'control groups':ti,ab,tt)    528,674
#40 'case control*':ti,ab,tt AND random*:ti,ab,tt NOT ('randomised controlled':ti,ab,tt OR 'randomized controlled':ti,ab,tt)    25,932
#41 'systematic review':ti,tt NOT (trial:ti,tt OR study:ti,tt)                          388,008
#42 nonrandom*:ti,ab,tt NOT random*:ti,ab,tt                                           22,196
#43 'random field*':ti,ab,tt                                                            3,378
#44 ('random cluster' NEAR/4 sampl*):ti,ab,tt                                           1,890
#45 review:ab AND review:it NOT trial:ti,tt                                         1,435,864
#46 'we searched':ab AND (review:ti,tt OR review:it)                                   65,137
#47 'update review':ab                                                                    158
#48 (databases NEAR/5 searched):ab                                                      92,876
#49 (rat:ti,tt OR rats:ti,tt OR mouse:ti,tt OR mice:ti,tt OR swine:ti,tt OR porcine:ti,tt OR murine:ti,tt OR sheep:ti,tt OR lambs:ti,tt OR pigs:ti,tt OR piglets:ti,tt OR rabbit:ti,tt OR rabbits:ti,tt OR cat:ti,tt OR cats:ti,tt OR dog:ti,tt OR dogs:ti,tt OR cattle:ti,tt OR bovine:ti,tt OR monkey:ti,tt OR monkeys:ti,tt OR trout:ti,tt OR marmoset*:ti,tt) AND 'animal experiment'/de    1,360,478
#50 'animal experiment'/de NOT ('human experiment'/de OR 'human'/de)                2,890,301
#51 #38 OR #39 OR #40 OR #41 OR #42 OR #43 OR #44 OR #45 OR #46 OR #47 OR #48 OR #49 OR #50    5,256,802
#52 #37 NOT #51                                                                      7,152,559
#53 #15 AND #52                                                                         1,487
#54 #16 AND #52                                                                           682
#55 #53 OR #54                                                                          1,928
```

Machine-readable exact queries and counts are in `EMBASE_line_counts_2026-07-22.csv`. The final set was smaller than the unfiltered combined set (#55 1,928 versus #17 5,357). The two modality sets overlap by 241 records because 1,487 + 682 − 1,928 = 241.

## Restrictions

No interface limit was applied for publication year, language, country, age, general anesthesia, surgical specialty, postoperative outcomes, abstract availability, full text, publication status, or journal-only publication type. No additional EBM or randomized-trial checkbox was applied. Conference records, preprints, Embase Classic records, MEDLINE records, and ClinicalTrials.gov-derived records were not excluded.

## Source and publication-type audit for #55

The interface displayed: MEDLINE 767; Embase 453; Embase and MEDLINE 445; Clinical Trials 260; Preprints 3; PubMed-not-MEDLINE 2. A separate Embase Classic count was not displayed. Publication-type facets showed Conference Abstract 159, Conference Paper 3, and Conference Review 2. These are reported exactly as displayed; category totals are not assumed to be mutually exclusive or additive. No source facet was used as a restriction. See `EMBASE_source_breakdown_2026-07-22.csv`.

## Known-study validation

Thirteen candidate author-year reports were checked. DOI intersections returned seven records in #17 and the same seven in #55: Ao 2021, Chen 2020, Gu 2019, Yu 2020, Zhou 2021, Lam 2022, and Szmit 2021. None of these seven was lost to the randomized-trial filter.

The six candidates absent from both sets were each found in Embase by exact DOI: Maurer 2024, Baldawi 2022, Zhu 2024, Wang 2022, Shah 2020, and Zhang 2024. Their absence from #17 reflects non-target interventions—press-tack/intradermal, battlefield/auricular, buccal, auricular buried intradermal, auricular, and manual acupuncture—not database absence. Lam 2022 was retrieved through the EA text-word line but remains unsuitable for final eligibility if the EA and auricular components cannot be separated. Cao 2023 was not treated as a required seed, as instructed. Full results are in `EMBASE_seed_validation_2026-07-22.csv`.

## Export

- Final exported set: #55.
- Final result count: 1,928.
- Export format: RIS format (Mendeley, EndNote).
- Export content: citation information; bibliographical information; abstract, original abstract, author keywords, and available index-related metadata; DOI, PMID/PUI and source/publication details; full-text, Embase, and OpenURL links.
- “Include search query in export”: not offered in the available export dialog.
- Single-file export attempt: Embase required personal sign-in for an export larger than 500 records.
- Workaround: sequential non-overlapping batches under active Lund institutional access, followed by local integrity checks and mechanical concatenation. No personal credential was entered or requested.

| Batch | Exported range | Records | SHA-256 |
|---|---:|---:|---|
| `EMBASE_TEAS_EA_2026-07-22_batch001.ris` | 1–500 | 500 | `ba0f329d8f764c251004e6a564ad4671e8ea81780007fda52d2e1b56bb6f1636` |
| `EMBASE_TEAS_EA_2026-07-22_batch002.ris` | 501–1000 | 500 | `834bbc75ff5db084f12d82e2cb63777563acdc494901815d8ae0eeabdd08f8fb` |
| `EMBASE_TEAS_EA_2026-07-22_batch003.ris` | 1001–1500 | 500 | `fd8c6e9f566ed02bbc8e8604b19fb85eda0ec808730ac692f01f03172230982d` |
| `EMBASE_TEAS_EA_2026-07-22_batch004.ris` | 1501–1928 | 428 | `89064403d0a21ca6894e43dd9d4b49ff59c05ba51713b9e75e92b6c885a5c060` |

The original four batches were retained. The merged file is `EMBASE_TEAS_EA_2026-07-22.ris`, SHA-256 `df095489600339a0674e3ac24c64208b278c5a27c0b1cc2a7b0514fdad1ae27a`.

## RIS verification

- #55 interface result count: 1,928.
- Records selected across the four ranges: 1,928.
- Batch RIS `ER  -` count: 500 + 500 + 500 + 428 = 1,928.
- Merged RIS `ER  -` count: 1,928.
- Merged RIS `TY  -` count: 1,928.
- Embase/PUI (`U2  -`) identifiers: 1,928 total and 1,928 unique; no duplicate identifier across batches.
- Titles (`T1  -`): 1,928 records.
- Author tags (`A1  -`): 10,234.
- Abstracts (`N2  -`): 1,872 records; missing abstracts reflect source availability.
- DOI tags (`DO  -`): 1,206 records.
- Publication-type tags (`M3  -`): 1,922 records.
- Source/journal tags (`JF  -`): 1,927 records.
- Result: all record-count comparisons agree. No deduplication was performed and MEDLINE overlaps were retained.

## Screenshots

- `screenshots/EMBASE_search_history_final.png`
- `screenshots/EMBASE_results_final.png`
- `screenshots/EMBASE_export_settings.png`

## Unresolved decisions and warnings

- The search was not saved to a personal Embase account because personal sign-in was unavailable. Local records fully preserve the executed strategy and export but do not create an account-side reusable saved search.
- #9 required the documented syntax-preserving expansion; it should receive human PRESS-style review.
- Lam 2022 is retrievable but may be ineligible because EA and auricular components may not be separable. This is a screening decision, not a search defect.
- The broad perioperative headings and `operat*`/anesthesia wording will retrieve irrelevant records; this is an expected sensitivity cost and no unvalidated narrowing was applied.
- The export is technically ready for a new Covidence import after investigator review. No Covidence import was performed in this task.
