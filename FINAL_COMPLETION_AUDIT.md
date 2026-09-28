# Final completion — pre-change audit (28 September 2026)

Written before any scientific change on branch `final-completion`, which was created from `origin/main`.

## Repository and deployment state

| Item | Value |
|---|---|
| `origin/main` HEAD | `80e7e42` (Merge PR #54, reviewer wording in RoB 2/GRADE records) |
| Deployment branch `claude-v26-dashboard-final` | `80e7e42` (same commit) |
| Latest Pages run | 36451379132, success (build, deploy, verify), 28 Sep 2026 16:29 UTC |
| Live `build-meta.json` | `git_commit` `80e7e42…`, built 2026-09-28T16:29:36Z, fingerprint `082ac6becd78` |
| Commits after the dashboard refinement (PR #51/#52) | PR #53 (second-review record; dashboard AI wording removed), PR #54 (RoB 2/GRADE reviewer wording) |
| Branch protection | `main` and `claude-v26-dashboard-final` are both unprotected |

## Test status before changes (all pass)

- `build_site.py`, `deploy_integrity_check.py`, `check_current_dashboard.py`: 38 contracts, 32 isolated mutations,
  72 download hashes.
- `check_handover.py --mutation-test`, `check_tab_data.py`: pass (v38 contract).
- `check_generated_artifacts.py --fast`: the generated dashboard matches its generator.
- `validate_adjudication.py`: OVERALL PASS. Checks: source integrity 73, registry 831, membership 210, input metadata
  177, input re-derivation 177, independent refit 345, RoB linkage 155, GRADE correspondence 38, participant ledger 70.
- `verify_regimen_extraction.py`: 70 reports, 280 rows, pass.
- `check_current_dashboard_ui.cjs`: 18/18 browser checks.

## Analytical state (unchanged, to be preserved)

- 70 reports, 69 trial families, 761 canonical results, 74 core models (69 fitted), 177 model inputs.
- 94 core RoB 2 assessments, 38 core GRADE bodies.
- QoR ~24 h: 3 bodies, 9 diagnostics, 8 RoB, 3 GRADE. QoR later windows: 6 models (4 bodies + 2 leave-one-out
  diagnostics), 5 RoB, **0 GRADE**.
- E1 24-h opioid bodies:
  - TEAS/sham: k=1, N=48, −7.70 [−10.62, −4.78].
  - EA/sham: no data.
  - TEAS/usual: k=1, N=47, −8.00 [−10.92, −5.08].
  - EA/usual: k=2, N=159, −6.83 [−76.39, 62.73].
  - The joint criterion is not established.
- E2 is post hoc and ungraded.
- Stata: 117 models, 64 pooled + 48 single-study verified, 5 no-data, 0 discrepancies, largest relative difference 9.0e-7.
- Second review (`second_review.csv`): SP, 2026-09-28, all confirmed, no changes. It covers RoB 2 (core 94, QoR 8, later 5),
  GRADE (core 38, QoR 3) and the regimen fields (280). The signalling-question file is **not** in the record.

## Provenance and documentation inconsistencies found

1. **`FINAL_CURRENT_STATE_REPORT.md`, and its dashboard copy, is stale.**
   - It is dated 20 Sep 2026.
   - Its deployment section names `d6f18d1` and "43 downloads"; the current state is 72 downloads and deployment `80e7e42`.
   - It does not mention the Stata layer, the E1 vs E2 workspace, the characteristics, the regimen extraction, the second
     review, or the reviewer-wording update.
   - It says "Prior human completion is user-reported" and "no further reviewer approval". Its canonical provenance
     fields now record a second review by SP on 28 Sep 2026.
   - The outstanding list is still accurate: none of the four items is complete at HEAD.
2. **`DASHBOARD_REFINEMENT_REPORT.md` is partly superseded.**
   - Sections 1 and 5 describe the regimen fields as single-extractor (they now carry a second review).
   - Section 8 is an accurate record of the 2971096 deployment.
   - It is a dated task report, so it will get a pointer note rather than a rewrite.
3. **The manuscript is stale on review provenance.**
   - `METHODS.md` (review-provenance note; "Use of AI-assisted tools"), `DISCUSSION.md` and `CONCLUSIONS.md` say the
     RoB 2/GRADE judgements "do not constitute two independent human assessments".
   - A second review of all of them by SP (28 Sep 2026, all confirmed) is now recorded, so these sentences need the new fact.
   - The AI-use disclosure itself describes methodology for journal submission. It is retained, not removed.
   - `RESULTS.md` and `DISCUSSION.md` describe the later-window QoR results as not certainty-rated. That is correct now
     and will change only if GRADE is completed.
4. **Reviewer fields are internally consistent.**
   - RoB 2 files, `grade.csv` and `qor_grade.csv` record the delegated first assessment and SP's second review.
   - `rob2_signalling_questions.csv` records "Delegated assessor" only, which matches `second_review.csv` (signalling
     answers are not listed as second-reviewed).
   - `methodological_decisions` records "Adopted under user delegation".
   - The older hash records (`08_QOR_ANALYSIS/verification.json`, `baseline_hashes.json`) describe earlier file versions;
     `PROVENANCE_WORDING_UPDATE_2026-09-28.md` explains this.
5. **The Overview "What changed" list** says "Risk-of-bias and all 38 certainty decisions adopted; no reviewer
   approval queue". This is still true, but it omits the second review (shown elsewhere on the Overview).

## Characteristics verification gaps (recomputed: 70 reports × 28 fields = 1,960 values)

| Status | Values |
|---|---|
| Verified (registry) | 731 |
| Legacy (v26, not re-verified) | 692 |
| Verified (PDF quote, second reviewer) | 208 |
| Canonical result register | 140 |
| Not reported in source | 72 |
| Source-traced (extraction record) | 71 |
| Verified (PDF quote) | 25 |
| Not verified | 16 |
| Partly verified (source excerpt) | 5 |

Priority fields:

| Field | Current status |
|---|---|
| Age | 69 legacy, 1 registry |
| Female | 68 legacy, 2 registry |
| BMI, ASA | 70 legacy each |
| Acupoints, frequency | 70 legacy each |
| Intensity | 68 legacy, 2 partly verified |
| Timing, sessions, session duration | 69 legacy, 1 partly verified each |
| Anaesthesia | 30 registry, 24 PDF quote, **16 not verified** |

That is 692 legacy values plus 16 not-verified anaesthesia values to source-verify.

## QoR GRADE gap

The four later-window bodies below are ungraded. The two leave-one-out diagnostics of `QOR15_SHAM_POD3` stay ungraded
by rule.

| Model | Comparison | k | N | MD (95% CI) | RoB 2 |
|---|---|---|---|---|---|
| `QOR40_SHAM_POD2` | QoR-40 TEAS vs sham POD2 | 1 | 60 | 3.67 (0.83 to 6.51) | Yu 2020: Some concerns |
| `QOR40_USUAL_48H` | QoR-40 TEAS vs usual care 48 h | 1 | 70 | 2.00 (0.82 to 3.18) | Liang 2021: Some concerns |
| `QOR15_SHAM_POD2` | QoR-15 TEAS vs sham POD2 | 1 | 97 | 3.86 (−0.09 to 7.81) | Zhou 2025: Some concerns |
| `QOR15_SHAM_POD3` | QoR-15 TEAS vs sham POD3 | 2 | 130 | 11.54 (−40.70 to 63.78), I² 81.9% | Hou 2023, Xing 2022: Some concerns |

## Narrative evidence gaps

- **LOS / PACU / extubation / mobilisation.** `10_FINAL_ADJUDICATION/los_audit.md` and `los_exact.md` (untracked
  working notes) hold source excerpts only. No structured table exists.
- **Harms.** `07_OUTCOME_COVERAGE/safety_evidence.csv` has 32 report entries with 22 free-text statuses. There is no
  final structured table with separated categories. The Gu 2019 count/prose conflict is documented but unresolved.
- **Satisfaction / acceptability.** `recovery_evidence.csv` has 29 entries: 16 QoR, 9 satisfaction, 2 quality of life,
  2 acceptability. There is no structured table with instrument, time point, arm values and synthesis usability.

## Manuscript and reference gaps

- `references/bibliography.csv` (tracked) has 31 entries, all `VERIFIED` against PubMed/Crossref. Every citekey in the
  current manuscript resolves to it: Introduction 21, Methods 12, Discussion 4. Results, Abstract and Conclusions carry
  no citations.
- The citekeys (`[@key]`) are not yet rendered as numbered references. This is the "placeholder" item.
- `references/reference_registry.csv` (44 entries) and `claim_citation_audit.csv` (24 claims) are untracked and audit
  the **previous, rejected manuscript** (a different review). There is no claim-level audit of the current manuscript.
- No automated check ties the manuscript's numbers (k, N, estimates, CIs, certainty) to the canonical outputs.

## Planned work (in order)

1. Later-window QoR GRADE (four bodies) in the existing QoR GRADE record, with correspondence checks.
2. Source verification of the 11 priority characteristic fields through a structured extraction file, the existing
   generator and a verifier. Plus a second-review worksheet; nothing is marked second-reviewed.
3. Structured tables for LOS/PACU/extubation/mobilisation, harms and satisfaction/acceptability, built from the source
   texts, with a verifier for quotations.
4. A claim-citation audit of the current manuscript, rendered numbered references, and a manuscript-number check
   against canonical outputs.
5. A regenerated, continuously current `FINAL_CURRENT_STATE_REPORT.md`. The 20 Sep version stays in git history.
   A contract will tie its inventory to the payload.
6. Dashboard integration only where the scientific state changes, then the final report and deployment.

No canonical estimate, CI, heterogeneity statistic, membership, eligibility, RoB 2 judgement or existing GRADE rating is
planned to change. Any discrepancy found will be documented and handled through the pipeline.
