# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Wang L, Zhou Y, Zhu Q, et al. Transcutaneous Electrical Acupoint Stimulation Improves Postoperative Sleep Quality in Patients Undergoing Gastrointestinal Cancer Surgery: A Prospective, Randomized Controlled Trial. Pain and Therapy. 2023;12(3):811–825.
- **Source Document in Google Drive:** `s40122-023-00493-2.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2100054971
- **Population:** 120 patients (aged 18–75 years, ASA I–III) undergoing elective laparoscopic gastrointestinal cancer surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Shenmen (HT7), Neiguan (PC6), and Sanyinjiao (SP6) for 30 minutes in the evening before sleep from POD 1 to POD 3 (dense-disperse 2/100 Hz, current 10–20 mA; n = 60 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes placed at identical acupoints with 0 mA electrical current (n = 60 analyzed).
- **Assessed Outcome:** Subjective Sleep Quality Score (Athens Insomnia Scale, AIS)
- **Assessed Timepoint:** Postoperative Day 1 (POD 1)
- **Numerical Result:**
  - Athens Insomnia Scale score on POD 1 was significantly lower (indicating better sleep) in the TEAS group compared with the Sham group (mean ± SD: 6.4 ± 1.8 vs. 9.8 ± 2.2, P < 0.001). Total sleep duration and subjective sleep efficiency recorded by actigraphy were also significantly superior in the TEAS group.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was generated using a computer-generated random number table created by SPSS 25.0." (p. 813, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocations were concealed in sequentially numbered, opaque, sealed envelopes opened by an independent acupuncturist." (p. 813, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, baseline AIS sleep score, surgical type, and operative duration were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Stimulation delivered in evening to awake patients; distinct tingling sensation in active TEAS vs. zero current in sham device.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and treating clinical staff were blinded to group assignments." (p. 814, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized ward sleep environment and standardized postoperative multimodal analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 120 randomized (60 TEAS, 60 Sham); all 120 completed follow-up and were analyzed (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete sleep quality and actigraphy data available for all 120 randomized patients (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated Athens Insomnia Scale (AIS) combined with objective wrist actigraphy recording.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform morning questionnaire administration and continuous actigraphy across both arms.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained sleep evaluators who administered questionnaires and analyzed actigraphy data were strictly blinded." (p. 814, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2100054971) on December 29, 2021.
- **5.2 Result selected:** No (N)
  - **Evidence:** AIS sleep scores, sleep efficiency, and pain scores reported across POD 1, POD 2, POD 3.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sequentially numbered sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake postoperative sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing outcome data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated scale and objective actigraphy assessed by blinded evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake postoperative sensory difference. |

---

### Step 4: Evidence Audit
- s40122-023-00493-2.pdf, p. 813, col. 1: "Randomization was generated using a computer-generated random number table... concealed in sequentially numbered, opaque, sealed envelopes..."
- s40122-023-00493-2.pdf, p. 817, Table 2: "AIS score on POD 1: TEAS 6.4 ± 1.8 vs. Sham 9.8 ± 2.2, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Wang_2023_Sleep",
  "source_file": "s40122-023-00493-2.pdf",
  "trial_registration": "ChiCTR2100054971",
  "outcome": "Athens Insomnia Scale score",
  "timepoint": "Postoperative Day 1 (POD 1)",
  "sample_size": {
    "teas": 60,
    "sham": 60,
    "total": 120
  },
  "result": {
    "teas_mean": 6.4,
    "teas_sd": 1.8,
    "sham_mean": 9.8,
    "sham_sd": 2.2,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
