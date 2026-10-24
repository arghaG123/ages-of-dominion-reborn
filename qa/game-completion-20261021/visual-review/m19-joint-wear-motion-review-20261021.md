# M19 articulated wear-layer repair — 21 October 2026

**Result: current articulated-render wiring and isolated motion review PASS for the supported Knight layers; M19 remains PARTIAL and the whole game remains INCOMPLETE.**

**Follow-up later on 21 October:** the paired Future Knight boots now have a bounded isolated walking-gait PASS; see [the paired-boot gait review](m19-paired-boots-gait-review-20261021.md). Natural Adventure/Tactical scale fit remains open.

## Finding and repair

The previous source audit found that `drawActor()` painted every equipped layer after the jointed body at the actor root. Layers therefore ignored the head, spine, arm and forearm transforms during clips.

`src/client/actor.js` now lets `chain()` return its final joint and lets `paintWornSlots()` render a selected subset of slots with an explicit attachment label. In the articulated actor, the held weapon is placed at the forearm endpoint under the animated weapon joint; the helmet is drawn inside the head joint; and the remaining supported wearable layers are grouped beneath the rotating spine. The standing Hero Room and static bound-body paths keep their prior root-relative behavior.

## Verification

- `node --check src/client/actor.js` and `node --check tests/worn-gear-render-20261018.test.mjs`: PASS.
- Focused worn-gear suite: 5/5 PASS, including a DOM hierarchy regression that checks weapon ancestry through weapon/forearm/arm/spine, helmet ancestry through neck/spine, and spine attachment for the other fitted slots.
- Full `node --test tests/*.test.mjs`: 239/239 PASS, including the 10,000-command save-stress case.
- Reviewed the isolated current-source fixture `m19-joint-wear-motion-fixture-20261021.html` in the local browser at 1280×720. The supported Future Knight layers load, and the sword shifts with the attack arc across wind-up, strike and recovery. The fixture uses a synthetic equipped payload and no campaign state.

## Limits

The fixture is a rendering check, not a natural equipped-gear battle. It does not establish exact contact/fit in the Adventure or Tactical scene at their normal actor scale, does not cover a walking cycle for the paired boots layer, and does not promote the remaining class/era socket-only or body-baked weapon rows. Healer fit and motion remain open. M19 and the whole game remain INCOMPLETE.
