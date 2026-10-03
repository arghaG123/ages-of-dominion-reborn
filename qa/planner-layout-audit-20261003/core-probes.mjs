import {newCampaign,validate} from '../../src/core/campaign.js';
import {startBattle,strike} from '../../src/core/battle.js';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {writeFile} from 'node:fs/promises';
const fresh=newCampaign(contract,data,1000);
const invalid=structuredClone(fresh);invalid.battle={id:'probe',kind:'tactical',status:'ACTIVE',practice:'campaign',rngState:1,round:1,stacks:[{id:'p',side:'p',count:1,spd:-1,uhp:-1,top:-1,x:999,y:999},{id:'e',side:'e',count:1,spd:1,uhp:1,top:1,x:0,y:0}],queue:['unknown']};
let acceptsMalformedBattle=false;try{validate(invalid,data);acceptsMalformedBattle=true;}catch{}
const stack=(id,side,x,y,spd)=>({id,side,x,y,spd,count:1,maxCount:1,uhp:10,top:10,atk:2,def:1,dmin:1,dmax:1,rng:0,shots:0});
const battle=startBattle({id:'probe-range',practice:'campaign',rngState:1,stacks:[stack('p','p',0,9,10),stack('e','e',6,0,1)]});
let remoteMeleeAccepted=false;try{remoteMeleeAccepted=strike(battle,'p','e').log.some(r=>r.type==='strike');}catch{}
const result={acceptsMalformedBattle,remoteMeleeAccepted,interpretation:'Existing scalar combat foundation is not a legal positioned Tactical engine. No campaign or executor output was written.'};
await writeFile(new URL('./core-probes.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
