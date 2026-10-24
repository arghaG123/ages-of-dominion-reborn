# Forge locked-state visual repair — 20 October 2026

**Focused result: PASS at 825×375, 933×424 and 1280×720. Whole-game visual and functional acceptance remains INCOMPLETE.**

## Observed defect

A fresh Stone campaign can open the Forge before building an Armory. In that state, the dock contained only the Forge inspector icon, but Forge styling expanded the dock into a large dark panel. On short landscape screens, the Armory requirement was hidden from the scene copy, and the details panel showed six empty slot filters before the player had any gear.

## Repair

- When the dock contains only the Forge inspector action, it now remains a 48×48 action medallion instead of a full-size empty panel.
- The closed Forge screen shows the Armory lock reason in its compact status block.
- The inspector explains how to unlock crafting and provides a visible **Return to Kingdom** control.
- Empty equipment-slot filters are omitted until an Armory offer, carried item or equipped item exists. The six-slot Forge path remains for campaigns with equipment.
- The panel keeps its tutorial control fully inside the short landscape viewport.

## Live verification

`forge-locked-empty-state-live-20261020.mjs` used fresh isolated browser contexts and visible UI navigation. It captured the closed Forge and its inspector at all three sizes. Every run confirmed the dock and inspector hit targets, visible lock text, the Kingdom return action, the tutorial control within the panel, and a return to Kingdom. No empty slot filters were shown. The run had zero page/console errors and zero failed HTTP responses.

Machine results and captures: `forge-locked-state-live/report.json` and the sibling `forge-locked-*.png` files.

The refreshed general screen runner captured 116 surfaces at 1280×720, 1180×820, 933×424 and 825×375, with zero browser errors and zero center-hit failures. Fresh `node --test tests/*.test.mjs`: **214/214 PASS**, including the bounded 10,000-command save-stress horizon.

The visible-UI, accelerated-clock all-age loadout journey was rerun after the UI and selector updates: **8 ages, 89 captures, zero browser/HTTP errors**, Hall/Walls/Barracks level 8, ten Army formations, and all six Future equipment slots preserved after save/reload. This is controlled-browser evidence, not an unassisted human-play claim. Refreshed report: `equipment-all-ages-live/natural-all-age-kingdom-live-20261020.json`.

## Acceptance boundary

This repair covers the early-game Forge lock state. It does not establish full M22 mock fidelity, all equipment-art coverage, all 30 mock comparisons, all 18 natural journeys, scene registration/physical traces, independent desktop acceptance, the final snapshot APK, device QA or owner acceptance. No APK or device action occurred. The whole product remains **INCOMPLETE**.
