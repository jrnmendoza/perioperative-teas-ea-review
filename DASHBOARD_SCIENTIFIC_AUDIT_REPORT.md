# Dashboard Scientific Audit Report

Prepared 2026-09-10, against commit history ending `[see changelog]`. Scope: a
P0 scientific-consistency pass against the 54-phase audit brief, not a full
implementation of all 54 phases in one session — see "Scope of this pass"
below before reading the table.

## Scope of this pass

The brief's P0 list (10 items) was checked item by item against live
authoritative sources. Three were real, previously-unfixed defects and are
resolved below. Four were checked computationally and found **already
correct** from earlier work in this project's history — they are recorded as
verified-clean, not re-done. Two required a judgement call with no single
source-supported answer; both are flagged rather than guessed at, per the
brief's own rule ("When uncertain: FLAG — DO NOT GUESS"). One (Stata
verification of the headline results) was already confirmed earlier in this
project's history and re-checked here.

The brief's P1–P3 items (RoB 2/GRADE interactivity, forest-plot hover context,
tooltip glossary, mobile/accessibility refinement, full structured-metadata
templating) are **not** covered by this pass. Several of their stated goals —
a Manuscript Lens, Results-safe/Discussion-safe/Do-not-say statements, claim
boundaries, a Reviewer Lens, reviewer-question-to-evidence pathways, a
Manuscript Evidence Map, team discussion prompts, strict evidence/interpretation
separation, and stale-interpretation detection — already exist on this
dashboard from prior work and are not rebuilt here; see
`09_V34_ANALYSIS/05_INTERPRETATION/build_interpretation_layer.py` and the
Manuscript Lens toggle on the Primary tab. This report does not claim P1–P3
complete; it is out of scope for this pass and is not represented otherwise
anywhere in this document.

| Issue | Severity | Section | Current state | Authoritative evidence | Resolution | Verified |
|---|---|---|---|---|---|---|
| EA-vs-usual-care model labelled `role: "PRIMARY"` alongside TEAS-vs-sham | **P0** | Primary tab, headline KPI card, GRADE Summary of Findings, interpretation layer | Fixed | PROSPERO synthesis strategy, verbatim: "Primary comparisons will be TEAS versus credible sham TEAS and EA versus sham EA. Supportive comparisons will evaluate TEAS and EA against usual care..." No sham-controlled EA trial reports this outcome in absolute IV MME (the only EA-vs-sham/placebo opioid contrast, Sim 2002, is weight-normalised mg/kg and feeds the Tier E SMD synthesis, not this model) | Relabelled to "Supportive evidence — EA vs usual care (no-stimulation comparator)"; `role` changed `primary`→`supporting` at the true source (`scripts/build_v34_dashboard_data.py` `MODEL_META`), regenerated forward; headline KPI card's three branches (all/TEAS/EA) rewritten to state the hierarchy and the insufficient-sham-EA-evidence caveat explicitly | 85/85 `validate_dashboard.py` checks; 7/7 Playwright suites; fingerprint-based staleness unaffected (0 stale) |
| PRISMA exclusion-reason gloss "(no 24h opioid/pain)" narrows the true eligibility framework | **P0** | PRISMA tab, "Reports Excluded" card | Fixed | PROSPERO's eligible-outcomes list is broad: opioid, pain, PONV, rescue analgesia, QoR, GI/functional recovery, LOS, persistent opioid use, adverse events — not only 24-h opioid/pain | Gloss changed to "no eligible perioperative outcome reported" with a tooltip naming the full eligible-outcome framework. Count (117) and category name ("Wrong outcome") **unchanged** — no source evidence the count itself is wrong | 85/85 checks; no test asserted the old string |
| Combined TEAS+EA k=7 synthesis competing visually/conceptually with the TEAS primary | **P0** | Primary tab | **Already correct** — not a defect | `STATA_MASTER_RESULTS["AN-01-COMB"].role === "SUPPORTING COMBINED"`, name "SUPPORTING COMBINED SYNTHESIS", prose already states "TEAS and EA differ in intervention delivery and comparator structure" and "the sham-controlled TEAS model is the primary analysis and the usual-care EA model is reported separately as supportive" | No change made | Read directly from source; verified live |
| Clinical Importance Studio quadrant counts inconsistent with paired k | **P0** | Clinical Importance Studio | **Already correct** — not a defect | `renderMCIDStudio()` computes `validStudies` from live per-study `mcid.is_paired`/`opioid_md`/`pain_md` fields and assigns each study to exactly one of 4 groups; counts and percentages are therefore consistent with paired-k by construction, not by coincidence | No change made | Computed live in a headless browser against the built site: paired k = 6, quadrant counts 3/0/3/0 sum to 6, percentages sum to 100.0% |
| Time-to-first-flatus N discrepancy (494 vs 596) | **P0** | GI recovery / Target E | **Already resolved** in earlier work | `scripts/validate_dashboard.py` bans `"N = 494"` outright and requires the hero card to show the source-re-derived `N = 596` | No change made | 85/85 checks include this guard; confirmed it still passes |
| Clinical-threshold wording contradicting itself (e.g. "below threshold" + "exceeds threshold" for the same ~9.91 mg estimate) | **P0** | Clinical Importance Studio / headline card | **Not found** | Searched all threshold-adjacent text for the described contradiction pattern | No change needed | Grep-verified absent |
| Stale k=6/k=7 narrative text | **P0** | Multiple (forest plots, meta-regression, moderator tables) | **Spot-checked, no genuine staleness found** | Every k=6 occurrence found is a legitimate different population (leave-one-out excluding one High-RoB trial; a 6-of-7 moderator subgroup; the paired opioid+pain MCID cohort, which the brief itself anticipated: "Some k=6 references may legitimately refer to paired opioid + pain study populations") | No change made — replacing correct, distinguished k=6 references with k=7 would itself introduce an error | Read against source; cross-checked against the Stata logs already verified earlier in this project |
| v26/v32/v33/v34 version labels co-occurring on the Primary results tab (20/0/29/14 mentions respectively) | **P1** (flagged, not resolved) | Primary tab | Open | Each version number represents a genuinely distinct, currently-active analytical layer (v26 locked primary results; v33 tiered secondary/derivability framework; v34 RoB2/GRADE/interpretation layer) rather than superseded duplicates — collapsing them into one version banner without a specific information-architecture decision risks misattributing which layer produced which figure | **Flagged, not guessed at.** No single source-supported consolidation exists; this needs a product decision, not a data fix | N/A — deliberately deferred |
| Headline results verified against Stata | **P0** | Primary tab | Already verified | `06_FINAL_ANALYSIS_V26/02_STATA/logs/01_opioid24_primary.log` forest block: TEAS k=4 MD −14.00 [−34.18,+6.19]; EA k=3 MD −3.94 [−19.77,+11.90]; combined k=7 MD −9.91 [−20.08,+0.27] | No change needed | Re-confirmed this pass against the live `v34_data.js` model values, which match to 4 decimal places (−13.9953, −3.9358, −9.9070) |

## Findings from earlier in this project's history that remain live and relevant

Two P0-class scientific defects were found and fixed **before** this pass, in
the same session, and are recorded here because they bear directly on this
audit's P0 "verify headline results" and "resolve discrepancies" mandate:

1. **Three reported, GRADE-rated analyses pool across the protocol's modality
   and comparator boundaries** (AN-02 Target A 0–48h opioid; AN-06 PONV 0–48h;
   AN-07 Target E flatus). `05_ponv.do` and `06_flatus.do` pool on endpoint
   alone, with no modality or comparator condition, contrary to the locked
   scope ("TEAS and EA analyses are stratified by modality... remain separate
   from sham-controlled evidence") and PROSPERO ("TEAS and electroacupuncture
   (EA) will not be combined in a pooled estimate"). All three now carry a
   visible warning in the Summary of Findings naming the mixed comparison
   types (`scripts/check_stratum_purity.py`, `dashboard/stratum_purity.js`).
   A protocol-compliant re-fit exists in
   `06_FINAL_ANALYSIS_V26/02_STATA/12_stratum_compliant_refit.do` but has
   **not** been adopted into the published estimates — that decision belongs
   to the review lead, and is recorded in `OUTSTANDING_DECISIONS.md`.
2. **The 12-record PRISMA screening gap was a unit mismatch**, not a missing
   set of records (5,100 references resolve to 5,088 studies; 12 references
   were additional reports of studies already present). Resolved and pinned
   with a regression test.

Both remain visible on the dashboard and are not duplicated here as new P0
findings; they are cross-referenced because this audit's P0 checklist would
otherwise appear to have missed them.
