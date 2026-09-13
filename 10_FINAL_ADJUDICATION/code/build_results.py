"""Explicit v35 adjudications. No result-label equality determines model admission.
Immutable v34 extraction + versioned decisions -> canonical rows -> model inputs.
"""
import csv,json,pathlib,re,math,collections,copy
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION'
def readcsv(p):return list(csv.DictReader(open(ROOT/p,encoding='utf-8-sig')))
def writecsv(p,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with open(ROOT/p,'w',newline='') as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def num(v):
 try:return float(v)
 except:return None
raw=readcsv('TEAS EA Verification/v34_reconciliation/data/v34_outcome_data.csv');studies={r['report_id']:r for r in readcsv('FINAL_TRIAL_REPORT_MAPPING.csv')}
rows={}
for r in raw:
 id=r['V34 record ID']; assert id and id not in rows
 s=r['Canonical study'];st=studies[s]
 x=dict(result_id=id,study=s,trial_id=st['trial_id'],comparison_id=r['Comparison ID'],intervention=r['Intervention arm'],comparator=r['Comparator arm'],modality=st['modality'],comparator_class=r['V34 comparator class'],family=r['Outcome family'],outcome=r['Outcome/result'],window=r['Timepoint/window'],population=r['Analysis population'] or 'Outcome-specific analyzed population',n_i=num(r['Analyzed n intervention']),n_c=num(r['Analyzed n comparator']),mean_i=num(r['Mean intervention']),sd_i=num(r['SD intervention']),mean_c=num(r['Mean comparator']),sd_c=num(r['SD comparator']),events_i=num(r['Events intervention']),events_c=num(r['Events comparator']),unit=r['Unit/scale'],data_type=r['Data type'],source_location=r['Source location'],source_quote=r['V34 source quote'],source_pdf=st['source_pdf'],source_sha256=st['source_sha256'],source_qc=r['Source-QC issue'],legacy_eligibility=r['V34 eligibility'],decision='EXCLUDE',rationale='Outside defined quantitative estimands; retained in full descriptive extraction.',models='',factor=1)
 if any(w in r['Data type'].lower() for w in ['median','graph','not reported']):x.update(decision='HOLD',rationale='No directly tabulated mean/SD or event/denominator for current quantitative body; preserve original statistic, no automatic median or graph conversion.')
 if any(w in r['V34 eligibility'].lower() for w in ['hold','ambiguous','not analysis']):x.update(decision='HOLD',rationale='Source ambiguity or unavailable required statistic: '+r['V34 eligibility reason'])
 if s.startswith('Yeh'):x.update(decision='HOLD',rationale='Probable overlapping family; conflicting epidural/IV route for opioids. No independent duplicated cohort admitted.')
 if s in ['Jin 2023','Long 2025']:x.update(decision='HOLD',rationale='General anaesthesia unverified from available main report.' if s=='Jin 2023' else 'Physical modality unresolved: needle OR patch in source.')
 rows[id]=x

def ids(ns):return [f'V33-OD-{n:04}' for n in ns]
def aids(ns):return [f'AUDIT-{n:04}' for n in ns]
spec=[]
def add(name,chosen,construct,mod,comp,role='ADDITIONAL',measure='MD',unit='',factor=1,note='Source construct/window/contrast reviewed; direct data admitted.',combine=True):
 assert mod in ['TEAS','EA']
 for id in chosen:assert id in rows,id
 spec.append(dict(model_id=name,result_ids=chosen,construct=construct,modality=mod,comparator=comp,role=role,measure=measure,unit=unit,note=note,combine=combine,factor=factor))
# Principal/supportive strict systemic24 estimands. Empty principal EA is explicit.
add('opioid24_TEAS_sham',ids([350]),'systemic_opioid_0_24h','TEAS','sham','PRINCIPAL',unit='mg IVMME')
add('opioid24_EA_sham',[],'systemic_opioid_0_24h','EA','sham','PRINCIPAL',unit='mg IVMME')
add('opioid24_TEAS_usual',ids([351]),'systemic_opioid_0_24h','TEAS','usual_care','SUPPORTIVE',unit='mg IVMME')
add('opioid24_EA_usual',ids([252,3]),'systemic_opioid_0_24h','EA','usual_care','SUPPORTIVE',unit='mg IVMME',note='El-Rakshy outcome Table2 retained with High RoB/source caveat; Seeva includes rescue.')
add('opioid24_EA_usual_without_ElRakshy',ids([3]),'systemic_opioid_0_24h','EA','usual_care','SENSITIVITY',unit='mg IVMME')
for suf in [.25,.5,1.]:
 for chen in [True,False]:
  add(f'opioid24_TEAS_sham_expanded_suf{suf:g}'+('' if chen else '_without_Chen2020'),ids([13,214,350]+([14] if chen else [])),'device_or_equivalence_uncertain_opioid_0_24h','TEAS','sham','SENSITIVITY',unit='assumed mg IVMME',factor={'V33-OD-0013':5,'V33-OD-0014':suf},note='Expanded device/rescue/unit-uncertain body. Published source values unchanged. Not the registered systemic estimand.')
add('opioid24_EA_usual_expanded',ids([252,3,52]),'device_or_systemic_opioid_0_24h','EA','usual_care','SENSITIVITY',unit='mg IVMME')
add('opioid_partial_EA_sham',ids([6,7]),'PCA_partial_1_to_24h','EA','sham','SENSITIVITY',unit='mg IV morphine')
add('opioid_partial_EA_usual',ids([4,5]),'PCA_partial_1_to_24h','EA','usual_care','SENSITIVITY',unit='mg IV morphine')
add('opioid_partial_TEAS_sham',ids([184,185]),'PCA_partial_1_to_24h','TEAS','sham','SENSITIVITY',unit='mg IV morphine',note='Lee Table8 excludes recovery-room doses; combine low/high arms; sham interval sum differs fromTable8.')
add('opioid24_EA_sham_weight_normalized',ids([107,108]),'PCA_morphine_0_24h_weight_normalized','EA','sham','SENSITIVITY',unit='mg/kg IV morphine')
add('opioid24_EA_sham_fentanyl_per_kg',ids([16]),'fentanyl_0_24h_weight_normalized','EA','sham','SENSITIVITY',unit='µg/kg fentanyl')
# Explicit secondary membership; compatible active arms combined, shared control counted once.
add('ponv24_TEAS_sham',ids([27,33,130,131,168,195,215,257,261,276])+aids([359]),'composite_PONV_0_24h','TEAS','sham',measure='RR',unit='risk ratio',note='0–24h or POD1 cumulative adverse-event reporting; Jiang PP population explicit. Lu two active protocols combined.')
add('ponv24_TEAS_sham_point_window_sensitivity',ids([27,33,130,131,168,195,215,257,261,276])+aids([359,127,369]),'PONV_24h_including_point_window_uncertain','TEAS','sham','SENSITIVITY','RR','risk ratio',note='Adds Lu2022 and Liang2021 24h assessments; cumulative window not presumed in main body.')
add('nausea24_EA_usual',ids([])+aids([77])+['V34-OD-0759'],'nausea_0_24h','EA','usual_care',measure='RR',unit='risk ratio')
add('vomiting24_EA_usual',ids([55])+aids([78]),'vomiting_0_24h','EA','usual_care',measure='RR',unit='risk ratio')
add('nausea24_TEAS_sham',ids([371,293])+aids([292,293]),'nausea_0_24h','TEAS','sham',measure='RR',unit='risk ratio')
add('vomiting24_TEAS_sham',ids([372,296,277])+aids([294,295,100]),'vomiting_0_24h','TEAS','sham',measure='RR',unit='risk ratio')
add('persistent_nausea24_TEAS_sham',ids([278]),'persistent_nausea_over5min_0_24h','TEAS','sham',measure='RR',unit='risk ratio')
add('nausea48_TEAS_sham',ids([139]),'nausea_0_48h','TEAS','sham',measure='RR',unit='risk ratio')
add('vomiting48_TEAS_sham',ids([140]),'vomiting_0_48h','TEAS','sham',measure='RR',unit='risk ratio')
add('ponv48_TEAS_usual',ids([56]),'composite_PONV_0_48h','TEAS','usual_care',measure='RR',unit='risk ratio')
# Zhu disjoint6–24h counts are not cumulative0–24h.
add('nausea6to24_EA_usual',ids([19,21,23]),'nausea_6_24h','EA','usual_care',measure='RR',unit='risk ratio')
add('vomiting6to24_EA_usual',ids([20,22,24]),'vomiting_6_24h','EA','usual_care',measure='RR',unit='risk ratio')
add('pain24_rest_TEAS_sham',ids([163,367,64]),'pain_rest_approximately24h','TEAS','sham',unit='0–10 points')
add('pain24_movement_TEAS_sham',ids([164]),'pain_movement_approximately24h','TEAS','sham',unit='0–10 points')
add('pain24_rest_TEAS_usual',[],'pain_rest_approximately24h','TEAS','usual_care',unit='0–10 points',note='Xing NTG vs NG isolates TEAS added to balanced TAP block.')
add('pain24_movement_EA_sham',ids([201,202]),'pain_movement_approximately24h','EA','sham',unit='0–10 points',factor=.1)
add('pain24_rest_EA_sham',[],'pain_rest_approximately24h','EA','sham',unit='0–10 points')
add('pain24_movement_EA_sham_with_He',ids([201,202,218]),'pain_movement_approximately24h','EA','sham','SENSITIVITY',unit='0–10 points',factor={'V33-OD-0201':.1,'V33-OD-0202':.1},note='He2026 reported SDs conflict with threshold counts; retain literal SD only as diagnostic.')
add('pain24_rest_EA_sham_He_reported_SD',ids([219]),'pain_rest_approximately24h','EA','sham','SENSITIVITY',unit='0–10 points',note='He2026 extremely small repeated SDs cannot be reconciled with threshold counts; no fabricated replacement.')
add('pain24_unclassified_TEAS_sham',ids([15,71,75,142,158,221])+aids([342]),'pain_setting_unspecified_24h','TEAS','sham','SENSITIVITY',unit='0–10 points',note='Rest/movement not established. Never use this mixed-setting body to assert registered pain co-outcome criterion.')
# Lee needs both frequencies: only one24h pain arm extracted, so do not select favorable low arm as principal.
add('pain24_Lee_low_arm_only',ids([187]),'pain_setting_unspecified_24h','TEAS','sham','SENSITIVITY',unit='0–10 points',note='Available low-frequency arm only; not admitted as a complete multiarm evidence body.')
add('pain24_Ng_unspecified',ids([118]),'pain_setting_unspecified_POD1','EA','sham','SENSITIVITY',unit='0–10 points')
add('pain6to24_movement_EA_usual',aids([2,3,4]),'pain_movement_interval6_24h','EA','usual_care','SENSITIVITY',unit='0–10 points',note='Interval summary cannot be assumed a point24h co-outcome.')
add('flatus_TEAS_sham',ids([28,82,134,223,239,62])+aids([251,252,253,347]),'time_first_flatus','TEAS','sham',unit='hours')
add('flatus_TEAS_usual',[],'time_first_flatus','TEAS','usual_care',unit='hours')
add('flatus_EA_sham',ids([117]),'time_first_flatus','EA','sham',unit='hours',factor=24)
add('flatus_EA_usual',ids([2,53,198])+aids([17,18,19]),'time_first_flatus','EA','usual_care',unit='hours')
add('bowelsounds_TEAS_sham',ids([222])+aids([173,346]),'time_first_bowel_sounds','TEAS','sham',unit='hours')
add('defecation_TEAS_sham',ids([135,224,240])+aids([254,255,256]),'time_first_defecation','TEAS','sham',unit='hours')
add('defecation_EA_sham',ids([115]),'time_first_defecation','EA','sham',unit='hours')
add('defecation_EA_usual',ids([54,116,199,380]),'time_first_defecation','EA','usual_care',unit='hours')
# Additional48/72-hour data preserve source clock/construct. No automatic median conversion.
add('opioid48_EA_usual_PCA',ids([254]),'PCA_fentanyl_0_48h','EA','usual_care','ADDITIONAL',unit='mg IVMME',factor=100)
add('opioid72_EA_usual_PCA',[], 'PCA_morphine_0_72h','EA','usual_care','ADDITIONAL',unit='mg IV morphine')
# Bring explicit absent v34 rows from historical source-normalized data, not a blind union.
for file,compid,newid in [('target_A_48h.csv','CHEN20_TEAS_vs_SHAM_SUF48','V35-CHEN20-48'),('target_B_72h.csv','YANG24_EA_vs_UC_MORPH72','V35-YANG24-72')]:
 r=next(r for r in readcsv('06_FINAL_ANALYSIS_V26/01_DATA/'+file) if r['comparison_id']==compid)
 template=copy.deepcopy(rows['V33-OD-0014' if 'CHEN' in newid else 'V33-OD-0052']);template.update(result_id=newid,comparison_id=compid,outcome=r['outcome'],window=r['time_window'],source_location=r['source_qc'],source_quote=r['Sourceverifiedresult'],mean_i=num(r['mean_i']),sd_i=num(r['sd_i']),mean_c=num(r['mean_c']),sd_c=num(r['sd_c']),models='',decision='SENSITIVITY',rationale='Explicit historical source-normalized additional endpoint; source construct caveat retained.')
 rows[newid]=template
# He48 author supplement, explicit fresh source value.
x=copy.deepcopy(rows['V33-OD-0214']);x.update(result_id='V35-HE26-48',window='0–48 h',mean_i=39.5,sd_i=4,mean_c=40.4,sd_c=7.1,source_location='Supplemental Table1 sm8842; mITT80/79',models='');rows[x['result_id']]=x
spec=[s for s in spec if s['model_id']!='opioid72_EA_usual_PCA']
add('opioid72_EA_usual_PCA',['V35-YANG24-72'],'PCA_morphine_0_72h','EA','usual_care','SENSITIVITY',unit='mg IV morphine',note='Yang unquantified IM rescue not included in device total.')
add('opioid72_EA_sham_PCA',ids([250]),'PCA_morphine_0_72h','EA','sham','ADDITIONAL',unit='mg IV morphine',note='Published three-day PCA mean/SD; separate from strict systemic24h outcome.')
for suf in [.25,.5,1.]:
 add(f'opioid48_TEAS_sham_uncertain_suf{suf:g}',['V35-CHEN20-48','V35-HE26-48'],'PCA_or_author_equivalent_0_48h','TEAS','sham','SENSITIVITY',unit='assumed mg IVMME',factor={'V35-CHEN20-48':suf},note='Chen unresolved basal contradiction and He unknown equivalence basis; no principal claim.')
# Native remifentanil additional body; mg->µg only; modalities never mixed.
add('intraop_remifentanil_TEAS_sham',ids([34,72,78,128,129,232,379,61])+aids([364]),'intraop_remifentanil','TEAS','sham','ADDITIONAL',unit='µg remifentanil',factor={'V33-OD-0128':1000,'V33-OD-0129':1000,'V33-OD-0232':1000})
add('intraop_remifentanil_TEAS_usual',[],'intraop_remifentanil','TEAS','usual_care','ADDITIONAL',unit='µg remifentanil')
add('intraop_remifentanil_EA_usual',ids([376,377,378]),'intraop_remifentanil','EA','usual_care','ADDITIONAL',unit='µg remifentanil',factor={'V33-OD-0376':1000,'V33-OD-0377':1000,'V33-OD-0378':1000})
add('intraop_remifentanil_EA_sham',ids([112]),'intraop_remifentanil','EA','sham','ADDITIONAL',unit='µg remifentanil')
# Native rescue components are not interchangeable with cumulative systemic exposure.
add('tramadol24_TEAS_usual_PCA',ids([299]),'PCA_tramadol_0_24h','TEAS','usual_care','SENSITIVITY',unit='mg IV tramadol')
add('tramadol24_TEAS_active_PCA',ids([300]),'PCA_tramadol_0_24h','TEAS','active_electrical','SENSITIVITY',unit='mg IV tramadol')
add('pethidine24_TEAS_usual_rescue',ids([303]),'rescue_pethidine_0_24h','TEAS','usual_care','ADDITIONAL',unit='mg IM pethidine')
add('pethidine24_TEAS_active_rescue',ids([304]),'rescue_pethidine_0_24h','TEAS','active_electrical','ADDITIONAL',unit='mg IM pethidine')
# Matched active-current non-acupoint control classified separately by conservative policy.
add('ponv24_TEAS_active',ids([331]),'composite_PONV_0_24h','TEAS','active_electrical','ADDITIONAL','RR','risk ratio',note='Song matched non-acupoint electrical stimulation; conservative active-control category. Broad-sham sensitivity available.')
add('pain24_TEAS_active_unspecified',ids([328]),'pain_setting_unspecified_24h','TEAS','active_electrical','SENSITIVITY',unit='0–10 points')
add('ponv24_TEAS_broad_sham_sensitivity',ids([27,33,130,131,168,195,215,257,261,276,331])+aids([359]),'composite_PONV_0_24h_broad_sham','TEAS','sham','SENSITIVITY','RR','risk ratio',note='Includes Song non-acupoint active-current sham as permitted by broader registered sham definition; diagnostic against conservative main taxonomy.')
# SMD comparison diagnostic only within each flatus stratum; same participants and membership.
for s in list(spec):
 if s['construct']=='time_first_flatus':
  d=copy.deepcopy(s);d.update(model_id=s['model_id']+'_SMD_sensitivity',measure='SMD',role='SENSITIVITY',unit='Hedges g',note='Same construct and membership as hours MD; no selection by I² or P.');spec.append(d)

def combine_arm(g):
 z=copy.deepcopy(g[0]);assert len(set((r['n_c'],r['mean_c'],r['sd_c'],r['events_c']) for r in g))==1,'Control mismatch '+str(g)
 if len(g)==1:return z
 n=sum(r['n_i'] for r in g);z['n_i']=n
 if g[0]['events_i'] is not None:z['events_i']=sum(r['events_i'] for r in g)
 else:
  mean=sum(r['n_i']*r['mean_i'] for r in g)/n
  sd=math.sqrt(sum((r['n_i']-1)*r['sd_i']**2+r['n_i']*(r['mean_i']-mean)**2 for r in g)/(n-1));z['mean_i']=mean;z['sd_i']=sd
 z['result_id']='+'.join(r['result_id'] for r in g);z['comparison_id']='COMBINED_COMPATIBLE_ACTIVE_ARMS';z['source_location']=' | '.join(r['source_location'] for r in g);return z
inputs=[];decisions=[]
for s in spec:
 group=collections.defaultdict(list)
 for id in s['result_ids']:
  r=rows[id];assert r['modality']==s['modality'],(id,r['modality'],s['modality']);x=copy.deepcopy(r)
  f=s['factor'].get(id,1) if isinstance(s['factor'],dict) else s['factor'];x['factor']=f
  for a in ['mean_i','mean_c','sd_i','sd_c']:
   if x[a] is not None:x[a]*=f
  group[x['trial_id']].append(x)
  r['models']+=';'+s['model_id'];r['decision']='INCLUDE' if s['role']!='SENSITIVITY' or r['decision']=='INCLUDE' else 'SENSITIVITY';r['rationale']=s['note']
  decisions.append(dict(result_id=id,model_id=s['model_id'],decision='SENSITIVITY' if s['role']=='SENSITIVITY' else 'INCLUDE',construct=s['construct'],window=r['window'],modality=s['modality'],comparator=s['comparator'],population=r['population'],rationale=s['note'],factor=f))
 for trial,g in group.items():
  x=combine_arm(g);x.update(model_id=s['model_id'],measure=s['measure'],construct=s['construct'],role=s['role'],analysis_unit=s['unit'],comparator_class=s['comparator'])
  if s['measure']=='RR':
   a,c=x['events_i'],x['events_c'];ni,nc=x['n_i'],x['n_c'];assert a is not None and c is not None and 0<=a<=ni and 0<=c<=nc
   if (a==0 and c==0) or (a==ni and c==nc):continue
   correction=.5 if min(a,ni-a,c,nc-c)==0 else 0
   aa=a+correction;cc=c+correction;nn1=ni+2*correction;nn0=nc+2*correction
   x['yi']=math.log((aa/nn1)/(cc/nn0));x['vi']=1/aa-1/nn1+1/cc-1/nn0;x['continuity_correction']=correction
  elif s['measure']=='MD':x['yi']=x['mean_i']-x['mean_c'];x['vi']=x['sd_i']**2/x['n_i']+x['sd_c']**2/x['n_c']
  else:
   ni,nc=x['n_i'],x['n_c'];df=ni+nc-2;sp=math.sqrt(((ni-1)*x['sd_i']**2+(nc-1)*x['sd_c']**2)/df);j=math.exp(math.lgamma(df/2)-.5*math.log(df/2)-math.lgamma((df-1)/2));g=j*(x['mean_i']-x['mean_c'])/sp;x['yi']=g;x['vi']=(ni+nc)/(ni*nc)+g*g/(2*(ni+nc))
  assert x['vi']>0
  inputs.append(x)
for r in rows.values():
 if not r['models']:decisions.append(dict(result_id=r['result_id'],model_id='NONE',decision=r['decision'],construct=r['family'],window=r['window'],modality=r['modality'],comparator=r['comparator_class'],population=r['population'],rationale=r['rationale']+' Source QC: '+r['source_qc'],factor=''))
writecsv('10_FINAL_ADJUDICATION/03_CANONICAL/results.csv',list(rows.values()));writecsv('FINAL_MODEL_MEMBERSHIP_MATRIX.csv',decisions);writecsv('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv',inputs)
(D/'02_DECISIONS/model_specifications.json').write_text(json.dumps(spec,indent=2))
trace=[]
for id in ids([13,14,214,350,351,252,3,52,6,7,16,107,108,184,185,111,190,191,67,68,245,246]):
 r=copy.deepcopy(rows[id]);r['registered_construct']='systemic opioid end surgery through24h';r['systemic_capture']='ALL SYSTEMIC OPIOID EXPOSURE supported by source' if id in ids([350,351,252,3]) else ('SYSTEMIC EXPOSURE WITH UNQUANTIFIED RESCUE' if id in ids([13,52,6,7]) else 'UNCLEAR / PCA OR NORMALIZED DOSE ONLY');trace.append(r)
writecsv('FINAL_PRIMARY_OUTCOME_TRACEABILITY.csv',trace)
print('Canonical rows',len(rows),'models',len(spec),'model input contrasts',len(inputs),'membership rows',len(decisions))
