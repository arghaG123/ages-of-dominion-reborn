"""Read-only package/pixel evidence; writes only a small diagnostic JSON."""
import hashlib,json,zipfile
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[2]
apk=R/'android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
report={'package':{'path':str(apk.relative_to(R)),'bytes':apk.stat().st_size,'sha256':sha(apk)},'sourceParity':[]}
with zipfile.ZipFile(apk) as z:
    for rel in ['src/client/main.js','src/client/hero-room.js','src/client/game.css','src/data/plate-overrides-20261007.json']:
        current=(R/rel).read_bytes()
        packed=z.read('assets/www/'+rel)
        report['sourceParity'].append({'file':rel,'match':current==packed,'sourceSHA256':hashlib.sha256(current).hexdigest(),'apkSHA256':hashlib.sha256(packed).hexdigest()})
p=R/'assets/derivatives/image-repair-20261011/actors/plates/tower-industrial-support.png'
im=Image.open(p).convert('RGBA')
n=0
for r,g,b,a in im.getdata():
    if a>=200 and r>200 and b>200 and g<80:n+=1
report['supportMatte']={'file':str(p.relative_to(R)),'opaqueMagentaPixels':n,'samples':{str(xy):im.getpixel(xy) for xy in [(0,0),(50,50),(450,250),(470,800)]},'limitation':'Sampled exterior alpha is zero. Magenta counts include intentional violet FX and do not prove a remaining floor or semantic matte failure. Full composite/mask review still needed.'}
(R/'qa/planner-blocker-solutions-20261011/package-matte.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
