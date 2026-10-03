// Scoped isolated gallery audit. Does not run game code or alter owner browser data.
const {chromium}=require('C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs/promises');
const path=require('node:path');
const out=__dirname;
const base='http://127.0.0.1:4186/design-preview/feedback-20261003/';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const context=await browser.newContext({viewport:{width:1280,height:720}});
 const page=await context.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 await page.goto(base,{waitUntil:'networkidle'});
 const catalogue=await page.evaluate(()=>window.reviewCatalogue);
 const old=catalogue.filter(s=>!['kingdom-stone-recovered','ui-resources-offense'].includes(s.id));
 const feedback=Object.fromEntries(old.map((s,i)=>[s.id,{decision:i%2?'revise':'keep',comment:`Isolated verifier fixture ${s.id}`,updatedAt:'2026-10-03T00:00:00Z'}]));
 const key='aod-section-feedback-20261003-v1';
 await page.evaluate(({key,feedback})=>localStorage.setItem(key,JSON.stringify(feedback)),{key,feedback});
 await page.reload({waitUntil:'networkidle'});
 await page.selectOption('#section','kingdom-stone-recovered');
 await page.locator('#comment').fill('Isolated verifier fixture new section');
 await page.reload({waitUntil:'networkidle'});
 const preserved=await page.evaluate(({key,feedback})=>{const actual=JSON.parse(localStorage.getItem(key));return Object.keys(feedback).every(id=>JSON.stringify(actual[id])===JSON.stringify(feedback[id]))},{key,feedback});
 const downloadEvent=page.waitForEvent('download'); await page.locator('#export').click();const download=await downloadEvent;
 await download.saveAs(path.join(out,'isolated-feedback-fixture.json'));
 const exported=JSON.parse(await fs.readFile(path.join(out,'isolated-feedback-fixture.json'),'utf8'));
 const results=[];
 for(const id of ['kingdom-stone-recovered','ui-resources-offense']){
  for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
   await page.setViewportSize({width,height});
   await page.goto(base+'?focus=1#'+id,{waitUntil:'networkidle'});
   await page.locator('#stage img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.decode())));
   const view=await page.evaluate(()=>{const stage=document.querySelector('#stage'),im=stage.querySelector('img'),rect=stage.getBoundingClientRect();return {selected:document.querySelector('#section').value,stage:rect.toJSON(),natural:[im.naturalWidth,im.naturalHeight],src:im.getAttribute('src'),loaded:im.complete&&im.naturalWidth>0,overflow:document.documentElement.scrollWidth>innerWidth,effective18pxIcon:im.naturalWidth===1280?18*Math.min(rect.width/im.naturalWidth,rect.height/im.naturalHeight):null}});
   const file=`gallery-focus-${id}-${width}x${height}.png`;await page.screenshot({path:path.join(out,file)});results.push({id,width,height,file,...view});
  }
 }
 const manifest=JSON.parse(await fs.readFile('C:/dev/ages-of-dominion-reborn/design-preview/feedback-20261003/preview-manifest.json','utf8'));
 const report={scope:'Two recovery sections only; new isolated context; QA feedback is not owner feedback',catalogueCount:catalogue.length,oldSectionCount:old.length,uniqueIds:new Set(catalogue.map(s=>s.id)).size,manifestCatalogueMatch:JSON.stringify(catalogue.map(s=>s.id))===JSON.stringify(manifest.samples.map(s=>s.id)),oldFixtureFeedbackPreserved:preserved,exportCount:exported.sections.length,exportOldFixturePreserved:old.every(s=>JSON.stringify(exported.sections.find(x=>x.id===s.id)?.feedback)===JSON.stringify(feedback[s.id])),results,errors};
 await fs.writeFile(path.join(out,'gallery.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));await context.close();await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
