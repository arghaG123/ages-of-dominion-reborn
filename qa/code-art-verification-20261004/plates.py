"""QA viewing plates only; original and derivative production files are untouched."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
rows=json.loads((out/'snapshot.json').read_text())['highres']['outputs']
plate=Image.new('RGB',(1200,((len(rows)+2)//3)*255),'#152128');draw=ImageDraw.Draw(plate)
for i,row in enumerate(rows):
    x=(i%3)*400;y=(i//3)*255
    with Image.open(root/row['file']) as im:
        im.thumbnail((390,220));plate.paste(im,(x,y+25))
    draw.text((x+4,y+4),row['id'],fill='white')
plate.save(out/'highres-overview.jpg',quality=92)
for ident in ['defense-terrain','tactical-terrain-ruins','defense-terrain-hills']:
    row=next(r for r in rows if r['id']==ident);pack=(root/row['file']).parent
    p=Image.new('RGB',(1376,768*2),'#152128')
    with Image.open(pack/'guide.png') as im:p.paste(im.resize((1376,768)),(0,0))
    with Image.open(pack/'output.png') as im:p.paste(im.resize((1376,768)),(0,768))
    p.save(out/(ident+'-guide-output.png'))
