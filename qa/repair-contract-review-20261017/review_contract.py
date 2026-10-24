from pathlib import Path
import hashlib,json,re,sys,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PROMPT=ROOT/'docs/plan/ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt'
ORIGINAL=ROOT/'docs/plan/ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt'
DELIM=b'===== BEGIN UNMODIFIED ORIGINAL AUTHORITATIVE COMPLETE EXECUTOR FILE =====\n'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def protected():
    baseline=json.loads((ROOT/'qa/independent-verification-20261017/protected-after.json').read_text(encoding='utf8'))
    return {rel:{'bytes':(ROOT/rel).stat().st_size,'sha256':sha(ROOT/rel)} if (ROOT/rel).is_file() else None for rel in baseline}
if sys.argv[1]=='before':
    put('protected-before.json',protected())
    put('prompt-before-identity.json',{'path':PROMPT.relative_to(ROOT).as_posix(),'bytes':PROMPT.stat().st_size,'sha256':sha(PROMPT),'originalSHA256':sha(ORIGINAL),'manualSHA256':sha(ROOT/'docs/plan/MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md'),'dateIST':'2026-10-17','note':'Prompt semantic revision only; preceding game audit results remain dated evidence.'})
    print('Snapshot saved')
elif sys.argv[1]=='verify':
    before=json.loads((OUT/'protected-before.json').read_text(encoding='utf8'));after=protected();put('protected-after.json',after)
    changes=[p for p in before if before[p]!=after[p]]
    prompt=PROMPT.read_bytes();original=ORIGINAL.read_bytes()
    owner=(ROOT/'docs/plan/OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md').read_bytes()
    retained=prompt.split(b'===== RETAINED 17 OCTOBER INDEPENDENT REPAIR PREFACE =====\n',1)[1]
    reconstructed=retained.split(DELIM,1)[0]+DELIM+original
    prior=json.loads((OUT/'prompt-before-identity.json').read_text(encoding='utf8'))
    checks={'originalEmbeddedExactly':prompt.split(DELIM,1)[1]==original,'ownerContractEmbeddedExactly':owner in prompt,'oneOriginalDelimiter':prompt.count(DELIM)==1,'priorRepairPrefaceAndScopeRetainedExactly':hashlib.sha256(reconstructed).hexdigest()==prior['sha256']}
    requirements={
        'U01':'icon plus amount', 'U02':'GameIconButton', 'U03':'No permanent label', 'U04':'equipment',
        'U05':'product copy', 'U06':'no-wall', 'U07':'No broad blur', 'U08':'source-bound geometry',
        'U09':'foreground occlusion', 'U10':'17', 'U11':'All eight ages', 'U12':'Gate A',
        'U13':'Gate B', 'U14':'Gate C', 'U15':'$100', 'U16':'checkpoint',
    }
    text=prompt.decode('utf8')
    ownerText=owner.decode('utf8')
    sections={m.group(1):ownerText[m.start():(re.search(r'^## U\d\d',ownerText[m.end():],re.M).start()+m.end() if re.search(r'^## U\d\d',ownerText[m.end():],re.M) else len(ownerText))] for m in re.finditer(r'^## (U\d\d)\b',ownerText,re.M)}
    rows=[{'id':k,'requiredPhrase':v,'presentInOwnSection':v in sections.get(k,''),'present':v in sections.get(k,'')} for k,v in requirements.items()]
    previous=json.loads((ROOT/'qa/independent-verification-20261017/scope-summary.json').read_text(encoding='utf8'))
    report={'dateIST':'2026-10-17','generatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promptBytes':len(prompt),'promptSHA256':sha(PROMPT),'originalSHA256':sha(ORIGINAL),'checks':checks,'ownerAssertions':rows,'preservedScope':previous,'protectedCount':len(before),'protectedChanges':changes,'limitation':'Structural/source-preservation checks of documentation. No new game/runtime/provider/device acceptance.'}
    sourceChecks=[]
    for rel,terms in {'src/client/main.js':['node.textContent = label','name.className = \'res-name\'','span.append(name, amount)','title.textContent = `${slotName[slot]}','button(name[0].toUpperCase()'],'src/client/game.css':['#resources span {','#resources span .res-name {','min-height: 48px;']}.items():
        p=ROOT/rel;lines=p.read_text(encoding='utf8').splitlines()
        for term in terms:sourceChecks.append({'path':rel,'sha256':sha(p),'needle':term,'lines':[i+1 for i,s in enumerate(lines) if term in s]})
    selection=json.loads((ROOT/'src/data/reviewed-source-selection.json').read_text(encoding='utf8'))
    stone=selection['kingdomTerrain']['stone'];p=ROOT/stone['displayFile']
    put('current-source-confirmation.json',{'sourceChecks':sourceChecks,'kingdomGeometry':json.loads((ROOT/'src/data/implementation-contract.json').read_text(encoding='utf8'))['geometry']['kingdom'],'stoneDisplayed':{'file':stone['displayFile'],'actualSHA256':sha(p),'declaredSHA256':stone.get('displaySHA256'),'catalogHashMatches':sha(p)==stone.get('displaySHA256'),'displayNote':stone.get('displayNote'),'observed':'Soft blotches and a visibly separate repeated fence course inspected directly in current ground/built native PNGs. Exact current repair recipe not inferred from historical helper names.'}})
    put('verification.json',report)
    links=[]
    for rel in ['docs/plan/OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md','docs/plan/REPAIR-PROMPT-ARCHITECTURE-AND-QA-REVIEW-2026-10-17.md']:
        p=ROOT/rel
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
            if not link.startswith(('http:','https:','#')):links.append({'source':rel,'link':link,'exists':(p.parent/link.split('#')[0]).resolve().exists()})
    report['missingLinks']=[r for r in links if not r['exists']]
    put('verification.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ['preservedScope','ownerAssertions']},indent=2))
    assert all(checks.values()) and all(r['present'] for r in rows) and not changes and not report['missingLinks']
