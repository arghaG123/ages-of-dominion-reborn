"""Planner-only isolated copies; never invokes production helpers."""
from pathlib import Path
import json, re, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_script(source, dest, replacements):
    s=(ROOT/source).read_text(encoding='utf-8-sig')
    for old,new in replacements: s=s.replace(old,new)
    (OUT/dest).write_text(s,encoding='utf-8')
copy_script('qa/planner-recheck-20261005/browser-recheck.mjs','browser-recheck.mjs',[
    ('qa/planner-recheck-20261005','qa/planner-three-ai-20261006'),
    ('output/playwright/planner-recheck-20261005','output/playwright/planner-three-ai-20261006'),('const port = 4237','const port = 4361')])
copy_script('qa/visual-playable-20261005/capture.mjs','capture.mjs',[
    ('qa/visual-playable-20261005','qa/planner-three-ai-20261006/visual'),('const port = 4317','const port = 4362')])
copy_script('qa/planner-recheck-20261005/natural-journey.mjs','natural-journey.mjs',[
    ('qa/planner-recheck-20261005','qa/planner-three-ai-20261006'),('const port = 4243','const port = 4363')])
copy_script('qa/planner-recheck-20261005/verify_artifacts.py','verify_artifacts.py',[
    ('INTERFACE-V8','INTERFACE-V9')])
copy_script('qa/planner-recheck-20261005/verify_v8.py','verify_v9.py',[
    ('INTERFACE-V8','INTERFACE-V9'),('qa/image-local-delivery-v8-20261005/scenes.json','qa/image-local-delivery-v9-20261005/scenes.json'),
    ('v8-bindings.json','v9-bindings.json'),('v8-verification.json','v9-verification.json')])
names=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
names += ['docs/plan/'+n for n in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','IMPLEMENTATION-CONTRACT.json','DATA-ADOPTION-LEDGER.json','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md']]
rows=[]
for n in names:
    p=ROOT/n
    if not p.exists(): rows.append({'path':n,'missing':True}); continue
    s=p.read_text(encoding='utf-8-sig')
    rows.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'headings':re.findall(r'^#{1,3} .+$',s,re.M)})
(OUT/'documents-read.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
snapshot={}
for folder in ['src','tests','scripts']:
    for p in (ROOT/folder).rglob('*'):
        if p.is_file(): snapshot[p.relative_to(ROOT).as_posix()]=sha(p)
(OUT/'source-before.json').write_text(json.dumps(snapshot,indent=2))
print(json.dumps({'documents':len(rows),'missing':[r['path'] for r in rows if r.get('missing')],'sourceFiles':len(snapshot)}))
