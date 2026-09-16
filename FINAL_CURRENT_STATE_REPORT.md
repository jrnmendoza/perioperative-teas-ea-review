# Current state of the TEAS/EA review: adjudication v36

16 September 2026 · branch `astra-final-resolution` · base `035ed97` + uncommitted v36 changes

## Data lock: NOT ALLOWED

The adjudication layer is internally consistent, source-traceable for the primary construct, and numerically reproducible. The review is **not ready for data lock**. Three things block it:

1. **Completeness.** 122 full texts were excluded as "wrong outcomes" under a primary-outcome screening rule, but registered eligibility admits any eligible outcome. Mechanical triage flags 84 of them for priority re-screening.
2. **PRISMA provenance.** Six included reports, among them Szmit 2021, the sole principal TEAS/sham opioid contributor, are still marked "excluded" in Covidence, and the reason counts in the PRISMA figure do not match the records.
3. **Sign-off gaps.** No human sign-off exists for GRADE or RoB 2 linkage, most secondary-body results lack exact RoB 2 assessments, and the registration identifier is unconfirmed.

The dashboard is stale and must not be rebuilt or deployed yet. Details: `10_FINAL_ADJUDICATION/06_REPORTS/UNRESOLVED_HUMAN_DECISIONS.md`.

## Which files are authoritative

| Role | Files |
|---|---|
| **Current (v36)** | `10_FINAL_ADJUDICATION/01–06` and `code/`; root `FINAL_TRIAL_REPORT_MAPPING.csv`, `FINAL_PARTICIPANT_LEDGER.csv`, `FINAL_PRIMARY_OUTCOME_TRACEABILITY.csv`, `FINAL_MODEL_MEMBERSHIP_MATRIX.csv`, `FINAL_RESULT_ROB2_LINKAGE.csv`, `FINAL_GRADE_RECOMMENDATIONS.md`; decision records `ASTRA_FINAL_PROTOCOL_RECONCILIATION.md`, `FINAL_PROSPERO_CURRENT_REVIEW_MATRIX.md`, `FINAL_PRIMARY_SOURCE_DECISIONS.md`, `FINAL_MME_CONVERSION_POLICY.md`, `FINAL_MME_CONVERSIONS.csv` |
| **Historical, not current** | `ASTRA_SCIENTIFIC_AUDIT.md`, `ASTRA_AUDIT_ISSUES.csv`, `ASTRA_VERIFICATION_AUDIT.md` (initial findings, still valid as findings); `ASTRA_FINAL_LOCK_REPORT.md`, `FINAL_DATA_LOCK_CHECKLIST.md`, `ASTRA_IMPLEMENTATION_PLAN.md`, `ASTRA_REMEDIATION_CHANGELOG.md`, `ASTRA_POST_REMEDIATION_INTEGRITY.md`, `ASTRA_PROSPERO_REMEDIATION_EVIDENCE.md` (13 Sep blocked pre-adjudication run: "no decisions implemented", k=4/k=7 estimates); copies in `00_STARTING_STATE/`; `06_FINAL_ANALYSIS_V26`, `07_TIERED_V33`, `08_V33_MASTER`, `09_V34_*`; `dashboard/`, `_site/` |
| **Superseded** | `10_FINAL_ADJUDICATION/05_REPRODUCTION/superseded_2026-09-13T1306_pre_final_membership/`: its 554/554 metafor PASS predated the committed model inputs and certified a different membership |

The "FINAL" filename prefix does not signal approval. Every adjudication decision was made after results were known.

## Contradictions found and dispositions

| Contradiction | Disposition |
|---|---|
| Lock report (13 Sep): "no human decisions implemented; existing k=4 TEAS/sham −13.99" vs adjudication layer: TEAS/sham k=1 −7.7 | Lock report is the historical blocked run. The adjudication layer was produced under the later user authorization in `00_STARTING_STATE/user_authorization.txt` and `run_identity.json`. |
| Committed HEAD registry labels Huang 2017 EA; HEAD results label it TEAS | Source is unambiguous TEAS (surface electrodes, HANS-200A, "non-invasive"). The user's uncommitted edit is retained and makes the chain consistent. |
| `statistical_policy.md` cites an independent metafor 5.0-1 reproduction | That reproduction was stale (above). Regenerated with metafor 5.2-1: 68 models, 731 fields, 0 failures. |
| Pan 2023 and Liang 2021 no-stimulation controls sat in sham bodies; Xiong 2021's electrode sham sat in a usual-care body | Corrected with source quotes (v36 C1–C3). Every membership now passes a comparator gate. |
| Seven study-level comparator labels contradicted source-verified result classes | Corrected with quotes; the other 63 flagged LEGACY |
| GRADE rationale text named only some High-RoB trials (pain rest, flatus EA/usual); nausea/vomiting 48 h text said "linkage incomplete" when linked | Text corrected; certainty unchanged |
| He 2026 48-h value cited the SAP (sm8842) instead of the eTables (sm8843) | Label corrected; eTables preserved byte-identically in `01_SOURCE_EVIDENCE/supplements/` |
| Zheng 2025 printed mean (SD) cannot produce its printed P values (new) | Values unchanged; three leave-out diagnostics added; bowel-sounds GRADE Low→Very low (reviewer to confirm) |

## Primary construct (all delivered systemic opioid, end of surgery–24 h, mg IV MME)

| Body | Role | k | N | MD (95% CI) | GRADE (ASTRA recommendation) |
|---|---|---:|---:|---|---|
| TEAS vs sham | Principal | 1 (Szmit 2021) | 48 | −7.70 (−10.62 to −4.78), single-study contrast | Low |
| EA vs sham | Principal | 0 | 0 | No eligible absolute 24-h systemic data | Not rated |
| TEAS vs usual care | Supportive | 1 (Szmit 2021, separate arm) | 47 | −8.00 (−10.92 to −5.08), single-study contrast | Very low |
| EA vs usual care | Supportive | 2 (El-Rakshy 2009, Seevaunnamtum 2016) | 159 | −6.83 (−76.39 to 62.73), REML + safeguarded HK | Very low |

No body meets the registered clinical criterion. No point estimate reaches −10 mg, and none of these trials contributes an eligible ~24-h pain result: Szmit's VAS is adjudicated as discharge pain, and the TEAS/sham rest-pain body (upper CI 0.33) comes from different trials. Chen 1998, Chen 2020, He 2026 hepatectomy, Yang 2024, Lin 2002, Lee 2011, Sim 2002 and Coura 2011 contribute only to labelled sensitivity or diagnostic models, never to primary results. All 22 primary-construct rows were verified literally against source text or registered supplements (`06_REPORTS/PRIMARY_EVIDENCE_TABLE.md`). v36 changed none of these four bodies.

## Participant accounting

70 reports; 69 operational trial units (Yeh 2010/2011 held as one probable-overlap family, counted once and excluded from models); 12,103 randomized participants as an operational count with a Yeh lower bound. That figure is **not** an analyzed or efficacy population, and the dashboard's 10,618 remains unsupported. Analyzed N is body-specific (see manifest). 48 of 70 reports contribute to at least one model.

## What was verified in v36

- Pre-edit committed state regenerated byte-identically (15/15 files); v36 chain deterministic (21/21 outputs).
- Independent validator (`code/validate_adjudication.py`, separate REML algorithm and input re-derivation) passes all 8 check groups. It fails on committed HEAD and on injected 1%/0.001 perturbations, so it can detect errors.
- metafor cross-check: 0 failures.
- 70 source PDFs, the PROSPERO PDF and the supplement copy hash-verified; 349 source files unchanged; no destructive commands; user edits preserved.

See `06_REPORTS/REPRODUCIBILITY_REPORT.md`, `GRADE_ROB2_RECONCILIATION.md`, `PRISMA_REPORT_TRIAL_ACCOUNTING.md`, `MODEL_MEMBERSHIP_ANALYSIS_MANIFEST.md` and `CHANGELOG_v36.md`.

## Reporting requirements that remain in force

Disclose that the protocol identifier is unconfirmed and that CRD420251090635 belongs to a similar review; all adjudication occurred after results were known; the 14 Aug screening rule versus the 20 Aug registered eligibility; re-inclusions outside Covidence; source contradictions (Chen 2020, He 2026 ×2, El-Rakshy 2009, Zheng 2025, Yeh); IV-MME unit uncertainty; and that k=1 and k=2 bodies are very uncertain. Do not present a diagnostic sensitivity as a primary result, and do not describe the reproducible calculations as validating source truth or completeness.
