# Tiered Primary-Outcome Derivability Audit — QC Report (v33)

**Date:** 2026-09-07
**Source of truth:** `TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx` (read-only; not modified)
**Scope of this pass:** derivability audit ONLY. No analysis was re-run, no dashboard value
was changed, no study classification was written back to any pipeline dataset.

---

## 1. Estimand

> Cumulative postoperative opioid consumption during the **first 24 hours after surgery**,
> standardized to intravenous morphine milligram equivalents (IV MME) where a defensible
> **prespecified, sourced** conversion is possible.

Eligibility for the estimand is defined **independently of reporting format**. Mean/SD is a
reporting convention, not the outcome.

Tiers are assigned **separately for two metrics**, because they have different requirements:

| Metric | Requirement | Consequence |
|---|---|---|
| **Absolute IV MME** | absolute mass + sourced conversion factor | weight-normalized units (mg/kg, µg/kg) are **not** usable |
| **SMD (Hedges' g)** | scale-invariant | weight-normalized units **are** usable; the unknown scaling constant cancels |

This distinction resolves an apparent contradiction in the existing pipeline: Coura 2011 and
Sim 2002 are legitimately in the broader **SMD** set while being genuinely ineligible for the
absolute-MME model.

---

## 2. Evidence derivability flow (computed from v32, not hard-coded)

```
70   included RCTs (v32 Study_Master)
 ↓
69   report any analgesic / pain / opioid outcome
 ↓
68   report a postoperative-opioid-consumption outcome family
 ↓
63   screened as potential 0–24 h opioid candidates (93 contrasts)
 ↓
21   report an exact 0–24 h cumulative postoperative opioid endpoint
 ↓
 7   Tier A  directly compatible (mean/SD + sourced absolute MME conversion)
 1   Tier B  deterministically derivable          (Chen 2015 — also Tier C in distribution)
 1   Tier C  alternative distribution             (Gao 2022)
 1   Tier D  recoverable only by digitization     (Gu 2019)
 8   Tier E  requires unverifiable assumptions
 3   Tier F  reports 0–24 h but not derivable     (Hou 2023, Yeh 2010, Yeh 2011)
```

The 42 remaining screened studies do not report an exact 0–24 h cumulative endpoint at all
(different window, different estimand, or no quantitative opioid consumption reported).

**This is the explanation for why strict primary k is much smaller than 70.**

---

## 3. Per-study QC table

| Study | v32 status | v33 tier (MME) | Change | Why | Primary? | Sensitivity? | PDF-verified? |
|---|---|---|---|---|---|---|---|
| Chen 1998 | inc_primary=1 | **A** | none | Exact 0–24 h PCA hydromorphone, mean/SD; sourced 5:1 factor | **Yes (S0, sham TEAS)** | — | v32 + prior pass |
| Chen 2020 | inc_primary=1 | **A** | none | Exact 0–24 h sufentanil, mean/SD; sourced 1000:1 | **Yes (S0, sham TEAS)** | — | prior pass |
| He 2026 (hepatectomy/JIS) | inc_primary=1 | **A** | none | Source reports MME directly | **Yes (S0, sham TEAS)** | — | prior pass |
| Szmit 2021 | inc_primary=1 | **A** | none | Exact 0–24 h PCA morphine, mean/SD | **Yes (S0, sham TEAS)** | — | prior pass |
| El-Rakshy 2009 | inc_primary=1 | **A** | **stratum** | Comparator is *PCA alone*, i.e. usual care — not sham | Supportive (usual-care EA) | — | prior pass |
| Seevaunnamtum 2016 | inc_primary=1 | **A** | **stratum** | Comparator is *standard care* | Supportive (usual-care EA) | — | prior pass |
| Yang 2024 | inc_primary=1 | **A** | **stratum** | Comparator is *usual care* | Supportive (usual-care EA) | — | prior pass |
| **Gao 2022** | absent from 24 h dataset | **C** | **ADD to S2** | Exact 0–24 h pump sufentanil **is** reported, as median (IQR) | No | **Yes (S2)** | ✅ `pdf-2.pdf` |
| **Chen 2015** | inc_sens=1, unclassified | **B+C** | **reclassify** | Deterministic: rescue count × fixed 2 mg IV morphine | No | **Yes (S2)** | ✅ `037_chen_2015_thyroidectomy_lund.pdf` |
| **Gu 2019** | absent from 24 h dataset | **D** | **ADD to S3 (pending)** | 24 h point exists only in Fig. 4; mL→µg is exact (1 µg/mL) | No | **Pending digitization** | ✅ `covidence_1471_full_article.pdf` |
| **Zhang 2025** | inc_sens=1 (in broader SMD k=10) | **E** | **REMOVE** | POD 1 ≠ 0–24 h: source defines "PODs 0 (day of surgery), 1, and 2" | No | **No** | ✅ `109551.pdf` |
| **Song 2020** | excluded | **E** | confirm + 2nd reason | Press-vs-delivery ambiguity **and** butorphanol has no sourced MME factor | No | No | ✅ `getfile.php-6.pdf` |
| **Oztas 2019** | excluded | **E** | confirm | No sourced tramadol/pethidine factor; combined-total SD unrecoverable | No | No | ✅ `covidence_505_full_article.pdf` |
| **Coura 2011** | inc_sens=1 (SMD set) | **E** (MME) / SMD-eligible | clarify | µg/kg; no weights reported; supplementary morphine also given | No | SMD only | ✅ `covidence_819_full_article.pdf` |
| **Chen 2015 (Hyperalgesia)** | inc_sens=1 | **E** (MME) / SMD-eligible | clarify | Deterministic in µg/kg only; absolute needs body weights | No | µg/kg only | ✅ `040_chen_2015_hyperalgesia_lund.pdf` |
| Sim 2002 | inc_sens=1 (SMD set) | **E** (MME) / SMD-eligible | clarify | mg/kg; shared placebo arm across two EA timing arms | No | SMD only | v32 |
| Jin 2023 | inc_sens=0 | **E** (MME) / SMD-eligible | clarify | mL of PCIA solution, concentration unreported; scale cancels in SMD | No | SMD only | v32 |
| Ntritsou 2014 | excluded | **E** | confirm | Total includes scheduled/background tramadol; not the estimand | No | No | v32 |
| Yeh 2010 / Yeh 2011 | duplicate hold | **F** | none | Overlapping cohort; Yeh 2010 route is **epidural**, not IV | No | No | v32 |
| Hou 2023 | excluded | **F** | none | Actual delivered sufentanil not reported | No | No | v32 |

---

## 4. Key verified findings

**Gao 2022 — the most consequential correction.**
`24 h analgesic pump, µg — 33.0 (0.0, 50.0) vs 30.0 (0.0, 60.0), P = 0.197` (n = 827/828).
This **is** the primary clinical estimand and must never be described as "primary outcome
unavailable." It is Tier C purely because of reporting format.
**It must not be transformed to mean/SD**: the 25th percentile is exactly **0.0 in both arms**,
so the distribution is zero-inflated and strongly non-normal, violating the normality
assumption the Wan/Luo estimators depend on.
*Direction note:* the point estimate slightly favours **sham** (33 vs 30 µg, P = 0.197). Adding
this trial to S2 will not inflate the intervention effect.

**Chen 2015 — deterministic derivation confirmed exactly.**
Source: "intravenous morphine 2 mg as rescue analgesia"; "Cumulative number of rescue analgesia
1 (1–3) vs 3.5 (2–7), P = 0.004". Multiplying by a positive constant is order-preserving, so
quantiles transform exactly: **2 (2–6) vs 7 (4–14) mg IV morphine**. Rescue morphine was the
only postoperative opioid, so this is complete 0–24 h exposure in the IV MME reference drug.

**Gu 2019 — conversion valid, window is the blocker.**
PCIA = 100 µg sufentanil in 100 mL ⇒ **exactly 1 µg/mL**, so mL and µg are numerically equal
(user's assumption confirmed). But the text reports **4 h, 8 h and 36 h** and skips 24 h; the
24 h point exists only in Fig. 4. Also note a fixed **2 mL/h basal infusion**, a large
protocol-mandated component common to both arms that dilutes the between-group contrast — this
must be recorded alongside any digitized value.

**Song 2020 — two independent blockers.**
(1) The source records "total number of **PCA pump presses**" and documents a **15-min lockout**;
presses and deliveries can therefore differ, and no delivered dose is reported. (2) Even with
resolved semantics, **butorphanol has no sourced IV MME equivalence** in this project's
reference tables. Comparator is also an active electrical control, not sham.

**Zhang 2025 — window mismatch, not a format problem.**
Source defines "postoperative days (PODs) **0 (day of surgery)**, 1, and 2" and reports total
sufentanil "on POD 1". POD 1 is therefore a separate calendar day that **excludes
day-of-surgery consumption** and extends past 24 h post-incision by an unknown amount.

**Oztas 2019 — confirmed exactly.**
Tramadol (0–24 h) 228.40 ± 87.89 vs 357.81 ± 123.70; pethidine (0–24 h) 20.66 ± 27.89 vs
33.12 ± 42.69. Combining requires within-person covariance, which is unavailable — `SD(total)
= √(SD₁² + SD₂²)` would assume independence and is not defensible. Pethidine was also **IM**,
tramadol **IV**.

**Coura 2011 — additional finding beyond the weight problem.**
"Table 2 Fentanyl dosage during first 24 h after operation", 13.1 ± 2.2 vs 16.3 ± 1.6 µg/kg.
No body weights are reported. Additionally, "supplementary doses of **morphine or fentanyl**
were allowed", so the reported fentanyl is **not complete opioid exposure**.

---

## 5. Defect found in the existing pipeline (not yet fixed)

`00_prep_data.do` assigns `comparator_type` with a **case-sensitive** match on `"Sham"` plus a
`"No-current"` literal. Four rows are consequently misfiled:

| Study | Source comparator text | Currently assigned | Should be |
|---|---|---|---|
| Chen 2015 | "Electrodes/device with no stimulation" | Usual Care / Control | **Sham** |
| Chen 2015 (Hyperalgesia) | "Electrodes/no-current sham" | Usual Care / Control | **Sham** |
| Zhang 2025 | "Sub-sensory sham" | Usual Care / Control | **Sham** |
| Yeh (lumbar-spine family) | "Electrical sham/nonacupoint AES" | Usual Care / Control | **Active electrical** |

**Impact on published results: none** — all four rows have `inc_primary = 0`, so no current
estimate is affected. But this **must** be fixed before any comparator-stratified analysis is
run, or Section 6 stratification will be wrong.

A parallel trap exists in the reverse direction and is now guarded in the audit script: Chen
1998's control is `"Sham ST36 TENS (0 mA)"`. A naive device-name match would file a genuine
**0 mA inert sham** as an *active electrical* comparator. The audit classifier tests inert-sham
markers before device names for exactly this reason.

---

## 6. Proposed analysis architecture

| Analysis | Composition | k | Note |
|---|---|---|---|
| **S0 strict primary — sham-controlled TEAS** | Chen 1998, Chen 2020, He 2026 (JIS), Szmit 2021 | **4** | = the existing "TEAS vs Sham" stratum |
| **S0 supportive — usual-care EA** | El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024 | **3** | = the existing "EA vs Usual Care" stratum |
| **Sham-controlled EA** | — | **0** | requires the explicit statement below |
| **S1** (+ pure Tier B mean/SD) | — | **+0** | no pure Tier B mean/SD case exists; Chen 2015 is Tier B **and** C |
| **S2** (+ Tier C, distribution-compatible) | + Gao 2022, Chen 2015 | +2 | parallel synthesis, **not** median→mean conversion |
| **S3** (+ Tier D digitized) | + Gu 2019 | +1 | only if dual-reviewer digitization succeeds |
| **S4** exploratory | Tier E assumption ranges | — | clearly labelled; never replaces S0 |

Required statement for Section 7:

> Insufficient sham-controlled EA evidence was available for a pooled estimate. The two
> sham-controlled EA candidates (Coura 2011, Sim 2002) report weight-normalized opioid doses
> that cannot be converted to absolute IV MME without individual body weights.

Multi-arm handling (must be preserved):
- **Chen 1998** — 4-arm, 3 contrasts share one sham arm; only the acupoint contrast enters S0.
- **Szmit 2021** — 3-arm; sham contrast enters S0, PCA-only contrast is the correlated
  alternative and must not be counted as a second study.
- **Sim 2002**, **Jin 2023**, **Oztas 2019** — shared control arms; same rule.

---

## 7. Unresolved / requires action

| Item | Action needed |
|---|---|
| Gu 2019 Fig. 4 | Formal dual-reviewer digitization. Values must **not** be visually estimated. |
| Tramadol, pethidine, butorphanol | No sourced parenteral IV MME factor located. Author contact or a citable equianalgesic source required before any of these can enter an MME model. |
| Hou 2023 | Author contact — delivered sufentanil not reported. |
| Jin 2023 | Author contact — PCIA fentanyl concentration not in the main article. |
| Yeh 2010 / 2011 | Cohort-overlap adjudication; also confirm epidural vs IV route before any MME use. |
| Coura 2011 | Dashboard currently shows a reader-facing **70-kg reconstruction**. Must be removed or relabelled "Legacy reconstruction — excluded from current locked analysis." |
| `comparator_type` classifier | Fix case-sensitivity before any comparator-stratified analysis. |

---

## 8. Not done in this pass (deliberately)

Per the staging instruction, the audit was completed and is presented for review **before**
any downstream regeneration. Not yet performed: Stata re-runs, tiered result generation,
forest plots, dashboard updates, Methods/Results/Discussion text. No statistical result has
been changed by this pass.

---

# 9. Stage 2 QC — execution (2026-09-08)

## 9.1 Items from §7 now closed

| Item | Status |
|---|---|
| Gu 2019 Fig. 4 | **Closed — rejected.** Digitized under the pre-specified protocol; axis calibration exact (max residual 0.0000), but validation against the trial's own in-text values failed (control arm overestimated by up to 16.0% while the TEAS arm reproduced to within 4.2%). Not admissible. Values recorded for provenance in `03_DIGITIZATION/gu2019_digitization_QC.md` and used in no analysis. Author contact prepared. |
| Coura 2011 70-kg reconstruction | **Closed.** Relabelled "LEGACY RECONSTRUCTION — excluded from the current locked analysis" on the dashboard, with the 70 kg named as an assumption the trial never reports. Verified that the locked data leaves `mean_i_mme`/`mean_c_mme` empty, so the reconstruction feeds no estimate. Sim 2002 relabelled on the same grounds. |
| `comparator_type` classifier | **Closed.** Rewritten to lower-case before matching, with inert-sham markers tested before device names. |

Still open: sourced IV MME factors for tramadol, pethidine and butorphanol;
author contact for Hou 2023 and Jin 2023; Yeh 2010/2011 cohort-overlap
adjudication and route confirmation.

## 9.2 Verification performed

**Arithmetic reproduction.** Every S0 mean difference and standard error was
recomputed inside Stata from the arm-level MME means, SDs and sample sizes, and
compared to the value carried in the dataset (tolerance 1e-4). All matched.

**Cross-engine agreement.** The v33 dataset was built independently from the
source PDFs, not from the locked `.dta`. Its S0 strata reproduce `OP24_TEAS_SHAM`
(−13.995275, [−34.180843, 6.1902914], p = 0.11447614) and `OP24_EA_CTRL`
(−3.9358339, [−19.773222, 11.901554], p = 0.39689466) to every printed digit.

**Prohibition gates.** The do-file exits non-zero on any of: a correlated
multi-arm alternative contrast entering S0; a missing MD or SE in S0; a row in
zero or both comparator strata; an MD/SE that does not reproduce from arm-level
values. All four passed.

**Pipeline re-run.** The full master pipeline was re-run after the comparator
classifier fix. All 14 steps completed with zero Stata errors (`r(nnn);`) in
every log.

**Validator.** 56 checks, all passing. The six new checks were mutation-tested
individually; each deliberate corruption tripped that check and no other.

## 9.3 Defects found during execution

**D1 — Figures C/D misrepresented the pre-specified intervals.** The first
implementation drew the tier- and comparator-sensitivity panels with
`meta forestplot`, which treats each row as a study and reconstructs its interval
as estimate ± 1.96·SE on a *z* scale. For a k = 4 Hartung–Knapp interval on t(3)
this narrows the interval by roughly a factor of 1.6, and the panel rendered the
non-significant primary result as −14.00 [−26.43, −1.56] with a pooled
"p = 0.02" across three separately fitted models. Both panels are now drawn
directly from the fitted bounds, with no overall diamond and no pooled test.
Caught before commit; no such figure was ever published.

**D2 — The master aggregate had silently drifted.**
`master_reconciled_results_v26.csv` is read by the dashboard but written by no
do-file, and was maintained by hand. Its seven estimator-grid rows were still at
k = 6 after the v32 migration moved the strict primary to k = 7, and its
broader-SMD row was still at k = 10 after the pipeline produced k = 9. Closed by
`scripts/sync_master_results.py`, which regenerates the aggregate from the Stata
tables and fails on drift; it compares numerically at the precision each cell is
displayed at, so human-readable rounding is preserved and only genuine
disagreement is reported.

**D3 — Per-stratum denominators were wrong.** The dashboard quoted TEAS as
N = 342 and EA as N = 334. The analysed arms sum to 337 and 339. Both were wrong
while their total (676) was right, which is exactly why the existing
total-denominator check passed. New check `t_stratum_denominators` closes this.

## 9.4 Statement on significance

Two analyses in this pass cross p = 0.05: the broader scale-free SMD (k = 9,
p = 0.028, I² = 95.0%) and the primary model re-fitted with unadjusted Wald
intervals (p = 0.030). Neither is reported as a headline result and neither
changes the review's conclusion. The Wald result differs from the pre-specified
analysis only in the reference distribution used to build the interval; the SMD
result carries I² ≈ 95% across a set that deliberately mixes absolute-dose and
weight-normalised endpoints. Both are recorded because suppressing a
sensitivity analysis that reaches significance would be as much a distortion as
promoting one.
