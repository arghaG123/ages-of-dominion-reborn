# Current-state amendment — 22 October 2026

The later [M14–M15 live update](M14-M15-CURRENT-LIVE-UPDATE-20261022.md) supersedes this earlier review's M14 no-deployment finding and M15 two-formation swamp comparison for the current Medieval Skirmish route. The fresh state shows actual deployment, six real formations, the registered gorge and the active initiative/action layout at 1280×720. M14 and M15 are now **PARTIAL**, not OPEN/FAIL; M16 remains **PARTIAL**. The historical screenshots and earlier results below are retained as evidence of their original states.

# Tactical mock review: M14–M16 — 22 October 2026

## Result

**Bounded tactical implementation and live interaction check: PASS. Mock appearance: M14 PARTIAL, M15 PARTIAL, M16 OPEN. Whole game: INCOMPLETE.** This review covers only the Medieval tactical slice. It does not accept the mocks, close J01–J18, or verify package, device, or owner gates.

## Live route and journey

- Route: `http://localhost:4174/?audit` in the approved in-app browser, 1280×720 landscape.
- Source terrain: the Medieval Tactical scene resolves to the registered wooded river-gorge image. The runtime scene carried the accessible description `Medieval Age wooded river gorge tactical ground`; the image is the 5504×3072 PNG listed below.
- Practice deployment copied three campaign formations and allowed legal placement. A second live run placed Clubman ×12, Slinger ×8, and Bone Crusher ×5, then started the battle.
- Live combat exercised a legal Clubman strike, Magic Arrow against a Dire Wolf, Wait, Defend, a Slinger move selected through the secondary panel, opening and cancelling the retreat confirmation, and Auto resolution to Victory.
- Return to campaign kept Medieval Age/day 4 and the four-slot army roster at Clubman ×12, Slinger ×8, Bone Crusher ×5, Man-at-Arms ×5. The game displayed “Your campaign is unchanged.” Resource counters advanced while the game remained open, so this is not a byte-identical full-save assertion.
- Browser console warnings/errors after the run: 0/0.

## Mock comparison

### M14 — Tactical deployment: PARTIAL

The live Medieval scene now uses the registered gorge and twin-bridge source, and the three formations can be positioned over the board. The comparison remains materially short of the mock’s dense two-sided formation presentation, clear highlighted tile grid, full initiative strip, and compact icon action group. The live setup still devotes a bottom tray to formation cards and does not visually reproduce the mock composition or its troop density. The candidate terrain is not owner-accepted.

### M15 — Tactical action: PARTIAL

The live desktop now renders the four primary actions in a compact 2×2 lower-right panel. Measured at 1280×720, the dock is 356×123 px and its four buttons are 165×48 px; the secondary-actions trigger sits just outside the dock so it does not create a fifth row. This tracks the mock’s action placement and hierarchy more closely. The mock still has substantially denser, more detailed units, visible tile lines/target presentation, and a cleaner frame. The JPEG browser capture is useful for composition review but is too compressed to certify fine typography or pixel fidelity.

### M16 — Battle result: OPEN

The retained live result is from a practice battle and says the campaign is unchanged. It lacks the mock’s campaign-battle identity, reward resources, loot, campaign casualties, and campaign-survivor presentation. A real campaign battle was not started against the user’s saved campaign, so the campaign-reward journey and its visual match remain unverified.

## Verification

- `node --test tests/*.test.mjs`: **265 passed, 0 failed**; includes the 10,000-command save-stress horizon.
- Focused tactical helper/deployment/action tests: **34 passed, 0 failed** before the compact-dock CSS adjustment; the full suite above includes the final CSS state.
- `git diff --check` reports CRLF carriage returns as trailing whitespace across already-dirty files; no line-ending normalization was performed. The current source files retain CRLF.
- No build/APK, device, provider, Git, cleanup, or owner-acceptance action was performed.

## Retained screenshots

These screenshots are JPEG, 1280×720. SHA-256 is recorded for current live images; each comparison mock remains at its original 1376×768 size.

| Evidence | SHA-256 |
| --- | --- |
| `medieval-skirmish-deployed-1280x720.jpg` | `d1834fbab11b6b973390d349aaa4377dd79a7a58f7b8e94f1f83edcd7326b940` |
| `medieval-action-dock-four-button-1280x720.jpg` | `313138354598911593f28f0b28338cbdecf73a2d0777215a3f147f2823d1bad4` |
| `medieval-action-spell-live-1280x720.jpg` | `dfb2ea2a22aceda5410977da1c7a8d4d1d602c4285f9a25962373af2578ebfb0` |
| `medieval-skirmish-result-1280x720.jpg` | `f497913f3630c53073c755a84442fc4507186dbe12651cd347903b8542bbd12f` |

Mock sources: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/14-tactical-deployment.jpg`, `15-tactical-action.jpg`, and `16-battle-result.jpg`.

Registered Medieval Tactical terrain: `assets/high-res/interactive-4k-first32-20261003/run-05-tactical-retry-20261004-015857/packs/tactical-terrain/output.png`, SHA-256 `6eadf55f2df8727bcc0415b0f5bc2a8f8c5c766e8ce18f7839923401e0c39e5e`.
