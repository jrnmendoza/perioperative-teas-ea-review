# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Zhang X, Wang Y, Chen H, et al. Transcutaneous Electrical Acupoints Stimulation Improves Spontaneous Voiding Recovery After Laparoscopic Cholecystectomy: A Randomized Clinical Trial. JAMA Surgery. 2023;158(8):805–813.
- **Source Document in Google Drive:** `covidence_308_full_article.pdf`
- **Trial Registration:** ClinicalTrials.gov NCT03631160
- **Population:** 1,948 patients (aged 18–65 years, ASA I–II) undergoing elective laparoscopic cholecystectomy without urinary catheterization.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Sanyinjiao (SP6) for 30 minutes preoperatively and 30 minutes immediately postoperatively in PACU (dense-disperse 2/100 Hz, current 10–20 mA; n = 975 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes and stimulator display with 0 mA current (n = 973 analyzed).
- **Assessed Outcome:** Time to First Spontaneous Voiding
- **Assessed Timepoint:** 0 to 24 hours postoperatively
- **Numerical Result:**
  - Time to first spontaneous voiding was significantly shorter in the TEAS group compared with the Sham group (median: 3.8 h vs. 5.9 h; hazard ratio 1.34, 95% CI 1.23–1.46, P < 0.001). Postoperative urinary retention requiring catheterization was also significantly lower in TEAS group (1.2% vs. 3.4%, P = 0.002).

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, multicenter, randomized, double-blind, sham-controlled parallel-group clinical trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was performed using a central computerized interactive web response system." (p. 806, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Central web-based automated allocation ensured complete concealment." (p. 806, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, baseline bladder volume, surgical duration, and anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Preoperative and PACU sham stimulation delivered with identical visual indicators; blinding questionnaire confirmed successful participant blinding.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were unaware of intervention allocation." (p. 807, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized fluid administration and perioperative care protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 1,948 randomized (975 TEAS, 973 Sham); all 1,948 analyzed in the primary intention-to-treat analysis (Fig. 1).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete follow-up for the primary outcome was obtained in 1,948 of 1,948 participants (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Standard nurse-verified recording of the exact time and volume of first spontaneous urination.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical objective voiding protocol and ultrasound bladder scan verification.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Ward outcome evaluators and ultrasound technicians were strictly blinded." (p. 807, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered at ClinicalTrials.gov (NCT03631160) on August 15, 2018 prior to participant recruitment.
- **5.2 Result selected:** No (N)
  - **Evidence:** Primary outcome (time to voiding) and secondary outcomes (catheterization rate, pain, PONV) reported as pre-specified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified Kaplan-Meier and Cox proportional hazards regression analyses.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Central computerized web randomization, strict concealment, baseline balance. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham design with validated blinding and complete ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data in a large multicenter trial (n=1,948). |
| **Domain 4: Measurement of the Outcome** | **Low** | Objective measurement by blinded assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospective registry (NCT03631160) with pre-published protocol and statistical analysis plan. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- covidence_308_full_article.pdf, p. 806, col. 2: "Randomization was performed using a central computerized interactive web response system..."
- covidence_308_full_article.pdf, p. 809, Table 2: "Time to first spontaneous voiding: TEAS median 3.8 h vs. Sham 5.9 h; HR 1.34 (95% CI 1.23–1.46), P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Zhang_2023",
  "source_file": "covidence_308_full_article.pdf",
  "trial_registration": "NCT03631160",
  "outcome": "Time to first spontaneous voiding",
  "timepoint": "0 to 24 hours postoperative",
  "sample_size": {
    "teas": 975,
    "sham": 973,
    "total": 1948
  },
  "result": {
    "teas_median_h": 3.8,
    "sham_median_h": 5.9,
    "hr": 1.34,
    "ci_lower": 1.23,
    "ci_upper": 1.46,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
