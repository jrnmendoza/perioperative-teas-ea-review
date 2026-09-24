"""Run the in-scope pipeline twice, cross-check R, regression-test metadata, and preserve logs/hashes.

Run using the numpy/scipy environment with ASTRA_R_LIBRARY set to a library containing metafor.
Does not screen records, run triage, edit sources, build the dashboard or communicate externally.
"""
import csv
import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT/'10_FINAL_ADJUDICATION'
V = D/'05_REPRODUCTION/v37'
os.chdir(ROOT)
CODE = D/'code'
chain = ['build_registry.py','build_results.py','fit_models.py','link_rob2.py',
         'grade_recommendations.py','crosswalk_covidence.py','build_reports.py',
         'validate_adjudication.py','build_v37_followup.py']


def run(command, log):
    p = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (V/log).write_text(p.stdout)
    print(log, 'PASS' if p.returncode==0 else 'FAIL', flush=True)
    if p.returncode:
        print(p.stdout)
        raise SystemExit(p.returncode)


def outputs():
    paths = [ROOT/line.split('  ',1)[1] for line in (D/'05_REPRODUCTION/output_sha256_v36.txt').read_text().splitlines()
             if 'exclusion_rescreen_triage.csv' not in line]
    paths += list((D/'02_DECISIONS/v37').glob('*.csv'))
    paths += [ROOT/'FINAL_CURRENT_STATE_REPORT.md', D/'05_REPRODUCTION/validation_report.json',
              D/'05_REPRODUCTION/R_session.txt', V/'followup_counts.json']
    paths += [D/'06_REPORTS'/name for name in ['model_comparison_v37.csv','model_analysis_manifest.csv',
              'primary_evidence_table.csv','PRISMA_REPORT_TRIAL_ACCOUNTING.md',
              'ROB2_PROVENANCE_RECONCILIATION_v37.md','UNRESOLVED_HUMAN_DECISIONS.md']]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


snapshots=[]
for iteration in [1,2]:
    for name in chain:
        run([sys.executable,str(CODE/name)],f'run{iteration}_{name}.log')
    run(['/usr/local/bin/Rscript',str(CODE/'reproduce_metafor.R')],f'run{iteration}_metafor.log')
    run([sys.executable,str(CODE/'compare_metafor.py')],f'run{iteration}_compare_metafor.log')
    validation=json.loads((D/'05_REPRODUCTION/validation_report.json').read_text())
    assert validation['overall']=='PASS'
    snapshots.append(outputs())
different=[p for p in snapshots[0] if snapshots[0][p]!=snapshots[1].get(p)]
assert not different, different

# In-memory mutation of the input after loading, not an edit to data or source files.
code=(CODE/'validate_adjudication.py').read_text()
needle="inputs = load('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv')"
assert code.count(needle)==1
mutated="__file__="+repr(str(CODE/'validate_adjudication.py'))+'\n'+code.replace(needle,needle+"\ninputs[0]['decision'] = 'EXCLUDE'")
test=subprocess.run([sys.executable,'-c',mutated],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(V/'negative_metadata_test.log').write_text(test.stdout)
negative=json.loads((D/'05_REPRODUCTION/validation_report.json').read_text())
(V/'negative_metadata_test.json').write_text(json.dumps(negative,indent=2)+'\n')
run([sys.executable,str(CODE/'validate_adjudication.py')],'restored_validation.log')
assert test.returncode==1 and negative['checks']['input_metadata']['status']=='FAIL'
assert all(v['status']=='PASS' for k,v in negative['checks'].items() if k!='input_metadata')
assert outputs()==snapshots[1], 'Regression-test restoration changed outputs'
run([sys.executable,str(CODE/'v37_integrity.py'),'verify'],'protected_integrity.log')
comparison=list(csv.DictReader(open(D/'05_REPRODUCTION/metafor_comparison.csv')))
assert all(r['pass_check']=='True' for r in comparison)
report=dict(status='PASS', deterministic_outputs=len(snapshots[0]), changed_outputs=different,
            output_sha256=snapshots[1], validator_groups=len(validation['checks']),
            metafor_fields=len(comparison), metafor_failed_fields=0,
            metadata_negative_control='Detected 1 corrupted decision field; exit 1; restored positive run passes',
            deferred='triage and reviewer screening package not executed; prior triage retained unchanged')
(V/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='output_sha256'},indent=2))
