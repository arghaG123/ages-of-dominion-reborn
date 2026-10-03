# Mock fidelity audit and design review status

Reviewed 2 October 2026. This audit rechecks all nineteen owner-supplied JPEGs against the proposed fresh plan and the static design-preview storyboard. It does not approve implementation or claim the previews are a working game. Owner review remains PENDING. Root DECISIONS.md governs current phase and exact-30/one-active-batch generation policy.

## Critical corrections from the earlier plan

1. **Seventeen pads, not ten.** Full-resolution 15_starter_kingdom_day1.jpg contains seventeen visible plus markers: nine in the upper development area, eight in the lower area. The hall is a separate eighteenth site. Ten old building types cannot be used as a ten-location cap. Walls are a perimeter system, not a plus-pad building. Every visible pad in the proposed layout must ultimately have a persistent selectable instance; no fake markers. Producer multiplicity, unique facilities, costs, output aggregation and save schema require explicit rules before implementation. Their balance is not approved merely by this count correction.
2. **World composition comes first.** The town/citadel, surrounding wall ring, broad populated interior and right river dominate the kingdom. A tiny settlement with a large resource dashboard is not a faithful interpretation. Mature density must grow from genuine state plus independent decorative dressing.
3. **Six actual gear slots.** Helmet, Chest, Weapon, Greaves, Shield and Ring surround the full character. The old four-slot baseline is a migration gap. The static preview uses existing Helmet/Chest/Weapon/Greaves art and visibly documented vector placeholders for Shield/Ring; it does not pretend six slots already work.
4. **No account/server/cloud surface.** The title's local entry actions replace the baked server/login utilities; Settings has local save management. Future Google Play publication is a distribution goal, not a cloud-save requirement.
5. **Exact scene appearance is distinct from baked text.** Mock numbers, invented CP, wave totals, rarity names and cloud toggles are not balancing rules. Proposed values are illustrative until implemented from real campaign data.
6. **Adventure is a landscape.** Roads, bridge crossings, forests, mines, guarded ruins, hero travel and fog should be inhabitable scenery. The collage's checkerboard/node representations are not acceptable as the principal world.
7. **Preserve actual roster scope.** Eight hero classes and eight neutral creature identities/dwellings remain full-product scope. Harpy, Griffin, Wyvern and Drone retain flying roles. New POV modes, PvP, gacha and exotic setting expansions are not prerequisites.
8. **Defense uses campaign resources and owned inventory.** Existing tuned tower functions remain, with age-appropriate visual identity. The plan does not invent a temporary defense currency, kill-cash economy or duplicate free deployment. Owned towers and real persistent Purchase/Retrofit costs must be clearly distinguished by future implementation.

## Measurement method and precision

Source JPEG sizes and hashes are exact in references/visual-targets/index.json. Placement measurements below are manual pixel readings from the unmodified raster at source size. Small ornamental glows and anti-aliased rims make bounds approximate (typically ±3–6 source pixels); this is not an extracted Figma specification. Normalized x/y are source pixel centers divided by width/height. Measurements communicate the actual supplied composition rather than arbitrariness; future comparison must inspect pixels at matched aspect and viewport.

Do not treat source-space visible ornament as the complete interaction target. At 424px width, a 32–36px visible medallion needs a separate 48px target, clamped fully inside safe insets. A center guide x=0.04 would be only 17px from the left edge; clamp its target center to at least safeLeft+24px. This accessibility adaptation must preserve edge clusters and central world visibility. A taller 424×933 display needs controlled camera reveal, not stretched architecture or uncontrolled cover-cropping of the river/walls.

## Seventeen Day 1 pad centers

Reference size: 720×1280. IDs are a proposed stable spatial ordering, not existing legacy building-type IDs. A plus center is only the interaction anchor; use the surrounding fenced ground polygon as the future footprint.

| Proposed pad | Source center x,y | Normalized x,y | Region |
|---|---|---|---|
| P01 | 260,512 | .3611,.4000 | Upper, near left of hall approach |
| P02 | 469,519 | .6514,.4055 | Upper, near right of hall approach |
| P03 | 191,554 | .2653,.4328 | Upper left |
| P04 | 311,553 | .4319,.4320 | Upper inner left |
| P05 | 410,553 | .5694,.4320 | Upper inner right |
| P06 | 539,559 | .7486,.4367 | Upper right |
| P07 | 110,615 | .1528,.4805 | Upper outer left |
| P08 | 177,631 | .2458,.4930 | Upper left below branch |
| P09 | 570,603 | .7917,.4711 | Upper outer right |
| P10 | 90,756 | .1250,.5906 | Lower outer left |
| P11 | 640,756 | .8889,.5906 | Lower outer right |
| P12 | 135,817 | .1875,.6383 | Lower left |
| P13 | 567,801 | .7875,.6258 | Lower right |
| P14 | 246,852 | .3417,.6656 | Lower inner left |
| P15 | 482,861 | .6694,.6727 | Lower inner right |
| P16 | 309,920 | .4292,.7188 | Lower front left |
| P17 | 419,923 | .5819,.7211 | Lower front right |

Central hall visual footprint is approximately x=.37–.64, y=.21–.32; rocky terrace spans roughly x=.29–.70, y=.28–.39. Its functional site is separate from all plus pads. The road/plaza occupies the center. Front gate is near x=.46, y=.79; walls curve around the lower settlement. The river and bridge at lower-right are key composition anchors.

The storyboard overlays selectable preview pad targets at all seventeen measured centers. The immutable JPEG still supplies fenced footprints and the painted hall, explicitly for design composition review. It is not a state-aware terrain asset. The future implementation must separate hall, wall, terrain and actual buildings, and make every visible pad real.

## Reference-by-reference audit

| Reference and exact size | Principal layout evidence | Adopt / correction / preview status |
|---|---|---|
| 00_title_splash_screen.jpg · 768×1376 | Crest/title occupies x≈.07–.93, y≈.05–.23. Scenic castle dominates center/right. Entry button centered near x=.50,y=.80, width≈.51. Loading strip near y=.91; utilities in bottom≈9%. | Preserve cinematic title, main entry emphasis and footer placement. Replace server/account/notice with local Continue/New Game/Load/Settings. Proposed preview retains immutable scene/title core with code-native local controls; no account/cloud action. |
| 01_stone_age_kingdom.jpg · 768×1376 | Same broad valley and city, primitive hall/stone monument at upper-middle; vertical left and lower-right medallions. | Preserve composition. Do not retain medieval cottages as Stone housing in final kit. Preview scene is an unchanged owner target, not newly generated art. |
| 02_bronze_age_kingdom.jpg · 768×1376 | Central terracotta/plaster citadel, dense lower settlement, wall ring, farms and boats; top compact rail. | Preserve terrace and city site while evolving structure materials. Bronze preview is target composition with separate DOM HUD. |
| 03_medieval_age_kingdom_reference.jpg · 571×1024 | Hero portrait near x=.035,y=.022; top bars left/right corners. Upper utility centers near x=.033,y=.075/.115/.153. Castle center about x=.50,y=.28; walls/town fill center .30–.84. Lower-left centers near y=.790/.833/.875/.918/.969. Lower-right near y=.878/.927/.974. | Main mature anchor. Keep elevated keep, wall perimeter, close town density, river/bridge and very compact edge HUD. Do not adopt tiny outlined old panorama. Reference comparison is available next to proposed target-backed HUD mock. |
| 04_gunpowder_age_kingdom.jpg · 768×1376 | Palace silhouette, mills, docks/boats; same valley/river/wall/city geometry. | Evolve town and equipment as well as palace. No new geometry just because a different generated panorama exists. Preview uses supplied age target. |
| 05_industrial_age_kingdom.jpg · 768×1376 | Central stone/brick identity, factories, smoke and iron rail bridges across the same river; gold edge HUD. | Preserve recognizable geography, era machinery and smoke visibility. Final town dressing must change materially. Preview uses supplied target; no animations claimed. |
| 06_modern_age_kingdom.jpg · 768×1376 | Tall central glass tower, modern roads/vehicles/solar fields and bridges, lower buildings within wall footprint; steel/blue medallions. | Full age transformation, retaining city location. Modern HUD material needs cooler metal while maintaining shared identity. Preview adopts image as design anchor only. |
| 07_hero_character_screen.jpg · 768×1376 | Hero occupies center x≈.25–.72,y≈.16–.68. Left equipment centers near x=.154,y=.222/.372/.523; right x=.846 at same rows. Identity plate near y=.69. Stat area y≈.72–.86; Upgrade/Skill Tree near y=.904; icon tabs along y=.970. | Six real slots, character-first staging and lower stats. Existing blue-cloth knight is reusable but does not match red-cape silhouette. Shield/Ring assets missing acceptance; vector placeholders in preview clearly disclosed outside scene. Skills/Spells proposed layouts supplement reference. |
| 08_equipment_forge_screen.jpg · 768×1376 | Header y≈.025–.075, close/back corners. Selected sword x≈.15–.86,y≈.16–.23 above a stone stand; selected info y≈.35–.47; five-column inventory y≈.50–.83; three action panels y≈.855–.925; bottom utilities. | Preserve item focus, dark forge, rarity/inventory area. Proposed layout uses real existing sword and item cutouts, four readable columns on phone as accessible adaptation. Reforge/sockets need rules before controls; no inert copied buttons. Stone stand still provisional CSS surface. |
| 11_tower_defense_screen.jpg · 768×1376 | Keep far upper-right; path winds from lower scene upward; towers occupy terrain on both sides. Wave/gate crest centered at top, four-tower tray x≈.12–.88,y≈.79–.905, hero abilities/speed below. | Proposed defense uses layered existing terrain, authored code-native winding path, tower cutouts, enemies and compact bottom tray. Camera/shadow/animation provisional. No repeated cost labels establish a guessed economy. |
| 13_army_roster_screen.jpg · 720×1280 | Selected full unit upper x≈.32–.65,y≈.08–.45; stats plate right x≈.67–.97,y≈.31–.45. Divider near y=.50; four class panels in lower area y≈.52–.83; recruitment strip and mini cards below. | Selected-unit stage and actual roster. Preview three current troop roles plus neutral creature access, without pretending the pictured fourth siege class already has matching rules/art. Full eight neutral creatures retained. Exact four-category product decision remains explicit review item. |
| 14_settings_more_screen.jpg · 720×1280 | One centered framed panel x≈.12–.88,y≈.27–.74 over blurred kingdom, title in upper panel; evenly spaced settings rows. Edge medallions remain. | Proposed centered dark panel preserves footprint; separate audio/motion/language/local save. Cloud Save replaced with local management. Buttons in static preview only switch layouts; slider/toggle mechanics are future implementation. |
| 15_starter_kingdom_day1.jpg · 720×1280 | Seventeen measured plus sites and separate hall/terrace; large empty central plaza; incomplete perimeter; sky/mountain band and river at right. | Count correction above is mandatory for fidelity. Preview all seventeen targets. Type assignment/repetition requires owner review and balance, not fake pads. |
| image_1a731519.jpg · 1408×768 | Landscape adventure fills frame; roads connect castles, mine, bridge and guarded sites; party rail upper/left, army/minimap upper-right, actions lower-right. | Adopt actual spatial exploration and edge actions. Cartoon linework is weaker than realistic material standard. Proposed view uses real terrain/props/actors with authored road/fog overlay, explicitly provisional. |
| image_f1fc2a4d.jpg · 1408×768 | Hero visibly on bridge/road; glowing landmark at right, mine upper-middle, castle upper-right, woods and loot. | Bridge crossing and world site coordinates must align with legal routes; turn budget and fog persist. Same Adventure preview represents these features without importing baked UI. |
| image_d2571c4b.jpg · 1408×768 | Nine-screen collage: towns/biomes, management, inventory, route previews, tactical grid, dragon event and upgrade trees. | Supports dedicated contextual screens, not nine different dashboards. Tactical preview uses coherent terrain plus subtle grid and independent stacks; inventory/skills/spells/story previews are separate proposed surfaces. |
| image_447bd8ac.jpg · 1408×768 | Tower mode montage with aerial/first/third person, tower upgrade trees, enemy info, PvP, summon. | Retain aerial defense, tower upgrades and enemy/Codex inspection. First/third person, PvP and gacha remain later explicit scope decisions, not initial dependencies. |
| image_49c5727f.jpg · 1408×768 | Massive realistic defense landscape, winding approach and distinct towers/actors/FX; party top-left, resource/health top-right, compact lower-right actions. | Inform material quality and defense terrain/engagement. Static preview has fewer actors by design for clarity, not a claimed final density/animation pass. War surface links to this mode rather than inventing a separate simulation. |
| image_d33c02c.jpg · 1408×768 | Montage of setting/POV variants, winding top-down lanes, magic, airborne enemies and boss. | Airborne roles already in roster retained; exotic boss/settings/POV expansions later. Codex shows actual retained creature scope. No cyberpunk campaign requirement inferred from this collage. |

## Preview limitations requiring explicit feedback

The thirty views show proposed composition and screen purpose, not production completeness. Existing human character cutouts often use frontal perspective; the world camera and animation kit still need matching. Several class portraits are armored reskins, so distinct mage/ranger/barbarian identity needs further art review. Shield/Ring placeholders and Iron/Future concepts are explicitly unapproved. Iron/Future have no age-specific image among the supplied nineteen references; a Medieval composition study cannot prove their final look.

Kingdom previews use the owner's immutable JPEG central world for an honest appearance target, with localized baked-edge HUD exclusion and separately rendered controls. They cannot demonstrate construction or district state, and must never be presented as a finished independent renderer. Compare original is an unmodified reference beside the proposal. Taller/landscape mock modes preserve image aspect, exposing unfilled/blurred overscan rather than stretching or claiming camera registration. The future AI must implement a bounded state-aware world once the owner approves the design direction.

Every inside-scene button is a preview navigation/state demonstration; no currency, building, combat, troop count or savegame is changed. The outside feedback field stores a review note on this device and can export notes. Reading, switching a view, saving a note or viewing screenshots is not implementation authorization or acceptance.

## Section feedback register

| Section | Views | Status and unresolved feedback |
|---|---|---|
| Entry / hero choice | 01–02 | PENDING — local actions, eight-class presentation, class-distinct art |
| Kingdom / ages / build | 03–13 | PENDING — seventeen-pad layout, producer/facility multiplicity, evolved districts/perimeter, Iron/Future identity |
| Hero / Army / Forge / Inventory / Skills / Spells | 14–19 | PENDING — six-slot framing, class identity, roster grouping, item grid and rules-backed actions |
| Adventure | 20 | PENDING — aerial landscape/camera, route/fog/party HUD, dwelling and guarded-site appearance |
| Tactical | 21 | PENDING — closer camera, stack grounding, grid contrast, action/initiative placement |
| Tower defense / War | 22–23 | PENDING — lane/pads, tower era art, wave/ability tray, kingdom-resource clarity |
| Story / Quests / Market | 24–26 | PENDING — chapter/journal depth, contextual surfaces and actual economy data |
| Settings / Saves / Codex / Tutorial | 27–30 | PENDING — panel footprint, local recovery states, discovery scope and single-step tutorial |

Owner can respond by section, for example “Adventure: move the party controls; make the camera higher.” Apply requested design corrections, update this register and retain the no-game-code phase until feedback is resolved. Browser captures verify rendered layout identity and clipping only; they do not constitute owner approval or hardware/gameplay acceptance.


## Latest scoped revision — 3 October 2026

Review `design-preview/review-reference-direction.html` for Resources, Adventure and Tactical. The AVIF was browser-decoded and visually inspected. Phone resources now show grain/provisions, logs, rock and coins at32px height above names/amounts. Existing aerial forest/river/road and ruins/stone-bridge art replaces the empty-grass studies; settlements/sites/guards/treasure and six count/health-bearing formations are added as static scale studies. Precise reuse and remaining gaps: `docs/plan/REFERENCE-DIRECTION-2026-10-03.md`.

Nine scoped literal captures at375x825/424x933/820x462 and shell checks at375/768/1280 passed asset/JS, resource/count bounds and48px scene button checks; final selected pixels were reviewed. Resource text contrast is approximately9.0:1/7.1:1. The375px gallery shell contains a341px scene. This is neither a full30-view audit nor physical-device/visual acceptance.

Still missing: clean transparent resource objects, larger fortified/biome-rich Adventure region with stone bridge, matching aerial site/actor camera, class-correct mounted Gawain and directional gait, high-detail Tactical terrain registered to legal7x10 cells. Some provisional cells/poses overlap painted obstacles. Current previews improve density but still fall short of the new target. Every section remains pending/revision-needed. Old game/raw art preserved read-only; no game source, installs/builds/APKs, image jobs or billing changes. Single-agent work only.

