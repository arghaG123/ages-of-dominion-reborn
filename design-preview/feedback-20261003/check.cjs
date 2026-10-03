// Review gallery QA only. Never loads or executes the game implementation.
const { chromium } = require('C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const root = 'C:/dev/ages-of-dominion-reborn';
const base = 'http://127.0.0.1:4186/design-preview/feedback-20261003/';
const out = path.join(root,'qa/section-preview-20261003');
const digest = b => crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 await fs.mkdir(out,{recursive:true});
 const browser = await chromium.launch({headless:true,channel:'msedge'});
 const page = await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
 await page.goto(base,{waitUntil:'networkidle'});
 const catalogue=await page.evaluate(()=>window.reviewCatalogue);
 const samples=[];
 for(const s of catalogue){
   await page.selectOption('#section',s.id);
   await page.locator('#stage img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.complete?null:new Promise(r=>{im.onload=r;im.onerror=r}))));
   const health=await page.evaluate(()=>({bad:[...document.querySelectorAll('#stage img')].filter(im=>!im.complete||!im.naturalWidth).map(im=>im.src),overflow:document.documentElement.scrollWidth>innerWidth,title:document.querySelector('#title').textContent,stage:document.querySelector('#stage').getBoundingClientRect().toJSON()}));
   if(health.bad.length||health.overflow)errors.push(s.id+': '+JSON.stringify(health));
   samples.push({...s,health});
 }
 const captures=[['home',1440,1000],['kingdom-day1',933,780],['classes',1280,1000],['tactical',825,650],['market',1280,900],['skills',1280,900],['settings',375,900],['kingdom-stone-recovered',1280,720],['ui-resources-offense',1280,720]];
 const captureFiles=[];
 for(const [id,width,height] of captures){
   await page.setViewportSize({width,height});await page.selectOption('#section',id);
   await page.locator('#stage img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.complete?null:new Promise(r=>{im.onload=r;im.onerror=r}))));
   const file=id+'-'+width+'.png';await page.screenshot({path:path.join(out,file),fullPage:true});captureFiles.push(file);
   const checks=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,smallButtons:[...document.querySelectorAll('button,select')].filter(el=>el.getClientRects().length&&el.getBoundingClientRect().height<47.9).map(el=>el.textContent.trim()),title:document.querySelector('#title').textContent}));
   if(checks.overflow||checks.smallButtons.length)errors.push(id+'/'+width+': '+JSON.stringify(checks));
 }
 await page.setViewportSize({width:1280,height:900});
 await page.selectOption('#section','market');
 await page.getByRole('button',{name:'Needs changes',exact:true}).click();
 await page.locator('#comment').fill('QA roundtrip: sample feedback only');
 await page.reload({waitUntil:'networkidle'});await page.selectOption('#section','market');
 const restored=await page.locator('#comment').inputValue();
 if(restored!=='QA roundtrip: sample feedback only')errors.push('Feedback failed reload roundtrip');
 const downloaded=page.waitForEvent('download');await page.locator('#export').click();const download=await downloaded;
 await download.saveAs(path.join(out,'feedback-roundtrip-QA.json'));
 const exported=JSON.parse(await fs.readFile(path.join(out,'feedback-roundtrip-QA.json'),'utf8'));
 if(exported.sections.length!==catalogue.length||exported.sections.find(s=>s.id==='market').feedback.comment!==restored)errors.push('Export did not retain all sections/notes');
 if(!exported.sections.some(s=>s.id==='kingdom-stone-recovered')||!exported.sections.some(s=>s.id==='ui-resources-offense'))errors.push('Export dropped a recovered sample');
 const contractSizes=[[825,375],[933,424],[1180,820],[1280,720]];
 const contractCaptures=[];
 for(const id of ['kingdom-stone-recovered','ui-resources-offense']){
   for(const [width,height] of contractSizes){
     await page.setViewportSize({width,height});
     await page.selectOption('#section',id);
     await page.locator('#stage img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.complete?null:new Promise(r=>{im.onload=r;im.onerror=r}))));
     const file='contract-'+id+'-'+width+'x'+height+'.png';
     await page.screenshot({path:path.join(out,file)});
     const view=await page.evaluate(()=>{
       const img=document.querySelector('#stage img');
       const stage=document.querySelector('#stage');
       return {loaded:!!(img&&img.complete&&img.naturalWidth),natural:[img?img.naturalWidth:0,img?img.naturalHeight:0],stageOverflow:!!(stage&&stage.scrollWidth>stage.clientWidth+1),documentOverflow:document.documentElement.scrollWidth>innerWidth+1};
     });
     if(!view.loaded)errors.push(id+'/'+width+'x'+height+' sample image missing');
     contractCaptures.push({id,width,height,file,...view});
   }
 }
 // Clear only the isolated QA browser context. This does not touch the owner's browser.
 await page.evaluate(()=>localStorage.removeItem('aod-section-feedback-20261003-v1'));
 const manifest={version:1,createdAt:new Date().toISOString(),reviewOnly:true,samples:catalogue,assetReferences:[],counts:{samples:catalogue.length,appearanceReferences:catalogue.filter(s=>s.view.reference).length,layoutSamples:catalogue.filter(s=>s.view.layout).length},note:'Existing originals unchanged. Layout samples are review documentation, not game execution or production asset/composite acceptance.'};
 const assets=new Set();
 for(const s of catalogue){
  if(s.view.reference)assets.add(path.join(root,'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images',s.view.reference));
 }
 // Original references are hash-bound. Dynamic source artwork is additionally bound in the asset review ledger.
 for(const p of assets)manifest.assetReferences.push({file:path.relative(root,p).replaceAll('\\','/'),sha256:digest(await fs.readFile(p))});
 await fs.writeFile(path.join(root,'design-preview/feedback-20261003/preview-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 const report={at:new Date().toISOString(),status:errors.length?'FAIL':'PASS',samples:catalogue.length,checkedViews:samples.map(s=>({id:s.id,...s.health})),captures:captureFiles,contractCaptures,feedbackRoundtrip:restored==='QA roundtrip: sample feedback only',feedbackExportSections:exported.sections.length,errors,limitations:'Technical gallery checks only. A loaded image and the absence of stage overflow do not prove visual fidelity. Registration, matte, composite, runtime and owner acceptance remain separate.'};
 await fs.writeFile(path.join(out,'checks.json'),JSON.stringify(report,null,2)+'\n');
 await browser.close();console.log(JSON.stringify({status:report.status,counts:manifest.counts,errors,captures:captureFiles}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
