// ═══════════════════════════════════════════════════════════════════════════
// FINDINGS-FIRST LAYER, EVIDENCE LINKS, URL ROUTING AND FILTER SCOPE
// ═══════════════════════════════════════════════════════════════════════════
// Usability layer only. It reads the same authoritative objects the rest of the
// dashboard uses (STATA_MASTER_RESULTS for saved Stata estimates and their
// adjudicated GRADE, window.V33_DATA for the generated evidence base) and never
// recomputes, rounds differently, or restates a scientific judgement.
//
// Three rules this file must keep:
//   1. Saved Stata estimates and browser-side exploratory calculations are
//      labelled differently and never presented as interchangeable.
//   2. A GRADE or RoB judgement is shown only next to the synthesis it was made
//      for. Nothing is inherited across analyses.
//   3. Study filters change study counts and characteristics. They never change
//      a saved estimate, and the interface says so where both are visible.

(function () {
  'use strict';

  // ── analyses that have a findings card ────────────────────────────────────
  // Each entry names the exact synthesis, the RoB outcome key that belongs to
  // it, and the download that contains it. `robKey` is the result-specific
  // key -- it is never a study-level summary.
  const PRIMARY_CARDS = [
    {
      id: 'AN-01-TEAS',
      role: 'primary',
      modality: 'TEAS',
      comparatorLabel: 'inert sham',
      robKey: 'opioid_24h',
      figure: 'forest_subgroup_modality_primary.png',
      download: 'v26/01_DATA/opioid_24h_primary.csv'
    },
    {
      id: 'AN-01-EA',
      role: 'primary',
      modality: 'EA',
      comparatorLabel: 'usual care / no stimulation',
      robKey: 'opioid_24h',
      figure: 'forest_subgroup_modality_primary.png',
      download: 'v26/01_DATA/opioid_24h_primary.csv'
    }
  ];

  const SUPPORTING_CARD = {
    id: 'AN-01-COMB',
    role: 'supporting',
    robKey: 'opioid_24h',
    figure: 'forest_opioid24_primary_mme.png',
    download: 'v26/01_DATA/opioid_24h_primary.csv'
  };

  const GRADE_SYMBOL = {
    'High': '⊕⊕⊕⊕',
    'Moderate': '⊕⊕⊕◯',
    'Low': '⊕⊕◯◯',
    'Very Low': '⊕◯◯◯',
    'Pending': '◯◯◯◯'
  };

  const esc = v => String(v == null ? '' : v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  const analysis = id => (window.STATA_MASTER_RESULTS || {})[id];

  // ── URL state ─────────────────────────────────────────────────────────────
  // A shareable link carries the tab plus whatever context the reader had
  // selected. Reopening it restores that context rather than a default view.
  const URL_KEYS = ['tab', 'outcome', 'subgroup', 'modality', 'comparator', 'study', 'analysis', 'rob'];
  let applyingUrl = false;
  // Captured at parse time. Any refresh() before the restore would otherwise
  // replaceState() the default view over the incoming deep link and lose it.
  let booted = false;
  let bootState = null;

  function readUrl() {
    const raw = window.location.hash.replace(/^#/, '');
    const out = {};
    if (!raw) return out;
    raw.split('&').forEach(pair => {
      const [k, v] = pair.split('=');
      if (k && v && URL_KEYS.includes(k)) out[k] = decodeURIComponent(v);
    });
    return out;
  }

  function currentState() {
    const s = { tab: window.activeTab || 'intro' };
    if (window.currentOutcome && window.currentOutcome !== 'opioid_24h') s.outcome = window.currentOutcome;
    if (window.currentSubgroup && window.currentSubgroup !== 'none') s.subgroup = window.currentSubgroup;
    if (window.filterModality && window.filterModality !== 'all') s.modality = window.filterModality;
    if (window.filterComparator && window.filterComparator !== 'all') s.comparator = window.filterComparator;
    if (window.focusStudyId) s.study = window.focusStudyId;
    if (window.focusAnalysisId) s.analysis = window.focusAnalysisId;
    return s;
  }

  function buildHash(state) {
    return '#' + URL_KEYS
      .filter(k => state[k] != null && state[k] !== '')
      .map(k => `${k}=${encodeURIComponent(state[k])}`)
      .join('&');
  }

  // push = a navigation the reader made (Back should undo it)
  // replace = a redraw that should not add a history entry
  function syncUrl(push) {
    if (applyingUrl || !booted) return;
    const hash = buildHash(currentState());
    if (hash === window.location.hash) return;
    if (push) window.history.pushState(currentState(), '', hash);
    else window.history.replaceState(currentState(), '', hash);
  }

  function applyUrl(explicit) {
    const s = explicit || readUrl();
    applyingUrl = true;
    try {
      if (s.modality && document.getElementById('filter-modality')) {
        window.filterModality = s.modality;
        document.getElementById('filter-modality').value = s.modality;
      }
      if (s.comparator && document.getElementById('filter-comparator')) {
        window.filterComparator = s.comparator;
        document.getElementById('filter-comparator').value = s.comparator;
      }
      if (s.outcome) {
        window.currentOutcome = s.outcome;
        const sel = document.getElementById('meta-outcome-select');
        if (sel && [...sel.options].some(o => o.value === s.outcome)) sel.value = s.outcome;
      }
      if (s.subgroup) {
        window.currentSubgroup = s.subgroup;
        const sel = document.getElementById('meta-subgroup-select');
        if (sel && [...sel.options].some(o => o.value === s.subgroup)) sel.value = s.subgroup;
      }
      window.focusStudyId = s.study || null;
      window.focusAnalysisId = s.analysis || null;
      if (s.rob) {
        const sel = document.getElementById('rob2-outcome-filter');
        if (sel && [...sel.options].some(o => o.value === s.rob)) sel.value = s.rob;
      }
      if (s.tab && document.getElementById(`tab-${s.tab}`)) {
        window.switchTab(s.tab);
      } else {
        window.renderActiveTab && window.renderActiveTab();
      }
    } finally {
      applyingUrl = false;
    }
    highlightFocus();
  }

  // ── evidence links ────────────────────────────────────────────────────────
  // Every saved analysis carries the same four routes out: who contributed, the
  // risk of bias for THIS result, the GRADE row for THIS synthesis, and the
  // dataset. Context travels with the link.
  function navigateTo(target) {
    const s = Object.assign(currentState(), target);
    applyingUrl = true;
    try {
      if (target.outcome) window.currentOutcome = target.outcome;
      if (target.modality) {
        window.filterModality = target.modality;
        const m = document.getElementById('filter-modality');
        if (m) m.value = target.modality;
      }
      if (target.comparator) {
        window.filterComparator = target.comparator;
        const c = document.getElementById('filter-comparator');
        if (c) c.value = target.comparator;
      }
      if (target.rob) {
        const sel = document.getElementById('rob2-outcome-filter');
        if (sel && [...sel.options].some(o => o.value === target.rob)) sel.value = target.rob;
      }
      window.focusStudyId = target.study || null;
      window.focusAnalysisId = target.analysis || null;
      window.switchTab(target.tab);
    } finally {
      applyingUrl = false;
    }
    window.history.pushState(s, '', buildHash(s));
    highlightFocus();
  }
  window.dashNavigate = navigateTo;

  function highlightFocus() {
    document.querySelectorAll('.evidence-focus').forEach(el => el.classList.remove('evidence-focus'));
    const id = window.focusAnalysisId;
    if (!id) return;
    const row = document.querySelector(`[data-analysis-id="${CSS.escape(id)}"]`);
    if (row) {
      row.classList.add('evidence-focus');
      row.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  }
  window.dashHighlightFocus = highlightFocus;

  function evidenceLinks(card) {
    const a = analysis(card.id);
    if (!a) return '';
    const modality = card.modality ? `&quot;${esc(card.modality)}&quot;` : 'null';
    const q = JSON.stringify({
      studies: { tab: 'explorer', outcome: card.robKey, analysis: card.id, modality: card.modality || null },
      rob: { tab: 'rob2', rob: card.robKey, analysis: card.id },
      grade: { tab: 'evidence', analysis: card.id }
    }).replace(/"/g, '&quot;');
    return `
      <div class="evidence-links" data-links='${q}'>
        <button type="button" class="evidence-link" data-route="studies">Contributing studies (k = ${esc(a.k)})</button>
        <button type="button" class="evidence-link" data-route="rob">Risk of bias for this result</button>
        <button type="button" class="evidence-link" data-route="grade">GRADE for this analysis</button>
        <a class="evidence-link" href="${esc(card.download)}" download>Download this analysis</a>
      </div>`;
  }

  function bindEvidenceLinks(root) {
    (root || document).querySelectorAll('.evidence-links').forEach(box => {
      let routes;
      try { routes = JSON.parse(box.getAttribute('data-links')); } catch (e) { return; }
      box.querySelectorAll('button.evidence-link').forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', () => {
          const r = routes[btn.getAttribute('data-route')];
          if (r) navigateTo(r);
        });
      });
    });
  }

  // ── findings-first hero ───────────────────────────────────────────────────
  function findingCard(card) {
    const a = analysis(card.id);
    if (!a) return '';
    const primary = card.role === 'primary';
    const sym = GRADE_SYMBOL[a.grade] || '';
    const pl = plainLanguage(a);
    return `
      <article class="finding-card ${primary ? 'finding-primary' : 'finding-supporting'}"
               data-analysis-id="${esc(card.id)}">
        <div class="finding-head">
          <span class="finding-role">${primary ? 'Primary finding' : 'Supporting analysis'}</span>
          <span class="finding-modality">${esc(a.modality || 'TEAS and EA combined')} vs ${esc(card.comparatorLabel || a.comparator || 'control')}</span>
        </div>
        <div class="finding-effect">${esc(a.mdText)}</div>
        <div class="finding-meta">
          <span>${esc(a.pVal)}</span>
          <span><span>${esc(a.k)}</span> <span>trials</span></span>
          <span><span>${esc(a.n)}</span> <span>participants</span></span>
          <span class="finding-grade ${esc(a.badgeClass || '')}"><span aria-hidden="true">${sym}</span> <span class="grade-word">${esc(a.grade)}</span> <span>certainty</span></span>
        </div>
        <p class="finding-plain"><span class="pl-subject">${esc(pl.subject)}</span> <span class="pl-body">${esc(pl.body)}</span></p>
        ${evidenceLinks(card)}
      </article>`;
  }

  // Plain-language reading of the saved estimate. It describes the interval that
  // Stata produced; it does not soften or strengthen it.
  function plainLanguage(a) {
    const crosses = /\[−?-?\d[^\]]*,\s*\+?\d/.test(a.mdText) &&
      /\[\s*−|\[\s*-/.test(a.mdText) && /,\s*\+/.test(a.mdText);
    return {
      subject: a.modality ? a.modality : 'The combined analysis',
      body: crosses
        ? 'used less opioid on average, but the confidence interval also includes no difference and an increase, so this does not demonstrate an opioid-sparing effect.'
        : 'showed a confidence interval that excludes no difference.'
    };
  }

  function renderFindingsHero() {
    const host = document.getElementById('findings-hero');
    if (!host || !window.STATA_MASTER_RESULTS) return;
    const teas = analysis('AN-01-TEAS');
    const ea = analysis('AN-01-EA');
    if (!teas || !ea) return;

    host.innerHTML = `
      <div class="finding-question">
        <h2 class="finding-q-title">Does perioperative TEAS or EA reduce opioid use after surgery?</h2>
        <dl class="finding-q-meta">
          <div><dt>Outcome</dt><dd>Cumulative postoperative opioid consumption</dd></div>
          <div><dt>Timepoint</dt><dd>0–24 hours after surgery</dd></div>
          <div><dt>Unit</dt><dd>mg intravenous morphine equivalents (IV MME)</dd></div>
          <div><dt>Model</dt><dd>Random effects, REML, Hartung–Knapp intervals</dd></div>
        </dl>
        <p class="finding-q-note">TEAS and EA are reported separately because they are different interventions
          tested against different comparators. Pooling them would average two different questions.</p>
      </div>
      <div class="finding-grid">${PRIMARY_CARDS.map(findingCard).join('')}</div>
      <div class="finding-supporting-wrap">${findingCard(SUPPORTING_CARD)}</div>
      <div class="finding-figures">
        <figure><img src="forest_subgroup_modality_primary.png" alt="Forest plot: 0-24 h opioid consumption by modality" loading="lazy">
          <figcaption>Primary outcome by modality (TEAS and EA shown separately).</figcaption></figure>
      </div>
      <p class="finding-more">Full contribution pathways, tier classification, sensitivity analyses,
        derivations and execution logs remain available in the sections below.</p>`;
    bindEvidenceLinks(host);
  }

  // ── overview GRADE card ───────────────────────────────────────────────────
  // The overview previously stated a single "Low" rating for the primary
  // outcome. The adjudicated assessments are modality-specific and differ, so
  // each certainty is shown against the synthesis it was made for.
  function renderGradeKpi() {
    const host = document.getElementById('kpi-grade-body');
    if (!host || !window.STATA_MASTER_RESULTS) return;
    const rows = [
      { id: 'AN-01-TEAS', label: 'TEAS vs sham' },
      { id: 'AN-01-EA', label: 'EA vs usual care' },
      { id: 'AN-01-COMB', label: 'Combined (supporting)' }
    ].map(r => {
      const a = analysis(r.id);
      return a ? { ...r, grade: a.grade, k: a.k } : null;
    }).filter(Boolean);
    if (!rows.length) return;

    host.innerHTML = rows.map(r => `
      <div class="kpi-grade-row" data-analysis-id="${esc(r.id)}">
        <span class="kpi-grade-label">${esc(r.label)} <span class="kpi-grade-k">k = ${esc(r.k)}</span></span>
        <span class="kpi-grade-val"><span aria-hidden="true">${GRADE_SYMBOL[r.grade] || ''}</span> <span class="grade-word">${esc(r.grade)}</span></span>
      </div>`).join('');
  }

  // ── coordinated outcome selection on Secondary Outcomes ───────────────────
  // The tab previously opened with a saved rescue-opioid analysis sitting above
  // an exploratory forest plot of the primary 24-hour opioid outcome -- two
  // unrelated results stacked as if they belonged together.
  //
  // The two selectors are now coordinated, but only where the estimands
  // genuinely correspond. A saved Stata analysis and a browser-side plot of the
  // "same" outcome can differ in study set and model, so a mapping is declared
  // only when the exploratory view answers the same question. Everything else
  // shows an explicit unavailable state instead of an unrelated plot.
  const SAVED_TO_EXPLORATORY = {
    V33_RESCUE_OPIOID_RR_24H: {
      outcome: 'rescue_analgesia',
      note: 'The exploratory plot uses the browser rescue-analgesia set, which is broader than ' +
            'the saved binary rescue-opioid model: it also contains non-opioid rescue. The two ' +
            'are related but not the same analysis.'
    },
    V33_INTRAOP_REMI_MD: {
      outcome: 'intraop_opioid',
      note: 'The exploratory plot covers intraoperative opioid generally; the saved analysis is ' +
            'remifentanil in µg only.'
    },
    V33_INTRAOP_REMI_SMD: {
      outcome: 'intraop_opioid',
      note: 'The saved analysis is the scale-free SMD of the same contrasts; the exploratory plot ' +
            'is on the raw scale.'
    },
    // No exploratory counterpart exists for these. Saying so is the honest
    // answer; showing a different outcome would not be.
    V33_INTRAOP_SUF_MD: {
      outcome: null,
      note: 'No exploratory browser plot covers intraoperative sufentanil. The exploratory ' +
            'intraoperative set is remifentanil-based and is a different drug, so it is not shown here.'
    },
    V33_QOR40_24H_MD: {
      outcome: null,
      note: 'No exploratory browser plot covers QoR-40. The saved Stata analysis is the only ' +
            'synthesis of this outcome.'
    },
    V33_GI_DEFECATION_MD: {
      outcome: null,
      note: 'No exploratory browser plot covers time to first defecation. The exploratory GI plot ' +
            'is time to first flatus, which is a different outcome.'
    }
  };

  // `sync` is true only when the reader changed the SAVED selector. On a plain
  // redraw the banner is refreshed but the exploratory selection is left alone:
  // forcing it on every render would silently override an outcome the reader
  // chose themselves, which is the opposite of coordinating the two.
  function coordinateSecondary(savedId, sync) {
    const panel = document.getElementById('tab-secondary');
    if (!panel) return;
    const expWrap = document.getElementById('exploratory-forest-wrap') ||
                    document.getElementById('meta-outcome-select')?.closest('.dashboard-card');
    let banner = document.getElementById('exploratory-coordination');
    if (!banner && expWrap) {
      banner = document.createElement('div');
      banner.id = 'exploratory-coordination';
      banner.className = 'coordination-banner';
      expWrap.insertBefore(banner, expWrap.firstChild);
    }
    if (!banner) return;

    const map = SAVED_TO_EXPLORATORY[savedId];
    const sel = document.getElementById('meta-outcome-select');
    const plot = expWrap.querySelector('.forest-table-wrap, table, svg')?.closest('div');

    if (map && map.outcome && sel && [...sel.options].some(o => o.value === map.outcome)) {
      if (sync && sel.value !== map.outcome) {
        sel.value = map.outcome;
        window.currentOutcome = map.outcome;
        if (typeof window.renderMetaLab === 'function') window.renderMetaLab();
      }
      const agrees = sel.value === map.outcome;
      banner.className = 'coordination-banner ' + (agrees ? 'coordination-matched' : '');
      banner.innerHTML = agrees
        ? `<strong>Exploratory browser calculation</strong> — recalculated live from the study data ` +
          `and matched to the saved analysis above. It is not the authoritative result. ` +
          `<span class="coordination-note">${esc(map.note)}</span>`
        : `<strong>Exploratory browser calculation</strong> — recalculated live in your browser. ` +
          `You have selected a different outcome from the saved analysis above, so the two do not ` +
          `correspond. <span class="coordination-note">${esc(map.note)}</span>`;
    } else if (map) {
      banner.className = 'coordination-banner coordination-unavailable';
      banner.innerHTML =
        `<strong>No matching exploratory analysis</strong> — ${esc(map.note)} ` +
        `The plot below is showing a different outcome and does not correspond to the saved ` +
        `analysis selected above.`;
    } else {
      banner.className = 'coordination-banner';
      banner.innerHTML =
        `<strong>Exploratory browser calculation</strong> — recalculated live in your browser from ` +
        `the study data. Saved Stata analyses above are the authoritative results.`;
    }
  }

  function initSecondaryCoordination() {
    const saved = document.getElementById('stata-secondary-select');
    if (!saved || saved.dataset.coordBound) return;
    saved.dataset.coordBound = '1';
    saved.addEventListener('change', () => coordinateSecondary(saved.value, true));
  }

  // ── section menu for long pages ───────────────────────────────────────────
  function renderSectionMenu() {
    const host = document.getElementById('section-menu');
    if (!host) return;
    const panel = document.querySelector('.tab-content.active');
    if (!panel) { host.hidden = true; return; }
    const marks = [...panel.querySelectorAll('[data-section]')];
    if (marks.length < 3) { host.hidden = true; host.innerHTML = ''; return; }
    host.hidden = false;
    host.innerHTML =
      `<span class="section-menu-label">On this page</span>` +
      marks.map(m => {
        const id = m.id || ('sec-' + m.getAttribute('data-section').replace(/\W+/g, '-').toLowerCase());
        m.id = id;
        return `<button type="button" class="section-menu-link" data-target="${esc(id)}">${esc(m.getAttribute('data-section'))}</button>`;
      }).join('');
    host.querySelectorAll('.section-menu-link').forEach(btn => {
      btn.addEventListener('click', () => {
        const el = document.getElementById(btn.getAttribute('data-target'));
        if (!el) return;
        const open = el.closest('details');
        if (open && !open.open) open.open = true;
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        el.setAttribute('tabindex', '-1');
        el.focus({ preventScroll: true });
      });
    });
  }

  // ── filter scope ──────────────────────────────────────────────────────────
  // Active filters are shown as removable chips so a reader can see at a glance
  // why a study count differs from 70 -- and so a persistent search restriction
  // cannot silently narrow a later view.
  function renderFilterChips() {
    const host = document.getElementById('filter-chips');
    if (!host) return;
    const chips = [];
    const add = (key, label, reset) => chips.push({ key, label, reset });
    if (window.filterModality && window.filterModality !== 'all') add('modality', `Modality: ${window.filterModality}`, () => { window.filterModality = 'all'; });
    if (window.filterComparator && window.filterComparator !== 'all') add('comparator', `Comparator: ${window.filterComparator}`, () => { window.filterComparator = 'all'; });
    if (window.filterSurgery && window.filterSurgery !== 'all') add('surgery', `Surgery: ${window.filterSurgery}`, () => { window.filterSurgery = 'all'; });
    if (window.filterRob && window.filterRob !== 'all') add('rob', `Risk of bias: ${window.filterRob}`, () => { window.filterRob = 'all'; });
    if (window.filterSearch) add('search', `Search: “${window.filterSearch}”`, () => {
      window.filterSearch = '';
      const i = document.getElementById('study-search-input'); if (i) i.value = '';
    });

    if (!chips.length) {
      host.hidden = true;
      host.innerHTML = '';
      return;
    }
    host.hidden = false;
    host.innerHTML =
      `<span class="filter-chips-label">Active filters</span>` +
      chips.map(c => `<button type="button" class="filter-chip" data-key="${esc(c.key)}">${esc(c.label)} <span aria-hidden="true">×</span></button>`).join('') +
      `<button type="button" class="filter-reset" id="filter-reset-all">Reset filters</button>`;

    chips.forEach(c => {
      const btn = host.querySelector(`.filter-chip[data-key="${c.key}"]`);
      if (btn) btn.addEventListener('click', () => { c.reset(); afterFilterChange(); });
    });
    const resetAll = host.querySelector('#filter-reset-all');
    if (resetAll) resetAll.addEventListener('click', () => {
      window.filterModality = 'all';
      window.filterComparator = 'all';
      window.filterSurgery = 'all';
      window.filterRob = 'all';
      window.filterSearch = '';
      const i = document.getElementById('study-search-input'); if (i) i.value = '';
      afterFilterChange();
    });
  }

  function afterFilterChange() {
    if (typeof window.syncToolbarDropdowns === 'function') window.syncToolbarDropdowns();
    if (typeof window.renderAllViews === 'function') window.renderAllViews();
    syncUrl(false);
  }

  // ── public entry point, called after every tab render ─────────────────────
  function refresh() {
    renderGradeKpi();
    if (window.activeTab === 'primary') renderFindingsHero();
    if (window.activeTab === 'secondary') {
      initSecondaryCoordination();
      const saved = document.getElementById('stata-secondary-select');
      if (saved) coordinateSecondary(saved.value, false);
    }
    renderSectionMenu();
    renderFilterChips();
    bindEvidenceLinks(document);
    highlightFocus();
    syncUrl(false);
  }
  window.dashRefreshUsability = refresh;

  // ── boot ──────────────────────────────────────────────────────────────────
  bootState = readUrl();
  window.addEventListener('popstate', () => { applyUrl(); });

  document.addEventListener('DOMContentLoaded', () => {
    // Wrap switchTab so every navigation pushes one history entry.
    const originalSwitch = window.switchTab;
    if (typeof originalSwitch === 'function' && !originalSwitch.__wrapped) {
      const wrapped = function (tabId) {
        const changing = tabId !== window.activeTab;
        originalSwitch.apply(this, arguments);
        refresh();
        if (changing && !applyingUrl) syncUrl(true);
      };
      wrapped.__wrapped = true;
      window.switchTab = wrapped;
    }
    refresh();
    window.addEventListener('languageChanged', refresh);
  });

  window.addEventListener('load', () => {
    booted = true;
    if (bootState && Object.keys(bootState).length) applyUrl(bootState);
    else refresh();
  });
})();
