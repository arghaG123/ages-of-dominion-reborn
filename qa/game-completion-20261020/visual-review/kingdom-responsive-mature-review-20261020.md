# Kingdom responsive mature-fixture review — 20 October 2026

**Focused result: PASS for scene selection, responsive exposure and plot hit geometry. Whole-game visual acceptance remains INCOMPLETE.**

## What was checked

Captured all eight Kingdom ages at 825×375, 933×424 and 1280×720 using isolated mature-save fixtures, for 24 live browser screenshots. Every expected age terrain loaded; all runs exposed 18 plot nodes and 18 occupied plots with wall level 1, had zero browser errors and failed responses, and had no document overflow. Every visible control remained in-frame and its actionable center received the DOM hit. At 825×375, I also clicked all 18 plot footprints for each age and verified each opened and closed its inspector: 144/144 browser interactions passed. Evidence: [24-run report](kingdom-mature-all-viewport-live/report.json) and [capture runner](kingdom-mature-all-viewport-live-20261020.mjs).

The first probe used the center of each plot group’s combined bounds. Tall building sprites extend above their clickable ground cell, so that point can sit over transparent sprite pixels. The probe was corrected to sample the transparent ground-footprint polygon that receives plot clicks. All 24 runs then passed; this was a QA-measurement correction, not a product repair.

## Visual finding: the diagonal placement is intentional

Kingdom uses an elevated isometric view. The active world-to-source transform `[60,-10,25,35,170,165]` projects the two grid axes to `(60,-10)` and `(25,35)`, so plot rows run diagonally across the screen. Building images are anchored at their measured feet and are not individually rotated. Direct comparison with the approved Kingdom mock camera confirms that this diagonal composition is intentional. Making the buildings or rows screen-straight would require a coordinated redesign of terrain, plots, roads, walls and pointer mapping, and would depart from the accepted mock camera.

## Remaining visual gap

The responsive check proves exposure and current plot hit geometry, not mock-level city quality. The mature fixtures are not earned progression, and their filled plots create a deliberately dense diagnostic scene. Across ages, the complete settlement still needs review for coherent facility art, believable spacing/scale, integrated same-family walls, natural construction/upgrade states, and parity with the much more detailed mock compositions. Physical site clearance and natural progression remain separate open gates.

Screenshots are available by age and viewport under `kingdom-mature-all-viewport-live/`, for example [Stone at 825×375](kingdom-mature-all-viewport-live/kingdom-age0-825x375.png) and [Future at 1280×720](kingdom-mature-all-viewport-live/kingdom-age7-1280x720.png). These synthetic fixtures do not establish natural all-age play, 30-mock or 18-journey acceptance, independent desktop review, final snapshot APK, later device or owner acceptance. No production art or game source was changed.
