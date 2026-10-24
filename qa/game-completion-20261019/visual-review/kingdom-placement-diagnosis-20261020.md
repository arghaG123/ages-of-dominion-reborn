# Kingdom building placement diagnosis — 20 October 2026

## Finding

The live Stone view combines two layers that can look tilted for different reasons. Many of the small settlement buildings are already painted into the currently selected terrain painting; the open-ground image is `assets/derivatives/kingdom-stone-family-20261018/stone-ground.png`. This is the image selected by `kingdomPainting()` in `src/client/kingdom-view.js`, not the older production terrain recorded in `src/data/stone-scene.json`. It shows the settlement from an elevated three-quarter camera, so its buildings, paths and rows run diagonally on screen. They are not individually rotated by runtime placement code.

The interactive Kingdom plots use an isometric ground projection. Its registered world-to-source affine is [60, -10, 25, 35, 170, 165]: a world-x step projects to [60, -10] pixels and a world-y step projects to [25, 35] pixels. Plot outlines therefore become slanted quadrilaterals that follow the painted map. Dynamic building images are drawn without a per-building rotation and their measured foot point is placed at the projected plot edge. Stone’s separate Town Hall layer uses uniform 0.1312 scaling plus translation in src/data/stone-scene.json, with no rotation or shear. The artwork itself has three-quarter perspective.

So the screen-diagonal arrangement comes from the ground-plane/camera composition, while any lean inside an individual cutout would be a source-art property. Rotating each sprite to face the screen would detach it from its ground footprint. A genuinely straight-on Kingdom would require coordinated redesign of terrain art, camera/projection, site coordinates, walls, roads and hit testing. This explains the current appearance; owner visual acceptance remains open.
## Evidence

- Live age fixture captures: `kingdom-ages-live-20261020/kingdom-live-age-review.json`; 8 ages × 2 landscape sizes (1280×720 and 825×375), 16 captures, 0 page or console errors. Every age was visually reviewed at both sizes. These are isolated age/Hall fixtures, not a natural eight-age campaign.
- Town Hall candidate comparison: `kingdom-ages-live-20261020/other-townhall-candidates-live-20261020.json`; generated Gunpowder and Modern candidate layers fit at both sizes.
- Natural browser journey: `natural-run-live-20261020-825x375/natural-run.json` and `natural-run-live-20261020-1280x720/natural-run.json`; 11 captured states each, legal route preview/confirmation, one guard battle, settlement, and reload persistence; 0 page or console errors. This is one natural journey, not the complete J01–J18 acceptance set.
- Isolated native IndexedDB probe: `native-storage-probe-live-20261020.json`; 12/12 assertions pass in a fresh browser context, with no page errors or missing resources.
- Full bounded Node suite: `node --test tests/*.test.mjs`; 205/205 pass.

## Data correction and remaining gates

The Industrial Town Hall PNG's bytes hash to `2014c11adac68355f50d4dbd4324bfc1893217722d0309129fffcd659cd6f11d`; the asset metadata had a one-character mismatch. The data and regression expectation now match the file bytes.

This diagnosis does not close the full visual/game acceptance. Full mock-by-mock pixel comparison, all 32 source-bound scene traces, the complete natural journey matrix, final web/package parity, independent desktop review, and later device and owner acceptance remain separate open gates.

## Fresh closed-inspector layout check - 20 October 2026

Visually reviewed natural fresh Stone captures at 825x375, 933x424, 1180x820 and 1280x720. Their bounded optimistic zero-inset world ratios are 91.37%, 93.25%, 97.04% and 96.89%; all four exact requested viewport sizes were delivered by the browser and there were no page or console errors. The HUD and primary controls stay inside the visible viewport in these captures. Raw measurements and images are in kingdom-prominence-live-20261020/kingdom-prominence-live-20261020.json and the sibling PNG files.

This meets only the >=80% rectangle-accounting threshold for these four closed-inspector renders. The metric excludes transparent gaps and does not establish safe-area behavior, ancestor hit-target clearance, landmark visibility/picking, inspector or dense states, physical-device behavior, or owner acceptance.

## Mock camera cross-check

The approved 02-kingdom-day1.jpg and 03-kingdom-stone.jpg references also use an elevated three-quarter view: plot rows, paths and building faces run diagonally across the screen. The diagonal camera treatment itself is therefore consistent with the mock direction. The current live Stone composition still differs in settlement density, integrated wall silhouette, and truthful dynamic building states; these remain separate visual repair and acceptance work.
