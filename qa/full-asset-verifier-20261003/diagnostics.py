import json,hashlib,base64,collections,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
x=json.loads((OUT/'inventory.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def sheet(rows,prefix,cols=3,cell=(460,340)):
 for page in range((len(rows)+11)//12):
    s=Image.new('RGB',(cols*cell[0],4*cell[1]),'#252525');d=ImageDraw.Draw(s)
    for n,r in enumerate(rows[page*12:(page+1)*12]):
      xx=n%cols*cell[0];yy=n//cols*cell[1]
      with Image.open(ROOT/r['file']) as im:
        im=im.convert('RGBA');im.thumbnail((cell[0]-10,cell[1]-52));s.paste(im,(xx+(cell[0]-im.width)//2,yy),im)
      d.text((xx+4,yy+cell[1]-48),Path(r['file']).name[:45],font=font,fill='white')
      d.text((xx+4,yy+cell[1]-26),r['sha256'][:12]+' '+str(r['size']),font=font,fill='white')
    s.save(OUT/f'{prefix}-{page+1}.jpg',quality=95)
sheet(x['deliveryFiles'],'delivery')
v2=[r for r in x['deliveryFiles'] if '/derivatives/v2/' in r['file']]
# actual-pixel intended-size icons and complete subjects on contrasting grounds
icons=[r for r in v2 if r['file'].split('/')[-1].startswith(('skill-','resource-'))]
s=Image.new('RGB',(1120,len(icons)*140),'#252525');d=ImageDraw.Draw(s)
for row,r in enumerate(icons):
  d.text((5,row*140+5),Path(r['file']).stem,font=font,fill='white')
  with Image.open(ROOT/r['file']) as im:
    for j,bg in enumerate(['#101820','#ffffff','#6e8468']):
      for k,sz in enumerate([18,36,64]):
        xx=240+j*280+k*88;yy=row*140+32
        sample=Image.new('RGB',(sz,sz),bg);scaled=im.convert('RGBA').resize((sz,sz),Image.Resampling.LANCZOS);sample.paste(scaled,(0,0),scaled);s.paste(sample,(xx,yy));d.text((xx,yy+70),str(sz)+'px',font=font,fill='white')
s.save(OUT/'v2-icons-intended-pixels.png')
for r in v2:
  im=Image.open(ROOT/r['file']).convert('RGBA');s=Image.new('RGB',(im.width*3,im.height))
  for n,bg in enumerate(['#000000','#ffffff','#6e8468']):
    sample=Image.new('RGBA',im.size,bg);sample.alpha_composite(im);s.paste(sample.convert('RGB'),(n*im.width,0))
  s.save(OUT/(Path(r['file']).stem+'-v2-full.png'))
# lossless crop diagnostics for objectively suspect newer sources; coordinates remain source-local.
targets={'workshop-stone':(0,700,1024,1024),'farm-bronze':(700,200,1024,850),'quarry-gunpowder':(0,250,1024,950),'lumber-industrial':(0,0,1024,400),'farm-future':(0,100,1024,900),'civilian-transport-modern':(0,0,1024,1024),'troop-stone-ranged':(250,180,820,830),'tower-modern-splash':(150,40,860,680),'attacker-stone-brute':(220,650,850,1000)}
for r in x['sources']:
  if r['id'] in targets:
    with Image.open(ROOT/r['file']) as im:im.crop(targets[r['id']]).save(OUT/(r['id']+'-native-crop.png'))
print('Viewing copies created. No source or delivery files changed.')
