"""Read-only asset audit and sandboxed offline runner probes. No provider calls."""
import sys, json, hashlib, base64, types, collections
from pathlib import Path
from decimal import Decimal
from PIL import Image, ImageOps, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path('C:/dev/ages-of-dominion-reborn')
QA=Path(__file__).parent
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d): (QA/n).write_text(json.dumps(d,indent=2),encoding='utf-8')
protected=[ROOT/p for p in ['docs/plan/image-production/budget-ledger.json','docs/plan/image-production/active-batch.lock.json','docs/plan/image-production/reconciled-accounting-ledger.json','scripts/interactive_runner_continuity.py','scripts/test_runner_continuity_offline.py']]
before={str(p):sha(p) for p in protected}
m=read('docs/plan/image-production/native4k-first32-delivery-manifest.json')
rows=[]; thumbs=[]
for i in m['items']:
 p=ROOT/i['nativePath']; resp=ROOT/i['responseBinding']['responseFile']
 with Image.open(p) as im:
  im.load(); dim=list(im.size); thumb=ImageOps.contain(im.convert('RGB'),(330,185));thumbs.append((i['canonicalID'],thumb))
 d=json.loads(resp.read_text(encoding='utf-8-sig'))
 blobs=[part['inlineData']['data'] for c in d.get('candidates',[]) for part in c.get('content',{}).get('parts',[]) if 'inlineData' in part]
 rh=sha(resp); oh=sha(p)
 rows.append({'id':i['canonicalID'],'path':i['nativePath'],'shaMatch':oh==i['nativeSHA256'],'decodeDimensions':dim,'responseHashMatch':rh==i['responseBinding']['responseSHA256'],'responseImageMatch':any(hashlib.sha256(base64.b64decode(b)).hexdigest()==oh for b in blobs),'exactWireEvidence':i['exactWireEvidence']})
save('native32-verification.json',rows)
sheet=Image.new('RGB',(1320,8*215),'#202124');draw=ImageDraw.Draw(sheet)
for k,(label,thumb) in enumerate(thumbs):
 x=(k%4)*330;y=(k//4)*215;sheet.paste(thumb,(x,y));draw.text((x+5,y+188),label,fill='white')
sheet.save(QA/'native32-contact.jpg')
later=read('docs/plan/IMAGE-LATER73-LOCAL-PREPARATION-MANIFEST-2026-10-04.json'); packs=[]
for i in later['items']:
 p=ROOT/i['localPackDir']; meta=json.loads((p/'request_meta.json').read_text(encoding='utf-8-sig')); prompt=(p/'prompt.txt').read_text(encoding='utf-8-sig');layout=json.loads((p/'layout_spec.json').read_text(encoding='utf-8-sig'))
 source=[]
 for s in i['sources']:
  f=ROOT/s['file']
  with Image.open(f) as im:im.load();dims=list(im.size)
  source.append({'file':s['file'],'shaMatch':sha(f)==s['sha256'],'dimensions':dims})
 packs.append({'id':i['id'],'group':i['group'],'order':i['order'],'promptStringHashMatch':hashlib.sha256(prompt.encode()).hexdigest()==meta['promptSHA256'],'promptEqualsMeta':prompt==meta['prompt'],'resolution':meta['requestedSize'],'source':source,'layout':layout,'purchaseStatus':meta['purchaseStatus'],'paidCallsAllowed':meta['paidCallsAllowed']})
save('later73-verification.json',packs)
ledger=read('docs/plan/image-production/reconciled-accounting-ledger.json');budget=read('docs/plan/image-production/budget-ledger.json')
components=sum(Decimal(str(v)) for v in ledger['componentsUSD'].values());batchsum=sum(Decimal(str(b.get('reconciledExposureUSD',0))) for b in budget['batches'])
save('accounting-check.json',{'reportedProtectedExposure':ledger['reconciledProtectedExposureUSD'],'componentSum':str(components),'unexplainedDifference':str(Decimal(str(ledger['reconciledProtectedExposureUSD']))-components),'budgetRowsSumPlusMockReserve':str(batchsum+Decimal(17)),'historical17RowSum':str(sum(Decimal(str(b['reconciledExposureUSD'])) for b in budget['batches'][:17])),'historical17ReconciliationTrail':budget['reconciliationTrail']['reconciledBatches01To17TotalUSD'],'noImageSavedTariff':str(Decimal(2484)*Decimal('.5')/Decimal(1000000)+Decimal(87)*Decimal(2)/Decimal(1000000)),'noImageCurrentStandardTariff':str(Decimal(2484)*Decimal('.5')/Decimal(1000000)+Decimal(87)*Decimal(3)/Decimal(1000000)),'all73ImageOutputOnly':str(Decimal(73)*Decimal(1680)*Decimal(60)/Decimal(1000000)),'invoices':'UNKNOWN'})
cleanup=read('docs/plan/image-production/cleanup-summary.json');deleted=cleanup['deletedFiles']
save('cleanup-check.json',{'listedCount':len(deleted),'uniquePaths':len({d['file'] for d in deleted}),'listedBytesSum':sum(d['bytes'] for d in deleted),'reportedBytes':cleanup['totalReclaimedBytes'],'pathsStillPresent':[d['file'] for d in deleted if (ROOT/d['file']).exists()],'finalNative4kFiles':list(str(p.relative_to(ROOT)) for p in (ROOT/'assets/production/final-native4k').iterdir()),'deletionHistoryAndPreDeleteHashes':'Not independently reconstructable from absence alone'})
# Load source without executing its test main or generating bytecode; redirect EVERY runner path.
mod=types.ModuleType('sandbox_runner');exec(compile((ROOT/'scripts/interactive_runner_continuity.py').read_text(encoding='utf-8-sig'),'runner','exec'),mod.__dict__)
sandbox=QA/'runner-sandbox';sandbox.mkdir(exist_ok=True)
mod.ROOT=sandbox;mod.PLAN_PROD=sandbox;mod.MUTEX_FILE=sandbox/'submission.mutex.json';mod.LOCAL_LOCK_FILE=sandbox/'active-batch.lock.json';mod.BUDGET_FILE=sandbox/'budget-ledger.json'
probes=[]
def record(name,observed):probes.append({'probe':name,'observed':observed})
a=mod.ContinuityRunner('same-owner');b=mod.ContinuityRunner('same-owner');a.acquire_mutex();b.acquire_mutex();record('same_owner_second_instance',{'firstHasLock':a.has_lock,'secondHasLock':b.has_lock})
g=sandbox/'geometry.json';g.write_text(json.dumps({'worldToSource':None,'sites':[],'bridges':[{'id':'bridge','rect':[12.15,7.2,1.55,.85],'cells':[[12,7],[14,7]]}]}))
record('empty_sites_invalid_camera_short_bridge',a.check_measured_geometry(sandbox))
bodysha=a.write_ahead_persisted_request(sandbox,'mock','prompt',{},.2);record('persisted_body_byte_hash',{'returned':bodysha,'actual':sha(sandbox/'request_body.json'),'match':bodysha==sha(sandbox/'request_body.json')})
rr=mod.ContinuityRunner('429');first=rr.execute_mock_request('mock','429_RETRY_ONCE',0);second=rr.execute_mock_request('mock','429_RETRY_ONCE',1);record('immediate_429_retry',{'first':first['status'],'second':second['status'],'firstBackoff':first['backoffSeconds']})
record('new_instance_pacing',{'nextAllowedPostAt':mod.ContinuityRunner().next_allowed_post_at})
a.release_mutex('UNKNOWN');record('unknown_state_persisted',json.loads(mod.MUTEX_FILE.read_text()));a.release_mutex();record('default_release_after_unknown',json.loads(mod.MUTEX_FILE.read_text()))
save('runner-probes.json',probes)
save('protected-file-preservation.json',{'before':before,'after':{str(p):sha(p) for p in protected},'unchanged':all(sha(p)==before[str(p)] for p in protected)})
print(json.dumps({'native32':len(rows),'nativeAllChecksPass':all(x['shaMatch'] and x['decodeDimensions']==[5504,3072] and x['responseHashMatch'] and x['responseImageMatch'] for x in rows),'later73':len(packs),'laterSourcesAllMatch':all(s['shaMatch'] for p in packs for s in p['source']),'laterPromptHashesMatch':sum(p['promptStringHashMatch'] for p in packs),'runnerProbes':probes,'qa':str(QA)},indent=2))
