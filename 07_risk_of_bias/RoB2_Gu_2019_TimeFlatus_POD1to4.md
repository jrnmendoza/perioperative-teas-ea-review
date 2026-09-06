# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Gu Y, Chen Y, Wang Z, et al. Effects of transcutaneous electrical acupoint stimulation on gastrointestinal function recovery after laparoscopic radical gastrectomy: A randomized controlled trial. European Journal of Integrative Medicine. 2019;26:11–17.
- **Source Document in Google Drive:** `covidence_1471_full_article.pdf`
- **Trial Registration:** None reported
- **Population:** 120 gastric cancer patients (aged 18–75 years, ASA I–III) undergoing laparoscopic radical gastrectomy under general anesthesia.
- **Intervention:** TEAS applied to bilateral Zusanli (ST36) and Neiguan (PC6) twice daily for 30 minutes from POD 1 to POD 3 at mixed dense-disperse frequency (2/100 Hz; n = 40 analyzed) or low frequency (2 Hz; n = 40 analyzed).
- **Comparator:** Sham TEAS using identical appearance electrodes applied to same acupoints with the stimulator display illuminated but 0 mA current delivered (n = 40 analyzed).
- **Assessed Outcome:** Time to First Postoperative Flatus
- **Assessed Timepoint:** Postoperative Day 1 to Day 4
- **Numerical Result:**
  - Time to first flatus was significantly shorter in the 2/100 Hz TEAS group compared with the Sham TEAS group (mean ± SD: 58.2 ± 9.4 h vs. 73.5 ± 11.2 h, P < 0.01). Time to first bowel sounds (32.4 ± 6.8 h vs. 45.2 ± 8.1 h) and time to first defecation were also significantly accelerated.

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, single-blind, sham-controlled 3-arm parallel-group trial (1:1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y)
  - **Evidence:** "Patients were allocated randomly to three groups using a computer-generated random number table." (p. 12, col. 2).
- **1.2 Allocation concealment:** Yes (Y)
  - **Evidence:** "Allocation was concealed in sequentially numbered, opaque sealed envelopes." (p. 12, col. 2).
- **1.3 Baseline balance:** No (N)
  - **Evidence:** Age, sex, BMI, tumor stage, surgical duration, and blood loss were comparable across the three groups (P > 0.05; Table 1).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably Yes (PY)
  - **Evidence:** Postoperative TEAS delivered to awake patients; distinct tingling sensation in active groups vs. zero current in sham group.
- **2.2 Carers awareness:** Probably No (PN)
  - **Evidence:** "Operating surgeons and ward nurses were unaware of the grouping." (p. 13, col. 1).
- **2.3 Contextual deviations:** No (N)
  - **Evidence:** Standardized ERAS gastrectomy protocol and standardized rescue analgesic regimen.
- **2.5 Appropriate analysis:** Yes (Y)
  - **Evidence:** 120 randomized (40 per arm); all 120 analyzed in assigned groups (100% ITT).
- **Domain 2 Judgment:** **Some concerns Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y)
  - **Evidence:** Complete follow-up data available for all 120 randomized patients (100% follow-up completion).
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N)
  - **Evidence:** Validated auscultation and nurse-verified documentation of flatus passage.
- **4.2 Differ between groups:** No (N)
  - **Evidence:** Uniform auscultation schedule every 2 hours.
- **4.3 Assessors aware:** No (N)
  - **Evidence:** "Data collection was performed by a designated investigator who was blinded to group allocation." (p. 13, col. 1).
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI)
  - **Evidence:** No trial registration number or protocol publication cited in the text.
- **5.2 Result selected:** Probably No (PN)
  - **Evidence:** Bowel sounds, flatus, defecation, and PONV rates reported across all groups.
- **5.3 Multiple analyses:** Probably No (PN)
  - **Evidence:** Standard pre-specified ANOVA and Tukey post-hoc tests.
- **Domain 5 Judgment:** **Some concerns Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer generation, sequentially numbered sealed opaque envelopes, baseline balanced. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Awake postoperative sensory contrast between active stimulation and silent 0 mA sham device. |
| **Domain 3: Missing Outcome Data** | **Low** | Zero missing data. |
| **Domain 4: Measurement of the Outcome** | **Low** | Blinded outcome assessors and standardized monitoring. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | Absence of prospective trial registration. |
| **OVERALL RISK OF BIAS** | **SOME CONCERNS** | Some concerns in Domain 2 (awake sensory contrast) and Domain 5 (unregistered trial). |

---

### Step 4: Evidence Audit
- covidence_1471_full_article.pdf, p. 12, col. 2: "Patients were allocated randomly to three groups using a computer-generated random number table... concealed in sequentially numbered, opaque sealed envelopes..."
- covidence_1471_full_article.pdf, p. 14, Table 2: "Time to first flatus: 2/100 Hz TEAS 58.2 ± 9.4 h vs. Sham 73.5 ± 11.2 h, P < 0.01."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Gu_2019",
  "source_file": "covidence_1471_full_article.pdf",
  "trial_registration": "None reported",
  "outcome": "Time to first flatus",
  "timepoint": "Postoperative Day 1 to Day 4",
  "sample_size": {
    "teas_mixed": 40,
    "teas_low": 40,
    "sham": 40,
    "total": 120
  },
  "result": {
    "teas_mixed_mean": 58.2,
    "teas_mixed_sd": 9.4,
    "sham_mean": 73.5,
    "sham_sd": 11.2,
    "p_value": "<0.01"
  },
  "overall_rob": "Some concerns"
}
```
