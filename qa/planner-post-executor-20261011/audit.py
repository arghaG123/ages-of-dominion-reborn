"""Independent read-only executor audit; writes only small QA and review rasters."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,zipfile
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
cache={}
def load(name): return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def sha(p):
    p=Path(p)
    if p not in cache:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
        cache[p]=h.hexdigest()
    return cache[p]
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

save('protected-before.json',{p.relative_to(ROOT).as_posix():sha(p) for folder in ['src','scripts','tests','assets/derivatives/image-complete-20261011'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts})
changed=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines()
save('worktree-before.json',{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'topLevelPaths':len(changed),'paths':changed,'trackedChangedFiles':subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()})
docs=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
for link in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')):
    p=(ROOT/'docs/plan'/link.split('#')[0]).resolve()
    if p.is_relative_to(ROOT) and p.is_file() and p.suffix in ['.md','.txt','.json']: docs.append(p.relative_to(ROOT).as_posix())
save('document-inventory.json',[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':sha(ROOT/p),'headings':re.findall(r'^#{1,3} (.+)',(ROOT/p).read_text(encoding='utf-8-sig'),re.M)} for p in sorted(set(docs))])

face=load('docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json')
refs=[]
def refs_walk(v):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and ('sha256' in v or 'bytes' in v):
            p=ROOT/v['path']; errors=[]
            if not p.is_file(): errors.append('MISSING')
            else:
                if v.get('sha256') and sha(p)!=v['sha256']: errors.append('HASH_MISMATCH')
                if v.get('bytes') is not None and p.stat().st_size!=v['bytes']: errors.append('SIZE_MISMATCH')
                if isinstance(v.get('dimensions'),dict):
                    with Image.open(p) as im:
                        if im.size!=(v['dimensions']['width'],v['dimensions']['height']): errors.append('DIMENSION_MISMATCH')
            refs.append({'path':v['path'],'errors':errors})
        for x in v.values(): refs_walk(x)
    elif isinstance(v,list):
        for x in v: refs_walk(x)
refs_walk(face)
ready=set(face.get('readySubset',[])); ready_rows={r['id'] for r in face['rows'] if r.get('status')=='READY'}
body_rows=[{'id':r['id'],'status':r.get('status'),'maxDisplayCssPx':r.get('maxDisplayCssPx'),'consumer':r.get('consumer'),'gates':r.get('gates'),'sources':r.get('sources')} for r in face['rows'] if r['id'].endswith('standing-body')]
save('interface-check.json',{'rows':len(face['rows']),'referenceCount':len(refs),'referenceIssues':[r for r in refs if r['errors']],'statusCounts':dict(Counter(r.get('status') for r in face['rows'])),'sceneCount':len(face['scenes']),'sceneGates':[{'id':r.get('id'),'gates':r.get('gates')} for r in face['scenes']],'readySubsetCount':len(ready),'readySubsetNotREADY':sorted(ready-ready_rows),'READYNotSubset':sorted(ready_rows-ready),'bodyRows':body_rows,'wholeDeliveryReady':face.get('wholeDeliveryReady'),'imageWorkComplete':face.get('imageWorkComplete')})

bodies=load('src/data/hero-bodies-20261011.json')['bodies']; body_results=[]
for key,r in bodies.items():
    p=ROOT/r['file']; src=ROOT/r['source']; native=ROOT/r['native']; im=Image.open(p).convert('RGBA'); a=np.array(im)[:,:,3];x,y,w,h=r['cropROI']
    row={'id':key,'file':r['file'],'outputHashPass':sha(p)==r['sha256'],'sourceHashPass':sha(src)==r['sourceSHA256'],'nativeHashPass':sha(native)==r['nativeSHA256'],'size':list(im.size),'cropFormatActually':'XYWH not canonical XYXY','sourceToOutput':r['sourceToOutput'],'maxVisibleCssPx':r['maxVisibleCssPx'],'rowCap':next((t.get('maxDisplayCssPx') for t in face['rows'] if t['id']==r['id']),None),'contactFromBottomBand':r['groundContact'],'visiblePixels':int((a>16).sum())}
    body_results.append(row)
save('body-contract-check.json',body_results)

plates=load('qa/image-complete-20261011/plate-despill.json'); plate_checks=[]
for r in plates['rows']:
    if r['action']=='KEEP_ORIGINAL': continue
    old=np.array(Image.open(ROOT/r['source']).convert('RGBA')); new=np.array(Image.open(ROOT/r['file']).convert('RGBA'))
    if r.get('roi'): x0,y0=r['offset']; old=old[y0:y0+new.shape[0],x0:x0+new.shape[1]]
    if old.shape!=new.shape: continue
    opaque=old[:,:,3]>200; loss=opaque&(new[:,:,3]<32)
    ys,xs=np.where(opaque)
    inner=np.zeros_like(opaque)
    if len(xs):
        xa,xb=int(np.quantile(xs,.2)),int(np.quantile(xs,.8)); ya,yb=int(np.quantile(ys,.1)),int(np.quantile(ys,.7));inner[ya:yb,xa:xb]=True
    plate_checks.append({'group':r['group'],'id':r['id'],'file':r['file'],'source':r['source'],'hashPass':sha(ROOT/r['file'])==r['sha256'],'opaqueBefore':int(opaque.sum()),'opaqueToTransparent':int(loss.sum()),'centralOpaqueToTransparent':int((loss&inner).sum()),'alphaReducedPixels':int((new[:,:,3]<old[:,:,3]).sum()),'residualHeuristic':r['after']['fraction'],'semanticMaskEvidence':False,'keyRGB':r['keyRGB']})
save('despill-check.json',{'producerSummary':plates['summary'],'checked':len(plate_checks),'rows':plate_checks,'note':'Alpha changes are measurement only. No foreground/background semantics inferred from these counts.'})

# Compact before/after contact sheet, reviewed as evidence, not production art.
chosen=sorted(plate_checks,key=lambda r:r['centralOpaqueToTransparent'],reverse=True)[:6]
sheet=Image.new('RGB',(800,6*220),(230,230,230)); draw=ImageDraw.Draw(sheet)
for i,r in enumerate(chosen):
    draw.text((8,i*220+5),r['group']+' '+r['id']+' | before / after',(0,0,0))
    for col,path in enumerate([r['source'],r['file']]):
        im=Image.open(ROOT/path).convert('RGBA');im.thumbnail((380,185)); bg=Image.new('RGBA',im.size,(38,49,58,255));bg.alpha_composite(im);sheet.paste(bg.convert('RGB'),(col*400+10,i*220+28))
sheet.save(OUT/'despill-review.jpg',quality=90)

transfer=load('docs/migration/device-handoff-20261009/transfer-manifest.json'); groups={}; issues=[]
for r in transfer['files']:
    if not r['path'].startswith('assets/'): continue
    p=ROOT/r['path']; status='MISSING' if not p.is_file() else 'PASS' if p.stat().st_size==r['bytes'] and sha(p)==r['sha256'] else 'MISMATCH'
    groups[status]=groups.get(status,0)+1
    if status!='PASS': issues.append(r['path'])
save('original-asset-preservation.json',{'checks':groups,'issues':issues})

pkg=load('qa/code-image-complete-20261011/package-check.json');apk=ROOT/pkg['apk'];names=set();problems=[]
with zipfile.ZipFile(apk) as z:
    names={n[11:] for n in z.namelist() if n.startswith('assets/www/') and not n.endswith('/')}
    for n in sorted(names):
        p=ROOT/n
        for stage in ['dist','android/app/src/main/assets/www']:
            q=ROOT/stage/n
            if not p.is_file() or not q.is_file() or sha(p)!=sha(q): problems.append({'file':n,'stage':stage})
        if not p.is_file() or hashlib.sha256(z.read('assets/www/'+n)).hexdigest()!=sha(p): problems.append({'file':n,'stage':'APK'})
    crc=z.testzip()
    manifest=z.read('AndroidManifest.xml')
save('package-check.json',{'apk':pkg['apk'],'bytes':apk.stat().st_size,'sha256':sha(apk),'reportedSHA256Matches':sha(apk)==pkg['apkSHA256'],'webEntries':len(names),'byteDifferences':problems,'crcBadEntry':crc,'oldReferencedReleasePresent':(ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk').is_file(),'producerNativeManifestClaim':{'applicationId':pkg['manifestApplicationId'],'permissions':pkg['manifestPermissions']},'nativeManifestProof':'producer string-pool check reviewed; authoritative aapt/merged-manifest check remains separately scoped','bodySourceCopiesPackaged':[r['source'] for r in bodies.values() if r['source'] in names],'bodyNativesPackaged':[r['native'] for r in bodies.values() if r['native'] in names]})
save('summary.json',{'interfaceRefs':len(refs),'referenceIssues':sum(bool(r['errors']) for r in refs),'readyMismatch':len(ready-ready_rows),'plateOutputsChecked':len(plate_checks),'bodyHashesPASS':all(r['outputHashPass'] and r['sourceHashPass'] and r['nativeHashPass'] for r in body_results),'originalAssets':groups,'packageBytes':apk.stat().st_size,'packageParityIssues':len(problems),'crc':crc})
print(json.dumps(load('qa/planner-post-executor-20261011/summary.json'),indent=2))
