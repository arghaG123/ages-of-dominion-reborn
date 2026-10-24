# M19 current equipment review — 21 October 2026

**Current-source update:** the root-level articulated wear-layer finding below is repaired for the supported Knight attachments. See the [attack-pose review](m19-joint-wear-motion-review-20261021.md) and [paired-boot gait review](m19-paired-boots-gait-review-20261021.md) for the current-source checks (focused 6/6; full suite 241/241). Natural Adventure/Tactical gear fit and motion, other class/era rows, Healer, and M19 acceptance remain OPEN.

**Result: Future Knight worn kit now passes its bounded natural journey and visual review; M19 remains PARTIAL and the whole game remains INCOMPLETE.**

## Current visual comparison

The approved target is `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/19-hero-equipment.jpg`. I inspected the natural Future Knight six-slot Hero captures at 825×375, 933×424 and 1280×720 in `qa/game-completion-20261020/visual-review/equipment-all-ages-live/hero-future-six-slot-loadout-*.png`.

At each viewport, the complete Knight stays inside the room and visibly wears the selected helmet, weapon, offhand, chest armor, boots and accessory. The item cards flank the figure without covering it. The saved natural-journey report records six unique item IDs and six `attached-asset` results after reload; the item icons and slot records also survive reload. The separate eight-age journey verifies the age-specific Knight weapon at all eight ages.

This corrects the Future Knight finding in `m19-equipment-mock-comparison-20261020.md`: that earlier report inspected the pre-overlay screenshots. Its statement that the Future body showed no item-specific attachments is stale after the 20 October repair. The earlier report remains as dated evidence for the before state.

## Current 32-kit / 192-slot audit

`m19-current-worn-matrix-live-20261021.mjs` resolved the current `heroBody`, `bodyMatchesKit` and `wornMarks` consumers, hashed each bound image, and enumerated all six slots for all eight classes and four kit eras. The 32 standing bodies hash-match their manifest and all match their assigned kit era. The 41 unique body/wear images decode as RGBA PNGs.

| Current slot appearance | Rows | Meaning |
| --- | ---: | --- |
| Item-specific attached asset | 9 | Six Future Knight slots plus Knight weapons in the other three kit eras |
| Static weapon baked into body | 24 | A weapon is visible in the body plate, but the selected weapon item layer is suppressed |
| Socket only | 159 | No current item-specific body layer is bound |

The slot-state matrix uses synthetic all-slots-worn input to enumerate the current painter bindings. It does not prove natural item acquisition or equip, item persistence, pixel fit for every overlay, or motion integration. Current machine evidence is `m19-current-worn-matrix-live-20261021.json`; the 32-plate visual sheet is `qa/game-completion-20261019/visual-review/hero-body-matrix-live-20261020-current.png`.

## Source-wiring audit and visual boundary

Current consumers confirm equipped payload wiring for the protagonist in the Hero Room (src/client/hero-room.js, wornPayload and paintEquippedSockets), Adventure (src/client/main.js, placeTraveler actor calls), and Tactical (src/client/main.js, heroFigure). The Hero Room paints layers over its standing body. In src/client/actor.js, drawActor appends paintWornSlots to the actor root after the jointed body; src/client/anatomy.js, drawBoundActor, does the same. This makes equipped layers available to those consumers, but the root-level overlays are not parented to the moving joints. Fit during motion remains unverified.

The 20 October natural package includes Adventure captures, but its hero is too small at map scale to establish visible item-specific gear. It contains no Tactical gear comparison capture. Thus source wiring is bounded PASS; Adventure/Tactical visual and motion integration remain OPEN. This audit does not upgrade any socket-only or synthetic matrix row to visual acceptance.
## Acceptance status

- Future Knight Hero-room six-slot appearance and natural save/reload: **bounded PASS** at three landscape sizes.
- Eight-age Knight weapon journey: **bounded PASS** in the recorded natural campaign run.
- 32 class/kit body identity and source integrity: **bounded PASS**; this checks body plates, not full presentation.
- Other class/kit wearable layers, per-item replacement of baked weapons, old-age gear on a new kit, and full natural empty/equipped comparisons: **OPEN**.
- Adventure/Tactical class gear integration, complete role motion, Healer anatomy/matte/motion and broader mock/scene review: **OPEN**.

The focused natural journey evidence is `qa/game-completion-20261020/visual-review/equipment-all-ages-live/natural-all-age-kingdom-live-20261020.json`. The current source matrix is an independent bounded audit, not a visual acceptance for the 159 socket-only rows. No APK, device or owner acceptance occurred.
