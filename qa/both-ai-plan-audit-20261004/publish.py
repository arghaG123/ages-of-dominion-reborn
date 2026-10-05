"""Publish planner docs only, preserving exact prior bytes and concurrent history."""
from pathlib import Path
import json,hashlib,re,os
from datetime import datetime,timezone
R=Path('C:/dev/ages-of-dominion-reborn');Q=Path(__file__).parent
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
# Complete all explicitly listed reading-order items, alongside the original linked-document pass.
prior=read(Q/'documents-read.json');names={R/x['file'] for x in prior if x['exists']}
names.update(R/'docs/plan'/x for x in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','references/visual-targets/index.json','references/visual-targets/README.md'])
names.update(R/'docs/plan'/x for x in ['BOTH-AI-INDEPENDENT-VERIFICATION-2026-10-04.md','WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md','CODE-AI-NEXT-AFTER-WHOLE-PLAN-AUDIT-2026-10-04.txt','IMAGE-AI-NEXT-LOCAL-DELIVERY-2026-10-04.txt'])
names.add(R/'docs/PLANNER-VERIFIER-HANDOFF.md')
docs=[]
for p in sorted(names):
 text=p.read_text(encoding='utf-8-sig');v=json.loads(text) if p.suffix=='.json' else None
 docs.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'charactersRead':len(text),'headings':re.findall(r'^#{1,4} .+$',text,re.M),'JSONKeysOrCount':list(v)[:40] if isinstance(v,dict) else len(v) if isinstance(v,list) else None})
(Q/'documents-read-complete.json').write_text(json.dumps(docs,indent=2),encoding='utf-8')
targets=['CURRENT-STATUS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/FULL-IMPLEMENTATION-SPEC.md','docs/plan/MASTER-PLAN.md','docs/plan/REQUIREMENTS-TRACEABILITY.md','docs/plan/VISUAL-DESIGN.md','docs/plan/INSTALLATION-TRANSFER.md']
publication=[]
for name in targets:
 p=R/name;old=p.read_bytes();stem='docs/plan/' if p.parent==R else 'plan/' if p.parent==R/'docs' else ''
 audit=stem+'BOTH-AI-INDEPENDENT-VERIFICATION-2026-10-04.md';plan=stem+'WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md';code=stem+'CODE-AI-NEXT-AFTER-WHOLE-PLAN-AUDIT-2026-10-04.txt';img=stem+'IMAGE-AI-NEXT-LOCAL-DELIVERY-2026-10-04.txt'
 banner=(f'> **Current both-AI and whole-plan audit — 4 October 2026:** Read [fresh executor verification]({audit}) and [current precedence, full35requirement crosswalk and planning corrections]({plan}); hand the owner-selected executors [Code/Art next task]({code}) and [Image local-delivery next task]({img}). Fresh75tests/coreguard journey PASS; currentunsignedrelease248webfiles match root/dist, previewID/zero packagedpermissions/asset-loader static PASS; olddebug stale. Actual Knight/Mage assemblies and Challenge seed/start are progress; static Hero clips, schematic Adventure, missing Hero/skill/item workflows and matte/identity/registration gaps leave fullgame INCOMPLETE. All510originals/73native+raw preservation and recorded derivative bindings PASS; new236derivative PNGs decode, but croppedheads, retainedsheet/background content and162RGB rig slices FAIL usable-role gates. DeadUNKNOWN/release repairs PASS; delayedmutex contention, unboundsuccessreuse and overwrittensubattempt history FAIL. Main/unified stated70.7012USD agree but unique-attempt/base arithmetic remains unresolved; invoicesUNKNOWN, no release/spend. Existingpaid scope exhausted: NO_NEW_PAID_CALLS. DeviceSTOPPED; storage/nullrestore and positive-morale choice affect their actions only. Latest authority/addendum supersedes contradictory historical phase/orientation/stage/batch text below. Planner QA/docs only, no provider/production/game/build/device/storage/Git mutation, executor messaging or delegation. Concurrent history preserved.\r\n\r\n')
 new=banner.encode('utf-8')+old;tmp=p.with_name(p.name+'.planner-audit.tmp');tmp.write_bytes(new)
 if p.read_bytes()!=old:
  tmp.unlink();raise RuntimeError('Concurrent documentation edit; refresh '+name)
 os.replace(tmp,p)
 publication.append({'file':name,'priorSHA256':hashlib.sha256(old).hexdigest(),'publishedSHA256':sha(p),'entirePriorBytesPreserved':p.read_bytes().endswith(old)})
links=[]
for x in publication:
 p=R/x['file'];first=p.read_text(encoding='utf-8-sig').split('\n\n',1)[0]
 for link in re.findall(r'\]\(([^)]+)\)',first):links.append({'from':x['file'],'target':link,'exists':(p.parent/link).resolve().is_file()})
(Q/'publication.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'documentsRead':len(docs),'updates':publication,'newLinks':links},indent=2),encoding='utf-8')
# Immutable before/closing comparison, not an attribution of concurrent edits to the planner.
start=read(Q/'protected-start.json');rows=[]
for x in start['files']:
 p=R/x['file'];h=sha(p) if p.is_file() else None;rows.append({'file':x['file'],'startSHA256':x['sha256'],'closingSHA256':h,'unchanged':h==x['sha256']})
(Q/'protected-closing.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'rows':rows,'unchanged':sum(x['unchanged'] for x in rows),'total':len(rows),'changed':[x['file'] for x in rows if not x['unchanged']]},indent=2),encoding='utf-8')
restore=read(R/'qa/full-asset-verifier-20261003/restore-manifest-draft.json')
(Q/'git-storage.json').write_text(json.dumps({'head':'cff552880ae15c892b736ac7847f6753787ca58f','branch':'main','trackedAssets':67,'restoreDestination':restore.get('destination'),'verifiedRows':sum(bool(x.get('externalCopyVerified') and x.get('independentBackupVerified') and x.get('restoreVerified')) for x in restore['files']),'remoteQueried':False,'unrecordedBackups':'UNKNOWN','device':'STOPPED'},indent=2),encoding='utf-8')
print(json.dumps({'documentsRead':len(docs),'updates':len(publication),'newLinks':len(links),'brokenNewLinks':[x for x in links if not x['exists']],'protectedUnchanged':sum(x['unchanged'] for x in rows),'protectedTotal':len(rows),'changed':[x['file'] for x in rows if not x['unchanged']]},indent=2))
