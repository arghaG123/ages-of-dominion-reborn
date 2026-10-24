## 21 October update — Jade Karst added to live owner-source binding

Current src/data/adventure-worlds.json has three matching runtimeFile/owner-file bindings: Grasslands, Feywild, and Jade Karst. Jade Karst’s source-coordinate trace, six site approaches, river mask, two bridge decks, and fresh isolated natural-browser route/reload were reviewed in [the Jade Karst report](jade-karst-owner-map-registration-review-20261021.md). Nine worlds remain unbound to their owner paintings. This updates the source-binding count only; full Adventure and whole-game visual, journey, independent-desktop, package, device, and owner acceptance stay open.
## Earlier 21 October update — Feywild added to live owner-source binding before Jade Karst

The earlier count was accurate at that checkpoint. src/data/adventure-worlds.json then had two matching runtimeFile/owner-file bindings: Grasslands and Feywild; Jade Karst is now the third. Feywild’s source-coordinate trace, six site approaches, two bridge crossings, and a fresh isolated natural-browser route/reload were reviewed in [the Feywild report](feywild-owner-map-registration-review-20261021.md). Ten worlds remain unbound to their owner paintings. This updates the binding count only; full Adventure and whole-game visual, journey, independent-desktop, package, device, and owner acceptance stay open.
# Adventure owner-map source reconciliation — 21 October 2026

**Classification: independent source and visual audit; Adventure and whole game remain INCOMPLETE.** This audit records which image the current runtime actually uses and whether the existing 12-world browser report proved the owner-selected paintings. It does not change game source, run tests, build an APK, or perform device/owner acceptance.

## Binding owner direction

The owner-selected campaign art is recorded in the **file** property of each entry in **src/data/adventure-worlds.json**. The 20 October status and handoff say that all 12 owner-selected clean paintings are campaign worlds and that Adventure paints the chosen owner map. The source check below contradicts that implementation claim. The original status statements are retained as history; this reconciliation supersedes them.

## Current source path

In **src/client/main.js**, **campaignMapImage()** at line 646 returns **mapFile || terrainFile || file**. The campaign picker uses this selector at lines 4045 and 4067. The live Adventure ground selector at lines 613–623 likewise prefers **mapFile** and then **terrainFile**. At lines 2125–2126, the rendered terrain attribute is assigned from those generated fields while the owner-selected **file** is placed in a separate reference attribute.

All 12 current data entries have both **file** and **mapFile**. Independent SHA-256 recomputation confirms **0 of 12 runtime-selected files match their owner-selected file**. The existing source inventory is in [owner-vs-runtime-adventure-map-sources-20261021.json](owner-vs-runtime-adventure-map-sources-20261021.json); it records both paths, byte sizes, dimensions, and hashes. The current registered source transform is the same flat **[86, 0, 0, 76.8, 0, 0]** matrix for all 12 worlds.

## What the 12-world live report proves

The 21 October live report has 12/12 passed rows, 12 saved reloads, zero browser errors, and zero failed responses. That is useful bounded evidence that the current generated maps load, a legal route can be committed, the minimap uses the same generated source, and the selected world/position persists through reload.

It does **not** validate the owner-selected image: the runner explicitly asserts that the rendered source ends with **world.mapFile**, and that both minimap layers use **world.mapFile**. Each report row records a generated derivative path. The runner and result are [adventure-minimap-map-art-live-20261021.mjs](adventure-minimap-map-art-live-20261021.mjs) and [report.json](adventure-minimap-map-art-live-20261021/report.json). Treat those results as generated-map runtime evidence, not owner-map visual acceptance.

## Visual and registration finding

The owner Grasslands painting is 1376×768, while the current Grasslands runtime derivative is 1672×940. Direct visual comparison shows different compositions. The current navigation/site overlay projected onto the owner painting places the Town region over the northern ridge and other named interaction regions away from several corresponding painted landmarks. See the [12-world current-geometry screening overview](owner-map-current-geometry-contact-overview-20261021.jpg), the [owner-vs-runtime source contact sheet](owner-vs-runtime-adventure-map-sources-20261021.png), and the [Grasslands current-registration overlay](grasslands-owner-map-current-geometry-overlay-20261021.png). The downsampled 12-world overview is a screening view only; it does not close detailed per-world tracing or interaction checks.

Changing **mapFile** to **file** without registration is unsafe: the current browser and natural-journey evidence exercises generated-map paths, and the owner-file imagery has not been shown to support those same water masks, bridge cells, site footprints, approaches and anchors. At minimum, the Grasslands overlay already shows that the current site registration cannot be accepted for the owner painting. The other 11 owner-map geometries are unverified, even where their generated-map movement tests pass.

## Required next repair and acceptance

Before an owner painting can be called runtime-bound, register each of the 12 maps against its actual source: trace its terrain/water/cliffs, roads and crossings; place its six sites, approaches, resources, guards and hero anchors against visible landmarks; and confirm the source-to-grid transform and hit regions. Then make the picker, stage, map interactions, fog/minimap and edge treatment use that same owner file. Keep generated-map results as separate historical evidence.

For each world, verify actual rendered pixels and landmarks, natural travel, every relevant crossing and site interaction, save/reload continuity, and phone/desktop viewports. Preserve the complete 12-world scope. A loaded image, matching generated-map hash, route regression, broad contact sheet, or passing Node suite alone cannot close owner-map appearance or geometry.

**Current disposition:** all 12 owner-selected maps are present in data, but 0/12 are the current runtime background source; source registration and owner-map visual acceptance are OPEN. Whole desktop completion, final APK, later device QA, and owner acceptance remain distinct gates.
Fresh checksum and browser-row reconciliation is recorded in [adventure-owner-map-runtime-source-recheck-20261021.json](adventure-owner-map-runtime-source-recheck-20261021.json). It captures the current owner/runtime hashes and every live image/minimap, route, and reload row for all 12 worlds.

## Fresh isolated runtime source verification — 21 October 2026

A second, fresh browser pass used a separate temporary browser context for each world and the visible New Campaign → world selection → Begin → Hero → Valley → Adventure controls. For all 12 correctly identified worlds, both the picker preview and Adventure stage loaded the generated mapFile; both minimap terrain layers also referenced that same generated file. The owner-selected file remained only in reference metadata. Owner-file matches: 0/12 in the picker, 0/12 in the Adventure stage, and 0/12 in the minimap. Browser-error worlds and failed-response worlds: 0/12.

This pass captures source selection and entry into Adventure only. It does not claim a route, site interaction, save/reload, source geometry, or visual acceptance pass. Twelve 1280×720 captures are retained beside the [fresh live report](adventure-owner-map-runtime-live-recheck-20261021/report.json); the [Grasslands runtime capture](adventure-owner-map-runtime-live-recheck-20261021/grasslands-1280x720.png) visibly renders the generated-map composition. The browser runner is [adventure-owner-map-runtime-live-recheck-20261021.mjs](adventure-owner-map-runtime-live-recheck-20261021.mjs). The test profiles were temporary and isolated; the existing save/profile was not opened.


## Owner-map bridge candidates absent from current topology — 21 October 2026

Review of the actual selected owner paintings found two actionable feature-registration gaps. The current runtime does not display these owner files, so these are owner-map registration requirements and candidate functional mismatches, not claims about the generated maps’ current movement behavior.

| World | Owner painting evidence | Current navigation data | Required next verification |
|---|---|---|---|
| Archipelago | The selected painting shows several land bridges joining the islands, including a stone arch into the eastern fortified island. | **mapFeatures.playableCrossings** is 0 and **geometry.bridges** is empty; 38 cells are blocked. | Trace each visible deck, both land approaches, island land masks and water cells from the owner image; confirm natural routes can traverse every intended connection. |
| Sunken Jungle | The selected painting shows a long foreground stone bridge and additional crossings over water. | **mapFeatures.playableCrossings** is 0 and **geometry.bridges** is empty; five cells are blocked as shallow basins. | Trace every visible bridge/deck and approaches plus the surrounding basin, waterfall and cliff cells; confirm each intended crossing with a natural route. |

The owner sources are [Archipelago](../../../assets/mocks/owner-approved-vast-adventure-maps-20261020/07_Vast_Map_Tropical_Archipelago_Monsoon.png) and [Sunken Jungle](../../../assets/mocks/owner-approved-vast-adventure-maps-20261020/12_Vast_Map_Sunken_Jungle_Ruins_Ziggurat.png). Current overlays appear in [worlds 07–09](owner-map-current-geometry-rows-20261021/worlds-07-09.png) and [worlds 10–12](owner-map-current-geometry-rows-20261021/worlds-10-12.png).

The overview is not precise enough to assign cells or mark route PASS. First register the complete owner source against its actual pixel landmarks, then update the per-world topology, bind the same source in picker/runtime/minimap, and verify the deck-to-bank route naturally. Keep the current zero-crossing rows OPEN until that work is proven.


## Current 12-world topology inventory — 21 October 2026

This is a literal inventory of the current JSON registrations, not an owner-map acceptance result. Current natural route checks run against the generated runtime selector identified earlier.

| World | Water feature | Playable crossings / bridge definitions | Blocked cells | Obstacles | Site records | Road records |
|---|---|---:|---:|---:|---:|---:|
| Grasslands | Branching river | 3 / 3 | 28 | 0 | 6 | 0 |
| Tundra | None recorded | 0 / 0 | 0 | 0 | 6 | 0 |
| Haunted Marsh | Shallow bog pools | 0 / 0 | 3 | 0 | 6 | 0 |
| Desert Volcano | Isolated oasis pools | 0 / 0 | 3 | 0 | 6 | 0 |
| Underworld | Isolated crystal cavern pools | 1 / 1 | 4 | 1 | 6 | 0 |
| Feywild | Tree river, waterfall and crystal springs | 1 / 1 | 9 | 0 | 6 | 0 |
| Archipelago | Marine lagoons and deep sea | 0 / 0 | 38 | 0 | 6 | 0 |
| Mesa Savanna | None recorded | 0 / 0 | 0 | 0 | 6 | 0 |
| Astral Peaks | None recorded | 0 / 0 | 0 | 0 | 6 | 0 |
| Blood Moon | None recorded | 0 / 0 | 0 | 0 | 6 | 0 |
| Jade Karst | Winding river and waterfall | 2 / 2 | 15 | 1 | 6 | 0 |
| Sunken Jungle | Shallow jungle basins | 0 / 0 | 5 | 0 | 6 | 0 |

An empty road array does not mean the painted art has no roads; the current integrated illustrations already contain roads. The executor must trace relevant traversable surfaces from the owner file and retain data only where gameplay needs it. Likewise, “none recorded” water and zero blockers do not prove there are no cliffs or other impassable painted areas. Inspect those against the owner image before acceptance.

## All-world owner-source crossing screen — 21 October 2026

A visual screening of all four owner-source geometry strips adds potential crossing work beyond Archipelago and Sunken Jungle. Tundra shows frozen crossing routes; Haunted Marsh has wetland bridge or boardwalk cues; Mesa Savanna has rope bridges over canyon cuts; Astral Peaks has a long stone sky bridge; Jade Karst has multiple bridge forms. These are source-image screening cues, not traced or accepted deck cells. All 12 current runtime backgrounds still select generated mapFile derivatives, so current geometry counts cannot be carried over as owner-map registration.

| World | Current generated crossings / bridge records | Owner-source screening |
|---|---:|---|
| Grasslands | 3 / 3 | Existing count needs source-specific trace |
| Tundra | 0 / 0 | Frozen crossing candidate |
| Haunted Marsh | 0 / 0 | Wetland bridge or boardwalk candidate |
| Desert Volcano | 0 / 0 | Trace water, lava and cliff boundaries; no deck inferred |
| Underworld | 1 / 1 | Existing count needs source-specific trace |
| Feywild | 1 / 1 | Existing count needs source-specific trace |
| Archipelago | 0 / 0 | Multiple island bridges; exact decks OPEN |
| Mesa Savanna | 0 / 0 | Canyon rope-bridge candidates |
| Astral Peaks | 0 / 0 | Sky-bridge candidate |
| Blood Moon | 0 / 0 | Trace lava and chasm boundaries; no deck inferred |
| Jade Karst | 2 / 2 | Bridge art is visible; existing count and positions are not source-validated |
| Sunken Jungle | 0 / 0 | Multiple stone and suspended crossings; exact decks OPEN |

The coordinate-labelled 16×10 grids for all 12 owner sources are diagnostic only:

| World | Grid | World | Grid |
|---|---|---|---|
| Grasslands | [grid](owner-map-source-grid-audit-20261021/grasslands-owner-source-16x10-grid.png) | Tundra | [grid](owner-map-source-grid-audit-20261021/tundra-owner-source-16x10-grid.png) |
| Haunted Marsh | [grid](owner-map-source-grid-audit-20261021/haunted-marsh-owner-source-16x10-grid.png) | Desert Volcano | [grid](owner-map-source-grid-audit-20261021/desert-volcano-owner-source-16x10-grid.png) |
| Underworld | [grid](owner-map-source-grid-audit-20261021/underworld-owner-source-16x10-grid.png) | Feywild | [grid](owner-map-source-grid-audit-20261021/feywild-owner-source-16x10-grid.png) |
| Archipelago | [grid](owner-map-source-grid-audit-20261021/archipelago-owner-source-16x10-grid.png) | Mesa Savanna | [grid](owner-map-source-grid-audit-20261021/mesa-savanna-owner-source-16x10-grid.png) |
| Astral Peaks | [grid](owner-map-source-grid-audit-20261021/astral-peaks-owner-source-16x10-grid.png) | Blood Moon | [grid](owner-map-source-grid-audit-20261021/blood-moon-owner-source-16x10-grid.png) |
| Jade Karst | [grid](owner-map-source-grid-audit-20261021/jade-karst-owner-source-16x10-grid.png) | Sunken Jungle | [grid](owner-map-source-grid-audit-20261021/sunken-jungle-owner-source-16x10-grid.png) |

Tighter crops: [Archipelago](owner-map-source-grid-audit-20261021/archipelago-crossing-detail-grid.png) and [Sunken Jungle](owner-map-source-grid-audit-20261021/sunken-jungle-crossing-detail-grid.png); machine inventory: [grid metadata](owner-map-source-grid-audit-20261021/report.json). No exact deck cells are assigned. The current bridge data model includes a rectangle, traversable cells and both approaches. Acceptance must confirm a bank-to-bank route traverses every deck cell orthogonally; current stepCost rejects diagonal entry to or exit from a marked bridge cell. First trace each owner source's actual ground, water/cliffs/gaps, crossings, six site footprints and approaches, resources/guards and hero anchor; then bind one source/registration in picker, stage and minimap and verify natural routes and save/reload. All 12 owner-map registrations remain OPEN.

## Mesa Savanna and Astral Peaks gap-topology consequence — 21 October 2026

The new owner-source coordinate grids show rope bridges spanning canyon cuts in Mesa Savanna and a long stone bridge between elevated landforms in Astral Peaks: [Mesa grid](owner-map-source-grid-audit-20261021/mesa-savanna-owner-source-16x10-grid.png), [Astral grid](owner-map-source-grid-audit-20261021/astral-peaks-owner-source-16x10-grid.png). Current world geometry records zero blocked cells, zero obstacles and zero bridge definitions in both. The current source path installs those world-specific arrays, and adventureMap adds the six site footprints as blockers; isOpen otherwise uses the blocked set. Therefore, if either owner painting were bound with today's topology, non-site canyon/sky-gap cells would remain walkable. This is a source/data inference, not an owner-image movement run. Trace cliffs, voids, bridge decks, both approaches and surrounding land before binding; then prove natural bank-to-bank routes and off-bridge rejection.

## Close review of Tundra, Haunted Marsh and Jade Karst — 21 October 2026

The coordinate grids sharpen three all-world screening leads:

- **Tundra:** The painting shows broad frozen channels and crossing forms. Current world topology records 0 blocked cells, 0 obstacles and 0 bridges. Trace which ice is intentionally walkable and where channels/cliffs need barriers; do not assume every frozen-looking surface is either water or a bridge.
- **Haunted Marsh:** The painting shows prominent stone arches over wetland channels. Current topology has three blocked cells ([5,2], [6,2], [7,2]) and no bridge definitions. Trace both arches, water edges and approaches from the native image before deciding whether each is a traversable route.
- **Jade Karst:** The painting shows several bridge spans while current generated geometry registers two decks: [4,6]–[5,6] and [10,4]–[11,4]. A visual overlay suggests the western registered deck may sit south of its painted arch. Treat that as a suspected source-registration mismatch, not a correction: trace native pixels and approaches before changing cells.

Evidence: [Tundra grid](owner-map-source-grid-audit-20261021/tundra-owner-source-16x10-grid.png), [Haunted Marsh grid](owner-map-source-grid-audit-20261021/haunted-marsh-owner-source-16x10-grid.png), [Jade Karst grid](owner-map-source-grid-audit-20261021/jade-karst-owner-source-16x10-grid.png). These are source-screen findings only, not natural route or owner-map acceptance.

## Archipelago site-to-landmark screening — 21 October 2026

The coordinate-labelled owner-source grid exposes a clear candidate mismatch in the generated registration. The current Mill footprint is [13,5,2,2] with approach [12,5], placing it over the volcanic/dragon island; the obvious windmill is on the western island near the [4,2]–[5,3] area. The Town footprint [8,5,3,2] and approach [7,5] lie over the southern harbor channel and ship/dock area, while the prominent fortified settlement is farther north/east. These are screening comparisons, not replacement coordinates: trace each complete structure, its actual playable edge and approach against the native source before editing. The other four site records also need source-specific review. See the [Archipelago coordinate grid](owner-map-source-grid-audit-20261021/archipelago-owner-source-16x10-grid.png); source registration remains OPEN.

## Desert Volcano owner-source site and lava-mask screening — 21 October 2026

The coordinate grid reveals candidate site and landform mismatches in the selected Desert Volcano painting. Current generated registration places Town at [8,1,3,2] with approach [9,3], over the northern ridge/towers; the dominant oasis citadel is centered lower around [7,4]–[9,5]. Mine is [3,3,2,2] with approach [5,3], east of the obvious wooden mining derrick near [1,3]. Current topology blocks only [4,2], [5,2] and [6,2], with no obstacles or bridge definitions; the owner painting has extensive eastern and southern lava channels. If the owner image were bound with these arrays, lava cells outside site footprints would remain walkable. This is a source/data inference, not a live owner-image movement result. Trace the actual lava/water/cliff masks, all six footprints/approaches and the source transform before binding; then verify legal routes around hazards and to each site. See the [Desert Volcano coordinate grid](owner-map-source-grid-audit-20261021/desert-volcano-owner-source-16x10-grid.png). Keep this source registration OPEN.

## Blood Moon owner-source hazard-mask screening — 21 October 2026

The selected Blood Moon painting has extensive red lava cracks and green glowing fissures. Current generated geometry records no blocked cells, no obstacles and no bridge definitions. Since the movement map blocks only registered terrain/obstacles and site footprints, binding this owner art with the current arrays would leave cells across those visible hazards walkable. This is a source/data inference, not a live owner-image movement result. Trace lethal or impassable crack/fissure regions and any genuine crossings against the native image; confirm safe routes around them before binding. See the [Blood Moon coordinate grid](owner-map-source-grid-audit-20261021/blood-moon-owner-source-16x10-grid.png). Keep source mask and route acceptance OPEN.

## Underworld owner-source Town footprint screening — 21 October 2026

The selected Underworld painting places current Town rect [0,6,3,3] and approach [3,6] over the lower-left purple crystal/serpent-cave area. The visible settlement-like buildings cluster near the map center and a large fortified structure occupies the upper-right cavern. This is a likely site-to-landmark mismatch that requires owner-source tracing; do not move the footprint from this screenshot alone. The current owner-map route remains unverified even though generated-map bridge evidence exists. See the [Underworld coordinate grid](owner-map-source-grid-audit-20261021/underworld-owner-source-16x10-grid.png). Re-register all six sites, approaches and source-specific topology before natural interaction review.


## Superseding runtime-source recheck — Grasslands bound, 21 October 2026

The earlier **0/12** runtime-to-owner-source result is accurate for the source snapshot audited above. After the targeted repair, a fresh current-source check finds **1/12** owner paintings selected at runtime: Grasslands now has an explicit `runtimeFile` equal to its approved `file`. The other eleven still resolve to generated `mapFile` values. The current per-world comparison is in [the refreshed source-grid report](owner-map-source-grid-audit-20261021/report.json); its coordinate overlays cover the twelve selected paintings.

For Grasslands, the picker, stage, minimap layers, Spellbook backdrop and edge backdrop now use the same selected image. The 1376×768 source is registered to the 16×10 grid with transform `[86, 0, 0, 76.8, 0, 0]`; the Town, Ruin, Mill, Mine, Dwelling and Shrine sites and approaches were reviewed. Natural browser checks at 1280×720 and 825×375 claimed the Ruin and reloaded successfully. A separate campaign crossed all three registered bridges, visited every deck cell, and retained deck visits and far-bank position after reload. See the [bounded review](grasslands-owner-map-registration-review-20261021.md), [Ruin report](grasslands-owner-map-registration-live-20261021-run01/report.json), and [bridge report](grasslands-owner-map-crossings-live-20261021-run02/report.json).

This does not certify all shoreline pixels, all dynamic actors or full Grasslands mock fidelity. For each of the remaining eleven worlds, independently trace actual image hazards, roads, site geometry and approaches, bridges/banks, dynamic anchors, transform, minimap/fog and edge treatment before binding, then run natural route/site/crossing/save/reload checks. Whole Adventure and whole-game acceptance remain INCOMPLETE.

## Superseding Underworld source/runtime recheck — fourth owner painting, 21 October 2026

The earlier Underworld Town-footprint screening correctly identified a source-registration question but was not a live owner-map result. Current src/data/adventure-worlds.json binds Underworld runtimeFile to the owner-selected file. Its existing river blockers, serpent obstacle, six site regions, and two-cell bridge were reviewed against the labeled 16×10 source grid. A fresh visible-control journey crossed both deck cells to the far bank, visited the Shrine, learned Tactics 1/3, and retained position, one movement point, discovery, and the lesson after reload. The live map renderer selected the owner painting and reported one registered bridge/crossing. The source-grid diagnostic now reports 4/12 owner paintings bound at runtime.

See [Underworld review](underworld-owner-map-registration-review-20261021.md) and the refreshed [coordinate-grid report](owner-map-source-grid-audit-20261021/report.json). This supersedes the Underworld-specific “route remains unverified” and “re-register before natural interaction review” conclusions above for the tested source binding, registered bridge, Shrine/Tactics interaction, and reload only. The broader visual, remaining-map, all-journey, independent desktop, package, device, and owner gates remain open.
