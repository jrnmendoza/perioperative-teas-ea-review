# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Yeh ML, Tsou TS, Lee BY, et al. Acupoint electrical stimulation reduces acute postoperative pain in surgical patients: A randomized, controlled clinical trial. Alternative Therapies in Health and Medicine. 2004;10(5):38–45.
- **Source Document in Google Drive:** `015_PainATHM-2.pdf`
- **Trial Registration:** None reported
- **Population:** 99 adult patients undergoing elective open abdominal or orthopedic surgery under general anesthesia.
- **Intervention:** Transcutaneous electrical acupoint stimulation applied to bilateral Hegu (LI4) and Zusanli (ST36) postoperatively for 30 minutes twice daily (dense-disperse 2/100 Hz; n = 50 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to non-acupoints without electrical current (0 mA; n = 49 analyzed).
- **Assessed Outcome:** Cumulative Postoperative Morphine Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Cumulative morphine consumption at 24 hours was significantly lower in the TEAS group compared with the Sham group (mean ± SD: 22.4 ± 8.6 mg vs. 34.2 ± 11.4 mg, P < 0.001). Resting and active pain VAS scores were also significantly reduced.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, single-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Patients were randomly allocated to either TEAS or sham stimulation using a random numbers table." (p. 40, col. 1).
- **1.2 Allocation concealment:** Probably Yes (PY)
  - **Evidence:** "Allocation was managed using sequentially numbered sealed envelopes prepared prior to trial initiation." (p. 40, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, surgical types, baseline pain, and intraoperative anesthetic doses were comparable (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Postoperative TEAS delivered while awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory contrast.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and clinical care teams were blinded to group allocation." (p. 40, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized PCA morphine rescue analgesia protocol administered uniformly.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 99 randomized (50 TEAS, 49 Sham); all 99 completed follow-up and were analyzed (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome records available for all 99 randomized patients (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Microprocessor PCA pump documentation of cumulative morphine consumption (mg).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical PCA parameters across both groups.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome evaluators who recorded PCA use were blinded to allocation." (p. 41, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No prospective clinical trial registration number or protocol publication cited in the manuscript.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Morphine consumption, VAS pain scores, and side effect rates reported across all evaluated time points.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Random number table, sealed envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake postoperative sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Electronic PCA pump records and blinded outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Lack of prospective clinical trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 (awake sensory difference) and Domain 5 (unregistered trial). |

---

### Step 4: Evidence Audit
- 015_PainATHM-2.pdf, p. 40, col. 1: "Patients were randomly allocated using a random numbers table... sequentially numbered sealed envelopes..."
- 015_PainATHM-2.pdf, p. 42, Table 2: "Morphine consumption at 24 h: TEAS 22.4 ± 8.6 mg vs. Sham 34.2 ± 11.4 mg, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Yeh_2004",
  "source_file": "015_PainATHM-2.pdf",
  "trial_registration": "None reported",
  "outcome": "Cumulative morphine consumption",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "teas": 50,
    "sham": 49,
    "total": 99
  },
  "result": {
    "teas_mean": 22.4,
    "teas_sd": 8.6,
    "sham_mean": 34.2,
    "sham_sd": 11.4,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
