// Planner fixture-only visual survey. Does not prove earned age progression.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import { newCampaign } from '../../src/core/campaign.js';
import { encode, SAVE_KEY, VIEW_KEY } from '../../src/core/save.js';
const root='C:/dev/ages-of-dominion-reborn', out=root+'/qa/planner-three-ai-20261006/ages-size', port=4366;
await mkdir(out,{recursive:true});
const server=spawn(process.execPath,['scripts/serve.mjs','--port',String(port)],{cwd:root,stdio:['ignore','pipe','pipe']});
const report={stateKind:'FIXTURE',setup:'Age, Armory, developed plots and ample resources injected; does not prove campaign progression.',rows:[],errors:[]};
let browser;
try {
 await new Promise(resolve=>setTimeout(resolve,500));
 browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 for(let age=4;age<8;age+=3){
  const c=newCampaign(contract,data,Date.now(),20261006); c.age=age;
  for(const k of Object.keys(c.resources)) c.resources[k]=500000;
  c.plots[0].level=8;
  const types=['farm','lumber','quarry','mine','barracks','workshop','hall','armory'];
  for(let i=0;i<types.length;i++){c.plots[i+1].type=types[i];c.plots[i+1].level=2;}
  for(const stack of c.army) stack.age=age;
  const context=await browser.newContext({viewport:{width:1280,height:720}});
  await context.addInitScript(({save,saveKey,viewKey})=>{localStorage.setItem(saveKey,save);localStorage.setItem(viewKey,'kingdom');},{save:encode(c,data),saveKey:SAVE_KEY,viewKey:VIEW_KEY});
  const page=await context.newPage(); page.on('pageerror',e=>report.errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${port}`);
  for(const screen of ['army']){
   if(screen!=='kingdom'){
    const nav=page.locator(`[data-choice="nav:${screen}"]`);
    if(await nav.getAttribute('data-nav')==='more'){
     const more=page.locator('[data-choice="nav-more"]');if(await more.innerText()!=='Fewer') await more.click();
    }
    await nav.click();
   }
   await page.waitForTimeout(750);
   await page.evaluate(async()=>{await Promise.all([...document.images].map(im=>im.decode().catch(()=>{})));});
   const file=`${out}/${age}-${screen}.png`; await page.screenshot({path:file});
   const dom=await page.evaluate(()=>({view:document.querySelector('#app').dataset.view,terrain:{src:document.querySelector('#terrain').getAttribute('src'),hidden:document.querySelector('#terrain').hidden,loaded:document.querySelector('#terrain').complete,naturalWidth:document.querySelector('#terrain').naturalWidth},figures:[...document.querySelectorAll('#world image')].map(n=>({href:n.getAttribute('href'),height:n.getAttribute('height'),cssBox:n.getBoundingClientRect().toJSON()}))}));
   report.rows.push({age,screen,path:file,sha256:createHash('sha256').update(await readFile(file)).digest('hex'),...dom});
  }
  await context.close();
 }
}catch(e){report.errors.push(String(e.stack||e));}finally{await browser?.close();server.kill();await writeFile(out+'/report.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify({rows:report.rows.length,errors:report.errors}));
