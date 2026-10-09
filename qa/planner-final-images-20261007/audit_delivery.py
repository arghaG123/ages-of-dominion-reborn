import json,pathlib,hashlib,collections,math,re,sys
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[2]; Q=R/'qa/planner-final-images-20261007'
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dims(v):return (v['width'],v['height']) if isinstance(v,dict) else tuple(v)
snap={}; report={'status':'INCOMPLETE','python':sys.version,'producers':{},'scenes':[],'preservation':[]}; rowsall=[]
cache={}
def checkfile(p,h=None,wh=None):
 p=pathlib.Path(p);p=p if p.is_absolute() else R/p
 if not p.is_file():return {'path':str(p),'exists':False}
 if str(p) in cache:
  out=dict(cache[str(p)]);out['hashMatch']=out['sha256']==h if h else None;out['dimensionMatch']=tuple(out.get('dimensions',[]))==dims(wh) if wh else None;return out
 digest=sha(p);snap[str(p.relative_to(R))]={'sha256':digest,'bytes':p.stat().st_size}
 out={'path':str(p),'exists':True,'sha256':digest,'hashMatch':digest==h if h else None}
 if p.suffix.lower() in ('.png','.jpg','.jpeg','.gif','.webp'):
  with Image.open(p) as im:
   im.load();out.update(dimensions=list(im.size),dimensionMatch=im.size==dims(wh) if wh else None,mode=im.mode)
   a=im.convert('RGBA').getchannel('A');out['alphaBBox']=a.getbbox();out['alphaExtrema']=a.getextrema()
 cache[str(p)]=dict(out);return out
for producer,prefix in [('environment','ENVIRONMENT-ART'),('actors','ACTORS-EQUIPMENT')]:
 path=f'docs/plan/{prefix}-RESIDUAL-INTERFACE-2026-10-07.json'; d=read(path);checkfile(path)
 cp=read(d['checkpoint']);checkfile(d['checkpoint'])
 ids=[x['id'] for x in d['rows']];ready=[x['id'] for x in d['rows'] if x['status']=='READY']
 summary={'rows':len(ids),'statuses':dict(collections.Counter(x['status'] for x in d['rows'])),'duplicateIds':[x for x,n in collections.Counter(ids).items() if n>1], 'phantomReady':sorted(set(d['readySubset'])-set(ready)), 'unlistedReady':sorted(set(ready)-set(d['readySubset'])), 'localProcessingCompleteClaim':cp.get('localProcessingComplete'),'localCompletionReason':cp.get('localCompletionReason'),'rowsAudit':[],'supportRows':[]}
 for row in d['rows']:
  rr={'id':row['id'],'producer':producer,'claimedStatus':row['status'],'claimedGates':row['gates'],'maxDisplayCssPx':row.get('maxDisplayCssPx'),'limitations':row.get('limitations'),'source':None,'output':None,'metadataProblems':[]}
  for key in ('source','output'):
   data=row.get(key)
   if data and data.get('path'):rr[key]=checkfile(data['path'],data.get('sha256'),data.get('dimensions'))
  out=rr['output']
  if out and out.get('exists') and out.get('dimensions'):
   w,h=out['dimensions']
   for key in ('groundContact','footprint'):
    for pt in row.get(key) or []:
     if not isinstance(pt,(list,tuple)) or len(pt)!=2:rr['metadataProblems'].append(f'{key} non-XY format: {pt}');continue
     if not(0<=pt[0]<=w and 0<=pt[1]<=h):rr['metadataProblems'].append(f'{key} outside output: {pt}')
   for key in ('entrance',):
    pt=row.get(key)
    if pt and not(0<=pt[0]<=w and 0<=pt[1]<=h):rr['metadataProblems'].append(f'{key} outside output: {pt}')
   env=row.get('heightEnvelope')
   if env and not isinstance(env,(list,tuple)):rr['metadataProblems'].append(f'heightEnvelope non-BoxXYXY format: {env}');env=None
   if env and (env[0]<0 or env[1]<0 or env[2]>w or env[3]>h):rr['metadataProblems'].append(f'heightEnvelope outside output: {env}')
  rr['missingEvidence']=[p for p in row.get('evidencePaths',[]) if not(R/p).exists()]
  rr['parts']=[{'name':x.get('name'),'matrix':x.get('matrix'),'check':checkfile(x['sourcePath'],x.get('sourceSha256'))} for x in row.get('transforms',{}).get('parts',[]) if x.get('sourcePath')]
  summary['rowsAudit'].append(rr);rowsall.append((row,rr))
 for row in d.get('supportRows',[]):summary['supportRows'].append({'id':row['id'],'check':checkfile(row['path'],row['sha256'],row['dimensions']),'contract':'NONSTANDARD_SUPPORT_ROW_NO_SOURCE_BINDING'})
 report['producers'][producer]=summary
 # Previous interface source/output bindings independently checked for preservation.
 old=read(f'docs/plan/{prefix}-INTERFACE-2026-10-06.json')
 for row in old['rows']:
  for key in ('source','output'):
   v=row.get(key)
   if v and v.get('path'):report['preservation'].append({'id':row['id'],'type':key,**checkfile(v['path'],v.get('sha256'))})
def project(pt):
 x,y=pt;return [60*x+25*y+170,-10*x+35*y+165]
def inside(p,poly):
 x,y=p;c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
def pd(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def sd(a,b,c,d):
 if cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0 and max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):return 0
 return min(pd(a,c,d),pd(b,c,d),pd(c,a,b),pd(d,a,b))
def distance(line,poly):
 if any(inside(p,poly) for p in line):return 0
 return min(sd(a,b,c,d) for a,b in zip(line,line[1:]) for c,d in zip(poly,poly[1:]+poly[:1]))
contract=read('src/data/implementation-contract.json')
print('CONTRACT KEYS',list(contract))
king=contract.get('kingdom',contract.get('geometry',{}).get('kingdom',{}));print('KINGDOM KEYS',list(king))
sites=king.get('sites',[])
if not sites:
 def find(v):
  if isinstance(v,dict):
   if 'sites' in v and isinstance(v['sites'],list):return v['sites']
   for c in v.values():
    r=find(c)
    if r:return r
  return []
 sites=find(contract)
for row in read('qa/image-residual-executor-20261007/environment/scenes.json'):
 rr={'id':row['id'],'status':row['status'],'promoted':row.get('promoted'),'source':checkfile(row['source']['path'],row['source']['sha256'],row['source']['dimensions']),'overlay':checkfile(row['overlay'],row.get('overlaySHA256')),'proposal':row.get('proposal'),'clearanceClaim':row.get('clearanceAudit'),'independentRoadChecks':[]}
 if row['mode']=='kingdom':
  for road in row['paintedRoadPolylines']:
   line=[[x/4,y/4] for x,y in road['polylineNative']];u=road.get('uncertaintyLegalPx',0)
   for site in sites:
    x,y,w,h=site['rect'];poly=[project(p) for p in [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]];dist=distance(line,poly)
    rr['independentRoadChecks'].append({'site':site['id'],'road':road['kind'],'distanceLegal':round(dist,3),'requiredLegal':8+u,'marginLegal':round(dist-8-u,3),'pass':dist>8+u})
 report['scenes'].append(rr)
# Source/testing/script snapshot: read only before/after comparison available to final verification.
for dirname in ('src','tests','scripts'):
 for p in (R/dirname).rglob('*'):
  if p.is_file() and '__pycache__' not in str(p):checkfile(p)
for p in (R/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images').glob('*.jpg'):checkfile(p)
Q.mkdir(exist_ok=True)
(Q/'input-hashes.json').write_text(json.dumps(snap,indent=2))
(Q/'delivery-checks.json').write_text(json.dumps(report,indent=2))
def sheet(items,path,cols=5,tw=330,th=240):
 canvas=Image.new('RGB',(cols*tw,math.ceil(len(items)/cols)*th),(42,42,45));dr=ImageDraw.Draw(canvas)
 for i,(label,p) in enumerate(items):
  x,y=i%cols*tw,i//cols*th;dr.text((x+6,y+4),label[:48],fill='white')
  if p and pathlib.Path(p).is_file():
   with Image.open(p) as im:
    im=im.convert('RGBA');im.thumbnail((tw-14,th-36));canvas.paste(im,(x+(tw-im.width)//2,y+30),im)
 canvas.save(Q/path)
for producer in ('environment','actors'):
 items=[(r['id']+' '+r['status'],R/r['output']['path']) for r,_ in rowsall if _['producer']==producer and r.get('output')]
 for i in range(0,len(items),40):sheet(items[i:i+40],f'{producer}-{i//40}.jpg')
sceneitems=[(r['id'],R/r['overlay']['path']) for r in report['scenes']];sheet(sceneitems,'scenes.jpg',4,480,290)
sheet([(p.name,p) for p in (R/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images').glob('*.jpg')],'references.jpg',5,390,240)
print('SUMMARY')
for k,v in report['producers'].items():
 bad=[r['id'] for r in v['rowsAudit'] if any(x and (not x['exists'] or x.get('hashMatch') is False or x.get('dimensionMatch') is False) for x in (r['source'],r['output']))]
 print(k,v['rows'],v['statuses'],'binding errors',bad,'coordinate bad rows',sum(bool(r['metadataProblems']) for r in v['rowsAudit']),'missing evidence',sum(bool(r['missingEvidence']) for r in v['rowsAudit']))
print('preservation mismatches',[x['id'] for x in report['preservation'] if not x['exists'] or x.get('hashMatch') is False])
for r in report['scenes'][:8]:print(r['id'],'road conflict count',sum(not x['pass'] for x in r['independentRoadChecks']))
