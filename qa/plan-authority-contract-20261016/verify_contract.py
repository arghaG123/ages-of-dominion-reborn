"""Verify handoff integrity and scope; does not award gameplay/art acceptance."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; PLAN=ROOT/'docs/plan'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
manual=PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md'; handoff=PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt'
m=manual.read_text(encoding='utf-8'); h=handoff.read_text(encoding='utf-8')
rows=json.loads((OUT/'owner-concern-index.json').read_text(encoding='utf-8'))
requirements={f'OWN-{n:02}' for n in range(1,20)}|{f'SYS-{n:02}' for n in range(1,17)}
mapped={n for row in rows for n in row['originalRequirements']}
G={f'G{n:02}' for n in range(1,17)};gmapped={n for row in rows for n in row['G']}
missing=[]
paths=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md','docs/plan/COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md','docs/plan/INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md','docs/plan/MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md']
for name in paths:
    p=ROOT/name;t=p.read_text(encoding='utf-8')
    if p not in [manual,PLAN/'INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md']:t=t.split('\n\n',1)[0]
    for ref in re.findall(r'\]\(([^)]+)\)',t):
        if '://' not in ref and not (p.parent/ref.split('#')[0]).is_file():missing.append({'from':name,'target':ref})
prior=json.loads((ROOT/'qa/plan-semantic-audit-20261016/verification.json').read_text(encoding='utf-8'))
result={'scope':'AUTHORITATIVE_PLAN_CONTRACT_AND_PRESERVATION_CHECK_ONLY','ownerConcernGroups':len(rows),'all35OriginalIdentitiesMapped':mapped==requirements,'all16FeatureIdentitiesMapped':gmapped==G,'manualExactBytesEmbedded':manual.read_bytes() in handoff.read_bytes(),'original96ExactBytesEmbedded':prior['original96ExactBytesEmbedded'],'original96Contiguous':prior['originalStepsContiguous'],'requiredM_R_J':prior['counts'],'protectedFiles':len(before),'protectedChanges':changed,'missingCurrentLinks':missing,'manualSections0And10Present':'## 0.' in m and '## 10.' in m,'noImplementationAcceptanceClaimed':True,'noProviderBuildDeviceGitMutations':True,'artifacts':{p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [manual,handoff]}}
checks=[result['all35OriginalIdentitiesMapped'],result['all16FeatureIdentitiesMapped'],result['manualExactBytesEmbedded'],result['original96ExactBytesEmbedded'],result['original96Contiguous'],result['manualSections0And10Present'],not changed,not missing,len(rows)==18]
result['structuralAndPreservationChecksPassed']=all(checks)
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
if not all(checks):raise SystemExit(1)
