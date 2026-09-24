# PRISMA and report-to-trial accounting (v36, 16 September 2026)

**Status: count-level arithmetic is reconstructable; record-level PRISMA is NOT reconciled.** The full-text stage is now crosswalked record-by-record from the Covidence exports to the 70-report registry. It shows six post-exclusion re-inclusions that Covidence never recorded, reason categories that do not match the PRISMA figure, and a material risk of missed eligible trials under the registered outcome criteria.

Evidence files: `02_DECISIONS/covidence_record_crosswalk.csv` (224 Covidence full-text records), `02_DECISIONS/registry_report_provenance.csv` (70 reports), `02_DECISIONS/exclusion_rescreen_triage.csv` (161 exclusions). Scripts: `code/crosswalk_covidence.py`, `code/triage_exclusions.py`.

## 1. Three units kept separate

| Unit | Count | Basis |
|---|---:|---|
| Report records in registry | 70 | `source_manifest.json`; all 70 PDF hashes verified |
| Operational trial units | 69 | Yeh 2010 + Yeh 2011 held as one probable-overlap family (not proven the same cohort) |
| Randomized participants, operational count | 12,103 | Sum of source-located randomized totals over 69 units, Yeh family counted once at 99 (lower bound; union unknown, ≤189 if distinct). **This is not an analyzed N, not a review-wide efficacy population, and not a replacement for the unsupported 10,618 KPI.** 68/70 excerpts contain allocation wording; An 2014 (88) and Huang 2017 (80, 4×20) were manually confirmed in v36. |
| Reports contributing to ≥1 current model | 48 | 22 reports contribute to no model (held, excluded construct, or data type) |

## 2. Full-text stage: Covidence ↔ registry

| Path into 70-report registry | Reports |
|---|---:|
| Covidence full-text INCLUDED (63 records; exported titles for Chen 2020, Gu 2019, Jin 2022→Jin 2023 and the second "Yeh 2010" record mapped manually) | 63 |
| Covidence EXCLUDED but in registry: **Gao 2022, Liu 2015, Zhang 2018** (excluded 20 Aug; Zhang 2018 also has a second record "Abstract only", 1 Sep) and **Oztas 2019, Song 2020, Szmit 2021** (excluded "Wrong outcomes", 1 Sep) | 6 |
| No record in either Covidence export: **Wu 2016** (plausibly the PRISMA "citation search" addition; `TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md` lists it as Tan #53, not found in Covidence) | 1 |
| **Total** | **70** |

Szmit 2021 is the **only** contributor to the principal TEAS/sham opioid body. Its Covidence status is still "excluded — wrong outcomes". Its re-inclusion is argued in `TAN_2024_COVIDENCE_RECONCILIATION_AUDIT.md`, and post-lock RoB IDs (`SONG20-POSTLOCK`, `GAO22-POSTLOCK`) show Song and Gao were added post-lock. No dated reviewer decision re-including these six was found.

## 3. Arithmetic against the PRISMA figure

| PRISMA figure (Word file) | Covidence exports | Reconciliation |
|---|---|---|
| Reports sought 224 | 63 included + 161 excluded = 224 | Matches |
| Not retrieved 14 | "Study not retrieved" = 2 | **Unreconciled** at reason level |
| Assessed 210; excluded 141; included 69 | Applying the 6 re-inclusions: 69 included, 155 excluded; 155 − 14 = 141 | Count-level consistent **only if** 12 not-retrieved records carry other reasons (unverified) |
| Exclusion reasons: outcomes 117, setting 9, intervention 9, comparator 3, population 2, design 1, language 0 | Wrong outcomes 122, publication language 12, setting 9, intervention 9, comparator 3, not retrieved 2, population 2, design 1, abstract only 1 | **Unreconciled**. PRISMA shows no language category although 12 records were excluded for publication language on 20 Aug, as the registered protocol requires. |
| Citation search +1 → 70 | Wu 2016 has no Covidence record | Probable; confirm |

Earlier stages (5,100 records → 5,088 studies → 2,928 screened) remain aggregate-only; no record-level export is in the repository (see `ASTRA_PRISMA_RECONCILIATION.md`).

## 4. Completeness risk from outcome-based exclusions

The registered record (20 Aug 2026) admits trials reporting "postoperative opioid consumption **or another eligible outcome**". Additional outcomes include pain, PONV, quality of recovery, GI recovery, length of stay, rescue analgesia and adverse events. In Covidence, 108 "wrong outcomes" exclusions are dated 20 Aug (registration day) and 14 are dated 1 Sep. These dates are consistent with the earlier 14 Aug primary-outcome-focused screening rule still being applied.

Mechanical triage of all 161 exclusions (keyword flags only; 91 full texts retrieved, 70 abstract-only):

| Triage | Records |
|---|---:|
| PRIORITY RE-SCREEN: "wrong outcomes" + intervention term + registered-outcome term, no non-English signal | 84 (66 on full text; 49 also mention randomization and general anaesthesia) |
| RE-SCREEN: "wrong outcomes" + outcome terms, intervention or language unconfirmed | 29 |
| No mechanical flag (reason retained pending confirmation) | 48 |

**These are not eligibility decisions.** Keyword presence cannot establish adult GA population, randomization, physical modality or extractable data. Still, the scale means the current 70-report evidence base cannot be assumed complete for secondary outcomes (PONV, pain, GI recovery, intraoperative opioid). Primary-outcome completeness is not established either: 71 of the 84 PRIORITY records mention an opioid term. Many of those mentions may be anaesthetic-methods text rather than a reported outcome, which is exactly what human re-screening must determine. Dual independent re-screening is required before data lock.

## 5. Report-to-trial identity

- **Yeh 2010 / Yeh 2011:** probable same cohort (identical sham baseline and outcome fingerprints) but discrepant route (epidural vs IV PCA), sessions and arm sizes. Held as one unit, counted once, excluded from all models. Author query drafted, not sent.
- No other shared registry IDs were found across the 70 reports (`ASTRA_VERIFICATION_SUPPORT/cohort_identity_screen.csv`). Yang 2020/2024, Gao 2021/2022, He breast/hepatectomy and Chen 2015/Yao 2015 were judged distinct on registry or population grounds.
- Registry metadata gaps kept as explicit statuses, not defaults: age/sex/BMI/ASA "NOT VERIFIED" for most reports; Wu 2016 surgery not documented; Huang 2017 `arms` field "20 vs 20" is one pairwise slice of a four-arm 80-participant trial.
