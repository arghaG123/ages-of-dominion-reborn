# Independent coverage appendix â€” 16 October 2026

**Whole game: INCOMPLETE.** See [findings and methods](INDEPENDENT-WHOLE-GAME-VERIFICATION-2026-10-16.md). A listed requirement is accounted for, not automatically accepted.

## Full feature contracts

| id | requirement | status | evidence | findings |
|---|---|---|---|---|
| G01 | Eight ages | FAIL | Core progression simulation and 32 imported views pass bounded; era/kit/style/scene acceptance fails. | F1 F4 F6 |
| G02 | Sparse Day 1 and economy | PARTIAL | Fresh resources, Hall/17 pads and paid Lumber Camp observed; final physical/composite acceptance remains open. | F0 F1 F6 |
| G03 | Construction and progression | PARTIAL | Core costs, build/upgrade/offline tests pass; natural build/export/restore observed; complete visible progression not replayed. | F2 |
| G04 | Adventure | FAIL | Navigation/guard logic tested; painted crossing/approach and mounted motion fail acceptance. | F1 F3 |
| G05 | Tactical | PARTIAL | Legal engine, morale and spell tests; live Skirmish/Auto/modal pass; formation/terrain/event/clip requirements open. | F1 F3 F9 |
| G06 | Defense | PARTIAL | Earned command simulation clears 20 Endless waves; visible role motion/physical lane and complete natural journey open. | F1 F2 F3 |
| G07 | Five War modes | PARTIAL | All entry/core/isolation paths covered in suite; complete visible setup/result/reload for all five unverified. | F2 |
| G08 | Hero/classes | FAIL | Eight class selection/body views inspected; Knight era mismatch, other unverified eras and incomplete kits. | F4 F5 F6 |
| G09 | Nine skills/eight spells | PARTIAL | Source/core tests including positive morale and all spells pass; natural earned Wisdom/Resurrection journey not independently complete. | F2 F9 |
| G10 | Six-slot equipment/Forge/bag | PARTIAL | Core recipes/qualities/slots tested; actual worn visual replacement and workshop/selected-item composition fail. | F2 F4 F6 |
| G11 | Army/eight creatures | PARTIAL | All eight earned core identities covered; complete natural dwelling/combat/rank/codex journeys and role gait open. | F2 F3 |
| G12 | Story/quests/Future | PARTIAL | Earned simulated chapters/milestones/six quests/Future pass; full visible branch/claim/return journey open. | F2 F6 |
| G13 | Market | PARTIAL | Core quotes/transactions and live Stone lock covered; ordinary Bronze buy/sell/error/cancel/reload not independently replayed. | F2 |
| G14 | Tutorial | PARTIAL | Core target sequence/skip/review tested and initial Build target observed; complete contextual visible sequence unverified. | F2 F6 |
| G15 | Save/recovery/settings | PARTIAL | Core fault tests and real export/import/Continue observed; long-browser quota failures and native/audio/performance closure remain. | F7 F8 |
| G16 | Shared consequences | PARTIAL | Core settlement/idempotency/practice isolation pass, bounded live Skirmish settles; full natural persistent multimode journey open. | F2 F7 |

## Original 19 owner / 16 system requirements

| id | requirement | status | related | evidence |
|---|---|---|---|---|
| OWN-01 | section feedback | UNVERIFIED | G01, G08, G10 | Owner explicitly rejects current game look/plot grid/box walls and keeps this AI verifier-only; final acceptance not claimed. |
| OWN-02 | fresh rebuild | PASS_BOUNDED |  | Current source and local package scanned; no old executable imports found. Exhaustive code ancestry was not audited. |
| OWN-03 | existing art reuse | PARTIAL | G01, G04, G08, G10 | Current assets/source hashes inspected for required consumers; whole provenance/archive transfer not re-audited. |
| OWN-04 | connected campaign | PARTIAL | G16 | See current related G rows; whole feature acceptance is not closed. |
| OWN-05 | exact composition | PARTIAL | G01, G04, G05, G06, G08, G10 | See current related G rows; whole feature acceptance is not closed. |
| OWN-06 | realistic first impression | PARTIAL | G01, G08 | See current related G rows; whole feature acceptance is not closed. |
| OWN-07 | Day1 footprints | PARTIAL | G02 | See current related G rows; whole feature acceptance is not closed. |
| OWN-08 | eight ages | PARTIAL | G01 | See current related G rows; whole feature acceptance is not closed. |
| OWN-09 | continuous terrain/sites | PARTIAL | G04 | See current related G rows; whole feature acceptance is not closed. |
| OWN-10 | true mount gait | PARTIAL | G04 | See current related G rows; whole feature acceptance is not closed. |
| OWN-11 | eight classes/kit eras | PARTIAL | G08 | See current related G rows; whole feature acceptance is not closed. |
| OWN-12 | Defense legality/roles | PARTIAL | G06 | See current related G rows; whole feature acceptance is not closed. |
| OWN-13 | grounded Tactical | PARTIAL | G05 | See current related G rows; whole feature acceptance is not closed. |
| OWN-14 | era-correct content | PARTIAL | G01, G08, G10 | See current related G rows; whole feature acceptance is not closed. |
| OWN-15 | quality/return play | PARTIAL | G12, G15, G16 | See current related G rows; whole feature acceptance is not closed. |
| OWN-16 | usable handoff | PASS_BOUNDED |  | Dated report, source snapshot, matrices and one complete portable executor continuation prepared; no Git publication/restore claim. |
| OWN-17 | no repeated setup | PASS_BOUNDED |  | Existing environment/version records reused and actual runner versions refreshed; no setup re-interview. |
| OWN-18 | image policy | AUTHORITY_RECORDED_LIVE_UNVERIFIED |  | Latest targeted extra $20 / absolute $100 ceiling documented. No live accounting/provider readiness refresh or paid call. |
| OWN-19 | offline/no-store/cloud | PASS_STATIC_RUNTIME_UNVERIFIED | G15 | Latest package has zero declared permissions and current runtime has no remote URLs. No independent device/network run. |
| SYS-01 | economy | PARTIAL | G02, G03 | See current related G rows; whole feature acceptance is not closed. |
| SYS-02 | Army | PARTIAL | G11 | See current related G rows; whole feature acceptance is not closed. |
| SYS-03 | six functional equipment slots | PARTIAL | G10 | See current related G rows; whole feature acceptance is not closed. |
| SYS-04 | Forge/Market | PARTIAL | G10, G13 | See current related G rows; whole feature acceptance is not closed. |
| SYS-05 | Hero | PARTIAL | G08, G09 | See current related G rows; whole feature acceptance is not closed. |
| SYS-06 | Adventure | PARTIAL | G04 | See current related G rows; whole feature acceptance is not closed. |
| SYS-07 | Tactical | PARTIAL | G05 | See current related G rows; whole feature acceptance is not closed. |
| SYS-08 | Defense | PARTIAL | G06 | See current related G rows; whole feature acceptance is not closed. |
| SYS-09 | Story/objectives | PARTIAL | G12 | See current related G rows; whole feature acceptance is not closed. |
| SYS-10 | settings/audio | PARTIAL | G15 | See current related G rows; whole feature acceptance is not closed. |
| SYS-11 | tutorial | PARTIAL | G14 | See current related G rows; whole feature acceptance is not closed. |
| SYS-12 | saves | PARTIAL | G15 | See current related G rows; whole feature acceptance is not closed. |
| SYS-13 | shared progression | PARTIAL | G16 | See current related G rows; whole feature acceptance is not closed. |
| SYS-14 | native | PARTIAL | G15 | Latest web package closure passes; native delivery binary differs and installed identity/full native performance remain unverified. |
| SYS-15 | mobile/performance | PARTIAL | G01, G05, G06, G15 | 52 requested screen/viewport visits; actual phone widths 826/934. Contrast, exact odd widths and dense Android FPS/memory/thermal not closed. |
| SYS-16 | five War options | PARTIAL | G07 | See current related G rows; whole feature acceptance is not closed. |

## All 30 design references

| reference | status | evidence |
|---|---|---|
| 01-home.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 02-kingdom-day1.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 03-kingdom-stone.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 04-kingdom-bronze.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 05-kingdom-iron.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 06-kingdom-medieval.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 07-kingdom-gunpowder.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 08-kingdom-industrial.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 09-kingdom-modern.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 10-kingdom-future.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 11-adventure-overview.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 12-adventure-crossing.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 13-adventure-foot.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 14-tactical-deployment.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 15-tactical-action.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 16-battle-result.jpg | PARTIAL | Live pending result/apply works; composed actual survivor/reward/loot result reference not independently accepted. |
| 17-defense-preparation.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 18-defense-wave.jpg | FAIL_OR_UNVERIFIED | Fresh runtime or all-age terrain overview inspected; physical registration/grounding/composition gates remain open (F1/F3/F6). |
| 19-hero-equipment.jpg | FAIL | Eight settled body views: flat chamber, wrong/unverified eras and icon overlays; coherent worn body still missing (F4/F5/F6). |
| 20-skills.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 21-spells.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 22-forge.jpg | FAIL | Fresh Forge shows generic SVG workshop/anvil rather than required prominent source-supported selected-item/workshop treatment (F6). |
| 23-inventory.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 24-army.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 25-story.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 26-quests.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 27-tutorial.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |
| 28-settings.jpg | PASS_BOUNDED_UNVERIFIED | Basic local Settings/Home/save UI works in inspected states; full native, quota/recovery/contrast/visual composition remain open. |
| 29-save-recovery.jpg | PASS_BOUNDED_UNVERIFIED | Basic local Settings/Home/save UI works in inspected states; full native, quota/recovery/contrast/visual composition remain open. |
| 30-icon-material-board.jpg | PARTIAL_UNVERIFIED | Reference reviewed at overview; counterpart/elements exist. Full state-specific composition and native/phone fidelity are not accepted. |

## All 18 connected journeys

| id | status | evidence |
|---|---|---|
| J01 | PARTIAL_NOT_COMPLETE | Independent fresh class/start and correct starter economy; full initial-target/cancel/class matrix remains bounded. |
| J02 | PARTIAL_NOT_COMPLETE | Independent ordinary Lumber Camp cost/completion/production and restored export; all upgrade/cancel/reload subcases not replayed here. |
| J03 | PARTIAL_NOT_COMPLETE | Core recruitment/capacity tests pass; complete ordinary visible recruit-to-combat journey not replayed. |
| J04 | PARTIAL_NOT_COMPLETE | Earned command progression and synthetic age views pass. Producer natural browser path grants resources/Hall (F2). |
| J05 | PARTIAL_NOT_COMPLETE | Core navigation tests pass; all-age physical crossing/mount acceptance fails (F1/F3). |
| J06 | PARTIAL_NOT_COMPLETE | Core fixed offers/guards tested; producer dwelling PASS leaves claimed false (F2). |
| J07 | PARTIAL_NOT_COMPLETE | Live Skirmish opens; required manual action/flyer/morale queue cases not all replayed. Role motion fails (F3/F9). |
| J08 | PARTIAL_NOT_COMPLETE | Independent Retreat focus trap/cancel and Auto/once-applied result pass bounded. Full victory/defeat/retreat/reload matrix open. |
| J09 | PARTIAL_NOT_COMPLETE | Core fixed-step/deploy/pause/reload tests pass. Complete natural visible Defense result and art gates remain open. |
| J10 | PARTIAL_NOT_COMPLETE | Five core mode entries covered. Independent Skirmish only; all five full natural flows not claimed. |
| J11 | PARTIAL_NOT_COMPLETE | Six slots/qualities tested in core and equipped visual fixtures. Producer natural Forge includes grants; appearance fails (F2/F4). |
| J12 | PARTIAL_NOT_COMPLETE | Core point/skill/all-spell/Resurrection tests pass. Producer live spell uses injected Wisdom/wounded stack, not natural earned journey. |
| J13 | PARTIAL_NOT_COMPLETE | Eight creatures earned via command simulation. Current independent natural dwelling-to-combat/rank loop not completed. |
| J14 | PARTIAL_NOT_COMPLETE | Core seven chapters/six quests/eight milestones/Future covered. Full ordinary visible saved branch/conclusion/claim loop remains open. |
| J15 | PARTIAL_NOT_COMPLETE | Core quotes and transactions pass; live Stone locked state observed. Ordinary complete Bronze transaction/error/cancel loop unverified. |
| J16 | PARTIAL_NOT_COMPLETE | Independent real export/import/restored Continue observed; all slots/corrupt/unsupported/quota/recovery/native flows not fully rerun. |
| J17 | PARTIAL_NOT_COMPLETE | Basic Settings/text/rotation sampled; full heard audio, contrast, tutorial and keyboard journey not fully closed. |
| J18 | PARTIAL_NOT_COMPLETE | Natural build and practice result plus preserved natural save; complete natural build/recruit/equip/travel/campaign-battle/defend/claim chain not proved. |
