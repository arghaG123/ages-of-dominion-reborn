import json,hashlib,re
from pathlib import Path
ROOT=Path('C:/dev/ages-of-dominion-reborn');OUT=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((OUT/'protected-before.json').read_text());changes=[]
for name,h in before.items():
 p=ROOT/name
 if not p.exists() or sha(p)!=h:changes.append(name)
after=set(str(p.relative_to(ROOT)) for base in ['assets','scripts','docs/plan/image-production','src'] for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in str(p))
result={'protectedExistingFiles':len(before),'changedOrMissing':changes,'added':sorted(after-set(before)),'pass':not changes and not(after-set(before))}
(OUT/'preservation-result.json').write_text(json.dumps(result,indent=2))
index=(ROOT/'docs/plan/README.md').read_text(encoding='utf-8-sig');files=set(re.findall(r'\b[\w-]+\.(?:md|json|txt)\b',index));docs=[]
for name in sorted(files):
 p=ROOT/'docs/plan'/name
 if p.exists():
  s=p.read_text(encoding='utf-8-sig');docs.append({'path':str(p),'sha256':sha(p),'chars':len(s),'headings':re.findall(r'^#{1,3} .+',s,re.M)})
(OUT/'all-listed-plan-reading.json').write_text(json.dumps(docs,indent=2))
print(json.dumps(result));print('all named index plan documents read',len(docs))
