(() => {
    'use strict';
    
    // Mount point: called by current_review_ui.js when "studies" tab is clicked
    window.renderRichExplorer = function(containerId) {
        const d = window.CURRENT_REVIEW;
        const graph = window.EVIDENCE_GRAPH;
        const $ = id => document.getElementById(id);
        const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
        
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
                .matrix-dot {
                    width: 12px; height: 12px; border-radius: 50%; margin: 0 auto;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .matrix-dot.active {
                    background: var(--accent);
                    box-shadow: 0 0 8px rgba(94, 234, 212, 0.4);
                }
                .matrix-dot.inactive {
                    background: var(--line);
                }
                .study-row:hover .matrix-dot.active {
                    transform: scale(1.2);
                    box-shadow: 0 0 12px rgba(94, 234, 212, 0.6);
                }
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

                // Add from models to catch multi-arm
                for (const mid of models) {
                    if (mid.includes('_sham') || mid.includes('SHAM')) contrasts.add('Sham');
                    if (mid.includes('_usual') || mid.includes('USUAL')) contrasts.add('Usual');
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
                
                // Determine N(anal) based on selected contrast, else fallback
                let displayN = s.analyzed_n || '—';
                if (state.comparator !== 'all' && inputs.length > 0) {
                    // Find an input matching the comparator
                    const compInput = inputs.find(inp => {
                        const mStr = inp.model_id.toLowerCase();
                        return (state.comparator === 'Sham' && mStr.includes('sham')) ||
                               (state.comparator === 'Usual' && mStr.includes('usual'));
                    });
                    if (compInput) {
                        displayN = `${Number(compInput.n_i) + Number(compInput.n_c)} (${state.comparator})`;
                    }
                }
                
                // Evaluate contribution dots using exact roles
                let opioid24 = 'none', pain24 = 'none', ponv = 'none', recovery = 'none';
                
                for (const mid of models) {
                    const mObj = graph.models[mid]?.canonical;
                    if (!mObj) continue;
                    
                    const midLower = mid.toLowerCase();
                    const isE1 = mObj.role === 'PRINCIPAL' || mObj.role === 'SUPPORTIVE';
                    const isE2 = mObj.role?.includes('E2');
                    
                    if (midLower.includes('opioid24') && !midLower.includes('opioid24_pacu')) {
                        if (isE1) opioid24 = 'E1';
                        else if (isE2 && opioid24 !== 'E1') opioid24 = 'E2';
                    }
                    
                    if (midLower.includes('pain24')) {
                        if (isE1) pain24 = 'E1';
                    }
                    
                    if (midLower.includes('ponv') || midLower.includes('nausea') || midLower.includes('vomiting')) {
                        if (isE1) ponv = 'E1';
                    }
                    
                    if (midLower.includes('qor') || midLower.includes('flatus') || midLower.includes('defecation')) {
                        if (midLower.includes('qor')) recovery = 'QoR';
                        else if (recovery === 'none') recovery = 'GI';
                    }
                }
                
                const dotHtml = (type) => {
                    if (type === 'none') return `<div class="matrix-dot inactive" title="No contribution"></div>`;
                    let color = 'var(--accent)';
                    if (type === 'E2') color = '#fbbf24'; // Warning color for E2
                    if (type === 'QoR') color = '#a78bfa'; // Purple for QoR
                    if (type === 'GI') color = '#60a5fa'; // Blue for GI
                    return `<div class="matrix-dot active" style="background:${color}" title="Contributes (${type})"></div>`;
                };
                
                return `
                    <tr style="cursor:pointer" class="study-row" data-id="${esc(s.report_id)}" title="Click to open study details and figures">
                        <td><strong>${esc(s.report_id)}</strong><br><small style="color:var(--text-secondary)">${esc(s.year)}</small></td>
                        <td><span class="tag">${esc(s.modality)}</span></td>
                        <td><span class="tag">${esc(s.comparator)}</span></td>
                        <td>${esc(bg.surgery_procedure || s.notes || '—')}</td>
                        <td style="text-align:right">${s.randomized_n_report || '—'}</td>
                        <td style="text-align:right">${esc(displayN)}</td>
                        <td style="text-align:center">${dotHtml(opioid24)}</td>
                        <td style="text-align:center">${dotHtml(pain24)}</td>
                        <td style="text-align:center">${dotHtml(ponv)}</td>
                        <td style="text-align:center">${dotHtml(recovery)}</td>
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
                                <th style="text-align:center" title="Opioid 24h">Opioid</th>
                                <th style="text-align:center" title="Pain 24h (Rest/Movement)">Pain</th>
                                <th style="text-align:center" title="Nausea/Vomiting">PONV</th>
                                <th style="text-align:center" title="QoR or GI Recovery">Recovery</th>
                                <th style="text-align:center">Figures</th>
                            </tr>
                        </thead>
                        <tbody>${rows || '<tr><td colspan="11" style="text-align:center; padding:2rem;">No studies found matching criteria.</td></tr>'}</tbody>
                    </table>
                </div>
            `;
            
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
                    ${models.length ? `<ul style="list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:8px;">${models.map(m => `<li><button class="text-button model-link" data-model="${esc(m)}" style="background:rgba(94,234,212,0.1); padding:6px 12px; border-radius:6px; font-weight:500;">${esc(m)} &rarr;</button></li>`).join('')}</ul>` : '<p>No quantitative contributions.</p>'}
                    
                    <h3>Result-specific Risk of Bias (v38)</h3>
                    <div class="table-scroll">
                        <table>
                            <thead>
                                <tr><th>Result</th><th>Outcome</th><th>Overall</th></tr>
                            </thead>
                            <tbody>
                                ${results.map(rid => {
                                    const rr = graph.results[rid]?.rob;
                                    return rr ? `<tr><td>${esc(rid)}</td><td>${esc(rr.outcome)}</td><td><span class="tag ${rr.overall==='High'?'risk-high':rr.overall==='Low'?'risk-low':''}">${esc(rr.overall)}</span></td></tr>` : '';
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                    
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
            
            // Handle model links inside the drawer
            drawer.querySelectorAll('.model-link').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    drawer.close();
                    // trigger global routing (from current_review_ui.js)
                    const mid = e.target.dataset.model;
                    document.querySelector(`[data-view="results"]`).click();
                    setTimeout(() => {
                        const sel = document.getElementById('model-select');
                        if(sel) {
                            sel.value = mid;
                            sel.dispatchEvent(new Event('change'));
                        }
                    }, 50);
                });
            });
        };

        const container = $(containerId);
        container.innerHTML = renderControls();
        renderTable();
        
        $('explorer-search').addEventListener('input', e => { state.search = e.target.value; updateUrl(); renderTable(); });
        $('explorer-modality').addEventListener('change', e => { state.modality = e.target.value; updateUrl(); renderTable(); });
        $('explorer-comparator').addEventListener('change', e => { state.comparator = e.target.value; updateUrl(); renderTable(); });
    };
})();
