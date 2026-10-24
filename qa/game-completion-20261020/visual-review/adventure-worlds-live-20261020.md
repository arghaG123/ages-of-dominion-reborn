# Owner-approved Adventure world integration — 20 October 2026

## Result

Implemented the owner's choice to make all 12 clean continental paintings selectable campaign worlds. The original gallery is preserved under `assets/mocks/owner-approved-vast-adventure-maps-20261020/`; all 40 copied source files have matching SHA256 hashes in `gallery-file-manifest.json`.

Each new campaign records one `adventureWorldId`. The world picker previews the selected painting and offers all 12 images with a name, realm, and biome. It asks before replacing a saved campaign and only writes the new state after confirmation. Legacy saves with no world choice migrate to the first clean world; an explicitly malformed value remains invalid. The selected painting remains tied to the campaign through age changes and reloads.

The Adventure scene now uses the selected 1376×768 painting. Its baked towns, roads, bridges, resource sites, and creatures remain visible without a second set of rendered site buildings. Existing route movement, fog, target handling, and save state remain active over the scene. The owner map backgrounds are included by the current static asset dependency collector.

The selected world name appears in the campaign gate and Adventure status/inspector. Live captures at 825×375 and 1280×720 were rechecked after this label change; the narrow inspector wraps the title within its panel without clipping.

## Verification

- `node --test tests/*.test.mjs`: **217 passed, 0 failed**, including 10,000-command save stress.
- `tests/adventure-worlds.test.mjs`: 12 IDs/files are unique and load as 1376×768 PNGs; selected IDs validate; unknown IDs reject; absent legacy IDs migrate; malformed present IDs do not silently repair.
- Live Chrome at **825×375, 933×424, and 1280×720**: all 12 map choices selected in each size, each image decoded at 1376×768, the panel and preview were visible, and there were zero page errors or failed HTTP responses.
- Live journey: selected Jade Karst, created a campaign, entered Adventure, committed one legal route move, waited for the durable save acknowledgement, then reloaded. The Jade map ID and selected image remained active. The live Adventure scene retained 160 movement hit cells and produced no duplicate building stamps.
- `scripts/asset-dependencies.mjs`: all **12** map images are in the runtime dependency set; **0 missing**.
- Source/pixel comparison: the 12-map geometry contact sheet was inspected for broad road, crossing, town, and site-footprint fit. The 12 live picker screens were inspected together.

## Visual evidence

- [All 12 live campaign-world pickers](adventure-worlds-live-20261020/all-12-campaign-worlds-contact.png)
- [All 12 source maps with current roads, crossing, and site geometry overlaid](owner-adventure-map-gallery-review-20261020/all-12-current-geometry-contact.png)
- [Jade Adventure at 825×375](adventure-worlds-live-20261020/adventure-825x375.png)
- [Jade Adventure at 1280×720](adventure-worlds-live-20261020/adventure-1280x720.png)
- Browser flow, dimensions, selected IDs, save acknowledgements, and error counts: [report.json](adventure-worlds-live-20261020/report.json)
- Repeatable browser review: [adventure-worlds-live-20261020.mjs](adventure-worlds-live-20261020.mjs)

## Acceptance boundary

The broad composition overlay looks consistent with the painted maps, and the live Jade scene was inspected at phone-landscape and desktop sizes. A full per-map audit of site collision edges, every site activation, and visual order during all 12 natural journeys remains open. This change does not close the broader M01–M30, J01–J18, 32-scene, independent desktop, final APK, device, or owner acceptance gates. Product status remains **INCOMPLETE**. No APK or device action was taken.
