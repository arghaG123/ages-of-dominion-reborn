# Grasslands owner-map source and natural-journey recheck — 21 October 2026

**Classification: runtime owner-image selection, bounded Ruin interaction/reload, and three bridge crossings PASS; Ruin landmark identity OPEN. Full Adventure and the desktop game remain INCOMPLETE.** Grasslands is one of four campaign worlds selecting its matching owner painting in live play.

## Source registration and site identity

src/data/adventure-worlds.json selects the owner image assets/mocks/owner-approved-vast-adventure-maps-20261020/01_Vast_Map_Grasslands_Sunny.png (1376×768, SHA256 F2EC666AB7D2929E51F2D9153B22F3335D330952EA91775D27A2535EC01A14E9). The flat transform [86, 0, 0, 76.8, 0, 0] matches the 16×10 grid. The current Ruin footprint is [1,6,2,2] with approach [3,6]. Direct review of the raw owner painting shows that footprint over the blue crystal grotto and adjacent stone path. The circular arena around columns 5–6, row 3 is the clearest ruin-like landmark elsewhere on the image. The semantic choice remains unresolved; do not count six-site visual alignment as accepted until the owner/design role is reconciled.

The existing landmarks for Town [2,2,2,2], Mill [14,4,2,2], Mine [13,7,2,2], Dwelling [4,7,2,2], and Shrine [6,8,1,1] remain candidates, not all-site natural-journey or full visual acceptance. The complete geometry and bridges are in the [source-grid report](owner-map-source-grid-audit-20261021/report.json) and [Grasslands grid](owner-map-source-grid-audit-20261021/grasslands-owner-source-16x10-grid.png).

## Bounded live evidence

Prior isolated visible-control journeys selected Grasslands, claimed the labeled Ruin from its approach, and retained position/claim after reload at 1280×720 and 825×375. A separate visible journey crossed all three registered Grasslands bridges, visited each deck cell, and retained the far-bank position and deck visits after reload. These demonstrate live interaction, crossing, and persistence at the recorded coordinates; they do not establish that the Ruin label belongs over the crystal grotto or complete the other natural journeys.

The fog substantially darkens unexplored terrain. The earlier live captures were inspected in-browser but were not saved as separate image files.

## Test history and remaining scope

The old 17/17 focused and 247/247 full-suite counts belong to the earlier Grasslands snapshot. After later Underworld geometry/test edits, the focused Adventure-world suite is recorded as 18/18; the full Node suite has not been rerun on that current source snapshot. No new tests were run for this recheck.

Resolve the intended Ruin landmark and approach from source semantics, then retain the natural claim/reload and bridge evidence as separate leaves. Review full Grasslands composition, all six sites, hazards, dynamic anchors, minimap/fog, edges, and required natural journeys. The other eight owner paintings, independent desktop acceptance, final APK parity, device QA, and owner acceptance remain open.

