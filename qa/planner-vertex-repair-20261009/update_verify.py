import pathlib,json,hashlib,re,posixpath
R=pathlib.Path(__file__).resolve().parents[2];Q=pathlib.Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
env='docs/plan/ENVIRONMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt';actor='docs/plan/ACTORS-EQUIPMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt';authority='docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md';updates=[]
for rel in ['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/AUDIT-UPDATE.md']:
 p=R/rel;text=p.read_text(encoding='utf-8-sig');marker='Latest OWNER Vertex repair authorization and blocker recovery — 9 October2026'
 if marker in text:continue
 base=posixpath.dirname(rel) or '.'
 def link(target):return posixpath.relpath(target,base)
 prefix='Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; bundled Node24.19.0 reverified9October2026; Python/image tooling recorded7October, verify executor versions. Task: Architecture/Planning; planner does not execute generation or game work.\n\n'
 prefix+='> **'+marker+':** Owner explicitly permits regenerating defective/blocked required art with Vertex, then processing it. This prospectively supersedes blanket NO_NEW_PAID_CALLS/local-only restrictions for necessary per-ID repair requests; it does not expand80USD hard cap/release15USD reserve/change legal geometry/retroactively verify older invoices or calls. Give owner-selected AIs exactly [Environment + sole Vertex coordinator]('+link(env)+') and [Actors/Equipment + actor-pack preparation]('+link(actor)+'). Both are complete seven-section whole-scope prompts; local preparation/processing stays parallel, all paid requests across both queues serialize throughAI1 with shared mutex/CAS/durable reservation/receipt, not two provider streams. [Authority and16blocker recovery cases]('+link(authority)+'); newer local budget records71.1156USD committed/protected including15reserve+fourcalls0.4144, leaving8.8844 under80 BEFORE fresh reconciliation/later liabilities; invoices/live access UNKNOWN. No repeated permission for affordable prepared repairs; exact unaffordable IDs/shortfall require owner budget decision. New native/derivative/QA/interfaces use9October exclusive namespaces; originals/Code crops/history stay intact. Verify actual pixels/semantics/geometry/rigs beforeREADY; blocker affects its own row or paid stream, not independent local work. Image completion/runtime/owner/device gates remain separate; whole gameINCOMPLETE, deviceSTOPPED. Planner wrote QA/docs/pointers only; no provider/account/job/paid/helper/image/game/build/device/Git/storage/lock/budget action or executor dispatch. Earlier local-only and date-specific completion/evidence paragraphs remain historical.\n\n'
 before=sha(p);p.write_text(prefix+text,encoding='utf-8');updates.append({'path':rel,'beforeSHA256':before,'afterSHA256':sha(p),'historyPreservedAsSuffix':p.read_text(encoding='utf-8').endswith(text)})
if updates or not (Q/'pointer-update.json').exists():save('pointer-update.json',updates)
else:updates=json.loads((Q/'pointer-update.json').read_text(encoding='utf-8'))
sections=['Task Summary','Environment','Inputs & Outputs','Step-by-Step Instructions','Edge Cases & Failure Modes','Acceptance Criteria','Do NOT'];checks=[]
for rel in [env,actor]:
 text=(R/rel).read_text(encoding='utf-8');heads=re.findall(r'^([1-7])\. ('+'|'.join(map(re.escape,sections))+r')$',text,re.M);steps=re.findall(r'^(\d+)\. (.+)$',text.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0],re.M)
 checks.append({'path':rel,'sha256':sha(R/rel),'sevenSectionsPass':heads==[(str(i),s) for i,s in enumerate(sections,1)],'atomicSteps':len(steps),'sequentialNumbering':list(map(lambda x:int(x[0]),steps))==list(range(1,len(steps)+1)),'latestAuthorizationPresent':'Latest direct OWNER AUTHORITY — 9 October2026' in text,'bodyProtocolsPresent':all(x in text for x in ['RegenerationPack={','ProviderReceipt={','PublishedPackIndex={','imageWorkComplete:boolean']),'blockerRecoveryCases':len(re.findall(r'^\| (?!Blocker|---).+\|$',text,re.M)),'conservativeBudgetPresent':'71.1156' in text and '8.8844' in text,'oneCoordinatorPresent':'SOLE Vertex provider/lock/budget coordinator' in text})
snap=json.loads((Q/'input-hashes.json').read_text(encoding='utf-8'));changed=[]
for rel,v in snap.items():
 p=R/rel
 if not p.is_file() or sha(p)!=v['sha256']:changed.append({'path':rel,'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None})
policy=(R/authority).read_text(encoding='utf-8');cases=[]
for line in policy.split('## Known and foreseeable blocker recovery\n',1)[1].split('## Generation acceptance and preservation',1)[0].splitlines():
 if line.startswith('| ') and not line.startswith('| Blocker'):
  cols=[c.strip() for c in line.strip('|').split('|')]
  if len(cols)==3:cases.append({'blocker':cols[0],'recovery':cols[1],'stopScope':cols[2]})
save('blocker-recovery.json',{'authorityDate':'2026-10-09','cases':cases,'finiteListCannotGuaranteeNoNewFailure':True,'generationExecutedByPlanner':False})
save('ownership.json',{'environmentAssets':'assets/derivatives/image-vertex-repair-20261009/environment/','actorsAssets':'assets/derivatives/image-vertex-repair-20261009/actors/','environmentQA':'qa/image-vertex-repair-20261009/environment/','actorsQA':'qa/image-vertex-repair-20261009/actors/','vertexCoordinator':'AI1_ONLY','providerReceipts':'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/{ENVIRONMENT,ACTORS}/','readyIndexes':['qa/image-vertex-repair-20261009/environment/regeneration/ready-index.json','qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json'],'exclusiveLocalWriters':True,'sharedControlWriter':'AI1_ONLY_WITH_HISTORICAL_PRESERVATION','localParallelPaidSerial':True,'executorDispatched':False})
missing=[]
for rel in [authority,*[r['path'] for r in updates]]:
 p=R/rel;text=p.read_text(encoding='utf-8');latest=text.split('Earlier local-only and date-specific completion/evidence paragraphs remain historical.')[0] if rel!=authority else text
 for link in re.findall(r'\]\(([^)]+)\)',latest):
  if re.match(r'^https?://',link):continue
  if not (p.parent/link).exists():missing.append({'path':rel,'link':link})
report={'exactlyTwoSuccessorImagePrompts':len(checks)==2,'promptChecks':checks,'protectedFiles':len(snap),'protectedCodeHistoricalPromptsInterfacesBudgetsControlsUnchanged':not changed,'protectedChanges':changed,'historyPreserved':all(r['historyPreservedAsSuffix'] for r in updates),'latestLinksValid':not missing,'brokenLinks':missing,'blockerCases':len(cases),'providerCalls':0,'paidCalls':0,'productionHelperExecutions':0,'imageProductEdits':0,'executorDispatch':False,'newCodeExecutionPrompt':False,'liveAccessBillingNotVerified':True}
save('final-verification.json',report);print(json.dumps(report,indent=2))
