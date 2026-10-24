from pathlib import Path
import hashlib,json,subprocess,re,collections,sys,datetime
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(n,v): (OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
def protected():
    roots=['src','assets','scripts','tests','android/app/src','android/gradle','design-preview/generated','docs/plan/image-production']
    paths=set()
    for r in roots:
        paths.update(p for p in (ROOT/r).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update(p for p in [ROOT/'index.html',ROOT/'package.json',ROOT/'package-lock.json',ROOT/'android/gradlew',ROOT/'android/gradlew.bat'] if p.exists())
    return {p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(paths)}
def snapshot():
    put('protected-before.json',protected())
    put('git-before.json',{'status':subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
def evidence():
    base=ROOT/'qa/mock-led-executor-20261016'
    inventory={}
    for p in base.rglob('*'):
        if p.is_file(): inventory[p.relative_to(ROOT).as_posix()]={'bytes':p.stat().st_size,'sha256':digest(p)}
    put('executor-evidence-identity.json',inventory)
    ledger=json.loads((base/'completion-contract.json').read_text(encoding='utf-8-sig'))
    put('ledger-current-copy.json',ledger)
    def leaves(x):
        if isinstance(x,dict):
            if 'leafId' in x and 'result' in x: yield x
            for v in x.values():yield from leaves(v)
        elif isinstance(x,list):
            for v in x:yield from leaves(v)
    rows=list(leaves(ledger));print('LEDGER',len(rows),dict(collections.Counter(r['result'] for r in rows)))
    print('PASS',json.dumps([r for r in rows if r['result']=='PASS'],ensure_ascii=False))
    summary={}
    for name in ['body-kit-gear-matrix','role-clip-matrix','scene-registration','style-review','journeys','viewport-review','remaining','storage-growth','storage-ordering','mechanics-coverage','balance-recovery','performance','package-check']:
        p=base/(name+'.json');x=json.loads(p.read_text(encoding='utf-8-sig'))
        summary[name]={'keys':list(x) if isinstance(x,dict) else 'list','top':{k:v for k,v in x.items() if not isinstance(v,(list,dict))} if isinstance(x,dict) else {},'counts':{k:len(v) for k,v in x.items() if isinstance(v,list)} if isinstance(x,dict) else {}}
    put('executor-summary.json',summary);print(json.dumps(summary,ensure_ascii=False))
    refs=[]
    for r in rows:
        for p in re.findall(r'(?:qa|assets|src|tests|docs)/[\w./-]+',json.dumps(r)):
            p=p.rstrip('.')
            refs.append({'leaf':r['leafId'],'status':r['result'],'path':p,'exists':(ROOT/p).exists()})
    put('ledger-evidence-paths.json',refs)
    print('MISSING PASS REFS',json.dumps([x for x in refs if x['status']=='PASS' and not x['exists']]))
if __name__=='__main__':
    if sys.argv[1]=='snapshot':snapshot()
    elif sys.argv[1]=='evidence':evidence()
    elif sys.argv[1]=='compare':
        before=json.loads((OUT/'protected-before.json').read_text());after=protected();put('protected-after.json',after)
        changes=[{'path':k,'before':before.get(k),'after':after.get(k)} for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)]
        put('protection-result.json',{'before':len(before),'after':len(after),'changes':changes});print('PROTECTION',len(before),len(after),'changed',len(changes))
