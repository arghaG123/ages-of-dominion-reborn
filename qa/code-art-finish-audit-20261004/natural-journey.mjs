// Read-only imported core; synthetic clock acceleration, no resource/stat/position grants.
import fs from 'node:fs/promises';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,advance} from '../../src/core/campaign.js';
import {adventureMap,isOpen} from '../../src/core/navigation.js';
import {save,load} from '../../src/core/save.js';
let s=newCampaign(contract,data,1000),i=0;const rows=[];
const act=(type,payload={})=>{s=command(s,{id:`audit-${++i}`,type,payload},s.clock,data);return s;};
const storage={m:new Map(),getItem(k){return this.m.get(k)??null},setItem(k,v){this.m.set(k,v)},removeItem(k){this.m.delete(k)}};
function reload(label){save(storage,s,data);const loaded=load(storage,data);if(loaded.status!=='VALID')throw Error('reload invalid');s=loaded.state;rows.push({label,revision:s.revision,visited:s.adventure?.visited,resolved:s.adventure?.resolvedGuards,encounter:s.adventure?.pendingEncounter?.id});}
function route(start,target,map){const q=[[start]],seen=new Set([start.join(',')]);while(q.length){const p=q.shift(),a=p.at(-1);if(a.join(',')===target.join(','))return p.slice(1);for(const d of [[0,-1],[1,0],[0,1],[-1,0]]){const n=[a[0]+d[0],a[1]+d[1]],k=n.join(',');if(seen.has(k)||!isOpen(map,...n))continue;if(map.guards.has(k)&&k!==target.join(',')&&!s.adventure.resolvedGuards.includes(k))continue;seen.add(k);q.push([...p,n]);}}return null;}
try{
 for(const [plotId,building] of [['P01','lumber'],['P02','farm'],['P03','quarry'],['P04','barracks']]){act('BUILD',{plotId,building});s=advance(s,s.buildJobs[0].completesAt,data);}
 act('RECRUIT',{role:'melee'});act('ENTER_ADVENTURE');reload('entered-fog');const map=adventureMap(contract.geometry.adventure);
 const targets=[...map.guards].map(k=>k.split(',').map(Number));
 for(const target of targets){
  const p=route([s.adventure.x,s.adventure.y],target,map);if(!p)throw Error('No legal path to '+target);
  for(const cell of p){if(s.adventure.moves<1)act('END_DAY');act('MOVE',{path:[cell]});}
  reload('natural-guard-'+target);const before=s.resources.gold;act('BEGIN_ENCOUNTER');reload('tactical-before-auto');act('BATTLE',{action:'auto'});
  const outcome=structuredClone(s.battle.outcome),status=s.battle.status;rows.push({label:'combat-'+target,status,outcome,startingGold:before});
  if(!s.battle.pendingSettlement)throw Error('Auto did not reach pending settlement');reload('pending-result');const tx={id:`settlement-${++i}`,type:'SETTLE_BATTLE',payload:{}};s=command(s,tx,s.clock,data);const once=JSON.stringify(s);s=command(s,tx,s.clock,data);const sameIdempotent=JSON.stringify(s)===once;let newIdRejected=false;try{act('SETTLE_BATTLE')}catch{newIdRejected=true}
  rows.push({label:'settled-'+target,gold:s.resources.gold,goldDelta:s.resources.gold-before,sameIdempotent,newIdRejected,army:s.army.map(x=>({type:x.type,count:x.count})),guardResolved:s.adventure.resolvedGuards.includes(target.join(',')),pending:s.adventure.pendingEncounter});reload('settled-reload');
  if(outcome.winner!=='p')throw Error('Natural starting army lost; no stat/resource grant or cleared flag fabricated');
 }
 const home=contract.geometry.adventure.sites.find(v=>v.id==='town').approach;
 const back=route([s.adventure.x,s.adventure.y],home,map);if(!back)throw Error('No legal return path');
 for(const cell of back){if(s.adventure.moves<1)act('END_DAY');act('MOVE',{path:[cell]});}
 act('RETURN_TOWN');reload('returned-town');rows.push({label:'home-return',atTown:s.adventure.atTown,position:[s.adventure.x,s.adventure.y],inventory:s.inventory});
}catch(e){rows.push({label:'stopping-evidence',error:e.message});}
const result={at:new Date().toISOString(),scope:'Core command journey, accelerated construction only. Actual legal paths/fog/guards/Auto/settle/reload. No resource, combat-stat, position or clear-flag fixtures. Browser/manual tactical/eight-age/owner/device scope separate.',rows,final:{resources:s.resources,adventure:s.adventure,battle:s.battle?.status,tutorial:s.tutorial}};
await fs.writeFile(new URL('./natural-journey.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
