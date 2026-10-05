from pathlib import Path
import json, hashlib, re
from PIL import Image,ImageDraw
ROOT=Path('C:/dev/ages-of-dominion-reborn'); OUT=ROOT/'qa/kingdom-image-progress-20261004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=['assets/production/production-03-20261003/images/01-kingdom-terrain-stone.png','assets/production/production-03-20261003/images/02-kingdom-terrain-medieval.png','assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png','qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v5-guide.png']
sheet=Image.new('RGB',(1376,820),(30,30,30)); d=ImageDraw.Draw(sheet); rows=[]
for i,s in enumerate(paths):
 p=ROOT/s; im=Image.open(p);im.load(); sheet.paste(im.convert('RGB').resize((688,384)),((i%2)*688,(i//2)*410+26));d.text(((i%2)*688+5,(i//2)*410+6),p.name,fill='white');rows.append({'file':s,'sha256':sha(p),'dimensions':list(im.size)})
sheet.save(OUT/'alternates-and-v5.jpg',quality=92)
report=(ROOT/'docs/plan/FIRST-32-4K-TACTICAL-RETRY-REPORT-2026-10-04.md').read_text(encoding='utf-8-sig')
outputs=json.loads((OUT/'outputs.json').read_text())
check=[]
for o in outputs:
 if 'run-05' in o['run']:check.append({'id':o['id'],'actualSHA256':o['sha256'],'actualHashAppearsInReport':o['sha256'] in report,'journalMatches':o['hashMatch']})
request=(ROOT/'assets/high-res/interactive-4k-first32-20261003/run-05-tactical-retry-20261004-015857/packs/tactical-terrain/request_meta.json').read_text(encoding='utf-8-sig')
(OUT/'extra-checks.json').write_text(json.dumps({'alternates':rows,'run5ProseHashChecks':check,'run5Authority':'Producer report quotes First try 2 tactical terrins; not direct authorization evidence in this planner chat','requestMetaFields':list(json.loads(request).keys())},indent=2),encoding='utf-8')
print(json.dumps(check,indent=2))
ages=('stone','bronze','iron','medieval','gunpowder','industrial','modern','future')
hallrows=[]; sheet=Image.new('RGB',(1536,820),(30,30,30));d=ImageDraw.Draw(sheet)
for i,age in enumerate(ages):
 p=ROOT/f'assets/production/production-01-20261003/images/{i+9:02d}-townhall-{age}.png';im=Image.open(p);im.load()
 hallrows.append({'id':'townhall-'+age,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'dimensions':list(im.size),'physicalRegistration':'UNVERIFIED'})
 thumb=im.convert('RGB');thumb.thumbnail((384,384));sheet.paste(thumb,((i%4)*384,(i//4)*410+26));d.text(((i%4)*384+5,(i//4)*410+6),age,fill='white')
sheet.save(OUT/'hall-age-sources.jpg',quality=90)
(OUT/'hall-age-sources.json').write_text(json.dumps(hallrows,indent=2),encoding='utf-8')
