"""Write three complete owner-copyable execution briefs. Planner documentation only."""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PLAN=ROOT/'docs/plan'
header='Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; Node >=24, bundled v24.19.0 independently verified 6 October 2026. Custom scripts/serve.mjs and scripts/build.mjs; npm dev is not Vite. Local art: Python 3.13.7 / Pillow 12.3.0 / NumPy 2.5.3 / OpenCV 5.0.0 / SciPy 1.18.1 verified at C:/Python313/python.exe. Android recorded configuration: Java 21 / Gradle 8.11.1 / AGP 8.7.3 / androidx.webkit 1.12.1 / compile-target 36 / min 24; toolchain not remeasured by planner.\n'
environment='''Work only in C:/dev/ages-of-dominion-reborn, using the current checkout and preserving intervening changes. Planner snapshot on 6 October: main HEAD c266e220fa024dfb95fbf534f180c40ed52585e3, git status --short empty; recheck without resetting. C:/dev/ages-of-dominion and C:/dev/aod-art-src are read-only requirement/data/art sources. Do not copy old gameplay/core/client source, bundles, saves or archived starters. Original rasters may be hard-linked: never overwrite originals or existing derivatives in place. Create new derivatives inside your exclusive directory.

Verified Node executable: C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe. Use it explicitly and put its bin directory first only in the current process PATH if a child script invokes node. Existing package scripts: dev=node scripts/serve.mjs; test=node --test tests/*.test.mjs; build=node scripts/build.mjs; build:apk=node scripts/build-apk.mjs. Inspect arguments before use. Reuse installed libraries; do not install unsolicited dependencies or change global configuration.

Latest owner instruction asks these three executors to complete the whole visible/playable game, with final fine polish afterward. This supersedes historical portrait, no-code and Stone-only stopping points for the Code executor. Primary layout is LANDSCAPE for the whole game. Planner chat remains verifier only; you are the separately owner-selected executor for your named scope. Do not dispatch/message another executor or spawn agents. Publish files for owner-mediated handoff.

NO_NEW_PAID_CALLS: purchased 17 batches, 32 native4K and 73 native2K already have outputs. No repurchase, retry, fallback, batch18+, reserve spending, provider/account/project/job/bucket query, login, billing/IAM change, generation runner or live lock/budget mutation. Three-role draft remains exactly Stone Clubman, Stone Slinger WITH SLING, Industrial STANDING Sharpshooter, DRAFT_NOT_SUBMITTED / OWNER_BUDGET_AUTHORIZATION_REQUIRED; do not add Bronze heavy. Bronze Charioteer is crew/horses/vehicle as one logical unit.

Runtime is entirely local with zero declared/granted device permissions including INTERNET and VIBRATE. Device work is STOPPED: no physical-device query/install/test. Preview ID com.agesofdominion.game.reborn.preview; permanent metadata com.agesofdominion.game. No signing/store/cloud/deploy, Git/index/history changes, archive restoration/cleanup/upload/storage migration. Frozen Kingdom affine [60,-10,25,35,170,165] and Hall scale 0.1312 require coordinated versioned review before activation of a change.

Assumptions: current accepted direction is the 30 landscape mocks; owner has not accepted the current runtime; local-only source-supported repair is authorized; external/device/paid work is excluded. If an assumption fails, record the exact affected ID/input and continue independent authorized tasks. Do not silently invent source anatomy, mechanics or acceptance.
'''
inputs='''Read AGENTS.md, START-HERE.md, CURRENT-STATUS.md, DECISIONS.md, docs/SESSION-HANDOFF.md, docs/BUILD-PROGRESS.md and the reading order in docs/plan/README.md, interpreting dated authority over historical banners. Current audit: docs/plan/BOTH-AI-INDEPENDENT-AUDIT-2026-10-06.md. Ownership/dependencies: docs/plan/THREE-AI-OWNERSHIP-2026-10-06.md. Owner priority: docs/plan/VISUAL-PLAYABLE-BUILD-OWNER-PRIORITY-2026-10-05.md. Mechanical authority: docs/plan/FULL-IMPLEMENTATION-SPEC.md, MASTER-PLAN.md, IMPLEMENTATION-CONTRACT.json (and active src/data/implementation-contract.json), GAME-DATA-REFERENCE.json, DATA-ADOPTION-LEDGER.json, SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md, REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md and WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md. Recheck existing implementation before declaring a feature absent.

Primary visual images: design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/. Actual pixel mapping, filenames relative to this directory:
- 01-home.jpg: Home; 02-kingdom-day1.jpg: sparse Day1; 03-kingdom-stone.jpg: developed Stone.
- 04-kingdom-bronze.jpg, 05-kingdom-iron.jpg, 06-kingdom-medieval.jpg, 07-kingdom-gunpowder.jpg, 08-kingdom-industrial.jpg, 09-kingdom-modern.jpg, 10-kingdom-future.jpg: the other seven Kingdom ages.
- 11-adventure-overview.jpg, 12-adventure-crossing.jpg, 13-adventure-foot.jpg: Adventure states.
- 14-tactical-deployment.jpg, 15-tactical-action.jpg, 16-battle-result.jpg: Tactical deployment/action/result.
- 17-defense-preparation.jpg, 18-defense-wave.jpg: Defense preparation/action.
- 19-hero-equipment.jpg, 20-skills.jpg, 21-spells.jpg: Hero/equipment/skills/spells.
- 22-forge.jpg, 23-inventory.jpg, 24-army.jpg: Forge/Inventory/Army.
- 25-story.jpg, 26-quests.jpg, 27-tutorial.jpg: Story/quests/tutorial.
- 28-settings.jpg, 29-save-recovery.jpg, 30-icon-material-board.jpg: Settings/recovery/UI materials.
assets/mocks/INDEX.md also maps earlier 26 supplied vertical references. Those are style/content/art sources, not primary layouts. Open actual images. Correct generated mistakes: title Ages of Dominion, canonical Stone rather than medieval kit, true Future rather than rural carryover, six real slots, canonical gear/data, no photographed device frames or duplicate icon meanings. Do not use full mock JPEGs as fake interactive game backgrounds.

Complete scope retained: eight ages Stone/Bronze/Iron/Medieval/Gunpowder/Industrial/Modern/Future; eight classes Knight/Ranger/Warlock/Mage/Paladin/Barbarian/Necromancer/Healer; Kingdom17pads + Hall + separate Walls and ten building types townhall/farm/lumber/quarry/mine/barracks/workshop/hall/armory/walls; Adventure16x10 continuous terrain; Tactical7columns x10rows, commander(0,9); Defense9x15 fixed1/60, four tower families and five attacker roles, real hero/army deployments. Four resources food/wood/stone/gold; six slots helm/weapon/offhand/armor/boots/accessory; four qualities Crude/Fine/Master/Relic; ten artifacts; three troop families per age; eight creatures wolf/bandit/bear/harpy/golem/griffin/wyvern/drone, four flyers harpy/griffin/wyvern/drone; nine skills; eight spells; seven story chapters + Future conclusion; six quests; eight milestones; rival and tutorial. Forge/Inventory/Market, music/SFX, reduced motion, help/credits/privacy, safe saves/import/export/slots/backup and all five War choices Siege/Tactical Duel/Endless/isolated Skirmish/local shared-seed Challenge remain required.

One connected campaign with idempotent spend/settlement; practice cannot change campaign XP/mana/resources/rewards/casualties/story. Preserve canonical equations/table IDs and command/save contracts. Positive morale's precise extra-turn effect is still undecided; isolate that affected mechanic, never guess or globally halt. Every age/screen must be built, not only Stone. Viewports825x375,933x424,1180x820,1280x720; portrait accessible rotate gate preserves state; actions >=48 CSSpx and readable text.

Build now: coherent Home/class selection, scene composition, real art/plots/buildings/cards/buttons, grounded figures, legal gameplay/feedback, all screens/ages and safe input/saves. Later polish: fine materials/micro-spacing/extra particles/cinematics/nonessential optimization. Blueprint-only terrain, missing building states, empty generic chambers, ungrounded whole-image dancing and absent age/screen are build failures. Correct static figures can be truthful interim display but do not close articulated gait or complete class-body requirements.

Fresh bounded baseline: 100 Node tests /98 PASS /2 exact historical-guide ENOENT; corrected independent browser20/20PASS, separate visual-shell16/16PASS, actual appearance still incomplete. Cancel returns focus to body (empty active ID), so restore-trigger focus remains a concrete accessibility repair. Existing unsigned APK3cc5bccdddcad1f1119b57025e480968e52581d6b10b55938125c8bd34964714 /410291618 bytes /300 matching source-dist-www-APK files /CRC and zero permissions static PASS; no device test. Image v9:19 ready rows, all32scenes PARTIAL/0promoted, eight full class chains incomplete;167 interface-associated file bindings hash/decode PASS,15 ready raster dimension/alpha checks and12 bounded joint metrics reproduce. Code Army draw asks130 legalpx for review plates and200 for stacks; Gunpowder heavy/Future ranged/Future heavy delivery limit remains64px. Respect actual visible CSS size plus metadata limits; do not extend by assumption.

Fresh 1280x720 Army measurement: cannon visible alpha16 HEIGHT57.55 CSSpx, Future ranged84.05 and Future heavy79.99; all image canvases102.58 CSSpx high. Future visible-height use exceeds64; cannon height alone does not establish a violation. Check whether each legacy64px acceptance means height or longest visible dimension before enforcing a cap. Current eight-age developed Kingdom fixtures also visibly retain magenta guide/sheet patches around some building layers and a dashed perimeter; eliminate those build defects through correct source-backed matte/binding and appropriate built/unbuilt Wall states, never call them polish.

Current art evidence: docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json; docs/plan/IMAGE-LOCAL-DELIVERY-V9-HANDOFF-2026-10-05.md; qa/image-local-delivery-v9-20261005/{checkpoint.json,scenes.json,screen-queue.json,healer-heads.json,joint-remeasure.json,new-joint-attempts.json,review/index.html}; older v4-v8 immutable. Reused14v8rows plus five Healer head cards are bounded ready; heads are not bodies. Healer boot hash4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21 remains successful135x131 cleanup,12474 alpha>16 foreground pixels. Knight thigh/greave13attempts and failed Paladin links must not be restarted. V9 Healer head/torso and skirt/leg attempts failed. Industrial coat hole, Modern heavy slab, Modern ranged snow and missing standing Sharpshooter remain scoped. Canvas conventions now named but complete consumable transform chains still require explicit validated matrices.

Stone has four coarse road traces, banks and deck16px uncertainty; roads/banks24-40px, no walkable polygons.31other scene IDs still untraced. V9 excludes stale ridge traces; its viewport sheets use uniform scale/CSS chrome but are ASSET_COMPOSITE, not gameplay or registration proof. Corrected int16 arithmetic8scenes/13360candidate pixels is not river accuracy. Missing exact guides: qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png,52050bytes/SHA256609d3195018ccf448f339f79e45fe90b9e5adfb2859674e40383144d2106f848; v5-guide.png,33988bytes/SHA256673492a6a1c6780eb77d9b0b24f7eefe30a98dc119c7fbee9e3edef088b8c1ff. Do not fabricate, weaken tests or restore archives to hide absence.
'''
contracts='''Typed handoff shared by both local-art producers; each writes only its own interface:
Gate = PASS|FAIL|UNVERIFIED|BLOCKED|NOT_APPLICABLE.
Affine6 = [a:number,b:number,c:number,d:number,e:number,f:number]; image x'=a*x+c*y+e,y'=b*x+d*y+f, +y down. BoxXYXY is half-open; DimensionsWH={width:int,height:int}; XY=[x:number,y:number].
ArtifactRow={id:string,role:string,age:int0..7|null,classId:string|null,status:READY|PARTIAL|FAIL|BLOCKED,source:{path:string,sha256:SHA256,roi:BoxXYXY|null},output:{path:string,sha256:SHA256,dimensions:DimensionsWH}|null,sourceToOutput:Affine6|null,intendedUse:string,maxDisplayCssPx:number|null,side:LEFT|RIGHT|UNKNOWN|NOT_APPLICABLE,groundContact:XY[]|null,footprint:XY[]|null,entrance:XY|null,heightEnvelope:BoxXYXY|null,frame:string,transforms:object,gates:{binding:Gate,semantics:Gate,matte:Gate,spatial:Gate,articulation:Gate,runtime:Gate,owner:Gate},evidencePaths:string[],limitations:string[],blockedBy:string[],nextAction:string|null}. NOT_APPLICABLE requires a reason. Missing field stays explicit null with an affected gate, not guessed.
ArtInterface={schema:1,producer:ENVIRONMENT|ACTORS,version:string,inputSnapshot:object,rows:ArtifactRow[],readySubset:string[],wholeDeliveryReady:boolean,reviewGallery:string,checkpoint:string}. READY applies only to the declared role/size/pose; wholeDeliveryReady cannot promote partial rows. Each source/output path and hash must resolve before delivery.
VisualRow={id:string,screen:string,age:int0..7|null,stateKind:NATURAL|FIXTURE|ASSET_COMPOSITE,referencePaths:string[],referenceHashes:SHA256[],actualPaths:string[],viewport:[int,int],sourceSnapshot:object,checks:{composition:Gate,placement:Gate,readability:Gate,stateTruth:Gate,playability:Gate},differences:string[],ownerAcceptance:UNVERIFIED|ACCEPTED|REJECTED}.
Checkpoint={status:INCOMPLETE|READY_FOR_OWNER_REVIEW,completedIds:string[],partialIds:string[],failedIds:string[],blockedIds:string[],nextExecutableActions:object,sourceHashes:object,evidencePaths:string[],polishQueue:object[],authorityLimits:string[]}. No technical count establishes visual or owner acceptance.

Release artifacts atomically after final validation. File paths/hashes are immutable handoff inputs; publish a new version for corrections. Do not overwrite another producer's interface, derivatives, helpers, scene queue or checkpoint. Never write root CURRENT-STATUS/SESSION-HANDOFF/BUILD-PROGRESS/README or canonical shared ledgers concurrently: each publishes its own handoff; planner/owner merges current pointers. Code alone owns runtime catalogs/source and integration. Art producers may inspect Code read-only to obtain frame/picking contracts; no runtime edits.

Every meaningful delivery includes a LOCAL HTML gallery showing unchanged approved reference beside actual produced result at intended size, state/viewport/hash/remaining differences. Art labels all composites ASSET_COMPOSITE with playabilityUNVERIFIED. Code publishes live URL + exact launch command, real runtime captures and ordinary interaction evidence. Source-only contact sheets, mock-only galleries, crop counts or package names do not meet this contract. Continue independent work while owner review is pending.
'''
environment_summary='''You are AI 1, the owner-selected LOCAL ENVIRONMENT ART executor. Complete all independently feasible environment, building/site/Wall/tower, scene geography and UI-material delivery needed for the whole eight-age/every-screen game using existing purchased sources. Deliver immediately usable rows and reference-versus-composite evidence, keeping impossible hidden ground or frozen-geometry conflicts explicit per ID. AI 2 owns characters/equipment; AI 3 owns all runtime construction. This is execution of local production, not another plan or a global wait for all art. Establish Stone material/camera grammar, then cover every age/biome/screen in the same task. Exact full completion cannot be claimed while required rows remain blocked.'''
actor_summary='''You are AI 2, the owner-selected LOCAL CHARACTER AND EQUIPMENT ART executor. Complete all independently feasible hero/class-kit, Army/troop/creature/attacker, mount/vehicle, gear/artifact and articulated-part delivery needed for the whole eight-age/every-screen game from existing sources. Deliver correct static art where appropriate, valid parts/subchains where full bodies are impossible, and actual source-backed assemblies. Preserve exact failed/exhausted methods and size/pose limits. AI 1 owns scene/world/UI art; AI 3 owns runtime construction. Execute the full finite source-supported queue, not a head-only or inventory-only pass, without new paid calls or invented anatomy.'''
code_summary='''You are AI 3, the owner-selected CODE executor. Complete the entire independently authored, visually recognizable and playable eight-age game in this repository against the approved30landscape mocks. The latest shell improves Home/portraits/backgrounds/modal isolation but remains an unfinished build: registered mutable Kingdom/buildings, coherent Adventure/Tactical/Defense, designed Army/Forge/support screens and whole journeys still need construction. Build Stone visual grammar, then every age and every screen in this task. Consume AI1/AI2 verified rows incrementally; complete all layouts, rules, accessibility and support independent of art. Publish actual runtime comparison galleries and demonstrated player flows. Final fine polish follows whole construction. Do not stop after three fixes, use art blockers as a global halt, or claim whole completion with missing primary scenes/rigs.'''
env_owned='''Exclusive writable ownership: assets/derivatives/environment-20261006/ for new terrain/layers/world/static tower/UI outputs; qa/environment-art-20261006/ for your scripts, recipes, masks, geography, composites, gallery, checkpoint and handoff; docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json for your interface. Version descendants only inside these prefixes. Existing shared scripts/image_*.py and v9 inputs are read-only. Resource/skill/spell/navigation/button-material icons belong to you; equipment/artifact item images belong to AI2. Stationary towers/Wall/building FX belong to you; attacking actors/hero/troop FX belong to AI2. No source/catalog/code/shared-pointer edits.'''
act_owned='''Exclusive writable ownership: assets/derivatives/actors-equipment-20261006/ for new characters/gear/parts/clip derivatives; qa/actors-equipment-20261006/ for your scripts, recipes, masks, assemblies, gallery, checkpoint and handoff; docs/plan/ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json for your interface. Version descendants only inside these prefixes. Existing shared scripts/image_*.py and v9 inputs are read-only. You own six-slot gear/artifact imagery, hero/troop/creature/attacker/mount/vehicle art and actor FX; AI1 owns terrain/buildings/Wall/towers/world sites/resource/skill/spell/navigation materials. No runtime/catalog/geography/shared-pointer edits.'''
code_owned='''Exclusive writable ownership: independently authored src/, index.html/runtime styles, Code-owned data/catalogs/consumer manifests, tests/, Code build/serve/package helpers, dist/, android/ static preview output and qa/code-whole-build-20261006/ with your gallery/checkpoint/handoff. Respect existing image helpers: do not edit scripts/image_*.py or image-owned controls. Package manifests/locks change only if necessary and justified; no unsolicited dependencies. You alone integrate runtime catalogs and consume docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json and ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json. Never write either interface or producer directories. Inspect current readySubset and verify hashes; a not-yet-delivered row remains scoped. If legacy paths must be retained for passing rows, bind unchanged bytes with their limits and attribution. Shared current-pointer documents are planner/owner-merged; publish your exclusive handoff instead.'''
env_steps=[
'Record a read-only source/interface/contract snapshot for your exclusive local-art queue.',
'Inspect actual approved landscape pixels for every environment and supporting-screen composition.',
'Build a per-ID queue from the existing32scene rows and actual building/site/Wall/tower/UI catalogs, separating reuse, feasible repair, exhausted methods and unavailable ground.',
'Release unchanged adequate world/UI rows through your own versioned interface with current hash/decode evidence.',
'Inspect native Stone ground and the v9 four road tracks, both banks, bridge/deck and central rock-ring pixels independently of legal overlays.',
'Refine Stone source-backed road corridors, approach/deck polygons, obstacles and walkable ground with uncertainty sufficiently small to assess complete legal footprints.',
'Trace Bronze geography from its own source preview rather than copying Stone coordinates.',
'Trace each remaining Kingdom age using a per-source manual or genuinely different bounded method.',
'Trace each Adventure/Tactical/Defense scene ID using its actual roads, banks, crossings, lanes, legal stopping ground and obstacles.',
'Map baked immutable scenery versus mutable buildings/roles/HUD/guide marks for each required sparse, developed and battle state.',
'Compare full site/corridor/contact/height envelopes with painted features under the active contract, including17pads/Hall/separateWalls and mode topology.',
'Publish a versioned geometry/camera proposal with picking and four-viewport implications for each source-backed conflict that cannot pass the frozen contract.',
'Prepare feasible scene-layer candidates only from available correctly registered source pixels; mark hidden required ground unavailable where local recovery cannot establish it.',
'Extract intact age-correct buildings for all ten types and meaningful construction/completed/upgrade states without synthesizing unseen structures.',
'Deliver Wall joins/perimeters, Adventure sites, four tower families and role-specific static props with base/contact/entrance/height/depth/facing metadata.',
'Prepare available Home/Army/Forge/Story/support environmental scene layers from existing sources without baking mutable UI or actors into background roles.',
'Prepare tight resource/skill/spell/navigation/material crops with correct semantic mapping and intended icon size; leave native CSS/vector chrome to Code.',
'Render every new annotation overlay from final annotation data with source/contract hashes and an explicit legend; exclude all withdrawn ridge candidates.',
'Render sparse/developed/action ASSET_COMPOSITE comparisons using uniform source-camera scaling and actual chrome/panel safe areas at all four landscape sizes.',
'Publish a local side-by-side approved-reference/result gallery covering each delivered age/mode/support environment with missing layers disclosed.',
'Validate all newly claimed/reused bindings, decode, transforms and original-input preservation once after final changes.',
'Publish ENVIRONMENT-ART-INTERFACE-2026-10-06.json containing exactly verified readySubset rows with geometry proposals kept PROPOSED until coordinated review.',
'Publish your exclusive full queue/checkpoint/handoff with all completed, partial, failed and blocked IDs and an exact next executable action per unresolved row.',
'Continue every remaining independent feasible environment task; if context/tool limits interrupt, preserve INCOMPLETE and a precise resume rather than declaring whole delivery ready.'
]
act_steps=[
'Record a read-only snapshot of existing character/gear sources, v9 ready rows, failed methods and canonical identities.',
'Inspect approved Hero/Army/Forge/Inventory and mode targets at actual intended display sizes.',
'Build a finite source-region queue covering eight classes/four kit eras,24troop roles,eightcreatures,fiveattackerroles,mounts/vehicles,sixslotgear/fourqualities/tenartifacts and actor FX where applicable.',
'Release unchanged adequate19v9ready rows belonging to your scope with binding, semantic, size and pose limits retained.',
'Preserve successful Healer boot bytes and the twelve reproduced bounded joint results without reopening placement sweeps.',
'Inspect the five new Healer head-card crops at native and intended-size white/black/neutral-green alpha composites; preserve views and UNKNOWN sides.',
'Inspect compatible Healer torso/skirt/arms/legs and each other class native semantic ROI as independent source-supported candidates.',
'Record present-but-undelivered anatomy separately from source-absent anatomy, inseparable labels/backgrounds and incompatible attachments.',
'Apply only a genuinely new bounded source-region mask or attachment method to unresolved Industrial/Modern/other actor mattes; preserve complete foreground and role-essential equipment.',
'Evaluate available independently different source-supported alternatives to failed links without restarting Knight13attempts, Paladin failures or v9 failed Healer alignments.',
'Publish explicit source-to-crop, derivative-local-to-neutral-canvas and joint-rotation matrices with named width/height, anchors, scale, sign, transform order and draw order for each usable link.',
'Validate measured links on generously padded canvases at neutral and documented-25/0/+25angles, preserving all transformed corners and foreground.',
'Inspect contact overlap within the anatomical joint ROI at alpha16/128 alongside silhouette, insertion, cuff alignment and z-order diagnostics.',
'Assemble each class into a source-backed single-scale neutral body where feasible; otherwise publish valid subchains and an exact missing-link diagram with all source regions identified.',
'Prepare grounded canonical troop/creature/attacker/static mount figures with footprint/contact/shadow/depth metadata and genuine supported directional/clip coverage.',
'Preserve Charioteer crew/horses/vehicle as one logical unit and retain essential elephant/cannon/tank parts; do not apply generic one-component rejection.',
'Retain64px limits for horse/motor/future transport and Gunpowderheavy/Futureranged/Futureheavy unless new independently inspected larger-size evidence supports a specific extension.',
'Prepare correct period/class-compatible gear/card/slot/artifact crops for all six categories using existing sources; no fabricated new item statistics or painted anatomy.',
'Publish short supported-pose/clip evidence with missing idle/walk/work/attack/hit/death/facing states explicitly open where source lacks parts.',
'Render approved-reference versus ASSET_COMPOSITE Hero/Army/Forge/Inventory comparisons for all delivered ages/classes with actual size/grounding and missing scene/UI layers disclosed.',
'Publish a local side-by-side gallery with neutral/arc/native/intended-size matte diagnostics and precise assembly limitations.',
'Validate each new/reused claimed binding, decode, matrix, dimensions, alpha bounds and input preservation after final changes.',
'Publish ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json with exact readySubset, static/part/subchain/full-rig roles and separate truthful gates.',
'Publish your exclusive whole queue/checkpoint/handoff covering every independently feasible character/equipment task and per-ID blockers, preserving unsubmitted three-role draft.',
'Continue independent feasible ROIs/classes/gear/creatures rather than stopping at Healer heads; if context/tool limits interrupt, preserve INCOMPLETE and exact resume actions.'
]
code_steps=[
'Snapshot current source/tests/catalogs and isolate your browser server/profile from the owner4173server/saves.',
'Inspect actual approved30landscape references alongside current loaded runtime screenshots before revising composition.',
'Create a full age/screen/mechanic acceptance matrix separating required build gaps, scoped art dependencies and optional fine polish.',
'Establish reusable slate/stone/brass panels, readable typography and48CSSpx contextual controls for the approved landscape visual grammar.',
'Complete Home/Continue/New/Load/Settings and eight-class selection with correct scene hierarchy, portraits and state-safe recovery.',
'Complete actual sparse/developed/construction Kingdom states for17pads/Hall/separateWalls and every building type using coherent terrain, grounded layers and picking.',
'Integrate each verified ENVIRONMENT row only after source/hash/semantic/frame/spatial checks, keeping unresolved proposals unactivated.',
'Complete age-specific Kingdom/building treatments through all eight ages without stopping at Stone.',
'Complete Adventure continuous terrain navigation, fog/sites/guards, legal route previews, movement budgeting, mounted/foot travel and return-to-town using canonical16x10topology.',
'Integrate each verified ACTORS row within declared role/pose/size limits, including grounded Army/Hero/creature/mount presentation without whole-image dancing.',
'Repair existing consumer size claims for64px-limited cannon/futuretroops/transports using actual visible CSS measurements and preserved delivery limits.',
'Complete Tactical deployment/queue/actions/preview/flyer legality/casualties/spells/Auto/confirmedRetreat/result on7x10topology with commander(0,9) separate from stacks.',
'Complete Retreat dismissal focus restoration to its surviving trigger, retaining tested modal trapping/inertness and guarding every input entrypoint.',
'Complete Defense9x15fixed-step presentation and simulation for four towers/fiveattackerroles/realheroarmy, correct lane/coverage/deployment/pause/speed/result and once-only settlement.',
'Complete all six functional equipment categories with meaningful era/class-compatible item cards, compare deltas beside confirmation, costs/qualities/craft/equip/unequip/loot/reload.',
'Complete Hero stats/mana/XP/skilltree/nineskills/eightspells using actual eligibility/prerequisites/effects and transparent disabled reasons.',
'Complete Army recruitment/capacity/stats/quantities/ranks/neutralcreatureCodex with correct static/animated identity and genuine commands.',
'Complete Inventory and Market grids/cards/trades using canonical item identities/resources and idempotent spend rules.',
'Complete seven story chapters/Future conclusion,rival,sixquests,eightmilestones and anchored tutorial with visible narrative and real progression state.',
'Complete Settings/music/SFX/reducedmotion/help/credits/privacy with local assets and safe foreground/background lifecycle.',
'Complete save/load/import/export/slots/backup/damage recovery and state-preserving portrait rotation without changing campaign state for UI gestures.',
'Complete all five War flows Siege/TacticalDuel/Endless/Skirmish/shared-seedChallenge with consistent entry/results/return and isolated practice consequences.',
'Audit full source equations/adoption ledger for any remaining unimplemented numeric rule; isolate undecided positive-morale extra-turn instead of inventing it.',
'Check every delivered screen at825x375,933x424,1180x820,1280x720 including open panels, long copy,48pxactions,readable combat labels,keyboard/touch/pointer and image-loading readiness.',
'Publish approved-reference versus actual-runtime galleries after each meaningful delivery with state/source/viewport hashes and precise visible differences.',
'Demonstrate ordinary fresh-save build/produce/recruit/travel/manualfight/earnloot/compareequip/return/prepareSiege/win/settle/save/reload journey without injected progress.',
'Demonstrate ordinary six-slot progression and every War/support flow; label any accelerated age/class/layout fixture separately from earned play.',
'Verify all eight ages/classes and biome/mode views with reproducible representative fixtures where necessary while retaining natural campaign acceptance as an independent gate.',
'Run meaningful targeted tests for changed legal rules/save/modal contracts and appropriate suite checks after broad changes; disclose exact guideENOENT separately without weakening tests.',
'Build the local web package after ready source integration and validate complete consumer asset closure against both producer interfaces.',
'Build an unsigned static previewAPK with correct ID/SDK/zero permissions after web validation; preserve prior packages and verify source-dist-www-APK hashes/CRC without device operations.',
'Publish your exclusive checkpoint/handoff with live URL/exact Node launch command/galleries/ordinary journey evidence/static package hashes and every remaining per-ID gap.',
'Continue all independent whole-build work while individual art/morale/guide/owner/device gates are pending; if context/tool limits interrupt, leave INCOMPLETE with concrete next actions.'
]
edge_common='''- A genuinely new source-region method gets one baseline and at most one justified correction with saved pixels; exhausted searches do not restart under new names. This does not exhaust untraced scenes or independent ROIs.
- Missing hidden ground/anatomy, wrong role, ambiguous side, failed matte and a frozen geometry conflict are distinct per-ID blockers. Do not warp/mirror/paint connectors or blur across unseen ground to conceal them.
- Whole-frame overlap/component counts/hash/decode/native resolution do not prove anatomy/geography/registration/playability. Blue masks may include sky; correct int16 arithmetic is necessary but not bank evidence.
- Async source loading must finish before actual-result capture. Preserve early unloaded captures as instrumentation history; do not label a fetch delay missing production art.
- Cancel/resize/reload/background must preserve state; modal acceptance covers focus containment, inert background, every action path and restore-trigger focus. A valid Escape/Cancel is not a spend or failure.
- A scene/background/card may be ready for a bounded use while full runtime/rig/owner acceptance stays open. No actor-size/pose/facing extrapolation beyond recorded evidence.
- Missing exact guide bytes keep those tests failing; no lookalike, test weakening, archive restore or invented preservation. Continue all independent scope.
- A prepared natural Siege win, all-six-slot natural equipment and earned eight-age completion remain separate from existing guard/orb/defeat journey and accelerated fixtures.
- Manual trace uncertainty must be smaller than clearance margin; full corridor/site/height envelopes and actual viewport camera/chrome matter, not point centers or stretched thumbnail sheets.
- Saved accounting/budget/invoices/UNKNOWN liabilities are historical local records, not fresh provider verification or purchase authority. Preserve them read-only.
'''
accept_common=[
'All owned IDs have current disposition/evidence/next action; complete eight-age/every-screen scope remains intact.',
'Actual approved-reference versus produced-result gallery exists with intended-size/state/source/viewport evidence and explicit remaining build gaps.',
'Primary construction gaps stay separate from fine-polish queue; no prototype chamber/blueprint/incorrect identity is marked complete.',
'No paid/provider/device/Git/storage/shared-writer operation occurred; originals/hard-linked bytes and historical outputs remain intact.',
'Ready rows preserve declared semantics/transforms/limits and separate binding/matte/spatial/articulation/runtime/owner gates.',
'Blocked rows name exact missing input/authority, feasible next action and independent work completed; no blanket stop.',
'Final status is INCOMPLETE while applicable build gates remain open; only owner grants visual acceptance.'
]
accept_env=[
'All32scene IDs have independently source-backed geography or precise feature-specific unavailable/unresolved evidence;0promoted baseline is not silently replaced by PASS.',
'Complete legal footprints/roads/banks/decks/approaches/walkable/blocked/height extents are assessed under frozen geometry with uncertainty and clear proposal status.',
'All required age-correct buildings/sites/Walls/towers/UI/environment layers are delivered or scoped-blocked with source-supported finite attempts.',
'Overlay pixels exactly agree with final annotations/legend; no withdrawn ridge traces or stretched camera evidence.',
'ENVIRONMENT interface/readySubset and own gallery/checkpoint/handoff are consumable independently of ACTORS readiness; composites are labeled ASSET_COMPOSITE.'
]
accept_act=[
'All eight class chains have actual source semantic evidence and reproducible neutral single-scale body or exact missing-link diagram plus usable subchains.',
'Every ready link has complete named matrices/pivots/frame/draworder/angle/side/size limits and inspected padded neutral/arc diagnostics.',
'Known exhausted methods and failed-byte-unavailable Paladin head remain honest; Healer boot/accepted static rows are preserved.',
'Troop/creature/attacker/mount/vehicle/equipment/artifact queue covers full scope;64px limits and Charioteer semantics remain intact.',
'ACTORS interface/readySubset and own gallery/checkpoint/handoff are consumable without environment completion; no static head/card is promoted to animated full body.'
]
accept_code=[
'All30target compositions and all ages/screens have real runtime result evidence, usable controls and true campaign states; owner can inspect the whole visual/playable build.',
'Frozen geometry/picking and current art gates remain truthful; no baked actors/HUD/roads mask incorrect legal behavior.',
'All three modes/fiveWar flows and support systems obey canonical rules and once-only campaign consequences; practice leaves campaign XP/mana/resources/rewards/casualties/story unchanged.',
'Natural ordinary journey including prepared Siege victory/settlement/reload and six functional slots is proven without fixture grants; injected age/class evidence is labeled.',
'All four landscape sizes and portrait preservation meet readability/48pxactions/focus/modal/touch/keyboard requirements; Retreat restores trigger focus.',
'Both producer interfaces are verified and consumed by Code only; unsupported rows remain scoped, while independent layouts/gameplay continue.',
'Live game URL/launch command/local comparison gallery and ordinary interaction evidence are provided; shell checks/test counts do not certify whole-game acceptance.',
'Unsigned static web/APK package has complete source/dist/www/APK closure,CRC,correctpreviewID,min24,target36,no permissions; no physical launch is claimed.'
]
dont='''Do not return a plan instead of performing your authorized execution. Do not stop at Stone, three fixes, a source inventory or a few cards. Do not use all-art-ready/owner-review/device/morale/missing-guide gates as a global halt. Do not declare whole completion while primary art/layout/gameplay remains partial. Do not adopt mock errors or full screenshots as fake gameplay. Do not extrapolate rigs/64px art, invent hidden pixels/mechanics, rerun exhausted sweeps, overwrite another producer, hand-edit historical provenance/status or erase failed evidence. Do not generate/pay/query provider/account/jobs/buckets, touch locks/budgets/reserve, expand the replacement draft, install/query devices, sign/publish/deploy, mutate Git, restore/clean/upload storage, message other AIs or spawn agents.'''
items=[('ENVIRONMENT-ART-AI-COMPLETE-PROMPT-2026-10-06.txt',environment_summary,env_owned,env_steps,accept_env,'Image composites are appearance evidence only. You may perform LOCAL production within your owned outputs; do not build/edit game source or call imagegen/providers.'),('ACTORS-EQUIPMENT-AI-COMPLETE-PROMPT-2026-10-06.txt',actor_summary,act_owned,act_steps,accept_act,'Image composites are appearance evidence only. You may perform LOCAL production within your owned outputs; do not build/edit game source or call imagegen/providers.'),('CODE-AI-COMPLETE-VISUAL-PLAYABLE-PROMPT-2026-10-06.txt',code_summary,code_owned,code_steps,accept_code,'Art-first applies to affected row promotion/placement: consume verified asset metadata before final runtime appearance acceptance. It does not block independent layouts/rules/support. Code can author CSS/native vector UI, but cannot invent painted source anatomy, regenerate producer art or silently change frozen geometry.')]
checks=[]
for name,summary,owned,steps,criteria,extra in items:
    s=header+'\n1. Task Summary\n\n'+summary+'\n\n2. Environment\n\n'+environment+'\n'+extra+'\n\n3. Inputs & Outputs\n\n'+inputs+'\n'+owned+'\n\n'+contracts+'\n4. Step-by-Step Instructions\n\n'+'\n'.join(f'{i}. {t}' for i,t in enumerate(steps,1))+'\n\n5. Edge Cases & Failure Modes\n\n'+edge_common+'\n6. Acceptance Criteria\n\n'+'\n'.join('[ ] '+t for t in criteria+accept_common)+'\n\n7. Do NOT\n\n'+dont+'\n'
    (PLAN/name).write_text(s,encoding='utf-8')
    sections=re.findall(r'^([1-7])\. (Task Summary|Environment|Inputs & Outputs|Step-by-Step Instructions|Edge Cases & Failure Modes|Acceptance Criteria|Do NOT)$',s,re.M)
    assert len(sections)==7 and [int(n) for n,_ in sections]==list(range(1,8))
    body=s.split('4. Step-by-Step Instructions\n\n')[1].split('\n\n5. Edge Cases')[0]
    nums=[int(n) for n in re.findall(r'^(\d+)\. ',body,re.M)]
    assert nums==list(range(1,len(steps)+1))
    # Hash actual Windows file bytes, including native CRLF, not the LF template.
    written=(PLAN/name).read_bytes()
    checks.append({'path':'docs/plan/'+name,'sections':len(sections),'atomicSteps':len(steps),'sha256':hashlib.sha256(written).hexdigest(),'bytes':len(written)})
(OUT/'prompt-structure-check.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
