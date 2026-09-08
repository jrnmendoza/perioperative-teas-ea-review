const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.DASHBOARD_URL || 'http://127.0.0.1:8765',{waitUntil:'networkidle'});
 const tabs=await page.locator('.tab-content').evaluateAll(es=>es.map(e=>e.id.slice(4)));
 const report={};
 for(const tab of tabs){
  await page.evaluate(t=>switchTab(t),tab);
  await page.waitForTimeout(300);
  report[tab]=await page.locator('#tab-'+tab).evaluate(el=>({
    headings:[...el.querySelectorAll('h2,h3')].map(e=>e.textContent.trim()),
    empty:[...el.querySelectorAll('[id]')].filter(e=>!e.textContent.trim()&&!e.children.length&&!['INPUT','IMG','SELECT','CANVAS'].includes(e.tagName)).map(e=>e.id),
    images:[...el.querySelectorAll('img')].map(e=>({src:e.getAttribute('src'),ok:e.complete&&e.naturalWidth>0})),
    controls:[...el.querySelectorAll('button,input,select,a')].map(e=>({id:e.id,label:(e.textContent||e.getAttribute('placeholder')||'').trim().slice(0,100),action:e.getAttribute('onclick'),href:e.getAttribute('href'),disabled:e.disabled})),
    text:el.innerText
  }));
 }
 const links=[...new Set(Object.values(report).flatMap(r=>r.controls.map(x=>x.href)).filter(x=>x&&!/^(https?:|mailto:|javascript:|#)/.test(x)))];
 report.brokenLinks=[];
 for(const link of links){const r=await page.request.get(new URL(link,page.url()).href); if(!r.ok())report.brokenLinks.push({link,status:r.status()});}
 report.errors=errors;
 fs.mkdirSync('tmp/tab-audit',{recursive:true});fs.writeFileSync('tmp/tab-audit/inventory.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(Object.fromEntries(Object.entries(report).map(([k,v])=>[k,v.headings?{headings:v.headings,empty:v.empty,brokenImages:v.images.filter(x=>!x.ok),controls:v.controls.length}:v])),null,2));
 await browser.close();
})();
