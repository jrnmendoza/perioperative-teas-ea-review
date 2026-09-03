import json

with open('06_data_extraction/jr_complete_results_payloads.json') as f:
    payloads = json.load(f)

with open('07_risk_of_bias/covidence_63_included_ids.json') as f:
    sids = json.load(f)

chunks = [
    sids[0:16],
    sids[16:32],
    sids[32:48],
    sids[48:63]
]

for idx, chunk in enumerate(chunks):
    chunk_payloads = {sid: payloads[sid] for sid in chunk if sid in payloads}
    js = f"window.__COVIDENCE_PAYLOADS = Object.assign(window.__COVIDENCE_PAYLOADS || {{}}, {json.dumps(chunk_payloads)});\n"
    if idx == 0:
        js = f"window.__COVIDENCE_SIDS = {json.dumps(sids)};\n" + js
    with open(f'06_data_extraction/payload_chunk_{idx+1}.js', 'w') as f:
        f.write(js)
    print(f"Payload chunk {idx+1}: {len(chunk)} studies, file size: {len(js)} bytes")
