# Linked cohort — Yeh, lumbar spinal surgery (Taiwan)

**Decision date:** 2026-09-11
**Decided by:** review lead
**Effect:** two included *reports* describe one included *study*.

## The two reports

| | Report A (retained as the study record) | Report B (companion report) |
|---|---|---|
| Register key | `Yeh 2010` | `Yeh 2011` |
| Citation | Yeh ML, Chung YC, Chen KM, Tsou MY, Chen HH. *Altern Ther Health Med*. 2010;16(6):10–18 | Yeh ML, Chung YC, Chen KM, Chen HH. *Int J Nurs Stud*. 2011;48(6):703–709 |
| PMID / DOI | 21280458 | 21084087 / 10.1016/j.ijnurstu.2010.10.009 |
| Covidence | 823 | 828 |
| Source PDF | `015_PainATHM-2.pdf` | `covidence_828_full_article.pdf` |
| Setting | 4000-bed medical centre, northern Taiwan | 3000-bed medical centre, northern Taiwan |
| Arms as reported | EG1 33 / EG2 30 / CG 31 | AES 30 / Sham 30 / Control 30 |
| Arms in the review's two-arm contrast | 33 / 30 (analysed 63) | 30 / 30 (analysed 60) |

## Identity: how the keys were assigned

**Decided 2026-09-12.** The two locked sheets had disagreed about which key named
which paper. `Study_Master` filed the *Int J Nurs Stud* trial under `Yeh 2010`, on
the strength of an `Identity correction` field reading "Yeh 2010 (ATHM) → Yeh 2011";
`Outcome_Data_AF_LOCK` filed the *Altern Ther Health Med* trial there. Because
`dashboard/data.js` mirrored both, each of its two rows carried one paper's
citation beside the other paper's arm denominators.

`scripts/audit_yeh_identity_convention.py` settles the question by counting the
sides using each file's own numbers — never a label or a filename. The two papers
are separable by their data: *Altern Ther Health Med* reports arms 33/30/31, AES
mean 18.6, PCA pushes 25.3, control 27.2, Table 4, and prints the PCA route as
epidural; *Int J Nurs Stud* reports 30/30/30, mean 19.3, PCA pushes 24.9, control
28.0, Table 3, mg IV morphine.

The count was **15 to 1**:

- **`Yeh 2010` = *Altern Ther Health Med* — 15 files**, including
  `Outcome_Data_AF_LOCK`, `Stata_AF_Long`, `analysis_dataset_locked`,
  `target_F_exploratory`, `opioid_24h_primary`, `Stata_Opioid24_Primary`,
  `AF_Result_Lock`, all five `v34_reconciliation` extracts (among them
  `v34_outcome_data.csv`, the cell-for-cell mirror of the locked workbook), and the
  `07_TIERED_V33` working set.
- **`Yeh 2010` = *Int J Nurs Stud* — 1 file**: `Study_Master` itself.

The review team adopted the majority convention. The `Identity correction` had been
written into one identity sheet and propagated nowhere; re-cutting the other fifteen
would have meant re-cutting the analytical data layer, including inputs to Stata
runs whose logs are committed.

`scripts/apply_yeh_identity_correction.py` applied it to the v34 workbook's
`Study_Master` sheet, its exported CSV, and the register's citation metadata
(`citation`, `doi`, `pmid`, `country_evidence`, `arm1_female`,
`unit_of_analysis_note`). It refuses to run if an arm denominator would move, and
its `--check` mode is asserted on every validation run.

**Nothing analytical changed.** No arm denominator, mean, SD, effect estimate,
RoB 2 judgement or GRADE rating was read or written. Both records remain on
DUPLICATE-OVERLAP HOLD in the lock (`include_strict` = `include_sensitivity` = 0 on
every row), so no synthesis reads either, and the study count of 69 is unchanged
because the pair counts once whichever way the identity resolves.

Two earlier readings on the same day were wrong and are recorded here so they are
not re-raised: the first called it a transposition of arm denominators, the second
an inverted citation. Both looked at one sheet and inferred the other.

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

The analysed denominators differ (63 in `Yeh 2010`, 60 in `Yeh 2011`) because the two papers report different subsets/timepoints of
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
