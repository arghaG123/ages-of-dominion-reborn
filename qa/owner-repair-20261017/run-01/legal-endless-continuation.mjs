import fs from 'node:fs';
import crypto from 'node:crypto';
import data from '../../../src/data/reference-data.json' with {type:'json'};
import {command,advanceActiveDefense,advanceReported,manaMax} from '../../../src/core/campaign.js';
import {defenseMarkers} from '../../../src/core/defense.js';
import {encode,decode} from '../../../src/core/save.js';
const out=new URL('.',import.meta.url), input=fs.readFileSync(new URL('legal-horizon-campaign.json',out),'utf8');
let state=decode(input,data), now=state.clock, serial=0;
const report={classification:'LEGAL_ACCELERATED_CORE_CONTINUATION',sourceSHA256:crypto.createHash('sha256').update(input).digest('hex'),overrides:0,commands:{},duels:[]};
function go(type,payload={}){state=command(state,{id:`continuation-${++serial}`,type,payload},now,data);report.commands[type]=(report.commands[type]||0)+1;}
try{
  for(let i=0;i<200;i++){
    go('START_DUEL');go('BATTLE',{action:'auto'});
    if(state.battle.status!=='RESOLVED')throw new Error('Auto did not resolve duel');
    report.duels.push({winner:state.battle.outcome.winner});go('SETTLE_BATTLE');
    const offer=state.hero.offers.find(o=>!o.chosen&&!o.declined);
    if(offer)go('CHOOSE_SKILL',{skill:offer.choices.includes('wisdom')?'wisdom':offer.choices.includes('offense')?'offense':offer.choices[0]});
    while(state.hero.points>0)go('SPEND_POINT',{stat:state.hero.level%3===0?'kno':'pow'});
    if(i%40===0)console.log(JSON.stringify({duels:i,level:state.hero.level,army:state.army.map(s=>s.count)}));
  }
  for(let i=0;i<4;i++)go('END_DAY');
  fs.writeFileSync(new URL('legal-trained-campaign.json',out),encode(state,data));
  report.before={level:state.hero.level,skills:state.hero.skills,mana:state.hero.mana,maxMana:manaMax(state,data),army:state.army};
  go('START_ENDLESS');go('DEPLOY_DEFENSE');
  const army=state.army.find(s=>s.age===7&&s.count>0);if(army)go('DEPLOY_ARMY',{stackId:army.id});
  go('DEFENSE',{dt:0,speed:2});
  let steps=0,lastCast=-100;
  while(state.defense.status==='ACTIVE'&&steps++<12000){
    const markers=defenseMarkers(state.defense);
    if(state.hero.mana>=40 && state.defense.heroHp>0 && state.defense.time-lastCast>2){
      const target=markers.enemies.find(e=>e.entered&&(e.role==='sapper'||e.role==='archer'||e.boss));
      if(target){go('DEFENSE_CAST',{x:target.at[0],y:target.at[1]});lastCast=state.defense.time;}
    }
    if(state.defense.status!=='ACTIVE')break;
    now+=250;state=advanceReported(state,now,data).state;state=advanceActiveDefense(state,.25);
  }
  report.endless={status:state.defense.status,cleared:state.defense.clearedWaves,waves:state.defense.waves,core:state.defense.core,time:state.defense.time,steps};
  report.twentyActualClears=state.defense.clearedWaves>=20;
  if(state.defense.status==='RESOLVED')go('SETTLE_DEFENSE');
  report.bytes=Buffer.byteLength(encode(state,data));
  fs.writeFileSync(new URL('legal-endless-continuation-campaign.json',out),encode(state,data));
}catch(error){report.error=String(error);report.stack=error.stack;process.exitCode=1;}
fs.writeFileSync(new URL('legal-endless-continuation-results.json',out),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({endless:report.endless,twenty:report.twentyActualClears,error:report.error}));
