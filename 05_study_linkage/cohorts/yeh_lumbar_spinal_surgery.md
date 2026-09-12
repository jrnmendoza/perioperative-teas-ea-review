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

> **Correction, 2026-09-12 — which key names which paper is an open question.**
>
> An earlier version of this record said "the register keys invert the publication
> years; the keys are labels, not dates". That is not established, and reading both
> PDFs in full shows the opposite is at least as likely.
>
> The two publications are distinguishable without ambiguity. *Altern Ther Health
> Med* 2010;16(6):10–18 (`015_PainATHM-2.pdf`, PMID 21280458) has five authors
> including Tsou M-Y, was run at a **4000-bed** centre, and reports arms of
> **33 / 30 / 31**. *Int J Nurs Stud* 2011;48(6):703–709
> (`covidence_828_full_article.pdf`, PMID 21084087, DOI 10.1016/j.ijnurstu.2010.10.009)
> has four authors, was run at a **3000-bed** centre, and reports **30 in every arm**.
>
> Register row `Yeh 2010` holds arm denominators 33 / 30 — the *Altern Ther Health
> Med* figures — while citing *Int J Nurs Stud*. Row `Yeh 2011` holds 30 / 30 — the
> *Int J Nurs Stud* figures — while citing *Altern Ther Health Med*. The same
> inversion is visible inside each row without opening a PDF: `Yeh 2010` records
> `arm1_n` 33 beside a female count of 20/30, and `Yeh 2011` records `arm1_n` 30
> beside 22/33.
>
> The arm denominators are the half that traces to the lock (`Outcome_Data_AF_LOCK`
> holds 33/30 and 33/31 under `Yeh 2010`, and 30/30 under `Yeh 2011`), and the
> original extraction records agree with it — `yeh_2010_spinal_aes_full_data_extraction.md`
> is headed *Altern Ther Health Med* and `yeh_2011_covidence_828_full_data_extraction.md`
> is headed *Int J Nurs Stud*, which also makes the key names match the publication
> years. The inverted citation most likely entered via
> `99_audit/consensus_audit_master_log.md`, which labels Covidence #828 — the
> *Int J Nurs Stud* paper — as "Yeh 2010".
>
> **Nothing has been changed.** Deciding whether to move the citations (leaving the
> lock untouched) or the arm data (re-cutting the lock) is a review-team call. It
> does not affect this record's conclusion below, which rests on the two papers
> describing one cohort, not on which key names which paper.

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
