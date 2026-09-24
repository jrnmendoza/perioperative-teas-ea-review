"""Preserve the inherited audit state and verify protected evidence/user work."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / '10_FINAL_ADJUDICATION'
RUN = D / '05_REPRODUCTION/v37'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    paths = set((D / '01_SOURCE_EVIDENCE').rglob('*'))
    paths.update((ROOT / 'dashboard').rglob('*'))
    paths.update([ROOT / 'scripts/build_site.py', ROOT / 'scripts/extract_article_figures.py'])
    for row in json.loads((D / '01_SOURCE_EVIDENCE/source_manifest.json').read_text()):
        paths.add(ROOT / row['file'])
    for row in json.loads((D / '01_SOURCE_EVIDENCE/supplements/supplement_manifest.json').read_text()):
        paths.add(ROOT / row['original_path'])
    paths.update(ROOT.glob('covidence_all_*.json'))
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths) if p.is_file()}


def snapshot():
    RUN.mkdir(parents=True, exist_ok=True)
    target = RUN / 'starting_state.json'
    if target.exists():
        raise SystemExit('Starting snapshot already exists; refusing to replace it.')
    state = dict(base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                 git_status=subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT, text=True),
                 protected_sha256=protected())
    baseline = RUN / 'baseline'
    baseline.mkdir()
    selected = [ROOT / 'FINAL_CURRENT_STATE_REPORT.md', ROOT / 'FINAL_GRADE_RECOMMENDATIONS.md']
    selected += list((D / '06_REPORTS').glob('*'))
    selected += [D / '04_MODELS/model_outputs.csv', D / '04_MODELS/model_outputs.json',
                 D / '03_CANONICAL/grade.csv', ROOT / 'FINAL_RESULT_ROB2_LINKAGE.csv',
                 D / '05_REPRODUCTION/validation_report.json', D / '05_REPRODUCTION/metafor_comparison.csv',
                 D / '05_REPRODUCTION/metafor_outputs.csv', D / '05_REPRODUCTION/R_session.txt']
    state['baseline_sha256'] = {}
    for p in selected:
        if p.is_file():
            relative = p.relative_to(ROOT)
            dest = baseline / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            state['baseline_sha256'][str(relative)] = sha(p)
    target.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n')
    print('Preserved', len(state['protected_sha256']), 'protected files and', len(state['baseline_sha256']), 'baseline artifacts.')


def verify():
    state = json.loads((RUN / 'starting_state.json').read_text())
    changed = [name for name, digest in state['protected_sha256'].items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    report = dict(base_commit=state['base_commit'], protected_files_checked=len(state['protected_sha256']),
                  changed_or_missing=changed, status='FAIL' if changed else 'PASS')
    (RUN / 'integrity.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if changed:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['snapshot', 'verify'])
    args = parser.parse_args()
    (snapshot if args.operation == 'snapshot' else verify)()
