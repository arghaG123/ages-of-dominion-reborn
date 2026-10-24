import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261019/visual-review/surfaces');
await fs.mkdir(out, { recursive: true });
const sizes = [{name:'1280x720',width:1280,height:720},{name:'825x375',width:825,height:375}];
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const report = {recordedAt:new Date().toISOString(),url:'http://127.0.0.1:4179/',surfaces:[],errors:[]};
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
      controls:[...document.querySelectorAll('button[data-choice]')].filter(b=>b.getClientRects().length).map(b=>({choice:b.dataset.choice,label:b.getAttribute('aria-label')||b.innerText.trim(),disabled:b.disabled,rect:(()=>{const r=b.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]})()}))
    }));
    report.surfaces.push({name,size:size.name,file:path.relative(root,file),...info});
  };
  await snap('home');
  await page.locator('[data-choice="new-campaign"]').click();
  await snap('class-select');
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForTimeout(220);
  await snap('kingdom');
  for (const route of ['adventure','hero','army','war']) {
    await page.locator('[data-choice="nav:' + route + '"]').click();
    await snap(route);
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
console.log(JSON.stringify({surfaces:report.surfaces.length,errors:report.errors,files:report.surfaces.map(s=>s.file)},null,2));