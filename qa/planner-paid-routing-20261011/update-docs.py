"""Update the ONE executor prompt and authority pointers; no provider/source mutation."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
name='OWNER-PAID-BATCH-PROGRESSIVE-AUTHORITY-2026-10-11.md'
protected=['src/core/battle.js','src/core/mechanics.js','src/core/campaign.js','src/client/main.js','scripts/interactive_runner_continuity.py','scripts/vertex-production.py']
before={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in protected}
p=R/'docs/plan/ONE-WORKABLE-CODE-IMAGE-BLOCKER-SOLUTIONS-PROMPT-2026-10-11.txt'
t=p.read_text(encoding='utf-8-sig')
old="Read this prompt, docs/plan/OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md,"
new='Read this prompt, docs/plan/'+name+', docs/plan/OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md,'
assert t.count(old)==1
t=t.replace(old,new)
old='Owner already authorizes necessary per-ID Vertex repairs and released15USD reserve ONCE. Hard80USD persists.'
new='Owner now explicitly authorizes needed paid requests and delegates batch-versus-progressive routing, with20seconds between successful progressive images, and requires the other AI to complete this WHOLE prompt. Prior15USD reserve was released ONCE; hard80USD persists. New necessary useful batches are permitted under the latest authority; blanket no-new-batches/batch18+ exclusions are superseded without allowing filler, duplicate purchases or per-ID attempt bypass.'
assert t.count(old)==1
t=t.replace(old,new)
assert t.count('Persist>=30s after success across restart.')==1
t=t.replace('Persist>=30s after success across restart.','Persist/enforce>=20seconds from completion of the successful progressive image response to the next generation POST, across IDs/callers/sessions/restarts; any longer quota deadline still applies. This supersedes the older30-second success instruction.')
assert t.count('No renamed-ID bypass/unlimited retry/filler/batch18+.')==1
t=t.replace('No renamed-ID bypass/unlimited retry/filler/batch18+.','No renamed-ID bypass/unlimited retry/filler. Required new useful batch jobs are authorized under F2; retain all original logicalIDs/attempt history.')
addition='''F2. Choose batch or progressive per proven need, then execute the whole delivery
Latest owner authority is docs/plan/OWNER-PAID-BATCH-PROGRESSIVE-AUTHORITY-2026-10-11.md. Use LOCAL for adequate existing natives and mask/binding repair. Use PROGRESSIVE_2K for genuinely missing Healer/Charioteer/class-kit/side/mount/vehicle/rig detail; process/review existing masters first. Use PROGRESSIVE_4K for only those frozen-camera terrain patches proved necessary by manual tracing/local registered assembly. A dependent pose/edit waits for accepted source/master evidence. Critical single needs and fewer than30genuine independent1Krows also use progressive; do not postpone them to fill a batch.

Use BATCH_1K for exactly30distinct useful independently prepared reviewed requirements whose final use genuinely needs only1K (such as verified missing small icons/props). Current official Vertex batch documentation limits image output to default1K;2K/4K output is unsupported, so required2K/4K never goes into a batch or becomes an upscaled native claim. Refresh the exact model/endpoint support and prices at dispatch.91unreviewed plates and32sceneFAIL rows are not purchase lists. Make a per-ID routing/dependency/source/attempt/worst-case-cost table. Missing body pointers and the seven existing standing natives need no repurchase.

The same coordinator mutex/cloudCAS/project operation registry controls BOTH modes. An active/possibly in-flightUNKNOWN batch/progressive operation blocks another generation; financial invoiceUNKNOWN on a verified terminal operation retains its hold but does not automatically block the stream. Reserve the complete aggregate30-row worst-case bound before a batchPOST and preserve per-row logicalIDs/raw/usage/failed/text-only history. A new batch namespace cannot bypass earlier attempts. Honor next-ready-authorized-batch-before-prior-terminal-collection only with verified terminality/readiness/aggregate affordability; retain bounds for uncollected results. If no ready next batch, collect immediately. Continue independent local/Code work while waiting.

Configure the actual progressive transport/callers to the new20-second successful-response-completion gap and verify persistence/restart offline; scripts/interactive_runner_continuity.py already documents20seconds but explicit caller values may differ. Do not edit historical30-second logs into20. Definite429 remains>=60seconds or longerRetry-After; crash/timeout after possiblePOST remainsUNKNOWN/fullhold/noresend until reconciled. Keep the existing materially-different per-ID bounded repair rules, hard80 and once-only reserve0. Needed affordable prepared calls are authorized: do not stop at packs/readiness or ask for repeat per-image permission. Unbounded actual liabilities/cap shortfall/activeUNKNOWN require exact evidence and affect the paid stream; keep every other ready task running.

One selected other AI completes ALL sections and all remaining Code/Image/game/visual/morale/journey/build scope, not merely generation. Collect/process/verify/integrate each accepted output, repair failed findings and deliver the current minimal build for this planner's independent verification. Keep genuine unresolved constraints explicit; a batch completion/prepared pack/checkpoint is not whole-task completion. No new backups/Git/publication/device activity now.

'''
anchor='G. Review existing art first, then acquire only proven missing sources\n'
assert t.count(anchor)==1
t=t.replace(anchor,addition+anchor)
old='exceed80,do paid calibration/filler/batch18+,switch provider/account/project/model/tier'
new='exceed80,do paid calibration/filler/unnecessary new batches,switch provider/account/project/model/tier'
assert t.count(old)==1
t=t.replace(old,new)
old='single stream/mutex/CAS/writeahead/transmitted image bytes/immutable receipts/pacing/bounded attempts.'
new='one shared batch/progressive stream/mutex/CAS/writeahead/transmitted image bytes/immutable receipts/bounded attempts; normal progressive>=20second completion-to-nextPOST gap,429>=60seconds or longerRetry-After, native1K-only batch routing and per-batch aggregate affordability.'
assert t.count(old)==1
t=t.replace(old,new)
p.write_text(t,encoding='utf-8')
for rel,prefix in {'AGENTS.md':'docs/plan/','START-HERE.md':'docs/plan/','CURRENT-STATUS.md':'docs/plan/','DECISIONS.md':'docs/plan/','docs/SESSION-HANDOFF.md':'plan/','docs/BUILD-PROGRESS.md':'plan/','docs/plan/README.md':'','docs/plan/FULL-IMPLEMENTATION-SPEC.md':'','docs/plan/MASTER-PLAN.md':''}.items():
    dest=R/rel; body=dest.read_bytes()
    notice=('> **Latest owner paid routing and whole-prompt execution - 11 October 2026:** [Paid authority/routing]('+prefix+name+'); [ONE updated complete executor prompt]('+prefix+'ONE-WORKABLE-CODE-IMAGE-BLOCKER-SOLUTIONS-PROMPT-2026-10-11.txt). Owner authorizes needed paid images, planner selects batch/progressive, other ONE AI completes ALL Code/Image/game/build prompt work. Progressive gap>=20seconds after successful response completion, persisted; supersedes30seconds. Batch default1K only/exactly30genuine independent useful rows; necessary2Kactors/rigs and proven4Kscene patches use progressive after native review/physical tracing. New necessary useful batches authorized; old blanket batch18+ prohibition superseded, no filler/ID-attempt bypass. Hard80/effectiveReserve0ONCE/retainedUNKNOWN/oneactive-or-inflightUNKNOWN/mutexCAS/writeahead/429>=60orRetryAfter persist. No repeat permission for prepared affordable needed calls. Morale decided/full-build-first independent planner review/later device-owner sequence persists. Planner docs/public research only, no provider/job/paid/lock/accounting/game/build/device/Git/backup/dispatch action. Earlier pacing/paid exclusions are historical.\r\n\r\n')
    dest.write_bytes(notice.encode()+body)
report={'sections':re.findall(r'^([1-7])\. (.+)$',t,re.M),'sourcePreserved':{s:hashlib.sha256((R/s).read_bytes()).hexdigest()==h for s,h in before.items()},'promptSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'progressiveGapSeconds':20,'quotaMinimumSeconds':60,'hardCapUSD':80,'paidRequestsMade':0,'providerQueriesMade':0,'executorDispatched':False}
assert len(report['sections'])==7 and all(report['sourcePreserved'].values())
(R/'qa/planner-paid-routing-20261011/checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
