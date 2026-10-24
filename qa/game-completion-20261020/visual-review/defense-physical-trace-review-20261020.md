# Defense physical trace review — 20 October 2026

**Result: INCOMPLETE.** All eight current Defense scene candidates were normalized to the contract source size (1376x768), then annotated with the frozen 29-cell lane, D1–D8 site rectangles, gate anchor and spawn anchor from src/data/implementation-contract.json. The affine used was [60,-8,20,35,270,100]. This is a visual alignment aid, not a collision map or owner acceptance.

Evidence:
- defense-eight-age-physical-trace-overlay-20261020.png
- defense-sites-8-ages-close-crops-20261020.png
- Individual overlays: defense-physical-trace-age0-20261020.png through defense-physical-trace-age7-20261020.png
- Regenerator: defense-physical-trace-overlay-20261020.py

The lane centerline generally tracks the visible road corridor, but the site crops show probable physical clearance conflicts that must be resolved before any Defense scene can receive a physical-trace PASS:
- Age 2 Iron, D8 intersects the gatehouse or curtain-wall footprint.
- Age 5 Industrial, D8 intersects the fortress gate/wall; D1 and D2 sit at the frozen stream and bridge approach.
- Age 6 Modern, D8 intersects the fortress gate/wall; D3 and D7 are crowded by water-side structures and town buildings.
- Age 7 Future, D3 is near the water/stone crossing, D5 overlaps broken masonry, and D6 overlaps the bridge deck.

These are visual flags from registered source-space crops. Confirm exact footprint collision and depth in the live rendered scene before repair. Preserve the frozen lane/site coordinates unless an explicit owner contract revision authorizes a gameplay-geometry change. Repair the affected scene art around its existing geometry, then regenerate overlays, verify clear placement and crossings in the live three-size Defense journey, and keep natural-age and owner acceptance separate. The other ages still need explicit site-by-site clearance sign-off even where no obvious conflict appears here.
## Runtime occupancy check added 20 October 2026

The synthetic all-site runtime preview now occupies D1–D8 in each age and confirms the rendered site IDs match the frozen contract. Age 2 D7/D8 sit against battlements/gatehouse; Age 5 D6 and Age 7 D6 sit at bridge decks. These may be intentional emplacement positions. The runtime evidence does not resolve collision or owner/mock fit, so no coordinates or art were changed and all physical-trace states remain pending. See `defense-site-occupancy-runtime-review-20261020.md`.
