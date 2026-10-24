# Defense preparation flow review — 20 October 2026

## Current result

Focused implementation and natural browser verification passed. The whole game remains incomplete.

The War screen now opens a no-session preparation view for Campaign Siege or Endless. It exposes the current resource balances, legal tower purchases, the Workshop slot requirement, and the route back to Kingdom. Starting a mode creates the session and pauses it before deployment. Owned towers are drawn on the exact defense pads used by `createDefense`, so the setup field remains truthful after purchases.

The shared action-icon helper now renders a labeled panel action when the panel is open and a matching dock action when it is closed. This removed the null `classList` crash that occurred when starting a defense from an open panel. The mobile defense title is placed below the resource rail.

## Verification

- `node --test tests/*.test.mjs`: 211/211 pass, including the 10,000-command save-stress test.
- Fresh-campaign defense preparation journey at 825×375 and 1280×720: no defense starts and no resources are spent until the explicit Start action; both modes can be selected; the player can leave for Kingdom; the started siege remains paused through hero and army deployment with zero wave time elapsed. No page or console errors.
- Separate natural purchase journey: built a Siege Workshop and Quarry through Kingdom controls, purchased a Support tower for exactly 80 wood, 50 stone and 60 gold, confirmed it appeared in preparation, then confirmed the active paused session used pads D1–D3 with the same tower families. No page or console errors.
- All-surface browser sweep: 116 captures at 1280×720, 1180×820, 933×424 and 825×375; zero page/console errors and zero fully exposed control hit failures.
- The preparation status and resource bar do not overlap at either 825×375 or 1280×720.

## Evidence

- [Natural preparation runner](defense-preparation-natural-live-20261020.mjs)
- [Natural purchase and pad continuity runner](defense-tower-purchase-natural-live-20261020.mjs)
- [Preparation journey report](defense-preparation-live/report.json)
- [Purchase journey report](defense-preparation-live/natural-tower-purchase-report.json)
- [116-surface review report](surfaces/surface-review.json)
- Screenshots are alongside these reports in `defense-preparation-live/` and `surfaces/`.

## Still open

This focused repair does not close the full M01–M30 and J01–J18 acceptance, all 32 physical scene reviews, complete all-age visual fidelity, independent desktop acceptance, final snapshot APK, or later device and owner gates. No package, device, release, paid provider action, or owner acceptance occurred in this pass.
