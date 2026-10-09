from audit import *
import base64, io
from PIL import ImageDraw
from scipy import ndimage
def rgba(n):
    with Image.open(ROOT/n) as im:return np.array(im.convert('RGBA'))
def ref(n):return {'path':n,'sha256':sha(ROOT/n),'bytes':(ROOT/n).stat().st_size}
outputs=[]; sheet=Image.new('RGB',(1400,460),'#202020');draw=ImageDraw.Draw(sheet)
for i,p in enumerate(sorted((ROOT/'assets/derivatives/image-unified-reserve-20261009/actors/bodies').glob('*.png'))):
    a=rgba(p.relative_to(ROOT));v=a[:,:,3]>16
    white=v&(a[:,:,:3].min(axis=2)>210)&(a[:,:,:3].max(axis=2)-a[:,:,:3].min(axis=2)<18)
    n=p.name;source=ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS/natives'/n
    s=rgba(source.relative_to(ROOT))
    rgbdiff=int((v&np.any(a[:,:,:3]!=s[:,:,:3],axis=2)).sum())
    lab,count=ndimage.label(v);sizes=np.bincount(lab.ravel());sizes[0]=0
    outputs.append({**ref(p.relative_to(ROOT).as_posix()),'visibleRGBDifferencesFromNative':rgbdiff,'visibleNearWhitePixels':int(white.sum()),'components':count,'largestComponents':sorted(sizes.tolist(),reverse=True)[:8]})
    im=Image.fromarray(a);im.thumbnail((195,410));sheet.paste(im,(i*200,30),im);draw.text((i*200+3,5),n.replace('class-','').replace('-standing-body.png',''),fill='white')
sheet.save(OUT/'current-bodies.jpg')
write('body-pixel-checks.json',outputs)
data=json.loads((ROOT/'qa/image-unified-reserve-20261009/diagnostics/plates.json').read_text());checks=[]
for row in data:
    output=row.get('output',{}).get('path')
    if not output or not (ROOT/output).exists():continue
    a=rgba(output);s=rgba(row['source']);v=a[:,:,3]>16
    checks.append({'id':row['id'],'path':output,'hashMatchesDiagnostic':sha(ROOT/output)==row['output'].get('sha256'),'dimensionsMatch':a.shape==s.shape,'visibleRGBDifferences':int((v&np.any(a[:,:,:3]!=s[:,:,:3],axis=2)).sum()) if a.shape==s.shape else None,'visibleMagenta':int((v&(a[:,:,0]>180)&(a[:,:,2]>150)&(a[:,:,1]<120)).sum())})
write('plate-pixel-checks.json',checks)
transforms=[]
for p in (ROOT/'qa/image-unified-reserve-20261009/recipes').glob('*.json'):
    row=json.loads(p.read_text());roi=row.get('roi');t=row.get('sourceToOutput')
    if roi is not None and t is not None:transforms.append({'id':row['id'],'roi':roi,'transform':t,'cropTranslationPass':t==[1,0,0,1,-roi[0],-roi[1]]})
write('crop-transform-checks.json',transforms)
wire=ROOT/'qa/image-unified-reserve-20261009/vertex-coordinator/healer-class-standing-body/request_body.json';parts=[]
def collect(v):
    if isinstance(v,dict):
        x=v.get('inlineData',v.get('inline_data'))
        if x and str(x.get('mimeType',x.get('mime_type',''))).startswith('image/'):
            b=base64.b64decode(x['data'],validate=True)
            with Image.open(io.BytesIO(b)) as im:im.load();size=list(im.size)
            parts.append({'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'size':size})
        for val in v.values():collect(val)
    elif isinstance(v,list):
        for val in v:collect(val)
collect(json.loads(wire.read_text()));write('healer-wire-check.json',{'wire':ref(wire.relative_to(ROOT).as_posix()),'parts':parts,'inlineImageCount':len(parts),'providerNotQueried':True})
raw=[];native_paths=[*(ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts').rglob('*.png'),*(ROOT/'assets/derivatives/image-vertex-repair-20261009/environment/native').glob('*.png')];natives={sha(p):p.relative_to(ROOT).as_posix() for p in native_paths}
for p in (ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/attempts').rglob('response.json'):
    parts.clear();collect(json.loads(p.read_text()));raw.append({'raw':ref(p.relative_to(ROOT).as_posix()),'images':[dict(x,native=natives.get(x['sha256'])) for x in parts]})
write('raw-native-checks.json',raw)
scenes=read('qa/image-unified-reserve-20261009/diagnostics/scenes.json');mode=read('src/data/mode-scenes.json')
write('scene-source-resolution.json',{'producerMissing':[r['id'] for r in scenes if r.get('blockedBy')],'runtimeCatalog':mode,'catalogSourcesExist':{key:[{'path':p,'exists':(ROOT/p).is_file()} for p in mode[key]] for key in ['adventure','tactical','defense']}})
closure=read('qa/planner-device-handoff-20261009/dist-closure.json');apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk';mismatch=[];checked=0
with zipfile.ZipFile(apk) as z:
    crc=z.testzip()
    for p in (OUT/'static-package').rglob('*'):
        if p.is_file():
            relative=p.relative_to(OUT/'static-package').as_posix();key='assets/www/'+relative
            try:b=z.read(key)
            except KeyError:mismatch.append({'path':relative,'reason':'MISSING'});continue
            checked+=1
            if hashlib.sha256(b).hexdigest()!=sha(p):mismatch.append({'path':relative,'reason':'HASH'})
    apkmanifest=z.read('AndroidManifest.xml')
write('package-checks.json',{'closure':len(closure['assets']),'missing':closure['missing'],'networkReferences':closure['escaping'],'apk':ref(apk.relative_to(ROOT).as_posix()),'apkCRCError':crc,'checkedWebFiles':checked,'webMismatches':mismatch,'packagedUsesPermissionMarkers':apkmanifest.count('uses-permission'.encode('utf-16le')),'manifestBinaryScanOnly':True,'device':'STOPPED','nativeRebuild':'NOT_RUN'})
print('delivery checks: bodies',len(outputs),'plates',len(checks),'transforms',len(transforms),'raw',len(raw),'APK',checked,'mismatches',len(mismatch),flush=True)
