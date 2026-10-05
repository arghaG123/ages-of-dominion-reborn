"""Planner-only local audit. Reads production; writes only this QA directory."""
from pathlib import Path
import json, hashlib, re, base64, io
from datetime import datetime, timezone
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('C:/dev/ages-of-dominion-reborn')
QA=ROOT/'qa/image-next-task-20261004'
RUN=ROOT/'assets/high-res/interactive-4k-first32-20261003/run-06-kingdom-20261004-023321'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(name,obj): (QA/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()

# Read required documents in full, catalog their identity and headings.
required=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
index=(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')
for ref in re.findall(r'\]\(([^)]+)\)',index):
    p=(ROOT/'docs/plan'/ref.split('#')[0]).resolve()
    if p.is_file() and p.suffix.lower() in ['.md','.txt','.json']: required.append(rel(p))
for name in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md','IMPLEMENTATION-CONTRACT.json','KINGDOM-8-LOCAL-PREP-GENERATION-PROMPT-2026-10-04.txt','KINGDOM-IMAGE-PROGRESS-VERIFICATION-2026-10-04.md','INTERACTIVE-IMAGE-AI-START-GENERATION-PROMPT-2026-10-03.txt','IMAGE-EXECUTOR-PREPARATION-CORRECTION-2026-10-03.md','INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json','FIRST-32-4K-KINGDOM-COMPLETION-REPORT-2026-10-04.md','CODE-ART-NEXT-EXECUTION-PROMPT-2026-10-04.txt']:
    required.append('docs/plan/'+name)
docs=[]
for name in dict.fromkeys(required):
    p=ROOT/name
    if not p.exists(): docs.append({'file':name,'missing':True}); continue
    content=p.read_text(encoding='utf-8-sig')
    docs.append({'file':name,'sha256':sha(p),'chars':len(content),'headings':re.findall(r'^#{1,3} .+$',content,re.M),'scopeExcerpts':[l[:850] for l in content.splitlines() if any(k in l.lower() for k in ['later73','later 73','2k groups','storage destination','planner/verifier only','six functional'])][:5]})
save('documents-read.json',docs)

protected=set()
for pattern in ['assets/production/*/images/*.png','assets/production/*/manifest.json','assets/production/*/ledger.json','assets/high-res/**/output.png','assets/high-res/**/manifest.json','assets/high-res/**/journal.json','assets/high-res/**/geometry.json','assets/high-res/**/request_meta.json','assets/high-res/**/base.png','assets/high-res/**/guide.png','assets/delivery/**/*.png','src/**/*','docs/plan/image-production/*.json','scripts/interactive_4k*.py','docs/plan/IMPLEMENTATION-CONTRACT.json']:
    protected.update(p for p in ROOT.glob(pattern) if p.is_file())
snapshot={'at':datetime.now(timezone.utc).isoformat(),'files':[{'file':rel(p),'sha256':sha(p)} for p in sorted(protected)]}
save('protected-start.json',snapshot)
queue=read(ROOT/'docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json')
man=read(RUN/'manifest.json'); jour=read(RUN/'journal.json')
first=[x for x in queue['items'] if x['group']=='4K-FIRST-32']
outputs=[]; bindings=[]; history=[]
for jp in sorted((ROOT/'assets/high-res/interactive-4k-first32-20261003').glob('*/journal.json')):
    j=read(jp)
    for a in j.get('attempts',[]):
        history.append({'run':jp.parent.name,'id':a.get('id'),'status':a.get('status',a.get('disposition')),'subattempts':a.get('subattempts',[]),'errorCode':a.get('errorCode'),'finishReason':a.get('finishReason'),'outputFile':a.get('outputFile')})
for item in sorted(man['items'],key=lambda x:x['order']):
    p=ROOT/item['outputFile']; actual=sha(p)
    with Image.open(p) as im: im.load(); dims=list(im.size); fmt=im.format
    refs=[]
    for jp in (ROOT/'assets/high-res/interactive-4k-first32-20261003').glob('*/journal.json'):
        for a in read(jp).get('attempts',[]):
            if a.get('outputFile')==item['outputFile'] and a.get('sha256'): refs.append({'run':jp.parent.name,'matches':a['sha256']==actual})
    outputs.append({'order':item['order'],'id':item['id'],'file':item['outputFile'],'sha256':actual,'dimensions':dims,'aspect':'43:24' if dims==[5504,3072] else None,'format':fmt,'decode':'PASS','manifestMatch':actual==item['sha256'],'journalMatches':refs,'spatialClaim':item.get('spatialStatus'),'actualSpatialGate':'UNVERIFIED','ownerAcceptance':'UNVERIFIED','runtimeApproved':False})
    pack=p.parent
    rp=pack/'response.json'
    if rp.exists():
        response=read(rp); imgs=[]
        for c in response.get('candidates',[]):
            for part in c.get('content',{}).get('parts',[]):
                if 'inlineData' in part:
                    data=base64.b64decode(part['inlineData']['data']); imgs.append({'sha256':hashlib.sha256(data).hexdigest(),'mimeType':part['inlineData'].get('mimeType'),'matchesOutput':hashlib.sha256(data).hexdigest()==actual})
        row={'id':item['id'],'responseFile':rel(rp),'responseSHA256':sha(rp),'responseImageCount':len(imgs),'responseImages':imgs,'finishReasons':[c.get('finishReason') for c in response.get('candidates',[])],'usage':response.get('usageMetadata'),'requestFiles':[rel(x) for x in pack.glob('request*')]}
        meta=pack/'request_meta.json'
        if meta.exists():
            m=read(meta); row['requestMetaKeys']=list(m); row['guideMatch']=m.get('guide_sha256')==sha(pack/'guide.png'); row['baseMatch']=m.get('base_sha256')==sha(pack/'base.png'); row['requestConfig']=m.get('generationConfig'); row['promptSHA256']=hashlib.sha256(m.get('prompt','').encode()).hexdigest()
        val=pack/'validation.json'
        if val.exists():
            v=read(val); source=v.get('sourceCandidate')
            if source: row['sourceBinding']={'file':source,'actualSHA256':sha(ROOT/source),'matches':sha(ROOT/source)==v.get('sourceCandidateSHA256')}
        bindings.append(row)
save('outputs.json',outputs); save('bindings.json',bindings); save('history.json',history)
saved=read(ROOT/'docs/plan/image-production/budget-ledger.json')
lock=read(ROOT/'docs/plan/image-production/active-batch.lock.json')
success=[a for a in jour['attempts'] if a.get('status')=='SUCCEEDED']
def stamp(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
pacing=[]
for prev,nxt in zip(success,success[1:]):
    ss=nxt['subattempts'][0]['startedAt']
    pacing.append({'previous':prev['id'],'next':nxt['id'],'previousCompletedAt':prev['completedAt'],'nextStartedAt':ss,'recordedGapSeconds':(stamp(ss)-stamp(prev['completedAt'])).total_seconds(),'resolution':'whole-second stamps; exact subsecond gap unproved'})
save('accounting-and-pacing.json',{'localLock':lock,'mutexPresent':(ROOT/'docs/plan/image-production/submission.mutex.json').exists(),'savedReconciliation':saved.get('reconciliationTrail'),'run6Usage':jour['summary'],'sumSuccessfulRun6RecordedCostUSD':sum(a['actualCostUSD'] for a in success),'pacing':pacing,'remoteStatus':'NOT_QUERIED'})

geom=read(RUN/'packs/kingdom-terrain-stone/geometry.json')
a,b,c,d,e,f=geom['worldToSource']
def point(x,y): return (a*x+c*y+e,b*x+d*y+f)
def poly(rect):
    x,y,w,h=rect
    return [point(x,y),point(x+w,y),point(x+w,y+h),point(x,y+h)]
def inside_rect_world(p,rect):
    sx,sy=p; det=a*d-b*c; wx=(d*(sx-e)-c*(sy-f))/det; wy=(-b*(sx-e)+a*(sy-f))/det
    x,y,w,h=rect
    return x<=wx<=x+w and y<=wy<=y+h
sites=geom['sites']; th=sites[0]; overlaps=[]
for i,s in enumerate(sites):
    x,y,w,h=s['rect']
    for t in sites[i+1:]:
        xx,yy,ww,hh=t['rect']
        if min(x+w,xx+ww)>max(x,xx) and min(y+h,yy+hh)>max(y,yy): overlaps.append([s['id'],t['id']])
excl=geom['hallFramingProposal']['envelopeExclusiveSource']
bridge=geom['bridges'][0]; bx,by,bw,bh=bridge['rect']
anal={'geometry':geom,'sitePolygons':[{'id':s['id'],'polygon':poly(s['rect'])} for s in sites],'pairwise2DRectOverlaps':overlaps,'hallReservationPolygon':poly(th['rect']),'roofEnvelopeCornersInsideCivicGroundPolygon':[inside_rect_world(p,th['rect']) for p in [(excl[0][0],excl[0][1]),(excl[1][0],excl[0][1]),(excl[1][0],excl[1][1]),(excl[0][0],excl[1][1])]],'roadStartSource':point(*geom['roads'][0][0]),'bridgePolygon':poly(bridge['rect']),'bridgeEndsAtWorldX':bx+bw,'riverFarBankWorldX':14,'bridgeFarBankGapWorldX':14-(bx+bw),'perPadApproachRecords':geom.get('approaches'),'hallContactMeasurementRecords':geom.get('hallContact'),'nativeToLogicalScale':[4,4]}
save('geometry-checks.json',anal)

# Bounded QA plates; never delivery/production modifications.
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
king=[x for x in outputs if x['id'].startswith('kingdom')]
sheet=Image.new('RGB',(1376,4*416),'#eee'); sd=ImageDraw.Draw(sheet)
for i,x in enumerate(king):
    im=Image.open(ROOT/x['file']).convert('RGB'); im.thumbnail((688,384))
    xx=(i%2)*688; yy=(i//2)*416; sheet.paste(im,(xx,yy+32)); sd.text((xx+8,yy+7),x['id'],fill='black',font=font)
sheet.save(QA/'kingdom-eight-native-overview.jpg',quality=94)
for x in king:
    pack=(ROOT/x['file']).parent
    im=Image.open(ROOT/x['file']).convert('RGB'); logical=im.resize((1376,768),Image.Resampling.LANCZOS)
    overlay=logical.copy(); od=ImageDraw.Draw(overlay)
    for s in sites:
        p=poly(s['rect']); od.line(p+[p[0]],fill='#ff00ff',width=2); centre=point(s['rect'][0]+s['rect'][2]/2,s['rect'][1]+s['rect'][3]/2); od.text(centre,s['id'],fill='white',stroke_width=1,stroke_fill='black',font=font)
    for road in geom['roads']: od.line([point(*p) for p in road],fill='#00ffff',width=2)
    p=poly(bridge['rect']); od.line(p+[p[0]],fill='red',width=3)
    od.rectangle((excl[0][0],excl[0][1],excl[1][0],excl[1][1]),outline='yellow',width=2)
    overlay.save(QA/(x['id']+'-overlay.jpg'),quality=95)
    # 1:1 native details around roof reservation, P09 and actual bridge corridor.
    areas={'civic-upper':(380,30,800,270),'right-pads':(760,180,1100,430),'crossing':(1060,245,1300,390),'lower-pads':(460,430,1030,555)}
    for label,box in areas.items(): im.crop(tuple(round(z*4) for z in box)).save(QA/(x['id']+'-native-'+label+'.jpg'),quality=96)
    plate=Image.new('RGB',(1376*3,768),'white'); plate.paste(Image.open(pack/'guide.png').convert('RGB'),(0,0)); plate.paste(Image.open(pack/'base.png').convert('RGB'),(1376,0)); plate.paste(logical,(2752,0)); plate.resize((2064,384),Image.Resampling.LANCZOS).save(QA/(x['id']+'-guide-base-output.jpg'),quality=95)
stone=Image.open(ROOT/king[0]['file']).convert('RGB').resize((1376,768),Image.Resampling.LANCZOS)
hall=Image.open(ROOT/'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png').convert('RGBA'); hall=hall.resize((348,348),Image.Resampling.LANCZOS)
comp=stone.convert('RGBA'); comp.alpha_composite(hall,(402,33)); comp.convert('RGB').save(QA/'stone-hall-proposal-composite.jpg',quality=96)
save('summary.json',{'at':datetime.now(timezone.utc).isoformat(),'readDocuments':len(docs),'protectedFiles':len(snapshot['files']),'outputCount':len(outputs),'uniqueIDs':len(set(x['id'] for x in outputs)),'uniqueFiles':len(set(x['file'] for x in outputs)),'all32QueueIDsPresent':set(x['id'] for x in outputs)==set(x['id'] for x in first),'allDecodeDimensionsAndHashPass':all(x['dimensions']==[5504,3072] and x['manifestMatch'] and all(y['matches'] for y in x['journalMatches']) for x in outputs),'historyStatuses':dict(Counter(x['status'] for x in history)),'physicalOutputFiles':len(list((ROOT/'assets/high-res/interactive-4k-first32-20261003').glob('*/packs/*/output.png'))),'proposed2KCounts':dict(Counter(x['group'] for x in queue['items'] if x['imageSize']=='2K'))})
print((QA/'summary.json').read_text()); print(json.dumps(anal,indent=2)[:2000]); print(json.dumps(pacing,indent=2))
