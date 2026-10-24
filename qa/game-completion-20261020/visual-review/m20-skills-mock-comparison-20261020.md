# M20 skills-screen mock comparison — 20 October 2026

**Result: selected-skill interaction and readable detail PASS; compact composition PARTIAL; whole-game acceptance remains INCOMPLETE.**

## Evidence

- Approved target: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/20-skills.jpg` (1360×768).
- Live runner: `qa/game-completion-20261020/visual-review/core-screens-live-20261020.mjs`.
- Current selected First Aid captures: `core-screens-live-20261020/hero-skill-detail-825x375.png` and `hero-skill-detail-1280x720.png`.
- Current `report.json` records 13 screen captures per viewport, loaded terrain, zero browser/console errors, zero failed HTTP responses, and selected-skill clipping checks at both sizes.

## Comparison and repair

The approved mock uses a 3×3 skill grid with a selected-skill detail plate beneath it. The runtime keeps its full Hero chamber and figure as the main scene, with the skill tree in the right-side inspector. All nine skills use distinct art, names and current ranks. At 1280×720 all nine cards and the selected detail fit together. At 825×375 the inspector scrolls; all nine remain reachable, though the full grid is not simultaneously visible.

The former compact detail came from a general notification below the panel and clipped after “after a won”. It now appears in a dedicated inline detail plate, highlights the selected sigil and scrolls into view when selected. First Aid shows “Recover 15/30/45% of losses after a won battle” with its rank. The 825×375 and 1280×720 live probes confirm the entire text fits inside the panel without horizontal or vertical clipping. Selection does not spend a skill point or mutate the skill rank. The same selected state is readable in both current screenshots.

## Acceptance status

- Nine distinct skill cards, names and ranks: PASS; all nine appear together at desktop, compact panel requires scrolling.
- Selected skill highlight and complete details at both tested sizes: PASS.
- Skill-offer purchase/decline lifecycle, maxed skills, rank persistence and all edge cases: OPEN beyond existing bounded tests.
- Full M20 composition and whole-game acceptance: PARTIAL/OPEN; compact screen does not show all nine simultaneously and overall scene differs from the mock.

The complete Node suite passed 228/228 after the source repair. This bounded visual/runtime comparison is not desktop/device/owner acceptance. No image-provider, package, APK, device, or Git action occurred.
