# Grasslands bridge navigation repair review — 21 October 2026

**Result: bounded current-source pass; whole Adventure and game remain INCOMPLETE.**

## Change

Compared the registered Grasslands geometry with a labeled 16×10 overlay of `assets/derivatives/adventure-world-maps-generated-20261020/grasslands-adventure-v1.png`. Restored the first world's `[86, 0, 0, 76.8, 0, 0]` transform after correcting an interrupted edit, retained the 28-cell traced water mask, and registered west watermill, central stone, and east stone crossing cells. The town collision rectangle is now `[6, 0, 5, 2]`, leaving the central gate row available to the bridge. Seeded resource/guard layouts now use deterministic backtracking through hash-ranked candidates; this keeps six unique, reachable anchors separated by at least three cells across all twenty variants.

The map image itself is unchanged. No fog opacity, terrain, route art, source registration, or other world was changed in this repair.

## Verification

- `node --check src/core/navigation.js`: PASS.
- `node --test tests/adventure-worlds.test.mjs`: 11/11 PASS, including the new Grasslands regression and all twenty layouts for every world.
- `node --test tests/*.test.mjs`: 238/238 PASS. The suite includes the bounded 10,000-command save-stress horizon; this remains automated test evidence.
- In the isolated `http://localhost:4179/` campaign, first canceled a preview at 5 moves, then separately confirmed a current-source route from `(8,3)` to `(6,2)`. Its visible path followed `(8,3) → (8,2) → (7,2) → (6,2)` across the registered central bridge; it cost 3 moves and left 2. After the travel animation and save completed, reload plus Continue retained the hero at `(6,2)` with 2 moves. The original `127.0.0.1` save was not opened. Post-reload page console error/warning query returned none.
- Reviewed the integrated map and live Adventure view at 1280×720. The unvisited terrain remains dark under the existing fog treatment; fog readability and full M11/M12 visual acceptance remain open. Screenshots were inspected live and not saved as files.

## Scope still open

This closes only the Grasslands water-mask / bridge-connectivity slice and the seeded-layout regression it exposed. Other-world source registration, full map and route fidelity, fog readability, grounded mounted crossing motion, remaining natural journeys and mock comparisons, independent desktop acceptance, the final APK, later device QA, and owner review remain distinct open gates. Product acceptance remains INCOMPLETE.
