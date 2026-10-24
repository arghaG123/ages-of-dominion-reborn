> **Authoritative execution contract - owner clarification, 16 October 2026:** The owner uses the plan as the complete source of truth for the other implementation AI. Read the [binding manual sections 0 and 10](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) and give that AI [ONE authoritative complete executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). All 18 owner-concern groups have mandatory outcomes, repair routes and evidence obligations; all original requirements, 30 mocks, 18 journeys, 16 G contracts and 96 steps remain required. Resolve/implement/verify/repair until every required current assertion passes; a checkpoint, blocked row or test count is not completion. The earlier semantic audit describes corrected prior wording. Planner remains documentation/verifier only; no production/provider/build/device/Git/cleanup/dispatch. Budget and later review sequence remain unchanged. **The specification is authoritative; implementation acceptance remains INCOMPLETE.**

> **Independent semantic PLAN audit ? 16 October 2026:** The major scope was present, but 11 documentation issues (4 P1 / 7 P2) needed correction: mechanics assertion gaps, skill points versus offers, save commit/acknowledgement and replacement races, layout/dense picking, Endless termination, inventory-capacity assumptions, healing targets and inherited references/source authority. Read the [plan audit](INDEPENDENT-PLAN-SEMANTIC-AUDIT-2026-10-16.md), [corrected manual section 9](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md#9-binding-corrections-from-the-independent-semantic-plan-audit) and give the other AI [ONE corrected complete executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). The manual is embedded verbatim; G01?G16 and original 96 steps are preserved. This is documentation correction, not game acceptance or a new test run. Planner/verifier only; no production/provider/build/device/Git/cleanup/dispatch. **Whole game INCOMPLETE.**

> **Latest owner clarification — detailed mock-led execution, 16 October 2026:** The ADVANCED MOCKS are the target finished design/look; the original game is reference context, not the acceptance ceiling. Read the [step-by-step solutions manual](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) and give the other AI [ONE complete updated executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). It includes 30 individual mock recipes, 10 concrete repair procedures, 18 journey assertion lists, file/function ownership, layout/transform examples, storage repair, budget controls and final evidence checks, plus all G01–G16 and the complete original 96-step sequence. This AI remains planner/verifier only. These are implementation instructions, not completed fixes; product stays INCOMPLETE.

> **16 October 2026 — independent verification: INCOMPLETE.** [Audit](INDEPENDENT-WHOLE-GAME-VERIFICATION-2026-10-16.md), [coverage](INDEPENDENT-WHOLE-GAME-COVERAGE-2026-10-16.md), [ONE complete executor continuation](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). **Owner priority: game appearance first.** [Original-game comparison and required plot/wall/world redesign](OWNER-GAME-LOOK-PRIORITY-AND-ORIGINAL-COMPARISON-2026-10-16.md); this AI verifies/plans, the other AI implements. Fresh 152 Node tests, 10 offline safeguards and 483-entry web/APK parity pass bounded. Scene scoring, natural-journey claims, kits/gear/roles/mounts/Healer, mock fidelity and long-save quota closure remain incomplete; current and delivered APK native bytes differ. [Owner art/budget authority](OWNER-ART-STYLE-HEALER-AND-BUDGET-2026-10-16.md): one coherent realistic/semi-realistic treatment; reuse a suitable complete Healer or generate a replacement; up to $20 beyond prior $80 solely for these fixes, absolute project exposure ceiling $100; released $15 reserve counted once, liabilities require fresh reconciliation. Planner changed QA/docs only; no production/provider/build/device/Git/cleanup/dispatch. Earlier contradictory completion/budget banners are historical.

Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; Node 24.19.0; Python 3.13.7; Android Java 21/WebView, compileSdk/targetSdk 36, minSdk 24, Gradle 8.11.1, Android Gradle Plugin 8.7.3, AndroidX WebKit 1.12.1.
Task classification: Architecture/Planning handoff for another AI to execute Feature Build, Debugging, Refactor where necessary, and Testing. Prepared 12 October 2026, Asia/Calcutta.

# Ages of Dominion — complete game design and interaction executor plan

## 1. Task Summary

You are the owner-selected implementation AI. Finish Ages of Dominion Reborn as a coherent, playable, landscape game that matches the approved mock compositions and the complete adopted gameplay scope. Preserve the functioning campaign core and verified repairs, replace the current disconnected screen/button presentation with contextual world interaction and connected player journeys, finish the source-bound terrain/art/rig/equipment work, complete every main and supporting screen, and deliver a verified offline preview package. Work through all requirements in this document; do not stop after navigation, a visual theme, one polished screen, a successful image batch, or passing unit tests. The owner explicitly says the current implementation creates a separate button for each section instead of real game interaction. Therefore, a feature is complete only when its actual entry, selection, preview, legal command, visible outcome, cancellation/failure behavior, save/reload and return journey work together. Complete the whole game/art/build first; independent desktop review follows; physical-device testing and owner review remain later. This document prepares that work and does not claim it has been executed.

**Current product verdict: INCOMPLETE.** This plan supersedes the obsolete completeness assumptions in `ONE-REMAINING-WORK-COMPLETE-PROMPT-2026-10-12.txt`. It does not erase historical evidence or replace the canonical game mechanics with generated mock text.

The baseline is the independent recheck of commit `6e1d9ecc121e6d3cf4d73db206407679b797e45c`, not the executor's “all F1–F8 resolved” banner. At plan preparation, HEAD still equals that commit; the audit/status documents contain uncommitted planner work that must be preserved.

Verified at that snapshot: 127/127 automated tests; 52 asserted screen/viewport visits; 32 age/mode and eight class fixtures; bounded ordinary battle/Retreat/Defense pause/reload checks; and 475-file source/dist/www/APK parity with CRC PASS. These results do not prove finished visuals, articulated actors, every human journey, balance, native runtime or owner acceptance.

The following are **already repaired at the stated verification level** and must not be needlessly rebuilt: Android confirmation and file-picker handlers exist in source; Home Load slot pointer obstruction is fixed at 1280×720; the Tactical/Defense treasury is hidden; all 80 active building entries pass the earlier magenta candidate scan. Keep their regressions covered. Native behavior and broader alpha/grounding acceptance remain separate.

## 2. Environment

### Workspace and execution boundaries

- Active repository: `C:/dev/ages-of-dominion-reborn`. Use its current branch; inspect changes before editing. Do not reset, clean or overwrite concurrent work.
- Old `C:/dev/ages-of-dominion` and raw `C:/dev/aod-art-src` are read-only reference sources. Independently authored new runtime code remains required; do not copy/import old executable gameplay/client modules.
- This is custom ES-module tooling. `package.json` declares Node >=24 and includes Vite as a dependency, but the actual authorized development/build entrypoints are the custom scripts below. Do not migrate the project to another engine/framework as a shortcut.
- Bundled verified Node: `C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`. PATH previously exposed Node 22.19.0; check before invoking npm/node. The configured Android versions above were reread during planning; refresh installed Java/SDK tool availability before building.
- Python 3.13.7 and local Pillow/NumPy/image tools were used for audit. Use explicit UTF-8 for document/JSON reads and writes on Windows.
- Browser evidence used Chrome and bundled Playwright. Use isolated browser profiles and disposable saves; never overwrite the owner's real save to prepare screenshots.
- Runtime is offline and local. Keep zero declared/granted Android permissions, including no INTERNET or VIBRATE. Development-tool networking is distinct from runtime permission policy.
- Preview application ID is `com.agesofdominion.game.reborn.preview`. Preserve the permanent identity metadata already recorded in the project; do not rename or replace the old installed game.
- No account/server features, Play Store work, signing-key changes, publication, new backups, cleanup or Git publication are added by this plan. Do not dispatch another AI from the planner chat. One selected executor owns the complete implementation handoff.
- No physical-device connection, installation or testing during this implementation pass. At desktop/build completion, provide the evidence and later device checklist; do not treat this document as an instruction to start device work early.

### Existing tools and code ownership

| Purpose | Existing entrypoints / files | Instruction |
| --- | --- | --- |
| Local server | `scripts/serve.mjs --port 4517` | Check whether the port is already serving this repository before starting another process. |
| Regression suite | `node --test tests/*.test.mjs` | Use Node 24; redirect `EARNED_SCOPE_OUT` to the new evidence folder. Current count 127 is a baseline, not a permanent ceiling. |
| Web build | `npm run build` / `scripts/build.mjs` | Refresh dependency closure from actual consumers. |
| APK build | `npm run build:apk` / `scripts/build-apk.mjs` | Build after source/art integration; preserve required predecessor packages. |
| Package verification | `scripts/verify-package-20261011.py` | Update discovered closure only for real consumer changes; check exact new package bytes. |
| Campaign/economy | `src/core/campaign.js`, `mechanics.js`, `rules.js` | Reuse validated command/transaction logic; presentation must not invent a second economy. |
| Adventure | `src/core/navigation.js`, campaign commands | Reuse actual legal paths, movement costs, site state and encounter identities. |
| Combat | `src/core/battle.js`, `defense.js`, `challenge.js` | Preserve legal actions, deterministic RNG, fixed-step simulation and isolation rules. |
| Persistence | `src/core/save.js` | Preserve validation, staged writes, backup/slots and existing saves. |
| Client orchestration | `src/client/main.js`, `choices.js`, `tactical-ui.js` | Refactor only where needed to replace flat button/page behavior with contextual interaction. |
| Layout / picking | `presentation.js`, `projection.js`, `visible-size.js`, `game.css` | Use one scene transform and its inverse; keep UI typography in screen space. |
| Actors / time / audio | `actor.js`, `rig.js`, `anatomy.js`, `motion.js`, `hero-room.js`, `audio.js` | Wire actual runtime consumers; retain separation of rendering and campaign mutation. |
| Android shell | `android/app/src/main/java/com/agesofdominion/game/MainActivity.java` | Preserve recent handlers; complete any remaining local document/lifecycle integration. |

### Art generation authority and limits

Existing owner authority permits necessary useful image work by the implementation executor under `OWNER-PAID-BATCH-PROGRESSIVE-AUTHORITY-2026-10-11.md`. This plan makes no provider calls and grants no larger budget. Before a paid request, reconcile current liabilities, active/UNKNOWN operations, locks, reservations and attempt histories. The historical $15.1673 figure is **not freshly verified remaining capacity**.

- Hard cap US$80; reserve released exactly once, effective reserve zero. Retain unresolved liability holds and invoice UNKNOWN state.
- Use the recorded authorized Vertex project/account/model and request-scoped configuration. Do not switch accounts/providers or change global billing/IAM/configuration to bypass a blocker.
- One active or in-flight UNKNOWN generation operation in the authorized project across batch and progressive routes; durable owned mutex/CAS/write-ahead reservation required.
- Default batch route is 1K and exactly 30 genuinely independent useful ready requests. No filler, calibration purchases or duplicate repurchases to reach 30.
- Necessary detailed actors/rig sources use progressive native 2K; proven scene patches requiring 4K use progressive native 4K after physical tracing and native review. Small ready needs may use progressive appropriate-resolution requests rather than padding a batch.
- Progressive success spacing is at least 20 seconds after the previous successful response completes, persisted across restarts. A definite 429 stops the stream until at least 60 seconds or a longer Retry-After. Ambiguous POST outcomes retain UNKNOWN/full holds with no blind resend.
- Inspect existing correct natives before purchase. Prefer a missing-source repair over blanket regeneration of all scenes/characters. Transmit real aligned reference/base/mask bytes, not textual claims that guides were provided.
- Refresh exact provider capability/pricing at dispatch; do not reuse historic prices as current quotes. Continue independent local implementation if paid work is genuinely blocked.

## 3. Inputs & Outputs

### Authoritative inputs and precedence

Read the current root `AGENTS.md`, `START-HERE.md`, `CURRENT-STATUS.md`, `DECISIONS.md`, `docs/SESSION-HANDOFF.md`, `docs/BUILD-PROGRESS.md` and the documents indexed by `docs/plan/README.md` as required by the repository. Resolve historical banners by dated owner authority, not by whichever PASS appears last in a search.

Use these inputs directly:

1. The owner's current requirement in this plan: match the approved game design and implement real connected game interactions instead of separate section buttons.
2. [Current independent recheck](INDEPENDENT-WHOLE-GAME-RECHECK-6e1d9ec-2026-10-12.md) and [earlier detailed audit](INDEPENDENT-WHOLE-GAME-AUDIT-2026-10-12.md), including scope/verification limitations.
3. [Canonical implementation specification](FULL-IMPLEMENTATION-SPEC.md), [master plan](MASTER-PLAN.md), [requirements traceability](REQUIREMENTS-TRACEABILITY.md), installed-environment and source-equation/adoption records.
4. `src/data/implementation-contract.json`, `reference-data.json` and current source-backed numeric tables. Existing compatibility and save invariants take precedence over invented mock statistics.
5. All 30 references in `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/`, plus the retained supplied references and their discoverable indexes.
6. Current art/scene bindings: `reviewed-source-selection.json`, `stone-scene.json`, `mode-scenes.json`, `age-buildings.json`, `actor-atlas.json`, `anatomy-binding-v1.json`, `hero-bodies-20261011.json`, `plate-catalog.json`, `plate-overrides-20261007.json`, `gear-icons-20261007.json`, `consumer-catalog-20261007.json` under `src/data/`.
7. [Review sequence and morale decision](OWNER-REVIEW-SEQUENCE-AND-MORALE-DECISION-2026-10-11.md) and [paid routing authority](OWNER-PAID-BATCH-PROGRESSIVE-AUTHORITY-2026-10-11.md).

Historical portrait dimensions and interim section-owner-approval gates do not override the later whole-game landscape/full-build-first decision. Do not ask for repeated approval of already decided morale or individual affordable authorized image repairs. If a genuinely unresolved design decision cannot be determined from these inputs, record its exact scope and continue independent work.

### Required player experience and navigation contract

The world is the primary interaction surface. A screen button is navigation, not a feature implementation. Retain accessible contextual alternatives for small or dense targets; a decorative screenshot with transparent hotspots is not a dynamic world.

| Context | Required entry and interaction | Required return / consequence |
| --- | --- | --- |
| Home | Continue, New, Load, Settings; real eight-class selection for a new campaign | Continue restores the actual saved scene/session; do not always force Kingdom. New confirms replacement when needed. |
| Roaming shell | Compact labeled/icon navigation for Kingdom, Adventure, Hero, Army and War, with a secondary menu | No permanent 13-section row. Preserve selected world/camera where safe; secondary sheets return to their source. |
| Kingdom | Tap actual empty plots, constructed buildings, Town Hall, Walls and the exit gate | Construction/upgrade/recruit/forge actions affect the same campaign; closing a sheet returns to the same location. |
| Hero | Select worn slots, carried items, skills or spells inside the Hero experience | Slot opens the relevant comparison/Forge category; skill points and equipment deltas persist. |
| Forge / inventory | Enter through the Armory, a Hero slot or carried item | Return to the invoking Hero/Kingdom context; crafting does not force unrelated navigation. |
| Market | Open a Kingdom sheet with real Bronze unlock and exchange state | Cancel has no transaction; confirmed exchange changes the campaign exactly once. No new Market building. |
| Journal | Open Story/Quests from compact objective/menu access | Objective actions link to the real relevant destination when legal; journal closes back to its origin. |
| Adventure | Tap actual destination/site/guard/pickup; preview route and cost | Commit legal travel, encounter, reward or return-to-town; preserve fog, offers and origin on reload. |
| Tactical | Enter from a guard, Duel, Skirmish or Challenge setup | Contextual battle HUD replaces roaming navigation; legal result/retreat returns to the correct origin. |
| Defense | Enter preparation from War or the Kingdom defense context | Select pads/entities directly; pause/menu preserves the session; results return to campaign context once. |
| Menu / recovery | Settings, Help, save slots, import/export and recovery | Modal/sheet focus and Back/Close return correctly without losing active session or silent reset. |

Implementation decision: use a single visible primary context panel at a time, with a clear Back/Close action and a compact menu for secondary functions. Do not require hover or drag-only gestures. Inventory may support drag as an enhancement, but tap-select/tap-confirm and keyboard alternatives must work. Keep battle legality and persistence in the existing core; hiding navigation must not create a hidden way to abandon or duplicate a battle.

**Scene UI state is transient.** A selected target, preview, highlighted route, open sheet, hover, camera gesture or animation event must not independently spend resources, advance a turn, pay rewards or mutate saved campaign progress.

### Full feature contracts to preserve and finish

| ID | Complete scope | Observable player outcome |
| --- | --- | --- |
| G01 | Eight ages: Stone, Bronze, Iron, Medieval, Gunpowder, Industrial, Modern, Future | Age changes terrain treatment, settlement, workers/transport, buildings, troops, towers and class kit coherently; retained items keep their own identity/age. |
| G02 | Sparse Day 1 and economy | Town Hall 1 plus 17 empty pads, separate Walls 0; four resources; initial supplies 250 food/250 wood/160 stone/150 gold; hero with empty gear; stored 12 melee/8 ranged and owned arrow/slow towers. No prebuilt facilities masquerading as progression. |
| G03 | Construction and progression | Four repeatable producers; unique Barracks/Workshop/Great Hall/Armory; separate Town Hall/Walls; actual costs, scaffold/timer/completion, facility capacities, age gates and capped offline income. Cancel spends zero. |
| G04 | Adventure | Hidden 16×10 navigation, terrain-grounded land/bridge routes, documented clearings/sites/pickups/guards, fog, fixed offers, movement/weather/rest/day transitions and committed travel without double spend. |
| G05 | Tactical | Hidden 7×10 topology, commander and six stack slots, legal deployment, true initiative, reachability/target previews, Move/Melee/Shoot/Defend/Wait/Spell/Auto/confirmed Retreat, flyers, effects and saved outcomes. |
| G06 | Defense | Hidden 9×15 lane/pads, fixed 1/60 simulation, four tower families, five attacker roles, persistent hero/army ownership, zero deployment fee, visible range/telegraphs/abilities, pause/2×/waves/gate HP/results. |
| G07 | Five War options | Campaign Siege, Tactical Duel, Endless, isolated no-consequence Skirmish and offline shared-seed Challenge; real setup, consequence explanation, execution and result for each. |
| G08 | Hero/classes | Knight, Ranger, Warlock, Mage, Paladin, Barbarian, Necromancer, Healer; correct identity/stats, level/XP, A/D/P/K, Knowledge×10 mana, morale/luck, four kit eras and actual battle influence. |
| G09 | Skills/spells | Nine exact skills with three levels/effects/prerequisites; eight exact spells with eligibility, mana and legal targets; earned Wisdom 3 and wounded-stack Resurrection included. |
| G10 | Equipment/Forge/bag | Six slots, four qualities Crude/Fine/Master/Relic, ten source-backed artifacts, unique IDs/compatibility, real craft/loot/equip/unequip/compare/stat deltas and worn appearance. Armory gates and actual quality/recipe costs apply. |
| G11 | Army/creatures | Three role families across eight ages, quantities/ranks/capacity/reinforcement and all eight creatures: wolf, bandit, bear, harpy, golem, griffin, wyvern, drone. Existing flyer traits persist. No invented split/merge rules. |
| G12 | Story/quests | Seven existing chapter subjects, persistent source-backed rival/branches, six quests, eight milestones and Future conclusion “The Valley We Keep”; once-only outcomes and saved consequences. |
| G13 | Market | Bronze unlock, four-resource rules, documented 100-unit transactions and exact buy/sell prices; unavailable reasons and transaction feedback. |
| G14 | Tutorial | Affordable sparse-start Build/Recruit/Travel/Tactical/Defense sequence anchored to actual objects/controls; wrong clicks do not advance; skip/review and step persistence. |
| G15 | Save/recovery/settings | Real save slots, import/export, corrupt/unsupported/quota handling, backup/recovery, lifecycle suspension; independent local music/SFX, reduced motion, Help/Credits/Privacy. |
| G16 | Shared consequences | Same hero/army/items/resources across campaign modes; persisted settlement IDs; no duplicate rewards, free revived losses, invisible second treasury or practice leakage. |

Retain the adopted formulas and validations. Positive morale is already decided: 4.2% per positive point, maximum 12.6%, one immediate bonus action per stack per round, no chains. Do not reopen it as a design choice. Preserve the earned-path repairs verified by the current suite: six slots, all quests/creatures/spells, Hero Hall/Defense XP, hero blast transitions and bounded Endless progression.

### Thirty-reference design contract

All names below are exact files within the reference directory. Build dynamic equivalents, not image-backed menus. A reference's typography, composition and visual hierarchy are goals; its fabricated text is not a mechanic. Extra unmocked Market/War/Help/recovery states must use the same design language and real rules.

| Reference | Required composition and behavior |
| --- | --- |
| 01-home.jpg | Correct Ages of Dominion title, panoramic world, compact book/menu treatment, visible save state and real Continue/New/Load/Settings. |
| 02-kingdom-day1.jpg | Sparse starting settlement, distinct upper civic site, all 17 empty selectable plots, separate perimeter and grounded first construction. Correct the mock's medieval Stone elements. |
| 03-kingdom-stone.jpg | Mature Stone settlement with primitive structures/materials, appropriate workers and terrain; no stone cathedral/medieval armor. |
| 04-kingdom-bronze.jpg | Bronze settlement transformation with coherent roads/fields/buildings and period troops/transport. |
| 05-kingdom-iron.jpg | Iron treatment across the whole settlement, not only Town Hall. |
| 06-kingdom-medieval.jpg | Medieval civic hierarchy, inhabited plots, perimeter, bridge and grounded settlement depth. |
| 07-kingdom-gunpowder.jpg | Gunpowder architecture/people/transport and coherent road/field treatment. |
| 08-kingdom-industrial.jpg | Industrial city treatment and matching production/transport/tower/army forms. |
| 09-kingdom-modern.jpg | Modern settlement and matching military/civic props without leftover early-age structures. |
| 10-kingdom-future.jpg | Future homeland with coherent advanced forms; correct mock rural carryovers and do not invent a Research Lab. |
| 11-adventure-overview.jpg | Inhabited sites, readable landmarks, fog and hero position integrated into continuous terrain. |
| 12-adventure-crossing.jpg | Actual committed route follows the painted crossing and banks; grounded mounted travel with legal picking. |
| 13-adventure-foot.jpg | On-foot movement, site approach, selection and encounter interaction at appropriate scale. |
| 14-tactical-deployment.jpg | Grounded formations and commander, legal deployment preview, visible roster and clear start/cancel state. |
| 15-tactical-action.jpg | Readable active stack/initiative, ground targets, meaningful attacks/spells and clear action feedback. |
| 16-battle-result.jpg | Composed victory/defeat/retreat result with actual survivors/casualties/XP/resources/loot and once-only return. |
| 17-defense-preparation.jpg | Scene-bound pads, tower selection/range preview, available owned roster and gate/wave preparation. |
| 18-defense-wave.jpg | Readable threats, grounded motion/attacks, telegraphs/projectiles, concise wave/gate/pause controls and no battle treasury. |
| 19-hero-equipment.jpg | Dominant full figure in a believable chamber; Helmet/Weapon/Shield left and Chest/Greaves/Ring right; real selected item and period-correct appearance. Ignore invented gear names. |
| 20-skills.jpg | Designed skill tree/panel with nine distinct square sigils, current rank, next effect, prerequisites and real point spending. |
| 21-spells.jpg | Designed spellbook/panel with eight distinct round glyphs, eligibility/mana/target information and actual legal selection. |
| 22-forge.jpg | Believable workshop and prominent correct selected item, six categories, quality/cost/material preview and visible crafting result. |
| 23-inventory.jpg | Readable carried/equipped grid with rarity, identity, compatible slots, comparison and confirmation; real empty/full states. |
| 24-army.jpg | Cohesive roster/codex with actual troop/creature art, counts/rank/stats/capacity and contextual recruitment. |
| 25-story.jpg | Journal-like chapters/rival/branch presentation with saved choices and meaningful context. |
| 26-quests.jpg | Objective presentation with actual progress/reward/claim state; exclude mock device frame from the runtime. |
| 27-tutorial.jpg | Short anchored instruction pointing to the actual target without hiding the scene; exclude mock device frame. |
| 28-settings.jpg | Clear local music/SFX/reduced-motion controls, Help/Credits/Privacy and correct return/focus. |
| 29-save-recovery.jpg | Usable slots/import/export/backup/recovery with explicit damaged versus absent state and safe replacement. |
| 30-icon-material-board.jpg | Consistent materials, semantic icon vocabulary and distinguishable shapes; resolve duplicated motifs instead of copying ambiguity. This is a design-system reference, not another menu page. |

### Geometry, art and motion output contract

All 32 age×scene families (Kingdom, Adventure, Tactical, Defense) require a real runtime source binding, measured source hash/dimensions, source-specific physical tracing, transformed geometry, registered dynamic-object anchors and native/phone composite review. Do not certify the wrong terrain file. Shared legal topology does not mean every painting has the same physical feature coordinates.

Use `[a,b,c,d,e,f]` for `x'=a*x+c*y+e`, `y'=b*x+d*y+f`. One world-to-source transform and one source-to-viewport transform must align terrain, actors, buildings, routes, selectors, labels and inverse picking. Preserve frozen legal geometry and documented Hall scale; do not move legal cells or shrink objects merely to make a failing trace pass. Correct the registered artwork/consumer or document the exact unresolved requirement.

The current Kingdom affine is `[60,-10,25,35,170,165]`, with source stage 1376×768 and the recorded Stone Hall scale 0.1312. Re-read the corresponding live contract before editing; other mode matrices come from their own contract entries. Keep consumer-specific display limits, including ordinary plates 130 CSS px, gear/mount/effect plates 64 CSS px, and the existing Hero-room-only standing-body exception up to 600 CSS px. Measure the actual visible bound after camera scaling. A large Forge composition is not permission to stretch a small icon or apply the Hero exception elsewhere: use a separately justified, source-supported presentation contract if needed and retain the original bounded consumer. Do not weaken a protected limit merely to pass a screenshot comparison.

Every displayed object needs truthful source lineage, alpha/edge review, footprint/pivot, depth/height, facing, era/role and intended-size evidence. Multi-source assemblies require each source and each actual transform; a single crop affine cannot describe five independently placed body parts. Preserve raw originals and rejected attempts.

Eight classes across ancient/medieval/powder/mech eras require complete visible combinations, not necessarily 32 newly purchased images. Reuse correct component layers/rigs where they genuinely meet the target. Ground locomotion requires articulated limbs; horses require visible hoof phases and a connected rider/saddle; engines require appropriate wheel/track/limb movement. Static portraits may remain in portrait contexts, never as proof of world animation.

Required clips are idle, walk/travel, work where relevant, attack, cast where applicable, hit and death, with proper direction changes and reduced-motion behavior. Review contact and attachment at extreme poses. Animation is driven by committed action/events and a presentation clock; frame callbacks cannot decide combat or issue rewards.

### UI and accessibility output contract

- Landscape evidence sizes: 825×375, 933×424, 1180×820 and 1280×720. Portrait shows an accessible rotate message without changing saved state.
- Keep canonical 16/20/25/31 typography in **screen-space CSS pixels** for instructional/body/hierarchy text. Where a compact secondary label must be smaller, document its purpose and enforce at least 14px; no essential rule, cost, objective or instruction in 5–10px scaled SVG text.
- Use 48×48 CSS px interactive hit targets with actual pointer ownership and visible focus. A larger invisible box behind another panel does not pass. Compact noninteractive resource symbols may retain their documented 18px/28px rail exception.
- Preserve the slate/stone/brass visual language and natural world colors. Local fonts/media only. Maintain measured contrast of at least 4.5:1 normal text and 3:1 large text; text size is not a substitute for contrast.
- In ordinary Kingdom overview with sheets closed, retain the canonical at-least-80% unoccluded world goal; use compact edge controls. Temporary focused inspectors may occupy more space and must dismiss cleanly.
- Do not scale entire support boards down to fit. Reflow, use appropriate panels/tabs or deliberately scroll secondary content. Primary action, selected subject and important costs remain visible.
- All controls need relevant default/focus/pressed/disabled/loading/error/success states. Disabled actions explain the specific prerequisite. Modal focus is trapped and restored; background cannot receive input. Cost/target selection remains reversible until the real confirmation boundary.
- Resources stay out of active Tactical, Defense and result HUDs. Economy changes appear in the correct preparation/result context without adding a second purse.

### Typed implementation and evidence contracts

These are interface requirements, not permission to replace existing working serialization. Adapt the current equivalent types/functions where present. Document any necessary migration and preserve old valid saves.

```ts
type Gate = 'PASS' | 'FAIL' | 'BLOCKED' | 'UNVERIFIED' | 'NOT_APPLICABLE';
type EvidenceKind = 'STATIC_CODE' | 'UNIT_TEST' | 'BROWSER_FLOW'
  | 'VISUAL_REVIEW' | 'PACKAGE_CHECK' | 'PHYSICAL_DEVICE' | 'OWNER_REVIEW';
type Affine = [number, number, number, number, number, number];
type Viewport = { width: number; height: number; dpr: number };
type CoreCommand = {
  id: string;                 // unique transaction identity, reuse rules enforced by core
  type: string;               // existing validated command vocabulary
  payload: Record<string, unknown>; // validate the command-specific schema
};
// existing call shape: command(state, input, now, data); now is finite epoch milliseconds
type GearSlot = 'helm' | 'weapon' | 'offhand' | 'armor' | 'boots' | 'accessory';
// Concrete existing payload examples, not a replacement for the whole core vocabulary:
type BuildInput = { id: string; type: 'BUILD'; payload: { plotId: string; building: string } };
type ForgeInput = { id: string; type: 'FORGE'; payload: { slot: GearSlot; quality?: 0 | 1 | 2 | 3 } };
type EquipInput = { id: string; type: 'EQUIP'; payload: { itemId: string } };
type UnequipInput = { id: string; type: 'UNEQUIP'; payload: { slot: GearSlot } };
type DesignEvidence = {
  referenceId: string; referencePath: string; referenceSHA256: string;
  runtimeView: string; fixtureDescription: string; synthetic: boolean;
  viewport: Viewport;
  // Normalized viewport rectangles, each [left, top, width, height] in 0..1:
  referenceRegions: Record<string, [number, number, number, number]>;
  runtimeRegions: Record<string, [number, number, number, number]>;
  regionPurpose: Record<string, string>; // main subject, world, HUD, menu, inspector, etc.
  minBodyTextCssPx: number; minHitTargetCssPx: number;
  occludedEssentialContent: string[]; intendedDeviations: string[];
  screenshotPaths: string[]; status: Gate; reviewNotes: string[];
};
type InteractionEvidence = {
  id: string; featureIds: string[]; requirementIds: string[];
  entry: string; preconditions: string[]; inputSteps: string[];
  expectedStateChange: string; expectedVisibleChange: string;
  cancelCase: string; failureCases: string[]; reloadExpectation: string;
  returnDestination: string; viewport: Viewport;
  beforeSaveHash: string; afterSaveHash: string;
  kind: EvidenceKind; status: Gate; evidencePaths: string[];
  failureReason?: string;
};
type SceneEvidence = {
  scene: 'kingdom' | 'adventure' | 'tactical' | 'defense'; age: number; // integer 0..7
  runtimeSourcePath: string; runtimeSourceSHA256: string;
  sourceWidth: number; sourceHeight: number; worldToSource: Affine;
  sourceToViewport: Affine; tracePath: string; traceSHA256: string;
  computedIntersections: number; minimumClearance: number;
  measuredConstraints: Record<string, number | boolean>;
  screenshots: string[]; geometryGate: Gate; visualGate: Gate;
  reviewerNotes: string[];
};
type RequirementEvidence = {
  id: string; source: string; implementationPaths: string[];
  codeGate: Gate; interactionGate: Gate; visualGate: Gate;
  packageGate: Gate; deviceGate: Gate; ownerGate: Gate;
  evidencePaths: string[]; remainingWork: string[];
};
```

All paths are repository-relative in machine evidence; all hashes SHA256 of actual bytes. Missing evidence is UNVERIFIED, not PASS. NOT_APPLICABLE needs a specific reason and cannot remove a required feature. Fixture records explicitly state synthetic state; earned records list commands/time simulation and grants, if any. Before/after hashes supplement, not replace, meaningful state assertions.

Required deliverables: integrated source/art; a complete OWN-01..OWN-19/SYS-01..SYS-16 and G01..G16 evidence matrix; a 30-reference design matrix; 32 scene records; class/kit/role/clip matrix; natural journey results; responsive screenshots and motion evidence; updated regression results; final package closure/hash; current status/handoff/build notes; and a deferred device checklist. Use one dated executor evidence namespace such as `qa/game-completion-20261012/`, with large media in a corresponding ignored `output/` folder. Preserve prior evidence. If files are ignored, state that plainly and do not claim Git alone transfers them.

## 4. Step-by-Step Instructions

Each numbered step has one primary action. The contracts in section 3 define the details. Verify the listed phase gate before depending on its output; a blocked asset does not prevent independent code or local review work.

### Phase A — establish an honest baseline

1. Record the current HEAD, branch and dirty-file inventory in the executor evidence namespace.
2. Read the authoritative inputs and resolve dated instruction precedence.
3. Record the actual installed runtime/build tool versions.
4. Capture the current source/asset hashes needed for audit comparisons.
5. Run the existing regression suite with evidence redirected away from prior reports.
6. Populate the complete requirement matrix with current evidence and remaining work.
7. Mark invalid scene/visual/rig completion claims as rejected historical evidence in the current status record.
8. Map all 30 reference compositions to measured subject/UI regions, actual runtime states and required interactions.

**Gate A:** every requirement has a disposition; the current audit defects are represented; no “missing screen button” is mistaken for the whole implementation gap; existing valid repairs and owner data are protected.

### Phase B — define and implement coherent interaction/navigation

9. Inventory every existing visible control and its actual command or navigation consumer.
10. Specify a state-transition table for entry, selection, preview, confirmation, outcome and return of every feature.
11. Implement the compact roaming navigation contract using existing routing primitives where adequate.
12. Implement the secondary menu and contextual Back/Close behavior.
13. Implement shared selection feedback for actual world objects and entities.
14. Implement a contextual inspector/action surface tied to the current selection.
15. Implement the modal focus/input boundary for confirmations and destructive choices.
16. Implement clear loading, unavailable and failure feedback for command execution.
17. Verify a real plot-to-build-to-completion-to-inspect-to-return journey through the new interaction pattern.
18. Remove obsolete duplicate section controls after their replacement journeys work.

**Gate B:** Home resumes the right scene; no permanent 13-section row; one meaningful active context; pointer/keyboard input targets the correct object; previews/cancel do not mutate campaign state; replacement navigation does not orphan any required feature. This is the first implementation checkpoint, not a reduced final scope.

### Phase C — register all physical scenes and art dependencies

19. Resolve the actual terrain consumer for each of the 32 age/scene combinations.
20. Measure source-specific roads, banks, decks, obstacles, site approaches and usable ground.
21. Correct the per-source art/registration defects using reviewed local material where sufficient.
22. Prepare necessary missing-source repair requests under the existing paid authority if local material is inadequate.
23. Integrate only accepted repaired sources with truthful hashes and provenance.
24. Replace unconditional scene PASS logic with assertions computed from the actual runtime source and trace.
25. Align terrain, objects, selectors, routes and inverse picking through the shared scene transforms.
26. Verify all 32 scene records with boundary/path/clearance assertions and visual overlays.
27. Verify every active building/prop silhouette, alpha edge, footprint, era and ground contact at intended size.

**Gate C:** no wrong-source certificate; no accepted nonzero forbidden intersections; every river crossing and lane follows the actual displayed geometry; shared topology is retained; visual review agrees with computed evidence. A purely color-based mask is not a semantic physical trace.

### Phase D — finish class art, equipment and real motion

28. Replace the malformed Healer assembly with a coherent reviewed body and accurate multi-input or single-source provenance.
29. Complete the eight-class/four-kit-era appearance matrix using legitimate reusable components.
30. Complete period/role-correct art for troops, creatures, attackers, towers, workers and transport.
31. Define measured body/gear/mount attachment points for each active rig family.
32. Integrate all six equipment slots into visible, class-compatible worn appearance.
33. Connect the reviewed articulated humanoid parts to actual world rendering.
34. Connect reviewed mount/vehicle parts to actual travel rendering.
35. Implement the required action clips for each applicable role.
36. Drive Tactical acting/attack feedback from the real queue/action contract instead of nonexistent `battle.active`.
37. Drive Defense/work/travel motion from real committed simulation events.
38. Implement reduced-motion variants without changing simulation outcomes.
39. Inspect motion/contact extremes and interruption/reload behavior for every active rig family.

**Gate D:** named bones are visibly consumed; no whole-image bobbing called gait; Healer is anatomically coherent; Stone/Future kit selection is correct; worn objects do not float over incompatible painted weapons; all six slots have functional and visual outcomes; current phase/action feedback matches the engine.

### Phase E — complete Kingdom and Adventure as playable places

40. Complete the sparse Day 1 composition and every plot's direct build interaction.
41. Complete constructed-building inspection and upgrade feedback.
42. Complete Town Hall age progression and separate Walls interaction.
43. Complete facility-based recruitment, workshop and Armory entry flows.
44. Complete the eight-age settlement composition and coherent environment changes.
45. Complete actual site/pickup/guard presentation on Adventure terrain.
46. Complete route preview and explicit legal travel confirmation.
47. Complete visible foot/mount traversal to the committed destination.
48. Complete contextual site outcomes with saved offers, fog and once-only rewards.
49. Complete guard-to-Tactical-to-original-site and town-return transitions.
50. Complete rest/day/weather/mana and offline-resume feedback using adopted rules.

**Gate E:** a natural new campaign can build, recruit, leave, move, enter an encounter, return and resume without grants or developer navigation. The world is interactive and dynamic; pads/lines/labels are selection aids rather than substitutes for the settlement and Adventure sites.

### Phase F — complete Tactical, Defense and War journeys

51. Complete Tactical roster placement and legal deployment presentation.
52. Complete active-stack/initiative visualization with actual engine ordering.
53. Complete direct battlefield target selection for movement, melee, shooting and spells.
54. Complete action-specific previews and visible combat feedback.
55. Complete Defend/Wait/Auto/Retreat interaction states and return behavior.
56. Complete the composed battle result screen from persisted actual outcomes.
57. Complete Defense pad/tower/range inspection and selection.
58. Complete roster/hero deployment and preparation purchase/retrofit flows.
59. Complete visible role-specific Defense threats, telegraphs, projectiles and effects.
60. Complete Defense ability targeting, wave controls and pause/speed presentation.
61. Complete Defense result and campaign-return presentation.
62. Complete setup and consequence labeling for all five War options.
63. Verify practice isolation and deterministic offline Challenge journeys.
64. Verify once-only settlement and saved active sessions across all combat modes.

**Gate F:** a player controls units/pads/targets in the scene; stack counts/targets/initiative are readable; actors are grounded; no offscreen invisible threats; result rewards and losses reconcile once; Skirmish cannot mutate campaign resources/XP/items/mana/casualties; Endless does not falsely claim victory at its old wave boundary.

### Phase G — complete supporting experiences and the unified design

65. Complete the dominant full-body Hero chamber and contextual equipment comparison.
66. Complete the designed skill progression interface with actual point spending.
67. Complete the spellbook and legal cast-selection interface.
68. Complete the Forge workshop, selected-item presentation and craft result flow.
69. Complete the carried/equipped inventory interface and compatibility feedback.
70. Complete Army recruitment/codex/capacity/rank presentation.
71. Complete the contextual Market transaction sheet.
72. Complete Story/rival/branch/Future journal presentation.
73. Complete quest/milestone progress, real destinations and once-only claims.
74. Complete the target-anchored tutorial and saved skip/review behavior.
75. Complete functional Settings/audio/reduced-motion/Help/Credits/Privacy surfaces.
76. Complete save slots, file flows and recovery presentation.
77. Complete Home composition and new-campaign/replacement/continue flows.
78. Apply the coherent icon/material/control-state design system to all remaining surfaces.
79. Adapt every screen to the four landscape sizes using readable screen-space layouts.

**Gate G:** all 30 references have implemented counterparts or documented design-system mappings; unmocked surfaces match the same language; no isolated button-list substitutes; no unfinished controls, borrowed mock stats or inaccessible overflow; all required features remain discoverable.

### Phase H — verify the complete desktop game

80. Add targeted regression coverage for new command boundaries, navigation, queue-driven feedback and save compatibility.
81. Run the complete current regression suite.
82. Execute the natural connected journeys defined in section 6 through ordinary visible controls.
83. Execute the full responsive state/viewport matrix with asserted actual views and state identities.
84. Capture actual motion evidence for travel, combat, work and mount contact.
85. Compare every required runtime composition with its reference at native and intended phone size.
86. Measure real hit ownership, clipping, contrast, text sizes and focus behavior.
87. Profile representative dense desktop scenes with declared hardware and scenario parameters.
88. Repair failures found by the complete desktop review.
89. Rerun affected checks after the repairs.

**Gate H:** no unresolved required functional/visual defect; all evidence is tied to current source/assets; old screenshots and hard-coded PASS reports cannot close a new gate. Desktop profiling is not proof of Android 60fps. A failed physical trace or missing required rig keeps the game INCOMPLETE even if every unit test passes.

### Phase I — package and hand off for independent review

90. Build the final standalone web output from the completed current source/art.
91. Build the preview APK from that exact web output.
92. Verify package closure, file hashes, CRC, application ID and zero permissions against the final artifact.
93. Record package size and runtime asset usage without deleting protected evidence or source material.
94. Update all requirement gates and status/handoff/build documents with current evidence.
95. Deliver the full comparison gallery, journey results, source snapshot and package record for independent desktop review.
96. Prepare the later physical-device checklist with native file/dialog/lifecycle/input/audio/performance cases.

**Gate I:** a complete, reproducible desktop candidate and exact package exist; independent review is explicitly pending until performed; physical-device and owner gates remain UNVERIFIED/deferred. If required work is blocked, provide its exact IDs, attempted solution, evidence, remaining dependency and next action, and keep the product INCOMPLETE.

## 5. Edge Cases & Failure Modes

| Failure mode | Required handling / proof |
| --- | --- |
| New work appears while executing | Recheck hashes/diff before edits; preserve others' changes; rerun affected verification against a named current snapshot. |
| Mock contains impossible/incorrect content | Preserve approved composition while following source-backed mechanics and documented era corrections; record the deviation explicitly. |
| A screen exists but has only navigation buttons | Keep the feature incomplete until its real input/command/result/save/return journey passes. |
| Hidden or wrong view during screenshot capture | Assert requested view, class/age/session and active state before capture; stop that record on mismatch. |
| SVG art partly decoded during capture | Wait for actual image readiness/settling; do not certify partial screenshots or blame missing anatomy without checking native bytes. |
| False scene/rig acceptance | Compare measured results with explicit constraints; FAIL on contradiction; never accept from a filename/hash/declared bone list alone. |
| Narrow landscape / menu expanded / long cost | Reflow or scroll intentionally; retain visible subject and primary action; test real pointer interception and full label readability. |
| Dense world targets smaller than fingers | Offer accessible contextual target alternatives without replacing direct world interaction; avoid overlapping invisible 48px hit regions. |
| Rapid repeated tap or stale preview | Revalidate current command preconditions and transaction identity; spend/reward once; explain invalidated state. |
| Cancel/Back/Escape outside confirmation | Restore origin/focus/selection; spend nothing; do not silently advance a battle or restart travel. |
| Modal open during background navigation | Block programmatic and pointer background transitions; preserve dialog focus and battle state. |
| Missing resources/facility/capacity/compatibility | Explain the exact reason; do not deduct partially or grant a compensating item. |
| Age advances with old equipped gear | Preserve item IDs/stats and old item appearance; update default kit separately; no free item upgrade. |
| Empty/full inventory, duplicate artifact, wrong slot | Enforce core compatibility/capacity; return a useful error with original state intact. |
| Active stack dies, waits or gains morale action | Resolve current queue through core API; animate the committed event; do not infer turn from a nonexistent/stale field. |
| Animation interrupted/reduced/paused | Keep logical state deterministic; visual completion never pays/spends; reload resumes/settles committed presentation safely. |
| Background Defense / 2× / final-wave blast | Freeze according to lifecycle policy; preserve fixed-step behavior; no hidden damage, skipped settlement or duplicate wave reward. |
| Lost/retreated encounter / result reload | Preserve real survivors/mana/origin; pending result persists; repeat claim pays zero. |
| Practice/Challenge setup canceled | Preserve campaign state according to the mode contract; do not leak temporary XP/items/early-call rewards. |
| Damaged/unsupported/imported save | Validate before replacement; distinguish absent from corrupt; retain usable old save and recovery options. |
| Storage quota or failed write | Report failure; do not falsely show Saved or erase the last valid save. |
| File picker cancel/native lifecycle interruption | Resolve pending callbacks safely; retain campaign state; leave physical confirmation for the later device gate. |
| No audio gesture or user mute | Respect browser/native autoplay limits and independent saved buses; do not retry sounds continuously or enable network media. |
| Required image source unavailable | Mark exact affected IDs BLOCKED; complete other local work; use authorized necessary repair only after readiness/budget reconciliation. |
| Provider timeout/429/UNKNOWN liability | Apply the recorded coordinator rules; no blind retries, reserve reset or invented zero-cost claim. |
| Tests pass but mock/interaction review fails | Keep the failed visual/interaction requirement open; do not call the whole game RELEASE_READY. |
| Current APK omits a newly referenced asset | Fix closure discovery/packaging and rebuild; do not remove a valid consumer to force parity. |

## 6. Acceptance Criteria

Every checkbox is pass/fail unless expressly labeled as a later gate. Link it to current evidence in the requirement matrix. Do not substitute promises, debug fixtures or successful function calls for visible player journeys.

### Coverage and navigation

- [ ] All 19 owner and 16 system requirements are accounted for using current superseding authority.
- [ ] All G01–G16 requirements and all 30 reference rows have current implementation/evidence links.
- [ ] All 32 age/scene combinations have source-bound physical and visual evidence.
- [ ] All eight classes/four kit eras and all active role/clip families have complete matrices.
- [ ] Home Continue resumes the correct saved origin/session; replacement and recovery work.
- [ ] The flat 13-section navigation is replaced by compact navigation plus contextual world interaction.
- [ ] Each feature demonstrates entry → selection/preview → legal action → visible outcome → save/reload → correct return.
- [ ] The same feature also demonstrates cancellation and relevant failure states without unintended mutation.
- [ ] Every planned feature is reachable through ordinary visible controls without developer commands.

### Mandatory connected browser journeys

Execute these with isolated fresh saves and real pointer/keyboard controls. Use seeded core/time simulations as separate supplemental evidence for long progression; label them explicitly. Do not claim an earned journey when importing a mature fixture.

| Journey | Required observable evidence |
| --- | --- |
| J01 Fresh start | Home → class choice → sparse Kingdom → correct first tutorial target; initial inventory/resources/plots match the contract. |
| J02 Build/upgrade | Empty plot → exact build preview → cancel unchanged → confirm once → worker/scaffold → completion → inspect → upgrade → reload. |
| J03 Recruitment | Real Barracks unlock → recruit → capacity/reinforcement feedback → Army roster → same stack in Adventure/combat. |
| J04 Age progression | Real Hall/payment gate → next-age world transformation → retained item identities → same plot/road topology → reload. All ages additionally covered by declared fixtures. |
| J05 Adventure travel | Leave town → select legal route → cost preview → cancel unchanged → confirm → grounded crossing/traversal → correct destination/fog/movement after reload. |
| J06 Site/guard | Visit site → saved offer/loot → no reroll on cancel/reload → guard → Tactical → actual result → correct originating site. |
| J07 Tactical interaction | Deployment → unit selection → initiative/targets → Move/Melee/Shoot/Spell/Defend/Wait as legal → meaningful feedback → saved queue. Include flyers and a morale bonus case. |
| J08 Retreat/Auto/results | Actual focus-trapped Retreat cancel/confirm, Auto under normal rules, victory/defeat/retreat summaries and once-only settlement after reload. |
| J09 Defense | Preparation → pad/tower/range → hero/army deployment → visible wave threats → ability target → pause/2× → save/reload → real result. |
| J10 War modes | Siege/Duel/Endless/Skirmish/Challenge each has working setup/start/result/return; practice isolation and seed reproducibility verified. |
| J11 Craft/equip | Hero slot → Forge correct category/item → Armory/quality/cost → craft → bag comparison → equip/unequip → visible body/stat change → reload. Repeat functional coverage for six slots. |
| J12 Hero progression | Earned point/skill offer → valid selection → changed combat stats; Wisdom 3 → legal wounded-stack Resurrection → HP/mana/casualty outcome. |
| J13 Creatures/roster | Eligible dwelling → fixed offer → recruit → roster/codex → combat → persistent survivor/rank change; supplemental earned test covers all eight identities. |
| J14 Story/quests | Rival/branch choice → changed journal/progress → milestone/quest claim → second claim zero → Future conclusion from the saved branch state. |
| J15 Market | Locked Stone state → Bronze unlock → insufficient balance → cancel → successful buy/sell → exact once-only resource delta. |
| J16 Recovery | Save all slots → load correct slot → valid export/import → canceled import → corrupt/unsupported file → preserved usable campaign and recovery. Native picker/export behavior remains later. |
| J17 Settings/tutorial | Independent Music/SFX, reduced motion, tutorial skip/review, keyboard focus, rotation message and return to unchanged state. |
| J18 Whole-game continuity | Build → recruit → equip → travel → battle → return → defend → claim objective → save/relaunch, with the same entity IDs and consistent costs/survivors. |

### Visual, art and accessibility

- [ ] Actual screenshot pairs exist for all 30 references with runtime state/viewport/hash labels.
- [ ] Native-size and actual phone-size inspection confirms composition, subject prominence, material/light consistency and readable hierarchy.
- [ ] Approved mock inaccuracies are corrected without introducing new mechanics or losing required composition.
- [ ] Healer has coherent anatomy and truthful source transforms; no visible magenta lines, detached fragments or incompatible arm/boot assembly.
- [ ] No wrong-era fallback silently substitutes for a required class kit.
- [ ] All six equipped slots have correct identities/stats and reviewed visible appearance.
- [ ] Actual world motion uses articulated role-appropriate parts and correct contacts; metadata or static bobbing does not pass.
- [ ] Terrain, selection, buildings, paths and targets remain aligned during resize/pan/zoom and inverse picking.
- [ ] All four landscape sizes pass target ownership, no overlapping essential labels, readable screen-space typography and visible primary actions.
- [ ] Body/instruction text follows the canonical 16px baseline; documented compact secondary text is at least 14px; no tiny scaled SVG instructions remain.
- [ ] Contrast, visible keyboard focus, modal trapping/restoration and non-hover interaction are verified.
- [ ] The battle/result HUD has no treasury rail or unexplained second economy.
- [ ] All named skills/spells/resources/slots have consistent, distinguishable icon semantics.

### Code, persistence and package

- [ ] Existing passing regressions remain passing; new meaningful boundary/interaction regressions cover changed behavior.
- [ ] Simulation/commands are deterministic and separate from animation/UI selection.
- [ ] The Tactical attack branch uses the actual queue/action state and displays the correct committed action.
- [ ] Save compatibility, duplicate-command handling, practice isolation and once-only settlement remain valid.
- [ ] Browser tests assert requested versus actual view/state; asset/page errors are zero on required journeys.
- [ ] Current package includes every required runtime asset, with matching source/dist/www/APK bytes and CRC PASS.
- [ ] Exact package filename, byte count, SHA256, source commit/dirty snapshot and test evidence are recorded.
- [ ] Merged and packaged manifests retain preview identity and zero permissions; runtime has no external font/media/data dependency.
- [ ] Desktop performance measurements declare scenario/hardware and do not claim device results.
- [ ] Completion claims distinguish implemented, automated-tested, desktop-played, visually reviewed, package-verified, device-tested and owner-accepted.

### Completion labels and later gates

Use **INCOMPLETE** while any required game/art/interaction/desktop/package item is FAIL, BLOCKED or UNVERIFIED. When those items pass, use **DESKTOP CANDIDATE — INDEPENDENT REVIEW PENDING** until the separate review actually passes. After that, use **READY FOR DEFERRED DEVICE TESTING**, not production/release-ready. PHYSICAL_DEVICE and OWNER_REVIEW remain UNVERIFIED in this executor pass.

The later device checklist must include actual safe insets/touch sizes, Back behavior, dialogs, file-picker/export/cancel flows, activity/background/kill/relaunch behavior, save integrity, dense-frame/memory/thermal behavior, audio and zero granted permissions. Android 60fps is a device measurement target, not a desktop assertion. Do not request interim owner approval as a substitute for completing the already authorized game.

## 7. Do NOT

- Do not produce another prototype, static gallery, dashboard or page/button checklist and call it the game.
- Do not stop after a theme change, navigation rewrite, single vertical slice, art batch or successful test run.
- Do not remove gameplay scope to make completion easier.
- Do not replace contextual world actions with a permanent row of links to every section.
- Do not use painted mock screenshots with hotspots as dynamic scenes.
- Do not invent equipment names, currencies, structures, combat rules or rewards from generated text.
- Do not turn synthetic fixtures or accelerated core tests into claims of ordinary human-earned play.
- Do not mark 32 scenes accepted because a script wrote PASS or because a hash matches an inactive source.
- Do not silence failing geometry checks, fabricate guide files, relax protected acceptance thresholds or alter legal topology to fit bad art.
- Do not certify a rig from exported bone names, unused JSON frames or whole-image wobble.
- Do not retain wrong-era bodies as a finished fallback or attach oversized inventory icons as proof of all worn equipment.
- Do not shrink entire screens until phone text fits; reflow the UI.
- Do not remove accessible contextual alternatives while adding direct scene interaction.
- Do not mutate campaign economy/turns/rewards from rendering callbacks or invent a temporary combat purse.
- Do not discard, reset or silently migrate valid saves without a tested compatibility path.
- Do not overwrite originals, historical producer evidence, independent audit captures or another executor's uncommitted changes.
- Do not rerun the old audit/scene-closing scripts unchanged and reuse their self-attested claims.
- Do not treat historical budget headroom or UNKNOWN provider outcomes as available money.
- Do not make filler purchases, reset reserve/attempt history, parallelize paid operations or blindly retry an ambiguous POST.
- Do not add frameworks/dependencies, broad refactors, servers/accounts, store publishing, permissions, cleanup or Git publication unrelated to the authorized work.
- Do not run physical-device tests before the whole game, final package and independent desktop review are complete.
- Do not claim independent review, owner acceptance, production readiness or device performance that has not actually occurred.
