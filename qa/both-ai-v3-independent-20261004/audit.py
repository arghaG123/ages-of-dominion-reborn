import sys, json, hashlib, pathlib, zipfile, math, collections
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
ROOT = pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT = ROOT / 'qa/both-ai-v3-independent-20261004'
OUT.mkdir(parents=True, exist_ok=True)
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def protected():
    paths=set()
    for folder in ['assets','src','scripts','tests','docs/plan/image-production','android/app/src','android/gradle']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file())
    planner_docs={'BOTH-AI-V3-INDEPENDENT-VERIFICATION-2026-10-04.md','CODE-AI-AFTER-V3-AUDIT-2026-10-04.txt','IMAGE-AI-AFTER-V3-AUDIT-2026-10-04.txt'}
    paths.update(p for p in (ROOT/'docs/plan').glob('*V3*') if p.is_file() and p.name not in planner_docs)
    paths.update(p for p in (ROOT/'android').glob('*') if p.is_file())
    paths.update(p for p in [ROOT/'package.json', ROOT/'index.html', ROOT/'android/app/build.gradle',ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'] if p.exists())
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(paths)}
if sys.argv[1]=='start':
    snap=protected();write('protected-start.json',snap);print('Protected start files',len(snap));sys.exit()
if sys.argv[1]=='end':
    before=read('qa/both-ai-v3-independent-20261004/protected-start.json');after=protected()
    result={'filesBefore':len(before),'filesAfter':len(after),'changed':[p for p in before if p in after and before[p]!=after[p]],'added':sorted(after.keys()-before.keys()),'deleted':sorted(before.keys()-after.keys())}
    write('preservation-result.json',result);print(json.dumps(result));sys.exit()

checks=[]
def bound(p,h,size=None,mode=None,label=''):
    p=ROOT/p; row={'path':str(p.relative_to(ROOT)).replace('\\','/'),'label':label,'exists':p.is_file(),'expectedHash':h}
    if p.is_file():
        row['actualHash']=sha(p);row['hashMatches']=row['actualHash']==h
        if p.suffix.lower() in ['.png','.webp','.jpg']:
            with Image.open(p) as im:
                im.load();row.update(dimensions=list(im.size),mode=im.mode)
                if size: row['dimensionsMatch']=list(im.size)==size
                if mode: row['modeMatches']=im.mode==mode
    checks.append(row);return row
actors=read('docs/plan/ACTORS-MOUNTS-V3-RESULTS.json')
rigs=read('assets/derivatives/rigs/v3/parts_manifest_v3.json')
parts=[];rig_checks=[]
for cls,sheet in rigs.items():
    if not isinstance(sheet,dict) or 'parts' not in sheet: continue
    parentmap={p['partName']:p for p in sheet['parts']}
    for p in sheet['parts']:
        parts.append((cls,p))
        bound(p['sourcePath'],p['sourceSHA256'],p['sourceDimensions'],label=cls+' source')
        bound(p['derivativePath'],p['derivativeSHA256'],p['derivativeDimensions'],p['derivativeMode'],cls+'/'+p['partName'])
        row={'class':cls,'part':p['partName'],'jointSourceMinusCropMatchesLocal':None,'localJointInBounds':None,'localJointAlpha':None,'parentAttachmentInParentCrop':None,'parentJointAlpha':None}
        crop=p['cropBBoxSource']; j=p.get('jointSourcePx'); loc=p.get('jointLocalPx')
        if j and loc:
            row['jointSourceMinusCropMatchesLocal']=[j[0]-crop[0],j[1]-crop[1]]==loc
            with Image.open(ROOT/p['derivativePath']) as im:
                row['localJointInBounds']=0<=loc[0]<im.width and 0<=loc[1]<im.height
                if row['localJointInBounds']:row['localJointAlpha']=im.convert('RGBA').getpixel(tuple(map(int,loc)))[3]
        par=parentmap.get(p.get('parentPart')); pj=p.get('parentJointSourcePx')
        if par and pj:
            pc=par['cropBBoxSource'];pl=[pj[0]-pc[0],pj[1]-pc[1]]
            with Image.open(ROOT/par['derivativePath']) as im:
                row['parentAttachmentInParentCrop']=0<=pl[0]<im.width and 0<=pl[1]<im.height
                if row['parentAttachmentInParentCrop']:row['parentJointAlpha']=im.convert('RGBA').getpixel(tuple(map(int,pl)))[3]
        rig_checks.append(row)
actorpaths=[]
for id,row in actors.items():
    if 'derivativePath' in row:
        actorpaths.append((id,row['derivativePath']))
        bound(row['derivativePath'],row['derivativeSHA256'],row['derivativeDimensions'],row['derivativeMode'],id)
    if 'sourcePath' in row:bound(row['sourcePath'],row['sourceSHA256'],label=id+' source')
    elif 'sourceProvenance' in row:
        path='assets/production/'+row['sourceProvenance'].split(' (')[0]
        bound(path,row['sourceSHA256'],label=id+' substitution source')
survey=read('docs/plan/KINGDOM-TERRAIN-SURVEY-V3-2026-10-04.json')
for t in survey['terrains']:bound(t['sourcePath'],t['sourceSHA256'],t['dimensions'],label=t['terrainId'])
manifest=read('docs/plan/IMAGE-DELIVERY-MANIFEST-V3-2026-10-04.json')
manifestpaths=[]
def collect(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if isinstance(x,str) and ('Directory' in k or k.endswith('Path') or k.endswith('Report') or k=='reuseResults'):
                if x.startswith(('assets/','qa/','docs/')):manifestpaths.append({'field':k,'path':x,'exists':(ROOT/x).exists()})
            collect(x)
    elif isinstance(v,list):
        for x in v:collect(x)
collect(manifest)
# Check explicitly advertised authentic substitution names independently of the detailed rows.
for p in ['assets/derivatives/substitutions/v3/troop-iron-melee-legionary-1k.png','assets/derivatives/substitutions/v3/troop-industrial-heavy-steamwalker-1k.png']:
    manifestpaths.append({'field':'summary-advertised-substitution','path':p,'exists':(ROOT/p).exists()})
write('binding-checks.json',checks);write('rig-joint-checks.json',rig_checks);write('manifest-paths.json',manifestpaths)

def sheet(name,items,cols=4,cell=(340,310),thumb=(310,232),background=(70,83,72)):
    cw,ch=cell;canvas=Image.new('RGB',(cw*cols,ch*math.ceil(len(items)/cols)),(24,28,29));d=ImageDraw.Draw(canvas)
    for i,(label,path) in enumerate(items):
        x=(i%cols)*cw;y=(i//cols)*ch
        with Image.open(ROOT/path) as im:
            im=im.convert('RGBA');bb=im.getbbox()
            if bb:im=im.crop(bb)
            im.thumbnail(thumb)
            canvas.paste(background,(x+8,y+42,x+cw-8,y+ch-28))
            canvas.paste(im,(x+(cw-im.width)//2,y+44+(thumb[1]-im.height)//2),im)
        d.text((x+8,y+6),label[:45],fill='white')
        d.text((x+8,y+ch-20),str(path).split('/')[-1][:43],fill='#adbabb')
    canvas.save(OUT/name)
sheet('actors-v3-overview.png',actorpaths,cols=5)
for cls,sheetrow in rigs.items():
    if isinstance(sheetrow,dict) and 'parts' in sheetrow:
        sheet('rig-'+cls+'-v3-overview.png',[(p['partName'],p['derivativePath']) for p in sheetrow['parts']],cols=4,cell=(310,285),thumb=(278,205))
# Consumer-scale evidence on white/black/neutral green for prioritized full-canvas sources.
priorities=['troop-stone-melee','troop-stone-ranged','hero-mount-horse','hero-mount-motor-transport','hero-mount-future-transport','troop-bronze-melee','troop-industrial-ranged']
samples=Image.new('RGB',(1200,220*len(priorities)),(30,32,35));d=ImageDraw.Draw(samples)
for i,id in enumerate(priorities):
    p=actors[id]['derivativePath'];im=Image.open(ROOT/p).convert('RGBA');im=im.crop(im.getbbox())
    d.text((6,220*i+4),id,fill='white')
    for k,bg in enumerate([(250,250,250),(0,0,0),(83,101,86)]):
        x=k*400;y=i*220+25;samples.paste(bg,(x,y,x+395,y+215))
        for h,offset in [(180,30),(64,240)]:
            thumb=im.copy();thumb.thumbnail((210,h));samples.paste(thumb,(x+offset,y+205-thumb.height),thumb)
samples.save(OUT/'prioritized-mattes-v3.png')

# Exact package closure: APK, generated native assets, dist, and root origins.
apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
closure={'apkSHA256':sha(apk),'apkBytes':apk.stat().st_size,'mismatches':[],'missing':[],'extra':[]}
with zipfile.ZipFile(apk) as z:
    files={n[len('assets/www/'):]:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('assets/www/') and not n.endswith('/')}
closure['packagedFiles']=len(files)
for relative,h in files.items():
    for prefix in ['', 'dist/', 'android/app/src/main/assets/www/']:
        p=ROOT/(prefix+relative)
        if not p.exists():closure['missing'].append(prefix+relative)
        elif sha(p)!=h:closure['mismatches'].append(prefix+relative)
for prefix in ['dist','android/app/src/main/assets/www']:
    names={str(p.relative_to(ROOT/prefix)).replace('\\','/') for p in (ROOT/prefix).rglob('*') if p.is_file()}
    closure['extra'].extend(prefix+'/'+p for p in sorted(names-set(files)))
write('package-closure.json',closure)
# All saved browser captures, including dimensions and hash records.
evidence=read('qa/visual-integration-20261004/evidence.json');shots=[]
def shotscollect(v):
    if isinstance(v,dict):
        if 'file' in v and 'sha256' in v and str(v['file']).endswith('.png'):
            shots.append(bound('qa/visual-integration-20261004/'+v['file'],v['sha256'],[v['width'],v['height']],label='saved browser capture'))
        for x in v.values():shotscollect(x)
    elif isinstance(v,list):
        for x in v:shotscollect(x)
shotscollect(evidence);write('saved-capture-bindings.json',shots)
summary={'actorRowsWithDerivatives':len(actorpaths),'rigParts':len(parts),'rigClasses':len(set(c for c,p in parts)), 'terrainRows':len(survey['terrains']),'checks':len(checks),'bindingFailures':[c for c in checks if not c['exists'] or c.get('hashMatches') is False or c.get('dimensionsMatch') is False or c.get('modeMatches') is False], 'rigJointOutOfBounds':[r for r in rig_checks if r['localJointInBounds'] is False or r['parentAttachmentInParentCrop'] is False], 'rigTransparentJoints':[r for r in rig_checks if r['localJointAlpha']==0 or r['parentJointAlpha']==0], 'rigOverlapValues':dict(collections.Counter(str(p.get('demonstratedPaintedOverlapPx')) for c,p in parts)), 'rigUncertaintyValues':dict(collections.Counter(str(p.get('jointUncertaintyPx')) for c,p in parts)),'missingAdvertisedPaths':[p for p in manifestpaths if not p['exists']], 'packageClosure':closure,'savedCaptureCount':len(shots)}
write('summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k not in ['rigTransparentJoints','bindingFailures','rigJointOutOfBounds']},indent=2))
print('FAIL COUNTS',len(summary['bindingFailures']),len(summary['rigTransparentJoints']),len(summary['rigJointOutOfBounds']))
