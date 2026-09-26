/* v38 canonical dashboard. No historical pooled or study-overall RoB inference. */
(() => {
  'use strict';
  function unitLabel(u){return u==='mg IVMME'?'mg IV MME':u==='assumed mg IVMME'?'assumed mg IV MME':u;}
  const d=window.CURRENT_REVIEW, $=id=>document.getElementById(id);
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num=(x,n=2)=>x===null||x===undefined||x===''?'—':Number(x).toFixed(n);
  const grade=new Map(d.grade.map(g=>[g.model_id,g]));
  const effect=m=>m.k?`${num(m.display_effect)} [${num(m.display_ci_low)}, ${num(m.display_ci_high)}] ${esc(unitLabel(m.unit))}`:'No eligible quantitative evidence';
  const table=(heads,rows)=>`<div class="table-scroll"><table><thead><tr>${heads.map(h=>`<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  const tag=x=>`<span class="tag ${x==='High'?'risk-high':x==='Low'?'risk-low':''}">${esc(x)}</span>`;
  const note=t=>`<p class="note">${t}</p>`;
  const qorLink=()=>d.qor_analysis?note('QoR addendum: three ~24-hour syntheses, eight additional exact-result assessments and three Very-low-certainty judgments. <button type="button" class="text-button" data-view="qor">View QoR results, RoB and GRADE</button>. The v38 core below is preserved.'):'';
  const models=role=>d.models.filter(m=>role.includes(m.role));
  const primary=models(['PRINCIPAL','SUPPORTIVE']);
  const modelTable=ms=>table(['Evidence body / role','k / N','Estimate [95% CI]','Certainty'],ms.map(m=>[`<button class="text-button model-link" data-model="${esc(m.model_id)}">${esc(m.model_id)}</button><br><small>${esc(m.role)}</small>`,`${m.k} / ${m.N}`,effect(m),tag(grade.get(m.model_id)?.certainty||'Diagnostic — not graded') ]));
  function title(h,p=''){return `<h2>${h}</h2>${p?`<p class="lede">${p}</p>`:''}`;}
  function overview(){return title('Evidence, with its limits','v38 core · 20 September 2026 · E2 sensitivity analysis · 23 September 2026 · PROSPERO CRD420261452908')+
    `<div class="summary-grid"><article><span class="eyebrow">Evidence inventory</span><strong>70 reports · 69 families</strong><p>12,103 randomized participants, operational count. This is not an analysed efficacy population. Yeh probable overlap counted once and held out of models.</p></article><article><span class="eyebrow">v38 core RoB and GRADE complete under delegation</span><strong>94 RoB assessments · 38 GRADE bodies</strong><p>All 90 current non-sensitivity component results covered. Four empty bodies not rated. New judgments are AI-conducted; prior human completion is user-reported.</p></article></div>`+
    note(`<strong>Outstanding work:</strong> ${d.outstanding.map(x => esc(x).replace(/\.$/, '')).join('; ')}. <a href=\"current/FINAL_CURRENT_STATE_REPORT.md\">Download the current-state report</a>.`)+
    qorLink()+`<h3>Primary question</h3>${modelTable(primary)}${note('No body establishes ≥10mg opioid sparing together with paired ~24h pain upper CI &lt;+1. Separate pain evidence cannot supply Szmit’s missing paired fixed-24h measurement. A one-study estimate is not a pooled meta-analysis.')}`+
    (d.e2_joint ? `<div class="panel"><h4>E2 post-hoc sensitivity analysis</h4>${
      (() => {
        const mTeas = d.e2_analysis.models.find(m=>m.body==='TEAS vs sham' && m.role==='E2 POST-HOC SENSITIVITY (main)');
        const mEa = d.e2_analysis.models.find(m=>m.body==='EA vs sham' && m.role==='E2 POST-HOC SENSITIVITY (main)');
        let txt = `TEAS vs sham (k=${mTeas.k}, N=${mTeas.N}): ${num(mTeas.effect)} mg IV MME [${num(mTeas.ci_low)}, ${num(mTeas.ci_high)}]. EA vs sham: ` + (mEa.k ? `(k=${mEa.k}) ${num(mEa.effect)} mg IV MME [${num(mEa.ci_low)}, ${num(mEa.ci_high)}].` : `k=${mEa.k}.`);
        
        const met_bodies = d.e2_joint.filter(x => x.joint_criterion === 'Met').map(x => x.body);
        if (met_bodies.length > 0) {
            txt += ` Joint criterion met in ${met_bodies.join(' and ')}`;
        } else {
            txt += ` Joint criterion met in no body`;
        }
        
        const cant_eval_bodies = d.e2_joint.filter(x => x.joint_criterion === 'Cannot be evaluated').map(x => x.body);
        if (cant_eval_bodies.length > 0) {
            txt += `; for ${cant_eval_bodies.join(' and ')} it cannot be evaluated`;
        }
        txt += `.`;
        txt += ` E2 was defined and amended after results were known. E1 stays primary. E2 is not graded.`;
        txt += ` <button type="button" class="text-button" data-view="results">See E2 section in Results</button>.`;
        txt += ` Trial-by-trial accounting: <a href="current/ADDITIONAL_FILE_12.md">Additional file 12</a>.`;
        return note(txt);
      })()
    }</div>` : '')+
    `<h3>What changed</h3><ul><li>Wu 2016 recorded as citation-search evidence; full-text dispositions reconciled.</li><li>Risk-of-bias and all 38 certainty decisions adopted; no reviewer approval queue.</li><li>Zheng’s unresolved continuous data held out of main models; original values retained in diagnostics.</li><li>Wu 2025 intraoperative dose preceded treatment and is now diagnostic only.</li><li>The 24-h QoR addendum (3 Very-low-certainty bodies).</li><li>Later-window QoR models, ungraded.</li><li>The E2 post-hoc sensitivity analysis, with E1 retained as primary. <button type="button" class="text-button" data-view="results">See E2 results</button>.</li></ul>`+
    note('The 12-reference import gap and historical outcome-focused exclusion limitation remain disclosed.');}
  // Plot extent: study CIs, stored pooled CI/PI, the null and (where recorded) the -10 mg threshold, padded 5%.
  const Z95=1.95996398454;
  const plotVals=(m,rows)=>[0,...rows.flatMap(r=>[+r.yi-Z95*Math.sqrt(+r.vi),+r.yi+Z95*Math.sqrt(+r.vi)]),...(m.k?[m.ci_low,m.ci_high]:[]),...(m.pi_low!==null&&m.pi_low!==undefined?[m.pi_low,m.pi_high]:[]),...(m.reaches10mg!==null&&m.reaches10mg!==undefined?[-10]:[])];
  const padRange=vals=>{const lo=Math.min(...vals),hi=Math.max(...vals),pad=(hi-lo||1)*.05;return [lo-pad,hi+pad];};
  function axisTicks(lo,hi,rr){
    const fmt=v=>String(+v.toFixed(6));
    if(rr){const sets=[[.01,.02,.05,.1,.2,.5,.75,1,1.5,2,4,5,10,20,50,100],[.001,.002,.005,.01,.02,.05,.1,.2,.5,1,2,5,10,20,50,100,200,500,1000],[.001,.01,.1,1,10,100,1000]];
      return sets.map(s=>s.filter(t=>Math.log(t)>=lo&&Math.log(t)<=hi)).find(s=>s.length<=7).map(t=>({v:Math.log(t),label:fmt(t)}));}
    const raw=(hi-lo)/5,p=10**Math.floor(Math.log10(raw)),step=[1,2,2.5,5,10].map(s=>s*p).find(s=>raw<=s),ticks=[];
    for(let v=Math.ceil(lo/step)*step;v<=hi;v+=step)ticks.push({v,label:fmt(v)});return ticks;
  }
  // Drawn only from canonical outputs and inputs: pooled estimate/CI/PI are never recomputed here.
  // rows defaults to the model's core inputs; range lets several plots share one axis.
  function forest(m,rows=d.inputs.filter(r=>r.model_id===m.model_id),range){
    if(!rows.length)return '';
    const rr=m.measure==='RR',show=v=>num(rr?Math.exp(v):v),z=Z95,tau2=+m.tau2||0,pooled=m.k>1;
    const w=rows.map(r=>1/(+r.vi+tau2)),wsum=w.reduce((a,b)=>a+b,0);
    const pts=rows.map((r,i)=>({name:r.study,mark:r.mark,y:+r.yi,lo:+r.yi-z*Math.sqrt(+r.vi),hi:+r.yi+z*Math.sqrt(+r.vi),w:w[i]/wsum}));
    const hasPI=m.pi_low!==null&&m.pi_low!==undefined,thr=m.reaches10mg!==null&&m.reaches10mg!==undefined?-10:null;
    const [lo,hi]=range||padRange(plotVals(m,rows));
    const X0=290,X1=640,x=v=>X0+(v-lo)/(hi-lo)*(X1-X0),ticks=axisTicks(lo,hi,rr);
    const RH=30,top=46,poolY=top+pts.length*RH+(pooled?8:0),piY=poolY+RH,axisY=(pooled?(hasPI?piY:poolY):top+(pts.length-1)*RH)+28,ht=axisY+(m.construct.startsWith('pre_')?46:66);
    const T=(tx,ty,s,o='')=>`<text x="${tx}" y="${ty}" fill="#dbeafe" font-size="13" ${o}>${s}</text>`;
    const comp={sham:'sham',usual_care:'usual care',active_electrical:'active electrical control'}[m.comparator]||esc(m.comparator);
    const summary=pooled?`pooled ${show(m.effect)} [${show(m.ci_low)}, ${show(m.ci_high)}]`:`single study ${show(m.effect)} [${show(m.ci_low)}, ${show(m.ci_high)}], not pooled`;
    return `<div class="forest-wrap"><svg viewBox="0 0 960 ${ht}" role="img" aria-label="Forest plot for ${esc(m.model_id)}: ${esc(summary)} ${esc(unitLabel(m.unit))}">`+
      T(8,20,'Study','fill-opacity=".75"')+T(660,20,rr?'Risk ratio [95% CI]':'Estimate [95% CI]','fill-opacity=".75"')+(pooled?T(952,20,'Weight','fill-opacity=".75" text-anchor="end"'):'')+
      `<line x1="${x(0)}" x2="${x(0)}" y1="30" y2="${axisY}" class="fp-null" stroke="#94a3b8" stroke-dasharray="4 4"/>`+
      (thr===null?'':`<line x1="${x(thr)}" x2="${x(thr)}" y1="30" y2="${axisY}" class="fp-tl" stroke="#fbbf24" stroke-dasharray="1 4" stroke-width="2"/><text class="fp-tt" x="${x(thr)}" y="${axisY+54}" fill="#fbbf24" font-size="11" text-anchor="middle">−10 mg registered threshold</text>`)+
      pts.map((p,i)=>{const y=top+i*RH,sz=pooled?5+11*Math.sqrt(p.w):9;return T(8,y+4,esc(p.name)+(p.mark?` <tspan class="fp-mut" fill="#94a3b8">${esc(p.mark)}</tspan>`:''))+`<line x1="${x(p.lo)}" x2="${x(p.hi)}" y1="${y}" y2="${y}" class="fp-s" stroke="#93c5fd" stroke-width="1.6"/><rect class="fp-f" x="${x(p.y)-sz/2}" y="${y-sz/2}" width="${sz}" height="${sz}" fill="#93c5fd"/>`+T(660,y+4,`${show(p.y)} [${show(p.lo)}, ${show(p.hi)}]`)+(pooled?T(952,y+4,`${(100*p.w).toFixed(1)}%`,'text-anchor="end"'):'');}).join('')+
      (pooled?`<line x1="8" x2="952" y1="${poolY-RH/2-4}" y2="${poolY-RH/2-4}" class="fp-sep" stroke="#2a3a52"/>`+T(8,poolY+4,'Pooled · REML, safeguarded HK','font-weight="600"')+
        `<polygon points="${x(m.ci_low)},${poolY} ${x(m.effect)},${poolY-8} ${x(m.ci_high)},${poolY} ${x(m.effect)},${poolY+8}" class="fp-pf" fill="#5eead4"/>`+T(660,poolY+4,`${show(m.effect)} [${show(m.ci_low)}, ${show(m.ci_high)}]`,'class="fp-pf" font-weight="600" fill="#5eead4"')+T(952,poolY+4,'100%','text-anchor="end"')+
        (hasPI?T(8,piY+4,'95% prediction interval','fill-opacity=".75"')+`<line x1="${x(m.pi_low)}" x2="${x(m.pi_high)}" y1="${piY}" y2="${piY}" class="fp-ps" stroke="#5eead4" stroke-width="2"/><line x1="${x(m.pi_low)}" x2="${x(m.pi_low)}" y1="${piY-5}" y2="${piY+5}" class="fp-ps" stroke="#5eead4" stroke-width="2"/><line x1="${x(m.pi_high)}" x2="${x(m.pi_high)}" y1="${piY-5}" y2="${piY+5}" class="fp-ps" stroke="#5eead4" stroke-width="2"/>`+T(660,piY+4,`${show(m.pi_low)} to ${show(m.pi_high)}`,'fill-opacity=".75"'):'')
      :T(660,top+pts.length*RH-6,'Single study · not pooled','class="fp-mut" font-size="12" fill="#94a3b8"'))+
      `<line x1="${X0}" x2="${X1}" y1="${axisY}" y2="${axisY}" class="fp-axis" stroke="#94a3b8"/>`+
      ticks.map(t=>`<line x1="${x(t.v)}" x2="${x(t.v)}" y1="${axisY}" y2="${axisY+5}" class="fp-axis" stroke="#94a3b8"/><text class="fp-mut" x="${x(t.v)}" y="${axisY+18}" fill="#94a3b8" font-size="11" text-anchor="middle">${t.label}</text>`).join('')+
      (m.construct.startsWith('pre_')?'':`<text x="${x(0)-8}" y="${axisY+36}" fill="#cbd5e1" font-size="12" text-anchor="end">← Favours ${esc(m.modality)}</text><text x="${x(0)+8}" y="${axisY+36}" fill="#cbd5e1" font-size="12">Favours ${comp} →</text>`)+
      T(660,axisY+18,`${rr?'Risk ratio, log scale; null = 1':'Difference; null = 0'} · ${esc(unitLabel(m.unit))}`,'class="fp-mut" font-size="12" fill="#94a3b8"')+
      `</svg></div>`;
  }
  function modelDetail(mid){
    const m=d.models.find(m=>m.model_id===mid);if(!m)return;
    const s=d.specifications.find(s=>s.model_id===mid),g=grade.get(mid),ins=d.inputs.filter(r=>r.model_id===mid);
    const panel=$('model-panel');panel.innerHTML=title(esc(mid),`${esc(m.role)} · ${esc(m.status)} · k=${m.k}, N=${m.N}`)+`<p class="estimate">${effect(m)}</p>`+
    `<details style="background:var(--bg); margin-bottom:16px"><summary>How to read this plot</summary><p style="font-size:0.9em">Squares are study estimates, sized by random-effects weight; their lines are normal-approximation 95% confidence intervals. The diamond is the canonical pooled estimate with its safeguarded Hartung–Knapp 95% confidence interval, which can be much wider than the study intervals when few studies are pooled. A single study is shown once and is not pooled. The bar under the diamond, where present, is the 95% prediction interval. The dashed line marks no effect (0, or 1 for risk ratios on a log scale); the dotted amber line marks the registered −10 mg IV MME threshold. Direction labels are printed under each axis.</p></details>`+
    forest(m)+note(esc((s.note||'Separate modality/comparator body. Compatible active arms combined; control counted once.').replace('mg/ug', 'mg/µg')))+
    (m.k>1?`<p>I² ${num(m.I2,1)}% <span title="I² represents the percentage of variation across studies that is due to heterogeneity rather than chance." style="cursor:help; border-bottom:1px dotted var(--accent); color:var(--accent)">?</span> · τ² ${num(m.tau2,3)} · safeguarded Hartung–Knapp interval.</p>`:'')+
    (m.pi_low!==null&&m.pi_low!==undefined?`<p>Prediction interval: ${num(m.measure==='RR'?Math.exp(m.pi_low):m.pi_low)} to ${num(m.measure==='RR'?Math.exp(m.pi_high):m.pi_high)} ${esc(unitLabel(m.unit))}. Interpret cautiously.</p>`:'')+
    table(['Contributor / exact result IDs','n intervention / control','Source location'],ins.map(r=>[`<button type="button" class="text-button result-open" data-result="${esc(r.result_id)}" data-result-model="${esc(r.model_id)}">${esc(r.study)}<br><small>${esc(r.result_id)}</small></button>`,`${num(r.n_i,0)} / ${num(r.n_c,0)}`,esc(r.source_location)]))+
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

    const e2PainConstant = 'As stated in E2_RESULTS.md, digitising Lin 2002 Fig. 1 has not been done and would be a further post-hoc decision.';
    const jointRows = (d.e2_joint || []).map(j => [j.body, j.opioid_limb, j.pain_limb, j.joint_criterion]);

    return `<h3 id="e2-section" tabindex="-1">E2 post-hoc sensitivity analysis</h3>` +
      note('E1 stays primary. Trial-by-trial accounting: <a href="current/ADDITIONAL_FILE_12.md">Additional file 12</a>. E2 is post-hoc, defined and amended (E2.1) after data were seen, and the decision to keep E1 primary was made after the E2 results were known.') +
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
  function studies(){return `<div id="rich-explorer-container"></div>`;}
  function studyRows(q=''){}
  function methods(){
    const e2_html = d.e2_methods_html ? `<h3>Post-hoc E2 sensitivity analysis</h3>` + Object.entries(d.e2_methods_html).map(([h, html]) => {
      return `<details><summary>${esc(h)}</summary>${html}</details>`;
    }).join('') + `<p><a href="current/AMENDED_PRIMARY_ESTIMAND_E2.md" download>Full E2 definition</a> · <a href="current/E2_RESULTS.md" download>E2 results</a></p>` : '';
    return title('Methods and adopted decisions','Posthoc adjudication with results known. No reviewer approval is awaited for these decisions.')+d.policies.map(p=>`<details><summary>${esc(p.topic)} · ${esc(p.status)}</summary><p>${esc(p.decision)}</p></details>`).join('')+e2_html+`<h3>Search strategies</h3>${(window.SEARCH_STRATEGIES||[]).map(s=>`<details><summary>${esc(s.name)} · ${esc(s.date)} · ${s.hits} records</summary><p>${esc(s.platform)} · ${esc(s.status)}</p><pre>${esc(s.strategy_text)}</pre><p class="source">${esc(s.source)}</p></details>`).join('')}`+note('Current R/metafor and independent Python validation results are in Downloads. Reproduction establishes computational consistency, not source truth or exhaustive selection.');
  }
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
    const renderRob=robList=>robList.map(r=>`<details><summary>${esc(r.study)} · ${esc(r.outcome)} · ${tag(r.overall)}</summary><p>${esc(r.window)} · ${esc(r.comparison)}</p>${[1,2,3,4,5].map(i=>`<p><strong>D${i}: ${esc(r['d'+i])}</strong> — ${esc(r['d'+i+'_rationale'])}</p>`).join('')}<p>${esc(r.overall_rationale)}</p><p class="source">${esc(r.source_pdf)} · ${esc(r.result_location)}</p></details>`).join('');
    return title('Quality of recovery at approximately 24 hours','Three separate TEAS comparisons · Eight reports · Positive differences favor TEAS')+
      note(esc(q.certainty_conclusion))+
      table(['Comparison','k / reported N','MD [95% CI], scale points','I²','Certainty'],q.main_models.map(m=>[esc(m.label),`${m.k} / ${m.N}`,estimate(m),`${num(m.I2,1)}%`,'Very low']))+
      note(esc(q.wu_note))+
      q.main_models.map(m=>{const g=q.grade.find(g=>g.model_id===m.model_id);return `<section id="qor-${esc(m.model_id)}" tabindex="-1"><h3>${esc(m.label)}</h3><img src="current/${esc(m.model_id)}.svg" style="width:100%;height:auto" alt="Forest plot: ${esc(m.label)}"><details><summary>Inputs and all five GRADE rationales</summary>${table(['Study / exact result','n TEAS / control','Mean (SD), TEAS / control','Source'],m.inputs.map(r=>[`${esc(r.study)}<br>${esc(r.result_id)}`,`${r.n_i} / ${r.n_c}`,`${r.mean_i} (${r.sd_i}) / ${r.mean_c} (${r.sd_c})`,esc(r.source_location)]))}${['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias'].map(k=>`<p><strong>${esc(k.replaceAll('_',' '))} (−${g[k+'_downgrades']})</strong>: ${esc(g[k])}</p>`).join('')}</details></section>`;}).join('')+
      `<h3 id="qor-diagnostics" tabindex="-1">Sensitivity analyses</h3>`+note('Eight leave-one-out analyses and one hypothetical Wu denominator-only stress test. Single-study remainders are not pooled. Diagnostics are not independently graded.')+
      table(['Diagnostic','k / N','MD [95% CI]','Limitation'],q.diagnostics.map(m=>[esc(m.label),`${m.k} / ${m.N}`,estimate(m),esc((m.note||'').replace('mg/ug', 'mg/µg'))]))+
      `<h3>Eight exact-result risk-of-bias assessments</h3>`+renderRob(q.rob)+
      note(esc(q.remaining)) + note(esc(q.core_status)) + note('The later-window models are now shown below, ungraded.') +
      (d.qor_later_models ? 
        `<h3>Later QoR windows (POD2 / 48 h and POD3)</h3>` +
        note('Ungraded. Single-study bodies are not pooled.') +
        table(['Model', 'k / N', 'MD [95% CI]', 'RoB', 'Certainty'], d.qor_later_models.map(m => [
          esc(m.label) + (m.note.includes('Leave-one-out') ? '<br><small>'+esc(m.note)+'</small>' : ''),
          `${m.k} / ${m.N}`,
          `${num(m.effect)} [${num(m.ci_low)}, ${num(m.ci_high)}]`,
          m.result_ids.map(rid => { const rr = d.qor_later_rob.find(r => r.result_id === rid); return rr ? esc(rr.study) + ': ' + tag(rr.overall) : ''; }).join('<br>'),
          tag('Not graded')
        ])) +
        d.qor_later_models.map(m => `<details id="qor-${esc(m.model_id)}" tabindex="-1"><summary>${esc(m.label)}</summary><img src="current/forest_${esc(m.model_id)}.svg" alt="${esc(m.label)}" style="width:100%;height:auto"><p>Forest plot produced with ${esc(d.qor_later_metafor_manifest.R_version)} / metafor ${esc(d.qor_later_metafor_manifest.metafor_version)} (same specification as the canonical cross-check); script: forest_qor_later.R</p></details>`).join('') +
        `<h3>Five exact-result risk-of-bias assessments (later windows)</h3>` + renderRob(d.qor_later_rob) : '') +
      `<p><a href="current/QOR_ANALYSIS_REPORT.md" download>Full QoR report</a> · <a href="current/qor_rob2_signals.csv" download>176 signalling responses</a> · <a href="current/qor_source_locators.csv" download>Source locators</a> · <a href="current/qor_verification.json" download>Independent verification</a></p>`;
  }
  // E1 vs E2 workspace: canonical E1 and post-hoc E2 bodies side by side, from stored outputs and decision files only.
  const E2_BODIES=[['TEAS vs sham','opioid24_TEAS_sham','E2_opioid24_TEAS_sham'],['TEAS vs usual care','opioid24_TEAS_usual','E2_opioid24_TEAS_usual'],['EA vs sham','opioid24_EA_sham','E2_opioid24_EA_sham'],['EA vs usual care','opioid24_EA_usual','E2_opioid24_EA_usual']];
  const resultIds=s=>s.startsWith('Tier B1')?[]:s.split(' / ').map(x=>x.split(' (')[0].trim());
  const bodyOf=r=>`${r.modality} vs ${/^sham/i.test(r.comparator)?'sham':/usual/i.test(r.comparator)?'usual care':r.comparator}`;
  // Same join as the CI contract: result ID, or report name for the E2.1 Tier B1 admissions.
  const accountingRows=(body,e1id,e2id)=>{
    const acc=d.e2_accounting,modality=body.split(' vs ')[0];
    const rows=[...acc.tierA.filter(r=>r.body===body),...acc.tierA_addendum.filter(r=>r.body.startsWith(modality+' vs unresolved'))].map(r=>({...r,tier:r.addendum_note?'A (addendum)':'A'}));
    const named=new Set(rows.map(r=>r.report));
    for(const [tier,list] of [['B1',acc.tierB1],['B2',acc.tierB2]])for(const r of list){
      if(bodyOf(r)!==body)continue;
      const a=rows.find(x=>x.report===r.report);
      if(a){a.detail=r;continue;}
      if(!named.has(r.report))rows.push({report:r.report,E1_disposition:r.E1_disposition||'—',E2_disposition:r.E2_disposition,E2_basis:r.E2_rule_failed,flags:r.flag||r.notes||'',mandatory_sensitivity:'',tier,detail:r});
    }
    const hit=(list,mid,r)=>list.find(x=>x.model_id===mid&&(resultIds(r.result_ids||'').includes(x.result_id)||((r.result_ids||'').startsWith('Tier B1')&&x.study===r.report)));
    return rows.map(r=>({...r,e1:hit(d.inputs,e1id,r),e2:hit(d.e2_inputs,e2id,r)}));
  };
  // Model ladder: stored estimate and CI per model on one axis (no recomputation).
  function ladder(items,range){
    const [lo,hi]=range,X0=400,X1=700,x=v=>X0+(v-lo)/(hi-lo)*(X1-X0),RH=26,top=36,axisY=top+items.length*RH,ticks=axisTicks(lo,hi,false);
    const T=(tx,ty,s,o='')=>`<text x="${tx}" y="${ty}" fill="#dbeafe" font-size="12" ${o}>${s}</text>`;
    return `<div class="forest-wrap"><svg viewBox="0 0 960 ${axisY+34}" role="img" aria-label="Sensitivity ladder: ${items.length} stored model estimates on a shared axis">`+
      T(8,18,'Model','fill-opacity=".75"')+T(716,18,'MD [95% CI] · k','fill-opacity=".75"')+
      `<line x1="${x(0)}" x2="${x(0)}" y1="24" y2="${axisY}" class="fp-null" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="${x(-10)}" x2="${x(-10)}" y1="24" y2="${axisY}" class="fp-tl" stroke="#fbbf24" stroke-dasharray="1 4" stroke-width="2"/>`+
      items.map((it,i)=>{const y=top+i*RH,cls=it.e2?'fp-ps':'fp-s',fcls=it.e2?'fp-pf':'fp-f',col=it.e2?'#5eead4':'#93c5fd';
        return T(8,y+4,esc(it.label),it.main?'font-weight="600"':'class="fp-mut" fill="#94a3b8"')+`<line x1="${x(it.lo)}" x2="${x(it.hi)}" y1="${y}" y2="${y}" class="${cls}" stroke="${col}" stroke-width="${it.main?2.5:1.5}"/>`+
          (it.main?`<polygon points="${x(it.lo)},${y} ${x(it.effect)},${y-6} ${x(it.hi)},${y} ${x(it.effect)},${y+6}" class="${fcls}" fill="${col}"/>`:`<circle cx="${x(it.effect)}" cy="${y}" r="4" class="${fcls}" fill="${col}"/>`)+
          T(716,y+4,`${num(it.effect)} [${num(it.lo)}, ${num(it.hi)}] · ${it.k}`,it.main?'font-weight="600"':'');}).join('')+
      `<line x1="${X0}" x2="${X1}" y1="${axisY}" y2="${axisY}" class="fp-axis" stroke="#94a3b8"/>`+ticks.map(t=>`<line x1="${x(t.v)}" x2="${x(t.v)}" y1="${axisY}" y2="${axisY+5}" class="fp-axis" stroke="#94a3b8"/><text class="fp-mut" x="${x(t.v)}" y="${axisY+18}" fill="#94a3b8" font-size="11" text-anchor="middle">${t.label}</text>`).join('')+
      T(716,axisY+18,'mg IV MME · dotted line −10 mg','class="fp-mut" font-size="11" fill="#94a3b8"')+`</svg></div>`;
  }
  function e1e2(){
    if(!d.e2_accounting||!d.e2_inputs)return title('E1 vs E2')+note('E2 inputs or accounting not loaded.');
    const want=parseHash().params.get('body'),[body,e1id,e2id]=E2_BODIES.find(b=>b[0]===want)||E2_BODIES[0];
    const m1=d.models.find(m=>m.model_id===e1id),m2=d.e2_analysis.models.find(m=>m.model_id===e2id),g=grade.get(e1id),j=(d.e2_joint||[]).find(x=>x.body===body);
    const [modality,cmp]=body.split(' vs ');
    const m2plot={...m2,measure:'MD',unit:m1.unit,construct:m1.construct,modality,comparator:m1.comparator};
    const rows1=d.inputs.filter(r=>r.model_id===e1id),e1ids=new Set(rows1.map(r=>r.study));
    const rows2=d.e2_inputs.filter(r=>r.model_id===e2id).map(r=>({...r,mark:e1ids.has(r.study)?'':'E2 only'}));
    const range=padRange([...plotVals(m1,rows1),...plotVals(m2plot,rows2)]);
    const est=m=>m.k?`${num(m.effect)} [${num(m.ci_low)}, ${num(m.ci_high)}]`:'No eligible evidence';
    const cmpRows=[['Role','Registered primary','Post-hoc sensitivity (defined and amended after data were seen)'],['k / N',`${m1.k} / ${m1.N}`,`${m2.k} / ${m2.N}`],['MD, mg IV MME [95% CI]',est(m1),est(m2)],
      ['I² · τ²',m1.k>1?`${num(m1.I2,1)}% · ${num(m1.tau2,3)}`:'—',m2.k>1?`${num(m2.I2,1)}% · ${num(m2.tau2,3)}`:'—'],
      ['Prediction interval',m1.pi_low!=null?`${num(m1.pi_low)} to ${num(m1.pi_high)}`:'—',m2.pi_low!=null?`${num(m2.pi_low)} to ${num(m2.pi_high)}`:'—'],
      ['Point estimate ≤ −10 mg',m1.k?(m1.reaches10mg?'Yes':'No'):'—',m2.reaches10mg?'Yes':'No'],['Certainty',tag(g?.certainty||'—'),tag('Not graded')]];
    const sens=[...(m1.k?[{label:'E1 · registered primary',effect:m1.effect,lo:m1.ci_low,hi:m1.ci_high,k:m1.k,main:true}]:[]),
      ...d.models.filter(m=>m.model_id.startsWith(e1id+'_')&&m.role==='SENSITIVITY'&&/mg IVMME$/.test(m.unit)&&m.k).map(m=>({label:'E1 sens · '+m.model_id.slice(e1id.length+1).replaceAll('_',' ')+(m.unit.startsWith('assumed')?' (assumed MME)':''),effect:m.effect,lo:m.ci_low,hi:m.ci_high,k:m.k})),
      {label:'E2 · post-hoc main',effect:m2.effect,lo:m2.ci_low,hi:m2.ci_high,k:m2.k,main:true,e2:true},
      ...d.e2_analysis.models.filter(m=>m.body===body&&m.model_id!==e2id).map(m=>({label:'E2 '+(m.role==='LEAVE-ONE-OUT'?'LOO':'sens')+' · '+((d.e2_labels||{})[m.model_id]||m.note||m.model_id).replace(/<[^>]+>/g,''),effect:m.effect,lo:m.ci_low,hi:m.ci_high,k:m.k,e2:true}))];
    const lrange=padRange([0,-10,...sens.flatMap(s=>[s.lo,s.hi])]);
    const acc=accountingRows(body,e1id,e2id).sort((a,b)=>(!!b.e2-!!a.e2)||(!!b.e1-!!a.e1)||a.report.localeCompare(b.report));
    const trial=r=>r?`<span style="white-space:nowrap">${num(+r.yi)} [${num(+r.yi-Z95*Math.sqrt(+r.vi))}, ${num(+r.yi+Z95*Math.sqrt(+r.vi))}]</span>${r.factor&&+r.factor!==1?`<br><small>factor ${esc(r.factor)}</small>`:''}`:'—';
    return title('E1 vs E2','Why the estimate changes between the registered primary (E1) and the post-hoc E2 synthesis: membership, trial-level estimates and sensitivity, from stored outputs only.')+
      note('<strong>E2 is post-hoc.</strong> It was defined, and amended (E2.1), after the data were seen; the decision to keep E1 as primary was made after E2 results were known. E1 remains the registered primary analysis. E2 is not graded and must not be reported as primary efficacy evidence.')+
      `<div class="body-picker" role="group" aria-label="Comparison">${E2_BODIES.map(([b])=>`<button type="button" class="e1e2-body${b===body?' active':''}" data-body="${esc(b)}" aria-pressed="${b===body}">${esc(b)}</button>`).join('')}</div>`+
      `<h3>${esc(body)}: summary</h3>`+table(['',`E1 · <button class="text-button model-link" data-model="${esc(e1id)}">${esc(e1id)}</button>`,`E2 · <button class="text-button model-link" data-model="${esc(e2id)}">${esc(e2id)}</button>`],cmpRows)+
      (j?note(`Registered joint criterion (≥10 mg sparing with paired ~24 h pain upper CI &lt; +1): opioid limb <strong>${esc(j.opioid_limb)}</strong>; pain limb <strong>${esc(j.pain_limb)}</strong>; joint <strong>${esc(j.joint_criterion)}</strong>.`):'')+
      `<h3>Forest plots on a shared axis</h3><h4>E1 · registered primary · ${esc(e1id)}</h4>`+(m1.k?forest(m1,rows1,range):note('No eligible quantitative E1 evidence for this comparison.'))+`<h4>E2 · post-hoc, not graded · ${esc(e2id)}</h4>`+forest(m2plot,rows2,range)+
      note('Both plots use the same horizontal scale. “E2 only” marks trials admitted by E2 that are not in the E1 body. E2 study rows show arm values after the stated conversion factor and arm combination.')+
      `<h3>Trial-by-trial accounting (${acc.length} candidate reports)</h3>`+
      table(['Report','E1','E2','Rule / basis','In E1 model','In E2 model: MD [95% CI]','Flags · required sensitivity'],acc.map(r=>[
        `${esc(r.report)}<br><small>Tier ${esc(r.tier)}${r.result_ids&&!r.result_ids.startsWith('Tier')?' · '+esc(r.result_ids):''}</small>`,esc(r.E1_disposition),`<strong>${esc(r.E2_disposition)}</strong>`,
        esc(r.E2_basis)+(r.detail?.source_locator?`<br><small>${esc(r.detail.source_locator)}${r.detail.resolvable_by?' · resolvable by: '+esc(r.detail.resolvable_by):''}</small>`:''),
        r.e1?'✓':'—',trial(r.e2),[r.flags,r.mandatory_sensitivity].filter(Boolean).map(esc).join('<br>')||'—']))+
      note('Dispositions are the committed E2 decision files (Tier A reclassification and addendum; Tier B1 extraction; Tier B2 re-check), unchanged. Reports held for unresolved source or comparator questions stay out of both analyses.')+
      `<h3>Sensitivity ladder</h3>`+ladder(sens,lrange)+
      note('Stored estimates only; nothing is re-fitted in the browser. E1 sensitivities with assumed MME conversions are labelled. A different estimate under a sensitivity is not evidence of effect modification.')+
      `<p><a href="current/ADDITIONAL_FILE_12.md" download>Additional file 12 (trial-by-trial accounting)</a> · <a href="current/AMENDED_PRIMARY_ESTIMAND_E2.md" download>E2 estimand and amendment</a> · <a href="current/e2_model_outputs.csv" download>E2 estimates</a></p>`;
  }
  const views={overview,results,e1e2,qor,coverage,prisma,evidence,risk,studies,methods,downloads};
  function render(id){if(!views[id])id='overview';$('content').innerHTML=(['results','risk','evidence','studies','methods','downloads'].includes(id)?qorLink():'')+views[id]();document.querySelectorAll('.nav [data-view]').forEach(b=>{b.classList.toggle('active',b.dataset.view===id);b.setAttribute('aria-selected',String(b.dataset.view===id));});if(id==='risk')riskRows();if(id==='studies'){if(window.renderRichExplorer){window.renderRichExplorer('rich-explorer-container');}else{studyRows();}}$('content').focus({preventScroll:true});return id;}
  // URL state: #view, #results?model=…&result=…, #qor?model=…; the Study Explorer adds its own filter/study keys.
  const parseHash=()=>{const [view,q='']=location.hash.slice(1).split('?');return {view,params:new URLSearchParams(q)};};
  const hashFor=(view,params={})=>{const q=new URLSearchParams(Object.entries(params).filter(([,v])=>v)).toString();return '#'+view+(q?'?'+q:'');};
  let routed=null;
  function setHash(h){history.replaceState(null,'',h);routed=location.hash;}
  function route(force){
    if(!force&&location.hash===routed)return;routed=location.hash;
    document.querySelectorAll('dialog[open]').forEach(x=>x.close());
    const {view,params}=parseHash(),id=render(view),mid=params.get('model');
    const focus=el=>{if(!el)return;if(el.tagName==='DETAILS')el.open=true;el.scrollIntoView({block:'start'});el.focus({preventScroll:true});};
    if(id==='results'&&mid){
      if(d.models.some(m=>m.model_id===mid)){$('model-select').value=mid;modelDetail(mid);if(params.get('result'))openResultDrawer(params.get('result'),mid);}
      else if((d.e2_analysis?.models||[]).some(m=>m.model_id===mid))focus($('e2-section'));
    }
    if(id==='qor'&&mid)focus($('qor-'+mid)||((d.qor_analysis?.diagnostics||[]).some(m=>m.model_id===mid)?$('qor-diagnostics'):null));
  }
  function show(id,params){const h=hashFor(id,params);if(location.hash!==h)history.pushState(null,'',h);route(true);}
  // Route any model ID (core, QoR 24 h, QoR diagnostic, QoR later window, E2) to where it is displayed.
  function openModel(mid){const qor=[...(d.qor_analysis?.main_models||[]),...(d.qor_analysis?.diagnostics||[]),...(d.qor_later_models||[])].some(m=>m.model_id===mid);show(qor?'qor':'results',{model:mid});}
  // Result/source inspector for one model input row. A result can feed several models with different
  // conversion factors, so the row is looked up by result ID and model ID together.
  // Closing the inspector drops ?result= (called directly too: some browsers defer the close event for hidden pages).
  function clearResultKey(){const {view,params}=parseHash();if($('result-drawer').open||view!=='results'||!params.get('result'))return;params.delete('result');setHash(hashFor('results',Object.fromEntries(params)));}
  function openResultDrawer(rid,mid){
    const r=d.inputs.find(x=>x.result_id===rid&&x.model_id===mid)||d.inputs.find(x=>x.result_id===rid);if(!r)return;
    const parts=rid.split('+'),rr=r.measure==='RR',val=v=>num(rr?Math.exp(v):v),z=1.95996398454;
    const panel=(h,body)=>`<div class="panel" style="margin:0 0 16px"><h3 style="margin-top:0">${h}</h3>${body}</div>`;
    const arms=r.data_type==='Mean/SD'
      ?table(['Arm','n','Mean','SD'],[[esc(r.intervention||'Intervention'),num(r.n_i,0),esc(r.mean_i),esc(r.sd_i)],[esc(r.comparator||'Comparator'),num(r.n_c,0),esc(r.mean_c),esc(r.sd_c)]])
      :table(['Arm','Events','n'],[[esc(r.intervention||'Intervention'),esc(r.events_i),num(r.n_i,0)],[esc(r.comparator||'Comparator'),esc(r.events_c),num(r.n_c,0)]]);
    const uses=d.inputs.filter(x=>x.result_id===rid);
    const rob=parts.map(p=>{const a=d.rob.find(x=>x.result_id===p);return a?`<details><summary>${esc(p)} · ${esc(a.outcome)} · ${tag(a.overall)}</summary>${[1,2,3,4,5].map(i=>`<p><strong>D${i}: ${esc(a['d'+i])}</strong> — ${esc(a['d'+i+'_rationale'])}</p>`).join('')}<p>${esc(a.overall_rationale)}</p></details>`:`<p>${esc(p)}: no v38 result-specific assessment recorded.</p>`;}).join('');
    const html=`<h2 style="margin-top:0">${esc(r.study)} · ${esc(rid)}</h2><p class="lede">${esc(r.outcome)} · ${esc(r.window)} · ${esc(r.population)}</p>`+
      (parts.length>1?note(`Combined-arm input: component results ${parts.map(esc).join(' + ')} were combined into one intervention arm before analysis; the control arm is counted once.`):'')+
      panel('Source',`<p><strong>${esc(r.source_location)}</strong></p>${r.source_quote?`<blockquote style="border-left:4px solid #64748b;padding-left:16px;margin-left:0">${esc(r.source_quote)}</blockquote>`:''}<p class="source">${esc(r.source_pdf)}<br>SHA-256: ${esc(r.source_sha256)}</p>${r.source_qc&&r.source_qc!=='NOT REPORTED'?`<p><strong>Extraction note:</strong> ${esc(r.source_qc)}</p>`:''}`)+
      panel(`Extracted data in ${esc(r.model_id)}`,arms+`<p>Reported unit: ${esc(r.unit)} · conversion factor ${esc(r.factor)} · analysed as ${esc(unitLabel(r.analysis_unit||r.measure))}${r.continuity_correction&&r.continuity_correction!=='0'?` · continuity correction ${esc(r.continuity_correction)}`:''}</p><p>Study estimate: <strong>${val(+r.yi)} [${val(+r.yi-z*Math.sqrt(+r.vi))}, ${val(+r.yi+z*Math.sqrt(+r.vi))}]</strong> <small>(yi ${num(r.yi,4)}, vi ${num(r.vi,4)}${rr?'; log scale':''})</small></p>${r.decision?`<p><strong>Decision:</strong> ${esc(r.decision)}${r.rationale?` — ${esc(r.rationale)}`:''}</p>`:''}`)+
      panel(`Used in ${uses.length} model${uses.length===1?'':'s'}`,`<ul>${uses.map(x=>`<li><button type="button" class="text-button" data-model="${esc(x.model_id)}">${esc(x.model_id)}</button> <small>${esc(x.role)} · factor ${esc(x.factor)}</small></li>`).join('')}</ul>`)+
      panel('Risk of bias (v38, result-specific)',rob);
    if(!$('result-drawer')){document.body.insertAdjacentHTML('beforeend',`<dialog id="result-drawer" aria-labelledby="result-drawer-title" style="width:820px;max-width:92vw;max-height:90vh;overflow-y:auto;background:var(--card)"><button type="button" id="close-result-drawer" aria-label="Close result inspector">Close</button><div id="result-drawer-content"></div></dialog>`);
      $('result-drawer').addEventListener('close',clearResultKey);}
    $('result-drawer-content').innerHTML=html;$('result-drawer-content').querySelector('h2').id='result-drawer-title';$('result-drawer').showModal();
    if(parseHash().view==='results')setHash(hashFor('results',{model:r.model_id,result:rid}));
  }
  document.addEventListener('click',e=>{const nav=e.target.closest('[data-view]');if(nav){document.querySelectorAll('dialog[open]').forEach(x=>x.close());show(nav.dataset.view);return;}const model=e.target.closest('[data-model]');if(model){openModel(model.dataset.model);return;}const fig=e.target.closest('.figure-open');if(fig){$('figure-image').src=fig.dataset.src;$('figure-image').alt=fig.dataset.caption;$('figure-caption').textContent=fig.dataset.caption;$('figure-dialog').showModal();return;}const bodyBtn=e.target.closest('.e1e2-body');if(bodyBtn){show('e1e2',{body:bodyBtn.dataset.body});return;}const res=e.target.closest('.result-open');if(res){openResultDrawer(res.dataset.result,res.dataset.resultModel);return;}if(e.target.id==='close-result-drawer'){$('result-drawer').close();clearResultKey();}});
  document.addEventListener('input',e=>{if(e.target.id==='risk-search')riskRows(e.target.value);if(e.target.id==='study-search')studyRows(e.target.value);});
  document.addEventListener('change',e=>{if(e.target.id==='model-select'){history.pushState(null,'',hashFor('results',{model:e.target.value}));routed=location.hash;modelDetail(e.target.value);}});
  $('close-figure').addEventListener('click',()=>$('figure-dialog').close());
  window.addEventListener('hashchange',()=>route());
  window.addEventListener('popstate',()=>route());
    document.querySelector('.nav').insertAdjacentHTML('beforeend', '<button type="button" id="theme-toggle" aria-label="Toggle light/dark theme" aria-pressed="false" style="margin-left:auto;padding:8px" title="Toggle theme">🌓</button>');
  $('theme-toggle').addEventListener('click', e => {
    const isDark = document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.dataset.theme = isDark ? 'light' : 'dark';
    e.target.setAttribute('aria-pressed', isDark);
  });
  route();if(!views[parseHash().view])setHash('#overview');
})();
