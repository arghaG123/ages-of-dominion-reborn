# Adventure north-edge camera safety — 21 October 2026

**Result: targeted Adventure edge repair and bounded live checks PASS. The whole game remains INCOMPLETE.**

## Repair

The mounted traveler was clipped at reachable north-row cells because each 16×10 world map uses the full 1376×768 scene with no north art margin. The focus camera clamps at the image edge. A 64px inset kept the actor on screen but placed two tall mounts behind the header; a 128px inset with an unblended backdrop introduced a hard horizontal scene seam.

The current source now applies an edge treatment only when the traveler is in the field at y=0:

- Reserve a 128 CSS-pixel north inset without changing the world transform or traveler size.
- Show that world's existing low-detail biome terrain behind the inset with the established dark overlay.
- Fade the top 18% of the terrain image into the backdrop; the traveler and world overlay remain sharp.
- Clear both the backdrop and image mask after leaving the north edge.

No source artwork was edited or generated. The backdrop is a same-world biome image, not a geometrically registered extension of the integrated map.

## Natural edge journeys

Each run starts a fresh visible campaign, selects a world, enters Adventure, uses a read-only path search to choose an open reachable north-edge cell, previews and commits every cardinal step through the game controls, waits for durable save acknowledgement, and reloads the campaign. All runs used 825×375.

| World | North cell | Steps | Minimum gap below header | Live report |
|---|---:|---:|---:|---|
| Grasslands | (5, 0) | 6 | 31.0px | [report](adventure-north-safety-grasslands-live-20261021-run04/report.json) |
| Tundra | (8, 0) | 5 | 42.2px | [report](adventure-north-safety-tundra-live-20261021-run04/report.json) |
| Haunted Marsh | (10, 0) | 3 | 67.3px | [report](adventure-north-safety-haunted-marsh-live-20261021-run04/report.json) |
| Desert Volcano | (7, 0) | 5 | 32.6px | [report](adventure-north-safety-desert-volcano-live-20261021-run04/report.json) |
| Underworld | (2, 0) | 7 | 33.9px | [report](adventure-north-safety-underworld-live-20261021-run04/report.json) |
| Feywild | (6, 0) | 5 | 29.6px | [report](adventure-north-safety-feywild-live-20261021-run04/report.json) |
| Archipelago | (5, 0) | 7 | 31.0px | [report](adventure-north-safety-archipelago-live-20261021-run04/report.json) |
| Mesa Savanna | (4, 0) | 2 | 28.2px | [report](adventure-north-safety-mesa-savanna-live-20261021-run04/report.json) |
| Astral Peaks | (4, 0) | 5 | 15.1px | [report](adventure-north-safety-astral-peaks-live-20261021-run04/report.json) |
| Blood Moon | (6, 0) | 5 | 30.3px | [report](adventure-north-safety-blood-moon-live-20261021-run04/report.json) |
| Jade Karst | (6, 0) | 6 | 31.8px | [report](adventure-north-safety-jade-karst-live-20261021-run04/report.json) |
| Sunken Jungle | (9, 0) | 3 | 50.9px | [report](adventure-north-safety-sunken-jungle-live-20261021-run04/report.json) |

All twelve reports passed with no browser errors or failed HTTP responses. The minimum measured traveler-to-header gap was 15.1px. The current-source contact sheet is [here](adventure-north-safety-contact-sheet-live-20261021-run04.jpg).

Responsive spot checks also passed: [Astral Peaks](adventure-north-safety-astral-peaks-933x424-live-20261021-run01/report.json) and [Feywild](adventure-north-safety-feywild-933x424-live-20261021-run01/report.json) at 933×424, and [Grasslands](adventure-north-safety-grasslands-1280x720-live-20261021-run01/report.json) at 1280×720. Grasslands was then moved one legal step south after reload; the current-source report confirms the edge metadata, stage background, and terrain mask all clear at (5, 1): [exit cleanup report](adventure-north-safety-exit-grasslands-live-20261021-run02/report.json).

The full bounded Node suite and JavaScript syntax check passed after the source change. These are current-source browser and Node checks; they do not establish owner approval, full visual acceptance, mobile/device acceptance, or whole-game completion. The screenshots were reviewed together and at full size. The previous hard seam is substantially softened into a biome transition; this does not certify global scene registration.

## Remaining acceptance

The north-edge treatment is one targeted Adventure repair. Site, encounter, other-boundary, all-age, mock-fidelity, complete natural-journey, whole-game independent desktop, APK, device, and owner gates remain separate and open as recorded in the current status documents.
