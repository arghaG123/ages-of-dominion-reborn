# Visual repair and live review — 18 October 2026

**Status: INCOMPLETE.** This is a targeted visual repair pass against the current source and the approved mock direction. It is not whole-game visual acceptance, an independent desktop review, or a release gate.

## Live review setup

- Source served from the local development server at `http://127.0.0.1:4174/?audit=1`.
- Fresh test campaign created only on that isolated origin; no owner save was opened. The test campaign was used for a natural wall-construction UI sequence and a Tactical Duel/Retreat check.
- Inspected the live UI at 825×375 and 933×424 landscape viewports. Console error list was empty.
- Screens listed below were viewed live. This pass did not archive browser screenshots to this folder; the review was not independently signed off.

## Repairs made

- **Stone Kingdom family:** added four high-detail candidate paintings for no wall, scaffold, built timber palisade and the taller wall. The wall gate is placed at the right-side bridge approach, and the support hues/lighting match across the family. A first wall candidate with a misplaced front gate was rejected before copying. `src/client/kingdom-view.js` routes Stone wall phases through the new family; later ages retain their existing paintings.
- **Small landscape support screens:** reserve the bottom navigation strip and the left dock strip in the scroll viewport. Market cards use a two-column layout at short heights, with buy/sell controls placed side by side. This prevents controls from sitting under the dock or navigation at 825×375.
- **Army inspector:** each stat now has its own bounded label/value tile. The 3×2 layout remains readable at both inspected landscape sizes.
- **Hero and spellbook:** skill and spell buttons now show their names beside the icons and rank/mana. At short heights, the Hero footer uses one compact status strip above the navigation. When the spellbook is open, socket labels face inward and the panel widens enough to show names.
- **Navigation/details:** changing the primary screen closes the old detail panel; opening a closed panel starts at the top. The panel title stays opaque and its close control stays in view while scrolling.
- **Kingdom actions:** removed the duplicate Town Hall Upgrade action when Town Hall itself is selected; a selected-site build action appears in either the dock or the inspector, not both. These changes were already present in this repair session and were checked live.

## Screen observations

| Area | Live result | Remaining visual or acceptance gap |
|---|---|---|
| Kingdom | At 825×375 the rebuilt Stone painting reads as open ground around the Hall; the selected site remains a clearing. A confirmed natural UI build progresses from scaffold to an integrated timber palisade with the road/bridge gap on the right. Costs were 120 stone and 40 wood. | The family is a generated visual candidate. It has not received a complete source-feature/gate trace or independent owner review. Other ages, building layers and all 18 site states remain open for full review. |
| Adventure | The valley painting, travel action and status block are visible; the 16:9 world is letterboxed at the 2.2:1 phone viewports. | The map shows only a bounded sample; full natural travel journeys, fog progression, and every site/guard/creature interaction are not accepted here. |
| Army | Clubman/Slinger cards and a six-stat inspector are legible at 825×375 and 933×424; no label collision remains in the inspected inspector. | Unit art/roles, all formation states, class/age coverage and natural recruitment journeys remain separate acceptance work. |
| Hero and equipment | All six socket names stay inside the usable play area; a compact class/stat line clears the bottom navigation. | The inspected save has empty sockets. This does not verify naturally earned/worn gear or garment/weapon fidelity; item showcase M22 remains open. |
| Skills and spells | Skill and spell names, ranks/mana and legal Tactical targets are visible. The Tactical spell panel keeps its title and close control while scrolled. | The panel is scrollable and only some entries appear at once. Wisdom progression, all spell effects, and natural journeys remain open. |
| Forge | Six slot choices and selected-slot detail fit at 825×375. | The large selected-item showcase from M22 is still missing; Stone-age armory lock is expected on this fresh campaign. |
| Market | Four resources display in a compact 2×2 card grid at both sizes. Stone-age trades are visibly locked, and card controls clear the dock/navigation. | The unlocked Bronze trading screen was not exercised in this live browser pass. |
| War and Tactical | All five mode cards are present in a scrollable layout. Starting a Tactical Duel shows living formations, legal action controls, and seven eligible spell casts; Retreat explains consequences before confirmation. | Visual quality and natural outcomes across all five modes are not accepted by this spot check. Combat remains letterboxed to preserve the 16:9 battlefield. |
| Story | Chapter copy and both choices are visible; archive stays in the scroll area above the navigation. | Only the initial chapter was viewed. The full chapter/quest sequence and Future conclusion remain open. |
| Settings and Help | Settings sliders remain inside their central panel; Help/credits/privacy cards fit without overlap. | Detailed mock-by-mock comparison and keyboard/touch acceptance remain open. |

## Generated image family

Reference: `assets/derivatives/mock-led-20261016/kingdom/kingdom-stone-ground.png` and the approved Stone Kingdom composition in M03. The generated images are 1678×937 RGB PNGs; their aspect ratio differs from the registered 1376×768 frame by less than 0.1%, enforced by `tests/four-repairs-20261017.test.mjs`. Full literal prompt text is retained in the task's image-generation interaction; this report records the source/output lineage and acceptance limits.

| State | Project file | SHA-256 | Generated output |
|---|---|---|---|
| No wall | `assets/derivatives/kingdom-stone-family-20261018/stone-ground.png` | `d4b066515ff33bf7bc24ccbc5a2aeb384337c21e8d8c1156c2dc40520038c654` | `C:\Users\pupan\.codex\generated_images\01a14d31-4376-7570-bde1-ae01df1f91de\exec-96d84229-c98f-40d3-99f9-27c6ecdeae03.png` |
| Scaffold | `assets/derivatives/kingdom-stone-family-20261018/stone-scaffold.png` | `672a55ef063492f68b2473d4021f3e927c8a90c3d9f607c281d64003305ae50d` | `C:\Users\pupan\.codex\generated_images\01a14d31-4376-7570-bde1-ae01df1f91de\exec-dc6cc08e-15c6-4577-b445-90dcd043331b.png` |
| Built wall | `assets/derivatives/kingdom-stone-family-20261018/stone-wall.png` | `9a89e075c291de6441d61778cb2a5e2e2abcfe7aac14e073c659739c1166b30d` | `C:\Users\pupan\.codex\generated_images\01a14d31-4376-7570-bde1-ae01df1f91de\exec-034ffb9c-098c-4f82-9b95-37a05069630a.png` |
| Taller wall | `assets/derivatives/kingdom-stone-family-20261018/stone-wall-tall.png` | `d7e5147ba79fa071d5a2ad41a53e70c7aff1c7b071ee937dfa26f1dd0ceb5d9c` | `C:\Users\pupan\.codex\generated_images\01a14d31-4376-7570-bde1-ae01df1f91de\exec-ccc2a0c5-4250-4994-9e3e-7df397ed1269.png` |

## Verification

- `node --test tests/*.test.mjs` — **180/180 PASS** (final run). The first run found one stale test expectation for the previous Stone ground filename; that assertion was updated before the final run.
- Live browser console errors — **0**.
- Natural UI wall sequence — open ground → scaffold → completed wall; costs were charged once after confirmation. This is one isolated campaign journey, not full game acceptance.

## Still required

- Compare every required M01–M30 view, button and state against the approved pixels; this pass reviewed representative screens, not the full mock set.
- Complete source-bound Kingdom tracing and review all ages/building layers, scene geometry, actors, worn equipment, animations, roles, natural journeys and browser persistence.
- Re-run the failed native IndexedDB probes; produce a current standalone desktop candidate; obtain independent desktop review before any final APK. Mobile/device and owner acceptance remain later, separate gates.

No Vertex/provider call, APK build, device action, Git mutation, cleanup or owner acceptance occurred in this pass. Product remains **INCOMPLETE**.
