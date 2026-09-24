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
    return {
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
    }
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
    for required_file in ['e2_model_outputs.csv', 'E2_RESULTS.md', 'AMENDED_PRIMARY_ESTIMAND_E2.md', 'qor_models_later.csv']:
        assert required_file in downloads_hrefs, f'Missing from downloads manifest: {required_file}'
    
    ui_js = (site/'current_review_ui.js').read_text()
    for forbidden in ['fetch(','XMLHttpRequest','localStorage.setItem']:
        assert forbidden not in ui_js, 'Unexpected external/hidden state operation'
    assert not re.search(r'k=\d+', ui_js), 'Literal k=<digits> found in current_review_ui.js'
    assert not re.search(r'-\d{1,2}\.\d{2}(?!\d)', ui_js), 'Literal decimal estimate found in current_review_ui.js'
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
    for key,mutate in mutations:
        x=copy.deepcopy(data);mutate(x);assert not checks(x)[key],f'Mutation escaped: {key}'
    
    # HTML placeholder mutation test
    def check_placeholders(html):
        html_without_scripts = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
        return not bool(re.search(r'\{[a-z_]+\}', html_without_scripts))
    
    mutated_page = page.replace('<noscript>', '<noscript>{unfilled_placeholder}</noscript>')
    assert not check_placeholders(mutated_page), 'Placeholder mutation escaped'

    if (site/'build-meta.json').exists():
        meta=json.load(open(site/'build-meta.json'));assert meta['master_version']=='v38' and meta['strict_primary_opioid_k']==1 and meta['canonical_reports']==70 and meta['included_studies']==69
    print(f'PASS v38 + addenda: {len(c)} contracts, {len(mutations)} isolated mutations, {len(data["downloads"])} download hashes, {len(images)} original figure files. Legacy v26 contract not applied.')
    return 0
if __name__=='__main__':
    location=sys.argv[sys.argv.index('--site')+1] if '--site' in sys.argv else None
    raise SystemExit(main(location))
