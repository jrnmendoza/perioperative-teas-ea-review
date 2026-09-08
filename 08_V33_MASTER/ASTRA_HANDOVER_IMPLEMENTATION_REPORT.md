# Astra handover implementation — 8 September 2026

## Findings and corrections

The frozen v33 master remains authoritative: 70 studies, 382 outcome rows,
strict primary k=7. No source values or primary estimates were changed.

Two errors in selection of existing secondary data were corrected:

1. **Wu 2025:** `Source PDFs/103940.pdf`, printed p. 3018 (Randomization and
   Blinding), explicitly places randomization on PACU arrival. Page 3019 places
   the intervention there too. Table 1, p. 3021, labels the intraoperative doses
   as baseline characteristics. Both intraoperative opioid rows therefore
   predate randomization and cannot estimate treatment effects. They remain in
   the frozen master, with a documented exclusion in the analysis-set builder
   and not-pooled register.
2. **Ng 2013:** the defecation model counted the same EA arm against both sham
   and no acupuncture. `covidence_1970_ng_2013.pdf` describes three randomized
   arms, 55 participants each (Methods; Tables 1, 3 and 4). Only EA vs sham is now included, retaining the
   blinded comparison and counting each participant once. The no-acupuncture
   contrast remains in the master and is documented as not pooled. This is a
   correction made after the original analysis, not a claimed prespecified rule.

The secondary Stata do-file was rerun after both selection corrections. Its
complete log is tracked under `08_V33_MASTER/02_STATA/logs/`. The unchanged
primary pipeline was not rerun: no primary inputs or master values changed.
The aggregate master-results synchronization check remains in sync.

## Draft assessment intake

All 18 supplied RoB 2 drafts are staged, with provenance and empty adjudication
fields, in `09_V34_INTAKE/v34_RoB2_Draft.csv`. None is merged into adjudicated
assessments. The result-coverage register also identifies four further
defecation-specific gaps. See `09_V34_INTAKE/README.md` for the outstanding work.

## Dashboard defects

- **C1:** generated and loaded author-inquiry JavaScript restores all 60 records,
  priority filtering and search. No author contact was sent.
- **C2:** four database strategies now load from preserved text verbatim.
  Counts come from source logs. CENTRAL shows 1,698 exported Trials, not 1,706
  mixed Cochrane records. PubMed retains its v0.2 export/non-formal status.
- **C3:** removed orphan patient/I² renderer references. Patient totals remain
  in the existing study-card subtitle; no extra KPI or hardcoded I² was added.
- **C4:** reordered contribution map → pathway → tiered derivability, shortened
  repeated framing and preserved the empty-cell, legacy-reconstruction and
  Zhang withdrawal caveats.
- **C5:** the interactive menu is constrained to quantitative keys generated
  from its dataset. A generated Stata selector exposes all six current secondary
  results and the five available forest plots. It states that global interactive
  filters do not refit those saved analyses, and assigns no GRADE rating. The
  former blanket claim that no trial reported an unavailable endpoint is removed.

New assets are cache-busted, source changes trigger Pages rebuilds, and secondary
figures are copied fresh from Stata output. Build-time regression checks are
additive; none of the existing gates was weakened or replaced.

## Verification

- Frozen-master QC: 26/26.
- Existing dashboard validator: 60/60.
- New handover regression checks: 12/12; 12 isolated mutations each fail only
  their intended check, with original data untouched.
- Browser: all 14 tabs activated without JavaScript errors; named dynamic
  targets populated; all four strategies compared verbatim; inquiry filtering
  and searching exercised; six Stata selections and five images checked.
- Deployment artifact integrity passes; aggregate results remain in sync.
- Relevant primary, tiered and secondary Stata logs contain no `r(nnn);` errors.

## Outstanding work

The completed 17-study extraction return is absent. The supplied audit is an
earlier v32 document with overlapping additions and remaining source-extraction
targets. No v34 master, v34 source-data integration or v34 inferential run is
claimed. Human result-specific RoB 2 adjudication remains required. Existing
source contradictions and publication-overlap questions remain unresolved.

## Reanalysis results

| Analysis | Previous k | Corrected k | Corrected estimate (95% CI) | p |
|---|---:|---:|---|---:|
| Intraoperative remifentanil (MD (ug)) | 9 | 8 | -116.764 (-177.316 to -56.211) | 0.0026 |
| Intraoperative remifentanil (Hedges g) | 9 | 8 | -0.526 (-0.921 to -0.131) | 0.0162 |
| Intraoperative sufentanil (MD (ug)) | 6 | 5 | -0.119 (-2.432 to 2.195) | 0.8937 |
| Time to first defecation (MD (hours)) | 8 | 7 | -4.805 (-7.628 to -1.982) | 0.0059 |
