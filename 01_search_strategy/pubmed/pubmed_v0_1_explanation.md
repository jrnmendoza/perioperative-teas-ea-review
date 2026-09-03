# PubMed pilot v0.1: explanation and test report

Status: ACCEPTABLE PILOT FOR PRESS-STYLE REVIEW; NOT A FORMAL SEARCH  
Executed: 2026-07-21T20:25:37+02:00  
Interface: NCBI PubMed E-utilities ESearch via HTTP POST  
Execution: count-only plus targeted sentinel-PMID intersections; the complete result set was not retrieved

## Exact strategy files

- Multiline exact strategy: `pubmed_v0_1_multiline.txt`
- Single-line transport strategy: `pubmed_v0_1_transport.txt`
- Auditable modality lines: `pubmed_v0_1_teas_line.txt` and `pubmed_v0_1_ea_line.txt`
- Shared setting and design components: `pubmed_v0_1_surgery_line.txt` and `pubmed_v0_1_rct_line.txt`

The transport file is a whitespace-normalized form of the multiline strategy; the Boolean logic and field tags are unchanged.

## Architecture and rationale

1. **TEAS line.** Combines exact TEAS/TAES names, reordered wording, electro-acupoint wording, contextual acronyms, contextual TENS-at-acupuncture-point logic, and descriptive surface-electrode language. TENS is never searched without an acupuncture-point qualifier.
2. **EA line.** Combines the `Electroacupuncture` MeSH heading, common free-text spelling/hyphenation variants, electric/electrical acupuncture phrases, and electrical-stimulation language tied to acupuncture needles.
3. **Surgery/perioperative line.** Uses operative-procedure and perioperative care/period headings plus broad surgical, operative, perioperative, pre/intra/postoperative, postsurgical, and anaesthesia text words. General anaesthesia is not mandatory.
4. **Randomized-trial line.** Implements the Cochrane Highly Sensitive Search Strategy sensitivity-maximizing PubMed filter (2008 revision), with `randomised[tiab]` added for explicit British spelling coverage. Source: [Cochrane Handbook, Chapter 4, Box 4.4.a](https://training.cochrane.org/handbook/current/chapter-04).
5. **Animal-only exclusion.** Applies `NOT (animals[mh] NOT humans[mh])`; this removes animal-only indexed records without imposing a mandatory human filter on unindexed records.

No adult, language, publication-date, general-anaesthesia, opioid, analgesia, pain, MME, morphine, PONV, recovery, or postoperative-outcome requirement is present.

## Result counts

| Auditable line | Exact logic | PubMed count |
|---|---|---:|
| TEAS | TEAS concept AND surgery/perioperative AND RCT filter NOT animal-only | 661 |
| EA | EA concept AND surgery/perioperative AND RCT filter NOT animal-only | 858 |
| Combined | (TEAS concept OR EA concept) AND surgery/perioperative AND RCT filter NOT animal-only | 1,170 |

The separate line counts sum to more than the combined count because PubMed terminology and indexing can place a report in both modality lines. This is expected and is not deduplication.

## Sentinel recall

- PubMed-indexed sentinel denominator: 25 reports (22 suspected TEAS; 3 suspected EA).
- Retrieved: 24/25 overall (96%).
- TEAS reports: 22/22 (100%).
- EA reports: 2/3 (66.7%).
- Non-indexed cross-database sentinel: 1 report, excluded from the PubMed denominator.
- Report-level results: `pubmed_v0_1_sentinel_recall.csv`.

### Investigated miss

Wang 2018, PMID 29391879, is the sole miss. The previous review's locally available full-text extraction clearly describes filiform needles at ST36, PC6, LI4, and ST37 connected to an electronesthesia apparatus, so it is a legitimate provisional EA sentinel. PubMed's title and abstract, however, use only generic *acupuncture* wording; the record has no MeSH headings and no searchable electrical, electroacupuncture, needle, current, device, or stimulation term. The surgery and RCT concepts are present, so the failure occurs exclusively in the modality concept.

No v0.1 revision was made. Retrieving this report from PubMed would require adding a generic acupuncture term that intentionally captures manual, auricular, press-tack, wrist-ankle, buccal, and other protocol-excluded acupuncture modalities. That is a material sensitivity-versus-specificity decision rather than a synonym correction and should be adjudicated during PRESS-style review. The report remains identifiable through the known-report set and later citation searching; this does not make it electronically retrievable by the current modality-focused query.

## PubMed diagnostics

PubMed returned the count without errors. It reported `QuotedPhraseNotFound` warnings for four zero-yield phrases:

- `"transcutaneous electric acupuncture stimulation"[tiab]`
- `"transcutaneous electro-acupoint stimulation"[tiab]`
- `"acupuncture-like transcutaneous electric nerve stimulation"[tiab]`
- `"electrically stimulating acupuncture"[tiab]`

These terms do not alter current retrieval because PubMed found no matching phrase. They are retained transparently in v0.1 for PRESS review rather than silently removed. A later cleanup, if approved, must be saved as a new version.

## Terms likely to increase irrelevant retrieval

- The contextual `TENS`/TENS-MeSH plus acupuncture-point branch may retrieve ordinary TENS studies when the article also mentions acupuncture points.
- `"electrical acupoint stimulation"`, `electric*[tiab]`, and `electrostimulat*[tiab]` branches may retrieve acupoint electrical stimulation that is not therapeutic TEAS or is used for monitoring.
- `Electroacupuncture[Mesh]` can retrieve records in which PubMed indexing does not distinguish surface TEAS from needle EA; three TEAS sentinels also intersected the EA line.
- Broad surgery text words such as `operation*`, `surg*`, `anesthe*`, and `anaesthe*` can retrieve non-operative or methodological uses of those words.
- The sensitivity-maximizing RCT terms `trial`, `groups`, and the `drug therapy` floating subheading improve recall but reduce precision.

These are anticipated screening burdens, not grounds for adding prohibited outcome or general-anaesthesia restrictions.

## Reproduction

From the repository root, run:

```bash
/Users/ryan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  01_search_strategy/pubmed/run_pubmed_pilot_test.py
```

The script checks whether `NCBI_API_KEY` is present and passes it directly to NCBI if available; it never prints or stores the value. Counts are dynamic and must be timestamped whenever re-run.

## Readiness recommendation

The strategy is ready for PRESS-style review as a pilot, not ready for formal execution. PRESS review should specifically decide whether to add a generic `acupunctur*` sensitivity backstop to capture metadata-hidden EA such as PMID 29391879, accept that report as a structurally unsearchable sentinel supplemented by citation methods, and remove or retain the four zero-yield quoted phrases. No full-result export should occur until those decisions are recorded in a new version.

## Other warnings and unresolved protocol decisions

- The supplied PROSPERO PDF is a preview that states the record has not yet been submitted or published; repository language therefore avoids implying registration is complete.
- The protocol says only published studies will be sought, while also specifying trial-register searching and allowing insufficient conference abstracts to await classification. Before register searching begins, clarify whether registers are used only to identify/link published reports and detect reporting bias, or whether unpublished results may become eligible evidence.
- The EA validation denominator contains only three clearly confirmed PubMed-indexed reports from the previous review. PRESS review should assess whether additional independent EA sentinels can be identified before formal execution.
- Search-validation status is provisional and must not be treated as final screening eligibility.
