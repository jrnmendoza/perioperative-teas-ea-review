# The five figure-only / unconverted values — digitization attempt and QC verdicts

**Date:** 2026-09-12
**Scope:** the five `note` fields the 2026-09-10 placeholder incident left open —
Wu 2016, Liu 2015, Zhang 2018 ×2, Gao 2022.
**Standard applied:** `gu2019_digitization_QC.md`, whose decisive step is that a
digitization is only trusted if it reproduces values the source reports
independently of the figure. Gu 2019 had three such anchors, failed against them,
and its digitized values were used in nothing.

**Verdicts: two digitized and validated, three refused.**

| Study / outcome | Verdict |
|---|---|
| Zhang 2018 — time to first flatus | **Digitized, validated** (7/7 anchors) |
| Zhang 2018 — VAS pain, POD 1 (~24 h) | **Digitized**, panel validated; this pair has no anchor of its own |
| Wu 2016 — VAS at rest/cough | **Refused** — no anchor exists |
| Liu 2015 — POD 1 pain | **Refused** — no anchor exists |
| Gao 2022 — 24 h analgesic-pump sufentanil | **Refused** — not a digitization question; the conversion is invalid |

Nothing below has been entered into any synthesis. See "What happens next".

---

## Zhang 2018 — digitized and validated

### Why this is not "visually inferring"

The locked workbook's instruction for this study is specific, and it is not a
prohibition on digitizing: *"Exact group mean±SE values are shown only in
Figure 2a; do not visually infer"*, and *"do not enter Figure 2 continuous
outcomes into quantitative meta-analysis until formal graph digitization or
author data provide exact means/SEs."* Formal digitization is the sanctioned
route. Eyeballing a raster is what is ruled out.

Figure 2 is **vector art**. Every bar is a path with exact coordinates in the PDF
content stream and every axis tick is a positioned text run, so no pixel is read
and no value is estimated by eye. This is a stronger method than the raster
pipeline used for Gu 2019, which is why it can succeed where that one could not.

### Method

1. Bars are filled rectangles keyed to arm by fill colour (black = TEA,
   grey = sham-TEA). One bar — POD 2 TEA — is drawn as an **unfilled outline**
   rather than a fill and is recovered from its two vertical edge segments. It
   would otherwise have been silently missing, and it turns out to be the
   tightest-validating pair in the figure.
2. Each panel is calibrated by least-squares fit over its own numeric axis ticks.
   The residual is judged as a percentage of that panel's axis range, because the
   three panels are scaled 0–150, 0–25 and 0–5; an absolute threshold would
   reject a panel calibrated to 0.28%.
3. Error bars: the vertical whisker above each bar top gives SE directly.
   SD = SE × √n with n = 21 per arm (Table 1).

| Panel | Ticks | Units per point | Max residual |
|---|---|---|---|
| a (hours) | 150, 100, 50, 0 | 1.515892 | 0.42 (**0.28%** of axis) |
| b (days) | 25, 20, 15, 10, 5, 0 | 0.189960 | 0.0554 (**0.22%**) |
| c (VAS) | 5, 4, 3, 2, 1, 0 | 0.041673 | 0.0086 (**0.17%**) |

### Validation — **PASSED, 7/7**

The paper reports seven percentage reductions in its Results text and tabulates
none of the underlying values. Every digitized pair was checked against its
reported percentage:

| Outcome | sham | TEA | Digitized | Reported | Error |
|---|---|---|---|---|---|
| Time to defecation | 105.777 | 72.373 | 31.58% | 31.7% | **0.12 pp** |
| Time to first flatus | 80.051 | 51.330 | 35.88% | 35.9% | **0.02 pp** |
| Postoperative hospital stay | 20.819 | 14.653 | 29.62% | 30.2% | **0.58 pp** |
| Time to resuming diet | 6.867 | 4.929 | 28.22% | 26.5% | **1.72 pp** |
| Time to ambulation | 4.853 | 2.725 | 43.85% | 42.8% | **1.05 pp** |
| VAS pain, POD 2 | 3.009 | 1.484 | 50.70% | 50.8% | **0.10 pp** |
| VAS pain, POD 3 | 2.715 | 0.968 | 64.36% | 64.9% | **0.54 pp** |

**What these anchors do and do not prove.** Each is a *ratio* between the two
arms, so they establish that the bars are read correctly relative to one another
— but a uniform error in the scale would cancel out and pass all seven unnoticed.
The absolute scale rests entirely on the axis-tick calibration above (residual
≤ 0.28% of axis). `scripts/validate_dashboard.py` therefore pins the three
`units_per_point` constants separately, because the validation set cannot.

Five of seven reproduce to within 0.6 pp. This is the opposite of the Gu 2019
outcome, where the errors were large, one-directional and confined to a single
arm — the signature of a source inconsistency rather than extraction noise.

### The two values the review actually needs

| Outcome | Arm | Mean | SE | SD (SE × √21) | n |
|---|---|---|---|---|---|
| Time to first flatus (h) | sham-TEA | 80.05 | 4.396 | 20.15 | 21 |
| | TEA | 51.33 | 2.780 | 12.74 | 21 |
| VAS pain, POD 1 (~24 h) | sham-TEA | 3.770 | 0.476 | 2.183 | 21 |
| | TEA | 3.956 | 0.476 | 2.183 | 21 |

Two things a reader should be told plainly:

- **The POD 1 pain pair has no anchor of its own.** The paper reports reductions
  for POD 2 and POD 3 only. The panel it sits in validated at both of those
  (0.10 pp and 0.54 pp), which is good evidence the panel is read correctly, but
  it is weaker than a direct check on the pair itself.
- **At POD 1, TEA is slightly *worse* than sham** (3.96 vs 3.77, a 4.9% increase).
  That is consistent with the paper reporting reductions only from POD 2 onward,
  and it matters: POD 1 is the timepoint the review's Target C needs, so this
  study does not support TEA at ~24 h even though it does at 48–72 h. The two
  POD 1 error bars are drawn identically in the source (both 0.476), which may
  mean they are schematic rather than separately computed.

---

## Wu 2016 and Liu 2015 — refused, no anchor exists

Both report their pain outcomes **only** as a direction and a P value:

- **Wu 2016:** VAS at rest/cough lower with true TAES than both comparators from
  6–60 h (Figure 1). No VAS number appears anywhere in the text.
- **Liu 2015:** *"Pain scores were significantly lower at postoperative day 1 in
  the TEAS group than in the sham group, whereas the VAS score in the TEAS group
  was comparatively higher at postoperative days 2 and 3 (figure 2)."* No number.

This was checked mechanically rather than by impression: across each full paper,
counting every `mean ± SD` pattern within 200 characters of "VAS", "pain score"
or "flatus" —

| Paper | `mean ± SD` patterns in the paper | …near a pain/flatus mention |
|---|---|---|
| Wu 2016 | 27 | **0** |
| Liu 2015 | 34 | **0** |
| Zhang 2018 | 7 | **0** — but seven *percentages* are reported, which is what made it digitizable |

Both papers report means and SDs freely for other variables (immune markers,
haemodynamics), so the absence next to the pain outcomes is a property of the
reporting, not of the extraction.

**There is therefore nothing to validate a digitization against.** Gu 2019 shows
why that is disqualifying: it *had* three anchors, and only because of them was
it possible to discover that its figure disagreed with its own text. Digitizing
Wu 2016 or Liu 2015 would produce numbers with no way to detect that same failure
— the values would look like data and carry no means of being checked. Recording
them "for provenance" would be worse than not producing them, because Gu 2019's
provenance-only values were safe precisely *because* validation had been run and
had failed loudly.

**Escalation:** author contact for the tabulated means and SDs, as for Gu 2019.

---

## Gao 2022 — refused, and not a digitization question

This value is not figure-only. It is tabulated, as a median with IQR:

> `24 h analgesic pump, µg   33.0 (0.0, 50.0)   30.0 (0.0, 60.0)   P = 0.197`

The open item is whether to convert it to mean/SD via Wan et al. **It must not
be**, and the source says why in the row above it:

> `Analgesic pump sufentanil, n (%)   597 (72.2)   588 (71.0)`

**About 28% of patients in each arm received no analgesic pump at all.** That is
why Q1 = 0 in both arms: the distribution has a large spike at zero. The Wan et al.
estimators assume approximate normality, which this distribution plainly violates.

Carrying the conversion out anyway makes the failure concrete:

| Arm | n | Q1 | median | Q3 | Wan mean | Wan SD | mean − 1.96 SD |
|---|---|---|---|---|---|---|---|
| TEAS | 827 | 0 | 33 | 50 | 27.67 | 37.13 | **−45.11 µg** |
| Sham | 828 | 0 | 30 | 60 | 30.00 | 44.56 | **−57.33 µg** |

A normal distribution with those parameters places roughly **23% of patients
below zero micrograms**. The derived SD does not describe this trial; it
describes a normal distribution that does not exist. This is the same concern
already recorded for Zhang 2023, where median = Q3 strained the symmetry
assumption — here it is not strained but broken.

**The correct treatment is the one already in place:** keep the median (IQR) and
the P value as source truth, and leave the row out of any MME pool. No author
contact is needed; the paper reports exactly what it should.

---

## What happens next

The two validated Zhang 2018 values are recorded here and in
`zhang2018_figure2_digitization.json`, and are surfaced on the dashboard with
their provenance. **They have not been entered into Target C or Target E.**

Admitting a digitized study to a locked synthesis is a review-team decision, in
the same way that clearing an interpretation staleness flag is: the workbook's
instruction is addressed to that decision, and this document exists to let the
team make it on evidence. Re-running `scripts/digitize_zhang2018_figure2.py`
reproduces every number above.
