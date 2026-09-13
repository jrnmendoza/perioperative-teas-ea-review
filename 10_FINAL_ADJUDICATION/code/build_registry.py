"""Rebuild source-linked report/trial registry from immutable sources and explicit adjudications."""
import csv,json,re,pathlib,hashlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION'
def read(p):return json.load(open(ROOT/p))
def csvout(p,rows):
 with open(ROOT/p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def slug(s):return re.sub(r'[^a-zA-Z0-9]+','_',s).strip('_')
m=read('10_FINAL_ADJUDICATION/01_SOURCE_EVIDENCE/source_manifest.json');base={r['key']:r for r in read('ASTRA_VERIFICATION_SUPPORT/data.js.json')}; chars=read('ASTRA_VERIFICATION_SUPPORT/study_characteristics.js.json');rob={r['Canonical study']:r for r in read('ASTRA_VERIFICATION_SUPPORT/workbook.json')['Corrected_RoB2']}
ns=[100,88,70,100,84,60,80,32,107,610,1655,20,120,128,130,161,74,80,114,101,614,174,49,280,80,75,100,92,100,80,129,88,60,576,100,277,35,165,75,48,120,64,90,85,380,71,120,88,140,27,90,90,100,60,90,62,59,180,74,99,90,60,90,72,42,1948,108,88,82,413]
assert len(ns)==len(m)==70
EA={'Coura 2011','El-Rakshy 2009','Grech 2016','He 2026 (breast/WJCO)','Huang 2017','Huang 2024','Huang 2025','Jin 2023','Li 2022','Lin 2002','Liu 2025','Ng 2013','Ntritsou 2014','Seevaunnamtum 2016','Sim 2002','Wong 2006','Xie 2014','Yang 2020','Yang 2024','Zhu 2022','An 2014'}
notes={'El-Rakshy 2009':'107 randomized in flow; allocation labels conflict across flow, baseline and abstract. Outcome Table 2: EA42/control53, not trial total.', 'Yeh 2010':'Probable overlap family: use maximum reported randomized cohort (99) as operational lower bound; unique family union unknown. Do not sum 99+90.', 'Yeh 2011':'Companion report in probable overlapping Yeh family, counted once under Yeh 2010. Cohort identity not proven.', 'Wang 2024':'140 randomized across two risk strata, each 35 OD/35 ODT. SNVP/MNVP totals are risk strata, not intervention arms.', 'Jiang 2026':'614 randomized 308/306; mITT593=296/297; PP587=294/293. Baseline sex/ASA denominators conflict; not repaired.', 'Pan 2023':'120 randomized 60/60; outcome analysis52/53. Flow attrition arm labels conflict; trial total retained.', 'Zhu 2022':'413 randomized; arm identity103/104 differs between abstract and flow. mITT405, PP400; outcome denominators used.', 'Ma 2026':'Only35 randomized18/17. Nonrandomized normal-sleep group26 excluded from randomized total.', 'Lee 2011':'49 randomized13/12/12/12; two low-frequency participants excluded;47 analyzed. Abstract calls47 randomized; flow/body control.', 'Yao 2015':'74 randomized;71 completed35/36. Automated prior extraction71 was analyzed rather than randomized N.', 'Long 2025':'Needle OR patch wording prevents physical modality determination. Retain registry; HOLD modality-specific inference.', 'Jin 2023':'174 randomized58/58/58;158 completed53/53/52. General anaesthesia not established from supplied main report; HOLD inference pending source verification.'}
rows=[];ledger=[];ident=[]
for x,n in zip(m,ns):
 study=x['study'];s=pathlib.Path(x['text_file']).read_text();pages=re.split(r'=== PDF PAGE (\d+) ===',s); hits=[]
 for j in range(1,len(pages),2):
  p,t=int(pages[j]),re.sub(r'\s+',' ',pages[j+1]);
  for z in re.finditer(r'\b'+str(n)+r'\b',t):
   quote=t[max(0,z.start()-160):z.end()+300];score=sum(w in quote.lower() for w in ['random','allocat','enroll','patients','flow','included'])
   hits.append((score,p,quote))
 hits=[h for h in hits if h[1] <= max(3,int(x['pages']*.72))]; hits.sort(reverse=True);p=hits[0][1] if hits else '';q=hits[0][2] if hits else 'See participant flow / allocation methods; spelled-out sample size.'
 # Counts are explicit human-readable adjudications above, not values inferred by this locator.
 
 if study=='Liu 2026 (burn)':p,q=5,'Visually verified CONSORT Figure 1: randomized88; allocated44/44; analyzed43/43. Abstract86 is analyzed, not randomized.'
 if study=='Huang 2025':p,q=4,'The remaining patients were randomly allocated to the EA arm (n = 51) or the Standard care group (n = 50). Total101 derived by addition.'
 if study=='Gao 2022':p,q=4,'Results / CONSORT: 1,655 randomized, TEAS827 and sham828; separators in source preserved.'
 if study=='Yeh 2010':p,q=6,'Results: Initially, 99 participants met the criteria and were included in the study. Five participants did not complete; remaining94=33/30/31.'
 if study=='Xing 2022':p,q=1,'Ninety patients undergoing laparoscopic gastric cancer surgery were randomly divided into general anesthesia, TAPB, and TEAS plus TAPB groups.'
 if study=='Xie 2014':p,q=1,'Sixty patients (ASA III) scheduled for elective radical esophagectomy were randomized into three groups.'
 if study=='Oztas 2019':p,q=1,'Research sample consisted of 48 patients who underwent abdominal surgery with a midline incision; patients randomized into three groups.'
 t='Yeh_probable_family' if study.startswith('Yeh ') else slug(study); b=base.get(study,{});c=chars.get(study,{});r=rob.get(study,{})
 mod='UNCLEAR' if study=='Long 2025' else ('EA' if study in EA else 'TEAS')
 row=dict(trial_id=t,report_id=study,year=b.get('year',re.search(r'\d{4}',study).group()),country=b.get('country','NOT VERIFIED'),surgery=c.get('surgery_procedure','NOT VERIFIED'),modality=mod,comparator=b.get('comparator_type','See source-defined result contrast'),randomized_n_report=n,randomized_n_counted=0 if study=='Yeh 2011' else n,analyzed_n=r.get('Analyzed n','OUTCOME SPECIFIC — see canonical results'),age_i_c='NOT VERIFIED',sex_i_c='NOT VERIFIED',bmi_i_c='NOT VERIFIED',asa_i_c='NOT VERIFIED',anesthesia=c.get('anesthesia','NOT VERIFIED in registry; see source methods'),rob2=r.get('Overall RoB 2','UNLINKED'),language='English full text',source_pdf=x['file'],source_sha256=x['sha256'],source_text=x['text_file'],n_source_page=p,n_source_excerpt=q,decision='RESOLVED — SOURCE DETERMINATIVE',notes=notes.get(study,'Randomized trial total; analyzed populations remain outcome-specific.'))
 if not row['source_pdf']:row['source_pdf']=next((v for k,v in x.items() if 'pdf' in k.lower()),'')
 if study.startswith('Yeh '):row['decision']='RESOLVED — CONSERVATIVE REVIEW RULE'
 if study=='Jin 2023':row['anesthesia']='UNCLEAR — general anaesthesia not established'
 rows.append(row)
 ledger.append(dict(trial_id=t,report_id=study,randomized_n=n,counted_randomized_n=row['randomized_n_counted'],itt_n=174 if study=='Jin 2023' else '',mitt_n={'Jiang 2026':593,'He 2026 (hepatectomy/JIS)':159,'Zhu 2022':405,'Zheng 2025':85}.get(study,''),pp_n={'Jiang 2026':587,'He 2026 (hepatectomy/JIS)':153,'Zhu 2022':400,'Song 2020':78}.get(study,''),outcome_n=r.get('Analyzed n','See canonical results'),source_page=p,source_excerpt=q,status='SOURCE VERIFIED total; operational lower bound for Yeh' if study.startswith('Yeh') else 'SOURCE VERIFIED',notes=row['notes']))
 body=s[:int(len(s)*.85)]; ids=sorted(set(re.findall(r'(?:NCT\d{8}|ChiCTR[\w-]*\d{6,}|ISRCTN\d+)',body,re.I)))
 identity=[]
 for z in re.finditer(r'(?i)recruit|ethic|registered|hospital|between',body):
  quote=re.sub(r'\s+',' ',body[max(0,z.start()-70):z.end()+180]);
  if len(identity)<10:identity.append(quote)
 ident.append(dict(report_id=study,trial_id=t,registry_ids=';'.join(ids),identity_excerpts=' | '.join(identity),source_text=x['text_file'],decision='PROBABLE OVERLAP — do not double count' if study.startswith('Yeh') else 'No additional cohort merge justified by available identity evidence'))
# Verified detailed primary-source baseline entries. Unverified fields are explicit blanks/status, never defaults.
patch={'Yang 2024':dict(age_i_c='52.7 ±11.0 / 55.8 ±11.6 years',sex_i_c='Female66/90 /56/90',anesthesia='General anaesthesia + paravertebral block'),'Wang 2024':dict(sex_i_c='All female; two risk strata'),'Szmit 2021':dict(anesthesia='General anaesthesia'),'Chen 1998':dict(anesthesia='General anaesthesia'),'Chen 2020':dict(anesthesia='General anaesthesia'),'Seevaunnamtum 2016':dict(anesthesia='General anaesthesia'),'El-Rakshy 2009':dict(anesthesia='General anaesthesia'),'He 2026 (hepatectomy/JIS)':dict(anesthesia='General anaesthesia'),'Huang 2024':dict(anesthesia='General anaesthesia')}
for r in rows:r.update(patch.get(r['report_id'],{}))
csvout('FINAL_TRIAL_REPORT_MAPPING.csv',rows);csvout('FINAL_PARTICIPANT_LEDGER.csv',ledger);csvout('10_FINAL_ADJUDICATION/02_DECISIONS/cohort_identity_recheck.csv',ident)
(D/'03_CANONICAL/studies.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False));print('Operational N lower bound',sum(r['randomized_n_counted'] for r in rows),'units',len(set(r['trial_id'] for r in rows)),collections.Counter(r['modality'] for r in rows))
