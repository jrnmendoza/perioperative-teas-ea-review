import json

with open('06_data_extraction/jr_complete_results_payloads.json') as f:
    payloads = json.load(f)

with open('07_risk_of_bias/covidence_63_included_ids.json') as f:
    sids = json.load(f)

# Split sids and payloads into 4 chunks of 16
chunks = [sids[i:i+16] for i in range(0, len(sids), 16)]

for i, chunk in enumerate(chunks):
    chunk_payloads = {sid: payloads[sid] for sid in chunk if sid in payloads}
    with open(f'06_data_extraction/chunk_{i+1}.json', 'w') as f:
        json.dump({'sids': chunk, 'payloads': chunk_payloads}, f, indent=2)
    print(f"Chunk {i+1}: {len(chunk)} studies ({len(chunk_payloads)} payloads)")
