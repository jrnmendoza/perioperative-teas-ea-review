import json, re

# Load raw references and parsed data
with open('tan_76_parsed.json') as f:
    tan = json.load(f)
with open('covidence_all_63_included.json') as f:
    inc = json.load(f)
with open('covidence_all_161_excluded.json') as f:
    exc = json.load(f)

# Master curated database for all 76 Tan RCTs
# Every study is audited individually against Covidence and the primary article.

studies_data = {
    1: {
        "study": "Ao 2021",
        "doi": "10.3892/etm.2021.9615",
        "found": "YES",
        "cov_id": "#438 (ID 1879896620)",
        "stage": "Extraction (Included)",
        "status": "INCLUDED",
        "reason": "None (Included in review)",
        "ft_checked": "YES",
        "outcomes": "VAS pain at 2, 6, 12, 24, 48 h; rescue pethidine; immune function (CD4+, CD8+, NK)",
        "opioid_24h": "NO (reports rescue pethidine frequency/rate, not continuous IV MME mass)",
        "primary_eligible": "NO",
        "judgment": "MATCHED — INCLUDED",
        "action": "none",
        "locator": "Exp Ther Med 2021;21:184; Results, Table II"
    },
    2: {
        "study": "Arnberger 2007",
        "doi": "10.1097/01.anes.0000290617.98058.d9",
        "found": "YES",
        "cov_id": "#895 (ID 1879897387)",
        "stage": "Title/Abstract screening",
        "status": "EXCLUDED",
        "reason": "Excluded at Title/Abstract screening (Irrelevant)",
        "ft_checked": "YES",
        "outcomes": "PONV incidence over 24 h; rescue ondansetron; no postoperative pain or opioid consumption reported",
        "opioid_24h": "NO",
        "primary_eligible": "NO",
        "judgment": "LEGITIMATE EXCLUSION",
        "action": "none",
        "locator": "Anesthesiology 2007;107(6):903-8; Methods, Outcomes"
    },
    3: {
        "study": "Bai 2018",
        "doi": "10.13703/j.0255-2930.2018.06.002",
        "found": "YES",
        "cov_id": "#589 (ID 1879896874)",
        "stage": "Full-text review",
        "status": "EXCLUDED",
        "reason": "Wrong outcomes",
        "ft_checked": "YES",
        "outcomes": "Intraoperative propofol and remifentanil consumption; extubation time; recovery time. No postoperative analgesia/opioid outcomes",
        "opioid_24h": "NO",
        "primary_eligible": "NO",
        "judgment": "LEGITIMATE EXCLUSION",
        "action": "none",
        "locator": "Zhongguo Zhen Jiu 2018;38(6):577-80; Table 2, Table 3"
    },
    4: {
        "study": "Chen 2020",
        "doi": "10.1111/1759-7714.13343",
        "found": "YES",
        "cov_id": "#480 (ID 1879896688)",
        "stage": "Extraction (Included)",
        "status": "INCLUDED",
        "reason": "None (Included in review)",
        "ft_checked": "YES",
        "outcomes": "Cumulative IV PCIA sufentanil at 6, 24, 48 h; VAS at 6, 24, 48 h; PONV; PCA attempts",
        "opioid_24h": "YES (24-h sufentanil: TEAS 72.43 ± 4.78 µg vs Sham 100.62 ± 10.20 µg, P < 0.001)",
        "primary_eligible": "YES (Strict primary 24-h IV MME analysis; converted via 0.1 factor to 7.243 vs 10.062 mg MME)",
        "judgment": "MATCHED — INCLUDED",
        "action": "none",
        "locator": "Thorac Cancer 2020;11(4):928-34; Results, Section 3.2, Fig 2, Table 2"
    },
    5: {
        "study": "Chen 2018",
        "doi": "10.1016/j.jclinane.2018.06.003",
        "found": "YES",
        "cov_id": "#566 (ID 1879896823)",
        "stage": "Full-text review",
        "status": "EXCLUDED",
        "reason": "Wrong outcomes",
        "ft_checked": "YES",
        "outcomes": "Time to first flatus, time to first defecation, postoperative ileus, bowel sounds. Postoperative pain and analgesic requirements were not assessed",
        "opioid_24h": "NO",
        "primary_eligible": "NO",
        "judgment": "LEGITIMATE EXCLUSION",
        "action": "none",
        "locator": "J Clin Anesth 2018;49:74-78; Methods, Measurements, p. 75"
    },
    6: {
        "study": "Chen 1998",
        "doi": "10.1097/00000539-199812000-00021",
        "found": "YES",
        "cov_id": "#969 (ID 1879897506)",
        "stage": "Extraction (Included)",
        "status": "INCLUDED",
        "reason": "None (Included in review)",
        "ft_checked": "YES",
        "outcomes": "PCA hydromorphone consumption, VAS pain, nausea, sedation after lower abdominal surgery",
        "opioid_24h": "YES (Hydromorphone reported at 24 h)",
        "primary_eligible": "YES (Secondary / sensitivity opioid analysis; EA vs active TENS comparison)",
        "judgment": "MATCHED — INCLUDED",
        "action": "none",
        "locator": "Anesth Analg 1998;87(6):1329-34; Table 2, Fig 2"
    },
    7: {
        "study": "Chen 2013",
        "doi": "None",
        "found": "YES",
        "cov_id": "#740 (ID 1879897137)",
        "stage": "Title/Abstract screening",
        "status": "EXCLUDED",
        "reason": "Excluded at Title/Abstract screening (Irrelevant)",
        "ft_checked": "YES",
        "outcomes": "Propofol and remifentanil consumption during transsphenoidal pituitary surgery under general anesthesia; extubation time. No postoperative analgesic data",
        "opioid_24h": "NO",
        "primary_eligible": "NO",
        "judgment": "LEGITIMATE EXCLUSION",
        "action": "none",
        "locator": "Zhongguo Zhen Jiu 2013;33(6):537-40; Methods, Results"
    },
    8: {
        "study": "Chen 2015",
        "doi": "10.1016/j.jclinane.2015.03.011",
        "found": "YES",
        "cov_id": "#657 (ID 1879897004)",
        "stage": "Extraction (Included)",
        "status": "INCLUDED",
        "reason": "None (Included in review)",
        "ft_checked": "YES",
        "outcomes": "Quality of recovery (QoR-40), VAS pain at 6, 24, 48 h, rescue dezocine analgesia, PONV after thyroidectomy",
        "opioid_24h": "NO (reports rescue dezocine requirements as counts/incidence, not continuous cumulative IV MME dose)",
        "primary_eligible": "NO",
        "judgment": "MATCHED — INCLUDED",
        "action": "none",
        "locator": "J Clin Anesth 2015;27(4):309-14; Table 2, Table 3"
    },
    9: {
        "study": "Chen 2015",
        "doi": "10.1007/s00540-015-2007-y",
        "found": "YES",
        "cov_id": "#673 (ID 1879897029)",
        "stage": "Extraction (Included)",
        "status": "INCLUDED",
        "reason": "None (Included in review)",
        "ft_checked": "YES",
        "outcomes": "Mechanical hyperalgesia threshold around incision, VAS pain, rescue dezocine dose, time to first rescue",
        "opioid_24h": "NO (reports time to first analgesia and dezocine rescue rate, but not 0-24 h cumulative PCA mass)",
        "primary_eligible": "NO",
        "judgment": "MATCHED — INCLUDED",
        "action": "none",
        "locator": "J Anesth 2015;29(5):714-20; Table 2, Fig 2"
    },
    10: {
        "study": "Chi 2019",
        "doi": "10.1142/s0192415x19500745",
        "found": "YES",
        "cov_id": "#488 (ID 1879896700)",
        "stage": "Title/Abstract screening",
        "status": "EXCLUDED",
        "reason": "Excluded at Title/Abstract screening (Irrelevant)",
        "ft_checked": "YES",
        "outcomes": "Postoperative knee surgery recovery (HSS score), serum cortisol, ACTH, IL-6, TNF-alpha. No postoperative pain or opioid consumption outcomes reported",
        "opioid_24h": "NO",
        "primary_eligible": "NO",
        "judgment": "LEGITIMATE EXCLUSION",
        "action": "none",
        "locator": "Am J Chin Med 2019;47(7):1445-58; Methods, Measurements"
    }
}

print(f'Populated initial {len(studies_data)} studies.')
