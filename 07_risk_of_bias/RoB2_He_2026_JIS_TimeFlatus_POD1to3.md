# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** He L, Chen M, Wang J, et al. Acupoint Stimulation After Anesthesia Induction Promotes Gastrointestinal Recovery in Colorectal Surgery: A Randomized Controlled Trial. Journal of Investigative Surgery. 2026;39(1):2653912.
- **Source Document in Google Drive:** `covidence_25_verified.pdf`
- **Trial Registration:** ClinicalTrials.gov NCT05396716
- **Population:** 158 adult patients (aged 18–75 years, ASA I–III) undergoing elective laparoscopic colorectal surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Shangjuxu (ST37) initiated immediately after anesthesia induction and continued until surgery end (dense-disperse 2/100 Hz, current 10–20 mA; n = 79 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with 0 mA current delivered (n = 79 analyzed).
- **Assessed Outcome:** Time to First Postoperative Flatus
- **Assessed Timepoint:** Postoperative Day 1 to Day 3
- **Numerical Result:**
  - Time to first postoperative flatus was significantly shorter in the TEAS group compared with the Sham group (mean ± SD: 44.8 ± 9.8 h vs. 56.2 ± 12.1 h, P < 0.001). Postoperative opioid requirements and time to first defecation were also significantly improved.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-based random sequence created by SAS software." (p. 3, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "The allocation sequence was concealed in sequentially numbered, opaque, sealed envelopes opened after induction." (p. 3, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor site, laparoscopic surgical duration, and blood loss were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Stimulation was administered strictly during general anesthesia while patients were fully unconscious; participant blinding was perfectly preserved.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and anesthesiologists managing postoperative care were blinded to group allocation." (p. 3, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized colorectal ERAS pathway and standardized rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 158 randomized (79 TEAS, 79 Sham); all 158 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete gastrointestinal follow-up records available for all 158 randomized patients (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Nurse-verified recording of the exact time of first flatus passage in hours.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform nursing documentation schedule across all patients.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome assessors who recorded recovery milestones were blinded to allocation." (p. 3, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered at ClinicalTrials.gov (NCT05396716) on May 25, 2022.
- **5.2 Result selected:** No (N)
  - **Evidence:** Time to flatus, defecation, and opioid consumption reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind design; intervention delivered during general anesthesia. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Nurse-verified objective timing and blinded outcome evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- covidence_25_verified.pdf, p. 3, col. 1: "Random numbers were generated using a computer-based random sequence... concealed in sequentially numbered, opaque, sealed envelopes..."
- covidence_25_verified.pdf, p. 5, Table 2: "Time to first flatus: TEAS 44.8 ± 9.8 h vs. Sham 56.2 ± 12.1 h, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "He_2026_JIS",
  "source_file": "covidence_25_verified.pdf",
  "trial_registration": "NCT05396716",
  "outcome": "Time to first flatus",
  "timepoint": "Postoperative Day 1 to Day 3",
  "sample_size": {
    "teas": 79,
    "sham": 79,
    "total": 158
  },
  "result": {
    "teas_mean": 44.8,
    "teas_sd": 9.8,
    "sham_mean": 56.2,
    "sham_sd": 12.1,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
