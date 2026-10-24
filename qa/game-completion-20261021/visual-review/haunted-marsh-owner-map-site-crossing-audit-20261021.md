# Haunted Marsh owner-map prebinding site and crossing audit — 21 October 2026

**Classification: owner-map source registration FAIL; generated terrain remains live.** This review compares the current JSON and 16×10 coordinate overlay to the owner painting. It is not live gameplay acceptance.

## Current source state

The selected owner painting is `assets/mocks/owner-approved-vast-adventure-maps-20261020/03_Vast_Map_Autumn_Marsh_Thunderstorm.png` (1376×768; SHA256 `52A11BACB9944E2A240A49E795B19B6FE20732CE66F8E3BC49C8D31F4B581429`). The labeled grid overlay hash is `7C7424398611BAD54BC1E72F5F5DD1CF0EF4003A41164A6D9164962916207676`, using transform `[86,0,0,76.8,0,0]`. `runtimeFile` is null, so recent Haunted Marsh journeys on generated terrain are not owner-map evidence.

Current geometry defines three blockers ([5,2], [6,2], [7,2]), no obstacles, no roads, and no bridges. The owner painting shows broad wetland channels, visible footpaths, and several stone bridge decks. Exact water/mud blockers, road segments, bridge cells, and both safe banks have not been traced; the current route map is insufficient to bind the painting.

## Site-role pixel review

| Site | Current rect / approach | Source-pixel disposition | Candidate / decision |
|---|---|---|---|
| Town | [11,0,4,3] / [10,3] | FAIL: most of this region is storm sky and mountain. | The main town could be the large waterside hamlet around columns 10–13, rows 4–6, or the central walled compound around columns 5–7, rows 5–6. Decide Town versus Ruin roles before setting the rectangle and safe entry. |
| Ruin | [2,5,2,2] / [4,5] | FAIL: this box covers forest, road, and marsh edge, not an obvious ruin. | The central walled compound is the strongest ruin-like candidate, but it could instead be the town. Reconcile its role from the approved map semantics. |
| Mill | [1,2,2,2] / [3,2] | FAIL: this footprint sits on the rocky western outcrop/mining approach. | Multiple windmills occupy the upper-right ridge around columns 11–15, row 2. Trace the exact mill group and a walkable approach. |
| Mine | [7,6,2,2] / [9,6] | FAIL: this box is over marsh channel and road. | The western cave, ore carts, and excavation near columns 0–2, rows 2–3 are the strongest mine candidate; current Mill overlaps part of this area. Candidate Mine [0,2,2,2], approach [2,3], requires exact entrance/route tracing. |
| Dwelling | [12,7,2,2] / [11,7] | PARTIAL: the footprint overlaps a lower-right hamlet and huts. | Plausible, but confirm the settlement boundary and that approach [11,7] is on safe ground. |
| Shrine | [8,3,2,2] / [8,5] | FAIL: the box covers a stone bridge/tower and wetland, not a clear shrine. | A green spectral altar near column 11, row 2 and a purple crystal grotto on the eastern edge are possible magical landmarks. Reconcile the intended shrine before assigning coordinates. |

The Town/Ruin candidates are intentionally unresolved because the image contains both a fortified compound and multiple hamlets. Do not bind guessed roles or reuse the current rectangles.

## Crossing and hazard tracing

At least three visible stone bridge/causeway structures cross the wetland channels. The source-grid view is a screening aid; this audit does not certify exact deck cells. Trace each intended deck, both banks, neighboring water/mud cells, land routes, and any passable marsh separately. The current three blocked cells do not establish a complete hazard mask. Do not treat an empty bridge array as proof that the visible crossings are decorative.

Before binding, reconcile all six site roles, exact footprints and approaches, hero start, resource/guard anchors, water/mud collision, roads, every intended deck, and both safe banks from source pixels. Then verify through ordinary visible controls: Town start, each site/reward, every bridge in both directions, off-deck rejection, hazard boundaries, and save/reload at required viewports. Keep owner-source binding, natural routes, readability, persistence, and whole-game acceptance as distinct leaves.

**Verification limits:** current Adventure JSON, raw owner painting, and labeled grid were inspected only. No production source changed, no tests ran, and no live journey used the owner painting. The whole game remains INCOMPLETE.