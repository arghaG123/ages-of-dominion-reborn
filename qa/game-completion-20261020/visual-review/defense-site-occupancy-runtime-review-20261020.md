# Defense site occupancy runtime review — 20 October 2026

**Result: runtime positions PASS; physical scene fit remains PENDING.** The all-age isolated preview started Siege at age 0–7 with eight synthetic tower records occupying D1–D8. The rendered runtime IDs matched the frozen site order in every age, each registered terrain image loaded, and the browser reported zero errors.

Evidence:
- Capture script: `defense-all-sites-live-20261020.mjs`
- Synthetic fixtures: `defense-all-sites-fixtures/` (duplicate tower families are used only to render all eight sites simultaneously; this is not a valid purchase history or balance test)
- Per-age 1280×720 captures and runtime report: `defense-all-sites-live/`
- Eight-age contact sheet: `defense-all-sites-live/defense-eight-ages-all-sites-contact-20261020.png`
- Frozen site geometry and affine: `src/data/implementation-contract.json`, `geometry.defense`

Visual observations from the live renderer:
- The site centers render on the expected contract coordinates. The tower plates are placed by the oblique/isometric source transform; the runtime does not independently rotate site coordinates.
- Age 2 D7/D8 render against the castle battlements/gatehouse. Age 5 D6 and age 7 D6 render at bridge decks. Those can read as intentional wall/bridge emplacements, so the screenshots alone do not prove a collision.
- The earlier source-space trace flags remain useful review prompts, especially water-edge and masonry locations. They are not sufficient grounds to move frozen gameplay sites or repaint the source artwork.

No production scene asset or gameplay geometry was changed in this review. Keep `mode-scenes.json` candidates at `CANDIDATE_RUNTIME_CHECKED_PHYSICAL_TRACE_PENDING` until mock-led fit criteria and rendered depth are signed off. This synthetic fixture does not prove natural campaign progression, ordinary owned tower capacity, balance, or owner acceptance.
