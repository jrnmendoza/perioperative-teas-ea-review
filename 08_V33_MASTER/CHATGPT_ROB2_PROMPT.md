# Result-specific Cochrane RoB 2 — evidence gathering and draft assessment

You are supporting the risk-of-bias assessment for a systematic review of
perioperative transcutaneous electrical acupoint stimulation (TEAS) and
electroacupuncture (EA). You have the full-text source PDFs.

## What this task is, and what it is not

**This is not the review's risk-of-bias assessment.** Cochrane RoB 2 requires
two independent human assessors reaching consensus, and the review will report
their judgements under their names. Your output is *preparatory*: the
signalling-question evidence, extracted verbatim, plus a **draft** judgement
that the human assessors will adjudicate, accept, or overturn.

Because of that, the evidence you quote matters far more than the verdict you
propose. A draft judgement with weak supporting quotes is worse than useless. A
domain marked "cannot be judged from the source" with a clear explanation of
what is missing is a genuinely useful answer.

---

## Why this task exists: RoB 2 is result-specific

Each of these trials has already been assessed — but only for **one** result.
The review has since begun analysing **other** results from the same trials, and
a RoB 2 judgement does not transfer between results.

The two domains that move hardest between outcomes in this literature:

**Domain 4 (measurement of the outcome).** In the same open-label trial, time to
first flatus and a patient-reported QoR-40 score can differ by two levels. An
unblinded participant scoring their own recovery is a very different measurement
problem from a nurse recording a bowel event.

**Domain 2 (deviations from intended interventions).** Intraoperative opioid
consumption is *titrated by the anaesthetist during surgery*. If the
anaesthetist knew the allocation, their dosing decisions are part of the
outcome. That concern does not arise for a postoperative bowel-function endpoint
in the same trial.

So: do not carry over the existing judgement. For each domain, decide afresh for
*this specific result*, and where your judgement differs from the existing one,
say so explicitly and explain why.

---

## The assessments needed (18 study × result pairs)

For every row below, assess the **named result**, not the study in general. The
"currently on file" column is the existing assessment of a *different* result in
the same trial — shown so you can compare, **not** to be copied.

### A. Binary rescue opioid use, 0–24 h / POD1
*(participants requiring any rescue opioid; a binary incidence outcome)*

| Study | Result to assess | Currently on file (different result) |
|---|---|---|
| Yu 2020 | Participants requiring rescue sufentanil, 0–24 h | Global QoR-40 — High |
| Tu 2024 | Any rescue tramadol use, within 24 h | Vomiting incidence — High |
| Liu 2026 (burn) | Any rescue dezocine use, through POD1 | Intraoperative remifentanil — Some concerns |

Consider especially: was rescue administration **protocolised** (e.g. triggered
by a VAS/NRS threshold) or left to clinician discretion? Who decided, and were
they blinded? A discretionary rescue decision by an unblinded clinician is a
Domain 4 and Domain 2 problem simultaneously.

### B. Intraoperative remifentanil consumption

| Study | Currently on file (different result) |
|---|---|
| Pan 2023 | Time to first postoperative flatus — High |
| Zhu 2022 | Postoperative vomiting — Some concerns |
| Zheng 2025 | Any PONV — Some concerns |
| Wu 2022 | VAS pain intensity — High |
| Wu 2025 | VAS pain intensity — High |
| Ntritsou 2014 | Total tramadol exposure — High |
| Lu 2021 | Post-mastectomy chronic pain incidence — High |
| Guo 2023 | Postoperative cognitive dysfunction — High |

Consider especially: was the **anaesthetist** blinded? Was intraoperative dosing
protocolised (e.g. titrated to a BIS or MAP target with stated rules), or at
discretion? Was the person recording the dose blinded? If dosing was
discretionary and the anaesthetist was unblinded, Domain 2 is likely serious and
should be argued as such.

### C. Intraoperative sufentanil consumption

| Study | Currently on file (different result) |
|---|---|
| Zhu 2022 | Postoperative vomiting — Some concerns |
| Wu 2025 | VAS pain intensity — High |
| Wang 2024 | PONV incidence — High |
| Song 2020 | PCA pump press number — Some concerns |

Same considerations as B. For **Wang 2024**, note that the trial has two PONV
risk strata (SNVP and MNVP) each with its own control arm — state whether your
judgement applies to both strata or differs between them.

### D. Global QoR-40 at ~24 h

| Study | Currently on file (different result) |
|---|---|
| Liang 2021 | CRBD incidence — High |

QoR-40 is entirely patient-reported. Domain 4 turns on whether participants were
credibly blinded — and specifically whether the sham was **sensory-matched**
(did control participants feel a comparable sensation?). Electrodes applied
without current are not sensory-matched to active stimulation.

### E. Time to first defecation

| Study | Currently on file (different result) |
|---|---|
| Yang 2024 | Morphine use via IV PCA — Some concerns |
| Lu 2022 | Time to meet discharge criteria — High |

Consider: how was defecation ascertained — patient self-report, nursing record,
or systematic assessment? Was the assessor blinded? Is the outcome susceptible
to reporting influenced by knowledge of allocation?

---

## What to produce for each of the 18 pairs

For **every RoB 2 domain**, answer the signalling questions, quote the evidence,
then give a draft judgement.

### Domain 1 — Randomisation process
1.1 Was the allocation sequence random?
1.2 Was the allocation sequence concealed until enrolment?
1.3 Did baseline differences suggest a problem with randomisation?

### Domain 2 — Deviations from intended interventions
State first which **effect of interest** you are assessing: *assignment to
intervention* (ITT-type) or *adhering to intervention*. Use **assignment**
unless the paper's own analysis is clearly per-protocol, and say which you used.

2.1 Were participants aware of their assigned intervention?
2.2 Were carers/people delivering the intervention aware?
2.3 Were there deviations arising from the trial context?
2.4 Were such deviations likely to have affected the outcome?
2.5 Were they balanced between groups?
2.6 Was an appropriate analysis used to estimate the effect of assignment?
2.7 Was there potential for substantial impact of failure to analyse
    participants in their randomised group?

### Domain 3 — Missing outcome data
3.1 Were data available for all, or nearly all, randomised participants?
3.2 Is there evidence the result was not biased by missing data?
3.3 Could missingness depend on the true value?
3.4 Is it likely that missingness depended on the true value?

Give the **exact analysed N per arm for this specific result** — it can differ
between outcomes within one trial.

### Domain 4 — Measurement of the outcome
4.1 Was the method of measuring the outcome inappropriate?
4.2 Could measurement/ascertainment have differed between groups?
4.3 Were outcome assessors aware of the assigned intervention?
4.4 Could assessment have been influenced by knowledge of the intervention?
4.5 Is it likely that assessment was influenced by knowledge of the
    intervention?

**This is the domain that most often differs from the existing assessment.**
State plainly who measured this specific outcome and whether they were blinded.

### Domain 5 — Selection of the reported result
5.1 Were the data analysed in accordance with a pre-specified plan finalised
    before unblinded outcome data were available?
5.2 Is the numerical result likely selected from multiple eligible outcome
    measurements?
5.3 …from multiple eligible analyses of the data?

Check for a **trial registration** (ChiCTR, NCT, etc.) and a protocol. Say
whether this specific outcome was pre-registered, and whether it was listed as
primary or secondary. If you cannot find a registration, say so.

---

## Output format

Return a CSV code block with this header, one row per study × result:

```
study,result_assessed,timepoint_window,effect_of_interest,comparison,randomized_n_int,randomized_n_comp,analyzed_n_int,analyzed_n_comp,d1_judgement,d1_rationale,d2_judgement,d2_rationale,d3_judgement,d3_rationale,d4_judgement,d4_rationale,d5_judgement,d5_rationale,overall_draft,differs_from_existing,why_it_differs,registration_id,key_quotes,assessor_uncertainty
```

- Judgements: `Low`, `Some concerns`, `High`, or `Cannot be judged`.
- `overall_draft` follows the RoB 2 algorithm: `High` if any domain is High, or
  if multiple domains at "Some concerns" substantially lower confidence; `Low`
  only if **all five** are Low; otherwise `Some concerns`. State which rule you
  applied.
- `differs_from_existing`: `Yes` / `No`, comparing with the "currently on file"
  judgement shown above.
- `key_quotes`: verbatim sentences supporting the domain judgements, each with
  its page number. This is the most important field in the row.
- `assessor_uncertainty`: anything you could not determine, and what document
  would resolve it.

Then, after the CSV, give a short prose paragraph per study explaining the
reasoning for the domains where your draft differs from what is on file.

---

## Rules

1. **Do not copy the existing judgement.** If you conclude it happens to be
   correct for this result too, say so and give the reason.
2. **Do not infer blinding from the word "double-blind" in the title or
   abstract.** Find who was actually blinded, in the Methods. Many trials
   describe themselves as double-blind while the anaesthetist or the
   acupuncturist was necessarily unblinded.
3. **Do not treat "no significant baseline differences" as evidence of adequate
   randomisation.** Domain 1 is about sequence generation and concealment.
4. **Do not guess a registration number.** If you cannot find one, write
   `NO REGISTRATION FOUND`.
5. **Do not soften a judgement because the trial is otherwise well conducted**,
   and do not harden one because the result was positive.
6. Where the source genuinely does not report enough to judge a domain, use
   `Cannot be judged` and name the missing information. Do not default to
   "Some concerns" as a way of avoiding the question.
7. Assess the result **as analysed in the paper**, using the analysed N for that
   result — not the randomised N, and not another outcome's N.

Finish with a summary table: study, result, draft overall, whether it differs
from the existing assessment, and the single most important piece of missing
information for that trial.
