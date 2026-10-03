"""Read-only inputs; writes inventory and diagnostic viewing copies only in QA."""
import hashlib,json,collections,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
rows=[]; batches=[]
prior=read(ROOT/'docs/plan/image-production/VERIFIER-REVIEW-20261003.json')
old={(x['batch'],x['id'],x['sourceSHA256']):x for x in prior['assets']}
for report in sorted((ROOT/'assets/production').glob('*/collection-report.json')):
    b=report.parent.name; c=read(report); m=read(report.parent/'manifest.json')
    items={x['id']:x for x in m['items']}
    start=len(rows)
    for x in sorted(c['outputs'],key=lambda x:items[x['id']]['position']):
        p=ROOT/x['file']; i=items[x['id']]; actual=sha(p)
        with Image.open(p) as im: im.load(); size=list(im.size); mode=im.mode
        historical=old.get((b,x['id'],x['sha256']),{})
        rows.append(dict(batch=b,id=x['id'],position=i['position'],kind=i['kind'],age=i.get('age'),modeRole=i.get('mode'),file=x['file'],sha256=actual,bytes=p.stat().st_size,size=size,imageMode=mode,technical='PASS' if actual==x['sha256'] and size==[x['width'],x['height']] and x['promptSHA256']==i['promptSHA256']==hashlib.sha256(i['prompt'].encode()).hexdigest() else 'FAIL',sourceContentHistorical=historical.get('sourceContentStatus','UNVERIFIED'),historicalClassification=historical.get('classification'),historicalReason=historical.get('reason',historical.get('reasons')),requiredAlpha=x['requiredAlpha'],nativeAlpha='A' in mode,visualScope='overview only; detail/registration/matte unverified',gates=dict(matte='UNVERIFIED' if x['requiredAlpha'] else 'NOT_APPLICABLE',registration='NOT_APPLICABLE' if i['kind'] in ['resource','skill','spell','gear','portrait'] else 'UNVERIFIED',runtime='UNVERIFIED',ownerAcceptance='UNVERIFIED')))
    group=rows[start:]
    sheets=[]
    for page in range(2):
        subset=group[page*15:(page+1)*15]
        sheet=Image.new('RGB',(1500,1800),'#252525'); d=ImageDraw.Draw(sheet)
        for n,r in enumerate(subset):
            x=(n%3)*500;y=(n//3)*360
            with Image.open(ROOT/r['file']) as im:
                im=im.convert('RGB'); im.thumbnail((490,315));sheet.paste(im,(x+(500-im.width)//2,y))
            d.text((x+6,y+318),f"{r['position']:02} {r['id']}",font=font,fill='white')
            d.text((x+6,y+339),r['sha256'][:12],font=font,fill='#bbbbbb')
        f=f'{b}-page{page+1}.jpg';sheet.save(OUT/f,quality=93);sheets.append(f)
    batches.append(dict(batch=b,count=len(group),technicalPass=sum(r['technical']=='PASS' for r in group),roles=dict(collections.Counter(r['kind'] for r in group)),bytes=sum(r['bytes'] for r in group),sheets=sheets))
derivatives=[]
for p in sorted((ROOT/'assets/delivery').rglob('*')):
    if p.is_file() and p.suffix.lower() in ['.png','.jpg','.webp']:
        with Image.open(p) as im: im.load();size=list(im.size);mode=im.mode
        derivatives.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size,size=size,imageMode=mode))
sizes=collections.defaultdict(lambda:dict(count=0,bytes=0))
largest=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts:continue
    rel=p.relative_to(ROOT);cat='/'.join(rel.parts[:2]) if rel.parts[0] in ['assets','qa','docs','design-preview'] else rel.parts[0]
    sizes[cat]['count']+=1;sizes[cat]['bytes']+=p.stat().st_size
    largest.append(dict(file=rel.as_posix(),bytes=p.stat().st_size))
result=dict(scope='all local production collections 01-08 and all delivery raster files; snapshot',batches=batches,attempts=len(rows),distinctIDs=len(set(r['id'] for r in rows)),sources=rows,deliveryFiles=derivatives,sizes=dict(sizes),largest=sorted(largest,key=lambda x:-x['bytes'])[:20])
(OUT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['batches','attempts','distinctIDs','sizes','largest']},indent=2))
