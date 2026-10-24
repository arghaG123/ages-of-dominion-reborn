# Feywild owner-map registration and live route review — 21 October 2026

**Classification: bounded source-registration and natural-browser PASS. Adventure and the whole game remain INCOMPLETE.** Two of 12 campaign worlds now select their owner painting in live play: Grasslands and Feywild. This review closes only the Feywild source binding, registered crossing travel, one mine reward, one skill-monument reward, and bounded reload persistence.

## Source registration

The Feywild record in src/data/adventure-worlds.json selects the matching owner painting through runtimeFile. The live renderer reports:

- source: assets/mocks/owner-approved-vast-adventure-maps-20261020/06_Vast_Map_Sylvan_Cherry_Blossom_Feywild.png
- registration: owner-registered-world-coordinate-layers-v1
- render model: integrated-map-art-plus-live-interactions
- bridges and playable crossings: 2 and 2

The hand-traced 16×10 registration uses worldToSource [86, 0, 0, 76.8, 0, 0]. It registers the upper stone arch bridge at [3,3], the lower footbridge at [2,6] and [3,6], water masks, blocked sky/tree-canopy cells, and six source-aligned places. The town, mine, dwelling, mill, ruin, and obelisk shrine each have a distinct footprint and approach. The grid overlay and source report are in [the owner-map source-grid audit](owner-map-source-grid-audit-20261021/report.json) and [Feywild grid image](owner-map-source-grid-audit-20261021/feywild-owner-source-16x10-grid.png).

## Isolated visible-control journey

A fresh browser origin at http://127.0.0.1:4197/ was used for this test campaign. At 1280×720, the visible flow selected Sylvan Feywild, entered the valley, reached and studied the shrine, and received First Aid 1/3. The Hero skill screen confirmed First Aid rank 1/3.

The journey crossed both registered bridges using route preview and confirmation: the lower route from [4,6] to [1,6] cost three steps across deck cells [3,6] and [2,6]; the upper route from [2,3] to [4,3] cost two steps across [3,3]. At the mine approach, Recover gold added 225 gold. After Save and reload, the campaign still showed three moves and 375 gold; the shrine lesson and explored mine were retained. The map element still reported the Feywild owner source and both crossings. Console error and warning logs were empty.

At 825×375, the landscape map and status card fit the stage. The travel panel scrolls to its lower actions and explanatory copy. The source painting is substantially dimmed by fog, so terrain readability and full mock fidelity remain open. The live screenshots were reviewed in-browser but were not saved as image files.

## Verification

- Focused Adventure and responsive Node suites: 38/38 passed.
- Full bounded Node suite, node --test tests/*.test.mjs: 248/248 passed, including the bounded save-stress case.
- node --check passed for src/client/main.js and src/core/navigation.js.
- The 12-world data file parses; exactly Grasslands and Feywild have runtimeFile equal to their owner file.

These results do not establish all-world visual fidelity, all natural journeys, independent desktop acceptance, final APK parity, device QA, or owner acceptance. Ten owner maps remain unbound to their owner paintings. Kingdom art, walls, actors, scenes, wearables, and the remaining whole-game acceptance leaves are still open.
## Independent source-pixel and saved-viewport recheck — 21 October 2026

I reopened the current owner painting and its registered 16×10 overlay. The current source image hash is SHA256 A1BB9CA33CB2C21F9BF951FAA22EFB94CB24D868EE10F851ED1AF90160985C16. The source-grid coordinates put Town [7,3,3,2] over the central white settlement and road, Mine [2,2,1,1] over the western mine works, Dwelling [10,1,3,3] over the great tree settlement, Mill [12,7,2,2] over the lower-right windmills, and Shrine [8,7,1,1] over the central obelisk. Ruin [7,7,1,1] covers the small stone landmark beside the obelisk. Both registered bridge regions ([3,3] and [2,6]–[3,6]) align with the visible waterfall arch and lower footbridge. This is a bounded source-pixel alignment check, not all-site natural-journey acceptance.

I also opened the saved 825×375 far-bank capture from `adventure-feywild-footbridge-natural-live-20261021-run04`. Its report identifies a fresh visible-control crossing campaign, with no recorded browser errors or failed responses; the capture SHA256 is 813BFFB4B6345A0F3A4719B5923B81C5A5D15D7A844E6721BA4039609BB4EEB8. The runtime screen strongly darkens most of the owner painting under fog, leaving only a limited area readable at this viewport. The screenshot report does not bind its run to the current owner-image hash, so exact capture-to-source identity remains unverified. Keep fog/readability and overall mock composition OPEN. No production source or test was changed or run for this recheck.