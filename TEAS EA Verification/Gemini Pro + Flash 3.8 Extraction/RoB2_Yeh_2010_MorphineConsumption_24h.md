# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Yeh ML, Chung YC, Chen KM, Chen HH. Pain reduction of acupoint electrical stimulation for patients with spinal surgery: A placebo-controlled study. *Anaesthesia*. 2010;65(1):19–24.
- **Source Document in Google Drive:** `covidence_828_full_article.pdf`
- **Trial Registration:** Not reported / omitted in text
- **Population:** 90 patients undergoing spinal surgery (lumbar discectomy/laminectomy) under general anesthesia.
- **Intervention (AES group):** Acupoint electrical stimulation at bilateral Zusanli (ST36), Yanglingquan (GB34), and Chengshan (BL57) using Pointron instrument (100 Hz, 15–25 mA) for 20 min on POD 1 (n = 30).
- **Comparator 1 (Sham AES):** Identical electrodes placed on non-acupoints (1.5–2.0 cm away) connected to stimulator with zero current output (0 mA), told frequency is sub-sensory (n = 30).
- **Comparator 2 (Control):** Conventional postoperative care alone (n = 30).
- **Assessed Outcome:** Postoperative PCA Morphine Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:** 
  - AES group (n = 30): Mean 28.3 ± 11.6 mg
  - Sham AES group (n = 30): Mean 38.6 ± 13.9 mg
  - Control group (n = 30): Mean 45.1 ± 16.2 mg
  - Difference: One-way ANOVA $F = 11.23$, $P = 0.001$; Scheffe's post hoc test $P < 0.05$ for AES vs. Sham and AES vs. Control

---

### Step 1: Study Design Verification
- **Experimental Design:** 3-arm randomized, placebo-controlled parallel trial (1:1:1 allocation ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y) — "randomisation was achieved through a computer-generated random number table" (`covidence_828_full_article.pdf`, p. 20, col. 2).
- **1.2 Allocation concealment:** No Information (NI) — Concealment mechanism not reported.
- **1.3 Baseline balance:** No (N) — Age, sex, spinal surgical level, and anesthesia duration balanced ($P > 0.05$; Table 1).
- **Domain 1 Judgment:** **Some Concerns** (due to missing concealment details).

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN) for AES vs. Sham — Inactive mock stimulator with sub-sensory deception. For AES vs. Control: Yes (open-label).
- **2.2 Carers awareness:** Probably No (PN) — Ward nurses managing PCA pumps were blinded to AES vs. Sham allocation.
- **2.3 Contextual deviations:** No (N) — Standardized IV-PCA morphine protocol: 1 mg bolus, 5-min lockout.
- **2.5 Appropriate analysis:** Yes (Y) — All 90 randomized participants analyzed (30 per arm; 100% complete).
- **Domain 2 Judgment:** **Low Risk of Bias** (for sham comparison).

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y) — 90 of 90 patients (100%) completed follow-up.
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N) — Objective PCA pump cumulative morphine log.
- **4.2 Differ between groups:** No (N)
- **4.3 Assessors aware:** No (N) — Assessors blinded to AES vs. Sham allocation.
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI) — Registry identifier not reported.
- **5.2 Result selected:** Probably No (PN) — Standard 24-h morphine consumption reported.
- **5.3 Multiple analyses:** Probably No (PN)
- **Domain 5 Judgment:** **Some Concerns** (unregistered protocol).

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Some concerns** | Computer-generated table, but concealment details omitted. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Sham control with sub-sensory blinding; 100% complete analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Complete follow-up for 100% of participants. |
| **Domain 4: Measurement of the Outcome** | **Low** | Objective electronic PCA pump records. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Registry record omitted. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Driven by Domains 1 and 5. |

---

### Step 4: Evidence Audit
- `covidence_828_full_article.pdf`, p. 20, col. 2: "randomisation was achieved through a computer-generated random number table".
- `covidence_828_full_article.pdf`, p. 21–22: "Total PCA morphine used (mg): AES 28.3 ± 11.6 vs. Sham 38.6 ± 13.9 vs. Control 45.1 ± 16.2, F = 11.23, P = 0.001."

---

### Step 5: Author Contact Flags
- Request clarification on allocation concealment and pre-specified trial protocol.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Yeh_2010",
  "source_file": "covidence_828_full_article.pdf",
  "outcome": "Postoperative PCA Morphine Consumption",
  "timepoint": "24 hours postoperative",
  "sample_size": {"aes": 30, "sham": 30, "control": 30, "total": 90},
  "result": {"aes_mean": 28.3, "aes_sd": 11.6, "sham_mean": 38.6, "sham_sd": 13.9, "control_mean": 45.1, "control_sd": 16.2, "p_value": 0.001},
  "overall_rob": "Some concerns"
}
```
