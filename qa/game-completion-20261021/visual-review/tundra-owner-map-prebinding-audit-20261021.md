# Tundra owner-map prebinding source and crossing audit — 21 October 2026

**Classification: owner-map site/route geometry FAIL; the source remains unbound.** This is a read-only source-grid review. It does not verify live Tundra behavior on the owner painting.

## Current source state

`src/data/adventure-worlds.json` currently selects generated terrain for `tundra`; `runtimeFile` is null. The owner painting is `assets/mocks/owner-approved-vast-adventure-maps-20261020/02_Vast_Map_Glacial_Tundra_Blizzard.png` (1376×768, SHA256 `C45AE88FAB2F321840B1C1C9761ED1FB7EA13269945BC652376B9D3E6DB56114`). The 16×10 grid overlay hash is `C4CBE3BBA381A1308CD7B1BCB53C4322AED8D38F9BD7709261254E81F8919550`; transform is `[86,0,0,76.8,0,0]`.

The current geometry has **zero blocked cells, obstacles, bridges, and roads**. The map art clearly contains frozen channels, snow paths, and several bridge/causeway structures. These missing registrations mean generated-map journeys cannot establish route safety on this painting.

## Site-by-site source review

| Site | Current rect / approach | Source-pixel disposition | Candidate or next decision |
|---|---|---|---|
| Town | `[9,1,4,2]` / `[10,3]` | FAIL: box lies mostly in aurora/sky and clips the eastern edge of the central ice citadel; the large domed settlement is at the west side. | Candidate Town `[1,3,3,2]`, approach `[3,5]`. Confirm whether the west domed city is the intended Town before binding. |
| Mine | `[1,3,2,2]` / `[3,3]` | FAIL: box covers a tower/ice approach. Gold ore carts and a cave/mining work area are on the lower west edge. | Candidate Mine `[0,5,2,2]`, approach `[2,6]`; trace the actual entrance and safe path. |
| Mill | `[9,6,2,2]` / `[8,6]` | FAIL: box lands on a stone tower/ice-channel area. | A wooden wheel and attached mill structure are visible near `[3,6]`. Candidate Mill `[3,6,1,1]`, approach `[4,6]`; verify full structure coverage and route. |
| Shrine | `[13,4,2,2]` / `[12,4]` | FAIL: box covers snowy channel/bridge terrain rather than a clear altar. | The turquoise obelisk on a circular rune base near `[7,7]` is the strongest shrine candidate: `[7,7,1,1]`, approach `[8,7]`. Confirm its role and route. |
| Ruin | `[1,7,2,2]` / `[3,7]` | FAIL: box covers the red crystal ridge, not a ruin. | Several stone towers and the central fortress could be mistaken for a ruin. Do not choose a replacement until the intended ruin role is mapped to the art. |
| Dwelling | `[5,2,2,2]` / `[7,3]` | PARTIAL: the box covers colorful tents and a nearby hamlet cluster; plausible dwelling art, but the footprint and approach are not accepted. | Retain as a candidate and verify the intended settlement boundary and safe approach. |

All candidate rectangles and approaches above are source-grid proposals only. They have not been used in live navigation, interaction, reward, save, or reload checks.

## Crossing and hazard tracing

The coordinate overlay shows at least three clear bridge/causeway candidates around the center-left channel, the center-right channel, and the lower-center channel. Their visible spans are only approximate screening zones; exact deck cells, both safe banks, surrounding ice-water blockers, and path connectivity remain untraced. The source image has additional narrow frozen channels that also need collision classification. Do not bind `runtimeFile` with empty masks or inferred deck cells.

Before binding, resolve every site role/footprint/approach, hero start, resource/guard anchors, all channel masks, roads, decks and both banks from the native pixels. Then run ordinary visible-control journeys against the owner painting for the Town start, each site/reward, every crossing in both directions, off-deck rejection, hazards, and save/reload at required viewports. Keep source geometry, runtime behavior, map readability, and full-game acceptance as separate leaves.

**Verification limits:** only the current JSON, raw owner image, and labeled 16×10 overlay were inspected. No production source changed, no tests ran, and no live Tundra journey was attempted. The full game remains INCOMPLETE.