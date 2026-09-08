const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.DASHBOARD_URL || 'http://127.0.0.1:8765',{waitUntil:'networkidle'});
 const ownsCards=()=>[...document.querySelectorAll('main .dashboard-card')].every(e=>e.closest('.tab-content'));
 assert.ok(await page.evaluate(ownsCards),'Every content card must belong to a tab');
 // Recreate the reported escaped-card defect and prove this guard rejects it.
 await page.evaluate(()=>{const card=document.querySelector('#tab-primary .dashboard-card');window.cardParent=card.parentElement;window.cardNext=card.nextSibling;window.movedCard=card;document.querySelector('main').append(card);});
 assert.equal(await page.evaluate(ownsCards),false,'Escaped-card mutation must fail');
 await page.evaluate(()=>cardParent.insertBefore(movedCard,cardNext));
 const groups=await page.locator('.nav-btn[data-nav-group]').evaluateAll(es=>es.map(e=>e.dataset.navGroup));
 for(const group of groups){
   await page.locator(`[data-nav-group="${group}"]`).click();
   const tabs=await page.locator(`#subnav-${group} .subnav-pill`).evaluateAll(es=>es.map(e=>e.dataset.tab));
   for(const tab of tabs){
     await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
     await page.locator(`.subnav-pill[data-tab="${tab}"]`).click();
     await page.waitForTimeout(350);
     const state=await page.evaluate(t=>({
       scroll:scrollY,
       visible:[...document.querySelectorAll('.tab-content')].filter(e=>e.getClientRects().length).map(e=>e.id),
       top:document.querySelector('#tab-'+t).getBoundingClientRect().top,
       heading:document.querySelector('#tab-'+t+' h2,#tab-'+t+' h3')?.textContent.trim(),
       stray:document.querySelectorAll('main > .dashboard-card').length
     }),tab);
     assert.deepEqual(state.visible,['tab-'+tab]);assert.equal(state.scroll,0);
     assert.ok(state.top<900,`${tab} begins below viewport: ${state.top}`);
     assert.ok(state.heading,`${tab} needs visible content`);assert.equal(state.stray,0);
   }
 }
 await page.locator('[data-nav-group="evidence"]').click();
 assert.equal(await page.locator('#grade-sof-table-body').isVisible(),true);
 fs.mkdirSync('tmp/tab-audit',{recursive:true});
 await page.screenshot({path:'tmp/tab-audit/navigation-evidence.png'});
 await page.locator('[data-tab="rob2"]').click();
 await page.selectOption('#rob2-outcome-filter','opioid_24h');
 const szmit=page.locator('#rob2-table-body tr').filter({hasText:'Szmit 2021'});
 assert.match(await szmit.innerText(),/Assessed:/);
 assert.equal(await szmit.locator('td').nth(6).locator('span').getAttribute('title'),'Some concerns');
 const primary=await page.evaluate(()=>STUDIES_DATA.filter(s=>s.outcomes.opioid_24h).map(s=>({name:s.key,state:resultRob(s,'opioid_24h').state})));
 assert.equal(primary.length,7);assert.ok(primary.every(s=>!['pending','not-assessed'].includes(s.state)));
 assert.doesNotMatch(await page.locator('#rob2-table-body').innerText(),/Outcome not measured/);
 await page.locator('[data-nav-group="results"]').click();
 await page.locator('[data-tab="metareg"]').click();
 assert.equal(await page.locator('#metareg-availability').isVisible(),true);
 await page.screenshot({path:'tmp/tab-audit/navigation-metareg.png'});
 assert.deepEqual(errors,[]);
 console.log('PASS: 14 tabs via actual navigation, one visible panel, top-of-page reset, no escaped cards; escaped-card mutation rejected; GRADE visible; Szmit and all seven primary RoBs mapped; meta-regression availability visible.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
