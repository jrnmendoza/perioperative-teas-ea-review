// Functional audit against a built local site or DASHBOARD_URL.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copiedText=text;}}}));
 await page.goto(process.env.DASHBOARD_URL || 'http://127.0.0.1:8765',{waitUntil:'networkidle'});
 const tabs=await page.locator('.subnav-pill').evaluateAll(es=>es.map(e=>e.dataset.tab));
 for(const tab of tabs){
   await page.evaluate(t=>switchTab(t),tab);
   await page.locator(`.subnav-pill[data-tab="${tab}"]`).click();
   assert.equal(await page.locator('.tab-content.active').getAttribute('id'),'tab-'+tab);
   assert.ok((await page.locator('#tab-'+tab).innerText()).length>100);
 }
 await page.evaluate(()=>{applyPreset('all');switchTab('secondary');});
 assert.ok(await page.locator('.subgroup-forest-header td').first().evaluate(e=>e.getBoundingClientRect().width>800),'Subgroup header must span the forest table');
 const outcomes=await page.locator('#meta-outcome-select option').evaluateAll(es=>es.map(e=>e.value));
 const subgroups=await page.locator('#meta-subgroup-select option').evaluateAll(es=>es.map(e=>e.value));
 const sorts=await page.locator('#meta-sort-select option').evaluateAll(es=>es.map(e=>e.value));
 let combinations=0;
 for(const modality of ['all','TEAS','EA']){
  await page.selectOption('#filter-modality',modality);
  for(const outcome of outcomes){
   await page.selectOption('#meta-outcome-select',outcome);
   const expected=await page.evaluate(()=>{
    const s=getFilteredStudies(false), binary=['ponv_24h','rescue_analgesia'].includes(currentOutcome);
    return (binary?MetaEngine.runBinaryMeta(s,currentOutcome):MetaEngine.runContinuousMeta(s,currentOutcome)).k;
   });
   if(outcome==='opioid_24h')assert.equal(expected,{all:7,TEAS:4,EA:3}[modality]);
   if(modality==='all')assert.equal(expected,{opioid_24h:7,opioid_48h:3,opioid_72h:1,pain_rest_24h:2,ponv_24h:2,flatus_time:6,intraop_opioid:7,rescue_analgesia:4}[outcome]);
   for(const subgroup of subgroups){
    await page.selectOption('#meta-subgroup-select',subgroup);
    for(const sort of sorts){
     await page.locator('#meta-sort-select').evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('change'));},sort);
     assert.equal(await page.locator('#forest-table-body .study-checkbox').count(),expected,`${modality}/${outcome}/${subgroup}/${sort}`);
     assert.doesNotMatch(await page.locator('#forest-table-body').innerText(),/NaN|undefined|Infinity/);
     combinations++;
    }
   }
  }
 }
 await page.evaluate(()=>{applyPreset('all');switchTab('explorer');});
 assert.equal(await page.locator('#explorer-table-body tr').count(),70);
 const ids=await page.evaluate(()=>STUDIES_DATA.map(s=>s.id));
 for(const id of ids){
  await page.evaluate(id=>openStudyDrawer(id),id);
  assert.doesNotMatch(await page.locator('#study-modal-content').innerText(),/(?<!Mixed\/)undefined|NaN/);
  await page.evaluate(()=>closeStudyDrawer());
 }
 await page.locator('#study-search-input').fill('THIS_STUDY_DOES_NOT_EXIST');
 await page.evaluate(()=>switchTab('secondary'));
 assert.match(await page.locator('#forest-table-body').innerText(),/No matching data/);
 await page.evaluate(()=>switchTab('limitations'));
 assert.match(await page.locator('#sim-baseline-md').innerText(),/No matching primary data/);
 await page.evaluate(()=>{applyPreset('all');switchTab('rob2');});
 assert.equal(await page.locator('#secondary-rob-coverage tbody tr').count(),26);
 for(const o of await page.locator('#rob2-outcome-filter option').evaluateAll(es=>es.map(e=>e.value))){
  await page.selectOption('#rob2-outcome-filter',o);
  assert.equal(await page.locator('#rob2-table-body tr').count(),70);
  assert.doesNotMatch(await page.locator('#rob2-table-body').innerText(),/(?<!Mixed\/)undefined|NaN/);
 }
 await page.evaluate(()=>switchTab('mcid'));
 for(const threshold of ['10mg','8mg','30pct','5mg']){
  await page.locator(`[data-thresh="${threshold}"]`).click();
  const counts=await page.locator('[id^="kpi-mcid-q"][id$="-count"]').allTextContents();
  assert.equal(counts.reduce((s,x)=>s+Number(x),0),6);
  assert.equal(await page.locator('#mcid-plot-container circle').count(),6);
  assert.doesNotMatch(await page.locator('#mcid-plot-container').innerHTML(),/NaN|Infinity/);
  await page.locator('#btn-export-mcid-report').click();
  assert.match(await page.evaluate(()=>copiedText),threshold==='30pct'?/30 %/:/mg IV MME/);
 }
 await page.evaluate(()=>{switchTab('limitations');applySimScenario('optimistic');});
 assert.equal(await page.locator('#sim-post-md').innerText(),'−10.00 mg');
 await page.evaluate(()=>applySimScenario('conservative'));
 assert.equal(await page.locator('#sim-post-md').innerText(),'−5.00 mg');
 await page.evaluate(()=>applySimScenario('worst'));
 assert.equal(await page.locator('#sim-post-md').innerText(),'+0.00 mg');
 await page.evaluate(()=>{switchTab('secondary');currentOutcome='opioid_24h';renderMetaLab();});
 assert.doesNotMatch(await page.locator('#forest-table-body').innerText(),/Simulated/);
 const downloadPromise=page.waitForEvent('download');
 await page.evaluate(()=>exportDatasetCSV());
 const download=await downloadPromise;
 const csv=fs.readFileSync(await download.path(),'utf8');
 assert.match(csv,/Not available in this dataset/);
 assert.doesNotMatch(csv,/(?<!Mixed\/)undefined|NaN/);
 assert.equal(csv.split('\n').filter(x=>x.includes('"Available"')).length,7);
 await page.evaluate(()=>{applySimScenario('baseline');switchTab('extraction');});
 for(const tab of ['equi','stat','pca','calc','lit'])await page.locator(`[data-conv-tab="${tab}"]`).click();
 await page.locator('[data-conv-tab="calc"]').click();
 for(const drug of await page.locator('#calc-drug-select option').evaluateAll(es=>es.map(e=>e.value))){
  await page.selectOption('#calc-drug-select',drug);
  assert.match(await page.locator('#calc-equi-res').innerText(),/mg IV MME/);
 }
 await page.locator('#calc-drug-dose').fill('-1');
 assert.match(await page.locator('#calc-equi-res').innerText(),/Enter/);
 await page.locator('#calc-stat-n').fill('');
 assert.match(await page.locator('#calc-stat-res').innerText(),/Enter/);
 await page.locator('#calc-stat-n').fill('50');
 assert.match(await page.locator('#calc-stat-res').innerText(),/Median 15/);
 await page.locator('#calc-stat-q1').fill('99');
 assert.match(await page.locator('#calc-stat-res').innerText(),/ordered/);
 await page.evaluate(()=>switchTab('evidence'));
 await page.locator('#btn-export-grade-sof').click();
 assert.equal(await page.evaluate(()=>copiedText.split('\n').filter(x=>x.startsWith('•')).length),await page.locator('#grade-sof-table-body tr').count());
 await page.evaluate(()=>switchTab('prisma'));
 await page.locator('#btn-export-prisma-summary').click();
 assert.match(await page.evaluate(()=>copiedText),/70 randomized/);
 await page.evaluate(()=>switchTab('glossary'));
 await page.locator('[data-lang="sv"]').click();
 assert.equal(await page.evaluate(()=>localStorage.getItem('app_lang')),'sv');
 await page.locator('[data-lang="en"]').click();
 await page.locator('#toggle-explain-stats').click();
 assert.equal(await page.locator('#toggle-explain-stats').getAttribute('aria-checked'),'false');
 await page.locator('#toggle-explain-stats').click();
 assert.equal(await page.locator('#toggle-explain-stats').getAttribute('aria-checked'),'true');
 await page.route(/\.log(?:\?|$)/,route=>route.abort());
 await page.reload({waitUntil:'networkidle'});
 await page.evaluate(()=>switchTab('primary'));
 await page.waitForFunction(()=>document.getElementById('stata-terminal-content').textContent.includes('could not be loaded'));
 await page.evaluate(()=>switchTab('metareg'));
 await page.waitForFunction(()=>document.getElementById('stata-metareg-terminal-content').textContent.includes('could not be loaded'));
 assert.deepEqual(errors,[]);
 fs.mkdirSync('tmp/tab-audit',{recursive:true});
 console.log(`PASS: ${tabs.length} tabs; ${combinations} forest combinations; 70 drawers; 26 secondary RoB rows; four MCID thresholds; simulator isolation; CSV; calculators; empty states.`);
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
