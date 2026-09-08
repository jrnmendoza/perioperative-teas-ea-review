# V33 Source QC Report

Perioperative TEAS & EA systematic review · PROSPERO CRD420251090635
Date: 2026-09-08

Every value added to v33 was read from a source PDF held in this project. This
report records what was checked, what was found, and what remains unresolved.

---

## 1. Source verifications performed

| Study | PDF | Verified | Result |
|---|---|---|---|
| Yao 2015 | `039_yao_2015.pdf` | Table 3, Table 2, abstract | All supplement values confirmed exactly |
| Chen 2015 | `037_chen_2015_thyroidectomy_lund.pdf` | Tables 1–2, Methods | Confirmed a distinct trial from Yao 2015 |
| Yu 2020 | `s13063-019-3892-4.pdf` | Tables 2–3, Results, abstract | Rescue confirmed; **pain values conflict internally** |
| Zhu 2022 | `covidence_381_full_article.pdf` | Table 1, Results, CONSORT | Values and arm Ns confirmed |
| Pan 2023 | `getfile.php-4.pdf` | Table 2 | Values and analysis Ns confirmed |
| Yang 2020 | `covidence_464_verified.pdf` | Abstract Results, GI table | Confirmed |
| Liang 2021 | `014_liang_2021.pdf` | Table 4, Results 3.3, Methods 2.7, Figure 2 | Values, Ns and T11/T12 definitions confirmed |

### Verbatim confirmations

**Yao 2015, Table 3** — "Time to first rescue analgesia (min) 59 (31–1440) 47
(13–196) 0.039 / Cumulative number of rescue analgesia 1 (1–3) 3.5 (2–7.8)
0.004 / … Nausea 17 (48.6%) 26 (72.2%) 0.041 / Vomiting 7 (20.0%) 19 (52.8%)
0.004", under headers "Group TEAS (n = 35)" and "Group C (n = 36)".

**Zhu 2022, Table 1** — "Intraoperative sufentanil (µg; mean ± SD) 38.1 ± 4.97
39.1 ± 4.83 39.0 ± 5.12 37.8 ± 4.87 0.892 / Intraoperative remifentanil (mg;
mean ± SD) 0.58 ± 0.23 0.58 ± 0.23 0.50 ± 0.25 0.57 ± 0.26 0.948", under
headers "Group Pre (n = 101) Group 30 (n = 98) Group Comb (n = 100) Group Usual
(n = 101)".

**Pan 2023, Table 2** — "Duration Remifentanil (ug) 740.1±276.9 854.0±287.5
0.04*", under "Group T (N=52) Group C (N=53)".

**Liang 2021, Methods 2.7** — QoR-40 measured "before anesthesia (T0),
postoperative 24 hours (T11), and postoperative 48 hours (T12)". CONSORT
Figure 2: "Analysed (n = 35)" in both arms.

**Yang 2020, abstract Results** — "time to first flatus (20.8±4.6 versus
24.1±6.2 hours, P=0.026) and defecation (53.9±6.0 versus 57.5±7.2 hours,
P=0.046)".

---

## 2. Unresolved source problems

### 2.1 Yu 2020 — two internal contradictions (BLOCKING for the pain rows)

| Quantity | Table 2 | Abstract | Results text |
|---|---|---|---|
| TEAS VAS POD1 | 3.70 (1.53) | 3.70 ± 1.41 | — |
| TEAS VAS POD2 | 1.83 (0.98) | 1.83 ± 0.88 | — |
| POD1 P | starred, P < 0.05 | P < 0.05 | P = 0.042 |
| POD2 P | starred, P < 0.05 | P < 0.05 | **P = 0.26** |

Control values agree everywhere (4.73 (1.53), 2.30 (0.95)). Note that Table 2's
TEAS SD at POD1 is identical to the control SD, which suggests a transcription
error in the table rather than in the abstract — but that is an inference, not
a fact, so neither variant was selected.

**Disposition:** both rows added with the Table 2 values (a table outranks an
abstract), marked `CONFLICTED`, excluded from every pooled model, and logged for
author contact. The alternative variant is recorded in the row's Source-QC
field so nothing is lost.

### 2.2 Liang 2021 — undefined metric (HOLD)

"The number of patients who required extra analgesia in the control group was
much higher than that in the TEAS group [3.8(1.9) vs. 5.0(2.9), P 0.045]".

A count of patients out of 35 cannot be 3.8 ± 1.9. Metric, unit and time window
are all unresolved. Held as narrative; explicitly not interpreted as mg
morphine or MME, per the instruction.

### 2.3 Zhu 2022 — omnibus P only

Intraoperative opioid quantities sit in the baseline table with a single
four-group omnibus P and no pairwise contrast or pairwise CI. Usable, but the
row records that the reported P is not the contrast being modelled.

---

## 3. Extraction targets still open (17 supplement rows)

No value was invented for any of these. They are recorded in
`v33_Supplement_Reconciliation` with disposition `SOURCE VERIFICATION NEEDED`.

Zhu 2022 (24-h movement pain, early pain, QoR-15, rescue analgesic/antiemetic,
first flatus) · Yang 2020 (pain, PONV, LOS) · Pan 2023 (24-h movement pain,
QoR-40, analgesic use, vomiting, LOS) · Lu 2022 · Li 2021 · Gu 2019 (PONV) ·
Huang 2025 · Gao 2021 (abdominal pain, nausea, vomiting, bowel sounds, diet) ·
Jiang 2026 · Wang 2023 · Tu 2024 · Sun 2017 · Sim 2002 · Lu 2021 · Long 2025 ·
Wang 2024 · Zheng 2025.

Several of these PDFs are present locally and could be extracted in a
subsequent pass; this pass verified the studies the supplement supplied values
for, plus every study whose PDF was opened for that purpose. Extending
extraction to the remaining targets is a scoped follow-up, not a blocker.

---

## 4. Prohibited operations — confirmed not performed

| Prohibition | Status |
|---|---|
| Median rescue count × mean weight × 0.05 µg/kg → MME | Not performed. Yao 2015 stays a count. |
| PCA reservoir content → consumption | Not performed. |
| Rescue incidence → MME | Not performed. Yu 2020 stays binary. |
| Graph-only → numerical promotion | Not performed. Gu 2019, Grech 2016, Zhan 2020, Wang 2023 stay graph-only. |
| POD1 → exact 24 h relabeling | Not performed. Zhang 2025 remains excluded from 0–24 h analyses. |
| Silent median → mean conversion | Not performed. QC asserts statistic-type integrity per row. |
| Double-counting a shared multi-arm control | Not performed. Zhu 2022 and Lu 2021 contribute one contrast per model. |
| Interpreting Liang 2021's 3.8/5.0 as MME | Not performed. Held. |
| Changing the study count | Not performed. 70 throughout. |

---

## 5. Risk of bias

`Corrected_RoB2` remains the authoritative source and was not modified. RoB 2 is
result-specific, and the newly added outcomes do **not** silently inherit
another outcome's rating:

- **Pan 2023** — the trial's existing RoB concern (post-randomisation
  exclusions, 105 randomised vs 52/53 analysed) is recorded on the new
  intraoperative remifentanil row and was not softened.
- **Yang 2020** — the existing open-label concern is carried onto the new
  defecation row, consistent with the sibling flatus row.
- **Yu 2020, Yao 2015, Zhu 2022, Liang 2021** — the added outcomes are not the
  result for which `Corrected_RoB2` recorded a judgement. They are flagged in
  the `Source-QC issue` field as lacking a result-specific assessment rather
  than being assigned one.

**Open item for the review team:** result-specific RoB 2 assessments are needed
for the 16 newly added analysable outcomes before they are reported as
GRADE-rated evidence. They are currently reported as source-verified data with
their provenance, not as RoB-rated results.
