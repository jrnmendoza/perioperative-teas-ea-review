"""Link existing assessments without synthesizing new RoB2 domain judgments."""
import json,csv,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION'
def loadcsv(p):return list(csv.DictReader(open(ROOT/p,encoding='utf-8-sig')))
def save(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with open(ROOT/p,'w',newline='') as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rs)
rows=loadcsv('10_FINAL_ADJUDICATION/03_CANONICAL/results.csv');corrected=json.load(open(ROOT/'ASTRA_VERIFICATION_SUPPORT/workbook.json'))['Corrected_RoB2'];reg=[];by_study={}
for i,r in enumerate(corrected):
 id=f'CORRECTED-V34-{i+1:03}';z=dict(assessment_id=id,study=r['Canonical study'],outcome=r['Selected result'],window=r['Timepoint/window'],comparison=r['Comparison'],population=r['Analyzed n'],**{f'd{j}':r[f'Domain {j}'] for j in range(1,6)},overall=r['Overall RoB 2'],provenance=r['Correction source'],source='v34 master: Corrected_RoB2 row'+str(i+2),human_signoff_date='NOT PRESENT IN CONSOLIDATED RECORD');reg.append(z);by_study[z['study']]=z
# Exact result applicability of selected corrected record; do not propagate study-level risk to all outcomes.
exact=[2,3,13,14,16,33,39,52,56,67,71,75,107,111,115,184,198,201,205,214,223,243,245,250,252,254,262,282,299,350]
exact={f'V33-OD-{n:04}' for n in exact}
# Existing AF-normalized records identify the exact outcome, population and contrast.
af=[]
for fn in ['target_A_48h.csv','target_B_72h.csv','target_C_pain24h.csv','target_D_ponv.csv','target_E_flatus.csv','target_F_exploratory.csv']:
 for r in loadcsv('06_FINAL_ANALYSIS_V26/01_DATA/'+fn):
  if not r.get('result_rob'):continue
  z=dict(assessment_id='AF26-'+r['lock_id'],study=r['study'],outcome=r['outcome'],window=r['time_window'],comparison=r['comparison_id'],population=f"{r['n_i']}/{r['n_c']}",**{f'd{j}':r.get(f'rob_d{j}','') for j in range(1,6)},overall=r['result_rob'],provenance=r.get('KeyQCnote',''),source='06_FINAL_ANALYSIS_V26/01_DATA/'+fn+'#'+r['lock_id'],human_signoff_date='NOT PRESENT IN CONSOLIDATED RECORD');reg.append(z);af.append((r,z))
def equal(a,b):
 for ca,cb in [('n_i','n_i'),('n_c','n_c'),('mean_i','mean_i'),('mean_c','mean_c'),('sd_i','sd_i'),('sd_c','sd_c'),('events_i','events_i'),('events_c','events_c')]:
  av,bv=a.get(ca,''),b.get(cb,'')
  if bool(av)!=bool(bv):return False
  if av:
   try:
    if abs(float(av)-float(bv))>1e-4:return False
   except:return False
 return True
# v36 (16 Sep 2026): manually reviewed exact matches where only the v26/v34 comparison-ID scheme differs
# (same study, outcome, window, denominators and all arm statistics). Yang2020 AUDIT-0078 vs F-mixed/undefined-005
# was rejected: identical counts but a different outcome (vomiting vs rescue bucinnazine).
manual={'V33-OD-0379':'AF26-F-intra-013','AUDIT-0364':'AF26-F-intra-012','V33-OD-0328':'AF26-SONG20-POSTLOCK-C'}
byid={z['assessment_id']:z for z in reg}
fresh=loadcsv('10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv')
fresh_by={z['result_id']:z for z in fresh}
assert len(fresh_by)==len(fresh)==94
reg.extend(fresh)
out=[]
for r in rows:
 candidates=[z for a,z in af if a['study']==r['study'] and a['comparison_id']==r['comparison_id'] and equal(a,r)]
 selected=None;rule=''
 if r['result_id'] in exact:selected=by_study[r['study']];rule='Exact result applicability manually mapped to latest consolidated corrected record; supersedes legacy selector.'
 elif candidates:selected=candidates[-1];rule='Exact source contrast and outcome statistics/population match to existing AF result assessment.'
 elif r['result_id'] in manual:
  selected=byid[manual[r['result_id']]];a=next(a for a,z in af if z is selected);assert a['study']==r['study'] and equal(a,r)
  rule='v36 reviewed exact match: same study/outcome/window/denominators/arm statistics; only comparison-ID scheme differs.'+(' v26 rest-pain label not source-supported; setting remains unspecified.' if r['result_id']=='V33-OD-0328' else '')
 alt=[z['assessment_id'] for z in candidates if not selected or z['assessment_id']!=selected['assessment_id']]
 z=dict(result_id=r['result_id'],outcome=r['outcome'],timepoint=r['window'],contrast=r['comparison_id'],population=r['population'],n_i=r['n_i'],n_c=r['n_c'],rob2_assessment_id=selected['assessment_id'] if selected else '',linkage_status='LINKED EXISTING RESULT ASSESSMENT' if selected else 'UNLINKED — no exact existing assessment established',overall=selected['overall'] if selected else 'UNLINKED',**{f'd{j}':selected[f'd{j}'] if selected else '' for j in range(1,6)},selection_rule=rule,alternative_assessments=';'.join(alt),provenance=selected['source'] if selected else 'Study-level record retained only as background; not an exact-result assessment.',human_final_signoff='NOT INDEPENDENTLY DOCUMENTED',models=r['models'])
 if r['result_id'] in fresh_by:
  a=fresh_by[r['result_id']]
  assert a['study']==r['study'] and a['outcome']==r['outcome'] and a['window']==r['window']
  assert a['population']==str(r['n_i'])+'/'+str(r['n_c'])
  z.update(rob2_assessment_id=a['assessment_id'],linkage_status='V38 AI-CONDUCTED EXACT RESULT ASSESSMENT',overall=a['overall'],**{f'd{j}':a[f'd{j}'] for j in range(1,6)},selection_rule='Fresh delegated source-based assessment; exact study/outcome/window/contrast/population. Historical judgments retained, not silently endorsed.',provenance=a['source'],human_final_signoff=a['human_signoff_date'],alternative_assessments=';'.join(filter(None,[z['rob2_assessment_id'],z['alternative_assessments']])))
 out.append(z)
save('FINAL_RESULT_ROB2_LINKAGE.csv',out);save('10_FINAL_ADJUDICATION/02_DECISIONS/existing_rob2_assessments.csv',reg)
print('Exact linked',sum(bool(r['rob2_assessment_id']) for r in out),'of',len(out),'unique canonical results')
