from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(OUT/n).write_text(json.dumps(d,indent=2),encoding='utf-8')
prior=load(ROOT/'qa/full-asset-verifier-20261003/protected-input-snapshot.json')['files']; retained=[]
for r in prior:
    f=r['file']
    if (f.startswith('assets/production/') and ('/images/' in f or f.endswith('.jsonl') or f.endswith('collection-report.json'))) or (f.startswith('assets/delivery/') and '/derivatives/' in f and '/v3/' not in f) or f=='docs/plan/IMPLEMENTATION-CONTRACT.json':
        p=ROOT/f; retained.append({'file':f,'expected':r['sha256'],'actual':sha(p) if p.exists() else None})
save('prior-preservation-check.json',{'checked':len(retained),'mismatches':[r for r in retained if r['expected']!=r['actual']],'files':retained})
old=Path('C:/dev/ages-of-dominion')
paths=['core/rules/combat.js','core/rules/units.js','core/rules/encounters.js','core/rules/roster.js','core/rules/hero.js','core/rules/adventureNavigation.js','core/data/buildings.js','core/state/storyFlags.js','client/shell/mapActions.js','client/shell/fightContext.js','client/shell/heroActions.js','client/shell/nodeActions.js','client/shell/warActions.js','src/battle/index.js','src/siege/index.js','src/siege/roles.js','src/util.js','reference/ages-of-dominion.html','docs/handoff/07-COMBAT-SPEC.md']
save('formula-source-provenance.json',[{'path':str(old/p),'sha256':sha(old/p),'lines':len((old/p).read_text(encoding='utf-8-sig').splitlines())} for p in paths])
ref=load(ROOT/'docs/plan/GAME-DATA-REFERENCE.json'); print('sourceFiles shape',str(ref['sourceFiles'])[:300])
docs=['START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','RESUME-HERE.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
docs+=['docs/plan/'+p for p in ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','FULL-IMPLEMENTATION-SPEC.md','DATA-ADOPTION-LEDGER.json']]
summary=[]
for f in docs:
    p=ROOT/f;t=p.read_text(encoding='utf-8-sig'); row={'file':f,'sha256':sha(p),'lines':len(t.splitlines()),'bytes':p.stat().st_size}
    if f.endswith('.json'):
        j=json.loads(t);row['structure']=list(j) if isinstance(j,dict) else {'rows':len(j)}
    else:row['headings']=[x for x in t.splitlines() if x.startswith('#')]
    summary.append(row)
save('reading-inventory.json',summary)
print(json.dumps({'preservedChecked':len(retained),'mismatches':[r['file'] for r in retained if r['expected']!=r['actual']],'docs':len(summary),'formulaSources':len(paths)}))
