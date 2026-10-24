import {readFile,writeFile} from 'node:fs/promises';
const records=[['CURRENT-STATUS.md','qa/priority-repair-20261023/independent-combined/REPORT.md'],['docs/SESSION-HANDOFF.md','../qa/priority-repair-20261023/independent-combined/REPORT.md'],['docs/BUILD-PROGRESS.md','../qa/priority-repair-20261023/independent-combined/REPORT.md']];
for(const [path,link] of records){
 const original=await readFile(path);
 const heading='## 23 October independent combined priority-repair verification';
 if(original.toString('utf8').startsWith(heading))continue;
 const prefix=heading+'\r\n\r\nIndependent integrated Node suite: **303/303 PASS**. Final integrated executor fingerprints match **10/10**. [Current report]('+link+') records live natural skill-offer/reload, deployment at three landscape sizes, Defense targets, and isolated native damaged-save export/backup/invalid-import recovery. Remaining: **H-01** positive spell uses damage-hit presentation/static plate motion; **D-01** casting allowance wording; **D-02** zero battle mana disappears. **M03 remains High / owner-deferred.** No reproduced Critical defect in the bounded checks; wider age/journey/visual/storage acceptance remains VERIFY. Preserve completed repairs and core mechanics. This verifier changed QA/handoff records only; no production repair, paid generation, build/device/Git publication. Whole game remains **INCOMPLETE**.\r\n\r\n';
 await writeFile(path,Buffer.concat([Buffer.from(prefix,'utf8'),original]));
}
console.log('Prepended current combined-audit note; prior bytes preserved.');
