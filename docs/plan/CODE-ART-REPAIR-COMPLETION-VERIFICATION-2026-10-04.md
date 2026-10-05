# Code and art-processing completion verification — 4 October 2026

**Result: INCOMPLETE.** The latest repair increment works in the normal browser paths checked below, but strict migration and replacement failure handling still have defects. The broader assigned art/game task remains unfinished. The executor's latest `CODE-AI-RESUME` also explicitly says INCOMPLETE and records no service/context limit. Its proposed next action should follow the remaining save fixes, then continue ready Defense/art/journey work.

Planner/verifier audit only: no game edits, art processing, production moves/deletes, provider/project calls, builds, device operations, executor messages, delegation or Git mutation. Evidence: [fresh QA directory](../../qa/code-art-next-verification-20261004/). Local dirty tree is on `main`, HEAD `cff552880ae15c892b736ac7847f6753787ca58f`; remote was not queried. Closing SHA comparison: **263/263 protected files unchanged** during this audit, including selected game/tests, delivery, native32 outputs, image controls, Android source, old dist/package. This does not survey every file on disk.

## Repairs independently checked

| Previous defect | Fresh result | Limit |
|---|---|---|
| New/Load slot/Import lost on reload | Actual controls now durably replace the prior Varek campaign; older imported revision advances past live; reload retains replacement | Normal paths PASS; fault handling below FAIL |
| Malformed modern story migrated into validity | String chapter, nonboolean quest claim and chapter/choice mismatch now reject | Explicit null fields still accepted; PARTIAL |
| Panel-open touch targets below48px | All18 targets inside/uncovered and centre-picked, open/closed at825×375,933×424,1180×820,1280×720;48px within floating-point tolerance | Sparse scene/control survey, not mature silhouettes, device insets or physical touch |
| Valid creature Army crash | Fresh context initialized before first load displays Dire Wolf×5 rank0 without errors; source/unit coverage resolves creature/flyer and role families | Browser wolf fixture only; natural dwelling/deployment journey open |
| Damaged Home lacks import/error | Parse reason plus Import, Export damaged save and New appear; valid backup Restore returns Varek and retains `broken-save` | Browser synthetic damaged campaign |
| All chapters claimable at Stone / false wins | Next chapter rejects at Stone; synthetic age stepping permits seven chapters; duplicate Future acknowledgement rejects, grants nothing; false-cleared validation covered | Natural all-age progression unverified |

`node --test tests/*.test.mjs`: **61 PASS /0 FAIL**, exit0, no skipped/cancelled. Reviewed scripts copied into this fresh QA directory; `browser.mjs`, `creature.mjs`, `journeys.mjs`, `probes.mjs` each exit0. Probe process success is not defect success: `probes.json` explicitly records9 FAIL cases. Browser has0 page errors. Background Defense time1.25s remains1.25s; oscillator scheduling3→3 hidden→5 resumed. This is scheduling evidence, not heard audio or native lifecycle proof.

## Remaining correctness findings

1. **High — latest valid campaign can be lost after live verification failure.** `src/core/save.js:28–64` stages the replacement and promotes the previous live bytes into backup. On failed live verification it restores the older backup, while leaving the corrupt live value. In `probes.mjs` mode `corrupt-live-write`, load becomes DAMAGED and backup no longer contains the latest Varek campaign. This uses a deliberately faulty in-memory storage adapter, not an ordinary browser failure observed in production. Required behavior: keep the latest valid campaign recoverable even when live rollback cannot succeed; never discard that sole valid recovery copy while reporting replacement failure.

2. **Medium — housekeeping failure reports replacement failure after durable success.** Successful commit's staged-key removal at `save.js:64` can throw outside the transaction catch. Probe `staged-cleanup-throws` leaves a valid new mage campaign on disk but `replaceCampaign` throws. `src/client/main.js:41` only promotes UI state after return, so this path can leave old UI and new durable state. Distinguish committed outcome from cleanup debt; test reload and stale autosaves after either outcome. Do not hide actual durability failures.

3. **Medium — present null values are silently reset.** `src/core/campaign.js:158–170` uses `value == null`. A field explicitly present as null is treated as an absent legacy field. Seven reproduced cases—chapter, choices, futureSeen, milestones, quests, q1 and flags—fail direct validation but pass decode after migration. Migrate recognized genuinely absent legacy properties only; reject malformed present fields and preserve the original bytes. Valid pre-Story migrations must still work.

## Art and whole-task completion

Actual fresh pixels inspected: `natural-four-buildings.png`, `hero.png`, `defense.png`, `kingdom-panel-825x375.png`. Natural starter supplies and elapsed construction produce level1 Lumber/Farm/Quarry/Barracks and tutorial step4, but those sites remain names/tinted footprints rather than completed building paintings. Existing terrain contains baked unrelated huts, foundations and obstacles; sparse Day1 fidelity is still open. Hero's main stage is empty. Defense shows a lane, squares and circles, without the required painted actor/projectile/boss presentation. Its core/UI remains partial for the full distinct-role/interception/army scope. Stick figures/markers are development presentation, not final articulated actors.

**66/66 prior delivery files unchanged**, and23 local selection path/hash bindings match, including the five UI derivative pairs and eight old Kingdom terrain pointers. These checks do not confer art approval. The current selection still uses historical1K terrain, not the new first32 native4K set. No new extraction/rig/atlas delivery closes the art assignment. Requirements matrix still has16 coarse rows instead of separate OWN-01..19/SYS-01..16 evidence.

Latest separate image audit: all32 native4K outputs technically valid; all8 new Kingdom terrain candidates fail bare-content acceptance. Remaining24 are not silently approved. Known incompatible Defense forest/hills remain excluded. Code AI owns existing-source processing and live consumers; Image AI separately owns terrain preparation/provider work. No new purchases/retries/later73 activation arise from this audit.

## Package, preservation and storage

Existing APK's41 packaged web files match old `dist`; eight differ from current root: index.html, audio.js, game.css, main.js, projection.js, campaign.js, defense.js, save.js. DEX still contains the old file-origin URL and lacks the new asset-loader origin literal. Updated Java source is not packaged-launch evidence. Preview rebuild/static verification is executor work. Device installation/testing remains STOPPED.

Saved restore destination remains null;0 verified restore rows and67 tracked asset paths. This blocks preservation-dependent whole-assets untracking/Git delivery, not unrelated code/art implementation. Remote SHA, external copies and restore success were not verified here.

Owner's conditional move-and-cleanup authority remains active: independently passed images go to image-only `assets/production/final-native4k/`, metadata outside; destination SHA/decode and references must close before proven redundant copies/comparisons/payloads are actually removed. Current first32 final-promotion eligibility remains0. The separate image executor owns that staging cleanup. No move or deletion occurred in this planner audit. This audit retained only bounded representative screenshots, total1,767,076bytes.

Next owner-selected executor prompt: [CODE-ART-IMPLEMENTATION-NEXT-TASK-2026-10-04.txt](CODE-ART-IMPLEMENTATION-NEXT-TASK-2026-10-04.txt). It supersedes the prior next-task prompt's defect baseline and blanket local cleanup prohibition while retaining full scope and independent acceptance gates.
