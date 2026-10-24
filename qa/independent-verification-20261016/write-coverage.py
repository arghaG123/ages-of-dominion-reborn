"""Publish audit dispositions; does not turn coverage into acceptance."""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
g=[
('G01','Eight ages','FAIL','Core progression simulation and 32 imported views pass bounded; era/kit/style/scene acceptance fails.','F1 F4 F6'),
('G02','Sparse Day 1 and economy','PARTIAL','Fresh resources, Hall/17 pads and paid Lumber Camp observed; final physical/composite acceptance remains open.','F0 F1 F6'),
('G03','Construction and progression','PARTIAL','Core costs, build/upgrade/offline tests pass; natural build/export/restore observed; complete visible progression not replayed.','F2'),
('G04','Adventure','FAIL','Navigation/guard logic tested; painted crossing/approach and mounted motion fail acceptance.','F1 F3'),
('G05','Tactical','PARTIAL','Legal engine, morale and spell tests; live Skirmish/Auto/modal pass; formation/terrain/event/clip requirements open.','F1 F3 F9'),
('G06','Defense','PARTIAL','Earned command simulation clears 20 Endless waves; visible role motion/physical lane and complete natural journey open.','F1 F2 F3'),
('G07','Five War modes','PARTIAL','All entry/core/isolation paths covered in suite; complete visible setup/result/reload for all five unverified.','F2'),
('G08','Hero/classes','FAIL','Eight class selection/body views inspected; Knight era mismatch, other unverified eras and incomplete kits.','F4 F5 F6'),
('G09','Nine skills/eight spells','PARTIAL','Source/core tests including positive morale and all spells pass; natural earned Wisdom/Resurrection journey not independently complete.','F2 F9'),
('G10','Six-slot equipment/Forge/bag','PARTIAL','Core recipes/qualities/slots tested; actual worn visual replacement and workshop/selected-item composition fail.','F2 F4 F6'),
('G11','Army/eight creatures','PARTIAL','All eight earned core identities covered; complete natural dwelling/combat/rank/codex journeys and role gait open.','F2 F3'),
('G12','Story/quests/Future','PARTIAL','Earned simulated chapters/milestones/six quests/Future pass; full visible branch/claim/return journey open.','F2 F6'),
('G13','Market','PARTIAL','Core quotes/transactions and live Stone lock covered; ordinary Bronze buy/sell/error/cancel/reload not independently replayed.','F2'),
('G14','Tutorial','PARTIAL','Core target sequence/skip/review tested and initial Build target observed; complete contextual visible sequence unverified.','F2 F6'),
('G15','Save/recovery/settings','PARTIAL','Core fault tests and real export/import/Continue observed; long-browser quota failures and native/audio/performance closure remain.','F7 F8'),
('G16','Shared consequences','PARTIAL','Core settlement/idempotency/practice isolation pass, bounded live Skirmish settles; full natural persistent multimode journey open.','F2 F7')]
grows=[dict(zip(['id','requirement','status','evidence','findings'],row))for row in g]
# Original identities are preserved, not renumbered as G rows.
links={'OWN-01':['G01','G08','G10'],'OWN-02':[],'OWN-03':['G01','G04','G08','G10'],'OWN-04':['G16'],'OWN-05':['G01','G04','G05','G06','G08','G10'],'OWN-06':['G01','G08'],'OWN-07':['G02'],'OWN-08':['G01'],'OWN-09':['G04'],'OWN-10':['G04'],'OWN-11':['G08'],'OWN-12':['G06'],'OWN-13':['G05'],'OWN-14':['G01','G08','G10'],'OWN-15':['G12','G15','G16'],'OWN-16':[],'OWN-17':[],'OWN-18':[],'OWN-19':['G15'],
 'SYS-01':['G02','G03'],'SYS-02':['G11'],'SYS-03':['G10'],'SYS-04':['G10','G13'],'SYS-05':['G08','G09'],'SYS-06':['G04'],'SYS-07':['G05'],'SYS-08':['G06'],'SYS-09':['G12'],'SYS-10':['G15'],'SYS-11':['G14'],'SYS-12':['G15'],'SYS-13':['G16'],'SYS-14':['G15'],'SYS-15':['G01','G05','G06','G15'],'SYS-16':['G07']}
special={
 'OWN-01':('UNVERIFIED','Owner explicitly rejects current game look/plot grid/box walls and keeps this AI verifier-only; final acceptance not claimed.'),
 'OWN-02':('PASS_BOUNDED','Current source and local package scanned; no old executable imports found. Exhaustive code ancestry was not audited.'),
 'OWN-03':('PARTIAL','Current assets/source hashes inspected for required consumers; whole provenance/archive transfer not re-audited.'),
 'OWN-16':('PASS_BOUNDED','Dated report, source snapshot, matrices and one complete portable executor continuation prepared; no Git publication/restore claim.'),
 'OWN-17':('PASS_BOUNDED','Existing environment/version records reused and actual runner versions refreshed; no setup re-interview.'),
 'OWN-18':('AUTHORITY_RECORDED_LIVE_UNVERIFIED','Latest targeted extra $20 / absolute $100 ceiling documented. No live accounting/provider readiness refresh or paid call.'),
 'OWN-19':('PASS_STATIC_RUNTIME_UNVERIFIED','Latest package has zero declared permissions and current runtime has no remote URLs. No independent device/network run.'),
 'SYS-14':('PARTIAL','Latest web package closure passes; native delivery binary differs and installed identity/full native performance remain unverified.'),
 'SYS-15':('PARTIAL','52 requested screen/viewport visits; actual phone widths 826/934. Contrast, exact odd widths and dense Android FPS/memory/thermal not closed.')}
source=(ROOT/'docs/plan/WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md').read_text(encoding='utf-8-sig')
original=[]
for line in source.splitlines():
 m=re.match(r'\| ((?:OWN|SYS)-\d\d) ([^|]+)\|',line)
 if not m:continue
 id,title=m.group(1),m.group(2).strip(); related=links[id]
 status,note=special.get(id,('PARTIAL','See current related G rows; whole feature acceptance is not closed.'))
 original.append({'id':id,'requirement':title,'status':status,'related':related,'evidence':note})
assert len(original)==35
plan=(ROOT/'docs/plan/COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md').read_text(encoding='utf-8-sig')
mocks=[]
for line in plan.splitlines():
 m=re.match(r'\| (\d\d-[^|]+\.jpg) \| (.+) \|',line)
 if not m:continue
 filename,requirement=m.groups(); n=int(filename[:2]);status='PARTIAL_UNVERIFIED';note='Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted.'
 if n in [2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18]:status='FAIL_OR_UNVERIFIED';note='Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6).'
 if n==19:status='FAIL';note='Eight settled body views: flat chamber, wrong/unverified eras and icon overlays; coherent worn body still missing (F4/F5/F6).'
 if n==22:status='FAIL';note='Fresh Forge shows generic SVG workshop/anvil rather than required prominent source-supported selected-item/workshop treatment (F6).'
 if n==16:status='PARTIAL';note='Live pending result/apply works; composed actual survivor/reward/loot result reference not independently accepted.'
 if n in [28,29]:status='PASS_BOUNDED_UNVERIFIED';note='Basic local Settings/Home/save UI works in inspected states; full native, quota/recovery/contrast/visual composition remain open.'
 mocks.append({'reference':filename,'requirement':requirement,'status':status,'evidence':note})
assert len(mocks)==30
journeys=[]
notes={
1:'Independent fresh class/start and correct starter economy; full initial-target/cancel/class matrix remains bounded.',
2:'Independent ordinary Lumber Camp cost/completion/production and restored export; all upgrade/cancel/reload subcases not replayed here.',
3:'Core recruitment/capacity tests pass; complete ordinary visible recruit-to-combat journey not replayed.',
4:'Earned command progression and synthetic age views pass. Producer natural browser path grants resources/Hall (F2).',
5:'Core navigation tests pass; all-age physical crossing/mount acceptance fails (F1/F3).',
6:'Core fixed offers/guards tested; producer dwelling PASS leaves claimed false (F2).',
7:'Live Skirmish opens; required manual action/flyer/morale queue cases not all replayed. Role motion fails (F3/F9).',
8:'Independent Retreat focus trap/cancel and Auto/once-applied result pass bounded. Full victory/defeat/retreat/reload matrix open.',
9:'Core fixed-step/deploy/pause/reload tests pass. Complete natural visible Defense result and art gates remain open.',
10:'Five core mode entries covered. Independent Skirmish only; all five full natural flows not claimed.',
11:'Six slots/qualities tested in core and equipped visual fixtures. Producer natural Forge includes grants; appearance fails (F2/F4).',
12:'Core point/skill/all-spell/Resurrection tests pass. Producer live spell uses injected Wisdom/wounded stack, not natural earned journey.',
13:'Eight creatures earned via command simulation. Current independent natural dwelling-to-combat/rank loop not completed.',
14:'Core seven chapters/six quests/eight milestones/Future covered. Full ordinary visible saved branch/conclusion/claim loop remains open.',
15:'Core quotes and transactions pass; live Stone locked state observed. Ordinary complete Bronze transaction/error/cancel loop unverified.',
16:'Independent real export/import/restored Continue observed; all slots/corrupt/unsupported/quota/recovery/native flows not fully rerun.',
17:'Basic Settings/text/rotation sampled; full heard audio, contrast, tutorial and keyboard journey not fully closed.',
18:'Natural build and practice result plus preserved natural save; complete natural build/recruit/equip/travel/campaign-battle/defend/claim chain not proved.'}
for n,note in notes.items():journeys.append({'id':f'J{n:02}','status':'PARTIAL_NOT_COMPLETE','evidence':note})
report={'date':'2026-10-16','verdict':'INCOMPLETE','G':grows,'originalRequirements':original,'mockReferences':mocks,'journeys':journeys,'counts':{'G':16,'OWN':19,'SYS':16,'mocks':30,'journeys':18},'scope':'Coverage accounting is not acceptance. Core simulation, imported visual fixtures, ordinary pointer play, package, device and owner gates remain separate.'}
(OUT/'coverage.json').write_text(json.dumps(report,indent=2))
md=['# Independent coverage appendix â€” 16 October 2026','', '**Whole game: INCOMPLETE.** See [findings and methods](INDEPENDENT-WHOLE-GAME-VERIFICATION-2026-10-16.md). A listed requirement is accounted for, not automatically accepted.','']
for title,rows,fields in [('Full feature contracts',grows,['id','requirement','status','evidence','findings']),('Original 19 owner / 16 system requirements',original,['id','requirement','status','related','evidence']),('All 30 design references',mocks,['reference','status','evidence']),('All 18 connected journeys',journeys,['id','status','evidence'])]:
 md+=['## '+title,'','| '+' | '.join(fields)+' |','|'+'---|'*len(fields)]
 for row in rows:md.append('| '+' | '.join((', '.join(row[f])if isinstance(row[f],list)else str(row[f])).replace('|','/')for f in fields)+' |')
 md.append('')
(ROOT/'docs/plan/INDEPENDENT-WHOLE-GAME-COVERAGE-2026-10-16.md').write_text('\n'.join(md),encoding='utf-8')
candidate=ROOT/'assets/high-res/final-native2k/portrait-ancient-healer.png'
from PIL import Image
im=Image.open(candidate)
(OUT/'healer-reuse-candidate.json').write_text(json.dumps({'file':str(candidate.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'size':im.size,'mode':im.mode,'status':'CANDIDATE_NOT_ACCEPTED','observed':'Complete standing figure, both feet, staff, basket, dark background. Identity differs from current composite. Requires style/matte/era/equipment/identity review; not automatically a world rig.'},indent=2))
print(report['counts'])
