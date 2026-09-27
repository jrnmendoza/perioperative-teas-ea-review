"""Deterministic export of the canonical model inputs for the Stata analysis layer (13_STATA).

Flattens every model's contributing rows (core v38, E2, QoR ~24 h incl. diagnostics, QoR later
windows) into one long CSV with arm-level data, plus a model list. Stata computes effect sizes and
pools from these rows; the canonical yi/vi are carried only so Stata can check its own effect sizes
row by row. Canonical pooled estimates are deliberately NOT exported to Stata; they are compared
afterwards by compare_stata.py. No values are typed by hand.
"""
import csv, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'; OUT = D / '13_STATA/input'
rows = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
COLS = ['analysis_set', 'model_id', 'row', 'study', 'result_id', 'data_type', 'n_i', 'mean_i', 'sd_i', 'events_i', 'n_c', 'mean_c', 'sd_c', 'events_c', 'canonical_yi', 'canonical_vi']
MCOLS = ['analysis_set', 'model_id', 'role', 'measure', 'unit', 'k', 'label']

def arm(set_, mid, i, r, dtype):
    return dict(analysis_set=set_, model_id=mid, row=i + 1, study=r['study'], result_id=r['result_id'], data_type=dtype,
                n_i=r.get('n_i', ''), mean_i=r.get('mean_i', ''), sd_i=r.get('sd_i', ''), events_i=r.get('events_i', ''),
                n_c=r.get('n_c', ''), mean_c=r.get('mean_c', ''), sd_c=r.get('sd_c', ''), events_c=r.get('events_c', ''),
                canonical_yi=r['yi'], canonical_vi=r['vi'])

inputs, models = [], []
# Core v38: model list and measures from model_outputs.csv; rows from model_inputs.csv (arm means are post-conversion).
core_in = rows(D / '04_MODELS/model_inputs.csv')
for m in rows(D / '04_MODELS/model_outputs.csv'):
    models.append(dict(analysis_set='core', model_id=m['model_id'], role=m['role'], measure=m['measure'], unit=m['unit'], k=m['k'], label=m['model_id']))
    for i, r in enumerate(x for x in core_in if x['model_id'] == m['model_id']):
        inputs.append(arm('core', m['model_id'], i, r, r['data_type']))
# E2: rows as analysed (after conversion factor and arm combination), exported by run_e2.py.
e2_in = rows(D / '09_E2_ANALYSIS/e2_model_inputs.csv')
for m in json.load(open(D / '09_E2_ANALYSIS/e2_model_outputs.json'))['models']:
    models.append(dict(analysis_set='E2', model_id=m['model_id'], role=m['role'], measure='MD', unit='mg IVMME', k=m['k'], label=m.get('note') or m['model_id']))
    for i, r in enumerate(x for x in e2_in if x['model_id'] == m['model_id']):
        inputs.append(arm('E2', m['model_id'], i, r, 'Mean/SD'))
# QoR ~24 h (main models and diagnostics) and later windows: inputs are embedded in the canonical JSON.
q = json.load(open(D / '08_QOR_ANALYSIS/qor_summary.json'))
for set_, ms in [('QoR 24h', q['main_models'] + q['diagnostics']), ('QoR later', json.load(open(D / '08_QOR_ANALYSIS/qor_models_later.json')))]:
    for m in ms:
        models.append(dict(analysis_set=set_, model_id=m['model_id'], role=m['role'], measure=m['measure'], unit=m['unit'], k=m['k'], label=m['label']))
        for i, r in enumerate(m['inputs']):
            inputs.append(arm(set_, m['model_id'], i, r, 'Mean/SD'))

# Figure specifications, derived from the canonical model list by fixed rules (no hand-typed values).
OUTCOME = {'systemic_opioid_0_24h': 'Cumulative 0-24 h systemic opioid consumption', 'composite_PONV_0_24h': 'Postoperative nausea and vomiting within 24 h',
           'nausea_0_24h': 'Nausea within 24 h', 'vomiting_0_24h': 'Vomiting within 24 h', 'pain_rest_approximately24h': 'Pain at rest at about 24 h',
           'time_first_flatus': 'Time to first flatus', 'time_first_bowel_sounds': 'Time to first bowel sounds', 'time_first_defecation': 'Time to first defecation',
           'intraop_remifentanil': 'Intraoperative remifentanil consumption'}
SECONDARY = set(OUTCOME) - {'systemic_opioid_0_24h'}
COMP = {'sham': 'sham', 'usual_care': 'usual care', 'active_electrical': 'active electrical control'}
UNIT = {'mg IVMME': 'mg IV MME', '0-10 points': 'points (0-10)', '0–10 points': 'points (0-10)'}
core_out = {m['model_id']: m for m in rows(D / '04_MODELS/model_outputs.csv')}
def xtitle(measure, unit, higher_better=False, mod='TEAS/EA'):
    if measure == 'RR': return f'Risk ratio (log scale); below 1 favours {mod}'
    return f"Mean difference, {UNIT.get(unit, unit)}; {'positive' if higher_better else 'negative'} favours {mod}"
specs = []
def spec(fid, kind, set_, mid, title, sub, xt, eform, thr, use, note=''):
    specs.append(dict(figure_id=fid, kind=kind, analysis_set=set_, model_id=mid, title=title, subtitle=sub, xtitle=xt, eform=eform, threshold=thr, use=use, note=note))
for body in ['TEAS_sham', 'TEAS_usual', 'EA_sham', 'EA_usual']:
    m = core_out['opioid24_' + body]; mod, cmp = body.split('_')
    if int(m['k']): spec(f'fig_e1_opioid24_{body.lower()}', 'forest', 'core', m['model_id'], f"E1 (registered primary): {mod} versus {COMP[m['comparator']]}",
                         OUTCOME[m['construct']], xtitle('MD', m['unit'], mod=mod), 0, -10, 'manuscript candidate')
    e = 'E2_opioid24_' + body
    spec(f'fig_e2_opioid24_{body.lower()}', 'forest', 'E2', e, f"E2 post-hoc sensitivity synthesis: {mod} versus {COMP[m['comparator']]}",
         'Not graded; E1 remains the registered primary analysis', xtitle('MD', 'mg IVMME', mod=mod), 0, -10, 'supplement candidate')
for m in core_out.values():
    if m['role'] == 'ADDITIONAL' and int(m['k']) >= 2 and m['construct'] in SECONDARY:
        spec(f"fig_sec_{m['model_id'].lower()}", 'forest', 'core', m['model_id'], f"{OUTCOME[m['construct']]}: {m['modality']} versus {COMP[m['comparator']]}",
             'Secondary outcome', xtitle(m['measure'], m['unit'], mod=m['modality']), int(m['measure'] == 'RR'), '', 'supplement candidate')
for m in json.load(open(D / '08_QOR_ANALYSIS/qor_summary.json'))['main_models']:
    spec(f"fig_qor_{m['model_id'].lower()}", 'forest', 'QoR 24h', m['model_id'], m['label'].replace('~', 'about '), 'Quality of recovery at about 24 h',
         xtitle('MD', m['unit'], higher_better=True, mod='TEAS'), 0, '', 'supplement candidate')
# Influence and small-study diagnostics only where k is large enough to be informative.
spec('fig_loo_ponv24_teas_sham', 'loo', 'core', 'ponv24_TEAS_sham', 'Leave-one-out: PONV within 24 h, TEAS versus sham', 'Influence diagnostic, not a new evidence body', xtitle('RR', ''), 1, '', 'supplement candidate')
spec('fig_loo_flatus_teas_sham', 'loo', 'core', 'flatus_TEAS_sham', 'Leave-one-out: time to first flatus, TEAS versus sham', 'Influence diagnostic, not a new evidence body', xtitle('MD', 'hours', mod='TEAS'), 0, '', 'supplement candidate')
spec('fig_loo_e2_opioid24_teas_sham', 'loo', 'E2', 'E2_opioid24_TEAS_sham', 'Leave-one-out: E2 TEAS versus sham (post-hoc)', 'Matches the canonical E2 leave-one-out models', xtitle('MD', 'mg IVMME', mod='TEAS'), 0, -10, 'supplement candidate')
spec('fig_funnel_ponv24_teas_sham', 'funnel', 'core', 'ponv24_TEAS_sham', 'Contour-enhanced funnel plot: PONV within 24 h, TEAS versus sham',
     'Exploratory; k = 10 is the conventional minimum; not used to change GRADE', 'Log risk ratio', 1, '', 'supplement candidate',
     'Only body with k >= 10; all other bodies: not evaluated because the number of studies is insufficient for a meaningful small-study-effect assessment.')
OUT.mkdir(parents=True, exist_ok=True)
for name, cols, data in [('stata_model_inputs.csv', COLS, inputs), ('stata_models.csv', MCOLS, models), ('figure_specs.csv', list(specs[0]), specs)]:
    with open(OUT / name, 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(data)
sources = ['04_MODELS/model_inputs.csv', '04_MODELS/model_outputs.csv', '09_E2_ANALYSIS/e2_model_inputs.csv', '09_E2_ANALYSIS/e2_model_outputs.json',
           '08_QOR_ANALYSIS/qor_summary.json', '08_QOR_ANALYSIS/qor_models_later.json']
with open(OUT / 'input_sources.sha256', 'w') as fh:
    for s in sources + ['13_STATA/input/stata_model_inputs.csv', '13_STATA/input/stata_models.csv', '13_STATA/input/figure_specs.csv']:
        fh.write(f"{hashlib.sha256((D / s).read_bytes()).hexdigest()}  10_FINAL_ADJUDICATION/{s}\n")
print(f"{len(models)} models, {len(inputs)} input rows ->", OUT.relative_to(ROOT))
