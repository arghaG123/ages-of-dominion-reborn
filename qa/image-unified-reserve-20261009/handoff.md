# Image handoff — unified reserve — 2026-10-09T12:35:08Z

Language/framework: JavaScript ES modules game, Python 3.13.7 image tools. This file is the Image handoff. It does not integrate Code.

## Budget

Owner quote recorded once: "use $15 reserve and instruct remain work and solution to do for one AI with a prompt."

Historical safety reserve 15 and historical protected exposure 79.8327 are unchanged. Effective reserve is 0. Prior liability excluding that reserve is 64.8327. Remaining capacity under 80 is 15.1673. This continuation reserved 0 and spent 0. The healer worst case from coordinator.estimate_upper_bound_usd for the decoded 4-image wire is 0.5266, and 64.8327 + 0 + 0.5266 + 0 = 65.3593. Invoices remain UNKNOWN. No second reserve-release record was written.

## What Code can bind

READY reuse, bytes untouched:

- `assets/runtime-code-20261007/troops/troop-stone-melee.png` translation [-477, -112]
- `assets/runtime-code-20261007/troops/troop-industrial-ranged.png` translation [-526, -103]
- `assets/runtime-code-20261007/troops/troop-industrial-heavy.png` translation [-233, -64]
- `assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png` translation [-363, -79]
- `assets/derivatives/rigs/v7/healer/boot.png` 135×131

`gear-stone-helm` crop affine is [1, 0, 0, 1, -82, -208]. Gear and icon ground contact is NOT_APPLICABLE.

New derivatives under `assets/derivatives/image-unified-reserve-20261009/` are partial plates. Do not treat them as full rigs or as scene clearance.

## Do not bind as finished

- Kingdom, adventure, tactical, and defense terrain. Spatial gate is FAIL. Affine [60, -10, 25, 35, 170, 165] and Hall scale 0.1312 stay frozen.
- Bronze runner and medieval archer.
- Wolf and brute. Pass 11 removed 266 and 294 stroke pixels. Wolf still has 139 far-thin pixels plus a 21-pixel red disk at [473, 783, 478, 795]. Brute still has 111 far-thin pixels. Feet and paws stayed. Crops: `qa/image-unified-reserve-20261009/review/creature-wolf-spot.jpg` and `qa/image-unified-reserve-20261009/review/brute-feet-spot.jpg`.
- Workshop lawn is gone. Pass 11 removed 2383 perspective-outline pixels. The stone, roof, forge, and tools remain. Preview: `qa/image-unified-reserve-20261009/review/workshop-iron-pass11.jpg`.
- Drone slab is gone. Three separated frames are published with durationMs null. No timing was invented.
- Warlock white floor and lower-right dust are gone. The plate is still a static body, not a gait.
- Healer standing body. The wire at `qa/image-unified-reserve-20261009/vertex-coordinator/healer-class-standing-body/request_body.json` decodes to 4 inline PNGs (bust, front neck, protected boot, and a guide pasted from those pixels). The single jobs list returned HTTP 400. No POST was sent. It is not READY.
- Any row whose producer label was READY solely in an older interface.

CSS: capped roles use 64 on the longest visible side. Ordinary static ceiling is 130. Measure alpha bounds, not transparent padding.

Runtime is UNVERIFIED. Owner acceptance is UNVERIFIED. The device stays STOPPED. `imageWorkComplete` is false. `localProcessingComplete` is false. `wholeDeliveryReady` is false.

Gallery: `qa/image-unified-reserve-20261009/review/gallery.html`
Interface: `docs/plan/IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json`
Checkpoint: `qa/image-unified-reserve-20261009/checkpoint.json`
