#!/usr/bin/env python3
"""
Extract a small set of trial characteristics from the source PDFs.

WHY THIS IS SHAPED THE WAY IT IS
--------------------------------
This review has already been burned once by plausible-looking values that
matched no source (see 99_audit/2026-09-10_placeholder_incident/). So this
extractor is deliberately conservative and fully auditable:

  * every accepted value carries the PDF, the page, and the VERBATIM sentence
    it came from -- nothing is stored that cannot be pointed back at a quote;
  * a value is accepted ONLY when the tight pattern for it produces a single
    consistent answer across the whole paper. Conflicting matches are recorded
    as `conflict` and treated as not reported, never resolved by guessing;
  * anything not matched stays absent, which the dashboard renders as NR.
    Nothing is inferred from the title, the abstract, or a sister trial.

Two requested variables are deliberately NOT extracted. A yield scan over all
70 PDFs found preoperative/baseline pain in 3 papers and baseline opioid
exposure in 4, and on inspection essentially all of those hits were false
positives -- reference-list titles ("Chronic Opioid Use after Surgery: ...")
and regression prose rather than a reported baseline. Extracting them would
have produced mostly wrong values, so they are reported as not recoverable.

Usage:  python3 scripts/extract_baseline_from_pdfs.py [--report]
Writes: dashboard/pdf_extracted.js  (generated; do not hand-edit)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "TEAS EA Verification" / "Source PDFs"
OUT_JS = ROOT / "dashboard" / "pdf_extracted.js"

# Studies whose PDF filename is not recoverable from the RoB 2 registers.
# Resolved by matching each paper's title and journal against its citation.
EXTRA_PDFS = {
    # Identity re-assigned 2026-09-12 to the convention used by Outcome_Data_AF_LOCK
    # and every other file holding arm-level data; see
    # 05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md.
    "Yeh 2010": "015_PainATHM-2.pdf",              # Altern Ther Health Med 2010;16(6)
    "Yeh 2011": "covidence_828_full_article.pdf",  # Int J Nurs Stud 2011;48(6), spinal surgery
    "El-Rakshy 2009": "covidence_868_full_article.pdf",
    "Coura 2011": "covidence_819_full_article.pdf",
    "Ao 2021": "download.pdf",
    "Wu 2016": "wu2015.pdf",
    "#105119 - Zhou 2025": "105119.pdf",
}

# "et al" without a trailing period still means the sentence is describing
# somebody else's trial -- Ng 2013's discussion of "this study by Meng et al, 16
# 90 patients were randomized" was being read as Ng's own randomised total.
CITATION_NOISE = re.compile(
    r"\bet al\b|doi:|https?://|\bPubMed\b|\bCrossRef\b|^\s*\d+\.\s|"
    r"\b(?:previous|prior|another|other)\s+(?:study|studies|trial|trials)\b|"
    r"\bin\s+(?:a|one|this)\s+study\s+by\b", re.I)


def norm(t: str) -> str:
    t = t.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    # "P.R. China" / "R.O.C." carry periods, and the affiliation pattern below
    # stops at a period so it cannot span sentences. Without this, every Chinese
    # affiliation written "Nanjing, Jiangsu, P.R. China" is invisible -- which is
    # exactly why Yang 2020 first resolved to its Australian collaborator.
    t = re.sub(r"\bP\.\s*R\.\s*(?=China)", "", t, flags=re.I)
    t = re.sub(r"\bPeople'?s Republic of China\b", "China", t, flags=re.I)
    return re.sub(r"[ \t]+", " ", t)


def sentence_around(text: str, start: int, end: int) -> str:
    lo = max(text.rfind(". ", 0, start), text.rfind("\n", 0, start)) + 1
    hi = text.find(". ", end)
    hi = len(text) if hi == -1 else hi + 1
    return re.sub(r"\s+", " ", text[lo:hi]).strip()[:300]


# ── Extractors ──────────────────────────────────────────────────────────────
# Each returns (value, quote) or None for one regex match.

# Anchored on the randomisation verb, then looking BACK a short distance for the
# nearest participant count. Scanning forwards instead picks up the wrong number
# in "Of 140 patients screened, 71 patients were randomly assigned" (Szmit 2021),
# and "enrolled" must not be treated as randomised. (The Jin 2023 example this
# comment used to cite was wrong, and is corrected in RANDOMISED_N_NOTES below:
# 174 IS that trial's randomised number. The guard is still right in general --
# Szmit 2021's "Of 140 patients screened, 71 patients were randomly assigned" is
# the case it exists for.) Thousands separators are required or
# Gao 2022's 1,655 is silently read as 655.
# Added 2026-09-12: the count is very often spelled out, and requiring digits
# was losing clean totals that the paper states in its first line of Methods --
# Sim 2002's "Ninety patients were randomly assigned", Yu 2020's "Sixty patients
# ... were randomly assigned". CARDINAL_WORDS parses those; it deliberately
# handles only 10-999, the range a surgical RCT's randomised total falls in.
RE_RANDOMISED = re.compile(
    r"(?P<count>\d[\d,]{1,6}|(?:one|two|three|four|five|six|seven|eight|nine)?\s*hundred(?:\s+and)?"
    r"(?:\s+(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety))?(?:[\s-]"
    r"(?:one|two|three|four|five|six|seven|eight|nine))?"
    r"|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[\s-]"
    r"(?:one|two|three|four|five|six|seven|eight|nine))?"
    r"|(?:ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen))"
    r"\s+(?:eligible\s+|adult\s+|consecutive\s+|female\s+|male\s+)?"
    r"(?:patients|participants|women|men|subjects|cases)\b"
    r"(?P<gap>[^.]{0,40}?)"
    r"\b(?:were\s+|was\s+)?(?:randomi[sz]ed|randomly\s+(?:assigned|allocated|divided|distributed))", re.I)

ONES = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9}
TENS = {"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,
        "eighty":80,"ninety":90}
TEENS = {"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
         "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19}


def cardinal(text):
    """'ninety-nine' -> 99; 'one hundred and twenty' -> 120; digits pass through.

    Returns None rather than guessing on anything this grammar does not cover.
    """
    t = text.strip().lower().replace("-", " ")
    t = re.sub(r"\band\b", " ", t)
    if re.fullmatch(r"[\d,]+", t):
        try:
            return int(t.replace(",", ""))
        except ValueError:
            return None
    words = t.split()
    total = 0
    if "hundred" in words:
        i = words.index("hundred")
        total = 100 * (ONES.get(words[i - 1], 1) if i else 1)
        words = words[i + 1:]
    rest = 0
    for w in words:
        if w in TENS:
            rest += TENS[w]
        elif w in TEENS:
            rest += TEENS[w]
        elif w in ONES:
            rest += ONES[w]
        elif w:
            return None
    return (total + rest) or None


# A randomised total DERIVED by adding up group sizes the paper states in the
# randomisation sentence itself. Kept in its own field, never merged with a
# directly stated total: "four groups of 25 each" is arithmetic on reported
# numbers, not a figure the paper prints.
RE_PER_GROUP = re.compile(
    r"randomi[sz]ed|randomly\s+(?:assigned|allocated|divided|distributed)", re.I)
RE_GROUPS_OF = re.compile(
    r"\b(?:in)?to\s+(?:one\s+of\s+)?(two|three|four|five|2|3|4|5)\s+"
    r"(?:equal\s+)?(?:groups?|treatment\s+regimens?|regimens?|arms?)\b"
    r"[^.]{0,60}?\b(?:of|with|each\s+with|containing)\s+"
    r"\(?\s*n\s*[=\u00bc]?\s*(\d{1,4})|"
    r"\b(?:in)?to\s+(?:one\s+of\s+)?(two|three|four|five|2|3|4|5)\s+"
    r"(?:equal\s+)?(?:groups?|treatment\s+regimens?|regimens?|arms?)\b"
    r"[^.]{0,60}?\bof\s+(\d{1,4})\s+(?:each|patients|participants|cases)", re.I)
RE_N_EACH = re.compile(
    r"\(\s*n\s*[=\u00bc]\s*(\d{1,4})\s*(?:for\s+)?(?:each(?:\s+group)?|per\s+group)\s*\)", re.I)
RE_N_PER_GROUP = re.compile(r"\bwith\s+(\d{1,4})\s+(?:patients|participants|cases)\s+per\s+group\b", re.I)
RE_N_ARM = re.compile(r"\(\s*n\s*[=\u00bc]\s*(\d{1,4})\s*\)", re.I)
GROUP_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5,
               "2": 2, "3": 3, "4": 4, "5": 5}

# A SECOND-STAGE randomisation: the count belongs to a sub-randomisation within
# already-formed groups, not to the trial's randomised total. Wang 2024 writes
# "Seventy patients from each group were then randomly allocated into the ...
# treatment subgroups" -- 70 PER GROUP, into subgroups, in a trial whose analysed
# total is 138. Without this guard that reads as a randomised total of 70.
RE_SUBRANDOMISED = re.compile(
    r"\b(?:from|in|of)\s+each\s+group\b|\bsub\s?groups?\b|\bfurther\s+randomi[sz]|"
    r"\bwithin\s+each\s+group\b|\beach\s+group\s+(?:was|were)\s+(?:then\s+)?randomi[sz]", re.I)

# ── Two further ways a paper states its randomised total, added 2026-09-12 ──
#
# A. A CONSORT FLOW-DIAGRAM LABEL. The count sits in a box as a label plus a
#    number, never in a sentence, so the sentence-based pass cannot see it:
#    Liang 2021's "Randomized (n = 75)", Seevaunnamtum 2016's "Randomisation
#    n = 64". The trap is the box directly above it -- Liang 2021 also prints
#    "Assessed for eligibility (n = 80)", and 80 is not the randomised number.
#    So the label must be a randomisation label and must not be preceded by an
#    eligibility/screening/enrolment word.
RE_CONSORT_LABEL = re.compile(
    r"\brandomi[sz](?:ed|ation|sed)\b[^\d\n]{0,18}?\(?\s*n\s*[=:\u00bc]\s*(\d{2,4})", re.I)

# B. A TOTAL THE PAPER CORROBORATES WITH ITS OWN ARMS. Jiang 2026 writes "614
#    eligible patients were allocated to the TEAS (n = 308) or sham-TEAS
#    (n = 306) group" and Luo 2026 "277 patients who underwent randomization
#    ... (TEAS group, n = 138; Sham-TEAS group, n = 139)". In both the stated
#    total equals the sum of the stated arms, which is the strongest evidence
#    available short of a flow diagram: the paper checks itself. Nothing is
#    inferred -- the total is accepted only because the arms reproduce it
#    exactly, so a sentence where they do not is rejected rather than summed.
RE_TOTAL_CANDIDATE = re.compile(
    r"(\d[\d,]{1,5})\s+(?:eligible\s+|adult\s+|consecutive\s+|female\s+|male\s+)?"
    r"(?:patients|participants|women|men|subjects|cases)\b", re.I)
RE_RANDOMISE_ANY = re.compile(
    r"randomi[sz]ed|randomi[sz]ation|randomly\s+(?:assigned|allocated|divided|distributed)"
    r"|were\s+allocated\s+to", re.I)


def consort_label_randomised(pages):
    """Rule A: a randomisation label in a flow diagram.

    TIGHTENED 2026-09-12 after its first run produced three wrong values and one
    unprovable one. Taking the first n= after a randomisation word is right in a
    flow-diagram box and wrong in a prose sentence, where that number is an ARM:
    Hou 2023's "randomized into either TEAS (n = 37) or control (n = 37)" gave 37
    for a trial of 74, Zhang 2018's "randomized to TEA (n = 21) and sham-TEA
    (n = 21)" gave 21 for 42, and Xie 2014's "(n=20 for each group)" across three
    groups gave 20 for 60. Liu 2026 (ESD) produced a 120 that its own quote did
    not contain at all.

    So a candidate is rejected unless it behaves like a total: a total is never
    equal to one of the arms printed beside it, and is never smaller than their
    sum. Where arms are visible, they arbitrate.
    """
    cands = {}
    for pno, text in body_pages(pages):
        t = re.sub(r"\s+", " ", norm(text))
        for m in RE_CONSORT_LABEL.finditer(t):
            before = t[max(0, m.start() - 46):m.start()]
            if RE_NOT_RANDOMISED.search(before) or RE_SUBRANDOMISED.search(before):
                continue
            n = int(m.group(1))
            if not (10 <= n <= 5000):
                continue
            ctx = t[max(0, m.start() - 70):m.end() + 170]
            # A per-group qualifier makes the number an arm by definition:
            # Xie 2014's "3 groups ... ( n=20 for each group)" is 20 PER ARM.
            if re.search(r"\b(?:for\s+)?each\s+group|per\s+group|each\s*\)", ctx, re.I):
                continue
            # Count EVERY parenthesised n in the context, including ones equal to
            # the candidate. Filtering those out was the bug that let Hou 2023
            # (37, 37) and Zhang 2018 (21, 21) through: when a trial's two arms
            # are the same size, the sibling that proves the number is an arm is
            # exactly the one a "different from n" filter discards.
            siblings = [int(x) for x in RE_N_ARM.findall(ctx) if int(x) > 0]
            if len(siblings) >= 2 and n in siblings and sum(siblings) != n:
                # The candidate is one of several sibling counts, so it is an arm,
                # not their total.
                continue
            others = [x for x in siblings if x != n]
            if len(others) >= 2 and n < sum(sorted(others)[-2:]):
                continue
            # The number has to be visible in the evidence we are about to store.
            quote = t[max(0, m.start() - 60):m.end() + 60].strip()
            if str(n) not in quote.replace(",", ""):
                continue
            cands.setdefault(n, []).append((pno, quote))
    return decide(cands, "randomised N (flow-diagram label)")


# A sentence that establishes the allocation was RANDOM, for papers whose
# total-bearing sentence uses CONSORT's "allocated to" instead. Jiang 2026 states
# "Patients were randomized into the TEAS or sham-TEAS groups at a 1:1 ratio using
# block randomization" on one page and prints its total on the next; the total is
# only a RANDOMISED total because of the first sentence, so both are stored and a
# value that cannot show either is refused.
RE_RANDOM_ALLOCATION_PROOF = re.compile(
    r"[^.]{0,200}\b(?:were\s+randomi[sz]ed|randomly\s+(?:assigned|allocated)|"
    r"randomi[sz]ation\s+sequence|block\s+randomi[sz]ation)\b[^.]{0,160}\.", re.I)


def randomisation_proof(pages):
    """The paper's own statement that allocation was random, if it makes one."""
    for pno, text in body_pages(pages):
        t = norm(text)
        for m in RE_RANDOM_ALLOCATION_PROOF.finditer(t):
            q = re.sub(r"\s+", " ", m.group()).strip()
            if CITATION_NOISE.search(q) or len(q) < 30:
                continue
            return {"page": pno, "quote": q[:300]}
    return None


def self_corroborated_randomised(pages):
    """Rule B: a stated total that equals the sum of the arms stated beside it."""
    cands = {}
    for pno, text in body_pages(pages):
        t = norm(text)
        for m in RE_RANDOMISE_ANY.finditer(t):
            q = sentence_around(t, m.start(), m.end())
            if CITATION_NOISE.search(q) or RE_SUBRANDOMISED.search(q):
                continue
            # A CONSORT flow diagram has no sentence punctuation, so
            # sentence_around() returns the whole blob and the "arms" it yields can
            # be from any stage of the diagram. Liu 2026 (ESD) summed its two
            # "Analyzed (n=58)" / "Analyzed (n=62)" boxes to 120 and offered it as a
            # randomised total -- the analysed denominator standing in for a
            # randomised one, which is the single substitution this field exists to
            # prevent. Two guards: refuse an undelimited blob, and refuse any
            # context carrying analysis-stage or attrition labels.
            if len(q) > 400:
                continue
            if re.search(r"analy[sz]ed|excluded\s+from\s+analysis|lost\s+to\s+follow", q, re.I):
                continue
            arms = [int(x) for x in RE_N_ARM.findall(q)]
            if len(arms) < 2:
                continue
            total = sum(arms)
            if not (10 <= total <= 5000):
                continue
            # The paper must PRINT that same total in the same sentence.
            printed = {int(x.replace(",", "")) for x, in
                       ((g,) for g in RE_TOTAL_CANDIDATE.findall(q))}
            if total not in printed:
                continue
            cands.setdefault(total, []).append((pno, re.sub(r"\s+", " ", q).strip()))
    got = decide(cands, "randomised N (total corroborated by its own arms)")
    if got and "value" in got and not re.search(r"randomi[sz]", got["quote"], re.I):
        # The total-bearing sentence says "allocated" rather than "randomised", so
        # it alone does not prove the number is a RANDOMISED total. Attach the
        # paper's own randomisation statement, or refuse the value.
        proof = randomisation_proof(pages)
        if not proof:
            return None
        got["randomisation_quote"] = proof["quote"]
        got["randomisation_page"] = proof["page"]
    return got


# Accepted values whose source sentence looks wrong until the paper's own
# arithmetic is checked. The note travels with the value so a reader who spots the
# same oddity finds it already adjudicated instead of re-opening it.
RANDOMISED_N_NOTES = {
    "Jin 2023":
        "Adjudicated 2026-09-12 by re-reading the source. The paper says \"174 eligible "
        "patients were enrolled ... and 29 were not randomized\", which reads as though the "
        "randomised total should be 174 - 29 = 145. It cannot be: the three arms are stated "
        "as n = 58 each and sum to exactly 174. The paper's own figures reconcile the other "
        "way -- 453 planned, 250 excluded leaves 203 eligible, and 203 - 29 not randomised "
        "gives 174 randomised. So 174 is the randomised number and \"enrolled\" is the loose "
        "word in that sentence; the enrolled figure its arithmetic implies is 203. No value "
        "changed as a result of this check.",
}

# Reports whose whole-trial randomised N is under an adjudicated, UNRESOLVABLE
# dispute. Quarantined here rather than extracted, because the papers themselves
# disagree and picking one would be inventing it -- the record is
# 05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md.
RANDOMISED_N_QUARANTINE = {
    "Yeh 2010": "Yeh 2010 prints 99 but its own Table 2 gives 33/30/31 = 94, and the "
                "companion report Yeh 2011 gives 90. Three mutually contradictory figures "
                "for one cohort; adjudicated 2026-09-12 as unresolvable from the "
                "publications.",
    "Yeh 2011": "Companion report of Yeh 2010. Its 30/30/30 is the pairwise contrast the "
                "review uses and is not disputed, but the whole-trial randomised total is "
                "part of the same unresolvable 90/94/99 dispute.",
}

# Words that mean the preceding count is NOT the randomised total.
RE_NOT_RANDOMISED = re.compile(
    # Stems, not whole words: "exclu" covers excluded/excluding/exclusion, which
    # matters because Sun 2017 writes "After exclusion of 55 patients, 380 ...".
    r"\b(screen|exclu|assessed for eligibility|enrol|eligib|approached|recruit|consent|"
    r"withdrew|withdrawn|dropped out|lost to follow)", re.I)

RE_ARMS = re.compile(
    r"\brandomly\s+(?:assigned|allocated|divided|distributed)\s+(?:in)?to\s+"
    r"(two|three|four|2|3|4)\s+(?:equal\s+)?groups?\b", re.I)

# Any "<number> <time unit>" inside a sentence already known to be about pulse width.
RE_DURATION = re.compile(r"(\d+(?:\.\d+)?)\s*(ms|msec|milliseconds?|[µuμ]s|microseconds?)\b", re.I)

RE_PULSE = re.compile(
    r"(?:pulse[\s-]*(?:width|duration)|wave[\s-]*width)[^.]{0,70}?"
    r"(\d+(?:\.\d+)?)\s*(ms|msec|milliseconds?|[µuμ]s|microseconds?)", re.I)

# Anaesthesia must be the trial's OWN protocol. An earlier version accepted any
# technique named in a sentence that also contained a protocol-ish verb, which
# was both too loose and too strict: it missed "scheduled for thyroidectomy under
# general anesthesia" (Chen 2015) because the verb fell outside the sentence
# split, and it turned Lu 2022 into a false conflict by accepting "when the
# patients received epidural anaesthesia" -- a sentence about somebody else's
# trial.
#
# Matching on PHRASE SHAPE instead fixes both. These are the forms a paper uses
# to state its own technique; "received"/"undergoing" are deliberately NOT among
# them, because they are equally natural when describing prior literature.
# Note this also excludes "local anaesthetic agents" (a drug, not a technique):
# only "local anaesthesia" can match.
_TECH = r"(general|spinal|epidural|combined spinal[- ]epidural|total intravenous|regional|local)"
RE_ANAES = re.compile(
    rf"(?:under|was|were)\s+{_TECH}\s+an(?:a)?esthesia\b"
    rf"|{_TECH}\s+an(?:a)?esthesia\s+(?:was|were)\s+"
    rf"(?:induced|maintained|administered|used|performed|given|achieved)"
    rf"|\(\s*{_TECH}\s+an(?:a)?esthesia", re.I)


# Country of the conducting centre, read from the AUTHOR AFFILIATION block.
# Anchored on an affiliation noun so it cannot pick up a journal's editorial
# front matter: Gao 2022's first page lists "Edited by: ... University of
# Pittsburgh, United States" and "Reviewed by: ... Capital Medical University,
# China" above the authors, and a bare country scan reads the editor's country.
COUNTRY_NAMES = [
    "China", "Taiwan", "Hong Kong", "Poland", "Turkey", "Brazil", "Greece",
    "United Kingdom", "Germany", "Iran", "India", "Egypt", "Thailand",
    "Singapore", "Japan", "Malaysia", "Spain", "Italy", "Denmark", "Sweden",
    "Norway", "Netherlands", "Australia", "Canada", "United States",
]
RE_AFFIL = re.compile(
    r"(Department|Dept\.|School|College|Institute|Hospital|Centre|Center|Clinic|Faculty|University)"
    r"[^.;]{0,160}?\b(" + "|".join(re.escape(c) for c in COUNTRY_NAMES) + r")\b", re.I)
# Front-matter that names other people's countries, never the trial's.
RE_EDITORIAL = re.compile(r"edited by|reviewed by|specialty section|received:|accepted:|published:", re.I)
# "Republic of Korea" / "South Korea" need their own spelling.
RE_KOREA = re.compile(r"\b(?:Republic of Korea|South Korea)\b", re.I)

WORD_NUM = {"two": 2, "three": 3, "four": 4, "2": 2, "3": 3, "4": 4}


RE_REFS_HEADING = re.compile(r"^\s*(references|reference list|bibliography)\s*$", re.I | re.M)


def strip_references(text: str) -> str:
    """Drop everything from a References heading onward.

    A reference list is full of sentences that look exactly like protocol
    statements -- "...after cesarean section under spinal anesthesia" (Gu 2019)
    and "...somato-visceral pain under epidural anesthesia" (Jin 2023) are
    citation TITLES, and both were being read as those trials' own technique.
    They carry no "et al" or doi on the matched line, so the citation filter
    could not see them.
    """
    m = RE_REFS_HEADING.search(text)
    return text[:m.start()] if m else text


def body_pages(pages):
    """Pages before the reference list, with the partial page truncated.

    The cutoff has to be DOCUMENT-level, not per page: a reference list starting
    on page 12 runs onto page 13, and a per-page rule leaves page 13 fully
    readable. That is how Liu 2015 -- a craniotomy trial -- acquired "spinal
    anaesthesia" from a cesarean-delivery citation, and Zhang 2025 acquired
    "combined spinal-epidural" the same way.
    """
    out, hit_refs = [], False
    for pno, raw in pages:
        if hit_refs:
            break
        text = norm(raw)
        m = RE_REFS_HEADING.search(text)
        if m:
            hit_refs = True
            text = text[:m.start()]
        out.append((pno, text))
    return out


def collect(pages, pattern, accept):
    """Run `pattern` over every page; return {value: [(page, quote), ...]}."""
    found: dict = {}
    for pno, text in body_pages(pages):
        for m in pattern.finditer(text):
            quote = sentence_around(text, m.start(), m.end())
            if CITATION_NOISE.search(quote):
                continue
            val = accept(m, quote, text)
            if val is None:
                continue
            found.setdefault(val, []).append((pno, quote))
    return found


def decide(found, label):
    """One consistent value -> accept with evidence. Otherwise report a conflict."""
    if not found:
        return None
    if len(found) == 1:
        value, hits = next(iter(found.items()))
        pno, quote = hits[0]
        return {"value": value, "page": pno, "quote": quote, "hits": len(hits)}
    return {"conflict": sorted(str(v) for v in found),
            "note": f"{label}: the paper yielded more than one candidate; "
                    f"not resolved automatically"}


def derive_randomised_from_groups(pages):
    """A randomised total added up from group sizes stated in the randomisation
    sentence. Separate from randomised_n on purpose: this is arithmetic on
    reported numbers, and a reader must be able to see the sum.

    Three shapes are accepted, all requiring the randomisation verb in the same
    sentence:
      "randomly assigned to one of four regimens (n = 25 each)"   -> 4 x 25
      "randomized into 4 groups with 95 patients per group"       -> 4 x 95
      "randomised to electroacupuncture (n = 56) or control (n = 46)" -> 56 + 46

    The third shape is the loosest, so it is accepted only when the sentence
    yields at least two per-arm counts and, where the paper also states an arm
    count, exactly that many. Anything else returns None and the field stays NR.
    """
    cands = {}
    for pno, text in body_pages(pages):
        t = norm(text)
        for m in RE_PER_GROUP.finditer(t):
            q = sentence_around(t, m.start(), m.end())
            if CITATION_NOISE.search(q) or RE_NOT_RANDOMISED.search(q):
                continue
            arms_m = re.search(r"\b(?:in)?to\s+(?:one\s+of\s+)?(two|three|four|five|2|3|4|5)\s+"
                               r"(?:equal\s+)?(?:groups?|treatment\s+regimens?|regimens?|arms?)\b",
                               q, re.I)
            arms = GROUP_WORDS.get(arms_m.group(1).lower()) if arms_m else None

            total, how = None, None
            g = re.search(r"\b(?:groups?|regimens?|arms?)\s+of\s+(\d{1,4})\s+each\b", q, re.I)
            per = RE_N_EACH.search(q) or RE_N_PER_GROUP.search(q) or g
            if per and arms:
                each = int(per.group(1))
                total, how = arms * each, f"{arms} groups x {each} each"
            elif not RE_SUBRANDOMISED.search(q):
                # Only counts that come AFTER the randomisation verb can be arms.
                # Li 2021 writes "gery (n = 105) and colorectal surgery (n = 201),
                # and were randomly assigned to group T or group S" -- those are
                # SURGERY-TYPE subgroups standing before the verb, and summing them
                # gave 306 for a trial with 140/140. Position is what separates an
                # arm from any other parenthesised n.
                vpos = RE_PER_GROUP.search(q)
                tail = q[vpos.end():] if vpos else ""
                per_arm = [int(x) for x in RE_N_ARM.findall(tail)]
                if len(per_arm) >= 2 and (arms is None or len(per_arm) == arms):
                    total = sum(per_arm)
                    how = " + ".join(str(x) for x in per_arm)
            if total is None or not (10 <= total <= 5000):
                continue
            cands.setdefault((total, how), []).append((pno, re.sub(r"\s+", " ", q).strip()))

    if not cands:
        return None
    totals = {t for (t, _) in cands}
    if len(totals) > 1:
        return {"conflict": sorted(str(t) for t in totals),
                "note": "derived randomised N: the paper's group sizes gave more than one "
                        "total; not resolved automatically"}
    (total, how), hits = next(iter(cands.items()))
    pno, quote = hits[0]
    return {"value": total, "page": pno, "quote": quote, "derivation": how,
            "hits": len(hits)}


def extract_one(pages):
    rec = {}

    def randomised(m, q, text=""):
        # Reject when the words between the count and the verb say the count is
        # a screening/enrolment figure rather than the number randomised.
        if RE_NOT_RANDOMISED.search(m.group("gap") or ""):
            return None
        # The disqualifying word can also sit BEFORE the count: Sun 2017's
        # "After exclusion of 55 patients, 380 patients were randomized" has the
        # exclusion count first, so look back a little as well.
        if RE_NOT_RANDOMISED.search(text[max(0, m.start() - 34):m.start()]):
            return None
        # ... or when the sentence explicitly removes people before randomisation.
        if re.search(r"\bnot\s+randomi[sz]ed\b", q, re.I):
            return None
        if RE_SUBRANDOMISED.search(q):
            return None
        n = cardinal(m.group("count"))
        if n is None:
            return None
        return n if 10 <= n <= 5000 else None

    r = decide(collect(pages, RE_RANDOMISED, randomised), "randomised N")
    # A total the paper corroborates with its own arms is at least as good as one
    # read from a bare sentence, and a flow-diagram label is the paper's own
    # CONSORT statement. Both count as STATED, not derived.
    if not (r and "value" in r):
        r = self_corroborated_randomised(pages) or r
    if not (r and "value" in r):
        r = consort_label_randomised(pages) or r
    if r: rec["randomised_n"] = r

    # Derived channel. Only runs when no total was stated directly, and only on a
    # sentence whose own verb is randomisation -- so an (n = ...) that belongs to
    # an ANALYSED subgroup elsewhere in the paper cannot reach it.
    if "randomised_n" not in rec:
        d = derive_randomised_from_groups(pages)
        if d: rec["randomised_n_derived"] = d

    a = decide(collect(pages, RE_ARMS, lambda m, q, text="": WORD_NUM.get(m.group(1).lower())), "arm count")
    if a: rec["arms"] = a

    # Pulse width is the one field where several values are CORRECT rather than
    # contradictory: a dense-disperse protocol states one width per frequency
    # (Li 2021: "2 Hz for 0.6 ms and 100 Hz for 0.2 ms"). Reporting only the
    # first would misdescribe the intervention, so join the distinct values.
    # The anchor ("pulse width" / "wave width") appears once, but the sentence can
    # state a width per frequency. Once an anchor is found, harvest every
    # duration in that same sentence rather than only the nearest one.
    widths, evidence = [], None
    for pno, text in body_pages(pages):
        for m in RE_PULSE.finditer(text):
            sent = sentence_around(text, m.start(), m.end())
            if CITATION_NOISE.search(sent):
                continue
            for dm in RE_DURATION.finditer(sent):
                unit = "ms" if dm.group(2).lower().startswith(("ms", "mil")) else "µs"
                val = f"{dm.group(1)} {unit}"
                if val not in widths:
                    widths.append(val)
            if evidence is None:
                evidence = (pno, sent)
    if widths and evidence:
        rec["pulse_width"] = {
            "value": " / ".join(sorted(widths, key=lambda v: float(v.split()[0]), reverse=True)),
            "page": evidence[0], "quote": evidence[1], "hits": len(widths),
        }

    def anaes(m, q, text=""):
        # The technique is whichever alternative in RE_ANAES matched.
        tech = next((g for g in m.groups() if g), None)
        if not tech:
            return None
        return (tech.strip().lower() + " anaesthesia").capitalize()
    # Anaesthesia is not a free variable in this review: the protocol makes
    # general anaesthesia an ELIGIBILITY CRITERION, verified at study selection
    # ("Adults ... undergoing an operative surgical procedure under general
    # anaesthesia"), and explicitly allows it "alone or with balanced regional or
    # neuraxial anaesthesia or analgesia". So a paper naming both general and
    # spinal anaesthesia is not contradicting itself and is not a conflict -- it
    # is describing the permitted combination. TIVA is likewise a general
    # technique, not an alternative to one.
    #
    # What is therefore worth extracting is not "which anaesthetic?" but the
    # reported DETAIL: the general technique as the paper words it, plus any
    # regional/neuraxial adjunct it names.
    GENERAL = {"General anaesthesia", "Total intravenous anaesthesia"}
    techniques = collect(pages, RE_ANAES, anaes)
    if techniques:
        general = sorted(v for v in techniques if v in GENERAL)
        adjuncts = sorted(v for v in techniques if v not in GENERAL)
        if general:
            # Keep the paper's OWN wording as the value -- TIVA is a general
            # technique, but a value of "General anaesthesia" would not be
            # literally provable from a quote that says "total intravenous
            # anesthesia [TIVA]", and every stored value here must be checkable
            # against its own quote. The general-vs-adjunct classification is
            # carried separately.
            ev = techniques[general[0]][0]
            rec["anaesthesia"] = {
                "value": general[0], "page": ev[0], "quote": ev[1],
                "is_general": True,
                "hits": sum(len(v) for v in techniques.values()),
                **({"adjuncts": adjuncts,
                    "note": "the paper also reports " + ", ".join(a.lower() for a in adjuncts)
                            + " -- the protocol permits general anaesthesia alone or combined with "
                              "regional or neuraxial anaesthesia"} if adjuncts else {}),
            }
        else:
            # Only regional/neuraxial named and no general technique stated. That
            # would contradict the eligibility criterion, so surface it rather
            # than quietly recording a technique.
            ev = techniques[adjuncts[0]][0]
            rec["anaesthesia"] = {
                "conflict": adjuncts,
                "note": "no general-anaesthesia statement found, only "
                        + ", ".join(a.lower() for a in adjuncts)
                        + "; the review's eligibility criterion requires general anaesthesia, so "
                          "this needs checking against the paper",
                "page": ev[0], "quote": ev[1],
            }

    # Country: affiliations live on the first page or two. Take the country named
    # in the FIRST affiliation phrase that is not inside editorial front matter;
    # that is the conducting centre. Multiple distinct countries across the
    # affiliation block are reported as a conflict rather than guessed at.
    # Collect every affiliation country in document order, then prefer the one
    # carrying the superscript-1 marker. Taking merely the first REGEX match is
    # not enough: in Yang 2020 affiliations 1 and 2 do not name a country in a
    # form this pattern sees, so the first match is affiliation 3 (RMIT,
    # Australia) -- a collaborator, not the conducting centre.
    found = []
    for pno, raw in pages[:2]:
        text = norm(raw)
        for m in RE_AFFIL.finditer(text):
            if RE_EDITORIAL.search(text[max(0, m.start() - 120):m.end()]):
                continue
            name = m.group(2)
            name = {"uk": "United Kingdom", "usa": "United States"}.get(name.lower(), name.title())
            lead = bool(re.search(r"(?:^|[^\d])1\s*$", text[max(0, m.start() - 4):m.start()]))
            found.append({"country": name, "page": pno,
                          "quote": sentence_around(text, m.start(), m.end()), "lead": lead})
        if RE_KOREA.search(text) and not any(f["country"].endswith("Korea") for f in found):
            found.append({"country": "Republic of Korea", "page": pno,
                          "quote": "Republic of Korea", "lead": False})
    if found:
        distinct = sorted({f["country"] for f in found})
        lead = next((f for f in found if f["lead"]), None)
        if len(distinct) == 1:
            pick = found[0]
        elif lead is not None:
            pick = lead
        else:
            # Several countries and no affiliation explicitly marked as the lead.
            # Yang 2020 is exactly this: its affiliation 1 (Nanjing) names no
            # country at all, so the only country-bearing affiliation is the
            # Australian collaborator at number 3. Picking the first match would
            # assert the wrong conducting centre, so refuse instead.
            rec["country"] = {"conflict": distinct,
                              "note": "country: several affiliation countries and no affiliation "
                                      "marked as the lead centre; not resolved automatically"}
            pick = None
        if pick is not None:
            others = [c for c in distinct if c != pick["country"]]
            rec["country"] = {
                "value": pick["country"], "page": pick["page"], "quote": pick["quote"],
                "hits": sum(1 for f in found if f["country"] == pick["country"]),
                **({"note": "marked as affiliation 1 (lead centre); the paper also lists "
                            + ", ".join(others)} if others else {}),
            }

    # Surgical population, for trials whose characteristics record has none.
    # Deliberately narrow: only an explicit "<N> patients undergoing <procedure>"
    # style statement, and only the phrase itself.
    for pno, text in body_pages(pages):
        m = re.search(r"\b(?:patients?|participants?|subjects?|women|men)\s+(?:with\s+[\w ]{3,30}\s+)?"
                      r"(?:who\s+)?(?:underwent|undergoing)\s+([a-z][^.;,()]{6,70})", text, re.I)
        if m and not CITATION_NOISE.search(sentence_around(text, m.start(), m.end())):
            rec["surgical_population"] = {
                "value": m.group(1).strip().rstrip(" and"),
                "page": pno, "quote": sentence_around(text, m.start(), m.end()), "hits": 1}
            break

    return rec


def build(pdf_map):
    import pypdf
    out = {}
    for key, fname in sorted(pdf_map.items()):
        path = PDF_DIR / fname
        if not path.exists():
            continue
        reader = pypdf.PdfReader(path)
        pages = [(i, p.extract_text() or "") for i, p in enumerate(reader.pages, 1)]
        rec = extract_one(pages)
        if key in RANDOMISED_N_NOTES and isinstance(rec.get("randomised_n"), dict):
            rec["randomised_n"]["adjudication"] = RANDOMISED_N_NOTES[key]
        if key in RANDOMISED_N_QUARANTINE:
            for f in ("randomised_n", "randomised_n_derived"):
                rec.pop(f, None)
            rec["randomised_n_quarantined"] = {
                "reason": RANDOMISED_N_QUARANTINE[key],
                "record": "05_study_linkage/cohorts/yeh_lumbar_spinal_surgery.md"}
        rec["source_pdf"] = fname
        out[key] = rec
    return out


def resolve_pdf_map():
    import csv
    m = json.loads((ROOT / "09_V34_ANALYSIS/03_ROB2/pdf_map.json").read_text())
    for f in (ROOT / "09_V34_ANALYSIS/03_ROB2").glob("*.csv"):
        with f.open(encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                if r.get("study") and r.get("source_pdf"):
                    m.setdefault(r["study"].strip(), r["source_pdf"].strip())
    m.update(EXTRA_PDFS)
    studies = json.JSONDecoder().raw_decode(
        (ROOT / "dashboard/data.js").read_text(encoding="utf-8")
        .split("window.STUDIES_DATA = ", 1)[1])[0]
    keys = {s["key"] for s in studies}
    return {k: v for k, v in m.items() if k in keys and (PDF_DIR / v).exists()}


def main() -> int:
    pdf_map = resolve_pdf_map()
    records = build(pdf_map)
    OUT_JS.write_text(
        "// Generated by scripts/extract_baseline_from_pdfs.py; do not edit.\n"
        "// Every value carries the source PDF, page and verbatim quote it came from.\n"
        "window.PDF_EXTRACTED = " + json.dumps(records, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8")

    fields = ("randomised_n", "randomised_n_derived", "arms", "pulse_width",
              "anaesthesia", "country")
    total = len(records)
    print(f"PDFs read: {total}/70")
    for f in fields:
        ok = sum(1 for r in records.values() if isinstance(r.get(f), dict) and "value" in r[f])
        clash = sum(1 for r in records.values() if isinstance(r.get(f), dict) and "conflict" in r[f])
        print(f"  {f:14} accepted {ok:2}/70   unresolved conflicts {clash}")
    if "--report" in sys.argv:
        for k, r in sorted(records.items()):
            bits = [f"{f}={r[f].get('value', 'CONFLICT')}" for f in fields if f in r]
            print(f"  {k:26} {', '.join(bits) or '(nothing extracted)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
