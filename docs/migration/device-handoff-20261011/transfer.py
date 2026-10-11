"""Create today's asset-only delta, verify it, or restore it without overwrites."""
from pathlib import Path
import argparse, hashlib, json, os, zipfile

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()
def safe(root, rel):
    parts=Path(rel).parts
    if Path(rel).is_absolute() or '..' in parts or ':' in rel or '\\' in rel: raise ValueError('Unsafe path: '+rel)
    p=root/rel
    if not p.resolve().is_relative_to(root.resolve()): raise ValueError('Path escapes root: '+rel)
    for q in [p,*p.parents]:
        if q==root.parent: break
        if q.is_symlink() or q.is_junction(): raise ValueError('Link/reparse destination: '+str(q))
    return p
def verify_zip(archive, manifest):
    if sha(archive)!=manifest['zip']['sha256']: raise ValueError('ZIP hash mismatch')
    with zipfile.ZipFile(archive) as z:
        expected={r['path'] for r in manifest['files']}|{'TRANSFER-MANIFEST.json','RESTORE.txt'}
        if set(z.namelist())!=expected or len(z.namelist())!=len(expected): raise ValueError('Unexpected or duplicate ZIP entries')
        embedded=json.loads(z.read('TRANSFER-MANIFEST.json'))
        if embedded['files']!=manifest['files']: raise ValueError('Embedded manifest mismatch')
        for r in manifest['files']:
            b=z.read(r['path'])
            if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']: raise ValueError('Bad ZIP member: '+r['path'])
    return {'status':'PASS','assetEntries':len(manifest['files']),'zipEntries':len(expected),'zipSHA256':manifest['zip']['sha256'],'restoreOnNewDevice':'UNVERIFIED'}
def build(refresh=False):
    inventory=json.loads((ROOT/'qa/planner-device-handoff-20261011/asset-inventory.json').read_text())
    namespaces=('assets/derivatives/image-complete-20261011/','assets/derivatives/image-repair-20261011/')
    rows=[r for r in inventory['files'] if r['path'].startswith(namespaces) and r['difference']=='NEW_BYTES']
    # Paths identify today's derivative namespaces; content is compared to the evidenced baseline.
    interface=json.loads((ROOT/'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json').read_text())
    bindings={(r.get('output') or {}).get('path'):r for r in interface.get('rows',[])}
    plates=json.loads((ROOT/'qa/image-complete-20261011/plate-despill.json').read_text())['rows']
    repairs=json.loads((ROOT/'qa/image-repair-20261011/protected-matte.json').read_text())
    if isinstance(repairs,dict): repairs=repairs.get('rows',repairs.get('repairs',list(repairs.values())))
    plate_bindings={r.get('file'):r for r in plates+repairs}
    files=[]
    for r in rows:
        p=safe(ROOT,r['path'])
        if sha(p)!=r['sha256'] or p.stat().st_size!=r['bytes']: raise ValueError('Source changed during audit')
        binding=bindings.get(r['path'],{})
        sources=binding.get('sources',[])
        plate=plate_bindings.get(r['path'],{})
        if not sources and plate.get('source'):
            src=safe(ROOT,plate['source'])
            sources=[{'path':plate['source'],'sha256':sha(src),'bytes':src.stat().st_size}]
        files.append({k:r[k] for k in ['path','bytes','sha256','role','difference']}|{'sources':sources,'contractId':binding.get('id',plate.get('id')),'acceptance':binding.get('status','UNACCEPTED_DERIVATIVE_OR_REPAIR_HISTORY')})
    manifest={'schema':1,'date':'2026-10-11','scope':'Only today new assets-folder derivatives; no baseline images, QA pictures, APKs or whole-project backup','baseline':{'path':inventory['baseline'],'sha256':inventory['baselineSHA256'],'all3647BaselineAssetsCurrentlyMatch':True},'nativeGeneration':'No new native bytes in assets relative to baseline; existing natives reused','files':sorted(files,key=lambda r:r['path']),'assetBytes':sum(r['bytes'] for r in files),'newDeviceRestore':'UNVERIFIED'}
    out=ROOT/'output/device-transfer-20261011'; out.mkdir(parents=True,exist_ok=True)
    archive=out/'new-assets-20261011.zip'
    if archive.exists():
        if not refresh: raise FileExistsError('Refusing a second build over existing ZIP')
        verify_zip(archive,json.loads((HERE/'new-assets-manifest.json').read_text()))
    restore='Restore baseline assets first (existing assets folder or verified previous transfer). Clone the published main commit. Run: python docs/migration/device-handoff-20261011/transfer.py verify --zip PATH/new-assets-20261011.zip ; then restore --zip same-path. Restore refuses different existing bytes and links. Never run producer scripts to reconstruct missing provenance. This archive contains only today new assets; it cannot replace the baseline. Read docs/plan/CROSS-DEVICE-CONTINUATION-2026-10-11.md. Product INCOMPLETE; destination restore UNVERIFIED.\n'
    with zipfile.ZipFile(archive,'w' if refresh else 'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        for r in manifest['files']: z.write(ROOT/r['path'],r['path'])
        z.writestr('TRANSFER-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('RESTORE.txt',restore)
    manifest['zip']={'path':archive.relative_to(ROOT).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
    (HERE/'new-assets-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    result=verify_zip(archive,manifest)
    (ROOT/'qa/planner-device-handoff-20261011/zip-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(manifest['zip']|result|{'assetBytes':manifest['assetBytes']},indent=2))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['build','verify','restore','verify-baseline']); ap.add_argument('--zip',type=Path); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--refresh-manifest',action='store_true'); args=ap.parse_args()
    if args.mode=='build': return build(args.refresh_manifest)
    if args.mode=='verify-baseline':
        baseline=json.loads((ROOT/'docs/migration/device-handoff-20261009/transfer-manifest.json').read_text()); rows=[r for r in baseline['files'] if r['path'].startswith('assets/')]
        failures=[r['path'] for r in rows if not safe(args.root,r['path']).is_file() or sha(safe(args.root,r['path']))!=r['sha256']]
        print(json.dumps({'files':len(rows),'failed':failures},indent=2)); return 1 if failures else 0
    manifest=json.loads((HERE/'new-assets-manifest.json').read_text()); archive=args.zip or ROOT/manifest['zip']['path']
    result=verify_zip(archive,manifest)
    if args.mode=='restore':
        # Preflight every destination before the first write; never replace unlike bytes.
        destinations=[(r,safe(args.root,r['path'])) for r in manifest['files']]
        for r,p in destinations:
            if p.exists() and (not p.is_file() or sha(p)!=r['sha256']): raise ValueError('Existing destination differs: '+str(p))
        restored=0
        with zipfile.ZipFile(archive) as z:
            for r,p in destinations:
                if p.exists(): continue
                p.parent.mkdir(parents=True,exist_ok=True)
                with p.open('xb') as f: f.write(z.read(r['path']))
                if sha(p)!=r['sha256']: raise ValueError('Readback mismatch: '+str(p))
                restored+=1
        result.update(restored=restored,verifiedDestinationFiles=len(destinations))
    print(json.dumps(result,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main() or 0)
