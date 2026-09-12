#!/usr/bin/env python3
"""Independent locked-primary browser contract, with isolated mutation tests."""
import copy
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=list(csv.DictReader((ROOT/'06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv').open()))
locked={r['study_unit']:r for r in source if r['inc_primary']=='1'}
data=json.JSONDecoder().raw_decode((ROOT/'dashboard/primary_browser.js').read_text().split('window.PRIMARY_BROWSER = ',1)[1])[0]
fields={'arm1_n':'n_i','arm2_n':'n_c','arm1_mean':'mean_i_mme','arm2_mean':'mean_c_mme','arm1_sd':'sd_i_mme','arm2_sd':'sd_c_mme','mean_diff':'md_mme','se':'se_mme','ci_low':'ci_low_mme','ci_upp':'ci_upp_mme'}

def checks(d):
    return {
        'exact locked membership':set(d)==set(locked) and len(d)==7,
        'locked numeric identity':all(k in d and all(d[k].get(f)==float(r[c]) for f,c in fields.items()) for k,r in locked.items()),
        'contrast identity':all(k in d and d[k].get('comparison_id')==r['comparison_id'] for k,r in locked.items()),
        'explicit IV units':all(r.get('unit')=='mg IV MME' for r in d.values()),
    }

assert all(checks(data).values()),checks(data)
key=next(iter(data))
mutations={
    'exact locked membership':lambda d:d.__setitem__('extra trial',copy.deepcopy(d[key])),
    'locked numeric identity':lambda d:d[key].__setitem__('mean_diff',0),
    'contrast identity':lambda d:d[key].__setitem__('comparison_id','wrong contrast'),
    'explicit IV units':lambda d:d[key].__setitem__('unit','oral MME'),
}
for name,mutate in mutations.items():
    changed=copy.deepcopy(data);mutate(changed)
    assert not checks(changed)[name],f'Mutation escaped: {name}'
targets=json.JSONDecoder().raw_decode((ROOT/'dashboard/browser_targets.js').read_text().split('window.BROWSER_TARGETS = ',1)[1])[0]
expected={
    'opioid_48h':{'An 2014','Chen 2020','Zhang 2023'},
    'opioid_72h':{'Yang 2024'},
    # Post-lock admissions 2026-09-12 (eligibility reconciliation pass):
    # Song 2020 and Gao 2022 join pain_rest_24h and ponv_24h; Zhang 2018
    # joins flatus_time from the validated Figure 2a digitisation.
    'pain_rest_24h':{'Liu 2021','Xing 2022','Song 2020','Gao 2022'},
    'ponv_24h':{'Lu 2021','Zheng 2025','Song 2020','Gao 2022'},
    'flatus_time':{'#105119 - Zhou 2025','Lu 2022','Ng 2013','Xing 2022','Yang 2020','Yang 2024','Zhang 2018'},
    'intraop_opioid':{'Guo 2023','Liang 2021','Lu 2021','Pan 2023','Wu 2022','Xing 2022','Zheng 2025'},
    'rescue_analgesia':{'#105119 - Zhou 2025','Tu 2024','Xie 2014','Yu 2020'},
}
def target_checks(d):
    membership=set(d)==set(expected) and all(set(d[k])==v for k,v in expected.items())
    values=True
    for records in d.values():
        for o in records.values():
            raw={r['comparison_id']:r for r in csv.DictReader((ROOT/o['source_dataset']).open())}[o['comparison_id']]
            values &= o['arm1_n']==float(raw['n_i']) and o['arm2_n']==float(raw['n_c'])
            for arm,col in ((1,'i'),(2,'c')):
                if 'arm1_events' in o: values &= o[f'arm{arm}_events']==float(raw[f'events_{col}'])
    return membership,values
assert target_checks(targets)==(True,True)
changed=copy.deepcopy(targets);changed['ponv_24h']['Xiong 2021']=changed['ponv_24h']['Lu 2021']
assert not target_checks(changed)[0], 'Wrong PONV window escaped'
changed=copy.deepcopy(targets);changed['opioid_48h']['An 2014']['arm1_n']=30
assert not target_checks(changed)[1], 'Invented denominator escaped'
print('PASS: 6 locked browser-data checks; 6 isolated mutations rejected.')

# Guard panel ownership as well as populated data. A card outside a tab remains
# visible everywhere and pushes later panels below the fold.
from html.parser import HTMLParser
class PanelParser(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.valid=True
    def handle_starttag(self,tag,attrs):
        if tag!='div': return
        attrs=dict(attrs)
        if 'dashboard-card' in attrs.get('class','').split():
            self.valid &= any(x.startswith('tab-') for x in self.stack)
        self.stack.append(attrs.get('id',''))
    def handle_endtag(self,tag):
        if tag=='div':
            if self.stack: self.stack.pop()
            else: self.valid=False
def valid_panels(html):
    p=PanelParser();p.feed(html);return p.valid and not p.stack
html=(ROOT/'dashboard/index.html').read_text()
assert valid_panels(html)
assert not valid_panels(html.replace('<!-- Section 2D: ROBUSTNESS','</div><!-- Section 2D: ROBUSTNESS'))
szmit=data['Szmit 2021']['rob2']
assert [szmit[f'd{i}'] for i in range(1,6)]+[szmit['overall']]==['Low','Low','Low','Low','Some concerns','Some concerns']
assert szmit['status']=='Assessed' and '0–24' in szmit['timepoint'] and 'row 70' in szmit['assessment_file']
print('PASS: tab ownership guard rejects escaped-card mutation; Szmit primary RoB matches the inspected v33 source row.')

characteristics=json.JSONDecoder().raw_decode((ROOT/'dashboard/study_characteristics.js').read_text().split('window.STUDY_CHARACTERISTICS = ',1)[1])[0]
def valid_characteristics(records):
    return (len(records)==70 and len({r['surgery_category'] for r in records.values()})==11
            and records['Chen 1998']['surgery_category']=='Gynecologic & Breast'
            and records['Chen 2020']['surgery_category']=='Thoracic & Cardiac'
            and records['An 2014']['surgery_category']=='Neurosurgery'
            and records['Liang 2021']['surgery_category']=='Urologic'
            and records['Wu 2016']['surgery_category']=='Not documented')
assert valid_characteristics(characteristics)
for r in characteristics.values():
    source=(ROOT/r['source_file']).read_text()
    assert r['source_excerpt'] in source,r['source_file']
    if r['source_line']:assert source.splitlines()[r['source_line']-1]==r['source_excerpt']
changed=copy.deepcopy(characteristics)
for r in changed.values():r['surgery_category']='Other General Surgery'
assert not valid_characteristics(changed),'Collapsed surgical categories escaped'
print('PASS: 70 surgical records trace to preserved sources; collapsed-category mutation rejected.')
