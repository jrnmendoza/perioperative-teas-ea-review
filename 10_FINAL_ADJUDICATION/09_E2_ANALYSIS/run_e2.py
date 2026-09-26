"""E2 post-hoc sensitivity analysis (E1 retained as primary; decision 2026-09-23 after this run).
Membership: 02_DECISIONS/v38/E2_tierA_reclassification.csv and E2_tierB1_extraction.csv
(committed in 9fa94d6 before this script was run). Estimator copied verbatim from
code/fit_models.py (REML + safeguarded Hartung-Knapp; k=1 within-study normal CI;
PI only for k>=5); arm combination copied from code/build_results.py combine_arm.
Canonical outputs are not modified; results go to 09_E2_ANALYSIS/ only.
2026-09-26: added the per-contrast export e2_model_inputs.csv for the dashboard. Membership, arm values
and estimator are unchanged; e2_model_outputs.csv/.json are byte-identical to the 2026-09-23 run."""
import csv, json, math, pathlib, copy
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import t, norm
ROOT=pathlib.Path(__file__).resolve().parents[2]; D=ROOT/'10_FINAL_ADJUDICATION'; OUT=D/'09_E2_ANALYSIS'
R={r['result_id']:r for r in csv.DictReader(open(D/'03_CANONICAL/results.csv',encoding='utf-8-sig'))}
def arm(rid,f=1.0):
    r=R[rid]; g=lambda k:float(r[k])
    return dict(trial=r['trial_id'],study=r['study'],rid=rid,factor=f,n_i=g('n_i'),mean_i=g('mean_i')*f,sd_i=g('sd_i')*f,n_c=g('n_c'),mean_c=g('mean_c')*f,sd_c=g('sd_c')*f)
# Tier B1 admissions under E2.1 (values from E2_tierB1_extraction.csv / E2_digitise_gu2019_fig4.json), ug sufentanil
EXTRA={'ZHANG2025':dict(trial='Zhang_2025',study='Zhang 2025',rid='E2.1-ZHANG2025-POD1',n_i=45,mean_i=50.53,sd_i=4.46,n_c=48,mean_c=53.79,sd_c=5.14),
       'GU2019':dict(trial='Gu_2019',study='Gu 2019',rid='E2.1-GU2019-FIG4-T4',n_i=58,mean_i=55.71,sd_i=7.93,n_c=59,mean_c=58.84,sd_c=7.41)}
def extra(key,f):
    x=copy.deepcopy(EXTRA[key]); x['factor']=f
    for a in ('mean_i','sd_i','mean_c','sd_c'): x[a]*=f
    return x
def combine(g):  # verbatim logic of build_results.combine_arm for continuous outcomes
    z=copy.deepcopy(g[0]); assert len(set((r['n_c'],r['mean_c'],r['sd_c']) for r in g))==1,'Control mismatch'
    if len(g)==1: return z
    n=sum(r['n_i'] for r in g); mean=sum(r['n_i']*r['mean_i'] for r in g)/n
    sd=math.sqrt(sum((r['n_i']-1)*r['sd_i']**2+r['n_i']*(r['mean_i']-mean)**2 for r in g)/(n-1))
    z.update(n_i=n,mean_i=mean,sd_i=sd,rid='+'.join(r['rid'] for r in g)); return z
def fit(contrasts):  # verbatim estimator from code/fit_models.py
    k=len(contrasts)
    if k==0: return dict(k=0,N=0,status='NO ELIGIBLE QUANTITATIVE DATA')
    y=np.array([c['mean_i']-c['mean_c'] for c in contrasts]); v=np.array([c['sd_i']**2/c['n_i']+c['sd_c']**2/c['n_c'] for c in contrasts])
    w0=1/v; C=w0.sum()-(w0*w0).sum()/w0.sum()
    if k>1:
        def nll(tau):
            w=1/(v+tau); mu=(w*y).sum()/w.sum(); return .5*(np.log(v+tau).sum()+np.log(w.sum())+(w*(y-mu)**2).sum())
        upper=max(1.,np.var(y)*10,v.max()*10); f=minimize_scalar(nll,bounds=(0,upper),method='bounded',options={'xatol':1e-12})
        tau=max(0,float(f.x)) if nll(f.x)<nll(0) else 0.
        w=1/(v+tau); mu=float((w*y).sum()/w.sum()); q=float((w*(y-mu)**2).sum()/(k-1)); se=math.sqrt(max(1,q)/w.sum()); crit=t.ppf(.975,k-1); i2=100*tau/(tau+(k-1)/C)
        status='REML + safeguarded Hartung-Knapp'
    else:
        tau=0.; mu=float(y[0]); se=math.sqrt(v[0]); crit=norm.ppf(.975); i2=None; q=None; status='SINGLE STUDY - NOT POOLED'
    lo,hi=mu-crit*se,mu+crit*se; pi=(None,None)
    if k>=5: s=math.sqrt(tau+se*se); pi=(mu-t.ppf(.975,k-1)*s, mu+t.ppf(.975,k-1)*s)
    cm=sum(c['n_c']*c['mean_c'] for c in contrasts)/sum(c['n_c'] for c in contrasts)
    return dict(k=k,N=int(sum(c['n_i']+c['n_c'] for c in contrasts)),status=status,effect=mu,ci_low=lo,ci_high=hi,tau2=tau,I2=i2,hk_scale=q,pi_low=pi[0],pi_high=pi[1],
                reaches10mg=mu<=-10,reaches8mg=mu<=-8,relative_reduction_descriptive_percent=-100*mu/cm,
                studies=';'.join(c['study'] for c in contrasts),contrast_ids=';'.join(c['rid'] for c in contrasts))
# ---- membership (from committed reclassification) ----
def teas_sham(f=0.5,drop=()):
    c={'Szmit 2021':arm('V33-OD-0350'),'Chen 1998':arm('V33-OD-0013',5),'Chen 2020':arm('V33-OD-0014',f),'He 2026 (hepatectomy)':arm('V33-OD-0214'),
       'Lee 2011':combine([arm('V33-OD-0184'),arm('V33-OD-0185')]),'Zhang 2025':extra('ZHANG2025',f),'Gu 2019':extra('GU2019',f)}
    return [v for k,v in c.items() if k not in drop]
def ea_usual(drop=()):
    c={'El-Rakshy 2009':arm('V33-OD-0252'),'Seevaunnamtum 2016':arm('V33-OD-0003'),'Yang 2024':arm('V33-OD-0052'),'Lin 2002':combine([arm('V33-OD-0004'),arm('V33-OD-0005')])}
    return [v for k,v in c.items() if k not in drop]
M=[]; INPUTS=[]
def add(mid,body,role,contrasts,note=''):
    r=dict(model_id=mid,body=body,role=role,note=note); r.update(fit(contrasts)); M.append(r)
    for c in contrasts:  # arm values as analysed (after conversion factor and arm combination)
        INPUTS.append(dict(model_id=mid,study=c['study'],trial_id=c['trial'],result_id=c['rid'],factor=c['factor'],n_i=c['n_i'],mean_i=c['mean_i'],sd_i=c['sd_i'],n_c=c['n_c'],mean_c=c['mean_c'],sd_c=c['sd_c'],
                           yi=c['mean_i']-c['mean_c'],vi=c['sd_i']**2/c['n_i']+c['sd_c']**2/c['n_c']))
# ---- validation against canonical v38 (must reproduce exactly) ----
canon={r['model_id']:r for r in csv.DictReader(open(D/'04_MODELS/model_outputs.csv'))}
VAL=[('opioid24_TEAS_sham',[arm('V33-OD-0350')]),
     ('opioid24_TEAS_sham_expanded_suf0.5',[arm('V33-OD-0013',5),arm('V33-OD-0214'),arm('V33-OD-0350'),arm('V33-OD-0014',.5)]),
     ('opioid24_EA_usual',[arm('V33-OD-0252'),arm('V33-OD-0003')]),
     ('opioid24_EA_usual_expanded',[arm('V33-OD-0252'),arm('V33-OD-0003'),arm('V33-OD-0052')])]
val=[]
for mid,cs in VAL:
    f=fit(cs); c=canon[mid]
    d=max(abs(f['effect']-float(c['effect'])),abs(f['ci_low']-float(c['ci_low'])),abs(f['ci_high']-float(c['ci_high'])))
    val.append(dict(model_id=mid,e2_code=round(f['effect'],6),canonical=round(float(c['effect']),6),max_abs_diff=d,pass_=d<1e-6))
assert all(v['pass_'] for v in val), val
# ---- E2 models ----
B='TEAS vs sham'
add('E2_opioid24_TEAS_sham',B,'E2 POST-HOC SENSITIVITY (main)',teas_sham())
add('E2_TEAS_sham_suf0.25',B,'SENSITIVITY',teas_sham(.25),'sufentanil 0.25 mg/ug')
add('E2_TEAS_sham_suf1.0',B,'SENSITIVITY',teas_sham(1.0),'sufentanil 1.0 mg/ug')
add('E2_TEAS_sham_excl_E2.1',B,'SENSITIVITY',teas_sham(drop=('Zhang 2025','Gu 2019')),'without Amendment E2.1 admissions')
add('E2_TEAS_sham_leaveout_Gu2019',B,'SENSITIVITY',teas_sham(drop=('Gu 2019',)),'source contradiction (figure vs text)')
add('E2_TEAS_sham_leaveout_Lee2011',B,'SENSITIVITY',teas_sham(drop=('Lee 2011',)),'source contradiction (Table 8)')
add('E2_TEAS_sham_excl_unquantified_rescue',B,'SENSITIVITY',teas_sham(drop=('Chen 1998','Lee 2011')),'known unquantified rescue removed')
add('E2_TEAS_sham_excl_unstated_route',B,'SENSITIVITY',teas_sham(drop=('He 2026 (hepatectomy)',)),'author equivalents of unstated route removed')
add('E2_TEAS_sham_E1_restriction',B,'SENSITIVITY',[arm('V33-OD-0350')],'restricted to E1-eligible = registered primary')
TS_KEYS=['Szmit 2021','Chen 1998','Chen 2020','He 2026 (hepatectomy)','Lee 2011','Zhang 2025','Gu 2019']  # dict keys, not canonical study labels
for s in TS_KEYS:
    add(f'E2_TEAS_sham_LOO_{s.split()[0]}_{s.split()[1][:4]}',B,'LEAVE-ONE-OUT',teas_sham(drop=(s,)),f'without {s}')
assert all(r['k']==6 for r in M if r['model_id'].startswith('E2_TEAS_sham_LOO_')), 'a leave-one-out did not drop exactly one trial'
add('E2_opioid24_TEAS_usual','TEAS vs usual care','E2 POST-HOC SENSITIVITY (main)',[arm('V33-OD-0351')])
add('E2_opioid24_EA_sham','EA vs sham','E2 POST-HOC SENSITIVITY (main)',[combine([arm('V33-OD-0006'),arm('V33-OD-0007')])],'Lin 2002 only; DP1 boundary; DP4 rescue')
B='EA vs usual care'
add('E2_opioid24_EA_usual',B,'E2 POST-HOC SENSITIVITY (main)',ea_usual())
add('E2_EA_usual_leaveout_ElRakshy',B,'SENSITIVITY',ea_usual(drop=('El-Rakshy 2009',)),'existing El-Rakshy diagnostic')
add('E2_EA_usual_excl_unquantified_rescue',B,'SENSITIVITY',ea_usual(drop=('Yang 2024','Lin 2002')),'known unquantified rescue removed (= E1 body)')
for s in ['El-Rakshy 2009','Seevaunnamtum 2016','Yang 2024','Lin 2002']:
    add(f'E2_EA_usual_LOO_{s.split()[0]}',B,'LEAVE-ONE-OUT',ea_usual(drop=(s,)),f'without {s}')
assert all(r['k']==3 for r in M if r['model_id'].startswith('E2_EA_usual_LOO_')), 'EA LOO did not drop exactly one'
keys=list(dict.fromkeys(k for r in M for k in r))
with open(OUT/'e2_model_outputs.csv','w',newline='') as fh: w=csv.DictWriter(fh,keys); w.writeheader(); w.writerows(M)
json.dump(dict(validation=val,models=M),open(OUT/'e2_model_outputs.json','w'),indent=1,default=str)
with open(OUT/'e2_model_inputs.csv','w',newline='') as fh: w=csv.DictWriter(fh,list(INPUTS[0])); w.writeheader(); w.writerows(INPUTS)
print('VALIDATION (E2 code vs canonical v38):')
for v in val: print(f"  {v['model_id']:38s} {v['e2_code']:>11.6f} vs {v['canonical']:>11.6f}  max|diff| {v['max_abs_diff']:.1e}  {'PASS' if v['pass_'] else 'FAIL'}")
print()
fmt=lambda x:'' if x is None else f'{x:.2f}'
for r in M:
    if r['k']==0: print(f"{r['model_id']:40s} k=0"); continue
    print(f"{r['model_id']:40s} k={r['k']} N={r['N']:>4} MD {r['effect']:7.2f} ({r['ci_low']:7.2f}, {r['ci_high']:7.2f})  I2={fmt(r['I2']):>6s}  PI=({fmt(r['pi_low'])}, {fmt(r['pi_high'])})  10mg={r['reaches10mg']}")
