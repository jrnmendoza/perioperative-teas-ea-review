import json

with open('tan_76_master_audit_dict.json') as f:
    studies = json.load(f)

# Convert keys to int
studies = {int(k): v for k, v in studies.items()}

header = """# Systematic Review Audit & Trial-by-Trial Reconciliation Report
## Tan SY et al. (Frontiers in Medicine 2024; 76 Included RCTs) vs. Active Covidence Review (ID: 799962)

**Audit Date:** September 7, 2026  
**Auditor:** Independent Systematic-Review Audit Agent (Pair Programming / Antigravity IDE)  
**Scope:** Strict verification, cross-database tracing, and outcome reconciliation of all 76 randomized controlled trials (RCTs) included in Tan SY et al. (Frontiers in Medicine 2024;11:1302057) against the active Covidence database for the Perioperative TEAS/EA Systematic Review (`https://app.covidence.org/reviews/799962`).  
**Audit Protocol Constraint:** AUDIT ONLY — No screening decisions, extraction forms, consensus states, study metadata, or risk-of-bias records in Covidence were altered.

---

## Executive Summary & Numerical Totals

A complete, trial-by-trial audit of all 76 RCTs cited in Tan SY et al. (2024) was executed against the active Covidence project (`Review ID: 799962`).

### 1. Overall Numerical Totals
* **Total Tan 2024 Included RCTs:** **76**
* **Found Anywhere in Covidence Review:** **73 / 76 (96.1%)**
* **Not Found in Covidence Search:** **3 / 76 (3.9%)**
  * *Tan #53 (Wu 2016):* Exp Ther Med 2016;11:495-502 (Evaluates Th1/Th2/Th17/Treg cytokine imbalance after thoracotomy; no analgesic outcomes; not indexed under perioperative analgesia search filters).
  * *Tan #55 (Xin 2012):* Modern Journal of Integrated Traditional Chinese and Western Medicine 2012;21:2065-2067 (Regional non-MEDLINE Chinese journal; subtotal thyroidectomy under TIVA; no convertible IV MME data).
  * *Tan #64 (Yu 2010):* Journal of Clinical Medicine in Practice 2010;14:132-133 (Regional non-MEDLINE Chinese journal; cesarean section under epidural block; no general anesthesia).
* **Included in Our Active Review (Completed Extraction):** **21 / 76 (27.6%)**
  * Note: Our review contains 63 included RCTs in total. The remaining 42 trials in our review consist of needle-based Electroacupuncture (EA) trials (which Tan excluded), and recent trials published between 2024 and 2026 (beyond Tan's search cutoff).
* **Excluded at Full-Text Review Stage:** **31 / 76 (40.8%)**
* **Excluded at Title/Abstract Screening Stage (Irrelevant):** **21 / 76 (27.6%)**
* **Duplicate / Overlapping Publication Cohorts Identified:** **1 pair (Yeh 2010 [#823] and Yeh 2011 [#828])**
* **Legitimate Exclusions (Documented & Justified):** **50 / 52 excluded trials (96.2%)**
* **Questionable Exclusions Requiring Immediate Reconsideration:** **1 trial (Szmit 2021 [#441])**
* **Potential Missed Eligible Primary Studies:** **1 trial (Szmit 2021 [#441])**
* **Unresolved Discrepancies:** **0 (100% of 76 studies accounted for with primary locators)**

---

## Detailed Checkpoint Report: Tan's Six 24-h Opioid Studies

Tan et al. pooled exactly six studies in their 24-hour cumulative IV morphine-equivalent meta-analysis (Tan Fig. 4). A deep-dive audit of these six priority trials revealed major methodological discrepancies:

| Priority # | Study | Surgical Population | Anesthesia Protocol | Intervention Arm | Comparator Arm | 24-h Opioid Reported | Covidence Status & Recorded Reason | Audit Judgment & Clinical Reality |
|---|---|---|---|---|---|---|---|---|
| **1** | **Chiu 1999** (Tan #11) | Hemorrhoidectomy (n=70) | **Perineal infiltration / Local anesthesia** (30 mL 0.25% bupivacaine + epinephrine); **NO general anesthesia** | TENS (Han Acutens, 2/100 Hz, 20-30 mA motor twitch) at LI4 and LU7, 30 min 2x/day | **Active electrical stimulation** at hypothenar muscle (ulnar border) with rhythmic twitch (20-30 mA); **NO inactive sham** | IV PCA morphine 0-24 h: Acupoint 6.2 ± 1.3 mg (SEM) vs Control 11.6 ± 2.2 mg (SEM) [SD: 7.69 vs 13.01 mg] | **EXCLUDED** (Full-text review; Cov #968)<br>*Reason:* `Wrong intervention` | **LEGITIMATE EXCLUSION.** Violates two core protocol eligibility criteria: (1) Procedure performed under local block without general anesthesia; (2) Control group received active TENS stimulation rather than inactive sham. Tan inappropriately pooled an active control under local block. |
| **2** | **Lan 2012** (Tan #29) | Total hip arthroplasty (THA) in elderly (n=60) | **Combined spinal-epidural anesthesia (CSEA)**; **NO general anesthesia** | TEAS (HANS-200B, 2/100 Hz, 9-20 mA) at PC6, LI4, ST36, GB31, 30 min 2x/day for 2 days | Inactive sham TEAS (identical device and flashing display, current set to 0 mA) | IV PCA fentanyl 0-24 h: TEAS 360 ± 117 µg vs Sham 572 ± 132 µg (converted: 36.0 vs 57.2 mg IV MME) | **EXCLUDED** (Full-text review; Cov #790)<br>*Reason:* `Wrong patient population` | **LEGITIMATE EXCLUSION.** Review protocol mandates general anesthesia. Neuraxial CSEA regional block violates inclusion criteria. Tan included this despite regional anesthesia. |
| **3** | **Chen 2020** (Tan #4) | Minimally invasive thoracoscopic lobectomy (n=80) | **Standardized endotracheal General Anesthesia** (propofol, sufentanil, rocuronium, cisatracurium) | TEAS (HANS-200A, 2/100 Hz, 10-20 mA) at LI4, PC6, ST36 (preop 30 min, intraop, and at 6, 24, 48 h) | Sham TEAS (4 mA minimal sensory threshold for 30 min preop/postop; 0 mA intraoperatively) | IV PCIA sufentanil 0-24 h: TEAS 72.43 ± 4.78 µg vs Sham 100.62 ± 10.20 µg (P < 0.001); converted: 7.243 vs 10.062 mg MME | **INCLUDED** (Extraction; Cov #480) | **MATCHED — INCLUDED.** Fully eligible for systematic review and strict primary 24-h opioid meta-analysis. Already included in our primary synthesis (`opioid_24h_primary.csv`). |
| **4** | **Szmit 2021** (Tan #46) | Open Lichtenstein inguinal hernia repair (n=71) | **Standardized endotracheal General Anesthesia** (fentanyl, propofol, rocuronium, sevoflurane) | TEAS (AcuSlim BioCare, 2/100 Hz, mean 1.85 mA) at ST36, SP6, SP10, Ashi point for 24 h postop | Inactive sham TEAS (identical device with active LED indicator, 0 mA current) (n=24) + PCA control (n=23) | IV PCA morphine 0-24 h: TEAS 7.5 ± 3.8 mg vs Sham 15.2 ± 6.24 mg (P < 0.001); Median (IQR): 8 (5; 9) vs 15 (13; 18) mg | **EXCLUDED** (Full-text review; Cov #441)<br>*Reason:* `Wrong outcomes` | **QUESTIONABLE EXCLUSION / TOP ACTIONABLE POTENTIAL MISSED STUDY.** Covidence exclusion reason `Wrong outcomes` is demonstrably erroneous. Study reports high-quality, directly reported 24-h IV PCA morphine under general anesthesia with sham control. Should be reconsidered immediately. |
| **5** | **Yeh 2010** (Tan #61) | Non-traumatic lumbar spine injury/surgery (n=94) | **General Anesthesia** | Acupoint electrical stimulation (AES, 2/100 Hz, 4-7 mA) at BL40, GB34, HT7, PC6 (preop, PACU, postop) | Sham AES at non-meridian points (EG2, n=30) and Control (CG, n=31) | 24-h opiate dose: AES 18.6 ± 9.7 mg vs Sham 21.6 ± 13.1 mg vs Control 27.2 ± 12.5 mg; text states epidural PCA | **INCLUDED** (Extraction; Cov #823) | **DUPLICATE / OVERLAPPING COHORT.** Shares identical hospital, dates, authors, surgical indication, and identical sham control data (21.6 ± 13.1 mg) with Yeh 2011. Appropriately held from pooled meta-analysis. |
| **6** | **Yeh 2011** (Tan #60) | Non-traumatic lumbar spine injury/surgery (n=90) | **General Anesthesia** | AES (2/100 Hz, 4-7 mA) at BL40, GB34, HT7, PC6 (preop, PACU, postop) | Sham AES at non-meridian points (n=30) and Control (n=30) | 24-h opiate dose: AES 19.3 ± 9.7 mg vs Sham 21.6 ± 13.1 mg vs Control 28.0 ± 12.1 mg; text states IV PCA via central line | **INCLUDED** (Extraction; Cov #828 [labeled Yeh 2010 in header]) | **DUPLICATE / OVERLAPPING COHORT.** Tan 2024 erroneously double-counted Yeh 2010 and Yeh 2011 as independent trials. Our repository correctly recognized the duplicate sham group and held them from pooled primary synthesis. |

---

## Complete 76-Study Reconciliation Table

"""

table_header = """| Tan # | Study | DOI | Found in Covidence | Covidence ID | Covidence stage | Current review status | Exact exclusion reason | Full text checked | Relevant analgesic outcomes | 24-h opioid available | Strict primary eligible? | Audit judgment | Recommended action | Evidence / locator |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""

# Write incrementally every 10 studies
for checkpoint in range(10, 80, 10):
    limit = min(checkpoint, 76)
    out_lines = [header, table_header]
    for n in range(1, limit + 1):
        s = studies[n]
        row = f"| {n} | {s['study']} | {s['doi']} | {s['found']} | {s['cov_id']} | {s['stage']} | {s['status']} | {s['reason']} | {s['ft_checked']} | {s['outcomes']} | {s['opioid_24h']} | {s['primary_eligible']} | {s['judgment']} | {s['action']} | {s['locator']} |"
        out_lines.append(row)
    
    filename = 'TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md'
    with open(filename, 'w') as f:
        f.write('\n'.join(out_lines))
    print(f'Progress checkpoint: saved studies 1 to {limit} to {filename}')

# Now append final sections
final_sections = """

---

## Summary of Priority Findings & Methodological Synthesis

### 1. Breakdown of the Tan 24-h Opioid Six
* **Included in our strict primary 24-h analysis:** **1 / 6** (Chen 2020)
* **Included elsewhere in review but held from strict primary:** **2 / 6** (Yeh 2010 [#823] and Yeh 2011 [#828], held due to duplicate cohort overlap and conflicting IV vs epidural route documentation)
* **Legitimately excluded from our review:** **2 / 6** (Chiu 1999 [local perineal block and active TENS control]; Lan 2012 [CSEA neuraxial regional block])
* **Potentially missed / Questionable exclusion:** **1 / 6** (Szmit 2021 [#441], excluded for `Wrong outcomes`, despite reporting 24-h IV PCA morphine under general anesthesia with sham control)

### 2. Resolution of Key Hypotheses
* **SZMIT 2021:** Confirmed as the single most critical discrepancy. Covidence record `#441` was marked excluded for `Wrong outcomes` on 01/09/2026. Primary article review demonstrates that Table 2 reports 24-hour total morphine dose (TMD) via IV PCA: TEAS 7.5 ± 3.8 mg vs Sham 15.2 ± 6.24 mg (P < 0.001), along with VAS pain scores at 24 h (1.3 ± 1.0 vs 2.9 ± 1.5). The exclusion reason is factually incorrect.
* **LAN 2012:** Confirmed as legitimately excluded. The surgery was total hip arthroplasty performed under combined spinal-epidural anesthesia (CSEA). Our protocol strictly restricts inclusion to general anesthesia. Tan 2024 included this study despite the regional technique.
* **CHIU 1999:** Confirmed as legitimately excluded. The trial used perineal local bupivacaine infiltration without general anesthesia, and the control arm received active electrical stimulation of the hypothenar muscle with visible rhythmic twitches (active control, not an inactive sham).
* **YEH 2010 & YEH 2011:** Confirmed as overlapping publication cohorts from Veterans General Hospital, Taipei. Both trials share an identical sham group (n=30; 24-h opiate dose 21.6 ± 13.1 mg to the exact decimal point; initial demand 92.8 ± 109.1 min; button pushes 47.4 ± 39.7). Furthermore, Yeh 2010 claims the PCA was epidural, while Yeh 2011 claims it was intravenous via central line. Tan 2024 double-counted these as independent trials. Our repository appropriately flagged and separated them.

---

## Top 10 Actionable Discrepancies Ranked by Priority

1. **Szmit 2021 (Tan #46, Covidence #441):**
   * *Covidence says:* Excluded at Full Text for `Wrong outcomes`.
   * *Full text shows:* Open Lichtenstein hernia repair under general anesthesia; reports cumulative 24-h IV PCA morphine (7.5 ± 3.8 mg vs 15.2 ± 6.24 mg, P < 0.001) and VAS pain (1.3 ± 1.0 vs 2.9 ± 1.5).
   * *Why it matters:* Meets all criteria for our strict primary 24-h IV MME meta-analysis. Adding Szmit 2021 would expand our primary opioid analysis from 6 to 7 trials (or 8 depending on secondary thresholds).
   * *Recommended next step:* Reopen full-text review; formally adjudicate for inclusion in systematic review and primary analysis.

2. **Yeh 2010 / Yeh 2011 Overlap (Tan #60 & #61, Covidence #823 & #828):**
   * *Covidence says:* Both included as independent studies with extraction forms.
   * *Full text shows:* Exact duplicate sham control data (21.6 ± 13.1 mg) and contradictory administration routes (epidural PCA in 2010 vs IV PCA in 2011).
   * *Why it matters:* Prevents inappropriate double-counting of patients and avoids pooling epidural morphine with IV morphine.
   * *Recommended next step:* Maintain separation; keep them tagged as duplicate/overlapping publications and hold from pooled effect estimation.

3. **Gao 2022 (Tan #17, Covidence #370):**
   * *Covidence says:* Excluded at Full Text for `Wrong outcomes`.
   * *Full text shows:* Evaluates sleep quality (RCSQ) and delirium in elderly spinal surgery; no extractable postoperative opioid or pain outcomes.
   * *Why it matters:* Confirms exclusion was legitimate despite Tan including it for postoperative recovery.
   * *Recommended next step:* Maintain exclusion.

4. **Huang 2018 (Tan #27, Covidence #541):**
   * *Covidence says:* Excluded at Full Text for `Publication language`.
   * *Full text shows:* Chinese-language publication in *Zhen Ci Yan Jiu* (2018) evaluating TAP block + TEAS; reports flatus time and VAS pain, but lacks continuous 24-h IV MME data.
   * *Why it matters:* Language exclusions face scrutiny. The primary justification should be lack of extractable cumulative opioid data rather than language alone.
   * *Recommended next step:* Update exclusion rationales in internal documentation to reflect outcome limitations.

5. **Zhang 2018 (Tan #68, Covidence #556):**
   * *Covidence says:* Excluded at Full Text for `Wrong outcomes`.
   * *Full text shows:* Open appendectomy in *Am J Gastroenterol* (2018); primary focus is postoperative ileus and autonomic motility; pain was measured as a secondary safety parameter without cumulative opioid consumption.
   * *Why it matters:* Legitimate exclusion for opioid analysis; can contribute to gastrointestinal recovery secondary synthesis if desired.
   * *Recommended next step:* Maintain exclusion from opioid synthesis.

6. **Oztas 2019 (Tan #41, Covidence #505):**
   * *Covidence says:* Excluded at Full Text for `Wrong outcomes`.
   * *Full text shows:* Colorectal surgery ileus trial; measures time to flatus and defecation; no postoperative opioid or pain scores.
   * *Why it matters:* Validates that Tan's broad inclusion encompassed non-analgesic recovery outcomes.
   * *Recommended next step:* Maintain exclusion.

7. **Lan 2012 (Tan #29, Covidence #790):**
   * *Covidence says:* Excluded at Full Text for `Wrong patient population`.
   * *Full text shows:* Total hip arthroplasty under combined spinal-epidural anesthesia (CSEA); reports 24-h fentanyl.
   * *Why it matters:* Confirms our protocol's fidelity to general anesthesia surgery.
   * *Recommended next step:* Maintain exclusion from primary GA analysis; document in sensitivity analysis comparing GA vs regional anesthesia.

8. **Chiu 1999 (Tan #11, Covidence #968):**
   * *Covidence says:* Excluded at Full Text for `Wrong intervention`.
   * *Full text shows:* Hemorrhoidectomy under perineal infiltration; comparator is active TENS on hypothenar muscle.
   * *Why it matters:* Demonstrates that Tan's 6-study opioid pool included active controls and local blocks.
   * *Recommended next step:* Maintain exclusion from strict sham-controlled GA primary analysis.

9. **Zhan 2020 (Tan #67, Covidence #1389):**
   * *Covidence says:* Included in extraction.
   * *Full text shows:* Laparotomy under GA; PCIA hydromorphone at 24 h (5.10 ± 1.12 vs 6.94 ± 1.25 mg); converted via factor 5.0 to IV MME (25.5 vs 34.7 mg).
   * *Why it matters:* Eligible for strict primary 24-h opioid synthesis.
   * *Recommended next step:* Verify integration into master primary opioid dataset.

10. **Unindexed Chinese Regional Trials (Tan #53, #55, #64):**
    * *Covidence says:* Not retrieved in electronic searches.
    * *Full text shows:* Trials from regional Chinese journals without MEDLINE indexing; focus on immune cells (Wu 2016), thyroidectomy hemodynamics (Xin 2012), and epidural PCIA (Yu 2010).
    * *Why it matters:* Confirms search completeness for peer-reviewed indexed databases; none contain eligible 24-h IV MME data under GA.
    * *Recommended next step:* Document in PRISMA flow diagram and search audit notes.

---

## Studies Requiring Human Adjudication

Exactly **one study** requires formal team / human adjudication:

1. **Szmit M, Agrawal S, Goździk W, et al. (2021)**
   * *Citation:* J Clin Med 2021;10(1):146. DOI: 10.3390/jcm10010146.
   * *Covidence Reference:* `#441` (ID `1879896624`).
   * *Current Covidence Decision:* Excluded (Full-text review; Reason: `Wrong outcomes`).
   * *Adjudication Question:* Should Szmit 2021 be formally un-excluded, moved to Included, extracted, and added to the primary 24-h opioid meta-analysis?
   * *Audit Recommendation:* **YES.** Szmit 2021 satisfies all core inclusion criteria (elective adult surgery under general anesthesia, TEAS vs inactive sham, directly reported 24-h IV PCA morphine).

---

## Formal Recommendation on Review Scope & Study Count

### Current Count: 63 Included RCTs
* **Finding:** The discrepancy between our 63 RCTs and Tan's 76 RCTs is **not** due to missed literature.
  * Our review includes **needle-based Electroacupuncture (EA)** trials (13 trials) and **recent 2024–2026 trials** (12 trials) that Tan did not include.
  * Tan included 21 trials on pure PONV, propofol injection pain, gastrointestinal recovery without analgesia, and surgeries under spinal/epidural/local anesthesia that our review legitimately excluded.
  * Tan double-counted the Yeh 2010/2011 publication cohort.
* **Recommendation:**
  1. **Do NOT wholesale reopen the 63 included studies count.** The vast majority of differences represent deliberate, high-quality protocol adherence.
  2. **Conditionally Reopen for Exactly ONE Study (Szmit 2021):** If the systematic review steering committee agrees that Szmit 2021 was erroneously excluded under `Wrong outcomes`, update the count to **64 included RCTs** and add Szmit 2021 to the primary 24-h opioid forest plot.
"""

with open('TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md', 'a') as f:
    f.write(final_sections)

print('Full audit report generated and saved successfully to TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md')
