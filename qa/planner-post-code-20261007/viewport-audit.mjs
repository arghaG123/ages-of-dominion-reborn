import {chromium} from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {spawn} from 'node:child_process';
import {writeFile,mkdir} from 'node:fs/promises';
const root='C:/dev/ages-of-dominion-reborn',out=root+'/qa/planner-post-code-20261007';
const server=spawn(process.execPath,['scripts/serve.mjs','--port','4428'],{cwd:root,stdio:['ignore','pipe','pipe']});let log='';server.stdout.on('data',b=>log+=b);server.stderr.on('data',b=>log+=b);
for(let i=0;i<50&&!log.includes('Reborn local preview');i++)await new Promise(r=>setTimeout(r,100));
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-proxy-server']});
const report={type:'FIXTURE_VIEWPORT_AND_MODAL_AUDIT',errors:[],rows:[],checks:[],instrumentation:'Initial browser report measured detached SVG nodes at zero before RAF. These live post-layout measurements supersede those size entries.'};
const sizes=[[825,375],[933,424],[1180,820],[1280,720]];await mkdir(out+'/viewports',{recursive:true});
async function ready(p){await p.evaluate(async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));await Promise.all([...document.querySelectorAll('svg image')].map(n=>new Promise(resolve=>{let im=new Image;im.onload=resolve;im.onerror=resolve;im.src=n.getAttribute('href')})));await new Promise(r=>requestAnimationFrame(r));});}
try{
for(let age=0;age<8;age++){
 const ctx=await browser.newContext({viewport:{width:1280,height:720}}),p=await ctx.newPage();p.on('pageerror',e=>report.errors.push(String(e)));await p.goto('http://127.0.0.1:4428');
 await p.evaluate(async(age)=>{const {default:data}=await import('/src/data/reference-data.json',{with:{type:'json'}});const {default:contract}=await import('/src/data/implementation-contract.json',{with:{type:'json'}});const {newCampaign}=await import('/src/core/campaign.js');const {encode,SAVE_KEY,VIEW_KEY}=await import('/src/core/save.js');let s=newCampaign(contract,data,Date.now(),123456);s.age=age;s.tutorial.skipped=true;s.plots.find(p=>p.id==='P01').type='barracks';s.plots.find(p=>p.id==='P01').level=1;s.army=['melee','ranged','heavy'].map((type,i)=>({id:'fixture-'+i,kind:'role',type,age,count:10,rank:0,xp:0}));localStorage.setItem(SAVE_KEY,encode(s,data));localStorage.setItem(VIEW_KEY,'army');},age);
 await p.reload();await ready(p);
 for(const screen of ['army','kingdom']){
  await p.locator('[data-choice="nav:'+screen+'"]').click();
  for(const [width,height] of sizes){await p.setViewportSize({width,height});await ready(p);const detail=await p.evaluate(()=>({screen:window.rebornSnapshot()?.age,plates:[...document.querySelectorAll('[data-plate]')].map(n=>{let b=n.getBoundingClientRect();return {path:n.dataset.plate,width:b.width,height:b.height,cap:Number(n.parentElement.dataset.plateCssCap)||130,cssDeclared:Number(n.parentElement.dataset.plateCssHeight)}}),text:[...document.querySelectorAll('#world text')].map(n=>{let b=n.getBoundingClientRect(),m=n.getScreenCTM();return {text:n.textContent,cssFont:parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b),visible:b.top>=70&&b.bottom<=innerHeight-56}})}));
   const id=screen+'-age-'+age+'-'+width+'x'+height;await p.screenshot({path:out+'/viewports/'+id+'.png'});report.rows.push({id,screen,age,viewport:[width,height],stateKind:'FIXTURE',path:'qa/planner-post-code-20261007/viewports/'+id+'.png',...detail});
  }
 }
 await ctx.close();
}
// Ordinary controls: isolate a fresh campaign and test dispatch guards while modal is open.
const ctx=await browser.newContext({viewport:{width:825,height:375}}),p=await ctx.newPage();await p.goto('http://127.0.0.1:4428');await p.locator('[data-choice="new-campaign"]').click();await p.locator('[data-choice="class:ranger"]').first().click();await p.locator('[data-choice="enter-valley"]').first().click();await p.locator('[data-choice="nav:war"]').click();await p.locator('#context').click();await p.getByRole('button',{name:'Skirmish',exact:true}).first().click();await ready(p);await p.locator('#dock [data-choice="retreat"]').click();
const guard=await p.evaluate(()=>{const before=window.rebornActions.length;document.querySelector('[data-cell][data-open="1"]').dispatchEvent(new MouseEvent('click',{bubbles:true}));document.querySelector('[data-choice="nav:kingdom"]').click();document.querySelector('#save').click();return {before,after:window.rebornActions.length,dialogOpen:!document.querySelector('#retreat').hidden,htmlHost:document.querySelector('#stage-field').tagName,inert:document.querySelector('#stage-field').hasAttribute('inert')};});report.checks.push({id:'map-nav-save-programmatic-modal-guard',pass:guard.before===guard.after&&guard.dialogOpen&&guard.inert,detail:guard});
let trapped=true;for(let i=0;i<6;i++){await p.keyboard.press(i%2?'Shift+Tab':'Tab');trapped&&=await p.evaluate(()=>document.activeElement.closest('#retreat')!==null);}report.checks.push({id:'bidirectional-tab-containment',pass:trapped});await ctx.close();
}catch(e){report.errors.push(e.stack)}finally{await browser.close();server.kill();report.serverLog=log;await writeFile(out+'/viewport-report.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify({errors:report.errors,captures:report.rows.length,checks:report.checks}));
