# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Liu S, Zhang M, Wang T, et al. Effects of Transcutaneous Electrical Acupoint Stimulation on Postoperative Pain and Recovery After Endoscopic Submucosal Dissection: A Randomized Controlled Trial. Chinese Journal of Integrative Medicine. 2026;32(8):720–727.
- **Source Document in Google Drive:** `covidence_69_full_article.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2100052837
- **Population:** 129 patients (aged 18–75 years, ASA I–III) undergoing elective endoscopic submucosal dissection (ESD) for early gastrointestinal neoplasms under propofol sedation.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Hegu (LI4) 30 min before sedation and continued until ESD completion (dense-disperse 2/100 Hz, current 10–20 mA; n = 64 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with 0 mA current delivered (n = 65 analyzed).
- **Assessed Outcome:** Incidence of Moderate-to-Severe Pain (NRS >= 4)
- **Assessed Timepoint:** 0 to 24 hours postoperatively
- **Numerical Result:**
  - Incidence of moderate-to-severe pain within 24 hours post-ESD was significantly lower in the TEAS group compared with the Sham group (8/64 [12.5%] vs. 21/65 [32.3%], P = 0.007). Propofol consumption during ESD (184.2 ± 32.5 mg vs. 238.6 ± 41.2 mg, P < 0.001) and time to first flatus were also significantly reduced.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random numbers were generated using a computer-generated random number sequence." (p. 721, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation sequences were sealed in sequentially numbered, opaque envelopes opened prior to sedation." (p. 721, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, lesion location, lesion size, procedure duration, and baseline hemodynamics were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Pre-sedation awake stimulation with active tingling (10–20 mA) vs. silent 0 mA sham device in awake patients.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Endoscopists, sedation nurses, and ward staff were blinded to group allocation." (p. 722, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized sedation protocol and standardized post-ESD rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 129 randomized (64 TEAS, 65 Sham); all 129 analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome records available for all 129 randomized patients (100% follow-up completion).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated Numerical Rating Scale (NRS 0–10) evaluated at 2, 6, 12, 24 h post-ESD.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical evaluation timing across both groups.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome evaluators were blinded to patient grouping." (p. 722, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2100052837) on November 4, 2021.
- **5.2 Result selected:** No (N)
  - **Evidence:** Moderate-to-severe pain incidence, propofol consumption, and GI recovery reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified dichotomous event analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake pre-procedure sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated NRS assessed by blinded outcome evaluators. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 due to awake pre-procedure sensory difference. |

---

### Step 4: Evidence Audit
- covidence_69_full_article.pdf, p. 721, col. 2: "Allocation sequences were sealed in sequentially numbered, opaque envelopes..."
- covidence_69_full_article.pdf, p. 723, Table 2: "Incidence of moderate-to-severe pain within 24 h: TEAS 8/64 (12.5%) vs. Sham 21/65 (32.3%), P = 0.007."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Liu_2026_ESD",
  "source_file": "covidence_69_full_article.pdf",
  "trial_registration": "ChiCTR2100052837",
  "outcome": "Incidence of moderate-to-severe pain",
  "timepoint": "0 to 24 hours postoperative",
  "sample_size": {
    "teas": 64,
    "sham": 65,
    "total": 129
  },
  "result": {
    "teas_events": 8,
    "sham_events": 21,
    "teas_pct": 12.5,
    "sham_pct": 32.3,
    "p_value": 0.007
  },
  "overall_rob": "Some concerns"
}
```
