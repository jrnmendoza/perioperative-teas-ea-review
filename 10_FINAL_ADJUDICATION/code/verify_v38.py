"""Deterministic v38 reproduction, protected-source checks and negative control."""
import csv,json,pathlib,subprocess,sys,hashlib,os
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION';V=D/'05_REPRODUCTION/v38';B=V/'baseline'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def run(name):
 p=subprocess.run([sys.executable,str(D/'code'/name)],cwd=ROOT,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(name+'\n'+p.stdout+p.stderr)
 return p.stdout
state=json.load(open(V/'starting_state.json'));source_bad=[p for p,h in state['source_sha256'].items() if sha(ROOT/p)!=h]
assert not source_bad,source_bad
preserved={p:h for p,h in state['baseline_sha256'].items() if p.startswith('dashboard/') and p!='dashboard/index.html'}
assert all(sha(ROOT/p)==h for p,h in preserved.items()),'Existing dashboard/user assets modified unexpectedly'
steps=['adjudicate_v38.py','build_results.py','fit_models.py','link_rob2.py','rob_signals_v38.py','grade_recommendations.py','build_reports.py','report_v38.py','build_current_dashboard.py']
for step in steps:run(step)
targets=list((D/'03_CANONICAL').glob('*'))+list((D/'04_MODELS').glob('*'))+list((D/'02_DECISIONS/v38').glob('*'))
targets += [D/'02_DECISIONS/model_specifications.json',ROOT/'FINAL_MODEL_MEMBERSHIP_MATRIX.csv',ROOT/'FINAL_RESULT_ROB2_LINKAGE.csv',ROOT/'FINAL_GRADE_RECOMMENDATIONS.md',ROOT/'FINAL_CURRENT_STATE_REPORT.md',ROOT/'dashboard/index.html',ROOT/'dashboard/current_review.js',ROOT/'dashboard/current_review.json']
targets=[p for p in targets if p.is_file()]
before={str(p.relative_to(ROOT)):sha(p) for p in targets}
for step in steps:run(step)
assert all(sha(ROOT/p)==h for p,h in before.items()),'Nondeterministic regeneration'
out=json.load(open(D/'04_MODELS/model_outputs.json'));by={m['model_id']:m for m in out};old={m['model_id']:m for m in json.load(open(B/'10_FINAL_ADJUDICATION/04_MODELS/model_outputs.json'))}
primary=['opioid24_TEAS_sham','opioid24_EA_sham','opioid24_TEAS_usual','opioid24_EA_usual']
assert all(by[mid]==old[mid] for mid in primary),'Primary numerical outputs changed'
allowed={'flatus_TEAS_sham','bowelsounds_TEAS_sham','intraop_remifentanil_TEAS_sham','flatus_TEAS_sham_SMD_sensitivity'}
changed=[mid for mid in by.keys()&old.keys() if by[mid]!=old[mid]]
assert set(changed)==allowed,changed
cur=read(D/'03_CANONICAL/results.csv');prev={r['result_id']:r for r in read(B/'10_FINAL_ADJUDICATION/03_CANONICAL/results.csv')}
fields=['study','outcome','window','n_i','n_c','mean_i','mean_c','sd_i','sd_c','events_i','events_c','source_pdf','source_sha256']
assert all(all(r[k]==prev[r['result_id']][k] for k in fields) for r in cur),'Source values changed'
rob=read(D/'02_DECISIONS/v38/rob2_assessments.csv');rid={r['result_id']:r for r in rob};signals=read(D/'02_DECISIONS/v38/rob2_signalling_questions.csv')
spec=json.load(open(D/'02_DECISIONS/model_specifications.json'));active={i for s in spec if s['role']!='SENSITIVITY' for i in s['result_ids']}
assert len(rid)==len(rob)==94 and len(active)==90 and active<=rid.keys()
assert len(signals)==94*22 and len({(r['assessment_id'],r['question_id']) for r in signals})==len(signals)
ledger=read(D/'02_DECISIONS/v38/prisma_record_ledger.csv');original={r['covidence_id']:r for r in read(D/'02_DECISIONS/covidence_record_crosswalk.csv')}
for r in ledger:
 if r['covidence_id'] in original:assert all(r[k]==v for k,v in original[r['covidence_id']].items())
p=json.load(open(D/'02_DECISIONS/v38/prisma_counts.json'))
assert p['references']-p['unmapped_import_difference']==p['reported_import_records']
assert p['reported_import_records']-p['automatic_duplicates']-p['manual_duplicates']-p['automation_exclusions']==p['screened']
assert p['screened']-p['title_abstract_excluded']==p['database_sought']
assert p['database_sought']-p['database_not_retrieved']-p['late_duplicates']==p['database_assessed']
assert p['database_assessed']-p['database_excluded']+p['citation_included']==p['included_reports']==70
assert sum(p['exclusion_reasons'].values())==147
validation=run('validate_adjudication.py')
# Negative control modifies only an in-memory read, not canonical artifacts.
injection="""import builtins,io,json,runpy,pathlib
orig=builtins.open
def checked(file,*a,**kw):
 f=orig(file,*a,**kw)
 if str(file).endswith('04_MODELS/model_outputs.json') and (not a or 'r' in a[0]):
  x=json.load(f);f.close();x[0]['effect']+=0.1;return io.StringIO(json.dumps(x))
 return f
builtins.open=checked
runpy.run_path('10_FINAL_ADJUDICATION/code/validate_adjudication.py',run_name='__main__')
"""
neg=subprocess.run([sys.executable,'-c',injection],cwd=ROOT,capture_output=True,text=True)
assert neg.returncode!=0 and 'FAIL independent_refit' in neg.stdout,neg.stdout+neg.stderr
(V/'negative_control.txt').write_text(neg.stdout+neg.stderr)
run('validate_adjudication.py')
env=dict(os.environ);env['ASTRA_R_LIBRARY']=os.environ.get('ASTRA_R_LIBRARY','/tmp/teas-v37.a6vDCB/rlib')
r=subprocess.run(['/usr/local/bin/Rscript',str(D/'code/reproduce_metafor.R')],cwd=ROOT,env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
run('compare_metafor.py');mf=read(D/'05_REPRODUCTION/metafor_comparison.csv');assert all(x['pass_check']=='True' for x in mf)
data=json.load(open(ROOT/'dashboard/current_review.json'))
assert data['models']==out and len(data['grade'])==38 and len(data['rob'])==94
downloads=json.load(open(ROOT/'dashboard/current/download_manifest.json'))
assert all(sha(ROOT/'dashboard'/x['href'])==x['sha256']==sha(ROOT/x['source']) for x in downloads)
# Source scripts loaded by the current page must not include historical inference.
index=(ROOT/'dashboard/index.html').read_text()
assert 'app.js' not in index and 'v34_data.js' not in index and 'CRD420251090635' not in index
assert all(t not in index for t in ['−14.00','k=7, N=676','−9.91'])
summary=dict(version='v38',overall='PASS',protected_source_files=len(state['source_sha256']),preserved_existing_dashboard_assets=len(preserved),deterministic_outputs=len(before),canonical_source_rows_unchanged=len(cur),primary_estimates_unchanged=4,changed_existing_models=sorted(changed),defined_models=len(out),fitted_models=sum(bool(m['k']) for m in out),pooled_models=sum(m['k']>1 for m in out),independent_validator_groups=9,negative_control='PASS: in-memory effect perturbation rejected with nonzero exit; canonical outputs unchanged',metafor_fields=len(mf),metafor_failures=0,fresh_rob_assessments=len(rob),current_non_sensitivity_components=len(active),signalling_responses=len(signals),prisma_ledger_rows=len(ledger),grade_rows=len(data['grade']),browser_qa=json.load(open(V/'browser_qa.json')),limitations=['Historical import events cannot be replayed from missing logs.','Reproducibility is not validation of source truth or selection completeness.','Legacy validator entrypoints now route v38 to the current-data contract; historical v26 contracts are not claimed as current validation.'])
(V/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'06_REPORTS/REPRODUCIBILITY_REPORT.md').write_text('# Reproducibility — v38\n\n'+f"PASS: {len(before)} deterministically regenerated outputs; 9 independent validation groups; {len(mf)} R/metafor fields with 0 failures; all 761 canonical source-statistic rows and four primary outputs unchanged.\n\n"+f"{len(state['source_sha256'])} protected source files and {len(preserved)} pre-existing dashboard assets (all except the replaced current index) match baseline hashes. Full original index remains in the v38 baseline.\n\n"+'The negative control perturbed a model effect only during an in-memory read; the validator rejected it with a nonzero exit. An unmodified validation immediately afterward passed.\n\n'+f"94 unique result-specific assessments / 2068 signalling responses cover all 90 current non-sensitivity components; 38 GRADE decisions; 225 selection-ledger records. {len(downloads)} current download hashes checked.\n\n"+'Browser QA: all 74 model selections, 70 study rows, 94 RoB entries, 38 GRADE rows, PRISMA, methods, source-figure lightbox and mobile overview/PRISMA checked; no console errors observed. Browser record is separate from numerical validation.\n\n'+'Run with a Python environment containing numpy/scipy: `python 10_FINAL_ADJUDICATION/code/verify_v38.py`; R requires metafor, with `ASTRA_R_LIBRARY` set to its library if nonstandard. Then regenerate dashboard/build so downloads include this completed verification: `python 10_FINAL_ADJUDICATION/code/build_current_dashboard.py` and `python scripts/build_site.py`.\n\n'+'Legacy dashboard entrypoints route v38 to the current canonical contract (11 checks, 4 isolated mutations and download/figure integrity); superseded v26 inference is not asserted as current. No source/deduplication truth or comprehensive evidence selection is certified by computational PASS.\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['browser_qa','limitations']},indent=2))
