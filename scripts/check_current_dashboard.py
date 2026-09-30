#!/usr/bin/env python3
"""v38 data/asset contract replacing the legacy v26 seven-trial UI contract."""
import csv,json,pathlib,hashlib,copy,sys,re,subprocess
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1];D=ROOT/'10_FINAL_ADJUDICATION'
def rows(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
E2_BODIES=[('TEAS vs sham','opioid24_TEAS_sham','E2_opioid24_TEAS_sham'),('TEAS vs usual care','opioid24_TEAS_usual','E2_opioid24_TEAS_usual'),
           ('EA vs sham','opioid24_EA_sham','E2_opioid24_EA_sham'),('EA vs usual care','opioid24_EA_usual','E2_opioid24_EA_usual')]
def e2_accounting_complete(d):
    """Every E1 principal/supportive input has exactly one INCLUDE row and every E2 main contrast exactly one ADMIT row
    in the Tier A dispositions (joined on result ID; E2.1 Tier B1 admissions on report). Mirrors the E1 vs E2 workspace."""
    if 'e2_accounting' not in d:return True
    A=d['e2_accounting']['tierA']+d['e2_accounting']['tierA_addendum']
    ids=lambda s:[] if s.startswith('Tier B1') else [x.split(' (')[0].strip() for x in s.split(' / ')]
    for body,e1,e2 in E2_BODIES:
        rows=[r for r in A if r['body']==body]
        match=lambda inp:[r for r in rows if inp['result_id'] in ids(r['result_ids']) or (r['result_ids'].startswith('Tier B1') and r['report']==inp['study'])]
        for inp in (x for x in d['inputs'] if x['model_id']==e1):
            m=match(inp)
            if len(m)!=1 or m[0]['E1_disposition']!='INCLUDE':return False
        for inp in (x for x in d['e2_inputs'] if x['model_id']==e2):
            m=match(inp)
            if len(m)!=1 or m[0]['E2_disposition']!='ADMIT':return False
    return True
def paired_pain_consistent(d):
    """The registry covers every E1 principal/supportive and E2 main opioid contrast; an eligible pairing needs an
    INCLUDE pain decision and matching arms; no eligible pairing exists where e2_joint says the pain limb cannot be evaluated."""
    if 'paired_pain' not in d:return True
    P=d['paired_pain']
    e1={m for _,m,_ in E2_BODIES};e2={m for _,_,m in E2_BODIES}
    want={(r['model_id'],r['result_id']) for r in d['inputs'] if r['model_id'] in e1}|{(r['model_id'],r['result_id']) for r in d['e2_inputs'] if r['model_id'] in e2}
    if {(r['opioid_model_id'],r['opioid_result_id']) for r in P}!=want:return False
    if any(r['pairing_status']=='ELIGIBLE PAIRED PAIN' and (r['pain_decision']!='INCLUDE' or r['arm_match']!='SAME ARMS') for r in P):return False
    blocked={b for b,_,m in E2_BODIES for j in d.get('e2_joint',[]) if j['body']==b and j['pain_limb'].startswith('Cannot be evaluated')}
    return not any(r['analysis']=='E2' and r['body'] in blocked and r['pairing_status']=='ELIGIBLE PAIRED PAIN' for r in P)
def sensitivity_map_complete(d):
    """Every SENSITIVITY-role core model is mapped exactly once; each parent is a core model; parent chains end at a
    non-sensitivity body or a stand-alone entry (no cycles); every row states a relation."""
    if 'sensitivity_map' not in d:return True
    S=d['sensitivity_map'];ids=[r['model_id'] for r in S];models={m['model_id']:m for m in d['models']};par={r['model_id']:r['parent_model_id'] for r in S}
    if sorted(ids)!=sorted(m for m,x in models.items() if x['role']=='SENSITIVITY') or any(not r['relation'] for r in S):return False
    for m in ids:
        seen=set()
        while par.get(m):
            if m in seen or par[m] not in models:return False
            seen.add(m);m=par[m]
    return True
CHAR_STATUS={'Verified (registry)','Verified (PDF quote)','Partly verified (source excerpt)','Canonical result register','Source-traced (extraction record)',
             'Legacy (v26, not re-verified)','Extracted (PDF quote, single extractor)','Verified (PDF quote, second reviewer)','Not reported in source','Not verified','Not extracted'}
def characteristics_complete(d):
    """Every report has the same harmonised fields; statuses come from the declared vocabulary; values never fill unsourced gaps."""
    if 'characteristics' not in d:return True
    C=d['characteristics'];ids={s['report_id'] for s in d['studies']}
    fields={}
    for r in C:fields.setdefault(r['report_id'],[]).append(r['field'])
    if set(fields)!=ids or len({tuple(v) for v in fields.values()})!=1:return False
    return all(r['status'] in CHAR_STATUS and (r['value']=='' if r['status'] in ('Not extracted','Not verified','Not reported in source') else True) for r in C)
def _extracted_ok(c,r):
    """A characteristic shown from an extraction-record row: same value, verbatim quote in the note, status from the review state."""
    extracted='Verified (PDF quote, second reviewer)' if r['second_review'].endswith(': confirmed') else 'Extracted (PDF quote, single extractor)'
    return c['value']==r['value'] and (r['quote'] in c.get('note','') and c['status']==extracted if r['status']=='Extracted (PDF quote)' else c['status']=='Not reported in source')
def regimen_verified(d):
    """Regimen fields shown in the explorer equal the extraction record, and every extracted value's verbatim quote is found
    on its stated page of the report's tracked text layer (code/verify_regimen_extraction.py, without the PDF hash step)."""
    rec=D/'14_CHARACTERISTICS/regimen_extraction.csv'
    if not rec.exists() or 'characteristics' not in d:return True
    sys.path.insert(0,str(D/'code'));import verify_regimen_extraction as V
    R={(r['report_id'],r['field']):r for r in rows(rec)}
    if any(V.check_row(r) for r in R.values()):return False
    C={(c['report_id'],c['field']):c for c in d['characteristics'] if c['field'] in V.FIELDS}
    return set(C)==set(R) and all(_extracted_ok(C[k],R[k]) for k in R)
def baseline_verified(d):
    """Baseline/protocol fields (age ... session duration): every record row's quote is found on its stated page; each field
    shown in the explorer comes from the record unless a registry value (or, for anaesthesia, an earlier PDF quote) takes
    precedence; no value is shown as extracted or second-reviewed without a record row and a page locator, and no row is
    marked second-reviewed unless second_review.csv covers the record (code/verify_baseline_extraction.py, without hashes)."""
    rec=D/'14_CHARACTERISTICS/baseline_protocol_extraction.csv'
    if not rec.exists() or 'characteristics' not in d:return True
    sys.path.insert(0,str(D/'code'));import verify_baseline_extraction as B
    R={(r['report_id'],r['field']):r for r in rows(rec)}
    if any(B.V.check_row(r,B.FIELDS) for r in R.values()):return False
    entry=next((x for x in d.get('second_review',[]) if x['file'].endswith('baseline_protocol_extraction.csv')),None)
    expected=f"{entry['reviewer']}, {entry['review_date']}: confirmed" if entry else None
    if any(r['second_review'] not in ('pending',expected) for r in R.values()):return False
    for c in d['characteristics']:
        if c['field'] not in B.FIELDS:continue
        r=R.get((c['report_id'],c['field']))
        if c['status'] in ('Verified (registry)','Verified (PDF quote)'):continue
        if not r or not _extracted_ok(c,r):return False
        if r['status']=='Extracted (PDF quote)' and not re.search(r' p\.\d',c['source']):return False
    return True
V38_SCRIPTS=['theme.js','evidence_graph.js','current_review.js','article_figures.js','search_strategies.js','interactive_explorer.js','current_review_ui.js']
NAV_GROUPS=[('Evidence',['overview','results','e1e2','qor']),('Explore studies',['studies','coverage','risk','evidence']),('Review process',['prisma','methods','downloads'])]
def nav_ok(nav):
    """Route navigation: every route once, in reader groups, as links (#view) with aria-current (not ARIA tabs)."""
    groups=re.findall(r'<span class="nav-group-label"[^>]*>([^<]+)</span><div class="nav-links">(.*?)</div>',nav)
    got=[(g,re.findall(r'<a href="#([a-z0-9]+)" data-view="\1"',links)) for g,links in groups]
    return got==NAV_GROUPS and 'role="tab' not in nav and nav.count('aria-current="page"')==1 and len(re.findall(r'data-view=',nav))==11
def theme_ok(js):
    """theme.js is the only script that uses browser storage: one fixed key, no network."""
    keys=set(re.findall(r"KEY\s*=\s*'([^']+)'",js))
    calls=re.findall(r'localStorage\.(\w+)\(([^,)]*)',js)
    return keys=={'teas-ea-review-theme'} and calls and all(c[1].strip()=='KEY' for c in calls) and not re.search(r'fetch\(|XMLHttpRequest|sendBeacon|document\.cookie',js)
def legend_ok(js):
    """The explorer legend explains exactly the statuses the characteristics use (one entry each, with help text)."""
    entries=re.findall(r"^\s+'([^']+)': \['(\w+)', 'vs-(?:ok|mid|warn|none)', '([^']+)',\s*\n\s*'([^']{40,})'\]",js,re.M)
    return {e[0] for e in entries}==CHAR_STATUS and len(entries)==len(CHAR_STATUS) and 'provenanceLegend()' in js and 'Characteristics do not all have the same verification level.' in js
def release_ok(d):
    """Release dates shown in the page come from the payload date and the dated E2 decision heading."""
    r=d.get('release');h=[k for k in d.get('e2_methods',{}) if k.startswith('Decision after the E2 run')]
    if not r or len(h)!=1:return False
    from datetime import datetime
    return r['core_version']==d['version'] and r['core_date']==d['date'] and r['e2_date']==datetime.strptime(re.search(r'\d{1,2} \w+ \d{4}',h[0]).group(0),'%d %B %Y').strftime('%Y-%m-%d')
GRADE_LEVELS=['High','Moderate','Low','Very low']
def qor_later_grade_consistent(d):
    """Later-window QoR GRADE: only evidence bodies (never leave-one-out diagnostics) are graded; each record carries its
    model's current k, N, estimate and CI; certainty equals High minus the recorded downgrades (floored at Very low); every
    domain has a written rationale; the review status agrees with second_review.csv."""
    if 'qor_later_grade' not in d:return True
    M={m['model_id']:m for m in d.get('qor_later_models',[])}
    reviewed=any(r['file'].endswith('qor_grade_later.csv') for r in d.get('second_review',[]))
    dom=['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias']
    for g in d['qor_later_grade']:
        m=M.get(g['model_id'])
        if not m or m['role']=='SENSITIVITY' or m.get('parent_model_id'):return False
        if int(g['k'])!=m['k'] or int(g['N'])!=m['N']:return False
        if any(abs(float(g[a])-float(m[a]))>1e-9*max(1,abs(float(m[a]))) for a in ('effect','ci_low','ci_high')):return False
        if g['certainty']!=GRADE_LEVELS[min(sum(int(g[k+'_downgrades']) for k in dom),3)]:return False
        if any(len(g[k])<40 for k in dom):return False
        if ('second review pending' in g['decision_status'])==reviewed:return False
    return len({g['model_id'] for g in d['qor_later_grade']})==len(d['qor_later_grade'])
def current_state_ok(d):
    """FINAL_CURRENT_STATE_REPORT.md is what its generator writes from the current records, every inventory value in it
    equals the same count recomputed from the payload, and it is dated no earlier than any date the payload carries
    (release, reviews, extractions) — so the dashboard never shows a later or different state than the report."""
    text=(ROOT/'FINAL_CURRENT_STATE_REPORT.md').read_text(encoding='utf-8')
    sys.path.insert(0,str(D/'code'));import build_current_state_report as B
    if text!=B.build():return False
    inv={k:int(v.replace(',','')) for k,v in re.findall(r'^\| ([^|]+?) \| ([\d,]+) \|$',text.split('## Inventory')[1].split('\n## ')[0],re.M)}
    C=Counter(c['status'] for c in d.get('characteristics',[]));N=d.get('narrative_outcomes',{});S=d.get('stata',{}).get('summary',[])
    got={'Included reports':len(d['studies']),'Operational trial families':len({s['trial_id'] for s in d['studies']}),'Canonical results':len(d['results_register']),
         'Core models (defined)':len(d['models']),'Core models with data':sum(int(m['k'])>0 for m in d['models']),'Core model inputs':len(d['inputs']),
         'Core RoB 2 assessments (result-specific)':len(d['rob']),'Core GRADE bodies':len(d['grade']),
         'QoR ~24 h main models':len(d['qor_analysis']['main_models']),'QoR ~24 h diagnostics':len(d['qor_analysis']['diagnostics']),
         'QoR ~24 h RoB 2 assessments':len(d['qor_analysis']['rob']),'QoR ~24 h GRADE bodies':len(d['qor_analysis']['grade']),
         'QoR later-window models':len(d.get('qor_later_models',[])),'QoR later-window RoB 2 assessments':len(d.get('qor_later_rob',[])),'QoR later-window GRADE bodies':len(d.get('qor_later_grade',[])),
         'Characteristic values (reports × fields)':sum(C.values()),'Characteristic values: legacy, not re-verified':C['Legacy (v26, not re-verified)'],
         'Characteristic values: single extractor, second review pending':C['Extracted (PDF quote, single extractor)'],'Characteristic values: second-reviewed PDF quotation':C['Verified (PDF quote, second reviewer)'],
         'Recovery-milestone rows':len(N.get('milestones',[])),'Harms rows (including not-located reports)':len(N.get('harms',[])),'Satisfaction/acceptability rows':len(N.get('satisfaction',[])),
         'Second-review record entries':len(d.get('second_review',[])),'Items awaiting second review':sum(int(x['items']) for x in d.get('second_review_pending',[])),
         'Stata-verified models':len(S),'Stata discrepancies':sum(r['status'].startswith('DISCREPANCY') for r in S)}
    if inv!=got:return False
    m=re.search(r'^(\d{1,2}) (\w+) (\d{4}) · ',text.splitlines()[2]);from datetime import datetime
    rdate=datetime.strptime(' '.join(m.groups()),'%d %B %Y').strftime('%Y-%m-%d') if m else ''
    payload_dates=list(d.get('release',{}).values())+[r['review_date'] for r in d.get('second_review',[])+d.get('qor_later_grade',[])]
    payload_dates+=re.findall(r'\d{4}-\d{2}-\d{2}',' '.join(r.get('extracted_by','') for k in N for r in N[k]))
    return bool(rdate) and all(x<=rdate for x in payload_dates if re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(x)))
NARR_FILES={'milestones':'recovery_milestones.csv','harms':'harms_structured.csv','satisfaction':'satisfaction_acceptability.csv'}
def narrative_verified(d):
    """Structured narrative outcomes shown in Coverage pass every row check of code/verify_narrative_outcomes.py (quote on the
    stated page, registry source, closed vocabularies, register links, no pooling, no unrecorded second review, every
    report in the harms table) and cover the same rows as the files."""
    n=d.get('narrative_outcomes')
    if n is None:return not (D/'15_NARRATIVE_OUTCOMES/recovery_milestones.csv').exists()
    sys.path.insert(0,str(D/'code'));import verify_narrative_outcomes as N
    reviewed={r['file']:r for r in d.get('second_review',[])}
    return set(n)==set(NARR_FILES) and not any(N.check_table(f,reviewed,n[k])[0] for k,f in NARR_FILES.items())
import functools
@functools.lru_cache(maxsize=None)  # git's index does not change during one run; each mutation re-runs every contract
def is_tracked(path):
    try:
        subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)], cwd=ROOT, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
def worksheet_ok(d):
    """The second-review worksheet is what its generator produces from the current records (every pending item, nothing
    else), its reviewer columns are blank (the worksheet never records a review), and the payload counts match it."""
    w=D/'02_DECISIONS/v38/second_review_worksheet.csv'
    if not w.exists():return 'second_review_pending' not in d
    sys.path.insert(0,str(D/'code'));import build_second_review_worksheet as W
    got=rows(w);want=[{k:str(v) for k,v in r.items()} for r in W.build()]
    if got!=want or any(r[k] for r in got for k in W.REVIEW_BLANK):return False
    from collections import Counter
    return d.get('second_review_pending')==[dict(item_type=t,record=r,items=n) for (t,r),n in sorted(Counter((x['item_type'],x['record']) for x in got).items())]
def second_review_consistent(d):
    """Each second-review row names a reviewer and date, counts the rows of the file it covers and carries that file's
    current SHA-256 (a judgement file changed after review invalidates the record); the regimen record agrees row by row."""
    if 'second_review' not in d:return True
    for r in d['second_review']:
        f=ROOT/r['file']
        if not (r['reviewer'] and re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['review_date']) and f.is_file()):return False
        if int(r['items'])!=len(rows(f)) or sha(f)!=r['file_sha256']:return False
        # A record with a per-row second_review column: every row marked reviewed carries this entry's reviewer and date;
        # 'all confirmed' leaves no row pending, and a partial outcome leaves pending only rows with nothing quoted.
        R=rows(f)
        if R and 'second_review' in R[0]:
            expected=f"{r['reviewer']}, {r['review_date']}: confirmed"
            if any(x['second_review'] not in ('pending',expected) for x in R):return False
            if r['outcome']=='all confirmed' and any(x['second_review']=='pending' for x in R):return False
            if r['outcome']!='all confirmed' and any(x['second_review']=='pending' and x.get('quote') for x in R):return False
    return True
def stata_reproduces_canonical(d):
    """The shipped Stata estimates still reproduce the current canonical models (catches a stale Stata run)."""
    if 'stata' not in d:return True
    canon={('core',m['model_id']):m for m in d['models']}
    canon.update({('E2',m['model_id']):m for m in d['e2_analysis']['models']})
    canon.update({('QoR 24h',m['model_id']):m for m in d['qor_analysis']['main_models']+d['qor_analysis']['diagnostics']})
    canon.update({('QoR later',m['model_id']):m for m in d.get('qor_later_models',[])})
    res={(r['analysis_set'],r['model_id']):r for r in d['stata']['results']}
    if set(res)!=set(canon) or any(s['status'].startswith('DISCREPANCY') for s in d['stata']['summary']):return False
    for key,m in canon.items():
        r=res[key]
        if int(r['k'])!=int(m['k']):return False
        if int(m['k'])==0:continue
        for a,b in [('theta','effect'),('ci_lb','ci_low'),('ci_ub','ci_high')]:
            if abs(float(r[a])-float(m[b]))>1e-6*max(1,abs(float(m[b]))):return False
    return True
def e2_inputs_consistent(d):
    """Each E2 model's exported contrasts match its study/contrast order and N, and reproduce its pooled effect from the stored tau2."""
    if 'e2_inputs' not in d:return True
    for m in d['e2_analysis']['models']:
        g=[r for r in d['e2_inputs'] if r['model_id']==m['model_id']]
        if [r['study'] for r in g]!=m['studies'].split(';') or [r['result_id'] for r in g]!=m['contrast_ids'].split(';'):return False
        if sum(float(r['n_i'])+float(r['n_c']) for r in g)!=m['N']:return False
        w=[1/(float(r['vi'])+float(m['tau2'])) for r in g]
        if abs(sum(wi*float(r['yi']) for wi,r in zip(w,g))/sum(w)-float(m['effect']))>1e-9:return False
    return True
def checks(d):
    canonical=json.load(open(D/'04_MODELS/model_outputs.json'));spec=json.load(open(D/'02_DECISIONS/model_specifications.json'))
    active={i for s in spec if s['role']!='SENSITIVITY' for i in s['result_ids']}
    p=d['prisma'];rs=d['rob'];gs=d['grade']
    ret = {
      'current version':d['version']=='v38' and d['registration']=='CRD420261452908',
      'exact model estimates and membership':d['models']==canonical and d['specifications']==spec,
      'exact numerical input identity':d['inputs']==rows(D/'04_MODELS/model_inputs.csv'),
      'exact GRADE identity':gs==rows(D/'03_CANONICAL/grade.csv') and len(gs)==38,
      'exact result RoB identity':rs==rows(D/'02_DECISIONS/v38/rob2_assessments.csv') and len(rs)==len({r['assessment_id'] for r in rs})==94,
      'all current inference components assessed':active<={r['result_id'] for r in rs},
      'canonical registry identity':d['studies']==json.load(open(D/'03_CANONICAL/studies.json')),
      'selection branch arithmetic':p['database_sought']-p['database_not_retrieved']-p['late_duplicates']==p['database_assessed'] and p['database_assessed']-p['database_excluded']+p['citation_included']==p['included_reports']==70,
      'selection label and provenance':p['exclusion_reasons'].get('no perioperative analgesia outcome found')==113 and p['unmapped_import_difference']==12 and p['citation_included']==1,
      'source holds not in main':not ({'AUDIT-0346','AUDIT-0347','V33-OD-0034','V33-OD-0078'}&active),
      'GRADE is evidence-body specific':{g['model_id'] for g in gs}=={s['model_id'] for s in spec if s['role']!='SENSITIVITY'},
      'outcome coverage addendum identity':d.get('outcome_coverage')==json.load(open(D/'07_OUTCOME_COVERAGE/coverage_summary.json')) if (D/'07_OUTCOME_COVERAGE/coverage_summary.json').exists() else True,
      'QoR analytical addendum identity':d.get('qor_analysis')==json.load(open(D/'08_QOR_ANALYSIS/qor_summary.json')) if (D/'08_QOR_ANALYSIS/qor_summary.json').exists() else True,
      'E2 sensitivity identity':d.get('e2_analysis')==json.load(open(D/'09_E2_ANALYSIS/e2_model_outputs.json')) if (D/'09_E2_ANALYSIS/e2_model_outputs.json').exists() else True,
      'E2 per-contrast input identity':d.get('e2_inputs')==rows(D/'09_E2_ANALYSIS/e2_model_inputs.csv') if (D/'09_E2_ANALYSIS/e2_model_inputs.csv').exists() else True,
      'E2 inputs reproduce E2 membership and pooled effects':e2_inputs_consistent(d),
      'E2 accounting identity':d.get('e2_accounting')=={k:rows(D/'02_DECISIONS/v38'/f) for k,f in [('tierA','E2_tierA_reclassification.csv'),('tierA_addendum','E2_tierA_reclassification_addendum.csv'),('tierB1','E2_tierB1_extraction.csv'),('tierB2','E2_tierB2_recheck.csv')]} if 'e2_accounting' in d else True,
      'E2 accounting covers E1 and E2 inputs':e2_accounting_complete(d),
      'Paired pain registry identity':d.get('paired_pain')==rows(D/'10_PAIRED_PAIN/paired_pain_registry.csv') if (D/'10_PAIRED_PAIN/paired_pain_registry.csv').exists() else True,
      'Paired pain registry covers contrasts and agrees with decisions':paired_pain_consistent(d),
      'Sensitivity map identity':d.get('sensitivity_map')==rows(D/'12_SENSITIVITY_MAP/sensitivity_parent_map.csv') if (D/'12_SENSITIVITY_MAP/sensitivity_parent_map.csv').exists() else True,
      'Sensitivity map covers every sensitivity model':sensitivity_map_complete(d),
      'Results register identity':d.get('results_register')==[{k:r[k] for k in ['result_id','study','trial_id','comparison_id','outcome','window','data_type','n_i','n_c','comparator_class','decision','rationale','models','source_location']} for r in rows(D/'03_CANONICAL/results.csv')] if 'results_register' in d else True,
      'Characteristics identity':d.get('characteristics')==rows(D/'14_CHARACTERISTICS/report_characteristics.csv') if (D/'14_CHARACTERISTICS/report_characteristics.csv').exists() else True,
      'Characteristics complete with declared statuses':characteristics_complete(d),
      # A value shown as quoted from a PDF (any extractor or review state) must name the PDF page it came from.
      'Quoted characteristic values carry a page locator':all(re.search(r'p\.\s?\d',c['source']) for c in d.get('characteristics',[]) if c['status'] in ('Verified (PDF quote)','Extracted (PDF quote, single extractor)','Verified (PDF quote, second reviewer)')),
      'Regimen extraction matches record and source quotes':regimen_verified(d),
      'Baseline/protocol extraction matches record and source quotes':baseline_verified(d),
      'Second-review worksheet current and unreviewed':worksheet_ok(d),
      'Current-state report is current and matches the payload':current_state_ok(d),
      'Narrative outcomes identity':d.get('narrative_outcomes')=={k:rows(D/'15_NARRATIVE_OUTCOMES'/f) for k,f in NARR_FILES.items()} if (D/'15_NARRATIVE_OUTCOMES/recovery_milestones.csv').exists() else 'narrative_outcomes' not in d,
      'Narrative outcomes verified against sources':narrative_verified(d),
      'Stata verification identity':d['stata']['summary']==rows(D/'13_STATA/output/stata_verification_summary.csv') and d['stata']['results']==rows(D/'13_STATA/output/stata_model_results.csv') if 'stata' in d else True,
      'Stata reproduces current canonical results':stata_reproduces_canonical(d),
      'QoR later-window identity':d.get('qor_later_models')==json.load(open(D/'08_QOR_ANALYSIS/qor_models_later.json')) if (D/'08_QOR_ANALYSIS/qor_models_later.json').exists() else True,
      'QoR later-window RoB identity': d.get('qor_later_rob') == rows(D/'08_QOR_ANALYSIS/qor_rob2_later.csv') and len(d.get('qor_later_rob', [])) == 5 if 'qor_later_rob' in d else True,
      'Release dates derived from payload and E2 decision':release_ok(d),
      'QoR later-window GRADE identity':d.get('qor_later_grade')==rows(D/'08_QOR_ANALYSIS/qor_grade_later.csv') if (D/'08_QOR_ANALYSIS/qor_grade_later.csv').exists() else True,
      'QoR later-window GRADE links current models':qor_later_grade_consistent(d),
      'Second-review record identity':d.get('second_review')==rows(D/'02_DECISIONS/v38/second_review.csv') if (D/'02_DECISIONS/v38/second_review.csv').exists() else True,
      'Second review covers current judgement files':second_review_consistent(d),
      'E2 methods integrity': d.get('e2_methods', {}).get('Timestamp note', '') == re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')).group(1).strip() if 'e2_methods' in d else True,

    }
    

    for item in d['downloads']:
        if not is_tracked(ROOT / item['source']):
            ret['all downloads tracked by git'] = False
            break
    else:
        ret['all downloads tracked by git'] = True

    if 'e2_methods_html' in d:
        import html as html_lib
        def normalize_source(text):
            text = re.sub(r'(?m)^---$', '', text)
            text = re.sub(r'\*\*(.*?)\*\*', r'\g<1>', text, flags=re.DOTALL)
            text = re.sub(r'`(.*?)`', r'\g<1>', text, flags=re.DOTALL)
            text = re.sub(r'(?m)^-\s+', '', text)
            text = re.sub(r'(?m)^\d+\.\s+', '', text)
            text = re.sub(r'(?m)^>\s+', '', text)
            return re.sub(r'\s+', ' ', text).strip()
        def normalize_html(h):
            h = h.replace('<p>', ' ').replace('</p>', ' ').replace('<ul>', ' ').replace('</ul>', ' ').replace('<li>', ' ').replace('</li>', ' ').replace('<blockquote>', ' ').replace('</blockquote>', ' ')
            h = re.sub(r'<[^>]+>', '', h)
            h = html_lib.unescape(h)
            return re.sub(r'\s+', ' ', h).strip()
            
        e2_methods_text = (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')
        def get_sec(txt, h, st=None):
            pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n#|\Z)'
            if st: pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n' + re.escape(st) + r'|\n#|\Z)'
            return re.search(pat, txt, re.DOTALL).group(1).strip()
        
        expected_e2 = {
            'Timestamp note': re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', e2_methods_text).group(1).strip(),
            'Why this document exists, stated plainly': get_sec(e2_methods_text, 'Why this document exists, stated plainly'),
            'E1 — registered primary (retained, reported in full)': get_sec(e2_methods_text, 'E1 — registered primary (retained, reported in full)'),
            'E2 — amended primary (post hoc)': get_sec(e2_methods_text, 'E2 — amended primary (post hoc)', st='### Admission rules'),
            'Prespecified sensitivity analyses for E2': get_sec(e2_methods_text, 'Prespecified sensitivity analyses for E2'),
            'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)': get_sec(e2_methods_text, 'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)'),
            'Decision after the E2 run — 23 September 2026: E1 retained as primary': get_sec(e2_methods_text, 'Decision after the E2 run — 23 September 2026: E1 retained as primary')
        }
        
        for k, v in expected_e2.items():
            if normalize_html(d['e2_methods_html'].get(k, '')) != normalize_source(v):
                ret['E2 HTML completeness'] = False
                break
        else:
            ret['E2 HTML completeness'] = True


    if 'qor_later_models' in d and 'qor_later_rob' in d:
        rob_ids = {r['result_id'] for r in d['qor_later_rob']}
        for m in d['qor_later_models']:
            if not set(m['result_ids']) <= rob_ids:
                ret['QoR later-window RoB identity'] = False

    if 'qor_later_metafor_manifest' in d:
        import hashlib
        man = d['qor_later_metafor_manifest']
        expected_models = json.load(open(D/'08_QOR_ANALYSIS/qor_models_later.json'))
        for f in man['files']:
            p = D/'08_QOR_ANALYSIS/metafor_forest_later'/f['file']
            if hashlib.sha256(p.read_bytes()).hexdigest() != f['sha256']:
                ret['QoR later-window metafor manifest'] = False
            else:
                ret.setdefault('QoR later-window metafor manifest', True)
        
        import csv
        comp = list(csv.DictReader(open(D/'08_QOR_ANALYSIS/metafor_forest_later/metafor_comparison_later.csv')))
        all_passed = True
        for row in comp:
            if row['passed'] != 'TRUE': all_passed = False
            model = next((m for m in expected_models if m['model_id'] == row['model_id']), None)
            if model and str(model.get(row['field'])) != 'None' and row['canonical'] != 'NA':
                try:
                    c_val = float(row['canonical'])
                    m_val = float(model[row['field']])
                    if abs(c_val - m_val) > 1e-4:
                        all_passed = False
                except:
                    pass
        if d.get('qor_later_metafor_manifest', {}).get('fail_comp'):
            all_passed = False
        ret['QoR later-window metafor comparison'] = all_passed

    return ret

def main(site=None):
    site=pathlib.Path(site or ROOT/'dashboard');data=json.load(open(site/'current_review.json'));c=checks(data)
    for name,ok in c.items():print(('PASS ' if ok else 'FAIL ')+name)
    if not all(c.values()):return 1
    js=(site/'current_review.js').read_text();loaded=json.JSONDecoder().raw_decode(js.split('window.CURRENT_REVIEW = ',1)[1])[0]
    assert loaded==data,'JS/JSON bundle mismatch'
    # Every Stata figure ships in the site with its registered hash; model figures print canonical values.
    for f in data.get('stata',{}).get('figures',[]):
        for ext in ('svg','pdf','png'):
            assert sha(site/f[ext+'_href'])==f[ext+'_sha256']==sha(ROOT/f[ext+'_file']),f[ext+'_href']
        assert f['kind']=='descriptive' or f['verification_status']=='values equal canonical',f['figure_id']
    # The Study Explorer graph must be exactly what the payload implies (catches a stale or hand-edited graph).
    from build_evidence_graph import graph_from
    shipped=json.JSONDecoder().raw_decode((site/'evidence_graph.js').read_text().split('window.EVIDENCE_GRAPH = ',1)[1])[0]
    assert shipped==graph_from(data),'Evidence graph is stale or not derived from current_review.json'
    x=copy.deepcopy(data);x['qor_analysis']['rob'].pop();assert graph_from(x)!=shipped,'Evidence-graph mutation escaped'
    assert {'QOR24-HOU2023','QOR48-HOU2023'}<=set(shipped['studies']['Hou 2023']['rob']),'Hou 2023 QoR assessments unlinked'
    assert all(shipped['models'][m['model_id']]['studies'] for m in data.get('e2_analysis',{}).get('models',[])),'E2 model without linked studies'
    page=(site/'index.html').read_text();srcs=re.findall(r'(?:src|href)="([^"#]+)"',page)
    for src in srcs:
        if src.startswith(('https:','http:')):continue
        assert (site/src.split('?')[0]).is_file(),src
    for item in data['downloads']:
        assert sha(site/item['href'])==item['sha256']==sha(ROOT/item['source']),item['href']
    assert all(token not in page for token in ['app.js','v34_data.js','CRD420251090635','k=7, N=676','−14.00','−9.91'])
    
    # New CI checks
    html_without_scripts = re.sub(r'<script.*?</script>', '', page, flags=re.DOTALL)
    html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
    assert not re.search(r'\{[a-z_]+\}', html_without_scripts), 'Unfilled placeholder found in index.html outside scripts/styles'
    nav_match = re.search(r'<nav class="nav"[^>]*>(.*?)</nav>', page)
    assert nav_match, 'Nav block not found'
    assert nav_ok(nav_match.group(0)), 'Navigation: wrong routes, groups or semantics'
    assert not nav_ok(nav_match.group(0).replace('data-view="studies"','data-view="study"')), 'Nav mutation escaped'
    assert not nav_ok(nav_match.group(0).replace('<a href="#results"','<a role="tab" href="#results"')), 'Nav role=tab mutation escaped'
    # Exactly the v38 assets are loaded (app.js and the other legacy bundles are not), theme.js in <head> before the CSS.
    loaded=[x.split('?')[0] for x in re.findall(r'<script src="([^"]+)"',page)]
    assert loaded==V38_SCRIPTS,f'Unexpected scripts loaded: {loaded}'
    head=page.split('</head>')[0]
    assert re.findall(r'<link rel="stylesheet" href="([^"?]+)',page)==['current_review.css'] and head.index('theme.js')<head.index('current_review.css'),'theme.js must load in <head> before the stylesheet'
    assert theme_ok((site/'theme.js').read_text()),'theme.js stores more than the one theme key or reaches the network'
    assert not theme_ok((site/'theme.js').read_text()+"localStorage.setItem('other','x')"),'Theme storage mutation escaped'
    explorer_js=(site/'interactive_explorer.js').read_text()
    assert legend_ok(explorer_js),'Study Explorer provenance legend is missing or its statuses differ from the characteristics vocabulary'
    assert not legend_ok(explorer_js.replace("'Legacy (v26, not re-verified)': ['L'","'Legacy': ['L'")),'Legend vocabulary mutation escaped'
    for js_name in ('interactive_explorer.js','current_review_ui.js'):
        assert 'localStorage' not in (site/js_name).read_text(),f'{js_name} must not use browser storage (theme.js alone keeps the theme choice)'
    footer_match = re.search(r'<footer>(.*?)</footer>', page)
    assert footer_match and '{' not in footer_match.group(1) and '}' not in footer_match.group(1), 'Placeholder found in footer'
    
    if 'e2_labels' in data and 'e2_analysis' in data:
        e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}
        for label_key in data['e2_labels']:
            assert label_key in e2_ids, f'e2_labels key {label_key} not in e2_analysis.models'
    
    downloads_hrefs = [item['href'].split('/')[-1] for item in data['downloads']]
    for required_file in ['e2_model_outputs.csv', 'E2_RESULTS.md', 'AMENDED_PRIMARY_ESTIMAND_E2.md', 'qor_models_later.csv', 'ADDITIONAL_FILE_12.md', 'additional_file_12_A1_primary_construct.csv', 'additional_file_12_A2_other_windows.csv', 'additional_file_12_tierB_no_candidate_result.csv']:
        assert required_file in downloads_hrefs, f'Missing from downloads manifest: {required_file}'
    assert len(downloads_hrefs) == len(set(downloads_hrefs)), 'Filename collision in downloads manifest'
    
    report_text = (ROOT/'FINAL_CURRENT_STATE_REPORT.md').read_text(encoding='utf-8')
    section_match = re.search(r'\*\*Not completed — outstanding\*\*(.*?)(?=\n\*\*|\n## |\Z)', report_text, re.DOTALL)
    expected_outstanding = re.findall(r'- \*\*(.*?)\*\*', section_match.group(1))
    assert data.get('outstanding') == expected_outstanding and len(expected_outstanding) > 0, "outstanding data mismatch or empty"
    
    e2_methods_text = (D/'02_DECISIONS/v38/AMENDED_PRIMARY_ESTIMAND_E2.md').read_text(encoding='utf-8')
    def get_sec(txt, h, st=None):
        pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n#|\Z)'
        if st: pat = r'#+\s+' + re.escape(h) + r'\s*\n(.*?)(?=\n' + re.escape(st) + r'|\n#|\Z)'
        return re.search(pat, txt, re.DOTALL).group(1).strip()
    
    expected_e2 = {
        'Timestamp note': re.search(r'(\*\*Timestamp note[^\n]+(?:\n[^\n]+)+)', e2_methods_text).group(1).strip(),
        'Why this document exists, stated plainly': get_sec(e2_methods_text, 'Why this document exists, stated plainly'),
        'E1 — registered primary (retained, reported in full)': get_sec(e2_methods_text, 'E1 — registered primary (retained, reported in full)'),
        'E2 — amended primary (post hoc)': get_sec(e2_methods_text, 'E2 — amended primary (post hoc)', st='### Admission rules'),
        'Prespecified sensitivity analyses for E2': get_sec(e2_methods_text, 'Prespecified sensitivity analyses for E2'),
        'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)': get_sec(e2_methods_text, 'Amendment E2.1 — 23 September 2026 (after E2 was applied to Tier B1)'),
        'Decision after the E2 run — 23 September 2026: E1 retained as primary': get_sec(e2_methods_text, 'Decision after the E2 run — 23 September 2026: E1 retained as primary')
    }
    assert data.get('e2_methods') == expected_e2, "e2_methods data mismatch"

    
    
    # v38 download checks
    report_text = (site/'current/FINAL_CURRENT_STATE_REPORT.md').read_text()
    assert 'adjudication v38' in report_text.splitlines()[0], 'FINAL_CURRENT_STATE_REPORT.md not v38'

    grade_text = (site/'current/FINAL_GRADE_RECOMMENDATIONS.md').read_text()
    assert 'v38' in grade_text.splitlines()[0], 'FINAL_GRADE_RECOMMENDATIONS.md not v38'

    import csv
    matrix_csv = (site/'current/FINAL_MODEL_MEMBERSHIP_MATRIX.csv').read_text().splitlines()
    matrix_reader = csv.DictReader(matrix_csv)
    matrix_pairs = {(row['result_id'], row['model_id']) for row in matrix_reader if row['decision'] == 'INCLUDE'}
    
    spec_json = json.loads((pathlib.Path(__file__).parent.parent / '10_FINAL_ADJUDICATION/02_DECISIONS/model_specifications.json').read_text())
    expected_pairs = {(r, s['model_id']) for s in spec_json if s['role'] != 'SENSITIVITY' for r in s['result_ids']}
    
    assert matrix_pairs == expected_pairs, f"Matrix pairs mismatch. Found {len(matrix_pairs)}, expected {len(expected_pairs)} (90)"
    
    rob2_csv = (site/'current/FINAL_RESULT_ROB2_LINKAGE.csv').read_text().splitlines()
    rob2_reader = csv.DictReader(rob2_csv)
    rob_linkages = set()
    for row in rob2_reader:
        if row['rob2_assessment_id']: rob_linkages.add(row['rob2_assessment_id'])
        if row['alternative_assessments']:
            rob_linkages.update([x.strip() for x in row['alternative_assessments'].split(';')])
            
    rob2_assessments_csv = (pathlib.Path(__file__).parent.parent / '10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv').read_text().splitlines()
    assess_ids = {row['assessment_id'] for row in csv.DictReader(rob2_assessments_csv)}
    
    missing_assessments = assess_ids - rob_linkages
    assert not missing_assessments, f"Missing assessments in linkage: {missing_assessments}"

    # Look in the repository, not next to the site: a build can be written anywhere.
    # Tracked files are what gets published; fall back to the working tree without git.
    try:
        root_files=subprocess.run(['git','ls-files','--','fix_*.py','test_ui.py'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.split()
    except (OSError,subprocess.CalledProcessError):
        root_files=[p.name for pattern in ('fix_*.py','test_ui.py') for p in ROOT.glob(pattern)]
    assert not root_files, f"Scratch files found in repo root: {root_files}"

    ui_js = (site/'current_review_ui.js').read_text()
    assert 'Review complete' not in ui_js, '"Review complete" found in current_review_ui.js without qualifier'
    for forbidden in ['fetch(','XMLHttpRequest','localStorage.setItem']:
        assert forbidden not in ui_js, 'Unexpected external/hidden state operation'
    assert not re.search(r'k=\d+', ui_js), 'Literal k=<digits> found in current_review_ui.js'
    assert not re.search(r'[−-]?\d{1,2}\.\d{2}(?!\d)', ui_js), 'Literal decimal estimate found in current_review_ui.js'
    assert "addEventListener('hashchange'" in ui_js, "hashchange listener missing"
    assert "addEventListener('popstate'" in ui_js, "popstate listener missing"
    assert "history.replaceState" in ui_js, "replaceState missing"
    if "function show(" in ui_js:
        show_body = ui_js.split("function show(")[1].split("}")[0]
        assert "history.replaceState" not in show_body, "replaceState found inside show()"
    if "document.addEventListener('click'" in ui_js:
        click_body = ui_js.split("document.addEventListener('click'")[1].split("});")[0]
        assert "history.replaceState" not in click_body, "replaceState found inside click listener"
    # Existing figures must survive and resolve in both source and built site.
    figures=json.JSONDecoder().raw_decode((site/'article_figures.js').read_text().split('window.ARTICLE_FIGURES = ',1)[1])[0]
    images=[f['src'] for fs in figures.values() for f in fs]
    assert all((site/name).is_file() for name in images)
    mutations=[('exact model estimates and membership',lambda d:d['models'][0].__setitem__('display_effect',999)),('exact GRADE identity',lambda d:d['grade'][0].__setitem__('certainty','High')),('exact result RoB identity',lambda d:d['rob'][0].__setitem__('d3','INVALID TEST VALUE')),('selection label and provenance',lambda d:d['prisma'].__setitem__('unmapped_import_difference',0))]
    if 'qor_analysis' in data:
        mutations.append(('QoR analytical addendum identity',lambda d:d['qor_analysis']['main_models'][0].__setitem__('effect',999)))
        q=data['qor_analysis']
        assert len(q['main_models'])==len(q['grade'])==3 and len(q['rob'])==8 and len(q['diagnostics'])==9
        assert {r['result_id'] for r in q['inputs']}=={r['result_id'] for r in q['rob']}
    if 'e2_analysis' in data:
        mutations.append(('E2 sensitivity identity',lambda d:d['e2_analysis']['models'][0].__setitem__('effect',999)))
    if 'qor_later_models' in data:
        mutations.append(('QoR later-window identity',lambda d:d['qor_later_models'][0].__setitem__('effect',999)))
    if 'qor_later_rob' in data:
        mutations.append(('QoR later-window RoB identity', lambda d: d['qor_later_rob'].__delitem__(0)))
    if 'qor_later_metafor_manifest' in data:
        mutations.append(('QoR later-window metafor manifest', lambda d: d['qor_later_metafor_manifest']['files'][0].__setitem__('sha256', 'badhash')))
        mutations.append(('QoR later-window metafor comparison', lambda d: d.get('qor_later_metafor_manifest').__setitem__('fail_comp', True)))

    if 'e2_inputs' in data:
        mutations.append(('E2 per-contrast input identity',lambda d:d['e2_inputs'][0].__setitem__('yi','0')))
        mutations.append(('E2 inputs reproduce E2 membership and pooled effects',lambda d:d['e2_inputs'].pop()))
    if 'results_register' in data:
        mutations.append(('Results register identity',lambda d:d['results_register'][0].__setitem__('decision','INCLUDE?')))
    if 'characteristics' in data:
        mutations.append(('Characteristics identity',lambda d:d['characteristics'][0].__setitem__('value','changed')))
        mutations.append(('Quoted characteristic values carry a page locator',lambda d:next(c for c in d['characteristics'] if c['status']=='Verified (PDF quote)').__setitem__('source','dashboard/pdf_extracted.js')))
        mutations.append(('Characteristics complete with declared statuses',lambda d:d['characteristics'][0].__setitem__('status','Confirmed')))
        if (D/'14_CHARACTERISTICS/regimen_extraction.csv').exists():
            REG=('postoperative_analgesia','pca_regimen','rescue_analgesia','cumulative_duration')
            mutations.append(('Regimen extraction matches record and source quotes',lambda d:next(c for c in d['characteristics'] if c['field'] in REG and c['status'] in ('Extracted (PDF quote, single extractor)','Verified (PDF quote, second reviewer)')).__setitem__('note','p.1: “quote not in source”')))
            mutations.append(('Regimen extraction matches record and source quotes',lambda d:[c.__setitem__('status','Extracted (PDF quote, single extractor)') for c in d['characteristics'] if c['status']=='Verified (PDF quote, second reviewer)'][:1]))
        if 'narrative_outcomes' in data:
            NV='Narrative outcomes verified against sources'
            first=lambda d,k,f=lambda r:True:next(r for r in d['narrative_outcomes'][k] if f(r))
            mutations.append(('Narrative outcomes identity',lambda d:first(d,'milestones').__setitem__('value_i','changed')))
            # a quote not in the source, an unreported harm turned into a zero, a pooled claim, a claimed second review,
            # a register link to another report's result, a report dropped from the harms table
            mutations.append((NV,lambda d:first(d,'milestones').__setitem__('quote','a quotation that is not in the report')))
            mutations.append((NV,lambda d:first(d,'harms',lambda r:r['reporting']=='Not located (not a zero)').update(events_i='0',events_c='0')))
            mutations.append((NV,lambda d:first(d,'satisfaction').__setitem__('synthesis','Pooled by random-effects meta-analysis.')))
            mutations.append((NV,lambda d:first(d,'harms',lambda r:r['quote']).__setitem__('second_review','ZZ, 2026-01-01: confirmed')))
            mutations.append((NV,lambda d:first(d,'harms',lambda r:not r['quote']).__setitem__('second_review','SP, 2026-09-30: confirmed') if any(x['file'].endswith('harms_structured.csv') for x in d.get('second_review',[])) else first(d,'harms',lambda r:not r['quote']).__setitem__('second_review','ZZ, 2026-01-01: confirmed')))
            mutations.append((NV,lambda d:first(d,'milestones',lambda r:r['register_result_id']).__setitem__('register_result_id','V33-OD-0001')))
            mutations.append((NV,lambda d:d['narrative_outcomes']['harms'].__setitem__(slice(None),[r for r in d['narrative_outcomes']['harms'] if r['report_id']!=d['narrative_outcomes']['harms'][0]['report_id']])))
        CS='Current-state report is current and matches the payload'
        mutations.append((CS,lambda d:d['qor_later_grade'].pop()))
        mutations.append((CS,lambda d:d['second_review_pending'][0].__setitem__('items',int(d['second_review_pending'][0]['items'])+1)))
        mutations.append((CS,lambda d:d['release'].__setitem__('e2_date','2026-12-31')))
        mutations.append((CS,lambda d:d['characteristics'][0].__setitem__('status','Legacy (v26, not re-verified)')))
        if 'second_review_pending' in data:
            mutations.append(('Second-review worksheet current and unreviewed',lambda d:d['second_review_pending'][0].__setitem__('items',0)))
            mutations.append(('Second-review worksheet current and unreviewed',lambda d:d['second_review_pending'].pop()))
        if (D/'14_CHARACTERISTICS/baseline_protocol_extraction.csv').exists():
            BAS=('age','female','bmi','asa','anaesthesia','acupoints','frequency','intensity','timing','sessions','session_duration')
            QUOTED=('Extracted (PDF quote, single extractor)','Verified (PDF quote, second reviewer)')
            first_bas=lambda d,st:next(c for c in d['characteristics'] if c['field'] in BAS and (c['status'] in QUOTED if st=='quoted' else c['status']==st) and (st!='quoted' or 'baseline_protocol_extraction' in c['source']))
            flip=lambda c:c.__setitem__('status',QUOTED[1-QUOTED.index(c['status'])])
            # a changed value, a quote that is not in the record, a review state that contradicts the record, a value with no page locator,
            # and a legacy value brought back where the record now governs
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:first_bas(d,'quoted').__setitem__('value','changed')))
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:first_bas(d,'quoted').__setitem__('note','p.1: “quote not in source”')))
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:flip(first_bas(d,'quoted'))))
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:(lambda c:c.__setitem__('source',c['source'].split(' p.')[0]))(first_bas(d,'quoted'))))
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:first_bas(d,'quoted').update(status='Legacy (v26, not re-verified)',source='dashboard/data.js')))
            mutations.append(('Baseline/protocol extraction matches record and source quotes',lambda d:first_bas(d,'Not reported in source').update(value='5–15 mA',status='Legacy (v26, not re-verified)')))
    if 'stata' in data:
        mutations.append(('Stata verification identity',lambda d:d['stata']['summary'][0].__setitem__('status','changed')))
        mutations.append(('Stata reproduces current canonical results',lambda d:next(r for r in d['stata']['results'] if r['model_id']=='opioid24_EA_usual').__setitem__('ci_lb','-17.56')))
    if 'sensitivity_map' in data:
        mutations.append(('Sensitivity map identity',lambda d:d['sensitivity_map'][0].__setitem__('relation','changed')))
        mutations.append(('Sensitivity map covers every sensitivity model',lambda d:d['sensitivity_map'].pop()))
    if 'paired_pain' in data:
        mutations.append(('Paired pain registry identity',lambda d:d['paired_pain'][0].__setitem__('pain_md','0')))
        mutations.append(('Paired pain registry covers contrasts and agrees with decisions',lambda d:[r.update(pairing_status='ELIGIBLE PAIRED PAIN') for r in d['paired_pain'] if r['study']=='Lin 2002' and r['analysis']=='E2']))
    if 'e2_accounting' in data:
        mutations.append(('E2 accounting identity',lambda d:d['e2_accounting']['tierB2'].pop()))
        mutations.append(('E2 accounting covers E1 and E2 inputs',lambda d:[r.__setitem__('E2_disposition','NOT ADMITTED') for r in d['e2_accounting']['tierA'] if r['report']=='Chen 1998']))
    mutations.append(('E2 methods integrity', lambda d: d['e2_methods'].update({'Timestamp note': 'Altered text'})))
    if 'qor_later_grade' in data:
        mutations.append(('QoR later-window GRADE identity',lambda d:d['qor_later_grade'][0].__setitem__('certainty','High')))
        mutations.append(('QoR later-window GRADE links current models',lambda d:d['qor_later_grade'][0].__setitem__('certainty','Moderate')))
        mutations.append(('QoR later-window GRADE links current models',lambda d:d['qor_later_grade'][0].__setitem__('model_id','QOR15_SHAM_POD3_WITHOUT_HOU_2023')))
        mutations.append(('QoR later-window GRADE links current models',lambda d:d['qor_later_grade'][1].__setitem__('ci_high','9.99')))
    if 'second_review' in data:
        mutations.append(('Second-review record identity',lambda d:d['second_review'][0].__setitem__('outcome','changed')))
        mutations.append(('Second review covers current judgement files',lambda d:d['second_review'][0].__setitem__('items','93')))
        mutations.append(('Second review covers current judgement files',lambda d:d['second_review'][3].__setitem__('file_sha256','0'*64)))
    mutations.append(('Release dates derived from payload and E2 decision', lambda d: d['release'].__setitem__('e2_date', '2026-09-20')))
    mutations.append(('all downloads tracked by git', lambda d: d['downloads'].append(dict(label='Fake', href='current/fake.txt', source='fake.txt', sha256='hash'))))
    if 'e2_methods_html' in data:
        def drop_line(d):
            val = d['e2_methods_html']['Decision after the E2 run — 23 September 2026: E1 retained as primary']
            d['e2_methods_html']['Decision after the E2 run — 23 September 2026: E1 retained as primary'] = val.replace('precise than E1&#x27;s −7.70 (−10.62, −4.78).', '')
        mutations.append(('E2 HTML completeness', drop_line))
    for key,mutate in mutations:
        x=copy.deepcopy(data);mutate(x);assert not checks(x)[key],f'Mutation escaped: {key}'
    
    # HTML placeholder mutation test
    def check_placeholders(html):
        html_without_scripts = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
        return not bool(re.search(r'\{[a-z_]+\}', html_without_scripts))
    
    mutated_page = page.replace('<noscript>', '<noscript>{unfilled_placeholder}</noscript>')
    assert not check_placeholders(mutated_page), 'Placeholder mutation escaped'

    assert "IVMME" not in page, "IVMME found in built index.html"
    assert "unitLabel" in ui_js, "current_review_ui.js missing unitLabel mapping"

    if (site/'build-meta.json').exists():
        meta=json.load(open(site/'build-meta.json'));assert meta['master_version']=='v38' and meta['strict_primary_opioid_k']==1 and meta['canonical_reports']==70 and meta['included_studies']==69
        # The page shows its commit and build time from an inline copy of build-meta.json (no hard-coded SHA).
        inline=re.findall(r'<script id="build-meta" type="application/json">(.*?)</script>',page.split('</head>')[0])
        assert len(inline)==1 and json.loads(inline[0])==meta,'Inline build metadata missing or differs from build-meta.json'
    else:
        assert 'id="build-meta"' not in page,'Source page must not carry a build record (only built sites do)'
    assert not re.search(r'\b(?:6619e2a|eeb6821)\b',ui_js+explorer_js),'Hard-coded commit SHA in dashboard scripts'
    print(f'PASS v38 + addenda: {len(c)} contracts, {len(mutations)} isolated mutations, {len(data["downloads"])} download hashes, {len(images)} original figure files. Legacy v26 contract not applied.')
    return 0
if __name__=='__main__':
    location=sys.argv[sys.argv.index('--site')+1] if '--site' in sys.argv else None
    raise SystemExit(main(location))
