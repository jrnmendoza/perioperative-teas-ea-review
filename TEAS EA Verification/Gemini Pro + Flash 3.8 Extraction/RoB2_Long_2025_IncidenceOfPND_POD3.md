# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Long Y, Chen M, Wang J, et al. Effect of electroacupuncture intervention before and after operation on perioperative neurocognitive disorders in elderly patients with hip fractures: A randomized controlled trial. Injury. 2025;56(1):111820.
- **Source Document in Google Drive:** `1-s2.0-S0020138325005200.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR2100053050
- **Population:** 160 elderly patients (aged >= 65 years, ASA I–III) undergoing surgical fixation for hip fractures under spinal or general anesthesia.
- **Intervention:** Electroacupuncture applied to Baihui (GV20), Yintang (GV29), and bilateral Zusanli (ST36) for 30 min before surgery and once daily for 30 min on POD 1–3 (dense-disperse 2/100 Hz; n = 80 analyzed).
- **Comparator:** Sham EA using non-penetrating blunt needles placed 1 cm lateral to acupoints without electrical current (0 mA; n = 80 analyzed).
- **Assessed Outcome:** Cumulative Incidence of Perioperative Neurocognitive Disorder (PND)
- **Assessed Timepoint:** Within 3 days postoperatively (POD 1 to POD 3)
- **Numerical Result:**
  - Cumulative incidence of PND (assessed by 3-minute Confusion Assessment Method [3D-CAM] and MMSE) within 3 days postoperatively was significantly lower in the EA group compared with the Sham group (11/80 [13.8%] vs. 24/80 [30.0%]; relative risk 0.46, 95% CI 0.24–0.87, P = 0.015). Postoperative systemic inflammatory markers (IL-6, TNF-alpha) were also significantly attenuated.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, double-blind, sham-controlled parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Randomization was generated using a computer-generated random allocation sequence prepared by an independent statistician." (p. 2, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation was concealed in sequentially numbered, opaque, sealed envelopes." (p. 2, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, baseline MMSE score, fracture type, surgical approach, and operative duration were balanced (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN)
  - **Evidence:** Blunt non-penetrating sham needles and sensory deception used; blinding assessment questionnaire confirmed successful participant blinding.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Orthopedic surgeons, ward nurses, and anesthesiologists were strictly blinded to group allocation." (p. 3, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized geriatric orthopedic perioperative pathway followed uniformly.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 160 randomized (80 EA, 80 Sham); all 160 completed follow-up and were analyzed (100% ITT).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete cognitive follow-up available for all 160 randomized patients through POD 3 (100% complete data).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Standardized validated neurocognitive battery (3D-CAM and MMSE administered twice daily).
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform assessment schedule across both arms.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Neurocognitive assessments were conducted by trained neuropsychological evaluators blinded to allocation." (p. 3, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y)
  - **Evidence:** Prospectively registered in Chinese Clinical Trial Registry (ChiCTR2100053050) on November 9, 2021.
- **5.2 Result selected:** No (N)
  - **Evidence:** PND incidence across POD 1, 2, 3 and inflammatory biomarkers reported as prespecified.
- **5.3 Multiple analyses:** No (N)
  - **Evidence:** Pre-specified dichotomous event analysis.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Double-blind sham needle design with validated blinding and full ITT analysis. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero loss to follow-up. |
| **Domain 4: Measurement of the Outcome** | **Low** | Validated neurocognitive battery administered by blinded neuropsychologists. |
| **Domain 5: Selection of the Reported Result** | **Low** | Prospectively registered with complete outcome reporting. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all 5 domains. |

---

### Step 4: Evidence Audit
- 1-s2.0-S0020138325005200.pdf, p. 2, col. 2: "Randomization was generated using a computer-generated random allocation sequence... concealed in sequentially numbered, opaque, sealed envelopes..."
- 1-s2.0-S0020138325005200.pdf, p. 4, Table 2: "Incidence of PND within 3 days: EA 11/80 (13.8%) vs. Sham 24/80 (30.0%), RR 0.46 (95% CI 0.24–0.87), P = 0.015."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Long_2025",
  "source_file": "1-s2.0-S0020138325005200.pdf",
  "trial_registration": "ChiCTR2100053050",
  "outcome": "Incidence of PND",
  "timepoint": "Within 3 days postoperative",
  "sample_size": {
    "ea": 80,
    "sham": 80,
    "total": 160
  },
  "result": {
    "ea_events": 11,
    "sham_events": 24,
    "ea_pct": 13.8,
    "sham_pct": 30.0,
    "rr": 0.46,
    "p_value": 0.015
  },
  "overall_rob": "Low"
}
```
