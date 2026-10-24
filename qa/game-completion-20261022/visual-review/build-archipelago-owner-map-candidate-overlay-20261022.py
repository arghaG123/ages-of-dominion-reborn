from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
root = Path.cwd()
world = next(w for w in json.loads((root / 'src/data/adventure-worlds.json').read_text(encoding='utf-8')) if w['id'] == 'archipelago')
source = root / world['file']
output = root / 'qa/game-completion-20261022/visual-review/archipelago-owner-map-candidate-registration-grid-20261022.png'
im = Image.open(source).convert('RGBA')
width, height = im.size
cw, ch = width / 16, height / 10
layer = Image.new('RGBA', im.size, (0,0,0,0))
draw = ImageDraw.Draw(layer, 'RGBA')
font = ImageFont.load_default()
for x,y in world['geometry']['blocked']:
    box=(round(x*cw),round(y*ch),round((x+1)*cw),round((y+1)*ch))
    draw.rectangle(box, fill=(20,75,220,78), outline=(195,225,255,185), width=2)
for x,y in world['geometry']['obstacles']:
    box=(round(x*cw),round(y*ch),round((x+1)*cw),round((y+1)*ch))
    draw.rectangle(box, fill=(240,40,20,135), outline=(255,218,190,245), width=3)
for bridge in world['geometry']['bridges']:
    for x,y in bridge['cells']:
        box=(round(x*cw),round(y*ch),round((x+1)*cw),round((y+1)*ch))
        draw.rectangle(box, fill=(0,230,185,145), outline=(200,255,240,255), width=3)
    x,y,w,h=bridge['rect']; px,py=round(x*cw),round(y*ch)
    draw.text((px+3,py+3),bridge['id'],font=font,fill=(0,20,20,255),stroke_width=2,stroke_fill=(220,255,245,255))
colors={'town':(255,220,0,255),'ruin':(210,90,255,255),'mill':(100,255,100,255),'mine':(255,150,40,255),'dwelling':(100,230,255,255),'shrine':(255,100,210,255)}
for site in world['geometry']['sites']:
    x,y,w,h=site['rect']; box=(round(x*cw),round(y*ch),round((x+w)*cw),round((y+h)*ch)); color=colors[site['id']]
    draw.rectangle(box, outline=color, width=4)
    draw.text((box[0]+3,box[1]+3),site['id'],font=font,fill=(15,10,0,255),stroke_width=2,stroke_fill=(255,255,235,255))
    ax,ay=site['approach']; cx,cy=round((ax+.5)*cw),round((ay+.5)*ch)
    draw.ellipse((cx-7,cy-7,cx+7,cy+7),fill=(255,240,0,240),outline=(0,0,0,255),width=2)
for name,point in world['geometry']['anchors'].items():
    ax,ay=point; cx,cy=round(ax*cw),round(ay*ch)
    if name=='hero': color=(255,255,255,255)
    elif name.startswith('guard'): color=(255,65,65,255)
    else: color=(255,255,255,220)
    draw.ellipse((cx-5,cy-5,cx+5,cy+5),fill=color,outline=(0,0,0,255),width=1)
for x in range(17):
    px=round(x*cw); draw.line((px,0,px,height),fill=(255,255,255,90),width=2)
for y in range(11):
    py=round(y*ch); draw.line((0,py,width,py),fill=(255,255,255,90),width=2)
for y in range(10):
    for x in range(16):
        label=f'{x},{y}'; cx,cy=round((x+.5)*cw),round((y+.5)*ch)
        bbox=draw.textbbox((0,0),label,font=font); tw,th=bbox[2]-bbox[0],bbox[3]-bbox[1]
        draw.rectangle((cx-tw//2-2,cy-th//2-2,cx+tw//2+2,cy+th//2+2),fill=(0,0,0,145))
        draw.text((cx-tw//2,cy-th//2),label,font=font,fill=(255,255,255,245))
Image.alpha_composite(im,layer).convert('RGB').save(output,optimize=True)
print(output.relative_to(root))