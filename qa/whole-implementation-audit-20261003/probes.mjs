import fs from 'node:fs';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,validate} from '../../src/core/campaign.js';
import {startBattle,validateBattle,legalTargets,meleeApproaches,strike} from '../../src/core/battle.js';
const results={};
const accepts=(fn)=>{try{fn();return true;}catch(e){return e.message;}};
const fresh=()=>newCampaign(contract,data,1000);
const act=(s,id,type,payload)=>command(s,{id,type,payload},1000,data);
let s=fresh(); s.resources.gold=10000;
s=act(s,'offer','OFFER_DWELLING',{type:'wolf'});
s=act(s,'claim','CLAIM_DWELLING',{});
results.dwellingCapacity={actual:s.army.length,allowed:2,paidGold:10000-s.resources.gold,validation:accepts(()=>validate(s,data))};
const stack=(id,side,x,y,spd=4)=>({id,side,x,y,spd,count:2,maxCount:2,atk:4,def:4,dmin:1,dmax:1,uhp:20,top:20,rng:0,shots:0,fly:0});
const battle=startBattle({id:'probe',positioned:true,rngState:4,mana:10,wisdom:1,stacks:[stack('p','p',1,3,5),stack('e','e',4,3,1)]});
const approach=meleeApproaches(battle,'p','e').find(Boolean);
results.advertisedMelee={targets:legalTargets(battle,'p').melee,approach,clientPayloadResult:accepts(()=>strike(battle,'p','e',{forceMelee:true})),withApproachResult:accepts(()=>strike(battle,'p','e',{forceMelee:true,approach}))};
results.malformedBattle={};
for(const [name,mutate] of Object.entries({negativeMana:b=>b.mana=-10,emptyQueue:b=>b.queue=[],invalidDamage:b=>b.stacks[0].dmin=-100,invalidMaxCount:b=>b.stacks[0].maxCount=0,over32bitRng:b=>b.rngState=2**40,falseVictory:b=>{b.status='RESOLVED';b.pendingSettlement=true;b.outcome={winner:'p'};}})){
const b=structuredClone(battle);mutate(b);results.malformedBattle[name]=accepts(()=>validateBattle(b));}
const f=structuredClone(battle);f.stacks[0].fly=1;f.stacks[0].x=3;f.stacks[0].y=5;
results.flyerWaterSave=accepts(()=>validateBattle(f));
const provenance=Object.fromEntries(['campaign.js','battle.js','save.js','navigation.js'].map(n=>[n,fs.statSync(new URL('../../src/core/'+n,import.meta.url)).mtime.toISOString()]));
fs.writeFileSync(new URL('./core-probes.json',import.meta.url),JSON.stringify({results,provenance},null,2)+'\n');
console.log(JSON.stringify(results,null,2));
