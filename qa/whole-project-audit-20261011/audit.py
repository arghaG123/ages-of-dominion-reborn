"""Read-only source/art/package audit. Writes diagnostics only; no backups/builds."""
from pathlib import Path
from collections import Counter
import hashlib, json, re, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
cache = {}

def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))

def sha(path):
    p = Path(path)
    if p not in cache:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
        cache[p] = h.hexdigest()
    return cache[p]

def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

protected = {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for folder in ['src','scripts','tests'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
save('protected-source-before.json',protected)

# Read canonical documents and all local files linked from the plan index.
documents = set(['START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/FULL-IMPLEMENTATION-SPEC.md','docs/plan/MASTER-PLAN.md','docs/plan/REQUIREMENTS-TRACEABILITY.md','docs/plan/NEXT-DEVICE-COMPLETE-CONTINUATION-PROMPT-2026-10-09.txt'])
index=ROOT/'docs/plan/README.md'
for link in re.findall(r'\]\(([^)]+)\)',index.read_text(encoding='utf-8-sig')):
    link=link.split('#')[0]
    if link and not re.match(r'\w+://',link):
        p=(index.parent/link).resolve()
        if p.is_relative_to(ROOT) and p.suffix in ['.md','.json','.txt'] and p.is_file(): documents.add(str(p.relative_to(ROOT)).replace('\\','/'))
reads=[]
for name in sorted(documents):
    p=ROOT/name
    text=p.read_text(encoding='utf-8-sig')
    reads.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p),'headings':re.findall(r'^#{1,3} (.+)',text,re.M)})
save('plan-read-inventory.json',reads)

transfer=load('docs/migration/device-handoff-20261009/transfer-manifest.json')
results=[]
for row in transfer['files']:
    p=ROOT/row['path']
    status='MISSING' if not p.is_file() else 'PASS' if p.stat().st_size==row['bytes'] and sha(p)==row['sha256'] else 'MISMATCH'
    results.append({'path':row['path'],'archive':row['archive'],'status':status})
save('transfer-check.json',{'files':len(results),'groups':{group:dict(Counter(r['status'] for r in results if r['archive']==group)) for group in sorted(set(r['archive'] for r in results))},'missingExamples':[r for r in results if r['status']!='PASS'][:12],'payloads':[{'path':x['sourcePath'],'present':(ROOT/x['sourcePath']).is_file()} for x in transfer['payloads']]})

interface=load('docs/plan/IMAGE-RECONCILE-INTERFACE-2026-10-11.json')
refs=[]
def check_refs(v):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and ('sha256' in v or 'bytes' in v):
            p=ROOT/v['path']
            status='MISSING' if not p.is_file() else 'PASS'
            if status=='PASS' and v.get('sha256') and sha(p)!=v['sha256']: status='HASH_MISMATCH'
            if status=='PASS' and v.get('bytes') is not None and p.stat().st_size!=v['bytes']: status='SIZE_MISMATCH'
            refs.append({'path':v['path'],'status':status})
        for x in v.values(): check_refs(x)
    elif isinstance(v,list):
        for x in v: check_refs(x)
check_refs(interface)
save('image-interface-check.json',{'version':interface['version'],'referenceChecks':dict(Counter(r['status'] for r in refs)),'issues':[r for r in refs if r['status']!='PASS'],'rows':dict(Counter(r.get('status','UNKNOWN') for r in interface['rows'])),'sceneCount':len(interface['scenes']),'sceneGates':[{'id':r.get('id'),'gates':r.get('gates'),'status':r.get('status')} for r in interface['scenes']],'readySubset':interface.get('readySubset'),'wholeDeliveryReady':interface.get('wholeDeliveryReady')})

consumer=load('src/data/consumer-catalog-20261007.json')
consumer_rows=consumer.get('assets',[])
save('consumer-status.json',{'rows':len(consumer_rows),'runtimeGates':dict(Counter(r.get('gates',{}).get('runtime','UNKNOWN') for r in consumer_rows)),'currentReconcileBindingFiles':[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'src').rglob('*') if p.is_file() and p.suffix in ['.js','.json','.css'] and ('image-reconcile-20261011' in p.read_text(encoding='utf-8-sig') or 'image-unified-reserve-20261009' in p.read_text(encoding='utf-8-sig'))]})

# Reproduce the declared asset closure without writing a dist/build copy.
files=set()
def visit(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if isinstance(x,str) and (k in ['file','terrain','uiFile','sourceFile','displayFile'] or k.endswith('File')): files.add(x)
            else: visit(x)
    elif isinstance(v,list):
        for x in v: visit(x)
for name in ['reviewed-source-selection','stone-scene','actor-atlas','plate-catalog','age-buildings','portrait-cards','plate-overrides-20261007','gear-icons-20261007']:
    visit(load('src/data/'+name+'.json'))
for r in consumer_rows:
    if r.get('gates',{}).get('runtime')=='PASS' and isinstance(r.get('outputPath'),str): files.add(r['outputPath'])
mode=load('src/data/mode-scenes.json')
for name in ['adventure','tactical','defense']: files.update(mode.get(name,[]))
expected=['index.html']+[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'src').rglob('*') if p.is_file()]+sorted(files)
missing=[x for x in expected if not (ROOT/x).is_file()]
network=[]
for name in ['index.html']+[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'src').rglob('*') if p.is_file() and p.suffix in ['.html','.js','.css','.json','.mjs']]:
    for url in re.findall(r'https?://[^\s"\x27`)<>]+',(ROOT/name).read_text(encoding='utf-8-sig')):
        if url!='http://www.w3.org/2000/svg': network.append({'path':name,'url':url})
apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
package={'expectedFiles':len(expected),'assetFiles':len(files),'missingCurrentFiles':missing,'networkReferences':network,'apkPresent':apk.is_file()}
if apk.is_file():
    package.update({'apkBytes':apk.stat().st_size,'apkSHA256':sha(apk)})
    with zipfile.ZipFile(apk) as z:
        names=set(z.namelist()); absent=[]; different=[]
        for name in expected:
            entry='assets/www/'+name
            if entry not in names: absent.append(name)
            elif (ROOT/name).is_file() and hashlib.sha256(z.read(entry)).hexdigest()!=sha(ROOT/name): different.append(name)
        package.update({'apkMissingCurrentFiles':absent,'apkDifferentCurrentFiles':different,'apkCrcBadEntry':z.testzip()})
save('package-check.json',package)

guides=[]
for suffix,want in [('v4','609d3195018ccf448f339f79e45fe90b9e5adfb2859674e40383144d2106f848'),('v5','673492a6a1c6780eb77d9b0b24f7eefe30a98dc119c7fbee9e3edef088b8c1ff')]:
    rel=f'qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-{suffix}-guide.png'
    p=ROOT/rel
    guides.append({'path':rel,'present':p.is_file(),'sha256Matches':p.is_file() and sha(p)==want,'tracked':bool(subprocess.check_output(['git','ls-files','--',rel],cwd=ROOT))})
save('guide-check.json',guides)
print(json.dumps({'planDocumentsRead':len(reads),'transferGroups':load('qa/whole-project-audit-20261011/transfer-check.json')['groups'],'imageReferences':dict(Counter(r['status'] for r in refs)),'runtimeGates':dict(Counter(r.get('gates',{}).get('runtime','UNKNOWN') for r in consumer_rows)),'expectedPackageFiles':len(expected),'apkMissing':len(package.get('apkMissingCurrentFiles',[])),'apkDifferent':len(package.get('apkDifferentCurrentFiles',[])),'networkReferences':len(network),'guides':guides},indent=2))
