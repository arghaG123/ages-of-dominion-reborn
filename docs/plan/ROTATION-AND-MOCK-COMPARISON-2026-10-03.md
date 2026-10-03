# Owner rejection, mock comparison and mobile rotation — 3 October 2026

The owner explicitly rejected the latest scene assembly as still far from the supplied real-game-looking mocks. Resource objects are too large; battles do not need a resource HUD. Phones can change orientation to give Adventure/Tactical more useful map space. This feedback supersedes the prior 32px-object/72px-panel proposal and any hard portrait-first restriction or automatic reset of narrow landscape requests. Both orientations must work; use the wider view when the player rotates.

Latest review: `../../design-preview/review-mock-comparison.html`. All supplied originals: `../../design-preview/all-owner-mocks.html`. Edge-to-edge static review with automatic orientation: `../../design-preview/index.html?stage=1#adventure` / `#tactical`. These are review documentation, not a playable game or final design acceptance.

## Actual visual findings

| Dimension | Supplied mocks | Rejected assembly | Required correction / current state |
|---|---|---|---|
| Camera | Authored aerial/three-quarter scene; terrain, sites, hero and armies agree | Top-down512px terrain mixed with isolated inspection-building and frontal actor cutouts | One registered scene camera and matching aerial/oblique assets. Still unresolved |
| World richness | Fortified settlements, river/stone bridges, roads, rocky terraces, ruins, biomes and inhabited detail | Forest patch with three pasted buildings; Tactical small ruins texture | Existing high-resolution ruins panorama now gives sharper material study; full Adventure/Tactical composition remains unfulfilled |
| Scale and grounding | Settlements integrated into terrain, figures contact ground, formations have depth/facing | Buildings too large, repeated poses, feet/cells overlap painted obstacles | Aerial site clusters and properly faced actors/formation projection. Still unresolved |
| Interface | Small resources, compact hero/initiative/actions, ornament with stone/metal identity | Large resource panel, long title bands, generic rectangular footer | Compact rail and reduced floating/context controls corrected; bespoke frame/material finish still missing |
| Mobile space | World remains dominant; camera/layout can adapt | Landscape could revert to tall below600px; gallery chrome consumed room | Removed landscape reset; auto mode responds to viewport orientation; edge-to-edge static review available |

The visual outcome is still below the owner's target. Do not substitute technical checks, an attractive raw panorama or a displayed original mock for a passing assembled game scene.

## Supplied reference coverage

The all-reference overview contains all19 original files and7 new files, including the retained duplicate and AVIF. Overview pixels were inspected as one contact sheet; the main Kingdom, latest Adventure/Tactical and close tactical references received targeted full-image comparison. This is not a new full-resolution audit of every detail in every montage.

| Reference group / files | Visual contract observed |
|---|---|
| `00_title_splash_screen.jpg` | Cinematic lighting, rendered ornament and compact entry controls |
| `01_stone_age_kingdom.jpg`, `02_bronze_age_kingdom.jpg`, `03_medieval_age_kingdom_reference.jpg`, `04_gunpowder_age_kingdom.jpg`, `05_industrial_age_kingdom.jpg`, `06_modern_age_kingdom.jpg` | Shared dense-city footprint, strong citadel, river/landform continuity, era-specific material identity, small corner resources/edge symbols |
| `15_starter_kingdom_day1.jpg` | Same coherent geography while sparse; all17 build sites plus separate Hall retained |
| `07_hero_character_screen.jpg`, `08_equipment_forge_screen.jpg`, `13_army_roster_screen.jpg` | Full-character/item/unit stage with material-rich frames; six actual gear slots and contextual controls; no generic dashboard substitution |
| `14_settings_more_screen.jpg` | Restrained contextual framed overlay; world remains background context |
| `11_tower_defense_screen.jpg`, `image_49c5727f.jpg` | Authored winding approach, terrain/actor/tower scale, depth and compact battle controls. Latest owner instruction removes resource HUD even where samples differ |
| `image_1a731519.jpg`, `image_f1fc2a4d.jpg` | Connected bridges/roads/sites, discoveries and travelling hero; structural reference while shared semi-realistic finish governs |
| `image_d2571c4b.jpg` | Separate contextual surfaces and battle/world modes; source collage/captions must not become scene art |
| `image_447bd8ac.jpg`, `image_d33c02c.jpg` | Terrain-rich defense/motion/ability/inspection ambitions; expansion POV/PvP/gacha or extra creatures are not automatic scope |
| `image_4f5e15d7.jpg`, `image_3a075f90.jpg` | Rich inhabited Adventure geography, fortified settlements, mines, dwellings, stone crossing/elevations/biomes; recognizable small object resources |
| `image_27abdc40.jpg`, its unchanged numbered duplicate, `image_4eb3e86f.jpg` | Grounded readable army groups, three-quarter depth, stone crossings/terraces and terrain detail; new pictured creature families are not adopted |
| `56c4947b88a7e300458b45f8-1.webp`, `5e83227346177c16c343c9b5.avif` | Close tactical actor scale, projected square planning cells, compact commander/actions and bottom initiative |

## Review corrections actually made

- Resource symbols are18px high with amounts alongside, in a28px corner rail. The previous extra label row and72px panel are removed. Existing recognizable material subjects remain; clean transparent independent resource art is still a gap.
- Tactical and Defense emit no campaign resource HUD into the review DOM. Defense's wave text no longer presents the treasury. Shared four-resource campaign economy and persistent purchase rules remain unchanged; this is visibility, not a new combat economy.
- Adventure/Tactical Auto mode chooses portrait or landscape from actual viewport orientation. Manual landscape no longer silently reverts because the contained gallery frame is narrow. The `?stage=1` review occupies100dvh/100%width, without gallery header/sidebar/footer consuming space. Scene selection and static foot/mounted pose survive resize.
- Adventure terrain fills the viewport, contextual controls are compact, and oversized site cutouts are reduced. The512px source still cannot provide the inhabited larger-world finish.
- Tactical copies the unchanged6336x2688 raw ruins panorama from `C:/dev/aod-art-src/battle-ground-ruins/attempt-3.png`, hash-recorded as `tactical-ruins-original.png`. An aspect-preserving source crop removes sky from the planning region. It is a sharper material study, not approved terrain/cell geometry. Units still overlap some painted masonry and have incorrect matching scale/facing; coherent battle art remains missing.
- Tactical title/initiative/actions are smaller and concentrated at edges/corners. Count and health overlays remain separate from cosmetic figures; seven columns × ten rows and commander(0,9) remain unchanged.
- Direct target/current/rejected comparisons replace the earlier review presentation. Original owner images stay labeled as evidence and are never presented as an authored playable scene.

## Remaining production requirements

The next scene proof must use a coherent high-detail Adventure region and a tactical battle ground/actor set with compatible three-quarter projection. Terrain must connect town approaches, roads, stone bridge, stream, ruins/mines and forest/elevation/biome transitions. Art needs its natural light/contact shadows; generic CSS panels do not create that finish. Formations need facing, depth, banners, full readable stack indicators and legal terrain registration. Gawain needs a class-correct mounted identity and directional walk/ride gait. Review Kingdom, Hero/Forge/Army and supporting screens against their own frame/material references before any gallery freeze; this targeted pass does not accept unmodified sections.

No automatic new image production is authorized by the rejection. Preserve reuse-first, exactly30 useful requests, one active globally and the billing-disabled/unknown-job state. No generation, dependency installation, game source or APK work occurred. Old game and raw art remain read-only sources.

## Verification / acceptance

`check-rotation-review.mjs` uses installed Playwright/Chrome. Seven targeted captures cover375x825 and825x375 for Adventure/Tactical/Kingdom plus portrait Defense. Tactical/Defense resource entries: zero. Asset/page errors, clipped count badges, scene buttons below48px and horizontal shell overflow at375/768/1280: none. Rotating after selecting the foot pose preserves that selection. These checks prove static review behavior only; no game state, physical phone, permissions, animation or finished visual acceptance is tested.

Latest owner status: **previous proposal REJECTED; new HUD/rotation corrections awaiting feedback; Adventure/Tactical scene fidelity still FAILS**. All full-product sections and explicit feedback-before-coding gate persist.
