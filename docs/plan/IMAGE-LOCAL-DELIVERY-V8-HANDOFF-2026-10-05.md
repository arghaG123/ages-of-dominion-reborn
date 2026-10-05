# Image local delivery v8 — 5 October 2026

Language/framework: Python 3.13.7, Pillow 12.3.0, NumPy 2.5.3, OpenCV 5.0.0, SciPy 1.18.1, measured this run. No provider call. `codeAIHandoffReady` is false. Ready rows can be consumed one at a time.

## Paths for Code

- Interface: `docs/plan/IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json`
- Checkpoint: `qa/image-local-delivery-v8-20261005/checkpoint.json`
- Scene detail: `qa/image-local-delivery-v8-20261005/scenes.json`
- Class labels: `qa/image-local-delivery-v8-20261005/class-semantics-v8.json`
- Chain diagrams: `qa/image-local-delivery-v8-20261005/assemblies/`
- Arithmetic: `qa/image-local-delivery-v8-20261005/arithmetic-regression.json` and `arithmetic-scene-diff.json`
- Stone overlay: `qa/image-local-delivery-v8-20261005/terrain/kingdom-terrain-stone-painted-and-legal.png`
- Stone proposal viewports: `qa/image-local-delivery-v8-20261005/terrain/kingdom-terrain-stone-four-viewport.png`

## Counts

- Reused ready rows: 14. Nine static troops, Ranger sleeve/vambrace at -25/0/+25, Healer boot 135×131, Healer leg/greave, Healer greave/boot, Paladin knee/greave.
- Partial: 43, including eight class chains and 32 scene plates. None of the plates are promoted.
- Failed: 4. Knight thigh/greave (13 attempts), Paladin thigh/knee, Paladin greave/boot, Paladin head bytes unavailable.
- Blocked: 1. Three-role draft, Clubman, Slinger, standing Sharpshooter, `DRAFT_NOT_SUBMITTED` / `OWNER_BUDGET_AUTHORIZATION_REQUIRED`.

## What this pass did

The widened blue test reproduces 8 scenes and 13360 candidate pixels before component filtering. That is not bank accuracy. A synthetic uint8 overflow pixel is in the regression file.

Relative-luminance roads flooded the ground. One Sobel-ridge correction was checked on Stone, Medieval and Adventure and followed vegetation, rocks and field edges. Those polylines were withdrawn. Painted roads on 31 plates stay unresolved, not absent and not complete.

Stone was read on a 100px legal grid, then corrected once: the north spur was dropped and the near bank was moved out of the channel. The ring, the radial toward the bridge, the river axis, both banks and the wooden deck are coarse, about 40 legal pixels. The legal centerline sits a mean 73.76 legal pixels off those tracks. The legal bridge rectangle is not the wooden deck. Proposal `proposal-v8-kingdom-terrain-stone-manual-tracks` is PROPOSED. Kingdom affine `[60,-10,25,35,170,165]` and Hall scale 0.1312 were not edited. `proposedCamera` is null.

River color-axes remain on plates where a widened-blue component passed the sky filter. Adventure and Medieval were visually consistent with the channel. Stone's channel touches the top edge, so the filter dropped it; the manual line is the Stone record. Blue is still not proof of a river on the unchecked plates.

Eight class chains are diagrams of present parts and missing links. Sides stay UNKNOWN. Healer head is missing. Mage torso labels stay withheld. Warlock text crops are not anatomy. No full body is ready.

Healer boot bytes are unchanged, SHA256 `4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21`. Industrial melee, Modern heavy and Modern ranged were not given a new matte method. Natives, v4–v7 interfaces and the replacement draft hash were unchanged. Game consumers were not edited.

## Not done

Roads on the other 31 plates, walkable ground, rock polygons, and a fitted camera were not produced. Missing transfer guides were not recreated. Owner, runtime and device acceptance stay open.
