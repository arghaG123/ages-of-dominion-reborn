# M19 equipment mock comparison — 20 October 2026

**Visual result: item-specific worn appearance FAIL; acceptance remains OPEN.** This is a focused comparison of the approved M19 mock and the two available Future Knight runtime screenshots. It does not claim completion of the all-class/all-era equipment matrix.

## Reviewed pixels

- Approved target: design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/19-hero-equipment.jpg (1360×768).
- Runtime before: qa/game-completion-20261020/visual-review/equipment-all-ages-live/hero-weapon-age-7-825x375.png (825×375).
- Runtime after six-slot loadout: qa/game-completion-20261020/visual-review/equipment-all-ages-live/hero-future-six-slot-loadout-825x375.png (825×375).
- Method: visually inspected the three images at native resolution; this is a composition/semantic comparison, not a pixel-difference score. The different aspect ratios and the mock medieval appearance versus the Future-age kit make direct pixel matching inappropriate.

## Finding

The mock presents one dominant, complete figure in a material chamber. The figure visibly wears a distinct helmet, chest armor, greaves/gauntlets, sword, shield and ring. In the runtime pair, the same central Future Knight body, suit and carbine remain visible before and after equipping. The slot icons and displayed stats change, but the gear does not visibly alter the figure. The two runtime screenshots therefore demonstrate equipment selection/state changes, not item-specific worn appearance.

The existing focused journey report, qa/game-completion-20261020/visual-review/equipment-all-ages-live/six-slot-loadout-and-forge-review-20261020.md, records the functional journey and explicitly says that bespoke item art for Helm, Offhand, Armor, Boots and Accessory is absent. It does not claim six physical overlays. M19 in docs/plan/ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt requires body changes with gear, all eight identities/four era kits, empty and fully equipped states, retained old-item age, full-figure visibility on phone, and Healer anatomy/matte review. Those checks remain open.

## Status and next evidence

- M19 visible appearance: **FAIL / OPEN** on the inspected Future Knight pair.
- Equipment function and persistence: bounded PASS as recorded in the existing natural journey report; not rerun here.
- Coverage of all classes, kits, item qualities, artifact variants, old gear and phone composition: **OPEN**.
- Full Node suite: 228/228 PASS in the current turn; bounded code evidence only.
- No source, provider, package, device or owner-acceptance action occurred.

Close this visual gate only after current runtime captures show compatible item-specific gear changes on the actual full figure and the required matrix has been reviewed. Keep functional, art, scene, desktop, package, device and owner acceptance as distinct gates.
