// Pure memory diagnostics. Writes only this QA output.
import fs from 'node:fs/promises';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,validate,command} from '../../src/core/campaign.js';
import {createDefense,validateDefense,advanceDefense,deployHero} from '../../src/core/defense.js';
import {save,load,SAVE_KEY} from '../../src/core/save.js';
const fresh=()=>newCampaign(contract,data,1000);
const base=fresh(), defense=createDefense(base,data,{practice:'siege',waves:3});
const rows=[['negative-time',s=>s.time=-1],['invalid-queue',s=>s.queue='corrupt'],['negative-tower-damage',s=>s.towers[0].dmg=-10],['empty-active-queue',s=>s.queue=[]],['false-resolved-victory',s=>{s.status='RESOLVED';s.pendingSettlement=true;s.winner='p';}]].map(([id,edit])=>{
 const d=structuredClone(defense);edit(d);let direct=false,host=false;
 try{validateDefense(d);direct=true;}catch{}
 try{validate({...structuredClone(base),defense:d},data);host=true;}catch{}
 return{id,directAccepted:direct,campaignAccepted:host,status:!direct&&!host?'PASS':'FAIL'};
});
let endless=deployHero(createDefense(base,data,{practice:'endless',waves:3}),9);
const extensions=[];
for(let n=0;n<4;n++){
 endless=JSON.parse(JSON.stringify(endless));
 for(const enemy of endless.queue) if(!enemy.spawned){enemy.hp=0;enemy.spawnAt=0;}
 endless=advanceDefense(endless,1/60);
 extensions.push({waves:endless.waves,extensions:endless.extensions,status:endless.status,hero:endless.heroDeployed});
}
const memory={values:new Map(),getItem(k){return this.values.get(k)??null;},setItem(k,v){this.values.set(k,v);},removeItem(k){this.values.delete(k);}};
save(memory,base,data);
const second=command(base,{id:'rival',type:'CHOOSE_RIVAL',payload:{name:'Varek Iron-Eye'}},1000,data);
save(memory,second,data);
memory.setItem(SAVE_KEY,'broken-save');
const before=load(memory,data);
save(memory,newCampaign(contract,data,5000,99),data);
let backupValid=true;try { JSON.parse(memory.getItem(SAVE_KEY+'-backup')); }catch {backupValid=false;}
const backup={id:'valid-backup-after-damaged-live-replacement',beforeBackupValid:!!before.backup,afterBackupValid:backupValid,afterBackup:memory.getItem(SAVE_KEY+'-backup'),status:backupValid?'PASS':'FAIL',scope:'Memory fixture, damaged live replaced through exported save; real UI paths must also preserve backup'};
const result={at:new Date().toISOString(),rows,endless:{extensions,status:extensions.every((r,i)=>r.status==='ACTIVE'&&r.waves===6+3*i&&r.hero)?'PASS':'FAIL',scope:'Synthetic clears; no balance or natural campaign claim'},backup};
await fs.writeFile(new URL('./probes.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
