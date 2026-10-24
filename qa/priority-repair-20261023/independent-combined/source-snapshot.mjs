import {readFile,writeFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=process.cwd(),out='qa/priority-repair-20261023/independent-combined/';
const fingerprint=async path=>{const bytes=await readFile(path);return {path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')}};
async function walk(path){const rows=[];for(const entry of await readdir(path,{withFileTypes:true})){const child=path+'/'+entry.name;if(entry.isDirectory())rows.push(...await walk(child));else rows.push(child)}return rows}
const expected=JSON.parse(await readFile('qa/priority-repair-20261023/grok-medium/source-hashes.json','utf8'));
const comparisons=[];for(const row of expected.files){const actual=await fingerprint(row.path);comparisons.push({...actual,matches:actual.sha256===row.sha256&&actual.bytes===row.bytes})}
const files=await Promise.all((await walk('src')).concat(await walk('tests'),['index.html','scripts/serve.mjs']).sort().map(fingerprint));
await writeFile(out+'source-snapshot.json',JSON.stringify({capturedAt:new Date().toISOString(),algorithm:'SHA256',executorSnapshotComparisons:comparisons,files},null,2)+'\n');
console.log(JSON.stringify({files:files.length,executorMatches:comparisons.filter(row=>row.matches).length,executorTotal:comparisons.length,main:files.find(row=>row.path==='src/client/main.js')}));
