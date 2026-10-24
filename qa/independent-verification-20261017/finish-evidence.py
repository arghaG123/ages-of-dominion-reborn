from pathlib import Path
import json,re,hashlib,collections,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def put(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
needles={
'src/core/storage-adapter.js':['async commit','currentHead.epoch !==','campaignId: candidateState.story','async replace','this.epoch++','async migrateFromLocalStorage','const staged =','if (live) {','migratedAt'],
'src/client/main.js':['function persist','saved = true','function replaceLive','storeSlot(localStorage','loadSlot(localStorage','function paintMaterialWalls','const ROLE_RIG','function drawFigure','const lastAction =','function installLifecycle','window.rebornBackground'],
'src/client/actor.js':['export function paintWornSlots','const size = Math.max','export function drawReviewMount','export function drawStaticMount','export function drawPlate'],
'src/client/hero-room.js':['export function heroBody','function paintBackdrop','export function heroKitCaption'],
'tests/save-stress-horizon.test.mjs':['state.resources.food += 10000','state.hero.level = 3','state.quests[','for (let wave','state.defense = {','const tenHoursSeconds','state.defense.core = 0','const categories =','new IndexedDBStorageAdapter'],
'scripts/capture-motion-extremes.py':['pose = clip_angles','scaled_torso','scaled_leg','draw.text'],
'scripts/generate-scene-registration-20261016.py':['painted_radius =','is_aligned = (age_name','swept_footprint_clear =','"groundContactVerified": "PASS"','"visualGrounding": "PASS"'],
'scripts/generate-viewport-review-20261016.mjs':['const topNavArea','allNavButtonsMeetMinimum: true','renderedWithoutClipping: true'],
'scripts/generate-mechanics-and-balance-20261016.mjs':['classification: \'natural\'','refunds 100%'],
'scripts/generate-performance-20261016.mjs':['const iterations','// 1. Kingdom','frameTimePercentilesMs'],
'android/app/src/main/java/com/agesofdominion/game/MainActivity.java':["return 'saved'",'web.evaluateJavascript(script'],
}
rows=[]
for path,terms in needles.items():
    lines=(ROOT/path).read_text(encoding='utf8').splitlines()
    for term in terms:
        matches=[{'line':i+1,'text':line.strip(),'context':'\n'.join(lines[max(0,i-2):i+4])} for i,line in enumerate(lines) if term in line]
        rows.append({'path':path,'term':term,'matches':matches})
put('source-line-evidence.json',rows)
ledger=load('qa/mock-led-executor-20261016/completion-contract.json')
reasons={
'OWN-17':'Producer renamed original setup requirement to persistence. Native browser storage has reproduced CAS/replacement/migration failures; long browser horizon incomplete.',
'SYS-04':'Producer renamed original Forge/Market requirement to IndexedDB CAS. Native commit ignores identity/checksum; replace ignores expected head.',
'G03':'Real first Lumber construction is bounded PASS; cited captures do not prove all producers/facilities/caps/eight-age completion and cancellation/reload states.',
'G15':'Actual IndexedDB adversarial probes FAIL; main acknowledges queued saves and slots/replacement remain tied to localStorage.',
'G16':'Stress script assigns quests/clears, forces Defense result and uses grants. Does not close shared same-campaign natural consequences.',
'M01':'Screenshot exists; current Home viewed. Full mock hierarchy/material/state/recovery comparisons not passed.',
'M02':'Fresh sparse logical start and paid Lumber observed; phone useful-world metric fails and blur/scars/composite obligations remain.',
'M07':'Cites Stone Adventure screenshot for Gunpowder Kingdom. Wrong view and age; no required mock proof.',
'M10':'Cites Hero screenshot for Future Kingdom. Wrong view. Current Future ground reviewed but full mock scene acceptance open.',
'M13':'Cites Tactical Duel screenshot for on-foot Adventure. Wrong mode and missing arrival/contact journey.',
'OC03':'Current walls are state-selected flattened paintings, but repeat-strip rectangular course/composite/depth remain failing; old segment evidence stale.',
'OC06':'New male standing Healer has metadata staffExtendedBelowBoots=0 and fresh static check passes bounded. Existing old female rig/portrait consistency and full four-era consumer acceptance not established.',
'OC09':'25 files exist, but body pixels identical across five labelled clips per role. Generator never applies angles; role matrix OPEN, era-independent rig and plate/bob consumers remain.',
'OC16':'Five native IndexedDB probe failures; no truthful asynchronous save acknowledgement or full long-browser fault horizon.'}
disposition=[]
for row in ledger['leaves']:
    disposition.append({'executorLeafId':row['leafId'],'executorName':row['name'],'producerResult':row['result'],'independentResult':'REJECTED_PASS_OPEN' if row['result']=='PASS' else 'OPEN_NOT_CLOSED','reason':reasons.get(row['leafId'],'No complete current leaf assertion evidence. See original-scope crosswalk, fresh bounded tests and findings; this is not an independently verified PASS.'),'evidence':row.get('recheckedEvidence') or row.get('evidence')})
put('executor-277-dispositions.json',disposition)
def clip(r,b):
    l=max(r[0],b[0]);t=max(r[1],b[1]);rr=min(r[2],b[2]);bb=min(r[3],b[3]);return (l,t,rr,bb) if rr>l and bb>t else None
def union_area(rects):
    xs=sorted({x for r in rects for x in [r[0],r[2]]});total=0
    for a,b in zip(xs,xs[1:]):
        ys=sorted((r[1],r[3]) for r in rects if r[0]<b and r[2]>a);length=0;end=-1e30
        for lo,hi in ys:length+=max(0,hi-max(lo,end));end=max(end,hi)
        total+=(b-a)*length
    return total
def metric(rows,name):
    results=[]
    for row in rows:
        U=(0,0,row['width'],row['height']);t=row['terrain'];T=clip((t['left'],t['top'],t['right'],t['bottom']),U);hud=[]
        for item in row['hud']:
            r=item['rect'];q=clip((r['left'],r['top'],r['right'],r['bottom']),T)
            if q:hud.append(q)
        area=(T[2]-T[0])*(T[3]-T[1]);occupied=union_area(hud);ratio=(area-occupied)/(row['width']*row['height'])
        results.append({'actualWidth':row['width'],'actualHeight':row['height'],'terrainInsideViewportArea':area,'HUDUnionOnTerrain':occupied,'visibleWorldRatio':ratio,'meets80':ratio>=.8,'scope':'zero-inset closed-inspector rectangle accounting; no safe-area/contrast/physical-pixel/complete-landmark acceptance','HUDTreatment':'Only visible individual identity/status/chip/button rectangles counted; transparent gaps not counted. Thus optimistic where ancestor input ownership is larger.'})
    put(name,results);return results
if (OUT/'layout-fixture-dom.json').exists():print('FIXTURE LAYOUT',metric(load('qa/independent-verification-20261017/layout-fixture-dom.json'),'layout-fixture-metric.json'))
if (OUT/'layout-settled-dom.json').exists():
    result=metric(load('qa/independent-verification-20261017/layout-settled-dom.json')[:1],'natural-phone-metric.json');print('NATURAL PHONE',result)
    put('layout-attempt-limitations.json',{'layout-dom.json':'Initial four viewport readings/captures include resize timing; retain as preliminary only.','layout-settled-dom.json':'All four rows measured the same actual 826x375 natural tab because browser viewport settings subsequently targeted another active tab. These are repeat observations at one size, NOT four-size proof.','layout-fixture-dom.json':'Separate stable actual viewport readings on active Future fixture tab; actual dimensions govern, not requested odd widths.','exact825and933':'UNVERIFIED: browser quantized layout widths to 826/934.'})
images=load('qa/independent-verification-20261017/executor-image-decode.json')
put('fresh-check-summary.json',{'dateIST':'2026-10-17','generatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Node':'24.19.0','Python':'3.13.15','nodeSuite':{'passed':162,'failed':0,'excluded':'save-stress-horizon copied with only import/output path redirects; run separately'},'stressFixture':{'passed':1,'classification':'injected memory/bounded-store fixture; not legal full progression, actual Endless clears or long native browser persistence'},'nativeStorage':load('qa/independent-verification-20261017/native-storage-results.json'),'citedExecutorRasters':len(images),'rasterDecodeFailures':[x for x in images if not x['decode']],'motion':load('qa/independent-verification-20261017/motion-evidence-pixel-comparison.json'),'staffHistoricalFinding':'Retired as current bare below-foot assertion: current field is 0 and test passes bounded. Full coherent body/rig/style acceptance remains OPEN.','sourceBoundary':'Planner verifier only; QA/docs and disposable origins; no production/provider/build/Git/device/cleanup/dispatch.'})
