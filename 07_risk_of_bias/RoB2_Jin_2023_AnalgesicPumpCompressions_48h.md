# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Jin Y, Huang S, Chen M, et al. Efficacy of electroacupuncture combined with intravenous patient-controlled analgesia after cesarean section: a randomized controlled trial. American Journal of Obstetrics and Gynecology MFM. 2023;5(8):101037.
- **Source Document in Google Drive:** `009_jin_2023.pdf`
- **Trial Registration:** ClinicalTrials.gov NCT04879212
- **Population:** 174 pregnant women undergoing elective cesarean delivery under combined spinal-epidural anesthesia at a tertiary university hospital (May 2021 to February 2022).
- **Intervention:** Electroacupuncture (EA) at bilateral Sanyinjiao (SP6) and Zusanli (ST36) starting 6 hours postoperatively, administered twice daily for 30 minutes each session over 48 hours (dense-disperse frequency 2/100 Hz, current 1–2 mA adjusted to deqi sensation; n = 87 analyzed).
- **Comparator:** Sham electroacupuncture at non-meridian points (1 cm lateral to SP6 and ST36) using identical appearance needles and stimulators without electrical current delivery (0 mA; n = 87 analyzed).
- **Assessed Outcome:** Cumulative Number of Patient-Controlled Intravenous Analgesia (PCIA) Pump Compressions
- **Assessed Timepoint:** 0 to 48 hours postoperatively
- **Numerical Result:**
  - EA group demonstrated significantly fewer PCIA pump compressions over 48 hours compared with sham EA group (median [IQR]: 12.0 [8.0–18.0] vs. 20.0 [14.0–28.0], P < 0.001). Total fentanyl consumption at 48 h was also significantly lower in the EA group (312.4 ± 42.1 µg vs. 428.6 ± 51.3 µg, P < 0.001).

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, single-center, patient- and assessor-blinded, sham-controlled parallel-group clinical trial (1:1 allocation ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was performed using a computer-generated random allocation sequence prepared by an independent statistician." (p. 2, col. 1).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation concealment was achieved using sequentially numbered, opaque, sealed envelopes that were kept by a research coordinator not involved in participant recruitment." (p. 2, col. 1).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Demographic characteristics, gestational age, parity, body mass index, surgical duration, and intraoperative blood loss were well balanced between groups (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Sham acupuncture at non-acupoint with mock electrical stimulator; participant blinding maintained with high success rate on post-trial blinding assessment questionnaire.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** Surgeons, ward nurses, and postoperative care personnel were blinded to intervention allocation.
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized spinal-epidural anesthesia and postoperative PCIA (fentanyl + flurbiprofen axetil) administered identically.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 174 randomized (87 EA, 87 Sham); all 174 analyzed in the primary intention-to-treat analysis (Fig. 1).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** 174 of 174 randomized patients (100%) completed the study and had complete PCIA pump records (p. 4, Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Automated digital micro-processor records from the electronic PCIA pump (validated objective logging).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical electronic PCA pumps programmed with same lockout interval and bolus dose.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Postoperative outcome assessors, ward staff, and data analysts were strictly blinded to group assignments." (p. 2, col. 2).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered at ClinicalTrials.gov (NCT04879212) on May 10, 2021 before enrollment was completed.
- **5.2 Result selected:** No (N)
  - **Evidence:** All prespecified primary and secondary outcomes (pump compressions, pain scores at rest and movement at 6, 12, 24, 48 h) reported.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Primary outcome evaluated as prespecified in the registry protocol.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer-generated random numbers, sealed opaque envelopes, and baseline balance. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham control, standardized care, full ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero attrition; 100% complete follow-up. |
| **Domain 4: Measurement of the Outcome** | **Low** | Objective electronic pump logging and blinded outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospective registry (NCT04879212) with full pre-specified reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- 009_jin_2023.pdf, p. 2, col. 1: "Randomization was performed using a computer-generated random allocation sequence... Allocation concealment was achieved using sequentially numbered, opaque, sealed envelopes..."
- 009_jin_2023.pdf, p. 5, Table 2: "Number of PCIA compressions at 48 h: EA 12.0 [8.0–18.0] vs. Sham EA 20.0 [14.0–28.0], P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Jin_2023",
  "source_file": "009_jin_2023.pdf",
  "trial_registration": "NCT04879212",
  "outcome": "PCIA pump compressions",
  "timepoint": "48 hours postoperative",
  "sample_size": {
    "ea": 87,
    "sham": 87,
    "total": 174
  },
  "result": {
    "ea_median": 12.0,
    "sham_median": 20.0,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
