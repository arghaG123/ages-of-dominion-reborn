# Natural equipped-weapon continuity review — 20 October 2026

**Result: focused bounded PASS. Whole-game visual and release acceptance remain INCOMPLETE.**

## Change

The Hero Room already drew the reviewed native-alpha Stone flint club, but `wornKit()` dropped its `wearLayer` before Adventure rendered the mounted Hero. The rig then kept its generic weapon as well. The live kit now passes the reviewed held-prop layer through to actors. `shouldDrawRigWeapon()` keeps the generic rig weapon when no supported body layer exists, suppresses it only when a supported held prop replaces it, and preserves the default uncustomized actor behavior.

## Natural UI journey and evidence

A fresh isolated Chromium profile used the visible UI to start a Knight campaign, build a Quarry and Armory, advance only idle production time, forge and equip a Stone weapon, save/reload, and enter Adventure.

- Hero equipment rendered one `assets/derivatives/worn-gear-20261018/flint-club-stone.png` native-alpha attachment.
- The mounted Adventure Hero rendered the same single attachment and zero generic `data-joint="weapon"` rig joints.
- The equipped item stayed equipped through reload; it was removed from inventory as expected.
- Zero browser page errors and console errors were recorded.
- `node --test tests/*.test.mjs` passed 209/209 after the source change, including the 10,000-command save stress case.

The close Hero view shows the prop clearly; the Adventure contact view shows the Hero at map scale, so the held prop naturally occupies fewer pixels there.

## Files

- Browser journey: `qa/game-completion-20261020/visual-review/natural-equipment-live-20261020.mjs`
- Machine-readable report: `qa/game-completion-20261020/visual-review/equipment-live/natural-equipment-live-20261020.json`
- Hero phone capture: `qa/game-completion-20261020/visual-review/equipment-live/hero-weapon-equipped-825x375.png`
- Hero desktop capture: `qa/game-completion-20261020/visual-review/equipment-live/hero-weapon-equipped-1280x720.png`
- Adventure map capture: `qa/game-completion-20261020/visual-review/equipment-live/hero-mounted-weapon-825x375.png`

## Limits and open work

This is Stone-age equipment continuity for one reviewed weapon, not confirmation of wearable art across Bronze–Future or acceptance of all Hero, Army, Adventure, Tactical, Defense, Kingdom, equipment, spell and battle mocks. Full M01–M30, J01–J18, 32 scene traces, broad natural-play coverage and independent desktop review remain open. The exact final-source APK, device verification and owner acceptance remain later gates. No APK or device action occurred.
