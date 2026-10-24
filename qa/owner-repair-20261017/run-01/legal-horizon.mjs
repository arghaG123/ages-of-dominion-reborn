// Legal accelerated core simulation; NOT natural UI or browser/device proof.
// No resource, hero, enemy, wave, result or claim fields are assigned.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import data from '../../../src/data/reference-data.json' with {type:'json'};
import contract from '../../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,cost,advanceReported,advanceActiveDefense,questReady} from '../../../src/core/campaign.js';
import {agePrice,forgeOffer,recruitCost,towerPurchaseCost} from '../../../src/core/rules.js';
import {encode,decode} from '../../../src/core/save.js';
const out=new URL('.',import.meta.url);
let now=1700000000000, state=newCampaign(contract,data,now,123456789), serial=0;
const result={classification:'LEGAL_ACCELERATED_CORE_SIMULATION',grants:0,stateFieldOverrides:0,commands:{},sessions:[],activeSimulationSeconds:0,clockAdvanceMs:0};
const start=performance.now();
function go(type,payload={}) {
  state=command(state,{id:`legal-${++serial}`,type,payload},now,data);
  result.commands[type]=(result.commands[type]||0)+1;
}
const affordable=price=>Object.entries(price).every(([key,n])=>state.resources[key]>=n);
function earn(price){let tries=0;while(!affordable(price)){
  if(++tries>500)throw new Error('Legal income could not afford '+JSON.stringify(price));
  const elapsed=[8,7,6,5,4,3.5,3,3][state.age]*3600000;
  now+=elapsed;result.clockAdvanceMs+=elapsed;
  state=advanceReported(state,now,data).state;
}}
function finishJobs(){if(!state.buildJobs.length)return;const elapsed=Math.max(...state.buildJobs.map(j=>j.completesAt))-now;now+=Math.max(0,elapsed);result.clockAdvanceMs+=Math.max(0,elapsed);state=advanceReported(state,now,data).state;}
function build(type,id,target=1){while((id==='walls'?state.walls:state.plots.find(p=>p.id===id)).level<target){
  const current=id==='walls'?state.walls:state.plots.find(p=>p.id===id);
  earn(cost(data,type,current.level));go('BUILD',{plotId:id,building:type});finishJobs();
}}
function recruit(role,times){for(let i=0;i<times;i++){earn(recruitCost(data,role,state.age));go('RECRUIT',{role});}}
function beginEndless(deploy=true){go('START_ENDLESS');if(deploy){go('DEPLOY_DEFENSE');const army=state.army.find(s=>s.age===7&&s.count>0);if(army)go('DEPLOY_ARMY',{stackId:army.id});}go('DEFENSE',{dt:0,speed:2});}
function sample(){
  const before=state.defense.time, ledger=Object.keys(state.settledTransactions).length;
  now+=250; result.clockAdvanceMs+=250;
  state=advanceReported(state,now,data).state;
  state=advanceActiveDefense(state,.25);
  const elapsed=state.defense.time-before;
  assert.ok(elapsed>=0 && elapsed<=.501);
  result.activeSimulationSeconds+=elapsed;
  assert.equal(Object.keys(state.settledTransactions).length,ledger,'internal advancement adds no transaction IDs');
}
try{
  build('lumber','P01');build('farm','P02');build('quarry','P03');build('mine','P04');
  for(const [id,type,target] of [['P01','lumber',5],['P02','farm',4],['P03','quarry',4],['P04','mine',5],['P05','barracks',3],['P06','workshop',2],['P07','armory',7]])build(type,id,target);
  build('townhall','townhall',8); build('walls','walls',8);
  while(state.age<7){earn(agePrice(state.age));go('AGE_UP');}
  assert.equal(state.age,7);
  for(const tower of [...state.towers]){earn({wood:120*(tower.tier+1),stone:100*(tower.tier+1),gold:80*(tower.tier+1)});go('RETROFIT',{towerId:tower.id});}
  for(const family of Object.keys(data.TOWERS)){if(!state.towers.some(t=>t.fam===family)){earn(towerPurchaseCost(data,family,state.age));go('BUY_TOWER',{family});}}
  for(const slot of contract.slots){const offer=forgeOffer(state.age,7,3);earn(offer.cost);go('FORGE',{slot,quality:3});go('EQUIP',{itemId:state.inventory.at(-1).id});}
  recruit('heavy',100);
  result.preparation={age:state.age,hero:state.hero,army:state.army,walls:state.walls,towers:state.towers,resources:state.resources,commands:serial};
  beginEndless(true);
  let samples=0;
  while(state.defense.status==='ACTIVE' && samples++<50000) sample();
  assert.equal(state.defense.status,'RESOLVED','Endless must reach a real simulated defeat, not an assigned result');
  const first={id:state.defense.id,winner:state.defense.winner,cleared:state.defense.clearedWaves,waves:state.defense.waves,core:state.defense.core,time:state.defense.time};
  result.sessions.push(first);
  result.twentyClears=first.cleared>=20;
  go('SETTLE_DEFENSE');
  result.bestAfterLoss=state.story.flags.endlessBest ?? null;
  result.q6Ready=questReady(state,data,'q6');
  if(result.q6Ready)go('CLAIM_QUEST',{id:'q6'});
  // Accumulate only real ACTIVE simulation time, entering and settling actual
  // sessions. Undeployed later sessions test legal defeat and re-entry without
  // pretending post-resolution loops are active play.
  let sessions=0;
  while(result.activeSimulationSeconds<36000){
    if(++sessions>1000)throw new Error('Active horizon session limit');
    beginEndless(false);
    while(state.defense.status==='ACTIVE' && result.activeSimulationSeconds<36000)sample();
    if(state.defense.status==='RESOLVED'){
      result.sessions.push({id:state.defense.id,cleared:state.defense.clearedWaves,core:state.defense.core,time:state.defense.time,winner:state.defense.winner});
      go('SETTLE_DEFENSE');
    }
    if(sessions%10===0)console.log(JSON.stringify({activeSeconds:Math.round(result.activeSimulationSeconds),sessions}));
  }
  // Settle the last session through actual simulation, preserving its outcome.
  while(state.defense?.status==='ACTIVE')sample();
  if(state.defense)go('SETTLE_DEFENSE');
  while(serial<10000)go('SETTINGS',{...state.settings});
  const raw=encode(state,data);assert.equal(decode(raw,data).revision,state.revision);
  result.explicitValidCommands=serial;
  result.internalLedgerCount=Object.keys(state.settledTransactions).length;
  result.encodedBytes=Buffer.byteLength(raw);
  result.realElapsedSeconds=(performance.now()-start)/1000;
  result.horizonComplete=result.twentyClears && result.activeSimulationSeconds>=36000 && serial>=10000;
  result.remaining=['All creature/skill/spell/quest/milestone natural obligations and actual browser storage capacity remain separate.'];
  fs.writeFileSync(new URL('legal-horizon-campaign.json',out),raw);
}catch(error){result.error=String(error);result.stack=error.stack;process.exitCode=1;}
fs.writeFileSync(new URL('legal-horizon-results.json',out),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({complete:result.horizonComplete,twentyClears:result.twentyClears,activeSeconds:result.activeSimulationSeconds,commands:serial,error:result.error}));
