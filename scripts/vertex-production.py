"""Explicit Vertex batch operations; no inference at prepare/status/collect.
Only submit performs a paid request. Never retries a POST of unknown outcome.
"""
import argparse, base64, hashlib, io, json, os, subprocess, sys, urllib.parse, urllib.request, urllib.error
import re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'docs/plan/image-production'
OUT=ROOT/'assets/production'
PROJECT='project-eaa4c1cc-8f19-4d24-9e6'
ACCOUNT='arghawork3@gmail.com'
BUCKET=PROJECT+'-aod-batch'
LOCK_OBJECT='design-mocks/active-batch.lock.json'
TERMINAL={'JOB_STATE_SUCCEEDED','JOB_STATE_FAILED','JOB_STATE_CANCELLED','JOB_STATE_EXPIRED'}
TOKEN=None
SCAN=[]
def stamp(): return datetime.now(timezone.utc).isoformat()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); os.replace(temporary,path)
def digest(data): return hashlib.sha256(data).hexdigest()
def auth():
    global TOKEN
    if TOKEN is None:
        result=subprocess.run(['gcloud.cmd','auth','print-access-token','--account='+ACCOUNT,'--project='+PROJECT],capture_output=True,text=True,check=True)
        TOKEN=result.stdout.strip()
    return TOKEN
def api(url,method='GET',body=None,mime='application/json'):
    data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,headers={'Authorization':'Bearer '+auth(),'Content-Type':mime})
    try:
        with urllib.request.urlopen(req,timeout=90) as response: content=response.read()
    except urllib.error.HTTPError as error:
        # API status is useful; raw request/header/token is never logged.
        raise RuntimeError(f'HTTP {error.code} {method} {url.split("?")[0]}') from None
    return json.loads(content) if mime=='application/json' and content else content
def storage_meta(obj): return api('https://storage.googleapis.com/storage/v1/b/'+BUCKET+'/o/'+urllib.parse.quote(obj,safe=''))
def storage_get(obj): return api('https://storage.googleapis.com/storage/v1/b/'+BUCKET+'/o/'+urllib.parse.quote(obj,safe='')+'?alt=media',mime='application/octet-stream')
def upload(obj,data,mime='application/json',generation='0'):
    url='https://storage.googleapis.com/upload/storage/v1/b/'+BUCKET+'/o?uploadType=media&name='+urllib.parse.quote(obj,safe='')+'&ifGenerationMatch='+str(generation)
    # Response is JSON even though upload body has its real media type.
    response=api(url,'POST',data,mime)
    return json.loads(response) if isinstance(response,bytes) else response
def list_jobs():
    records=[]
    # Discover project locations instead of assuming the two previously inspected regions cover all work.
    locations=api(f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations')
    regions={'global','us','eu','us-central1'} | {p['locationId'] for p in locations.get('locations',[]) if re.fullmatch(r'[a-z]+(?:-[a-z]+)+[0-9]+',p['locationId'])}
    while locations.get('nextPageToken'):
        locations=api(f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations?pageToken='+urllib.parse.quote(locations['nextPageToken'],safe=''))
        regions |= {p['locationId'] for p in locations.get('locations',[]) if re.fullmatch(r'[a-z]+(?:-[a-z]+)+[0-9]+',p['locationId'])}
    for region in sorted(regions):
        base=f'https://{region+"-" if region!="global" else ""}aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{region}/batchPredictionJobs?pageSize=100'
        page=None
        while True:
            try: data=api(base+('&pageToken='+urllib.parse.quote(page,safe='') if page else ''))
            except RuntimeError as error:
                if str(error).startswith('HTTP 404 '):
                    SCAN.append({'location':region,'status':'NOT_SUPPORTED_BY_BATCH_ENDPOINT','evidence':str(error)})
                    break
                raise
            records.extend({'region':region,'name':j['name'],'state':j.get('state','UNKNOWN'),'displayName':j.get('displayName')} for j in data.get('batchPredictionJobs',[]))
            SCAN.append({'location':region,'status':'CHECKED','jobs':len(data.get('batchPredictionJobs',[])),'hasNextPage':bool(data.get('nextPageToken'))})
            page=data.get('nextPageToken')
            if not page: break
    return records
def provider_get(name): return api('https://aiplatform.googleapis.com/v1/'+name)
def persist_lock(data,generation):
    response=upload(LOCK_OBJECT,json.dumps(data).encode(),generation=generation)
    data['cloud_lock_generation']=response['generation']
    write(PLAN/'active-batch.lock.json',data)
    return response['generation']
def manifest(index): return read(PLAN/f'batch-{index:02}-manifest.json')
def validate_paid(m,b):
    def require(test,message):
        if not test: raise RuntimeError(message)
    require(m['model']=='gemini-3.1-flash-image' and m['project']==PROJECT and m['region']=='global','Wrong paid model/project/region')
    require(len(m['items'])==30 and len({i['id'] for i in m['items']})==30,'Need exactly30 unique useful requests')
    require(m['maxOutputTokens']==4096 and m['inputTokenUpperBoundPerRequest']==12000 and m['reservedUSD']>=6,'Cost bound/config changed; refuse submission')
    for item in m['items']:
        require(item['requestedOutputs']==1 and item['aspect'] in ['16:9','1:1'],'Invalid output count/aspect')
        require(len(item['prompt'].encode())<=8000,'Prompt exceeds conservative input token bound')
        require(digest(item['prompt'].encode())==item['promptSHA256'],'Prompt hash mismatch')
        p=ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'/item['styleReference']
        require(digest(p.read_bytes())==item['styleReferenceSHA256'],'Style hash mismatch')
        if item['guide']:
            require(digest((ROOT/item['guide']).read_bytes())==item['guideSHA256'],'Guide hash mismatch')
    import math
    require(math.isfinite(b['historicalMock']['conservativeReservation']) and b['historicalMock']['conservativeReservation']>=2,'Invalid historical reservation')
    require(len({x['id'] for x in b['batches']})==len(b['batches']),'Duplicate budget rows')
    require(all(math.isfinite(x['reservedUSD']) and x['reservedUSD']>=6 and (x.get('billedTotal') is None or math.isfinite(x['billedTotal']) and x['billedTotal']>=0) for x in b['batches']),'Invalid/negative reservation or billing')
    def batch_liability(x):
        if x.get('billedTotal') is not None and math.isfinite(x['billedTotal']): return x['billedTotal']
        if x.get('reconciledExposureUSD') is not None and math.isfinite(x['reconciledExposureUSD']) and x.get('providerState')=='JOB_STATE_SUCCEEDED':
            return x['reconciledExposureUSD']
        return x['reservedUSD']
    committed=max(b['historicalMock']['conservativeReservation'],b['historicalMock'].get('billedTotal') or 0)+sum(batch_liability(x) for x in b['batches'])
    require(b['hardCap']==80 and b['safetyReserve']>=15 and committed+m['reservedUSD']+b['safetyReserve']<=80,'Hard budget would be exceeded')
    return committed
def readiness(index):
    m=manifest(index); b=read(PLAN/'budget-ledger.json'); committed=validate_paid(m,b)
    jobs=list_jobs(); blockers=[j for j in jobs if j['state'] not in TERMINAL]
    report={'checkedAt':stamp(),'batch':m['id'],'requests':30,'locations':SCAN,'jobs':jobs,'blockers':blockers,'committedReservationUSD':committed,'newReservationUSD':m['reservedUSD'],'safetyUSD':b['safetyReserve'],'hardCapUSD':b['hardCap'],'ready':not blockers,'costBound':{'imageAndAnyOutputUpperUSD':30*m['maxOutputTokens']*30/1e6,'inputUpperUSD':30*m['inputTokenUpperBoundPerRequest']*.25/1e6,'batchReservationIncludesUSD':m['reservedUSD'],'actualInvoice':None}}
    write(PLAN/f'batch-{index:02}-readiness.json',report); return report
def submit(index):
    mutex=PLAN/'submission.mutex.json'
    fd=os.open(mutex,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,json.dumps({'pid':os.getpid(),'created':stamp(),'batch':index}).encode()); os.close(fd)
    safe_to_release=False
    try:
        report=readiness(index)
        if not report['ready']: safe_to_release=True; raise RuntimeError('Active/unknown authorized-project job; no submission')
        m=manifest(index); destination=OUT/m['id']
        if destination.exists(): safe_to_release=True; raise RuntimeError('Batch already has submission record; no repeat POST')
        old=read(PLAN/'active-batch.lock.json')
        name=old.get('provider_job_name') or old.get('provider_job') or old.get('operation_name') or old.get('provider_operation')
        if not name: name=old.get('job_name')
        # Historical lock field differs; only exact resource string qualifies.
        if not name:
            name=next((v for v in old.values() if isinstance(v,str) and '/batchPredictionJobs/' in v),None)
        if not name or provider_get(name).get('state') not in TERMINAL: safe_to_release=True; raise RuntimeError('Prior lock provider state not confirmed terminal')
        cloudmeta=storage_meta(LOCK_OBJECT); cloudold=json.loads(storage_get(LOCK_OBJECT))
        cloudname=next((v for v in cloudold.values() if isinstance(v,str) and '/batchPredictionJobs/' in v),None)
        if cloudname!=name: safe_to_release=True; raise RuntimeError('Local/cloud lock disagree; fail closed')
        if old.get('batch_id','').startswith('landscape-mocks'):
            old['owner_status']='DIRECTION_APPROVED_WITH_SYNC_CORRECTIONS_2026_10_03'
        else: old['owner_status']=old.get('owner_status','PRODUCTION_ASSETS_UNVERIFIED')
        old['workflow_state']='ARCHIVED_TERMINAL'; old['assetApproval']=old.get('assetApproval','UNVERIFIED')
        write(PLAN/'archive'/f'{old.get("batch_id",old.get("id","prior"))}.lock.json',old)
        record={'batch_id':m['id'],'model':m['model'],'project':PROJECT,'account':ACCOUNT,'state':'SUBMITTING_UNKNOWN','workflow_state':'RESERVED','createdAt':stamp(),'manifest_sha256':digest((PLAN/f'batch-{index:02}-manifest.json').read_bytes()),'requestedOutputs':30,'reservedUSD':m['reservedUSD'],'provider_job_name':None}
        generation=persist_lock(record,cloudmeta['generation'])
        destination.mkdir(parents=True,exist_ok=False); write(destination/'manifest.json',m)
        b=read(PLAN/'budget-ledger.json'); b['batches'].append({'id':m['id'],'reservedUSD':m['reservedUSD'],'state':'RESERVED_UNKNOWN','createdAt':stamp(),'usageEstimateUSD':None,'billedTotal':None}); write(PLAN/'budget-ledger.json',b)
        references={}
        for item in m['items']:
            paths=[ROOT/item['guide']] if item['guide'] else []
            paths.append(ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'/item['styleReference'])
            for path in paths:
                h=digest(path.read_bytes())
                if h not in references:
                    obj=f'production/{m["id"]}/reference/{h}{path.suffix}'
                    upload(obj,path.read_bytes(),'image/png' if path.suffix=='.png' else 'image/jpeg')
                    references[h]='gs://'+BUCKET+'/'+obj
        requests=[]
        for item in m['items']:
            parts=[{'text':item['prompt']}]
            paths=[ROOT/item['guide']] if item['guide'] else []
            paths.append(ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'/item['styleReference'])
            parts += [{'fileData':{'mimeType':'image/png' if p.suffix=='.png' else 'image/jpeg','fileUri':references[digest(p.read_bytes())]}} for p in paths]
            requests.append({'request':{'contents':[{'role':'user','parts':parts}],'generationConfig':{'responseModalities':['IMAGE'],'candidateCount':1,'maxOutputTokens':m['maxOutputTokens'],'imageConfig':{'aspectRatio':item['aspect']}}}})
        data=('\n'.join(json.dumps(r,separators=(',',':')) for r in requests)+'\n').encode()
        (destination/'input.jsonl').write_bytes(data); write(destination/'references.json',references)
        obj=f'production/{m["id"]}/input.jsonl'; upload(obj,data,'application/jsonl')
        payload={'displayName':m['id'],'model':'publishers/google/models/'+m['model'],'inputConfig':{'instancesFormat':'jsonl','gcsSource':{'uris':['gs://'+BUCKET+'/'+obj]}},'outputConfig':{'predictionsFormat':'jsonl','gcsDestination':{'outputUriPrefix':'gs://'+BUCKET+f'/production/{m["id"]}/output/'}}}
        write(destination/'submission.json',payload); write(destination/'ledger.json',record)
        # ONE POST. Timeout/network failure keeps UNKNOWN lock and mutex; human/metadata reconciliation required.
        job=api(f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/batchPredictionJobs','POST',payload)
        write(destination/'provider-job.json',job)
        record.update(provider_job_name=job['name'],state=job.get('state','UNKNOWN'),submittedAt=stamp(),workflow_state='PROVIDER_ACTIVE')
        persist_lock(record,generation); write(destination/'ledger.json',record)
        b['batches'][-1].update(state=record['state'],providerJob=job['name']); write(PLAN/'budget-ledger.json',b)
        safe_to_release=True
        print(json.dumps({'batch':m['id'],'name':job['name'],'state':job['state'],'reservedUSD':m['reservedUSD']}))
    finally:
        if safe_to_release: mutex.unlink(missing_ok=True)
def status(index):
    m=manifest(index); path=OUT/m['id']; ledger=read(path/'ledger.json'); job=provider_get(ledger['provider_job_name']); write(path/'provider-job.json',job)
    ledger.update(state=job.get('state','UNKNOWN'),checkedAt=stamp()); write(path/'ledger.json',ledger)
    # Status reads never mutate the shared submission lock. Readiness reconciles remote terminal state.
    print(json.dumps({'batch':m['id'],'state':job.get('state','UNKNOWN'),'completion':job.get('completionStats',{}),'output':job.get('outputInfo',{})})); return job
def collect(index):
    m=manifest(index); path=OUT/m['id']; job=status(index)
    if (path/'collection-report.json').exists():
        existing=read(path/'collection-report.json')
        if existing.get('technicalStatus')=='PASS': raise RuntimeError('Already collected: preserve immutable output/report')
    if job.get('state') not in TERMINAL: raise RuntimeError('Provider active/unknown: cannot collect')
    if index==1 and not (OUT/manifest(2)['id']/'provider-job.json').exists() and not (PLAN/'next-batch-deferred.json').exists():
        raise RuntimeError('Prepared useful batch2 must submit before collect1; use advance1. Record explicit budget/backlog defer if unavailable.')
    directory=job.get('outputInfo',{}).get('gcsOutputDirectory')
    if not directory: raise RuntimeError('No terminal output directory')
    prefix=directory.removeprefix('gs://'+BUCKET+'/'); token=None; objects=[]
    while True:
        url='https://storage.googleapis.com/storage/v1/b/'+BUCKET+'/o?prefix='+urllib.parse.quote(prefix,safe='')
        page=api(url+('&pageToken='+urllib.parse.quote(token,safe='') if token else '')); objects.extend(page.get('items',[])); token=page.get('nextPageToken')
        if not token: break
    target=path/'provider-output'; target.mkdir(exist_ok=True); rows=[]
    for obj in objects:
        if obj['name'].endswith('.jsonl'):
            content=storage_get(obj['name']); original=target/Path(obj['name']).name
            if original.exists() and original.read_bytes()!=content: raise RuntimeError('Refuse overwriting different raw original')
            if not original.exists(): original.write_bytes(content)
            rows += [json.loads(line) for line in content.decode().splitlines() if line.strip()]
    items={x['promptSHA256']:x for x in m['items']}; outputs=[]; errors=[]; used=set(); usage=[]
    for row in rows:
        parts=row.get('request',{}).get('contents',[{}])[0].get('parts',[]); prompt=next((p.get('text') for p in parts if 'text' in p),None)
        item=items.get(digest((prompt or '').encode()))
        if not item: errors.append('Unassociated echoed prompt'); continue
        if item['id'] in used: errors.append('Duplicate request '+item['id']); continue
        used.add(item['id']); response=row.get('response',{}); usage.append(response.get('usageMetadata',{})); found=[]
        for candidate in response.get('candidates',[]):
            for part in candidate.get('content',{}).get('parts',[]):
                if 'inlineData' in part and part['inlineData'].get('mimeType','').startswith('image/'):
                    try: blob=base64.b64decode(part['inlineData']['data'],validate=True); found.append((blob,part['inlineData']['mimeType']))
                    except Exception: errors.append(item['id']+': invalid base64')
        if len(found)<1: errors.append(f'{item["id"]}: expected1 actual{len(found)}'); continue
        blob,mime=found[-1]
        try:
            with Image.open(io.BytesIO(blob)) as image:
                image.load(); width,height=image.size; alpha='A' in image.getbands(); ext='.png' if mime=='image/png' else '.jpg'
                if (mime,image.format) not in [('image/png','PNG'),('image/jpeg','JPEG')]: errors.append(item['id']+': MIME/decode format mismatch')
                ratio=16/9 if item['aspect']=='16:9' else 1
                if abs(width/height-ratio)>.02 or not (850000<=width*height<=1200000): errors.append(item['id']+': invalid approximate1MP/aspect dimensions')
        except Exception: errors.append(item['id']+': invalid image decode'); continue
        filename=f'{item["position"]:02}-{item["id"]}{ext}'; p=path/'images'/filename; p.parent.mkdir(exist_ok=True)
        if p.exists() and p.read_bytes()!=blob: errors.append(item['id']+': refusing different original overwrite'); continue
        if not p.exists(): p.write_bytes(blob)
        outputs.append({'id':item['id'],'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':digest(blob),'mime':mime,'width':width,'height':height,'alpha':alpha,'promptSHA256':item['promptSHA256'],'reviewStatus':'UNVERIFIED','runtimeApproved':False,'requiredAlpha':item['requiredAlpha']})
    if len(outputs)!=30: errors.append(f'Expected30 outputs actual{len(outputs)}')
    if len({o['sha256'] for o in outputs})!=len(outputs): errors.append('Duplicate output bytes')
    report={'batch':m['id'],'collectedAt':stamp(),'requests':len(rows),'outputs':outputs,'errors':errors,'technicalStatus':'PASS' if not errors else 'FAIL','visualStatus':'UNVERIFIED','runtimeApproved':False,'usage':usage}
    write(path/'collection-report.json',report)
    lines=['# '+m['id'],'','Technical '+report['technicalStatus']+'; pixel/content/assembly review UNVERIFIED. No runtime approval.','']+['- ['+o['id']+'](images/'+Path(o['file']).name+')' for o in outputs]
    (path/'REVIEW-INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'batch':m['id'],'outputs':len(outputs),'errors':errors,'visualStatus':'UNVERIFIED'}))
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['readiness','submit','status','collect','advance']); parser.add_argument('batch',type=int,choices=list(range(1,19))); args=parser.parse_args()
    if args.action=='readiness': print(json.dumps(readiness(args.batch)))
    elif args.action=='submit': submit(args.batch)
    elif args.action=='status': status(args.batch)
    elif args.action=='collect': collect(args.batch)
    else:
        job=status(args.batch)
        if job.get('state') not in TERMINAL: raise RuntimeError('Current job active/unknown; advance stopped')
        if args.batch==1: submit(2)
        collect(args.batch)
if __name__=='__main__':
    try: main()
    except Exception as error: print(type(error).__name__+': '+str(error),file=sys.stderr); sys.exit(1)
