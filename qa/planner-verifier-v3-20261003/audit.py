"""Read-only verifier inputs; writes only to this new diagnostic directory."""
from pathlib import Path
import json, hashlib, importlib.util, copy, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
protected=[]
for directory in ['assets/production','assets/delivery','scripts','src','tests','dist']:
    for p in sorted((ROOT/directory).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts: protected.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
save('protected-input-snapshot.json',protected)
reports=[]; originals=[]
for p in sorted((ROOT/'assets/production').glob('production-*/collection-report.json')):
    r=load(p); reports.append({'batch':r['batch'],'count':len(r['outputs']),'reportSHA256':sha(p)})
    for o in r['outputs']: originals.append({'batch':r['batch'],'id':o['id'],'file':o['file'],'expected':o['sha256'],'actual':sha(ROOT/o['file'])})
save('current-originals.json',{'batches':reports,'count':len(originals),'distinctIDs':len(set(o['id'] for o in originals)),'mismatches':[o for o in originals if o['expected']!=o['actual']],'outputs':originals})
base=ROOT/'assets/delivery/stone-starter-20261003'
hall=[np.array(Image.open(base/p).convert('RGBA')) for p in ['derivatives/townhall-stone.png','derivatives/v2/townhall-stone.png','derivatives/v3/townhall-stone.png']]
v1,v2,v3=hall
mask=v1[:,:,3]>16
distance=cv2.distanceTransform(mask.astype('uint8'),cv2.DIST_L2,5)
counts={}
for name,a in zip(['v1','v2','v3'],hall):
    counts[name]={'opaque':int((a[:,:,3]>16).sum()),'lostV1':int((mask & (a[:,:,3]<=16)).sum()),'lostV1Deep12AllColours':int(((distance>12)&(a[:,:,3]<=16)).sum()),'lostV1Deep24AllColours':int(((distance>24)&(a[:,:,3]<=16)).sum()),'rgbChanged':int((np.any(a[:,:,:3]!=v1[:,:,:3],axis=2)&mask).sum())}
patches={}
for name,(x,y,w,h) in {'roof-central':(300,200,350,230),'front-wall':(420,520,230,170),'left-timber':(200,530,150,170),'right-timber':(680,550,150,170)}.items():
    valid=mask[y:y+h,x:x+w]; patches[name]={'rect':[x,y,w,h],'v1Opaque':int(valid.sum()),'v2Lost':int((valid&(v2[y:y+h,x:x+w,3]<=16)).sum()),'v3Lost':int((valid&(v3[y:y+h,x:x+w,3]<=16)).sum())}
colors=[(12,16,20),(255,255,255),(110,132,104)]
sheet=Image.new('RGB',(1536,590),(40,40,40)); d=ImageDraw.Draw(sheet)
for col,(name,a) in enumerate(zip(['v1','v2','v3'],hall)):
    for row,c in enumerate(colors):
        bg=Image.new('RGBA',(1024,1024),c+(255,)); bg.alpha_composite(Image.fromarray(a)); bg=bg.convert('RGB').resize((170,170))
        sheet.paste(bg,(col*512,row*190+20)); d.text((col*512,row*190),f'{name} full subject / {c}',fill='white')
        crop=Image.new('RGBA',(1024,1024),c+(255,)); crop.alpha_composite(Image.fromarray(a)); sheet.paste(crop.convert('RGB').crop((290,170,610,330)),(col*512+185,row*190+20))
sheet.save(OUT/'hall-comparison.png')
edge=Image.new('RGB',(1024*3,1024),(30,30,30))
for i,c in enumerate(colors):
    bg=Image.new('RGBA',(1024,1024),c+(255,)); bg.alpha_composite(Image.fromarray(v3)); edge.paste(bg.convert('RGB'),(i*1024,0))
edge.save(OUT/'hall-v3-native-backgrounds.png')
g1=np.array(Image.open(base/'derivatives/resource-gold.png').convert('RGBA')); g3=np.array(Image.open(base/'derivatives/v3/resource-gold.png').convert('RGBA'))
goldsheet=Image.new('RGB',(950,500),(30,30,30)); d=ImageDraw.Draw(goldsheet)
for row,(name,a) in enumerate([('v1',g1),('v3',g3)]):
    d.text((5,row*250+5),name,fill='white'); xs,ys=None,None
    yy,xx=np.where(a[:,:,3]>16); icon=Image.fromarray(a).crop((xx.min(),yy.min(),xx.max()+1,yy.max()+1))
    for j,c in enumerate(colors):
        for k,size in enumerate([18,36,160]):
            f=size/max(icon.size); small=icon.resize((round(icon.width*f),round(icon.height*f)),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(size+16,size+16),c+(255,)); tile.alpha_composite(small,(8,8)); goldsheet.paste(tile.convert('RGB'),(65+j*290+k*65,row*250+35))
goldsheet.save(OUT/'gold-comparison.png')
lum=lambda a: np.dot(a[:,:,:3].astype(float),[.299,.587,.114])
gm=g1[:,:,3]>16
save('independent-pixel-checks.json',{'hall':counts,'patches':patches,'gold':{'alphaChanged':int((g1[:,:,3]!=g3[:,:,3]).sum()),'rgbChanged':int((np.any(g1[:,:,:3]!=g3[:,:,:3],axis=2)&gm).sum()),'meanAbsLuminanceChange':float(np.abs(lum(g1)-lum(g3))[gm].mean()),'maxAbsLuminanceChange':float(np.abs(lum(g1)-lum(g3))[gm].max())}})
gates=module('audit_review_gates',ROOT/'scripts/review_gates.py')
joined=gates.evaluate(); fixtures=gates.safety_fixtures()
save('gate-checks.json',{'rows':len(joined['rows']),'historical':sum(r.get('reviewSource')=='HISTORICAL' for r in joined['rows']),'collectionOnly':sum(r.get('reviewSource')=='COLLECTION_ONLY' for r in joined['rows']),'stale':joined['stale'],'outputStale':joined['outputStale'],'scene':joined['scene'],'safetyFixtures':fixtures,'executorIntegrity':gates.interior_integrity()})
save('joined-rows.json',joined)
bench=load(ROOT/'qa/benchmark/report.json')
save('saved-benchmark-scope.json',{'hash':sha(ROOT/'qa/benchmark/report.json'),'at':bench['at'],'automated':len(bench['automated']),'failures':[c['id'] for c in bench['automated'] if c['status']=='FAIL'],'manual':bench['manual'],'assets':len(bench['assets'])})
dist=[]
for p in sorted((ROOT/'dist').rglob('*')):
    if p.is_file():
        rel=p.relative_to(ROOT/'dist'); source=ROOT/rel
        dist.append({'file':str(rel),'bytes':p.stat().st_size,'sourceExists':source.exists(),'equalsSource':source.exists() and sha(source)==sha(p)})
save('dist-scope.json',dist)
print(json.dumps({'batches':reports,'pixels':counts,'gates':{'rows':len(joined['rows']),'stale':len(joined['stale']),'outputStale':len(joined['outputStale']),'scene':joined['scene']},'fixtures':fixtures,'executorIntegrity':gates.interior_integrity(),'distFiles':len(dist)}))
