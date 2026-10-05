import json, hashlib, re, math
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path('C:/dev/ages-of-dominion-reborn')
OUT=Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(ROOT/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json')
protected={str(p.relative_to(ROOT)):sha(p) for base in ['assets','scripts','docs/plan/image-production','src'] for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
(OUT/'protected-before.json').write_text(json.dumps(protected,indent=2))
checks=[]
def walk(o,where='manifest'):
 if isinstance(o,dict):
  path=o.get('path',o.get('slicePath')); expected=o.get('sha256',o.get('sliceSHA256'))
  if path and expected:
   p=ROOT/path; result={'where':where,'path':path,'expected':expected,'exists':p.exists()}
   if p.exists():
    result['actual']=sha(p); result['hashMatch']=result['actual']==expected
    if p.suffix.lower()=='.png':
     im=Image.open(p); im.load(); result.update(size=list(im.size),mode=im.mode)
     result['dimensionMatch']=list(im.size)==o.get('dimensions',list(im.size))
     if im.mode=='RGBA': result['alphaExtrema']=list(im.getchannel('A').getextrema()); result['alphaBBox']=im.getchannel('A').getbbox()
   checks.append(result)
  for k,v in o.items(): walk(v,where+'.'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o): walk(v,where+f'[{i}]')
walk(m)
(OUT/'binding-checks.json').write_text(json.dumps(checks,indent=2))
rows=m['cleanUsableRows']+m.get('failedUnrecoverableRows',[])
print('top keys',list(m)); print('bindings',len(checks),'failures',[x for x in checks if not x.get('hashMatch') or not x.get('dimensionMatch',True)])
print('rows',len(rows)); print('categories', {c:sum(r.get('category')==c for r in rows) for c in set(r.get('category') for r in rows)})
summary=[]
groups={}
for r in rows:
 summary.append({k:r.get(k) for k in ['id','category','canonicalMapping','gates','notes']})
 d=r.get('derivative',{}); path=d.get('path')
 if path: groups.setdefault(r.get('category','unknown'),[]).append((r['id'],path))
 for part in r.get('parts',r.get('rigParts',[])):
  if 'slicePath' in part: groups.setdefault('rig-parts',[]).append((r['id']+' '+str(part.get('partIndex'))+' '+part.get('partName',''),part['slicePath']))
(OUT/'row-dispositions.json').write_text(json.dumps(summary,indent=2))
rig=read(ROOT/'assets/derivatives/rigs/parts_manifest.json')
groups['rig-parts']=[(rid+' '+str(p.get('partIndex'))+' '+p.get('partName',''),p['slicePath']) for rid,r in rig.items() for p in r['parts']]
for group,entries in groups.items():
 for page in range(math.ceil(len(entries)/12)):
  chunk=entries[page*12:(page+1)*12]
  canvas=Image.new('RGB',(1200,math.ceil(len(chunk)/4)*310),(220,220,220)); draw=ImageDraw.Draw(canvas)
  for i,(label,path) in enumerate(chunk):
   im=Image.open(ROOT/path).convert('RGBA'); im.thumbnail((290,210))
   x=(i%4)*300;y=(i//4)*310
   draw.text((x+3,y+3),label[:46],fill='black'); draw.text((x+3,y+17),label[46:90],fill='black')
   bg=Image.new('RGBA',(294,220),(110,132,104,255)); bg.alpha_composite(im,((294-im.width)//2,(220-im.height)//2));canvas.paste(bg.convert('RGB'),(x+3,y+34))
   for j,col in enumerate([(0,0,0,255),(255,255,255,255),(110,132,104,255)]):
    small=Image.open(ROOT/path).convert('RGBA');small.thumbnail((92,50));b=Image.new('RGBA',(94,50),col);b.alpha_composite(small,((94-small.width)//2,(50-small.height)//2));canvas.paste(b.convert('RGB'),(x+j*98+3,y+258))
  canvas.save(OUT/f'{group}-{page+1}.png')
index=(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')
refs=set(re.findall(r'\]\(([^)]+)\)',index)+re.findall(r'`([^`]+\.(?:md|json|txt))`',index))
docread=[]
for ref in sorted(refs):
 p=(ROOT/'docs/plan'/ref).resolve()
 if p.is_file() and p.suffix in ['.md','.json','.txt']:
  t=p.read_text(encoding='utf-8-sig'); docread.append({'path':str(p),'sha256':sha(p),'chars':len(t),'headings':re.findall(r'^#{1,3} .+',t,re.M)})
(OUT/'required-index-reading.json').write_text(json.dumps(docread,indent=2))
print('required index documents read',len(docread));print('sheets',list(groups))
