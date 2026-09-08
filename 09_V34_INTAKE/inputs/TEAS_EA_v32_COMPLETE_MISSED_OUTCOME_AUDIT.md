# TEAS/EA v32 --- Complete Missed-Outcome Audit

**Project:** Perioperative TEAS / Electroacupuncture Systematic Review\
**Base master:**
`TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx`\
**Canonical studies:** 70 RCTs\
**Purpose:** Source-grounded handoff of outcomes identified as missing
or under-extracted from v32, for reconciliation into v33 and subsequent
analysis.

> This is an additive audit layer, not a replacement for v32. Do not
> overwrite existing source-verified values without adjudication.

## 1. Executive conclusion

The audit does not support removing RCTs simply because they do not
enter the strict primary meta-analysis. Instead, v32 is selective rather
than exhaustive at outcome level for several studies. The audit
identified 19 studies with high-confidence missing or under-extracted
outcome families/timepoints.

The strict primary outcome remains cumulative systemic postoperative
opioid consumption from end of surgery through 24 h. Binary rescue use,
rescue counts, intraoperative opioids, PCA demand, 48-h totals,
ambiguous analgesic requirements and graph-only outcomes are distinct
outcomes and must not be promoted automatically into the primary
analysis.

## 2. Non-negotiable rules

-   Do not manufacture MME from PCA reservoir contents.
-   Do not convert rescue-opioid incidence into dose.
-   Do not multiply median rescue counts by mean weight to manufacture
    mean opioid consumption.
-   Preserve median/IQR unless a prespecified conversion is justified.
-   Graph-only data remain graph-only until formal digitization.
-   POD1 is not automatically exact 0--24 h.
-   Intraoperative and postoperative opioid consumption remain separate.
-   PCA presses/demands are not drug mass.
-   Multi-arm trials require shared-control handling.
-   Newly analyzed outcomes require result-specific RoB 2 or an explicit
    pending flag.
-   Null/nonsignificant results remain valid evidence.
-   Deduplicate using study + outcome + timepoint + intervention +
    comparator.

# 3. Source-verified additions

## Yu 2020

### Rescue sufentanil use, 0--24 h

-   TEAS: **13/30 (43.3%)**
-   Control: **24/30 (80.0%)**
-   P \< 0.01
-   **Ready as binary rescue-opioid endpoint (RR).**
-   Do not convert to MME.

### Resting pain

-   POD1: **3.70 vs 4.73**
-   POD2: **1.83 vs 2.30**
-   Variance/source-table details require verification before pooling.
-   Preserve the identified POD2 source discrepancy until adjudicated.

Other reported domains: QoR-40, PONV, rescue antiemetic use, MMSE.

## Yao 2015

### Cumulative rescue sufentanil administrations, 0--24 h

-   TEAS: **median 1 (IQR 1--3)**
-   Control: **median 3.5 (IQR 2--7.8)**
-   P = **0.004**
-   Rescue regimen: IV sufentanil **0.05 μg/kg per administration**.
-   Use as rescue-opioid frequency evidence.
-   Do not manufacture mean MME from median counts × mean weight.

### Time to first rescue

-   TEAS: **59 min (31--1440)**
-   Control: **47 min (13--196)**
-   P = **0.039**

### QoR-40, 24 h

-   TEAS: **176.5 ± 10.2**
-   Control: **164.8 ± 14.7**

### Nausea, 0--24 h

-   TEAS: **17/35**
-   Control: **26/36**

Also reports postoperative pain at 0.5, 1, 2, 4, 8 and 24 h.

## Zhu 2022

Multi-arm RCT; verify arm N and handle shared control correctly.

### Intraoperative sufentanil

  Arm                      Mean ± SD
  ------------- --------------------
  Pre-EA          **38.1 ± 4.97 μg**
  30-min EA       **39.1 ± 4.83 μg**
  Combined EA     **39.0 ± 5.12 μg**
  Usual care      **37.8 ± 4.87 μg**

### Intraoperative remifentanil

  Arm                      Mean ± SD
  ------------- --------------------
  Pre-EA          **0.58 ± 0.23 mg**
  30-min EA       **0.58 ± 0.23 mg**
  Combined EA     **0.50 ± 0.25 mg**
  Usual care      **0.57 ± 0.26 mg**

Additional outcomes needing complete source transcription/checking: -
24-h movement pain - early postoperative pain - QoR-15 - rescue
analgesic use - rescue antiemetic use - first flatus - PONV

## Pan 2023

### Intraoperative remifentanil

-   TEAS: **740.1 ± 276.9 μg**
-   Control: **854.0 ± 287.5 μg**
-   P = **0.04**
-   Verify analysis N before pooling.
-   Preserve RoB implications of post-randomization exclusions.

Additional reported outcomes: - 24-h movement pain - QoR-40 -
postoperative analgesic use - vomiting - GI recovery - LOS -
PACU/recovery measures

## Liang 2021

### QoR-40

24 h: - TEAS **191.7 ± 4.4** - Control **189.1 ± 4.3** - P = **0.007**

48 h: - TEAS **195.3 ± 1.9** - Control **193.3 ± 3.0** - P \< **0.001**

### Postoperative analgesia requirement

-   TEAS **3.8 (1.9)**
-   Control **5.0 (2.9)**
-   P = **0.045**

**HOLD:** exact metric/unit/window is insufficiently clear. Do not
interpret as morphine mg or MME.

Other reported domains: pain, PONV, CRBD, MMSE/cognitive recovery.

## Yang 2020

### First defecation

-   EA **53.9 ± 6.0 h**
-   Usual care **57.5 ± 7.2 h**
-   P = **0.046**

### First flatus

-   EA **20.8 ± 4.6 h**
-   Usual care **24.1 ± 6.2 h**
-   P = **0.026**

Other reported domains: pain, PONV, out-of-bed activity, hospital stay.

Morphine PCA was used, but actual delivered morphine is not adequately
reported. Do not derive consumption from reservoir/programming.

## Huang 2025

### First flatus

-   EA **36.4 ± 8.0 h**
-   Control **42.2 ± 8.5 h**

### First defecation

-   EA **46.0 ± 8.0 h**
-   Control **51.3 ± 9.4 h**

Other reported domains: - pain VAS - additional analgesic use -
vomiting - QoR-40 - LOS - bowel obstruction - adverse events

Rescue analgesia was ketorolac 30 mg IM. This is not opioid consumption.

## Gao 2021

Large multicenter sham-controlled RCT: - randomized **610** - TEAS
**303** - sham **307**

### Postoperative paralytic ileus

-   TEAS **98/303 (32.3%)**
-   Sham **126/307 (41.0%)**

### First flatus

-   TEAS **63.4 ± 29.0 h**
-   Sham **76.3 ± 37.9 h**

### First defecation

-   TEAS **106.7 ± 65.6 h**
-   Sham **121.5 ± 65.6 h**

Other reported domains: - abdominal pain/distension - nausea -
vomiting - return to normal diet - bowel-sound recovery

Do not infer opioid dose from categorical postoperative analgesia use.

# 4. Additional high-confidence under-extracted studies

## Lu 2022

Source-extract before analysis: - rest pain 24/48/72 h - cough/movement
pain 24/48/72 h - PONV - QoR-15 24/48/72 h

## Li 2021

Under-extracted: - PONV at multiple postoperative timepoints -
additional pain timepoints - hospital LOS - GI/recovery outcomes where
absent

Verified examples: - VAS ≥4 at 6 h: approximately **21.4% vs 35.7%** -
PONV event counts include 6 h **51/140 vs 100/140** and 12 h **54/140 vs
81/140**

Preserve repeated timepoints; do not treat them as independent studies.

## Gu 2019

Under-extracted: - continuous pain at 4, 8, 16, 24, 36 h - PONV 0--24
h - GI recovery

Verified examples: - 24-h VAS **1.98 ± 0.39 vs 2.72 ± 0.73** - PONV
approximately **12% vs 32.2%**

Verify exact arm N/source definition before analysis.

## Jiang 2026

Under-extracted: - first defecation - abdominal distension -
postoperative LOS - additional postoperative pain where reported

## Wang 2023

Under-extracted: - rest pain 24/48/72 h - activity pain 48/72 h -
postoperative events - hospital stay

## Tu 2024

Under-extracted: - nausea severity 0--2 h - 2--6 h - 6--24 h - rescue
metoclopramide by interval

## Sun 2017

Under-extracted: - additional pain timepoints including 1/6/48 h where
reported - PONV components - recovery times

## Sim 2002

Under-extracted: - rest pain 6/12/18/24 h - 24-h mean pain - PONV -
opioid-related adverse effects

## Lu 2021

Under-extracted: - pain at rest/cough - rescue analgesia -
nausea/vomiting/severity components - recovery times

## Long 2025

Under-extracted: - hospital LOS - additional VAS timepoints - additional
PCIA timepoints

Do not equate PCIA metrics automatically with opioid mass.

## Wang 2024

Under-extracted: - interval-specific vomiting where separately reported,
especially severe-history stratum - avoid duplicating events already
represented in PONV composites.

## Zheng 2025

Under-extracted: - 24-h resting pain NRS

# 5. Analysis implications

## Primary opioid outcome

This audit does **not** automatically add studies to the strict 0--24 h
cumulative postoperative opioid model.

Do not promote: - Yu binary rescue use - Yao rescue counts - Yao time to
first rescue - Zhu/Pan intraoperative opioids - Liang ambiguous
analgesia requirement - PCA demand - PCA reservoir content - 48-h opioid
totals - graph-only values without formal digitization

The primary k changes only if another trial supplies an exact compatible
cumulative 0--24 h systemic opioid dose with usable variance.

## Secondary opioid/analgesic architecture

Keep conceptually separate: 1. postoperative opioid dose at other
windows 2. intraoperative opioid requirement 3. binary rescue opioid use
4. rescue opioid frequency 5. time to first rescue analgesia 6. PCA
demand/deliveries 7. non-opioid rescue analgesia

## Pain

Consider rest vs movement/cough and clinically coherent time windows.
Repeated timepoints from one study must not be treated as independent
trials.

## PONV

Keep distinct where possible: - composite PONV - nausea - vomiting -
rescue antiemetic use

Avoid double-counting composite PONV and components in one pooled
estimate.

## Quality of recovery

QoR-15 and QoR-40 should not be pooled as raw MD. Use
instrument-specific analyses or SMD only if clinically justified.

## GI recovery

Keep distinct: - first flatus - first defecation - postoperative ileus -
bowel-sound recovery - normal diet - abdominal distension

Binary POI must not be pooled with continuous time-to-flatus/defecation.

## Length of stay

Pool only compatible units/definitions/statistic types. Do not silently
treat medians as means.

# 6. Eligibility conclusion

The audit supports retaining the **70-RCT evidence base** unless a
separate protocol-based eligibility adjudication establishes a genuine
exclusion.

The correct interpretation is:

> The review contains 70 eligible RCTs spanning a broad perioperative
> evidence base, while the strict primary estimand---cumulative systemic
> opioid consumption during the first 24 postoperative hours---is
> available in a much smaller subset. Several secondary analgesic and
> recovery outcomes were under-extracted in v32 and should be
> incorporated into v33.

# 7. Recommended v33 workflow

1.  Preserve v32 unchanged.
2.  Create `TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx`.
3.  Reconcile every supplementary row against v32.
4.  Classify each as ADDED / ALREADY PRESENT / UPDATED / HELD / SOURCE
    VERIFICATION NEEDED / NOT ANALYSIS ELIGIBLE.
5.  Record PDF, page, table/figure, arm N, statistic type, timepoint and
    analysis population.
6.  Regenerate all analysis-readiness and Set/Stata/AF sheets.
7.  Rerun analyses from scratch.
8.  Verify results in Stata.
9.  Update result-specific RoB 2 for newly analyzed results.
10. Rebuild dashboard from generated results.
11. Maintain a complete v32→v33 change log.

# 8. Priority queue

### Priority 1 --- opioid-related

1.  Yu 2020 --- binary 24-h rescue sufentanil
2.  Yao 2015 --- 24-h rescue sufentanil frequency
3.  Yao 2015 --- time to first rescue
4.  Pan 2023 --- intraoperative remifentanil
5.  Zhu 2022 --- intraoperative sufentanil/remifentanil

### Priority 1 --- recovery

6.  Liang 2021 --- QoR-40 at 24/48 h
7.  Gao 2021 --- POI/flatus/defecation
8.  Huang 2025 --- flatus/defecation
9.  Yang 2020 --- defecation

### Priority 2

10. Complete pain extraction
11. Complete PONV/nausea/vomiting extraction
12. Complete QoR extraction
13. Complete LOS extraction
14. Complete rescue analgesia/antiemetic extraction

# 9. Files to use with this handoff

Use together: -
`TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx` -
`TEAS_EA_v32_SUPPLEMENTARY_MISSED_OUTCOMES_FOR_CLAUDE_CODE.xlsx` -
`TEAS_EA_v32_missed_outcomes_audit.xlsx`

The structured Excel supplement is the additive data layer; this
Markdown is the complete interpretation, QC and analysis handoff.
