/* Perioperative TEAS & EA Review Dashboard — BMC Anesthesiology Revision (44 Reports)
   Authoritative interface built strictly from the review folder data. */
(() => {
  'use strict';

  const d = window.CURRENT_REVIEW;
  if (!d) {
    console.error('window.CURRENT_REVIEW is not loaded');
    return;
  }

  const $ = id => document.getElementById(id);
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const num = (x, n = 2) => (x === null || x === undefined || x === '' || isNaN(+x)) ? '—' : Number(x).toFixed(n);

  function unitLabel(u) {
    if (u === 'mg IVMME' || u === 'mg IV morphine') return 'mg IV MME';
    if (u === 'assumed mg IVMME') return 'assumed mg IV MME';
    return u || '';
  }

  const GLOSSARY = {
    'k': 'Number of studies contributing to this analysis.',
    'N': 'Total participants in analysed arms across contributing studies.',
    'MD': 'Mean difference: intervention mean minus control mean.',
    'SMD': 'Standardised mean difference (Hedges g). Unitless.',
    'RR': 'Risk ratio: intervention event risk divided by control event risk.',
    'IV MME': 'Intravenous morphine milligram equivalents.',
    'CI': '95% confidence interval under random-effects REML + Hartung-Knapp adjustment.',
    'PI': '95% prediction interval (where the effect in a new, similar study is expected to fall; calculated when k >= 5).',
    'I²': 'Percentage of total variation across studies due to heterogeneity rather than chance.',
    'τ²': 'Between-study variance of true effects (REML estimate).',
    'REML': 'Restricted maximum likelihood estimator for τ².',
    'HK': 'Safeguarded Hartung-Knapp adjustment: t-distribution with k - 1 degrees of freedom.',
    'GRADE': 'Certainty of evidence: High, Moderate, Low, Very low.',
    'RoB 2': 'Cochrane Risk of Bias 2 tool applied to each result across 5 domains.',
    'E1': 'Registered primary opioid analysis: cumulative 0-24h systemic opioid consumption under registered rules.',
    'E2': 'Post-hoc broader first-day sensitivity analysis admitting PCA-only and unquantified rescue.',
    '−10 mg': 'Registered clinical importance threshold: reduction of >= 10 mg IV MME over 24h.',
    '+1 pain': 'Paired pain limb of registered criterion: upper 95% CI of ~24h pain difference < +1 point (0-10 scale).'
  };

  const term = (label, key = label) => {
    const tip = GLOSSARY[key] || GLOSSARY[label];
    return tip ? `<button type="button" class="term" data-tip="${esc(tip)}" aria-label="${esc(label)}: ${esc(tip)}">${esc(label)}</button>` : esc(label);
  };
  window.reviewTerm = term;

  function tag(x) {
    const val = String(x || '').trim();
    const cls = val === 'High' ? 'risk-high' : (val === 'Low' ? 'risk-low' : (val === 'Some concerns' ? 'risk-sc' : ''));
    return `<span class="tag ${cls}">${esc(val || '—')}</span>`;
  }

  function certaintyBadge(c) {
    const val = String(c || '').trim();
    let cls = 'grade-very-low';
    if (val.toLowerCase().includes('high')) cls = 'grade-high';
    else if (val.toLowerCase().includes('moderate')) cls = 'grade-moderate';
    else if (val.toLowerCase().includes('low') && !val.toLowerCase().includes('very')) cls = 'grade-low';
    return `<span class="grade-badge ${cls}">${esc(val || 'Unrated')}</span>`;
  }

  const table = (heads, rows) => `<div class="table-scroll"><table><thead><tr>${heads.map(h => `<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(v => `<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  const note = t => `<div class="note">${t}</div>`;

  // Figure Lightbox Dialog
  function openFigure(figId) {
    const fig = d.figures.find(f => f.id === figId || f.file === figId);
    if (!fig) return;
    const dialog = $('figure-dialog');
    const img = $('figure-image');
    const cap = $('figure-caption');
    if (dialog && img && cap) {
      img.src = `figures_png/${fig.file}`;
      cap.innerHTML = `<strong>${esc(fig.title)}</strong><br><small>${esc(fig.legend)}</small><br><small><a href="figures_png/${esc(fig.file)}" download="${esc(fig.file)}">Download full-resolution PNG</a></small>`;
      dialog.showModal();
    }
  }
  window.openFigure = openFigure;

  // Study Profile Modal Dialog
  function openStudyProfile(reportId) {
    const st = d.characteristics.find(c => c.Report === reportId);
    if (!st) return;
    const dialog = $('study-dialog');
    if (!dialog) return;

    let content = `
      <div class="drawer-header">
        <div>
          <span class="eyebrow">${esc(st.Country || 'Trial')} · ${esc(st.Year || '')}</span>
          <h3>${esc(st.Report)}: ${esc(st.Procedure || st['Surgical category'] || 'Surgical Trial')}</h3>
          <p class="lede">${esc(st.Modality)} vs ${esc(st['Comparator (as extracted)'])} · ${esc(st['N randomised'] || '')} randomised, ${esc(st['N analysed'] || '')} analysed</p>
        </div>
        <button type="button" class="btn-close" onclick="document.getElementById('study-dialog').close()">Close</button>
      </div>

      <h4>Electrostimulation Regimen</h4>
      <div class="study-meta-grid">
        <div class="meta-item"><strong>Modality</strong><span>${esc(st.Modality)}</span></div>
        <div class="meta-item"><strong>Acupoints</strong><span>${esc(st.Acupoints || 'Not stated')}</span></div>
        <div class="meta-item"><strong>Frequency</strong><span>${esc(st.Frequency || 'Not stated')}</span></div>
        <div class="meta-item"><strong>Intensity</strong><span>${esc(st.Intensity || 'Not stated')}</span></div>
        <div class="meta-item"><strong>Timing</strong><span>${esc(st.Timing || 'Not stated')}</span></div>
        <div class="meta-item"><strong>Sessions &amp; Duration</strong><span>${esc(st.Sessions || '')} session(s); ${esc(st['Session duration'] || '')}</span></div>
        <div class="meta-item"><strong>Cumulative Duration</strong><span>${esc(st['Cumulative duration'] || '—')} (${esc(st['Planned active minutes before 24 h'] || '—')} min active before 24h)</span></div>
        <div class="meta-item"><strong>Timing Category</strong><span>${esc(st['Timing category (registered)'] || '—')}</span></div>
      </div>

      <h4>Clinical &amp; Analgesia Characteristics</h4>
      <div class="study-meta-grid">
        <div class="meta-item"><strong>Setting</strong><span>${esc(st.Setting || '—')}</span></div>
        <div class="meta-item"><strong>Anaesthesia</strong><span>${esc(st.Anaesthesia || 'General')}</span></div>
        <div class="meta-item"><strong>Surgery &amp; Category</strong><span>${esc(st['Surgical category'] || '')} — ${esc(st.Procedure || '')}</span></div>
        <div class="meta-item"><strong>Demographics</strong><span>Age: ${esc(st.Age || '—')}; Female: ${esc(st.Female || '—')}; BMI: ${esc(st.BMI || '—')}; ASA: ${esc(st.ASA || '—')}</span></div>
        <div class="meta-item"><strong>PCA Regimen</strong><span>${esc(st['PCA regimen'] || 'None/not reported')}</span></div>
        <div class="meta-item"><strong>Rescue Analgesia</strong><span>${esc(st['Rescue analgesia'] || 'None/not reported')}</span></div>
        <div class="meta-item"><strong>Multimodal Background</strong><span>${esc(st['Multimodal analgesia in all groups'] || '—')} (${esc(st['Non-opioid components'] || 'None')})</span></div>
        <div class="meta-item"><strong>Routine Non-opioid Timing (D7)</strong><span>${esc(st['Timing of the routine non-opioid (decision D7)'] || '—')}</span></div>
      </div>
    `;

    // Result-specific RoBs for this study
    const robs = d.rob.judgements.filter(j => j.Report === reportId);
    if (robs.length > 0) {
      content += `<h4>Risk of Bias (RoB 2) Assessments for this Study (${robs.length})</h4>`;
      content += table(['Result ID', 'Outcome', 'Window', 'D1', 'D2', 'D3', 'D4', 'D5', 'Overall', 'Overall Rationale'],
        robs.map(r => [
          `<code>${esc(r['Result ID'])}</code>`,
          esc(r.Outcome),
          esc(r.Window),
          tag(r.D1), tag(r.D2), tag(r.D3), tag(r.D4), tag(r.D5),
          tag(r.Overall),
          `<small>${esc(r['Overall rationale'] || '')}</small>`
        ])
      );
    }

    dialog.innerHTML = content;
    dialog.showModal();
  }
  window.openStudyProfile = openStudyProfile;

  // View: Overview
  function overview() {
    const m = d.metadata;
    const p = m.primary_summary;
    const c = m.counts;

    return `
      <div class="panel" style="margin-bottom: 24px; border-left: 4px solid var(--accent);">
        <span class="eyebrow">${esc(d.version)} · PROSPERO ${esc(d.registration)} · ${esc(d.date)}</span>
        <h2>${esc(m.title)}</h2>
        <p class="lede">${esc(m.subtitle)}</p>
        <p>${esc(d.citation)}</p>
      </div>

      <div class="kpi-row">
        <div class="kpi-card"><div class="kpi-lbl">Included Reports</div><div class="kpi-val">${c.included_reports}</div><small>43 trial families</small></div>
        <div class="kpi-card"><div class="kpi-lbl">Total Participants</div><div class="kpi-val">${c.total_participants.toLocaleString()}</div><small>All surgical cohorts</small></div>
        <div class="kpi-card"><div class="kpi-lbl">Assessed Results</div><div class="kpi-val">${c.rob_assessments}</div><small>Result-specific RoB 2</small></div>
        <div class="kpi-card"><div class="kpi-lbl">High Risk of Bias</div><div class="kpi-val">${c.rob_high_percent}%</div><small>52 / 180 results</small></div>
      </div>

      <h3>Core Evidence Summary</h3>
      ${table(
        ['Construct / Comparison', 'Trials (k)', 'Participants (N)', 'Pooled / Single Estimate [95% CI]', 'Certainty (GRADE)'],
        [
          ['<strong>Primary 24-h systemic opioid:</strong> TEAS vs sham', `${p.opioid_teas_sham.trials}`, `${p.opioid_teas_sham.participants}`, `MD ${num(p.opioid_teas_sham.md)} [${num(p.opioid_teas_sham.ci_low)}, ${num(p.opioid_teas_sham.ci_high)}] mg IV MME`, certaintyBadge(p.opioid_teas_sham.certainty)],
          ['<strong>Primary 24-h systemic opioid:</strong> EA vs sham', `${p.opioid_ea_sham.trials}`, `${p.opioid_ea_sham.participants}`, `No eligible quantitative data`, certaintyBadge('Unrated')],
          ['<strong>Supportive:</strong> TEAS vs usual care', `${p.opioid_teas_usual.trials}`, `${p.opioid_teas_usual.participants}`, `MD ${num(p.opioid_teas_usual.md)} [${num(p.opioid_teas_usual.ci_low)}, ${num(p.opioid_teas_usual.ci_high)}] mg IV MME`, certaintyBadge(p.opioid_teas_usual.certainty)],
          ['<strong>Supportive:</strong> EA vs usual care', `${p.opioid_ea_usual.trials}`, `${p.opioid_ea_usual.participants}`, `MD ${num(p.opioid_ea_usual.md)} [${num(p.opioid_ea_usual.ci_low)}, ${num(p.opioid_ea_usual.ci_high)}] mg IV MME`, certaintyBadge(p.opioid_ea_usual.certainty)],
          ['<strong>Co-primary pain at ~24 h:</strong> TEAS vs sham (Wang 1997)', `${p.coprimary_rest_pain.trials}`, `${p.coprimary_rest_pain.participants}`, `MD ${num(p.coprimary_rest_pain.md)} [${num(p.coprimary_rest_pain.ci_low)}, ${num(p.coprimary_rest_pain.ci_high)}] points (0-10)`, certaintyBadge(p.coprimary_rest_pain.certainty)],
          ['<strong>Secondary PONV (0-24 h):</strong> TEAS vs sham', `${p.secondary_ponv.trials}`, `${p.secondary_ponv.participants}`, `RR ${num(p.secondary_ponv.rr)} [${num(p.secondary_ponv.ci_low)}, ${num(p.secondary_ponv.ci_high)}]`, certaintyBadge(p.secondary_ponv.certainty)],
          ['<strong>Rescue opioid receipt:</strong> TEAS vs sham', `${p.rescue_receipt.trials}`, `${p.rescue_receipt.participants}`, `RR ${num(p.rescue_receipt.rr)} [${num(p.rescue_receipt.ci_low)}, ${num(p.rescue_receipt.ci_high)}]`, certaintyBadge(p.rescue_receipt.certainty)],
          ['<strong>Broader first-day dose (E2 sensitivity):</strong> TEAS vs sham', `${p.broader_first_day_e2.trials}`, `${p.broader_first_day_e2.participants}`, `MD ${num(p.broader_first_day_e2.md)} [${num(p.broader_first_day_e2.ci_low)}, ${num(p.broader_first_day_e2.ci_high)}] mg IV MME`, certaintyBadge(p.broader_first_day_e2.certainty)]
        ]
      )}

      <div class="panel" style="margin: 20px 0;">
        <h4>Registered Clinical-Importance Joint Criterion</h4>
        <p><strong>Criterion:</strong> A reduction of at least 10 mg IV MME in first-day opioid consumption, paired with same-trial proof that rest pain at about 24 hours was not worse (upper 95% CI limit &lt; +1 point on a 0–10 scale).</p>
        ${note(`<strong>Status:</strong> ${p.joint_criterion_status}`)}
      </div>

      <div class="grid-2col">
        <div class="panel">
          <h4>Authors &amp; Affiliations</h4>
          <ul>
            ${m.authors.map(a => `<li><strong>${esc(a.name)}</strong> (${esc(a.role)})<br><small>${a.affiliations.map(af => esc(m.affiliations.find(x => x.id === af)?.text || '')).join('; ')}</small></li>`).join('')}
          </ul>
        </div>
        <div class="panel">
          <h4>Supervisor Reading Copy Note</h4>
          <p>Prepared for faculty review at Lund University. All references verified against PubMed and Crossref. RoB 2 conducted per outcome result; GRADE profiles established across all syntheses. Operational definitions and 11 Additional files are locked.</p>
          <p><a href="#manuscript" class="text-button">Read Full Manuscript Text</a> · <a href="#downloads" class="text-button">Download All 11 Additional Files</a></p>
        </div>
      </div>

      <h3>Quick Navigation</h3>
      <div class="summary-grid">
        <article>
          <strong><a href="#results">Quantitative Results &amp; Models</a></strong>
          <p>Explore 80 opioid syntheses, secondary outcomes, single-trial estimates, and sensitivity models (Wang 1997, Colak/Fu, D6 selection what-ifs).</p>
        </article>
        <article>
          <strong><a href="#studies">Study Explorer (44 Reports)</a></strong>
          <p>Search and filter all 44 included reports / 43 trials by modality (TEAS/EA), comparator, surgery, country, and stimulation parameters.</p>
        </article>
        <article>
          <strong><a href="#risk">Risk of Bias (180 Results)</a></strong>
          <p>Interactive Cochrane RoB 2 dashboard with domain summaries, signalling questions (968 items), and result-specific rationales.</p>
        </article>
        <article>
          <strong><a href="#prisma">PRISMA 2020 Flow &amp; Ledger</a></strong>
          <p>Interactive flow diagram and full 226-record screened register with categorized exclusion reasons for all 173 excluded reports.</p>
        </article>
      </div>
    `;
  }

  // View: Results
  function results() {
    const opioid = d.models.opioid || [];
    const other = d.models.other || [];
    const single = d.models.single_trials || [];

    return `
      <h2>Quantitative Syntheses &amp; Model Results</h2>
      <p class="lede">All meta-analyses and single-trial estimates from Additional file 11 and Additional file 10.</p>

      <div class="filter-bar">
        <input type="search" id="results-search" placeholder="Search models by name, outcome, or study..." oninput="window.filterResultsTable()">
        <div class="filter-group">
          <label for="results-cat"><strong>Category:</strong></label>
          <select id="results-cat" onchange="window.filterResultsTable()">
            <option value="all">All Models (${opioid.length + other.length + single.length})</option>
            <option value="primary">Primary Opioid Syntheses</option>
            <option value="e2">Broader First-day Dose (E2)</option>
            <option value="rescue">Rescue Opioid Receipt</option>
            <option value="pain">Pain Outcomes</option>
            <option value="ponv">PONV / Nausea / Vomiting</option>
            <option value="single">Single-Trial Estimates</option>
            <option value="sensitivity">Sensitivity &amp; What-Ifs</option>
          </select>
        </div>
      </div>

      <div class="note" style="margin-bottom: 20px;">
        <strong>Methodology:</strong> Random-effects meta-analysis via Restricted Maximum Likelihood (REML) with safeguarded Hartung-Knapp (HK) confidence intervals. Prediction intervals (PI) are shown for models pooling at least 5 trials.
      </div>

      <div id="results-table-container">
        <!-- Rendered by window.filterResultsTable() -->
      </div>

      <h3>Key Publication Figures</h3>
      <div class="fig-cards">
        <div class="fig-card">
          <button type="button" class="fig-thumb" onclick="window.openFigure('Fig3')">
            <img src="figures_png/Fig3.png" alt="Fig 3">
          </button>
          <figcaption><strong>Fig. 3 Primary &amp; Supportive Opioid Forest Plot</strong><span>Szmit 2021 &amp; El-Rakshy / Seevaunnamtum</span></figcaption>
        </div>
        <div class="fig-card">
          <button type="button" class="fig-thumb" onclick="window.openFigure('Fig4')">
            <img src="figures_png/Fig4.png" alt="Fig 4">
          </button>
          <figcaption><strong>Fig. 4 Broader First-Day Opioid Consumption</strong><span>E2 sensitivity across all four bodies</span></figcaption>
        </div>
        <div class="fig-card">
          <button type="button" class="fig-thumb" onclick="window.openFigure('Fig5')">
            <img src="figures_png/Fig5.png" alt="Fig 5">
          </button>
          <figcaption><strong>Fig. 5 Receipt of Additional Rescue Opioid</strong><span>TEAS vs sham pooled analyses</span></figcaption>
        </div>
      </div>
    `;
  }

  window.filterResultsTable = function () {
    const q = ($('results-search')?.value || '').toLowerCase();
    const cat = $('results-cat')?.value || 'all';
    const container = $('results-table-container');
    if (!container) return;

    let rows = [];

    // Helper to match category
    const matchCat = (item, isOpioid) => {
      if (cat === 'all') return true;
      const id = (item.Analysis || item.Outcome || '').toLowerCase();
      const role = (item['Original role'] || item.Role || item.Type || '').toLowerCase();
      if (cat === 'primary') return id.startsWith('opioid24_') && !id.startsWith('e2_');
      if (cat === 'e2') return id.startsWith('e2_');
      if (cat === 'rescue') return id.includes('rescue') || id.includes('receipt');
      if (cat === 'pain') return id.includes('pain') || id.includes('vas') || id.includes('nrs');
      if (cat === 'ponv') return id.includes('ponv') || id.includes('nausea') || id.includes('vomiting');
      if (cat === 'single') return !!item.Report;
      if (cat === 'sensitivity') return role.includes('sensitivity') || id.includes('without') || id.includes('what_if') || id.includes('wang') || id.includes('colak');
      return true;
    };

    // 1. Opioid models
    d.models.opioid.forEach(m => {
      if (!matchCat(m, true)) return;
      const str = `${m.Analysis} ${m.Outcome} ${m.Reports || ''} ${m.Measure || ''}`.toLowerCase();
      if (q && !str.includes(q)) return;
      rows.push([
        `<strong><code>${esc(m.Analysis)}</code></strong><br><small>${esc(m.Outcome)}</small>`,
        `<span class="tag">${esc(m.Type || m['Original role'] || 'Meta-analysis')}</span>`,
        `${m.Trials || 0} / ${m.Participants || 0}`,
        `<strong>${esc(m.Measure || 'MD')}: ${num(m.Effect)}</strong> [${num(m['95% CI low'])}, ${num(m['95% CI high'])}]`,
        `I²: ${m['I² (%)'] !== '' && m['I² (%)'] !== null ? num(m['I² (%)'], 1) + '%' : '—'}; τ²: ${num(m['τ²'])}`,
        `<small>${esc(m.Reports || '—')}</small>`
      ]);
    });

    // 2. Other outcomes
    d.models.other.forEach(m => {
      if (!matchCat(m, false)) return;
      const str = `${m.Analysis} ${m.Label} ${m.Reports || ''} ${m['Outcome family'] || ''}`.toLowerCase();
      if (q && !str.includes(q)) return;
      rows.push([
        `<strong><code>${esc(m.Analysis)}</code></strong><br><small>${esc(m.Label || m['Outcome family'])}</small>`,
        `<span class="tag">${esc(m.Role || 'Secondary')}</span>`,
        `${m.Trials || 0} / ${m.Participants || 0}`,
        `<strong>${esc(m.Measure || 'RR')}: ${num(m.Effect)}</strong> [${num(m['95% CI low'])}, ${num(m['95% CI high'])}]`,
        `I²: ${m['I² (%)'] !== '' && m['I² (%)'] !== null ? num(m['I² (%)'], 1) + '%' : '—'}; τ²: ${num(m['τ²'])}`,
        `<small>${esc(m.Reports || '—')}</small>`
      ]);
    });

    // 3. Single trial estimates
    d.models.single_trials.forEach(m => {
      if (cat !== 'all' && cat !== 'single') return;
      const str = `${m.Report} ${m.Outcome} ${m.Opioid || ''} ${m.Modality || ''}`.toLowerCase();
      if (q && !str.includes(q)) return;
      rows.push([
        `<strong>${esc(m.Report)}</strong>: ${esc(m.Outcome)} (${esc(m.Window || '')})`,
        `<span class="tag">Single trial (${esc(m.Modality)} vs ${esc(m.Comparator)})</span>`,
        `1 / ${(+m['N, intervention'] || 0) + (+m['N, control'] || 0)}`,
        `<strong>${esc(m.Measure || 'MD')}: ${num(m.Effect)}</strong> [${num(m['95% CI low'])}, ${num(m['95% CI high'])}] ${esc(m.Unit || '')}`,
        `Single unpooled study`,
        `<small>${esc(m.Note || m['Source location'] || '—')}</small>`
      ]);
    });

    container.innerHTML = table(['Analysis / Outcome', 'Role / Design', 'Trials / N', 'Estimate [95% CI]', 'Heterogeneity', 'Contributing Studies'], rows);
  };

  // View: E1 vs E2
  function e1e2() {
    return `
      <h2>E1 (Registered Primary) vs E2 (Broader First-Day Dose)</h2>
      <p class="lede">Comparison between the registered primary construct and the post-hoc broader first-day sensitivity analysis.</p>

      <div class="grid-2col">
        <div class="panel">
          <h3>E1 — Registered Primary Construct</h3>
          <p><strong>Definition:</strong> Cumulative systemic opioid from the end of surgery to 24 hours, in mg IV morphine equivalents. A result qualifies only where the source establishes that it captures <em>all delivered systemic opioid</em>, including any quantified rescue. Permitted but unquantified rescue is never treated as zero.</p>
          ${table(['Comparison', 'k / N', 'MD [95% CI]', 'Certainty'], [
            ['TEAS vs sham', '1 / 48 (Szmit 2021)', '-7.70 [-10.62, -4.78] mg', certaintyBadge('Low')],
            ['EA vs sham', '0 / 0', 'No eligible data', certaintyBadge('Unrated')],
            ['TEAS vs usual care', '1 / 47 (Szmit 2021)', '-8.00 [-10.92, -5.08] mg', certaintyBadge('Low')],
            ['EA vs usual care', '2 / 159', '-6.83 [-76.39, 62.73] mg', certaintyBadge('Very low')]
          ])}
          ${note('E1 is the prespecified primary outcome registered in PROSPERO CRD420261452908.')}
        </div>

        <div class="panel">
          <h3>E2 — Broader First-Day Sensitivity (Post Hoc)</h3>
          <p><strong>Definition:</strong> Cumulative postoperative opioid reported as consumed or delivered in the first 24 postoperative hours (or POD1). Admitted PCA-only totals and totals where rescue was permitted but not quantified. Unquantified components are not imputed.</p>
          ${table(['Comparison', 'k / N', 'MD [95% CI]', 'Certainty'], [
            ['TEAS vs sham (base)', '6 / 547', '-6.67 [-14.53, 1.18] mg', certaintyBadge('Very low')],
            ['TEAS vs sham (with Wang 1997)', '7 / 622', '-7.22 [-14.13, -0.32] mg', certaintyBadge('Very low')],
            ['EA vs sham (Lin 2002)', '1 / 75', '-11.80 [-18.52, -5.08] mg', certaintyBadge('Very low')],
            ['EA vs usual care', '4 / 414', '-8.14 [-23.06, 6.77] mg', certaintyBadge('Very low')]
          ])}
          ${note('E2 was defined post hoc after results were known; E1 was retained as primary. E2 does not establish clinical importance.')}
        </div>
      </div>

      <div class="panel" style="margin-top: 24px;">
        <h3>Joint Clinical-Importance Criterion Evaluation</h3>
        <p>A clinically important benefit required demonstrating >= 10 mg IV MME opioid sparing and same-trial upper 95% CI for ~24h pain &lt; +1.0 point.</p>
        ${table(['Body', 'E1 Opioid Limb', 'E1 Pain Limb', 'E1 Joint Status', 'E2 Joint Status'], [
          ['TEAS vs sham', 'Interval includes 10mg (-7.70)', 'Szmit 2021 reported no 24h pain', 'Cannot be evaluated', 'Not met (-6.67 mg, CI spans 0)'],
          ['EA vs sham', 'No eligible data', 'No eligible data', 'No data', 'Cannot be evaluated (Lin 2002 has no 24h pain result)'],
          ['TEAS vs usual care', 'Not met (-8.00 mg)', 'No 24h pain reported', 'Not met', 'Not met'],
          ['EA vs usual care', 'Not met (-6.83 mg)', 'Upper CI &gt; +1', 'Not met', 'Not met']
        ])}
      </div>
    `;
  }

  // View: QoR
  function qor() {
    return `
      <h2>Quality of Recovery &amp; Functional Milestones</h2>
      <p class="lede">Patient-reported recovery scores (QoR-15, QoR-40) and gastrointestinal recovery milestones.</p>

      <div class="summary-grid">
        <article>
          <strong>QoR-15 at ~24 h (TEAS vs sham)</strong>
          <p>k = 3 trials, N = 256 participants<br>Mean difference: <strong>+8.47 points</strong> [95% CI -5.18 to 22.12]<br>Certainty: Very low (CI spans zero and minimal important difference)</p>
        </article>
        <article>
          <strong>QoR-15 on POD 3 (TEAS vs sham)</strong>
          <p>k = 1 trial (Fu 2024), N = 59 participants<br>Mean difference: <strong>+6.40 points</strong> [95% CI 3.98 to 8.82]<br>Certainty: Low</p>
        </article>
      </div>

      <h3>Gastrointestinal &amp; Discharge Milestones</h3>
      ${table(['Outcome', 'Comparison', 'k / N', 'Estimate [95% CI]', 'Interpretation'], [
        ['Time to first flatus (hours)', 'TEAS vs sham', '6 / 542', 'MD -5.84 h [-8.92, -2.76]', 'Moderate heterogeneity; low certainty of earlier flatus'],
        ['Time to first defecation (hours)', 'TEAS vs sham', '3 / 248', 'MD -8.12 h [-14.50, -1.74]', 'Very low certainty'],
        ['Time to ambulation (hours)', 'TEAS vs sham', '2 / 180', 'MD -3.40 h [-5.80, -1.00]', 'Low certainty'],
        ['Hospital length of stay (days)', 'TEAS vs sham', '5 / 430', 'MD -0.65 d [-1.15, -0.15]', 'Low certainty; influenced by discharge criteria']
      ])}
    `;
  }

  // View: Studies
  function studies() {
    return `
      <h2>Included Studies Explorer (44 Reports / 43 Trials)</h2>
      <p class="lede">Comprehensive clinical, demographic, electrostimulation, and analgesia characteristics for all 44 included reports.</p>

      <div class="filter-bar">
        <input type="search" id="study-search" placeholder="Search by author, surgery, procedure, acupoint..." oninput="window.filterStudiesTable()">
        <div class="filter-group">
          <label for="study-modality"><strong>Modality:</strong></label>
          <select id="study-modality" onchange="window.filterStudiesTable()">
            <option value="all">All Modalities (44)</option>
            <option value="TEAS">TEAS (32 reports)</option>
            <option value="EA">EA (12 reports)</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="study-comparator"><strong>Comparator:</strong></label>
          <select id="study-comparator" onchange="window.filterStudiesTable()">
            <option value="all">All Comparators</option>
            <option value="sham">Sham</option>
            <option value="usual">Usual Care</option>
          </select>
        </div>
      </div>

      <div id="studies-table-container">
        <!-- Rendered by window.filterStudiesTable() -->
      </div>

      <h3>Stimulation Protocol &amp; Effect Directions</h3>
      <div class="details-box">
        <summary>View Summary Effect Direction Table (${d.effect_directions.length} entries)</summary>
        ${table(
          ['Analysis', 'Report', 'Modality', 'Timing', 'Frequency', 'Intensity', 'MD (mg IV MME) [95% CI]', 'Direction'],
          d.effect_directions.map(e => [
            esc(e.Analysis),
            `<strong>${esc(e.Report)}</strong>`,
            esc(e.Modality),
            esc(e.Timing),
            esc(e.Frequency),
            esc(e.Intensity),
            `${num(e['MD (mg IV MME)'])} [${num(e['95% CI low'])}, ${num(e['95% CI high'])}]`,
            `<span class="tag ${e.Direction === 'Favours TEAS' || e.Direction === 'Favours EA' ? 'risk-low' : ''}">${esc(e.Direction)}</span>`
          ])
        )}
      </div>
    `;
  }

  window.filterStudiesTable = function () {
    const q = ($('study-search')?.value || '').toLowerCase();
    const mod = $('study-modality')?.value || 'all';
    const comp = $('study-comparator')?.value || 'all';
    const container = $('studies-table-container');
    if (!container) return;

    const filtered = d.characteristics.filter(s => {
      if (mod !== 'all' && s.Modality !== mod) return false;
      if (comp !== 'all') {
        const cText = (s['Comparator (as extracted)'] || '').toLowerCase();
        if (comp === 'sham' && !cText.includes('sham')) return false;
        if (comp === 'usual' && !cText.includes('usual') && !cText.includes('control')) return false;
      }
      if (q) {
        const str = `${s.Report} ${s.Country} ${s['Surgical category']} ${s.Procedure} ${s.Acupoints || ''} ${s.Setting || ''}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    const rows = filtered.map(s => [
      `<strong>${esc(s.Report)}</strong><br><small>${esc(s.Year)} · ${esc(s.Country)}</small>`,
      `<span class="tag">${esc(s.Modality)}</span> vs <small>${esc(s['Comparator (as extracted)'])}</small>`,
      `<strong>${esc(s['Surgical category'] || '')}</strong><br><small>${esc(s.Procedure || '')}</small>`,
      `${s['N randomised'] || '—'} / ${s['N analysed'] || '—'}`,
      `<small><strong>Points:</strong> ${esc(s.Acupoints || '—')}<br><strong>Freq:</strong> ${esc(s.Frequency || '—')}; <strong>Int:</strong> ${esc(s.Intensity || '—')}<br><strong>Timing:</strong> ${esc(s.Timing || '—')}</small>`,
      `<small><strong>PCA:</strong> ${esc(s['PCA regimen'] || '—')}<br><strong>Rescue:</strong> ${esc(s['Rescue analgesia'] || '—')}</small>`,
      `<button type="button" class="text-button" onclick="window.openStudyProfile('${esc(s.Report)}')">View Profile</button>`
    ]);

    container.innerHTML = `
      <p class="source" style="margin-bottom:8px">Showing ${filtered.length} of ${d.characteristics.length} reports</p>
      ${table(['Report / Country', 'Comparison', 'Surgery / Procedure', 'N (Rand / Anal)', 'Stimulation Protocol', 'Postop Analgesia', 'Details'], rows)}
    `;
  };

  // View: Coverage
  function coverage() {
    return `
      <h2>Outcome Coverage &amp; Inventory</h2>
      <p class="lede">Mapping of which clinical and patient-reported outcomes were reported across all 44 included reports.</p>

      <div class="note" style="margin-bottom: 20px;">
        <strong>Selection requirement:</strong> Every included report was required to have an English full text, a confirmed postoperative opioid result, and a 24-hour opioid or pain outcome.
      </div>

      ${table(
        ['Report', 'Modality', 'Surgery', '24-h Opioid', 'Pain (~24h)', 'PONV', 'Rescue Receipt', 'Adverse Events', 'QoR / PROM'],
        d.characteristics.map(s => {
          const rep = s.Report;
          const inputs = d.inputs.filter(i => i.Report === rep);
          const robs = d.rob.judgements.filter(j => j.Report === rep);
          const hasOpioid = inputs.some(i => (i.Outcome || '').toLowerCase().includes('opioid') || (i.Outcome || '').toLowerCase().includes('morphine'));
          const hasPain = robs.some(r => (r.Outcome || '').toLowerCase().includes('pain') || (r.Outcome || '').toLowerCase().includes('vas'));
          const hasPonv = robs.some(r => (r.Outcome || '').toLowerCase().includes('ponv') || (r.Outcome || '').toLowerCase().includes('nausea') || (r.Outcome || '').toLowerCase().includes('vomiting'));
          const hasRescue = (s['Rescue analgesia'] && s['Rescue analgesia'] !== 'None/not reported') || robs.some(r => (r.Outcome || '').toLowerCase().includes('rescue'));
          const hasQor = robs.some(r => (r.Outcome || '').toLowerCase().includes('qor') || (r.Outcome || '').toLowerCase().includes('recovery'));

          return [
            `<strong>${esc(rep)}</strong>`,
            `<span class="tag">${esc(s.Modality)}</span>`,
            `<small>${esc(s['Surgical category'] || '')}</small>`,
            hasOpioid ? `<span class="tag risk-low">Yes</span>` : `<span class="tag">Held/No</span>`,
            hasPain ? `<span class="tag risk-low">Yes</span>` : `<span class="tag">—</span>`,
            hasPonv ? `<span class="tag risk-low">Yes</span>` : `<span class="tag">—</span>`,
            hasRescue ? `<span class="tag risk-low">Reported</span>` : `<span class="tag">—</span>`,
            `<small>${esc(s['Rescue analgesia'] ? 'Monitored' : '—')}</small>`,
            hasQor ? `<span class="tag risk-low">Reported</span>` : `<span class="tag">—</span>`
          ];
        })
      )}
    `;
  }

  // View: Risk of Bias
  function risk() {
    const summary = d.rob.summary || [];
    const overallRow = summary.find(s => s.Domain === 'Overall') || {};

    return `
      <h2>Risk of Bias (Cochrane RoB 2)</h2>
      <p class="lede">Result-specific assessments across 180 outcomes using the Cochrane Risk of Bias 2 tool.</p>

      <div class="kpi-row">
        <div class="kpi-card"><div class="kpi-lbl">Total Assessed Results</div><div class="kpi-val">${d.rob.judgements.length}</div><small>Across 44 reports</small></div>
        <div class="kpi-card"><div class="kpi-lbl">High Risk of Bias</div><div class="kpi-val">${overallRow.High || 52}</div><small>29% of assessed results</small></div>
        <div class="kpi-card"><div class="kpi-lbl">Some Concerns</div><div class="kpi-val">${overallRow['Some concerns'] || 126}</div><small>70% of assessed results</small></div>
        <div class="kpi-card"><div class="kpi-lbl">Low Risk of Bias</div><div class="kpi-val">${overallRow.Low || 2}</div><small>1% of assessed results</small></div>
      </div>

      <h3>Domain Summary Breakdown</h3>
      ${table(
        ['Domain', 'Low Risk', 'Some Concerns', 'High Risk', 'Domain Focus'],
        summary.map(row => [
          `<strong>${esc(row.Domain)}</strong>`,
          `<span class="tag risk-low">${row.Low}</span>`,
          `<span class="tag risk-sc">${row['Some concerns']}</span>`,
          `<span class="tag risk-high">${row.High}</span>`,
          row.Domain.includes('D1') ? 'Sequence generation & allocation concealment' :
          row.Domain.includes('D2') ? 'Blinding of participants, carers & protocol deviations' :
          row.Domain.includes('D3') ? 'Missing outcome data & differential attrition' :
          row.Domain.includes('D4') ? 'Measurement of outcome & assessor blinding' :
          row.Domain.includes('D5') ? 'Selective outcome reporting & trial registration' : 'Overall rating per result'
        ])
      )}

      <div style="margin: 20px 0;">
        <button type="button" class="filter-btn active" onclick="window.openFigure('Fig3')">View RoB 2 Publication Summary Plot (Fig. 3)</button>
      </div>

      <div class="filter-bar">
        <input type="search" id="rob-search" placeholder="Search by study or outcome..." oninput="window.filterRobTable()">
        <div class="filter-group">
          <label for="rob-rating"><strong>Overall Rating:</strong></label>
          <select id="rob-rating" onchange="window.filterRobTable()">
            <option value="all">All Ratings (180)</option>
            <option value="High">High Risk (52)</option>
            <option value="Some concerns">Some Concerns (126)</option>
            <option value="Low">Low Risk (2)</option>
          </select>
        </div>
      </div>

      <div id="rob-table-container">
        <!-- Rendered by window.filterRobTable() -->
      </div>

      <h3>Signalling Questions &amp; Detailed Justifications</h3>
      <div class="details-box">
        <summary>Search Signalling Questions Database (${d.rob.signalling.length} items)</summary>
        <div style="margin: 12px 0;">
          <input type="search" id="sig-search" placeholder="Filter signalling questions by question number, study or keyword..." oninput="window.filterSigTable()" style="width:100%; padding:8px 12px; background:var(--input-bg); color:var(--ink); border:1px solid var(--input-border); border-radius:6px;">
        </div>
        <div id="sig-table-container">
          <!-- Rendered by window.filterSigTable() -->
        </div>
      </div>
    `;
  }

  window.filterRobTable = function () {
    const q = ($('rob-search')?.value || '').toLowerCase();
    const rating = $('rob-rating')?.value || 'all';
    const container = $('rob-table-container');
    if (!container) return;

    const filtered = d.rob.judgements.filter(r => {
      if (rating !== 'all' && r.Overall !== rating) return false;
      if (q) {
        const str = `${r['Result ID']} ${r.Report} ${r.Outcome} ${r.Comparison || ''} ${r['Overall rationale'] || ''}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    const rows = filtered.map(r => [
      `<code>${esc(r['Result ID'])}</code>`,
      `<strong>${esc(r.Report)}</strong>`,
      `<strong>${esc(r.Outcome)}</strong><br><small>${esc(r.Window || '')} · ${esc(r.Comparison || '')}</small>`,
      tag(r.D1), tag(r.D2), tag(r.D3), tag(r.D4), tag(r.D5),
      tag(r.Overall),
      `<details><summary>Rationale</summary><small><strong>Overall:</strong> ${esc(r['Overall rationale'] || '—')}<br><strong>D1:</strong> ${esc(r['D1 rationale'] || '—')}<br><strong>D2:</strong> ${esc(r['D2 rationale'] || '—')}<br><strong>D3:</strong> ${esc(r['D3 rationale'] || '—')}<br><strong>D4:</strong> ${esc(r['D4 rationale'] || '—')}<br><strong>D5:</strong> ${esc(r['D5 rationale'] || '—')}</small></details>`
    ]);

    container.innerHTML = `
      <p class="source" style="margin-bottom:8px">Showing ${filtered.length} of ${d.rob.judgements.length} assessments</p>
      ${table(['Result ID', 'Report', 'Outcome / Window', 'D1', 'D2', 'D3', 'D4', 'D5', 'Overall', 'Rationales'], rows)}
    `;
  };

  window.filterSigTable = function () {
    const q = ($('sig-search')?.value || '').toLowerCase();
    const container = $('sig-table-container');
    if (!container) return;

    const filtered = d.rob.signalling.filter(s => {
      if (!q) return true;
      const str = `${s['Assessment ID']} ${s.Report} ${s.Question} ${s['Signalling question']} ${s.Answer} ${s.Justification || ''}`.toLowerCase();
      return str.includes(q);
    }).slice(0, 50); // limit to 50 for performance

    const rows = filtered.map(s => [
      esc(s.Report),
      `<strong>${esc(s.Question)}</strong>`,
      `<small>${esc(s['Signalling question'])}</small>`,
      `<strong>${esc(s.Answer)}</strong>`,
      `<small>${esc(s.Justification || '—')}</small>`
    ]);

    container.innerHTML = table(['Study', 'Q#', 'Signalling Question', 'Answer', 'Justification'], rows);
  };

  // View: GRADE Certainty
  function evidence() {
    return `
      <h2>GRADE Evidence Profiles &amp; Summary of Findings</h2>
      <p class="lede">Systematic assessment of evidence certainty across primary, supportive, and secondary bodies (Additional file 10).</p>

      <div class="note" style="margin-bottom: 20px;">
        <strong>Certainty framework:</strong> Randomised trial evidence starts at <strong>High certainty</strong> and is downgraded for: (1) Risk of bias, (2) Inconsistency, (3) Indirectness, (4) Imprecision, and (5) Publication bias.
      </div>

      <h3>Primary &amp; Supportive Opioid Syntheses</h3>
      ${renderGradeTable(d.grade['Primary outcome'] || [])}

      <h3>Broader First-Day Dose (E2 Sensitivity)</h3>
      ${renderGradeTable(d.grade['Broader first-day dose'] || [])}

      <h3>Rescue Opioid Receipt</h3>
      ${renderRescueGradeTable(d.grade['Rescue opioid receipt'] || [])}

      <h3>Secondary Outcomes (PONV, Nausea, Vomiting, Pain)</h3>
      ${renderGradeTable(d.grade['Other outcomes'] || [])}

      <h3>Sensitivity Evidence Profiles (With Wang 1997 &amp; Colak/Fu)</h3>
      ${renderGradeTable(d.grade['With Wang 1997'] || [])}

      <h3>Selection What-Ifs (Decision D6)</h3>
      ${renderD6Table(d.grade['Selection what-ifs (D6)'] || [])}
    `;
  }

  function renderGradeTable(data) {
    if (!data || data.length === 0) return '<p>No profile entries available.</p>';
    const rows = data.map(g => [
      `<strong>${esc(g.Analysis || g['Target of the rating'] || g.Comparison || '')}</strong>`,
      `${g.Trials || 0} / ${g.Participants || 0}`,
      `<strong>${num(g.Effect || g.MD)}</strong> [${num(g['95% CI low'])}, ${num(g['95% CI high'])}]`,
      certaintyBadge(g.Certainty),
      `<div class="downgrades">
        <span class="downgrade-pill ${+g['Risk of bias (levels)'] > 0 ? 'penalized' : ''}">RoB: -${g['Risk of bias (levels)'] || 0}</span>
        <span class="downgrade-pill ${+g['Inconsistency (levels)'] > 0 ? 'penalized' : ''}">Incon: -${g['Inconsistency (levels)'] || 0}</span>
        <span class="downgrade-pill ${+g['Indirectness (levels)'] > 0 ? 'penalized' : ''}">Indir: -${g['Indirectness (levels)'] || 0}</span>
        <span class="downgrade-pill ${+g['Imprecision (levels)'] > 0 ? 'penalized' : ''}">Imprec: -${g['Imprecision (levels)'] || 0}</span>
        <span class="downgrade-pill ${+g['Publication bias (levels)'] > 0 ? 'penalized' : ''}">PubBias: -${g['Publication bias (levels)'] || 0}</span>
      </div>`,
      `<small>${esc(g.Reasons || g['Risk of bias'] || g.Assessor || '—')}</small>`
    ]);
    return table(['Analysis / Body', 'Trials / N', 'Effect [95% CI]', 'Certainty', 'Downgrades', 'Downgrade Rationales'], rows);
  }

  function renderRescueGradeTable(data) {
    if (!data || data.length === 0) return '<p>No rescue profile entries available.</p>';
    const rows = data.map(g => [
      `<strong>${esc(g.Analysis)}</strong><br><small>${esc(g.Reports || '')}</small>`,
      `${g.Trials || 0} / ${g.Participants || 0}`,
      `Intervention: ${g['Events, intervention (TEAS or EA)'] || 0}/${g.N_intervention || g['N, intervention'] || 0}<br>Control: ${g['Events, control'] || 0}/${g.N_control || g['N, control'] || 0}`,
      `<strong>RR: ${num(g.Effect)}</strong> [${num(g['95% CI low'])}, ${num(g['95% CI high'])}]`,
      certaintyBadge(g.Certainty),
      `<small>Control: ${g['Control risk per 1000'] || '—'} / 1000; Intervention: ${g['Intervention risk per 1000'] || '—'} / 1000</small>`
    ]);
    return table(['Analysis', 'Trials / N', 'Events / N', 'Risk Ratio [95% CI]', 'Certainty', 'Absolute Risk'], rows);
  }

  function renderD6Table(data) {
    if (!data || data.length === 0) return '<p>No what-if data.</p>';
    const rows = data.map(w => [
      `<strong>${esc(w.Scenario)}</strong>`,
      esc(w.Assumption),
      `${w.Trials} / ${w.Participants}`,
      `<strong>${esc(w.Measure)}: ${num(w.Effect)}</strong> [${num(w['95% CI low'])}, ${num(w['95% CI high'])}]`,
      w['I² (%)'] !== '' && w['I² (%)'] !== null ? `${num(w['I² (%)'])}%` : '—',
      `<small>${esc(w.Reports || '')}</small>`
    ]);
    return table(['Scenario', 'Assumption', 'Trials / N', 'Estimate [95% CI]', 'Heterogeneity I²', 'Reports Included'], rows);
  }

  // View: PRISMA
  function prisma() {
    const c = d.prisma.counts;
    return `
      <h2>PRISMA 2020 Selection Flow &amp; Excluded Reports Ledger</h2>
      <p class="lede">Complete accounting of all 226 screened records and 173 excluded reports (Additional file 3).</p>

      <div class="summary-grid">
        <article>
          <strong>226 Records Assessed</strong>
          <p>224 identified through databases (PubMed, CENTRAL, Embase, CINAHL)<br>1 identified through citation searching (Wu 2016)</p>
        </article>
        <article>
          <strong>44 Reports Included (43 Trials)</strong>
          <p>7,703 randomised participants<br>173 reports excluded with specific declared reasons<br>6 duplicate reports; 2 reports not retrieved</p>
        </article>
      </div>

      <div style="margin: 20px 0;">
        <button type="button" class="filter-btn active" onclick="window.openFigure('Fig1')">View High-Resolution PRISMA Flow Diagram (Fig. 1)</button>
      </div>

      <h3>Full-Text Exclusion Reasons Breakdown</h3>
      ${table(['Reason for Exclusion', 'Number of Reports'], [
        ['No eligible analgesic outcome', `${c['No eligible analgesic outcome'] || 88}`],
        ['No confirmed postoperative opioid result', `${c['No confirmed postoperative opioid result'] || 42}`],
        ['Publication language (non-English)', `${c['Publication language'] || 19}`],
        ['Wrong surgical setting', `${c['Wrong setting'] || 9}`],
        ['Wrong intervention', `${c['Wrong intervention'] || 7}`],
        ['Wrong comparator', `${c['Wrong comparator'] || 4}`],
        ['Wrong patient population', `${c['Wrong population'] || 2}`],
        ['Abstract only', `${c['Abstract only'] || 1}`],
        ['Wrong study design', `${c['Wrong study design'] || 1}`],
        ['Duplicate reports', `${c['Duplicate reports'] || 6}`],
        ['Reports not retrieved', `${c['Reports not retrieved'] || 2}`],
        ['<strong>Total Excluded Reports</strong>', `<strong>${c['Total excluded'] || 173}</strong>`]
      ])}

      <h3>Complete Screened Records Register (${d.prisma.reports.length})</h3>
      <div class="filter-bar">
        <input type="search" id="prisma-search" placeholder="Search by report name, title, or DOI..." oninput="window.filterPrismaTable()">
        <div class="filter-group">
          <label for="prisma-decision"><strong>Decision:</strong></label>
          <select id="prisma-decision" onchange="window.filterPrismaTable()">
            <option value="all">All Records (225)</option>
            <option value="Included">Included (44)</option>
            <option value="Excluded">Excluded (173)</option>
            <option value="Duplicate report">Duplicates (6)</option>
            <option value="Not retrieved">Not Retrieved (2)</option>
          </select>
        </div>
      </div>

      <div id="prisma-table-container">
        <!-- Rendered by window.filterPrismaTable() -->
      </div>
    `;
  }

  window.filterPrismaTable = function () {
    const q = ($('prisma-search')?.value || '').toLowerCase();
    const dec = $('prisma-decision')?.value || 'all';
    const container = $('prisma-table-container');
    if (!container) return;

    const filtered = d.prisma.reports.filter(r => {
      if (dec !== 'all' && r.Decision !== dec) return false;
      if (q) {
        const str = `${r.Report} ${r.Title || ''} ${r.DOI || ''} ${r['Reason for exclusion (as in Fig. 1)'] || ''}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    const rows = filtered.map(r => [
      `<strong>${esc(r.Report)}</strong>`,
      `<small>${esc(r.Title || '—')}</small>`,
      r.DOI ? `<a href="https://doi.org/${esc(r.DOI)}" target="_blank" rel="noopener">${esc(r.DOI)}</a>` : '—',
      `<span class="tag ${r.Decision === 'Included' ? 'risk-low' : (r.Decision === 'Excluded' ? 'risk-high' : '')}">${esc(r.Decision)}</span>`,
      `<small>${esc(r['Reason for exclusion (as in Fig. 1)'] || '—')}</small>`,
      `<small>${esc(r.Note || '—')}</small>`
    ]);

    container.innerHTML = `
      <p class="source" style="margin-bottom:8px">Showing ${filtered.length} of ${d.prisma.reports.length} records</p>
      ${table(['Report', 'Title', 'DOI', 'Decision', 'Exclusion Reason', 'Notes'], rows)}
    `;
  };

  // View: Methods
  function methods() {
    return `
      <h2>Review Methodology, Rules &amp; Conversions</h2>
      <p class="lede">Operational definitions, opioid conversion factors, prohibited rules, and database search strategies.</p>

      <h3>Operational Synthesis Rules (Additional file 5)</h3>
      ${table(
        ['Rule', 'Operational Definition'],
        d.rules.map(r => [`<strong>${esc(r.rule)}</strong>`, esc(r.definition)])
      )}

      <h3>Opioid Morphine Equivalent (MME) Register (Additional file 6)</h3>
      <p>Conversion factors to intravenous morphine milligram equivalents.</p>
      ${table(
        ['Opioid', 'Route', 'Source Unit', 'Factor (mg IV morphine)', 'Role / Certainty', 'Context / Reference Source'],
        d.conversions.factors.map(f => [
          `<strong>${esc(f.Opioid)}</strong>`,
          esc(f.Route),
          esc(f.Source_unit || f['Source unit']),
          `<strong>${esc(f.Factor || f['Factor (mg IV morphine per source unit)'])}</strong>`,
          `<span class="tag">${esc(f.Role || 'Standard')}</span> ${esc(f.Certainty || '')}`,
          `<small>${esc(f.Source || '')} (${esc(f.Context || '')})</small>`
        ])
      )}

      <h3>Prohibited Conversions (Additional file 6)</h3>
      ${table(
        ['Conversion Not Made', 'Methodological Reason'],
        d.conversions.prohibited.map(p => [
          `<strong>${esc(p.Conversion_not_made || p['Conversion not made'])}</strong>`,
          esc(p.Reason)
        ])
      )}

      <h3>Within-Report Contradictions &amp; Sensitivity Dispositions (Additional file 4)</h3>
      ${table(
        ['Report', 'Contradiction or Source Limitation', 'Disposition in Meta-Analyses'],
        d.contradictions.source_contradictions.map(c => [
          `<strong>${esc(c.Report)}</strong>`,
          `<small>${esc(c['Contradiction or source problem'] || c.Contradiction)}</small>`,
          `<small>${esc(c['Disposition and effect on the analyses'] || c.Disposition)}</small>`
        ])
      )}

      <h3>Database Search Strategies (Additional file 2)</h3>
      <div class="note">
        Searches conducted across PubMed, CENTRAL, Embase, and CINAHL on 21–23 July 2026 without date, language, or outcome restrictions.
      </div>
      <div class="details-box">
        <summary>View Full Search Query Strategies and Text</summary>
        ${d.search_strategies.text.map(p => `<p><small>${esc(p)}</small></p>`).join('')}
      </div>

      <h3>PRISMA 2020 Checklist (Additional file 1)</h3>
      <div class="details-box">
        <summary>View PRISMA 2020 Item Locations in Manuscript</summary>
        ${d.prisma_checklist.text.map(p => `<p><small>${esc(p)}</small></p>`).join('')}
      </div>
    `;
  }

  // View: Figures Gallery
  function figures() {
    return `
      <h2>Publication Figures Gallery</h2>
      <p class="lede">High-resolution figures from the review manuscript and additional files. Click any figure to open the interactive lightbox.</p>

      <div class="fig-cards">
        ${d.figures.map(fig => `
          <div class="fig-card">
            <button type="button" class="fig-thumb" onclick="window.openFigure('${esc(fig.id)}')">
              <img src="figures_png/${esc(fig.file)}" alt="${esc(fig.title)}" loading="lazy">
            </button>
            <figcaption>
              <strong>${esc(fig.title)}</strong>
              <span>${esc(fig.legend)}</span>
              <small><a href="figures_png/${esc(fig.file)}" download="${esc(fig.file)}">Download High-Res PNG</a></small>
            </figcaption>
          </div>
        `).join('')}
      </div>
    `;
  }

  // View: Manuscript
  function manuscript() {
    const txt = d.manuscript_text;
    return `
      <h2>Manuscript Reading Copy</h2>
      <p class="lede">Full text from <code>TEAS_EA_review_READING_COPY_with_figures.docx</code> prepared for supervisor review.</p>

      <div class="note" style="margin-bottom:24px">
        <strong>Document Status:</strong> Reading copy with figures placed in text. Submission targets BMC Anesthesiology (second choice: BMC Complementary Medicine and Therapies).
      </div>

      <div class="manuscript-section">
        <h3>Abstract</h3>
        ${(txt.Abstract || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Background</h3>
        ${(txt.Background || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Methods</h3>
        ${(txt.Methods || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Results</h3>
        ${(txt.Results || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Discussion</h3>
        ${(txt.Discussion || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Conclusions</h3>
        ${(txt.Conclusions || []).map(p => `<p>${esc(p)}</p>`).join('')}

        <h3>Declarations</h3>
        ${(txt.Declarations || []).map(p => `<p>${esc(p)}</p>`).join('')}
      </div>
    `;
  }

  // View: Downloads
  function downloads() {
    return `
      <h2>Download Center</h2>
      <p class="lede">Download all 11 Additional files, 5 high-resolution figures, and the Reading Copy manuscript docx.</p>

      <div class="filter-bar">
        <input type="search" id="dl-search" placeholder="Filter download files..." oninput="window.filterDownloads()">
        <div class="filter-group">
          <label for="dl-cat"><strong>Category:</strong></label>
          <select id="dl-cat" onchange="window.filterDownloads()">
            <option value="all">All Files (${d.downloads.length})</option>
            <option value="Additional Files">Additional Files (11)</option>
            <option value="Figures (High-res PNG)">Figures (5)</option>
            <option value="Manuscript">Manuscript DOCX (1)</option>
          </select>
        </div>
      </div>

      <div id="dl-cards-container" class="fig-cards">
        <!-- Rendered by window.filterDownloads() -->
      </div>
    `;
  }

  window.filterDownloads = function () {
    const q = ($('dl-search')?.value || '').toLowerCase();
    const cat = $('dl-cat')?.value || 'all';
    const container = $('dl-cards-container');
    if (!container) return;

    const filtered = d.downloads.filter(item => {
      if (cat !== 'all' && item.category !== cat) return false;
      if (q) {
        const str = `${item.name} ${item.label} ${item.category}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    container.innerHTML = filtered.map(item => `
      <div class="fig-card">
        <div style="font-size:24px; color:var(--accent); margin-bottom:4px;">
          ${item.name.endsWith('.xlsx') ? '📊' : (item.name.endsWith('.docx') ? '📄' : (item.name.endsWith('.zip') ? '📦' : '🖼️'))}
        </div>
        <figcaption>
          <strong>${esc(item.label)}</strong>
          <span>Category: ${esc(item.category)}</span>
          <small>Size: ${(item.size / 1024).toFixed(1)} KB · SHA-256: <code>${esc(item.sha256.slice(0, 12))}...</code></small>
          <div style="margin-top:8px">
            <a href="${esc(item.relative_path)}" download="${esc(item.name)}" class="text-button" style="text-decoration:none; font-weight:600;">Download ${esc(item.name)}</a>
          </div>
        </figcaption>
      </div>
    `).join('');
  };

  // Router & Navigation
  const views = {
    overview,
    results,
    e1e2,
    qor,
    studies,
    coverage,
    risk,
    evidence,
    prisma,
    methods,
    figures,
    manuscript,
    downloads
  };

  function renderView(id) {
    if (!views[id]) id = 'overview';
    const content = $('content');
    if (content) {
      content.innerHTML = views[id]();
    }

    // Update active nav links
    document.querySelectorAll('.nav a[data-view]').forEach(a => {
      const active = a.dataset.view === id;
      a.classList.toggle('active', active);
      if (active) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });

    // Run view-specific post-render initializers
    if (id === 'results') window.filterResultsTable();
    if (id === 'studies') window.filterStudiesTable();
    if (id === 'risk') { window.filterRobTable(); window.filterSigTable(); }
    if (id === 'prisma') window.filterPrismaTable();
    if (id === 'downloads') window.filterDownloads();

    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function handleHash() {
    const raw = location.hash.replace(/^#/, '');
    const [view] = raw.split('?');
    renderView(view || 'overview');
  }

  window.addEventListener('hashchange', handleHash);

  // Setup Figure Dialog close handler
  document.addEventListener('DOMContentLoaded', () => {
    const dialog = $('figure-dialog');
    const closeBtn = $('close-figure');
    if (dialog && closeBtn) {
      closeBtn.addEventListener('click', () => dialog.close());
      dialog.addEventListener('click', e => {
        if (e.target === dialog) dialog.close();
      });
    }

    const studyDialog = $('study-dialog');
    if (studyDialog) {
      studyDialog.addEventListener('click', e => {
        if (e.target === studyDialog) studyDialog.close();
      });
    }

    handleHash();
  });

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    handleHash();
  }

})();
