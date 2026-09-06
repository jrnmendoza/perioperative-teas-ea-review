# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Yao Y, Bian W, Cheng W, et al. Transcutaneous Electrical Acupoint Stimulation Improves the Postoperative Quality of Recovery and Analgesia after Gynecological Laparoscopic Surgery: A Randomized Controlled Trial. Evidence-Based Complementary and Alternative Medicine. 2015;2015:438706.
- **Source Document in Google Drive:** `039_yao_2015.pdf`
- **Trial Registration:** None reported
- **Population:** 70 female patients (aged 20–60 years, ASA I–II) scheduled for elective gynecological laparoscopic surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Hegu (LI4) and Sanyinjiao (SP6) for 30 min before anesthesia induction and once daily for 30 min on POD 1 (dense-disperse 2/100 Hz, current 10–20 mA; n = 35 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with the stimulator turned off (0 mA; n = 35 analyzed).
- **Assessed Outcome:** Quality of Recovery-40 (QoR-40) Total Score
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Global QoR-40 score at 24 hours postoperatively was significantly higher in the TEAS group compared with the Sham group (mean ± SD: 178.4 ± 8.6 vs. 165.2 ± 10.4, P < 0.001). All five recovery dimensions (physical comfort, emotional state, physical independence, psychological support, and pain) showed significant improvements.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was performed using a random number table." (p. 2, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocations were kept in sealed, opaque, sequentially numbered envelopes opened prior to induction." (p. 2, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, weight, baseline QoR-40, surgical duration, and intraoperative anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction awake stimulation with active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory difference.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, intraoperative anesthesiologists, and ward nurses were blinded to grouping." (p. 2, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized balanced general anesthesia and postoperative rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 70 randomized (35 TEAS, 35 Sham); all 70 completed follow-up and were analyzed (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete QoR-40 questionnaire completed for all 70 randomized participants (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated QoR-40 multidimensional questionnaire (score range 40–200).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform administration at exactly 24 h postoperatively.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Postoperative questionnaire evaluations were carried out by a dedicated investigator blinded to allocation." (p. 2, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No prospective clinical trial registration number or protocol publication cited in the manuscript.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Total QoR-40 score and all five individual sub-domain scores reported.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard parametric analysis.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Random number table, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Pre-induction awake sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated multidimensional instrument administered by blinded evaluator. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Lack of prospective clinical trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 (awake sensory difference) and Domain 5 (unregistered trial). |

---

### Step 4: Evidence Audit
- 039_yao_2015.pdf, p. 2, col. 2: "Allocations were kept in sealed, opaque, sequentially numbered envelopes..."
- 039_yao_2015.pdf, p. 4, Table 2: "QoR-40 total score at 24 h: TEAS 178.4 ± 8.6 vs. Sham 165.2 ± 10.4, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Yao_2015",
  "source_file": "039_yao_2015.pdf",
  "trial_registration": "None reported",
  "outcome": "QoR-40 total score",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "teas": 35,
    "sham": 35,
    "total": 70
  },
  "result": {
    "teas_mean": 178.4,
    "teas_sd": 8.6,
    "sham_mean": 165.2,
    "sham_sd": 10.4,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
