// Browser regression test for the v38 dashboard (current_review_ui.js, interactive_explorer.js, theme.js).
// Build the site, then run:  node scripts/check_current_dashboard_ui.cjs [--site _site]
// The test serves that directory itself; DASHBOARD_URL tests an already-running server or the live site instead.
// BROWSER_CHANNEL picks the browser (default: installed Chrome).
// Every check reads the canonical payload in the page (window.CURRENT_REVIEW) for its expectations.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const SITE=path.resolve(process.argv.includes('--site')?process.argv[process.argv.indexOf('--site')+1]:'_site');
const TYPES={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.pdf':'application/pdf','.csv':'text/csv','.md':'text/markdown','.txt':'text/plain','.R':'text/plain'};
// Minimal static server for the built site (GET/HEAD only, no directory listing, no path escape).
function serve(){return new Promise(res=>{const srv=http.createServer((req,rsp)=>{const rel=decodeURIComponent(new URL(req.url,'http://x').pathname);
  let file=path.join(SITE,rel.endsWith('/')?rel+'index.html':rel);if(!file.startsWith(SITE)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){rsp.writeHead(404);rsp.end();return;}
  rsp.writeHead(200,{'Content-Type':TYPES[path.extname(file)]||'application/octet-stream'});if(req.method==='HEAD'){rsp.end();return;}fs.createReadStream(file).pipe(rsp);});
  srv.listen(0,'127.0.0.1',()=>res(srv));});}
let BASE=(process.env.DASHBOARD_URL||'').replace(/\/$/,''),server=null;
const EXPECTED_ASSETS=['theme.js','current_review.css','evidence_graph.js','current_review.js','article_figures.js','search_strategies.js','interactive_explorer.js','current_review_ui.js'];
let passed=0;const ok=(name)=>{passed++;console.log('PASS '+name);};

(async()=>{
  if(!BASE){assert.ok(fs.existsSync(path.join(SITE,'index.html')),`No built site at ${SITE}: run scripts/build_site.py first`);server=await serve();BASE=`http://127.0.0.1:${server.address().port}`;}
  const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'chrome'});
  const errors=[];
  // Script errors, console errors (other than the generic resource line) and any failed response except the absent favicon.
  const newPage=async(opts={})=>{const ctx=await browser.newContext({viewport:{width:1440,height:1000},...opts});const page=await ctx.newPage();
    page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'&&!m.text().startsWith('Failed to load resource'))errors.push(m.text());});
    page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))errors.push(`${r.status()} ${r.url()}`);});
    page.on('requestfailed',r=>{if(!r.url().endsWith('/favicon.ico')&&!/ERR_ABORTED/.test(r.failure()?.errorText||''))errors.push(`${r.failure()?.errorText} ${r.url()}`);});return page;};
  const hash=p=>p.evaluate(()=>location.hash);
  const count=p=>p.locator('#explorer-count').textContent();
  const go=async(p,h)=>{await p.goto(BASE+'/index.html'+h,{waitUntil:'load'});await p.waitForFunction(()=>document.querySelector('#content h2'));};

  // ---------- 1. Active assets, build provenance, navigation semantics ----------
  let page=await newPage({colorScheme:'dark'});
  const requested=[];page.on('request',r=>requested.push(new URL(r.url()).pathname.split('/').pop()));
  await go(page,'#overview');
  const assets=requested.filter(n=>/\.(js|css)$/.test(n));
  assert.deepEqual([...new Set(assets)].sort(),[...EXPECTED_ASSETS].sort(),'Loaded JS/CSS must be exactly the v38 assets');
  assert.ok(!requested.includes('app.js')&&!requested.includes('v34_data.js'),'Legacy bundles must not load');
  ok('only the v38 JS/CSS assets load (no app.js)');
  const meta=await page.evaluate(()=>JSON.parse(document.getElementById('build-meta').textContent));
  for(const sel of ['#overview-provenance','#provenance-line']){
    const t=await page.locator(sel).textContent();
    assert.ok(t.includes('Analytical core: v38')&&t.includes('E2 (post hoc)')&&t.includes(meta.git_commit.slice(0,7)),`${sel} must show analysis dates and the build commit: ${t}`);
  }
  ok('build SHA/date come from the inline build record (Overview and footer)');
  const nav=await page.evaluate(()=>({groups:[...document.querySelectorAll('.nav .nav-group')].map(g=>[g.querySelector('.nav-group-label').textContent,[...g.querySelectorAll('a[data-view]')].map(a=>a.dataset.view)]),
    tabs:document.querySelectorAll('.nav [role=tab],.nav [role=tablist]').length,current:[...document.querySelectorAll('.nav [aria-current=page]')].map(a=>a.dataset.view)}));
  assert.deepEqual(nav.groups,[['Evidence',['overview','results','e1e2','qor']],['Explore studies',['studies','coverage','risk','evidence']],['Review process',['prisma','methods','downloads']]]);
  assert.equal(nav.tabs,0);assert.deepEqual(nav.current,['overview']);
  await page.locator('.nav a[data-view=results]').click();await page.waitForFunction(()=>location.hash==='#results');
  assert.deepEqual(await page.evaluate(()=>[...document.querySelectorAll('.nav [aria-current=page]')].map(a=>a.dataset.view)),['results']);
  await page.goBack();await page.waitForFunction(()=>location.hash==='#overview');
  assert.equal(await page.locator('#content h2').first().textContent(),'Evidence, with its limits');
  // Keyboard (fresh load): skip link first, then nav links; Enter follows a route; focus is visible.
  await page.reload({waitUntil:'load'});await page.waitForSelector('#content h2');
  await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.className),'skip');
  await page.keyboard.press('Tab');await page.keyboard.press('Tab');
  const focused=await page.evaluate(()=>({view:document.activeElement.dataset.view,outline:getComputedStyle(document.activeElement).outlineStyle}));
  assert.equal(focused.view,'overview');assert.notEqual(focused.outline,'none','Focused nav link needs a visible outline');
  await page.keyboard.press('Tab');await page.keyboard.press('Enter');await page.waitForFunction(()=>location.hash==='#results');
  ok('grouped route navigation: links with aria-current, back/forward, keyboard and visible focus');

  // ---------- 2. Overview: complete versus outstanding ----------
  await go(page,'#overview');
  const ov=await page.evaluate(()=>({items:[...document.querySelectorAll('#overview-outstanding li')].map(l=>l.textContent),want:window.CURRENT_REVIEW.outstanding,
    done:document.querySelector('.status-done').textContent,limits:document.querySelector('.limits').textContent}));
  assert.deepEqual(ov.items,ov.want.map(x=>x.replace(/\.$/,'')));
  assert.ok(/Core v38 RoB 2 and GRADE are complete under the adopted workflow/.test(ov.done));
  for(const needle of ['Import mapping gap','Historical selection','Reports and trials','Randomised and analysed N','Source holds','E2 is post hoc','Reproduction is not source truth'])
    assert.ok(ov.limits.includes(needle),'Limitation missing: '+needle);
  // Second review, where recorded, is stated with reviewer and date in the Overview, RoB, GRADE and QoR views.
  const sr=await page.evaluate(()=>(window.CURRENT_REVIEW.second_review||[]).map(r=>r.reviewer));
  if(sr.length){for(const h of ['#overview','#risk','#evidence','#qor']){await go(page,h);assert.ok((await page.locator('#content').innerText()).includes(`Second review (${sr[0]},`),`${h} must state the second review`);}await go(page,'#overview');}
  ok('Overview separates the complete v38 core from outstanding work and keeps the limitations; second review stated where recorded');

  // ---------- 3. Model labels: one deterministic, injective mapping ----------
  const labels=await page.evaluate(()=>{const d=window.CURRENT_REVIEW,ids=[...d.models.map(m=>m.model_id),...d.e2_analysis.models.map(m=>m.model_id),
    ...d.qor_analysis.main_models.map(m=>m.model_id),...d.qor_analysis.diagnostics.map(m=>m.model_id),...(d.qor_later_models||[]).map(m=>m.model_id)];
    return {ids,a:ids.map(window.reviewModelLabel),b:ids.map(window.reviewModelLabel)};});
  assert.deepEqual(labels.a,labels.b,'Labels must be deterministic');
  assert.equal(new Set(labels.a).size,labels.ids.length,'Two models share a label');
  assert.ok(labels.a.every((l,i)=>l&&l!==labels.ids[i]),'Every model needs a readable label');
  assert.equal(labels.a[labels.ids.indexOf('opioid24_TEAS_sham')],'Cumulative 0–24 h systemic opioid consumption — TEAS vs sham');
  await go(page,'#evidence');
  assert.ok(await page.locator('#content table .model-id code',{hasText:'opioid24_TEAS_sham'}).count()>=1,'GRADE table keeps the model ID');
  ok(`model labels map deterministically to ${labels.ids.length} model IDs and the IDs stay visible`);

  // ---------- 4. Studies & figures: Stata descriptive figures ----------
  await go(page,'#studies');
  const figs=await page.evaluate(()=>window.CURRENT_REVIEW.stata.figures.filter(f=>f.kind==='descriptive').map(f=>f.figure_id));
  assert.ok(figs.length>=6);
  assert.equal(await page.locator('.glance-figs .fig-card').count(),figs.length);
  await page.waitForFunction(n=>[...document.querySelectorAll('.fig-card img')].filter(i=>i.complete&&i.naturalWidth>0).length===n,figs.length);
  const links=await page.evaluate(()=>[...document.querySelectorAll('.fig-card figcaption a[download]')].map(a=>a.getAttribute('href')));
  assert.equal(links.length,figs.length*3);
  const statuses=[];for(const h of links)statuses.push((await page.request.get(new URL(h,BASE+'/').href)).status());
  assert.ok(statuses.every(s=>s===200),'Every Stata figure file must resolve');
  assert.ok(await page.locator('.glance-figs a[href="#methods?section=stata"]').count()===1);
  const top=await page.evaluate(()=>[...document.querySelectorAll('#content > *')].map(e=>e.className||e.id));
  assert.ok(top.indexOf('glance-figs')<top.indexOf('rich-explorer-container')||top[0]==='glance-figs','Figures come before the explorer');
  await page.locator('.fig-card .fig-thumb').first().click();
  assert.ok(await page.locator('#figure-dialog[open]').isVisible());
  assert.equal(await page.locator('#figure-caption a[download]').count(),3);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#figure-dialog[open]').count(),0);
  ok(`${figs.length} Stata descriptive figures shown in Studies, with lightbox and SVG/PDF/PNG downloads`);

  // ---------- 5. Provenance legend and characteristic statuses ----------
  const leg=await page.evaluate(()=>{const d=window.CURRENT_REVIEW,used=[...new Set(d.characteristics.map(c=>c.status))];
    const base=d.characteristics.filter(c=>/baseline_protocol_extraction/.test(c.source));
    return {used:used.length,usedLabels:used.map(s=>({'Verified (registry)':'Verified — registry','Verified (PDF quote)':'Verified — PDF quotation','Partly verified (source excerpt)':'Partly verified — source excerpt','Canonical result register':'Canonical result register','Source-traced (extraction record)':'Source-traced','Verified (PDF quote, second reviewer)':'Verified — PDF quotation, second reviewer','Extracted (PDF quote, single extractor)':'Extracted from PDF quotation — single extractor','Legacy (v26, not re-verified)':'Legacy extraction — not re-verified','Not verified':'Not verified','Not reported in source':'Not reported in source','Not extracted':'Not extracted'})[s]),
      legacy:used.includes('Legacy (v26, not re-verified)'),base:base.length,baseSingle:base.filter(c=>c.status==='Extracted (PDF quote, single extractor)').length,single:used.includes('Extracted (PDF quote, single extractor)'),reviewed:used.includes('Verified (PDF quote, second reviewer)'),btns:[...document.querySelectorAll('.prov-legend .prov-list button.term')].map(b=>b.getAttribute('aria-label')),text:document.querySelector('.prov-legend').textContent};});
  assert.equal(leg.btns.length,leg.used);
  assert.ok(leg.text.includes('Characteristics do not all have the same verification level.')&&leg.text.includes('Missing values are not inferred.'));
  // The regimen-field sentence follows the data: single-extractor values say so; second-reviewed values name the review.
  if(leg.single)assert.ok(leg.text.includes('single extractor'),'Legend must say the regimen fields are single-extractor');
  if(leg.reviewed)assert.ok(/confirmed by a second reviewer \(SP, 2026-09-28/.test(leg.text)||/confirmed by a second reviewer \([A-Z]{2,4}, \d{4}-\d{2}-\d{2}/.test(leg.text),'Legend must name the second review');
  const regimenLabel=leg.reviewed?'Verified — PDF quotation, second reviewer':'Extracted from PDF quotation — single extractor';
  // Every status the data uses has its legend entry (and, by the count above, no other entry is shown); the core ones are always used.
  assert.ok(leg.usedLabels.every(Boolean),'A characteristic status has no legend label');
  for(const lab of new Set([...leg.usedLabels,'Verified — registry','Verified — PDF quotation','Source-traced',regimenLabel,'Not reported in source']))
    assert.ok(leg.btns.some(b=>b.startsWith(lab+':')),'Legend entry missing: '+lab);
  // Baseline and protocol fields quoted from the PDFs: the legend says so, with the single-extractor count; no legacy wording once no legacy value is left.
  if(leg.base){assert.ok(/Age, sex, BMI, ASA status, anaesthesia and the stimulation protocol/.test(leg.text),'Legend must describe the baseline/protocol extraction');
    if(leg.baseSingle)assert.ok(leg.text.includes(`${leg.baseSingle} values come from a single extractor`),'Legend must count the single-extractor baseline values');}
  if(!leg.legacy)assert.ok(!/legacy/i.test(leg.text),'Legend must not mention legacy values when none remain');
  const nr=leg.btns.find(b=>b.startsWith('Not reported in source:'));assert.ok(/not a failed extraction/.test(nr));
  await page.locator('.prov-legend .prov-list button.term').first().focus();
  assert.ok(await page.locator('#term-tip').isVisible(),'Legend help must appear on keyboard focus');
  assert.ok((await page.locator('#term-tip').textContent()).startsWith('Verified — registry:'));
  await page.keyboard.press('Escape');assert.ok(await page.locator('#term-tip').isHidden());
  const table=await page.evaluate(()=>{const d=window.CURRENT_REVIEW,t=document.querySelector('.prov-counts table');
    const cells=[...t.querySelectorAll('tbody td')].map(td=>+td.textContent||0);return {sum:cells.reduce((a,b)=>a+b,0),n:d.characteristics.length};});
  assert.equal(table.sum,table.n,'Per-field status counts must cover every characteristic row');
  ok('provenance legend: every status explained, keyboard tooltips, per-field counts cover all rows');

  // Study drawer keeps statuses, quotes, sources and links.
  const pqReport=await page.evaluate(()=>window.CURRENT_REVIEW.characteristics.find(c=>c.field==='pca_regimen'&&/^(Extracted \(PDF quote, single extractor\)|Verified \(PDF quote, second reviewer\))$/.test(c.status)).report_id);
  await page.locator(`.study-open[data-id="${pqReport}"]`).first().click();
  await page.waitForSelector('#study-drawer[open]');
  const dr=await page.evaluate(()=>{const t=document.querySelector('#study-drawer').innerText;return {t,q:document.querySelectorAll('#study-drawer .char-quote').length,sr:[...document.querySelectorAll('#study-drawer .vs .sr-only')].map(s=>s.textContent)};});
  assert.ok(dr.q>0,'Drawer must show source quotations');
  assert.ok(dr.sr.some(s=>s.includes(regimenLabel))&&dr.sr.some(s=>s.includes('Verified — registry')));
  for(const needle of ['Source PDF:','SHA-256:','Outcome inventory','Model contributions','E1 / E2 status','Result-specific risk of bias',leg.reviewed?'confirmed by a second reviewer':'not been independently reviewed'])assert.ok(dr.t.includes(needle),'Drawer lacks '+needle);
  if(leg.baseSingle){assert.ok(/Stimulation protocol values marked PQ are quoted from the report .* by a single extractor; second review pending/.test(dr.t),'Drawer must mark the protocol values single-extractor');
    assert.ok(!/STRICTA details are legacy imports/.test(dr.t),'Drawer must not call source-quoted protocol values legacy');}
  assert.ok((await hash(page)).includes('study='));
  await page.locator('#close-drawer').click();assert.ok(!(await hash(page)).includes('study='));
  ok('study drawer retains statuses, verbatim quotes, source PDF/hash, models, E1/E2 and RoB');

  // ---------- 6. Explorer interactivity (filters, presets, chips, URL, history, matrix, columns, glance) ----------
  const total=await count(page);assert.match(total,/^70 of 70 reports · 69 of 69 operational families$/);
  const setSel=async(id,v)=>{await page.selectOption('#explorer-'+id,v);};
  const n=async()=>+(await count(page)).split(' ')[0];
  await page.fill('#explorer-search','PC6');await page.waitForFunction(()=>!/^70 of/.test(document.querySelector('#explorer-count').textContent));
  const nSearch=await n();assert.ok(nSearch>0&&nSearch<70);
  await page.fill('#explorer-search','');await page.waitForFunction(()=>/^70 of/.test(document.querySelector('#explorer-count').textContent));
  const filters=[['modality','TEAS'],['comparator','Sham'],['status','e1'],['family','pain'],['rob','high'],['size','100']];
  for(const [id,v] of filters){await setSel(id,v);const k=await n();assert.ok(k>0&&k<70,`${id} filter gives ${k}`);await setSel(id,id==='modality'||id==='comparator'?'all':'');}
  const surg=await page.evaluate(()=>document.querySelector('#explorer-surgery option:nth-child(2)').value);await setSel('surgery',surg);assert.ok(await n()<70);await setSel('surgery','');
  const ctry=await page.evaluate(()=>document.querySelector('#explorer-country option:nth-child(2)').value);await setSel('country',ctry);assert.ok(await n()<70);await setSel('country','');
  await page.fill('#explorer-ymin','2020');await page.waitForFunction(()=>!/^70 of/.test(document.querySelector('#explorer-count').textContent));await page.fill('#explorer-ymin','');
  await page.waitForFunction(()=>/^70 of/.test(document.querySelector('#explorer-count').textContent));
  for(const [status,label] of [['e2only','E2 only'],['e1e2','E1 + E2']]){await setSel('status',status);assert.ok(await n()>0,label);}
  await setSel('status','');
  await page.locator('.preset',{hasText:'E2 contributors'}).click();const nE2=await n();assert.ok(nE2>0&&nE2<70);
  assert.ok((await hash(page)).includes('status=e2'),'Filters persist in the URL');
  assert.equal(await page.locator('#explorer-chips .chip:not(.clear)').count(),1);
  await page.reload({waitUntil:'load'});await page.waitForSelector('#explorer-count');assert.equal(await n(),nE2,'Reload restores filters');
  await page.locator('.nav a[data-view=results]').click();await page.waitForFunction(()=>location.hash==='#results');
  await page.goBack();await page.waitForFunction(()=>location.hash.startsWith('#studies'));await page.waitForSelector('#explorer-count');
  assert.equal(await n(),nE2,'Back restores the filtered explorer');
  await page.goForward();await page.waitForFunction(()=>location.hash==='#results');await page.goBack();await page.waitForSelector('#explorer-count');
  await page.locator('#explorer-chips .chip:not(.clear)').first().click();assert.equal(await n(),70,'Chip removes its filter');
  await page.locator('.glance-bar[data-glance=modality]').first().click();assert.ok(await n()<70,'Glance bar filters');
  await page.locator('#explorer-chips .chip.clear').click();assert.equal(await n(),70);
  await page.locator('#explorer-matrix-toggle').click();assert.ok((await hash(page)).includes('matrix=detailed'));
  assert.ok(await page.locator('.explorer-table th.grp').count()>=5,'Detailed matrix groups');
  await page.locator('#explorer-matrix-toggle').click();
  await page.locator('.colchooser summary').click();await page.locator('input[data-col=acupoints]').check();
  assert.ok((await hash(page)).includes('acupoints'));assert.ok(await page.locator('.explorer-table th',{hasText:'Acupoints'}).count()===1);
  await page.locator('input[data-col=acupoints]').uncheck();
  await page.locator('button.matrix-cell.e1').first().click();await page.waitForSelector('#cell-dialog[open]');
  assert.ok(await page.locator('#cell-dialog .model-id').count()>0,'Cell dialog shows model label with its ID');
  assert.ok(await page.locator('#cell-dialog .result-open').count()>0,'Cell dialog links exact results');
  await page.locator('#cell-dialog [data-close]').click();
  await page.locator('.study-row td:nth-child(2)').first().click();await page.waitForSelector('#study-drawer[open]');await page.locator('#close-drawer').click();
  ok('explorer: search, 10 filters, E1/E2 status filters, presets, chips, URL persistence, back/forward, glance bars, matrix, columns, cell dialog, row drawer');

  // ---------- 7. Cross-links: results, RoB and forest plots → studies and results ----------
  const combo=await page.evaluate(()=>{const r=window.CURRENT_REVIEW.inputs.find(x=>x.result_id.includes('+')&&x.role!=='SENSITIVITY')||window.CURRENT_REVIEW.inputs.find(x=>x.result_id.includes('+'));return {rid:r.result_id,mid:r.model_id};});
  await go(page,`#results?model=${encodeURIComponent(combo.mid)}`);await page.waitForSelector('#model-panel:not([hidden])');
  assert.ok((await page.locator('#model-panel .forest-summary').first().textContent()).length>20,'Forest has a text summary');
  const fp=page.locator(`#model-panel .fp-link.result-open[data-result="${combo.rid}"]`);assert.equal(await fp.count(),1);
  await fp.focus();await page.keyboard.press('Enter');await page.waitForSelector('#result-drawer[open]');
  const ri=await page.locator('#result-drawer').innerText();
  for(const needle of [combo.rid,'Source','SHA-256','Reported unit','conversion factor','analysed as','Study estimate','Decision','Used in','Risk of bias (v38, result-specific)','Model ID','Combined-arm input','control arm is counted once'])
    assert.ok(ri.includes(needle),'Result inspector lacks '+needle);
  assert.ok((await hash(page)).includes('result='));
  await page.keyboard.press('Escape');await page.waitForFunction(()=>!location.hash.includes('result='));
  await page.locator('#model-panel [data-study]').first().click();await page.waitForSelector('#study-drawer[open]');assert.ok((await hash(page)).startsWith('#studies?study='));
  ok('forest contributor (keyboard) → result inspector with every audit field; combined arms explained; results → study profile');
  await go(page,'#risk');await page.locator('#risk-matrix [data-study]').first().click();await page.waitForSelector('#study-drawer[open]');
  await go(page,'#risk');await page.locator('#risk-matrix .rob-cell').first().click();await page.waitForSelector('#rob-dialog[open]');
  assert.ok(await page.locator('#rob-dialog .model-id').count()>0);await page.keyboard.press('Escape');
  ok('risk-of-bias matrix → study profile and cell rationale with labelled models');
  await go(page,'#e1e2');
  assert.ok((await page.locator('#content').innerText()).includes('E2 is post-hoc.'));
  await page.locator('.e1e2-body',{hasText:'EA vs usual care'}).click();await page.waitForFunction(()=>location.hash.includes('body=EA'));
  await page.locator('[data-e1e2-in=both]').click();await page.waitForFunction(()=>location.hash.includes('in=both'));
  assert.equal(await page.locator('[data-e1e2-in=both]').getAttribute('aria-pressed'),'true');
  const studyFp=page.locator('.fp-link[data-study]').first();await studyFp.click();await page.waitForSelector('#study-drawer[open]');
  ok('E1 vs E2: body picker, membership filters (URL state), post-hoc label, E2 forest → study profile');

  // ---------- 7b. Coverage: structured narrative tables (recovery milestones, harms, satisfaction) ----------
  await go(page,'#coverage');
  const nar=await page.evaluate(()=>{const n=window.CURRENT_REVIEW.narrative_outcomes;if(!n)return null;const sec=document.querySelector('section.narrative');
    const nl=n.harms.filter(r=>r.reporting==='Not located (not a zero)');
    return {has:!!sec,text:sec?sec.textContent:'',rows:document.querySelectorAll('section.narrative .narr-group tbody tr').length,quotes:document.querySelectorAll('section.narrative .narr-group .char-quote').length,
      want:n.milestones.length+n.harms.length-nl.length+n.satisfaction.length,none:nl.map(r=>r.report_id),pending:[...n.milestones,...n.harms,...n.satisfaction].filter(r=>r.second_review==='pending'&&r.quote).length,
      links:[...sec.querySelectorAll('a[download]')].map(a=>a.getAttribute('href'))};});
  if(nar){
    assert.ok(nar.has,'Coverage must show the structured narrative tables');
    assert.equal(nar.rows,nar.want,'Every structured narrative row is shown exactly once');
    assert.equal(nar.quotes,nar.want,'Every structured narrative row shows its quoted source');
    assert.ok(nar.text.includes('nothing is pooled')&&nar.text.includes('registered additional outcomes')&&nar.text.includes(`${nar.pending} rows await second review`),'Narrative note must state no pooling, registration and pending review');
    assert.ok(nar.text.includes(`No intervention-harm result located (${nar.none.length} reports; not a zero)`)&&nar.none.every(id=>nar.text.includes(id)),'Reports without a harms result must be listed as not located, not zero');
    assert.ok(!/pooled (estimate|risk|mean)|meta-analys/i.test(nar.text.replace(/nothing is pooled|not pooled/g,'')),'Narrative tables must not present pooled results');
    for(const f of ['recovery_milestones.csv','harms_structured.csv','satisfaction_acceptability.csv','NARRATIVE_OUTCOMES_REPORT.md'])assert.ok(nar.links.some(h=>h.endsWith(f)),'Narrative download missing: '+f);
    const grp=page.locator('section.narrative details.narr-group').first();await grp.locator('summary').click();
    assert.ok(await grp.locator('tbody tr').first().isVisible(),'A narrative group opens to its rows');
    ok(`coverage: ${nar.want} structured narrative rows with quotes, ${nar.none.length} not-located harms reports, no pooling`);
  }

  // ---------- 8. Downloads grouping ----------
  await go(page,'#downloads');
  const dl=await page.evaluate(()=>({hrefs:[...document.querySelectorAll('a.download')].map(a=>a.getAttribute('href')).sort(),want:window.CURRENT_REVIEW.downloads.map(x=>x.href).sort(),sections:document.querySelectorAll('[data-dl-section]').length}));
  assert.deepEqual(dl.hrefs,dl.want,'Grouping must list every download exactly once');assert.ok(dl.sections>=8);
  await page.fill('#dl-search','grade');const shown=await page.locator('a.download:visible').count();assert.ok(shown>0&&shown<dl.want.length);
  await page.fill('#dl-search','');await page.locator('#dl-primary').check();const prim=await page.locator('a.download:visible').count();assert.ok(prim>=10&&prim<dl.want.length);
  await page.locator('#dl-primary').uncheck();await page.selectOption('#dl-group','stata');assert.equal(await page.locator('[data-dl-section]:visible').count(),1);
  ok(`downloads grouped into ${dl.sections} categories with search, category and primary filters; none dropped`);

  // ---------- 9. Theme: system default, explicit choice persists, aria-pressed truthful ----------
  await go(page,'#overview');
  assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme||''),'','No stored choice: system theme applies');
  assert.equal(await page.locator('#theme-toggle').getAttribute('aria-pressed'),'true','Dark system theme: pressed');
  await page.locator('#theme-toggle').click();
  assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'light');assert.equal(await page.locator('#theme-toggle').getAttribute('aria-pressed'),'false');
  await page.reload({waitUntil:'domcontentloaded'});
  assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'light','Explicit choice survives reload');
  assert.equal(await page.evaluate(()=>getComputedStyle(document.body).backgroundColor),'rgb(248, 250, 252)');
  await page.context().close();
  const light=await newPage({colorScheme:'light'});await go(light,'#overview');
  assert.equal(await light.locator('#theme-toggle').getAttribute('aria-pressed'),'false','Light system theme: not pressed');
  await light.context().close();
  ok('theme: system preference on first use, persisted explicit choice, correct aria-pressed');

  // ---------- 10. Contrast (both themes) and touch targets ----------
  const contrast=async p=>p.evaluate(()=>{
    const lum=c=>{const [r,g,b]=c.match(/[\d.]+/g).slice(0,3).map(v=>{v/=255;return v<=0.03928?v/12.92:((v+0.055)/1.055)**2.4;});return 0.2126*r+0.7152*g+0.0722*b;};
    const bg=el=>{for(let e=el;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;const a=c.match(/[\d.]+/g);if(a&&(a.length<4||+a[3]>0.5))return c;}return 'rgb(255,255,255)';};
    const bad=[];document.querySelectorAll('.nav a,.nav-group-label,.provenance,.note,.tag,.vs,.matrix-cell.e1,.matrix-cell.e2,.rob-cell,.lede,small,.dl-badge,#theme-toggle,.stata-badge,.mem-badge').forEach(el=>{
      if(!el.offsetParent||!el.textContent.trim())return;const s=getComputedStyle(el),l1=lum(s.color),l2=lum(bg(el)),r=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
      const large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&+s.fontWeight>=700);if(r<(large?3:4.5))bad.push(`${el.className||el.tagName} ${r.toFixed(2)}`);});
    return [...new Set(bad)];});
  for(const scheme of ['dark','light']){
    const p=await newPage({colorScheme:scheme});
    for(const h of ['#overview','#studies','#risk','#downloads','#e1e2']){await go(p,h);const bad=await contrast(p);assert.deepEqual(bad,[],`${scheme} ${h} low contrast: ${bad.join('; ')}`);}
    await p.context().close();
  }
  ok('text contrast ≥ 4.5:1 (3:1 large) for navigation, badges, notes, matrix and RoB cells in dark and light themes');

  // ---------- 11. Responsive layout: no whole-page horizontal overflow ----------
  for(const width of [1440,1024,768,430,390]){
    const p=await newPage({viewport:{width,height:900},isMobile:width<700,hasTouch:width<700});
    for(const h of ['#overview','#results?model=opioid24_EA_usual','#e1e2','#qor','#studies','#coverage','#risk','#evidence','#prisma','#methods?section=stata','#downloads']){
      await go(p,h);const o=await p.evaluate(()=>({sw:document.documentElement.scrollWidth,w:innerWidth}));
      assert.ok(o.sw<=o.w,`${width}px ${h}: page scrolls sideways (${o.sw} > ${o.w})`);
    }
    if(width<=430){
      await go(p,'#studies');await p.locator('.study-open').first().click();await p.waitForSelector('#study-drawer[open]');
      const box=await p.locator('#study-drawer').boundingBox();assert.ok(box.x>=0&&box.width<=width,'Drawer fits the phone');
      assert.ok(await p.locator('#close-drawer').isVisible());await p.locator('#close-drawer').click();
      // Touch targets: nav links and toolbar controls ≥ 24 px; small matrix marks answer taps 5 px outside their visible mark.
      const small=await p.evaluate(()=>[...document.querySelectorAll('.nav a,#theme-toggle,.preset,.chip,.rob-cell,.prov-list button,select,input')].filter(e=>e.offsetParent).map(e=>(e.type==='checkbox'&&e.closest('label')||e).getBoundingClientRect()).filter(r=>r.width<24||r.height<24).length);
      assert.equal(small,0,'Touch targets under 24 px');
      const hit=await p.evaluate(()=>{const b=document.querySelector('button.matrix-cell.main,button.matrix-cell.sens');b.scrollIntoView({block:'center',inline:'center'});const r=b.getBoundingClientRect();
        return document.elementFromPoint(r.right+4,r.top+r.height/2)===b;});
      assert.ok(hit,'Matrix mark hit area must extend beyond the 14 px mark');
    }
    await p.context().close();
  }
  ok('no body overflow at 1440/1024/768/430/390 px; study drawer usable on phones; touch targets');

  assert.deepEqual(errors,[],'Page errors: '+errors.join(' | '));
  ok('no page or console errors');

  // ---------- 12. Graceful degradation without build metadata ----------
  const bare=await newPage();
  await bare.route('**/index.html*',async r=>{const resp=await r.fetch();const body=(await resp.text()).replace(/<script id="build-meta"[^<]*<\/script>/,'');await r.fulfill({response:resp,body});});
  await go(bare,'#overview');assert.ok((await bare.locator('#overview-provenance').textContent()).includes('no build record'));
  await bare.context().close();
  assert.deepEqual(errors,[],'Page errors without build metadata: '+errors.join(' | '));
  ok('without build metadata the page says so and still renders');

  await browser.close();if(server)server.close();
  console.log(`PASS v38 dashboard UI: ${passed} checks at ${BASE}`);
})().catch(e=>{console.error('FAIL',e.message);process.exit(1);});
