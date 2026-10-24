# Independent live and source recheck — 22 October 2026

**Current whole-game status: INCOMPLETE.** Checked at 2026-10-22 17:27 UTC. This update corrects stale source claims and records the current M22 Forge repair and natural item journey. It does not close M01–M30, J01–J18, final package, device, or owner acceptance.

## Adventure production-map currentness

A fresh verifier ran `campaignMapImage()` against every world in `src/data/adventure-worlds.json`, hashed each selected on-disk PNG, read its PNG dimensions, and compared the production binding and geometry v4 source/hash/size fields. Result: **12/12 selected and valid; 0 invalid; no supplied mock path selected as production.** The per-world evidence is [production-map-binding-recheck-v4-20261022.json](production-map-binding-recheck-v4-20261022.json).

This supersedes the `qa/independent-status-20261022/VERIFICATION.md` statement that the runtime binds 11/12 supplied paintings. That statement is stale relative to current source and must not be repeated as a live defect. Source and hash correctness still do not prove all-world natural journeys, site semantics, pixel quality, or compact-screen acceptance.

The current Adventure frame was captured on the approved local route at 1280×720: [grasslands-adventure-live-1280x720.jpg](adventure-map-currentness-review/grasslands-adventure-live-1280x720.jpg), SHA256 `8ad014b2d9d7240eb65e60fb2b1a9c38621acc22a042d00b445ccab0a24590d7`. M11 remains PARTIAL: the game-specific Grasslands map is live and traversable, while M11’s focal settlement, resource plaque, and bottom-right shortcut composition are not matched. The capture is a browser JPEG and is not used for fine typography certification. A separate file named `grasslands-production-map-live-1280x720.jpg` was captured during a screen transition and contains Forge; exclude it from Adventure evidence.

## M22 Forge visual repair

The Forge now opens its recipe panel on entry, presents the current item and worn comparison, displays all four source-defined quality tiers, and keeps the six functional gear slots in a two-column right rail. The active offer is usable; locked tiers identify Armory levels 3, 5, and 7 and show their costs. Quality labels remain the source-defined Crude/Fine/Master/Relic values in the authoritative data contract.

The workpiece and workshop background were shifted left so the sword does not sit behind the menu. At 1280×720 the workpiece image bounding box is x=218.2…777.2 and the recipe panel is x=814…1118; the six-slot rail is x=1132.8…1262.8. Current live capture: [forge-live-1280x720-m22-repaired-final.jpg](forge-m22-live-review/forge-live-1280x720-m22-repaired-final.jpg), SHA256 `e1c1f0f225b304e5870ddd07645dc90439cf2f202c7de4f19412ada5f128be60`.

M22 remains PARTIAL because only the current 1280×720 natural state was visually checked; empty/populated, selected-comparison, all Armory levels, exact mock pixel comparison, and required compact sizes remain open. M23’s full inventory hierarchy and its mock composition also remain PARTIAL.

## Natural Forge → compare → equip → reload journey

On the existing campaign shown at `http://localhost:4174/?audit`, I confirmed the displayed Crude Knight’s Longsword recipe (320 wood, 240 stone, 280 gold), crafted it, compared it with the empty Weapon slot, and equipped it. The carried count changed from 1 to 2 on craft and to 1 after equip. The Hero screen showed ATK 3→6; the live actor included `worn-gear-art` sourced from `assets/derivatives/worn-gear-20261020/weapon-medieval.png`. The save indicator returned from “Saving campaign” to “Save campaign.” After reload and Continue, the weapon slot and ATK 6 persisted.

This journey changed the local preview campaign’s game state by spending in-game resources and equipping the item; it did not involve real-money purchases or provider calls. Evidence: [confirmation](forge-m22-live-review/forge-craft-confirmation-1280x720.jpg) SHA256 `2383e31d8357b6bf8830ecff958c9c361a147ca6ce4759aab533fbbd02cef2cc`; [comparison](forge-m22-live-review/forge-longsword-compare-1280x720.jpg) SHA256 `03395598fb5836c4b02b2b2daee7db6f64f9740081444a3633806b253a5818c2`; [reloaded equipped Hero](forge-m22-live-review/hero-equipped-longsword-reload-1280x720.jpg) SHA256 `f508bb37fa032925d82d918df26e95b1d1e59c457e51634ce0ffef5566a819b4`.

## Verification and remaining gates

- `node --test tests/*.test.mjs`: **265/265 PASS**, including the 10,000-command save-stress horizon (27.7 seconds).
- Focused responsive and worn-gear tests: **34/34 PASS**; `node --check` passed for `main.js` and `hero-room.js`.
- The live route reported **0 browser warnings and 0 errors** after the Forge and equip review.
- The current desktop source is still not a release snapshot. No web/native/APK build, install, device QA, or owner review was performed.
- M14/M15/M16, M01–M30 visual coverage, J01–J18 natural journeys, eight-age Kingdom states, 32 class/kit rows, motion, all physical scenes, supported-size browser review, full browser persistence/recovery, and final package parity remain open.

Use this recheck as current supplemental evidence; preserve the earlier reports as historical records and use the latest owner contract for remaining scope. Overall product and release remain **INCOMPLETE**.
