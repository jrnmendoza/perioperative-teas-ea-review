# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Gao Y, Wang H, Sun M, et al. Transcutaneous electrical acupoint stimulation applied in lower limbs decreases the incidence of paralytic ileus after colorectal surgery: A multicenter randomized controlled trial. Surgery. 2021;170(6):1618–1626.
- **Source Document in Google Drive:** `covidence_400_full_article.pdf`
- **Trial Registration:** ClinicalTrials.gov NCT03086304
- **Population:** 400 adult patients (aged 18–75 years, ASA I–III) undergoing elective colorectal resection across four tertiary hospitals in China.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Sanyinjiao (SP6) twice daily for 30 minutes from Postoperative Day 1 until first bowel movement or POD 5 (dense-disperse 2/100 Hz, current 10–20 mA adjusted to comfortable tingling; n = 200 analyzed).
- **Comparator:** Sham TEAS using identical electrodes and lead wires applied to identical acupoints with no electrical current (0 mA; n = 200 analyzed).
- **Assessed Outcome:** Cumulative Incidence of Postoperative Paralytic Ileus (POI)
- **Assessed Timepoint:** Within 5 days postoperatively (POD 1 to POD 5)
- **Numerical Result:**
  - Incidence of postoperative paralytic ileus within 5 days was significantly lower in the TEAS group compared with the Sham group (21/200 [10.5%] vs. 41/200 [20.5%]; relative risk 0.51, 95% CI 0.31–0.83, P = 0.005). Time to first flatus (61.2 ± 16.4 h vs. 73.8 ± 19.1 h, P < 0.001) and hospital stay were also significantly reduced.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, multicenter, randomized, double-blind, sham-controlled parallel-group trial (1:1 allocation ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was performed using a central computerized web-based randomization system with stratified block randomization." (p. 1619, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Central web-based allocation ensured complete concealment until participant enrollment was finalized." (p. 1619, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, ASA score, laparoscopic vs. open approach, surgical duration, and intraoperative fluid management were balanced across groups (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Sham TEAS delivered 0 mA using identical devices; blinding assessment questionnaires demonstrated successful participant blinding across both arms.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Colorectal surgeons, ward nursing staff, and clinical caretakers were strictly blinded to group allocation throughout hospitalization." (p. 1620, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized ERAS colorectal pathway followed uniformly across all participating centers.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 400 randomized (200 TEAS, 200 Sham); all 400 analyzed in the primary intention-to-treat analysis (Fig. 1).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete outcome data for primary POI endpoint available for all 400 participants (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Standardized consensus criteria for postoperative paralytic ileus (absence of bowel motility, abdominal distension, intolerance to oral diet, nausea/vomiting requiring NG tube re-insertion).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical diagnostic monitoring criteria across all four centers.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Independent outcome assessors and members of the adjudication committee were blinded to allocation." (p. 1620, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered at ClinicalTrials.gov (NCT03086304) on March 22, 2017 before recruitment began.
- **5.2 Result selected:** No (N)
  - **Evidence:** Primary outcome (POI incidence) and all secondary outcomes (flatus, defecation, length of stay) reported as pre-specified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Primary dichotomous analysis conformed to pre-published statistical analysis plan.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Centralized web-based randomization, strict allocation concealment, and balanced baseline characteristics. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Multicenter double-blind sham design, standardized ERAS care, 100% ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero attrition for primary outcome. |
| **Domain 4: Measurement of the Outcome** | **Low** | Standardized consensus diagnostic criteria evaluated by blinded independent assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospective registry (NCT03086304) with fully concordant reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- covidence_400_full_article.pdf, p. 1619, col. 2: "Randomization was performed using a central computerized web-based randomization system..."
- covidence_400_full_article.pdf, p. 1622, Table 2: "Incidence of paralytic ileus: TEAS 21/200 (10.5%) vs. Sham 41/200 (20.5%), RR 0.51 (95% CI 0.31–0.83), P = 0.005."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Gao_2021",
  "source_file": "covidence_400_full_article.pdf",
  "trial_registration": "NCT03086304",
  "outcome": "Incidence of paralytic ileus",
  "timepoint": "Within 5 days postoperative",
  "sample_size": {
    "teas": 200,
    "sham": 200,
    "total": 400
  },
  "result": {
    "teas_events": 21,
    "sham_events": 41,
    "teas_pct": 10.5,
    "sham_pct": 20.5,
    "rr": 0.51,
    "p_value": 0.005
  },
  "overall_rob": "Low"
}
```
