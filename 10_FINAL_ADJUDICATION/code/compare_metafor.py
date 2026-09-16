"""Compare scipy model outputs with the independent R/metafor refit field by field."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
py = {m['model_id']: m for m in json.load(open(D / '04_MODELS/model_outputs.json'))}
mf = {r['model_id']: r for r in csv.DictReader(open(D / '05_REPRODUCTION/metafor_outputs.csv'))}
fitted = {k for k, v in py.items() if v['k']}
assert set(mf) == fitted, ('model sets differ', sorted(set(mf) ^ fitted))
rows = []
for mid in sorted(mf):
    for field in ['k', 'N', 'effect', 'se', 'ci_low', 'ci_high', 'p', 'tau2', 'I2', 'pi_low', 'pi_high']:
        a, b = py[mid].get(field), mf[mid][field]
        if a is None and b in ('NA', ''):
            continue
        a, b = float(a), float(b); tol = 1e-5 + 1e-5 * abs(a)
        rows.append(dict(model_id=mid, field=field, python=a, metafor=b, absolute_difference=abs(a - b), tolerance=tol, pass_check=abs(a - b) <= tol))
    for field in ['max_effect_input_difference', 'max_variance_input_difference']:
        rows.append(dict(model_id=mid, field=field, python=0, metafor=float(mf[mid][field]), absolute_difference=float(mf[mid][field]), tolerance=1e-10, pass_check=float(mf[mid][field]) <= 1e-10))
with open(D / '05_REPRODUCTION/metafor_comparison.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
fails = [r for r in rows if not r['pass_check']]
print(f'metafor comparison: {len(mf)} models, {len(rows)} fields, {len(fails)} failures')
for r in fails:
    print(' -', r)
