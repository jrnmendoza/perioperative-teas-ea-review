import json,pathlib,concurrent.futures,urllib.request,re,hashlib
import fitz
root=pathlib.Path(__file__).resolve().parents[2]; out=root/'10_FINAL_ADJUDICATION/01_SOURCE_EVIDENCE/exclusions';out.mkdir(exist_ok=True)
rows=json.load(open(root/'covidence_all_161_excluded.json'))
def one(r):
 k=str(r['id']); p=out/(k+'.pdf');z={'id':k,'study':r['study_id'],'title':r['title'],'reason':r['exclusion_reason'],'excluded_on':r['excluded_on']}
 refs=r.get('references',[]);url=next((x.get('path_to_fulltext') for x in refs if x.get('path_to_fulltext')),'')
 z['doi']=';'.join(x.get('doi','') or '' for x in refs);z['abstract']=r.get('abstract','')
 if url:
  try:
   if not p.exists():
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'});b=urllib.request.urlopen(req,timeout=25).read()
    if not b.startswith(b'%PDF'):raise ValueError('Not PDF')
    p.write_bytes(b)
   doc=fitz.open(p);s='\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+d.get_text() for i,d in enumerate(doc));(out/(k+'.txt')).write_text(s)
   z.update(status='RETRIEVED',pages=len(doc),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),text_file=str((out/(k+'.txt')).relative_to(root)))
  except Exception as e:z['status']=type(e).__name__
 else:z['status']='NO FULLTEXT LINK IN EXPORT'
 return z
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:res=list(pool.map(one,rows))
(out/'manifest.json').write_text(json.dumps(res,indent=2,ensure_ascii=False))
from collections import Counter
print(Counter(r['status'] for r in res))
