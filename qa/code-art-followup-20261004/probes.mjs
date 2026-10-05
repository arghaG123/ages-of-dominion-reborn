// Pure memory QA; output only in this diagnostic directory.
import fs from 'node:fs/promises';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,validate,questReady} from '../../src/core/campaign.js';
import {save,load,encode,decode,checksum,restoreBackup,SAVE_KEY} from '../../src/core/save.js';
const fresh=()=>newCampaign(contract,data,1000);const act=(s,id,type,payload={})=>command(s,{id,type,payload},s.clock,data);
class Memory{values=new Map();failKey=null;getItem(k){return this.values.get(k)??null;}setItem(k,v){if(k===this.failKey)throw Error('QA quota');this.values.set(k,v);}removeItem(k){this.values.delete(k);}}
const mem=new Memory();let s=fresh();save(mem,s,data);s=act(s,'rival','CHOOSE_RIVAL',{name:'Varek Iron-Eye'});save(mem,s,data);const kept=mem.getItem(SAVE_KEY+'-backup');mem.setItem(SAVE_KEY,'damaged-QA');save(mem,fresh(),data);const damagedReplacement={validBackup:mem.getItem(SAVE_KEY+'-backup')===kept,damagedRetained:mem.getItem(SAVE_KEY+'-damaged')==='damaged-QA',liveValid:load(mem,data).status==='VALID'};
mem.setItem(SAVE_KEY,'damaged-QA-2');mem.failKey=SAVE_KEY;let failed=false;try{save(mem,s,data);}catch{failed=true;}const quota={failed,backupUnchanged:mem.getItem(SAVE_KEY+'-backup')===kept,damagedLiveUnchanged:mem.getItem(SAVE_KEY)==='damaged-QA-2'};mem.failKey=null;restoreBackup(mem,data);const restore={valid:load(mem,data).status==='VALID',backupUnchanged:mem.getItem(SAVE_KEY+'-backup')===kept,damagedRetained:mem.getItem(SAVE_KEY+'-damaged')==='damaged-QA'};
const malformed=[];let chosen=act(fresh(),'c0','STORY_CHOICE',{index:0});
for(const [id,edit] of [['chapter-choice-mismatch',s=>s.story.choices=[]],['invalid-claimed-type',s=>s.quests.q1.claimed='claimed'],['invalid-chapter-type',s=>s.story.chapter='7']]){
 const m=structuredClone(chosen);edit(m);let direct=false,decoded=null,error=null;try{validate(m,data);direct=true;}catch{}const payload=JSON.stringify(m);try{decoded=decode(JSON.stringify({schema:1,payload,checksum:checksum(payload)}),data);}catch(e){error=e.message;}
 malformed.push({id,directAccepted:direct,decodeAccepted:!!decoded,decodedChapter:decoded?.story.chapter,decodedFirstQuest:decoded?.quests.q1.claimed,error,status:!direct&&decoded?'FAIL':'PASS'});
}
let progression=fresh();for(let i=0;i<7;i++)progression=act(progression,'story'+i,'STORY_CHOICE',{index:0});const chapters={age:progression.age,chapter:progression.story.chapter,resources:progression.resources,scope:'Seven age-themed chapters can all be claimed at Stone; age/progression eligibility requires explicit binding rather than inferred approval.'};
let win=fresh();win.story.flags['cleared:false']=false;const falseFlag={ready:questReady(win,data,'q1'),scope:'A false cleared flag is counted as a win; semantic save validation is open.'};
const legacy=structuredClone(chosen);delete legacy.story.chapter;delete legacy.story.choices;delete legacy.story.futureSeen;delete legacy.story.milestones;legacy.quests={};const payload=JSON.stringify(legacy);let legacyAccepted=false;try{decode(JSON.stringify({schema:1,payload,checksum:checksum(payload)}),data);legacyAccepted=true;}catch{}
const result={at:new Date().toISOString(),damagedReplacement,quota,restore,malformed,chapters,falseFlag,legacyAccepted,scope:'Memory fixtures; no natural gameplay, file storage, native or owner acceptance.'};await fs.writeFile(new URL('./probes.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
