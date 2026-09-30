(() => {
    'use strict';
    // Study Explorer: characteristics, filters, contribution matrix and study drawer.
    // Everything is read from the canonical payload (CURRENT_REVIEW) and the evidence graph; nothing is re-fitted,
    // and missing characteristics are shown with their status, never filled.
    const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const num = (x, n = 2) => x === null || x === undefined || x === '' || isNaN(+x) ? '—' : Number(x).toFixed(n);
    const term = (label, key) => window.reviewTerm ? window.reviewTerm(label, key) : esc(label);
    // Model references use the main UI's single label mapping (label + model ID); plain ID if it is unavailable.
    const modelName = mid => window.reviewModelName ? window.reviewModelName(mid) : `<button type="button" class="text-button model-link" data-model="${esc(mid)}">${esc(mid)}</button>`;
    const Z95 = 1.95996398454;

    // Detailed contribution matrix: outcome families and the model-ID rule that assigns a model to each.
    const FAMILIES = [
        ['Opioid', 'op_e1', 'E1 0–24 h', m => m.startsWith('opioid24_')],
        ['Opioid', 'op_e2', 'E2 0–24 h', m => m.startsWith('E2_')],
        ['Opioid', 'op_48', '48 h', m => m.startsWith('opioid48_')],
        ['Opioid', 'op_72', '72 h', m => m.startsWith('opioid72_')],
        ['Opioid', 'op_other', 'Rescue / other', m => /^(pethidine24_|tramadol24_|opioid_partial_)/.test(m)],
        ['Opioid', 'op_intra', 'Intraoperative', m => m.startsWith('intraop_')],
        ['Pain', 'pain_rest', 'Rest ~24 h', m => m.startsWith('pain24_rest_')],
        ['Pain', 'pain_move', 'Movement ~24 h', m => m.startsWith('pain24_movement_')],
        ['Pain', 'pain_other', 'Other / sensitivity', m => m.startsWith('pain') && !/^pain24_(rest|movement)_/.test(m)],
        ['PONV', 'ponv', 'Composite', m => m.startsWith('ponv')],
        ['PONV', 'nausea', 'Nausea', m => m.startsWith('nausea')],
        ['PONV', 'vomit', 'Vomiting', m => m.startsWith('vomiting')],
        ['PONV', 'pnausea', 'Persistent nausea', m => m.startsWith('persistent_nausea')],
        ['GI', 'flatus', 'Flatus', m => m.startsWith('flatus')],
        ['GI', 'bowel', 'Bowel sounds', m => m.startsWith('bowelsounds')],
        ['GI', 'defec', 'Defecation', m => m.startsWith('defecation')],
        ['Recovery', 'qor15', 'QoR-15 ~24 h', (m, later) => m.startsWith('QOR15') && !later.has(m)],
        ['Recovery', 'qor40', 'QoR-40 ~24 h', (m, later) => m.startsWith('QOR40') && !later.has(m)],
        ['Recovery', 'qorlater', 'Later QoR', (m, later) => later.has(m)],
        ['Other', 'harms', 'Harms reported', null],
        ['Other', 'satis', 'Satisfaction / acceptability', null],
    ];
    // Compact view: five columns, each the highest-ranked state across its detailed families.
    const COMPACT = { opioid: ['Opioid 0–24 h', ['op_e1', 'op_e2']], pain: ['Pain', ['pain_rest', 'pain_move', 'pain_other']],
        ponv: ['PONV', ['ponv', 'nausea', 'vomit', 'pnausea']], qor: ['QoR', ['qor15', 'qor40', 'qorlater']], gi: ['GI recovery', ['flatus', 'bowel', 'defec']] };
    // Register keywords per compact family, used only to list extracted results that are in no model.
    const FAMILY_RX = { opioid: /opioid|morphine|fentanyl|sufentanil|tramadol|pethidine|remifentanil|hydromorphone|oxycodone|PCA|analges/i,
        pain: /pain|VAS|NRS/i, ponv: /nausea|vomit|PONV/i, qor: /QoR|quality of recovery/i, gi: /flatus|bowel|defecat|gastrointestinal/i };
    const TIER = { sens: 1, reported: 1, main: 2, e2: 3, e1: 4 };
    const STATE = { e1: 'E1 primary body (principal/supportive)', e2: 'E2 post-hoc main body only', main: 'main (non-sensitivity) body',
        sens: 'sensitivity/diagnostic models only', reported: 'reported descriptively (not pooled)' };
    const STATUSES = [['e1', 'E1 contributor'], ['e2', 'E2 contributor'], ['e2only', 'E2 only'], ['e1e2', 'E1 + E2'], ['principal', 'Principal body'],
        ['supportive', 'Supportive body'], ['additional', 'Additional outcome body'], ['sensitivity', 'Sensitivity analysis'], ['diagnostic', 'Diagnostic'],
        ['held', 'Held result(s)'], ['nomodel', 'No current quantitative model']];
    const ROB = [['high', 'Has a High-risk result'], ['sc', 'Has a Some-concerns result'], ['low', 'All assessed results Low'], ['none', 'No result-specific assessment']];
    const SIZE = [['lt50', '< 50', n => n < 50], ['50', '50–99', n => n >= 50 && n < 100], ['100', '100–199', n => n >= 100 && n < 200],
        ['200', '200–499', n => n >= 200 && n < 500], ['500', '≥ 500', n => n >= 500]];
    const YEARS = [['–2005', 0, 2005], ['2006–10', 2006, 2010], ['2011–15', 2011, 2015], ['2016–20', 2016, 2020], ['2021–', 2021, 9999]];
    // Characteristics columns (harmonised; each shown with its verification status).
    const CHARS = [['year', 'Year'], ['trial_family', 'Trial family'], ['country', 'Country'], ['surgical_category', 'Surgical category'], ['procedure', 'Procedure'],
        ['randomized_n', 'N randomised'], ['analysed_n', 'N analysed'], ['age', 'Age'], ['female', 'Female'], ['bmi', 'BMI'], ['asa', 'ASA'],
        ['anaesthesia', 'Anaesthesia'], ['postoperative_analgesia', 'Postoperative analgesia'], ['pca_regimen', 'PCA regimen'], ['rescue_analgesia', 'Rescue analgesia'],
        ['acupoints', 'Acupoints'], ['frequency', 'Frequency'], ['intensity', 'Intensity'], ['timing', 'Timing'], ['sessions', 'Sessions'],
        ['session_duration', 'Session duration'], ['cumulative_duration', 'Cumulative duration'], ['intervention_arms', 'Intervention arms'], ['control_arms', 'Control / sham arms']];
    const DEFAULT_COLS = ['surgical_category', 'randomized_n', 'analysed_n'];
    // Verification status of each characteristic (the status strings of 14_CHARACTERISTICS/report_characteristics.csv,
    // set by code/build_characteristics.py): badge, colour class, plain-language label and what the status means.
    // Order = strongest to weakest provenance; the legend, badges and tooltips all read from this one table.
    const VS = {
        'Verified (registry)': ['V', 'vs-ok', 'Verified — registry',
            'Taken from the canonical v38 study registry, the adjudicated record of each report. The registry marks every field it could not confirm from the source as not verified; those never carry this badge. For randomised N the registry also stores the source page and a verbatim excerpt (shown in the study profile).'],
        'Verified (PDF quote)': ['PDF', 'vs-ok', 'Verified — PDF quotation',
            'Found in the primary report by the conservative PDF extraction step, which keeps a value only with its page number and the verbatim sentence it came from, and only when the whole paper gives one consistent answer.'],
        'Partly verified (source excerpt)': ['SX', 'vs-ok', 'Partly verified — source excerpt',
            'Checked against a dated source excerpt for this protocol item. Other parts of the same stimulation description may still be legacy values.'],
        'Canonical result register': ['REG', 'vs-ok', 'Canonical result register',
            'Arm descriptions copied from the adjudicated canonical results register (the same record the models use), not from a separate characteristics extraction.'],
        'Source-traced (extraction record)': ['TR', 'vs-mid', 'Source-traced',
            'Traced to a specific file and line of an earlier structured extraction record of the report. Not re-read against the PDF for this dashboard.'],
        'Verified (PDF quote, second reviewer)': ['PQ2', 'vs-ok', 'Verified — PDF quotation, second reviewer',
            'Extracted from the primary report with the page and a verbatim quotation (machine-checked against the report’s text on that page), then checked and confirmed by a second reviewer. The reviewer and date are in the value’s source.'],
        'Extracted (PDF quote, single extractor)': ['PQ', 'vs-mid', 'Extracted from PDF quotation — single extractor',
            'Extracted from the primary report by one extractor, with the page and a verbatim quotation. The quotation is machine-checked against the report’s text on that page, but the value has not been independently reviewed by a second extractor.'],
        'Legacy (v26, not re-verified)': ['L', 'vs-warn', 'Legacy extraction — not re-verified',
            'Inherited from the older v26 data workbook and not re-checked against the primary report. Check the report before using it for subgrouping or characteristics text.'],
        'Not verified': ['NV', 'vs-none', 'Not verified',
            'The registry records this field as not verified and no other checked source exists, so no value is shown.'],
        'Not reported in source': ['NR', 'vs-none', 'Not reported in source',
            'The full text was searched and the report does not state this item. This is a finding about the report, not a failed extraction, and it does not mean the item was absent in the trial.'],
        'Not extracted': ['NE', 'vs-none', 'Not extracted',
            'No structured extraction exists for this field. Nothing is inferred to fill the gap.'] };
    const REGIMEN_FIELDS = ['postoperative_analgesia', 'pca_regimen', 'rescue_analgesia', 'cumulative_duration'];
    // Baseline and protocol fields quoted from the PDFs (14_CHARACTERISTICS/baseline_protocol_extraction.csv); a registry value keeps priority.
    const BASELINE_FIELDS = ['age', 'female', 'bmi', 'asa', 'anaesthesia', 'acupoints', 'frequency', 'intensity', 'timing', 'sessions', 'session_duration'];
    const STRICTA_FIELDS = ['acupoints', 'frequency', 'intensity', 'timing', 'sessions', 'session_duration'];
    const EXTRA_FIELD_LABEL = { modality: 'Modality', comparator: 'Comparator (study label)', comparator_class: 'Comparator class', randomized_n_counted: 'N randomised (operational count)' };
    const PRESETS = [['All', {}], ['TEAS', { modality: 'TEAS' }], ['EA', { modality: 'EA' }], ['Sham controlled', { comparator: 'Sham' }], ['Usual care', { comparator: 'Usual' }],
        ['E1 contributors', { status: 'e1' }], ['E2 contributors', { status: 'e2' }], ['E2 only', { status: 'e2only' }], ['Pain evidence', { family: 'pain' }],
        ['PONV evidence', { family: 'ponv' }], ['GI evidence', { family: 'gi' }], ['QoR evidence', { family: 'qor' }], ['High RoB', { rob: 'high' }], ['Held / source issue', { status: 'held' }]];
    const FILTER_KEYS = ['search', 'modality', 'comparator', 'surgery', 'country', 'ymin', 'ymax', 'rob', 'size', 'family', 'status'];

    // ---- Per-report index, built once per payload (search and filters never rebuild the graph).
    let INDEX = null;
    function buildIndex(d, graph) {
        const later = new Set((d.qor_later_models || []).map(m => m.model_id));
        const smap = new Map((d.sensitivity_map || []).map(r => [r.model_id, r]));
        const chars = {};
        for (const c of d.characteristics || []) (chars[c.report_id] ||= {})[c.field] = c;
        const register = {};
        for (const r of d.results_register || []) (register[r.study] ||= []).push(r);
        const harms = new Set((d.outcome_coverage?.safety || []).map(r => r.study));
        const satis = new Set((d.outcome_coverage?.recovery || []).filter(r => /satisf|accept/i.test(r.kind)).map(r => r.study));
        const tierOf = (mid, m) => {
            const role = m?.role || '';
            if (mid.startsWith('E2_')) return role.includes('(main)') ? 'e2' : 'sens';
            if (mid.startsWith('opioid24_')) return role === 'PRINCIPAL' || role === 'SUPPORTIVE' ? 'e1' : 'sens';
            return ['PRINCIPAL', 'SUPPORTIVE', 'ADDITIONAL'].includes(role) ? 'main' : 'sens';
        };
        return d.studies.map(s => {
            const id = s.report_id, g = graph.studies[id] || {}, models = g.models || [], ch = chars[id] || {}, reg = register[id] || [];
            const cells = {};
            for (const mid of models) {
                const fam = FAMILIES.find(f => f[3] && f[3](mid, later));
                if (!fam) continue;
                const t = tierOf(mid, graph.models[mid]?.canonical), cell = cells[fam[1]] ||= { tier: t, models: [] };
                cell.models.push(mid);
                if (TIER[t] > TIER[cell.tier]) cell.tier = t;
            }
            if (harms.has(id)) cells.harms = { tier: 'reported', models: [] };
            if (satis.has(id)) cells.satis = { tier: 'reported', models: [] };
            const compact = {};
            for (const [k, [, keys]] of Object.entries(COMPACT)) {
                const cs = keys.map(x => cells[x]).filter(Boolean);
                if (cs.length) compact[k] = { tier: cs.reduce((a, c) => TIER[c.tier] > TIER[a] ? c.tier : a, cs[0].tier), models: cs.flatMap(c => c.models) };
            }
            const roles = models.map(mid => graph.models[mid]?.canonical?.role || '');
            const st = new Set();
            if (cells.op_e1?.tier === 'e1') st.add('e1');
            if (cells.op_e2 && cells.op_e2.models.some(m => (graph.models[m]?.canonical?.role || '').includes('(main)'))) st.add('e2');
            if (st.has('e2') && !st.has('e1')) st.add('e2only');
            if (st.has('e1') && st.has('e2')) st.add('e1e2');
            if (roles.includes('PRINCIPAL')) st.add('principal');
            if (roles.includes('SUPPORTIVE')) st.add('supportive');
            if (roles.includes('ADDITIONAL')) st.add('additional');
            if (roles.some(r => r === 'SENSITIVITY' || r === 'LEAVE-ONE-OUT')) st.add('sensitivity');
            if (models.some(m => /diagnostic|stand-alone/.test(smap.get(m)?.relation || '') || m.includes('diagnostic'))) st.add('diagnostic');
            if (reg.some(r => r.decision === 'HOLD')) st.add('held');
            if (!models.length) st.add('nomodel');
            const robs = (g.rob || []).map(rid => graph.results[rid]?.rob).filter(Boolean);
            const fams = new Set(Object.keys(compact));
            const val = f => ch[f]?.value || '';
            // Plain words search descriptive text; ID-like terms (model or result IDs) search IDs, exact match first.
            const search = [id, s.trial_id, s.year, s.modality, s.comparator, g.background?.citation, ...CHARS.map(([f]) => val(f)), ...reg.map(r => r.outcome)].join(' ').toLowerCase();
            const ids = [...new Set([...models, ...reg.flatMap(r => [r.result_id, ...r.models.split(';')]), ...(g.results || [])])].filter(Boolean).map(x => x.toLowerCase());
            return { id, s, ch, cells, compact, st, robs, fams, reg, models, inputs: g.inputs || [], search, ids,
                year: +s.year, n: +s.randomized_n_report, surgery: val('surgical_category'), country: val('country'), cmp: val('comparator_class') };
        });
    }

    window.renderRichExplorer = function (containerId) {
        const d = window.CURRENT_REVIEW, graph = window.EVIDENCE_GRAPH, $ = id => document.getElementById(id);
        // Second-review note for a record file, from second_review.csv (reviewer and ISO date), or "pending".
        const reviewNote = file => { const r = (d.second_review || []).find(x => x.file.endsWith(file)); return r ? `confirmed by a second reviewer (${esc(r.reviewer)}, ${esc(r.review_date)})` : 'second review pending'; };
        if (!INDEX) INDEX = buildIndex(d, graph);
        const byId = new Map(INDEX.map(r => [r.id, r]));
        const nFam = new Set(INDEX.map(r => r.s.trial_id)).size;
        const ROLE_RANK = { PRINCIPAL: 0, SUPPORTIVE: 1, ADDITIONAL: 2 };

        const state = { search: '', modality: 'all', comparator: 'all', surgery: '', country: '', ymin: '', ymax: '', rob: '', size: '', family: '', status: '',
            study: '', matrix: 'compact', cols: DEFAULT_COLS.slice() };
        const qp = new URLSearchParams(window.location.hash.split('?')[1] || '');
        for (const k of [...FILTER_KEYS, 'study', 'matrix']) if (qp.has(k)) state[k] = qp.get(k);
        if (qp.has('cols')) state.cols = qp.get('cols').split(',').filter(c => CHARS.some(x => x[0] === c));
        const updateUrl = () => {
            const p = new URLSearchParams();
            for (const k of FILTER_KEYS) if (state[k] && state[k] !== 'all') p.set(k, state[k]);
            if (state.matrix !== 'compact') p.set('matrix', state.matrix);
            if (state.cols.join(',') !== DEFAULT_COLS.join(',')) p.set('cols', state.cols.join(','));
            if (state.study) p.set('study', state.study);
            const str = p.toString();
            window.history.replaceState(null, '', window.location.hash.split('?')[0] + (str ? '?' + str : ''));
        };

        // ---- Filtering (never refits anything).
        const contrastsOf = r => {
            const c = new Set(), lc = r.s.comparator.toLowerCase();
            if (lc.includes('sham')) c.add('Sham'); if (lc.includes('usual')) c.add('Usual'); if (lc.includes('active')) c.add('Active');
            for (const inp of r.inputs) { const cls = (inp.comparator_class || inp.comparator || '').toLowerCase(); if (cls.includes('sham')) c.add('Sham'); if (cls.includes('usual')) c.add('Usual'); if (cls.includes('active')) c.add('Active'); }
            for (const m of r.models) { if (/_sham|SHAM/.test(m)) c.add('Sham'); if (/_usual|USUAL/.test(m)) c.add('Usual'); if (m.includes('_active')) c.add('Active'); }
            if (!c.size) c.add('Unclear');
            return c;
        };
        const robState = r => !r.robs.length ? 'none' : r.robs.some(x => x.overall === 'High') ? 'high' : r.robs.some(x => x.overall === 'Some concerns') ? 'sc' : 'low';
        const idLike = w => w.includes('_') || /^(v33-|audit-|e2\.|qor)/.test(w);
        const exactIds = new Set(INDEX.flatMap(r => r.ids));
        const wordMatch = (r, w) => idLike(w) ? (exactIds.has(w) ? r.ids.includes(w) : r.ids.some(x => x.includes(w))) : r.search.includes(w);
        const matches = r => {
            if (state.search && !state.search.toLowerCase().split(/\s+/).filter(Boolean).every(w => wordMatch(r, w))) return false;
            if (state.modality !== 'all' && (state.modality === 'Unclear' ? r.s.modality !== 'UNCLEAR' : !(r.s.modality === state.modality || r.models.some(m => m.includes(state.modality + '_'))))) return false;
            if (state.comparator !== 'all' && !contrastsOf(r).has(state.comparator)) return false;
            if (state.surgery && r.surgery !== state.surgery) return false;
            if (state.country && r.country !== state.country) return false;
            if (state.ymin && r.year < +state.ymin) return false;
            if (state.ymax && r.year > +state.ymax) return false;
            if (state.rob && (state.rob === 'high' ? robState(r) !== 'high' : state.rob === 'sc' ? !r.robs.some(x => x.overall === 'Some concerns') : robState(r) !== state.rob)) return false;
            if (state.size && !SIZE.find(x => x[0] === state.size)[2](r.n)) return false;
            if (state.family && !r.fams.has(state.family)) return false;
            if (state.status && !r.st.has(state.status)) return false;
            return true;
        };

        // ---- Rendering helpers.
        // Cell badge: the abbreviation, with the plain-language status for screen readers and the full meaning on hover.
        const vs = c => { if (!c) return ''; const [ab, cls, lab, help] = VS[c.status] || ['?', 'vs-none', c.status, ''];
            return `<span class="vs ${cls}" data-tip="${esc(lab + ': ' + help + (c.source ? ' Source: ' + c.source : ''))}"><span class="sr-only">(${esc(lab)}) </span><span aria-hidden="true">${ab}</span></span>`; };
        // detail (study drawer): also show the verbatim source quote or extraction note carried in the note field.
        const charCell = (r, f, detail) => { const c = r.ch[f]; if (!c) return '<small>Not extracted</small>';
            const v = c.value || (VS[c.status] && !c.value ? VS[c.status][2] : 'Not extracted');
            return `${c.value ? esc(v) : `<small>${esc(v)}</small>`} ${vs(c)}${detail && c.note ? `<br><small class="char-quote">${esc(c.note)}</small>` : ''}`; };
        // Provenance legend (above the explorer): one keyboard-reachable help button per status, from VS.
        const statusBtn = s => { const [ab, cls, lab, help] = VS[s]; return `<button type="button" class="term vs ${cls}" data-tip="${esc(lab + ': ' + help)}" aria-label="${esc(lab)}: ${esc(help)}">${ab}</button>`; };
        // What an extraction record's fields currently say, from the data (single extractor, or second-reviewed with reviewer and date).
        const regimenStatus = (fields = REGIMEN_FIELDS) => {
            const rs = (d.characteristics || []).filter(c => fields.includes(c.field) && /extraction\.csv/.test(c.source)), single = rs.filter(c => c.status === 'Extracted (PDF quote, single extractor)').length;
            const reviewed = rs.filter(c => c.status === 'Verified (PDF quote, second reviewer)'), who = [...new Set(reviewed.map(c => (c.source.match(/second review ([A-Z]{2,4}, \d{4}-\d{2}-\d{2})/) || [])[1]).filter(Boolean))];
            return single ? `quoted from the report PDF (each quotation machine-checked against the report’s text); ${single} values come from a single extractor and stay marked as such until independently reviewed.`
                : `quoted from the report PDF (each quotation machine-checked against the report’s text) and confirmed by a second reviewer${who.length ? ` (${esc(who.join('; '))})` : ''}${rs.filter(c => c.status === 'Not reported in source').every(c => c.source.includes('second review')) ? ', including the fields recorded as not reported' : ''}.`;
        };
        const provenanceLegend = () => {
            const all = d.characteristics || [], used = Object.keys(VS).filter(s => all.some(c => c.status === s));
            const fields = [...new Set(all.map(c => c.field))].map(f => [f, (CHARS.find(x => x[0] === f) || [, EXTRA_FIELD_LABEL[f] || f.replaceAll('_', ' ')])[1]]);
            const count = (f, s) => all.filter(c => c.field === f && c.status === s).length;
            return `<section class="prov-legend" aria-labelledby="prov-legend-title"><h3 id="prov-legend-title">How far each characteristic has been checked</h3>
                <p class="note"><strong>Characteristics do not all have the same verification level.</strong> Registry- and PDF-verified values are distinguished from source-traced${used.includes('Legacy (v26, not re-verified)') ? ', legacy' : ''} and single-extractor fields. Missing values are not inferred.</p>
                <ul class="prov-list">${used.map(s => `<li>${statusBtn(s)} <span>${esc(VS[s][2])}</span></li>`).join('')}</ul>
                <p class="source">Select or focus a badge for what it means. <strong>Postoperative analgesia, PCA regimen, rescue analgesia and cumulative stimulation duration</strong>: ${regimenStatus()}</p>
                ${all.some(c => BASELINE_FIELDS.includes(c.field) && /baseline_protocol_extraction/.test(c.source)) ? `<p class="source"><strong>Age, sex, BMI, ASA status, anaesthesia and the stimulation protocol (acupoints, frequency, intensity, timing, sessions, session duration)</strong>, where the registry does not already hold a verified value: ${regimenStatus(BASELINE_FIELDS)}</p>` : ''}
                <details class="prov-counts"><summary>Verification level by field (${INDEX.length} reports)</summary><div class="table-scroll"><table><thead><tr><th scope="col">Field</th>${used.map(s => `<th scope="col" title="${esc(VS[s][2])}"><span class="vs ${VS[s][1]}" aria-hidden="true">${VS[s][0]}</span><span class="sr-only">${esc(VS[s][2])}</span></th>`).join('')}</tr></thead>
                <tbody>${fields.map(([f, l]) => `<tr><th scope="row">${esc(l)}</th>${used.map(s => { const n = count(f, s); return `<td>${n || '<span class="muted">·</span>'}</td>`; }).join('')}</tr>`).join('')}</tbody></table></div>
                <p class="source">Number of reports per field and status, from the harmonised characteristics file in Downloads.</p></details></section>`;
        };
        const cellBtn = (r, key, label, cell) => {
            if (!cell) return `<button type="button" class="matrix-cell none" data-cell="${key}" data-id="${esc(r.id)}" aria-label="${esc(r.id)} ${esc(label)}: no current model contribution; show extracted results">–</button>`;
            const lab = `${r.id} ${label}: ${STATE[cell.tier]}${cell.models.length ? '. Models: ' + cell.models.join(', ') : ''}`;
            return `<button type="button" class="matrix-cell ${cell.tier}" data-cell="${key}" data-id="${esc(r.id)}" aria-label="${esc(lab)}. Show results" title="${esc(lab)}">${cell.tier === 'e1' ? 'E1' : cell.tier === 'e2' ? 'E2' : cell.tier === 'reported' ? 'R' : ''}</button>`;
        };
        const activeFilters = () => {
            const out = [];
            const lab = (k, v) => ({ modality: `Modality: ${v}`, comparator: `Comparator: ${v}`, surgery: `Surgery: ${v}`, country: `Country: ${v}`, ymin: `From ${v}`, ymax: `To ${v}`,
                rob: ROB.find(x => x[0] === v)?.[1], size: `N ${SIZE.find(x => x[0] === v)?.[1]}`, family: `${COMPACT[v]?.[0]} evidence`, status: STATUSES.find(x => x[0] === v)?.[1], search: `Search: “${v}”` })[k];
            for (const k of FILTER_KEYS) if (state[k] && state[k] !== 'all') out.push([k, lab(k, state[k])]);
            return out;
        };
        const glance = () => {
            const bar = (key, value, label, n, max, on) => `<button type="button" class="glance-bar${on ? ' on' : ''}" data-glance="${key}" data-value="${esc(value)}" aria-pressed="${on}"><span class="gl-label">${esc(label)}</span><span class="gl-track"><span class="gl-fill" style="width:${Math.max(2, 100 * n / max)}%"></span></span><span class="gl-n">${n}</span></button>`;
            const group = (title, key, items, cur) => { const max = Math.max(...items.map(i => i[2])); return `<div class="glance-group"><h4>${title}</h4>${items.map(([v, l, n]) => bar(key, v, l, n, max, cur === v)).join('')}</div>`; };
            const count = f => { const m = new Map(); for (const r of INDEX) m.set(f(r), (m.get(f(r)) || 0) + 1); return [...m.entries()].sort((a, b) => b[1] - a[1]); };
            const fig = (d.stata?.figures || []).find(f => f.figure_id === 'fig_desc_evidence_base');
            return `<details class="glance" open><summary>Evidence-base counts: select a bar to filter <small>(${INDEX.length} reports, ${nFam} trial families; counts are reports, not patients)</small></summary><div class="glance-grid">` +
                group('Surgical category', 'surgery', count(r => r.surgery).map(([v, n]) => [v, v, n]), state.surgery) +
                group('Country', 'country', count(r => r.country).map(([v, n]) => [v, v, n]), state.country) +
                group('Publication year', 'year', YEARS.map(([l, a, b]) => [`${a}-${b}`, l, INDEX.filter(r => r.year >= a && r.year <= b).length]), state.ymin || state.ymax ? `${state.ymin || 0}-${state.ymax || 9999}` : '') +
                group('Modality', 'modality', count(r => r.s.modality).map(([v, n]) => [v === 'UNCLEAR' ? 'Unclear' : v, v, n]), state.modality) +
                group('Comparator (study-level label)', 'comparator', count(r => r.cmp).map(([v, n]) => [({ sham: 'Sham', 'usual care': 'Usual', 'active control': 'Active' })[v] || 'Unclear', v, n]), ({ Sham: 'sham', Usual: 'usual care', Active: 'active control' })[state.comparator] || '') +
                group('Randomised N per report', 'size', SIZE.map(([k, l, f]) => [k, l, INDEX.filter(r => f(r.n)).length]), state.size) +
                `</div>${fig ? `<p class="source">The same counts as publication figures (Stata): <a href="#fig-${esc(fig.figure_id)}">Evidence base at a glance</a>, above.</p>` : ''}</details>`;
        };

        const renderControls = () => `
            <h2>Study Explorer &amp; Contribution Matrix</h2>
            <p class="lede">All ${INDEX.length} reports (${nFam} operational trial families): characteristics with their verification status, and each report's contribution to the evidence bodies. Filters select reports; they never refit a meta-analysis.</p>
            ${provenanceLegend()}
            <div class="explorer-toolbar">
                <div style="flex:2;min-width:240px"><label for="explorer-search">Search</label>
                    <input id="explorer-search" type="search" placeholder="Study, year, country, surgery, acupoint (e.g. PC6), outcome, model or result ID" value="${esc(state.search)}"></div>
                <div><label for="explorer-modality">Modality</label><select id="explorer-modality">${[['all', 'All'], ['TEAS', 'TEAS'], ['EA', 'Needle EA'], ['Unclear', 'Unclear']].map(([v, l]) => `<option value="${v}"${state.modality === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div><label for="explorer-comparator">Comparator</label><select id="explorer-comparator">${[['all', 'All'], ['Sham', 'Sham'], ['Usual', 'Usual care'], ['Active', 'Active control'], ['Unclear', 'Unclear']].map(([v, l]) => `<option value="${v}"${state.comparator === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div><label for="explorer-status">Contribution</label><select id="explorer-status"><option value="">Any</option>${STATUSES.map(([v, l]) => `<option value="${v}"${state.status === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div><label for="explorer-family">Outcome family</label><select id="explorer-family"><option value="">Any</option>${Object.entries(COMPACT).map(([v, [l]]) => `<option value="${v}"${state.family === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div><label for="explorer-rob">Result-specific RoB</label><select id="explorer-rob"><option value="">Any</option>${ROB.map(([v, l]) => `<option value="${v}"${state.rob === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div><label for="explorer-surgery">Surgery</label><select id="explorer-surgery"><option value="">Any</option>${[...new Set(INDEX.map(r => r.surgery))].sort().map(v => `<option${state.surgery === v ? ' selected' : ''}>${esc(v)}</option>`).join('')}</select></div>
                <div><label for="explorer-country">Country</label><select id="explorer-country"><option value="">Any</option>${[...new Set(INDEX.map(r => r.country))].filter(Boolean).sort().map(v => `<option${state.country === v ? ' selected' : ''}>${esc(v)}</option>`).join('')}</select></div>
                <div><label for="explorer-size">Randomised N</label><select id="explorer-size"><option value="">Any</option>${SIZE.map(([v, l]) => `<option value="${v}"${state.size === v ? ' selected' : ''}>${l}</option>`).join('')}</select></div>
                <div class="yr"><label for="explorer-ymin">Year from / to</label><span><input id="explorer-ymin" type="number" inputmode="numeric" min="1990" max="2030" value="${esc(state.ymin)}" aria-label="Year from"><input id="explorer-ymax" type="number" inputmode="numeric" min="1990" max="2030" value="${esc(state.ymax)}" aria-label="Year to"></span></div>
            </div>
            <div class="presets" role="group" aria-label="Filter presets">${PRESETS.map(([l], i) => `<button type="button" class="preset" data-preset="${i}">${esc(l)}</button>`).join('')}</div>
            <div class="chips-row"><span id="explorer-count" aria-live="polite"></span><span id="explorer-chips"></span></div>
            <div id="explorer-glance"></div>
            <details class="colchooser"><summary>Columns and characteristics</summary>
                <fieldset><legend class="sr-only">Characteristic columns</legend>${CHARS.map(([f, l]) => `<label class="chk"><input type="checkbox" data-col="${f}"${state.cols.includes(f) ? ' checked' : ''}> ${esc(l)}</label>`).join('')}</fieldset>
                <p class="source">Each value carries its verification badge (${Object.values(VS).map(([ab, cls, lab]) => `<span class="vs ${cls}" aria-hidden="true">${ab}</span> ${esc(lab)}`).join(' · ')}); see the legend above for what each means.${(d.characteristics || []).some(c => c.status === 'Legacy (v26, not re-verified)') ? ' Legacy values have not been re-checked against the PDF: do not use them for subgrouping or characteristics text without checking.' : ''}</p></details>
            <div class="matrix-bar">
                <div class="matrix-legend" aria-label="Contribution legend">
                    <span><span class="matrix-cell e1">E1</span> E1 primary opioid body</span><span><span class="matrix-cell e2">E2</span> E2 post-hoc body only</span>
                    <span><span class="matrix-cell main"></span> Main body</span><span><span class="matrix-cell sens"></span> Sensitivity/diagnostic only</span>
                    <span><span class="matrix-cell reported">R</span> Reported, not pooled</span><span><span class="matrix-cell none">–</span> No model contribution</span></div>
                <button type="button" id="explorer-matrix-toggle" class="preset" aria-pressed="${state.matrix === 'detailed'}">${state.matrix === 'detailed' ? 'Compact matrix' : 'Detailed matrix'}</button>
            </div>
            <details class="howto"><summary>How to read the contribution matrix</summary><p>Each cell shows how a report contributes to an outcome family: <strong>E1</strong> in a registered primary opioid body; <strong>E2</strong> only in the post-hoc E2 synthesis; a filled mark in a main (graded or additional) body; a ring in sensitivity or diagnostic models only; <strong>R</strong> reported descriptively (harms, satisfaction). A dash means no current model uses a result from this family; it does not mean the outcome was not measured. Select any cell to see the exact results, their decisions and the reason a result is excluded or held.</p></details>
            <div id="explorer-table-container"></div>
            <dialog id="study-drawer" aria-labelledby="study-drawer-title"><div id="study-drawer-content"></div></dialog>
            <dialog id="cell-dialog" aria-labelledby="cell-dialog-title"><button type="button" class="dlg-close" data-close="cell-dialog">Close</button><div id="cell-dialog-content"></div></dialog>`;

        const renderTable = () => {
            const rows = INDEX.filter(matches), fams = new Set(rows.map(r => r.s.trial_id)).size;
            const cols = state.cols.map(f => CHARS.find(c => c[0] === f)).filter(Boolean);
            const matrixCols = state.matrix === 'detailed' ? FAMILIES.map(([g, k, l]) => [k, l, g]) : Object.entries(COMPACT).map(([k, [l]]) => [k, l, '']);
            const header = state.matrix === 'detailed'
                ? `<tr><th rowspan="2">Study</th><th rowspan="2">Modality</th><th rowspan="2">Comparator</th>${cols.map(([, l]) => `<th rowspan="2">${esc(l)}</th>`).join('')}${[...new Set(FAMILIES.map(f => f[0]))].map(g => `<th colspan="${FAMILIES.filter(f => f[0] === g).length}" class="grp">${g}</th>`).join('')}<th rowspan="2">Figures</th></tr><tr>${matrixCols.map(([, l]) => `<th class="mx">${esc(l)}</th>`).join('')}</tr>`
                : `<tr><th>Study</th><th>Modality</th><th>Comparator</th>${cols.map(([, l]) => `<th>${esc(l)}</th>`).join('')}${matrixCols.map(([, l]) => `<th class="mx">${esc(l)}</th>`).join('')}<th>Figures</th></tr>`;
            const body = rows.map(r => {
                let nAnal = null;
                if (state.comparator !== 'all') {
                    const inp = r.inputs.filter(i => i.n_i !== undefined && i.n_i !== '' && (i.comparator_class || i.comparator || '').toLowerCase().includes(state.comparator.toLowerCase()))
                        .sort((a, b) => (ROLE_RANK[graph.models[a.model_id]?.canonical?.role] ?? 3) - (ROLE_RANK[graph.models[b.model_id]?.canonical?.role] ?? 3))[0];
                    if (inp) nAnal = `${Number(inp.n_i) + Number(inp.n_c)}<br><small>${esc(inp.model_id)}</small>`;
                }
                const figs = (window.ARTICLE_FIGURES?.[r.id] || []).length;
                return `<tr class="study-row" data-id="${esc(r.id)}"><td><button type="button" class="text-button study-open" data-id="${esc(r.id)}" aria-haspopup="dialog">${esc(r.id)}</button><br><small>${esc(r.s.trial_id)}</small></td>` +
                    `<td><span class="tag">${esc(r.s.modality)}</span></td><td><span class="tag">${esc(r.s.comparator)}</span></td>` +
                    cols.map(([f]) => `<td class="ch">${f === 'analysed_n' && nAnal ? nAnal : charCell(r, f)}</td>`).join('') +
                    matrixCols.map(([k, l]) => `<td class="mxc">${cellBtn(r, k, l, state.matrix === 'detailed' ? r.cells[k] : r.compact[k])}</td>`).join('') +
                    `<td class="mxc">${figs ? `<span class="tag">${figs}</span>` : '<small>–</small>'}</td></tr>`;
            }).join('');
            $('explorer-table-container').innerHTML = `<div class="table-scroll"><table class="explorer-table"><thead>${header}</thead><tbody>${body || `<tr><td colspan="${4 + cols.length + matrixCols.length}" style="text-align:center;padding:2rem">No reports match these filters.</td></tr>`}</tbody></table></div>`;
            $('explorer-count').textContent = `${rows.length} of ${INDEX.length} reports · ${fams} of ${nFam} operational families`;
            const chips = activeFilters();
            $('explorer-chips').innerHTML = chips.map(([k, l]) => `<button type="button" class="chip" data-chip="${k}" aria-label="Remove filter ${esc(l)}">${esc(l)} ×</button>`).join('') +
                (chips.length ? '<button type="button" class="chip clear" data-chip="__all">Clear filters</button>' : '');
            $('explorer-glance').innerHTML = glance();
        };

        // ---- Cell detail: exact results behind a contribution cell, with decisions from the register.
        const openCell = (id, key) => {
            const r = byId.get(id); if (!r) return;
            const detailed = FAMILIES.find(f => f[1] === key), compactKey = COMPACT[key] ? key : Object.keys(COMPACT).find(k => COMPACT[k][1].includes(key));
            const label = detailed ? `${detailed[0]} · ${detailed[2]}` : COMPACT[key][0];
            const cell = detailed ? r.cells[key] : r.compact[key];
            let html = `<h2 id="cell-dialog-title" style="margin-top:0">${esc(id)} · ${esc(label)}</h2>`;
            if (key === 'harms' || key === 'satis') {
                const recs = key === 'harms' ? (d.outcome_coverage?.safety || []).filter(x => x.study === id) : (d.outcome_coverage?.recovery || []).filter(x => x.study === id && /satisf|accept/i.test(x.kind));
                html += recs.length ? `<p>Reported descriptively; not pooled.</p>` + recs.map(x => `<div class="panel"><p><strong>${esc(x.status || x.kind)}</strong> · ${esc(x.window)}</p><p>${esc(x.finding || x.source_values)}</p><p><small>${esc(x.denominator || x.population || '')}${x.limitation ? ' · ' + esc(x.limitation) : ''}${x.synthesis_disposition ? ' · ' + esc(x.synthesis_disposition) : ''}</small></p><p class="source">${esc(x.source_pdf)} · pp. ${esc(x.pdf_pages)}</p></div>`).join('')
                    : '<p>No record in the outcome-coverage audit for this report.</p>';
            } else {
                const models = cell ? cell.models : [], used = new Set();
                html += `<p>${cell ? esc(STATE[cell.tier]) : 'No current model uses a result from this family for this report.'}</p>`;
                for (const mid of models) {
                    const m = graph.models[mid]?.canonical || {}, core = d.models.some(x => x.model_id === mid), rr = (m.measure || '') === 'RR';
                    const ins = r.inputs.filter(i => i.model_id === mid);
                    html += `<h3>${modelName(mid)}</h3><p><small>${esc(m.role || '')} · ${esc(m.status || '')} · k = ${esc(m.k ?? '')}</small></p>` +
                        `<div class="table-scroll"><table><thead><tr><th>Result</th><th>Window</th><th>n (I / C)</th><th>Study estimate</th><th>Source</th><th>RoB</th><th>Decision</th></tr></thead><tbody>` +
                        ins.map(i => {
                            const parts = String(i.result_id).split('+'), reg = r.reg.find(x => x.result_id === parts[0]) || {}, rob = parts.map(p => graph.results[p]?.rob?.overall).filter(Boolean);
                            parts.forEach(p => used.add(p));
                            const est = i.yi !== undefined && i.yi !== '' ? (() => { const y = +i.yi, se = Math.sqrt(+i.vi), f = v => num(rr ? Math.exp(v) : v); return `${f(y)} [${f(y - Z95 * se)}, ${f(y + Z95 * se)}]`; })() : '—';
                            const link = core ? `<button type="button" class="text-button result-open" data-result="${esc(i.result_id)}" data-result-model="${esc(mid)}">${esc(i.result_id)}</button>` : esc(i.result_id);
                            return `<tr><td>${link}</td><td>${esc(reg.window || i.window || '')}</td><td>${num(i.n_i, 0)} / ${num(i.n_c, 0)}</td><td>${est}</td><td>${esc(i.source_location || reg.source_location || '')}</td><td>${rob.length ? rob.map(x => `<span class="tag ${x === 'High' ? 'risk-high' : x === 'Low' ? 'risk-low' : 'rob-sc'}">${esc(x)}</span>`).join(' ') : '<small>not assessed</small>'}</td><td>${esc(reg.decision || '')}</td></tr>`;
                        }).join('') + `</tbody></table></div>`;
                }
                const rx = FAMILY_RX[compactKey], others = r.reg.filter(x => rx && rx.test(x.outcome) && !used.has(x.result_id));
                html += `<h3>${models.length ? 'Other extracted results in this family' : 'Extracted results in this family'} (${others.length})</h3>` +
                    (others.length ? `<div class="table-scroll"><table><thead><tr><th>Result</th><th>Outcome</th><th>Window</th><th>Decision</th><th>Reason recorded</th></tr></thead><tbody>${others.map(x => `<tr><td>${esc(x.result_id)}</td><td>${esc(x.outcome)}</td><td>${esc(x.window)}</td><td><strong>${esc(x.decision)}</strong></td><td>${esc(x.rationale)}</td></tr>`).join('')}</tbody></table></div>`
                        : '<p>No extracted result for this outcome family in the canonical results register for this report.</p>') +
                    note(`Decisions and reasons are copied from the canonical results register. A family is matched here by outcome wording, so this list is a navigation aid; model membership above is exact.`);
            }
            html += `<p><button type="button" class="text-button study-open" data-id="${esc(id)}">Open the ${esc(id)} study profile →</button></p>`;
            $('cell-dialog-content').innerHTML = html; $('cell-dialog').showModal();
        };
        const note = t => `<p class="note">${t}</p>`;

        // ---- Study drawer.
        const clearStudyKey = e => {
            const drawer = $('study-drawer');
            if (e && e.target !== drawer) return;
            if (!drawer || !drawer.isConnected || drawer.open || !window.location.hash.startsWith('#studies') || !state.study) return;
            state.study = ''; updateUrl();
        };
        const openDrawer = id => {
            const r = byId.get(id); if (!r) return;
            if ($('cell-dialog').open) $('cell-dialog').close();
            const s = r.s, g = graph.studies[id] || {}, bg = g.background || {}, ch = r.ch;
            const row = (label, f) => `<tr><th scope="row">${esc(label)}</th><td>${charCell(r, f, true)}</td></tr>`;
            const tbl = rowsHtml => `<div class="table-scroll"><table><tbody>${rowsHtml}</tbody></table></div>`;
            const acc = [...(d.e2_accounting?.tierA || []), ...(d.e2_accounting?.tierA_addendum || [])].filter(x => x.report === id || (id.startsWith(x.report + ' (') && x.report.includes(' ')));
            const b12 = [...(d.e2_accounting?.tierB1 || []), ...(d.e2_accounting?.tierB2 || [])].filter(x => x.report === id);
            const holds = r.reg.filter(x => x.decision === 'HOLD');
            const coreIn = new Set(d.inputs.filter(i => i.study === id).flatMap(i => [i.result_id, ...String(i.result_id).split('+')]));
            const inputFor = rid => d.inputs.find(i => i.study === id && String(i.result_id).split('+').includes(rid));
            const figs = window.ARTICLE_FIGURES?.[id] || [];
            const byStatus = Object.keys(VS).map(st => [st, Object.values(ch).filter(c => c.status === st).length]).filter(([, n]) => n);
            const html = `
                <div class="drawer-head"><button type="button" id="close-drawer" aria-label="Close study profile">&times;</button>
                    <h2 id="study-drawer-title" style="margin:0 0 4px">${esc(id)}</h2><p class="source" style="margin:0">${esc(bg.citation || '')}${bg.doi ? ` · <a href="https://doi.org/${esc(bg.doi)}" target="_blank" rel="noopener">DOI</a>` : ''}</p>
                    <p style="margin:8px 0 0"><span class="tag">${esc(s.modality)}</span> <span class="tag">${esc(s.comparator)}</span> <span class="tag">${esc(s.trial_id)}</span> ${[...r.st].filter(x => ['e1', 'e2', 'e2only', 'held'].includes(x)).map(x => `<span class="tag badge-${x}">${esc(STATUSES.find(y => y[0] === x)[1])}</span>`).join(' ')}</p>
                    <nav class="drawer-nav" aria-label="Sections">${['Population', 'Anaesthesia', 'Intervention', 'Comparator', 'Outcomes', 'Models', 'E1/E2', 'RoB', 'Figures', 'Sources', 'Holds'].map(x => `<a href="#dr-${x.replace(/\W/g, '')}">${x}</a>`).join('')}</nav></div>
                <p class="source">Verification of this report’s ${Object.keys(ch).length} characteristic fields: ${byStatus.map(([st, n]) => `<span class="vs ${VS[st][1]}" aria-hidden="true">${VS[st][0]}</span> ${esc(VS[st][2])} ${n}`).join(' · ')}. Badges beside each value show which; hover a badge, or see the legend in the explorer, for what it means.</p>
                <h3 id="dr-Population">Population</h3>${tbl(row('Year', 'year') + row('Country', 'country') + row('Surgical category', 'surgical_category') + row('Procedure', 'procedure') + row('Randomised N', 'randomized_n') + row('Analysed N', 'analysed_n') + row('Age', 'age') + row('Female', 'female') + row('BMI', 'bmi') + row('ASA', 'asa'))}
                <h3 id="dr-Anaesthesia">Anaesthesia and analgesia</h3>${tbl(row('Anaesthesia', 'anaesthesia') + row('Postoperative analgesia', 'postoperative_analgesia') + row('PCA regimen', 'pca_regimen') + row('Rescue analgesia', 'rescue_analgesia'))}
                ${REGIMEN_FIELDS.some(f => ch[f]?.status === 'Extracted (PDF quote, single extractor)') ? note('Postoperative analgesia, PCA regimen, rescue analgesia and cumulative stimulation duration are quoted from the report (quotation shown under each value, machine-checked against the report’s text) by a single extractor; they have not been independently reviewed.')
                  : REGIMEN_FIELDS.some(f => ch[f]?.status === 'Verified (PDF quote, second reviewer)') ? note(`Postoperative analgesia, PCA regimen, rescue analgesia and cumulative stimulation duration are quoted from the report (quotation shown under each value, machine-checked against the report’s text) and were confirmed by a second reviewer (${esc((ch[REGIMEN_FIELDS.find(f => ch[f]?.status === 'Verified (PDF quote, second reviewer)')].source.match(/second review ([A-Z]{2,4}, \d{4}-\d{2}-\d{2})/) || [, 'see source'])[1])}).`) : ''}
                ${['age', 'female', 'bmi', 'asa', 'anaesthesia'].some(f => /^(Extracted \(PDF quote, single extractor\)|Verified \(PDF quote, second reviewer\))$/.test(ch[f]?.status || '') && /baseline_protocol_extraction/.test(ch[f].source)) ? note(`Population and anaesthesia values quoted from the report (quotation shown under each value, machine-checked against the report’s text) were extracted by one extractor and ${reviewNote('baseline_protocol_extraction.csv')}.`) : ''}
                <h3 id="dr-Intervention">Intervention</h3>${tbl(row('Intervention arms (result register)', 'intervention_arms') + row('Acupoints', 'acupoints') + row('Frequency', 'frequency') + row('Intensity', 'intensity') + row('Timing', 'timing') + row('Sessions', 'sessions') + row('Session duration', 'session_duration') + row('Cumulative duration', 'cumulative_duration'))}
                ${STRICTA_FIELDS.some(f => /^(Extracted \(PDF quote, single extractor\)|Verified \(PDF quote, second reviewer\))$/.test(ch[f]?.status || '') && /baseline_protocol_extraction/.test(ch[f].source)) ? note(`Stimulation protocol values are quoted from the report (quotation shown under each value, machine-checked against the report’s text); extracted by one extractor and ${reviewNote('baseline_protocol_extraction.csv')}. The intervention-arm text comes from the canonical result register.`)
                  : STRICTA_FIELDS.some(f => ch[f]?.status === 'Legacy (v26, not re-verified)') ? note('STRICTA details marked L are legacy imports (not re-verified); the intervention-arm text comes from the canonical result register.') : ''}
                ${bg.stricta?.status === 'Verified' && STRICTA_FIELDS.some(f => ch[f]?.status === 'Partly verified (source excerpt)') ? note(`Partly source-verified ${esc(bg.stricta.verification_date)}: “${esc(bg.stricta.source_excerpt)}”${bg.stricta.correction_note ? ' ' + esc(bg.stricta.correction_note) : ''}`) : ''}
                <h3 id="dr-Comparator">Comparator</h3>${tbl(`<tr><th scope="row">Study-level label</th><td>${esc(s.comparator)} <small>(${esc(s.comparator_source_status || '')})</small></td></tr>` + row('Control / sham arms (result register)', 'control_arms'))}
                <h3 id="dr-Outcomes">Outcome inventory (${r.reg.length} extracted results)</h3>
                <div class="table-scroll"><table><thead><tr><th>Result</th><th>Outcome</th><th>Window</th><th>Decision</th><th>Models</th></tr></thead><tbody>${r.reg.map(x => { const inp = inputFor(x.result_id);
                    return `<tr><td>${inp ? `<button type="button" class="text-button result-open" data-result="${esc(inp.result_id)}" data-result-model="${esc(inp.model_id)}">${esc(x.result_id)}</button>` : esc(x.result_id)}</td><td>${esc(x.outcome)}</td><td>${esc(x.window)}</td><td><strong>${esc(x.decision)}</strong>${x.decision !== 'INCLUDE' && x.rationale ? `<br><small>${esc(x.rationale)}</small>` : ''}</td><td>${x.models.split(';').filter(Boolean).map(m => modelName(m)).join('<br>') || '<small>none</small>'}</td></tr>`; }).join('')}</tbody></table></div>
                <h3 id="dr-Models">Model contributions (${r.models.length})</h3>
                ${r.models.length ? `<div class="table-scroll"><table><thead><tr><th>Model</th><th>Role</th><th>k</th></tr></thead><tbody>${r.models.map(mid => { const m = graph.models[mid]?.canonical || {}; return `<tr><td>${modelName(mid)}</td><td>${esc(m.role || '—')}</td><td>${esc(m.k ?? '—')}</td></tr>`; }).join('')}</tbody></table></div>` : note('No contribution to any current model. This is not an efficacy claim; results may be reported but not poolable, held or ineligible (see the outcome inventory).')}
                <h3 id="dr-E1E2">E1 / E2 status</h3>
                ${acc.length || b12.length ? `<div class="table-scroll"><table><thead><tr><th>Comparison</th><th>E1</th><th>E2</th><th>Rule / basis</th></tr></thead><tbody>${acc.map(x => `<tr><td><button type="button" class="text-button" data-e1e2="${esc(x.body)}">${esc(x.body)} →</button></td><td>${esc(x.E1_disposition)}</td><td><strong>${esc(x.E2_disposition)}</strong></td><td>${esc(x.E2_basis)}</td></tr>`).join('')}${b12.filter(x => !acc.some(a => a.report === x.report)).map(x => `<tr><td>${esc(x.modality)} vs ${esc(x.comparator)}</td><td>${esc(x.E1_disposition || '—')}</td><td><strong>${esc(x.E2_disposition)}</strong></td><td>${esc(x.E2_rule_failed)}</td></tr>`).join('')}</tbody></table></div>` : note('Not a candidate for the primary opioid outcome in the E2 decision files.')}
                <h3 id="dr-RoB">Result-specific risk of bias (${r.robs.length})</h3>
                ${r.robs.length ? `<div class="table-scroll"><table><thead><tr><th>Result</th><th>Outcome / window</th><th>Overall</th></tr></thead><tbody>${r.robs.map(x => `<tr><td>${esc(x.result_id)}</td><td>${esc(x.outcome)}<br><small>${esc(x.window)}</small></td><td><span class="tag ${x.overall === 'High' ? 'risk-high' : x.overall === 'Low' ? 'risk-low' : 'rob-sc'}">${esc(x.overall)}</span></td></tr>`).join('')}</tbody></table></div><p><button type="button" class="text-button" data-risk-q="${esc(id)}">Open these assessments in the RoB matrix →</button></p>` : note('No result-specific RoB 2 assessment: none of this report’s results is in a current non-sensitivity body. No study-wide rating is substituted.')}
                ${figs.length ? `<h3 id="dr-Figures">Article figures (${figs.length})</h3><div class="figure-grid">${figs.map(f => `<figure><button class="figure-open" data-src="${esc(f.src)}" data-caption="${esc(id + ' · ' + f.caption)}"><img src="${esc(f.src)}" loading="lazy" alt="${esc(id + ' ' + f.caption)}"></button><figcaption>${esc(f.caption)}</figcaption></figure>`).join('')}</div>` : `<h3 id="dr-Figures">Article figures</h3><p><small>None extracted.</small></p>`}
                <h3 id="dr-Sources">Sources and provenance</h3>
                <p class="source">Source PDF: ${esc(s.source_pdf)}<br>SHA-256: ${esc(s.source_sha256)}<br>Registry N source: page ${esc(s.n_source_page)} · “${esc((s.n_source_excerpt || '').slice(0, 220))}…”</p>
                <p class="source">Characteristic sources: ${[...new Set(Object.values(ch).map(c => c.source).filter(Boolean))].map(esc).join(' · ')}</p>
                <h3 id="dr-Holds">Holds and source queries (${holds.length})</h3>
                ${holds.length ? `<ul>${holds.map(x => `<li><strong>${esc(x.result_id)}</strong> ${esc(x.outcome)} (${esc(x.window)}): ${esc(x.rationale)}</li>`).join('')}</ul>` : '<p><small>No held results.</small></p>'}`;
            $('study-drawer-content').innerHTML = html;
            const drawer = $('study-drawer');
            if (!drawer.open) drawer.showModal();
            state.study = id; updateUrl();
            $('close-drawer').addEventListener('click', () => { drawer.close(); clearStudyKey(); });
            drawer.querySelectorAll('.drawer-nav a').forEach(a => a.addEventListener('click', e => { e.preventDefault(); drawer.querySelector(a.getAttribute('href'))?.scrollIntoView({ block: 'start' }); }));
        };

        // ---- Mount and events (delegated; the table re-renders without rebuilding the index).
        const container = $(containerId);
        container.innerHTML = renderControls();
        renderTable();
        $('study-drawer').addEventListener('close', clearStudyKey);
        if (state.study) openDrawer(state.study);
        const set = (k, v) => { state[k] = v; updateUrl(); renderTable(); };
        let timer;
        container.addEventListener('input', e => {
            if (e.target.id === 'explorer-search') { clearTimeout(timer); const v = e.target.value; timer = setTimeout(() => set('search', v), 150); }
            if (e.target.id === 'explorer-ymin' || e.target.id === 'explorer-ymax') { clearTimeout(timer); const k = e.target.id.slice(9), v = e.target.value; timer = setTimeout(() => set(k, v), 300); }
        });
        container.addEventListener('change', e => {
            const id = e.target.id;
            if (id?.startsWith('explorer-') && !['explorer-search', 'explorer-ymin', 'explorer-ymax'].includes(id)) set(id.slice(9), e.target.value);
            if (e.target.dataset.col) { state.cols = CHARS.map(c => c[0]).filter(f => container.querySelector(`[data-col="${f}"]`).checked); updateUrl(); renderTable(); }
        });
        const syncControls = () => {
            for (const k of ['modality', 'comparator', 'status', 'family', 'rob', 'surgery', 'country', 'size', 'search', 'ymin', 'ymax']) { const el = $('explorer-' + k); if (el) el.value = state[k] === undefined ? '' : state[k]; }
        };
        container.addEventListener('click', e => {
            const t = e.target;
            const cellB = t.closest('.matrix-cell[data-cell]'); if (cellB) { e.stopPropagation(); openCell(cellB.dataset.id, cellB.dataset.cell); return; }
            const pre = t.closest('[data-preset]'); if (pre) { for (const k of FILTER_KEYS) state[k] = ['modality', 'comparator'].includes(k) ? 'all' : ''; Object.assign(state, PRESETS[+pre.dataset.preset][1]); syncControls(); updateUrl(); renderTable(); return; }
            const chip = t.closest('[data-chip]'); if (chip) { const k = chip.dataset.chip; for (const x of (k === '__all' ? FILTER_KEYS : [k])) state[x] = ['modality', 'comparator'].includes(x) ? 'all' : ''; syncControls(); updateUrl(); renderTable(); return; }
            const gl = t.closest('[data-glance]'); if (gl) {
                const k = gl.dataset.glance, v = gl.dataset.value;
                if (k === 'year') { const [a, b] = v.split('-'); const on = state.ymin === a && state.ymax === b; state.ymin = on ? '' : a; state.ymax = on ? '' : (b === '9999' ? '' : b); if (!on && b === '9999') state.ymax = ''; }
                else if (k === 'modality') state.modality = state.modality === (v === 'UNCLEAR' ? 'Unclear' : v) ? 'all' : (v === 'UNCLEAR' ? 'Unclear' : v);
                else if (k === 'comparator') { const m = { sham: 'Sham', 'usual care': 'Usual', 'active control': 'Active' }[v] || 'Unclear'; state.comparator = state.comparator === m ? 'all' : m; }
                else state[k] = state[k] === v ? '' : v;
                syncControls(); updateUrl(); renderTable(); return;
            }
            if (t.id === 'explorer-matrix-toggle') { state.matrix = state.matrix === 'detailed' ? 'compact' : 'detailed'; t.textContent = state.matrix === 'detailed' ? 'Compact matrix' : 'Detailed matrix'; t.setAttribute('aria-pressed', String(state.matrix === 'detailed')); updateUrl(); renderTable(); return; }
            if (t.closest('[data-close="cell-dialog"]')) { $('cell-dialog').close(); return; }
            const so = t.closest('.study-open'); if (so) { e.stopPropagation(); openDrawer(so.dataset.id); return; }
            const row = t.closest('.study-row'); if (row && !t.closest('button,a,input,select')) openDrawer(row.dataset.id);
        });
    };
})();
