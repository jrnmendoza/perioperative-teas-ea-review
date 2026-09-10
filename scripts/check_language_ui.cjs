const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=process.env.DASHBOARD_URL || 'http://127.0.0.1:8765';
 await page.goto(url,{waitUntil:'networkidle'});
 await page.evaluate(()=>setLanguage('en'));
 const source=await page.evaluate(()=>JSON.stringify(STUDIES_DATA));
 const downloads=await page.locator('#tab-export a').evaluateAll(es=>es.map(e=>e.getAttribute('href')));
 const tabs=await page.locator('.subnav-pill').evaluateAll(es=>es.map(e=>e.dataset.tab));
 const english={};
 for(const tab of tabs){await page.evaluate(t=>switchTab(t),tab);english[tab]=await page.locator('#tab-'+tab+' h2,#tab-'+tab+' h3').first().innerText();}
 await page.locator('[data-lang="sv"]').click();
 for(const tab of tabs){
  await page.evaluate(t=>switchTab(t),tab);
  await page.waitForTimeout(100);
  const heading=await page.locator('#tab-'+tab+' h2,#tab-'+tab+' h3').first().innerText();
  assert.notEqual(heading,english[tab],`${tab}: heading should translate`);
 }
 await page.evaluate(()=>switchTab('intro'));
 assert.match(await page.locator('#kpi-smd-card').innerText(),/Med enkla ord.*osäkerheten/s);
 assert.match(await page.locator('#kpi-grade-card').innerText(),/Med enkla ord.*begränsad/s);
 assert.match(await page.locator('#kpi-smd-card').innerText(),/−0,97/);
 assert.match(await page.locator('#kpi-grade-card .kpi-value').innerText(),/⊕⊕◯◯ Låg/);
 await page.selectOption('#filter-modality','TEAS');
 await page.waitForTimeout(100);
 // Title text changed from "TEAS Primary 24-h Opioid Sparing" to "Primary
 // Efficacy Analysis: TEAS vs Sham" so the EA-vs-usual-care companion result
 // is no longer implicitly co-labelled "primary" (PROSPERO's primary EA
 // comparison is EA vs sham, for which no eligible trial exists). The
 // Swedish translation still has to name TEAS and identify this as the
 // primary/effect analysis.
 {
   const svTitle = await page.locator('#kpi-effect-title').innerText();
   assert.match(svTitle, /TEAS/i, 'TEAS title should still name TEAS after translation');
   assert.match(svTitle, /effektanalys|primär/i, 'TEAS title should still identify this as the primary/effect analysis after translation');
 }
 assert.match(await page.locator('#kpi-study-count').innerText(),/studier/);
 await page.evaluate(()=>switchTab('explorer'));
 await page.selectOption('#filter-surgery','Thoracic & Cardiac');
 await page.waitForTimeout(100);
 assert.match(await page.locator('#explorer-surgery-summary').innerText(),/Kirurgiska specialiteter/);
 assert.match(await page.locator('#filter-surgery option:checked').innerText(),/Torax/);
 const selectedRows=await page.locator('#explorer-table-body tr').count();
 await page.locator('[data-lang="en"]').click();
 assert.equal(await page.locator('#filter-surgery').inputValue(),'Thoracic & Cardiac');
 assert.equal(await page.locator('#filter-surgery option:checked').innerText(),'Thoracic & Cardiac');
 assert.equal(await page.locator('#explorer-table-body tr').count(),selectedRows);
 assert.match(await page.locator('#study-search-input').getAttribute('placeholder'),/Search author/);
 await page.locator('[data-lang="sv"]').click();
 assert.match(await page.locator('#study-search-input').getAttribute('placeholder'),/Sök författare/);
 await page.locator('[data-preset="all"]').click();
 await page.evaluate(()=>switchTab('rob2'));
 await page.selectOption('#rob2-outcome-filter','opioid_24h');
 await page.selectOption('#filter-rob','Low');
 await page.waitForTimeout(100);
 assert.match(await page.locator('#rob2-outcome-status-badge').innerText(),/Bedömda för utfallet/);
 const rows=await page.locator('#rob2-table-body tr').count();
 await page.locator('[data-lang="en"]').click();
 assert.equal(await page.locator('#rob2-table-body tr').count(),rows);
 assert.match(await page.locator('#rob2-outcome-status-badge').innerText(),/Assessed for Outcome/);
 assert.deepEqual(await page.locator('#tab-export a').evaluateAll(es=>es.map(e=>e.getAttribute('href'))),downloads);
 assert.equal(await page.evaluate(()=>JSON.stringify(STUDIES_DATA)),source,'Translations must not change scientific data');
 await page.locator('[data-lang="sv"]').click();
 await page.reload({waitUntil:'networkidle'});
 assert.equal(await page.locator('html').getAttribute('lang'),'sv');
 assert.match(await page.locator('#kpi-smd-card').innerText(),/−0,97/);
 await page.screenshot({path:'tmp/tab-audit/swedish-overview.png'});
 await page.evaluate(()=>showStatPopover('hedgesG',document.querySelector('#kpi-smd-card .stat-info-btn')));
 assert.match(await page.locator('#stat-popover-context-text').innerText(),/−0,97/);
 assert.doesNotMatch(await page.locator('#stat-popover-context-text').innerText(),/0,156|−0,89/);
 await page.evaluate(()=>setLanguage('en'));
 assert.match(await page.locator('#stat-popover-context-text').innerText(),/−0.97/);
 assert.match(await page.locator('#stat-popover-context-text').innerText(),/seven-trial/);
 await page.evaluate(()=>hideStatPopover());
 await page.locator('[data-lang="en"]').click();
 assert.match(await page.locator('#kpi-smd-card').innerText(),/−0.97/);
 assert.match(await page.locator('#kpi-grade-card .kpi-value').innerText(),/⊕⊕◯◯ Low/);
 assert.deepEqual(errors,[]);
 console.log('PASS: EN/SV headings on all 14 tabs, bilingual interpretations and correct saved values, dynamic filter labels, preserved selections, reversible text, persistence, unchanged scientific data and download targets.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
