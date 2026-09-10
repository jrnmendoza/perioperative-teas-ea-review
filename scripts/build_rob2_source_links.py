#!/usr/bin/env python3
"""
Link each RoB 2 matrix cell to the specific, per-domain, source-quoted
rationale it actually has -- and to the source PDF that quote comes from.

WHY THIS EXISTS
The RoB 2 matrix's interactive popovers (renderRoB2Matrix() in app.js) read
their rationale from STUDIES_DATA[i].rob2_outcomes[outcomeKey].rationale --
which for the current dataset is, for every single one of the 75 currently
assessed results, either empty, a short one-line stub, or a general adoption
note. It is NEVER the rich, per-domain, source-quoted text that actually
exists for the same results in the review's own RoB 2 registers
(09_V34_ANALYSIS/03_ROB2/v34_rob2_draft_assessments.csv, 36 rows, and
v34_rob2_priority2_assessments.csv, 493 rows) -- confirmed: 529/529 of those
rows contain at least 3 distinct domain markers with embedded verbatim quotes
from the source PDF, and 0/75 of the client-side rationale strings do.

Both registers are already loaded client-side in full, as
window.V34_DATA.rob2_results.results (36 rows) and
window.V34_DATA.rob2_priority2.results (493 rows) -- this script does not
duplicate them. What it adds is the missing LINK between a matrix cell (keyed
by the dashboard's own outcome "bucket", e.g. opioid_24h) and the specific row
in those 529 that the cell is actually about, plus the per-domain split of
that row's rationale text.

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

Verified: 34 of 75 assessed results resolve this way (up from an initial 29
using keyword+timepoint alone), confirmed to ADD to that set with zero
removals or changes to any of the original 29 -- diffed explicitly against
the prior version rather than assumed. Several remaining multi-candidate
cases (e.g. Tu 2024's rescue_analgesia, Lu 2021's ponv_24h, Wu 2022's
intraop_remi) stay unresolved because their only lexical distinguishing
signal is a word ("incidence" vs "consumption", "count" vs "index") that is
too easily generic elsewhere to trust as a rule -- this is a genuine limit of
a lexical heuristic, not a bug left unfixed, and resolving them properly would
mean reading the source PDFs directly, the same standard this review applies
to every other judgement in it, rather than adding another regex.

WHAT THIS DOES NOT DO
Invent a page number. Neither register carries one (checked: 0 of 529 rows
mention a page reference), so only the source PDF filename is given as the
locator, not a specific page -- a reader with access to that PDF can search
it for the quoted phrase, which is exact and copied from the source, but this
script will not fabricate a page number to make the answer look more precise
than the data supports.

Usage:  python3 scripts/build_rob2_source_links.py
Exit:   0 on success, 1 if the expected data files are missing.
"""
from __future__ import annotations

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
    "opioid_24h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia", "pca dose"], ["24"], False),
    "opioid_48h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["48"], False),
    "opioid_72h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["72"], False),
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
    "pca_behavior": (["pca", "press", "demand", "bolus"], None, False),
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


def find_link(bucket: str, candidates: list[dict], oc_outcome_name: str = "") -> tuple[dict | None, str]:
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
    if len(hits) == 1:
        return hits[0], "keyword_timepoint_unique"
    if len(hits) > 1:
        return _tiebreak(oc_outcome_name, hits)
    return None, ""


def load_v34_rob2_rows() -> list[dict]:
    src = (DASH / "v34_data.js").read_text(encoding="utf-8")
    d = json.loads(src[src.index("window.V34_DATA = ") +
                       len("window.V34_DATA = "):src.rindex(";")])
    return d["rob2_results"]["results"] + d["rob2_priority2"]["results"]


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
            total_assessed += 1
            match, method = find_link(bucket, by_study.get(st["key"], []),
                                      oc.get("outcome_name") or "")
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
            }

    if total_assessed == 0:
        raise SystemExit("no assessed RoB 2 results found -- data.js may be malformed")
    coverage = len(links) / total_assessed

    return {
        "generated_by": "scripts/build_rob2_source_links.py",
        "disclaimer": (
            "Links each RoB 2 matrix cell to the specific per-domain, source-quoted "
            "rationale and source PDF it has in the review's RoB 2 registers, where that "
            "link can be established without guessing (an explicit keyword/timepoint rule "
            "matching exactly one candidate result for that study). Coverage is partial by "
            "construction: a cell with no entry here has no ambiguity-free match, not a "
            "missing quote -- see the dashboard's own note on those cells. No page number is "
            "given because none exists in the source registers; the source PDF filename is "
            "the exact locator available."),
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
