"""Read-only local handoff inspection; writes only its own new QA directory.
No tests, builds, gameplay, network, provider, Git mutation, or archive mutation.
"""
from pathlib import Path
import csv, hashlib, json, re, subprocess, zipfile
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(name, obj): (OUT/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf-8',errors='replace').strip()
def record(p): return {'path':rel(p),'bytes':p.stat().st_size,'sha256':sha(p)}

required=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
plan_names=['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','references/visual-targets/index.json','references/visual-targets/README.md','FULL-IMPLEMENTATION-SPEC.md','IMPLEMENTATION-CONTRACT.json','DATA-ADOPTION-LEDGER.json','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md']
reading=[]
for name in required+['docs/plan/'+n for n in plan_names]:
    p=ROOT/name
    if not p.exists(): reading.append({'path':name,'missing':True}); continue
    s=p.read_text(encoding='utf-8-sig'); row=record(p); row['lines']=len(s.splitlines())
    if p.suffix=='.json':
        data=json.loads(s); row['shape']=list(data) if isinstance(data,dict) else {'rows':len(data),'firstRowKeys':list(data[0]) if data and isinstance(data[0],dict) else []}
    else: row['headings']=[l for l in s.splitlines() if l.startswith('#')]
    reading.append(row)
write('documents-read.json',reading)

paths=[]
for directory in ['assets','src','scripts','tests','qa','docs/plan/image-production','docs/asset-provenance','android/app/src/main/java','android/app/src/main/res']:
    for p in (ROOT/directory).rglob('*'):
        if p.is_file() and OUT not in p.parents and '__pycache__' not in p.parts: paths.append(p)
for p in [ROOT/'index.html',ROOT/'package.json',ROOT/'package-lock.json',ROOT/'android/app/src/main/AndroidManifest.xml']:
    if p.exists(): paths.append(p)
protected=[record(p) for p in sorted(set(paths))]
write('protected-before.json',protected)

status=git('status','--porcelain=v1','-uall').splitlines()
index=set(git('ls-files').splitlines()); head=set(git('ls-tree','-r','--name-only','HEAD').splitlines())
write('git-local.json',{'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'remotes':git('remote','-v').splitlines(),'cachedOriginMain':git('rev-parse','refs/remotes/origin/main'),'liveRemote':'UNQUERIED','clean':not status,'statusRows':len(status),'stagedRows':sum(l[0] not in ' ?' for l in status),'unstagedRows':sum(l[1] not in ' ?' for l in status),'untrackedRows':sum(l.startswith('??') for l in status),'indexPaths':len(index),'headPaths':len(head),'indexAssets':sum(x.startswith('assets/') for x in index),'headAssets':sum(x.startswith('assets/') for x in head),'status':status})

transfer={}
for name in ['TRANSFER-INCLUDE-2026-10-04.csv','GIT-ALLOWLIST-2026-10-04.csv','NON-GIT-TRANSFER-2026-10-04.csv']:
    p=ROOT/'docs/migration'/name; rows=list(csv.DictReader(p.open(encoding='utf-8-sig',newline=''))); result=[]
    for row in rows:
        f=ROOT/row['Path']; state='MISSING' if not f.exists() else 'PASS' if sha(f)==row['SHA256'].lower() and f.stat().st_size==int(row['Bytes']) else 'CHANGED'
        if state!='PASS': result.append({'path':row['Path'],'status':state,'current':record(f) if f.exists() else None})
    transfer[name]={'manifest':record(p),'rows':len(rows),'bytes':sum(int(r['Bytes']) for r in rows),'mismatches':result}
write('transfer-manifest-checks.json',transfer)

interface=read('docs/plan/IMAGE-DELIVERY-INTERFACE-V6-2026-10-04.json')
img=[]
for row in read('qa/image-local-solution-20261004/v6-hashes.json'):
    p=ROOT/row['path']; out=record(p); out['recordedSHA256']=row['sha256']; out['hashPass']=out['sha256']==row['sha256']
    with Image.open(p) as im:
        im.load(); out.update({'size':list(im.size),'mode':im.mode,'visibleAlphaBounds':list(im.getchannel('A').getbbox() or []) if im.mode=='RGBA' else None})
    img.append(out)
write('image-v6-bindings.json',{'interface':record(ROOT/'docs/plan/IMAGE-DELIVERY-INTERFACE-V6-2026-10-04.json'),'wholeReady':interface['codeAIHandoffReady'],'bindings':img})

report=read('qa/code-playable-20261004/report.json'); captures=[]
for step in report['viewport']+report['steps']:
    ref=step['image']; p=ROOT/'qa/code-playable-20261004'/ref['file']; row=record(p); row['hashPass']=row['sha256']==ref['sha256']; row['bytesPass']=row['bytes']==ref['bytes']; captures.append(row)
write('latest-code-evidence.json',{'report':record(ROOT/'qa/code-playable-20261004/report.json'),'sourceScript':record(ROOT/'scripts/capture-playable-20261004.mjs'),'captureBindings':captures,'reportFinishedUTC':report['finished'],'defense':report['defense'],'inventory':report['inventory'],'saved':report['saved'],'reportedErrors':report['errors'],'reportedFailures':report['failures'],'independentReplay':'NOT_RUN_PLANNER_ROLE'})

apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'; pkg=record(apk); closure=[]
with zipfile.ZipFile(apk) as z:
    pkg['zipBadEntry']=z.testzip()
    for name in z.namelist():
        if name.startswith('assets/www/') and not name.endswith('/'):
            path=name[len('assets/www/'):]; digest=hashlib.sha256(z.read(name)).hexdigest()
            row={'path':path,'packageSHA256':digest}
            for label,base in [('root',ROOT),('dist',ROOT/'dist'),('www',ROOT/'android/app/src/main/assets/www')]:
                p=base/path; row[label+'Matches']=p.exists() and sha(p)==digest
            closure.append(row)
    pkg['packagedManifestSHA256']=hashlib.sha256(z.read('AndroidManifest.xml')).hexdigest()
pkg['closure']=closure
pkg['nativeRuntime']='UNVERIFIED_DEVICE_STOPPED'
write('apk-current.json',pkg)

catalogs={}
for name in ['src/data/plate-catalog.json','src/data/anatomy-binding-v1.json','src/data/static-mounts-v1.json','src/data/portrait-cards.json','qa/image-local-solution-20261004/run-report.json','docs/plan/image-production/production-budget-ledger.json','docs/asset-provenance/raw-response-archive-index.json']:
    p=ROOT/name
    if p.exists(): catalogs[name]={'file':record(p),'data':read(name)}
write('consumer-and-archive-records.json',catalogs)

write('summary.json',{'inspectedUTC':datetime.now(timezone.utc).isoformat(),'role':'PLANNER_VERIFIER_LOCAL_READ_ONLY','protectedFiles':len(protected),'imageV6Files':len(img),'imageV6HashesPass':all(r['hashPass'] for r in img),'captureFiles':len(captures),'captureHashesPass':all(r['hashPass'] and r['bytesPass'] for r in captures),'apk':{k:v for k,v in pkg.items() if k!='closure'},'apkWebFiles':len(closure),'apkCurrentRootMismatches':[r['path'] for r in closure if not r['rootMatches']],'apkDistMismatches':[r['path'] for r in closure if not r['distMatches']],'apkWWWMismatches':[r['path'] for r in closure if not r['wwwMatches']],'transferMismatches':{k:v['mismatches'] for k,v in transfer.items()},'tests':'NOT_RUN','builds':'NOT_RUN','provider':'NOT_QUERIED','device':'STOPPED','gitMutation':False,'storageMutation':False})
print((OUT/'summary.json').read_text())
