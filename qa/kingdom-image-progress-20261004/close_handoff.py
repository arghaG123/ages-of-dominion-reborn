from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path('C:/dev/ages-of-dominion-reborn');OUT=ROOT/'qa/kingdom-image-progress-20261004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
marker='Independent eight-Kingdom image audit — 4 October 2026'
base='**'+marker+':** Read [the focused verification]({report}) and [the complete corrected image-executor prompt]({prompt}). Fresh local check:24 distinct native5504x3072 outputs (8Adventure/8Tactical/8Defense), all journal hashes/decode PASS;8Kingdom unused and LOCAL_PREPARATION_REPAIR_REQUIRED. Copied blocker constants mix active/proposed geometry; existing blurred bases/untransmitted masks are not validated inputs. Image AI owns coherent local source/base/guide/contact/clearance repair, then each ready authorized Kingdom call; no Code AI Task3 or blanket guide approval prerequisite. Latest direct owner pacing:30 seconds after each successful image; classified Vertex429 =>wait60 seconds then retry affected request, with durable ownership/accounting; ambiguous outcomes/billing/access/budget remain blockers and no NO_IMAGE automatic retry. Saved protected exposure61.4324USD includes15reserve/invoicesUNKNOWN; remote readiness not queried. Generated spatial/content/runtime/owner gates remain separate. Planner QA/docs only; no provider, production/source/lock/budget, game/build/device/storage/Git mutation, executor messaging or delegation. Concurrent executor banners and history preserved below.'
paths={'CURRENT-STATUS.md':'docs/plan/','docs/SESSION-HANDOFF.md':'plan/','docs/BUILD-PROGRESS.md':'plan/','docs/PLANNER-VERIFIER-HANDOFF.md':'plan/','docs/plan/README.md':''}
changes=[]
for s,prefix in paths.items():
 p=ROOT/s;old=p.read_bytes(); text=old.decode('utf-8-sig')
 if marker in text:continue
 banner='> '+base.format(report=prefix+'KINGDOM-IMAGE-PROGRESS-VERIFICATION-2026-10-04.md',prompt=prefix+'KINGDOM-8-LOCAL-PREP-GENERATION-PROMPT-2026-10-04.txt')+'\n\n'
 new=(banner+text).encode('utf-8')
 # Read latest bytes, preserve all existing banners, refuse a detected concurrent edit.
 if p.read_bytes()!=old:raise RuntimeError('Concurrent documentation update: '+s)
 tmp=p.with_name(p.name+'.kingdom-audit.tmp');tmp.write_bytes(new);os.replace(tmp,p)
 changes.append({'file':s,'oldSHA256':hashlib.sha256(old).hexdigest(),'newSHA256':sha(p),'priorBytesPreserved':p.read_bytes()[len(banner.encode('utf-8')):]==text.encode('utf-8')})
rows=json.loads((OUT/'protected-start.json').read_text())
rows+= [{'file':r['file'],'sha256':r['sha256']} for r in json.loads((OUT/'outputs.json').read_text())]
rows+= json.loads((OUT/'hall-age-sources.json').read_text())
rows+= json.loads((OUT/'extra-checks.json').read_text())['alternates']
checked=[]
for r in rows:
 p=ROOT/r['file'];actual=sha(p) if p.exists() else None
 checked.append({'file':r['file'],'startSHA256':r['sha256'],'closingSHA256':actual,'unchanged':actual==r['sha256']})
closing={'snapshotUTC':datetime.now(timezone.utc).isoformat(),'runDirectories':[p.name for p in sorted((ROOT/'assets/high-res/interactive-4k-first32-20261003').glob('run-*'))],'allProtectedFilesUnchanged':all(r['unchanged'] for r in checked),'checkedCount':len(checked),'files':checked,'documentationChanges':changes,'providerQueried':False}
(OUT/'protected-closing.json').write_text(json.dumps(closing,indent=2),encoding='utf-8')
prompt=(ROOT/'docs/plan/KINGDOM-8-LOCAL-PREP-GENERATION-PROMPT-2026-10-04.txt').read_text(encoding='utf-8')
checks={'eightKingdomIDs':all('kingdom-terrain-'+a in prompt for a in ('stone','bronze','iron','medieval','gunpowder','industrial','modern','future')),'owner30Sec':bool('AT LEAST30 seconds' in prompt),'owner60Sec429Retry':bool('WAIT60 seconds' in prompt and 'RETRY THE AFFECTED REQUEST' in prompt),'noInventedRetryCap':'do not invent a retry-count cap' in prompt,'noNOIMAGERetry':'NO_IMAGE/rejected/incomplete output consumes its attempt' in prompt,'allProtectedUnchanged':closing['allProtectedFilesUnchanged'],'allPriorDocBodiesPreserved':all(r['priorBytesPreserved'] for r in changes),'fullCopyablePromptWords':len(prompt.split())}
(OUT/'handoff-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in closing.items() if k not in ('files','documentationChanges')},indent=2));print(json.dumps(checks,indent=2))
