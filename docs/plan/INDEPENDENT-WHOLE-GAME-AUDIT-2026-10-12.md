Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; custom Node 24.19.0 server/build tools; Python 3.13.7; Android Java/WebView wrapper (physical runtime deferred).
Task: independent Code Review and Testing. Date: 12 October 2026 (Asia/Calcutta).

# Independent whole-game visual and code audit

**Verdict: INCOMPLETE. The 12 October RELEASE_READY banner and blanket visual/scene/rig completion claims are not supported. Physical-device testing remains deferred until the planned game, final build, and independent desktop review are complete.**

Review snapshot: HEAD `1341551da1cfc8f6666eba108d530054c75271bf` plus the existing uncommitted executor changes. This audit changes reports/status pointers only. It does not repair game code or artwork, alter producer acceptance/accounting records, generate images, rebuild/install an APK, contact a provider, or commit/push.

[Reference-versus-runtime gallery](../../output/playwright/independent-audit-20261012/gallery.html) · [Evidence folder](../../output/playwright/independent-audit-20261012/) · [30-mock overview](../../output/playwright/independent-audit-20261012/mocks-30.jpg) · [Phone overview](../../output/playwright/independent-audit-20261012/phone-all.jpg) · [Eight-age Kingdom](../../output/playwright/independent-audit-20261012/eight-kingdom.jpg)

## What was actually checked

- Current scope/precedence in AGENTS, START-HERE, CURRENT-STATUS, DECISIONS, SESSION-HANDOFF, BUILD-PROGRESS, plan README, canonical FULL-IMPLEMENTATION-SPEC, MASTER-PLAN, REQUIREMENTS-TRACEABILITY, VISUAL-DESIGN, mock/art/reference ledgers, installation guidance, adoption/geometry contracts and latest executor prompt. The plan README resolves 121 linked text/JSON documents with no missing links. Historical no-code/portrait/morale-pending/budget figures are not treated as current authority.
- All 30 approved landscape mock compositions at overview scale; native-size inspection of Hero, Forge and Tactical references; live outputs at actual phone/desktop scale. Generated titles, fabricated statistics and known rejected elements in mocks remain excluded from mechanics.
- All 13 primary screens at 825x375, 933x424, 1180x820 and 1280x720, with asserted actual view: **52 correct screen/viewport visits**, no page/asset-load errors. Primary screenshots include empty/locked states, not fabricated active battles.
- **32 separately imported, validated visual fixtures**: four scene families across eight ages, at 1280x720; age was asserted after import. **Eight class fixtures**, with class/view asserted. Mature plots were synthetic level-3 arrangements. These are visual coverage, not earned progression or balanced campaigns.
- Ordinary pointer-driven fresh campaign, Tactical Duel, Auto, result settlement, Retreat focus/cancel/background-blocking at four sizes, Siege start/hero+army deployment, pause and saved paused-defense reload. Additional supporting captures cover six equipped slots, skills, all-spell eligibility, Forge, bag comparison, Story/quests, Adventure, save slots and damaged-save recovery. Gear/Wisdom fixtures are explicitly synthetic.
- Fresh full Node suite with EARNED_SCOPE_OUT redirected to this audit: **127/127 PASS**, 0 failures/skips. Core/equation/save/geometry/consumer tests are bounded automated evidence, not proof of final pixels or every user journey.
- Existing unsigned APK read/CRC/closure verification: **475/475 current files identical across source/dist/www/APK**, no current file omissions/drift/network references, preview application ID, no declared permissions. APK **596,008,420 bytes**, SHA256 `aa115673eaca301d836f3d98d90be7ebe51816347783cdf9cb3c27d20caeb3be`. No build/install/signing was performed.

## Findings, highest priority first

### F1 — P1: All 32 scene acceptances are invalid as completion evidence

`scripts/close_all_32_physical_scenes_20261012.py:143,147,179,596,675-695` assigns usable/PASS/ACCEPTED_BOUNDED_USE without failing on its measured intersections. Roads, banks, decks and approach coordinates are largely constant templates. Tactical deck clearances include hard-coded zero intersections/24px clearances. These are not independent per-source physical tracings.

The saved interface contains **29/32 nonzero pad/obstacle intersections**, with zero minimum clearance for those rows, despite claiming collision-free acceptance. The other three zero-intersection rows also lack defensible full-scene acceptance. Colour heuristics are not semantic ground masks. The Stone overlay visibly draws roads over rocks and bridges/pads away from painted features. Current live Adventure and Defense paths remain schematic lines crossing terrain inconsistently.

There are also **two runtime/source mismatches**: Stone and Medieval Kingdom scene claims refer to different terrain files from the active `reviewed-source-selection.json` binding. For example Stone acceptance inspects production-03, while runtime uses production-01 (still `runtimeApproved:false`). Matching a hash for the wrong active image cannot certify the game.

Evidence: [integrity.json](../../output/playwright/independent-audit-20261012/integrity.json), producer [Stone overlay](../../qa/scene-verification-20261012/kingdom-terrain-stone-verified.png), fresh eight-age scene sheets. Reopen the 32 completion gates; bind the actual displayed terrain, trace painted geometry per source, and make clearance assertions fail honestly before promotion. Do not simply relabel these images or alter legal geometry to hide the mismatch.

### F2 — P1: The producer's visual report does not prove the stated checks

`scripts/audit-mocks-20261012.mjs:131-175,243-250,286-316` does not assert navigation success. **41/52 saved screen records have a different activeView from their label**. Most alleged gameplay views actually show Home; three early records have no active view. Mock comparisons are prewritten Markdown; no comparison is performed. The advertised 48px check uses **44px**. The modal check merely reads existence/inert/active-element values; it never opens and exercises the dialog. Safe-area PASS is also written unconditionally.

The fresh independent 52-screen browser run fixes the evidence gap but finds failures below. Preserve the old report as rejected evidence; it must not justify RELEASE_READY. The fresh Retreat tests really did open the dialog, cycle Tab, block background navigation, Escape-cancel and compare unchanged battle state, and passed at all four sizes.

### F3 — P1: Healer is visibly malformed, and its source transform is misrepresented

The current `class-healer-standing-body.png` has a horizontal magenta line across the neck, detached left-side fragments, overlapping/duplicated arms, and a visibly assembled torso/legs. These defects appear both in the file and the live Healer room.

`scripts/execute_priority1_art.py:34-51` composites five separately positioned parts from v6/v7/v9, then publishes a crop/affine as if it transformed one native sheet (`:94-103`). That single affine does not describe the assembly. The catalog's PARTIAL status is more accurate than the RELEASE_READY prose, but the asset is already rendered. Require a coherent silhouette/anatomy, clean alpha/native and intended-size review, and an honest multi-input composition transform/provenance before visual acceptance. The new body hash/existence test only proves bytes exist.

Evidence: [live Healer](../../output/playwright/independent-audit-20261012/fixture-class-healer.png), [body](../../assets/derivatives/image-complete-20261011/actors/bodies/class-healer-standing-body.png), `src/data/hero-bodies-20261011.json`.

### F4 — P1: Declaring bone hierarchies did not complete runtime animation

`src/client/actor.js:201-204` returns null when `atlas.worldReady` is falsey; the active atlas has no true worldReady flag. The added BONE_HIERARCHY/MOUNT_BONE_HIERARCHY, footContact/contactPhase and JSON animation frame metadata are not consumed by the world renderer. `anatomy.js` remains a single partial Ranger assembly with missing arms/hands and independent pose code.

`main.js:1152,1322-1345,1367` explicitly renders Tactical/Defense actors with time 0, idle and reduced:true. Workers and some Adventure paths are similarly static. Existing static mounts/schematic fallbacks do not prove horse/rider gait, active role-specific movement, casting, hit/death clips, or painted socket/contact integrity. Keep full rig/motion acceptance open and wire reviewed parts/clips into actual consumers before checking clip extremes in real scenes.

### F5 — P1: Android wrapper lacks required confirmation and file selection behavior

Static code review, **not a physical-device test**: `android/app/src/main/java/com/agesofdominion/game/MainActivity.java:21-34` sets a WebViewClient but never a WebChromeClient/file chooser. Home's New campaign replacement uses browser `confirm()` (`main.js:1563,1608`); import and Challenge-file controls use file inputs.

Official Android documentation says that without a WebChromeClient, JavaScript confirm is suppressed and returns false; default file requests are cancelled. Consequently the wrapper leaves campaign replacement and file-import workflows unimplemented for Android even though desktop Chrome supports them. Add local confirmation and permission-free document selection handling, plus explicitly verify the export/download path. Export failure is not independently reproduced here. [Android WebChromeClient API](https://developer.android.com/reference/android/webkit/WebChromeClient#onJsConfirm(android.webkit.WebView,%20java.lang.String,%20java.lang.String,%20android.webkit.JsResult)), [file chooser API](https://developer.android.com/reference/android/webkit/WebChromeClient#onShowFileChooser(android.webkit.WebView,%20android.webkit.ValueCallback%3Candroid.net.Uri[]%3E,%20android.webkit.WebChromeClient.FileChooserParams)).

The zero-permission package check remains valid. Native behavior still requires later device verification after implementation completion; do not install now.

### F6 — P2: Live building mattes and class/kit completeness still fail

Fresh mature-age screenshots visibly show saturated magenta bases/rectangles, including Iron buildings, the Medieval town hall, Gunpowder buildings and Modern hall. `age-buildings.json` still binds v2/live derivatives. A candidate colour scan flags all 80 building entries; that count is **not** a claim that every coloured pixel is unwanted. The visible rectangular remnants in the screenshots are confirmed failures and need per-subject repairs.

All eight classes load, but the full four-kit-era matrix is not complete. Stone Knight falls back to a portrait; Paladin visibly wears steel plate in the Stone fixture; other bodies explicitly have unverified era metadata. Slot numbers can work while worn appearance remains unimplemented. Hero gear/UI must reflect the same equipped identities without mismatched static weapons or armour. The Bronze heavy does now depict horses, harness, crew and a chariot; its substantial ground patch and lack of animation remain bounded limitations. Do not continue calling the current Bronze plate infantry.

Evidence: [eight classes](../../output/playwright/independent-audit-20261012/eight-classes.jpg), [eight Kingdoms](../../output/playwright/independent-audit-20261012/eight-kingdom.jpg), integrity colour candidates.

### F7 — P2: Responsive text, overlays and Load controls have reproducible defects

- At 825x375, Story/War descriptive text is **8.39 CSS px**, Help/Market copy **9.59px**, some headings **10.79px**. `paintSupportBoard`/`paintChamber` (`main.js:274-376`) paint fixed-size SVG text, then `projection.js:35` can use cover sizing without keeping this content in bounds. Help lines run across card boundaries and upper headings are cropped. HTML 48px button dimensions do not prove text/content fit.
- Hero/Forge have correctly sized HTML controls but the phone figure/Forge subject is buried by copy and side columns. Expanded navigation and active Defense dock labels visibly collide or truncate. Scrollability is not proof of a legible initial layout. Four-viewport evidence is desktop CSS/DPR1, not physical safe-inset validation.
- Home **Load** keeps the full gate overlay above the opened panel (`game.css` gate z-index4, panel z-index2; `paintGate` only opens panel). At 1280x720, the centre of **Save slot 3** hits **Continue**, and **Load slot 3** hits **New campaign**. This is a real hit-target obstruction, not just a dim screenshot. [Pointer evidence](../../output/playwright/independent-audit-20261012/load-panel.json).
- `resources()` (`main.js:214-217`) shows the treasury on every non-Home view. Live active Tactical, Defense and result screenshots show it, contrary to the canonical battle-HUD rule.

Use screen-space readable text/flow layouts for supporting panels, preserve scene subjects, and make Load a properly layered/focused surface. Recheck actual pointer hit ownership, clipping and scroll access, not only bounding rectangles.

### F8 — P2: The finished visual experience still differs substantially from the approved direction

The comparison gallery contains the actual mocks and current captures, not a written assertion of resemblance. Kingdom has incomplete perimeter/civic composition and mature settlement density. Adventure still shows labeled pads and schematic route lines rather than inhabited sites registered to the terrain. Tactical lacks the mock's clear grounded formations/initiative presentation; current small stacks are obscured by labels. Defense uses a thick zigzag over the artwork rather than a registered lane. Hero/Forge use a plain gradient/vector room/anvil, with a small or covered subject. Skills, spells, inventory, Story/quests and settings remain mostly generic lists or simple cards; result display is a button on the battlefield rather than the composed outcome panel.

This is required screen/art implementation work, not only final polishing. Keep the owner's approved direction while correcting the mocks' known wrong titles/eras/icon semantics. The full game cannot be called visually complete on the strength of source tests or image file presence.

## Scope coverage and what remains

| Plan area | Fresh code / functional evidence | Visual / remaining gate |
|---|---|---|
| Home, eight-class choice | New campaign and class selection work in desktop; all 8 class fixtures render | Composition/full body/era gaps; Android confirmation issue |
| Kingdom: 18 sites, 10 buildings, production and walls | Core construction/economy/offline/instance tests pass; all 8 mature scene fixtures load | Pads/roads/perimeter/grounding and building mattes fail; no mature-city visual acceptance |
| Eight-age progression | Command-driven suite reaches age7, 8 milestones, Future conclusion | Eight Kingdom/Adventure/Tactical/Defense backgrounds viewed; cross-era character/equipment visual matrix remains incomplete |
| Adventure/navigation/sites/fog/dwelling | Navigation/encounter/dwelling tests pass; fresh entered-Adventure render; earned test buys all 8 creatures | Registered sites/bridge/corridors, travel gait and every ordinary site journey not visually accepted |
| Tactical/Auto/Retreat/result | Legal action/seed/morale/spell tests pass; live Duel Auto resolves, result applies; Retreat passes four-size focus/cancel/background tests | Deployment/formation/initiative/results art and active rigs incomplete |
| Siege/Endless and threat roles | Fixed-step/pause/speed/role tests pass; simulated Siege5/5; Endless20 clears; live deploy/pause/reload pass | Lane/terrain registration, role motion/grounding and dense-wave visual review open |
| Skirmish and local Challenge | Existing isolation/shared-seed tests freshly pass | Full ordinary browser Challenge import/export journey not repeated; Android file selection missing |
| Hero stats/9 skills/8 spells/morale | Source formulas and tests pass; earned Wisdom3, all 8 casts, Resurrection heals **14HP** for **20 mana** | Full class/era equipment appearances, graphical skill/spell presentation and rigs open |
| Six slots/4 qualities/10 artifacts | Earned suite verifies six equipped slots, qualities, loot; fresh comparison UI rendered | Bag/Forge composition and phone overlap fail; art attachments incomplete |
| Army/recruit/rank/8 creatures | Current roster tests and earned unlocks pass; four-size starter Army rendered | Full per-role animation/era/matte/grounding not accepted |
| Market | Bronze transaction tests pass; locked/unlocked rendering sampled | Generic panel/tiny copy; mock-quality presentation open |
| Story, 6 quests, rival, Future | Earned test claims q1-q6; branch/milestone/once-only tests pass | Narrative/quest presentation remains generic; complete ordinary browser branches not exercised |
| Tutorial | Core correct-command progression and sparse-start tests pass | Current cues render; complete fresh pointer-only onboarding journey not rerun in this audit |
| Saves/slots/import/export/recovery | Suite tests recovery/transaction boundaries; fixture imports work in Chrome; damaged-state UI distinct; Defense reload pass | Load slot obstruction; Android dialog/file chooser gap; export/device lifecycle pending |
| Settings/audio/reduced motion/help | Settings/background/audio unit tests pass; portrait rotate state preserved | Tiny/cropped support copy; no subjective audio or device safe-area/performance acceptance |
| Art provenance/consumer contracts | Current asset closure and source hashes checked; Bronze subject correction recognized | Healer composition transforms, physical-scene evidence and full painted-rig gates fail |
| Android/build/offline | Current 475-file APK closure and CRC pass; previewID/no permissions; Java source reviewed | Wrapper integration defects, unsigned artifact, final lean/complete build and physical testing remain open |
| Cloud/account/store/payments | Outside offline runtime scope; no action | No provider/accounting/paid authority change inferred from this audit |

The 19 owner requirements and 16 system requirements in REQUIREMENTS-TRACEABILITY remain subject to their current superseding landscape/full-build-first authority. OWN-05/06/08/10/11/13/14/15 and SYS-14/15 are not closed by this delivery. OWN-01 is a historical execution gate, not a reason to erase subsequently authorized work. Storage/Git/provider gates were not re-audited as game-completion evidence.

## What the passing results mean

The automated earned run uses legal commands and documented simulated income caps, not a human waiting through the campaign. It reaches Future, six equipped slots, all six quests, eight creatures, eight spells, a Siege win and 20 Endless clears. This is significant functional progress. It does not prove campaign pacing, every class/seed, ordinary end-to-end browser play, Android runtime, complete art or owner acceptance.

The independent browser data distinguishes natural starter interactions from synthetic age/class/gear displays. Two audit-harness setup errors were corrected (preserving the Town Hall in fixtures; importing via the real validated import flow instead of fighting pagehide autosave). An already-open Forge comparison is handled explicitly. Final fixture/support/journey reports have no fatal error. The first broad browser report retains its initial fixture error as history; its 52 asserted primary-screen results are valid and the separate final fixtures.json supersedes only that fixture phase.

## Required closure order

1. Correct the unsupported scene, visual-audit and rig completion claims without overwriting historical evidence.
2. Repair source-bound terrain registration and active consumer bindings for all 32 scenes.
3. Repair Healer anatomy/provenance, building mattes, class/kit appearances and remaining actor/scene art.
4. Integrate actual reviewed rigs/clips in the running game and inspect motion/contact extremes.
5. Complete the required mock-derived screen layouts and fix phone readability, control overlaps, Load layering and battle HUD.
6. Implement Android confirmation/file selection/export handling while retaining the offline zero-permission policy.
7. Rerun relevant regressions, finish all planned game/art work, and create/verify the complete final build.
8. Independently review the completed desktop build against the whole scope and mocks.
9. Only then perform physical-device testing and owner review as already sequenced by the owner. No physical-device action was taken here.

Do not freeze the suite forever at 127 tests, treat the old $15.1673 capacity as freshly reconciled spend authority, install an unsigned artifact directly, or interpret this audit as permission to regenerate accepted assets. None is necessary to finish the present review.

## Reproduction and evidence

Use `C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe` (24.19.0). PATH Node is 22.19.0 and is not the audit runner. Start `scripts/serve.mjs --port 4517` for the browser helpers. Helpers create fresh browser contexts and write only this audit's output. Set `EARNED_SCOPE_OUT=output/playwright/independent-audit-20261012/earned-scope.json` before `node --test tests/*.test.mjs` to preserve producer evidence.

- `tests.txt`, `earned-scope.json`: fresh suite and simulated progression.
- `browser.mjs` / `browser.json`: 52 asserted primary screen visits and phone text metrics.
- `fixtures.mjs` / `fixtures.json`: 32 age-mode and 8 class visual fixtures, asserted state/view.
- `journey.mjs` / `journey.json`: ordinary battle/Retreat/pause/reload behavior at four sizes.
- `support.mjs` / `support.json`: synthetic six-slot/Forge/skills/spells/Story and damaged-save checks.
- `load-panel.mjs` / `load-panel.json`: actual pointer-hit ownership for Load overlay.
- `integrity.json`: all32 scene contradictions, active-source mismatches, candidate building matte pixels, producer screenshot mislabels.
- `package-check.json`: separate read-only rerun of the existing package verifier with output redirected; production report untouched.
- `inspected-code-hashes.json`: reviewed source/test/native-file hashes; not a substitute for behavioral evidence.

Audit media under output/ is local evidence and is ignored by Git; this report's source findings stand independently. No new transfer ZIP, cleanup, build, provider call, commit or push was performed.
