# Amendment — companion reports and the unit of analysis

**Date:** 2026-09-11
**Status:** adopted
**Raised by:** review lead
**Scope:** counting and reporting only. No eligibility criterion, search, outcome
definition, analysis method or effect estimate is changed by this amendment.

## What changed

The review now distinguishes **included reports** from **included studies**, and
reports both:

- **Included reports: 70**
- **Included studies: 69**

Previously the review reported a single figure of 70, which counted reports while
labelling them studies.

## Why

Yeh 2010 and Yeh 2011 are two reports of one three-arm randomised trial of
lumbar spinal surgery: same author team, same population and procedure, same
setting, and the sham arm's figures identical between the papers. Full evidence
and the linkage record are in
`05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md`.

Counting them as two studies would overstate the size of the evidence base and,
if both were ever pooled, would double-count the same participants.

## How this is reported

PRISMA 2020 already separates these quantities — its flow diagram has distinct
boxes for reports of included studies and for studies included in review. The
dashboard's PRISMA panel now states both, and `build-meta.json` carries
`included_studies` alongside `canonical_reports`.

Counts that are genuinely about **records or reports** are unchanged and remain
70, including:

- the identification split (69 via database searching + 1 via citation searching);
- `Study_Master` in the locked v34 workbook, which holds one row per report;
- the study contribution map, which maps reports to analyses.

The locked master data is therefore **not** altered by this amendment. That is
deliberate: the workbook records what the search retrieved, and re-cutting it to
69 rows would misstate the search and break the lock this review relies on.

## Effect on results

None. Neither Yeh report contributes arm-level data to any pooled analysis, so no
effect estimate, confidence interval, heterogeneity statistic or GRADE rating
changes. A validator check
(`t_companion_publications_cannot_double_count`) now fails the build if either
report is ever added to a synthesis without resolving the unit of analysis first.

## Related

- `05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md` — the linkage record
- `99_audit/2026-09-10_placeholder_incident/` — the data-integrity work during
  which the duplication was identified
