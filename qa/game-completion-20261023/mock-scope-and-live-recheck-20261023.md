# Mock scope and live recheck — 23 October 2026

## Scope decisions

- The 30 generated landscape screen references are M01–M30.
- The 12 owner-approved Adventure continent maps are a separate approved set. They are not counted among M01–M30 and need no additional mock review. Keep their current game-specific production bindings and geometry.
- Preserve truthful Stone Day 1: Walls level 0 and no finished perimeter wall. Compare the M02 wall direction only against a naturally built later state; do not fake a completed wall on Day 1.

## Current-source live observations

- M12 Bridge crossing: in the isolated local review at `http://localhost:41837/?audit`, the current Adventure view shows the registered close bridge image with the mounted live traveler. Fog remains present. The earlier naturally committed one-step movement survived Continue/reload; route feedback reports `Cross Bridge · cost 1`. The current-source live recheck below confirms the turquoise route preview, cost badge, and floating lower-right confirmation action. M12 remains open because the mock's nearby convoy/guard context is absent.
- M19 Hero equipment: the current isolated Stone Knight screen shows the real unarmored cloth body with six empty sockets. This is truthful for the empty loadout, but does not match the mock's equipped Medieval hero, named equipment, comparison panel, or stats. M19 remains open.
- M03 Stone Kingdom: the isolated test campaign naturally completed Wall level 1. Its current Day 5 view remains a circular timber palisade around a mostly empty center; the mock shows a dense town inside an integrated enclosure and a selected Sawmill inspector. The live catalog has Lumber Camp, not Sawmill. Day 1 remains untouched; M03 remains open.
- The page on `localhost:4174` is the existing user save and was not interacted with. The isolated test origin `localhost:41837` is separate.

## Bounded verification

- `node --test tests/*.test.mjs`: 295 passed, 0 failed.
- `node --check src/client/main.js`: passed.
- `src/client/main.js` remained CRLF-only after the renderer changes.
- Kingdom action-sheet repair: widened to 560px, changed to two columns, and compacted for short landscape; visually checked at 1280×720, 933×424, and 825×375. The formerly colliding cost labels now remain readable. This improves panel usability but does not close M03 scene fidelity.
- These checks and live observations do not close the remaining mocks, all-age natural journeys, package/device gates, or owner acceptance.

## Same-source Adventure recheck — 23 October 2026

- Reviewed the isolated test origin at 1280×720 after loading current source `src/client/main.js` SHA256 `6C20063077335F38BEE04BEC7F478DC5A6EB57E382BB27B595E08D4FF61AAB13`. The existing user save on `localhost:4174` was not opened or changed.
- M12 route preview: `Travel and sites` → `Travel east` showed a one-step turquoise route and endpoint on the registered bridge close-up, with the live mounted Knight and `Cross Bridge · cost 1`. Confirming it reduced movement from 5 to 4, persisted the move, and closed the explicitly requested panel. A return route was previewed, then the inspector was closed; the lower-right floating `Cross Bridge` action and cost badge appeared beside the route at `[894,660,210,48]` in the 1280×720 viewport, matching the mock's action placement. This repairs the panel disappearing immediately on open and verifies the normal route action. The target's nearby armed convoy is still absent, so the current-source M12 status is **PARTIAL**.
- M11 overview after the step: the full current world view showed the minimap, discovered Town/Shrine labels, hero/army status, resources, and travel actions. The target's separate Quests/Bag/Camp/Diplomacy tray and its lower-right army panel are absent; M11 remains partial. The 12 approved Adventure maps remain excluded from the M01–M30 mock review.
- Updated bounded checks: `node --test tests/*.test.mjs` passed 296/296; `node --check src/client/main.js` passed. `main.js` remains CRLF-only (5,318 CRLF, 0 bare LF).
- During the M12/M11 recheck, no fixtures, item grants, age changes, paid generation, or device installs were used, and the user's `localhost:4174` campaign was not opened. The isolated campaign was already a Day 5 review save; its journey is not full-campaign acceptance evidence. The later natural M03 builds are listed separately below.
- M03 real-cost construction recheck: from the isolated Day 5 save, Farm at P02, Quarry at P03, and Barracks at P04 were built through their visible cost-confirmation flows; the existing Lumber Camp at P01 was selected. All four buildings render as live plot content. The scene still has a large empty yard, timber palisade, and Lumber Camp inspector rather than the mock's dense enclosure and Sawmill/worker-output inspector. M03 remains a visual FAIL; campaign progression is truthful and Day 1 remains unchanged.
- M27 tutorial recheck: from the isolated Day 5 save, completing the Farm, Quarry, and Barracks advanced the tutorial through their natural steps with normal costs. The later live run continued into the Day 8 guard encounter; it still does not reproduce the M27 mock's early Stone Build Farm callout and matching composition, so M27 remains open.
- Follow-on natural tutorial run: after recruitment and leaving town, normal movement through the isolated seeded Adventure map found the Bandit/Wolf guard at [14,2]; choosing “Fight the guard” opened the real Stone tactical battle. This confirms step 6 is reachable through visible play, not a fixture. Before the guard was visited, the tutorial still said “Fight the guard” with no discovered marker, so its cue now says “Explore nearby roads to find a guard” until an unresolved encounter exists. Focused cue/crossing tests passed 25/25 and the complete Node suite passed 297/297. This does not close the M27 early Build Farm screenshot or visual-composition gate.
- Browser console check on the current isolated game view returned no errors.

## M03 follow-up with a naturally developed Stone Kingdom — 23 October 2026

- Continued only the isolated campaign at http://localhost:41837/?audit; the existing user campaign at localhost:4174 was not opened. Reached a natural Day 8 state and built all 17 functional plots P01–P17 through their visible cost and confirmation flow. The selected Lumber Camp, Farm, Quarry, Gold Mine, Barracks, Siege Workshop, Hero Hall and Armory states are real campaign structures; no resource grants or wall/plot geometry changes were used.
- Added a compact Kingdom inspector readout based on the existing rates(state) economy calculation. Selecting P01 exposes its reviewed resource icon and accessible Lumber Camp production: 0.45 wood per second context next to the existing upgrade cost. The UI reports the implemented economy and does not invent a worker count or call the catalog building a Sawmill.
- Rechecked the developed live pixels against 03-kingdom-stone.jpg: the selected-site details are more useful, and all built plots render as dynamic building layers inside the truthful later-age wall. The interior still lacks the mock's dense residential mass and fields, and the scene hierarchy remains visibly different. M03 therefore remains **visual FAIL / incomplete** pending a real density and composition repair.
- Added focused production attribution tests. Full `node --test tests/*.test.mjs` passed 299/299; `node --check` passed for `src/client/main.js`, `src/client/kingdom-production.js` and `tests/kingdom-production.test.mjs`. `src/client/main.js` remains CRLF-only (5,343 CRLF, 0 bare LF).
## M11 Adventure interface-only recheck — 23 October 2026

- Reviewed the current isolated Adventure screen at 1280 × 720. Per the owner clarification, this pass did not compare or re-evaluate any of the 12 approved Adventure map designs, map pixels, source bindings, or geometry.
- The live UI shows icon-and-amount resource chips, a minimap, a four-move status, the hero level/XP/mana panel, army stack/unit totals, and the real pending-guard action. The mock adds a separate lower-right four-item Quests/Bag/Camp/Diplomacy tray and a differently arranged army plaque. Current hero state has no persistent overworld HP field; I did not display fabricated HP. M11 remains **PARTIAL** for interface hierarchy and quick access.
- The current source hashes are src/client/main.js C7631321B3D9662A737FC40A76D7FD57496D0F4ACF9ECF63C88754BE291139D3 and src/client/polish.css 82EA1B46BAEE8B49EE3D1815478140BEC10EF0E058F1B718FB288E6F295D6227; helper and production-test hashes are recorded above.

## M11 quick-access live follow-up — 23 October 2026

- On the isolated 1280 × 720 Adventure screen, each icon-first accessible action routed to its existing feature: Quests opened Story and visibly scrolled the side panel to the QUESTS list; Bag opened Hero Inventory; Camp opened Travel and sites with Rest and End day visible; Diplomacy opened the Rival section. No movement, rest, end-day, recruitment, story-choice or other spending action was taken.
- Re-rendering and switching to Hero leave one tray in the DOM but hide it outside Adventure; opening the Camp panel hides it. Adventure shows exactly four actions without covering the primary travel action. The Quests route focus/scroll is now applied after the render resets panel scroll.
- Current isolated view console check returned no errors. Screenshots were inspected live and not retained as files. This pass did not re-review the 12 approved Adventure map designs, bindings, or geometry. M11 remains PARTIAL because the broader scene and army/status composition still differ from its screen mock.
- Owner direction: defer M03 dense-city composition repair for now. M03 remains a recorded visual FAIL; keep truthful Day 1 walls at level 0 and do not introduce a finished Day 1 wall.
- Latest independent disposition in `mock-design-independent-closeout-20261023.md`: 0 closed, 15 partial, 9 failed comparisons, 6 unmatched states across M01–M30.

- Latest bounded checks after the M11 shortcut repair: `node --test tests/*.test.mjs` passed 299/299; `node --check` passed for `src/client/main.js`, `src/client/kingdom-production.js` and `tests/kingdom-production.test.mjs`. The current main.js remains CRLF-only (5,388 CRLF, 0 bare LF).

## M12 crossing focus registration follow-up — 23 October 2026

- The runtime focus rectangle now matches the reviewed asset registration `[774, 223, 342, 192]`; the crossing test expectation was updated with it. Geometry check confirms both deck-cell centers and both approach-cell centers remain inside this rectangle.
- The focused crossing test passes 5/5 and the bounded Node suite passes 299/299. This is source/geometry evidence only: no current-source live M12 screenshot or natural-state visual recheck was made, so M12 remains **FAIL** until that review.
- M03 dense-city repair remains deferred by owner direction; its recorded FAIL is still open. The 12 approved Adventure map designs remain excluded from this M01–M30 screen-mock review.

## M25 Story current live review — 23 October 2026

- Rechecked the isolated review origin `http://127.0.0.1:41838/?audit` at 1280×720, on a fresh truthful Stone Day 1 campaign. The user campaign at `localhost:4174` was not opened or changed.
- The current Story screen now mounts Chronicle, Objectives, and Settings controls. The chapter plaque, resource strip, objective list, and equipment/milestone panels are legible without the previous header overlap. The Settings route opens the existing Settings view; no preference was changed. No quest reward, economy action, age change, item grant, or campaign transaction was performed.
- The live campaign is Chapter I while the M25 reference depicts Chapter IV. This confirms the layout repair in a real current-source screen but does not match the mock's chapter state or complete visual composition. The screenshot was inspected live and not retained as a file. M25 remains **PARTIAL**; the prior closeout's statement that the updated HUD had not been viewed is superseded by this bounded recheck.
- `node --test tests/*.test.mjs`: 299 passed, 0 failed. `node --check src/client/main.js`: passed. `src/client/main.js` remains CRLF-only (5,389 CRLF, 0 bare LF; SHA256 `a7d884b2a313c258e765e1a4849958ea3de99abb488cbc92e814cba94eb5ceeb`).
- This follow-up does not change the 30-mock disposition totals: 0 closed, 15 partial, 9 failed comparisons, and 6 unmatched states. The 12 separately approved Adventure map designs were not reviewed again. Whole-game acceptance remains **INCOMPLETE**.
