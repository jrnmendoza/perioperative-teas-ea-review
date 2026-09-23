# Pre-committed decision rules for author replies

**Written 22 September 2026; fixed and hashed 23 September 2026, before any author
reply was received.** A scan of the review author's mailbox on 23 September found
no reply from any queried author: only the three delivery failures already
logged. Covers the eleven queries sent on 22 September. File hashes are recorded in
`precommitted_decision_rules.sha256` and in `author_query_log.csv`.

**What these rules can and cannot claim.** Every effect size these trials would
contribute is already public in the published reports, and the review team
knew them when these rules were written (Appendix A). The rules are therefore
not blind to effects. What they fix is narrower and checkable: **before any
author has answered, they state which answer moves each result where**, using
only the registered estimand and the existing conversion policy. A reply
changes a disposition only through a condition written here.

---

## General rules

**G1 — Immutability.** No rule for a trial may be amended after any reply from
that trial's authors is received. An amendment before a reply must be logged
with date and reason, and the superseded text retained verbatim.

**G2 — Effect-blindness of the conditions.** No condition refers to the
direction, size, significance or precision of a result, or to its effect on any
pooled estimate. Appendix A lists known effects for transparency only.

**G3 — INCLUDE** (principal body if sham-controlled; supportive if usual care)
requires **all** of:

- (a) **delivered** opioid — not programmed doses, demands or button presses;
- (b) a window from the **end of surgery** to **24 hours**. A window starting
  later (for example at PCA connection) qualifies only if no opioid was given
  before its start;
- (c) **all systemic opioid** given in the window is inside the reported
  quantity, or the authors confirm none was given outside it;
- (d) every opioid component has a **registered factor**: IV morphine 1, IV
  hydromorphone 5 mg/mg, IV fentanyl 0.1 mg/µg, IV sufentanil 0.5 mg/µg
  (central). **Tramadol, pethidine, dezocine, oxycodone, alfentanil,
  remifentanil, butorphanol and bucinnazine have none**
  (`FINAL_MME_CONVERSION_POLICY.md`, line 11);
- (e) an arm-level mean and dispersion for the **combined** total. Separately
  reported components are never summed into a total SD;
- (f) an **absolute** dose. A weight-normalised dose is never multiplied by a
  mean weight;
- (g) an eligible population: surgery under **general anaesthesia**;
- (h) a **systemic** route. Epidural or other neuraxial opioid is not systemic.

**G4 — SENSITIVITY.** The result is eligible, reports a systemic opioid
quantity, and fails one or more of (b), (c), (d), (e) or (f). It enters the
expanded bodies only.

**G5 — HOLD.** A source question still prevents classification.

**G6 — EXCLUDE** from the opioid bodies. The result fails (g) or (h), or has no
convertible opioid at all. Trial-level eligibility for other outcomes is
adjudicated separately and is not decided by these rules.

**G7 — No reply or undelivered.** The current disposition stands. An
undelivered query is reported as undelivered, never as unanswered.

**G8 — Partial replies.** Each condition is assessed on its own. A condition the
reply does not address is treated as **not met**.

**G9 — Replies that conflict with the publication.** Author-supplied aggregate
values are accepted when they resolve a documented ambiguity. If a reply
contradicts a clearly printed value without explaining the discrepancy, the
result goes to HOLD and the conflict is reported. Published values are never
overwritten; the author value and its date are recorded alongside them.

**G10 — Comparator class** follows the authors' description of what the arm
received. Identical placement with no current is sham. No procedure is usual
care. Current delivered at non-acupoint sites is an active electrical control.

**G11 — Mechanical consequences.** Any newly admitted result goes through the
unchanged pipeline: compatible active arms combined with the shared control
counted once; REML with safeguarded Hartung–Knapp for k ≥ 2; a fresh
result-specific RoB 2 from source plus reply, recorded before the model is
rerun; GRADE redone. If a sufentanil-derived result enters a principal or
supportive body, the 0.25 and 1.0 mg/µg factors become **mandatory
sensitivity analyses for that body**.

---

## Trial rules

Each rule states the result's current disposition, its **ceiling** (the best
disposition any reply can produce under G3–G6), and the conditions.

### C1 — Jin 2023 · EA vs sham · HOLD · ceiling INCLUDE

- All participants under neuraxial anaesthesia → **EXCLUDE** (G6, g).
- Mixed anaesthesia, with no arm-level data for the general-anaesthesia subset →
  **EXCLUDE** (G6, g). Mixed, with that subset supplied → assess the subset below.
- General anaesthesia confirmed **and** a verified fentanyl concentration
  supplied, so that delivered mL × µg/mL is a valid linear factor, **and** every
  other opioid in the pump has a registered factor **and** (a), (b), (c), (e) met
  → **INCLUDE**.
- General anaesthesia confirmed, but concentration missing, or volume is
  programmed or demanded rather than delivered → **SENSITIVITY**.
- Both active arms combined against the sham arm (G11).

### C2 — Xie 2014 · EA vs sham · HOLD · ceiling INCLUDE, **realistically SENSITIVITY**

- Table 2 reports dezocine rescue in 5–35% of participants per arm. Dezocine has
  no registered factor.
- **INCLUDE** only if all of: a delivered sufentanil total restricted to 0–24 h
  is supplied with its SD; **no participant** in the compared arms received
  dezocine or any other unfactored opioid within 0–24 h; and (a), (b), (e) are met.
- Dezocine given within 0–24 h to any participant → **SENSITIVITY** at best.
- Total confirmed as 48 h or whole-PCA-period, with no 0–24 h figure →
  **SENSITIVITY**.
- Arm A ("control") is classified under G10. If A received no procedure, the C
  versus A contrast follows the same rules into the EA versus usual care body.
- **Table 2 prints 133 ± 7.0 (sham) and 134 ± 5.9 (control); the Results text
  prints 133.5 and 134.3.** Table values are retained unless the authors confirm
  otherwise (G9). The discrepancy is recorded as a minor source inconsistency.

### C3 — Yeh 2010/2011 · TEAS vs sham · HOLD · ceiling INCLUDE

- 24-hour opioid given epidurally or by another neuraxial route → **EXCLUDE** (G6, h).
- Intravenous route confirmed **and** cohort relationship resolved — independent
  cohorts, or overlap with a mapping that lets the family contribute one result
  — **and** (a), (b), (c), (e) met → **INCLUDE**.
- Intravenous confirmed, cohort relationship unresolved → **HOLD**.
- The family is counted once whatever the reply.

### C4 — Ntritsou 2014 · EA vs sham · EXCLUDE · ceiling EXCLUDE

- Tramadol has no registered factor. **No reply can produce an IV-MME result.**
- A reply is used only to make the narrative description accurate: window,
  delivery mode, and any other opioid given.
- The same condition blocks a native-tramadol pooled analysis: no other
  sham-controlled trial reports tramadol in a matching window.

### D1 — Chen 1998 · TEAS vs sham (Group IV vs Group I) · SENSITIVITY · ceiling INCLUDE

- Group I received current at any site → reclassified as active electrical
  control (G10). The contrast leaves the sham body and is assessed as
  TEAS versus active control.
- Supplemental 0–24 h analgesics were **non-opioid**, **and** the "total in 24 h"
  hydromorphone includes the PACU dose and is delivered → **INCLUDE**.
- Supplemental analgesics included an opioid **with** a registered factor, and a
  combined 0–24 h total with SD is supplied → **INCLUDE**.
- Supplemental opioid with a registered factor, but components only →
  **SENSITIVITY**.
- Supplemental opioid **without** a registered factor (for example oxycodone or
  pethidine) → **SENSITIVITY**.

### D2 — Lee 2011 · TEAS vs sham (Groups 3+4 vs Group 2) · SENSITIVITY · ceiling INCLUDE

- No opioid given in the recovery room before PCA started, or recovery-room
  doses are included in Table 8's delivered dosage → assess (a)–(e); if met,
  **INCLUDE**.
- Recovery-room opioid given and not included: a combined total with SD, all
  components factored → **INCLUDE**; components only → **SENSITIVITY**.
- The recorded discrepancy between the sham interval sum and Table 8 must be
  resolved by the reply. If it is not → **SENSITIVITY** (G8).
- Groups 3 and 4 combined against Group 2 (G11).

### D3 — Lin 2002 · EA vs sham (Groups III+IV vs Group II) · SENSITIVITY · ceiling INCLUDE, **realistically SENSITIVITY**

- The protocol gave **pethidine 1 mg/kg IM** on request during the first
  postoperative hour, then PCA morphine from hour 1. Pethidine has no registered
  factor, and the dose is weight-based.
- **INCLUDE** only if the authors report that **no participant** in the compared
  arms received pethidine or any other opioid before PCA connection, and
  (a), (e) are met.
- Any pethidine given in the compared arms → **SENSITIVITY**, whatever else the
  reply supplies.

### D4 — Sim 2002 · EA vs sham (Groups II+III vs Group I) · SENSITIVITY · ceiling INCLUDE

- Absolute delivered morphine in mg per arm, with SD, over 0–24 h from the end
  of surgery, **and** no other systemic opioid in the window (or any included and
  factored, with a combined SD) → **INCLUDE**.
- Body-weight summaries only → **SENSITIVITY** (G3 f; the native mg/kg result is
  retained).
- Intraoperative alfentanil lies outside the window and does not affect
  classification.

### D5 — Coura 2011 · EA vs sham · SENSITIVITY · ceiling INCLUDE · **currently UNDELIVERED**

- The disposition stands until a reply is received through a working route (G7).
- Absolute delivered fentanyl in µg per arm, with SD, from the end of surgery to
  24 h, **and** opioid in sedative infusions either absent or included and
  factored → **INCLUDE**.
- Sedative infusion containing an unfactored opioid (for example remifentanil) →
  **SENSITIVITY**.
- Body-weight summaries only → **SENSITIVITY**.
- Data available only as analysed (13 vs 9 of 32 randomised) are accepted. The
  attrition is carried into RoB 2 and does not by itself block inclusion.

### B1 — Chen 2020 · TEAS vs sham · SENSITIVITY · ceiling INCLUDE

- A delivered sufentanil total from the end of surgery to 24 h — basal infusion
  plus delivered demand doses — per arm with SD, **and** rescue either none or
  factored and included in a combined total with SD → **INCLUDE**.
  G11 then makes the 0.25 and 1.0 factors mandatory sensitivities for the
  principal TEAS body.
- Totals confirmed as demand doses only → **SENSITIVITY** (G3 a, c).
- Rescue with an unfactored opioid → **SENSITIVITY**.
- The 48-hour totals (118.52 and 140.15 µg) do not qualify, whatever the reply.

### B2 — He 2026 (hepatectomy) · TEAS vs sham · SENSITIVITY · ceiling INCLUDE

- Values confirmed as **IV** morphine equivalents, with the authors' drug list and
  factors each matching a registered factor, **and** (a), (b), (c), (e) met →
  **INCLUDE** as reported.
- IV equivalents, but one or more of the authors' factors differs from the
  registered one: native-drug totals supplied → recompute with registered
  factors and **INCLUDE** if (e) holds for the recomputed total; no native totals
  → **SENSITIVITY**.
- **Oral** equivalents: native-drug totals supplied → recompute and assess as
  above; no native totals → **SENSITIVITY**. No oral-to-IV factor is assumed.
- Any unfactored opioid in the total → **SENSITIVITY**.
- Weight-normalised at any stage → **SENSITIVITY** unless absolute totals are
  supplied.

---

## Ceilings — what these queries can deliver at most

| Principal body | Now | Reachable through replies | Ceiling k |
|---|---:|---|---:|
| TEAS vs sham | 1 (Szmit 2021) | Chen 2020, He 2026, Chen 1998, Lee 2011, Yeh 2010/2011 | **6** |
| EA vs sham | 0 | Jin 2023, Sim 2002; Coura 2011 if a working route is found | **2** (3 with Coura) |

Xie 2014 and Lin 2002 are capped at SENSITIVITY by unfactored rescue opioids
unless the authors report that no participant received them. Ntritsou 2014
cannot reach any IV-MME body.

---

## Appendix A — known effects (transparency only; no rule refers to these)

IV-MME mean differences at the central factors, from published arm-level data:

| Trial | Body | MD, mg IV MME (95% CI) |
|---|---|---|
| Chen 1998 | TEAS vs sham | −21.00 (−32.96, −9.04) |
| Chen 2020 | TEAS vs sham | −14.09 (−15.84, −12.35) at 0.5 mg/µg |
| He 2026 (hep) | TEAS vs sham | −0.60 (−1.73, +0.53) |
| Lee 2011 | TEAS vs sham | −4.91 and −3.06 (two arms, not yet combined) |
| Yeh 2011 | TEAS vs sham | −2.30 (−8.13, +3.53) |
| Lin 2002 | EA vs sham | −15.20 and −8.40 (two arms) |
| Xie 2014 | EA vs sham | −9.00 (−11.02, −6.98) at 0.5 mg/µg |
| Jin 2023, Sim 2002, Coura 2011 | EA vs sham | not convertible from published data |
| Ntritsou 2014 | EA vs sham | not convertible (tramadol) |

The rules would admit He 2026, the largest trial in the set, whose effect is
close to zero, on the same terms as Chen 1998, whose effect is the largest.

---

## Not covered

The four unsent queries (El-Rakshy 2009, Zheng 2025, He 2026 breast, Long 2025)
have no rules yet. Rules must be added here **before** any of them is sent.
