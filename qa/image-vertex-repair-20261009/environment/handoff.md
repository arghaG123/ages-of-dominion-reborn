# Environment vertex repair handoff, 9 October 2026

Image AI 1 finished the local environment pass and every paid call that fits under the US$80 cap. `imageWorkComplete` is false. `wholeDeliveryReady` is false. The coordinator has no UNKNOWN write-ahead. The mutex is released.

## Local result

- 145 residual sprites were remeasured. 78 are READY for their declared use, with source and output frames stored separately. The rest are PARTIAL because a declared contact lands on transparent pixels. Coordinates were not clamped.
- The eight named green-slab ids were measured. None had a separable flat bottom slab, so no subject was erased. Magenta on the residual sprites is zero. Iron, Medieval, and Modern Town Hall magenta remains on the old `assets/delivery/stone-starter-20261003/derivatives/v2/live/buildings/` runtime files. Code should rebind those consumers to the residual outputs named on the artifact rows.
- Kingdom painted-road conflicts reproduce 7, 8, 7, 8, 8, 8, 8, 9 from Stone through Future. Frozen affine `[60, -10, 25, 35, 170, 165]` and Hall scale `0.1312` were not edited. Proposals stay `PROPOSED` and inactive.
- Nine full mock screenshots stay reference-only. Support rows record Code-native UI where no new image is required.
- Four viewports use one uniform scale and letterboxing. They are `ASSET_COMPOSITE` plates, not gameplay screens.

## Paid result

- Project `project-eaa4c1cc-8f19-4d24-9e6`, model `gemini-3.1-flash-image`, global endpoint.
- Eleven kingdom 4K responses plus the resumed medieval correction are native 5504×3072. The medieval v2 body was the same retained request after HTTP 429. That resume did not add a second reservation.
- Candidate A fails geometry. Candidate B for stone, bronze, iron, and medieval also fails: the painted pads, hall terrace, roads, and camera do not follow the frozen legal guide. Medieval shows a river, a ravine, and a different pad layout. No third kingdom attempt was sent. Gunpowder, industrial, modern, and future corrections were not sent: the same correction method already failed, and a new 0.4931 reservation does not fit.
- Seven actor packs were collected at native 2048×2048 PNG: knight, ranger, warlock, mage, paladin, barbarian, and necromancer standing bodies. Each shows one full standing subject on a flat white ground, which the actor prompt allows. They are candidates only. This coordinator did not write AI2 directories and did not mark them READY.
- Exposure is 79.8327 USD committed/protected: baseline 71.1156 plus 8.7171 retained for this repair. Headroom under 80 is 0.1673 USD. The 15 USD reserve stays inside the baseline. Invoices are unknown.
- Eleven actor packs remain unsent. The next one, `class-healer-standing-body`, needs 0.40 USD. Eleven packs need 4.40 USD, so the shortfall is 4.2327 USD.
- Sixteen adventure and defense packs remain unsent. At 0.4931 USD each they need about 7.89 USD. That shortfall is about 7.72 USD.
- Owner budget decision is required before any further paid call.

## Code handoff

Do not bind the new kingdom candidates. Rebind only the cleaner residual or repaired building sprites, and keep runtime, owner, and device acceptance open. Actor natives are under `qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS/natives/` for AI2 to copy and review.
