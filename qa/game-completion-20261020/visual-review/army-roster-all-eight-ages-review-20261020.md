# Army roster all-age visual and natural journey review — 20 October 2026

**Result: focused all-age Army UI PASS; whole-game acceptance remains INCOMPLETE.**

## Natural journey

The same fresh campaign used visible controls to build four income sites, an Armory and a Barracks at P06; forge/equip one legal weapon and recruit one legal current-age formation in each age; advance through Future; and save/reload.

- Barracks levels 1–8 were built through the normal construction controls to expand formation capacity.
- Eight current-age formations were recruited and paid for through the Army UI: Bone Crusher, Axeman, Crossbowman, Siege Knight, Grenadier, Sharpshooter, Battle Tank and Plasma Trooper.
- The army grew from two starter stacks to ten stacks. All ten stack IDs, counts and ages plus Barracks level 8 survived save/reload.
- The live Army screen used the matching age muster background and rendered all three melee/ranged/heavy recruitment cards with loaded role art in each age.
- Army screenshots cover 825×375, 933×424 and 1280×720 in all eight ages (24 captures). The compact-layout contact sheet is `qa/game-completion-20261020/visual-review/equipment-all-ages-live/army-rosters-all-eight-ages-825x375-contact-20261020.jpg`.
- The selected formation inspector stays separate from the roster and recruitment rows. The full Future roster scroll rail exposes its first and last formation at all three viewports without page-level horizontal overflow.
- The previous centered flex row clipped its first card when the roster became wider than its viewport. It now starts at the left edge, contains horizontal swipe overscroll, and uses a gold scrollbar theme. Visual inspection of the refreshed Future capture confirms the Clubman card is fully visible at the rail start.
- The browser journey recorded zero page errors, console errors or HTTP 400+ responses.

## Mock comparison

M24's core hierarchy is present: era-specific role choices, formation cards with rank stars, army capacity and a selected-formation stat/recruit inspector. The live view arranges these around the age-specific muster scene and keeps the formation rail horizontally scrollable as the army grows; it does not claim pixel-identical positioning to the wider static mock.

## Evidence

- Runner: `qa/game-completion-20261020/visual-review/natural-all-age-equipment-live-20261020.mjs`
- Machine report: `qa/game-completion-20261020/visual-review/equipment-all-ages-live/natural-all-age-kingdom-live-20261020.json` (`passed: true`, 8 ages, 8 recruits, 10-stack reload, 89 total captures).
- All-age contact sheet: `qa/game-completion-20261020/visual-review/equipment-all-ages-live/army-rosters-all-eight-ages-825x375-contact-20261020.jpg`.
- Fresh bounded suite after the Army rail repair: `node --test tests/*.test.mjs` — **210/210 PASS**, including the 10,000-command save-stress test.

## Limits

This pass recruits one current-age role per age and verifies all three role choices render; it does not claim that every role/class kit, battle animation, mock, scene trace or journey is fully accepted. The mock-led 30-screen/18-journey review, 32-scene physical review, independent desktop gate, final snapshot APK and later device/owner gates remain open. No APK, device, release or owner acceptance occurred.
