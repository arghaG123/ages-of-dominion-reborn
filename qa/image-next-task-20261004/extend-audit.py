from pathlib import Path
import json,hashlib
from collections import Counter,defaultdict
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=ROOT/'qa/image-next-task-20261004'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(n,x): (QA/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
q=read(ROOT/'docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json')
draft=[]
for x in q['items']:
    if x['imageSize']!='2K': continue
    sources=[]
    for s in x['sources']:
        p=ROOT/s['file']; item=dict(s); item['exists']=p.exists()
        if p.exists():
            item['actualSHA256']=sha(p); item['hashMatch']=item['actualSHA256']==s['sha256']
            with Image.open(p) as im: item['dimensions']=list(im.size)
        sources.append(item)
    group=x['group']; kind='hero painting' if 'HERO' in group else ('army role master' if 'ARMY' in group else ('articulation source sheet' if x['id'].startswith('rig-') else 'mount/transport or rival identity'))
    consumer='Hero/Equipment scene plus Adventure actor reference' if 'HERO' in group else ('Army + Tactical + Defense shared role identity' if 'ARMY' in group else 'Adventure/Tactical/Defense animation inputs or Story rival identity')
    draft.append({'group':group,'order':x['order'],'id':x['id'],'proposedResolution':'2K','purchaseStatus':'INACTIVE_OWNER_SCHEDULING_REQUIRED','requestKind':kind,'consumerNeed':consumer,'sources':sources,'executorWork':'Inspect existing pixels/semantic identity; choose source; prepare local role-specific references, exact prompt, crop/part/pose reservations and hash-bound request pack. Reuse existing sources for Code AI now. No POST.','sourceVisualStatus':'UNVERIFIED','ownerAcceptance':'UNVERIFIED'})
save('later73-preparation-manifest.json',{'scope':'Local preparation only; no purchase activation','count':len(draft),'counts':dict(Counter(x['group'] for x in draft)),'items':draft})
space=defaultdict(int); byrun=defaultdict(lambda:defaultdict(int)); large=[]
base=ROOT/'assets/high-res/interactive-4k-first32-20261003'
for p in base.rglob('*'):
    if not p.is_file(): continue
    size=p.stat().st_size; category=('final-native-output' if p.name=='output.png' else 'base64-response' if p.name=='response.json' else 'comparison' if p.name=='comparison.png' else 'viewport' if 'viewports' in p.parts else 'preparation-raster' if p.suffix.lower() in ['.png','.jpg','.jpeg'] else 'compact-metadata-or-other')
    space[category]+=size; byrun[p.relative_to(base).parts[0]][category]+=size
    if size>20_000_000: large.append({'file':p.relative_to(ROOT).as_posix(),'bytes':size,'category':category})
save('disk-usage.json',{'bytesByCategory':dict(space),'totalBytes':sum(space.values()),'MiBByCategory':{k:round(v/1048576,2) for k,v in space.items()},'byRun':{k:dict(v) for k,v in byrun.items()},'largeFiles':large,'cleanupPerformed':False,'eligibleForMoveOrDeletionNow':False,'reason':'32 technical PASS; full per-image spatial/content acceptance not established. Compact provenance/durable preservation must precede evidence retirement.'})
prior=read(ROOT/'qa/kingdom-image-progress-20261004/outputs.json')
save('prior24-preservation.json',[{'file':x['file'],'oldSHA256':x['sha256'],'currentSHA256':sha(ROOT/x['file']),'unchanged':sha(ROOT/x['file'])==x['sha256']} for x in prior])
noimage=[]
for p in base.glob('*/packs/*/response.json'):
    r=read(p); cand=r.get('candidates',[])
    if any(c.get('finishReason')=='NO_IMAGE' for c in cand):
        usage=r.get('usageMetadata',{}); cost=usage.get('promptTokenCount',0)*.5/1e6+usage.get('candidatesTokenCount',0)*60/1e6
        noimage.append({'file':p.relative_to(ROOT).as_posix(),'usage':usage,'savedRateIllustrationUSD':cost,'rateStatus':'Historical saved-rate arithmetic only, not invoice/tariff verification'})
save('no-image-usage.json',noimage)
print('Draft',len(draft),'sources',sum(len(x['sources']) for x in draft),'allsourcehashpass',all(s.get('hashMatch') for x in draft for s in x['sources']))
print(json.dumps({k:round(v/1048576,2) for k,v in space.items()},indent=2)); print('NO_IMAGE saved-rate arithmetic',sum(x['savedRateIllustrationUSD'] for x in noimage))
