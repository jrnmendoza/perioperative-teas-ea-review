// Regression checks for the findings-first usability layer.
//
// Scope: coordinated outcome selection, evidence links, URL restoration,
// Back/Forward behaviour and filter scope. These are usability assertions --
// they must never assert a scientific value, only that the value shown next to
// an analysis is the one belonging to that analysis.
//
// Run: node scripts/check_usability_ui.cjs
const {chromium} = require('playwright');
const assert = require('assert');
const path = require('path');

const SITE = 'file://' + path.resolve(__dirname, '..', '_site', 'index.html');

async function boot(browser, hash) {
  const page = await browser.newPage({viewport: {width: 1440, height: 900}});
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(SITE + (hash || ''));
  await page.waitForFunction(() => typeof window.switchTab === 'function');
  await page.waitForTimeout(500);
  return {page, errors};
}

(async () => {
  const browser = await chromium.launch();
  let checks = 0;

  // ── 1. Findings first ────────────────────────────────────────────────────
  {
    const {page, errors} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(400);

    const hero = await page.locator('#findings-hero').innerText();
    assert.ok(/reduce opioid use after surgery/i.test(hero), 'clinical question missing');
    // Compared case-insensitively: these labels are uppercased by CSS.
    for (const needed of ['Outcome', 'Timepoint', 'Unit', 'Model']) {
      assert.ok(hero.toLowerCase().includes(needed.toLowerCase()),
        `findings header missing ${needed}`);
    }
    // TEAS and EA appear as separate findings, each with k, N and a certainty.
    const cards = await page.locator('#findings-hero .finding-card').count();
    assert.ok(cards >= 3, `expected TEAS, EA and a supporting card; saw ${cards}`);
    for (const id of ['AN-01-TEAS', 'AN-01-EA']) {
      const t = await page.locator(`.finding-card[data-analysis-id="${id}"]`).innerText();
      assert.ok(/trials/.test(t) && /participants/.test(t), `${id} missing k or N`);
      assert.ok(/certainty/i.test(t), `${id} missing GRADE certainty`);
    }
    assert.equal(errors.length, 0, 'page errors: ' + errors.join('; '));
    checks += 4;
    await page.close();
  }

  // ── 2. GRADE is shown per synthesis, never inherited ─────────────────────
  {
    const {page} = await boot(browser);
    const shown = await page.evaluate(() => {
      const rows = [...document.querySelectorAll('#kpi-grade-body .kpi-grade-row')];
      return rows.map(r => ({
        id: r.getAttribute('data-analysis-id'),
        text: r.innerText.replace(/\s+/g, ' ').trim()
      }));
    });
    const saved = await page.evaluate(() => {
      const m = window.STATA_MASTER_RESULTS;
      return {teas: m['AN-01-TEAS'].grade, ea: m['AN-01-EA'].grade, comb: m['AN-01-COMB'].grade};
    });
    assert.equal(shown.length, 3, 'overview GRADE should list each synthesis separately');
    const byId = Object.fromEntries(shown.map(r => [r.id, r.text]));
    // Each row must carry ITS OWN adjudicated rating, in whichever language.
    const words = {'Low': ['Low', 'Låg'], 'Very Low': ['Very Low', 'Mycket låg']};
    assert.ok(words[saved.teas].some(w => byId['AN-01-TEAS'].includes(w)),
      `TEAS row should show ${saved.teas}: ${byId['AN-01-TEAS']}`);
    assert.ok(words[saved.ea].some(w => byId['AN-01-EA'].includes(w)),
      `EA row should show ${saved.ea}: ${byId['AN-01-EA']}`);
    // The whole point: the two modality ratings differ, so no single headline
    // rating may stand in for both.
    assert.notEqual(saved.teas, saved.ea,
      'this check exists because TEAS and EA certainty differ; update it if the adjudication changes');
    checks += 3;
    await page.close();
  }

  // ── 3. Evidence links carry context to the right destination ─────────────
  {
    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(300);

    // contributing studies -> explorer, filtered to that modality
    await page.click('.finding-card[data-analysis-id="AN-01-TEAS"] button[data-route="studies"]');
    await page.waitForTimeout(500);
    let st = await page.evaluate(() => ({
      tab: window.activeTab, modality: window.filterModality, hash: location.hash
    }));
    assert.equal(st.tab, 'explorer', 'studies link should open the Study Explorer');
    assert.equal(st.modality, 'TEAS', 'studies link should carry the modality');
    assert.ok(st.hash.includes('modality=TEAS'), 'modality missing from the URL');

    // risk of bias -> rob2, with the result-specific outcome selected
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(300);
    await page.click('.finding-card[data-analysis-id="AN-01-TEAS"] button[data-route="rob"]');
    await page.waitForTimeout(500);
    st = await page.evaluate(() => ({
      tab: window.activeTab,
      rob: document.getElementById('rob2-outcome-filter').value
    }));
    assert.equal(st.tab, 'rob2');
    assert.equal(st.rob, 'opioid_24h',
      'RoB link must select the result-specific outcome, not a study-level summary');

    // GRADE -> evidence tab, highlighting that analysis only
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(300);
    await page.click('.finding-card[data-analysis-id="AN-01-EA"] button[data-route="grade"]');
    await page.waitForTimeout(500);
    st = await page.evaluate(() => ({
      tab: window.activeTab,
      focus: window.focusAnalysisId,
      highlighted: [...document.querySelectorAll('.evidence-focus')].map(e => e.getAttribute('data-analysis-id'))
    }));
    assert.equal(st.tab, 'evidence');
    assert.equal(st.focus, 'AN-01-EA');
    assert.deepEqual(st.highlighted, ['AN-01-EA'],
      'exactly the requested analysis should be highlighted');

    // every card offers a download
    const dl = await page.evaluate(() => {
      const a = document.querySelector('.finding-card[data-analysis-id="AN-01-TEAS"] a.evidence-link');
      return a ? a.getAttribute('href') : null;
    });
    assert.ok(dl && /\.csv$/.test(dl), 'each analysis needs a download link');
    checks += 8;
    await page.close();
  }

  // ── 4. URL restoration on a fresh load ───────────────────────────────────
  {
    const {page} = await boot(browser, '#tab=rob2&rob=flatus_time&analysis=AN-07-TARGET-E');
    await page.waitForTimeout(900);
    const st = await page.evaluate(() => ({
      tab: window.activeTab,
      rob: document.getElementById('rob2-outcome-filter').value,
      focus: window.focusAnalysisId,
      hash: location.hash
    }));
    assert.equal(st.tab, 'rob2', 'a shared link must open its tab');
    assert.equal(st.rob, 'flatus_time', 'a shared link must restore its outcome selection');
    assert.equal(st.focus, 'AN-07-TARGET-E', 'a shared link must restore its analysis focus');
    assert.ok(st.hash.includes('flatus_time'), 'the URL must survive the restore');
    checks += 4;
    await page.close();
  }

  // ── 5. Back / Forward ────────────────────────────────────────────────────
  {
    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(300);
    await page.click('.finding-card[data-analysis-id="AN-01-EA"] button[data-route="grade"]');
    await page.waitForTimeout(400);
    assert.equal(await page.evaluate(() => window.activeTab), 'evidence');

    await page.goBack();
    await page.waitForTimeout(500);
    assert.equal(await page.evaluate(() => window.activeTab), 'primary', 'Back should return to the findings');

    await page.goForward();
    await page.waitForTimeout(500);
    assert.equal(await page.evaluate(() => window.activeTab), 'evidence', 'Forward should return to GRADE');
    checks += 3;
    await page.close();
  }

  // ── 6. Filter scope is visible, resettable, and never edits an estimate ──
  {
    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('explorer'));
    await page.waitForTimeout(300);

    const savedBefore = await page.evaluate(() => window.STATA_MASTER_RESULTS['AN-01-TEAS'].mdText);
    const allRows = await page.locator('#explorer-table-body tr').count();

    await page.selectOption('#filter-modality', 'TEAS');
    await page.waitForTimeout(400);
    const chips = await page.locator('#filter-chips').innerText();
    assert.ok(/TEAS/.test(chips), 'an active filter must be visible as a chip');
    const filteredRows = await page.locator('#explorer-table-body tr').count();
    assert.ok(filteredRows < allRows, 'the filter should actually narrow the study list');

    const savedAfter = await page.evaluate(() => window.STATA_MASTER_RESULTS['AN-01-TEAS'].mdText);
    assert.equal(savedAfter, savedBefore, 'a study filter must never change a saved estimate');

    await page.click('#filter-reset-all');
    await page.waitForTimeout(400);
    const resetRows = await page.locator('#explorer-table-body tr').count();
    assert.equal(resetRows, allRows, 'Reset filters must restore the full study list');
    assert.ok(await page.locator('#filter-chips').isHidden(), 'chips should disappear once no filter is active');
    checks += 5;
    await page.close();
  }

  // ── 7. Section menu jumps into collapsed sections ────────────────────────
  {
    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(400);
    const links = await page.locator('#section-menu .section-menu-link').count();
    assert.ok(links >= 8, `long pages need a section menu; saw ${links} entries`);
    await page.locator('#section-menu .section-menu-link', {hasText: 'Derivations'}).first().click();
    await page.waitForTimeout(500);
    const opened = await page.evaluate(() => {
      const el = document.querySelector('[data-section="Derivations"]');
      return el && el.tagName === 'DETAILS' ? el.open : !!el?.closest('details')?.open;
    });
    assert.ok(opened, 'jumping to a collapsed section should open it');
    checks += 2;
    await page.close();
  }

  // ── 8. Coordinated outcome selection on Secondary Outcomes ───────────────
  {
    const {page} = await boot(browser, '#tab=secondary');
    await page.waitForTimeout(900);

    // A saved analysis with a genuine exploratory counterpart syncs the plot.
    await page.selectOption('#stata-secondary-select', 'V33_RESCUE_OPIOID_RR_24H');
    await page.waitForTimeout(500);
    let st = await page.evaluate(() => ({
      exploratory: document.getElementById('meta-outcome-select').value,
      banner: document.getElementById('exploratory-coordination')?.className || ''
    }));
    assert.equal(st.exploratory, 'rescue_analgesia',
      'a saved rescue-opioid analysis should not sit above a primary-opioid plot');
    assert.ok(st.banner.includes('coordination-matched'), 'matched state not shown');

    // A saved analysis with no counterpart must say so explicitly rather than
    // leaving an unrelated plot underneath it.
    for (const id of ['V33_QOR40_24H_MD', 'V33_GI_DEFECATION_MD', 'V33_INTRAOP_SUF_MD']) {
      await page.selectOption('#stata-secondary-select', id);
      await page.waitForTimeout(400);
      st = await page.evaluate(() => {
        const b = document.getElementById('exploratory-coordination');
        return {cls: b?.className || '', text: b?.innerText || ''};
      });
      assert.ok(st.cls.includes('coordination-unavailable'),
        `${id} has no exploratory counterpart and must show an unavailable state`);
      assert.ok(/does not correspond|different outcome|different drug/i.test(st.text),
        `${id} unavailable state must explain the difference`);
    }

    // Saved and exploratory must be labelled differently.
    const labels = await page.locator('#tab-secondary').innerText();
    assert.ok(/exploratory/i.test(labels), 'exploratory calculations must be labelled as such');
    checks += 6;
    await page.close();
  }

  // ── 9. The findings card works in Swedish too ────────────────────────────
  // The main reader journey must be complete in both languages. Untranslated
  // fragments here were how the earlier "N trials / N participants / certainty"
  // gap was found: they sat inside a text node with a number, which the exact
  // dictionary can never match.
  {
    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(400);
    await page.click('.btn-lang[data-lang="sv"]');
    await page.waitForTimeout(900);

    const card = await page.locator('.finding-card[data-analysis-id="AN-01-TEAS"]').innerText();
    for (const sv of ['studier', 'deltagare', 'tillförlitlighet']) {
      assert.ok(card.includes(sv), `Swedish findings card missing "${sv}": ${card}`);
    }
    for (const en of ['trials', 'participants', 'certainty']) {
      assert.ok(!new RegExp('\\b' + en + '\\b').test(card),
        `English "${en}" still visible in the Swedish findings card`);
    }
    const links = await page.locator('.finding-card[data-analysis-id="AN-01-TEAS"] .evidence-link').allInnerTexts();
    assert.ok(links.some(t => /Ladda ner/i.test(t)), 'download link not translated');
    assert.ok(links.some(t => /Risk för bias/i.test(t)), 'RoB link not translated');

    // Saved estimates must be identical in both languages.
    const svEffect = await page.locator('.finding-card[data-analysis-id="AN-01-TEAS"] .finding-effect').innerText();
    await page.click('.btn-lang[data-lang="en"]');
    await page.waitForTimeout(700);
    const enEffect = await page.locator('.finding-card[data-analysis-id="AN-01-TEAS"] .finding-effect').innerText();
    assert.equal(svEffect, enEffect, 'the saved estimate must not change with the interface language');
    checks += 4;
    await page.close();
  }

  // ── 10. No horizontal page overflow at any supported width ───────────────
  // The page must never scroll sideways. Content that genuinely exceeds its box
  // scrolls inside that box; it never moves the document. Checked on every tab,
  // and on the primary tab with every collapsible section expanded, because a
  // single collapsed section can hide a wide table.
  {
    const WIDTHS = [320, 375, 768, 1024, 1440];
    const TABS = ['intro', 'explorer', 'prisma', 'primary', 'secondary', 'mcid', 'metareg',
                  'evidence', 'rob2', 'limitations', 'search', 'extraction', 'glossary', 'export'];
    for (const width of WIDTHS) {
      const page = await browser.newPage({viewport: {width, height: 900}});
      await page.goto(SITE);
      await page.waitForFunction(() => typeof window.switchTab === 'function');
      await page.waitForTimeout(500);
      for (const tab of TABS) {
        await page.evaluate(t => switchTab(t), tab);
        await page.waitForTimeout(160);
        const over = await page.evaluate(() => {
          const d = document.documentElement;
          return d.scrollWidth - d.clientWidth;
        });
        assert.ok(over <= 1, `horizontal overflow of ${over}px on "${tab}" at ${width}px`);
      }
      await page.evaluate(() => {
        switchTab('primary');
        document.querySelectorAll('#tab-primary details').forEach(d => (d.open = true));
      });
      await page.waitForTimeout(450);
      const expanded = await page.evaluate(() => {
        const d = document.documentElement;
        return d.scrollWidth - d.clientWidth;
      });
      assert.ok(expanded <= 1,
        `horizontal overflow of ${expanded}px on primary with all sections expanded at ${width}px`);
      await page.close();
      checks += 1;
    }
  }

  // ── 11. Containment must not clip content ────────────────────────────────
  // Making things fit is only correct if nothing becomes unreachable. Any box
  // that hides its own overflow must not be hiding content -- except where an
  // ellipsis marks a deliberate truncation.
  {
    const page = await browser.newPage({viewport: {width: 375, height: 812}});
    await page.goto(SITE);
    await page.waitForFunction(() => typeof window.switchTab === 'function');
    await page.waitForTimeout(500);
    for (const tab of ['primary', 'rob2', 'secondary', 'limitations', 'extraction']) {
      await page.evaluate(t => switchTab(t), tab);
      await page.waitForTimeout(200);
      const bad = await page.evaluate(() => [...document.querySelectorAll('.tab-content.active *')]
        .filter(e => {
          const cs = getComputedStyle(e);
          if (cs.textOverflow === 'ellipsis') return false;
          return cs.overflowX === 'hidden' && e.scrollWidth > e.clientWidth + 2;
        })
        .map(e => e.tagName + '.' + String(e.className || '').split(' ')[0]));
      assert.deepEqual(bad, [], `content clipped without a scrollbar on "${tab}": ${bad.join(', ')}`);
    }
    // And the visible text must be the same at narrow and wide widths.
    const narrow = await page.evaluate(() => {
      switchTab('primary');
      return document.querySelector('.tab-content.active').innerText.replace(/\s+/g, ' ').trim().length;
    });
    await page.setViewportSize({width: 1440, height: 900});
    await page.waitForTimeout(400);
    const wide = await page.evaluate(() =>
      document.querySelector('.tab-content.active').innerText.replace(/\s+/g, ' ').trim().length);
    assert.equal(narrow, wide, 'narrow and wide viewports must show the same content');
    checks += 2;
    await page.close();
  }

  // ── 12. v34 analysis set ─────────────────────────────────────────────────
  // The dashboard must show the v34 models, each stratified, and must not
  // present a withdrawn or superseded model as current evidence.
  {
    const fs = require('fs');
    const path2 = require('path');
    const root = path2.resolve(__dirname, '..');
    const stata = fs.readFileSync(
      path2.join(root, '09_V34_ANALYSIS/03_RESULTS/v34_models.csv'), 'utf8')
      .trim().split('\n');
    const head = stata[0].split(',');
    const byId = {};
    for (const line of stata.slice(1)) {
      const c = line.split(',');
      const row = Object.fromEntries(head.map((h, i) => [h, c[i]]));
      byId[row.model_id] = row;
    }

    const {page} = await boot(browser);
    await page.evaluate(() => switchTab('primary'));
    await page.waitForTimeout(600);

    const shown = await page.evaluate(() => {
      const V = window.V34_DATA;
      return {
        master: V.master, studies: V.canonical_studies, rows: V.outcome_rows,
        k: V.strict_primary_k,
        models: V.models.map(m => ({id: m.model_id, k: m.k, est: m.estimate,
                                    lo: m.ci_low, hi: m.ci_high, label: m.label})),
        withdrawn: V.withdrawn.map(w => w.analysis_id),
        rendered: document.querySelectorAll('#v34-models tbody tr').length,
      };
    });

    assert.ok(/v34/.test(shown.master), `dashboard should read the v34 master: ${shown.master}`);
    assert.equal(shown.studies, 70, 'canonical study count must stay 70');
    assert.equal(shown.rows, 757, 'v34 outcome-row count must be 757');
    assert.equal(shown.k, 7, 'strict primary k must stay 7');
    assert.ok(shown.rendered >= 13, `expected the v34 models to render; saw ${shown.rendered}`);

    // Every displayed estimate must equal the Stata value it claims to be.
    for (const m of shown.models) {
      const src = byId[m.id];
      assert.ok(src, `${m.id} is displayed but absent from the Stata results`);
      assert.equal(Number(m.k), Number(src.k), `${m.id}: k mismatch`);
      for (const [disp, col] of [[m.est, 'estimate'], [m.lo, 'ci_low'], [m.hi, 'ci_high']]) {
        assert.ok(Math.abs(Number(disp) - Number(src[col])) < 5e-4,
          `${m.id}.${col}: dashboard ${disp} != Stata ${src[col]}`);
      }
      // Every model names its stratum. The one permitted cross-stratum model is
      // the historical combined audit synthesis, which the protocol keeps
      // separate from the strata and which must say so in its own label.
      const isCombinedAudit = /combined audit/i.test(m.label);
      if (isCombinedAudit) {
        assert.ok(/ALL_AUDIT/.test(m.id),
          `only the combined audit may be cross-stratum: ${m.label}`);
      } else {
        assert.ok(/TEAS|EA/.test(m.label) && /sham|usual care/i.test(m.label),
          `${m.id} label must name one modality and one comparator: ${m.label}`);
      }
    }

    // The withdrawn mixed-window rescue model must not appear as a live result.
    assert.ok(shown.withdrawn.includes('V33_RESCUE_OPIOID_RR_24H'),
      'the mixed-window rescue model must be registered as withdrawn');
    const retired = await page.evaluate(() => {
      const rows = [...document.querySelectorAll('.v33-retired')];
      return {
        count: rows.length,
        allStruck: rows.every(r => r.querySelector('s')),
        anyUnlabelled: rows.some(r => !r.querySelector('.v34-badge')),
      };
    });
    assert.ok(retired.count >= 6, 'retired v33 secondary rows should still be listed');
    assert.ok(retired.allStruck, 'retired rows must be struck through, not shown as current');
    assert.ok(!retired.anyUnlabelled, 'every retired row needs a withdrawn/superseded badge');

    // No GRADE certainty may be attached to a v34 model.
    const certainty = await page.evaluate(() =>
      [...document.querySelectorAll('#v34-models tbody tr td:last-child')]
        .map(td => td.innerText.trim().toLowerCase()));
    assert.ok(certainty.length && certainty.every(c => /pending|pågår/.test(c)),
      `v34 models must show certainty as pending, saw ${JSON.stringify(certainty.slice(0, 3))}`);

    checks += 8;
    await page.close();
  }

  await browser.close();
  console.log(`PASS: ${checks} usability regression checks — findings first, per-synthesis GRADE, ` +
    `evidence links with context, URL restore, Back/Forward, filter scope, section menu, ` +
    `coordinated outcome selection, bilingual findings, no overflow at 320-1440px, ` +
    `v34 model integrity.`);
})().catch(e => { console.error(e); process.exit(1); });
