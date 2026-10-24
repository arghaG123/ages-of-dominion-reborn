# Jade Karst water and bridge registration review — 21 October 2026

**Disposition: partial pass for two bounded natural bridge crossings; Jade map and desktop acceptance remain INCOMPLETE.** These checks validate the current source data and visible UI route flow. They do not certify the full 12-world Adventure map set, all Adventure interactions, the M01–M30 mock set, or the complete desktop game.

## Current-source repair

The old Jade mask blocked nearly every cell in row 5, which did not follow the painted winding river. The current 16×10 cell topology uses the following water cells: (13,2), (12,3), (10,4), (11,4), (12,4), (8,5), (9,5), (4,6), (5,6), (7,6), (6,7), (3,8), (4,8), (5,8), and (5,9). The bridge cells are reopened by the runtime navigation map. The cliff-face cell (4,5) is separately blocked as an obstacle.

Both bridge decks are source-registered to the current integrated map image:

- West arch: deck (4,6)–(5,6), approaches (5,5) and (3,6).
- East arch: deck (10,4)–(11,4), approaches (9,4) and (11,5).

The east deck moved up from row 5 to the visible row-4 arch. The mine guard moved off that bridge to (12,5), and the food anchor moved from the lower waterfall cell (3,8) to the adjacent dry trail cell (3,7). Bridge tiles can no longer be skipped with a diagonal step.

## Evidence inspected

The jade-karst-effective-topology-review.png overlay places current blocked cells, deck tiles, approaches, obstacles, and baseline anchors on jade-karst-adventure-v1.png. The deck cells cover the painted arches; approach markers sit on adjacent land/trail. Live route previews in run04 and run05 follow those deck cells at the current map scale. Hoof-to-deck pixel contact at fine scale is not established by these captures.

Fresh UI-driven browser runs, each in its own context:

- East bridge (adventure-jade-karst-east-bridge-full-crossing-live-20261021-run04/report.json): from (8,4), approach (9,4), then route (10,4) → (11,4) → (11,5). Commit and reload persist the far bank with saveState=committed. Motion sampling: 217 frames, 190 moving, 217 mounted, 191 distinct marker positions.
- West bridge (adventure-jade-karst-west-bridge-full-crossing-live-20261021-run05/report.json): from (8,4), approach (5,5), then route (5,6) → (4,6) → (3,6). Commit and reload persist the far bank with saveState=committed. Motion sampling: 216 frames, 189 moving, 216 mounted, 190 distinct marker positions.
- Both scripts report no browser errors or failed HTTP responses. Their passed fields apply only to bounded navigation, motion, persistence, and reload; the reports explicitly leave map and product acceptance unestablished.
- node --test tests/adventure-worlds.test.mjs: 11/11 PASS.
- node --test tests/*.test.mjs: 241/241 PASS, including the 10,000-command save stress horizon.

## Remaining Jade gates

The cell mask is a coarse gameplay approximation of a painted 16×10 map; the exact water shoreline and all off-route cells are not fully traced. The run captures do not resolve hoof contact at pixel scale, nor do they verify every resource, guard, site, seed layout, or both bridge journeys under all relevant presentation states. Run02 and run03 contain pre-current-geometry crossing evidence and must not be used as proof for the repaired topology. Review run04 and run05 for current bounded journeys.

Continue with a finer Jade shoreline and contact review, then inspect the registered barriers and natural journeys for the remaining Adventure worlds. All other mock, scene, age, gameplay, save, desktop, and release gates remain separately open. No APK build, device test, provider action, Git mutation, or owner acceptance occurred here.
