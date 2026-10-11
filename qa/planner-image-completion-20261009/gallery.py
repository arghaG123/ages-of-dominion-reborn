import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
def sheet(name,items,w=420,h=300,cols=4):
    out=Image.new('RGB',(w*cols,h*((len(items)+cols-1)//cols)), '#252a32');d=ImageDraw.Draw(out)
    for i,(label,path) in enumerate(items):
        x=(i%cols)*w;y=(i//cols)*h
        d.text((x+8,y+5),label,fill='white')
        try:
            im=Image.open(ROOT/path).convert('RGBA');im.thumbnail((w-16,h-36));bg=Image.new('RGBA',im.size,'#586b68');bg.alpha_composite(im);out.paste(bg.convert('RGB'),(x+(w-im.width)//2,y+28))
        except Exception as e:d.text((x+8,y+30),str(e)[:50],fill='red')
    out.save(QA/name,quality=93)
items=[(p.stem,p.relative_to(ROOT).as_posix()) for p in (ROOT/'assets/derivatives/image-vertex-repair-20261009/environment/native').glob('*.png')]
sheet('kingdom-candidates.jpg',items,w=460,h=300)
items=[(p.stem,p.relative_to(ROOT).as_posix()) for p in (ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS/natives').glob('*.png')]
sheet('actor-native-candidates.jpg',items,w=310,h=390)
j=json.loads((ROOT/'docs/plan/ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json').read_text(encoding='utf-8-sig'))
ids=['troop-stone-ranged','gear-stone-helm','gear-stone-boots','troop-bronze-heavy','troop-medieval-heavy','hero-mount-barded-horse','troop-medieval-ranged','healer-boot','troop-iron-melee','attacker-bronze-runner']
items=[]
for r in j['rows']:
    if r['id'] in ids and r.get('output'):items.append((r['id']+' '+r['status'],r['output']['path']))
sheet('actor-local-results.jpg',items,w=380,h=400)
for p in (ROOT/'qa/image-vertex-repair-20261009/environment/geography/guides').glob('*stone*'):
    print('guide',p.relative_to(ROOT))
print('sheets ready')
