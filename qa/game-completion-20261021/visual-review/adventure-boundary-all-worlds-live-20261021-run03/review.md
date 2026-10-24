# Adventure north-edge traveler framing — 21 October 2026

**Current-source bounded PASS; full Adventure and game remain INCOMPLETE.** The compact all-world boundary run exposed one remaining clipping case: Archipelago's mounted traveler was 10.8px above the viewport on row 1; row-0-only safety did not protect the preceding border-adjacent cell.

## Repair

`src/client/main.js` now activates the north-edge terrain backdrop and the existing 128px camera safety offset for map rows 0 and 1. This keeps the mount and rider visible before the hero reaches the top border while the stage background fills the uncovered map margin. Added a focused responsive-source regression for the row threshold and backdrop.

## Current-source journey evidence

Twelve fresh isolated browser contexts began a new Stone Age campaign in each Adventure world. Each journey selected a reachable, guard-free border cell through a read-only path search, then previewed and committed every cardinal move through visible game controls. Saved world, edge position, and explored cells were checked after reload.

At 825×375, the browser measured the mount and actor SVG boxes on every route step. All 12 journeys passed; all 12 actor-bound checks passed; all 12 reloads matched the destination; frame or terrain-backdrop coverage held for every step. Browser errors and failed responses: 0. The actor-bound check is only a viewport-containment measurement; it does not grant overall mock, art, or owner acceptance. The full contact sheet is `adventure-boundary-all-worlds-live-20261021-run03/all-12-outer-edge-traveler-bounds-contact.jpg`; per-world captures and reports are in the corresponding `adventure-boundary-<world>-live-20261021-run03/` folders. The aggregate records SHA256 for the source and runner.

Focused `tests/visual-responsive-20261018.test.mjs`: 20/20. Full `node --test tests/*.test.mjs`: 240/240. `node --check src/client/main.js`: pass.

## Limits and continuation

All twelve fresh campaigns began in Stone Age; these results do not verify mounted bounds for later-age mounts or other classes. They also do not close the M11/M12 visual composition, ordinary non-edge travel, remaining Adventure interactions, all 30 mock screens, full natural journeys, independent desktop acceptance, final package, device, or owner review. Keep those gates separate and the whole game INCOMPLETE.
