# Jade Karst owner-map source and route recheck — 21 October 2026

**Classification: owner-image runtime binding, two natural bridge crossings, and bounded reload PASS; site registration PARTIAL. The Mill footprint FAILs source alignment, so Jade Karst is not a fully registered owner map. Adventure and the whole game remain INCOMPLETE.** Four of twelve campaign worlds currently select their owner painting in live play: Grasslands, Feywild, Jade Karst, and Crystal Underworld.

## Source registration and site recheck

src/data/adventure-worlds.json selects the matching Jade Karst owner painting:

assets/mocks/owner-approved-vast-adventure-maps-20261020/11_Vast_Map_Jade_Bamboo_Karst_Clean.png

The source image is 1376×768, SHA256 69E7BE94D2FA3C0D7D7769BC48FF839610059A0E01A8B51453A5EE7480E12C55. The current flat transform is [86, 0, 0, 76.8, 0, 0]. The current Mill record is rect [1,3,2,2], approach [3,3]. Direct review of the owner image and current 16×10 grid shows that footprint over western cliff/gold-cart terrain. Visible mill candidates are the wooden waterwheel around column 3, row 5, and windmills on the northern island around columns 8–10, row 0. Neither candidate is covered by the registered Mill rect. This is a source-alignment FAIL; the intended mill landmark and a safe approach need an explicit mapping decision.

The other five site roles have not been independently closed by this recheck. The current report records 15 blocked cells and two bridge decks. Both decks align with visible crossings: west deck [4,6]–[5,6] between approaches [5,5] and [3,6]; east deck [10,4]–[11,4] between approaches [9,4] and [11,5]. See the [source-grid report](owner-map-source-grid-audit-20261021/report.json) and [Jade Karst grid](owner-map-source-grid-audit-20261021/jade-karst-owner-source-16x10-grid.png).

## Existing natural crossing evidence

The earlier isolated visible-control journey on http://127.0.0.1:4198/ crossed the east deck in both directions, crossed the west deck, then saved and reloaded at the west endpoint. Reload retained day 4, position, and two moves, and the scene still selected the Jade owner painting with both registered crossings. This evidence supports those route and reload leaves only; it did not visit or validate the Mill interaction.

At 825×375 the map field fit and the details panel scrolled to its lower actions. The 1280×720 route was also reviewed. Fog substantially darkened the painting. Those viewport checks do not close map-wide visual fidelity or site alignment.

## Verification scope and remaining work

The prior report's statement that all six site footprints align with the source grid is withdrawn. The 18/18 focused map suite and 249/249 full Node suite were recorded on an earlier source snapshot; the full suite was not rerun after later geometry/test edits. The current focused Adventure-world suite is recorded as 18/18 after the Underworld change. No new tests were run for this recheck.

Repair the Mill footprint and approach using the waterwheel candidate unless source semantics select the northern windmills. Retain the Town, Dwelling, and Mine source-pixel alignment findings; resolve the Ruin and Shrine landmarks from owner/design semantics, then check each required interaction/reward through visible natural travel. Recheck the two bridge routes and actual rendered map, fog, minimap, dynamic anchors, and reload state. Whole-game visual fidelity, the other eight owner bindings, complete natural journeys, independent desktop review, final APK parity, device QA, and owner acceptance remain open.


## Independent site-role source-pixel recheck — 21 October 2026

The current Jade owner image SHA256 is 69E7BE94D2FA3C0D7D7769BC48FF839610059A0E01A8B51453A5EE7480E12C55, matching the source hash recorded above. Reopened the raw image and 16×10 overlay against current adventure-world data:

- Town [7,2,3,2] covers the central palace/civic compound; its approach [8,4] is on the southern road/gate area.
- Dwelling [10,1,2,2] covers the northeast settlement cluster; approach [10,3] is at its south edge.
- Mine [13,6,2,2] covers the eastern stone quarry and work carts; approach [12,6] is beside the access path.
- Mill [1,3,2,2] remains a clear source-alignment FAIL. A plausible source-grounded replacement is the wooden waterwheel at about column 3, rows 5–6: candidate rect [3,5,1,2], approach [2,6]. This candidate avoids the currently registered west bridge deck, but natural reachability and exact footprint still need verification. The pair of northern windmills around columns 8–9, row 0 is an alternate Mill landmark; the waterwheel is the stronger local fit for the site role.
- Ruin [1,7,2,2] does not cover the clear central stone pagoda/ruin around [5,7]; it ends immediately above the separate lower-left temple near [1,9]. Keep the role and exact footprint unresolved. Candidate [5,7,1,1] with approach [4,7] is source-based only and is not route-verified.
- Shrine [9,7,2,2] overlaps the enchanted lotus pond and sacred tree; that may be intentional, but the nearby southern pagoda and crystal landmarks leave the source role ambiguous. Keep Shrine OPEN until its intended landmark is reconciled.

This review upgrades Town, Dwelling, and Mine to plausible source-pixel alignment, but not to natural site/interaction acceptance. Existing west/east crossing routes and reload remain separate bounded evidence. No production source or tests were changed or run.