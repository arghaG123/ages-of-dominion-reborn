"""Read-only recovery audit; writes diagnostic evidence only in this directory."""
from pathlib import Path
import sys, json, hashlib, copy
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path('C:/dev/ages-of-dominion-reborn')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
import review_gates

def read(p): return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ledger = read('assets/delivery/stone-starter-20261003/gate-ledger.json')
review = read('docs/plan/image-production/VERIFIER-REVIEW-20261003.json')
registry = read('docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json')
result = review_gates.evaluate()
records = []
for item in ledger['assets']:
    src, dst = ROOT / item['sourceFile'], ROOT / item['derivative']
    with Image.open(dst) as im:
        im.load(); size, mode = list(im.size), im.mode
    record = dict(id=item['id'], batch=item['batch'], sourceFile=item['sourceFile'], sourceSHA256=sha(src), sourceMatch=sha(src)==item['sourceSHA256'], derivative=item['derivative'], derivativeSHA256=sha(dst), derivativeMatch=sha(dst)==item['derivativeSHA256'], size=size, mode=mode)
    if 'registration' in item:
        reg = item['registration']
        record['registration'] = reg
        with Image.open(dst) as im: arr=np.array(im)
        ys,xs=np.where(arr[:,:,3]>16)
        m=np.array(reg['placementMatrix'])
        placed=m @ np.vstack((xs,ys,np.ones(len(xs))))
        record['placedOpaqueBounds']=[float(placed[0].min()),float(placed[1].min()),float(placed[0].max()),float(placed[1].max())]
        record['opaquePixelsOutsideSource']=int(((placed[0]<0)|(placed[0]>=1376)|(placed[1]<0)|(placed[1]>=768)).sum())
        site=next(s for s in read('docs/plan/IMPLEMENTATION-CONTRACT.json')['geometry']['kingdom']['sites'] if s['id']==reg['siteId'])
        a,b,c,d,e,f=ledger['camera']; x,y,w,h=site['rect']
        expected=np.array([a*(x+w/2)+c*(y+h/2)+e,b*(x+w/2)+d*(y+h/2)+f])
        actual=m@np.array(reg['groundPivot']+[1])
        record['pivotTargetErrorPx']=float(np.linalg.norm(actual-expected))
    records.append(record)

# These fixtures inject metadata only; no production file is changed.
base_item=next(x for x in review['assets'] if x['id']=='skill-offense' and x['batch']=='production-03-20261003')
base_extra=next(x for x in ledger['assets'] if x['id']=='skill-offense')
def probe(extra, visual=None, sources=None):
    return review_gates.evaluate(review_items=[base_item], registry_items=sources or [], delivery={'assets':[extra]}, visual=visual or {'assets':[]})
stale=copy.deepcopy(base_extra); stale['derivative']='qa/recovery-verifier-20261003/does-not-exist.png'; stale['derivativeSHA256']='0'*64
missing=probe(stale)['rows'][0]
auto_fail=copy.deepcopy(base_extra); auto_fail['gates']['matte']['status']='FAIL'
note={'batch':base_item['batch'],'id':base_item['id'],'sourceSHA256':base_item['sourceSHA256'],'gates':{'matte':'PASS','runtime':'PASS','ownerAcceptance':'PASS'}}
no_promotion=probe(auto_fail,{'assets':[note]})['rows'][0]
stale_note=copy.deepcopy(note); stale_note['derivativeSHA256']='0'*64; stale_note['gates']['matte']='FAIL'
visual_result=probe(base_extra,{'assets':[stale_note]})['rows'][0]
wrong_path=copy.deepcopy(next(s for s in registry['sources'] if s['id']=='skill-offense')); wrong_path['sourceFile']='qa/recovery-verifier-20261003/does-not-exist.png'
path_result=probe(base_extra,sources=[wrong_path])['selected'][0]
probes={
 'staleSourceFixtureRejected':review_gates.stale_fixture(),
 'missingWrongHashDerivative':{'matte':missing['gates']['matte'],'derivative':missing['derivative'],'staleCount':len(probe(stale)['stale'])},
 'staleDerivativeVisualApplied':visual_result['gates']['matte']=='FAIL',
 'registryWrongSourcePathAccepted':path_result['acceptedForRecovery'],
 'automatedFailPreserved':no_promotion['gates']['matte']=='FAIL',
 'runtimeOwnerNotPromoted':not no_promotion['runtimeApproved'] and not no_promotion['ownerAccepted'] and no_promotion['gates']['runtime']!='PASS' and no_promotion['gates']['ownerAcceptance']!='PASS'
}
originals=[]
for report in sorted((ROOT/'assets/production').glob('*/collection-report.json')):
    for item in json.loads(report.read_text(encoding='utf-8-sig'))['outputs']:
        p=ROOT/item['file']
        with Image.open(p) as im: im.load(); valid_size=list(im.size)==[item['width'],item['height']]
        originals.append({'batch':report.parent.name,'id':item['id'],'file':item['file'],'sha256':sha(p),'match':sha(p)==item['sha256'],'dimensionsMatch':valid_size})
guides=[]
for batch in (1,2,3):
    for item in read(f'docs/plan/image-production/batch-{batch:02}-manifest.json')['items']:
        if item.get('guide') and item['id']=='townhall-stone':
            p=ROOT/item['guide']; guides.append(dict(batch=batch,file=item['guide'],expected=item['guideSHA256'],actual=sha(p),match=item['guideSHA256']==sha(p)))
terrain=next(x for x in ledger['assets'] if x['id']=='kingdom-terrain-stone')
delta=np.abs(np.array(Image.open(ROOT/terrain['derivative']).convert('RGB')).astype(np.int16)-np.array(Image.open(ROOT/terrain['sourceFile']).convert('RGB')).astype(np.int16)).sum(axis=2)
summary={'reviewRows':len(result['rows']),'fresh':sum(r['hashMatch'] for r in result['rows']),'stale':len(result['stale']),'selectedFresh':sum(s['acceptedForRecovery'] for s in result['selected']),'sourceContentPass':sum(r['gates']['sourceContent']=='PASS' for r in result['rows']),'runtimeApproved':sum(r['runtimeApproved'] for r in result['rows']),'ownerAccepted':sum(r['ownerAccepted'] for r in result['rows']),'originals':len(originals),'originalsHashPass':sum(o['match'] for o in originals),'originalsDecodeSizePass':sum(o['dimensionsMatch'] for o in originals),'derivatives':len(records),'derivativeHashPass':sum(r['derivativeMatch'] and r['sourceMatch'] for r in records),'terrainEditedPixelsOver12':int((delta>12).sum()),'compositeSHA256':sha(ROOT/ledger['composite']['file']),'compositeHashMatch':sha(ROOT/ledger['composite']['file'])==ledger['composite']['sha256']}
snapshot_paths=['scripts/review_gates.py','scripts/recover_first_delivery.py','scripts/benchmark.py','qa/delivery-20261003/visual-gates.json','assets/delivery/stone-starter-20261003/gate-ledger.json','assets/delivery/stone-starter-20261003/processing-record.json','docs/plan/image-production/VERIFIER-REVIEW-20261003.json','docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json','docs/plan/IMPLEMENTATION-CONTRACT.json','src/data/reviewed-source-selection.json','src/client/main.js','src/client/game.css','design-preview/feedback-20261003/index.html','design-preview/feedback-20261003/preview-manifest.json','design-preview/feedback-20261003/check.cjs','qa/benchmark/report.json','qa/section-preview-20261003/checks.json']
snapshot={p:sha(ROOT/p) for p in snapshot_paths}

# Lossless 1:1 PNG edge crops on three backgrounds, without changing derivatives.
crops={'skill-offense':(280,152,792,192),'resource-stone':(330,155,720,330),'resource-food':(150,110,470,340),'resource-wood':(580,700,920,850),'resource-gold':(550,745,870,865),'farm-stone':(510,225,880,415),'lumber-stone':(800,390,1000,550),'quarry-stone':(350,40,720,275),'mine-stone':(600,280,950,450),'townhall-stone':(470,840,980,1010)}
for ident, box in crops.items():
    im=Image.open(ROOT/f'assets/delivery/stone-starter-20261003/derivatives/{ident}.png').convert('RGBA').crop(box)
    w,h=im.size; sheet=Image.new('RGB',(w*3,h+24),(36,36,36)); d=ImageDraw.Draw(sheet)
    for n,color in enumerate(((0,0,0),(255,255,255),(110,132,104))):
        bg=Image.new('RGBA',(w,h),color+(255,)); bg.alpha_composite(im)
        sheet.paste(bg.convert('RGB'),(n*w,24)); d.text((n*w+4,5),f'{ident} {box} RGB{color}',fill='white')
    sheet.save(OUT/f'edge-{ident}.png')

# Apply only the frozen source-to-viewport fit to the actual composite and reference.
comp=Image.open(ROOT/ledger['composite']['file']).convert('RGB')
ref=Image.open(ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/03-kingdom-stone.jpg').convert('RGB')
for vw,vh in read('docs/plan/IMPLEMENTATION-CONTRACT.json')['viewports']:
    for label,im in [('composite',comp),('reference',ref)]:
        scale=min(vw/1376,vh/768); fit=(round(1376*scale),round(768*scale)); out=Image.new('RGB',(vw,vh),(24,32,35)); out.paste(im.resize(fit,Image.Resampling.LANCZOS),((vw-fit[0])//2,(vh-fit[1])//2)); out.save(OUT/f'{label}-{vw}x{vh}.png')
data={'summary':summary,'fixtures':probes,'delivery':records,'originals':originals,'guides':guides,'snapshot':snapshot,'joinedDeliveryGates':[r for r in result['rows'] if any(x['id']==r['id'] and x['batch']==r['batch'] for x in ledger['assets'])]}
(OUT/'audit.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'summary':summary,'fixtures':probes,'guides':guides,'registration':[{'id':r['id'],'bounds':r['placedOpaqueBounds'],'outside':r['opaquePixelsOutsideSource'],'pivotError':r['pivotTargetErrorPx']} for r in records if 'registration' in r]},indent=2))
