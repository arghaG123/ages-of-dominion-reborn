from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, re
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
items = {
    'START-HERE.md': 'docs/plan/',
    'CURRENT-STATUS.md': 'docs/plan/',
    'DECISIONS.md': 'docs/plan/',
    'docs/SESSION-HANDOFF.md': 'plan/',
    'docs/BUILD-PROGRESS.md': 'plan/',
    'docs/PLANNER-VERIFIER-HANDOFF.md': 'plan/',
    'docs/plan/README.md': '',
    'docs/plan/GIT-ASSET-STORAGE-PLAN-2026-10-03.md': '',
}
for relative, prefix in items.items():
    p = ROOT/relative
    prior = p.read_text(encoding='utf-8-sig')
    marker = '> **Current code-persistence audit — 3 October 2026:**'
    if not prior.startswith(marker):
        text = (f'{marker} Read [the confirmed stopping diagnosis/current evidence]({prefix}CODE-AI-PERSISTENCE-DIAGNOSIS-2026-10-03.md) and [the complete ready-work executor prompt]({prefix}CODE-AI-FINISH-ALL-READY-WORK-PROMPT-2026-10-03.txt). Owner supplied the actual stop reason: unrelated image/device/morale/art-approval gates were treated as global blockers. Fresh49 core tests PASS, but new Defense-save/finite-Endless probes and phone crop FAIL; full implementation/art/owner/native-runtime acceptance remain incomplete. Local and freshly checked remote main are cff5528; preview APK exists (static previewID/zero declared permissions checked), no install here.67assets paths are tracked; inspected restore draft still has null destination/zero verified rows, unrecorded backups UNKNOWN. This supersedes no-commits/no-remote/no-APK and45/48-test status. Missing gates affect their own IDs only; continue independent authorized executor work. Planner QA/docs only; no game repair/build/provider/production/storage/Git mutation, messaging or delegation. Prior text remains history.\n\n')
        p.write_text(text+prior,encoding='utf-8')
stop_message = '''Owner-supplied code executor stopping message, received during this audit:
I stopped because several gates cannot be closed from this chat: no new paid images, no device install, no invented morale rule, and no self-awarded art approval. That was a bad place to halt. The parts that can be built locally should keep moving, and I continued them.

main is now cff552880ae15c892b736ac7847f6753787ca58f.
Short landscape stages use the same camera and cover the world when letterboxing would leave it under 80% of the stage width. 49 tests pass.
Kingdom plots no longer paint filled rectangles and level numbers over the terrain. The selected plot still has a target.
A preview APK assembled successfully: com.agesofdominion.game.reborn.preview, landscape, no permissions. It was not installed.
Still not finished, and not accepted: the Hall stays at scale 0.1312, the terrain painting still has baked huts, the 510 originals are not a reviewed derivative set, and positive morale is still your decision.
'''
(OUT/'owner-supplied-stop-message.txt').write_text(stop_message,encoding='utf-8')
snapshot = json.loads((OUT/'snapshot.json').read_text())
changed = []
for row in snapshot['sourceHashes']:
    p=ROOT/row['file']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']: changed.append(row['file'])
doclinks = []
report = ROOT/'docs/plan/CODE-AI-PERSISTENCE-DIAGNOSIS-2026-10-03.md'
for destination in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
    if not (report.parent/destination).exists(): doclinks.append(destination)
prompt = ROOT/'docs/plan/CODE-AI-FINISH-ALL-READY-WORK-PROMPT-2026-10-03.txt'
summary = {'at':datetime.now(timezone.utc).isoformat(),'sourceOrTestHashChangesDuringAudit':changed,'missingReportLinks':doclinks,'promptWords':len(prompt.read_text(encoding='utf-8').split()),'promptSHA256':hashlib.sha256(prompt.read_bytes()).hexdigest(),'updatedPointers':list(items),'physicalDeviceRun':False,'buildRun':False,'providerCall':False,'executorMessageOrDelegation':False,'gitMutation':False,'limits':'Test/pure-probe/browser QA and docs only; saved benchmark not rerun; native runtime/owner acceptance unverified; concurrently changed producer files belong to the separate executor'}
(OUT/'final-checks.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
