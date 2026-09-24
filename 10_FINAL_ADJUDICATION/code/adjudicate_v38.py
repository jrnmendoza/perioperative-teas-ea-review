"""Authored v38 decisions, not an automated risk-of-bias classifier.

Each study entry was considered against its full-text methods/flow and the exact
results below. Shared design facts are reused; outcome/arm exceptions are explicit.
Raw exports, source values and historical assessments are never overwritten.
"""
import csv, json, pathlib, collections, hashlib, re, html
ROOT=pathlib.Path(__file__).resolve().parents[2]; D=ROOT/'10_FINAL_ADJUDICATION'
OUT=D/'02_DECISIONS/v38'; OUT.mkdir(exist_ok=True)
def read(p): return list(csv.DictReader(open(ROOT/p,encoding='utf-8-sig')))
def save(p,rows):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
S={s['report_id']:s for s in json.load(open(D/'03_CANONICAL/studies.json'))}
# D1,D2,D3,D4,D5: L=Low, S=Some concerns, H=High.
# D5 conservatively S when a prospective result-level analysis plan has not been
# verified. Merely mentioning an outcome in the published paper is not enough.
P={}
def p(study,vector,d1,d2,d3,d4): P[study]=(vector,[d1,d2,d3,d4])
p('An 2014','SLHLS','Computer random numbers; concealment not established.','EA under sedation and blinded observation; no demonstrated trial-related deviations.','7/88 omitted, including repeat surgery and persistent unconsciousness: plausibly strongly related to opioid requirement.','Recorded PCA fentanyl dose; participant and observer masking reported.')
p('Chen 2015','LLLLS','Computer sequence and opaque allocation envelopes.','Patient, clinical and assessment masking; no evidence of material differential care.','One protocol-breach omission from 84; little missing information.','Masked PONV ascertainment; no demonstrated masking failure.')
p('Chen 2015 (Hyperalgesia)','LLLLS','Computer sequence and opaque envelopes.','Broad masking of patients and clinical/assessment personnel.','One omission from 60; little missing information.','Masked PONV collection; no documented measurement asymmetry.')
p('El-Rakshy 2009','SSHLS','Computer sequence; concealment insufficiently documented.','Usual-care allocation and inconsistent group descriptions leave co-intervention concerns; awareness alone is not proof of deviations.','107 randomized versus 95 analysed, conflicting arm labels and exclusions: outcome-dependent missingness cannot reasonably be dismissed.','Recorded morphine exposure; measurement of delivered dose is objective.')
p('Gao 2021','LSLLS','Central block sequence with sealed allocation.','Patients not blinded; differential postoperative behaviours/care cannot be excluded.','610/307 analysed in the intention-to-treat population.','Bowel sounds obtained by masked auscultation; patient-reported events assessed separately below.')
p('Gao 2022','LSLSS','Electronic block randomization with concealed implementation.','Incomplete patient masking; possible differential reporting/care without proof of major deviations.','827/828 intention-to-treat denominators retained.','Nausea-containing outcomes depend on incompletely masked patient reporting; vomiting assessed separately.')
p('Gu 2019','SLLLS','Computer-generated sequence; concealment not adequately specified.','Patients, data collectors and statistician masked.','3/120 not analysed; low fraction without evidence of important differential loss.','Masked symptom/event recording; patient report alone does not establish biased measurement.')
p('Guo 2023','LLSLS','Independent allocation technician and controlled sequence implementation.','Masked anaesthesia management under common protocol.','18/128 omitted postrandomization; balance among completers does not establish benign missingness.','Recorded remifentanil dose by masked clinical team.')
p('He 2026 (hepatectomy/JIS)','LLLLL','Secure web randomization, stratification and blocks.','Patients and clinical/outcome staff masked; treatment under general anaesthesia with concealment.','Two cancellations/withdrawals from 161; 159 mITT, little outcome loss.','Primary PONV assessed under masking; protocol/SAP and supplement available in the source set.')
p('Huang 2024','LLSSS','Computer sequence in opaque envelopes opened only by acupuncturist; prior claim of absent concealment rejected.','Common rehabilitation and analgesia; no demonstrated material deviations.','114 randomized, 108 completed; ITT claimed and tables retain 38/arm, but handling of missing walking-pain measurements not sufficiently explained.','Subjective walking pain; incomplete sensory masking and active-side sensations leave measurement concerns, not automatic high risk.')
p('Huang 2025','LSSHS','Central concealed allocation.','Open usual-care comparison; differential recovery behaviour/co-interventions possible.','13/101 omitted, including complications; reasons can relate to recovery.','Unblinded patient/family reports determine recovery times and are likely susceptible to expectations.')
p('Jiang 2026','LLSLS','Independent randomization with opaque envelopes.','Deception sham with patient/assessor masking and common care.','614 allocated, 587 analysed; text withdrawal arithmetic also inconsistent. Worst/best-case ITT applies to primary flatus, not this per-protocol PONV result.','Masked postoperative symptom assessment.')
p('Liang 2021','LLSLS','Independent computer sequence and sealed allocation.','Anaesthetist explicitly masked despite absence of a stimulation sham.','5/75 excluded for changed procedure/blood sampling; remifentanil may already have been measured and exclusions are not clearly ignorable.','Objective dose titrated by explicitly masked anaesthetist.')
p('Liu 2015','LLSLS','Randomized concealed allocation; only acupuncturist knows assignment.','Patients, anaesthesiologists, surgeons and recovery assessors masked.','4/92 removed for >8h operations or >2500mL blood loss, plausibly related to postoperative symptoms.','Masked nausea/vomiting collection.')
p('Liu 2021','SS LSS'.replace(' ',''),'Online sequence; concealment insufficiently specified.','No-current sham with incompletely established clinical/patient masking.','100/100 retained for these pain contrasts.','Pain is subjective; explicit assessor masking pertains to cognitive testing, not clearly to pain. Possible influence, without evidence justifying automatic High.')
p('Liu 2026 (burn)','LLLLS','Computer sequence with opaque envelopes and independent allocation monitoring.','Broad masking and common perioperative care.','Fig 1 (PDF p5): 102 screened, 14 excluded BEFORE randomization, 88 allocated; one skin-intolerance loss/arm, 86 analysed. Not 16 postrandomization losses.','Masked postoperative nausea-vomiting assessment.')
p('Lu 2021','LSLSS','Central web block randomization in multicentre trial.','Patients not fully masked; potential differential care/reporting; clinician dosing assessed separately.','576 intention-to-treat participants retained across the two active arms and shared control.','Patient-reported nausea component potentially influenced; objective vomiting and masked dose assessed separately.')
p('Lu 2022','LSSSS','Computer sequence with sealed allocation.','Patient awareness of treatment possible despite assessor masking.','6/100 excluded (five open conversions and one refusal); recovery-related missingness remains possible.','Patient-reported flatus vulnerable to awareness; observed defecation considered separately.')
p('Luo 2026','LSLHS','Computer sequence in sequentially numbered opaque envelopes (methods).','Anaesthetists unblinded; possible differential care, not demonstrated major deviations.','277/277 retained.','Blinding test: 77.5% active and 66.2% sham correctly guessed allocation. Subjective nausea likely influenced; vomiting has separate rating.')
p('Ng 2013','SLLLS','Random allocation using NON-opaque envelopes: concealment concern.','EA/sham participants masked; no-acupuncture arm handled separately.','All 165 participants retained.','Masked assessment and sham participant masking for selected sham contrasts.')
p('Ntritsou 2014','SSHHS','Computer randomization; concealment controlled by department director but implementation insufficiently detailed.','Clinical staff aware; differential titration/co-intervention concerns.','5/75 excluded with insufficient reasons; missing clinician-titrated dose potentially informative.','Remifentanil is objective once delivered but dose is actively determined by an unblinded anaesthetist and likely influenced.')
# Missingness in Ntritsou is uncertain rather than demonstrated substantial bias.
P['Ntritsou 2014']=('SSSHS',P['Ntritsou 2014'][1])
p('Oztas 2019','SSLHS','Web block randomization; concealment not established.','Patients/data collector unblinded; rescue management may differ in both usual-care and active-TENS comparisons.','One off-protocol drug exclusion; small missing fraction.','Rescue pethidine depends on unblinded clinical decisions and pain reports; likely influenced, even though delivered milligrams are recorded.')
p('Pan 2023','SSHLS','Random grouping reported, allocation concealment insufficiently documented.','No credible stimulation sham; protocol-deviation exclusions and possible differential care.','Fig 3 (PDF p5): 60/60 allocated before exclusions for external analgesia, PCIA and surgery changes. 105 analysed; arm exclusion sums conflict with final 52/53. Informative missingness likely.','Observable vomiting recorded; clinician-determined remifentanil assessed separately.')
p('Seevaunnamtum 2016','SLLLS','Computer-generated randomization; concealment not fully described.','EA begun under general anaesthesia; patients and postoperative assessors masked despite usual-care classification.','64/64 retained.','Objective recorded postoperative PCA morphine with masked patients/assessors.')
p('Song 2020','LLLLS','Computer randomization and opaque envelopes.','Active non-acupoint current preserves sensory masking; not an inert sham comparator.','85/85 retained.','Masked symptom assessment with matched active-current control.')
p('Sun 2017','LLSLS','Computer sequence in opaque envelopes, operator alone aware.','Patients, anaesthetists and evaluators masked with minimal-sensation sham.','19/380 losses include changed surgery, prolonged operation and complications; GI-related missingness possible.','Masked patient/event recording for all three timing-arm comparisons.')
p('Szmit 2021','LLLLS','Independent statistician computer block sequence and independent allocation.','Sham procedure preserves patient masking; no evidence of material differential care; no-stimulation arm considered separately.','71/71 across three arms retained.','PCA log records actual morphine; patient demand is part of the assignment effect, not automatically measurement bias.')
p('Wang 2023','LLSLS','Computer sequence and sequential opaque envelopes.','Broad patient and assessor masking.','5/88 protocol-breach exclusions rather than full ITT; recovery-related missingness cannot be ruled out.','Masked flatus report collection.')
p('Wong 2006','SLHLS','Sequence/concealment insufficiently detailed.','Blunt sham and opaque shielding; patients and surgeons masked.','2/27 postoperative-complication exclusions could have substantially different morphine requirements in this very small trial.','Recorded three-day PCA morphine with participant masking.')
p('Wu 2022','SLSLS','Computer sequence; concealment insufficiently documented.','Opaque shielding and masked clinical/research team.','6/90 omitted (five controls, one active), including complications/incomplete data after intraoperative outcome was obtained.','Recorded remifentanil under clinician masking.')
p('Wu 2025','LLLLS','Independent computer-generated randomization on PACU arrival.','Outcome occurred before randomization/treatment: no post-assignment deviations can affect it.','100/100 analysed.','Recorded pre-intervention intraoperative dose. This is NOT a causal efficacy outcome of subsequent PACU treatment; retained only as diagnostic.')
p('Xing 2022','LLSLS','Computer sequence, sealed allocation relayed by independent nurse.','Opaque shielding and masked clinicians; equal TAP intervention.','One loss per selected 30-patient arm; loss-to-follow-up explanation insufficient to exclude pain/recovery association.','Masked clinicians record dose; possible awake sensory unmasking affects subjective pain/flatus separately.')
p('Xiong 2021','SS LSS'.replace(' ',''),'Computer sequence in sealed envelopes; opacity/sequential safeguards not fully documented.','Anaesthetists aware; co-intervention concerns despite masked postoperative resident.','67 screened, five excluded BEFORE allocation; all 62 randomized analysed.','No-current sham and possible postoperative tingling; incomplete sensory masking for nausea-containing composite.')
p('Yang 2020','SSLSS','SPSS sequence in sealed envelopes; opacity and recruiter independence not adequately detailed.','Participants/provider unblinded, anaesthetists/assessors masked; possible differential recovery care.','Two omissions from 59 (one no PVB, one preoperative withdrawal); limited missingness.','Open-label patient reporting may affect nausea and GI times; observed vomiting considered separately.')
p('Yang 2024','LSLHS','Computer sequence and sequentially numbered opaque sealed envelopes.','Open participant treatment with masked outcome staff; recovery behaviour and laxative co-interventions require caution.','180 ITT participants with three withdrawals; little missing outcome information.','Patient-reported flatus/defecation likely influenced by awareness; 72h laxative rule particularly relevant to defecation. Symptom-specific ratings below.')
p('Yao 2015','LLSLS','Computer sequence and sequentially numbered opaque envelopes.','Patients, anaesthetists, surgeons, nurses and collectors masked.','3/74 omitted for protocol breach; nature not sufficient to establish absence of symptom-related missingness.','Masked postoperative nausea/vomiting collection.')
p('Yu 2020','SLLLS','Computer table and nurse allocation; concealment safeguards insufficiently detailed.','Only acupuncturist informed, gel electrodes in same setting; clinical staff and participants masked.','60/60 retained.','Blinded collector BN administered questionnaires and collected outcomes.')
p('Zheng 2025','LSSLS','Seeded random allocation and sequential opaque envelopes. Equal 44/44 allocation is possible by chance and is NOT evidence of faulty randomization.','Anaesthetists not masked; possible dose/co-intervention differences.','3/88 excluded for surgical changes/prolonged operation, potentially informative for GI recovery/dose.','Patient and outcome-assessor masking; continuous outcome-specific measurement problems handled below.')
p('Zhou 2025','LLLLS','Computer sequence and sequential opaque sealed envelopes.','Patient and assessor masking with scripted practitioner interaction.','3/100 missing; little missing information and no documented differential outcome-related attrition.','Masked PONV and flatus collection.')
p('Zhu 2022','SSLSS','Computer sequence in opaque envelopes, but patient envelope selection leaves sequence implementation concerns.','Usual-care participants unblinded; recovery care/reporting could differ.','13/413 omitted; limited fraction; reported EM handling, but complete-case denominators used here.','Nausea/flatus self-reports potentially influenced by awareness; vomiting and clinician-masked dose separately rated.')
OV={}
def override(ids,domain,rating,reason):
    for rid in ids.split('|'): OV.setdefault(rid,{})[domain]=(rating,reason)
override('V33-OD-0239|V33-OD-0240',4,'S','Patients not blinded; self-reported first flatus/defecation can be influenced despite blinded assessor.')
override('V33-OD-0277|AUDIT-0294|AUDIT-0295|V33-OD-0140|AUDIT-0078|V33-OD-0055|V33-OD-0020|V33-OD-0022|V33-OD-0024',4,'L','Observable vomiting with common ascertainment; no evidence that knowledge of assignment materially altered measurement. Not equated to subjective nausea.')
override('V33-OD-0128|V33-OD-0129',2,'L','Anaesthesia team masked with opaque shielding; standard titration and no demonstrated deviations.')
override('V33-OD-0128|V33-OD-0129|V33-OD-0376|V33-OD-0377|V33-OD-0378',4,'L','Objective intraoperative dose recorded by masked anaesthesia team; each active arm linked separately.')
override('V33-OD-0135',4,'L','Observable bowel motion collected by masked observer; less susceptible than first flatus.')
override('V33-OD-0116|V33-OD-0351',2,'S','No-treatment comparator lacks participant masking; possible differential care, without automatic High rating merely for awareness.')
override('V33-OD-0116',4,'S','No-acupuncture participants know assignment; bowel-motion reporting may be influenced despite masked assessor.')
override('V33-OD-0379',4,'H','Unblinded/no-sham intraoperative setting; anaesthetist-titrated remifentanil likely affected by knowledge of treatment. Generic double-blind wording does not establish anaesthetist masking.')
override('V33-OD-0062|V33-OD-0064',4,'S','Authors acknowledge possible sensory unmasking during awake pre-induction stimulation; subjective pain/flatus may be influenced, but likelihood insufficient for High.')
override('V34-OD-0759',4,'S','Unblinded patient reporting of nausea may be influenced; not conflated with observed vomiting or bowel-timing judgment.')
override('AUDIT-0346',4,'S','Bowel-sound timing/assessment schedule insufficiently clear. SD/P inconsistency is a separate source-validity hold, not automatically a RoB domain.')
override('AUDIT-0347',4,'H','Reported flatus definition refers to stool, compromising the construct; no confident interpretation as first gas passage.')
override('V33-OD-0034',4,'H','Unblinded anaesthetist determines remifentanil titration; likely influenced by allocation.')
work=read('10_FINAL_ADJUDICATION/02_DECISIONS/v37/rob2_non_sensitivity_worklist.csv')
assert len(work)==94 and set(r['study'] for r in work)==set(P)
ratings={'L':'Low','S':'Some concerns','H':'High'}; assessments=[]; evidence=[]
for r in work:
    vector,reasons=P[r['study']]; vector=list(vector); reasons=list(reasons)+['Prospective result-level analysis plan not independently verified for this exact endpoint/window/contrast. Published outcome naming alone does not establish prespecification; no evidence sufficient to assert selective choice with High certainty.']
    if r['study']=='He 2026 (hepatectomy/JIS)':reasons[4]='Primary PONV outcome and analysis supported by available registered protocol/SAP and source supplement; no unexplained selection identified.'
    for dom,(rating,reason) in OV.get(r['result_id'],{}).items():vector[dom-1]=rating;reasons[dom-1]=reason
    assert len(vector)==5
    overall='High' if 'H' in vector else ('Some concerns' if 'S' in vector else 'Low')
    s=S[r['study']]; text=(ROOT/s['source_text']).read_text(); lines=text.splitlines()
    z=dict(assessment_id='V38-'+r['result_id'],result_id=r['result_id'],study=r['study'],outcome=r['outcome'],window=r['window'],comparison=r['intervention']+' vs '+r['comparator'],population=r['n_i']+'/'+r['n_c'],**{f'd{i+1}':ratings[c] for i,c in enumerate(vector)},overall=overall,**{f'd{i+1}_rationale':q for i,q in enumerate(reasons)},overall_rationale='High in at least one domain.' if overall=='High' else ('Residual concerns do not jointly establish likely material bias sufficient for High; do not mechanically count concerns.' if overall=='Some concerns' else 'No important domain concern identified for this result.'),reviewer='AI assistant under user delegation',review_date='2026-09-20',effect_of_interest='Effect of assignment to intervention',source_pdf=s['source_pdf'],source_sha256=s['source_sha256'],source_text=s['source_text'],result_location=r['source_location'],source='10_FINAL_ADJUDICATION/02_DECISIONS/v38/rob2_assessments.csv#V38-'+r['result_id'],provenance='Fresh v38 source-based domain assessment; supersedes conflicting historical selection for this exact result. Prior human completion is user-reported, not independently signed here.',human_signoff_date='USER REPORTS PRIOR REVIEW COMPLETE; new judgment AI-conducted')
    assessments.append(z)
    # Reproducible text locators support inspection; not an automated rating rule.
    for i,line in enumerate(lines):
        if re.search(r'random|envelope|conceal|blind|withdraw|exclu|intention|protocol|registr|missing',line,re.I):
            evidence.append(dict(assessment_id=z['assessment_id'],study=r['study'],source_text=s['source_text'],line=i+1,excerpt=' '.join(lines[max(0,i-1):i+3])))
save(OUT/'rob2_assessments.csv',assessments);save(OUT/'rob2_source_locators.csv',evidence)
# Full-text record reconciliation, retaining every original exported decision.
cross=read('10_FINAL_ADJUDICATION/02_DECISIONS/covidence_record_crosswalk.csv')
doi_groups=collections.defaultdict(list)
for r in cross:
 if r['doi'].strip():doi_groups[r['doi'].strip().lower()].append(r)
duplicates={};duplicate_register=[]
for doi,group in doi_groups.items():
 if len(group)<2:continue
 titles={re.sub(r'[\W_]+',' ',html.unescape(r['title']).lower()).strip() for r in group}
 assert len(titles)==1,(doi,titles)
 keep=min(group,key=lambda r:int(r['covidence_id']))
 for r in group:
  if r is keep:continue
  duplicates[r['covidence_id']]=keep['covidence_id']
  duplicate_register.append(dict(duplicate_record=r['covidence_id'],retained_record=keep['covidence_id'],doi=doi,title=keep['title'],duplicate_original_reason=r['exclusion_reason'],retained_original_reason=keep['exclusion_reason'],reason_conflict=r['exclusion_reason']!=keep['exclusion_reason'],basis='Same normalized DOI and title. Lowest Covidence ID retained as administrative count convention, not a clinical validation of exclusion.'))
assert len(duplicates)==6
save(OUT/'late_duplicate_register.csv',duplicate_register)
reinstated={'1879896511','1879897042','1879896727','1879896637','1879896624','1879896808'}
ledger=[]
for r in cross:
    z=dict(r); cid=r['covidence_id']; status=r['covidence_decision']; reason=r['exclusion_reason']
    if cid in reinstated: status='INCLUDED'; reason=''; basis='v38 delegated adjudication adopts source-verified eligible canonical report; original exclusion preserved.'
    elif cid in duplicates:status='DUPLICATE';reason='Duplicate record identified at full-text reconciliation';basis='Same DOI and normalized title as '+duplicates[cid]+'. Late removal; do not rewrite historical early dedup count.'
    elif cid=='1882881336': status='EXCLUDED';reason='Abstract only';basis='Related Zhang2018 conference abstract, distinct DOI 10.1111/1751-2980.12664 (Crossref: Posters, J Digestive Diseases19 S1 pp12–48). Not an exact duplicate publication; retained abstract-only exclusion, not another included trial.'
    elif reason=='Study not retrieved':status='NOT RETRIEVED';basis='Saved export records nonretrieval; not a full-text exclusion.'
    else:basis='Retained exported disposition; no new exclusion re-screening requested.'
    if reason=='Wrong outcomes':reason='no perioperative analgesia outcome found'
    z.update(route='DATABASE',final_disposition=status,final_reason=reason,duplicate_of=duplicates.get(cid,''),decision_basis=basis,adjudication_date='2026-09-20');ledger.append(z)
z={k:'' for k in ledger[0]};z.update(covidence_id='CITATION-WU2016',covidence_study_id='Wu 2016',registry_report='Wu 2016',route='CITATION SEARCH',final_disposition='INCLUDED',decision_basis='Citation-search discovery confirmed by user on 2026-09-20; historical discovery date not invented.',adjudication_date='2026-09-20');ledger.append(z)
assert len(ledger)==225
db=[r for r in ledger if r['route']=='DATABASE'];counts=collections.Counter(r['final_disposition'] for r in db);reasons=collections.Counter(r['final_reason'] for r in db if r['final_disposition']=='EXCLUDED')
assert counts=={'INCLUDED':69,'EXCLUDED':147,'NOT RETRIEVED':2,'DUPLICATE':6},counts
assert reasons['no perioperative analgesia outcome found']==113
save(OUT/'prisma_record_ledger.csv',ledger)
prisma=dict(version='v38',date='2026-09-20',databases={'Embase':1928,'CENTRAL':1698,'CINAHL':465,'PubMed':1009},references=5100,reported_import_records=5088,unmapped_import_difference=12,automatic_duplicates=1651,manual_duplicates=1,automation_exclusions=508,screened=2928,title_abstract_excluded=2704,database_sought=224,database_not_retrieved=2,database_assessed_records=222,late_duplicates=6,database_assessed=216,database_excluded=147,database_included=69,citation_sought=1,citation_assessed=1,citation_included=1,included_reports=70,operational_trial_families=69,exclusion_reasons=dict(reasons),caveats=['The 12-reference difference between raw RIS exports and reported imports is an unmapped historical import/consolidation gap, not 12 verified duplicate removals.','Upstream 5088/1651/1/508/2928/2704 counts are historical aggregate figures, not a replayed record-level deduplication log.','Six exact DOI/title duplicates identified late: Chung, Tian, Tong, Tu, Wang and Yang. Lowest-ID record retained for count convention; Tu records conflict on outcome versus intervention reason, and that clinical exclusion rationale is not newly validated.','Zhang2018 conference abstract has a distinct DOI and remains Abstract only, not an exact duplicate publication.','The requested outcome-exclusion label preserves historical dispositions; it is not a fresh proof that all excluded articles lack every protocol-eligible outcome.','Yeh 2010/2011 remain one probable overlapping family for operational counting; both are held out of models.'])
(OUT/'prisma_counts.json').write_text(json.dumps(prisma,indent=2)+'\n')
print('v38 assessments',len(assessments),collections.Counter(a['overall'] for a in assessments));print('PRISMA',counts,reasons)
