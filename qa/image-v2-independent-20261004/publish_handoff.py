from pathlib import Path
ROOT=Path('C:/dev/ages-of-dominion-reborn')
report='IMAGE-V2-INDEPENDENT-REVERIFICATION-2026-10-04.md'
code='CODE-AI-AFTER-IMAGE-V2-REVERIFICATION-2026-10-04.txt'
image='IMAGE-AI-AFTER-V2-REVERIFICATION-2026-10-04.txt'
for name,prefix in [('CURRENT-STATUS.md','docs/plan/'),('docs/SESSION-HANDOFF.md','plan/'),('docs/BUILD-PROGRESS.md','plan/'),('docs/plan/README.md','')]:
 p=ROOT/name; old=p.read_text(encoding='utf-8-sig')
 banner=f'> **Latest independent Image v2 reverification — 4 October 2026:** [Report]({prefix}{report}); give the owner-selected executors [Code prompt FIRST]({prefix}{code}) and [Image prompt SECOND]({prefix}{image}). 482 bindings/240 unique files,73 raw/native matches,510original hashes and2976protected-byte preservation PASS.37card framing improves; current19actor matte rows,3mount floors,rig semantic/pivot interface and polygon-clearance method FAIL; Paladin/Healer source parts deserve local extraction, not blanket irrecoverability.9producer offline probes reproduce, but4isolated reuse-binding corruptions FAIL. Local70.7012protected arithmetic reconciles/twoUNKNOWN holds retained; nested40.225field stale/invoicesUNKNOWN. Fresh APK fbe989b5,296623132bytes/260root-dist-packaged matches PASS static;79tests executor-reported, runtime/native/owner UNVERIFIED, deviceSTOPPED. Code retains working features and continues ready scene/UI/animation/manual journey work; Image owns scoped versioned local repairs. NO_NEW_PAID_SCOPE. Planner QA/docs only, no provider/production/game/build/device/Git/storage mutation, executor messages or delegation. Concurrent banners/history preserved.\n\n'
 p.write_text(banner+old,encoding='utf-8')
for name in ['docs/plan/VISUAL-REPAIR-NEXT-PHASE-2026-10-04.md','docs/PLANNER-VERIFIER-HANDOFF.md']:
 p=ROOT/name;old=p.read_text(encoding='utf-8-sig')
 prefix='' if '/plan/' in name else 'plan/'
 add=f'\n\n## Fresh independent v2 update — 4 October 2026\n\nRead [{report}]({prefix}{report}) and the complete updated [{code}]({prefix}{code}), then [{image}]({prefix}{image}). These supersede earlier next-phase prompts for this handoff. Current Code resume is79tests reported/new static260-file APK closure; preserve frame clock/travel/Hero/Forge/Army/duel improvements. Image technical delivery and portrait framing improve, while exact local actor/mount/anatomy/terrain-survey/reuse-binding and nested accounting gaps remain. Paladin/Healer sources visibly support further local extraction. Work is prepared for owner handoff, not dispatched. Full product INCOMPLETE; no new paid scope, deviceSTOPPED and scoped owner/morale/storage gates persist. Protected files unchanged; planner wrote QA/docs only.\n'
 p.write_text(old+add,encoding='utf-8')
print('Published root status, both handoffs, build progress, plan index and next-phase addendum; preserved concurrent prior content.')
