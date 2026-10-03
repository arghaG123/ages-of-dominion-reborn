# Independent review and current status

Review date: 2 October 2026. Scope: **documentation, supplied-image interpretation, static source/configuration inspection and preservation checks**. Updated for the latest numbered requests: canonical root now exists as docs/design-only, owner section feedback precedes coding, exact30/one-active batching applies, and store/cloud/account work is deferred. See AUDIT-UPDATE.md for the current package verdict. This review did not implement or test a new game. Planning review is distinct from code, visual, owner and Android acceptance.

## Status at preparation

| Item | Status | What the status means |
|---|---|---|
| Production blueprint and visual specification | Independently audited; reconciled planning contract | A future implementation contract, not delivered features |
| Nineteen current supplied images | Reviewed as design references | Their composition and interaction ideas are captured; baked text/values are not mechanics |
| Generated art library | 854 raw files (5,076,636,300 bytes) and 961 public rasters (102,769,936 bytes) inventoried; 31 raw and 55 processed candidates visually reviewed | Individual review coverage is explicit; the entire library is not accepted |
| Fresh implementation at `C:/dev/ages-of-dominion-reborn` | Created as docs/design-only workspace | Gameplay source is absent; another AI codes only after owner preview feedback and explicit instruction |
| Unused starter draft | Archived at `C:/dev/ages-of-dominion-reborn-unused-draft-2026-10-02` | Incomplete, unverified and not adopted as a foundation |
| Old project source preservation | 226 inspected source/native/test files matched captured SHA-256 values | Zero content changes across that hash comparison; this is not a claim about every media/cache file or Git metadata |
| Fresh unit/browser/device verification | Not run | No fresh application exists to certify in this planning deliverable |
| Paid generation or APK installation by this review | None | Review and planning only |

The previous project's tests and build were run earlier in the assessment before the later planning-only instruction: 459 tests across 45 files passed; its production build passed with a 568.01 kB main chunk and the existing >500 kB warning; 20 original data tables matched its prototype. These are **old-game evidence**, not a test result for the proposed fresh game. They were not rerun as part of this documentation-only audit.

## What was inspected

The audit read the old owner requirements, relevant handoff constraints/screen/battle/adventure contracts, current data exports and extension definitions, economy/hero/army/forge/market handlers, tutorial/story/rival/offline state logic, save contracts, current settings/audio surfaces and native configuration. The nineteen images supplied in the conversation were checked against the packaged all-reference contact sheet. Static data inspection executed only read-only export summaries; it did not run gameplay or change tables.

The source folders remain evidence, not an instruction to copy their implementation. The old `core/data` parity constraint protects the old project. It does not make its executable modules the new project's architecture or permit copying them.

## Factual baseline and fresh-plan treatment

| System | Verified existing fact | Required fresh treatment |
|---|---|---|
| Ages | Seven base rows plus Future extension: Stone, Bronze, Iron, Medieval, Gunpowder, Industrial, Modern, Future | Eight complete product ages; distinguish first calibration fixtures from full progression |
| Resources | Food, wood, stone, gold | Four live totals, consistent deductions/rewards/production in all modes |
| Buildings | townhall, farm, lumber, quarry, mine, barracks, workshop, hall, armory, walls | Ten actual functional identities, dynamic upper Town Hall/citadel and walls; decorative density does not add fake sites |
| Army roles | melee, ranged, heavy; eight period names through extension | Three roles, persistent real stacks; pictured cavalry/siege categories do not create a silent fourth role |
| Towers | arrow, splash, slow, support; eight period forms through extension | Four functional families; era-specific form changes do not silently create new family unlock gates |
| Tower availability | Existing purchase/render handlers have no family-specific age gate | Any proposed new gate must be an explicit new design decision with balance consequences, not a supposed old rule |
| Hero classes | Three base classes plus five extensions, eight total | All eight class choices/stat growth and era visuals must work; do not use only the three-class table for new classes |
| Equipment | Six legacy IDs: weapon, armor, helm, boots, art1, art2 | All six visible positions must accept real compatible items and affect the hero; explain how shield/ring-looking mock positions map to functional IDs |
| Forge and artifacts | Four generated gear categories, four quality tiers, ten unique artifacts | Fully functional six-position equipment/inventory, with acquisition rules for artifacts as well as gear; a historical four-category forge is not a reason to leave two slots inert |
| Forge quality | Crude, Fine, Master, Relic; old multipliers 1, 1.8, 2.8, 4 | Preview actual craft quality/cost/result and use age-correct art in Forge as well as Hero |
| Mock forge extras | Enhance +10, reforge, sockets and set bonuses are not old implemented rules | Record their disposition as deliberate later systems; no decorative unusable buttons |
| Hero primaries | Attack, Defense, Power, Knowledge; mana capacity Knowledge×10 | Real displayed stats, spell scaling and equipment effects; mock combat-power/capacity numbers cannot be invented |
| Skills and spells | Nine skills, three skill levels; eight spells; old skill offer provides two choices | Declare fresh unlock/progression defaults in the data ledger; all skills/spells must eventually be observable and functional |
| Ranks | Five stack/tower ranks; hero level/XP is separate | Do not invent a hero rank merely because an old screen spec said so |
| Terrain/weather | Eight terrain identities; seven weather states | Coherent ground plane and readable modifiers; no floating land enemies or blinding weather band |
| Market | Old Bronze unlock; buy/sell batches of 100, buy 120 gold/sell 60 gold | Adopt or deliberately revise the ledger values; correct live exchange and no eleventh fake plot |
| Offline progress | Existing cap hours: 8, 7, 6, 5, 4, 3.5, 3; Future clamps to 3 | An explicit eight-age fresh cap table and chronological build completion; never award a week of production uncapped |
| Story | Seven existing chapter subjects, six quest templates, six possible persistent rival names | Complete eight-age narrative/progression; state the Future conclusion explicitly rather than implying eight old chapters exist |
| Tutorial/rival | Current callers exist; old “no caller” text is stale | Fresh anchored onboarding, persistence, rival memory and meaningful story payoffs remain required |
| Settings | Current haptics, help, credits, privacy and local-save controls exist; audio currently has a master gain | Fresh Music/SFX controls need separate real buses; haptics availability must be honest under zero-permission policy |
| War options | Current campaign defence, tactical duel, Endless, no-consequence Skirmish and local shared-seed challenge features exist | Explicit scope/status for each; first proof may be narrower, full features cannot vanish without a stated disposition |
| Current navigation/save | Existing schema v8 with deterministic 16×10 landscape navigation | Fresh schema and namespace; no automatic adoption of old saves or executable core |
| Existing articulated rigs | Two current registry IDs, not zero | Fresh mount/worker/battle/defence animation needs its own clip proof and coverage; paintings are not rigs |

There are 20 original table exports: AGES 7, RANKS 5, RANKXP 5, RES 4, ROLES 3, CREATURES 8, TOWERS 4, BUILDINGS 10, TERRAIN 8, WEATHER 7, PRIMARIES 4, CLASSES 3, SKILLS 9, SPELLS 8, SLOTS 6, GEAR 4, QUAL 4, ARTIFACTS 10, STORY 7 and QUEST_TEMPLATES 6. These counts describe the old baseline; Future/classes extensions explain why product counts differ. [GAME-DATA-REFERENCE.json](GAME-DATA-REFERENCE.json) freezes all 20 tables, seven extension exports, starting counts/resources and cap references with 17 source hashes. Executable function bodies are not copied; computed spell fields have reference-only markers and retain their formula descriptions as data. The future builder must implement fresh rules against this specification and log deliberate changes. Do not use values from the abandoned starter as approved balance.

## Historical contradictions resolved or requiring reconciliation

Latest owner instruction chooses full fresh source and another AI's implementation. The earlier recovery recommendation to retain executable core is superseded. Earlier “photorealistic only,” painted Heroes III, old reference-folder priority and 375×812 targets are superseded by the latest semi-realistic/realistic supplied direction and 424×933 primary viewport, with 360×800 and 820×1180 coverage.

The required tactical baseline is **7 columns ×10 rows**, separate from the hidden Adventure 16×10 grid and Defence 9×15 lane space. An intermediate draft introduced 11×8 inadvertently; the final Master Plan, visual contract, traceability and kickoff now consistently use 7×10. Auto and confirmed Retreat are intentional features; old prose forbidding them is stale. A visible unit/hero position must be defined from the new scene projection, rather than copied as a code-coordinate assumption.

The current reference set contains thirteen portrait target screens and six additional landscape/sample montages. First-/third-person, PvP, gacha, exotic settings and deeper enhancement panels inform expansion ideas; they do not require fake controls or silently create first-slice scope. Adventure is an inhabited continuous landscape, and Tactical and Defence are separate playable modes with different clocks.

## Acceptance plan for the implementing AI

| ID | Given / when | Required observable result |
|---|---|---|
| QA-01 Fresh boundary | Given the docs/design-only root, when later authoring game source | No copied/imported old gameplay/client/core, source symlinks, old bundle, old saves, caches or secrets; reviewed art/config has a transfer ledger |
| QA-02 Kingdom visual gate | Given Stone starter and developed Medieval fixtures at each target viewport, when opening Kingdom | Reference camera/river/citadel/wall/city proportions and edge HUD match; all17 reference-mapped plus pads, separate upper hall/perimeter, correct scale/light/occlusion; owner review remains separately recorded |
| QA-03 Construction | Given an affordable empty site, when confirming twice rapidly and reloading during construction | Cost deducted once; one persisted build/scaffold; visible completion changes the correct building and production; unaffordable state explains its reason |
| QA-04 Joined campaign | Given a naturally recruited army, when travelling, fighting, looting/equipping, returning, defending and reloading | Identical entity IDs and consistent resources/XP/items/counts in every scene; casualties and rewards settle exactly once |
| QA-05 Movement | Given blocked water, a bridge, limited movement and a reachable guarded site, when panning/pinching/previewing/committing | Gestures spend zero; preview uses authoritative legal path; bridge alignment and exact cost are correct; interrupted travel never rerolls or double charges |
| QA-06 Tactical legality | Given deployed stacks on a 7×10 board, when moving, attacking, shooting, waiting, defending and casting | Correct initiative and legality, visible previews, mana/effects, enemy response and readable grounded formations; illegal action cannot change state |
| QA-07 Tactical outcomes | Given an active encounter, when using manual play, Auto, retreat cancel/confirm or reloading at settlement | Deterministic rules, real survivors/losses, correct return destination and once-only rewards; Auto is not a guaranteed win |
| QA-08 Defence | Given four tower functions plus campaign army/hero, when placing/upgrading and running/pause/resume/2× waves | Fixed 1/60 logic, meaningful range/effect, no duplicated deployment, no attacks from offscreen spawn, melee interception, persistent casualties and actual wave settlement |
| QA-09 Role threats | Given archers, sappers, support, airborne or boss content included by the full plan, when engaging it | Visible threat and role-specific movement/counterplay; no unbeatable hidden shooter or army that cannot respond |
| QA-10 All equipment | Given compatible items for all six slots, when swapping/unequipping/crafting/looting/reloading | Each slot functional, before/after numeric comparison, compatible art and real combat/stat effects; unavailable actions absent or explained |
| QA-11 Progression | Given all eight ages/classes and required skill/spell/story/objective data, when progressing through them | Correct visuals and unlocks, Future closure, repeat claims rejected and usable recovery after defeat; no class or era uses an unrelated silent fallback |
| QA-12 Save failures | Given damaged live/backup/import, unsupported schema, truncated writes, quota errors and out-of-order autosaves | Useful recovery; damaged is distinct from absent; no silent New Game, stale write or valid-save overwrite; validation includes IDs, phases and ranges |
| QA-13 Clock/lifecycle | Given construction/travel/tactical/defence in progress, when suspending or changing clock backward/forward | Chronological capped production, preserved commitments, paused continuous combat and no duplicate settlement; resume explains actual cap/income |
| QA-14 UI and motion | Given each surface in empty/default/pressed/disabled/busy/error states, when resizing and using keyboard/touch/reduced motion | No clipping/overflow/stale hit geometry; ≥48×48px targets and focus handling; narrow-phone board uses bounded pan/zoom or an accessible target list when cells cannot fit; articulated attachments/gait; simulation timing independent from animation |
| QA-15 Native | Given an isolated preview application ID, when building/syncing/compiling and later installing for review | Correct SDK/permissions/local assets; old app remains installed separately; real insets/gestures/lifecycle/offline/performance evidence reported separately |

Require complete command output/exit codes from the future new project, meaningful state assertions and inspected screenshots identifying actual surface, viewport, fixture, action and outcome. A screenshot filename, old unit test, mock canvas “not.toThrow,” file dimension, checksum/provenance or color statistic cannot stand in for visual matching. Some old Hero/Realm filenames contain Title/Battle pixels; reuse no such evidence without inspecting it.

The visual minimum is 424×933, 360×800 and 820×1180, plus supported combat landscape/resizing. Device acceptance requires the actual target Android hardware. The first Medieval fixture is visual calibration, not proof of natural eight-age campaign play. Final completion needs all planned required systems, modes, content and failure states, rather than declaring the first slice the whole game.

## Review limits and outstanding completion conditions

The raw inventory describes file presence and size. Selective contact sheets and the candidate manifest do not prove all 854 raw files suitable. Evaluate full-resolution sources of any selected file, processing quality, provenance, permitted shipping use and assembled projection before adoption. Iron/Future final composition and broad articulated motion remain future production work. Necessary Vertex batch generation remains within the owner's existing authorization and agreed scope; ask only for genuinely unresolved budget, credentials or materially expanded scope. Historical 763/787 asset counts do not themselves justify an unlimited replacement purchase.

Optional haptics must obey the zero-permission rule. An Android manifest removing VIBRATE does not prove native vibration works. Platform-supported permission-free feedback can be enabled after verification; otherwise show haptics unavailable rather than presenting an inert preference. Inspect the merged and packaged manifest, not just whether a runtime permission dialog appears.

`modern-web-guidance` was not found in available repository/user skill locations during this review. The package's explicit responsive, canvas lifecycle, reduced-motion, safe-area, touch and verification contracts provide implementation guidance; do not claim that missing guide was applied or block the plan merely on its name.

The independent specification audit verified exact values for all 20 original tables and seven product-extension exports, reference-only function markers, all 17 source hashes, and all 19 supplied source/reference-copy hashes. A final preservation comparison again found zero content changes across the 226 captured old source/native/test files. The canonical root exists as a docs/design-only repository; no fresh game implementation is present. **Earlier planning contract passed; current update verdict is recorded in AUDIT-UPDATE.md.** The final Master Plan/traceability explicitly preserve campaign Siege, Tactical Duel, Endless, isolated Skirmish and local shared-seed Challenge. Native transfer explicitly requires zero ANY declared/granted device permissions in merged and packaged manifests; optional haptics cannot introduce VIBRATE. Geometry, all-six-slot semantics, Future narrative, shared-state flow, source boundaries and cross-references are reconciled. This is document acceptance only. Fresh gameplay, final art, articulated motion, owner likeness and physical-device behavior remain **unverified until the other AI implements and supplies their respective evidence**.




