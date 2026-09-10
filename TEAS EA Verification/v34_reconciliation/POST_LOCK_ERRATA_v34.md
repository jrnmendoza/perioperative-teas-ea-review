# Post-lock errata — v34 extraction dataset

Source-verified corrections identified **after** the v34 extraction dataset was
locked. This register exists so a correction is never applied silently: each
entry records what the source actually says, who verified it, what the locked
dataset currently holds, and whether the correction has been applied.

**Scope of the lock.** `TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx`
is pinned by SHA-256 in `scripts/build_v34_dashboard_data.py`, which aborts the
build on mismatch. `TEAS EA Verification/v34_reconciliation/data/v34_outcome_data.csv`
mirrors that workbook's `Outcome_Data` sheet, and `source_normalized_outcome_rows`
on the dashboard is read from the workbook's own `Summary` sheet. Changing any
one of those without the others produces a silent divergence, so corrections are
recorded here first and applied as a set.

| # | Study | Issue | Status |
|---|---|---|---|
| 1 | Yang 2024 | Nausea 0–24 h result used by an analysis but absent from the dataset | **Applied and re-locked 2026-09-10** |
| 2 | Yang 2024 | Vomiting 0–24 h result mislabelled "Within 72 h" | **Applied and re-locked 2026-09-10** |
| 3 | Szmit 2021 | Nausea window is 24-h-bounded but not explicitly 0–24 h | **Open — no data change; classification note** |
| 4 | — | Stratum label incomplete in a v26 results file | **Open — no data change** |

## Re-lock record — 2026-09-10

Errata 1 and 2 were applied to the master workbook and mirrored into
`v34_reconciliation/data/v34_outcome_data.csv`. Errata 3 and 4 are unchanged and
remain open: neither is a data correction, and neither gated this re-lock.

| | before | after |
|---|---|---|
| workbook SHA-256 | `985dc26a943cf30e1bbdac552a5eb69a6fb2d73fd252d0bc194abbdb8538d6f3` | `b1bfcfb59b28f88102a443cc350b98c46eb73743e3c951fce125813cfcdff66d` |
| `Outcome_Data` rows | 757 | 758 |

The pre-errata workbook is preserved in git history at commit `5aa94f2`, which
is the authoritative copy:

```bash
git show 5aa94f2:"TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx" > pre_errata.xlsx
```

The patcher also writes a working copy next to the master as
`TEAS_EA_RECONCILED_MASTER_DATA_v34_PRE_ERRATA_BACKUP.xlsx`. That copy is left
untracked on purpose: committing a 2.1 MB byte-duplicate of a file git already
stores would bloat the repository without adding recoverability.

**No published estimate changed.** The 10 GRADE-rated v34 models, the RoB 2
rollup and all 22 interpretation records were regenerated and are identical;
the interpretation layer's staleness check reported 0 stale records. That is the
expected result — `TD_NAUSEA_0_24H` is a v26 analysis, not one of the manifested
v34 models, and it had already been computed from these values. What changed is
that the dataset now *contains* the result the analysis consumed.

### A defect found during the re-lock, and what it means for erratum 2

The first application of `apply_post_lock_errata.py` corrected only **half** of
erratum 2. The script substituted literal XML fragments, and the cell holding the
machine-readable time class is `<x:c r="BI55" s="102" t="str">` — the style
attribute was missing from the literal, so that substitution matched nothing. A
single guard covered both substitutions, so the successful `G55` edit satisfied
it, and `verify()` checked only the human-readable `Timepoint/window` field. The
workbook would have gone out with `Timepoint/window` = "0-24 h after surgery"
and `V34 time class` = "within 72h" — internally contradictory, and wrong in
precisely the field a window filter reads.

This was caught by comparing the patched workbook against the CSV rather than
trusting the script's own "verified" line. The script now matches cells by
reference with the attributes preserved, asserts each substitution independently,
and verifies both fields. The corrected workbook hashes to `b1bfcfb5…`; the
incomplete one hashed to `0079f7f3…`, which is the value printed in this
register's earlier dry-run notes and in any working copy taken before
2026-09-10 — **that hash should not be trusted or restored.**

---

## Erratum 1 — Yang 2024 postoperative nausea, 0–24 h: result missing from the dataset

**Verified 2026-09-10** by direct reading of the source PDF
(`TEAS EA Verification/Source PDFs/covidence_1930_full_article.pdf`;
Drive: `https://drive.google.com/file/d/160N3psd5tLEphwXHJzUEZ3uJfaIXcs5V/view?usp=drivesdk`).
Independently reported by a second reviewer and confirmed against the primary
source by this pipeline before recording.

**What the source says.** Methods:

> "Incidence of PON and POV (defined as at least one episode of nausea or
> vomiting that occurred), pain at rest and on movement were recorded at
> 0–24 h, 24–48 h and 48–72 h after surgery."

Table 3, under the heading **"0–24 h after surgery"**:

> "Incidence of Nausea [n(%)] — 24(26.7) [EA] · 40(44.4) [UC] · P = 0.013"

Both arms are n = 90, retained in the intention-to-treat analysis.

**The problem.** The pooled nausea 0–24 h analysis (`TD_NAUSEA_0_24H`,
RR 0.603 [0.303, 1.203], k = 3) lists Yang 2024 as a contributing trial and its
Stata result is consistent with these counts — but the locked extraction dataset
contained **no nausea row for Yang 2024 at all**, only morphine, flatus,
defecation and vomiting.

**Materiality.** No published estimate is wrong: the analysis already used these
values. This is a completeness and traceability defect — the dataset does not
contain a result the review's own analysis consumed.

**Correction applied.** New row (`V34-OD-0759`, comparison ID
`YANG24_EA_vs_UC_NAUSEA24`): Postoperative nausea, 0–24 h after surgery,
events 24/90 (EA) vs 40/90 (usual care), reported P = 0.013, RR 0.60,
`SOURCE-VERIFIED`, RoB 2 status `ROB2_RESULT_SPECIFIC_PENDING` — no
result-specific RoB 2 judgement exists for this result yet, and none is invented
here.

---

## Erratum 2 — Yang 2024 postoperative vomiting: window mislabelled

**Verified 2026-09-10**, same source.

**What the locked dataset held.** Row 55 (`YANG24_EA_vs_UC_VOMIT`), events
12/90 vs 25/90, reported P = 0.016, `Timepoint/window` = **"Within 72 h"**,
`V34 endpoint time class` = "within 72h".

**What the source says.** Table 3 reports vomiting separately for each interval:

> 0–24 h after surgery — "Incidence of Vomiting [n(%)] — 12(13.3) · 25(27.8) · P = 0.016"
> 24–48 h after surgery — "6(6.7) · 10(11.1) · P = 0.295"
> 48–72 h after surgery — "0(0) · 0(0)"

and the Results text confirms it independently:

> "the incidence of 0–24 h POV (13.3%) in Group EA was significantly lower than
> that in Group UC (27.8%)."

**Decisive detail.** The stored counts (12 / 25) and the stored P (0.016) match
the **0–24 h** interval exactly; the 24–48 h interval is 6 / 10 with P = 0.295.
The values in the dataset were always the 0–24 h values — only the window label
was wrong.

**Consequence — an earlier concern is withdrawn.** Before the source was read it
appeared that Yang 2024 might have to be removed from `TD_VOMIT_0_24H` under the
same standard applied to Zhang 2025 (whose POD-1 endpoint is not an explicit
0–24 h clock window). That does **not** apply here: Yang 2024 reports an
explicit, interval-specific 0–24 h endpoint and legitimately belongs in that
analysis. No analysis is withdrawn as a result of this erratum.

**Correction applied.** `Timepoint/window` → "0-24 h after surgery";
endpoint time class → "0-24h". No counts, denominators or P value changed.

---

## Erratum 3 — Szmit 2021 nausea: window is bounded at 24 h but not explicitly labelled

**Status: open. No data change.** Recorded as a classification question for the
review team, not a correction.

Szmit 2021 contributes nausea 0/24 (TEAS) vs 4/24 (sham) — the randomised
TEAS-vs-sham contrast; the third arm is PCA-only control (2/23) and is not the
relevant comparison here. The dataset records the window as "Postoperative
observation period; PCA/TEAS discontinued at 24 h".

The paper describes adverse events as recorded "during the postoperative
observation period", and separately establishes that "The PCA therapy and
TEAS/sham were discontinued at 24 h". The observation period is therefore
demonstrably bounded at 24 h, but the endpoint is not itself labelled 0–24 h in
the way Yang 2024 ("0–24 h after surgery") and Ma 2026 ("within 24 hours after
surgery") are.

**Why this is left open rather than decided here.** The review applied a strict
explicit-clock-window standard when it withdrew Zhang 2025 from the 0–24 h
opioid analyses. Whether Szmit 2021 meets that same standard for nausea is a
methodological judgement for the review team, not a data question. If the strict
reading is adopted, `TD_NAUSEA_0_24H` should carry a sensitivity analysis
excluding Szmit 2021; if the bounded-observation-period reading is accepted, the
window should be described as 24-h-bounded rather than as an explicit 0–24 h
endpoint.

---

## Erratum 4 — stratum label incomplete in a results file

**Status: open. No data change.** `TD_NAUSEA_0_24H` is reported with k = 3 and
an identical pooled estimate (RR 0.6035) in both results files, but the named
studies disagree:

- `06_FINAL_ANALYSIS_V26/03_RESULTS/master_reconciled_results_v26.csv` —
  "Nausea 0-24h (Yang 2024, Ma 2026, Szmit 2021)" ✓ complete
- `06_FINAL_ANALYSIS_V26/03_RESULTS/results_targetD_ponv.csv` —
  "Nausea 0-24h (Yang 2024, Ma 2026)" — two names for a k = 3 analysis

The second label is incomplete rather than describing a different analysis. Both
files are v26 analysis outputs and are not edited here.

---

## Known upstream caveat

`TEAS EA Verification/v34_reconciliation/code/reconcile.py` generates
`v34_outcome_data.csv` from the **v33** locked workbook. The Yang 2024 nausea
omission originates upstream, in that v33 source. Errata 1 and 2 are therefore
applied to the v34 workbook and its mirrored CSV **only** — re-running
`reconcile.py` against the unmodified v33 source would reintroduce the
omission and the wrong window label.

This is recorded rather than silently worked around. Resolving it properly means
either correcting the v33 source as well, or adding an explicit post-lock
correction step to `reconcile.py` that applies this register. That decision
belongs with the review lead.

### Guarded, 2026-09-10 — the decision is still open, the risk is not

The decision above is unchanged and still the review lead's. What changed is
that a re-run can no longer quietly undo the corrections while that decision is
pending.

The applied entries are now also declared machine-readably in
`data/post_lock_errata.json`, and two independent guards read it:

1. **`reconcile.py` refuses to write.** Before writing any output it checks its
   own reconstructed `Outcome_Data` against the register. Running it today
   aborts with exit status 1, naming all three reverted fields, and writes
   nothing — confirming empirically that a plain re-run *would* have reverted
   this re-lock.
2. **`validate_dashboard.py` checks the artefacts on disk**
   (`t_post_lock_errata_still_applied`). This catches the case the first guard
   cannot: a regeneration of the workbook *and* the CSV together. Both defects
   originate upstream, so a clean rebuild reproduces them consistently in both
   places, every mirror check still passes, and only an assertion about the
   corrections themselves notices. Both guards are mutation-tested against
   exactly these scenarios.

Neither guard applies a correction or decides anything. They fail loudly instead
of choosing on the review lead's behalf.

Two unrelated reproducibility defects in `reconcile.py` were fixed at the same
time. It read the consolidated source-PDF audit from `/Users/ryan/Downloads/`,
an unversioned path that does not exist on any other machine, even though the
script itself had preserved a git-tracked copy in `inputs/`; it now reads the
tracked copy. And that input carried no integrity check, so a different file at
that path would have been reconciled without complaint — its SHA-256 is now
asserted the same way the v33 workbook's already was.
