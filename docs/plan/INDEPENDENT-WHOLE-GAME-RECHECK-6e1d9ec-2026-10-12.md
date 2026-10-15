Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; custom Node 24.19.0 tooling; Python 3.13.7; Android Java/WebView wrapper.
Task: independent Code Review and Testing. Date: 12 October 2026 (Asia/Calcutta).

# Current whole-game audit after the newer implementation

**Verdict: INCOMPLETE. Some earlier defects are fixed, but the claim that all eight findings are resolved is unsupported. Physical-device testing remains deferred until all planned game/art work, the final build and independent desktop verification are complete.**

Current inspected commit: `6e1d9ecc121e6d3cf4d73db206407679b797e45c`. This recheck supersedes the current-status conclusions of the [earlier audit](INDEPENDENT-WHOLE-GAME-AUDIT-2026-10-12.md), while retaining its plan coverage, historical evidence and unchanged findings. The newer commits appeared before audit closeout, so the changed source, artwork, browser flows and package were checked again. This verifier made no game/art/provider/build/device/Git changes.

[Current 30-mock comparison gallery](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/gallery.html) · [Phone screens](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/phone-all.jpg) · [All eight classes](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/eight-classes.jpg) · [Evidence folder](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/)

## Fresh verification

| Check | Current result and limit |
| --- | --- |
| Full Node suite | **127/127 PASS**, zero failures/skips; 44.1 seconds. Output and earned progression evidence redirected to this audit folder. |
| Primary browser coverage | **13 screens × four viewports = 52 asserted visits**, no page/HTTP errors. Sizes: 825×375, 933×424, 1180×820, 1280×720. |
| Age/class visual coverage | **32 age/mode fixtures and eight class fixtures**, actual age/class/view asserted after validated file import. Synthetic mature plots, not human-earned campaigns. |
| Live gameplay | Fresh ordinary Tactical Duel, Auto/result settlement, Retreat focus cycling/background blocking/Escape cancellation at four sizes; Siege hero/army deployment, pause stability and paused active-defense save/reload pass. |
| Supporting surfaces | Fresh six-slot equipment/Forge/skills/spells/Story fixtures at phone and desktop sizes, Adventure entry, save slots and damaged-save UI. |
| Current unsigned APK | **475/475 source/dist/www/APK files identical**, CRC PASS, preview application ID, zero declared permissions, no current network references. Existing artifact read only; no new build/install. |

Current APK: `android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk`, **587,326,144 bytes**, SHA256 `9dee031c81975dc104a419bc4c47e55e4e8badd065c6738caba68eeba6fde16e`. The older 596,008,420-byte result belongs to the earlier snapshot.

The new Home hides navigation by design. The initial rerun stopped when its old helper attempted hidden navigation; the corrected helper uses the visible Continue button first and then asserts the requested view. The initial failure is retained separately. Age/class captures were repeated with image-settle time to avoid mistaking partly decoded SVG images for missing bodies. Final reports contain no fatal error.

## What is fixed or materially improved

- **Android confirmation/file selection source gap:** `MainActivity.java` now installs a WebChromeClient, handles confirm/cancel, launches the system chooser and returns selected URIs. The earlier claim that these handlers are absent is closed at source-review level. Actual native confirmation/import/export, cancellation and lifecycle behavior remain for later device testing.
- **Home Load pointer obstruction:** fresh 1280×720 hit tests reach all three Save/Load slot controls, including the previously obstructed third slot. This is a bounded desktop fix, not a claim about every device size.
- **Battle treasury:** `resources()` now excludes Tactical and Defense; live active-mode screenshots confirm it is hidden.
- **Building magenta rectangles:** all 80 active building entries use the revised bindings and the same candidate-colour scan returns zero flagged entries. Fresh eight-age Kingdom screenshots no longer show the previous magenta rectangles. This closes that specific defect, not all alpha, grounding or physical registration gates.
- **Home and general UI:** Home has a left book-like sidebar and large terrain view; the gold/slate styling, controls and Hero slot presentation changed. Help/War text now wraps. These are real changes, but do not establish all-30-mock acceptance.

## Remaining actionable findings

### P1 — Scene completion evidence is still invalid (original F1)

The acceptance script and interface were not repaired by the follow-up commit. The existing **29/32 intersecting scene records**, hard-coded tactical clearances, unconditional PASS/ACCEPTED_BOUNDED_USE assignments, and Stone/Medieval Kingdom runtime-source discrepancies remain. `scripts/close_all_32_physical_scenes_20261012.py:143,147,179,596,675-695` still cannot establish physical tracing/clearance acceptance.

Fresh [Adventure](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/eight-adventure.jpg) and [Defense](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/eight-defense.jpg) sheets show schematic paths crossing terrain/painted features without correct registration. For example, Bronze Adventure's overlaid crossing is separate from the painted bridge; Modern Defense traverses painted buildings. Rebind and validate the actual displayed source and trace legal paths against its painted features. Merely adding a status paragraph does not close this gate.

### P1 — The original producer visual audit remains unreliable (original F2)

`scripts/audit-mocks-20261012.mjs` and its report are unchanged: **41/52 mislabeled screen records**, prewritten mock-comparison conclusions, a 44px check advertised as 48px, and unexercised modal claims remain historical rejected evidence. The independent fresh browser reports provide valid bounded evidence; they find unresolved visual problems. Replace the producer's unsupported conclusions with actual assertions and inspected pixels before calling the game complete.

### P1 — Healer anatomy and provenance remain defective (original F3)

The new Healer hash is `babb4fda8ae7f42d85f5735aa11576ca93d153a26fe038344f75765953a92f35`. The native still shows a thin horizontal coloured line across the neck, detached left fragments, disconnected/overlapping arm assemblies and incoherent clothing/boots. The [settled live Healer capture](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/fixture-class-healer.png) confirms malformed anatomy at intended size; [native audit copy](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/healer-native.png) preserves exact current pixels for review.

`hero-bodies-20261011.json` adds `magentaNeckStripeRemoved:true` and a composition description, but retains a single-source affine for the five-input assembly in `scripts/execute_priority1_art.py:34-51`. That does not supply the actual per-part transforms/provenance. Repair the silhouette/anatomy and record the real composition; keep the existing PARTIAL gate until independently accepted.

### P1 — Articulated rigs and class/kit coverage are unfinished (original F4/F6)

Passing `animTime()` and clip strings in `main.js` is an improvement over forced time-zero rendering. However, `drawPlate()` (`src/client/actor.js:362-387`) still draws one image and applies whole-image bob/rotation. Its `pose:'single'` branch ignores requested attack/death pose changes. `drawActor()` still returns null without `atlas.worldReady`; the active atlas does not enable it. Bone hierarchy metadata is still not consumed to articulate the painted characters/mounts.

Hero now displays the same class body even when `data-kit-match='mismatch'`. Stone Knight visibly wears medieval plate. `paintEquippedSockets()` adds three fixed-position icons (weapon/offhand/helm), while armor, boots and accessory do not change the body. These icons sit over already-painted gear and do not establish per-body sockets or the required four kit eras. Complete the actual rig/era/gear consumers and inspect their motion/contact extremes.

### P2 — New Tactical attack-selection branch reads a nonexistent field

`src/client/main.js:1175` compares the stack ID with `state.battle.active`, but the battle contract stores a queue and exposes `activeStackId(battle)` (`src/core/battle.js:40`). The fresh live probe finds active stack `army-1`, no `active` field, and zero attack clips. Consequently this added attack branch never selects the current stack. Use the real battle/action contract and distinguish an actual attack event from merely being the active turn. [Probe](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/attack-probe.json).

### P2 — Phone readability and control layout remain broken (original F7)

The new chamber camera (`main.js:559-564`) fits the entire SVG board into the available height. At **825×375**, measured text is now approximately **5.46px Story**, **5.82px War/Settings**, and **6.55px Help/Market**. Text wraps, but the resulting screen-space copy is too small. [Actual-size Help](../../output/playwright/independent-audit-20261012/followup-6e1d9ec/825x375-help.png).

Expanded navigation clips names across all phone views. Active Defense dock labels overlap one another. Equipped Hero/Forge still lose important copy/subject area when panels are open on a short screen. The Forge phone capture clips its resource-cost line beneath the side panel. No target bounding rectangle below 48px was reported, but that does not establish text fit, visible hit area, or accessibility. Fix responsive flow and screen-space typography, then check pointer ownership and clipping at all four sizes.

### P2 — Whole-game mock fidelity remains incomplete (original F8)

Home is closer to the proposed structure, but a global palette/font change does not implement the remaining approved compositions. Kingdom registration/density, Adventure inhabited sites, Tactical formation/initiative readability, Defense lane integration, Hero room art, Forge subject presentation, supporting panels and the result composition remain incomplete in the current comparison gallery. The refreshed screenshots cover all 30 reference rows and all eight ages; the known fabricated text/wrong-era details in generated mocks remain excluded from mechanics authority.

## Completion order and verification boundary

1. Correct unsupported scene/visual/rig completion claims and bind evidence to actual runtime sources.
2. Finish source-specific scene geometry, Healer/art provenance, class kits, equipment appearance and articulated actors/mounts.
3. Fix Tactical attack-state selection and responsive screen layouts; finish the remaining mock-derived presentations.
4. Rerun affected regressions and independent whole-scope desktop review, then verify the completed final package.
5. Perform physical-device testing only after the whole planned game/build is complete, as requested. Test native dialogs/file flows, lifecycle/save integrity, insets, performance, audio and touch behavior then.

The earlier report's full plan coverage matrix still applies except for the fixes explicitly closed above. Passing automated simulated progression is not a human pacing/balance study. This audit does not claim every possible campaign/class/seed/action path, subjective audio approval, Android runtime, owner acceptance, signed release readiness, provider/invoice status or cross-device asset transfer verification.

Audit evidence is under `output/playwright/independent-audit-20261012/followup-6e1d9ec/`: tests/earned-scope, browser, fixtures, journey, support, load-panel, attack-probe, building-colour scan, package-check, reviewed-source hashes, captures and gallery. It is local and ignored by Git. Existing producer records and prior audit evidence were preserved. Only audit documents/status pointers and independent evidence were changed by this verifier.
