# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Zhang Y, Wang H, Sun M, et al. Effects of Transcutaneous Electrical Acupoint Stimulation on Postoperative Acute Visceral, Incisional, and Inflammatory Pain Following Laparoscopic Colorectal Cancer Surgery: A Randomized Controlled Trial. Journal of Pain Research. 2025;18:1125–1138.
- **Source Document in Google Drive:** `109551.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2400093634
- **Population:** 86 patients (aged 18–75 years, ASA I–III) undergoing elective laparoscopic radical resection of colorectal cancer.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36), Shangjuxu (ST37), and Sanyinjiao (SP6) once daily for 30 minutes from Postoperative Day 0 (PACU) through Postoperative Day 3 (dense-disperse frequency 2/100 Hz, current 10–20 mA; n = 43 analyzed).
- **Comparator:** Sham TEAS with electrode placement on non-acupoints (1.5 cm lateral to ST36, ST37, and SP6) without electrical stimulation (0 mA; n = 43 analyzed).
- **Assessed Outcome:** Acute Visceral Pain Score (NRS 0–10)
- **Assessed Timepoint:** Postoperative Day 1 (POD 1)
- **Numerical Result:**
  - Visceral pain score on POD 1 was significantly lower in the TEAS group compared with the Sham group (mean ± SD: 2.31 ± 0.74 vs. 3.48 ± 0.86, P < 0.001). Total cumulative sufentanil consumption from POD 0 to POD 3 was also significantly reduced in the TEAS group (78.4 ± 12.2 µg vs. 104.6 ± 15.8 µg, P < 0.001).

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was performed using Stata 16.0 software to generate a random sequence." (p. 1127, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Sequentially numbered, opaque, sealed envelopes were used for allocation concealment... opened by a dedicated research nurse." (p. 1127, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor stage, surgical approach, operative duration, and blood loss were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Sham stimulation performed using identical electrodes at non-acupoint with 0 mA current; blinding index confirmed successful blinding.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation throughout the trial." (p. 1127, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized ERAS multimodal analgesic regimen (flurbiprofen axetil + sufentanil PCIA) administered identically.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 86 randomized (43 TEAS, 43 Sham); all 86 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete visceral pain records available for all 86 randomized participants through POD 3 (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated Numerical Rating Scale (NRS 0–10) differentiated specifically for visceral, incisional, and low back pain components.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Standardized testing and definition applied uniformly across both groups.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Outcome assessors were trained, independent, and strictly blinded to treatment allocation." (p. 1127, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2400093634).
- **5.2 Result selected:** No (N)
  - **Evidence:** Visceral, incisional, and low back pain scores reported across POD 0, POD 1, POD 2, POD 3.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Prespecified repeated measures and ANOVA analyses.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Stata computer generation, sequentially numbered sealed opaque envelopes, balanced baseline. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind design with identical sham non-acupoints and 0 mA stimulation. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing outcome data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated NRS differentiated pain measurement by blinded assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- 109551.pdf, p. 1127, col. 1: "Randomization was performed using Stata... Sequentially numbered, opaque, sealed envelopes were used..."
- 109551.pdf, p. 1130, Table 2: "Visceral pain score on POD 1: TEAS 2.31 ± 0.74 vs. Sham 3.48 ± 0.86, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Zhang_2025",
  "source_file": "109551.pdf",
  "trial_registration": "ChiCTR2400093634",
  "outcome": "Acute visceral pain score (NRS)",
  "timepoint": "Postoperative Day 1 (POD 1)",
  "sample_size": {
    "teas": 43,
    "sham": 43,
    "total": 86
  },
  "result": {
    "teas_mean": 2.31,
    "teas_sd": 0.74,
    "sham_mean": 3.48,
    "sham_sd": 0.86,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
