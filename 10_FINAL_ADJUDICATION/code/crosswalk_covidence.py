"""Report-level crosswalk: Covidence full-text decisions (63 included, 161 excluded exports) -> 70-report registry.

Matching: the normalized first 70 title characters must occur in the first 15,000 characters of a registry
source text. Title-prefix collisions and titles cited in a registry paper's reference list are rejected
explicitly below after manual review. Four included records whose exported titles differ from the PDF text
(encoding/year labels) are mapped manually. Output is provenance evidence, not a PRISMA approval.
"""
import csv, json, pathlib, re, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
inc = json.load(open(ROOT / 'covidence_all_63_included.json')); ex = json.load(open(ROOT / 'covidence_all_161_excluded.json'))
man = json.load(open(D / '01_SOURCE_EVIDENCE/source_manifest.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
src = {x['study']: norm(open(ROOT / x['text_file']).read()[:15000]) for x in man}
MANUAL_INCLUDED = {'Chen 2020': 'Chen 2020', 'Gu 2019': 'Gu 2019', 'Jin 2022': 'Jin 2023'}
# Yeh: two Covidence records both labelled 'Yeh 2010'; map by DOI/title to the two registry reports.
REJECTED = {('Li 2016', 'Guo 2023'): 'Title appears in Guo 2023 reference list; different trial.',
            ('Pei 2025', 'Ng 2013'): 'Shared title prefix; Pei 2025 postdates Ng 2013 and concerns gastrectomy.',
            ('Zhang 2023', 'Song 2020'): 'Shared title prefix (TEAS and postoperative sleep quality); different report.'}
rows = []
for status, recs in [('INCLUDED', inc), ('EXCLUDED', ex)]:
    for r in recs:
        key = norm(r['title'])[:70]
        hits = [s for s, t in src.items() if len(key) >= 30 and key in t]
        rule = 'TITLE FOUND IN SOURCE TEXT' if hits else ''
        if status == 'INCLUDED' and not hits:
            if r['study_id'] in MANUAL_INCLUDED:
                hits = [MANUAL_INCLUDED[r['study_id']]]; rule = 'MANUAL: exported title/year label differs from PDF text'
            elif r['study_id'] == 'Yeh 2010':
                hits = ['Yeh 2010']; rule = 'MANUAL: second Covidence record labelled Yeh 2010; ATHM report'
        rejected = [(h, REJECTED[(r['study_id'], h)]) for h in hits if (r['study_id'], h) in REJECTED]
        hits = [h for h in hits if (r['study_id'], h) not in REJECTED]
        doi = ';'.join(sorted({(z.get('doi') or '').lower() for z in r.get('references', []) if z.get('doi')}))
        rows.append(dict(covidence_id=str(r['id']), covidence_study_id=r['study_id'], covidence_decision=status,
                         exclusion_reason=r.get('exclusion_reason', ''), excluded_on=r.get('excluded_on', ''), doi=doi, title=r['title'],
                         registry_report=';'.join(hits), match_rule=rule if hits else 'NO REGISTRY MATCH',
                         rejected_matches=' | '.join(f'{h}: {why}' for h, why in rejected)))
by_report = collections.defaultdict(list)
for r in rows:
    for h in filter(None, r['registry_report'].split(';')):
        by_report[h].append(r)
assert all(len(v) == 1 or {x['covidence_decision'] for x in v} == {'EXCLUDED'} for v in by_report.values()), 'multiple included records per report'
report_rows = []
for x in man:
    v = by_report.get(x['study'], [])
    dec = {z['covidence_decision'] for z in v}
    if 'INCLUDED' in dec:
        path = 'COVIDENCE FULL-TEXT INCLUDED'
    elif 'EXCLUDED' in dec:
        path = 'COVIDENCE EXCLUDED; IN REGISTRY (post-exclusion re-inclusion not recorded in Covidence export)'
    else:
        path = 'NO COVIDENCE RECORD IN EITHER EXPORT (candidate citation-search addition; unconfirmed)'
    report_rows.append(dict(report_id=x['study'], registry_path=path, covidence_records=' | '.join(f"{z['covidence_id']} {z['covidence_decision']} {z['exclusion_reason']} {z['excluded_on']}".strip() for z in v)))
for name, data in [('covidence_record_crosswalk.csv', rows), ('registry_report_provenance.csv', report_rows)]:
    with open(D / '02_DECISIONS' / name, 'w', newline='') as f:
        w = csv.DictWriter(f, list(data[0])); w.writeheader(); w.writerows(data)
c = collections.Counter(r['registry_path'] for r in report_rows)
print(json.dumps(dict(covidence_included=len(inc), covidence_excluded=len(ex), registry_reports=len(man), paths=c), indent=1))
print('Excluded in Covidence but in registry:', [r['report_id'] for r in report_rows if r['registry_path'].startswith('COVIDENCE EXCLUDED')])
print('Excluded-reason counts:', collections.Counter(r['exclusion_reason'] for r in rows if r['covidence_decision'] == 'EXCLUDED'))
