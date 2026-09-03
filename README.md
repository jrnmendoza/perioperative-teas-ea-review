# Perioperative TEAS and EA Review 2026

Reproducible repository for a new systematic review of perioperative transcutaneous electrical acupoint stimulation (TEAS) and needle-based electroacupuncture (EA) in adults undergoing operative surgery under general anaesthesia.

## Authority and status

- Authoritative protocol: `00_protocol/source/PROSPERO TEAS EA.pdf`.
- Locked operational summary: `00_protocol/protocol_scope_locked.md`.
- The protocol PDF was copied unchanged from the supplied source and is protected by the checksum recorded in `99_audit/project_initialization_log.md`.
- This repository is independent of the previous broad acupuncture review. Previous-project files are read-only sources for terminology, known-report validation, and reproducibility comparisons; they are not raw inputs to this review.
- Current stage: narrowed PubMed v0.2 citation export prepared for manual Covidence upload at the user's request. It is not labelled the formal PubMed search.

## Guardrails

- TEAS and EA remain separate modalities in every downstream analysis.
- Sham-controlled contrasts are principal; usual-care and no-stimulation contrasts are supportive and separate.
- No date or language restrictions apply to electronic database searches. Full-text eligibility is restricted to reports published in English under the dated amendment in `00_protocol/amendments/2026-08-20_english_full_text_eligibility.md`.
- General anaesthesia is verified during screening, not required in the electronic search.
- Opioid use, pain, postoperative outcomes, PONV, recovery, and other outcomes are not mandatory search concepts.
- No search results have been imported into Covidence, deduplicated, screened, or used to obtain full text in this repository. A validated 1,009-record PubMed RIS is ready for manual upload under `02_search_exports/derived/pubmed/2026-07-21_v0_2/`.

## Repository map

- `00_protocol/`: source protocol, locked scope, and future amendments.
- `01_search_strategy/`: master concepts, database translations, pilot versions, and PRESS materials.
- `02_search_exports/`: immutable raw exports, derived files, and manifests when formal searching begins.
- `03_deduplication/` through `10_manuscript/`: staged review workflow.
- `99_audit/`: append-only project and provenance records.

## PubMed pilot

The proposed v0.1 strategy is stored in multiline and single-line transport forms under `01_search_strategy/pubmed/`. Counts and sentinel-recall testing are documented separately so the strategy text is not overwritten by run metadata. Re-run instructions are in the accompanying explanation and script.
