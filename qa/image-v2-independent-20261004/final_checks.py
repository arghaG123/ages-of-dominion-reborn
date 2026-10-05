import json,hashlib,zipfile
from pathlib import Path
from decimal import Decimal
from PIL import Image,ImageDraw
ROOT=Path('C:/dev/ages-of-dominion-reborn');OUT=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json');rows=m['cleanUsableRows']+m['failedUnrecoverableRows']
canvas=Image.new('RGB',(1200,900),(210,210,210));d=ImageDraw.Draw(canvas)
for i,r in enumerate([r for r in rows if r['id'].startswith('rival-identity')]):
 mp=r.get('canonicalMapping',{});d.text((i%3*400+3,i//3*450+3),mp.get('canonicalName','')+' / '+r['id'],fill='black');d.text((i%3*400+3,i//3*450+20),'Old baseline (left) / current card (right)',fill='black')
 name=mp.get('canonicalName','');num=mp.get('rNum',mp.get('baselineRivalNumber'))
 if num is None:
  num={'Bran the Relentless':4,'Malakor the Flayed':2,'Thalric Ash-Bane':3,'Soren the Unforgiving':6,'Varek Iron-Eye':1,'Karn Blood-Tide':5}.get(name)
 for j,p in enumerate([Path(f'C:/dev/ages-of-dominion/public/art/rival-{num}.webp'),ROOT/r['derivative']['path']]):
  if p.exists():
   im=Image.open(p).convert('RGB');im.thumbnail((194,360));canvas.paste(im,(i%3*400+j*200,i//3*450+65))
canvas.save(OUT/'rival-baseline-comparison.png')
bindings=read(OUT/'binding-checks.json');report={'uniqueBoundFiles':len(set(x['path'] for x in bindings)),'references':len(bindings)}
e=read(OUT/'supplement-evidence.json')
apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
rootchecks=[]
with zipfile.ZipFile(apk) as z:
 for n in z.namelist():
  if n.startswith('assets/www/') and not n.endswith('/'):
   rel=n[11:];p=ROOT/rel
   if p.exists():rootchecks.append({'path':rel,'match':hashlib.sha256(z.read(n)).hexdigest()==sha(p)})
report['apkRootMatches']={'count':len(rootchecks),'failures':[r for r in rootchecks if not r['match']]}
report['accountingRawEstimateRecordedRates']=str(Decimal(e['accounting']['rawUsageTotals']['promptTokenCount'])*Decimal('.5')/Decimal(1000000)+Decimal(73*1680)*Decimal(60)/Decimal(1000000)+Decimal(e['accounting']['rawUsageTotals']['candidatesTokenCount']-73*1680)*Decimal(3)/Decimal(1000000))
report['mainLedgerExposure']=str(Decimal(e['accounting']['allRowsSumUSD'])+Decimal('2')+Decimal('15'))
report['manifestSHA256']=sha(ROOT/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json')
aliases=[]
for r in rows:
 for path in r.get('derivative',{}).get('allDerivativePaths',[]):
  p=ROOT/path;aliases.append({'path':path,'exists':p.exists(),'hashMatch':p.exists() and sha(p)==r['derivative']['sha256']})
report['portraitAliases']={'count':len(aliases),'failures':[x for x in aliases if not x['hashMatch']]}
raws=[]
for p in (ROOT/'assets/high-res/later73-preparation-packs').rglob('response.json'):
 data=read(p);parts=data['candidates'][0]['content']['parts'];images=[x['inlineData'] for x in parts if 'inlineData' in x]
 import base64
 b=base64.b64decode(images[0]['data']);final=ROOT/'assets/high-res/final-native2k'/ (p.parent.name+'.png')
 raws.append({'id':p.parent.name,'nativeMatchesRaw':final.exists() and hashlib.sha256(b).hexdigest()==sha(final)})
report['rawNativeBindings']={'count':len(raws),'failures':[x for x in raws if not x['nativeMatchesRaw']]}
(OUT/'final-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
