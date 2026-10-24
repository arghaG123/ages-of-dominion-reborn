# Gemini High closeout — 23 October 2026

## Result

| ID | Disposition |
|---|---|
| H1 | verified unchanged. M03 dense-city redesign stays `DEFERRED_OWNER`. |
| H2 | verified unchanged. The earlier readability repair still holds at 825×375, 933×424, and 1280×720. |
| H3 | fixed. On short landscape the tactical deployment tray covered the legal-cell centers. It now sits in the lower-right, and all 11 centers stay clear. |
| H4 | verified unchanged |
| H5 | verified unchanged |
| H6 | verified unchanged. The building cue still names the next usable control. |

Luna’s Critical handoff was finished before this edit. `qa/priority-repair-20261023/luna-critical/c1-c2-c3-verification-and-repairs-20261023.md` records C1, C2, and C3 PASS and `overallPass: true`. Luna’s Kingdom dock stays clear of `nav:war`. Continue still clears a rejected-import fault. `src/client/game.css` is still Luna’s copy.

This pass edited presentation CSS and the responsive test that locks it. `src/core/` was not edited. Core formulas, save schema, costs, balance, and production Adventure map geometry are unchanged. Day 1 stays unwalled. The existing Market stays the trade surface. The 12 approved Adventure maps stay. No Git publication, paid generation, asset-set replacement, APK build, device test, or consolidated status edit.

## Changed files

| File | SHA256 | Bytes | Change |
|---|---|---|---|
| `src/client/polish.css` | `def880c939b300d12bbf3c295b23ca7e7b028f97dfeceab81d5f0a5e29106581` | 119827 | Short-landscape tactical tray uses the same selector as the desktop width rule, then pins the tray to the lower-right at `min(340px, 36vw)`. |
| `tests/visual-responsive-20261018.test.mjs` | `8a9c06e6a2f439fa3f4a067965f660c5ce7785e9d3a549c842bc44d928719508` | 34510 | The short-landscape deployment test now requires that selector, width, and wrapping card names. |

Files remeasured and left as they were:

| File | SHA256 | Bytes |
|---|---|---|
| `src/client/main.js` | `7a1f82867f8d1a8a16c5eaa17512789c5c6963274fbcc955a6f4a1000214d491` | 294184 |
| `src/client/game.css` | `d1fd3633d9a8bd6ce5342e97a6ac2f9645d14ff7dcb1cf7ac9e57dcfc48c275d` | 37566 |
| `src/client/screen-presentation.js` | `e9e7b484df56a7483022c766ae04db6f3cc61599637e3873969da5e619fba09e` | 9548 |

The first tray edit used a weaker selector. The live probe still showed a full-width tray because `#app[data-view="tactical"] #scene-ui.game-status.battle-deployment { width: auto; max-width: none; }` won. The repair that shipped repeats that selector inside the short-screen media query. The camera and `wideBoardCamera` were left alone: shrinking the board to clear a full-width tray letterboxes the field.

## Live review

Isolated `?audit` Stone Knight, new campaign, headless Chrome. The user save on port 4174 was not opened.

Two full passes on `http://127.0.0.1:52978`. Both passes recorded zero page errors. Screen measurements match after the fresh-campaign upcoming-enemy wording is set aside. `probe-runs.json` holds both passes. Pass 1 screenshots are the `after-*` files. The 825×375 tactical shot is identical across passes (`563189` bytes, SHA256 `845ec0274643c7fbd703c9fc178403b9105551068f66c3dbe18906025b59d274`). The 1280×720 tactical shot differs by 10 bytes between passes; the measured tray, cell count, and controls match.

A separate cell probe, `cells-probe.json`, repeated the legal-cell measurement at all three sizes after the repair: 11 visible centers, 0 covered, no miss. The pre-repair cell measurement is `cells-before.json`.

Node, after the last source edit:

- Focused `tests/screen-presentation.test.mjs`, `tests/visual-responsive-20261018.test.mjs`, `tests/defense-wave-presentation.test.mjs`: 63 tests, 63 pass, 0 fail. Log: `C:\Users\pupan\AppData\Local\Temp\grok-goal-9d38cef0b19e\implementer\high-focused-tests.log`.
- `node --test tests/*.test.mjs`: 300 tests, 300 pass, 0 fail. Log: `C:\Users\pupan\AppData\Local\Temp\grok-goal-9d38cef0b19e\implementer\node-test.log`.

## Rows

| ID | Status | What was checked | Evidence |
|---|---|---|---|
| H1 | verified unchanged | Day 1 host is `data-walls="unbuilt"`, `data-walls-phase="none"`, wall stamps `0`, at 825×375, 933×424, and 1280×720. The tutorial plot sits on open grass. Scenic huts and the riverside fence are ground art. The Stone Town Hall stays on its painted yard. | `after-kingdom-825x375.png`, `after-kingdom-933x424.png`, `after-kingdom-1280x720.png` |
| H2 | verified unchanged | Closed Kingdom useful world is 0.9051, 0.9260, and 0.9658. Stage drawing size equals each viewport. Terrain fill is 1. Panel is closed. Primary controls sampled on these screens are at least 48×48 CSS px, and each center hits the named control. Kingdom nav is 48×48 at 825×375 and 48×50 at 1280×720. The dock does not overlap `nav:war`. Resource amounts 250, 250, 160, and 150 are unclipped. | Kingdom, forge, adventure, army, tactical, and defense shots below. `probe-runs.json`. |
| H3 | fixed | Before the repair, at 825×375 the tray was y=226 h=131 and covered all 11 legal-cell centers. At 933×424 it covered 10 centers, and cell 2,7 hit a button. At 1280×720 the tray was already y=582 h=120 with 11 centers clear. After the repair the short tray is lower-right: 825×375 tray x=520 y=203.5 w=297 h=163.5, 11 centers clear; 933×424 tray y=264 h=152, 11 clear; 1280×720 unchanged, 11 clear. Allied cards are Clubman ×12 (selected) and Slinger ×8. Opponents on the field are Dire Wolf 4, Bandit 3, and Cave Bear 2. Start Battle and Cancel setup self-hit. At 825×375 they are 85×48 and 90×48. At 1280×720 both are 128×48. Cancel setup returns to War. Defense prep `start-siege` is 252×48, center-hits itself, and opens a paused siege: selected `Paused · siege · Wave 1 of 5 · core 400`, HUD `Prepare your defense` / `0 / 5 waves · 400 gate HP`, session waves 5, cleared 0, core 400, paused, time 0, 2 towers, 0 enemies. Lane pads D3–D8. Deploy actions name the hero and the owned Clubman ×12 and Slinger ×8 stacks. | Before: `before-tactical-825x375.png`, `cells-before.json`. After: `after-tactical-825x375.png`, `after-tactical-cells-825x375.png`, `after-tactical-cells-933x424.png`, `after-tactical-cells-1280x720.png`, `after-tactical-1280x720.png`, `after-defense-prep-825x375.png`, `after-defense-live-825x375.png`, `after-defense-live-933x424.png`, `after-defense-live-1280x720.png`, `cells-probe.json`. |
| H4 | verified unchanged | Empty Stone Knight: cloth body, six empty sockets (`scene-hero-slot:helm`, `weapon`, `offhand`, `armor`, `boots`, `accessory`). Sockets are 48×48 at 825×375 and 933×424, and 64×64 at 1280×720. Message lists every socket as empty. Forge message is `Inventory: 0 items.` The panel says an Armory is required. `forge-return-kingdom` is 234×48 at 825×375 and 933×424, 278×48 at 1280×720, center-hits itself, and returns the view to kingdom at each size. Army message is `Army 2/2`. Owned stacks are the melee stack of 12 and the ranged stack of 8, shown in deployment as Clubman ×12 and Slinger ×8. `army-codex:wolf` reads `Wolf Available` and does not overlap Save. | `after-hero-825x375.png`, `after-hero-933x424.png`, `after-hero-1280x720.png`, `after-forge-825x375.png`, `after-forge-933x424.png`, `after-forge-1280x720.png`, `after-army-825x375.png`, `after-army-933x424.png`, `after-army-1280x720.png` |
| H5 | verified unchanged | Enter Adventure opens the grasslands world. Hero is at x=6, y=5, `atTown` false. Message: `Road steps cost 1. 3 marked water crossings connect the traversable banks. Site footprints stay blocked.` The four shortcuts are 48×48 and each center hits its own control. `adventure-quick:quests` opens the story panel, selected `Choose a rival`. Map geometry was not edited. | `after-adventure-825x375.png`, `after-adventure-933x424.png`, `after-adventure-1280x720.png`, `after-adventure-quests-825x375.png` |
| H6 | verified unchanged | At 825×375 the closed kingdom says `Next: Select the highlighted empty site.` The highlighted plot click selects `P01: empty plot level 0`. The cue becomes `Next: Choose a building.` `build-picker:P01` is 243×48 and the center hit is that button. After the click the cue is `Next: Build a Lumber Camp.` `build:P01:lumber` is 117×75.39, text `Build Lumber Camp 25 15`, and the center hit is that button. The same site cue is in the kingdom message at 933×424 and 1280×720. | `after-kingdom-site-825x375.png`, `after-kingdom-picker-825x375.png` |

## Interactions named above

- Kingdom plot P01 at 825×375 opens `build-picker:P01`, then `build:P01:lumber`.
- Forge `forge-return-kingdom` at 825×375, 933×424, and 1280×720 returns the view to kingdom.
- Adventure `adventure-quick:quests` at 48×48 opens the story panel.
- Tactical `cancel-battle-setup` returns to War.
- Defense `start-siege` at 825×375 starts the paused Campaign Siege and shows wave 1 of 5 and core 400.
- Kingdom `nav:war` center-hits itself and does not overlap the dock.

## M03 dense-city redesign

`DEFERRED_OWNER`. Day 1 stays unwalled. Lumber Camp remains the real building with its 25 wood and 15 stone price. No Marketplace facility was added.

## Acceptable differences

- Day 1 has no finished wall.
- Lumber Camp is the real production building. The picker shows its 25 / 15 price.
- The existing Market remains the trade surface.
- The empty Stone Knight wears cloth, with six empty sockets.
- Chapter, biome, roster, and equipment follow this new Stone campaign. Upcoming-enemy order differs between fresh campaigns.
- The hero stands on the existing road. No convoy or extra camera was added.

## Medium notes for Grok

Left in place:

- D1. Kingdom inspector detail: thumbnail, name, production, cost, time, and upgrade feedback.
- D2. Adventure shortcut hierarchy copy. The four shortcuts already meet 48×48.
- D3. Defense wording. The paused HUD says `Prepare your defense` and `0 / 5 waves · 400 gate HP` while the selected title says `Wave 1 of 5`. Both match this paused time-0 session. The existing defense-wave test expects that time-0 title.
- D4. Skill, spell, affordability, and inventory comparison.
- D5. Army roster clarity. Owned stacks stay on the roster. The center muster showcase is separate from the owned Clubman and Slinger stacks. The Wolf codex entry is available, not owned.
- D6. Story, quest, settings, and recovery wording beyond the building-tutorial cue.
- D7. Shared secondary icon and type sizing.
- Extra clarity note: at 1280×720 the deployment card names still use a single-line ellipsis. Portraits, counts, and the field labels distinguish the stacks. At 825×375 the roster scroller peeks the next opponent card; Clubman and Slinger are fully named, and the field labels name Dire Wolf, Bandit, and Cave Bear.

## Core defects for Luna

None reproduced. Combat math, save schema, costs, balance, and map geometry were not changed.

## Limits

An active tactical round’s attack effect was not played. Deployment showed the selected ally, both sides, and the legal cells. The paused siege showed the lane, wave, and core. No effect was invented.

Older `before-kingdom-site-825x375.png`, `before-forge-825x375.png`, and `before-army-1280x720.png` remain from the earlier readability repair. This pass used the live pixels and the tactical before/after files named above.
