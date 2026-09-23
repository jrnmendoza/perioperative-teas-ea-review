# Digitisation record — Gu 2019, Fig. 4 (24-hour analgesic consumption)

Adopted under Amendment E2.1. Reproduce with `E2_digitise_gu2019_fig4.py`, which
re-extracts the figure from the hash-pinned PDF
(`covidence_1471_full_article.pdf`, SHA-256 `b6fb0c09…aa33`, page 4, embedded
image 999 × 527 px). Output: `E2_digitise_gu2019_fig4.json`. The third-party
image itself is not stored in the repository.

**Axis.** Eleven gridlines (0–100 mL). Linear fit residual ≤ 0.21 units; **1 pixel
= 0.209 mL**. The caption states mean ± SD. The y-axis is labelled
"Analgesics consumption (ml)".

## Validation against values printed in the text

| Arm | Time | Figure mean | Text mean | Difference | Figure SD | Text SD |
|---|---|---:|---:|---:|---:|---:|
| L-TEAS | 4 h | 10.02 | 10.02 | 0.00 | 2.29 | 2.26 |
| L-TEAS | 8 h | 19.41 | 20.55 | −1.14 | 4.91 | 4.59 |
| L-TEAS | 36 h | 72.40 | 72.64 | −0.24 | 9.81 | 9.74 |
| **C-TEAS** | 4 h | 15.23 | 13.38 | **+1.85** | 3.13 | 2.98 |
| **C-TEAS** | 8 h | 27.33 | 24.63 | **+2.70** | 4.07 | 3.94 |
| **C-TEAS** | 36 h | 79.91 | 76.01 | **+3.90** | 10.64 | 10.43 |

**Source contradiction.** The control-arm bars exceed the printed control means at
every time point where both exist: by 9–19 pixels, against a resolution of about
1 pixel, and increasingly with time. The TEAS arm agrees within about 1 pixel at
4 h and 36 h. Standard deviations agree throughout. The 24-hour control value is
therefore likely to be overstated, which would bias the contrast in favour of
TEAS. **No correction is applied.** The result is flagged, and a leave-out
analysis excluding Gu 2019 is mandatory.

## Digitised 24-hour values (T4)

| Arm | n | Mean (mL = µg sufentanil) | SD (mean of whiskers) | Whiskers (+/−) |
|---|---:|---:|---:|---:|
| C-TEAS (sham) | 59 | 58.84 | 7.41 | 7.72 / 7.09 |
| L-TEAS | 58 | 55.71 | 7.93 | 8.14 / 7.72 |

The PCIA contained 100 µg sufentanil in 100 mL (1 µg/mL), stated in the methods on
p.2, so mL equals µg sufentanil. That is a valid linear factor under X3. PCIA
started at the end of the operation, and consumption was taken from the device
records, so it is delivered.

| Sufentanil factor | MD, mg IV MME (95% CI) |
|---|---|
| 0.25 | −0.78 (−1.48, −0.09) |
| **0.5 (central)** | **−1.57 (−2.96, −0.17)** |
| 1.0 | −3.13 (−5.91, −0.35) |
