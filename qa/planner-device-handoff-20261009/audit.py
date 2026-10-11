"""Read-only verification; outputs belong exclusively to this dated audit."""
from pathlib import Path
import json, hashlib, os, re, subprocess, collections, datetime, ctypes, zipfile
from PIL import Image
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()
def write(n,x): (OUT/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
if __name__=='__main__':
    write('git-before.json',{'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'remotes':git('remote','-v'),'status':git('status','--porcelain=v1'),'tracked':git('ls-files').splitlines()})
    files=[]; groups=collections.defaultdict(lambda:{'files':0,'bytes':0,'allocatedBytes':0}); snap={}; links=[]
    comp=ctypes.windll.kernel32.GetCompressedFileSizeW; comp.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)];comp.restype=ctypes.c_ulong
    for base,dirs,names in os.walk(ROOT):
        dirs[:]=[d for d in dirs if not (Path(base)/d).is_symlink()]
        for name in names:
            p=Path(base)/name;rel=p.relative_to(ROOT).as_posix();s=p.stat();hi=ctypes.c_ulong();lo=comp(str(p),ctypes.byref(hi));alloc=(hi.value<<32)|lo
            g=groups[rel.split('/')[0]];g['files']+=1;g['bytes']+=s.st_size;g['allocatedBytes']+=alloc
            if s.st_nlink>1: links.append({'path':rel,'links':s.st_nlink})
            files.append({'path':rel,'bytes':s.st_size,'mtimeNs':s.st_mtime_ns})
            if rel.startswith(('assets/','src/','tests/','scripts/','docs/','qa/','design-preview/','android/')) and not rel.startswith(('qa/planner-device-handoff-20261009/','android/app/build/','android/.gradle/','android/app/src/main/assets/')) and not rel.endswith(('.pyc',)):
                snap[rel]={'sha256':sha(p),'bytes':s.st_size}
    write('inventory.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':dict(groups),'files':files,'hardlinks':links})
    write('protected-before.json',snap)
    print('Snapshot',len(snap),'files; groups',dict(groups),flush=True)
    # Read every path in the documented reading order; retain bounded semantic extracts.
    names=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
    rd=(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig')
    for name in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md']:
        names.append('docs/plan/'+name)
    for target in re.findall(r'\]\(([^)#]+)\)',rd):
        p=(ROOT/'docs/plan'/target).resolve()
        if p.is_file() and p.suffix in ['.md','.txt','.json'] and p.is_relative_to(ROOT):names.append(p.relative_to(ROOT).as_posix())
    reading=[]
    for n in sorted(set(names)):
        p=ROOT/n
        if not p.exists():reading.append({'path':n,'missing':True});continue
        t=p.read_text(encoding='utf-8-sig');x={'path':n,'sha256':sha(p),'chars':len(t)}
        if p.suffix=='.json':
            j=json.loads(t);x['keysOrLength']=list(j)[:30] if isinstance(j,dict) else len(j)
        else:x['headings']=re.findall(r'^#{1,3} .*$',t,re.M);x['latestExcerpt']=t[:2200]
        reading.append(x)
    write('reading.json',reading)
    results={}; cache={}
    def check(ref):
        n=ref.get('path');p=ROOT/n if n else None
        x={'path':n,'exists':bool(p and p.is_file())}
        if not x['exists']:return x
        x['sha256']=snap.get(n,{}).get('sha256') or sha(p);x['bytes']=p.stat().st_size
        x['hashPass']=not ref.get('sha256') or ref['sha256']==x['sha256'];x['bytesPass']=ref.get('bytes') is None or ref['bytes']==x['bytes']
        if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp']:
            if n not in cache:
                with Image.open(p) as im:
                    im.load();a=np.array(im.convert('RGBA'));visible=a[:,:,3]>16
                    ys,xs=np.where(visible)
                    cache[n]={'width':im.width,'height':im.height,'mode':im.mode,'alphaBBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'visiblePixels':int(visible.sum()),'magentaPixels':int((visible&(a[:,:,0]>180)&(a[:,:,2]>150)&(a[:,:,1]<120)).sum()),'greenPixels':int((visible&(a[:,:,1]>a[:,:,0].astype(int)*1.4)&(a[:,:,1]>a[:,:,2].astype(int)*1.4)&(a[:,:,1]>90)).sum())}
            x.update(cache[n]);dim=ref.get('dimensions');x['dimensionsPass']=not dim or ([x['width'],x['height']]==([dim.get('width'),dim.get('height')] if isinstance(dim,dict) else dim))
        return x
    for name in ['IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json','ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json','ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json']:
        data=read('docs/plan/'+name);refs=[]
        def visit(v):
            if isinstance(v,dict):
                if isinstance(v.get('path'),str) and v['path'].startswith(('assets/','qa/')):refs.append(check(v))
                for k,item in v.items():visit(item)
            elif isinstance(v,list):
                for item in v:visit(item)
        visit(data)
        rows=data.get('rows',data.get('assets',[]));results[name]={'rows':len(rows),'statusCounts':dict(collections.Counter(r.get('status','NONE') for r in rows)),'references':refs,'missing':[r['path'] for r in refs if not r['exists']],'mismatch':[r for r in refs if any(r.get(k) is False for k in ['hashPass','bytesPass','dimensionsPass'])]}
        print(name,len(refs),'refs; missing',len(results[name]['missing']),'mismatch',len(results[name]['mismatch']),flush=True)
    write('interface-checks.json',results)
    rows=read('qa/image-unified-reserve-20261009/diagnostics/scenes.json')
    write('scope.json',{'unifiedCheckpoint':read('qa/image-unified-reserve-20261009/checkpoint.json'),'scenes':{'rows':len(rows),'spatial':dict(collections.Counter(r.get('gates',{}).get('spatial','UNVERIFIED') for r in rows))},'budgetRelease':read('docs/plan/image-production/budget-ledger.json').get('ownerReserveRelease20261009')})
    ziprows=[]
    with zipfile.ZipFile(ROOT/'assets.zip') as z:
        for i in z.infolist():
            if i.is_dir():continue
            n=i.filename.replace('\\','/');local=n if n.startswith('assets/') else 'assets/'+n
            ziprows.append({'entry':n,'path':local,'bytes':i.file_size,'crc':i.CRC,'currentBytes':snap.get(local,{}).get('bytes')})
    write('existing-archive-inventory.json',ziprows)
    print('Archive entries',len(ziprows),'; first',ziprows[:2],flush=True)
