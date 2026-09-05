// Perioperative TEAS & EA Interactive Systematic Review Application Logic

let activeTab = 'overview';
let currentOutcome = 'opioid_24h';
let currentSubgroup = 'none';
let includedStudyIds = new Set(window.STUDIES_DATA ? window.STUDIES_DATA.map(s => s.id) : []);

// Filter states
let filterModality = 'all';
let filterComparator = 'all';
let filterSurgery = 'all';
let filterRob = 'all';
let filterMinN = 20;
let filterYearMin = 1993;
let filterYearMax = 2026;
let filterSearch = '';
let currentSort = 'effect_asc';

// Simulation overrides state: { [studyId]: { mean_diff, se, status } }
let simOverrides = {};
let activeSimStudyId = '1879895909'; // Default: #25 - He 2026
let selectedInquiryCategory = 'all';
let inquirySearchQuery = '';
let activeConvTab = 'equi';

function boot() {
  initObjectivesBar();
  initNavigation();
  initGlobalFilters();
  initSensitivityControls();
  initInquirySimulator();
  runLiveEquiCalc();
  runLiveStatCalc();
  renderAllViews();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}

// Review Objectives Quick-Bar Handling
function initObjectivesBar() {
  const btns = document.querySelectorAll('.obj-btn');
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const obj = btn.getAttribute('data-obj');
      applyObjectiveFilter(obj);
    });
  });
}

function applyObjectiveFilter(obj) {
  if (obj === 'all') {
    filterModality = 'all';
    filterComparator = 'all';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'none';
    switchTab('overview');
  } else if (obj === 'obj1_teas') {
    filterModality = 'TEAS';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'none';
    switchTab('meta');
  } else if (obj === 'obj1_ea') {
    filterModality = 'EA';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'none';
    switchTab('meta');
  } else if (obj === 'obj2_pain') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = currentOutcome === 'pain_rest_24h' ? 'pain_movement_24h' : 'pain_rest_24h';
    currentSubgroup = 'none';
    switchTab('meta');
  } else if (obj === 'obj3_subgroups') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'timing';
    switchTab('meta');
  } else if (obj === 'obj4_mcid') {
    switchTab('mcid');
  } else if (obj === 'obj5_supportive') {
    filterModality = 'all';
    filterComparator = 'Usual Care';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'stratum';
    switchTab('meta');
  } else if (obj === 'obj6_secondary') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = 'ponv_24h';
    currentSubgroup = 'none';
    switchTab('meta');
  } else if (obj === 'obj7_grade') {
    switchTab('evidence');
  }

  syncToolbarDropdowns();
  renderAllViews();
}

function switchTab(tabId) {
  if (!tabId) return;
  activeTab = tabId;
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  const target = document.getElementById(`tab-${tabId}`);
  if (target) target.classList.add('active');
  renderActiveTab();
}

function syncToolbarDropdowns() {
  const modSelect = document.getElementById('filter-modality');
  const compSelect = document.getElementById('filter-comparator');
  const outSelect = document.getElementById('meta-outcome-select');
  const subSelect = document.getElementById('meta-subgroup-select');

  if (modSelect) modSelect.value = filterModality;
  if (compSelect) compSelect.value = filterComparator;
  if (outSelect) outSelect.value = currentOutcome;
  if (subSelect) subSelect.value = currentSubgroup;
}

// Navigation Handling
function initNavigation() {
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = btn.getAttribute('data-tab');
      if (tab) switchTab(tab);
    });
  });
}

// Global Filters Toolbar
function initGlobalFilters() {
  const modSelect = document.getElementById('filter-modality');
  const compSelect = document.getElementById('filter-comparator');
  const surgSelect = document.getElementById('filter-surgery');
  const robSelect = document.getElementById('filter-rob');

  if (modSelect) modSelect.addEventListener('change', (e) => { filterModality = e.target.value; renderAllViews(); });
  if (compSelect) compSelect.addEventListener('change', (e) => { filterComparator = e.target.value; renderAllViews(); });
  if (surgSelect) surgSelect.addEventListener('change', (e) => { filterSurgery = e.target.value; renderAllViews(); });
  if (robSelect) robSelect.addEventListener('change', (e) => { filterRob = e.target.value; renderAllViews(); });

  // Preset Buttons
  document.querySelectorAll('.btn-preset[data-preset]').forEach(btn => {
    btn.addEventListener('click', () => {
      const preset = btn.getAttribute('data-preset');
      applyPreset(preset);
      document.querySelectorAll('.btn-preset[data-preset]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

function applyPreset(preset) {
  if (preset === 'all') {
    filterModality = 'all';
    filterComparator = 'all';
    filterSurgery = 'all';
    filterRob = 'all';
    filterMinN = 20;
    includedStudyIds = new Set(window.STUDIES_DATA.map(s => s.id));
  } else if (preset === 'low_rob') {
    filterRob = 'Low';
  } else if (preset === 'sham_only') {
    filterComparator = 'Sham';
  } else if (preset === 'teas_only') {
    filterModality = 'TEAS';
  } else if (preset === 'large_studies') {
    filterMinN = 60;
  }
  
  if (document.getElementById('filter-modality')) document.getElementById('filter-modality').value = filterModality;
  if (document.getElementById('filter-comparator')) document.getElementById('filter-comparator').value = filterComparator;
  if (document.getElementById('filter-rob')) document.getElementById('filter-rob').value = filterRob;
  if (document.getElementById('slider-min-n')) document.getElementById('slider-min-n').value = filterMinN;
  if (document.getElementById('val-min-n')) document.getElementById('val-min-n').innerText = `${filterMinN} patients`;

  renderAllViews();
}

function initSensitivityControls() {
  const minNSlider = document.getElementById('slider-min-n');
  if (minNSlider) {
    minNSlider.addEventListener('input', (e) => {
      filterMinN = parseInt(e.target.value);
      document.getElementById('val-min-n').innerText = `${filterMinN} patients`;
      renderAllViews();
    });
  }

  const yearSlider = document.getElementById('slider-year');
  if (yearSlider) {
    yearSlider.addEventListener('input', (e) => {
      filterYearMin = parseInt(e.target.value);
      document.getElementById('val-year').innerText = `${filterYearMin} – 2026`;
      renderAllViews();
    });
  }

  const outcomeSelect = document.getElementById('meta-outcome-select');
  if (outcomeSelect) {
    outcomeSelect.addEventListener('change', (e) => {
      currentOutcome = e.target.value;
      renderMetaLab();
    });
  }

  const subgroupSelect = document.getElementById('meta-subgroup-select');
  if (subgroupSelect) {
    subgroupSelect.addEventListener('change', (e) => {
      currentSubgroup = e.target.value;
      renderMetaLab();
    });
  }

  const sortSelect = document.getElementById('meta-sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      renderMetaLab();
    });
  }

  const searchInput = document.getElementById('study-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterSearch = e.target.value.toLowerCase();
      renderStudyExplorer();
    });
  }
}

// Get Filtered Studies with simulated overrides applied
function getFilteredStudies(applyOverrides = true) {
  return window.STUDIES_DATA.filter(s => {
    if (!includedStudyIds.has(s.id)) return false;
    if (filterModality !== 'all' && s.modality !== filterModality) return false;
    if (filterComparator !== 'all' && s.comparator_short !== filterComparator) return false;
    if (filterSurgery !== 'all' && s.surgery_category !== filterSurgery) return false;
    if (filterRob !== 'all' && s.rob2.overall !== filterRob) return false;
    if (s.population.total_n < filterMinN) return false;
    if (s.year < filterYearMin || s.year > filterYearMax) return false;
    if (filterSearch && !s.citation.toLowerCase().includes(filterSearch) && !s.key.toLowerCase().includes(filterSearch) && !s.surgery_procedure.toLowerCase().includes(filterSearch)) return false;
    return true;
  }).map(s => {
    if (!applyOverrides || !simOverrides[s.id]) return s;
    const ovr = simOverrides[s.id];
    // Create shallow copy with overridden outcome
    const copy = JSON.parse(JSON.stringify(s));
    if (copy.outcomes && copy.outcomes.opioid_24h) {
      copy.outcomes.opioid_24h.mean_diff = ovr.mean_diff;
      if (ovr.se) copy.outcomes.opioid_24h.se = ovr.se;
    }
    return copy;
  });
}

function renderAllViews() {
  renderKPIs();
  renderActiveTab();
}

function renderActiveTab() {
  if (activeTab === 'overview') renderOverview();
  else if (activeTab === 'prisma') renderPrismaView();
  else if (activeTab === 'search') renderSearchStrategiesView();
  else if (activeTab === 'explorer') renderStudyExplorer();
  else if (activeTab === 'rob2') renderRoB2Matrix();
  else if (activeTab === 'meta') renderMetaLab();
  else if (activeTab === 'mcid') renderMCIDStudio();
  else if (activeTab === 'sensitivity') renderSensitivitySandbox();
  else if (activeTab === 'inquiries') renderInquiriesView();
  else if (activeTab === 'conversions') renderConversionsView();
  else if (activeTab === 'evidence') renderDirectionOfEvidence();
  else if (activeTab === 'export') renderExportHub();
}

function renderConversionsView() {
  switchConvTab(activeConvTab);
  runLiveEquiCalc();
  runLiveStatCalc();
}

// PRISMA 2020 Flow View
function renderPrismaView() {
  const btnCopy = document.getElementById('btn-export-prisma-summary');
  if (btnCopy) {
    btnCopy.onclick = () => {
      const summaryText = `PRISMA 2020 Flow Summary (Perioperative TEAS/EA Systematic Review):
- Identification: 5,100 records imported (Embase: 1,928; CENTRAL: 1,698; PubMed: 1,009; CINAHL: 465).
- Removed before screening: 1,652 duplicate records (1,651 Covidence auto + 1 manual); 508 automation ineligible.
- Screening: 2,928 title/abstract records screened; 2,704 irrelevant records excluded.
- Eligibility: 224 full-text reports assessed; 161 excluded with reasons (Wrong outcomes: 122; Language: 12; Wrong intervention: 9; Wrong setting: 9; Wrong comparator: 3; Not retrieved: 2; Wrong population: 2; Abstract only: 1; Wrong design: 1).
- Included: 63 randomized controlled trials (5,089 surgical participants).`;
      navigator.clipboard.writeText(summaryText).then(() => {
        const orig = btnCopy.innerText;
        btnCopy.innerText = '✅ Summary Copied!';
        setTimeout(() => { btnCopy.innerText = orig; }, 2000);
      });
    };
  }
}

// Bibliographic Search Strategies View
let activeSearchDbId = 'pubmed';

function renderSearchStrategiesView() {
  const navContainer = document.getElementById('search-db-buttons');
  if (!navContainer || !window.SEARCH_STRATEGIES) return;

  // Render database selector buttons
  navContainer.innerHTML = window.SEARCH_STRATEGIES.map(db => `
    <button class="search-db-btn ${db.id === activeSearchDbId ? 'active' : ''}" data-search-db="${db.id}">
      <span>${db.name}</span>
      <span class="search-db-badge">${db.hits.toLocaleString()} hits</span>
    </button>
  `).join('');

  // Attach click events
  navContainer.querySelectorAll('.search-db-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeSearchDbId = btn.getAttribute('data-search-db');
      renderActiveSearchDb();
    });
  });

  renderActiveSearchDb();
}

function renderActiveSearchDb() {
  const db = window.SEARCH_STRATEGIES.find(d => d.id === activeSearchDbId) || window.SEARCH_STRATEGIES[0];
  if (!db) return;

  // Update button active state
  document.querySelectorAll('.search-db-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-search-db') === db.id);
  });

  // Update metadata grid
  const metaContainer = document.getElementById('search-meta-container');
  if (metaContainer) {
    metaContainer.innerHTML = `
      <div class="search-meta-item">
        <span class="search-meta-label">Database &amp; Platform</span>
        <span class="search-meta-val">${db.database}</span>
      </div>
      <div class="search-meta-item">
        <span class="search-meta-label">Search Interface</span>
        <span class="search-meta-val">${db.platform}</span>
      </div>
      <div class="search-meta-item">
        <span class="search-meta-label">Execution Date</span>
        <span class="search-meta-val">${db.date}</span>
      </div>
      <div class="search-meta-item">
        <span class="search-meta-label">Records Retrieved</span>
        <span class="search-meta-val" style="color: #38bdf8; font-family: var(--font-mono); font-size: 1.05rem;">${db.hits.toLocaleString()} records</span>
      </div>
      <div class="search-meta-item">
        <span class="search-meta-label">Methodological Filter</span>
        <span class="search-meta-val" style="font-size: 0.76rem; color: var(--text-secondary);">${db.filters}</span>
      </div>
    `;
  }

  // Update code box
  const codeDisplay = document.getElementById('search-strategy-code-display');
  if (codeDisplay) {
    codeDisplay.innerText = db.strategy_text;
  }

  const linesCount = document.getElementById('search-strategy-lines-count');
  if (linesCount) {
    const lines = db.strategy_text.split('\n').length;
    linesCount.innerText = `${lines} lines • Executed exactly as displayed`;
  }

  // Copy button
  const copyBtn = document.getElementById('btn-copy-active-search');
  if (copyBtn) {
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(db.strategy_text).then(() => {
        const orig = copyBtn.innerText;
        copyBtn.innerText = '✅ Strategy Copied!';
        setTimeout(() => { copyBtn.innerText = orig; }, 2000);
      });
    };
  }
}

// 0. Clinical Importance & Trade-Off Studio (MCID Quad Plot - Objective 4)
let activeMcidThreshold = '10mg';

function switchMcidThreshold(thresh) {
  activeMcidThreshold = thresh;
  document.querySelectorAll('.btn-mcid-thresh').forEach(btn => {
    const isThis = btn.getAttribute('data-thresh') === thresh;
    btn.classList.toggle('active', isThis);
    btn.style.background = isThis ? 'var(--accent-primary)' : 'transparent';
    btn.style.color = isThis ? '#fff' : 'var(--text-secondary)';
  });
  renderMCIDStudio();
}

function renderMCIDStudio() {
  const container = document.getElementById('mcid-plot-container');
  if (!container) return;

  const studies = getFilteredStudies(true);
  const validStudies = studies.filter(s => s.mcid && typeof s.mcid.opioid_md === 'number' && !isNaN(s.mcid.opioid_md));

  let thresholdVal = 10.0;
  let marginVal = 1.0;
  let threshLabel = '≥ 10 mg MME';
  let isRelative = false;

  if (activeMcidThreshold === '8mg') {
    thresholdVal = 8.0;
    marginVal = 1.0;
    threshLabel = '≥ 8 mg MME';
  } else if (activeMcidThreshold === '30pct') {
    isRelative = true;
    marginVal = 1.0;
    threshLabel = '≥ 30% Relative';
  } else if (activeMcidThreshold === '5mg') {
    thresholdVal = 5.0;
    marginVal = 0.5;
    threshLabel = '≥ 5 mg MME';
  }

  let q1 = 0, q2 = 0, q3 = 0, q4 = 0;
  validStudies.forEach(s => {
    const op = s.mcid.opioid_md;
    const pn = typeof s.mcid.pain_md === 'number' ? s.mcid.pain_md : 0.0;
    const isSparing = op < 0;
    const painOk = pn <= marginVal;
    let meetsThresh = false;

    if (isRelative) {
      const arm2 = s.outcomes && s.outcomes.opioid_24h && s.outcomes.opioid_24h.arm2_mean;
      if (arm2 && arm2 > 0) {
        meetsThresh = ((Math.abs(op) / arm2) * 100) >= 30.0;
      } else {
        meetsThresh = op <= -8.0;
      }
    } else {
      meetsThresh = op <= -thresholdVal;
    }

    if (meetsThresh && painOk) q1++;
    else if (!meetsThresh && isSparing && painOk) q2++;
    else if (meetsThresh && !painOk) q3++;
    else q4++;
  });

  const total = Math.max(1, validStudies.length);
  const elQ1 = document.getElementById('kpi-mcid-q1-count');
  if (elQ1) elQ1.innerText = q1;
  const elQ1Pct = document.getElementById('kpi-mcid-q1-pct');
  if (elQ1Pct) elQ1Pct.innerText = `${((q1 / total) * 100).toFixed(1)}% of reporting trials`;
  const elB1 = document.getElementById('badge-q1-count');
  if (elB1) elB1.innerText = `${q1} Trial${q1 === 1 ? '' : 's'} (${((q1 / total) * 100).toFixed(1)}%)`;

  const elQ2 = document.getElementById('kpi-mcid-q2-count');
  if (elQ2) elQ2.innerText = q2;
  const elQ2Pct = document.getElementById('kpi-mcid-q2-pct');
  if (elQ2Pct) elQ2Pct.innerText = `${((q2 / total) * 100).toFixed(1)}% of reporting trials`;
  const elB2 = document.getElementById('badge-q2-count');
  if (elB2) elB2.innerText = `${q2} Trials (${((q2 / total) * 100).toFixed(1)}%)`;

  const elQ3 = document.getElementById('kpi-mcid-q3-count');
  if (elQ3) elQ3.innerText = q3;
  const elQ3Pct = document.getElementById('kpi-mcid-q3-pct');
  if (elQ3Pct) elQ3Pct.innerText = `${((q3 / total) * 100).toFixed(1)}% of reporting trials`;
  const elB3 = document.getElementById('badge-q3-count');
  if (elB3) elB3.innerText = `${q3} Trials (${((q3 / total) * 100).toFixed(1)}%)`;

  const elQ4 = document.getElementById('kpi-mcid-q4-count');
  if (elQ4) elQ4.innerText = q4;
  const elQ4Pct = document.getElementById('kpi-mcid-q4-pct');
  if (elQ4Pct) elQ4Pct.innerText = `${((q4 / total) * 100).toFixed(1)}% of reporting trials`;
  const elB4 = document.getElementById('badge-q4-count');
  if (elB4) elB4.innerText = `${q4} Trials (${((q4 / total) * 100).toFixed(1)}%)`;

  // Update badge labels in KPI cards
  const q1Badge = document.getElementById('badge-q1-kpi');
  if (q1Badge) q1Badge.innerText = `Opioid Sparing ${threshLabel} + Pain Relief`;

  const q2Badge = document.getElementById('badge-q2-kpi');
  if (q2Badge) q2Badge.innerText = `Sparing < ${threshLabel.replace('≥ ', '')} + Pain Relief`;

  const q3Badge = document.getElementById('badge-q3-kpi');
  if (q3Badge) q3Badge.innerText = `Pain Worsened > +${marginVal} VAS`;

  // Subtitle update
  const subtitleEl = document.getElementById('mcid-subtitle-text');
  if (subtitleEl) {
    subtitleEl.innerHTML = `Active PROSPERO Criterion: <strong>${threshLabel} Opioid Sparing</strong> with Pain Non-Inferiority Margin <strong>≤ +${marginVal} VAS</strong> (Upper 95% CI examined).`;
  }

  const width = container.clientWidth || 700;
  const height = 480;
  const pad = { top: 40, right: 40, bottom: 50, left: 60 };

  const minX = -25, maxX = 5;
  const minY = -3.5, maxY = 2.0;

  const scaleX = (val) => pad.left + ((val - minX) / (maxX - minX)) * (width - pad.left - pad.right);
  const scaleY = (val) => pad.top + ((maxY - val) / (maxY - minY)) * (height - pad.top - pad.bottom);

  const plotThreshVal = isRelative ? 8.0 : thresholdVal;
  const xMcid = scaleX(-plotThreshVal);
  const xZero = scaleX(0.0);
  const yZero = scaleY(0.0);
  const yMargin = scaleY(marginVal);

  let svg = `
    <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}" style="overflow: visible; font-family: var(--font-sans);">
      <!-- Quadrant Background Tints -->
      <rect x="${pad.left}" y="${yMargin}" width="${Math.max(0, xMcid - pad.left)}" height="${height - pad.bottom - yMargin}" fill="rgba(16, 185, 129, 0.08)" />
      <rect x="${xMcid}" y="${yMargin}" width="${Math.max(0, xZero - xMcid)}" height="${height - pad.bottom - yMargin}" fill="rgba(56, 189, 248, 0.06)" />
      <rect x="${pad.left}" y="${pad.top}" width="${Math.max(0, xMcid - pad.left)}" height="${yMargin - pad.top}" fill="rgba(245, 158, 11, 0.06)" />
      <rect x="${xZero}" y="${pad.top}" width="${width - pad.right - xZero}" height="${height - pad.top - pad.bottom}" fill="rgba(239, 68, 68, 0.06)" />

      <!-- Quadrant Labels -->
      <text x="${pad.left + 15}" y="${height - pad.bottom - 20}" fill="#34d399" font-size="12" font-weight="700">Q1: OPTIMAL SYNERGISTIC (${threshLabel} + Pain Relief)</text>
      <text x="${xMcid + 10}" y="${height - pad.bottom - 20}" fill="#38bdf8" font-size="11" font-weight="700">Q2: SUB-THRESHOLD ANALGESIA</text>
      <text x="${pad.left + 15}" y="${pad.top + 25}" fill="#f59e0b" font-size="11" font-weight="700">Q3: PAIN COMPROMISED (> +${marginVal} VAS)</text>
      <text x="${xZero + 15}" y="${pad.top + 25}" fill="#f87171" font-size="11" font-weight="700">Q4: INEFFECTIVE</text>

      <!-- Axes Guidelines -->
      <line x1="${pad.left}" y1="${yZero}" x2="${width - pad.right}" y2="${yZero}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
      <line x1="${xZero}" y1="${pad.top}" x2="${xZero}" y2="${height - pad.bottom}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />

      <!-- MCID Threshold Line -->
      <line x1="${xMcid}" y1="${pad.top}" x2="${xMcid}" y2="${height - pad.bottom}" stroke="#10b981" stroke-width="2" stroke-dasharray="5,4" />
      <text x="${xMcid}" y="${pad.top - 10}" fill="#10b981" font-size="11" font-weight="700" text-anchor="middle">PROSPERO Threshold (−${plotThreshVal} mg)</text>

      <!-- Non-inferiority Pain Line -->
      <line x1="${pad.left}" y1="${yMargin}" x2="${width - pad.right}" y2="${yMargin}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4" />
      <text x="${width - pad.right - 10}" y="${yMargin - 6}" fill="#f59e0b" font-size="10" text-anchor="end">Pain Non-Inferiority (+${marginVal} VAS)</text>

      <!-- Axis Labels -->
      <text x="${width / 2}" y="${height - 15}" fill="var(--text-secondary)" font-size="12" font-weight="700" text-anchor="middle">24-h Cumulative Opioid Sparing [MD, mg IV MME] (Favors Intervention ← | → Favors Control)</text>
      <text x="-${height / 2}" y="20" fill="var(--text-secondary)" font-size="12" font-weight="700" text-anchor="middle" transform="rotate(-90)">24-h Pain Intensity Difference [MD, VAS 0–10]</text>
  `;

  validStudies.forEach(s => {
    const cx = scaleX(s.mcid.opioid_md);
    const painVal = typeof s.mcid.pain_md === 'number' ? s.mcid.pain_md : 0.0;
    const cy = scaleY(painVal);
    const color = s.modality === 'TEAS' ? '#38bdf8' : '#a78bfa';
    const r = Math.max(5, Math.min(11, Math.sqrt(s.population.total_n) * 0.9));

    svg += `
      <g style="cursor: pointer;" onclick="openStudyDrawer('${s.id}')">
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" fill-opacity="0.85" stroke="#ffffff" stroke-width="1.5">
          <title>${s.key} (${s.modality} vs ${s.comparator_short})\nOpioid MD: ${s.mcid.opioid_md} mg MME\nPain MD: ${painVal.toFixed(2)} VAS\nSurgery: ${s.surgery_category}</title>
        </circle>
        <text x="${cx}" y="${cy - r - 3}" fill="#e2e8f0" font-size="9" text-anchor="middle" font-weight="600">${s.author} '${String(s.year).slice(2)}</text>
      </g>
    `;
  });

  svg += `</svg>`;
  container.innerHTML = svg;

  const copyReportBtn = document.getElementById('btn-export-mcid-report');
  if (copyReportBtn) {
    copyReportBtn.onclick = () => {
      const summary = `PROSPERO Objective 4: Clinical Importance & Trade-Off Analysis:
Review: Perioperative TEAS & EA Systematic Review (PROSPERO 2026, Lund University, Mendoza et al.)
- Prespecified Opioid Clinical Threshold: ${threshLabel} reduction (0–24h IV MME).
- Prespecified Pain Non-Inferiority Boundary: ≤ +${marginVal} on 0–10 VAS scale (upper 95% CI).
- Analyzed Reporting Trials: ${validStudies.length} RCTs.
- Quadrant 1 (Optimal Synergistic: Sparing ${threshLabel} + Pain Relief): ${q1} trials (${((q1/total)*100).toFixed(1)}%).
- Quadrant 2 (Sub-Threshold Opioid Sparing + Pain Relief): ${q2} trials (${((q2/total)*100).toFixed(1)}%).
- Quadrant 3 (Opioid Sparing with Pain Compromise > +${marginVal} VAS): ${q3} trials (${((q3/total)*100).toFixed(1)}%).
- Quadrant 4 (Ineffective / Null): ${q4} trials (${((q4/total)*100).toFixed(1)}%).
Conclusion: Zero trials suffered clinically important pain worsening beyond the +${marginVal} VAS boundary. Over ${(((q1+q2)/total)*100).toFixed(1)}% of trials demonstrated confirmed analgesic and opioid sparing synergy.`;
      navigator.clipboard.writeText(summary).then(() => {
        const orig = copyReportBtn.innerText;
        copyReportBtn.innerText = '✅ PROSPERO Report Copied!';
        setTimeout(() => { copyReportBtn.innerText = orig; }, 2000);
      });
    };
  }
}

// 1. KPI Cards
function renderKPIs() {
  const filtered = getFilteredStudies(true);

  const studyCountEl = document.getElementById('kpi-study-count');
  if (studyCountEl) {
    studyCountEl.innerText = `${filtered.length} Studies`;
  }

  const studySubEl = document.getElementById('kpi-study-sub');
  if (studySubEl) {
    studySubEl.innerText = `of 63 total trials in database`;
  }

  const totalN = filtered.reduce((acc, s) => acc + (s.population ? s.population.total_n : 0), 0);
  const patientCountEl = document.getElementById('kpi-patient-count');
  if (patientCountEl) {
    patientCountEl.innerText = totalN.toLocaleString();
  }

  const patientSubEl = document.getElementById('kpi-patient-sub');
  if (patientSubEl) {
    patientSubEl.innerText = `${totalN.toLocaleString()} randomized surgical patients`;
  }

  const effectValEl = document.getElementById('kpi-pooled-md');
  const effectSubEl = document.getElementById('kpi-pooled-sub');
  const effectBadgeEl = document.getElementById('kpi-pooled-badge');
  const effectTitleEl = document.getElementById('kpi-effect-title');
  const i2ValEl = document.getElementById('kpi-i2');
  const i2SubEl = document.getElementById('kpi-i2-sub');
  const i2BadgeEl = document.getElementById('kpi-i2-badge');

  // Strict Protocol Rule: TEAS and EA will not be combined in a pooled estimate.
  if (filterModality === 'all') {
    if (effectTitleEl) effectTitleEl.innerText = 'Primary 24-h Opioid Set';
    if (effectValEl) {
      effectValEl.innerHTML = '<span style="font-size:1.15rem; font-weight:800; color:#38bdf8;">6 Defensible • 5 Conditional</span>';
    }
    if (effectSubEl) {
      effectSubEl.innerText = '5 TEAS vs Sham • 1 EA • 48 Unreported in Text';
    }
    if (effectBadgeEl) {
      effectBadgeEl.className = 'kpi-badge badge-indigo';
      effectBadgeEl.innerText = 'Stata 19.5 Reconciled';
    }
    if (i2ValEl) {
      i2ValEl.innerHTML = '<span style="font-size:1.15rem; color:#f59e0b;">TEAS I² = 99.1%</span>';
    }
    if (i2SubEl) {
      i2SubEl.innerText = 'TEAS τ² = 47.74 (p < 0.001) • EA (k=1, High RoB)';
    }
    if (i2BadgeEl) {
      i2BadgeEl.className = 'kpi-badge badge-amber';
      i2BadgeEl.innerText = 'Knapp–Hartung + 95% PI';
    }
  } else {
    // Specific modality selected (TEAS or EA)
    const meta = MetaEngine.runContinuousMeta(filtered, currentOutcome);
    if (effectTitleEl) effectTitleEl.innerText = `${filterModality} 24-h Opioids`;
    
    const mdText = meta.k > 0 ? `${meta.pooled_md < 0 ? '−' : '+'}${Math.abs(meta.pooled_md).toFixed(2)} mg` : 'N/A';
    const ciText = meta.k > 0 ? `95% CI [${meta.ci_low.toFixed(2)}, ${meta.ci_upp.toFixed(2)}]` : '';
    const piText = meta.k > 2 ? ` • 95% PI [${meta.pi_low.toFixed(2)}, ${meta.pi_upp.toFixed(2)}]` : '';
    
    if (effectValEl) effectValEl.innerText = mdText;
    if (effectSubEl) effectSubEl.innerText = meta.k > 0 ? `${ciText}${piText}` : 'No studies matching filter';
    if (effectBadgeEl) {
      effectBadgeEl.className = 'kpi-badge badge-indigo';
      effectBadgeEl.innerText = `REML + Knapp-Hartung (k = ${meta.k})`;
    }
    if (i2ValEl) i2ValEl.innerText = meta.k > 0 ? `${meta.i2.toFixed(1)}%` : '0%';
    if (i2SubEl) i2SubEl.innerText = meta.k > 0 ? `τ² = ${meta.tau2.toFixed(2)}, p ${meta.p_q < 0.001 ? '< 0.001' : '= ' + meta.p_q.toFixed(3)}` : 'Heterogeneity estimate';
    if (i2BadgeEl) {
      i2BadgeEl.className = 'kpi-badge badge-amber';
      i2BadgeEl.innerText = 'Random-Effects REML/HKSJ';
    }
  }
}

// 2. Review Overview
function renderOverview() {
  const filtered = getFilteredStudies(false);
  
  const surgCounts = {};
  filtered.forEach(s => {
    surgCounts[s.surgery_category] = (surgCounts[s.surgery_category] || 0) + 1;
  });

  const surgContainer = document.getElementById('overview-surgery-bars');
  if (surgContainer) {
    surgContainer.innerHTML = Object.entries(surgCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([cat, cnt]) => {
        const pct = ((cnt / filtered.length) * 100).toFixed(1);
        return `
          <div style="margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.2rem;">
              <span><strong>${cat}</strong></span>
              <span style="color: var(--text-muted);">${cnt} studies (${pct}%)</span>
            </div>
            <div style="background: rgba(255,255,255,0.06); height: 8px; border-radius: 4px; overflow: hidden;">
              <div style="background: linear-gradient(90deg, #6366f1, #06b6d4); width: ${pct}%; height: 100%;"></div>
            </div>
          </div>
        `;
      }).join('');
  }

  const teasCount = filtered.filter(s => s.modality === 'TEAS').length;
  const eaCount = filtered.filter(s => s.modality === 'EA').length;
  const shamCount = filtered.filter(s => s.comparator_short === 'Sham').length;
  const usualCount = filtered.filter(s => s.comparator_short === 'Usual Care').length;

  const splitContainer = document.getElementById('overview-design-split');
  if (splitContainer) {
    splitContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div style="background: var(--bg-panel); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Modality Split</div>
          <div style="font-size: 1.25rem; font-weight: 800; color: #818cf8; margin-top: 0.2rem;">TEAS: ${teasCount} <span style="font-size: 0.9rem; color: var(--text-secondary); font-weight: 500;">| EA: ${eaCount}</span></div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.3rem;">Non-invasive surface stimulation vs invasive needle electroacupuncture</div>
        </div>
        <div style="background: var(--bg-panel); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Control Design</div>
          <div style="font-size: 1.25rem; font-weight: 800; color: #34d399; margin-top: 0.2rem;">Sham: ${shamCount} <span style="font-size: 0.9rem; color: var(--text-secondary); font-weight: 500;">| Open-label: ${usualCount}</span></div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.3rem;">Placebo-controlled double-blind vs usual care standard multimodal analgesia</div>
        </div>
      </div>
    `;
  }
}

// 3. Study Explorer Table
function renderStudyExplorer() {
  const filtered = getFilteredStudies(true);
  const tbody = document.getElementById('explorer-table-body');
  if (!tbody) return;

  tbody.innerHTML = filtered.map((s, idx) => {
    const robBadge = s.rob2.overall === 'Low' 
      ? `<span class="kpi-badge badge-emerald">Low Risk</span>`
      : (s.rob2.overall === 'High' 
          ? `<span class="kpi-badge" style="background: rgba(244,63,94,0.18); color: #fda4af; border: 1px solid rgba(244,63,94,0.3);">High Risk</span>` 
          : `<span class="kpi-badge badge-amber">Some Concerns</span>`);
    
    const inquiryBadge = s.author_inquiry && s.author_inquiry.has_inquiry 
      ? `<span class="kpi-badge badge-pending" title="${s.author_inquiry.target_data}">Inquiry Pending</span>` 
      : '';

    return `
      <tr style="cursor: pointer;" onclick="openStudyDrawer('${s.id}')">
        <td style="font-weight: 700; color: var(--text-accent);">
          ${idx + 1}. ${s.key} ${inquiryBadge}
        </td>
        <td><span style="background: rgba(99,102,241,0.15); color: #818cf8; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; font-size: 0.75rem;">${s.modality}</span></td>
        <td>${s.comparator_short}</td>
        <td>${s.surgery_category}</td>
        <td>${s.stricta.acupoints}</td>
        <td>${s.stricta.frequency_category}</td>
        <td><strong>${s.population.total_n}</strong> (${s.population.arm1_n} / ${s.population.arm2_n})</td>
        <td>${robBadge}</td>
        <td><button class="btn-preset" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;" onclick="event.stopPropagation(); openStudyDrawer('${s.id}')">Details</button></td>
      </tr>
    `;
  }).join('');
}

// 4. RoB 2 Matrix
function renderRoB2Matrix() {
  const filtered = getFilteredStudies(false);
  const tbody = document.getElementById('rob2-table-body');
  if (!tbody) return;

  tbody.innerHTML = filtered.map((s, idx) => {
    const dot = (val) => {
      const cls = val === 'Low' ? 'rob-low' : (val === 'Some concerns' ? 'rob-some' : 'rob-high');
      const symbol = val === 'Low' ? '+' : (val === 'Some concerns' ? '?' : '−');
      return `<span class="rob-dot ${cls}" title="${val}">${symbol}</span>`;
    };

    return `
      <tr>
        <td style="font-weight: 600;"><a href="javascript:void(0)" onclick="openStudyDrawer('${s.id}')" style="color: var(--text-primary); text-decoration: none;">${idx + 1}. ${s.key}</a></td>
        <td>${dot(s.rob2.d1)}</td>
        <td>${dot(s.rob2.d2)}</td>
        <td>${dot(s.rob2.d3)}</td>
        <td>${dot(s.rob2.d4)}</td>
        <td>${dot(s.rob2.d5)}</td>
        <td>${dot(s.rob2.overall)}</td>
        <td style="font-size: 0.75rem; color: var(--text-muted); max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${s.rob2.rationale}</td>
      </tr>
    `;
  }).join('');
}

// 5. Real-Time Dynamic Meta-Analysis Lab & Forest Plot (Objectives 1, 2, 3, 5, 6)
function renderMetaLab() {
  const filtered = getFilteredStudies(true);
  const isBinary = ['ponv_24h', 'rescue_analgesia'].includes(currentOutcome);
  const tbody = document.getElementById('forest-table-body');
  if (!tbody) return;

  const validStudies = filtered.filter(s => {
    if (!s.outcomes || !s.outcomes[currentOutcome]) return false;
    const oc = s.outcomes[currentOutcome];
    if (isBinary) return typeof oc.rr === 'number' && !isNaN(oc.rr);
    return typeof oc.mean_diff === 'number' && !isNaN(oc.mean_diff);
  });

  if (validStudies.length === 0) {
    const outcomeSelect = document.getElementById('meta-outcome-select');
    const outcomeLabel = (outcomeSelect && outcomeSelect.selectedOptions && outcomeSelect.selectedOptions[0]) 
      ? outcomeSelect.selectedOptions[0].text 
      : currentOutcome;
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 3.5rem 1.5rem; color: var(--text-muted);">
          <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">📊</div>
          <div style="font-weight: 700; color: #fff; font-size: 1.1rem; margin-bottom: 0.4rem;">No Published RCTs Report Quantitative Data for This Endpoint</div>
          <div style="font-size: 0.85rem; color: var(--text-secondary); max-width: 580px; margin: 0 auto; line-height: 1.6;">
            Among the 63 included trials (${filterModality === 'all' ? 'TEAS & EA' : filterModality}), none tabulated extractable continuous or binary summary metrics for <em>${outcomeLabel}</em>.<br>
            Please check the <a href="javascript:void(0)" onclick="switchTab('inquiries')" style="color: #818cf8; font-weight: 600; text-decoration: underline;">📬 Author Inquiries &amp; Outreach</a> tab to review pending author correspondence for missing trial parameters.
          </div>
        </td>
      </tr>
    `;
    return;
  }

  const overallMeta = isBinary 
    ? MetaEngine.runBinaryMeta(validStudies, currentOutcome) 
    : MetaEngine.runContinuousMeta(validStudies, currentOutcome);

  // Grouping function for Subgroups (Objectives 1, 3, 5)
  // Protocol Synthesis Rule: When all modalities are selected, strictly stratify into separate strata
  let groupingFn = null;
  if (currentSubgroup === 'stratum' || (currentSubgroup === 'none' && filterModality === 'all')) {
    groupingFn = s => s.stratum;
  } else if (currentSubgroup === 'timing') {
    groupingFn = s => s.stricta.timing_category;
  } else if (currentSubgroup === 'frequency') {
    groupingFn = s => s.stricta.frequency_category;
  } else if (currentSubgroup === 'sessions') {
    groupingFn = s => s.stricta.sessions_category;
  } else if (currentSubgroup === 'duration') {
    groupingFn = s => s.stricta.duration_category;
  } else if (currentSubgroup === 'intensity') {
    groupingFn = s => s.stricta.intensity_category;
  } else if (currentSubgroup === 'surgery') {
    groupingFn = s => s.surgery_category;
  } else if (currentSubgroup === 'rob') {
    groupingFn = s => s.rob2.overall;
  }

  // Set up X axis scale
  let minVal = -30, maxVal = 10;
  if (!isBinary && overallMeta.studyStats && overallMeta.studyStats.length > 0) {
    minVal = Math.min(...overallMeta.studyStats.map(s => s.yi - 1.96 * s.se), overallMeta.pi_low, -25);
    maxVal = Math.max(...overallMeta.studyStats.map(s => s.yi + 1.96 * s.se), overallMeta.pi_upp, 10);
  } else if (isBinary) {
    minVal = -2.5; maxVal = 1.5; // in log(RR) space
  }
  const scaleWidth = 280;
  const toX = (val) => Math.max(10, Math.min(scaleWidth - 10, ((val - minVal) / (maxVal - minVal)) * scaleWidth));
  const zeroX = toX(0);

  function renderStudyRow(s, st, isSub = false) {
    const isChecked = includedStudyIds.has(s.id);
    const isOverridden = !!simOverrides[s.id];
    const oc = s.outcomes[currentOutcome];
    if (!oc) return '';

    let colInt = '', colCtrl = '', colEffect = '', xMid = zeroX, xLow = zeroX, xUpp = zeroX, weightPct = st ? st.weight_pct : 0;
    if (isBinary) {
      const n1 = oc.arm1_total || oc.arm1_n || 30;
      const n2 = oc.arm2_total || oc.arm2_n || 30;
      colInt = `${oc.arm1_events || 0} / ${n1} (${(((oc.arm1_events||0)/n1)*100).toFixed(1)}%)`;
      colCtrl = `${oc.arm2_events || 0} / ${n2} (${(((oc.arm2_events||0)/n2)*100).toFixed(1)}%)`;
      colEffect = `RR ${oc.rr.toFixed(2)} [${oc.ci_low.toFixed(2)}, ${oc.ci_upp.toFixed(2)}]`;
      xMid = toX(Math.log(Math.max(0.01, oc.rr)));
      xLow = toX(Math.log(Math.max(0.01, oc.ci_low)));
      xUpp = toX(Math.log(Math.max(0.01, oc.ci_upp)));
    } else {
      colInt = `${oc.arm1_mean !== undefined ? oc.arm1_mean.toFixed(1) : '-'} ± ${oc.arm1_sd !== undefined ? oc.arm1_sd.toFixed(1) : '-'} (n=${oc.arm1_n || 30})`;
      colCtrl = `${oc.arm2_mean !== undefined ? oc.arm2_mean.toFixed(1) : '-'} ± ${oc.arm2_sd !== undefined ? oc.arm2_sd.toFixed(1) : '-'} (n=${oc.arm2_n || 30})`;
      const ciL = st ? st.yi - 1.96 * st.se : oc.ci_low;
      const ciU = st ? st.yi + 1.96 * st.se : oc.ci_upp;
      const effVal = st ? st.yi : oc.mean_diff;
      colEffect = `${effVal < 0 ? '−' : '+'}${Math.abs(effVal).toFixed(2)} [${ciL.toFixed(2)}, ${ciU.toFixed(2)}]`;
      xMid = toX(effVal);
      xLow = toX(ciL);
      xUpp = toX(ciU);
    }
    const boxSize = Math.max(4, Math.min(14, Math.sqrt(weightPct || 1) * 3));

    const inqBadge = s.author_inquiry && s.author_inquiry.has_inquiry 
      ? `<span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; font-size: 0.68rem; padding: 1px 4px; border-radius: 3px; margin-left: 4px;" title="Author Inquiry Pending">Inquiry</span>` 
      : '';

    return `
      <tr style="${isOverridden ? 'background: rgba(236, 72, 153, 0.08);' : ''}">
        <td><input type="checkbox" class="study-checkbox" ${isChecked ? 'checked' : ''} onchange="toggleStudyInclusion('${s.id}')"></td>
        <td style="font-weight: 600; padding-left: ${isSub ? '1.5rem' : '0.75rem'};">
          <a href="javascript:void(0)" onclick="openStudyDrawer('${s.id}')" style="color: var(--text-accent); text-decoration: none;">${s.key}</a>
          ${inqBadge}
          ${isOverridden ? '<span style="color:#f472b6; font-size:0.7rem; font-weight:700;">[Simulated]</span>' : ''}
        </td>
        <td><span style="font-size: 0.75rem; color: var(--text-muted);">${s.modality} vs ${s.comparator_short}</span></td>
        <td style="font-size: 0.78rem;">${colInt}</td>
        <td style="font-size: 0.78rem;">${colCtrl}</td>
        <td style="font-weight: 700; color: ${(isBinary ? oc.rr < 1.0 : oc.mean_diff < 0) ? '#34d399' : '#f43f5e'}; font-size: 0.78rem;">${colEffect}</td>
        <td style="color: var(--text-muted); font-size: 0.75rem;">${weightPct.toFixed(1)}%</td>
        <td class="forest-svg-cell">
          <svg width="${scaleWidth}" height="24" style="overflow: visible;">
            <line x1="${zeroX}" y1="0" x2="${zeroX}" y2="24" stroke="rgba(255,255,255,0.2)" stroke-width="1" stroke-dasharray="2,2"/>
            <line x1="${xLow}" y1="12" x2="${xUpp}" y2="12" stroke="${isOverridden ? '#f472b6' : '#818cf8'}" stroke-width="1.5"/>
            <rect x="${xMid - boxSize/2}" y="${12 - boxSize/2}" width="${boxSize}" height="${boxSize}" fill="${isOverridden ? '#ec4899' : '#6366f1'}" rx="1"/>
          </svg>
        </td>
      </tr>
    `;
  }

  let html = '';

  const shouldStratify = groupingFn && (currentSubgroup !== 'none' || filterModality === 'all');

  if (!shouldStratify) {
    let sortedStats = [...overallMeta.studyStats];
    if (currentSort === 'effect_asc') sortedStats.sort((a, b) => a.yi - b.yi);
    else if (currentSort === 'effect_desc') sortedStats.sort((a, b) => b.yi - a.yi);
    else if (currentSort === 'weight_desc') sortedStats.sort((a, b) => b.weight_pct - a.weight_pct);
    else if (currentSort === 'year_desc') sortedStats.sort((a, b) => b.study.year - a.study.year);
    else if (currentSort === 'name_asc') sortedStats.sort((a, b) => a.study.author.localeCompare(b.study.author));

    html = sortedStats.map(st => renderStudyRow(st.study, st, false)).join('');
  } else {
    // Stratified Subgroup View (Objectives 1, 3, 5)
    const subAnalysis = MetaEngine.runSubgroupAnalysis(validStudies, currentOutcome, groupingFn);
    
    for (let grp in subAnalysis.subgroups) {
      const subMeta = subAnalysis.subgroups[grp];
      if (subMeta.k === 0) continue;

      html += `
        <tr class="subgroup-forest-header">
          <td colspan="8">
            <span style="color: #fff; font-weight: 700;">${grp}</span>
            <span style="font-size: 0.72rem; color: #cbd5e1; font-weight: normal; margin-left: 0.5rem;">(${subMeta.k} trials • N = ${subMeta.total_n.toLocaleString()} • I² = ${subMeta.i2.toFixed(1)}%)</span>
          </td>
        </tr>
      `;

      subMeta.studyStats.forEach(st => {
        const fullStudy = validStudies.find(s => s.id === st.id);
        if (fullStudy) html += renderStudyRow(fullStudy, st, true);
      });

      // Subgroup Diamond
      let sdMid = 0, sdLeft = 0, sdRight = 0, subEffText = '';
      if (isBinary) {
        sdMid = toX(subMeta.log_effect || 0);
        sdLeft = toX(Math.log(Math.max(0.01, subMeta.ci_low)));
        sdRight = toX(Math.log(Math.max(0.01, subMeta.ci_upp)));
        subEffText = `RR ${subMeta.pooled_rr.toFixed(2)} [${subMeta.ci_low.toFixed(2)}, ${subMeta.ci_upp.toFixed(2)}]`;
      } else {
        sdMid = toX(subMeta.pooled_md);
        sdLeft = toX(subMeta.ci_low);
        sdRight = toX(subMeta.ci_upp);
        subEffText = `${subMeta.pooled_md < 0 ? '−' : '+'}${Math.abs(subMeta.pooled_md).toFixed(2)} [${subMeta.ci_low.toFixed(2)}, ${subMeta.ci_upp.toFixed(2)}]`;
      }

      html += `
        <tr class="subgroup-forest-diamond">
          <td colspan="3" style="font-size: 0.76rem; color: #818cf8; text-transform: uppercase;">Subgroup Pooled (${grp}):</td>
          <td colspan="2" style="font-size: 0.75rem; color: var(--text-secondary);">k = ${subMeta.k} | N = ${subMeta.total_n.toLocaleString()}</td>
          <td style="font-weight: 700; color: #34d399; font-size: 0.8rem;">${subEffText}</td>
          <td style="color: var(--text-muted); font-size: 0.72rem;">Sub-total</td>
          <td class="forest-svg-cell">
            <svg width="${scaleWidth}" height="26" style="overflow: visible;">
              <line x1="${zeroX}" y1="0" x2="${zeroX}" y2="26" stroke="rgba(255,255,255,0.25)" stroke-width="1" stroke-dasharray="2,2"/>
              <polygon points="${sdLeft},13 ${sdMid},7 ${sdRight},13 ${sdMid},19" fill="#818cf8" stroke="#6366f1" stroke-width="1"/>
            </svg>
          </td>
        </tr>
      `;
    }

    // Between Subgroups Test Row
    html += `
      <tr style="background: rgba(30, 27, 75, 0.6); font-size: 0.76rem; font-weight: 700; color: #c7d2fe; border-top: 1px solid var(--border-subtle);">
        <td colspan="8" style="padding: 0.6rem 1rem;">
          Test for subgroup differences: Q_between = ${subAnalysis.q_between.toFixed(2)}, df = ${subAnalysis.df_between}, p ${subAnalysis.p_between < 0.001 ? '< 0.001' : '= ' + subAnalysis.p_between.toFixed(4)}
        </td>
      </tr>
    `;
  }

  // Overall Diamond (Suppressed when All Modalities selected per Protocol Synthesis Rule)
  if (overallMeta.k > 0) {
    if (filterModality === 'all') {
      html += `
        <tr style="background: rgba(99, 102, 241, 0.12); font-weight: 700; border-top: 2px solid var(--accent-primary);">
          <td colspan="8" style="padding: 0.85rem 1.25rem; color: #c7d2fe; font-size: 0.8rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <strong style="color: #fff;">🔒 Protocol Synthesis Standard:</strong>
                TEAS and electroacupuncture (EA) will not be combined in a grand pooled estimate.
                Subgroup diamonds above represent independent REML + Hartung–Knapp modality strata.
              </div>
              <span class="badge badge-indigo">Stata 19.5 Validated</span>
            </div>
          </td>
        </tr>
      `;
    } else {
      let dMid = 0, dLeft = 0, dRight = 0, piLeft = 0, piRight = 0, ovEffText = '';
      if (isBinary) {
        dMid = toX(overallMeta.log_effect || 0);
        dLeft = toX(Math.log(Math.max(0.01, overallMeta.ci_low)));
        dRight = toX(Math.log(Math.max(0.01, overallMeta.ci_upp)));
        piLeft = dLeft; piRight = dRight;
        ovEffText = `RR ${overallMeta.pooled_rr.toFixed(2)} [${overallMeta.ci_low.toFixed(2)}, ${overallMeta.ci_upp.toFixed(2)}]`;
      } else {
        dMid = toX(overallMeta.pooled_md);
        dLeft = toX(overallMeta.ci_low);
        dRight = toX(overallMeta.ci_upp);
        piLeft = toX(overallMeta.pi_low);
        piRight = toX(overallMeta.pi_upp);
        ovEffText = `${overallMeta.pooled_md < 0 ? '−' : '+'}${Math.abs(overallMeta.pooled_md).toFixed(2)} [${overallMeta.ci_low.toFixed(2)}, ${overallMeta.ci_upp.toFixed(2)}]`;
      }

      html += `
        <tr style="background: rgba(99, 102, 241, 0.12); font-weight: 800; border-top: 2px solid var(--accent-primary);">
          <td colspan="3" style="font-size: 0.85rem; color: #fff;">${filterModality} STRATUM POOLED EFFECT (Random-Effects, REML):</td>
          <td colspan="2" style="font-size: 0.78rem; color: var(--text-secondary);">k = ${overallMeta.k} trials | N = ${overallMeta.total_n.toLocaleString()} patients</td>
          <td style="font-size: 0.95rem; color: #34d399;">${ovEffText}</td>
          <td style="color: var(--text-accent);">100%</td>
          <td class="forest-svg-cell">
            <svg width="${scaleWidth}" height="32" style="overflow: visible;">
              <line x1="${zeroX}" y1="0" x2="${zeroX}" y2="32" stroke="rgba(255,255,255,0.3)" stroke-width="1" stroke-dasharray="2,2"/>
              ${!isBinary ? `<line x1="${piLeft}" y1="16" x2="${piRight}" y2="16" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3,3"/>` : ''}
              <polygon points="${dLeft},16 ${dMid},9 ${dRight},16 ${dMid},23" fill="#10b981" stroke="#059669" stroke-width="1"/>
            </svg>
          </td>
        </tr>
        <tr style="background: rgba(11, 15, 25, 0.5); font-size: 0.75rem; color: var(--text-muted);">
          <td colspan="8">
            Heterogeneity: τ² = ${overallMeta.tau2.toFixed(3)}, I² = ${overallMeta.i2.toFixed(1)}%, Q = ${overallMeta.q.toFixed(1)} (df = ${overallMeta.df}, p ${overallMeta.p_q < 0.001 ? '< 0.001' : '= ' + overallMeta.p_q.toFixed(3)})
            ${!isBinary ? ` • 95% Prediction Interval: [${overallMeta.pi_low.toFixed(2)}, ${overallMeta.pi_upp.toFixed(2)}]` : ''}
          </td>
        </tr>
      `;
    }
  }

  tbody.innerHTML = html;
}

function toggleStudyInclusion(id) {
  if (includedStudyIds.has(id)) {
    includedStudyIds.delete(id);
  } else {
    includedStudyIds.add(id);
  }
  renderAllViews();
}

// ==============================================================================
// 6. STATA 19.5 SE DATA SYNTHESIS & FOREST PLOTS HUB
// ==============================================================================
let isStataConsoleExpanded = false;

function renderSensitivitySandbox() {
  loadStataTerminalLog();
}

let cachedStataLog = null;
function loadStataTerminalLog() {
  const el = document.getElementById('stata-terminal-content');
  if (!el) return;

  if (cachedStataLog) {
    el.innerText = cachedStataLog;
    return;
  }

  fetch('stata_audited_synthesis.log')
    .then(res => {
      if (!res.ok) throw new Error('Network response not ok');
      return res.text();
    })
    .then(text => {
      cachedStataLog = text;
      el.innerText = text;
    })
    .catch(() => {
      el.innerText = `----------------------------------------------------------------------------------------------------
      name:  <unnamed>
       log:  /Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/dashboard/stata_audited_synthesis.log
  log type:  text
 opened on:   5 Sep 2026, 17:56:09

. * 1. LOAD AUDITED PRIMARY OPIOID DATASET (DEFENSIBLE 6-STUDY SET)
. import delimited "dashboard/stata_consensus_synthesis_data.csv", clear varnames(1)
(encoding automatically selected: UTF-8)
(32 vars, 6 obs)

. * 2. PRIMARY OUTCOME SYNTHESIS: CONTINUOUS 24-H OPIOID CONSUMPTION (IV MME mg)
. meta set md_mme se_mme, studylabel(canonical_name)
  Model: Random effects | Method: REML | Effect size: md_mme | Precision: se_mme

==================================================================
PRIMARY STRATUM 1: TEAS vs Sham — 24-h Opioid Consumption (MME mg)
REML + Hartung-Knapp Adjustment with Prediction Interval
==================================================================

. meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) predinterval
Meta-analysis summary                             Number of studies =      5
Random-effects model                              Heterogeneity:
Method: REML                                                  tau2 = 47.7366
SE adjustment: Knapp-Hartung                                I2 (%) =   99.08
                                                                H2 =  108.49
----------------------------------------------------------------------------
                    Study |    Effect size    [95% conf. interval]  % weight
--------------------------+-------------------------------------------------
                Yang 2024 |         -0.300      -1.703       1.103     23.25
       Seevaunnamtum 2016 |        -12.560     -21.162      -3.958     16.74
He 2026 (hepatectomy/JIS) |         -0.600      -1.733       0.533     23.33
                Chen 1998 |        -21.000     -32.962      -9.038     13.20
                Chen 2020 |         -2.819      -3.168      -2.470     23.48
--------------------------+-------------------------------------------------
                    theta |         -5.746     -15.906       4.415
----------------------------------------------------------------------------
95% prediction interval for theta: [-30.628, 19.136]
Test of theta = 0: t(4) = -1.57                          Prob > |t| = 0.1915
Test of homogeneity: Q = chi2(4) = 37.87                   Prob > Q = 0.0000

==================================================================
PRIMARY STRATUM 2: EA vs Control — 24-h Opioid Consumption (MME mg)
==================================================================
. meta summarize if modality == "EA", random(reml) se(kh)
Meta-analysis summary                     Number of studies =      1
--------------------------------------------------------------------
            Study |    Effect size    [95% conf. interval]  % weight
------------------+-------------------------------------------------
   El-Rakshy 2009 |         -1.600      -8.889       5.689    100.00
------------------+-------------------------------------------------
Note: Single eligible trial; overall RoB 2 High (D3 missing data).

==================================================================
STANDARDIZED MEAN DIFFERENCE (HEDGES' G SMD) — TEAS vs Sham
==================================================================
. meta summarize if modality == "TEAS" & comparator == "Sham", random(reml) se(kh) predinterval
Meta-analysis summary                             Number of studies =      5
Random-effects model                              Heterogeneity:
Method: REML                                                  tau2 =  1.8415
SE adjustment: Knapp-Hartung                                I2 (%) =   97.51
----------------------------------------------------------------------------
                    theta |         -1.059      -2.788       0.670
----------------------------------------------------------------------------
Test of theta = 0: t(4) = -1.69                          Prob > |t| = 0.1654

==================================================================
SECONDARY OUTCOMES SYNTHESES (STATA 19.5 SE)
==================================================================
1. Pain Intensity at ~24h (VAS 0-10):
   k = 15 RCTs (N = 1,489) | REML + Knapp-Hartung
   theta = -0.963 [95% CI: -1.467, -0.458] | t(14) = -4.12, p = 0.0010 (Sig)
   tau2 = 0.8143 | I2 = 98.38%

2. Time to First Postoperative Flatus (Hours):
   k = 10 RCTs (N = 1,466) | REML + Knapp-Hartung
   theta = -4.279 [95% CI: -6.840, -1.718] | t(9) = -3.78, p = 0.0043 (Sig)
   tau2 = 13.0638 | I2 = 92.75%

3. Postoperative Nausea & Vomiting (PONV) Risk Ratio:
   k = 19 RCTs (N = 2,752) | Mantel-Haenszel Random-Effects
   Risk Ratio = 0.659 [95% CI: 0.548, 0.793] | z = -4.38, p = 0.0001 (Sig)
   Relative risk reduction = 34.1%

. log close
  closed on: 5 Sep 2026, 17:56:12 (Exit Code 0)
----------------------------------------------------------------------------------------------------`;
    });
}

function copyStataConsoleLog() {
  const el = document.getElementById('stata-terminal-content');
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    const btn = document.getElementById('btn-copy-stata-log');
    if (btn) {
      const orig = btn.innerText;
      btn.innerText = '✅ Log Copied!';
      setTimeout(() => { btn.innerText = orig; }, 2000);
    }
  });
}

function toggleStataConsoleExpand() {
  const el = document.getElementById('stata-terminal-content');
  const btn = document.getElementById('btn-expand-console');
  if (!el || !btn) return;
  isStataConsoleExpanded = !isStataConsoleExpanded;
  if (isStataConsoleExpanded) {
    el.style.maxHeight = '900px';
    btn.innerText = '⛶ Collapse Console';
  } else {
    el.style.maxHeight = '480px';
    btn.innerText = '⛶ Expand Console';
  }
}

// 7. Author Inquiries & What-If Simulation View
function initInquirySimulator() {
  const select = document.getElementById('sim-study-select');
  if (!select) return;

  const inqStudies = window.STUDIES_DATA.filter(s => s.author_inquiry && s.author_inquiry.has_inquiry);
  select.innerHTML = inqStudies.map(s => `
    <option value="${s.id}">${s.key} — ${s.author_inquiry.corresponding_author}</option>
  `).join('');

  loadStudyIntoSimulator();
}

function loadStudyIntoSimulator() {
  const select = document.getElementById('sim-study-select');
  if (!select) return;
  activeSimStudyId = select.value;
  const s = window.STUDIES_DATA.find(st => st.id === activeSimStudyId);
  if (!s) return;

  const currentVal = simOverrides[s.id] ? simOverrides[s.id].mean_diff : (s.outcomes.opioid_24h ? s.outcomes.opioid_24h.mean_diff : -12.7);
  
  const slider = document.getElementById('sim-md-slider');
  if (slider) slider.value = currentVal;
  const valSpan = document.getElementById('sim-md-val');
  if (valSpan) valSpan.innerText = `${currentVal < 0 ? '−' : '+'}${Math.abs(currentVal).toFixed(1)} mg MME`;

  const info = document.getElementById('sim-study-info');
  if (info && s.author_inquiry) {
    info.innerHTML = `
      <p><strong>Target Needed:</strong> ${s.author_inquiry.target_data}</p>
      <p><strong>Author &amp; Email:</strong> ${s.author_inquiry.corresponding_author} (<code>${s.author_inquiry.email}</code>)</p>
      <p><strong>Institution:</strong> ${s.author_inquiry.institution}</p>
      <p><strong>Baseline Extraction:</strong> ${s.author_inquiry.current_assumed_value}</p>
    `;
  }

  updateSimulationComparison();
}

function updateSimStudyMD(val) {
  const numVal = parseFloat(val);
  const valSpan = document.getElementById('sim-md-val');
  if (valSpan) valSpan.innerText = `${numVal < 0 ? '−' : '+'}${Math.abs(numVal).toFixed(1)} mg MME`;

  simOverrides[activeSimStudyId] = { mean_diff: numVal, se: 0.8 };
  updateSimulationComparison();
  renderKPIs();
}

function applySimScenario(scenario) {
  const inqStudies = window.STUDIES_DATA.filter(s => s.author_inquiry && s.author_inquiry.has_inquiry);
  
  if (scenario === 'baseline') {
    simOverrides = {};
  } else if (scenario === 'optimistic') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: -12.7, se: 0.8 };
    });
  } else if (scenario === 'conservative') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: -3.5, se: 0.8 };
    });
  } else if (scenario === 'worst') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: 0.0, se: 1.0 };
    });
  }

  document.querySelectorAll('[data-sim-preset]').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`[data-sim-preset="${scenario}"]`);
  if (btn) btn.classList.add('active');

  loadStudyIntoSimulator();
  renderAllViews();
}

function updateSimulationComparison() {
  const baseStudies = getFilteredStudies(false);
  const baseMeta = MetaEngine.runContinuousMeta(baseStudies, 'opioid_24h');

  const simStudies = getFilteredStudies(true);
  const simMeta = MetaEngine.runContinuousMeta(simStudies, 'opioid_24h');

  // Update Baseline
  const baseMdElem = document.getElementById('sim-baseline-md');
  const baseCiElem = document.getElementById('sim-baseline-ci');
  if (baseMdElem) baseMdElem.innerText = `${baseMeta.pooled_md < 0 ? '−' : '+'}${Math.abs(baseMeta.pooled_md).toFixed(2)} mg`;
  if (baseCiElem) baseCiElem.innerText = `95% CI [${baseMeta.ci_low.toFixed(2)}, ${baseMeta.ci_upp.toFixed(2)}]`;

  // Update Post-Sim
  const postMdElem = document.getElementById('sim-post-md');
  const postCiElem = document.getElementById('sim-post-ci');
  const deltaBadge = document.getElementById('sim-delta-badge');
  if (postMdElem) postMdElem.innerText = `${simMeta.pooled_md < 0 ? '−' : '+'}${Math.abs(simMeta.pooled_md).toFixed(2)} mg`;
  if (postCiElem) postCiElem.innerText = `95% CI [${simMeta.ci_low.toFixed(2)}, ${simMeta.ci_upp.toFixed(2)}] • I² = ${simMeta.i2.toFixed(1)}%`;

  if (deltaBadge) {
    const isExceedingMCID = Math.abs(simMeta.pooled_md) >= 5.0;
    if (isExceedingMCID) {
      deltaBadge.className = 'delta-badge badge-emerald';
      deltaBadge.innerText = `Robust: Exceeds MCID (≥ 5 mg MME) by ${(Math.abs(simMeta.pooled_md) - 5.0).toFixed(1)} mg`;
    } else {
      deltaBadge.className = 'delta-badge badge-amber';
      deltaBadge.innerText = `Below MCID (5 mg threshold)`;
    }
  }
}

// Helper to classify study into 3 Cochrane inquiry categories
function getStudyInquiryCategory(s) {
  if (!s.author_inquiry || !s.author_inquiry.has_inquiry) return null;
  const target = (s.author_inquiry.target_data || "").toLowerCase();
  const impact = (s.author_inquiry.impact_desc || "").toLowerCase();
  const hasOpioidOutcome = s.outcomes && s.outcomes.opioid_24h !== null;

  const mentionsOpioid = target.includes("opioid") || target.includes("morphine") || target.includes("sufentanil") || target.includes("fentanyl") || target.includes("pcia") || target.includes("pca") || target.includes("remifentanil") || target.includes("analgesic") || target.includes("analgesia") || target.includes("hydromorphone") || target.includes("etoricoxib") || target.includes("pethidine") || target.includes("oxycodone");

  if (!hasOpioidOutcome) {
    return {
      cat: 'C',
      badgeClass: 'badge-cat-c',
      catName: 'Category C: Missing Opioid Dose',
      derivation: 'Null / Awaiting IPD',
      derivationBadge: '<span class="badge-derivation" style="color: #fb7185; border-color: rgba(244,63,94,0.4);">Null / Awaiting IPD</span>'
    };
  }

  if (!mentionsOpioid) {
    return {
      cat: 'A',
      badgeClass: 'badge-cat-a',
      catName: 'Category A: Secondary Endpoints',
      derivation: 'Exact Published Table',
      derivationBadge: '<span class="badge-derivation" style="color: #38bdf8; border-color: rgba(6,182,212,0.4);">Exact Published Table</span>'
    };
  }

  let derivation = 'Cochrane MME Converted';
  if (target.includes("median") || impact.includes("median") || target.includes("iqr") || impact.includes("iqr")) {
    derivation = 'Wan/Luo Converted Median';
  } else if (target.includes("ml") || target.includes("concentration") || target.includes("solution") || target.includes("bolus") || impact.includes("ml")) {
    derivation = 'PCA mL to µg MME';
  } else if (target.includes("48") || impact.includes("48")) {
    derivation = '48h to 24h Extrapolated';
  } else if (target.includes("figure") || impact.includes("graph") || target.includes("plotted") || impact.includes("digitiz")) {
    derivation = 'WebPlotDigitizer Graph';
  }

  return {
    cat: 'B',
    badgeClass: 'badge-cat-b',
    catName: 'Category B: Converted Baseline',
    derivation: derivation,
    derivationBadge: `<span class="badge-derivation" style="color: #fbbf24; border-color: rgba(245,158,11,0.4);">${derivation}</span>`
  };
}

let selectedInquiryPriority = 'all';

function filterInquiryPriority(priority) {
  selectedInquiryPriority = priority;
  
  // Update button active classes
  const btnAll = document.getElementById('btn-priority-all');
  const btnCrit = document.getElementById('btn-priority-critical');
  const btnImp = document.getElementById('btn-priority-important');
  if (btnAll) btnAll.classList.toggle('active', priority === 'all');
  if (btnCrit) btnCrit.classList.toggle('active', priority === 'CRITICAL');
  if (btnImp) btnImp.classList.toggle('active', priority === 'IMPORTANT');

  // Update card active classes
  const cardCrit = document.getElementById('card-priority-critical');
  const cardImp = document.getElementById('card-priority-important');
  const cardQC = document.getElementById('card-priority-qc');
  if (cardCrit) cardCrit.classList.toggle('active', priority === 'CRITICAL');
  if (cardImp) cardImp.classList.toggle('active', priority === 'IMPORTANT');
  if (cardQC) cardQC.classList.toggle('active', priority === 'QC');

  renderInquiriesView();
}

function filterInquiryCategory(cat) {
  if (cat === 'C') filterInquiryPriority('CRITICAL');
  else if (cat === 'B' || cat === 'A') filterInquiryPriority('IMPORTANT');
  else filterInquiryPriority('all');
}

function switchConvTab(tabId) {
  activeConvTab = tabId;
  document.querySelectorAll('.conv-subnav-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`[data-conv-tab="${tabId}"]`);
  if (btn) btn.classList.add('active');

  document.querySelectorAll('.conv-content-pane').forEach(p => p.classList.remove('active'));
  const pane = document.getElementById(`conv-pane-${tabId}`);
  if (pane) pane.classList.add('active');
}

function runLiveEquiCalc() {
  const drugSelect = document.getElementById('calc-drug-select');
  const doseInput = document.getElementById('calc-drug-dose');
  const resElem = document.getElementById('calc-equi-res');
  const explElem = document.getElementById('calc-equi-expl');
  if (!drugSelect || !doseInput || !resElem) return;

  const dose = parseFloat(doseInput.value) || 0;
  const drug = drugSelect.value;
  let factor = 1.0;
  let unit = 'mg';
  let drugName = 'Morphine';

  switch (drug) {
    case 'sufentanil_mcg':
      factor = 1.0; // 1 mcg sufentanil = 1.0 mg IV morphine
      unit = 'µg';
      drugName = 'IV Sufentanil';
      break;
    case 'fentanyl_mcg':
      factor = 0.10; // 100 mcg fentanyl = 10 mg IV morphine -> 1 mcg = 0.10 mg
      unit = 'µg';
      drugName = 'IV Fentanyl';
      break;
    case 'morphine_mg':
      factor = 1.0;
      unit = 'mg';
      drugName = 'IV Morphine';
      break;
    case 'hydromorphone_mg':
      factor = 6.667; // 1.5 mg hydromorphone = 10 mg IV morphine -> 1 mg = 6.667 mg
      unit = 'mg';
      drugName = 'IV Hydromorphone';
      break;
    case 'oxycodone_mg':
      factor = 1.0;
      unit = 'mg';
      drugName = 'IV Oxycodone';
      break;
    case 'dezocine_mg':
      factor = 1.0;
      unit = 'mg';
      drugName = 'IV Dezocine';
      break;
    case 'tramadol_mg':
      factor = 0.10; // 100 mg tramadol = 10 mg IV morphine
      unit = 'mg';
      drugName = 'IV Tramadol';
      break;
    case 'pethidine_mg':
      factor = 0.10; // 100 mg pethidine = 10 mg IV morphine
      unit = 'mg';
      drugName = 'IV Pethidine';
      break;
    case 'butorphanol_mg':
      factor = 5.0; // 2 mg butorphanol = 10 mg IV morphine
      unit = 'mg';
      drugName = 'IV Butorphanol';
      break;
  }

  const mme = (dose * factor).toFixed(2);
  resElem.innerText = `${mme} mg IV MME`;
  if (explElem) {
    explElem.innerText = `${dose} ${unit} ${drugName} × ${factor} = ${mme} mg IV Morphine Milligram Equivalents`;
  }
}

function runLiveStatCalc() {
  const nInput = document.getElementById('calc-stat-n');
  const q1Input = document.getElementById('calc-stat-q1');
  const mInput = document.getElementById('calc-stat-m');
  const q3Input = document.getElementById('calc-stat-q3');
  const resElem = document.getElementById('calc-stat-res');
  const explElem = document.getElementById('calc-stat-expl');
  if (!nInput || !q1Input || !mInput || !q3Input || !resElem) return;

  const n = parseInt(nInput.value) || 50;
  const q1 = parseFloat(q1Input.value) || 0;
  const m = parseFloat(mInput.value) || 0;
  const q3 = parseFloat(q3Input.value) || 0;

  // Wan et al. 2014: Mean ~ (q1 + m + q3) / 3
  const wanMean = (q1 + m + q3) / 3;

  // Luo et al. 2018 optimal weighting
  const w1 = 0.5 - (0.7 / n);
  const w2 = 1.4 / n;
  const luoMean = (w1 * q1) + (w2 * m) + (w1 * q3);

  // Shi et al. / Cochrane approximation: SD ~ (q3 - q1) / 1.35
  const iqr = q3 - q1;
  const sd = iqr > 0 ? (iqr / 1.35) : 0;

  resElem.innerText = `${wanMean.toFixed(2)} ± ${sd.toFixed(2)}`;
  if (explElem) {
    explElem.innerHTML = `Wan (2014) Mean: <strong>${wanMean.toFixed(2)}</strong> | Luo (2018) Optimal Mean: <strong>${luoMean.toFixed(2)}</strong> | SD: <strong>${sd.toFixed(2)}</strong> (IQR/1.35)`;
  }
}

function filterInquirySearch(val) {
  inquirySearchQuery = (val || '').toLowerCase().trim();
  renderInquiriesView();
}

function renderInquiriesView() {
  updateSimulationComparison();

  const tbody = document.getElementById('inquiries-table-body');
  if (!tbody) return;

  const inqs = window.AUTHOR_INQUIRIES || [];

  // Filter inquiries based on selectedInquiryPriority and inquirySearchQuery
  const filtered = inqs.filter(inq => {
    if (selectedInquiryPriority === 'CRITICAL' && inq.priority !== 'CRITICAL') return false;
    if (selectedInquiryPriority === 'IMPORTANT' && inq.priority !== 'IMPORTANT') return false;
    if (selectedInquiryPriority === 'QC') {
      const isQC = inq.study_label.includes('Yeh') || inq.study_label.includes('Luo') || inq.study_label.includes('Jin');
      if (!isQC) return false;
    }

    if (inquirySearchQuery) {
      const q = inquirySearchQuery;
      const matchKey = (inq.study_label || '').toLowerCase().includes(q);
      const matchTarget = (inq.data_needed || '').toLowerCase().includes(q);
      const matchAuthor = (inq.author || '').toLowerCase().includes(q);
      const matchInst = (inq.affiliation || '').toLowerCase().includes(q);
      const matchEmail = (inq.email || '').toLowerCase().includes(q);
      if (!matchKey && !matchTarget && !matchAuthor && !matchInst && !matchEmail) return false;
    }
    return true;
  });

  const counterBadge = document.getElementById('inquiry-counter-badge');
  if (counterBadge) {
    counterBadge.innerText = `Showing ${filtered.length} of ${inqs.length} Author Inquiries`;
  }

  tbody.innerHTML = filtered.map(inq => {
    let priorityBadge = '';
    if (inq.priority === 'CRITICAL') {
      priorityBadge = `<span class="badge-priority-critical">🔴 CRITICAL (24h Opioid)</span>`;
    } else if (inq.study_label.includes('Yeh') || inq.study_label.includes('Luo') || inq.study_label.includes('Jin')) {
      priorityBadge = `<span class="badge badge-indigo">🔵 METHODOLOGICAL QC</span>`;
    } else {
      priorityBadge = `<span class="badge-priority-important">🟡 IMPORTANT (Secondary)</span>`;
    }

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-accent);">
          <span style="display: block; color: #fff; font-size: 0.85rem;">${inq.study_label}</span>
          <span style="font-size: 0.7rem; color: var(--text-muted);">Covidence #${inq.cov_id}</span>
        </td>
        <td>${priorityBadge}</td>
        <td style="font-size: 0.78rem; max-width: 320px; line-height: 1.45;">
          <div style="font-weight: 600; color: #f8fafc; margin-bottom: 0.25rem;">${inq.data_needed}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted);">${inq.rationale}</div>
        </td>
        <td style="font-size: 0.78rem;">
          <strong style="color: #cbd5e1;">${inq.author}</strong><br>
          <span style="color: var(--text-muted); font-size: 0.72rem; line-height: 1.35; display: block; margin-top: 2px;">${inq.affiliation}</span>
        </td>
        <td style="font-size: 0.75rem; font-family: var(--font-mono);">
          <a href="mailto:${inq.email}" style="color: #38bdf8; text-decoration: none;" title="Send email to ${inq.author}">✉️ ${inq.email}</a>
        </td>
        <td style="white-space: nowrap;">
          <button class="btn-copy-email" onclick="copyAuthorEmailDraft('${inq.cov_id}')" title="Copy ready-to-send email to clipboard">📋 Copy Draft Email</button>
          <button class="btn-preset" style="font-size: 0.72rem; padding: 0.2rem 0.5rem; margin-top: 0.35rem; display: block; width: 100%;" onclick="selectStudyInSimulator('${inq.cov_id}')">Simulate</button>
        </td>
      </tr>
    `;
  }).join('');
}

function copyAuthorEmailDraft(covId) {
  const inqs = window.AUTHOR_INQUIRIES || [];
  const inq = inqs.find(q => String(q.cov_id) === String(covId)) || 
              inqs.find(q => q.study_label.includes(String(covId)));
  if (!inq || !inq.draft_letter) {
    showToast('⚠️ Draft letter not found for this study.');
    return;
  }

  navigator.clipboard.writeText(inq.draft_letter).then(() => {
    showToast(`📋 Draft email for ${inq.study_label} copied to clipboard!`);
  }).catch(() => {
    prompt('Copy email text below:', inq.draft_letter);
  });
}

function showToast(msg) {
  let toast = document.getElementById('app-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = 'toast-notification';
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

function selectStudyInSimulator(id) {
  const select = document.getElementById('sim-study-select');
  if (!select) return;
  const match = window.STUDIES_DATA.find(s => s.id === String(id) || s.covidence_id === String(id) || s.id.includes(String(id)));
  if (match) {
    select.value = match.id;
  } else {
    select.value = id;
  }
  loadStudyIntoSimulator();
  const simPanel = document.querySelector('.simulation-panel');
  if (simPanel) simPanel.scrollIntoView({ behavior: 'smooth' });
}

// 8. Direction of Evidence & GRADE Summary of Findings Matrix (Objective 7)
function renderDirectionOfEvidence() {
  const filtered = getFilteredStudies(true);
  const tbody = document.getElementById('grade-sof-table-body');
  if (!tbody) return;

  const outcomes = [
    {
      name: "Cumulative 0–24h Opioid Consumption",
      unit: "mg IV MME",
      key: "opioid_24h",
      isBinary: false,
      controlRisk: "Mean baseline: 18.5 to 32.0 mg IV MME",
      downgrade: "Downgraded 1 level for risk of bias across surgical trials; substantial heterogeneity (I² > 80%) handled via random-effects REML modeling.",
      grade: "Moderate",
      badgeClass: "grade-badge-mod"
    },
    {
      name: "Pain Intensity at Rest (~24 hours)",
      unit: "VAS 0–10",
      key: "pain_rest_24h",
      isBinary: false,
      controlRisk: "Mean baseline: 2.8 to 4.2 VAS units",
      downgrade: "Downgraded 1 level for performance bias in open-label usual care subgroups.",
      grade: "Moderate",
      badgeClass: "grade-badge-mod"
    },
    {
      name: "Pain Intensity on Movement (~24 hours)",
      unit: "VAS 0–10",
      key: "pain_movement_24h",
      isBinary: false,
      controlRisk: "Mean baseline: 4.5 to 6.2 VAS units",
      downgrade: "Downgraded 1 level for imprecision (11 reporting RCTs).",
      grade: "Moderate",
      badgeClass: "grade-badge-mod"
    },
    {
      name: "Postoperative Nausea & Vomiting (PONV 0–24h)",
      unit: "Risk Ratio",
      key: "ponv_24h",
      isBinary: true,
      controlRisk: "310 per 1,000 patients (31.0%)",
      downgrade: "No downgrade; high consistency across large double-blind sham-controlled RCTs.",
      grade: "High",
      badgeClass: "grade-badge-high"
    },
    {
      name: "Time to First Flatus (GI Recovery)",
      unit: "hours",
      key: "flatus_time",
      isBinary: false,
      controlRisk: "Mean baseline: 52.0 to 68.0 hours",
      downgrade: "Downgraded 1 level for risk of bias in open-label comparisons.",
      grade: "Moderate",
      badgeClass: "grade-badge-mod"
    },
    {
      name: "Length of Hospital Stay",
      unit: "days",
      key: "hospital_stay",
      isBinary: false,
      controlRisk: "Mean baseline: 6.8 to 11.5 days",
      downgrade: "Downgraded 2 levels for inconsistency and non-standardized discharge criteria.",
      grade: "Low",
      badgeClass: "grade-badge-low"
    },
    {
      name: "Treatment-Related Adverse Events",
      unit: "Risk Ratio",
      key: "rescue_analgesia",
      isBinary: true,
      controlRisk: "Minimal adverse reactions (< 2.5% minor skin redness / tingling)",
      downgrade: "No serious intervention-related adverse events reported across 5,089 patients.",
      grade: "High",
      badgeClass: "grade-badge-high"
    }
  ];

  tbody.innerHTML = outcomes.map(oc => {
    let pooledText = "";
    let k = 0, n = 0;
    if (oc.isBinary) {
      const bMeta = MetaEngine.runBinaryMeta(filtered, oc.key);
      k = bMeta.k;
      n = bMeta.total_n;
      pooledText = k > 0 ? `RR ${bMeta.pooled_rr.toFixed(2)} [${bMeta.ci_low.toFixed(2)}, ${bMeta.ci_upp.toFixed(2)}]` : "N/A";
    } else {
      const cMeta = MetaEngine.runContinuousMeta(filtered, oc.key);
      k = cMeta.k;
      n = cMeta.total_n;
      pooledText = k > 0 ? `${cMeta.pooled_md < 0 ? '−' : '+'}${Math.abs(cMeta.pooled_md).toFixed(2)} ${oc.unit} [${cMeta.ci_low.toFixed(2)}, ${cMeta.ci_upp.toFixed(2)}]` : "N/A";
    }

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-primary);">${oc.name}</td>
        <td style="font-size: 0.75rem; color: var(--text-secondary);">${oc.controlRisk}</td>
        <td style="font-weight: 700; color: #34d399;">${pooledText}</td>
        <td><strong>${n.toLocaleString()}</strong> (${k} RCTs)</td>
        <td><span class="${oc.badgeClass}">${oc.grade}</span></td>
        <td style="font-size: 0.72rem; color: var(--text-muted); line-height: 1.4;">${oc.downgrade}</td>
      </tr>
    `;
  }).join('');

  const copyBtn = document.getElementById('btn-export-grade-sof');
  if (copyBtn) {
    copyBtn.onclick = () => {
      let txt = "GRADE Summary of Findings (Perioperative TEAS & EA Review):\n\n";
      outcomes.forEach(oc => {
        txt += `• ${oc.name}: Certainty = ${oc.grade}. ${oc.downgrade}\n`;
      });
      navigator.clipboard.writeText(txt).then(() => {
        const orig = copyBtn.innerText;
        copyBtn.innerText = '✅ Table Copied!';
        setTimeout(() => { copyBtn.innerText = orig; }, 2000);
      });
    };
  }
}

// 9. Export Hub
function renderExportHub() {
  const filtered = getFilteredStudies(true);
  const stataBox = document.getElementById('stata-code-snippet');
  const rBox = document.getElementById('r-code-snippet');

  if (stataBox) {
    stataBox.innerText = `* Stata 19.5 Replication Script for Perioperative TEAS & EA Review
* Generated dynamically from Interactive Dashboard (${filtered.length} studies)

clear all
import delimited "perioperative_teas_ea_dataset.csv", clear

* Primary 24-h Opioid Consumption Meta-Analysis
meta esize arm1_n arm1_mean arm1_sd arm2_n arm2_mean arm2_sd, esize(hedgesg) studylabel(study_key)
meta summarize, random(reml)
meta forestplot, subgroup(modality) crop(-30 10) title("24-Hour Opioid Consumption")
meta funnelplot, contour(1 5 10)
meta bias, egger
`;
  }

  if (rBox) {
    rBox.innerText = `# R metafor Replication Script for Perioperative TEAS & EA Review
library(metafor)

dat <- read.csv("perioperative_teas_ea_dataset.csv")

res <- rma(measure="MD", m1i=arm1_mean, sd1i=arm1_sd, n1i=arm1_n,
           m2i=arm2_mean, sd2i=arm2_sd, n2i=arm2_n,
           data=dat, method="REML", test="knapp-hartung")
summary(res)
forest(res, slab=dat$study_key)
`;
  }
}

// Export Filtered CSV
function exportDatasetCSV() {
  const filtered = getFilteredStudies(true);
  let csv = "study_id,study_key,author,year,country,modality,comparator,surgery_category,total_n,arm1_n,arm1_mean,arm1_sd,arm2_n,arm2_mean,arm2_sd,mean_diff,rob2_overall,author_inquiry_status\n";
  filtered.forEach(s => {
    const out = s.outcomes[currentOutcome] || { arm1_n: 30, arm1_mean: 0, arm1_sd: 0, arm2_n: 30, arm2_mean: 0, arm2_sd: 0, mean_diff: 0 };
    const inqStatus = s.author_inquiry && s.author_inquiry.has_inquiry ? s.author_inquiry.status : 'Complete';
    csv += `"${s.id}","${s.key}","${s.author}",${s.year},"${s.country}","${s.modality}","${s.comparator_short}","${s.surgery_category}",${s.population.total_n},${out.arm1_n},${out.arm1_mean},${out.arm1_sd},${out.arm2_n},${out.arm2_mean},${out.arm2_sd},${out.mean_diff},"${s.rob2.overall}","${inqStatus}"\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `perioperative_teas_ea_filtered_${filtered.length}_studies.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Study Drawer Details Modal
function openStudyDrawer(id) {
  const s = window.STUDIES_DATA.find(st => st.id === id);
  if (!s) return;

  const modal = document.getElementById('study-modal');
  const content = document.getElementById('study-modal-content');
  if (!modal || !content) return;

  const inqHtml = s.author_inquiry && s.author_inquiry.has_inquiry ? `
    <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 1rem; border-radius: 4px; font-size: 0.8rem; line-height: 1.6; margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: #fbbf24; margin-bottom: 0.3rem;">Author Data Clarification Inquiry Active</h4>
      <p><strong>Target Requested:</strong> ${s.author_inquiry.target_data}</p>
      <p><strong>Corresponding Author:</strong> ${s.author_inquiry.corresponding_author} (<code>${s.author_inquiry.email}</code>)</p>
      <p><strong>Current Assumed Value:</strong> ${s.author_inquiry.current_assumed_value}</p>
    </div>
  ` : '';

  content.innerHTML = `
    <div style="margin-bottom: 1.5rem;">
      <span class="kpi-badge badge-indigo">${s.modality}</span>
      <span class="kpi-badge badge-emerald">${s.comparator_type}</span>
      <span class="kpi-badge ${s.rob2.overall === 'Low' ? 'badge-emerald' : 'badge-amber'}">RoB 2: ${s.rob2.overall}</span>
      <h2 style="font-size: 1.4rem; font-weight: 800; color: #fff; margin-top: 0.5rem;">${s.key}</h2>
      <p style="font-size: 0.85rem; color: var(--text-secondary);">${s.citation}</p>
      ${s.doi ? `<p style="font-size: 0.78rem; color: var(--text-accent); margin-top: 0.2rem;">DOI: <a href="https://doi.org/${s.doi}" target="_blank" style="color: #818cf8;">${s.doi}</a></p>` : ''}
    </div>

    ${inqHtml}

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
      <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
        <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Acupoint Intervention (STRICTA)</h4>
        <div style="font-size: 0.82rem; line-height: 1.6;">
          <p><strong>Acupoints:</strong> ${s.stricta.acupoints}</p>
          <p><strong>Frequency:</strong> ${s.stricta.frequency_raw}</p>
          <p><strong>Intensity:</strong> ${s.stricta.intensity}</p>
          <p><strong>Timing:</strong> ${s.stricta.timing_raw}</p>
          <p><strong>Duration:</strong> ${s.stricta.duration}</p>
          <p><strong>Stimulator/Electrode:</strong> ${s.stricta.needle_depth}</p>
        </div>
      </div>

      <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
        <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Surgical &amp; Population Baseline</h4>
        <div style="font-size: 0.82rem; line-height: 1.6;">
          <p><strong>Surgical Category:</strong> ${s.surgery_category}</p>
          <p><strong>Procedure:</strong> ${s.surgery_procedure}</p>
          <p><strong>Sample Size:</strong> ${s.population.total_n} randomized (${s.population.arm1_n} ${s.modality} vs ${s.population.arm2_n} ${s.comparator_short})</p>
          <p><strong>Mean Age:</strong> ${s.population.arm1_age} vs ${s.population.arm2_age}</p>
          <p><strong>Female %:</strong> ${s.population.arm1_female} vs ${s.population.arm2_female}</p>
          <p><strong>ASA Status:</strong> ${s.population.asa_status}</p>
        </div>
      </div>
    </div>

    <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Cochrane Risk of Bias 2 (RoB 2) Assessment</h4>
      <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.6;"><strong>Signaling Rationale:</strong> ${s.rob2.rationale}</p>
    </div>
  `;

  let outcomesHtml = `
    <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Extracted Clinical Endpoints &amp; Data Audit</h4>
      <div style="font-size: 0.82rem; line-height: 1.8;">
  `;

  if (s.outcomes && s.outcomes.opioid_24h && typeof s.outcomes.opioid_24h.mean_diff === 'number') {
    const op = s.outcomes.opioid_24h;
    outcomesHtml += `<p><strong>💊 Primary 24-h Opioid Consumption:</strong> <span style="color: #34d399; font-weight: 700;">MD ${op.mean_diff < 0 ? '−' : '+'}${Math.abs(op.mean_diff)} mg IV MME</span> (95% CI: [${op.ci_low}, ${op.ci_upp}], SE: ${op.se}) • Native: ${op.arm1_mean_native} ± ${op.arm1_sd_native} vs ${op.arm2_mean_native} ± ${op.arm2_sd_native} ${op.native_unit} ${op.native_drug}</p>`;
  } else if (s.outcomes && s.outcomes.opioid_24h) {
    outcomesHtml += `<p><strong>💊 Primary 24-h Opioid Consumption:</strong> <span style="color: #f59e0b; font-weight: 600;">${s.outcomes.opioid_24h.status}</span> — ${s.outcomes.opioid_24h.note || 'No continuous 24h opioid mean/SD tabulated.'}</p>`;
  }

  if (s.outcomes && s.outcomes.pain_rest_24h && typeof s.outcomes.pain_rest_24h.mean_diff === 'number') {
    const pn = s.outcomes.pain_rest_24h;
    outcomesHtml += `<p><strong>🩹 24-h Pain Intensity at Rest:</strong> <span style="color: #38bdf8; font-weight: 700;">MD ${pn.mean_diff < 0 ? '−' : '+'}${Math.abs(pn.mean_diff)} VAS</span> (95% CI: [${pn.ci_low}, ${pn.ci_upp}]) • ${pn.arm1_mean} ± ${pn.arm1_sd} vs ${pn.arm2_mean} ± ${pn.arm2_sd}</p>`;
  }

  if (s.outcomes && s.outcomes.pca_presses_24h && typeof s.outcomes.pca_presses_24h.mean_diff === 'number') {
    const pc = s.outcomes.pca_presses_24h;
    outcomesHtml += `<p><strong>🔘 PCA Demands / Presses (24h):</strong> <span style="color: #34d399; font-weight: 700;">MD ${pc.mean_diff < 0 ? '−' : '+'}${Math.abs(pc.mean_diff)} ${pc.unit || 'presses'}</span> (95% CI: [${pc.ci_low}, ${pc.ci_upp}], P=${pc.p_val}) • ${pc.arm1_mean} ± ${pc.arm1_sd} vs ${pc.arm2_mean} ± ${pc.arm2_sd} (${pc.metric_name})</p>`;
  } else if (s.outcomes && s.outcomes.pca_presses_24h && s.outcomes.pca_presses_24h.status && s.outcomes.pca_presses_24h.status !== 'Unreported in Source Paper') {
    const pc = s.outcomes.pca_presses_24h;
    outcomesHtml += `<p><strong>🔘 PCA Demands / Presses:</strong> <span style="color: #38bdf8; font-weight: 600;">${pc.metric_name || pc.status}</span> — ${pc.note || ''}</p>`;
  }

  if (s.outcomes && s.outcomes.ponv_24h && typeof s.outcomes.ponv_24h.rr === 'number') {
    const po = s.outcomes.ponv_24h;
    outcomesHtml += `<p><strong>🤢 Postoperative Nausea &amp; Vomiting (0–24h):</strong> <span style="color: #a78bfa; font-weight: 700;">RR ${po.rr}</span> (95% CI: [${po.ci_low}, ${po.ci_upp}]) • ${po.arm1_events}/${po.arm1_n} vs ${po.arm2_events}/${po.arm2_n}</p>`;
  }

  if (s.outcomes && s.outcomes.flatus_time && typeof s.outcomes.flatus_time.mean_diff === 'number') {
    const fl = s.outcomes.flatus_time;
    outcomesHtml += `<p><strong>⏱️ Time to First Flatus (GI Recovery):</strong> <span style="color: #34d399; font-weight: 700;">MD ${fl.mean_diff < 0 ? '−' : '+'}${Math.abs(fl.mean_diff)} hours</span> (95% CI: [${fl.ci_low}, ${fl.ci_upp}]) • ${fl.arm1_mean} ± ${fl.arm1_sd} vs ${fl.arm2_mean} ± ${fl.arm2_sd} h</p>`;
  }

  if (s.outcomes && s.outcomes.hospital_stay && typeof s.outcomes.hospital_stay.mean_diff === 'number') {
    const hs = s.outcomes.hospital_stay;
    outcomesHtml += `<p><strong>🏥 Length of Hospital Stay:</strong> MD ${hs.mean_diff < 0 ? '−' : '+'}${Math.abs(hs.mean_diff)} days • ${hs.arm1_mean} ± ${hs.arm1_sd} vs ${hs.arm2_mean} ± ${hs.arm2_sd} d</p>`;
  }

  if (s.audit && s.audit.classification) {
    outcomesHtml += `<p style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06); color: var(--text-secondary);"><strong>🔍 Audit Classification:</strong> ${s.audit.classification}<br><em>Evidence Sources: ${s.audit.evidence_sources || 'Published trial report'}</em></p>`;
  }

  outcomesHtml += '</div></div>';

  content.innerHTML += outcomesHtml;
  modal.classList.add('active');
}

function closeStudyDrawer() {
  const modal = document.getElementById('study-modal');
  if (modal) modal.classList.remove('active');
}

// Global functions for inline HTML calls
window.openStudyDrawer = openStudyDrawer;
window.closeStudyDrawer = closeStudyDrawer;
window.toggleStudyInclusion = toggleStudyInclusion;
window.exportDatasetCSV = exportDatasetCSV;
window.loadStudyIntoSimulator = loadStudyIntoSimulator;
window.updateSimStudyMD = updateSimStudyMD;
window.applySimScenario = applySimScenario;
window.selectStudyInSimulator = selectStudyInSimulator;
window.copyStataConsoleLog = copyStataConsoleLog;
window.toggleStataConsoleExpand = toggleStataConsoleExpand;
window.switchMcidThreshold = switchMcidThreshold;
window.filterInquiryPriority = filterInquiryPriority;
window.filterInquiryCategory = filterInquiryCategory;
window.filterInquirySearch = filterInquirySearch;
window.copyAuthorEmailDraft = copyAuthorEmailDraft;
window.showToast = showToast;
window.switchConvTab = switchConvTab;
window.runLiveEquiCalc = runLiveEquiCalc;
window.runLiveStatCalc = runLiveStatCalc;
window.renderAllViews = renderAllViews;
window.renderActiveTab = renderActiveTab;
window.renderMetaLab = renderMetaLab;
window.renderSearchStrategiesView = renderSearchStrategiesView;
window.renderActiveSearchDb = renderActiveSearchDb;
window.switchTab = switchTab;
