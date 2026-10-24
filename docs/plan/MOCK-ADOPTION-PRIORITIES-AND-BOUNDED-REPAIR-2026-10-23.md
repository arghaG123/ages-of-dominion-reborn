# Mock adoption priorities and bounded repair instructions — 23 October 2026

## Owner clarification and purpose

The owner asks for Critical, High, Medium and Minor visual/functional mismatches, fixing the first three before optional polish. Preserve the game's core functionality and completed work. Whole-game and Adventure mocks are samples of desirable design, not synchronized game states or a requirement to reproduce every pictured feature. Adopt what improves this game; repair what looks wrong or plays badly. Do not restart the implementation.

This clarification supersedes literal-image acceptance criteria that demand invented facilities, exact sample prices, chapter numbers, troop counts, camera scenes or decorative props. It does not remove adopted mechanics, eight-age coverage, three modes, six equipment slots, nine skills, eight spells, campaign continuity or save safety. Earlier contracts remain applicable to actual game requirements. A genuine feature required by the adopted specification cannot be dismissed merely because it also appears in a mock.

This is a planning/triage handoff, not a fresh live game audit or implementation PASS. No production edits, builds, provider calls, save interactions or executor dispatch were performed for it. Historical findings below require current confirmation before repair. The separately recorded owner deferral of M03 dense-city work remains in force; that deferred High issue is explicit, not silently passed or demoted.

## Evidence and why the old loop needs correction

Read together:

- `qa/game-completion-20261023/mock-design-independent-closeout-20261023.md` and its JSON: older 0 closed / 15 partial / 9 failed / 6 unmatched classification.
- `qa/game-completion-20261023/mock-scope-and-live-recheck-20261023.md`: later crossing, truthful empty-loadout hero, Kingdom inspector, Adventure shortcuts, tutorial and Story follow-ups. These supersede older findings for their specific observations.
- `docs/plan/VISUAL-DESIGN.md`, section 8, already says Market is a contextual trading surface and needs no invented extra plot.
- `docs/plan/MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md`, section 1, already says generated names, numbers, facilities and currencies do not create mechanics.
- M01–M30: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/`; overview `../review-overview.jpg` relative to that directory.
- Adventure v4 source/geometry report and contact sheet: `qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/`.

This planner inspected the 30-image overview, retained M07 and M12 screenshots, Adventure v4 contact sheet, current reports and relevant source entrypoints. The retained captures are historical and visibly degraded; their softness/text distortion alone cannot establish a current rendering defect. Current landscape interaction and every individual screen at full resolution were not independently re-run here. Recent 299/299 test results are reported by the executor, not rerun by this planner.

The old tally mixes actual defects, acceptable differences and missing evidence. Do not chase “30 exact matches.” Reassess each assertion under the rules below and keep the historical tally intact as history.

## Severity and status are different fields

| Priority | Meaning | Examples | Required response |
|---|---|---|---|
| Critical | Progress/save integrity fails, a required mode cannot be used, or visual/input disagreement causes destructive/wrong actions | Lost campaign, duplicate rewards/debits, mandatory route blocked, wrong entity receives a purchase | Reproduce safely, fix the responsible logic/input mapping, prove recovery and no repeated transaction |
| High | Major visual incoherence or a primary action/state is misleading or hard to use | Detached wall/buildings, unreadable primary action, gear display lies about equipment, units/targets cannot be distinguished | Smallest effective visual or functional repair; current before/after interaction and pixel check |
| Medium | Core task works but clarity, feedback, hierarchy or consistency materially suffers | Crowded inspector, confusing selection, weak affordability feedback, unclear route/quest status | Local presentation/feedback repair; exercise affected state and compact layout |
| Minor | Cosmetic preference without meaningful usability or truthfulness impact | Exact trim, background prop, ornamental texture, small spacing difference | Defer; cannot hold this repair pass open |

Statuses: `VERIFY` (not established current), `CONFIRMED_FAIL`, `FIXED_VERIFIED`, `ACCEPTABLE_DIFFERENCE`, `DEFERRED_OWNER`, `BLOCKED_EXTERNAL`. An unvisited later age is VERIFY, not a confirmed broken age. An acceptable difference closes only that comparison assertion; it does not certify the screen's other behavior. No current Critical defect is independently confirmed by this planning pass; the save/reward/progression checks below are risk-prioritized verification obligations.

## Fixed adoption decisions: stop asking the game to imitate sample state

1. M02 Day 1: Hall/real starting buildings, unbuilt sites and Walls 0 remain truthful. No finished wall or keep granted for the picture. Adopt terrain quality, clear paths and unobtrusive HUD. Wall growth is checked in real later construction states.
2. M03: Lumber Camp is the functional counterpart of sample Sawmill. Display actual production; no fictitious worker count. Density/integration remains a real visual concern, separately deferred by owner. Never build fake functional buildings into the ground artwork.
3. M05/M06: use the existing Market trade flow. A new Marketplace plot, price table or facility system is unnecessary. Medieval civic focal quality is a separate art/composition issue; do not fake a castle upgrade or discard an explicit age-art requirement merely to close it.
4. M08–M10: use existing age-correct facilities and genuine progression. Sample Residential Tower / Research Lab labels do not independently mandate new economy buildings. Verify the real eight-age content and transitions.
5. M11–M13: preserve the 12 approved game-specific Adventure maps and v4 geometry. Their source examples are inspiration, not runtime substitutions. Overview, readable routes, discovered landmarks, hero, fog, costs and contextual actions matter. A strategic view is valid; a cinematic close-up, parked mount, guard convoy or Woodcutter label is not independently mandatory. Preserve a working crossing focus already implemented; do not add more camera modes for parity.
6. M14–M18: use the actual terrain, roster, mode and wave rules. A swamp versus a gorge, two legitimate formations versus a pictured army, or wave 3 versus sample 14/20 is not a defect. Units, legal actions, terrain collisions, HP, wave/core state and consequences must be clear and correct. A legitimate loss is not proof of a balance bug; do not weaken combat to get a screenshot.
7. M19–M24: actual gear, class, age, inventory and roster determine the display. An empty inventory is valid. Verify populated and changed states with real earned/crafted content, but do not grind for the sample War Axe. Do not introduce durability, item weight, extra abilities or equipment systems solely because generated copy suggests them.
8. M25/M26: render the player's actual chapter, objectives, choices and rewards. Chapter I versus IV is an acceptable comparison difference. Test actual chapter transitions separately; do not replay hours only for the sample chapter.
9. M27/M28/M29: adopt anchored guidance, readable settings and safe recovery. Device frames, mock-language options or unsupported controls are unnecessary. Existing required settings must work and persist.
10. M30 is a style reference, not a new player-facing screen. Adopt a consistent readable realistic/semi-realistic icon family. Do not regenerate all icons to match a particular bronze bevel.

## Repair queue: specific problem, smallest change, stopping check

### Critical — verify first; repair only actual failures

| ID / affected mocks | Evidence state and task | Where to inspect | Stop when |
|---|---|---|---|
| C1 / M01 M29, all transactions | Recent CAS conflict/export repair exists; live failed-export and damaged recovery remain unverified. Use isolated saves: conflict, export, invalid import, valid backup, reload. Never overwrite the user's slot to test. | `src/client/save-feedback.js`, `src/client/main.js`, `src/core/save.js`, `src/core/storage-adapter.js`, `src/core/campaign.js` | Last-good committed save survives; failed candidate can be exported/read back; recovery is explicit; reload restores committed state; stale writer cannot overwrite it |
| C2 / M11–M18 M21 M26 | Verify actual required travel/encounter/settlement/progression continuity. Check illegal targets, combat result once, quest claim once, movement/mana/payment once, resume after interruption. Existing passing evidence is retained if applicable. | `src/core/navigation.js`, `battle.js`, `defense.js`, `campaign.js` | Normal visible journey completes; invalid/repeated actions do not corrupt state; the same result survives reload |
| C3 / M02–M24 M27 | Verify art/hit-target alignment for primary actions at supported landscape sizes. Elevate to Critical only if mis-targeting causes destructive action or blocks mandatory progression. | `src/client/main.js`, `projection.js`, `kingdom-view.js`, CSS; existing geometry consumers | Tap/click selects the pictured entity; overlays do not pass clicks through; confirmation describes the exact resulting transaction |

### High — fix visually wrong or misleading presentation

| ID / affected mocks | Evidence state and task | Where to inspect | Stop when |
|---|---|---|---|
| H1 / M02–M10 | Retained Kingdom captures show sparse composition; later notes confirm open-yard concern. Dense-city redesign is `DEFERRED_OWNER`. For other confirmed defects, repair only wrong wall state, overlap, floating contact, blur or depth. Preserve legal sites and dynamic owned buildings. | `src/client/kingdom-view.js`, `main.js` (`paintMaterialWalls` / building painter), `presentation.js`, reviewed terrain bindings | No-wall/scaffold/built/upgraded state is truthful; applicable buildings sit on terrain and remain selectable; no foreign wall stamp or broad blur. Deferred density stays explicitly open |
| H2 / M01–M30 | Current compact readability/input evidence is incomplete. Inspect sharp native captures before changing fonts/art. Fix primary text/control clipping, obstructed playfield, unusable target sizes and inconsistent dominant HUD clusters. | `src/client/game.css`, `polish.css`, `main.js` | Readable prices/status/actions at 825×375, 933×424, 1280×720; primary targets retain 48×48 CSS px with disjoint hit regions; closed Kingdom inspector retains the existing ≥80% useful-world requirement |
| H3 / M14–M18 | Prior reviews focus too much on biome/count mismatch. Verify and fix real actor scale/contact, distinct sides, selected unit, target/effect clarity, lane/core readability and correct animation timing. | `src/client/main.js`, `screen-presentation.js`, `presentation.js`, existing actor/FX consumers | Player can identify active unit, legal target, result, threats and remaining core/wave state; motion/effects follow committed action; no fake crowd or extra deployed army |
| H4 / M19 M22–M24 | Empty-loadout cloth hero and Army/Forge layouts have later repair evidence: preserve them. Verify six-slot equip/unequip, compare, forge-to-inventory, class/age identity and owned roster. Repair wrong item attachment or misleading artwork only if reproduced. | `src/client/hero-room.js`, `main.js` (`buildHeroInventoryPanel`, `paintArmy`, `paintForge`), gear/body catalogs | Real changes alter correct socket/item/stats and persist; empty state stays honest; weapon/body bounds do not intrude into controls; owned and available units are distinguishable |
| H5 / M11–M13 | Keep Adventure art/bindings. Verify route marker, hero, bridge and site hitboxes line up; focus view must not relocate game state. Repair only demonstrated registration or obstruction. | `src/client/adventure-map-source.js`, `adventure-crossing-presentation.js`, `adventure-travel-presentation.js`, `main.js`, `projection.js` | Visible move follows legal path, costs accurately, reveals fog correctly, selects right site and survives reload; no need for pictured convoy or cinematic remake |
| H6 / M27 | New target/cue repairs exist. Verify fresh tutorial and later guard-discovery guidance. Fix wrong target, blocked action or misleading step. | Existing tutorial logic in `src/client/main.js` and campaign consumers | Early build guidance points to the actual usable control; steps advance after real success; skip/review and return work without resetting campaign |

### Medium — local usability and consistency

| ID / affected mocks | Do only if still present | Stopping check |
|---|---|---|
| D1 / M03–M10 | Selected building thumbnail/name, actual production, cost/time/upgrade feedback; reuse recently repaired two-column inspector and `kingdom-production.js` | No clipped cost labels; selected entity and action are clear; close returns to world |
| D2 / M11–M13 | Hero/movement/resource hierarchy; route confirmation; existing Quests/Bag/Camp/Diplomacy shortcuts | Four existing routes open correct features; context panels and tray do not overlap; invalid/insufficient movement feedback is clear |
| D3 / M16–M18 | Result/reward/casualty hierarchy, wave progress and tower affordances | Practice rewards remain explicitly absent; campaign deltas match actual settlement; current wave/core and next action are readable |
| D4 / M20–M23 | Available/learned/locked skill states, legal spell targets/mana, affordability, item comparisons and empty/populated inventory feedback | Real eligible action succeeds, ineligible action explains why, deltas are correct; no fabricated catalog entries |
| D5 / M24 | Roster selection, recruit cost/capacity, owned counts and formation feedback | Recruit once changes correct stack/balance and reload preserves it; selected card and available capacity are clear |
| D6 / M25–M29 | Story/quest status, tutorial text, settings return, safe-recovery wording | Actual chapter and once-only rewards are clear; no collision; settings persist; recovery never promises an unsaved state was committed |
| D7 / M01 M30, shared | Remaining icon-family, active/focus state and secondary typography inconsistencies | Same action has same symbol/meaning; resource amounts readable, names accessible in details; no ornamental redesign loop |

### Minor — defer

Exact mock stone/metal trim, prop positions, NPC crowd density unrelated to readability, decorative cart/convoy, lighting preference, exact castle silhouette where the adopted era/focal requirement is otherwise met, icon bevel, sample title branding, exact line breaks, and a few pixels of harmless spacing. Do not demote unreadable text, wrong-era identity, obstructed targets or deceptive state to Minor. M03's large empty-yard composition issue remains High/deferred, not ordinary decorative density.

## All 30 screen mocks: bounded adoption map

Priorities refer to applicable checks, not a claim that every check currently fails.

| Mock | Adopt / verify | Allow without repair | Queue |
|---|---|---|---|
| M01 Home | Clear Continue/New/Load hierarchy, real save availability, readable art/text | Different title/castle/background | C1, H2, D7 |
| M02 Day 1 | Coherent starter terrain, paths, honest unbuilt plots and wall state | No completed wall/keep | C3, H1, H2 |
| M03 Stone | Grounded buildings/wall, useful selected-building inspector | Lumber Camp name and actual income | H1 deferred density; D1 |
| M04 Bronze | Age identity, real construction and readable inspector | Current town population and plot layout | H1, H2, D1 |
| M05 Iron | Age identity and clear real Market exchange | Market as existing screen | H1, H2, D1 |
| M06 Medieval | Coherent civic focal point and real Market access | No invented Marketplace facility | H1, H2, D1 |
| M07 Gunpowder | Correct age art, foundry/action visibility | Existing wall topology and real army | H1, H2, D1 |
| M08 Industrial | Actual age transition and age-correct structure feedback | Sample-specific facility names | C2 verification, H1, D1 |
| M09 Modern | Actual age transition and era coherence | Sample Residential Tower | C2 verification, H1, D1 |
| M10 Future | Actual final age/conclusion and truthful upgrades | Sample Research Lab | C2 verification, H1, D1 |
| M11 Adventure | Legible landscape/hero/routes/minimap and useful shortcuts | Current approved world and real stats | H5, D2 |
| M12 Crossing | Registered crossing, clear cost and confirmation | No convoy or exact camera angle | C2, H5, D2 |
| M13 Site | Site identity, real offer/count/cost/capacity and persistence | Farmstead/dwelling versus Woodcutter; no parked mount | C2, H5, D2 |
| M14 Deployment | Legal placement, owned stack tray, readable field | Different biome and true unit count | C3, H3 |
| M15 Action | Selected stack, turn order, legal actions, feedback | Different battle composition | C2, H3 |
| M16 Result | Outcome, real casualties/XP/loot, clear return | Honest zero rewards in practice | C2, D3 |
| M17 Defense prep | Legal towers/deployment, core/lane/cost clarity | No fictitious hero/army deployment | H3, D3 |
| M18 Wave | Live wave/core/threats/effects and settlement | Any genuine wave; actual mode horizon | C2, H3, D3 |
| M19 Hero | Truthful body/gear, six sockets, stats and compare | Current class/age/items; empty cloth body | H4 |
| M20 Skills | Nine skills, learned/available/locked state, real points/offers | Different ranks or backdrop | D4 |
| M21 Spells | Eight spells, legality, mana/targets/effects | Existing spellbook location and different battlefield | C2, D4 |
| M22 Forge | Selected craft preview, six-slot catalog, quality/cost/result | Existing recipe names | H4, D4 |
| M23 Inventory | Clear grid/selection/equip/compare and persistence | Empty slots, another earned item; no invented weight | H4, D4 |
| M24 Army | Age-correct lineup and real roster/recruitment | Current troops/creatures and count | H4, D5 |
| M25 Story | Readable narrative/choices and consistent chapter HUD | Any actual chapter/backdrop | C2 when settlement involved, D6 |
| M26 Quests | Progress, eligibility, reward and once-only claim | Different chapter/objective progress | C2, D6 |
| M27 Tutorial | Anchored guidance and real step progression | No phone frame/exact screenshot stage | H6, D6 |
| M28 Settings | Real settings, persistence, close/return, readability | Different underlying scene; no invented settings | H2, D6 |
| M29 Recovery | Safe detection, export/backup/import/last-good flow | Different safe dialog arrangement | C1, D6 |
| M30 Materials | Consistent realistic icons, states and readable sizes | No literal material-board screen | D7; cosmetic remainder Minor |

## Execution protocol for the existing implementation chat

1. Preserve the shared dirty checkout, current saves, approved maps and implemented improvements. Read this priority guide before old mock checklists. Do not restart all 30 screens, rebuild the app architecture or regenerate asset sets.
2. In one existing ledger, classify each outstanding assertion as defect, acceptable difference or verification gap. Attach C/H/D priority and evidence status. Deduplicate shared CSS/HUD/root causes; a shared fix is one task with multiple affected screens.
3. Freeze the Critical/High/Medium queue for this pass. Only newly reproduced defects of those severities can extend it; a new preference cannot. Keep M03 density `DEFERRED_OWNER` and Minor polish outside the active queue. State explicitly if a deferred High issue prevents full visual completion.
4. Check C1–C3 first. If verified sound, retain the implementation and move on. Then H2 shared legibility, H3 battle/defense, H4 gear/roster, H5 Adventure interaction, H6 tutorial, and any non-deferred H1 defects. Finally D1–D7. Reuse existing proof when its source dependencies and tested behavior remain valid.
5. Before each edit record one reproducible symptom, screenshot/action, expected game behavior, exact affected files and exit test. A lack of a matching mock chapter/price/convoy is not a symptom.
6. Make one small causal repair. Test relevant behavior and inspect the affected live screen. If the same symptom survives two repair attempts, stop repeating cosmetic edits: diagnose the underlying transform/state/layout/asset cause and select a different bounded approach. If an external capability is unavailable, record that exact blocker and continue independent rows; do not report PASS or invent a replacement feature.
7. Use the approved browser route and an isolated audit campaign. Do not bypass browser policy or use the existing user save for destructive checks. If landscape access is unavailable, mark live verification blocked and stop source churn aimed at an unseen screen.
8. Use 825×375, 933×424 and 1280×720 for changed shared layout; sample all affected screen families. Use current full-resolution captures to distinguish actual rendering faults from capture compression. Inspect actual pixels and action behavior, not screenshot filenames or DOM counts alone.
9. For gameplay proof use visible natural actions. Isolated fixture states may exercise rare layout/overflow/late-age variants and must be labeled; they do not prove earned progression. Reuse a valid continued natural campaign for genuine age transitions rather than replaying for exact mock content. All eight ages and required journey outcomes remain verification scope.
10. Retain each verified row. A change to unrelated source does not automatically invalidate all prior work: map changed functions/styles/assets to affected evidence, rerun those cases and one shared-shell smoke check. A shared rendering change may legitimately affect many screens; record its impact honestly. Record exact source identity for new captures without calling older captures current.
11. Run focused tests during fixes and `node --test tests/*.test.mjs` once for the integrated final source; rerun after meaningful subsequent changes. Do not run the whole suite after every copy/spacing change. No broad refactor, paid art or new mechanic solely for mock likeness.
12. Finish the active C/H/D queue with fixed-and-verified or explicit unresolved rows. Produce one closeout listing remaining Minor polish, owner-deferred High work and actual external blockers separately. A report is not a substitute for authorized repairs; a blocker is not permission for infinite retries. “Bounded repair pass complete” is distinct from whole-game acceptance.
13. Preserve the existing release sequence: complete independent desktop verification before final snapshot APK, then later device QA and owner review. No checkpoint APK just to show progress. This guide neither authorizes provider/build/device/Git action in the planner chat nor waives the executor's existing controls.

Minimum evidence row:

`id | mocks | severity | symptom/expected | status | current-source identity | campaign/mode/age | viewport | before/after capture | actual action/result/reload | focused test | remaining limitation`

Done means the stated game-specific defect is gone and its real outcome works. Acceptable differences are documented once. The game need not become a pixel copy of internally inconsistent sample images.
