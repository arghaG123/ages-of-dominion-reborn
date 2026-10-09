import pathlib,json,hashlib,re
from PIL import Image,ImageDraw
import numpy as np
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
snap=read('qa/planner-post-code-20261007/input-hashes.json');buildings=read('src/data/age-buildings.json');new={r['id']:r for r in read('docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json')['rows']};rows=[];panels=[]
for age,b in buildings['ages'].items():
 for kind,r in b.items():
  if not isinstance(r,dict) or not r.get('file'):continue
  f=R/r['file'];raw=np.asarray(Image.open(f).convert('RGBA'));rgb=raw[:,:,:3].astype(np.int16);vis=raw[:,:,3]>128;m=vis&(rgb[:,:,0]>150)&(rgb[:,:,2]>120)&(rgb[:,:,1]<rgb[:,:,0]*.65)&(rgb[:,:,1]<rgb[:,:,2]*.75)
  snap[r['file']]={'sha256':sha(f),'bytes':f.stat().st_size};nr=new.get(kind+'-'+age);row={'id':kind+'-'+age,'age':age,'kind':kind,'actualRuntimePath':r['file'],'actualRuntimeSha256':sha(f),'actualRuntimeDimensions':list(Image.open(f).size),'magentaCandidateVisiblePixels':int(m.sum()),'residualOutput':nr.get('output') if nr else None,'sameAsResidual':bool(nr and nr.get('output',{}).get('path')==r['file']),'note':'Color candidates diagnostic; runtime screenshots confirm obvious TownHall magenta patches in Iron/Medieval/Modern.'};rows.append(row)
  if kind=='townhall' and age in ('iron','medieval','modern'):
   for label,p in [('currentCodeconsumer',f),('residualproducer',R/nr['output']['path'])]:
    im=Image.open(p).convert('RGBA');im.thumbnail((450,340));bg=Image.new('RGB',(470,385),(42,43,47));bg.paste(im,((470-im.width)//2,38),im);ImageDraw.Draw(bg).text((8,8),kind+'-'+age+' '+label,fill='white');panels.append(bg)
canvas=Image.new('RGB',(940,385*3),(35,35,38))
for i,p in enumerate(panels):canvas.paste(p,((i%2)*470,(i//2)*385))
canvas.save(Q/'runtime-townhall-vs-residual.jpg')
network=[]
for p in (R/'dist/src').rglob('*'):
 if p.is_file() and p.suffix in ('.js','.mjs','.json','.css'):
  for url in re.findall(r'https?://[^\s"\x27`)<>]+',p.read_text(encoding='utf-8-sig')):
   if url!='http://www.w3.org/2000/svg':network.append({'path':p.relative_to(R).as_posix(),'url':url})
(Q/'actual-building-bindings.json').write_text(json.dumps({'rows':rows,'runtimeNetworkReferences':network,'note':'Existing runtime age-building consumers differ from residual interface; clean residual candidates require metadata validation and later Code binding, not automatic remasking.'},indent=2))
(Q/'input-hashes.json').write_text(json.dumps(snap,indent=2))
print(json.dumps({'rows':len(rows),'magentaCandidateTownHalls':[[r['id'],r['magentaCandidateVisiblePixels']] for r in rows if r['kind']=='townhall'],'networkReferences':network},indent=2))
