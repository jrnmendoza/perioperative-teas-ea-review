import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DASH = ROOT / 'dashboard'

def build():
    cr_path = DASH / 'current_review.json'
    if not cr_path.exists():
        print("current_review.json not found")
        return
        
    data = json.loads(cr_path.read_text())
    
    graph = {
        'studies': {},
        'models': {},
        'results': {}
    }
    
    # 1. Initialize Studies
    for s in data.get('studies', []):
        sid = s['report_id']
        bg = data.get('background', {}).get(sid, {})
        graph['studies'][sid] = {
            'canonical': s,
            'background': bg,
            'models': [],
            'results': [],
            'rob': [],
            'inputs': []
        }
        
    # Gather all models
    all_models = list(data.get('models', []))
    all_models += data.get('qor_analysis', {}).get('main_models', [])
    all_models += data.get('qor_analysis', {}).get('diagnostics', [])
    all_models += data.get('qor_later_models', [])
    all_models += data.get('e2_analysis', {}).get('models', [])
    
    # 2. Initialize Models
    for m in all_models:
        mid = m['model_id']
        grade = next((g for g in data.get('grade', []) if g['model_id'] == mid), None)
        graph['models'][mid] = {
            'canonical': m,
            'grade': grade,
            'studies': [],
            'results': [],
            'inputs': []
        }
        
    # Gather all RoB
    all_rob = list(data.get('rob', []))
    all_rob += data.get('qor_analysis', {}).get('rob', [])
    all_rob += data.get('qor_later_rob', [])
    
    # 3. Results / RoB
    for r in all_rob:
        rid = r['result_id']
        sid = r['study']
        graph['results'][rid] = {
            'rob': r,
            'study': sid,
            'models': []
        }
        if sid not in graph['studies']:
            graph['studies'][sid] = {
                'canonical': {'report_id': sid}, 'background': {}, 'models': [], 'results': [], 'rob': [], 'inputs': []
            }
        if rid not in graph['studies'][sid]['rob']:
            graph['studies'][sid]['rob'].append(rid)
        if rid not in graph['studies'][sid]['results']:
            graph['studies'][sid]['results'].append(rid)

    # Gather all inputs
    all_inputs = list(data.get('inputs', []))
    for m in data.get('qor_analysis', {}).get('main_models', []) + data.get('qor_analysis', {}).get('diagnostics', []):
        for inp in m.get('inputs', []):
            inp_copy = dict(inp)
            inp_copy['model_id'] = m['model_id']
            all_inputs.append(inp_copy)
    for m in data.get('qor_later_models', []):
        for inp in m.get('inputs', []):
            inp_copy = dict(inp)
            inp_copy['model_id'] = m['model_id']
            all_inputs.append(inp_copy)
    for m in data.get('e2_analysis', {}).get('models', []):
        sids = m.get('studies', '').split(';') if isinstance(m.get('studies'), str) else m.get('studies', [])
        rids = m.get('contrast_ids', '').split(';') if isinstance(m.get('contrast_ids'), str) else m.get('contrast_ids', [])
        for sid, rid in zip(sids, rids):
            if sid and rid:
                all_inputs.append({'study': sid.strip(), 'model_id': m['model_id'], 'result_id': rid.strip()})

    # 4. Links from Inputs
    for inp in all_inputs:
        sid = inp['study']
        mid = inp['model_id']
        composite_rid = inp['result_id']
        
        if sid not in graph['studies']:
            graph['studies'][sid] = {
                'canonical': {'report_id': sid}, 'background': {}, 'models': [], 'results': [], 'rob': [], 'inputs': []
            }
            
        graph['studies'][sid]['inputs'].append(inp)
        if mid not in graph['studies'][sid]['models']:
            graph['studies'][sid]['models'].append(mid)
            
        if mid in graph['models']:
            graph['models'][mid]['inputs'].append(inp)
            if sid not in graph['models'][mid]['studies']:
                graph['models'][mid]['studies'].append(sid)
                
        # Handle composite results for both study and model mapping
        for rid in composite_rid.split('+'):
            if rid not in graph['studies'][sid]['results']:
                graph['studies'][sid]['results'].append(rid)
            if rid not in graph['models'][mid]['results']:
                graph['models'][mid]['results'].append(rid)
                
            if rid not in graph['results']:
                graph['results'][rid] = {'study': sid, 'models': []}
            if mid not in graph['results'][rid]['models']:
                graph['results'][rid]['models'].append(mid)

    (DASH / 'evidence_graph.json').write_text(json.dumps(graph, indent=2))
    (DASH / 'evidence_graph.js').write_text("window.EVIDENCE_GRAPH = " + json.dumps(graph) + ";\n")
    print("Graph built successfully.")

if __name__ == '__main__':
    build()
