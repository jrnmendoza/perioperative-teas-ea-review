# Linked cohort — Yeh, lumbar spinal surgery (Taiwan)

**Decision date:** 2026-09-11
**Decided by:** review lead
**Effect:** two included *reports* describe one included *study*.

## The two reports

| | Report A (retained as the study record) | Report B (companion report) |
|---|---|---|
| Register key | `Yeh 2010` | `Yeh 2011` |
| Citation | Yeh ML, et al. *Int J Nurs Stud*. 2011;48(6):703–709 | Yeh ML, et al. *Altern Ther Health Med*. 2010;16(6):10–18 |
| PMID | 21084087 | 21280458 |
| Source PDF | `covidence_828_full_article.pdf` | `015_PainATHM-2.pdf` |

Note that the register keys invert the publication years; the keys are labels,
not dates.

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

The analysed denominators differ (63 in Report A, 60 in Report B) because the two
papers report different subsets/timepoints of the same cohort — which is what
companion reports do, and is not evidence of two trials.

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
