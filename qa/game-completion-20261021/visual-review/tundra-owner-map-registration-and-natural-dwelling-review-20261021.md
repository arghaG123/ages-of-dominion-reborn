# Tundra owner-map registration and natural Dwelling journey — 21 October 2026

## Result

The runtime now selects the approved Tundra painting, with a 16×10 source transform, six source-aligned site regions, frozen-channel cells, three crossing definitions, and road traces. A fresh isolated browser journey reached the Dwelling through visible UI controls, claimed the saved Dire Wolf offer and its linked Q3 reward once, and retained the payment and five-unit stack after reload. This is bounded Adventure evidence; the map and whole game remain INCOMPLETE.

- Owner painting: `assets/mocks/owner-approved-vast-adventure-maps-20261020/02_Vast_Map_Glacial_Tundra_Blizzard.png`
- Owner painting SHA-256: `C45AE88FAB2F321840B1C1C9761ED1FB7EA13269945BC652376B9D3E6DB56114`
- Current `src/data/adventure-worlds.json` SHA-256: `2652112E756915DBC284E6FB3956C8D574D7026F196EBD91D4A9DF44FBCE3FA3`
- Runtime owner-map bindings: 6/12 (Grasslands, Tundra, Haunted Marsh, Underworld, Feywild, Jade Karst). This is an integration count, not a whole-game completion percentage.

## Source registration

The Tundra entry uses `[86, 0, 0, 76.8, 0, 0]` for `worldToSource`. It registers 10 blocked frozen-channel cells, 23 edge/landform obstacle cells, three road traces, and these crossing decks:

- West stone bridge: cells `(6,6)` and `(7,6)`, approached from `(5,6)` and `(8,6)`.
- East ice-channel bridge: cells `(12,4)` and `(13,4)`, approached from `(11,4)` and `(14,4)`.
- South channel bridge: cell `(9,8)`, approached from `(8,8)` and `(10,8)`.

The six registered sites are Town `(1,3,3,2)`, Ruin `(7,1,3,3)`, Mill `(3,6,1,1)`, Mine `(0,5,2,2)`, Dwelling `(5,2,2,2)`, and Shrine `(7,7,1,1)`, each with a legal approach in the source grid. Independent inspection of the 16×10 overlay found these regions plausibly aligned with the painted domed settlement, citadel, waterwheel, mine works, tents, and blue altar. This is source-coordinate review, not owner approval.

## Natural journey and checks

Fresh isolated run [run03](adventure-tundra-dwelling-natural-live-20261021-run03/report.json) used seed-selected layout `tundra-layout-3`. It started at `(3,5)` and naturally traveled to Dwelling approach `(7,4)` over a route costing 11 movement points. The UI exposed and canceled the full route preview without changing state; the journey then committed each adjacent visible step, ended two days through the Adventure panel, and spent exactly 11 movement points. No guard encounter was bypassed.

At the site, the on-foot Knight and Dwelling interaction were present. The fixed five-Dire-Wolf offer survived leaving/reopening the panel and reload. Claiming it deducted 40 food and 35 gold once, added one five-unit stack, and made Q3 ready. The Q3 reward was claimed once; a second reload retained the claimed offer, creature stack, resources, and reward history. The journey recorded 11 screenshots across 825×375, 933×424, and 1280×720, with zero browser errors and zero missing responses. I visually reviewed the on-foot captures at all three sizes and the 825×375 Dwelling context panel; the composition and interaction remain legible at those sizes.

Focused command `node --test tests/adventure-worlds.test.mjs tests/screen-presentation.test.mjs`: 37/37 passed. The full `node --test tests/*.test.mjs` suite also passed 252/252, including the bounded save-stress test. These are source/test results, not visual or whole-game acceptance.

## Natural full bridge crossings

Fresh run [crossing run02](adventure-tundra-natural-bridge-crossings-live-20261021-run02/report.json) used an ordinary newly created campaign and its naturally assigned seed `2109135227` (`tundra-layout-20`). Visible adjacent-cell controls took the Knight across the west stone bridge from `(5,6)` to `(8,6)`, the east ice-channel bridge from `(11,4)` to `(14,4)`, and the south channel bridge from `(8,8)` to `(10,8)`. Every deck cell was individually committed and saved in `adventure.visited`. The route ended after six end-day actions; no guard shortcut, console error, or missing response occurred. Reload restored the same campaign at `(10,8)` with all three decks still discovered.

The owner painting is marked as `integrated-map-art-plus-live-interactions`; its bridge art is already part of the selected source image. The initial crossing-run assertion incorrectly expected separate generic bridge sprites, which the integrated renderer suppresses to avoid duplicate stamps. That verifier-only failure is retained as run01; run02 instead checked the live world/source binding and verified each painted bridge through full natural movement. Captures after each crossing were visually reviewed at 1280×720 and aligned with the painted west, east, and south bridges.

## Remaining site interactions and map-cell hit testing

Fresh run [run04](adventure-tundra-natural-bridge-crossings-live-20261021-run04/report.json) repeated the three natural bridge crossings, then visited the Shrine, Ruin, Mill, and Mine in the same ordinary campaign. It studied the Shrine and selected Leadership (rank 0→1), claimed 90 XP at the Ruin, collected the saved 115-food Mill offer, and recovered the saved 223-gold Mine offer. The claimed-site ledger, deck discoveries, and final Mine position `(2,6)` all survived reload. Nine end-day actions were used over the full route; browser errors and missing responses were both zero. The four post-claim 1280×720 captures were visually reviewed.

The first expanded run exposed a real cell-hit issue: the on-foot Knight SVG intercepted a click on the cell immediately ahead while leaving the Shrine. The UI now sets `pointer-events="none"` on the decorative on-foot actor group in `src/client/main.js`; it remains exposed as the accessible `Your hero on foot` image. Run04 asserted that property at each visited site and successfully committed the formerly intercepted move from `(8,7)` to `(8,6)`. The pre-fix run03 failure is retained as the finding; the corrected live journey is run04.

## Town return and re-entry

Fresh run [run05](adventure-tundra-natural-bridge-crossings-live-20261021-run05/report.json) repeated the bridge and four-site itinerary, then traveled from the Mine approach `(2,6)` to Town approach `(3,5)` through visible UI steps. The enabled Return to town control changed `adventure.atTown` to true and opened the Kingdom view. Re-entering Adventure restored the same map position, 30 visited cells, all four site claims, and the existing bridge discoveries. Reload retained the campaign and returned Adventure position `(3,5)`. There were zero browser errors or missing responses; the Town approach, returned Kingdom, and re-entered map captures were visually reviewed at 1280×720.

## Still open

- Independently finish the complete water, hazard, and edge-obstacle trace; the current mask is a bounded route candidate.
- Retain full owner review of site-to-landmark identity.
- Review the entire map against the owner composition and readability target at every required viewport; inspect fog and minimap behavior.
- Complete the other six owner-map bindings, all remaining mock and gameplay requirements, independent full-desktop acceptance, final package, later device QA, and owner review.

Tundra's live owner image, Dwelling journey, all three full bridge crossings, Shrine/Ruin/Mill/Mine interactions, and the Town return/re-entry loop now pass bounded checks. Tundra map acceptance, Adventure completion, release readiness, and whole-game acceptance remain OPEN.
