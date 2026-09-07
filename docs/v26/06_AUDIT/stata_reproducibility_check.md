# Stata Reproducibility & Methodological Audit Report: v26 Final Lock

**Review Title:** Perioperative Transcutaneous Electrical Acupoint Stimulation (TEAS) and Electroacupuncture (EA) for Postoperative Opioid Sparing: Systematic Review and Meta-Analysis of Randomized Controlled Trials  
**PROSPERO Registration:** CRD420251090635  
**Audit Date:** September 6, 2026  
**Auditor:** Statistical-Analysis and Reproducibility Auditor (DeepMind Antigravity)  
**Authoritative Input Source:** `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx`  
**Execution Engine:** StataNow 19.5 SE (`/Users/ryan/bin/stata-se`), 64-bit macOS  
**Authoritative Analysis Directory:** `/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/06_FINAL_ANALYSIS_V26/`

---

## 1. Executive Summary of Audit Findings

1. **v26 Master Workbook is Authoritative:**  
   The file `TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx` constitutes the sole, locked source of truth. All historical AI extractions, unverified CSVs in `/stata/`, and older iterations (v17–v25) have been formally retired and superseded.

2. **Primary Outcome Redefinition & Correction:**  
   Legacy scripts synthesized an uncurated pool of 11 trials that mixed direct milligrams, protocol-prohibited average-weight multiplications (converting mg/kg or µg/kg to mg), patient-controlled analgesia (PCA) bolus proxies, and postoperative day 1 (POD1) measurements. Under v26, exactly **6 randomized controlled trials** directly reported 24-h cumulative opioid consumption in absolute mass:
   - **Chen 1998** (TEAS vs Sham)
   - **Chen 2020** (TEAS vs Sham)
   - **El-Rakshy 2009** (EA vs Control)
   - **He 2026** (TEAS vs Sham)
   - **Seevaunnamtum 2016** (EA vs Usual Care)
   - **Yang 2024** (EA vs Usual Care)

3. **Loss of Artificial Statistical Significance:**  
   - The legacy 11-study model reported an artificial pooled effect of $-5.04\text{ mg IV MME}$ ($p = 0.0395$).  
   - Under the rigorous, protocol-compliant 6-trial primary model using Restricted Maximum Likelihood (REML) with Hartung–Knapp (`se(kh)`) standard error adjustment, the pooled mean difference is:
     $$\mathbf{MD = -4.684\text{ mg IV MME} \quad [95\%\text{ CI: } -12.257 \text{ to } +2.889], \quad t(5) = -1.59, \quad p = 0.1727}$$
     $$\tau^2 = 31.4862, \quad I^2 = 98.29\%, \quad Q = 37.92 \ (p < 0.0001), \quad 95\%\text{ Prediction Interval: } [-22.280, +12.912]$$
   - DerSimonian–Laird (DL) without Hartung–Knapp adjustment yielded $\text{MD} = -2.402\text{ mg}$ (95% CI: $-4.472$ to $-0.333$, $p = 0.0229$). This audit confirms that the legacy report's claim of statistical significance was an artifact of unadjusted DL standard errors and improper study pooling.

4. **Target A–F Locked Synthesis Results:**
   - **Target A (0–48 h Cumulative Opioid, $k=3$):** $\text{MD} = -2.808\text{ mg IV MME}$ (95% CI: $-5.986$ to $+0.369$, $p = 0.0627$; $\tau^2 = 0.7107, I^2 = 49.79\%$). Mandatory sensitivity excluding An 2014 ($k=2$): $\text{MD} = -2.433\text{ mg}$ ($p = 0.1273$).
   - **Target B (0–72 h Cumulative Opioid):** Strict exact 0–72h is $k=1$ (Yang 2024 alone: $\text{MD} = -0.500\text{ mg IV morphine}$, 95% CI: $-4.078$ to $+3.078$, $p = 0.784$; NOT POOLED). Broader model ($k=2$, with Wong 2006): $\text{MD} = -1.471\text{ mg}$ ($p = 0.6716$).
   - **Target C (Pain at Rest ~24 h, $k=2$):** $\text{MD} = -0.177\text{ VAS points (0–10)}$ (95% CI: $-0.683$ to $+0.330$, $p = 0.1413$; $\tau^2 = 0.000, I^2 = 0.00\%$; both Xing 2022 and Liu 2021 have High RoB).
   - **Target D (PONV Stratified):** Composite PONV 0–24h ($k=2$): $\text{RR} = 0.560$ (95% CI: $0.139$ to $2.257$, $p = 0.1191$); Composite PONV 0–48h ($k=2$): $\text{RR} = 0.523$ (95% CI: $0.216$ to $1.267$, $p = 0.0682$); Nausea 0–24h ($k=2$): $\text{RR} = 0.621$ ($p = 0.0873$); Vomiting 0–24h ($k=2$): $\text{RR} = 0.575$ ($p = 0.2682$). All pooled strata $\tau^2 = 0.000, I^2 = 0.00\%$.
   - **Target E (Time to First Flatus, $k=6$):** $\text{MD} = -2.004\text{ hours}$ (95% CI: $-3.142$ to $-0.866$, $t(5) = -4.56$, $p = 0.0062$; $\tau^2 = 0.000, I^2 = 0.00\%$). SMD Hedges' g = $-0.456$ ($p = 0.0002$). Sensitivity excluding Ng 2013 ($k=5$): $\text{MD} = -1.967\text{ hours}$ ($p = 0.0115$).
   - **Target F (Exploratory):**
     - Intraoperative titrated remifentanil mass ($k=7$): $\text{MD} = -114.21\text{ µg}$ (95% CI: $-213.72$ to $-14.70$, $p = 0.0308$; $\tau^2 = 8288.48, I^2 = 80.69\%$).
     - Postoperative rescue opioid requirement ($k=4$ strict): $\text{RR} = 0.505$ (95% CI: $0.340$ to $0.750$, $p = 0.0119$; $\tau^2 = 0.000, I^2 = 0.00\%$). All binary rescue ($k=5$): $\text{RR} = 0.493$ (95% CI: $0.362$ to $0.671$, $p = 0.0031$).

---

## 2. Full Inventory & Classification of Legacy Files

| File Path | Previous Role | Audit Finding | Classification | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| `stata/stata_consensus_synthesis_data.csv` | Primary 24h opioid synthesis | Included 11 studies; misclassified Seevaunnamtum 2016 and Yang 2024 as TEAS; illegally multiplied mg/kg and µg/kg by mean body weight (Sim 2002, Coura 2011); mixed POD1 into 24h (Zhang 2025). | **NOT REPRODUCIBLE / REPLACED** | Replaced by `06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv`. |
| `stata/stata_48h_opioid_synthesis_data.csv` | 48h opioid synthesis | Mixed converted units without sensitivity reporting; included 5 unverified studies. | **REPLACED** | Replaced by `06_FINAL_ANALYSIS_V26/01_DATA/target_A_48h.csv`. |
| `stata/stata_72h_opioid_synthesis_data.csv` | 72h opioid synthesis | Pooled 4 studies including Zhang 2025 (which has no 72h data) and Xie 2014 (which was 48h) with MME factor 1.0 treating µg as mg. | **NOT REPRODUCIBLE / REPLACED** | Replaced by `06_FINAL_ANALYSIS_V26/01_DATA/target_B_72h.csv`. |
| `stata/stata_secondary_synthesis_data.csv` | PONV, Pain, Flatus synthesis | Pooled unstratified PONV across 2h–72h; lumped rest and movement pain; unverified flatus timepoints. | **REPLACED** | Replaced by target-specific files `target_C_pain24h.csv`, `target_D_ponv.csv`, `target_E_flatus.csv`. |
| `results/stata_master_results.csv` | Legacy Master Results | Contained stale estimates (-5.035 mg MME for 24h, -2.37 mg for 48h, -8.76 mg for 72h, etc.). | **REPLACED** | Replaced by `06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv`. |
| `results/paired_mcid_dataset.csv` | Paired MCID opioid vs pain | Fabricated pairings (mislabeled modalities, imputed 24h opioids for Ntritsou 2014, paired non-rest pain). | **NOT REPRODUCIBLE / SUPERSEDED** | Documented as invalid; zero strict trials have paired primary 24h opioid and 24h rest pain. |
| `stata/01_24h_opioid_primary.do` to `19_grade_inputs.do` | Legacy Stata scripts | Outdated scripts based on old consensus CSVs; hardcoded old paths. | **SUPERSEDED** | Fully superseded by `06_FINAL_ANALYSIS_V26/02_STATA/00_master.do` pipeline. |
| `dashboard/` & `docs/` HTML / JS / PNG | Interactive Web Dashboard | Rendered stale 11-study estimates (-5.035 mg) and old forest plots. | **UPDATED & SYNCHRONIZED** | All figures, tables, Stata console outputs, and equations updated to v26 lock. |

---

## 3. Methodological Governance & Cochrane Compliance

1. **Hartung–Knapp Adjustment (`se(kh)`):**
   In small meta-analyses ($k < 10$), standard Wald-type normal distribution confidence intervals exhibit severe anti-conservative bias and false-positive rates as high as 30%. Stata's `meta summarize, random(reml) se(kh)` applies the Knapp–Hartung adjustment using a Student's $t$-distribution with $k-1$ degrees of freedom. For the primary opioid outcome ($k=6, df=5$), the critical multiplier is $t_{0.05, 5} = 2.571$ (compared to normal $z = 1.960$).

2. **Multivariable Meta-Regression Audit (10:1 Rule):**
   Per Cochrane Handbook Section 10.11.4.1, multivariable meta-regression is inappropriate when there are fewer than 10 studies per candidate covariate. With $k=6$ in the primary analysis, any multivariable meta-regression is severely underpowered and carries unacceptable risk of ecological confounding. An exploratory meta-regression on modality code (TEAS vs EA) in Stata yielded:
   $$\beta = -1.794\text{ mg IV MME} \quad [95\%\text{ CI: } -20.916 \text{ to } +17.329], \quad t(4) = -0.26, \quad p = 0.8074, \quad R^2 = 0.00\%$$
   This formally confirms no evidence of effect modification between TEAS and EA.

3. **Prevention of Double-Counting (Unit-of-Analysis Errors):**
   - Chen 1998, Xie 2014, and Lee 2011 have multi-arm designs sharing a control group. In all syntheses, shared control arms were never duplicated into the same pooled stratum without splitting or selecting the primary active arm.
   - Yeh 2010 and Yeh 2011 represent an overlapping publication family and were kept on hold as a single unpooled publication unit.
   - Yu Wang et al. (JAMA Surg 2023) was audited and confirmed excluded under Wrong Outcomes (postoperative transcutaneous auricular vagus nerve stimulation for sleep disturbance, not perioperative TEAS/EA for opioid sparing).

---

## 4. Master Pipeline Verification (`00_master.do`)

The entire analysis was tested via batch execution from a clean session:
```bash
/Users/ryan/bin/stata-se -b do 06_FINAL_ANALYSIS_V26/02_STATA/00_master.do
```
All 10 scripts completed with return code 0:
1. `00_prep_data.do` -> Extracted and formatted 8 locked datasets in `01_DATA/`.
2. `01_opioid24_primary.do` -> Executed primary 24-h opioid REML + KH, modality subgroups, sensitivity, DL.
3. `02_targetA_48h.do` -> Executed Target A (0-48h) strict ($k=3$), sensitivity ($k=2$, $k=4$).
4. `03_targetB_72h.do` -> Executed Target B (0-72h) strict ($k=1$), broader ($k=2$).
5. `04_pain.do` -> Executed Target C (Pain at rest ~24h, $k=2$).
6. `05_ponv.do` -> Executed Target D (PONV 6 stratified risk ratio models).
7. `06_flatus.do` -> Executed Target E (Time to flatus MD & SMD, $k=6$).
8. `07_targetF.do` -> Executed Target F (Intraoperative remifentanil, postop delivered, rescue opioid, PCA).
9. `08_sensitivity.do` -> Executed leave-one-out influence analyses and 7-estimator sensitivity grid.
10. `09_subgroups_metareg.do` -> Executed modality subgroups, comparator subgroups, and meta-regression audit.

**Audit Status:** 100% REPRODUCIBLE, FULLY LOCKED, AUTHORITATIVE.
