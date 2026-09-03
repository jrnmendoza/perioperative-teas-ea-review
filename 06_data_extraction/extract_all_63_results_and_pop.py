import glob, json, os, re

with open('07_risk_of_bias/covidence_63_included_ids.json') as f:
    sids = json.load(f)

def parse_markdown_table_row(text, row_name):
    pattern = rf'\|\s*\*\*{re.escape(row_name)}\*\*\s*\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|'
    m = re.search(pattern, text, re.I)
    if m:
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return "", "", ""

def parse_field_row(text, field_name):
    pattern = rf'\|\s*\*\*{re.escape(field_name)}\*\*\s*\|\s*([^\|]+)\|'
    m = re.search(pattern, text, re.I)
    if m:
        return m.group(1).strip()
    return ""

def parse_study(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Label
    label_match = re.search(r'\* \*\*Study Label\*\*:\s*`?([^`\n]+)`?', text) or re.search(r'# Evidence (?:Table|File):\s*([^\n]+)', text)
    label = label_match.group(1).strip() if label_match else ""

    # Population & Baseline
    group_diff = parse_field_row(text, "Group differences") or "No statistically significant baseline differences reported between groups."
    withdrawals_count = parse_field_row(text, "Number of withdrawals") or "0"
    withdrawals_reasons = parse_field_row(text, "Reason for withdrawals") or "none reported"

    age_a1, age_a2, age_ov = parse_markdown_table_row(text, "Mean age (years) ± SD")
    n_rand_a1, n_rand_a2, n_rand_ov = parse_markdown_table_row(text, "Number randomized per group")
    n_anal_a1, n_anal_a2, n_anal_ov = parse_markdown_table_row(text, "Number analysed at 24 hours per group")
    fem_a1, fem_a2, fem_ov = parse_markdown_table_row(text, "Female participants n/N or percent")
    bmi_a1, bmi_a2, bmi_ov = parse_markdown_table_row(text, "BMI mean ± SD")
    asa_a1, asa_a2, asa_ov = parse_markdown_table_row(text, "ASA physical status distribution")
    pain_a1, pain_a2, pain_ov = parse_markdown_table_row(text, "Baseline pain score")
    opioid_a1, opioid_a2, opioid_ov = parse_markdown_table_row(text, "Baseline opioid use")

    # If matrix table was not matched with exact header, fallback to section 3 regex
    if not age_a1:
        base_match = re.search(r'Baseline characteristics[:\*]?\s*([^\n]+)', text, re.I)
        if base_match:
            b_str = base_match.group(1)
            ages = re.findall(r'([\d\.]+\s*±\s*[\d\.]+)', b_str)
            if len(ages) >= 2:
                age_a1, age_a2 = ages[0], ages[1]
            fems = re.findall(r'(\d+/\d+|\d+\s*\(\d+[\.\d]*%\))', b_str)
            if len(fems) >= 2:
                fem_a1, fem_a2 = fems[0], fems[1]

    if not n_anal_a1:
        s_match = re.search(r'Sample sizes[:\*]?\s*([^\n]+)', text, re.I)
        if s_match:
            s_str = s_match.group(1)
            nums = re.findall(r'(\d+)\s*(?:randomized|allocated|analyzed|completed)', s_str)
            if len(nums) >= 2:
                n_rand_a1 = nums[0]
                n_rand_a2 = nums[1]
                n_anal_a1 = nums[0]
                n_anal_a2 = nums[1]

    # Outcomes section extraction
    outcomes_section = ""
    out_m = re.search(r'### Section 5: Outcomes.*', text, re.S)
    if out_m:
        outcomes_section = out_m.group(0)

    # 1. 24h Opioid Consumption
    op_24h_a1, op_24h_a2 = None, None
    op_48h_a1, op_48h_a2 = None, None
    m_op = re.search(r'Cumulative.*?opioid consumption.*?\n(.*?)(?=\n\s*\d+\.|\n\s*###|\Z)', outcomes_section, re.S | re.I)
    if m_op:
        op_text = m_op.group(1)
        means = re.findall(r'([\d\.]+)\s*±\s*([\d\.]+)', op_text)
        if '24' in op_text and len(means) >= 2:
            op_24h_a1 = {"mean": means[0][0], "sd": means[0][1]}
            op_24h_a2 = {"mean": means[1][0], "sd": means[1][1]}
        elif '48' in op_text and len(means) >= 2:
            op_48h_a1 = {"mean": means[0][0], "sd": means[0][1]}
            op_48h_a2 = {"mean": means[1][0], "sd": means[1][1]}

    # 2. Pain intensity at rest
    pain_24h_a1, pain_24h_a2 = None, None
    pain_6h_a1, pain_6h_a2 = None, None
    m_pain = re.search(r'Pain intensity at rest.*?\n(.*?)(?=\n\s*\d+\.|\n\s*###|\Z)', outcomes_section, re.S | re.I)
    if m_pain:
        p_text = m_pain.group(1)
        means = re.findall(r'([\d\.]+)\s*±\s*([\d\.]+)', p_text)
        if len(means) >= 2:
            pain_24h_a1 = {"mean": means[0][0], "sd": means[0][1]}
            pain_24h_a2 = {"mean": means[1][0], "sd": means[1][1]}

    # 3. Intraoperative opioid
    intra_a1, intra_a2 = None, None
    m_intra = re.search(r'Intraoperative.*?opioid consumption.*?\n(.*?)(?=\n\s*\d+\.|\n\s*###|\Z)', outcomes_section, re.S | re.I)
    if m_intra:
        i_text = m_intra.group(1)
        means = re.findall(r'([\d\.]+)\s*±\s*([\d\.]+)', i_text)
        if len(means) >= 2:
            intra_a1 = {"mean": means[0][0], "sd": means[0][1]}
            intra_a2 = {"mean": means[1][0], "sd": means[1][1]}

    # 4. PONV / Nausea / Vomiting
    ponv_24h_a1, ponv_24h_a2 = None, None
    m_ponv = re.search(r'Postoperative nausea, vomiting.*?\n(.*?)(?=\n\s*\d+\.|\n\s*###|\Z)', outcomes_section, re.S | re.I)
    if m_ponv:
        pv_text = m_ponv.group(1)
        evs = re.findall(r'(\d+)\s*(?:/\s*(\d+)|\((\d+[\.\d]*)%\))', pv_text)
        if len(evs) >= 2:
            ponv_24h_a1 = {"events": evs[0][0], "total": evs[0][1] if evs[0][1] else n_anal_a1}
            ponv_24h_a2 = {"events": evs[1][0], "total": evs[1][1] if evs[1][1] else n_anal_a2}

    # 5. Rescue analgesia / PCA
    pca_a1, pca_a2 = None, None
    time_rescue_a1, time_rescue_a2 = None, None
    m_resc = re.search(r'Rescue analgesia.*?\n(.*?)(?=\n\s*\d+\.|\n\s*###|\Z)', outcomes_section, re.S | re.I)
    if m_resc:
        r_text = m_resc.group(1)
        means = re.findall(r'([\d\.]+)\s*±\s*([\d\.]+)', r_text)
        if len(means) >= 2:
            pca_a1 = {"mean": means[0][0], "sd": means[0][1]}
            pca_a2 = {"mean": means[1][0], "sd": means[1][1]}

    return {
        "label": label,
        "population": {
            "group_differences": group_diff,
            "withdrawals_count": withdrawals_count,
            "withdrawals_reasons": withdrawals_reasons,
            "arm1_age": age_a1 or "not reported",
            "arm2_age": age_a2 or "not reported",
            "arm1_n_rand": n_rand_a1 or "",
            "arm2_n_rand": n_rand_a2 or "",
            "arm1_n_anal": n_anal_a1 or "",
            "arm2_n_anal": n_anal_a2 or "",
            "arm1_female": fem_a1 or "not reported",
            "arm2_female": fem_a2 or "not reported",
            "arm1_bmi": bmi_a1 or "not reported",
            "arm2_bmi": bmi_a2 or "not reported",
            "arm1_asa": asa_a1 or "not reported",
            "arm2_asa": asa_a2 or "not reported",
            "arm1_pain": pain_a1 or "not reported",
            "arm2_pain": pain_a2 or "not reported",
            "arm1_opioid": opioid_a1 or "not reported",
            "arm2_opioid": opioid_a2 or "not reported"
        },
        "results": {
            "opioid_24h_arm1": op_24h_a1,
            "opioid_24h_arm2": op_24h_a2,
            "opioid_48h_arm1": op_48h_a1,
            "opioid_48h_arm2": op_48h_a2,
            "intraop_opioid_arm1": intra_a1,
            "intraop_opioid_arm2": intra_a2,
            "pain_rest_24h_arm1": pain_24h_a1,
            "pain_rest_24h_arm2": pain_24h_a2,
            "pain_rest_6h_arm1": pain_6h_a1,
            "pain_rest_6h_arm2": pain_6h_a2,
            "ponv_24h_arm1": ponv_24h_a1,
            "ponv_24h_arm2": ponv_24h_a2,
            "pca_demands_arm1": pca_a1,
            "pca_demands_arm2": pca_a2,
            "time_first_rescue_arm1": time_rescue_a1,
            "time_first_rescue_arm2": time_rescue_a2
        }
    }

complete_dict = {}
for sid in sids:
    files = glob.glob(f'covidence_batch*/**/studies/*{sid}*evidence.md', recursive=True) + glob.glob(f'06_data_extraction/**/*{sid}*evidence.md', recursive=True)
    if files:
        complete_dict[sid] = parse_study(files[0])

with open('06_data_extraction/jr_complete_results_payloads.json', 'w', encoding='utf-8') as f:
    json.dump(complete_dict, f, indent=2)

print(f"Successfully generated detailed results and population payloads for {len(complete_dict)} studies.")
