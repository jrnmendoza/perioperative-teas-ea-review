# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Liu T, Zhang X, Zhou C, et al. Effects of electroacupuncture on supraventricular arrhythmia and sleep quality in patients undergoing thoracoscopic lung surgery: A randomized controlled trial. Frontiers in Neurology. 2025;16:1394208.
- **Source Document in Google Drive:** `pdf.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2300077984
- **Population:** 120 adult patients (aged 18–75 years, ASA I–II) undergoing thoracoscopic pulmonary resection under general anesthesia.
- **Intervention:** Electroacupuncture applied to bilateral Neiguan (PC6), Shenmen (HT7), and Xinshu (BL15) for 30 minutes in the evening on POD 1 to POD 3 (dense-disperse 2/100 Hz, current 1–2 mA; n = 60 analyzed).
- **Comparator:** Sham EA using non-penetrating blunt needles placed at identical acupoints with no electrical current (0 mA; n = 60 analyzed).
- **Assessed Outcome:** Subjective Sleep Efficiency (Athens Insomnia Scale, AIS)
- **Assessed Timepoint:** Postoperative Day 1 (POD 1)
- **Numerical Result:**
  - Athens Insomnia Scale score on POD 1 was significantly lower (better sleep quality) in the EA group compared with the Sham group (mean ± SD: 5.8 ± 1.6 vs. 8.9 ± 2.1, P < 0.001). Cumulative incidence of postoperative supraventricular arrhythmia (SVA) was also significantly lower in the EA group (8/60 [13.3%] vs. 20/60 [33.3%], P = 0.009).

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was generated using a computer-generated random number table." (p. 2, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation concealment was achieved using sequentially numbered, opaque, sealed envelopes." (p. 2, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, baseline sleep score, lung resection type, and operative duration were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Non-penetrating blunt sham needles and sensory deception used; blinding questionnaire indicated successful blinding.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Thoracic surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation." (p. 3, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized thoracic ERAS care pathway and telemetry monitoring protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 120 randomized (60 EA, 60 Sham); all 120 completed follow-up and were analyzed (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete sleep and Holter ECG telemetry data available for all 120 randomized patients (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated Athens Insomnia Scale (AIS) combined with continuous automated Holter electrocardiogram telemetry.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform telemetry and survey administration schedule across all patients.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Cardiologists analyzing Holter data and outcome assessors evaluating AIS scores were strictly blinded." (p. 3, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2300077984) on November 24, 2023.
- **5.2 Result selected:** No (N)
  - **Evidence:** Sleep scores, arrhythmia incidence, and heart rate variability metrics reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified continuous and survival analyses.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham needle design with validated blinding and full ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Objective telemetry and validated scale assessed by blinded experts. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- pdf.pdf, p. 2, col. 2: "Allocation concealment was achieved using sequentially numbered, opaque, sealed envelopes..."
- pdf.pdf, p. 4, Table 2: "AIS score on POD 1: EA 5.8 ± 1.6 vs. Sham 8.9 ± 2.1, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Liu_2025_Sleep",
  "source_file": "pdf.pdf",
  "trial_registration": "ChiCTR2300077984",
  "outcome": "Athens Insomnia Scale score",
  "timepoint": "Postoperative Day 1 (POD 1)",
  "sample_size": {
    "ea": 60,
    "sham": 60,
    "total": 120
  },
  "result": {
    "ea_mean": 5.8,
    "ea_sd": 1.6,
    "sham_mean": 8.9,
    "sham_sd": 2.1,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
