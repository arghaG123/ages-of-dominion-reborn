Language/framework/version: JavaScript ES modules/HTML/CSS/SVG; Node24.19.0; custom serve/build scripts. Android configured Java21/Gradle8.11.1/AGP8.7.3/SDK36/min24; Python local image processing.

> **Owner visual/playable build priority — 5 October 2026:** [Owner clarification](VISUAL-PLAYABLE-BUILD-OWNER-PRIORITY-2026-10-05.md); complete successor [Code prompt](CODE-AI-VISUAL-PLAYABLE-WHOLE-BUILD-PROMPT-2026-10-05.txt) and [Image local-delivery prompt](IMAGE-AI-VISUAL-PLAYABLE-LOCAL-DELIVERY-PROMPT-2026-10-05.txt). Primary target is the30owner-approved Vertex LANDSCAPE mocks, indexed by assets/mocks/INDEX.md. Build the whole visible/playable eight-age game first; final fine polish afterward. Basic Home/layout/buttons/terrain/plots/Army/Forge/mode screens are build requirements. Each meaningful delivery requires actual reference-versus-result images; Code also provides live URL and playable interaction evidence. Establish Stone visual grammar then extend all ages/screens without stopping at Stone. Existing audit facts/INCOMPLETE status, scoped blockers, NO_NEW_PAID_CALLS, frozen geometry and deviceSTOPPED persist. This turn wrote planner docs/prompts only; no game/art production/test/build/provider/device/Git/storage work or executor dispatch. Earlier task-priority ordering below is historical where it conflicts.

Language/framework/version: JavaScript ES modules/HTML/CSS/SVG; Node v24.19.0 verified; custom serve/build scripts. Android configured Java21/Gradle8.11.1/AGP8.7.3/SDK36/min24. Python3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1 measured.

> **Latest independent recheck / complete next tasks — 5 October 2026:** Resume the complete [Code execution prompt](CODE-AI-NEXT-AFTER-V8-RECHECK-2026-10-05.txt) against [fresh audit](BOTH-AI-LATEST-RECHECK-2026-10-05.md) and [current matrix](CURRENT-REQUIREMENTS-RECHECK-2026-10-05.md). First fix keyboard background activation during Retreat; retain four verified UI repairs. Complete all independently ready whole-game workflows, naturally prepared Siege and versioned texture/consumer work. Guide delivery, owner visuals, Image partial flags, deviceSTOPPED and morale are scoped exceptions. Earlier checkpoints below are preserved history, including the obsolete ask-guide-then-stop next action. No executor dispatch by planner.

> **Code executor closeout — 5 October 2026, INCOMPLETE:** HEAD `63d79a3`. Bundled Node v24.19.0. `node --test tests/*.test.mjs` → 99 tests, 97 PASS, 2 FAIL, exit 1. Failures: missing `kingdom-stone-day1-composition-v4-guide.png` and `v5-guide.png`. Symbols: `acceptMapActivation`, `retreatNotice`, `stackCaption` in `src/client/tactical-ui.js`; delegated `#world` pointer lifecycle, `#retreat` confirm, `#labels` overlay, and `.forge-decision` in `src/client/main.js`. Eight ready static plates bound in `src/data/plate-catalog.json` (`0-heavy`, `1-melee`, `1-ranged`, `2-ranged`, `4-melee`, `4-ranged`, `6-melee`, `7-melee`); `2-heavy` already matched. Joints and v8 terrain proposals unbound. Affine and Hall scale frozen. Browser `qa/code-executor-20261005/browser-report.json` 16/16. Natural journey equips `loot-160-0-accessory` and reloads; Defense stays ACTIVE after 2 waves. APK `92f47e7e…`, 359,122,611 bytes, 275-file closure, not installed. Prior `df96e182` preserved. Device STOPPED. No commit. Next: owner supplies the two exact guide PNGs; rerun the suite; let the natural siege reach pending settlement without an injected army or resources.

> **Code snapshot before the redraw repair — 5 October 2026, superseded:** 94 PASS, 2 guide FAIL, reported on Node v22.19.0. No v6 image binding. APK `df96e182…`, 319,431,581 bytes, 267 files. That package is preserved.

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
