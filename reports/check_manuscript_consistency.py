#!/usr/bin/env python3
"""Consistency checks for the BMC Anesthesiology manuscript (Phase 23).

Compares every number and certainty word in a manuscript draft against the
canonical adjudication outputs, so the manuscript cannot silently contain a
value the analysis does not produce.

Usage:
    python3 reports/check_manuscript_consistency.py path/to/manuscript.docx
    python3 reports/check_manuscript_consistency.py path/to/manuscript.md

Exit status is 1 if any ERROR-level finding is raised.

What it checks
    1.  Study, report and trial-unit counts are internally consistent and match
        the canonical registry.
    2.  Participant totals match the registry, and the operational count is not
        described as an analysed or efficacy population.
    3.  Every "MD ... (95% CI ...)" in the text matches a model in
        model_outputs.csv to within rounding.
    4.  Every risk ratio in the text matches a model.
    5.  No superseded value from v26/v33/v34/v36/v37 or the stale dashboard
        appears anywhere.
    6.  The correct PROSPERO identifier is used and the wrong one is absent.
    7.  Certainty words near a model name agree with grade.csv.
    8.  Abstract and Results do not disagree on k, N or the primary estimate.
    9.  No forbidden phrasing: "pooled" applied to a k=1 body, prospective
        registration, "no deviations", upgraded GRADE, two-independent-reviewer
        claims for the v38 assessments.
    10. Reference numbers are contiguous and every one is cited in the text.
    11. Numbers that appear in tables also appear, unchanged, in the text.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "10_FINAL_ADJUDICATION" / "03_CANONICAL"
MODELS = ROOT / "10_FINAL_ADJUDICATION" / "04_MODELS"
REPORTS = ROOT / "10_FINAL_ADJUDICATION" / "06_REPORTS"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PROSPERO_CORRECT = "CRD420261452908"
PROSPERO_WRONG = "CRD420251090635"

# Values from superseded versions and the stale public dashboard. Any of these
# appearing in a manuscript means a number was inherited rather than derived.
SUPERSEDED = {
    "-13.99": "v33/v36 TEAS-vs-sham k=4; now a labelled sensitivity diagnostic",
    "13.99": "v33/v36 TEAS-vs-sham k=4; now a labelled sensitivity diagnostic",
    "-14.00": "v33/v36 TEAS-vs-sham k=4; now a labelled sensitivity diagnostic",
    "-9.91": "superseded k=7 combined TEAS+EA; modality pooling is prohibited",
    "10,618": "unsupported dashboard participant KPI",
    "10618": "unsupported dashboard participant KPI",
    "-7.95": "previous manuscript pooled 48 h estimate",
    "-7.9 MME": "previous manuscript pooled 48 h estimate",
    "1,176": "previous manuscript participant total",
    "1 176": "previous manuscript participant total",
    "n = 922": "previous manuscript pooled n",
    "n=922": "previous manuscript pooled n",
    "RR 0.30": "previous manuscript PONV estimate; current is RR 0.640",
    "-16.5": "previous manuscript flatus estimate; current is -4.983 h",
    "-5.335": "v37 flatus estimate; v38 is -4.983 h after the Zheng 2025 removal",
    "-7.191": "v37 bowel-sounds estimate; v38 is -6.086 h and crosses the null",
    "-114.8": "v37 intraoperative remifentanil; v38 is -175.702 ug",
    "I2 = 94": "previous manuscript heterogeneity for a model that no longer exists",
    "I2=94": "previous manuscript heterogeneity for a model that no longer exists",
}

FORBIDDEN_PHRASES = [
    (r"registered\s+prospectively|prospectively\s+registered",
     "Prospective conduct is not established; the associate editor rejected this claim once",
     "prospective"),
    (r"no\s+amendments\s+were\s+made",
     "Four dated amendments exist"),
    (r"no\s+deviations\s+occurred",
     "Two potential deviations and one unresolved item are recorded"),
    (r"upgrad(ed|ing)\s+(for|to)\b.{0,60}(certainty|GRADE|moderate)",
     "GRADE upgrading is not applied; RCT bodies are not upgraded"),
    (r"large\s+effect.{0,40}upgrad",
     "GRADE upgrading is not applied"),
    (r"two\s+reviewers\s+independently\s+assessed",
     "v38 assessments are AI-conducted under author delegation, not two independent human reviews"),
    (r"all\s+(analytical\s+)?(code\s+and\s+)?output.{0,40}validated\s+by\s+the\s+authors",
     "This exact claim was used against the previous submission"),
    (r"American\s+Pain\s+Society",
     "Superseded conversion policy; see FINAL_MME_CONVERSION_POLICY.md"),
    (r"auricular|press[- ]tack|wrist[- ]ankle|buccal\s+acupuncture",
     "Out of scope under the registered TEAS/EA definitions", "modality"),
    (r"back[- ]transform.{0,40}pooled\s+SD",
     "SMD back-transformation is not part of the current method"),
    (r"\bMCID\b.{0,60}\b8\s*(mg\s*)?(IV[- ])?MME",
     "8 mg is a sensitivity threshold; the registered primary threshold is 10 mg with paired pain"),
]

# A forbidden pattern is exempt when the surrounding window shows it is being
# negated, defined as out of scope, or quoted as a starting point. Without this,
# a correctly written Methods section trips every rule it is complying with.
EXEMPTION_WINDOW = 450
EXEMPTIONS = {
    "prospective": [r"\bnot\b", r"\bdo not\b", r"\bdoes not\b", r"\bcannot\b",
                    r"\bwithout claiming\b", r"\brather than\b"],
    "modality": [r"\bexclud", r"\bnot eligible\b", r"\bout of scope\b",
                 r"\bineligible\b", r"\bwere excluded\b", r"\bwe excluded\b"],
    "high_certainty": [r"start(s|ed|ing)?\s+at\b", r"begin(s|ning)?\s+at\b"],
    "wrong_crd": [r"separate", r"broader review", r"does not describe",
                  r"not identify", r"must not", r"belongs to"],
}


def exempt(text: str, start: int, end: int, kind: str) -> bool:
    back = 900 if kind == "modality" else EXEMPTION_WINDOW
    window = text[max(0, start - back): end + EXEMPTION_WINDOW]
    return any(re.search(p, window, re.I) for p in EXEMPTIONS.get(kind, []))


PLURAL_K1_PATTERN = re.compile(
    r"pooled\s+(estimate|analysis|result)s?\b.{0,120}?\b(k\s*=\s*1|single[- ]study)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class Finding:
    level: str          # ERROR | WARN | INFO
    check: str
    message: str
    context: str = ""


@dataclass
class Canon:
    studies: list = field(default_factory=list)
    models: dict = field(default_factory=dict)
    e2_models: dict = field(default_factory=dict)   # post-hoc E2 sensitivity outputs
    grade: dict = field(default_factory=dict)

    @property
    def n_reports(self) -> int:
        return len(self.studies)

    @property
    def n_randomized(self) -> int:
        return sum(
            s["randomized_n_counted"]
            for s in self.studies
            if isinstance(s.get("randomized_n_counted"), (int, float))
        )


def load_canon() -> Canon:
    c = Canon()
    c.studies = json.loads((CANON / "studies.json").read_text())
    with (MODELS / "model_outputs.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row.get("model_id") or row.get("model") or row.get("id")
            if key:
                c.models[key] = row
    # Outputs of the separate analyses whose estimates the manuscript also reports.
    for tag, path in (("E2", MODELS.parent / "09_E2_ANALYSIS" / "e2_model_outputs.csv"),
                      ("QOR", MODELS.parent / "08_QOR_ANALYSIS" / "qor_models.csv"),
                      ("QOR_LATER", MODELS.parent / "08_QOR_ANALYSIS" / "qor_models_later.csv")):
        if path.exists():
            with path.open(newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    if row.get("model_id"):
                        c.e2_models[f"{tag}:" + row["model_id"]] = row
    with (CANON / "grade.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            c.grade[row["model_id"]] = row
    return c


def extract_text(path: Path) -> tuple[str, list[str]]:
    """Return (body_text, table_cell_texts)."""
    if path.suffix.lower() == ".docx":
        z = zipfile.ZipFile(path)
        root = ET.fromstring(z.read("word/document.xml"))
        body = root.find(W + "body")
        paras, cells = [], []

        def para_text(p):
            return "".join(t.text or "" for t in p.iter(W + "t"))

        def walk(node, in_table=False):
            for ch in node:
                if ch.tag == W + "p":
                    (cells if in_table else paras).append(para_text(ch))
                elif ch.tag == W + "tbl":
                    walk(ch, in_table=True)
                else:
                    walk(ch, in_table)

        walk(body)
        return "\n".join(paras), cells

    text = path.read_text(encoding="utf-8")
    cells = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    return text, cells


def num(s: str) -> float | None:
    try:
        return float(s.replace("−", "-").replace(",", ""))
    except ValueError:
        return None


def close(a: float, b: float, tol: float = 0.06) -> bool:
    """Tolerant to the rounding a manuscript legitimately applies."""
    return abs(a - b) <= max(tol, abs(b) * 0.01)


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_counts(text: str, c: Canon) -> list[Finding]:
    out = []
    # Only flag counts that actually claim to be the INCLUDED-report total.
    # "224 reports sought", "31 reports were judged high risk" and "across 40
    # reports" are legitimate PRISMA-flow and risk-of-bias statements.
    incl = re.compile(
        r"(?:(\d+)\s+included\s+reports?"
        r"|(\d+)\s+reports?\s+(?:were\s+)?includ"
        r"|includ\w*\s+(\d+)\s+reports?"
        r"|(\d+)\s+reports?\s+representing)", re.I)
    for m in incl.finditer(text):
        r = next(g for g in m.groups() if g)
        if int(r) not in (c.n_reports, 69):
            out.append(Finding("ERROR", "counts",
                               f"'{m.group(0).strip()}' does not match the canonical "
                               f"{c.n_reports} included reports / 69 trial families"))
    if re.search(r"\b14\s+RCTs?\b", text, re.I):
        out.append(Finding("ERROR", "counts",
                           "'14 RCTs' is the previous manuscript's count"))
    if re.search(r"\btrials?\b", text, re.I) and not re.search(
            r"trial (famil|unit)", text, re.I):
        out.append(Finding("INFO", "counts",
                           "Check that 'trials' vs 'reports' vs 'trial families' "
                           "is used consistently (70 / 69)"))
    return out


def check_participants(text: str, c: Canon) -> list[Finding]:
    out = []
    total = c.n_randomized
    for m in re.finditer(r"([\d][\d, ]{3,})\s+(?:randomi[sz]ed\s+)?(?:adults?|participants?|patients?)",
                         text, re.I):
        v = num(m.group(1))
        if not v or v <= 1000 or int(v) == total:
            continue
        # A count inside a cited sentence belongs to the cited study, not to
        # this review. Background sections legitimately quote large cohorts.
        # Sentence bounds must ignore decimal points ("48.7%", "7.15%"),
        # otherwise the sentence is truncated before its citation marker.
        bound = re.compile(r"[.;](?=\s|$)")
        starts = [mm.end() for mm in bound.finditer(text, 0, m.start())]
        lo = starts[-1] if starts else 0
        nxt = bound.search(text, m.end())
        hi = nxt.end() if nxt else len(text)
        sentence = text[lo:hi]
        if re.search(r"\[@[^\]]+\]|\[\d{1,3}(?:[,\u2013-]\s*\d{1,3})*\]", sentence):
            continue
        out.append(Finding("ERROR", "participants",
                           f"'{m.group(1).strip()}' does not match the canonical "
                           f"randomized total {total}", m.group(0)))
    if str(total) in text or f"{total:,}" in text:
        window = ""
        for m in re.finditer(re.escape(str(total)) + r"|" + re.escape(f"{total:,}"), text):
            window += text[max(0, m.start() - 200): m.end() + 200]
        if not re.search(r"operational", window, re.I):
            out.append(Finding("ERROR", "participants",
                               f"{total} must be described as an operational randomized "
                               "count, not an analysed or efficacy population"))
    return out


def _match_model(est, lo, hi, pool):
    hit, ci_ok = None, False
    for mid, row in pool.items():
        for ekey, lokey, hikey in (("effect", "ci_low", "ci_high"),
                                   ("display_effect", "display_ci_low", "display_ci_high")):
            mv = num(str(row.get(ekey, "")))
            if mv is None or not close(est, mv):
                continue
            hit = mid
            mlo, mhi = num(str(row.get(lokey, ""))), num(str(row.get(hikey, "")))
            if (lo is None or mlo is None or close(lo, mlo)) and \
               (hi is None or mhi is None or close(hi, mhi)):
                return mid, True
    return hit, ci_ok


# Manuscript style: "−7.70 (−10.62 to −4.78)" or "−6.17 mg IV MME (−12.47 to 0.14)",
# including table cells. Added 2026-09-23 after a negative control showed the
# "MD ... (95% CI ...)" pattern alone never fired on the Results text.
BARE_EFFECT = re.compile(
    r"(?<![\d.])(−?-?\d+\.\d+)\s*(?:mg IV MME|mg|points|µg|h)?\s*"
    r"\((−?-?\d+\.\d+)\s+to\s+(−?-?\d+\.\d+)\)")


def check_effects(text: str, c: Canon) -> list[Finding]:
    """Match 'MD -7.70 (95% CI -10.62 to -4.78)' style statements to a model."""
    out = []
    covered = []
    pat = re.compile(
        r"(?:MD|mean difference|RR|risk ratio)\s*[:=]?\s*"
        r"(−?-?\d+\.?\d*)\s*"
        r"\(?\s*95\s*%?\s*CI\s*[:=]?\s*"
        r"(−?-?\d+\.?\d*)\s*(?:to|,|–|-)\s*(−?-?\d+\.?\d*)",
        re.I)
    for m in pat.finditer(text):
        covered.append(m.span())
        est, lo, hi = (num(m.group(i)) for i in (1, 2, 3))
        if est is None:
            continue
        hit = None
        ci_ok = False
        for mid, row in c.models.items():
            for ekey, lokey, hikey in (("effect", "ci_low", "ci_high"),
                                       ("display_effect", "display_ci_low", "display_ci_high")):
                mv = num(str(row.get(ekey, "")))
                if mv is None or not close(est, mv):
                    continue
                hit = mid
                mlo, mhi = num(str(row.get(lokey, ""))), num(str(row.get(hikey, "")))
                if (lo is None or mlo is None or close(lo, mlo)) and \
                   (hi is None or mhi is None or close(hi, mhi)):
                    ci_ok = True
                break
            if ci_ok:
                break
        if hit is None:
            out.append(Finding("ERROR", "effects",
                               f"Estimate {est} ({lo} to {hi}) matches no model in "
                               "model_outputs.csv", m.group(0)))
        elif not ci_ok:
            out.append(Finding("ERROR", "effects",
                               f"Estimate {est} matches model '{hit}' but the reported "
                               f"interval ({lo} to {hi}) does not", m.group(0)))
    pool = {**c.models, **c.e2_models}
    for m in BARE_EFFECT.finditer(text):
        if any(a <= m.start() < b for a, b in covered):
            continue
        est, lo, hi = (num(m.group(i)) for i in (1, 2, 3))
        if est is None:
            continue
        hit, ci_ok = _match_model(est, lo, hi, pool)
        if hit is None:
            out.append(Finding("ERROR", "effects",
                               f"Estimate {est} ({lo} to {hi}) matches no model in "
                               "model_outputs.csv, the E2 outputs or the QoR outputs", m.group(0)))
        elif not ci_ok:
            out.append(Finding("ERROR", "effects",
                               f"Estimate {est} matches model '{hit}' but the reported "
                               f"interval ({lo} to {hi}) does not", m.group(0)))
    return out


def check_superseded(text: str) -> list[Finding]:
    out = []
    low = text.lower()
    for token, why in SUPERSEDED.items():
        if token.lower() in low:
            out.append(Finding("ERROR", "superseded",
                               f"Superseded value '{token}' present: {why}"))
    return out


def check_registration(text: str) -> list[Finding]:
    out = []
    for m in re.finditer(re.escape(PROSPERO_WRONG), text):
        if exempt(text, m.start(), m.end(), "wrong_crd"):
            out.append(Finding("INFO", "registration",
                               f"{PROSPERO_WRONG} appears, but in disambiguating context"))
            continue
        out.append(Finding("ERROR", "registration",
                           f"{PROSPERO_WRONG} belongs to the similar broader review"))
    # The registration number belongs in the Abstract and Methods. Only require
    # it when one of those is present, so a section-only draft does not fail.
    needs_id = re.search(r"^#*\s*(Abstract|Methods)\s*$", text, re.I | re.M)
    if needs_id and PROSPERO_CORRECT not in text:
        out.append(Finding("ERROR", "registration",
                           f"{PROSPERO_CORRECT} is missing"))
    elif not needs_id and PROSPERO_CORRECT not in text:
        out.append(Finding("INFO", "registration",
                           "No Abstract/Methods section here; registration ID not required"))
    return out


def check_certainty(text: str, c: Canon) -> list[Finding]:
    out = []
    words = r"(very low|low|moderate|high)"
    for mid, row in c.grade.items():
        for m in re.finditer(re.escape(mid), text, re.I):
            window = text[max(0, m.start() - 250): m.end() + 250]
            found = {w.lower() for w in re.findall(words, window, re.I)}
            expect = row["certainty"].lower()
            if found and not any(expect.startswith(f) or f in expect for f in found):
                out.append(Finding("ERROR", "certainty",
                                   f"{mid}: text near it says {sorted(found)}, "
                                   f"grade.csv says '{row['certainty']}'"))
    for m in re.finditer(r"\bhigh[- ]certainty\b", text, re.I):
        if exempt(text, m.start(), m.end(), "high_certainty"):
            continue
        out.append(Finding("ERROR", "certainty",
                           "No body in this review is rated High certainty",
                           m.group(0)))
    return out


def check_abstract_vs_results(text: str) -> list[Finding]:
    out = []
    # Only meaningful once an Abstract section exists. Matching on a bare word
    # "Background" mid-sentence (e.g. "distinguished from background claims")
    # would otherwise treat most of a section draft as the abstract.
    m_abs = re.search(r"^#*\s*Abstract\s*$", text, re.I | re.M)
    if not m_abs:
        return [Finding("INFO", "abstract",
                        "No Abstract section in this file; abstract checks skipped")]
    rest = text[m_abs.end():]
    m_end = re.search(r"^#*\s*(?:Background|Introduction)\s*$", rest, re.I | re.M)
    if not m_end:
        return [Finding("INFO", "abstract", "Could not locate the abstract boundary")]
    abstract, body = rest[:m_end.start()], rest[m_end.end():]

    def numbers(s):
        return set(re.findall(r"−?-?\d+\.\d+", s))

    for v in numbers(abstract):
        if v not in body:
            out.append(Finding("ERROR", "abstract",
                               f"Abstract reports {v}, which does not appear in the body"))
    for m in re.finditer(r"\bk\s*=\s*(\d+)", abstract):
        if f"k = {m.group(1)}" not in body and f"k={m.group(1)}" not in body:
            out.append(Finding("WARN", "abstract",
                               f"Abstract reports k={m.group(1)}; confirm the body agrees"))
    if len(abstract.split()) > 350:
        out.append(Finding("ERROR", "abstract",
                           f"Abstract is {len(abstract.split())} words; BMC allows 350"))
    if not re.search(r"CRD420261452908\s*\.?\s*$", abstract.strip(), re.M):
        out.append(Finding("WARN", "abstract",
                           "BMC requires the registration number as the last abstract line"))
    return out


def check_forbidden(text: str) -> list[Finding]:
    out = []
    for entry in FORBIDDEN_PHRASES:
        pat, why = entry[0], entry[1]
        kind = entry[2] if len(entry) > 2 else None
        for m in re.finditer(pat, text, re.I):
            if kind and exempt(text, m.start(), m.end(), kind):
                continue
            out.append(Finding("ERROR", "phrasing", why, m.group(0)[:80]))
    if PLURAL_K1_PATTERN.search(text):
        out.append(Finding("ERROR", "phrasing",
                           "A k=1 body is described as pooled; policy requires a "
                           "study contrast with a within-study normal CI"))
    return out


def check_references(text: str) -> list[Finding]:
    out = []
    # A numbered reference list only exists once the bibliography is written.
    # Without this guard, a wrapped line beginning "10." (e.g. "...Additional
    # file\n10.") is mistaken for a reference entry.
    if not re.search(r"^#*\s*References\s*$", text, re.I | re.M):
        return out
    cited = {int(n) for n in re.findall(r"\[(\d{1,3})(?:[,–-]\s*\d{1,3})*\]", text)}
    for grp in re.findall(r"\[([\d,\s–-]+)\]", text):
        for n in re.findall(r"\d{1,3}", grp):
            cited.add(int(n))
    listed = {int(m.group(1)) for m in re.finditer(r"^\s*(\d{1,3})\.\s+\w", text, re.M)}
    if listed:
        missing = sorted(listed - cited)
        if missing:
            out.append(Finding("ERROR", "references",
                               f"Listed but never cited: {missing}"))
        dangling = sorted(n for n in cited - listed if n <= max(listed))
        if dangling:
            out.append(Finding("ERROR", "references",
                               f"Cited but not in the reference list: {dangling}"))
        gaps = sorted(set(range(1, max(listed) + 1)) - listed)
        if gaps:
            out.append(Finding("ERROR", "references",
                               f"Reference numbering is not contiguous; missing {gaps}"))
    return out


def check_tables_vs_text(text: str, cells: list[str]) -> list[Finding]:
    out = []
    tnums = set()
    for cell in cells:
        tnums |= set(re.findall(r"−?-?\d+\.\d{2,}", cell))
    for v in sorted(tnums):
        if v not in text:
            out.append(Finding("WARN", "tables",
                               f"Table value {v} does not appear in the narrative text"))
    return out


def check_crossrefs(text: str) -> list[Finding]:
    out = []
    for kind in ("Table", "Figure", "Additional file"):
        cited = {int(n) for n in re.findall(rf"{kind}\s+(\d+)", text)}
        if cited:
            gaps = sorted(set(range(1, max(cited) + 1)) - cited)
            if gaps:
                out.append(Finding("WARN", "crossrefs",
                                   f"{kind} numbering skips {gaps}"))
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"not found: {path}")
        return 2

    canon = load_canon()
    text, cells = extract_text(path)
    all_text = text + "\n" + "\n".join(cells)

    findings: list[Finding] = []
    findings += check_counts(all_text, canon)
    findings += check_participants(all_text, canon)
    findings += check_effects(all_text, canon)
    findings += check_superseded(all_text)
    findings += check_registration(all_text)
    findings += check_certainty(all_text, canon)
    findings += check_abstract_vs_results(text)
    findings += check_forbidden(all_text)
    findings += check_references(all_text)
    findings += check_tables_vs_text(text, cells)
    findings += check_crossrefs(all_text)

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: (order[f.level], f.check))

    print(f"Manuscript: {path}")
    print(f"Canonical:  {canon.n_reports} reports, {canon.n_randomized} randomized, "
          f"{len(canon.models)} models, {len(canon.grade)} GRADE bodies\n")

    if not findings:
        print("No findings.")
        return 0

    for f in findings:
        ctx = f"  <<{f.context.strip()}>>" if f.context else ""
        print(f"[{f.level:5}] {f.check:14} {f.message}{ctx}")

    errors = sum(1 for f in findings if f.level == "ERROR")
    print(f"\n{errors} error(s), {len(findings) - errors} other finding(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
