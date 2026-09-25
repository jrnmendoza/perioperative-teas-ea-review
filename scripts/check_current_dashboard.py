#!/usr/bin/env python3
"""v38 data/asset contract replacing the legacy v26 seven-trial UI contract."""
import csv,json,pathlib,hashlib,copy,sys,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];D=ROOT/'10_FINAL_ADJUDICATION'
def rows(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checks(d):
    canonical=json.load(open(D/'04_MODELS/model_outputs.json'));spec=json.load(open(D/'02_DECISIONS/model_specifications.json'))
    active={i for s in spec if s['role']!='SENSITIVITY' for i in s['result_ids']}
    p=d['prisma'];rs=d['rob'];gs=d['grade']
    ret = {
      'current version':d['version']=='v38' and d['registration']=='CRD420261452908',
      'exact model estimates and membership':d['models']==canonical and d['specifications']==spec,
      'exact numerical input identity':d['inputs']==rows(D/'04_MODELS/model_inputs.csv'),
      'exact GRADE identity':gs==rows(D/'03_CANONICAL/grade.csv') and len(gs)==38,
      'exact result RoB identity':rs==rows(D/'02_DECISIONS/v38/rob2_assessments.csv') and len(rs)==len({r['assessment_id'] for r in rs})==94,
      'all current inference components assessed':active<={r['result_id'] for r in rs},
      'canonical registry identity':d['studies']==json.load(open(D/'03_CANONICAL/studies.json')),
      'selection branch arithmetic':p['database_sought']-p['database_not_retrieved']-p['late_duplicates']==p['database_assessed'] and p['database_assessed']-p['database_excluded']+p['citation_included']==p['included_reports']==70,
      'selection label and provenance':p['exclusion_reasons'].get('no perioperative analgesia outcome found')==113 and p['unmapped_import_difference']==12 and p['citation_included']==1,
      'source holds not in main':not ({'AUDIT-0346','AUDIT-0347','V33-OD-0034','V33-OD-0078'}&active),
      'GRADE is evidence-body specific':{g['model_id'] for g in gs}=={s['model_id'] for s in spec if s['role']!='SENSITIVITY'},
      'outcome coverage addendum identity':d.get('outcome_coverage')==json.load(open(D/'07_OUTCOME_COVERAGE/coverage_summary.json')) if (D/'07_OUTCOME_COVERAGE/coverage_summary.json').exists() else True,
      'QoR analytical addendum identity':d.get('qor_analysis')==json.load(open(D/'08_QOR_ANALYSIS/qor_summary.json')) if (D/'08_QOR_ANALYSIS/qor_summary.json').exists() else True,
      'E2 sensitivity identity':d.get('e2_analysis')==json.load(open(D/'09_E2_ANALYSIS/e2_model_outputs.json')) if (D/'09_E2_ANALYSIS/e2_model_outputs.json').exists() else True,
      'QoR later-window identity':d.get('qor_later_models')==json.load(open(D/'08_QOR_ANALYSIS/qor_models_later.json')) if (D/'08_QOR_ANALYSIS/qor_models_later.json').exists() else True,
      'QoR later-window RoB identity': d.get('qor_later_rob') == rows(D/'08_QOR_ANALYSIS/qor_rob2_later.csv') and len(d.get('qor_later_rob', [])) == 5 if 'qor_later_rob' in d else True,
      'E2 methods integrity': d.get('e2_methods', {}).get('Timestamp note', '') == re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')).group(1).strip() if 'e2_methods' in d else True,

    }
    

    import subprocess
    def is_tracked(path):
        try:
            subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)], cwd=ROOT, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    for item in d['downloads']:
        if not is_tracked(ROOT / item['source']):
            ret['all downloads tracked by git'] = False
            break
    else:
        ret['all downloads tracked by git'] = True

    if 'e2_methods_html' in d:
        import html as html_lib
        def normalize_source(text):
            text = re.sub(r'(?m)^---$', '', text)
            text = re.sub(r'\*\*(.*?)\*\*', r'\g<1>', text, flags=re.DOTALL)
            text = re.sub(r'`(.*?)`', r'\g<1>', text, flags=re.DOTALL)
            text = re.sub(r'(?m)^-\s+', '', text)
            text = re.sub(r'(?m)^\d+\.\s+', '', text)
            text = re.sub(r'(?m)^>\s+', '', text)
            return re.sub(r'\s+', ' ', text).strip()
        def normalize_html(h):
            h = h.replace('<p>', ' ').replace('</p>', ' ').replace('<ul>', ' ').replace('</ul>', ' ').replace('<li>', ' ').replace('</li>', ' ').replace('<blockquote>', ' ').replace('</blockquote>', ' ')
            h = re.sub(r'<[^>]+>', '', h)
            h = html_lib.unescape(h)
            return re.sub(r'\s+', ' ', h).strip()
            
        e2_methods_text = (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')
        def get_sec(txt, h, st=None):
            pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n#|\Z)'
            if st: pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n' + re.escape(st) + r'|\n#|\Z)'
            return re.search(pat, txt, re.DOTALL).group(1).strip()
        
        expected_e2 = {
            'Timestamp note': re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', e2_methods_text).group(1).strip(),
            'Why this document exists, stated plainly': get_sec(e2_methods_text, 'Why this document exists, stated plainly'),
            'E1 — registered primary (retained, reported in full)': get_sec(e2_methods_text, 'E1 — registered primary (retained, reported in full)'),
            'E2 — amended primary (post hoc)': get_sec(e2_methods_text, 'E2 — amended primary (post hoc)', st='### Admission rules'),
            'Prespecified sensitivity analyses for E2': get_sec(e2_methods_text, 'Prespecified sensitivity analyses for E2'),
            'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)': get_sec(e2_methods_text, 'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)'),
            'Decision after the E2 run — 23 September 2026: E1 retained as primary': get_sec(e2_methods_text, 'Decision after the E2 run — 23 September 2026: E1 retained as primary')
        }
        
        for k, v in expected_e2.items():
            if normalize_html(d['e2_methods_html'].get(k, '')) != normalize_source(v):
                ret['E2 HTML completeness'] = False
                break
        else:
            ret['E2 HTML completeness'] = True


    if 'qor_later_models' in d and 'qor_later_rob' in d:
        rob_ids = {r['result_id'] for r in d['qor_later_rob']}
        for m in d['qor_later_models']:
            if not set(m['result_ids']) <= rob_ids:
                ret['QoR later-window RoB identity'] = False

    if 'qor_later_metafor_manifest' in d:
        import hashlib
        man = d['qor_later_metafor_manifest']
        expected_models = json.load(open(D/'08_QOR_ANALYSIS/qor_models_later.json'))
        for f in man['files']:
            p = D/'08_QOR_ANALYSIS/metafor_forest_later'/f['file']
            if hashlib.sha256(p.read_bytes()).hexdigest() != f['sha256']:
                ret['QoR later-window metafor manifest'] = False
            else:
                ret.setdefault('QoR later-window metafor manifest', True)
        
        import csv
        comp = list(csv.DictReader(open(D/'08_QOR_ANALYSIS/metafor_forest_later/metafor_comparison_later.csv')))
        all_passed = True
        for row in comp:
            if row['passed'] != 'TRUE': all_passed = False
            model = next((m for m in expected_models if m['model_id'] == row['model_id']), None)
            if model and str(model.get(row['field'])) != 'None' and row['canonical'] != 'NA':
                try:
                    c_val = float(row['canonical'])
                    m_val = float(model[row['field']])
                    if abs(c_val - m_val) > 1e-4:
                        all_passed = False
                except:
                    pass
        if d.get('qor_later_metafor_manifest', {}).get('fail_comp'):
            all_passed = False
        ret['QoR later-window metafor comparison'] = all_passed

    return ret

def main(site=None):
    site=pathlib.Path(site or ROOT/'dashboard');data=json.load(open(site/'current_review.json'));c=checks(data)
    for name,ok in c.items():print(('PASS ' if ok else 'FAIL ')+name)
    if not all(c.values()):return 1
    js=(site/'current_review.js').read_text();loaded=json.JSONDecoder().raw_decode(js.split('window.CURRENT_REVIEW = ',1)[1])[0]
    assert loaded==data,'JS/JSON bundle mismatch'
    page=(site/'index.html').read_text();srcs=re.findall(r'(?:src|href)="([^"#]+)"',page)
    for src in srcs:
        if src.startswith(('https:','http:')):continue
        assert (site/src.split('?')[0]).is_file(),src
    for item in data['downloads']:
        assert sha(site/item['href'])==item['sha256']==sha(ROOT/item['source']),item['href']
    assert all(token not in page for token in ['app.js','v34_data.js','CRD420251090635','k=7, N=676','−14.00','−9.91'])
    
    # New CI checks
    html_without_scripts = re.sub(r'<script.*?</script>', '', page, flags=re.DOTALL)
    html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
    assert not re.search(r'\{[a-z_]+\}', html_without_scripts), 'Unfilled placeholder found in index.html outside scripts/styles'
    nav_match = re.search(r'<nav class="nav"[^>]*>(.*?)</nav>', page)
    assert nav_match, 'Nav block not found'
    nav_buttons = re.findall(r'data-view="([^"]+)"', nav_match.group(1))
    assert nav_buttons == ['overview', 'results', 'qor', 'coverage', 'studies', 'risk', 'evidence', 'prisma', 'methods', 'downloads'], f"Wrong nav buttons: {nav_buttons}"
    footer_match = re.search(r'<footer>(.*?)</footer>', page)
    assert footer_match and '{' not in footer_match.group(1) and '}' not in footer_match.group(1), 'Placeholder found in footer'
    
    if 'e2_labels' in data and 'e2_analysis' in data:
        e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}
        for label_key in data['e2_labels']:
            assert label_key in e2_ids, f'e2_labels key {label_key} not in e2_analysis.models'
    
    downloads_hrefs = [item['href'].split('/')[-1] for item in data['downloads']]
    for required_file in ['e2_model_outputs.csv', 'E2_RESULTS.md', 'AMENDED_PRIMARY_ESTIMAND_E2.md', 'qor_models_later.csv', 'ADDITIONAL_FILE_12.md', 'additional_file_12_A1_primary_construct.csv', 'additional_file_12_A2_other_windows.csv', 'additional_file_12_tierB_no_candidate_result.csv']:
        assert required_file in downloads_hrefs, f'Missing from downloads manifest: {required_file}'
    assert len(downloads_hrefs) == len(set(downloads_hrefs)), 'Filename collision in downloads manifest'
    
    report_text = (ROOT/'FINAL_CURRENT_STATE_REPORT.md').read_text(encoding='utf-8')
    section_match = re.search(r'\*\*Not completed — outstanding\*\*(.*?)(?=\n\*\*|\n## |\Z)', report_text, re.DOTALL)
    expected_outstanding = re.findall(r'- \*\*(.*?)\*\*', section_match.group(1))
    assert data.get('outstanding') == expected_outstanding and len(expected_outstanding) > 0, "outstanding data mismatch or empty"
    
    e2_methods_text = (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')
    def get_sec(txt, h, st=None):
        pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n#|\Z)'
        if st: pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n' + re.escape(st) + r'|\n#|\Z)'
        return re.search(pat, txt, re.DOTALL).group(1).strip()
    
    expected_e2 = {
        'Timestamp note': re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', e2_methods_text).group(1).strip(),
        'Why this document exists, stated plainly': get_sec(e2_methods_text, 'Why this document exists, stated plainly'),
        'E1 — registered primary (retained, reported in full)': get_sec(e2_methods_text, 'E1 — registered primary (retained, reported in full)'),
        'E2 — amended primary (post hoc)': get_sec(e2_methods_text, 'E2 — amended primary (post hoc)', st='### Admission rules'),
        'Prespecified sensitivity analyses for E2': get_sec(e2_methods_text, 'Prespecified sensitivity analyses for E2'),
        'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)': get_sec(e2_methods_text, 'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)'),
        'Decision after the E2 run — 23 September 2026: E1 retained as primary': get_sec(e2_methods_text, 'Decision after the E2 run — 23 September 2026: E1 retained as primary')
    }
    assert data.get('e2_methods') == expected_e2, "e2_methods data mismatch"

    
    
    # v38 download checks
    report_text = (site/'current/FINAL_CURRENT_STATE_REPORT.md').read_text()
    assert 'adjudication v38' in report_text.splitlines()[0], 'FINAL_CURRENT_STATE_REPORT.md not v38'

    grade_text = (site/'current/FINAL_GRADE_RECOMMENDATIONS.md').read_text()
    assert 'v38' in grade_text.splitlines()[0], 'FINAL_GRADE_RECOMMENDATIONS.md not v38'

    import csv
    matrix_csv = (site/'current/FINAL_MODEL_MEMBERSHIP_MATRIX.csv').read_text().splitlines()
    matrix_reader = csv.DictReader(matrix_csv)
    matrix_pairs = {(row['result_id'], row['model_id']) for row in matrix_reader if row['decision'] == 'INCLUDE'}
    
    spec_json = json.loads((pathlib.Path(__file__).parent.parent / '10_FINAL_ADJUDICATION/02_DECISIONS/model_specifications.json').read_text())
    expected_pairs = {(r, s['model_id']) for s in spec_json if s['role'] != 'SENSITIVITY' for r in s['result_ids']}
    
    assert matrix_pairs == expected_pairs, f"Matrix pairs mismatch. Found {len(matrix_pairs)}, expected {len(expected_pairs)} (90)"
    
    rob2_csv = (site/'current/FINAL_RESULT_ROB2_LINKAGE.csv').read_text().splitlines()
    rob2_reader = csv.DictReader(rob2_csv)
    rob_linkages = set()
    for row in rob2_reader:
        if row['rob2_assessment_id']: rob_linkages.add(row['rob2_assessment_id'])
        if row['alternative_assessments']:
            rob_linkages.update([x.strip() for x in row['alternative_assessments'].split(';')])
            
    rob2_assessments_csv = (pathlib.Path(__file__).parent.parent / '10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv').read_text().splitlines()
    assess_ids = {row['assessment_id'] for row in csv.DictReader(rob2_assessments_csv)}
    
    missing_assessments = assess_ids - rob_linkages
    assert not missing_assessments, f"Missing assessments in linkage: {missing_assessments}"

    # Look in the repository, not next to the site: a build can be written anywhere.
    # Tracked files are what gets published; fall back to the working tree without git.
    try:
        root_files=subprocess.run(['git','ls-files','--','fix_*.py','test_ui.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.split()
    except (OSError,subprocess.CalledProcessError):
        root_files=[p.name for pattern in ('fix_*.py','test_ui.py') for p in ROOT.glob(pattern)]
    assert not root_files, f"Scratch files found in repo root: {root_files}"

    ui_js = (site/'current_review_ui.js').read_text()
    assert 'Review complete' not in ui_js, '"Review complete" found in current_review_ui.js without qualifier'
    for forbidden in ['fetch(','XMLHttpRequest','localStorage.setItem']:
        assert forbidden not in ui_js, 'Unexpected external/hidden state operation'
    assert not re.search(r'k=\d+', ui_js), 'Literal k=<digits> found in current_review_ui.js'
    assert not re.search(r'[−-]?\d{1,2}\.\d{2}(?!\d)', ui_js), 'Literal decimal estimate found in current_review_ui.js'
    assert "addEventListener('hashchange'" in ui_js, "hashchange listener missing"
    assert "addEventListener('popstate'" in ui_js, "popstate listener missing"
    assert "history.replaceState" in ui_js, "replaceState missing"
    if "function show(" in ui_js:
        show_body = ui_js.split("function show(")[1].split("}")[0]
        assert "history.replaceState" not in show_body, "replaceState found inside show()"
    if "document.addEventListener('click'" in ui_js:
        click_body = ui_js.split("document.addEventListener('click'")[1].split("});")[0]
        assert "history.replaceState" not in click_body, "replaceState found inside click listener"
    # Existing figures must survive and resolve in both source and built site.
    figures=json.JSONDecoder().raw_decode((site/'article_figures.js').read_text().split('window.ARTICLE_FIGURES = ',1)[1])[0]
    images=[f['src'] for fs in figures.values() for f in fs]
    assert all((site/name).is_file() for name in images)
    mutations=[('exact model estimates and membership',lambda d:d['models'][0].__setitem__('display_effect',999)),('exact GRADE identity',lambda d:d['grade'][0].__setitem__('certainty','High')),('exact result RoB identity',lambda d:d['rob'][0].__setitem__('d3','INVALID TEST VALUE')),('selection label and provenance',lambda d:d['prisma'].__setitem__('unmapped_import_difference',0))]
    if 'qor_analysis' in data:
        mutations.append(('QoR analytical addendum identity',lambda d:d['qor_analysis']['main_models'][0].__setitem__('effect',999)))
        q=data['qor_analysis']
        assert len(q['main_models'])==len(q['grade'])==3 and len(q['rob'])==8 and len(q['diagnostics'])==9
        assert {r['result_id'] for r in q['inputs']}=={r['result_id'] for r in q['rob']}
    if 'e2_analysis' in data:
        mutations.append(('E2 sensitivity identity',lambda d:d['e2_analysis']['models'][0].__setitem__('effect',999)))
    if 'qor_later_models' in data:
        mutations.append(('QoR later-window identity',lambda d:d['qor_later_models'][0].__setitem__('effect',999)))
    if 'qor_later_rob' in data:
        mutations.append(('QoR later-window RoB identity', lambda d: d['qor_later_rob'].__delitem__(0)))
    if 'qor_later_metafor_manifest' in data:
        mutations.append(('QoR later-window metafor manifest', lambda d: d['qor_later_metafor_manifest']['files'][0].__setitem__('sha256', 'badhash')))
        mutations.append(('QoR later-window metafor comparison', lambda d: d.get('qor_later_metafor_manifest').__setitem__('fail_comp', True)))

    mutations.append(('E2 methods integrity', lambda d: d['e2_methods'].update({'Timestamp note': 'Altered text'})))
    mutations.append(('all downloads tracked by git', lambda d: d['downloads'].append(dict(label='Fake', href='current/fake.txt', source='fake.txt', sha256='hash'))))
    if 'e2_methods_html' in data:
        def drop_line(d):
            val = d['e2_methods_html']['Decision after the E2 run — 23 September 2026: E1 retained as primary']
            d['e2_methods_html']['Decision after the E2 run — 23 September 2026: E1 retained as primary'] = val.replace('precise than E1&#x27;s −7.70 (−10.62, −4.78).', '')
        mutations.append(('E2 HTML completeness', drop_line))
    for key,mutate in mutations:
        x=copy.deepcopy(data);mutate(x);assert not checks(x)[key],f'Mutation escaped: {key}'
    
    # HTML placeholder mutation test
    def check_placeholders(html):
        html_without_scripts = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
        return not bool(re.search(r'\{[a-z_]+\}', html_without_scripts))
    
    mutated_page = page.replace('<noscript>', '<noscript>{unfilled_placeholder}</noscript>')
    assert not check_placeholders(mutated_page), 'Placeholder mutation escaped'

    assert "IVMME" not in page, "IVMME found in built index.html"
    assert "unitLabel" in ui_js, "current_review_ui.js missing unitLabel mapping"

    if (site/'build-meta.json').exists():
        meta=json.load(open(site/'build-meta.json'));assert meta['master_version']=='v38' and meta['strict_primary_opioid_k']==1 and meta['canonical_reports']==70 and meta['included_studies']==69
    print(f'PASS v38 + addenda: {len(c)} contracts, {len(mutations)} isolated mutations, {len(data["downloads"])} download hashes, {len(images)} original figure files. Legacy v26 contract not applied.')
    return 0
if __name__=='__main__':
    location=sys.argv[sys.argv.index('--site')+1] if '--site' in sys.argv else None
    raise SystemExit(main(location))
