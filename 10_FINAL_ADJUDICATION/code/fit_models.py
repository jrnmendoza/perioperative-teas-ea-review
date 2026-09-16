"""Independent scipy restricted-likelihood fit; safeguarded Hartung-Knapp."""
import csv,json,pathlib,math,collections,sys
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import t,norm
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION'
rows=list(csv.DictReader(open(D/'04_MODELS/model_inputs.csv')));spec=json.load(open(D/'02_DECISIONS/model_specifications.json'));groups=collections.defaultdict(list)
for r in rows:groups[r['model_id']].append(r)
out=[]
for s in spec:
 g=groups[s['model_id']];k=len(g);r={z:s[z] for z in ['model_id','construct','modality','comparator','role','measure','unit']};r.update(k=k,N=sum(int(float(x['n_i']))+int(float(x['n_c'])) for x in g),studies=';'.join(x['study'] for x in g),status='NO ELIGIBLE QUANTITATIVE DATA' if not k else ('SINGLE STUDY — NOT POOLED' if k==1 else 'REML + safeguarded Hartung–Knapp'))
 if not k:out.append(r);continue
 y=np.array([float(x['yi']) for x in g]);v=np.array([float(x['vi']) for x in g]);w0=1/v;C=w0.sum()-(w0*w0).sum()/w0.sum()
 if k>1:
  def nll(tau):
   w=1/(v+tau);mu=(w*y).sum()/w.sum();return .5*(np.log(v+tau).sum()+np.log(w.sum())+(w*(y-mu)**2).sum())
  upper=max(1.,np.var(y)*10,v.max()*10);fit=minimize_scalar(nll,bounds=(0,upper),method='bounded',options={'xatol':1e-12});tau=max(0,float(fit.x)) if nll(fit.x)<nll(0) else 0.
  w=1/(v+tau);mu=float((w*y).sum()/w.sum());q=float((w*(y-mu)**2).sum()/(k-1));se=math.sqrt(max(1,q)/w.sum());crit=t.ppf(.975,k-1);p=2*t.sf(abs(mu/se),k-1);i2=100*tau/(tau+(k-1)/C);Q=float((w0*(y-(w0*y).sum()/w0.sum())**2).sum())
 else:tau=0.;mu=float(y[0]);se=math.sqrt(v[0]);crit=norm.ppf(.975);p=2*norm.sf(abs(mu/se));i2=None;Q=None;q=None
 lo=mu-crit*se;hi=mu+crit*se;pi_lo=pi_hi=None
 # Sparse PIs are not shown; same declared rule in independent implementation.
 if k>=5:pi_lo=mu-t.ppf(.975,k-1)*math.sqrt(tau+se*se);pi_hi=mu+t.ppf(.975,k-1)*math.sqrt(tau+se*se)
 r.update(effect=mu,se=se,ci_low=lo,ci_high=hi,p=p,tau2=tau,I2=i2,Q=Q,hk_scale=q,pi_low=pi_lo,pi_high=pi_hi)
 if s['measure']=='RR':r.update(display_effect=math.exp(mu),display_ci_low=math.exp(lo),display_ci_high=math.exp(hi))
 else:r.update(display_effect=mu,display_ci_low=lo,display_ci_high=hi)
 r['pain_margin_result']='EXCLUDES CLINICALLY IMPORTANT WORSENING' if s['construct'].startswith(('pain_rest_approximately','pain_movement_approximately')) and hi<1 else ('DOES NOT EXCLUDE CLINICALLY IMPORTANT WORSENING' if s['construct'].startswith(('pain_rest_approximately','pain_movement_approximately')) else 'NOT APPLICABLE')
 if s['construct']=='systemic_opioid_0_24h':
  cm=sum(float(x['n_c'])*float(x['mean_c']) for x in g)/sum(float(x['n_c']) for x in g);r.update(reaches10mg=mu<=-10,reaches8mg=mu<=-8,relative_reduction_descriptive_percent=-100*mu/cm,relative_reference='Participant-weighted comparator mean; descriptive only; not pooled ratio of means')
 out.append(r)
keys=list(dict.fromkeys(k for r in out for k in r))
with open(D/'04_MODELS/model_outputs.csv','w',newline='') as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(out)
(D/'04_MODELS/model_outputs.json').write_text(json.dumps(out,indent=2,allow_nan=False))
print('Fitted',len(out),'defined estimands;',sum(r['k']>1 for r in out),'pooled models')
for r in out:
 if r['role']!='SENSITIVITY':print(r['model_id'],r['k'],r['N'],round(r.get('display_effect',0),4),round(r.get('display_ci_low',0),4),round(r.get('display_ci_high',0),4))
