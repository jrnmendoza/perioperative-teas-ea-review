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
    "Yeh 2011": "015_PainATHM-2.pdf",              # Altern Ther Health Med 2010;16(6)
    "Yeh 2010": "covidence_828_full_article.pdf",  # Int J Nurs Stud 2011;48(6), spinal surgery
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
    return re.sub(r"[ \t]+", " ", t.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl"))


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
# and "enrolled" must not be treated as randomised -- Jin 2023 enrolled 174 and
# says 29 of them were never randomised. Thousands separators are required or
# Gao 2022's 1,655 is silently read as 655.
RE_RANDOMISED = re.compile(
    r"(\d[\d,]{1,6})\s+(?:eligible\s+|adult\s+|consecutive\s+|female\s+|male\s+)?"
    r"(?:patients|participants|women|men|subjects)\b"
    r"(?P<gap>[^.]{0,40}?)"
    r"\b(?:were\s+|was\s+)?(?:randomi[sz]ed|randomly\s+(?:assigned|allocated|divided|distributed))", re.I)

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

# Anaesthesia must be the trial's own protocol, not a literature mention. Require
# a protocol verb nearby and reject anything that looks like a citation.
RE_ANAES = re.compile(
    r"\b(general|spinal|epidural|combined spinal[- ]epidural|total intravenous|regional)\s+"
    r"an(?:a)?esthesia\b", re.I)
RE_ANAES_CONTEXT = re.compile(
    r"\b(underwent|undergoing|scheduled|received|induced|maintained|performed under|"
    r"operated under|carried out under|surgery under)\b", re.I)

WORD_NUM = {"two": 2, "three": 3, "four": 4, "2": 2, "3": 3, "4": 4}


def collect(pages, pattern, accept):
    """Run `pattern` over every page; return {value: [(page, quote), ...]}."""
    found: dict = {}
    for pno, raw in pages:
        text = norm(raw)
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
        try:
            n = int(m.group(1).replace(",", ""))
        except ValueError:
            return None
        return n if 10 <= n <= 5000 else None

    r = decide(collect(pages, RE_RANDOMISED, randomised), "randomised N")
    if r: rec["randomised_n"] = r

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
    for pno, raw in pages:
        text = norm(raw)
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
        if not RE_ANAES_CONTEXT.search(q):
            return None
        return (m.group(1).strip().lower().replace("total intravenous", "total intravenous")
                + " anaesthesia").capitalize()
    an = decide(collect(pages, RE_ANAES, anaes), "anaesthesia")
    if an: rec["anaesthesia"] = an

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

    fields = ("randomised_n", "arms", "pulse_width", "anaesthesia")
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
