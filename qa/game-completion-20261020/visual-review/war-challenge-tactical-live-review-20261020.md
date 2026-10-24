# War, Challenge and Tactical visual review — 20 October 2026

**Focused result: PASS. Whole game: INCOMPLETE.** The current War and Tactical surfaces were reviewed against the approved tactical-action and battle-result compositions at compact landscape (825×375) and desktop (1280×720). Natural player flows were run from isolated fresh campaigns.

## Repairs

- Challenge seed and scenario-code inputs now have visible inline labels as well as accessible names.
- Starting a challenge closes its setup panel so the player enters the full Tactical field.
- Challenge result export now appears in the pending-result dialog, where it is reachable before settlement clears the battle.
- Tactical initiative moved to the lower left and the action dock to the lower right to follow the approved mock composition. The dock is hidden while the result dialog is open, leaving its two result actions clear.

No new image generation was needed. The existing rendered battle scene is sharp and correctly registered; the previous mismatch came from screen composition and missing controls.

## Natural browser verification

`war-mode-natural-live-20261020.mjs` ran six isolated UI campaigns: Skirmish, Tactical Duel and Challenge, each at both viewports. All six battles resolved as victories in this run. Each mode had zero page or console errors and zero failed HTTP responses.

- All five War cards fit and receive input at both sizes.
- Visible seed and scenario-code labels were verified. An out-of-range seed was rejected without starting a battle.
- A local challenge JSON file imported the expected seed and label. Export produced the matching descriptor; Copy produced a local encoded challenge code.
- Starting a Challenge closes the side panel. Tactical actions are fully within the viewport and receive input.
- Challenge result export from the result dialog produced `aod-challenge-result.json` with the expected descriptor, outcome and digest before settlement.
- Skirmish and Challenge leave campaign resources, hero progression, inventory, army and RNG unchanged. Tactical Duel recorded its campaign result and paid the 150-gold victory reward once.
- All three settled outcomes survived reload without a second payout.

Evidence and screenshots: [`war-modes-live/`](war-modes-live/), with the machine-readable run report at [`report.json`](war-modes-live/report.json).

## Visual comparison

The tactical HUD now uses the mock's lower-left initiative / lower-right action arrangement. The battle-result overlay retains the mock's centered, high-contrast result panel and one clear return action; Challenge adds its export action above return. At 825×375, both buttons remain legible and within the result card.

The live encounter intentionally reflects the recruited campaign roster. A fresh campaign has fewer formations than the mock's large army tableau, so the battlefield remains less populated and the live action controls are compact icon medallions. Those are visible mock-fidelity gaps; this review does not claim exact pixel parity or all-age battle-scene acceptance.

## Regression checks

- `node --test tests/*.test.mjs`: **211/211 PASS**, including the 10,000-command save-stress test.
- `capture-surfaces.mjs`: **116 captures, zero browser errors, zero failed control hit checks** across 1280×720, 1180×820, 933×424 and 825×375.
- Fresh Warlock Adventure / Tactical spellcast / manual move / settle / reload journey: PASS at 825×375 and 1280×720; Magic Arrow spent 5 mana and the result persisted.

## Remaining acceptance

This focused repair does not close M01–M30, J01–J18, physical traces for all 32 age/mode scenes, all-age mock comparison, class/kit/motion acceptance, independent desktop review, final snapshot APK verification, or later device and owner acceptance. The product remains **INCOMPLETE**.
