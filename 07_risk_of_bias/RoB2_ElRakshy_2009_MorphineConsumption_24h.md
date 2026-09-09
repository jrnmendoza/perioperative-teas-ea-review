# Cochrane Risk of Bias 2 (RoB 2) Assessment

> **SUPERSEDES a prior "SOME CONCERNS" overall judgment.** On 2026-09-09 a
> second, independent reviewer re-read the primary source directly and
> found Domain 3 to be High, not Some concerns, driven by an internal
> inconsistency in the publication's own intervention-group denominators
> that the original assessment below did not identify. This pipeline
> independently verified the decisive claim (the flow-diagram numbers in
> Figure 1) by rendering and visually inspecting the source PDF page
> itself before adopting this correction — see the Step 4a addendum below.
> The corrected domain and overall judgments are recorded in Step 3 and
> Step 6; the original Domain 3 reasoning is retained struck through for
> transparency about what changed and why.
>
> The header fields below (Population/Intervention) also contained a
> transcription error inherited from a different study's template
> (112 patients / open inguinal hernia repair / Hegu-Zusanli at 2 Hz) —
> corrected here against the actual source text.

## Study & Result Information
- **Study Citation:** El-Rakshy M, Clark SC, Thompson J, Thant M. Effect of intraoperative electroacupuncture on postoperative pain, analgesic requirements, nausea and sedation: a randomised controlled trial. *Acupuncture in Medicine*. 2009;27(1):9–12. doi:10.1136/aim.2008.000075.
- **Source Document:** `covidence_batch_20/studies/11_1879897344_El-Rakshy_2009.pdf` (also archived as `covidence_868_full_article.pdf`)
- **Trial Registration:** Not reported / omitted in text
- **Population:** 107 patients undergoing elective abdominal hysterectomy or laparoscopic cholecystectomy, ASA I–II, conducted in 1999 at Scunthorpe & Goole Hospitals.
- **Intervention:** Intraoperative electroacupuncture at GV2/GV4/BL32/BL23/LI4/PC6 (hysterectomy) or LR3/SP6/LI4/PC6 (cholecystectomy), 10 Hz, intensity 7/10, needles placed after induction and removed before recovery-room transfer ("PCA + acupuncture" arm).
- **Comparator:** PCA alone, with adhesive dressings placed over the same acupoints (no needles/stimulation) to preserve blinding ("PCA" arm).
- **Assessed Outcome:** Total Postoperative PCA Morphine Consumption
- **Assessed Timepoint:** 24 hours postoperatively
- **Numerical Result (Table 2, as published):**
  - PCA/control (n = 53): Mean 36.9 ± 18.0 mg
  - PCA + acupuncture (n = 42): Mean 35.3 ± 18.0 mg
  - Difference: Mann–Whitney U test, $P = 0.961$

---

### Step 1: Study Design Verification
- **Experimental Design:** Prospective, randomized, controlled parallel-group trial.
- **Unit of Randomization:** Individual patient.

---

### Step 2: Signaling Questions & Domain Evaluations

#### Domain 1: Risk of bias arising from the randomization process
- **1.1 Random sequence generation:** Yes (Y) — "Patients were allocated to treatment groups on the basis of a computer-generated randomisation list using Statistical Package for Social Sciences (SPSS)" (p. 9).
- **1.2 Allocation concealment:** No Information (NI) — the paper states only "In consecutive order, patients were allocated to one or other group after consulting the list" (p. 9); no sealed-envelope, central-allocation, or other concealment mechanism is described.
- **Domain 1 Judgment:** **Some Concerns** (adequate random sequence generation, but allocation concealment cannot be established from the report).

#### Domain 2: Risk of bias due to deviations from the intended interventions
- **2.1/2.2 Participant and carer awareness:** Probably No (PN) — "Double blinding was achieved by placing adhesive dressings on all acupuncture sites in all patients, to ensure that neither the patients themselves nor the staff caring for the patients knew which treatment each patient received" (p. 9); the anaesthetists were explicitly NOT blinded ("The anaesthetists were not blinded to the patient's group allocation, but were not involved in the assessment of the patients," p. 10) but this is an intended, protocol-described unblinding of a non-assessing role, not a deviation.
- **2.5 Appropriate analysis:** Probably No (PN) — 2 of 62 acupuncture-allocated patients "withdrew their consent because they did not want to have acupuncture" post-randomisation and were excluded from analysis (p. 11); this is a small, intervention-related exclusion, not on its own sufficient for High.
- **Domain 2 Judgment:** **Some Concerns** (small intervention-related post-randomisation exclusion; otherwise a well-standardised, appropriately blinded protocol).

#### Domain 3: Risk of bias due to missing outcome data
~~- **3.1 Data completeness:** No (N) — Only 42 of 56 (75%) in EA group had 24-h data (Table 2).~~
~~- **3.2 Missingness unrelated to outcome:** Probably Yes (PY) — Exclusions were technical PCA discontinuation or protocol violations, but differential attrition raises concerns.~~
~~- **Domain 3 Judgment (ORIGINAL, SUPERSEDED):** Some Concerns (substantial differential missing outcome data).~~

**Corrected 2026-09-09.** The original assessment above treated this as ordinary differential attrition from a clean 56-vs-56 randomised base. A fresh, independent re-read (confirmed by this pipeline rendering the actual PDF page and inspecting Figure 1 directly, not just its text) found that the publication's own group denominators for this trial are internally irreconcilable across five different locations:

1. **Abstract (p. 9):** "107 patients ... were randomised to receive either electroacupuncture (n = 56) or no additional treatment (n = 46)" — 56 + 46 = 102, not 107, an internal contradiction within the same sentence.
2. **Figure 1 flow diagram (p. 10), verified by direct visual inspection of the rendered PDF page, not just its extracted text:** "Randomised (n = 107)" → "Allocated to acupuncture (n = 60) ... Analysed (n = 58)" and "Allocated to control (n = 47) ... Analysed (n = 44)". I.e., the flow diagram assigns **58 analysed to acupuncture, 44 to control**.
3. **Results narrative (p. 11):** "A total of 58 patients were analysed in the PCA arm and 44 in the PCA + acupuncture arm" — the same two numbers, 58 and 44, but assigned to the **opposite** arms from Figure 1.
4. **Table 1 (p. 11):** "PCA: 56 female + 2 male = 58; PCA + acupuncture: 36 female + 8 male = 44" — agrees with the Results narrative's reversed labelling, not with Figure 1.
5. **Table 3 (p. 12):** pain-score totals of PCA = 56, PCA + acupuncture = 46 — a third, different denominator pair matching neither Figure 1 (60/47 allocated, 58/44 analysed) nor Table 1/Results (58/44 reversed).
6. **Table 2 (p. 11), the table actually reporting the assessed 24-h morphine result:** PCA = 53, PCA + acupuncture = 42 — a fourth denominator pair, specific to this outcome.

The authors themselves report a plausible mechanism for this confusion in Statistical methods (p. 11): "Unfortunately the statistician became ill after performing the data entry and initial analysis. The original data remained inaccessible ... This report is written on the basis of the initial print-out generated by SPSS; data were re-entered into SPSS V.15.0." No participant-level reconciliation, missing-data analysis, or sensitivity analysis is reported anywhere in the paper that resolves which denominator pair is correct, or which specific patients are missing from the 24-h morphine result in each randomised arm.

- **Domain 3 Judgment (CORRECTED):** **High.** Not because 25% vs 5% attrition automatically crosses the High threshold, but because the publication's own group denominators/labels for this trial cannot be reconciled at all — the completeness of outcome data for this specific randomised comparison cannot be reliably established from the source, and the authors' own account of losing the original dataset forecloses any prospect of resolving it from elsewhere in the paper.

#### Domain 4: Risk of bias in measurement of the outcome
- **4.1 Measurement method:** No (N) — "During the first 24 h of postoperative care, all patients received morphine sulphate via the PCA route. The concentration of morphine in the PCA pump was 1 mg/ml; the lock-out time was 5 minutes" (p. 10) — an objective, electronically logged medication-use outcome, identical method in both arms.
- **4.3 Assessor blinding:** No (N) — "The recovery nurse who was assessing the patient was blinded to the technique, since patients in both groups came to the recovery room with a dressing covering the acupuncture point" (p. 10).
- **Domain 4 Judgment:** **Low** (objective outcome, identical measurement method, blinded assessors).

#### Domain 5: Risk of bias in selection of the reported result
- **5.1 Pre-specified analysis plan:** No Information (NI) — no trial registration is reported, but the Statistical methods section (p. 11) states in advance of Results: "The primary outcome for comparing the groups was the mean dose (mg) of morphine used. This was calculated for 4 h and for 24 h in order to be able to detect any time-related effects of acupuncture" — the 24-h morphine endpoint assessed here is the paper's own stated primary outcome, not a post hoc selection.
- **5.2 Selective reporting risk:** Probably No (PN) — no registered protocol exists to confirm the full set of planned analyses, and the loss of the original dataset (see Domain 3) adds uncertainty about what analyses were actually available to the investigators, though there is no positive evidence of selective reporting.
- **Domain 5 Judgment:** **Some Concerns** (a stated a priori primary outcome, reported, but unregistered and reconstructed after the original data became inaccessible).

---

### Step 3: Overall Judgment & Summary Table

| Domain | Judgment | Key Supporting Rationale |
|---|:---:|---|
| **Domain 1: Randomization Process** | **Some concerns** | Computer-generated schedule, but concealment method not described. |
| **Domain 2: Deviations from Intended Interventions** | **Some concerns** | Small intervention-related post-randomisation exclusion (2 of 62 allocated to acupuncture refused it); otherwise well-standardised and blinded. |
| **Domain 3: Missing Outcome Data** | **HIGH** *(corrected 2026-09-09, was Some concerns)* | The publication's intervention-group denominators/labels are irreconcilable across the flow diagram, Results text, Table 1, abstract, and Table 3; outcome-data completeness for this randomised comparison cannot be reliably established, and the original dataset is confirmed lost. |
| **Domain 4: Measurement of the Outcome** | **Low** | Objective PCA-pump morphine logs; blinded recovery-room assessor. |
| **Domain 5: Selection of the Reported Result** | **Some concerns** | 24-h morphine is the paper's own stated a priori primary outcome, but unregistered and reconstructed after data loss. |
| **OVERALL RISK OF BIAS** | **HIGH** *(corrected 2026-09-09, was SOME CONCERNS)* | Driven by Domain 3. |

---

### Step 4: Evidence Audit
- p. 9 (Abstract): "107 patients ... were randomised to receive either electroacupuncture (n = 56) or no additional treatment (n = 46)."
- p. 9 (Study design): "Patients were allocated to treatment groups on the basis of a computer-generated randomisation list using Statistical Package for Social Sciences (SPSS)... In consecutive order, patients were allocated to one or other group after consulting the list."
- p. 9 (Study design): "Double blinding was achieved by placing adhesive dressings on all acupuncture sites in all patients..."
- p. 10 (Study protocol): "The anaesthetists were not blinded to the patient's group allocation, but were not involved in the assessment of the patients."
- p. 10 (Assessments): "During the first 24 h of postoperative care, all patients received morphine sulphate via the PCA route. The concentration of morphine in the PCA pump was 1 mg/ml; the lock-out time was 5 minutes."
- p. 10 (Study protocol): "The recovery nurse who was assessing the patient was blinded to the technique, since patients in both groups came to the recovery room with a dressing covering the acupuncture point."
- p. 11 (Statistical methods): "The primary outcome for comparing the groups was the mean dose (mg) of morphine used. This was calculated for 4 h and for 24 h..."
- p. 11 (Statistical methods): "Unfortunately the statistician became ill after performing the data entry and initial analysis. The original data remained inaccessible... This report is written on the basis of the initial print-out generated by SPSS; data were re-entered into SPSS V.15.0."
- p. 11 (Results): "Five patients were withdrawn: two patients in the PCA + acupuncture group scheduled for laparoscopic cholecystectomy withdrew their consent because they did not want to have acupuncture. Three patients, all in the PCA alone group ... were withdrawn either because they received other forms of analgesia ... or because of a change in the scheduled procedure ... Therefore, in total 102 patients completed the study."
- p. 11 (Results): "A total of 58 patients were analysed in the PCA arm and 44 in the PCA + acupuncture arm."
- p. 11 (Table 1): "PCA ... Totals 56 [female] 2 [male] = 58; PCA + acupuncture ... Totals 36 [female] 8 [male] = 44."
- p. 11 (Table 2): "Total analgesia in 24 h, mg: PCA (n = 53) 36.9 ± 18.0 vs. PCA + acupuncture (n = 42) 35.3 ± 18.0, P = 0.961."
- p. 12 (Table 3): "PCA 32 18 5 1 [Total] 56; PCA + acupuncture 31 15 0 0 [Total] 46."

#### Step 4a: Independent verification of Figure 1 (added 2026-09-09)

The extracted plain-text file for this PDF (`covidence_batch_20/studies/11_1879897344_El-Rakshy_2009_text.txt`) captures only the caption "Figure 1 Flow chart of the study" — the numbers inside the flow chart are graphical content, not extracted text. Before adopting the second reviewer's claim that Figure 1 reverses the group labels relative to Table 1/Results, this pipeline rendered page 2 of the source PDF to an image (`pymupdf`, 200 dpi) and visually inspected it directly. The flow chart reads exactly:

> Enrolment → Randomised (n = 107) → Allocation → **Allocated to acupuncture (n = 60)**, Did not receive allocated intervention (n = 2), Refused acupuncture / **Allocated to control (n = 47)**, Received allocated intervention (n = 47) → Follow-up → **Followed up (n = 58)**, Discontinued intervention (n = 0) [acupuncture arm] / **Followed up (n = 44)**, Discontinued intervention (n = 3), Change of operative or anaesthetic procedure [control arm] → Analysis → **Analysed (n = 58)** [acupuncture] / **Analysed (n = 44)** [control]

This confirms the reversal independently of the second reviewer's report: Figure 1 assigns 58 analysed to acupuncture and 44 to control, while the Results narrative and Table 1 both assign 58 to PCA/control and 44 to acupuncture — the same two numbers, opposite arms. The Domain 3 correction above is adopted on this independently-verified basis, not on the second reviewer's report alone.

---

### Step 5: Author Contact Flags
- Query which of the five reported denominator pairs (Figure 1: 60/47 allocated, 58/44 analysed; Results/Table 1: 58/44 reversed; Abstract: 56/46; Table 3: 56/46; Table 2: 53/42) reflects the trial's actual randomised and analysed group sizes, and request the underlying patient-level data if it has since been recovered (the authors reported the original dataset as inaccessible following the study statistician's illness).
- Request allocation concealment details.

---

### Step 6: Final Structured Extraction
```json
{
  "study_id": "ElRakshy_2009",
  "source_file": "covidence_batch_20/studies/11_1879897344_El-Rakshy_2009.pdf",
  "outcome": "Total Postoperative PCA Morphine Consumption",
  "timepoint": "24 hours postoperative",
  "sample_size_as_published_table2": {"control_analyzed": 53, "ea_analyzed": 42},
  "sample_size_note": "Table 2's own n's (53/42) are used for the numerical result per this review's pooling rule; the trial's underlying randomised/analysed denominators cannot be reconciled across the paper -- see Domain 3.",
  "result": {"control_mean": 36.9, "control_sd": 18.0, "ea_mean": 35.3, "ea_sd": 18.0, "p_value": 0.961},
  "overall_rob": "High",
  "d1": "Some concerns", "d2": "Some concerns", "d3": "High", "d4": "Low", "d5": "Some concerns",
  "adopted_by": "John Ryan N. Mendoza (review lead)",
  "adopted_date": "2026-09-09",
  "provenance_note": "Domain 3 and overall corrected from an earlier 'Some concerns' judgment after a second, independent reviewer re-read the primary source and identified irreconcilable intervention-group denominators across the flow diagram, Results text, Table 1, abstract, and Table 3. This pipeline independently verified the flow-diagram claim by rendering and visually inspecting the source PDF page before adopting the correction."
}
```
