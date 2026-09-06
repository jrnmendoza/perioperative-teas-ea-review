from pathlib import Path
import json, hashlib, re, datetime
import openpyxl
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
MASTER = PROJECT / 'TEAS_EA_RECONCILED_MASTER_DATA_v20_PRIMARY_OPIOID_SET.xlsx'
for sub in ['source_text','baseline','phase_a','adjudicated','ledger','qa','output']:
    (ROOT/sub).mkdir(parents=True,exist_ok=True)
def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str))
w=openpyxl.load_workbook(MASTER,read_only=True,data_only=True)
tables={}
for s in w:
    it=iter(s.values); headers=list(next(it)); tables[s.title]=[dict(zip(headers,r)) for r in it if any(v is not None for v in r)]
studies=[r['Canonical study'] for r in tables['Study_Master']]
roster=[]
for i,name in enumerate(studies,1):
    sid=f'S{i:03}'
    roster.append({'Study_ID':sid,'Study':name})
    relevant={k:[dict(_baseline_row=j+2,**r) for j,r in enumerate(v) if r.get('Canonical study')==name or r.get('Study unit')==name] for k,v in tables.items()}
    save(ROOT/'baseline'/f'{sid}.json',relevant)
    ledger=ROOT/'ledger'/f'{sid}.json'
    if not ledger.exists(): save(ledger,{'Study_ID':sid,'Study':name,'stage':'PENDING_SOURCE_REVIEW'})
save(ROOT/'roster.json',roster)
save(ROOT/'baseline'/'all_tables.json',tables)
manifest=[]
for path in sorted((PROJECT/'Source PDFs').glob('*.pdf')):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    r=PdfReader(path)
    pages=[p.extract_text(extraction_mode='layout') or '' for p in r.pages]
    dest=ROOT/'source_text'/(path.stem+'.txt')
    dest.write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)))
    manifest.append({'file':path.name,'path':str(path),'text_path':str(dest),'sha256':digest,'pages':len(pages),'first_page':pages[0][:1800] if pages else ''})
save(ROOT/'source_manifest.json',manifest)
save(ROOT/'run_manifest.json',{'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':str(MASTER),'baseline_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'studies':len(studies),'outcomes':len(tables['Outcome_Data']),'pdfs':len(manifest),'model_for_scientific_review':'gpt-6-astra','reasoning_effort':'high','blinding':'Baseline values withheld from source reviewers until phase_a file saved.'})
print(json.dumps({'studies':len(studies),'outcomes':len(tables['Outcome_Data']),'pdfs':len(manifest)}))
for p in manifest:
    print(p['file'], re.sub(r'\s+',' ',p['first_page'])[:260])
