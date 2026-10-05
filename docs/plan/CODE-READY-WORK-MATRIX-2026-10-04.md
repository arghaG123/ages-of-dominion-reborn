> **QA archive location update — 4 October 2026:** Superseded APK files named below have been retired from the QA working folders after verified backups. Their exact bytes remain in the two qa-retired stores; see ../storage-cleanup/QA-CLEANUP-2026-10-04.md and its hash/path restore index. Current package 02f85e52 remains in Android build outputs. Historical build outcomes are unchanged.

# Code ready-work matrix — INCOMPLETE — 4 October 2026

Canonical IDs are OWN-01–OWN-19 and SYS-01–SYS-16 plus SYS-12a from `REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md`. This pass consumed pixels and hashes. It did not treat Image summary flags as acceptance. `codeAIHandoffReady` stays false. State stays INCOMPLETE.

`node --test tests/*.test.mjs` → 91 PASS after the rider-scale edit and the consumer bindings. Browser evidence is `qa/code-matte-journey-20261004/report.json`. Unsigned APK `02f85e52c5c1aab755e42374bfd2c166f7ba0d5e23519314830de0e00b5694bd`, 319,425,603 bytes, 266-file closure. Not installed.

## This pass

- Iron heavy, gunpowder heavy, future ranged, and future heavy point at the checked v4 files, pose `single`, `staticMaxHeight` 130. Hashes are in `src/data/plate-catalog.json`.
- Stone melee, stone ranged, and industrial ranged keep their previous plates and carry a provisional caption. v4 slabs and the prone sheet are listed under `rejected` and are not the consumers.
- Motor and future transport are in `src/data/static-mounts-v1.json` at 64px. Ages 6 and 7 draw them. No rider is attached.
- Horse review hash is the current file `1e6e5977…`. The ranger seat in `08-mounted-travel.png` matches the 0.34 scale. The guard marker shares the arrival cell.
- Natural seed 123456789 dropped no bag item. The labeled Forge fixture proved Attack 3 → 4 → 3 and a five-slot reload.
- Siege flag `e` and endless flag `0` are core losses. The towers in `13-siege-paused.png` sit off the lane.
- Age fixture reached Future. It injected Hall level 8 and 500000 of each resource.
- Prior packages `90d06878` and `04c66255` remain under `qa/code-ready-20261004/preserved-apk/`.

The rows below from the previous pass stay as history where they are not replaced by this section.

## Ready work done in this pass

- Ranger binding `src/data/anatomy-binding-v1.json` uses corrected roles. Hands and upper arms stay missing. `forearm_hand_left`, `quiver_cloak`, and the v3 horse stay withheld. Overlap remeasure: `python scripts/code_ready_measurements.py --check`.
- Pending ancient knight card: `assets/consumers/code-20261004/portrait-ancient-knight-pending.png`, sha256 `ceb56f2c77c577bee849562cf34091d965adf3dae018382dcf60f6b2a992c7a3`. `portraitCard('knight', 0)` stays null. Medieval knight stays age 3. Image’s separate opaque card `assets/derivatives/portraits/v4/hero-knight-ancient-card.png` was not overwritten and is not the runtime card.
- Iron melee and industrial heavy plates point at the real v3 substitution files, pose `single`. Advertised `*-1k.png` names do not exist.
- v4 horse `assets/derivatives/mounts/v4/hero-mount-horse.png`, sha256 `cf20f1a339268daf13b32e2acb5bfe7b232928e3e88a11fa0ccde42d6b980bf0`. Bottom 187 rows are transparent. Travel draws it as one pose with at most a 1.5px bob. Hooves are not separate parts. The v3 floor-band file stays withheld. Screenshot: `qa/code-ready-20261004/followup/02-mounted-review.png`. The ranger sits on the saddle. Legs are partly hidden by the horse. This is a review sample, not an accepted mount.
- Army review captions sit under the plates. Iron Age Legionary is the clean substitution. Iron Age War Elephant still shows the older floored plate. Screenshot: `qa/code-ready-20261004/followup/01-iron-captions.png`.
- Kingdom affine `[60,-10,25,35,170,165]`, Hall scale 0.1312, and the baked terrain file were not changed. Proposal only: `docs/plan/KINGDOM-SCENE-PROPOSAL-V1-2026-10-04.json`.
- Manual starter journey, live construction clock, one-charge confirm, five War starts with Endless and Siege paused: `qa/code-ready-20261004/manual/report.json`. Acceleration is none for construction. Endless and Siege are fixtures. The rolled bag item was seen in the Forge sentence and was not equipped in that capture.
- Age prices from live rules: `docs/plan/AGE-PROGRESSION-MATRIX-2026-10-04.md`. That file is not a played eight-age journey.
- `npm run dev` is `node scripts/serve.mjs`. An occupied port prints the selected port and exits without stopping the other process.
- `npm run build:apk` preserves the previous release and debug APKs, builds dist, syncs www, and runs `assembleRelease` through `cmd.exe`. A direct spawn of `gradlew.bat` returns `EINVAL`. The new unsigned package is sha256 `04c662556e21f3ca6f25752c8f44427756481d59fc5e05949409bc118594de1a`, 297,724,620 bytes. 265 files match across dist, `android/app/src/main/assets/www`, and `assets/www` inside the APK. `aapt dump badging` reports `com.agesofdominion.game.reborn.preview`, sdk 24, target 36. `aapt dump permissions` lists no `uses-permission`. The previous `90d06878…` package (296,625,603 bytes) is at `qa/code-ready-20261004/preserved-apk/app-release-unsigned.apk`. The older `fbe989b5` copy remains at `qa/visual-integration-20261004/preserved-fbe989b5-app-release-unsigned.apk`. Not installed.

## Per-ID layers

| ID | Source / derivative / spatial | UI / runtime | Owner / device / storage | Next ready task |
|---|---|---|---|---|
| OWN-01 | Section reviews are open | Implementation is authorized | Owner acceptance open | Owner reviews sections. Code does not wait on this for other rows |
| OWN-02 | Fresh `src/client`, `src/core`, `src/data` | No old executable import | Dirty tree, no commit | Keep authoring here |
| OWN-03 | Ranger parts and two substitution hashes bound. v4 horse hash bound as a review | Other v4 rows are automatic keys or residual floors | Image files not overwritten | Bind a class only after a pixel pass of that class |
| OWN-04 | Three modes connect in source and in the manual starter | Live builds, recruit, travel, tactical settle, defense, save | Full site-by-site play is not claimed | Equip the rolled bag item on a later manual pass |
| OWN-05 | Active affine and Hall scale held | Day 1 logical state passes | Baked painting still shows developed content | Owner compares the proposal. Do not replace the terrain from Code |
| OWN-06 | Ranger standing figure is a partial painted review | Pending knight bust is a card, not a body | Owner review open | Keep missing hands visible as missing |
| OWN-07 | 17 empty sites, Hall 1, walls unbuilt at start | Manual build dropped empty sites 17 to 13 | Hall registration unaccepted | No local geometry change |
| OWN-08 | Eight ages in rules and the age matrix | Plate review can show ages 2 and 5 without changing the campaign age | Not a played eight-age journey | Leave the balance matrix separate from the starter |
| OWN-09 | Legal roads and one-charge spend | Double confirm stayed disabled | Painted continuous terrain unaccepted | Keep the proposal versioned |
| OWN-10 | v4 horse single pose plus painted ranger | `data-gait=single-pose`, `data-hoof-articulation=not-separated` | Not owner accepted | Separate hoof parts do not exist, so do not invent a gait |
| OWN-11 | Seven accepted ancient cards, medieval knight at age 3, pending ancient knight below that | Ranger is the only bound painted class | Other rig labels remain wrong | Do not extend the skeleton |
| OWN-12 | Defense roles, pause, 2×, deploy | Manual Endless and Siege were paused and reloaded | Dense owner observation open | A full wave clear is not a ready local task |
| OWN-13 | 7×10 rules and manual clicks until settlement | The post-battle line is the idle tactical sentence | Owner combat pass open | Record the next manual fight with the equip control on Forge |
| OWN-14 | Era plates for the review ages | Iron heavy is still the floored elephant, not the steam walker | Wrong-role rows stay withheld | Retarget a plate only when its own pixels pass |
| OWN-15 | Rival, quests, milestones in source | Story chapter opened in the manual pass | Owner read-through open | No further Code task until review notes arrive |
| OWN-16 | This matrix and the resume | Handoffs name the open rows | — | Keep INCOMPLETE |
| OWN-17 | Installed environment already recorded | No new credential request | — | None |
| OWN-18 | Image policy | Not this executor | Accounting and invoices stay Image’s | No provider call |
| OWN-19 | Preview package | Not installed | Device STOPPED | No install, sign, or store |
| SYS-01 | Economy rules | Manual builds spent on the live clock | — | None ready |
| SYS-02 | Creature labels and age plates | Iron legionary caption is under the figure | Walker fringe and floored plates remain | None until a new clean plate exists |
| SYS-03 | Six slots, compare text | Forge sentence shows worn, next, and cost | Item paintings are not accepted cards | Equip was not clicked in the manual capture |
| SYS-04 | Forge blocks without an Armory | Market stays closed in Stone | — | None |
| SYS-05 | Nine skills, eight glyphs, ranger partial body | Positive morale effect still pending | That effect only | Do not invent the morale result |
| SYS-06 | Route preview and one spend | Review horse plus ranger on the adventure map | Eight painted biomes incomplete | Biomes are Image content |
| SYS-07 | Tactical rules | Manual settle reached | Owner pass open | None |
| SYS-08 | 1/60, pause, 2× | Device frame timing unverified | Device STOPPED | None on device |
| SYS-09 | Seven chapters and future conclusion | Story opened | Owner read-through | None |
| SYS-10 | Local buses, reduced motion, help | Heard audio unverified | Device STOPPED | None on device |
| SYS-11 | Tutorial cues | Manual builds followed the starter steps | Not an owner tutorial pass | None |
| SYS-12 | Save slot 1 load in the browser | Ordinary device storage unverified | Device STOPPED | None on device |
| SYS-12a | Migration and fault probes remain in the suite | — | — | Keep the probes labeled |
| SYS-13 | Skirmish and Challenge do not pay campaign gold | Technical | — | None |
| SYS-14 | Preview id, min 24, target 36, no `uses-permission` | Unsigned `02f85e52…`, 319,425,603 bytes, 266-file closure | Not installed. Prior `90d06878` and `04c66255` preserved | No device install |
| SYS-15 | 48px targets held in the manual four-size pass | No device 60 fps | Device STOPPED | Re-measure only if a later edit moves controls |
| SYS-16 | All five War options started | Endless and Siege paused on purpose | Replay is local | Do not call a paused fixture a cleared siege |

## Durable blocked checkpoint

These actions stay blocked. They do not stop the other rows.

| Action | Evidence |
|---|---|
| Owner visual acceptance | No owner section sign-off in this pass |
| Positive morale effect | Still an owner decision. No invented bonus |
| Device launch, heard audio, physical 60 fps | Device testing STOPPED. No install |
| Git preservation | No commit and no push. Destinations are not a Code mutation in this pass |
| Kingdom baked scene acceptance | `assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png` remains the live painting. Proposal images are diagrams |
| v3 horse as a world mount | `assets/derivatives/mounts/v3/hero-mount-horse.png` flat bottom band |
| Non-ranger rigs | v4 knight pilot is `FAIL_NO_PAINTED_OVERLAP`. Other corrected names do not add missing sides |
| v4 stone melee, motor mount, industrial ranged | Residual dirt, residual floor, or a prone caption sheet. Not bound |
| Natural eight-age play | `docs/plan/AGE-PROGRESSION-MATRIX-2026-10-04.md` is computed, not played |
| Cleared Siege or Endless | `qa/code-matte-journey-20261004/report.json` records core losses with 0 waves. The towers are off the lane. That placement is the next ready defect |
| Natural bag drop on seed 123456789 | The guard win added no item. Equip was proved on the labeled Forge fixture |
| ffmpeg motion video | ffmpeg is absent. Evidence is PNG frames |

The next ready Code task is the starter defense leak: towers sit off the lane, so Siege and Endless never clear a wave. Owner art review, morale, device testing, and storage destinations stay scoped blockers and do not stop that repair. The product remains INCOMPLETE.
