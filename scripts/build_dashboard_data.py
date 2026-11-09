#!/usr/bin/env python3
"""
Build complete structured JSON and JS payloads for the Perioperative TEAS & EA Review Dashboard
ONLY using all data in this folder (/Users/ryan/Downloads/TEAS draft 2).
"""

import os
import sys
import json
import hashlib
import openpyxl
try:
    import docx
except ImportError:
    docx = None
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = Path('/Users/ryan/Downloads/TEAS draft 2')

if (ROOT / 'dashboard/Additional_files').exists():
    AF = ROOT / 'dashboard/Additional_files'
    FIGS = ROOT / 'dashboard/figures_png'
    RC_DOCX = ROOT / 'dashboard/TEAS_EA_review_READING_COPY_with_figures.docx'
    TARGET_DIRS = [ROOT / 'dashboard']
    if DOWNLOAD_DIR.exists():
        TARGET_DIRS.append(DOWNLOAD_DIR)
elif DOWNLOAD_DIR.exists():
    AF = DOWNLOAD_DIR / 'Additional_files'
    FIGS = DOWNLOAD_DIR / 'figures_png'
    RC_DOCX = DOWNLOAD_DIR / 'TEAS_EA_review_READING_COPY_with_figures.docx'
    TARGET_DIRS = [DOWNLOAD_DIR]
    if (ROOT / 'dashboard').exists():
        TARGET_DIRS.append(ROOT / 'dashboard')
else:
    raise FileNotFoundError("Could not find Additional_files in repo or downloads")

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and (v != v):
        return None
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None
    return v

def clean_dict(d):
    return {k: clean_val(v) for k, v in d.items()}

print("1. Reading Additional_file_3.xlsx (PRISMA Flow & Reports)...")
wb3 = openpyxl.load_workbook(AF / 'Additional_file_3.xlsx', data_only=True)
prisma_counts = {}
for r in wb3['Fig. 1 counts'].iter_rows(values_only=True):
    if r and r[0] and r[0] != 'Reason':
        prisma_counts[str(r[0]).strip()] = int(r[1]) if r[1] is not None else 0

reports_rows = list(wb3['Reports'].iter_rows(values_only=True))
h3 = [str(c).strip() for c in reports_rows[0]]
prisma_reports = []
for r in reports_rows[1:]:
    if any(r):
        row_dict = {h3[i]: clean_val(r[i]) for i in range(len(h3))}
        prisma_reports.append(row_dict)

print("2. Reading Additional_file_4.xlsx (Contradictions & Held Decisions)...")
wb4 = openpyxl.load_workbook(AF / 'Additional_file_4.xlsx', data_only=True)
contra_rows = list(wb4['Contradictions'].iter_rows(values_only=True))
h4_contra = [str(c).strip() for c in contra_rows[0]]
contradictions = []
for r in contra_rows[1:]:
    if any(r):
        contradictions.append({h4_contra[i]: clean_val(r[i]) for i in range(len(h4_contra))})

held_rows = list(wb4['Held or sensitivity-only'].iter_rows(values_only=True))
h4_held = [str(c).strip() for c in held_rows[0]]
held_decisions = []
for r in held_rows[1:]:
    if any(r):
        held_decisions.append({h4_held[i]: clean_val(r[i]) for i in range(len(h4_held))})

print("3. Reading Additional_file_5.xlsx (Rules, Analysis Inputs, Extracted Results)...")
wb5 = openpyxl.load_workbook(AF / 'Additional_file_5.xlsx', data_only=True)
rules_rows = list(wb5['Rules'].iter_rows(values_only=True))
rules = []
for r in rules_rows[1:]:
    if any(r):
        rules.append({'rule': clean_val(r[0]), 'definition': clean_val(r[1])})

inputs_rows = list(wb5['Analysis inputs'].iter_rows(values_only=True))
h5_inp = [str(c).strip() for c in inputs_rows[0]]
analysis_inputs = []
for r in inputs_rows[1:]:
    if any(r):
        analysis_inputs.append({h5_inp[i]: clean_val(r[i]) for i in range(len(h5_inp))})

extracted_rows = list(wb5['Extracted results'].iter_rows(values_only=True))
h5_ext = [str(c).strip() for c in extracted_rows[0]]
extracted_results = []
for r in extracted_rows[1:]:
    if any(r):
        extracted_results.append({h5_ext[i]: clean_val(r[i]) for i in range(len(h5_ext))})

no_res_rows = list(wb5['Reports without a result'].iter_rows(values_only=True))
h5_no = [str(c).strip() for c in no_res_rows[0]]
reports_without_result = []
for r in no_res_rows[1:]:
    if any(r):
        reports_without_result.append({h5_no[i]: clean_val(r[i]) for i in range(len(h5_no))})

print("4. Reading Additional_file_6.xlsx (Opioid MME Conversions)...")
wb6 = openpyxl.load_workbook(AF / 'Additional_file_6.xlsx', data_only=True)
factors_rows = list(wb6['Factors'].iter_rows(values_only=True))
h6_fac = [str(c).strip() for c in factors_rows[0]]
conversion_factors = []
for r in factors_rows[1:]:
    if any(r):
        conversion_factors.append({h6_fac[i]: clean_val(r[i]) for i in range(len(h6_fac))})

prohib_rows = list(wb6['Prohibited conversions'].iter_rows(values_only=True))
h6_pro = [str(c).strip() for c in prohib_rows[0]]
prohibited_conversions = []
for r in prohib_rows[1:]:
    if any(r):
        prohibited_conversions.append({h6_pro[i]: clean_val(r[i]) for i in range(len(h6_pro))})

applied_rows = list(wb6['Applied to results'].iter_rows(values_only=True))
h6_app = [str(c).strip() for c in applied_rows[0]]
applied_factors = []
for r in applied_rows[1:]:
    if any(r):
        applied_factors.append({h6_app[i]: clean_val(r[i]) for i in range(len(h6_app))})

print("5. Reading Additional_file_7.xlsx (Study Characteristics & Effect Directions)...")
wb7 = openpyxl.load_workbook(AF / 'Additional_file_7.xlsx', data_only=True)
chars_rows = list(wb7['Characteristics'].iter_rows(values_only=True))
h7_char = [str(c).strip() for c in chars_rows[0]]
characteristics = []
for r in chars_rows[1:]:
    if any(r):
        characteristics.append({h7_char[i]: clean_val(r[i]) for i in range(len(h7_char))})

eff_rows = list(wb7['Effect directions'].iter_rows(values_only=True))
h7_eff = [str(c).strip() for c in eff_rows[0]]
effect_directions = []
for r in eff_rows[1:]:
    if any(r):
        effect_directions.append({h7_eff[i]: clean_val(r[i]) for i in range(len(h7_eff))})

print("6. Reading Additional_file_9.xlsx (RoB 2 Judgements, Domain Summary, Signalling Questions)...")
wb9 = openpyxl.load_workbook(AF / 'Additional_file_9.xlsx', data_only=True)
judg_rows = list(wb9['Judgements'].iter_rows(values_only=True))
h9_judg = [str(c).strip() for c in judg_rows[0]]
rob_judgements = []
for r in judg_rows[1:]:
    if any(r):
        rob_judgements.append({h9_judg[i]: clean_val(r[i]) for i in range(len(h9_judg))})

dom_rows = list(wb9['Domain summary'].iter_rows(values_only=True))
h9_dom = [str(c).strip() for c in dom_rows[0]]
rob_domain_summary = []
for r in dom_rows[1:]:
    if any(r):
        rob_domain_summary.append({h9_dom[i]: clean_val(r[i]) for i in range(len(h9_dom))})

sig_rows = list(wb9['Signalling questions'].iter_rows(values_only=True))
h9_sig = [str(c).strip() for c in sig_rows[0]]
rob_signalling = []
for r in sig_rows[1:]:
    if any(r):
        rob_signalling.append({h9_sig[i]: clean_val(r[i]) for i in range(len(h9_sig))})

not_assessed_rows = list(wb9['Not assessed'].iter_rows(values_only=True))
h9_na = [str(c).strip() for c in not_assessed_rows[0]]
rob_not_assessed = []
for r in not_assessed_rows[1:]:
    if any(r):
        rob_not_assessed.append({h9_na[i]: clean_val(r[i]) for i in range(len(h9_na))})

d6_trials_rows = list(wb9['D6 what-if trials'].iter_rows(values_only=True))
h9_d6 = [str(c).strip() for c in d6_trials_rows[0]]
rob_d6_what_ifs = []
for r in d6_trials_rows[1:]:
    if any(r):
        rob_d6_what_ifs.append({h9_d6[i]: clean_val(r[i]) for i in range(len(h9_d6))})

print("7. Reading Additional_file_10.xlsx (GRADE Evidence Profiles)...")
wb10 = openpyxl.load_workbook(AF / 'Additional_file_10.xlsx', data_only=True)
grade_profiles = {}
for sheet in wb10.sheetnames:
    if sheet == 'README': continue
    srows = list(wb10[sheet].iter_rows(values_only=True))
    hs = [str(c).strip() for c in srows[0]]
    sheet_data = []
    for r in srows[1:]:
        if any(r):
            sheet_data.append({hs[i]: clean_val(r[i]) for i in range(len(hs)) if i < len(r)})
    grade_profiles[sheet] = sheet_data

print("8. Reading Additional_file_11.xlsx (Opioid & Secondary Models, Single-Trial Estimates)...")
wb11 = openpyxl.load_workbook(AF / 'Additional_file_11.xlsx', data_only=True)
models_opioid = []
srows = list(wb11['Opioid analyses'].iter_rows(values_only=True))
hs = [str(c).strip() for c in srows[0]]
for r in srows[1:]:
    if any(r):
        models_opioid.append({hs[i]: clean_val(r[i]) for i in range(len(hs)) if i < len(r)})

models_other = []
srows = list(wb11['Other outcomes'].iter_rows(values_only=True))
hs = [str(c).strip() for c in srows[0]]
for r in srows[1:]:
    if any(r):
        models_other.append({hs[i]: clean_val(r[i]) for i in range(len(hs)) if i < len(r)})

single_trial_estimates = []
srows = list(wb11['Single-trial estimates'].iter_rows(values_only=True))
hs = [str(c).strip() for c in srows[0]]
for r in srows[1:]:
    if any(r):
        single_trial_estimates.append({hs[i]: clean_val(r[i]) for i in range(len(hs)) if i < len(r)})

rescue_missing_outcomes = []
srows = list(wb11['Rescue missing outcomes'].iter_rows(values_only=True))
hs = [str(c).strip() for c in srows[0]]
for r in srows[1:]:
    if any(r):
        rescue_missing_outcomes.append({hs[i]: clean_val(r[i]) for i in range(len(hs)) if i < len(r)})

print("9. Reading Word Documents (PRISMA checklist, Search strategies, Reading copy)...")
if docx is not None:
    doc1 = docx.Document(AF / 'Additional_file_1.docx')
    af1_text = [p.text.strip() for p in doc1.paragraphs if p.text.strip()]
    af1_tables = []
    for t in doc1.tables:
        table_data = []
        for row in t.rows:
            table_data.append([c.text.strip() for c in row.cells])
        if table_data:
            af1_tables.append(table_data)

    doc2 = docx.Document(AF / 'Additional_file_2.docx')
    af2_text = [p.text.strip() for p in doc2.paragraphs if p.text.strip()]
    af2_tables = []
    for t in doc2.tables:
        table_data = []
        for row in t.rows:
            table_data.append([c.text.strip() for c in row.cells])
        if table_data:
            af2_tables.append(table_data)

    doc_reading = docx.Document(RC_DOCX)
    manuscript_sections = {}
    current_sec = 'Header'
    manuscript_sections[current_sec] = []
    for p in doc_reading.paragraphs:
        txt = p.text.strip()
        if not txt: continue
        if p.style.name.startswith('Heading 1'):
            current_sec = txt
            manuscript_sections[current_sec] = []
        elif p.style.name.startswith('Heading 2'):
            manuscript_sections[current_sec].append(f'### {txt}')
        else:
            manuscript_sections[current_sec].append(txt)
else:
    print("   (python-docx not installed; reusing pre-compiled docx sections)")
    existing = {}
    for td in TARGET_DIRS:
        if (td / 'current_review.json').exists():
            existing = json.loads((td / 'current_review.json').read_text(encoding='utf-8'))
            break
    af1_text = existing.get('prisma_checklist', {}).get('text', [])
    af1_tables = existing.get('prisma_checklist', {}).get('tables', [])
    af2_text = existing.get('search_strategies', {}).get('text', [])
    af2_tables = existing.get('search_strategies', {}).get('tables', [])
    manuscript_sections = existing.get('manuscript_text', {})

print("10. Gathering Figures and Downloads metadata...")
figures_info = [
    {
        'id': 'Fig1',
        'file': 'Fig1.png',
        'title': 'Fig. 1 PRISMA 2020 flow diagram',
        'legend': 'PRISMA 2020 flow diagram showing search results, full-text exclusions with reasons, and 44 included reports (from 43 trials).'
    },
    {
        'id': 'Fig2',
        'file': 'Fig2.png',
        'title': 'Fig. 2 Contribution of each included report to the analyses',
        'legend': 'Heatmap matrix showing which analyses each of the 44 included reports contributed to across opioid outcomes, pain, PONV, and recovery.'
    },
    {
        'id': 'Fig3',
        'file': 'Fig3.png',
        'title': 'Fig. 3 Risk of bias',
        'legend': 'Risk-of-bias judgements across 180 assessed results using the Cochrane RoB 2 tool, showing percentages in each domain (D1–D5) and overall.'
    },
    {
        'id': 'Fig4',
        'file': 'Fig4.png',
        'title': 'Fig. 4 Broader first-day opioid consumption, by modality and comparator',
        'legend': 'Forest plots of broader first-day postoperative opioid consumption (mg IV morphine equivalents) for TEAS vs sham, TEAS vs usual care, EA vs sham, and EA vs usual care.'
    },
    {
        'id': 'Fig5',
        'file': 'Fig5.png',
        'title': 'Fig. 5 Receipt of additional rescue opioid, TEAS versus sham',
        'legend': 'Forest plot of the proportion of participants receiving additional rescue opioid analgesia, comparing TEAS with sham.'
    }
]

downloads_manifest = []
# Additional files 1 to 11
af_titles = {
    'Additional_file_1.docx': 'Additional file 1: PRISMA 2020 & PRISMA-S checklist',
    'Additional_file_2.docx': 'Additional file 2: Database search strategies',
    'Additional_file_3.xlsx': 'Additional file 3: PRISMA flow & excluded reports register',
    'Additional_file_4.xlsx': 'Additional file 4: Source contradictions & sensitivity decisions',
    'Additional_file_5.xlsx': 'Additional file 5: Extracted data & operational definitions',
    'Additional_file_6.xlsx': 'Additional file 6: Opioid conversion register (MME)',
    'Additional_file_7.xlsx': 'Additional file 7: Study characteristics & effect directions',
    'Additional_file_8.zip': 'Additional file 8: Analysis code, reproduction & verification',
    'Additional_file_9.xlsx': 'Additional file 9: Risk-of-bias (RoB 2) result assessments',
    'Additional_file_10.xlsx': 'Additional file 10: GRADE evidence profiles & summary of findings',
    'Additional_file_11.xlsx': 'Additional file 11: Opioid & secondary outcome model results'
}

for fname in sorted(os.listdir(AF)):
    fpath = AF / fname
    if fpath.is_file() and not fname.startswith('.'):
        downloads_manifest.append({
            'name': fname,
            'label': af_titles.get(fname, fname),
            'category': 'Additional Files',
            'size': fpath.stat().st_size,
            'sha256': hashlib.sha256(fpath.read_bytes()).hexdigest(),
            'relative_path': f'Additional_files/{fname}'
        })

# Figures
for fig in figures_info:
    fpath = FIGS / fig['file']
    if fpath.is_file():
        downloads_manifest.append({
            'name': fig['file'],
            'label': fig['title'],
            'category': 'Figures (High-res PNG)',
            'size': fpath.stat().st_size,
            'sha256': hashlib.sha256(fpath.read_bytes()).hexdigest(),
            'relative_path': f'figures_png/{fig["file"]}'
        })

# Reading copy DOCX
rc_path = RC_DOCX
if rc_path.is_file():
    downloads_manifest.append({
        'name': 'TEAS_EA_review_READING_COPY_with_figures.docx',
        'label': 'Manuscript Reading Copy with Embedded Figures (DOCX)',
        'category': 'Manuscript',
        'size': rc_path.stat().st_size,
        'sha256': hashlib.sha256(rc_path.read_bytes()).hexdigest(),
        'relative_path': 'TEAS_EA_review_READING_COPY_with_figures.docx'
    })

print("11. Assembling Master Review Object...")
review_master = {
    'version': 'BMC Revision (44 Reports)',
    'date': '2026-11-08',
    'registration': 'CRD420261452908',
    'target_journal': 'BMC Anesthesiology',
    'citation': 'Mendoza JRN, Peters SK, Sjöberg C, Jildenstål P. Perioperative transcutaneous electrical acupoint stimulation and electroacupuncture for postoperative opioid consumption: a systematic review and meta-analysis of randomised trials. Lund University, 2026.',
    'metadata': {
        'title': 'Perioperative electrical acupoint stimulation for postoperative opioid sparing',
        'subtitle': 'A systematic review and meta-analysis of randomised trials',
        'authors': [
            {'name': 'John Ryan Nual Mendoza', 'affiliations': ['1', '2'], 'role': 'Corresponding author', 'email': 'john_ryan.nual_mendoza@med.lu.se'},
            {'name': 'Siv Katrin Peters', 'affiliations': ['2'], 'role': 'Author, second reviewer'},
            {'name': 'Carina Sjöberg', 'affiliations': ['1'], 'role': 'Author, supervisor'},
            {'name': 'Pether Jildenstål', 'affiliations': ['1'], 'role': 'Author, supervisor'}
        ],
        'affiliations': [
            {'id': '1', 'text': 'Department of Health Sciences, Faculty of Medicine, Lund University, Lund, Sweden'},
            {'id': '2', 'text': 'Region Skåne, Sweden'}
        ],
        'counts': {
            'included_reports': len(characteristics),
            'included_trials': 43,
            'total_participants': 7703,
            'screened_records': len(prisma_reports),
            'excluded_reports': prisma_counts.get('Total excluded', 173),
            'rob_assessments': len(rob_judgements),
            'rob_high_percent': 29,
            'opioid_models': len(models_opioid),
            'other_models': len(models_other),
            'single_trial_estimates': len(single_trial_estimates)
        },
        'primary_summary': {
            'opioid_teas_sham': {
                'trials': 1,
                'participants': 48,
                'study': 'Szmit 2021',
                'md': -7.70,
                'ci_low': -10.62,
                'ci_high': -4.78,
                'unit': 'mg IV MME',
                'certainty': 'Low',
                'reaches_10mg': False,
                'interval_includes_10mg': True
            },
            'opioid_ea_sham': {
                'trials': 0,
                'participants': 0,
                'status': 'No eligible quantitative data'
            },
            'opioid_teas_usual': {
                'trials': 1,
                'participants': 47,
                'study': 'Szmit 2021',
                'md': -8.00,
                'ci_low': -10.92,
                'ci_high': -5.08,
                'unit': 'mg IV MME',
                'certainty': 'Low'
            },
            'opioid_ea_usual': {
                'trials': 2,
                'participants': 159,
                'studies': ['El-Rakshy 2009', 'Seevaunnamtum 2016'],
                'md': -6.83,
                'ci_low': -76.39,
                'ci_high': 62.73,
                'unit': 'mg IV MME',
                'certainty': 'Very low'
            },
            'coprimary_rest_pain': {
                'trials': 1,
                'participants': 60,
                'study': 'Wang 1997',
                'md': -1.03,
                'ci_low': -1.80,
                'ci_high': -0.26,
                'scale': '0-10 VAS/NRS',
                'certainty': 'Low'
            },
            'secondary_ponv': {
                'trials': 9,
                'participants': 2848,
                'rr': 0.60,
                'ci_low': 0.45,
                'ci_high': 0.79,
                'certainty': 'Low'
            },
            'rescue_receipt': {
                'trials': 5,
                'participants': 478,
                'rr': 0.51,
                'ci_low': 0.38,
                'ci_high': 0.69,
                'certainty': 'Low'
            },
            'broader_first_day_e2': {
                'trials': 6,
                'participants': 547,
                'md': -6.67,
                'ci_low': -14.53,
                'ci_high': 1.18,
                'certainty': 'Very low',
                'with_wang_trials': 7,
                'with_wang_participants': 622,
                'with_wang_md': -7.22,
                'with_wang_ci_low': -14.13,
                'with_wang_ci_high': -0.32
            },
            'joint_criterion_status': 'The registered clinical-importance criterion (≥10 mg IV MME reduction + paired ~24h pain upper 95% CI < +1 point) could not be evaluated in the primary trial because Szmit 2021 did not report a 24-hour pain result.'
        }
    },
    'prisma': {
        'counts': prisma_counts,
        'reports': prisma_reports
    },
    'characteristics': characteristics,
    'effect_directions': effect_directions,
    'rob': {
        'judgements': rob_judgements,
        'summary': rob_domain_summary,
        'signalling': rob_signalling,
        'not_assessed': rob_not_assessed,
        'd6_what_ifs': rob_d6_what_ifs
    },
    'grade': grade_profiles,
    'models': {
        'opioid': models_opioid,
        'other': models_other,
        'single_trials': single_trial_estimates,
        'rescue_missing': rescue_missing_outcomes
    },
    'inputs': analysis_inputs,
    'extracted_results': extracted_results,
    'reports_without_result': reports_without_result,
    'conversions': {
        'factors': conversion_factors,
        'prohibited': prohibited_conversions,
        'applied': applied_factors
    },
    'contradictions': {
        'source_contradictions': contradictions,
        'held_decisions': held_decisions
    },
    'rules': rules,
    'search_strategies': {
        'text': af2_text,
        'tables': af2_tables
    },
    'prisma_checklist': {
        'text': af1_text,
        'tables': af1_tables
    },
    'figures': figures_info,
    'manuscript_text': manuscript_sections,
    'downloads': downloads_manifest
}

for target in TARGET_DIRS:
    out_json = target / 'current_review.json'
    out_js = target / 'current_review.js'
    print(f"Writing {out_json}...")
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(review_master, f, indent=2, ensure_ascii=False)

    print(f"Writing {out_js}...")
    with open(out_js, 'w', encoding='utf-8') as f:
        f.write('/* Generated from 44-report BMC Revision folder data; authoritative lock. */\n')
        f.write('window.CURRENT_REVIEW = ')
        json.dump(review_master, f, ensure_ascii=False)
        f.write(';\n')
    print(f"Saved: {out_json} ({out_json.stat().st_size:,} bytes), {out_js} ({out_js.stat().st_size:,} bytes)")

print("Done! Review master data compiled successfully.")

