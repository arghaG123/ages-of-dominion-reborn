> **Later owner correction, 17 October 2026:** [U01–U16](OWNER-MOBILE-GAME-UI-KINGDOM-AND-RELEASE-GATES-2026-10-17.md) now specifies icon-led mobile game presentation, sharp integrated Kingdom wall/ground families and complete desktop review before final packaging/mobile QA. [The same ONE repair file](ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt) is revised in place with those directions and the full unchanged original contract. Findings/test counts below are the earlier implementation audit, not a fresh rerun by this prompt review.

# Independent executor verification — 17 October 2026

**Verdict: INCOMPLETE. The current implementation is not a completed desktop candidate.** This is a fresh verification of the newer checkout, not a repetition of the 16 October missing-file findings. Several repairs are real; substantial visual, storage, evidence, journey and package failures remain. Every required unexercised assertion remains OPEN/UNVERIFIED.

Give the other implementation AI **[ONE complete current repair file](ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt)**. It supersedes the 16 October remaining-work and 17 October four-failure repair entrypoints and embeds the original authoritative complete executor file unmodified. The original specification remains authoritative; the fresh preface corrects stale findings and supplies executable repair routes. No implementation agent was dispatched.

## Fresh scope and method

Canonical root: `C:/dev/ages-of-dominion-reborn`; date 17 October 2026, Asia/Calcutta. Node **24.19.0**, Python **3.13.15** verified. Existing dirty worktree used; HEAD and initial dirty paths recorded read-only in [git-before.json](../../qa/independent-verification-20261017/git-before.json). This verifier wrote only QA and documentation, served existing source without building, and used disposable browser origins. No production/art/native changes, paid/provider/account/ledger/lock action, build, device operation, Git mutation, cleanup, backup/duplicate asset tree or delegation was performed.

Evidence root: [qa/independent-verification-20261017](../../qa/independent-verification-20261017/). Reproducible harnesses, current source line excerpts, hashes, screenshots and machine crosswalks are saved there. The source review used the code-review skill; Qodo CLI was unavailable, so no external rules retrieval or installation occurred. No web research was needed for these local implementation observations.

- Read current pointers, authoritative manual/complete file, original requirements/data/contracts, latest repair files, prior audits and README-linked inputs. [Reading/input identities](../../qa/independent-verification-20261017/reading-input-identities.json) records exact files, hashes and missing inputs; historical banners are not current acceptance.
- **162/162 Node tests PASS**, with `EARNED_SCOPE_OUT` redirected to new QA. The hard-coded stress test was excluded from the ordinary run, copied into an isolated QA harness with only import/output path changes, then **1/1 PASS** separately. [Suite output](../../qa/independent-verification-20261017/node-tests.tap), [redirected stress output](../../qa/independent-verification-20261017/stress.tap). Its result is fixture evidence with the defects below, not acceptance of its advertised horizon. Old offline safeguard suite was not rerun because it overwrites old QA; its previous 10/10 is historical only.
- Opened actual pixels for all **30 mocks**, all **32 current class/kit files**, all **32 Kingdom ground/scaffold/wall/upgrade images**, the other **24 displayed mode sources**, producer motion images, and fresh runtime counterparts. Overview inspection identifies concrete failures; it does not certify every native matte edge or every composite frame. [Mock identities](../../qa/independent-verification-20261017/mock-identities.json), [kit identities](../../qa/independent-verification-20261017/kit-identity.json), [visual sheets](../../qa/independent-verification-20261017/visual-and-package.py).
- Ordinary game input on new origin **4537**: no false Continue, New/default Knight, Enter Kingdom, Hall1/17 empty sites/Walls0, legal P01 Lumber purchase **25 wood/15 stone**, ordinary job completion, visible producer/income, Save/reload, Hero/Adventure inspection. [Reload state](../../qa/independent-verification-20261017/natural-build-reload.txt). This is a bounded natural subset, **not complete J01/J02/J18**: cancel/upgrade/full campaign children were not all performed.
- Real browser IndexedDB adversarial fixture on separate origin **4538**, using the production adapter: **five failed assertions**. Future visual fixture on separate origin **4539** uses an explicit **1e12 resource grant and accelerated core construction**; it never counts as earned progression. Ordinary UI within it exercised Unequip/stat change/reload and seven chapter choices/real Future acknowledgement/no reward/reload. [Native storage results](../../qa/independent-verification-20261017/native-storage-results.json), [Future fixture source](../../qa/independent-verification-20261017/visual-fixture.html), [ending deltas](../../qa/independent-verification-20261017/story-ending-fixture.json).
- Read-only current source/catalog/dynamic package comparison and APK CRC/manifest inspection performed. No APK was rebuilt or installed.

## Corrected historical findings and preserved repairs

1. The previously missing browser/wall/Healer/motion screenshots **now exist and decode**. The old blanket missing-capture finding is retired as current. Relevance, current source binding, visual correctness and actual assertions still matter.
2. `kingdomPainting()` now chooses age/state-specific PNGs; the active wall renderer no longer assembles runtime segment stamps. Logical Walls0/job/1/upgrade selection passes bounded tests. The finished pixels/depth still fail F05; do not revert the state selection.
3. `hero-kit-eras-20261017.json` supplies 32 actual variant bindings, all checked file hashes match. The producer's old **2 matched / 30 mismatched** matrix is stale against this consumer. It is not a current 30-purchase requirement. F06 records actual newer defects.
4. Current Healer `staffExtendedBelowBoots` is **0**, and its below-foot regression passes. The historical **185** finding is not current. Full anatomy, background, class/kit/portrait/rig consistency and motion acceptance remain OPEN.
5. Huge resource values now compact to labels such as `1000B`, retaining full accessible values. Fresh fixture UI did not reproduce the old full-integer overflow; arithmetic was preserved. Exact-width/inset/full supported-range acceptance remains separate.
6. Reaching Future alone correctly does not skip story. Seven real choices followed by **Keep the valley** show saved **The Valley We Keep**, award no acknowledgement reward and survive reload. This passes a bounded **injected-setup UI** case, not natural Future/J14/J18 closure.

## Severity-ranked findings

All findings below are **P1** because they prevent required completion; narrower metadata/reporting defects within them are P2. Source lines are indexed in [source-line-evidence.json](../../qa/independent-verification-20261017/source-line-evidence.json). There is no claim that the owner's actual save suffered the losses reproduced on disposable fixtures.

### F01 — Native IndexedDB replacement/CAS/migration can overwrite newer progress

Fresh [browser probe](../../qa/independent-verification-20261017/native-storage-probes.html) and [results](../../qa/independent-verification-20261017/native-storage-results.json) use real IndexedDB and the actual `src/core/storage-adapter.js`:

- `commit()` accepts a supplied head with deliberately wrong `campaignId` and `checksum`; it checks only epoch/revision.
- `replace()` ignores `expectedHead`. A second adapter with the old head replaces newer revision **200 with 150**. Its epoch comes from a per-instance counter rather than the durable current head.
- `migrateFromLocalStorage()` then replaces that DB revision **150 with old revision 1**. It lacks the required resumable source-hash marker/newer-progress protection.
- The migration inventory detects staged source bytes, but the stored export omits them.

`campaignId` is derived from `story.chapter`, so it is neither stable nor unique campaign identity. `main.js:persist()` reports success immediately after queuing a promise, clears faults and can return Saved before durable completion. `replaceLive()` first requires synchronous localStorage replacement and logs later IDB failure; the slot UI still uses localStorage. The backend that was meant to solve dense-store quota therefore does not own all persistence flows. The native lifecycle script immediately returns `'saved'` after calling the JS background hook; it does not await IDB commit. These source findings are distinct from later native-runtime verification.

**Repair:** implement manual A05/R09/10.4 completely: asynchronous authoritative bootstrap; transactional full-head CAS and durable replacement epoch; all slots/import/New/recovery in the selected backend; independently validated migration records/marker; preserve valid backup/damaged/staged bytes; pending/committed/failed/uncertain acknowledgement per epoch/revision; queue coalescing and native snapshot acknowledgement. Run real browser race/abort/quota/restart/lifecycle schedules. Do not clear stores, reset progress or silently use stale localStorage.

### F02 — The 277-row ledger is neither the original identity crosswalk nor an expanded leaf proof

Fresh parsing confirms **14 PASS, 263 OPEN**; `remaining.json` still says desktop review prerequisites are met and internal blockers are zero. That claim is rejected. [277 independent dispositions](../../qa/independent-verification-20261017/executor-277-dispositions.json) reopen all 14 whole-leaf PASS claims while retaining bounded valid observations.

The producer repurposes original IDs: original **OWN-17 means no repeated setup questions**, but its ledger means multi-slot persistence; original **SYS-04 means Forge/Market**, but its ledger means IndexedDB CAS. Original **OWN-19 is absent**. Matching a total of 35 rows does not preserve the original 19 owner + 16 system requirements.

Evidence relevance is also wrong: **M07 Gunpowder Kingdom** cites Stone Adventure; **M10 Future Kingdom** cites Hero; **M13 on-foot Adventure** cites Tactical Duel. Their PNGs now exist, but depict the wrong requirement. G03's construction screenshots cannot close all producers/facilities/caps/chronology. The 277 rows are largely parent-sized identities, not the expanded required action/negative/reload/viewport/slot/mechanics children.

**Repair:** restore exact original identities with explicit later-authority dispositions; give new internal categories separate IDs. Expand mandatory children and bind current source/state/capture/assertions. Set prerequisite claims false until actual pre-package functional/visual/desktop conditions pass. Do not edit old QA to conceal failures.

### F03 — Passing stress/mechanics/performance scripts overstate what they exercised

`tests/save-stress-horizon.test.mjs` grants resources repeatedly, assigns level/growth/offers, directly marks claims/milestones, creates 20 clear flags and a SETTLED Defense object, then forces terminal core/status and creates another session. It does **not** actually clear those 20 waves. Its 36,000-second loop does not count only ACTIVE session time; `advanceActiveDefense()` returns early after resolution. Consequently “ten active hours” and legitimate terminal loss/re-entry are unproved. Its 10,000 declared commands, roughly **975,011 serialized characters** and bounded-store/Map behavior are useful **injected fixture** evidence, not legal fresh-to-Future/full native-browser horizon proof.

`scripts/generate-mechanics-and-balance-20261016.mjs` writes descriptive VERIFIED/natural rows without executing their named inputs/expected numeric outputs. It even describes a **100% paid construction-cancel refund**, while the contract requires preview-cancel zero spend and does not authorize inventing that mechanic. `performance.json` times Node projections/simulation, not browser rendered frames, long tasks, image composition or native FPS. Generator success cannot close these categories.

**Repair:** replace false claims with matching actual assertions. Retain useful fixture measurements under honest labels; use legal earned simulation for progression/clears/active accumulated time/real defeat and re-entry; exercise resulting dense payloads in native browser stores. Add all A06 numeric/cancel/reload mechanics and A08 real/accelerated balance recovery evidence. Measure rendered performance separately. Do not alter rules to match erroneous generated descriptions.

### F04 — Functioning equipment still renders as floating miniature inventory items

`actor.js:paintWornSlots()` draws the gear inventory image at generic fractions in a small square (`max(22, body.width*.16)`), rather than a compatible worn garment/weapon/attachment. The fresh Future figure displays tiny spare helm/torso/boots/accessory items over the body while its painted carbine remains. [Current worn figure](../../qa/independent-verification-20261017/fixture-future-worn-1280.png).

Unequip worked in the UI: Weapon became Empty, bag +1, Attack **8→3**, and reload retained it. [Reload evidence](../../qa/independent-verification-20261017/fixture-unequip-reload.txt). This preserves functional progress; it does not fix the painted weapon conflict or create believable wearing. Data attributes and captions now claim worn attachment more strongly than the pixels support.

**Repair:** use actual per-class/era landmarks and source-supported garment/prop layers; mask/remove incompatible defaults, attach to real hands/head/torso/feet with appropriate scale/depth/contact. Keep inventory icons in inventory UI. Cover all six slots, qualities/artifacts/old items, 32 class/kit rows and 192 meaningful slot decisions without purchasing 192 images.

![Actual current worn-item failure](../../qa/independent-verification-20261017/fixture-future-worn-1280.png)

### F05 — Integrated-looking world/room/workshop composition and physical walls remain unfinished

Fresh [support-screen overview](../../qa/independent-verification-20261017/current-support-overview.jpg) versus [mocks 16–30](../../qa/independent-verification-20261017/mocks-16-30.jpg) confirms the Hero's generic gradient chamber, Forge's flat anvil/tiny item, and Story/settings/help's generic card slabs do not deliver the advanced mock compositions. Correct story text or button entry is not their visual acceptance.

All eight wall-state families were inspected: [early ages](../../qa/independent-verification-20261017/walls-1-4.jpg), [later ages](../../qa/independent-verification-20261017/walls-5-8.jpg). State selection is improved, but broad blurred ground scars and repeated rigid perimeter strips/slabs remain visibly separate from the source terrain. Writing the assembly into a PNG does not synchronize lighting, materials, perspective or ground contact. The current `paintMaterialWalls()` only appends empty groups; walls are entirely in the background terrain, so required front/back occlusion is not implemented by those groups.

**Repair:** preserve the latest same-kind age/state painting direction and actual cost/state rules; repair source-supported ground/wall integration, gate/road contact, material joins and proper foreground occlusion/masks. Build real chamber/workshop/journal/roster counterparts using each M recipe. Compare actual dynamic sparse/building/mature/equipped/action/result states at native/phone sizes. No runtime stretched wall stamps, completed-city backdrop pretending to be saved buildings, lowered art target or interim owner gate.

### F06 — New kit files fix selection metadata but include incomplete bodies and stale identity families

All 32 new consumer paths exist and hashes match. Actual [32-kit overview](../../qa/independent-verification-20261017/class-kits-32.jpg) nevertheless shows **ancient Paladin ending at the calves and mech Paladin at the knees**, with metadata placing “feet” near the last image row. Some Ranger/Healer/Warlock variants retain visible studio/matte shapes. Era strings and file hashes cannot establish complete anatomy or coherent style.

The current static Healer is a male photographic figure; its atlas/rig references still include the older female identity. Full body/portrait/rig/default-kit/equipment consistency remains unproved. The below-foot staff repair is a bounded positive finding, not a complete OC06 pass. A test that places the foot at the final row and counts alpha below it cannot prove that the actual boots exist or make contact.

**Repair:** reject incomplete masters before derivatives; recover suitable complete images/compatible layers, actual anatomical foot/contact landmarks and clean alpha, then update dependent portrait/rig/consumer families together. Review every class/era empty and worn at native/intended size. Do not automatically regenerate 30 rows from the obsolete matrix.

### F07 — “25 motion extremes” are identical body poses; actual roles/events remain incomplete

Fresh pixel hashing excluding label rows found **one distinct body image per role across all five labelled clips**, for Knight/Ranger/Barbarian/Warlock/Healer. [Hash results](../../qa/independent-verification-20261017/motion-evidence-pixel-comparison.json), [actual producer images](../../qa/independent-verification-20261017/motion-extremes-25.jpg). `capture-motion-extremes.py` calculates angles but only pastes unrotated body crops. These are neither real runtime captures nor proof of motion extremes; its dismembered previews also cannot be treated as runtime anatomy passes.

Live source still maps role→class without era in `ROLE_RIG/drawJointedRole`, so Bronze/Future role identity is not established by choosing a generic Knight/Ranger/Barbarian rig. Whole-image mount/plate bob paths remain. `drawFigure()` selects animation from the last log entry with absolute animation time rather than a finite start/duration event, leaving replay/duration/previous-actor concerns. It also supplies the player's `wornKit()` to role figures indiscriminately. Role matrix acceptance remains OPEN.

**Repair:** source-supported actual runtime limbs/contacts/directions for required roles/eras/creatures/attackers/workers/mounts/vehicles; correct player/enemy equipment ownership; finite stable committed-event playback after queue advance; real intermediate/extreme/grounded motion observations. Keep static images only in appropriate static contexts. Do not call a changed transform or unused atlas artistic closure.

### F08 — All 32 scene gates remain physically unproved; eight Kingdom source bindings are stale

Fresh source/hash comparison finds **all eight Kingdom hashes stale** in the producer scene JSON. The other 24 hashes match their listed sources, but a matching hash is not geometric acceptance. [Current 32-scene crosswalk](../../qa/independent-verification-20261017/scene-32-current.json).

The generator estimates painted obstacle radius from a gradient statistic and derives deck alignment partly from age name. It checks centre samples rather than continuous real actor footprints, and hardcodes `groundContactVerified:PASS` / `visualGrounding:PASS`. Its own overall result remains OPEN, **0/32 pass**. Fresh overview of Adventure/Tactical/Defense sources is retained; no new claim of full native polygon tracing is made by this verifier.

**Repair:** exact-source manual native feature polygons; legal path/deck/approach overlay; measured actual role/pose ground footprints continuously swept inside usable surfaces and outside real obstacles; full static footprints/vertical extents/depth; current integrated review. Preserve contract matrices and cells. Repair art, retrace changed sources, reject sample stamps and desired geometry labelled as observed art.

### F09 — Ordinary Stone phone world prominence fails; exact sizes/insets/performance remain open

Settled ordinary Stone closed-inspector measurement at actual **826×375** has terrain beginning near **y=56.14px**. After clipping meaningful terrain to the viewport and subtracting the union of individual visible identity/status/resource/button rectangles, useful world is **78.30%**, below 80%. This is optimistic accounting: transparent gaps are excluded and larger ancestor input-owning areas are not charged. [Raw geometry](../../qa/independent-verification-20261017/layout-settled-dom.json), [calculation](../../qa/independent-verification-20261017/natural-phone-metric.json), [phone pixels](../../qa/independent-verification-20261017/phone-settled-825.png).

The separate Future fixture passes the same bounded zero-inset rectangle metric at actual **826×375 (85.98%)**, **934×424 (88.33%)**, **1180×820 (94.43%)**, **1280×720 (93.85%)**. This does not repair the Stone failure or close exact odd sizes, safe insets, all landmarks/picking, inspector/dense states, contrast or motion. [Fixture raw geometry](../../qa/independent-verification-20261017/layout-fixture-dom.json), [metric](../../qa/independent-verification-20261017/layout-fixture-metric.json).

Measurement limitations are explicit: initial four-size captures include resize timing; a later attempted series measured the same natural tab at 826×375 four times because viewport settings affected the other active tab. Those repeats are **not four-size proof**. The final Future series records its actual distinct sizes. [Attempt limitations](../../qa/independent-verification-20261017/layout-attempt-limitations.json). Browser quantization leaves exact 825/933 layout checks UNVERIFIED. No artificial inset emulation or physical device claim is made.

The producer viewport generator hardcodes touch/typography/contrast/clipping success and overall VERIFIED, contradicting its own failing phone fields. **Repair:** actual A02/A03 shared-camera/reflow/ground-extension/input/focus solution with honest metrics at required exact sizes/insets/states. Actual rendered performance/audio/native behavior require their own evidence, not Node projection timings.

### F10 — Current-source package closure fails; static manifest and CRC pass only their own layer

Read-only [package-current.json](../../qa/independent-verification-20261017/package-current.json) compares **567 current expected source/catalog/dynamic paths**: **54 missing + 15 differing files** in each of `dist/`, Android `www/` and the existing APK. Missing paths comprise 4 current code/data files, 24 state-wall paintings, 24 class/era variants and 2 gear files. The current old checker enumerates 519 paths and omits 48 dynamic wall/kit dependencies. Existing source now imports modules that the old packaged snapshot does not contain; the old APK represents an older implementation, not these repairs. This does not assert that the self-contained older APK necessarily crashes.

Current build-output APK: `android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk`, **616,295,432 bytes**, SHA256 **`7bd7fa2de1dbccbc46102484d26378d930e47ea321d696ade2b2763e7b50b69c`**. CRC clean; static application ID `com.agesofdominion.game.reborn.preview`; **zero declared permissions**. Existing status's `76dbbcf5…` / 615,635,661 bytes is stale. The current APK's manifest/dex/resources hashes are recorded. No source-to-dex rebuild, delivery-folder equality, signing, installed permissions or native runtime was verified; older delivery APKs are preserved, not promoted as this candidate.

**Repair:** fix transitive/dynamic enumeration in build and verifier, finish required pre-package functional/visual/desktop leaves, then build/sync/package once from frozen final source/art/native inputs. Verify final web closure, manifest/dex identity, zero permissions and exact delivered bytes/hash. Keep device/owner review at the later authorized stage.

## Full coverage and acceptance layers

The [coverage appendix](INDEPENDENT-EXECUTOR-COVERAGE-2026-10-17.md) and [scope summary](../../qa/independent-verification-20261017/scope-summary.json) reconcile original **35**, G**16**, original **96**, M**30**, J**18**, scene**32**, class/kit**32** and slot**192** obligations. All 96 original step texts still match the current original source. Complete manual and original complete-file hashes remain exactly the historical anchors; this verifier did not alter them.

The producer's 18 journeys remain labelled simulation, **0 complete**, **20 explicitly unverified subcases**. They model only 36 producer subcases; they are not the full manual assertion set plus the J18 chain. No independent full natural J is awarded. Fresh ordinary and fixture observations above are evidence subsets, not replacement scope. Natural Wisdom3/wounded Resurrection, full five-mode setup/results, all creatures/ranks/quests/milestones/Market/recovery and same-campaign J18 remain unverified at their required layer.

Technical unit regressions: **PASS_BOUNDED**. Logical sparse start/first construction: **PASS_BOUNDED**. Compact resource labels and Future conclusion fixture: **PASS_BOUNDED**. Storage safety: **FAIL**. Mock/worn/body/wall/motion acceptance: **FAIL/OPEN**. Physical scene closure: **OPEN/UNVERIFIED**. Full natural journeys and long native-browser horizon: **OPEN/UNVERIFIED**. Current package parity: **FAIL**. Existing static CRC/preview ID/permission absence: **PASS_BOUNDED**. Final native/device/owner acceptance: **UNVERIFIED**, with later sequence preserved.

## Preservation and handoff

The pre/post protection check hashes **5,046 protected production/art/script/test/native/source-mock/financial-control files: zero changes**. All **144 previously inventoried executor evidence files are unchanged**. [Protection result](../../qa/independent-verification-20261017/protection-result.json), [prior-evidence comparison](../../qa/independent-verification-20261017/prior-executor-evidence-preservation.json), and [handoff verification](../../qa/independent-verification-20261017/handoff-verification.json) record these checks and byte-exact original-contract embedding. These are preservation checks, not game acceptance. This pass makes no invoice/capacity claim: targeted additional $20, absolute exposure $100, released $15 counted once, all provider/mutex/pacing/UNKNOWN controls remain unchanged.

Execute the **one repair file**, preserve working repairs, fix all remaining required concerns, obtain current evidence and deliver the full candidate. No owner approval is needed for routine authorized local repairs or affordable prepared authorized calls; external limits affect exact rows only. This verifier remains planner/verifier. The product remains **INCOMPLETE** until all required current assertions and the later independent/device/owner sequence actually pass.
