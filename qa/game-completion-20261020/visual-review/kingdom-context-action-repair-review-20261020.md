# Kingdom contextual-action review — 20 October 2026

## Change

The selected-site inspector no longer includes every building type alongside Town Hall, wall, age, day and tutorial controls. An empty site exposes one contextual build-picker action; an owned building exposes only its upgrade action. The focused picker contains the eight legal building types with current-age building art, resource symbols, exact displayed costs and accessible names. Town Hall, walls, age advance, end day and recruitment stay reachable in a separate Kingdom-actions sheet. Construction preconditions remain core-validated; an unavailable choice keeps its reason reachable.

The normal Kingdom state line now identifies the current age/day/weather and selected site/action without repeating the previous long settlement paragraph.

## Live browser evidence

`kingdom-context-actions-live-20261020.mjs` created a fresh campaign through the visible UI in isolated Chromium profiles at **825×375** and **1280×720**.

- The selected empty-site inspector has one build action, one Kingdom-actions entry and the tutorial control; it has no unrelated per-building cost list.
- The picker exposes all eight legal buildings. Each option has loaded current-age art, a full accessible name, cost amounts, and at least a 48 CSS-pixel hit height.
- The last build option scrolls fully into the panel at both sizes.
- Lumber Camp preview followed by Cancel preserved the site level and all four resources.
- The Kingdom-actions sheet exposed Town Hall, Walls and End day. End day advanced the isolated campaign exactly one day.
- Both runs reported zero page/console errors and zero failed responses.

Captures and full measurements are in [`kingdom-context-actions-live/report.json`](kingdom-context-actions-live/report.json), including selected inspector, picker top/bottom and Kingdom-actions screenshots for both sizes.

## Tests

Fresh `node --test tests/*.test.mjs`: **211/211 PASS**, including the 10,000-command save-stress horizon. `node --check src/client/main.js` passed. The browser evidence is a bounded UI interaction/visual check, not a claim of full Kingdom or game acceptance.

## Still open

This closes only the Kingdom selected-action clutter. The approved all-age mock comparisons, natural Kingdom progression and wall/site clearance, remaining screen and journey scope, all required physical scene reviews, independent desktop acceptance, exact final APK, later device QA and owner acceptance remain open. No package or device work was done.
