# Gu 2019 — Figure 4 digitization attempt and QC verdict

**Study:** Gu S, et al. *Eur J Integr Med* 2019;26:11–17. TEAS after laparoscopic radical
gastrectomy. n = 58 (L-TEAS) / 59 (C-TEAS, placebo-control: stimulator output wires cut).
**Target:** cumulative postoperative analgesic (PCIA solution) consumption at **T4 = 24 h**.
**Why digitization was needed:** the 24 h value is not tabulated anywhere. Tables 1–4 cover
patient characteristics, RSS, GI recovery and satisfaction. The Results text reports analgesic
consumption at 4 h, 8 h and 36 h only, and **skips 24 h**. The value exists only in Fig. 4.

## Unit conversion (verified, exact — not the blocker)
PCIA = 100 µg sufentanil in 100 mL ⇒ **1.0 µg/mL**, so mL and µg sufentanil are numerically
equal. Timepoints are explicitly defined in-source, three times: "T1, T2, T3, T4 and T5
represent 4, 8, 16, 24 and 36 h after operation respectively."

## Method
1. Figure extracted losslessly from the publisher PDF (`p4_Im1.jpg`, 999×527 px, RGB).
2. Series separated by colour masks (blue = C-TEAS, orange = L-TEAS); legend band (top 70 px)
   excluded so legend swatches cannot be mistaken for bars.
3. Y-axis calibrated on 9 detected horizontal gridlines (uniform 48.0 px per 10 units).
   Linear fit `value = -0.2083333 × row + 101.9792`, **max residual 0.0000**. The fit implies
   y = 0 at row 489.50; the independently detected baseline is row 488.5 (1 px agreement).
4. Bar tops taken as the first row where ≥60% of the bar's columns are series-coloured.
5. **Validation:** the method was applied blind to the three timepoints the text DOES report,
   before reading anything at T4.

## Extracted coordinates (bar column ranges, px)
| Timepoint | C-TEAS (blue) | L-TEAS (orange) |
|---|---|---|
| T1 (4 h)  | 165–204 | 215–254 |
| T2 (8 h)  | 341–379 | 390–429 |
| T3 (16 h) | 516–555 | 565–604 |
| T4 (24 h) | 691–730 | 742–779 |
| T5 (36 h) | 866–905 | 917–956 |

## Digitized values (mL ≡ µg sufentanil)
| Timepoint | C-TEAS | L-TEAS |
|---|---|---|
| T1 (4 h)  | 15.52 | 10.10 |
| T2 (8 h)  | 27.60 | 19.69 |
| T3 (16 h) | 41.77 | 36.98 |
| **T4 (24 h)** | **59.06** | **55.73** |
| T5 (36 h) | 79.90 | 72.60 |

## Validation result — **FAILED**
| Timepoint | Arm | Digitized | Text-reported | Error | % error |
|---|---|---|---|---|---|
| T1 (4 h) | C-TEAS | 15.52 | 13.38 | +2.14 | **+16.0%** |
| T1 (4 h) | L-TEAS | 10.10 | 10.02 | +0.08 | +0.8% |
| T2 (8 h) | C-TEAS | 27.60 | 24.63 | +2.97 | **+12.1%** |
| T2 (8 h) | L-TEAS | 19.69 | 20.55 | −0.86 | −4.2% |
| T5 (36 h) | C-TEAS | 79.90 | 76.01 | +3.89 | **+5.1%** |
| T5 (36 h) | L-TEAS | 72.60 | 72.64 | −0.04 | −0.0% |

## Verdict and interpretation
The **method is sound**: calibration residual is exactly zero, and the identical pipeline
reproduces the **L-TEAS** arm to within 0.8%, 4.2% and 0.04% at the three validation points.

The failure is **arm-specific and one-directional**: every **C-TEAS** bar reads systematically
HIGHER in the figure than the value stated in the text (+16.0%, +12.1%, +5.1%). Random
digitization error cannot produce a consistent, single-arm, single-signed bias while the other
arm is reproduced almost exactly. This is therefore evidence of an **inconsistency within the
source between Figure 4 and the Results text for the control arm**, not a limitation of the
extraction.

**Consequence:** the T4 (24 h) value cannot be trusted from either route — the figure
disagrees with the text wherever the two can be compared, and the text does not report 24 h at
all. Gu 2019 is therefore **not** admissible to S3.

**Escalation:** this is beyond what independent dual-reviewer digitization can fix, because
re-reading the same figure cannot reconcile a figure-vs-text discrepancy. Gu 2019 requires
**author contact** for the tabulated 24 h means and SDs, and for clarification of the C-TEAS
values in Fig. 4.

**Digitized values above are recorded for provenance only. They are NOT used in any analysis.**
