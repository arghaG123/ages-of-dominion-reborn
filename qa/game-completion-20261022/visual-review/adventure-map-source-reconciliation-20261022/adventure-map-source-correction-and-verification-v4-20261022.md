# Adventure map source correction and verification — v4, 22 October 2026

## Current result

The owner-supplied twelve pictures are visual examples for appearance, composition, and quality. They are not production maps and their landmarks do not define gameplay. The runtime now accepts a campaign background only when the independently generated `productionMapFile`, its source binding, its SHA256, and active geometry v4 all agree. No `file`, `mapFile`, or reference-image fallback is accepted.

All twelve generated Adventure map assets were retained and reused after reviewing their full-map imagery and matching map-specific geometry. Their terrain, six site areas, roads, hazard cells, crossing decks and banks, safe starts, resources, and guard anchors are recorded in the v4 machine-readable matrix. Geometry remains on a 16×10 grid, bound to each PNG's native dimensions. Two overlapping site hitboxes were corrected; all other production geometry was retained. The examples, generated maps, saves, old evidence, and unrelated dirty work remain in place. No image purchase or provider request was made.

The whole game is still **INCOMPLETE**. This closes the scoped source/geometry repair, not the full-game desktop, final APK, device, or owner acceptance gates.

## Sources, geometry history, and runtime

Each world has four recorded geometry versions:

- **v1**: interaction geometry traced on the supplied example image. It is retained as history only.
- **v2**: earlier generated-map geometry, preserved in `production-geometry-v2-preserved.json`.
- **v3**: the generated-map geometry that was active before this correction. It had overlapping site hitboxes in Haunted Marsh and Astral Peaks.
- **v4**: current generated-map geometry. It removes those overlaps and is the only version accepted by the runtime selector.

`src/client/adventure-map-source.js` checks the current production path, source binding, geometry source path, version, and image hash metadata. `src/client/main.js` draws the selected production image and registers v4 world coordinate layers. `src/core/navigation.js` consumes the same per-world geometry for traversability, guards, anchors, bridges, and site approaches. The complete v1–v4 source and geometry record for every stable world ID is in [per-world-map-source-geometry-v4-20261022.json](per-world-map-source-geometry-v4-20261022.json).

The previously cited individual `*-current-production-geometry.png` files are preserved but are not current geometry evidence: they show reference geometry v1. The v3 contact sheet is a historical pre-fix rendering. Use the newly generated [v4 production-map and geometry contact sheet](adventure-map-production-geometry-v4-contact.png) and the twelve PNG overlays in `production-geometry-v4-overlays/`.

## Per-world reconciliation

The reference column identifies the supplied visual example only. Runtime uses the production image in the third column and the matching v4 geometry below it. Each evidence link overlays the current v4 footprints, approaches, roads, hazards, bridges, and anchors on that exact PNG.

| Stable world ID | Reference example | Runtime production image | Active v4 geometry and landmark roles | Per-world evidence |
| --- | --- | --- | --- | --- |
| grasslands | `01_Vast_Map_Grasslands_Sunny.png` | `assets/derivatives/adventure-world-maps-generated-20261020/grasslands-adventure-v1.png` | 15 water cells, 6 cliffs, 3 crossings, 3 roads; river citadel, cliff sanctuary, windmill, mine camp, farmstead, standing-stone shrine | [overlay](production-geometry-v4-overlays/grasslands-production-geometry-v4.png); 20/20 layouts |
| tundra | `02_Vast_Map_Glacial_Tundra_Blizzard.png` | `assets/derivatives/adventure-world-maps-generated-20261020/tundra-adventure-v1.png` | 12 cliffs, 0 crossings, 3 roads; mountain citadel, icebound statue, sawmill camp, gold mine, cliff lodge, glacier shrine | [overlay](production-geometry-v4-overlays/tundra-production-geometry-v4.png); 20/20 |
| haunted-marsh | `03_Vast_Map_Autumn_Marsh_Thunderstorm.png` | `assets/derivatives/adventure-world-maps-generated-20261020/haunted-marsh-adventure-v1.png` | 7 bog cells, 3 cliffs, 0 crossings, 3 roads; necropolis keep, haunted stone grove, marsh windmill, sunken quarry, marsh village, lantern shrine | [overlay](production-geometry-v4-overlays/haunted-marsh-production-geometry-v4.png); 20/20 |
| desert-volcano | `04_Vast_Map_Desert_Volcanic_Sandstorm.png` | `assets/derivatives/adventure-world-maps-generated-20261020/desert-volcano-adventure-v1.png` | 4 water cells, 10 lava cells, 7 cliffs, 0 crossings, 3 roads; sandstone palace, skull cave, oasis mill, mine entrance, caravan quarter, sun temple | [overlay](production-geometry-v4-overlays/desert-volcano-production-geometry-v4.png); 20/20 |
| underworld | `05_Vast_Map_Subterranean_Underworld_Cavern.png` | `assets/derivatives/adventure-world-maps-generated-20261020/underworld-adventure-v1.png` | 7 water cells, 5 cliffs, 0 crossings, 3 roads; fortress district, serpent-skull cavern, crystal watermill, gold works, mushroom grotto, crystal altar | [overlay](production-geometry-v4-overlays/underworld-production-geometry-v4.png); 20/20 |
| feywild | `06_Vast_Map_Sylvan_Cherry_Blossom_Feywild.png` | `assets/derivatives/adventure-world-maps-generated-20261020/feywild-adventure-v1.png` | 2 water cells, 4 cliffs, 0 crossings, 3 roads; sylvan city, mossy stone circle, grove mill, crystal quarry, woodland homes, spring shrine | [overlay](production-geometry-v4-overlays/feywild-production-geometry-v4.png); 20/20 |
| archipelago | `07_Vast_Map_Tropical_Archipelago_Monsoon.png` | `assets/derivatives/adventure-world-maps-generated-20261020/archipelago-adventure-v1.png` | 73 water cells, 2 cliffs, 4 sandbar/causeway crossings, 2 roads; harbor city, island temple, shore mill, volcanic mine cave, island village, beacon shrine | [overlay](production-geometry-v4-overlays/archipelago-production-geometry-v4.png); 20/20 |
| mesa-savanna | `08_Vast_Map_Highland_Mesa_Canyon_Savanna.png` | `assets/derivatives/adventure-world-maps-generated-20261020/mesa-savanna-adventure-v1.png` | 10 cliffs, 0 crossings, 3 roads; mesa citadel, fossil arch, savanna mill, canyon mine, watchtower, stone-circle shrine | [overlay](production-geometry-v4-overlays/mesa-savanna-production-geometry-v4.png); 20/20 |
| astral-peaks | `09_Vast_Map_Celestial_Cloud_Peaks_Astral.png` | `assets/derivatives/adventure-world-maps-generated-20261020/astral-peaks-adventure-v1.png` | 12 cliffs, 0 crossings, 3 roads; observatory city, moon arch, cloud mill, crystal quarry, high-aerie roost, lunar gate | [overlay](production-geometry-v4-overlays/astral-peaks-production-geometry-v4.png); 20/20 |
| blood-moon | `10_Vast_Map_Blood_Moon_Wasteland_Eclipse.png` | `assets/derivatives/adventure-world-maps-generated-20261020/blood-moon-adventure-v1.png` | 8 lava cells, 6 cliffs, 0 crossings, 3 roads; eclipse fortress, red obelisk, ash mill, crystal mine, creature den, fire shrine | [overlay](production-geometry-v4-overlays/blood-moon-production-geometry-v4.png); 20/20 |
| jade-karst | `11_Vast_Map_Jade_Bamboo_Karst_Clean.png` | `assets/derivatives/adventure-world-maps-generated-20261020/jade-karst-adventure-v1.png` | 10 water cells, 6 cliffs, 2 crossings, 3 roads; karst palace, cliff pagoda, terraced mill, river mine, bamboo hamlet, waterfall shrine | [overlay](production-geometry-v4-overlays/jade-karst-production-geometry-v4.png); 20/20 |
| sunken-jungle | `12_Vast_Map_Sunken_Jungle_Ruins_Ziggurat.png` | `assets/derivatives/adventure-world-maps-generated-20261020/sunken-jungle-adventure-v1.png` | 17 water cells, 4 cliffs, 3 crossings, 3 roads; jungle temple settlement, stone ruin, river waterwheel, mine cave, canopy village, blue river shrine | [overlay](production-geometry-v4-overlays/sunken-jungle-production-geometry-v4.png); 20/20 |

The matrix includes each map's exact SHA256 and dimensions, the complete geometry for v1/v2/v3/v4, all six site rectangles and approaches, terrain masks, bridge cells and banks, road traces, anchors, and the corresponding overlay path. The source manifest verifies all retained reference, production-map, and separate terrain PNG files against their recorded bytes and hashes.

## Geometry and gameplay repair

| World | Site | v3 rectangle | v4 rectangle | Entrance |
| --- | --- | --- | --- | --- |
| Haunted Marsh | dwelling | `[0,1,3,2]` | `[0,1,2,2]` | `[3,1]` preserved |
| Astral Peaks | ruin | `[9,4,3,2]` | `[9,4,2,2]` | `[8,5]` preserved |
| Astral Peaks | shrine | `[10,3,2,3]` | `[11,4,1,2]` | `[12,5]` preserved |

These hitboxes now identify separate painted landmarks. All six site rectangles are checked for pairwise overlap, and every site has a distinct interaction tile; both invariants run in the data authoring script and Adventure regression suite. The 240-layout check also validates safe starts, all six resource/guard anchors, site approaches, bridge deck continuity and banks, hazard masks, route reachability, and unique seeded placements. Astral Peaks gold stays at `[13.5,5.5]`; cell `[13,5]` is open and reachable in every layout.

The generated landscape remains static environment art. Functional site hotspots, claim status, rewards, traveler/mount placement, caches, guards, and encounter outcomes come from campaign state. A decorative background building alone does not imply ownership or a claimed reward.

## Save migration and visible-controls verification

Adventure save geometry is now v4. `src/core/campaign.js` accepts versions 1, 2, and 3, keeps stable world IDs, and writes v4. For valid v3 saves, it retains the current hero position, discoveries, claims, caches, resolved guards, resources, and valid pending encounter packs. Invalid or disconnected positions and invalid pending encounters use safe recovery. Existing v1/v2 remapping remains; malformed present versions remain errors rather than resetting campaigns.

The migration suite verifies both a valid v3 encounter stays on its existing guard cell with its pack and progress intact, and an invalid v3 position is recovered without dropping visits, claims, caches, or resources. Earlier v1/v2 preservation tests continue to pass.

On isolated origin `http://127.0.0.1:41837/`, an existing v3 campaign was opened after the source change, saved through the visible Save Campaign control, reloaded, and continued. The world remained Grasslands; the UI retained 516 gold, 110 XP, and 17 army units, with explored Town, Shrine, and Mine. Runtime DOM reported the generated Grasslands image for both terrain and geometry source, map version 4, and board/registration v4. The origin is isolated; the production save origin was not opened or reset.

One visible-controls natural journey used the Sunlit Riverlands controls for travel, a Shrine lesson, water crossing, cache/site rewards, guard battle and reward settlement, save, and reload. The eleven other worlds have full layout/geometry coverage and rendered-map overlay review, but no new full natural journey is claimed for each of them.

## Viewport and appearance review

The open-inspector Adventure scene was checked at the requested landscape sizes. The browser rounds the two compact document client widths to 826 and 934 CSS pixels. The complete image fits the map pane at all three sizes, and the mounted horse/rider stays inside the pane. Screenshots are under `live-run-v4/evidence/`.

| Requested size | Document client | Map bounds | Inspector bounds | Mounted actor bounds |
| --- | --- | --- | --- | --- |
| 825×375 | 826×375 | `[0,36.48,537.6,302.24]` | `[537.6,54,280,281.2]` | `[340.34,92.61,87.89,85.86]` |
| 933×424 | 934×424 | `[0,30.52,645.6,362.96]` | `[645.6,54,280,306]` | `[417.96,113.97,87.89,85.86]` |
| 1280×720 | 1280×720 | `[0,100.83,922,518.35]` | `[922,72,350,568]` | `[616.63,254.2,87.89,85.86]` |

All map edges remain visible with the inspector open. The refreshed renders show the production landscape at the map pane's full 16×10 source aspect, without compact map cropping or the prior edge darkening. Fog remains bounded at 0.32 opacity. The generated map contact sheet and v4 overlays were reviewed against the supplied examples for landscape quality and composition, while site/hazard/crossing geometry was judged against the actual generated map and gameplay requirements. This is agent visual review, not owner acceptance.

## Verification and remaining gaps

- `node --test tests/adventure-worlds.test.mjs` — 21/21 pass.
- `node --test tests/*.test.mjs` — 254/254 pass, 0 failed.
- All 12 maps, all 12 × 20 deterministic layouts (240 total), and all 12 current image/geometry bindings are covered. The production map images and geometry overlays are in the v4 evidence set.
- Map generation prompts, provider receipts, or other per-map generation records were not found with the twelve PNGs. The image files are preserved and their hashes are verified; provenance remains incomplete.
- Only the Sunlit Riverlands journey is claimed as a complete natural visible-controls journey. Other worlds have deterministic and visual geometry evidence, not full natural-play evidence.
- Owner visual acceptance and the independent desktop verification of the entire game remain open. The final snapshot APK has not been built; device verification and owner acceptance remain later gates.
- No reference or generated map, save, prior evidence, or unrelated dirty work was deleted. No build, APK, device, provider, purchase, or Git action was performed.
