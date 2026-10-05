// Independent memory-only failure injection. Writes only this QA directory.
import fs from 'node:fs/promises';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command,validate} from '../../src/core/campaign.js';
import {save,load,decode,checksum,replaceCampaign,SAVE_KEY} from '../../src/core/save.js';
const fresh=()=>newCampaign(contract,data,1000);
const act=(s,id,type,payload={})=>command(s,{id,type,payload},s.clock,data);
const wrap=s=>{const payload=JSON.stringify(s);return JSON.stringify({schema:1,payload,checksum:checksum(payload)});};
const migration=[];
for(const [id,edit] of [
 ['chapter-null',s=>s.story.chapter=null],['choices-null',s=>s.story.choices=null],['futureSeen-null',s=>s.story.futureSeen=null],['milestones-null',s=>s.story.milestones=null],['quests-null',s=>s.quests=null],['q1-null',s=>s.quests.q1=null],['flags-null',s=>s.story.flags=null],
 ['chapter-string',s=>s.story.chapter='7'],['quest-claimed-string',s=>s.quests.q1.claimed='yes'],['chapter-choice-mismatch',s=>s.story.chapter=1]
]){
 const s=fresh();edit(s);let direct=false,decoded=false,error=null;
 try{validate(s,data);direct=true;}catch{}
 try{decode(wrap(s),data);decoded=true;}catch(e){error=e.message;}
 migration.push({id,directAccepted:direct,decodeAccepted:decoded,error,status:!direct&&decoded?'FAIL':'PASS'});
}
class Memory{
 values=new Map();corruptLive=false;failCleanup=false;
 getItem(k){return this.values.get(k)??null;}
 setItem(k,v){this.values.set(k,this.corruptLive&&k===SAVE_KEY?'corrupt-live-write':v);}
 removeItem(k){if(this.failCleanup&&k===SAVE_KEY+'-staged')throw Error('Injected cleanup failure');this.values.delete(k);}
}
function prepared(){const m=new Memory();let s=fresh();save(m,s,data);s=act(s,'rival','CHOOSE_RIVAL',{name:'Varek Iron-Eye'});save(m,s,data);return{m,s,oldLive:m.getItem(SAVE_KEY),oldBackup:m.getItem(SAVE_KEY+'-backup')};}
const replacement=[];
for(const mode of ['corrupt-live-write','staged-cleanup-throws']){
 const {m,s,oldLive,oldBackup}=prepared();const incoming=fresh();incoming.hero.class='mage';
 m.corruptLive=mode==='corrupt-live-write';m.failCleanup=mode==='staged-cleanup-throws';
 let returned=null,error=null;try{returned=replaceCampaign(m,incoming,data);}catch(e){error=e.message;}
 m.corruptLive=false;m.failCleanup=false;const now=load(m,data);
 const pass=mode==='corrupt-live-write'
  ? !!error&&!returned&&now.status==='DAMAGED'&&now.backup?.story.rival==='Varek Iron-Eye'
  : !error&&!!returned&&now.status==='VALID'&&now.state?.hero.class==='mage'&&now.state?.story.rival==null;
 replacement.push({mode,error,returned:!!returned,liveBytesUnchanged:m.getItem(SAVE_KEY)===oldLive,backupBytesUnchanged:m.getItem(SAVE_KEY+'-backup')===oldBackup,loadedStatus:now.status,loadedRival:now.state?.story.rival,loadedClass:now.state?.hero.class,recoveryBackupRival:now.backup?.story.rival,scope:'Failure injection, not an observed ordinary browser-storage failure',status:pass?'PASS':'FAIL'});
}
let story=fresh();story=act(story,'choice0','STORY_CHOICE',{index:0});let earlyRejected=false;try{act(story,'early1','STORY_CHOICE',{index:0});}catch{earlyRejected=true;}
const before=structuredClone(story.resources);let repeatsRejected=0;
for(let chapter=1;chapter<7;chapter++){story.age=chapter;story=act(story,'c'+chapter,'STORY_CHOICE',{index:0});}
const seven={chapter:story.story.chapter,age:story.age,earlyRejected};story.age=7;const prior=structuredClone(story.resources);story=act(story,'future','ACK_FUTURE',{});let duplicateRejected=false;try{act(story,'future-again','ACK_FUTURE',{});}catch{duplicateRejected=true;}
const result={at:new Date().toISOString(),migration,replacement,story:{...seven,futureGrantNone:JSON.stringify(prior)===JSON.stringify(story.resources),duplicateRejected},scope:'Synthetic memory fixtures; no game changes, natural eight-age completion, native/device or owner acceptance.'};
await fs.writeFile(new URL('./probes.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
