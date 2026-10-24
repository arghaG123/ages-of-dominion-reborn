# Sunken Jungle owner-map registration and natural journey review — 21 October 2026

**Status: bounded Adventure source, route, interaction, and persistence pass. Sunken Jungle and the whole game remain INCOMPLETE.**

This work binds Sunken Jungle to its approved painting, traces four playable crossings, six site areas, waterfall channels, and the southeast lava pit, then verifies one natural journey through the live UI. Runtime owner-painting bindings are now 8 of 12 (66.7% of that binding task). There is no defensible weighted whole-game completion percentage; the map count does not estimate it.

## Source registration

- Owner painting: `assets/mocks/owner-approved-vast-adventure-maps-20261020/12_Vast_Map_Sunken_Jungle_Ruins_Ziggurat.png`
- SHA-256: `6887fada0efd62f73d473d122d44b1adb6c5e0de287efa4d1300b21d2f3c1fbd`
- Native dimensions: 1376×768; 16×10 cells; source transform is 86×76.8 pixels per cell.
- `runtimeFile` selects the same painting as `file`; the integrated renderer layers movement, fog, actors, and interactions over it.
- Geometry registers 36 water-channel cells, five southeast lava obstacle cells, four crossings, and six site footprints. Bridge decks override the water mask so the crossings stay walkable.

The [candidate registration overlay](sunken-jungle-owner-map-candidate-registration-grid-20261021.png) was compared with the source painting and live screenshots. It maps the golden ziggurat, mine works, floating book altar, stilt village, east-cliff windmills, and green rune obelisk to the corresponding interaction regions. These role assignments are source-based verifier judgments, not owner approval.

| Site | Registered footprint | Approach | Source reading |
|---|---:|---:|---|
| Town | [8,0,4,3] | [8,4] | Golden ziggurat and south stair entrance |
| Ruin | [9,7,1,1] | [8,7] | Green runic obelisk |
| Mill | [13,1,3,2] | [13,3] | East-cliff windmills |
| Mine | [0,3,2,2] | [2,5] | Western gold mine and quarry |
| Dwelling | [7,5,3,2] | [7,4] | Central stilt-village cluster |
| Shrine | [4,2,1,1] | [4,3] | Floating spellbook altar |

Crossing registrations:

- West rope bridge: deck [3,4], [4,4]; approaches [3,5], [5,4]. The western bank at [3,5] is open ground, not blocked channel.
- Central stone causeway: deck [4,6], [5,6], [5,7], [6,7], [7,7]; approaches [3,6], [8,7].
- East timber bridge: deck [10,5], [11,5], [11,6], [12,6]; approaches [10,4], [13,6].
- Southeast rope bridge: deck [11,8], [12,8]; approaches [10,8], [13,8].

## Verification

- `node --test tests/adventure-worlds.test.mjs`: 19/19 passed after the source edit.
- `node --test tests/*.test.mjs`: 252/252 passed on the resulting source snapshot. This is bounded Node evidence.
- The suite exercised twenty deterministic resource/guard layouts for each of the twelve campaign worlds.
- Fresh natural browser run01 started a new campaign, built a Barracks, entered Sunken Jungle, crossed every full registered deck through visible adjacent-cell movement, visited all six site regions, and used the Shrine, Ruin, Mill, Mine, and Dwelling interactions. It returned from the Town approach, re-entered the map, and reloaded with the same campaign, position, bridge discoveries, site claims, and dwelling purchase. Browser errors and 404 responses: zero. See [run report](adventure-sunken-jungle-owner-map-natural-live-20261021-run01/report.json), [runner](adventure-sunken-jungle-owner-map-natural-live-20261021.mjs), and [captures](adventure-sunken-jungle-owner-map-natural-live-20261021-run01/).
- The run used ordinary campaign seed `2327855614` and selected `sunken-jungle-layout-9`. All four bridge decks were visited in the persisted movement history.

## Open acceptance

At 825×375 and 933×424, the hero-following world field extends about 85.5 and 96.7 pixels below the viewport, respectively. The screenshots show the lower map clipped without page overflow. They verify responsive rendering and interaction placement, not the complete painted composition. Full source/fog/hazard readability, semantic owner approval, other natural seeds, and complete Sunken Jungle acceptance remain open. Other Adventure maps, required mock-led screens and journeys, independent desktop acceptance, final snapshot package, later device QA, and owner review also remain open.

No APK, device, provider, Git, or cleanup action was performed.
