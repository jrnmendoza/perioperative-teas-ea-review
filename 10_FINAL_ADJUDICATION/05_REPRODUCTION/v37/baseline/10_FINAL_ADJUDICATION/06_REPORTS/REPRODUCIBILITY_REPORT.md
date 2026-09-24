# Reproducibility report (v36, 16 September 2026)

**Result: the full adjudication chain regenerates deterministically from its declared inputs, and two independent implementations reproduce every fitted model. This establishes computational reproducibility and internal consistency only. It does not establish that source extractions are true, that the evidence base is complete, or that any judgment is approved.**

## 1. Revision and environment

| Item | Value |
|---|---|
| Branch / HEAD | `astra-final-resolution` / `035ed976033944c5861ac3f471ac3852778b715f` (checks ran with v36 changes in the worktree; those changes were then committed unaltered as `dbb15df`–`3e56991` and merged via PR #23) |
| Python | 3.14.7, numpy 2.5.3, scipy 1.18.1, in a scratch venv (Homebrew Python lacks scipy) |
| R | 4.5.2, metafor 5.2-1 in a scratch library (the 13 Sep run used metafor 5.0-1 from `/tmp/astra-r-library`, which no longer exists) |
| Input hashes | `05_REPRODUCTION/integrity_v36.json` → `input_sha256` (v34 outcome extraction, verification-support JSON, v26 target CSVs, Covidence exports, source manifests) |
| Output hashes | `05_REPRODUCTION/output_sha256_v36.txt` (21 outputs) |
| Full log | `05_REPRODUCTION/run_log_v36.txt` |

## 2. Commands (run from the project root)

```bash
PY=<venv>/bin/python            # any Python with numpy+scipy
$PY 10_FINAL_ADJUDICATION/code/build_registry.py        # 70 reports, 69 trial units
$PY 10_FINAL_ADJUDICATION/code/build_results.py         # 761 canonical rows, 73 models, 179 input contrasts
$PY 10_FINAL_ADJUDICATION/code/fit_models.py            # REML + safeguarded HK (scipy bounded REML likelihood)
$PY 10_FINAL_ADJUDICATION/code/link_rob2.py             # 97/761 exact RoB 2 links
$PY 10_FINAL_ADJUDICATION/code/grade_recommendations.py # 38 authored GRADE bodies
ASTRA_R_LIBRARY=<rlib> Rscript 10_FINAL_ADJUDICATION/code/reproduce_metafor.R
$PY 10_FINAL_ADJUDICATION/code/compare_metafor.py       # 68 models, 731 fields
$PY 10_FINAL_ADJUDICATION/code/triage_exclusions.py     # 161 exclusion triage flags
python3 10_FINAL_ADJUDICATION/code/crosswalk_covidence.py
$PY 10_FINAL_ADJUDICATION/code/build_reports.py         # generated table reports
$PY 10_FINAL_ADJUDICATION/code/validate_adjudication.py # independent validator
```

## 3. Results

| Check | Scope | Tolerance | Result |
|---|---|---|---|
| Regeneration of committed state before v36 edits | 15 canonical/derived files, rebuilt in a scratch mirror with the user's uncommitted Huang 2017 edit | byte identity | **PASS** 15/15 identical |
| Determinism (v36) | 21 outputs, full chain run twice | byte identity | **PASS** 21/21 |
| metafor vs scipy | 68 fitted models (k≥1), 731 fields: k, N, effect, SE, CI, p, τ², I², PI; plus metafor-recomputed yi/vi vs stored inputs | abs diff ≤ 1e-5 + 1e-5·abs(value); yi/vi ≤ 1e-10 | **PASS** 0 failures (max scaled diff ~1e-7) |
| Validator: source integrity | 70 source PDFs vs manifest SHA-256, text files, PROSPERO PDF vs `run_identity.json`, He 2026 supplement copy vs original | SHA-256 identity | **PASS** 73/73 |
| Validator: registry consistency | `studies.json` ↔ `FINAL_TRIAL_REPORT_MAPPING.csv` ↔ result rows (modality, trial ID, comparator, N, hash); Yeh held as one unit counted once | exact | **PASS** |
| Validator: membership semantics | 212 memberships: modality, source-verified comparator class, held studies (Yeh, Jin 2023, Long 2025) excluded, source location present, non-sensitivity bodies only use INCLUDE rows, primary units absolute mg | exact | **PASS** |
| Validator: input re-derivation | 179 trial-level contrasts re-derived from canonical rows (factors, arm combination, shared-control identity, RR zero-cell rule, SMD) | MD/RR rel. 1e-9; SMD 5e-4 (approx. J) | **PASS** |
| Validator: independent refit | Fisher-scoring REML + safeguarded HK; k=1 not pooled; PI only k≥5 | MD/RR rel. 1e-6; τ² +1e-6 abs; SMD 5e-4 | **PASS** 340 fields |
| Validator: RoB 2 linkage | 97 links: study identity and overall rating match assessment register; unlinked results carry no rating | exact | **PASS** |
| Validator: GRADE correspondence | 38 bodies: row exists for every non-sensitivity model and no other; header k/N/certainty and effect text match outputs; cited participant counts equal model N; threshold-crossing claims true | exact | **PASS** |
| Validator: participant ledger | Yeh 2011 counted 0; ITT/mITT/PP ≤ randomized | exact | **PASS** |
| Primary literal source check | 22 primary-construct rows: all arm means/SDs occur as printed in source text or registered supplement | literal token (decimal point or comma) | **PASS** 22/22 |

**Negative controls (the validator can fail):**
- Run against committed HEAD, it **FAILS** registry consistency: HEAD `studies.json` labels Huang 2017 EA while HEAD `results.csv` labels its five rows TEAS. It also fails membership semantics: Pan 2023 in a sham body, Xiong 2021 and eight other rows with unreviewed `CONTROL_TYPE_REVIEW_REQUIRED` comparators. The two Chen 2015 hash failures in that run were mirror artifacts, because those PDFs sit at the project root.
- Mutating one stored variance by 1% and one stored CI bound by 0.001 produced one input_rederivation failure and one independent_refit failure.

## 4. Failures encountered and classification

| Failure | Class | Resolution |
|---|---|---|
| `scipy` missing from Homebrew Python | Archive environment | Scratch venv; not committed |
| `/tmp/astra-r-library` absent (13 Sep metafor library) | Archive environment | `reproduce_metafor.R` now honours `ASTRA_R_LIBRARY`; default unchanged |
| Untracked `05_REPRODUCTION/` from 13:06 predated the 13:08 model inputs (different membership: PONV k=11, pain-rest k=2, Xing as usual care); its 554/554 PASS did not certify the committed outputs | Computational provenance | Preserved in `superseded_2026-09-13T1306_pre_final_membership/` with README; regenerated against current inputs |
| Committed HEAD not internally consistent (Huang 2017 registry EA vs results TEAS) | Scientific metadata | User's TEAS edit (uncommitted at the start of v36, now `dbb15df`) is source-supported and resolves it (see changelog) |
| metafor SMD warning (`abs(yi) > 2`) | Scientific data flag | Traced to Zheng 2025 flatus (g = −2.04). Source labels values mean (SD), but the printed P values are incompatible with them. Leave-out diagnostics were added; printed values are unchanged. |
| First triage run joined no full texts (int vs string Covidence ID) | Computational (this run) | Fixed before outputs were used |
| First determinism check hashed 0 files (zsh word-splitting) | Computational (this run) | Re-run with array; 21/21 identical |

## 5. What this does not show

Reproduction starts from extracted values. It cannot detect an extraction that consistently misreads a source, an unreported co-intervention, missing eligible trials (see `PRISMA_REPORT_TRIAL_ACCOUNTING.md`), or the correctness of GRADE and RoB judgments. The dashboard (`dashboard/`, `_site/`) was not rebuilt and is not covered.
