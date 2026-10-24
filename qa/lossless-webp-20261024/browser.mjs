import data from '../../dist/src/data/reference-data.json' with { type: 'json' };
import contract from '../../dist/src/data/implementation-contract.json' with { type: 'json' };
import worlds from '../../dist/src/data/adventure-worlds.json' with { type: 'json' };
import { newCampaign, command } from '../../dist/src/core/campaign.js';
import { encode } from '../../dist/src/core/save.js';
import { IndexedDBStorageAdapter } from '../../dist/src/core/storage-adapter.js';
import { legalDeploymentCells } from '../../dist/src/core/battle.js';

const result = document.querySelector('#result');
const screens = ['home','kingdom','adventure','hero','army','forge','market','tactical','defense','story','war','settings','help','campaignMapSelect'];
const parameters=new URLSearchParams(location.search);
const viewport={width:Number(parameters.get('width'))||1280,height:Number(parameters.get('height'))||720};
const report = { scope:'Fixture-based compression/render regression; not natural journeys or physical touch/device QA', viewport, assetChecks:[], screenChecks:[], errors:[], complete:false };
const manifest = await fetch('../../dist/asset-encoding.json').then(r=>r.json());
const adapter = new IndexedDBStorageAdapter();
let frame, sequence = 0;
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
function show() { result.textContent = JSON.stringify({complete:report.complete, assets:report.assetChecks.length, screens:report.screenChecks.length, failures:report.errors, latest:report.screenChecks.at(-1)},null,2); }
function send(state,type,payload={}) { return command(state,{id:`webp-${sequence++}`,type,payload},state.clock,data); }
function fixture(age, screen, { heroClass='knight', worldId=worlds[0].id, wall='none' } = {}) {
  let state = newCampaign(contract,data,Date.now(),123456,worldId);
  state = send(state,'SET_CLASS',{class:heroClass});
  state.age=age; state.hero.class=heroClass;
  state.story.flags.enteredValley=true; state.tutorial.skipped=true; state.settings.reducedMotion=true;
  state.army.forEach(stack=>{stack.age=age;});
  state.walls.level=wall==='tall'?2:wall==='built'?1:0;
  if(wall==='scaffold') state.buildJobs=[{id:'webp-wall-fixture',plotId:'walls',type:'walls',targetLevel:1,startedAt:state.clock,completesAt:state.clock+600000}];
  if(screen==='tactical') {
    state=send(state,'START_SKIRMISH');
    for(const id of state.battle.deployment.movableIds) state=send(state,'DEPLOY_BATTLE_STACK',{stackId:id,cell:legalDeploymentCells(state.battle,id)[0]});
    state=send(state,'START_DEPLOYED_BATTLE');
  }
  if(screen==='defense') {
    state=send(state,'START_SIEGE'); state=send(state,'DEPLOY_DEFENSE');
    state=send(state,'DEFENSE',{dt:0,paused:true});
  }
  return state;
}
async function decodeUrl(url, expected) {
  const image=new Image();image.src=url;
  try { await image.decode(); } catch(error) { throw new Error(`Cannot decode ${url}: ${error.message}`); }
  if(!image.naturalWidth || !image.naturalHeight) throw new Error(`Empty decoded image ${url}`);
  if(expected && (image.naturalWidth!==expected[0] || image.naturalHeight!==expected[1])) throw new Error(`Dimensions changed ${url}`);
  return [image.naturalWidth,image.naturalHeight];
}
async function checkScreen(age,screen,options={}) {
  if(location.origin!=='http://localhost:4175') throw new Error('Disposable test origin required; no writes allowed here');
  if(frame) { await frame.contentWindow?.rebornBackground?.(true);frame.remove();frame=null;await pause(40); }
  const state=fixture(age,screen,options);
  const previous=await adapter.loadLive(data);
  await adapter.replace(previous.head??null,encode(state,data),data,screen==='tactical'||screen==='defense'?screen:'kingdom');
  frame=document.createElement('iframe');frame.title=`${screen} age ${age}`;
  frame.style.width=viewport.width+'px';frame.style.height=viewport.height+'px';
  frame.src='../../dist/index.html?audit';document.querySelector('#host').append(frame);
  await new Promise((resolve,reject)=>{frame.onload=resolve;frame.onerror=reject;});
  const w=frame.contentWindow,doc=frame.contentDocument;
  const runtimeErrors=[];
  w.addEventListener('error',event=>{if(event.message)runtimeErrors.push(event.message);});
  w.addEventListener('unhandledrejection',event=>runtimeErrors.push(String(event.reason)));
  for(let attempt=0;attempt<150 && (!doc.querySelector('#app')?.dataset.view || typeof doc.querySelector('#context')?.onclick!=='function');attempt++) await pause(20);
  // An offline-resume note legitimately opens the campaign gate. Use Continue,
  // as a player would, rather than treating its gate panel as the main menu.
  if(doc.querySelector('#app')?.dataset.view==='home' && screen!=='home' && screen!=='campaignMapSelect') {
    const continueButton=doc.querySelector('[data-choice="continue"]');
    if(continueButton) {continueButton.click();await pause(20);}
  }
  if(doc.querySelector('#app')?.dataset.view!==screen) {
    const destination=screen==='campaignMapSelect'?'home':screen;
    const navigation=doc.querySelector(`[data-choice="nav:${destination}"]`);
    if(navigation) navigation.click();
    else {doc.querySelector('#context').click();const menu=doc.querySelector(`[data-choice="menu:${destination}"]`);if(!menu)throw new Error(`Missing menu ${destination}`);menu.click();}
    if(screen==='campaignMapSelect') doc.querySelector('[data-choice="new-campaign"]').click();
  }
  await pause(60);
  if(screen==='hero' && options.tab) {
    const tab=doc.querySelector(`[data-choice="hero-tab:${options.tab}"]`);
    if(!tab) throw new Error(`Missing Hero tab ${options.tab}`);
    tab.click();await pause(40);
  }
  const actual=doc.querySelector('#app')?.dataset.view;
  if(actual!==screen) throw new Error(`Expected ${screen}, rendered ${actual}`);
  if(w.innerWidth!==viewport.width||w.innerHeight!==viewport.height) throw new Error('Unexpected game viewport');
  const urls=new Set();
  for(const node of doc.querySelectorAll('img[src],image[href]')) {
    const value=node.getAttribute('src')||node.getAttribute('href');
    if(value&&!value.startsWith('#')&&!value.startsWith('data:')) urls.add(new URL(value,frame.src).href);
  }
  for(const node of doc.querySelectorAll('[style]')) {
    for(const match of node.getAttribute('style').matchAll(/url\(["']?([^"')]+)["']?\)/g)) if(!match[1].startsWith('#')) urls.add(new URL(match[1],frame.src).href);
  }
  for(const url of urls) await decodeUrl(url);
  if(runtimeErrors.length) throw new Error(runtimeErrors.join('; '));
  const row={age,screen,options,actual,imageUrls:[...urls],passed:true};report.screenChecks.push(row);show();return row;
}
document.querySelector('#run').onclick=async()=>{
  document.querySelector('#run').disabled=true;
  try {
    // Verify every packaged image through the browser decoder, not only file existence.
    const queue=[...manifest.assets];
    await Promise.all(Array.from({length:3},async()=>{while(queue.length){const row=queue.shift();try{const dimensions=await decodeUrl(new URL('../../dist/'+row.file,location.href).href,row.dimensions);report.assetChecks.push({file:row.file,dimensions,passed:true});}catch(error){report.errors.push({asset:row.file,error:String(error)});}show();}}));
    for(let age=0;age<8;age++) for(const screen of screens) {try{await checkScreen(age,screen);}catch(error){report.errors.push({age,screen,error:String(error)});show();}}
    for(let age=0;age<8;age++) for(const wall of ['scaffold','built','tall']) {try{await checkScreen(age,'kingdom',{wall});}catch(error){report.errors.push({age,wall,error:String(error)});}}
    for(const heroClass of Object.keys(data.CLASSES)) for(const age of [0,3,4,7]) {try{await checkScreen(age,'hero',{heroClass});}catch(error){report.errors.push({heroClass,age,error:String(error)});}}
    for(let age=0;age<8;age++) for(const tab of ['skills','spells','inventory']) {try{await checkScreen(age,'hero',{tab});}catch(error){report.errors.push({age,tab,error:String(error)});}}
    for(const world of worlds) {try{await checkScreen(0,'adventure',{worldId:world.id});}catch(error){report.errors.push({world:world.id,error:String(error)});}}
    report.complete=true;report.passed=report.errors.length===0;show();
  }catch(error){report.errors.push({error:String(error)});show();}
};
document.querySelector('#show').onclick=()=>checkScreen(7,document.querySelector('#review').value).catch(error=>{report.errors.push({error:String(error)});show();});
document.querySelector('#download').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='browser-verification.json';a.click();URL.revokeObjectURL(a.href);};
