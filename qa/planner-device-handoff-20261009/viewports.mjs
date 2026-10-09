// Node 24 ES modules; isolated seeded layout fixtures, no earned-age claim.
import {chromium} from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {spawn} from 'node:child_process';
import {writeFile,mkdir} from 'node:fs/promises';
const root=process.cwd(),out=root+'/qa/planner-device-handoff-20261009',port=4504;
const server=spawn(process.execPath,['scripts/serve.mjs','--port',String(port)],{stdio:['ignore','pipe','pipe']});let log='';server.stdout.on('data',c=>log+=c);
let browser;const report={scope:'Eight-age seeded Army fixtures at four viewports; no saved owner profile, no natural progression claim',errors:[],rows:[]};
await mkdir(out+'/viewports',{recursive:true});
try {
 for(let i=0;i<50&&!log.includes('Reborn local preview');i++)await new Promise(r=>setTimeout(r,100));
 browser=await chromium.launch({headless:true,args:['--no-proxy-server'],executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 for(const viewport of [{width:825,height:375},{width:933,height:424},{width:1180,height:820},{width:1280,height:720}]){
  for(let age=0;age<8;age++){
   const c=await browser.newContext({viewport}),p=await c.newPage();await p.goto('http://127.0.0.1:'+port);
   await p.evaluate(async age=>{const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});const {default:contract}=await import('/src/data/implementation-contract.json',{with:{type:'json'}});const {newCampaign}=await import('/src/core/campaign.js');const {encode,SAVE_KEY,VIEW_KEY}=await import('/src/core/save.js');const s=newCampaign(contract,data,Date.now(),246813579);s.age=age;s.tutorial.skipped=true;s.plots[1].type='barracks';s.plots[1].level=1;s.army=['melee','ranged','heavy'].map((type,i)=>({id:'army-'+i,kind:'role',type,age,count:10,rank:0,xp:0}));localStorage.setItem(SAVE_KEY,encode(s,data));localStorage.setItem(VIEW_KEY,'army');},age);
   await p.reload();await p.evaluate(async()=>{await Promise.all([...document.querySelectorAll('svg image')].map(n=>new Promise(resolve=>{const im=new Image();im.onload=resolve;im.onerror=resolve;im.src=n.getAttribute('href')})))});
   const metrics=await p.evaluate(()=>({texts:[...document.querySelectorAll('#world text')].map(n=>{const m=n.getScreenCTM(),r=n.getBoundingClientRect(),stage=document.querySelector('#stage-field').getBoundingClientRect();return {text:n.textContent,fontCss:parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b),rect:{x:r.x,y:r.y,width:r.width,height:r.height},clipped:r.y<stage.y||r.bottom>stage.bottom||r.x<stage.x||r.right>stage.right}}),plates:[...document.querySelectorAll('[data-plate]')].map(n=>({path:n.dataset.plate,width:n.getBoundingClientRect().width,height:n.getBoundingClientRect().height}))}));
   report.rows.push({viewport,age,...metrics});if(age===7)await p.screenshot({path:out+'/viewports/army-future-'+viewport.width+'x'+viewport.height+'.png'});await c.close();
  }
 }
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();server.kill();await writeFile(out+'/viewport-report.json',JSON.stringify(report,null,2))}
console.log(JSON.stringify({errors:report.errors,rows:report.rows.length,minCaptionCss:Math.min(...report.rows.flatMap(r=>r.texts.map(t=>t.fontCss))),clippedRows:report.rows.filter(r=>r.texts.some(t=>t.clipped)).length}));
