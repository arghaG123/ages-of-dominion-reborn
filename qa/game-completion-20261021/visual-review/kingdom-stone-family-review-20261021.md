# Stone Kingdom populated family review — 21 October 2026

Status: **runtime-bound and naturally browser-checked; full visual and owner acceptance remain open.**

## Repair

The Stone Kingdom now uses a versioned four-state terrain family. It adds a denser settlement around the registered central building district while retaining the interactive site overlays and the original isometric transform. The live Quarry, walls, and Town Hall remain separate game objects.

The selected images are all RGB 1678×937. The old runtime family remains in place. The first generated built-wall image was rejected because its canvas was 1677×938; the exact-frame replacement is used.

## Runtime changes

- src/client/kingdom-view.js now routes Stone ground, scaffold, level-1 wall, and taller wall to assets/derivatives/kingdom-stone-populated-20261021/.
- tests/four-repairs-20261017.test.mjs now asserts the versioned runtime family.
- The live Story > Quests journal places the six-slot equipment goal before the milestone list.
- docs/plan/GAME-DATA-REFERENCE.json now records the intentional seven-chapter Story adaptation as STORY_ALL. originalTables.STORY remains frozen.

## Image records

| Phase | Runtime file | Bytes | SHA-256 |
|---|---|---:|---|
| Ground | assets/derivatives/kingdom-stone-populated-20261021/stone-ground.png | 3,815,218 | 1B16E9A0EAACB23C4E1E1CB1DF2375D773DCA591C91B62ADB67511573ADB7890 |
| Scaffold | assets/derivatives/kingdom-stone-populated-20261021/stone-scaffold.png | 3,678,548 | BF336003716E4C66CB384EEDA84B11994A56501AF8443F939C24805A62265628 |
| Wall | assets/derivatives/kingdom-stone-populated-20261021/stone-wall.png | 3,681,281 | 0AF7D29B8532DD9B4889A8226588B5B63F48681BF46513166ADFC3C56CD5907F |
| Taller wall | assets/derivatives/kingdom-stone-populated-20261021/stone-wall-tall.png | 3,674,876 | 616E84813D9840C24FF6C30A22FEB0A1B6E8A09DEE4A95FC5C7F2872B8B63069 |

Built-in image generation produced the source outputs under C:/Users/pupan/.codex/generated_images/01a14d31-4376-7570-bde1-ae01df1f91de:

- Ground: exec-05205edf-5bba-465b-93f6-e02b11ce51ca.png
- Scaffold: exec-907f4ca3-991c-41c4-a338-c491f6a72e23.png
- Wall v1, rejected for frame ratio: exec-bddf07d3-f8bd-4300-9739-523b9266676b.png
- Wall v2, selected: exec-b2e6914b-fd9c-4414-b22b-6088a94e555a.png
- Taller wall: exec-9217db9c-3b83-4647-b20f-9bac927d8e3d.png

## Geometry and visual checks

The site and road overlays are in qa/game-completion-20261020/visual-review/kingdom-stone-populated-*-site-overlay-20261021.png. They show all 18 site polygons, the central road, and the lower-center gate anchor. The right river crossing remains separate from the gate.

ORB/RANSAC feature registration against the current active Stone ground returned near-identity transforms for all four phases. Median and p95 reprojection residuals were:

- Ground: 0.272 px / 2.464 px
- Scaffold: 0.572 px / 2.364 px
- Wall: 0.348 px / 2.273 px
- Taller wall: 0.410 px / 2.557 px

These measurements confirm camera/frame alignment; they do not replace pixel-level road, bank, gate-contact, or owner review.

The isolated natural browser run uses visible UI controls to start a fresh Jade campaign, build a Quarry, and raise Walls through levels 1 and 2. Ground, both scaffold jobs, the built wall, and the taller wall were captured at 1280×720 and 825×375: 10 screenshots, 18 plots each, expected 1678×937 terrain loaded, zero page/console/network errors. Report and capture runner:

- qa/game-completion-20261021/visual-review/kingdom-stone-family-live-20261021-run2/report.json
- qa/game-completion-20261021/visual-review/kingdom-stone-family-live-20261021.mjs

The complete Node suite passes 234/234; the focused Kingdom file passes 9/9.

## Visual result and remaining scope

The new ground is visibly more populated and the natural phase transitions read clearly. The central building district remains intentionally open at campaign start; the resulting Stone scene is still less dense than the approved fully developed Kingdom mock. All-age Kingdom buildings and wall families, complete mock-by-mock comparisons, physical scene contact review, full natural journeys, independent desktop acceptance, final package, device, and owner review remain open. This bounded Stone repair does not complete the game.

The diagonal site rows come from the approved isometric matrix [60,-10,25,35,170,165]. Building art is foot-anchored and not individually rotated. Straightening the rows alone would misalign the terrain, roads, walls, and click targets.

## Final image prompts

Ground:

“Use case: precise-object-edit. Asset type: Stone Age Kingdom game terrain background. Input image 1 is the edit target and must keep its exact wide camera framing, river and riverbanks, both crossings, roads, existing huts, farms, forests, terrain contours, lighting direction and image boundaries. Input image 2 is a visual reference only for the denser settlement scale and lived-in town feeling; do not copy its UI or text. Change only the settlement density: add a coherent semi-realistic Stone Age village around the outer edges of the existing central clearing, with small timber-and-stone houses, market shelters, workshops, gardens and short connecting paths that follow the existing roads. Preserve the open central construction district and leave the upper-center Town Hall anchor unobstructed for a separately rendered building. Leave clear, natural ground at every existing gameplay building site; do not place new buildings or props on those site footprints. Keep all roads, the river, shoreline, bridge approaches and crossing stones exactly aligned with image 1. Match the original aerial isometric camera, scale, natural materials, warm daylight and sharp high-quality strategy-game render. No wall or fence, no added river, no grid, no labels, no numbers, no UI, no text, no logo, no watermark, no image borders.”

Scaffold:

“Use case: precise-object-edit. Asset type: matching Stone Age Kingdom scaffold terrain phase. Input image 1 is the edit target. Input image 2 is a reference only for the exact central perimeter route and gate shape. Preserve input 1’s camera, crop, river and banks, bridge, roads, terrain, houses, farms, vegetation, lighting, all existing site footprints and upper-center Hall opening exactly. Change only the wall-construction state: add a low, incomplete timber construction scaffold around the same central settlement perimeter shown in input 2. Show upright work posts, a few braces and materials, with a clearly open gate at the right-side bridge approach. Keep the scaffold phase visibly distinct from both bare ground and a completed palisade. Leave all 18 gameplay building site footprints and the central road corridor unobstructed. Maintain the same sharp semi-realistic aerial isometric strategy-game art. No finished wall, no extra structures inside build footprints, no new terrain or road changes, no UI, text, labels, grid, logo, watermark, or border.”

Wall v2:

“Use case: precise-object-edit. Asset type: completed Stone Age Kingdom palisade terrain phase. Input image 1 is the edit target. Input image 2 is a reference only for the exact perimeter route, timber wall style and lower-central-road gate. Preserve input 1’s complete camera, crop, river, banks, bridge, roads, terrain, populated outer settlement, farms, vegetation, light, and all 18 clear gameplay building sites. Change only the wall state to a finished integrated palisade along the same central ring; closely spaced upright logs, natural shadow, grounded earth-and-stone base, one traversable gate opening exactly where the lower central road reaches the perimeter. The right-side river bridge remains separate. Preserve the source canvas aspect exactly: 1678 pixels wide by 937 pixels high, ratio 1.7908:1; do not crop, expand, rotate, or reframe. Match the other phases’ sharp, warm, semi-realistic aerial-isometric strategy-game quality. No structures on build sites, no blocked central road, no new water/roads, no text, labels, UI, grid, logo, watermark or border.”

Taller wall:

“Use case: precise-object-edit. Asset type: upgraded Stone Age Kingdom timber wall terrain phase. Input image 1 is the edit target. Input image 2 is a reference only for the taller wall silhouette and material treatment. Preserve input 1’s exact camera, crop, river and banks, bridge crossing, roads, terrain, populated outer village, farms, vegetation, lighting and all 18 clear gameplay building footprints. Change only the central perimeter wall: make it a taller, reinforced Stone Age palisade with thicker upright logs, a few small timber lookout platforms and stronger lower braces, following the same wall route as the reference. Keep the gate opening on the lower central road at the image-1 location; the river bridge remains a separate crossing on the right. Keep the central road clear, and do not put structures on any of the 18 build sites or block the Hall anchor. Match the existing warm light, scale, grounded shadows and sharp semi-realistic aerial isometric strategy-game materials. No extra wall outside the perimeter, no stone castle towers, no new structures, no UI, text, labels, grid, logo, watermark, or border.”
