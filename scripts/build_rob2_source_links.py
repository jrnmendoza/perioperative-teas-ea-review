#!/usr/bin/env python3
"""
Link each RoB 2 matrix cell to the specific, per-domain, source-quoted
rationale it actually has -- and to the source PDF that quote comes from.

WHY THIS EXISTS
The RoB 2 matrix's interactive popovers (renderRoB2Matrix() in app.js) read
their rationale from STUDIES_DATA[i].rob2_outcomes[outcomeKey].rationale --
which for the current dataset is, for every single one of the 74 currently
assessed results, either empty, a short one-line stub, or a general adoption
note. It is NEVER the rich, per-domain, source-quoted text that actually
exists for the same results in the review's own RoB 2 registers
(09_V34_ANALYSIS/03_ROB2/v34_rob2_draft_assessments.csv, 36 rows, and
v34_rob2_priority2_assessments.csv, 515 rows -- 493 plus 22 added while
closing this script's own remaining coverage gaps, see "EXTENDING THE
REGISTER ITSELF" below) -- confirmed: 551/551 of those rows contain at least
3 distinct domain markers with embedded verbatim quotes from the source PDF,
and 0/75 of the client-side rationale strings do.

Both registers are already loaded client-side in full, as
window.V34_DATA.rob2_results.results (36 rows) and
window.V34_DATA.rob2_priority2.results (515 rows) -- generated from the same
two CSVs this script reads (scripts/build_v34_dashboard_data.py). This script
reads the CSVs directly rather than that client-side copy, though: the copy
drops analysed_n_i/analysed_n_c/randomised_n_i/randomised_n_c on the way into
v34_data.js, and _match_by_denominator() below needs those fields -- an
earlier version of this script, built against the client-side copy, could
only ever disambiguate by wording, and that is what forced the elaborate
lexical tiebreak this file also contains.

What this script adds is the missing LINK between a matrix cell (keyed by the
dashboard's own outcome "bucket", e.g. opioid_24h) and the specific row in
those 551 that the cell is actually about, plus the per-domain split of that
row's rationale text.

WHY THE JOIN IS DETERMINISTIC KEYWORD/TIMEPOINT MATCHING, NOT FUZZY TEXT
SIMILARITY
Tried first: matching STUDIES_DATA's outcome_name/timepoint text against the
CSV's outcome/timepoint text by normalized substring overlap. Result: 13 of 75
confidently matched, 53 ambiguous -- the two data sources were authored at
different times with different outcome-name conventions (e.g. "Total fentanyl
PCIA dose" vs "Exact cumulative postoperative fentanyl"), and free-text
similarity cannot safely disambiguate that. A study contributing multiple
results to the same outcome family (e.g. two PONV-related rows) makes this
worse, not better.

This instead matches by an explicit, conservative keyword+timepoint rule per
dashboard outcome bucket (BUCKET_RULES below), plus EXCLUDE_PATTERNS for
outcomes that share a family label or drug name with genuine candidates but
are never the right answer (opioid side effects, PONV-rescue medications,
composite "success" measures), and only records a link when EXACTLY ONE row
in that study's contributions satisfies the rule -- "zero matches" and "more
than one match" are both left unlinked rather than guessed at. A second pass
(_tiebreak()) resolves SOME multi-candidate cases using the dashboard's own
already-selected outcome_name, but only via each candidate's DISTINGUISHING
tokens against the others, and only when that points to exactly one winner --
see _tiebreak()'s docstring for two lexical false positives found and fixed
while building it, both the same shape: a word that reads as generic filler
in most candidates is the one distinguishing word in another, so a static
stopword list added on suspicion (without a concrete failure to justify it)
reliably introduces a new wrong answer somewhere else. Only "consumption" is
excluded from tiebreak scoring, and only because a concrete false match
(Jin 2023, documented in _tiebreak()) demonstrated it needed to be; broader
additions tried during development (total, dose, amount, requirement, level)
were reverted after "total" produced the mirror-image bug on Zheng 2025.

BEFORE THE LEXICAL TIEBREAK: HARD NUMBERS, WHERE THEY EXIST
_match_by_denominator() tries two numeric checks ahead of any wording, using
fields the client-side copy above does not carry:

  1. Does a candidate's recorded analysed_n_i/analysed_n_c exactly match the
     denominator the dashboard's OWN stored value for this bucket already
     implies (arm1_n/arm2_n, or an arm1_total/arm2_total derived from an
     events/total pair)? If so, that candidate is not inferred to be the
     source of that figure, it is read directly off both sides.
  2. Failing that, is exactly one candidate's analysed_n recorded at all (its
     siblings blank)? A row with no analysed n was not what produced a
     dashboard figure that has one.

Both found by manually tracing Jin 2023's opioid_24h bucket: dashboard value
(n=53, n=52); one candidate's analysed_n is exactly (53, 52); the sibling
candidate's analysed_n is blank. Same mechanism separately resolved Lu 2021's
ponv_24h bucket, where one candidate's denominator (190, 188) exactly matches
the dashboard's own stored total and the other candidate's (198, 188) does
not.

A separate family-label bleed-through was found and fixed the same way as the
ponv_24h fix above: pca_behavior matched on "family + outcome" combined text,
and two genuinely different Long 2025 rows ("PCIA compression count", "PCIA
solution consumption") both share the family label "Opioid demand" and so
both matched via that label regardless of what they actually measure. Fixed
by requiring pca_behavior's keywords to hit outcome text specifically, same
as ponv_24h/ponv_48h already did.

Verified: 65 of 74 assessed results resolve this way (up from an initial 29
using keyword+timepoint alone, then 34, 37, 43 as harder evidence and register
fixes were added, then 65 once the register itself was extended -- see
"EXTENDING THE REGISTER ITSELF" below), confirmed to ADD to the prior set
with zero removals or changes at every step -- diffed explicitly against the
prior committed version each time, not assumed. Nine remaining cases stay
unresolved because NEITHER hard evidence, wording, NOR a genuine new register
row settles them, checked individually rather than left by default:

- Yeh 2010 and Yeh 2011 (both pca_behavior) are the SAME trial published
  twice (same authors, same 3-arm design, the sham arm's own figures
  byte-for-byte identical between the two papers -- 21.6+/-13.1 mg in both).
  The dashboard's own rob2_outcomes rationale for both already says "HOLD ...
  potential overlap ... do not count independently" -- adding independent
  RoB 2 data for both would risk legitimising a double-count the review has
  already paused on. This is a unit-of-analysis decision for the review
  team, not a linking gap this script resolves.
- Tu 2024's rescue_analgesia candidates share an identical analysed_n that
  does not match the dashboard's own stored total (77, 76); the source PDF's
  own Table 1 confirms the paper's actual analysed n is (57, 58) for BOTH
  candidates -- checked against the primary source directly, and it matches
  neither. A discrepancy worth the review lead's attention, not a linking
  problem this script can paper over.
- Xie 2014's rescue_analgesia (dezocine) and Yang 2020's flatus_time both
  have genuine source-PDF data for the named outcome, but the actual Table
  values (Xie 2014: EAS 5% [1/20] vs Sham 30% [6/20], from Table 2; Yang
  2020: 20.8+/-4.6 h vs 24.1+/-6.2 h, from Table 3) do not match the
  dashboard's own stored figures for either cell (4/20 vs 10/20; 67.45+/-10.42
  vs 73.55+/-12.18) -- neither a unit conversion nor an arm-relabelling
  explains the gap. Flagged for the review lead rather than forced.
- Wu 2022's intraop_remi candidates were checked against their source PDF:
  the paper separately reports both a raw cumulative remifentanil total
  (1637 vs 1383 µg) AND a weight/time-normalised "index" (0.114 vs 0.084
  µg/min/kg) as two genuinely distinct results, so the ambiguity is real,
  not a data gap.
- Lu 2022's pca_behavior candidates remain a genuine 6-way tie (2 metrics x
  3 timepoints) even after excluding a same-bucket consumption-family row
  (see find_link()'s pca_behavior-specific filter) -- the dashboard's own
  outcome_name for that cell ("PCA attempts/deliveries") and timepoint
  ("24/48/72 h") both name multiple candidates at once, meaning the
  dashboard itself has not picked a single one either.
- Zheng 2025's pca_behavior candidates ("Effective PCIA button presses" vs
  "Total PCIA button presses") are a genuine tie the dashboard's own
  outcome_name already reflects by naming both ("Total/effective PCIA use").
- Yang 2024's intraop_remi has no genuine gap in the register to fill: the
  source PDF was read directly and reports NO intraoperative opioid figure
  at all, only postoperative PCA morphine.

THE FOUR ADDITIONAL MECHANISMS THAT RAISED 37 -> 43
- _rows_for_study() normalises a "#<id> - " key prefix ("#105119 - Zhou
  2025") that the CSV registers never carry, found by auditing every study
  key against every CSV study name for an exact-match failure rather than
  assuming a zero-candidate result meant "never assessed": it was a naming
  mismatch, not a missing assessment, and fixing it alone resolved 2 cells.
- _is_real_judgement() excludes the one "Assessed" cell (Xie 2014's
  opioid_72h) whose d1-d5/overall are all "--" -- an eligibility/
  reclassification bookkeeping note, not an RoB 2 judgement, so it
  structurally has no domain rationale to link to. This changes the
  denominator (75 -> 74), not the numerator.
- opioid_72h's timepoint list gained "first 3 postoperative days" alongside
  "72": Wong 2006's own register row spells its 72h window that way, never
  as a digit, and the dashboard's own outcome_name for the same cell already
  says "first 3 postoperative days (~72 h)" -- the same window, the paper's
  own phrasing, not a new rule invented to fit.
- MANUAL_OVERRIDES holds three cases the automated rule cannot settle on
  keyword/timepoint/denominator evidence alone, each resolved by reading
  either the CSV row's own rationale text or the source PDF directly (see
  the dict's own docstring for what was read and why each settles the
  case) -- this is the "read the source PDFs directly" standard the
  previous version of this docstring said full resolution would require,
  applied to exactly the cases where the cheaper mechanisms ran out.

EXTENDING THE REGISTER ITSELF (43 -> 65)
Everything above links a matrix cell to a row the register ALREADY has. The
remaining gap after 43 was audited cell by cell instead of stopping there:
for every still-unlinked cell, checked whether its study has zero rows in
the register at all (a real, structural "never assessed" gap -- Chen 1998,
Coura 2011, El-Rakshy 2009, Seevaunnamtum 2016, Yeh 2010, Yeh 2011 have
none), or whether the study HAS rows but not the specific outcome/timepoint
the cell needs (a gap in what was extracted, not in what the paper reports).

22 of those were the second kind, genuinely closeable: the source PDF (or,
where none exists locally, a verified per-study evidence.md extraction with
page-cited quotes -- see 09_V34_ANALYSIS/../covidence_batch_*/studies/) was
read directly, a new row was drafted in the same D1-D5/rationale format as
every existing row, and it was appended to v34_rob2_priority2_assessments.csv
(493 -> 515 rows). Each new row's numeric data was cross-checked against the
dashboard's own already-stored pooled figure where one exists (e.g. Zhang
2025's "Total sufentanil consumption 50.53+/-4.46 vs 53.79+/-5.14" matches
the dashboard's stored value exactly; Coura 2011, Chen 2020's three results,
Yang 2024's four results, Zheng 2025's composite PONV, and Jin 2023's pump
compressions all matched the same way) -- this is direct primary-source
confirmation, not an assumption that the new row belongs to that cell.

One serious finding while doing this: a separate, pre-existing set of files
("Gemini Pro + Flash 3.8 Extraction/RoB2_*.md", mirrored into 07_risk_of_bias/
and TEAS EA Verification/Gemini Pro + Flash 3.8 Extraction/) makes claims
that do not match their own cited source PDFs -- e.g. its Chen 1998 file
names the drug as morphine and cites "sealed envelopes" for allocation
concealment, but the actual PDF's drug is hydromorphone and the word
"envelope" does not appear anywhere in it. That directory was NOT used as a
source for any row added here; every new row was drafted from either a
verified, page-cited evidence.md extraction or the source PDF text directly,
the same standard as the rest of this script.

Two small rule extensions were needed to let the new rows auto-link the same
way existing ones do (both scoped and justified individually, not broadened
speculatively): pca_behavior's keyword list gained "attempt" (Chen 2020's new
row is worded "PCIA pump attempts", and "pcia" does not contain the substring
"pca"), and opioid_24h's timepoint list gained "pod 1" alongside "24"
(Zhang 2025's new row is timepointed "POD 1" -- the paper's own Table 4
header -- consistent with how the review already treats "POD1" as ~24h
elsewhere in this same register, e.g. Yu 2020's pain_rest_24h row is
annotated "POD1 (~24 h)"). Both checked against the full register for false
positives before being added; neither changed any existing link.

Two further discrepancies were found this same way and are NOT filled in --
see the two bullet points above (Xie 2014 rescue_analgesia, Yang 2020
flatus_time) for what the actual PDF tables say versus what the dashboard
has stored.

WHAT THIS DOES NOT DO
Invent a page number. Neither register carries one (checked: 0 of 551 rows
mention a page reference), so only the source PDF filename is given as the
locator, not a specific page -- a reader with access to that PDF can search
it for the quoted phrase, which is exact and copied from the source, but this
script will not fabricate a page number to make the answer look more precise
than the data supports.

Usage:  python3 scripts/build_rob2_source_links.py
Exit:   0 on success, 1 if the expected data files are missing.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
OUT = DASH / "rob2_source_links.js"

# (keyword regexes, OR'd; timepoint substrings that must appear, ANY'd or None
# if the bucket has no time window; whether keywords must hit the OUTCOME text
# specifically rather than family+outcome combined). Deliberately conservative:
# under-matching (leaving a cell unlinked) is the safe failure mode here,
# over-matching (linking the wrong result) is not.
#
# outcome_only=True matters for the PONV/nausea/vomiting split: these rows'
# `family` field is "PONV" for the composite, nausea-alone AND vomiting-alone
# rows alike, so a family-inclusive search on "ponv_24h" (composite) matched
# "Nausea incidence" and "Vomiting incidence" rows too, purely because they
# share a family label with the genuine composite row -- found by manually
# reviewing every 2+-candidate case this pass turned up, not by inspection of
# the rule alone.
BUCKET_RULES = {
    # "pod 1" alongside "24": Zhang 2025's register row for this bucket is
    # timepointed "POD 1" (the paper's own Table 4 header), never spelling
    # out "24" -- consistent with how the review already treats "POD1" as
    # ~24h elsewhere (e.g. Yu 2020's pain_rest_24h row is annotated "POD1
    # (~24 h)" in this same register). Checked: no OTHER opioid-consumption
    # row in the register uses "POD1"/"POD 1" as its timepoint, so this
    # cannot pull in a wrong candidate for any other study.
    "opioid_24h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia", "pca dose"], ["24", "pod 1"], False),
    "opioid_48h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["48"], False),
    # "first 3 postoperative days" alongside "72": Wong 2006's register row for
    # this exact bucket is timepointed "First 3 postoperative days total", never
    # spelling out "72" -- the dashboard's own outcome_name for the same cell
    # says "first 3 postoperative days (~72 h)", so this is the same window
    # under the paper's own phrasing, not a guess. Checked: no OTHER Wong 2006
    # row (its per-day breakdowns) contains this phrase, so it cannot pull in
    # a wrong candidate.
    "opioid_72h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["72", "first 3 postoperative days"], False),
    "pain_rest_24h": (["pain", "vas", "nrs"], ["24"], False),
    "ponv_24h": (["ponv", "nausea.*vomit", "composite", "any ponv"], ["24"], True),
    "ponv_48h": (["ponv", "nausea.*vomit", "composite", "any ponv"], ["48"], True),
    "nausea_24h": (["nausea"], ["24"], False),
    "nausea_48h": (["nausea"], ["48"], False),
    "vomiting_24h": (["vomit"], ["24"], False),
    "vomiting_48h": (["vomit"], ["48"], False),
    "flatus_time": (["flatus"], None, False),
    "rescue_analgesia": (["rescue"], None, False),
    "intraop_remi": (["remifentanil", "alfentanil"], None, False),
    # outcome_only=True: many PCA-related rows share the family label
    # "Opioid demand" regardless of what they actually measure, so "demand"
    # matching via family+outcome combined text let two genuinely different
    # Long 2025 rows ("PCIA compression count" and "PCIA solution
    # consumption") both pass -- found the same way as the ponv_24h family
    # bleed-through above, by checking why a case that should have resolved
    # via a unique keyword hit did not.
    # "attempt" added alongside bare "pca": Chen 2020's press-count row is
    # worded "Total and effective PCIA pump attempts" -- "pcia" does not
    # contain the substring "pca", so the bare keyword alone missed it.
    # Checked every other "attempt"-containing row in the register first
    # (He 2026, Lu 2022 x3): all are already "Opioid demand"-family PCA
    # rows that either already matched via "pca" or are already part of
    # Lu 2022's established, still-unresolved multi-way tie, so this adds
    # no new false positives.
    "pca_behavior": (["pca", "press", "demand", "bolus", "attempt"], None, True),
    "qor_24h": (["qor", "quality of recovery"], ["24"], False),
}
ALL_WINDOWS = ("24", "48", "72")

# Outcomes that are never the right answer for ANY bucket above, even though
# they share a family label or drug name with genuine candidates: opioid
# SIDE EFFECTS (not consumption), PONV-RESCUE medications (not analgesic
# rescue), and composite "success" measures that would misattribute a
# single-symptom bucket's rationale to a different, broader outcome. Found by
# manually reviewing every case this rule set produced 2+ candidates for.
EXCLUDE_PATTERNS = [
    r"\bdrowsiness\b", r"\bpruritus\b", r"\bsedation\b", r"\bitching\b",
    r"\bmetoclopramide\b", r"\btropisetron\b", r"\bondansetron\b", r"\bantiemetic\b",
    r"\bcomplete response\b",
]


def split_domains(rationale: str) -> dict[int, str]:
    """
    Split a "D1 ...: 'quote'. D2 ...: 'quote'. ..." rationale into
    {1: text, 2: text, ...}, stripping the redundant leading "D<n>[judgement]:"
    label from each segment (the authoritative judgement is the dashboard's own
    d1..d5 columns, not re-parsed from this free text).
    """
    markers = list(re.finditer(r"\bD([1-5])\b", rationale))
    out = {}
    for i, m in enumerate(markers):
        start = m.start()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(rationale)
        domain = int(m.group(1))
        text = rationale[start:end].strip().rstrip(".").strip()
        text = re.sub(rf"^D{domain}\s*[A-Za-z ]*?:\s*", "", text)
        out[domain] = text.strip()
    return out


def row_text(row: dict, outcome_only: bool) -> str:
    if outcome_only:
        return (row.get("outcome") or "").lower()
    return f"{row.get('family', '')} {row.get('outcome', '')}".lower()


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "of", "the", "a", "an", "to", "in", "for", "and", "or", "with",
    "at", "on", "postoperative", "cumulative", "incidence",
    # "consumption" specifically, not a broader generic-word list: it is
    # present in the outcome label of nearly every opioid-related candidate
    # in this dataset, so its presence in exactly one of two candidates is
    # not evidence about WHICH one outcome_name refers to (see
    # _tiebreak()'s docstring, the Jin 2023 false match). A first pass also
    # added "total", "dose", "amount", "requirement", "level" on the same
    # reasoning, without the same concrete evidence -- and "total" promptly
    # produced the mirror-image bug: Zheng 2025's pca_behavior bucket wants
    # "Total/effective PCIA use", genuinely ambiguous between a "Total PCIA
    # button presses" candidate and an "Effective PCIA button presses" one,
    # and stopwording "total" silently deleted that candidate's ONLY
    # distinguishing token, turning a tie this function is supposed to leave
    # unresolved into a confident, wrong, one-sided answer. Reverted to just
    # the one word with actual evidence behind it.
    "consumption",
}


def _tokens(text: str) -> set[str]:
    return {w for w in _TOKEN_RE.findall((text or "").lower()) if w not in _STOPWORDS}


def _tiebreak(oc_outcome_name: str, candidates: list[dict]) -> tuple[dict | None, str]:
    """
    When the keyword+timepoint rule alone leaves more than one candidate,
    break the tie using each candidate's DISTINGUISHING tokens -- the words
    that differ between the candidates, not their raw text overlap with the
    target.

    Two failed attempts before this one, both found by manually checking
    every result:

    Plain token overlap (any positive score, strictly ahead of the runner-up)
    was too loose: Jin 2023's opioid_24h bucket (wants "Cumulative 24-h Opioid
    Consumption") scored "Published 'fentanyl consumption' / PCIA solution
    volume" over "Exact cumulative fentanyl mass / MME" on a single shared
    word, "consumption" -- despite the other candidate being the correct
    match (the PCIA-solution-volume figure is a proxy this review has
    separately flagged as not the recoverable fentanyl mass; see
    07_TIERED_V33/build_tier_e_smd_dataset.py's Jin 2023 notes).

    Requiring a raw overlap of >=2 tokens with a >=2 margin, to fix that, was
    then too strict: it also rejected Liu 2021's pain_rest_24h bucket (wants
    "Pain intensity at rest"), where "VAS at rest" is obviously the right
    answer over "VAS with coughing" -- but outcome_name is short, so the
    shared, correctly-discriminating word ("rest") is the only overlap there
    ever will be, and a token-count floor built for longer strings rejected a
    short, unambiguous one.

    This computes, for each candidate, the tokens NOT shared by every
    candidate (what actually makes it different from its siblings), and
    checks whether the target's tokens pick out exactly one candidate via
    those distinguishing tokens. "Rest" distinguishes "VAS at rest" from
    "VAS with coughing" and IS in the target -> correct, unique answer from a
    single word. "Consumption" is NOT a distinguishing token between Jin
    2023's two candidates (neither the word nor a synonym is unique to
    either) -- it does not appear in either candidate's own text as a
    distinguishing word, only as ambient vocabulary -- so no candidate wins
    on it, and that case stays correctly unresolved.
    """
    target = _tokens(oc_outcome_name)
    if not target or len(candidates) < 2:
        return None, ""
    cand_tokens = [_tokens(c.get("outcome")) for c in candidates]
    shared_by_all = set.intersection(*cand_tokens) if cand_tokens else set()
    scored = []
    for c, toks in zip(candidates, cand_tokens):
        distinguishing = toks - shared_by_all
        scored.append((len(distinguishing & target), c))
    scored.sort(key=lambda x: -x[0])
    top, runner_up = scored[0][0], (scored[1][0] if len(scored) > 1 else -99)
    if top > 0 and top > runner_up:
        return scored[0][1], "tiebreak_distinguishing_token"
    return None, ""


def find_link(bucket: str, candidates: list[dict], oc_outcome_name: str = "",
              dash_denominator: tuple[int, int] | None = None) -> tuple[dict | None, str]:
    rule = BUCKET_RULES.get(bucket)
    if not rule or not candidates:
        return None, ""
    keywords, timepoints, outcome_only = rule
    hits = []
    for row in candidates:
        text = row_text(row, outcome_only)
        if any(re.search(pat, f"{row.get('family', '')} {row.get('outcome', '')}".lower())
               for pat in EXCLUDE_PATTERNS):
            continue
        if not any(re.search(kw, text) for kw in keywords):
            continue
        if timepoints:
            tp = (row.get("timepoint") or "").lower()
            if not any(t in tp for t in timepoints):
                continue
            other = [w for w in ALL_WINDOWS if w not in timepoints]
            if any(w in tp for w in other):
                continue
        hits.append(row)
    if bucket == "pca_behavior" and len(hits) > 1:
        # "pca" alone (kept as a keyword for cases like Lin 2002, whose only
        # register row is a plain PCA-morphine-delivered figure with no
        # "press"/"demand"/"bolus" wording at all) also pulls in genuine
        # consumption-family rows once a study has more than one PCA-labelled
        # result -- e.g. Lu 2022's "Exact cumulative PCA opioid consumption"
        # alongside its actual demand/behaviour rows. When at least one hit is
        # explicitly family "Opioid demand" (this bucket's real subject),
        # drop the non-demand siblings rather than let a same-bucket
        # consumption figure compete with them -- that family split is read
        # directly off the data, not inferred from wording.
        demand_hits = [h for h in hits if (h.get("family") or "") == "Opioid demand"]
        if demand_hits and len(demand_hits) < len(hits):
            hits = demand_hits
    if len(hits) == 1:
        return hits[0], "keyword_timepoint_unique"
    if len(hits) > 1:
        # Hard numbers before wording: does a candidate's recorded analysed-n
        # match the dashboard's own stored denominator for this bucket, or is
        # exactly one candidate the only one with any analysed-n recorded at
        # all? Both are facts read off the data, not an inference from which
        # words happen to appear in a label -- tried first, and only falling
        # through to the text-based tiebreak (word choice, therefore weaker
        # evidence) when neither settles it.
        match, method = _match_by_denominator(hits, dash_denominator)
        if match:
            return match, method
        return _tiebreak(oc_outcome_name, hits)
    return None, ""


# Cases the automated rule (keyword+timepoint, then hard denominators, then
# distinguishing-token wording) cannot settle because the evidence that
# settles them isn't in either of those places -- it's either in the CSV
# row's OWN rationale text (already a verbatim extraction from the source
# PDF, just not literally matching this bucket's keyword/timepoint pattern)
# or requires reading the source PDF directly, the standard this review
# applies everywhere else. Each entry names exactly what was read and why it
# settles the case -- this is not a lexical heuristic, it is a short list of
# individually-verified answers, and every one is checked against the
# candidate list at build time (KeyError if the named outcome text no longer
# exists among that study's rows, so a future register edit cannot silently
# leave a stale override in place).
MANUAL_OVERRIDES: dict[tuple[str, str], tuple[str, str]] = {
    ("Chen 2015 (Hyperalgesia)", "opioid_24h"): (
        "Derived cumulative sufentanil dose from fixed 0.05 µg/kg bolus",
        "Two candidates share n=(29,30): a raw PCIA-bolus COUNT (the paper's "
        "own named secondary outcome per its D5 text) and a dose figure "
        "DERIVED from that count (bolus count × fixed per-bolus dose), whose "
        "own D5/flags text says so explicitly ('review-derived calculation, "
        "not the paper's own reported figure'). The bucket is a dose/mass "
        "measure ('Cumulative 24-h Opioid Consumption'), and the sibling "
        "study Chen 2015 (non-Hyperalgesia) resolves its own opioid_24h cell "
        "the same way -- to a dose derived from a fixed per-administration "
        "amount, not the raw administration count -- so this follows the "
        "review's own established convention for this exact situation "
        "rather than guessing between the two.",
    ),
    ("Yao 2015", "rescue_analgesia"): (
        "Cumulative number of rescue analgesia administrations",
        "Two candidates at n=(35,36): an administration COUNT and a TIME-TO-"
        "FIRST-administration. The dashboard's own outcome_name for this "
        "cell is 'Rescue sufentanil administration count' -- it names a "
        "count, not a time-to-event, and only one candidate is a count. The "
        "distinguishing-token tiebreak misses this because 'administration' "
        "(singular, target) and 'administrations' (plural, candidate) are "
        "different tokens under exact matching, not because the evidence is "
        "actually ambiguous.",
    ),
    ("Xing 2022", "ponv_48h"): (
        "PONV incidence",
        "The only PONV row for this study carries timepoint 'Postoperative' "
        "with no hour figure, so the keyword+timepoint rule cannot place it "
        "in ponv_24h vs ponv_48h. Read the source PDF directly "
        "(s40122-022-00429-2.pdf) to settle it: 'The frequency of PONV was "
        "reported by 5 patients in the NTG group, 11 patients in the NG "
        "group, and 13 patients in the G group within 48 h after surgery' -- "
        "the paper's own text states the window is 48 h.",
    ),
}


def _apply_manual_override(study_key: str, bucket: str, candidates: list[dict]
                            ) -> tuple[dict | None, str]:
    entry = MANUAL_OVERRIDES.get((study_key, bucket))
    if not entry:
        return None, ""
    outcome_text, _evidence = entry
    for row in candidates:
        if row.get("outcome") == outcome_text:
            return row, "manual_source_verified"
    raise KeyError(
        f"MANUAL_OVERRIDES[{study_key!r}, {bucket!r}] names outcome "
        f"{outcome_text!r}, which no longer appears among {study_key}'s "
        f"register rows -- the register changed since this override was "
        f"written; update or remove it.")


PRIORITY1_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"
PRIORITY2_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_priority2_assessments.csv"


def load_v34_rob2_rows() -> list[dict]:
    """
    Read the two RoB 2 registers directly, not via window.V34_DATA in
    v34_data.js.

    v34_data.js's embedded rob2_results/rob2_priority2 JSON is a build-time
    COPY of these two CSVs (see scripts/build_v34_dashboard_data.py), and that
    copy drops analysed_n_i/analysed_n_c/randomised_n_i/randomised_n_c --
    fields this script needs for _match_by_denominator() below and did not
    have access to in an earlier version, which is why that version could
    only ever disambiguate by wording. Reading the CSVs directly is also
    simply reading the actual source rather than a lossy derived copy of it.
    """
    rows = []
    for path in (PRIORITY1_CSV, PRIORITY2_CSV):
        with path.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                row["family"] = row.get("outcome_family", "")  # CSV column name differs
                rows.append(row)
    return rows


def _as_int(v) -> int | None:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _dashboard_denominator(dash_outcome_value: dict) -> tuple[int, int] | None:
    """
    The (arm1, arm2) denominator the dashboard's own stored value for this
    bucket implies, from whichever fields it actually populated -- an
    explicit n, or a total implied by an events/total pair. None if the
    dashboard carries no value for this bucket at all (most buckets, most
    studies: the RoB 2 assessment can exist without a pooled/displayed value).
    """
    if not dash_outcome_value:
        return None
    n1 = _as_int(dash_outcome_value.get("arm1_n"))
    n2 = _as_int(dash_outcome_value.get("arm2_n"))
    if n1 is not None and n2 is not None:
        return (n1, n2)
    t1 = _as_int(dash_outcome_value.get("arm1_total"))
    t2 = _as_int(dash_outcome_value.get("arm2_total"))
    if t1 is not None and t2 is not None:
        return (t1, t2)
    return None


def _match_by_denominator(candidates: list[dict], want: tuple[int, int] | None) -> tuple[dict | None, str]:
    """
    Disambiguate using each candidate's analysed_n_i/analysed_n_c against hard
    numbers, in order of how much they can prove:

    1. If the dashboard has a stored value for this bucket (`want` is not
       None), a candidate whose analysed_n EXACTLY matches it is the row that
       value actually came from -- not inferred, read directly off both sides.
    2. Failing that, if exactly one candidate has analysed_n recorded at all
       (its siblings are blank, meaning no result-level n was extracted for
       them), that is still real evidence: a row with no n is not what
       produced a dashboard figure that has one.

    Both found while manually tracing Jin 2023's opioid_24h bucket: its
    dashboard value is (n=53, n=52), one candidate row has that as its
    analysed_n exactly, and the OTHER candidate's analysed_n is blank -- both
    checks independently point to the same answer.
    """
    parsed = [( _as_int(c.get("analysed_n_i")), _as_int(c.get("analysed_n_c")), c) for c in candidates]

    if want is not None:
        exact = [c for n1, n2, c in parsed if (n1, n2) == want]
        if len(exact) == 1:
            return exact[0], "denominator_exact_match"

    with_n = [c for n1, n2, c in parsed if n1 is not None and n2 is not None]
    if len(with_n) == 1:
        return with_n[0], "denominator_unique_recorded"

    return None, ""


def load_studies() -> list[dict]:
    src = (DASH / "data.js").read_text(encoding="utf-8")
    start = src.index("window.STUDIES_DATA = [") + len("window.STUDIES_DATA = ")
    depth, i, in_str, esc = 0, start, False, False
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(src[start:i + 1])
        i += 1
    raise RuntimeError("could not parse window.STUDIES_DATA out of data.js")


_STUDY_PREFIX_RE = re.compile(r"^#\d+\s*-\s*")


def _rows_for_study(by_study: dict[str, list[dict]], study_key: str) -> list[dict]:
    """
    Look up a study's register rows by the dashboard's own key, falling back
    to stripping a leading "#<id> - " marker (e.g. "#105119 - Zhou 2025") if
    the direct lookup finds nothing.

    Found by checking every zero-candidate case for a naming mismatch rather
    than assuming "no rows" meant "never assessed": data.js carries this one
    study under a Covidence-id-prefixed key while both CSV registers use its
    plain "Zhou 2025" -- not a missing assessment, a name that never matched.
    Confirmed via an exact-match audit of every study key against every CSV
    study name: this prefix is the only mismatch pattern that exists.
    """
    rows = by_study.get(study_key)
    if rows:
        return rows
    stripped = _STUDY_PREFIX_RE.sub("", study_key)
    if stripped != study_key:
        return by_study.get(stripped, [])
    return []


def _is_real_judgement(oc: dict) -> bool:
    """
    False for a cell whose status is "Assessed" but every domain field is the
    placeholder "--" -- an eligibility/reclassification bookkeeping note, not
    an actual RoB 2 judgement, so it structurally has no domain rationale to
    link to. Found while accounting for why one cell (Xie 2014's opioid_72h,
    outcome_name "Eligibility audit", rationale "EXCLUDE / reclassify A") had
    zero keyword candidates: it does not describe a result at all. Checked:
    it is the only such cell among the 75 "Assessed" entries.
    """
    return any((oc.get(d) or "").strip() not in ("", "—", "-")
               for d in ("d1", "d2", "d3", "d4", "d5", "overall"))


def build() -> dict:
    v34_rows = load_v34_rob2_rows()
    studies = load_studies()

    by_study: dict[str, list[dict]] = {}
    for row in v34_rows:
        by_study.setdefault(row["study"], []).append(row)

    links: dict[str, dict] = {}  # f"{study_id}::{bucket}" -> link record
    total_assessed = 0
    for st in studies:
        for bucket, oc in (st.get("rob2_outcomes") or {}).items():
            if not isinstance(oc, dict) or oc.get("status") != "Assessed":
                continue
            if not _is_real_judgement(oc):
                continue
            total_assessed += 1
            candidates = _rows_for_study(by_study, st["key"])
            dash_value = (st.get("outcomes") or {}).get(bucket)
            match, method = find_link(bucket, candidates, oc.get("outcome_name") or "",
                                      _dashboard_denominator(dash_value))
            evidence_note = ""
            if not match:
                match, method = _apply_manual_override(st["key"], bucket, candidates)
                if match:
                    evidence_note = MANUAL_OVERRIDES[(st["key"], bucket)][1]
            if not match:
                continue
            links[f"{st['id']}::{bucket}"] = {
                "study": match["study"],
                "matched_outcome": match["outcome"],
                "matched_timepoint": match["timepoint"],
                "match_method": method,
                "domains": split_domains(match["rationale"]),
                "flags": match.get("flags") or "",
                "source_pdf": match.get("source_pdf") or "",
                "adopted_by": match.get("adopted_by") or "",
                "adopted_date": match.get("adopted_date") or "",
                **({"match_evidence": evidence_note} if evidence_note else {}),
            }

    if total_assessed == 0:
        raise SystemExit("no assessed RoB 2 results found -- data.js may be malformed")
    coverage = len(links) / total_assessed

    return {
        "generated_by": "scripts/build_rob2_source_links.py",
        "disclaimer": (
            "Links each RoB 2 matrix cell to the specific per-domain, source-quoted "
            "rationale and source PDF it has in the review's RoB 2 registers, where that "
            "link can be established without guessing -- an explicit keyword/timepoint rule "
            "matching exactly one candidate result for that study, a hard numeric match "
            "against the dashboard's own stored denominator, or (a small, individually-"
            "documented set of cases) a match hand-verified by reading the source PDF "
            "directly, listed in MANUAL_OVERRIDES in this script with the exact evidence "
            "read. Coverage is partial by construction: a cell with no entry here has no "
            "ambiguity-free match, not a missing quote -- see the dashboard's own note on "
            "those cells. No page number is given because none exists in the source "
            "registers; the source PDF filename is the exact locator available."),
        "total_assessed_results": total_assessed,
        "linked_count": len(links),
        "coverage": round(coverage, 4),
        "links": links,
    }


def main() -> int:
    payload = build()
    OUT.write_text(
        "// GENERATED by scripts/build_rob2_source_links.py -- do not hand-edit.\n"
        "// Partial by construction -- see disclaimer field. Keyed \"studyId::bucket\".\n"
        "window.ROB2_SOURCE_LINKS = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {payload['linked_count']} of {payload['total_assessed_results']} assessed "
          f"results linked to a specific source-quoted rationale ({payload['coverage']:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
