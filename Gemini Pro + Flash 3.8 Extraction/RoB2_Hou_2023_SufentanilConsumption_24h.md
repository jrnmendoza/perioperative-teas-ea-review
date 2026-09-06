# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Hou L, Zhang X, Zhou C, et al. Effects of electroacupuncture on postoperative pain and recovery after gynecological laparoscopic surgery: A randomized controlled trial. Heliyon. 2023;9(3):e14423.
- **Source Document in Google Drive:** `007_hou_2023.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2000029891
- **Population:** 186 female patients (aged 20–65 years, ASA I–II) scheduled for elective gynecological laparoscopic surgery under general anesthesia.
- **Intervention:** Electroacupuncture applied to bilateral Sanyinjiao (SP6), Zusanli (ST36), and Guanyuan (CV4) for 30 minutes before anesthesia induction and once daily for 30 minutes on POD 1 (dense-disperse 2/100 Hz, current 1–2 mA; n = 93 analyzed).
- **Comparator:** Sham EA using non-penetrating blunt needles placed at identical acupoints with 0 mA current delivered (n = 93 analyzed).
- **Assessed Outcome:** Cumulative Sufentanil Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result:**
  - Cumulative sufentanil consumption at 24 hours postoperatively was significantly lower in the EA group compared with the Sham group (mean ± SD: 42.6 ± 6.8 µg vs. 56.4 ± 8.2 µg, P < 0.001). Rest and coughing pain VAS scores and incidence of PONV were also significantly reduced.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was generated using a computer-based random sequence created by SPSS software." (p. 2, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation sequences were sealed in sequentially numbered, opaque, sealed envelopes." (p. 2, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, BMI, surgical duration, baseline vital signs, and anesthetic doses were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Non-penetrating blunt sham needles and sensory deception used; post-trial blinding assessment confirmed successful participant blinding across groups.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Surgeons, anesthesiologists, and ward nursing staff were blinded to group allocation." (p. 3, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized general anesthesia regimen and standardized PCIA sufentanil rescue analgesia protocol.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 186 randomized (93 EA, 93 Sham); all 186 completed and analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete 24-hour outcome records available for all 186 randomized patients (100% complete data; Fig. 1).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Electronic microprocessor-controlled PCIA pump documentation of cumulative sufentanil consumption (µg).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Identical PCIA programming across all participants.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Trained outcome assessors recording postoperative variables were blinded to treatment allocation." (p. 3, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2000029891) on February 17, 2020.
- **5.2 Result selected:** No (N)
  - **Evidence:** Sufentanil consumption, VAS pain scores, and PONV rates reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Standard pre-specified continuous parametric analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham needle design with validated blinding and full ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Electronic PCIA pump records and blinded outcome assessors. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- 007_hou_2023.pdf, p. 2, col. 2: "Randomization was generated using a computer-based random sequence... sealed in sequentially numbered, opaque, sealed envelopes..."
- 007_hou_2023.pdf, p. 4, Table 2: "Sufentanil consumption at 24 h: EA 42.6 ± 6.8 µg vs. Sham 56.4 ± 8.2 µg, P < 0.001."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Hou_2023",
  "source_file": "007_hou_2023.pdf",
  "trial_registration": "ChiCTR2000029891",
  "outcome": "Cumulative sufentanil consumption",
  "timepoint": "24 hours postoperative",
  "sample_size": {
    "ea": 93,
    "sham": 93,
    "total": 186
  },
  "result": {
    "ea_mean": 42.6,
    "ea_sd": 6.8,
    "sham_mean": 56.4,
    "sham_sd": 8.2,
    "p_value": "<0.001"
  },
  "overall_rob": "Low"
}
```
