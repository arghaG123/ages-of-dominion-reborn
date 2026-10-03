"""Update only planner-owned documents; retain their previous text and ledger history."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
entries=[]
files=['CURRENT-STATUS.md','START-HERE.md','RESUME-HERE.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/FULL-IMPLEMENTATION-SPEC.md']
for f in files:
    p=ROOT/f;before=p.read_bytes();relative='docs/plan/' if '/' not in f else ('plan/' if f.startswith('docs/') and not f.startswith('docs/plan/') else '')
    text=(f'> **CURRENT INDEPENDENT V3 AUDIT — 3 October 2026:** Read [{"the recovery/foundation audit"}]({relative}RECOVERY-V3-PLANNER-AUDIT-2026-10-03.md), [source-equation/delivery corrections]({relative}SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md) and [the ordered current coding/recovery prompt]({relative}CODING-RECOVERY-AI-V3-NEXT-PROMPT-2026-10-03.txt) before historical instructions below. Snapshot270 originals/265 IDs through09; all current output hashes match, prior01–08/v1/v2/contract preservation287 files PASS. Hall v3 subject integrity and Gold v3 bounded18/36px colour/detail improve; native Hall pink warning persists. Stone scene registration/composition FAIL. Consumer discovery270/90 historical/180 unreviewed, six old fixtures PASS; additional missing-evidence/member/camera/policy probes FAIL. Current benchmark still hardcodes240. Isolated state probes reproduce movement refill/guard bypass and invalid-save-domain acceptance. Saved388-check benchmark/23-test run and14-file dist are limited foundations; dist omits referenced assets. No full test/benchmark/build/browser/native/device run was performed by this planner. Source evidence resolves several formerly missing formulas; positive morale effect remains owner decision pending. Current geometry unchanged; vertical-envelope/framing proposal required, not silent shrink/warp. Preserve five bounded UI artwork results and all history; runtime/owner acceptance stays UNVERIFIED. This chat remains planner/verifier only. Batch AI separately retains09–13/150max authority and budget/one-active/stop-on-quota rules; no provider/delegation/storage execution here.\n\n')
    p.write_bytes(text.encode('utf-8')+before)
    entries.append({'file':f,'beforeSHA256':sha(before),'afterSHA256':sha(p.read_bytes()),'historicalSuffixPreserved':p.read_bytes().endswith(before)})
p=ROOT/'docs/plan/CODING-RECOVERY-AI-NEXT-PROMPT-2026-10-03.txt';before=p.read_bytes()
p.write_bytes(b'CURRENT POINTER: use CODING-RECOVERY-AI-V3-NEXT-PROMPT-2026-10-03.txt. The following prompt is preserved as pre-v3 history; do not restart repaired Hall/Gold work or hardcode240 sources.\n\n'+before)
entries.append({'file':str(p.relative_to(ROOT)),'beforeSHA256':sha(before),'afterSHA256':sha(p.read_bytes()),'historicalSuffixPreserved':p.read_bytes().endswith(before)})
p=ROOT/'docs/plan/DATA-ADOPTION-LEDGER.json';before=p.read_bytes();d=json.loads(before.decode('utf-8-sig'))
statuses={'unit-derived':'DOCUMENTED_FORMULA_IMPLEMENTATION_PENDING','tactical-damage':'DOCUMENTED_DAMAGE_FORMULA_ENGINE_PENDING','tactical-turns':'DOCUMENTED_PARTIAL_TURNS_MORALE_DECISION_PENDING','spells-legality':'DOCUMENTED_PARTIAL_SOURCE_TARGET_EDGES_OPEN','defense-engine':'DOCUMENTED_WAVE_ROLE_FORMULAS_ENGINE_CONTRACT_PENDING','encounters':'DOCUMENTED_FORMULA_IMPLEMENTATION_PENDING','adventure-endday':'DOCUMENTED_CORE_DAY_FORMULA_RESPAWN_INTEGRATION_PENDING','hero-level':'DOCUMENTED_FORMULA_IMPLEMENTATION_PENDING','loot':'DOCUMENTED_PROBABILITIES_SIX_SLOT_POOL_PENDING','story-dwelling':'DOCUMENTED_FORMULA_IMPLEMENTATION_PENDING','endless-challenge':'DOCUMENTED_PARTIAL_SOURCE_SETTLEMENT_CONTRACT_PENDING'}
paths={'tactical-turns':'C:/dev/ages-of-dominion/src/battle/index.js','spells-legality':'C:/dev/ages-of-dominion/src/battle/index.js','adventure-endday':'C:/dev/ages-of-dominion/client/shell/mapActions.js','hero-level':'C:/dev/ages-of-dominion/reference/ages-of-dominion.html','loot':'C:/dev/ages-of-dominion/client/shell/fightContext.js'}
# The ledger's collection key is intentionally discovered, not renamed.
for key,value in d.items():
    if isinstance(value,list) and any(isinstance(x,dict) and x.get('id')=='unit-derived' for x in value):
        for row in value:
            ident=row.get('id')
            if ident in statuses:
                row.setdefault('planningHistory',[]).append({'at':'2026-10-03','reason':'Independent planner source-equation correction','priorRecord':dict(row)})
                # Avoid retaining a self-reference through the just-created history list.
                row['planningHistory'][-1]['priorRecord'].pop('planningHistory',None)
                row['status']=statuses[ident];row['specification']='docs/plan/SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md';row['sourceEvidence']='qa/planner-verifier-v3-20261003/formula-source-provenance.json';row['implemented']=False
                if ident in paths:row['sourcePath']=paths[ident]
                row['reason']='Source definitions documented; completion requires fresh independent implementation and affected fixtures/integration. Partial policies stay explicitly open.'
d['plannerCorrection']={'at':'2026-10-03','specification':'docs/plan/SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','runtimeVerified':False,'ownerAccepted':False,'moraleDecision':'PENDING_OWNER_CHOICE_EXTRA_TURN_VS_COSMETIC'}
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
entries.append({'file':str(p.relative_to(ROOT)),'beforeSHA256':sha(before),'afterSHA256':sha(p.read_bytes()),'correctionIDs':list(statuses),'priorRecordsPreservedInPlanningHistory':True})
(OUT/'planning-updates.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
ref=json.loads((ROOT/'docs/plan/GAME-DATA-REFERENCE.json').read_text(encoding='utf-8-sig'))
checks=[{'source':r['sourcePath'],'expected':r['sha256'],'actual':sha(Path(r['sourcePath']).read_bytes())} for r in ref['sourceFiles']]
(OUT/'frozen-data-source-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps({'updated':len(entries),'historicalTextPreserved':all(x.get('historicalSuffixPreserved',True) for x in entries),'frozenDataOrigins':len(checks),'dataMismatches':sum(x['actual']!=x['expected'] for x in checks)}))
