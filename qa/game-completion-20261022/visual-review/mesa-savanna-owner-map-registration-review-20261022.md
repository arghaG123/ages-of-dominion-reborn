# Mesa Savanna owner-map registration and natural journey review — 22 October 2026

**Status: bounded Adventure source, route, interaction, and persistence pass. Red Mesa Frontier and the whole game remain INCOMPLETE.**

The runtime now selects the approved Mesa Savanna painting with source-grid site regions, four painted rope bridges, and two canyon channels. A fresh natural browser journey crossed every registered deck, interacted with the Shrine, Ruin, Mill, Mine, and Dwelling, returned to Town, re-entered Adventure, and reloaded. Runtime owner-painting bindings are 10 of 12 (83.3% of that binding task), not a whole-game completion percentage. The repository has no defensible weighted whole-game percentage.

## Source registration

- Owner painting: `assets/mocks/owner-approved-vast-adventure-maps-20261020/08_Vast_Map_Highland_Mesa_Canyon_Savanna.png`
- SHA-256: `70ffbaafe7bc62453b1379d9d403ae4a82db8b2a2bab11bcc7d8262dfe7c0441`
- Native dimensions: 1376×768; 16×10 cells; source transform is 86×76.8 pixels per cell.
- `runtimeFile` selects the same file as `file`; the integrated renderer preserves the painted crossings and adds live travel and interaction layers.
- Geometry registers 39 canyon-channel cells, four rope bridge decks, and six site areas.

The [candidate registration overlay](mesa-savanna-owner-map-candidate-registration-grid-20261022.png) was compared against the source painting and live captures. These landmark-role assignments are verifier judgments, not owner approval.

| Site | Registered footprint | Approach | Source reading |
|---|---:|---:|---|
| Town | [6,0,4,3] | [6,3] | Central elephant fortress |
| Ruin | [11,7,1,2] | [12,7] | Red obelisk and surrounding works |
| Mill | [9,8,1,2] | [8,8] | Lower windmill beside the stream |
| Mine | [0,2,1,2] | [1,3] | Western gold mine |
| Dwelling | [13,6,2,2] | [12,6] | Eastern settlement |
| Shrine | [6,7,2,2] | [6,6] | Glowing crystal pool |

Crossing registrations:

- West north rope bridge: deck [2,3], [3,3], [4,3]; approaches [1,3], [5,3].
- West south rope bridge: deck [2,6], [3,6], [4,6]; approaches [1,6], [5,6].
- East north rope bridge: deck [9,3], [10,3], [11,3], [12,3]; approaches [8,3], [13,3].
- East south rope bridge: deck [9,6], [10,6], [11,6]; approaches [8,6], [12,6].

The eastern south-bank approach at [12,6] remains walkable. Including that cell in the water mask blocked the Dwelling approach and made seeded layout generation search impossible placements; the corrected mask preserves the illustrated channel while keeping the bridge bank and Dwelling reachable.

## Verification

- `node --test --test-name-pattern='Mesa Savanna' tests/adventure-worlds.test.mjs`: 2/2 passed.
- `node --test tests/*.test.mjs`: 256/256 passed on the resulting source snapshot. This is bounded Node evidence.
- Route tests verify all four full decks, orthogonal deck entry, source dimensions, site entrances, and guard-free itineraries in all twenty deterministic layouts.
- Fresh natural run01 used seed `3583177659` (`mesa-savanna-layout-11`). It started at Town (6,3), crossed west north to (1,3), west south to (5,6), east north to (13,3), and east south to (12,6). It learned a Shrine skill, claimed Ruin XP, Mill food, Mine gold, and the Dwelling creature offer. It then returned to Town, re-entered, and reloaded at (6,3), retaining all bridge discoveries, four Adventure claims, the dwelling purchase, and the same campaign. Eighteen End Day actions; browser errors and 404 responses: zero. See [run01 report](adventure-mesa-savanna-owner-map-natural-live-20261022-run01/report.json), [runner](adventure-mesa-savanna-owner-map-natural-live-20261022.mjs), and [captures](adventure-mesa-savanna-owner-map-natural-live-20261022-run01/).

## Open acceptance

At 825×375 and 933×424, the hero-following map extends about 85.5 and 96.7 pixels below the viewport. The bottom painting is cropped without page overflow. The screenshot evidence is in the [run01 report](adventure-mesa-savanna-owner-map-natural-live-20261022-run01/report.json); full composition and compact-layout acceptance remain open. The owner-art landmark roles have not received separate owner review. Astral Peaks and Blood Moon remain unbound. Other Adventure maps, mock-led screens and journeys, independent desktop acceptance, final snapshot package, later device QA, and owner review also remain open.

No APK, device, provider, Git, or cleanup action was performed.
