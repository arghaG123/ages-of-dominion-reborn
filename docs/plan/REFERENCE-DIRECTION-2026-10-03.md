# Scoped reference and design revision — 3 October 2026

Latest review: `../../design-preview/review-reference-direction.html`. Live proposals: `../../design-preview/index.html#adventure` and `#tactical`. This record supersedes earlier claims that the empty-grass studies meet the target or that nominal icon dimensions establish legibility. Owner acceptance remains pending; implementation is not authorized by this revision.

## Reference review completed

All seven supplied files remain in `references/owner-additions-2026-10-02/` unchanged, including the exact duplicate pair. The previously unread AVIF successfully decoded in installed Chrome at its original 470 × 264 size; browser evidence is `../../design-preview/evidence/reference-direction/owner-avif-browser.png`. It shows a close oblique battlefield, distinctive formations, projected square planning cells, bottom initiative portraits and compact commander/actions. It supports camera, scale and HUD study. Its creatures, formulas and labels are not adopted mechanics. The other six raster references retain their already-recorded interpretation in REVIEW-NOTES.

## Resource contract and actual preview changes

Four campaign resources remain Food/Wood/Stone/Gold. The inspected Medieval Wood asset is a shield and Stone is a tower; Food is a dark embossed medallion. These are unsuitable material symbols even when enlarged. The revised HUD presents 32px-high objects above explicit names and readable amounts, separate from navigation medallions. Food reuses the center of Bronze grain/provisions artwork. Logs, rocks and coins use CSS source windows from `image_4f5e15d7.jpg`; dark crop pixels blend into the rail. Owner raster bytes are unchanged. This is permitted static appearance evidence, not cleaned or adopted runtime resource art.

Inspect the 375px capture at native scale: `adventure-375.png`. Objects can be distinguished in the revised pixels; owner feedback is still needed on size, appearance and legibility. Clean transparent material icons with natural shadows remain missing. CSS blend treatment lightens dark material detail and is not an approved extraction technique for production. Labels support recognition rather than conceal the art gap. Values are illustrative, with no changes to starting supplies or economic formulas.

## Adventure composition

The revised study reuses `map-land-forest.webp`: an aerial continuous road, river, wooden bridge, forests and rocky elevation. Existing Medieval hall/mine/workshop illustrations provide settlement, guarded mine and dwelling scale studies; a bandit marks a guard, coins mark treasure, and a hero occupies the central road/crossing region. A route, movement budget and compact contextual actions remain visible. Portrait is primary. Landscape uses a full-width terrain crop with bounded sites and controls. These static layouts do not prove a larger authored region, legal path, fog, collection, minimap, navigation or movement spending.

Future authored composition must connect an inhabited settlement, stone crossing, mine, guarded ruin and forest dwelling with physically readable roads. Keep elevations and biome edges visible, without covering central geography with cards. Site clusters require aerial camera, matching lighting and smaller environmental scale, rather than oversized single inspection buildings. The current wooden bridge is a mismatch with the stone-crossing target. Settlement fortifications, ruins and richer biome/terrain transitions remain missing. The displayed cavalry is a provisional mounted scale reference, not class-correct Gawain. The foot/mounted control switches static poses only; misleading static translation-as-travel was removed.

## Tactical composition and unchanged rules

The revised study reuses `map-land-ruins.webp`: stone crossings, broken walls, rocky terraces and aerial paths. It adds six three-figure formations with independent count badges and health strips; the commander is visually separate from troop stacks. Compact encounter/initiative information and Move/Attack/Defend/Wait/Spell/Retreat actions surround the terrain. Sample health/count/round data is illustrative. Painted figures are cosmetic stack representatives, never new separately simulated units.

Preserve seven columns × ten rows and commander `(0,9)`. Portrait is the primary phone arrangement; landscape is an alternative inspection/combat presentation. The final camera must fit useful formations and planning areas without cropping flanks. Terrain, bridge decks, terrace heights and legal cells need one registered projection. Current CSS grid/cell marks do not establish that projection or terrain legality: some cells/actors overlap painted walls. This remains an open visual/registration defect. No hex topology, flanking rules, rival identity or new creature family is inferred from the new samples.

## Precise reuse and art gaps

| Role | Reuse / evidence | Remaining gap |
|---|---|---|
| Resource symbols | Existing Bronze provisions; owner logs/rocks/coins as CSS windows | Four clean transparent object assets; natural shadow and dark detail preserved at phone scale |
| Adventure ground | Existing 512 × 512 forest road/river/crossing | Portrait-authored larger region, stone bridge, settlement approaches and varied biomes/elevations |
| Adventure sites | Existing Medieval hall, mine and workshop | Fortified settlement, aerial ruin/dwelling clusters, camera/scale/light agreement and meaningful site variants |
| Hero | Existing knight on-foot pose and cavalry mounted stand-in | Class-correct Gawain horse/rider, directional facing and complete walk/ride gait frames |
| Tactical ground | Existing 512 × 512 ruins/stone bridge region | Higher-detail coherent 7 × 10 projection; accessible crossings, cells and occluder registration |
| Formations | Existing melee/ranged/cavalry/bandit/wolf static poses | Facing/grounding, banners, distinct selected/target states and complete action/effect animations |
| Minimap and world states | New references establish desired hierarchy | Genuine region-derived minimap/fog/site state; omit fabricated map behavior from static proof |

Five additional existing assets were copied unchanged and SHA256-verified in `design-preview/asset-provenance.json`: forest/ruins ground, Medieval mine/workshop and Bronze Food icon. No paid images or pixel edits occurred. These gaps refine the existing useful-art backlog; they do not authorize submissions, alter the exact30/single-active policy, remove items from full scope or claim billing/job-state resolution.

## Verification and acceptance limits

Installed Playwright 1.62.1 with installed Chrome produced nine captures: Adventure/Tactical/Medieval at literal 375 × 825, 424 × 933 and 820 × 462. Scoped page/asset errors, broken images, clipped resource entries/counts and scene buttons under 48px: none. Shell widths 375/768/1280: no horizontal overflow. Resource amount/label contrast: approximately 9.0:1 / 7.1:1. Foot/mounted pose selection works. Tactical study contains 70 cells. These are documentation checks, not rules tests, hardware UX or acceptance.

At a 375px gallery shell, the contained scene is 341px wide; literal 375px captures are separate evidence. Selected final phone and landscape pixels were inspected and compared with the supplied references. No complete30-view audit was repeated; the larger resource rail can affect other gallery content and requires future scoped/full review before gallery freeze. Every section remains pending/revision-needed, with no new owner acceptance. No game source, dependencies, builds/APKs, image jobs or old-project writes occurred.

Final evidence check: all7 new-reference hashes and all5 newly reused asset hashes match their records. The actual375px shell /341px Adventure frame was also captured and visually inspected (`adventure-shell-375.png`); the resource names/objects/amounts remain visible. Review comparison page images decode without errors. Resource crops preserve source aspect ratio.
