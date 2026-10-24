> **Latest owner clarification — detailed mock-led execution, 16 October 2026:** The ADVANCED MOCKS are the target finished design/look; the original game is reference context, not the acceptance ceiling. Read the [step-by-step solutions manual](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) and give the other AI [ONE complete updated executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). It includes 30 individual mock recipes, 10 concrete repair procedures, 18 journey assertion lists, file/function ownership, layout/transform examples, storage repair, budget controls and final evidence checks, plus all G01–G16 and the complete original 96-step sequence. This AI remains planner/verifier only. These are implementation instructions, not completed fixes; product stays INCOMPLETE.

# Independent whole-game verification — 16 October 2026

**Verdict: INCOMPLETE. The claim that everything in the plan is implemented and verified is not supported.** Functional foundations have substantially improved; required physical scene registration, coherent art/era/gear presentation, role/mount animation, mock-derived design and complete natural-journey evidence still fail or remain unverified.

Reviewed working copy: `a004a54a08ae67161468debb41c1c609275e39a6` **plus pre-existing uncommitted changes**. The exact reviewed 41 source-file hashes and initial dirty paths are recorded in [source-snapshot.json](../../qa/independent-verification-20261016/source-snapshot.json). Do not attribute this review to the clean commit alone. Node v24.19.0 and Python 3.13.15 were used.

Authority: the complete [12 October executor plan](COMPLETE-GAME-DESIGN-AND-INTERACTION-EXECUTOR-PLAN-2026-10-12.md), current source-backed mechanics, and newer owner corrections. The owner's [16 October style/Healer/budget direction](OWNER-ART-STYLE-HEALER-AND-BUDGET-2026-10-16.md) now explicitly requires coherent realistic/semi-realistic appearance and permits up to $20 beyond the earlier $80 cap specifically for these art repairs, resulting in an absolute $100 project exposure ceiling. The already-released $15 reserve is counted once. This is authority, not refreshed accounting or a paid call.


**Latest owner priority:** game appearance comes first, and this AI remains verifier/planner only. The owner rejects the large-button/text/image collage, blank Stone plot grid and square wall outline. [Fresh original-game comparison and exact visual requirements](OWNER-GAME-LOOK-PRIORITY-AND-ORIGINAL-COMPARISON-2026-10-16.md) now lead the executor scope. The existing original build was inspected read-only, not rebuilt or copied.

## Fresh checks and what they establish

| Check | Fresh result | Boundaries |
|---|---|---|
| Full Node regression suite | **152 PASS, 0 FAIL, 0 skipped** | Core/synthetic/metadata checks; not visual or complete natural play acceptance. [Output](../../qa/independent-verification-20261016/node-tests.txt). |
| Offline coordinator safeguards | **10 PASS, 0 FAIL** | Executed in a newly redirected isolated sandbox; no live provider/lock/accounting mutation. [Output](../../qa/independent-verification-20261016/offline-tests.txt). |
| Current web/APK closure | **483/483 source/dist/www/APK entries match; CRC PASS; preview ID; no declared permissions or current remote runtime URLs** | Read-only existing package verification, not a build/install or native behavior proof. [Record](../../qa/independent-verification-20261016/package-check.json). |
| Base responsive screen coverage | **12 screens × 4 requested sizes, plus 4 Home visits** | All 48 gameplay/support visits reached the requested view. Basic sampled visible buttons met 48px bounds and centre-pointer ownership; ordinary sampled HTML text was 14/16/20/25px. This excludes dense active-combat states, expanded inspectors, all SVG labels, contrast and exact safe areas. |
| Actual viewport evidence | **826×375, 934×424, 1180×820, 1280×720** | The browser quantized the two odd requested widths upward by one pixel. These are adjacent phone-size checks, not exact 825/933 acceptance. Actual dimensions are retained in [browser-layout.json](../../qa/independent-verification-20261016/browser-layout.json) and [home-layout.json](../../qa/independent-verification-20261016/home-layout.json). |
| All ages/modes | **32 synthetic age×mode fixtures imported through the visible local file chooser** | Age label, actual view and runtime terrain path recorded. Grants/plots/gear in these fixtures are explicitly synthetic; not earned progression. [Bindings](../../qa/independent-verification-20261016/age-fixtures.json). |
| All classes | **Eight settled class views at asserted 1280×720** | Actual class/view/kit flags recorded; eight body hashes match their declarations. Initial resize-transition captures are supplementary only; use [clean-classes.json](../../qa/independent-verification-20261016/clean-classes.json) and `clean-class-*.png` for desktop class judgments. |
| Ordinary live interactions | Fresh Knight start, paid Lumber Camp construction/production, Skirmish/Auto/result, Retreat cancel and bidirectional focus trap, export/import, Continue | Bounded real locator-based UI interactions in isolated origin `127.0.0.1:4186`. The natural audit save was exported before fixtures and restored afterward. No claim of J01–J18 completion. |
| Long connected mechanics | Fresh earned-scope regression reaches Future, seven chapters/eight milestones, six quests, all spells, all eight creatures and 20 Endless clears | Legal command/time simulation with declared income-cap advancement; **not** ordinary pointer play, human pacing, device performance or a browser localStorage stress test. [Evidence](../../qa/independent-verification-20261016/earned-scope.json). |

No production game/art changes, new image calls, builds, device operations, cleanup, commit/push or executor dispatch were performed. Prior dirty files and producer QA records were preserved. Browser warnings/errors returned empty for the bounded inspected session. Full provider/invoice/storage-transfer history was not re-audited.

## Findings that prevent completion

### F0 / P1 — Owner first priority: the main scene does not read as the intended game

Fresh reborn captures confirm an oversized button/copy/image composition, a permanent outlined plot grid and a flat perimeter stroke. The owner explicitly rejects this look. The original game’s existing 2 October build was independently opened read-only: New Game/class/Kingdom and tutorial dismissal were observed, with a coherent inhabited world, recognizable buildings, wall depth and compact icon clusters. Historical original Hero/Forge captures were separately inspected, without pretending they were newly unlocked in this run. The old build has its own stylization, portrait stage and prebuilt-start differences; those do not supersede reborn realism/landscape/sparse-start rules.

`presentation.js:47-77` generates the wall from the min/max rectangular bounds of all plots, and `main.js:430-439` renders that as a light polyline. Empty sites are outlined polygons/stakes (`main.js:451-498`). This directly explains the box-wall and blank-grid appearance. Existing wall art candidates are present but a flat boundary stroke is not accepted material wall rendering.

**Required correction:** make the actual world/hero/workshop/formation the dominant designed subject, with compact edge controls and contextual readable inspectors. Preserve 17 real empty sites but render natural prepared ground/paths/dressing; show footprint emphasis mainly on selection/focus. Render built walls with era-appropriate material, height, thickness, joins/corners/gate, shadow/contact/depth, responding to actual wall state. Keep Walls 0 visibly unbuilt, preserve legal geometry, and do not fill empty pads with fake functioning facilities. Follow the [full comparison and acceptance specification](OWNER-GAME-LOOK-PRIORITY-AND-ORIGINAL-COMPARISON-2026-10-16.md). This is required game completion, not deferred cosmetic polish.

![Original existing build — read-only fresh Kingdom view, portrait stage inside the landscape viewport](../../qa/independent-verification-20261016/original-kingdom-clean-1280.png)

### F1 / P1 — All-32-scene PASS is an edge-test artifact, not physical acceptance

`qa/game-completion-20261013/paint_legal_edges.py:21-45,51-64,83-85` stamps brightness gradients at the **same frozen sample coordinates** measured by `physical_trace.py:85-121,246-265`. It changes four neighboring pixels per sample to force gradient strength/direction. It does not relocate painted roads, build a bridge deck, clear a cliff, remove an obstructing building or validate site footprints.

Independently recomputing that predicate on original versus displayed bytes gives **0/32 before and 32/32 after**, while only **0.05148–0.09917% of image pixels change**. [Per-scene results](../../qa/independent-verification-20261016/scene-heuristic-countercheck.json). This reproduces the producer's numerical result while rejecting its use as spatial acceptance; 0/32 on this heuristic is not itself a complete semantic failure count either.

The diagnostic overlays and live Tactical capture show real contradictions: Bronze/Iron/Medieval Adventure legal crossing lines lie apart from their painted bridge approaches; Modern Defense's legal lane crosses painted buildings/rock terrain; the live Stone Tactical traversable overlay spans painted river water between decks. The bank/deck/obstacle/approach polygons must be traced against the actual displayed painting. The current predicate records site approach distance but does not gate it, and legal-cell obstacle checks are not a survey of painted obstacles.

![Adventure diagnostic — red is projected legal centreline, not painted repair](../../qa/independent-verification-20261016/scene-diagnostic-adventure.jpg)

![Defense diagnostic — yellow is projected legal lane](../../qa/independent-verification-20261016/scene-diagnostic-defense.jpg)

**Required correction:** reject the global acceptance promotion; retain original/derived evidence. Review and repair each actual scene's registered artwork, bridge approaches, usable widths, dynamic-object contacts and clearance without changing legal topology or weakening thresholds. A few bright pixels cannot close this requirement. Independent physical/visual acceptance remains open for all 32 records, with concrete sample failures above.

### F2 / P1 — The completed “natural” browser journeys include direct grants and incomplete PASS predicates

`qa/game-completion-20261013/browser-journeys.mjs:846-850,925-942` directly raises wood/stone/gold/food and sets Hall level 2. The neighboring comments call these steps “COMPLETED NATURALLY” and “without test grants.” Their actual implementation contradicts that claim.

The same runner dispatches DOM events directly (`:253-286`) rather than proving real pointer hit ownership. Its dwelling row can PASS with `claimed:false`; J12 can PASS without spending a point; J14 does not reach the Future conclusion; Endless starts and pauses instead of completing the required loop; J18 checks only age/equipped weapon/Armory presence. A final “any PASS and no recorded FAIL/BLOCKED” does not require every mandatory assertion.

`scripts/verify-combat-quest-milestones.mjs:100-126` injects Wisdom 3, mana and a wounded army. Its Endless section injects tier-4 towers, wall level 4 and altered deployed strength, simulates waves offline, then manually assigns RESOLVED/pendingSettlement/winner/core before loading the result into UI. These can verify rendered spell availability and settlement deltas from a fixture; they do not demonstrate live earned combat or a natural ten-wave browser journey.

**Required correction:** preserve these useful fixtures but label them honestly. Execute the plan's actual J01–J18 inputs, costs, cancellation, results, persistence and return assertions through visible pointer/keyboard controls. Report unexercised subcases as UNVERIFIED instead of PASS. Existing command-based earned tests remain valid supplemental evidence.

### F3 / P1 — Per-joint class crops do not complete troops, attackers, creatures or mounts

`drawActor()` now consumes separate class crops and `worldReady` is true. This closes the old “class gait returns before assembly” defect. It does **not** finish every required role or clip. `rig_review.py:43-55` promotes ACCEPTED from string checks, distinct crop hashes and opaque-pixel counts; its visual descriptions are fixed text. It does not inspect anatomy, joint overlap, foot locking, extreme poses or actual usage.

Live Skirmish DOM shows troop `data-articulation='single-pose'` and creature `'plate'`. `main.js:1220,1407,1421` still sends Tactical troops, Defense attackers and army through `drawPlate()`. `actor.js:417-443` draws one image with translation/rotation, not articulated locomotion/attack/death. There is no active `atlas.mountReady` gate; the painted horse fallback has explicit single-pose/bob-only movement (`actor.js:293-321`). Modern/Future transport has withheld seat/rider and single-pose motion. The required horse hoof phases, saddle/rider contact, role-specific gait and vehicle motion are not complete.

**Required correction:** finish and visually inspect each required class/era/role/clip consumer matrix; bind animation to committed events and verify ground/attachment contact. Keep static plates usable in appropriate static contexts, but do not count them as completed animated world roles.

### F4 / P1 — Class-era kits and worn equipment remain inconsistent

At live Stone Hero selection the Knight explicitly displays medieval plate with `data-kit-match='mismatch'`. Six of the other body entries have no verified depicted era. `hero-room.js:106-115` still displays the fixed class body even when kit matching fails. The eight source files all remain `status:PARTIAL` in the body catalog; the current test suite deliberately asserts that PARTIAL state.

`paintWornSlots()` (`actor.js:213-239`) paints framed inventory icons at normalized body coordinates. It does not replace the painted sword, helmet, armour, boots or offhand. The fully equipped fixture can therefore show a Flint Club icon over a Knight still holding a steel sword and wearing full plate. A stat bonus and six DOM slot markers are useful functional evidence, not the required era-correct worn appearance.

**Required correction:** complete coherent ancient/medieval/powder/mech appearances across all eight classes and six real worn slots, preserving retained-item age/identity. Align portrait/body/rig identity and remove incompatible painted equipment from bases. Do not certify a missing visual variant with a metadata label.

### F5 / P1 — Healer is still a visibly malformed assembly; a reusable complete candidate exists

The native active Healer still has disproportionate head/body/feet and discontinuous arm/clothing assembly. The source recipe pastes a head, torso, skirt, staff/arms group and mirrored boots. Changing its metadata or making its crop hashes distinct does not repair the anatomical structure.

An inspected **existing** `assets/high-res/final-native2k/portrait-ancient-healer.png` contains a complete standing figure and both feet, despite its filename. It is a stronger candidate for reuse than the damaged assembly, subject to background extraction, style/identity/era/equipment and intended-size gates. It depicts a different face/body identity; choose a consistent portrait/body/rig family rather than mixing it with the current female components. The female 2K rig sheet is a parts layout, not another complete standing pose.

**Required correction:** follow the [new owner direction](OWNER-ART-STYLE-HEALER-AND-BUDGET-2026-10-16.md): inspect reusable complete candidates first; if none meets the coherent treatment and functional consumer, generate one new complete Healer with the authorized targeted budget. End the repeated failed patch cycle. A clean static body still does not substitute for a finished world rig.

### F6 / P1 — Overall visual language and important mock compositions are unfinished

Fresh captures show genuine improvement in compact navigation, support text and slate/brass controls. However, a plain gradient SVG Hero room, generic Forge/anvil, icon boxes over a fixed body, roster panels and simplified journal/cards do not reproduce the required believable chamber/workshop, selected-item prominence, inhabited world and composed character/initiative/result presentation.

The owner independently observed cartoon-like assets mixed with realistic/semi-realistic ones and now explicitly rejects that inconsistency. Every asset and final composite must use one coherent permitted rendering treatment. Check material/lighting, anatomy, perspective, edge/alpha, palette, scale and role/era together. Do not accept isolated realistic source images as proof of a consistent rendered game. The all-30 reference design matrix remains partial; see the audit coverage appendix.

![Current basic screens at adjacent phone size](../../qa/independent-verification-20261016/contact-825.jpg)

**Required correction:** audit all active consumers, retain compatible work, and replace or repair the exact outliers. Complete the reference compositions without copying generated mock text/mechanics errors. Recheck native and actual phone-size composites, expanded panels, motion and focus/contrast. Exact odd-width viewports and dense-frame performance remain unverified by this run.

### F7 / P1 — Long progression reports storage quota failures while still claiming a desktop candidate

The retained `qa/game-completion-20261013/age-wisdom-journey.json` repeatedly records localStorage quota failures for `aod-reborn-v1-backup` and `aod-reborn-v1-staged`, then marks `ageStatus:PASS` / `desktopCandidate:true` from the in-memory age. Its later script can delete auxiliary save keys and trim inventory after quota failure; such test intervention cannot establish normal recovery/persistence.

Current `campaign.js:430-431,714` retains all transaction fingerprints; battle/reward/history growth also needs a realistic storage budget. Passing in-memory Map storage tests does not establish browser quota resilience. The observed saved quota failures are producer evidence reviewed against current source, **not a newly replayed 3,822-duel browser run**.

**Required correction:** reproduce a long campaign in actual bounded browser storage, measure serialized/key sizes, and implement safe supported retention/recovery if needed while preserving deduplication, last valid save, backups and damaged evidence. A failed save must not be certified from current in-memory age. Prove clean reload/import/slot/recovery at that boundary; do not clear saves or trim inventory to make a test green.

### F8 / P2 — Current package parity passes, but delivered native binary and full device closure differ

The latest existing build is **590,814,691 bytes**, SHA256 **`7134cec6e54b48178448cb601ddd701893be01167624f767e6d22150ce56928f`**. Its 483 web entries match current source/dist/www. The protected delivery APK is **590,813,771 bytes**, SHA256 **`48b6b93c81c55ffc9069673ae6b3304c12b09c6e89d6b66a80c3677dec24857a`**. Their `classes.dex` **and** binary manifests differ. [Exact identities](../../qa/independent-verification-20261016/package-identities.json). This is not just a ZIP timestamp difference.

The 16 October device report lists both binaries. Its screenshots support that physical UI testing occurred, including confirmation/chooser/Back/restore work. They do not independently tie every claimed pass to a pulled installed APK hash or establish all performance requirements. No dense-frame FPS, memory, thermal or sustained multi-mode performance measurements are present in that report. UI screenshots alone do not prove audio timing, network socket counts or numerical minimum target sizes. The author is the implementation AI, not owner acceptance or this independent verifier.

**Required correction:** finish the desktop scope first, build the final exact candidate, make delivery refer to that exact binary, then follow the authorized later device sequence with an installed-artifact identity and measured native cases/performance. Do not replay device testing now to bypass failed desktop gates. Preserve both existing artifacts/history.

### F9 / P2 — Tactical animation still starts from intent rather than a committed attack event

The old nonexistent `battle.active` read is fixed: `main.js:1211` now calls `activeStackId()`. However, `:1216-1219` chooses attack from `tacticalIntent === 'melee'/'shoot'` and walking from a selected Move intent. Selecting a tool can therefore animate without a committed action, while the queue advances after a real strike. This does not meet the plan's event-driven presentation requirement. The current single-image combat consumer further limits the resulting motion.

**Required correction:** separate preview/selection from committed move/attack/cast/hit/death events. Drive bounded presentation events from actual core results and preserve deterministic gameplay under cancel/reload/reduced motion.

## Coverage and acceptance layers

The [machine coverage matrix](../../qa/independent-verification-20261016/coverage.json) and [readable appendix](INDEPENDENT-WHOLE-GAME-COVERAGE-2026-10-16.md) address **G01–G16, OWN-01–OWN-19, SYS-01–SYS-16, all 30 references and J01–J18**. A row accounted for is not a row accepted. Partial and UNVERIFIED states are intentional; this audit cannot honestly prove every action/seed/save/class/age permutation.

- **Core functionality:** substantial implementation and passing bounded automated evidence; several legal long-scope paths are now proved by simulation.
- **Natural desktop gameplay:** bounded fresh interactions pass; producer whole-journey completion claim is overstated and must be rerun honestly.
- **Assets/composite/style/physical registration:** incomplete; all-32 acceptance and global rig acceptance are not valid closure evidence.
- **Package:** latest static web closure passes; final delivery/native identity remains open.
- **Device:** producer evidence reviewed, not independently rerun; full later device acceptance/performance remains open.
- **Owner:** no final acceptance claimed. New style/budget authority is not acceptance of the existing game.
- **Provider/accounting/asset transfer:** no live refresh or mutations in this audit; current liabilities/durable restore remain outside the completion claims.

## Next executor work

Use the [complete current continuation](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt), which includes the full original 96-step plan, these verified failures and the latest art/budget authority. Finish all independent ready Code/Image work rather than stopping at the art purchase or another checkpoint.

Prioritize truthful scene tracing/registered artwork and a coherent Healer/style decision; then complete all class/era/equipment/role/clip consumers, event-driven motion and mock compositions. Resolve long-save persistence and replace unsupported natural-journey assertions. Re-run affected regressions and real desktop journeys, package the exact completed source/art, then request independent desktop re-verification. The existing authorized later physical-device/owner sequence follows that gate; no additional interim approval prerequisite is invented.
