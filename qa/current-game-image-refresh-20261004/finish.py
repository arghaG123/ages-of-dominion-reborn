"""Verify preservation and review artifact links; no production mutations."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/current-game-image-refresh-20261004'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
before=json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
changed=[]
for row in before:
    p=ROOT/row['path']
    if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:changed.append(row['path'])
preservation={'checkedFiles':len(before),'changedOrMissing':changed,'status':'PASS' if not changed else 'CONCURRENT_CHANGE_REQUIRES_REVIEW','scope':'Existing assets/src/scripts/android outputs/dist/www excluding .gradle/intermediates/node_modules. New QA/docs are outside this protected set.'}
(OUT/'preservation-result.json').write_text(json.dumps(preservation,indent=2),encoding='utf-8')
names=['docs/plan/CURRENT-GAME-AND-IMAGE-SOLUTION-AUDIT-2026-10-04.md','docs/plan/CODE-AI-CURRENT-GAME-COMPLETE-BRIEF-2026-10-04.txt','docs/plan/IMAGE-AI-CONSOLIDATED-LOCAL-SOLUTION-2026-10-04.txt']
files=[];broken=[]
for name in names:
    p=ROOT/name;text=p.read_text(encoding='utf-8')
    files.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
    if p.suffix=='.md':
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if not (p.parent/link).exists():broken.append(link)
assert not broken,broken
(OUT/'deliverables.json').write_text(json.dumps({'files':files,'brokenReportLinks':broken},indent=2),encoding='utf-8')
print(json.dumps({'preservation':preservation,'deliverableFiles':files,'brokenReportLinks':broken},indent=2))
