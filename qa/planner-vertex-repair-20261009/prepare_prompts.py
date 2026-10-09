"""Planner-only prompt/policy preparation. Never invokes production/provider helpers."""
import pathlib,re,json,hashlib,posixpath
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
Q.mkdir(parents=True,exist_ok=True)
protected=[]
for base in ('src','tests','scripts'):
 protected.extend(p for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
protected.extend(R/p for p in ['index.html','package.json','.git/index','.git/HEAD','docs/plan/image-production/budget-ledger.json','docs/plan/image-production/reconciled-accounting-ledger.json','docs/plan/image-production/active-batch.lock.json','docs/plan/image-production/submission.mutex.json','docs/plan/image-production/pacing_state.json','docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json','docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json','docs/plan/ENVIRONMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt','docs/plan/ACTORS-EQUIPMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt','qa/image-residual-executor-20261007/actors/regeneration-manifest.json'])
protected.extend(p for p in (R/'assets/runtime-code-20261007').rglob('*') if p.is_file())
snapshot={p.relative_to(R).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in protected if p.is_file()};save('input-hashes.json',snapshot)
policy=(R/'docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md').read_text(encoding='utf-8')
matrix=policy.split('## Known and foreseeable blocker recovery\n',1)[1].split('## Generation acceptance and preservation',1)[0].strip()
authority='''Latest direct OWNER AUTHORITY — 9 October2026: "If is there any blocker or the art is not correctly generated , then can regenerate that art with vertex AI then work." Necessary per-ID Vertex replacements of defective/missing required art are now authorized. This supersedes historical NO_NEW_PAID_CALLS/local-only text for this bounded successor execution. Do not ask again for each affordable ready repair request. Preserve existing US$80 hard cap/US$15 protected reserve/one-active-or-unknown rule; no blanket repurchase, reserve spending, batch18+, filler or new game content. Planner created instructions only; YOU execute your assigned work.

Use gemini-3.1-flash-image in supplied project project-eaa4c1cc-8f19-4d24-9e6, existing intended account arghawork3@gmail.com, global supported endpoint and existing bucket. No project/provider/model/region/tier fallback, IAM/billing/global CLI setting change, device/Git/runtime work. Refresh actual access/active operations privately before calls; never expose tokens/credential content. Local released mutex/terminal lock is historical, not fresh remote evidence.

Known budget snapshot, locally inspected9October: newer docs/plan/image-production/budget-ledger.json reconciliation totalCommittedProtectedUSD71.1156/marginUnderHardCapUSD8.8844, INCLUDING15reserve and the4actorcall estimate0.4144. Older reconciled-accounting-ledger.json reports70.7012/9.2988 and omits that newer addition; do not double-count it or spend the optimistic older margin. Invoices UNKNOWN; reconcile unique attempts/later liability/holds conservatively before each dispatch. Unknown is not zero; do not release reserve or arbitrary holds. Aim60 is already exceeded; hard80 persists. If scope exceeds verified affordability, finish affordable/local work and publish pending IDs/shortfall for explicit owner budget decision. No current affordability/all-scope success guarantee.

Official documentation checked9October: model supports image generation/editing/native2K/4K; standard global output-only approximate costs0.101USD/2K and0.15USD/4K PLUS inputs/text/reasoning/storage/overhead. References: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image?hl=en and https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing?hl=en . Refresh before paid execution. Reserve the configured worst-case token/candidate/input bound, including unexpected extra images; output-only examples are NOT per-call ceilings. Use candidateCount1/one-image instruction and documented response settings; verify native decoded size, not upscale. Do not send a paid calibration/test call.

Concurrency: both Image AIs prepare/matte/measure/assemble in parallel, but AI1 is the SOLE Vertex provider/lock/budget coordinator for both ready queues. AI2 owns actor packs and consumes AI1's published actor response receipts; AI1 does not touch AI2 outputs/helpers/queue/interface. AI1 stores every raw provider response under its own vertex-coordinator directory, keyed by owner/canonicalID/unique attempt. Actor ownership is retained in receipt; AI2 copies only verified immutable returned native bytes into its OWN new candidates before processing. No two independent provider streams, no executor messages/subagents; filesystem ready packs/atomic receipt publication are the coordination contract. Each producer completes other local rows while a request waits. After local queues finish, checkpoint pending packs rather than falsely claim all work complete; AI1 must service prepared sibling packs as they arrive, not stop after its own queue.

Exact signaling paths: AI1 publishes qa/image-vertex-repair-20261009/environment/regeneration/ready-index.json; AI2 publishes qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json. Coordinator response files/receipts/scheduler are exclusively under qa/image-vertex-repair-20261009/environment/vertex-coordinator/, with receipts/ENVIRONMENT/ and receipts/ACTORS/ owner subdirectories. Both producer queues include preparationComplete:boolean and pendingPackIds:string[]. Coordinator records last pinned index versions/served-or-blocked IDs. AI1 may close the coordinator only when both preparationComplete:true indexes are present and all included paid requests are terminal/processed or precisely budget/access/unknown-blocked. If sibling preparation is still ongoing, continue independent work and use bounded status checks; preserve pending coordinator state on interruption, never report completion or invent a new automation.

Use sequential individual native2K actor/parts/item/effect requests and native4K scenes as required by canonical scope. One initial candidate plus AT MOST one justified directed correction per affectedID, both logged/costed; corrected attempt has a new request hash/attempt identity with preserved first failure. Reuse existing adequate rows and successful responses across restarts. Historical exactly30 applies to a separately authorized batch workflow; do not pad this individual repair workflow to30 or create batch18+. A genuinely new compatible generated source may unblock an exhausted LOCAL anatomical method; preserve the old13-attempt history and test the new source without pretending it is recovered original anatomy.

Prepare exact defect-specific reference/base/mask/geometry/landmark packs locally. Null old queue fields or blanket owner guide acceptance are not global pre-generation prerequisites. Generation of hidden ground is allowed as NEW source pixels matching the fixed guide; local blur/warp/fake reconstruction of originals remains forbidden. New terrain may correct wrongly painted roads to match frozen legal pads/roads/Hall/Wall/bridge anchors; changing frozen affine/Hallscale/camera anchors requires separate recorded authority. Full mock screenshots/baked UI are never accepted gameplay output.
'''
transport='''Single-active transport invariants for AI1: adapt inspected generic scripts/interactive_runner_continuity.py ONLY into your owned helpers and new output paths. Never run the historical first32/later73 mains or a hard-coded producer that overwrites originals. Inspect/test the actual adapted transport and budget guard OFFLINE before the first new inference: exclusive atomic mutex with PID/UUID; project-wide cloud CAS ifGenerationMatch; write-ahead EXACT wire bytes/hash and durable reservation before POST; identical bytes sent; no hidden SDK/HTTP retries; crash recovery and successful-response reuse; funds guard enforced before every send. Original helper/history stays read-only. Preserve old ledger versions and append dated new receipts; don't hand-edit historical success/provenance flags.

AI1 alone may update the established shared submission controls: docs/plan/image-production/{submission.mutex.json,active-batch.lock.json,pacing_state.json,budget-ledger.json,reconciled-accounting-ledger.json} and dated archive/evidence entries, plus existing bucket design-mocks/active-batch.lock.json via CAS. Preserve prior bytes/owner history; no force-clearing live/unknown foreign locks. Compute exposure INCLUDING protected reserve only once: verified prior committed/protected exposure + new liabilities/reservations not already counted + new bounded request <=80USD. Do not add15 again if already included, and do not subtract it as available cash. Catch duplicate subattempt IDs and reconcile usage/receipts by unique wire request, not misleading success/reuse labels.

Enforce persisted>=20s gap after successful image calls. On definite429/quota: STOP paid run, saveRetry-After/backoff>=60s and same pending body; resume only after definite rejection and documented accounting/backoff reconciliation, without hidden retry or changing project. Possible dispatched timeout/disconnect/5xx/crash becomesUNKNOWN with full retained liability and blocks all paid calls until exact operation is reconciled. Never resend unknown request merely because time elapsed. Record refused/failed/text-only/no-image responses; they can still cost money. Release owned lock only after every sent attempt has verified terminal/collected or definitively not-accepted state.
'''
contracts='''Generation typed contract (relative forward-slash paths, finite numbers, SHA25664hex):
RepairKind=LOCAL_REPAIR|REUSE|VERTEX_REPLACEMENT|CODE_BINDING_ONLY|AUTHORITY_REQUIRED.
RepairDecision={id:string,owner:ENVIRONMENT|ACTORS,canonicalRequirement:string,kind:RepairKind,defectEvidence:string[],localAttemptEvidence:string[],whyGenerationNecessary:string|null,sourceRefs:SourceRef[],preserve:string[],requiredOutput:string,priority:integer,nextAction:string}.
RegenerationPack={schema:1,id:string,owner:ENVIRONMENT|ACTORS,canonicalId:string,version:string,state:DRAFT|READY|BLOCKED,defect:string,reason:string,priorSourceHashes:string[],referenceRefs:FileRef[],base:FileRef|null,mask:FileRef|null,guide:FileRef|null,landmarks:object|null,legalGeometrySHA256:string|null,requestedResolution:2K|4K,aspectRatio:string,expectedNativeDimensions:WH|null,project:string,model:string,promptPath:string,promptSHA256:string,wireBodyPath:string,wireBodySHA256:string,inputTransforms:object[],semanticCriteria:string[],geometryCriteria:object[],maxCandidateCalls:integer1..2,estimatedUpperBoundUSD:number|null,readinessEvidence:string[],blockedBy:string[]}. Mask/guide-null is allowed ONLY if role-specific applicability is explicitly justified, never because omitted preparation was called a blocker. Never send unsupported invented mask API fields; a guide/mask may be a labeled image input per current API.
PublishedPackIndex={schema:1,owner:ENVIRONMENT|ACTORS,version:string,publishedAt:string,complete:true,packs:{id,path,sha256:string}[]}. Write index LAST atomically; only own producer writes its index. Coordinator pins and rehashes complete versioned packs. A changed/rejected pack becomes a new version; no mutation while in use.
ProviderReceipt={id:string,canonicalId:string,owner:ENVIRONMENT|ACTORS,attemptId:string,requestPackSHA256:string,wireBodySHA256:string,project:string,model:string,resolution:string,status:SUCCEEDED_CANDIDATE|REJECTED|FAILED|UNKNOWN,providerOperation:string|null,rawResponsePath:string|null,rawResponseSHA256:string|null,images:FileRef[],usage:object|null,reservedUSD:number,actualOrRetainedExposureUSD:number,complete:boolean,rejectionEvidence:string[],nextAction:string|null}. Receipt is published atomically only after response/image bytes persist and hash/decode checks finish; UNKNOWN has no consumable output. ProviderSUCCEEDED does not set imageREADY. Owning Image AI reviews semantic/matte/spatial/articulation gates, source-binds accepted new native candidate and processes it inside its own namespace.
Supplement successor Interface and Checkpoint with authorityDate:2026-10-09, repairDecisions:RepairDecision[], regenerationPacks:string, generationReceipts:string[], paidCompletedIds:string[], paidPendingIds:string[], retainedUnknownIds:string[], budgetSnapshot:object, localProcessingComplete:boolean, imageWorkComplete:boolean, localCompletionReason:string. Local complete with paid requests pending is NOT imageWorkComplete. wholeDeliveryReady staysfalse for any applicable failed/unverified primary gate; Code/runtime/device/owner are still separate.
'''
envsteps=[
'Verify your interpreter and installed local libraries.',
'Save the immutable original/producer/Code/control-file input hash snapshot in your owned QA directory.',
'Build the complete environment queue covering145artifacts,9support references,32scenes and all omitted canonical states.',
'Inspect actual reference/native/producer/current runtime pixels for each owned family.',
'Classify each row as reuse, bounded local repair, necessary Vertex replacement, Code binding only or missing authority.',
'Reuse adequate clean rows unchanged with source/crop/limit provenance.',
'Diagnose each confirmed green/magenta/slab/material defect from its actual source and recipe.',
'Perform the bounded source-aware local repair where existing pixels suffice.',
'Validate subject/material/color/contact preservation for every locally corrected output.',
'Normalize every artifact source-to-crop frame/contact/footprint/entrance/height envelope.',
'Trace each32scene from actual native paint with feature-specific applicability.',
'Measure all17pads/Hall/Walls/roads/banks/decks/approaches/height/obstacle/corridor bounds and uncertainty.',
'Prepare source-specific frozen-geometry guides for necessary terrain regeneration.',
'Prepare exact regeneration packs for missing ground/layers or unsuccessful local environmental repairs.',
'Publish your immutable environment READY pack index atomically.',
'Inspect the existing generic continuity runner and all historical input/output path hazards.',
'Adapt the minimal provider coordinator into your exclusive helper directory.',
'Verify the coordinator lock/write-ahead/reservation/reuse/no-hidden-retry/cost guard OFFLINE.',
'Refresh intended account/project/model/pricing and project-wide active-or-unknown state privately.',
'Reconcile unique committed/unknown attempt exposure across the two saved ledgers and later receipts.',
'Pin each available complete sibling actor pack index as a read-only input.',
'Schedule all ready affordable environment and actor requests by dependency/value and deterministic age/family coverage.',
'Acquire the shared owned project lock and durable reservation before the next eligible request.',
'Submit that exact prepared individual Vertex request only after every transport/budget guard passes.',
'Persist raw response/image bytes and terminal orUNKNOWN attempt state without overwriting existing art.',
'Publish complete owner-tagged immutable receipts for collected responses.',
'Apply the specified blocker recovery rule before continuing paid scheduling.',
'Review each new environment candidate against its exact semantic/geometry/native-size criteria.',
'Prepare at most one evidence-directed correction pack for an affected rejected candidate within budget.',
'Process each accepted environment native candidate locally into reproducible owned derivatives.',
'Validate all new contacts/clearance/state-layer/matte/transform gates independently.',
'Finish source-supported support materials or prepare necessary clean-layer generation requests.',
'Render actual reference/native/result ASSET_COMPOSITE comparisons with uniform camera/chrome safe areas at allfourviewports.',
'Verify final input preservation, output hashes/decode/dimensions/alpha/transforms and exact READY subset.',
'Publish your successor environment interface and actual pixel gallery.',
'Publish the final checkpoint with exact local/paid/budget/unknown/Code/owner outcomes.',
'Continue both ready paid queues and all independent environment local rows until delivered or precisely evidence-blocked.'
]
actsteps=[
'Verify your interpreter and installed local libraries.',
'Save the immutable original/producer/Code input hash snapshot in your owned QA directory.',
'Build the full actor queue covering167rows, all8ages/classes and every omitted canonical kit/mount/effect state.',
'Inspect actual native/producer/Code/reference pixels for each owned family.',
'Classify every row as reuse, bounded local repair, necessary Vertex replacement, Code binding only or missing authority.',
'Recheck and reuse the three adequate Code troop crops unchanged for declared bounded uses.',
'Prepare a checker-aware local Slinger baseline protecting complete body and sling.',
'Perform at most one justified local Slinger correction from the saved baseline evidence.',
'Validate Slinger body/weapon/contact preservation on native contrasting backgrounds and intended sizes.',
'Diagnose bothStonegear and allattacker/creature sheet/floor/matte concerns.',
'Correct every feasible source-supported existing matte in your exclusive namespace.',
'Validate anatomy/identity/kit/color/contact after each local correction.',
'Inspect all8class native anatomy/side/socket/pose evidence and preserved exhausted links.',
'Prepare consistent source/reference/landmark guides for genuinely missing complete bodies or compatible donor parts.',
'Prepare exact regeneration packs for missing anatomy/pose or unsuccessful local art repairs.',
'Publish the immutable actor READY pack index atomically for AI1 coordinator discovery.',
'Complete other independent local rows while the coordinator processes prepared requests.',
'Consume only complete matching owner-tagged provider receipts with verified pack/body/image hashes.',
'Copy verified returned native candidate bytes into your OWN new immutable native namespace.',
'Review each generated actor candidate against full-body/role/side/pose/gear/background/native-size criteria.',
'Prepare at most one evidence-directed paid correction pack per rejectedID within coordinator affordability.',
'Process each accepted native actor/item/effect candidate into source-bound local derivatives.',
'Publish exact single-subject/frameROIs for feasible sheets and actor/projectile effects.',
'Attempt genuinely new compatible source-supported anatomical links without rerunning old exhausted methods.',
'Publish complete per-part source/parent/canvas/socket/pivot/scale/draw-order/side matrices.',
'Publish stable frame trim registration and checked motion arc evidence for surviving assemblies.',
'Validate articulation without claiming full gait from a static body or sampled angles.',
'Normalize artifact source/crop/contact/footprint/height metadata.',
'Finish feasible all8age/six-slot/four-quality/ten-artifact/mount/transports presentation.',
'Measure actual alpha-derived visibleCSS limits with camera/safe areas at allfourviewports.',
'Render actual reference/native/result/assembly ASSET_COMPOSITE comparisons across all owned screen families.',
'Verify final hashes/decode/dimensions/alpha/recipes/input preservation and exact READY subset.',
'Publish your successor actor interface and actual pixel gallery.',
'Publish the final checkpoint with local/paid/pending/unknown/Code/owner gates explicitly separate.',
'Continue every independent actor row until delivered or precisely evidence-blocked.'
]
outputs=[]
for who,oldname,newname in [
 ('environment','ENVIRONMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt','ENVIRONMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt'),
 ('actors','ACTORS-EQUIPMENT-IMAGE-AI-AFTER-CODE-EXECUTION-2026-10-07.txt','ACTORS-EQUIPMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt')]:
 text=(R/'docs/plan'/oldname).read_text(encoding='utf-8');text=text.replace('assets/derivatives/image-after-code-20261007/'+who+'/','assets/derivatives/image-vertex-repair-20261009/'+who+'/').replace('qa/image-after-code-20261007/','qa/image-vertex-repair-20261009/')
 text=text.replace('ENVIRONMENT-ART-AFTER-CODE-INTERFACE-2026-10-07.json','ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json').replace('ACTORS-EQUIPMENT-AFTER-CODE-INTERFACE-2026-10-07.json','ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json')
 text=text.replace('Execute this whole owned scope; do not return another plan.','Execute the whole owned repair/regeneration scope under the9October owner authority; do not return another plan. Bundled Node24.19.0 reverified9October2026.')
 text=text.replace('source-supported LOCAL environment image task','environment repair and necessary Vertex regeneration task').replace('source-supported LOCAL actor/equipment task','actor/equipment repair and necessary Vertex regeneration task')
 if who=='environment':
  start=text.index('LOCAL existing-source processing only, NO_NEW_PAID_CALLS,');end=text.index('\n\nAssumptions:',start)
  text=text[:start]+authority+'\n'+transport+'''\nExclusive additional AI1 writes: qa/image-vertex-repair-20261009/environment/vertex-coordinator/ for BOTH queues' raw bodies/responses/native candidates/receipts/scheduler/cost evidence, plus the tightly scoped shared submission-control files listed above. AI2 packs/outputs remain read-only. Store native environment candidates under assets/derivatives/image-vertex-repair-20261009/environment/native/. Preserve old game/raw-art/production/native/hard-links/Code/previousproducer bytes. No runtime/build/device/Git/storage cleanup or executor dispatch. DeviceSTOPPED; zero runtimepermissions. Frozen affine[60,-10,25,35,170,165]/Hallscale0.1312 unchanged. Read docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md.\n'''+text[end:]
  text=text.replace('existing native painted pixels determine feasible layers; neither mask nor crop can recover hidden ground.','Existing-source local masks/crops cannot recover hidden ground; necessary NEW Vertex terrain/layers are now allowed with exact prepared geometry/reference constraints and actual post-generation validation.')
  text=text.replace('Hidden required ground cannot be reconstructed by blur, warp or guessed painting.','Hidden required ground cannot be reconstructed by local blur, warp or guessed painting; prepare a constrained new Vertex source instead.')
  text=text.replace('Hidden ground behind a Hall/building cannot be recreated with blur, warp, guessed painting, screenshot fill or a paid retry.','Hidden ground behind a Hall/building cannot be reconstructed locally by blur/warp/screenshot fill. Necessary NEW Vertex ground is now authorized when guided by frozen legal geometry and approved appearance; reject wrong geometry and allow at most one directed correction.')
 else:
  start=text.index('LOCAL existing-source processing only. NO_NEW_PAID_CALLS.');end=text.index('\n\nAssumptions:',start)
  text=text[:start]+authority+'''\nAI2 has NO independent provider/lock/budget writer. Store actor packs under qa/image-vertex-repair-20261009/actors/regeneration/packs/ and publish qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json atomically. Read returned actor receipts only from qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/. Your new native candidates belong under assets/derivatives/image-vertex-repair-20261009/actors/native/; rehash copied provider bytes and retain exact raw-response provenance. Coordinator receipt is a dependency only for that requestedID, not a reason to stop the rest of your local queue. No changes to AI1/shared controls/helpers/catalogs/rootpointers/runtime/build/device/Git/storage; no executor messaging/delegation. Old game/raw art/production/native/hard-links/Code/previousproducer bytes remain read-only. DeviceSTOPPED/frozenaffine/Hallscale/zero runtimepermissions persist. Read docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md.\n'''+text[end:]
  text=text.replace('actual painted anatomy/pose/kit supports feasible assembly, not filenames or a requirement diagram.','Assembly requires actual compatible anatomy/pose/kit. Where originals genuinely lack it, generate a new complete source/compatible donor with explicit class/side/landmark guides, then verify it. Filenames/diagrams never prove anatomy.')
 text=text.replace('This local task authorizes zero new calls.','The9October instruction authorizes necessary prospective Vertex repair requests throughAI1; it does not retroactively establish older authority or invoices.')
 text=text.replace('No paid replacement authority.','Necessary prospective replacement authority now exists under the9October coordinator/budget rules.')
 text=text.replace('If no clean source exists, give exact absence evidence and Code-native-material recommendation, not another whole screenshot.','If a required art layer lacks a clean source, prepare a constrained Vertex replacement pack. If the layer should be Code-native UI, record that no new image is needed. Never deliver another whole mock screenshot as a functional layer.')
 text=text.replace('Some green is painted in source; preserve foliage/material and genuine shadows.','Some green is painted in source; preserve foliage/material and genuine shadows. If genuine source contamination cannot be separated locally, prepare a subject-preserving Vertex edit/replacement pack with before/after semantic criteria.')
 text=text.replace('Fresh actual Kingdom fixtures additionally','The7October actual Kingdom fixtures additionally').replace('Fresh independent full pad-quad','The7October independent full pad-quad')
 text=text.replace('Current Code', '7October Code').replace('Fresh starting findings', '7October audited starting findings (refresh current bytes before reuse)')
 text=text.replace('Full6affine', 'Full6affine')
 step_start=text.index('4. Step-by-Step Instructions\n');step_end=text.index('5. Edge Cases & Failure Modes\n',step_start)
 steps=envsteps if who=='environment' else actsteps
 text=text[:step_start]+contracts+'\n4. Step-by-Step Instructions\n\n'+'\n'.join(f'{i}. {s}' for i,s in enumerate(steps,1))+'''\n\nEach step is one action. Validate relevant gates perID before promotion. Existing adequate sources are reused. Local methods remain bounded; necessary new native sources are permitted through the9October regeneration workflow. Global paid-access/unknown/budget problems stop paid dispatch only; continue independent local scope. Record newly observed failure types and exact next action.\n\n'''+text[step_end:]
 edge=text.index('5. Edge Cases & Failure Modes\n')+len('5. Edge Cases & Failure Modes\n');text=text[:edge]+'\n'+matrix+'\n\n'+text[edge:]
 # Replace old prohibition that conflicts with newly authorized new-native anatomy; no invented old pixel claims.
 text=text.replace('Crop cannot invent standing anatomy or missing kit.','Crop cannot invent standing anatomy or missing kit. Use necessary constrained Vertex generation to obtain NEW compatible source material when the existing source lacks it.')
 text=text.replace('No whole-image dancing, stretched body chains, guessed joint connectors or diagram promotion.','No whole-image dancing, stretched body chains, guessed joint connectors or diagram promotion; generated donor anatomy still needs measured compatibility and articulation evidence.')
 acc=text.index('6. Acceptance Criteria\n')+len('6. Acceptance Criteria\n');text=text[:acc]+'''\n[ ] Every blocked/defectiveID has an actionable repair/reuse/generation/Code/authority decision rather than a blanket stop.
[ ] Necessary ready affordable Vertex repairs are actually submitted/collected/processed, not merely drafted or deferred under superseded NO_NEW_PAID_CALLS.
[ ] Each regeneration has immutable defect-specific inputs/wire hash/owner/attempt/cost/receipt and current model/access/lock evidence.
[ ] One provider coordinator serves both queues; mutex/CAS/write-ahead/reservations/reuse/no-hidden-retry invariants pass offline checks.
[ ] New liabilities stay within80hardcap with15reserve protected; allunique attempts/unknowns/rejections are counted and preserved.
[ ] Originals/oldnative/acceptedCodecrops/historical source/oldfailedmethods are preserved; all new native bytes use NEW namespaces.
[ ] Raw provider success is inspected as a candidate; semantics/matte/geometry/body/articulation readiness is independently validated.
[ ] Access/quota/budget/unknown failures have exact recovery evidence and do not stop independent local rows.
[ ] Local-processing completion is separate from paid-pending/imageWorkComplete and Code/owner/device acceptance.
'''.replace('\n+','\n')+text[acc:]
 last=text.index('7. Do NOT\n')
 ending='''7. Do NOT

Do not overwrite originals/native/hard-links/olddeliveries/acceptedCodecrops, edit src/tests/sharedscripts/Android/canonical geometry/rootpointers, run gamebuilds/devices/Git/storagecleanup/restore/upload, dispatch/message/delegateAI, or erase failed histories. Do not repurchase clean adequate art or generate outside defect/missing canonical requirements. No batch18+/filler/unlimitedretries/provider fallback/modelprojectregiontier switch, budgetexpansion/reserve spending, forceunlock, duplicateUNKNOWNPOST or implicitSDKretry. New Vertex sources are allowed under9October authority; do not fake restoration of original anatomy/ground, native resolution/alpha, owner acceptance or fullbodygait. Finish all feasible owned local and affordable generation scope and publish precise remaining evidence.
'''
 if who=='actors':ending+='AI2 must never submit to Vertex independently or mutate AI1 coordinator/shared controls; publish prepared actor packs and process verified matching responses in your own namespace.\n'
 text=text[:last]+ending
 output=R/'docs/plan'/newname;output.write_text(text,encoding='utf-8');outputs.append({'owner':who,'path':output.relative_to(R).as_posix(),'sha256':sha(output),'steps':len(steps)})
save('prompts.json',outputs)
budget=json.loads((R/'docs/plan/image-production/budget-ledger.json').read_text(encoding='utf-8'));save('budget-snapshot.json',{'date':'2026-10-09','source':'docs/plan/image-production/budget-ledger.json','sha256':sha(R/'docs/plan/image-production/budget-ledger.json'),'recordedExposureUSD':71.1156,'protectedReserveUSD':15,'recordedRemainingUnder80USD':8.8844,'olderReconciledLedgerExposureUSD':70.7012,'laterFourCallsAlreadyIncludedUSD':.4144,'invoiceStatus':'UNKNOWN','liveAccountProjectState':'NOT_QUERIED_BY_PLANNER','generationCallsThisTurn':0})
print(json.dumps(outputs,indent=2))
