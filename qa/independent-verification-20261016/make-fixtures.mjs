// Explicit synthetic visual fixtures. Never evidence of earned progression.
import fs from 'node:fs';
import data from '../../src/data/reference-data.json' with {type:'json'};
import contract from '../../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,validate} from '../../src/core/campaign.js';
import {encode} from '../../src/core/save.js';
const out=new URL('./fixtures/',import.meta.url); fs.mkdirSync(out,{recursive:true});
const classes=Object.keys(data.CLASSES);
const types=['lumber','farm','quarry','mine','barracks','workshop','hall','armory','lumber','farm','quarry','mine','lumber','farm','quarry','mine','lumber'];
function make(age,cls){
 const s=newCampaign(contract,data,Date.now(),123456789); s.age=age;s.hero.class=cls;s.tutorial.skipped=true;
 s.resources={food:100000,wood:100000,stone:100000,gold:100000};
 let i=0; for(const p of s.plots){ if(p.id==='townhall'){p.level=8;continue;}p.type=types[i++];p.level=3; }
 s.walls.level=3;
 for(const slot of ['helm','weapon','offhand','armor','boots','accessory'])s.hero.equip[slot]={id:`fixture-${slot}`,kind:'gear',slot,age,quality:0};
 validate(s,data);return s;
}
for(let age=0;age<8;age++)fs.writeFileSync(new URL(`age-${age}.json`,out),encode(make(age,'knight'),data));
for(const cls of classes)fs.writeFileSync(new URL(`class-${cls}.json`,out),encode(make(0,cls),data));
fs.writeFileSync(new URL('./fixture-note.json',import.meta.url),JSON.stringify({synthetic:true,earned:false,purpose:'Visual and source binding only',ageCount:8,classes},null,2));
console.log('Synthetic age and class fixtures created and validated');
