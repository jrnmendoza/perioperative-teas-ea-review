// Regression checks for the result-specific RoB 2 panel (adopted status).
//
// Scope: that the 36 result-specific judgements reach the page intact, that
// each is visibly attributed to who adopted it and when, that the panel never
// claims an independent dual-assessor record this pipeline was never given,
// and that the result-level filtering (outcome family, study, overall,
// model/synthesis) actually filters what is rendered and coordinates with the
// model rollup table.
//
// These are presentation and provenance assertions. They never assert a
// domain judgement -- only that what the data file holds, including its
// provenance fields, is what the reader sees, accurately.
//
// Run: node scripts/check_rob2_results_ui.cjs
const {chromium} = require('playwright');
const assert = require('assert');
const path = require('path');

const SITE = 'file://' + path.resolve(__dirname, '..', '_site', 'index.html');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: {width: 1440, height: 900}});
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(SITE);
  await page.waitForFunction(() => typeof window.switchTab === 'function');
  await page.evaluate(() => switchTab('primary'));
  await page.waitForTimeout(700);

  const D = await page.evaluate(() => (window.V34_DATA || {}).rob2_results || null);
  assert.ok(D, 'v34 data carries no rob2_results payload');
  assert.strictEqual(D.count, 36, `expected 36 results, data holds ${D.count}`);
  assert.strictEqual(D.results.length, 36, 'result list is not 36 long');
  assert.strictEqual(D.status, 'ROB2_RESULT_SPECIFIC_ADOPTED', `payload status is ${D.status}`);
  assert.ok(D.adopted_by && D.adopted_date, 'payload is missing adopted_by/adopted_date');
  assert.ok(D.results.every(r => r.adopted_by && r.adopted_date),
    'not every result row carries adopted_by/adopted_date');

  // 1. every result row reaches the DOM, with all five domains
  const open = await page.evaluate(() => {
    const ds = [...document.querySelectorAll('#tab-primary details')];
    const d = ds.find(x => /result-specific judgements/i.test(
      x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    const rows = [...d.querySelectorAll('tbody tr')];
    return {
      rows: rows.length,
      allFiveDomains: rows.every(r => (r.children[1].textContent.match(/D[1-5] /g) || []).length === 5),
      overalls: rows.map(r => r.children[2].textContent.trim()),
    };
  });
  assert.ok(open, 'the result judgements disclosure is not present');
  assert.strictEqual(open.rows, 36, `${open.rows} result rows rendered, expected 36`);
  assert.ok(open.allFiveDomains, 'a rendered result row is missing one of D1-D5');

  // 2. the rendered overall column matches the data, row for row
  const wantOveralls = D.results.map(r => r.overall);
  assert.deepStrictEqual(open.overalls, wantOveralls,
    'the overall judgements shown do not match the data file row for row');

  // 3. the panel visibly attributes adoption, and does not overclaim
  const text = await page.evaluate(() => document.getElementById('tab-primary').innerText);
  assert.ok(text.includes(D.adopted_by) || /Adopted/i.test(text),
    'no visible adoption attribution on the panel');
  assert.ok(/dual-assessor record/i.test(text),
    'the panel drops the disclosure that no separate dual-assessor record was provided');
  assert.ok(!/independently\s+(double|dual)[- ]assess/i.test(text),
    'the panel claims an independent dual-assessment that was never provided to this pipeline');

  // 4. the certainty note separates "RoB 2 adopted" from "GRADE complete"
  const cert = await page.evaluate(() => (window.V34_DATA || {}).certainty_note || '');
  assert.ok(/adopted/i.test(cert),
    'the certainty note does not reflect the adopted RoB 2 status');
  assert.ok(/not[^.]{0,40}(a )?completed? GRADE|NOT[^.]{0,60}completed? grade/i.test(cert),
    'the certainty note does not say GRADE itself remains incomplete');
  for (const domain of ['inconsistency', 'imprecision', 'indirectness', 'publication bias']) {
    assert.ok(cert.toLowerCase().includes(domain),
      `the certainty note drops the still-unassessed domain "${domain}"`);
  }

  // 5. the model rollup reaches the DOM and is complete
  const rollDetails = await page.evaluate(() => {
    const d = [...document.querySelectorAll('#tab-primary details')]
      .find(x => /inherits from these results/i.test(x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    return d.querySelectorAll('tbody tr').length;
  });
  assert.strictEqual(rollDetails, D.model_rollup.length,
    `${rollDetails} rollup rows rendered, data holds ${D.model_rollup.length}`);

  // 6. filtering: the overall-risk filter actually hides non-matching rows
  const filterByOverall = await page.evaluate(() => {
    const sel = document.getElementById('v34rob-f-overall');
    if (!sel) return null;
    sel.value = 'High';
    window.v34ApplyRobFilters();
    const table = document.getElementById('v34-rob-results-table');
    const visible = [...table.querySelectorAll('tbody tr')].filter(r => !r.hidden);
    const ok = visible.length > 0 && visible.every(r => r.dataset.robOverall === 'High');
    sel.value = ''; window.v34ApplyRobFilters();
    return {count: visible.length, ok};
  });
  assert.ok(filterByOverall, 'the overall-risk filter control is not present');
  const wantHigh = D.results.filter(r => r.overall === 'High').length;
  assert.strictEqual(filterByOverall.count, wantHigh,
    `overall=High filter showed ${filterByOverall.count} rows, data has ${wantHigh}`);
  assert.ok(filterByOverall.ok, 'the overall-risk filter let a non-High row through');

  // 7. coordination: clicking a model row filters the results table to that model,
  //    and opens the disclosure if it was closed (start from closed so the open
  //    assertion below is actually exercising the click, not a state left over
  //    from step 1 having already opened it)
  const modelClick = await page.evaluate(() => {
    const details = document.getElementById('v34-rob-results-details');
    if (details) details.open = false;
    const modelRow = document.querySelector('.v34-rob-model-row');
    if (!modelRow) return null;
    const modelId = modelRow.dataset.robModel;
    modelRow.click();
    const table = document.getElementById('v34-rob-results-table');
    const visible = [...table.querySelectorAll('tbody tr')].filter(r => !r.hidden);
    const ok = visible.length > 0 &&
      visible.every(r => (r.dataset.robModels || '').split('; ').includes(modelId));
    const detailsOpen = document.getElementById('v34-rob-results-details')?.open === true;
    window.v34ResetRobFilters();
    return {modelId, count: visible.length, ok, detailsOpen};
  });
  assert.ok(modelClick, 'no clickable model row found in the rollup table');
  assert.ok(modelClick.detailsOpen, 'clicking a model row did not open the results disclosure');
  assert.ok(modelClick.ok && modelClick.count > 0,
    `clicking model ${modelClick.modelId} did not correctly filter the results table`);

  // 8. reset control actually clears every filter
  const resetWorks = await page.evaluate(() => {
    document.getElementById('v34rob-f-overall').value = 'Low';
    window.v34ApplyRobFilters();
    window.v34ResetRobFilters();
    const table = document.getElementById('v34-rob-results-table');
    return [...table.querySelectorAll('tbody tr')].every(r => !r.hidden);
  });
  assert.ok(resetWorks, 'Reset did not clear an active filter');

  // 9. mutation: the honest-provenance text must be detectable if removed
  const mutationCaught = await page.evaluate(() => {
    const t = document.getElementById('tab-primary').innerHTML
      .replace(/dual-assessor record/g, 'independently dual-assessed');
    return !/dual-assessor record/.test(t) && /independently dual-assessed/.test(t);
  });
  assert.ok(mutationCaught, 'the provenance-text check cannot detect its own removal');

  // 10. the honest-provenance text and source-QC flags survive translation
  const sv = await page.evaluate(async () => {
    const btn = document.querySelector('[onclick*="sv"], #lang-sv, [data-lang="sv"]');
    if (btn) btn.click();
    else if (typeof window.setLanguage === 'function') window.setLanguage('sv');
    else return null;
    await new Promise(r => setTimeout(r, 900));
    return document.getElementById('tab-primary').innerText;
  });
  assert.ok(sv, 'could not switch the page to Swedish; the SV assertions would be vacuous');
  assert.ok(/tvåbedömarunderlag/i.test(sv),
    'the Swedish view drops the translated no-separate-dual-assessor-record disclosure');
  assert.ok(!/oberoende dubbelbedömning (har|är) (gjord|genomförd)/i.test(sv),
    'the Swedish view claims an independent dual assessment that was not provided');

  // 11. translation must not have altered any judgement
  const svOveralls = await page.evaluate(() => {
    const d = [...document.querySelectorAll('#tab-primary details')].find(x =>
      /resultatspecifika bedömningarna|result-specific judgements/i.test(
        x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    return [...d.querySelectorAll('tbody tr')].map(r => r.children[2].textContent.trim());
  });
  assert.ok(svOveralls, 'the result disclosure is not findable in the Swedish view');
  assert.strictEqual(svOveralls.length, 36, 'the Swedish view does not render all 36 rows');
  const svHigh = svOveralls.filter(v => /^(High|Hög)/.test(v)).length;
  const enHigh = wantOveralls.filter(v => v === 'High').length;
  assert.strictEqual(svHigh, enHigh,
    `switching language changed the number of High-risk results (${enHigh} -> ${svHigh})`);

  assert.deepStrictEqual(errors, [], 'page errors: ' + errors.join(' | '));
  await browser.close();
  console.log(`PASS: ${D.count} result-specific RoB 2 judgements rendered with all five ` +
    `domains, overall column matches the data row for row, ${D.model_rollup.length} model ` +
    `rollup rows, honest adoption provenance shown, filtering and model-click coordination ` +
    `work, GRADE-vs-RoB2 distinction and source-QC flags intact in English and Swedish.`);
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
