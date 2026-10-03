"""Documentation handoff and final read-only integrity checks."""
from pathlib import Path
import hashlib,json,collections,datetime
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def prepend(rel, text):
    p=ROOT/rel
    old=p.read_text(encoding='utf-8-sig')
    if not old.startswith(text): p.write_text(text+'\n\n'+old,encoding='utf-8')

headline='**Current whole-game audit / owner handoff — 3 October 2026:** '
summary=('Production01–17 locally collected:510 originals/504 IDs; all510 original/prompt hashes match. Fresh41 core tests PASS; existing dist16-source/23-asset closure PASS bounded. Five fresh correctness failures, schematic/incomplete world/support screens and Kingdom framing/registration FAIL remain; native/device and owner acceptance UNVERIFIED. Saved benchmark480-source/627PASS/1budgetFAIL/11manualUNVERIFIED is stale. Saved producer protected exposure57.225USD reconciles completed usage, invoices UNKNOWN; retained119USD holds are history, consumer accounting needs repair. Owner requests32 individual native4K first, later73 native2K in proposed32/17/24 groups; no batch18+, retry/filler or expanded budget. Owner Git destination https://github.com/arghaG123/ages-of-dominion-reborn, commit/push after replacement code task and verified two durable asset copies/restore. Wholeassets/ outsideGit; backup destinations still missing; no move/delete now. Planner changed only QA/docs, no code/production/provider/build/device/Git work or executor messaging/delegation. Historical text follows.')
for rel,prefix in [('CURRENT-STATUS.md','docs/plan/'),('docs/SESSION-HANDOFF.md','plan/'),('docs/BUILD-PROGRESS.md','plan/'),('docs/PLANNER-VERIFIER-HANDOFF.md','plan/'),('docs/plan/README.md','')]:
    links=(f'Read [the current audit]({prefix}WHOLE-IMPLEMENTATION-PLANNER-AUDIT-2026-10-03.md), '
           f'[replacement code prompt]({prefix}REPLACEMENT-CODE-AI-PROMPT-2026-10-03.txt), '
           f'[individual image prompt]({prefix}INTERACTIVE-IMAGE-AI-PROMPT-2026-10-03.txt) and '
           f'[105-item queue]({prefix}INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json). ')
    prepend(rel,'> '+headline+links+summary)
prepend('DECISIONS.md','> **Latest owner handoff — 3 October 2026:** Owner requests whole-implementation verification and replacement code/image executor prompts after code AI usage ended and all17 image batches finished. Owner selected32 individual4K terrain images first, then73 individual2K in later divided groups; the32/17/24 group order is a proposal, not activated now. Existing hard80/aim60/protected15, supplied project, one active/unknown and stop-on-quota persist; no additional retries/filler/batch18+. Owner supplies https://github.com/arghaG123/ages-of-dominion-reborn for commit/push AFTER replacement code task completes. Entireassets/ stays outsideGit; preserve provenance plus two verified durable copies and cleanrestore before ignore/staging, no deleting/moving now. Archive/backup destinations remain genuinely missing. This chat remains planner/verifier only; no execution/delegation. Read [current audit](docs/plan/WHOLE-IMPLEMENTATION-PLANNER-AUDIT-2026-10-03.md) and its two prompts. Historical text follows.')
prepend('docs/plan/GIT-ASSET-STORAGE-PLAN-2026-10-03.md','> **Current owner destination / timing — 3 October 2026:** Git destination is https://github.com/arghaG123/ages-of-dominion-reborn. This supersedes unknown repository/account/name in historical proposal below. Commit/push only AFTER replacement code AI next task completes and storage/restore prerequisites pass. Entireassets/ remains outsideGit. External archive plus independent durable-copy destinations/access/cost scope are still missing; no backup/upload/ignore/staging/commit/push performed by planner. Preserve all local originals and history; no move/delete. Read [current code prompt](REPLACEMENT-CODE-AI-PROMPT-2026-10-03.txt) for concrete order.')

inv=json.loads((OUT/'inventory.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_diff=[x for x,h in inv['sourceHashes'].items() if sha(ROOT/x)!=h]
originals=json.loads((OUT/'originals.json').read_text())
original_diff=[x['file'] for x in originals if sha(ROOT/x['file'])!=x['sha256']]
ledger=json.loads((ROOT/'docs/plan/image-production/budget-ledger.json').read_text(encoding='utf-8-sig'))
q=json.loads((ROOT/'docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json').read_text())
baseline=json.loads((ROOT/'docs/plan/HIGH-RESOLUTION-UPGRADE-COUNT-2026-10-03.json').read_text())['scenarios']['TERRAIN_BACKGROUNDS_ONLY']['items']
expected={x['id'] for x in baseline if x['plannedResolution'] in ('4K','2K')}
actual=[x['id'] for x in q['items']]
assert len(actual)==105 and len(set(actual))==105 and set(actual)==expected
assert collections.Counter(x['imageSize'] for x in q['items'])=={'4K':32,'2K':73}
names=['WHOLE-IMPLEMENTATION-PLANNER-AUDIT-2026-10-03.md','REPLACEMENT-CODE-AI-PROMPT-2026-10-03.txt','INTERACTIVE-IMAGE-AI-PROMPT-2026-10-03.txt','INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json']
result={'checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceFilesUnchanged':not source_diff,'original510HashesUnchanged':not original_diff,'productionBudgetLedgerUnchanged':inv['budgetLedger']==ledger,'queueIdsExactlyMatchOwnerSelectedAllocation':True,'queueCounts':dict(collections.Counter(x['imageSize'] for x in q['items'])),'deliverables':{n:{'bytes':(ROOT/'docs/plan'/n).stat().st_size,'sha256':sha(ROOT/'docs/plan'/n)} for n in names},'sourceDifferences':source_diff,'originalDifferences':original_diff,'limitations':'No baseline snapshot for every lock/guide file; no planner mutations of those files were performed. No live provider state, native/device acceptance or actual archive verified.'}
(OUT/'final-checks.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['sourceFilesUnchanged'] and result['original510HashesUnchanged'] and result['productionBudgetLedgerUnchanged']
print(json.dumps(result,indent=2))
