// v33 DASHBOARD DATA LAYER — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_v33_dashboard_data.py
//
// Master : TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx
// Studies: 70   Outcome rows: 382
// Strict primary opioid k: 7
//
// Every number is read from the v33 workbook or from a Stata result file.
// None is copied from previous HTML or JS.
window.V33_DATA = {
  "generated_by": "scripts/build_v33_dashboard_data.py",
  "master": "TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx",
  "canonical_studies": 70,
  "outcome_rows": 382,
  "strict_primary_k": 7,
  "contribution_map": {
    "groups": [
      {
        "id": "primary_opioid_24h",
        "label": "Primary 0–24 h opioid",
        "definition": "Contributes an analysable cumulative 0–24 h postoperative opioid dose to the strict primary model.",
        "n_studies": 7
      },
      {
        "id": "other_postop_opioid",
        "label": "Other postoperative opioid",
        "definition": "Reports postoperative opioid consumption at another window, in another unit, or in a form that cannot enter the strict model.",
        "n_studies": 30
      },
      {
        "id": "intraoperative_opioid",
        "label": "Intraoperative opioid",
        "definition": "Reports intraoperative opioid requirement. A different estimand from postoperative consumption; never pooled with it.",
        "n_studies": 18
      },
      {
        "id": "rescue_opioid",
        "label": "Rescue analgesia / opioid",
        "definition": "Reports rescue opioid use, rescue administration counts, or time to first rescue.",
        "n_studies": 11
      },
      {
        "id": "opioid_demand",
        "label": "PCA demand / presses",
        "definition": "Reports PCA attempts, presses or deliveries. A behavioural proxy, not a drug quantity.",
        "n_studies": 13
      },
      {
        "id": "pain",
        "label": "Pain",
        "definition": "Reports a postoperative pain score.",
        "n_studies": 28
      },
      {
        "id": "ponv",
        "label": "PONV / nausea / vomiting",
        "definition": "Reports postoperative nausea or vomiting.",
        "n_studies": 26
      },
      {
        "id": "qor",
        "label": "Quality of recovery",
        "definition": "Reports QoR-40 or QoR-15.",
        "n_studies": 5
      },
      {
        "id": "gi_recovery",
        "label": "GI recovery",
        "definition": "Reports flatus, defecation, bowel sounds, diet or ileus.",
        "n_studies": 14
      },
      {
        "id": "los_recovery",
        "label": "LOS / recovery",
        "definition": "Reports length of stay or another recovery endpoint.",
        "n_studies": 5
      },
      {
        "id": "other_narrative",
        "label": "Other / narrative only",
        "definition": "Carries outcome information that no current pooled model uses.",
        "n_studies": 8
      }
    ],
    "per_study": [
      {
        "study": "An 2014",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Ao 2021",
        "families": [
          "opioid_demand",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Chen 1998",
        "families": [
          "other_postop_opioid",
          "primary_opioid_24h"
        ],
        "n_families": 2,
        "in_primary": true
      },
      {
        "study": "Chen 2015",
        "families": [
          "other_postop_opioid",
          "ponv",
          "qor"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Chen 2015 (Hyperalgesia)",
        "families": [
          "opioid_demand",
          "other_postop_opioid",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Chen 2020",
        "families": [
          "other_postop_opioid",
          "pain",
          "primary_opioid_24h"
        ],
        "n_families": 3,
        "in_primary": true
      },
      {
        "study": "Coura 2011",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "El-Rakshy 2009",
        "families": [
          "other_postop_opioid",
          "primary_opioid_24h"
        ],
        "n_families": 2,
        "in_primary": true
      },
      {
        "study": "Gao 2021",
        "families": [
          "gi_recovery"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Gao 2022",
        "families": [
          "intraoperative_opioid",
          "other_postop_opioid",
          "pain",
          "ponv"
        ],
        "n_families": 4,
        "in_primary": false
      },
      {
        "study": "Grech 2016",
        "families": [
          "other_narrative"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Gu 2019",
        "families": [
          "gi_recovery",
          "other_postop_opioid",
          "pain"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Guo 2023",
        "families": [
          "intraoperative_opioid",
          "other_narrative"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "He 2026 (breast/WJCO)",
        "families": [
          "pain"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "He 2026 (hepatectomy/JIS)",
        "families": [
          "opioid_demand",
          "other_postop_opioid",
          "ponv",
          "primary_opioid_24h"
        ],
        "n_families": 4,
        "in_primary": true
      },
      {
        "study": "Hou 2023",
        "families": [
          "pain",
          "ponv",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Huang 2017",
        "families": [
          "intraoperative_opioid",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Huang 2024",
        "families": [
          "opioid_demand",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Huang 2025",
        "families": [
          "gi_recovery"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Jiang 2026",
        "families": [
          "gi_recovery",
          "intraoperative_opioid",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Jin 2023",
        "families": [
          "opioid_demand",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Lee 2011",
        "families": [
          "other_postop_opioid",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Li 2021",
        "families": [
          "gi_recovery",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Li 2022",
        "families": [
          "pain"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Liang 2021",
        "families": [
          "other_narrative",
          "qor",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Lin 2002",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Liu 2015",
        "families": [
          "intraoperative_opioid",
          "los_recovery",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Liu 2021",
        "families": [
          "opioid_demand",
          "other_narrative",
          "pain"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Liu 2025",
        "families": [
          "other_narrative"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Liu 2026 (ESD)",
        "families": [
          "pain",
          "ponv",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Liu 2026 (burn)",
        "families": [
          "intraoperative_opioid",
          "ponv",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Long 2025",
        "families": [
          "opioid_demand",
          "other_narrative",
          "pain",
          "ponv"
        ],
        "n_families": 4,
        "in_primary": false
      },
      {
        "study": "Lu 2021",
        "families": [
          "intraoperative_opioid",
          "pain",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Lu 2022",
        "families": [
          "gi_recovery",
          "los_recovery",
          "opioid_demand"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Luo 2026",
        "families": [
          "other_postop_opioid",
          "pain",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Ma 2026",
        "families": [
          "ponv"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Ng 2013",
        "families": [
          "gi_recovery",
          "opioid_demand",
          "pain"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Ntritsou 2014",
        "families": [
          "intraoperative_opioid",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Oztas 2019",
        "families": [
          "other_postop_opioid",
          "pain",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Pan 2023",
        "families": [
          "gi_recovery",
          "intraoperative_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Seevaunnamtum 2016",
        "families": [
          "other_postop_opioid",
          "primary_opioid_24h"
        ],
        "n_families": 2,
        "in_primary": true
      },
      {
        "study": "Sim 2002",
        "families": [
          "intraoperative_opioid",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Song 2020",
        "families": [
          "intraoperative_opioid",
          "opioid_demand",
          "other_narrative",
          "other_postop_opioid",
          "pain",
          "ponv"
        ],
        "n_families": 6,
        "in_primary": false
      },
      {
        "study": "Sun 2017",
        "families": [
          "pain"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Szmit 2021",
        "families": [
          "other_postop_opioid",
          "pain",
          "ponv",
          "primary_opioid_24h"
        ],
        "n_families": 4,
        "in_primary": true
      },
      {
        "study": "Tu 2024",
        "families": [
          "pain",
          "ponv",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Wang 2023",
        "families": [
          "gi_recovery",
          "rescue_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Wang 2024",
        "families": [
          "intraoperative_opioid",
          "ponv"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Wong 2006",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Wu 2016",
        "families": [
          "los_recovery",
          "ponv"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Wu 2022",
        "families": [
          "intraoperative_opioid",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Wu 2025",
        "families": [
          "intraoperative_opioid",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Xie 2014",
        "families": [
          "opioid_demand",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Xing 2022",
        "families": [
          "gi_recovery",
          "intraoperative_opioid",
          "opioid_demand",
          "pain",
          "ponv"
        ],
        "n_families": 5,
        "in_primary": false
      },
      {
        "study": "Xiong 2021",
        "families": [
          "other_postop_opioid",
          "ponv"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Yang 2020",
        "families": [
          "gi_recovery"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Yang 2024",
        "families": [
          "gi_recovery",
          "other_postop_opioid",
          "ponv",
          "primary_opioid_24h"
        ],
        "n_families": 4,
        "in_primary": true
      },
      {
        "study": "Yao 2015",
        "families": [
          "ponv",
          "qor",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Yeh 2010",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Yeh 2011",
        "families": [
          "other_postop_opioid"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Yu 2020",
        "families": [
          "pain",
          "qor",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Zhan 2020",
        "families": [
          "other_narrative"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Zhang 2014",
        "families": [
          "intraoperative_opioid",
          "los_recovery",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Zhang 2018",
        "families": [
          "gi_recovery"
        ],
        "n_families": 1,
        "in_primary": false
      },
      {
        "study": "Zhang 2023",
        "families": [
          "los_recovery",
          "other_postop_opioid"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Zhang 2025",
        "families": [
          "other_postop_opioid",
          "pain",
          "rescue_opioid"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Zheng 2025",
        "families": [
          "intraoperative_opioid",
          "opioid_demand",
          "ponv"
        ],
        "n_families": 3,
        "in_primary": false
      },
      {
        "study": "Zhou 2021",
        "families": [
          "other_postop_opioid",
          "pain"
        ],
        "n_families": 2,
        "in_primary": false
      },
      {
        "study": "Zhou 2025",
        "families": [
          "gi_recovery",
          "pain",
          "ponv",
          "qor",
          "rescue_opioid"
        ],
        "n_families": 5,
        "in_primary": false
      },
      {
        "study": "Zhu 2022",
        "families": [
          "intraoperative_opioid",
          "ponv"
        ],
        "n_families": 2,
        "in_primary": false
      }
    ],
    "studies_with_no_family": [],
    "graph_only_or_unreported": [
      "Grech 2016",
      "Zhan 2020"
    ],
    "note": "A study may contribute to several outcome families. Being included in the review is not the same as contributing to the primary meta-analysis: most included trials report no analysable cumulative 0–24 h opioid dose."
  },
  "primary": {
    "OP24_PRIM_COMB": {
      "analysis_id": "OP24_PRIM_COMB",
      "k": 7.0,
      "estimate": -9.9070034,
      "ci_low": -20.079363,
      "ci_high": 0.2653563,
      "p_value": 0.054538377,
      "tau2": 113.91055,
      "i2": 98.569153
    },
    "OP24_TEAS_SHAM": {
      "analysis_id": "OP24_TEAS_SHAM",
      "k": 4.0,
      "estimate": -13.995275,
      "ci_low": -34.180843,
      "ci_high": 6.1902914,
      "p_value": 0.11447614,
      "tau2": 156.88229,
      "i2": 98.590675
    },
    "OP24_EA_CTRL": {
      "analysis_id": "OP24_EA_CTRL",
      "k": 3.0,
      "estimate": -3.9358339,
      "ci_low": -19.773222,
      "ci_high": 11.901554,
      "p_value": 0.39689466,
      "tau2": 28.471277,
      "i2": 77.152611
    },
    "OP24_LOWROB_ONLY": {
      "analysis_id": "OP24_LOWROB_ONLY",
      "k": 6.0,
      "estimate": -11.272961,
      "ci_low": -23.181637,
      "ci_high": 0.63571644,
      "p_value": 0.059135512,
      "tau2": 123.59916,
      "i2": 98.866768
    },
    "OP24_PRIM_SMD": {
      "analysis_id": "OP24_PRIM_SMD",
      "k": 7.0,
      "estimate": -0.96674985,
      "ci_low": -2.0861762,
      "ci_high": 0.15267643,
      "p_value": 0.079024479,
      "tau2": 1.3659765,
      "i2": 96.496735
    }
  },
  "secondary": [
    {
      "analysis_id": "V33_RESCUE_OPIOID_RR_24H",
      "outcome": "Binary rescue opioid use, 0-24 h/POD1",
      "measure": "Risk ratio",
      "model": "REML + Hartung-Knapp",
      "k": 3.0,
      "estimate": 0.5188122902699271,
      "ci_low": 0.3703789571689463,
      "ci_high": 0.7267318710343158,
      "p_value": 0.0139500213975341,
      "tau2": 1.61398288492e-07,
      "i2": 6.32295635288e-05
    },
    {
      "analysis_id": "V33_INTRAOP_REMI_MD",
      "outcome": "Intraoperative remifentanil",
      "measure": "MD (ug)",
      "model": "REML + Hartung-Knapp",
      "k": 9.0,
      "estimate": -104.4153488345436,
      "ci_low": -158.5477302258938,
      "ci_high": -50.28296744319328,
      "p_value": 0.0021449228538168,
      "tau2": 2061.423450304245,
      "i2": 52.6029518747458
    },
    {
      "analysis_id": "V33_INTRAOP_REMI_SMD",
      "outcome": "Intraoperative remifentanil",
      "measure": "Hedges g",
      "model": "REML + Hartung-Knapp",
      "k": 9.0,
      "estimate": -0.4856536657820866,
      "ci_low": -0.8355517036100668,
      "ci_high": -0.1357556279541064,
      "p_value": 0.0125990505939633,
      "tau2": 0.1489417961823781,
      "i2": 81.58561726334138
    },
    {
      "analysis_id": "V33_INTRAOP_SUF_MD",
      "outcome": "Intraoperative sufentanil",
      "measure": "MD (ug)",
      "model": "REML + Hartung-Knapp",
      "k": 6.0,
      "estimate": -0.1139999801003263,
      "ci_low": -1.935307606873889,
      "ci_high": 1.707307646673237,
      "p_value": 0.8784720332157816,
      "tau2": 0.2737063886365303,
      "i2": 26.7547036294689
    },
    {
      "analysis_id": "V33_QOR40_24H_MD",
      "outcome": "Global QoR-40 at ~24 h",
      "measure": "MD (points)",
      "model": "REML + Hartung-Knapp",
      "k": 3.0,
      "estimate": 7.340984043233228,
      "ci_low": -4.601338739466667,
      "ci_high": 19.2833068259331,
      "p_value": 0.1181493599900199,
      "tau2": 19.67163008856182,
      "i2": 82.49676329864293
    },
    {
      "analysis_id": "V33_GI_DEFECATION_MD",
      "outcome": "Time to first defecation",
      "measure": "MD (hours)",
      "model": "REML + Hartung-Knapp",
      "k": 8.0,
      "estimate": -10.31466296322132,
      "ci_low": -18.45448754652791,
      "ci_high": -2.174838379914727,
      "p_value": 0.0200434952860491,
      "tau2": 54.07790488315739,
      "i2": 88.6064989733423
    }
  ],
  "not_pooled": [
    {
      "study": "Yao 2015",
      "outcome": "Cumulative rescue administrations",
      "window": "0-24 h",
      "stat": "Median (IQR) 1 (1-3) vs 3.5 (2-7.8), P=0.004",
      "reason": "Rescue COUNT, not dose. Multiplying a median count by 0.05 ug/kg and a mean body weight would not recover any individual-level quantity."
    },
    {
      "study": "Chen 2015 (Hyperalgesia)",
      "outcome": "Rescue sufentanil PCIA boluses",
      "window": "0-24 h",
      "stat": "Median (IQR) 3 (2-4) vs 7 (6-8)",
      "reason": "Rescue COUNT in boluses; weight-normalised per-bolus dosing not reconstructable. Different unit from Yao 2015, so the two counts are not pooled with each other either."
    },
    {
      "study": "Yao 2015",
      "outcome": "Time to first rescue analgesia",
      "window": "0-24 h",
      "stat": "Median 59 (31-1440) vs 47 (13-196) min, P=0.039",
      "reason": "k=1; dispersion is a reported range and the upper bound is the 24-h censoring point. Narrative only."
    },
    {
      "study": "Liang 2021",
      "outcome": "Postoperative analgesia requirement",
      "window": "unclear",
      "stat": "3.8 (1.9) vs 5.0 (2.9), P=0.045",
      "reason": "HOLD. Source calls it a count of patients, which 3.8/35 cannot be. Metric, unit and window all undefined."
    },
    {
      "study": "Yu 2020",
      "outcome": "Resting pain VAS",
      "window": "POD1 and POD2",
      "stat": "POD1 3.70 vs 4.73; POD2 1.83 vs 2.30",
      "reason": "CONFLICTED. Table 2 and abstract disagree on the TEAS SDs (1.53/0.98 vs 1.41/0.88) and on the POD2 P value (table stars P<0.05, Results text says P=0.26)."
    },
    {
      "study": "Zhou 2021",
      "outcome": "Any postoperative opioid use",
      "window": "undefined",
      "stat": "18/41 vs 30/40",
      "reason": "Postoperative window not defined in the source, so it cannot join the 0-24 h binary rescue model."
    },
    {
      "study": "Liu 2026 (ESD)",
      "outcome": "Any rescue IV morphine use",
      "window": "through 48 h",
      "stat": "19/58 vs 40/62",
      "reason": "48-h window; kept out of the 0-24 h binary rescue model."
    },
    {
      "study": "Hou 2023",
      "outcome": "Any rescue flurbiprofen use",
      "window": "postoperative",
      "stat": "15/36 vs 28/36",
      "reason": "Flurbiprofen is an NSAID, not an opioid. Not pooled with opioid rescue."
    },
    {
      "study": "Oztas 2019",
      "outcome": "Rescue pethidine / dexketoprofen",
      "window": "0-24 h",
      "stat": "mean/SD reported",
      "reason": "No sourced IV MME factor for pethidine; dexketoprofen is an NSAID."
    },
    {
      "study": "Zhu 2022",
      "outcome": "Intraoperative sufentanil and remifentanil",
      "window": "intraoperative",
      "stat": "4-group omnibus P only (0.892 / 0.948)",
      "reason": "Two of three active contrasts are dropped from each model so the shared usual-care arm (n=101) is not counted more than once."
    },
    {
      "study": "Lu 2021",
      "outcome": "Total remifentanil",
      "window": "intraoperative",
      "stat": "two active arms vs one sham arm",
      "reason": "Multi-arm; only the combined PC6+CV17 contrast enters the model."
    }
  ],
  "caveats": [
    {
      "analysis_id": "V33_RESCUE_OPIOID_RR_24H",
      "level": "high",
      "text": "Fragile. Yu 2020 carries 80.8% of the weight in this k=3 model, and it is the trial this analysis was newly built around. Leave-one-out: omitting Tu 2024 gives RR 0.520 (0.119–2.268, p=0.112) and omitting Yu 2020 gives RR 0.433 (0.063–2.995, p=0.114) — the result does not survive either. I²=0% reflects three similar point estimates, not a well-estimated between-study variance. Hypothesis-generating only."
    },
    {
      "analysis_id": "V33_GI_DEFECATION_MD",
      "level": "moderate",
      "text": "Robust to the new data but severely heterogeneous (I²=88.6%). Excluding the newly added Yang 2020 contrast gives −11.95 h (−21.52 to −2.38, p=0.022, k=7): the effect was already present and the addition did not create it."
    },
    {
      "analysis_id": "V33_INTRAOP_REMI_MD",
      "level": "moderate",
      "text": "Intraoperative requirement is a different estimand from postoperative consumption and says nothing about opioid sparing after surgery. Doses are titrated intraoperatively by the anaesthetist, so this outcome is vulnerable to performance bias wherever blinding was imperfect."
    },
    {
      "analysis_id": "V33_QOR40_24H_MD",
      "level": "moderate",
      "text": "k=3 with I²=82.5%. The three trials span a 9-point range of effect (+2.6 to +11.7 QoR-40 points) and the interval crosses zero."
    }
  ]
};
