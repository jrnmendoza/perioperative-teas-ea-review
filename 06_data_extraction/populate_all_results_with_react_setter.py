import json, time

# Read the extracted results payload
with open('06_data_extraction/jr_complete_results_payloads.json') as f:
    payloads = json.load(f)

with open('07_risk_of_bias/covidence_63_included_ids.json') as f:
    sids = json.load(f)

print(f"Loaded {len(sids)} included study IDs and {len(payloads)} study payloads.")
