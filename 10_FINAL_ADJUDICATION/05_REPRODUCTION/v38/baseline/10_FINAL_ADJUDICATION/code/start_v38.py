"""Preserve the v37 state and existing user dashboard work before authorized v38 edits."""
import hashlib,json,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]; D=ROOT/'10_FINAL_ADJUDICATION'; V=D/'05_REPRODUCTION/v38'
assert not (V/'starting_state.json').exists(), 'Do not overwrite the v38 baseline'
V.mkdir(parents=True,exist_ok=True)
paths=list((ROOT/'dashboard').rglob('*'))+list((D/'code').glob('*.py'))
paths+=list((D/'03_CANONICAL').glob('*'))+list((D/'04_MODELS').glob('*'))+list((D/'06_REPORTS').glob('*'))
paths += [ROOT/n for n in ['scripts/build_site.py','FINAL_CURRENT_STATE_REPORT.md','FINAL_RESULT_ROB2_LINKAGE.csv','FINAL_GRADE_RECOMMENDATIONS.md','FINAL_MODEL_MEMBERSHIP_MATRIX.csv']]
snap={}
for p in paths:
 if p.is_file():
  rel=p.relative_to(ROOT); target=V/'baseline'/rel; target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
  snap[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((D/'05_REPRODUCTION/v37/starting_state.json').read_text())
source={k:v for k,v in prior['protected_sha256'].items() if not k.startswith(('dashboard/','scripts/'))}
state=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),baseline_sha256=snap,source_sha256=source)
(V/'starting_state.json').write_text(json.dumps(state,indent=2)+'\n')
print('v38 baseline files',len(snap),'protected source files',len(source))
