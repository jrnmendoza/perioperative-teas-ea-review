# Dashboard Scientific Audit — Changelog

Entries for this pass only. See `DASHBOARD_SCIENTIFIC_AUDIT_REPORT.md` for the
full P0 checklist including items verified-clean with no change made.

---

### 1. EA-vs-usual-care model relabelled from `PRIMARY` to `SUPPORTIVE`

- **Section:** Primary tab headline KPI card (all/TEAS/EA branches), GRADE
  Summary of Findings table, interpretation layer.
- **Old:** `role: "PRIMARY"`; name "PRIMARY MODALITY 2: EA vs Usual Care";
  badge "PRIMARY MODALITY 2 (EA vs Usual Care)"; headline card title "EA
  Primary 24-h Opioid Sparing"; interpretation-layer label "Primary 0–24 h
  opioid — EA vs usual care".
- **New:** `role: "supporting"` / `"SUPPORTIVE"`; name "SUPPORTIVE EA
  EVIDENCE: EA vs Usual Care"; badge "SUPPORTIVE EA EVIDENCE
  (Usual-Care/No-Stimulation Comparator)"; headline card title "Supportive EA
  Evidence (Usual-Care Comparator)"; interpretation-layer label "Supportive
  evidence — EA vs usual care (no-stimulation comparator), 0–24 h opioid".
  TEAS's own card retitled "Primary Efficacy Analysis: TEAS vs Sham" /
  "PRIMARY EFFICACY ANALYSIS (TEAS vs Sham)" for parallel clarity. The
  all-modality headline card and its badge now state the hierarchy and the
  insufficient-sham-EA-evidence caveat explicitly rather than presenting TEAS
  and EA as co-equal "Modality-Specific" primaries.
- **Reason:** PROSPERO's synthesis strategy is explicit: "Primary comparisons
  will be TEAS versus credible sham TEAS and EA versus sham EA. Supportive
  comparisons will evaluate TEAS and EA against usual care, no stimulation, or
  attention controls." Confirmed the dataset contains no sham-controlled EA
  trial reporting this outcome in absolute IV MME — the sole EA-vs-sham/placebo
  opioid contrast (Sim 2002) is weight-normalised and already routed to the
  Tier E scale-free SMD synthesis, not this model.
- **Authoritative source:** `00_protocol/source/PROSPERO TEAS EA.pdf`,
  "Strategy for data synthesis"; `TEAS EA Verification/v34_reconciliation/data/v34_outcome_data.csv`
  (comparator/modality resolution for every EA-modality opioid contrast).
- **Statistical result changed:** No. k, N, estimate, CI, p, I², τ² for this
  model are byte-identical before and after (verified: fingerprint over
  `bound_evidence` is computed only from those fields and did not change; 0
  stale records after regeneration).
- **Interpretation changed:** Yes — label, role, and surrounding prose. The
  underlying claim boundaries, do-not-say list, reviewer questions and
  discussion prompts for this analysis are unchanged; only what the analysis
  is *called* changed.
- **Fixed at:** `scripts/build_v34_dashboard_data.py` (`MODEL_META`, the true
  source), regenerated forward into `dashboard/v34_data.js` and
  `dashboard/interpretation_layer.js`. Hand-edited in parallel at
  `dashboard/app.js` (`STATA_MASTER_RESULTS["AN-01-EA"]`, the headline KPI
  card's three `filterModality` branches) since that object is not currently
  generated from the same pipeline (see the audit report's note on remaining
  hardcoded-text consolidation, out of scope for this pass).
- **Translations:** Corresponding Swedish entries added to
  `dashboard/ui_translations.js` for every new English string introduced.
- **QC status:** Verified. 85/85 `validate_dashboard.py` checks; 7/7 Playwright
  suites (`check_usability_ui`, `check_rob2_results_ui`,
  `check_interpretation_ui`, `check_tabs_ui`, `check_navigation_ui`,
  `check_language_ui`, `check_handover_ui`). `check_usability_ui`'s
  modality/comparator-naming assertion caught a wording slip in the first
  attempt (`usual-care` hyphenated, not matching the required `usual care`
  token) — fixed in the label text, not the test.
  `check_language_ui`'s TEAS-title regex was updated (word-order assumption
  only; still asserts the Swedish translation names TEAS and identifies the
  card as the primary/effect analysis) because the English source text it
  translates intentionally changed.

---

### 2. PRISMA exclusion-reason gloss corrected

- **Section:** PRISMA tab, "Reports Excluded" card.
- **Old:** "Wrong outcomes (no 24h opioid/pain)" — 117 (83.0%).
- **New:** "Wrong outcome — no eligible perioperative outcome reported", with
  a tooltip naming the full eligible-outcome framework (opioid, pain, PONV,
  rescue analgesia, QoR, GI/functional recovery, LOS, persistent opioid use,
  adverse events).
- **Reason:** The old gloss implied exact 24-h opioid/pain reporting was
  required for eligibility. PROSPERO's eligible-outcomes list is materially
  broader.
- **Authoritative source:** `00_protocol/source/PROSPERO TEAS EA.pdf`,
  "Additional outcomes".
- **Statistical result changed:** No — the count (117) and category name
  ("Wrong outcome") are unchanged; only the parenthetical gloss, which was an
  editorial addition rather than a transcribed source figure, was corrected.
  No source-level evidence was found that the count itself is wrong, so per
  the audit brief's rule it was not touched.
- **Interpretation changed:** Yes — wording only.
- **QC status:** Verified. 85/85 checks; no test depended on the old string.

---

### 3. `check_language_ui.cjs` assertion updated to match intentionally changed source text

- **File:** `scripts/check_language_ui.cjs`.
- **Old:** `assert.match(..., /TEAS.*opioidbesparing/i)` — tied to the retired
  English title "TEAS Primary 24-h Opioid Sparing".
- **New:** Two assertions — the translated title still contains "TEAS", and
  still contains "effektanalys" or "primär" (Swedish for
  analysis/primary) — matching the new English title "Primary Efficacy
  Analysis: TEAS vs Sham" without assuming word order.
- **Reason:** The English source text changed under item 1 above; the test's
  literal-substring assertion was tied to wording that no longer exists by
  design, not to a translation defect. Not weakened: it still fails if the
  translated title stops naming TEAS or stops identifying the card as a
  primary/effect analysis.
- **QC status:** Verified passing before and after against the intended
  Swedish string.
