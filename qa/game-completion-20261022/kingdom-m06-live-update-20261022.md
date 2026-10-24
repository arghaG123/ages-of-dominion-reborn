# M06 Kingdom layout live update — 22 October 2026

**Product remains INCOMPLETE. M06 remains FAIL_VISUAL_OPEN.** The approved local preview was checked at 1280 × 720 in the existing in-app tab: `http://localhost:4174/?audit`.

## Current live view

- Natural Medieval campaign, day 4, storm; 17 built sites plus the level-4 Town Hall. P02 Farm was selected without buying, upgrading, or placing anything.
- The real selected-building inspector now sits at the lower center: CSS box `[432, 576, 416, 132]`. It shows Farm level 1, Upgrade Farm, Kingdom actions, and Skip tutorial. This matches M06's inspector placement, but the selected content is not the mock's Marketplace.
- The Kingdom navigation now forms a left rail: box `[12, 220, 58, 280]`; all five buttons are at least 48 CSS pixels high. The world transform remains `translate(-10px, 0px) scale(0.9375)` over the full stage.
- The inspector remains an overlay. Kingdom scene labels no longer reserve a false right-side panel inset.
- The live terrain is the 1376 × 768 Medieval stone-curtain family painting. Its 12 × 10 mine sites are twelve actual owned `mine` plots; no ownership or plot data was fabricated.
- Browser warning/error log: empty. Save control returned to “Save campaign.” Resource counters rose while the preview was open from passive production. After a reload showed the saved campaign gate, Continue resumed the same campaign; P02 was then selected. No construction, purchase, upgrade, slot load, or overwrite occurred.

## Visual result and remaining failure

The left navigation and lower-center inspector now follow the M06 screen composition more closely. The city itself still fails the mock: the interior has 12 repeated mine structures, broad open land between sites, and no dense varied residential center. The Town Hall remains its source-bound Medieval manor artwork rather than a central castle. The visible Farm inspector also differs from M06's Marketplace panel. Therefore M06 stays **FAIL_VISUAL_OPEN**, and no eight-age Kingdom visual gate is closed by this change.

Live screenshots were observed through CUA but not retained as files. The exact 825 × 375 and 933 × 424 live layouts remain unavailable through this approved browser route; CSS and responsive tests are not compact live captures. No owner acceptance, final desktop acceptance, package, APK, device, or release gate is claimed.

## Verification

- `node --test tests/*.test.mjs`: **269/269 PASS**, including the save horizon stress test.
- `node --test tests/visual-responsive-20261018.test.mjs`: **32/32 PASS**.
- `node --check src/client/main.js`: PASS.
- Current preview console warnings/errors: **0/0**.

Implementation is limited to `src/client/polish.css` and the Kingdom-specific panel measurement in `src/client/main.js`; the responsive test adds coverage for the new layout and inset rule.
