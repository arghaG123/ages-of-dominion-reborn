// Independent isolated browser verification. No source edits, build or owner save access.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const root='C:/dev/ages-of-dominion-reborn';
const output=path.join(root,'output/playwright/planner-verification-20261005');
const qa=path.join(root,'qa/planner-verification-20261005');
await mkdir(output,{recursive:true});
const server=spawn(process.execPath,['scripts/serve.mjs','--port','4209'],{cwd:root,stdio:['ignore','pipe','pipe']});
let log=''; server.stdout.on('data',b=>log+=b); server.stderr.on('data',b=>log+=b);
let browser;
const report={evidenceType:'fresh isolated browser; Skirmish ordinary controls; Forge fixture explicitly injected into this isolated context',errors:[],checks:[]};
try{
  for(let i=0;i<50;i++){if(log.includes('Reborn local preview'))break;if(server.exitCode!==null)throw Error(log);await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context=await browser.newContext({viewport:{width:825,height:375}});
  let page=await context.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.goto('http://127.0.0.1:4209');
  await page.locator('[data-choice="new-campaign"]').first().click();
  await page.locator('[data-choice="class:ranger"]').first().click();
  await page.locator('[data-choice="enter-valley"]').first().click();
  await page.locator('#context').click();
  await page.screenshot({path:path.join(output,'kingdom.png')});
  await page.locator('[data-choice="nav:war"]').click();
  await page.getByRole('button',{name:'Skirmish',exact:true}).first().click();
  await page.waitForTimeout(350);
  report.tacticalDOM=await page.locator('body').ariaSnapshot();
  report.tacticalLabelMetrics=await page.locator('#world text').evaluateAll(ns=>ns.map(n=>({text:n.textContent,fontSize:getComputedStyle(n).fontSize,screenScale:n.getScreenCTM().a,box:n.getBoundingClientRect().toJSON()})));
  const targets=await page.locator('[data-cell]').evaluateAll(nodes=>nodes.map(n=>({cell:n.dataset.cell,clickHandler:typeof n.onclick,fill:n.getAttribute('fill'),box:n.getBoundingClientRect().toJSON()})));
  const open=targets.find(n=>n.fill==='#70b9c555');
  const before=await page.evaluate(()=>window.rebornSnapshot());
  if(!open)throw Error('No legal move highlight');
  await page.mouse.click(open.box.x+open.box.width/2,open.box.y+open.box.height/2);
  await page.waitForTimeout(100);
  const after=await page.evaluate(()=>window.rebornSnapshot());
  report.checks.push({id:'tactical-map-move',cell:open.cell,handlersAfterAnimation:targets.filter(n=>n.clickHandler==='function').length,stacksUnchanged:JSON.stringify(before.battle.stacks)===JSON.stringify(after.battle.stacks),beforeRevision:before.revision,afterRevision:after.revision,beforeStacks:before.battle.stacks,afterStacks:after.battle.stacks});
  await page.locator('#choices [data-choice^="move:"]').first().click();
  report.checks.push({id:'tactical-panel-move',beforeRevision:after.revision,afterRevision:(await page.evaluate(()=>window.rebornSnapshot())).revision});
  await page.screenshot({path:path.join(output,'tactical.png')});
  let dialogs=0; page.on('dialog',async d=>{dialogs++;await d.dismiss();});
  await page.locator('#dock [data-choice="retreat"]').click();
  report.checks.push({id:'retreat-first-click',dialogs,state:(await page.evaluate(()=>window.rebornSnapshot())).battle,message:await page.locator('#message').textContent(),buttons:await page.locator('#choices button,#dock button').allTextContents()});

  // Isolated fixture solely to verify the new Forge comparison and confirmation.
  report.fixture=await page.evaluate(async()=>{
    const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});
    const {newCampaign,command,heroStats}=await import('/src/core/campaign.js');
    const {encode,SAVE_KEY,VIEW_KEY}=await import('/src/core/save.js');
    const {default:contract}=await import('/src/data/implementation-contract.json',{with:{type:'json'}});
    let s=newCampaign(contract,data,Date.now(),123456789);
    const slot=s.plots.find(x=>x.id!=='townhall');slot.type='armory';slot.level=1;
    s=command(s,{id:'audit-forge',type:'FORGE',payload:{slot:'weapon',quality:0}},Date.now(),data);
    return {kind:'INJECTED_ARMORY_FIXTURE',stats:heroStats(s,data),inventory:s.inventory,encoded:encode(s,data),saveKey:SAVE_KEY,viewKey:VIEW_KEY};
  });
  const fixtureContext=await browser.newContext({viewport:{width:825,height:375}});
  await fixtureContext.addInitScript(f=>{if(!localStorage.getItem(f.saveKey)){localStorage.setItem(f.saveKey,f.encoded);localStorage.setItem(f.viewKey,'forge');}},report.fixture);
  page=await fixtureContext.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.goto('http://127.0.0.1:4209');
  if(!(await page.locator('#panel').evaluate(n=>n.classList.contains('open'))))await page.locator('#context').click();
  await page.locator('#choices [data-choice^="equip:"]').first().click();
  const compare=await page.evaluate(()=>({state:window.rebornSnapshot(),message:document.querySelector('#message').textContent,messageBox:document.querySelector('#message').getBoundingClientRect().toJSON(),panelBox:document.querySelector('#panel').getBoundingClientRect().toJSON()}));
  await page.screenshot({path:path.join(output,'forge-compare.png')});
  await page.locator('#choices [data-choice^="equip-confirm:"]').first().click();
  const equipped=await page.evaluate(()=>window.rebornSnapshot());
  await page.reload();
  const reload=await page.evaluate(()=>window.rebornSnapshot());
  const statsAfter=await page.evaluate(async()=>{const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});const {heroStats}=await import('/src/core/campaign.js');return heroStats(window.rebornSnapshot(),data);});
  report.checks.push({id:'forge-compare-confirm',message:compare.message,messageBox:compare.messageBox,panelBox:compare.panelBox,statsAfter,equipBeforeConfirm:compare.state.hero.equip.weapon,equipAfter:equipped.hero.equip.weapon,equipReload:reload.hero.equip.weapon});
}catch(e){report.errors.push(String(e.stack||e));}
finally{await browser?.close();server.kill();report.serverLog=log;await writeFile(path.join(qa,'browser-report.json'),JSON.stringify(report,null,2));}
console.log(JSON.stringify({errors:report.errors,checks:report.checks.map(({id,...x})=>({id,...(id==='tactical-map-move'?{handlers:x.handlersAfterAnimation,before:x.beforeRevision,after:x.afterRevision}:id==='retreat-first-click'?{dialogs:x.dialogs,status:x.state?.status,winner:x.state?.winner,buttons:x.buttons}:x)}))},null,2));
