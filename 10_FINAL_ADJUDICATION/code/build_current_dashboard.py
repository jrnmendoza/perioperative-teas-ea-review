"""Generate the v38 dashboard and audited downloads from canonical outputs.

Legacy assets and the full pre-edit dashboard baseline remain untouched. Only
explicitly selected descriptive metadata (not old effects/RoB) is reused.
"""
import csv,json,pathlib,shutil,html,hashlib
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
 # Distinct download name avoids collision with the v38 verification file.
 shutil.copyfile(D/'08_QOR_ANALYSIS/verification.json',OUT/'qor_verification.json')
 downloads.append(dict(label='QoR numerical and preservation checks',href='current/qor_verification.json',source='10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/verification.json',sha256=hashlib.sha256((OUT/'qor_verification.json').read_bytes()).hexdigest()))
for label,path in files:
 p=ROOT/path;target=OUT/p.name;shutil.copyfile(p,target);downloads.append(dict(label=label,href='current/'+p.name,source=path,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
oldtext=(DASH/'data.js').read_text();old=json.JSONDecoder().raw_decode(oldtext.split('window.STUDIES_DATA = ',1)[1])[0]
background={s['key']:{k:s.get(k) for k in ['citation','doi','country','country_evidence','surgery_procedure','stricta','population']} for s in old}
data=dict(version='v38',date='2026-09-20',registration='CRD420261452908',models=js('10_FINAL_ADJUDICATION/04_MODELS/model_outputs.json'),specifications=js('10_FINAL_ADJUDICATION/02_DECISIONS/model_specifications.json'),inputs=rows('10_FINAL_ADJUDICATION/04_MODELS/model_inputs.csv'),grade=rows('10_FINAL_ADJUDICATION/03_CANONICAL/grade.csv'),rob=rows('10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv'),studies=js('10_FINAL_ADJUDICATION/03_CANONICAL/studies.json'),background=background,prisma=js('10_FINAL_ADJUDICATION/02_DECISIONS/v38/prisma_counts.json'),policies=js('10_FINAL_ADJUDICATION/02_DECISIONS/v38/methodological_decisions.json'),downloads=downloads)
if coverage_path.exists():data['outcome_coverage']=json.loads(coverage_path.read_text())
if qor_path.exists():
 data['qor_analysis']=json.loads(qor_path.read_text())
 if (D/'08_QOR_ANALYSIS/qor_models_later.json').exists():
  data['qor_later_models']=json.loads((D/'08_QOR_ANALYSIS/qor_models_later.json').read_text())

e2_path=D/'09_E2_ANALYSIS/e2_model_outputs.json'
if e2_path.exists():
 data['e2_analysis']=json.loads(e2_path.read_text())
 files.append(('E2 sensitivity estimates','10_FINAL_ADJUDICATION/09_E2_ANALYSIS/e2_model_outputs.csv'))
 files.append(('E2 sensitivity report','10_FINAL_ADJUDICATION/09_E2_ANALYSIS/E2_RESULTS.md'))
 files.append(('E2 amended estimand decision','10_FINAL_ADJUDICATION/02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md'))
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
nav=''.join(f'<button type="button" role="tab" data-view="{key}" aria-controls="content" aria-selected="{str(key=="overview").lower()}" class="{"active" if key=="overview" else ""}">{label}</button>' for key,label in [('overview','Overview'),('results','Results'),('qor','QoR analysis'),('coverage','Outcome coverage'),('studies','Studies & figures'),('risk','Risk of bias'),('evidence','GRADE'),('prisma','PRISMA'),('methods','Methods'),('downloads','Downloads')])
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Perioperative TEAS &amp; EA — Evidence Review v38</title><link rel="stylesheet" href="current_review.css"></head>
<body><a class="skip" href="#content">Skip to evidence</a><div class="shell"><header><span class="eyebrow">Systematic review · Adjudication v38</span><h1>Perioperative electrical acupoint stimulation for postoperative opioid sparing</h1><p class="lede">TEAS and needle EA assessed separately · <a href="https://www.crd.york.ac.uk/PROSPERO/view/CRD420261452908" target="_blank" rel="noopener">PROSPERO CRD420261452908</a></p><nav class="nav" role="tablist" aria-label="Review sections">{nav}</nav></header><main id="content" tabindex="-1" style="padding-top:32px">{static}<noscript><p>JavaScript enables model selection, detailed bias assessments and article figures. <a href="current/FINAL_CURRENT_STATE_REPORT.md">Download the current-state report</a>.</p></noscript></main><footer>v38 · 20 September 2026 · Local analytical release. Posthoc AI-assisted adjudication, with source and selection limitations disclosed. Review displays currently in English. Historical interface and user changes preserved in the project’s v38 baseline.</footer></div><dialog id="figure-dialog"><button type="button" id="close-figure" aria-label="Close article figure">Close</button><p id="figure-caption"></p><img id="figure-image" alt=""></dialog><script src="current_review.js"></script><script src="article_figures.js"></script><script src="search_strategies.js"></script><script src="current_review_ui.js"></script><!--BUILD_BADGE--></body></html>'''
(DASH/'index.html').write_text(page)
(OUT/'download_manifest.json').write_text(json.dumps(downloads,indent=2)+'\n')
print('Dashboard v38:',len(data['models']),'models;',len(downloads),'current downloads; article figures preserved')
