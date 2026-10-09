import json,pathlib,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parents[2];Q=R/'qa/planner-final-images-20261007'
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
results=[];special=[]
ids={'troop-stone-melee','troop-stone-ranged','troop-industrial-ranged','troop-industrial-heavy','armory-stone','barracks-stone','skill-offense','gear-stone-boots','attacker-bronze-runner','troop-iron-melee'}
for pre in ('ENVIRONMENT-ART','ACTORS-EQUIPMENT'):
 d=read(f'docs/plan/{pre}-RESIDUAL-INTERFACE-2026-10-07.json')
 for row in d['rows']:
  if not row.get('output'):continue
  with Image.open(R/row['output']['path']) as im:arr=np.array(im.convert('RGBA'),dtype=np.int16)
  rgb=arr[:,:,:3];a=arr[:,:,3];mag=(rgb[:,:,0]>140)&(rgb[:,:,2]>120)&(rgb[:,:,1]<.65*np.minimum(rgb[:,:,0],rgb[:,:,2]))&(a>128)
  rr={'id':row['id'],'producer':d['producer'],'alphaOpaqueFraction':float(np.mean(a>128)),'alphaNonzeroFraction':float(np.mean(a>0)),'magentaCandidateVisiblePixels':int(mag.sum()),'note':'Color candidate counts are diagnostics, not automatic semantic failure.'}
  results.append(rr)
  if row['id'] in ids:special.append(row)
canvas=Image.new('RGB',(1600,math.ceil(len(special)/2)*345),(35,35,38));dr=ImageDraw.Draw(canvas)
for idx,row in enumerate(special):
 x=(idx%2)*800;y=(idx//2)*345;dr.text((x+8,y+5),row['id']+'   SOURCE / DELIVERED',fill='white')
 for j,key in enumerate(('source','output')):
  with Image.open(R/row[key]['path']) as im:
   im=im.convert('RGBA');im.thumbnail((380,300));bg=Image.new('RGBA',(380,300),'white');bg.alpha_composite(im,((380-im.width)//2,(300-im.height)//2));canvas.paste(bg.convert('RGB'),(x+8+j*390,y+30))
canvas.save(Q/'native-source-output-diagnostics.jpg')
(Q/'pixel-metrics.json').write_text(json.dumps(results,indent=2))
print('regenerated metrics',[r for r in results if r['id'] in ['troop-stone-melee','troop-stone-ranged','troop-industrial-ranged','troop-industrial-heavy']])
print('magenta candidates >500',[(r['id'],r['magentaCandidateVisiblePixels']) for r in results if r['magentaCandidateVisiblePixels']>500])
# Runtime/reference gallery built from actual loaded browser captures, not producer claims.
mapping={'home-1280':'01-home','kingdom-day1':'02-kingdom-day1','adventure':'11-adventure-overview','hero':'19-hero-equipment','army':'24-army','forge':'22-forge','story':'25-story','settings':'28-settings','tactical':'14-tactical-deployment'}
refdir=R/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
cv=Image.new('RGB',(1600,len(mapping)*330),(30,30,34));draw=ImageDraw.Draw(cv)
for i,(name,ref) in enumerate(mapping.items()):
 draw.text((8,i*330+5),name+' APPROVED REFERENCE / CURRENT RUNTIME (no successor integration)',fill='white')
 for j,p in enumerate([refdir/(ref+'.jpg'),Q/'pixels'/(name+'.png')]):
  if not p.exists():continue
  with Image.open(p) as im:im=im.convert('RGB');im.thumbnail((788,300));cv.paste(im,(j*800+(800-im.width)//2,i*330+26))
cv.save(Q/'reference-runtime.jpg')
