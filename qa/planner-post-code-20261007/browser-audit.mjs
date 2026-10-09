import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {mkdir,writeFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
const out='C:/dev/ages-of-dominion-reborn/qa/planner-post-code-20261007';
await mkdir(out+'/pixels',{recursive:true});
const report={type:'FRESH_ISOLATED_BROWSER',origin:'http://127.0.0.1:4427',errors:[],checks:[],captures:[],journey:'Natural new campaign/class selection/Skirmish; age layouts below are FIXTURE, no earned campaign claim'};
const server=spawn(process.execPath,['scripts/serve.mjs','--port','4427'],{cwd:'C:/dev/ages-of-dominion-reborn',stdio:['ignore','pipe','pipe']});
let serverLog='';server.stdout.on('data',c=>serverLog+=c);server.stderr.on('data',c=>serverLog+=c);
for(let n=0;n<50&&!serverLog.includes('Reborn local preview');n++)await new Promise(r=>setTimeout(r,100));
const browser=await chromium.launch({headless:true,args:['--no-proxy-server'],executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const context=await browser.newContext({viewport:{width:1280,height:720}});const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
const check=(id,pass,detail)=>report.checks.push({id,pass,detail});
async function ready(){await page.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await Promise.all([...document.querySelectorAll('svg image')].map(n=>new Promise(resolve=>{const i=new Image();i.onload=resolve;i.onerror=resolve;i.src=n.getAttribute('href');})));});}
async function shot(id,type='NATURAL'){await ready();await page.screenshot({path:out+'/pixels/'+id+'.png'});report.captures.push({id,type,viewport:page.viewportSize()});}
async function nav(name){await page.locator('#nav-more').count().then(async n=>{if(n){} });const target=page.locator('[data-choice="nav:'+name+'"]');if(!await target.isVisible())await page.locator('[data-choice="nav-more"]').click();await target.click();}
try{
 await page.goto(report.origin);await shot('home-1280');
 await page.locator('[data-choice="new-campaign"]').first().click();await shot('class-selection');
 await page.locator('[data-choice="class:ranger"]').first().click();await page.locator('[data-choice="enter-valley"]').first().click();await shot('kingdom-day1');
 check('natural-day1-sparse',await page.evaluate(()=>{const s=window.rebornSnapshot();return s.age===0&&s.plots.filter(p=>p.type===null).length===17&&s.walls.level===0;}));
 for(const name of ['adventure','hero','army','forge','market','story','settings','help','war']){await nav(name);await shot(name);}
 if(!await page.locator('#panel').evaluate(n=>n.classList.contains('open')))await page.locator('#context').click();
 await page.getByRole('button',{name:'Skirmish',exact:true}).first().click();await page.waitForTimeout(300);await shot('tactical');
 const labels=await page.evaluate(()=>[...document.querySelectorAll('#labels span')].map(n=>({text:n.textContent,size:parseFloat(getComputedStyle(n).fontSize)})));
 check('tactical-labels',labels.length>0&&labels.every(x=>x.size>=14),labels);
 const before=await page.evaluate(()=>window.rebornActions.length);
 const retreat=page.locator('#dock [data-choice="retreat"]');await retreat.click();
 check('retreat-opens-without-action',await page.evaluate(before=>!document.querySelector('#retreat').hidden&&window.rebornActions.length===before,before),{before});
 const inert=await page.evaluate(()=>['stage-field','world','terrain','panel','nav','dock','context','save'].map(id=>({id,inert:!!document.getElementById(id).closest('[inert]')})));
 check('retreat-inert',inert.every(x=>x.inert),inert);await page.keyboard.press('Tab');check('retreat-tab-contained',await page.evaluate(()=>['retreat-confirm','retreat-cancel'].includes(document.activeElement.id)));
 await page.locator('#retreat-cancel').click();const focus=await page.evaluate(()=>({id:document.activeElement.id,choice:document.activeElement.dataset.choice,hidden:document.querySelector('#retreat').hidden,actions:window.rebornActions.length}));
 check('retreat-cancel-focus-return',focus.choice==='retreat',focus);check('retreat-cancel-no-action',focus.hidden&&focus.actions===before,focus);
 await retreat.click();await page.keyboard.press('Escape');check('retreat-escape-focus-return',await page.evaluate(()=>document.activeElement.dataset.choice==='retreat'));
 await retreat.click();await page.locator('#retreat-confirm').click();check('retreat-confirm-once',await page.evaluate(()=>window.rebornActions.filter(x=>x.action==='retreat').length===1));
 const portraitBefore=await page.evaluate(()=>JSON.stringify({hero:window.rebornSnapshot().hero,army:window.rebornSnapshot().army}));await page.setViewportSize({width:375,height:825});await shot('portrait-rotate');await page.setViewportSize({width:1280,height:720});
 check('portrait-state-preserved',await page.evaluate(v=>JSON.stringify({hero:window.rebornSnapshot().hero,army:window.rebornSnapshot().army})===v,portraitBefore));
 // Explicit accelerated fixture covers all ages; no grant enters the natural context.
 const seeded=await page.evaluate(async()=>{const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});const {default:contract}=await import('/src/data/implementation-contract.json',{with:{type:'json'}});const {newCampaign}=await import('/src/core/campaign.js');const {encode,SAVE_KEY,VIEW_KEY}=await import('/src/core/save.js');return {data,contract,SAVE_KEY,VIEW_KEY};});
 for(let age=0;age<8;age++){
  const fctx=await browser.newContext({viewport:{width:825,height:375}});const fp=await fctx.newPage();await fp.goto(report.origin);
  await fp.evaluate(async({age})=>{const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});const {default:contract}=await import('/src/data/implementation-contract.json',{with:{type:'json'}});const {newCampaign}=await import('/src/core/campaign.js');const {encode,SAVE_KEY,VIEW_KEY}=await import('/src/core/save.js');const s=newCampaign(contract,data,Date.now(),246813579);s.age=age;s.tutorial.skipped=true;const barracks=s.plots.find(p=>p.id==='P01');barracks.type='barracks';barracks.level=1;s.army=['melee','ranged','heavy'].map((type,i)=>({id:'army-'+i,kind:'role',type,age,count:10,rank:0,xp:0}));localStorage.setItem(SAVE_KEY,encode(s,data));localStorage.setItem(VIEW_KEY,'army');},{age});
  await fp.reload();await fp.evaluate(async()=>{await Promise.all([...document.querySelectorAll('svg image')].map(n=>new Promise(resolve=>{const i=new Image();i.onload=resolve;i.onerror=resolve;i.src=n.getAttribute('href');})));});
  const plates=await fp.locator('[data-plate]').evaluateAll(ns=>ns.map(n=>{const b=n.getBoundingClientRect();return {path:n.dataset.plate,width:b.width,height:b.height,parentHeight:n.parentElement.dataset.plateHeight};}));report.checks.push({id:'army-fixture-size-age-'+age,pass:null,detail:plates});
  await fp.screenshot({path:out+'/pixels/army-age-'+age+'.png'});report.captures.push({id:'army-age-'+age,type:'FIXTURE',viewport:[825,375]});await fctx.close();
 }
}catch(e){report.errors.push(e.stack||String(e));}finally{await context.close();await browser.close();server.kill();report.serverLog=serverLog;await writeFile(out+'/browser-report.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify({errors:report.errors,checks:report.checks.filter(x=>x.pass!==null),captures:report.captures.length},null,2));

