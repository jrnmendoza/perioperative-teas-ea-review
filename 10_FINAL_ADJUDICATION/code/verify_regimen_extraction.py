"""Check the regimen extraction record (14_CHARACTERISTICS/regimen_extraction.csv) against the source texts.

The record holds four fields per included report that were not previously extracted: postoperative analgesia,
PCA regimen, rescue analgesia and cumulative intervention duration. Every extracted value must carry a verbatim
quote (and optionally a second one) that is found on the stated PDF page of the report's text layer; a field
with no statement in the report is recorded as "Not reported in source" with no value and no quote. Nothing is
inferred. The second_review column is 'pending' or '<initials>, <YYYY-MM-DD>: confirmed'. Exits non-zero on any failure and writes a hash manifest when the record passes.

Usage: python3 10_FINAL_ADJUDICATION/code/verify_regimen_extraction.py [--partial]
  --partial  allow reports that are not yet in the record (while extraction is in progress).
"""
import csv, functools, hashlib, json, pathlib, re, sys, unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
RECORD = D / '14_CHARACTERISTICS/regimen_extraction.csv'
FIELDS = ('postoperative_analgesia', 'pca_regimen', 'rescue_analgesia', 'cumulative_duration')
STATUSES = ('Extracted (PDF quote)', 'Not reported in source')
COLS = ['report_id', 'field', 'value', 'status', 'page', 'quote', 'page2', 'quote2', 'note', 'source_pdf', 'source_sha256', 'extracted_by', 'second_review']
registry = {s['report_id']: s for s in json.load(open(D / '03_CANONICAL/studies.json'))}

def norm(s):
    """Text-layer artifacts only: ligatures and compatibility forms (NFKC), control characters left by lost glyphs,
    soft hyphens, end-of-line hyphenation and whitespace."""
    s = re.sub(r'-\n(?=[a-z])', '', s)
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    s = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

_pages = {}
def pages(rid):
    if rid not in _pages:
        t = (ROOT / registry[rid]['source_text']).read_text(encoding='utf-8')
        parts = re.split(r'=== PDF PAGE (\d+) ===', t)
        _pages[rid] = {int(parts[i]): norm(parts[i + 1]) for i in range(1, len(parts), 2)}
    return _pages[rid]

@functools.lru_cache(maxsize=None)  # pure function of the tracked text layer; the gates call it many times per run
def quote_found(rid, page, quote):
    """Exact match after whitespace normalisation; fallback ignores whitespace only (text layers split words)."""
    txt = pages(rid).get(int(page), '')
    q = norm(quote)
    return q in txt or re.sub(r'\s', '', q) in re.sub(r'\s', '', txt)

def check_row(r, fields=FIELDS):
    errs = []
    rid = r['report_id']
    if rid not in registry: return [f'unknown report {rid}']
    if r['field'] not in fields: errs.append(f'unknown field {r["field"]}')
    if r['status'] not in STATUSES: errs.append(f'bad status {r["status"]}')
    if r['source_pdf'] != registry[rid]['source_pdf'] or r['source_sha256'] != registry[rid]['source_sha256']: errs.append('source PDF/hash differs from registry')
    if r['status'] == 'Extracted (PDF quote)':
        if not r['value'].strip() or not r['quote'].strip() or not r['page']: errs.append('extracted value needs value, page and quote')
        elif not quote_found(rid, r['page'], r['quote']): errs.append(f'quote not found on p{r["page"]}: {r["quote"][:80]}')
        if r['quote2'].strip() and not quote_found(rid, r['page2'] or 0, r['quote2']): errs.append(f'quote2 not found on p{r["page2"]}: {r["quote2"][:80]}')
    else:
        if r['value'] or r['quote'] or r['quote2']: errs.append('"Not reported in source" must have no value or quote')
    # Second review: 'pending', or the second reviewer's initials, ISO date and outcome (confirmed = value and status agreed).
    if r['second_review'] != 'pending' and not re.fullmatch(r'[A-Z]{2,4}, \d{4}-\d{2}-\d{2}: confirmed', r['second_review']):
        errs.append(f'bad second_review {r["second_review"]!r}')
    return [f'{rid} / {r["field"]}: {e}' for e in errs]

def main():
    partial = '--partial' in sys.argv
    rows = list(csv.DictReader(open(RECORD, encoding='utf-8')))
    errs = [e for r in rows for e in check_row(r)]
    keys = [(r['report_id'], r['field']) for r in rows]
    errs += [f'duplicate row {k}' for k in {k for k in keys if keys.count(k) > 1}]
    done = {rid for rid, _ in keys}
    for rid in done:
        errs += [f'{rid}: missing field {f}' for f in FIELDS if (rid, f) not in keys]
    if not partial:
        errs += [f'{rid}: report not in record' for rid in registry if rid not in done]
    for rid in sorted(done):
        pdf = ROOT / registry[rid]['source_pdf']
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != registry[rid]['source_sha256']: errs.append(f'{rid}: PDF hash changed')
    if errs:
        print('\n'.join('FAIL ' + e for e in errs)); return 1
    from collections import Counter
    print(f'PASS regimen extraction: {len(done)} reports, {len(rows)} rows,', dict(Counter((r['field'], r['status']) for r in rows)))
    if not partial:
        files = [RECORD, pathlib.Path(__file__)]
        (RECORD.parent / 'regimen_extraction.sha256').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in files))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
