# Cochrane Risk of Bias 2 (RoB 2) Assessment

## Study & Result Information
- **Study Citation:** Tu LD, Li PC, Zhao Y, Feng RZ, Lv JQ. Transcutaneous electrical acupoint stimulation for postoperative nausea and vomiting in patients undergoing craniotomy: A randomized controlled trial. *Complementary Therapies in Clinical Practice*. 2024;54:101824.
- **Source Document in Google Drive:** `study_244_Tu_2023.pdf`
- **Trial Registration:** Chinese Clinical Trial Registry ChiCTR-TRC-13003026 (Registered in 2013)
- **Population:** 120 adult neurosurgical patients (aged 18–70 years, ASA I–II) undergoing elective craniotomy under general anesthesia.
- **Intervention:** TEAS at bilateral P6 (Neiguan) for 30 min upon regaining consciousness in PACU, 2/100 Hz, current adjusted to patient-reported *de qi* sensation (n = 57 analyzed).
- **Comparator:** Sham TEAS at bilateral P6 for 30 min with identical stimulator, electrodes, and display, but severed copper wire inside delivering 0 mA (n = 58 analyzed).
- **Assessed Outcome:** Postoperative Pain Intensity (Visual Analog Scale, 0–10 cm)
- **Assessed Timepoint:** 6 to 24 hours postoperatively
- **Numerical Result:** 
  - TEAS group (n = 57): Median 2 (IQR: 0.5–3)
  - Sham TEAS group (n = 58): Median 4 (IQR: 3–4)
  - Difference: Mann–Whitney $z = 4.007$, $P = 0.001$ (Table 5)

---

### Step 1: Study Design Verification
- **Experimental Design:** Individually randomized parallel-group trial (1:1 ratio).
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y) — Computer-generated random number schedule (`study_244_Tu_2023.pdf`, Section 2.4).
- **1.2 Allocation concealment:** Yes (Y) — Sequentially numbered, opaque, sealed envelopes (SNOSE) (`study_244_Tu_2023.pdf`, Section 2.4).
- **1.3 Baseline balance:** No (N) — Demographics and intraoperative analgesics well balanced (Table 2).
- **Domain 1 Judgment:** **Low Risk of Bias**

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1 Participant awareness:** Probably No (PN) — Sham group received sham stimulation with severed wire, identical visual indicators/sound, and sub-sensory deception protocol (`study_244_Tu_2023.pdf`, Section 2.5).
- **2.2 Carers awareness:** Probably No (PN) — Ward nurses and attending physicians administering analgesics were blinded.
- **2.3 Contextual deviations:** No (N) — Standardized rescue analgesia protocol (tramadol 10 mg IM for VAS > 6). At 6–24 h, 3 patients in TEAS vs. 6 patients in sham received tramadol ($P = 0.315$; Table 4).
- **2.5 Appropriate analysis:** Probably Yes (PY) — 115/120 analyzed (5 exclusions due to coma/ICP, balanced 3 vs. 2).
- **Domain 2 Judgment:** **Low Risk of Bias**

#### Domain 3: Risk of bias due to missing outcome data
- **3.1 Data completeness:** Yes (Y) — 115/120 (95.8%) complete data (`study_244_Tu_2023.pdf`, Table 5).
- **3.2 Missingness unrelated to true value:** Yes (Y) — Coma/ICP complications unrelated to acute pain rating.
- **Domain 3 Judgment:** **Low Risk of Bias**

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Inappropriate measurement:** No (N) — Validated standard Visual Analog Scale (VAS, 0–10).
- **4.2 Measurement differ between groups:** No (N) — Identical measurement timing and administration.
- **4.3 Outcome assessors aware:** No (N) — "Another blinded observer (nurse) recorded the postoperative data... pain score was measured using a standard VAS at 0–2, 2–6, and 6–24 h after craniotomy." (`study_244_Tu_2023.pdf`, Section 2.4 & 2.6).
- **4.4 Assessment influenced by knowledge:** No (N) — Assessor was strictly blinded.
- **Domain 4 Judgment:** **Low Risk of Bias**

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** Yes (Y) — Prospective ChiCTR registration and protocol publication in *Trials* 2014.
- **5.2 Result selected from multiple measurements:** No (N) — VAS pain reported across all specified time intervals (0–2, 2–6, 6–24 h; Table 5).
- **5.3 Result selected from multiple analyses:** No (N) — Non-parametric Mann-Whitney U test prespecified for skewed pain scores.
- **Domain 5 Judgment:** **Low Risk of Bias**

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Low** | Computer-generated list; SNOSE concealment; balanced baseline characteristics. |
| **Domain 2: Deviations from Intended Interventions** | **Low** | Validated sham device blinding; blinded clinical carers; protocolized rescue analgesia. |
| **Domain 3: Missing Outcome Data** | **Low** | <5% attrition (95.8% complete data). |
| **Domain 4: Measurement of the Outcome** | **Low** | Independent blinded nurse assessor recording standard VAS pain scores. |
| **Domain 5: Selection of the Reported Result** | **Low** | Pre-specified protocol endpoints; all measurement windows fully reported. |
| **OVERALL RISK OF BIAS** | **LOW** | Low risk of bias across all domains. |

---

### Step 4: Evidence Audit
- **Pain Measurement:** `study_244_Tu_2023.pdf`, p. 3, col. 1: "The pain score was measured using a standard VAS at 0–2, 2–6, and 6–24 h after craniotomy."
- **Data Point:** `study_244_Tu_2023.pdf`, p. 4, Table 5: "6–24 h after operation: TEAS group median 2 (IQR 0.5–3), Sham TEAS group median 4 (IQR 3–4), $z = 4.007$, $P = 0.001$."

---

### Step 5: Author Contact Flags
- None.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "Tu_2024",
  "source_file": "study_244_Tu_2023.pdf",
  "outcome": "Postoperative Pain Intensity (VAS 0-10)",
  "timepoint": "6-24 hours postoperative",
  "sample_size": {"teas": 57, "sham": 58},
  "result": {"teas_median": 2, "teas_iqr": "0.5-3", "sham_median": 4, "sham_iqr": "3-4", "p_value": 0.001},
  "overall_rob": "Low"
}
```
