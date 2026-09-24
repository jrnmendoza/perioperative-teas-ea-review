"""Generate the v38 dashboard and audited downloads from canonical outputs.

Legacy assets and the full pre-edit dashboard baseline remain untouched. Only
explicitly selected descriptive metadata (not old effects/RoB) is reused.
"""
import csv,json,pathlib,shutil,html,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION';DASH=ROOT/'dashboard';OUT=DASH/'current';OUT.mkdir(exist_ok=True)
def rows(p):return list(csv.DictReader(open(ROOT/p,encoding='utf-8-sig')))
def js(p):return json.load(open(ROOT/p))
files=[
('Late duplicate record mappings','10_FINAL_ADJUDICATION/02_DECISIONS/v38/late_duplicate_register.csv'),
('Current-state report','FINAL_CURRENT_STATE_REPORT.md'),('GRADE: all 38 reviewed bodies','FINAL_GRADE_RECOMMENDATIONS.md'),
('GRADE table','10_FINAL_ADJUDICATION/03_CANONICAL/grade.csv'),('94 result-specific RoB assessments','10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv'),
('RoB source-text locators','10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_source_locators.csv'),('PRISMA 225-record ledger','10_FINAL_ADJUDICATION/02_DECISIONS/v38/prisma_record_ledger.csv'),
('PRISMA counts and provenance','10_FINAL_ADJUDICATION/02_DECISIONS/v38/prisma_counts.json'),('PRISMA accounting report','10_FINAL_ADJUDICATION/06_REPORTS/PRISMA_REPORT_TRIAL_ACCOUNTING.md'),
('Adopted methodological decisions','10_FINAL_ADJUDICATION/02_DECISIONS/v38/METHODOLOGICAL_DECISIONS.md'),('Primary evidence table','10_FINAL_ADJUDICATION/06_REPORTS/primary_evidence_table.csv'),
('All model estimates','10_FINAL_ADJUDICATION/04_MODELS/model_outputs.csv'),('All model inputs','10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv'),('Exact result membership','FINAL_MODEL_MEMBERSHIP_MATRIX.csv'),
('All 761 canonical results','10_FINAL_ADJUDICATION/03_CANONICAL/results.csv'),('Participant accounting','FINAL_PARTICIPANT_LEDGER.csv'),('Exact-result RoB linkage','FINAL_RESULT_ROB2_LINKAGE.csv'),
('v37 → v38 changes','10_FINAL_ADJUDICATION/06_REPORTS/model_comparison_v38.csv'),('Nine GRADE category changes','10_FINAL_ADJUDICATION/02_DECISIONS/v38/grade_changes.csv'),
('Independent validation','10_FINAL_ADJUDICATION/05_REPRODUCTION/validation_report.json'),('739-field R cross-check','10_FINAL_ADJUDICATION/05_REPRODUCTION/metafor_comparison.csv')]
if (D/'05_REPRODUCTION/v38/verification.json').exists():files.append(('v38 verification summary','10_FINAL_ADJUDICATION/05_REPRODUCTION/v38/verification.json'))
if (D/'02_DECISIONS/v38/rob2_signalling_questions.csv').exists():files.append(('RoB signalling-question record','10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_signalling_questions.csv'))
coverage_path=D/'07_OUTCOME_COVERAGE/coverage_summary.json'
if coverage_path.exists():
 for label,name in [('Harms and PROM coverage report','OUTCOME_COVERAGE_REPORT.md'),('All 70 report coverage checks','report_coverage.csv'),('Recovery and satisfaction source evidence','recovery_evidence.csv'),('Safety source evidence','safety_evidence.csv')]:
  files.append((label,'10_FINAL_ADJUDICATION/07_OUTCOME_COVERAGE/'+name))
downloads=[]
qor_path=D/'08_QOR_ANALYSIS/qor_summary.json'
if qor_path.exists():
 for label,name in [('QoR synthesis and certainty report','QOR_ANALYSIS_REPORT.md'),('QoR exact arm inputs','qor_inputs.csv'),('QoR main and diagnostic estimates','qor_models.csv'),('QoR eight result-specific RoB assessments','qor_rob2.csv'),('QoR 176 signalling responses','qor_rob2_signals.csv'),('QoR domain source locators','qor_source_locators.csv'),('QoR three GRADE bodies','qor_grade.csv'),('QoR independent R comparison','qor_metafor_comparison.csv')]:
  files.append((label,'10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/'+name))
 for name in ['QOR40_SHAM_24H','QOR40_USUAL_24H','QOR15_SHAM_24H']:
  files.append(('QoR forest: '+name,'10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/'+name+'.svg'))
 if (D/'08_QOR_ANALYSIS/qor_models_later.csv').exists():
  files.append(('QoR later-window models','10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_models_later.csv'))
  files.append(('QoR later-window exact arm inputs', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_inputs_later.csv'))
  files.append(('QoR later-window RoB', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_rob2_later.csv'))
  files.append(('QoR later-window RoB signals', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_rob2_signals_later.csv'))
  files.append(('QoR later-window source locators', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_source_locators_later.csv'))
  files.append(('QoR later-window R script', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/forest_qor_later.R'))
  files.append(('QoR later-window R log', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/forest_qor_later_run.txt'))
  files.append(('QoR later-window metafor estimates', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/metafor_estimates.csv'))
  files.append(('QoR later-window metafor comparison', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/metafor_comparison_later.csv'))
  import shutil
  shutil.copyfile(D/'08_QOR_ANALYSIS/metafor_forest_later/R_session_forest_later.txt', OUT/'R_session_forest_later.txt')
  files.append(('QoR later-window R session info', '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/R_session_forest_later.txt'))
  import json
  qor_later_models = json.loads((D/'08_QOR_ANALYSIS/qor_models_later.json').read_text())
  for m in qor_later_models:
      files.append(('QoR later-window forest: ' + m['model_id'], '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/metafor_forest_later/forest_' + m['model_id'] + '.svg'))
 # Distinct download name avoids collision with the v38 verification file.
 shutil.copyfile(D/'08_QOR_ANALYSIS/verification.json',OUT/'qor_verification.json')
 downloads.append(dict(label='QoR numerical and preservation checks',href='current/qor_verification.json',source='10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/verification.json',sha256=hashlib.sha256((OUT/'qor_verification.json').read_bytes()).hexdigest()))
e2_path=D/'09_E2_ANALYSIS/e2_model_outputs.json'
if e2_path.exists():
 files.append(('E2 sensitivity estimates','10_FINAL_ADJUDICATION/09_E2_ANALYSIS/e2_model_outputs.csv'))
 files.append(('E2 sensitivity report','10_FINAL_ADJUDICATION/09_E2_ANALYSIS/E2_RESULTS.md'))
 files.append(('E2 amended estimand decision','10_FINAL_ADJUDICATION/02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md'))
files.append(('Additional file 12: trial-by-trial accounting for the primary opioid outcome','manuscript/ADDITIONAL_FILE_12.md'))
files.append(('Additional file 12 A1 primary construct','manuscript/additional_files/additional_file_12_A1_primary_construct.csv'))
files.append(('Additional file 12 A2 other windows','manuscript/additional_files/additional_file_12_A2_other_windows.csv'))
files.append(('Additional file 12 tierB no candidate result','manuscript/additional_files/additional_file_12_tierB_no_candidate_result.csv'))
filenames=set()
for label,path in files:
 if pathlib.Path(path).name in filenames: raise ValueError('Filename collision: ' + pathlib.Path(path).name)
 filenames.add(pathlib.Path(path).name)
 p=ROOT/path;target=OUT/p.name;shutil.copyfile(p,target);downloads.append(dict(label=label,href='current/'+p.name,source=path,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
oldtext=(DASH/'data.js').read_text();old=json.JSONDecoder().raw_decode(oldtext.split('window.STUDIES_DATA = ',1)[1])[0]
background={s['key']:{k:s.get(k) for k in ['citation','doi','country','country_evidence','surgery_procedure','stricta','population']} for s in old}
data=dict(version='v38',date='2026-09-20',registration='CRD420261452908',models=js('10_FINAL_ADJUDICATION/04_MODELS/model_outputs.json'),specifications=js('10_FINAL_ADJUDICATION/02_DECISIONS/model_specifications.json'),inputs=rows('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv'),grade=rows('10_FINAL_ADJUDICATION/03_CANONICAL/grade.csv'),rob=rows('10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv'),studies=js('10_FINAL_ADJUDICATION/03_CANONICAL/studies.json'),background=background,prisma=js('10_FINAL_ADJUDICATION/02_DECISIONS/v38/prisma_counts.json'),policies=js('10_FINAL_ADJUDICATION/02_DECISIONS/v38/methodological_decisions.json'),downloads=downloads)
if coverage_path.exists():data['outcome_coverage']=json.loads(coverage_path.read_text())
if qor_path.exists():
 data['qor_analysis']=json.loads(qor_path.read_text())
 if (D/'08_QOR_ANALYSIS/qor_models_later.json').exists():
  data['qor_later_models']=json.loads((D/'08_QOR_ANALYSIS/qor_models_later.json').read_text())
  data['qor_later_rob'] = rows('10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_rob2_later.csv')
  data['qor_later_metafor_manifest'] = json.loads((D/'08_QOR_ANALYSIS/metafor_forest_later/manifest.json').read_text())

e2_path=D/'09_E2_ANALYSIS/e2_model_outputs.json'
if e2_path.exists():
 data['e2_analysis']=json.loads(e2_path.read_text())

report_text = (ROOT/'FINAL_CURRENT_STATE_REPORT.md').read_text(encoding='utf-8')
section_match = re.search(r'\*\*Not completed — outstanding\*\*(.*?)(?=\n\*\*|\n## |\Z)', report_text, re.DOTALL)
if not section_match or not section_match.group(1).strip(): raise ValueError("Not completed — outstanding section missing or empty")
outstanding_items = re.findall(r'- \*\*(.*?)\*\*', section_match.group(1))
if not outstanding_items: raise ValueError("No outstanding items found")
data['outstanding'] = outstanding_items

e2_methods_text = (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')
e2_methods_data = {}
m = re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', e2_methods_text)
if not m: raise ValueError("Timestamp note not found")
e2_methods_data['Timestamp note'] = m.group(1).strip()
def get_sec(txt, h, st=None):
    pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n#|\Z)'
    if st: pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n' + re.escape(st) + r'|\n#|\Z)'
    m2 = re.search(pat, txt, re.DOTALL)
    if not m2: raise ValueError(f"Heading not found: {h}")
    return m2.group(1).strip()
e2_methods_data['Why this document exists, stated plainly'] = get_sec(e2_methods_text, 'Why this document exists, stated plainly')
e2_methods_data['E1 — registered primary (retained, reported in full)'] = get_sec(e2_methods_text, 'E1 — registered primary (retained, reported in full)')
e2_methods_data['E2 — amended primary (post hoc)'] = get_sec(e2_methods_text, 'E2 — amended primary (post hoc)', st='### Admission rules')
e2_methods_data['Prespecified sensitivity analyses for E2'] = get_sec(e2_methods_text, 'Prespecified sensitivity analyses for E2')
e2_methods_data['Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)'] = get_sec(e2_methods_text, 'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)')
e2_methods_data['Decision after the E2 run — 23 September 2026: E1 retained as primary'] = get_sec(e2_methods_text, 'Decision after the E2 run — 23 September 2026: E1 retained as primary')
data['e2_methods'] = e2_methods_data

data['e2_methods_html'] = {}
for h, text in e2_methods_data.items():
    html_blocks = []
    blocks = re.split(r'\n\n+', text.strip())
    for block in blocks:
        if block == "---":
            continue
        lines = block.split('\n')
        
        # Check if it is a list block
        is_ul = lines[0].startswith('- ')
        is_ol = re.match(r'^\d+\.\s', lines[0]) is not None
        if is_ul or is_ol:
            tag = 'ul' if is_ul else 'ol'
            items = []
            cur_item = []
            for line in lines:
                if line.startswith('- ') or re.match(r'^\d+\.\s', line):
                    if cur_item:
                        items.append(' '.join(cur_item))
                    # Remove bullet/number prefix
                    cur_item = [re.sub(r'^-\s+|^\d+\.\s+', '', line)]
                elif line.strip():
                    cur_item.append(line.strip())
            if cur_item:
                items.append(' '.join(cur_item))
            
            lis = []
            for item in items:
                esc_item = html.escape(item)
                esc_item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', esc_item)
                esc_item = re.sub(r'`(.*?)`', r'<code>\1</code>', esc_item)
                lis.append(f"<li>{esc_item}</li>")
            html_blocks.append(f"<{tag}>{''.join(lis)}</{tag}>")
            
        elif lines[0].startswith('> '):
            text_content = ' '.join([line[2:] if line.startswith('> ') else line.strip() for line in lines])
            esc_item = html.escape(text_content)
            esc_item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', esc_item)
            esc_item = re.sub(r'`(.*?)`', r'<code>\1</code>', esc_item)
            html_blocks.append(f"<blockquote>{esc_item}</blockquote>")
            
        else:
            text_content = ' '.join([line.strip() for line in lines if line.strip()])
            esc_item = html.escape(text_content)
            esc_item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', esc_item)
            esc_item = re.sub(r'`(.*?)`', r'<code>\1</code>', esc_item)
            html_blocks.append(f"<p>{esc_item}</p>")
            
    data['e2_methods_html'][h] = ''.join(html_blocks)


data['e2_labels']={
  'E2_TEAS_sham_LOO_Gu_2019': 'Leave out Gu 2019 (figure–text contradiction)',
  'E2_TEAS_sham_LOO_Lee_2011': 'Leave out Lee 2011 (Table 8 contradiction)',
  'E2_TEAS_sham_LOO_He_2026': 'Without unstated-route equivalents (He 2026)',
  'E2_TEAS_sham_excl_unquantified_rescue': 'Without known unquantified rescue (Chen 1998, Lee 2011)',
  'E2_TEAS_sham_excl_E2.1': 'Without E2.1 admissions (Zhang 2025, Gu 2019)',
  'E2_EA_usual_LOO_El-Rakshy': 'Leave out El-Rakshy 2009',
  'E2_TEAS_sham_LOO_Szmit_2021': 'without Szmit 2021',
  'E2_TEAS_sham_LOO_Chen_1998': 'without Chen 1998',
  'E2_TEAS_sham_LOO_Chen_2020': 'without Chen 2020',
  'E2_TEAS_sham_LOO_Zhang_2025': 'without Zhang 2025',
  'E2_EA_usual_LOO_Seevaunnamtum': 'without Seevaunnamtum 2016',
  'E2_EA_usual_LOO_Yang': 'without Yang 2024',
  'E2_EA_usual_LOO_Lin': 'without Lin 2002',
  'E2_TEAS_sham_suf0.25': 'Sufentanil 0.25 mg/µg',
  'E2_TEAS_sham_suf1.0': 'Sufentanil 1.0 mg/µg (main analysis uses 0.5 mg/µg)',
  'E2_EA_usual_excl_unquantified_rescue': 'Without known unquantified rescue (= E1 body)',
  'E2_TEAS_sham_E1_restriction': 'Restricted to E1-eligible (= registered primary)'
 }
if 'e2_analysis' in data:
 e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}
 for k in data['e2_labels'].keys():
  assert k in e2_ids, f"Label key not found in E2 model outputs: {k}"

 if 'e2_analysis' in data:
  data['e2_joint'] = []
  for b in ['TEAS vs sham', 'TEAS vs usual care', 'EA vs sham', 'EA vs usual care']:
   # Look up the E2 main model by body; a missing or duplicate body is an error,
   # never a silent "Not met".
   hits = [x for x in data['e2_analysis']['models'] if x['body'] == b and x['role'] == 'E2 POST-HOC SENSITIVITY (main)']
   assert len(hits) == 1, f"Expected one E2 main model for {b!r}, found {len(hits)}"
   m = hits[0]

   if m['ci_high'] < -10:
    op_limb = f"Met ({m['effect']:.2f})"
   elif m['effect'] <= -10:
    op_limb = f"Met by point estimate ({m['effect']:.2f}), k={m['k']}"
   else:
    op_limb = "Not met"
    
   if m['effect'] > -10:
    pain_limb = "—"
    joint_crit = "Not met"
   else:
    if b == 'EA vs sham':
     pain_limb = "Cannot be evaluated: Lin 2002 reports pain only in a figure (Fig. 1) and has no eligible ~24-h pain result; pain from other trials cannot supply the pairing."
     joint_crit = "Cannot be evaluated"
    else:
     # No recorded pain-limb disposition exists for any other body (E2_RESULTS.md).
     raise AssertionError(f"{b}: opioid limb reaches 10 mg but no pain-limb disposition is recorded")

   data['e2_joint'].append({'body': b, 'opioid_limb': op_limb, 'pain_limb': pain_limb, 'joint_criterion': joint_crit})
(DASH/'current_review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
(DASH/'current_review.js').write_text('/* Generated from canonical v38 data; do not edit. */\nwindow.CURRENT_REVIEW = '+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n')
e=html.escape
static='<h2>Current primary evidence — v38</h2><p>70 reports / 69 operational trial families. 94 result-specific RoB assessments; all 38 GRADE bodies reviewed under user delegation. New judgments AI-conducted; prior human completion user-reported.</p><div class="table-scroll"><table><thead><tr><th>Body</th><th>k / N</th><th>MD mg IV MME [95% CI]</th></tr></thead><tbody>'
for m in data['models']:
 if m['role'] not in ('PRINCIPAL','SUPPORTIVE'):continue
 value=f"{m['display_effect']:.2f} [{m['display_ci_low']:.2f}, {m['display_ci_high']:.2f}]" if m['k'] else 'No eligible data'
 static+=f'<tr><td>{e(m["model_id"])}</td><td>{m["k"]} / {m["N"]}</td><td>{value}</td></tr>'
static+='</tbody></table></div><p>No body establishes the registered ≥10mg sparing plus paired ~24h pain upper CI &lt;+1 criterion. The 12-reference historical import gap and exclusion-completeness limitation remain disclosed. See downloads for details.</p>'
if qor_path.exists():static+='<p>QoR addendum: three approximately-24-hour syntheses, eight new result-specific assessments and three Very-low-certainty judgments. All pooled confidence intervals include zero. See the QoR analysis tab. Four later-window QoR models (POD2/3) are also available.</p>'
if 'e2_joint' in data:
 ea_joint = next((x['joint_criterion'] for x in data['e2_joint'] if x['body'] == 'EA vs sham'), 'Not met')
 ea_text = 'cannot be evaluated because its pain limb cannot be evaluated' if 'Cannot be evaluated' in ea_joint else 'is ' + ea_joint.lower()
 any_met = any('Met' in x['joint_criterion'] and 'Not met' not in x['joint_criterion'] for x in data['e2_joint'])
 met_text = 'in at least one body' if any_met else 'in no body'
 static += f'<p>E2 post-hoc sensitivity analysis: E1 kept as primary, not graded. The joint criterion is met {met_text} (for EA vs sham it {ea_text}).</p>'
nav=''.join(f'<button type="button" role="tab" data-view="{key}" aria-controls="content" aria-selected="{str(key=="overview").lower()}" class="{"active" if key=="overview" else ""}">{label}</button>' for key,label in [('overview','Overview'),('results','Results'),('qor','QoR analysis'),('coverage','Outcome coverage'),('studies','Studies & figures'),('risk','Risk of bias'),('evidence','GRADE'),('prisma','PRISMA'),('methods','Methods'),('downloads','Downloads')])
build_date = ""
meta_path = DASH / 'build-meta.json'
if meta_path.exists():
    meta = json.loads(meta_path.read_text())
    if 'build_date' in meta:
        build_date = f" · Build {meta['build_date']}"

page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Perioperative TEAS &amp; EA — Evidence Review v38</title><link rel="stylesheet" href="current_review.css"></head>
<body><a class="skip" href="#content">Skip to evidence</a><div class="shell"><header><span class="eyebrow">Systematic review · Adjudication v38</span><h1>Perioperative electrical acupoint stimulation for postoperative opioid sparing</h1><p class="lede">TEAS and needle EA assessed separately · <a href="https://www.crd.york.ac.uk/PROSPERO/view/CRD420261452908" target="_blank" rel="noopener">PROSPERO CRD420261452908</a></p><nav class="nav" role="tablist" aria-label="Review sections">{nav}</nav></header><main id="content" tabindex="-1" style="padding-top:32px">{static}<noscript><p>JavaScript enables model selection, detailed bias assessments and article figures. <a href="current/FINAL_CURRENT_STATE_REPORT.md">Download the current-state report</a>.</p></noscript></main><footer>v38 core · 20 September 2026 · E2 sensitivity analysis · 23 September 2026{build_date} · Public analytical release (not data-locked). Post-hoc AI-assisted adjudication, with source and selection limitations disclosed. Review displays currently in English. Historical interface and user changes preserved in the project’s v38 baseline.</footer></div><dialog id="figure-dialog"><button type="button" id="close-figure" aria-label="Close article figure">Close</button><p id="figure-caption"></p><img id="figure-image" alt=""></dialog><script src="current_review.js"></script><script src="article_figures.js"></script><script src="search_strategies.js"></script><script src="current_review_ui.js"></script><!--BUILD_BADGE--></body></html>'''
(DASH/'index.html').write_text(page)
(OUT/'download_manifest.json').write_text(json.dumps(downloads,indent=2)+'\n')
print('Dashboard v38:',len(data['models']),'models;',len(downloads),'current downloads; article figures preserved')
