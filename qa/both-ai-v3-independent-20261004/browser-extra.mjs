import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
const out='C:/dev/ages-of-dominion-reborn/qa/both-ai-v3-independent-20261004';
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const results=[];
for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:4173/');
  await page.click('#context');await page.click('[data-choice="new-campaign"]');await page.click('[data-choice="class:mage"]');
  if(!(await page.locator('#panel').evaluate(n=>n.classList.contains('open'))))await page.click('#context');
  const hero=await page.evaluate(()=>{
    const card=document.querySelector('[data-presentation="portrait-card"] image').getBoundingClientRect();
    const stage=document.querySelector('#stage').getBoundingClientRect();
    const panel=document.querySelector('#panel').getBoundingClientRect();
    return {card:{x:card.x,y:card.y,right:card.right,bottom:card.bottom},stage:{x:stage.x,y:stage.y,right:stage.right,bottom:stage.bottom},panelLeft:panel.left,insideStage:card.top>=stage.top&&card.bottom<=stage.bottom,clearOfPanel:card.right<=panel.left};
  });
  await page.screenshot({path:path.join(out,`browser-extra-${width}x${height}-hero-panel.png`)});
  await page.click('[data-choice="enter-valley"]');
  const panelOpen=await page.locator('#panel').evaluate(n=>n.classList.contains('open'));if(!panelOpen)await page.click('#context');
  const plots=await page.evaluate(()=>{
    const s=document.querySelector('#stage').getBoundingClientRect(),p=document.querySelector('#panel').getBoundingClientRect();
    return [...document.querySelectorAll('.plot')].map(n=>{
      const box=n.querySelector('rect[fill="transparent"]').getBoundingClientRect();const x=(box.left+box.right)/2,y=(box.top+box.bottom)/2;
      const picked=document.elementFromPoint(x,y)?.closest('.plot')?.getAttribute('aria-label');
      return {id:n.getAttribute('aria-label'),width:box.width,height:box.height,x,y,insideStage:box.left>=s.left&&box.right<=s.right&&box.top>=s.top&&box.bottom<=s.bottom,clearOfPanel:box.right<=p.left,picked};
    });
  });
  await page.screenshot({path:path.join(out,`browser-extra-${width}x${height}-kingdom-panel.png`)});
  results.push({width,height,hero,plots,errors});await context.close();
}
await browser.close();await writeFile(path.join(out,'browser-extra-results.json'),JSON.stringify(results,null,2));
console.log(JSON.stringify(results.map(r=>({width:r.width,height:r.height,hero:r.hero,plotCount:r.plots.length,shortTargets:r.plots.filter(p=>p.width<47.5||p.height<47.5),clipped:r.plots.filter(p=>!p.insideStage||!p.clearOfPanel),wrongCenterPicks:r.plots.filter(p=>p.id!==p.picked),errors:r.errors})),null,2));
