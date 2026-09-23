"""Digitise Gu 2019 Fig. 4 (analgesic consumption, mL) from the hash-pinned source PDF.
Re-extracts the embedded image; the third-party image itself is not stored in the repository."""
import hashlib, json, sys, numpy as np, pymupdf
from PIL import Image
PDF="TEAS EA Verification/Source PDFs/covidence_1471_full_article.pdf"
SHA="b6fb0c0901f5f6716bd6cc6facc06f0844dca5c5e9d357527f55936d5de0aa33"
assert hashlib.sha256(open(PDF,"rb").read()).hexdigest()==SHA, "source PDF hash mismatch"
doc=pymupdf.open(PDF); pg=doc[3]
info=[i for i in pg.get_image_info(xrefs=True) if round(i["bbox"][1])==543][0]
pix=pymupdf.Pixmap(doc,info["xref"]); pix=pymupdf.Pixmap(pymupdf.csRGB,pix) if pix.n-pix.alpha>3 else pix
a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3].astype(int)
near=lambda c,t:(np.abs(a-np.array(c)).sum(axis=2)<t)
grey=near((217,217,217),45); H=a.shape[0]
rows=[y for y in range(H) if grey[y,120:980].sum()>300]; g=[]
for y in rows:
    (g[-1].append(y) if g and y-g[-1][-1]<=2 else g.append([y]))
gy=np.array([np.mean(x) for x in g]); gv=np.linspace(100,0,len(gy))
k,b=np.polyfit(gy,gv,1); val=lambda y:k*y+b
dark=(a.sum(axis=2)<330)
def clusters(m):
    cols=np.where(m[60:486].sum(axis=0)>20)[0]; out=[]
    for c in cols: (out[-1].append(c) if out and c-out[-1][-1]<=2 else out.append([c]))
    return [(o[0],o[-1]) for o in out if o[-1]-o[0]>15]
def run(y,cx,step):
    gap=0; last=y
    while 0<y<490:
        if dark[y,cx-2:cx+3].any(): last=y; gap=0
        else:
            gap+=1
            if gap>3: break
        y+=step
    return last
res={"axis":{"slope":k,"intercept":b,"gridlines":len(gy),"units_per_px":abs(k),
     "max_gridline_residual":float(max(abs(val(gy)-gv)))}}
for arm,col in (("C-TEAS",(68,114,196)),("L-TEAS",(237,125,49))):
    m=near(col,60)
    for i,(x0,x1) in enumerate(clusters(m)):
        top=int(np.min(np.where(m[:,x0+3:x1-3].any(axis=1))[0])); cx=(x0+x1)//2
        mean=val(top); su=val(run(top,cx,-1))-mean; sl=mean-val(run(top+2,cx,1))
        res.setdefault(arm,{})[f"T{i+1}"]=dict(mean=round(mean,2),sd_upper_whisker=round(su,2),
            sd_lower_whisker=round(sl,2),sd=round((su+sl)/2,2))
json.dump(res,sys.stdout,indent=1)
