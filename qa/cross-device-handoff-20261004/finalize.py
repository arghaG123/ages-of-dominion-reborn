"""Validate the portable handoff, add documentation pointers, check preservation."""
from pathlib import Path
import hashlib,json,re,subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
DOC=ROOT/'docs/CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
 return h.hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
targets={'CURRENT-STATUS.md':'docs/CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','START-HERE.md':'docs/CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','docs/SESSION-HANDOFF.md':'CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','docs/BUILD-PROGRESS.md':'CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','docs/PLANNER-VERIFIER-HANDOFF.md':'CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','docs/plan/README.md':'../CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','docs/migration/README.md':'../CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md'}
pointer_rows=[]
for name,link in targets.items():
 p=ROOT/name; before=p.read_bytes(); s=before.decode('utf-8-sig')
 marker='**Cross-device handoff and parallel correction workflow — 5 October 2026:**'
 banner=f'> {marker} Read [the portable handoff with COMPLETE separate Code/Image prompts]({link}). Owner wants the whole game/every screen patched while Image AI corrects scenes/assets, then Code integrates each verified corrected image. Latest saved ordinary journey records prepared Siege win and earned shield/equip/reload (executor evidence; 22 capture hashes checked), superseding the old zero-wave result for that journey. Existing 02f85e52 APK is stale against four current web files. Image v6 25 hash/decode bindings pass but matte/joint/scene gaps remain; whole product INCOMPLETE. Git main cff5528 is dirty/staged/untracked; Git-only transfer misses current work and ignored assets. Migration manifests have changed/missing latest rows; recorded backup locations unavailable in this inspection. Refresh transfer snapshot; no new paid calls/device authority. Planner local QA/docs only; no game/build/provider/device/Git/storage mutation or executor dispatch. Historical and concurrent records preserved below.\n\n'
 if marker not in s:
  p.write_text(banner+s,encoding='utf-8')
 pointer_rows.append({'path':name,'beforeSHA256':hashlib.sha256(before).hexdigest(),'afterSHA256':digest(p),'method':'prepend preserved prior content'})
save('documentation-pointers.json',pointer_rows)

s=DOC.read_text(encoding='utf-8'); links=[]
for target in re.findall(r'\]\(([^)]+)\)',s):
 if target.startswith(('http://','https://','#')): continue
 path=(DOC.parent/target.split('#')[0]).resolve()
 links.append({'target':target,'exists':path.exists(),'repositoryRelative':not Path(target).is_absolute() and str(path).startswith(str(ROOT))})
save('portable-link-check.json',{'links':links,'missing':[r for r in links if not r['exists']],'outsideRepository':[r for r in links if not r['repositoryRelative']],'twoCompleteSeparatePrompts':all(t in s for t in ['COMPLETE SEPARATE PROMPT — CODE AI','COMPLETE SEPARATE PROMPT — IMAGE AI']),'documentSHA256':digest(DOC),'documentBytes':DOC.stat().st_size})
before=json.loads((OUT/'protected-before.json').read_text());changes=[];missing=[]
for r in before:
 p=ROOT/r['path']
 if not p.exists():missing.append(r['path'])
 elif digest(p)!=r['sha256']:changes.append({'path':r['path'],'beforeSHA256':r['sha256'],'afterSHA256':digest(p),'classification':'documentation pointer' if r['path'] in targets else 'concurrent or external change; planner did not edit this file'})
save('preservation-result.json',{'checkedUTC':datetime.now(timezone.utc).isoformat(),'baselineFiles':len(before),'unchanged':len(before)-len(changes)-len(missing),'changed':changes,'missing':missing,'plannerAllowedWrites':'new QA directory, portable document, prepended documentation pointers only'})
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
print(json.dumps({'document':str(DOC),'bytes':DOC.stat().st_size,'missingLinks':[r for r in links if not r['exists']],'outsideLinks':[r for r in links if not r['repositoryRelative']],'preservationChanged':changes,'preservationMissing':missing,'unchangedProtected':len(before)-len(changes)-len(missing),'currentHEAD':head},indent=2))
