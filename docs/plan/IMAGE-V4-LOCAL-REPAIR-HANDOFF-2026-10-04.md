# Image v4 local repair handoff — 4 October 2026

Current matte decisions are in `docs/plan/IMAGE-DELIVERY-INTERFACE-V5-2026-10-04.json` and `docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-2026-10-04.json`. Gunpowder heavy and Future ranged meet the small-static keep. Their cobble plane and neighbor rectangle are gone. Stone melee, Stone ranged, and Industrial ranged remain the only primary replacement draft, status `DRAFT_NOT_SUBMITTED` / `OWNER_BUDGET_AUTHORIZATION_REQUIRED`. `codeAIHandoffReady` stays false. The paragraphs below are the earlier v4 pass.

The actor section below is stale where it still says Gunpowder heavy fails. Eight actor rows plus Gunpowder heavy, Future ranged, and the horse meet a bounded review. Stone melee and Stone ranged still fail as slabs. Industrial ranged is still the prone sheet.

Image-owned local corrections after the v3 independent verification. v3 files were not overwritten. No provider, project, account, job, or bucket call. No game, native, Git, or device work.

## Interface

`docs/plan/IMAGE-DELIVERY-INTERFACE-V4-2026-10-04.json`

- 75 distinct role rows. The v2 count of 76 included a duplicate mountedKnight, not a missing paid identity.
- Substitution sources are literal paths under `assets/production/...`. Dimensions stay in their own fields.
- Advertised filenames `troop-iron-melee-legionary-1k.png` and `troop-industrial-heavy-steamwalker-1k.png` do not exist. The files that exist are `assets/derivatives/substitutions/v3/troop-iron-melee.png` and `assets/derivatives/substitutions/v3/troop-industrial-heavy.png`.
- `codeAIHandoffReady` is false. There is no blanket usable-sprite count.
- Referenced paths in this interface were checked on disk: 0 missing.

## Actors and mounts

Outputs: `assets/derivatives/actors/v4/`, `assets/derivatives/mounts/v4/`, evidence `qa/image-v4-repair-20261004/actors/`.

Inspected:

- `troop-stone-melee`: boots remain, the dirt plinth rectangle is gone, thin dirt wedges remain beside the shafts. Status `BOUNDED_REVIEW_SAMPLE_RESIDUAL_EDGE_DIRT`. The contact record is the lowest retained pixel, not a measured anatomical foot.
- `hero-mount-horse`: hooves remain and the grey floor fill is gone. A hairline can remain. Status `BOUNDED_REVIEW_SAMPLE_RESIDUAL_HAIRLINE`.
- `hero-mount-motor-transport`: wheels remain and a ground shape remains. Status `RESIDUAL_FLOOR_WHEELS_PRESENT`.
- `troop-industrial-ranged`: still a prone caption sheet. Status `FAIL_PRONE_CAPTION_SHEET_NOT_ISOLATED`.
- `troop-stone-ranged`: floor still reaches the bottom of the matte. Status `RESIDUAL_FLOOR_NOT_A_CLEAN_SAMPLE`.

Other named rows received an automatic backdrop and light-earth key only. Their status is `AUTOMATIC_KEY_NOT_VISUALLY_ACCEPTED`. They are not clean.

`troop-iron-melee` stays a wrong-role stencil. `troop-industrial-heavy` stays a wrong-role gunner. `knight-mounted-master` stays the medieval mounted painting and is not relabeled. The 1K legionary and steam-walker substitutions stay separately identified.

## Rigs

`qa/image-v4-repair-20261004/rigs-v4.json` and `assets/derivatives/rigs/v4/`.

Knight is the pilot: magenta-family components were separated. Combined assemblies are labeled as assemblies, not whole limbs. The left thigh/greave pair was placed at a virtual pivot and rotated to -25, 0, and 25 degrees with nearest-neighbour overlays in `qa/image-v4-repair-20261004/rigs/`. Overlap is not a painted socket. Status `FAIL_NO_PAINTED_OVERLAP`.

The other classes keep corrected names for the crops the audit showed were mislabeled (helmet called torso, sleeve called hand, and the rest of that list). Those renames do not create missing sides. `rotationOverlapVerified` is false.

## Ancient knight card

`assets/derivatives/portraits/v4/hero-knight-ancient-card.png`

Exact crop `(420, 220, 1120, 1180)` from read-only `C:/dev/aod-art-src/hero-knight-ancient/attempt-1.png`, hash `eb03424f0a599894dfa5bdcc9124a84221c2959787c3c8fdc18d24636180acf8`, 1536×2752 RGB. The card is 700×960 RGB, opaque, and includes the head and face. Class, era, and owner acceptance are unverified. It is not an alpha world actor and it is not the medieval mounted knight. The 37 improved portrait cards and 44 v2 alias files were not regenerated.

## Terrain

`qa/image-v4-repair-20261004/terrain/clearance-v4.json` covers 9 sources.

Active matrix remains `[60, -10, 25, 35, 170, 165]`, contract hash prefix `43553411`. Candidate v2 keeps its own matrix and a different hall rectangle. Clearance is the distance from each rasterized site polygon to annotated blue-water and dark-rock masks at that file's own pixel scale. Roof color and roughness are not collision. Roads are not labeled. No source is declared to contain a baked townhall.

On native `kingdom-terrain-stone` (5504×3072) the active hall polygon does not intersect those water or rock masks (minimum clearance about 2140px to water and 1845px to rock). The candidate-v2 hall on the same image is a different polygon (about 401k pixels versus about 170k). That open-ground reading is only for those two masks. It does not accept the scene. The 1k Stone composition is a separate source and its candidate hall does intersect the rock mask. Scenes are not promoted.

## Offline reuse

`scripts/interactive_runner_continuity.py` now requires the saved request body, response hash, and output hash. It checks prompt, source bytes and order, image size, aspect ratio, model, and endpoint when that identity is part of the request. A missing identity returns `FAILED_REUSE_*` and does not dispatch.

Sandbox `qa/image-v4-isolated-controls-20261004/` copies the runner and points `ROOT` at the sandbox before import. Network, credentials, subprocess, and transport are forbidden. Report `v4-controls-report.json`: 27 probes passed, 0 failed, including the previous 14 producer probes, the 11 stronger cases, swapped source order, and wrong aspect ratio.

## Accounting

`docs/plan/ACCOUNTING-CONSISTENCY-V4-2026-10-04.json` retains 70.7012 USD, nested batch 40.24, UNKNOWN liabilities 0.287224, and invoices UNKNOWN. The 9.2988 margin is not spend authority.

## Still open

These rows stay open and do not authorize a new paid call: residual floors on the unreviewed actors and the motor/future transports, the prone industrial sheet, wrong-role iron and industrial heavies, the medieval mounted knight, rig parts that are combined or absent, unproved painted sockets, kingdom scene registration, owner acceptance, and runtime binding.
