> **Latest authority — 3 October 2026:** whole-game LANDSCAPE confirmed; original Vertex design mocks authorized, reuse optional for this scope. Read [the new plan](LANDSCAPE-ORIGINAL-MOCK-PLAN-2026-10-03.md). Older portrait/reuse/no-generation instructions are historical. Exactly30/single-active/unknown-job restrictions and feedback-before-coding persist. Thirty briefs are drafted; zero generated. Supplied project access awaits local account sign-in; remote operations remain UNKNOWN.

# Ages of Dominion — art reuse, review evidence and remaining work

Decision date: 2 October 2026. This is a source-art assessment and future implementation plan. No image-generation request was submitted for this handoff. No source art was deleted or replaced. The package contains documents, JSON inventories and JPG review/reference images only. The unused draft at C:/dev/ages-of-dominion-reborn-unused-draft-2026-10-02 is an archive, not the adopted implementation; C:/dev/ages-of-dominion-reborn is reserved for the future fresh game.

Read VISUAL-DESIGN.md for camera, composition, all nineteen supplied targets, independent layers and visual/interaction acceptance. MASTER-PLAN.md owns gameplay and fresh-code boundaries. Do not import an old runtime/art directory wholesale or treat old provenance acceptance labels as current visual approval.

## 1. What exists and what was actually reviewed

The owner already has a substantial generated-art library. Its original PNG attempts often retain more resolution and alternate compositions than the selected processed WebP. Start there before spending money on replacements.

| Evidence | Coverage | Meaning |
|---|---|---|
| raw-inventory.json | All 854 files recursively found in C:/dev/aod-art-src; 5,076,636,300 bytes | Path/group/file/byte inventory. Not a claim that every original was viewed or approved. |
| public-art-inventory.json | 961 raster files in C:/dev/ages-of-dominion/public/art; 102,769,936 bytes | Exact paths, dimensions, byte sizes, alpha-channel presence and SHA-256 for every processed file. Existence is not usability. |
| reviewed-art-ledger.json | 31 raw originals and 55 processed candidates explicitly inspected | Exact path, dimensions, SHA-256, review status and notes for these candidates. See row-specific limitations. |
| asset-manifest.json | 31 processed components selected for possible reuse | A compact candidate kit, not a finished accepted scene. The byte-identical copies remain in the archived unused draft only; final handoff has no WebP runtime package. |
| references/visual-targets/index.json | All 19 supplied JPEGs | Original source path, dimensions and SHA-256; unchanged copies are visual targets for review only. |
| review/*.jpg | Contact sheets for the inspected sets | Visual evidence and navigation aids, not full-resolution delivery assets. Individual originals remain authoritative for edge quality. |

Direct image and contact-sheet review covered every available raw panorama attempt across eight ages, all eight processed panoramas, representative raw terrain/title/citadel/wall/hero/item/unit/tower candidates, the full selected Stone building/prop/tower/static actor kit, and representative processed townhalls from every other age. All nineteen user references were reviewed together. The rest of the large raw and processed libraries remain inventoried but not visually accepted. A small contact sheet cannot prove animation completeness or perfect alpha at actual device size.

Status vocabulary is deliberate:

- **accepted-candidate:** suitable isolated component to test in a coherent assembled scene. This does not mean the final scene is approved or that animation is complete.
- **staged-reference:** useful material/composition evidence, often with baked state; cannot ship as a primary interactive world layer without substantial separation/rework.
- **staged-provisional / staged-material / staged-presentation / staged-kit-piece:** a limited purpose component requiring registration, processing or use-specific validation.
- **rejected-primary-world / rejected-adventure-world / rejected-small-hud:** unsuitable for that stated role. The original is retained; rejection is not deletion and need not forbid unrelated inspection/title use.
- **unreviewed:** file exists but no visual claim is made. Inventory-only files belong here regardless of previous approval tags.

## 2. Why the existing selected kingdom art fails

The main requested kingdom is a broad mature settlement beneath an elevated citadel, with a believable river valley, close wall ring, realistically rendered materials and small edge controls. The shipped selected Medieval panorama depicts a smaller ink-outlined town with too much vacant foreground. Reusing a more realistic individual house cannot fix that underlying composition/material mismatch. A huge resource panel then hides the citadel, further weakening the target.

The old provenance record C:/dev/ages-of-dominion/docs/training/provenance/pano-medieval.json selects attempt 10. Its acceptance verdict checked that most sites were open, no perimeter barrier surrounded the town, and no HUD/text/marks existed. Those are structural checks; the record did not establish reference-matched materials, city scale, elevated citadel or the requested walls. The absence of a wall was particularly misaligned with the mature mock. Treating that structural verdict as a finished visual pass led to a wrong selected file.

A static finished-city JPEG behind invisible hotspots has a different defect: it looks like a city, but it cannot honestly show new-game emptiness, construction, actual building upgrades, wall changes or the player's citadel level. Its geometry would remain painted regardless of campaign state. Preserve the target appearance by using registered independent layers. The primitive hall, mature citadel, district dressing and walls must actually respond to their corresponding state.

Saved evidence reviewed from the old project is historical evidence, not a new browser/hardware verification: docs/handoff/evidence-2026-10-02/kingdom-after-harvest.png shows the outlined landscape, dominating top UI and sprite mismatch; battle-deployed.png shows separated scene strips and a plain gray board; journey2-siege-424.png shows a diagram-like lane rather than terrain. Several saved files were mislabeled: hero-medieval-424.png contains Title, and journey2-hero-424.png contains Battle. The next AI must verify screen identity before declaring screenshot coverage.

## 3. Raw panorama comparison — all available attempts

All thirteen available raw panorama PNGs are 3072×5504. The paths below are relative to C:/dev/aod-art-src; their exact absolute paths and SHA-256 values are in reviewed-art-ledger.json. No older missing attempt is assumed available.

| Raw source | Decision for primary kingdom | Observed usability and problem |
|---|---|---|
| pano-stone/attempt-1.png | Reference only | Larger sparse primitive village and several lawn sites are closer in scale than the selected tiny town. Many buildings/hall remain baked; cannot represent a genuinely empty start. |
| pano-stone/attempt-2.png | Reject | Small flat outlined town; wrong finish and too much empty terrain. |
| pano-stone/attempt-3.png | Reference only | More realistic material, but warm golden developed village, small city and excess foreground. |
| pano-bronze/attempt-1.png | Reference only | Broad populated city ring closer to the mature composition, with softer semi-realistic finish. All city state remains baked. |
| pano-bronze/attempt-2.png | Reference only | Stronger realistic materials and different closer camera, broad lawns; developed baked town. |
| pano-iron/attempt-2.png | Reject | Flat illustrated small-town composition and oversized meadow. |
| pano-medieval/attempt-8.png | Reject | Small flat colored town, wrong density and finish. |
| pano-medieval/attempt-9.png | Reference only | Better roof/terrain material and extra foreground houses than attempt 10; castle and town remain baked and geography does not satisfy empty-start layering. |
| pano-medieval/attempt-10.png | Reject | Selected processed source; visibly ink-outlined trees, houses and fields despite structural approval. |
| pano-gunpowder/attempt-2.png | Reject | Same small outlined town structure; extra period elements do not fix camera/materials. |
| pano-industrial/attempt-2.png | Reject | Industrial additions over a small flat outlined town. |
| pano-modern/attempt-2.png | Reject | Inconsistent modern additions amid the older miniature town; weak city identity. |
| pano-future/attempt-2.png | Reference only | More pronounced futuristic forms, but flat planes and changed circular footprint. Not an approved continuity solution. |

Only Medieval attempts 8, 9 and 10 are present in this raw folder. Older provenance references to attempts 1–7 are not evidence that those files are transferable now. The public panorama files are 1440×3200 processed derivatives; scaling them up does not restore lost detail or remove baked structures. No accepted clean, building-free, reference-registered Day 1 terrain base was found among these inspected panorama candidates. That is narrower than declaring the entire raw corpus unusable.

Review sheets: raw-pano-1.jpg and raw-pano-2.jpg show the Stone/Medieval alternatives; raw-other-ages-1.jpg and raw-other-ages-2.jpg show the other age panoramas. Do not select the latest numbered file merely because it was the last attempt.

## 4. Other raw originals worth reusing or considering

Dimensions and SHA-256 are stored with exact paths in reviewed-art-ledger.json. The examples below intentionally include both stronger raw alternatives and rejected wrong-subject images.

| Source under C:/dev/aod-art-src | Dimensions | Use decision |
|---|---|---|
| bld-townhall-stone/attempt-2.png | 2048×2048 | Plausible primitive timber/thatch hall cluster on key matte. Reprocess edges if needed; a viable independently changing starter central building. |
| bld-townhall-medieval/attempt-2.png | 2048×2048 | Believable cottage/hall, useful secondary building; cannot supply the large elevated castle silhouette. |
| bld-walls-medieval/attempt-1.png | 2048×2048 | Stone two-turret gate and short segment. Useful kit piece, insufficient perimeter by itself. |
| tower-arrow-medieval/attempt-1.png | 2048×2048 | High-camera stone arrow tower. Register to terrain/light/pad scale before acceptance. |
| item-weapon-medieval/attempt-2.png | 2048×2048 | Realistic inventory longsword. Reuse after matte and blade-edge validation, with real item data. |
| hero-knight-medieval/attempt-2.png | 1536×2752 | Full armored character and dark hall, suitable frontal inspection/hero presentation. Not an aerial map actor. |
| unit-melee-medieval/attempt-14.png | 2048×2048 | Realistic static frontal fighter on magenta matte. Candidate for roster/inspection or temporary static combat representation; not proven matching world camera or animated rig. |
| battle-back-plains/attempt-1.png | 5056×3392 | Realistic meadow/river valley with ruined tower at left; lower camera. Provisional battlefield backdrop or material reference, not kingdom base. |
| battle-ground-plains/attempt-1.png | 6336×2688 | Realistic grassy foreground with far river/castle; tactical environment candidate after coherent projection and subject placement. |
| battle-ground-hills/attempt-2.png | 6336×2688 | Realistic open grass/hills/sky with no castle, promising tactical terrain candidate. Not a portrait valley city substrate. |
| battle-back-hills/attempt-2.png | 5056×3392 | Cartoon pasture/rocks/fences; reject for realistic main world finish. |
| title-ridge/attempt-1.png, attempt-2.png, attempt-3.png | 2528×1696 each | Cinematic far landscape layers with keyed margins; attempt 2 has particularly useful realistic ridges/light. Title-only camera/composition, not main kingdom geography. |
| title-fore/attempt-1.png, attempt-2.png, attempt-3.png | 2528×1696 each | Close frontal forest cutouts; title foreground candidates. Cannot stand in for high-aerial trees. |
| region-hills/attempt-3.png | 1536×2752 | A framed parchment town picture despite its region filename. Wrong subject for the inhabited Adventure landscape. |

Raw melee Medieval attempts 9–13, Stone townhall attempt 1, remaining biome originals, FX and other scaffold attempts were inventoried but not visually passed. Their presence is a next review opportunity, not proof that animation, a full matching world kit or missing mode scenery already exists. Inspect them by role before requesting new art.

## 5. Compact processed candidate kit

The 31 selected processed components total 5,791,586 bytes. Their source is C:/dev/ages-of-dominion/public/art, with full per-file dimensions, SHA-256 and alpha data in asset-manifest.json. These are components for a first assembled proof; there is deliberately no panorama in the shortlist.

| Files | Dimensions and alpha | Suitable role / limitation |
|---|---|---|
| bld-townhall-stone.webp, bld-farm-stone.webp, bld-lumber-stone.webp, bld-quarry-stone.webp, bld-mine-stone.webp, bld-barracks-stone.webp, bld-workshop-stone.webp, bld-hall-stone.webp, bld-armory-stone.webp, bld-walls-stone.webp | 1024×1024, alpha | Realistic timber/thatch/stone independent structures for existing functional type IDs. Minor blue/magenta fringes need inspection/cleanup. Walls is one gate piece, not a complete ring. |
| prop-tree-stone.webp, prop-bush-stone.webp, prop-rock-stone.webp | 512×512, alpha | Natural foreground/district objects with separate anchors; limit repeated identical silhouettes. |
| tower-arrow-stone.webp, tower-splash-stone.webp, tower-slow-stone.webp, tower-support-stone.webp | 1024×1024, alpha | Existing four-function Stone tower kit; test silhouette/camera/materials in authored defense scene, preserve real tuned functions. |
| unit-melee-stone.webp, unit-ranged-stone.webp, unit-heavy-stone.webp | 768×768, alpha | Static unit/roster representation. Their more frontal angle needs world-camera validation and honest temporary labeling. |
| enemy-bandit-stone.webp, enemy-wolf-stone.webp | 768×768, alpha | Static enemy candidates, same angle/animation limitations. |
| hero-knight-ancient.webp | 1080×1920, opaque | High-quality hero inspection illustration; armor reads Bronze/Roman more than primitive Stone. Stage accordingly or treat as explicitly temporary. |
| ground-grass-medieval.webp, ground-road-stone.webp, ground-rock-medieval.webp | 512×512, opaque | Natural material patches only. Project/blend to landform; never assemble obvious checkerboard cells as the final environment. |
| sky-stone.webp | 2048×768, opaque | Far blue sky/ridge component, requiring horizon/camera registration. |
| battle-back-plains.webp | 1536×1024, opaque | Provisional tactical backdrop; lower camera and left ruin constrain integration. Prefer raw when higher detail is useful. |
| ui-medallion-rim.webp | 256×256, alpha | Reusable metal rim. Add readable distinct icons; dark miniature imagery is not automatically usable navigation. |
| ui-plate-frame.webp | 512×512, alpha | Restrained border candidate; use correct slicing and material surface, do not distort a square into a wide ribbon. |
| ui-button-brass.webp | 256×128, opaque | Material/button component with real text rendered separately; check contrast and target states. |

The other-age processed townhalls were inspected: Bronze plaster/terracotta cottage, Iron courtyard house, Gunpowder brick/slate hall, Industrial brick/glass hall, Modern glass office and Future blue glass structure. They show reusable material quality; an office/hall is not automatically the required imposing central citadel. Confirm the intended architectural role, common camera, base scale, shadow and age progression before transfer. Inventory matching @realm derivatives separately; they were not all reviewed and must not replace the inspected original silently.

Other observed limitations: ground-water-medieval.webp looks like pebbles/paint rather than a convincing river; ground-water-stone.webp is muted green-gray water needing geometry/reflection integration; ground-field-medieval.webp is an explicit divided agricultural pattern and is not a map base. ground-field-stone.webp is a plausible ochre furrow texture for a localized farm patch. The large brown ui-sheet-frame.webp conflicts with the required world-dominant HUD. Stone resource icons are ornate but visually ambiguous at phone scale. scaffold-stone.webp has actual alpha but visibly rough/blocky matte edges; reprocess or reject after target-size inspection rather than assuming a gray display means no alpha exists.

Review sheets candidate-1.jpg, candidate-2.jpg, candidate-3.jpg and cross-age-and-raw-categories.jpg provide visual context. The processed candidate files were not adopted by the final plan package.

## 6. Raw-to-processed transfer rules

The next AI should create a small explicit transfer list only after choosing a component for a role. For each transfer record: logical asset ID; original source/attempt; source SHA-256 and dimensions; processing operations; resulting file path/hash/dimensions; camera/light contract; ground anchor; alpha/mask quality; draw layer; gameplay state represented; status and comparison evidence. Existing asset-manifest.json and reviewed-art-ledger.json are the seed, not a universal pass.

Retain original PNGs outside the runtime. Prefer a suitable higher-resolution raw original when a processed derivative has key fringes, loss of detail or different crop. Do not overwrite good originals or reuse a processed filename with different hidden content. Compare the processed image against raw with identical framing, then against the assembled scene at actual display size. Hash identity proves copying, not artistic quality.

Key-matte cleanup is a processing step: remove the uniform matte, handle hair/cloth/roof edges, recover soft shadow deliberately, defringe colored borders, and inspect on both light grass and dark stone. Preserve architectural texture rather than erasing it with aggressive thresholding. Alpha-channel existence is not proof of clean transparency; premultiplication and edge dilation must agree with renderer sampling. Raw outputs are often opaque keyed PNGs, not promised native transparent sprites.

Every world component needs a ground footpoint and physical reference scale, not placement by its file's center. Independent contact shadows, ambient occlusion and small material color correction can unify a kit; they cannot repair a fundamentally frontal camera or ink-outlined illustration. Avoid mirrored directional shadows. Decorative district buildings never receive fake construction controls. A blade/hero inspection asset may use frontal framing without becoming a top-down world actor.

Do not assemble a perimeter by rotating one perspective gate PNG arbitrarily. Use matching back/front/side wall sections, corners and gate variants, or a properly projected modular geometry/material approach. Keep gate level/material visually connected to the actual wall state.

Keep working outputs, candidates and rejected attempts separate from adopted runtime assets. Runtime should receive only explicit approved scene components at necessary resolution/compression. Old generation prompts, geometric control sketches and structural-only acceptance files are research evidence, not automatic instructions for the fresh project.

## 7. Proven gaps, review opportunities and priority

| Priority / role | Evidence-backed state | Next action and replacement criterion |
|---|---|---|
| P0: registered kingdom landform | None of thirteen reviewed raw panoramas is a clean state-aware Day 1 base matching reference 15/03. | First examine any remaining relevant terrain originals. Salvage/rework useful terrain if practicable; otherwise optional narrowly scoped new cleared layer. Reject miniature town, baked housing, wrong river/camera or vast empty foreground. |
| P0: rocky citadel terrace and mature castle identity | Stone hall exists; reviewed Medieval townhall is cottage; panoramas bake castle. No accepted independent matching terrace/castle combination established. | Separate terrain terrace and actual townhall/citadel visual. Reuse suitable inspected component; audit other originals before replacing. It must register to starter/mature geography and respond to real age/level. |
| P0: coherent wall perimeter | Reviewed Stone/Medieval wall assets are short gate pieces. Complete matching front/back/corner/side kit was not demonstrated. | Audit wall originals/geometry options, prove one registered ring and upgrade before requesting a broad age set. Reject impossible rotated perspectives and painted unchanging walls. |
| P0: HUD readability | Rim/frame material usable; several ornate resource images muddy/ambiguous. | Test real readable symbols in compact edge targets. Replace only failing icons, not entire UI art set. No browser-dashboard resource card grid. |
| P1: Stone structures and props | Reusable existing kit with fringe/camera limitations. | Process/scale/register and compare one assembled starter; no justification for regenerating every building first. |
| P1: dense mature dressing | Mature target has many apparent structures; a few standalone sprites cannot express it. | Add independent decorative districts tied to development using existing architecture where fitting. Need matching scale/material masks; no fake functional houses. |
| P1: real Adventure landscape | Reviewed region-hills original is wrong subject; other biome/region files exist but were not passed. | Audit remaining region/terrain originals before spending. Prove one coherent road/bridge/fog/site landscape and actual travel rather than selecting one unrelated backdrop per node. |
| P1: tactical terrain and actors | Two stronger raw terrain candidates; static unit art exists but aerial camera/rig completeness unproven. | Assemble one coherent battlefield and inspect projected cells/grounding. Audit actor parts/frames, state actual animation coverage honestly. |
| P1: defense lane | Tower/actor kit exists; no accepted authored winding base/pad registration was established in inspected candidates. | Audit other terrain; author lane/pad coordinates and prove range/hit alignment before replacing terrain. No baked towers/enemies. |
| P2: hero/forge/army | Good frontal hero/item art exists, but full six-slot item coverage not audited. | Reuse inspected artwork and review remaining gear. Implement six real slots/data first; generate only proven missing item roles after catalog review. |
| P2: all-age polish, animation/FX | Extensive library exists; neither full coherent eight-age kit nor all requested animation proven. | Inventory by scene role and age, inspect and assemble sequentially. Do not count unused files or malformed attempts as completed animations. |

Missing accepted evidence is not equivalent to a missing file. Unreviewed categories should be inspected before a replacement request is approved. A first visual proof needs only the selected functional structures for seventeen real pads and hall, a coherent landform/terrace/perimeter and usable edge HUD; it does not require all eight ages and all modes' art to be generated first. Start Stone and a developed Medieval calibration fixture; expand after the assembled comparison passes.

## 8. Future Vertex batch policy — exactly thirty, one at a time

No new image jobs are submitted by this design review. Follow root DECISIONS.md and the environment status document for the current lock and owner policy: future authorized image work uses exactly 30 useful numbered images per batch, one active batch at a time, and no progressive/incremental generation. Do not submit a separate two-image calibration batch, silently run online replacements, or start the next batch before the prior job is terminal and its outputs are recorded/reviewed. The previously described two-image experiment is superseded.

Use stable model gemini-3.1-flash-image. Its model page confirms batch support; current batch documentation limits image output to 1K, even though other request contexts offer higher sizes. Retain the user's batch workflow and keep generation outside the offline game. [Google model documentation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-flash-image), [Google batch documentation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/batch-prediction-gemini).

A useful proposed first set of exactly 30 outputs, subject to the remaining original-art audit and approved storyboard, is below. These are planned roles, not submitted request JSONL. The terrace/terrain pair is two members of this full batch, not a separate job. Freeze one camera/light contract and condition every matching world component on the same approved owner references. A batch cannot guarantee component registration; inspect the whole returned set, record rejects, and do not use progressive requests to conceal failure.

| Number | Useful image role |
|---|---|
| 01 | Cleared Day1 valley/river/city landform, portrait, no UI/buildings, preserving seventeen pad positions and hall site |
| 02 | Independent rocky citadel terrace/stairs/ramp, empty top, matching landform camera/light |
| 03 | Independent Stone central hall variant fitted to terrace |
| 04 | Independent Medieval central citadel fitted to the same site |
| 05 | Stone wall rear sections |
| 06 | Stone wall front sections |
| 07 | Stone wall side/corner sections |
| 08 | Stone gate variants |
| 09 | Medieval wall rear sections |
| 10 | Medieval wall front sections |
| 11 | Medieval wall side/corner sections |
| 12 | Medieval gate variants |
| 13 | Stone decorative housing district cluster, no interactive labels |
| 14 | Medieval decorative housing district cluster, matching city scale |
| 15 | Stone garden/production district dressing |
| 16 | Medieval market/civic district dressing |
| 17 | Aerial adventure meadow/forest/river terrain region, no actors/UI/sites baked |
| 18 | Adventure bridge/path crossing component matched to region |
| 19 | Adventure mine/ruin/guarded-site cluster components matched to region |
| 20 | Adventure hero aerial actor, matching selected class/camera |
| 21 | Coherent tactical terrain at approved board projection, no grid/UI/actors baked |
| 22 | Tactical melee actor at approved projection |
| 23 | Tactical ranged actor at approved projection |
| 24 | Tactical heavy actor at approved projection |
| 25 | Tactical bandit enemy at approved projection |
| 26 | Authored defense winding approach terrain, no towers/enemies/UI baked |
| 27 | Defense empty pad/ground foundation component |
| 28 | Missing Shield inspection item, matching six-slot presentation |
| 29 | Missing Ring inspection item, matching six-slot presentation |
| 30 | Class-distinct hero inspection illustration to replace the most misleading existing armored reskin |

Reuse suitable existing components first. If review proves a listed role already satisfactory, replace that numbered request with another documented genuine gap before submitting, keeping exactly 30 useful outputs; do not duplicate good artwork merely to fill count. Refer to the environment document for billing and job status. UNKNOWN active-job status is a fail-closed submission lock; disabled billing is a real environment blocker to future jobs. Neither blocks offline preview review. Raw key-matte outputs need separate processing and alpha inspection; native transparent generation is not promised. Owner feedback and plan correction precede implementation and any generation submission.

## 9. Implementation acceptance and transfer

The future AI should preserve the raw source library and old project, create fresh game code at the reserved target, and transfer only chosen art through an explicit manifest. Build one state-aware scene first. Show raw candidate, processed component, assembled starter and developed Medieval view side by side; record the actual viewport/save/action. The target is the exact composition/material/HUD intent of the supplied mocks, with real readable data and real actions.

Art readiness is partial: strong isolated buildings, material patches, towers, character/item inspection and static units can be reused now; clean matching landscape, terrace/citadel/perimeter registration and fully coherent animated mode scenery remain unproven. This assessment does not establish a completed game or visual acceptance. The documents specify how another AI can reach that acceptance without wasting the existing art investment.


## Latest scoped revision — 3 October 2026

Review `design-preview/review-reference-direction.html` for Resources, Adventure and Tactical. The AVIF was browser-decoded and visually inspected. Phone resources now show grain/provisions, logs, rock and coins at32px height above names/amounts. Existing aerial forest/river/road and ruins/stone-bridge art replaces the empty-grass studies; settlements/sites/guards/treasure and six count/health-bearing formations are added as static scale studies. Precise reuse and remaining gaps: `docs/plan/REFERENCE-DIRECTION-2026-10-03.md`.

Nine scoped literal captures at375x825/424x933/820x462 and shell checks at375/768/1280 passed asset/JS, resource/count bounds and48px scene button checks; final selected pixels were reviewed. Resource text contrast is approximately9.0:1/7.1:1. The375px gallery shell contains a341px scene. This is neither a full30-view audit nor physical-device/visual acceptance.

Still missing: clean transparent resource objects, larger fortified/biome-rich Adventure region with stone bridge, matching aerial site/actor camera, class-correct mounted Gawain and directional gait, high-detail Tactical terrain registered to legal7x10 cells. Some provisional cells/poses overlap painted obstacles. Current previews improve density but still fall short of the new target. Every section remains pending/revision-needed. Old game/raw art preserved read-only; no game source, installs/builds/APKs, image jobs or billing changes. Single-agent work only.



## Latest owner correction — 3 October 2026

Owner REJECTED the latest assembly as still far from the beautiful real-game-looking mocks. Resource icons were too big; no resources are wanted in battles. Phones may rotate to provide Adventure/Tactical more space. Latest comparison: `design-preview/review-mock-comparison.html`; all26 supplied files: `design-preview/all-owner-mocks.html`; detailed updated contract: `docs/plan/ROTATION-AND-MOCK-COMPARISON-2026-10-03.md`.

Actual corrections:18px symbols in28px corner rail; no resource HUD in Tactical/Defense; auto portrait/landscape resize and edge-to-edge static review via `index.html?stage=1#adventure` / `#tactical`; smaller contextual controls; sharper unchanged raw Tactical ruins source. Seven scoped captures pass technical checks. These do not establish game-like finish: Adventure source/detail and both modes' camera, grounding, scale, facing and authored composition remain visual failures. Prior resource32px/rail72px and portrait-restriction claims are superseded. Owner acceptance/coding gate remains unresolved. No image job, game source, dependencies or APK work; single-agent only; old game/raw art preserved.

