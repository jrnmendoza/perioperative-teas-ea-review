/* v38 canonical dashboard. No historical pooled or study-overall RoB inference. */
(() => {
  'use strict';
  const d=window.CURRENT_REVIEW, $=id=>document.getElementById(id);
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num=(x,n=2)=>x===null||x===undefined||x===''?'—':Number(x).toFixed(n);
  const grade=new Map(d.grade.map(g=>[g.model_id,g]));
  const effect=m=>m.k?`${num(m.display_effect)} [${num(m.display_ci_low)}, ${num(m.display_ci_high)}] ${esc(m.unit)}`:'No eligible quantitative evidence';
  const table=(heads,rows)=>`<div class="table-scroll"><table><thead><tr>${heads.map(h=>`<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  const tag=x=>`<span class="tag ${x==='High'?'risk-high':x==='Low'?'risk-low':''}">${esc(x)}</span>`;
  const note=t=>`<p class="note">${t}</p>`;
  const qorLink=()=>d.qor_analysis?note('QoR addendum: three ~24-hour syntheses, eight additional exact-result assessments and three Very-low-certainty judgments. <button type="button" class="text-button" data-view="qor">View QoR results, RoB and GRADE</button>. The v38 core below is preserved.'):'';
  const models=role=>d.models.filter(m=>role.includes(m.role));
  const primary=models(['PRINCIPAL','SUPPORTIVE']);
  const modelTable=ms=>table(['Evidence body / role','k / N','Estimate [95% CI]','Certainty'],ms.map(m=>[`<button class="text-button model-link" data-model="${esc(m.model_id)}">${esc(m.model_id)}</button><br><small>${esc(m.role)}</small>`,`${m.k} / ${m.N}`,effect(m),tag(grade.get(m.model_id)?.certainty||'Diagnostic — not graded') ]));
  function title(h,p=''){return `<h2>${h}</h2>${p?`<p class="lede">${p}</p>`:''}`;}
  function overview(){return title('Evidence, with its limits','v38 core · 20 September 2026 · E2 sensitivity analysis · 23 September 2026 · PROSPERO CRD420261452908')+
    `<div class="summary-grid"><article><span class="eyebrow">Evidence inventory</span><strong>70 reports · 69 families</strong><p>12,103 randomized participants, operational count. This is not an analysed efficacy population. Yeh probable overlap counted once and held out of models.</p></article><article><span class="eyebrow">Review complete under delegation</span><strong>94 RoB assessments · 38 GRADE bodies</strong><p>All 90 current non-sensitivity component results covered. Four empty bodies not rated. New judgments are AI-conducted; prior human completion is user-reported.</p></article></div>`+
    qorLink()+`<h3>Primary question</h3>${modelTable(primary)}${note('No body establishes ≥10mg opioid sparing together with paired ~24h pain upper CI &lt;+1. Separate pain evidence cannot supply Szmit’s missing paired fixed-24h measurement. A one-study estimate is not a pooled meta-analysis.')}`+
    `<h3>What changed</h3><ul><li>Wu 2016 recorded as citation-search evidence; full-text dispositions reconciled.</li><li>Risk-of-bias and all 38 certainty decisions adopted; no reviewer approval queue.</li><li>Zheng’s unresolved continuous data held out of main models; original values retained in diagnostics.</li><li>Wu 2025 intraoperative dose preceded treatment and is now diagnostic only.</li><li>The 24-h QoR addendum (3 Very-low-certainty bodies).</li><li>Later-window QoR models, ungraded.</li><li>The E2 post-hoc sensitivity analysis, with E1 retained as primary. <button type="button" class="text-button" data-view="results">See E2 results</button>.</li></ul>`+
    note('The 12-reference import gap and historical outcome-focused exclusion limitation remain disclosed.');}
  function forest(m){
    const rows=d.inputs.filter(r=>r.model_id===m.model_id);if(!rows.length)return '';
    const pts=rows.map(r=>({name:r.study,y:+r.yi,lo:+r.yi-1.95996398454*Math.sqrt(+r.vi),hi:+r.yi+1.95996398454*Math.sqrt(+r.vi)}));
    pts.push({name:m.k===1?'Study estimate':'REML / safeguarded HK',y:m.effect,lo:m.ci_low,hi:m.ci_high,total:true});
    let lo=Math.min(0,...pts.map(p=>p.lo)),hi=Math.max(0,...pts.map(p=>p.hi));const span=hi-lo||1;lo-=span*.07;hi+=span*.07;
    const x=v=>250+(v-lo)/(hi-lo)*410,ht=50+pts.length*35;
    const display=v=>num(m.measure==='RR'?Math.exp(v):v);
    return `<div class="forest-wrap"><svg viewBox="0 0 960 ${ht}" role="img" aria-label="Forest plot for ${esc(m.model_id)}"><line x1="${x(0)}" x2="${x(0)}" y1="12" y2="${ht-27}" stroke="#64748b" stroke-dasharray="4 4"/>${pts.map((p,i)=>{const y=28+i*35;return `<text x="8" y="${y+4}" fill="#dbeafe" font-size="13">${esc(p.name)}</text><line x1="${x(p.lo)}" x2="${x(p.hi)}" y1="${y}" y2="${y}" stroke="${p.total?'#5eead4':'#93c5fd'}" stroke-width="2"/><circle cx="${x(p.y)}" cy="${y}" r="${p.total?6:4}" fill="${p.total?'#5eead4':'#93c5fd'}"/><text x="682" y="${y+4}" fill="#dbeafe" font-size="13">${display(p.y)} [${display(p.lo)}, ${display(p.hi)}]</text>`;}).join('')}<text x="250" y="${ht-5}" fill="#94a3b8" font-size="12">${m.measure==='RR'?'Risk ratio (log axis; null = 1)':'Difference (null = 0)'} · ${esc(m.unit)}</text></svg></div>`;
  }
  function modelDetail(mid){
    const m=d.models.find(m=>m.model_id===mid);if(!m)return;
    const s=d.specifications.find(s=>s.model_id===mid),g=grade.get(mid),ins=d.inputs.filter(r=>r.model_id===mid);
    const panel=$('model-panel');panel.innerHTML=title(esc(mid),`${esc(m.role)} · ${esc(m.status)} · k=${m.k}, N=${m.N}`)+`<p class="estimate">${effect(m)}</p>`+forest(m)+note(esc((s.note||'Separate modality/comparator body. Compatible active arms combined; control counted once.').replace('mg/ug', 'mg/µg')))+
    (m.k>1?`<p>I² ${num(m.I2,1)}% · τ² ${num(m.tau2,3)} · safeguarded Hartung–Knapp interval.</p>`:'')+
    (m.pi_low!==null&&m.pi_low!==undefined?`<p>Prediction interval: ${num(m.measure==='RR'?Math.exp(m.pi_low):m.pi_low)} to ${num(m.measure==='RR'?Math.exp(m.pi_high):m.pi_high)} ${esc(m.unit)}. Interpret cautiously.</p>`:'')+
    table(['Contributor / exact result IDs','n intervention / control','Source location'],ins.map(r=>[`${esc(r.study)}<br><small>${esc(r.result_id)}</small>`,`${num(r.n_i,0)} / ${num(r.n_c,0)}`,esc(r.source_location)]))+
    (g?`<h3>GRADE: ${esc(g.certainty)}</h3>${['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias'].map(k=>`<p><strong>${esc(k.replaceAll('_',' '))} (−${g[k+'_downgrades']})</strong> — ${esc(g[k])}</p>`).join('')}`:note('Diagnostic only. Not an independently graded efficacy conclusion.'));
    panel.hidden=false;panel.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function e2_section() {
    if(!d.e2_analysis) return '';
    const e2 = d.e2_analysis;
    const est = m => m ? `${num(m.effect)} [${num(m.ci_low)}, ${num(m.ci_high)}]` : '—';
    const mainE2 = e2.models.filter(m => m.role === 'E2 POST-HOC SENSITIVITY (main)');
    
    const removeDups = ms => ms.filter(m => !['E2_TEAS_sham_leaveout_Gu2019', 'E2_TEAS_sham_leaveout_Lee2011', 'E2_TEAS_sham_excl_unstated_route', 'E2_EA_usual_leaveout_ElRakshy', 'E2_TEAS_sham_E1_restriction'].includes(m.model_id));
    const teasAll = removeDups(e2.models.filter(m => m.body === 'TEAS vs sham' && m.role !== 'E2 POST-HOC SENSITIVITY (main)'));
    const eaAll = removeDups(e2.models.filter(m => m.body === 'EA vs usual care' && m.role !== 'E2 POST-HOC SENSITIVITY (main)'));

    const teasSens = teasAll.filter(m => !m.model_id.includes('_LOO_'));
    const teasLoo = teasAll.filter(m => m.model_id.includes('_LOO_'));
    const eaSens = eaAll.filter(m => !m.model_id.includes('_LOO_'));
    const eaLoo = eaAll.filter(m => m.model_id.includes('_LOO_'));

    const getLabel = m => (d.e2_labels && d.e2_labels[m.model_id]) ? d.e2_labels[m.model_id] : esc((m.note || 'E2 main').replace('mg/ug', 'mg/µg'));

    const estTable = (m2, m1) => {
        const piText = (m2.k >= 5 && m2.pi_low !== null && m2.pi_high !== null) ? `PI ${num(m2.pi_low)} to ${num(m2.pi_high)}` : 'PI not shown (k<5)';
        const hetero = (m2.k > 1 && m2.I2 !== null) ? `<br><small>I² ${num(m2.I2, 1)}%, ${piText}</small>` : '<br><small>—</small>';
        const caveat = m2.body === 'EA vs sham' ? '<br><small>Lin 2002 only; admitted on a boundary reading of DP1 (PCA from hour 1) and DP4 (unquantified IM pethidine first-hour rescue); high risk of bias</small>' : '';
        return [
          esc(m2.body),
          m1 && m1.k ? `${m1.k} / ${m1.N}` : '0 / 0',
          m1 && m1.k ? effect(m1).replace(' mg IV MME', '') : 'No eligible data',
          `${m2.k} / ${m2.N}`,
          est(m2) + hetero + caveat,
          tag('Not graded')
        ];
    };

    const teasMain = mainE2.find(m=>m.model_id==='E2_opioid24_TEAS_sham');
    const teasModels = [teasMain, ...teasSens, ...teasLoo];
    const crossesZero = teasModels.filter(m => m.ci_high > 0).length;
    const noneReaches = teasModels.filter(m => m.effect > -10).length;
    const total = teasModels.length;
    const crossZeroText = crossesZero === total ? 'All ' + total + ' TEAS-vs-sham E2 analyses cross zero' : crossesZero + ' of ' + total + ' TEAS-vs-sham E2 analyses cross zero';
    const noneReachesText = noneReaches === total ? 'none reaches -10 mg.' : (total - noneReaches) + ' reaches -10 mg.';
    const teasCaption = `${crossZeroText}; ${noneReachesText}`;

    const looRange = (loo) => {
        if (!loo.length) return '';
        const min = Math.min(...loo.map(m => m.effect));
        const max = Math.max(...loo.map(m => m.effect));
        return note(`Leave-one-out range: ${num(min)} to ${num(max)} mg.`);
    };

    const opioidLimb = m => {
        if (!m) return 'Not met';
        if (m.ci_high < -10) return `Met (${num(m.effect)})`;
        if (m.effect <= -10) return `Met by point estimate (${num(m.effect)}), k=${m.k}`;
        return 'Not met';
    };
    const painLimb = m => {
        if (!m || (m.effect > -10)) return '—';
        if (m.body === 'EA vs sham') return 'Cannot be evaluated: Lin 2002 reports pain only in a figure (Fig. 1) and has no eligible ~24-h pain result; pain from other trials cannot supply the pairing.';
        return 'Not met';
    };
    const jointText = m => {
        if (!m || (m.effect > -10)) return 'Not met';
        if (m.body === 'EA vs sham') return 'Cannot be evaluated';
        return 'Not met';
    };
    const e2PainConstant = 'As stated in E2_RESULTS.md, digitising Lin 2002 Fig. 1 has not been done and would be a further post-hoc decision.';

    const jointRows = [
        'TEAS vs sham', 'TEAS vs usual care', 'EA vs sham', 'EA vs usual care'
    ].map(b => {
        const m = mainE2.find(x => x.body === b);
        return [b, opioidLimb(m), painLimb(m), jointText(m)];
    });

    return `<h3>E2 post-hoc sensitivity analysis</h3>` +
      note('E1 stays primary. E2 is post-hoc, defined and amended (E2.1) after data were seen, and the decision to keep E1 primary was made after the E2 results were known.') +
      table(['Body', 'E1 k / N', 'E1 Estimate [95% CI]', 'E2 k / N', 'E2 Estimate [95% CI]', 'E2 Certainty'], mainE2.map(m2 => {
        const m1 = primary.find(m => m.model_id === 'opioid24_' + m2.model_id.replace('E2_opioid24_', ''));
        return estTable(m2, m1);
      })) +
      `<h4>TEAS vs sham — sensitivity analyses</h4>` +
      note(teasCaption) +
      table(['Analysis', 'k', 'MD [95% CI]'], [teasMain, ...teasSens].map(m => [getLabel(m), m.k, est(m)])) +
      (() => {
        const e1Rest = e2.models.find(m => m.model_id === 'E2_TEAS_sham_E1_restriction');
        return e1Rest ? note(`The registered E1 primary (${esc(e1Rest.studies)} only; k=${e1Rest.k}, N=${e1Rest.N}): ${est(e1Rest)}`) : '';
      })() +
      `<h4>TEAS vs sham — leave-one-out</h4>` +
      looRange(teasLoo) +
      table(['Analysis', 'k', 'MD [95% CI]'], teasLoo.map(m => [getLabel(m), m.k, est(m)])) +
      `<h4>EA vs usual care — sensitivity analyses</h4>` +
      table(['Analysis', 'k', 'MD [95% CI]'], [mainE2.find(m=>m.model_id==='E2_opioid24_EA_usual'), ...eaSens].map(m => [getLabel(m), m.k, est(m)])) +
      `<h4>EA vs usual care — leave-one-out</h4>` +
      looRange(eaLoo) +
      table(['Analysis', 'k', 'MD [95% CI]'], eaLoo.map(m => [getLabel(m), m.k, est(m)])) +
      `<h4>Joint criterion (≥10 mg sparing and paired pain upper limit &lt; +1)</h4>` +
      table(['Body', 'Opioid limb', 'Pain limb', 'Joint criterion'], jointRows) +
      note(e2PainConstant);
  }
  function results(){return title('Results and diagnostics','Fixed canonical analyses. Selecting a model does not silently change study membership.')+`<label for="model-select">Evidence body</label><select id="model-select"><option value="">Choose a model…</option>${['PRINCIPAL','SUPPORTIVE','ADDITIONAL','SENSITIVITY'].map(role=>`<optgroup label="${role}">${d.models.filter(m=>m.role===role).map(m=>`<option value="${esc(m.model_id)}">${esc(m.model_id)} · k=${m.k}</option>`).join('')}</optgroup>`).join('')}</select><div id="model-panel" class="panel" hidden></div><h3>Principal and supportive</h3>${modelTable(primary)}<h3>Additional outcomes</h3>${modelTable(models(['ADDITIONAL']))}<details><summary>36 explicitly labelled sensitivity / diagnostic models</summary>${modelTable(models(['SENSITIVITY']))}</details>`+e2_section();}
  function prisma(){const p=d.prisma;return title('Selection and accounting','Historical aggregate screening counts, reconciled full-text record dispositions and a separate citation route.')+
    `<div class="flow-grid"><section><h3>Database route</h3><div class="flow-box">5100 raw references<br><small>Embase 1928 · CENTRAL 1698 · CINAHL 465 · PubMed 1009</small></div><div class="flow-arrow">↓</div><div class="flow-box">5088 reported imports<br><small>12-reference difference: mapping unavailable</small></div><div class="flow-arrow">↓ 1651 automatic duplicates + 1 manual duplicate + 508 automation removals</div><div class="flow-box">2928 screened → 2704 excluded</div><div class="flow-arrow">↓</div><div class="flow-box">224 reports sought → 2 not retrieved</div><div class="flow-arrow">↓</div><div class="flow-box">222 retrieved records → 6 late duplicates removed</div><div class="flow-arrow">↓</div><div class="flow-box">216 distinct reports assessed → 147 excluded</div><div class="flow-arrow">↓</div><div class="flow-box highlight">69 included database reports</div></section><section><h3>Citation route</h3><div class="flow-box">Wu 2016 · 1 report<br><small>Citation-search origin confirmed by user</small></div><div class="flow-arrow">↓</div><div class="flow-box">1 sought · 1 retrieved · 1 assessed</div><div class="flow-arrow">↓</div><div class="flow-box highlight">1 included citation report</div><h3>Combined evidence inventory</h3><div class="flow-box highlight">70 reports<br>69 operational trial families</div></section></div>`+
    table(['Full-text exclusion reason','Records'],Object.entries(p.exclusion_reasons).map(([r,n])=>[esc(r),n]))+
    note('147 substantive report exclusions are separate from six exact DOI/title duplicate records removed late. Zhang’s distinct conference abstract remains Abstract only. Six formerly excluded reports reinstated locally; original Covidence decisions are preserved in the downloadable ledger.')+p.caveats.map(c=>note(esc(c))).join('');}
  function evidence(){return title('Certainty of evidence','38 bodies reviewed and adopted under delegation: 34 rated, four empty. No sensitivity is given a standalone efficacy grade.')+table(['Body','Certainty','Downgrades: bias / inconsistency / indirectness / imprecision / publication','Decision'],d.grade.map(g=>[`<button class="text-button model-link" data-model="${esc(g.model_id)}">${esc(g.model_id)}</button>`,tag(g.certainty),['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias'].map(k=>g[k+'_downgrades']).join(' / '),esc(g.decision_status)]))+note('Select an evidence body to inspect all five rationales, its estimate and contributors. Moderate-certainty standalone pain evidence does not establish the joint opioid-and-pain criterion.');}
  function risk(){return title('Result-specific risk of bias','94 fresh assessments cover all 90 current non-sensitivity components plus four held/diagnostic results. No study-overall rating is substituted for an outcome-specific assessment.')+`<label for="risk-search">Find study, outcome, result ID or judgment</label><input id="risk-search" type="search" placeholder="e.g. Luo, nausea, V33-OD-0139"><div id="risk-list"></div>`+note('AI-conducted assessment under user delegation, dated 20 September 2026. Prior human completion is user-reported. Complete domain rationales and source locators are downloadable. Other historical/sensitivity results without fresh assessment are not silently called Low risk.');}
  function riskRows(q=''){$('risk-list').innerHTML=d.rob.filter(r=>`${r.study} ${r.outcome} ${r.result_id} ${r.overall}`.toLowerCase().includes(q.toLowerCase())).map(r=>`<details><summary>${esc(r.study)} · ${esc(r.outcome)} · ${tag(r.overall)}<br><small>${esc(r.result_id)} · ${esc(r.window)} · n=${esc(r.population)}</small></summary><p>${esc(r.comparison)}</p>${[1,2,3,4,5].map(i=>`<p><strong>D${i}: ${esc(r['d'+i])}</strong> — ${esc(r['d'+i+'_rationale'])}</p>`).join('')}<p>${esc(r.overall_rationale)}</p><p class="source">${esc(r.source_pdf)} · ${esc(r.result_location)}</p></details>`).join('');}
  function studies(){return title('Study explorer','Canonical report inventory, model contribution and article figures. RoB is shown by result, never as a single inherited study label.')+`<label for="study-search">Find a report</label><input id="study-search" type="search" placeholder="Study name or year"><div id="study-list"></div>`;}
  function studyRows(q=''){$('study-list').innerHTML=d.studies.filter(s=>s.report_id.toLowerCase().includes(q.toLowerCase())).map(s=>{
    const ms=d.models.filter(m=>m.studies.split(';').map(x=>x.trim()).includes(s.report_id)),rs=d.rob.filter(r=>r.study===s.report_id),fs=window.ARTICLE_FIGURES?.[s.report_id]||[];
    return `<details><summary>${esc(s.report_id)} · ${esc(s.modality)}<br><small>${esc(s.comparator)} · randomized n=${s.randomized_n_report}; counted n=${s.randomized_n_counted}</small></summary><p>${esc(s.notes)}</p><p class="source">${esc(s.source_pdf)}<br>SHA-256: ${esc(s.source_sha256)}</p><p>Trial family: ${esc(s.trial_id)} · ${esc(s.n_source_excerpt)}</p><h3>Current models (${ms.length})</h3>${ms.length?modelTable(ms):note('No current quantitative contribution; retained inventory/eligibility/source hold is not an efficacy claim.')}<h3>Fresh result-specific assessments (${rs.length})</h3>${rs.length?table(['Result','Outcome','Overall'],rs.map(r=>[esc(r.result_id),esc(r.outcome),tag(r.overall)])):note('No fresh v38 assessment needed for a current non-sensitivity contribution. Historical assessments are not displayed as current study-wide judgments.')}<h3>Article figures (${fs.length})</h3><div class="figure-grid">${fs.map(f=>`<figure><button class="figure-open" data-src="${esc(f.src)}" data-caption="${esc(s.report_id+' · '+f.caption)}"><img src="${esc(f.src)}" loading="lazy" alt="${esc(s.report_id+' '+f.caption)}"></button><figcaption>${esc(f.caption)}</figcaption></figure>`).join('')}</div></details>`;}).join('');}
  function methods(){return title('Methods and adopted decisions','Posthoc adjudication with results known. No reviewer approval is awaited for these decisions.')+d.policies.map(p=>`<details><summary>${esc(p.topic)} · ${esc(p.status)}</summary><p>${esc(p.decision)}</p></details>`).join('')+`<h3>Search strategies</h3>${(window.SEARCH_STRATEGIES||[]).map(s=>`<details><summary>${esc(s.name)} · ${esc(s.date)} · ${s.hits} records</summary><p>${esc(s.platform)} · ${esc(s.status)}</p><pre>${esc(s.strategy_text)}</pre><p class="source">${esc(s.source)}</p></details>`).join('')}`+note('Current R/metafor and independent Python validation results are in Downloads. Reproduction establishes computational consistency, not source truth or exhaustive selection.');}
  function downloads(){return title('Data and audit downloads','Preserved v38 core plus clearly labelled coverage and QoR addenda. Historical versions remain in the project baseline.')+`<div class="download-grid">${d.downloads.map(x=>`<a class="download" href="${esc(x.href)}" download>${esc(x.label)}<small>${esc(x.href.split('/').pop())}</small></a>`).join('')}</div>`;}
  function coverage(){
    const c=d.outcome_coverage;
    if(!c)return title('Outcome coverage')+note('No coverage addendum loaded.');
    return title('Harms and patient-reported recovery','Coverage addendum · 20 September 2026 · All 70 included report texts checked')+
      `<div class="summary-grid"><article><span class="eyebrow">Recovery evidence exists</span><strong>${c.qor_reports} QoR reports</strong><p>${c.satisfaction_reports} satisfaction/willingness reports; ${c.quality_of_life_reports} additional quality-of-life reports; ${c.acceptability_reports} additional acceptability reports. Categories can overlap.</p></article><article><span class="eyebrow">Reporting limits</span><strong>No eligible persistent-opioid-use result located</strong><p>Registered window: beyond 30 days. Long-term pain follow-up is not opioid-use follow-up. Missing reporting is not zero events.</p></article></div>`+
      (d.qor_analysis?qorLink()+note('The table below preserves the original coverage-audit dispositions. Its candidate / awaiting-assessment labels describe that earlier audit, not the current status of the eight ~24-hour results now assessed in the QoR analysis tab. Other windows and source holds remain separate.'):note('Coverage and descriptive extraction are complete within available-source scope. New QoR meta-analyses and exact-result RoB/GRADE remain to be done.'))+
      `<h3>Recovery, satisfaction and acceptability</h3>`+
      table(['Report / instrument','Timing / population','Source values','Synthesis decision'],c.recovery.map(r=>[`${esc(r.study)}<br><strong>${esc(r.instrument)}</strong><br><small>PDF p${esc(r.pdf_pages)}</small>`,`${esc(r.window)}<br>${esc(r.population)}`,esc(r.source_values),esc(r.synthesis_disposition)]))+
      `<h3>Safety findings (${c.safety_records} report entries)</h3>`+
      note('Do not conclude no harms. Skin reactions, electrical discomfort, needle incidents and treatment-intolerance withdrawals occurred. He 2026 hepatectomy reports two deaths versus none at six months, without intervention attribution. These are neither proven TEAS-caused deaths nor evidence of zero serious outcomes.')+
      c.safety.map(r=>`<details><summary>${esc(r.study)} · ${esc(r.status)}</summary><p>${esc(r.finding)}</p><p>${esc(r.window)} · ${esc(r.denominator)}</p><p>${esc(r.limitation)}</p><p class="source">${esc(r.source_pdf)} · PDF p${esc(r.pdf_pages)}</p></details>`).join('')+
      `<p><a href="current/OUTCOME_COVERAGE_REPORT.md" download>Download coverage report</a> · <a href="current/report_coverage.csv" download>All 70 reports</a> · <a href="current/recovery_evidence.csv" download>Recovery evidence</a> · <a href="current/safety_evidence.csv" download>Safety evidence</a></p>`;
  }
  function qor(){
    const q=d.qor_analysis;if(!q)return title('Quality of recovery')+note('QoR analysis not loaded.');
    const estimate=m=>`${num(m.effect)} [${num(m.ci_low)}, ${num(m.ci_high)}]`;
    return title('Quality of recovery at approximately 24 hours','Three separate TEAS comparisons · Eight reports · Positive differences favor TEAS')+
      note(esc(q.certainty_conclusion))+
      table(['Comparison','k / reported N','MD [95% CI], scale points','I²','Certainty'],q.main_models.map(m=>[esc(m.label),`${m.k} / ${m.N}`,estimate(m),`${num(m.I2,1)}%`,'Very low']))+
      note(esc(q.wu_note))+
      q.main_models.map(m=>{const g=q.grade.find(g=>g.model_id===m.model_id);return `<section><h3>${esc(m.label)}</h3><img src="current/${esc(m.model_id)}.svg" style="width:100%;height:auto" alt="Forest plot: ${esc(m.label)}"><details><summary>Inputs and all five GRADE rationales</summary>${table(['Study / exact result','n TEAS / control','Mean (SD), TEAS / control','Source'],m.inputs.map(r=>[`${esc(r.study)}<br>${esc(r.result_id)}`,`${r.n_i} / ${r.n_c}`,`${r.mean_i} (${r.sd_i}) / ${r.mean_c} (${r.sd_c})`,esc(r.source_location)]))}${['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias'].map(k=>`<p><strong>${esc(k.replaceAll('_',' '))} (−${g[k+'_downgrades']})</strong>: ${esc(g[k])}</p>`).join('')}</details></section>`;}).join('')+
      `<h3>Sensitivity analyses</h3>`+note('Eight leave-one-out analyses and one hypothetical Wu denominator-only stress test. Single-study remainders are not pooled. Diagnostics are not independently graded.')+
      table(['Diagnostic','k / N','MD [95% CI]','Limitation'],q.diagnostics.map(m=>[esc(m.label),`${m.k} / ${m.N}`,estimate(m),esc((m.note||'').replace('mg/ug', 'mg/µg'))]))+
      `<h3>Eight exact-result risk-of-bias assessments</h3>`+q.rob.map(r=>`<details><summary>${esc(r.study)} · ${esc(r.outcome)} · ${tag(r.overall)}</summary><p>${esc(r.window)} · ${esc(r.comparison)}</p>${[1,2,3,4,5].map(i=>`<p><strong>D${i}: ${esc(r['d'+i])}</strong> — ${esc(r['d'+i+'_rationale'])}</p>`).join('')}<p>${esc(r.overall_rationale)}</p><p class="source">${esc(r.source_pdf)} · ${esc(r.result_location)}</p></details>`).join('')+
      note(esc(q.remaining)) + note(esc(q.core_status)) + note('The later-window models are now shown below, ungraded.') +
      (d.qor_later_models ? 
        `<h3>Later QoR windows (POD2 / 48 h and POD3)</h3>` +
        note('Ungraded. Single-study bodies are not pooled.') +
        table(['Model', 'k / N', 'MD [95% CI]', 'Certainty'], d.qor_later_models.map(m => [
          esc(m.label) + (m.note.includes('Leave-one-out') ? '<br><small>'+esc(m.note)+'</small>' : ''),
          `${m.k} / ${m.N}`,
          `${num(m.effect)} [${num(m.ci_low)}, ${num(m.ci_high)}]`,
          tag('Not graded')
        ])) : '') +
      `<p><a href="current/QOR_ANALYSIS_REPORT.md" download>Full QoR report</a> · <a href="current/qor_rob2_signals.csv" download>176 signalling responses</a> · <a href="current/qor_source_locators.csv" download>Source locators</a> · <a href="current/qor_verification.json" download>Independent verification</a></p>`;
  }
  const views={overview,results,qor,coverage,prisma,evidence,risk,studies,methods,downloads};
  function show(id){if(!views[id])id='overview';$('content').innerHTML=(['results','risk','evidence','studies','methods','downloads'].includes(id)?qorLink():'')+views[id]();document.querySelectorAll('.nav [data-view]').forEach(b=>{b.classList.toggle('active',b.dataset.view===id);b.setAttribute('aria-selected',String(b.dataset.view===id));});if(id==='risk')riskRows();if(id==='studies')studyRows();history.replaceState(null,'','#'+id);$('content').focus({preventScroll:true});}
  document.addEventListener('click',e=>{const nav=e.target.closest('[data-view]');if(nav){show(nav.dataset.view);return;}const model=e.target.closest('[data-model]');if(model){show('results');$('model-select').value=model.dataset.model;modelDetail(model.dataset.model);return;}const fig=e.target.closest('.figure-open');if(fig){$('figure-image').src=fig.dataset.src;$('figure-image').alt=fig.dataset.caption;$('figure-caption').textContent=fig.dataset.caption;$('figure-dialog').showModal();}});
  document.addEventListener('input',e=>{if(e.target.id==='risk-search')riskRows(e.target.value);if(e.target.id==='study-search')studyRows(e.target.value);});
  document.addEventListener('change',e=>{if(e.target.id==='model-select')modelDetail(e.target.value);});
  $('close-figure').addEventListener('click',()=>$('figure-dialog').close());
  show(location.hash.slice(1)||'overview');
})();
