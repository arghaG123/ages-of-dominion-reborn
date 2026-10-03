from pathlib import Path
import copy, json, importlib.util
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
g=module('gates_probe',ROOT/'scripts/review_gates.py')
d=load(ROOT/'assets/delivery/stone-starter-20261003/gate-ledger.json')
v=load(ROOT/'qa/delivery-20261003/visual-gates-current.json')
checks={}
def scene_probe(label,delivery,visual):
    r=g.evaluate(delivery=delivery,visual=visual)
    checks[label]={'scene':r['scene'],'outputStale':r['outputStale']}
dv=copy.deepcopy(d); vv=copy.deepcopy(v); vv['scene']['composite']='PASS'
scene_probe('baselineWithPassForProbeOnly',dv,vv)
dv=copy.deepcopy(d); vv=copy.deepcopy(v); vv['scene']['composite']='PASS'; vv['scene']['constituentSHA256']={}; vv['scene']['registrationRevision']={}
scene_probe('omittedAllConstituentsAndRegistrations',dv,vv)
dv=copy.deepcopy(d); vv=copy.deepcopy(v); vv['scene']['composite']='PASS'; dv['cameraHash']=vv['scene']['cameraHash']='obsolete-camera'; dv['contractHash']=vv['scene']['contractHash']='obsolete-contract'
scene_probe('mutuallyMatchingStaleCameraAndContract',dv,vv)
dv=copy.deepcopy(d); vv=copy.deepcopy(v); vv['scene']['composite']='PASS'; vv['scene']['evidence']=['missing-verifier-evidence.png']
scene_probe('missingVisualEvidenceFile',dv,vv)
dv=copy.deepcopy(d); vv=copy.deepcopy(v)
for item in dv['assets']:
    if item['id']=='resource-gold':
        item['artworkReadyForUse']={'status':'PASS','evidence':'missing.png','policyRevision':'stale','sizes':[18,36]}
r=g.evaluate(delivery=dv,visual=vv)
checks['unboundArtworkPass']=[x.get('artworkReadyForUse') for x in r['rows'] if x['id']=='resource-gold']
save('adversarial-gate-probes.json',checks)
print(checks)
