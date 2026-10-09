# Actors and equipment handoff — 9 October 2026

Image AI 2 published local repairs and 18 regeneration packs. No Vertex call was made from this producer. `localProcessingComplete` is true. `imageWorkComplete` is false. `wholeDeliveryReady` is false. Runtime, device, and owner gates stay open.

## Reuse

Code crops kept byte-for-byte:

- troop-stone-melee `c61f0e3dec06a344744f3f4d21a6cf7dabdb4df61730c42eac535c7988f2104a` 1369x1852, translation [-477, -112]
- troop-industrial-ranged `5df473c9336451f51f2babf21ed88b7c5dc8bd5bc901615b8851a07c5183823f` 1247x1851, translation [-526, -103]
- troop-industrial-heavy `9455bf02f32921c7fa0bf3d2bce4f561e9c311a37e36ad99bd3dbafa7fcbc758` 1640x1921, translation [-233, -64]

## Local repairs

- Slinger crop `assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png` from native `937949e300d24d0b53d5f735cbf03f2a985800b3ef9c110a373b76f100e583f5`. Checker flood plus one enclosed-component correction. Sling and pouch remain.
- Stone helm and stone boots pink slabs cleared. Boots still have a thin sole fringe and stay PARTIAL.
- Other gear and artifact icons with the same pink predicate are in the derivative gear folder. Rows with many opaque components stay PARTIAL.
- Bronze charioteer, medieval heavy cavalry, and the barded horse were separated from flat backdrops. Ground patches or the horse plane remain, so those rows stay PARTIAL. Display cap for the charioteer and the horse is 64 CSS pixels on the longest side.
- Medieval ranged pose sheet split into 12 component frames. Primary review frame is frame 01.
- Effect sheets have component ROIs under `qa/image-vertex-repair-20261009/actors/recipes/`. Projectile and impact belong to ACTORS.

## Not claimed

Full class bodies, iron melee color, bronze runner, medieval archer, future sniper and hover tank, gunpowder cannon crew, medieval melee soldier, paladin head, and two transports are packs for AI1. The Knight thigh search was not repeated. `qa/image-local-solution-20261004/joints/knight_thigh_greave_correction_0.png` is still absent.

Ready rows in this interface: 104. Partial: 57. Failed: 6.

First-attempt reservation for 18 packs at 0.4 USD is 7.2 USD against 8.8844 USD headroom. A second attempt on every pack does not fit. Invoices are UNKNOWN. The 15 USD reserve is untouched.

## Code, after both image producers finish

Bind the slinger crop through the plate override path. Keep the three crops above. Use `visible-size.js` conservative caps. Gear icons, artifact icons, mounts, and effect atlases still need explicit screen bindings. This handoff does not edit `src/`.
