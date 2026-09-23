# Amended primary estimand (E2) — definition

**Status: FIXED 23 September 2026.** Decision points DP1–DP4 were confirmed by the
review author (J.R.N. Mendoza) on 23 September 2026, each at the stated default;
DP5 is unchanged registered policy. **No model has been run under E2.** The file
hash is in `amended_primary_estimand_E2.sha256`. An external timestamp (a git
commit) is still to be made, and must precede any E2 extraction or model run.

**Timestamp note (23 September 2026).** The review author chose not to send the hashes to a
third party. The only timestamp is local git commit `95fcf66` (2026-09-23 20:58 +0200), which
the review team controls. This is recorded so the strength of the pre-registration claim is not
overstated.

## Why this document exists, stated plainly

The registered primary outcome (E1) admits one sham-controlled TEAS trial and no
sham-controlled EA trial. After seeing that result, and after seeing the expanded
k=4 sensitivity estimates, the review team decided to amend the primary outcome
to a broader construct. **This is a post-hoc change made with results known.** It
will be reported as such in PROSPERO and in the manuscript. E1 remains fully
reported.

This document defines E2 **before** E2 is applied to any result. Its purpose is to
make the definition checkable: every admission and exclusion must follow from
the text here, not from what a result does to the estimate.

---

## E1 — registered primary (retained, reported in full)

> Cumulative systemic postoperative opioid consumption from the end of surgery to
> 24 hours, converted to IV MME using prespecified conversion rules. Programmed
> but undelivered patient-controlled analgesia doses will not be counted as
> consumed opioid. (PROSPERO CRD420261452908, v1.0)

## E2 — amended primary (post hoc)

**Construct.** Cumulative postoperative opioid **reported as consumed or
delivered** in the first 24 postoperative hours, in mg IV morphine equivalents,
**including totals that capture patient-controlled analgesia only and totals
where additional rescue opioid was given but not quantified.**

What E2 relaxes relative to E1 is limited to **completeness of capture**. What
counts as a dose, the unit, the conversion rules and the prohibited conversions
are unchanged.

### Admission rules — a result enters E2 if all of these hold

**A1 — Consumed, not requested.** The quantity is reported as opioid consumed,
used, delivered or administered. Results explicitly reported as demands, button
presses, or programmed or requested doses are excluded (E1's registered sentence
still applies).

**A2 — Window.** The reported window ends 24 hours after surgery and is stated as
one of:
- "0–24 h", "first 24 h", "24 h postoperatively" or equivalent;
- a period beginning at PACU arrival or PCA connection within the first
  postoperative hour and ending at 24 h;
- POD1, **only** where the report defines it as the first 24 hours after surgery.

A window that is unstated ("study PCA period"), described as "perioperative",
defined by calendar day, or longer than 24 hours does not qualify.

**A3 — Incomplete capture admitted.** Admission does not depend on whether rescue
or non-PCA opioid was given, quantified or included. The admitted quantity is the
reported total. Unquantified components are **not imputed and not added**; they
are recorded as a capture limitation.

**A4 — Convertible quantity.** The reported total is in a drug with a registered
factor — IV morphine 1, IV hydromorphone 5 mg/mg, IV fentanyl 0.1 mg/µg, IV
sufentanil 0.5 mg/µg (central) — or is already expressed by the authors as
morphine equivalents (see decision point 2). A result whose **only** quantified
opioid lacks a registered factor (tramadol, pethidine, dezocine, oxycodone,
alfentanil, remifentanil, butorphanol, bucinnazine) is excluded. A result where
the unfactored drug is only an **unquantified rescue** alongside a convertible
total is admitted under A3.

**A5 — Absolute dose with dispersion.** An arm-level mean and SD, or a dispersion
convertible to an SD by the review's existing rules, of an absolute dose.

**A6 — Eligibility.** The trial meets PICOS, including general anaesthesia, and
the opioid route is systemic.

### Exclusions that do not change — these are registered policy, not strictness

- **X1** Weight-normalised doses are never multiplied by a mean weight (prohibited conversion 1).
- **X2** Rates are never multiplied by a duration (prohibited conversion 2).
- **X3** Pump volume is never converted to mass without a verified concentration (prohibited conversion 3).
- **X4** Programmed doses and button presses are never counted as delivered (prohibited conversion 4; E1 text).
- **X5** Separately reported components are never summed into a total SD (prohibited conversion 5).
- **X6** No oral-to-IV factor is assumed where the route of an equivalence is stated as oral.

### Unchanged across E1 and E2

- **Separation.** TEAS and EA are never pooled. Sham, usual care and active
  electrical controls are never pooled.
- **Scope.** All four modality × comparator bodies, plus active control where
  data exist. E2 is applied to every body, not selectively.
- **HOLD.** A HOLD caused by an unresolved source question (for example
  anaesthesia unverified, or cohort overlap) remains a HOLD. E2 changes capture
  requirements, not source questions.
- **Joint criterion.** At least 10 mg IV MME less opioid **and** paired ~24-h pain
  evidence with an upper 95% limit below +1 point. 8 mg and 30% remain
  sensitivity thresholds only.
- **Pipeline.** Compatible active arms are combined with the shared control
  counted once; REML with safeguarded Hartung–Knapp for k ≥ 2; within-study
  normal interval for k = 1; prediction intervals only for k ≥ 5; fresh
  result-specific RoB 2; GRADE redone.

### Candidate set — E2 is applied uniformly

1. Every result already extracted against the opioid construct (Additional file
   12, Tiers A1 and A2 — 0–24 h results only).
2. **The eight Tier B1 reports**, which must be extracted and classified against
   E2 before the rerun. Applying E2 only to results already extracted would be a
   selective application.
3. Tier B2 reports are re-checked for a qualifying 24-hour total.

### Prespecified sensitivity analyses for E2

- Sufentanil 0.25 and 1.0 mg/µg, for every body with a sufentanil-derived result.
- Restriction to E1-eligible results — that is, the registered primary.
- Exclusion of results with known unquantified rescue (A3).
- Exclusion of author-reported equivalents of unstated route (decision point 2).
- Leave-one-out for k ≥ 3.

---

## Decision points — confirmed 23 September 2026

Each default below is chosen on principle. **None was chosen by examining which
trials it admits.** If the review team changes a default, record the reason here
before the file is fixed.

| # | Question | Default | Alternative | Confirmed |
|---|---|---|---|---|
| **DP1** | Window tolerance (A2) | Stated 24-h windows, including those starting at PACU arrival or PCA connection within hour 1; POD1 only if defined as 24 h | Stated "0–24 h" only | **Default** |
| **DP2** | Author-reported "morphine equivalents" of unstated route | Admitted as reported, flagged, with an exclusion sensitivity analysis | Excluded from E2 | **Default** |
| **DP3** | Totals whose delivered-versus-demanded status is unstated | Admitted, provided the report calls it consumption (A1) | Excluded unless stated as delivered | **Default** |
| **DP4** | Unfactored drug given only as unquantified rescue | Admitted under A3; the convertible total is used | Excluded | **Default** |
| **DP5** | Central sufentanil factor | 0.5 mg/µg, unchanged from registered policy | *None — changing it post hoc is not recommended* | Registered policy |

---

## What happens next, in order

1. ~~The review team confirms or changes DP1–DP5.~~ Done 23 September 2026.
2. The file is marked FIXED (done) and hashed (done), then **committed**. **Nothing is run before the commit.**
3. The Tier B1 reports are extracted and classified against E2.
4. All bodies are rerun under E2 through the unchanged pipeline.
5. PROSPERO major revision; manuscript "Changes from the protocol" section, with
   E1 and E2 reported side by side.

---

## Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)

**Made by the review author (J.R.N. Mendoza) after E2 had been applied to the eight
Tier B1 reports, knowing that these two changes admit exactly Zhang 2025 and
Gu 2019. Zhang 2025's effect was known, and so were three of Gu 2019's four time
points.** The superseded text above is retained unchanged.

**Reason, as given:** the review author chose to admit these reports without
querying their authors.

**Change 1 — DP1, POD1.** A total reported for "POD1" is accepted as the first 24
hours after surgery, **whatever the report's own definition of POD0 or POD1**.
This supersedes the DP1 default ("POD1 only where the report defines it as the
first 24 hours"). It applies to every candidate result, not only Zhang 2025.

**Change 2 — figure digitisation adopted.** An arm-level mean and SD printed only
in a figure may be digitised from the source image, subject to all of these:

- pixel measurement against the figure's own axis gridlines, with the axis fit
  residual and the units per pixel recorded;
- a reproducible script that re-extracts the image from the hash-pinned PDF;
- validation against every value from the same figure that is also printed in the
  text;
- any figure–text disagreement beyond measurement resolution is handled under the
  review's source-contradiction policy: the result is admitted with a flag and a
  **mandatory leave-out sensitivity analysis**, and published values are never
  "corrected".

This applies to every candidate result, including the Tier B2 re-check.

**Consequence.** Both reports enter the E2 TEAS-versus-sham body. The sufentanil
factors 0.25 and 1.0 are mandatory sensitivities for that body (G11).
