# Eight-age equipped-weapon visual and runtime review — 20 October 2026

**Result: focused natural UI PASS; whole-game acceptance remains INCOMPLETE.**

## Art and attachment change

Added seven age-specific, transparent, semi-realistic weapon cutouts for Bronze, Iron, Medieval, Gunpowder, Industrial, Modern and Future. Stone continues to use the previously reviewed flint club. Each uses a shared landscape 1536×1024 canvas and lower-right hand pivot. Pixel inspection confirmed RGBA files, zero-alpha corners in six images, and one-pixel corner alpha in two images; there is no opaque checkerboard. SHA-256, dimensions, alpha bounds, prompt family and attachment metadata are in `assets/derivatives/worn-gear-20261020/manifest.json`.

Only the Knight receives this sword/saber/knife family on a live actor. The Hero close-up reads the reviewed body-kit description and leaves the weapon socket-only when that static plate already contains a sword or carbine (Medieval, Modern and Future), preventing duplicate props. Adventure uses the age-specific held prop on the Knight's jointed rider and suppresses the generic rig weapon when the native-alpha attachment is supported. Other classes keep their existing role-specific weapon rigs and Hero slot representation.

## Natural UI verification

Fresh isolated Chromium campaign, using visible controls only: choose Knight, enter the Valley, build four legal producers and an Armory, forge and equip one weapon in each age, pay each legal age gate, complete the Town Hall/wall progression through Future, enter the age-specific Adventure scenes, then save/reload Future. Browser time was advanced only for idle construction and production; campaign state and resources were not injected.

- Eight of eight age weapons were forged for their current age and equipped through the UI.
- The Adventure rider used the matching per-age asset, exactly one attachment layer and zero generic weapon joints in all eight ages.
- Hero view uses an attachment where the reviewed plate is unarmed; Medieval/Modern/Future plates keep their built-in weapons without a second overlay.
- Twenty-four Hero captures cover 825×375, 933×424 and 1280×720 across all ages.
- The complete age journey reached Hall level 8 and wall level 8, reloaded at Future, and recorded zero page/console errors and zero HTTP responses with status 400+.
- Fresh `node --test tests/*.test.mjs`: 210/210 PASS, including per-age asset path, dimensions, RGBA channel, attachment anchor, built-in weapon, class gate and duplicate-rig behavior.

## Evidence

- Journey runner: `qa/game-completion-20261020/visual-review/natural-all-age-equipment-live-20261020.mjs`
- Machine report and screens: `qa/game-completion-20261020/visual-review/equipment-all-ages-live/`
- Prior close Hero and Adventure Stone continuity run: `qa/game-completion-20261020/visual-review/natural-equipped-weapon-adventure-review-20261020.md`
- Asset contract and hashes: `assets/derivatives/worn-gear-20261020/manifest.json`

## Limits and open work

The new art is Knight-specific; other classes retain their own role weapons and do not yet get item-specific body cutouts. Hero static plates that already depict a weapon keep the item in its slot, so this review does not claim that the item changes those standing plates. This closes only age-specific Knight weapon continuity, not full equipment coverage, the M01–M30/J01–J18 comparison, all 32 scene traces, independent desktop acceptance, or release acceptance. No APK or device action occurred.
