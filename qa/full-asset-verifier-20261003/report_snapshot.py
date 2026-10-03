"""Local verification only. Writes new diagnostic reports; never processes production assets."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, collections, importlib.util
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
inventory=read(OUT/'inventory.json')
baseline=read(ROOT/'docs/plan/image-production/full-purchase-inventory.json')
required={x['id'] for x in baseline['items']}
seen={x['id'] for x in inventory['sources']}
findings={
 'workshop-stone':'Bottom canvas clips yard/base. Recover cropped fragment only or reconstruct locally; camera and contact plane unresolved.',
 'farm-bronze':'Right canvas clips edge dressing/building. Green guide material remains. Native right-edge crop reviewed.',
 'barracks-stone':'Green guide material survives around facility; isolate material from guide and verify grounding.',
 'armory-stone':'Guide residue and ground apron need local separation; rendered facility candidate.',
 'workshop-iron':'Guide-like green ground material remains; segmentation and true contact plane needed.',
 'quarry-gunpowder':'Compound quarry and perimeter cut at source boundaries; preserve useful rock/architecture fragments. Natural quarry footprint, not silhouette rectangle.',
 'farm-industrial':'Bottom yard reaches canvas; inspect exact usable crop before registering.',
 'lumber-industrial':'Native crop confirms chimney is cut at top boundary; source cannot supply complete chimney without repair.',
 'workshop-modern':'Right courtyard reaches canvas; inspect/reconstruct only required facility extent.',
 'farm-future':'Native crop confirms greenhouse wings cut at canvas edges. Center/wings remain useful fragments, not complete standalone facility.',
 'civilian-transport-modern':'Pair of workers and one transport are present as requested. Blank unused guide slot is not a missing-request defect; green panels require separation.',
 'civilian-transport-industrial':'Worker/transport candidates present; remove green guide panels. Do not require four occupied slots for a three-subject prompt.',
 'civilian-transport-future':'Worker/transport candidates present; crop and remove guide panels. Anatomy/pivots remain unverified.',
 'troop-stone-melee':'Weapon silhouette appears spear/staff-like in overview; verify required Clubman/flint club identity before source-content PASS.',
 'troop-stone-ranged':'Native crop shows sling/stone implements and detailed figure; footing/ground island separation, camera and animation remain open.',
 'troop-bronze-melee':'Generated sword/shield infantry candidate; frozen role is Axeman. Weapon/identity needs explicit review, not filename approval.',
 'troop-medieval-heavy':'Plated foot knight is useful. Siege Knight form and any mounted requirement need explicit roster resolution; no silent renaming.',
 'troop-industrial-ranged':'Extra/duplicate weapon-like fragment visible; separate before rigging, inspect hands and intended weapon.',
 'tower-modern-splash':'Native crop shows rotary multi-barrel gun rather than obvious mortar. AOE mechanism/family requires action/art review; not automatically a finished splash tower.',
 'tower-future-arrow':'Weapon/emitter role unclear in overview; validate intended beam/projectile action without relying on label.',
 'tower-future-slow':'Beam/smoke reaches edge; extract mutable FX separately from idle tower.',
 'attacker-stone-brute':'Native foot crop confirms green guide rectangle under feet. Figure candidate; remove guide, define contact pivot and articulated rig.',
 'attacker-stone-runner':'Static leaning pose is a source figure, not running animation or rig. Verify limbs and gait contacts.'
}
wrong_heavy={
 'bronze':('Charioteer','bronze phalanx infantry'),
 'iron':('War Elephant','armored human infantry'),
 'gunpowder':('Cannon Crew','cuirassier/grenadier infantry without cannon'),
 'industrial':('Steam Walker','machine-gun shock trooper'),
 'modern':('Battle Tank','heavy-weapons infantry'),
 'future':('Hover Tank','powered-armour human juggernaut')}
critical={f'troop-{age}-heavy':f'Required {wanted}; prompt and pixels provide {got}. Wrong complete roster identity; preserve figure as possible crew/reference. Correct plan before any purchase.' for age,(wanted,got) in wrong_heavy.items()}
critical['tower-iron-splash']='Cannon-like gunpowder artillery contradicts Iron no-gunpowder era rule. Useful later-era reference; not Iron source-content PASS.'
findings.update(critical)
rows=[]
for r in inventory['sources']:
    x=dict(r)
    x['overviewReviewed']=True
    x['overviewEvidence']=[f"qa/full-asset-verifier-20261003/{r['batch']}-page{1 if r['position']<=15 else 2}.jpg"]
    crop=OUT/(r['id']+'-native-crop.png')
    if crop.exists(): x['detailEvidence']=crop.relative_to(ROOT).as_posix()
    kind=r['kind']
    default={
      'building':'Rendered structure/material candidate. Separate background, ground apron and guide marks; use physical base, depth/occlusion and shared world registration. Walls are modular kits, not one rectangular building.',
      'terrain':'Terrain/material candidate. Keep declared immutable outskirts; separate mutable objects and markers. Registered topology, clearings and crossings remain required; opaque terrain needs no alpha matte.',
      'sheet':'Requested prop/worker/construction sheet candidate. Crop requested subjects independently, validate useful positions against literal prompt and remove guide panels. Sheet count is not extracted/rigged count.',
      'troop':'Static detailed figure candidate. Roster/weapon, camera, pivots, segmentation and articulated motion need separate review; no animation proof exists.',
      'tower':'Tower structure candidate. Era, attack family and muzzle/emitter action unresolved. Separate baked aura, rings, beams and active FX from idle structure.',
      'attacker':'Static figure source candidate. Pivot, segmentation, articulated animation and lane fit unresolved.',
      'resource':'UI symbol source candidate. Judge intended pixel size, material colour and silhouette separately from world registration.',
      'skill':'UI emblem source candidate. Judge actual icon size and role readability; world footprint does not apply.',
      'spell':'UI/spell artwork candidate. Separate emblem readability from runtime spell/action/FX semantics.',
      'portrait':'Character painting source candidate. Identity/anatomy and UI/world usage separate; source painting is not an articulated actor.',
      'actor':'Character/mount source candidate. Age/identity and actual articulated gait unresolved.',
      'gear':'Gear source candidate. Material/slot identity, isolated silhouette and functional six-slot behavior separate.',
      'site':'Adventure-site source candidate. Local extraction and physical entrance/footprint/world corridor fit unresolved.'}[kind]
    x['currentOverviewStatus']='FAIL' if r['id'] in critical else 'UNVERIFIED'
    x['currentFinding']=findings.get(r['id'],default)
    x['historicalReviewPreserved']=bool(r['historicalReason'])
    if r['historicalReason']: x['currentFinding']+=' Historical hash-bound assessment: '+str(r['historicalReason'])
    if r['technical']!='PASS': raise ValueError(r['file'])
    rows.append(x)
delivery=read(ROOT/'assets/delivery/stone-starter-20261003/gate-ledger.json')
scoped={'resource-food':(18,'Food rail symbol'), 'resource-wood':(18,'Wood rail symbol'), 'resource-stone':(18,'Stone rail symbol'), 'skill-offense':(36,'Offense UI emblem at 36/64 px')}
deliveryrows=[]
for r in delivery['assets']:
    x={k:r[k] for k in ('id','batch','sourceFile','sourceSHA256','derivative','derivativeSHA256')}
    x['sourceHashMatch']=digest(ROOT/x['sourceFile'])==x['sourceSHA256']
    x['derivativeHashMatch']=digest(ROOT/x['derivative'])==x['derivativeSHA256']
    ident=x['id'];terrain=ident.startswith('kingdom-terrain')
    x['reviewPolicy']='ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03 v1; bounded use, no runtime/owner promotion'
    x['intendedUseArtwork']='PASS' if ident in scoped else 'FAIL' if ident in ['townhall-stone','resource-gold'] or terrain else 'UNVERIFIED'
    x['matte']='NOT_APPLICABLE' if terrain else 'PASS' if ident in scoped else 'FAIL' if ident=='townhall-stone' else 'UNVERIFIED'
    x['registration']='NOT_APPLICABLE' if ident in scoped or ident=='resource-gold' else 'FAIL'
    x['nativeDiagnosticQuality']='WARNING' if ident in scoped else 'FAIL' if ident in ['townhall-stone','resource-gold'] else 'UNVERIFIED'
    x['runtime']='UNVERIFIED';x['ownerAcceptance']='UNVERIFIED'
    x['evidence']=['qa/full-asset-verifier-20261003/v2-icons-intended-pixels.png'] if ident in scoped or ident=='resource-gold' else [f'qa/full-asset-verifier-20261003/{ident}-v2-full.png'] if not terrain else ['qa/recovery-correction-20261003/viewports/hall-only-1280x720.png']
    if ident in scoped:
        px,usage=scoped[ident];x['useScope']={'purpose':usage,'minimumReviewedPixels':px,'backgrounds':['#101820','#ffffff','#6e8468'],'largerExportUse':'UNVERIFIED'}
        x['reason']='Recognizable intact artwork at the specified actual-pixel UI size. Tiny native diagnostic fringes remain and are recorded, but do not block this bounded use. No world camera or rig criterion applies.'
    elif ident=='townhall-stone':x['reason']='Severe opaque roof/front loss and ghost edges. Rebuild v3 from immutable original/v1. Mask distance bug treats all opaque material as edge. Placement clips roof and lacks physical contact registration.'
    elif ident=='resource-gold':x['reason']='Magenta removal became red coin sides, visible even at intended size. Correct localized material colour; do not erase coin structure.'
    elif terrain:x['reason']='Matte not applicable. Visible flat restamped polygon pads and blurred lower river patch fail natural terrain treatment; register static/dynamic scenery and topology.'
    else:x['reason']='Building structure largely intact; tiny fringe alone is not an automatic paid-replacement reason. Local ground/plinth handling and physical base/camera registration remain unresolved.'
    deliveryrows.append(x)
scene=dict(delivery['composite']);scene['actualSHA256']=digest(ROOT/scene['file']);scene['hashMatch']=scene['actualSHA256']==scene['sha256'];scene['currentVisualStatus']='FAIL';scene['ownerAcceptance']='UNVERIFIED';scene['runtime']='UNVERIFIED'
scene['findings']=['Hall body visibly damaged by mask, roof touches/clips stage edge.', 'Flat uniform pad polygons and lower river blur remain visible.', 'Static age-correct huts/logs outside active footprints are not automatically a failure. Map them to immutable scenery; clear actual mutable/obstructing objects.', 'Viewport-fit rasters inspected at 825x375, 1280x720 and 1180x820; these are saved composites, not new runtime captures.']
spec=importlib.util.spec_from_file_location('review_gates_readonly',ROOT/'scripts/review_gates.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
g=module.evaluate(); fixtures=module.safety_fixtures()
bench=read(ROOT/'qa/benchmark/report.json')
checks={'at':now,'scope':'read-only evaluate() and safety fixtures; benchmark report inspected, benchmark main NOT run',
 'reviewRows':len(g['rows']),'reviewSourceFresh':sum(x['hashMatch'] for x in g['rows']), 'reviewSourceStale':len(g['stale']),
 'selectedRows':len(g['selected']),'selectedFresh':sum(x['acceptedForRecovery'] for x in g['selected']),
 'outputStale':g.get('outputStale'), 'scene':g.get('scene'),'fixtures':fixtures,
 'savedBenchmark':{'at':bench['at'],'checks':len(bench['automated']),'statuses':dict(collections.Counter(x['status'] for x in bench['automated'])),'assets':len(bench['assets']),'batches':dict(collections.Counter(x['batch'] for x in bench['assets'])),'sourceGateCounts':dict(collections.Counter(x['gates']['sourceContent'] for x in bench['assets'])),'manual':collections.Counter(x['status'] for x in bench['manual']),'productApproved':bench['productApproved']}}
save('current-gate-checks.json',checks)
save('all-source-review.json',{'version':1,'at':now,'role':'PLANNER_VERIFIER_ONLY','scope':'All 240 sources overview; targeted native crops; no global fine-matte/registration/rig PASS claim','attempts':240,'distinctLiteralIDs':len(seen),'baselineRequestedIDs':len(required&seen),'baselineNotYetRequestedIDs':sorted(required-seen),'unmatchedIDs':sorted(seen-required),'newOverviewCompleteRoleFailures':critical,'rows':rows})
save('current-delivery-review.json',{'version':1,'at':now,'role':'PLANNER_VERIFIER_ONLY','scope':'11 current v2 asset versions, not 55 independent assets','intendedUseArtworkPass':4,'nativeAllPurposePass':0,'runtimeVerified':0,'ownerAccepted':0,'assets':deliveryrows,'scene':scene})
files=[]
# Allowlisted existing artifacts only. Metadata manifest is a backup proposal, not an upload/backup claim.
for directory in ['assets','docs/plan/image-production','src','tests','scripts','qa/recovery-correction-20261003','qa/recovery-verifier-20261003','qa/delivery-20261003','design-preview/generated']:
    for p in sorted((ROOT/directory).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            rel=p.relative_to(ROOT).as_posix(); files.append({'file':rel,'bytes':p.stat().st_size,'sha256':digest(p)})
for name in ['package.json','index.html','docs/plan/IMPLEMENTATION-CONTRACT.json']:
    p=ROOT/name;files.append({'file':name,'bytes':p.stat().st_size,'sha256':digest(p)})
save('protected-input-snapshot.json',{'at':now,'files':files})
storagefiles=[dict(x,proposedObjectKey=f"objects/sha256/{x['sha256'][:2]}/{x['sha256']}",remoteURI=None,externalCopyVerified=False,independentBackupVerified=False,restoreVerified=False) for x in files if x['file'].startswith(('assets/','docs/plan/image-production/','design-preview/generated/'))]
save('restore-manifest-draft.json',{'version':1,'at':now,'status':'PROPOSAL_NO_EXTERNAL_BACKUP_OR_UPLOAD_PERFORMED','destination':None,'files':storagefiles})
save('summary.json',{'at':now,'attempts':240,'batches':8,'technicalPass':240,'associationPass':read(OUT/'associations.json')['count'],'distinctIDs':len(seen),'baselineIDsNotRequested':len(required-seen),'deliveryRasterFiles':len(inventory['deliveryFiles']),'currentAssetVersions':len(deliveryrows),'scopedArtworkPass':4,'newCompleteRoleFailures':len(critical),'rawImageBytes':sum(x['bytes'] for x in inventory['sources']),'rawPredictionBytes':sum(p.stat().st_size for p in (ROOT/'assets/production').glob('*/provider-output/predictions.jsonl')),'protectedFiles':len(files),'fixturesAllPass':all(fixtures.values())})
print(json.dumps(read(OUT/'summary.json')))
