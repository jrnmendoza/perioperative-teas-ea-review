# V33 Integration Report

Perioperative TEAS & EA systematic review · PROSPERO CRD420251090635
Date: 2026-09-08

---

## 1. Inputs

| Role | Resolved absolute path |
|---|---|
| Base master (v32) | `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx` |
| Supplement | `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_v32_SUPPLEMENTARY_MISSED_OUTCOMES_FOR_CLAUDE_CODE.xlsx` |
| Output (v33) | `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx` |

**Exactly one copy of each input exists in the project.** A recursive search
found no duplicates and no other `v3x` master.

### v32 immutability

v32's mtime was recent at the time of the search, so its content was checked
against the committed git blob rather than trusted:

```
sha256 = 74fda7d176fae15af4aa5bbff318514f998adcf957a2f9cad67e8de55ab7b12f
```

Working copy and committed blob are byte-identical; the mtime was a filesystem
touch, not an edit. The build script asserts this hash **before and after**
writing v33, and the QC gate re-asserts it independently. v32 was opened
read-only throughout; v33 was produced from a `copyfile`.

---

## 2. Supplement structure

The workbook has three sheets: `README`, `Missed_Data_v32` (40 data rows × 18
columns) and `Analysis_Priority`. The README was read first and its merge rules
were followed as written — in particular, that the supplement is additive, that
graph-only outcomes stay graph-only, that reported statistic types are
preserved, and that MME must not be manufactured from PCA reservoir content,
binary rescue use, median rescue counts, unclear units, or weight-based doses.

`Data readiness` was treated as authoritative and **not** flattened:

| Readiness | Rows | Treatment |
|---|---:|---|
| READY (values supplied) | 8 | Verified against source, then added |
| READY after N verification | 5 | Arm N verified from source, then added |
| READY after multi-arm N verification | 6 | Arm N verified; shared control flagged |
| READY after analysis-N verification | 1 | Analysis N verified; RoB concern retained |
| PARTIAL | 2 | Source-checked; conflict found; added as CONFLICTED, not pooled |
| HOLD | 1 | Added as a HOLD row, narrative only |
| SOURCE-EXTRACT BEFORE ANALYSIS | 17 | Recorded as unresolved extraction targets; **no value invented** |

---

## 3. Duplicate / conflict audit

Every supplement row was matched against v32's `Outcome_Data`, `Analysis_Readiness`,
`Set_*` and `Stata_*` sheets on a composite key of canonical study + outcome
family + outcome/result + timepoint/window + intervention arm + comparator arm.
Matching was never done on study name alone.

| Class | Rows |
|---|---:|
| A. genuinely missing from v32 | 16 |
| B. already present identically | 6 |
| C. present but incomplete / undefined | 1 |
| D. present but conflicting | 0 |
| E. same outcome, different legitimate timepoint | 0 |
| F. same outcome, different legitimate contrast | 0 |
| G. requires source verification | 17 |

Full row-by-row disposition is in the `v33_Supplement_Reconciliation` sheet.

**Class B (already present, no duplicate created):** Gao 2021 paralytic ileus,
first flatus and first defecation; Huang 2025 first flatus and first defecation;
Yao 2015 QoR-40. All six matched existing v32 values exactly.

### A near-duplicate that is not one

The supplement's **Yao 2015** rescue data (median 1, IQR 1–3 vs 3.5, IQR 2–7.8;
P = 0.004) is almost identical to v32's **Chen 2015** rescue data (median 1,
IQR 1–3 vs 3.5, IQR 2–7; P = 0.004). Both PDFs were opened:

| | Chen 2015 | Yao 2015 |
|---|---|---|
| Journal | Int J Clin Exp Med 2015;8(8):13622–7 | Evid Based Complement Alternat Med 2015 |
| Surgery | Thyroidectomy | Gynaecological laparoscopy |
| n | 41 / 42 | 35 / 36 |
| Rescue drug | IV morphine 2 mg | IV sufentanil 0.05 µg/kg |
| QoR-40 at 24 h | median 183 (172–190) vs 168 (154–183) | mean 176.5 (10.2) vs 164.8 (14.7) |

They are **different trials** from the same Fujian group (Yusheng Yao is third
author on Chen 2015 and first author on Yao 2015). No rows were merged and no
study was removed. The coincidence in the rescue medians is genuine and is
recorded so a later reader does not re-raise it.

---

## 4. What was added

18 rows appended to `Outcome_Data` (364 → 382). Every value was read out of the
source PDF named below, not copied from the supplement.

| Study | Outcome | Source | Arm N |
|---|---|---|---|
| Yu 2020 | Participants requiring rescue sufentanil, 0–24 h | Trials 2020;21:43 Table 3 | 30 / 30 |
| Yu 2020 | Resting pain VAS, POD1 | Table 2 + abstract | 30 / 30 |
| Yu 2020 | Resting pain VAS, POD2 | Table 2 + abstract | 30 / 30 |
| Yao 2015 | Cumulative rescue administrations, 0–24 h | Table 3 | 35 / 36 |
| Yao 2015 | Time to first rescue analgesia | Table 3 | 35 / 36 |
| Yao 2015 | Postoperative nausea, 0–24 h | Table 3 | 35 / 36 |
| Yao 2015 | Postoperative vomiting, 0–24 h | Table 3 | 35 / 36 |
| Zhu 2022 ×3 | Intraoperative sufentanil (Pre / 30-min / Comb) | Acupunct Med 2022;40(5) Table 1 | 101 / 98 / 100 vs 101 |
| Zhu 2022 ×3 | Intraoperative remifentanil (Pre / 30-min / Comb) | Table 1 | 101 / 98 / 100 vs 101 |
| Pan 2023 | Intraoperative remifentanil | J Pain Res 2023;16 Table 2 | 52 / 53 |
| Yang 2020 | Time to first defecation | Med Sci Monit 2020 | 29 / 28 |
| Liang 2021 | Global QoR-40 at 24 h (T11) | Evid Based Complement Alternat Med Table 4 | 35 / 35 |
| Liang 2021 | Global QoR-40 at 48 h (T12) | Table 4 | 35 / 35 |
| Liang 2021 | Postoperative analgesia requirement | Table 4 | 35 / 35 |

Yao 2015 vomiting (7/35 vs 19/35, P = 0.004) was not in the supplement; it was
found in the same table while verifying the nausea row and is recorded as such.

### Arm-N verifications performed

- **Zhu 2022** — 413 randomised (103/104/103/103), 400 completed. Table 1's own
  column headers give the analysis Ns: 101 / 98 / 100 / 101. These match the
  existing v32 PONV rows, so the shared usual-care denominator is consistent.
- **Pan 2023** — 105 randomised; Table 2 headers give Group T N = 52, Group C
  N = 53, confirming post-randomisation exclusions. The existing RoB 2 concern
  is retained and was not softened.
- **Yang 2020** — 60 recruited, 59 randomised (30/29), 57 completed. Analysis
  Ns 29/28, mirroring the existing v32 flatus row.
- **Liang 2021** — 75 allocated (37/38), 35/35 analysed per the CONSORT diagram.
  T11 and T12 are defined in the source Methods as postoperative 24 h and 48 h.
- **Yu 2020** — 60 randomised, 30/30; percentages in Table 3 (43.3%, 80%)
  confirm the denominators.

---

## 5. Source inconsistencies discovered

**Yu 2020 — internal contradiction, unresolved.**
Table 2 reports TEAS VAS as 3.70 (1.53) at POD1 and 1.83 (0.98) at POD2. The
abstract reports 3.70 ± 1.41 and 1.83 ± 0.88 for the same results. Separately,
the Results text states "P = 0.042 and P = 0.26 for T1 and T2 respectively"
while Table 2 stars both with P < 0.05 and the abstract claims P < 0.05 for
both. Table 2's TEAS SD at POD1 (1.53) is also identical to the control SD,
which is itself suspicious. Both variants are recorded; the rows are marked
CONFLICTED and enter no pooled model. Author contact required.

**Liang 2021 — metric undefined.**
The source describes "the number of patients who required extra analgesia" as
3.8 (1.9) vs 5.0 (2.9). A count of patients out of 35 cannot be 3.8 with a
dispersion of 1.9. The wording and the statistic are mutually inconsistent, and
the time window is not stated. Held; explicitly **not** interpreted as mg
morphine or MME.

**Zhu 2022 — outcome placement.**
The intraoperative opioid quantities appear in Table 1 among baseline and
anaesthesia parameters, with a single four-group omnibus P (0.892 for
sufentanil, 0.948 for remifentanil) and no pairwise contrast. They are usable
as an intraoperative-opioid outcome but should be read as balance data, and
that is recorded on the rows.

---

## 6. Technical defect found in the workbook copy

v32 contains **596 formula cells** (`Outcome_Data` 522, `Study_Master` 63,
`Summary` 11). openpyxl cannot evaluate formulas and discards Excel's cached
results on save. A naive copy-and-append would have handed every downstream
consumer reading with `data_only=True` a `None` for those cells — silently
emptying the derived-effect columns of **190 of the 364** v32 outcome rows.

The build materialises all 596 cached values before writing, and the QC gate
asserts that v33 has no more blank `Derived effect measure` cells than v32 did.

A second stale-count defect was found and fixed: the v33 `Summary` sheet
inherited v32's "Source-normalized outcome rows = 364" while `Outcome_Data`
held 382. `build_site.py` now counts `Outcome_Data` directly and **raises** if
the workbook's stated figure disagrees, so the count can never be hardcoded or
drift again.

---

## 7. Primary-outcome protection

- No appended row is flagged `Primary opioid meta-analysis eligible? = Yes`.
- No appended row is flagged `Exact 0-24 h postoperative opioid? = Yes`.
- The strict primary model is **unchanged at k = 7**, and the pooled estimate
  is numerically identical to the v32 run:

| | k | MD (mg IV MME) | 95% KH CI | p |
|---|---:|---:|---|---:|
| v32 run | 7 | −9.90700 | −20.0794 to +0.2654 | 0.054538 |
| v33 run | 7 | −9.90700 | −20.0794 to +0.2654 | 0.054538 |

Nothing in the supplement met the primary-outcome criteria, exactly as its own
`Primary 0-24h opioid eligible?` column states for all 40 rows. No STOP
condition was triggered.

Specifically excluded from the primary model, as instructed: Yu 2020 binary
rescue sufentanil; Yao 2015 rescue administration counts; Liang 2021 ambiguous
analgesia requirement; all intraoperative opioid outcomes; 48-h outcomes; PCA
presses; PCA volume; reservoir content; graph-only outcomes.

---

## 8. Study count

70 canonical RCTs, unchanged. The supplementary audit was not treated as
grounds to alter eligibility, and no study was removed for failing to
contribute to the primary meta-analysis.

---

## 9. Outputs

| File | Contents |
|---|---|
| `TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx` | 31 sheets; all 29 v32 sheets preserved plus `v33_Change_Log` and `v33_Supplement_Reconciliation` |
| `08_V33_MASTER/build_v33_master.py` | Reproducible build |
| `08_V33_MASTER/qc_v33_master.py` | 26-check pre-analysis gate |
| `08_V33_MASTER/build_v33_analysis_sets.py` | Derived secondary analysis datasets |
| `08_V33_MASTER/01_DATA/*.csv` | Analysis-ready datasets + not-pooled register |
| `08_V33_MASTER/02_STATA/20_v33_secondary.do` | Stata secondary analyses |
| `08_V33_MASTER/03_RESULTS/results_v33_secondary.csv` | Stata results |
| `08_V33_MASTER/04_FIGURES/*.png` | Forest plots |
| `dashboard/v33_data.js` | Generated dashboard layer |
