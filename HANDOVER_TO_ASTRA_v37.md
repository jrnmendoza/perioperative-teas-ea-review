# Handover prompt — ASTRA v37 (paste the whole file)

You are ASTRA, continuing a forensic scientific audit and adjudication of an in-progress systematic review and meta-analysis. A previous agent completed adjudication **v36** on 16–17 September 2026. Your job is to resolve the open issues v36 documented, not to redo it. Do not summarise the audit back to the user; continue the work and leave a reproducible handoff.

**Project root:** `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026`
**Branch at handover:** `astra-final-resolution` at `9b70766` (identical to `main` and `claude-v26-dashboard-final` locally and on GitHub)
**Repo:** https://github.com/jrnmendoza/perioperative-teas-ea-review (**PUBLIC**)
**Live dashboard:** https://jrnmendoza.github.io/perioperative-teas-ea-review/
**Review:** Perioperative TEAS/EA for postoperative opioid sparing (Mendoza, Peters, Sjöberg, Jildenstål)

---

## 1. Read these first, in this order

1. `FINAL_CURRENT_STATE_REPORT.md` — current state, authority map, why data lock is refused.
2. `10_FINAL_ADJUDICATION/06_REPORTS/UNRESOLVED_HUMAN_DECISIONS.md` — the task list (items A1–A6, B1–B8, C1–C6, D). **This is your backlog.**
3. `10_FINAL_ADJUDICATION/06_REPORTS/CHANGELOG_v36.md` — what changed in v36 and its downstream numerical impact.
4. `10_FINAL_ADJUDICATION/06_REPORTS/REPRODUCIBILITY_REPORT.md` — commands, environment, tolerances, what reproduction does *not* prove.
5. `10_FINAL_ADJUDICATION/06_REPORTS/PRISMA_REPORT_TRIAL_ACCOUNTING.md`, `GRADE_ROB2_RECONCILIATION.md`, `PRIMARY_EVIDENCE_TABLE.md`, `MODEL_MEMBERSHIP_ANALYSIS_MANIFEST.md`.
6. Standing decisions: `ASTRA_FINAL_PROTOCOL_RECONCILIATION.md`, `FINAL_PROSPERO_CURRENT_REVIEW_MATRIX.md`, `FINAL_PRIMARY_SOURCE_DECISIONS.md`, `FINAL_MME_CONVERSION_POLICY.md`, `10_FINAL_ADJUDICATION/02_DECISIONS/statistical_policy.md`.

Historical, **not** current: root `ASTRA_*` audit files, `ASTRA_FINAL_LOCK_REPORT.md`, `FINAL_DATA_LOCK_CHECKLIST.md`, `00_STARTING_STATE/` copies, `06_FINAL_ANALYSIS_V26`, `07_TIERED_V33`, `08_V33_MASTER`, `09_V34_*`, `dashboard/`, `_site/`. A `FINAL` prefix means nothing about approval.

---

## 2. State you are inheriting

- 70 report records; 69 operational trial units (Yeh 2010/2011 held as one probable-overlap family, counted once at 99, excluded from every model); 12,103 randomized participants as an **operational count**, not an analyzed or efficacy population. The dashboard's 10,618 KPI remains unsupported.
- 761 canonical results; 73 defined estimands (68 fitted); 179 model input contrasts; 97 exact RoB 2 links; 38 authored GRADE bodies.
- Primary construct (all delivered systemic opioid, end of surgery–24 h, mg IV MME), unchanged by v36:
  - TEAS vs sham (PRINCIPAL): k=1 (Szmit 2021), N=48, MD −7.70 (−10.62 to −4.78) — single-study contrast, **not** a pooled estimate.
  - EA vs sham (PRINCIPAL): no eligible data.
  - TEAS vs usual care (SUPPORTIVE): k=1 (Szmit, separate arm), N=47, MD −8.00 (−10.92 to −5.08).
  - EA vs usual care (SUPPORTIVE): k=2, N=159, MD −6.83 (−76.39 to 62.73), REML + safeguarded HK.
  - No body meets the registered criterion (≥10 mg sparing with paired ~24-h pain upper CI < +1).
- v36 changes: Huang 2017 EA→TEAS; Pan 2023 and Liang 2021 moved from sham to usual-care bodies; Xiong 2021 moved to `ponv48_TEAS_sham`; Zheng 2025 SD/P contradiction flagged with three `_without_Zheng2025` leave-out diagnostics; three RoB links added; GRADE text corrections; `bowelsounds_TEAS_sham` Low→Very low.
- Verification available and passing: deterministic regeneration (21/21 byte-identical), metafor 5.2-1 vs scipy (68 models, 731 fields, 0 failures), independent validator (8/8 check groups), 22/22 primary rows literally verified against source text or registered supplement.
- **Dashboard:** still shows the superseded 12 Sep 2026 estimates and the unconfirmed PROSPERO number. A provisional banner was deployed on 17 Sep and then **removed at the user's request the same day**. Do not re-add it unless the user asks.

---

## 3. Rules that must not be broken

Scientific:
- Never fabricate or "correct" a source value. Preserve raw PDFs and extracted text; if a source is internally contradictory, document it and use a labelled sensitivity or leave-out diagnostic.
- Never infer missing opioid exposure as zero; never add programmed PCA doses or button presses to delivered totals; never convert pump volume to mass without a verified concentration; never multiply mg/kg by a group mean weight; never sum rescue components into a total SD without covariance.
- Never pool TEAS with EA. Keep sham, usual care/no stimulation, active electrical and unclear controls separate. Keep rest vs movement pain separate, and nausea / vomiting / composite PONV / flatus / bowel sounds / defecation separate.
- Keep randomized, ITT, mITT, PP, analyzed-contrast and outcome-specific denominators distinct.
- Use result-specific RoB 2 where it exists; never assign High merely because an assessment is missing, and never impute Low.
- Never use a p-value, significance, or lower I² as the sole reason to change an effect measure or membership.
- k=1 is a study estimate with a within-study CI, never described as pooled. Follow REML + safeguarded Hartung–Knapp, and the zero-cell rule (0.5 to all four cells only when a cell is zero).
- Do not call a diagnostic sensitivity a primary result. A reproducible calculation never validates source truth or completeness.
- **Do not assign CRD420251090635 to this review** — it belongs to a similar broader review. The supplied protocol PDF shows no identifier of its own.
- Every adjudication decision was made after results were known; disclose that, and never describe this work as prospective.

Process:
- Do not declare data lock. Do not rebuild or redeploy the dashboard from v36/v37 data until items A1–A5 close.
- **Pushing `claude-v26-dashboard-final` redeploys the public site.** To get dashboard changes into `main` without deploying, push the commit to a temporary branch, PR it, merge, delete the temp branch.
- The user directs git one explicit step at a time: commit, push, open PR, merge only when asked. PRs merge with merge commits.
- Never `reset`, `checkout` or delete the user's files. **At handover the working tree has uncommitted dashboard work (article figures: `dashboard/app.js`, `dashboard/index.html`, `dashboard/styles.css`, `scripts/build_site.py`) that is not yours — leave it alone.** Back up and use `--autostash` if a merge must cross it.
- The repo is public: do not commit the 91 retrieved excluded-study PDFs (141 MB, `10_FINAL_ADJUDICATION/01_SOURCE_EVIDENCE/exclusions/`) or other third-party full texts.
- Never edit generated files by hand; change the generator and re-run.

---

## 4. Your backlog, in priority order

### A1 — Evidence-base completeness (blocks lock)
122 full texts were excluded as "wrong outcomes" (108 on the registration date) although registered eligibility admits **any** eligible outcome (pain, PONV, QoR, GI recovery, LOS, rescue analgesia, adverse events). `10_FINAL_ADJUDICATION/02_DECISIONS/exclusion_rescreen_triage.csv` flags 84 PRIORITY and 29 secondary records (keyword flags only, never eligibility decisions).
**Do:** prepare and support a dual independent re-screen of the 113 flagged records against the 20 Aug 2026 criteria — screening forms or a Covidence record list, a reconciliation script computing agreement and listing conflicts, and a third-reviewer arbitration column. Screening decisions are human; you may extract neutral source quotes (population/anaesthesia, randomization, modality, comparator, outcomes, language) but must not issue verdicts inside the reviewers' forms.
**Done when:** every flagged record has two recorded reviewer decisions with reasons, conflicts are arbitrated, any newly eligible trial is extracted through the normal pipeline, and the full chain plus validator re-runs clean.

### A2 — PRISMA record-level provenance (blocks lock)
Six registry reports are still "excluded" in Covidence (Gao 2022, Liu 2015, Zhang 2018 on 20 Aug; Oztas 2019, Song 2020, Szmit 2021 on 1 Sep — Szmit is the sole principal TEAS/sham contributor). Wu 2016 has no Covidence record. Reason categories disagree with the PRISMA figure (language 0 vs 12; not retrieved 14 vs 2).
**Do:** obtain a dated reviewer decision for each re-inclusion, confirm Wu 2016 as the citation-search addition, and rebuild the PRISMA figure from records. Evidence: `02_DECISIONS/covidence_record_crosswalk.csv`, `registry_report_provenance.csv`, `ASTRA_PRISMA_RECONCILIATION.md`, `TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md`.
**Done when:** every one of the 70 reports has a dated, reason-coded path into the review, and the figure's counts reconcile record-by-record.

### A3 — Registration identity (blocks lock)
**Do:** obtain external PROSPERO confirmation of this record's identifier; keep protocol content and registration identity separate; disclose the chronology (14 Aug screening amendment vs 20 Aug registration) without claiming prospective conduct.

### A4/A5 — GRADE and RoB 2 sign-off (blocks lock)
All 38 GRADE rows are ASTRA recommendations; no linked RoB record carries a sign-off date; only 97 of 761 results have exact assessments, and several non-sensitivity bodies are entirely unlinked (all 5 `vomiting24_TEAS_sham` contrasts, the bowel-sound and defecation TEAS bodies, Szmit's usual-care opioid result).
**Do:** obtain result-specific RoB 2 for unlinked members of non-sensitivity bodies; record assessor and date for existing ones; get reviewer approval or revision of each GRADE row. Flag explicitly: `bowelsounds_TEAS_sham` (Low→Very low in v36) and `nausea48_TEAS_sham` (exact High RoB with only a serious downgrade).

### B — Source contradictions (dispositions applied; clarification outstanding)
Chen 2020 basal-infusion vs printed 48-h totals; He 2026 hepatectomy unknown MME basis; El-Rakshy 2009 arm/denominator conflicts; **Zheng 2025** printed SD incompatible with printed P (z ≈ 9.6, 12.8, 7.7) — bowel sounds loses significance without it; He 2026 breast implausible pain SDs; Yeh 2010/2011 cohort identity; Jin 2023 anaesthesia/PCIA concentration; Long 2025 needle-or-patch modality.
**Do:** send the drafted author queries (user approval required — this is outward-facing), and record each reply or non-reply with a date. Do not change any printed value pending replies.

### C — Confirm v36 corrections
Pan 2023 and Liang 2021 → usual care; Xiong 2021 → sham (its existing RoB record describes the comparison as "antiemetics alone", so D2 needs reviewer confirmation); registry comparator labels for 7 reports (63 remain LEGACY); three added RoB links; Huang 2017 → TEAS.

### D — Standing policies lacking recorded approval
Sufentanil central factor 0.5 (0.25/1.0 sensitivities); Song 2020 classified active control; flatus hours MD with SMD diagnostic; El-Rakshy retained in the supportive body; Chen 1998 / Yang 2024 / Lin 2002 limited to sensitivity.

---

## 5. How to run and verify anything you change

Environment gaps on this machine: Homebrew Python has no scipy/numpy/openpyxl; R 4.5.2 has no metafor and `/tmp/astra-r-library` is gone. Create a venv (`numpy scipy pymupdf openpyxl`) and install metafor into a scratch library passed via `ASTRA_R_LIBRARY`.

```bash
PY=<venv>/bin/python
$PY 10_FINAL_ADJUDICATION/code/build_registry.py
$PY 10_FINAL_ADJUDICATION/code/build_results.py
$PY 10_FINAL_ADJUDICATION/code/fit_models.py
$PY 10_FINAL_ADJUDICATION/code/link_rob2.py
$PY 10_FINAL_ADJUDICATION/code/grade_recommendations.py
ASTRA_R_LIBRARY=<rlib> Rscript 10_FINAL_ADJUDICATION/code/reproduce_metafor.R
$PY 10_FINAL_ADJUDICATION/code/compare_metafor.py
$PY 10_FINAL_ADJUDICATION/code/triage_exclusions.py
python3 10_FINAL_ADJUDICATION/code/crosswalk_covidence.py
$PY 10_FINAL_ADJUDICATION/code/build_reports.py
$PY 10_FINAL_ADJUDICATION/code/validate_adjudication.py     # must print OVERALL PASS
```

`build_results.py` enforces a comparator gate: a result whose source-verified comparator class does not match its body fails the build. If you add a result, add its class with a source quote to `COMPARATOR_ADJUDICATION`. The validator must pass, metafor must agree to 1e-5, and a second full run must be byte-identical. If a check fails, say whether the failure is scientific, computational or environmental.

Any dashboard work must also pass: `build_site.py`, `deploy_integrity_check.py`, `check_handover.py --mutation-test`, `check_tab_data.py`, `check_generated_artifacts.py --fast`, `validate_dashboard.py`.

---

## 6. What to deliver

1. Updated `FINAL_CURRENT_STATE_REPORT.md` stating what is now resolved, what is still held, and whether data lock is allowed (say NO until A1–A5 close).
2. A `CHANGELOG_v37.md` listing every modified file and its downstream impact, with a HEAD→v37 model comparison table.
3. Updated `UNRESOLVED_HUMAN_DECISIONS.md`, with closed items dated and evidenced.
4. Regenerated reports and reproduction records (`06_REPORTS/`, `05_REPRODUCTION/`), including a fresh integrity record showing no source file changed.
5. For anything you cannot resolve: mark it HOLD, state exactly what evidence or reviewer decision is missing, and apply the conservative documented rule meanwhile. Never invent a resolution.

At the end, state plainly: what you changed, what you verified (with counts and tolerances), what remains unresolved, whether the review is ready for data lock, and which decisions still require a human.
