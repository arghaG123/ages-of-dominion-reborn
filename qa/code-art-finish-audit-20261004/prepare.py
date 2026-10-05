"""Independent local planner inspection; own QA files only, no builds."""
from pathlib import Path
import json,hashlib,re,subprocess,zipfile
from datetime import datetime,timezone
R=Path('C:/dev/ages-of-dominion-reborn'); Q=R/'qa/code-art-finish-audit-20261004'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
patterns=['src/**/*','tests/*.mjs','assets/delivery/**/*','assets/high-res/**/output.png','docs/plan/image-production/*.json','docs/plan/IMPLEMENTATION-CONTRACT.json','android/app/src/**/*','android/app/build.gradle','android/app/build/outputs/apk/debug/*.apk','dist/**/*','index.html','package.json']
files=sorted({p for pat in patterns for p in R.glob(pat) if p.is_file()})
put('protected-start.json',{'at':datetime.now(timezone.utc).isoformat(),'files':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]})
old=R/'qa/code-art-next-verification-20261004'
for n in ['browser.mjs','journeys.mjs','probes.mjs']:(Q/n).write_bytes((old/n).read_bytes())
listed=['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','references/visual-targets/index.json','references/visual-targets/README.md']
names=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']+['docs/plan/'+n for n in listed]+['docs/plan/'+n for n in ['CODE-AI-RESUME-2026-10-04.md','REQUIREMENTS-MATRIX-2026-10-04.md','FULL-IMPLEMENTATION-SPEC.md','CODE-ART-IMPLEMENTATION-NEXT-TASK-2026-10-04.txt','GIT-ASSET-STORAGE-PLAN-2026-10-03.md','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md']]
docs=[]
for n in names:
 p=R/n
 if not p.exists():docs.append({'file':n,'missing':True});continue
 text=p.read_text(encoding='utf-8-sig'); row={'file':n,'sha256':sha(p),'charsRead':len(text),'headings':re.findall(r'^#{1,3} .+$',text,re.M)}
 if p.suffix=='.json':
  v=json.loads(text);row['topKeysOrCount']=list(v)[:25] if isinstance(v,dict) else len(v)
 docs.append(row)
put('documents-read.json',docs)
apk=R/'android/app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(apk) as z:
 rows=[]
 for n in z.namelist():
  if n.startswith('assets/www/') and not n.endswith('/'):
   rel=n[len('assets/www/'):];h=hashlib.sha256(z.read(n)).hexdigest();rows.append({'file':rel,'sha256':h,'rootMatch':sha(R/rel)==h if (R/rel).is_file() else None,'distMatch':sha(R/'dist'/rel)==h if (R/'dist'/rel).is_file() else None})
 dex=b'\n'.join(z.read(n) for n in z.namelist() if re.fullmatch(r'classes\d*\.dex',n))
 required=[p.relative_to(R).as_posix() for p in (R/'src').rglob('*') if p.is_file()]+['index.html']
 put('apk-static.json',{'apkSHA256':sha(apk),'bytes':apk.stat().st_size,'webFiles':rows,'rootMismatches':[x['file'] for x in rows if x['rootMatch'] is False],'distMismatches':[x['file'] for x in rows if x['distMatch'] is False],'currentSourceMissingFromPackage':sorted(set(required)-{x['file'] for x in rows}),'oldFileOriginLiteral':b'file:///android_asset/www/index.html' in dex,'assetLoaderOriginLiteral':b'https://appassets.androidplatform.net/assets/www/' in dex,'device':'STOPPED'})
def git(*a):return subprocess.run(['git','--no-optional-locks',*a],cwd=R,capture_output=True,text=True,check=True).stdout.strip()
restore=read(R/'qa/full-asset-verifier-20261003/restore-manifest-draft.json')
put('git-storage.json',{'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'remotesLocalConfig':git('remote','-v'),'trackedAssets':len(git('ls-files','assets').splitlines()),'draftDestination':restore.get('destination'),'verifiedRestoreRows':sum(bool(x.get('externalCopyVerified') and x.get('independentBackupVerified') and x.get('restoreVerified')) for x in restore['files']),'remoteQueried':False})
selection=read(R/'src/data/reviewed-source-selection.json');bindings=[]
for group in ['delivery','kingdomTerrain']:
 for id,v in selection[group].items():
  for key,hkey in [('file','sha256'),('uiFile','uiSHA256'),('sourceFile','sourceSHA256'),('displayFile','displaySHA256')]:
   if key in v:bindings.append({'id':id,'role':key,'file':v[key],'hashMatch':(R/v[key]).is_file() and sha(R/v[key])==v.get(hkey)})
processing=read(R/'qa/code-art-consumers-20261004/processing.json');new=[]
from PIL import Image
for v in processing['assets']:
 p=R/v['derivative']
 with Image.open(p) as im:im.load();size=im.size;mode=im.mode
 new.append({'id':v['id'],'sourceHashMatch':sha(R/v['sourceFile'])==v['sourceSHA256'],'derivativeHashMatch':sha(p)==v['derivativeSHA256'],'decodedSize':size,'mode':mode})
before=read(old/'protected-closing.json')['rows'];delivery=[]
for v in before:
 if v['file'].startswith('assets/delivery/'):
  delivery.append({'file':v['file'],'unchanged':sha(R/v['file'])==v['closingSHA256']})
put('art-bindings.json',{'bindings':bindings,'newProcessing':new,'priorDelivery':delivery})
print(json.dumps({'protected':len(files),'missingDocs':[x['file'] for x in docs if x.get('missing')],'bindingFailures':[x for x in bindings if not x['hashMatch']],'newDerivatives':new,'priorDeliveryUnchanged':sum(x['unchanged'] for x in delivery),'priorDeliveryCount':len(delivery)},indent=2))
