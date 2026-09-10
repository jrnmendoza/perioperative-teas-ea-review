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
dashboard outcome bucket (BUCKET_RULES below), and only records a link when
EXACTLY ONE row in that study's contributions satisfies the rule --
"zero matches" and "more than one match" are both left unlinked rather than
guessed at. Verified: 29 of 75 assessed results resolve to exactly one
candidate this way. That is genuine, checkable coverage; it is not claimed to
be complete, and the dashboard says so for the cells it cannot link.

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

# (keyword regexes to require in "family outcome", OR'd; timepoint substrings
# that must appear, ANY'd -- or None if the bucket has no time window at all).
# Deliberately conservative: under-matching (leaving a cell unlinked) is the
# safe failure mode here, over-matching (linking the wrong result) is not.
BUCKET_RULES = {
    "opioid_24h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia", "pca dose"], ["24"]),
    "opioid_48h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["48"]),
    "opioid_72h": (["opioid", "morphine", "fentanyl", "sufentanil", "tramadol",
                    "mme", "pcia"], ["72"]),
    "pain_rest_24h": (["pain", "vas", "nrs"], ["24"]),
    "ponv_24h": (["ponv", "nausea.*vomit", "composite"], ["24"]),
    "ponv_48h": (["ponv", "nausea.*vomit", "composite"], ["48"]),
    "nausea_24h": (["nausea"], ["24"]),
    "nausea_48h": (["nausea"], ["48"]),
    "vomiting_24h": (["vomit"], ["24"]),
    "vomiting_48h": (["vomit"], ["48"]),
    "flatus_time": (["flatus"], None),
    "rescue_analgesia": (["rescue"], None),
    "intraop_remi": (["remifentanil"], None),
    "pca_behavior": (["pca", "press", "demand", "bolus"], None),
    "qor_24h": (["qor", "quality of recovery"], ["24"]),
}
ALL_WINDOWS = ("24", "48", "72")


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


def row_text(row: dict) -> str:
    return f"{row.get('family', '')} {row.get('outcome', '')}".lower()


def find_link(bucket: str, candidates: list[dict]) -> dict | None:
    rule = BUCKET_RULES.get(bucket)
    if not rule or not candidates:
        return None
    keywords, timepoints = rule
    hits = []
    for row in candidates:
        text = row_text(row)
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
    return hits[0] if len(hits) == 1 else None


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
            match = find_link(bucket, by_study.get(st["key"], []))
            if not match:
                continue
            links[f"{st['id']}::{bucket}"] = {
                "study": match["study"],
                "matched_outcome": match["outcome"],
                "matched_timepoint": match["timepoint"],
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
