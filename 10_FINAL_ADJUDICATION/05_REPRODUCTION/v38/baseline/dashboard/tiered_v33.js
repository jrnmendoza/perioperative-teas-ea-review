// v33 TIERED PRIMARY-OUTCOME DERIVABILITY — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_tiered_v33.py
//
// Every count, study name, effect estimate and interval below is read from the
// v33 data and Stata result files; none is typed here. The tier definitions are
// the classification rule, not data, and are stated in the generator.
//
// Data     : 07_TIERED_V33/01_DATA + 05_RESULTS (StataNow 19.5)
// Audit    : 07_TIERED_V33/PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.xlsx (93 rows)
// Estimator: Random-effects REML + Hartung–Knapp (t reference distribution)
window.TIERED_V33 = {
  "generated_by": "scripts/build_tiered_v33.py",
  "data_source": "07_TIERED_V33/01_DATA + 05_RESULTS (StataNow 19.5)",
  "audit_rows": 93,
  "audit_file": "07_TIERED_V33/PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.xlsx",
  "outcome": "Cumulative postoperative opioid consumption",
  "window": "0–24 h",
  "unit": "mg intravenous morphine milligram equivalents (IV MME)",
  "estimator": "Random-effects REML",
  "ci_method": "Hartung–Knapp (t reference distribution)",
  "tier_definitions": [
    {
      "tier": "A",
      "label": "Directly compatible",
      "rule": "Exact 0–24 h cumulative postoperative opioid, reported as mean and SD, in an absolute dose unit with a sourced MME conversion factor."
    },
    {
      "tier": "B",
      "label": "Deterministically derived",
      "rule": "Recoverable by an exact arithmetic identity from reported quantities, with no distributional assumption."
    },
    {
      "tier": "C",
      "label": "Alternative distributional form",
      "rule": "Exactly the right estimand, but reported as a median and IQR. Reported as a parallel synthesis; never converted to mean/SD for pooling."
    },
    {
      "tier": "D",
      "label": "Recoverable only by digitization",
      "rule": "Present only in a figure. Admissible only if a pre-specified digitization passes validation against values stated in the text."
    },
    {
      "tier": "E",
      "label": "Requires a prohibited assumption for absolute dose",
      "rule": "Would need an assumed body weight, an assumed solution concentration, PCA presses treated as delivered doses, POD1 treated as 0–24 h, or an invented covariance to reach an absolute IV MME value — not admissible for the absolute-MME estimand at any tier. A subset with a native mean/SD (no such assumption needed for the WITHIN-STUDY standardized effect) is admissible on a separate, scale-free SMD (Hedges' g) exploratory synthesis instead — see the Tier E panel below. This is a different, weaker claim than the primary."
    }
  ],
  "strata": {
    "teas_sham": [
      {
        "study": "Chen 1998",
        "year": 1998,
        "modality": "TEAS",
        "comparator": "Sham",
        "n_i": 25,
        "n_c": 25,
        "unit_src": "mg hydromorphone",
        "mme_factor": 5.0,
        "md_mme": -21.0,
        "se_mme": 6.103,
        "multiarm_note": "4-arm; acupoint contrast only; shares one sham arm with the dermatomal and non-acupoint contrasts",
        "source_locator": "covidence_969_chen_1998.pdf; v32 Opioid_24h_Candidates"
      },
      {
        "study": "Chen 2020",
        "year": 2020,
        "modality": "TEAS",
        "comparator": "Sham",
        "n_i": 40,
        "n_c": 40,
        "unit_src": "ug sufentanil",
        "mme_factor": 1.0,
        "md_mme": -28.19,
        "se_mme": 1.781,
        "multiarm_note": "",
        "source_locator": "Thoracic Cancer 2020 Chen; v32 Opioid_24h_Candidates"
      },
      {
        "study": "He 2026 (hepatectomy/JIS)",
        "year": 2026,
        "modality": "TEAS",
        "comparator": "Sham",
        "n_i": 80,
        "n_c": 79,
        "unit_src": "mg MME",
        "mme_factor": 1.0,
        "md_mme": -0.6,
        "se_mme": 0.578,
        "multiarm_note": "",
        "source_locator": "J Invest Surg 2026 eTable 1 (reports MME directly)"
      },
      {
        "study": "Szmit 2021",
        "year": 2021,
        "modality": "TEAS",
        "comparator": "Sham",
        "n_i": 24,
        "n_c": 24,
        "unit_src": "mg IV morphine",
        "mme_factor": 1.0,
        "md_mme": -7.7,
        "se_mme": 1.491,
        "multiarm_note": "3-arm; sham contrast used; PCA-only arm is the correlated alternative",
        "source_locator": "pdf-3.pdf (J Clin Med 2021;10:146)"
      }
    ],
    "ea_usual": [
      {
        "study": "El-Rakshy 2009",
        "year": 2009,
        "modality": "EA",
        "comparator": "Usual Care",
        "n_i": 42,
        "n_c": 53,
        "unit_src": "mg IV morphine",
        "mme_factor": 1.0,
        "md_mme": -1.6,
        "se_mme": 3.719,
        "multiarm_note": "",
        "source_locator": "Acupunct Med 2009; Table 2 (n=42/53)"
      },
      {
        "study": "Seevaunnamtum 2016",
        "year": 2016,
        "modality": "EA",
        "comparator": "Usual Care",
        "n_i": 32,
        "n_c": 32,
        "unit_src": "mg morphine",
        "mme_factor": 1.0,
        "md_mme": -12.56,
        "se_mme": 4.389,
        "multiarm_note": "",
        "source_locator": "Anesth Pain Med 2016;6(6):e40106"
      },
      {
        "study": "Yang 2024",
        "year": 2024,
        "modality": "EA",
        "comparator": "Usual Care",
        "n_i": 90,
        "n_c": 90,
        "unit_src": "mg morphine",
        "mme_factor": 1.0,
        "md_mme": -0.3,
        "se_mme": 0.716,
        "multiarm_note": "",
        "source_locator": "Explore (NY) 2024;20(3):450-455"
      }
    ],
    "multiarm_alternatives": [
      {
        "study": "Szmit 2021 (PCA-only arm)",
        "year": 2021,
        "modality": "TEAS",
        "comparator": "Usual Care",
        "n_i": 24,
        "n_c": 23,
        "unit_src": "mg IV morphine",
        "mme_factor": 1.0,
        "md_mme": -8.0,
        "se_mme": 1.49,
        "multiarm_note": "correlated with SZMIT21_TEAS_vs_SHAM_MORPH24 - never pool both",
        "source_locator": "pdf-3.pdf (J Clin Med 2021;10:146)"
      }
    ],
    "ea_sham_k": 0
  },
  "parallel_synthesis": [
    {
      "study": "Gao 2022",
      "modality": "TEAS",
      "comparator": "Sham",
      "n_i": 827,
      "n_c": 828,
      "median_i": 33.0,
      "q1_i": 0.0,
      "q3_i": 50.0,
      "median_c": 30.0,
      "q1_c": 0.0,
      "q3_c": 60.0,
      "median_difference": 3.0,
      "reported_p": "0.197",
      "not_pooled_reason": "25th percentile is exactly 0.0 in BOTH arms: zero-inflated, strongly non-normal. Wan/Luo mean-SD recovery is not defensible here.",
      "source_locator": "pdf-2.pdf Table: '24 h analgesic pump, ug 33.0 (0.0, 50.0) vs 30.0 (0.0, 60.0)'"
    },
    {
      "study": "Chen 2015",
      "modality": "TEAS",
      "comparator": "Sham",
      "n_i": 41,
      "n_c": 42,
      "median_i": 2.0,
      "q1_i": 2.0,
      "q3_i": 6.0,
      "median_c": 7.0,
      "q1_c": 4.0,
      "q3_c": 14.0,
      "median_difference": -5.0,
      "reported_p": "0.004",
      "not_pooled_reason": "Tier B derivation: rescue count x fixed 2 mg IV morphine. Multiplication by a positive constant is order-preserving, so quantiles transform exactly. Rescue morphine was the only postoperative opioid.",
      "source_locator": "037_chen_2015_thyroidectomy_lund.pdf: counts 1 (1-3) vs 3.5 (2-7) x 2 mg"
    }
  ],
  "analysis_sets": {
    "S0_teas_sham": {
      "analysis_id": "V33_S0_TEAS_SHAM",
      "analysis_set": "S0 (Tier A only)",
      "modality": "TEAS",
      "comparator": "Inert sham",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -13.995,
      "ci_low": -34.181,
      "ci_high": 6.19,
      "p_value": 0.1145,
      "tau2": 156.882,
      "i2": 98.59,
      "pi_low": -74.4,
      "pi_high": 46.41,
      "estimator": "REML",
      "ci_method": "Hartung-Knapp",
      "notes": "PRIMARY analysis. Tier A only; single comparator stratum."
    },
    "S0_ea_usual": {
      "analysis_id": "V33_S0_EA_USUAL",
      "analysis_set": "S0 (Tier A only)",
      "modality": "EA",
      "comparator": "Usual care / no stimulation",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 3,
      "effect_measure": "Mean difference",
      "estimate": -3.936,
      "ci_low": -19.773,
      "ci_high": 11.902,
      "p_value": 0.3969,
      "tau2": 28.471,
      "i2": 77.15,
      "pi_low": -86.3,
      "pi_high": 78.43,
      "estimator": "REML",
      "ci_method": "Hartung-Knapp",
      "notes": "SUPPORTIVE. Not sham-controlled; no sham-controlled EA trial reports this outcome."
    },
    "S1": {
      "analysis_id": "V33_S1_TEAS_SHAM",
      "analysis_set": "S1 (Tier A + Tier B)",
      "modality": "TEAS",
      "comparator": "Inert sham",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -13.995,
      "ci_low": -34.181,
      "ci_high": 6.19,
      "p_value": 0.1145,
      "tau2": 156.882,
      "i2": 98.59,
      "pi_low": null,
      "pi_high": null,
      "estimator": "REML",
      "ci_method": "Hartung-Knapp",
      "notes": "Identical to S0: no pure Tier B case exists. Chen 2015's exact derivation yields medians, so it is Tier C."
    },
    "S2": {
      "analysis_id": "V33_S2_PARALLEL",
      "analysis_set": "S2 (Tier C parallel synthesis)",
      "modality": "TEAS",
      "comparator": "Sham / usual care",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME (medians)",
      "k": 2,
      "effect_measure": "Median difference (not pooled)",
      "estimate": null,
      "ci_low": null,
      "ci_high": null,
      "p_value": null,
      "tau2": null,
      "i2": null,
      "pi_low": null,
      "pi_high": null,
      "estimator": "None (narrative parallel synthesis)",
      "ci_method": "None",
      "notes": "Gao 2022 and Chen 2015 report medians/IQRs. Gao 2022 is zero-inflated (Q1=0 in both arms), so Wan/Luo recovery is indefensible. Presented as medians alongside S0, never pooled with it."
    },
    "S3": {
      "analysis_id": "V33_S3_TEAS_SHAM",
      "analysis_set": "S3 (Tier A + Tier D)",
      "modality": "TEAS",
      "comparator": "Inert sham",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -13.995,
      "ci_low": -34.181,
      "ci_high": 6.19,
      "p_value": 0.1145,
      "tau2": 156.882,
      "i2": 98.59,
      "pi_low": null,
      "pi_high": null,
      "estimator": "REML",
      "ci_method": "Hartung-Knapp",
      "notes": "Identical to S0: the sole digitization candidate (Gu 2019) failed its pre-specified validation-against-text check (control arm error up to 16.0%)."
    },
    "sens_comparator": {
      "analysis_id": "V33_SENS_C1_SZMIT_ALT",
      "analysis_set": "Comparator sensitivity",
      "modality": "TEAS",
      "comparator": "Sham, with Szmit 2021 usual-care arm substituted",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -14.071,
      "ci_low": -34.177,
      "ci_high": 6.035,
      "p_value": 0.1123,
      "tau2": 155.677,
      "i2": 98.58,
      "pi_low": null,
      "pi_high": null,
      "estimator": "REML",
      "ci_method": "Hartung-Knapp",
      "notes": "Swap, not addition: Szmit 2021 contributes exactly one contrast."
    },
    "sens_reml_wald": {
      "analysis_id": "V33_SENS_C2_REML_WALD",
      "analysis_set": "Estimator/CI sensitivity",
      "modality": "TEAS",
      "comparator": "Inert sham",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -13.995,
      "ci_low": -26.635,
      "ci_high": -1.356,
      "p_value": 0.03,
      "tau2": 156.882,
      "i2": 98.59,
      "pi_low": null,
      "pi_high": null,
      "estimator": "REML",
      "ci_method": "Wald (z)",
      "notes": "Shown for comparison only. Wald intervals are anticonservative at k=4; the pre-specified primary remains Hartung-Knapp."
    },
    "sens_dl_kh": {
      "analysis_id": "V33_SENS_C2_DL_KH",
      "analysis_set": "Estimator/CI sensitivity",
      "modality": "TEAS",
      "comparator": "Inert sham",
      "outcome": "Cumulative postoperative opioid consumption",
      "window": "0-24 h",
      "unit": "mg IV MME",
      "k": 4,
      "effect_measure": "Mean difference",
      "estimate": -14.024,
      "ci_low": -34.189,
      "ci_high": 6.141,
      "p_value": 0.1137,
      "tau2": 171.852,
      "i2": 98.71,
      "pi_low": null,
      "pi_high": null,
      "estimator": "DerSimonian-Laird",
      "ci_method": "Hartung-Knapp",
      "notes": "Shown for comparison only."
    }
  },
  "tier_e_smd": {
    "status": "EXPLORATORY",
    "summary": "Tier E holds results that report the exact 0-24 h cumulative opioid estimand as a mean/SD, but in a unit with no sourced absolute-IV-MME conversion (a weight-normalized dose, or a volume proxy with an unreported concentration). That blocks the ABSOLUTE-MME primary above, not a WITHIN-STUDY standardized effect: a Hedges' g divides the between-arm difference by the pooled SD, so the unit cancels. This is a different, weaker claim (a relative standardized effect, not mg spared) and is never pooled with, added to, or substituted for the S0-S3 absolute-MME estimates above.",
    "contrasts": [
      {
        "study": "Coura 2011",
        "year": 2011,
        "modality": "EA",
        "comparator": "Sham/placebo",
        "stratum": "ea_sham",
        "n_i": 13.0,
        "n_c": 9,
        "unit_src": "ug/kg fentanyl",
        "hedges_g": -1.553,
        "hedges_se": 0.493,
        "sensitivity_only": false,
        "combine_note": "",
        "multiarm_note": "",
        "caveat": "Supplementary morphine/fentanyl was permitted per-protocol, so reported fentanyl is not complete opioid exposure; weight-normalized (no sourced absolute-MME factor) -- admissible on SMD only.",
        "source_locator": "covidence_819_full_article.pdf: Table 2, 13.1+/-2.2 vs 16.3+/-1.6 ug/kg"
      },
      {
        "study": "Sim 2002 (preop + postop EA combined)",
        "year": 2002,
        "modality": "EA",
        "comparator": "Placebo EA",
        "stratum": "ea_sham",
        "n_i": 60.0,
        "n_c": 30,
        "unit_src": "mg/kg morphine",
        "hedges_g": -0.444,
        "hedges_se": 0.226,
        "sensitivity_only": false,
        "combine_note": "Combined via Cochrane Handbook 6.5.2.10 from preop-EA (n=30, 0.52+/-0.19) and postop-EA (n=30, 0.58+/-0.27), both vs the same placebo arm (n=30, 0.68+/-0.38).",
        "multiarm_note": "Two correlated active arms sharing one placebo control; combined into one contrast per Cochrane Handbook 6.5.2.10, never pooled as two independent studies.",
        "caveat": "Weight-normalized (mg/kg); absolute-dose reconstruction via an assumed body weight is prohibited -- admissible on SMD only.",
        "source_locator": "v32 Opioid_24h_Candidates (mg/kg morphine, 0-24 h); PDF not re-verified this pass"
      },
      {
        "study": "Jin 2023 (2Hz + 20/100Hz combined)",
        "year": 2023,
        "modality": "EA",
        "comparator": "Sham nonpenetrating EA/no current",
        "stratum": "teas_sham",
        "n_i": 106.0,
        "n_c": 52,
        "unit_src": "mL PCIA solution (proxy)",
        "hedges_g": -0.912,
        "hedges_se": 0.177,
        "sensitivity_only": false,
        "combine_note": "Combined via Cochrane Handbook 6.5.2.10 from the 2Hz arm (n=53, 39.31+/-15.58) and the 20/100Hz arm (n=53, 45.72+/-16.92), both vs the same sham arm (n=52, 56.54+/-12.5).",
        "multiarm_note": "Two correlated frequency arms sharing one sham arm; combined into one contrast per Cochrane Handbook 6.5.2.10.",
        "caveat": "No sourced solution concentration, so absolute fentanyl mass is not recoverable; the unknown concentration is a common constant for both arms and cancels in a standardized effect -- admissible on SMD only. Modality is labelled EA in the audit (electroacupuncture); this row is placed in the 'teas_sham' stratum here as the only sham-controlled EA-family SMD candidate outside the ea_sham (placebo) stratum built from Sim 2002/Coura 2011 -- see the generator's stratum notes.",
        "source_locator": "v32 Opioid_24h_Candidates; concentration absent from main article per v32 QC"
      },
      {
        "study": "Oztas 2019",
        "year": 2019,
        "modality": "TEAS",
        "comparator": "Usual care",
        "stratum": "teas_usual",
        "n_i": 15.0,
        "n_c": 16,
        "unit_src": "mg tramadol",
        "hedges_g": -1.168,
        "hedges_se": 0.389,
        "sensitivity_only": false,
        "combine_note": "",
        "multiarm_note": "",
        "caveat": "Tramadol alone is not complete opioid exposure (rescue pethidine was also given, reported separately and not combinable -- see the excluded OZT19_TAES_vs_CTRL_TOTALOP24 row); no sourced tramadol:morphine IV MME factor exists in this review's reference tables -- admissible on SMD only. Overall RoB 2 for this study is High. Only comparison in this review's TEAS-vs-usual-care stratum: k=1, cannot be pooled.",
        "source_locator": "covidence_505_full_article.pdf: Tramadol HCl (0-24 h) 228.40+/-87.89 (TEAS) vs 357.81+/-123.70 (control) mg"
      },
      {
        "study": "Chen 2015 (Hyperalgesia)",
        "year": 2015,
        "modality": "TEAS",
        "comparator": "Electrodes/no-current sham",
        "stratum": "teas_sham",
        "n_i": 29.0,
        "n_c": 30,
        "unit_src": "ug/kg sufentanil (median/IQR, Cochrane 6.5.2.5-approximated to mean/SD)",
        "hedges_g": -2.664,
        "hedges_se": 0.358,
        "sensitivity_only": true,
        "combine_note": "Approximated from published median (IQR): intervention 0.15 (0.1-0.2), comparator 0.35 (0.3-0.4), via mean~=median and SD~=IQR/1.35 (Cochrane Handbook 6.5.2.5, assumes approximate symmetry). NOT the same case as Gao 2022 (Tier C): that distribution's 25th percentile is exactly 0 in both arms (zero-inflated), which this review has already ruled makes the same approximation indefensible; Chen 2015 (Hyperalgesia)'s IQR bounds are both strictly positive.",
        "multiarm_note": "",
        "caveat": "SENSITIVITY ONLY: median/IQR approximated to mean/SD, not a native mean/SD value like every other row in this file. Reported alongside, never silently merged into, the main Tier E SMD estimate.",
        "source_locator": "040_chen_2015_hyperalgesia_lund.pdf: T5 = 24 h after surgery"
      }
    ],
    "excluded": [
      {
        "study": "Zhang 2025",
        "reason": "Window mismatch: reports postoperative day 1, not an explicit 0-24 h clock window. The SMD metric does not fix a wrong time window."
      },
      {
        "study": "Ntritsou 2014",
        "reason": "Wrong estimand: reported total tramadol includes protocol-mandated background dosing, not only demand-driven postoperative consumption."
      },
      {
        "study": "Oztas 2019 (combined opioid dose)",
        "reason": "Combined tramadol + pethidine total; the combined variance is not recoverable without an unknown within-person covariance."
      },
      {
        "study": "Oztas 2019 (TEAS vs TENS arm)",
        "reason": "Comparator eligibility unresolved (audit status: 'Check') -- excluded pending a decision, not assumed eligible or ineligible."
      },
      {
        "study": "Song 2020",
        "reason": "Assumption-dependent derivation: PCA pump presses are recorded, not delivered doses, and presses != deliveries is an unverifiable assumption regardless of metric."
      }
    ],
    "analysis_sets": {
      "ea_sham": {
        "analysis_id": "V33_TIERE_EA_SHAM_SMD",
        "analysis_set": "Tier E exploratory SMD",
        "modality": "EA",
        "comparator": "Sham/placebo",
        "outcome": "Cumulative postoperative opioid consumption (standardized, Hedges' g)",
        "window": "0-24 h",
        "unit": "Hedges' g (SMD, dimensionless)",
        "k": 2,
        "effect_measure": "Standardized mean difference (Hedges' g)",
        "estimate": -0.912,
        "ci_low": -7.871,
        "ci_high": 6.046,
        "p_value": 0.3442,
        "tau2": 0.468,
        "i2": 76.09,
        "pi_low": null,
        "pi_high": null,
        "estimator": "REML",
        "ci_method": "Hartung-Knapp",
        "notes": "EXPLORATORY. Coura 2011 + Sim 2002 (two correlated EA-timing arms combined per Cochrane Handbook 6.5.2.10). Weight-normalized native units (ug/kg, mg/kg); not convertible to absolute IV MME. Not a substitute for the missing sham-controlled EA absolute-MME estimate (k=0 in the S0 primary)."
      },
      "teas_sham_main": {
        "analysis_id": "V33_TIERE_TEAS_SHAM_SMD_MAIN",
        "analysis_set": "Tier E exploratory SMD",
        "modality": "EA",
        "comparator": "Sham nonpenetrating EA/no current",
        "outcome": "Cumulative postoperative opioid consumption (standardized, Hedges' g)",
        "window": "0-24 h",
        "unit": "Hedges' g (SMD, dimensionless)",
        "k": 1,
        "effect_measure": "Standardized mean difference (Hedges' g)",
        "estimate": -0.912,
        "ci_low": -1.258,
        "ci_high": -0.565,
        "p_value": null,
        "tau2": null,
        "i2": null,
        "pi_low": null,
        "pi_high": null,
        "estimator": "Single study (no pooling)",
        "ci_method": "Normal approximation (g +/- 1.96 x SE)",
        "notes": "EXPLORATORY, k=1 (Jin 2023, two correlated frequency arms combined per Cochrane Handbook 6.5.2.10). Volume (mL PCIA solution) proxy for fentanyl mass; concentration unreported, so the unit cancels in SMD but is not convertible to absolute dose. Cannot be meta-analysed with k=1; CI is a normal approximation, not Hartung-Knapp."
      },
      "teas_sham_sensitivity": {
        "analysis_id": "V33_TIERE_TEAS_SHAM_SMD_SENS",
        "analysis_set": "Tier E exploratory SMD sensitivity",
        "modality": "EA/TEAS",
        "comparator": "Sham",
        "outcome": "Cumulative postoperative opioid consumption (standardized, Hedges' g)",
        "window": "0-24 h",
        "unit": "Hedges' g (SMD, dimensionless)",
        "k": 2,
        "effect_measure": "Standardized mean difference (Hedges' g)",
        "estimate": -1.76,
        "ci_low": -12.89,
        "ci_high": 9.369,
        "p_value": 0.2939,
        "tau2": 1.456,
        "i2": 94.82,
        "pi_low": null,
        "pi_high": null,
        "estimator": "REML",
        "ci_method": "Hartung-Knapp",
        "notes": "SENSITIVITY, not the main Tier E estimate. Adds Chen 2015 (Hyperalgesia) to Jin 2023 (combined). Chen 2015 (Hyperalgesia) is median/IQR approximated to mean/SD (Cochrane Handbook 6.5.2.5); this is a materially weaker evidentiary basis than every other row in this file, which are all native mean/SD. Reported as a named addition, never merged silently into V33_TIERE_TEAS_SHAM_SMD_MAIN."
      },
      "teas_usual": {
        "analysis_id": "V33_TIERE_TEAS_USUAL_SMD",
        "analysis_set": "Tier E exploratory SMD",
        "modality": "TEAS",
        "comparator": "Usual care",
        "outcome": "Cumulative postoperative opioid consumption (standardized, Hedges' g)",
        "window": "0-24 h",
        "unit": "Hedges' g (SMD, dimensionless)",
        "k": 1,
        "effect_measure": "Standardized mean difference (Hedges' g)",
        "estimate": -1.168,
        "ci_low": -1.93,
        "ci_high": -0.406,
        "p_value": null,
        "tau2": null,
        "i2": null,
        "pi_low": null,
        "pi_high": null,
        "estimator": "Single study (no pooling)",
        "ci_method": "Normal approximation (g +/- 1.96 x SE)",
        "notes": "EXPLORATORY, k=1 (Oztas 2019). Native mg tramadol; no sourced tramadol:morphine IV MME factor, and tramadol alone is not complete opioid exposure (rescue pethidine reported separately). Overall RoB 2 High. Cannot be meta-analysed with k=1; CI is a normal approximation, not Hartung-Knapp."
      }
    }
  },
  "figures": [
    {
      "file": "forestA_S0_teas_sham_24h_mme.png",
      "caption": "A. Primary — TEAS vs inert sham, cumulative 0–24 h opioid (mg IV MME)"
    },
    {
      "file": "forestB_S0_ea_usualcare_24h_mme.png",
      "caption": "B. Supportive — EA vs usual care, cumulative 0–24 h opioid (mg IV MME)"
    },
    {
      "file": "forestC_tier_sensitivity.png",
      "caption": "C. Tier sensitivity — analysis sets S0, S1, S3"
    },
    {
      "file": "forestD_comparator_sensitivity.png",
      "caption": "D. Comparator sensitivity — sham vs usual-care strata"
    },
    {
      "file": "forestE_ea_sham_smd.png",
      "caption": "E. EXPLORATORY — Tier E scale-free SMD, EA vs sham/placebo (Hedges' g, k=2). Not the absolute-MME estimand."
    },
    {
      "file": "forestF_teas_sham_smd_sensitivity.png",
      "caption": "F. EXPLORATORY SENSITIVITY — Tier E scale-free SMD, EA/TEAS vs sham (Hedges' g, k=2), adding a median/IQR-approximated study."
    }
  ],
  "empty_cells": [
    {
      "cell": "EA vs inert sham",
      "k": 0,
      "statement": "No sham-controlled EA trial reports an analysable cumulative 0–24 h opioid mean and SD in absolute dose units. The EA estimate is a usual-care comparison and cannot be read as a specific-acupoint effect."
    },
    {
      "cell": "Tier B increment (S1)",
      "k": 0,
      "statement": "No trial supplies a deterministic mean/SD derivation that is not already Tier A. Chen 2015's rescue-bolus derivation is exact, but the reported quantities are medians and IQRs, so it is Tier C."
    },
    {
      "cell": "Tier D increment (S3)",
      "k": 0,
      "statement": "One candidate (Gu 2019, Figure 4) was digitized under a pre-specified protocol. Axis calibration was exact, and the low-frequency TEAS arm reproduced the in-text values to within 4.2%, but the control arm was overestimated by up to 16.0% — a figure-versus-text inconsistency in the source. The digitization failed validation and Gu 2019 is not admissible."
    }
  ],
  "withdrawn": [
    {
      "study": "Zhang 2025",
      "reason": "Reports postoperative day 1, not an explicit 0–24 h clock window. Removed from every 0–24 h analysis, including the scale-free broader SMD sensitivity (k = 10 → 9): the SMD changes the unit, not the estimand."
    },
    {
      "study": "Coura 2011 (70 kg reconstruction)",
      "reason": "The reader-facing absolute-dose reconstruction multiplies µg/kg by an assumed 70 kg the trial never reports. Labelled a legacy reconstruction; it feeds no pooled estimate. Coura 2011 enters only the scale-free SMD sensitivity, from its native µg/kg values."
    }
  ]
};
