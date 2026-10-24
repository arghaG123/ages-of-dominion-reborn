# M23 inventory mock comparison — 20 October 2026

**Result: item-grid and selected-comparison presentation PASS on desktop, PARTIAL on compact landscape; whole-game acceptance remains INCOMPLETE.**

## Reviewed pixels and evidence

- Approved target: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/23-inventory.jpg` (1360×768).
- Current selected-item captures: `qa/game-completion-20261020/visual-review/equipment-all-ages-live/forge-item-selected-825x375.png` and `forge-item-selected-1280x720.png`.
- Natural all-age journey/report: `qa/game-completion-20261020/visual-review/natural-all-age-equipment-live-20261020.mjs` and `equipment-all-ages-live/natural-all-age-kingdom-live-20261020.json`.
- The comparison uses the actual approved and live screenshots at display size; it is not a pixel-difference score or owner acceptance.

## Result

The approved mock presents an armory with a standing hero, six equipment sockets, illustrated item cards and a selected-item comparison with equip/unequip actions. The repaired runtime now displays seven Future carried items as a four-column image grid, with all seven item icons loaded. Selecting Flint Club shows its identity, gear icon, actual attack bonus, worn weapon comparison and Equip, Unequip and Cancel controls. No unsupported durability or weight values were added. At 1280×720 the campaign-age figure is fully visible between the slot rail, inventory tray and inspector. At 825×375 and 933×424 the slot rail, inventory tray and inspector stay separate and the selected preview and Equip action remain fully visible; the full figure is omitted at these short heights to protect the controls.

The focused live browser journey reached all eight ages, forged age-correct weapons, recruited formations, and retained all six Future equipment slots after save/reload. In the Cancel check, inventory and worn gear stayed unchanged; resource deltas matched passive production only. It passed with zero browser/HTTP errors. The all-age journey runner was rerun after the repair.

## Acceptance status

- Illustrated carried-item grid and selected comparison: PASS at desktop; compact presentation PASS with the hero figure omitted.
- Grid/inspector and desktop hero clearance at 825×375, 933×424 and 1280×720: PASS; no measured overlap.
- Equip/unequip and six-slot persistence: bounded natural UI PASS; unrelated item families, duplicate/full-bag, incompatible-item and complete edge-case matrix remain OPEN.
- Exact M23 composition and item-specific worn appearance: PARTIAL/OPEN. The mock uses a wide lower panel and displays the hero at left; compact runtime omits the body, and the separate M19 worn-appearance requirement remains unsatisfied for five non-weapon slots.
- Overall M23 and whole-game acceptance: OPEN.

The complete Node suite passed 228/228 after this repair. This is bounded source/browser evidence, not final desktop, device, or owner acceptance. No image-provider, package, APK, device, or Git action occurred.
