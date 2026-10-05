"""Read local evidence; write this audit only. No builds, provider or asset mutations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, zipfile
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p):
    return hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
source_paths = sorted([*ROOT.glob('src/**/*.*'), *ROOT.glob('tests/*.mjs'), ROOT/'package.json', ROOT/'android/app/src/main/AndroidManifest.xml', ROOT/'android/app/src/main/java/com/agesofdominion/game/MainActivity.java'])
source_hashes = [{'file': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in source_paths if p.is_file()]
raw = json.loads((ROOT/'qa/whole-implementation-audit-20261003/originals.json').read_text())
bad = [r['file'] for r in raw if not (ROOT/r['file']).exists() or sha(ROOT/r['file']) != r['sha256']]
benchmark = json.loads((ROOT/'qa/benchmark/report.json').read_text())
restore = json.loads((ROOT/'qa/full-asset-verifier-20261003/restore-manifest-draft.json').read_text())
apk = ROOT/'android/app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(apk) as z:
    packaged = [n for n in z.namelist() if n.startswith('assets/www/')]
    mismatches = []
    for n in packaged:
        p = ROOT/n.removeprefix('assets/www/')
        if p.exists() and hashlib.sha256(z.read(n)).hexdigest() != sha(p): mismatches.append(n)
    index = z.read('assets/www/index.html').decode()
    native_manifest = {'sourceExists': True, 'moduleEntry': 'type="module"' in index, 'packagedLocalFiles': len(packaged), 'currentRootFileMismatch': mismatches}
report = {
    'at': datetime.now(timezone.utc).isoformat(),
    'scope': 'Planner read-only inspection plus isolated tests/QA; no build/install/provider/production/storage/Git mutation',
    'head': git('rev-parse','HEAD'), 'branch': git('branch','--show-current'),
    'remoteHeadsFresh': git('ls-remote','--heads','origin'),
    'trackedAssets': git('ls-files','assets').splitlines(),
    'sourceHashes': source_hashes,
    'coreTests': {'command':'node --test tests/*.test.mjs','observedPass':49,'observedFail':0,'fresh':True,'note':'Observed once in tool output; no build performed'},
    'originals': {'count':len(raw),'distinctIds':len({r['id'] for r in raw}),'hashMismatch':bad,'status':'PASS' if not bad else 'FAIL','scope':'Matches recorded original SHA256; not content/derivative acceptance'},
    'savedBenchmark': {'at':benchmark['at'],'automatedPass':sum(r['status']=='PASS' for r in benchmark['automated']),'automatedFail':sum(r['status']=='FAIL' for r in benchmark['automated']),'manualUnverified':sum(r['status']=='UNVERIFIED' for r in benchmark['manual']),'assetCount':len(benchmark['assets']),'freshRun':False},
    'storageEvidence': {'draftStatus':restore.get('status'),'destination':restore.get('destination'),'fullyVerifiedRows':sum(bool(r.get('externalCopyVerified') and r.get('independentBackupVerified') and r.get('restoreVerified')) for r in restore['files']),'scope':'Inspected saved manifest; actual unrecorded external copies remain UNKNOWN'},
    'apk': {'file':apk.relative_to(ROOT).as_posix(),'bytes':apk.stat().st_size,'sha256':sha(apk),'builtByPlanner':False,'runtime':'UNVERIFIED','deviceTesting':'STOPPED_UNAUTHORIZED',**native_manifest},
}
(OUT/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['sourceHashes','trackedAssets']},indent=2))
