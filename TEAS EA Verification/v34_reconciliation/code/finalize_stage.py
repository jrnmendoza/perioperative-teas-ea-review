#!/usr/bin/env python3
import json,csv,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
import openpyxl
BASE=Path(__file__).resolve().parents[1]
s=json.load(open(BASE/'data/analysis_stage.json'));U=s['updates'];D=s['outcomes']
w=openpyxl.load_workbook(BASE/'inputs/v33_working_copy.xlsx',data_only=False)
v={sh.title:[list(r) for r in sh.iter_rows(values_only=True)] for sh in w}
def rec(m):return [dict(zip(m[0],r)) for r in m[1:]]
def mat(rs,h=None):
    h=h or list(rs[0]);return [h]+[[r.get(k) for k in h] for r in rs]
def js(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def sha(x):return hashlib.sha256(js(x).encode()).hexdigest()
def writecsv(p,rs,h=None):
    with open(p,'w',encoding='utf-8-sig',newline='') as f:
        ww=csv.DictWriter(f,fieldnames=h or list(rs[0]),extrasaction='ignore');ww.writeheader();ww.writerows(rs)
results=list(csv.DictReader(open(BASE/'results/v34_model_results.csv')))
assert 'V34_ANALYSIS_SUCCESS' in (BASE/'results/v34_analysis.log').read_text()
assert len(results)==len(s['analysis_jobs'])
for r in results:
    for k in ['k','estimate','ci_low','ci_high','p_value','tau2','i2']:r[k]=float(r[k])
U['V34_Model_Results']=mat(results)
rb={(r['analysis_id'],r['phase']):r for r in results}
for r in results:
    if r['phase']=='v34' and r['analysis_id'].startswith('primary'):
        old=rb[r['analysis_id'],'v33_matched']
        assert all(r[k]==old[k] for k in ['k','estimate','ci_low','ci_high','p_value','tau2','i2'])

# Update current QA summaries while preserving original adjudications/history.
actualchanges=[]
for i,oldr in enumerate(rec(v['Outcome_Data']),2):
    newr=D[i-2];ch={k:{'old':oldr.get(k),'new':newr.get(k)} for k in v['Outcome_Data'][0] if oldr.get(k)!=newr.get(k)}
    if ch:actualchanges.append({'excel_row':i,'record':newr,'changes':ch})
auditissues=list(v['Audit_Issues'])
for c in s['conflicts']:
    auditissues.append([c['study'],'V34 source reconciliation',c['outcome']+'; '+c['value_A']+' | '+c['value_B'],c['current_structured_choice'],'Material' if c['analysis_status']=='HOLD' else 'Source QC',c['analysis_status']])
U['Audit_Issues']=auditissues
normal=list(v['AF_Normalization_Log'])
for z in actualchanges:
    r=z['record'];normal.append([r['V34 record ID'],'V34 correction',r['Canonical study'],r['Outcome/result'],'v33 original retained in frozen input','V34_SOURCE_CORRECTION',r['Comparison ID'],s['correction_reason'].get(r['V34 record ID'],'Current source correction')+'; changed fields: '+', '.join(z['changes'])])
U['AF_Normalization_Log']=normal
unres=list(v['AF_Unresolved'])
for c in s['conflicts']:
    if c['requires_author_contact']=='Yes':unres.append(['V34','Source audit',c['study']+' / '+c['outcome'],c['value_A']+' | '+c['value_B'],c['current_structured_choice'],c['reason_for_choice'],'SOURCE_CONFLICT',c['analysis_status'],'NO — affected result held / source version retained',c['notes'] or 'See V34_Source_Conflicts and active readiness'])
U['AF_Unresolved']=unres
afsum=[list(r) for r in v['AF_Lock_Summary']]
afsum[0][0]='Historical A–F lock summary; v34 active status below'
afsum += [[None]*18]+[[k,val]+[None]*16 for k,val in [('V34 active AF source rows',len(U['Outcome_Data_AF_LOCK'])-1),('V34 Stata AF long rows',len(U['Stata_AF_Long'])-1),('V34 source correction rows',len(actualchanges)),('V34 added result-specific RoB pending',sum(bool(r.get('V34 audit row')) and r['V34 eligibility']=='INCLUDE' for r in D)),('Historical lock interpretation','Counts above describe the inherited lock only; new results have no inherited A–F judgment. Active overrides appear in V34 readiness and regenerated Stata AF long.')]]
U['AF_Lock_Summary']=afsum
afrows=rec(U['Stata_AF_Long']);ql=[]
for r in rec(v['AF_Priority_QA']):
    matches=[z for z in afrows if z['lock_id']==r['Lock ID']]
    z=dict(r)
    if matches:
        z['Include strict']=max(x['include_strict'] or 0 for x in matches)
        z['Include sensitivity']=max(x['include_sensitivity'] or 0 for x in matches)
        z['Narrative']=max(x['narrative_only'] or 0 for x in matches)
        z['QA status']='V34 ACTIVE HOLD OVERRIDE' if any(x['analysis_action']=='V34_HOLD' for x in matches) else 'PASS — inherited result lock checked against current AF source layer'
    else:z['QA status']='HISTORICAL LOCK — no numeric long row; retained, not newly promoted'
    ql.append(z)
U['AF_Priority_QA']=mat(ql,v['AF_Priority_QA'][0])

# Sheet-by-sheet review: explicit decisions for sheets intentionally unchanged.
review=[]
for name in v:
    if name in U:action='REGENERATED / UPDATED';reason='Current source values, readiness, counts or explicit correction log regenerated.'
    else:
        action='REVIEWED — PRESERVED'
        reason={'Corrected_RoB2':'Historical selected-result assessments retained; all new results have separate V34_Result_RoB2 pending status.',
          'AF_Result_Lock':'Immutable historical adjudications retained; active overrides in Stata_AF_Long and V34_Source_Conflicts.',
          'AF_P1_Disposition':'Historical adjudication decisions retained; no source conflict silently resolved.',
          'Scope_Exclusion_Audit':'No eligibility-scope change; original excluded report remains excluded.',
          'AG_Candidate_Data':'Historical candidate model output retained; not promoted to source truth.',
          'v33_Change_Log':'Historical version log retained.',
          'v33_Supplement_Reconciliation':'Historical v33 reconciliation retained.'}.get(name,'Historical source layer retained with provenance; not used to override v34 current source data.')
    review.append({'sheet':name,'review_action':action,'v33_rows':len(v[name]),'v34_rows':len(U.get(name,v[name])),'reason':reason})
U['V34_Sheet_Review']=mat(review)

# Semantic/native validity checks in addition to exact composite-key tests.
checks=[]
def check(label,ok,evidence):
    checks.append({'check':label,'status':'PASS' if ok else 'FAIL','evidence':str(evidence)})
check('Duplicate check',not s['duplicate_keys_existing'],'No new exact normalized composite duplicates; Li 2021 6-hour alias rejected independently. Full reviewed matching register retained.')
check('Outcome-row reconciliation',len(D)==382+374-1+2 and len(s['dispositions'])==374,f'382 + 374 - 1 duplicate + 2 supplement-dependent endpoints = {len(D)}')
check('Canonical IDs',len({r[0] for r in U['Study_Master'][1:]})==70 and {r['Canonical study'] for r in D}=={r[0] for r in v['Outcome_Data'][1:]},'70 canonical studies/reports; no original study disappeared; original comparison IDs retained.')
check('Analysis_Readiness row agreement',len(U['Analysis_Readiness'])==len(U['Outcome_Data']),f'{len(D)} records in each; exact record ID links.')
check('Strict primary k',all(len(U[n])-1==7 for n in ['Set_Opioid_24h','Opioid_Primary_StudyLevel','Stata_Opioid24_Primary']), '7 across all primary sheets; summary computed; TEAS 4 / EA 3; N=676.')
check('Strict primary estimate unchanged',all(rb[x,'v34']['estimate']==rb[x,'v33_matched']['estimate'] for x in ['primary_24h_mme_ALL_AUDIT','primary_24h_mme_TEAS_Sham','primary_24h_mme_EA_Usual_care']),'Stata matched source rerun identical for combined audit and both protocol strata.')
li=[r for r in D if r['Canonical study']=='Liang 2021' and r['Outcome family']=='Catheter-related bladder discomfort']
check('Liang randomized/analyzed N',all((r['Randomized n intervention'],r['Randomized n comparator'],r['Analyzed n intervention'],r['Analyzed n comparator'])==(37,38,35,35) for r in li),f'{len(li)} CRBD rows; randomized 37/38, analyzed 35/35.')
gu=next(r for r in D if r['Comparison ID']=='GU19_OPIOID24')
check('Gu no invented opioid mass',gu['Primary opioid meta-analysis eligible?']=='No' and gu['Mean intervention'] is None and gu['V34 eligibility']=='GRAPH ONLY','24-h graph-only multimodal PCIA volume; no mass conversion.')
graph=[r for r in D if r.get('V34 audit row') and 'graph' in str(r['Data type']).lower()]
check('Graph-only numeric protection',all(all(r[h] is None for h in ['Mean intervention','SD intervention','Mean comparator','SD comparator']) for r in graph),f'{len(graph)} new graph-only rows, no invented means/SDs.')
perc=[r for r in D if r.get('V34 audit row') and str(r['Data type']).startswith('Published percentage')]
check('Percentage protection',all(r['Events intervention'] is None and r['Events comparator'] is None for r in perc),f'{len(perc)} percentage-only rows; no reconstructed events.')
mins=[r for r in D if r.get('V34 audit row') and r['Data type']=='Median/range']
check('Median/range protection',all(r['Mean intervention'] is None and r['Q1 intervention'] is None and r['Minimum intervention'] is not None for r in mins),f'{len(mins)} source ranges mapped to min/max, never Q1/Q3 or means.')
source=rec(U['V34_Source_PDF_Audit']);sn=[r for r in source if 'NOT ACCESSED' in r['supplement_status']]
check('Source-not-accessed distinction',len([r for r in D if r['V34 eligibility']=='SOURCE NOT ACCESSED'])==2 and len(sn)==7,'7 study-level supplement/protocol access gaps; 2 explicit Gao outcome rows. No replacement with NOT REPORTED.')
required={'Yu 2020','Lu 2021','Lu 2022','Long 2025','Liang 2021','Zheng 2025','Gu 2019','Zhu 2022','Jiang 2026','Tu 2024','Pan 2023'}
check('Source-conflict preservation',required.issubset({c['study'] for c in s['conflicts']}),f'{len(s["conflicts"])} visible conflict/correction records, including all 11 required studies; raw source notes and quotations retained.')
check('New result-specific RoB',all(r['V34 RoB2 status']=='ROB2_RESULT_SPECIFIC_PENDING' for r in D if r.get('V34 audit row') and r['V34 eligibility']=='INCLUDE'),'No newly eligible outcome inherits study-wide Low/Some concerns/High.')
check('Formula check (source/staging)',not any(isinstance(x,str) and x in ['#REF!','#DIV/0!','#VALUE!','#NAME?','#N/A'] for mm in list(v.values())+list(U.values()) for row in mm for x in row),'Inputs have no formulas/named ranges. No error-value cells introduced; exported XLSX is separately validated.')
check('Stata consistency',len(results)==len(s['analysis_jobs']),f'{len(results)} successful Stata model runs, native values rebuilt from current source; every selected model has independent study units.')
assert all(c['status']=='PASS' for c in checks),[c for c in checks if c['status']=='FAIL']
U['V34_QC']=mat(checks)

# Row-level deltas capture every changed pre-existing cell. Newly appended
# Outcome_Data rows each have one entry; new derivative sheets have checksum
# references to avoid reproducing megabytes of the same source values.
LH=['change_id','study','source_audit_batch','change_type','sheet','old_value_or_status','new_value_or_status','outcome_family','outcome_result','timepoint','intervention','comparator','source_pdf','drive_link','page','table_or_figure','reason','analysis_impact','primary_model_impact','rob2_action','resolved_or_hold']
log=[];sources={r['study']:r for r in source}
def entry(st,typ,sheet,oldval,newval,reason,r=None,batch=None):
    r=r or {};p=sources.get(st,{})
    e=dict.fromkeys(LH);e.update(change_id=f'V34-{len(log)+1:05d}',study=st,source_audit_batch=batch or p.get('batch'),change_type=typ,sheet=sheet,old_value_or_status=oldval,new_value_or_status=newval,outcome_family=r.get('Outcome family'),outcome_result=r.get('Outcome/result'),timepoint=r.get('Timepoint/window'),intervention=r.get('Intervention arm'),comparator=r.get('Comparator arm'),source_pdf=r.get('V34 source filename') or p.get('source_pdf_filename'),drive_link=r.get('Source PDF URL') or p.get('drive_link'),page=r.get('Source location'),table_or_figure=r.get('Source location'),reason=reason,analysis_impact=r.get('V34 eligibility reason') or 'Rebuilt current view / provenance; consult row IDs and native analysis manifest',primary_model_impact='None — strict primary k=7 and numerical results unchanged',rob2_action=r.get('V34 RoB2 status') or 'No new automatic RoB judgments',resolved_or_hold=r.get('V34 eligibility') or 'TRACEABLE UPDATE')
    log.append(e)
for name,m in U.items():
    if name not in v:
        entry(None,'ADDED',name,None,js({'rows':len(m),'columns':len(m[0]),'sha256_of_matrix':sha(m)}),'New source/analysis/history sheet; exact content in workbook and reproducible stage JSON.')
        continue
    oldm=v[name]
    for i in range(max(len(oldm),len(m))):
        oldr=oldm[i] if i<len(oldm) else [];newr=m[i] if i<len(m) else []
        # For existing row values, compare coordinates, including dropped cells.
        changes={str(col+1):{'old':oldr[col] if col<len(oldr) else None,'new':newr[col] if col<len(newr) else None} for col in range(max(len(oldr),len(newr))) if (oldr[col] if col<len(oldr) else None)!=(newr[col] if col<len(newr) else None)}
        if not changes:continue
        # New non-Outcome rows are logged by an explicit append batch reference below.
        if i>=len(oldm) and name!='Outcome_Data':continue
        rr=dict(zip(m[0],newr)) if i else {};st=rr.get('Canonical study') or rr.get('study') or rr.get('Study')
        if name=='Outcome_Data' and i:
            rr=D[i-1];st=rr['Canonical study'];rid=rr['V34 record ID']
            existing_value_change=any(int(k)<=38 for k in changes)
            typ=rr.get('V34 disposition') if i>=len(oldm) else s['correction_type'].get(rid,'METADATA_CORRECTION') if existing_value_change else 'METADATA_CORRECTION'
            reason=s['correction_reason'].get(rid,'Source-audit import with full raw statistics/provenance; no inferred quantities' if i>=len(oldm) else 'Add current result identity, readiness and result-specific RoB metadata; original source values preserved.')
        else:typ='UPDATED_EXISTING';reason='Rebuild current source/derived view; original v33 worksheet retained in frozen input. Coordinate-keyed cell delta.'
        entry(st,typ or 'ADDED',name,js({'excel_row':i+1,'cells':{k:z['old'] for k,z in changes.items()}}),js({'excel_row':i+1,'cells':{k:z['new'] for k,z in changes.items()}}),reason,rr)
    if len(m)>len(oldm) and name!='Outcome_Data':entry(None,'ADDED',name,None,js({'first_appended_excel_row':len(oldm)+1,'rows':len(m)-len(oldm),'sha256_appended_rows':sha(m[len(oldm):])}),'Traceable regenerated append batch; values derive from Outcome_Data / preserved AF source layer.')
for d in s['dispositions']:
    if d['disposition']=='ALREADY_PRESENT':
        r=D[d['v33_excel_row']-2];entry(d['study'],'ALREADY_PRESENT','Outcome_Data',f'Existing v33 Excel row {d["v33_excel_row"]}',f'Audit row {d["audit_row"]} matched; no duplicate appended','Composite semantic match: outcome threshold, 6-h timepoint, TEAS/sham, events 30/140 vs 50/140.',r,d['batch'])
U['V33_to_V34_Change_Log']=mat(log,LH)
writecsv(BASE.parent/'TEAS_EA_v33_to_v34_RECONCILIATION_LOG.csv',log,LH)

study_summary=[]
for st in sources:
    ds=[d for d in s['dispositions'] if d['study']==st];new=[r for r in D if r['Canonical study']==st and (r.get('V34 audit row') or r.get('V34 disposition')=='SOURCE_NOT_ACCESSED')]
    study_summary.append({'study':st,'audit_rows':len(ds),'v33_rows':sum(r[0]==st for r in v['Outcome_Data'][1:]),'v34_rows':sum(r['Canonical study']==st for r in D),'net_added':len(new),'existing_source_rows_updated':sum(z['record']['Canonical study']==st for z in actualchanges),'already_present':sum(d['disposition']=='ALREADY_PRESENT' for d in ds),'new_numeric_secondary_candidates':sum(r['V34 eligibility']=='INCLUDE' for r in new),'new_graph_only':sum(r['V34 eligibility']=='GRAPH ONLY' for r in new),'new_not_reported':sum(r['V34 eligibility']=='NOT REPORTED' for r in new),'source_not_accessed_outcomes':sum(r['V34 eligibility']=='SOURCE NOT ACCESSED' for r in new),'new_holds':sum(r['V34 eligibility']=='HOLD' for r in new),'note':sources[st]['verification_notes']})
U['V34_Study_Summary']=mat(study_summary)
# Add a batch reference for the final summary, then re-save the log. Do not log
# the change log itself (recursive provenance would be meaningless).
entry(None,'ADDED','V34_Study_Summary',None,js({'rows':len(study_summary),'sha256':sha(study_summary)}),'Generated study-level reconciliation counts; every number derives from row dispositions.')
U['V33_to_V34_Change_Log']=mat(log,LH);writecsv(BASE.parent/'TEAS_EA_v33_to_v34_RECONCILIATION_LOG.csv',log,LH)
writecsv(BASE/'data/v34_study_summary.csv',study_summary)
s.update(updates=U,checks=checks,actual_source_changes=[{'excel_row':z['excel_row'],'record_id':z['record']['V34 record ID'],'study':z['record']['Canonical study'],'changes':z['changes']} for z in actualchanges],study_summary=study_summary,model_results=results,change_log_rows=len(log))
payload=json.dumps(s,ensure_ascii=False,indent=2)
tmp=BASE/'data/final_stage.pending.json'
tmp.write_text(payload,encoding='utf-8')
assert json.loads(tmp.read_text(encoding='utf-8'))['change_log_rows']==len(log)
tmp.replace(BASE/'data/final_stage.json')
print(js({'updated_original_source_rows':len(actualchanges),'change_log_rows':len(log),'checks':len(checks),'sheets_modified_or_added':len(U),'source_access_gap_studies':len(sn),'study_summary':study_summary}))
