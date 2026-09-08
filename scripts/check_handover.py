#!/usr/bin/env python3
"""Handover regression checks with isolated one-defect mutation tests."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
from build_reference_data import search_data

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def js(name, variable):
    return json.JSONDecoder().raw_decode((ROOT / f'dashboard/{name}.js').read_text().split(f'window.{variable} = ', 1)[1])[0]


def load():
    sets = {name: rows(f'08_V33_MASTER/01_DATA/{name}.csv') for name in
            ('v33_rescue_opioid_binary_24h', 'v33_intraop_remifentanil', 'v33_intraop_sufentanil', 'v33_qor40_24h', 'v33_gi_first_defecation')}
    return dict(
        hashes=[hashlib.sha256((ROOT / f'TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_{v}_FINAL_LOCK_READY.xlsx').read_bytes()).hexdigest() for v in ('v32','v33')],
        inquiries=js('author_inquiries','AUTHOR_INQUIRIES'),
        searches=js('search_strategies','SEARCH_STRATEGIES'),
        html=(ROOT / 'dashboard/index.html').read_text(),
        app=(ROOT / 'dashboard/app.js').read_text(),
        sets=sets,
        drafts=rows('09_V34_INTAKE/v34_RoB2_Draft.csv'),
        coverage=rows('09_V34_INTAKE/result_rob2_coverage.csv'),
        results=rows('08_V33_MASTER/03_RESULTS/results_v33_secondary.csv'),
        primary=rows('06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv'),
    )


def checks(d):
    html, app = d['html'], d['app']
    expected_coverage = {(name, r['study'], r['comparison_id']) for name, rs in d['sets'].items() for r in rs}
    actual_coverage = {(r['analysis_set'],r['study'],r['comparison_id']) for r in d['coverage']}
    mapping = {'V33_RESCUE_OPIOID_RR_24H':'v33_rescue_opioid_binary_24h',
               'V33_INTRAOP_REMI_MD':'v33_intraop_remifentanil',
               'V33_INTRAOP_REMI_SMD':'v33_intraop_remifentanil',
               'V33_INTRAOP_SUF_MD':'v33_intraop_sufentanil',
               'V33_QOR40_24H_MD':'v33_qor40_24h',
               'V33_GI_DEFECATION_MD':'v33_gi_first_defecation'}
    return {
        'frozen masters': d['hashes'] == ['74fda7d176fae15af4aa5bbff318514f998adcf957a2f9cad67e8de55ab7b12f','64ef683c58a1faa2bf408f415d03d96dd6622abf8ded24a72f43db9c47a82a2a'],
        'outreach source identity': d['inquiries'] == json.loads((ROOT/'dashboard/author_inquiries.json').read_text()),
        'verbatim search and metadata': d['searches'] == search_data(),
        'reference script loads': all(f'src="{n}.js' in html for n in ('author_inquiries','search_strategies','meta_outcomes')),
        'removed orphan KPI targets': all(x not in app for x in ("getElementById('kpi-patient-count')", "getElementById('kpi-i2')", "getElementById('kpi-i2-sub')")),
        'panel sequence': html.find('id="v33-map"') < html.find('id="pathway-flow"') < html.find('id="t33-flow"'),
        'draft isolation': len(d['drafts']) == 18 and all(not r['adjudicated_by'] and not r['adjudicated_on'] and 'NOT ADJUDICATED' in r['assessment_status'] for r in d['drafts']),
        'result coverage': expected_coverage == actual_coverage and len(d['coverage']) == len(expected_coverage) and all(not r['overall'] for r in d['coverage'] if r['assessment_status']=='PENDING'),
        'Wu baseline exclusion': all(r['study'] != 'Wu 2025' for key in ('v33_intraop_remifentanil','v33_intraop_sufentanil') for r in d['sets'][key]),
        'Ng shared arm once': [r['comparison_id'] for r in d['sets']['v33_gi_first_defecation'] if r['study']=='Ng 2013'] == ['NG13_EA_vs_SHAM_BOWEL'],
        'Stata sample counts': all(int(float(r['k'])) == len(d['sets'][mapping[r['analysis_id']]]) for r in d['results']),
        'strict primary preserved': sum(r['inc_primary']=='1' for r in d['primary']) == 7,
    }


def main():
    d = load()
    failures = [name for name, ok in checks(d).items() if not ok]
    if failures:
        print('FAIL:', ', '.join(failures))
        return 1
    if '--mutation-test' in sys.argv:
        def replace_study(x):
            x['sets']['v33_intraop_remifentanil'][0]['study']='Wu 2025'
            next(r for r in x['coverage'] if r['analysis_set']=='v33_intraop_remifentanil')['study']='Wu 2025'
        mutations = {
            'frozen masters': lambda x: x['hashes'].__setitem__(1, 'changed'),
            'outreach source identity': lambda x: x['inquiries'].pop(),
            'verbatim search and metadata': lambda x: x['searches'][0].__setitem__('strategy_text','changed'),
            'reference script loads': lambda x: x.__setitem__('html', x['html'].replace('src="author_inquiries.js','src="missing.js')),
            'removed orphan KPI targets': lambda x: x.__setitem__('app',x['app']+"getElementById('kpi-i2')"),
            'panel sequence': lambda x: x.__setitem__('html',x['html'].replace('id="v33-map"','id="temp"').replace('id="pathway-flow"','id="v33-map"').replace('id="temp"','id="pathway-flow"')),
            'draft isolation': lambda x: x['drafts'][0].__setitem__('adjudicated_by','Invented sign-off'),
            'result coverage': lambda x: x['coverage'][0].__setitem__('overall','Low'),
            'Wu baseline exclusion': replace_study,
            'Ng shared arm once': lambda x: x['sets']['v33_gi_first_defecation'][1].__setitem__('study','Changed trial'),
            'Stata sample counts': lambda x: x['results'][0].__setitem__('k','99'),
            'strict primary preserved': lambda x: x['primary'].append({'inc_primary':'1'}),
        }
        # Keep coverage synchronized in the Ng mutation to isolate its guard.
        original = mutations['Ng shared arm once']
        def mutate_ng(x):
            original(x)
            next(r for r in x['coverage'] if r['comparison_id']=='NG13_EA_vs_SHAM_BOWEL')['study']='Changed trial'
        mutations['Ng shared arm once'] = mutate_ng
        for name, mutate in mutations.items():
            broken = copy.deepcopy(d)
            mutate(broken)
            caught = [n for n, ok in checks(broken).items() if not ok]
            assert caught == [name], (name, caught)
        print(f'PASS: {len(mutations)} isolated mutations caught only by their intended check; originals untouched.')
    print(f'PASS: {len(checks(d))} handover regression checks.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
