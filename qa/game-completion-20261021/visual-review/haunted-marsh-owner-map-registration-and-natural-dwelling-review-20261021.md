# Haunted Marsh owner map registration and natural Dwelling journey — 21 October 2026

## Current bounded result

The live Haunted Marsh runtime now selects the owner-approved autumn marsh painting. Its SHA-256 is `52A11BACB9944E2A240A49E795B19B6FE20732CE66F8E3BC49C8D31F4B581429`. The 16×10 source transform is `[86, 0, 0, 76.8, 0, 0]`; the current registration contains six site footprints/approaches, two road traces, 25 blocked cells, and three bridge definitions. The registered crossings are the west footbridge at `[5,3]`, central stone bridge at `[8,3]–[9,3]`, and east stone bridge at `[13,6]`.

A fresh isolated browser journey (`run16`) used visible controls from a new Stone Age campaign, built a Barracks, previewed and canceled a route without consuming movement, and traveled from the Town approach to the Dwelling approach. The report records one day transition and nine committed movement points. At the Dwelling, the player opened the fixed five-Dire-Wolf offer (40 food, 35 gold), backed out and reopened it, reloaded with the same offer, claimed it once, and reloaded with the five-unit roster stack and payment persisted. Quest Q3 became ready and its 200-food/150-gold reward was claimed once; a second reload did not pay again. The journey completed with zero browser errors and zero failed responses.

The run captured 825×375, 933×424, and 1280×720 views. Reviewed captures show the owner painting in the Adventure scene, the dwelling label on the wide view, and the fixed offer reachable on the compact panel. Fog still makes much of the storm painting dark, and the compact camera focuses on only part of the world.

The focused current-source command `node --test tests/screen-presentation.test.mjs tests/adventure-worlds.test.mjs` passed 36/36 tests, including 20 deterministic reachable layouts for each world and the Haunted Marsh registration assertions.

## Limits and remaining work

This proves one natural Dwelling interaction and its persistence path on the owner painting. It does not independently close the source-to-art identity of all six landmarks, full water/hazard classification, or natural traversal of each of the three registered crossings. It does not close the other Adventure worlds, all-age journeys, required mock fidelity, full desktop acceptance, final package, mobile/device QA, or owner acceptance. The Adventure and whole game remain **INCOMPLETE**.

Earlier 21 October Haunted Marsh prebinding audits describe the state before the owner painting was bound and before roads, crossings, and site coordinates were added. Preserve them as historical evidence; this review is the current bounded update, not a claim that all earlier findings or full-game gates are closed.

## Evidence

- Current source registration: `src/data/adventure-worlds.json`, world `haunted-marsh`.
- Natural journey report and captures: `qa/game-completion-20261021/visual-review/adventure-haunted-marsh-dwelling-natural-live-20261021-run16/`.
- Previous prebinding audit (historical): `qa/game-completion-20261021/visual-review/haunted-marsh-owner-map-site-crossing-audit-20261021.md`.
