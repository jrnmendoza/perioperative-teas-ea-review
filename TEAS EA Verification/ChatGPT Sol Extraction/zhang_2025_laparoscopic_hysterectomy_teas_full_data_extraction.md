# Covidence full data extraction - Zhang et al. 2025

## Source article
**Zhang Y, Dai Q, Zhang J, Wang J, Zhuang X, Zhang A, Huang L, Du W.**  
*Effects of Transcutaneous Electrical Acupoint Stimulation on Postoperative Acute Visceral, Incisional, and Low Back Pain and Recovery in Patients Undergoing Laparoscopic Hysterectomy: A Randomized Controlled Trial.*  
**Journal of Pain Research. 2025;18:6477-6489.**  
**DOI:** 10.2147/JPR.S553932  
**Trial registration:** ChiCTR2400093634

**Covidence study ID:** **NR from the uploaded filename `109551.pdf`.**

**Extraction basis:** Full-text PDF supplied by the user.  
**NR = not reported in the supplied article.**  
**Calculated = derived directly from published values and not explicitly stated by the authors.**  
Where the article contains inconsistent flow numbers, confidence intervals, P-values, or prose/table discrepancies, these are preserved and explicitly flagged rather than silently corrected.

---

# 1. Study details

| Field / question | Extracted answer |
|---|---|
| First author | **Yu Zhang** |
| Publication year | **2025** |
| Full title | **Effects of Transcutaneous Electrical Acupoint Stimulation on Postoperative Acute Visceral, Incisional, and Low Back Pain and Recovery in Patients Undergoing Laparoscopic Hysterectomy: A Randomized Controlled Trial** |
| Journal | **Journal of Pain Research** |
| Volume / pages | **18:6477-6489** |
| DOI | **10.2147/JPR.S553932** |
| Country | **China** |
| Institution | **The First Affiliated Hospital of Wenzhou Medical University, Wenzhou, China** |
| Number of centers | **Single-center** |
| Recruitment period | **Methods: March 2024-April 2025** |
| Abstract recruitment wording | **February 2024-2025** |
| Design | **Prospective randomized sham-controlled trial** |
| Trial registration | **ChiCTR2400093634** |
| Ethics approval | Ethics Committee of The First Affiliated Hospital of Wenzhou Medical University |
| Ethics approval date | **23 February 2024** |
| Ethics approval number | **KY2024-019** |
| Written informed consent | **Yes** |
| CONSORT adherence | **Yes, stated** |
| Declaration | **Helsinki Declaration** |
| Funding | Zhejiang TCM Administration Project **2023ZL086**; NSFC **82104622**; Wenzhou Science and Technology Bureau **Y20210787**; Zhejiang Natural Science Foundation **LQ24H310013** |
| Competing interests | **None declared** |
| Data sharing | Deidentified participant data available from corresponding author on reasonable request |
| Received | **15 July 2025** |
| Accepted | **15 November 2025** |
| Published | **4 December 2025** |

---

# 2. Study design and methodology

| Field / question | Extracted answer |
|---|---|
| Design | **Two-arm randomized controlled trial** |
| Arms | Active TEAS vs sham TEAS |
| Allocation ratio | **1:1** |
| Randomized | **108 total; 54/group** |
| Final analyzed | **93 total: 45 TEAS, 48 control** |
| Randomization method | **Stata 15.0 computer-generated random sequence** |
| Allocation concealment | **Sealed opaque envelopes, consecutively numbered** |
| Participant blinding | **Yes** |
| Anesthesiologist blinding | **Yes** |
| Outcome-assessor blinding | **Yes** |
| TEAS provider blinding | **No / not feasible** |
| Primary outcome | Maximum postoperative **visceral, incisional, and low-back pain** on POD0, POD1, POD2 |
| Secondary outcomes | Cytokines, sufentanil consumption, PCIA demands, rescue analgesia, PONV/other adverse events, recovery metrics |
| Statistical software | **Stata 15 SE** |
| Normality testing | **Shapiro-Wilk** |
| Continuous tests | Independent t test or Wilcoxon rank-sum |
| Categorical tests | Chi-square or Fisher exact |
| Repeated pain analysis | **Generalized Estimating Equations (GEE)** |
| GEE covariates | Age, BMI, education, previous abdominal surgery |
| Multiple-comparison correction | **Bonferroni, threshold P<0.017** |
| General significance threshold | **P<0.05** |
| Sample-size basis | Pilot visceral-pain NRS POD1: 2.53 ± 0.96 vs 3.40 ± 1.11 |
| Required sample | **43/group** |
| Planned with 20% dropout | **54/group, 108 total** |
| Full ITT analysis | **No** |

---

# 3. Participant flow

According to the Results and **Figure 2 on page 5**:

| Stage | TEAS | Control | Total |
|---|---:|---:|---:|
| Assessed for eligibility | - | - | **120** |
| Randomized | **54** | **54** | **108** |
| Excluded after randomization | **9** | **6** | **15** |
| Final analyzed | **45** | **48** | **93** |

## Post-randomization exclusions
### TEAS
- Surgical protocol modification: **5**
- Withdrawal of consent: **4**

### Control
- Surgical protocol modification: **6**

## Major screening arithmetic inconsistency
The article states:
- 120 assessed
- 5 declined
- 3 failed inclusion criteria
- 108 randomized

However:
- **120 - 5 - 3 = 112**, not 108.

Figure 2 likewise lists only **8 pre-randomization exclusions** but shows **108 randomized** from 120 assessed.

### Audit implication
There are **4 unexplained pre-randomization participants** in the reported flow.

### Attrition
- TEAS: **9/54 = 16.7%**
- Control: **6/54 = 11.1%**
- Overall post-randomization exclusion: **15/108 = 13.9%**

No full ITT analysis retaining all 108 randomized patients is presented.

---

# 4. Eligibility and population

| Field / question | Extracted answer |
|---|---|
| Population | Patients undergoing **elective laparoscopic hysterectomy** |
| Age | **18-65 years** |
| ASA | **I-II** |
| PCIA planned | **Required** |
| Ability to complete questionnaires | Required |
| Skin infection/lesion/scar at electrode site | Excluded |
| TEAS-electrode allergy | Excluded |
| Conversion to open surgery | Excluded |
| Psychiatric illness | Excluded |
| Pregnancy/lactation | Excluded |
| Severe cardiopulmonary disease | Excluded |
| Severe hepatic/renal dysfunction | Excluded |
| Preoperative opioid abuse | **Excluded** |
| Illicit drug use | Excluded |
| Withdrawal of consent | Exclusion criterion |
| Chronic opioid use | Opioid abuse excluded; otherwise **NR** |
| Chronic pain | **NR** |

---

# 5. Baseline characteristics

Table 1 on page 6:

| Characteristic | TEAS (n=45) | Control (n=48) | P |
|---|---:|---:|---:|
| Age, years | **51.91 ± 7.37** | **50.31 ± 6.46** | 0.27 |
| BMI, kg/m² | **23.63 ± 2.72** | **24.52 ± 3.09** | 0.14 |
| Previous abdominal surgery | **17 (37.78%)** | **10 (20.83%)** | 0.07 |
| Hypertension | **14 (31.11%)** | **10 (20.83%)** | 0.26 |
| Diabetes | **3 (6.67%)** | **3 (6.25%)** | 0.93 |
| Dysmenorrhea | **12 (26.67%)** | **14 (29.17%)** | 0.79 |
| Anesthesia duration, min | **91.66 ± 36.56** | **95.58 ± 28.62** | 0.58 |
| Surgery duration, min | **73.34 ± 33.12** | **84.13 ± 25.84** | 0.09 |

Education-level distributions were also reported and not significantly different (P=0.25).

---

# 6. TEAS intervention

| Field / question | Extracted answer |
|---|---|
| Modality | **Transcutaneous electrical acupoint stimulation (TEAS)** |
| Invasive | **No** |
| Acupoints | **Bilateral LI4 (Hegu), PC6 (Neiguan), SP6 (Sanyinjiao), ST36 (Zusanli)** |
| Pairing | **LI4-PC6 and SP6-ST36** |
| Device | **HANS-200F** |
| Manufacturer | Nanjing Jisheng Medical Technology Co., Ltd. |
| Frequency | **2/100 Hz** |
| Waveform | **Dense-disperse** |
| Intensity | **1 mA below the patient's maximum tolerance threshold** |
| Start | **30 min before anesthesia induction** |
| Intraoperative TEAS | **Yes** |
| End | **Continued throughout surgery** |
| Postoperative TEAS | **No** |
| Number of treatment periods | **One continuous preoperative/intraoperative exposure** |
| Provider | Trained anesthesiologists |
| Provider training | At least **1 week standardized instruction + consistency assessment** |

### Figure confirmation
The **acupoint diagram on page 3** identifies LI4, PC6, ST36, and SP6.

---

# 7. Sham comparator

| Field / question | Extracted answer |
|---|---|
| Electrode placement | **Identical to active TEAS** |
| Frequency setting | **2/100 Hz dense-disperse** |
| Intensity | **1 mA below the sensory threshold** |
| Electrical output | Apparently **sub-sensory stimulation**, not explicitly zero current |
| Participant blinding | **Yes, intended** |
| Sensory instruction | All patients told they might feel tingling, mild vibration, or no sensation |
| Formal blinding-success assessment | **NR** |

### Important comparator nuance
Unlike a simple no-current sham, the control appears to have received stimulation **below sensory threshold**.  
Do not code the comparator as definitely “no current” unless clarified.

---

# 8. General anesthesia

| Field / question | Extracted answer |
|---|---|
| Sufentanil induction | **0.4 µg/kg IV** |
| Propofol induction | **2 mg/kg IV** |
| Rocuronium | **0.6 mg/kg IV** |
| Maintenance propofol | **4-12 mg/kg/h** |
| Remifentanil | **0.1-0.2 µg/kg/min** |
| Sevoflurane | **1-2% end-tidal** |
| BIS target | **40-60** |
| EtCO₂ target | **30-40 mmHg** |
| Palonosetron | **0.25 mg IV**, 30 min before completion |
| Flurbiprofen axetil | **100 mg IV**, 30 min before completion |
| Wound infiltration | **10 mL 0.75% ropivacaine** after skin closure |

### Co-intervention implication
Local ropivacaine infiltration likely reduced incisional pain and may have masked an incremental TEAS effect at the incision site, as the authors themselves note.

---

# 9. Postoperative PCIA protocol

| Field / question | Extracted answer |
|---|---|
| PCA route | **Intravenous** |
| Opioid | **Sufentanil** |
| Reservoir | **100 µg sufentanil diluted to 100 mL** |
| Concentration | **1 µg/mL - calculated** |
| Background infusion | **2 mL/h = 2 µg/h - calculated** |
| Bolus | **2 mL = 2 µg - calculated** |
| Lockout | **10 min** |
| PACU rescue opioid | **IV sufentanil until NRS <4** |
| Ward rescue analgesic | **Indomethacin 50 mg rectal suppository if NRS ≥4** |

---

# 10. Exact POD1 / approximately 24-hour postoperative sufentanil endpoint

Table 4 on page 9 reports:

| Outcome | TEAS | Control | Effect | P |
|---|---:|---:|---|---:|
| Total sufentanil consumption | **50.53 ± 4.46 µg** | **53.79 ± 5.14 µg** | MD **-3.26 µg** (95% CI -5.25 to -1.27) | **0.002** |

## Calculated effect
- Absolute reduction: **3.26 µg**
- Relative reduction vs control: approximately **6.1%**

### Time-window interpretation
The article labels this endpoint **“on POD1”**, not explicitly “0-24 h.”

However, the programmed basal infusion alone is:
- 2 µg/h × 24 h = **48 µg**

The published means of **50.53 and 53.79 µg** are highly consistent with approximately 24 h of basal infusion plus bolus/rescue use.

### Extraction decision
Code as:
- **direct POD1 cumulative sufentanil consumption**
- **very likely first-24-h postoperative consumption**
- if your protocol requires an explicitly defined clock-based 0-24-h window, mark for confirmation rather than silently assuming.

### Clinical interpretation
The opioid reduction is statistically significant but **small (~6%)**, so it is unlikely to meet a conventional threshold for clinically meaningful opioid sparing if your review uses a substantially larger relative-reduction threshold.

---

# 11. 24-hour opioid / MME endpoint

| Field | Extraction |
|---|---|
| Native opioid | **IV sufentanil** |
| POD1 mean | **50.53 ± 4.46 vs 53.79 ± 5.14 µg** |
| Relative reduction | **~6.1%** |
| P-value | **0.002** |
| Exact clock window | **Not explicitly stated; labeled POD1** |
| Native continuous endpoint | **Yes** |
| MME conversion | Apply the review's prespecified IV-sufentanil conversion rule |
| Clinically meaningful opioid sparing | **Probably no, based on magnitude alone** |
| Author confirmation desirable | **Yes, if strict 0-24-h definition is mandatory** |

---

# 12. PCIA bolus demand

Table 4:

| Group | PCIA bolus demands |
|---|---:|
| TEAS | **0 (0-2)** |
| Control | **2 (1-4)** |
| P-value | **<0.001** |

Reported estimated mean difference:
- **-1.75** (95% CI -2.96 to -0.53)

### Interpretation
TEAS substantially reduced patient-driven PCIA demand.

---

# 13. Rescue analgesia

Table 4:

| Outcome | TEAS | Control | P |
|---|---:|---:|---:|
| Rescue analgesia demands | **14/45 (31.11%)** | **29/48 (60.42%)** | **0.005 in Table 4** |

## Calculated from raw events
- Crude RR ≈ **0.515**
- Absolute risk reduction ≈ **29.3 percentage points**
- NNT ≈ **3.4**

### Major reporting inconsistency
Table 4 reports:
- **RR 0.70 (95% CI 0.44-1.10)**
- **P=0.005**

These values are internally incompatible because:
- crude RR from event counts is about **0.52**, not 0.70
- the reported 95% CI **crosses 1**
- yet the reported P-value is significant.

The Results prose also reports a different P-value:
- **P=0.002**

### Extraction decision
Use the **raw event counts** as primary data and flag the published RR/CI/P-value as inconsistent.

---

# 14. Primary pain outcomes

Primary outcomes were maximum:
- visceral pain
- incisional pain
- low-back pain (LBP)

at:
- POD0
- POD1
- POD2

POD0 measurements were obtained within the **first 6 postoperative hours**.

---

# 15. Visceral pain

Adjusted GEE:
- overall TEAS group effect: **P=0.007**

Post-hoc:
- POD0: adjusted beta magnitude **0.72**, 95% CI **0.20 to 1.25**, P=0.007
- POD1: adjusted beta magnitude **0.96**, P=0.009
- POD2: no significant difference after Bonferroni threshold in maximum score

### Major POD1 confidence-interval problem
The Results print:
- beta = **0.96**
- 95% CI **[1.67, 2.65]**

The estimate lies outside the printed CI, so this is internally impossible and requires verification.

---

# 16. Moderate-to-severe visceral pain

Read directly from **Figure 3D on page 8**:

| Time | TEAS | Control | P |
|---|---:|---:|---:|
| POD0 | **6.7%** | **25.0%** | **0.016** |
| POD1 | **8.9%** | **37.5%** | **0.001** |
| POD2 | **0%** | **6.2%** | **<0.001** |

### Interpretation
TEAS markedly reduced moderate-to-severe visceral pain across POD0-POD2.

---

# 17. Low-back pain

Adjusted GEE:
- overall TEAS group effect: **P=0.012**

Post-hoc:
- POD0 beta magnitude **0.65**, 95% CI 0.14-1.16, P=0.012
- POD1 beta magnitude **1.06**, 95% CI 0.20-1.91, P=0.016
- POD2 beta magnitude **0.71**, 95% CI 0.24-1.20, P=0.003

---

# 18. Moderate-to-severe low-back pain

From **Figure 3F on page 8**:

| Time | TEAS | Control | P |
|---|---:|---:|---:|
| POD0 | **2.2%** | **14.6%** | **<0.001** |
| POD1 | **17.8%** | **29.2%** | **0.679** |
| POD2 | **2.2%** | **4.2%** | **0.106** |

### Note
The article text says the incidence was significantly reduced on POD0, which matches the figure.  
The POD1 and POD2 incidence differences were not significant after correction.

---

# 19. Incisional pain

Adjusted GEE group effect:
- estimate **-0.281**
- **P=0.210**

No significant differences were observed in maximum incisional-pain scores or moderate-to-severe incisional-pain incidence.

From **Figure 3E on page 8**:

| Time | TEAS | Control | P |
|---|---:|---:|---:|
| POD0 moderate/severe | **2.2%** | **4.2%** | **0.542** |
| POD1 moderate/severe | **2.2%** | **4.2%** | **0.688** |
| POD2 moderate/severe | **2.2%** | **2.1%** | **0.995** |

### Interpretation
TEAS did **not** improve incisional pain.

---

# 20. Cytokines on POD1

Table 3:

| Cytokine | TEAS | Control | MD (95% CI) | P |
|---|---:|---:|---|---:|
| IL-2 | **2.58 ± 0.29** | **2.61 ± 0.45** | -0.03 (-0.12 to 0.19) | 0.67 |
| IL-4 | **2.88 ± 1.20** | **3.17 ± 1.45** | -0.29 (-0.84 to 0.26) | 0.30 |
| IL-6 | **16.63 ± 13.85** | **38.59 ± 29.22** | **-21.96 (-31.48 to -12.44)** | **<0.001** |
| TNF-alpha | **2.87 ± 1.37** | **2.57 ± 0.28** | 0.30 (-0.10 to 0.70) | 0.14 |

### Interpretation
Only **IL-6** was significantly lower with TEAS.

Units are **not clearly specified in the table excerpt** and should not be inferred.

---

# 21. Recovery outcomes

Table 5:

| Outcome | TEAS | Control | P |
|---|---:|---:|---:|
| Pelvic drain removal, h | **19.95 ± 7.89** | **29.10 ± 17.51** | **0.005** |
| First ambulation, h | **19.91 ± 5.88** | **28.31 ± 19.01** | **0.006** |
| Postoperative discharge, d | **4.07 ± 1.68** | **6.06 ± 4.28** | **0.004** |
| First flatus, h | **13.14 ± 10.53** | **16.60 ± 10.36** | 0.110 |
| First oral liquid, h | **7.11 ± 5.66** | **9.16 ± 5.39** | 0.077 |
| First solid food tolerance, h | **13.11 ± 7.53** | **15.16 ± 5.79** | 0.140 |
| Hospitalization cost, yuan | **14,542 ± 158** | **15,903 ± 15,245** | **<0.001 in table** |

---

# 22. Major recovery-table inconsistencies

Several Table 5 statistics are internally inconsistent.

## Postoperative discharge
Printed:
- MD **-2.05 days**
- 95% CI **-4.32 to 0.23**
- **P=0.004**

The CI crosses 0, which conflicts with P=0.004.

## Solid-food tolerance
Printed:
- MD **-2.00 h**
- 95% CI **-3.35 to -0.64**
- **P=0.140**

The CI excludes 0, which conflicts with P=0.140.

## Hospital costs
Table:
- TEAS **14,542 ± 158**
- Control **15,903 ± 15,245**
- MD **-1361**
- 95% CI **-1951 to -770**
- **P<0.001**

Results prose says:
- costs were **higher in TEAS**
- yet the table values and negative MD show costs were **lower in TEAS**.

The Results prose also gives **P=0.004**, not <0.001.

### Extraction decision
Preserve the raw table values and flag these inferential statistics for verification.

---

# 23. PONV and other complications

Table 6:

| Outcome | TEAS | Control | RR (95% CI) | P |
|---|---:|---:|---|---:|
| PONV | **14/45 (31.11%)** | **25/48 (52.08%)** | **0.60 (0.36-0.99)** | **0.04** |
| Shoulder pain | 1 (2.22%) | 2 (4.17%) | 0.53 (0.05-5.82) | 0.99 |
| Sleep disturbance | 8 (17.78%) | 6 (12.50%) | 1.42 (0.54-3.78) | 0.48 |
| Dizziness | 5 (11.11%) | 6 (12.50%) | 0.89 (0.29-2.71) | 0.84 |
| Surgical-site infection | 0 | 1 (2.08%) | NA | 0.33 |
| Fever | 12 (26.67%) | 8 (16.67%) | 1.60 (0.72-3.55) | 0.24 |
| Cough | 7 (15.56%) | 12 (25.00%) | Printed RR 0.62 (0.69-1.44) | 0.26 |
| Allergic reaction | 0 | 1 (2.08%) | NA | 0.33 |
| Abdominal distension | 5 (11.11%) | 6 (12.50%) | 0.89 (0.29-2.71) | 0.84 |
| Intermuscular venous thrombosis | 0 | 1 (2.08%) | NA | 0.33 |

### Cough RR inconsistency
The printed cough RR is **0.62**, but its 95% CI is **0.69-1.44**, which does not contain the point estimate.

---

# 24. Key review variables

| Review variable | Extraction |
|---|---|
| Modality | **TEAS** |
| Invasive | **No** |
| Surgery | **Laparoscopic hysterectomy** |
| Acupoints | **Bilateral LI4 + PC6 + SP6 + ST36** |
| Device | **HANS-200F** |
| Frequency | **2/100 Hz** |
| Waveform | **Dense-disperse** |
| Active intensity | **1 mA below maximum tolerated threshold** |
| Sham intensity | **1 mA below sensory threshold** |
| Timing | **30 min pre-induction through entire surgery** |
| Postoperative TEAS | **No** |
| Induction sufentanil | **0.4 µg/kg** |
| PCIA opioid | **Sufentanil** |
| PCIA concentration | **1 µg/mL calculated** |
| Background infusion | **2 µg/h calculated** |
| Bolus | **2 µg calculated** |
| Lockout | **10 min** |
| POD1 sufentanil | **50.53 ± 4.46 vs 53.79 ± 5.14 µg** |
| Relative opioid reduction | **~6.1%** |
| PCIA bolus demands | **0 (0-2) vs 2 (1-4)** |
| Rescue analgesia | **31.1% vs 60.4%** |
| Visceral pain | **Lower on POD0-POD1** |
| LBP | **Lower POD0-POD2** |
| Incisional pain | **No effect** |
| IL-6 | **16.63 ± 13.85 vs 38.59 ± 29.22** |
| PONV | **31.1% vs 52.1%** |
| Ambulation | **19.91 vs 28.31 h** |
| Pelvic drain removal | **19.95 vs 29.10 h** |

---

# 25. Missing / unresolved Covidence fields

1. Covidence study ID
2. Exact recruitment dates: abstract vs Methods discrepancy
3. Explanation for **4 unaccounted pre-randomization patients**
4. Full ITT outcomes for all 108 randomized patients
5. Exact sham current amplitude in mA
6. Whether “1 mA below sensory threshold” delivered actual sub-sensory current throughout surgery
7. Exact 0-24-h definition for the POD1 sufentanil endpoint
8. Whether total sufentanil includes induction dose or only postoperative PCIA/rescue use
9. Exact PACU rescue sufentanil dose by group
10. Number of PACU rescue sufentanil administrations
11. Correct RR/CI/P for rescue analgesia
12. Correct visceral-pain POD1 beta confidence interval
13. Correct discharge mean difference / confidence interval / P-value
14. Correct solid-food tolerance P-value or confidence interval
15. Correct direction and P-value for hospitalization cost
16. Correct cough RR confidence interval
17. Cytokine measurement units
18. Full raw maximum pain values by group/time if needed for meta-analysis

---

# 26. Major methodological / audit issues

1. **108 randomized but only 93 analyzed**; no full ITT analysis.
2. Post-randomization exclusions were somewhat asymmetric: 9 TEAS vs 6 control.
3. Screening arithmetic is internally inconsistent: 120 assessed minus 8 listed exclusions does not yield 108 randomized.
4. Randomization and envelope concealment were otherwise clearly described.
5. Participants, anesthesiologists, and assessors were blinded.
6. Sham stimulation was **sub-sensory rather than clearly zero-current**, which is a relatively rigorous comparator but requires precise coding.
7. TEAS was preoperative + intraoperative only.
8. The trial provides a **direct continuous POD1 sufentanil endpoint**.
9. The opioid reduction is statistically significant but only about **6%**, likely below a clinically meaningful opioid-sparing threshold.
10. PCIA-demand and rescue-analgesia outcomes strongly favor TEAS.
11. The rescue-analgesia RR/CI/P-values are internally inconsistent; raw counts should be prioritized.
12. Pain benefit was phenotype-specific:
    - strong for visceral pain
    - strong for low-back pain
    - absent for incisional pain.
13. Wound infiltration with ropivacaine may have reduced the ability to detect incremental incisional analgesia.
14. Figure 3 provides exact moderate-to-severe pain percentages and should be retained.
15. IL-6 reduction was large, while IL-2, IL-4, TNF-alpha were unchanged.
16. Several recovery-table confidence intervals and P-values are internally inconsistent.
17. Hospital-cost direction in the prose contradicts the numeric table.
18. The cough RR lies outside its printed CI.
19. Single-center trial with modest analyzed sample size.
20. Chronic postoperative pain was not assessed.

---

# 27. Suggested author-contact questions

1. **Can you clarify the participant flow? 120 assessed minus the 8 listed exclusions would leave 112, but only 108 were randomized.**
2. **Can you provide an ITT analysis for all 108 randomized participants?**
3. **Does the POD1 total sufentanil value represent cumulative postoperative sufentanil over exactly the first 24 h?**
4. **Does total POD1 sufentanil include only PCIA/rescue doses, or also the 0.4-µg/kg induction dose?**
5. **What actual sham current was delivered when the device was set 1 mA below sensory threshold?**
6. **Can you provide exact PACU rescue sufentanil consumption by group?**
7. **Can you clarify the rescue-analgesia RR 0.70 (0.44-1.10), which does not match the raw event ratio and conflicts with the reported significant P-value?**
8. **What is the correct P-value for rescue analgesia: 0.002 in the Results text or 0.005 in Table 4?**
9. **What is the correct 95% CI for the POD1 visceral-pain beta estimate of 0.96?**
10. **Can you clarify the discharge outcome, whose 95% CI crosses zero despite P=0.004?**
11. **Can you clarify the solid-food tolerance result, whose CI excludes zero despite P=0.140?**
12. **Were hospitalization costs lower or higher with TEAS, and what is the correct P-value?**
13. **Can you clarify the cough RR and 95% CI?**
14. **What were the units for IL-2, IL-4, IL-6 and TNF-alpha?**
15. **Can you provide raw maximum pain values by group/time if continuous pain meta-analysis is planned?**

---

# 28. Concise Covidence-ready summary

**Zhang et al. 2025** randomized **108 patients undergoing laparoscopic hysterectomy** to active TEAS or sham stimulation; **93 were included in the final analysis (45 TEAS, 48 control)**.

TEAS was delivered at **bilateral LI4, PC6, SP6 and ST36** using a **HANS-200F**, **2/100-Hz dense-disperse stimulation**, beginning **30 min before anesthesia and continuing throughout surgery**. Active intensity was set **1 mA below maximum tolerance**, whereas sham was set **1 mA below sensory threshold**.

All patients received standardized multimodal analgesia and postoperative IV sufentanil PCIA:
- reservoir: **100 µg/100 mL**
- background: **2 mL/h = 2 µg/h**
- bolus: **2 mL = 2 µg**
- lockout: **10 min**

The key opioid endpoint on POD1 was:
- **TEAS: 50.53 ± 4.46 µg**
- **Control: 53.79 ± 5.14 µg**
- MD **-3.26 µg**
- **P=0.002**
- calculated reduction ≈ **6.1%**

This is a statistically significant but **small opioid-sparing effect**. The magnitude is unlikely to represent clinically meaningful opioid sparing if your threshold is substantially larger than 6%.

PCIA bolus demand also favored TEAS:
- **0 (0-2) vs 2 (1-4), P<0.001**

Rescue analgesia:
- **14/45 (31.1%) vs 29/48 (60.4%)**
- raw-event RR ≈ **0.52**
- but the article reports internally inconsistent RR/CI/P-values.

Pain effects were differential:
- **visceral pain lower on POD0-POD1**
- **low-back pain lower on POD0-POD2**
- **incisional pain unchanged**

Figure 3 shows moderate-to-severe visceral pain:
- POD0 **6.7% vs 25.0%**
- POD1 **8.9% vs 37.5%**
- POD2 **0% vs 6.2%**

TEAS also reduced IL-6 and PONV and accelerated ambulation and pelvic-drain removal.

The major audit issues are the **unreconciled 120-to-108 screening flow, 108-to-93 complete-case analysis, inconsistent rescue-analgesia statistics, impossible visceral-pain confidence interval, and several contradictory recovery-table CIs/P-values**.
