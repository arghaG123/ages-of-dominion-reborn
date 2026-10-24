# Six-slot equipment and Forge layout review — 20 October 2026

**Result: focused Future loadout and Forge layout PASS; whole-game acceptance remains INCOMPLETE.**

## Natural loadout journey

The isolated browser campaign starts in Stone and advances through all eight ages using visible game controls. It builds the four producers and Armory, forges and equips one legal current-age Knight weapon per age, enters each age's Adventure scene, and completes Town Hall and wall progression through level 8. In Future, it forges and equips Helm, Offhand, Armor, Boots and Accessory after the age-specific weapon is already worn.

- All six Future equipment IDs survive save/reload.
- The Hero figure reports six worn socket records; the Hero panel reports six filled cards with reviewed gear icons.
- Weapon continuity remains verified at all ages: the matching native-alpha item appears once on the Adventure Knight, with no generic weapon joint duplicate.
- Forge closed and inspector states were captured at 825×375, 933×424 and 1280×720. The slot rail and action area do not overlap at any size; the Forge price row fits without horizontal overflow.
- While the inspector is open, exactly one Forge action remains in the panel and no hidden action clone stays in the dock to intercept clicks.
- The final run recorded zero browser/page/console errors and zero HTTP responses at status 400+.

## Repair

The earlier captures showed the Forge action dock covering the slot rail and its price/compare buttons clipping across the scene. The Forge view now uses a bounded, scrollable right action area, wraps the resource-price row, and keeps the six-slot rail on the left. The compact Forge preview leaves clear space on short landscape screens. Re-rendering no longer leaves duplicate dock actions under the open inspector.

The Future Hero captures show the six equipped items as icon cards and worn socket records. They do **not** claim six physical body overlays: the current Future Knight plate already depicts armor and a carbine, and bespoke item art for Helm, Offhand, Armor, Boots and Accessory is not present. This pass verifies legal equipment, slot UI and persistence, not item-specific changes to the static body plate or coverage for other classes.

## Evidence

- Runner: `qa/game-completion-20261020/visual-review/natural-all-age-equipment-live-20261020.mjs`
- Machine report and 89 screen captures: `qa/game-completion-20261020/visual-review/equipment-all-ages-live/` (the added 24 captures cover Army roster screens across all eight ages and three viewports).
- Forge rail/dock rectangles and price overflow assertions are recorded in `natural-all-age-kingdom-live-20261020.json`.
- Fresh `node --test tests/*.test.mjs`: **210/210 PASS**, including 10,000-command save stress.
- The natural journey reaches age 7, Hall 8 and wall 8, then reloads with all six Future slots filled.
- All-age Army roster results are documented in `qa/game-completion-20261020/visual-review/army-roster-all-eight-ages-review-20261020.md`.

No APK, device, owner-acceptance or release action occurred. The full M01–M30/J01–J18 mock/journey gates, independent desktop acceptance, remaining art and physical scene reviews, final snapshot APK and later mobile/owner gates stay open.
