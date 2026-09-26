(() => {
    'use strict';
    
    // Mount point: called by current_review_ui.js when "studies" tab is clicked
    window.renderRichExplorer = function(containerId) {
        const d = window.CURRENT_REVIEW;
        const graph = window.EVIDENCE_GRAPH;
        const $ = id => document.getElementById(id);
        const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

        // Contribution matrix: outcome family from the model ID, state from the canonical role.
        const COLS = { opioid: 'Opioid 0–24 h', pain: 'Pain', ponv: 'PONV', qor: 'QoR', gi: 'GI recovery' };
        const STATE = { e1: 'E1 primary body (principal/supportive)', e2: 'E2 post-hoc main body only', main: 'main (non-sensitivity) body', sens: 'sensitivity/diagnostic models only' };
        const TIER = { sens: 1, main: 2, e2: 3, e1: 4 };
        const classify = (mid, m) => {
            const role = m?.role || '', main = ['PRINCIPAL', 'SUPPORTIVE', 'ADDITIONAL'].includes(role);
            if (mid.startsWith('E2_')) return ['opioid', role.includes('(main)') ? 'e2' : 'sens'];
            if (mid.startsWith('opioid24_')) return ['opioid', role === 'PRINCIPAL' || role === 'SUPPORTIVE' ? 'e1' : 'sens'];
            if (mid.startsWith('QOR')) return ['qor', main ? 'main' : 'sens'];
            if (mid.startsWith('pain')) return ['pain', main ? 'main' : 'sens'];
            if (/^(ponv|nausea|vomiting|persistent_nausea)/.test(mid)) return ['ponv', main ? 'main' : 'sens'];
            if (/^(flatus|defecation|bowelsounds)/.test(mid)) return ['gi', main ? 'main' : 'sens'];
            return null;
        };
        const ROLE_RANK = { PRINCIPAL: 0, SUPPORTIVE: 1, ADDITIONAL: 2 };

        let state = {
            search: '',
            modality: 'all',
            comparator: 'all'
        };

        const hashParts = window.location.hash.split('?');
        if (hashParts.length > 1) {
            const qp = new URLSearchParams(hashParts[1]);
            if (qp.has('search')) state.search = qp.get('search');
            if (qp.has('modality')) state.modality = qp.get('modality');
            if (qp.has('comparator')) state.comparator = qp.get('comparator');
        }

        const updateUrl = () => {
            const params = new URLSearchParams();
            if (state.search) params.set('search', state.search);
            if (state.modality !== 'all') params.set('modality', state.modality);
            if (state.comparator !== 'all') params.set('comparator', state.comparator);
            const str = params.toString();
            const newHash = window.location.hash.split('?')[0] + (str ? '?' + str : '');
            window.history.replaceState(null, '', newHash);
        };

        const renderControls = () => `
            <style>
                .explorer-toolbar {
                    display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;
                    background: var(--card);
                    padding: 1.25rem 1.5rem;
                    border-radius: 12px;
                    border: 1px solid var(--line);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    margin-bottom: 1.5rem;
                }
                .explorer-toolbar > div {
                    display: flex; flex-direction: column;
                }
                .explorer-toolbar label {
                    margin: 0 0 6px 4px; font-size: 13px; font-weight: 500; color: var(--muted);
                }
                .explorer-toolbar input, .explorer-toolbar select {
                    background: var(--bg);
                    border: 1px solid #3c506b;
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    font-size: 14px;
                    transition: border-color 0.2s, box-shadow 0.2s;
                }
                .explorer-toolbar input:focus, .explorer-toolbar select:focus {
                    border-color: var(--accent);
                    box-shadow: 0 0 0 3px rgba(94, 234, 212, 0.15);
                    outline: none;
                }
                .study-row {
                    transition: background-color 0.2s, transform 0.2s ease-out;
                }
                .study-row:hover {
                    background-color: rgba(255, 255, 255, 0.03);
                    transform: translateX(4px);
                }
                .matrix-cell {
                    display: inline-flex; align-items: center; justify-content: center;
                    width: 26px; height: 20px; border-radius: 10px; font-size: 10px; font-weight: 700; color: #0b1220;
                }
                .matrix-cell.e1 { background: var(--accent); }
                .matrix-cell.e2 { background: #fbbf24; }
                .matrix-cell.main { background: #93c5fd; width: 14px; height: 14px; }
                .matrix-cell.sens { border: 2px solid #93c5fd; width: 14px; height: 14px; }
                .matrix-cell.none { color: var(--muted); font-weight: 400; font-size: 14px; }
                .matrix-legend { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; font-size: 13px; color: var(--muted); margin: 0 0 8px; }
                .matrix-legend span { display: inline-flex; align-items: center; gap: 6px; }
                .study-open { font-weight: 700; color: var(--ink); max-width: none; }
                /* Sleek Side Drawer */
                #study-drawer {
                    margin-right: 0;
                    margin-left: auto;
                    margin-top: 0;
                    margin-bottom: 0;
                    height: 100vh;
                    max-height: 100vh;
                    width: 800px;
                    max-width: 95vw;
                    border-radius: 16px 0 0 16px;
                    background: #0d1624;
                    box-shadow: -10px 0 30px rgba(0,0,0,0.5);
                    border: 1px solid var(--line);
                    border-right: none;
                }
                #study-drawer::backdrop {
                    background: rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(3px);
                }
                /* Drawer Animations */
                #study-drawer {
                    animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); }
                    to { transform: translateX(0); }
                }
            </style>
            <h2>Study Explorer &amp; Contribution Matrix</h2>
            <p class="lede">Explore all 70 reports, their characteristics, and their contributions to the meta-analytical models.</p>
            
            <div class="explorer-toolbar">
                <div style="flex: 1; min-width: 250px;">
                    <label for="explorer-search">Search studies</label>
                    <input id="explorer-search" type="search" placeholder="Study name, year, etc." value="${esc(state.search)}">
                </div>
                <div>
                    <label for="explorer-modality">Modality</label>
                    <select id="explorer-modality">
                        <option value="all" ${state.modality === 'all' ? 'selected' : ''}>All Modalities</option>
                        <option value="TEAS" ${state.modality === 'TEAS' ? 'selected' : ''}>TEAS</option>
                        <option value="EA" ${state.modality === 'EA' ? 'selected' : ''}>Needle EA</option>
                        <option value="Unclear" ${state.modality === 'Unclear' ? 'selected' : ''}>Unclear modality</option>
                    </select>
                </div>
                <div>
                    <label for="explorer-comparator">Comparator</label>
                    <select id="explorer-comparator">
                        <option value="all" ${state.comparator === 'all' ? 'selected' : ''}>All Comparators</option>
                        <option value="Sham" ${state.comparator === 'Sham' ? 'selected' : ''}>Sham-controlled</option>
                        <option value="Usual" ${state.comparator === 'Usual' ? 'selected' : ''}>Usual care</option>
                        <option value="Active" ${state.comparator === 'Active' ? 'selected' : ''}>Active control</option>
                        <option value="Unclear" ${state.comparator === 'Unclear' ? 'selected' : ''}>Unclear control</option>
                    </select>
                </div>
            </div>
            
            <div class="matrix-legend" aria-label="Contribution legend">
                <span><span class="matrix-cell e1">E1</span> E1 primary opioid body</span>
                <span><span class="matrix-cell e2">E2</span> E2 post-hoc body only</span>
                <span><span class="matrix-cell main"></span> Main body</span>
                <span><span class="matrix-cell sens"></span> Sensitivity/diagnostic only</span>
                <span><span class="matrix-cell none">–</span> No model contribution (may still be reported, held or ineligible)</span>
            </div>
            <p class="source" style="margin:0 0 4px"><span id="explorer-count" aria-live="polite"></span> · Hover a cell for the exact models. Pain includes the 6–24 h interval sensitivity; PONV includes nausea/vomiting and 48 h windows.</p>
            <div id="explorer-table-container"></div>
            
            <dialog id="study-drawer">
                <div id="study-drawer-content"></div>
            </dialog>
        `;

        const renderTable = () => {
            const getContrasts = (s, models) => {
                let contrasts = new Set();
                let modalities = new Set();
                
                // Base from report-level string
                const compLower = s.comparator.toLowerCase();
                if (compLower.includes('sham')) contrasts.add('Sham');
                if (compLower.includes('usual')) contrasts.add('Usual');
                if (compLower.includes('active')) contrasts.add('Active');
                
                if (s.modality === 'TEAS') modalities.add('TEAS');
                if (s.modality === 'EA') modalities.add('EA');
                if (s.modality === 'UNCLEAR') modalities.add('Unclear');

                // Add from models and arm-level inputs to catch multi-arm trials
                for (const inp of graph.studies[s.report_id]?.inputs || []) {
                    const cls = (inp.comparator_class || inp.comparator || '').toLowerCase();
                    if (cls.includes('sham')) contrasts.add('Sham');
                    if (cls.includes('usual')) contrasts.add('Usual');
                    if (cls.includes('active')) contrasts.add('Active');
                }
                for (const mid of models) {
                    if (mid.includes('_sham') || mid.includes('SHAM')) contrasts.add('Sham');
                    if (mid.includes('_usual') || mid.includes('USUAL')) contrasts.add('Usual');
                    if (mid.includes('_active')) contrasts.add('Active');
                    if (mid.includes('TEAS_')) modalities.add('TEAS');
                    if (mid.includes('EA_')) modalities.add('EA');
                }
                
                if (contrasts.size === 0) contrasts.add('Unclear');
                if (modalities.size === 0) modalities.add('Unclear');
                return { contrasts: Array.from(contrasts), modalities: Array.from(modalities) };
            };

            let filtered = d.studies.filter(s => {
                if (state.search && !s.report_id.toLowerCase().includes(state.search.toLowerCase()) && 
                    !(graph.studies[s.report_id]?.background?.citation || '').toLowerCase().includes(state.search.toLowerCase()) &&
                    !(graph.studies[s.report_id]?.background?.surgery_procedure || '').toLowerCase().includes(state.search.toLowerCase())) return false;
                
                const models = graph.studies[s.report_id]?.models || [];
                const traits = getContrasts(s, models);
                
                if (state.modality !== 'all' && !traits.modalities.includes(state.modality)) return false;
                if (state.comparator !== 'all' && !traits.contrasts.includes(state.comparator)) return false;
                
                return true;
            });
            
            const rows = filtered.map(s => {
                const bg = graph.studies[s.report_id]?.background || {};
                const models = graph.studies[s.report_id]?.models || [];
                const inputs = graph.studies[s.report_id]?.inputs || [];
                const numFigs = (window.ARTICLE_FIGURES?.[s.report_id] || []).length;
                
                // With a comparator selected, show the analysed n of that contrast, taken from the
                // highest-ranked model input (principal > supportive > additional > sensitivity).
                let displayN = esc(s.analyzed_n || '—');
                if (state.comparator !== 'all') {
                    const compInput = inputs
                        .filter(inp => inp.n_i !== undefined && inp.n_i !== '' && (inp.comparator_class || inp.comparator || '').toLowerCase().includes(state.comparator.toLowerCase()))
                        .sort((a, b) => (ROLE_RANK[graph.models[a.model_id]?.canonical?.role] ?? 3) - (ROLE_RANK[graph.models[b.model_id]?.canonical?.role] ?? 3))[0];
                    if (compInput) displayN = `${Number(compInput.n_i) + Number(compInput.n_c)}<br><small>${esc(compInput.model_id)}</small>`;
                }
                
                // Contribution cells: highest-ranked role per outcome family; tooltip lists every model.
                const cells = {};
                for (const mid of models) {
                    const c = classify(mid, graph.models[mid]?.canonical);
                    if (!c) continue;
                    const cell = cells[c[0]] ||= { tier: 'sens', models: [] };
                    cell.models.push(mid);
                    if (TIER[c[1]] > TIER[cell.tier]) cell.tier = c[1];
                }
                const dotHtml = (key) => {
                    const cell = cells[key];
                    if (!cell) return `<span class="matrix-cell none" role="img" aria-label="${esc(COLS[key])}: no current model contribution" title="No contribution to any current model. The outcome may still be reported, held or ineligible.">–</span>`;
                    const label = `${COLS[key]}: ${STATE[cell.tier]}. Models: ${cell.models.join(', ')}`;
                    return `<span class="matrix-cell ${cell.tier}" role="img" aria-label="${esc(label)}" title="${esc(label)}">${cell.tier === 'e1' ? 'E1' : cell.tier === 'e2' ? 'E2' : ''}</span>`;
                };
                
                return `
                    <tr style="cursor:pointer" class="study-row" data-id="${esc(s.report_id)}">
                        <td><button type="button" class="text-button study-open" data-id="${esc(s.report_id)}" aria-haspopup="dialog">${esc(s.report_id)}</button><br><small>${esc(s.trial_id)}</small></td>
                        <td><span class="tag">${esc(s.modality)}</span></td>
                        <td><span class="tag">${esc(s.comparator)}</span></td>
                        <td>${esc(bg.surgery_procedure || 'Not verified')}</td>
                        <td style="text-align:right">${s.randomized_n_report || '—'}</td>
                        <td style="text-align:right">${displayN}</td>
                        ${Object.keys(COLS).map(k => `<td style="text-align:center">${dotHtml(k)}</td>`).join('')}
                        <td style="text-align:center">${numFigs > 0 ? `<span class="badge" style="background:var(--accent); color:white;">${numFigs}</span>` : '<span style="color:var(--text-muted)">-</span>'}</td>
                    </tr>
                `;
            }).join('');
            
            $('explorer-table-container').innerHTML = `
                <div class="table-scroll">
                    <table>
                        <thead>
                            <tr>
                                <th>Study</th>
                                <th>Modality</th>
                                <th>Comparator</th>
                                <th>Surgery</th>
                                <th style="text-align:right">N(rand)</th>
                                <th style="text-align:right">N(anal)</th>
                                ${Object.values(COLS).map(c => `<th style="text-align:center">${c}</th>`).join('')}
                                <th style="text-align:center">Figures</th>
                            </tr>
                        </thead>
                        <tbody>${rows || '<tr><td colspan="12" style="text-align:center; padding:2rem;">No studies found matching criteria.</td></tr>'}</tbody>
                    </table>
                </div>
            `;
            $('explorer-count').textContent = `${filtered.length} of ${d.studies.length} reports`;
            
            document.querySelectorAll('.study-row').forEach(row => {
                row.addEventListener('click', () => openDrawer(row.dataset.id));
            });
        };

        const openDrawer = (id) => {
            const s = d.studies.find(x => x.report_id === id);
            if (!s) return;
            const bg = graph.studies[id]?.background || {};
            const models = graph.studies[id]?.models || [];
            const results = graph.studies[id]?.results || [];
            
            const stricta = bg.stricta || {};
            
            let html = `
                <div style="position:sticky; top:0; background:#0d1624; padding-bottom:16px; margin-bottom:16px; border-bottom:1px solid var(--line); z-index:10;">
                    <button type="button" id="close-drawer" aria-label="Close" style="float:right; background:rgba(255,255,255,0.05); border:1px solid var(--line); color:var(--ink); cursor:pointer; font-size:20px; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; transition:background 0.2s;">&times;</button>
                    <h2 style="margin:0 0 4px 0">${esc(s.report_id)}</h2>
                    <p class="source" style="margin:0;">${esc(bg.citation || '')}</p>
                </div>
                
                <div style="padding-right:8px;">
                    <div style="display:flex; gap:8px; margin-bottom:24px;">
                        <span class="tag">${esc(s.modality)}</span>
                        <span class="tag" style="background:#133833; color:#99f6e4;">${esc(s.comparator)}</span>
                    </div>
                    
                    <h3>Intervention details (STRICTA)</h3>
                    ${stricta.status === 'Verified'
                        ? `<p class="note"><span class="tag risk-low">Partly source-verified ${esc(stricta.verification_date)}</span> Fields shown as “Unverified” were not checked. Source excerpt: “${esc(stricta.source_excerpt)}”</p>`
                        : `<p class="note"><span class="tag risk-high">Not source-verified</span> Imported from the historical dashboard. Check the PDF before using these details for subgrouping or characteristics text.</p>`}
                    <div class="table-scroll">
                        <table>
                            <tbody>
                                <tr><th>Acupoints</th><td>${esc(stricta.acupoints || '—')}</td></tr>
                                <tr><th>Frequency</th><td>${esc(stricta.frequency_raw || stricta.frequency_category || '—')}</td></tr>
                                <tr><th>Intensity</th><td>${esc(stricta.intensity || stricta.intensity_category || '—')}</td></tr>
                                <tr><th>Timing</th><td>${esc(stricta.timing_raw || stricta.timing_category || '—')}</td></tr>
                                <tr><th>Duration</th><td>${esc(stricta.duration_raw || stricta.duration_category || '—')}</td></tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <h3>Model Contributions</h3>
                    ${models.length ? `<div class="table-scroll"><table><thead><tr><th>Model</th><th>Role</th><th>k</th></tr></thead><tbody>${models.map(mid => { const m = graph.models[mid]?.canonical || {}; return `<tr><td><button type="button" class="text-button model-link" data-model="${esc(mid)}">${esc(mid)} &rarr;</button></td><td>${esc(m.role || '—')}</td><td>${esc(m.k ?? '—')}</td></tr>`; }).join('')}</tbody></table></div>` : '<p>No contribution to any current model. This is not an efficacy claim; the report may still be reported-not-poolable, held or ineligible for these outcomes.</p>'}

                    <h3>Result-specific Risk of Bias (v38 and QoR addenda)</h3>
                    ${results.length ? `<div class="table-scroll">
                        <table>
                            <thead>
                                <tr><th>Result</th><th>Outcome / window</th><th>Overall</th></tr>
                            </thead>
                            <tbody>
                                ${results.map(rid => {
                                    const rr = graph.results[rid]?.rob;
                                    return rr ? `<tr><td>${esc(rid)}</td><td>${esc(rr.outcome)}<br><small>${esc(rr.window)}</small></td><td><span class="tag ${rr.overall==='High'?'risk-high':rr.overall==='Low'?'risk-low':''}">${esc(rr.overall)}</span></td></tr>`
                                              : `<tr><td>${esc(rid)}</td><td colspan="2"><small>No result-specific assessment recorded (used in: ${esc((graph.results[rid]?.models || []).join(', ') || '—')})</small></td></tr>`;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>` : '<p>No linked results.</p>'}
                    
                    ${(window.ARTICLE_FIGURES?.[s.report_id] || []).length ? `
                    <h3>Article figures (${(window.ARTICLE_FIGURES?.[s.report_id] || []).length})</h3>
                    <div class="figure-grid">${(window.ARTICLE_FIGURES?.[s.report_id] || []).map(f=>`<figure><button class="figure-open" data-src="${esc(f.src)}" data-caption="${esc(s.report_id+' · '+f.caption)}"><img src="${esc(f.src)}" loading="lazy" alt="${esc(s.report_id+' '+f.caption)}"></button><figcaption>${esc(f.caption)}</figcaption></figure>`).join('')}</div>
                    ` : ''}
                    
                    <p class="source" style="margin-top:32px;">Source document: ${esc(s.source_pdf)}</p>
                </div>
            `;
            
            $('study-drawer-content').innerHTML = html;
            const drawer = $('study-drawer');
            drawer.showModal();
            
            $('close-drawer').addEventListener('click', () => drawer.close());
            // Model links (data-model) are routed by current_review_ui.js to core, QoR or E2 displays.
        };

        const container = $(containerId);
        container.innerHTML = renderControls();
        renderTable();
        
        $('explorer-search').addEventListener('input', e => { state.search = e.target.value; updateUrl(); renderTable(); });
        $('explorer-modality').addEventListener('change', e => { state.modality = e.target.value; updateUrl(); renderTable(); });
        $('explorer-comparator').addEventListener('change', e => { state.comparator = e.target.value; updateUrl(); renderTable(); });
    };
})();
