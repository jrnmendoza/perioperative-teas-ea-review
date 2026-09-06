# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Li W, Xu Y, Yang X, et al. Perioperative transcutaneous electrical acupoint stimulation for improving postoperative gastrointestinal function: A randomized controlled trial. Journal of Integrative Medicine. 2021;19(3):211–218.
- **Source Document in Google Drive:** `covidence_437_full_article.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR1900023263
- **Population:** 120 patients (aged 18–75 years, ASA I–III) scheduled for elective laparoscopic gastrointestinal surgery (gastric or colorectal cancer resection).
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Shangjuxu (ST37) 30 min before anesthesia induction and once daily for 30 min on POD 1–3 (dense-disperse 2/100 Hz, current 10–20 mA; n = 60 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with zero current delivered (0 mA; n = 60 analyzed).
- **Assessed Outcome:** Time to First Postoperative Flatus
- **Assessed Timepoint:** Postoperative Day 1 to Day 4
- **Numerical Result:**
  - Time to first postoperative flatus was significantly shorter in the TEAS group compared with the Sham group (mean ± SD: 58.4 ± 14.2 h vs. 72.8 ± 16.5 h, P < 0.001). Time to first bowel sound and first defecation were also significantly accelerated in the TEAS group.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio stratified by surgery type).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was conducted using a computer-generated random sequence stratified by surgical type (gastric vs colorectal)." (p. 212, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation was concealed in sequentially numbered, opaque, sealed envelopes prepared by an independent staff member." (p. 212, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor site, laparoscopic surgical duration, and blood loss were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-induction stimulation delivered while awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates discernible awake sensation contrast.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and anesthesiologists managing postoperative care were blinded to group allocation." (p. 213, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized perioperative care pathway and rescue analgesic protocols.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 120 randomized (60 TEAS, 60 Sham); all 120 analyzed in their assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete follow-up data available for all 120 randomized patients (100% follow-up completion; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Objective auscultation of bowel sounds and validated patient/nursing recovery logs of flatus time.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical 2-hourly auscultation and documentation schedule.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Independent outcome assessors blinded to group allocation conducted postoperative assessments." (p. 213, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR1900023263) on May 19, 2019.
- **5.2 Result selected:** No (N)
  - **Evidence:** First bowel sounds, flatus, and defecation times all reported.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Standard continuous parametric and Kaplan-Meier analyses as prespecified.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation with stratification, sealed opaque envelopes, balanced baseline. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Pre-induction awake sensory awareness between active 10–20 mA stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Standardized evaluation by blinded independent assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-induction sensory difference. |

---

### Step 4: Evidence Audit
- covidence_437_full_article.pdf, p. 212, col. 2: "Allocation was concealed in sequentially numbered, opaque, sealed envelopes..."
- covidence_437_full_article.pdf, p. 214, Table 2: "Time to first flatus: TEAS 58.4 ± 14.2 h vs. Sham 72.8 ± 16.5 h, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Li_2021",
  "source_file": "covidence_437_full_article.pdf",
  "trial_registration": "ChiCTR1900023263",
  "outcome": "Time to first flatus (hours)",
  "timepoint": "Postoperative Day 1 to Day 4",
  "sample_size": {
    "teas": 60,
    "sham": 60,
    "total": 120
  },
  "result": {
    "teas_mean": 58.4,
    "teas_sd": 14.2,
    "sham_mean": 72.8,
    "sham_sd": 16.5,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
