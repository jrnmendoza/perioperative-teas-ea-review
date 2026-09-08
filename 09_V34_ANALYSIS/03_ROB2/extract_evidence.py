#!/usr/bin/env python3
"""Pull the RoB 2 domain-relevant sentences out of each source PDF, with page
locators, so each draft judgement is anchored to text an assessor can check.

This extracts evidence. It does not judge: the judgement is made by a person
reading the extracted quotes against the RoB 2 signalling questions.
"""
import json, re, sys
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
PDFS = ROOT / "TEAS EA Verification" / "Source PDFs"
HERE = Path(__file__).resolve().parent

# RoB 2 domains -> the terms that signal relevant text
DOMAIN = {
 "D1_randomisation": [r"random(ly|ised|ized|isation|ization|/)", r"allocat", r"conceal",
                      r"sealed envelope", r"opaque", r"computer[- ]generated", r"random number",
                      r"block(ed)? randomi", r"baseline characteristic", r"comparable at baseline"],
 "D2_deviations":    [r"blind", r"mask(ed|ing)", r"double[- ]blind", r"single[- ]blind",
                      r"unaware", r"intention[- ]to[- ]treat", r"\bITT\b", r"per[- ]protocol",
                      r"anesthesiologist (was|were) (not )?", r"investigator (was|were)",
                      r"identical (in )?appearance", r"same device"],
 "D3_missing":       [r"withdrew|withdrawn|withdrawal", r"drop(ped)?[- ]?out", r"lost to follow",
                      r"exclud(ed|ing) (from|after)", r"missing data", r"complet(ed|ers) the (study|trial)",
                      r"analys(ed|is) (set|population)", r"\bmITT\b", r"CONSORT"],
 "D4_measurement":   [r"outcome (was|were) (assessed|measured|recorded|evaluated)",
                      r"assessor", r"observer", r"investigator (who|blinded)",
                      r"visual analog", r"\bVAS\b", r"numeric(al)? rating", r"\bNRS\b",
                      r"QoR-?40", r"nausea and vomiting (was|were)", r"PONV was",
                      r"recorded by", r"(first )?(flatus|defecation|bowel sound)",
                      r"patient[- ]controlled", r"\bPCA\b|\bPCIA\b", r"consumption (was|were)"],
 "D5_reporting":     [r"registered|registration|registry", r"ChiCTR|NCT\d|UMIN|IRCT|ISRCTN|ACTRN",
                      r"protocol", r"primary (outcome|endpoint)", r"secondary (outcome|endpoint)",
                      r"sample size", r"power (analysis|calculation)", r"pre[- ]?specified"],
}
CTX = 260

def sentences(text):
    text = re.sub(r"-\n(?=[a-z])", "", text)          # de-hyphenate line breaks
    text = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.;])\s+(?=[A-Z(])", text)

def main():
    mapping = json.loads((HERE / "pdf_map.json").read_text())
    only = sys.argv[1:] or list(mapping)
    # Merge into whatever evidence.json already holds rather than replacing it:
    # passing specific study names on the command line (the normal way to add
    # newly-mapped studies without re-extracting everyone) previously wrote out
    # a file containing ONLY those studies, silently discarding every other
    # study's evidence already on disk.
    out_path = HERE / "evidence.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {}
    for study in only:
        pdf = mapping.get(study)
        if not pdf:
            continue
        doc = pymupdf.open(PDFS / pdf)
        pages = [(i + 1, p.get_text()) for i, p in enumerate(doc)]
        doc.close()
        found = {d: [] for d in DOMAIN}
        seen = set()
        for pno, ptxt in pages:
            for s in sentences(ptxt):
                s = s.strip()
                if not (30 < len(s) < 600):
                    continue
                for dom, pats in DOMAIN.items():
                    if any(re.search(p, s, re.I) for p in pats):
                        key = (dom, s[:90])
                        if key in seen:
                            continue
                        seen.add(key)
                        found[dom].append({"p": pno, "quote": s[:CTX]})
        out[study] = {"pdf": pdf, "pages": len(pages), "evidence": found}
    out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for s, v in out.items():
        n = sum(len(x) for x in v["evidence"].values())
        print(f"{s:<28} {v['pdf']:<40} {v['pages']:>3}pp  {n:>3} quotes  " +
              " ".join(f"{d.split('_')[0]}={len(v['evidence'][d])}" for d in DOMAIN))

main()
