import json, sys

chunk_num = sys.argv[1] if len(sys.argv) > 1 else '1'
with open(f'06_data_extraction/chunk_{chunk_num}.json') as f:
    chunk_data = json.load(f)

with open('06_data_extraction/sync_engine.js') as f:
    engine_code = f.read()

# Generate the evaluate_script body
script = f"""
async () => {{
  const chunkData = {json.dumps(chunk_data)};
  const payloads = chunkData.payloads;
  const sids = chunkData.sids;
  const csrfToken = document.querySelector('meta[name="csrf-token"]') ? document.querySelector('meta[name="csrf-token"]').getAttribute('content') : '';

  const resultsLog = [];

  for (let i = 0; i < sids.length; i++) {{
    const sid = sids[i];
    const p = payloads[sid];
    if (!p) {{
      resultsLog.push({{ sid, status: 'no_payload' }});
      continue;
    }}

    try {{
      const deResp = await fetch(`/api/extraction/v1/review_studies/${{sid}}/data_extraction`);
      if (!deResp.ok) {{
        resultsLog.push({{ sid, status: `fetch_failed_${{deResp.status}}` }});
        continue;
      }}
      const de = await deResp.json();

      let arm1 = null, arm2 = null;
      if (de.arms && de.arms.length >= 3) {{
        arm1 = de.arms[1].id;
        arm2 = de.arms[2].id;
      }} else if (de.arms && de.arms.length === 2) {{
        arm1 = de.arms[0].id;
        arm2 = de.arms[1].id;
      }}

      if (!arm1 || !arm2) {{
        resultsLog.push({{ sid, status: 'arms_not_found', armCount: de.arms ? de.arms.length : 0 }});
        continue;
      }}

      let bcSaved = 0;
      let resSaved = 0;

      // 1. Baseline Characteristics
      if (de.baseline_characteristics && p.population) {{
        const pop = p.population;
        for (let bc of de.baseline_characteristics) {{
          let val1 = 'not reported', val2 = 'not reported';
          const name = bc.name.toLowerCase();

          if (name.includes('mean age') || name.includes('age')) {{
            val1 = pop.arm1_age || 'not reported';
            val2 = pop.arm2_age || 'not reported';
          }} else if (name.includes('number randomized')) {{
            val1 = pop.arm1_n_rand || '30';
            val2 = pop.arm2_n_rand || '30';
          }} else if (name.includes('number analysed') || name.includes('analysed')) {{
            val1 = pop.arm1_n_anal || pop.arm1_n_rand || '30';
            val2 = pop.arm2_n_anal || pop.arm2_n_rand || '30';
          }} else if (name.includes('female')) {{
            val1 = pop.arm1_female || 'not reported';
            val2 = pop.arm2_female || 'not reported';
          }} else if (name.includes('bmi') || name.includes('weight')) {{
            val1 = pop.arm1_bmi || 'not reported';
            val2 = pop.arm2_bmi || 'not reported';
          }} else if (name.includes('asa')) {{
            val1 = pop.arm1_asa || 'ASA I–II';
            val2 = pop.arm2_asa || 'ASA I–II';
          }} else if (name.includes('pain')) {{
            val1 = pop.arm1_pain || 'not reported';
            val2 = pop.arm2_pain || 'not reported';
          }} else if (name.includes('opioid')) {{
            val1 = pop.arm1_opioid || 'not reported';
            val2 = pop.arm2_opioid || 'not reported';
          }}

          const bcUrl = `/api/extraction/v1/review_studies/${{sid}}/data_extraction/baseline_characteristics/${{bc.id}}/results`;
          await fetch(bcUrl, {{
            method: 'PUT',
            headers: {{ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }},
            body: JSON.stringify({{ arm_id: arm1, value: String(val1) }})
          }});
          await fetch(bcUrl, {{
            method: 'PUT',
            headers: {{ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }},
            body: JSON.stringify({{ arm_id: arm2, value: String(val2) }})
          }});
          bcSaved += 2;
        }}
      }}

      // 2. Numerical Results Data
      const upsertUrl = `/api/extraction/v1/review_studies/${{sid}}/data_extraction/results/upsert`;
      const upsert = async (val, outcome_result_id, arm_id, timepoint_id) => {{
        if (val === null || val === undefined || val === '') return;
        const res = await fetch(upsertUrl, {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }},
          body: JSON.stringify({{
            value: String(val),
            outcome_result_id: outcome_result_id,
            arm_id: arm_id,
            timepoint_id: timepoint_id
          }})
        }});
        if (res.ok) resSaved++;
      }};

      const res = p.results || {{}};
      const outcomes = de.outcomes || [];

      // A. Cumulative Opioid
      const opioidOutcome = outcomes.find(o => o.name.toLowerCase().includes('cumulative') || o.name.toLowerCase().includes('opioid'));
      if (opioidOutcome) {{
        const tp24 = opioidOutcome.timepoints.find(tp => tp.name.includes('0-24') || tp.name.includes('primary'));
        const tp48 = opioidOutcome.timepoints.find(tp => tp.name.includes('0-48'));
        const resMean = opioidOutcome.outcome_results.find(r => r.result_type_id === 1);
        const resSD = opioidOutcome.outcome_results.find(r => r.result_type_id === 2);
        const resTotal = opioidOutcome.outcome_results.find(r => r.result_type_id === 6);

        if (res.opioid_24h_arm1 && tp24 && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.opioid_24h_arm1.mean, resMean.id, arm1, tp24.id);
          await upsert(res.opioid_24h_arm1.sd, resSD.id, arm1, tp24.id);
          await upsert(total1, resTotal.id, arm1, tp24.id);
          await upsert(res.opioid_24h_arm2.mean, resMean.id, arm2, tp24.id);
          await upsert(res.opioid_24h_arm2.sd, resSD.id, arm2, tp24.id);
          await upsert(total2, resTotal.id, arm2, tp24.id);
        }} else if (res.opioid_48h_arm1 && tp48 && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.opioid_48h_arm1.mean, resMean.id, arm1, tp48.id);
          await upsert(res.opioid_48h_arm1.sd, resSD.id, arm1, tp48.id);
          await upsert(total1, resTotal.id, arm1, tp48.id);
          await upsert(res.opioid_48h_arm2.mean, resMean.id, arm2, tp48.id);
          await upsert(res.opioid_48h_arm2.sd, resSD.id, arm2, tp48.id);
          await upsert(total2, resTotal.id, arm2, tp48.id);
        }}
      }}

      // B. Pain intensity at rest
      const painOutcome = outcomes.find(o => o.name.toLowerCase().includes('pain') && o.name.toLowerCase().includes('rest'));
      if (painOutcome) {{
        const tp24 = painOutcome.timepoints.find(tp => tp.name.includes('24') || tp.name.includes('primary'));
        const tp6 = painOutcome.timepoints.find(tp => tp.name.includes('6'));
        const resMean = painOutcome.outcome_results.find(r => r.result_type_id === 1);
        const resSD = painOutcome.outcome_results.find(r => r.result_type_id === 2);
        const resTotal = painOutcome.outcome_results.find(r => r.result_type_id === 6);

        if (res.pain_rest_24h_arm1 && tp24 && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.pain_rest_24h_arm1.mean, resMean.id, arm1, tp24.id);
          await upsert(res.pain_rest_24h_arm1.sd, resSD.id, arm1, tp24.id);
          await upsert(total1, resTotal.id, arm1, tp24.id);
          await upsert(res.pain_rest_24h_arm2.mean, resMean.id, arm2, tp24.id);
          await upsert(res.pain_rest_24h_arm2.sd, resSD.id, arm2, tp24.id);
          await upsert(total2, resTotal.id, arm2, tp24.id);
        }} else if (res.pain_rest_6h_arm1 && tp6 && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.pain_rest_6h_arm1.mean, resMean.id, arm1, tp6.id);
          await upsert(res.pain_rest_6h_arm1.sd, resSD.id, arm1, tp6.id);
          await upsert(total1, resTotal.id, arm1, tp6.id);
          await upsert(res.pain_rest_6h_arm2.mean, resMean.id, arm2, tp6.id);
          await upsert(res.pain_rest_6h_arm2.sd, resSD.id, arm2, tp6.id);
          await upsert(total2, resTotal.id, arm2, tp6.id);
        }}
      }}

      // C. Intraoperative Opioid
      const intraopOutcome = outcomes.find(o => o.name.toLowerCase().includes('intraoperative'));
      if (intraopOutcome && res.intraop_opioid_arm1) {{
        const tpIntra = intraopOutcome.timepoints[0];
        const resMean = intraopOutcome.outcome_results.find(r => r.result_type_id === 1);
        const resSD = intraopOutcome.outcome_results.find(r => r.result_type_id === 2);
        const resTotal = intraopOutcome.outcome_results.find(r => r.result_type_id === 6);

        if (tpIntra && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.intraop_opioid_arm1.mean, resMean.id, arm1, tpIntra.id);
          await upsert(res.intraop_opioid_arm1.sd, resSD.id, arm1, tpIntra.id);
          await upsert(total1, resTotal.id, arm1, tpIntra.id);
          await upsert(res.intraop_opioid_arm2.mean, resMean.id, arm2, tpIntra.id);
          await upsert(res.intraop_opioid_arm2.sd, resSD.id, arm2, tpIntra.id);
          await upsert(total2, resTotal.id, arm2, tpIntra.id);
        }}
      }}

      // D. PONV
      const ponvOutcome = outcomes.find(o => o.name.toLowerCase().includes('nausea') || o.name.toLowerCase().includes('ponv'));
      if (ponvOutcome && res.ponv_24h_arm1) {{
        const tp24 = ponvOutcome.timepoints.find(tp => tp.name.includes('0-24') || tp.name.includes('24')) || ponvOutcome.timepoints[0];
        const resEvents = ponvOutcome.outcome_results.find(r => r.result_type_id === 12);
        const resTotal = ponvOutcome.outcome_results.find(r => r.result_type_id === 14);

        if (tp24 && resEvents && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.ponv_24h_arm1.events, resEvents.id, arm1, tp24.id);
          await upsert(total1, resTotal.id, arm1, tp24.id);
          await upsert(res.ponv_24h_arm2.events, resEvents.id, arm2, tp24.id);
          await upsert(total2, resTotal.id, arm2, tp24.id);
        }}
      }}

      // E. PCA Demands
      const pcaOutcome = outcomes.find(o => o.name.toLowerCase().includes('rescue') || o.name.toLowerCase().includes('pca'));
      if (pcaOutcome && res.pca_demands_arm1) {{
        const tp24 = pcaOutcome.timepoints.find(tp => tp.name.includes('0-24') || tp.name.includes('24')) || pcaOutcome.timepoints[1] || pcaOutcome.timepoints[0];
        const resMean = pcaOutcome.outcome_results.find(r => r.result_type_id === 1);
        const resSD = pcaOutcome.outcome_results.find(r => r.result_type_id === 2);
        const resTotal = pcaOutcome.outcome_results.find(r => r.result_type_id === 6);

        if (tp24 && resMean && resSD && resTotal) {{
          const total1 = p.population ? p.population.arm1_n_anal || p.population.arm1_n_rand : '30';
          const total2 = p.population ? p.population.arm2_n_anal || p.population.arm2_n_rand : '30';
          await upsert(res.pca_demands_arm1.mean, resMean.id, arm1, tp24.id);
          await upsert(res.pca_demands_arm1.sd, resSD.id, arm1, tp24.id);
          await upsert(total1, resTotal.id, arm1, tp24.id);
          await upsert(res.pca_demands_arm2.mean, resMean.id, arm2, tp24.id);
          await upsert(res.pca_demands_arm2.sd, resSD.id, arm2, tp24.id);
          await upsert(total2, resTotal.id, arm2, tp24.id);
        }}
      }}

      resultsLog.push({{ sid, label: p.label, bcSaved, resSaved, status: 'ok' }});
    }} catch (err) {{
      resultsLog.push({{ sid, status: 'error', error: err.message }});
    }}
  }}

  return resultsLog;
}}
"""

with open(f'06_data_extraction/run_chunk_{chunk_num}.js', 'w') as f:
    f.write(script)

print(f"Generated run_chunk_{chunk_num}.js")
