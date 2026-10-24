> **Current owner clarification - 16 October 2026:** The findings below describe the preceding plan wording and its corrections. The owner requires the plan to be the complete execution source of truth. [Manual sections 0 and 10](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) now bind every concern to implementation, repair and current evidence, including deterministic fit/storage decisions and final completion rules. Use [ONE authoritative executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt). This adds documentation requirements, not an implementation PASS or budget expansion.

# Independent semantic audit of the complete plan — 16 October 2026

**Verdict: the plan covered the major product scope, but it was not yet complete or precise enough to execute reliably. This audit found and corrected 11 documentation issues: four P1 and seven P2.** No required product feature was intentionally removed. The corrected instructions remain an implementation specification; the game stays **INCOMPLETE**.

The main defects were not missing headings. Some instructions mixed different mechanics, omitted the exact completion route, or specified a safeguard without enough failure ordering to implement it safely. Others could be read as contradictory when the manual and original 96 steps were combined. A 30/18/96 structural PASS did not detect those defects.

Give the other AI **[ONE complete corrected executor file](ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt)**. It embeds the [updated manual](MOCK-LED-IMPLEMENTATION-SOLUTIONS-MANUAL-2026-10-16.md) verbatim, including binding A01–A08 corrections, all G01–G16 contracts and the original 96-step sequence verbatim. The owner can hand over that one file; this report explains the audit, rather than being a second execution prompt. No executor was messaged or dispatched.

## Authority, reviewed inputs and evidence limits

This new chat follows the owner's switch-first request and planner/verifier-only instruction. Canonical root is `C:/dev/ages-of-dominion-reborn`; original game/raw-art roots remain read-only. Changes in this audit are confined to documentation and new QA files. No production edits, provider calls, financial/lock mutations, builds, device actions, storage cleanup, backups or Git mutations were performed. Read-only source inspection and public standards research supported the prose audit. No subagents were spawned.

The input identities are recorded in [input-identities.json](../../qa/plan-semantic-audit-20261016/input-identities.json). The manual and executor file matched the transferred hashes `20924b5c…` and `89e21f87…` before editing. Latest root banners and canonical requirements/equations were consulted, along with the 12 October full plan, 16 October implementation audit/coverage, owner style/budget and look-priority documents. [reading-inventory.json](../../qa/plan-semantic-audit-20261016/reading-inventory.json) records a full UTF-8 inventory of 153 mandatory/index-linked documents, with no missing file. Inventory reading is not a claim of exhaustive semantic validation of every historical report or image. Current owner authority resolves historical banners.

All 30 advanced mock hashes were freshly compared to their earlier exact pins. The retained all-30 contact sheet was visually inspected; Hero19 and Forge22 were additionally viewed individually at native dimensions. That supports the target hierarchy/material interpretation, not a fresh detailed acceptance review of every mock or current game screen. No new runtime session was opened. The old original game was not rerun, and its prior comparisons remain dated evidence. Current source branches for points/offers, healing, Endless, persistence, transactions and camera were read directly. The prior 152 tests/10 safeguards/483 parity results were **not rerun** and are not new results of this plan audit.

Protection evidence covers 719 existing files under `src`, `scripts`, `tests`, Android app source and root entry/manifests. It is a before/after hash check, not a fresh provenance audit of all historical art or Android build binaries. All 30 mock pins are checked separately. Existing dirty production/history was preserved. Current source hashes, not old completion labels, are the basis for the inspected behavior.

## Severity-ranked findings and corrections

P1 means an instruction could drive incorrect gameplay/storage behavior or allow substantial missing scope to be marked complete. P2 means ambiguity, feasibility or handoff reliability requires correction before closing its affected row. These severities assess the **plan**, not newly reproduced game defects. “Corrected” below means the documentation changed; it does not mean implementation passed.

### P1-01 — Detailed journeys did not enumerate several required mechanics

**Type: missing assertion detail, broadly present feature scope.** G03/G04/G08/G09/G10/G11 and original step50 named economy/day/weather/skills/gear, but the short J lists did not individually require all producer chronology/caps, terrain/weather states, exact skill effects, artifact behaviors, rank boundaries or loss-recovery balance. J05 primarily checked route/position/fog; J12 primarily checked a point/offer and Resurrection. An executor could complete those listed subcases while leaving other adopted behavior untested.

Evidence: original plan G03–G11 and step50; manual J04–J05/J11–J14; [MASTER content inventory (line 75)](MASTER-PLAN.md), [equations (line 9)](SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md). **Correction:** manual A06 adds eight explicit mechanics assertion families with all nine skills, eight spells, ten artifacts, eight terrains, seven weather keys, economy/XP/rank boundaries, Defense roles and narrative effects. A08 adds `balance-recovery.json` and real-versus-simulated timing. Existing tests may be reused only where they assert those cases. All mechanics remain implemented/unverified according to actual evidence, not these lists.

### P1-02 — Skill offers were conflated with primary-stat points

**Type: incorrect/ambiguous mechanics instruction.** Original M20 said “offers, points/selection/decline” and required an “effect/point delta” for choosing a skill. It also assumed two choices. Current [campaign.js:661 (line 661)](../../src/core/campaign.js) spends a primary point; `CHOOSE_SKILL` at666 consumes an offered choice and increases a rank without decreasing `hero.points`. The equations specify up to two choices, not always two.

**Correction:** M20 and A04 now explicitly separate those flows, including one-choice/all-maxed/decline/reload states. They prohibit an invented point-purchase skill tree. J12's “skill or stat point” cannot close both mechanics; the supplement requires both separately.

### P1-03 — R09 overstated rollback after every persistence failure

**Type: incorrect failure semantics.** R09 originally said “abort/failure retains the prior valid durable state.” That is correct for an aborted database transaction, but not a failed readback/UI acknowledgement after successful commit. Replaying a gameplay command at that point could duplicate its effect.

Evidence: original manual R09.6, [current staged save path (line 31)](../../src/core/save.js); the [IndexedDB commit algorithm](https://www.w3.org/TR/IndexedDB-3/#commit-transaction) distinguishes successful commit from later handler errors. **Correction:** R09.6/A05 distinguish validation failure, confirmed abort, request success, transaction completion and ambiguous post-commit acknowledgement. Resolve the latter by reading the durable expected identity, never blind command replay. The proposed adapter and regression schedules are still **unimplemented here**.

### P1-04 — Async revision ordering did not define replacement epochs, multiple writers or full migration

**Type: under-specified safety design.** R09.7–9 required serialization/coalescing and migration but did not define comparison across New/import/slot replacements, two tabs, same-ID older imports, or migration of slots/backup/view/damaged records. A promise queue orders one page only; a numeric revision alone does not identify the selected campaign generation. A partial migration can strand valid slots or let an old autosave return after import.

Evidence: manual R09; [replaceCampaign (line 87)](../../src/core/save.js), slot/load/view APIs in the same file. **Correction:** A05 adds expected-head `{epoch,campaignId,revision,checksum}`, transactional compare-and-write, replacement fencing, a multiwriter policy, all-key migration and interrupted-migration cases. It separates adapter metadata from the v1 export format, preserves old bytes and tests native acknowledgement later. Removing timer UUIDs must preserve production/clock/jobs, not just Defense time. No database backend was selected or written by this audit.

### P2-05 — The concrete overlay proposal lacked a world-area feasibility decision

**Type: feasibility gap, not proof that every layout is impossible.** The non-overlapping 825×375 HUD rectangles do not prove ≥80% useful unoccluded world. Contain-fitting 1376×768 uses 81.44% of the viewport before HUD; with the proposed rectangular HUD intersections the analytical useful area is about 71.44%. This is a counterexample to an automatic acceptance assumption, not a measurement of the current renderer, whose camera also supports cover/focus fitting.

Evidence: manual§3.2; [camera implementation (line 37)](../../src/client/projection.js); [calculation and assumptions](../../qa/plan-semantic-audit-20261016/layout-counterexample.json). **Correction:** A02 defines the usable inset rectangle and actual terrain-minus-HUD union, supplies reflow/camera/ground-extension options and states the crop/anchor checks. Inspector overlap has its own fallback. The80% target and Hall scale were not lowered; final four-size feasibility remains unverified.

### P2-06 — Dense 48px world targets lacked an ambiguity procedure

**Type: missing interaction decision.** R01 and§3.2 called for direct picking, 48px targets and an accessible list, without explaining which target owns a press when projected sites/formations are closer than48px. Expanding invisible boxes does not resolve overlap.

**Correction:** A03 specifies stable-ID disambiguation/focus or zoom, list alternatives, pointer cancellation/capture, occlusion and actual ownership checks for all 18 sites plus dense combat/pads. It retains direct world interaction. Keyboard/screen-reader names/state feedback and modal rejection are included. Actual target spacing and input still require runtime proof.

### P2-07 — Endless's ten-wave requirement omitted its legal terminal route

**Type: under-specified journey.** J10 required ten clears, settlement/best and ongoing generation, but did not say how an infinite session legally reaches settlement. This omission is particularly dangerous given prior forced-RESOLVED fixture claims.

Evidence: [defense.js:422 (line 422)](../../src/core/defense.js) extends Endless when its queue clears and resolves defeat when core dies; [campaign.js:410 (line 410)](../../src/core/campaign.js) writes best after actual resolution/settlement. **Correction:** J10/A07 require ≥10 non-leaked clears, then continued ordinary play to actual defeat, Apply once, best/q6/casualty/reload checks. No invented ten-wave victory/retire button or forced death is authorized. Natural duration/balance remains a real unresolved implementation test.

### P2-08 — “Full bag” rejection had no adopted numeric capacity

**Type: ambiguous invented-rule risk.** R06/M23 and the older plan requested full-inventory handling, but the adopted specification provides no numeric bag limit and the inspected FORGE/EQUIP paths do not supply one. Storage quotas are not gameplay capacity.

**Correction:** R06/M23/A07 preserve the uncapped collection, require dense scrolling/selection/persistence and condition a full-bag rejection on a genuine cited capacity rule. This resolves the existing behavior without inventing a cap or deleting items. All six slots and artifact/identity checks remain mandatory; this is not a waiver of large-save testing.

### P2-09 — Combined-file inherited section numbers and ordering could misdirect execution

**Type: handoff contradiction/ambiguity.** Original step82 says journeys are in “section6”; the combined file's manual§6 contains mock recipes, while journeys are in§7. The manual work-order table and original phase sequence also looked like two independent strict schedules. The vague owner-additions index and old absolute runtime path complicated input resolution.

**Correction:** A01 explicitly binds inherited references to the original 12 October plan, names the actual local input/index paths, gives a current-tool resolution rule and treats the 96 steps as the dependency spine with manual repairs supplying details. Original96step text remains verbatim, with its reference correction explicit in the one-file header. No required phase or previously authorized independent work is removed.

### P2-10 — Full-health healing tests could imply an unsupported rejection

**Type: ambiguous legal-target instruction.** M21 grouped “wrong/dead/full-health targets” without specifying whether each should fail. The current source and adopted equation cap healing on living friendly stacks; they do not require full-health rejection or refund.

Evidence: [battle.js:486 (line 486)](../../src/core/battle.js) and the spell section of [source equations (line 33)](SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md). **Correction:** M21/A04 distinguish wrong-side/dead rejection from source-defined capped/no-op healing and its real mana/cast consequences. Wounded-stack natural Resurrection remains required. No new target restriction was introduced.

### P2-11 — Live source could be mistaken for the final rule authority

**Type: authority ambiguity.** Manual§1 directed the executor to current source rules. With known implementation defects, that can preserve a bug merely because the current code implements it. Planning/live contracts also have similarly named paths.

**Correction:**§1/A01 distinguish owner changes, frozen/adopted tables/equations, current executable evidence and mock visuals. Exact planning/live paths, hashes and conflict fields are required. A08 clarifies cell-centre conversion and stage/native/camera frames. The known matrices and illustrative `(8,8)→(850,365)→(3400,1460)` example were checked algebraically and need no formula change. Missing physical thresholds stay proposed/unverified rather than guessed PASS values.

## What was already sufficiently specified

The previous manual already adequately stated advanced-mock visual priority; sparse Hall1/17empty/Walls0; physical walls; dynamic layers;32real scene traces; source-supported Healer reuse/replacement; class/era kits; six worn slots; articulated role/mount/contact/event work; honest natural/simulation/fixture distinctions; zero-runtime-permission policy; exact package identity; scoped blockers; and independent desktop before later device/owner review. These were retained and made more checkable, not treated as missing features.

The targeted extra $20 / absolute $100 ceiling, released $15 counted once, one active/inflightUNKNOWN, mutex/CAS/write-ahead/reservations/receipts, ≥20seconds after successful response completion, ≥60seconds/longerRetryAfter for 429, default 1K batches of 30 useful rows and necessary progressive 2K/4K routing were present. A08 clarifies that total below $100 alone cannot authorize unrelated use of the extra allowance. No live liability, invoice, remaining-capacity or affordability result was inferred. A realistic static body remains distinct from a usable rig.

## Complete requirement mapping

The following machine files contain explicit identity-preserving rows and manual semantic assessments. They are documentation coverage, **not implementation PASS**. No OWN/SYS identity was renamed. The35original requirements are assessed individually below; G/step/mock/journey files preserve their source text/actions and exact instructions.

- [35original OWN/SYS rows](../../qa/plan-semantic-audit-20261016/original-35-crosswalk.json), including source lines and sufficiently-specified/corrected/residual distinctions.
- [G01–G16](../../qa/plan-semantic-audit-20261016/G16-crosswalk.json) and [all 96 original actions](../../qa/plan-semantic-audit-20261016/original-96-crosswalk.json), with phase/detail/reference mappings.
- [All 30 mock states](../../qa/plan-semantic-audit-20261016/M30-crosswalk.json) and [all 18 journey assertion lists](../../qa/plan-semantic-audit-20261016/J18-crosswalk.json), including changed subcases.
- [32 scene obligations](../../qa/plan-semantic-audit-20261016/scene-32-obligations.json) and [192 class/kit/slot decisions](../../qa/plan-semantic-audit-20261016/class-kit-slot-192-obligations.json). These are required review rows, not accepted assets or purchase orders. A07 additionally enumerates troop/tower/attacker/creature/worker/transport role and clip scope.

<!-- ORIGINAL35_TABLE -->

| Original ID | Requirement | Semantic plan assessment / binding instructions |
|---|---|---|
| OWN-01 | Latest: plan and section previews before another AI codes | SUFFICIENT_WITH_CURRENT_OVERRIDE: No interim pre-code approval; independent desktop then later device/owner. Manual A01/A08; M01–M30. |
| OWN-02 | Fresh code in a different folder | SUFFICIENT: Independent source/read-only reference boundaries; no old executable imports. Manual A01; section 2. |
| OWN-03 | Reuse generated images and installation settings | SUFFICIENT_WITH_RESIDUAL: Reuse and source lineage explicit; missing historical records remain UNKNOWN. Manual R03–R07/A08. |
| OWN-04 | AoE III Kingdom + Heroes VII Adventure/Tactical + tower defence | CORRECTED_ASSERTION_GAP: Whole connected campaign plus explicit shared consequences and lost-army recovery. Manual J18/A06. |
| OWN-05 | Exact mock composition and controls | CORRECTED_LAYOUT_GAP: Mock composition with actual state; concrete contain/HUD feasibility and focused-sheet fallback. Manual M01–M30/A02. |
| OWN-06 | Semi-realistic/realistic first impression | SUFFICIENT_WITH_RESIDUAL: Coherent realistic treatment; pixel quality and affordability still unverified. Manual section 3.1/R04/A08. |
| OWN-07 | Real Day1 build footprints | CORRECTED_DENSE_PICKING_GAP: Hall1+17 empty+Walls0; natural clearings and actual contextual target ownership. Manual R01/R02/J01–J02/A03. |
| OWN-08 | OWNER §§2–4: all eight ages across every channel | CORRECTED_ASSERTION_GAP: All eight age families; item-age distinct from campaign age; caps and derived stats. Manual R03/R05/M02–M10/A06–A07. |
| OWN-09 | OWNER §5: continuous terrain and meaningful sites | CORRECTED_ASSERTION_GAP: 16×10 paths/sites, full physical traces and terrain/weather/day/rest. Manual R03/J05–J06/A06/A08. |
| OWN-10 | OWNER §6: true horse/rider gait | SUFFICIENT_WITH_RESIDUAL: True mount gait/rider/vehicle requirements specified; sources/contact outcomes unverified. Manual R07/M12/A07. |
| OWN-11 | OWNER §7: classes and period appearance | CORRECTED_MECHANICS_LANGUAGE: Eight classes/four kits/192 slot decisions; skill offers separate from points. Manual R05/R06/M19/A04/A07. |
| OWN-12 | OWNER §8: offscreen archer/range/melee/flying faults | CORRECTED_ASSERTION_GAP: Visible entry, range, role/telegraph/flight and density assertions. Manual R03/R07/J09/A06. |
| OWN-13 | OWNER §9: grounded tactical warfare | CORRECTED_ASSERTION_GAP: Grounding/actions/targets, queue, RNG and retaliation cases. Manual M14–M16/J07–J08/A03/A06. |
| OWN-14 | OWNER §10: quarry/enemy/gear/tower era mismatch | SUFFICIENT_WITH_RESIDUAL: Era/role/gear/worn source matrices specified; no art completion claim. Manual R05–R07/A07. |
| OWN-15 | OWNER §§1/12: quality and return play | CORRECTED_BALANCE_GAP: Retain full progression and measure real timing/loss recovery; no guessed rebalance. Manual J14/J18/A06/A08. |
| OWN-16 | OWNER §13: detailed handoff for another AI | CORRECTED_REFERENCE_GAP: One consistent prompt, exact input paths and inherited section resolution. Manual A01/A08; single executor file. |
| OWN-17 | Latest: no repeated setup questions | SUFFICIENT: Refresh installed facts; no stale absolute runtime path dependence or setup re-interview. Manual section 2/A01. |
| OWN-18 | Latest: exactly30 images per batch, one active only | SUFFICIENT_WITH_RESIDUAL: Targeted extra20/absolute100/reserve once and serialized provider controls; live budget UNKNOWN. Manual section 2/A08. |
| OWN-19 | Latest: no Cloud/account/Play Store work | SUFFICIENT_WITH_RESIDUAL: Offline local runtime, zero permissions; provider dev tooling separate, native/device unverified. Manual R10/A08. |
| SYS-01 | Economy | CORRECTED_ASSERTION_GAP: Per-instance producers/unique facilities, chronology/caps/costs and offline report. Manual R01/R02/J02/J04/A06. |
| SYS-02 | Army | CORRECTED_ASSERTION_GAP: 24 role names/eight creatures/flyers/ranks/reinforcement/IDs. Manual M24/J03/J13/A06–A07. |
| SYS-03 | Equipment | CORRECTED_CAPACITY_AMBIGUITY: Six worn and functional slots; no invented bag cap; artifacts/quality/age assertions. Manual R06/J11/A06–A07. |
| SYS-04 | Forge/Market | SUFFICIENT_WITH_ADDED_ASSERTIONS: Real Armory quality/cost/craft and Bronze buy/sell; Gold is price. Manual M22/J11/J15/A06. |
| SYS-05 | Hero | CORRECTED_MECHANICS_LANGUAGE: Points/offers and full-health target expectations corrected; all skills/spells/effects. Manual M19–M21/J12/A04/A06. |
| SYS-06 | Adventure | CORRECTED_ASSERTION_GAP: All site/day/rest/terrain/weather transitions, fixed offers/fog and guard return. Manual M11–M13/J05–J06/A06. |
| SYS-07 | Tactical | CORRECTED_ASSERTION_GAP: Full action/queue/flight/effect/RNG/damage/retaliation scope. Manual M14–M16/J07–J08/A03/A06. |
| SYS-08 | Defence | CORRECTED_TERMINAL_ROUTE: Four tower/five attacker behavior and natural Endless clear-to-defeat-to-settlement route. Manual M17–M18/J09–J10/A06–A07. |
| SYS-09 | Story/objectives | SUFFICIENT_WITH_ADDED_ASSERTIONS: Seven chapters plus Future, six rivals/quests/eight milestones and branch effects. Manual M25–M26/J14/A06. |
| SYS-10 | Settings/audio | SUFFICIENT_WITH_RESIDUAL: Music/SFX/local media/motion/help/privacy; heard/native/device evidence separate. Manual M28/J17/A03/A08. |
| SYS-11 | Tutorial | SUFFICIENT: Anchored correct-command tutorial with cancel/skip/review/reload. Manual M27/J01/J17/A03. |
| SYS-12 | Saves | CORRECTED_FAILURE_AND_RACE_GAPS: Atomicity vs acknowledgement, epoch/CAS, all-key migration and adversarial schedules. Manual R09/J16/A05. |
| SYS-13 | Shared progression | CORRECTED_ASSERTION_GAP: Shared campaign IDs/costs/rewards/mana/casualties and storage replacement ordering. Manual J18/A05–A06. |
| SYS-14 | Native | SUFFICIENT_WITH_RESIDUAL: Exact final binary/native manifest/preview identity/device matrix, no early device action. Manual R10/A08. |
| SYS-15 | Mobile/performance | CORRECTED_LAYOUT_GAP: Four landscape sizes, dense selection/insets/readability and measured performance. Manual section 3.2/R10/A02–A03/A08. |
| SYS-16 | War options | CORRECTED_TERMINAL_ROUTE: All five options; deterministic Challenge/isolation; Endless not a ten-wave victory. Manual J10/A06–A07. |

<!-- END_ORIGINAL35_TABLE -->

## Remaining uncertainty and required executor evidence

Documentation cannot guarantee that a usable source exists for every rig/gear/angle, that all artistic outcomes satisfy the advanced mocks, or that repairs are affordable within the targeted allowance. Final physical traces/clearance fields, usable four-size layout, complete Healer matte/identity,192 slot compatibility decisions and every clip/contact remain actual work. Existing missing historical source/license/transfer records remain UNKNOWN until separately evidenced; this pass neither restores nor closes them.

Long-play storage remains an observed prior failure with a credible timer-ledger path. This audit read the source but did not measure new browser growth or prove the sole cause. A05 is a proposed compatible safety design with failure schedules. IndexedDB availability/durability on the deployed WebView and native lifecycle acknowledgment must be tested by the executor and later device stage. It is not a universal power-loss guarantee. Explicit user transaction histories and legitimate inventory can still grow; define and measure the supported campaign horizon rather than claiming unlimited persistence.

All naturalJ01–J18 subcases, real pacing to earned Wisdom 3/Endless/Future, loss recovery/economy balance, target accessibility, offline/native behavior and final exact binary remain unverified by this **plan** audit. The correction assigns concrete inputs/actions/assertions/fallbacks, but it is not an implementation result. Any genuinely absent numeric rule needs its exact sources and bounded decision; it cannot be invented from generated text or self-certified thresholds. Continue unrelated ready work.

## Verification of the documentation revision

Run `python qa/plan-semantic-audit-20261016/audit_documents.py verify` for structure/hash checks only. [verification.json](../../qa/plan-semantic-audit-20261016/verification.json) records the final manual/executor/report hashes, exact verbatim embedding, 16 G contracts, 96 contiguous original steps, 30 M / 10 R / 18 J and preservation results. It is deliberately labelled `DOCUMENTATION_STRUCTURE_AND_PRESERVATION_ONLY`. Old `qa/planner-detailed-solutions-20261016/handoff-verification.json` stays unchanged as historical input; its old document hashes are not final identities.

The actual semantic findings above were established by comparing requirements, algorithms, source branches and the layout counterexample. Counting rows cannot establish those conclusions. No game tests/builds were rerun to audit prose. **The corrected plan is more complete and internally consistent, with residual execution/art/budget evidence explicitly open; whole game INCOMPLETE.**
