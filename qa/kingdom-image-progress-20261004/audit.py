"""Read-only production inspection; writes only scoped QA evidence. No network."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, math
from PIL import Image, ImageDraw, ImageChops
ROOT=Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/kingdom-image-progress-20261004'
OUT.mkdir(exist_ok=True)
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(n,d): (OUT/n).write_text(json.dumps(d,indent=2),encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
readme=ROOT/'docs/plan/README.md'
docs=[ROOT/p for p in ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']]
for m in re.findall(r'\]\(([^)]+)\)',readme.read_text(encoding='utf-8-sig')):
    if not m.startswith(('http','codex:')):
        p=(readme.parent/m.split('#')[0]).resolve()
        if p.is_file() and p.suffix.lower() in ('.md','.txt','.json','.html'): docs.append(p)
for name in ['INSTALLED-ENVIRONMENT.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','AUDIT-UPDATE.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md','IMPLEMENTATION-CONTRACT.json','KINGDOM-CANDIDATE-PLANNER-AUDIT-2026-10-03.md','INTERACTIVE-IMAGE-AI-START-GENERATION-PROMPT-2026-10-03.txt','IMAGE-EXECUTOR-PREPARATION-CORRECTION-2026-10-03.md','CODE-ART-INDEPENDENT-VERIFICATION-2026-10-04.md','CODE-ART-COMPLETE-REMAINING-WORK-PROMPT-2026-10-04.txt']:
    p=ROOT/'docs/plan'/name
    if p.is_file(): docs.append(p)
docrows=[]
for p in dict.fromkeys(docs):
    s=p.read_text(encoding='utf-8-sig')
    docrows.append({'file':rel(p),'sha256':sha(p),'charsRead':len(s),'firstHeadings':re.findall(r'^#{1,3} .+$',s,re.M)[:8]})
write('documents-read.json',docrows)
staging=ROOT/'assets/high-res/interactive-4k-first32-20261003'
protected=[]
def protect(p):
    if p.is_file(): protected.append({'file':rel(p),'sha256':sha(p)})
for p in [ROOT/'src/data/stone-scene.json',ROOT/'src/data/implementation-contract.json',ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json',ROOT/'docs/plan/image-production/budget-ledger.json',ROOT/'docs/plan/image-production/active-batch.lock.json']: protect(p)
attempts=[]; outputs=[]; seen_outputs=set()
for run in sorted(staging.glob('run-*')):
    for name in ('journal.json','manifest.json'): protect(run/name)
    jp=run/'journal.json'
    if not jp.exists(): continue
    journal=load(jp)
    for a in journal.get('attempts',[]):
        entry={**a,'runDirectory':rel(run)}
        attempts.append(entry)
        if a.get('outputFile'):
            p=ROOT/a['outputFile']
            if rel(p) in seen_outputs: continue
            seen_outputs.add(rel(p))
            im=Image.open(p); im.load()
            outputs.append({'id':a['id'],'file':rel(p),'run':run.name,'dimensions':list(im.size),'sha256':sha(p),'journalSHA':a.get('sha256'),'hashMatch':sha(p)==a.get('sha256'),'decode':True})
write('outputs.json',outputs)
write('attempts.json',attempts)
queue=load(ROOT/'docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json')
items=queue.get('items',queue.get('requests',[]))
if not items:
    for v in queue.values():
        if isinstance(v,list) and v and isinstance(v[0],dict) and 'id' in v[0]: items=v; break
contract=load(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json')
geom=contract['geometry']['kingdom']; mat=geom['worldToSource']
def project(x,y):
    a,b,c,d,e,f=mat
    return [a*x+c*y+e,b*x+d*y+f]
def poly(r):
    x,y,w,h=r
    return [project(x,y),project(x+w,y),project(x+w,y+h),project(x,y+h)]
packs=[]
plate=Image.new('RGB',(1376,8*410),(32,32,32)); draw=ImageDraw.Draw(plate)
for i,age in enumerate(('stone','bronze','iron','medieval','gunpowder','industrial','modern','future')):
    ident='kingdom-terrain-'+age
    pack=staging/'run-02-20261004-010239/packs'/ident
    val=load(pack/'validation.json'); g=load(pack/'geometry.json')
    files={}
    for p in sorted(pack.glob('*')):
        if p.is_file():
            protect(p); r={'file':rel(p),'sha256':sha(p)}
            if p.suffix=='.png':
                im=Image.open(p); im.load(); r['dimensions']=list(im.size)
            files[p.name]=r
    source=ROOT/val['sourceCandidate']; protect(source)
    row={'id':ident,'pack':rel(pack),'source':rel(source),'sourceSHA':sha(source),'sourceHashMatchesValidation':sha(source)==val['sourceCandidateSHA256'],'files':files,'geometryMatchesActiveContract':g==geom,'savedDisposition':val['disposition'],'savedPhysicalBlockers':val['physicalBlockers']}
    row['candidateSources']=[s for it in items if it.get('id')==ident for s in it.get('sources',[])]
    mc=Image.open(pack/'mask_change.png').convert('L'); mk=Image.open(pack/'mask_keep.png').convert('L')
    row['masksComplementary']=ImageChops.difference(ImageChops.invert(mc),mk).getbbox() is None
    row['changeMaskWhitePixels']=mc.histogram()[255]
    base=Image.open(pack/'base.png').convert('RGB'); guide=Image.open(pack/'guide.png').convert('RGB')
    for j,im in enumerate((base,guide)):
        im=im.resize((688,384),Image.Resampling.LANCZOS)
        plate.paste(im,(688*j,410*i+26))
    draw.text((8,410*i+6),ident+' | saved blurred base / guide',(255,255,255))
    packs.append(row)
plate.save(OUT/'kingdom-eight-packs.jpg',quality=90)
write('kingdom-packs.json',packs)
scene=load(ROOT/'src/data/stone-scene.json')
hall=Image.open(ROOT/scene['hall']['file']).convert('RGBA'); hall.load(); protect(ROOT/scene['hall']['file'])
alpha=hall.getchannel('A'); bbox=alpha.point(lambda x:255 if x>16 else 0).getbbox()
m=scene['hall']['matrix']
def hs(x,y): return [m[0][0]*x+m[0][1]*y+m[0][2],m[1][0]*x+m[1][1]*y+m[1][2]]
candidate=load(ROOT/'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json')
write('candidate-keys.json',{k:(list(v.keys()) if isinstance(v,dict) else str(v)[:180]) for k,v in candidate.items()})
claims={'matrix':mat,'activeTownhallPolygon':poly(geom['sites'][0]['rect']),'activeRoadStart':project(*geom['roads'][0][0]),'activeP11Polygon':poly(next(s['rect'] for s in geom['sites'] if s['id']=='P11')),'hallSize':list(hall.size),'hallAlphaGT16BBox':bbox,'activeHallFullRasterBounds':[hs(0,0),hs(1024,1024)],'activeHallAlphaBounds':[hs(bbox[0],bbox[1]),hs(bbox[2],bbox[3])],'fullRasterWidthActive':1024*.1312,'fullRasterWidthProposal':1024*.34,'proposalCentreDistance':math.dist((640,291.26),(644.6,297.4)),'blockerConstantsHardcodedIn':'scripts/interactive_4k_continuation_runner.py:541-582','maskConsumer':'request payload contains prompt, guide and base only; masks not attached by existing continuation runner','baseConsumer':'prepare_base_image uses BoxBlur(10) only within site bounding rectangles; no object silhouette removal'}
write('geometry-claims.json',claims)
hallbg=Image.new('RGBA',hall.size,(65,85,65,255)); hallbg.alpha_composite(hall); hallbg.convert('RGB').save(OUT/'hall-native.jpg',quality=94)
nativebase=Image.open(ROOT/packs[0]['source']).convert('RGBA')
hallscaled=hall.resize((round(1024*.1312),round(1024*.1312)),Image.Resampling.LANCZOS)
nativebase.alpha_composite(hallscaled,(round(m[0][2]),round(m[1][2])))
pd=ImageDraw.Draw(nativebase)
pd.line([tuple(p) for p in claims['activeTownhallPolygon']+[claims['activeTownhallPolygon'][0]]],fill='red',width=3)
pd.line([tuple(project(*p)) for p in geom['roads'][0]],fill='cyan',width=3)
nativebase.convert('RGB').save(OUT/'stone-active-registration.jpg',quality=94)
budget=load(ROOT/'docs/plan/image-production/budget-ledger.json')
summary={'snapshotUTC':stamp,'distinctSuccessfulIDs':len(set(o['id'] for o in outputs)),'successfulFiles':len(outputs),'allJournalHashesMatch':all(o['hashMatch'] for o in outputs),'nativeDimensions':sorted(set(tuple(o['dimensions']) for o in outputs)),'successesByMode':{mode:sum(o['id'].startswith(mode+'-') for o in outputs) for mode in ('kingdom','adventure','tactical','defense')},'kingdomPaidAttemptEntries':[a for a in attempts if a.get('id','').startswith('kingdom-') and (a.get('paidCalls',0)>0 or a.get('status') in ('SENDING_POST','SUCCEEDED','FAILED','UNKNOWN'))],'savedBudgetReconciliation':budget.get('reconciliationTrail'),'savedMutexExists':(ROOT/'docs/plan/image-production/submission.mutex.json').exists(),'documentsRead':len(docrows),'providerQueried':False,'productionMutated':False}
write('snapshot.json',summary)
write('protected-start.json',list({r['file']:r for r in protected}.values()))
print(json.dumps(summary,indent=2))
print(json.dumps(claims,indent=2))
print(json.dumps([{'id':p['id'],'source':p['source'],'candidateSources':p['candidateSources'],'geometryMatches':p['geometryMatchesActiveContract'],'guideSHA':p['files']['guide.png']['sha256'],'sourceSHA':p['sourceSHA']} for p in packs],indent=2))
