"""Planner priority/pointer updates, preserving all previous content."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'docs/plan'
BRIEF='VISUAL-PLAYABLE-BUILD-OWNER-PRIORITY-2026-10-05.md'
CODE='CODE-AI-VISUAL-PLAYABLE-WHOLE-BUILD-PROMPT-2026-10-05.txt'
IMAGE='IMAGE-AI-VISUAL-PLAYABLE-LOCAL-DELIVERY-PROMPT-2026-10-05.txt'
language='Language/framework/version: JavaScript ES modules/HTML/CSS/SVG; Node24.19.0; custom serve/build scripts. Android configured Java21/Gradle8.11.1/AGP8.7.3/SDK36/min24; Python local image processing.\n\n'
files=[
('CURRENT-STATUS.md','docs/plan/'),('START-HERE.md','docs/plan/'),
('docs/SESSION-HANDOFF.md','plan/'),('docs/BUILD-PROGRESS.md','plan/'),
('docs/PLANNER-VERIFIER-HANDOFF.md','plan/'),('docs/plan/README.md',''),
('docs/plan/CODE-AI-RESUME-2026-10-04.md',''),('docs/plan/IMAGE-LOCAL-SOLUTION-HANDOFF-2026-10-04.md',''),
('docs/plan/CURRENT-REQUIREMENTS-RECHECK-2026-10-05.md',''),
('docs/plan/REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md',''),('docs/plan/CODE-READY-WORK-MATRIX-2026-10-04.md','')]
changes=[]
for rel,base in files:
    p=ROOT/rel; old=p.read_text(encoding='utf-8-sig')
    if 'Owner visual/playable build priority — 5 October 2026' in old:
        changes.append({'path':rel,'alreadyUpdated':True,'currentSha256':hashlib.sha256(old.encode()).hexdigest()})
        continue
    text=old.replace('## Ordered whole-scope executor priorities','## Previous executor ordering — superseded by the owner visual/playable build priority',1)
    prefix=language+f'> **Owner visual/playable build priority — 5 October 2026:** [Owner clarification]({base+BRIEF}); complete successor [Code prompt]({base+CODE}) and [Image local-delivery prompt]({base+IMAGE}). Primary target is the30owner-approved Vertex LANDSCAPE mocks, indexed by assets/mocks/INDEX.md. Build the whole visible/playable eight-age game first; final fine polish afterward. Basic Home/layout/buttons/terrain/plots/Army/Forge/mode screens are build requirements. Each meaningful delivery requires actual reference-versus-result images; Code also provides live URL and playable interaction evidence. Establish Stone visual grammar then extend all ages/screens without stopping at Stone. Existing audit facts/INCOMPLETE status, scoped blockers, NO_NEW_PAID_CALLS, frozen geometry and deviceSTOPPED persist. This turn wrote planner docs/prompts only; no game/art production/test/build/provider/device/Git/storage work or executor dispatch. Earlier task-priority ordering below is historical where it conflicts.\n\n'
    p.write_text(prefix+text,encoding='utf-8')
    changes.append({'path':rel,'priorSha256':hashlib.sha256(old.encode()).hexdigest(),'newSha256':hashlib.sha256((prefix+text).encode()).hexdigest()})
checks=[]
for name in [CODE,IMAGE]:
    text=(PLAN/name).read_text()
    assert text.startswith('Language/framework/version:')
    headings=re.findall(r'(?m)^[1-7]\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',text)
    assert headings==['Task Summary','Environment','Inputs & Outputs','Step-by-Step Instructions','Edge Cases & Failure Modes','Acceptance Criteria','Do NOT']
    assert 'all eight ages' in text.lower() or 'eight-age' in text.lower()
    assert 'NO_NEW_PAID_CALLS' in text or 'no new paid' in text
    assert (PLAN/BRIEF).is_file()
    checks.append({'path':name,'sections':len(headings),'fullScope':True,'primaryLandscapeTargets':True,'visibleDeliverables':True,'polishDeferred':True})
# Check numbered mock inputs and prompt/brief internal links.
record=json.loads((Path(__file__).parent/'prompt-and-reference-check.json').read_text())
for m in record['primaryMocks']:
    assert hashlib.file_digest((ROOT/m['path']).open('rb'),'sha256').hexdigest()==m['sha256']
assert len(record['primaryMocks'])==30
for path in [PLAN/BRIEF]:
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        assert (path.parent/target).resolve().exists(),target
(Path(__file__).parent/'final-handoff-check.json').write_text(json.dumps({'promptChecks':checks,'unchangedPrimaryMocks':30,'pointerChanges':changes,'implementationPerformed':False,'executorDispatch':False},indent=2))
print(json.dumps({'promptSections':[x['sections'] for x in checks],'unchangedPrimaryMocks':30,'updatedPointers':len(changes),'implementationPerformed':False,'executorDispatch':False},indent=2))
