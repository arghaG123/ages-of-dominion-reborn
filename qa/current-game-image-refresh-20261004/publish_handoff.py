"""Add scoped planner pointers without replacing executor/history bytes."""
import hashlib,json,pathlib
ROOT=pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/current-game-image-refresh-20261004'
rows=[]
files=['CURRENT-STATUS.md','START-HERE.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
for name in files:
    p=ROOT/name
    prefix='docs/plan/' if '/' not in name else ('plan/' if name.startswith('docs/') and not name.startswith('docs/plan/') else '')
    report=prefix+'CURRENT-GAME-AND-IMAGE-SOLUTION-AUDIT-2026-10-04.md'
    code=prefix+'CODE-AI-CURRENT-GAME-COMPLETE-BRIEF-2026-10-04.txt'
    image=prefix+'IMAGE-AI-CONSOLIDATED-LOCAL-SOLUTION-2026-10-04.txt'
    banner=(f'> **Fresh current-game / Image-v5 audit — 4 October 2026, planner/verifier:** [Report]({report}); complete owner-supplied [Code brief]({code}) and [Image local solution]({image}). Both useful passes remain INCOMPLETE: assembled Kingdom/Adventure/Tactical/Defense still fail the promised finished standard. Latest Code reports91tests (not rerun here); current APK02f85e52/319425603bytes/all266root-dist-Android-www matches independently PASS. All30v5 ledger hashes PASS; new Ranger parts/boot repairs exist, joint/matte/content gaps remain. Healer green-panel connectivity does not prove limbs absent; padded anatomical joint tests and bounded per-ROI masks replace crop-edge/threshold methods. Zero-wave Defense losses are saved outcomes, but D1/D2 lane distance0.6 is within base ranges, so off-lane/no-coverage blame is unproved. Stone ranged canonical Slinger and Bronze Heavy Charioteer correct ambiguous replacement/multi-subject rules. No completion percentage, paid/device authority or executor dispatch. Device STOPPED. Planner new QA/docs/pointers only; concurrent executor history preserved below.\r\n\r\n').encode('utf-8')
    original=p.read_bytes()
    if b'Fresh current-game / Image-v5 audit' in original[:300]:continue
    # Recheck immediately before mutation to preserve another writer's newest bytes.
    if p.read_bytes()!=original:raise RuntimeError('Concurrent pointer change: '+name)
    p.write_bytes(banner+original)
    after=p.read_bytes();assert after[len(banner):]==original
    rows.append({'path':name,'oldSHA256':hashlib.sha256(original).hexdigest(),'newSHA256':hashlib.sha256(after).hexdigest(),'oldBytesRetainedAsExactSuffix':True})
(OUT/'handoff-preservation.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'updatedPointers':len(rows),'allPriorBytesPreserved':all(r['oldBytesRetainedAsExactSuffix'] for r in rows)}))
