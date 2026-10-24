# Sunken Jungle owner-map prebinding audit — 21 October 2026

**Classification: FAIL for current site/bridge registration against the owner painting; runtime owner binding is absent. Semantic role assignment and full hazard/route tracing remain OPEN.** This is a source-grid and raw-pixel review, not evidence from live owner-map play.

## Evidence and current state

The source is assets/mocks/owner-approved-vast-adventure-maps-20261020/12_Vast_Map_Sunken_Jungle_Ruins_Ziggurat.png (1376×768, SHA256 6887FADA0EFD62F73D473D122D44B1ADB6C5E0DE287EFA4D1300B21D2F3C1FBD). It was inspected beside its generated 16×10 coordinate grid at qa/game-completion-20261021/visual-review/owner-map-source-grid-audit-20261021/sunken-jungle-owner-source-16x10-grid.png.

The current diagnostic report says runtimeFile is null, runtimeMatchesOwner is false, and the renderer uses the generated Sunken Jungle map. It records transform [86, 0, 0, 76.8, 0, 0], six sites, and zero bridge definitions. The recent natural dwelling offer/claim/reload run is therefore not owner-painting or source-registration evidence.

## Site alignment findings

| Site | Current registration | Raw-pixel observation | Finding |
|---|---|---|---|
| Town | rect [6,0,3,2], approach [8,2] | The rectangle covers northern canopy; the clear walled settlement is around columns 4–6, rows 3–4. | FAIL |
| Mine | rect [1,1,2,2], approach [3,2] | The rectangle covers waterfall/forest. Ore carts and gold-mining works are visible on the western edge. | FAIL |
| Dwelling | rect [8,3,2,2], approach [10,3] | The rectangle lands on the ziggurat's lower stair and the mounted hero; the stilt-house settlement is around columns 7–10, rows 5–6. | FAIL |
| Ruin | rect [1,3,2,2], approach [3,4] | The rectangle covers waterfall/river. The central ziggurat and lower circular arena are plausible ruin landmarks, but the intended role is not determined by this grid alone. | FAIL / role unresolved |
| Mill | rect [13,1,2,2], approach [12,2] | The footprint covers the upper-right windmills. | Candidate alignment; approach and interaction still need verification |
| Shrine | rect [11,3,2,2], approach [11,5] | The footprint touches the east side of the ziggurat. The floating book altar and blue crystal grotto are other plausible shrine landmarks. | Role unresolved |

The painting visibly includes several water crossings: a western rope bridge, a broad central stone bridge/causeway, and an eastern timber bridge. The current source-grid geometry registers no bridges. Before binding, identify each deck and both safe banks, register walkable deck cells separately from water blockers, and prove routes across them without shifting painted landmarks or allowing the hero to stand on hazards.

## Required repair and verification route

1. Reconcile all six site semantics with the owner image, then place bounded footprints over the chosen painted structures and select adjacent walkable approaches. Treat the coordinates in the current report as rejected where marked FAIL; do not copy them into a new runtime binding.
2. Trace the visible bridges, water, cliffs, ziggurat mass, arena, mining works, settlements, and actor-safe start on the 16×10 grid. Resolve overlaps and unreachable approaches from actual source pixels.
3. Bind runtimeFile only after site/bridge/hazard geometry is source-aligned. Keep the generated map available for comparison and preserve the original painting.
4. In a later authorized implementation/verification pass, check natural visible-control travel to all six sites and across every registered bridge, then save/reload discoveries, rewards, movement, and position. Review actual rendered pixels at the required desktop and compact viewports; source-grid and test evidence alone cannot close visual acceptance.

Whole-game status remains INCOMPLETE. No source, runtime, test, provider, build, device, Git, storage, or cleanup action was performed in this audit.

