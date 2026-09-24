"""Render a submission copy of the manuscript from the working drafts.
- Converts [@key; @key] placeholders to BMC numbered citations ([1], [2, 3], [4-6]) using
  references/bibliography.csv, and asserts numbering follows first appearance.
- Strips each section's draft-status note. Unresolved '[AUTHOR DECISION ...]' blocks are
  replaced by a visible placeholder and make the build NOT SUBMISSION-READY.
- Appends references/REFERENCES_BMC.md and writes a build report listing every gate.
The working drafts are never modified."""
import csv, re, pathlib, datetime, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; MS=ROOT/"manuscript"; OUT=MS/"submission"
SECTIONS=["ABSTRACT","INTRODUCTION","METHODS","RESULTS","DISCUSSION","CONCLUSIONS"]
BMC_REQUIRED=["Title page","Abstract","Keywords","Background","Methods","Results","Discussion","Conclusions",
              "Abbreviations","Declarations","References"]
bib={r["key"]:r for r in csv.DictReader(open(ROOT/"references/bibliography.csv",encoding="utf-8"))}
num={k:int(r["number"]) for k,r in bib.items()}
gates=[]; decisions=[]; unknown=[]; seen=[]

def compress(ns):
    ns=sorted(set(ns)); out=[]; i=0
    while i<len(ns):
        j=i
        while j+1<len(ns) and ns[j+1]==ns[j]+1: j+=1
        out.append(f"{ns[i]}–{ns[j]}" if j-i>=2 else ", ".join(str(n) for n in ns[i:j+1])); i=j+1
    return "["+", ".join(out)+"]"
def cite(m):
    keys=re.findall(r"@([A-Za-z0-9_:-]+)",m.group(1)); ns=[]
    for k in keys:
        if k not in num: unknown.append(k); continue
        ns.append(num[k])
        if num[k] not in seen: seen.append(num[k])
    return compress(ns) if ns else m.group(0)
def strip_and_gate(name,text):
    L=text.splitlines(); i=1; offset=0
    while i<len(L) and not L[i].startswith(">") and L[i].strip()=="": i+=1
    if i<len(L) and L[i].startswith(">"):          # leading draft-status note
        while i<len(L) and (L[i].startswith(">") or L[i].strip()==""): i+=1
        offset=i-2; L=[L[0],""]+L[i:]
    out=[]; k=0
    while k<len(L):
        if L[k].startswith(">"):
            blk=[]; start=k
            while k<len(L) and L[k].startswith(">"): blk.append(L[k]); k+=1
            joined=" ".join(b.lstrip("> ").strip() for b in blk)
            tag=re.match(r"\*\*\[([^\]]+)\]\*\*",joined)
            label=tag.group(1) if tag else "unlabelled blockquote"
            ln=start+1+(offset if start>=2 else 0)   # line number in the working draft
            decisions.append(f"{name}.md line {ln}: {label}")
            out.append(f"**[[UNRESOLVED — {label} — see {name}.md line {ln}]]**")
        else: out.append(L[k]); k+=1
    return "\n".join(out)
parts=[]; words={}
for s in SECTIONS:
    t=(MS/f"{s}.md").read_text(encoding="utf-8")
    t=strip_and_gate(s,t)
    t=re.sub(r"\[(@[^\]]+)\]",cite,t)
    body=[l for l in t.splitlines()[1:] if not l.startswith("#") and not l.startswith("**[[")]
    words[s]=len(re.sub(r"[*|`]"," ","\n".join(body)).split())
    parts.append(t.strip())
# numbering must follow first appearance in the rendered order
if seen!=list(range(1,len(seen)+1)): gates.append(f"Citation numbering does not follow first appearance: {seen}")
uncited=sorted(set(num.values())-set(seen))
if uncited: gates.append(f"References never cited in the rendered text: {uncited}")
if unknown: gates.append(f"Citation keys with no bibliography entry: {sorted(set(unknown))}")
if decisions: gates.append(f"{len(decisions)} unresolved author decision(s) in the text")
present={"Abstract","Background","Methods","Results","Discussion","Conclusions","References"}
missing=[x for x in BMC_REQUIRED if x not in present]
refs=(ROOT/"references/REFERENCES_BMC.md").read_text(encoding="utf-8")
reflist="\n".join(l for l in refs.splitlines() if re.match(r"^\d+\. ",l))
today=datetime.date.today().isoformat(); ready=not gates
OUT.mkdir(exist_ok=True)
doc=[f"<!-- RENDERED {today} by reports/render_submission.py from the working drafts. Do not edit; edit the drafts and re-render. Status: {'SUBMISSION-READY' if ready else 'NOT SUBMISSION-READY'} -->",""]
doc+=["\n\n".join(parts),"","# References","",reflist,""]
(OUT/"MANUSCRIPT_RENDERED.md").write_text("\n".join(doc),encoding="utf-8")
R=[f"# Render report — {today}","",f"**Status: {'SUBMISSION-READY' if ready else 'NOT SUBMISSION-READY'}**",""]
R+=["## Gates",""]+([f"- {g}" for g in gates] or ["- none"])+[""]
R+=["## Unresolved author decisions",""]+([f"- {d}" for d in decisions] or ["- none"])+[""]
R+=["## BMC sections not yet written (not a render failure)",""]+[f"- {m}" for m in missing]+[""]
R+=["## Citations",f"- {len(seen)} references cited, numbered 1–{len(seen)} by first appearance; list appended from `references/REFERENCES_BMC.md`.",""]
R+=["## Word counts (rendered, approximate)","","| Section | Words |","|---|---:|"]+[f"| {s.title()} | {words[s]} |" for s in SECTIONS]
(OUT/"RENDER_REPORT.md").write_text("\n".join(R)+"\n",encoding="utf-8")
print("\n".join(R)); sys.exit(0)
