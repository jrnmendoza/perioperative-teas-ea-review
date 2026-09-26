"""Paired opioid-pain registry for the registered clinical-importance criterion.

For every opioid contrast in an E1 principal/supportive body or an E2 main body, list each
same-trial, same-comparator pain result in the canonical results register and classify the
pairing mechanically. No new adjudication: eligibility comes from the canonical model
specifications (pain_rest/pain_movement ~24 h constructs outside sensitivity roles, the rule
fit_models.py applies for pain_margin_result), and every other pain result carries its own
canonical decision and rationale as the reason it cannot be used.

Output: 10_PAIRED_PAIN/paired_pain_registry.csv (+ paired_pain.sha256).
"""
import csv, hashlib, json, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'; OUT = D / '10_PAIRED_PAIN'
Z = 1.959963984540054
rows = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))

E1 = {'opioid24_TEAS_sham': 'TEAS vs sham', 'opioid24_TEAS_usual': 'TEAS vs usual care', 'opioid24_EA_sham': 'EA vs sham', 'opioid24_EA_usual': 'EA vs usual care'}
E2 = {'E2_opioid24_TEAS_sham': 'TEAS vs sham', 'E2_opioid24_TEAS_usual': 'TEAS vs usual care', 'E2_opioid24_EA_sham': 'EA vs sham', 'E2_opioid24_EA_usual': 'EA vs usual care'}
CLASS = {'sham': 'sham', 'usual care': 'usual_care'}

results = rows(D / '03_CANONICAL/results.csv')
by_id = {r['result_id']: r for r in results}
specs = {s['model_id']: s for s in json.load(open(D / '02_DECISIONS/model_specifications.json'))}
registered_pain = {m for m, s in specs.items() if s['construct'].startswith(('pain_rest_approximately', 'pain_movement_approximately')) and s['role'] != 'SENSITIVITY'}

contrasts = [dict(analysis='E1', body=E1[r['model_id']], model_id=r['model_id'], study=r['study'], trial_id=r['trial_id'], result_id=r['result_id'],
                  comparator_class=r['comparator_class'], n_i=r['n_i'], n_c=r['n_c'], yi=r['yi'], vi=r['vi'])
             for r in rows(D / '04_MODELS/model_inputs.csv') if r['model_id'] in E1]
contrasts += [dict(analysis='E2', body=E2[r['model_id']], model_id=r['model_id'], study=r['study'], trial_id=r['trial_id'], result_id=r['result_id'],
                   comparator_class=CLASS[E2[r['model_id']].split(' vs ')[1]], n_i=r['n_i'], n_c=r['n_c'], yi=r['yi'], vi=r['vi'])
              for r in rows(D / '09_E2_ANALYSIS/e2_model_inputs.csv') if r['model_id'] in E2]

def ci(y, v): return (y - Z * math.sqrt(v), y + Z * math.sqrt(v))

out = []
for c in contrasts:
    y, v = float(c['yi']), float(c['vi']); lo, hi = ci(y, v)
    base = dict(analysis=c['analysis'], body=c['body'], opioid_model_id=c['model_id'], study=c['study'], trial_id=c['trial_id'],
                opioid_result_id=c['result_id'], opioid_n_i=c['n_i'], opioid_n_c=c['n_c'], opioid_md=y, opioid_ci_low=lo, opioid_ci_high=hi)
    # Same arms: the pain result's intervention/comparator descriptions equal those of the opioid result
    # (or of one component of a combined-arm result). E2.1 admissions have no register row, so they fall
    # back to the normalised comparator class.
    comps = [by_id[x] for x in c['result_id'].split('+') if x in by_id]
    same_arms = (lambda r: any((r['intervention'], r['comparator']) == (o['intervention'], o['comparator']) for o in comps)) if comps \
        else (lambda r: r['comparator_class'].lower().replace(' ', '_') == c['comparator_class'])
    pains = [r for r in results if r['trial_id'] == c['trial_id'] and same_arms(r)
             and any(k in r['outcome'].lower() for k in ('pain', 'vas', 'nrs'))]
    if not pains:
        out.append({**base, 'pain_result_id': '', 'pain_outcome': '', 'pain_window': '', 'pain_unit': '', 'pain_n_i': '', 'pain_n_c': '', 'pain_md': '', 'pain_ci_low': '', 'pain_ci_high': '',
                    'pain_decision': '', 'arm_match': '', 'pairing_status': 'NO SAME-TRIAL PAIN RESULT',
                    'reason': 'No pain result for this trial and comparator in the canonical results register.'})
        continue
    for p in pains:
        cont = p['data_type'] == 'Mean/SD'
        if cont:
            md = float(p['mean_i']) - float(p['mean_c']); se2 = float(p['sd_i']) ** 2 / float(p['n_i']) + float(p['sd_c']) ** 2 / float(p['n_c']); plo, phi = ci(md, se2)
        if '+' in c['result_id'] and '+' not in p['result_id']:
            arms = 'ONE OF COMBINED ARMS'
        elif p['n_i'] and float(p['n_i']) == float(c['n_i']) and float(p['n_c']) == float(c['n_c']):
            arms = 'SAME ARMS'
        else:
            arms = f"SAME ARM LABELS, DIFFERENT N (opioid {c['n_i']}/{c['n_c']}, pain {p['n_i']}/{p['n_c']})"
        eligible = cont and bool({m for m in p['models'].split(';') if m} & registered_pain)
        if eligible and arms == 'SAME ARMS':
            status, reason = 'ELIGIBLE PAIRED PAIN', 'Same trial and arms; in a registered ~24 h rest/movement pain body.'
        elif eligible:
            status, reason = 'PAIN ELIGIBLE, ARMS DIFFER', f'In a registered pain body but {arms.lower()}.'
        else:
            status, reason = 'NOT USABLE FOR REGISTERED CRITERION', f"{p['decision']}: {p['rationale'].strip()}" + ('' if cont else ' (not a continuous score)')
        out.append({**base, 'pain_result_id': p['result_id'], 'pain_outcome': p['outcome'], 'pain_window': p['window'], 'pain_unit': p['unit'],
                    'pain_n_i': p['n_i'], 'pain_n_c': p['n_c'], 'pain_md': md if cont else '', 'pain_ci_low': plo if cont else '', 'pain_ci_high': phi if cont else '',
                    'pain_decision': p['decision'], 'arm_match': arms, 'pairing_status': status, 'reason': reason})

OUT.mkdir(exist_ok=True)
with open(OUT / 'paired_pain_registry.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, list(out[0])); w.writeheader(); w.writerows(out)
files = [pathlib.Path(__file__), OUT / 'paired_pain_registry.csv']
(OUT / 'paired_pain.sha256').write_text(''.join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n" for f in files))
from collections import Counter
print(f"{len(contrasts)} opioid contrasts, {len(out)} registry rows:", dict(Counter(r['pairing_status'] for r in out)))
