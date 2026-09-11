#!/usr/bin/env python3
"""Generate browser reference data from preserved search and outreach sources."""
import json
import csv
import re
import math
import openpyxl
from build_study_characteristics import build as surgical_characteristics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def browser_targets(studies):
    """Mirror established Stata target selections, preserving estimand boundaries."""
    def canonical(name):
        return re.sub(r'^#\d+\s*-\s*', '', name).strip()
    names={canonical(s['key']):s['key'] for s in studies}
    specs=[('opioid_48h','A_48h'),('opioid_72h','B_72h'),('pain_rest_24h','C_pain24h'),
           ('ponv_24h','D_ponv'),('flatus_time','E_flatus'),('intraop_opioid','F_exploratory'),('rescue_analgesia','F_exploratory')]
    targets={}
    for key,file in specs:
        result={}
        path=ROOT/f'06_FINAL_ANALYSIS_V26/01_DATA/target_{file}.csv'
        for r in csv.DictReader(path.open()):
            if key=='intraop_opioid':
                if r['target']!='F-intra' or r['unit'] not in ('µg remifentanil','mg remifentanil') or not r['mean_i']: continue
            elif r['include_strict']!='1': continue
            if key=='ponv_24h' and r['endpoint_stratum']!='D_PONV_0-24h': continue
            if key=='rescue_analgesia' and (r['target']!='F-rescue-opioid' or r['unit']!='participants' or not r['events_i']): continue
            name=names[canonical(r['study'])]
            if name in result: raise ValueError(f'Duplicate browser contrast: {key}/{name}')
            o={'arm1_n':float(r['n_i']),'arm2_n':float(r['n_c']), 'unit':r['unit'],
               'comparison_id':r['comparison_id'],'source_dataset':str(path.relative_to(ROOT)),
               'source_note':r['source_qc'], 'result_rob':r['result_rob']}
            if key in ('ponv_24h','rescue_analgesia'):
                a,c=float(r['events_i']),float(r['events_c'])
                o.update(arm1_events=a,arm2_events=c)
                rr=(a/o['arm1_n'])/(c/o['arm2_n'])
                se=math.sqrt(1/a-1/o['arm1_n']+1/c-1/o['arm2_n'])
                o.update(rr=rr,se=se,ci_low=math.exp(math.log(rr)-1.96*se),ci_upp=math.exp(math.log(rr)+1.96*se))
            else:
                suffix='_mme' if key=='opioid_48h' else '_hours' if key=='flatus_time' else ''
                factor=1000 if key=='intraop_opioid' and r['unit']=='mg remifentanil' else 1
                for arm,letter in ((1,'i'),(2,'c')):
                    for stat in ('mean','sd'): o[f'arm{arm}_{stat}']=float(r[f'{stat}_{letter}{suffix}'])*factor
                mdcol='md'+suffix; secol='se'+suffix
                md=float(r[mdcol]) if r.get(mdcol) else o['arm1_mean']-o['arm2_mean']
                se=float(r[secol]) if r.get(secol) else math.sqrt(o['arm1_sd']**2/o['arm1_n']+o['arm2_sd']**2/o['arm2_n'])
                o.update(mean_diff=md,se=se,ci_low=md-1.96*se,ci_upp=md+1.96*se)
                if key in ('opioid_48h','opioid_72h'): o['unit']='mg IV MME'
                if key=='intraop_opioid': o['unit']='µg remifentanil'
                # The *_hours columns are already converted, so the row's own
                # unit label ('days' for Ng 2013) describes the raw statistic,
                # not the value emitted here. Label what we actually emit.
                if key=='flatus_time':
                    if r['unit']!='hours':
                        o['converted_from']=f"{r['mean_i']} ± {r['sd_i']} vs {r['mean_c']} ± {r['sd_c']} {r['unit']} (×24)"
                    o['unit']='hours'
            result[name]=o
        targets[key]=result
    assert {k:len(v) for k,v in targets.items()}==dict(opioid_48h=3,opioid_72h=1,pain_rest_24h=2,ponv_24h=2,flatus_time=6,intraop_opioid=7,rescue_analgesia=4)
    return targets


def search_data():
    base = ROOT / '01_search_strategy'
    specs = [
        ('pubmed', 'PubMed', 'NCBI PubMed', '2026-07-21',
         'pubmed/pubmed_v0_2_multiline.txt', 'pubmed/pubmed_v0_2_explanation.md',
         r'Combined unique PubMed records: ([\d,]+)',
         'Cochrane sensitivity-maximizing RCT component; animal-only exclusion.',
         'v0.2 export; not labelled a formal search'),
        ('cochrane', 'CENTRAL', 'Cochrane Library Search Manager', '2026-07-21',
         'cochrane/2026-07-21/CENTRAL_search_strategy_2026-07-21.txt',
         'cochrane/2026-07-21/CENTRAL_search_log_2026-07-21.md',
         r'Exported: all ([\d,]+) CENTRAL',
         'CENTRAL Trials only; no additional trial, language, date or outcome filter.',
         'Strategy entered 2026-07-21; CENTRAL export completed 2026-07-22'),
        ('embase', 'Embase', 'Embase.com (Elsevier)', '2026-07-22',
         'embase/2026-07-22/EMBASE_search_strategy_2026-07-22.txt',
         'embase/2026-07-22/EMBASE_search_log_2026-07-22.md',
         r'Final result count: ([\d,]+)',
         'Randomized-trial component; see verbatim strategy for all exclusions.',
         'Revised executed search'),
        ('cinahl', 'CINAHL Ultimate', 'EBSCOhost', '2026-07-23',
         'cinahl/2026-07-23/CINAHL_search_strategy_2026-07-23.txt',
         'cinahl/2026-07-23/CINAHL_search_log_2026-07-23.md',
         r'F3 platform count: ([\d,]+)',
         'RCT component and animal-only exclusion; no interface limiters.',
         'CINAHL Ultimate substituted for Complete with user authorization'),
    ]
    result = []
    for ident, name, platform, date, strategy, log, pattern, filters, status in specs:
        count = re.search(pattern, (base / log).read_text())
        if not count:
            raise ValueError(f'Missing source count: {log}')
        result.append(dict(id=ident, name=name, database=name, platform=platform,
                           date=date, hits=int(count[1].replace(',', '')),
                           filters=filters, status=status,
                           source=str((base / strategy).relative_to(ROOT)),
                           count_source=str((base / log).relative_to(ROOT)),
                           strategy_text=(base / strategy).read_bytes().decode('utf-8')))
    return result


def main():
    data = (ROOT / 'dashboard/data.js').read_text().split('window.STUDIES_DATA = ', 1)[1]
    studies = json.JSONDecoder().raw_decode(data)[0]
    workbook=ROOT/'TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx'
    wb=openpyxl.load_workbook(workbook,read_only=True,data_only=True)
    iterator=wb['Corrected_RoB2'].iter_rows(values_only=True)
    headers=next(iterator)
    corrected={}
    for rownum,values in enumerate(iterator,2):
        r=dict(zip(headers,values));r['rownum']=rownum;corrected[r['Canonical study']]=r
    wb.close()
    available = sorted({key for study in studies for key, value in study.get('outcomes', {}).items()
                        if isinstance(value, dict) and any(isinstance(value.get(k), (int, float))
                                                          for k in ('mean_diff', 'rr'))})
    payloads = {
        'study_characteristics': ('STUDY_CHARACTERISTICS', surgical_characteristics()),
        'browser_targets': ('BROWSER_TARGETS', browser_targets(studies)),
        'author_inquiries': ('AUTHOR_INQUIRIES', json.loads((ROOT / 'dashboard/author_inquiries.json').read_text())),
        'search_strategies': ('SEARCH_STRATEGIES', search_data()),
        'meta_outcomes': ('META_OUTCOMES', available),
        'primary_browser': ('PRIMARY_BROWSER', {
            r['study_unit']: {
                **{target: float(r[source]) for target, source in {
                    'arm1_n':'n_i','arm2_n':'n_c','arm1_mean':'mean_i_mme',
                    'arm1_sd':'sd_i_mme','arm2_mean':'mean_c_mme','arm2_sd':'sd_c_mme',
                    'mean_diff':'md_mme','se':'se_mme','ci_low':'ci_low_mme','ci_upp':'ci_upp_mme'}.items()},
                'unit':'mg IV MME', 'comparison_id':r['comparison_id']
            } for r in csv.DictReader((ROOT / '06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv').open())
            if r['inc_primary']=='1'
        }),
    }
    for study in studies:
        name=study['key']
        if name not in payloads['primary_browser'][1] or study.get('rob2_outcomes',{}).get('opioid_24h',{}).get('status')=='Assessed': continue
        r=corrected[name]
        if '24' not in str(r['Timepoint/window']): raise ValueError(f'Primary RoB time window mismatch: {name}')
        payloads['primary_browser'][1][name]['rob2']={
            'status':'Assessed', 'outcome_name':r['Selected result'],'timepoint':r['Timepoint/window'],
            **{f'd{i}':r[f'Domain {i}'] for i in range(1,6)},'overall':r['Overall RoB 2'],
            'rationale':r['Correction source'],
            'assessment_file':f"v33 Corrected_RoB2, row {r['rownum']}; {r['Comparison']}"
        }
    for filename, (variable, payload) in payloads.items():
        (ROOT / f'dashboard/{filename}.js').write_text(
            '// Generated by scripts/build_reference_data.py; do not edit.\n'
            f'window.{variable} = ' + json.dumps(payload, ensure_ascii=False, indent=2) + ';\n')
        print(f'{filename}: {len(payload)} records')


if __name__ == '__main__':
    main()
