"""Assemble documentation mappings from manually reviewed semantic assignments."""
from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; PLAN=ROOT/'docs/plan'
def read(n): return (PLAN/n).read_text(encoding='utf-8')
def save(n,o): (OUT/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def line(t,s): return t[:t.index(s)].count('\n')+1
manual=read('MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md')
original=read('COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md')
handoff_path=PLAN/'ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt'
old=handoff_path.read_text(encoding='utf-8')
prefix=old.split('===== DETAILED MOCK-LED SOLUTIONS MANUAL =====',1)[0]
if 'Semantic audit revision:' not in prefix:
    prefix += 'Semantic audit revision: all corrections A01–A08 in manual section 9 are binding. Original 96 steps remain verbatim; inherited section numbers refer to the 12 October plan as explained in A01. Read manual section 7 for journeys. No game fixes or fresh implementation acceptance are asserted by this revision.\n\n'
tail=old.split('===== FULL G01–G16 PRODUCT CONTRACT =====',1)[1]
tail_bytes=handoff_path.read_bytes().split('===== FULL G01–G16 PRODUCT CONTRACT ====='.encode('utf-8'),1)[1]
handoff_path.write_bytes((prefix+'===== DETAILED MOCK-LED SOLUTIONS MANUAL =====\n\n').encode('utf-8')+(PLAN/'MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md').read_bytes()+'\n\n===== FULL G01–G16 PRODUCT CONTRACT ====='.encode('utf-8')+tail_bytes)

# Each value below is a manual semantic assignment, not keyword-derived coverage.
own=[
('A01/A08; M01–M30','SUFFICIENT_WITH_CURRENT_OVERRIDE','No interim pre-code approval; independent desktop then later device/owner.'),
('A01; section 2','SUFFICIENT','Independent source/read-only reference boundaries; no old executable imports.'),
('R03–R07/A08','SUFFICIENT_WITH_RESIDUAL','Reuse and source lineage explicit; missing historical records remain UNKNOWN.'),
('J18/A06','CORRECTED_ASSERTION_GAP','Whole connected campaign plus explicit shared consequences and lost-army recovery.'),
('M01–M30/A02','CORRECTED_LAYOUT_GAP','Mock composition with actual state; concrete contain/HUD feasibility and focused-sheet fallback.'),
('section 3.1/R04/A08','SUFFICIENT_WITH_RESIDUAL','Coherent realistic treatment; pixel quality and affordability still unverified.'),
('R01/R02/J01–J02/A03','CORRECTED_DENSE_PICKING_GAP','Hall1+17 empty+Walls0; natural clearings and actual contextual target ownership.'),
('R03/R05/M02–M10/A06–A07','CORRECTED_ASSERTION_GAP','All eight age families; item-age distinct from campaign age; caps and derived stats.'),
('R03/J05–J06/A06/A08','CORRECTED_ASSERTION_GAP','16×10 paths/sites, full physical traces and terrain/weather/day/rest.'),
('R07/M12/A07','SUFFICIENT_WITH_RESIDUAL','True mount gait/rider/vehicle requirements specified; sources/contact outcomes unverified.'),
('R05/R06/M19/A04/A07','CORRECTED_MECHANICS_LANGUAGE','Eight classes/four kits/192 slot decisions; skill offers separate from points.'),
('R03/R07/J09/A06','CORRECTED_ASSERTION_GAP','Visible entry, range, role/telegraph/flight and density assertions.'),
('M14–M16/J07–J08/A03/A06','CORRECTED_ASSERTION_GAP','Grounding/actions/targets, queue, RNG and retaliation cases.'),
('R05–R07/A07','SUFFICIENT_WITH_RESIDUAL','Era/role/gear/worn source matrices specified; no art completion claim.'),
('J14/J18/A06/A08','CORRECTED_BALANCE_GAP','Retain full progression and measure real timing/loss recovery; no guessed rebalance.'),
('A01/A08; single executor file','CORRECTED_REFERENCE_GAP','One consistent prompt, exact input paths and inherited section resolution.'),
('section 2/A01','SUFFICIENT','Refresh installed facts; no stale absolute runtime path dependence or setup re-interview.'),
('section 2/A08','SUFFICIENT_WITH_RESIDUAL','Targeted extra20/absolute100/reserve once and serialized provider controls; live budget UNKNOWN.'),
('R10/A08','SUFFICIENT_WITH_RESIDUAL','Offline local runtime, zero permissions; provider dev tooling separate, native/device unverified.')]
sysrows=[
('R01/R02/J02/J04/A06','CORRECTED_ASSERTION_GAP','Per-instance producers/unique facilities, chronology/caps/costs and offline report.'),
('M24/J03/J13/A06–A07','CORRECTED_ASSERTION_GAP','24 role names/eight creatures/flyers/ranks/reinforcement/IDs.'),
('R06/J11/A06–A07','CORRECTED_CAPACITY_AMBIGUITY','Six worn and functional slots; no invented bag cap; artifacts/quality/age assertions.'),
('M22/J11/J15/A06','SUFFICIENT_WITH_ADDED_ASSERTIONS','Real Armory quality/cost/craft and Bronze buy/sell; Gold is price.'),
('M19–M21/J12/A04/A06','CORRECTED_MECHANICS_LANGUAGE','Points/offers and full-health target expectations corrected; all skills/spells/effects.'),
('M11–M13/J05–J06/A06','CORRECTED_ASSERTION_GAP','All site/day/rest/terrain/weather transitions, fixed offers/fog and guard return.'),
('M14–M16/J07–J08/A03/A06','CORRECTED_ASSERTION_GAP','Full action/queue/flight/effect/RNG/damage/retaliation scope.'),
('M17–M18/J09–J10/A06–A07','CORRECTED_TERMINAL_ROUTE','Four tower/five attacker behavior and natural Endless clear-to-defeat-to-settlement route.'),
('M25–M26/J14/A06','SUFFICIENT_WITH_ADDED_ASSERTIONS','Seven chapters plus Future, six rivals/quests/eight milestones and branch effects.'),
('M28/J17/A03/A08','SUFFICIENT_WITH_RESIDUAL','Music/SFX/local media/motion/help/privacy; heard/native/device evidence separate.'),
('M27/J01/J17/A03','SUFFICIENT','Anchored correct-command tutorial with cancel/skip/review/reload.'),
('R09/J16/A05','CORRECTED_FAILURE_AND_RACE_GAPS','Atomicity vs acknowledgement, epoch/CAS, all-key migration and adversarial schedules.'),
('J18/A05–A06','CORRECTED_ASSERTION_GAP','Shared campaign IDs/costs/rewards/mana/casualties and storage replacement ordering.'),
('R10/A08','SUFFICIENT_WITH_RESIDUAL','Exact final binary/native manifest/preview identity/device matrix, no early device action.'),
('section 3.2/R10/A02–A03/A08','CORRECTED_LAYOUT_GAP','Four landscape sizes, dense selection/insets/readability and measured performance.'),
('J10/A06–A07','CORRECTED_TERMINAL_ROUTE','All five options; deterministic Challenge/isolation; Endless not a ten-wave victory.')]
trace=read('REQUIREMENTS-TRACEABILITY.md')
cross=[]
for prefix,assignments in [('OWN',own),('SYS',sysrows)]:
    for i,(where,status,meaning) in enumerate(assignments,1):
        ident=f'{prefix}-{i:02}'
        source=next(x for x in trace.splitlines() if x.startswith(f'| {ident} |'))
        cross.append({'id':ident,'originalRequirement':source.split('|')[2].strip(),'originalSource':'docs/plan/REQUIREMENTS-TRACEABILITY.md','sourceLine':line(trace,source),'manualCoverage':where,'planDisposition':status,'semanticAssessment':meaning,'implementationAcceptance':'NOT_TESTED_BY_PLAN_AUDIT'})
save('original-35-crosswalk.json',cross)

report_path=PLAN/'INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md'
report=report_path.read_text(encoding='utf-8')
table='| Original ID | Requirement | Semantic plan assessment / binding instructions |\n|---|---|---|\n'
for row in cross:
    table+=f"| {row['id']} | {row['originalRequirement']} | {row['planDisposition']}: {row['semanticAssessment']} Manual {row['manualCoverage']}. |\n"
start='<!-- ORIGINAL35_TABLE -->'; end='<!-- END_ORIGINAL35_TABLE -->'
if end in report:
    report=report.split(start,1)[0]+start+'\n\n'+table+'\n'+end+report.split(end,1)[1]
else:
    report=report.replace(start,start+'\n\n'+table+'\n'+end)
report_path.write_text(report,encoding='utf-8')

groups=[(1,8,'A01/A08','BASELINE_AND_SCOPE'),(9,18,'section 3/A02/A03','NAVIGATION_AND_INPUT'),(19,27,'R03/A02/A08','PHYSICAL_REGISTRATION'),(28,39,'R04–R07/A04/A07','ART_GEAR_MOTION'),(40,50,'R01–R02/J01–J06/A06','KINGDOM_ADVENTURE'),(51,64,'J07–J10/A03/A04/A06/A07','COMBAT_WAR'),(65,79,'M19–M30/A04–A07','SUPPORT_AND_RESPONSIVE'),(80,89,'R08–R09/J01–J18/A02–A08','DESKTOP_EVIDENCE'),(90,96,'R10/A08','FINAL_PACKAGE_AND_REVIEW')]
sequence=original.split('## 4. Step-by-Step Instructions\n',1)[1].split('\n## 5.',1)[0]
steps=[]
for number,action in re.findall(r'^(\d+)\. (.+)$',sequence,re.M):
    n=int(number); g=next(g for g in groups if g[0]<=n<=g[1])
    steps.append({'id':f'STEP-{n:02}','originalNumber':n,'action':action,'sourceLine':line(original,f'{n}. {action}'),'manualInstructions':g[2],'subject':g[3],'semanticDisposition':'PRESERVED_WITH_BINDING_CORRECTIONS' if n in [20,26,51,66,76,79,82,86,88] else 'SUFFICIENT_PHASE_ACTION_WITH_REFERENCED_DETAILS','note':'Step82 inherited section6 resolves to original verification section and manual section7 journeys.' if n==82 else 'No implementation completion asserted.'})
save('original-96-crosswalk.json',steps)

Gwhere=['R03/R05/A06–A07','R01/J01/A03','R01/R02/J02/J04/A06','R03/M11–M13/J05–J06/A06','R07/M14–M16/J07–J08/A03/A04/A06','R03/R07/M17–M18/J09/A06','J10/A06–A07','R04/R05/M19/J12/A04/A06','M20–M21/J12/A04/A06','R06/M22–M23/J11/A06–A07','M24/J03/J13/A06–A07','M25–M26/J14/A06','J15/A06','M27/J01/J17','R09/R10/M28–M29/J16–J17/A05','J18/A05–A06']
grows=[]
for i,row in enumerate(re.findall(r'^\| G\d{2} \|.+$',original,re.M)):
    grows.append({'id':f'G{i+1:02}','contract':row,'sourceLine':line(original,row),'manualInstructions':Gwhere[i],'planDisposition':'SPECIFIED_WITH_REFERENCED_CORRECTIONS','implementationAcceptance':'NOT_TESTED'})
save('G16-crosswalk.json',grows)

prior=json.loads((ROOT/'qa/planner-detailed-solutions-20261016/reference-targets.json').read_text(encoding='utf-8'))
targets=[]
for row in prior['targets']:
    p=ROOT/row['path']; digest=hashlib.sha256(p.read_bytes()).hexdigest()
    heading=next(x for x in manual.splitlines() if x.startswith('### '+row['id']+' '))
    targets.append({**row,'manualLine':line(manual,heading),'currentSHA256':digest,'unchangedFromPriorPin':digest==row['sha256'],'semanticDisposition':'SPECIFIED_RECIPE_AND_STATE_CHECKS','additionalCorrections':{'M19':'A07 matrix scope','M20':'A04 points distinct from offers','M21':'A04 full-health capped behavior','M23':'A07 no invented bag cap','M18':'A07 Endless terminal route','M26':'A07 actual settled q6'}.get(row['id'],'A02/A03/A06/A08 as relevant'),'visualReviewThisTurn':'ALL30_OVERVIEW; M19/M22_NATIVE; NO_NEW_RUNTIME_ACCEPTANCE'})
save('M30-crosswalk.json',targets)
journeys=[]
for n in range(1,19):
    ident=f'J{n:02}'; heading=next(x for x in manual.splitlines() if x.startswith('### '+ident+' '))
    section=manual.split(heading,1)[1].split('\n### ',1)[0].split('\n## ',1)[0]
    journeys.append({'id':ident,'manualLine':line(manual,heading),'assertions':re.findall(r'^\d+\. (.+)$',section,re.M) or [section.strip()],'semanticDisposition':'SPECIFIED_PLUS_A06_SUBMECHANICS','implementationAcceptance':'NOT_TESTED','corrections':{'J05':'Day/rest/biome/weather supplement A06','J10':'A07 natural clear-to-defeat-to-settle; no forced resolution','J11':'A06/A07 all artifacts/qualities/age; no invented cap','J12':'A04 independent points/offers; full-health rules','J16':'A05 epochs/commit acknowledgement/all-key migration','J17':'A02/A03 insets, dense hit ownership, accessibility','J18':'A06/A08 actual complete identity/delta chain and loss recovery'}.get(ident,'Retain original natural/simulation/fixture classification and all subassertions.')})
save('J18-crosswalk.json',journeys)

contract=json.loads((ROOT/'src/data/implementation-contract.json').read_text(encoding='utf-8'))
scenes=[]
for mode in ['kingdom','adventure','tactical','defense']:
    geom=contract['geometry'][mode]
    for age in range(8): scenes.append({'scene':mode,'age':age,'stage':geom.get('sourceSize'),'matrix':geom.get('worldToSource'),'requiredInstructions':'R03/A02/A08','geometryGate':'UNVERIFIED_BY_PLAN_AUDIT','note':'Requires exact displayed bytes, real trace, protected threshold source and runtime composite. No gradient PASS inherited.'})
save('scene-32-obligations.json',scenes)

classes=['knight','ranger','warlock','mage','paladin','barbarian','necromancer','healer']; eras=['ancient','medieval','powder','mech']; slots=['helm','weapon','offhand','armor','boots','accessory']
save('class-kit-slot-192-obligations.json',[{'class':c,'era':e,'slot':s,'instruction':'R04–R07/A07','gate':'UNVERIFIED_BY_PLAN_AUDIT','reusedSourcesAllowed':True} for c in classes for e in eras for s in slots])

W,H=825,375; scale=min(W/1376,H/768); tw=1376*scale; left=(W-tw)/2
rects=[(16,16,160,48),(W-64,16,48,48),(W-384,16,304,28),(16,H-72,376,56)]
intersection=sum(max(0,min(x+w,left+tw)-max(x,left))*max(0,min(y+h,H)-max(y,0)) for x,y,w,h in rects)
save('layout-counterexample.json',{'kind':'ANALYTICAL_PROPOSED_LAYOUT_NOT_RUNTIME_MEASUREMENT','viewport':[W,H],'stage':[1376,768],'containScale':scale,'terrainWidth':tw,'terrainAreaFraction':tw/W,'nonoverlappingHudRectangles':rects,'terrainIntersectionArea':intersection,'remainingWorldFraction':(tw*H-intersection)/(W*H),'zeroInsets':True,'limitation':'Assumes whole HUD bounds occlude and contain camera; actual runtime mode/insets/shape must be measured.'})
print(json.dumps({'original35':len(cross),'G':len(grows),'originalSteps':len(steps),'M':len(targets),'J':len(journeys),'sceneRows':len(scenes),'slotDecisions':len(classes)*len(eras)*len(slots),'mocksUnchanged':all(x['unchangedFromPriorPin'] for x in targets)}))
