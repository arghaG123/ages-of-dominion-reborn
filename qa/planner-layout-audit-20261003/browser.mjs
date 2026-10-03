import {chromium} from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const out=fileURLToPath(new URL('./',import.meta.url));
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const report=[];
for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
 const page=await browser.newPage({viewport:{width,height}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file:///C:/dev/ages-of-dominion-reborn/design-preview/kingdom-layout-candidate.html?panel=1&fixture=1');
 await page.waitForSelector('svg image');
 const dims=await page.evaluate(()=>{const svg=document.querySelector('svg'),r=svg.getBoundingClientRect(),p=document.querySelector('#panel').getBoundingClientRect(),s=Math.min(r.width/1376,r.height/768),ox=(r.width-1376*s)/2,oy=(r.height-768*s)/2;return {rect:r.toJSON(),panel:p.toJSON(),scale:s,offset:[ox,oy],panelSourceX:(p.left-r.left-ox)/s,images:[...document.querySelectorAll('img')].map(i=>[i.complete,i.naturalWidth]),svgImageCount:document.querySelectorAll('svg image').length};});
 const sites=await page.evaluate(()=>{const c=globalThis.KINGDOM_CANDIDATE.candidate,[a,b,d,e,tx,ty]=c.camera;return c.geometry.sites.map(p=>{const [x,y,w,h]=p.rect;return {id:p.id,source:[a*(x+w/2)+d*(y+h/2)+tx,b*(x+w/2)+e*(y+h/2)+ty]};});});
 const hits=[];
 for(const s of sites){const [x,y]=s.source;await page.mouse.click(dims.rect.left+dims.offset[0]+x*dims.scale,dims.rect.top+dims.offset[1]+y*dims.scale);const hit=await page.evaluate(()=>window.candidatePick);hits.push({expected:s.id,actual:hit?.site});}
 const before=await page.evaluate(()=>window.candidatePick);
 await page.mouse.click(dims.panel.left+20,dims.panel.top+30);
 const panelBlocked=JSON.stringify(before)===JSON.stringify(await page.evaluate(()=>window.candidatePick));
 await page.screenshot({path:out+`${width}x${height}-panel-fixture.png`});
 await page.locator('#context').click();
 await page.screenshot({path:out+`${width}x${height}-fixture.png`});
 let letterboxMiss=null;
 if(dims.offset[0]>5||dims.offset[1]>5){await page.mouse.click(dims.rect.left+2,dims.rect.top+2);letterboxMiss=(await page.evaluate(()=>window.candidatePick))?.site===null;}
 if(width===825){await page.setViewportSize({width:1280,height:720});await page.locator('[data-view="compare"]').click();const pane=page.locator('.pane').nth(1);const r=await pane.boundingBox(),s=Math.min(r.width/1376,r.height/768),ox=(r.width-1376*s)/2,oy=(r.height-768*s)/2;const p=sites.find(i=>i.id==='P01').source;await page.mouse.click(r.x+ox+p[0]*s,r.y+oy+p[1]*s);report.push({compareResizePick:await page.evaluate(()=>window.candidatePick)});}
 report.push({viewport:[width,height],dims,hits,panelBlocked,letterboxMiss,errors});await page.close();
}
await browser.close();await writeFile(out+'browser-checks.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.map(r=>r.viewport?{viewport:r.viewport,stage:[r.dims.rect.width,r.dims.rect.height],panelSourceX:r.dims.panelSourceX,hits:r.hits.filter(p=>p.expected!==p.actual),panelBlocked:r.panelBlocked,letterboxMiss:r.letterboxMiss,errors:r.errors}:r),null,2));
