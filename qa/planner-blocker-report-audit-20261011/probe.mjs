import fs from 'node:fs';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,validate} from '../../src/core/campaign.js';
import {createDefense,deployHero,castDefense,validateDefense} from '../../src/core/defense.js';
import {startBattle,move,legalMoves,validateBattle,activeStackId} from '../../src/core/battle.js';
import {encode,decode} from '../../src/core/save.js';
const rows=[];
function check(id,fn){try{rows.push({id,...fn()});}catch(e){rows.push({id,unexpectedError:e.stack});}}
const fresh=()=>newCampaign(contract,data,1000);
function lastEnemy(practice){const s=deployHero(createDefense(fresh(),data,{practice,waves:1}),4); const last=s.queue.at(-1);for(const e of s.queue){e.spawned=true;e.hp=e===last?1:0;e.progress=2;}s.enemies=s.queue.filter(e=>e.spawned);validateDefense(s);return s;}
for(const practice of ['siege','endless'])check('blast-final-enemy-'+practice,()=>{const s=lastEnemy(practice);try{castDefense(s,14,2);return {reproduced:false};}catch(e){return {reproduced:true,error:e.message,validBefore:true,clearedBefore:s.clearedWaves};}});
check('bonus-save-forged-flags',()=>{let b=startBattle({id:'bonus',positioned:true,rngState:1,mana:0,morale:3,stacks:[{id:'p',side:'p',x:1,y:8,count:2,maxCount:2,atk:1,def:1,dmin:1,dmax:1,uhp:20,top:20,spd:2},{id:'e',side:'e',x:5,y:2,count:2,maxCount:2,atk:1,def:1,dmin:1,dmax:1,uhp:20,top:20,spd:1}]}); b.currentBonusId='p';b.stacks[0].bonusPending=true;b.stacks[0].moraleChecked=true;b.stacks[0].moraleBonusGranted=false;b.queue=['e','p'];validateBattle(b);const state=fresh();state.battle=b;const saved=decode(encode(state,data),data);return {reproduced:true,acceptedBySave:true,currentBonusId:saved.battle.currentBonusId,activeStackId:activeStackId(saved.battle),granted:saved.battle.stacks[0].moraleBonusGranted};});
check('defense-xp-save-negative',()=>{const state=fresh();state.defense=createDefense(state,data,{practice:'siege',waves:1});state.defense.towers[0].xp=-100;validate(state,data);const saved=decode(encode(state,data),data);return {reproduced:true,acceptedBySave:true,xp:saved.defense.towers[0].xp};});
check('dwelling-history-contradictory-terms',()=>{const s=fresh();s.dwelling={id:'dwelling:dwelling:wolf',siteId:'dwelling',type:'wolf',count:2,multiplier:1,claimed:false};s.dwellingHistory=[{...s.dwelling,count:99,multiplier:0.5}];validate(s,data);const saved=decode(encode(s,data),data);return {reproduced:true,acceptedBySave:true,openCount:saved.dwelling.count,historyCount:saved.dwellingHistory[0].count,openMultiplier:saved.dwelling.multiplier,historyMultiplier:saved.dwellingHistory[0].multiplier};});
const result={date:'2026-10-11',scope:'Isolated synthetic negative/edge diagnostics, not earned gameplay',rows};fs.writeFileSync(new URL('./probes.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
