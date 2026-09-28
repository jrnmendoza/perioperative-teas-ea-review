"""Check that every citing sentence in the current manuscript has a claim-citation audit row.

references/current_claim_citation_audit.csv holds one row per citing sentence of manuscript/{ABSTRACT..CONCLUSIONS}.md:
the sentence, its citekeys and reference numbers, the source checked and a verdict. This script re-extracts the citing
sentences and fails when a sentence or its citekeys changed without the audit being updated, when a citekey is not in
references/bibliography.csv, or when a row's verdict is outside the fixed vocabulary.

Usage: python3 references/check_claim_citation_audit.py [--write-skeleton]
  --write-skeleton  print CSV rows (verdict blank) for sentences missing from the audit, for the checker to fill in.
"""
import csv, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECTIONS = ['ABSTRACT', 'INTRODUCTION', 'METHODS', 'RESULTS', 'DISCUSSION', 'CONCLUSIONS']
AUDIT = ROOT / 'references/current_claim_citation_audit.csv'
VERDICTS = ('Supported', 'Supported with qualification', 'Partly supported', 'Not supported')
COLS = ['claim_id', 'section', 'claim', 'citekeys', 'reference_numbers', 'identifiers', 'source_checked', 'verdict', 'note', 'checked_by']

def citing_sentences():
    """(section, sentence, [citekeys]) for every sentence carrying a [@key] citation outside draft-status notes."""
    out = []
    for sec in SECTIONS:
        text = (ROOT / f'manuscript/{sec}.md').read_text(encoding='utf-8')
        for para in re.split(r'\n\s*\n', text):
            if para.lstrip().startswith('>'):
                continue                    # draft-status and author-decision notes are not manuscript claims
            flat = ' '.join(para.split())
            for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z*])', flat):
                keys = [k for c in re.findall(r'\[(@[^\]]+)\]', sent) for k in re.findall(r'@([A-Za-z0-9_:-]+)', c)]
                if keys:
                    out.append((sec, sent, keys))
    return out

def main():
    bib = {r['key']: r for r in csv.DictReader(open(ROOT / 'references/bibliography.csv', encoding='utf-8'))}
    rows = list(csv.DictReader(open(AUDIT, encoding='utf-8'))) if AUDIT.exists() else []
    audited = {(r['section'], r['claim']): r for r in rows}
    errs, missing = [], []
    for sec, sent, keys in citing_sentences():
        errs += [f'{sec}: unknown citekey @{k}' for k in keys if k not in bib]
        r = audited.get((sec, sent))
        if not r:
            missing.append((sec, sent, keys)); continue
        if r['citekeys'] != '; '.join(keys): errs.append(f'{r["claim_id"]}: citekeys changed ({r["citekeys"]} -> {"; ".join(keys)})')
        if r['reference_numbers'] != '; '.join(bib[k]['number'] for k in keys if k in bib): errs.append(f'{r["claim_id"]}: reference numbers differ from bibliography.csv')
        if r['verdict'] not in VERDICTS: errs.append(f'{r["claim_id"]}: bad verdict {r["verdict"]!r}')
        if r['verdict'] != 'Supported' and not r['note']: errs.append(f'{r["claim_id"]}: a qualified verdict needs a note')
    current = {(s, t) for s, t, _ in citing_sentences()}
    errs += [f'{r["claim_id"]}: audited sentence no longer in the manuscript' for r in rows if (r['section'], r['claim']) not in current]
    errs += [f'{s}: citing sentence not audited: {t[:90]}' for s, t, _ in missing]
    if '--write-skeleton' in sys.argv:
        w = csv.DictWriter(sys.stdout, COLS)
        for i, (s, t, k) in enumerate(missing, 1):
            w.writerow(dict(claim_id=f'NEW-{i}', section=s, claim=t, citekeys='; '.join(k), reference_numbers='; '.join(bib[x]['number'] for x in k if x in bib),
                            identifiers='; '.join(f"PMID {bib[x]['pmid']}" if bib[x]['pmid'] else f"doi {bib[x]['doi']}" for x in k if x in bib)))
    if errs:
        print('\n'.join('FAIL ' + e for e in errs)); return 1
    from collections import Counter
    print(f'PASS claim-citation audit: {len(rows)} citing sentences, {len({k for r in rows for k in r["citekeys"].split("; ")})} references;', dict(Counter(r['verdict'] for r in rows)))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
