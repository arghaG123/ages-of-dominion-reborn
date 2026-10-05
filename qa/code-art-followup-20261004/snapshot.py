"""Planner read-only snapshot. Output stays in this QA directory."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
paths=sorted(set(p for pat in ['src/**/*.*','tests/*.mjs','android/app/src/main/**/*.*','android/*.gradle','android/app/build.gradle','index.html','assets/delivery/**/*.*','docs/plan/image-production/active-batch.lock.json','docs/plan/image-production/budget-ledger.json','docs/plan/CODE-AI-RESUME-2026-10-04.md','docs/plan/REQUIREMENTS-MATRIX-2026-10-04.md'] for p in ROOT.glob(pat) if p.is_file()))
prior=json.loads((ROOT/'qa/code-art-verification-20261004/snapshot.json').read_text())
old={r['file']:r['sha256'] for r in prior['sources']}
rows=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]
changes=[r['file'] for r in rows if r['file'] in old and old[r['file']]!=r['sha256']]
selection=json.loads((ROOT/'src/data/reviewed-source-selection.json').read_text());scene=json.loads((ROOT/'src/data/stone-scene.json').read_text())
bindings=[]
def scan(obj,origin):
    if isinstance(obj,dict):
        for key,hkey in [('sourceFile','sourceSHA256'),('displayFile','displaySHA256'),('file','sha256'),('uiFile','uiSHA256')]:
            if isinstance(obj.get(key),str) and obj[key].startswith('assets/'):
                p=ROOT/obj[key]; actual=sha(p) if p.is_file() else None
                item={'origin':origin,'key':key,'file':obj[key],'exists':p.is_file(),'expected':obj.get(hkey),'actual':actual,'hashMatch':actual==obj.get(hkey) if obj.get(hkey) else None}
                if p.is_file():
                    with Image.open(p) as im:item['dimensions']=list(im.size);im.verify()
                bindings.append(item)
        for key,v in obj.items():scan(v,origin+'.'+key)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):scan(v,origin+f'[{i}]')
scan(selection,'selection');scan(scene,'scene')
apk=ROOT/'android/app/build/outputs/apk/debug/app-debug.apk'; package=[]
with zipfile.ZipFile(apk) as z:
    for n in z.namelist():
        if not n.startswith('assets/www/') or n.endswith('/'):continue
        rel=n.removeprefix('assets/www/');h=hashlib.sha256(z.read(n)).hexdigest()
        package.append({'file':rel,'sha256':h,**{label:sha(ROOT/base/rel)==h if (ROOT/base/rel).is_file() else None for label,base in [('rootMatches',''),('distMatches','dist')]}})
restore=json.loads((ROOT/'qa/full-asset-verifier-20261003/restore-manifest-draft.json').read_text())
result={'at':datetime.now(timezone.utc).isoformat(),'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'remote':git('remote','get-url','origin'),'remoteMain':git('ls-remote','--heads','origin','main'),'dirty':git('status','--short'),'files':rows,'changedSincePreviousSourceSnapshot':changes,'consumerBindings':bindings,'apk':{'sha256':sha(apk),'bytes':apk.stat().st_size,'files':package,'rootMismatches':[r['file'] for r in package if r['rootMatches'] is False],'distMismatches':[r['file'] for r in package if r['distMatches'] is False],'missingRoot':[r['file'] for r in package if r['rootMatches'] is None]},'storage':{'destination':restore.get('destination'),'verifiedRows':sum(bool(r.get('externalCopyVerified') and r.get('independentBackupVerified') and r.get('restoreVerified')) for r in restore['files']),'trackedAssets':len(git('ls-files','assets').splitlines()),'unrecordedCopies':'UNKNOWN'},'scope':'No production/provider/build/device/storage/Git mutation. Current consumer bindings only; no repeated all-batch audit.'}
(OUT/'snapshot-start.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'head':result['head'],'sourceChanges':changes,'bindings':len(bindings),'badBindings':[r for r in bindings if not r['exists'] or r['hashMatch'] is False],'apkRootMismatches':result['apk']['rootMismatches'],'apkDistMismatches':result['apk']['distMismatches'],'storage':result['storage']},indent=2))
