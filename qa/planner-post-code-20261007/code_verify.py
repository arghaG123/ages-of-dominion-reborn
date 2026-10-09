"""Independent read-only Code/consumer/package audit; writes planner QA only."""
import pathlib,json,hashlib,zipfile,collections,re,sys
from PIL import Image,ImageDraw
import numpy as np
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
snapshot=read('qa/planner-post-code-20261007/input-hashes.json') if (Q/'input-hashes.json').exists() else {}
def record(p):
 p=pathlib.Path(p);p=p if p.is_absolute() else R/p
 if p.is_file():snapshot[p.relative_to(R).as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
for p in (R/'assets/runtime-code-20261007').rglob('*'):
 if p.is_file():record(p)
for p in (R/'qa/code-whole-build-20261007').rglob('*'):
 if p.is_file() and 'chrome-profile' not in p.parts:record(p)
cat=read('src/data/consumer-catalog-20261007.json'); rows=cat['assets'];checks=[];pixel=[]
for row in rows:
 c={'id':row['id'],'runtime':row['gates']['runtime'],'use':row['use'],'files':[]}
 for prefix in ('source','output'):
  path=row.get(prefix+'Path');h=row.get(prefix+'Sha256')
  if path:
   p=R/path;record(p);d={'kind':prefix,'path':path,'exists':p.is_file(),'hashMatch':p.is_file() and sha(p)==h}
   if p.is_file() and prefix=='output':
    with Image.open(p) as im:
     im.load();d['dimensions']=list(im.size);d['dimensionMatch']=row.get('dimensions')=={'width':im.width,'height':im.height}
   c['files'].append(d)
 checks.append(c)
 if row.get('outputPath') and (R/row['outputPath']).is_file():
  with Image.open(R/row['outputPath']) as im:a=np.asarray(im.convert('RGBA'))
  rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3];opaque=alpha>128
  m=opaque&(rgb[:,:,0]>150)&(rgb[:,:,2]>120)&(rgb[:,:,1]<rgb[:,:,0]*.65)&(rgb[:,:,1]<rgb[:,:,2]*.75)
  pixel.append({'id':row['id'],'path':row['outputPath'],'alphaOpaqueFraction':float(opaque.mean()),'magentaCandidateVisiblePixels':int(m.sum()),'note':'Diagnostic color count, not semantic PASS/FAIL.'})
repairs=read('qa/code-whole-build-20261007/pixel-report.json')['repairs'];panels=[];rmetrics=[]
for row in repairs:
 if not row.get('outputPath'):continue
 src=Image.open(R/row['sourcePath']).convert('RGBA');out=Image.open(R/row['outputPath']).convert('RGBA')
 x,y=row['cropOffset'];crop=src.crop((x,y,x+out.width,y+out.height));oa=np.asarray(out);ca=np.asarray(crop)
 rgbExact=bool(np.array_equal(oa[:,:,:3],ca[:,:,:3])); opaque=oa[:,:,3]>128
 rmetrics.append({'id':row['id'],'sourceHashPass':sha(R/row['sourcePath'])==row['actualSourceSha256'],'outputHashPass':sha(R/row['outputPath'])==row['outputSha256'],'dimensionsPass':list(out.size)==[row['dimensions']['width'],row['dimensions']['height']],'opaqueFraction':float(opaque.mean()),'sourceRGBExactlyRetained':rgbExact,'transformPass':row['sourceToOutput']==[1,0,0,1,-x,-y],'scope':'RGB crop identity and visual subject inspection; no arbitrary animation claim.'})
 for label,im in [('source',src),('Code matte',out)]:
  bg=Image.new('RGB',(360,400),(64,64,70));im.thumbnail((350,360));bg.paste(im,((360-im.width)//2,32),im);ImageDraw.Draw(bg).text((8,8),row['id']+' '+label,fill='white');panels.append(bg)
sheet=Image.new('RGB',(720,400*len(rmetrics)),(40,40,40))
for i,im in enumerate(panels):sheet.paste(im,((i%2)*360,(i//2)*400))
sheet.save(Q/'code-repaired-troops.jpg')
closure=read('qa/recovery-executor-20261003/dist-closure.json');apkpath=R/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
pkg={'claimedClosure':closure['files'],'checkedAssets':0,'errors':[],'webSourceMismatches':[],'crc':None,'apk':None}
if apkpath.is_file():
 pkg['apk']={'path':apkpath.relative_to(R).as_posix(),'bytes':apkpath.stat().st_size,'sha256':sha(apkpath)}
 with zipfile.ZipFile(apkpath) as z:
  for item in closure['assets']:
   rel=item['file'];digests={}
   for prefix in ('','dist/','android/app/src/main/assets/www/'):
    p=R/(prefix+rel);digests[prefix or 'source']=sha(p) if p.is_file() else None
   try:digests['APK']=hashlib.sha256(z.read('assets/www/'+rel)).hexdigest()
   except KeyError:digests['APK']=None
   if any(v!=item['sha256'] for v in digests.values()):pkg['errors'].append({'path':rel,'expected':item['sha256'],'actual':digests})
   pkg['checkedAssets']+=1
  for p in [R/'index.html',*(R/'src').rglob('*')]:
   if not p.is_file():continue
   rel=p.relative_to(R).as_posix();h=sha(p)
   vals={prefix:sha(R/(prefix+rel)) if (R/(prefix+rel)).is_file() else None for prefix in ('dist/','android/app/src/main/assets/www/')}
   try:vals['APK']=hashlib.sha256(z.read('assets/www/'+rel)).hexdigest()
   except KeyError:vals['APK']=None
   if any(v!=h for v in vals.values()):pkg['webSourceMismatches'].append({'path':rel,'actual':vals})
  pkg['crc']=z.testzip();pkg['manifestPresent']='AndroidManifest.xml' in z.namelist()
old=read('qa/planner-final-images-20261007/input-hashes.json');changes=[]
for p,v in old.items():
 f=R/p
 if not f.exists() or sha(f)!=v['sha256']:changes.append({'path':p,'exists':f.exists(),'current':sha(f) if f.exists() else None,'prior':v['sha256']})
save('code-consumer-checks.json',{'rows':len(rows),'runtimeCounts':dict(collections.Counter(r['gates']['runtime'] for r in rows)),'runtimePassingButNotNecessarilyConsumed':[r['id'] for r in rows if r['gates']['runtime']=='PASS'],'checks':checks,'repairs':rmetrics,'priorSnapshotChanges':changes})
save('pixel-metrics-current.json',pixel);save('package-checks.json',pkg);save('input-hashes.json',snapshot)
print(json.dumps({'consumerRows':len(rows),'fileErrors':[c['id'] for c in checks if any(not f['exists'] or not f['hashMatch'] or f.get('dimensionMatch') is False for f in c['files'])],'repairs':rmetrics,'package':{k:v for k,v in pkg.items() if k!='errors'},'closureErrors':len(pkg['errors']),'snapshotChanges':len(changes)},indent=2))
