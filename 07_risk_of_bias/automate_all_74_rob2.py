import csv, json, time, os

# Load master assessments
studies = []
with open('07_risk_of_bias/rob2_master_assessment.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        studies.append(row)

print(f"Loaded {len(studies)} study assessments.")

# We will generate a structured JS injection payload for each study that can be executed in page
def generate_study_js(s):
    d1_judg = s['d1_judgment']
    d1_com = f"Random sequence: {s['d1_random_sequence']}; Allocation concealment: {s['d1_allocation_concealment']}; Baseline balance: {s['d1_baseline_balance']}."
    
    d2_judg = s['d2_judgment']
    d2_com = f"Participant awareness: {s['d2_participant_blinding']}; Personnel awareness: {s['d2_personnel_blinding']}; Context deviations: {s['d2_protocol_deviations']}; ITT analysis: {s['d2_itt_analysis']}."
    
    d3_judg = s['d3_judgment']
    d3_com = f"Outcome data completeness: {s['d3_data_completeness']}; Missingness bias evidence: {s['d3_missing_not_biased']}."
    
    d4_judg = s['d4_judgment']
    d4_com = f"Outcome measurement validity: {s['d4_measurement_validity']}; Assessor awareness: {s['d4_assessor_blinding']}."
    
    d5_judg = s['d5_judgment']
    d5_com = f"Prospective protocol registration: {s['d5_selective_reporting']}; Outcome selection: {s['d5_outcome_selection']}."
    
    ov_judg = s['overall_rob']
    ov_com = f"Overall Cochrane RoB 2 summary judgment: {ov_judg} risk of bias. {s['rob_support_rationale']}"
    
    judgements = [
        {"judg": d1_judg, "comment": d1_com},
        {"judg": d2_judg, "comment": d2_com},
        {"judg": d3_judg, "comment": d3_com},
        {"judg": d4_judg, "comment": d4_com},
        {"judg": d5_judg, "comment": d5_com},
        {"judg": ov_judg, "comment": ov_com}
    ]
    return judgements

# Save precompiled payloads
with open('07_risk_of_bias/study_payloads.json', 'w', encoding='utf-8') as f:
    payloads = {}
    for s in studies:
        payloads[s['study_id']] = {
            'study_key': s['study_key'],
            'citation': s['citation'],
            'judgements': generate_study_js(s)
        }
    json.dump(payloads, f, indent=2)

print("Generated and saved study_payloads.json for all 74 studies.")
