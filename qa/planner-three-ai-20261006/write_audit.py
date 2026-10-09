"""Publish independent audit and planner-owned pointers; no production changes."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import hashlib,json,re,html
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PLAN=ROOT/'docs/plan'
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
v=read('docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json')
art=read('qa/planner-three-ai-20261006/artifact-summary.json')
verify=read('qa/planner-three-ai-20261006/v9-verification.json')
browser=read('qa/planner-three-ai-20261006/browser-report.json')
journey=read('qa/planner-three-ai-20261006/journey-report.json')
ages=read('qa/planner-three-ai-20261006/ages/report.json')
sizes=read('qa/planner-three-ai-20261006/ages-size/report.json')
measured=[]
for r in sizes['rows']:
    for x in r['figures']:
        if any(t in x['href'] for t in ['troop-gunpowder-heavy','troop-future-ranged','troop-future-heavy']):
            im=Image.open(ROOT/x['href']).convert('RGBA'); box=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
            h=(box[3]-box[1])/im.height*x['cssBox']['height']
            measured.append({'age':r['age'],'path':x['href'],'imageLegalHeight':float(x['height']),'imageCssHeight':x['cssBox']['height'],'visibleAlpha16CssHeight':h,'deliveryLimitPx':64,'exceedsVisible64':h>64,'stateKind':'FIXTURE','viewport':[1280,720]})
(OUT/'consumer-size-check.json').write_text(json.dumps(measured,indent=2))
before=read('qa/planner-three-ai-20261006/source-before.json')
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
(OUT/'source-preservation.json').write_text(json.dumps({'checked':len(before),'changed':changed,'scope':'existing src/tests/scripts captured before audit; does not hash every historical original'},indent=2))
focus={'id':'retreat-cancel-restore-trigger-focus','gate':'FAIL' if not browser.get('cancelFocus',{}).get('choice') else 'UNVERIFIED','observed':browser.get('cancelFocus'),'scope':'Cancel safely dismisses; active element ID empty and no trigger choice. Legacy20 modal/input checks still PASS.'}
(OUT/'additional-observations.json').write_text(json.dumps([focus],indent=2))
terminal=next(x['state']['defense'] for x in journey['steps'] if x['id']=='defense-before-settle')
perid={'readyRows':[{'id':r['id'],'producerStatus':r['status'],'binding':'PASS','runtime':'UNVERIFIED','owner':'UNVERIFIED','limitations':r.get('limit',r.get('limitations'))} for r in v['readySubset']],
       'scenes':[{'id':r['id'],'producerStatus':r['status'],'promoted':r['promoted'],'binding':'PASS','roadPaths':len(r['paintedRoadPolylines']),'walkablePolygons':len(r['walkablePolygons']),'spatial':'UNVERIFIED','owner':'UNVERIFIED','nextAction':r.get('nextExecutableAction'),'executor':'AI1'} for r in v['scenes']],
       'classChains':v['classChains'],'extraFocus':focus,'consumerSizes':measured,'wholeProduct':'INCOMPLETE'}
(OUT/'per-id-status.json').write_text(json.dumps(perid,indent=2))
refs=ROOT/'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
mockrows=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted(refs.glob('*.jpg'))]
assert len(mockrows)==30
(OUT/'approved-reference-hashes.json').write_text(json.dumps(mockrows,indent=2))
canvas=Image.new('RGB',(1280,8*210),'#141414'); draw=ImageDraw.Draw(canvas)
for age in range(8):
    for col,screen in enumerate(['kingdom','army','adventure','defense']):
        draw.text((col*320+4,age*210+2),f'FIXTURE age {age} / {screen}',fill='white')
        canvas.paste(ImageOps.contain(Image.open(OUT/f'ages/{age}-{screen}.png').convert('RGB'),(316,178)),(col*320+2,age*210+25))
canvas.save(OUT/'eight-age-overview.jpg')
gallery=OUT/'visual-loaded/gallery.html'
gallery.write_text(gallery.read_text().replace('src="../../design-preview/','src="../../../design-preview/').replace('<p>Live game:', '<p>Audit capture server has been stopped. Start the command below to review locally. Live game:'),encoding='utf-8')
summary={'date':'2026-10-06','wholeProduct':'INCOMPLETE','sourceSnapshot':{'HEAD':'c266e220fa024dfb95fbf534f180c40ed52585e3','beforeExistingFiles':len(before),'changedExistingFiles':changed},'suite':{'total':100,'pass':98,'fail':2,'cause':'exact historical guides missing; runner nonzero; shell wrapper completed after reading log'},'browser':{'checks':len(browser['checks']),'pass':sum(x['pass'] for x in browser['checks']),'errors':browser['errors'],'additionalObservation':focus},'journey':{'steps':len(journey['steps']),'errors':journey['errors'],'defenseTerminal':terminal,'scope':'natural build/recruit/guard win/earned orb equip/return/Defense defeat settle/reload; prepared win and all6slots remain open'},'package':art['package'],'image':{'readyRows':len(v['readySubset']),'associations':verify['bindings'],'failures':verify['bindingFailures'],'readyRasterChecks':len(verify['readyRasterChecks']),'jointMetrics':len(verify['jointChecks']),'scenes':len(v['scenes']),'promoted':sum(bool(r['promoted']) for r in v['scenes'])},'ageFixtureShots':len(ages['rows']),'consumerSizes':measured,'authority':'planner QA/docs only; no production/code/build/provider/device/Git/storage change or messaging/delegation'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
report=f'''Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; Node v24.19.0 independently verified 6 October 2026, custom serve/build scripts. Python3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1 measured. Android toolchain configuration is recorded, not remeasured; APK metadata was inspected statically.

# Both AI changes: independent audit, 6 October 2026

Whole product **INCOMPLETE**. The new Code shell and Image v9 make useful progress, but no age is independently established as visually complete to the approved landscape direction. Home/class selection and painted mode backgrounds are improved; Kingdom registration/mutable states, designed Army/Forge/support screens, full character rigs and whole earned journeys remain build work. Final material/FX/micro-spacing/optional optimization can follow. Missing primary screens, meaningful art and gameplay cannot move to the polish queue.

This is the owner-requested fresh-chat verification after the 5 October baseline. Source snapshot main `c266e220fa024dfb95fbf534f180c40ed52585e3`, initial git status empty, replaces older dirty63d79a3 baseline. Read-only comparison of {len(before)} existing src/tests/scripts files found {len(changed)} changed during this audit. Planner wrote isolated QA, audit/prompts and current pointers only. No game/art production, package build, provider/account/project/job/bucket query, physical device work, Git/index/history/storage mutation, executor message or agent dispatch occurred.

## What changed and what the actual pixels show

| Area | Fresh evidence / disposition | Remaining construction |
|---|---|---|
| Home/class | Landscape Stone valley, correct title and real New/Load/Settings; eight painted class cards; no schematic entry figure. Useful PARTIAL. | Approved Home has strong left-side title/action hierarchy and immersive scene. Current title/actions sit lower with generic top/footer chrome. Continue requires an existing save. Class portraits do not establish all full bodies/kits. |
| Kingdom | New brass pad/stake presentation; Hall loads; developed eight-age fixture layers captured. PARTIAL. | Current hard rectangular pads and dark framing differ from approved sparse/developed valley composition; source/physical registration and correct mutable/baked contents remain open. All17pads/Hall/Walls/full building states need integrated proof. |
| Adventure | Painted forest ground now loads, replacing the earlier blueprint-only frame. PARTIAL. | Legal route/cell/site blocks remain schematic overlays; complete painted paths/crossings/walkable ground/site/hero placement is unverified. |
| Tactical/Defense | Native paintings load and commands remain accessible. PARTIAL. | Thick schematic paths/grid/targets and small figures do not match approved grounded battle presentation. Painted/legal crossings/lanes/coverage/obstacles are not accepted. |
| Army | Static figures load and no whole-image walk dance in roster; age variants captured. PARTIAL. | Flat large empty chamber rather than approved camp/roster/composition; Stone slabs and role/body limits remain. Consumer64px limits need repair, see measured evidence. |
| Forge/Inventory/Hero | Forge has six canonical slot cards/glyphs and real comparison fixture still passes at four sizes. PARTIAL. | No approved immersive bench/current-era item presentation; empty slot state is legitimate before gear, but generic empty chamber alone does not deliver Forge. Full six-slot ordinary journey and Hero class/kit art remain open. |
| Story/settings/other support | Live navigation and data controls exist; Story and Settings snapshots saved. PARTIAL/whole scope UNVERIFIED. | Designed narrative/support composition remains largely empty chamber/generic UI. Quests/skills/spells/recovery/every War/support flow require full current visual/playable matrix. |
| Image v9 | Five Healer head cards added to14ready reused rows. Named WH/HW/XY conventions, leg-subchain poses, sourceBinding gates corrected; scene/gallery diagnostics improved. Bounded PASS. | Heads/subchain are not full bodies; all eight chains incomplete;32scene plates PARTIAL/0promoted. Missing full transforms/unsupported size/side/pose and complete geography remain scoped. |

Primary reference is the30Vertex LANDSCAPE mocks in `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/`, indexed by assets/mocks/INDEX.md. Earlier26vertical images remain style/content references. Mock title/Stone/Future/gear/device errors are corrected using canonical data; direction approval is not runtime acceptance.

Actual comparisons: [loaded runtime gallery](../../qa/planner-three-ai-20261006/visual-loaded/gallery.html), [reference/result overview](../../qa/planner-three-ai-20261006/reference-runtime-loaded.jpg), [eight-age fixture overview](../../qa/planner-three-ai-20261006/eight-age-overview.jpg). Early unloaded capture images are preserved separately and are not missing-art findings. The loaded pass waits for raster decoding. All8ages x Kingdom/Army/Adventure/Defense =32fixtures captured without page errors; these are layout/art fixtures, not earned progression or whole acceptance. Selected overview and native images were inspected; this is not a fine-pixel approval of every source asset.

## Independent local results

- Node24 suite:100tests,98PASS,2FAIL due to exact missing v4/v5historical guide PNGs; unchanged cause from prior99/97baseline. Do not weaken tests, fabricate guides or restore archives. Test runner reports failure; the shell tool returned0 after the log-tail command, so tool wrapper success is not suite success.
- Corrected held-pointer/modal/input/Forge harness:20/20PASS. Redraw-safe pointer/touch/keyboard/reduced-motion/resize, closed cells, Retreat open/cancel/Escape/confirm/once settlement, no background actions while open, Forge visible deltas at four sizes,14pxlabels and portrait preservation receive bounded PASS. Additional Cancel focus observation: active element id empty/no trigger choice after dismissal, **FAIL restore-trigger focus**. Containment repair is real; remaining restore-focus is separate.
- Instrumentation correction: initial old harness pressed Enter on the now-correctly focused Cancel then tested the dismissed dialog as though still open. Raw report/log retained under `*-harness-before-correction.*`. Corrected probe activates only escaped background focus, leaving legitimate modal controls untouched. No application source changed to pass it.
- Separate loaded shell capture:16/16technical predicates PASS,17actual screenshots; predicates such as data-board=painted and slot count are not composition/registration/whole-game PASS.
- Natural isolated fresh-save journey:17saved checkpoints, no harness errors. Four builds/real production/recruit/travel/manualguard10,5win/earned orb `loot-161-0-accessory` compare/equip/return/heroarmyDefense/settlement/reload reproduced. This run Defense RESOLVED enemy win, {terminal['cleared']} cleared wave, pending settlement true, core {terminal['core']:.3f} before settlement; after settlement defense null andgold250. Earlier2wave result is historical. Timing/RNG/checkpoint changes are not inferred balance regressions. Prepared natural Siege victory, all6natural slots, earned8ages/classes and allWar/support journeys remain open.
- Current unsigned APK `{art['package']['sha256']}`,{art['package']['bytes']}bytes:300source/dist/Android-www/APKfile matches,300APKwebentries,ZIPCRC PASS. Fresh aapt35 static metadata:previewID,min24,target/compile36; no uses-permission. No APK build or physical-device test. DeviceSTOPPED. Recorded AGP8.7.3/compile36 warning remains executor history. Current package is much larger than prior359122611bytes; nonessential optimization is later unless performance/usability requires it.
- Image v9:167distinct referenced associations hash/decode PASS;15ready-raster dimension/alpha16bounds checks PASS;12prior bounded joint overlap metrics reproduce; all19sourceBindinggates nowPASS. This resolves v8's unverified ready-binding labels and canvas-order ambiguity, without proving full anatomy/articulation/scene geography. Healerboot135x131/main12474pixels/retainedRGBAunchanged reproduced. This association set differs from v8's172including two missing guides; those guides still fail the suite and were not recovered.

Exact machine evidence and per-ID scope: [summary](../../qa/planner-three-ai-20261006/summary.json), [per-ID outcomes](../../qa/planner-three-ai-20261006/per-id-status.json), browser-report.json, journey-report.json, artifact-summary.json/package-files.json, v9-verification.json/v9-bindings.json, source-preservation.json, approved-reference-hashes.json and consumer-size-check.json in the same QA folder.

## Remaining Image and consumer limits

Healer front-neck/card actual alpha was inspected; transparent green RGB is not opaque background damage. Five cards are static views, sideUNKNOWN; failed head-to-torso/skirt-to-leg and incomplete torso/skirt remain. Reuse successful boot and valid subchains. Knight thigh/greave13attempts, Paladinfailedlinks/missing rejected headbytes, Industrialcoat/Modernslab/snow, absent standingSharpshooter remain scoped. No replacement authorization is inferred.

Stone v9 overlay excludes withdrawn ridge lines and improves deck placement. It still has only coarse4roadpaths/24-40legalpx road-bank uncertainty, deck16px and0walkablepolygons. The ring crosses/hugs rocks; the central rock feature/full legal footprints have no clearance PASS. Other31scenes have no painted paths/banks/approach/walkable/blocked annotation. Uniform four-viewport composites improve on stretched v8thumbnails but are not actual runtime registration. Int16candidate correction8scenes/13360pixels remains arithmetic-only. Per-source manual tracing is feasible unfinished work; generic Sobel exhaustion does not exhaust31independent scenes.

Code `src/client/main.js` asks130legalpx for Army review and200for stacks; `drawPlate` clamps catalogstaticMaxHeight130. Fixture measurement at1280x720 is saved per cannon/Futureranged/Futureheavy with actual image CSS bounds and visible-alpha-derived height in consumer-size-check.json. These are consumer/delivery-limit conflicts where recorded visible64px is exceeded; smaller phones do not imply larger-view acceptance. Preserve64pxdelivery limits unless genuinely new Image evidence explicitly expands them.

## Three complete owner-distributable prompts

1. [AI1: environment/building/site/tower/UI art and geography](ENVIRONMENT-ART-AI-COMPLETE-PROMPT-2026-10-06.txt):all32scenegeography/8ageworld layers, sparse/developed states and staticworld/UI metadata.
2. [AI2: character/Army/Hero/equipment/rig delivery](ACTORS-EQUIPMENT-AI-COMPLETE-PROMPT-2026-10-06.txt):source-supported identities/mattes/subchains/full bodies when feasible, gear/artifacts/mounts/creatures/attacking actors.
3. [AI3: whole visual/playable Code build](CODE-AI-COMPLETE-VISUAL-PLAYABLE-PROMPT-2026-10-06.txt):allages/screens/rules/support/ordinary journeys, runtime integration, galleries/liveURL and unsignedstatic package.

Art is a bottleneck for final scene registration/body/gear presentation, so two local-art queues have distinct ownership. Art-first is per-row: immutable source -> producer recipe/verified interface -> Code binding/placement -> actual gameplay/owner review. Code completes layouts/rules/support during art work and integrates each ready row immediately. No global wait for all32scenes/owner/device. Producers write separate interfaces and helpers; Code alone updates runtime catalogs. Rootstatus/currenthandoff files are planner/owner merged, not concurrent executor writers. [Exact ownership/dependencies](THREE-AI-OWNERSHIP-2026-10-06.md).

All three prompts have exactly7sections, typed contracts, explicit assumptions,30reference mapping, fullscope, finite methods, exact boundaries, pass/fail criteria and durable partial/resume instructions. Structural checks:24/25/33numbered steps respectively in QA prompt-structure-check.json. Review of prompt structure is not executor completion. Planner did not dispatch them. NO_NEW_PAID_CALLS/frozenKingdomgeometry/deviceSTOPPED/zeroofflinepermissions/preciseguide/morale/owner scopes persist.
'''
(PLAN/'BOTH-AI-INDEPENDENT-AUDIT-2026-10-06.md').write_text(report,encoding='utf-8')
ownership='''Language/framework/version: JavaScript ES modules/HTML/CSS/SVG, verified Node24.19.0; local Python3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1. Android recorded configuration, no device work.

# Three-AI ownership and dependency map — 6 October 2026

Whole visual/playable product INCOMPLETE. Distribute the three complete prompts manually; no executor was messaged or dispatched by planner. Existing originals/v4-v9interfaces/canonicalmechanics/frozengeometry are shared immutable inputs. Each AI rechecks intervening state read-only.

| AI | Exclusive production ownership | Exclusive handoff/interface | Dependencies |
|---|---|---|---|
| 1 Environment | assets/derivatives/environment-20261006/; QA/scripts/recipes/geography in qa/environment-art-20261006/ | docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json; own checkpoint/gallery/handoff | Reads sources/v9/activeCodegeometry; no wait for actors to finish geography/building metadata. |
| 2 Actors/equipment | assets/derivatives/actors-equipment-20261006/; QA/scripts/recipes/rigs in qa/actors-equipment-20261006/ | docs/plan/ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json; own checkpoint/gallery/handoff | Reads sources/v9; contact/depth metadata uses shared immutable frame, no terrain edits. |
| 3 Code | src/runtime/catalogs/tests/Codebuildservehelpers/dist/android static package; qa/code-whole-build-20261006/ | Own checkpoint/liveURL/runtimegallery/interactionevidence/handoff | Verifies and consumes each producer readySubset, never writes producer interfaces/outputs. |

AI1 owns buildings/Hall/Walls/towers/static sites/terrain/scene-environments/resource+skill+spell+navigation icons/materials/staticworldFX. AI2 owns hero/classes/troops/creatures/attackers/mounts/vehicles/gear/artifacts/actorFX. AI3 owns all real UI/CSS/vectorchrome/render consumers/gameplay/save/native staticpackage. AI1 may assemble figures read-only in scene composites; AI2 may use scene layers read-only for grounded figure/gear composites. Neither may publish the other's derivative under duplicate ownership or change its interface. New corrections use immutable descendants inside the same owner's prefixes; no shared V10 writer or shared production helper modification.

Sequential dependency for a given affected row:

1. Art owner selects and hashes immutable existing input.
2. Art owner prepares finite local source-backed derivative/annotation with typed matrices/contact/size/pose limits.
3. Art owner verifies semantics/matte/spatial or marks exact scoped limitations and atomically publishes its readySubset.
4. Code verifies that row before changing the consuming catalog/renderer.
5. Code proves placement/controls/legal consequences at fourviewports through real runtime captures.
6. Owner reviews visible result; owner acceptance and device acceptance stay independent.

Code begins independent screen construction/rules/support immediately, establishes Stone grammar then completes all8ages/screens in the same task. Home chrome/buttons, Army/Forge layouts, story/settings/recovery, save/rules and positive-morale-independent mechanics do not require all-art-ready. Final scene/body promotion requires only the corresponding row. Unavailable hidden ground/standing anatomy or frozen geometry conflict blocks its exact row; all independent work continues. Existing v9 bounded ready rows can be reused unchanged with preserved limits while new interfaces are prepared.

Both art owners label galleries ASSET_COMPOSITE/playabilityUNVERIFIED. Code delivers approvedreference/actualruntime side-by-side gallery/liveURL/ordinaryjourneys; no technical count or filename is finishedgame. Required build gaps stay separate from optional polish.

Shared CURRENT-STATUS.md, START-HERE.md, DECISIONS.md, docs/SESSION-HANDOFF.md, docs/BUILD-PROGRESS.md, docs/PLANNER-VERIFIER-HANDOFF.md and planREADME/currentrequirements are planner/owner merge points. Executors do not overwrite them; publish exclusive owner-mergeable handoffs. Shared source/catalog/build edits are Code-only; original art/productionqueues/providerlocks/budgets remain read-only. No Git/storage/device/provider/payments/dispatch authority. Frozen Kingdom affine[60,-10,25,35,170,165]/Hall0.1312 requires a versioned coordinated proposal/review, not silent activation.

The whole work is covered collectively by [AI1 prompt](ENVIRONMENT-ART-AI-COMPLETE-PROMPT-2026-10-06.txt), [AI2 prompt](ACTORS-EQUIPMENT-AI-COMPLETE-PROMPT-2026-10-06.txt), [AI3 prompt](CODE-AI-COMPLETE-VISUAL-PLAYABLE-PROMPT-2026-10-06.txt). Final source/visual/playable/runtime/native/owner gates remain honest; lack of new-source authority can keep specific required rows blocked after all feasible local work.
'''
(PLAN/'THREE-AI-OWNERSHIP-2026-10-06.md').write_text(ownership,encoding='utf-8')
banner='''Language/framework/version: JavaScript ES modules/HTML/CSS/SVG; Node24.19.0 and Python3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1 independently verified 6 October 2026. Custom serve/build scripts; Android configuration recorded, deviceSTOPPED.

> **Fresh independent Code/Image audit + three whole-work prompts — 6 October 2026, INCOMPLETE:** {audit}. New Code landscape shell and Imagev9improve actual results, but no visually complete age established. Fresh100tests/98PASS/2exactguideENOENT; corrected browser20/20PASS plus Cancel restore-trigger-focusFAIL; loaded shell16/16technicalPASS;32eight-age fixtures; natural guard/orb/return/Defense defeat-settle/reload, preparedwin/all6slots/earned8ages still open. Current unsignedAPK3cc5bccd/410291618bytes/300source-dist-www-APKmatches/CRC/previewID/SDK24-36/zero permissions staticPASS. Imagev9:19boundedready/167bindingsPASS/15rasterchecks/12jointmetrics;32scenesPARTIAL/0promoted/eightfullchainsincomplete. Give owner-selected AIs {a1}, {a2}, {a3}; {map}. Per-row art->verifiedhandoff->Codeintegration, independent Code layouts/rules/support continue. All prompts exactly7sections;24/25/33steps. Separate producer directories/interfaces, Code-only runtimewriter; shared pointers planner/ownermerged. NO_NEW_PAID_CALLS/frozengeometry/deviceSTOPPED/full8ages/all30landscapetargets persist. Planner QA/docs only; no game/artproduction/build/provider/device/Git/storage mutation or executor dispatch/delegation. Dated/concurrent history follows.

'''
targets={'CURRENT-STATUS.md':'docs/plan/','START-HERE.md':'docs/plan/','DECISIONS.md':'docs/plan/','docs/SESSION-HANDOFF.md':'plan/','docs/BUILD-PROGRESS.md':'plan/','docs/PLANNER-VERIFIER-HANDOFF.md':'plan/','docs/plan/README.md':'','docs/plan/CURRENT-REQUIREMENTS-RECHECK-2026-10-05.md':''}
for name,prefix in targets.items():
    p=ROOT/name; old=p.read_text(encoding='utf-8-sig')
    b=banner.format(audit=f'[audit]({prefix}BOTH-AI-INDEPENDENT-AUDIT-2026-10-06.md)',a1=f'[AI1 environment]({prefix}ENVIRONMENT-ART-AI-COMPLETE-PROMPT-2026-10-06.txt)',a2=f'[AI2 actors/equipment]({prefix}ACTORS-EQUIPMENT-AI-COMPLETE-PROMPT-2026-10-06.txt)',a3=f'[AI3 whole-game Code]({prefix}CODE-AI-COMPLETE-VISUAL-PLAYABLE-PROMPT-2026-10-06.txt)',map=f'[ownership/dependencies]({prefix}THREE-AI-OWNERSHIP-2026-10-06.md)')
    p.write_text(b+old,encoding='utf-8')
print(json.dumps({'auditWritten':True,'pointerFiles':list(targets),'existingSourceChanges':changed,'sizeMeasurements':measured,'sceneRows':len(v['scenes'])},indent=2))
