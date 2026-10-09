import sys, json, hashlib, re, collections, datetime, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA)); from audit_common import read,sha,dump
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(n,x): dump(n,x)
cache={}
def probe(path):
    if path in cache:return cache[path]
    p=ROOT/path; d={'path':path,'exists':p.is_file()}
    if p.is_file():
        d.update(bytes=p.stat().st_size,sha256=sha(p),mtimeUTC=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
        if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp']:
            try:
                with Image.open(p) as im:
                    im.load(); a=np.asarray(im.convert('RGBA')); vis=a[:,:,3]>16; rgb=a[:,:,:3].astype(np.int16)
                    ys,xs=np.where(vis); d.update(dimensions={'width':im.width,'height':im.height},mode=im.mode,alphaFraction=float(vis.mean()),alphaBounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,magentaPixels=int((vis&(rgb[:,:,0]>180)&(rgb[:,:,2]>150)&(rgb[:,:,1]<110)).sum()))
            except Exception as e:d['decodeError']=str(e)
    cache[path]=d;return d
def refs(v):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and 'sha256' in v:yield v
        for k,x in v.items():
            if k not in ['inlineData','data']:yield from refs(x)
    elif isinstance(v,list):
        for x in v:yield from refs(x)
def checks(j):
    out=[]
    for r in refs(j):
        d=probe(r['path']); errors=[]
        if not d['exists']:errors.append('MISSING')
        else:
            for k in ['sha256','bytes','dimensions']:
                if r.get(k) is not None and r[k]!=d.get(k):errors.append(k.upper()+'_MISMATCH')
            if d.get('decodeError'):errors.append('DECODE')
        out.append({'path':r['path'],'errors':errors})
    return out
# Protect source, originals, both producers, shared controls and previous QA; independent new QA is exclusive.
roots=['src','scripts','tests','assets/production','assets/high-res','assets/runtime-code-20261007','assets/derivatives/image-residual-executor-20261007','assets/derivatives/image-vertex-repair-20261009','qa/image-vertex-repair-20261009','docs/plan/image-production']
protected={rel(p):sha(p) for root in roots for p in (ROOT/root).rglob('*') if p.is_file()}
for p in (ROOT/'docs/plan').glob('*INTERFACE*'):protected[rel(p)]=sha(p)
save('input-hashes.json',{'atUTC':stamp,'files':protected})
# Read required root documents and every local README document link. Persist exact reading inventory.
paths=set(['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md'])
for s in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')):
    p=(ROOT/'docs/plan'/s.split('#')[0]).resolve()
    if p.is_file() and p.is_relative_to(ROOT):paths.add(rel(p))
paths.update('docs/plan/'+n for n in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md'])
reading=[]
for path in sorted(paths):
    p=ROOT/path
    if not p.is_file():reading.append({'path':path,'missing':True});continue
    text=p.read_text(encoding='utf-8-sig',errors='replace')
    reading.append({'path':path,'sha256':sha(p),'bytes':p.stat().st_size,'headings':re.findall(r'^#{1,3} .+$',text,re.M),'policyExcerpts':[{'line':i,'text':line[:700]} for i,line in enumerate(text.splitlines(),1) if re.search(r'protected|safety.?reserve|eight.age|whole.*INCOMPLETE|planning.*only|verifier.*only',line,re.I)][:12]})
save('reading-inventory.json',reading)
results={}; allrows=[]
for owner,prefix in [('environment','ENVIRONMENT-ART'),('actors','ACTORS-EQUIPMENT')]:
    j=read(f'docs/plan/{prefix}-VERTEX-REPAIR-INTERFACE-2026-10-09.json'); rows=j['rows']; allrows+=rows
    actualready=[r['id'] for r in rows if r['status']=='READY']; represented=j['readySubset']; duplicates=[k for k,v in collections.Counter(r['id'] for r in rows).items() if v>1]
    refchecks=checks(j); per=[]
    for r in rows:
        out=r.get('output'); pd=probe(out['path']) if out and isinstance(out,dict) else None
        errs=[]
        a=r.get('sourceToOutput'); src=r.get('source'); roi=src.get('roi') if isinstance(src,dict) else None
        if a and roi and out and r.get('reusedFrom') is None:
            if a==[1,0,0,1,0,0] and (roi[0]!=0 or roi[1]!=0):errs.append('IDENTITY_WITH_NONZERO_SOURCE_ROI')
        contacts=r.get('groundContact') or []; contactpixels=[]
        if pd and pd.get('dimensions'):
            with Image.open(ROOT/out['path']) as im:
                alpha=im.convert('RGBA').getchannel('A')
                for xy in contacts:
                    if isinstance(xy,(list,tuple)) and len(xy)==2:
                        x,y=map(lambda v:int(round(v)),xy); contactpixels.append(alpha.getpixel((x,y)) if 0<=x<im.width and 0<=y<im.height else None)
        if r['status']=='READY' and contactpixels and any(x is None or x<=16 for x in contactpixels):errs.append('READY_CONTACT_TRANSPARENT_OR_OUTSIDE')
        per.append({'id':r['id'],'status':r['status'],'role':r.get('role'),'age':r.get('age'),'intendedUse':r.get('intendedUse'),'output':out,'contactAlpha':contactpixels,'geometryWarnings':errs,'gates':r.get('gates'),'nextAction':r.get('nextAction')})
    results[owner]={'rows':len(rows),'statuses':dict(collections.Counter(r['status'] for r in rows)),'roleCounts':dict(collections.Counter(r.get('role') for r in rows)),'duplicates':duplicates,'readySubsetCount':len(represented),'readyOmittedFromSubset':sorted(set(actualready)-set(represented)),'subsetNotReady':sorted(set(represented)-set(actualready)),'referenceChecks':len(refchecks),'referenceFailures':[x for x in refchecks if x['errors']], 'wholeDeliveryReady':j['wholeDeliveryReady'],'coverage':j.get('coverage'),'budgetSnapshot':j.get('budgetSnapshot'),'generationReceipts':j.get('generationReceipts'),'paidPendingIds':j.get('paidPendingIds'),'paidBlockedIds':j.get('paidBlockedIds'),'imageReview':j.get('imageReview'),'geometryWarningCounts':dict(collections.Counter(e for r in per for e in r['geometryWarnings']))}
    save(owner+'-per-id.json',per)
    save(owner+'-scene-review.json',j.get('scenes',[]))
save('delivery-checks.json',results)
# Coordinator receipt validation, only safe response metadata, never emit inline/base64/token data.
receipts=[]
for p in (ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts').rglob('*.json'):
    j=json.loads(p.read_text(encoding='utf-8-sig'))
    receipts.append({'file':rel(p),'keys':list(j),'metadata':{k:v for k,v in j.items() if k in ['id','canonicalId','owner','attemptId','status','requestPackSHA256','wireBodySHA256','rawResponsePath','rawResponseSHA256','reservedUSD','actualOrRetainedExposureUSD','complete','images','rejectionEvidence','usage','nextAction']},'referenceChecks':checks(j)})
save('receipts.json',receipts)
save('pixel-file-probes.json',list(cache.values()))
print(json.dumps({k:{x:v for x,v in j.items() if x not in ['readyOmittedFromSubset','coverage','budgetSnapshot','generationReceipts','imageReview']} for k,j in results.items()},indent=2)[:12500])
print('receipts',len(receipts),'protected',len(protected),'reading',len(reading),'probes',len(cache))
