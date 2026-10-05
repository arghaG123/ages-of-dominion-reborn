# Visual integration — 4 October 2026 — INCOMPLETE

Code executor pass. No provider call, device install, signing, Git mutation, or Image-file edit. Owner acceptance and device QA stay open.

## Package

- Unsigned release: `android/app/build/outputs/apk/release/app-release-unsigned.apk`
- SHA256 `90d0687844321ef1e0964da884e4e3906b0e7d5d465a94a1c5598da9db46ce75`
- 296,625,603 bytes
- Preview id `com.agesofdominion.game.reborn.preview`, minSdk 24, targetSdk 36
- Merged release manifest lists no `uses-permission`. `allowBackup` is false. `usesCleartextTraffic` is false.
- `dist`, `android/app/src/main/assets/www`, and APK `assets/www` each have 261 files and zero hash mismatches.
- `node scripts/build.mjs` reported 232 local assets and no network references.
- Preserved prior package: `qa/visual-integration-20261004/preserved-fbe989b5-app-release-unsigned.apk`, SHA256 `fbe989b58240bcd7981b993efb6ed4accb894fbf4ae42c73731a2e92efe830db`, 296,623,132 bytes.
- Packaging does not show a native launch, heard audio, or device frame time. Device testing stays STOPPED.

## Commands

- `node --test tests/*.test.mjs` → 82 pass, 0 fail. Includes `tests/connected-journey-20261004.test.mjs` and `tests/war-defense.test.mjs`. Construction and defense clocks in those tests are labeled fixtures, not a natural eight-age playthrough.
- `node scripts/capture-visual-20261004.mjs http://127.0.0.1:4175` → exit 0, `failures: []`.
- `android\gradlew.bat assembleRelease --offline` → BUILD SUCCESSFUL. Not installed.

## Captures

Directory: `qa/visual-integration-20261004/`. `evidence.json` records viewport, `deviceScaleFactor` 1, `devicePixelRatio` 1, panel closed for the scene shots, and PNG sha256 values.

Viewports 825×375, 933×424, 1180×820, and 1280×720 each have home, hero-mage-walk, kingdom-day1, and adventure-travel. At all four, the Mage card is `portrait-card` with box `128,40,500,500`, the card top is below the header (75 to 93px), visible controls are at least 48px, Day 1 has 17 stakes, Hall present, walls `unbuilt` level 0 version `walls-presentation-v1`, terrain `baked-unaccepted`.

1280×720 also has hero walk frames 0–3 at 250ms, travel frames 0–3 at 120ms, forge, army, war, tactical, market, defense, story, settings, help, and defense-siege. ffmpeg is not installed, so there is no encoded clip. Travel frames 2 and 3 share the same sha256, beginning `2022ab292a74`, because the one-cell route had already finished.

## What the pixels separate

- Source: the ancient Mage card still has a complete head. It was not recropped. Knight has no Stone card. `knight-mounted-master` stays rejected. Named rig slices and floored sheets stay withheld (`data-named-parts="withheld"`).
- Live placement: the earlier clip was the card origin plus the cover camera. The card now sits inside the stage and the hero focus. Actions sit in the header.
- Skeleton: the walker and the horse are schematic marks, not reviewed anatomy. The horse is an upright side silhouette with a saddle, rider, tail, and four legs. It is not the floored horse sheet. Preview-east plants 4 hooves. Confirmed travel uses `mountWalk`.

## Still open

Stone baked terrain still shows extra huts and roads outside the empty pads. That painting stays failed development evidence. Adventure, Defense, and Tactical maps are still diagrams. Eight-age biome art, owner section review, positive morale, preservation destinations, and device testing remain their own open gates.
