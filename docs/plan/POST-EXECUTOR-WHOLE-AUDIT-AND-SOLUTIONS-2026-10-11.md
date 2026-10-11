# Independent audit of the Code + Image executor pass — 11 October 2026

**Overall: INCOMPLETE; request changes before treating this as the completed game.** The executor made real local improvements and correctly retained an overall incomplete checkpoint. Its list of open work understates additional image, presentation, contract and verification defects found here. The next executor must repair these and continue the whole scope, rather than close another small subset.

This planner independently reviewed the 32 top-level changed/untracked paths at entry, the tracked diff, new implementation/data/tests/helpers/interfaces and saved evidence. Earlier planner prompt/audit/status files are part of those 32 paths; the count is not 32 executor implementation changes. Fresh checks: Node24.19.0 tests, isolated Chrome layout/class checks, all original transfer assets, current output hashes/dimensions, source/dist/www/APK parity/CRC and aapt36 package/permission inspection. No production repair, provider query/call, accounting change, game/APK build, device action, backup/ZIP, Git staging/commit/push or executor dispatch occurred. Audit writes are small QA/docs and bounded review captures only.

## Independently confirmed progress

- **111/111 tests PASS**, zero failed/skipped. The three new tests check static body contracts/fitting/kit labels, not full realistic rigs or complete gameplay.
- **3647/3647 original transfer-manifest assets match** size/SHA256. Existing production originals remain intact. Seven body outputs and their recorded intermediate/native sources match hashes. All90 despilled output hashes match their report.
- **77 successor-interface reference checks PASS**, with no missing/hash/size/dimension errors. Seven formerly missing native pointers now correctly reference the existing identical bytes. Original receipt paths remain recorded.
- Both exact small v4/v5 guides are present, and `.gitignore` now contains precise exceptions. No replacement guide purchase is needed.
- New Hero room uses seven standing bodies and six slot cards; Slinger is bound through its override. Army terrain background, Forge composition/quality choices and dwelling controls are implementation progress, not final visual acceptance.
- **Fresh current APK parity PASS bounded:**473 web entries match current source, dist and Android www, CRC clean,584456970 bytes,SHA256 `8ebaf5e3921f3344a7903c6b4a62232340456c8c5bccff10fb711e5cb3168c88`. Fresh aapt36 verifies preview ID `com.agesofdominion.game.reborn.preview`, min24/target36 and zero declared permissions. No install, granted-permission, native lifecycle or performance claim.
- Fresh Chrome:28 screen/viewport combinations across7 navigation surfaces plus all8 class choices run without console/network errors. This is scoped live checking, not all30 reference/state acceptance.
- The saved executor journey records real-time affordability waits, recruitment, guard combat/reload, one weapon craft/equip, mode starts/results and some story/settings/slots behavior. These are reviewed saved claims; this audit did not rerun the long earned journey.

## Actionable findings and solutions

### F1 — P1: global hue despill removes legitimate subject/effect pixels

`scripts/image_despill_plates_20261011.py:51` estimates key from image chroma and at lines69–77 scales alpha for every qualifying pixel. There is no foreground protection, boundary/background segmentation or per-ID semantic mask. Marker deletion also uses detached component size/saturation without semantic proof. This violates the requested source-supported protection of cloth, weapons, anatomy and violet FX.

Actual before/after review shows Industrial support tower `5-support` loses much of its intentional violet ring/energy structure.17020 formerly opaque pixels become nearly transparent;3294 are in the measured central region. Counts alone are not semantic loss proof; the reviewed before/after pixels establish the missing effect. Other removals may be desirable floor cleanup and must be reviewed individually. A remaining magenta fraction below1% is neither foreground preservation nor a matte PASS.

**Solution:** classify each of90 adopted outputs against its immutable source. Keep safe bounded repairs; replace only damaged ones using background-connected masks plus explicit body/weapon/cloth/FX/shadow protection. Retain violet glows deliberately with per-ID applicability, not a universal magenta threshold. Rebind safe predecessor bytes temporarily where current output visibly destroys required content; preserve both histories. Record preservation deltas and inspect on light/dark/real-scene backgrounds before promotion.

### F2 — P1: wrong role/era and non-magenta floors remain live

The newly overridden Bronze heavy is still a single spear-and-shield infantryman on a large painted slab, not the required Charioteer crew/horse/vehicle unit. The Medieval archer remains on a large opaque olive rectangle after despill. Both can have tiny magenta fractions while failing semantics/matte. This is directly visible in `despill-review.jpg` and the output PNGs.

The new Hero renderer chooses `heroBody(classId)` at `src/client/hero-room.js:122`, independent of age/equipment, but labels `kitEra(state.age)` at line140. Saved Stone footage shows a steel-armoured Knight holding a sword while the real weapon slot contains a Flint Club and other slots are empty. All ages reuse that same body. The new slot renderer calls `gearIconFor(slot)` using campaign age, rather than the worn item's own age/identity. This risks visually modernizing retained old items. Labels and stat changes do not implement visible gear attachments.

**Solution:** maintain separate class/kit-era/body and item/age/quality/compatible-slot references; correct each live role and preserve old item appearance until replaced. Reuse suitable existing source subjects where they actually exist; necessary missing bodies/kits/crew/mounts require correct per-ID source preparation and authorized affordable generation. Do not reinterpret incorrect infantry as Charioteer. Make equipment state visible through supported attachments/layers, with honest partial status until complete. Native SVG room/smithy gradients remain provisional scenery under the semi-realistic/realistic final-art requirement.

### F3 — P1: new Hero/Forge actions and text fail phone usability

Fresh browser measurements at825x375:
- Six Hero SVG slot targets are83.94x39.50 CSSpx.
- Six Forge SVG targets are275.80x41.97 CSSpx.
- Hero essential slot/stat text includes3.703–5.863 CSSpx; Forge labels include8.394–10.193 CSSpx.

All12 SVG targets also fail48px height at933x424. Hero text still has a9.094px minimum at1280x720. Existing HTML action buttons do not make newly clickable SVG cards compliant. The executor's `screenHealth()` selects only HTML `button` and checks broken HTML `img`; it neither measures SVG role buttons nor validates text or SVG image loading. Its `meaningful-targets-48px` PASS therefore cannot cover these new controls.

**Solution:** size UI at CSS scale independently of the terrain camera, or use responsive native controls positioned over the room with actual48px targets and readable type. Keep actor/world registration unchanged. Reflow/scroll/collapse secondary details rather than scale all text into the1376x768 art canvas. Audit `button,[role=button],input,select,textarea` plus scene actions, text transformed through getScreenCTM, clipping and keyboard/focus behavior. Check real SVG asset responses/loading. Preserve existing Retreat/Army passes; broaden tests only to the unverified new vectors.

### F4 — P2: static-body interface, size and ROI contracts disagree

The interface adds seven `READY_STATIC_STANDING` rows to `readySubset`, although the declared row status vocabulary uses `READY`; resulting readySubset12 contains7 non-READY rows. Gates `NOT_A_RIG` and `PASS_HERO_ROOM` are outside the declared gate enum. Intended bounded use should be separate from gates/status. Each row still declares maxDisplayCssPx130 while its consumer/body contract says600. The new tests assert600 rather than validating the previously constrained130/64 per-use policy; Forge preview/slot code similarly invents260/96 caps. Large intended Hero use needs an explicitly supported, consistent per-use contract rather than a silent expansion.

Body `cropROI` uses `[x,y,width,height]` at `scripts/image_complete_bodies_20261011.py:131`, whereas the canonical ROI is half-open `[x0,y0,x1,y1]`. Grounding derives the last opaque row and12-row alpha band, not semantic feet. The Ranger algorithm description says lowest6% but its actual code uses30%; auditability needs correction. Actual resized pixel extents and coordinate convention must be reflected in the recipe.

**Solution:** publish a new atomic successor schema revision with legal enums, bounded `intendedUse`, declared frames, consistent caps, canonical ROI and explicit resize/rounding conventions. Keep animation eligibility separate; a valid static use may have articulation NOT_APPLICABLE with limitation, not a full rig PASS. Measure actual feet/hoof/door contacts. Do not silently update historical records or self-certify large display suitability. Resolve any required large Hero rendering through verified source/detail and a documented per-use proposal consistent with owner direction; preserve existing caps until justified.

### F5 — P1: mandatory gameplay acceptance was replaced by weaker checks

The saved50/50 journey is not the required completion evidence:
- Siege used the starter arrow/slow towers, hero and one stack; it lost after2 of5 waves with coreHP about-17.615. The check deliberately accepts that loss. The once-only victory-reward path remains unproved.
- Forge earns/equips one Crude weapon, not six slots/qualities/artifacts. The6 visible cards only establish layout presence.
- Endless records6 configured waves but only2 cleared. `endless-extends-or-ends` accepts immediate end/loss and does not require actual cleared waves beyond the original boundary.
- Practice comparisons cover selected gold/XP/inventory-length/army fields, not all resources,mana,item contents,quests/story/transactions or reload/replay.
- Forty screen/viewport combinations cover10 screens, not all30 references plus required selected/empty/error/result states. No earned age beyond Stone is demonstrated.

**Solution:** keep these bounded evidence rows as history. Add separate hard checks for naturally prepared Siege WIN/full clearance/reward/casualty settlement and second reload/claim zero duplication; six earned equipped compatible slots with exact deductions/effects/reload; actual Endless extension after clearing its initial wave count; full practice isolation and five complete mode round-trips. Continue earned eight-age progression without debug grants. Diagnose affordability/preparation/balance from adopted formulas and legal play, not guaranteed-win edits. Failure should stay visible and trigger correction rather than broaden the predicate.

### F6 — P1: changing APK filename did not preserve the referenced prior package

The old `android/app/build/outputs/apk/release/app-release-unsigned.apk` is absent now. The executor checkpoint admits Gradle replaced the release output directory. Naming a new output within the same managed directory did not keep the old referenced package in place. This contradicts the handoff's preservation requirement despite making no backup copy.

**Solution:** record the exact lost historical path/hash as unavailable; do not fabricate it, create a replacement backup or pretend original-assets PASS covers APKs. Before another packaging run, inspect actual Gradle output cleanup behavior. Keep the existing final package outside the cleanup path through a direct checked move to a stable delivery location, with updated evidence pointers and no byte duplication, or configure a proven non-destructive artifact output. Build staging is transient; owner-referenced delivered bytes must not be deleted by it. Do not use the retained `--preserve-existing` backup option under the current no-backup instruction.

### F7 — P2: package has shadowed plate sources in its declared closure

Current473-file parity is genuine. However, the build independently visits base `plateCatalog` and `plateOverrides`.94 base plate files whose runtime group keys are overridden are still packaged, totalling100117235 bytes (~95.5MiB) before compression. Other consumers may intentionally reference some of them; this is an exclusion candidate list, not permission to delete originals or claim all100MB removable. The huge584MB package and repeated dist/www copies conflict with the requested storage-conscious minimal delivery.

**Solution:** derive effective runtime plate entries after override merge, enumerate every actual consumer including review/fallback states, keep proven referenced bases, and separate provenance/source-only references from shipped files. Optimize delivery textures/atlases only after source/pixel/detail approval, preserve original assets in place, and test actual offline loads across states. Refresh dynamic closure and APK parity after final integration. Do not reduce texture fidelity or discard required age/class content merely to shrink bytes.

### F8 — scope remains open; none of these external gates excuse feasible work

All32 successor scene records are byte-structurally unchanged from the prior interface; all32 spatial gates remainFAIL. No registered terrain repair was produced. Seven bodies are static candidates; complete class/kit/mount/transport/effect rigs and semantic animation delivery remain unfinished. Healer body remains missing. Native SVG interiors and current sampled Kingdom/Adventure/Tactical composition do not establish realistic final finish. No complete30-reference comparison or earned8age journey exists. Existing measured/schematic actor-atlas records are not erased by the statement that no new full body rigs were delivered.

**Solution:** follow the complete next prompt, prioritizing source-bound terrain prototypes and real supported rigs after the correctness regressions. Paid necessary per-ID work retains the prior owner authorization/reserve-release policy, but current affordability/account/jobs/UNKNOWN operations have not been verified by this planner. No provider activity/accounting change is evidence of restraint, not a new global blocker or a verified current15.1673USD balance. Device STOPPED, morale PENDING_OWNER_DECISION and owner acceptance UNVERIFIED affect only their dependent actions.

## Whole-scope disposition

Technical foundations and package are boundedPASS. Kingdom pads/economy/tutorial, Army/recruitment/creatures, Hero/skills/spells, Forge/Market/inventory, Adventure/sites/guard flows, Tactical actions/settlement, Defense/War/natural victories, story/rival/quests/milestones/Future, save/import/export/recovery/settings/audio/help/privacy, all8age visuals and performance remain PARTIAL or UNVERIFIED at complete-product scope. Scene spatial and final visual/articulated presentation remainFAIL/INCOMPLETE. No owner/product or physical-device acceptance is inferred.

Git HEAD remains790629dec96226021182c8ab5c03bc4e474b8db9; no staging/push performed. The32-path worktree count was at entry and will grow with this audit. Required helper source, corrected small contracts/docs and two essential guides are suitable for later explicit scoped delivery; generated media/bulk assets/rawpayloads/APKs/caches remain excluded. Do not stage blindly from the old32-path count. Do not commit an interface referring to ignored production files and call a clone sufficient restoration.

## Evidence and next executor

Evidence: `qa/planner-post-executor-20261011/` contains audit/browser helper source, current worktree/document inventory,111-test result, original-asset preservation, body/despill/interface/scene checks, current live layout measurements/captures, package parity/closure review, aapt native evidence and final preservation comparison. Pixel review is bounded; magenta heuristics and byte hashes do not self-attest semantic/visual acceptance.

Give the owner-selected ONE executor `docs/plan/NEXT-WHOLE-CODE-IMAGE-REPAIR-PROMPT-2026-10-11.txt`. It includes current successful work to preserve, defects/solutions, the full product inventory, ordered persistent execution, scoped paid/owner/device blockers and stronger completion predicates. The planner did not send it to an executor.
