"""Read-only delivery audit; writes only this planner QA directory."""
import hashlib
import json
from pathlib import Path
import zipfile
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p):
    return hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
def read(p):
    return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))

interface = read('docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json')
measure = read('qa/image-local-continuation-20261005/measurements.json')
refs = []
def walk(value, location):
    if isinstance(value, list):
        for i, x in enumerate(value): walk(x, f'{location}[{i}]')
    elif isinstance(value, dict):
        for field, digest in [('path','sha256'), ('source','sourceSha256'), ('parent','parentSha256'), ('child','childSha256'), ('evidence','sha256'), ('derivative','sha256')]:
            if isinstance(value.get(field), str) and isinstance(value.get(digest), str):
                refs.append((location, value[field], value[digest]))
        for k,v in value.items(): walk(v, f'{location}.{k}')
walk(interface, 'interface')
walk(read('qa/image-local-continuation-20261005/input-hashes.json'), 'inputHashes')
walk(read('qa/image-local-continuation-20261005/class-semantics.json'), 'classSemantics')
walk(read('qa/image-local-continuation-20261005/scene-survey-summary.json'), 'sceneSurvey')
results=[]
seen=set()
for loc, rel, expected in refs:
    if (rel,expected) in seen: continue
    seen.add((rel,expected)); p=ROOT/rel
    row={'path':rel,'exists':p.is_file(),'expected':expected,'record':loc}
    if p.is_file():
        row['actual']=sha(p); row['hashMatch']=row['actual']==expected
        if p.suffix.lower()=='.png':
            try:
                with Image.open(p) as im: im.load(); row['dimensions']=list(im.size)
                row['decode']=True
            except Exception as e: row['decode']=False; row['error']=str(e)
    results.append(row)

# Independently validate the claimed boot cleanup against its unchanged source pixels.
src=np.array(Image.open(ROOT/'assets/derivatives/rigs/v6/healer/boot.png').convert('RGBA'))
dst=np.array(Image.open(ROOT/'assets/derivatives/rigs/v7/healer/boot.png').convert('RGBA'))
labels,n=ndimage.label(src[:,:,3]>16)
counts=np.bincount(labels.ravel()); counts[0]=0; main=int(counts.argmax())
ys,xs=np.where(labels==main); box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
crop=src[box[1]:box[3],box[0]:box[2]]
mask=(labels==main)[box[1]:box[3],box[0]:box[2]]
boot={'sourceMainAlpha16Pixels':int(mask.sum()),'mainBounds':box,'dimensionsMatch':crop.shape==dst.shape,'mainRGBAUnchanged':bool(np.array_equal(crop[mask],dst[mask])),'outputAlpha16Pixels':int((dst[:,:,3]>16).sum())}

apk=ROOT/'android/app/build/outputs/apk/release/app-release-unsigned.apk'
package={'exists':apk.is_file()}
if apk.is_file():
    package.update(bytes=apk.stat().st_size,sha256=sha(apk))
    files=[p for p in (ROOT/'dist').rglob('*') if p.is_file()]
    rows=[]
    with zipfile.ZipFile(apk) as z:
        package['zipCRCFailure']=z.testzip()
        for p in files:
            rel=p.relative_to(ROOT/'dist').as_posix(); h=sha(p)
            native=ROOT/'android/app/src/main/assets/www'/rel; source=ROOT/rel
            entry='assets/www/'+rel
            rows.append({'path':rel,'dist':h,'nativeMatch':native.is_file() and sha(native)==h,'apkMatch':entry in z.namelist() and hashlib.sha256(z.read(entry)).hexdigest()==h,'sourceExists':source.is_file(),'sourceMatch':source.is_file() and sha(source)==h})
        package['apkWebEntries']=len([x for x in z.namelist() if x.startswith('assets/www/') and not x.endswith('/')])
    package['files']=len(rows); package['mismatches']=[r for r in rows if not r['nativeMatch'] or not r['apkMatch'] or (r['sourceExists'] and not r['sourceMatch'])]
    (OUT/'package-files.json').write_text(json.dumps(rows,indent=2))

report={'bindingsChecked':len(results),'bindingFailures':[r for r in results if not r.get('hashMatch') or r.get('decode') is False],'readyRows':len(interface['readySubset']),'inputHashesCount':read('qa/image-local-continuation-20261005/input-hashes.json')['present'],'sceneRows':len(measure['scenes']),'boot':boot,'package':package}
(OUT/'artifact-bindings.json').write_text(json.dumps(results,indent=2))
(OUT/'artifact-summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

