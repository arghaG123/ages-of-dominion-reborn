import json, hashlib, re, sys, collections, datetime
from pathlib import Path
ROOT=Path('C:/dev/ages-of-dominion-reborn')
QA=Path(__file__).resolve().parent
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def dump(n,x): (QA/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def summary(v):
    if isinstance(v,list): return {'count':len(v),'sample':v[:2]}
    if isinstance(v,dict): return {k:summary(x) if isinstance(x,(dict,list)) else x for k,x in v.items() if k not in ['repairDecisions','sourceHashes','raw','inlineData']}
    return v
if __name__=='__main__':
    print('Python',sys.version)
    for owner in ['environment','actors']:
        base=f'qa/image-vertex-repair-20261009/{owner}'
        c=read(base+'/checkpoint.json')
        print(owner,'checkpoint',json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in c.items() if k not in ['repairDecisions','sourceHashes','budgetSnapshot']})[:6000])
        path='docs/plan/'+('ENVIRONMENT-ART' if owner=='environment' else 'ACTORS-EQUIPMENT')+'-VERTEX-REPAIR-INTERFACE-2026-10-09.json'
        i=read(path)
        print(owner,'interface keys',[(k,len(v) if isinstance(v,(dict,list)) else v) for k,v in i.items() if k!='repairDecisions'])
        rows=i.get('rows',i.get('artifacts',[]))
        print('row keys',list(rows[0]) if rows else None,'sample',json.dumps(rows[0] if rows else {})[:8000])
        print('statuses',collections.Counter(r.get('status',r.get('technicalStatus')) for r in rows))
    for p in ['docs/plan/image-production/budget-ledger.json','docs/plan/image-production/reconciled-accounting-ledger.json']:
        j=read(p); print('budget',p,json.dumps({k:summary(v) for k,v in j.items() if k not in ['reservations','notes','reconciliationTrail']})[:6500]); print('trail',json.dumps(j.get('reconciliationTrail')))
