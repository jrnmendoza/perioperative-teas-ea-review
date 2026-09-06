// Perioperative TEAS & EA Systematic Review — Global Reader-Assistance, i18n & Popover System
// Lund University Faculty of Medicine • PROSPERO 2026

(function() {
  'use strict';

  // ══════════════════════════════════════════════════════════════════
  // 1. STATE & STORAGE MANAGEMENT
  // ══════════════════════════════════════════════════════════════════
  let currentLang = 'en';
  let explainStats = 'ON';
  let activePopover = null;
  let hoverTimeout = null;

  function initFromStorage() {
    // Check URL query parameters first: ?lang=en or ?lang=sv
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    if (langParam && (langParam.toLowerCase() === 'sv' || langParam.toLowerCase() === 'en')) {
      currentLang = langParam.toLowerCase();
      localStorage.setItem('app_lang', currentLang);
    } else {
      const storedLang = localStorage.getItem('app_lang');
      if (storedLang && (storedLang === 'sv' || storedLang === 'en')) {
        currentLang = storedLang;
      } else {
        currentLang = 'en';
      }
    }

    // Explain Statistics setting (default: ON for first-time visitors)
    const storedExplain = localStorage.getItem('explain_statistics');
    if (storedExplain === 'OFF') {
      explainStats = 'OFF';
    } else {
      explainStats = 'ON';
      localStorage.setItem('explain_statistics', 'ON');
    }

    applyExplainStatsClasses();
  }

  function applyExplainStatsClasses() {
    const isOff = explainStats === 'OFF';
    document.body.classList.toggle('explain-stats-off', isOff);
    document.body.classList.toggle('explain-stats-on', !isOff);

    const toggleBtn = document.getElementById('toggle-explain-stats');
    const statusText = document.getElementById('explain-stats-status');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-checked', isOff ? 'false' : 'true');
      toggleBtn.classList.toggle('active', !isOff);
    }
    if (statusText) {
      const tDict = window.TRANSLATIONS && window.TRANSLATIONS[currentLang];
      statusText.textContent = isOff 
        ? (tDict?.controls?.explainStatsOff || 'OFF') 
        : (tDict?.controls?.explainStatsOn || 'ON');
    }
  }

  // ══════════════════════════════════════════════════════════════════
  // 2. INTERNATIONALIZATION (i18n) ENGINE
  // ══════════════════════════════════════════════════════════════════
  function t(path, fallback) {
    if (!window.TRANSLATIONS) return fallback || path;
    const dict = window.TRANSLATIONS[currentLang] || window.TRANSLATIONS['en'];
    const parts = path.split('.');
    let val = dict;
    for (let p of parts) {
      if (val && typeof val === 'object' && p in val) {
        val = val[p];
      } else {
        // Fallback to English dictionary
        val = null;
        break;
      }
    }
    if (val !== null && val !== undefined) return val;

    // Fallback to English
    const enDict = window.TRANSLATIONS['en'];
    let enVal = enDict;
    for (let p of parts) {
      if (enVal && typeof enVal === 'object' && p in enVal) {
        enVal = enVal[p];
      } else {
        return fallback || path;
      }
    }
    return enVal || fallback || path;
  }

  function setLanguage(lang) {
    if (lang !== 'en' && lang !== 'sv') return;
    currentLang = lang;
    localStorage.setItem('app_lang', lang);
    document.documentElement.lang = lang;

    // Update active button classes in header
    document.querySelectorAll('.btn-lang').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });

    // Update all text nodes with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const translated = t(key);
      if (translated) {
        el.textContent = translated;
      }
    });

    // Update all HTML nodes with data-i18n-html
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      const translated = t(key);
      if (translated) {
        el.innerHTML = translated;
      }
    });

    // Update titles / tooltips
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      const translated = t(key);
      if (translated) {
        el.setAttribute('title', translated);
      }
    });

    // Update status text on toggle
    applyExplainStatsClasses();

    // Re-render glossary if tab is open
    if (window.activeTab === 'glossary') {
      renderGlossaryTab();
    }

    // Trigger re-render of active dynamic views in app.js
    if (typeof window.renderActiveTab === 'function') {
      window.renderActiveTab();
    }

    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
  }

  function toggleExplainStatistics() {
    explainStats = explainStats === 'ON' ? 'OFF' : 'ON';
    localStorage.setItem('explain_statistics', explainStats);
    applyExplainStatsClasses();
    window.dispatchEvent(new CustomEvent('explainStatsChanged', { detail: { state: explainStats } }));
  }

  // ══════════════════════════════════════════════════════════════════
  // 3. STATISTICAL POPOVER & TOOLTIP SYSTEM
  // ══════════════════════════════════════════════════════════════════
  function createPopoverElement() {
    if (document.getElementById('stat-popover-container')) return;

    const container = document.createElement('div');
    container.id = 'stat-popover-container';
    container.className = 'stat-popover-hidden';
    container.setAttribute('role', 'dialog');
    container.setAttribute('aria-modal', 'false');
    container.setAttribute('aria-label', 'Statistical Explanation');

    container.innerHTML = `
      <div class="stat-popover-backdrop" onclick="window.hideStatPopover()"></div>
      <div class="stat-popover-card" onclick="event.stopPropagation()">
        <div class="stat-popover-header">
          <div class="stat-popover-title-row">
            <span class="stat-popover-icon">ⓘ</span>
            <h4 class="stat-popover-term" id="stat-popover-term-text">Term</h4>
            <span class="stat-popover-badge" id="stat-popover-category">Category</span>
          </div>
          <button class="stat-popover-close" onclick="window.hideStatPopover()" aria-label="Close">&times;</button>
        </div>
        <div class="stat-popover-body">
          <div class="stat-popover-def" id="stat-popover-def-text">Short definition</div>
          <div class="stat-popover-context-box">
            <span class="stat-popover-context-title">🔬 ${currentLang === 'sv' ? 'I denna översikt' : 'In this Review'}:</span>
            <p id="stat-popover-context-text">Contextual interpretation</p>
          </div>
        </div>
        <div class="stat-popover-footer">
          <button class="stat-popover-learn-btn" id="stat-popover-learn-more">
            📖 ${currentLang === 'sv' ? 'Öppna ordlista' : 'Explore in Glossary'}
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(container);

    // Global keyboard listener for Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        hideStatPopover();
      }
    });
  }

  function showStatPopover(termKey, triggerEl) {
    createPopoverElement();
    const glossary = window.STAT_GLOSSARY && (window.STAT_GLOSSARY[currentLang] || window.STAT_GLOSSARY['en']);
    if (!glossary || !glossary[termKey]) return;

    const entry = glossary[termKey];
    const container = document.getElementById('stat-popover-container');
    const card = container.querySelector('.stat-popover-card');
    const termEl = document.getElementById('stat-popover-term-text');
    const catEl = document.getElementById('stat-popover-category');
    const defEl = document.getElementById('stat-popover-def-text');
    const ctxEl = document.getElementById('stat-popover-context-text');
    const learnBtn = document.getElementById('stat-popover-learn-more');

    termEl.textContent = entry.term;
    catEl.textContent = entry.category || 'Statistics';
    defEl.textContent = entry.shortDef;
    ctxEl.textContent = entry.context;

    learnBtn.onclick = () => {
      hideStatPopover();
      if (typeof window.switchTab === 'function') {
        window.switchTab('glossary');
        setTimeout(() => {
          const targetCard = document.getElementById(`glossary-card-${termKey}`);
          if (targetCard) {
            targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            targetCard.classList.add('glossary-highlight');
            setTimeout(() => targetCard.classList.remove('glossary-highlight'), 2000);
          }
        }, 150);
      }
    };

    container.className = 'stat-popover-visible';
    activePopover = { termKey, triggerEl };

    if (triggerEl) {
      triggerEl.setAttribute('aria-expanded', 'true');
    }

    // Position card on desktop (on mobile viewport < 640px, CSS centers/bottom-sheets it)
    if (window.innerWidth >= 640 && triggerEl) {
      const rect = triggerEl.getBoundingClientRect();
      const cardWidth = Math.min(360, window.innerWidth - 30);
      card.style.position = 'absolute';
      card.style.width = `${cardWidth}px`;

      let left = rect.left + (rect.width / 2) - (cardWidth / 2);
      if (left < 15) left = 15;
      if (left + cardWidth > window.innerWidth - 15) left = window.innerWidth - cardWidth - 15;

      let top = rect.bottom + window.scrollY + 8;
      // If card overflows bottom of viewport, position above trigger
      if (rect.bottom + 260 > window.innerHeight && rect.top > 260) {
        top = rect.top + window.scrollY - 240;
      }

      card.style.left = `${left}px`;
      card.style.top = `${top}px`;
    } else {
      card.style.position = '';
      card.style.left = '';
      card.style.top = '';
      card.style.width = '';
    }
  }

  function hideStatPopover() {
    const container = document.getElementById('stat-popover-container');
    if (container) {
      container.className = 'stat-popover-hidden';
    }
    if (activePopover && activePopover.triggerEl) {
      activePopover.triggerEl.setAttribute('aria-expanded', 'false');
    }
    activePopover = null;
  }

  function toggleStatPopover(termKey, triggerEl) {
    if (activePopover && activePopover.termKey === termKey) {
      hideStatPopover();
    } else {
      showStatPopover(termKey, triggerEl);
    }
  }

  // ══════════════════════════════════════════════════════════════════
  // 4. ATTACH LISTENERS TO INTERACTIVE INFORMATION ICONS (ⓘ)
  // ══════════════════════════════════════════════════════════════════
  function initStatIcons() {
    createPopoverElement();

    document.querySelectorAll('.stat-info-btn, [data-stat-term]').forEach(btn => {
      const termKey = btn.getAttribute('data-stat-term');
      if (!termKey) return;

      // Prevent duplicate listeners
      if (btn.hasAttribute('data-stat-bound')) return;
      btn.setAttribute('data-stat-bound', 'true');
      btn.setAttribute('tabindex', '0');
      btn.setAttribute('role', 'button');
      btn.setAttribute('aria-haspopup', 'dialog');
      btn.setAttribute('aria-expanded', 'false');

      // Click / Tap (desktop + mobile)
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleStatPopover(termKey, btn);
      });

      // Desktop Hover
      btn.addEventListener('mouseenter', () => {
        if (window.innerWidth >= 640) {
          clearTimeout(hoverTimeout);
          hoverTimeout = setTimeout(() => {
            showStatPopover(termKey, btn);
          }, 200);
        }
      });

      btn.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimeout);
      });

      // Keyboard Focus
      btn.addEventListener('focus', () => {
        if (window.innerWidth >= 640) {
          showStatPopover(termKey, btn);
        }
      });

      btn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleStatPopover(termKey, btn);
        }
      });
    });
  }

  // ══════════════════════════════════════════════════════════════════
  // 5. STATISTICS GLOSSARY TAB RENDERER
  // ══════════════════════════════════════════════════════════════════
  function renderGlossaryTab() {
    const container = document.getElementById('tab-glossary');
    if (!container) return;

    const glossary = window.STAT_GLOSSARY && (window.STAT_GLOSSARY[currentLang] || window.STAT_GLOSSARY['en']);
    if (!glossary) return;

    const isSv = currentLang === 'sv';
    const titleText = isSv ? 'Metodologisk och statistisk ordlista' : 'Methodological & Statistical Concept Glossary';
    const subText = isSv 
      ? 'Kompakt förklaringsstöd skräddarsytt för kliniker och forskare som läser denna systematiska översikt över perioperativ TEAS och EA.'
      : 'Reader-assistance knowledgebase tailored for clinicians and researchers interpreting this systematic review of perioperative TEAS and EA.';
    const searchPh = isSv ? 'Sök begrepp (t.ex. konfidensintervall, REML, MD)...' : 'Search concept (e.g. confidence interval, REML, MD)...';
    const filterAll = isSv ? 'Alla kategorier' : 'All Categories';
    const jumpText = isSv ? 'Gå till analys' : 'Jump to Analysis';

    // Get unique categories
    const categories = Array.from(new Set(Object.values(glossary).map(g => g.category)));

    container.innerHTML = `
      <div class="dashboard-card" style="margin-bottom: 1.5rem; border-top: 3px solid #6366f1;">
        <div class="card-header" style="flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
              <span class="badge badge-indigo">Cochrane &amp; GRADE Methodology</span>
              <span class="badge badge-emerald">Bilingual Reader Support</span>
            </div>
            <h2>${titleText}</h2>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem; max-width: 900px; line-height: 1.55;">
              ${subText}
            </p>
          </div>

          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; width: 100%; max-width: 450px;">
            <input type="text" id="glossary-search-input" class="filter-select" placeholder="${searchPh}" style="flex: 1; padding: 0.55rem 0.85rem; font-size: 0.82rem; background: rgba(17, 24, 39, 0.9); border: 1px solid var(--border-subtle); color: #fff; border-radius: var(--radius-md);">
          </div>
        </div>

        <!-- Category Filters -->
        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
          <button class="btn-preset active" data-glossary-cat="all">${filterAll}</button>
          ${categories.map(cat => `<button class="btn-preset" data-glossary-cat="${cat}">${cat}</button>`).join('')}
        </div>

        <!-- Glossary Grid -->
        <div class="glossary-grid" id="glossary-cards-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem;">
          ${Object.entries(glossary).map(([key, item]) => `
            <div class="glossary-card" id="glossary-card-${key}" data-cat="${item.category}" style="background: rgba(17, 24, 39, 0.7); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.2s ease;">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
                  <h3 style="font-size: 1.05rem; color: #f8fafc; font-weight: 700;">${item.term}</h3>
                  <span class="badge badge-indigo" style="font-size: 0.65rem; white-space: nowrap;">${item.category}</span>
                </div>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.55; margin-bottom: 0.75rem;">
                  ${item.shortDef}
                </p>
                <div style="background: rgba(99, 102, 241, 0.05); border-left: 3px solid #818cf8; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.76rem; color: var(--text-secondary); line-height: 1.5;">
                  <strong style="color: #a5b4fc;">🔬 ${isSv ? 'I denna översikt' : 'In this Review'}:</strong> ${item.context}
                </div>
              </div>
              <div style="margin-top: 1rem; display: flex; justify-content: flex-end;">
                ${item.jumpTab ? `
                  <button class="btn-preset" onclick="window.switchTab('${item.jumpTab}')" style="font-size: 0.73rem; padding: 0.35rem 0.7rem; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #c7d2fe;">
                    ${jumpText} &rarr;
                  </button>
                ` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    // Filter handling
    const searchInput = document.getElementById('glossary-search-input');
    const catBtns = container.querySelectorAll('[data-glossary-cat]');
    let activeCat = 'all';

    function filterGlossary() {
      const q = (searchInput?.value || '').toLowerCase().trim();
      const cards = container.querySelectorAll('.glossary-card');

      cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const cat = card.getAttribute('data-cat');
        const matchesCat = activeCat === 'all' || cat === activeCat;
        const matchesQ = !q || text.includes(q);

        if (matchesCat && matchesQ) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', filterGlossary);
    }

    catBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        catBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCat = btn.getAttribute('data-glossary-cat');
        filterGlossary();
      });
    });
  }

  // ══════════════════════════════════════════════════════════════════
  // 6. EXPORT GLOBALS
  // ══════════════════════════════════════════════════════════════════
  window.t = t;
  window.setLanguage = setLanguage;
  window.getCurrentLanguage = () => currentLang;
  window.toggleExplainStatistics = toggleExplainStatistics;
  window.getExplainStatsState = () => explainStats;
  window.showStatPopover = showStatPopover;
  window.hideStatPopover = hideStatPopover;
  window.toggleStatPopover = toggleStatPopover;
  window.initStatIcons = initStatIcons;
  window.renderGlossaryTab = renderGlossaryTab;

  // Initialize on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    initFromStorage();
    initStatIcons();
    setLanguage(currentLang);
  });

})();
