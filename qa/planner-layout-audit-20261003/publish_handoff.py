from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
summary=('> **Independent candidate audit — 3 October 2026, approximately19:45 IST:** '
'Read [the current audit]({audit}) and [next coding/recovery prompt]({prompt}). '
'Fresh scoped verification:8 tests PASS; all18 candidate site centres pick at four landscape sizes; Hall/contract/guide hashes, uniform.34 envelope, road exclusion and saved package hashes PASS. '
'Candidate remains NOT_OWNER_ACCEPTED: physical threshold/base survey incomplete, actual preview chrome92px differs from metadata112px,14 mature rectangle pairs overlap and tabletP11 partly sits under the panel. Current terrain/composite FAIL. '
'New local evidence supersedes390/unsubmitted14/ungenerated-scene claims:01–14 collected420 originals/415 IDs with all hashes matching;15 saved PENDING/PROVIDER_ACTIVE at19:33:20 IST, live state not queried. '
'Kingdomv4 already generated in14 against a different guide still labelled NOT_OWNER_ACCEPTED; input lacks Hallv3 image. Output improves Stone scene art but crossing/river spatial fidelity FAIL; preserve as reference, no automatic repurchase or runtime adoption. '
'Saved benchmark537PASS/1budgetFAIL covers390; retained15-batch holds+mock/reserve sum107USD, producer47.856 reconciliation covers01–13 only; invoices unknown. '
'Malformed battle-save and remote-melee probes expose incomplete Tactical legality; Defense/textured rigs/five War choices remain incomplete. Positive morale stays PENDING_OWNER_DECISION. '
'Planner wrote QA/docs only; no provider/game/recovery/build/device/budget edits or executor delegation/messages. Historical text follows.\n\n')
targets={'CURRENT-STATUS.md':'docs/plan/','docs/SESSION-HANDOFF.md':'plan/','docs/BUILD-PROGRESS.md':'plan/','docs/PLANNER-VERIFIER-HANDOFF.md':'plan/','docs/plan/README.md':'','docs/plan/KINGDOM-SCENE-CORRECTION-STATUS-2026-10-03.md':''}
ledger=[]
for p,base in targets.items():
 path=R/p;old=path.read_bytes();text=old.decode('utf-8-sig')
 header=summary.format(audit=base+'KINGDOM-CANDIDATE-PLANNER-AUDIT-2026-10-03.md',prompt=base+'CODING-RECOVERY-POST-CANDIDATE-PROMPT-2026-10-03.txt')
 path.write_bytes(header.encode('utf-8')+old)
 ledger.append({'file':p,'oldSHA256':hashlib.sha256(old).hexdigest(),'newSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'historicalBytesPreserved':path.read_bytes().endswith(old)})
(O/'handoff-writes.json').write_text(json.dumps(ledger,indent=2)+'\n')
(O/'scoped-test-result.json').write_text(json.dumps({'command':'node --test tests/kingdom-layout-candidate.test.mjs tests/domain.test.mjs','exitCode':0,'tests':8,'pass':8,'fail':0,'full35SuiteRerun':False,'source':'Fresh exec output in this planner chat'},indent=2)+'\n')
print(json.dumps(ledger,indent=2))
