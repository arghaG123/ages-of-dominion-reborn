"""Read local files, write this QA directory only. No provider/build/Git mutation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
paths=sorted(p for group in ['src/**/*.*','tests/*.mjs','android/app/src/main/**/*.*'] for p in ROOT.glob(group) if p.is_file())
originals=json.loads((ROOT/'qa/whole-implementation-audit-20261003/originals.json').read_text())
bad=[r['file'] for r in originals if not (ROOT/r['file']).exists() or sha(ROOT/r['file'])!=r['sha256']]
rows={}; journals=[]
for jp in sorted((ROOT/'assets/high-res/interactive-4k-first32-20261003').glob('*/journal.json')):
    journal=json.loads(jp.read_text(encoding='utf-8')); journals.append({'file':jp.relative_to(ROOT).as_posix(),'sha256':sha(jp),'summary':journal.get('summary')})
    for r in journal.get('attempts',[]):
        if not r.get('outputFile') or not r.get('sha256'): continue
        p=ROOT/r['outputFile']
        if not p.exists(): continue
        digest=sha(p)
        with Image.open(p) as im: size=list(im.size); im.verify()
        rows[r['id']]={'id':r['id'],'file':r['outputFile'],'sha256':digest,'matchesJournal':digest==r['sha256'],'dimensions':size,'technical':'PASS' if digest==r['sha256'] and size==[5504,3072] else 'FAIL','spatial':'UNVERIFIED','owner':'UNVERIFIED'}
apk=ROOT/'android/app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(apk) as z:
    packaged=[n for n in z.namelist() if n.startswith('assets/www/') and not n.endswith('/')]
    mismatches=[n for n in packaged if (ROOT/n.removeprefix('assets/www/')).is_file() and hashlib.sha256(z.read(n)).hexdigest()!=sha(ROOT/n.removeprefix('assets/www/'))]
restore=json.loads((ROOT/'qa/full-asset-verifier-20261003/restore-manifest-draft.json').read_text())
assets=[p for p in (ROOT/'assets').rglob('*') if p.is_file()]
catalog=[{'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in assets]
(OUT/'asset-preservation-catalog.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'purpose':'Concrete local preservation proposal; no copies performed','destination':None,'independentDestination':None,'files':catalog},indent=2))
result={'at':datetime.now(timezone.utc).isoformat(),'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'remoteConfigured':git('remote','get-url','origin'),'remoteLive':'NOT_QUERIED','dirty':git('status','--short'),'sources':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths],'originals':{'count':len(originals),'ids':len({r['id'] for r in originals}),'mismatches':bad},'highres':{'count':len(rows),'outputs':list(rows.values()),'journals':journals,'providerLive':'NOT_QUERIED'},'apk':{'bytes':apk.stat().st_size,'sha256':sha(apk),'packagedFiles':len(packaged),'rootMismatches':mismatches,'nativeRuntime':'UNVERIFIED','device':'STOPPED_UNAUTHORIZED'},'preservation':{'assetsFiles':len(assets),'assetsBytes':sum(r['bytes'] for r in catalog),'trackedAssets':git('ls-files','assets').splitlines(),'savedDestination':restore.get('destination'),'savedVerifiedRows':sum(bool(r.get('externalCopyVerified') and r.get('independentBackupVerified') and r.get('restoreVerified')) for r in restore['files']),'unrecordedCopies':'UNKNOWN'}}
(OUT/'snapshot.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['sources','dirty','highres','preservation']},indent=2))
print(json.dumps({'highresCount':len(rows),'highresFailed':[r['id'] for r in rows.values() if r['technical']=='FAIL'],'assetsFiles':len(assets),'assetsBytes':result['preservation']['assetsBytes'],'trackedAssets':len(result['preservation']['trackedAssets'])}))
