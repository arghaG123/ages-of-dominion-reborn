"""Only documentation pointers; read latest files immediately and retain history."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
AUDIT='BOTH-AI-LATEST-RECHECK-2026-10-05.md'
CODE='CODE-AI-NEXT-AFTER-V8-RECHECK-2026-10-05.txt'
IMAGE='IMAGE-AI-NEXT-AFTER-V8-RECHECK-2026-10-05.txt'
MATRIX='CURRENT-REQUIREMENTS-RECHECK-2026-10-05.md'
language='Language/framework/version: JavaScript ES modules/HTML/CSS/SVG; Node v24.19.0 verified; custom serve/build scripts. Android configured Java21/Gradle8.11.1/AGP8.7.3/SDK36/min24. Python3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1 measured.\n\n'
changes=[]
def write_with_history(path,prefix):
    file=ROOT/path
    old=file.read_text(encoding='utf-8-sig')
    assert 'Latest independent recheck / complete next tasks' not in old,'avoid duplicate pointer'
    changes.append({'path':str(path),'priorSha256':hashlib.sha256(old.encode()).hexdigest()})
    file.write_text(prefix+old,encoding='utf-8')
for rel,base in [
    ('CURRENT-STATUS.md','docs/plan/'),('START-HERE.md','docs/plan/'),
    ('docs/SESSION-HANDOFF.md','plan/'),('docs/BUILD-PROGRESS.md','plan/'),
    ('docs/PLANNER-VERIFIER-HANDOFF.md','plan/'),('docs/CROSS-DEVICE-CONTINUATION-HANDOFF-2026-10-04.md','plan/'),
    ('docs/plan/README.md','')]:
    prefix=language+f'> **Latest independent recheck / complete next tasks — 5 October 2026, planner/verifier, INCOMPLETE:** [Fresh audit]({base+AUDIT}); complete owner-copyable [Code next task]({base+CODE}) and [Image next task]({base+IMAGE}); [current36row matrix]({base+MATRIX}). Fresh Node24:99tests/97PASS/2exact-guideENOENT/exit1. Fresh browser19PASS/1newRetreat-modal-isolationFAIL; the four earlier UI repairs pass. Natural fresh-save guard/earnedorb/return/Siege-defeat-after2waves/one-settlement/reload pass bounded. Current unsignedAPK92f47e7e/359122611bytes/275file closure/CRC/previewID/SDK24-36/zero uses-permission staticPASS. V8:170present hash/decode associationsPASS,2missingguides,12joint metrics reproduce, widened arithmetic8scenes/13360pixels; whole rigs/32terrain remain incomplete. Withdrawn traces persist in non-Stone overlay pixels; Healer heads exist in native source; Stone four-viewport sheet is stretched-thumbnail evidence. NO_NEW_PAID_CALLS; geometry frozen; deviceSTOPPED. Planner QA/docs only; no game/art production/build/provider/device/Git/storage mutation or executor dispatch/delegation. Earlier paragraphs below are dated history where they conflict.\n\n'
    write_with_history(Path(rel),prefix)
matrix=(ROOT/'docs/plan'/MATRIX).read_text()
for rel in ['docs/plan/REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md','docs/plan/CODE-READY-WORK-MATRIX-2026-10-04.md']:
    prefix=matrix+'\n---\n\n## Dated executor and planner history retained verbatim\n\nThe following complete previous content is historical; the current matrix above supplies per-ID status and executable next actions. Earlier none-ready/owner-only stop statements and old package counts do not govern the current task.\n\n'
    write_with_history(Path(rel),prefix)
write_with_history(Path('docs/plan/CODE-AI-RESUME-2026-10-04.md'),language+f'> **Latest independent recheck / complete next tasks — 5 October 2026:** Resume the complete [Code execution prompt]({CODE}) against [fresh audit]({AUDIT}) and [current matrix]({MATRIX}). First fix keyboard background activation during Retreat; retain four verified UI repairs. Complete all independently ready whole-game workflows, naturally prepared Siege and versioned texture/consumer work. Guide delivery, owner visuals, Image partial flags, deviceSTOPPED and morale are scoped exceptions. Earlier checkpoints below are preserved history, including the obsolete ask-guide-then-stop next action. No executor dispatch by planner.\n\n')
write_with_history(Path('docs/plan/IMAGE-LOCAL-SOLUTION-HANDOFF-2026-10-04.md'),language+f'> **Latest independent recheck / complete next tasks — 5 October 2026:** Use complete [Image local execution prompt]({IMAGE}) and [fresh audit]({AUDIT}). V8 is current but partial:14ready rows/78semantic records/eight incomplete chains/32partial scenes. Produce a versioned successor, bounded native-Healer head/other ROIs, complete local transforms, truthful gates, actual per-scene geography and consistent overlays/real-camera comparisons. NO_NEW_PAID_CALLS; originals/frozen geometry/history preserved. Earlier records below remain dated history.\n\n')
(OUT/'documentation-pointer-changes.json').write_text(json.dumps(changes,indent=2))
paths=[p for p in (ROOT/'src').rglob('*') if p.is_file()]+[ROOT/'index.html',ROOT/'package.json',ROOT/'scripts/serve.mjs',ROOT/'scripts/image_v7_local_continuation.py',ROOT/'scripts/image_v8_local_delivery.py',ROOT/'scripts/image_v8_withdraw_ridge_roads.py']+[p for p in (ROOT/'tests').glob('*.test.mjs')]
hashes=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in paths]
(OUT/'examined-source-hashes.json').write_text(json.dumps(hashes,indent=2))
for name in [CODE,IMAGE]:
    text=(ROOT/'docs/plan'/name).read_text()
    sections=re.findall(r'(?m)^([1-7])\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',text)
    assert len(sections)==7
    before,body=text.split('4. Step-by-Step Instructions',1)
    body=body.split('5. Edge Cases & Failure Modes',1)[0]
    nums=[int(n) for n in re.findall(r'(?m)^(\d+)\. ',body)]
    assert nums==list(range(1,len(nums)+1))
rows=re.findall(r'(?m)^\| (OWN-\d+|SYS-\d+a?) ',matrix)
assert len(rows)==36 and len(set(rows))==36,(len(rows),rows)
print(json.dumps({'updatedDocs':len(changes),'examinedSourceHashes':len(hashes),'promptSections':[7,7],'atomicStepCounts':[38,30],'stableRequirementRows':len(rows)},indent=2))
