"""Manual source-fact signalling record accompanying v38 domain judgments.

Answers are authored from methods, flow and outcome assessment, not inferred
backwards from final domain ratings. Short labels are not the official form.
No claim of independent assessors or validated RoB2-software execution.
"""
import csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'10_FINAL_ADJUDICATION';O=D/'02_DECISIONS/v38'
rows=list(csv.DictReader(open(O/'rob2_assessments.csv')))
Q={'1.1':'Random sequence?','1.2':'Concealed allocation?','1.3':'Baseline pattern suggests randomization failure?',
 '2.1':'Participant aware?','2.2':'Care personnel aware?','2.3':'Trial-context deviations?','2.4':'Deviations affect outcome?','2.5':'Deviations balanced?','2.6':'Assignment-effect analysis appropriate?','2.7':'Analysis departure materially consequential?',
 '3.1':'All or nearly all outcome data?','3.2':'Evidence missingness does not bias result?','3.3':'Missingness could depend on outcome?','3.4':'Such dependence likely?',
 '4.1':'Measurement method inappropriate?','4.2':'Measurement differs between arms?','4.3':'Outcome assessor aware?','4.4':'Awareness could influence measurement?','4.5':'Influence likely?',
 '5.1':'Prospective analysis plan verified?','5.2':'Result selected from multiple measurements?','5.3':'Result selected from multiple analyses?'}
# Explicit allocation facts: sequence/concealment/baseline signal.
A={}
for names,value in [
 ('An 2014|El-Rakshy 2009|Gu 2019|Liu 2021|Ntritsou 2014|Oztas 2019|Seevaunnamtum 2016|Wu 2022|Xiong 2021|Yang 2020|Yu 2020','Y NI PN'),
 ('Chen 2015|Chen 2015 (Hyperalgesia)|Gao 2021|Gao 2022|Guo 2023|He 2026 (hepatectomy/JIS)|Huang 2024|Huang 2025|Jiang 2026|Liang 2021|Liu 2015|Liu 2026 (burn)|Lu 2021|Lu 2022|Luo 2026|Song 2020|Sun 2017|Szmit 2021|Wang 2023|Wu 2025|Xing 2022|Yang 2024|Yao 2015|Zheng 2025|Zhou 2025','Y PY PN'),
 ('Ng 2013','Y N PN'),('Wong 2006','NI NI PN'),('Pan 2023','PY NI PN'),('Zhu 2022','Y NI PN')]:
 for name in names.split('|'):A[name]=value.split()
# Awareness/deviations are answered from masking/care descriptions; lack of a
# sham is not automatically awareness during general anaesthesia.
B={}
for names,value in [
 ('An 2014|Chen 2015|Chen 2015 (Hyperalgesia)|Gu 2019|Guo 2023|He 2026 (hepatectomy/JIS)|Jiang 2026|Liu 2015|Liu 2026 (burn)|Song 2020|Sun 2017|Wang 2023|Wong 2006|Wu 2022|Yao 2015|Yu 2020|Zhou 2025','PN PN NA NA NA PY NA'),
 ('Liang 2021|Seevaunnamtum 2016','PN PN NA NA NA PY NA'),
 ('Huang 2024|Xing 2022','PY PN PN NA NA PY NA'),
 ('Szmit 2021|Ng 2013','PN PY PN NA NA Y NA'),
 ('Gao 2021|Gao 2022|Huang 2025|Lu 2021|Lu 2022|Yang 2020|Yang 2024|Zhu 2022','PY PY NI NI NI PY NA'),
 ('El-Rakshy 2009|Ntritsou 2014|Oztas 2019|Pan 2023','PY Y NI NI NI PY NA'),
 ('Liu 2021|Xiong 2021|Zheng 2025','NI PY NI NI NI PY NA'),
 ('Luo 2026','Y Y NI NI NI Y NA'),
 ('Wu 2025','N N NA NA NA Y NA')]:
 for name in names.split('|'):B[name]=value.split()
assert set(A)==set(B)=={r['study'] for r in rows}
# Outcome-data availability judged in context, not via a fixed percentage rule.
missing_uncertain={'Guo 2023','Huang 2024','Huang 2025','Jiang 2026','Liang 2021','Liu 2015','Lu 2022','Ntritsou 2014','Sun 2017','Wang 2023','Wu 2022','Xing 2022','Yao 2015','Zheng 2025'}
missing_likely={'An 2014','El-Rakshy 2009','Pan 2023','Wong 2006'}
# Explicitly named subjective/awareness affected measurements.
aware_possible=set('V33-OD-0239 V33-OD-0240 V33-OD-0276 V33-OD-0278 V33-OD-0201 V33-OD-0202 V33-OD-0163 V33-OD-0164 AUDIT-0292 AUDIT-0293 V33-OD-0130 V33-OD-0131 V33-OD-0134 V33-OD-0116 V33-OD-0062 V33-OD-0064 V33-OD-0056 AUDIT-0077 V33-OD-0002 V33-OD-0380 V34-OD-0759 AUDIT-0017 AUDIT-0018 AUDIT-0019 V33-OD-0019 V33-OD-0021 V33-OD-0023'.split())
aware_likely=set('V33-OD-0198 V33-OD-0199 V33-OD-0139 V33-OD-0112 V33-OD-0303 V33-OD-0304 V33-OD-0379 V33-OD-0053 V33-OD-0054 V33-OD-0034'.split())
out=[]
for r in rows:
 rid=r['result_id'];s=r['study'];answers={}
 groups={1:A[s],2:B[s],3:('PN NI PY PY' if s in missing_likely else 'PN NI PY NI' if s in missing_uncertain else 'PY NA NA NA').split(),4:'PN PN PN NA NA'.split(),5:('Y PN PN' if s=='He 2026 (hepatectomy/JIS)' else 'NI PN PN').split()}
 if rid in aware_possible:groups[4]='PN PN PY Y NI'.split()
 if rid in aware_likely:groups[4]='PN PN Y Y PY'.split()
 if rid=='AUDIT-0346':groups[4]='NI PN PN NA NA'.split()
 if rid=='AUDIT-0347':groups[4]='Y PN PN NA NA'.split()
 if rid in ('V33-OD-0116','V33-OD-0351'):groups[2]='Y PY NI NI NI Y NA'.split()
 if rid in ('V33-OD-0128','V33-OD-0129'):groups[2]='PY PN PN NA NA Y NA'.split()
 for domain,values in groups.items():
  for i,value in enumerate(values,1):answers[f'{domain}.{i}']=value
 assert set(answers)==set(Q)
 for q,answer in answers.items():
  dom=q[0];out.append(dict(assessment_id=r['assessment_id'],result_id=rid,study=s,question_id=q,short_question=Q[q],answer=answer,justification=r['d'+dom+'_rationale'],final_domain_judgment=r['d'+dom],judgment_basis='Manual source-informed assessment; see domain rationale for uncertainty/author judgment. Not a software-generated rating.',source_text=r['source_text'],source_pdf=r['source_pdf'],result_location=r['result_location'],reviewer=r['reviewer'],review_date=r['review_date']))
with open(O/'rob2_signalling_questions.csv','w',newline='') as f:w=csv.DictWriter(f,list(out[0]));w.writeheader();w.writerows(out)
(O/'ROB2_METHOD.md').write_text('''# v38 result-specific risk-of-bias method

94 assessments cover every component of all 38 non-sensitivity evidence bodies before the v38 membership changes. After four continuous/pre-intervention results were held, all 90 current components remain covered. Other canonical/sensitivity-only results are not asserted to have fresh completed assessment.

The target is assignment to intervention. The 22 signalling responses per assessment use Y / PY / PN / N / NI / NA (yes / probably yes / probably no / no / no information / not applicable). Short question labels are paraphrases, not a verbatim official form. Responses are authored from source methods, allocation flow and result ascertainment; domain ratings are manual judgments, not claimed output from validated RoB software. NI denotes insufficient information, not proof of misconduct or bias.

The exact outcome, arm comparison, population, timepoint, source PDF/hash and result location are recorded. Domain rationales accompany every response; additional source-text line locators are in rob2_source_locators.csv. Shared design facts are reused explicitly; outcome- and arm-dependent answers are separately adjudicated. No human names, signatures or second independent assessment are invented. The user reports previous human review complete; these new assessments are AI-conducted under delegation.

Materiality decisions: awareness does not itself establish trial-context deviation or High D2. Incomplete follow-up is assessed for relation to the outcome, not a universal attrition cutoff. Informative removal of postoperative complications is not excused as unrelated to acupuncture. Subjective nausea/pain/flatus and clinician-titrated dose differ from masked observable vomiting or logged PCA exposure. Lack of a verified prospective analysis plan usually warrants Some concerns, not automatic High. Multiple Some concerns were considered jointly, not mechanically promoted by counting domains; final overall rationale is recorded.

Source holds (e.g., inconsistent SD/P or pre-treatment outcomes) concern interpretability/eligibility as well as RoB and are not resolved by assigning a bias rating. Wu2025 intraoperative-dose assessment concerns a baseline/negative-control contrast, not efficacy of the subsequent treatment.

Guidance: https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-08
''')
print('v38 signalling responses',len(out),'for',len(rows),'assessments')
