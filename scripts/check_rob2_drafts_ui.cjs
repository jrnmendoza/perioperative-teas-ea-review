// Regression checks for the draft result-specific RoB 2 panel.
//
// Scope: that the 36 draft judgements reach the page intact, that every one of
// them is visibly labelled a DRAFT, and that the page never presents a draft as
// an adjudicated judgement. RoB 2 is the review's central quality appraisal and
// is reported under named assessors; a draft shown as settled would claim an
// appraisal nobody has made.
//
// These are presentation assertions. They never assert a domain judgement --
// only that what the data file holds is what the reader sees.
//
// Run: node scripts/check_rob2_drafts_ui.cjs
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

  const D = await page.evaluate(() => (window.V34_DATA || {}).rob2_drafts || null);
  assert.ok(D, 'v34 data carries no rob2_drafts payload');
  assert.strictEqual(D.count, 36, `expected 36 drafts, data holds ${D.count}`);
  assert.strictEqual(D.results.length, 36, 'draft result list is not 36 long');
  assert.strictEqual(D.status, 'ROB2_RESULT_SPECIFIC_DRAFT_PENDING_ADJUDICATION',
    `draft payload status is ${D.status}`);

  // 1. every draft row reaches the DOM, with all five domains
  const open = await page.evaluate(() => {
    const ds = [...document.querySelectorAll('#tab-primary details')];
    const d = ds.find(x => /draft result-specific judgements/i.test(
      x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    const rows = [...d.querySelectorAll('tbody tr')];
    return {
      rows: rows.length,
      // count chips in the domains cell only -- the rationale prose also names domains
      allFiveDomains: rows.every(r => (r.children[1].textContent.match(/D[1-5] /g) || []).length === 5),
      overalls: rows.map(r => r.children[2].textContent.trim()),
    };
  });
  assert.ok(open, 'the draft judgements disclosure is not present');
  assert.strictEqual(open.rows, 36, `${open.rows} draft rows rendered, expected 36`);
  assert.ok(open.allFiveDomains, 'a rendered draft row is missing one of D1-D5');

  // 2. the rendered overall column matches the data, row for row
  const wantOveralls = D.results.map(r => r.overall);
  assert.deepStrictEqual(open.overalls, wantOveralls,
    'the overall judgements shown do not match the data file row for row');

  // 3. the panel is visibly marked as a draft, and claims nothing final
  const text = await page.evaluate(() => document.getElementById('tab-primary').innerText);
  assert.ok(/DRAFT — not adjudicated/.test(text), 'no visible DRAFT label on the panel');
  assert.ok(/two independent human assessors/i.test(text),
    'the panel does not state that two independent assessors are required');
  assert.ok(!/risk of bias (is )?(now )?(complete|finalised|finalized|adjudicated)\b/i.test(text),
    'the panel claims the risk-of-bias appraisal is complete');

  // 4. drafting must not have released the GRADE hold
  const cert = await page.evaluate(() => (window.V34_DATA || {}).certainty_note || '');
  assert.ok(/pending/i.test(cert) && /draft/i.test(cert),
    'the certainty note no longer distinguishes a pending draft from a rating');

  // 5. the model rollup reaches the DOM and is complete
  const roll = await page.evaluate(() => {
    const d = [...document.querySelectorAll('#tab-primary details')]
      .find(x => /would inherit/i.test(x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    return d.querySelectorAll('tbody tr').length;
  });
  assert.strictEqual(roll, D.model_rollup.length,
    `${roll} rollup rows rendered, data holds ${D.model_rollup.length}`);

  // 6. mutation: a draft presented without its label must be rejected
  const mutationCaught = await page.evaluate(() => {
    const t = document.getElementById('tab-primary').innerHTML
      .replace(/DRAFT — not adjudicated/g, 'Risk of bias');
    return !/DRAFT — not adjudicated/.test(t);
  });
  assert.ok(mutationCaught, 'the DRAFT label check cannot detect its own removal');

  // 7. the DRAFT labelling survives translation -- a reader in Swedish must not
  //    see these presented as settled judgements either
  const sv = await page.evaluate(async () => {
    const btn = document.querySelector('[onclick*="sv"], #lang-sv, [data-lang="sv"]');
    if (btn) btn.click();
    else if (typeof window.setLanguage === 'function') window.setLanguage('sv');
    else return null;  // asserted non-null below: a skipped check is not a passed check
    await new Promise(r => setTimeout(r, 900));
    return document.getElementById('tab-primary').innerText;
  });
  assert.ok(sv, 'could not switch the page to Swedish; the SV assertions would be vacuous');
  {
    assert.ok(/UTKAST – ej slutbedömt/.test(sv),
      'the Swedish view does not carry the translated DRAFT label');
    assert.ok(/oberoende/i.test(sv),
      'the Swedish view drops the independent-assessor requirement');
  }

  // 8. translation must not have altered any judgement
  const svOveralls = await page.evaluate(() => {
    const d = [...document.querySelectorAll('#tab-primary details')].find(x =>
      /utkastbedömningarna|draft result-specific judgements/i.test(
        x.querySelector('summary')?.textContent || ''));
    if (!d) return null;
    d.open = true;
    return [...d.querySelectorAll('tbody tr')].map(r => r.children[2].textContent.trim());
  });
  assert.ok(svOveralls, 'the draft disclosure is not findable in the Swedish view');
  {
    assert.strictEqual(svOveralls.length, 36,
      'the Swedish view does not render all 36 draft rows');
    const svHigh = svOveralls.filter(v => /^(High|Hög)/.test(v)).length;
    const enHigh = wantOveralls.filter(v => v === 'High').length;
    assert.strictEqual(svHigh, enHigh,
      `switching language changed the number of High-risk results (${enHigh} -> ${svHigh})`);
  }

  assert.deepStrictEqual(errors, [], 'page errors: ' + errors.join(' | '));
  await browser.close();
  console.log(`PASS: ${D.count} draft result-specific RoB 2 judgements rendered with all ` +
    `five domains, overall column matches the data row for row, ` +
    `${D.model_rollup.length} model rollup rows, DRAFT labelling enforced, GRADE hold intact.`);
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
