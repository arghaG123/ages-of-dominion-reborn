import json, hashlib, zipfile, re
from pathlib import Path
from decimal import Decimal
from PIL import Image,ImageDraw
ROOT=Path('C:/dev/ages-of-dominion-reborn');OUT=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
e={};prod=ROOT/'docs/plan/image-production'
budget=read(prod/'budget-ledger.json');unified=read(prod/'UNIFIED-ACCOUNTING-RECONCILIATION-2026-10-04.json');journal=read(prod/'interactive-2k-later73-journal.json')
e['accounting']={'allRows':len(budget['batches']),'allRowsSumUSD':str(sum(Decimal(str(x['reconciledExposureUSD'])) for x in budget['batches'])),'productionBatchRows':sum(x['id'].startswith('production-') for x in budget['batches']),'productionBatchSumUSD':str(sum(Decimal(str(x['reconciledExposureUSD'])) for x in budget['batches'] if x['id'].startswith('production-'))),'unifiedBatchSum':unified['baseBreakdown']['batches01To17ActualUSD'],'baseSumUSD':str(Decimal('40.24')+sum(Decimal(str(x)) for x in unified['baseBreakdown']['buffers4K'].values())+Decimal('2')+Decimal('15')),'mainHeadlineFields':{k:v for k,v in budget.items() if any(s in k.lower() for s in ['reconcil','total','exposure','later','cost'])}}
successes={}
for a in journal['attempts']:
 if a.get('status')=='SUCCEEDED':successes[(a['id'],a.get('sha256'))]=a
e['accounting'].update(uniqueSuccesses=len(successes),journalUniqueSuccessSumUSD=str(sum(Decimal(str(x['costUSD'])) for x in successes.values())),journalHeadline=journal.get('summary'),unknownLiabilities=unified['later73UnknownLiabilities'])
# Independently sum saved final raw usage, without querying tariffs or provider.
usage={'promptTokenCount':0,'candidatesTokenCount':0,'thoughtsTokenCount':0,'totalTokenCount':0};raw=[]
for p in (ROOT/'assets/high-res/later73-preparation-packs').rglob('response.json'):
 r=read(p);u=r.get('usageMetadata',{});raw.append(str(p.relative_to(ROOT)))
 for k in usage:usage[k]+=u.get(k,0)
e['accounting']['rawResponseFiles']=len(raw);e['accounting']['rawUsageTotals']=usage
# Generic recursively inspect collection report hashes.
orig=[]
for p in (ROOT/'assets/production').glob('*/collection-report.json'):
 data=read(p)
 for o in data.get('outputs',[]):
  orig.append(o)
e['productionCollectionKeys']=list(read(next((ROOT/'assets/production').glob('*/collection-report.json'))))
e['productionOriginals']={'count':len(orig),'uniqueIDs':len(set(x['id'] for x in orig)),'mismatches':[x['file'] for x in orig if sha(ROOT/x['file'])!=x['sha256']]}
native=read(prod/'native4k-first32-delivery-manifest.json')
e['native4k']=[{'id':r['canonicalID'],'path':r['nativePath'],'hashMatch':sha(ROOT/r['nativePath'])==r['nativeSHA256'],'dimensions':list(Image.open(ROOT/r['nativePath']).size)} for r in native['items']]
g=read(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json')['geometry']['kingdom'];cg=read(ROOT/'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json')['geometry']
def proj(pt,mat):a,b,c,d,tx,ty=mat;x,y=pt;return [a*x+c*y+tx,b*x+d*y+ty]
e['geometry']={'active':g,'candidate':cg}
terrain=[('stone_v4','assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png')]+[(r['canonicalID'],r['nativePath']) for r in native['items'] if r['canonicalID'].startswith('kingdom-terrain')]
for name,path in terrain:
 im=Image.open(ROOT/path).convert('RGB');im=im.resize((1376,768));d=ImageDraw.Draw(im)
 for site in g['sites']:
  x,y,w,h=site['rect'];p=[tuple(proj(pt,g['worldToSource'])) for pt in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]];d.line(p+[p[0]],fill='cyan',width=3);d.text(p[0],site['id'],fill='white')
 for road in g['roads']:d.line([tuple(proj(pt,g['worldToSource'])) for pt in road],fill='yellow',width=3)
 for b in g.get('bridges',[]):
  x,y,w,h=b['rect'];p=[tuple(proj(pt,g['worldToSource'])) for pt in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]];d.line(p+[p[0]],fill='red',width=4)
 im.save(OUT/(name+'-active-overlay.png'))
# Fresh static APK closure; never build/install/launch.
apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'; closure=[]
with zipfile.ZipFile(apk) as z:
 for n in z.namelist():
  if n.startswith('assets/www/') and not n.endswith('/'):
   rel=n[len('assets/www/'):];p=ROOT/'dist'/rel;b=z.read(n);closure.append({'path':rel,'distExists':p.exists(),'match':p.exists() and hashlib.sha256(b).hexdigest()==sha(p)})
e['apk']={'sha256':sha(apk),'bytes':apk.stat().st_size,'files':len(closure),'mismatches':[x for x in closure if not x['match']]}
(OUT/'supplement-evidence.json').write_text(json.dumps(e,indent=2));(OUT/'apk-closure.json').write_text(json.dumps(closure,indent=2))
print('accounting',json.dumps(e['accounting'],indent=2));print('native4k',len(e['native4k']),'fail',sum(not r['hashMatch'] for r in e['native4k']));print('APK',e['apk']);print('collections',e['productionOriginals'])
# Native-detail patches for exact already-observed failures, all QA-only.
details=[('stone-floor','assets/derivatives/actors/troop-stone-melee.png',(450,1400,1450,1950)),('bronze-labels','assets/derivatives/actors/troop-bronze-ranged.png',(350,250,950,850)),('horse-floor','assets/derivatives/mounts/hero-mount-horse.png',(400,1300,1800,1875)),('barbarian-residue','assets/derivatives/rigs/rig-source-parts-barbarian_part_03.png',None),('paladin-source','assets/high-res/final-native2k/rig-source-parts-paladin.png',None),('healer-source','assets/high-res/final-native2k/rig-source-parts-healer.png',None)]
for name,path,box in details:
 im=Image.open(ROOT/path).convert('RGBA');im=im.crop(box) if box else im
 im.thumbnail((1000,1000));canvas=Image.new('RGB',(im.width*3,im.height))
 for i,col in enumerate([(0,0,0,255),(255,255,255,255),(110,132,104,255)]):
  b=Image.new('RGBA',im.size,col);b.alpha_composite(im);canvas.paste(b.convert('RGB'),(i*im.width,0))
 canvas.save(OUT/(name+'-detail.png'))
