# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Liu H, Zhao M, Gao X, et al. Effects of Transcutaneous Electrical Acupoint Stimulation on Postoperative Cognitive Decline in Elderly Patients Undergoing Laparoscopic Colorectal Surgery: A Randomized Controlled Trial. Journal of Pain Research. 2021;14:3125–3136.
- **Source Document in Google Drive:** `getfile.php-2.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2000040397
- **Population:** 110 elderly patients (aged 65–80 years, ASA I–III) scheduled for elective laparoscopic colorectal cancer resection under general anesthesia.
- **Intervention:** TEAS applied to Baihui (GV20), Dazhui (GV14), and bilateral Zusanli (ST36) for 30 min before anesthesia induction and once daily for 30 min on POD 1–3 (dense-disperse 2/100 Hz, current 10–20 mA; n = 55 analyzed).
- **Comparator:** Control group receiving sham TEAS with identical appearance electrodes placed at identical acupoints with 0 mA current delivered (n = 55 analyzed).
- **Assessed Outcome:** Incidence of Postoperative Cognitive Decline (POCD)
- **Assessed Timepoint:** Postoperative Day 7 (POD 7)
- **Numerical Result:**
  - Incidence of POCD (defined as a decline of >= 1 standard deviation on >= 2 neuropsychological tests) on POD 7 was significantly lower in the TEAS group compared with the Control group (6/55 [10.9%] vs. 15/55 [27.3%], P = 0.028). Postoperative serum S100B and NSE levels were also significantly lower in the TEAS group.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-generated random number table prepared by an independent statistician." (p. 3126, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "The allocation sequence was sealed in sequentially numbered, opaque envelopes opened prior to induction." (p. 3126, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, education level, baseline MMSE score, tumor site, surgical duration, and blood loss were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory difference.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and anesthesiologists managing anesthesia were blinded to group allocation." (p. 3127, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized general anesthesia regimen and standardized postoperative multimodal analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 110 randomized (55 TEAS, 55 Control); all 110 analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete POD 7 neuropsychological test battery completed for all 110 randomized patients (100% follow-up completion).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Comprehensive battery of validated neuropsychological tests (MMSE, MoCA, Digit Span, Trail Making Tests A and B).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical evaluation timing at baseline and POD 7.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Neuropsychological evaluations were conducted by designated psychologists blinded to allocation." (p. 3127, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2000040397) on November 28, 2020.
- **5.2 Result selected:** No (N)
  - **Evidence:** POCD incidence, individual test scores, and neurobiomarkers reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified dichotomous event analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sequentially numbered sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake pre-induction sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated neuropsychological battery assessed by blinded psychologists. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-induction sensory difference. |

---

### Step 4: Evidence Audit
- getfile.php-2.pdf, p. 3126, col. 2: "Random numbers were generated using a computer-generated random number table... sealed in sequentially numbered, opaque envelopes..."
- getfile.php-2.pdf, p. 3129, Table 2: "Incidence of POCD on POD 7: TEAS 6/55 (10.9%) vs. Control 15/55 (27.3%), P = 0.028."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Liu_2021_Cognitive",
  "source_file": "getfile.php-2.pdf",
  "trial_registration": "ChiCTR2000040397",
  "outcome": "Incidence of POCD",
  "timepoint": "Postoperative Day 7 (POD 7)",
  "sample_size": {
    "teas": 55,
    "control": 55,
    "total": 110
  },
  "result": {
    "teas_events": 6,
    "control_events": 15,
    "teas_pct": 10.9,
    "control_pct": 27.3,
    "p_value": 0.028
  },
  "overall_rob": "Some concerns"
}
```
