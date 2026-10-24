# Kingdom projection and all-age presentation review — 20 October 2026

**Orientation result: matches the landscape mock camera. Whole-game visual acceptance: INCOMPLETE.** The active Kingdom source transform is `[60,-10,25,35,170,165]`. Its world basis vectors are `(60,-10)` and `(25,35)`, so both map axes project diagonally. The landscape Kingdom mock set uses the same elevated, oblique composition; straight screen rows would diverge from that target.

The plot renderer projects each cell and places its building image from a measured foot anchor; it does not rotate the image per plot. Stone starter huts are painted scenery in `stone-ground.png`, while owned buildings are separate plot layers. The visibly angled rooflines come from the isometric art and camera perspective, not from a runtime rotation.

Current evidence:
- All eight ages rendered in a fresh isolated browser context at 1280×720 with their correct age ground image, 18 Kingdom plot nodes, Town Hall plus 17 occupied fixture plots, level-1 age wall and no browser errors.
- Mature fixtures use only one of each unique facility and legal save bytes; they are still injected static-age fixtures, not earned progression. Per-age captures and report: `kingdom-mature-all-ages-live/`.
- Current eight-age screen sheet: `kingdom-current-all-eight-age-contact-20261020.jpg`.
- Mock eight-age screen sheet: `kingdom-mock-all-eight-age-contact-20261020.jpg`.
- Focused Stone mock/runtime comparison: `kingdom-stone-projection-mock-v-runtime-20261020.jpg`.
- Natural browser subjourney from a fresh isolated profile: New Campaign → Knight → Kingdom → build Lumber Camp → durable save acknowledgement → reload. The same campaign, built plot, level and view survived; saved head matched current revision. No page/console errors or 404s. Evidence: `natural-campaign-build-reload/report.json` and before/after captures.
- Fresh bounded suite: `node --test tests/*.test.mjs` → 209/209 PASS. Fresh isolated real-browser storage probe → 12/12 PASS_BOUNDED, zero browser errors or 404s: `native-storage-probe-rerun-20261020.json`.

The current and mock projections align, but the assembled Kingdom does not yet meet full mock fidelity across city density, scene coherence, texture/detail, all age transitions, responsive states or every owned-building interaction. The synthetic renders and one natural UI subjourney cannot establish the 30-mock, 18-journey or full campaign acceptance gates. No projection or gameplay geometry was changed in this review.
