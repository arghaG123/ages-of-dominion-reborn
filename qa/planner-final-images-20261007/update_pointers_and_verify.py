import pathlib,json,hashlib,re,os
R=pathlib.Path(__file__).resolve().parents[2];Q=R/'qa/planner-final-images-20261007'
names=['START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']
changes=[]
for name in names:
 p=R/name;old=p.read_bytes();text=old.decode('utf-8-sig')
 def link(label,target):return '['+label+']('+os.path.relpath(R/target,p.parent).replace('\\','/')+')'
 banner='Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; verified Node24.19.0 and Python3.12.14/3.13.7 on7October2026. Custom serve/build scripts; Android recorded/deviceSTOPPED.\n\n'
 banner+='> **Latest both-image delivery verification and ONE Code prompt — 7 October 2026, INCOMPLETE:** '+link('independent audit','docs/plan/BOTH-RESIDUAL-IMAGE-DELIVERIES-INDEPENDENT-AUDIT-2026-10-07.md')+'; '+link('complete owner-copyable Code execution prompt','docs/plan/CODE-AI-WHOLE-GAME-AFTER-BOTH-IMAGE-AUDIT-2026-10-07.txt')+'; '+link('actual QA/gallery','qa/planner-final-images-20261007/gallery.html')+'; '+link('per-ID consumer decisions','qa/planner-final-images-20261007/per-id-status.json')+'. Both residual interfaces are present: Environment145rows+9reference-onlysupportscreens/32partialscenes; Actors167rows/148READYclaims/13PARTIAL/6FAIL. Current hashes/decode/dimensions and readySubset integrity PASS;7dimensionerrors/twojointomissions/sixfailedrows repaired. Actual pixels FAIL multiple mattes/sheets/greenbases; all4regeneratedtroop derivatives are near-empty, independently reproduced from the defective flood mask. Four prior native source hashes changed; separate paid authority/invoices UNVERIFIED. Geography conflicts remain in all8Kingdomages; proposals inactive/fullclassbodies incomplete. Fresh100tests/98PASS/2exactguideENOENT;22browsercaptures and8ArmyageFIXTURES, RetreatCancel/EscapefocusFAIL/SVGinertnessgap/testedmapguardPASS. Current Code catalogs consume neither residual delivery. Whole8ages/every-screenCodeconstruction, validatedconsumerpreparation, realjourneys andpackageclosure are the next executor scope; no blanketart/device/morale/guidehalt. Planner QA/docs only; no game/producer/source/provider/build/device/Git/storage/lock/budget mutation, executor message or agents. Earlier dated records remain history.\n\n'
 if 'Latest both-image delivery verification and ONE Code prompt' not in text:
  p.write_bytes((banner+text).encode('utf-8'));changes.append({'path':name,'priorSha256':hashlib.sha256(old).hexdigest(),'priorBytes':len(old),'appendedHistoryPreserved':p.read_bytes().endswith(text.encode('utf-8'))})
(Q/'pointer-update.json').write_text(json.dumps(changes,indent=2))
snapshot=json.loads((Q/'input-hashes.json').read_text());changed=[]
for rel,v in snapshot.items():
 p=R/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=v['sha256']:changed.append(rel)
prompt=R/'docs/plan/CODE-AI-WHOLE-GAME-AFTER-BOTH-IMAGE-AUDIT-2026-10-07.txt';s=prompt.read_text();sections=re.findall(r'^([1-7])\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',s,re.M)
steps=s.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0];numbered=[int(x) for x in re.findall(r'^(\d+)\. ',steps,re.M)]
gallery=(Q/'gallery.html').read_text();missing=[]
for rel in re.findall(r'(?:href|src)="([^"]+)"',gallery):
 if not (Q/rel).exists():missing.append(rel)
out={'protectedInputSnapshotFiles':len(snapshot),'changedSinceAudit':changed,'pointerUpdates':changes,'exactSevenSections':len(sections)==7 and [x[0] for x in sections]==list('1234567'),'atomicStepSequence':numbered==list(range(1,44)),'stepCount':len(numbered),'galleryBrokenLinks':missing,'promptSha256':hashlib.sha256(prompt.read_bytes()).hexdigest(),'status':'PASS' if not changed and len(sections)==7 and not missing and all(x['appendedHistoryPreserved'] for x in changes) else 'FAIL'}
(Q/'final-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='pointerUpdates'},indent=2))
