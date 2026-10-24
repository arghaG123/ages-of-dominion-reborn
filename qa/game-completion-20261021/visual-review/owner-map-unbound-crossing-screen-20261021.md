# Unbound Adventure owner-map crossing screen — 21 October 2026

**Classification: open prebinding defect screen; no new runtime or gameplay PASS.** The current source-grid report lists twelve worlds. Four are runtime-bound (Grasslands, Feywild, Jade Karst, Underworld); all eight unbound worlds have six registered sites and zero bridge definitions. This is a diagnostic data count, then checked against the displayed owner-source grids.

| Unbound world | Blocked cells | Bridge definitions | Current source-grid observation |
|---|---:|---:|---|
| Tundra | 0 | 0 | Several ice channels and at least two visible bridge decks; collision and deck cells are unclassified. |
| Haunted Marsh | 3 | 0 | Stone crossings pass through wetland channels; current water/route registration needs source tracing. |
| Desert Volcano | 3 | 0 | Rope bridges cross canyon gaps; current geometry has no registered decks. |
| Archipelago | 38 | 0 | Multiple islands are connected by stone and timber crossings; water blockers exist but no bridge cells/banks are registered. |
| Mesa Savanna | 0 | 0 | Bridge requirement is not settled from the current screen; classify cliffs, water, roads, and any passable causeways before deciding. |
| Astral Peaks | 0 | 0 | Elevated stone viaducts and valley crossings are visible; their walkable decks and safe banks are not registered. |
| Blood Moon | 0 | 0 | No clear water-crossing system is evident in this screen; classify fortress spans, cliffs, and roads rather than assuming bridge definitions are needed. |
| Sunken Jungle | 5 | 0 | Western rope bridge, central stone causeway, and eastern timber crossing are visible. See the [detailed Sunken Jungle audit](sunken-jungle-owner-map-site-misalignment-audit-20261021.md). |

The source grids show obvious crossing structures in at least six of the eight unbound paintings, while those six currently have no bridge definitions. In particular, zero blockers in Tundra and Astral Peaks do not establish safe traversal through their visible icy/valley channels. The map art, collision mask, deck cells, and approach cells need one shared source-coordinate trace.

## Required next work

For each unbound painting, trace roads, water/cliffs, every visible crossing, six semantic sites, safe approaches, hero start, hazards, and dynamic anchors against its exact source pixels. Add a bridge definition only where the art shows a traversable bridge; mark any map with no bridge as a deliberate source-specific classification. Register water and cliff blockers without blocking painted decks. Do not copy generated-map coordinates blindly.

Before enabling each owner painting, run later-authorized natural visible-control journeys through all reachable sites and registered crossings, save/reload the position and discoveries, and inspect the actual renderer at the required desktop and compact viewports. Keep binding, geometry, natural journey, persistence, and visual acceptance as separate leaves.

Evidence: current qa/game-completion-20261021/visual-review/owner-map-source-grid-audit-20261021/report.json and its twelve world grids. The owner grids are source-coordinate diagnostics, not a certification of full map registration. Whole-game status remains INCOMPLETE.

