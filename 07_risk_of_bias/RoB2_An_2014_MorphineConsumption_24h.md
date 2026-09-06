# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** An L, Zhou J, Wang Z, et al. Electro-Acupuncture Decreases Postoperative Pain and Improves Recovery in Patients Undergoing a Supratentorial Craniotomy. The American Journal of Chinese Medicine. 2014;42(5):1099–1109.
- **Source Document in Google Drive:** `covidence_698_full_article.pdf`
- **Trial Registration:** None reported
- **Population:** 90 patients (aged 18–65 years, ASA I–II) undergoing elective supratentorial craniotomy for brain tumor resection under general anesthesia.
- **Intervention:** Intraoperative electroacupuncture applied to bilateral Hegu (LI4) and Waiguan (TE5) starting after intubation and continuing throughout surgery under general anesthesia (dense-disperse 2/100 Hz, current 1–2 mA; n = 30 analyzed).
- **Comparator:** Sham EA with identical acupuncture needles placed at non-meridian points without electrical current (0 mA; n = 30 analyzed). A third control group received general anesthesia alone (n = 30 analyzed).
- **Assessed Outcome:** Cumulative Postoperative Morphine Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Cumulative morphine consumption over 24 hours was significantly lower in the EA group compared with the Sham EA group and Control group (mean ± SD: 12.4 ± 3.8 mg vs. 24.6 ± 5.2 mg vs. 26.2 ± 5.8 mg, P < 0.001). Postoperative VAS pain scores, sedation scores, and PACU discharge times were also significantly improved.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled 3-arm parallel-group trial (1:1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Random allocation was performed using a computer-generated random number table." (p. 1101, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Group assignments were enclosed in sequentially numbered, opaque, sealed envelopes." (p. 1101, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor location, craniotomy duration, and intraoperative anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Stimulation delivered strictly while patients were fully unconscious under general anesthesia.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Neurosurgeons, anesthesiologists maintaining anesthesia, and ward nurses were blinded to grouping." (p. 1101, col. 2).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized neurosurgical anesthesia protocol and standardized PCA morphine regimen.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 90 randomized (30 per arm); all 90 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome records available for all 90 participants (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Electronic microprocessor-controlled PCA pump documentation of cumulative morphine consumption (mg).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical PCA parameters (1 mg bolus, 6 min lockout) across all groups.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Outcome assessors recording postoperative recovery and pain were blinded to group allocation." (p. 1101, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No prospective clinical trial registration number or protocol publication cited in the manuscript.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Cumulative morphine consumption, VAS pain scores, and PONV rates reported at all time points.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard pre-specified ANOVA and Tukey post-hoc tests.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sequentially numbered sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind design; intervention delivered during general anesthesia. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Electronic PCA pump records and blinded outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Absence of prospective trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 5 due to lack of prospective clinical trial registration. |

---

### Step 4: Evidence Audit
- covidence_698_full_article.pdf, p. 1101, col. 1: "Random allocation was performed using a computer-generated random number table... enclosed in sequentially numbered, opaque, sealed envelopes..."
- covidence_698_full_article.pdf, p. 1104, Table 2: "Postoperative morphine consumption at 24 h: EA 12.4 ± 3.8 mg vs. Sham 24.6 ± 5.2 mg vs. Control 26.2 ± 5.8 mg, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "An_2014",
  "source_file": "covidence_698_full_article.pdf",
  "trial_registration": "None reported",
  "outcome": "Cumulative morphine consumption",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "ea": 30,
    "sham": 30,
    "control": 30,
    "total": 90
  },
  "result": {
    "ea_mean": 12.4,
    "ea_sd": 3.8,
    "sham_mean": 24.6,
    "sham_sd": 5.2,
    "control_mean": 26.2,
    "control_sd": 5.8,
    "p_value": "<0.001"
  },
  "overall_rob": "Some concerns"
}
```
