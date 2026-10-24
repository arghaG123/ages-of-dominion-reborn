from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def put(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def identity(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
paths=['AGENTS.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/plan/README.md']
paths+=['docs/plan/'+n for n in ['ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt','MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md','ONE-REMAINING-EXECUTOR-AFTER-VERIFICATION-2026-10-16.txt','ONE-FOUR-LIVE-FAILURES-PROMPT-2026-10-17.txt','COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md','MASTER-PLAN.md','FULL-IMPLEMENTATION-SPEC.md','REQUIREMENTS-TRACEABILITY.md','SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','DATA-ADOPTION-LEDGER.json','GAME-DATA-REFERENCE.json','IMPLEMENTATION-CONTRACT.json','INDEPENDENT-WHOLE-GAME-VERIFICATION-2026-10-16.md','INDEPENDENT-WHOLE-GAME-COVERAGE-2026-10-16.md','INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md','OWNER-ART-STYLE-HEALER-AND-BUDGET-2026-10-16.md','OWNER-GAME-LOOK-PRIORITY-AND-ORIGINAL-COMPARISON-2026-10-16.md','INSTALLED-ENVIRONMENT.md','AUDIT-UPDATE.md','VISUAL-DESIGN.md','MOCK-FIDELITY-AUDIT.md','ART-REUSE.md','asset-manifest.json','reviewed-art-ledger.json','raw-inventory.json','public-art-inventory.json','INSTALLATION-TRANSFER.md','REVIEW-AND-STATUS.md','NEXT-AI-PROMPT.md','references/visual-targets/index.json','references/visual-targets/README.md','references/owner-additions-2026-10-02/index.json']]
readme=(ROOT/'docs/plan/README.md').read_text(encoding='utf8')
for link in re.findall(r'\]\(([^)]+)\)',readme):
    if not link.startswith(('http:','https:')):
        p=(ROOT/'docs/plan'/link.split('#')[0]).resolve()
        if p.is_file() and p.suffix.lower() in ['.json','.md','.txt']:paths.append(p.relative_to(ROOT).as_posix())
inventory=[]
for rel in sorted(set(paths)):
    p=ROOT/rel
    if not p.is_file():inventory.append({'path':rel,'exists':False});continue
    text=p.read_text(encoding='utf-8-sig');row=identity(p);row['exists']=True;row['lines']=len(text.splitlines())
    row['headings']=[{'line':i+1,'heading':s} for i,s in enumerate(text.splitlines()) if s.startswith('#')]
    if p.suffix=='.json':
        obj=json.loads(text);row['jsonRootKeys']=list(obj) if isinstance(obj,dict) else {'listCount':len(obj)}
    inventory.append(row)
put('reading-input-identities.json',inventory)
manual=(ROOT/'docs/plan/MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_text(encoding='utf8')
original=(ROOT/'docs/plan/REQUIREMENTS-TRACEABILITY.md').read_text(encoding='utf8')
reqs=[]
ledger=load('qa/mock-led-executor-20261016/completion-contract.json')['leaves']
byid={r['leafId']:r for r in ledger}
for i,line in enumerate(original.splitlines()):
    m=re.match(r'\|\s*((?:OWN|SYS)-\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|',line)
    if m:
        ident,name,outcome,evidence=m.groups();e=byid.get(ident)
        reqs.append({'id':ident,'originalRequirement':name,'source':'docs/plan/REQUIREMENTS-TRACEABILITY.md','line':i+1,'plannedOutcome':outcome,'requiredEvidence':evidence,'executorName':e.get('name') if e else None,'identityPreserved':bool(e and e.get('name')==name),'currentVerdict':'OPEN_FULL_ACCEPTANCE','evidence':'node-tests.tap; current report findings F01-F10; evidence layers remain separate'})
put('original-35-current.json',reqs)
steps=load('qa/plan-semantic-audit-20261016/original-96-crosswalk.json')
stepText=(ROOT/'docs/plan/COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md').read_text(encoding='utf8')
for r in steps:
    r['currentTextPresent']=f"{r['originalNumber']}. {r['action']}" in stepText
    r['currentImplementationVerdict']='OPEN_FULL_ACCEPTANCE'
    r['currentEvidence']='Source inventory, fresh tests/browser/art/package review; see report F01-F10. No claim that a test count closes the step.'
put('original-96-current.json',steps)
groups={}
for prefix,n in [('M',30),('J',18),('G',16)]:
    source=manual if prefix in ['M','J'] else stepText
    rows=[]
    for i in range(1,n+1):
        ident=f'{prefix}{i:02}';matches=list(re.finditer(r'^### '+ident+r'\b[^\n]*',source,re.M))
        if matches:
            start=matches[0].start();end=source.find('\n### ',matches[0].end());end=end if end>=0 else len(source)
            section=source[start:end]
        else:
            matches=list(re.finditer(r'^\| '+ident+r' \|[^\n]*',source,re.M));section=matches[0].group(0) if matches else ''
        rows.append({'id':ident,'sourceAssertion':section,'currentResult':'OPEN_FULL_ACCEPTANCE','executorResult':byid.get(ident,{}).get('result'),'evidenceRule':'Use matching current state and all mandatory subcases; test/source presence is bounded evidence only.'})
    groups[prefix]=rows;put(prefix+'-current-coverage.json',rows)
oldScenes=load('qa/mock-led-executor-20261016/scene-registration.json')['scenes'];currentScenes=[]
selection=load('src/data/reviewed-source-selection.json');modes=load('src/data/mode-scenes.json')
for r in oldScenes:
    mode=r['mode'];age=r['ageName'];idx=r['ageIndex'];path=f'assets/derivatives/mock-led-20261016/kingdom/kingdom-{age}-ground.png' if mode=='kingdom' else modes[mode][idx]
    current=identity(ROOT/path);old=r['displayedSource'];currentScenes.append({'mode':mode,'age':age,'current':current,'oldDisplayed':old,'sourceStillMatches':current['sha256']==old.get('sha256'),'verdict':'OPEN_PHYSICAL_FIT_UNPROVED','reason':'Generator uses desired geometry/gradient radius, not full native feature polygons and actual swept actor footprints. Contact PASS is hardcoded.'})
put('scene-32-current.json',currentScenes)
journeys=load('qa/mock-led-executor-20261016/journeys.json')
put('journey-evidence-audit.json',{'producerSummary':journeys['summary'],'classifications':dict(collections.Counter(r['classification'] for r in journeys['journeys'])),'unverifiedSubcases':[s['subcaseId'] for r in journeys['journeys'] for s in r['mandatorySubcases'] if s['result']!='PASS'],'freshNatural':'New campaign, enter Kingdom, pay 25 wood/15 stone for P01 lumber, ordinary completion, income, save/reload; not complete J01/J02/J18.','freshFixture':'Future resource/gear setup, real UI seven choices/ACK_FUTURE no-reward and reload; six-slot functional test and current worn pixels.','requiredOriginalAssertionCounts':{r['id']:len(re.findall(r'^\d+\.',r['sourceAssertion'],re.M)) for r in groups['J']}})
mechanics=load('qa/mock-led-executor-20261016/mechanics-coverage.json')
put('mechanics-assertion-audit.json',{'categoryCount':len(mechanics['categories']),'rows':sum(len(x.get('rows',[])) for x in mechanics['categories']),'generatorRunsAssertions':False,'classification':'descriptive inventory; no current numeric observed outputs or natural command trace','requiredSource':'manual A06 all eight numbered categories; J01-J18; full adopted data/equations','fullClosure':'UNVERIFIED','freshTests':'162 Node + one redirected stress fixture PASS, classifications bounded. Stress fixture injects supplies/skills/claims/clears and forces terminal loss.'})
put('scope-summary.json',{'originalRequirements':len(reqs),'originalSteps':len(steps),'stepTextFound':sum(r['currentTextPresent'] for r in steps),'mockTargets':len(groups['M']),'journeys':len(groups['J']),'GContracts':len(groups['G']),'scenes':len(currentScenes),'classKitRows':32,'slotDecisionsRequired':192,'executorLedgerCounts':dict(collections.Counter(r['result'] for r in ledger)),'originalRequirementIdsAbsentFromExecutor':[r['id'] for r in reqs if r['executorName'] is None],'manualHash':identity(ROOT/'docs/plan/MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md'),'executorHash':identity(ROOT/'docs/plan/ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt')} )
print(json.dumps(load('qa/independent-verification-20261017/scope-summary.json'),indent=2))
