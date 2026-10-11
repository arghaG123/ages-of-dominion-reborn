# Image local delivery v9 — 5 October 2026

Language/framework: Python 3.13.7, Pillow 12.3.0, NumPy 2.5.3, OpenCV 5.0.0, SciPy 1.18.1, measured this run at `C:\Python313\python.exe`. No provider call. `codeAIHandoffReady` is false. Ready rows can be consumed one at a time.

## Paths for Code

- Interface: `docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json`
- Checkpoint: `qa/image-local-delivery-v9-20261005/checkpoint.json`
- Scene detail: `qa/image-local-delivery-v9-20261005/scenes.json`
- Review gallery (local file, ASSET_COMPOSITE only): `qa/image-local-delivery-v9-20261005/review/index.html`
- Review index: `qa/image-local-delivery-v9-20261005/review/review-index.json`
- Screen queue: `qa/image-local-delivery-v9-20261005/screen-queue.json`
- Healer leg clip: `qa/image-local-delivery-v9-20261005/assemblies/healer-leg-subchain-arc.gif`
- Stone overlay: `qa/image-local-delivery-v9-20261005/terrain/kingdom-terrain-stone-status.png`
- Four viewports: `qa/image-local-delivery-v9-20261005/terrain/kingdom-stone-four-viewport.jpg`

This pass did not start a server. `liveUrl` is null. Code's command is `node scripts/serve.mjs`. The script defaults to port 4173. The concurrent Code status records an isolated preview at `http://127.0.0.1:4317`. Image did not open either port.

## Counts

- Ready: 19. The 14 v8 rows, plus five Healer head cards from the native 2048 sheet: front with neck, front bust, three-quarter, profile with braid, profile with bun.
- Partial: 8 class chains, 32 scene plates, Healer crown, Healer braid, and the inspected torso-to-skirt neutral. None of the plates are promoted.
- Failed, preserved: Knight thigh/greave (13 attempts), Paladin thigh/knee, Paladin greave/boot, Paladin head bytes unavailable.
- Failed, new and stopped: Healer head-to-torso (rounded neck stump on the collar, one alignment) and Healer skirt-to-leg (cuff ratio 6.25 at scale 1).
- Blocked: 1. Clubman, Slinger, standing Sharpshooter. `DRAFT_NOT_SUBMITTED` / `OWNER_BUDGET_AUTHORIZATION_REQUIRED`. Draft hash unchanged.

## What this pass did

Five Healer heads are static cards. Side is UNKNOWN. They are not a body. The leg subchain (upper leg, greave, v7 boot) is assembled at scale 1 for -25, 0, and +25 degrees. The boot follows the greave with no extra ankle bend. The twelve prior joint metrics match v8 exactly. v8 `canvas` arrays are `[height, width]`. Pivots in v9 are named `[x, y]`.

Stone roads, river banks, the wooden deck, and the rock ring are manual legal-frame traces. Deck uncertainty is 16 legal pixels on the checked midspan. Roads and banks stay 24–40. The overlay draws only those traces plus legal site rectangles. Withdrawn ridge lines are not in the v9 overlay. The widened blue test again changes 8 scenes and 13360 candidate pixels. That is not bank accuracy. The Stone blue mask did not describe the river.

The town hall is pasted at frozen scale 0.1312. Kingdom affine `[60,-10,25,35,170,165]` was not edited. Viewport sheets use one uniform scale, the consumer focus camera, and CSS-derived chrome. They are not runtime screenshots. `proposedCamera` is null.

Healer boot SHA256 is still `4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21`. v8, the contract, and the three-role draft bytes were unchanged. Game consumers were not edited.

## Still open

Bronze through Future show a river and a bridge. Their polylines are not traced, and Stone's coordinates must not be copied onto them. Adventure, Tactical, and Defense plates are fitted in the gallery and are not traced. Home has no scene plate. Forge shows the six canonical slot names and no new gear bitmaps. Walkable ground is not traced. Full bodies remain incomplete. Horse, motor, future transport, Gunpowder heavy, Future ranged, and Future heavy stay at a 64px delivery limit. Code's 130px use of those three troops is a consumer repair.

Missing transfer guides were not recreated. Owner, runtime, and device acceptance stay open.

## Next executable action

Manually trace `kingdom-terrain-bronze` roads, banks, and bridge from `qa/image-local-delivery-v9-20261005/inspect/kingdom-terrain-bronze-legal.jpg`. Do not rerun the exhausted Knight or Paladin placements, and do not repeat the failed Healer neck or skirt-to-leg alignments.
