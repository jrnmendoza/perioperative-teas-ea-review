# Dashboard refinement — report (28 September 2026)

A refinement of the deployed v38 dashboard: provenance, reader navigation, study exploration, figure
discoverability, accessibility and tests. No analysis was rewritten and no canonical value changed. The
pre-edit audit is in `DASHBOARD_REFINEMENT_AUDIT.md`.

## 1. What changed

**Study-characteristic provenance (Studies & figures)**
- A legend, "How far each characteristic has been checked", now sits directly under the Study Explorer
  introduction instead of inside a collapsed column chooser. It carries the warning *"Characteristics do not all
  have the same verification level. Registry- and PDF-verified values are distinguished from source-traced,
  legacy and single-extractor fields. Missing values are not inferred."*
- Every status has a plain-language label (Verified — registry; Verified — PDF quotation; Partly verified —
  source excerpt; Canonical result register; Source-traced; Extracted from PDF quotation — single extractor;
  Legacy extraction — not re-verified; Not verified; Not reported in source; Not extracted). Each badge is a
  keyboard-reachable help button in the existing glossary tooltip system (same `.term` element, hover, focus
  and tap, Escape to close). The help text says whether the value was checked against the report, inherited
  from v26, single-extractor, or explicitly not reported (which is a finding about the report, not an
  extraction failure).
- The analgesia, PCA, rescue and cumulative-stimulation fields are stated to be quoted from the PDF
  (machine-checked quotation) but single-extractor, "unless and until they are independently reviewed". This
  appears in the legend and in the study drawer. Their status was not relabelled.
- The legend has a per-field table of verification counts, computed from the characteristics file. Cell badges
  in the table and drawer show the same help on hover and carry the plain label for screen readers. The drawer
  now breaks down its report's fields by status instead of giving one merged count.
- All labels and help text come from one table (`VS` in `interactive_explorer.js`). The contract checks that it
  explains exactly the statuses the characteristics file uses.

**Stata descriptive figures in Studies & figures**
- A new "Evidence base at a glance" section opens the Studies view with the six registered Stata descriptive
  figures (combined panel, year, country, sample size, surgical category, modality × comparator). They are the
  files from `dashboard/current/stata/`, not redrawn. Each card has a preview, an enlarge-in-lightbox button,
  SVG/PDF/PNG downloads, "Generated in Stata", the register's suggested use, a one-line description, and a
  link to the figure register. The section says the bars count reports and test nothing.
- The lightbox now offers SVG/PDF/PNG downloads for every Stata figure, including model figures.
- The Studies view now runs: figures → explorer introduction and provenance legend → filters and presets →
  interactive evidence-base counts → matrix legend → study table with contribution matrix → study drawer.

**Reader-facing model labels**
- One deterministic function (`modelLabel` in `current_review_ui.js`, shared with the explorer) builds labels
  from stored fields. Core models use outcome construct, modality and comparator plus the qualifier the ID
  carries: `opioid24_TEAS_sham` becomes "Cumulative 0–24 h systemic opioid consumption — TEAS vs sham". QoR
  models use their stored label; E2 models use their body and stored E2 label.
- "Model ID: `…`" stays beneath each label. Applied in the Results tables, model selector and model panel,
  sensitivity comparison, GRADE, RoB filter and RoB dialog, result inspector, E1 vs E2 headers, Stata figure
  register, small-study table, and the explorer's cell dialog and study drawer. The browser test confirms the
  mapping is deterministic and injective across all 117 model IDs.

**Navigation**
- The 11 routes are grouped as Evidence (Overview, Results, E1 vs E2, QoR analysis), Explore studies
  (Studies & figures, Outcome coverage, Risk of bias, GRADE) and Review process (PRISMA, Methods, Downloads).
  Route names and every hash URL are unchanged.
- Semantics: option B. The controls are route links (`<a href="#results">`) with `aria-current="page"`. The
  ARIA tab roles are gone, because they promised a tab keyboard model that did not exist. Links can be opened
  in a new tab.
- On first load, focus now stays at the top, so the skip link is the first Tab stop; focus moves to the
  content only on in-page route changes.

**Complete versus outstanding (Overview)**
- Three cards: the evidence inventory; "Complete · v38 core" ("Core v38 RoB 2 and GRADE are complete under the
  adopted workflow…", counts computed from the payload); and "Outstanding", which lists the current-state
  report's outstanding items from `d.outstanding` (not re-typed). Nothing says reviewer approval is awaited.
- An always-open "Limitations that stay in view" list covers: the 12-reference import mapping gap, historical
  selection, reports versus trial families, randomised versus analysed N, source holds, E2 as post hoc, and reproduction
  versus source truth. (On the user's instruction on 28 September 2026, the statements that RoB 2/GRADE
  judgements were AI-conducted were removed from this list, the "Complete · v38 core" card, the Risk of bias
  note, the footer and the no-JavaScript summary.) It is computed from PRISMA counts and the results
  register (e.g. 261 held results in 58 reports, none in any model).

**Build and analysis provenance**
- Overview and footer: "Analytical core: v38 · 20 Sept 2026 · E2 (post hoc): 23 Sept 2026 · Dashboard build:
  <date> · commit <sha>". The core date comes from the payload and the E2 date from the dated decision
  heading in `AMENDED_PRIMARY_ESTIMAND_E2.md` (new payload key `release`). Build date and SHA come from an
  inline copy of `build-meta.json` that `build_site.py` writes into the page, so no SHA is hard-coded. The
  commit links to GitHub. A copy without build metadata says "no build record in this copy".
- The fixed build badge stays for crawlers and is now `aria-hidden` (its text is in the footer).

**Downloads**
- 71 files in 11 categories (review status and decisions; model data; GRADE; RoB 2; E1/E2; QoR; Stata;
  characteristics; outcome coverage; PRISMA; independent reproduction), assigned by fixed source-path rules
  with an "Other" fallback so nothing can drop out. 19 files are badged Primary and the rest Audit. There is a
  search box, a category filter and a "Primary files only" switch, and the browser test checks that every
  download is listed once.

**Forest plots**
- A one-line summary above each browser forest plot: pooled (k, N, REML + safeguarded HK, estimate, unit,
  I², PI where stored), single study (not pooled), plus the −10 mg line where drawn. On phones it adds a
  "scroll sideways" hint. The plots themselves are unchanged.

**Theme**
- New `dashboard/theme.js`, loaded in `<head>` before the stylesheet, so there is no flash of the wrong theme.
  It follows the system preference until the reader chooses, then keeps the choice under the single key
  `teas-ea-review-theme`. The toggle ("Dark theme", `aria-pressed` = dark in effect) now reports the current
  state; it used to report the previous one. It follows system changes when no explicit choice exists.
  Scientific figures are not recoloured.

**Accessibility fixes**
- Glossary and legend tooltips no longer vanish when keyboard focus scrolls them into view, or when a
  resting mouse fires a stray `mouseover`.
- Amber E2 matrix cells and badges use dark text: about 3:1 contrast before, now about 6:1 or better in both
  themes. The "Audit" badge contrast is fixed.
- Small matrix marks (14 px) keep their look but have a 26 px hit area. Column-chooser checkboxes are 18 px
  inside 32 px labels.
- The figure dialog is labelled by its caption. Focus outlines cover every focusable control, including SVG
  study labels.

## 2. What did not change

Confirmed by `git diff origin/main` and the identity contracts. Unchanged: canonical result data, model inputs,
model memberships, effect estimates, confidence intervals, heterogeneity (τ², I², Q, PI), RoB 2 judgements,
GRADE judgements, E1, E2 and the QoR models (24 h and later windows). No file under `03_CANONICAL`,
`02_DECISIONS`, `04_MODELS`, `05_REPRODUCTION`, `07_OUTCOME_COVERAGE`, `08_QOR_ANALYSIS`, `09_E2_ANALYSIS`,
`10_PAIRED_PAIN`, `12_SENSITIVITY_MAP`, `13_STATA` or `14_CHARACTERISTICS` changed. The only
`10_FINAL_ADJUDICATION` change is the page generator (`code/build_current_dashboard.py`).

`dashboard/current_review.json`: all 31 existing keys are byte-identical to `origin/main`. One key was added,
`release` (core version and date, E2 date, QoR date). No discrepancy between display and canonical files was
found, so no scientific value was repaired.

## 3. Scientific integrity checks (final run on the built site)

| Check | Result |
|---|---|
| `build_site.py --out _site` | built |
| `deploy_integrity_check.py --site _site` | PASS: 36 contracts, 28 isolated mutations, 71 download hashes, 253 article-figure files |
| `check_handover.py --mutation-test` | PASS (v38 contract) |
| `check_tab_data.py` | PASS (v38 contract) |
| `check_generated_artifacts.py --fast` | PASS: generated dashboard matches its generator |
| `check_current_dashboard.py` | PASS (as above) |
| `validate_adjudication.py` | OVERALL PASS: 70 reports, 69 trial units, 761 results, 74 models (69 fitted), 177 input contrasts re-derived, 345 refits, 38 GRADE bodies, 155 RoB-linked results, 12,103 operational randomised |
| `check_current_dashboard_ui.cjs --site _site` (new) | PASS: 18 browser checks |

New contract checks, each with a mutation that must fail:
- navigation (routes, groups, link semantics, no ARIA tabs);
- exactly the v38 scripts load, with `theme.js` in `<head>` before the CSS;
- `theme.js` is the only script using storage, with one key and no network calls;
- the explorer legend covers exactly the characteristics status vocabulary;
- release dates derive from the payload and the E2 decision heading;
- the inline build record equals `build-meta.json`, is absent from unbuilt pages, and no commit SHA is
  hard-coded.

New browser test (`scripts/check_current_dashboard_ui.cjs`). It serves the built site itself, and its checks
were proven to fail on three deliberate regressions (legend removed, one download dropped, forest links
broken). It covers:
1. active assets (no `app.js`);
2. build SHA and date from metadata, with graceful degradation when the metadata is missing;
3. grouped navigation, `aria-current`, back/forward, keyboard and visible focus;
4. the complete-versus-outstanding split and the limitations list;
5. model labels (117, deterministic and unique);
6. Stata figures in Studies (all images load; 18 SVG/PDF/PNG links resolve; lightbox);
7. the provenance legend (every status, keyboard tooltip, per-field counts summing to all 1,960 rows);
8. the study drawer (statuses, verbatim quotes, PDF and hash, models, E1/E2, RoB);
9. explorer search and all 10 filters, E1/E2 status filters, presets, chips, URL persistence and reload,
   back/forward, glance bars, compact/detailed matrix, column selection, cell dialog and row drawer;
10. forest contributor by keyboard to the result inspector: result ID, source, SHA-256, unit, conversion
    factor, analysis scale, study estimate, decision, every model, result-specific RoB, and the combined-arm
    note that the control arm is counted once;
11. results, RoB matrix and E2 forest links to study profiles;
12. E1 vs E2 body and membership filters, and the post-hoc label;
13. downloads grouping (none dropped) and filters;
14. theme (system default, persistence, `aria-pressed`);
15. text contrast in dark and light themes;
16. no whole-page horizontal overflow on 11 views at 1440/1024/768/430/390 px, the study drawer on phones,
    and touch targets;
17. no page or console errors.

CI: the browser test was added to the deploy workflow's build job, after the existing gates, using the
runner's installed Chrome through `npm ci`. It also runs on pull requests in a new no-deploy workflow,
`dashboard-checks.yml`.

## 4. Stata reconciliation

Stata was not rerun. All nine hashed Stata inputs are unchanged since the executed run. The descriptive
do-file's columns are byte-identical: only the four new regimen columns changed, and Stata does not read them.

| Item | Value |
|---|---|
| Stata version | StataNow/SE 19.5 (revision 12 Aug 2026), Mac Apple Silicon |
| Models checked | 117 (core 74, E2 25, QoR 24 h 12, QoR later 6) |
| Pooled models verified | 64 |
| Single-study models verified (not pooled) | 48 |
| No eligible data | 5 |
| Discrepancies | 0 |
| Largest relative difference | 9.0 × 10⁻⁷ |
| Figure register | 33 figures × SVG/PDF/PNG; every shipped file equals its registered SHA-256 (contract); the 6 descriptive figures' 18 links resolve in the built site (browser test) |

The contract "Stata reproduces current canonical results" passes, and dashboard work introduced no discrepancy.

## 5. Study-characteristic provenance (70 reports × 28 fields = 1,960 values)

| Status | Values |
|---|---|
| Verified — registry | 731 |
| Legacy extraction — not re-verified (v26) | 692 |
| Extracted from PDF quotation — single extractor | 208 |
| Canonical result register (arm descriptions) | 140 |
| Not reported in source | 72 |
| Source-traced (extraction record) | 71 |
| Verified — PDF quotation | 25 |
| Not verified | 16 |
| Partly verified — source excerpt | 5 |
| Not extracted | 0 |

By field:
- **Registry-verified for all 70 reports:** year, trial family, modality, comparator, comparator class,
  randomised N, operational N, analysed N.
- **Country:** 69 registry, 1 PDF quotation.
- **Procedure:** 69 registry, 1 source-traced.
- **Surgical category:** 70 source-traced.
- **Anaesthesia:** 30 registry, 24 PDF quotation, 16 not verified.
- **Age:** 69 legacy, 1 registry. **Female:** 68 legacy, 2 registry. **BMI, ASA:** 70 legacy each.
- **Acupoints, frequency:** 70 legacy each.
- **Intensity:** 68 legacy, 2 partly verified. **Timing, sessions, session duration:** 69 legacy and
  1 partly verified each.
- **Intervention and control arms:** 70 canonical result register each.
- **Single-extractor PDF quotations (second review pending):**
  - postoperative analgesia: 60 extracted, 10 not reported;
  - PCA regimen: 43 extracted, 27 not reported;
  - rescue analgesia: 35 extracted, 35 not reported;
  - cumulative stimulation duration: 70 extracted.

## 6. Remaining limitations (not claimed as complete)

- Outstanding review deliverables (from `FINAL_CURRENT_STATE_REPORT.md`, unchanged): GRADE for the four
  later-window QoR bodies; structured LOS/PACU/extubation/mobilisation tables; finalised harms and
  satisfaction tables; the reference registry and claim-citation audit extension. None was completed at HEAD.
- The four regimen fields remain single-extractor. The anaesthesia, age, sex, BMI, ASA and STRICTA fields are
  still mostly legacy or not verified.
- The sensitivity parent map remains a proposed display grouping.
- The 12-reference import gap, historical exclusion labels, post-hoc E2 timing and source holds are unchanged
  and remain disclosed on the Overview. The dashboard no longer states that RoB 2/GRADE judgements were
  AI-conducted (removed on user instruction); the regimen-field tooltip still describes that extraction as
  AI-assisted, single extractor.
- The contrast test covers the main text classes, not every pixel. SVG forest text relies on theme variables
  and was checked visually in both themes. The Stata PNG previews sit on white in both themes, by design.
- The repository `venv/` lost scipy on its Python upgrade; the validator ran in a scratch environment.

## 7. Files changed

- `DASHBOARD_REFINEMENT_AUDIT.md` (new), `DASHBOARD_REFINEMENT_REPORT.md` (new)
- `10_FINAL_ADJUDICATION/code/build_current_dashboard.py`
- `dashboard/index.html`, `dashboard/current_review.json`, `dashboard/current_review.js` (regenerated)
- `dashboard/current_review_ui.js`, `dashboard/interactive_explorer.js`, `dashboard/current_review.css`
- `dashboard/theme.js` (new)
- `scripts/build_site.py`, `scripts/check_current_dashboard.py`
- `scripts/check_current_dashboard_ui.cjs` (new)
- `.github/workflows/deploy-pages.yml`, `.github/workflows/dashboard-checks.yml` (new)

## 8. Deployment (28 September 2026)

| Item | Value |
|---|---|
| Pull request | #51 (`dashboard-refinement`), PR check `Dashboard checks (no deploy)` run 36440707735: success, including the 18 browser checks on the GitHub runner |
| Merge commit (deployed) | `2971096` (`2971096bd6d405a683f3c4f833b39ffaed9327de`); tree identical to the tested branch head `d7ced44` |
| Deployment branch | `claude-v26-dashboard-final` fast-forwarded `6619e2a` → `2971096` |
| Pages workflow | run 36443711226: build (all gates plus the new browser test), deploy and live verify all `success` |
| Live build record | `build-meta.json`: `git_commit` `2971096…`, `build_timestamp_utc` 2026-09-28T15:27:36Z, `content_fingerprint` `9dffc2d6eddd` |
| Live URL | https://jrnmendoza.github.io/perioperative-teas-ea-review/ |
| Cache-busting URL | https://jrnmendoza.github.io/perioperative-teas-ea-review/?build=2971096 |

Live post-deployment verification:
- `scripts/verify_deployment.py` (workflow verify job): passed.
- All 71 live downloads and all 99 live Stata figure files (33 × SVG/PDF/PNG) are SHA-256 identical to the
  repository sources and the figure register.
- Live `index.html`, `current_review.js`, `current_review_ui.js`, `interactive_explorer.js`,
  `current_review.css` and `theme.js` are byte-identical to the locally tested build.
- `scripts/check_current_dashboard_ui.cjs` against the live site: 18/18 checks pass. These include no
  whole-page overflow at 1440/1024/768/430/390 px, dark and light contrast, and no page or console errors.
  The Overview and footer show commit `2971096` from the live build record.
- Screenshots checked at 1440 px (Overview) and 390 px (Studies & figures).

This report commit changes only this file, which is outside the workflow's path filter, so pushing it does not
redeploy; the site content is that of `2971096`.
