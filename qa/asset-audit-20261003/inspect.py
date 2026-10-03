"""Offline evidence only: preserve sources; contact sheets are viewing aids, not art edits."""
import collections, hashlib, json, math
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('C:/dev/ages-of-dominion-reborn')
OUT = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
def sheet(name, records, width=420, height=330, cols=3):
    canvas = Image.new('RGB',(cols*width, math.ceil(len(records)/cols)*(height+50)), '#20252a')
    draw = ImageDraw.Draw(canvas)
    for n,(label,path) in enumerate(records):
        x,y=(n%cols)*width,(n//cols)*(height+50)
        with Image.open(path) as original:
            im=original.convert('RGB'); im.thumbnail((width-8,height-8))
            canvas.paste(im,(x+(width-im.width)//2,y+(height-im.height)//2))
        draw.text((x+8,y+height+3),label,fill='white',font=font)
    target=OUT/(name+'.jpg'); canvas.save(target,quality=94)
    return str(target.relative_to(ROOT)).replace('\\','/')

def main():
    groups=collections.defaultdict(list); items=[]; batches=[]; protected=[]
    for folder in sorted((ROOT/'assets/production').glob('production-*')):
        m=read(folder/'manifest.json'); lookup={x['id']:x for x in m['items']}
        p=read(folder/'provider-job.json'); l=read(folder/'ledger.json')
        c=read(folder/'collection-report.json') if (folder/'collection-report.json').exists() else {}
        batches.append({'batch':folder.name,'job':p.get('name'),'savedProviderState':p.get('state'), 'savedAt':l.get('checkedAt'), 'outputs':len(c.get('outputs',[])), 'errors':c.get('errors'), 'technicalStatus':c.get('technicalStatus'), 'visualStatus':c.get('visualStatus')})
        for path in folder.iterdir():
            if path.is_file(): protected.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path)})
        for output in sorted(c.get('outputs',[]),key=lambda x:lookup[x['id']]['position']):
            spec=lookup[output['id']]; path=ROOT/output['file']
            with Image.open(path) as im:
                im.load(); size=list(im.size); bands=im.getbands()
            row={**output,'batch':folder.name,'position':spec['position'],'kind':spec['kind'],'mode':spec.get('mode'),'attempt':spec.get('attempt',1),'registration':spec.get('registration'),'actualSize':size,'actualAlpha':'A' in bands,'hashMatch':sha(path)==output['sha256']}
            items.append(row)
            b=folder.name.split('-')[1]
            category=spec['kind']
            if category=='terrain': category=spec.get('mode','terrain')+'-terrain'
            if b=='03' and category in ['building','skill','gear']: category='objects'
            groups[b+'-'+category].append((str(spec['position']).zfill(2)+' '+spec['id'],path))
    sheets={k:sheet(k,v) for k,v in groups.items()}
    refs=ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
    sheets['approved-direction']=sheet('approved-direction',[(p.stem,p) for p in [refs/'03-kingdom-stone.jpg',refs/'06-kingdom-medieval.jpg',refs/'11-adventure-overview.jpg',refs/'15-tactical-action.jpg',refs/'18-defense-wave.jpg',refs/'19-hero-equipment.jpg',refs/'22-forge.jpg',refs/'30-icon-material-board.jpg']],480,300,2)
    for p in [ROOT/'docs/plan/image-production/budget-ledger.json',ROOT/'docs/plan/image-production/active.lock.json',ROOT/'src/client/main.js',ROOT/'scripts/vertex-production.py',ROOT/'scripts/benchmark.py',ROOT/'assets/production/VISUAL-REVIEW-2026-10-03.md']:
        if p.exists(): protected.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p)})
    snapshot={'at':datetime.now(timezone.utc).isoformat(),'batches':batches,'assets':items,'sheets':sheets,'protectedMetadata':protected,'note':'Local saved provider facts only. No provider query. Hash/decoding is technical evidence only.'}
    (OUT/'local-snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'batches':batches,'outputs':len(items),'allHashesMatch':all(x['hashMatch'] for x in items),'alphaRequired':sum(x['requiredAlpha'] for x in items),'sheets':sheets},indent=2))
if __name__=='__main__':main()
