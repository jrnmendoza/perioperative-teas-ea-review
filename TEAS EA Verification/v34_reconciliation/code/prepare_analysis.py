#!/usr/bin/env python3
"""Prepare native results and explicitly selected independent Stata datasets.
No implied pooling across different endpoint definitions or time windows.
"""
import json,csv,math,re,hashlib
from pathlib import Path
from collections import defaultdict,Counter
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent.parent
s=json.load(open(BASE/'data/reconciliation_stage.json'));D=s['outcomes'];U=s['updates']
def readcsv(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def writecsv(p,rows,headers=None):
    headers=headers or list(rows[0]) if rows else headers or ['record_id']
    with open(p,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction='ignore');w.writeheader();w.writerows(rows)
def matrix(rows,headers=None):
    headers=headers or list(rows[0]);return [headers]+[[r.get(h) for h in headers] for r in rows]
def n(x):
    try:return float(x)
    except (ValueError,TypeError):return None
def effect(r,scale=1):
    ni,nc=r['Analyzed n intervention'],r['Analyzed n comparator']
    if not ni or not nc:return {}
    if r['Data type']=='Mean/SD':
        mi,si,mc,sc=[r[h] for h in ['Mean intervention','SD intervention','Mean comparator','SD comparator']]
        if None in (mi,si,mc,sc) or min(ni,nc)<2:return {}
        md=(mi-mc)*scale;se=math.sqrt(si*si/ni+sc*sc/nc)*scale
        sp=math.sqrt(((ni-1)*si*si+(nc-1)*sc*sc)/(ni+nc-2));g=(mi-mc)/sp*(1-3/(4*(ni+nc)-9)) if sp else None
        return {'measure':'MD','effect':round(md,6),'se':round(se,6) if se>0 else None,'hedges_g':round(g,6) if g is not None else None,'hedges_se':round(math.sqrt((ni+nc)/(ni*nc)+g*g/(2*(ni+nc))),6) if g is not None else None,'effect_note':'Native MD; no pooled interpretation without compatible model.','scale_factor':scale}
    if r['Data type']=='Events/total':
        ei,ec=r['Events intervention'],r['Events comparator']
        if None in (ei,ec):return {}
        if ei==ec==0:return {'measure':'logRR','effect':None,'se':None,'effect_note':'Double-zero: retained as safety evidence; no logRR estimated.','scale_factor':1}
        cc=.5 if 0 in (ei,ec,ni-ei,nc-ec) else 0
        # Add .5 to all four cells when correction is required => N increases by 1.
        ei+=cc;ec+=cc;ni+=2*cc;nc+=2*cc
        return {'measure':'logRR','effect':round(math.log((ei/ni)/(ec/nc)),6),'se':round(math.sqrt(1/ei-1/ni+1/ec-1/nc),6),'effect_note':'0.5 added to all four cells' if cc else 'Uncorrected log risk ratio','scale_factor':1}
    return {}

byid={r['Comparison ID']:r for r in D}
native=[]
for r in D:
    b={'record_id':r['V34 record ID'],'comparison_id':r['Comparison ID'],'study':r['Canonical study'],'endpoint_family':r['V34 endpoint class'],'outcome':r['Outcome/result'],'window':r['Timepoint/window'],'time_class':r['V34 time class'],'statistic_type':r['Data type'],'modality':r['V34 modality'],'comparator_type':r['V34 comparator class'],'intervention':r['Intervention arm'],'comparator':r['Comparator arm'],'unit':r['Unit/scale'],'n_i':r['Analyzed n intervention'],'n_c':r['Analyzed n comparator'],'mean_i':r['Mean intervention'],'sd_i':r['SD intervention'],'mean_c':r['Mean comparator'],'sd_c':r['SD comparator'],'events_i':r['Events intervention'],'events_c':r['Events comparator'],'eligibility':r['V34 eligibility'],'reason':r['V34 eligibility reason'],'rob2':r['V34 RoB2 status'],'analysis_population':r.get('Analysis population'),'source':r['Source PDF URL'],'source_location':r['Source location'],'selected_model':None,'effect':None,'se':None,'measure':None,'effect_note':None,'scale_factor':1,'hedges_g':None,'hedges_se':None}
    if r['V34 eligibility']=='INCLUDE':b.update(effect(r))
    native.append(b)
nb={r['comparison_id']:r for r in native}

# Exact, established primary factor metadata; numerical values rebuilt from Outcome_Data.
baseline=readcsv(ROOT/'07_TIERED_V33/01_DATA/tiered_primary_v33.csv')
pmeta={r['comparison_id']:r for r in baseline if r['in_S0']=='1'}
primary=[]
for p in s['primary']:
    r=byid[p['comparison_id']];m=pmeta[p['comparison_id']];factor=float(m['mme_factor']);e=effect(r,factor)
    z=dict(nb[p['comparison_id']]);z.update(e);z.update({'dataset':'primary_24h_mme','unit':'mg IV morphine equivalents','modality':m['modality'],'comparator_type':m['comparator'].replace('Care','care'),'conversion_provenance':'Preserved prespecified v33 factor; 06_FINAL_ANALYSIS_V26/06_AUDIT/opioid_conversion_audit.csv','mme_factor':factor})
    for k,h in [('mean_i','Mean intervention'),('sd_i','SD intervention'),('mean_c','Mean comparator'),('sd_c','SD comparator')]:z[k]=r[h]*factor
    assert abs(z['effect']-float(m['md_mme']))<1e-6 and abs(z['se']-float(m['se_mme']))<1e-6,(p['study_unit'],z,m)
    primary.append(z)
assert len(primary)==7
writecsv(BASE/'data/v34_primary_24h_mme.csv',primary)
U['V34_Primary_MME']=matrix(primary)

# Continue the five existing secondary datasets with corrected definitions.
# Old study selections are used as protocol metadata only; all values reread from v34.
model_ids={}
oldsets={}
for name in ['intraop_remifentanil','intraop_sufentanil','qor40_24h','gi_first_defecation','rescue_opioid_binary_24h']:
    oldsets[name]=readcsv(ROOT/f'08_V33_MASTER/01_DATA/v33_{name}.csv')
    ids=[z['comparison_id'] for z in oldsets[name]]
    if name=='qor40_24h':ids=[i for i in ids if 'day 1' not in byid[i]['Timepoint/window'].lower()]+['V34_B1_119']
    if name=='rescue_opioid_binary_24h':ids=[i for i in ids if byid[i]['Canonical study']=='Yu 2020']
    if name.startswith('intraop_'):
        drug=name.split('_',1)[1]
        ids += [r['Comparison ID'] for r in D if r.get('V34 audit row') and r['Canonical study']=='Liang 2021' and drug in r['Outcome/result'].lower()]
    model_ids[name]=ids

selected=[];man=[];jobs=[]
def addjobs(name,rows,phase):
    groups=defaultdict(list)
    for z in rows:
        # Wang risk strata are separate cohorts within one trial. Do not count
        # them as two independent RCTs in a shared model.
        stratum=(' / SNVP stratum' if 'SNVP' in z['comparison_id'] else ' / MNVP stratum') if z['study']=='Wang 2024' else ''
        groups[z['modality']+' / '+z['comparator_type']+stratum].append(z)
    for group,rs in groups.items():
        assert len(rs)==len({r['study'] for r in rs}), (name,group,'non-independent studies')
        slug=re.sub('[^a-zA-Z0-9]+','_',name+'_'+group).strip('_')
        fname=f'{phase}_{slug}.csv';writecsv(BASE/'data'/fname,rs)
        if phase=='v34':man.append({'dataset':fname,'analysis':name,'study_count':len(rs),'effect_type':rs[0]['measure'],'comparator':rs[0]['comparator_type'],'modality':rs[0]['modality'],'exclusions':'Only explicit selected independent contrasts; see not-pooled register','unresolved_holds':'New result-specific RoB pending; source-specific holds excluded','pooling_status':'REML'+(' + Hartung-Knapp' if len(rs)>=3 else ' (normal CI; k=2)') if len(rs)>=2 else 'k=1: no pooled estimate','study_names':'; '.join(r['study'] for r in rs)})
        if len(rs)>=2:jobs.append({'id':slug,'phase':phase,'file':fname,'measure':rs[0]['measure'],'k':len(rs)})

for name,ids in model_ids.items():
    rows=[]
    for rid in ids:
        r=byid[rid];assert r['V34 eligibility']=='INCLUDE',(name,rid,r['V34 eligibility'])
        z=dict(nb[rid]);sc=1000 if name.startswith('intraop_') and str(r['Unit/scale']).lower().startswith('mg') else 1
        z.update(effect(r,sc));z['selected_model']=name
        if name.startswith('intraop_'):
            assert all(t not in str(r['Unit/scale']) for t in ['/kg','/min']),rid
            z['unit']='ug '+name.split('_',1)[1]
            for k in ['mean_i','sd_i','mean_c','sd_c']:z[k]*=sc
        assert z['se'] and z['se']>0
        rows.append(z);selected.append(z);nb[rid]['selected_model']=name
    writecsv(BASE/f'data/v34_{name}.csv',rows)
    addjobs(name,rows,'v34')
    # Re-run the original v33 analysis inputs within the same modality/comparator
    # strata for a fair before/after comparison; historical mixed-window rescue
    # and POD1 QoR results are not presented as exact-window comparisons.
    before=[]
    for old in oldsets[name]:
        rid=old['comparison_id']
        if name=='rescue_opioid_binary_24h' and rid not in ids:continue
        if name=='qor40_24h' and rid not in ids:continue
        z=dict(nb[rid]);z['effect']=float(old['md'] if 'md' in old else old['lnrr']);z['se']=float(old['se'] if 'se' in old else old['se_lnrr']);z['selected_model']=name
        before.append(z)
    addjobs(name,before,'v33_matched')

# Primary full model is a historical cross-stratum audit; protocol strata are also run.
addjobs('primary_24h_mme',primary,'v34')
oldprim=[]
for z in primary:
    m=pmeta[z['comparison_id']];q=dict(z);q['effect']=float(m['md_mme']);q['se']=float(m['se_mme']);oldprim.append(q)
addjobs('primary_24h_mme',oldprim,'v33_matched')
for phase,rows in [('v34',primary),('v33_matched',oldprim)]:
    fname=f'{phase}_primary_24h_mme_ALL_AUDIT.csv';writecsv(BASE/'data'/fname,rows);jobs.append({'id':'primary_24h_mme_ALL_AUDIT','phase':phase,'file':fname,'measure':'MD','k':len(rows)})

# Every requested family receives a native data-preparation file, including holds.
# These are evidence maps, not automatically poolable datasets.
def familyfile(z):
    f=z['endpoint_family'].lower()
    if 'intraoperative opioid' in f:return 'intraoperative_opioid'
    if 'time to first rescue' in f:return 'time_to_first_rescue'
    if 'rescue opioid frequency' in f:return 'rescue_opioid_frequency'
    if 'rescue opioid use' in f:return 'rescue_opioid_use'
    if 'opioid dose' in f:return 'postoperative_opioid_other_windows'
    if 'qor-15' in f:return 'qor15'
    if 'qor-40' in f:return 'qor40'
    if f.startswith('pain') or f=='chronic pain':return 'pain'
    if f.startswith('ponv'):return 'ponv'
    if f.startswith('nausea'):return 'nausea'
    if f.startswith('vomiting'):return 'vomiting'
    if f=='rescue antiemetic':return 'rescue_antiemetic'
    if f.startswith('gi'):return 'gi_recovery'
    if f=='los':return 'los'
    if any(t in f for t in ['adverse','neurocognitive','cognitive','cardiac','bladder','urinary']):return 'adverse_events_and_cognition'
    if any(t in f for t in ['pca','pcia','analgesia']):return 'analgesic_proxies_and_nonopioid_rescue'
    return 'functional_recovery_and_other'
fg=defaultdict(list)
for z in native:fg[familyfile(z)].append(z)
for f,rows in fg.items():
    writecsv(BASE/f'data/v34_native_{f}.csv',rows,list(native[0]))
    man.append({'dataset':f'v34_native_{f}.csv','analysis':f,'study_count':len({r['study'] for r in rows}),'effect_type':'Native MD / logRR where valid; medians/graph/NR held','comparator':'Separated in comparator_type; no automatic pooling','modality':'Separated in modality; no automatic pooling','exclusions':'See eligibility and model status on every row','unresolved_holds':str(sum(r['eligibility']!='INCLUDE' for r in rows))+' non-include rows','pooling_status':'PREPARED EVIDENCE MAP: exact definition/window/arm selection required','study_names':'; '.join(sorted({r['study'] for r in rows}))})

notpooled=[]
for z in native:
    if z['selected_model'] or z['comparison_id'] in pmeta:continue
    reason=z['reason']
    if z['eligibility']=='INCLUDE':
        reason='Native numeric candidate, not newly pooled: exact outcome definition/time/scale or prespecified arm selection requires a model-specific decision. No automatic pooling of the gap-fill audit.'
        if z['study']=='Sun 2017':reason='Three shared-control timing contrasts; no established v33 selection for this new endpoint. Retain all, select/adjust arms before pooling.'
        if z['study']=='Tu 2024' and 'tramadol' in z['outcome'].lower():reason='Corrected source window 6–24 h; removed from cumulative 0–24 h rescue model.'
        if z['study']=='Liu 2026 (burn)' and 'dezocine' in z['outcome'].lower():reason='Through POD1 is not confirmed exact cumulative 0–24 h; separate POD1 result, not pooled with exact window.'
        if z['study']=='Yu 2020' and 'QoR-40' in z['outcome']:reason='POD1/POD2 preserved separately from exact 24-h QoR-40.'
    notpooled.append(dict(z,not_pooled_reason=reason))
writecsv(BASE/'data/v34_not_pooled_register.csv',notpooled,list(native[0])+['not_pooled_reason'])
writecsv(BASE/'data/v34_secondary_native_all.csv',native,list(native[0]))
writecsv(BASE/'data/v34_secondary_selected.csv',selected)
U['V34_Secondary_Ready']=matrix(selected)
U['V34_Not_Pooled']=matrix(notpooled,list(native[0])+['not_pooled_reason'])
U['V34_Stata_Manifest']=matrix(man)
# Retain legacy manifest column names while regenerating its current entries.
mh=U.get('Stata_Manifest',[])
oldmh=['analysis_id','analysis_group','endpoint_stratum','provisional_status','strict_k_lock_items','sensitivity_k_lock_items','effect_data_rule','pooling_rule','mandatory_sensitivity_or_hold','notes']
U['Stata_Manifest']=matrix([dict(zip(oldmh,[m['dataset'],m['analysis'],m['modality']+' / '+m['comparator'],m['pooling_status'],m['study_count'],None,m['effect_type'],'One independent study/compatible stratum',m['unresolved_holds'],m['exclusions']])) for m in man],oldmh)
writecsv(BASE/'data/v34_stata_manifest.csv',man)

# Stata is the authoritative inferential engine. Matched before/after runs share
# the same estimator and stratum. No publication or dashboard updates performed.
lines=['clear all','set more off','capture log close',f'log using "{BASE}/results/v34_analysis.log", replace',
 'tempname OUT',f'postfile `OUT\' str100 analysis_id str20 phase str10 measure double(k estimate ci_low ci_high p_value tau2 i2) str25 model using "{BASE}/results/v34_model_results.dta", replace']
for job in jobs:
    kh=' se(kh)' if job['k']>=3 else ''
    lines += [f'import delimited "{BASE}/data/{job["file"]}", clear varnames(1) encoding("utf-8")', 'assert !missing(effect,se) & se>0',
              'meta set effect se, studylabel(study)',f'meta summarize, random(reml){kh}',
              f'post `OUT\' ("{job["id"]}") ("{job["phase"]}") ("{job["measure"]}") (r(N)) (r(theta)) (r(ci_lb)) (r(ci_ub)) (r(p)) (r(tau2)) (r(I2)) ("REML'+(' + Hartung-Knapp' if job['k']>=3 else ' normal CI')+'")']
lines += ['postclose `OUT\'',f'use "{BASE}/results/v34_model_results.dta", clear',f'export delimited "{BASE}/results/v34_model_results.csv", replace','display "V34_ANALYSIS_SUCCESS"','log close']
(BASE/'code/run_stata.do').write_text('\n'.join(lines)+'\n')
s.update(updates=U,analysis_jobs=jobs,analysis_manifest=man,selected_secondary=selected,native_analysis=native,primary_mme=primary)
(BASE/'data/analysis_stage.pending.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
(BASE/'data/analysis_stage.pending.json').replace(BASE/'data/analysis_stage.json')
print(json.dumps({'selected_models':{k:len(v) for k,v in model_ids.items()},'native_families':{k:len(v) for k,v in fg.items()},'stata_jobs':len(jobs)},indent=2))
