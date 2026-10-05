import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const ctx=await browser.newContext(); const page=await ctx.newPage(); const errors=[];
page.on('pageerror',e=>errors.push(String(e))); const checks=[];
try {
 for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
  await page.setViewportSize({width,height});await page.goto('http://127.0.0.1:4173');await page.waitForFunction(()=>typeof window.rebornSnapshot==='function');
  await page.screenshot({path:path.join(out,`kingdom-${width}x${height}.png`)});
  const survey=await page.evaluate(()=>{
   const r=e=>{const q=e.getBoundingClientRect();return{x:q.x,y:q.y,width:q.width,height:q.height,right:q.right,bottom:q.bottom};};
   const stage=r(document.getElementById('stage'));
   return{stage,sites:[...document.querySelectorAll('.plot')].map(e=>{const rect=r(e.querySelector('rect'));const poly=r(e.querySelector('polygon'));return{id:e.getAttribute('aria-label').split(':')[0],target:rect,footprint:poly,targetInside:rect.x>=stage.x&&rect.y>=stage.y&&rect.right<=stage.right&&rect.bottom<=stage.bottom};}),hall:r(document.querySelector('#world image')),frame:getComputedStyle(document.getElementById('frame')).transform};
  });
  const pick=[];
  for(const id of ['townhall','P03','P04','P05']){
   const site=survey.sites.find(s=>s.id===id);await page.mouse.click(site.target.x+site.target.width/2,site.target.y+site.target.height/2);
   pick.push({id,picked:await page.evaluate(()=>window.rebornPick?.site),selected:await page.locator('#selected').textContent()});
  }
  if(await page.locator('#context').getAttribute('aria-expanded')!=='true')await page.locator('#context').click();await page.screenshot({path:path.join(out,`kingdom-panel-${width}x${height}.png`)});
  checks.push({viewport:[width,height],survey,pick,panel:await page.locator('#panel').boundingBox()});
 }
 await page.setViewportSize({width:1280,height:720});
 await page.getByRole('button',{name:'Adventure',exact:true}).click();await page.screenshot({path:path.join(out,'adventure.png')});
 await page.getByRole('button',{name:'Hero',exact:true}).click();await page.screenshot({path:path.join(out,'hero.png')});
 await page.getByRole('button',{name:'Story',exact:true}).click();await page.screenshot({path:path.join(out,'story.png')});
 const story=await page.locator('#message').textContent();
 await page.getByRole('button',{name:'War',exact:true}).click();await page.getByRole('button',{name:'Campaign Siege',exact:true}).click();
 await page.waitForTimeout(1200);await page.screenshot({path:path.join(out,'defense-active.png')});
 await page.evaluate(()=>window.rebornBackground(true));const paused=await page.evaluate(()=>window.rebornSnapshot());
 await page.waitForTimeout(600);const pausedAfter=await page.evaluate(()=>window.rebornSnapshot());
 await page.reload();await page.waitForFunction(()=>typeof window.rebornSnapshot==='function');
 const reloaded=await page.evaluate(()=>({state:window.rebornSnapshot(),selected:document.getElementById('selected').textContent}));
 // Truly separate context: clearing an active page before unload can be overwritten by its pagehide autosave.
 const tacticalCtx=await browser.newContext({viewport:{width:1280,height:720}});const tacticalPage=await tacticalCtx.newPage();
 await tacticalPage.goto('http://127.0.0.1:4173');await tacticalPage.waitForFunction(()=>typeof window.rebornSnapshot==='function');
 await tacticalPage.getByRole('button',{name:'War',exact:true}).click();await tacticalPage.locator('#context').click();await tacticalPage.getByRole('button',{name:'Skirmish',exact:true}).click();
 const tacticalReady=await tacticalPage.locator('#selected').textContent();await tacticalPage.screenshot({path:path.join(out,'tactical.png')});await tacticalCtx.close();
 const fileCtx=await browser.newContext();const filePage=await fileCtx.newPage();const fileErrors=[];
 filePage.on('console',m=>{if(m.type()==='error')fileErrors.push(m.text());});filePage.on('pageerror',e=>fileErrors.push(String(e)));
 await filePage.goto('file:///C:/dev/ages-of-dominion-reborn/index.html');await filePage.waitForTimeout(500);
 const fileReady=await filePage.evaluate(()=>typeof window.rebornSnapshot==='function');await fileCtx.close();
 await fs.writeFile(path.join(out,'browser.json'),JSON.stringify({at:new Date().toISOString(),checks,errors,story,tacticalReady,backgroundDefense:{before:paused.defense.time,after:pausedAfter.defense.time,status:paused.defense.time===pausedAfter.defense.time?'PASS':'FAIL'},reload:{scene:reloaded.selected,defensePresent:!!reloaded.state.defense},fileScheme:{ready:fileReady,errors:fileErrors,scope:'Desktop Chrome architecture diagnostic only; Android WebView runtime UNVERIFIED'},scope:'Fresh root localhost browser; isolated context; no build/native/device/owner acceptance'},null,2));
 console.log(JSON.stringify({errors,sites:checks.map(c=>({viewport:c.viewport,clipped:c.survey.sites.filter(s=>!s.targetInside).map(s=>s.id),pick:c.pick})),fileReady,fileErrors}));
}finally{await ctx.close();await browser.close();}
