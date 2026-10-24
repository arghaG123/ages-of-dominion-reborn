# Adventure fog-edge repair — 20 October 2026

## Change

The previous renderer painted one translucent polygon per unvisited cell. Its straight cell edges made large panels across bright sand and snow. The renderer now builds one non-interactive SVG mask from the same unvisited cells, softly feathers only the boundary, then applies the low-opacity terrain tint. The saved `adventure.visited` membership remains the authority for fog, site discovery, movement and minimap content; this change only affects the visible edge.

## Live visual/runtime evidence

Reran the all-age Adventure browser sweep into the new `adventure-fog-repair-live/` folder, preserving the earlier review. It used valid isolated campaign envelopes, selected Adventure and left town in the browser at ages 0–7 and 825×375, 933×424 and 1280×720.

- 24/24 views loaded the registered terrain and displayed one fog overlay with a resolvable mask and blur filter.
- Each fresh entry had one visited cell; all other cells remained represented in the fog mask. The minimap and 160 Adventure cell targets continued to render.
- All observed controls stayed in-frame and received their center hits; page errors and failed responses were both zero.
- Manual comparison of Gunpowder and Industrial screenshots shows the previous broad, sharp-edged panels are softened without blurring the terrain artwork. The 1280×720 Gunpowder screenshot with fog is paired with a diagnostic capture where only the fog surface is hidden; they differ, confirming the overlay is active.

Evidence: `adventure-fog-repair-live/report.json`, `adventure-fog-repair-live/adventure-age4-1280x720.png`, and `adventure-fog-repair-live/adventure-age4-1280x720-fog-disabled-diagnostic.png`. The runner supports `AOD_ADVENTURE_REVIEW_OUT` so future runs can preserve dated captures.

## Acceptance boundary

This closes only the angular fog-edge defect. The current early-state campaign still has a sparse world compared with the advanced Adventure mocks: discovered settlements, named sites, people, pickups, encounter contexts, physical route/bridge trace and natural progression need separate review. All-age mock fidelity, full J01–J18 evidence, independent desktop acceptance, final APK, later device QA and owner acceptance remain open. No package or device work was done.
