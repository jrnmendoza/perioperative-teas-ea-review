import json

with open('06_data_extraction/jr_complete_results_payloads.json') as f:
    payloads = json.load(f)

with open('07_risk_of_bias/covidence_63_included_ids.json') as f:
    sids = json.load(f)

print(f"Loaded {len(sids)} studies and {len(payloads)} payloads.")

# Write a combined data dictionary to a JS file that can be loaded in browser
with open('06_data_extraction/all_payloads_bundle.js', 'w') as f:
    f.write('window.__COVIDENCE_PAYLOADS = ' + json.dumps(payloads, indent=2) + ';\n')
    f.write('window.__COVIDENCE_SIDS = ' + json.dumps(sids, indent=2) + ';\n')

print("Saved all_payloads_bundle.js")
