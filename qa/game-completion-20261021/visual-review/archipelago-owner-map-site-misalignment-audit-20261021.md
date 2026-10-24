# Archipelago owner-map prebinding audit — 21 October 2026

**Classification: FAIL for current site/bridge registration against the owner painting; runtime owner binding is absent. Several landmark semantics and safe approaches remain OPEN.** This is a source-grid and raw-pixel review, not evidence from live owner-map play.

## Evidence and current state

The source is assets/mocks/owner-approved-vast-adventure-maps-20261020/07_Vast_Map_Tropical_Archipelago_Monsoon.png (SHA256 01533C4DD285C7F624B7D8E756CDD353B48C6EB3FAEC510824147251EFDA1AF6). It was inspected beside its generated 16×10 coordinate grid at qa/game-completion-20261021/visual-review/owner-map-source-grid-audit-20261021/archipelago-owner-source-16x10-grid.png.

The current diagnostic report says runtimeFile is null, runtimeMatchesOwner is false, 38 cells are blocked, and bridgeDefinitions is empty. The live runtime therefore still uses the generated Archipelago map. Any existing natural route on that map does not verify this owner painting's sites, crossings, or fidelity.

## Site alignment findings

| Site | Current registration | Raw-pixel observation | Finding |
|---|---|---|---|
| Town | rect [8,5,3,2], approach [7,5] | The footprint sits over open water and a ship. The owner painting has island settlements, including a central fortified city and beach/port neighborhoods. | FAIL |
| Mill | rect [13,5,2,2], approach [12,5] | The footprint is on the volcanic island near a dragon and lava, not the visible windmills on the lower-left island. | FAIL |
| Shrine | rect [0,5,2,2], approach [2,5] | The footprint covers a windmill. The intended shrine among the island altars, crystal formations, and other magical landmarks is unresolved. | FAIL / role unresolved |
| Mine | rect [2,3,2,2], approach [4,3] | This footprint appears to cover red crystal and mining-cart art. | Candidate alignment; approach and interaction still need verification |
| Dwelling | rect [6,1,2,2], approach [8,3] | This footprint covers a small settlement on a northern island. | Candidate alignment; route and interaction still need verification |
| Ruin | rect [8,0,2,2], approach [8,2] | The footprint covers a small tower/islet area; confirm that this is the intended ruin rather than another settlement. | Role unresolved |

The owner image visibly joins islands with stone and timber bridges/causeways. The source-grid data has 38 blocked cells but zero bridge definitions. Trace every visible deck, adjacent safe bank, water cell, and approach together so the water mask does not seal islands or leave arbitrary water traversable. Preserve source composition, avoid placing the hero or interaction hotspot on the ship/water, and check reachability from the actual start.

## Required repair and verification route

1. Reconcile the six site semantics with the owner painting. Replace the failed Town, Mill, and Shrine placements with bounded footprints on confirmed landmarks and safe walkable approaches; verify the candidate Mine and Dwelling before retaining them.
2. Trace each inter-island bridge/causeway and water blocker on the 16×10 grid. Register walkable deck cells and both banks, then prove routes through every crossing without changing the painting's legal geometry.
3. Bind runtimeFile only after the sites, bridges, blockers, start, and dynamic anchors agree with source pixels. Keep the generated map available for comparison and preserve the original painting.
4. In a later authorized implementation/verification pass, use visible controls to visit all sites, cross every registered bridge, and save/reload the position, movement, discoveries, and rewards. Inspect actual rendered pixels at required desktop and compact viewports.

See the [cross-world crossing screen](owner-map-unbound-crossing-screen-20261021.md). Whole-game status remains INCOMPLETE.

