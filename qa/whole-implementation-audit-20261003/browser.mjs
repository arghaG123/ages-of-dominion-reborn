import {chromium} from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const out=new URL('./',import.meta.url);
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const context=await browser.newContext({viewport:{width:1280,height:720}});
const page=await context.newPage();const errors=[]; const failed=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
await page.goto('http://127.0.0.1:4173');await page.waitForFunction(()=>typeof window.rebornSnapshot==='function');
const screens=['kingdom','adventure','hero','army','forge','market','tactical','defense','story','war','settings','home'];
const surfaces=[];
for(const screen of screens){
await page.locator('#nav').getByRole('button',{name:screen[0].toUpperCase()+screen.slice(1),exact:true}).click();
await page.evaluate(()=>{if(!document.querySelector('#panel').classList.contains('open'))document.querySelector('#context').click();});
surfaces.push(await page.evaluate(()=>({screen:document.querySelector('#nav [aria-current]').textContent,heading:document.querySelector('#selected').textContent,choices:[...document.querySelectorAll('#choices button')].map(x=>x.textContent),message:document.querySelector('#message').textContent,terrain:document.querySelector('#terrain').hidden?null:document.querySelector('#terrain').getAttribute('src'),svgImages:document.querySelectorAll('#world image').length,overflow:document.documentElement.scrollWidth>innerWidth})));
await page.screenshot({path:new URL(`ui-${screen}.png`,out).pathname.replace(/^\/(\w:)/,'$1')});
}
await page.getByRole('button',{name:'Continue',exact:true}).click();
const continueResult=await page.locator('#selected').textContent();
const viewports=[];
await page.locator('#nav').getByRole('button',{name:'Kingdom',exact:true}).click();
for(const [width,height] of [[825,375],[933,424],[1180,820],[1280,720]]){
await page.setViewportSize({width,height});
const metrics=await page.evaluate(()=>({stage:document.querySelector('#stage').getBoundingClientRect().toJSON(),header:document.querySelector('header').getBoundingClientRect().toJSON(),footer:document.querySelector('footer').getBoundingClientRect().toJSON(),resourceImages:[...document.querySelectorAll('#resources img')].map(x=>({width:x.width,height:x.height})),overflow:document.documentElement.scrollWidth>innerWidth}));
viewports.push({viewport:[width,height],...metrics});
await page.screenshot({path:new URL(`kingdom-${width}x${height}.png`,out).pathname.replace(/^\/(\w:)/,'$1')});
}
const damaged=await browser.newContext({viewport:{width:1280,height:720}});
await damaged.addInitScript(()=>localStorage.setItem('aod-reborn-v1','broken-save'));
const dp=await damaged.newPage();await dp.goto('http://127.0.0.1:4173');await dp.waitForFunction(()=>typeof window.rebornSnapshot==='function');
await dp.getByRole('button',{name:'Actions',exact:true}).click();
await dp.getByRole('button',{name:'New campaign',exact:true}).click();
const before=await dp.evaluate(()=>window.rebornSnapshot().clock);
await dp.waitForTimeout(1200);
const after=await dp.evaluate(()=>window.rebornSnapshot().clock);
await fs.writeFile(new URL('browser-checks.json',out),JSON.stringify({errors,failed,surfaces,viewports,homeContinueHeading:continueResult,damagedNewCampaignClock:{before,after,ticks:after>before},scope:'Isolated browser contexts. No user save touched. No build/native/device test.'},null,2)+'\n');
await browser.close();console.log(JSON.stringify({errors,failed,homeContinueHeading:continueResult,damagedNewCampaignTicks:after>before,surfaces:surfaces.length}));
