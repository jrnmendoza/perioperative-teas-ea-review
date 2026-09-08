# Extraction task — perioperative TEAS/EA systematic review (v33 gap-fill)

You are performing **source data extraction** for a Cochrane-style systematic
review and meta-analysis of perioperative transcutaneous electrical acupoint
stimulation (TEAS) and electroacupuncture (EA). You have the full-text source
PDFs. I have a locked master dataset (v33) that already contains some outcomes
from these trials; I need the ones it is still missing.

Your output will be ingested mechanically into a locked analysis dataset. Accuracy
and honesty about what is *not* reported matter more than completeness.

---

## PART 0 — THE RULES (read before extracting anything)

These are not stylistic preferences. A single violation contaminates a locked
meta-analysis, so I would rather receive 20 correct rows than 60 rows where a
few were inferred.

### Absolutely prohibited

1. **Do not invent, estimate, infer, interpolate, or "reasonably approximate"
   any number.** If a value is not printed in the paper, the answer is
   `NOT REPORTED`.
2. **Do not read values off a graph.** If an outcome appears only in a figure
   and not in text or a table, record it as `GRAPH ONLY` with the figure number.
   Do not estimate the bar height, the axis position, or the error bar.
3. **Do not convert medians/IQRs into means/SDs.** Report exactly the statistic
   the paper reports. Do not apply Wan, Luo, Hozo, or any similar transformation.
4. **Do not convert anything into morphine milligram equivalents (MME).** Do not
   multiply counts by doses. Do not multiply mg/kg by a body weight. Do not
   convert PCA solution volume into drug mass. Report the native unit.
5. **Do not treat a count of rescue doses as a drug dose**, or a number of PCA
   button presses as drug delivered, or a PCA reservoir volume as consumption.
6. **Do not merge arms** of a multi-arm trial, and do not collapse a control arm
   that is shared between comparisons. Report each arm separately with its own N.
7. **Do not fill a blank with a value from the abstract if the table differs** —
   see Part 3: report both and flag the conflict.
8. **Do not report a percentage without its numerator and denominator.** If the
   paper gives only "23.3%", give me `23.3% of N=30` and put the raw count as
   `NOT REPORTED` unless the count is printed.
9. **Do not silently change a time window.** "POD1" is not "0–24 h" unless the
   paper explicitly defines it as a 24-hour clock window from end of surgery. If
   the paper says POD1, write POD1.

### Required for every row

- The **exact arm N used for that specific analysis** (not just the randomised
  N). If the analysed N differs from the randomised N, give both.
- A **verbatim quote** of the sentence, table row, or cell you took the numbers
  from — copied character-for-character, including the punctuation.
- The **page number** and the **table or figure number** (e.g. "p. 419,
  Table 2, row 'Duration Remifentanil (ug)'").
- Whether the analysis is **ITT, per-protocol, available-case, or unstated**.
- Any **ambiguity, inconsistency, or oddity** you noticed, even if minor.

### When something is missing

Use exactly one of these strings in the value field:

| String | Meaning |
|---|---|
| `NOT REPORTED` | The paper does not report this outcome at all |
| `GRAPH ONLY` | Reported only in a figure; no numeric value in text/table |
| `NO VARIANCE` | Point estimate given but no SD/SE/IQR/CI |
| `NO DENOMINATOR` | Percentage or count given but the N for that analysis is unclear |
| `AMBIGUOUS` | Reported, but the metric/unit/window is not defined well enough to use |

Never leave a cell blank and never write "N/A", "~", "approx", or a guess.

---

## PART 1 — OUTPUT FORMAT

Return **one CSV code block**, comma-separated, with a header row and these
exact columns in this exact order. Quote any field containing a comma.

```
study,outcome_family,outcome_result,timepoint_window,intervention_arm,comparator_arm,randomized_n_int,randomized_n_comp,analyzed_n_int,analyzed_n_comp,statistic_type,value_int,dispersion_int,value_comp,dispersion_comp,events_int,events_comp,unit_scale,reported_p,effect_estimate_as_printed,analysis_population,page,table_or_figure,verbatim_quote,ambiguity_notes
```

Field notes:

- `statistic_type` — one of: `Mean/SD`, `Mean/SE`, `Median/IQR`, `Median/range`,
  `Events/total`, `Percentage only`, `Graph only`, `Other (describe)`.
- `value_int` / `value_comp` — the mean or median. Leave the dispersion columns
  for the SD, SE, IQR or range **as printed** (e.g. `1.5` or `2–7.8` or
  `95% CI 0.31 to 0.88`).
- `events_int` / `events_comp` — raw event counts for binary outcomes only.
- `unit_scale` — e.g. `VAS 0-10`, `NRS 0-10`, `hours`, `minutes`, `days`,
  `mg tramadol`, `QoR-15 points`, `participants`.
- `reported_p` — exactly as printed (`0.04`, `<0.001`, `NS`, `NOT REPORTED`).
- `effect_estimate_as_printed` — any MD/RR/OR/HR with CI the paper itself gives.
- `analysis_population` — `ITT`, `Per-protocol`, `Available-case`, `Unstated`.
- One row per **arm-pair per timepoint**. A three-arm trial with two active arms
  against one control at two timepoints produces four rows.

After the CSV, add a short prose section per study listing anything that did not
fit the schema, plus any concern about the trial's reporting.

---

## PART 2 — WHAT TO EXTRACT, BY STUDY

For each study below I list **what I already have** (do not re-extract these —
they are locked and verified) and **what I need**. If an outcome I list as
needed turns out not to exist in the paper, say so explicitly with
`NOT REPORTED`; that is a useful answer, not a failure.

Extract **every timepoint the paper reports** for the outcomes requested, not
just the one I name — if a paper reports pain at 1, 6, 12, 24 and 48 h, I want
all five rows.

---

### 1. Zhu 2022 — *Acupunct Med* 2022;40(5):415–424
Preoperative EA for PONV in laparoscopic gynaecological surgery. Four arms:
Group Pre (n=101), Group 30 (n=98), Group Comb (n=100), Group Usual (n=101),
per-protocol of 413 randomised / 400 completed.

**Already have:** postoperative nausea and vomiting at 6–24 h (all three active
arms vs usual care); intraoperative sufentanil and remifentanil (all three arms).

**Need:** 24-h movement pain (NRS); early postoperative pain at every reported
timepoint; QoR-15 at every reported timepoint; rescue analgesic requirement;
rescue antiemetic requirement (reported at 0–6 h and 6–24 h); time to first
flatus; nausea and vomiting at 0–6 h if reported separately; PONV severity
scores.
**Note:** report all three active arms separately against Group Usual.

---

### 2. Yang 2020 — *Med Sci Monit* 2020 (EA, thoracoscopic surgery)
59 randomised (EA 30 / UC 29), 57 completed; analysed 29/28.

**Already have:** time to first flatus (20.8±4.6 vs 24.1±6.2 h); time to first
defecation (53.9±6.0 vs 57.5±7.2 h).

**Need:** postoperative pain intensity at every reported timepoint; PONV
incidence and severity; duration of hospital stay; abdominal distension
incidence and severity; rescue medication use.

---

### 3. Pan 2023 — *J Pain Res* 2023;16 (TEAS, laparoscopic myomectomy)
105 randomised; Group T N=52, Group C N=53.

**Already have:** time to first flatus; intraoperative remifentanil
(740.1±276.9 vs 854.0±287.5 µg).

**Need:** 24-h movement pain; resting pain at every reported timepoint; QoR-40
(total and, if printed, subscales) at every reported timepoint; postoperative
analgesic/rescue use; vomiting and nausea incidence; length of stay; time to
ambulation or other recovery endpoints.

---

### 4. Lu 2022 — TEAS + ERAS
**Already have:** time to discharge criteria; first flatus; first defecation;
PCA attempts at 24 h; successful PCA deliveries at 24 h.

**Need:** resting pain and coughing pain at 24, 48 and 72 h; QoR-15 at 24, 48
and 72 h; PONV incidence; any other recovery endpoints reported numerically.

---

### 5. Li 2021 — Perioperative TEAS
**Already have:** time to first bowel motion by auscultation; time to first
flatus; GI dysfunction (no bowel sounds >48 h, 26/140 vs 44/140); VAS ≥4 at 6 h
(30/140 vs 50/140).

**Need:** PONV incidence at **all six** reported postoperative timepoints (give
each interval separately with its own numerator/denominator); pain at every
other reported timepoint (VAS scores and/or VAS≥4 counts); hospital length of
stay.

---

### 6. Gu 2019 — Long-duration TEAS, PCIA
**Already have:** VAS pain at 24 h; time to first bowel sounds, flatus,
defecation; cumulative PCIA solution consumed at 4 h, 8 h and 36 h.

**Need:** PONV incidence 0–24 h (and any other interval reported); nausea and
vomiting separately if reported; rescue antiemetic use.
**Critical:** the 24-hour PCIA consumption value appears to exist **only in
Figure 4**. If so, report it as `GRAPH ONLY` — do **not** estimate it from the
figure. If a numeric 24-h value does appear anywhere in the text, tables or
supplementary material, quote it verbatim; that would be a significant finding
for us.

---

### 7. Huang 2025 — Postoperative EA + ERAS
**Already have:** time to first flatus (36.4±8.0 vs 42.2±8.5 h); time to first
defecation (46.0±8.0 vs 51.3±9.4 h).

**Need:** pain VAS at every reported timepoint; ketorolac rescue analgesic use
(**note: ketorolac is an NSAID, not an opioid — report it as ketorolac, in mg or
as a count, and do not convert it**); vomiting and nausea incidence; QoR-40;
length of stay; postoperative bowel obstruction incidence.

---

### 8. Gao 2021 — Multicentre TEAS, 610 randomised (TEAS 303 / Sham 307)
**Already have:** postoperative paralytic ileus (98/303 vs 126/307); time to
first flatus; time to first defecation; time to resume normal diet.

**Need:** abdominal pain (incidence and/or score); nausea incidence; vomiting
incidence; time to first bowel sounds; any other GI recovery endpoint; pain
scores at every reported timepoint; length of stay.

---

### 9. Jiang 2026 — Perioperative TEAS
**Already have:** time to first flatus (both the primary and the modified-ITT
analysis); PONV within 24 h (44/294 vs 67/293); intraoperative remifentanil.

**Need:** time to first defecation; abdominal distension; postoperative length
of stay; all additional pain results at every reported timepoint; any rescue
analgesia data.

---

### 10. Wang 2023 — Nighttime TEAS
**Already have:** cumulative additional rescue-analgesia doses 0–72 h
(0.53±0.55 vs 0.98±0.96); time to first flatus.

**Need:** resting pain and activity pain at 24, 48 and 72 h — **note that our
records suggest these may be graph-only; if so say `GRAPH ONLY` with the figure
number**; postoperative adverse events; hospital stay; sleep quality (PSQI/AIS)
if reported numerically rather than only in a figure.

---

### 11. Tu 2024 — Postoperative TEAS
**Already have:** vomiting at 2–6 h (8/57 vs 17/58) and 6–24 h (11/57 vs 15/58);
VAS pain at 6–24 h; any rescue tramadol use within 24 h (3/57 vs 6/58).

**Need:** nausea severity at 0–2 h, 2–6 h and 6–24 h (give the scale and whether
it is a score or a count); rescue metoclopramide use by interval; vomiting at
0–2 h if reported; pain at other intervals.

---

### 12. Sun 2017 — Four-arm TEAS timing trial
Arms: preoperative true TEAS only; preoperative + intraoperative; preoperative +
postoperative; all-period sham (SSS) as the shared control.

**Already have:** activity-evoked VAS at 24 h for all three active arms vs SSS.

**Need:** additional pain timepoints (1 h, 6 h, 48 h and any others), for **each
active arm separately vs SSS**; PONV components (nausea, vomiting, retching)
with counts and denominators; recovery times; supplemental analgesic use with
raw counts if printed (we currently hold only percentages: 11.0%, 15.4%, 7.9%
vs 23.3% — **the raw numerators and denominators would be valuable**).

---

### 13. Sim 2002 — EA vs placebo EA, PCA morphine
**Already have:** cumulative PCA morphine 0–24 h (preoperative and postoperative
EA arms, in mg/kg); PCA morphine 6–12 h; intraoperative alfentanil rate.

**Need:** resting pain at 6, 12, 18 and 24 h and the 24-h mean; PONV incidence;
opioid-related adverse effects (pruritus, sedation, respiratory depression)
with counts and denominators; **the mean body weight of each arm if printed**
(for documentation only — I will not use it to convert mg/kg to mg).

---

### 14. Lu 2021 — Post-mastectomy TEAS, two active arms
Arms: Combined PC6+CV17 TEAS (n≈190); Single PC6 TEAS (n≈198); Sham (n≈188).

**Already have:** chronic pain at 6 months (both arms); total intraoperative
remifentanil (both arms); any PONV at 24 h (both arms).

**Need:** resting and coughing pain at every reported timepoint, **each active
arm separately vs sham**; rescue analgesia use; nausea and vomiting severity
(not just incidence); recovery times; acute postoperative pain scores.

---

### 15. Long 2025 — Perioperative electrical acupoint stimulation
**Already have:** PND at POD1 and POD3; VAS pain at 24 h; PCIA solution
consumption at 48 h; PCIA compression count at 48 h; PONV incidence.

**Need:** hospital length of stay; VAS at every other reported timepoint;
PCIA solution consumption and compression counts at **24 h** if reported
separately from 48 h.
**Note:** the denominators in this trial appear inconsistent (event counts vs
printed percentages disagree). Please report the exact denominator printed in
each table header and flag any mismatch you find.

---

### 16. Wang 2024 — TEAS within PONV risk strata
Two strata, each with its own control: SNVP (simple) and MNVP (moderate).

**Already have:** PONV incidence at 6–12 h and 12–24 h (SNVP); 0–2 h and 2–6 h
(MNVP); any PONV 0–36 h (both strata); intraoperative sufentanil (both strata).

**Need:** interval-specific **vomiting** wherever reported separately from
combined PONV, in both strata; nausea separately if reported; rescue antiemetic
use; pain scores.
**Note:** keep SNVP and MNVP strictly separate — they are different patients
with their own control arms.

---

### 17. Zheng 2025 — Perioperative TEAS
**Already have:** any PONV within 24 h (18/42 vs 29/43); total intraoperative
remifentanil (233.1±29.6 vs 289.5±37.9 µg); total PCIA button presses
(6.3±2.2 vs 10.7±3.9).

**Need:** 24-h resting pain NRS; pain at every other reported timepoint;
**the exact PCIA pump duration** (our record says it is not stated — please
confirm or find it); rescue analgesia; recovery endpoints.

---

## PART 3 — TWO ADJUDICATION TASKS

These are not extractions. Two papers contradict themselves and I need a careful
second reader to characterise the contradiction precisely. **Do not resolve it
by picking the value you think is right** — report exactly what each location
says.

### A. Yu 2020 — *Trials* 2020;21:43

I have found what appears to be an internal inconsistency in the VAS results.
Please check every location in the paper (abstract, Results text, Table 2, any
figure, any supplementary file) and report **verbatim** what each one says for:

1. TEAS group VAS at T1 (postoperative day 1) — value and dispersion
2. TEAS group VAS at T2 (postoperative day 2) — value and dispersion
3. Control group VAS at T1 and T2
4. The **P value** for the T1 comparison and for the T2 comparison

What I believe I am seeing (please confirm or refute independently — do not
simply agree with me):
- Table 2 gives TEAS 3.70 (1.53) at T1 and 1.83 (0.98) at T2
- The abstract gives 3.70 ± 1.41 and 1.83 ± 0.88
- The Results text says "P = 0.042 and P = 0.26 for T1 and T2, respectively"
- Table 2 marks both timepoints with an asterisk defined as P < 0.05

Also note whether Table 2's TEAS SD at T1 is identical to the control SD, and
whether the paper reports the QoR-40 at T2 and the MMSE with dispersions.

### B. Liang 2021 — TEAS for catheter-related bladder discomfort (TURP)

The paper reports "postoperative analgesia requirement" as **3.8 (1.9) vs
5.0 (2.9), P = 0.045**, and describes it in the text as "the number of patients
who required extra analgesia". A count of patients out of 35 per arm cannot be
3.8 with a dispersion of 1.9.

Please determine from the full text, tables, methods and any supplement:
1. What is this outcome actually measuring — a count of patients, a number of
   analgesic doses, a dose in mg, a score, or something else?
2. What drug was used for rescue analgesia, and at what dose?
3. Over what time window was it measured?
4. Is the dispersion an SD, an SE, or an IQR?
5. Does the Methods section define this outcome anywhere?

If the paper genuinely never defines it, say so plainly — that is the answer I
expect and it is what I will act on.

---

## PART 4 — HOW TO WORK

1. Open each PDF and read the Methods for outcome definitions and time windows
   **before** reading the results tables. Many errors come from assuming a
   timepoint label means what it sounds like.
2. Take values from **tables in preference to the abstract**, but check both and
   report any disagreement.
3. Check for supplementary material; several of these trials put interval-level
   data there.
4. For every trial, note the **CONSORT flow**: randomised, excluded, analysed
   per arm. I need the analysed N, not the randomised N, for each outcome.
5. Work study by study. Do not batch-guess.

If you are uncertain about anything — a unit, a window, whether two numbers
refer to the same thing — put it in `ambiguity_notes` rather than resolving it
silently. Flagged uncertainty is useful to me; a confident wrong number is not.

Finish with a summary table: for each of the 17 studies, how many rows you
extracted, how many outcomes were `NOT REPORTED`, how many were `GRAPH ONLY`,
and any trial you think has a reporting problem worth contacting the authors
about.
