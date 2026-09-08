# Handover intake, 8 September 2026

The supplied 18-row RoB 2 CSV and its companion narrative are preserved verbatim
under `inputs/`. `v34_RoB2_Draft.csv` adds stable result IDs, source hashes,
draft status, and empty human-adjudication fields. It is a parallel CSV register,
not an adjudicated workbook sheet. No draft enters `Corrected_RoB2` or GRADE.
Regenerate it with `python3 09_V34_INTAKE/ingest_rob2_drafts.py`.

`result_rob2_coverage.csv` resolves each current secondary contrast to either an
existing assessment for that result or an explicit pending status. Wang 2024's
two risk strata retain separate comparison IDs. The supplied draft itself says
their Domain 3 judgments differ; human adjudication must retain that distinction.
Twenty-one of 26 analysed contrasts remain pending, representing 20 study/result
pairs (Wang's two strata share an intake draft). Five contrasts have an existing
assessment for the relevant result. This coverage check does not independently
validate those existing human assessments.

Four further study/result gaps were absent from the supplied register: first
defecation in Huang 2025, Gu 2019, Gao 2021, and Yang 2020. Their on-file judgments
concern flatus or ileus, which cannot be transferred to defecation.

The two Wu 2025 drafts are retained for provenance but marked excluded from
treatment-effect synthesis: intraoperative outcomes predate PACU randomization.
All other draft judgments and supporting text remain exactly as supplied. They
have not been independently source-verified or adjudicated. In particular, some
entries cite prior audits instead of page-specific quotations; Song 2020 is
explicitly unjudgeable. "Completed" in the input filename does not mean the
review's assessments are complete.

## Extraction intake

The supplied missed-outcome audit targets v32 and overlaps the v33 integration.
It is a list of findings and further extraction targets, not the completed
17-study, arm-level CSV specified by `08_V33_MASTER/CHATGPT_EXTRACTION_PROMPT.md`.
It includes unresolved candidates such as Li 2021's interval PONV counts and
additional pain/recovery timepoints. These are not promoted from prose into a
pooled model. The requested completed extraction return has not been supplied.

No v34 master was created and no full v34 pipeline switch was attempted. The
v32/v33 workbooks remain byte-identical to their baselines. The present work
corrects selection of existing secondary data and repairs the dashboard. A v34
data integration still requires source verification of the returned extractions,
composite-key reconciliation, cached-formula preservation, new reconciliation
sheets, and a v34 QC gate before changing the authoritative master.

Historical instructions in the v32 audit permitting digitization or potential
median conversion are not adopted. The later handover's prohibitions govern
this work. Graph-only evidence remains graph-only; no MME is manufactured.
