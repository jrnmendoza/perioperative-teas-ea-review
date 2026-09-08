# Handover — perioperative TEAS/EA systematic review

You are taking over an in-progress systematic review and meta-analysis. You have
the project folder. This document is the state of play, the rules that must not
be broken, and three jobs.

**Project root:** `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026`
**Branch:** `main` (also mirrored to `claude-v26-dashboard-final`, which is what
GitHub Pages deploys from)
**Last commit at handover:** `2455713`
**Live site:** https://jrnmendoza.github.io/perioperative-teas-ea-review/
**PROSPERO:** CRD420251090635

---

## 1. Orientation

### The pipeline — nothing bypasses it

```
TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx   (authoritative master)
   └─ 06_FINAL_ANALYSIS_V26/02_STATA/00_prep_data.do  ─► locked .dta/.csv datasets
        └─ 00_master.do STEPS 1-14                    ─► 03_RESULTS/*.csv
             └─ scripts/build_*.py                    ─► dashboard/*.js (generated)
                  └─ scripts/build_site.py            ─► _site/
                       └─ GitHub Actions              ─► live site
```

The directory is still called `06_FINAL_ANALYSIS_V26` for path stability; it
reads the **v33** master. Don't rename it.

### Key locations

| What | Where |
|---|---|
| Authoritative master | `TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx` |
| Previous master (frozen) | `…_v32_FINAL_LOCK_READY.xlsx` |
| v33 build + QC | `08_V33_MASTER/build_v33_master.py`, `qc_v33_master.py` |
| Secondary analysis sets | `08_V33_MASTER/01_DATA/*.csv` |
| Secondary Stata | `08_V33_MASTER/02_STATA/20_v33_secondary.do` |
| Tiered primary analysis | `07_TIERED_V33/02_STATA/13_tiered_primary_v33.do` |
| Source PDFs | `TEAS EA Verification/Source PDFs/` |
| Generators | `scripts/build_*.py` |
| Gates | `scripts/validate_dashboard.py`, `deploy_integrity_check.py`, `verify_deployment.py`, `08_V33_MASTER/qc_v33_master.py` |

### Stata

`/Users/ryan/bin/stata-se -b do <file>` — StataNow 19.5, the authoritative
inferential engine. **It does not always exit on its own.** Wait for the log's
closing marker (e.g. `SUCCESS:` or `closed on:`) and then kill the process;
don't assume a hung wrapper means a failed run. Check every log for `r(nnn);`.

### Current headline numbers (do not change these without cause)

| | k | Estimate | 95% KH CI | p |
|---|---:|---:|---|---:|
| Primary 0–24 h opioid (combined, contextual) | 7 | −9.907 mg IV MME | −20.079, +0.265 | 0.0545 |
| S0 primary: TEAS vs sham | 4 | −13.995 | −34.181, +6.190 | 0.1145 |
| S0 supportive: EA vs usual care | 3 | −3.936 | −19.773, +11.902 | 0.3969 |

70 canonical studies · 382 outcome rows · strict primary **k = 7**.

---

## 2. Rules that must not be broken

These are enforced by automated gates. If you find yourself wanting to edit a
gate so your change passes, stop — that is the signal that the change is wrong.

1. **v32 and v33 masters are immutable.** v32's sha256 is
   `74fda7d176fae15af4aa5bbff318514f998adcf957a2f9cad67e8de55ab7b12f` and is
   asserted before and after every build. New data goes into a **new** master
   (v34), never into v33.
2. **Strict primary k must remain 7.** If your work would change it, **stop and
   produce a written justification before proceeding.** This is a hard gate.
3. **Never manufacture MME.** Not from PCA reservoir volume, not from binary
   rescue incidence, not from median rescue counts, not from mg/kg × a body
   weight, not from PCA presses.
4. **Never convert median/IQR to mean/SD** for pooling. Median/IQR evidence is
   reported in parallel, in its own units.
5. **Never read a number off a graph.** Graph-only stays graph-only.
6. **Never pool across estimands**: binary rescue *use* ≠ opioid *dose*;
   intraoperative ≠ postoperative; PCA presses ≠ drug consumption; opioid rescue
   ≠ NSAID rescue; QoR-40 ≠ QoR-15; POD1 ≠ an explicit 0–24 h clock window.
7. **Multi-arm trials contribute one contrast per model.** A shared control is
   never counted twice. See `MULTIARM_PICK` in
   `08_V33_MASTER/build_v33_analysis_sets.py`.
8. **No number is hardcoded into the dashboard markup.** Everything is generated
   into `dashboard/*.js` and rendered. The validator fails the build otherwise.
9. **RoB 2 is result-specific.** A judgement for one outcome does not transfer
   to another outcome in the same trial.
10. **A sensitivity analysis crossing p = 0.05 does not change a conclusion.**
    These analyses exist to test robustness, not to find significance.

### Working style that the gates assume

Every new check must be **mutation-tested**: deliberately break the thing it
guards, confirm that check fails and that others don't, then restore. Several
real defects in this project were caught only that way — including a validator
function that silently shadowed another of the same name while the suite still
reported all-pass.

---

## 3. Job A — ingest the new extraction data into v34

The user is having a second extractor complete the outstanding source
extractions. The brief they were given is
`08_V33_MASTER/CHATGPT_EXTRACTION_PROMPT.md` — read it first; it defines the
exact CSV schema you will receive and the codes used for missing data
(`NOT REPORTED`, `GRAPH ONLY`, `NO VARIANCE`, `NO DENOMINATOR`, `AMBIGUOUS`).

It covers 17 studies: Zhu 2022, Yang 2020, Pan 2023, Lu 2022, Li 2021, Gu 2019,
Huang 2025, Gao 2021, Jiang 2026, Wang 2023, Tu 2024, Sun 2017, Sim 2002,
Lu 2021, Long 2025, Wang 2024, Zheng 2025.

### What to do

1. **Do not trust it on arrival.** Re-verify a sample against the PDFs in
   `TEAS EA Verification/Source PDFs/` before ingesting anything — at minimum
   every row that would enter a pooled model, and every row that contradicts
   something already in v33. Extracting from these papers surfaced two genuine
   source contradictions and one near-duplicate that looked like a duplicate and
   was not; assume more of the same.
2. **Build v34 the way v33 was built.** Copy
   `08_V33_MASTER/build_v33_master.py` as the pattern. Critically, it
   **materialises cached formula values before saving** — v33 contains formula
   cells whose cached results openpyxl discards on save, and without that step
   you will silently blank the derived-effect columns of ~190 rows. Keep that
   code.
3. **Run duplicate detection on the composite key** (study + outcome family +
   outcome/result + timepoint + intervention arm + comparator arm) before
   appending. Never match on study name alone — `He 2026 (breast/WJCO)` and
   `He 2026 (hepatectomy/JIS)` are different trials, and a stem match on
   "He 2026" has already caused one real bug in this project.
4. **Add `v34_Change_Log` and `v34_Supplement_Reconciliation` sheets**, matching
   the v33 pattern, so every row's disposition is auditable.
5. **Port and extend the QC gate** (`qc_v33_master.py` → `qc_v34_master.py`).
   All 26 existing checks must still pass, plus new ones for whatever the new
   data introduces.
6. Then re-run the full pipeline, regenerate the dashboard layer, and re-verify.

### Watch for specifically

- **Gu 2019** — if a *numeric* 24-hour PCIA value turns up in the text or
  supplement, that converts a rejected graph-only outcome into usable evidence
  and would change the S3 tier analysis in `07_TIERED_V33`. Read
  `07_TIERED_V33/03_DIGITIZATION/gu2019_digitization_QC.md` first: a digitization
  was attempted and **failed validation** (control arm overestimated by up to
  16%), so a figure-derived value is not acceptable — only a printed one.
- **Huang 2025's rescue drug is ketorolac**, an NSAID. It must not join any
  opioid-rescue analysis.
- **Sun 2017** currently gives only percentages (11.0%, 15.4%, 7.9% vs 23.3%).
  Without raw numerators and denominators it cannot enter a binary model.
- **Wang 2024** has two PONV risk strata with separate control arms — keep them
  separate; they are not a shared-control multi-arm situation.

---

## 4. Job B — ingest result-specific RoB 2

The brief given to the assessor is `08_V33_MASTER/CHATGPT_ROB2_PROMPT.md`. The
gap register is `08_V33_MASTER/01_DATA/v33_rob2_gap_register.csv` — **18 study ×
result pairs** whose RoB 2 currently borrows a judgement made about a *different*
outcome in the same trial.

The primary model is **not** affected: all 7 contributing trials have the 0–24 h
opioid result itself assessed. The gap is in the secondary analyses (binary
rescue opioid use 3/3 borrowed; intraoperative remifentanil 8/9; intraoperative
sufentanil 4/6; QoR-40 1/3; first defecation 2/8).

### What to do

1. **Treat the returned judgements as drafts, not as the review's RoB 2.**
   Cochrane requires two independent human assessors reaching consensus. Store
   them in a clearly-labelled sheet — `v34_RoB2_Draft` or similar — with an
   explicit `adjudicated_by` column that stays empty until a human signs off.
   **Do not merge unadjudicated drafts into `Corrected_RoB2`.**
2. `Corrected_RoB2` currently holds **one result per study**. Extending it to
   multiple results per study is a schema change: either add a `Result ID` key
   and allow multiple rows per study, or create a parallel result-level sheet.
   Whichever you choose, update every consumer and make the validator assert
   that each analysed result resolves to a RoB row **for that result**.
3. **Until adjudication, the secondary analyses must not be GRADE-rated.** They
   are currently presented on the dashboard as source-verified results with
   provenance, which is the defensible position. Don't upgrade that framing on
   the strength of a draft.

---

## 5. Job C — dashboard coherence and broken tabs

I diagnosed the dashboard before handing over. All 14 tabs switch and render
without JavaScript errors, so the failures are **silent** — every one is hidden
behind an `if (el)` or `|| []` guard. Here is the actual defect list.

### C1. Author Outreach table is completely empty (Limitations tab) — REAL BUG

`dashboard/author_inquiries.json` exists (60 records, 105 KB) and is read
server-side by `scripts/build_primary_pathway.py`, but **it is never loaded into
the page.** There is no `<script>` tag and no fetch, so `window.AUTHOR_INQUIRIES`
is `undefined`, `renderInquiriesView()` falls through `|| []`, and
`#inquiries-table-body` renders **zero rows**. The priority filter buttons and
the search box above it are therefore also inert.

Fix: generate `dashboard/author_inquiries.js` (a `window.AUTHOR_INQUIRIES = […];`
wrapper) from the JSON via a small script in `scripts/`, load it in
`index.html`, and register it in `CACHE_BUSTED_ASSETS` in `build_site.py`.

### C2. Search strategy display is empty (Search tab) — REAL BUG

`window.SEARCH_STRATEGIES` is **never defined anywhere in the project**.
`renderSearchStrategies()` returns early at `app.js:386`, so
`#search-db-buttons` has 0 children and `#search-strategy-code-display` is
empty. The tab shows its concept-map table and nothing else.

The real data exists as authoritative text files in `01_search_strategy/`:

```
01_search_strategy/cochrane/2026-07-21/CENTRAL_search_strategy_2026-07-21.txt
01_search_strategy/cinahl/2026-07-23/CINAHL_search_strategy_2026-07-23.txt
01_search_strategy/embase/2026-07-22/EMBASE_search_strategy_2026-07-22.txt
01_search_strategy/pubmed/…
01_search_strategy/master/search_concept_map.md
01_search_strategy/master/search_decision_log.md
```

Fix: generate `dashboard/search_strategies.js` from those files — database name,
strategy date, verbatim strategy text, and the result count if recorded in the
decision log. **Transcribe the strategies verbatim; do not paraphrase or
reformat them.** A published search strategy must be reproducible exactly.

### C3. Orphaned KPI elements — REAL BUG (silent partial render)

`app.js` writes to three IDs that **do not exist** in `index.html`:

| ID | Referenced at | Consequence |
|---|---|---|
| `kpi-patient-count` | `app.js:692` | The patient KPI card shows its subtitle ("10,678 randomized surgical patients") but no headline number |
| `kpi-i2` | `app.js:706` | No I² headline value |
| `kpi-i2-sub` | — | No I² subtitle |

Decide deliberately: either add the missing card markup so the KPI row is
complete, or delete the dead code in `app.js`. **Do not leave it half-wired.**
If you add an I² card, its value must come from the generated data layer, not be
typed in.

### C4. Coherence pass

The Primary tab has grown three stacked panels that overlap in purpose and
should be sequenced so a reader moves through one argument:

1. **Study Contribution Map** (`renderV33`) — why 70 included trials give k = 7
2. **Primary Outcome Contribution Pathway** (`renderPrimaryPathway`) — which
   trials carry 24-h information and why they do or don't qualify
3. **Tiered derivability panel** (`renderTieredV33`) — of those that do, what
   can be pooled without a prohibited assumption

They currently appear in a different order and repeat some framing. Reorder and
de-duplicate, but **keep every substantive caveat** — particularly the
empty-cell statements ("no sham-controlled EA trial reports this outcome, k=0"),
the legacy-reconstruction labels on Coura 2011 and Sim 2002, and the Zhang 2025
withdrawal note. Those exist because the numbers were once presented without
them.

Also worth doing: the Secondary tab's interactive forest selector lists outcomes
that the v33 secondary analyses now cover (rescue analgesia, intraoperative
remifentanil). Check it reads from the generated layer rather than a separate
hardcoded list, and reconcile if not.

### How to verify dashboard work

Don't trust "the tab loads". Test that every element a renderer targets is
actually populated after its tab is activated:

```javascript
// switch through every tab, then check each render target is non-empty
```

That is how C1–C3 were found — all three pass a naive "does the tab render"
check.

---

## 6. Gates you must keep green

| Command | Expect |
|---|---|
| `python3 08_V33_MASTER/qc_v33_master.py` | 26/26 (write a v34 equivalent) |
| `python3 scripts/validate_dashboard.py` | 60/60 |
| `python3 scripts/build_site.py && python3 scripts/deploy_integrity_check.py` | all pass |
| `python3 scripts/sync_master_results.py --check` | in sync |
| Stata logs | zero `r(nnn);` across all logs |

`scripts/verify_deployment.py --commit <sha>` runs post-deploy against the live
site. Both it and `deploy_integrity_check.py` now **derive** the expected master
version and outcome-row count from the workbook the build used — do not
reintroduce hardcoded expectations there.

Deployment is by pushing to `main` **and** `claude-v26-dashboard-final`; the
workflow triggers on the latter. If you touch a script not listed in the
workflow's `paths:` filter, add it, or your change will not trigger a rebuild —
that has already bitten twice.

---

## 7. Reporting conventions

Commits are structured, one per phase — data integration, reanalysis, dashboard.
Commit messages state what changed, what was found, and what was deliberately
not done. The reports in `08_V33_MASTER/` (`V33_INTEGRATION_REPORT.md`,
`V33_SOURCE_QC_REPORT.md`, `V33_ANALYSIS_CHANGELOG.md`,
`V33_ANALYSIS_QC_REPORT.md`, `V33_DASHBOARD_UPDATE_REPORT.md`) are the model —
write v34 equivalents.

Two habits worth continuing:

- **Record what you did not do, and why.** The not-pooled register
  (`08_V33_MASTER/01_DATA/v33_not_pooled_register.csv`) is rendered on the
  dashboard so exclusions are visible rather than implicit.
- **State fragility next to the result.** The binary rescue-opioid RR is
  significant (p = 0.014) but Yu 2020 carries 80.8% of the weight and
  leave-one-out breaks it; that caveat sits beside the number on the dashboard.
  Keep that standard.

---

## 8. Open items inherited

1. 18 result-specific RoB 2 assessments pending adjudication (Job B).
2. 17 extraction targets pending (Job A).
3. **Yu 2020** — internal source contradiction: Table 2 gives TEAS VAS SDs
   1.53 / 0.98, the abstract gives 1.41 / 0.88, and the Results text says
   P = 0.26 for POD2 while the table stars it P < 0.05. Rows are marked
   `CONFLICTED` and pooled nowhere. Needs author contact.
4. **Liang 2021** — "postoperative analgesia requirement" 3.8 (1.9) vs 5.0 (2.9)
   is described in the source as a count of patients, which 3.8 out of 35 cannot
   be. Held; needs author contact.
5. **Yeh 2010 / Yeh 2011** — publication-family overlap unadjudicated; treated as
   one study unit.
6. **Gu 2019** — digitization failed validation; still graph-only.
7. Whether the intraoperative-opioid analyses belong in the review at all, given
   they answer a different question from its primary aim.

---

## 9. If something looks wrong

Several things in this project look like errors and are not — and one thing that
looked like a coincidence was real. Before "fixing" any of these, read the
documentation:

- **Yao 2015 and Chen 2015 both report median 1 vs 3.5 rescue at P = 0.004.**
  They are genuinely different trials from the same Fujian group (gynaecological
  laparoscopy n = 35/36 vs thyroidectomy n = 41/42). Verified from both PDFs. Do
  not merge them.
- **`06_FINAL_ANALYSIS_V26` reads the v33 master.** The name is historical.
- **The combined k = 7 primary estimate is labelled "supporting/contextual",**
  not the headline. v33 reports TEAS-vs-sham (k = 4) and EA-vs-usual-care
  (k = 3) separately because pooling them averages two different questions.
- **Zhang 2025 is excluded from all 0–24 h analyses** including the scale-free
  SMD. POD1 is not an explicit clock window, and an SMD changes the unit, not
  the estimand.
