"""Local planner QA only: source/art/package read; own QA outputs only."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,re
from datetime import datetime,timezone
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=ROOT/'qa/code-art-next-verification-20261004'
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x): (QA/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
files=set()
for pattern in ['src/**/*','tests/*.mjs','assets/delivery/**/*','assets/high-res/**/output.png','docs/plan/image-production/*.json','docs/plan/IMPLEMENTATION-CONTRACT.json','android/app/src/**/*','android/app/build.gradle','android/app/build/outputs/apk/debug/*.apk','dist/**/*','index.html','package.json']:
    files.update(p for p in ROOT.glob(pattern) if p.is_file())
rows=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)]
save('protected-start.json',{'at':datetime.now(timezone.utc).isoformat(),'files':rows})
old=read(ROOT/'qa/code-art-followup-20261004/snapshot-start.json')
save('changed-since-previous.json',[{'file':x['file'],'oldSHA256':x.get('sha256'),'currentSHA256':sha(ROOT/x['file']) if (ROOT/x['file']).is_file() else None} for x in old['files'] if x.get('sha256') and (ROOT/x['file']).is_file() and sha(ROOT/x['file'])!=x['sha256']])
for name in ['browser.mjs','creature.mjs','journeys.mjs']:
    source=(ROOT/'qa/code-art-followup-20261004'/name).read_text(encoding='utf-8')
    # Retain only representative defect/result screenshots in this fresh audit.
    source=source.replace('await p.screenshot({path:path.join(out,`kingdom-${width}x${height}.png`)});','')
    source=source.replace('await p.screenshot({path:path.join(out,`kingdom-panel-${width}x${height}.png`)});','if(width===825)await p.screenshot({path:path.join(out,`kingdom-panel-${width}x${height}.png`)});')
    source=source.replace("await p.screenshot({path:path.join(out,'new-save-failed.png')});",'')
    (QA/name).write_text(source,encoding='utf-8')
apk=ROOT/'android/app/build/outputs/apk/debug/app-debug.apk'; packaged=[]
if apk.exists():
    with zipfile.ZipFile(apk) as z:
        for name in z.namelist():
            if name.startswith('assets/www/') and not name.endswith('/'):
                rel=name.removeprefix('assets/www/'); digest=hashlib.sha256(z.read(name)).hexdigest()
                packaged.append({'file':rel,'sha256':digest,'rootMatch':sha(ROOT/rel)==digest if (ROOT/rel).is_file() else None,'distMatch':sha(ROOT/'dist'/rel)==digest if (ROOT/'dist'/rel).is_file() else None})
        dex=b'\n'.join(z.read(n) for n in z.namelist() if re.fullmatch(r'classes\d*\.dex',n))
        dexFacts={'oldFileOriginLiteral':b'file:///android_asset/www/index.html' in dex,'assetLoaderOriginLiteral':b'https://appassets.androidplatform.net/assets/www/' in dex}
    save('apk-static.json',{'at':datetime.now(timezone.utc).isoformat(),'apkSHA256':sha(apk),'apkBytes':apk.stat().st_size,'webFiles':packaged,'rootMismatches':[x['file'] for x in packaged if x['rootMatch'] is False],'distMismatches':[x['file'] for x in packaged if x['distMatch'] is False],'dexFacts':dexFacts,'device':'STOPPED_NO_INSTALL_OR_QUERY'})
restore=read(ROOT/'qa/full-asset-verifier-20261003/restore-manifest-draft.json')
def git(*args): return subprocess.run(['git','--no-optional-locks',*args],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
save('local-git-storage.json',{'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'trackedAssets':len(git('ls-files','assets').splitlines()),'destination':restore.get('destination'),'verifiedRestoreRows':sum(bool(x.get('externalCopyVerified') and x.get('independentBackupVerified') and x.get('restoreVerified')) for x in restore['files']),'remote':'NOT_QUERIED','storageMutation':False})
docs=[]
for n in ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/CODE-AI-RESUME-2026-10-04.md','docs/plan/REQUIREMENTS-MATRIX-2026-10-04.md','docs/plan/CODE-ART-NEXT-EXECUTION-PROMPT-2026-10-04.txt','docs/plan/FULL-IMPLEMENTATION-SPEC.md','docs/plan/MASTER-PLAN.md','docs/plan/REQUIREMENTS-TRACEABILITY.md','docs/plan/ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md','docs/plan/IMAGE-FIRST32-INDEPENDENT-VERIFICATION-2026-10-04.md','docs/plan/IMAGE-ONLY-PRODUCTION-AND-CLEANUP-2026-10-04.md']:
    p=ROOT/n; text=p.read_text(encoding='utf-8-sig'); docs.append({'file':n,'sha256':sha(p),'charsRead':len(text),'headings':re.findall(r'^#{1,3} .+$',text,re.M)})
save('documents-read.json',docs)
print(json.dumps({'protected':len(rows),'apkRootMismatches':[x['file'] for x in packaged if x['rootMatch'] is False],'storage':read(QA/'local-git-storage.json')},indent=2))
