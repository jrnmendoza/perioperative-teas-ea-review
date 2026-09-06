# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Xiao W, Wang L, Zhu Q, et al. Effects of transcutaneous electrical acupoint stimulation on postoperative recovery in patients undergoing gynecological laparoscopic surgery: A randomized controlled trial. BMC Anesthesiology. 2022;22:312.
- **Source Document in Google Drive:** `s12871-022-01875-3.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR1800014634
- **Population:** 84 female patients (aged 20–60 years, ASA I–II) scheduled for elective gynecological laparoscopic surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Hegu (LI4), Neiguan (PC6), and Zusanli (ST36) for 30 minutes before anesthesia induction and once daily for 30 minutes on POD 1 (dense-disperse 2/100 Hz, current 10–20 mA; n = 42 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with 0 mA current delivered (n = 42 analyzed).
- **Assessed Outcome:** Quality of Recovery-40 (QoR-40) Total Score
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Global QoR-40 score at 24 hours postoperatively was significantly higher in the TEAS group compared with the Sham group (mean ± SD: 176.4 ± 9.8 vs. 164.2 ± 11.5, P < 0.001). Postoperative resting and coughing VAS pain scores, nausea incidence, and time to first ambulation were also significantly improved.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-generated random allocation sequence prepared by an independent statistician." (p. 2, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "The allocation sequence was concealed in sequentially numbered, opaque, sealed envelopes." (p. 2, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, BMI, surgical duration, baseline QoR-40 score, and intraoperative anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory contrast.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation." (p. 3, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized general anesthesia regimen and standardized postoperative rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 84 randomized (42 TEAS, 42 Sham); all 84 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete QoR-40 questionnaires obtained for all 84 randomized patients (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated QoR-40 multidimensional questionnaire.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform administration at exactly 24 h postoperatively.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome assessors who administered questionnaires were blinded to group allocation." (p. 3, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR1800014634) on January 26, 2018.
- **5.2 Result selected:** No (N)
  - **Evidence:** QoR-40 total and sub-domain scores, pain scores, and PONV rates reported as prespecified.
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
| **Domain 4: Measurement of the Outcome** | **Low** | Validated instrument administered by blinded outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-induction sensory difference. |

---

### Step 4: Evidence Audit
- s12871-022-01875-3.pdf, p. 2, col. 2: "Random numbers were generated using a computer-generated random allocation sequence... concealed in sequentially numbered, opaque, sealed envelopes..."
- s12871-022-01875-3.pdf, p. 4, Table 2: "QoR-40 score at 24 h: TEAS 176.4 ± 9.8 vs. Sham 164.2 ± 11.5, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Xiao_2022",
  "source_file": "s12871-022-01875-3.pdf",
  "trial_registration": "ChiCTR1800014634",
  "outcome": "QoR-40 total score",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "teas": 42,
    "sham": 42,
    "total": 84
  },
  "result": {
    "teas_mean": 176.4,
    "teas_sd": 9.8,
    "sham_mean": 164.2,
    "sham_sd": 11.5,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
