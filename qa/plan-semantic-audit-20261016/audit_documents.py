"""Documentation-only inventory and preservation checks; never imports game code."""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PLAN = ROOT / 'docs/plan'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def protected():
    paths = [p for d in ['src','scripts','tests','android/app/src'] for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/n for n in ['index.html','package.json','package-lock.json'] if (ROOT/n).is_file()]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}

if sys.argv[1] == 'baseline':
    if (OUT/'protected-before.json').exists(): raise SystemExit('Baseline already exists; preserve it')
    write('protected-before.json', protected())
    mandatory = ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
    names = ['INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','MASTER-PLAN.md','REQUIREMENTS-TRACEABILITY.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','GAME-DATA-REFERENCE.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md']
    paths = {ROOT/n for n in mandatory} | {PLAN/n for n in names}
    for ref in re.findall(r'\]\(([^)]+)\)', (PLAN/'README.md').read_text(encoding='utf-8')):
        if '://' not in ref:
            paths.add((PLAN/ref.split('#')[0]).resolve())
    rows=[]
    for p in sorted(paths):
        if p.is_file():
            body=p.read_text(encoding='utf-8-sig',errors='replace')
            rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'lines':len(body.splitlines()),'read':'UTF8_DOCUMENT_INVENTORY_NOT_SEMANTIC_ACCEPTANCE'})
        else: rows.append({'path':str(p),'missing':True})
    write('reading-inventory.json',rows)
    inputs = [PLAN/n for n in ['MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md','ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt','COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md']]
    write('input-identities.json',[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs])
    print(json.dumps({'protectedFiles':len(protected()),'readingInventory':len(rows),'missing': [r['path'] for r in rows if r.get('missing')]}))
elif sys.argv[1] == 'verify':
    before=json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
    after=protected()
    changes=[p for p in sorted(before.keys()|after.keys()) if before.get(p)!=after.get(p)]
    manual=(PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_text(encoding='utf-8')
    handoff=(PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt').read_text(encoding='utf-8')
    original=(PLAN/'COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md').read_text(encoding='utf-8')
    sequence=original.split('## 4. Step-by-Step Instructions\n',1)[1].split('\n## 5.',1)[0]
    steps=[int(x) for x in re.findall(r'^(\d+)\. ', sequence,re.M)]
    handoff_bytes=(PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt').read_bytes()
    original_bytes=(PLAN/'COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md').read_bytes()
    sequence_bytes=original_bytes.split(b'## 4. Step-by-Step Instructions',1)[1].split(b'## 5.',1)[0]
    result={'scope':'DOCUMENTATION_STRUCTURE_AND_PRESERVATION_ONLY','manualEmbeddedVerbatim':manual in handoff,'manualExactBytesEmbedded':(PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_bytes() in handoff_bytes,'original96SequenceVerbatim':sequence in handoff,'original96ExactBytesEmbedded':sequence_bytes in handoff_bytes,'originalStepsContiguous':steps==list(range(1,97)),'counts':{k:len(re.findall(v,manual,re.M)) for k,v in {'M':r'^### M\d{2} ', 'R':r'^### R\d{2} ', 'J':r'^### J\d{2} '}.items()},'featureContracts':len(re.findall(r'^\| G\d{2} \|',handoff,re.M)),'protectedFiles':len(before),'protectedChanges':changes,'implementationAcceptance':'NOT_TESTED','providerBuildDeviceGitMutations':False}
    result['artifacts']={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md',PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt',PLAN/'INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md']}
    write('verification.json',result)
    print(json.dumps(result,indent=2))
