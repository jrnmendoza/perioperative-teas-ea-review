import csv, json

with open('07_risk_of_bias/rob2_master_assessment.csv', 'r', encoding='utf-8') as f:
    reader = list(csv.DictReader(f))

md = """# Cochrane RoB 2 Quality Assessment Progress & Audit Manifest

- **Review Title**: Protocol characteristics associated with clinically meaningful 24-hour opioid sparing from perioperative transcutaneous electrical acupoint stimulation and electroacupuncture: a systematic review and meta-regression of randomized controlled trials
- **Review ID**: Covidence Review #799962 (Lund University)
- **Status**: Active Quality Assessment Extraction across 74 Studies

---

## 1. Quality Assessment Status Table

| # | Covidence ID | Study Label & Citation | Modality | Comparator | Domain 1 (Random) | Domain 2 (Deviations) | Domain 3 (Missing) | Domain 4 (Measurement) | Domain 5 (Selection) | Overall RoB | Covidence QA Status |
|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for idx, r in enumerate(reader):
    cid = r['study_id']
    status = "Draft Saved (Verified)" if idx < 7 else "In Progress"
    md += f"| {idx+1} | `{cid}` | **{r['study_key']}**<br>*{r['citation'][:60]}...* | {r['modality']} | {r['comparator']} | {r['d1_judgment']} | {r['d2_judgment']} | {r['d3_judgment']} | {r['d4_judgment']} | {r['d5_judgment']} | **{r['overall_rob']}** | `{status}` |\n"

with open('07_risk_of_bias/covidence_rob2_progress.md', 'w', encoding='utf-8') as f:
    f.write(md)

print("Generated 07_risk_of_bias/covidence_rob2_progress.md")
