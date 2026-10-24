# Archipelago owner-map registration and natural journey review — 22 October 2026

**Status: bounded Adventure source, route, interaction, and persistence pass. Stormbound Isles and the whole game remain INCOMPLETE.**

The runtime now selects the approved Archipelago painting with source-grid sites, two playable stone bridges, channel blockers, and volcanic obstacles. Two fresh natural browser journeys completed the bridge-and-site itinerary; run02 uses a direct Town-to-west-bank crossing. Runtime owner-painting bindings are 9 of 12 (75% of that binding task), not a whole-game completion percentage. The repository has no defensible weighted whole-game percentage.

## Source registration

- Owner painting: `assets/mocks/owner-approved-vast-adventure-maps-20261020/07_Vast_Map_Tropical_Archipelago_Monsoon.png`
- SHA-256: `01533c4dd285c7f624b7d8e756cdd353b48c6eb3faec510824147251efda1af6`
- Native dimensions: 1376×768; 16×10 cells; source transform is 86×76.8 pixels per cell.
- `runtimeFile` selects the same file as `file`; the integrated renderer preserves the painted bridges and adds live travel and interaction layers.
- Geometry registers 76 marine-channel cells, three volcanic obstacle cells, two playable bridge decks, and six site areas.

The [candidate registration overlay](archipelago-owner-map-candidate-registration-grid-20261022.png) was compared with the source painting and live captures. The Town region covers the central fortified city; the Ruin covers the northern tower islet; the Mill covers the lower-left windmill; the Mine covers the western mine works; the Dwelling covers the northern settlement; and the Shrine covers the stone altar on the western mainland. These role assignments are verifier judgments, not owner approval.

| Site | Registered footprint | Approach | Source reading |
|---|---:|---:|---|
| Town | [11,2,2,2] | [10,3] | Central fortified city and west gate |
| Ruin | [8,0,2,2] | [8,2] | Northern tower islet |
| Mill | [0,5,2,2] | [2,5] | Lower-left windmill island |
| Mine | [2,3,2,2] | [4,3] | Western mine and red crystal works |
| Dwelling | [6,1,2,2] | [7,3] | Northern island settlement |
| Shrine | [5,4,1,1] | [6,4] | Stone ring altar west of the Town bridge |

Crossing registrations:

- West stone bridge: deck [8,3], [9,3]; approaches [7,3], [10,3].
- Southeast stone bridge: deck [12,5], [13,5]; approaches [11,5], [14,5].

## Verification

- `node --test tests/adventure-worlds.test.mjs`: 21/21 passed after the source edit.
- `node --test tests/*.test.mjs`: 254/254 passed on the resulting source snapshot. This is bounded Node evidence.
- The new route regression exercises both complete crossings and all six site entrances in each of the twenty deterministic layouts without routing through a guard.
- Fresh ordinary live run02 used seed `2839038045` (`archipelago-layout-5`). It started at Town `(10,3)`, crossed the west bridge to `(7,3)`, traversed the southeast bridge to `(14,5)`, visited all six site regions, and used the Shrine, Ruin, Mill, Mine, and Dwelling interactions. Return to Town, map re-entry, and reload restored the same campaign and position with both bridge decks discovered, four Adventure claims, and the dwelling purchase preserved. Browser errors and 404 responses: zero. See [run02 report](adventure-archipelago-owner-map-natural-live-20261022-run02/report.json), [runner](adventure-archipelago-owner-map-natural-live-20261022.mjs), and [captures](adventure-archipelago-owner-map-natural-live-20261022-run02/).
- Run01 also completed the itinerary on `archipelago-layout-19`; its first bridge sequence was a full round trip from Town. The corrected runner now prefers the bank where the hero is already standing; run02 proves the direct crossing.

## Open acceptance

At 825×375 and 933×424, the hero-following map field extends about 85.5 and 96.7 pixels below the viewport, respectively. The lower painting is cropped without page overflow. This is responsive-layout evidence, not full composition acceptance. The image also darkens under Adventure fog. Full source/fog/readability review, semantic owner approval for the Ruin and Shrine roles, and map acceptance remain open. Other Adventure maps, required mock-led screens and journeys, independent desktop acceptance, final snapshot package, later device QA, and owner review also remain open.

No APK, device, provider, Git, or cleanup action was performed.
