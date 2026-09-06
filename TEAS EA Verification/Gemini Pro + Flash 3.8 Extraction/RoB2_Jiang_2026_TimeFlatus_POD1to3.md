# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Jiang X, Zhang Y, et al. Transcutaneous electrical acupoint stimulation accelerates postoperative gastrointestinal function recovery in patients undergoing non-gastrointestinal laparoscopic surgery: a randomized controlled trial. *Complementary Therapies in Clinical Practice*. 2026;64:101890.
- **Source Document in Google Drive:** `study_4_Jiang_2026.pdf`
- **Trial Registration:** ClinicalTrials.gov NCT03724656
- **Population:** 587 patients scheduled for selective non-gastrointestinal laparoscopic surgery (laparoscopic cholecystectomy, gynecologic surgery, etc.) under general anesthesia.
- **Intervention:** TEAS administered at bilateral ST36 (Zusanli) and PC6 (Neiguan) 30 min before anesthesia continuing until surgery completion, dilatational wave (2/100 Hz, 6-15 mA adjusted to patient tolerance; n = 294).
- **Comparator:** Sham TEAS with identical electrodes and lead placement at ST36 and PC6, connected to identical device with no current delivery (0 mA; n = 293).
- **Assessed Outcome:** Time to First Postoperative Flatus (hours)
- **Assessed Timepoint:** Postoperative follow-up (0-72 hours)
- **Numerical Result:** 
  - TEAS group (n = 294): Median 21.50 h (IQR: 19.0 to 23.5 h)
  - Sham TEAS group (n = 293): Median 27.00 h (IQR: 23.5 to 30.0 h)
  - Log-rank test $P < 0.001$; Hazard Ratio (HR) = 0.55 (95% CI: 0.46 to 0.65)

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, double-blind, randomized, sham-controlled, parallel-group trial (1:1 allocation ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y) — Block randomization via computer-generated allocation (`study_4_Jiang_2026.pdf`, Section 2.3).
- **1.2 Allocation concealment:** Yes (Y) — "accessed the randomization sequence through sealed opaque envelopes containing computer-generated allocations" (Section 2.3).
- **1.3 Baseline balance:** No (N) — Surgical type, anesthesia time, operative time, blood loss, and baseline demographics balanced ($P > 0.05$; Table 1 & Table 2).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN) — Sham TEAS delivered via identical device and electrode setup under general anesthesia context.
- **2.2 Carers awareness:** Probably No (PN) — "Patients, outcome assessors, and statisticians were blinded to group assignments" (Section 2.3). Surgeons and ward nurses blinded.
- **2.3 Contextual deviations:** No (N) — Standardized perioperative anesthesia and ERAS pathway.
- **2.5 Appropriate analysis:** Yes (Y) — All 587 randomized patients analyzed (294 TEAS vs. 293 Sham).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y) — 587 of 587 randomized patients (100%) completed follow-up.
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N) — Time to first flatus recorded by blinded independent assessors.
- **4.2 Differ between groups:** No (N) — Identical clinical monitoring.
- **4.3 Assessors aware:** No (N) — Outcome assessors were blinded.
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y) — Prospectively registered at ClinicalTrials.gov (NCT03724656).
- **5.2 Result selected:** No (N) — Primary endpoint reported fully as pre-specified.
- **5.3 Multiple analyses:** No (N) — Standard survival Kaplan-Meier and log-rank tests applied.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer-generated block randomization; sealed opaque envelopes; balanced baseline. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham-controlled design; 100% ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | 100% data completeness (587/587 analyzed). |
| **Domain 4: Measurement of the Outcome** | **Low** | Blinded independent outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered in ClinicalTrials.gov (NCT03724656). |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk across all 5 evaluation domains. |

---

### Step 4: Evidence Audit
- `study_4_Jiang_2026.pdf`, p. 2, col. 2: "sealed opaque envelopes containing computer-generated allocations."
- `study_4_Jiang_2026.pdf`, p. 3, col. 2: "time to first flatus in TEAS group compared to sham-TEAS group (21.5 h [19.0–23.5] vs. 27.0 h [23.5–30.0], log-rank test, P < 0.001)."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Jiang_2026",
  "source_file": "study_4_Jiang_2026.pdf",
  "trial_registration": "NCT03724656",
  "outcome": "Time to First Postoperative Flatus (hours)",
  "timepoint": "0-72 hours postoperative",
  "sample_size": {"teas": 294, "sham": 293, "total": 587},
  "result": {"teas_median": 21.5, "teas_iqr": "19.0-23.5", "sham_median": 27.0, "sham_iqr": "23.5-30.0", "p_value": "<0.001"},
  "overall_rob": "Low"
}
```
