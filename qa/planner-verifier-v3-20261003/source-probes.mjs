// Isolated in-memory checks, no game fixes, browser, build, provider, or device calls.
import fs from 'node:fs';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,validate,command} from '../../src/core/campaign.js';
import {adventureMap,routeCost,isOpen} from '../../src/core/navigation.js';
const fresh=()=>newCampaign(contract,data,1000);
const r={invalidStateAccepted:{},journey:{}};
const invalid={negativeArmyCount:s=>s.army[0].count=-5,unknownArmyRole:s=>s.army[0].type='invented',unknownTowerFamily:s=>s.towers[0].fam='invented',invalidDay:s=>s.day=-1,unknownPlotID:s=>s.plots[1].id='invented',outOfBoundsJourney:s=>s.adventure={x:999,y:999,moves:5,visited:[],resolvedGuards:[]},overCapacityMana:s=>s.hero.mana=1e9,equipmentWrongSlot:s=>s.hero.equip.weapon={id:'wrong-slot',kind:'gear',slot:'boots',age:0,quality:0},arbitraryBattlePayload:s=>s.battle={invented:true}};
for(const[k,change]of Object.entries(invalid)){const s=fresh();change(s);try{validate(s,data);r.invalidStateAccepted[k]=true;}catch(e){r.invalidStateAccepted[k]=false;}}
const act=(s,id,type,payload)=>command(s,{id,type,payload},1000,data);
let s=act(fresh(),'enter','ENTER_ADVENTURE',{});
const map=adventureMap(contract.geometry.adventure), approach=contract.geometry.adventure.sites.find(s=>s.id==='town').approach;
const start=[s.adventure.x,s.adventure.y];
const queue=[{cell:start,path:[],cost:0}], seen=new Set();let path;
while(queue.length){queue.sort((a,b)=>a.cost-b.cost);const n=queue.shift();const k=n.cell.join(',');if(seen.has(k))continue;seen.add(k);if(k===approach.join(',')){path=n;break;}for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;const p=[n.cell[0]+dx,n.cell[1]+dy];try{const next=[...n.path,p], c=routeCost(map,start,next).cost;if(c<=5)queue.push({cell:p,path:next,cost:c});}catch{}}}
if(path){s=act(s,'to-town','MOVE',{path:path.path});r.journey.beforeReturn=s.adventure.moves;s=act(s,'return','RETURN_TOWN',{});s=act(s,'reenter','ENTER_ADVENTURE',{});r.journey.afterReenter=s.adventure.moves;r.journey.path=path;}
const guard=[...map.guards][0].split(',').map(Number);let after;
for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)if(isOpen(map,guard[0]+dx,guard[1]+dy))after=[guard[0]+dx,guard[1]+dy];
const guarded=fresh();guarded.adventure={x:guard[0],y:guard[1],moves:5,visited:[],resolvedGuards:[],pendingEncounter:{id:'guard-open',cell:guard,status:'UNRESOLVED_COMBAT_BLOCKED'}};
try{const moved=act(guarded,'leave-guard','MOVE',{path:[after]});r.journey.pendingEncounterAllowsMove=true;r.journey.pendingEncounterAfter=moved.adventure.pendingEncounter;}catch(e){r.journey.pendingEncounterAllowsMove=false;r.journey.error=e.message;}
fs.writeFileSync(new URL('source-probes.json',import.meta.url),JSON.stringify(r,null,2));console.log(JSON.stringify(r));
