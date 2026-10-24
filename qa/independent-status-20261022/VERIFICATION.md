## Owner clarification — 22 October 2026: Adventure references are examples, not production maps

The owner explicitly clarified that the supplied Adventure mock pictures demonstrate the intended appearance and are random examples, not game-specific maps. Prior wording calling them approved production paintings was a mistaken interpretation. Directly binding 11 of these reference images and adapting gameplay geometry around them is not accepted progress toward the owner requirement. Withdraw this audit's recommendation to bind Blood Moon to the remaining reference picture. The 11/12 count describes the current mistaken binding only.

Correct direction: retain the examples as visual references and use independently authored, game-specific Adventure maps designed around the required gameplay, landmarks, traversability and mechanics. Existing generated mapFile assets remain available, but their suitability and matching geometry must be checked before reuse. Do not flip the image selector alone: recent site/collision/crossing data was traced to the example pictures. Prepare a source-and-geometry reconciliation, preserving current work and saves. This clarification does not authorize production edits in this verification turn.

# Independent game status — 22 October 2026

**INCOMPLETE.** Current source, bounded fresh browser review, tests and package bytes were independently checked. No completion percentage is justified. This audit changes QA/documentation only; it does not repair production, build an APK, use a provider, touch a device or publish Git changes.

## Verified now

- `node --test tests/*.test.mjs`: **257 PASS / 1 FAIL / 258 total**, about 24.2 seconds. The failure is `tests/adventure-worlds.test.mjs:997`, within the test beginning at line 975: Astral Peaks gold is on blocked ground.
- A separate probe checked all **240 world/layout combinations** (12 worlds × 20 layouts), testing six resource/guard destinations for blocked cells and route existence. It isolated one blocked destination: Astral Peaks, layout index 0, seed 23, gold `[13,5]`. This is static navigation evidence, not full site, bridge, guard, reward or natural-play acceptance. See `all-layout-anchor-probe.json`.
- Current `adventure-worlds.json` and `campaignMapImage()` bind **11/12** supplied owner paintings; Blood Moon selects its generated fallback. Every supplied painting exists. Older 4/12, 8/12 and 10/12 counts are superseded for this binding subtask only.
- Current dependency collector resolves **809 asset paths**, zero missing and zero unresolved templates. That proves file dependency resolution, not art correctness or package inclusion. See `asset-dependency-audit.json`.
- Fresh ordinary UI review used a new campaign on separate origin `127.0.0.1:4543`, leaving existing user saves on other origins alone. Visited Kingdom, Forge, Story, Adventure and Siege preparation; screenshots are beside this report. Browser warning/error log query returned zero. No campaign resources/state were injected.
- Reviewed the earlier same-day core, support, all-world and eight-age captures and their report. They record useful bounded natural progress: 12 one-move/reload world journeys, eight-age progression, Skirmish victories, campaign recruitment/battle settlement, and Defense pause/reload and defeat settlement. Those runs were not rerun end-to-end in this audit.

## Fix these confirmed defects first

1. **Astral gold is inaccessible.** The baseline gold anchor `[13.5,5.5]` floors to `[13,5]`, within the Shrine collision footprint. Repair the anchor or source-correct footprint/approach in `src/data/adventure-worlds.json`; preserve genuine painted landmarks. Rerun all twenty layouts in every world and the full suite. Do not weaken the walkability assertion.
2. **Compact Adventure loses map content.** Fresh Grasslands at 825×375 measures `#terrain`, `#frame` and `#world` at y=0, height=460.8, bottom=460.8: **85.8px below the viewport**. Prior all-world review also records larger Underworld cropping. Repair camera/fit and inset rules in `src/client/projection.js`, `src/client/main.js` and applicable CSS; keep actors, landmark access, inspectors and controls usable. Verify 825×375, 933×424 and 1280×720, both overview and open inspector, edges and later-age mounts. Do not merely clip away unreachable content or shrink all text.
3. **Blood Moon uses the wrong map source.** `src/client/adventure-map-source.js` prefers `runtimeFile`, then `mapFile`. Blood Moon has no owner `runtimeFile`, so its generated image wins. Trace the owner painting's sites, hazards, approaches and crossings before binding it; then prove natural travel, interactions, rewards and reload. Adding a filename alone does not finish registration.
4. **Forge desktop composition fails M22.** Fresh 1280×720 rendering shows the body and shadow suspended over the workshop, a slot rail overlapping the information card, and a large empty inventory panel dominating the view. Compare `forge-live-1280x720.png` with `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/22-forge.jpg`. Repair `paintForge()`/scene layout and CSS around the actual bench, selected item, costs and contextual inventory. Verify empty/locked and populated/craft/equip states at all required sizes. The compact workshop background is present; this is not a missing-image diagnosis.
5. **Siege preparation duplicates the start action.** Fresh 825×375 UI has two visible `Start Campaign Siege` buttons: dock and inspector. Choose one contextual primary entry; ensure all tower rows are reachable by scroll/focus and unavailable reasons remain accessible. Verify deployment, pause/resume and return without duplicate commands. Screenshot: `siege-preparation-live-825x375.png`.

## Required unfinished work, with evidence boundaries

### Equipment, class kits and motion

`src/client/hero-room.js` explicitly limits held-weapon layers to Knight; other worn layers are Knight/Future only. Eight Knight weapon ages plus five Future wearable slots do not establish six-slot appearance across eight classes/four kits. Functional stat equipment and socket icons are separate from visible wear. Finish the required 32 class/kit rows and 192 attachment decisions with real supported layers or contract-approved justified mappings, coherent anatomy/style/mattes, grounded scale and natural equipped combat/travel. Preserve the proven joint-parenting and paired-boot improvements. Recheck Healer from current pixels rather than repeating its obsolete below-foot-staff finding.

Role-, mount- and vehicle-specific motion still needs current natural-scene acceptance. Passing committed-event and synthetic gait tests establishes bounded implementation behavior, not believable movement, attacks, casts or ground contact at gameplay scale.

### Kingdom and physical scenes

Current `kingdom-view.js` selects same-age `none/scaffold/built/tall` paintings, and `paintMaterialWalls()` no longer attaches stretched wall stamps. Those old implementation defects must not be reported as still present. The eight-age natural contact sheet shows integrated wall imagery. Finish independent pixel/state verification of all 32 age/phase combinations: empty plots and wall level 0, construction, completed level 1 and taller upgrades; sharp ground; source-correct gates/crossings; truthful dynamic Hall and owned buildings; mature/dense picking; useful-world coverage. A family filename is not state or geometry acceptance.

Complete current physical traces and rendered review for all 32 age/mode scenes, with real actor extents, lanes, banks, bridges and obstacles. Adventure source binding alone does not close collision-to-paint alignment, fog readability, all-site semantics or all-world journeys.

### Complete the actual player journeys

Close J01–J18 from the authoritative manual using ordinary visible controls, current source hashes and saved state. Retain new successful natural spell, recruitment, battle and progression evidence; do not repeat it as an old failure. Fill remaining assertions for all War modes, full five-wave Campaign Siege victory/reward/once-only settlement, prepared Workshop/tower route, Endless termination/persistence, all classes/creatures, populated Forge, Market, story/quests/Future conclusions, tutorial and recovery flows. The recorded default-roster defeat at wave 2/5 is not a balance verdict. A Workshop runner file/directory exists, but no completed `report.json` was present there in this audit; do not claim that route passed.

Finish actual-browser persistence at supported growth: IndexedDB commit acknowledgements, simultaneous/replaced saves, interrupted writes, corruption/recovery/import/export, quota failure without losing the last good save, and background/resume of active Tactical/Defense. Passing Node CAS/queue/stress tests does not prove the entire browser/native lifecycle. The old five IndexedDB failures are historical, not freshly reproduced by this audit.

### Story and remaining presentation

The earlier same-day report shows rival choices under navigation at 825×375. **This audit did not reproduce overlap:** three lower rival buttons ended at y=309.35 and navigation began at y=311.60 (about 2.25px clearance). Keep robust font/zoom/inset/scroll/focus behavior open; do not label this a current confirmed overlap. Recheck the exact older capture conditions and 933×424. Compare every remaining screen and interaction state with M01–M30 and U01–U16; the broad core contact sheet is not full fidelity approval.

## Package and release gates

Read-only comparisons of `index.html` plus all 53 current `src/` files (54 files total):

- `dist/`: **1 missing, 12 different** from source.
- Native `assets/www/`: **10 missing, 22 different**.
- Build-output APK: **10 missing, 22 different** in embedded web source; 616,295,432 bytes; SHA256 `7bd7fa2de1dbccbc46102484d26378d930e47ea321d696ade2b2763e7b50b69c`.
- Delivery APK: **12 missing, 22 different**; 590,814,691 bytes; SHA256 `7134cec6e54b48178448cb601ddd701893be01167624f767e6d22150ce56928f`.

Exact paths are in `package-source-audit.json`. These are source-only comparisons, not a new full asset/CRC/permission audit. Neither APK can represent the current game. Do not build a checkpoint package to hide unfinished desktop work.

Completion order: repair current desktop defects and remaining scope → independently pass all required mock/scene/mechanics/natural/persistence assertions → build the final web/native/APK snapshot → verify source/assets/package parity, identity, offline permissions and install behavior → later physical-device QA/repair → owner review. Desktop, final package, device and owner acceptance are all OPEN.

## Authoritative work scope

Continue using `docs/plan/ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt` and its original embedded manual, all M01–M30, J01–J18, G01–G16, U01–U16 and 96 original steps. Append current evidence without removing original requirements. Repair → verify → repair failures → recheck is the completion loop. This report supplies current status and priorities, not acceptance or implementation authorization.
