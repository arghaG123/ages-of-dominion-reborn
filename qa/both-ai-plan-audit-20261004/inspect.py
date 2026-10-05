"""Planner read-only inspection. Writes only this new QA directory."""
from pathlib import Path
import json,hashlib,re,zipfile,subprocess,collections
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path('C:/dev/ages-of-dominion-reborn');Q=Path(__file__).parent
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
patterns=['src/**/*','tests/*','scripts/*.py','scripts/*.mjs','assets/derivatives/**/*','assets/delivery/**/*','assets/high-res/**/output.png','assets/high-res/final-native2k/*.png','docs/plan/image-production/*.json','docs/plan/IMAGE*MANIFEST*.json','docs/plan/IMPLEMENTATION-CONTRACT.json','android/app/src/**/*','android/app/build.gradle','android/app/build/outputs/apk/**/*.apk','dist/**/*','index.html','package.json']
files=sorted({p for pat in patterns for p in R.glob(pat) if p.is_file()})
snap={'at':datetime.now(timezone.utc).isoformat(),'files':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]}
put('protected-start.json',snap)
old=read(R/'qa/code-art-finish-audit-20261004/protected-start.json')['files'];current={x['file']:x for x in snap['files']}
put('changed-since-code-audit.json',{'changed':[x['file'] for x in old if x['file'] in current and x['sha256']!=current[x['file']]['sha256']],'missing':[x['file'] for x in old if x['file'] not in current],'new':[x['file'] for x in snap['files'] if x['file'] not in {v['file'] for v in old}]})
# Read every locally resolvable document linked/listed by the plan index, plus canonical frozen contracts.
index=R/'docs/plan/README.md';txt=index.read_text(encoding='utf-8-sig')
targets=re.findall(r'\]\(([^)]+)\)',txt)+re.findall(r'`([^`]+\.(?:md|json|txt))`',txt)
names=[R/x for x in ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md']]+[index]
names += [(index.parent/x.split('#')[0]).resolve() for x in targets if not re.match(r'\w+://',x)]
names += [R/'docs/plan'/x for x in ['FULL-IMPLEMENTATION-SPEC.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','IMPLEMENTATION-CONTRACT.json','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','DATA-ADOPTION-LEDGER.json','GAME-DATA-REFERENCE.json','ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','IMAGE-AI-DELIVERY-AND-REPAIR-REPORT-2026-10-04.md','IMAGE-DELIVERY-MANIFEST-2026-10-04.json','KINGDOM-REPAIR-CONSTRAINTS-2026-10-04.json','KINGDOM-REPAIR-CONSTRAINTS-2026-10-04.md']]
names += [R/'docs/plan'/x for x in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','references/visual-targets/index.json','references/visual-targets/README.md']]
names=[R/'docs/PLANNER-VERIFIER-HANDOFF.md' if str(p).replace('\\','/').endswith('/docs/plan/docs/PLANNER-VERIFIER-HANDOFF.md') else p for p in names]
docs=[];extract=[]
for p in sorted(set(names)):
 row={'file':str(p.relative_to(R)) if p.is_relative_to(R) else str(p),'exists':p.is_file()}
 if p.is_file() and p.suffix in ['.md','.json','.txt','.html']:
  s=p.read_text(encoding='utf-8-sig');row.update(sha256=sha(p),charactersRead=len(s),headings=re.findall(r'^#{1,4} .+$',s,re.M))
  if p.suffix=='.json':v=json.loads(s);row['keysOrCount']=list(v)[:40] if isinstance(v,dict) else len(v)
  if p.name in ['MASTER-PLAN.md','DATA-ADOPTION-LEDGER.json','IMPLEMENTATION-CONTRACT.json','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','INSTALLATION-TRANSFER.md','VISUAL-DESIGN.md']:
   extract += ['\nFILE '+row['file']]+[line for line in s.splitlines() if (line.startswith('#') or re.search(r'Given|When|Then|Stage|stage|UNVERIFIED|pending|PENDING|equation|morale|performance|slots|role',line)) and not line.startswith('>')]
 docs.append(row)
put('documents-read.json',docs);(Q/'plan-extracts.txt').write_text('\n'.join(extract),encoding='utf-8')
# Native73 preservation checked against prior closing snapshot, without regeneration.
prior=read(R/'qa/later71-independent-audit-20261004/closing-protected-start.json');put('native73-preservation.json',[{'file':v['file'],'unchanged':(R/v['file']).is_file() and sha(R/v['file'])==v['sha256']} for v in prior])
# Fresh source/raw originals and 4K hashes checked using saved output manifests only.
orig=[]
for p in (R/'docs/plan/image-production').glob('*outputs.json'):
 try:v=read(p)
 except Exception:continue
 def visit(o):
  if isinstance(o,dict):
   f=o.get('file') or o.get('localPath') or o.get('outputFile');h=o.get('sha256') or o.get('outputSHA256')
   if f and h and isinstance(f,str):
    path=Path(f);path=path if path.is_absolute() else R/path
    if path.is_file():orig.append({'file':str(path),'hashMatch':sha(path)==h})
   for x in o.values():visit(x)
  elif isinstance(o,list):
   for x in o:visit(x)
 visit(v)
put('original-manifest-bindings.json',orig)
# Recursively validate delivery files/hash pairs and decode every derivative; no production write.
m=read(R/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json');bindings=[]
def walk(o,where='root'):
 if isinstance(o,dict):
  for k,v in o.items():
   if isinstance(v,str) and ('file' in k.lower() or 'path' in k.lower()) and v.lower().endswith(('.png','.json')):
    p=R/v;hk=next((x for x in [k.replace('File','SHA256').replace('Path','SHA256'),k+'SHA256','sha256','derivativeSHA256','sourceSHA256'] if x in o),None)
    bindings.append({'at':where,'key':k,'file':v,'exists':p.is_file(),'hashKey':hk,'hashMatch':sha(p)==o[hk] if p.is_file() and hk else None})
   walk(v,where+'.'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o):walk(v,where+f'[{i}]')
walk(m);put('delivery-bindings.json',bindings)
derivs=[]
for p in (R/'assets/derivatives').rglob('*.png'):
 with Image.open(p) as im:im.load();mode=im.mode;size=im.size;alpha=im.getchannel('A') if 'A' in im.getbands() else None
 derivs.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'size':size,'mode':mode,'alphaBBox':alpha.getbbox() if alpha else None,'alphaExtrema':alpha.getextrema() if alpha else None})
put('derivatives.json',derivs)
for group in ['actors','mounts','substitutions','rigs','portraits']:
 ps=sorted((R/'assets/derivatives'/group).glob('*.png'))
 for start in range(0,len(ps),16):
  subset=ps[start:start+16];sheet=Image.new('RGB',(1200,320*((len(subset)+3)//4)),(70,80,70));d=ImageDraw.Draw(sheet)
  for i,p in enumerate(subset):
   with Image.open(p) as im:t=im.convert('RGBA');t.thumbnail((285,275))
   x=(i%4)*300;y=(i//4)*320;sheet.paste(t,(x+5,y+5),t);d.text((x+5,y+285),p.stem[:40],fill='white')
  sheet.save(Q/f'{group}-{start//16+1}.jpg',quality=92)
# Inspect both current APK variants; no build/install.
packages=[]
for p in (R/'android/app/build/outputs/apk').rglob('*.apk'):
 with zipfile.ZipFile(p) as z:
  rows=[]
  for n in z.namelist():
   if n.startswith('assets/www/') and not n.endswith('/'):
    rel=n[11:];h=hashlib.sha256(z.read(n)).hexdigest();rows.append({'file':rel,'rootMatch':sha(R/rel)==h if (R/rel).is_file() else None,'distMatch':sha(R/'dist'/rel)==h if (R/'dist'/rel).is_file() else None})
  dex=b'\n'.join(z.read(n) for n in z.namelist() if re.fullmatch(r'classes\d*\.dex',n))
  packages.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'webCount':len(rows),'rootMismatches':[x['file'] for x in rows if x['rootMatch'] is False],'distMismatches':[x['file'] for x in rows if x['distMatch'] is False],'assetLoader':b'appassets.androidplatform.net' in dex,'backgroundBridge':b'rebornBackground' in dex,'oldFileOrigin':b'file:///android_asset/www/index.html' in dex,'rows':rows})
put('apk-static.json',packages)
print(json.dumps({'protected':len(files),'docs':len(docs),'missingDocs':[x['file'] for x in docs if not x['exists']],'derivatives':dict(collections.Counter(x['file'].split('/')[2] for x in derivs)),'packages':[{k:v for k,v in x.items() if k!='rows'} for x in packages]},indent=2))
