"""Resolve every [@key] cited in the manuscript to an authoritative record (PubMed, else Crossref),
verify it against what the traceability records expect, and emit a BMC Vancouver list + RIS.
Nothing is taken from memory: identifiers come from the traceability records or from a
journal/year/volume/page search, and every field comes from the fetched record."""
import csv, json, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]; REF=ROOT/"references"; SRC=REF/"sources"
EU="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
def get(url):
    time.sleep(0.4)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"teas-ea-review-bibliography/1.0"}),timeout=30) as r: return r.read().decode("utf-8")
def esearch(term):
    d=json.loads(get(EU+"esearch.fcgi?db=pubmed&retmode=json&retmax=10&term="+urllib.parse.quote(term)))
    return d["esearchresult"]["idlist"]
# key -> how to find it, and what the traceability record expects (for verification)
SPEC={
 "weiser2015":      dict(pmid="26313057", exp=dict(journal="Lancet",year="2015",first="S11")),
 "gan2014":         dict(pmid="24237004", exp=dict(journal="Curr Med Res Opin",year="2014",vol="30",first="149")),
 "liu2023china":    dict(pmid="37927993", exp=dict(year="2023",vol="39",doi="10.1016/j.lanwpc.2023.100822")),
 "kehlet2003":      dict(pmid="14667752", exp=dict(journal="Lancet",year="2003",vol="362",first="1921")),
 "brummett2017":    dict(pmid="28403427", exp=dict(journal="JAMA Surg",year="2017",vol="152")),
 "frangakis2026":   dict(term="10.1136/rapm-2025-107296[aid]", doi="10.1136/rapm-2025-107296", exp=dict(year="2026",doi="10.1136/rapm-2025-107296")),
 "bologheanu2025":  dict(pmid="39976966", exp=dict(year="2025",vol="8",doi="10.1001/jamanetworkopen.2024.60794")),
 "lawal2020":       dict(pmid="32584407", exp=dict(year="2020",vol="3",doi="10.1001/jamanetworkopen.2020.7367")),
 "adams2023":       dict(pmid="37059626", exp=dict(year="2023",vol="130",first="709",doi="10.1016/j.bja.2023.02.037")),
 "han2003":         dict(term="Trends Neurosci[ta] AND 2003[dp] AND 26[vi] AND 17[pg] AND Han JS[au]", exp=dict(journal="Trends Neurosci",year="2003",vol="26",first="17")),
 "han2004":         dict(pmid="15135942", exp=dict(year="2004",vol="361",first="258")),
 "lin2022":         dict(pmid="35422904", exp=dict(year="2022",vol="14",first="1469")),
 "wang2021":        dict(term="Chin Med[ta] AND 2021[dp] AND 16[vi] AND 56[pg]", exp=dict(journal="Chin Med",year="2021",vol="16",first="56")),
 "wu2016review":    dict(term="e0150367[pg] AND PLoS One[ta] AND 2016[dp]", exp=dict(year="2016",vol="11",first="e0150367")),
 "liu2025review":   dict(pmid="39814622", exp=dict(year="2025",vol="26",first="319")),
 "lu2023review":    dict(pmid="37256901", exp=dict(year="2023",vol="18",doi="10.1371/journal.pone.0285943")),
 "tahmasbi2025":    dict(term="10.1016/j.pmn.2024.12.005[aid]", exp=dict(year="2025",vol="26",first="111",doi="10.1016/j.pmn.2024.12.005")),
 "chu2026":         dict(pmid="41767528", exp=dict(year="2026",vol="13",doi="10.3389/fmed.2026.1772210")),
 "laigaard2021":    dict(pmid="33678402", exp=dict(year="2021",vol="126",first="1029")),
 "myles2017":       dict(pmid="28186223", exp=dict(year="2017",vol="118",first="424")),
 "page2021statement":dict(term="BMJ[ta] AND 2021[dp] AND 372[vi] AND n71[pg]", exp=dict(journal="BMJ",year="2021",vol="372",first="n71")),
 "page2021ee":      dict(term="BMJ[ta] AND 2021[dp] AND 372[vi] AND n160[pg]", exp=dict(journal="BMJ",year="2021",vol="372",first="n160")),
 "macpherson2010":  dict(term="STRICTA[ti] AND revised[ti] AND 2010[dp] AND MacPherson H[au]", choose="PLoS Med", exp=dict(year="2010")),
 "sterne2019":      dict(term="BMJ[ta] AND 2019[dp] AND 366[vi] AND l4898[pg]", exp=dict(journal="BMJ",year="2019",vol="366",first="l4898")),
 "guyatt2008":      dict(term="BMJ[ta] AND 2008[dp] AND 336[vi] AND 924[pg] AND Guyatt GH[au]", exp=dict(journal="BMJ",year="2008",vol="336",first="924")),
 "viechtbauer2010": dict(doi="10.18637/jss.v036.i03", crossref_only=True, exp=dict(year="2010",vol="36")),
 "veroniki2016":    dict(term="Res Synth Methods[ta] AND 2016[dp] AND 7[vi] AND 55[pg] AND Veroniki AA[au]", exp=dict(year="2016",vol="7",first="55")),
 "hartung2001":     dict(term="Stat Med[ta] AND 2001[dp] AND 20[vi] AND 1771[pg]", exp=dict(journal="Stat Med",year="2001",vol="20",first="1771")),
 "rover2015":       dict(term="BMC Med Res Methodol[ta] AND 2015[dp] AND 15[vi] AND 99[pg]", exp=dict(year="2015",vol="15",first="99")),
 "inthout2016":     dict(term="BMJ Open[ta] AND 2016[dp] AND 6[vi] AND e010247[pg]", exp=dict(journal="BMJ Open",year="2016",vol="6",first="e010247")),
 "higgins2002":     dict(term="Stat Med[ta] AND 2002[dp] AND 21[vi] AND 1539[pg]", exp=dict(journal="Stat Med",year="2002",vol="21",first="1539")),
}
def txt(e): return "".join(e.itertext()).strip() if e is not None else ""
def parse_pubmed(pmid):
    xml=get(EU+f"efetch.fcgi?db=pubmed&retmode=xml&id={pmid}"); (SRC/f"pubmed_{pmid}.xml").write_text(xml,encoding="utf-8")
    a=ET.fromstring(xml).find(".//PubmedArticle"); art=a.find(".//Article")
    au=[]
    for x in art.findall("./AuthorList/Author"):
        if x.find("CollectiveName") is not None: au.append(txt(x.find("CollectiveName")))
        else: au.append((txt(x.find("LastName"))+" "+txt(x.find("Initials"))).strip())
    pd=art.find("./Journal/JournalIssue/PubDate")
    year=txt(pd.find("Year")) or (re.search(r"\d{4}",txt(pd.find("MedlineDate"))) or [""])[0] if pd is not None else ""
    if not year:
        ad=art.find("./ArticleDate/Year"); year=txt(ad)
    ids={x.get("IdType"):txt(x) for x in a.findall(".//PubmedData/ArticleIdList/ArticleId")}
    eloc={x.get("EIdType"):txt(x) for x in art.findall("./ELocationID")}
    status=a.find(".//MedlineCitation").get("Status","")
    pubstat=txt(a.find(".//PubmedData/PublicationStatus"))
    return dict(source="PubMed",pmid=pmid,authors=au,title=txt(art.find("ArticleTitle")).rstrip("."),
        journal=txt(a.find(".//MedlineJournalInfo/MedlineTA")) or txt(art.find("./Journal/ISOAbbreviation")),
        year=year,volume=txt(art.find("./Journal/JournalIssue/Volume")),issue=txt(art.find("./Journal/JournalIssue/Issue")),
        pages=txt(art.find("./Pagination/MedlinePgn")),elocation=eloc.get("pii","") if not txt(art.find("./Pagination/MedlinePgn")) else "",
        doi=ids.get("doi","") or eloc.get("doi",""),publication_status=pubstat)
def parse_crossref(doi):
    j=json.loads(get("https://api.crossref.org/works/"+urllib.parse.quote(doi))); (SRC/("crossref_"+re.sub(r"[^A-Za-z0-9]+","_",doi)+".json")).write_text(json.dumps(j,indent=1),encoding="utf-8")
    m=j["message"]
    au=[(x.get("family","")+" "+"".join(p[0] for p in re.split(r"[\s\-.]+",x.get("given","")) if p)).strip() for x in m.get("author",[])]
    dp=(m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0]
    title=re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",(m.get("title") or [""])[0])).strip().rstrip(".")
    journal=(m.get("container-title") or [""])[0]; prov=["Crossref"]
    for issn in m.get("ISSN",[]):   # NLM journal abbreviation, by ISSN
        ids=json.loads(get(EU+"esearch.fcgi?db=nlmcatalog&retmode=json&term="+urllib.parse.quote(issn+"[issn]")))["esearchresult"]["idlist"]
        if ids:
            d=json.loads(get(EU+f"esummary.fcgi?db=nlmcatalog&retmode=json&id={ids[0]}"))["result"][ids[0]]
            if d.get("medlineta"): journal=d["medlineta"]; prov.append(f"NLM Catalog {ids[0]} (abbreviation)"); break
    pages=m.get("page") or ""
    if not pages:  # publisher citation metadata at the DOI landing page
        try:
            html=get("https://doi.org/"+doi); fp=re.search(r'name="citation_firstpage" content="([^"]*)"',html); lp=re.search(r'name="citation_lastpage" content="([^"]*)"',html)
            if fp: pages=fp.group(1)+("-"+lp.group(1) if lp else ""); prov.append("publisher citation_firstpage/lastpage (pages)")
        except Exception: pass
    return dict(source=" + ".join(prov),pmid="",authors=au,title=title,journal=journal,year=str(dp[0]),
        volume=m.get("volume",""),issue=m.get("issue",""),pages=pages,elocation=m.get("article-number","") or "",
        doi=m.get("DOI",""),publication_status="published-print" if m.get("published-print") else "online")
def first_page(r): return (r["pages"].split("-")[0] if r["pages"] else r["elocation"]).strip()
def verify(r,exp):
    issues=[]
    for k,v in exp.items():
        got={"journal":r["journal"],"year":r["year"],"vol":r["volume"],"first":first_page(r),"doi":r["doi"].lower()}[k]
        if k=="doi": v=v.lower()
        if k=="first" and got.lower().lstrip("e")!=v.lower().lstrip("e") and got.lower()!=v.lower(): issues.append(f"{k}: expected {v}, record has {got or '(none)'}")
        elif k!="first" and got!=v: issues.append(f"{k}: expected {v}, record has {got or '(none)'}")
    return issues
def order_keys():
    order=[]
    for f in ("INTRODUCTION","METHODS","RESULTS","DISCUSSION","CONCLUSIONS"):
        t=(ROOT/f"manuscript/{f}.md").read_text(encoding="utf-8")
        body="\n".join(l for l in t.splitlines()[1:] if not l.startswith(">"))
        for m in re.finditer(r"\[@([^\]]+)\]",body):
            for k in re.findall(r"@?([A-Za-z0-9_:-]+)",m.group(1)):
                if k not in order: order.append(k)
    return order
def shorten(p):  # Vancouver page elision: 1921-1928 -> 1921-8
    m=re.fullmatch(r"(\w*?)(\d+)-(\w*?)(\d+)",p or "")
    if not m or m.group(1)!=m.group(3): return (p or "").replace("--","-")
    a,b=m.group(2),m.group(4)
    if len(a)==len(b):
        i=0
        while i<len(a) and a[i]==b[i]: i+=1
        b=b[i:] or b[-1:]
    return f"{m.group(1)}{a}-{b}"
def vancouver(r):
    au=r["authors"]; A=", ".join(au[:6])+(", et al" if len(au)>6 else "")
    loc=shorten(r["pages"]) or r["elocation"]
    if r["volume"] and loc: tail=f"{r['year']};{r['volume']}:{loc}."
    elif r["volume"]: tail=f"{r['year']};{r['volume']}."
    else: tail=f"{r['year']}; doi:{r['doi']}."
    return f"{A}. {r['title']}. {r['journal']}. {tail}"
if __name__=="__main__":
    today=datetime.date.today().isoformat(); order=order_keys(); rows=[]
    missing=[k for k in order if k not in SPEC]; assert not missing, f"no lookup spec for {missing}"
    for n,k in enumerate(order,1):
        s=SPEC[k]; note=""
        if s.get("crossref_only"): r=parse_crossref(s["doi"]); how="Crossref DOI"
        else:
            pmid=s.get("pmid")
            if not pmid:
                ids=esearch(s["term"]); how=f"PubMed search: {s['term']}"
                if s.get("choose") and len(ids)>1:
                    recs=[parse_pubmed(i) for i in ids]; pick=[x for x in recs if x["journal"]==s["choose"]]
                    note=f"{len(ids)} co-published versions found ({'; '.join(x['journal'] for x in recs)}); {s['choose']} version used — REVIEW TEAM TO CONFIRM"
                    r=pick[0] if pick else recs[0]
                else:
                    assert len(ids)==1, f"{k}: search returned {ids}"
                    r=parse_pubmed(ids[0])
            else: r=parse_pubmed(pmid); how="PubMed PMID (from traceability record)"
            if not r["pmid"] and s.get("doi"): r=parse_crossref(s["doi"]); how="Crossref DOI"
        iss=verify(r,s["exp"])
        rows.append(dict(number=n,key=k,verification="VERIFIED" if not iss else "CHECK: "+"; ".join(iss),resolved_by=how,note=note,
            pmid=r["pmid"],doi=r["doi"],authors="; ".join(r["authors"]),n_authors=len(r["authors"]),title=r["title"],journal=r["journal"],
            year=r["year"],volume=r["volume"],issue=r["issue"],pages=r["pages"],elocation=r["elocation"],
            publication_status=r["publication_status"],source=r["source"],retrieved=today,vancouver=vancouver(r)))
        print(f"{n:2d} {k:18s} {rows[-1]['verification'][:70]:70s} {r['source']}")
    with open(REF/"bibliography.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    ris=[]
    for r in rows:
        ris+= ["TY  - JOUR"]+[f"AU  - {a}" for a in r["authors"].split("; ") if a]+[f"TI  - {r['title']}",f"JO  - {r['journal']}",f"PY  - {r['year']}"]
        ris+= [f"VL  - {r['volume']}"]*(bool(r["volume"]))+[f"IS  - {r['issue']}"]*(bool(r["issue"]))
        if r["pages"]:
            sp,_,ep=r["pages"].partition("-"); ris+=[f"SP  - {sp}"]+([f"EP  - {ep}"] if ep else [])
        elif r["elocation"]: ris+=[f"SP  - {r['elocation']}"]
        ris+= [f"DO  - {r['doi']}"]*(bool(r["doi"]))+[f"AN  - PMID:{r['pmid']}"]*(bool(r["pmid"]))+[f"ID  - {r['key']}",f"N1  - citation key {r['key']}","ER  - ",""]
    (REF/"bibliography.ris").write_text("\n".join(ris),encoding="utf-8")
    L=["# References","",f"BMC Vancouver style, numbered in order of first citation. Generated {today} by `references/build_bibliography.py` from PubMed/Crossref records; see `bibliography.csv` for identifiers and verification status.",""]
    L+=[f"{r['number']}. {r['vancouver']}" for r in rows]
    (REF/"REFERENCES_BMC.md").write_text("\n".join(L)+"\n",encoding="utf-8")
    print("\nwritten: bibliography.csv, bibliography.ris, REFERENCES_BMC.md")
