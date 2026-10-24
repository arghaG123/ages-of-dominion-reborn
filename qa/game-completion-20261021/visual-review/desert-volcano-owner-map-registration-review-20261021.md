# Desert Volcano owner-map registration and natural journey review — 21 October 2026

**Status: bounded Adventure source, route, interaction, and persistence pass. Desert Volcano and the whole game remain INCOMPLETE.**

This work binds the Desert Volcano campaign world to its approved owner painting, traces two visible bridge decks, distinguishes oasis water from volcanic obstacles, and verifies one full natural journey. It raises runtime owner-painting bindings to 7 of 12 (58.3% of that binding task). The repository has no defensible weighted whole-game completion percentage; this map count does not estimate it.

## Source registration

- Owner painting: `assets/mocks/owner-approved-vast-adventure-maps-20261020/04_Vast_Map_Desert_Volcanic_Sandstorm.png`
- SHA-256: `5c37a730955356dacc8997011af3778105e0d041ab9f056b761583e7a4c3887f`
- Native dimensions: 1376×768; 16×10 cells; source transform is 86×76.8 pixels per cell.
- `runtimeFile` now selects the same owner file as `file`; the integrated renderer uses this source with live movement and interaction layers.
- Map feature registration describes isolated oasis pools, two playable crossings, and lava/sulfur hazards.

The visual grid overlay is [desert-volcano-owner-map-registration-grid-20261021.png](desert-volcano-owner-map-registration-grid-20261021.png). It places the two upper/lower oasis pools in the blocked mask, fourteen fissure/vent cells in the obstacle mask, and the six site rectangles and approaches over the mapped landmarks.

| Site | Registered footprint | Approach | Source reading |
|---|---:|---:|---|
| Town | [7,4,2,2] | [7,6] | Central golden capital |
| Shrine | [2,0,2,2] | [3,2] | Stepped pyramid |
| Ruin | [8,7,1,1] | [8,6] | Cyan runed obelisk |
| Mill | [6,7,1,1] | [7,7] | Windmill |
| Mine | [0,3,2,2] | [2,4] | Gold mine and quarry works |
| Dwelling | [5,5,2,2] | [5,4] | Western oasis tent cluster; this role assignment is plausible, not owner-approved |

Crossing registrations:

- West canyon arch: deck cells [1,2] and [2,2], approached from [1,1] and [3,2].
- East lava/dragon bridge: deck cells [10,7] and [11,7], approached from [9,7] and [12,7].

## Verification

- `node --test tests/adventure-worlds.test.mjs`: 19/19 passed after the source edit.
- `node --test tests/*.test.mjs`: 252/252 passed on the resulting source snapshot. This is bounded Node evidence.
- The full suite exercised twenty deterministic reachable resource/guard layouts for every campaign world.
- Fresh ordinary browser run02 crossed both complete bridges, visited all six sites, claimed the Shrine lesson, Ruin XP, Mill food, Mine gold, and one fixed creature dwelling offer, then returned to Town, re-entered Adventure, and reloaded. Position, bridge discoveries, four Adventure site claims, dwelling purchase, and campaign identity persisted.
- Fresh ordinary browser run03 repeated that journey on another generated layout and added captures at 825×375 and 933×424. Browser errors and 404 responses were zero. See [run03 report](adventure-desert-volcano-owner-map-natural-live-20261021-run03/report.json), [script](adventure-desert-volcano-owner-map-natural-live-20261021.mjs), and [compact captures](adventure-desert-volcano-owner-map-natural-live-20261021-run03/).
- Run01 initially stopped on a verifier assumption that dwelling recruitment appears in `adventure.claimedSites`; the campaign stores the dwelling purchase separately. The corrected verifier checks that dedicated state; run02 and run03 passed.

## Open acceptance

At 825×375 and 933×424, the hero-following camera fills the wide viewport and crops the map vertically; it does not expose page overflow. Those captures verify the layout and visible interaction layer, not the whole painted composition. Full source readability/fog/hazard review, all-seed natural play, semantic owner approval for the dwelling landmark, and complete Desert map acceptance remain open. Other Adventure maps, required mock-led screens and journeys, independent desktop acceptance, final snapshot package, later device QA, and owner review also remain open.

No APK, device, provider, Git, or cleanup action was performed.
