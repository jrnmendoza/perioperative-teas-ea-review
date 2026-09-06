# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Coura LE, Manoel CH, Moyses AM, et al. Electroacupuncture in postoperative pain: a randomized, double-blind, sham-controlled clinical trial. Acupuncture in Medicine. 2011;29(1):16–20.
- **Source Document in Google Drive:** `covidence_819_full_article.pdf`
- **Trial Registration:** None reported
- **Population:** 90 patients (aged 18–65 years, ASA I–II) undergoing hemorrhoidectomy under spinal anesthesia at Unimed Hospital Centre, Joinville, Brazil.
- **Intervention:** Preoperative electroacupuncture applied to bilateral Chengshan (BL57), Ciliao (BL32), and Sanyinjiao (SP6) for 30 minutes (mixed frequency 2/100 Hz; n = 30 analyzed).
- **Comparator:** Sham transcutaneous electrical stimulation with inactive electrodes placed over the same acupoints with no electrical current (0 mA; n = 30 analyzed). A third control group received standard care alone (n = 30).
- **Assessed Outcome:** Postoperative Morphine Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Cumulative morphine consumption over 24 hours was significantly lower in the EA group compared with the Sham group and Control group (mean ± SD: 4.2 ± 3.1 mg vs. 11.5 ± 5.2 mg vs. 13.8 ± 6.0 mg, P < 0.01). Pain scores at rest and during first defecation were also significantly lower in the EA group.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled 3-arm clinical trial.
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Patients were randomly allocated to one of three groups using a random numbers table." (p. 17, col. 1).
- **1.2 Allocation concealment:** No Information (NI)
  - **Evidence:** The specific method used to conceal the sequence (e.g. sealed envelopes) is not detailed in the paper.
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, surgical duration, and baseline characteristics were comparable across the three groups (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Some concerns Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Acupuncture needles with deqi sensation and electrical stimulation vs. surface sham TENS electrodes with 0 mA current; awake patients may perceive needle penetration vs. pad.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** Surgical team and ward nurses administering postop analgesia were blinded.
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized spinal anesthesia and standardized PRN morphine analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 90 randomized (30 per group); all 90 analyzed in their assigned groups.
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome data obtained for all 90 participants (100% follow-up).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Nursing documentation of administered morphine doses (mg).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Standardized PRN prescription and pain assessment protocol across all hospital rooms.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Ward nurses evaluating pain and administering rescue medication were blinded to group allocation." (p. 17, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No trial registration number or protocol publication cited in the manuscript.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Morphine requirements and pain scores reported at all measured intervals.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard parametric analysis.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Some concerns** | Allocation concealment mechanism not reported. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake physical difference between invasive needle EA with tingling and non-invasive surface sham TENS. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing outcome data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Blinded ward nursing staff administering rescue analgesia. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Lack of prospective clinical trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 1 (unclear concealment), Domain 2 (needle vs. sham pad sensation), and Domain 5 (unregistered). |

---

### Step 4: Evidence Audit
- covidence_819_full_article.pdf, p. 17, col. 1: "Patients were randomly allocated to one of three groups using a random numbers table..."
- covidence_819_full_article.pdf, p. 18, Table 2: "Morphine consumption at 24 h: EA 4.2 ± 3.1 mg vs. Sham 11.5 ± 5.2 mg vs. Control 13.8 ± 6.0 mg, P < 0.01."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Coura_2011",
  "source_file": "covidence_819_full_article.pdf",
  "trial_registration": "None reported",
  "outcome": "Morphine consumption",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "ea": 30,
    "sham": 30,
    "control": 30,
    "total": 90
  },
  "result": {
    "ea_mean": 4.2,
    "ea_sd": 3.1,
    "sham_mean": 11.5,
    "sham_sd": 5.2,
    "control_mean": 13.8,
    "control_sd": 6.0,
    "p_value": "<0.01"
  },
  "overall_rob": "Some concerns"
}
```
