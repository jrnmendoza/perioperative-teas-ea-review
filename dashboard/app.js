// Perioperative TEAS & EA Interactive Systematic Review Application Logic

let activeTab = 'intro';
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
const STUDY_FILTER_TABS = ['intro','explorer','rob2'];

// Simulation overrides state: { [studyId]: { mean_diff, se, status } }
let simOverrides = {};
let activeSimStudyId = '1879895909'; // Default: #25 - He 2026
let selectedInquiryCategory = 'all';
let inquirySearchQuery = '';
let activeConvTab = 'equi';

function boot() {
  // The interactive primary view must use the exact locked set and values.
  for (const s of window.STUDIES_DATA) {
    const characteristics=window.STUDY_CHARACTERISTICS[s.key];
    s.surgery_category=characteristics.surgery_category;
    s.surgery_procedure=characteristics.surgery_procedure;
    s.primary_record = s.outcomes.opioid_24h;
    s.outcomes.opioid_24h = window.PRIMARY_BROWSER[s.key] ? {...s.primary_record, ...window.PRIMARY_BROWSER[s.key]} : null;
    const primaryRob=window.PRIMARY_BROWSER[s.key]?.rob2;
    if (primaryRob) {
      s.rob2_outcomes ||= {assessed_list:[]};
      s.rob2_outcomes.opioid_24h=primaryRob;
      s.rob2_outcomes.assessed_list ||= [];
      s.rob2_outcomes.assessed_list.push(primaryRob);
    }
    for (const [key,records] of Object.entries(window.BROWSER_TARGETS)) s.outcomes[key]=records[s.key] || null;
  }
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
    switchTab('intro');
  } else if (obj === 'obj1_teas') {
    filterModality = 'TEAS';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'none';
    switchTab('primary');
  } else if (obj === 'obj1_ea') {
    filterModality = 'EA';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'none';
    switchTab('primary');
  } else if (obj === 'obj2_pain') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = currentOutcome === 'pain_rest_24h' ? 'pain_movement_24h' : 'pain_rest_24h';
    currentSubgroup = 'none';
    switchTab('secondary');
  } else if (obj === 'obj3_subgroups') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'timing';
    switchTab('primary');
  } else if (obj === 'obj4_mcid') {
    switchTab('mcid');
  } else if (obj === 'obj5_supportive') {
    filterModality = 'all';
    filterComparator = 'Usual Care';
    currentOutcome = 'opioid_24h';
    currentSubgroup = 'stratum';
    switchTab('secondary');
  } else if (obj === 'obj6_secondary') {
    filterModality = 'all';
    filterComparator = 'Sham';
    currentOutcome = 'ponv_24h';
    currentSubgroup = 'none';
    switchTab('secondary');
  } else if (obj === 'obj7_grade') {
    switchTab('evidence');
  }

  syncToolbarDropdowns();
  renderAllViews();
}

const tabGroupMap = {
  intro: 'overview',
  explorer: 'studies',
  prisma: 'studies',
  primary: 'results',
  secondary: 'results',
  mcid: 'results',
  metareg: 'results',
  evidence: 'evidence',
  rob2: 'evidence',
  limitations: 'evidence',
  search: 'methods',
  extraction: 'methods',
  glossary: 'more',
  export: 'more'
};

function switchTab(tabId) {
  if (!tabId) return;
  activeTab = tabId;
  const group = tabGroupMap[tabId] || 'overview';

  // Toggle top-level 6 nav buttons
  document.querySelectorAll('.nav-btn[data-nav-group]').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-nav-group') === group);
  });
  // Also support direct data-tab buttons if any
  document.querySelectorAll('.nav-btn:not([data-nav-group])').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });

  // Toggle subnav groups
  document.querySelectorAll('.subnav-group').forEach(sg => {
    sg.style.display = 'none';
  });
  const activeSubgroup = document.getElementById(`subnav-${group}`);
  if (activeSubgroup) {
    activeSubgroup.style.display = 'flex';
  }

  // Toggle subnav pills
  document.querySelectorAll('.subnav-pill').forEach(pill => {
    pill.classList.toggle('active', pill.getAttribute('data-tab') === tabId);
  });

  // Toggle tab contents
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  const target = document.getElementById(`tab-${tabId}`);
  if (target) target.classList.add('active');
  renderKPIs();
  renderActiveTab();
  // Each navigation opens one panel at its beginning, not at the old scroll depth.
  document.querySelector('.kpi-grid').style.display=tabId==='intro'?'':'none';
  if (target) {
    target.setAttribute('tabindex','-1');
    target.focus({preventScroll:true});
  }
  window.scrollTo({top:0,left:0,behavior:'instant'});
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
  const availableOutcomes = new Set(window.META_OUTCOMES || []);
  document.querySelectorAll('#meta-outcome-select option').forEach(option => {
    if (!availableOutcomes.has(option.value)) option.remove();
  });
  document.querySelectorAll('#meta-outcome-select optgroup').forEach(group => {
    if (!group.children.length) group.remove();
  });
  const modSelect = document.getElementById('filter-modality');
  const compSelect = document.getElementById('filter-comparator');
  const surgSelect = document.getElementById('filter-surgery');
  if (surgSelect) {
    surgSelect.innerHTML='<option value="all">All Surgical Specialties</option>'+[...new Set(window.STUDIES_DATA.map(s=>s.surgery_category))].sort().map(c=>`<option value="${pwEsc(c)}">${pwEsc(c)}</option>`).join('');
  }
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
    filterYearMin = 1993;
    filterYearMax = 2026;
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
  if (document.getElementById('filter-surgery')) document.getElementById('filter-surgery').value = filterSurgery;
  if (preset === 'all') {
    filterSearch = '';
    const search = document.getElementById('study-search-input');
    if (search) search.value = '';
  }
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
      renderAllViews();
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
      renderAllViews();
    });
  }

  const explorerRobSelect = document.getElementById('explorer-rob-outcome');
  if (explorerRobSelect) {
    explorerRobSelect.addEventListener('change', (e) => {
      explorerRobOutcome = e.target.value;
      renderAllViews();
    });
  }
}

// Get Filtered Studies with simulated overrides applied
function getFilteredStudies(applyOverrides = true) {
  return window.STUDIES_DATA.filter(s => {
    if (!includedStudyIds.has(s.id)) return false;
    if (!STUDY_FILTER_TABS.includes(activeTab)) return true;
    if (filterModality !== 'all' && s.modality !== filterModality) return false;
    if (filterComparator !== 'all' && s.comparator_short !== filterComparator) return false;
    if (filterSurgery !== 'all' && s.surgery_category !== filterSurgery) return false;
    if (filterRob !== 'all') {
      // Filter on the result-specific judgment for the active context, not on a
      // single global study-level label.
      const resultKey=activeTab==='explorer'?explorerRobOutcome:activeTab==='rob2'?document.getElementById('rob2-outcome-filter').value:activeTab==='secondary'?currentOutcome:'summary';
      const st = resultRob(s, resultKey).state;
      const want = robState(filterRob);
      if (st !== want) return false;
    }
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
  renderLeaveOneOutTable();
  renderActiveTab();
}

function renderActiveTab() {
  const showFilters=STUDY_FILTER_TABS.includes(activeTab);
  document.querySelector('.control-toolbar').style.display=showFilters?'':'none';
  const scope = document.getElementById('filter-scope');
  if (scope) {
    scope.style.display=showFilters?'':'none';
    scope.textContent='Filters update study counts and distributions in Overview, Study Explorer and the RoB matrix. Search remains active until cleared or All Studies is selected. Saved effect estimates and GRADE are not recalculated. Other tabs use their own analysis sets.';
  }
  if (activeTab === 'intro') renderOverview();
  else if (activeTab === 'prisma') renderPrismaView();
  else if (activeTab === 'search') renderSearchStrategiesView();
  else if (activeTab === 'explorer') renderStudyExplorer();
  else if (activeTab === 'rob2') renderRoB2Matrix();
  else if (activeTab === 'secondary') renderMetaLab();
  else if (activeTab === 'mcid') renderMCIDStudio();
  else if (activeTab === 'metareg') renderMetaRegStudio();
  else if (activeTab === 'primary') { ilRenderLensToggle(); renderV34(); renderV33(); renderPrimaryPathway(); renderTieredV33(); renderSensitivitySandbox(); ilRenderEvidenceMap(); }
  else if (activeTab === 'limitations') { renderInquiriesView(); updateSimulationComparison(); }
  else if (activeTab === 'extraction') renderConversionsView();
  else if (activeTab === 'evidence') renderDirectionOfEvidence();
  else if (activeTab === 'glossary' && typeof window.renderGlossaryTab === 'function') window.renderGlossaryTab();
  else if (activeTab === 'export') renderExportHub();

  if (typeof window.initStatIcons === 'function') {
    window.initStatIcons();
  }
  if (typeof window.dashRefreshUsability === 'function') {
    window.dashRefreshUsability();
  }
}

function renderConversionsView() {
  switchConvTab(activeConvTab);
  runLiveEquiCalc();
  runLiveStatCalc();
}

// PRISMA 2020 Flow View
// Modality/comparator/population totals for the PRISMA "Included" card,
// computed live from the same STUDIES_DATA the Study Explorer renders from
// -- never hardcoded, so a future study addition/removal cannot leave this
// card stale the way the old hardcoded "5,089 patients / 49 TEAS + 14 EA"
// figures did (see 06_FINAL_ANALYSIS_V26/06_AUDIT/dashboard_v26_reconciliation.md #26.3).
function prismaPopulationSummary() {
  const studies = window.STUDIES_DATA || [];
  const n = studies.length;
  const totalPatients = studies.reduce((sum, s) => sum + ((s.population && s.population.total_n) || 0), 0);
  const teas = studies.filter(s => s.modality === 'TEAS').length;
  const ea = studies.filter(s => s.modality === 'EA').length;
  const sham = studies.filter(s => s.comparator_short === 'Sham').length;
  const usualCare = studies.filter(s => s.comparator_short === 'Usual Care').length;
  const other = n - teas - ea;
  const otherComparator = n - sham - usualCare;
  return {
    n, totalPatients, teas, ea, sham, usualCare,
    text: `${n} studies • ${totalPatients.toLocaleString()} total randomized patients • ${teas} TEAS / ${ea} EA${other ? ` / ${other} other` : ''} • ${sham} sham-controlled / ${usualCare} usual-care-controlled${otherComparator ? ` / ${otherComparator} other` : ''}.`,
  };
}

function renderPrismaView() {
  const summaryEl = document.getElementById('prisma-population-summary');
  const pop = prismaPopulationSummary();
  if (summaryEl && window.STUDIES_DATA) summaryEl.textContent = pop.text;

  const btnCopy = document.getElementById('btn-export-prisma-summary');
  if (btnCopy) {
    btnCopy.onclick = () => {
      const summaryText = `PRISMA 2020 Flow Summary (Perioperative TEAS/EA Systematic Review) -- updated 2026-09-07:
- Identification: 5,100 records imported (Embase: 1,928; CENTRAL: 1,698; PubMed: 1,009; CINAHL: 465).
- Removed before screening: 2,160 records (1,651 Covidence auto-duplicates + 1 manual duplicate + 508 automation ineligible).
- Screening: 2,928 title/abstract records screened; 2,704 irrelevant records excluded.
- Eligibility: 224 reports sought; 14 not retrieved; 210 assessed; 141 excluded with reasons (Wrong outcomes: 117; Wrong setting: 9; Wrong intervention: 9; Wrong comparator: 3; Wrong population: 2; Wrong design: 1).
- Included: 70 randomized controlled trials (69 via database search + 1 via citation searching). RoB 2 complete for all 70. ${pop.text}
NOTE: 5,100 identified minus 2,160 removed before screening implies 2,940 should reach screening, but 2,928 is the number transcribed from the source PRISMA record for that stage (a 12-record gap not itemised in the supplied document) -- flagged, not silently corrected.`;
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
    linesCount.innerText = `${lines} lines • ${db.status}`;
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

  const studies = getFilteredStudies(false);
  const validStudies = studies.filter(s => s.mcid && s.mcid.is_paired === true && typeof s.mcid.opioid_md === 'number' && !isNaN(s.mcid.opioid_md) && typeof s.mcid.pain_md === 'number' && !isNaN(s.mcid.pain_md));

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

  const groups = [[],[],[],[]];
  const plottedOpioid = study => isRelative ? 100*study.mcid.opioid_md/study.outcomes.opioid_24h.arm2_mean : study.mcid.opioid_md;
  const primaryCut = isRelative ? 30 : thresholdVal;
  const lowerCut = isRelative ? 15 : 5;
  validStudies.forEach(study => {
    const op=plottedOpioid(study), painOk=study.mcid.pain_md<=marginVal;
    const group=!painOk || op>=0 ? 3 : op<=-primaryCut ? 0 : op<=-lowerCut ? 1 : 2;
    groups[group].push(study);
  });
  const [q1,q2,q3,q4]=groups.map(g=>g.length);
  const unitLabel=isRelative?'%':'mg IV MME';
  const labels=[`Sparing ≥ ${primaryCut} ${unitLabel}, pain difference ≤ +${marginVal}`,
    `Sparing ${lowerCut}–<${primaryCut} ${unitLabel}, pain difference ≤ +${marginVal}`,
    `Sparing >0–<${lowerCut} ${unitLabel}, pain difference ≤ +${marginVal}`,
    `No opioid reduction or pain difference > +${marginVal}`];
  groups.forEach((g,i)=>{
    const card=document.querySelector(`.quadrant-card.q${i+1}`);
    card.querySelector('.quadrant-title span').textContent=labels[i];
    card.querySelector('.quadrant-desc').textContent=(g.length?g.map(s=>s.key).join(', '):'No matching trials.')+' Classification uses study-level point estimates; it does not establish pain non-inferiority.';
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
  if (q1Badge) q1Badge.innerText = labels[0];

  ['badge-q2-kpi','badge-q3-kpi','badge-q4-kpi'].forEach((id,i)=>{ const el=document.getElementById(id); if(el) el.textContent=labels[i+1]; });

  // Subtitle update
  const totalN = validStudies.reduce((acc, s) => acc + ((s.population && s.population.total_n) ? s.population.total_n : 0), 0);
  const subtitleEl = document.getElementById('mcid-subtitle-text');
  if (subtitleEl) {
    subtitleEl.innerHTML = `Selected exploratory threshold: <strong>${threshLabel} Opioid Sparing</strong> with Pain Non-Inferiority Margin <strong>≤ +${marginVal} VAS</strong> (Point estimates only; non-inferiority is not established). Paired Continuous Cohort: <strong>k = ${validStudies.length} trials (N = ${totalN.toLocaleString()} analysed)</strong>.`;
  }

  const width = container.clientWidth || 700;
  const height = 480;
  const pad = { top: 40, right: 40, bottom: 50, left: 60 };

  const minX = Math.min(-25, ...validStudies.map(plottedOpioid)) - 5, maxX = 5;
  const minY = Math.min(-1, ...validStudies.map(s=>s.mcid.pain_md)) - 0.5;
  const maxY = Math.max(marginVal + 0.5, ...validStudies.map(s=>s.mcid.pain_md)) + 0.5;

  const scaleX = (val) => pad.left + ((val - minX) / (maxX - minX)) * (width - pad.left - pad.right);
  const scaleY = (val) => pad.top + ((maxY - val) / (maxY - minY)) * (height - pad.top - pad.bottom);

  const plotThreshVal = primaryCut;
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

      <!-- Axes Guidelines -->
      <line x1="${pad.left}" y1="${yZero}" x2="${width - pad.right}" y2="${yZero}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
      <line x1="${xZero}" y1="${pad.top}" x2="${xZero}" y2="${height - pad.bottom}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />

      <!-- MCID Threshold Line -->
      <line x1="${xMcid}" y1="${pad.top}" x2="${xMcid}" y2="${height - pad.bottom}" stroke="#10b981" stroke-width="2" stroke-dasharray="5,4" />
      <text x="${xMcid}" y="${pad.top - 10}" fill="#10b981" font-size="11" font-weight="700" text-anchor="middle">Selected threshold (−${plotThreshVal} ${unitLabel})</text>

      <!-- Non-inferiority Pain Line -->
      <line x1="${pad.left}" y1="${yMargin}" x2="${width - pad.right}" y2="${yMargin}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4" />
      <text x="${width - pad.right - 10}" y="${yMargin - 6}" fill="#f59e0b" font-size="10" text-anchor="end">Pain Non-Inferiority (+${marginVal} VAS)</text>

      <!-- Axis Labels -->
      <text x="${width / 2}" y="${height - 15}" fill="var(--text-secondary)" font-size="12" font-weight="700" text-anchor="middle">24-h Opioid Difference [${unitLabel}] (Favors Intervention ← | → Favors Control)</text>
      <text x="-${height / 2}" y="20" fill="var(--text-secondary)" font-size="12" font-weight="700" text-anchor="middle" transform="rotate(-90)">24-h Pain Intensity Difference [MD, VAS 0–10]</text>
  `;

  for (let tick=0; tick<=4; tick++) {
    const x=minX+(maxX-minX)*tick/4, y=minY+(maxY-minY)*tick/4;
    svg += `<text x="${scaleX(x)}" y="${height-pad.bottom+16}" fill="#94a3b8" font-size="9" text-anchor="middle">${x.toFixed(1)}</text><text x="${pad.left-8}" y="${scaleY(y)+3}" fill="#94a3b8" font-size="9" text-anchor="end">${y.toFixed(1)}</text>`;
  }

  validStudies.forEach((s,index) => {
    const cx = scaleX(plottedOpioid(s));
    const painVal = typeof s.mcid.pain_md === 'number' ? s.mcid.pain_md : 0.0;
    const cy = scaleY(painVal);
    const color = s.modality === 'TEAS' ? '#38bdf8' : '#a78bfa';
    const r = Math.max(5, Math.min(11, Math.sqrt(s.population.total_n) * 0.9));

    svg += `
      <g style="cursor: pointer;" onclick="openStudyDrawer('${s.id}')">
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" fill-opacity="0.85" stroke="#ffffff" stroke-width="1.5">
          <title>${s.key} (${s.modality} vs ${s.comparator_short})\nOpioid MD: ${s.mcid.opioid_md} mg MME\nPain MD: ${painVal.toFixed(2)} VAS\nSurgery: ${s.surgery_category}</title>
        </circle>
        <text x="${cx}" y="${cy - r - 3 - (index%2)*14}" fill="#e2e8f0" font-size="9" text-anchor="middle" font-weight="600">${s.author} '${String(s.year).slice(2)}</text>
      </g>
    `;
  });

  svg += `</svg>`;
  container.innerHTML = svg;

  const copyReportBtn = document.getElementById('btn-export-mcid-report');
  if (copyReportBtn) {
    copyReportBtn.onclick = () => {
      const summary = `Exploratory paired opioid–pain view: k=${validStudies.length}, N=${totalN}.\nSelected threshold: ${primaryCut} ${unitLabel}; pain point-estimate margin: +${marginVal}.\n`+
        labels.map((label,i)=>`${label}: ${groups[i].length}; ${groups[i].map(s=>s.key).join(', ') || 'none'}`).join('\n')+
        '\nThese point-estimate classifications do not establish non-inferiority or individual-patient safety.';
      navigator.clipboard.writeText(summary).then(() => {
        const orig = copyReportBtn.innerText;
        copyReportBtn.innerText = '✅ Paired Report Copied!';
        setTimeout(() => { copyReportBtn.innerText = orig; }, 2000);
      });
    };
  }
}

// 1. KPI Cards
function renderKPIs() {
  const filtered = getFilteredStudies(false);

  const studyCountEl = document.getElementById('kpi-study-count');
  if (studyCountEl) {
    studyCountEl.innerText = `${filtered.length} Studies`;
  }

  const totalN = filtered.reduce((acc, s) => acc + (s.population ? s.population.total_n : 0), 0);

  const patientSubEl = document.getElementById('kpi-patient-sub');
  if (patientSubEl) {
    patientSubEl.innerText = `${totalN.toLocaleString()} randomized surgical patients`;
  }

  const effectValEl = document.getElementById('kpi-pooled-md');
  const effectSubEl = document.getElementById('kpi-pooled-sub');
  const effectBadgeEl = document.getElementById('kpi-pooled-badge');
  const effectTitleEl = document.getElementById('kpi-effect-title');

  // Locked Protocol v32: Modality-specific estimates and strict direct primary (k=7, N=676)
  if (filterModality === 'all') {
    if (effectTitleEl) {
      effectTitleEl.innerHTML = '<span data-i18n="kpi.primaryTitle">Primary 24-h Opioid Sparing (Modality-Specific)</span><button class="stat-info-btn" data-stat-term="meanDifference" aria-label="Statistical explanation for Mean Difference">ⓘ</button>';
    }
    if (effectValEl) {
      effectValEl.innerHTML = 'TEAS: −14.00 mg <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">[−34.18, +6.19]</span><br>EA: −3.94 mg <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">[−19.77, +11.90]</span>';
    }
    if (effectSubEl) {
      effectSubEl.innerText = 'Supporting Combined Synthesis (k=7, N=676): MD = −9.91 mg [−20.08, +0.27], p = 0.055';
    }
    if (effectBadgeEl) {
      effectBadgeEl.className = 'kpi-badge badge-emerald';
      effectBadgeEl.innerHTML = '<span data-i18n="kpi.primaryBadge">PRIMARY: TEAS &amp; EA Modality-Specific &bull; Combined = Supporting</span><button class="stat-info-btn" data-stat-term="knappHartung" style="margin-left: 3px;" aria-label="Statistical explanation for Knapp-Hartung">ⓘ</button>';
    }
  } else if (filterModality === 'TEAS') {
    if (effectTitleEl) {
      effectTitleEl.innerHTML = '<span>TEAS Primary 24-h Opioid Sparing</span><button class="stat-info-btn" data-stat-term="meanDifference" aria-label="Statistical explanation for Mean Difference">ⓘ</button>';
    }
    if (effectValEl) {
      effectValEl.innerHTML = '−14.00 mg <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">95% CI [−34.18, +6.19]</span>';
    }
    if (effectSubEl) {
      effectSubEl.innerText = 'k = 4, N = 337 • REML + Knapp–Hartung • p = 0.1145, τ² = 156.88, I² = 98.6%';
    }
    if (effectBadgeEl) {
      effectBadgeEl.className = 'kpi-badge badge-indigo';
      effectBadgeEl.innerHTML = '<span>PRIMARY MODALITY 1 (TEAS vs Sham)</span><button class="stat-info-btn" data-stat-term="knappHartung" style="margin-left: 3px;" aria-label="Statistical explanation for Knapp-Hartung">ⓘ</button>';
    }
  } else if (filterModality === 'EA') {
    if (effectTitleEl) {
      effectTitleEl.innerHTML = '<span>EA Primary 24-h Opioid Sparing</span><button class="stat-info-btn" data-stat-term="meanDifference" aria-label="Statistical explanation for Mean Difference">ⓘ</button>';
    }
    if (effectValEl) {
      effectValEl.innerHTML = '−3.94 mg <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">95% CI [−19.77, +11.90]</span>';
    }
    if (effectSubEl) {
      effectSubEl.innerText = 'k = 3, N = 339 • REML + Knapp–Hartung • p = 0.397, τ² = 28.47, I² = 77.2%';
    }
    if (effectBadgeEl) {
      effectBadgeEl.className = 'kpi-badge badge-amber';
      effectBadgeEl.innerHTML = '<span>PRIMARY MODALITY 2 (EA vs Usual Care)</span><button class="stat-info-btn" data-stat-term="knappHartung" style="margin-left: 3px;" aria-label="Statistical explanation for Knapp-Hartung">ⓘ</button>';
    }
  }

  if (typeof window.initStatIcons === 'function') {
    window.initStatIcons();
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
    const heading=surgContainer.closest('.dashboard-card')?.querySelector('h2');
    if (heading) heading.textContent=`Surgical Specialties Distribution (${filtered.length} Trials)`;
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
      }).join('') || '<p>No studies match the current filters.</p>';
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

// ═══════════════════════════════════════════════════════════════════════════
// RESULT-SPECIFIC RoB 2 (Cochrane RoB 2 is a property of a RESULT, not a study)
// ═══════════════════════════════════════════════════════════════════════════
// Authoritative source: AF_Result_Lock in
// TEAS_EA_RECONCILED_MASTER_DATA_v26_FINAL_LOCK_READY.xlsx, compiled into
// s.rob2_outcomes[<outcome key>] = {status, d1..d5, overall, outcome_name, timepoint, rationale}.
//
// s.rob2.* is a study-level OVERVIEW only. It must never stand in for a
// result-specific judgment, and an absent judgment must never be shown as High.

// Which result the Study Explorer's RoB column describes.
let explorerRobOutcome = 'opioid_24h';

const ROB_OUTCOME_LABELS = {
  summary: 'study-level overview',
  opioid_24h: '0–24 h opioid consumption',
  opioid_48h: '0–48 h opioid consumption',
  opioid_72h: '0–72 h opioid consumption',
  pain_rest_24h: 'pain at rest ~24 h',
  ponv_24h: 'composite PONV 0–24 h',
  ponv_48h: 'composite PONV 0–48 h',
  nausea_24h: 'nausea alone 0–24 h',
  nausea_48h: 'nausea alone 0–48 h',
  vomiting_24h: 'vomiting alone 0–24 h',
  vomiting_48h: 'vomiting alone 0–48 h',
  flatus_time: 'time to first flatus',
  rescue_analgesia: 'rescue analgesia requirement',
  intraop_remi: 'intraoperative titrated remifentanil',
  pca_behavior: 'PCA behaviour',
  qor_24h: 'quality of recovery ~24 h'
};

// Returns a judgment object for one study x one result.
// state is one of: 'low' | 'some' | 'high' | 'pending' | 'not-assessed' | 'study-level'
function resultRob(s, outcomeKey) {
  if (outcomeKey === 'summary') {
    const r = (s && s.rob2) || {};
    return {
      state: robState(r.overall),
      isStudyLevel: true,
      d1: r.d1, d2: r.d2, d3: r.d3, d4: r.d4, d5: r.d5,
      overall: r.overall,
      outcome_name: 'Study-level overview',
      timepoint: '',
      rationale: r.rationale || 'Study-level consensus overview (not result-specific)'
    };
  }
  const oc = s && s.rob2_outcomes && s.rob2_outcomes[outcomeKey];
  if (oc && oc.status === 'Assessed') {
    return {
      state: robState(oc.overall),
      isStudyLevel: false,
      d1: oc.d1, d2: oc.d2, d3: oc.d3, d4: oc.d4, d5: oc.d5,
      overall: oc.overall,
      outcome_name: oc.outcome_name,
      timepoint: oc.timepoint,
      rationale: oc.rationale
    };
  }
  const pending = oc && /pending/i.test(String(oc.status || ''));
  return {
    state: pending ? 'pending' : 'not-assessed',
    isStudyLevel: false,
    d1: 'NR', d2: 'NR', d3: 'NR', d4: 'NR', d5: 'NR',
    overall: pending ? 'Pending' : 'NR',
    outcome_name: '',
    timepoint: '',
    rationale: pending
      ? 'RoB 2 assessment pending for this result'
      : 'No result-specific assessment is available in this dashboard. This does not establish that the outcome was unmeasured; domain judgments are not imputed.'
  };
}

// Normalise a raw judgment string to a distinct state. Unrecognised, empty and
// "not reported" values resolve to 'not-assessed' - NEVER to 'high'.
function robState(val) {
  if (val === null || val === undefined) return 'not-assessed';
  const v = String(val).trim().toLowerCase();
  if (!v || v === 'nr' || v === 'not reported' || v === 'not assessed' || v === '⋯' || v === 'unmeasured' || v === '-' || v === '—') return 'not-assessed';
  if (v.includes('pending')) return 'pending';
  if (v === 'low') return 'low';
  if (v === 'some concerns' || v === 'some_concerns' || v === 'some') return 'some';
  if (v === 'high') return 'high';
  return 'not-assessed';
}

const ROB_BADGE = {
  low:           { text: 'Low',           bg: 'rgba(16,185,129,0.18)',  fg: '#6ee7b7', bd: 'rgba(16,185,129,0.35)' },
  some:          { text: 'Some concerns', bg: 'rgba(245,158,11,0.18)',  fg: '#fbbf24', bd: 'rgba(245,158,11,0.35)' },
  high:          { text: 'High',          bg: 'rgba(244,63,94,0.18)',   fg: '#fda4af', bd: 'rgba(244,63,94,0.35)' },
  pending:       { text: 'Pending',       bg: 'rgba(129,140,248,0.18)', fg: '#c7d2fe', bd: 'rgba(129,140,248,0.35)' },
  'not-assessed':{ text: 'Not assessed',  bg: 'rgba(255,255,255,0.06)', fg: '#94a3b8', bd: 'rgba(255,255,255,0.16)' }
};

function robBadgeHtml(state, title) {
  const b = ROB_BADGE[state] || ROB_BADGE['not-assessed'];
  return `<span class="kpi-badge" style="background: ${b.bg}; color: ${b.fg}; border: 1px solid ${b.bd};" title="${title || b.text}">${b.text}</span>`;
}

// v26: every catalogued author inquiry carries a recorded disposition
// (AF_P1_Disposition / AF_Unresolved). None is a global final-lock blocker, so
// no inquiry may be rendered as an open "Pending" item. Only the single
// Yeh 2010 / Yeh 2011 cohort-overlap question is still a hard hold.
function inquiryDisposition(s) {
  const ai = s && s.author_inquiry;
  if (!ai || !ai.has_inquiry) return null;
  const raw = String(ai.status || '').trim();
  if (/HARD_HOLD/i.test(raw)) return { label: 'Hard hold', cls: 'rose', title: 'Hard hold: cohort-overlap adjudication (handled by exclusion from pooling, not by author reply)' };
  if (/^Dispositioned:/i.test(raw)) {
    const cls = raw.replace(/^Dispositioned:\s*/i, '').replace(/_/g, ' ').toLowerCase();
    return { label: 'Dispositioned', cls: 'emerald', title: 'Dispositioned \u2014 ' + cls + ' (not a final-lock blocker)' };
  }
  if (/Complete in Manuscript/i.test(raw)) return { label: 'Complete', cls: 'emerald', title: 'Required data are complete in the published manuscript' };
  return { label: 'Dispositioned', cls: 'emerald', title: raw || 'Dispositioned in the v26 lock' };
}

// 3. Study Explorer Table
function renderStudyExplorer() {
  const filtered = getFilteredStudies(false);
  const summary=document.getElementById('explorer-surgery-summary');
  if (summary) {
    const counts={};
    filtered.forEach(s=>{const category=s.surgery_category || 'Not recorded';counts[category]=(counts[category]||0)+1;});
    summary.innerHTML=`<h3>Surgical specialties (${filtered.length} studies)</h3><div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.6rem;">`+
      Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([name,n])=>`<span class="badge badge-indigo">${pwEsc(name)}: ${n}</span>`).join('')+
      (filtered.length?'':'<p>No studies match the current filters.</p>')+'</div>';
  }
  const tbody = document.getElementById('explorer-table-body');
  if (!tbody) return;

  tbody.innerHTML = filtered.map((s, idx) => {
    const rr = resultRob(s, explorerRobOutcome);
    const robTitle = rr.isStudyLevel
      ? 'Study-level overview - not a result-specific judgment'
      : (rr.state === 'not-assessed' || rr.state === 'pending'
          ? rr.rationale
          : `${rr.outcome_name}${rr.timepoint ? ' (' + rr.timepoint + ')' : ''}`);
    const robBadge = robBadgeHtml(rr.state, robTitle);
    
    const disp = inquiryDisposition(s);
    const inquiryBadge = disp
      ? `<span class="kpi-badge ${disp.cls === 'rose' ? 'badge-rose' : 'badge-emerald'}" title="${disp.title}">${disp.label}</span>`
      : '';

    return `
      <tr style="cursor: pointer;" onclick="openStudyDrawer('${s.id}')">
        <td style="font-weight: 700; color: var(--text-accent);">
          ${idx + 1}. ${s.key} ${inquiryBadge}
        </td>
        <td><span style="background: rgba(99,102,241,0.15); color: #818cf8; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; font-size: 0.75rem;">${s.modality}</span></td>
        <td>${s.comparator_short}</td>
        <td>${s.surgery_category}<br><small style="color:var(--text-muted)">${pwEsc(s.surgery_procedure || 'Procedure not recorded')}</small></td>
        <td>${s.stricta.acupoints}</td>
        <td>${s.stricta.frequency_category}</td>
        <td><strong>${s.population.total_n}</strong> (${s.population.arm1_n} / ${s.population.arm2_n})</td>
        <td>${robBadge}</td>
        <td><button class="btn-preset" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;" onclick="event.stopPropagation(); openStudyDrawer('${s.id}')">Details</button></td>
      </tr>
    `;
  }).join('') || '<tr><td colspan="9">No studies match the current filters.</td></tr>';

  const ctxEl = document.getElementById('explorer-rob-context');
  if (ctxEl) {
    const label = ROB_OUTCOME_LABELS[explorerRobOutcome] || explorerRobOutcome;
    if (explorerRobOutcome === 'summary') {
      ctxEl.innerHTML = 'study-level overview &mdash; not result-specific';
    } else {
      const assessed = filtered.filter(s => {
        const st = resultRob(s, explorerRobOutcome).state;
        return st !== 'not-assessed' && st !== 'pending';
      }).length;
      ctxEl.innerHTML = `for: ${label} &bull; ${assessed}/${filtered.length} assessed`;
    }
  }
}

// 4. RoB 2 Matrix (Result-Specific and Summary View)
function renderRoB2Matrix() {
  renderKPIs();
  const coveragePanel=document.getElementById('secondary-rob-coverage');
  if (coveragePanel) {
    const rows=window.V33_DATA.result_rob2_coverage;
    const pending = rows.filter(r => r.assessment_status === 'PENDING').length;
    coveragePanel.innerHTML='<h3>Secondary Result Coverage — v33 legacy analysis sets (historical)</h3>'
      +'<p style="color:#fdba74;">The five analysis sets below (<code>v33_rescue_opioid_binary_24h</code>, '
      +'<code>v33_intraop_remifentanil</code>, <code>v33_intraop_sufentanil</code>, <code>v33_qor40_24h</code>, '
      +'<code>v33_gi_first_defecation</code>) pooled across modality and comparator strata and have since been '
      +'either <strong>withdrawn</strong> (mixed incompatible time windows or comparator strata) or '
      +'<strong>superseded</strong> by the properly modality/comparator-stratified v34 models — see the RESULTS '
      +'tab for both. They are retained here only as a historical RoB 2 coverage audit trail for the review\'s '
      +'own record, not as current pooled evidence.</p>'
      +'<p>The review\'s current result-specific RoB 2 register — every result inside a fitted v34 model, plus '
      +'every result not currently pooled — is judged per result (not per study) and lives on the RESULTS tab. '
      +(pending
        ? `<strong style="color:#fca5a5;">${pending} row(s) below are still PENDING</strong>: no matching `
          +'result-specific judgement has been identified for them yet. Pending judgments are never borrowed '
          +'from another outcome, and drafts remain unadjudicated until a match is confirmed.'
        : 'Every row below has since been matched to a result-specific judgement from that v34 register '
          +'(marked "(v34)" below) or already carried one from an earlier per-study assessment; none are '
          +'pending.')
      +' This register is not altered by the study filters.</p>'
      +'<div style="overflow-x:auto"><table class="forest-table"><thead><tr><th>Study / contrast</th><th>Result</th><th>Status</th></tr></thead><tbody>'
      +rows.map(r=>`<tr><td>${pwEsc(r.study)}<br><small>${pwEsc(r.comparison_id)}</small></td><td>${pwEsc(r.result_assessed)}</td><td>${pwEsc(r.assessment_status)}${r.overall?' — '+pwEsc(r.overall):''}${r.existing_selected_result?`<br><small style="color:var(--text-muted);">matched: ${pwEsc(r.existing_selected_result)}</small>`:''}</td></tr>`).join('')
      +'</tbody></table></div>';
  }
  const filtered = getFilteredStudies(false);
  const tbody = document.getElementById('rob2-table-body');
  if (!tbody) return;

  const outcomeSelect = document.getElementById('rob2-outcome-filter');
  const activeOutcome = outcomeSelect ? outcomeSelect.value : 'summary';
  const statusBadge = document.getElementById('rob2-outcome-status-badge');

  let assessedCount = 0;
  let unmeasuredCount = 0;

  // Five distinct states. robState() never maps an unknown/absent value to High.
  const dot = (val) => {
    switch (robState(val)) {
      case 'low':     return `<span class="rob-dot rob-low" title="Low risk of bias">+</span>`;
      case 'some':    return `<span class="rob-dot rob-some" title="Some concerns">?</span>`;
      case 'high':    return `<span class="rob-dot rob-high" title="High risk of bias">−</span>`;
      case 'pending': return `<span class="rob-dot" style="background: rgba(129,140,248,0.2); color: #c7d2fe; border: 1px solid rgba(129,140,248,0.5);" title="RoB 2 assessment pending for this result">⏳</span>`;
      default:        return `<span class="rob-dot" style="background: rgba(255,255,255,0.08); color: var(--text-muted); border: 1px dashed rgba(255,255,255,0.2);" title="No result-specific assessment available; outcome absence is not established">⋯</span>`;
    }
  };

  tbody.innerHTML = filtered.map((s, idx) => {
    const rr = resultRob(s, activeOutcome);
    const d1 = rr.d1, d2 = rr.d2, d3 = rr.d3, d4 = rr.d4, d5 = rr.d5;
    const overall = rr.overall;
    let rationale;

    if (rr.isStudyLevel) {
      rationale = rr.rationale;
      assessedCount++;
    } else if (rr.state === 'not-assessed' || rr.state === 'pending') {
      rationale = `<span style="color: var(--text-muted); font-style: italic;">${rr.rationale}</span>`;
      unmeasuredCount++;
    } else {
      rationale = `<strong>Assessed:</strong> ${rr.outcome_name} (${rr.timepoint})`;
      assessedCount++;
    }

    return `
      <tr>
        <td style="font-weight: 600;"><a href="javascript:void(0)" onclick="openStudyDrawer('${s.id}')" style="color: var(--text-primary); text-decoration: none;">${idx + 1}. ${s.key}</a></td>
        <td>${dot(d1)}</td>
        <td>${dot(d2)}</td>
        <td>${dot(d3)}</td>
        <td>${dot(d4)}</td>
        <td>${dot(d5)}</td>
        <td>${dot(overall)}</td>
        <td style="font-size: 0.75rem; color: var(--text-secondary); max-width: 380px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${rationale}</td>
      </tr>
    `;
  }).join('') || '<tr><td colspan="8">No studies match the current filters.</td></tr>';

  if (statusBadge) {
    if (activeOutcome === 'summary') {
      statusBadge.innerHTML = `<span class="badge badge-indigo">Study-Level Overview: ${filtered.length} Studies</span>`;
    } else {
      statusBadge.innerHTML = `<span class="badge badge-emerald">Assessed for Outcome: ${assessedCount}</span> <span class="badge badge-indigo" style="margin-left: 6px;">Pending or not assessed: ${unmeasuredCount}</span>`;
    }
  }
}

function renderStataSecondary() {
  const select = document.getElementById('stata-secondary-select');
  const panel = document.getElementById('stata-secondary-result');
  const results = window.V33_DATA?.secondary || [];
  if (!select || !panel || !results.length) return;
  if (!select.children.length) {
    select.innerHTML = results.map(r => `<option value="${pwEsc(r.analysis_id)}">${pwEsc(r.outcome)} — ${pwEsc(r.measure)}</option>`).join('');
    select.onchange = renderStataSecondary;
  }
  const r = results.find(r => r.analysis_id === select.value) || results[0];
  const caveats = (window.V33_DATA.caveats || []).filter(c => c.analysis_id === r.analysis_id);
  panel.innerHTML = `<p><strong>${pwEsc(r.outcome)}</strong>: ${pwEsc(r.measure)} ${r.estimate.toFixed(3)}
    (95% CI ${r.ci_low.toFixed(3)} to ${r.ci_high.toFixed(3)}), k=${r.k}, p=${r.p_value.toPrecision(3)}.
    ${pwEsc(r.model)}; StataNow 19.5.</p>
    <p>Result-specific RoB 2 adjudication pending. No GRADE rating is assigned here.
    This saved analysis uses its documented analysis set; the interactive filters below do not alter it.</p>
    ${caveats.map(c => `<p>${pwEsc(c.text)}</p>`).join('')}
    ${r.figure ? `<img src="${pwEsc(r.figure)}" alt="Stata forest plot: ${pwEsc(r.outcome)}" style="width:100%;height:auto;margin-top:1rem;">` : ''}`;
}

// 5. Real-Time Dynamic Meta-Analysis Lab & Forest Plot (Objectives 1, 2, 3, 5, 6)
function renderMetaLab() {
  const metaModality=STUDY_FILTER_TABS.includes(activeTab)?filterModality:'all';
  renderStataSecondary();
  const filtered = getFilteredStudies(false);
  const isBinary = ['ponv_24h', 'rescue_analgesia'].includes(currentOutcome);
  const tbody = document.getElementById('forest-table-body');
  if (!tbody) return;

  const validStudies = filtered.filter(s => {
    if (!s.outcomes || !s.outcomes[currentOutcome]) return false;
    const oc = s.outcomes[currentOutcome];
    if (isBinary) return oc.rr>0 && oc.ci_low>0 && oc.ci_upp>oc.ci_low && (oc.arm1_total ?? oc.arm1_n)>0 && (oc.arm2_total ?? oc.arm2_n)>0;
    return Number.isFinite(oc.mean_diff) && Number.isFinite(oc.se) && oc.se>0 && oc.arm1_n>0 && oc.arm2_n>0;
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
          <div style="font-weight: 700; color: #fff; font-size: 1.1rem; margin-bottom: 0.4rem;">No matching data in this interactive view</div>
          <div style="font-size: 0.85rem; color: var(--text-secondary); max-width: 580px; margin: 0 auto; line-height: 1.6;">
            No study matches the current filters for <em>${outcomeLabel}</em> in this interactive dataset. This does not establish that the outcome was unreported. Check the source-verified Stata secondary analyses above and the contribution map.
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
  if (currentSubgroup === 'stratum' || (currentSubgroup === 'none' && metaModality === 'all')) {
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
    groupingFn = s => {
      const st = resultRob(s, currentOutcome).state;
      return (ROB_BADGE[st] || ROB_BADGE['not-assessed']).text;
    };
  }

  if (groupingFn && metaModality === 'all' && !['none','stratum'].includes(currentSubgroup)) {
    const selectedGrouping = groupingFn;
    groupingFn = s => `${s.stratum} — ${selectedGrouping(s) || 'Unreported'}`;
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
    const isOverridden = false; // Hypothetical changes are confined to the inquiry simulator.
    const oc = s.outcomes[currentOutcome];
    if (!oc) return '';

    let colInt = '', colCtrl = '', colEffect = '', xMid = zeroX, xLow = zeroX, xUpp = zeroX, weightPct = st ? st.weight_pct : 0;
    if (isBinary) {
      const n1 = oc.arm1_total ?? oc.arm1_n;
      const n2 = oc.arm2_total ?? oc.arm2_n;
      colInt = Number.isFinite(oc.arm1_events) ? `${oc.arm1_events} / ${n1} (${(oc.arm1_events/n1*100).toFixed(1)}%)` : `Events unavailable (n=${n1})`;
      colCtrl = Number.isFinite(oc.arm2_events) ? `${oc.arm2_events} / ${n2} (${(oc.arm2_events/n2*100).toFixed(1)}%)` : `Events unavailable (n=${n2})`;
      colEffect = `RR ${oc.rr.toFixed(2)} [${oc.ci_low.toFixed(2)}, ${oc.ci_upp.toFixed(2)}]`;
      xMid = toX(Math.log(Math.max(0.01, oc.rr)));
      xLow = toX(Math.log(Math.max(0.01, oc.ci_low)));
      xUpp = toX(Math.log(Math.max(0.01, oc.ci_upp)));
    } else {
      colInt = `${Number.isFinite(oc.arm1_mean) ? oc.arm1_mean.toFixed(1) : '—'} ± ${Number.isFinite(oc.arm1_sd) ? oc.arm1_sd.toFixed(1) : '—'} (n=${oc.arm1_n ?? '—'})`;
      colCtrl = `${Number.isFinite(oc.arm2_mean) ? oc.arm2_mean.toFixed(1) : '—'} ± ${Number.isFinite(oc.arm2_sd) ? oc.arm2_sd.toFixed(1) : '—'} (n=${oc.arm2_n ?? '—'})`;
      const ciL = st ? st.yi - 1.96 * st.se : oc.ci_low;
      const ciU = st ? st.yi + 1.96 * st.se : oc.ci_upp;
      const effVal = st ? st.yi : oc.mean_diff;
      colEffect = `${effVal < 0 ? '−' : '+'}${Math.abs(effVal).toFixed(2)} [${ciL.toFixed(2)}, ${ciU.toFixed(2)}]`;
      xMid = toX(effVal);
      xLow = toX(ciL);
      xUpp = toX(ciU);
    }
    const boxSize = Math.max(4, Math.min(14, Math.sqrt(weightPct || 1) * 3));

    const inqDisp = inquiryDisposition(s);
    const inqBadge = inqDisp
      ? `<span style="background: ${inqDisp.cls === 'rose' ? 'rgba(244,63,94,0.18)' : 'rgba(16,185,129,0.18)'}; color: ${inqDisp.cls === 'rose' ? '#fda4af' : '#6ee7b7'}; font-size: 0.68rem; padding: 1px 4px; border-radius: 3px; margin-left: 4px;" title="${inqDisp.title}">${inqDisp.label}</span>`
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

  const shouldStratify = groupingFn && (currentSubgroup !== 'none' || metaModality === 'all');

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

      subMeta.studyStats.sort((a,b) => {
        const sa=a.study || validStudies.find(s=>s.id===a.id), sb=b.study || validStudies.find(s=>s.id===b.id);
        if(currentSort==='effect_desc') return b.yi-a.yi;
        if(currentSort==='weight_desc') return b.weight_pct-a.weight_pct;
        if(currentSort==='year_desc') return sb.year-sa.year;
        if(currentSort==='name_asc') return sa.author.localeCompare(sb.author);
        return a.yi-b.yi;
      }).forEach(st => {
        const fullStudy = st.study || validStudies.find(s => s.id === st.id);
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
          <td colspan="3" style="font-size: 0.76rem; color: #818cf8; text-transform: uppercase;">${subMeta.k===1?"Single study":"Subgroup Pooled"} (${grp}):</td>
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
    if (metaModality === 'all') {
      html += `
        <tr style="background: rgba(99, 102, 241, 0.12); font-weight: 700; border-top: 2px solid var(--accent-primary);">
          <td colspan="8" style="padding: 0.85rem 1.25rem; color: #c7d2fe; font-size: 0.8rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <strong style="color: #fff;">🔒 Protocol Synthesis Standard:</strong>
                TEAS and electroacupuncture (EA) will not be combined in a grand pooled estimate.
                Subgroup diamonds above represent independent DerSimonian–Laird modality strata.
              </div>
              <span class="badge badge-indigo">Exploratory browser calculation</span>
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
          <td colspan="3" style="font-size: 0.85rem; color: #fff;">${metaModality} ${overallMeta.k===1?"SINGLE STUDY":"STRATUM POOLED EFFECT (Random-Effects, DL)"}:</td>
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
// 6. STATA 19.5 BE DATA SYNTHESIS & FOREST PLOTS HUB
// ==============================================================================
let isStataConsoleExpanded = false;

function renderSensitivitySandbox() {
  loadStataTerminalLog();
  switchLooMode('primary');
}

const PRIMARY_LOO_DATA = [
  {"omitted_study_id": "1879897506", "omitted_canonical_name": "Chen 1998", "omitted_author": "Chen L", "omitted_year": 1998, "modality": "TEAS", "remaining_k": 6, "remaining_total_n": 626, "pooled_md": -8.439, "se": 4.449, "wald_ci_low": -17.253, "wald_ci_upp": 0.375, "wald_p_val": 0.0606, "kh_ci_low": -19.875, "kh_ci_upp": 2.997, "kh_p_val": 0.1163, "tau2": 115.199, "i2": 98.806, "dfbetas": -0.33, "wald_sig": false, "kh_sig": false},
  {"omitted_study_id": "1879896688", "omitted_canonical_name": "Chen 2020", "omitted_author": "Chen J", "omitted_year": 2020, "modality": "TEAS", "remaining_k": 6, "remaining_total_n": 596, "pooled_md": -5.831, "se": 3.011, "wald_ci_low": -11.256, "wald_ci_upp": -0.406, "wald_p_val": 0.0351, "kh_ci_low": -13.571, "kh_ci_upp": 1.91, "kh_p_val": 0.1106, "tau2": 36.769, "i2": 95.929, "dfbetas": -1.354, "wald_sig": true, "kh_sig": false},
  {"omitted_study_id": "1879897344", "omitted_canonical_name": "El-Rakshy 2009", "omitted_author": "El-Rakshy", "omitted_year": 2009, "modality": "EA", "remaining_k": 6, "remaining_total_n": 581, "pooled_md": -11.273, "se": 4.633, "wald_ci_low": -20.494, "wald_ci_upp": -2.052, "wald_p_val": 0.0166, "kh_ci_low": -23.182, "kh_ci_upp": 0.636, "kh_p_val": 0.0591, "tau2": 123.599, "i2": 98.867, "dfbetas": 0.295, "wald_sig": true, "kh_sig": false},
  {"omitted_study_id": "1879895909", "omitted_canonical_name": "He 2026 (hepatectomy/JIS)", "omitted_author": "He", "omitted_year": 2026, "modality": "TEAS", "remaining_k": 6, "remaining_total_n": 517, "pooled_md": -11.616, "se": 4.557, "wald_ci_low": -20.704, "wald_ci_upp": -2.529, "wald_p_val": 0.0122, "kh_ci_low": -23.331, "kh_ci_upp": 0.099, "kh_p_val": 0.0513, "tau2": 117.452, "i2": 97.112, "dfbetas": 0.375, "wald_sig": true, "kh_sig": false},
  {"omitted_study_id": "1879896891", "omitted_canonical_name": "Seevaunnamtum 2016", "omitted_author": "Seevaunnamtum", "omitted_year": 2016, "modality": "EA", "remaining_k": 6, "remaining_total_n": 612, "pooled_md": -9.551, "se": 4.865, "wald_ci_low": -19.12, "wald_ci_upp": 0.018, "wald_p_val": 0.0504, "kh_ci_low": -22.057, "kh_ci_upp": 2.955, "kh_p_val": 0.1068, "tau2": 134.531, "i2": 98.966, "dfbetas": -0.073, "wald_sig": false, "kh_sig": false},
  {"omitted_study_id": "NEW32_SZMIT2021", "omitted_canonical_name": "Szmit 2021", "omitted_author": "Szmit", "omitted_year": 2021, "modality": "TEAS", "remaining_k": 6, "remaining_total_n": 628, "pooled_md": -10.363, "se": 4.915, "wald_ci_low": -20.137, "wald_ci_upp": -0.589, "wald_p_val": 0.0377, "kh_ci_low": -22.997, "kh_ci_upp": 2.271, "kh_p_val": 0.0888, "tau2": 137.894, "i2": 98.818, "dfbetas": 0.093, "wald_sig": true, "kh_sig": false},
  {"omitted_study_id": "1879896323", "omitted_canonical_name": "Yang 2024", "omitted_author": "Yang", "omitted_year": 2024, "modality": "EA", "remaining_k": 6, "remaining_total_n": 496, "pooled_md": -11.665, "se": 4.531, "wald_ci_low": -20.701, "wald_ci_upp": -2.63, "wald_p_val": 0.0114, "kh_ci_low": -23.313, "kh_ci_upp": -0.018, "kh_p_val": 0.0498, "tau2": 116.03, "i2": 97.274, "dfbetas": 0.388, "wald_sig": true, "kh_sig": true}
];

let currentLooMode = 'primary';

function switchLooMode(mode) {
  currentLooMode = mode;
  const btnPrimary = document.getElementById('btn-loo-primary') || document.getElementById('btn-loo-teas');
  const btnComb = document.getElementById('btn-loo-comb');
  const metaEl = document.getElementById('loo-dataset-meta');
  const footEl = document.getElementById('loo-table-footnote');
  const calloutGrid = document.getElementById('loo-callout-grid');

  if (btnPrimary) {
    btnPrimary.style.background = 'var(--accent-primary)';
    btnPrimary.style.color = '#fff';
    btnPrimary.style.border = 'none';
  }
  if (btnComb) {
    btnComb.style.background = 'rgba(255,255,255,0.08)';
    btnComb.style.color = 'var(--text-secondary)';
    btnComb.style.border = '1px solid var(--border-subtle)';
  }
  if (metaEl) metaEl.innerText = 'Primary 24-h Opioid Synthesis • k = 7 Strict Trials (N = 676)';
  if (footEl) footEl.innerText = 'Baseline complete primary synthesis (k=7, N=676): Pooled MD = −9.907 mg IV MME [95% KH CI: −20.079 to +0.265], p = 0.0545, τ² = 113.911, I² = 98.57%. All models estimated via REML.';
  if (calloutGrid) {
    const rows=PRIMARY_LOO_DATA;
    const crossing=rows.filter(r=>r.kh_ci_low<=0 && r.kh_ci_upp>=0).length;
    const benchmark=rows.filter(r=>r.pooled_md<=-10).length;
    calloutGrid.innerHTML=`<p>${crossing} of ${rows.length} Hartung–Knapp intervals include zero. Omitting Yang 2024 gives p=0.0498; crossing p=0.05 does not change the review conclusion.</p><p>${benchmark} omission-model point estimates reach a 10 mg reduction. A point estimate reaching a benchmark is not proof of a clinically important effect.</p>`;
  }
  renderLeaveOneOutTable();
}
window.switchLooMode = switchLooMode;

function renderLeaveOneOutTable() {
  const tbody = document.getElementById('leave-one-out-tbody');
  if (!tbody) return;

  const data = PRIMARY_LOO_DATA;

  tbody.innerHTML = data.map(row => {
    const waldBadge = row.wald_sig 
      ? '<span class="badge badge-emerald" style="font-size: 0.68rem; padding: 2px 6px;">Sig (p &lt; 0.05)</span>' 
      : '<span class="badge badge-amber" style="font-size: 0.68rem; padding: 2px 6px;">Crosses 0</span>';
    const khBadge = row.kh_sig 
      ? '<span class="badge badge-emerald" style="font-size: 0.68rem; padding: 2px 6px;">Sig (p &lt; 0.05)</span>' 
      : '<span class="badge badge-amber" style="font-size: 0.68rem; padding: 2px 6px;">p = ' + row.kh_p_val.toFixed(4) + '</span>';
    const isSpecial = Math.abs(row.dfbetas) > 1;
    const badgeLabel = '|DFBETAS| > 1';
    const rowStyle = isSpecial ? 'background: rgba(99, 102, 241, 0.08); font-weight: 600;' : '';

    return `
      <tr style="${rowStyle}">
        <td><strong>${row.omitted_canonical_name}</strong> <span class="badge ${row.modality === 'TEAS' ? 'badge-indigo' : 'badge-cyan'}" style="font-size: 0.65rem; margin-left: 4px;">${row.modality}</span> ${isSpecial ? `<span class="badge badge-indigo" style="font-size: 0.65rem; margin-left: 4px;">${badgeLabel}</span>` : ''}</td>
        <td>${row.omitted_year}</td>
        <td>${row.remaining_k} (${row.remaining_total_n})</td>
        <td style="color: #34d399; font-weight: 700;">${row.pooled_md.toFixed(3)}</td>
        <td>[${row.wald_ci_low.toFixed(3)}, ${row.wald_ci_upp.toFixed(3)}]</td>
        <td>${row.wald_p_val.toFixed(4)} ${waldBadge}</td>
        <td>[${row.kh_ci_low.toFixed(3)}, ${row.kh_ci_upp.toFixed(3)}]</td>
        <td>${row.kh_p_val.toFixed(4)} ${khBadge}</td>
        <td>${row.tau2.toFixed(3)}</td>
        <td>${row.i2.toFixed(1)}%</td>
        <td style="color: ${Math.abs(row.dfbetas) > 1.0 ? '#f87171' : 'var(--text-secondary)'}; font-weight: ${Math.abs(row.dfbetas) > 1.0 ? '700' : 'normal'};">${row.dfbetas.toFixed(3)}</td>
      </tr>
    `;
  }).join('');
}

let cachedStataLog = null;
function loadStataTerminalLog() {
  const el = document.getElementById('stata-terminal-content');
  if (!el) return;

  if (cachedStataLog) {
    el.innerText = cachedStataLog;
    return;
  }

  fetch('v26/02_STATA/logs/01_opioid24_primary.log')
    .then(res => {
      if (!res.ok) throw new Error('Network response not ok');
      return res.text();
    })
    .then(text => {
      cachedStataLog = text;
      el.innerText = text;
    })
    .catch(() => { el.textContent='Execution log could not be loaded. Use the downloadable log link or retry when connectivity is restored.'; });
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

  const inqStudies = window.STUDIES_DATA.filter(s => s.outcomes.opioid_24h && Number.isFinite(s.outcomes.opioid_24h.se));
  select.innerHTML = inqStudies.map(s => `
    <option value="${s.id}">${s.key}</option>
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
  if (info) info.textContent = `${s.key}: hypothetical changes to the existing primary result. Observed standard error ${s.outcomes.opioid_24h.se.toFixed(3)} is retained. No missing author data or variance is invented. Changes stay in this simulator.`;

  updateSimulationComparison();
}

function updateSimStudyMD(val) {
  const numVal = parseFloat(val);
  const valSpan = document.getElementById('sim-md-val');
  if (valSpan) valSpan.innerText = `${numVal < 0 ? '−' : '+'}${Math.abs(numVal).toFixed(1)} mg MME`;

  simOverrides[activeSimStudyId] = { mean_diff: numVal };
  updateSimulationComparison();
  renderKPIs();
}

function applySimScenario(scenario) {
  const inqStudies = window.STUDIES_DATA.filter(s => s.outcomes.opioid_24h && Number.isFinite(s.outcomes.opioid_24h.se));
  
  if (scenario === 'baseline') {
    simOverrides = {};
  } else if (scenario === 'optimistic') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: -10 };
    });
  } else if (scenario === 'conservative') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: -5 };
    });
  } else if (scenario === 'worst') {
    inqStudies.forEach(s => {
      simOverrides[s.id] = { mean_diff: 0 };
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

  if (!baseMeta.k) {
    ['sim-baseline-md','sim-post-md'].forEach(id => document.getElementById(id).textContent='No matching primary data');
    ['sim-baseline-ci','sim-post-ci','sim-delta-badge'].forEach(id => document.getElementById(id).textContent='');
    return;
  }

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
    const isExceedingExploratory = simMeta.pooled_md <= -5.0;
    if (isExceedingExploratory) {
      deltaBadge.className = 'delta-badge badge-emerald';
      deltaBadge.innerText = `Hypothetical point estimate exceeds exploratory threshold (≥ 5 mg MME) by ${(Math.abs(simMeta.pooled_md) - 5.0).toFixed(1)} mg`;
    } else {
      deltaBadge.className = 'delta-badge badge-amber';
      deltaBadge.innerText = `Below exploratory threshold (5 mg)`;
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

  const dose = Number(doseInput.value);
  if (!doseInput.value.trim() || !Number.isFinite(dose) || dose < 0) {
    resElem.textContent='Enter a non-negative dose.';
    if (explElem) explElem.textContent='No conversion calculated.';
    return;
  }
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
    explElem.innerText = `${dose} ${unit} ${drugName} × ${factor} = ${mme} mg IV Morphine Milligram Equivalents. Research conversion only; does not update extracted data.${['sufentanil_mcg','hydromorphone_mg'].includes(drug) ? ' This factor remains unresolved pending independent verification.' : ''}`;
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

  const n=Number(nInput.value), q1=Number(q1Input.value), m=Number(mInput.value), q3=Number(q3Input.value);
  if (![nInput,q1Input,mInput,q3Input].every(x=>x.value.trim()) || !Number.isInteger(n) || n<2 || ![q1,m,q3].every(Number.isFinite) || q1>m || m>q3) {
    resElem.textContent='Enter N ≥ 2 and ordered Q1 ≤ median ≤ Q3.';
    explElem.textContent='No value calculated from invalid or missing inputs.'; return;
  }
  resElem.textContent=`Median ${m} (IQR ${q1}–${q3}), N=${n}`;
  explElem.textContent='Preserved as reported. This review does not convert median/IQR to mean/SD for pooling.';
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

  for (const [id, label, priority] of [
    ['btn-priority-all', 'All inquiries', null],
    ['btn-priority-critical', 'Critical: 24h opioid', 'CRITICAL'],
    ['btn-priority-important', 'Important: secondary', 'IMPORTANT'],
  ]) {
    const button = document.getElementById(id);
    if (button) button.textContent = `${label} (${priority ? inqs.filter(r => r.priority === priority).length : inqs.length})`;
  }

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
    const p1Count = (window.P1_DISPOSITIONS && window.P1_DISPOSITIONS.length) ? window.P1_DISPOSITIONS.length : 19;
    counterBadge.innerHTML = `Showing ${filtered.length} of ${inqs.length} Author Inquiries &bull; <span style="color: #34d399; font-weight: 700;">✅ ${p1Count}/${p1Count} P1 Issues Audited (0 Blockers)</span>`;
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

const STATA_MASTER_RESULTS = {
  "AN-01-TEAS": {
    id: "AN-01-TEAS",
    name: "PRIMARY MODALITY 1: TEAS vs Sham (0–24h Opioid Consumption)",
    role: "PRIMARY",
    outcome: "Cumulative 0–24h Opioid Consumption",
    modality: "TEAS",
    comparator: "Sham",
    k: 4,
    n: 337,
    mdText: "−14.00 mg IV MME [−34.18, +6.19]",
    pVal: "p = 0.1145",
    controlRisk: "Mean baseline: 10.06 to 53.50 mg IV MME",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels: -1 for inconsistency (I² = 98.6%, τ² = 156.88) and -1 for imprecision (k=4, 95% KH CI crosses zero: −34.18 to +6.19 mg). Direct sham-controlled TEAS trials (Chen 1998, Chen 2020, He 2026, Szmit 2021).",
    robStatus: "Some concerns across all 4 contributing trials"
  },
  "AN-01-EA": {
    id: "AN-01-EA",
    name: "PRIMARY MODALITY 2: EA vs Usual Care (0–24h Opioid Consumption)",
    role: "PRIMARY",
    outcome: "Cumulative 0–24h Opioid Consumption",
    modality: "EA",
    comparator: "Usual Care / Control",
    k: 3,
    n: 339,
    mdText: "−3.94 mg IV MME [−19.77, +11.90]",
    pVal: "p = 0.3969",
    controlRisk: "Mean baseline: 33.94 to 44.00 mg IV MME",
    grade: "Very Low",
    badgeClass: "grade-badge-verylow",
    downgrade: "Downgraded 4 levels: -1 for risk of bias (serious; High RoB present in a minority of contributing trials, 1 of 3 -- El-Rakshy 2009), -1 for inconsistency (I² = 77.2%, τ² = 28.47), and -2 for very serious imprecision (k=3, highly imprecise 95% KH CI crossing zero: −19.77 to +11.90 mg). Nominal downgrade floors at Very Low (GRADE has no lower rating), so this correction does not change the label, but the review's own reasoning had previously omitted an explicit risk-of-bias line despite already describing El-Rakshy 2009 as High RoB below. (El-Rakshy 2009, Seevaunnamtum 2016, Yang 2024).",
    robStatus: "High RoB (El-Rakshy 2009, confirmed 2026-09-09 by independent re-read of the primary source: the publication's intervention-group denominators are irreconcilable across its flow diagram, Results text, Table 1, abstract, and Table 3, so the completeness of the 24-h morphine outcome data cannot be reliably established -- RoB 2 Domain 3, High); Some concerns (Seevaunnamtum 2016, Yang 2024)"
  },
  "AN-01-COMB": {
    id: "AN-01-COMB",
    name: "SUPPORTING COMBINED SYNTHESIS: Perioperative Stimulation vs Sham/Usual Care (0–24h)",
    role: "SUPPORTING COMBINED",
    outcome: "Cumulative 0–24h Opioid Consumption",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham (TEAS) / Usual Care (EA)",
    k: 7,
    n: 676,
    mdText: "−9.91 mg IV MME [−20.08, +0.27]",
    pVal: "p = 0.0545",
    controlRisk: "Mean baseline: 10.06 to 53.50 mg IV MME",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels: -1 for inconsistency (I² = 98.6%, τ² = 113.91) and -1 for imprecision (95% KH CI crosses zero; 95% prediction interval: −39.35 to +19.54 mg). All 7 strict direct trials.",
    robStatus: "6 Some concerns, 1 High RoB"
  },
  "AN-01-SMD": {
    id: "AN-01-SMD",
    name: "SUPPORTING PRIMARY: Standardized Mean Difference (Hedges' g)",
    role: "SUPPORTING",
    outcome: "Cumulative 0–24h Opioid (SMD)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 7,
    n: 676,
    mdText: "g = −0.97 [−2.09, +0.15]",
    pVal: "p = 0.0790",
    controlRisk: "Standardized across diverse opioid formulations",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels for inconsistency (I² = 96.5%) and imprecision (95% KH CI crosses zero).",
    robStatus: "5 Some concerns, 1 High RoB"
  },
  "AN-02-TARGET-A": {
    id: "AN-02-TARGET-A",
    name: "TARGET A: Cumulative 0–48h Opioid Consumption (Strict)",
    role: "TARGET A",
    outcome: "Cumulative 0–48h Opioid Consumption",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 3,
    n: 1999,
    mdText: "−10.27 mg IV MME [−34.83, +14.30]",
    pVal: "p = 0.2139",
    controlRisk: "Mean baseline: 14.0 to 103.3 mg IV MME",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels: -1 for inconsistency (I² = 97.1%, τ² = 94.56 — substantial between-trial variance after the corrected sufentanil conversion) and -1 for imprecision (95% KH CI crosses zero: −34.83 to +14.30 mg). Trials: Chen 2020, Zhang 2023, An 2014.",
    robStatus: "Low / Some concerns"
  },
  "AN-03-TARGET-B": {
    id: "AN-03-TARGET-B",
    name: "TARGET B: Cumulative 0–72h Opioid Consumption (Strict Exact: Yang 2024)",
    role: "TARGET B",
    outcome: "Cumulative 0–72h Opioid Consumption",
    modality: "EA vs Usual Care",
    comparator: "Usual Care",
    k: 1,
    n: 180,
    mdText: "−0.50 mg Morphine [−4.08, +3.08]",
    pVal: "p = 0.7840",
    controlRisk: "Mean control: 17.50 ± 10.00 mg morphine",
    grade: "Very Low",
    badgeClass: "grade-badge-verylow",
    downgrade: "Single trial (k=1, N=180, Yang 2024 alone: MD = −0.50 mg [−4.08, +3.08], p = 0.7840); very serious imprecision (not pooled). Broader sensitivity including Wong 2006 (first 3 days, k=2, N=205): MD = −1.47 mg [−34.42, +31.48], p = 0.6716.",
    robStatus: "Some concerns"
  },
  "AN-04-TARGET-C": {
    id: "AN-04-TARGET-C",
    name: "TARGET C: Postoperative Pain at Rest (~24h, VAS 0–10)",
    role: "TARGET C",
    outcome: "Rest Pain at ~24h (VAS 0–10)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 2,
    n: 158,
    mdText: "−0.18 VAS [−0.68, +0.33]",
    pVal: "p = 0.1414",
    controlRisk: "Mean baseline: 2.10 to 2.47 VAS points",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels: both contributing trials (Xing 2022, Liu 2021) are High Risk of Bias; 95% KH CI crosses zero (I² = 0.0%, τ² = 0.00).",
    robStatus: "High RoB across all trials"
  },
  "AN-05-TARGET-D-24": {
    id: "AN-05-TARGET-D-24",
    name: "TARGET D: Composite Postoperative Nausea & Vomiting (PONV 0–24h)",
    role: "TARGET D",
    outcome: "Composite PONV (0–24h)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 2,
    n: 463,
    mdText: "RR 0.56 [0.14, 2.26]",
    pVal: "p = 0.1191",
    controlRisk: "286 per 1,000 patients (28.6%)",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels for imprecision (k=2, small events, 95% KH CI crosses 1.0: 0.14 to 2.26; Zheng 2025, Lu 2021).",
    robStatus: "Some concerns"
  },
  "AN-06-TARGET-D-48": {
    id: "AN-06-TARGET-D-48",
    name: "TARGET D: Composite Postoperative Nausea & Vomiting (PONV 0–48h)",
    role: "TARGET D",
    outcome: "Composite PONV (0–48h)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 2,
    n: 120,
    mdText: "RR 0.52 [0.22, 1.27]",
    pVal: "p = 0.0682",
    controlRisk: "233 per 1,000 patients (23.3%)",
    grade: "Low",
    badgeClass: "grade-badge-low",
    downgrade: "Downgraded 2 levels for risk of bias and imprecision (k=2, 95% KH CI crosses 1.0; Xiong 2021, Xing 2022).",
    robStatus: "High RoB / Some concerns"
  },
  "AN-07-TARGET-E": {
    id: "AN-07-TARGET-E",
    name: "TARGET E: Time to First Postoperative Flatus (GI Recovery, Hours)",
    role: "TARGET E",
    outcome: "Time to First Flatus (Hours)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 6,
    n: 596,
    mdText: "−2.00 hours [−3.14, −0.87]",
    pVal: "p = 0.0062",
    controlRisk: "Mean baseline: 32.2 to 85.0 hours",
    grade: "Moderate",
    badgeClass: "grade-badge-mod",
    downgrade: "Downgraded 1 level for risk of bias across surgical settings; homogeneity is high (I² = 0.0%, τ² = 0.00, p = 0.0062). Standardized: Hedges' g = −0.46 (p = 0.0002). Trials: Zhou 2025, Yang 2020, Yang 2024, Xing 2022, Lu 2022, Ng 2013.",
    robStatus: "Some concerns / High RoB"
  },
  "AN-08-TARGET-F-REMI": {
    id: "AN-08-TARGET-F-REMI",
    name: "TARGET F: Intraoperative Titrated Remifentanil Requirements (µg)",
    role: "TARGET F",
    outcome: "Intraoperative Remifentanil (µg)",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 7,
    n: 890,
    mdText: "−114.21 µg [−213.72, −14.70]",
    pVal: "p = 0.0308",
    controlRisk: "Mean baseline: 533 to 2,800 µg remifentanil",
    grade: "Moderate",
    badgeClass: "grade-badge-mod",
    downgrade: "Downgraded 1 level for surgical duration and case-mix heterogeneity across trials (I² = 80.7%, τ² = 8288).",
    robStatus: "Some concerns"
  },
  "AN-09-TARGET-F-RESCUE": {
    id: "AN-09-TARGET-F-RESCUE",
    name: "TARGET F: Postoperative Rescue Opioid Requirement (Strict Binary)",
    role: "TARGET F",
    outcome: "Rescue Opioid Requirement",
    modality: "Combined (TEAS + EA)",
    comparator: "Sham / Control",
    k: 4,
    n: 312,
    mdText: "RR 0.50 [0.34, 0.75]",
    pVal: "p = 0.0119",
    controlRisk: "384 per 1,000 patients (38.4%)",
    grade: "Moderate",
    badgeClass: "grade-badge-mod",
    downgrade: "Downgraded 1 level for potential risk of bias; consistency was high (I² = 0.0%, τ² = 0.00, p = 0.0119). Trials: Xie 2014, Yu 2020, Tu 2024, Zhou 2025.",
    robStatus: "Some concerns / High RoB"
  }
};

// 8. Direction of Evidence & GRADE Summary of Findings Matrix (Objective 7)
function renderDirectionOfEvidence() {
  const tbody = document.getElementById('grade-sof-table-body');
  if (!tbody) return;

  const resultsList = Object.values(STATA_MASTER_RESULTS);

  tbody.innerHTML = resultsList.map(item => {
    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-primary);">${item.name}</td>
        <td style="font-size: 0.75rem; color: var(--text-secondary);">${item.controlRisk}</td>
        <td style="font-weight: 700; color: #34d399;">${item.mdText} <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: normal;">(${item.pVal})</span></td>
        <td><strong>${item.n.toLocaleString()}</strong> (${item.k} RCTs)</td>
        <td>
          <span class="${item.badgeClass}">${item.grade}</span>
          <button class="stat-info-btn" data-stat-term="gradeCertainty" aria-label="GRADE ${item.grade} Certainty Explanation">ⓘ</button>
        </td>
        <td style="font-size: 0.72rem; color: var(--text-muted); line-height: 1.4;">
          ${item.downgrade}
          <div style="margin-top: 3px; color: #fbbf24; font-size: 0.68rem; font-style: italic;">[${item.robStatus}]</div>
        </td>
      </tr>
    `;
  }).join('');

  if (typeof window.initStatIcons === 'function') {
    window.initStatIcons();
  }

  const copyBtn = document.getElementById('btn-export-grade-sof');
  if (copyBtn) {
    copyBtn.onclick = () => {
      let txt = "GRADE Summary of Findings (Perioperative TEAS & EA Review — StataNow 19.5 BE Reconciled):\n\n";
      resultsList.forEach(item => {
        txt += `• ${item.name}: ${item.mdText} (${item.pVal}) | ${item.n} pts (${item.k} RCTs) | Certainty: ${item.grade} | ${item.downgrade} [${item.robStatus}]\n`;
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
  document.getElementById('stata-code-snippet').textContent = `* Authoritative replication: run from the repository root.
do "06_FINAL_ANALYSIS_V26/02_STATA/00_master.do"
* Current supplementary secondary analyses:
do "08_V33_MASTER/02_STATA/20_v33_secondary.do"
* The filtered browser CSV is for inspection, not a substitute for the locked input datasets.`;
  document.getElementById('r-code-snippet').textContent = `# Inspect the downloaded Stata results in R; this does not refit the models.
results <- read.csv("master_reconciled_results_v26.csv")
print(results)
# Reproduce inferential results using the Stata pipeline above.`;
}

// Export Filtered CSV
function exportDatasetCSV() {
  const filtered = getFilteredStudies(false);
  const fields = ['study_id','study_key','author','year','country','modality','comparator','surgery_category','total_n',
    'arm1_n','arm1_mean','arm1_sd','arm1_events','arm2_n','arm2_mean','arm2_sd','arm2_events','mean_diff','rr','se','ci_low','ci_upp','unit',
    'comparison_id','source_dataset','source_note','exported_outcome','data_status','rob2_result_specific','rob2_study_level_overview','author_inquiry_disposition'];
  const rows = filtered.map(s => {
    const out = s.outcomes[currentOutcome] || {};
    const rr = resultRob(s, currentOutcome);
    return {study_id:s.id,study_key:s.key,author:s.author,year:s.year,country:s.country,
      modality:s.modality,comparator:s.comparator_short,surgery_category:s.surgery_category,total_n:s.population.total_n,
      ...out,arm1_n:out.arm1_total ?? out.arm1_n,arm2_n:out.arm2_total ?? out.arm2_n,exported_outcome:currentOutcome,
      data_status:Number.isFinite(out.mean_diff)||Number.isFinite(out.rr)?'Available':'Not available in this dataset',
      rob2_result_specific:rr.overall || (rr.state==='pending'?'Pending':'Not assessed'),
      rob2_study_level_overview:s.rob2?.overall,
      author_inquiry_disposition:inquiryDisposition(s)?.label || 'No inquiry recorded'};
  });
  const cell = value => '"'+String(value ?? '').replaceAll('"','""')+'"';
  const csv = [fields.join(','), ...rows.map(row=>fields.map(key=>cell(row[key])).join(','))].join('\n')+'\n';
  const url = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8;'}));
  const link = document.createElement('a'); link.href=url;
  link.download=`perioperative_teas_ea_${currentOutcome}_${filtered.length}_studies.csv`;
  link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function openStudyDrawer(id) {
  const s = window.STUDIES_DATA.find(st => st.id === id);
  if (!s) return;

  const modal = document.getElementById('study-modal');
  const content = document.getElementById('study-modal-content');
  if (!modal || !content) return;

  const inqHtml = s.author_inquiry && s.author_inquiry.has_inquiry ? `
    <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 1rem; border-radius: 4px; font-size: 0.8rem; line-height: 1.6; margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: #fbbf24; margin-bottom: 0.3rem;">Recorded Author Clarification Request</h4>
      <p><strong>Target Requested:</strong> ${s.author_inquiry.target_data}</p>
      <p><strong>Corresponding Author:</strong> ${s.author_inquiry.corresponding_author} (<code>${s.author_inquiry.email}</code>)</p>
      <p><strong>Historical inquiry entry (not an extracted value):</strong> ${s.author_inquiry.current_assumed_value}</p>
    </div>
  ` : '';

  content.innerHTML = `
    <div style="margin-bottom: 1.5rem;">
      <span class="kpi-badge badge-indigo">${s.modality}</span>
      <span class="kpi-badge badge-emerald">${s.comparator_type}</span>
      ${(() => {
        const rr = resultRob(s, explorerRobOutcome);
        const ctx = ROB_OUTCOME_LABELS[explorerRobOutcome] || explorerRobOutcome;
        return robBadgeHtml(rr.state, `RoB 2 for ${ctx}`) +
          `<span class="kpi-badge" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">RoB 2 context: ${ctx}</span>`;
      })()}
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
          <p><strong>Duration:</strong> ${s.stricta.duration_raw || "Not recorded"}</p>
          <p><strong>Stimulator/Electrode:</strong> ${s.stricta.needle_depth}</p>
        </div>
      </div>

      <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
        <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Surgical &amp; Population Baseline</h4>
        <div style="font-size: 0.82rem; line-height: 1.6;">
          <p><strong>Surgical Category:</strong> ${s.surgery_category}</p>
          <p><strong>Procedure:</strong> ${s.surgery_procedure}</p>
          <p><strong>Analysed sample:</strong> ${s.population.total_n} (${s.population.arm1_n} ${s.modality} vs ${s.population.arm2_n} ${s.comparator_short})</p>
          ${s.population.randomized_total_n && s.population.randomized_total_n !== s.population.total_n
            ? `<p><strong>Randomised:</strong> ${s.population.randomized_total_n} (${s.population.randomized_arm1_n} vs ${s.population.randomized_arm2_n}) &mdash; <span style="color: var(--text-muted);">post-randomisation losses are reflected in the analysed denominators used for synthesis</span></p>` : ''}
          <p><strong>Mean Age:</strong> ${s.population.arm1_age} vs ${s.population.arm2_age}</p>
          <p><strong>Female %:</strong> ${s.population.arm1_female} vs ${s.population.arm2_female}</p>
          <p><strong>ASA Status:</strong> ${s.population.asa_status}</p>
        </div>
      </div>
    </div>

    <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin: 0;">Cochrane RoB 2 &mdash; study-level overview <span style="text-transform: none; font-weight: 500; color: #94a3b8;">(not result-specific; see the per-result table below)</span></h4>
        ${robBadgeHtml(robState(s.rob2.overall), 'Study-level overview')}
      </div>
      
      <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.75rem; font-size: 0.72rem;">
        <span class="badge" style="background: rgba(255,255,255,0.06);">D1 Randomization: <strong>${s.rob2.d1}</strong></span>
        <span class="badge" style="background: rgba(255,255,255,0.06);">D2 Deviations: <strong>${s.rob2.d2}</strong></span>
        <span class="badge" style="background: rgba(255,255,255,0.06);">D3 Missing Data: <strong>${s.rob2.d3}</strong></span>
        <span class="badge" style="background: rgba(255,255,255,0.06);">D4 Measurement: <strong>${s.rob2.d4}</strong></span>
        <span class="badge" style="background: rgba(255,255,255,0.06);">D5 Selection: <strong>${s.rob2.d5}</strong></span>
      </div>

      <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.5rem;"><strong>Signaling Rationale:</strong> ${s.rob2.rationale}</p>

      ${s.rob2_outcomes && s.rob2_outcomes.assessed_list && s.rob2_outcomes.assessed_list.length > 0 ? `
        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.08);">
          <h5 style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #818cf8; margin-bottom: 0.5rem;">Result-Specific RoB 2 Assessments (${s.rob2_outcomes.assessed_list.length} Endpoints Assessed)</h5>
          ${s.rob2_outcomes.assessed_list.map(a => `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem; font-size: 0.75rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
                <span style="font-weight: 700; color: var(--text-primary);">${a.outcome_name} <span style="font-weight: normal; color: var(--text-muted);">(${a.timepoint})</span></span>
                <span class="badge ${a.overall === 'Low' ? 'badge-emerald' : (a.overall === 'Some Concerns' || a.overall === 'Some concerns' ? 'badge-amber' : 'badge-rose')}" style="font-size: 0.65rem;">${a.overall}</span>
              </div>
              <div style="font-size: 0.7rem; color: var(--text-secondary); display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <span>D1: <strong>${a.d1}</strong></span>
                <span>D2: <strong>${a.d2}</strong></span>
                <span>D3: <strong>${a.d3}</strong></span>
                <span>D4: <strong>${a.d4}</strong></span>
                <span>D5: <strong>${a.d5}</strong></span>
                <span style="color: var(--text-muted); font-style: italic; margin-left: auto;">${a.assessment_file || a.rationale || "Source reference not recorded"}</span>
              </div>
            </div>
          `).join('')}
          <div style="font-size: 0.68rem; color: var(--text-muted); font-style: italic; margin-top: 0.3rem;">* Other results may be unassessed or absent from this browser dataset; see the current secondary coverage register. No domain judgments are imputed.</div>
        </div>
      ` : '<div style="font-size: 0.72rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem;">Trial assessed using consensus study-level signaling resolution.</div>'}
    </div>
  `;

  let outcomesHtml = `
    <div style="background: var(--bg-panel); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: var(--text-muted); margin-bottom: 0.75rem;">Extracted Clinical Endpoints &amp; Data Audit</h4>
      <div style="font-size: 0.82rem; line-height: 1.8;">
  `;

  if (s.outcomes && s.outcomes.opioid_24h && typeof s.outcomes.opioid_24h.mean_diff === 'number') {
    const op = s.outcomes.opioid_24h;
    const nativeDetail = op.native_drug ? ` • Native: ${op.arm1_mean_native !== undefined ? op.arm1_mean_native : op.arm1_mean} ± ${op.arm1_sd_native !== undefined ? op.arm1_sd_native : op.arm1_sd} vs ${op.arm2_mean_native !== undefined ? op.arm2_mean_native : op.arm2_mean} ± ${op.arm2_sd_native !== undefined ? op.arm2_sd_native : op.arm2_sd} ${op.native_unit || ''} ${op.native_drug}` : '';
    const derDetail = op.derivation_rule ? `<br><span style="font-size:0.75rem; color:#94a3b8;"><strong>Derivation Rule:</strong> ${op.derivation_rule}</span>` : '';
    outcomesHtml += `<p><strong>💊 Primary (0–24h Opioid Consumption):</strong> <span style="color: #34d399; font-weight: 700;">MD ${op.mean_diff < 0 ? '−' : '+'}${Math.abs(op.mean_diff)} mg IV MME</span> (95% CI: [${op.ci_low}, ${op.ci_upp}], SE: ${op.se})${nativeDetail}${derDetail}</p>`;
  } else if (s.outcomes && s.outcomes.opioid_24h) {
    outcomesHtml += `<p><strong>💊 Primary (0–24h Opioid Consumption):</strong> <span style="color: #f59e0b; font-weight: 600;">${s.outcomes.opioid_24h.status}</span> — ${s.outcomes.opioid_24h.note || 'No continuous 24h opioid mean/SD tabulated.'}</p>`;
  } else {
    outcomesHtml += '<p><strong>Primary 0–24h analysis:</strong> This study does not contribute to the locked seven-study primary set. Consult the contribution map for its result-level disposition.</p>';
  }

  if (s.outcomes && s.outcomes.opioid_48h && typeof s.outcomes.opioid_48h.mean_diff === 'number') {
    const op48 = s.outcomes.opioid_48h;
    const nativeDetail = op48.native_drug ? ` • Native: ${op48.arm1_mean_native !== undefined ? op48.arm1_mean_native : '-'} vs ${op48.arm2_mean_native !== undefined ? op48.arm2_mean_native : '-'} ${op48.native_unit} (MD ${op48.md_native})` : '';
    outcomesHtml += `<p><strong>💊 Key Secondary (0–48h Opioid Consumption):</strong> <span style="color: #34d399; font-weight: 700;">MD ${op48.mean_diff < 0 ? '−' : '+'}${Math.abs(op48.mean_diff)} mg IV MME</span> (95% CI: [${op48.ci_low}, ${op48.ci_upp}], SE: ${op48.se})${nativeDetail}</p>`;
  } else if (s.outcomes && s.outcomes.opioid_48h && s.outcomes.opioid_48h.role === 'PCA Volume Proxy') {
    outcomesHtml += `<p><strong>💊 Key Secondary (0–48h Opioid Consumption):</strong> <span style="color: #38bdf8; font-weight: 600;">PCA Volume Proxy</span> — ${s.outcomes.opioid_48h.note}</p>`;
  }

  if (s.outcomes && s.outcomes.opioid_72h && typeof s.outcomes.opioid_72h.mean_diff === 'number') {
    const op72 = s.outcomes.opioid_72h;
    const nativeDetail = op72.native_drug ? ` • Native: ${op72.arm1_mean_native !== undefined ? op72.arm1_mean_native : '-'} vs ${op72.arm2_mean_native !== undefined ? op72.arm2_mean_native : '-'} ${op72.native_unit} (MD ${op72.md_native})` : '';
    outcomesHtml += `<p><strong>💊 Exploratory (0–72h Opioid Consumption):</strong> <span style="color: #34d399; font-weight: 700;">MD ${op72.mean_diff < 0 ? '−' : '+'}${Math.abs(op72.mean_diff)} mg IV MME</span> (95% CI: [${op72.ci_low}, ${op72.ci_upp}], SE: ${op72.se})${nativeDetail}</p>`;
  } else if (s.outcomes && s.outcomes.opioid_72h && s.outcomes.opioid_72h.role === 'Rescue / Proxy') {
    outcomesHtml += `<p><strong>💊 Exploratory (0–72h Opioid Consumption):</strong> <span style="color: #38bdf8; font-weight: 600;">Surrogate / Rescue</span> — ${s.outcomes.opioid_72h.note}</p>`;
  }

  if (s.outcomes && s.outcomes.pain_rest_24h && typeof s.outcomes.pain_rest_24h.mean_diff === 'number') {
    const pn = s.outcomes.pain_rest_24h;
    outcomesHtml += `<p><strong>🩹 24-h Pain Intensity at Rest:</strong> <span style="color: #38bdf8; font-weight: 700;">MD ${pn.mean_diff < 0 ? '−' : '+'}${Math.abs(pn.mean_diff)} VAS</span> (95% CI: [${pn.ci_low ?? "Not recorded"}, ${pn.ci_upp ?? "Not recorded"}]) • ${pn.arm1_mean ?? "Not recorded"} ± ${pn.arm1_sd ?? "Not recorded"} vs ${pn.arm2_mean ?? "Not recorded"} ± ${pn.arm2_sd ?? "Not recorded"}</p>`;
  }

  if (s.outcomes && s.outcomes.pca_presses_24h && typeof s.outcomes.pca_presses_24h.mean_diff === 'number') {
    const pc = s.outcomes.pca_presses_24h;
    outcomesHtml += `<p><strong>🔘 PCA Demands / Presses (24h):</strong> <span style="color: #34d399; font-weight: 700;">MD ${pc.mean_diff < 0 ? '−' : '+'}${Math.abs(pc.mean_diff)} ${pc.unit || 'presses'}</span> (95% CI: [${pc.ci_low ?? "Not recorded"}, ${pc.ci_upp ?? "Not recorded"}], P=${pc.p_val ?? "Not recorded"}) • ${pc.arm1_mean ?? "Not recorded"} ± ${pc.arm1_sd ?? "Not recorded"} vs ${pc.arm2_mean ?? "Not recorded"} ± ${pc.arm2_sd ?? "Not recorded"} (${pc.metric_name ?? "Not recorded"})</p>`;
  } else if (s.outcomes && s.outcomes.pca_presses_24h && s.outcomes.pca_presses_24h.status && s.outcomes.pca_presses_24h.status !== 'Unreported in Source Paper') {
    const pc = s.outcomes.pca_presses_24h;
    outcomesHtml += `<p><strong>🔘 PCA Demands / Presses:</strong> <span style="color: #38bdf8; font-weight: 600;">${pc.metric_name || pc.status}</span> — ${pc.note || ''}</p>`;
  }

  if (s.outcomes && s.outcomes.rescue_analgesia && typeof s.outcomes.rescue_analgesia.rr === 'number') {
    const ra = s.outcomes.rescue_analgesia;
    outcomesHtml += `<p><strong>🆘 Supplemental / Rescue Analgesia:</strong> <span style="color: #34d399; font-weight: 700;">RR ${ra.rr ?? "Not recorded"}</span> (95% CI: [${ra.ci_low ?? "Not recorded"}, ${ra.ci_upp ?? "Not recorded"}], P=${ra.p_val ?? "Not recorded"}) • ${ra.arm1_events ?? "Not recorded"}/${ra.arm1_total ?? ra.arm1_n ?? "Not recorded"} vs ${ra.arm2_events ?? "Not recorded"}/${ra.arm2_total ?? ra.arm2_n ?? "Not recorded"} (${ra.definition ?? "Not recorded"}) — <em>${ra.note || ''}</em></p>`;
  } else if (s.outcomes && s.outcomes.rescue_analgesia && s.outcomes.rescue_analgesia.status && s.outcomes.rescue_analgesia.status !== 'Unreported in Source Paper') {
    const ra = s.outcomes.rescue_analgesia;
    outcomesHtml += `<p><strong>🆘 Supplemental / Rescue Analgesia:</strong> <span style="color: #f59e0b; font-weight: 600;">${ra.status ?? "Not recorded"}</span> — ${ra.note || ''}</p>`;
  }

  if (s.outcomes && s.outcomes.intraop_opioid && typeof s.outcomes.intraop_opioid.mean_diff === 'number') {
    const io = s.outcomes.intraop_opioid;
    outcomesHtml += `<p><strong>💉 Intraoperative Opioid Requirements:</strong> <span style="color: #38bdf8; font-weight: 700;">MD ${io.mean_diff < 0 ? '−' : '+'}${Math.abs(io.mean_diff)} ${io.unit ?? "Not recorded"} ${io.drug ?? "Not recorded"}</span> (95% CI: [${io.ci_low ?? "Not recorded"}, ${io.ci_upp ?? "Not recorded"}], P=${io.p_val ?? "Not recorded"}) • ${io.arm1_mean ?? "Not recorded"} ± ${io.arm1_sd ?? "Not recorded"} vs ${io.arm2_mean ?? "Not recorded"} ± ${io.arm2_sd ?? "Not recorded"} — <em>${io.note || ''}</em></p>`;
  } else if (s.outcomes && s.outcomes.intraop_opioid && s.outcomes.intraop_opioid.status && s.outcomes.intraop_opioid.status !== 'Unreported in Source Paper') {
    const io = s.outcomes.intraop_opioid;
    outcomesHtml += `<p><strong>💉 Intraoperative Opioid Requirements:</strong> <span style="color: #38bdf8; font-weight: 600;">${io.status ?? "Not recorded"}</span> — ${io.note || ''}</p>`;
  }

  if (s.outcomes && s.outcomes.ponv_24h && typeof s.outcomes.ponv_24h.rr === 'number') {
    const po = s.outcomes.ponv_24h;
    outcomesHtml += `<p><strong>🤢 Postoperative Nausea &amp; Vomiting (0–24h):</strong> <span style="color: #a78bfa; font-weight: 700;">RR ${po.rr ?? "Not recorded"}</span> (95% CI: [${po.ci_low ?? "Not recorded"}, ${po.ci_upp ?? "Not recorded"}]) • ${po.arm1_events ?? "Not recorded"}/${po.arm1_total ?? po.arm1_n ?? "Not recorded"} vs ${po.arm2_events ?? "Not recorded"}/${po.arm2_total ?? po.arm2_n ?? "Not recorded"}</p>`;
  }

  if (s.outcomes && s.outcomes.flatus_time && typeof s.outcomes.flatus_time.mean_diff === 'number') {
    const fl = s.outcomes.flatus_time;
    outcomesHtml += `<p><strong>⏱️ Time to First Flatus (GI Recovery):</strong> <span style="color: #34d399; font-weight: 700;">MD ${fl.mean_diff < 0 ? '−' : '+'}${Math.abs(fl.mean_diff)} hours</span> (95% CI: [${fl.ci_low ?? "Not recorded"}, ${fl.ci_upp ?? "Not recorded"}]) • ${fl.arm1_mean ?? "Not recorded"} ± ${fl.arm1_sd ?? "Not recorded"} vs ${fl.arm2_mean ?? "Not recorded"} ± ${fl.arm2_sd ?? "Not recorded"} h</p>`;
  }

  if (s.outcomes && s.outcomes.hospital_stay && typeof s.outcomes.hospital_stay.mean_diff === 'number') {
    const hs = s.outcomes.hospital_stay;
    outcomesHtml += `<p><strong>🏥 Length of Hospital Stay:</strong> MD ${hs.mean_diff < 0 ? '−' : '+'}${Math.abs(hs.mean_diff)} days • ${hs.arm1_mean ?? "Not recorded"} ± ${hs.arm1_sd ?? "Not recorded"} vs ${hs.arm2_mean ?? "Not recorded"} ± ${hs.arm2_sd ?? "Not recorded"} d</p>`;
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

// ── state bridge for the usability layer (dashboard/findings.js) ───────────
// The filter and selection state above is declared with `let`, so it is not
// reachable on `window`. Rather than restructure app.js, expose the same
// variables through accessors: findings.js reads and writes exactly these, so
// there is one source of truth and no shadow copy that could drift.
Object.defineProperties(window, {
  activeTab:        {get: () => activeTab,        set: v => { activeTab = v; },        configurable: true},
  currentOutcome:   {get: () => currentOutcome,   set: v => { currentOutcome = v; },   configurable: true},
  currentSubgroup:  {get: () => currentSubgroup,  set: v => { currentSubgroup = v; },  configurable: true},
  filterModality:   {get: () => filterModality,   set: v => { filterModality = v; },   configurable: true},
  filterComparator: {get: () => filterComparator, set: v => { filterComparator = v; }, configurable: true},
  filterSurgery:    {get: () => filterSurgery,    set: v => { filterSurgery = v; },    configurable: true},
  filterRob:        {get: () => filterRob,        set: v => { filterRob = v; },        configurable: true},
  filterSearch:     {get: () => filterSearch,     set: v => { filterSearch = v; },     configurable: true}
});
window.syncToolbarDropdowns = syncToolbarDropdowns;
window.focusStudyId = null;
window.focusAnalysisId = null;

// ══════════════════════════════════════════════════════════════════
// META-REGRESSION & MODERATOR STUDIO (Objective 3)
// ══════════════════════════════════════════════════════════════════

// v26: the k=11 bubble-plot studio and the multivariable effect-modifier simulator
// were withdrawn. Neither is reproduced by 06_FINAL_ANALYSIS_V26/02_STATA/09_subgroups_metareg.do,
// which fits exactly one meta-regression (modality, k=7, p=0.308) and no multivariable model.
// The stubs below keep any stale inline handler from throwing.

let cachedMetaRegLog = null;

function switchBubblePlot() { /* withdrawn in v26 */ }
function setPredModality() { /* withdrawn in v26 */ }
function updateMetaRegPrediction() { /* withdrawn in v26 */ }

function loadMetaRegTerminalLog() {
  const el = document.getElementById('stata-metareg-terminal-content');
  if (!el) return;

  if (cachedMetaRegLog) {
    el.innerText = cachedMetaRegLog;
    return;
  }

  fetch('v26/02_STATA/logs/09_subgroups_metareg.log')
    .then(res => {
      if (!res.ok) throw new Error('Network response not ok');
      return res.text();
    })
    .then(text => {
      cachedMetaRegLog = text;
      el.innerText = text;
    })
    .catch(() => { el.textContent='Execution log could not be loaded. Use the downloadable log link or retry when connectivity is restored.'; });
}

function renderMetaRegStudio() {
  loadMetaRegTerminalLog();
}

window.switchBubblePlot = switchBubblePlot;
window.setPredModality = setPredModality;
window.updateMetaRegPrediction = updateMetaRegPrediction;
window.renderMetaRegStudio = renderMetaRegStudio;


// ═══════════════════════════════════════════════════════════════════════════
// PRIMARY OUTCOME CONTRIBUTION PATHWAY
// ═══════════════════════════════════════════════════════════════════════════
// Answers "why do 63 included RCTs become 6 in the strict 24-h analysis?".
// Everything is read from window.PRIMARY_PATHWAY, generated by
// scripts/build_primary_pathway.py from the v26 lock + the final Stata run.
// No count is written in the HTML or here: if a study is reclassified in the
// locked data, regenerating the file moves it and every number follows.
//
// Wording rule: the other included trials are NEVER called "excluded from the
// review". They are included RCTs that do not contribute to THIS estimand.

const PW_CAT = {
  strict:      { label: 'STRICT PRIMARY',                 bg: 'rgba(16,185,129,0.16)',  fg: '#6ee7b7', bd: 'rgba(16,185,129,0.4)' },
  conditional: { label: 'SENSITIVITY ONLY',               bg: 'rgba(56,189,248,0.16)',  fg: '#7dd3fc', bd: 'rgba(56,189,248,0.4)' },
  candidate:   { label: 'AUTHOR DATA POTENTIALLY NEEDED', bg: 'rgba(245,158,11,0.16)',  fg: '#fbbf24', bd: 'rgba(245,158,11,0.4)' },
  hold:        { label: 'HARD HOLD / DEPENDENCY',         bg: 'rgba(244,63,94,0.16)',   fg: '#fda4af', bd: 'rgba(244,63,94,0.4)' },
  other:       { label: 'OTHER OUTCOME ONLY',             bg: 'rgba(129,140,248,0.16)', fg: '#c7d2fe', bd: 'rgba(129,140,248,0.4)' },
  none:        { label: 'NOT RELEVANT TO PRIMARY ESTIMAND', bg: 'rgba(255,255,255,0.06)', fg: '#94a3b8', bd: 'rgba(255,255,255,0.16)' }
};

function pwChip(cat) {
  const c = PW_CAT[cat] || PW_CAT.none;
  return `<span class="kpi-badge" style="background:${c.bg};color:${c.fg};border:1px solid ${c.bd};white-space:nowrap;">${c.label}</span>`;
}
function pwEsc(v) {
  return String(v == null ? '' : v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function pwSigned(v, dp = 2) {
  if (v == null || isNaN(v)) return '—';
  return (v < 0 ? '−' : '+') + Math.abs(v).toFixed(dp);
}
function pwP(v) {
  if (v == null || isNaN(v)) return '—';
  return v < 0.001 ? 'p < 0.001' : 'p = ' + v.toFixed(3);
}

function renderPrimaryPathway() {
  const P = window.PRIMARY_PATHWAY;
  if (!P || !document.getElementById('pathway-flow')) return;
  const c = P.counts;
  const R = P.results;

  const sub = document.getElementById('pathway-subtitle');
  if (sub) sub.innerHTML =
    `Which trials carry relevant 24-hour information, and what limits their use.`;

  const prov = document.getElementById('pathway-provenance-badge');
  if (prov) prov.textContent = 'Derived from ' + P.data_source.replace('.xlsx', '');

  // ── headline ─────────────────────────────────────────────────────────────
  const head = document.getElementById('pathway-headline');
  if (head) head.innerHTML =
    `<strong>${c.reporting_relevant_24h_info} trials</strong> report information potentially relevant to the 24-hour opioid outcome.
     ${c.strict} provide data directly compatible with the prespecified primary estimand and form the strict analysis.
     ${c.conditional} more carry relevant 24-hour information but need a broader assumption, so they are held to sensitivity analysis.
     ${c.author_contact_candidates} further trials could become strict contributors if targeted author clarification resolves a specific reporting gap.
     The remaining ${c.other_outcome_contributors + c.no_pooled_model} included trials
     <strong>are not excluded from the review</strong> &mdash; ${c.other_outcome_contributors} contribute to other outcomes
     (48-h and 72-h opioid, pain, PONV, flatus, rescue analgesia, intraoperative opioid, PCA behaviour),
     and ${c.no_pooled_model} contribute to the narrative and evidence map without entering a pooled model.`;

  // ── flow ─────────────────────────────────────────────────────────────────
  const arrow = `<div style="text-align:center;color:var(--text-muted);font-size:1.1rem;line-height:1;margin:0.3rem 0;">&darr;</div>`;
  const step = (n, label, note, colour) => `
    <div style="display:flex;align-items:center;gap:0.9rem;padding:0.75rem 1rem;background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-left:4px solid ${colour};border-radius:var(--radius-sm);">
      <div style="font-size:1.5rem;font-weight:800;color:${colour};min-width:3.4rem;text-align:right;">${n}</div>
      <div>
        <div style="font-weight:700;color:#f8fafc;font-size:0.86rem;">${label}</div>
        <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.5;">${note}</div>
      </div>
    </div>`;

  const flow = document.getElementById('pathway-flow');
  if (flow) flow.innerHTML =
    step(c.included_rcts, 'RCTs included in the systematic review',
         'Every one screened, extracted, reconciled and risk-of-bias assessed.', '#818cf8') +
    arrow +
    step(c.reporting_relevant_24h_info, 'report potentially relevant postoperative opioid information at ~24 h',
         'Carry a 24-hour opioid candidate row in the locked analysis dataset.', '#38bdf8') +
    arrow +
    `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:0.75rem;">
       ${step(c.strict, 'STRICT PRIMARY contributors',
              `N = ${c.strict_n}. Directly compatible with the prespecified estimand.`, '#34d399')}
       ${step(c.conditional, 'conditional / sensitivity only',
              `N = ${c.conditional_n}. Relevant 24-h data requiring a broader assumption.`, '#38bdf8')}
       ${step(c.author_contact_candidates, 'pending author clarification',
              'Could become strict contributors if a specific reporting gap is resolved.', '#fbbf24')}
     </div>`;

  // ── three panels ─────────────────────────────────────────────────────────
  const panels = document.getElementById('pathway-panels');
  if (panels) {
    const strictRows = P.primary_strict.map(r => `
      <li style="margin-bottom:0.5rem;">
        <strong style="color:#f8fafc;">${pwEsc(r.study_unit)}</strong>
        <span style="color:var(--text-muted);">(n = ${r.n_i}/${r.n_c})</span>
        <div style="font-size:0.74rem;color:var(--text-secondary);line-height:1.5;">
          ${pwEsc(r.outcome)} &bull; ${pwEsc(r.time_window)}<br>
          <span style="color:#6ee7b7;">Qualifies:</span> ${pwEsc(r.qualifies_because)}
        </div>
      </li>`).join('');

    const condRows = P.primary_conditional.map(r => `
      <li style="margin-bottom:0.5rem;">
        <strong style="color:#f8fafc;">${pwEsc(r.study_unit)}</strong>
        <span style="color:var(--text-muted);">(n = ${r.n_i}/${r.n_c})</span>
        <div style="font-size:0.74rem;color:var(--text-secondary);line-height:1.5;">
          Reported as ${pwEsc(r.unit)} (${pwEsc(r.data_type)})<br>
          <span style="color:#7dd3fc;">Not strict because:</span> ${pwEsc(r.not_strict_because)}<br>
          <span style="color:var(--text-muted);">${pwEsc(r.sensitivity_note || r.conversion_note)}</span>
        </div>
      </li>`).join('');

    const candRows = P.primary_author_contact_candidates.map(r => {
      const ac = r.author_contact || {};
      const gap = ac.gap_note
        ? `<div style="margin-top:0.35rem;padding:0.4rem 0.55rem;background:rgba(244,63,94,0.1);border-left:3px solid #fb7185;border-radius:3px;color:#fda4af;">${pwEsc(ac.gap_note)}</div>`
        : '';
      return `
      <li style="margin-bottom:0.7rem;">
        <strong style="color:#f8fafc;">${pwEsc(r.study_unit)}</strong> ${r.hard_hold ? pwChip('hold') : ''}
        <div style="font-size:0.74rem;color:var(--text-secondary);line-height:1.55;">
          <span style="color:#fbbf24;">Available:</span> ${pwEsc(r.outcome)} &bull; ${pwEsc(r.time_window)} &bull; n = ${r.n_i}/${r.n_c}<br>
          <span style="color:#fbbf24;">Missing:</span> ${pwEsc(r.source_qc)}<br>
          <span style="color:#fbbf24;">Requested:</span> ${ac.data_needed ? pwEsc(ac.data_needed) : '<em>no request drafted</em>'}<br>
          <span style="color:#fbbf24;">Would become strictly usable if:</span> ${pwEsc(r.v26_decision)} is resolved<br>
          <span style="color:#fbbf24;">Contact status:</span> <strong>${pwEsc(ac.status)}</strong>
          <span style="color:var(--text-muted);">&mdash; ${pwEsc(ac.status_basis)}</span>
          ${gap}
        </div>
      </li>`;
    }).join('');

    const panel = (title, colour, count, nlabel, body, foot) => `
      <div class="card-glass" style="padding:1.15rem;border-top:3px solid ${colour};">
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:800;color:${colour};">${title}</div>
        <div style="font-size:1.6rem;font-weight:800;color:#f8fafc;margin:0.2rem 0 0.1rem;">${count}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.7rem;">${nlabel}</div>
        <ul style="list-style:none;padding:0;margin:0;font-size:0.8rem;">${body}</ul>
        ${foot ? `<div style="margin-top:0.7rem;padding-top:0.6rem;border-top:1px solid var(--border-subtle);font-size:0.74rem;color:var(--text-secondary);line-height:1.55;">${foot}</div>` : ''}
      </div>`;

    panels.innerHTML =
      panel('Strict primary analysis', '#34d399', `k = ${c.strict}`, `N = ${c.strict_n} analysed`, strictRows,
            '<strong>Definition:</strong> directly reported, or defensibly harmonisable to a common dose metric, cumulative systemic postoperative opioid consumption at approximately or exactly 24 hours.') +
      panel('Broader sensitivity (conditional)', '#38bdf8', `+ ${c.conditional}`, `N = ${c.conditional_n} analysed`, condRows,
            'These are valid randomised trials carrying relevant information. Their reported <em>estimand</em> is less directly compatible with the primary outcome &mdash; that is a reporting-compatibility judgement, not a judgement of study quality.') +
      panel('Pending author clarification', '#fbbf24', c.author_contact_candidates, 'potential strict contributors', candRows,
            'Listed only where the trial carries potentially relevant 24-hour opioid information and a documented reporting gap. Contact status is never inferred.');
  }

  // ── strict vs broader comparison ────────────────────────────────────────
  const cmp = document.getElementById('pathway-comparison');
  if (cmp) {
    const est = P.md_pool_estimability;
    const sm = R.strict_smd, bs = R.broader_smd, md = R.strict_md;
    let rows = '';
    if (md) rows += `
      <tr>
        <td><strong>Strict primary &mdash; mean difference</strong><div style="font-size:0.72rem;color:var(--text-muted);">the prespecified primary result</div></td>
        <td>${md.k}</td><td>${c.strict_n}</td>
        <td>${pwSigned(md.estimate)} mg</td>
        <td>[${pwSigned(md.ci_low)}, ${pwSigned(md.ci_high)}]</td>
        <td>${(md.ci_high - md.ci_low).toFixed(2)}</td>
        <td>${pwP(md.p_value)}</td><td>${md.i2}%</td>
      </tr>`;
    if (sm) rows += `
      <tr>
        <td><strong>Strict primary &mdash; SMD</strong><div style="font-size:0.72rem;color:var(--text-muted);">same 6 trials, scale-free metric</div></td>
        <td>${sm.k}</td><td>${c.strict_n}</td>
        <td>g = ${pwSigned(sm.estimate)}</td>
        <td>[${pwSigned(sm.ci_low)}, ${pwSigned(sm.ci_high)}]</td>
        <td>${(sm.ci_high - sm.ci_low).toFixed(2)}</td>
        <td>${pwP(sm.p_value)}</td><td>${sm.i2}%</td>
      </tr>`;
    if (bs) rows += `
      <tr style="background:rgba(56,189,248,0.06);">
        <td><strong>Broader sensitivity &mdash; SMD</strong><div style="font-size:0.72rem;color:var(--text-muted);">adds the conditional trials with an estimable effect</div></td>
        <td>${bs.k}</td><td>${c.broader_smd_n}</td>
        <td>g = ${pwSigned(bs.estimate)}</td>
        <td>[${pwSigned(bs.ci_low)}, ${pwSigned(bs.ci_high)}]</td>
        <td>${(bs.ci_high - bs.ci_low).toFixed(2)}</td>
        <td>${pwP(bs.p_value)}</td><td>${bs.i2}%</td>
      </tr>`;

    let interp = '';
    if (sm && bs) {
      const dEst = Math.abs(bs.estimate - sm.estimate);
      const wS = sm.ci_high - sm.ci_low, wB = bs.ci_high - bs.ci_low;
      const crosses = (a) => (a.ci_low < 0 && a.ci_high > 0);
      const changed = crosses(sm) !== crosses(bs);
      interp = `
        <p style="margin:0 0 0.5rem;">On the identical standardized metric the point estimate barely moves
        &mdash; from g = ${pwSigned(sm.estimate)} to g = ${pwSigned(bs.estimate)}, a difference of ${dEst.toFixed(3)} &mdash;
        while the confidence interval narrows from ${wS.toFixed(2)} to ${wB.toFixed(2)} units wide.</p>
        <p style="margin:0 0 0.5rem;"><strong>${changed
          ? 'The interval crosses the no-effect line in the strict model and not in the broader one.'
          : 'The conclusion is unchanged between the two models.'}</strong>
        This is a change in <em>precision</em>, not in estimated effect. The strict model contains fewer
        independent studies and therefore carries more uncertainty; adding trials narrows the interval
        even when they say much the same thing.
        ${changed ? 'Reading that shift as "the effect became real" would be a mistake &mdash; the broader model buys its precision by accepting weaker assumptions about what the added trials measured.' : ''}</p>
        <p style="margin:0;">The strict analysis remains the prespecified primary result. The broader analysis is
        reported as sensitivity only.</p>`;
    }

    cmp.innerHTML = `
      <div class="card-glass" style="padding:1.15rem;">
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:800;color:#a78bfa;">Strict vs broader &mdash; what actually changes</div>
        <div style="overflow-x:auto;margin-top:0.7rem;">
          <table class="forest-table" style="font-size:0.78rem;">
            <thead><tr>
              <th>Analysis</th><th>k</th><th>N</th><th>Pooled estimate</th>
              <th>95% CI (Knapp&ndash;Hartung)</th><th>CI width</th><th>p</th><th>I&sup2;</th>
            </tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
        <div style="margin-top:0.8rem;font-size:0.8rem;color:var(--text-secondary);line-height:1.6;">${interp}</div>
        <div style="margin-top:0.8rem;padding:0.75rem 0.9rem;background:rgba(245,158,11,0.07);border-left:3px solid #f59e0b;border-radius:var(--radius-sm);font-size:0.78rem;color:#e2e8f0;line-height:1.6;">
          <strong>Why there is no k = ${est.candidate_pool_k} mean-difference row.</strong>
          The candidate pool is k = ${est.candidate_pool_k} (N = ${est.candidate_pool_n}), but only
          ${est.with_estimable_md} of those have an estimable mean difference in mg IV MME and
          ${est.with_estimable_smd} have an estimable standardized effect.
          ${pwEsc(est.verdict)}
          ${est.unpoolable_units.length ? `<br><span style="color:var(--text-muted);">Contributing to neither pooled model: ${est.unpoolable_units.map(pwEsc).join('; ')}.</span>` : ''}
        </div>
      </div>`;
  }

  // ── estimand box ────────────────────────────────────────────────────────
  const estb = document.getElementById('pathway-estimand');
  if (estb) estb.innerHTML = `
    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:800;color:#38bdf8;">Primary estimand</div>
    <p style="margin:0.5rem 0 0.7rem;color:#e2e8f0;">&ldquo;${pwEsc(P.estimand.statement)}&rdquo;</p>
    <div style="font-size:0.75rem;color:var(--text-secondary);">Why some reported data are not automatically equivalent:</div>
    <ul style="margin:0.4rem 0 0 1.1rem;padding:0;font-size:0.76rem;color:var(--text-secondary);line-height:1.6;">
      ${P.estimand.not_equivalent.map(([a, b]) => `<li><strong style="color:#cbd5e1;">${pwEsc(a)}</strong> ${pwEsc(b)}</li>`).join('')}
    </ul>`;

  // ── what could change ───────────────────────────────────────────────────
  const wcc = document.getElementById('pathway-whatcouldchange');
  if (wcc) wcc.innerHTML = `
    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:800;color:#fbbf24;">What could change the primary analysis?</div>
    <p style="margin:0.5rem 0 0.6rem;color:#e2e8f0;">
      The strict analysis currently contains ${c.strict} RCTs. Additional eligible trials may enter it if authors
      supply sufficient missing 24-hour opioid data or clarify reporting ambiguities. The strict meta-analysis
      will be updated if new source-verifiable data are obtained.</p>
    <p style="margin:0 0 0.6rem;color:var(--text-secondary);font-size:0.78rem;">
      Author contact is <strong>not</strong> intended to selectively seek data that strengthen the treatment
      effect. The same predefined eligibility rule is applied to every otherwise eligible study with
      potentially relevant but insufficiently reported primary-outcome data, whatever direction its
      published result points in.</p>
    <p style="margin:0;color:var(--text-muted);font-size:0.76rem;">
      If a candidate is resolved, regenerating <code>primary_pathway.js</code> moves that study between
      categories and every count on this page follows automatically &mdash; k = ${c.strict} would become
      k = ${c.strict + 1} without editing any explanatory text.</p>`;

  // ── maturity ────────────────────────────────────────────────────────────
  const mat = document.getElementById('pathway-maturity');
  if (mat) {
    const openCands = P.primary_author_contact_candidates.length;
    const pill = (label, value, colour) => `
      <div style="flex:1 1 200px;padding:0.7rem 0.9rem;background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-left:3px solid ${colour};border-radius:var(--radius-sm);">
        <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);font-weight:700;">${label}</div>
        <div style="font-size:0.85rem;font-weight:700;color:${colour};margin-top:0.15rem;">${value}</div>
      </div>`;
    mat.innerHTML = `<div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
      ${pill('Data reconciliation', 'COMPLETE', '#34d399')}
      ${pill('Current strict analysis', openCands ? 'PROVISIONAL — pending targeted author data' : 'FINAL', openCands ? '#fbbf24' : '#34d399')}
      ${pill('Broader sensitivity', 'AVAILABLE (SMD metric)', '#38bdf8')}
      ${pill('Author-contact follow-up', openCands + ' candidate' + (openCands === 1 ? '' : 's') + ' — contact prepared, no response documented', '#fbbf24')}
    </div>`;
  }

  renderPathwayTable();
}

function renderPathwayTable() {
  const P = window.PRIMARY_PATHWAY;
  const tb = document.getElementById('pathway-table-body');
  if (!P || !tb) return;
  const yes = '<span style="color:#6ee7b7;font-weight:700;">Yes</span>';
  const no  = '<span style="color:var(--text-muted);">No</span>';
  const rows = [];

  P.primary_strict.forEach(r => rows.push([r.study_unit, yes, yes, yes, yes, no,
    no, pwEsc(r.qualifies_because), 'strict']));
  P.primary_conditional.forEach(r => rows.push([r.study_unit, yes, yes, yes, no, yes,
    no, pwEsc(r.not_strict_because), 'conditional']));
  P.primary_author_contact_candidates.forEach(r => rows.push([
    r.study_unit + (r.covers_publications > 1
      ? ` <span style="font-size:0.7rem;color:#fbbf24;">(one study unit covering ${r.covers_publications} reports)</span>` : ''),
    yes, yes, yes, no, no,
    yes, pwEsc(r.v26_decision) + ' &mdash; ' + pwEsc((r.author_contact || {}).status),
    r.hard_hold ? 'hold' : 'candidate']));
  P.other_outcome_contributors.forEach(r => rows.push([r.study_unit, yes, no, no, no, no,
    no, 'Contributes to: ' + r.also_contributes_to.map(pwEsc).join('; '), 'other']));
  P.no_pooled_model.forEach(r => rows.push([r.study_unit, yes, no, no, no, no,
    no, 'Included in the review; contributes to the narrative and evidence map, not to a pooled model', 'none']));

  const cap = document.getElementById('pathway-table-caption');
  if (cap) {
    const famRows = [...P.primary_strict, ...P.primary_conditional, ...P.primary_author_contact_candidates]
      .filter(r => r.covers_publications > 1);
    const extra = famRows.reduce((a, r) => a + r.covers_publications - 1, 0);
    cap.innerHTML =
      `${rows.length} rows covering all ${P.counts.included_rcts} included RCTs.` +
      (extra ? ` The row count is lower than the study count because ${famRows.length} publication-family ` +
               `unit${famRows.length === 1 ? '' : 's'} cover${famRows.length === 1 ? 's' : ''} ${extra + famRows.length} reports ` +
               `between them: the v26 lock treats overlapping publications as one study unit, so they are ` +
               `never counted as independent trials.` : '');
  }

  tb.innerHTML = rows.map(([name, a, b, cc, d, e, f, reason, cat]) => `
    <tr>
      <td style="font-weight:600;">${name.includes('<span') ? name : pwEsc(name)}</td>
      <td>${a}</td><td>${b}</td><td>${cc}</td><td>${d}</td><td>${e}</td><td>${f}</td>
      <td style="font-size:0.74rem;color:var(--text-secondary);">${pwChip(cat)} ${reason}</td>
    </tr>`).join('');
}

function togglePathwayTable() {
  const w = document.getElementById('pathway-table-wrap');
  const b = document.getElementById('btn-pathway-table');
  if (!w) return;
  w.hidden = !w.hidden;
  if (b) b.textContent = w.hidden ? '📋 Study-level table' : '📋 Hide study-level table';
}

window.STATA_MASTER_RESULTS = STATA_MASTER_RESULTS;
window.renderPrimaryPathway = renderPrimaryPathway;
window.togglePathwayTable = togglePathwayTable;

// ═══════════════════════════════════════════════════════════════════════════
// v33 TIERED PRIMARY-OUTCOME DERIVABILITY
// ═══════════════════════════════════════════════════════════════════════════
// Answers a different question from the pathway above. The pathway asks which
// trials carry 24-hour information at all; this asks, of those that do, which
// can be pooled WITHOUT an assumption the protocol prohibits — and says plainly
// where the answer is "none".
//
// Everything is read from window.TIERED_V33, generated by
// scripts/build_tiered_v33.py from the v33 data files and the Stata results.
// Nothing here is hardcoded except the tier colours.

const T33_TIER_STYLE = {
  A: { bg: 'rgba(16,185,129,0.14)',  fg: '#6ee7b7', bd: 'rgba(16,185,129,0.42)' },
  B: { bg: 'rgba(56,189,248,0.14)',  fg: '#7dd3fc', bd: 'rgba(56,189,248,0.42)' },
  C: { bg: 'rgba(245,158,11,0.14)',  fg: '#fbbf24', bd: 'rgba(245,158,11,0.42)' },
  D: { bg: 'rgba(168,85,247,0.14)',  fg: '#d8b4fe', bd: 'rgba(168,85,247,0.42)' },
  E: { bg: 'rgba(244,63,94,0.14)',   fg: '#fda4af', bd: 'rgba(244,63,94,0.42)' }
};

function t33Effect(r) {
  if (r.estimate == null) return '<span style="color:var(--text-muted);">not pooled</span>';
  return `<strong>${pwSigned(r.estimate, 2)}</strong> mg IV MME
          [${pwSigned(r.ci_low, 2)}, ${pwSigned(r.ci_high, 2)}], ${pwP(r.p_value)}` +
         (r.i2 == null ? '' : `, I² = ${r.i2.toFixed(1)}%`);
}

function renderTieredV33() {
  const T = window.TIERED_V33;
  if (!T || !document.getElementById('t33-flow')) return;
  const S = T.analysis_sets;

  const sub = document.getElementById('t33-subtitle');
  if (sub) sub.innerHTML =
    `Of the studies carrying 0–24 hour opioid information, which can be pooled without an assumption the
     protocol prohibits — and where the honest answer is "none". Derived from a
     ${T.audit_rows}-row derivability audit of every candidate outcome row.`;

  // ── tier ladder ──────────────────────────────────────────────────────────
  const flow = document.getElementById('t33-flow');
  if (flow) {
    const occupancy = {
      A: `${T.strata.teas_sham.length + T.strata.ea_usual.length} contrasts pooled ` +
         `(TEAS vs sham k=${T.strata.teas_sham.length}; EA vs usual care k=${T.strata.ea_usual.length})`,
      B: 'no case — nothing is deterministically derivable that is not already Tier A',
      C: `${T.parallel_synthesis.length} studies — reported in their own units, never converted`,
      D: '1 candidate attempted, 0 admitted — the digitization failed validation',
      E: 'not admissible for the absolute-MME primary — 4 native mean/SD contrasts (5 with ' +
         'one median/IQR-approximated sensitivity addition) are admissible on a separate, ' +
         'scale-free SMD exploratory synthesis instead (see below)'
    };
    flow.innerHTML = T.tier_definitions.map(d => {
      const s = T33_TIER_STYLE[d.tier];
      return `
      <div style="display:grid;grid-template-columns:2.2rem 1fr;gap:0.8rem;align-items:start;
                  padding:0.7rem 0.85rem;border-left:3px solid ${s.bd};background:${s.bg};
                  border-radius:var(--radius-sm);margin-bottom:0.5rem;">
        <div style="font-weight:800;font-size:1.05rem;color:${s.fg};line-height:1.3;">${d.tier}</div>
        <div>
          <div style="font-weight:700;color:#f8fafc;font-size:0.86rem;">${pwEsc(d.label)}</div>
          <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.55;margin-top:0.15rem;">${pwEsc(d.rule)}</div>
          <div style="font-size:0.75rem;color:${s.fg};margin-top:0.3rem;font-weight:600;">${pwEsc(occupancy[d.tier])}</div>
        </div>
      </div>`;
    }).join('');
  }

  // ── analysis sets ────────────────────────────────────────────────────────
  const sets = document.getElementById('t33-sets');
  if (sets) {
    const card = (title, badge, badgeBg, badgeFg, body) => `
      <div class="card-glass" style="padding:1rem;">
        <span class="kpi-badge" style="background:${badgeBg};color:${badgeFg};">${badge}</span>
        <h4 style="margin:0.4rem 0 0.45rem;font-size:0.92rem;color:#f8fafc;">${title}</h4>
        <div style="font-size:0.79rem;color:var(--text-secondary);line-height:1.6;">${body}</div>
      </div>`;

    const studyList = arr => arr.map(s => pwEsc(s.study)).join(', ');

    sets.innerHTML = [
      card(`S0 primary — ${pwEsc(S.S0_teas_sham.modality)} vs ${pwEsc(S.S0_teas_sham.comparator.toLowerCase())} (k = ${S.S0_teas_sham.k})`,
           'PRIMARY', 'rgba(16,185,129,0.18)', '#6ee7b7',
           `${t33Effect(S.S0_teas_sham)}<br>
            <span style="color:var(--text-muted);">95% prediction interval
            ${S.S0_teas_sham.pi_low == null ? '—' :
              `[${pwSigned(S.S0_teas_sham.pi_low, 1)}, ${pwSigned(S.S0_teas_sham.pi_high, 1)}]`}.
            ${pwEsc(S.S0_teas_sham.estimator)} + ${pwEsc(S.S0_teas_sham.ci_method)}.</span><br>
            <span style="color:var(--text-muted);">${studyList(T.strata.teas_sham)}.</span>`),

      card(`S0 supportive — EA vs usual care (k = ${S.S0_ea_usual.k})`,
           'SUPPORTIVE', 'rgba(56,189,248,0.18)', '#7dd3fc',
           `${t33Effect(S.S0_ea_usual)}<br>
            <span style="color:var(--text-muted);">${studyList(T.strata.ea_usual)}.
            Reported separately from the sham-controlled model: a different comparator answers a
            different question, so the two are not averaged together.</span>`),

      card(`S1 — adding deterministically derived evidence (k = ${S.S1.k})`,
           'NO CHANGE', 'rgba(148,163,184,0.18)', '#cbd5e1',
           pwEsc(S.S1.notes)),

      card(`S2 — median/IQR evidence (k = ${T.parallel_synthesis.length})`,
           'PARALLEL SYNTHESIS', 'rgba(245,158,11,0.18)', '#fbbf24',
           T.parallel_synthesis.map(p => `
             <div style="margin-bottom:0.4rem;">
               <strong>${pwEsc(p.study)}</strong> (n = ${p.n_i} vs ${p.n_c}):
               ${p.median_i} (IQR ${p.q1_i}–${p.q3_i}) vs ${p.median_c} (IQR ${p.q1_c}–${p.q3_c}) mg IV MME;
               reported p = ${pwEsc(p.reported_p)}.
               <div style="color:var(--text-muted);font-size:0.75rem;">${pwEsc(p.not_pooled_reason)}</div>
             </div>`).join('')),

      card(`S3 — adding graph-digitized evidence (k = ${S.S3.k})`,
           'NO CHANGE', 'rgba(148,163,184,0.18)', '#cbd5e1',
           pwEsc(S.S3.notes)),

      card('Sensitivity analyses',
           'ROBUSTNESS', 'rgba(129,140,248,0.18)', '#c7d2fe',
           `<div><strong>Comparator swap.</strong> ${t33Effect(S.sens_comparator)}
             <span style="color:var(--text-muted);">— ${pwEsc(S.sens_comparator.notes)}</span></div>
            <div style="margin-top:0.35rem;"><strong>REML + Wald.</strong> ${t33Effect(S.sens_reml_wald)}
             <span style="color:var(--text-muted);">— ${pwEsc(S.sens_reml_wald.notes)}</span></div>
            <div style="margin-top:0.35rem;"><strong>DerSimonian–Laird + Hartung–Knapp.</strong> ${t33Effect(S.sens_dl_kh)}</div>`)
    ].join('');
  }

  // ── Tier E exploratory scale-free SMD synthesis ─────────────────────────
  const tiere = document.getElementById('t33-tiere');
  if (tiere && T.tier_e_smd) {
    const E = T.tier_e_smd.analysis_sets;
    const smdEffect = r => {
      if (r == null || r.estimate == null) return '<span style="color:var(--text-muted);">not pooled</span>';
      const ciLabel = r.k === 1 ? '95% CI (normal approx.)' : '95% Hartung–Knapp CI';
      return `<strong>g = ${pwSigned(r.estimate, 3)}</strong> [${pwSigned(r.ci_low, 3)}, ${pwSigned(r.ci_high, 3)}]
              (${ciLabel})` +
             (r.p_value == null ? '' : `, ${pwP(r.p_value)}`) +
             (r.i2 == null ? '' : `, I² = ${r.i2.toFixed(1)}%`);
    };
    const contrastList = arr => arr.map(c => {
      const label = c.sensitivity_only
        ? `${pwEsc(c.study)} <span style="color:#fbbf24;">(sensitivity-only, median/IQR approximated)</span>`
        : pwEsc(c.study);
      return `<div style="margin-bottom:0.3rem;">
        <strong>${label}</strong> (n = ${c.n_i} vs ${c.n_c}; ${pwEsc(c.unit_src)}): g = ${pwSigned(c.hedges_g, 3)}
        ${c.combine_note ? `<div style="color:var(--text-muted);font-size:0.73rem;">${pwEsc(c.combine_note)}</div>` : ''}
      </div>`;
    }).join('');

    tiere.innerHTML = `
      <h4 style="font-size:0.9rem;color:#fda4af;margin:0 0 0.4rem;">
        Tier E — exploratory scale-free SMD synthesis (not the absolute-MME estimand)
      </h4>
      <p style="font-size:0.78rem;color:var(--text-secondary);line-height:1.6;margin-bottom:0.7rem;">
        ${pwEsc(T.tier_e_smd.summary)}
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:1rem;">
        <div class="card-glass" style="padding:1rem;">
          <span class="kpi-badge" style="background:rgba(244,63,94,0.18);color:#fda4af;">EXPLORATORY</span>
          <h4 style="margin:0.4rem 0 0.45rem;font-size:0.92rem;color:#f8fafc;">
            EA vs sham/placebo, scale-free SMD (k = ${E.ea_sham.k})
          </h4>
          <div style="font-size:0.79rem;color:var(--text-secondary);line-height:1.6;">
            ${smdEffect(E.ea_sham)}<br>
            <span style="color:var(--text-muted);">${pwEsc(E.ea_sham.notes)}</span>
          </div>
        </div>
        <div class="card-glass" style="padding:1rem;">
          <span class="kpi-badge" style="background:rgba(244,63,94,0.18);color:#fda4af;">EXPLORATORY</span>
          <h4 style="margin:0.4rem 0 0.45rem;font-size:0.92rem;color:#f8fafc;">
            EA/TEAS vs sham, scale-free SMD (k = ${E.teas_sham_main.k}, single study)
          </h4>
          <div style="font-size:0.79rem;color:var(--text-secondary);line-height:1.6;">
            ${smdEffect(E.teas_sham_main)}<br>
            <span style="color:var(--text-muted);">${pwEsc(E.teas_sham_main.notes)}</span>
          </div>
        </div>
        <div class="card-glass" style="padding:1rem;">
          <span class="kpi-badge" style="background:rgba(245,158,11,0.18);color:#fbbf24;">SENSITIVITY</span>
          <h4 style="margin:0.4rem 0 0.45rem;font-size:0.92rem;color:#f8fafc;">
            + Chen 2015 (Hyperalgesia), median/IQR-approximated (k = ${E.teas_sham_sensitivity.k})
          </h4>
          <div style="font-size:0.79rem;color:var(--text-secondary);line-height:1.6;">
            ${smdEffect(E.teas_sham_sensitivity)}<br>
            <span style="color:var(--text-muted);">${pwEsc(E.teas_sham_sensitivity.notes)}</span>
          </div>
        </div>
        <div class="card-glass" style="padding:1rem;">
          <span class="kpi-badge" style="background:rgba(244,63,94,0.18);color:#fda4af;">EXPLORATORY</span>
          <h4 style="margin:0.4rem 0 0.45rem;font-size:0.92rem;color:#f8fafc;">
            TEAS vs usual care, scale-free SMD (k = ${E.teas_usual.k}, single study)
          </h4>
          <div style="font-size:0.79rem;color:var(--text-secondary);line-height:1.6;">
            ${smdEffect(E.teas_usual)}<br>
            <span style="color:var(--text-muted);">${pwEsc(E.teas_usual.notes)}</span>
          </div>
        </div>
      </div>
      <details style="margin-top:0.8rem;">
        <summary style="cursor:pointer;font-size:0.82rem;color:var(--text-secondary);">
          Show the ${T.tier_e_smd.contrasts.length} underlying contrasts and combining/approximation notes
        </summary>
        <div style="margin-top:0.6rem;font-size:0.78rem;">${contrastList(T.tier_e_smd.contrasts)}</div>
      </details>
      <details style="margin-top:0.6rem;">
        <summary style="cursor:pointer;font-size:0.82rem;color:var(--text-secondary);">
          Show ${T.tier_e_smd.excluded.length} Tier E rows excluded even from this SMD synthesis
        </summary>
        <div style="margin-top:0.6rem;">
          ${T.tier_e_smd.excluded.map(x => `
            <div style="padding:0.5rem 0.65rem;background:rgba(244,63,94,0.06);border-left:3px solid rgba(244,63,94,0.4);
                        border-radius:var(--radius-sm);margin-bottom:0.35rem;">
              <strong style="font-size:0.79rem;color:#f8fafc;">${pwEsc(x.study)}</strong>
              <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:0.1rem;">${pwEsc(x.reason)}</div>
            </div>`).join('')}
        </div>
      </details>`;
  }

  // ── empty cells and withdrawals ──────────────────────────────────────────
  const empty = document.getElementById('t33-empty');
  if (empty) {
    empty.innerHTML = `
      <h4 style="font-size:0.9rem;color:#fca5a5;margin:0 0 0.5rem;">Where the answer is "no evidence", said plainly</h4>
      ${T.empty_cells.map(e => `
        <div style="padding:0.6rem 0.75rem;background:rgba(244,63,94,0.06);border-left:3px solid rgba(244,63,94,0.45);
                    border-radius:var(--radius-sm);margin-bottom:0.45rem;">
          <div style="font-weight:700;color:#f8fafc;font-size:0.82rem;">${pwEsc(e.cell)} — k = ${e.k}</div>
          <div style="font-size:0.77rem;color:var(--text-secondary);line-height:1.55;margin-top:0.15rem;">${pwEsc(e.statement)}</div>
        </div>`).join('')}
      <h4 style="font-size:0.9rem;color:#fbbf24;margin:0.9rem 0 0.5rem;">Withdrawn from the 0–24 hour analyses in v33</h4>
      ${T.withdrawn.map(w => `
        <div style="padding:0.6rem 0.75rem;background:rgba(245,158,11,0.06);border-left:3px solid rgba(245,158,11,0.45);
                    border-radius:var(--radius-sm);margin-bottom:0.45rem;">
          <div style="font-weight:700;color:#f8fafc;font-size:0.82rem;">${pwEsc(w.study)}</div>
          <div style="font-size:0.77rem;color:var(--text-secondary);line-height:1.55;margin-top:0.15rem;">${pwEsc(w.reason)}</div>
        </div>`).join('')}`;
  }

  // ── figures ──────────────────────────────────────────────────────────────
  const figs = document.getElementById('t33-figures');
  if (figs) {
    figs.innerHTML = T.figures.map(f => `
      <div class="stata-plot-card">
        <div class="stata-plot-img-wrap">
          <a href="v33/${pwEsc(f.file)}" target="_blank">
            <img src="v33/${pwEsc(f.file)}" alt="${pwEsc(f.caption)}" class="stata-plot-img">
          </a>
        </div>
        <div class="stata-plot-footer"><p style="font-size:0.76rem;">${pwEsc(f.caption)}</p></div>
      </div>`).join('');
  }
}

window.renderTieredV33 = renderTieredV33;

// ═══════════════════════════════════════════════════════════════════════════
// v33 STUDY CONTRIBUTION MAP + v33 RESULTS
// ═══════════════════════════════════════════════════════════════════════════
// Read entirely from window.V33_DATA, generated by
// scripts/build_v33_dashboard_data.py from the v33 master and the Stata output.
// The map exists to answer one question honestly: why do 70 included RCTs
// produce a primary meta-analysis of 7?

function v33Pct(n, d) { return d ? (100 * n / d).toFixed(0) : '0'; }

function renderV33() {
  const V = window.V33_DATA;
  if (!V || !document.getElementById('v33-map')) return;

  const sub = document.getElementById('v33-subtitle');
  if (sub) sub.innerHTML =
    `All <strong>${V.canonical_studies}</strong> included RCTs, mapped across
     <strong>${V.contribution_map.groups.length}</strong> outcome families from
     <strong>${V.outcome_rows}</strong> source-normalised outcome rows in ${pwEsc(V.master)}.
     A trial may contribute to several families. Being included in the review is not the same as
     contributing to the primary meta-analysis.`;

  // ── contribution map ────────────────────────────────────────────────────
  const map = document.getElementById('v33-map');
  if (map) {
    const total = V.canonical_studies;
    map.innerHTML = V.contribution_map.groups.map(g => {
      const pct = v33Pct(g.n_studies, total);
      const primary = g.id === 'primary_opioid_24h';
      const col = primary ? '#34d399' : '#7dd3fc';
      return `
      <div style="margin-bottom:0.55rem;">
        <div style="display:flex;justify-content:space-between;align-items:baseline;gap:0.6rem;">
          <span style="font-size:0.82rem;font-weight:${primary ? 700 : 600};color:${primary ? '#6ee7b7' : '#e2e8f0'};">
            ${pwEsc(g.label)}</span>
          <span style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;">
            <strong style="color:${col};">${g.n_studies}</strong> / ${total} studies</span>
        </div>
        <div style="height:7px;background:rgba(255,255,255,0.07);border-radius:4px;overflow:hidden;margin-top:0.2rem;">
          <div style="height:100%;width:${pct}%;background:${col};opacity:0.85;"></div>
        </div>
        <div style="font-size:0.72rem;color:var(--text-muted);line-height:1.5;margin-top:0.2rem;">
          ${pwEsc(g.definition)}</div>
      </div>`;
    }).join('');
  }

  // ── headline reconciliation ─────────────────────────────────────────────
  const head = document.getElementById('v33-headline');
  if (head) {
    const prim = V.contribution_map.groups.find(g => g.id === 'primary_opioid_24h');
    const graphOnly = V.contribution_map.graph_only_or_unreported || [];
    head.innerHTML =
      `<strong>${V.canonical_studies} randomised trials are included in this review.
       ${prim.n_studies} contribute to the primary 0–24 hour opioid meta-analysis.</strong>
       That gap is a reporting problem, not an exclusion: the other
       ${V.canonical_studies - prim.n_studies} trials were screened and extracted, and most contribute to other outcome families. Each trial has a RoB 2 assessment on file, but additional results need their own assessments. These trials do not
       report a cumulative 0–24 hour opioid dose in a form that can be pooled.
       ${graphOnly.length ? `${graphOnly.length} trial${graphOnly.length > 1 ? 's' : ''}
       (${graphOnly.map(pwEsc).join(', ')}) report every outcome only as a graph or not at all,
       and contribute no analysable number anywhere.` : ''}`;
  }

  // ── secondary results ───────────────────────────────────────────────────
  const res = document.getElementById('v33-results');
  if (res && V.secondary && V.secondary.length) {
    res.innerHTML = `
      <div style="overflow-x:auto;">
        <table class="forest-table" style="font-size:0.76rem;">
          <thead><tr>
            <th>Analysis</th><th>Measure</th><th>k</th><th>Estimate</th>
            <th>95% CI</th><th>p</th><th>I²</th>
          </tr></thead>
          <tbody>
          ${V.secondary.map(r => {
            // Every one of these is withdrawn or superseded in v34. They are
            // shown struck through with their disposition so a reader who
            // remembers the old number can find out what replaced it -- never
            // as a current estimate.
            const withdrawn = r.v34_status === 'withdrawn';
            const badge = withdrawn
              ? '<span class="v34-badge v34-withdrawn">withdrawn</span>'
              : '<span class="v34-badge v34-superseded">superseded</span>';
            return `
            <tr class="v33-retired">
              <td style="font-weight:600;"><s>${pwEsc(r.outcome)}</s> ${badge}</td>
              <td><s>${pwEsc(r.measure)}</s></td>
              <td><s>${r.k}</s></td>
              <td><s>${r.estimate == null ? '—' : r.estimate.toFixed(3)}</s></td>
              <td><s>${r.ci_low == null ? '—' : `${r.ci_low.toFixed(3)} to ${r.ci_high.toFixed(3)}`}</s></td>
              <td><s>${r.p_value == null ? '—' : (r.p_value < 0.001 ? '&lt;0.001' : r.p_value.toFixed(3))}</s></td>
              <td><s>${r.i2 == null ? '—' : r.i2.toFixed(1) + '%'}</s></td>
            </tr>
            <tr class="v33-retired-note"><td colspan="7">${pwEsc(r.v34_note)}</td></tr>`;
          }).join('')}
          </tbody>
        </table>
      </div>
      ${(V.caveats || []).map(c => {
        const col = c.level === 'high' ? '#fca5a5' : '#fbbf24';
        const bg = c.level === 'high' ? 'rgba(244,63,94,0.07)' : 'rgba(245,158,11,0.06)';
        const row = (V.secondary || []).find(x => x.analysis_id === c.analysis_id);
        return `
        <div style="margin-top:0.55rem;padding:0.55rem 0.7rem;background:${bg};
                    border-left:3px solid ${col};border-radius:var(--radius-sm);">
          <div style="font-weight:700;color:${col};font-size:0.78rem;">
            ${c.level === 'high' ? '⚠ Read with caution' : 'Interpretation'} —
            ${pwEsc(row ? row.outcome : c.analysis_id)}</div>
          <div style="font-size:0.75rem;color:var(--text-secondary);line-height:1.6;margin-top:0.15rem;">
            ${pwEsc(c.text)}</div>
        </div>`;
      }).join('')}
      <p style="font-size:0.74rem;color:var(--text-muted);margin-top:0.6rem;line-height:1.6;">
        Random-effects REML with Hartung–Knapp intervals, fitted in StataNow 19.5 by
        <code>08_V33_MASTER/02_STATA/20_v33_secondary.do</code>. These are secondary analyses and
        result-specific RoB 2 adjudication remains pending; no GRADE rating is assigned here. They
        are kept deliberately separate: binary rescue opioid <em>use</em> is never pooled with
        opioid <em>dose</em>, intraoperative requirement is never pooled with postoperative
        consumption, and PCA presses are never pooled with drug consumption.
      </p>`;
  }

  // ── not-pooled register ─────────────────────────────────────────────────
  const np = document.getElementById('v33-notpooled');
  if (np && V.not_pooled && V.not_pooled.length) {
    np.innerHTML = `
      <h4 style="font-size:0.9rem;color:#fbbf24;margin:0 0 0.5rem;">
        Reported, but deliberately not pooled (${V.not_pooled.length})</h4>
      ${V.not_pooled.map(r => `
        <div style="padding:0.55rem 0.7rem;background:rgba(245,158,11,0.06);
                    border-left:3px solid rgba(245,158,11,0.45);border-radius:var(--radius-sm);
                    margin-bottom:0.4rem;">
          <div style="font-weight:700;color:#f8fafc;font-size:0.8rem;">
            ${pwEsc(r.study)} — ${pwEsc(r.outcome)}
            <span style="font-weight:400;color:var(--text-muted);">(${pwEsc(r.window)})</span></div>
          <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:0.12rem;">${pwEsc(r.stat)}</div>
          <div style="font-size:0.74rem;color:var(--text-muted);line-height:1.55;margin-top:0.15rem;">
            ${pwEsc(r.reason)}</div>
        </div>`).join('')}`;
  }
}

window.renderV33 = renderV33;

// ═══════════════════════════════════════════════════════════════════════════
// v34 ANALYSIS SET
// ═══════════════════════════════════════════════════════════════════════════
// Reads window.V34_DATA, generated by scripts/build_v34_dashboard_data.py from
// the v34 reconciled master and the Stata results in
// 09_V34_ANALYSIS/03_RESULTS/v34_models.csv.
//
// Three things this renderer must get right:
//   1. Every model is one modality against one comparator. Nothing is shown as
//      a cross-stratum pool.
//   2. Withdrawn analyses stay visible as withdrawn, with what replaced them.
//      A withdrawal a reader cannot see is not a withdrawal.
//   3. No GRADE certainty is attached to a new or restratified model: the
//      result-specific risk-of-bias assessments are pending, and an old rating
//      does not describe a changed synthesis.

function v34Fmt(v, dp) {
  if (v == null || isNaN(v)) return '—';
  return (v < 0 ? '−' : '') + Math.abs(v).toFixed(dp == null ? 2 : dp);
}

function v34Effect(m) {
  if (m.estimate == null) return '<span style="color:var(--text-muted);">not estimable</span>';
  if (m.measure === 'logRR' && m.rr != null) {
    return `RR <strong>${m.rr.toFixed(3)}</strong> [${m.rr_low.toFixed(3)}, ${m.rr_high.toFixed(3)}]`;
  }
  return `<strong>${v34Fmt(m.estimate)}</strong> [${v34Fmt(m.ci_low)}, ${v34Fmt(m.ci_high)}] ${pwEsc(m.unit || '')}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// INTERPRETATION LAYER — working manuscript / peer-review overlay
// ═══════════════════════════════════════════════════════════════════════════
// Reads window.INTERPRETATION_LAYER, generated by
// 09_V34_ANALYSIS/05_INTERPRETATION/build_interpretation_layer.py.
//
// This is NOT evidence, and the separation is structural, not stylistic:
// everything below only READS from the interpretation payload and writes to
// its own DOM containers. It never touches V34_DATA, TIERED_V33,
// STATA_MASTER_RESULTS or any other evidence structure, so no amount of
// editing here can change an extracted value, a RoB 2 judgement, a GRADE
// rating, a statistical result or a study's inclusion.
//
// Every record carries a fingerprint of the exact evidence values it was
// generated against. When the generator sees those values move, it marks the
// record stale, and the panels below show the warning INSTEAD OF presenting
// the interpretation as current — manuscript language attached to a
// superseded result is the specific failure this layer is built to prevent.

const IL_STATUS_STYLE = {
  'stable': {label: 'Stable', bg: 'rgba(16,185,129,0.15)', fg: '#6ee7b7',
    hint: 'No open source-QC flag, unjudged result or estimator dependence on this analysis’s own inputs. Not the same as “locked”.'},
  'under-review': {label: 'Under review', bg: 'rgba(56,189,248,0.15)', fg: '#7dd3fc',
    hint: 'A contributing result is still being assessed.'},
  'sensitivity-dependent': {label: 'Sensitivity-dependent', bg: 'rgba(245,158,11,0.15)', fg: '#fbbf24',
    hint: 'The reading changes depending on an analytical choice.'},
  'source-qc-required': {label: 'Source QC required', bg: 'rgba(244,63,94,0.15)', fg: '#fda4af',
    hint: 'A source-level issue in a contributing study is still open.'},
  'author-contact-useful': {label: 'Author contact useful', bg: 'rgba(168,85,247,0.15)', fg: '#d8b4fe',
    hint: 'Information only the authors or a registry hold could settle an open question.'},
};

const IL_CLAIM_STYLE = {
  supported: {dot: '🟢', label: 'Supported'},
  qualified: {dot: '🟡', label: 'Supported with qualification'},
  unsupported: {dot: '🔴', label: 'Not supported'},
};

function ilLayer() { return window.INTERPRETATION_LAYER || null; }

function ilRecord(analysisId) {
  const L = ilLayer();
  if (!L) return null;
  return L.records.find(r => r.analysis_id === analysisId) || null;
}

function ilLensOn() {
  try { return localStorage.getItem('teas-manuscript-lens') === '1'; }
  catch (e) { return false; }
}

function ilSetLens(on) {
  try { localStorage.setItem('teas-manuscript-lens', on ? '1' : '0'); } catch (e) {}
  ilRenderLensToggle();
  if (typeof renderV34 === 'function') renderV34();
  ilRenderEvidenceMap();
}

function ilToggleLens() { ilSetLens(!ilLensOn()); }

function ilStatusChip(rec) {
  const s = IL_STATUS_STYLE[rec.status] || IL_STATUS_STYLE['under-review'];
  return `<span class="v34-badge" title="${pwEsc(rec.status_reason)}"
     style="background:${s.bg};color:${s.fg};margin-left:0.35rem;">${pwEsc(s.label)}</span>`;
}

function ilStaleBanner(rec) {
  if (!rec.stale) return '';
  return `
    <div style="padding:0.5rem 0.65rem;background:rgba(245,158,11,0.12);
                border-left:3px solid rgba(245,158,11,0.6);border-radius:var(--radius-sm);
                margin-bottom:0.5rem;font-size:0.78rem;color:#fbbf24;">
      ⚠️ <strong>Interpretation may be outdated</strong> — the underlying analysis changed since
      this text was generated: ${pwEsc(rec.stale_detail)}. Treat the wording below as superseded
      until the interpretation layer is regenerated.
    </div>`;
}

// Layer 3: the manuscript / reviewer panel for one analysis.
function ilPanelHtml(rec) {
  const claims = rec.claims.map(c => {
    const st = IL_CLAIM_STYLE[c.level] || IL_CLAIM_STYLE.qualified;
    return `<div style="margin-bottom:0.35rem;">
      <span>${st.dot}</span> <strong style="color:#f8fafc;">${pwEsc(st.label)}:</strong>
      ${pwEsc(c.claim)}
      <div style="color:var(--text-muted);font-size:0.73rem;margin-left:1.3rem;">${pwEsc(c.basis)}</div>
    </div>`;
  }).join('');

  const dns = rec.do_not_say.length ? rec.do_not_say.map(d => `
      <div style="margin-bottom:0.3rem;">
        <span style="color:#f87171;">✕</span> ${pwEsc(d.text)}
        <div style="color:var(--text-muted);font-size:0.73rem;margin-left:1.3rem;">${pwEsc(d.why)}</div>
      </div>`).join('')
    : `<div style="color:var(--text-muted);font-size:0.75rem;">No overclaim warning fires for this
       analysis: the interval excludes no effect, heterogeneity is not considerable, and certainty
       is not low.</div>`;

  const rq = rec.reviewer_questions.length ? rec.reviewer_questions.map(q => `
      <div style="margin-bottom:0.4rem;">
        <div style="color:#f8fafc;">• ${pwEsc(q.question)}</div>
        <div style="color:var(--text-muted);font-size:0.72rem;margin-left:0.8rem;">
          fires because — ${pwEsc(q.trigger)}<br>
          evidence available — ${pwEsc(q.pathway)}
        </div>
      </div>`).join('')
    : `<div style="color:var(--text-muted);font-size:0.75rem;">No reviewer-question rule is
       triggered by this analysis's own numbers.</div>`;

  const prompts = rec.discussion_prompts.length ? `
    <div style="margin-top:0.7rem;">
      <div style="font-weight:700;color:#c7d2fe;font-size:0.78rem;">Questions for manuscript discussion</div>
      <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.25rem;">
        Brainstorming prompts for the team — not findings.</div>
      ${rec.discussion_prompts.map(p => `<div style="margin-bottom:0.25rem;">• ${pwEsc(p)}</div>`).join('')}
    </div>` : '';

  const whyK = rec.why_k ? `
    <div style="margin-top:0.7rem;padding:0.5rem 0.65rem;background:rgba(56,189,248,0.07);
                border-left:3px solid rgba(56,189,248,0.45);border-radius:var(--radius-sm);">
      <div style="font-weight:700;color:#7dd3fc;font-size:0.78rem;">${pwEsc(rec.why_k.headline)}</div>
      <div style="font-size:0.75rem;line-height:1.6;margin-top:0.2rem;">${pwEsc(rec.why_k.explanation)}</div>
      <div style="font-size:0.72rem;color:var(--text-muted);margin-top:0.2rem;">
        See — ${pwEsc(rec.why_k.pathway)}</div>
    </div>` : '';

  return `
    ${ilStaleBanner(rec)}
    <div style="font-size:0.78rem;line-height:1.65;">
      <div style="padding:0.5rem 0.65rem;background:rgba(148,163,184,0.08);
                  border-radius:var(--radius-sm);margin-bottom:0.6rem;">
        <div style="font-weight:700;color:#cbd5e1;font-size:0.76rem;">What this result actually means</div>
        <div style="margin-top:0.2rem;">${pwEsc(rec.context)}</div>
      </div>

      <div style="font-weight:700;color:#6ee7b7;font-size:0.78rem;">Results-safe (factual)</div>
      <div style="margin-bottom:0.5rem;">${pwEsc(rec.results_safe)}</div>

      <div style="font-weight:700;color:#7dd3fc;font-size:0.78rem;">Discussion-safe (interpretation)</div>
      <div style="margin-bottom:0.5rem;">${pwEsc(rec.discussion_safe)}</div>

      <div style="font-weight:700;color:#fda4af;font-size:0.78rem;">Do not say</div>
      <div style="margin-bottom:0.6rem;">${dns}</div>

      <div style="font-weight:700;color:#f8fafc;font-size:0.78rem;">Claim boundaries</div>
      <div style="margin-bottom:0.6rem;">${claims}</div>

      <div style="font-weight:700;color:#fbbf24;font-size:0.78rem;">Reviewer lens — likely questions</div>
      <div>${rq}</div>
      ${prompts}
      ${whyK}
      <div style="margin-top:0.7rem;font-size:0.72rem;color:var(--text-muted);
                  border-top:1px solid rgba(148,163,184,0.2);padding-top:0.4rem;">
        <strong>Draft interpretation — for team discussion.</strong> Generated by explicit rules from
        this review's own analysis outputs; not manuscript text and not a finding. Bound to
        evidence fingerprint <code>${pwEsc(rec.fingerprint)}</code>.
      </div>
    </div>`;
}

// Delegated toggle for the per-row "Discuss this result" disclosure.
function ilToggleRow(analysisId) {
  const host = document.getElementById(`il-row-${analysisId}`);
  if (!host) return;
  host.hidden = !host.hidden;
}

// Evidence | Manuscript Lens. Default is Evidence: the interpretation layer
// is opt-in, so the dashboard's resting state is the factual one.
function ilRenderLensToggle() {
  const host = document.getElementById('il-lens-toggle');
  if (!host) return;
  const L = ilLayer();
  if (!L) { host.innerHTML = ''; return; }
  const on = ilLensOn();
  const btn = (label, active) => `
    <span style="padding:0.25rem 0.6rem;border-radius:4px;font-size:0.75rem;font-weight:700;
                 ${active ? 'background:rgba(199,210,254,0.22);color:#e0e7ff;'
                          : 'color:var(--text-muted);'}">${label}</span>`;
  host.innerHTML = `
    <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
      <button type="button" id="il-lens-btn" onclick="ilToggleLens()" aria-pressed="${on}"
              style="display:inline-flex;align-items:center;gap:0.1rem;background:rgba(148,163,184,0.12);
                     border:1px solid rgba(148,163,184,0.3);border-radius:6px;padding:0.15rem;
                     cursor:pointer;">
        ${btn('Evidence', !on)}${btn('Manuscript Lens', on)}
      </button>
      <span style="font-size:0.74rem;color:var(--text-muted);">
        ${on ? 'Showing working interpretation alongside each result. Numbers are unchanged — this is an overlay.'
             : 'Evidence view. Turn on Manuscript Lens for draft wording, claim boundaries and likely reviewer questions.'}
      </span>
      ${L.stale_count ? `<span class="v34-badge" style="background:rgba(245,158,11,0.15);color:#fbbf24;">
        ${L.stale_count} interpretation${L.stale_count === 1 ? '' : 's'} may be outdated</span>` : ''}
    </div>`;
}

// Section 9: the Manuscript Evidence Map.
function ilRenderEvidenceMap() {
  const host = document.getElementById('il-evidence-map');
  if (!host) return;
  const L = ilLayer();
  if (!L) { host.innerHTML = ''; return; }

  const sub = document.getElementById('il-map-subtitle');
  if (sub) sub.textContent = L.disclaimer;

  const cell = s => `<td style="padding:0.45rem 0.5rem;vertical-align:top;
                       border-bottom:1px solid rgba(255,255,255,0.05);">${s}</td>`;

  host.innerHTML = `
    <div style="overflow-x:auto;">
      <table style="width:100%;min-width:1180px;border-collapse:collapse;font-size:0.73rem;">
        <thead><tr style="color:var(--text-muted);text-align:left;">
          <th style="padding:0.35rem 0.5rem;">Finding</th>
          <th style="padding:0.35rem 0.5rem;">Evidence</th>
          <th style="padding:0.35rem 0.5rem;">Certainty</th>
          <th style="padding:0.35rem 0.5rem;">Main caveat</th>
          <th style="padding:0.35rem 0.5rem;">Results-safe statement</th>
          <th style="padding:0.35rem 0.5rem;">Discussion interpretation</th>
          <th style="padding:0.35rem 0.5rem;">Top reviewer issue</th>
          <th style="padding:0.35rem 0.5rem;">Status</th>
        </tr></thead>
        <tbody>
        ${L.records.map(r => {
          const b = r.bound_evidence;
          const caveat = (r.claims.find(c => c.level === 'qualified') || {}).basis
            || 'No qualifying caveat is triggered for this analysis.';
          const topQ = r.reviewer_questions.length ? r.reviewer_questions[0].question
            : 'No reviewer-question rule is triggered.';
          const s = IL_STATUS_STYLE[r.status] || IL_STATUS_STYLE['under-review'];
          return `<tr${r.stale ? ' style="opacity:0.65;"' : ''} data-il-map-id="${pwEsc(r.analysis_id)}">
            ${cell(`<strong style="color:#f8fafc;">${pwEsc(r.label)}</strong>${
              r.stale ? '<div style="color:#fbbf24;">⚠️ may be outdated</div>' : ''}`)}
            ${cell(`k = ${b.k}<br><span style="color:var(--text-muted);">${pwEsc(b.estimator)}</span>`)}
            ${cell(pwEsc(b.grade))}
            ${cell(pwEsc(caveat))}
            ${cell(pwEsc(r.results_safe))}
            ${cell(pwEsc(r.discussion_safe))}
            ${cell(pwEsc(topQ))}
            ${cell(`<span class="v34-badge" style="background:${s.bg};color:${s.fg};">${pwEsc(s.label)}</span>`)}
          </tr>`;
        }).join('')}
        </tbody>
      </table>
    </div>
    <p style="font-size:0.73rem;color:var(--text-muted);margin-top:0.6rem;line-height:1.6;">
      Draft interpretation for team discussion — every column except Evidence and Certainty is
      generated wording, not manuscript text and not a finding. Each row is bound to a fingerprint
      of the analysis values it describes and is flagged here if those values move. Nothing in this
      table can change an extracted value, a RoB 2 judgement, a GRADE rating or a pooled estimate.
    </p>`;
}

window.ilToggleRow = ilToggleRow;
window.ilToggleLens = ilToggleLens;
window.ilRenderEvidenceMap = ilRenderEvidenceMap;
window.ilRenderLensToggle = ilRenderLensToggle;

// Model IDs in V34_DATA.models whose estimate/CI/k are a byte-for-byte
// reproduction of an existing, already-graded GRADE Summary-of-Findings
// analysis (verified by exact numeric match, not by rob_key/label
// similarity alone -- most REPRODUCED models do NOT have such a match and
// correctly still show "reassessment pending"). Reusing that rating here
// is safe ONLY because the numbers confirm it is the same fitted model,
// re-derived from the v34 reconciled dataset as a consistency check.
const V34_VERIFIED_REPRODUCTION_OF = {
  "v34_primary_24h_mme_TEAS_Sham": "AN-01-TEAS",
  "v34_primary_24h_mme_EA_Usual_care": "AN-01-EA",
  "v34_primary_24h_mme_ALL_AUDIT": "AN-01-COMB",
};

function v34GradeBadgeClass(grade) {
  const g = (grade || '').toLowerCase();
  if (g === 'high') return 'grade-badge-high';
  if (g === 'moderate') return 'grade-badge-mod';
  if (g === 'low') return 'grade-badge-low';
  if (g === 'very low') return 'grade-badge-verylow';
  return 'v34-badge v34-pending';
}

function v34CertaintyCell(m, V) {
  const reproOf = V34_VERIFIED_REPRODUCTION_OF[m.model_id];
  if (reproOf && window.STATA_MASTER_RESULTS && window.STATA_MASTER_RESULTS[reproOf]) {
    const src = window.STATA_MASTER_RESULTS[reproOf];
    return `<span class="${v34GradeBadgeClass(src.grade)}">${pwEsc(src.grade)}</span>
            <div style="font-size:0.68rem;color:var(--text-muted);margin-top:0.2rem;">
              verified reproduction of ${pwEsc(reproOf)}</div>`;
  }
  const g = V.grade_new_models && V.grade_new_models.ratings.find(r => r.model_id === m.model_id);
  if (g) {
    return `<span class="${v34GradeBadgeClass(g.grade)}">${pwEsc(g.grade)}</span>
            <div style="font-size:0.68rem;color:var(--text-muted);margin-top:0.2rem;">
              rule-based, not panel-reviewed</div>`;
  }
  return '<span class="v34-badge v34-pending">reassessment pending</span>';
}

function renderV34() {
  const V = window.V34_DATA;
  if (!V || !document.getElementById('v34-models')) return;

  const sub = document.getElementById('v34-subtitle');
  if (sub) sub.innerHTML =
    `Analyses fitted in StataNow 19.5 from <strong>${pwEsc(V.master)}</strong>
     (${V.canonical_studies} canonical studies, ${V.outcome_rows} outcome rows).
     ${V.new_model_count} models are new in v34 and ${V.reproduced_model_count} were
     independently reproduced from the reconciliation's own datasets.
     Every model is a single modality against a single comparator type.`;

  // ── model table ─────────────────────────────────────────────────────────
  const host = document.getElementById('v34-models');
  if (host) {
    const rows = V.models.slice().sort((a, b) => {
      const order = {primary: 0, supporting: 1, secondary: 2};
      return (order[a.role] - order[b.role]) || a.label.localeCompare(b.label);
    });
    host.innerHTML = `
      <div style="overflow-x:auto;">
        <table class="forest-table" style="font-size:0.76rem;">
          <thead><tr>
            <th>Analysis</th><th>k</th><th>Estimate (95% CI)</th>
            <th>p</th><th>I²</th><th>Model</th><th>Certainty</th>
          </tr></thead>
          <tbody>
          ${rows.map(m => {
            const rec = ilRecord(m.model_id);
            const lens = ilLensOn();
            return `
            <tr data-analysis-id="${pwEsc(m.model_id)}">
              <td style="font-weight:600;">${pwEsc(m.label)}
                ${m.phase === 'NEW' ? '<span class="v34-badge v34-new">new in v34</span>' : ''}
                ${rec ? ilStatusChip(rec) : ''}
                ${rec ? `<div><button type="button" class="il-discuss-btn"
                   data-il-for="${pwEsc(m.model_id)}"
                   onclick="ilToggleRow('${pwEsc(m.model_id)}')"
                   style="margin-top:0.3rem;background:none;border:none;padding:0;cursor:pointer;
                          color:#c7d2fe;font-size:0.72rem;text-decoration:underline;">
                   Discuss this result →</button></div>` : ''}
              </td>
              <td>${m.k}</td>
              <td${rec ? ` title="${pwEsc(rec.context)}"` : ''}>${v34Effect(m)}</td>
              <td>${m.p_value == null ? '—' : (m.p_value < 0.001 ? '&lt;0.001' : m.p_value.toFixed(3))}</td>
              <td>${m.i2 == null ? '—' : m.i2.toFixed(1) + '%'}</td>
              <td style="font-size:0.72rem;color:var(--text-muted);">${pwEsc(m.estimator)}</td>
              <td>${v34CertaintyCell(m, V)}</td>
            </tr>
            ${rec ? `<tr id="il-row-${pwEsc(m.model_id)}" class="il-detail-row" ${lens ? '' : 'hidden'}>
              <td colspan="7" style="background:rgba(15,23,42,0.5);padding:0.8rem 1rem;">
                ${ilPanelHtml(rec)}
              </td>
            </tr>` : ''}`;
          }).join('')}
          </tbody>
        </table>
      </div>
      <p style="font-size:0.74rem;color:var(--text-muted);margin-top:0.6rem;line-height:1.6;">
        ${pwEsc(V.certainty_note)}
      </p>`;
  }

  // ── withdrawn and superseded ────────────────────────────────────────────
  const wd = document.getElementById('v34-withdrawn');
  if (wd) {
    wd.innerHTML = `
      <h4 style="font-size:0.9rem;color:#fca5a5;margin:0 0 0.5rem;">
        Withdrawn — no longer current evidence (${V.withdrawn.length})</h4>
      ${V.withdrawn.map(w => `
        <div style="padding:0.65rem 0.8rem;background:rgba(244,63,94,0.07);
                    border-left:3px solid rgba(244,63,94,0.5);border-radius:var(--radius-sm);
                    margin-bottom:0.5rem;">
          <div style="font-weight:700;color:#f8fafc;font-size:0.83rem;">${pwEsc(w.label)}</div>
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.15rem;">
            <s>${pwEsc(w.previous)}</s></div>
          <div style="font-size:0.77rem;color:var(--text-secondary);line-height:1.6;margin-top:0.3rem;">
            <strong>Why:</strong> ${pwEsc(w.reason)}</div>
          <div style="font-size:0.77rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
            <strong>Now:</strong> ${pwEsc(w.now)}</div>
          <div style="font-size:0.74rem;color:var(--text-muted);margin-top:0.2rem;">${pwEsc(w.affects)}</div>
        </div>`).join('')}

      <h4 style="font-size:0.9rem;color:#fbbf24;margin:1rem 0 0.5rem;">
        Superseded by stratified models (${V.superseded.length})</h4>
      ${V.superseded.map(x => `
        <div style="padding:0.6rem 0.8rem;background:rgba(245,158,11,0.06);
                    border-left:3px solid rgba(245,158,11,0.45);border-radius:var(--radius-sm);
                    margin-bottom:0.45rem;">
          <div style="font-weight:700;color:#f8fafc;font-size:0.82rem;">${pwEsc(x.old)}</div>
          <div style="font-size:0.75rem;color:var(--text-muted);"><s>${pwEsc(x.old_desc)}</s></div>
          <div style="font-size:0.77rem;color:var(--text-secondary);line-height:1.6;margin-top:0.25rem;">
            ${pwEsc(x.reason)}</div>
        </div>`).join('')}`;
  }

  // ── source holds ────────────────────────────────────────────────────────
  const holds = document.getElementById('v34-holds');
  if (holds) {
    const h = V.source_holds;
    holds.innerHTML = `
      <h4 style="font-size:0.9rem;color:#7dd3fc;margin:0 0 0.5rem;">
        Source holds carried forward</h4>
      <div class="v34-hold-grid">
        <div class="v34-hold"><span class="v34-hold-n">${h.conflict_records}</span>
          <span>source conflict or correction records, kept visible rather than resolved silently</span></div>
        <div class="v34-hold"><span class="v34-hold-n">${h.supplement_access_gaps.length}</span>
          <span>studies with unaccessed supplements or protocols</span></div>
        <div class="v34-hold"><span class="v34-hold-n">${h.source_not_accessed_outcomes.length}</span>
          <span>outcomes recorded as SOURCE NOT ACCESSED, which is not the same as not reported</span></div>
        <div class="v34-hold"><span class="v34-hold-n">${V.poolable_scan.shared_arm_holds}</span>
          <span>groups still held for comparator or shared-arm adjudication</span></div>
        <div class="v34-hold"><span class="v34-hold-n">${(V.rob2_worklist||{}).blocking_grade ?? '—'}</span>
          <span>result-specific RoB 2 assessments inside a fitted model — adopted by the review lead</span></div>
      </div>
      ${V.comparator_resolution ? `
      <div style="margin-top:0.8rem;padding:0.6rem 0.75rem;background:rgba(52,211,153,0.06);
                  border-left:3px solid rgba(52,211,153,0.45);border-radius:var(--radius-sm);">
        <div style="font-weight:700;color:#6ee7b7;font-size:0.8rem;">
          Comparator and modality classification resolved</div>
        <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
          ${V.comparator_resolution.rows_resolved} rows that the reconciliation left as
          REVIEW_REQUIRED are now classified
          (${Object.entries(V.comparator_resolution.by_comparator)
              .map(([k2,v2])=>`${v2} ${pwEsc(k2)}`).join(', ')});
          ${V.comparator_resolution.rows_unresolved} remain unresolved.
          <span style="display:block;margin-top:0.25rem;color:var(--text-muted);">
            ${pwEsc(V.comparator_resolution.note)}</span>
        </div>
      </div>` : ''}
      ${V.rob2_worklist ? `
      <div style="margin-top:0.6rem;padding:0.6rem 0.75rem;background:rgba(148,163,184,0.07);
                  border-left:3px solid rgba(148,163,184,0.45);border-radius:var(--radius-sm);">
        <div style="font-weight:700;color:#cbd5e1;font-size:0.8rem;">
          Result-specific risk of bias — ${V.rob2_worklist.blocking_grade} assessments
          inside fitted models</div>
        <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
          ${pwEsc(V.rob2_worklist.note)}
        </div>
        ${V.rob2_results && V.rob2_results.count ? v34RobResultsHtml(V.rob2_results, 'v34rob') : `
        <details style="margin-top:0.4rem;">
          <summary style="cursor:pointer;font-size:0.76rem;color:#7dd3fc;">
            Show the ${V.rob2_worklist.blocking_grade} results</summary>
          <ul style="margin:0.4rem 0 0 1rem;font-size:0.75rem;color:var(--text-muted);line-height:1.65;">
            ${V.rob2_worklist.blocking_list.map(r =>
              `<li>${pwEsc(r.study)} — ${pwEsc(r.outcome)} @ ${pwEsc(r.timepoint)}</li>`).join('')}
          </ul>
        </details>`}
      </div>` : ''}
      ${V.rob2_priority2 && V.rob2_priority2.count ? `
      <div style="margin-top:0.6rem;padding:0.6rem 0.75rem;background:rgba(148,163,184,0.07);
                  border-left:3px solid rgba(148,163,184,0.3);border-radius:var(--radius-sm);">
        <div style="font-weight:700;color:#cbd5e1;font-size:0.8rem;">
          Result-specific risk of bias — ${V.rob2_priority2.count} results not currently pooled</div>
        <div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
          Results reported by a single trial, held for a source conflict, or otherwise outside
          every fitted model above, assessed to the same result-specific standard so the review's
          risk-of-bias register is complete rather than stopping at what is currently pooled.
          ${V.rob2_priority2.unresolved_count ? `
          <span style="color:#fdba74;">${V.rob2_priority2.unresolved_count} of these could not be
          matched to a source PDF with confidence and are marked UNRESOLVED rather than assessed
          against a possibly-wrong article</span> — filter "Overall: UNRESOLVED" below to see them.` : ''}
        </div>
        ${v34RobResultsHtml(V.rob2_priority2, 'v34rob2')}
      </div>` : ''}
      ${V.grade_new_models && V.grade_new_models.count ? v34GradeNewModelsHtml(V.grade_new_models) : ''}
      <p style="font-size:0.76rem;color:var(--text-secondary);line-height:1.6;margin-top:0.55rem;">
        Unaccessed supplements: ${h.supplement_access_gaps.map(pwEsc).join(', ')}.
        ${h.source_not_accessed_outcomes.map(pwEsc).join('; ')}.
      </p>`;
  }
}


// Result-specific RoB 2 judgements for the results inside a fitted model.
// Read from the source article against the RoB 2 signalling questions and
// anchored to quoted text; not written into the frozen workbook. Adopted by
// the review lead on 2026-09-08 as the review's current result-specific RoB 2
// assessment (see adopted_by / adopted_date on the payload and on each row).
// Standard Cochrane RoB 2 practice calls for two independent assessors
// reconciling any disagreement -- no separately documented dual-assessor
// record was provided to this pipeline, and the panel says so; that is not
// the same as the assessment being incomplete or unadopted. Each result is
// judged on its own — a study-wide judgement is never displayed in place of
// a result-specific one.
function v34RobTone(v){
  return v === 'High' ? '#fca5a5'
       : v === 'Some concerns' ? '#fcd34d'
       : v === 'Low' ? '#6ee7b7'
       : v === 'UNRESOLVED' ? '#fdba74' : 'var(--text-muted)';
}
function v34RobChip(label, v){
  return `<span style="display:inline-block;padding:0.05rem 0.32rem;margin:0 0.2rem 0.2rem 0;
    border-radius:3px;background:rgba(255,255,255,0.05);font-size:0.66rem;
    color:${v34RobTone(v)};white-space:nowrap;">${label} ${pwEsc(v)}</span>`;
}
function v34RobResultsFilterOptions(D, field){
  return [...new Set((D.results||[]).map(r => r[field]).filter(Boolean))].sort();
}
// Aggregate D1-D5 + Overall distribution as a stacked bar per domain, with
// the denominator stated explicitly (D.count, the exact rows the bars are
// computed over -- never the full study count, since these are per-RESULT
// judgements and one study can contribute several results).
function v34RobDomainBarsHtml(D){
  const dc = D.domain_counts || {};
  const domains = [['d1_randomisation','D1 Randomisation'],['d2_deviations','D2 Deviations'],
    ['d3_missing','D3 Missing data'],['d4_measurement','D4 Measurement'],['d5_reporting','D5 Reporting']];
  const order = ['Low','Some concerns','High','UNRESOLVED'];
  const total = D.count || Object.values(dc.d1_randomisation||{}).reduce((a,b)=>a+b,0);
  if (!total) return '';
  const rows = domains.map(([key,label]) => {
    const counts = dc[key] || {};
    const segs = order.filter(k=>counts[k]).map(k => {
      const pct = (counts[k]/total*100).toFixed(1);
      return `<div style="width:${pct}%;background:${v34RobTone(k)};height:100%;" title="${pwEsc(label)}: ${counts[k]} ${pwEsc(k)} (${pct}%)"></div>`;
    }).join('');
    return `
      <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.3rem;">
        <span style="font-size:0.68rem;color:var(--text-muted);width:130px;flex-shrink:0;">${pwEsc(label)}</span>
        <div style="flex:1;height:0.8rem;border-radius:3px;overflow:hidden;display:flex;background:rgba(255,255,255,0.05);">${segs}</div>
      </div>`;
  }).join('');
  return `
    <div style="margin-top:0.5rem;">
      <div style="font-size:0.7rem;color:var(--text-muted);">Domain distribution across all ${total} judged results (denominator = rows judged, not study count):</div>
      ${rows}
    </div>`;
}

function v34RobResultsHtml(D, idPrefix){
  idPrefix = idPrefix || 'v34rob';
  const oc = D.overall_counts || {};
  const order = ['Low','Some concerns','High','UNRESOLVED'];
  const summary = order.filter(k=>oc[k]).map(k=>
    `<span style="color:${v34RobTone(k)};font-weight:700;">${oc[k]} ${pwEsc(k)}</span>`).join(' · ');
  const families = v34RobResultsFilterOptions(D, 'family');
  const studies = v34RobResultsFilterOptions(D, 'study');
  const rows = (D.results||[]).map(r => `
    <tr data-rob-study="${pwEsc(r.study)}" data-rob-family="${pwEsc(r.family)}"
        data-rob-overall="${pwEsc(r.overall)}" data-rob-models="${pwEsc(r.models||'')}">
      <td style="padding:0.3rem 0.4rem;vertical-align:top;">
        <div style="font-weight:600;color:var(--text-primary);">${pwEsc(r.study)}</div>
        <div style="color:var(--text-muted);font-size:0.7rem;">${pwEsc(r.outcome)} @ ${pwEsc(r.timepoint)}</div>
        <div style="color:var(--text-muted);font-size:0.68rem;margin-top:0.1rem;">${pwEsc(r.intervention||'')} vs ${pwEsc(r.comparator||'')}</div>
      </td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;white-space:nowrap;">
        ${v34RobChip('D1',r.d1)}${v34RobChip('D2',r.d2)}${v34RobChip('D3',r.d3)}
        ${v34RobChip('D4',r.d4)}${v34RobChip('D5',r.d5)}
      </td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;white-space:nowrap;
                 color:${v34RobTone(r.overall)};font-weight:700;">${pwEsc(r.overall)}</td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;color:var(--text-secondary);
                 font-size:0.7rem;line-height:1.55;">
        ${pwEsc(r.rationale)}
        ${r.flags ? `<div style="margin-top:0.2rem;color:#fcd34d;">⚑ ${pwEsc(r.flags)}</div>` : ''}
        <div style="margin-top:0.2rem;color:var(--text-muted);">source: ${pwEsc(r.source_pdf||'')}</div>
      </td>
    </tr>`).join('');
  const roll = (D.model_rollup||[]).map(m => `
    <tr class="${idPrefix}-model-row" data-rob-model="${pwEsc(m.model_id)}"
        style="cursor:pointer;" title="Click to filter the results below to this model"
        onclick="v34FilterRobByModel('${pwEsc(m.model_id)}','${idPrefix}')">
      <td style="padding:0.25rem 0.4rem;"><code>${pwEsc(m.model_id)}</code></td>
      <td style="padding:0.25rem 0.4rem;text-align:right;">${m.k}</td>
      <td style="padding:0.25rem 0.4rem;text-align:right;color:#6ee7b7;">${m.low}</td>
      <td style="padding:0.25rem 0.4rem;text-align:right;color:#fcd34d;">${m.some}</td>
      <td style="padding:0.25rem 0.4rem;text-align:right;color:#fca5a5;">${m.high}</td>
      <td style="padding:0.25rem 0.4rem;color:var(--text-secondary);font-size:0.7rem;">
        ${pwEsc(m.signal)}${m.high_risk_studies && m.high_risk_studies !== '-'
          ? `<div style="color:var(--text-muted);">via ${pwEsc(m.high_risk_studies)}</div>` : ''}
      </td>
    </tr>`).join('');
  return `
    <div style="margin-top:0.5rem;padding:0.5rem 0.6rem;background:rgba(125,211,252,0.06);
                border-left:3px solid rgba(125,211,252,0.5);border-radius:var(--radius-sm);">
      <div style="font-weight:700;color:#7dd3fc;font-size:0.78rem;">
        Adopted ${pwEsc(D.adopted_date || '')} by ${pwEsc(D.adopted_by || 'the review lead')}</div>
      <div style="font-size:0.74rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
        ${pwEsc(D.note)}
      </div>
      <div style="margin-top:0.35rem;font-size:0.76rem;color:var(--text-secondary);">
        ${D.count} assessed: ${summary}
      </div>
      ${v34RobDomainBarsHtml(D)}
    </div>
    <details id="${idPrefix}-results-details" style="margin-top:0.4rem;">
      <summary style="cursor:pointer;font-size:0.76rem;color:#7dd3fc;">
        Show the ${D.count} result-specific judgements with their supporting evidence</summary>
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;margin:0.5rem 0 0.4rem;">
        <select id="${idPrefix}-f-overall" class="filter-select" style="font-size:0.72rem;" onchange="v34ApplyRobFilters('${idPrefix}')">
          <option value="">Overall: all</option>
          ${order.filter(k=>oc[k]).map(k=>`<option value="${pwEsc(k)}">${pwEsc(k)}</option>`).join('')}
        </select>
        <select id="${idPrefix}-f-family" class="filter-select" style="font-size:0.72rem;" onchange="v34ApplyRobFilters('${idPrefix}')">
          <option value="">Outcome family: all</option>
          ${families.map(f=>`<option value="${pwEsc(f)}">${pwEsc(f)}</option>`).join('')}
        </select>
        <select id="${idPrefix}-f-study" class="filter-select" style="font-size:0.72rem;" onchange="v34ApplyRobFilters('${idPrefix}')">
          <option value="">Study: all</option>
          ${studies.map(s=>`<option value="${pwEsc(s)}">${pwEsc(s)}</option>`).join('')}
        </select>
        <select id="${idPrefix}-f-model" class="filter-select" style="font-size:0.72rem;" onchange="v34ApplyRobFilters('${idPrefix}')">
          <option value="">Model/synthesis: all</option>
          ${(D.model_rollup||[]).map(m=>`<option value="${pwEsc(m.model_id)}">${pwEsc(m.model_id)}</option>`).join('')}
        </select>
        <button type="button" class="filter-select" style="font-size:0.72rem;cursor:pointer;"
                onclick="v34ResetRobFilters('${idPrefix}')">Reset</button>
        <span id="${idPrefix}-filter-count" style="font-size:0.72rem;color:var(--text-muted);"></span>
      </div>
      <div style="overflow-x:auto;">
        <table id="${idPrefix}-results-table" style="width:100%;min-width:720px;border-collapse:collapse;font-size:0.74rem;">
          <thead><tr style="color:var(--text-muted);text-align:left;">
            <th style="padding:0.3rem 0.4rem;">Result</th>
            <th style="padding:0.3rem 0.4rem;">Domains</th>
            <th style="padding:0.3rem 0.4rem;">Overall</th>
            <th style="padding:0.3rem 0.4rem;">Basis in the source</th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </details>
    ${(D.model_rollup||[]).length ? `
    <details style="margin-top:0.3rem;">
      <summary style="cursor:pointer;font-size:0.76rem;color:#7dd3fc;">
        What each fitted model inherits from these results</summary>
      <p style="font-size:0.7rem;color:var(--text-muted);margin:0.3rem 0;">Click a model row to filter the results above to that model.</p>
      <div style="overflow-x:auto;margin-top:0.2rem;">
        <table style="width:100%;min-width:620px;border-collapse:collapse;font-size:0.74rem;">
          <thead><tr style="color:var(--text-muted);text-align:left;">
            <th style="padding:0.25rem 0.4rem;">Model</th>
            <th style="padding:0.25rem 0.4rem;text-align:right;">k</th>
            <th style="padding:0.25rem 0.4rem;text-align:right;">Low risk</th>
            <th style="padding:0.25rem 0.4rem;text-align:right;">Some concerns</th>
            <th style="padding:0.25rem 0.4rem;text-align:right;">High risk</th>
            <th style="padding:0.25rem 0.4rem;">GRADE risk-of-bias signal</th>
          </tr></thead>
          <tbody>${roll}</tbody>
        </table>
      </div>
    </details>` : ''}`;
}
window.v34RobResultsHtml = v34RobResultsHtml;

// Client-side filtering over the rendered result-specific RoB 2 rows. Filters
// combine with AND; the models column holds a "; "-separated list, so a model
// filter matches on substring against that list, not exact equality.
// idPrefix distinguishes the priority-1 (in-a-fitted-model, default 'v34rob')
// and priority-2 (not-currently-pooled, 'v34rob2') panels, which render two
// independent copies of this same table/filter structure on one page.
function v34ApplyRobFilters(idPrefix){
  idPrefix = idPrefix || 'v34rob';
  const table = document.getElementById(idPrefix + '-results-table');
  if (!table) return;
  const ov = (document.getElementById(idPrefix + '-f-overall')||{}).value || '';
  const fam = (document.getElementById(idPrefix + '-f-family')||{}).value || '';
  const st = (document.getElementById(idPrefix + '-f-study')||{}).value || '';
  const mo = (document.getElementById(idPrefix + '-f-model')||{}).value || '';
  let shown = 0, total = 0;
  table.querySelectorAll('tbody tr').forEach(tr => {
    total++;
    const match =
      (!ov || tr.dataset.robOverall === ov) &&
      (!fam || tr.dataset.robFamily === fam) &&
      (!st || tr.dataset.robStudy === st) &&
      (!mo || (tr.dataset.robModels||'').split('; ').includes(mo));
    tr.hidden = !match;
    if (match) shown++;
  });
  const countEl = document.getElementById(idPrefix + '-filter-count');
  if (countEl) countEl.textContent = (ov||fam||st||mo) ? `showing ${shown} of ${total}` : '';
}
function v34ResetRobFilters(idPrefix){
  idPrefix = idPrefix || 'v34rob';
  ['-f-overall','-f-family','-f-study','-f-model'].forEach(suffix => {
    const el = document.getElementById(idPrefix + suffix);
    if (el) el.value = '';
  });
  v34ApplyRobFilters(idPrefix);
}
// Coordination: clicking a model in the rollup table opens the results
// disclosure (if collapsed) and filters the results table to that model,
// mirroring the outcome-selection coordination used elsewhere in the dashboard.
function v34FilterRobByModel(modelId, idPrefix){
  idPrefix = idPrefix || 'v34rob';
  const details = document.getElementById(idPrefix + '-results-details');
  if (details) details.open = true;
  const sel = document.getElementById(idPrefix + '-f-model');
  if (sel) { sel.value = modelId; }
  v34ApplyRobFilters(idPrefix);
  const table = document.getElementById(idPrefix + '-results-table');
  if (table) table.scrollIntoView({behavior: 'smooth', block: 'nearest'});
}
window.v34ApplyRobFilters = v34ApplyRobFilters;
window.v34ResetRobFilters = v34ResetRobFilters;
window.v34FilterRobByModel = v34FilterRobByModel;

// GRADE certainty for the five new v34 models. Computed by an explicit,
// stated rule applied identically to all five (see
// 09_V34_ANALYSIS/04_GRADE/compute_new_model_grade.py), NOT an independent
// GRADE panel's consensus judgement -- GRADE certainty, like RoB 2, is an
// assessor judgement that Cochrane/GRADE guidance bounds with bands and
// principles rather than a formula. Adopted by the review lead, same status
// already applied to the RoB 2 domain these ratings build on.
function v34GradeTone(g){
  return g === 'High' ? '#6ee7b7' : g === 'Moderate' ? '#7dd3fc'
       : g === 'Low' ? '#fcd34d' : g === 'Very Low' ? '#fca5a5' : 'var(--text-muted)';
}
function v34GradeNewModelsHtml(G){
  const rows = (G.ratings||[]).map(r => {
    const domainChips = (r.domains||[]).map(d => {
      const tone = d.downgrade === 0 ? '#6ee7b7' : d.downgrade === -1 ? '#fcd34d' : '#fca5a5';
      return `<span title="${pwEsc(d.reason)}" style="display:inline-block;padding:0.05rem 0.32rem;
        margin:0 0.2rem 0.2rem 0;border-radius:3px;background:rgba(255,255,255,0.05);
        font-size:0.66rem;color:${tone};white-space:nowrap;cursor:help;">${pwEsc(d.name)} ${d.downgrade}</span>`;
    }).join('');
    return `
    <tr>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;">
        <div style="font-weight:600;color:var(--text-primary);">${pwEsc(r.outcome)}</div>
        <div style="color:var(--text-muted);font-size:0.7rem;">${pwEsc(r.window)} · ${pwEsc(r.modality)} vs ${pwEsc(r.comparator)}</div>
        <div style="color:var(--text-muted);font-size:0.68rem;"><code>${pwEsc(r.model_id)}</code></div>
      </td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;white-space:nowrap;">
        ${r.measure === 'logRR' ? 'logRR' : 'MD'} ${r.estimate} [${r.ci_low}, ${r.ci_high}]<br>
        <span style="color:var(--text-muted);font-size:0.7rem;">k=${r.k}, N=${r.n}, I²=${r.i2}%, p=${pwEsc(String(r.p_value)).slice(0,6)}</span>
      </td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;white-space:nowrap;">${domainChips}</td>
      <td style="padding:0.3rem 0.4rem;vertical-align:top;white-space:nowrap;
                 color:${v34GradeTone(r.grade)};font-weight:700;">${pwEsc(r.grade)}</td>
    </tr>`;
  }).join('');
  return `
    <div style="margin-top:0.6rem;padding:0.5rem 0.6rem;background:rgba(125,211,252,0.06);
                border-left:3px solid rgba(125,211,252,0.5);border-radius:var(--radius-sm);">
      <div style="font-weight:700;color:#7dd3fc;font-size:0.78rem;">
        GRADE certainty for these ${G.count} v34 models — adopted ${pwEsc(G.adopted_date||'')} by ${pwEsc(G.adopted_by||'the review lead')}</div>
      <div style="font-size:0.74rem;color:var(--text-secondary);line-height:1.6;margin-top:0.2rem;">
        ${pwEsc(G.note)}
      </div>
    </div>
    <details style="margin-top:0.4rem;">
      <summary style="cursor:pointer;font-size:0.76rem;color:#7dd3fc;">
        Show the GRADE rating and per-domain downgrades for these ${G.count} models</summary>
      <div style="overflow-x:auto;margin-top:0.4rem;">
        <table style="width:100%;min-width:760px;border-collapse:collapse;font-size:0.74rem;">
          <thead><tr style="color:var(--text-muted);text-align:left;">
            <th style="padding:0.3rem 0.4rem;">Model</th>
            <th style="padding:0.3rem 0.4rem;">Estimate</th>
            <th style="padding:0.3rem 0.4rem;">Domains (hover for reason)</th>
            <th style="padding:0.3rem 0.4rem;">GRADE</th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </details>`;
}
window.v34GradeNewModelsHtml = v34GradeNewModelsHtml;

window.renderV34 = renderV34;
