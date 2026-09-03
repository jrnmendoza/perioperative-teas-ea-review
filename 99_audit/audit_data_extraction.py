import glob, os, re

evidence_files = sorted(glob.glob('covidence_batch_*/studies/*_evidence.md'))
tsv_files = sorted(glob.glob('covidence_batch_*/studies/*_interventions.tsv'))

print(f"Total evidence files: {len(evidence_files)}")
print(f"Total TSV files: {len(tsv_files)}")

audit_results = []

for ef in evidence_files:
    with open(ef, 'r', encoding='utf-8') as f:
        content = f.read()
    
    basename = os.path.basename(ef)
    
    # Study Label / Key
    label = basename.replace('_evidence.md', '')
    title_m = re.search(r'# Evidence (?:Table|File):\s*(.*)', content)
    if title_m:
        label = title_m.group(1).strip()
    
    # 24-h opioid status
    op_m = re.search(r'\|\s*\*\*24-hour postoperative opioid status\*\*\s*\|\s*([^\|]+)\|', content)
    opioid_status = op_m.group(1).strip() if op_m else "not found"
    
    # 24-h pain at rest
    pr_m = re.search(r'\|\s*\*\*24-hour pain-at-rest status\*\*\s*\|\s*([^\|]+)\|', content)
    pain_rest_status = pr_m.group(1).strip() if pr_m else "not found"
    
    # 24-h movement pain
    pm_m = re.search(r'\|\s*\*\*24-hour movement-pain status\*\*\s*\|\s*([^\|]+)\|', content)
    pain_move_status = pm_m.group(1).strip() if pm_m else "not found"
    
    # 24-h pain unspecified
    pu_m = re.search(r'\|\s*\*\*24-hour pain—activity condition unspecified status\*\*\s*\|\s*([^\|]+)\|', content)
    pain_unspec_status = pu_m.group(1).strip() if pu_m else "not found"
    
    # Primary amendment eligibility
    el_m = re.search(r'\|\s*\*\*Eligibility under the primary-outcome amendment\*\*\s*\|\s*([^\|]+)\|', content)
    eligibility_text = el_m.group(1).strip() if el_m else "not found"
    
    # Design
    des_m = re.search(r'\|\s*\*\*Design\*\*\s*\|\s*([^\|]+)\|', content)
    design = des_m.group(1).strip() if des_m else "not found"
    
    # Anaesthesia
    anes_m = re.search(r'\|\s*\*\*Anaesthesia technique\*\*\s*\|\s*([^\|]+)\|', content)
    anaesthesia = anes_m.group(1).strip() if anes_m else "not found"

    # Surgical category
    surg_m = re.search(r'\|\s*\*\*Surgical category\*\*\s*\|\s*([^\|]+)\|', content)
    surg_cat = surg_m.group(1).strip() if surg_m else "not found"

    # Check companion TSV
    tsv_name = ef.replace('_evidence.md', '_interventions.tsv')
    tsv_exists = os.path.exists(tsv_name)
    tsv_row_count = 0
    tsv_cols = 0
    if tsv_exists:
        with open(tsv_name, 'r', encoding='utf-8') as tf:
            tlines = [tl.strip() for tl in tf.readlines() if tl.strip()]
            tsv_row_count = len(tlines) - 1 # excluding header
            if len(tlines) > 0:
                tsv_cols = len(tlines[0].split('\t')) - 2 # excluding Row and Field columns
    
    audit_results.append({
        'file': ef,
        'label': label,
        'opioid_status': opioid_status,
        'pain_rest_status': pain_rest_status,
        'pain_move_status': pain_move_status,
        'pain_unspec_status': pain_unspec_status,
        'eligibility': eligibility_text,
        'design': design,
        'anaesthesia': anaesthesia,
        'surgical_category': surg_cat,
        'tsv_exists': tsv_exists,
        'tsv_rows': tsv_row_count,
        'tsv_arms': tsv_cols
    })

print("\n=== AUDIT MATRIX SUMMARY (29 EVIDENCE DOSSIERS) ===\n")
for r in audit_results:
    print(f"Study: {r['label']}")
    print(f"  Opioid: {r['opioid_status']} | Pain Rest: {r['pain_rest_status']} | Pain Move: {r['pain_move_status']} | Pain Unspec: {r['pain_unspec_status']}")
    print(f"  Surg: {r['surgical_category']} | Anesthesia: {r['anaesthesia'][:50]}... | TSV: {r['tsv_rows']} rows, {r['tsv_arms']} arms")
    print("-" * 60)
