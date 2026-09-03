# Search decision log

Append-only. Corrections must be added as new dated entries; prior entries are not edited or deleted.

## 2026-07-21 - SD-001 - Review-specific repository boundary

Decision: Treat the previous broad acupuncture review as read-only. Use it only to identify terminology, known reports, and reproducibility comparisons. Do not copy or reuse its raw search exports.

Rationale: This is a new review with narrower electrical-modality eligibility and its own protocol authority.

## 2026-07-21 - SD-002 - Separate modality architecture

Decision: Construct TEAS and EA as separate search lines, combine them with OR only at the retrieval stage, and retain separate contribution counts.

Rationale: The protocol prohibits pooling TEAS and EA downstream and the search contribution of each modality must be auditable.

## 2026-07-21 - SD-003 - No mandatory anaesthesia or outcome block

Decision: Do not require general anaesthesia, opioid consumption, analgesia, pain, MME, morphine, PONV, recovery, or any postoperative outcome in the electronic search.

Rationale: These concepts can be absent or incomplete in titles, abstracts, and indexing. General anaesthesia is verified during screening.

## 2026-07-21 - SD-004 - PubMed randomized-trial component

Decision: Use the Cochrane sensitivity-maximizing PubMed randomized-trial component and standard animal-only exclusion.

Rationale: It is a validated, sensitive filter appropriate to randomized-trial identification and includes British and American spelling variants in this implementation.

## 2026-07-21 - SD-005 - Provisional known-report set

Decision: Freeze the initial sentinel metadata before testing PubMed v0.1. Include only reports for which the previous review clearly supports surface TEAS or separable needle-based EA. Keep non-PubMed-indexed reports outside the PubMed recall denominator.

Rationale: A predeclared denominator reduces circular revision of the strategy and allows legitimate cross-database sentinels to be retained.

## 2026-07-21 - SD-006 - Pilot-only execution

Decision: Run count-only and targeted sentinel-intersection tests. Do not retrieve the full result set.

Rationale: The user requested strategy testing before record retrieval and explicitly prohibited formal-search labeling, import, deduplication, screening, and full-text downloading.

## 2026-07-21 - SD-007 - PubMed v0.1 miss not overfit

Decision: Preserve v0.1 unchanged after 24/25 sentinel recall and send the generic-acupuncture backstop question to PRESS-style review.

Rationale: The missed confirmed EA report (PMID 29391879) contains no electrical, electroacupuncture, needle, current, device, stimulation, or MeSH signal in PubMed metadata. Adding a synonym cannot repair the miss. Generic `acupunctur*` would retrieve it but materially expands the modality line to protocol-excluded manual, auricular, press-tack, wrist-ankle, buccal, and other acupuncture. That tradeoff requires explicit methodological review rather than a post hoc targeted edit.

## 2026-07-21 - SD-008 - v0.1 pilot disposition

Decision: Mark PubMed v0.1 acceptable for PRESS-style review but not ready for formal execution.

Rationale: The query has full TEAS sentinel recall, focused EA terminology, a validated sensitive RCT component, no prohibited mandatory concepts, and transparent modality counts. Formal execution is held pending adjudication of the one metadata-hidden EA miss and four zero-yield phrase warnings.

## 2026-07-21 - SD-009 - Narrowed PubMed v0.2 export

Decision: Create v0.2 by removing only `operation*[tiab]`, then retrieve all PubMed citations and generate a validated RIS after the user explicitly requested a Covidence upload file.

Rationale: The term contributed 161 records while its removal preserved v0.1's 24/25 indexed sentinel recall. Anaesthesia stems, modality MeSH headings, and the complete validated randomized-trial component remain because their removal offers smaller gains or greater recall risk. The export is not called the formal PubMed search.

