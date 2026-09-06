import json
from pathlib import Path
root=Path(__file__).resolve().parent
ids=['S021','S022','S023','S024','S025','S027','S028','S029','S030']
required=['Study_ID','Study','reviewer_model','reasoning_effort','phase_a_saved_before_baseline','study','outcomes','rob2','opioid_candidate','duplicate_map','author_contact','summary']
allowed={'VERIFIED','VERIFIED WITH QUALIFICATION','CORRECTED','MATERIAL ERROR','DUPLICATE/OVERLAP HOLD','GRAPH DIGITIZATION NEEDED','AUTHOR DATA NEEDED','NOT ANALYSIS ELIGIBLE','UNRESOLVABLE FROM PUBLICATION'}
report={'studies':[],'errors':[],'review_flags':[]}
for sid in ids:
    p=json.loads((root/'phase_a'/f'{sid}.json').read_text())
    b=json.loads((root/'baseline'/f'{sid}.json').read_text())
    f=json.loads((root/'adjudicated'/f'{sid}.json').read_text())
    l=json.loads((root/'ledger'/f'{sid}.json').read_text())
    def err(s): report['errors'].append(sid+': '+s)
    for k in required:
        if k not in f: err('missing top-level '+k)
    bs={r['_baseline_row']:r for r in b['Outcome_Data']}
    os={r['baseline_row']:r for r in f['outcomes']}
    if len(os)!=len(f['outcomes']) or set(bs)!=set(os): err('row coverage mismatch')
    for n,r in os.items():
        if r['verification_status'] not in allowed: err(str(n)+' invalid status')
        orig=bs[n]; final=r['final']
        if set(final)!=(set(orig)-{'_baseline_row'}):err(str(n)+' field schema mismatch')
        checks={c['field']:c for c in r['field_checks']}
        if set(checks)!=set(final):err(str(n)+' incomplete field checks')
        changes={c['field']:c for c in r['changes']}
        for k,v in final.items():
            if checks.get(k,{}).get('source_value')!=v: err(str(n)+' field-check value mismatch '+k)
            if v!=orig[k] and k not in changes:err(str(n)+' undocumented change '+k)
            if k in changes and (changes[k]['old_value']!=orig[k] or changes[k]['final_value']!=v):err(str(n)+' inaccurate change '+k)
        for arm in ['intervention','comparator']:
            e=final['Events '+arm];nn=final['Analyzed n '+arm]
            if e is not None and nn is not None and not(0<=e<=nn):err(str(n)+' events outside n')
    ris=[]
    for r in f['rob2']:
        ris.append(r['result_id'])
        qs=r['signaling_questions']
        if len(qs)!=22 or len(set(q['question'].split()[0] for q in qs))!=22:err(r['result_id']+' signaling question coverage')
        for q in qs:
            if q['answer'] not in {'Y','PY','PN','N','NI','NA'}:err(r['result_id']+' invalid signaling answer')
            for k in ['evidence','source_location','reasoning']:
                if not q.get(k):err(r['result_id']+' empty '+k)
        if len(r['domains'])!=5:err(r['result_id']+' domain count')
        if any(d['judgment']=='High' for d in r['domains']) and r['overall']!='High':err(r['result_id']+' high domain overall mismatch')
        if qs[1]['answer'] in {'N','PN'} and r['domains'][0]['judgment']!='High':report['review_flags'].append(sid+': '+r['result_id']+' D1 nonconcealment algorithm')
    if len(ris)!=len(set(ris)):err('duplicate result ids')
    if l.get('stage')!='ADJUDICATED':err('ledger not adjudicated')
    if p.get('baseline_accessed') is not False or not f['phase_a_saved_before_baseline']:err('phase declaration')
    report['studies'].append({'Study_ID':sid,'rows':len(os),'rob2_results':len(ris),'changed_fields':sum(len(o['changes']) for o in os.values()),'stage':l['stage'],'phase_a_before_adjudicated_mtime':(root/'phase_a'/f'{sid}.json').stat().st_mtime < (root/'adjudicated'/f'{sid}.json').stat().st_mtime})
report['total_rows']=sum(s['rows'] for s in report['studies'])
report['total_rob2_results']=sum(s['rob2_results'] for s in report['studies'])
print(json.dumps(report,indent=2))

