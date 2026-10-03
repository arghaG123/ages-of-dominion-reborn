"""Local reproducible contract/production benchmark. No cloud or inferred visual approval."""
from pathlib import Path
import copy, hashlib, json, math, sys
import importlib.util
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageChops
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'qa/benchmark'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def point(g,x,y): a,b,c,d,e,f=g['worldToSource']; return (a*x+c*y+e,b*x+d*y+f)
def bounds_valid(g):
    w,h=g['sourceSize']
    return all(24<=px<=w-24 and 24<=py<=h-24 for px,py in [point(g,x,y) for x,y in [(0,0),(g['cols'],0),(0,g['rows']),(g['cols'],g['rows'])]])
def road_hits_pad(g):
    pads=Image.new('1',tuple(g['sourceSize'])); roads=pads.copy(); dp=ImageDraw.Draw(pads); dr=ImageDraw.Draw(roads)
    for site in g['sites']:
        if not site['id'].startswith('P'): continue
        x,y,w,h=site['rect']; dp.polygon([point(g,x,y),point(g,x+w,y),point(g,x+w,y+h),point(g,x,y+h)],fill=1)
    for road in g['roads']: dr.line([point(g,x,y) for x,y in road],fill=1,width=16)
    return ImageChops.logical_and(pads,roads).getbbox() is not None
def reachable(g,start):
    blocked={tuple(c) for c in g['blocked']+g.get('obstacles',[])}
    for bridge in g['bridges']: blocked -= {tuple(c) for c in bridge['cells']}
    for site in g['sites']:
        x,y,w,h=site['rect']; blocked |= {(c,r) for c in range(g['cols']) for r in range(g['rows']) if x<=c+.5<x+w and y<=r+.5<y+h}
    if start in blocked or not(0<=start[0]<g['cols'] and 0<=start[1]<g['rows']): return set()
    seen={start}; todo=[start]
    while todo:
        c,r=todo.pop()
        for q in [(c+1,r),(c-1,r),(c,r+1),(c,r-1)]:
            if 0<=q[0]<g['cols'] and 0<=q[1]<g['rows'] and q not in blocked and q not in seen: seen.add(q); todo.append(q)
    return seen
def deployment_valid(g):
    occupied=set(); blocked={tuple(p) for p in g['blocked']+g.get('obstacles',[])}
    for bridge in g['bridges']: blocked-={tuple(c) for c in bridge['cells']}
    for id,(x,y) in g['anchors'].items():
        cell=(math.floor(x),math.floor(y))
        if cell in occupied or cell in blocked or not(0<=x<g['cols'] and 0<=y<g['rows']): return False
        occupied.add(cell)
        if id=='commander':
            if (x,y)!=(.5,9.5): return False
        else:
            rx,ry,rw,rh=g['deployment']['allied' if id.startswith('L') else 'enemy']
            if not(rx<=x<rx+rw and ry<=y<ry+rh): return False
    return len(occupied)==7
def footprints_valid(g):
    rects=[s['rect'] for s in g['sites']]
    for x,y,w,h in rects:
        if w<=0 or h<=0 or x<0 or y<0 or x+w>g['cols'] or y+h>g['rows']: return False
    for i,(x,y,w,h) in enumerate(rects):
        for xx,yy,ww,hh in rects[i+1:]:
            if max(x,xx)<min(x+w,xx+ww) and max(y,yy)<min(y+h,yy+hh): return False
    return True
def defense_valid(g):
    lane=g['lane']; occupied={tuple(p) for p in lane}
    return len(occupied)==len(lane) and all(0<=x<g['cols'] and 0<=y<g['rows'] for x,y in lane) and all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(lane,lane[1:])) and all(not(x<=c+.5<x+w and y<=r+.5<y+h) for x,y,w,h in [s['rect'] for s in g['sites']] for c,r in lane)
def main():
    contract=read(ROOT/'docs/plan/IMPLEMENTATION-CONTRACT.json'); checks=[]
    def check(id,passed,details): checks.append({'id':id,'type':'AUTOMATED','status':'PASS' if passed else 'FAIL','details':details})
    frozen=read(ROOT/'docs/plan/GAME-DATA-REFERENCE.json'); tables=frozen['originalTables']; extensions=frozen['productExtensions']
    expected={'ages':[r['n'].split()[0].lower() for r in extensions['AGES_ALL']['value']],'resources':[r['k'] for r in tables['RES']['value']],'classes':list(extensions['CLASSES_ALL']['value']),'skills':list(tables['SKILLS']['value']),'spells':list(tables['SPELLS']['value']),'creatures':list(tables['CREATURES']['value']),'flyers':[k for k,v in tables['CREATURES']['value'].items() if v.get('fly')]}
    def inventory_valid(c): return all(set(c[k])==set(v) and len(c[k])==len(set(c[k])) for k,v in expected.items()) and c['slots']==['helm','weapon','offhand','armor','boots','accessory']
    check('inventory',inventory_valid(contract),'Exact unique IDs compared to frozen tables/extensions; pixel semantics manual')
    bad=copy.deepcopy(contract); bad['classes'][1]=bad['classes'][0]; check('fixture-reject-duplicate-identities',not inventory_valid(bad),'Same inventory validator rejects duplicate class with count8')
    g=contract['geometry']['kingdom']; pads=[s for s in g['sites'] if s['id'].startswith('P')]
    check('kingdom18sites',len(g['sites'])==18 and len(pads)==17 and sum(p['region']=='upper' for p in pads)==9 and sum(p['region']=='lower' for p in pads)==8,'Separate upperHall +9upper/8lowerpads; Walls separate')
    check('road-footprint-clearance',not road_hits_pad(g),'Rendered16px road strip cannot intrude into build pads')
    for mode,g in contract['geometry'].items():
        check(mode+'-source-bounds',bounds_valid(g),'All world boundary corners have24px source margin')
        check(mode+'-guide-hash',digest(ROOT/g['guide'])==g['guide_sha256'],'Exact immutable registration source')
        a,b,c,d,e,f=g['worldToSource']; check(mode+'-invertible',abs(a*d-b*c)>1e-8,'Projection supports exact inverse picking')
        check(mode+'-footprints',footprints_valid(g),'Positive, nonoverlapping site footprints insideworld')
        for vw,vh in contract['viewports']:
            scale=min(vw/g['sourceSize'][0],vh/g['sourceSize'][1]); off=((vw-g['sourceSize'][0]*scale)/2,(vh-g['sourceSize'][1]*scale)/2)
            x,y=point(g,g['cols']/2,g['rows']/2); sx,sy=x*scale+off[0],y*scale+off[1]
            check(f'{mode}-fit-{vw}x{vh}',0<=sx<vw and 0<=sy<vh,'One sharedcamera fit; phone48px picking remains rendered check')
    adv=contract['geometry']['adventure']; seen=reachable(adv,(8,8)); targets=[tuple(s['approach']) for s in adv['sites']]+[(3,8),(7,9),(14,5),(10,4),(12,4),(10,5)]
    check('adventure-corridors',all(t in seen for t in targets),'All sixsite approaches,fourpickups,twoguards reached through legal stone crossing')
    tac=contract['geometry']['tactical']; check('tactical-deployment',deployment_valid(tac),'Sixstack slots pluscommander0,9 distinct unblocked/legal zones')
    defense=contract['geometry']['defense']; check('defense-lane',defense_valid(defense),'Fixed9x15 contiguouslane insideworld, unique and no towerpad collision')
    # Mutation fixtures prove checks can reject the failures they claim to detect.
    bad=copy.deepcopy(contract['geometry']['kingdom']); bad['worldToSource'][5]=-200
    check('fixture-reject-clipped-map',not bounds_valid(bad),'Negative fixture projects ground outside source')
    bad=copy.deepcopy(contract['geometry']['kingdom']); bad['roads']=[[[6.7,1],[6.7,5]]]
    check('fixture-reject-pad-road',road_hits_pad(bad),'Negative fixture road strip crosses P03')
    bad=copy.deepcopy(tac); bad['anchors']['L2']=[1.5,4.5]
    check('fixture-reject-illegal-deployment',not deployment_valid(bad),'Same deployment validator rejects previousdocument illegalexample')
    bad=copy.deepcopy(defense); bad['sites'][0]['rect']=[2,12,.8,.8]; check('fixture-reject-pad-on-lane',not defense_valid(bad),'Same lane validator rejects illegal towerpad collision')
    budget=read(ROOT/'docs/plan/image-production/budget-ledger.json')
    ledger_ids={x['id'] for x in budget['batches']}
    lock_path=ROOT/'docs/plan/image-production/active-batch.lock.json'
    lock=read(lock_path) if lock_path.exists() else {}
    lock_extra=float(lock.get('reservedUSD') or 0) if lock.get('batch_id') not in ledger_ids else 0
    holds=budget['historicalMock']['conservativeReservation']+sum(x['reservedUSD'] for x in budget['batches'])+lock_extra
    trail=budget.get('reconciliationTrail') or {}
    measured=trail.get('measuredCompletedUsageTokens') or {}
    tariff=trail.get('standardTariff') or {}
    invoices_unknown=budget.get('billedTotal') is None and all(batch.get('billedTotal') is None for batch in budget['batches'])
    holds_retained=all(batch.get('holdRetained') is True and batch.get('reservedUSD', 0) > 0 for batch in budget['batches'])
    input_tokens=measured.get('inputTokens')
    output_tokens=measured.get('outputTokens')
    rate_ok=tariff.get('inputPer1M')==0.5 and tariff.get('imageOutputPer1M')==60
    if invoices_unknown and holds_retained and rate_ok and isinstance(input_tokens, int) and isinstance(output_tokens, int) and input_tokens > 0 and output_tokens > 0:
        standard=input_tokens*tariff['inputPer1M']/1e6+output_tokens*tariff['imageOutputPer1M']/1e6
        protected=round(standard*1.15+budget['historicalMock']['conservativeReservation']+budget['safetyReserve'], 3)
    else:
        protected=holds+budget['safetyReserve']
    historical=holds+budget['safetyReserve']
    check('budget-committed',protected<=budget['target']==60 and protected<=budget['hardCap']==80 and invoices_unknown and holds_retained and historical>=119,f'Evidence-bounded protected exposure {protected} USD. Historical holds {holds} USD plus the safety reserve remain {historical} USD and are not erased. Invoices stay unknown and are not zero. Lock extra {lock_extra}.')
    loader=importlib.util.spec_from_file_location('vertex',ROOT/'scripts/vertex-production.py'); provider=importlib.util.module_from_spec(loader); loader.loader.exec_module(provider)
    bad=copy.deepcopy(budget); bad['batches']=[{'id':'exhausted','reservedUSD':70,'billedTotal':None}]; rejected=False
    try: provider.validate_paid(read(ROOT/'docs/plan/image-production/batch-01-manifest.json'),bad)
    except RuntimeError: rejected=True
    check('fixture-reject-overbudget',rejected,'Real paid validator rejects overspend without network')
    for index in [1,2]:
        m=read(ROOT/f'docs/plan/image-production/batch-{index:02}-manifest.json'); items=m['items']
        check(f'batch{index}-useful30',len(items)==30 and len({i['id'] for i in items})==30 and all(i['requestedOutputs']==1 for i in items),'Unique useful output positions, no paid filler')
        check(f'batch{index}-pricebound',m['reservedUSD']>=30*m['maxOutputTokens']*30/1e6+30*m['inputTokenUpperBoundPerRequest']*.25/1e6,'Token ceiling charged conservatively atimage rate, plus overhead margin')
        for item in items:
            guide_hash=item.get('guideSHA256') or ''
            snapshot=ROOT/'docs/plan/image-production/historical-snapshots'/f'{guide_hash}.png'
            guide_ok=(not item.get('guide')) or digest(ROOT/item['guide'])==guide_hash or (snapshot.exists() and digest(snapshot)==guide_hash)
            tag=(guide_hash or item['promptSHA256'])[:12]
            check(m['id']+':'+item['id']+':'+tag+'-provenance',hashlib.sha256(item['prompt'].encode()).hexdigest()==item['promptSHA256'] and guide_ok,'Prompt and guide binding; historical snapshot satisfies a replaced shared guide without rewriting it')
            if 'registration' in item:
                matrix=contract['geometry'][item['mode']]['worldToSource']; axes=item['registration']['worldAxesSource']; check(m['id']+':'+item['id']+':'+tag+'-camera-axes',all(abs(axes[i]/axes[0]-matrix[i]/matrix[0])<1e-7 for i in range(4)),'Object base shares mode camera axes')
        if index==2:
            skills=[i['id'].removeprefix('skill-') for i in items if i['kind']=='skill']; spells=[i['id'].removeprefix('spell-') for i in items if i['kind']=='spell']
            check('exact-ability-semantics',skills==contract['skills'] and spells==contract['spells'],'Nine and eight unique named prompts; generated glyph semantics manual')
            bad=copy.deepcopy(contract); bad['skills'][-1]=bad['skills'][0]; check('fixture-reject-duplicate-semantics',not inventory_valid(bad),'Shared validator rejects duplicate abilityID')
    assets=[]
    for file in (ROOT/'assets/production').glob('*/collection-report.json') if (ROOT/'assets/production').exists() else []:
        report=read(file)
        for output in report['outputs']:
            path=ROOT/output['file']; passed=digest(path)==output['sha256']
            with Image.open(path) as im: im.load(); passed &= list(im.size)==[output['width'],output['height']]
            check(file.parent.name+':'+output['id']+':'+output['sha256'][:12]+'-decode-hash',passed,'Decodedoriginal and exact SHA256; no approval inferred')
            assets.append({'id':output['id'],'batch':file.parent.name,'sourceSHA256':output['sha256'],'technical': 'PASS' if passed else 'FAIL','alpha': 'PASS' if not output['requiredAlpha'] or output['alpha'] else 'FAIL_REQUIRED_PROCESSING','content':'UNVERIFIED','composite':'UNVERIFIED','runtimeApproved':False})
    import review_gates
    joined=review_gates.evaluate()
    by_key={(r['batch'], r['id'], r['sourceSHA256']): r for r in joined['rows']}
    for asset in assets:
        row=by_key.get((asset['batch'], asset['id'], asset['sourceSHA256']))
        if row is None:
            asset['gates']={name: 'UNVERIFIED' for name in review_gates.GATES}
            asset['gates']['technical']=asset['technical']
            asset['content']='UNVERIFIED'
            asset['reviewBinding']='MISSING_REVIEW'
        elif not row['hashMatch']:
            asset['gates']={name: 'REJECTED_STALE_HASH' for name in review_gates.GATES}
            asset['content']='REJECTED_STALE_HASH'
            asset['reviewBinding']='STALE'
        else:
            asset['gates']=row['gates']
            asset['content']=row['gates']['sourceContent']
            asset['composite']=row['gates']['composite']
            asset['runtimeApproved']=False
            asset['ownerAcceptance']=row['gates']['ownerAcceptance']
            asset['reviewBinding']=row.get('reviewSource', 'HISTORICAL')
            asset['artworkReadyForUse']=row.get('artworkReadyForUse', {'status': 'UNVERIFIED'})
    check('review-hash-fresh', len(joined['stale'])==0 and all(r['hashMatch'] for r in joined['rows']), 'Verifier rows match current source bytes or they are rejected')
    snapshot_path=ROOT/'qa/recovery-executor-20261003/collection-snapshot.json'
    current=sorted((asset['batch'], asset['id'], asset['sourceSHA256']) for asset in assets)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    previous=read(snapshot_path)['rows'] if snapshot_path.exists() else []
    previous_keys={(row['batch'], row['id'], row['sourceSHA256']) for row in previous}
    current_keys=set(current)
    check('dynamic-collection-coverage', len(assets)>0 and len(current_keys)==len(current) and all(asset['technical']=='PASS' for asset in assets) and current_keys >= previous_keys, 'Discovered collection rows are hash-checked against the saved snapshot. The count is not fixed at 240')
    if not snapshot_path.exists() and all(asset['technical']=='PASS' for asset in assets):
        snapshot_path.write_text(json.dumps({'rows':[{'batch':b,'id':i,'sourceSHA256':s} for b,i,s in current]}, indent=2)+'\n', encoding='utf-8')
    check('missing-review-unverified', all(a['content']=='UNVERIFIED' and 'REJECTED_STALE_HASH' not in a['gates'].values() for a in assets if a.get('reviewBinding')=='COLLECTION_ONLY'), 'A source with no historical review is UNVERIFIED, not a stale hash')
    check('hall-interior-intact', review_gates.interior_integrity()['pass'], 'Hall v3 keeps v1 roof and wall interiors opaque')
    check('bounded-ui-preserved', review_gates.preserved_ui()['pass'], 'Food, Wood, Stone and Offense v2 files stay at their reviewed hashes')
    check('review-gates-separate', all(r['runtimeApproved'] is False and r['ownerAccepted'] is False and r['gates']['runtime']!='PASS' and r['gates']['ownerAcceptance']!='PASS' for r in joined['rows']) and any(r['gates']['sourceContent']=='PASS' for r in joined['rows']), 'Source-content acceptance does not set runtime or owner approval')
    check('review-stale-fixture', review_gates.stale_fixture(), 'A mismatched source hash cannot inherit a PASS review')
    selected={s['id']: s for s in joined['selected']}
    check('candidate-townhall-batch03', selected['townhall-stone']['acceptedForRecovery'] and selected['townhall-stone']['preferredReviewCandidateKey'].startswith('production-03-20261003:'), 'Hall selection is the reviewed batch 03 candidate, not the batch 01 path')
    check('candidate-offense-batch03', selected['skill-offense']['acceptedForRecovery'] and selected['skill-offense']['preferredReviewCandidateKey'].startswith('production-03-20261003:'), 'Offense selection is the reviewed batch 03 plaque')
    check('candidate-resources-batch01', all(selected['resource-'+name]['acceptedForRecovery'] and selected['resource-'+name]['preferredReviewCandidateKey'].startswith('production-01-20261003:') for name in ('food','wood','stone','gold')), 'The four resources stay on their reviewed batch 01 sources')
    delivery_ledger=ROOT/'assets/delivery/stone-starter-20261003/gate-ledger.json'
    check('delivery-ledger-present', delivery_ledger.exists(), 'First delivery derivatives record source and output hashes')
    if delivery_ledger.exists():
        delivery=read(delivery_ledger)
        for item in delivery['assets']:
            source_ok=digest(ROOT/item['sourceFile'])==item['sourceSHA256']
            derivative_ok=(ROOT/item['derivative']).exists() and digest(ROOT/item['derivative'])==item['derivativeSHA256']
            check(item['batch']+':'+item['id']+':'+item['derivativeSHA256'][:12]+'-delivery-hash', source_ok and derivative_ok, 'Derivative stays bound to the reviewed source hash')
    manual=[{'id':id,'type':'MANUAL','status':'UNVERIFIED','requiredEvidence':evidence} for id,evidence in [('era-authenticity','Eachoutput against era matrix; Stone no medieval structures, Future transformed wholekit'),('age-landmark-camera','Eightterrains share exact terrace/river/crossing/perimeter/padmap registration; inspect actual pixels'),('hero-unit-identity','Face/gear/role/facing master comparison'),('content-count-semantics','Exact visible9skills8spells6gear4resources, no duplicates/bakedlabels'),('pivot-shadow-scale','Measured source pivots,groundfootprints,contactshadow and camera in composed scene'),('alpha-matte','Edgehalo/internal holes/translucent shadow preserve object; magenta JPEG cannotpass'),('composite-reference','Stone sparse/Medieval grown and3mode scoped landscape paired referencecaptures'),('hud-touch-contrast','18px4resource28rail; noneTactical/Defense;48pxhitbounds safeinsets and contrast measured'),('animation-gait','Articulated foot/hoof contact and attachment clip-extremes'),('physical-android','Real isolatedAPK zeropermissions/network and60fpsdenseSiege'),('whole-campaign','Natural fulljourney and all8ages5Waroptions withoutfixture grants')]]
    report={'version':1,'at':datetime.now(timezone.utc).isoformat(),'automated':checks,'manual':manual,'assets':assets,'automatedStatus':'FAIL' if any(c['status']=='FAIL' for c in checks) else 'PASS','visualStatus':'UNVERIFIED','productApproved':False}
    REPORT.mkdir(parents=True,exist_ok=True)
    archive=REPORT/'report-before-dynamic-discovery-20261003.json'
    if (REPORT/'report.json').exists() and not archive.exists(): archive.write_bytes((REPORT/'report.json').read_bytes())
    (REPORT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Reproducible design benchmark','','Automated '+report['automatedStatus']+'; manual/pixel/composite/device review UNVERIFIED. Product approved: false.','','|Check|Type|Status|Evidence|','|---|---|---|---|']+['|'+c['id']+'|'+c['type']+'|'+c['status']+'|'+c.get('details',c.get('requiredEvidence',''))+'|' for c in checks+manual]
    (REPORT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'automated':report['automatedStatus'],'checks':len(checks),'failures':[c['id'] for c in checks if c['status']=='FAIL'],'manualUnverified':len(manual),'assetCount':len(assets)}))
    sys.exit(1 if report['automatedStatus']=='FAIL' else 0)
if __name__=='__main__': main()
