# Shared map-space composition blueprint — 3 October 2026

**Current review:** [Adventure / Tactical placement blueprint](../../design-preview/review-map-space.html). This is a proposed spatial specification, not finished terrain, a playable scene or owner acceptance. The previous scene assembly remains rejected. Work follows the latest request to plan appropriate terrain spots before placing independent objects.

The authorised deliverable here is a blueprint and comparison against actual owner mocks. It deliberately does not replace the existing scene with another arbitrary background. No whole mock is used as authored scenery, and no inspection cutouts are presented as matching world actors. Finished materials and production layers are still missing.

## Actual mock composition and proposed response

Direct pixel review: `references/owner-additions-2026-10-02/image_4f5e15d7.jpg` and `image_27abdc40.jpg`, each 1408 × 768. Positions below are approximate visual readings, not extracted source geometry. Reference files are unchanged.

| Relationship in actual reference | Blueprint response | Still missing |
|---|---|---|
| Adventure: large fortified town above/left of central travelling hero; gate road physically meets the junction | A1 reserves a 3 × 3 ground clearing above H; south gate approach (8,4) joins the hero road | Matching aerial fortified-town cluster, exposed gate, state variants |
| River down the left; stone bridge spans the water and joins roads on both banks | B1 reserves two consecutive crossing cells, with west/east approach pads, a continuous hero-to-mill/shrine corridor | High-detail authored riverbanks, stone deck/arches and rail occlusion layers |
| Separate discoveries/guards lie beside roads; forest dwelling cluster southeast; hostile ruin northeast | A5 southeast forest clearing; A2 northeast ruin; G1/G2 guard ground anchors; four pickup pads on connected side clearings | Era/identity-correct dwelling and ruin art; no inferred sample factions or currencies |
| Terrain has woods, rocky skyline, water and open inhabited fields, rather than all objects atop one forest patch | Excluded wooded southwest/southeast margins; northern rocky scenery; useful open east bank with six site clearings | Continuous naturalistic terrain and dressing following these reserved areas |
| Tactical: allied figures occupy near left ledges; enemies occupy the deeper opposite bank, with stream/stone crossings between | Three allied and three enemy stack slots, two crossing lanes, open approaches, fixed commander (0,9) | Close matched aerial formations, natural foot contact, facing and depth |
| Tactical rocks/ruins frame playable ground instead of receiving actors | Ten authored obstacle cells excluded; scenery outside the active field; river column blocks movement except its two decks | Terrain matched to these polygons; no old panorama obstacle assumed compatible |

The blueprint adopts the reference's spatial relationships, not its labels, hexes, rival identity, extra resource count or unplanned creatures. It proposes different authored coordinates; no claim of a pixel-identical composition is made.

## One world / camera contract

Both modes use the same coordinate convention and projection procedure, with different proposed camera distances/elevations because Adventure is regional and Tactical is closer. One cell is one **design ground unit**, not an adopted metre or combat reach. Origins are upper-left logical cell corners, column increases right, row increases down; actor and route anchors are `(column+.5,row+.5)`. Site rectangles are ground bounds, not sprite bounding boxes. Tactical remains square 7 columns × 10 rows; Adventure remains hidden 16 × 10. No coordinate remapping on rotation.

For yaw `a`, elevation `e`, ground unit scale `u`, ground point `(x,y,z)`:

```text
sourceX = u * (cos(a)*x + sin(a)*y)
sourceY = u * (sin(e)*(-sin(a)*x + cos(a)*y) - cos(e)*z)
screen  = viewportFit * (source - cameraSourceOrigin) + viewportOffset
```

Blueprint proposals: Adventure yaw 15°, elevation 55°, unit 80 source pixels; Tactical yaw 15°, elevation 40°, unit 96. These are explicit starting calibration values, **not measured angles of existing art and not a frozen accepted camera**. Orthographic projection is a reproducible design starting point; compare a future matched art calibration against the mock before freezing it.

The review SVG contains one root camera/viewBox and all scene layers beneath one `world-plane`. Every cell polygon, road, clearing, site approach, bridge, foot anchor, selection ring and route uses `project()` with that mode's camera. Resize preserves the source coordinates and changes only uniform viewport fit/offset. SVG `preserveAspectRatio="xMidYMid meet"` avoids independent stretching. There are no screen-percent site placements or unrelated image crops.

Whole region includes every reserved site/slot. Crossing detail changes only the root camera window, openly showing a subset; Whole region restores all locations. This is a review framing control, not implemented gameplay pan/zoom. Portrait overview is necessarily smaller than landscape; small blueprint labels do not establish final actor or battle-count readability. The final game needs bounded focus/pan plus a reachable overview, with readable screen-space information anchored to the same projected world position.

When assets are authored, each asset record must include source dimensions, exact contact pivot(s), ground footprint polygon, roof/body silhouette bounds, unit reference height, camera yaw/elevation/orthographic scale, ground facing, light direction, shadow coverage, and occluder masks. A footpoint is not the image centre or its shadow's lowest pixel. Ground map uses this projection; upright actors retain body height via `z`, not a sheared bitmap pretending to be a ground texture. Screen-space labels/counts follow their projected anchors with bounded pixel offsets.

Picking must use the inverse of the same viewport and ground transform. Future height/terrace picking needs explicit surface identity; no claim that a 2D inverse solves arbitrary 3D terrain. Draw contact shadows beneath actors; sort sites/actors/occluders by camera ground depth; bridge rails/front walls are separate occlusion pieces. Avoid sorting by file centre or arbitrary DOM order.

## Adventure terrain and empty footprints

Author terrain around these reservations. Do not first select an unrelated finished landscape and try to fit these points onto it. The exact authored records are in [map-space-data.js](../../design-preview/map-space-data.js). Coordinates are zero-based; these are a review proposal, not generated campaign content.

| ID | Ground footprint (origin; width × depth) | Approach / facing |
|---|---|---|
| A1 fortified town | (7,1); 3 × 3 | (8,4), south gate / +row |
| A2 guarded ruin | (12,1); 2 × 2 | (12,3), south opening / +row |
| A3 mill | (1,4); 2 × 2 | (2,6), south apron / +row |
| A4 mine | (11,6); 2 × 2 | (10,6), west entrance / −column |
| A5 forest dwelling | (11,8); 2 × 2 | (10,8), west clearing / −column |
| A6 shrine | (1,8); 2 × 2 | (2,7), north opening / −row |
| F / W / S / G pickups | Food (3,8); Wood (7,9); Stone (14,5); Gold (10,4); each 1 × 1 | Connected side clearing; no extra currencies |
| G1 / G2 guards | (12,4) / (10,5); each 1 × 1 | Separate encounter positions outside structure footprint |
| H travelling hero | (8,8), centre (8.5,8.5) | Foot or mounted actor pivots use the same saved ground anchor |

Each clearing reserves its full bounds; the site object's base is inset 0.2 units on every side, leaving an explicit edge margin. Roads terminate at the approach outside the structure footprint. High tower/roof silhouettes can extend above the ground rectangle only if their authored occlusion and screen silhouettes remain compatible with nearby routes. Reserved resource pads are discovery objects, not the compact resource HUD.

Water occupies columns 4 and 5, rows 0–9. Only (4,6) and (5,6) are deck crossings. B1 ground deck is `(3.75,6.05,2.5,.9)` with clear approaches (3,6)/(6,6); width .9 units must include the route corridor and actor/horse feet. Deck surface height is `z=0`, matching both approaches in this proof; any future raised deck needs a real connected ramp and matching height, not pasted hovering art.

Dense woodland / cliff exclusions: `(0,4)…(0,9)`, `(1,7)`, `(14,8),(15,8),(14,9),(15,9)`, `(14,0),(15,0)…(15,5)`. Northern high rock dressing remains outside site clearings. There is no playable sky band. Different natural materials can blend across ground; cell boundaries are not texture tiles or visible exploration squares.

Hero-to-crossing-to-shrine approach:

```text
(8,8) → (8,7) → (7,7) → (7,6) → (6,6)
      → (5,6) → (4,6) → (3,6) → (2,6) → (2,7)
```

Town road: (8,4)→(8,5)→(8,6)→(8,7)→(8,8). Branches connect mine, dwelling, ruin and four resource pads in the authored records. G1/G2 interrupt their encounter approach; a drawn physical road beyond a guard is not a currently legal movement preview. The shown yellow hero route avoids both guards. These sample corridors use orthogonal cell steps for clarity; they do not replace the campaign's adopted diagonal movement/corner rules, movement costs or pathfinder. No navigation implementation has been written.

## Tactical ground, deployment and formation reservation

No resource HUD. Commander remains at (0,9). This proposed battlefield is a two-bank encounter layout, not a new battle topology or a universal terrain required for every biome.

Stream occupies column 3 at every row. B1 deck (3,3), approaches (2,3)/(4,3); B2 deck (3,7), approaches (2,7)/(4,7). Deck rectangles `(2.75,3.1,1.5,.8)` and `(2.75,7.1,1.5,.8)` extend into their approach cells. Contact surfaces remain z=0. Arches, stream depth and parapets must not consume the reserved deck corridor.

Blocked rocks/walls: `(0,0),(1,0),(0,1),(6,0),(6,1),(0,5),(6,5),(6,8),(6,9),(5,9)`. Place ruin silhouettes/cliffs on these footprints or beyond board limits. Legal ground cells must stay clear, including the commander's cell. Proposed allied deployment: columns 0–2, rows 6–9 (12 cells). Proposed enemy deployment: columns 4–6, rows 0–3 excluding blocked (6,0)/(6,1) (10 cells). These start bands need future rule review; the six displayed active combat slots below are a separate composition fixture, not a claim that all six lie inside deployment bands.

| Active ground slot | Coordinate | Visual facing / reservation |
|---|---|---|
| C commander | (0,9) | Separate actor, no troop-stack count implied |
| L1 melee | (1,8) | Toward lower bridge / enemy bank |
| L2 ranged | (1,4) | Across stream / toward enemy bank |
| L3 heavy | (2,1) | Toward upper lane / enemy bank |
| R1 / R2 / R3 enemy groups | (5,2) / (5,4) / (5,7) | Opposed facing toward allied bank |

Each stack reserves a `.76 × .76` ground square inset `.12` from its cell. Future representative formation offsets in local footprint space: centre `(0,.12)`, rear left `(-.2,-.16)`, rear right `(.2,-.16)` with each base radius ≤.12; rotate those ground offsets to the stack facing before projection. Representative figures express **one stack**, never new independently simulated entities. Fit silhouette height and count/health badge at actual phone pixels; numerical badges are omitted from this geometry proof because there is no campaign combat state.

Separate example route: (1,8)→(1,7)→(2,7)→(3,7)→(4,7). The destination is clear; R3 at (5,7) is a separate enemy/target. Exact move range, engagement, cover, flying paths, spell areas and damage remain adopted rules to verify later. This blueprint reserves obstruction geometry without adding sample flanking formulas or new creature families.

Terrain, site/slot footprints, deployment marks, road material, route line, selection outline, target outline and actor contacts must remain distinct layers. Toggling the planning grid cannot remove/shift the terrain or any site. A minimap must later derive from this region; no generic decorative minimap is asserted here.

## Asset fit record

Directly inspected current copied candidates below. Camera observations are visual, not recovered rendering metadata. Manual source pivot estimates have roughly ±8–16 source-pixel uncertainty and **are not approved pivots**; a source-alpha/shadow audit must resolve them before use. Camera mismatch cannot be solved by CSS scale or mirroring.

| Existing candidate | Observed fit / camera / facing gap | Ground scale / pivot requirement and decision |
|---|---|---|
| `art/map-land-forest.webp` · 512 × 512 | High aerial forest road; one wooden bridge. Dense canopy leaves no matching A1/A2/A4/A5 clearings. Source camera and ground dimensions not recorded. | Do not stretch into the 16 × 10 region. Forest/water material evidence only; topology requires an authored map with reserved ground and stone crossing. |
| `art/tactical-ruins-original.png` · 6336 × 2688 | Low horizon camera; irregular baked foreground masonry/planks/barrel. No corresponding two-bank/two-deck board; no obstacle polygons or source projection. | Sharp source does not fit legal slots. Ruin/stone material reference only; do not remap a uniform 7 × 10 grid across it. |
| `art/bld-townhall-medieval.webp` · 1024 × 1024 | Single half-timber house, three-quarter roof. No town wall/gate cluster or documented camera. Visible base extends roughly x140–915/y615–895, not a measured world footprint. | Approximate base centre (520,825), not square image centre. Cannot fill A1 3 × 3 as a fortified town; possible secondary building only after matching ground camera and base. |
| `art/bld-mine-medieval.webp` · 1024 × 1024 | Three-quarter mine with rails and rubble already in its base; mouth faces lower-left in image. Exact camera unknown. Magenta/blue edges visible. | A4 is a 2 × 2 clearing with west-facing entrance. Approximate mouth/rail exit (440,635); rubble bounds roughly x75–935/y470–875 must fit inside its inset base. Do not rotate a 2D bitmap to fake the west entrance; match/calibrate or reject. |
| `art/unit-heavy-medieval.webp` · 768 × 768 | Cavalry faces viewer/right, shallow overhead view; red/blue rider is a troop stand-in, not proven Gawain. Long baked shadow extends below/right. No directional gait. | Visible figure y≈120–568. Fore hoof ≈(382,560), rear hoof ≈(220,490); provisional ground pivot ≈(325,516). The shadow's y≈736 is not a hoof. Match aerial camera, class identity, route-facing variants and independent soft contact shadow. |
| `art/unit-melee-medieval.webp` · 768 × 768 | Frontal standing soldier; no opposed formation views; long baked shadow, no walk/attack/hit/death gait. | Foot contacts ≈(360,562)/(480,534), pivot ≈(420,548). Body y≈120–568. Use cropped visible figure height when calibrating to ≤.76-cell formation footprint; file-wide scaling is wrong. Remains inspection/scale reference until camera/facing fit. |

Adventure scale brief: ordinary foot actor height initially .45 ground units; mounted silhouette .65; site bases 1.6 × 1.6 for a 2 × 2 clearing; town base 2.6 × 2.6 for A1. Tactical initial foot actor .75 units, mounted 1.05; representative ground discs/formation offsets as above. These values are explicit **art-calibration proposals**, not physical heights or approved game rules. Future asset calibration must compare mock figure/site scale and actual 375px/rotated-phone pixels before accepting them.

Reserve matching terrain/site/actor art needs in the existing useful-art backlog; do not submit generation. Reuse-first, exactly 30 useful requests, one active batch globally and provider jobs UNKNOWN / BILLING_DISABLED remain. No new job, image editing, billing change or runtime generator is part of this work.

## Verification and acceptance

Scope: static blueprint coordinates, projection, layer controls, reference/asset loads and responsive review page. Retain scoped browser evidence in `design-preview/evidence/map-space/`. Coordinate checks must reject road/route steps on water without decks, obstacle/site intrusion, disconnected approaches/pickup branches, duplicate formation cells, and commander drift. Check each bridge includes the route centre and has accessible land approaches. Verify projected anchor/cell centres remain registered after actual viewport resize and mode/detail/layer changes.

Automated consistency is not gameplay legality or naturalistic fidelity. Inspect the actual blueprint and unchanged mock side by side. Missing rendered terrain, aerial site assets, actor camera/facing/gaits, final counts/HUD, physical phone and full-gallery review remain **unverified / unresolved**. No section is accepted and no game code is authorised. The full eight-age, three-mode linked campaign and Defense hidden 9 × 15 are unchanged.

### Executed evidence

`check-map-space.mjs` completed with exit0 using the recorded bundled Node/Playwright and installed Chrome, with the existing localhost server. Geometry checks passed for both maps: footprint non-overlap/exclusions, in-bounds connected route steps, water-only-at-decks, clear approaches, reachable Adventure branches/pickup pads/guards, distinct contact cells and fixed commander. These are checks of the authored proposal, not tests of future gameplay.

Eight browser cases passed: Adventure/Tactical at375×825,825×375,768×1024,1280×1024. No page/asset errors, broken images, horizontal page overflow or review buttons below48px. Actor anchor versus reserved slot centre error <.01 screen pixels after resize; all overview footprints in bounds;160/70 planning cells preserved. Mode/layer/detail switches verified; detail viewBox preserved after portrait resize. Text contrast: body14.34:1, secondary10.33:1, button10.86:1, pressed6.87:1. These measurements cover the review shell, not a future textured HUD.

Seven scoped captures retained: both mode blueprints at375 and825 widths, two side-by-side desktop comparisons, one portrait Adventure crossing detail. Selected final pixels were inspected. Empty site areas, continuous crossing route and distinct ground slots are visible; portrait overview is smaller but its short IDs remain readable. Natural rendered geography, realistic figure/site scale and high-detail terrain are **not supplied by this drawing**. No new owner acceptance. Evidence and exact measurements: `../../design-preview/evidence/map-space/checks.json`.
