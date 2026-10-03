from pathlib import Path
import json, hashlib, re
import numpy as np, cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hall=np.array(Image.open(ROOT/'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png'))
r,g,b=hall[:,:,0].astype(int),hall[:,:,1].astype(int),hall[:,:,2].astype(int)
pink=(hall[:,:,3]>16)&(r>120)&(b>g+30)&(g<140)
n,labels,stats,cent=cv2.connectedComponentsWithStats(pink.astype('uint8'),8)
components=sorted(stats[1:].tolist(),key=lambda s:s[4],reverse=True)[:12]
sheet=Image.new('RGB',(1200,600),(25,25,25)); draw=ImageDraw.Draw(sheet)
for i,(x,y,w,h,area) in enumerate(components[:6]):
    box=(max(0,x-30),max(0,y-30),min(1024,x+w+30),min(1024,y+h+30))
    for j,color in enumerate([(0,0,0,255),(255,255,255,255)]):
        tile=Image.new('RGBA',(1024,1024),color); tile.alpha_composite(Image.fromarray(hall)); crop=tile.crop(box).convert('RGB')
        crop.thumbnail((190,240)); sheet.paste(crop,(i*200,j*300+30)); draw.text((i*200,j*300+3),str((x,y,w,h,area)),fill='white')
sheet.save(OUT/'hall-pink-native-crops.png')
contract=load(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json'); report=load(ROOT/'qa/recovery-v3-20261003/report.json'); reg=report['hall']['registration']
yy,xx=np.where(hall[:,:,3]>16); cx,cy=reg['centroid']; s=reg['footprintScale']; dx,dy=reg['destination']
truebounds=[float(dx+s*(xx.min()-cx)),float(dy+s*(yy.min()-cy)),float(dx+s*(xx.max()-cx)),float(dy+s*(yy.max()-cy))]
sizes={}
iconsheet=Image.new('RGB',(600,180),(30,30,30)); draw=ImageDraw.Draw(iconsheet)
for i,name in enumerate(['food','wood','stone','gold']):
    p=ROOT/f'assets/delivery/stone-starter-20261003/derivatives/{"v3" if name=="gold" else "v2"}/resource-{name}.png'; im=Image.open(p).convert('RGBA'); a=np.array(im); iy,ix=np.where(a[:,:,3]>16); bw,bh=int(ix.max()-ix.min()+1),int(iy.max()-iy.min()+1)
    sizes[name]={'sourceSize':list(im.size),'subjectBBoxSize':[bw,bh],'subjectMaxDimensionIn18pxCSSBox':18*max(bw,bh)/max(im.size)}
    draw.text((i*150,5),name,fill='white')
    for j,size in enumerate([18,36]):
        icon=im.resize((size,size),Image.Resampling.LANCZOS)
        for k,c in enumerate([(12,16,20,255),(255,255,255,255),(110,132,104,255)]):
            tile=Image.new('RGBA',(size+8,size+8),c);tile.alpha_composite(icon,(4,4));iconsheet.paste(tile.convert('RGB'),(i*150+k*45,j*65+25))
iconsheet.save(OUT/'actual-uncropped-ui-boxes.png')
refs=[]
for p in [ROOT/'docs/plan/image-production/guides/kingdom.png',ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/02-kingdom-day1.jpg',ROOT/'docs/plan/references/visual-targets/15_starter_kingdom_day1.jpg']:
    refs.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
testnames={}
for p in (ROOT/'tests').glob('*.mjs'):testnames[p.name]=re.findall(r"test\('([^']+)'",p.read_text(encoding='utf-8'))
out={'hallPinkPixelsDiagnosticOnly':int(pink.sum()),'hallPinkComponents':components,'trueScaleBoundsUsingExecutorContactHeuristic':truebounds,'footprintScale':s,'currentScale':reg['scale'],'uiSubjectSizes':sizes,'referenceHashes':refs,'testDeclarations':testnames,'testCount':sum(map(len,testnames.values()))}
(OUT/'detail-checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8'); print(json.dumps(out))
