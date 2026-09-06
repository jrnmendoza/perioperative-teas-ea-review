# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Zhou Y, Wang L, Zhu Q, et al. Transcutaneous electrical acupoint stimulation accelerates postoperative gastrointestinal recovery in elderly patients: A randomized controlled trial. Perioperative Medicine. 2026;15:42.
- **Source Document in Google Drive:** `covidence_48_verified.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2300078615
- **Population:** 102 elderly patients (aged >= 65 years, ASA I–III) undergoing elective laparoscopic colorectal surgery under general anesthesia.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36), Shangjuxu (ST37), and Hegu (LI4) twice daily for 30 minutes from POD 1 to POD 3 (dense-disperse 2/100 Hz, current 10–20 mA; n = 51 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with 0 mA current delivered (n = 51 analyzed).
- **Assessed Outcome:** Time to First Postoperative Flatus
- **Assessed Timepoint:** Postoperative Day 1 to Day 3
- **Numerical Result:**
  - Time to first postoperative flatus was significantly shorter in the TEAS group compared with the Sham group (mean ± SD: 46.4 ± 10.2 h vs. 59.8 ± 12.6 h, P < 0.001). Time to first defecation (66.8 ± 14.2 h vs. 80.4 ± 16.5 h, P < 0.001) and postoperative hospital stay were also significantly reduced.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-generated random allocation sequence prepared by an independent statistician." (p. 3, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "The allocation sequence was concealed in sequentially numbered, opaque, sealed envelopes." (p. 3, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor site, surgical duration, and blood loss were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Postoperative TEAS delivered while awake; active tingling (10–20 mA) vs. turned-off sham device (0 mA) creates awake sensory difference.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, ward nurses, and anesthesiologists managing anesthesia were blinded to group allocation." (p. 3, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized colorectal ERAS pathway and standardized rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 102 randomized (51 TEAS, 51 Sham); all 102 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete gastrointestinal follow-up records available for all 102 randomized patients (100% complete data; Fig. 1).
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
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2300078615) on December 12, 2023.
- **5.2 Result selected:** No (N)
  - **Evidence:** Time to flatus, defecation, and length of stay reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake postoperative sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Nurse-verified objective timing and blinded outcome evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake postoperative sensory difference. |

---

### Step 4: Evidence Audit
- covidence_48_verified.pdf, p. 3, col. 1: "Random numbers were generated using a computer-generated random allocation sequence... concealed in sequentially numbered, opaque, sealed envelopes..."
- covidence_48_verified.pdf, p. 5, Table 2: "Time to first flatus: TEAS 46.4 ± 10.2 h vs. Sham 59.8 ± 12.6 h, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Zhou_2026",
  "source_file": "covidence_48_verified.pdf",
  "trial_registration": "ChiCTR2300078615",
  "outcome": "Time to first flatus",
  "timepoint": "Postoperative Day 1 to Day 3",
  "sample_size": {
    "teas": 51,
    "sham": 51,
    "total": 102
  },
  "result": {
    "teas_mean": 46.4,
    "teas_sd": 10.2,
    "sham_mean": 59.8,
    "sham_sd": 12.6,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
