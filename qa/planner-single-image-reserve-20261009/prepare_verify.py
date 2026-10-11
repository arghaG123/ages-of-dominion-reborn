import json,re,hashlib,datetime
from pathlib import Path
from decimal import Decimal as D
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
PROMPT=ROOT/'docs/plan/ONE-IMAGE-AI-RESERVE-COMPLETION-PROMPT-2026-10-09.txt'
AUTH=ROOT/'docs/plan/OWNER-RESERVE-RELEASE-SINGLE-IMAGE-AI-2026-10-09.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(QA/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
protected=[]
for folder in ['src','scripts','tests','docs/plan/image-production']:
    protected.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
protected.extend(p for p in (ROOT/'docs/plan').glob('*INTERFACE*') if p.is_file())
protected.extend(ROOT/'docs/plan'/n for n in ['ENVIRONMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt','ACTORS-EQUIPMENT-IMAGE-AI-VERTEX-REPAIR-EXECUTION-2026-10-09.txt','IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md','IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md'])
before={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
dump('input-hashes.json',{'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':before})
budget=json.loads((ROOT/'docs/plan/image-production/budget-ledger.json').read_text(encoding='utf-8-sig'));current=D(str(budget['vertexRepair20261009']['currentCommittedProtectedUSD']));release=D('15');cap=D(str(budget['hardCap']));base=current-release;headroom=cap-base
assert cap==D('80') and release==D(str(budget['safetyReserve']))
dump('budget-policy.json',{'authorityQuote':'use $15 reserve and instruct remain work and solution to do for one AI with a prompt.','sourceSHA256':sha(ROOT/'docs/plan/image-production/budget-ledger.json'),'oldProtectedTotalUSD':str(current),'releasedReserveUSD':str(release),'effectiveProtectedReserveUSD':'0','priorLiabilityUSD':str(base),'remainingCapacityUSD':str(headroom),'hardCapUSD':str(cap),'ledgerMutated':False})
# Independent planner arithmetic model ONLY, not a test of actual executor transport.
def allows(liability,new,authorization=True,releaseAlreadyApplied=False,subtractAgain=False):
    if not authorization or (releaseAlreadyApplied and subtractAgain):return False
    return liability+new<=cap
guards=[('release_once',allows(base,D('0.4')),True),('exact_cap',allows(base,headroom),True),('over_cap',allows(base,headroom+D('0.0001')),False),('missing_authority',allows(base,D('0.4'),False),False),('double_release',allows(base,D('0.4'),True,True,True),False),('do_not_add_reserve_to_cap',allows(base,D('15.20')),False),('legacy_unreleased_guard',allows(current,D('0.4')),False),('later_liability_reduces_capacity',allows(base+D('1'),headroom),False)]
assert all(a==b for _,a,b in guards)
dump('budget-arithmetic-checks.json',{'scope':'Independent planner arithmetic checks; executor must test its actual guard/transport OFFLINE','cases':[{'name':n,'actual':a,'expected':b,'pass':a==b} for n,a,b in guards]})
t=PROMPT.read_text(encoding='utf-8');heads=re.findall(r'^([1-7])\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',t,re.M)
assert len(heads)==7 and [n for n,_ in heads]==list('1234567')
steps=t.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0]
nums=[int(x) for x in re.findall(r'^(\d+)\. ',steps,re.M)];assert nums==list(range(1,47))
refs=re.findall(r'\b(?:0[1-9]|[12][0-9]|30)-[a-z0-9-]+\.jpg',t);assert len(set(refs))==30
for n in refs:assert (ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'/n).is_file()
required=['15.1673','64.8327','US$80','Seven collected','All18 actor packs','39attackers/all8creatures','Eight green bases','32 actor recipes','All12 new Kingdom','maxNewCandidates','one renewed','UNKNOWN','sourceToOutput','AtlasFrame','Part=','imageWorkComplete','localProcessingComplete','readySubset','Device STOPPED','NO_NEW_IMAGE_NEEDED']
missing=[x for x in required if x not in t];assert not missing,missing
dump('prompt-checks.json',{'promptSHA256':sha(PROMPT),'sections':heads,'atomicSteps':len(nums),'primaryReferences':len(set(refs)),'acceptanceChecks':len(re.findall(r'^\[ \]',t,re.M)),'requiredContractsAndFixes':required,'missing':missing,'singleExecutor':True,'futureActualTransportTested':False})
targets=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/AUDIT-UPDATE.md']
updates=[]
for name in targets:
    p=ROOT/name;old=p.read_text(encoding='utf-8-sig');h=sha(p)
    prefix='' if name.startswith('docs/plan/') else 'plan/' if name.startswith('docs/') else 'docs/plan/'
    banner=f'> **Latest OWNER reserve release / ONE Image AI — 9 October 2026:** Owner says "use $15 reserve and instruct remain work and solution to do for one AI with a prompt." Use exactly [the single complete executor prompt]({prefix}ONE-IMAGE-AI-RESERVE-COMPLETION-PROMPT-2026-10-09.txt) and [recorded authority/solutions]({prefix}OWNER-RESERVE-RELEASE-SINGLE-IMAGE-AI-2026-10-09.md). This supersedes the two-image-executor split and protected15spending prohibition prospectively for this repair pass. Hard80 remains: current79.8327 includes15; released effective priorliability64.8327 gives15.1673capacity BEFORE laterliabilities/freshreconciliation. Planner has not changed financial controls or spent funds. One selectedAI owns Environment+Actors+solecoordinator in NEW image-unified-reserve-20261009 namespaces; process7collectedbodies first, fix39attacker/8creature magenta/eightgreenbases/32cropaffines, transmit real guides, complete rigs/atlases/full32scene/every-screen scope, and change failed free-layout terrain method to registered source-bound local/constrained-edit solutions. One bounded materiallydifferent renewed candidate per exhaustedID is an explicitly stated execution interpretation; no blind replay/unlimitedretry. Originalhistory/Codecrops/legalgeometry persist; applicable Image gates must pass beforeREADY. WholegameINCOMPLETE/runtime-ownerUNVERIFIED/deviceSTOPPED. Planner writes QA/docs/pointers only; no provider/paid/production/game/build/device/Git/storage/delegation action. Earlier dated reserve/split/audit paragraphs are historical.\n\n'
    if old.startswith('Language/framework/version:'):
        line,sep,rest=old.partition('\n');new=line+'\n\n'+banner+rest.lstrip('\r\n')
    else:new=banner+old
    p.write_text(new,encoding='utf-8',newline='')
    updates.append({'path':name,'beforeSHA256':h,'afterSHA256':sha(p),'oldBodyRetained':old in new or old.partition('\n')[2].lstrip('\r\n') in new})
dump('pointer-update.json',updates)
broken=[]
for p in [AUTH]+[ROOT/n for n in targets]:
    txt=p.read_text(encoding='utf-8-sig');links=re.findall(r'\]\(([^)]+)\)',txt)
    if p!=AUTH:links=[x for x in links if 'ONE-IMAGE-AI-RESERVE' in x or 'OWNER-RESERVE-RELEASE' in x]
    for l in links:
        if '://' not in l and not (p.parent/l).resolve().exists():broken.append({'file':str(p),'link':l})
changes=[n for n,h in before.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
assert not changes and not broken and all(x['oldBodyRetained'] for x in updates)
dump('final-verification.json',{'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sections':7,'steps':46,'promptsCreated':1,'references':30,'budgetModelChecks':len(guards),'protectedFilesChecked':len(before),'protectedChanges':changes,'pointerUpdates':len(updates),'historyRetained':True,'brokenLinks':broken,'plannerExecutedProvider':False,'ledgerOrLockMutated':False,'executorDispatched':False})
print(json.dumps({'sections':7,'steps':46,'references':30,'budgetChecks':len(guards),'protected':len(before),'protectedChanges':changes,'pointers':len(updates),'brokenLinks':broken,'remainingCapacityUSD':str(headroom)},indent=2))
