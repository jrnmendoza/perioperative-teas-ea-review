"""Rebuild Additional file 12 (trial-by-trial accounting for the primary opioid outcome)
from the committed records: Tier A CSVs, the Tier B text-signal CSV, and the E2
classification files in 10_FINAL_ADJUDICATION/02_DECISIONS/v38/ and 09_E2_ANALYSIS/.
Adds E2 (post-hoc sensitivity) dispositions and the documented reasons for Tier B."""
import csv, json, pathlib
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1]
AF=ROOT/"manuscript/additional_files"; V=ROOT/"10_FINAL_ADJUDICATION/02_DECISIONS/v38"; E2O=ROOT/"10_FINAL_ADJUDICATION/09_E2_ANALYSIS"
rd=lambda p:list(csv.DictReader(open(p,encoding="utf-8-sig")))
def wr(p,rows):
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import re
esc=lambda s:re.sub(r"\bn=(\d+)/(\d+)",r"\1 vs \2 participants",(s or "").replace("|","\\|").replace("\n"," ").strip())
A1=rd(AF/"additional_file_12_A1_primary_construct.csv"); A2=rd(AF/"additional_file_12_A2_other_windows.csv")
TB=rd(AF/"additional_file_12_tierB_no_candidate_result.csv")
RC=rd(V/"E2_tierA_reclassification.csv")+rd(V/"E2_tierA_reclassification_addendum.csv")
B1=rd(V/"E2_tierB1_extraction.csv"); B2=rd(V/"E2_tierB2_recheck.csv")
OUT={r["model_id"]:r for r in rd(E2O/"e2_model_outputs.csv")}
CAN={r["model_id"]:r for r in rd(ROOT/"10_FINAL_ADJUDICATION/04_MODELS/model_outputs.csv")}
studies=json.load(open(ROOT/"10_FINAL_ADJUDICATION/03_CANONICAL/studies.json"))
nrep=len({s["report_id"] for s in studies}); ntrial=len({s["trial_id"] for s in studies})

def e2_for(rid, window):
    parts=set(rid.split("+"))
    for r in RC:
        ids=set(x.strip().split(" ")[0] for x in r["result_ids"].replace("/","+").split("+"))
        if parts & ids: return r["E2_disposition"], r["E2_basis"]
    if any(w in window for w in ("48","72","3 postoperative days","POD1-3")):
        return "NOT APPLICABLE", "Not a 24-hour result; E2 is a 24-hour construct"
    return "UNCLASSIFIED", ""
for rows in (A1,A2):
    for r in rows:
        d,b=e2_for(r["result_id"],r["window"]); r["E2_disposition"]=d; r["E2_basis"]=b
assert not [r for r in A1+A2 if r["E2_disposition"]=="UNCLASSIFIED"], "unclassified Tier A result"
b1={r["report"]:r for r in B1}; b2={r["report"]:r for r in B2}
for r in TB:
    if r["report"] in b1:
        x=b1[r["report"]]; r["checked"]="B1: extracted under E2"
        r["documented_reason"]=x["E2_rule_failed"]; r["E2_disposition"]=x["E2_disposition"]
    elif r["report"] in b2:
        x=b2[r["report"]]; r["checked"]="B2: re-checked under E2"
        r["documented_reason"]=x["E2_rule_failed"]; r["E2_disposition"]=x["E2_disposition"]
    else:
        r["checked"]="Not re-examined individually (automated signal: no numeric opioid data)"
        r["documented_reason"]=""; r["E2_disposition"]="NOT RE-EXAMINED"
wr(AF/"additional_file_12_A1_primary_construct.csv",A1); wr(AF/"additional_file_12_A2_other_windows.csv",A2)
wr(AF/"additional_file_12_tierB_no_candidate_result.csv",TB)

r1=sorted({r["report"] for r in A1}); r2=sorted({r["report"] for r in A2}); allA=sorted(set(r1)|set(r2))
tier=Counter(r["tier"] for r in TB)
L=[]; w=L.append
w("# Additional file 12. Trial-by-trial accounting for the primary opioid outcome"); w("")
w(f"**Why this file exists.** The review included {nrep} reports representing {ntrial} trial families, yet the principal comparison for the registered primary outcome — all delivered systemic opioid, end of surgery to 24 hours, in mg IV MME — rests on a single trial. This file accounts for every included report against that outcome, so the reduction from {ntrial} trial families to one principal contrast can be audited report by report.")
w("")
w("**Two classifications are shown.** **E1** is the registered primary outcome, and it governs every primary result. **E2** is a post-hoc broadened construct that relaxes completeness of opioid capture only. It is reported as a sensitivity analysis. E2 was defined and applied after the primary results were known; its definition, amendment (E2.1) and the decision to retain E1 as primary are in Additional file 10, Section 7.1.")
w(""); w("## Summary"); w("")
w("| Tier | Definition | Reports | Results |"); w("|---|---|---:|---:|")
w(f"| **A1** | Candidate result adjudicated against the registered primary construct (systemic opioid, 0–24 h) | {len(r1)} | {len(A1)} |")
w(f"| **A2** | Opioid result at a different window or construct (0–48 h, 0–72 h, rescue-only), or a combined-arm form of an A1 result | {len(r2)} | {len(A2)} |")
w(f"| **B** | No candidate postoperative opioid result in the analysis record | {len(TB)} | 0 |")
w(f"| | **Total included reports** | **{nrep}** | **{len(A1)+len(A2)}** |"); w("")
w(f"Tier A1 and A2 overlap by report ({len(r1)} + {len(r2)} reports span {len(allA)} distinct reports); {len(allA)} + {len(TB)} = {nrep}."); w("")
w("### What each classification yields"); w("")
w("| Body | E1 k | E1 MD, mg IV MME (95% CI) | E2 k | E2 MD, mg IV MME (95% CI) |"); w("|---|---:|---|---:|---|")
f2=lambda r:f"{float(r['effect']):.2f} ({float(r['ci_low']):.2f} to {float(r['ci_high']):.2f})" if r.get("effect") else "No eligible data"
for body,e1,e2 in (("TEAS vs sham","opioid24_TEAS_sham","E2_opioid24_TEAS_sham"),("TEAS vs usual care","opioid24_TEAS_usual","E2_opioid24_TEAS_usual"),
                   ("EA vs sham","opioid24_EA_sham","E2_opioid24_EA_sham"),("EA vs usual care","opioid24_EA_usual","E2_opioid24_EA_usual")):
    w(f"| {body} | {CAN[e1]['k']} | {f2(CAN[e1])} | {OUT[e2]['k']} | {f2(OUT[e2])} |")
w(""); w("No body met the registered joint criterion under either classification. For EA vs sham under E2 (a single trial), the criterion could not be evaluated because that trial contributes no eligible ~24-hour pain result."); w("")
w("## Tier A1 — adjudicated against the registered primary construct"); w("")
w("| E1 disposition | Results | Meaning |"); w("|---|---:|---|")
M={"INCLUDE":"Eligible for a principal or supportive body","SENSITIVITY":"Admitted only to labelled sensitivity analyses","HOLD":"Withheld from synthesis pending unresolved source questions","EXCLUDE":"Not admitted to any body"}
for k,v in Counter(r["decision"] for r in A1).most_common(): w(f"| {k} | {v} | {M.get(k,'')} |")
w(""); w("Only results capturing **all** systemic opioid exposure were eligible under E1. The four eligible results are Szmit 2021 (two arms), El-Rakshy 2009 and Seevaunnamtum 2016, which is why the principal TEAS bodies are k=1 and the supportive EA body is k=2."); w("")
w("| Result ID | Report | Modality | Comparator | Reported quantity | Window | Systemic capture | E1 | E2 |"); w("|---|---|---|---|---|---|---|---|---|")
for r in sorted(A1,key=lambda x:(x["report"],x["result_id"])):
    w("| "+" | ".join(esc(r[k])[:52] for k in ["result_id","report","modality","comparator","reported","window","systemic_capture","decision","E2_disposition"])+" |")
w(""); w("## Tier A2 — opioid results at other windows or constructs"); w("")
w("| Result ID | Report | Modality | Comparator | Reported quantity | Window | Construct | E1 | E2 |"); w("|---|---|---|---|---|---|---|---|---|")
for r in sorted(A2,key=lambda x:(x["report"],x["result_id"])):
    w("| "+" | ".join(esc(r[k])[:52] for k in ["result_id","report","modality","comparator","reported","window","systemic_capture","decision","E2_disposition"])+" |")
w(""); w("## Tier B — reports with no candidate opioid result"); w("")
w("Tier B reports were graded by an automated search of each report's hash-pinned source text. Reports graded B1 and B2 were then extracted or re-checked individually, and every one now carries a documented reason. Reports graded B3 and B4 showed no numeric opioid data and were not re-examined individually.")
w(""); w("| Grade | Basis | Reports | Individually checked |"); w("|---|---|---:|---|")
GB={"B1":"Opioid-outcome phrase co-located with a 24-hour window marker and numeric data","B2":"Opioid-outcome phrase with numeric data, no 24-hour marker nearby","B3":"Opioid mentioned; no numeric outcome data co-located","B4":"No opioid-outcome phrase in source text"}
for k in ("B1","B2","B3","B4"): w(f"| **{k}** | {GB[k]} | {tier.get(k,0)} | {'Yes — extracted' if k=='B1' else ('Yes — re-checked' if k=='B2' else 'No')} |")
w(""); w("### B1 — extracted individually"); w("")
w("No B1 report yields an E1 result. Two were admitted to E2 only under amendment E2.1: Zhang 2025 (postoperative-day-1 total taken as 24 hours) and Gu 2019 (24-hour value digitised from a figure; figure–text contradiction flagged).")
w(""); w("| Report | Modality / comparator | What is reported | Why it is not a registered-outcome result | E2 |"); w("|---|---|---|---|---|")
for x in sorted(B1,key=lambda z:z["report"]):
    w(f"| {esc(x['report'])} | {esc(x['modality'])} / {esc(x['comparator'])[:28]} | {esc(x['opioid_reported'])[:90]} | {esc(x['E2_rule_failed'])[:120]} | {esc(x['E2_disposition'])[:60]} |")
w(""); w("### B2 — re-checked individually"); w("")
w("No B2 report yields an E1 or an E2 result. Yeh 2010 remains held as part of the Yeh 2010/2011 family.")
w(""); w("| Report | Comparator | What is reported | Reason | E2 |"); w("|---|---|---|---|---|")
for x in sorted(B2,key=lambda z:z["report"]):
    w(f"| {esc(x['report'])} | {esc(x['comparator'])[:24]} | {esc(x['what_is_reported'])[:110]} | {esc(x['E2_rule_failed'])[:100]} | {esc(x['E2_disposition'])} |")
b34=sorted(r["report"] for r in TB if r["tier"] in ("B3","B4"))
w(""); w(f"### B3 and B4 — not re-examined individually ({len(b34)} reports)"); w("")
w("These reports showed no numeric opioid outcome data in the automated search, and they were not re-examined by hand. An opioid quantity reported only in a table or figure that the text search did not reach cannot be ruled out. This is a limitation of this accounting. Reports: "+", ".join(b34)+".")
w(""); w("## Method note"); w("")
w("Tier A1 is reproduced from `primary_evidence_table.csv` and Tier A2 from `model_inputs.csv` (both in `10_FINAL_ADJUDICATION/`). E1 classifications, dispositions and source locators are reproduced as recorded. E2 dispositions come from `02_DECISIONS/v38/E2_tierA_reclassification.csv` plus a dated addendum for two held results omitted from it, `E2_tierB1_extraction.csv` and `E2_tierB2_recheck.csv`. E2 estimates come from `09_E2_ANALYSIS/e2_model_outputs.csv`. Tier B grades are an automated screening signal and not an adjudication. No result was added, removed, reclassified or recomputed in producing this file.")
w(""); w("**Accompanying data files:** `additional_file_12_A1_primary_construct.csv`, `additional_file_12_A2_other_windows.csv` and `additional_file_12_tierB_no_candidate_result.csv`. Each now carries E2 columns, and the Tier B file carries the documented reason for each B1 and B2 report.")
(ROOT/"manuscript/ADDITIONAL_FILE_12.md").write_text("\n".join(L)+"\n",encoding="utf-8")
print("A1",len(A1),"A2",len(A2),"TB",len(TB),"| E2 dispositions A1+A2:",dict(Counter(r["E2_disposition"] for r in A1+A2)),"| TB:",dict(Counter(r["E2_disposition"] for r in TB)))
