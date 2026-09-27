"""Harmonised report characteristics for the Study Explorer and the Stata descriptive analyses.

One row per report and field, with a value, a verification status and the source it came from. Sources are
used in a fixed order of provenance and nothing is inferred to fill a gap:

  Verified (registry)                 03_CANONICAL/studies.json value not marked NOT VERIFIED
  Verified (PDF quote)                dashboard/pdf_extracted.js (PDF page + verbatim quote)
  Partly verified (source excerpt)    03_CANONICAL/verified_metadata.json field (source excerpt + hash)
  Canonical result register           03_CANONICAL/results.csv arm descriptions (intervention / comparator)
  Source-traced (extraction record)   dashboard/study_characteristics.js (extraction-record file + line)
  Legacy (v26, not re-verified)       dashboard/data.js (v26 master workbook import)
  Extracted (PDF quote, single extractor)
                                      14_CHARACTERISTICS/regimen_extraction.csv: postoperative analgesia, PCA regimen,
                                      rescue analgesia and cumulative stimulation time, each with a verbatim quote checked
                                      against the report's text layer (code/verify_regimen_extraction.py); one extractor,
                                      second review pending
  Not reported in source              regimen field searched in the full text and not reported there
  Not verified                        registry value explicitly marked NOT VERIFIED and no other source
  Not extracted                       no structured source exists for this field

Outputs: 14_CHARACTERISTICS/report_characteristics.csv (long; the note column carries the verbatim quote for extracted
regimen fields) and report_characteristics_wide.csv (values only, for Stata) plus a hash manifest.
"""
import csv, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'; OUT = D / '14_CHARACTERISTICS'
def js(name, var):
    t = (ROOT / 'dashboard' / name).read_text(); return json.JSONDecoder().raw_decode(t.split(var + ' = ', 1)[1])[0]
LEGACY_KEY = {'#105119 - Zhou 2025': 'Zhou 2025'}
fix = lambda d: {LEGACY_KEY.get(k, k): v for k, v in d.items()}
registry = json.load(open(D / '03_CANONICAL/studies.json'))
pdf = fix(js('pdf_extracted.js', 'window.PDF_EXTRACTED'))
traced = fix(js('study_characteristics.js', 'window.STUDY_CHARACTERISTICS'))
legacy = {LEGACY_KEY.get(s['key'], s['key']): s for s in js('data.js', 'window.STUDIES_DATA')}
overlay = json.load(open(D / '03_CANONICAL/verified_metadata.json'))
results = list(csv.DictReader(open(D / '03_CANONICAL/results.csv', encoding='utf-8-sig')))
REGIMEN = OUT / 'regimen_extraction.csv'
regimen = {(r['report_id'], r['field']): r for r in csv.DictReader(open(REGIMEN, encoding='utf-8'))} if REGIMEN.exists() else {}

def ok(v): return v not in (None, '') and 'NOT VERIFIED' not in str(v)
COMPARATOR_CLASS = lambda s: 'sham' if s.lower().startswith('sham') else 'usual care' if s.lower().startswith('usual') else 'active control' if s.lower().startswith('active') else 'unclear'
out = []
def put(rid, field, value, status, source='', note=''):
    out.append(dict(report_id=rid, field=field, value='' if value is None else str(value).strip(), status=status, source=source, note=note))

for s in registry:
    rid = s['report_id']; lg = legacy.get(rid, {}); pe = pdf.get(rid, {}); tr = traced.get(rid, {}); ov = overlay.get(rid, {}).get('stricta', {})
    reg = 'Verified (registry)'; regsrc = '03_CANONICAL/studies.json'
    put(rid, 'year', s['year'], reg, regsrc)
    put(rid, 'trial_family', s['trial_id'], reg, regsrc)
    put(rid, 'modality', s['modality'], reg, regsrc)
    put(rid, 'comparator', s['comparator'], reg, regsrc)
    put(rid, 'comparator_class', COMPARATOR_CLASS(s['comparator']), reg, regsrc + ' (study-level label; result-level class governs models)')
    put(rid, 'randomized_n', s['randomized_n_report'], 'Verified (registry)', f"{regsrc}; source page {s.get('n_source_page')}")
    put(rid, 'randomized_n_counted', s['randomized_n_counted'], reg, regsrc + ' (operational family count)')
    put(rid, 'analysed_n', s['analyzed_n'], reg, regsrc + ' (report-level text; outcome-specific n differs)')
    # Country and anaesthesia: registry, then PDF quote, then extraction record, then legacy.
    for field, rkey, pkey, tkey, lkey in [('country', 'country', 'country', None, 'country'), ('anaesthesia', 'anesthesia', 'anaesthesia', 'anesthesia', None)]:
        if ok(s.get(rkey)): put(rid, field, s[rkey], reg, regsrc)
        elif isinstance(pe.get(pkey), dict) and pe[pkey].get('value'): put(rid, field, pe[pkey]['value'], 'Verified (PDF quote)', f"{pe.get('source_pdf', '')} p.{pe[pkey].get('page')}")
        elif tkey and tr.get(tkey): put(rid, field, tr[tkey], 'Source-traced (extraction record)', f"{tr.get(tkey + '_source_file')}:{tr.get(tkey + '_source_line')}")
        elif lkey and lg.get(lkey): put(rid, field, lg[lkey], 'Legacy (v26, not re-verified)', 'dashboard/data.js')
        else: put(rid, field, '', 'Not verified' if rkey in s else 'Not extracted')
    put(rid, 'surgical_category', tr.get('surgery_category', ''), 'Source-traced (extraction record)' if tr.get('surgery_category') else 'Not extracted',
        f"{tr.get('source_file')}:{tr.get('source_line')}" if tr else '')
    if ok(s.get('surgery')): put(rid, 'procedure', s['surgery'], reg, regsrc)
    elif tr.get('surgery_procedure'): put(rid, 'procedure', tr['surgery_procedure'], 'Source-traced (extraction record)', f"{tr.get('source_file')}:{tr.get('source_line')}")
    else: put(rid, 'procedure', '', 'Not verified')
    pop = lg.get('population') or {}
    for field, rkey, lkeys in [('age', 'age_i_c', ('arm1_age', 'arm2_age')), ('female', 'sex_i_c', ('arm1_female', 'arm2_female')),
                               ('bmi', 'bmi_i_c', ('arm1_bmi', 'arm2_bmi')), ('asa', 'asa_i_c', ('asa_status',))]:
        if ok(s.get(rkey)): put(rid, field, s[rkey], reg, regsrc)
        elif any(pop.get(k) for k in lkeys): put(rid, field, ' vs '.join(str(pop[k]) for k in lkeys if pop.get(k)), 'Legacy (v26, not re-verified)', 'dashboard/data.js population')
        else: put(rid, field, '', 'Not verified' if rkey in s else 'Not extracted')
    arms = sorted({r['intervention'] for r in results if r['study'] == rid}); ctrls = sorted({r['comparator'] for r in results if r['study'] == rid})
    put(rid, 'intervention_arms', ' | '.join(arms), 'Canonical result register', '03_CANONICAL/results.csv')
    put(rid, 'control_arms', ' | '.join(ctrls), 'Canonical result register', '03_CANONICAL/results.csv')
    st = lg.get('stricta') or {}
    for field, okey, lkeys in [('acupoints', 'acupoints', ('acupoints',)), ('frequency', 'frequency_raw', ('frequency_raw', 'frequency_category')),
                               ('intensity', 'intensity', ('intensity', 'intensity_category')), ('timing', 'timing_raw', ('timing_raw', 'timing_category')),
                               ('sessions', 'sessions', ('sessions_category',)), ('session_duration', 'duration_raw', ('duration_raw', 'duration_category'))]:
        if ov.get(okey) and ov[okey] != 'Unverified': put(rid, field, ov[okey], 'Partly verified (source excerpt)', f"03_CANONICAL/verified_metadata.json ({ov.get('verification_date')})")
        elif any(st.get(k) for k in lkeys): put(rid, field, next(st[k] for k in lkeys if st.get(k)), 'Legacy (v26, not re-verified)', 'dashboard/data.js stricta')
        else: put(rid, field, '', 'Not extracted')
    for field in ('postoperative_analgesia', 'pca_regimen', 'rescue_analgesia', 'cumulative_duration'):
        x = regimen.get((rid, field))
        if not x:
            put(rid, field, '', 'Not extracted')
        elif x['status'] == 'Extracted (PDF quote)':
            pages = f"p.{x['page']}" + (f", p.{x['page2']}" if x['quote2'] else '')
            quote = f"p.{x['page']}: “{x['quote']}”" + (f" p.{x['page2']}: “{x['quote2']}”" if x['quote2'] else '')
            put(rid, field, x['value'], 'Extracted (PDF quote, single extractor)', f"{x['source_pdf']} {pages} (regimen_extraction.csv)",
                quote + (f" Note: {x['note']}" if x['note'] else ''))
        else:
            put(rid, field, '', 'Not reported in source', f"{x['source_pdf']} (full text checked; regimen_extraction.csv)", x['note'])

OUT.mkdir(exist_ok=True)
with open(OUT / 'report_characteristics.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, list(out[0])); w.writeheader(); w.writerows(out)
fields = list(dict.fromkeys(r['field'] for r in out)); wide = {}
for r in out: wide.setdefault(r['report_id'], {'report_id': r['report_id']})[r['field']] = r['value']
with open(OUT / 'report_characteristics_wide.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, ['report_id'] + fields); w.writeheader(); w.writerows(wide.values())
srcs = ['10_FINAL_ADJUDICATION/03_CANONICAL/studies.json', '10_FINAL_ADJUDICATION/03_CANONICAL/verified_metadata.json', '10_FINAL_ADJUDICATION/03_CANONICAL/results.csv',
        '10_FINAL_ADJUDICATION/14_CHARACTERISTICS/regimen_extraction.csv',
        'dashboard/pdf_extracted.js', 'dashboard/study_characteristics.js', 'dashboard/data.js', 'dashboard/../10_FINAL_ADJUDICATION/code/build_characteristics.py',
        '10_FINAL_ADJUDICATION/14_CHARACTERISTICS/report_characteristics.csv', '10_FINAL_ADJUDICATION/14_CHARACTERISTICS/report_characteristics_wide.csv']
with open(OUT / 'characteristics.sha256', 'w') as fh:
    for p in srcs:
        q = (ROOT / p).resolve(); fh.write(f"{hashlib.sha256(q.read_bytes()).hexdigest()}  {q.relative_to(ROOT)}\n")
from collections import Counter
print(len(wide), 'reports,', len(out), 'field rows;', dict(Counter(r['status'] for r in out)))
