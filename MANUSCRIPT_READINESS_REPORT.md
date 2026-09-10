# Manuscript Readiness Report

Prepared 2026-09-10. Status categories: **READY** / **READY WITH CAVEAT** /
**NOT READY**. This report assesses whether each section's underlying
evidence and infrastructure support drafting — it does not draft the
manuscript.

| Section | Status | Why |
|---|---|---|
| Primary outcome (TEAS vs sham, 0–24h opioid) | **READY WITH CAVEAT** | k=4, MD −14.00 [−34.18, +6.19], Low certainty, Stata-verified. Draft Results-safe/Discussion-safe wording and claim boundaries exist (Manuscript Lens). Caveat: interval crosses the null and I²=98.6% — the draft wording already reflects this, but any manuscript claim of "opioid-sparing effect" needs the same qualification. |
| Supportive EA evidence (EA vs usual care) | **READY WITH CAVEAT** | k=3, MD −3.94 [−19.77, +11.90], Very Low certainty. Now correctly labelled supportive, not primary (this pass). Caveat: manuscript must state explicitly that no sham-controlled EA estimate exists for this outcome — the absence itself is a finding, not silence. |
| Combined cross-modality synthesis | **READY WITH CAVEAT** | Correctly demoted to contextual/supporting throughout. Caveat: **AN-06 (PONV 0–48h) and its sibling AN-02, AN-07 pool across modality/comparator strata the protocol keeps separate** — flagged live on the dashboard but not yet re-fitted into the published estimate. Not manuscript-ready until the review lead adopts either the pooled estimate (with a stated protocol deviation) or the stratified re-fit (`06_FINAL_ANALYSIS_V26/02_STATA/12_stratum_compliant_refit.do`). |
| Secondary outcomes (pain, GI recovery, intraoperative opioid, rescue analgesia) | **READY WITH CAVEAT** | Values Stata-verified; N discrepancies (flatus) resolved with a regression guard. Target A (0–48h opioid) and Target E (flatus) share the stratum-purity defect above and carry the same caveat. |
| Nausea/vomiting components (unreported) | **NOT READY** | Pre-specified per PROSPERO ("nausea, vomiting, or composite PONV") but currently unreported with a reason ("component of a composite") that is weaker than it appeared before this protocol check. Decision pending — see `OUTSTANDING_DECISIONS.md` item 1. |
| RoB 2 | **READY WITH CAVEAT** | 531 result-specific judgements across priority-1 (37) and priority-2 (494) registers, all five domains populated. Caveat: independent dual assessment is in progress; the manuscript's Methods must state the assessor process once that concludes, not before (deliberately deferred, not omitted — see PRISMA items 11/23c below). |
| GRADE | **READY WITH CAVEAT** | 10 rule-based v34 model ratings plus the legacy Target A–F Summary-of-Findings ratings; all disclose they are rule-based, not an independent panel judgement. Caveat: the three stratum-purity-flagged analyses (AN-02/06/07) need re-grading if their estimates change. |
| PRISMA | **READY** | Full flow reconciled (5,100 references → 5,088 studies → 2,928 screened → 210 assessed → 70 included); the 12-record apparent gap was a unit mismatch, resolved and pinned. Citation-searched trial (Wu 2016) named and derived, not asserted. |
| Study characteristics | **READY** | 70 canonical studies, extraction provenance recorded per study. |
| Sensitivity analyses | **READY** | Leave-one-out, conversion-factor sensitivity, and named sensitivity variants (e.g. Chen 2015 Hyperalgesia median/IQR approximation) all computed and disclosed as sensitivity, not promoted on the basis of significance. |
| Derivability / Tier E | **READY** | Tiered architecture (A–F) intact; Tier E scale-free SMD synthesis carries its own overclaim guardrails (no certainty rating, no absolute-dose claim, explicit "not a substitute for the missing sham-controlled EA estimate"). |
| Clinical interpretation (Clinical Importance Studio) | **READY** | Verified this pass: quadrant counts and percentages are computed live from the paired dataset and are internally consistent by construction (checked computationally against the built site: k=6, quadrants 3/0/3/0, percentages sum to 100.0%). |
| Reproducibility | **READY** | Master workbook SHA-256 pinned with hard-abort on mismatch; every generated dashboard file names the script that produced it; the post-lock errata register is independently re-derived on every build rather than trusted as static text. |
| Remaining source QC | **READY WITH CAVEAT** | Two post-lock classification questions remain open (Szmit 2021's nausea window; an incomplete stratum label in a v26 results file) — both are labelling/classification decisions, not data defects, and are itemised in `OUTSTANDING_DECISIONS.md`. |

## Overall

**NOT READY for submission as a whole**, blocked specifically on: (1) the
nausea/vomiting reporting decision, and (2) the stratum-purity re-fit decision
for AN-02/06/07. Every other section is READY or READY WITH CAVEAT, and the
caveats are stated, sourced, and already visible on the dashboard rather than
hidden. Once those two decisions are made, this report's status upgrades
accordingly — neither requires new analysis, only a decision from the review
lead using numbers already computed.
