# All-age Tactical scene and HUD review — 20 October 2026

**Bounded fixture result: PASS for scene loading and HUD geometry; visual art result: FAIL for two ages; whole game: INCOMPLETE.** I compared live Tactical captures across all eight registered ages against the approved action composition at 825×375, 933×424 and 1280×720.

## Evidence

[`tactical-all-ages-hud-live/`](tactical-all-ages-hud-live/) contains 24 screenshots and a machine-readable report. Each run imported a valid campaign envelope with only its age field changed, started a Skirmish, and inspected the rendered Tactical scene. This is an isolated visual fixture, not natural progression or acceptance evidence.

- All eight Tactical terrain files loaded from the selected `mode-scenes.json` paths.
- Every capture retained all 70 board cells, kept the setup panel closed and produced zero browser errors or failed HTTP responses.
- The initiative panel remained at lower left and the action dock at lower right. All visible Tactical actions stayed in bounds and received input at their centers.
- The HUD placement now follows the approved M15 action composition.

## Visual failures

- **Medieval (age 3):** `assets/derivatives/scene-edges-20261013/tactical-medieval.png` still has white editor/registration dots along the river and bridge.
- **Future (age 7):** `assets/derivatives/scene-edges-20261013/tactical-future.png` still has white editor/registration dots along the river, masonry and bridge.

These dots are baked into the selected images; the runtime grid is a separate overlay. Preserve the bridge, water, terrain texture, registration and frozen cell geometry while repairing those two source-bound art candidates. I made no production art change in this verifier pass.

The current fixture has two formations, while M15 shows a much larger army. It verifies the HUD with a real scene and legal field cells, but it does not establish density parity with a full campaign roster. Physical bridge/cell clearance and natural progression remain open for all ages.

## Scope boundary

No age advancement, native package, APK, device or owner review was performed. M01–M30, J01–J18, all 32 scene traces, independent desktop acceptance, final snapshot APK and later device/owner gates remain open. Product status remains **INCOMPLETE**.
