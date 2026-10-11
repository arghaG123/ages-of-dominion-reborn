"""Read-only v8 validation. No production helpers imported or executed."""
import hashlib, json, sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def digest(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
v8=read('docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json')
sem=read('qa/image-local-delivery-v8-20261005/class-semantics-v8.json')
scenes=read('qa/image-local-delivery-v9-20261005/scenes.json')
refs={}
def walk(v):
    if isinstance(v,dict):
        for pathkey,hashkey in [('path','sha256'),('source','sourceSha256'),('parent','parentSha256'),('child','childSha256'),('evidence','sha256'),('diagram','diagramSha256'),('derivative','sha256')]:
            if isinstance(v.get(pathkey),str) and isinstance(v.get(hashkey),str): refs[(v[pathkey],v[hashkey])]=True
        for val in v.values(): walk(val)
    elif isinstance(v,list):
        for val in v: walk(val)
for val in [v8,sem,scenes,read('qa/image-local-continuation-20261005/input-hashes.json')]: walk(val)
bindings=[]
for (rel,h) in refs:
    p=ROOT/rel; row={'path':rel,'expected':h,'exists':p.is_file()}
    if p.is_file():
        row['sha256']=digest(p); row['match']=row['sha256']==h
        if p.suffix.lower()=='.png':
            with Image.open(p) as im: im.load(); row['dimensions']=list(im.size); row['decode']=True
    bindings.append(row)
ready=[]; joints=[]
for r in v8['readySubset']:
    if 'path' in r:
        with Image.open(ROOT/r['path']) as im:
            rgba=np.asarray(im.convert('RGBA')); ys,xs=np.where(rgba[:,:,3]>16)
            box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
            ready.append({'id':r['id'],'dimensions':list(im.size),'dimensionsMatch':list(im.size)==r['dimensions'],'alpha16Bounds':box,'boundsMatch':box==r['visibleAlpha16']})
    cf=r.get('coordinateFrames')
    if not cf or not cf.get('parent'): continue
    parent=np.asarray(Image.open(ROOT/cf['parent']).convert('RGBA'))
    child=np.asarray(Image.open(ROOT/cf['child']).convert('RGBA'))
    height,width=cf['canvas']; pivot=cf['sharedPivotCanvas']; pc=cf['cuffParent']; cc=cf['cuffChild']
    shifted=cf.get('childPivotCanvas',pivot); cw=max(pc['width'],cc['width'])
    def warp(arr,cuff,point,angle):
        rad=np.deg2rad(angle); c,s=float(np.cos(rad)),float(np.sin(rad)); x,y=cuff['cx'],cuff['y']; px,py=point
        m=np.array([[c,-s,px-c*x+s*y],[s,c,py-s*x-c*y]],np.float32)
        return cv2.warpAffine(arr,m,(width,height),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    pl=warp(parent,pc,pivot,0)
    for pose in r['poses']:
        cl=warp(child,cc,shifted,pose['angle']); x,y=shifted
        x0,x1=max(0,int(x-cw*2)),min(width,int(x+cw*2)); y0,y1=max(0,int(y-cw)),min(height,int(y+cw))
        overlap=int(((pl[y0:y1,x0:x1,3]>128)&(cl[y0:y1,x0:x1,3]>16)).sum())
        joints.append({'id':r['id'],'angle':pose['angle'],'overlap':overlap,'expected':pose['overlapParent128Child16'],'match':overlap==pose['overlapParent128Child16'],'canvasConvention':'height,width as implemented; not declared in v8'})
contract=read('src/data/implementation-contract.json')
sceneChecks=[]
for s in scenes:
    si=next(x for x in v8['scenes'] if x['id']==s['id'])
    sceneChecks.append({'id':s['id'],'sourceMatch':s['source']==si['source'],'affineMatchesContract':s['legalAffineActive']==contract['geometry'][s['mode']]['worldToSource'],'roadCount':len(s['paintedRoadPolylines']),'walkableCount':len(s['walkablePolygons']),'promoted':s['promoted'],'interfaceRoadsMatch':s['paintedRoadPolylines']==si['paintedRoadPolylines']})
report={'python':sys.version.split()[0],'bindings':len(bindings),'bindingFailures':[x for x in bindings if not x.get('match')],'readyRasterChecks':ready,'jointChecks':joints,'semanticsRows':len(sem),'classChains':len(v8['classChains']),'scenes':sceneChecks,'readySourceGateUnverified':[r['id'] for r in v8['readySubset'] if r['gates']['sourceBinding']['gate']=='UNVERIFIED'],'limits':'Bindings/overlap reproduction do not prove anatomy, full rigs, painted geography, native or owner acceptance.'}
(OUT/'v9-bindings.json').write_text(json.dumps(bindings,indent=2))
(OUT/'v9-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['scenes','readyRasterChecks','jointChecks']},indent=2))
print('joint metric mismatches',len([x for x in joints if not x['match']]))
