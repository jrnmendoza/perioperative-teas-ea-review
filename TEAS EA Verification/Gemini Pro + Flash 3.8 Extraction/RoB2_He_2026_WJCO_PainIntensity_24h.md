# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** He L, Chen M, Liu Y, et al. Efficacy of transcutaneous electrical acupoint stimulation on postoperative immune function and analgesia in cancer surgery: A randomized controlled trial. World Journal of Clinical Oncology. 2026;17(2):114431.
- **Source Document in Google Drive:** `covidence_41_verified.pdf`
- **Trial Registration:** None reported
- **Population:** 130 adult patients (aged 18–75 years, ASA I–III) undergoing elective gastrointestinal cancer surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36), Hegu (LI4), and Sanyinjiao (SP6) for 30 minutes before anesthesia induction and once daily for 30 minutes on POD 1–2 (dense-disperse 2/100 Hz, current 10–20 mA; n = 65 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with 0 mA current delivered (n = 65 analyzed).
- **Assessed Outcome:** Postoperative Pain Intensity at Rest (VAS 0–10)
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - VAS pain score at rest at 24 hours postoperatively was significantly lower in the TEAS group compared with the Sham group (mean ± SD: 2.2 ± 0.6 vs. 3.6 ± 0.8, P < 0.001). Postoperative rescue analgesic consumption was significantly reduced and natural killer (NK) cell activity was significantly better preserved in the TEAS group.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was generated using a computer-generated random number table." (p. 4, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Group assignments were enclosed in sequentially numbered, opaque, sealed envelopes." (p. 4, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor clinical stage, surgical duration, and blood loss were comparable between groups (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory contrast.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation." (p. 4, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized general anesthesia regimen and standardized rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 130 randomized (65 TEAS, 65 Sham); all 130 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome records available for all 130 randomized patients (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated Visual Analog Scale (VAS 0–10).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform evaluation schedule across all patients.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome evaluators were blinded to patient grouping." (p. 4, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No prospective clinical trial registration number or protocol publication cited in the manuscript.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Pain scores at 6, 12, 24, 48 h, rescue analgesia, and immune parameters reported as prespecified.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake pre-induction sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Standardized VAS assessed by blinded evaluators. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Lack of prospective clinical trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 (awake sensory difference) and Domain 5 (unregistered trial). |

---

### Step 4: Evidence Audit
- covidence_41_verified.pdf, p. 4, col. 1: "Randomization was generated using a computer-generated random number table... enclosed in sequentially numbered, opaque, sealed envelopes..."
- covidence_41_verified.pdf, p. 7, Table 2: "VAS pain score at 24 h: TEAS 2.2 ± 0.6 vs. Sham 3.6 ± 0.8, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "He_2026_WJCO",
  "source_file": "covidence_41_verified.pdf",
  "trial_registration": "None reported",
  "outcome": "Pain intensity at rest (VAS)",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "teas": 65,
    "sham": 65,
    "total": 130
  },
  "result": {
    "teas_mean": 2.2,
    "teas_sd": 0.6,
    "sham_mean": 3.6,
    "sham_sd": 0.8,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
