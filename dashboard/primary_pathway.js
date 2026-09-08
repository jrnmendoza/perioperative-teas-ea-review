// PRIMARY OUTCOME CONTRIBUTION PATHWAY — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_primary_pathway.py
//
// Every count is derived from the v26 lock and the final Stata run; none is
// hardcoded. If an author supplies usable data and the locked dataset is
// updated, re-running this script moves the study between categories and the
// dashboard counts follow automatically.
//
// Source workbook : TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx
// Statistics      : StataNow 19.5 BE — 06_FINAL_ANALYSIS_V26 + 07_TIERED_V33
// PROSPERO        : CRD420251090635
window.PRIMARY_PATHWAY = {
  "generated_by": "scripts/build_primary_pathway.py",
  "data_source": "TEAS_EA_RECONCILED_MASTER_DATA_v32_FINAL_LOCK_READY.xlsx",
  "statistical_source": "StataNow 19.5 BE — 06_FINAL_ANALYSIS_V26 + 07_TIERED_V33",
  "prospero": "CRD420251090635",
  "review_included_rcts": 70,
  "candidate_rows": 16,
  "publications_with_24h_info": 17,
  "primary_strict": [
    {
      "study_unit": "Chen 1998",
      "study_id": "1879897506",
      "study_ids": [
        "1879897506"
      ],
      "covers_publications": 1,
      "comparison_id": "CHEN98_ACU_vs_SHAM",
      "n_i": 25,
      "n_c": 25,
      "n_total": 50,
      "data_type": "Mean/SD",
      "unit": "mg hydromorphone",
      "time_window": "First 24 h postoperatively",
      "outcome": "Cumulative IV PCA hydromorphone",
      "result_rob": "Some concerns",
      "md_mme": -21.0,
      "se_mme": 6.1033,
      "hedges_g": -0.9579,
      "hedges_se": 0.2986,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "Four-arm RCT; shared sham control must be handled correctly",
      "conversion_note": "Opioid/MME conversion required using prespecified review conversion",
      "sensitivity_note": "Four-arm study; alternative active-site contrasts belong in sensitivity/mechanistic analyses.",
      "source_url": "https://drive.google.com/file/d/1lUyYj9aN1CL9RpY86ZY0970To83Kb17s/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    },
    {
      "study_unit": "Chen 2020",
      "study_id": "1879896688",
      "study_ids": [
        "1879896688"
      ],
      "covers_publications": 1,
      "comparison_id": "CHEN20_TEAS_vs_SHAM",
      "n_i": 40,
      "n_c": 40,
      "n_total": 80,
      "data_type": "Mean/SD",
      "unit": "µg sufentanil",
      "time_window": "24 h postoperatively",
      "outcome": "Cumulative sufentanil",
      "result_rob": "Some concerns",
      "md_mme": -28.19,
      "se_mme": 1.7811,
      "hedges_g": -3.505,
      "hedges_se": 0.3561,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "Sham was 4 mA pre/postoperatively but 0 mA intraoperatively; preserve this nuance",
      "conversion_note": "Opioid/MME conversion required using prespecified review conversion",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/1y0_cC1NCl5g2vYxDMOtYmxVA_YEE-rsR/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target A — 0–48 h opioid",
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    },
    {
      "study_unit": "El-Rakshy 2009",
      "study_id": "1879897344",
      "study_ids": [
        "1879897344"
      ],
      "covers_publications": 1,
      "comparison_id": "ELR09_EA_vs_CTRL_MORPH24",
      "n_i": 42,
      "n_c": 53,
      "n_total": 95,
      "data_type": "Mean/SD",
      "unit": "mg IV morphine",
      "time_window": "First 24 h",
      "outcome": "Total IV morphine analgesia",
      "result_rob": "High",
      "md_mme": -1.6,
      "se_mme": 3.7185,
      "hedges_g": -0.0882,
      "hedges_se": 0.2067,
      "v26_decision": "INCLUDE IN PRIMARY WITH SENSITIVITY EXCLUSION",
      "source_qc": "Publication has irreconcilable allocation/analyzed group labels. Use Table 2 n=42 EA and n=53 control for this result; do not substitute overall study denominators.",
      "conversion_note": "Use native IV morphine; convert to review-standard MME only per prespecified rule",
      "sensitivity_note": "High RoB / denominator inconsistency: rerun meta-analysis excluding this study.",
      "source_url": "https://drive.google.com/file/d/12AfIox-MgnMU15U-mdvZgaTKnukXKvAR/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY WITH SENSITIVITY EXCLUSION"
    },
    {
      "study_unit": "He 2026 (hepatectomy/JIS)",
      "study_id": "1879895909",
      "study_ids": [
        "1879895909"
      ],
      "covers_publications": 1,
      "comparison_id": "HEJIS26_TEAS_vs_CTRL_MME24",
      "n_i": 80,
      "n_c": 79,
      "n_total": 159,
      "data_type": "Mean/SD",
      "unit": "mg MME",
      "time_window": "0-24 h",
      "outcome": "Total postoperative opioid consumption in morphine equivalents",
      "result_rob": "Some concerns",
      "md_mme": -0.6,
      "se_mme": 0.5783,
      "hedges_g": -0.1643,
      "hedges_se": 0.1589,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "Supplemental eTable 1 directly reports MME; mITT excludes one canceled surgery and one consent withdrawal after randomization",
      "conversion_note": "None",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/1VgOxIOrGe7ZVevkKEVP7G-0V1DXPU0Gf/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    },
    {
      "study_unit": "Seevaunnamtum 2016",
      "study_id": "1879896891",
      "study_ids": [
        "1879896891"
      ],
      "covers_publications": 1,
      "comparison_id": "SEEVA16_EA_vs_UC",
      "n_i": 32,
      "n_c": 32,
      "n_total": 64,
      "data_type": "Mean/SD",
      "unit": "mg morphine",
      "time_window": "First 24 h postoperatively",
      "outcome": "Cumulative IV PCA morphine requirement",
      "result_rob": "Some concerns",
      "md_mme": -12.56,
      "se_mme": 4.3891,
      "hedges_g": -0.7067,
      "hedges_se": 0.2577,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "No allocation-concealment method reported",
      "conversion_note": "None",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/1OhuqhDUCEmOij7fZFhHHCJNwfQ9xpMzd/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    },
    {
      "study_unit": "Szmit 2021",
      "study_id": "NEW32_SZMIT2021",
      "study_ids": [
        "NEW32_SZMIT2021"
      ],
      "covers_publications": 1,
      "comparison_id": "SZMIT21_TEAS_vs_SHAM_MORPH24",
      "n_i": 24,
      "n_c": 24,
      "n_total": 48,
      "data_type": "Mean/SD",
      "unit": "mg IV morphine",
      "time_window": "0-24 h postoperative",
      "outcome": "Total IV PCA morphine dose",
      "result_rob": "Some concerns",
      "md_mme": -7.7,
      "se_mme": 1.4913,
      "hedges_g": -1.466,
      "hedges_se": 0.3251,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "Source reports both mean/SD and median/IQR; primary outcome prespecified and directly reported.",
      "conversion_note": "None",
      "sensitivity_note": "Three-arm RCT; PCA-only control is an alternative correlated comparator.",
      "source_url": "https://drive.google.com/file/d/1SbgHRO4KEP9X0Unz75vDMFCvlkDTEgk3/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target D — PONV"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    },
    {
      "study_unit": "Yang 2024",
      "study_id": "1879896323",
      "study_ids": [
        "1879896323"
      ],
      "covers_publications": 1,
      "comparison_id": "YANG24_EA_vs_UC_MORPH24",
      "n_i": 90,
      "n_c": 90,
      "n_total": 180,
      "data_type": "Mean/SD",
      "unit": "mg morphine",
      "time_window": "First 24 h / POD1",
      "outcome": "Morphine use via IV PCA",
      "result_rob": "Some concerns",
      "md_mme": -0.3,
      "se_mme": 0.7157,
      "hedges_g": -0.0622,
      "hedges_se": 0.1491,
      "v26_decision": "INCLUDE IN PRIMARY",
      "source_qc": "All 180 randomized participants retained in ITT; open-label patients but objective PCA drug-use record",
      "conversion_note": "None",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/160N3psd5tLEphwXHJzUEZ3uJfaIXcs5V/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target B — 0–72 h opioid",
        "Target D — PONV",
        "Target E — time to first flatus",
        "Target F — exploratory opioid outcomes"
      ],
      "category": "strict",
      "qualifies_because": "INCLUDE IN PRIMARY"
    }
  ],
  "primary_conditional": [
    {
      "study_unit": "Chen 2015",
      "study_id": "1879897004",
      "study_ids": [
        "1879897004"
      ],
      "covers_publications": 1,
      "comparison_id": "CHEN15Q_TEAS_vs_CTRL_RESCUEMORPH24",
      "n_i": 41,
      "n_c": 42,
      "n_total": 83,
      "data_type": "Median/IQR",
      "unit": "mg IV morphine",
      "time_window": "0-24 h",
      "outcome": "Cumulative rescue IV morphine dose derived from fixed 2-mg rescue administrations",
      "result_rob": "High",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": null,
      "hedges_se": null,
      "v26_decision": "CONDITIONAL — DERIVED MEDIAN/IQR",
      "source_qc": "Source reports rescue-administration count 1 (1-3) vs 3.5 (2-7); each rescue administration was fixed at morphine 2 mg. Linear conversion to mg is exact, but the source itself reports counts rather than dose.",
      "conversion_note": "Use native IV morphine; convert to review-standard MME only per prespecified rule",
      "sensitivity_note": "Use only if derived dose endpoints are permitted and median/IQR synthesis is prespecified.",
      "source_url": "https://drive.google.com/file/d/1ZtE8GImDcpDJH1tOvzqazoh_S4Gd67oH/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "conditional",
      "not_strict_because": "CONDITIONAL — DERIVED MEDIAN/IQR",
      "estimable_md": false,
      "estimable_smd": false
    },
    {
      "study_unit": "Chen 2015 (Hyperalgesia)",
      "study_id": "1879897029",
      "study_ids": [
        "1879897029"
      ],
      "covers_publications": 1,
      "comparison_id": "CHEN15H_TEAS_vs_SHAM_SUFKG24",
      "n_i": 29,
      "n_c": 30,
      "n_total": 59,
      "data_type": "Median/IQR",
      "unit": "µg/kg sufentanil",
      "time_window": "0-24 h",
      "outcome": "Derived cumulative sufentanil dose from fixed 0.05 µg/kg bolus",
      "result_rob": "Some concerns",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": null,
      "hedges_se": null,
      "v26_decision": "CONDITIONAL — WEIGHT-NORMALIZED DERIVED",
      "source_qc": "Exact linear conversion from 0.05 µg/kg per bolus × reported bolus count. Do not convert to absolute µg or MME without individual body weights.",
      "conversion_note": "Opioid/MME conversion required using prespecified review conversion",
      "sensitivity_note": "Do not convert to absolute µg/MME using group-average weight.",
      "source_url": "https://drive.google.com/file/d/13YKAZZsc2VQEPqkw1Ye40BYDZSRpI6N3/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "conditional",
      "not_strict_because": "CONDITIONAL — WEIGHT-NORMALIZED DERIVED",
      "estimable_md": false,
      "estimable_smd": false
    },
    {
      "study_unit": "Coura 2011",
      "study_id": "1879897266",
      "study_ids": [
        "1879897266"
      ],
      "covers_publications": 1,
      "comparison_id": "COURA11_EA_vs_SHAM",
      "n_i": 13,
      "n_c": 9,
      "n_total": 22,
      "data_type": "Mean/SD",
      "unit": "µg/kg fentanyl",
      "time_window": "First 24 h postoperatively",
      "outcome": "Cumulative fentanyl",
      "result_rob": "High",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": -1.5533,
      "hedges_se": 0.4928,
      "v26_decision": "CONDITIONAL — CONVERSION/ATTRITION",
      "source_qc": "10/32 post-randomization exclusions; supplemental morphine/fentanyl inclusion unclear",
      "conversion_note": "Opioid/MME conversion required using prespecified review conversion",
      "sensitivity_note": "High RoB; include only if the protocol prespecifies handling of weight-normalized opioid doses.",
      "source_url": "https://drive.google.com/file/d/120NJxCmxsdiyqWTXzjmaUWAaVa1i8iZz/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "conditional",
      "not_strict_because": "CONDITIONAL — CONVERSION/ATTRITION",
      "estimable_md": false,
      "estimable_smd": true
    },
    {
      "study_unit": "Sim 2002",
      "study_id": "1879897479",
      "study_ids": [
        "1879897479"
      ],
      "covers_publications": 1,
      "comparison_id": "SIM02_PREOP_vs_PLACEBO_MORPH24",
      "n_i": 30,
      "n_c": 30,
      "n_total": 60,
      "data_type": "Mean/SD",
      "unit": "mg/kg morphine",
      "time_window": "0-24 h",
      "outcome": "Cumulative postoperative IV PCA morphine",
      "result_rob": "Some concerns",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": -0.5257,
      "hedges_se": 0.2626,
      "v26_decision": "CONDITIONAL — WEIGHT-NORMALIZED + MULTI-ARM",
      "source_qc": "Do not convert mg/kg to absolute mg using group mean body weight; aggregate means cannot reconstruct individual absolute dose",
      "conversion_note": "Weight-normalized endpoint; do not reconstruct absolute dose from group mean weight",
      "sensitivity_note": "Do not reconstruct absolute mg from mean body weight.",
      "source_url": "https://drive.google.com/file/d/1YsNHL-J3Kgfu8mCanRrNu_bHk_roj0w6/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "conditional",
      "not_strict_because": "CONDITIONAL — WEIGHT-NORMALIZED + MULTI-ARM",
      "estimable_md": false,
      "estimable_smd": true
    },
    {
      "study_unit": "Zhang 2025",
      "study_id": "1879896013",
      "study_ids": [
        "1879896013"
      ],
      "covers_publications": 1,
      "comparison_id": "ZHANG25_TEAS_vs_SHAM_SUFPOD1",
      "n_i": 45,
      "n_c": 48,
      "n_total": 93,
      "data_type": "Mean/SD",
      "unit": "µg sufentanil",
      "time_window": "POD1; approximately 24 h but exact clock window not explicit",
      "outcome": "Total sufentanil consumption",
      "result_rob": "High",
      "md_mme": -3.26,
      "se_mme": 0.9962,
      "hedges_g": -0.6703,
      "hedges_se": 0.2132,
      "v26_decision": "CONDITIONAL — POD1 ≠ STRICT CLOCK 24H",
      "source_qc": "Endpoint is directly reported as POD1, not explicitly clock-defined 0-24 h; 15/108 excluded after randomization",
      "conversion_note": "Opioid/MME conversion required using prespecified review conversion",
      "sensitivity_note": "High RoB from post-randomization exclusions; use only if POD1 is accepted as the 24-h window.",
      "source_url": "https://drive.google.com/file/d/1eHx6Hk16vmIfMgoiZ5eNae4zmCR5ktwJ/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [],
      "category": "conditional",
      "not_strict_because": "CONDITIONAL — POD1 ≠ STRICT CLOCK 24H",
      "estimable_md": true,
      "estimable_smd": true
    }
  ],
  "primary_author_contact_candidates": [
    {
      "study_unit": "Jin 2023",
      "study_id": "1879896440",
      "study_ids": [
        "1879896440"
      ],
      "covers_publications": 1,
      "comparison_id": "JIN23_2HZ_vs_SHAM_VOL24",
      "n_i": 53,
      "n_c": 52,
      "n_total": 105,
      "data_type": "Mean/SD",
      "unit": "mL PCIA solution",
      "time_window": "24 h",
      "outcome": "Published 'fentanyl consumption' / PCIA solution volume",
      "result_rob": "High",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": -1.2097,
      "hedges_se": 0.2123,
      "v26_decision": "EXCLUDE FROM DOSE; PCA VOLUME PROXY ONLY",
      "source_qc": "Main article does not report fentanyl concentration. Do not convert mL to µg/mg/MME. 2-Hz vs 20/100-Hz inferential statistics conflict between table and prose",
      "conversion_note": "Do not convert unless concentration and delivered dose are fully known",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/1fkNAFra0gZ9jkWkzp_S0TWy-5zVrXCtj/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ],
      "category": "candidate",
      "hard_hold": false,
      "documented_issue": null,
      "author_contact": {
        "status": "CONTACT PREPARED",
        "status_basis": "A drafted inquiry letter exists in author_inquiries.json. The project records no sent/response field, so no further status can be asserted.",
        "roster_label": "#326 - Jin 2022",
        "data_needed": "Concentration of fentanyl in the postoperative PCIA pump solution (e.g. µg/mL or total µg fentanyl in total volume mL).",
        "impact": "Allows direct mathematical conversion of the reported mL volumes into micrograms (µg) of fentanyl and oral/IV morphine milligram equivalents (MME) for primary opioid meta-analysis.",
        "priority": "IMPORTANT",
        "addresses_primary_blocker": true,
        "gap_note": ""
      }
    },
    {
      "study_unit": "Luo 2026",
      "study_id": "1879895932",
      "study_ids": [
        "1879895932"
      ],
      "covers_publications": 1,
      "comparison_id": "LUO26_TEAS_vs_SHAM_OPIOIDEQUIV",
      "n_i": 138,
      "n_c": 139,
      "n_total": 277,
      "data_type": "Mean/SD",
      "unit": "published as mg; definition/unit unresolved",
      "time_window": "Perioperative",
      "outcome": "Published 'sufentanil equivalents' metric",
      "result_rob": "Some concerns",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": 0.1348,
      "hedges_se": 0.1203,
      "v26_decision": "EXCLUDE UNTIL UNIT/DEFINITION RESOLVED",
      "source_qc": "Source labels approximately 15-16 as 'sufentanil equivalents (mg)' without explaining conversion; preserve verbatim",
      "conversion_note": "None",
      "sensitivity_note": "",
      "source_url": "https://drive.google.com/file/d/1xxZle6mPpcnmHLblJbsy1kA4CyQHpvm2/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [
        "Target D — PONV"
      ],
      "category": "candidate",
      "hard_hold": true,
      "documented_issue": null,
      "author_contact": {
        "status": "CONTACT PREPARED",
        "status_basis": "A drafted inquiry letter exists in author_inquiries.json. The project records no sent/response field, so no further status can be asserted.",
        "roster_label": "#35 - Luo 2026",
        "data_needed": "Cumulative 24-hour postoperative systemic opioid consumption (mean ± SD in IV MME) and resting vs movement pain distinction at 24 hours.",
        "impact": "Provides precise postoperative opioid dosage in IV MME and verifies pain conditions for the primary review synthesis in a 277-patient tympanoplasty trial.",
        "priority": "IMPORTANT",
        "addresses_primary_blocker": true,
        "gap_note": ""
      }
    },
    {
      "study_unit": "Yeh lumbar-spine publication family — ONE study unit pending overlap adjudication",
      "study_id": null,
      "study_ids": [
        "1879897280",
        "1879897273"
      ],
      "covers_publications": 2,
      "comparison_id": "YEH11_AES_vs_SHAM_MORPH24",
      "n_i": 30,
      "n_c": 30,
      "n_total": 60,
      "data_type": "Mean/SD",
      "unit": "mg IV morphine",
      "time_window": "First 24 postoperative hours",
      "outcome": "24-h IV morphine PCA dose",
      "result_rob": "Some concerns",
      "md_mme": -2.3,
      "se_mme": 2.976,
      "hedges_g": -0.197,
      "hedges_se": 0.2588,
      "v26_decision": "HOLD — OVERLAPPING PUBLICATIONS",
      "source_qc": "Highly similar to Yeh 2010 in population, acupoints, comparator and 24-h opioid values; do not count independently until cohort/publication linkage is adjudicated.",
      "conversion_note": "Use native IV morphine; convert to review-standard MME only per prespecified rule",
      "sensitivity_note": "Do not include either report until the publication/cohort linkage is adjudicated.",
      "source_url": "https://drive.google.com/file/d/1ZJ60ZvJ5Q7sRu1iptK_tLLfBXxZZ_Hwl/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [],
      "category": "candidate",
      "hard_hold": true,
      "documented_issue": {
        "issue_id": "P1-01",
        "issue": "Potential overlapping/companion cohort; identical sham PCA/morphine values and near-identical active/control values.",
        "disposition_class": "HARD_HOLD_DEPENDENCY",
        "quantitative_action": "Exclude both publications from any common pooled model until overlap is adjudicated; keep one unresolved publication-family study unit.",
        "author_need": "Confirm whether cohorts overlap wholly/partly. If unresolved, retain both on duplicate-family hold.",
        "status": "HARD HOLD",
        "blocker": "NO",
        "source_sheet": "AF_P1_Disposition"
      },
      "author_contact": {
        "status": "CONTACT PREPARED",
        "status_basis": "A drafted inquiry letter exists in author_inquiries.json. The project records no sent/response field, so no further status can be asserted.",
        "roster_label": "#828 - Yeh 2010",
        "data_needed": "Incidence of postoperative nausea, vomiting, or rescue antiemetic administration (0-24h) and prospective clinical trial registration identifier.",
        "impact": "Supplies author-verified emetic outcomes and prospective registration details for 90-patient spinal surgery trial.",
        "priority": "IMPORTANT",
        "addresses_primary_blocker": false,
        "gap_note": "The prepared letter does not request the information that blocks this trial's 24-h opioid result. Contacting the author as drafted would not, on its own, make the trial strictly usable."
      }
    },
    {
      "study_unit": "Zhou 2021",
      "study_id": "1879896611",
      "study_ids": [
        "1879896611"
      ],
      "covers_publications": 1,
      "comparison_id": "ZHOU21_TEAS_vs_UC_OPIOIDUSE",
      "n_i": 41,
      "n_c": 40,
      "n_total": 81,
      "data_type": "Events/total",
      "unit": "participants",
      "time_window": "Postoperative window not clearly defined as 0-24 h",
      "outcome": "Any postoperative opioid use",
      "result_rob": "High",
      "md_mme": null,
      "se_mme": null,
      "hedges_g": null,
      "hedges_se": null,
      "v26_decision": "EXCLUDE FROM CONTINUOUS DOSE; USE SEPARATE BINARY ANALYSIS",
      "source_qc": "Exact postoperative time window is not clearly stated",
      "conversion_note": "None",
      "sensitivity_note": "Can be analyzed separately as binary opioid-use incidence.",
      "source_url": "https://drive.google.com/file/d/1PxYyULBv_ZjWeqAm_bNYkDn_j2_lNYLq/view?usp=drivesdk",
      "source_sheet": "Stata_Opioid24_Primary / opioid_24h_primary.csv",
      "also_contributes_to": [],
      "category": "candidate",
      "hard_hold": false,
      "documented_issue": {
        "issue_id": "P1-09",
        "issue": "Exact opioid-consumption time window unclear; morphine-equivalent conversion differs between Methods and Table footnote.",
        "disposition_class": "RESOLVED_BY_EXCLUSION",
        "quantitative_action": "Exclude from fixed 24/48/72-h opioid pools. Retain binary opioid-use and author-defined MME only in evidence map/native-scale descriptive analyses.",
        "author_need": "Exact time window and actual conversion rule required for fixed-window MME synthesis.",
        "status": "DISPOSITIONED",
        "blocker": "NO",
        "source_sheet": "AF_P1_Disposition"
      },
      "author_contact": {
        "status": "CONTACT PREPARED",
        "status_basis": "A drafted inquiry letter exists in author_inquiries.json. The project records no sent/response field, so no further status can be asserted.",
        "roster_label": "#433 - Zhou 2021",
        "data_needed": "Cumulative 24-hour postoperative systemic opioid consumption (mg IV MME) separated from entire stay consumption, and resting vs movement condition for POD 1 pain scores.",
        "impact": "Supplies author-verified 24-hour postoperative opioid consumption and clarifies pain measurement condition for 81-patient gastrectomy trial.",
        "priority": "IMPORTANT",
        "addresses_primary_blocker": true,
        "gap_note": ""
      }
    }
  ],
  "other_outcome_contributors": [
    {
      "study_unit": "Lin 2002",
      "study_id": "1879897477",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Wong 2006",
      "study_id": "1879897414",
      "also_contributes_to": [
        "Target B — 0–72 h opioid"
      ]
    },
    {
      "study_unit": "Lee 2011",
      "study_id": "1879897255",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Ng 2013",
      "study_id": "1879897195",
      "also_contributes_to": [
        "Target E — time to first flatus"
      ]
    },
    {
      "study_unit": "An 2014",
      "study_id": "1879897069",
      "also_contributes_to": [
        "Target A — 0–48 h opioid"
      ]
    },
    {
      "study_unit": "Ntritsou 2014",
      "study_id": "1879897120",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Xie 2014",
      "study_id": "1879897074",
      "also_contributes_to": [
        "Target A — 0–48 h opioid",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Zhang 2014",
      "study_id": "1879897091",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Huang 2017",
      "study_id": "1882881457",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Sun 2017",
      "study_id": "1879896963",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Yang 2020",
      "study_id": "1879896661",
      "also_contributes_to": [
        "Target E — time to first flatus"
      ]
    },
    {
      "study_unit": "Yu 2020",
      "study_id": "1879896692",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Ao 2021",
      "study_id": "1879896620",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Liang 2021",
      "study_id": "1879896610",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Liu 2021",
      "study_id": "1879896597",
      "also_contributes_to": [
        "Target C — pain at rest ~24 h",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Lu 2021",
      "study_id": "1879896580",
      "also_contributes_to": [
        "Target D — PONV",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Xiong 2021",
      "study_id": "1879896608",
      "also_contributes_to": [
        "Target D — PONV"
      ]
    },
    {
      "study_unit": "Lu 2022",
      "study_id": "1879896426",
      "also_contributes_to": [
        "Target E — time to first flatus",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Wu 2022",
      "study_id": "1879896450",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Xing 2022",
      "study_id": "1879896460",
      "also_contributes_to": [
        "Target C — pain at rest ~24 h",
        "Target D — PONV",
        "Target E — time to first flatus",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Guo 2023",
      "study_id": "1879896335",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Hou 2023",
      "study_id": "1879896391",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Pan 2023",
      "study_id": "1879896396",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Zhang 2023",
      "study_id": "1879896412",
      "also_contributes_to": [
        "Target A — 0–48 h opioid"
      ]
    },
    {
      "study_unit": "Tu 2024",
      "study_id": "1879896309",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Long 2025",
      "study_id": "1879896090",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Wu 2025",
      "study_id": "1879896116",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Zheng 2025",
      "study_id": "1879896014",
      "also_contributes_to": [
        "Target D — PONV",
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Jiang 2026",
      "study_id": "1879895860",
      "also_contributes_to": [
        "Target F — exploratory opioid outcomes"
      ]
    },
    {
      "study_unit": "Ma 2026",
      "study_id": "1879895855",
      "also_contributes_to": [
        "Target D — PONV"
      ]
    }
  ],
  "no_pooled_model": [
    {
      "study_unit": "Yao 2015",
      "study_id": "1879897026",
      "also_contributes_to": []
    },
    {
      "study_unit": "Grech 2016",
      "study_id": "1879896952",
      "also_contributes_to": []
    },
    {
      "study_unit": "Gu 2019",
      "study_id": "1881841223",
      "also_contributes_to": []
    },
    {
      "study_unit": "Zhan 2020",
      "study_id": "1881841076",
      "also_contributes_to": []
    },
    {
      "study_unit": "Gao 2021",
      "study_id": "1879896559",
      "also_contributes_to": []
    },
    {
      "study_unit": "Li 2021",
      "study_id": "1879896618",
      "also_contributes_to": []
    },
    {
      "study_unit": "Li 2022",
      "study_id": "1879896493",
      "also_contributes_to": []
    },
    {
      "study_unit": "Zhu 2022",
      "study_id": "1879896528",
      "also_contributes_to": []
    },
    {
      "study_unit": "Wang 2023",
      "study_id": "1879896394",
      "also_contributes_to": []
    },
    {
      "study_unit": "Huang 2024",
      "study_id": "1879896311",
      "also_contributes_to": []
    },
    {
      "study_unit": "Wang 2024",
      "study_id": "1879896259",
      "also_contributes_to": []
    },
    {
      "study_unit": "Huang 2025",
      "study_id": "1879896131",
      "also_contributes_to": []
    },
    {
      "study_unit": "Liu 2025",
      "study_id": "1879896021",
      "also_contributes_to": []
    },
    {
      "study_unit": "#105119 - Zhou 2025",
      "study_id": "1879896105",
      "also_contributes_to": []
    },
    {
      "study_unit": "He 2026 (breast/WJCO)",
      "study_id": "1879895945",
      "also_contributes_to": []
    },
    {
      "study_unit": "Liu 2026 (burn)",
      "study_id": "1879895960",
      "also_contributes_to": []
    },
    {
      "study_unit": "Liu 2026 (ESD)",
      "study_id": "1879896009",
      "also_contributes_to": []
    },
    {
      "study_unit": "Gao 2022",
      "study_id": "NEW32_GAO2022",
      "also_contributes_to": []
    },
    {
      "study_unit": "Song 2020",
      "study_id": "NEW32_SONG2020",
      "also_contributes_to": []
    },
    {
      "study_unit": "Wu 2016",
      "study_id": "NEW32_WU2016",
      "also_contributes_to": []
    },
    {
      "study_unit": "Liu 2015",
      "study_id": "NEW32_LIU2015",
      "also_contributes_to": []
    },
    {
      "study_unit": "Oztas 2019",
      "study_id": "NEW32_OZTAS2019",
      "also_contributes_to": []
    },
    {
      "study_unit": "Zhang 2018",
      "study_id": "NEW32_ZHANG2018",
      "also_contributes_to": []
    }
  ],
  "reconciles": true,
  "counts": {
    "included_rcts": 70,
    "reporting_relevant_24h_info": 17,
    "candidate_rows": 16,
    "strict": 7,
    "strict_n": 676,
    "conditional": 5,
    "conditional_n": 317,
    "candidate_pool": 12,
    "candidate_pool_n": 993,
    "author_contact_candidates": 4,
    "other_outcome_contributors": 30,
    "no_pooled_model": 23,
    "broader_smd_k": 9,
    "broader_smd_n": 758
  },
  "results": {
    "strict_md": {
      "analysis_id": "OP24_PRIM_COMB",
      "k": 7,
      "effect_measure": "MD (mg IV MME)",
      "estimate": -9.907,
      "ci_low": -20.0794,
      "ci_high": 0.2654,
      "p_value": 0.05454,
      "tau2": 113.9106,
      "i2": 98.57,
      "model": "REML + Hartung-Knapp",
      "stratum": "Combined Strict Primary (TEAS + EA)"
    },
    "strict_smd": {
      "analysis_id": "OP24_STRICT_SMD",
      "k": 7,
      "effect_measure": "Hedges g (SMD)",
      "estimate": -0.9667,
      "ci_low": -2.0862,
      "ci_high": 0.1527,
      "p_value": 0.07902,
      "tau2": 1.366,
      "i2": 96.5,
      "model": "REML + Hartung-Knapp",
      "stratum": "Strict primary 24-h opioid, Hedges g"
    },
    "broader_smd": {
      "analysis_id": "OP24_BROADER_SMD",
      "k": 9,
      "effect_measure": "Hedges g (SMD)",
      "estimate": -0.9691,
      "ci_low": -1.8011,
      "ci_high": -0.1371,
      "p_value": 0.02767,
      "tau2": 1.0701,
      "i2": 94.99,
      "model": "REML + Hartung-Knapp",
      "stratum": "Strict + conditional 24-h opioid, Hedges g"
    }
  },
  "md_pool_estimability": {
    "candidate_pool_k": 12,
    "candidate_pool_n": 993,
    "with_estimable_md": 8,
    "with_estimable_smd": 9,
    "unpoolable_units": [
      "Chen 2015",
      "Chen 2015 (Hyperalgesia)"
    ],
    "verdict": "A pooled mean difference across the full candidate pool is NOT estimable. Sim 2002 and Coura 2011 report weight-normalised doses and the v26 lock prohibits reconstructing absolute dose from group-mean body weight; the two Chen 2015 reports are Median/IQR with no derived mean/SD. The broader sensitivity analysis therefore uses the scale-free standardized mean difference, which legitimately pools weight-normalised with absolute-dose endpoints."
  },
  "estimand": {
    "statement": "Between-group difference in cumulative systemic postoperative opioid consumption during the first 24 postoperative hours, harmonised to a common opioid-dose metric where a prespecified and source-supported conversion is possible.",
    "not_equivalent": [
      [
        "POD1",
        "is not necessarily an exact 0–24 h clock window"
      ],
      [
        "mg/kg or µg/kg",
        "is not absolute mg without a defensible individual-level conversion"
      ],
      [
        "rescue-administration count",
        "is not cumulative dose unless the reconstruction is fully justified"
      ],
      [
        "PCA button presses",
        "are analgesic-seeking behaviour, not opioid dose"
      ],
      [
        "mixed analgesic rescue",
        "is not opioid consumption"
      ],
      [
        "a graph-derived value",
        "is not an exact source-reported number"
      ]
    ]
  }
};
