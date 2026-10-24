# Adventure all-age live visual review — 20 October 2026

**Focused result:** 24 isolated visual fixture runs passed the bounded runtime/layout checks; Adventure visual fidelity remains incomplete against the approved mocks. Whole game remains **INCOMPLETE**.

## Scope and method

`adventure-all-ages-live/report.json` records age-only valid visual fixtures at 825×375, 933×424 and 1280×720. Each run entered Adventure and left town. This is a scene-selection and responsive-layout review; it is not natural age progression, a complete route journey, physical trace acceptance, or owner approval.

All 24 runs loaded the registered age scene, rendered the Adventure board and all 160 Adventure cell targets, showed the minimap, and kept the observed controls inside the viewport and responsive to center hits. There were zero browser errors and zero failed network responses. The screenshots were manually reviewed at 1280×720, with additional review of the Industrial scene at 825×375.

## Scene mapping and evidence

| Age | Registered scene | Live capture |
|---|---|---|
| Stone | `assets/derivatives/professional-20261018/scenes/adventure-stone-organic-v1.png` | [1280×720](adventure-all-ages-live/adventure-age0-1280x720.png) |
| Bronze | `assets/derivatives/visual-repair-20261020/scenes/adventure-bronze-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age1-1280x720.png) |
| Iron | `assets/derivatives/visual-repair-20261020/scenes/adventure-iron-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age2-1280x720.png) |
| Medieval | `assets/derivatives/visual-repair-20261020/scenes/adventure-medieval-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age3-1280x720.png) |
| Gunpowder | `assets/derivatives/visual-repair-20261020/scenes/adventure-gunpowder-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age4-1280x720.png) |
| Industrial | `assets/derivatives/visual-repair-20261020/scenes/adventure-industrial-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age5-1280x720.png) |
| Modern | `assets/derivatives/visual-repair-20261020/scenes/adventure-modern-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age6-1280x720.png) |
| Future | `assets/derivatives/visual-repair-20261020/scenes/adventure-future-clean-v1.png` | [1280×720](adventure-all-ages-live/adventure-age7-1280x720.png) |

## Visual findings

- The landscape scenes are detailed and fill the frame. The age-specific town art reads at a glance, and the hero remains visible against each scene.
- On the brighter sand and snow scenes, the unvisited-cell fog reads as broad, sharp-edged polygonal panels over the landscape. These shapes are runtime fog, not seams baked into the scene images: Adventure paints a translucent `.fog` polygon for every unvisited cell (`src/client/main.js`, `src/client/game.css`). The fixed cell geometry produces a noticeable map-shaped boundary, especially in the Gunpowder and Industrial captures.
- Against the approved Adventure mocks (`11-adventure-overview.jpg`, `12-adventure-crossing.jpg`, `13-adventure-foot.jpg`), the live view is substantially under-populated. The reviewed state contains one town and the hero, without the mock’s named sites, occupied settlement, guards/other people, pickups or contextual site panel. The screenshots therefore do not establish mock-level composition or encounter presentation.
- The live HUD is compact and remains in-frame at the inspected sizes: minimap and journey prompt on the left, resources and menu controls on the right, and the icon dock at lower left. The geometry/hit assertions establish exposure and center input only, not visual acceptance for every Adventure interaction.
- Age 7 combines future-era town art with a devastated ruin landscape. This is legible as a future setting, but the scene/mood coherence against the approved mock direction remains unaccepted.

## Acceptance boundary

The run report is a **focused PASS** for loading and layout only. It is **not** a natural all-age journey and does not verify physical routes, bridge/cell alignment, visited-mask progression, every location interaction, or mock parity. No production art or game source was changed during this verifier pass. Whole-game scene, natural journey, independent desktop, final snapshot APK, later device and owner gates remain open.

Machine evidence: [24-run report](adventure-all-ages-live/report.json) and [capture runner](adventure-all-ages-live-20261020.mjs).
