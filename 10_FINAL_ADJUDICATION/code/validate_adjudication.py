"""Independent validation of the adjudication layer (v36, 16 Sep 2026).

Does not import or reuse build/fit code. Re-derives model inputs from canonical result rows and the
model specification, refits with Fisher-scoring REML (a different algorithm from fit_models.py), and
checks provenance, membership, family uniqueness, RoB/GRADE correspondence and source integrity.
A PASS establishes internal consistency and numerical reproducibility only; it does not validate
source truth or review completeness.
"""
import csv, json, math, hashlib, pathlib, re, collections, sys
from scipy.stats import t as tdist, norm

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / '10_FINAL_ADJUDICATION'
TOL_REL, TOL_ABS = 1e-6, 1e-8
checks = collections.OrderedDict()


def load(p):
    return list(csv.DictReader(open(ROOT / p, encoding='utf-8-sig')))


def record(name, failures, n):
    checks[name] = dict(status='PASS' if not failures else 'FAIL', n_checked=n, n_failed=len(failures), failures=failures[:50])


def f(v):
    return None if v in ('', None) else float(v)


results = {r['result_id']: r for r in load('10_FINAL_ADJUDICATION/03_CANONICAL/results.csv')}
studies = json.load(open(D / '03_CANONICAL/studies.json'))
mapping = {r['report_id']: r for r in load('FINAL_TRIAL_REPORT_MAPPING.csv')}
spec = json.load(open(D / '02_DECISIONS/model_specifications.json'))
inputs = load('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv')
outputs = {m['model_id']: m for m in json.load(open(D / '04_MODELS/model_outputs.json'))}
link = {r['result_id']: r for r in load('FINAL_RESULT_ROB2_LINKAGE.csv')}
grade = {r['model_id']: r for r in load('10_FINAL_ADJUDICATION/03_CANONICAL/grade.csv')}
manifest = json.load(open(D / '01_SOURCE_EVIDENCE/source_manifest.json'))
study_by = {s['report_id']: s for s in studies}

# 1. Source integrity.
fails = []
for x in manifest:
    p = ROOT / x['file']
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != x['sha256']:
        fails.append(f"{x['study']}: PDF missing or hash mismatch")
    if not (ROOT / x['text_file']).exists():
        fails.append(f"{x['study']}: extracted text missing")
ident = json.load(open(D / '00_STARTING_STATE/run_identity.json'))
if hashlib.sha256((D / '01_SOURCE_EVIDENCE/PROSPERO_authoritative_supplied.pdf').read_bytes()).hexdigest() != ident['protocol_sha256']:
    fails.append('PROSPERO PDF hash differs from run_identity.json')
sups = json.load(open(D / '01_SOURCE_EVIDENCE/supplements/supplement_manifest.json'))
for x in sups:
    for p, h in [(x['original_path'], x['original_sha256']), (x['copy_path'], x['copy_sha256'])]:
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h:
            fails.append(f'supplement hash mismatch: {p}')
record('source_integrity', fails, len(manifest) + 1 + 2 * len(sups))

# 2. Registry/mapping/results consistency.
fails = []
if len(studies) != 70 or len({s['trial_id'] for s in studies}) != 69:
    fails.append(f'expected 70 reports/69 trial units, got {len(studies)}/{len({s["trial_id"] for s in studies})}')
for s in studies:
    m = mapping[s['report_id']]
    for k in ['trial_id', 'modality', 'comparator', 'randomized_n_counted', 'source_sha256']:
        if str(s[k]) != str(m[k]):
            fails.append(f"{s['report_id']}: studies.json {k}={s[k]} vs mapping {m[k]}")
for r in results.values():
    s = study_by[r['study']]
    if r['modality'] != s['modality'] or r['trial_id'] != s['trial_id']:
        fails.append(f"{r['result_id']}: result modality/trial {r['modality']}/{r['trial_id']} vs registry {s['modality']}/{s['trial_id']}")
yeh = [s for s in studies if s['report_id'].startswith('Yeh ')]
if {s['trial_id'] for s in yeh} != {'Yeh_probable_family'} or sum(int(s['randomized_n_counted']) for s in yeh) != 99:
    fails.append('Yeh family not held as one trial unit counted once (99)')
record('registry_consistency', fails, len(studies) + len(results))

# 3. Membership semantics.
GATE = {'sham': {'Sham'}, 'usual_care': {'Usual care'}, 'active_electrical': {'Active electrical'}}
BROAD = {'ponv24_TEAS_broad_sham_sensitivity'}
fails = []
n = 0
for s in spec:
    for rid in s['result_ids']:
        n += 1
        r = results.get(rid)
        if r is None:
            fails.append(f"{s['model_id']}: missing result {rid}"); continue
        if r['modality'] != s['modality']:
            fails.append(f"{s['model_id']}: {rid} modality {r['modality']}")
        if r['comparator_class'] not in GATE[s['comparator']] and s['model_id'] not in BROAD:
            fails.append(f"{s['model_id']}: {rid} comparator {r['comparator_class']} not {s['comparator']}")
        if r['trial_id'] == 'Yeh_probable_family' or r['study'] in ('Jin 2023', 'Long 2025'):
            fails.append(f"{s['model_id']}: held study {r['study']} admitted")
        if not r['source_location'] or not r['source_pdf'] or not r['source_sha256']:
            fails.append(f"{s['model_id']}: {rid} lacks source location/PDF/hash")
        if s['role'] != 'SENSITIVITY' and r['decision'] != 'INCLUDE':
            fails.append(f"{s['model_id']}: non-sensitivity body uses {rid} with decision {r['decision']}")
        if s['model_id'] not in r['models'].split(';'):
            fails.append(f"{s['model_id']}: {rid} membership not recorded on canonical row")
    if s['role'] in ('PRINCIPAL', 'SUPPORTIVE') and s['construct'] == 'systemic_opioid_0_24h':
        for rid in s['result_ids']:
            if 'mg' not in results[rid]['unit'] or '/kg' in results[rid]['unit']:
                fails.append(f"{s['model_id']}: {rid} unit {results[rid]['unit']} not absolute mg")
if any(s['modality'] not in ('TEAS', 'EA') for s in spec):
    fails.append('model without single modality')
record('membership_semantics', fails, n)

# v37: exported input metadata must describe the specific model, not an earlier snapshot.
fails = []
for r in inputs:
    expected = 'SENSITIVITY' if r['role'] == 'SENSITIVITY' else 'INCLUDE'
    if r['decision'] != expected or r['models'] != r['model_id']:
        fails.append(f"{r['model_id']}/{r['result_id']}: stale decision/models metadata")
record('input_metadata', fails, len(inputs))

# 4. Independent re-derivation of model inputs (arm combination, factors, effect sizes).
def combine(rows):
    if len(rows) == 1:
        return dict(rows[0])
    z = dict(rows[0]); ni = sum(r['n_i'] for r in rows); z['n_i'] = ni
    if rows[0]['events_i'] is not None:
        z['events_i'] = sum(r['events_i'] for r in rows)
    else:
        m = sum(r['n_i'] * r['mean_i'] for r in rows) / ni
        ss = sum((r['n_i'] - 1) * r['sd_i'] ** 2 + r['n_i'] * (r['mean_i'] - m) ** 2 for r in rows)
        z['mean_i'], z['sd_i'] = m, math.sqrt(ss / (ni - 1))
    return z


derived = {}
fails = []
for s in spec:
    by_trial = collections.defaultdict(list)
    for rid in s['result_ids']:
        r = results[rid]
        fac = s['factor'].get(rid, 1) if isinstance(s['factor'], dict) else s['factor']
        x = {k: f(r[k]) for k in ['n_i', 'n_c', 'mean_i', 'sd_i', 'mean_c', 'sd_c', 'events_i', 'events_c']}
        for k in ['mean_i', 'sd_i', 'mean_c', 'sd_c']:
            if x[k] is not None:
                x[k] *= fac
        by_trial[r['trial_id']].append(x)
    ys = []
    for trial, rows in by_trial.items():
        if len({(r['n_c'], r['mean_c'], r['sd_c'], r['events_c']) for r in rows}) != 1:
            fails.append(f"{s['model_id']}/{trial}: shared comparator differs across combined arms")
        x = combine(rows)
        if s['measure'] == 'RR':
            a, c, n1, n0 = x['events_i'], x['events_c'], x['n_i'], x['n_c']
            if (a == 0 and c == 0) or (a == n1 and c == n0):
                continue
            cc = 0.5 if 0 in (a, n1 - a, c, n0 - c) else 0.0
            # 0.5 to each of the four cells: arm totals rise by 1, never by 0.5.
            a1, b1, c1, d1 = a + cc, n1 - a + cc, c + cc, n0 - c + cc
            y = math.log((a1 / (a1 + b1)) / (c1 / (c1 + d1))); v = 1 / a1 - 1 / (a1 + b1) + 1 / c1 - 1 / (c1 + d1)
        elif s['measure'] == 'MD':
            y = x['mean_i'] - x['mean_c']; v = x['sd_i'] ** 2 / x['n_i'] + x['sd_c'] ** 2 / x['n_c']
        else:
            n1, n0 = x['n_i'], x['n_c']; df = n1 + n0 - 2
            sp = math.sqrt(((n1 - 1) * x['sd_i'] ** 2 + (n0 - 1) * x['sd_c'] ** 2) / df)
            j = 1 - 3 / (4 * df - 1)  # approximation; compared with looser tolerance below
            g = j * (x['mean_i'] - x['mean_c']) / sp; y = g; v = (n1 + n0) / (n1 * n0) + g * g / (2 * (n1 + n0))
        ys.append((trial, y, v, x['n_i'] + x['n_c']))
    derived[s['model_id']] = ys
# Compare with stored inputs.
stored = collections.defaultdict(list)
for r in inputs:
    stored[r['model_id']].append(r)
n = 0
for mid, ys in derived.items():
    st = {r['trial_id']: r for r in stored[mid]}
    if len(st) != len(stored[mid]):
        fails.append(f'{mid}: duplicate trial family within model inputs')
    if set(st) != {t for t, *_ in ys}:
        fails.append(f'{mid}: trial set differs {sorted(st)} vs {sorted(t for t, *_ in ys)}')
        continue
    smd = any(r['measure'] == 'SMD' for r in stored[mid])
    for trial, y, v, _ in ys:
        n += 1
        tol = 5e-4 if smd else 1e-9
        if abs(float(st[trial]['yi']) - y) > tol * max(1, abs(y)) or abs(float(st[trial]['vi']) - v) > tol * max(1, v):
            fails.append(f'{mid}/{trial}: yi/vi {st[trial]["yi"]}/{st[trial]["vi"]} vs independent {y}/{v}')
record('input_rederivation', fails, n)

# 5. Independent Fisher-scoring REML + safeguarded Hartung-Knapp.
def reml(y, v):
    tau = max(0.0, (sum((yi - sum(y) / len(y)) ** 2 for yi in y) / (len(y) - 1)) - sum(v) / len(v))
    for _ in range(2000):
        w = [1 / (vi + tau) for vi in v]; sw = sum(w); mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
        # P-matrix quantities for REML score and Fisher information (diagonal V).
        r = [yi - mu for yi in y]
        trP = sum(w) - sum(wi * wi for wi in w) / sw
        trPP = sum(wi * wi for wi in w) - 2 * sum(wi ** 3 for wi in w) / sw + (sum(wi * wi for wi in w) / sw) ** 2
        rPPr = sum((wi * ri) ** 2 for wi, ri in zip(w, r))
        step = (rPPr - trP) / trPP
        new = max(0.0, tau + step)
        if abs(new - tau) < 1e-12 * max(1, tau):
            tau = new; break
        tau = new
    w = [1 / (vi + tau) for vi in v]; sw = sum(w); mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    return tau, mu, sw, w


fails = []
n = 0
for s in spec:
    mid = s['model_id']; out = outputs[mid]; ys = derived[mid]; k = len(ys)
    if out['k'] != k or out['N'] != int(sum(z[3] for z in ys)):
        fails.append(f"{mid}: k/N {out['k']}/{out['N']} vs {k}/{int(sum(z[3] for z in ys))}")
    if k == 0:
        continue
    y = [z[1] for z in ys]; v = [z[2] for z in ys]
    if k == 1:
        tau, mu, se, crit = 0.0, y[0], math.sqrt(v[0]), norm.ppf(.975)
    else:
        tau, mu, sw, w = reml(y, v)
        q = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y)) / (k - 1)
        se = math.sqrt(max(1.0, q) / sw); crit = tdist.ppf(.975, k - 1)
    exp = dict(effect=mu, se=se, ci_low=mu - crit * se, ci_high=mu + crit * se, tau2=tau)
    tol = 5e-4 if s['measure'] == 'SMD' else 1e-6
    for key, val in exp.items():
        n += 1
        o = out.get(key)
        if abs(o - val) > tol * max(1, abs(val)) + (1e-6 if key == 'tau2' else 0):
            fails.append(f'{mid}: {key} stored {o} vs independent {val}')
    if (k >= 5) != (out.get('pi_low') is not None):
        fails.append(f'{mid}: prediction-interval display rule violated (k={k})')
    if k == 1 and (out.get('I2') is not None or out['status'] != 'SINGLE STUDY — NOT POOLED'):
        fails.append(f'{mid}: k=1 presented as pooled')
record('independent_refit', fails, n)

# 6. RoB linkage correspondence.
fails = []
reg = {r['assessment_id']: r for r in load('10_FINAL_ADJUDICATION/02_DECISIONS/existing_rob2_assessments.csv')}
n = 0
for rid, l in link.items():
    if not l['rob2_assessment_id']:
        if l['overall'] != 'UNLINKED':
            fails.append(f'{rid}: unlinked result carries a rating {l["overall"]}')
        continue
    n += 1
    a = reg[l['rob2_assessment_id']]; r = results[rid]
    if a['study'] != r['study']:
        fails.append(f'{rid}: assessment study {a["study"]} != {r["study"]}')
    if l['overall'] != a['overall']:
        fails.append(f'{rid}: overall {l["overall"]} != assessment {a["overall"]}')
    if not a['population'] or not re.search(r'\d', a['population']):
        fails.append(f'{rid}: assessment population not specified')
if set(link) != set(results):
    fails.append('linkage rows do not cover canonical results exactly')
record('rob2_linkage', fails, n)

# 7. GRADE correspondence.
fails = []
nonsens = [s['model_id'] for s in spec if s['role'] != 'SENSITIVITY']
for mid in nonsens:
    if mid not in grade:
        fails.append(f'{mid}: no GRADE row')
for mid in grade:
    if mid not in outputs or outputs[mid]['role'] == 'SENSITIVITY':
        fails.append(f'{mid}: GRADE row for non-current or sensitivity model')
text = open(ROOT / 'FINAL_GRADE_RECOMMENDATIONS.md').read()
for mid in nonsens:
    o = outputs[mid]
    sec = re.search(r'## ' + re.escape(mid) + r'\n\n\*\*(.+?)\*\*; k=(\d+), N=(\d+)\.(.*?)(?=\n## |\Z)', text, re.S)
    if not sec:
        fails.append(f'{mid}: section missing'); continue
    if sec.group(1) != grade[mid]['certainty'] or int(sec.group(2)) != o['k'] or int(sec.group(3)) != o['N']:
        fails.append(f'{mid}: GRADE header disagrees with model outputs')
    if o['k']:
        want = f"{o['display_effect']:.3f} (95% CI {o['display_ci_low']:.3f} to {o['display_ci_high']:.3f})"
        if want not in sec.group(4):
            fails.append(f'{mid}: GRADE effect text does not match output {want}')
    if o['k'] == 1 and re.search(r'k\s*=?\s*[2-9]', grade[mid]['imprecision'] + grade[mid]['inconsistency']):
        fails.append(f'{mid}: single-study body described with k>1')
    for num in re.findall(r'(\d{2,5}) (?:analyzed )?participants', ' '.join(grade[mid].values())):
        if int(num) != o['N']:
            fails.append(f'{mid}: rationale cites {num} participants; model N={o["N"]}')
    if o['k'] and mid.startswith('opioid24') and 'crosses' in grade[mid]['imprecision']:
        lo, hi = o['display_ci_low'], o['display_ci_high']
        if not (lo < -10 < hi or lo < -8 < hi or lo < 0 < hi):
            fails.append(f'{mid}: imprecision says CI crosses a threshold but it does not')
record('grade_correspondence', fails, len(nonsens))

# 8. Participant accounting labels.
fails = []
ledger = load('FINAL_PARTICIPANT_LEDGER.csv')
if sum(int(r['counted_randomized_n']) for r in ledger if r['report_id'] == 'Yeh 2011') != 0:
    fails.append('Yeh 2011 counted separately')
for r in ledger:
    for k in ['itt_n', 'mitt_n', 'pp_n']:
        if r[k] and int(r[k]) > int(r['randomized_n']):
            fails.append(f"{r['report_id']}: {k} {r[k]} exceeds randomized {r['randomized_n']}")
record('participant_ledger', fails, len(ledger))

summary = dict(
    validator='10_FINAL_ADJUDICATION/code/validate_adjudication.py',
    python=sys.version.split()[0],
    counts=dict(reports=len(studies), trial_units=len({s['trial_id'] for s in studies}), canonical_results=len(results),
                models=len(spec), fitted_models=sum(1 for o in outputs.values() if o['k']), model_input_contrasts=len(inputs),
                graded_bodies=len(grade), rob_linked_results=sum(1 for l in link.values() if l['rob2_assessment_id']),
                randomized_counted_operational=sum(int(r['counted_randomized_n']) for r in ledger)),
    tolerances=dict(MD_RR='relative 1e-6 (tau2 +1e-6 absolute)', SMD='relative 5e-4 (large-sample J approximation)', inputs_MD_RR='relative 1e-9'),
    checks=checks, overall='PASS' if all(c['status'] == 'PASS' for c in checks.values()) else 'FAIL')
(D / '05_REPRODUCTION/validation_report.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False))
for name, c in checks.items():
    print(f"{c['status']:4} {name}: {c['n_checked']} checked, {c['n_failed']} failed")
    for x in c['failures'][:10]:
        print('     -', x)
print('OVERALL', summary['overall'], json.dumps(summary['counts']))
if summary['overall'] != 'PASS':
    raise SystemExit(1)
