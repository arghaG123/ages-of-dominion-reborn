from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=ROOT/'qa/image-next-task-20261004'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
later=read(QA/'later73-preparation-manifest.json')
later['createdAt']=datetime.now(timezone.utc).isoformat()
later['role']='PLANNER_VERIFIER_LOCAL_PROPOSAL'; later['providerCallsPerformed']=False
save(ROOT/'docs/plan/IMAGE-LATER73-LOCAL-PREPARATION-MANIFEST-2026-10-04.json',later)
rows=[]
for x in read(QA/'outputs.json'):
    p=ROOT/x['file']; pack=p.parent
    redundant=[]
    for c in [pack/'comparison.png',*sorted((pack/'viewports').glob('*.png'))]:
        if c.exists(): redundant.append({'file':c.relative_to(ROOT).as_posix(),'bytes':c.stat().st_size,'sha256':sha(c),'kind':'reproducible-review-raster','action':'REMOVE_ONLY_AFTER_INDEPENDENT_ASSET_PASS_DESTINATION_AND_REFERENCE_CLOSURE','performed':False})
    rp=pack/'response.json'
    if rp.exists(): redundant.append({'file':rp.relative_to(ROOT).as_posix(),'bytes':rp.stat().st_size,'sha256':sha(rp),'kind':'mixed-unique-response-metadata-and-duplicate-image-payload','action':'COMPACT_ALL_NON_IMAGE_FIELDS_AND_VERIFY_PAYLOAD_EQUIVALENCE; RETIRE_EXACT_RAW_BYTES_ONLY_WITH_APPLICABLE_PRESERVATION_GATE','performed':False})
    rows.append({'id':x['id'],'sourceFile':x['file'],'sourceSHA256':x['sha256'],'sourceBytes':p.stat().st_size,'dimensions':x['dimensions'],'targetFile':'assets/production/final-native4k/'+x['id']+'.png','promotionStatus':'NOT_ELIGIBLE_PENDING_INDEPENDENT_ASSET_PASS','technicalStatus':'PASS','contentStatus':'FAIL' if x['id'].startswith('kingdom') else 'UNVERIFIED','spatialStatus':'FAIL' if x['id'] in ['kingdom-terrain-stone','kingdom-terrain-bronze','kingdom-terrain-iron','kingdom-terrain-medieval','kingdom-terrain-gunpowder','kingdom-terrain-industrial','defense-terrain','defense-terrain-hills'] else 'UNVERIFIED','independentApprovalReference':None,'ownerAcceptance':'UNVERIFIED','runtimeApproved':False,'movePerformed':False,'retirementCandidates':redundant})
save(QA/'promotion-and-cleanup-candidates.json',{'ownerAuthority':'Conditional image-only move and redundant cleanup after independent verification; explicit 4 October 2026 chat instructions','targetFolder':'assets/production/final-native4k','targetImagesOnly':True,'eligibleRowsNow':0,'items':rows})
banner=('> **Independent first32 image verification and owner cleanup direction — 4 October 2026:** '
        'Read [{reportLabel}]({report}) and [{promptLabel}]({prompt}). Fresh32distinct native5504x3072 outputs/response bytes/hashes/decode PASS, including8Kingdom Run6; earlier24 unchanged. '
        'All8Kingdom bare-content FAIL (baked plots/foundations/kit), with measured crossing/ground/topology failures; physical/composite/runtime/owner gates remain separate. '
        'Image AI next: measured32delivery/spatial manifest, useful local recovery, complete73proposed2Kpacks (purchase INACTIVE), offline continuity repairs. '
        'Owner now explicitly requires independently passed images moved to image-only assets/production/final-native4k, then actual proven-redundancy cleanup after destination hash/reference checks; current0rows independently approved for promotion. '
        'First32staging2.655GiB:793.44MiB finalPNG,1563.26MiB base64responses,219.57MiB comparisons/viewports. Unique evidence/history remains preserved; scoped preservation blocks affect their files only. '
        'Saved exposure62.8346USD includes15reserve/invoicesUNKNOWN/error-liability reconciliation open; remote state not queried. '
        'Planner QA/docs only; no production/provider/lock/budget/game/build/device/storage/Git mutation, executor message or delegation. Preserve concurrent banners/history below.\n\n')
targets={'CURRENT-STATUS.md':'docs/plan/','docs/SESSION-HANDOFF.md':'plan/','docs/BUILD-PROGRESS.md':'plan/','docs/PLANNER-VERIFIER-HANDOFF.md':'plan/','docs/plan/README.md':'','docs/plan/GIT-ASSET-STORAGE-PLAN-2026-10-03.md':''}
docchecks=[]
for file,prefix in targets.items():
    p=ROOT/file; old=p.read_bytes()
    addition=banner.format(reportLabel='the new scoped image audit',report=prefix+'IMAGE-FIRST32-INDEPENDENT-VERIFICATION-2026-10-04.md',promptLabel='complete next image-AI task',prompt=prefix+'IMAGE-AI-VALIDATE-PREPARE-AND-CLEANUP-PROMPT-2026-10-04.txt').encode('utf-8')
    p.write_bytes(addition+old)
    docchecks.append({'file':file,'originalBodySHA256':hashlib.sha256(old).hexdigest(),'oldBodyPreserved':p.read_bytes()[len(addition):]==old})
start=read(QA/'protected-start.json'); close=[]
for x in start['files']:
    p=ROOT/x['file']; current=sha(p) if p.exists() else None
    close.append({'file':x['file'],'startSHA256':x['sha256'],'closingSHA256':current,'unchanged':current==x['sha256']})
save(QA/'protected-closing.json',{'at':datetime.now(timezone.utc).isoformat(),'checked':len(close),'unchanged':sum(x['unchanged'] for x in close),'changed':[x for x in close if not x['unchanged']],'rows':close})
prompt=ROOT/'docs/plan/IMAGE-AI-VALIDATE-PREPARE-AND-CLEANUP-PROMPT-2026-10-04.txt'
save(QA/'handoff-checks.json',{'docBodies':docchecks,'protectedUnchanged':all(x['unchanged'] for x in close),'promptWords':len(prompt.read_text(encoding='utf-8').split()),'promptSHA256':sha(prompt),'73Rows':len(later['items']),'promotionRows':len(rows),'eligibleRows':0,'storageMoveOrDeletionPerformed':False,'providerCallsPerformed':False,'executorsContacted':False,'subagentsSpawned':False})
print(json.dumps(read(QA/'handoff-checks.json'),indent=2))
