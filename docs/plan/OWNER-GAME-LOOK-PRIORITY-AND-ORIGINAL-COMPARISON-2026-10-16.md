> **Latest owner clarification — detailed mock-led execution, 16 October 2026:** The ADVANCED MOCKS are the target finished design/look; the original game is reference context, not the acceptance ceiling. Read the [step-by-step solutions manual](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) and give the other AI [ONE complete updated executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). It includes 30 individual mock recipes, 10 concrete repair procedures, 18 journey assertion lists, file/function ownership, layout/transform examples, storage repair, budget controls and final evidence checks, plus all G01–G16 and the complete original 96-step sequence. This AI remains planner/verifier only. These are implementation instructions, not completed fixes; product stays INCOMPLETE.

# Game appearance first — original comparison and owner correction, 16 October 2026

**Owner's first concern is how the actual game looks. Current visual acceptance: FAIL.** The owner describes the reborn build as a combination of big buttons, text and some images, rejects the blank Stone plots and box-like wall, and requests comparison with the original game. The owner explicitly reiterates: **this AI verifies/plans; the other AI implements.** No production repair, image call, build, dispatch or device action is authorized to this verifier by this clarification.

This is a required correction within the full game scope, not an optional polish backlog. Passing mechanics/tests does not defer it until after owner review. The [complete executor plan](COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md), [independent audit](INDEPENDENT-WHOLE-GAME-VERIFICATION-2026-10-16.md) and [art/budget authority](OWNER-ART-STYLE-HEALER-AND-BUDGET-2026-10-16.md) remain applicable.

## What was inspected

- The original repository `C:/dev/ages-of-dominion` remained read-only. Its **existing** `dist/` was served read-only at isolated `127.0.0.1:4190`, without rebuilding or modifying it. The original `dist/index.html` is dated 2 October 2026, 8,560 bytes, SHA256 `fd2be8abec37b3780856f03a67cee8c402ff7c649de8e6359a345fa3768ea0d4`. This is a review of that built artifact, not a claim about an unbuilt latest old source.
- Fresh ordinary New Game → Choose Knight → Kingdom, tutorial dismissal and Hero-entry attempt were observed. Hero was locked until first battle; `original-hero-locked-1280.png` records that lock and **is not a Hero-screen capture**. No old campaign was imported or granted progression.
- Fresh evidence: `qa/independent-verification-20261016/original-home-1280.png`, `original-kingdom-clean-1280.png`, `original-hero-locked-1280.png`. The old game uses a portrait stage inside the landscape viewport; this does not change the reborn whole-game landscape decision.
- Separately inspected retained old screenshots: `C:/dev/ages-of-dominion/docs/after/stone-03-kingdom.png`, `stone-05-hero.png`, `stone-08-forge.png`, and `docs/handoff/evidence-2026-10-02/kingdom-after-harvest.png`. These are historical visual references, not fresh functional proof.
- Compared them with the fresh reborn 52 base views, 32 imported age/mode views, eight settled class views and approved 30-reference overview. No claim that the original is flawless, fully realistic, orientation-compatible or the final target.

## Specific visual conclusions

### First impression and hierarchy

The original places a recognizable inhabited settlement/hero and world imagery at the centre, with icon-based edge clusters, a compact identity portrait, terrain-associated buildings and visible boundary structures. Its historical Hero/Forge views have purpose-specific framing and materials. Some old art is stylized, some old HUD is oversized, and its prebuilt starter differs from the reborn sparse-start requirement; those shortcomings are not adoption instructions.

The reborn screen repeatedly exposes generic rectangular controls, extensive option/copy panels and separate image plates. The Hero room is a gradient SVG floor, Forge a generic anvil, and the city is read as marked development rectangles over a painting. Even when individual pixels are realistic, the scene does not have the agreed integrated game composition. This is an art-direction, world-composition and interaction-hierarchy failure, not a missing border colour or font tweak.

**Executor:** keep the world/subject visually dominant and put ordinary interactions on actual buildings, plots, units and items. Use compact edge controls and short contextual inspectors opened by a selection. Full 48px owned touch targets and accessible alternate target lists remain required; large permanent text/button panels are not the only way to provide them. Preserve readable screen-space type rather than shrinking text to conceal the problem.

### Stone Age plots

`src/client/main.js:451-498` renders rectangular site polygons and stakes; `presentation.js:4-6` labels brass outlines/stakes as the empty-site presentation. The current ordinary overview looks like a persistent layout/debug grid. Sparse does not need to mean sterile, unfinished or diagrammatic.

**Executor:** preserve Hall 1, exactly 17 truly empty selectable sites and Walls 0. Make the empty ground a believable sparse settlement: naturally shaped prepared clearings, worn tracks, blended soil/grass, modest stakes/ropes where appropriate, terrain and era-appropriate nonfunctional dressing. Such dressing must not imply a facility, production, ownership or upgrade that does not exist. Reveal a subtle selected/hover/focus build footprint contextually; avoid outlining every unbuilt pad with a bright box in the default scene. Show real foundations/scaffold/work activity only while a paid construction job is active, and actual completed buildings only after completion. Maintain all site identities, costs, picking and legal road/river clearance.

### Walls

`src/client/presentation.js:47-77` computes min/max of all site rectangles, expands the bounding rectangle and leaves a small gate gap. `src/client/main.js:430-439` renders it as a thick light SVG polyline when built and a dashed line when unbuilt. That is the direct cause of the owner's square-box observation: built-wall appearance does not consume believable wall height, material, gate/corner/segment art or depth.

**Executor:** do not certify a stroke as a finished wall. Review the existing wall assets in `assets/production/production-04-20261003/images/05-walls-stone.png` and the corresponding eight-age candidates before purchasing replacements. Use correctly registered, period-appropriate wall/palisade segments with visible height, thickness, corners/end caps, a believable gate, connected joins, ground contact, lighting/shadows and correct depth/occlusion. Follow a reviewed settlement boundary consistent with plots, road and gate, rather than exposing a generic site bounding box. Do not move legal path cells or silently invalidate old saves to fit the art. If a contract genuinely prevents a valid composition, record the precise versioned proposal and keep that gate open.

At Walls 0, a completed physical perimeter must not be painted as if built. An optional construction preview is explicit and temporary. Building/upgrade states must visibly change the actual wall while preserving costs and defense effects. The age/level appearance must be reviewed at normal camera scale and phone size, not only in an isolated sprite sheet.

### Art and scene continuity

The original is a reference for game-like composition and integrated scene cues, **not permission to copy old executable code, revive cartoon art, use its portrait layout, or bake a completed city behind hotspots**. Independently author the new implementation. Keep the reborn landscape requirement and one coherent semi-realistic/realistic treatment, with truthful state-driven terrain/buildings/actors/walls/equipment and matched materials/light/perspective.

## Required visual acceptance for the other AI

1. Ordinary Home/Kingdom/Adventure/battle/Hero/Forge screens immediately read as distinct game places, with a dominant world/subject and intentional compact UI; no generic card dashboard passes as final art direction.
2. Normal Kingdom with inspectors dismissed meets the existing at-least-80% unoccluded-world goal with useful scene scale; large blank letterbox regions or a tiny city do not count as world prominence.
3. Stone sparse start looks deliberately composed and inhabited at a modest scale while retaining all 17 unbuilt sites and correct state. No permanent bright plot grid, invented functional starting facilities or fake paid completion.
4. Walls 0 / building / built / upgraded and at least representative early/later ages have actual material/depth/gate/contact evidence. No square outline masquerades as built masonry/palisade.
5. Direct world selection, contextual cancel/confirm, concise cost feedback, focus and return work with adequate real touch targets. Accessibility does not require crowding the main scene with every action.
6. Healer, other figures, terrain, architecture, equipment, effects and final rendering agree in anatomy/material/light/camera/style. Worn gear and the selected hero identity are consistent.
7. Supply labelled actual runtime comparisons with the approved mocks and relevant original-game visual references, asserting source/view/age/state/viewport. Compare native and intended phone size, inspector closed/open, construction and motion extremes. Do not call filenames, tests or self-written PASS text visual acceptance.
8. Complete the required game and final candidate; return for independent verification. Owner final review and the authorized later device sequence follow real desktop completion. No interim approval loop is introduced. Independent ready mechanics/persistence work continues while art is being repaired.

**Priority:** game-like world composition, natural Stone plots and physical walls are first-order acceptance failures. They must be addressed together with the scene registration, synchronized style, Healer, worn-gear and animation findings—not deferred behind another test-count/completion announcement.
