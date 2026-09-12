# Adjudicated — Chen 2015 thyroidectomy pair (Fujian Provincial Hospital)

**Adjudication date:** 2026-09-12
**Question:** do these two reports describe one randomised cohort?
**Answer:** **No. Two separate trials.** Both are retained as independent studies.
**Effect on counts:** none. Included reports stay 70; included studies stay 69.

## Why the pair was flagged

`scripts/build_cohort_overlap_scan.py` flags any two reports sharing a first
author plus country of conduct, surgical specialty and modality, where either the
surgical population matches or an arm denominator is shared. This pair matched on
all four context fields and on the surgical population (elective thyroidectomy),
and sits in two issues of the same journal in the same year. It was flagged for
manual review rather than merged, which is what the scan is for.

## The two reports

| | `Chen 2015` | `Chen 2015 (Hyperalgesia)` |
|---|---|---|
| Citation | *Int J Clin Exp Med* 2015;**8(8)**:13622–13627 | *Int J Clin Exp Med* 2015;**8(4)**:5781–5787 |
| Article ID | IJCEM0010937 | IJCEM0006509 |
| Source PDF | `037_chen_2015_thyroidectomy_lund.pdf` | `040_chen_2015_hyperalgesia_lund.pdf` |
| **IRB approval** | **K2014-12-003** | **K2014-07-003** |
| **Recruitment** | **January 2015 – May 2015** | **August 2014 – December 2014** |
| Trial registration | ClinicalTrials.gov **NCT02333747** | none stated |
| Assessed for eligibility | 91 | 73 |
| Enrolled | 84 | 60 |
| Analysed | 83 (41 / 42) | 59 (29 / 30) |
| Primary outcome | QoR-40 at 24 h | mechanical pain threshold |
| Author list | Chen, **Yang**, Yao, Dai, **Qian**, **Liu** | Chen, Yao, **Wu**, Dai, **Zhao**, **Qiu** |
| Funding | 2015J01373 | 2012Y0012 |

## Evidence that these are two studies

Any one of the first three rows below would settle it; together they are decisive.

- **Separate ethics approvals from the same board.** Report A: *"After obtaining
  ethical approval from Fujian Provincial Hospital (Ref: K2014-12-003)"*.
  Report B: *"approved and oversighted by the Institutional Review Board of
  Fujian Provincial Hospital (Ref: K2014-07-003)"*. One cohort does not carry two
  approval numbers.
- **Non-overlapping recruitment windows.** Report A recruited *"from January 2015
  to May 2015"*; Report B enrolled *"from August 2014 to December 2014"*. Report B
  had finished recruiting before Report A began.
- **Independent screening funnels.** Report A: *"We initially assessed 91 patients
  for eligibility … 3 patients did not meet the inclusion criteria, 4 declined to
  participate, and the remaining 84 patients enrolled"*. Report B: *"We initially
  assessed 73 patients for eligibility … 7 patients did not meet the inclusion
  criteria, 6 declined to participate, and the remaining 60 patients enrolled"*.
  Different screened, excluded, declined and enrolled counts throughout.
- **Report A is prospectively registered and Report B is not.** NCT02333747 covers
  the QoR-40 trial only.
- **Different primary outcomes and different comparator wording** — Report A's
  control arm had *"the apparatus … applied, while electronic stimulation was not"*;
  Report B's sham arm *"had the electrodes applied, but received no stimulation"*.
  Both are sham/placebo arms and both records are correctly classified
  `Sham-Controlled (Placebo Double-Blind)`; the point here is only that the two
  protocols are separately written, not that they differ in kind.
- **Overlapping but not identical author teams**, and separate funding grants.

## What is shared, and why it is not evidence of one cohort

Same first author, same single centre, same procedure, same sex restriction
(female only), same ASA I–II eligibility, same age band (18–60), same device
(HANS-100A), same acupoints (LI4, PC6) and same stimulation parameters
(2/10 Hz, 6–9 mA, 30 min). That is one research group running a consistent
protocol across consecutive trials, which is what the shared-context fields in
the scan are designed to notice — and precisely why the scan flags rather than
merges.

No arm denominator is shared between the two reports (41/42 vs 29/30), which was
already the weaker signal pointing this way before the PDFs were read.

## Records affected

None. Both records stay in the register exactly as they are, and both continue to
count as separate studies. `scripts/build_cohort_overlap_scan.py` now carries this
adjudication so the pair is reported as **resolved — separate cohorts** rather
than as an open flag, and the evidence travels with it.

## Related

- `05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md` — the one pair that *is*
  a single study
- `00_protocol/amendments/2026-09-11_unit_of_analysis_companion_reports.md`
