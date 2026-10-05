> **QA archive location update — 4 October 2026:** Superseded APK files named below have been retired from the QA working folders after verified backups. Their exact bytes remain in the two qa-retired stores; see ../storage-cleanup/QA-CLEANUP-2026-10-04.md and its hash/path restore index. Current package 02f85e52 remains in Android build outputs. Historical build outcomes are unchanged.

# Code AI resume — INCOMPLETE — 4 October 2026

No commit and no push. No provider call, lock edit, device install, or Image-file overwrite. Ready-work detail: `CODE-READY-WORK-MATRIX-2026-10-04.md`.

## This pass

- `node --test tests/*.test.mjs` → 91 PASS. That run includes the seated-rider scale already in `src/client/main.js` (`scale: 0.34`, saddle `y + 34`). The browser crop shows the partial ranger seated on the v4 horse. A red guard marker shares that cell and sits beside the rider's head. That is placement, not a horse matte defect. Bobbing is still not a gait.
- On-disk v4 horse hash is now `1e6e597702438a40b3b6da983bc3502e8c68d8aa31eb4f330e65a54f0bb3b189`. The older recorded hash `cf20f1a3…` does not match the file. The consumer uses the file that was checked at 130px. Image interface files were not edited.
- Iron heavy consumer is `assets/derivatives/actors/v4/troop-iron-heavy.png`, sha256 `620b7997…`. At 130px it is a war elephant with howdah, tusks, and four feet, without a floor slab. The older live plate stays unused.
- Gunpowder heavy, future ranged, and future heavy use their v4 files as single-pose plates capped at 130px. Contact marks remain and are labeled. Stone melee, stone ranged, and industrial ranged stay on their old plates and are captioned provisional. Legionary and Steam Walker stay the v3 substitutions. The medieval mounted knight is not relabeled.
- Motor transport and future transport are 64px static reviews. Ground is still visible at 130px, so they are not drawn at travel-horse size. No saddle was measured, so no rider is attached. Future travel in the browser shows the craft. The modern motor path is covered by the unit test; this pass has no separate modern-age screenshot.
- Pending ancient knight card remains the labeled review card. It is not owner accepted. The knight body on that screen is still the stick figure.
- Kingdom affine `[60,-10,25,35,170,165]` and Hall scale 0.1312 are unchanged.
- Browser evidence: `qa/code-matte-journey-20261004/`. Seed 123456789. Live construction clock. Travel to 10,5 spent once. Tactical winner `p`. The battle added no bag item.
- Forge fixture, labeled: Armory and 5000 of each resource. Flint Club moves Attack from 3 to 4. Unequip returns Attack to 3. After a weapon swap, slot 2 reload keeps five worn items and two bag weapons.
- Siege, Speed 2x, pause, resume, settlement, slot reload: flag `siege:siege-1-157` = `e`, 0 waves. Endless, pause at core 400, resume, settlement: flag `endless:endless-1-355` = 0. Both are core losses. The starter towers sit off the lane. This is not a cleared siege.
- Age fixture, labeled: Town Hall level 8 and 500000 of each resource. Advance age reaches Future. Checkpoints `checkpoints/age-1.json` through `age-7.json`. This is not an earned economy.
- `npm run build:apk` completed. New unsigned APK sha256 `02f85e52c5c1aab755e42374bfd2c166f7ba0d5e23519314830de0e00b5694bd`, 319,425,603 bytes. 266 files match dist, www, and the package. Preview id `com.agesofdominion.game.reborn.preview`, minSdk 24, target 36, no listed uses-permission. Not installed. Preserved `90d06878…` is still 296,625,603 bytes at `qa/code-ready-20261004/preserved-apk/app-release-unsigned.apk`. Preserved `04c66255…` is 297,724,620 bytes beside it. The older `fbe989b5` copy remains.

## Still open — INCOMPLETE

- Owner visual acceptance, including the pending ancient knight card.
- Device launch, heard audio, and device frame timing. Device QA stays STOPPED.
- The baked Kingdom painting and the schematic Adventure, Tactical, and Defense boards.
- Starter towers do not cover the lane, so Siege and Endless settle as defeats with 0 waves.
- Separate hoof parts, so the review horse has no gait. Motor and future craft still show ground above 64px.
- Ranger hands and upper arms are still missing. Other classes are not painted bodies.
- Positive morale effect, for that effect only.
- Git preservation destinations. Do not untrack `assets/` or push.
- A natural eight-age economy. The played Future path used an injected Hall and resources.
- Native launch is not established by the unsigned package.

## Next ready Code work

The starter defense leak is a ready defect: the two starting towers are drawn off the lane and the legal 2x session never clears a wave. The owner rejection in CURRENT-STATUS also asks for one coherent Stone-age play loop. That work is separate from missing art, owner review, morale, and storage.
