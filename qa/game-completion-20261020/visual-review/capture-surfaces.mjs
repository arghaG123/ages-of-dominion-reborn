import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/surfaces');
await fs.mkdir(out, { recursive: true });
const sizes = [{name:'1280x720',width:1280,height:720},{name:'1180x820',width:1180,height:820},{name:'933x424',width:933,height:424},{name:'825x375',width:825,height:375}];
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const report = {recordedAt:new Date().toISOString(),url:'http://127.0.0.1:4179/',surfaces:[],errors:[],controlHitFailures:[]};
for (const size of sizes) {
  const context = await browser.newContext({viewport:{width:size.width,height:size.height},deviceScaleFactor:1});
  const page = await context.newPage();
  page.on('pageerror', e => report.errors.push({size:size.name,error:String(e)}));
  page.on('console', m => { if(m.type()==='error') report.errors.push({size:size.name,error:m.text()}); });
  await page.goto(report.url,{waitUntil:'networkidle'});
  const snap = async (name) => {
    await page.waitForTimeout(120);
    const file = path.join(out, name + '-' + size.name + '.png');
    await page.screenshot({path:file,fullPage:false});
    const info = await page.evaluate(() => ({
      view:document.querySelector('#app')?.dataset.view || 'home',
      title:document.title,
      scroll:{body:[document.body.scrollWidth,document.body.scrollHeight],panel:document.querySelector('#panel')?[document.querySelector('#panel').scrollWidth,document.querySelector('#panel').scrollHeight,document.querySelector('#panel').clientWidth,document.querySelector('#panel').clientHeight]:null},
      controls:[...document.querySelectorAll('button[data-choice]')].filter(b=>b.getClientRects().length).map(b=>{
        const r=b.getBoundingClientRect();
        const x=r.left+r.width/2, y=r.top+r.height/2;
        const hit=document.elementFromPoint(x,y);
        const owner=hit?.closest('button[data-choice]')?.dataset.choice||null;
        const visible=r.width>0&&r.height>0&&x>=0&&x<=innerWidth&&y>=0&&y<=innerHeight&&getComputedStyle(b).visibility!=='hidden';
        const clippedBy=[];
        for(let a=b.parentElement;a&&a!==document.body;a=a.parentElement){
          const s=getComputedStyle(a), ar=a.getBoundingClientRect();
          const clipsX=['hidden','clip','auto','scroll'].includes(s.overflowX);
          const clipsY=['hidden','clip','auto','scroll'].includes(s.overflowY);
          if((clipsX&&(r.left<ar.left||r.right>ar.right))||(clipsY&&(r.top<ar.top||r.bottom>ar.bottom)))clippedBy.push(a.id||a.className||a.tagName.toLowerCase());
        }
        const fullyInViewport=r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;
        const panel=document.querySelector('#panel.open'),pr=panel?.getBoundingClientRect();
        const occludedByPanel=Boolean(panel&&!panel.contains(b)&&x>=pr.left&&x<=pr.right&&y>=pr.top&&y<=pr.bottom&&panel.contains(hit));
        const fullyExposed=visible&&fullyInViewport&&clippedBy.length===0&&!occludedByPanel;
        return {choice:b.dataset.choice,label:b.getAttribute('aria-label')||b.innerText.trim(),disabled:b.disabled,visible,fullyExposed,clippedBy,occludedByPanel,centerOwned:owner===b.dataset.choice,centerOwner:owner,rect:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]};
      })
    }));
    const failed = info.controls.filter(control=>control.fullyExposed&&!control.centerOwned);
    if (failed.length) report.controlHitFailures.push({name,size:size.name,controls:failed});
    report.surfaces.push({name,size:size.name,file:path.relative(root,file),...info});
  };
  await snap('home');
  await page.locator('[data-choice="new-campaign"]').click();
  await snap('class-select');
  const classChoices = await page.locator('[data-choice^="scene-class:"]').evaluateAll(nodes => nodes.map(node => node.dataset.choice));
  if (classChoices.length !== 8) report.errors.push({size:size.name,error:`Expected 8 class portraits, found ${classChoices.length}`});
  for (const choice of classChoices) {
    const classId = choice.slice('scene-class:'.length);
    const portrait = page.locator(`[data-choice="${choice}"]`);
    await portrait.click();
    if (await portrait.getAttribute('aria-current') !== 'true') report.errors.push({size:size.name,error:`${classId} portrait did not select from its center hit target`});
    await snap(`class-preview-${classId}`);
  }
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForTimeout(220);
  await snap('kingdom');
  for (const route of ['adventure','hero','army','war']) {
    await page.locator('[data-choice="nav:' + route + '"]').click();
    await snap(route);
    if (route === 'hero') {
      await page.locator('[data-choice="inspect:hero"]').click();
      await snap('hero-skills');
      await page.locator('#panel').evaluate(panel => { panel.scrollTop = panel.scrollHeight; });
      await snap('hero-skills-bottom');
      await page.locator('[data-choice="hero-tab:spells"]').click();
      await page.locator('#panel').evaluate(panel => { panel.scrollTop = 0; });
      await snap('hero-spellbook');
      await page.locator('#panel').evaluate(panel => { panel.scrollTop = panel.scrollHeight; });
      await snap('hero-spellbook-bottom');
      await page.locator('#panel-close').click();
    }
    const contextButton = page.locator('#context');
    if (await contextButton.count()) {
      await contextButton.click();
      await snap(route + '-controls');
      await contextButton.click();
    }
  }
  // Supporting destinations reachable from the compact menu.
  for (const route of ['forge','market','story','settings','help','home']) {
    const isOpen = await page.locator('#panel.open').count();
    if (!isOpen) await page.locator('#context').click();
    const key = 'menu:' + route;
    if (await page.locator('[data-choice="' + key + '"]').count()) {
      await page.locator('[data-choice="' + key + '"]').click();
      await snap(route);
    } else {
      report.errors.push({size:size.name,error:'missing menu route ' + key});
    }
  }
  await context.close();
}
await browser.close();
await fs.writeFile(path.join(out,'surface-review.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({surfaces:report.surfaces.length,errors:report.errors,controlHitFailures:report.controlHitFailures,files:report.surfaces.map(s=>s.file)},null,2));
