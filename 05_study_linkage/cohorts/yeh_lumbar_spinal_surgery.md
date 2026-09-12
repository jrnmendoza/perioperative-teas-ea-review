# Linked cohort — Yeh, lumbar spinal surgery (Taiwan)

**Decision date:** 2026-09-11
**Decided by:** review lead
**Effect:** two included *reports* describe one included *study*.

## The two reports

| | Report A (retained as the study record) | Report B (companion report) |
|---|---|---|
| Register key | `Yeh 2010` | `Yeh 2011` |
| Citation **as the register currently states it** | Yeh ML, et al. *Int J Nurs Stud*. 2011;48(6):703–709 | Yeh ML, et al. *Altern Ther Health Med*. 2010;16(6):10–18 |
| PMID as stated | 21084087 | 21280458 |
| Arm denominators the row actually holds | 33 / 30 | 30 / 30 |

> **Correction, 2026-09-12 (superseding two earlier corrections the same day).**
>
> An earlier version of this record said "the register keys invert the publication
> years; the keys are labels, not dates". A second correction said the citations
> were on the wrong rows. **Both were wrong**, and the reason is worth stating
> plainly: *the two locked sheets contradict each other about which key names which
> paper*, so no single field in the dashboard can be named as the defective one.
>
> | | `Study_Master.csv` says | `Outcome_Data_AF_LOCK.csv` says |
> |---|---|---|
> | `Yeh 2010` | Covidence **828**, internal ID 1879897280, summary "AES (n=30) 19.3 ± 9.7 vs Sham AES (n=30) 21.6 ± 13.1, MD −2.30" → **Int J Nurs Stud** | Table 4, arms **33/30** and **33/31**, mean 18.6, "mg morphine; source explicitly calls PCA epidural" → **Altern Ther Health Med** |
> | `Yeh 2011` | Covidence **823**, `Identitycorrection: "Yeh 2010 (ATHM) → Yeh 2011"`, summary "EG1 (n=33) 18.6 ± 9.7 vs EG2 (n=30) 21.6 ± 13.1" → **Altern Ther Health Med** | Table 3, arms **30/30**, mean 19.3, control 28.0, "mg IV morphine" → **Int J Nurs Stud** |
>
> The same three numbers — 19.3 ± 9.7 versus 21.6 ± 13.1, MD −2.30 — are filed
> under `Yeh 2010` in `Study_Master` and under `Yeh 2011` in `Outcome_Data_AF_LOCK`.
> That is a direct contradiction inside the locked master, visible from the two
> sheets alone.
>
> `dashboard/data.js` mirrors **both** sheets faithfully, which is exactly why each
> of its rows is crossed within itself: citation, DOI and PMID follow `Study_Master`;
> arm denominators follow `Outcome_Data_AF_LOCK`; and the baseline sex counts follow
> the citation, so `Yeh 2010` holds 20/30 beside `arm1_n` 33 and `Yeh 2011` holds
> 22/33 beside `arm1_n` 30.
>
> The likely origin: `Study_Master`'s `Yeh 2011` row carries an `Identitycorrection`
> recording that the ATHM paper was renamed from "Yeh 2010 (ATHM)" to "Yeh 2011",
> and its `Antigravitystudylabel` still reads "Yeh 2010 (ATHM)". That rename was
> applied to `Study_Master` and never applied to `Outcome_Data_AF_LOCK`.
>
> **Nothing has been changed, and the dashboard is the wrong place to change it.**
> Aligning `data.js` with either sheet would only change which locked sheet it
> contradicts. Resolving this means re-cutting `Study_Master` or
> `Outcome_Data_AF_LOCK` so the two agree — a decision about the locked master, and
> one to weigh carefully because `Outcome_Data_AF_LOCK` is the sheet the analyses
> read.
>
> **This record's conclusion is unaffected.** It rests on the two papers describing
> one cohort, not on which key names which paper, and both Yeh records are on
> DUPLICATE-OVERLAP HOLD in the lock itself (`AFincludestrict = 0`,
> `AFincludesensitivity = 0` on every row), so no synthesis reads either.

## Evidence that these are one study

- **Same author team** — Mei-Ling Yeh, Yu-Chu Chung, Kang-Min Chen, Hsing-Hsia Chen.
- **Same population and procedure** — lumbar / non-traumatic spinal surgery.
  Report B: *"Ninety-nine patients undergoing lumbar spinal surgery were randomly
  assigned to one of three groups."* Report A: *"patients who were scheduled for
  surgery to correct non-traumatic lumbar spine injuries at a 3000-bed medical
  center in northern Taiwan."*
- **Same three-arm design** — acupoint electrical stimulation at true acupoints,
  sham acupoints, and control.
- **Same setting** — a large medical centre in northern Taiwan.
- **Identical sham-arm figures** between the two papers, noted during the RoB 2
  source-linking work (`scripts/build_rob2_source_links.py`).

The analysed denominators differ (63 in the row keyed `Yeh 2010`, 60 in the row
keyed `Yeh 2011`) because the two papers report different subsets/timepoints of
the same cohort — which is what companion reports do, and is not evidence of two
trials. The papers also disagree about the cohort size: the *Int J Nurs Stud*
flow diagram shows 99 assessed, 90 meeting inclusion criteria and 30/30/30
randomised, while *Altern Ther Health Med* states "Ninety-nine patients … were
randomly assigned to one of three groups" with groups of 33/30/31. Neither figure
is used as the trial's randomised N.

## What follows from this

- **Included studies: 69.** **Included reports: 70.** PRISMA 2020 keeps these as
  separate quantities, and the review now reports both.
- Neither report may contribute arm-level data to a synthesis independently;
  doing so would double-count the same participants. Enforced by
  `t_companion_publications_cannot_double_count` in
  `scripts/validate_dashboard.py`.
- Both records stay in the register. Removing Report B would destroy the audit
  trail and misstate how many reports the search actually yielded.
- Neither report currently contributes to any pooled estimate, so **no effect
  estimate changes as a result of this decision**.

## Records affected

`dashboard/data.js`:

- `Yeh 2010` — `companion_report: "Yeh 2011"`
- `Yeh 2011` — `duplicate_report_of: "Yeh 2010"`

Both carry a `unit_of_analysis_note` stating the decision.
