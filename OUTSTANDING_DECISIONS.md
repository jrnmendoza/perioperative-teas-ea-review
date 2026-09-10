# Outstanding decisions — perioperative TEAS/EA review

For the review lead and second reviewer. Six items. None is a coding task; each
needs a human judgement that the pipeline deliberately refuses to make on your
behalf. Each one below states the question, what the review's own evidence says,
the options, and what changes under each.

Prepared 2026-09-10 against commit `ee5f8f1`. Dashboard:
https://jrnmendoza.github.io/perioperative-teas-ea-review/

---

## 1. Nausea and vomiting are pre-specified separately, and are not reported

**This is the item to decide first.** It was found while preparing this brief and
it changes a decision already taken.

The PROSPERO record's Additional outcomes state, verbatim:

> "Postoperative nausea, vomiting, **or** composite PONV during 0-24 hours,
> 0-48 hours, and the longest reported interval."

So nausea alone and vomiting alone are pre-specified outcomes, not merely
components of the composite. The review currently computes them and does not
report them:

| Analysis | k | Estimate | Currently recorded reason |
|---|---|---|---|
| Nausea 0–24 h | 3 | RR 0.60 [0.30, 1.20] | "component of a reported composite" |
| Vomiting 0–24 h | 2 | RR 0.58 [0.02, 13.37] | "component of a reported composite" |
| Nausea 0–48 h | 1 | RR 0.46 [0.30, 0.69] | "single trial" |
| Vomiting 0–48 h | 1 | — | "single trial" |

The "component of a composite" reason was recorded before the protocol was
checked on this point. Against a protocol that pre-specifies them separately, it
is a weaker justification than it appeared, and this is exactly the pattern
PRISMA item 21 asks about.

Note the direction: nausea 0–24 h and nausea 0–48 h both favour the
intervention, and nausea 0–48 h excludes the null. Not reporting pre-specified
outcomes that favour the intervention is not a conflict-of-interest problem, but
it is still selective outcome reporting, and a reviewer who reads the protocol
will ask.

**Options**

- **(a) Report them as pre-specified secondary outcomes.** Most defensible. They
  would need GRADE ratings, which do not currently exist for them.
- **(b) Keep them unreported and state a defensible reason.** The protocol
  permits reporting the composite *or* the components ("or"), so choosing the
  composite is arguably within it — but the reason recorded must then say that,
  not "component of a composite".
- **(c) Report the 0–24 h analyses only** and leave the k = 1 rows as single
  trials.

**Recommendation:** (a) or (c). Under (b) the wording of the reason has to change
regardless — the current text does not survive contact with the protocol.

**What I need from you:** which option, and if (a) or (c), confirmation that
GRADE should be computed for the newly reported outcomes.

---

## 2. "Target A–F" — the labels, not the legitimacy

I had this recorded as an open question about whether these analyses have a
standing methodological role. **Reading the PROSPERO record answers it: they all
do.** Every one maps to a pre-specified Additional outcome:

| Internal label | Analysis | PROSPERO Additional outcome |
|---|---|---|
| Target A | 0–48 h opioid | "Cumulative postoperative opioid consumption during 0-48 hours" |
| Target B | 0–72 h opioid | "…0-72 hours" |
| Target C | Pain at rest, 24 h | "Pain at rest and during movement at approximately 6, 24, 48, and 72 hours" |
| Target D | PONV 0–24 h / 0–48 h | "Postoperative nausea, vomiting, or composite PONV during 0-24 hours, 0-48 hours" |
| Target E | Time to first flatus | "gastrointestinal recovery" |
| Target F | Intraoperative remifentanil | "Intraoperative opioid consumption" |
| Target F | Rescue opioid | "Need for rescue analgesia" |

The word "Target" appears **zero times** in the locked protocol scope and zero
times in PROSPERO. It is internal working vocabulary that has leaked into the
Summary of Findings.

**Options**

- **(a) Rename throughout** to the protocol's own wording, presented as
  secondary outcomes.
- **(b) Keep the labels** and add a mapping table showing each Target's
  pre-specified origin.

**Recommendation:** (a) for the manuscript, (b) for the dashboard, where the
labels are load-bearing in file names and analysis IDs. A reader should never
have to learn a private taxonomy to check a pre-specified outcome.

**What I need from you:** approval to rename in manuscript-facing surfaces. I
would not touch analysis IDs.

---

## 3. Szmit 2021's nausea window (post-lock erratum 3)

Szmit 2021 contributes nausea 0/24 (TEAS) vs 4/24 (sham). The paper records
adverse events "during the postoperative observation period" and separately
states that "PCA therapy and TEAS/sham were discontinued at 24 h". The
observation period is therefore demonstrably bounded at 24 h, but the endpoint
is not labelled 0–24 h the way Yang 2024 ("0–24 h after surgery") and Ma 2026
("within 24 hours after surgery") are.

This matters because the review already applied a strict explicit-clock-window
standard once, when it withdrew Zhang 2025 from the 0–24 h opioid analyses.

**Options**

- **(a) Strict reading** — Szmit 2021 does not meet the same standard.
  `TD_NAUSEA_0_24H` then needs a sensitivity analysis excluding it (k drops 3 → 2).
- **(b) Bounded-observation reading** — accept it, and describe the window as
  24-h-bounded rather than as an explicit 0–24 h endpoint.

**Recommendation:** none. This is a consistency judgement about your own
standard, and I should not make it. I will note that (a) is the reading
consistent with how Zhang 2025 was treated.

**What I need from you:** (a) or (b), and if (a), whether the sensitivity
analysis should be computed now.

---

## 4. An incomplete stratum label in a v26 results file (erratum 4)

`TD_NAUSEA_0_24H` is reported with k = 3 and an identical pooled estimate in two
results files, but they name different studies:

- `master_reconciled_results_v26.csv` — "Nausea 0-24h (Yang 2024, Ma 2026, Szmit 2021)" ✓
- `results_targetD_ponv.csv` — "Nausea 0-24h (Yang 2024, Ma 2026)" — two names for a k = 3 analysis

The second label is incomplete, not a different analysis. No estimate is
affected. It is untouched only because both files are v26 analysis outputs and
this pipeline does not edit those without sign-off.

**What I need from you:** permission to correct the label in
`results_targetD_ponv.csv`, or a decision to leave it and note it. Two minutes
either way.

---

## 5. The v33 upstream source (known upstream caveat)

`reconcile.py` regenerates the v34 extraction dataset from the **v33** workbook.
Both corrections applied in the 2026-09-10 re-lock — Yang 2024's missing nausea
row, and its mislabelled vomiting window — originate upstream in that v33 source,
so a plain re-run would silently reintroduce both.

That risk is now contained: `reconcile.py` aborts with exit 1 and writes nothing,
and `validate_dashboard.py` independently checks the corrections are still on
disk. Both are mutation-tested. **Nothing is at risk while the decision waits.**

**Options**

- **(a) Correct the v33 source workbook** so the defects stop originating
  upstream. Cleanest; changes a frozen artefact.
- **(b) Add a post-lock correction stage to `reconcile.py`** that applies the
  errata register on every run. Leaves v33 frozen; adds a permanent step.

**Recommendation:** (b). v33 is a frozen, SHA-pinned artefact and the register
already exists in machine-readable form, so the correction stage is small and
self-documenting. (a) means editing a locked file to fix a dataset derived from
it, which is the more disruptive of the two.

**What I need from you:** (a) or (b).

---

## 6. Four PRISMA items need process statements

These cannot be derived from any file. They are facts about how the review was
conducted.

| Item | What PRISMA asks | What is needed |
|---|---|---|
| 8 | Selection process | How many reviewers screened each record; how disagreements were resolved |
| 9 | Data collection process | How many people extracted data from each report; independently or not |
| 11 | Risk-of-bias assessment | How many assessors per result; how disagreements were resolved |
| 23c | Limitations of review processes | Follows from 8, 9 and 11 |

Items 11 and 23c are deliberately held open on the dashboard, and the
risk-of-bias assessor process is deliberately excluded from the Limitations
section, because independent dual assessment is still in progress. Both will be
written once that concludes — the validator currently refuses to let either be
closed early.

**What I need from you:** one sentence each for items 8 and 9, and for 11 once
dual assessment concludes.

---

## Summary of what to send back

1. Nausea/vomiting: option (a), (b) or (c) — and whether to compute GRADE
2. Target A–F: approval to rename in manuscript-facing surfaces
3. Szmit 2021: strict or bounded reading — and whether to run the sensitivity analysis
4. Stratum label: permission to correct, or leave and note
5. v33 upstream: correct the source, or add a correction stage
6. One sentence each on screening (8) and extraction (9) process

Items 1, 3 and 5 change what the pipeline does and I would act on them the same
day. Items 2 and 4 are small. Item 6 is text only.
