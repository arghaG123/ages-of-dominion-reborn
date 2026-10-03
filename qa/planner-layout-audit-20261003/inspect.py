from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageChops

R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
def read(p): return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
c=read('qa/recovery-executor-20261003/kingdom-layout-candidate.json')
g=read('qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.json')
pack=json.loads((R/'design-preview/kingdom-layout-candidate-data.js').read_text().split(' = ',1)[1].rstrip(';\n'))
cam=c['camera']
def project(p):
 x,y=p; a,b,d,e,tx,ty=cam
 return [a*x+d*y+tx,b*x+e*y+ty]
def inverse(p):
 x,y=p; a,b,d,e,tx,ty=cam; det=a*e-b*d
 return [(e*(x-tx)-d*(y-ty))/det,(-b*(x-tx)+a*(y-ty))/det]
def poly(rect):
 x,y,w,h=rect
 return [project(p) for p in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]]
def mask(pol):
 im=Image.new('1',tuple(c['sourceSize'])); ImageDraw.Draw(im).polygon(pol,fill=1); return im
hallsite=c['geometry']['sites'][0]['rect']; hp=poly(hallsite)
points=[]
for p in c['surveyPoints']:
 w=inverse(p['source']); x,y,b,h=hallsite
 points.append(dict(id=p['id'],source=p['source'],world=w,inTownhallPad=x<=w[0]<=x+b and y<=w[1]<=y+h))
im=Image.open(R/c['hall']['file']).convert('RGBA'); alpha=im.getchannel('A'); bounds=alpha.point(lambda x:255 if x>16 else 0).getbbox()
m=c['hall']['matrix']; transform=lambda p:[m[0][0]*p[0]+m[0][2],m[1][1]*p[1]+m[1][2]]
pads=Image.new('1',tuple(c['sourceSize'])); dp=ImageDraw.Draw(pads)
for s in c['geometry']['sites'][1:]: dp.polygon(poly(s['rect']),fill=1)
roads=Image.new('1',tuple(c['sourceSize'])); dr=ImageDraw.Draw(roads)
for r in c['geometry']['roads']:dr.line([tuple(project(p)) for p in r],fill=1,width=16)
fixtures=c['fixtures']; conflicts=[]
for i,a in enumerate(fixtures):
 for b in fixtures[i+1:]:
  x,y,w,h=a['envelope']; u,v,q,t=b['envelope']
  dx=min(x+w,u+q)-max(x,u);dy=min(y+h,v+t)-max(y,v)
  if dx>0 and dy>0:conflicts.append([a['id'],b['id'],round(dx*dy,2)])
coll=[];errors=[];ids=[]
for p in sorted((R/'assets/production').glob('*/collection-report.json')):
 report=json.loads(p.read_text()); outputs=report['outputs']; coll.append({'batch':p.parent.name,'outputs':len(outputs)})
 for out in outputs:
  ids.append(out['id']); file=out.get('file') or out.get('path')
  if file:
   f=R/file
   if not f.exists(): f=p.parent/file
  else: f=next((p.parent/'images').glob('*-'+out['id']+'.*'))
  if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=out['sha256']:errors.append(str(f))
lock=read('docs/plan/image-production/active-batch.lock.json'); budget=read('docs/plan/image-production/budget-ledger.json')
manifests=[]
for n in range(14,18):
 p=f'docs/plan/image-production/batch-{n:02}-manifest.json'
 if not (R/p).exists():continue
 data=read(p); rows=data.get('requests',data.get('items',[]))
 manifests.append({'batch':n,'keys':list(data),'requests':len(rows),'sceneRows':[r for r in rows if 'kingdom-stone-day1' in r.get('id','')]})
closure=read('qa/recovery-executor-20261003/dist-closure.json'); dist=[]
for row in closure['assets']:
 p=R/'dist'/row['file']; dist.append({'file':row['file'],'matches':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']})
result={'hashes':{p:sha(p) for p in [c['hall']['file'],c['guide']['file'],'docs/plan/IMPLEMENTATION-CONTRACT.json','src/data/implementation-contract.json','src/data/stone-scene.json']},'previewDataMatchesCandidate':pack['candidate']==c,'guideDataAgreement':{k:g[k]==c[k] for k in ['camera','sourceSize','hall','surveyPoints','missingTerrain','viewportSafe']},'guideSitesAgree':g['sites']==c['geometry']['sites'],'guideRoadsAgree':g['roads']==c['geometry']['roads'],'opaqueBoundsAlpha16':bounds,'transformedOpaqueBounds':[transform(bounds[:2]),transform([bounds[2]-1,bounds[3]-1])],'padPolygon':hp,'points':points,'roadsPlotsRasterIntersection':ImageChops.logical_and(pads,roads).getbbox(),'fixtureRectangleIntersections':conflicts,'collection':coll,'outputs':len(ids),'distinctIds':len(set(ids)),'originalHashErrors':errors,'savedLock':lock,'budgetConservativeHoldsPlusMockReserve':sum(b['reservedUSD'] for b in budget['batches'])+budget['historicalMock']['conservativeReservation']+budget['safetyReserve'],'budgetKeys':list(budget),'budgetReconciledFields':{k:v for k,v in budget.items() if 'reconcil' in k.lower() or 'exposure' in k.lower()},'latestBudgetRows':budget['batches'][-2:],'manifests':manifests,'savedDistAssets':len(dist),'savedDistHashFailures':[d for d in dist if not d['matches']]}
(O/'artifact-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
