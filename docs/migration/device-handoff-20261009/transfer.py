"""Python 3.12+; local byte-verified device transfer. No network or credentials.
Prepare runs only on the source computer. Restore/verify work on any checkout.
Never overwrites unlike files. Copy both payload ZIPs manually to the new device.
"""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,subprocess,zipfile,re,os
ROOT=Path(__file__).resolve().parents[3]
META=Path(__file__).resolve().parent
MANIFEST=META/'transfer-manifest.json'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def streamhash(f):
    h=hashlib.sha256()
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def target(n):
    p=PurePosixPath(n)
    if p.is_absolute() or '..' in p.parts or ':' in n or '\\' in n:raise ValueError('Unsafe archive path')
    dest=ROOT/n
    for part in [dest,*dest.parents]:
        if part.exists() and (part.is_symlink() or getattr(part.stat(),'st_file_attributes',0)&1024):raise ValueError('Reparse point')
    return dest
def forbidden(n):
    return any(x in n.lower().split('/') for x in ['chrome-profile','chromium-profile','playwright-profile','.git','.ssh','.gcloud','.aws','node_modules']) or bool(re.search(r'(^|/)(\.env($|\.)|credentials\.json|application_default_credentials\.json|service[-_]account[^/]*\.json)|\.(jks|keystore|p12|pfx)$',n,re.I))
def scan_json(data,n):
    patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'ya29\.[A-Za-z0-9_-]{20,}',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'AIza[0-9A-Za-z_-]{35}']
    def walk(v,key='',opaque=False):
        if isinstance(v,dict):
            image_inline=str(v.get('mimeType',v.get('mime_type',''))).startswith('image/')
            for k,item in v.items():walk(item,k,image_inline and k=='data')
        elif isinstance(v,list):
            for item in v:walk(item,key)
        elif isinstance(v,str):
            # Provider signatures and inline image base64 are opaque provenance, not auth credentials.
            if key in ['thoughtSignature','thought_signature'] or opaque:return
            if any(re.search(pattern,v) for pattern in patterns):raise ValueError('Credential-pattern match; details suppressed: '+n)
    if n.endswith('.jsonl'):
        for line in data.decode('utf-8-sig').splitlines():
            if line.strip():walk(json.loads(line))
    else:walk(json.loads(data))
def prepare():
    folder=ROOT/'output/device-transfer-20261009';folder.mkdir(parents=True,exist_ok=True)
    rows=[];base=ROOT/'assets.zip'
    with zipfile.ZipFile(base) as z:
        actual={p.relative_to(ROOT).as_posix():p for p in (ROOT/'assets').rglob('*') if p.is_file()}
        if {i.filename for i in z.infolist() if not i.is_dir()}!=set(actual):raise ValueError('Existing assets.zip does not cover the exact current asset tree')
        for i,n in enumerate(sorted(actual)):
            if forbidden(n):raise ValueError('Excluded sensitive path in assets')
            h=digest(actual[n])
            with z.open(n) as f:zh=streamhash(f)
            if h!=zh:raise ValueError('Assets archive differs: '+n)
            rows.append({'path':n,'sha256':h,'bytes':actual[n].stat().st_size,'archive':'assets.zip'})
            if i%500==0:print('Verified assets',i,flush=True)
    tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
    selected=[]
    for directory in ['qa','design-preview']:
        for p in (ROOT/directory).rglob('*'):
            if not p.is_file():continue
            n=p.relative_to(ROOT).as_posix()
            if n in tracked or forbidden(n) or '/__pycache__/' in n or n.startswith('qa/planner-device-handoff-20261009/static-package/'):continue
            # All local QA pictures and provider wire lineage; versionable scripts/reports are committed separately.
            if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.gif','.mp4','.avif','.apk','.wav','.mp3'] or p.name in ['request_body.json','response.json','predictions.jsonl']:selected.append(p)
    supplement=folder/'qa-and-lineage.zip'
    if supplement.exists():raise ValueError('Transfer ZIP already exists; use a fresh namespace, never overwrite')
    for p in selected:
        if p.suffix in ['.json','.jsonl']:scan_json(p.read_bytes(),p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(supplement,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for i,p in enumerate(sorted(selected)):
            n=p.relative_to(ROOT).as_posix()
            if p.suffix in ['.json','.jsonl']:
                data=p.read_bytes()
                scan_json(data,n)
            h=digest(p);z.write(p,n);rows.append({'path':n,'sha256':h,'bytes':p.stat().st_size,'archive':'qa-and-lineage.zip'})
            if i%500==0:print('Packaged QA',i,flush=True)
    payloads=[]
    for p in [base,supplement]:
        subset=[r for r in rows if r['archive']==p.name]
        with zipfile.ZipFile(p) as z:
            for row in subset:
                with z.open(row['path']) as f:
                    if streamhash(f)!=row['sha256']:raise ValueError('Archive readback failed: '+row['path'])
        payloads.append({'name':p.name,'sourcePath':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size,'verifiedEntries':len(subset)})
    archived=json.loads((ROOT/'docs/asset-provenance/raw-response-archive-index.json').read_text())
    result={'schema':1,'baseCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'payloads':payloads,'files':rows,'status':'LOCAL_PAYLOAD_READBACK_PASS','newDeviceRestore':'UNVERIFIED','remoteAssetUpload':'NOT_PERFORMED','missingHistoricalInputs':{'rawArchiveRecords':len(archived['records']),'bytes':sum(r['bytes'] for r in archived['records']),'externalArchivePresent':Path(archived['externalArchive']).exists(),'independentBackupPresent':Path(archived['independentBackupRoot']).exists(),'restorationIndex':'docs/asset-provenance/raw-response-archive-index.json'},'excluded':['credentials/signing material','browser profiles/user saves','build copies and caches','.git history (clone from GitHub)']}
    MANIFEST.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'payloads':payloads,'files':len(rows),'missing':result['missingHistoricalInputs']},indent=2),flush=True)
def restore(folder,verify_only):
    x=json.loads(MANIFEST.read_text());errors=[];checked=0
    for spec in x['payloads']:
        p=folder/spec['name']
        if not p.is_file() or p.stat().st_size!=spec['bytes'] or digest(p)!=spec['sha256']:raise ValueError('Missing or damaged payload '+spec['name'])
        with zipfile.ZipFile(p) as z:
            for row in [r for r in x['files'] if r['archive']==spec['name']]:
                n=row['path'];dest=target(n)
                if forbidden(n):raise ValueError('Sensitive destination prohibited')
                if dest.exists():
                    if dest.stat().st_size!=row['bytes'] or digest(dest)!=row['sha256']:errors.append({'path':n,'reason':'UNLIKE_DESTINATION'});continue
                elif verify_only:errors.append({'path':n,'reason':'MISSING'});continue
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True);temp=dest.with_name(dest.name+'.handoff-partial')
                    with z.open(n) as src,temp.open('xb') as dst:
                        for b in iter(lambda:src.read(4*1024*1024),b''):dst.write(b)
                    if digest(temp)!=row['sha256']:raise ValueError('Extracted hash failed '+n)
                    os.rename(temp,dest)
                checked+=1
    report={'checked':checked,'errors':errors,'operation':'verify' if verify_only else 'restore'}
    print(json.dumps(report,indent=2))
    if errors:raise SystemExit(1)
def late():
    x=json.loads(MANIFEST.read_text());known={r['path'] for r in x['files']}
    files=[p for p in (ROOT/'qa/planner-device-handoff-20261009').rglob('*') if p.is_file() and p.suffix in ['.png','.jpg'] and p.relative_to(ROOT).as_posix() not in known and 'static-package' not in p.parts]
    if not files:print('No late captures');return
    p=ROOT/'output/device-transfer-20261009/final-audit-captures.zip'
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for f in files:z.write(f,f.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(p) as z:
        for f in files:
            n=f.relative_to(ROOT).as_posix();h=digest(f)
            with z.open(n) as stream:
                if streamhash(stream)!=h:raise ValueError('Late capture readback failed')
            x['files'].append({'path':n,'sha256':h,'bytes':f.stat().st_size,'archive':p.name})
    x['payloads'].append({'name':p.name,'sourcePath':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size,'verifiedEntries':len(files)})
    MANIFEST.write_text(json.dumps(x,indent=2)+'\n');print('Late captures',len(files))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('operation',choices=['prepare','prepare-late','restore','verify']);a.add_argument('--payload-dir',type=Path);args=a.parse_args()
    if args.operation=='prepare':prepare()
    elif args.operation=='prepare-late':late()
    else:
        if args.payload_dir is None:a.error('--payload-dir is required')
        restore(args.payload_dir,args.operation=='verify')
