# Tactical Medieval and Future scene repair — 20 October 2026

**Status: source repair bound and live-browser reviewed at three landscape sizes; physical trace is supporting evidence only; whole-game acceptance remains INCOMPLETE.**

## Change

The active Tactical backgrounds for Medieval (age 3) and Future (age 7) contained visible white editor/registration specks baked into the terrain art. I kept both original files intact, created clean candidates, and switched the two `mode-scenes.json` entries to the reviewed candidates:

- Medieval: `assets/derivatives/visual-repair-20261020/scenes/tactical-medieval-clean-candidate-v1.png` (1678×937; SHA256 `6f3eb57663cb3aa584a9a7e74f8df67f394c8845508a57511e0809b7867e83d2`)
- Future: `assets/derivatives/visual-repair-20261020/scenes/tactical-future-clean-candidate-v1.png` (1678×937; SHA256 `e4b0bfd0e75e600afeda1daa5b86934449ed8f63e94f6f88e313cbfbed6a3d01`)

The editing model refreshed surrounding material details as well as removing the specks. The scene captures retain the battlefield landmarks and bridge placement under the unchanged grid transform; the source and geometry remain separate, and these are not owner-accepted art plates.

## Live verification

The bound sources were rendered through the actual Tactical UI for both ages at 825×375, 933×424 and 1280×720. All six runs loaded the selected image, retained the 70-cell board, and reported zero browser errors and zero failed responses. The white dots are absent in the live screenshots. Reports and captures:

- [Medieval age 3 report and captures](tactical-clean-live-age3/)
- [Future age 7 report and captures](tactical-clean-live-age7/)

The independent scene-sampling script evaluated the two candidate sources against frozen geometry. Both had 82 route samples, zero route/obstacle intersections, both bridge approaches aligned, and minimum sampled clearances of 1.09 world units (Medieval) and 1.12 (Future). The full 32-scene ledger still reports OPEN; these metrics do not replace a human physical trace.

## Comparison and remaining acceptance

The approved [M15 tactical mock](../../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/15-tactical-action.jpg) also uses a readable river crossing and a battlefield grid. The new scenes preserve that relationship and remove the baked markers. Remaining work includes full mock fidelity, roster-density parity with the mock, the other open scene traces, natural-play coverage, independent desktop review, and the later exact-package/device/owner gates. No APK was built for this visual checkpoint.
