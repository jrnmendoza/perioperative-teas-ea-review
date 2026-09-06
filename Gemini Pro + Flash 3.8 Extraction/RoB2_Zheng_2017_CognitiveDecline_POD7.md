# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Zheng H, Zhang Y, Wang Y, et al. Effect of transcutaneous electrical acupoint stimulation on postoperative cognitive dysfunction in elderly patients: A randomized controlled trial. Journal of Anesthesia. 2017;31(1):58–65.
- **Source Document in Google Drive:** `covidence_666_full_article.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR-TRC-14004207
- **Population:** 80 elderly patients (aged >= 65 years, ASA I–II) undergoing elective spine or joint surgery under general anesthesia.
- **Intervention:** TEAS applied to Baihui (GV20), Dazhui (GV14), and bilateral Zusanli (ST36) for 30 minutes before anesthesia induction and once daily for 30 minutes on POD 1–3 (dense-disperse 2/100 Hz, current 10–20 mA; n = 40 analyzed).
- **Comparator:** Control group receiving sham TEAS with identical appearance electrodes placed at identical acupoints with 0 mA current delivered (n = 40 analyzed).
- **Assessed Outcome:** Incidence of Postoperative Cognitive Dysfunction (POCD)
- **Assessed Timepoint:** Postoperative Day 7 (POD 7)
- **Numerical Result:**
  - Incidence of POCD on POD 7 was significantly lower in the TEAS group compared with the Control group (4/40 [10.0%] vs. 12/40 [30.0%], P = 0.025). Mini-Mental State Examination (MMSE) scores on POD 7 were also significantly higher in the TEAS group (28.1 ± 1.4 vs. 26.2 ± 1.8, P < 0.001).

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-generated random number table." (p. 59, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "The allocation sequence was sealed in sequentially numbered, opaque envelopes opened prior to induction." (p. 59, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, education level, baseline MMSE score, surgical duration, and anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory difference.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and anesthesiologists managing anesthesia were blinded to group allocation." (p. 60, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized general anesthesia regimen and standardized postoperative multimodal analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 80 randomized (40 TEAS, 40 Control); all 80 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete POD 7 neuropsychological test battery completed for all 80 randomized patients (100% follow-up completion).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Comprehensive battery of validated neuropsychological tests (MMSE and neuropsychological battery).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical evaluation timing at baseline and POD 7.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Neuropsychological evaluations were conducted by designated evaluators blinded to allocation." (p. 60, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR-TRC-14004207).
- **5.2 Result selected:** No (N)
  - **Evidence:** POCD incidence, MMSE scores, and biomarkers reported as prespecified.
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
| **Domain 4: Measurement of the Outcome** | **Low** | Validated neuropsychological battery assessed by blinded evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-induction sensory difference. |

---

### Step 4: Evidence Audit
- covidence_666_full_article.pdf, p. 59, col. 2: "Random numbers were generated using a computer-generated random number table... sealed in sequentially numbered, opaque envelopes..."
- covidence_666_full_article.pdf, p. 62, Table 2: "Incidence of POCD on POD 7: TEAS 4/40 (10.0%) vs. Control 12/40 (30.0%), P = 0.025."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Zheng_2017",
  "source_file": "covidence_666_full_article.pdf",
  "trial_registration": "ChiCTR-TRC-14004207",
  "outcome": "Incidence of POCD",
  "timepoint": "Postoperative Day 7 (POD 7)",
  "sample_size": {
    "teas": 40,
    "control": 40,
    "total": 80
  },
  "result": {
    "teas_events": 4,
    "control_events": 12,
    "teas_pct": 10.0,
    "control_pct": 30.0,
    "p_value": 0.025
  },
  "overall_rob": "Some concerns"
}
```
