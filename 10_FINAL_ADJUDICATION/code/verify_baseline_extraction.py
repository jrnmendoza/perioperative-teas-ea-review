"""Check the baseline and protocol extraction record (14_CHARACTERISTICS/baseline_protocol_extraction.csv).

The record replaces the v26 legacy values of eleven characteristic fields (age, female, BMI, ASA status, anaesthesia,
acupoints, frequency, intensity, timing, sessions, session duration) with values taken from the source PDFs. The rules
are those of the regimen record (verify_regimen_extraction.py, whose row check this reuses): every extracted value
carries a verbatim quote (optionally a second one) found on the stated page of the report's text layer; a field the
report does not state is "Not reported in source" with no value and no quote; the source PDF and hash match the registry;
second_review is 'pending' or '<initials>, <YYYY-MM-DD>: confirmed'.

Coverage: every report has a row for every field, except a field whose value is already verified in the registry
(03_CANONICAL/studies.json) or, for anaesthesia, by an earlier PDF quote (dashboard/pdf_extracted.js); those keep
their verified value. Exits non-zero on any failure and writes a hash manifest when the record passes.

Usage: python3 10_FINAL_ADJUDICATION/code/verify_baseline_extraction.py
"""
import csv, hashlib, json, pathlib, re, sys
from collections import Counter
import verify_regimen_extraction as V

ROOT = V.ROOT; D = V.D
RECORD = D / '14_CHARACTERISTICS/baseline_protocol_extraction.csv'
FIELDS = ('age', 'female', 'bmi', 'asa', 'anaesthesia', 'acupoints', 'frequency', 'intensity', 'timing', 'sessions', 'session_duration')
REGISTRY_KEY = {'age': 'age_i_c', 'female': 'sex_i_c', 'bmi': 'bmi_i_c', 'asa': 'asa_i_c', 'anaesthesia': 'anesthesia'}
ok = lambda v: v not in (None, '') and 'NOT VERIFIED' not in str(v)

def already_verified():
    """(report, field) pairs whose value is verified elsewhere and so needs no row here."""
    t = (ROOT / 'dashboard/pdf_extracted.js').read_text()
    pdf = json.JSONDecoder().raw_decode(t.split('window.PDF_EXTRACTED = ', 1)[1])[0]
    pdf = {{'#105119 - Zhou 2025': 'Zhou 2025'}.get(k, k): v for k, v in pdf.items()}
    out = set()
    for rid, s in V.registry.items():
        out |= {(rid, f) for f, k in REGISTRY_KEY.items() if ok(s.get(k))}
        a = pdf.get(rid, {}).get('anaesthesia')
        if isinstance(a, dict) and a.get('value'): out.add((rid, 'anaesthesia'))
    return out

def main():
    rows = list(csv.DictReader(open(RECORD, encoding='utf-8')))
    errs = []
    if rows and list(rows[0]) != V.COLS: errs.append(f'columns differ from {V.COLS}')
    errs += [e for r in rows for e in V.check_row(r, FIELDS)]
    keys = [(r['report_id'], r['field']) for r in rows]
    errs += [f'duplicate row {k}' for k in {k for k in keys if keys.count(k) > 1}]
    have = set(keys); verified = already_verified()
    errs += [f'{rid}: no row and no verified value for {f}' for rid in V.registry for f in FIELDS if (rid, f) not in have | verified]
    # Provenance wording: one extractor, dated; a second review is recorded only in second_review.
    errs += [f'{r["report_id"]} / {r["field"]}: bad extracted_by {r["extracted_by"]!r}' for r in rows
             if not re.fullmatch(r'Single extractor, \d{4}-\d{2}-\d{2}', r['extracted_by'])]
    for rid in sorted({r for r, _ in keys}):
        if hashlib.sha256((ROOT / V.registry[rid]['source_pdf']).read_bytes()).hexdigest() != V.registry[rid]['source_sha256']:
            errs.append(f'{rid}: PDF hash changed')
    if errs:
        print('\n'.join('FAIL ' + e for e in errs)); return 1
    print(f'PASS baseline/protocol extraction: {len({r for r, _ in keys})} reports, {len(rows)} rows;',
          dict(Counter(r['status'] for r in rows)), f'second review: {dict(Counter(r["second_review"] for r in rows))}')
    files = [RECORD, pathlib.Path(__file__)]
    (RECORD.parent / 'baseline_protocol_extraction.sha256').write_text(
        ''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in files))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
