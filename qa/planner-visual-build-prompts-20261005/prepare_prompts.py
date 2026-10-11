"""Write planner prompts only. No game/source/image/provider operations."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'docs/plan'
CODE='CODE-AI-VISUAL-PLAYABLE-WHOLE-BUILD-PROMPT-2026-10-05.txt'
IMAGE='IMAGE-AI-VISUAL-PLAYABLE-LOCAL-DELIVERY-PROMPT-2026-10-05.txt'
BRIEF='VISUAL-PLAYABLE-BUILD-OWNER-PRIORITY-2026-10-05.md'
MOCKDIR='design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
mockmap='''Primary visual authority: the30Vertex-generated LANDSCAPE mocks approved by the owner after the orientation change, indexed by assets/mocks/INDEX.md and stored under design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/. Earlier26vertical owner images supply artwork/atmosphere/content reference; they do not replace approved landscape layout. Open the actual pixels before work. The downloaded HTML galleries are indexes only. Approval establishes the visual direction; it does not certify generated synchronization/content errors or current runtime.

Complete landscape target mapping (filenames relative to that images/ directory):
- Home/entry:01-home.jpg.
- Kingdom sparse Day1:02-kingdom-day1.jpg; developed Stone:03-kingdom-stone.jpg.
- Kingdom other seven ages:04-kingdom-bronze.jpg,05-kingdom-iron.jpg,06-kingdom-medieval.jpg,07-kingdom-gunpowder.jpg,08-kingdom-industrial.jpg,09-kingdom-modern.jpg,10-kingdom-future.jpg.
- Adventure overview/crossing/foot travel:11-adventure-overview.jpg,12-adventure-crossing.jpg,13-adventure-foot.jpg.
- Tactical deployment/action/result:14-tactical-deployment.jpg,15-tactical-action.jpg,16-battle-result.jpg.
- Defense preparation/live wave:17-defense-preparation.jpg,18-defense-wave.jpg.
- Hero/equipment/skills/spells:19-hero-equipment.jpg,20-skills.jpg,21-spells.jpg.
- Forge/Inventory/Army:22-forge.jpg,23-inventory.jpg,24-army.jpg.
- Story/quests/tutorial:25-story.jpg,26-quests.jpg,27-tutorial.jpg.
- Settings/save recovery/UI materials:28-settings.jpg,29-save-recovery.jpg,30-icon-material-board.jpg.

Use approved composition, landscape camera, scene hierarchy, readable panels, contextual controls and slate/stone/brass interface language. Correct known mock errors using canonical data: game title Ages of Dominion, Stone era identity instead of medieval content, true Future era instead of rural carryover, six canonical equipment slots instead of invented labels, no literal photographed device frame or duplicate icon meanings. Do not turn a full mock JPEG into a clickable screenshot pretending to be a game.

Owner priority: BUILD THE WHOLE VISUAL, PLAYABLE GAME FIRST; FINAL POLISH AFTERWARD. Basic scene art, correctly placed real controls, readable interfaces, genuine build/battle/equipment states and coherent interaction are required construction work now. Fine texture/edge refinements, decorative micro-spacing, elaborate transitions/particles, cinematic animations, audio mixing and nonessential packaging optimizations may enter a named later polish queue. Stability, legal state, save safety, input accessibility and misleading role/terrain errors are not deferred as polish. Missing source anatomy is an explicit affected-asset blocker; do not replace it with a dancing stick figure or claim articulated animation. A correctly identified intact static figure is an honest interim display where appropriate; this does not close the full animation requirement.

Visible evidence contract:
- VisualGate=PASS|FAIL|UNVERIFIED|BLOCKED; PASS requires an actual inspected runtime/composite, not a filename/hash/test count.
- VisualRow={id:string,screen:string,age:integer0..7|null,classId:string|null,referencePaths:string[],referenceHashes:SHA256[],sourceHashes:object,viewports:[width:number,height:number][],stateKind:NATURAL|FIXTURE|ASSET_COMPOSITE,screenshotPaths:string[],checks:{composition:VisualGate,artPlacement:VisualGate,controlsOrContacts:VisualGate,readability:VisualGate,stateTruth:VisualGate,playability:VisualGate},differences:string[],blocker:string|null,nextAction:string|null,ownerAcceptance:UNVERIFIED|ACCEPTED|REJECTED}.
- ReviewIndex={schema:1,generatedAt:string,sourceSnapshot:object,liveUrl:string|null,rows:VisualRow[],polishQueue:{id:string,reason:string,priority:integer}[],wholeBuildStatus:INCOMPLETE|READY_FOR_OWNER_REVIEW}. Image-only rows set playabilityUNVERIFIED and stateKindASSET_COMPOSITE; they never self-certify runtime playability.
- Runtime action evidence={action:string,ordinaryUI:boolean,beforeStateHash:SHA256,afterStateHash:SHA256,result:string,screenshotPath:string,saveReloadVerified:boolean}. Injected fixture setup is labeled and cannot prove natural progression.

Provide a local HTML review gallery with reference and actual result side by side, screenshot/animation links, tested viewport/state, explicit remaining differences and the correct live game URL for Code. Use local files only, unchanged reference images and a distinct QA directory; preserve prior captures. The gallery must show the produced work. Do not label a contact sheet of source art or a mock-only gallery a gameplay result. The owner's existing4173server/profile/save must remain undisturbed; use an unused isolated verification port and report it explicitly.
'''
def section(text,n,title,content):
    start=f'{n}. {title}\n'
    left,rest=text.split(start,1)
    if n<7:
        titles=['Task Summary','Environment','Inputs & Outputs','Step-by-Step Instructions','Edge Cases & Failure Modes','Acceptance Criteria','Do NOT']
        marker=f'{n+1}. {titles[n]}\n'
        _old,right=rest.split(marker,1)
        return left+start+'\n'+content.strip()+'\n\n'+marker+right
    return left+start+'\n'+content.strip()+'\n'
code=(PLAN/'CODE-AI-NEXT-AFTER-V8-RECHECK-2026-10-05.txt').read_text()
code=section(code,1,'Task Summary',f'''You are the owner-selected CODE EXECUTOR. Execute the entire remaining eight-age game build in C:/dev/ages-of-dominion-reborn against the OWNER-APPROVED VERTEX LANDSCAPE MOCKS. The owner has explicitly rejected the current portrait-card/stick-figure entry, rough Kingdom plots, blueprint maps, dancing static Army pictures, empty Forge rectangles and generic controls. Deliver the complete visually recognizable and playable game, with visible results the owner can inspect after each meaningful screen/flow delivery. Construct one consistent Stone visual/playable foundation, then apply it across all eight ages and every support/mode screen without stopping at Stone. Final polish follows the whole build; do not hide unfinished screen construction behind that deferral. Keep existing correct mechanics and saves. This is execution, not a request for another plan, and no new paid image/device/Git authority is granted. Image AI independently delivers existing-source local assets; consume each verified row without waiting for whole-art readiness. Current priority supersedes earlier bug-first/test-first/texture-optimization-first stopping points. Complete all independently ready work; publish exact scoped blockers, visible evidence and a durable resume only when something truly cannot proceed. Read docs/plan/{BRIEF} for this owner clarification.''')
code=code.replace('Current baseline:',mockmap+'\nCurrent baseline:')
steps=[
'Capture the latest read-only source/tool/checkpoint snapshot while preserving all intervening executor changes.',
'Read the canonical mechanics and the actual30approved landscape mock pixels using the target mapping above.',
'Create one complete per-screen/per-age visual and playable work queue with known blockers separated from later polish.',
'Save baseline runtime screenshots for the rejected Home/Hero/Kingdom/Adventure/Army/Forge/Defense states in an isolated context.',
'Create the local review-gallery scaffold with approved references, baseline screenshots and explicit unimplemented labels; update the relevant row immediately when each following screen/flow is delivered.',
'Build the Home screen around mock01 with the correct title, landscape scenic composition, designed Continue/New/Load/Settings controls and truthful save/empty/recovery states.',
'Build the class-selection and Hero interfaces around mocks19–21 with correct portraits/kits, actual stats/equipment/skills/spells and no unsolicited schematic figure beside a portrait.',
'Build the shared slate/stone/brass interface components for navigation, contextual panels, buttons, icons, resource rails and result dialogs using accessible real controls.',
'Build Stone Kingdom around mocks02–03 with17empty sites plus Hall1/separate unbuiltWalls, clear selection, real empty/scaffold/completed/upgrade visuals, grounded building placement and unobscured build actions.',
'Verify real Kingdom build/upgrade/resource/cancel/reload consequences against its new visible states without changing frozen geometry or covering baked content with arbitrary opaque rectangles.',
'Build Adventure around mocks11–13 with usable painted terrain/layers, truthful sites/fog/routes/crossings/selection and grounded visible travel consistent with the16x10legal world.',
'Build the Army roster around mock24 with readable cards/portraits, true counts/ranks/stats/capacity/recruit/reinforce controls and grounded stable figures rather than whole-image dancing.',
'Build Forge and Inventory around mocks22–23 with recognizable slot icons/cards, selected/worn equipment, actual quality/cost/affordability, item artwork or truthful empty states, compare/confirm/cancel/equip/unequip/bag flows.',
'Build Tactical deployment/action/result around mocks14–16 with registered terrain, grounded armies, visible commander/turn queue/count/health/action previews and usable contextual actions on the7x10board.',
'Repair Retreat modal isolation so every background control is inert, keyboard focus stays in the dialog and cancel/Escape/confirm preserve documented once-only consequences.',
'Verify manual Tactical move/melee/shoot/spell/wait/defend/auto/retreat/flyer/result actions against the rendered states while retaining the already repaired redraw-safe input.',
'Build Defense preparation/live results around mocks17–18 with visible terrain/lane/gate/pads/towers/attackers/hero/army, real wave preview/telegraphs/abilities/pause/2x and fixed1/60simulation.',
'Build every five-War setup and outcome flow for Siege/TacticalDuel/Endless/isolatedSkirmish/localshared-seedChallenge with visible consequences and no practice leakage.',
'Build Story/quests/tutorial around mocks25–27 with seven chapters/Futureconclusion, six quests/eight milestones/rival/branch claims and contextual step guidance.',
'Build Market and all support/save interfaces consistently with mocks28–30, including local music/SFX/reducedmotion/help/credits/privacy/slots/import/export/backup/recovery.',
'Integrate each individually verified Image successor asset at its documented semantic role/size/pose/contact coordinates while preserving immutable source art.',
'Record a specific per-scene proposal when a source-backed visual mismatch requires geometry changes; keep affine[60,-10,25,35,170,165]/Hall0.1312active until explicit coordinated review.',
'Extend the complete visual/gameplay system across all eight Kingdom ages, three troop families per age, era-specific class kits/towers/buildings/gear/biomes and Future ending without merely retinting Stone.',
'Complete remaining eight-class progression, nine skills/eight spells, eight neutral creatures/four flyers, six equipment slots/four qualities/ten artifacts and frozen economy/age-gate rules through their visible interfaces.',
'Record a natural isolated build/recruit/travel/manualguard/earn-or-legally-craft/compare/equip/return/preparedSiege/settle/save/reload journey with ordinary controls and real production.',
'Verify all other mode/support/age paths with appropriate labeled browser scenarios, preserving the distinction between natural progression and injected all-age/state fixtures.',
'Compare actual reference-versus-runtime pixels for every mapped screen/state at825x375,933x424,1180x820,1280x720 with uniform camera fit, safe areas, readable text,48CSSpx action controls, focus and state-preserving portrait rotate.',
'Publish a new local side-by-side review gallery and evidence JSON immediately after each meaningful visual/flow delivery so the owner can see actual progress while other ready work continues.',
'Run focused correctness regressions for substantive changes while leaving cosmetic micro-polish and nonessential performance optimization on the later queue.',
'Run the complete Node24suite after the whole current build with honest counts/exit codes and the unchanged exact-guide evidence caveat.',
'Build the current web and unsigned static preview APK after actual substantive changes with source/dist/www/APK closure, CRC, previewID/SDK/zero-permission evidence and no device work.',
'Refresh every current requirement row and whole-build checkpoint from actual visual/playable evidence with remaining core blockers and a separate polish queue.',
'Return the live URL, exact launch command, review-gallery URL/path, screenshots/short captured interaction clips, changed symbols, verification results and precise resume actions while continuing every unblocked whole-build task.'
]
code=section(code,4,'Step-by-Step Instructions','\n'.join(f'{i+1}. {s}' for i,s in enumerate(steps)))
code=code.replace('5. Edge Cases & Failure Modes\n','5. Edge Cases & Failure Modes\n\n- Basic Home/layout/terrain/plot/button/card construction is required now. Final polish deferral does not excuse the rejected blueprint/empty-box/stick-figure interface. Subtle animation/FX/material refinements and nonessential atlas/package optimization can wait.\n- An Image or geometry block keeps the affected visual row FAIL/BLOCKED; build every other screen and flow. Do not silently substitute a distorted full mock screenshot or claim that unseen ground/anatomy was recovered.\n- The complete build and owner acceptance are separate: READY_FOR_OWNER_REVIEW requires visible whole scope and documented limitations, never a blanket finished-product claim.\n')
criteria='''[ ] The primary comparison set is the approved30Vertex LANDSCAPE mocks; earlier vertical layouts and generated content mistakes are not adopted as runtime authority.
[ ] Home/entry/class selection is visibly designed and useful; the portrait-plus-dancing-stick-figure presentation is gone.
[ ] Every main/support screen has real working controls in its intended visual composition; plain debug interfaces are not offered as completed screens.
[ ] Kingdom clearly shows lawful empty/building/scaffold/upgrade/wall states with sensible grounds/selection; known baked-content/geometry conflicts remain explicitly failed until resolved.
[ ] Adventure/Tactical/Defense present appropriate painted, registered scenes and true live objects; blueprint-only display fails the core visual gate.
[ ] Army/Hero/Forge/Inventory show meaningful cards/icons/gear/stat states and truthful available figure use; no whole-image dance is passed as character articulation.
[ ] All eight ages/eight classes and all three modes/fiveWar flows are present with frozen mechanics, progression, assets/era identity and actual usable interfaces.
[ ] Story/Future/quests/milestones/rival/tutorial/Market/local support/save workflows are implemented and browser-demonstrated; pure engine tests are insufficient UI evidence.
[ ] Natural Stone play covers construction/real production/recruitment/travel/manualcombat/gear/preparedDefense/once-onlysettlement/save/reload; fixtures and defeat results are labeled honestly.
[ ] Six functional slots/fourqualities/tenartifacts, three troopfamilies perage, eightcreatures/fourflyers, nineskills/eightspells and fourresources remain full scope.
[ ] Every mapped view has actual reference-versus-runtime captures with correct viewport/state/source hashes and differences; all four landscape sizes and portrait preservation are covered.
[ ] Accessible48CSSpx action alternatives/readable text/focus/modal isolation/save safety/legal spends/settlements hold throughout the core build.
[ ] The review gallery shows produced runtime states and working-flow evidence with the correct live URL; mock-only galleries/test-count summaries do not satisfy delivery.
[ ] New Image bindings pass appropriate source/semantic/size/transform/contact checks; frozen geometry/originals/partial limits remain protected.
[ ] Final tests and static package metadata/closure are recorded honestly; missing exact guide failures remain nonzero and devices remainSTOPPED.
[ ] Remaining core visual/playable gaps and deferred optional polish are separate queues; no unfinished age/screen is relabeled polish.
[ ] Current per-ID records and checkpoint remainINCOMPLETE whenever required build gates fail; owner acceptance/native performance are never fabricated.'''
code=section(code,6,'Acceptance Criteria',criteria)
code=code.replace('7. Do NOT\n','7. Do NOT\n\nDo not deliver another mostly invisible rules/asset-processing pass. Do not postpone the basic approved screen appearance until after a blueprint game is declared complete. Do not stop after Stone, a modal fix, a test run or one passing screen. Do not demand pixel-perfect final polish before extending the coherent visual build across the whole game. Do not add unnecessary idle schematic figures or oscillate entire roster artwork as a substitute for grounded animation.\n')
(PLAN/CODE).write_text(code,encoding='utf-8')
image=(PLAN/'IMAGE-AI-NEXT-AFTER-V8-RECHECK-2026-10-05.txt').read_text()
image=section(image,1,'Task Summary',f'''You are the owner-selected IMAGE/LOCAL-ASSET EXECUTOR. Prioritize the assets and registration needed to turn the existing prototype into the complete OWNER-APPROVED VERTEX LANDSCAPE visual/playable game. Prepare all feasible existing-source scene layers, era-correct subjects, usable character/card/slot/icon assets, measured transforms and source-backed geometry proposals for every age and screen, with actual assembled comparison images that the owner can inspect. Start with the shared Stone visual grammar, then continue all eight ages and support/mode surfaces; do not stop at inventory or one class. Code AI builds the game concurrently and consumes each individually verified delivery. Basic usable scene/subject assets are build work now; fine matte refinement/cinematic animation/optional material polish follows the whole build. Missing source anatomy/hidden ground remains a scoped explicit failure rather than fabricated pixels or paid regeneration. Current authority is LOCAL EXISTING-SOURCE ONLY, NO_NEW_PAID_CALLS; no game/device/Git/storage/provider work or dispatch. Read docs/plan/{BRIEF} for this owner clarification.''')
image=image.replace('Current Image inputs:',mockmap+'\nCurrent Image inputs:')
# Retain complete prior finite-source method instructions and exact historical limitations.
image=image.replace('4. Step-by-Step Instructions\n','4. Step-by-Step Instructions\n')
body=image.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0]
oldsteps=re.findall(r'(?m)^\d+\. (.*)$',body)
assert len(oldsteps)==30
newsteps=[
'Read the actual approved30LANDSCAPE mock images and build a full per-screen/per-age visible asset-delivery queue mapped to the filenames above.',
'Publish a compact source-to-target plan for immediate Home/Kingdom/Adventure/Army/Forge/Tactical/Defense/Hero/support artwork needs with truly unavailable anatomy/ground separated from optional polish.',
]+oldsteps
newsteps.insert(18,'Prepare usable cards/slot silhouettes/equipment/resource/skill/spell/button-icon material crops from existing correct sources with tight bounds, intended display size, contrast/background scope and semantic identity; use CSS/native vector chrome in Code where no bitmap is needed.')
newsteps.insert(27,'Produce reference-versus-assembled target composites for Home/StoneKingdom/Adventure/Army/Forge/Tactical/Defense and each delivered age using only actual source-backed parts, uniform camera fit, representative sparse/developed/action states and explicit missing layers.')
newsteps.insert(28,'Publish a new local side-by-side Image review gallery with reference/actual composite/alpha-background diagnostics/short supported-pose clips, per-row hashes/coordinates/limitations and exact delivery paths for Code; label every image ASSET_COMPOSITE rather than live gameplay.')
newsteps[-1]='Return the full ready interface/recipe/checkpoint delivery and visible review-gallery paths with reusable/complete/partial/failed/blocked counts, every remaining build gap and a separate optional-polish queue; continue independent ready IDs without awaiting full-art flag or owner review of unrelated rows. If a real tool/context/time limit interrupts, publish INCOMPLETE with the exact resume action.'
image=section(image,4,'Step-by-Step Instructions','\n'.join(f'{i+1}. {s}' for i,s in enumerate(newsteps)))
image=image.replace('5. Edge Cases & Failure Modes\n','5. Edge Cases & Failure Modes\n\n- The approved landscape scene layout and core usable assets are current build work; matte micro-cleanup and cinematic refinements may be later polish when they do not destroy readability, anatomy or placement. Do not hide a wrong-role standing/prone mismatch or missing ground as polish.\n- Deliver independent useful rows as soon as verified, with assembled pixels. No need to wait for all32scenes/all8rigs; whole scope stays in the finite queue. Code owns runtime UI/gameplay and CSS/vector chrome; do not make bitmap preparation a global prerequisite for real buttons.\n- Reference-versus-composite evidence supports local appearance only. Code must prove corresponding runtime placement/control behavior; Image cannot declare game playable from source composites.\n')
image=image.replace('6. Acceptance Criteria\n','6. Acceptance Criteria\n\n[ ] Approved30LANDSCAPE targets are the primary layout/composition reference and every relevant age/screen has a current asset queue.\n[ ] Newly usable rows have actual assembled comparison pixels at intended size, not only crop inventories/mask metrics.\n[ ] A local reference-versus-composite gallery shows immediately consumable results, source/transform/semantic limits and every unresolved core build gap.\n[ ] Core scene/role/registration/body gaps remain separate from optional fine polish; no unfinished primary asset is silently declared polished or ready.\n')
image=image.replace('7. Do NOT\n','7. Do NOT\n\nDo not return another invisible preparation-only pass, a gallery of unassembled source paintings, or a mock-only image collection as the visual result. Do not wait for pixel-perfect fine cleanup before releasing independently usable rows. Do not introduce new paid generation or expand the three-role unsubmitted draft.\n')
(PLAN/IMAGE).write_text(image,encoding='utf-8')
# Verify document structure, numbering and all canonical mock inputs without executing helpers.
result=[]
for name in [CODE,IMAGE]:
    text=(PLAN/name).read_text()
    headings=re.findall(r'(?m)^[1-7]\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',text)
    assert len(headings)==7,(name,headings)
    body=text.split('4. Step-by-Step Instructions\n',1)[1].split('5. Edge Cases & Failure Modes\n',1)[0]
    nums=[int(n) for n in re.findall(r'(?m)^(\d+)\. ',body)]
    assert nums==list(range(1,len(nums)+1))
    result.append({'path':'docs/plan/'+name,'sections':len(headings),'steps':len(nums),'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest()})
mocks=[]
for p in sorted((ROOT/MOCKDIR).glob('*.jpg')):
    mocks.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
assert len(mocks)==30
(Path(__file__).parent/'prompt-and-reference-check.json').write_text(json.dumps({'prompts':result,'primaryMocks':mocks},indent=2))
print(json.dumps({'prompts':result,'primaryMocks':len(mocks)},indent=2))
