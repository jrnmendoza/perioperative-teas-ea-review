// Run with the bundled Playwright dependency; serve the built site on port 8765.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({headless:true, channel:process.env.BROWSER_CHANNEL || 'chrome'});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(process.env.DASHBOARD_URL || 'http://127.0.0.1:8765', {waitUntil:'networkidle'});
  const tabs = await page.locator('.tab-content').evaluateAll(els => els.map(e => e.id.replace('tab-', '')));
  for (const tab of tabs) {
    await page.evaluate(tab => switchTab(tab), tab);
    assert.ok((await page.locator(`#tab-${tab}`).innerText()).trim(), `${tab} empty`);
  }
  await page.evaluate(() => switchTab('limitations'));
  assert.equal(await page.locator('#inquiries-table-body tr').count(), await page.evaluate(() => window.AUTHOR_INQUIRIES.length));
  await page.locator('#btn-priority-critical').click();
  assert.equal(await page.locator('#inquiries-table-body tr').count(), await page.evaluate(() => window.AUTHOR_INQUIRIES.filter(x => x.priority === 'CRITICAL').length));
  await page.locator('#btn-priority-all').click();
  await page.locator('#inquiry-search-input').fill('yao');
  assert.ok((await page.locator('#inquiries-table-body').innerText()).includes('Yao'));
  await page.locator('#inquiry-search-input').fill('');
  await page.evaluate(() => switchTab('search'));
  assert.equal(await page.locator('#search-db-buttons button').count(), 4);
  for (const source of await page.evaluate(() => window.SEARCH_STRATEGIES)) {
    await page.locator(`[data-search-db="${source.id}"]`).click();
    assert.equal(await page.locator('#search-strategy-code-display').innerText(), source.strategy_text);
    assert.equal(source.strategy_text, fs.readFileSync(source.source, 'utf8'));
  }
  await page.evaluate(() => switchTab('primary'));
  for (const id of ['v33-subtitle','v33-headline','v33-map','v33-results','v33-notpooled','pathway-subtitle','pathway-headline','pathway-flow','pathway-panels','pathway-comparison','pathway-estimand','pathway-whatcouldchange','pathway-maturity','pathway-table-body','t33-subtitle','t33-flow','t33-sets','t33-empty','t33-figures']) {
    assert.ok((await page.locator(`#${id}`).textContent()).trim(), `${id} empty`);
  }
  const order = await page.evaluate(() => ['v33-map','pathway-flow','t33-flow'].map(id => document.getElementById(id).getBoundingClientRect().top));
  assert.ok(order[0] < order[1] && order[1] < order[2]);
  await page.screenshot({path:'tmp/handover/primary.png',fullPage:false});
  await page.evaluate(() => switchTab('secondary'));
  for (const id of await page.locator('#stata-secondary-select option').evaluateAll(els => els.map(e => e.value))) {
    await page.selectOption('#stata-secondary-select', id);
    assert.ok((await page.locator('#stata-secondary-result').innerText()).includes('No GRADE rating'));
    for (const img of await page.locator('#stata-secondary-result img').all()) {
      await img.evaluate(el => el.decode());
      assert.ok(await img.evaluate(el => el.naturalWidth > 0));
    }
  }
  const options = await page.locator('#meta-outcome-select option').evaluateAll(els => els.map(e => e.value).sort());
  assert.deepEqual(options, await page.evaluate(() => window.META_OUTCOMES.slice().sort()));
  await page.screenshot({path:'tmp/handover/secondary.png',fullPage:false});
  assert.deepEqual(errors, []);
  console.log(`PASS: ${tabs.length} tabs, populated renderer targets, reference filters, four verbatim strategies, six Stata analyses, loaded plots and generated interactive options.`);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
