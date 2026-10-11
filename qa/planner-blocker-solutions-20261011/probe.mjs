// Small independent diagnostics only. Synthetic states are fixtures, never earned play.
import fs from 'node:fs';
import crypto from 'node:crypto';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command} from '../../src/core/campaign.js';
import {dwellingPool,grantHeroXp} from '../../src/core/mechanics.js';
import {encode,decode} from '../../src/core/save.js';
const out='qa/planner-blocker-solutions-20261011';
const hashes={};
for(const p of ['src/core/campaign.js','src/core/mechanics.js','src/core/defense.js','src/core/battle.js','src/client/hero-room.js','tests/earned-scope-20261011.test.mjs']) hashes[p]=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let s=newCampaign(contract,data,1700000000000,123456789);
// Isolate offer replacement from legal journey/capacity/payment acceptance.
s.age=7;
const at=contract.geometry.adventure.sites.find(x=>x.id==='dwelling').approach;
s.adventure={x:at[0],y:at[1],moves:5,visited:[at.join(',')],resolvedGuards:[],pendingEncounter:null,atTown:false};
s.dwelling={type:'wolf',count:5,multiplier:1,claimed:true};
const reopened=command(s,{id:'fixture-next-offer',type:'OFFER_DWELLING',payload:{type:'bandit'}},s.clock,data);
const cancelled=command(reopened,{id:'fixture-cancel',type:'CANCEL_DWELLING',payload:{}},s.clock,data);
const resumed=decode(encode(cancelled,data),data);
let changedOpenRejected=false;
try {command(resumed,{id:'fixture-change-open',type:'OFFER_DWELLING',payload:{type:'bear'}},s.clock,data);} catch(e){changedOpenRejected=/Offer already open/.test(e.message);}
const skill=newCampaign(contract,data,s.clock,123456789);
skill.hero.skills.wisdom=2;
const offers=[];
for(let i=0;i<2000&&!offers.some(o=>o.choices.includes('wisdom'));i++) {
  grantHeroXp(skill,data,110,1);
  while(skill.hero.offers.some(o=>!o.chosen&&!o.declined)) {
    const o=skill.hero.offers.find(o=>!o.chosen&&!o.declined);
    offers.push({level:o.level,choices:[...o.choices]});
    const pick=o.choices.includes('wisdom')?'wisdom':o.choices.find(k=>skill.hero.skills[k]<3);
    if(pick) {skill.hero.skills[pick]++;o.chosen=pick;} else o.declined=true;
  }
}
const report={fixtureOnly:true,node:process.version,hashes,dwelling:{afterClaimNewOffer:reopened.dwelling,cancelReloadSame:JSON.stringify(reopened.dwelling)===JSON.stringify(resumed.dwelling),changedOpenRejected,pool:dwellingPool(data,7)},skills:{allClassesUseSameSkillPool:true,offers,wisdom:skill.hero.skills.wisdom,limitation:'Synthetic XP fixture proves offer generation can reach Wisdom3; does not prove owner-seed earned route.'}};
fs.writeFileSync(out+'/source-probes.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({dwelling:report.dwelling,skills:report.skills,node:report.node},null,2));
