# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Guo J, Li N, Wang J, et al. Effects of transcutaneous electrical acupoint stimulation on postoperative recovery after laparoscopic bariatric surgery: A randomized controlled trial. Heliyon. 2023;9(9):e19386.
- **Source Document in Google Drive:** `006_guo_2023.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2000035552
- **Population:** 128 obese patients (BMI >= 32.5 kg/m2, ASA II–III) undergoing elective laparoscopic sleeve gastrectomy under general anesthesia.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36), Shangjuxu (ST37), and Hegu (LI4) 30 min before anesthesia induction and once daily for 30 min on POD 1–2 (dense-disperse 2/100 Hz, current 10–20 mA; n = 64 analyzed).
- **Comparator:** Sham TEAS with identical electrodes placed at identical acupoints with 0 mA current delivered (n = 64 analyzed).
- **Assessed Outcome:** Time to First Postoperative Flatus
- **Assessed Timepoint:** Postoperative Day 1 to Day 3
- **Numerical Result:**
  - Time to first postoperative flatus was significantly shorter in the TEAS group compared with the Sham group (mean ± SD: 28.4 ± 6.2 h vs. 36.8 ± 7.9 h, P < 0.001). Postoperative resting and coughing VAS pain scores, opioid requirements, and QoR-15 scores were also significantly improved.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using SPSS 25.0 software by an independent statistician." (p. 3, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Sequentially numbered, opaque, sealed envelopes were used to conceal the random sequence." (p. 3, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, comorbidities, surgical duration, and anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered awake; active tingling sensation (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory difference.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation." (p. 3, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized bariatric ERAS pathway and standardized rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 128 randomized (64 TEAS, 64 Sham); all 128 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete follow-up data available for all 128 randomized patients (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Nurse-verified recording of the exact time of first flatus passage in hours.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform nursing documentation schedule across all patients.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Designated outcome evaluators were blinded to group assignments." (p. 3, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2000035552).
- **5.2 Result selected:** No (N)
  - **Evidence:** Time to flatus, defecation, pain scores, and QoR-15 scores reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake pre-induction sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Nurse-verified objective timing and blinded outcome evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-induction sensory difference. |

---

### Step 4: Evidence Audit
- 006_guo_2023.pdf, p. 3, col. 1: "Random numbers were generated using SPSS 25.0 software... Sequentially numbered, opaque, sealed envelopes were used..."
- 006_guo_2023.pdf, p. 5, Table 2: "Time to first flatus: TEAS 28.4 ± 6.2 h vs. Sham 36.8 ± 7.9 h, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Guo_2023",
  "source_file": "006_guo_2023.pdf",
  "trial_registration": "ChiCTR2000035552",
  "outcome": "Time to first flatus",
  "timepoint": "Postoperative Day 1 to Day 3",
  "sample_size": {
    "teas": 64,
    "sham": 64,
    "total": 128
  },
  "result": {
    "teas_mean": 28.4,
    "teas_sd": 6.2,
    "sham_mean": 36.8,
    "sham_sd": 7.9,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
