# Asset acceptance clarification — 3 October 2026

Planner/verifier policy revision 1. This corrects review applicability and reporting; it does not approve a game, alter the current camera contract, purchase images, or overwrite historical decisions. Read with [the all-batch audit](ALL-BATCHES-ASSET-AUDIT-2026-10-03.md). Latest direct owner authority overrides historical no-code directions for the executing AI; this planner chat remains documentation/verification only.

## Count useful progress separately

Use these independent measures: submitted requests; locally collected originals; technically verified originals; source identities/content reviewed; recoverable candidates; extracted derivatives; artwork ready for a specified use; registered world assets; integrated runtime assets; owner-accepted sections. A request, candidate, sheet, diagnostic JPEG and integrated asset are different units. A derivative can be usable before runtime/owner review. A source can be valuable while its current derivative is defective.

Statuses are PASS, FAIL, UNVERIFIED and NOT_APPLICABLE. FAIL needs observed contrary evidence. UNVERIFIED includes missing evidence, missing review and unfinished integration. NOT_APPLICABLE needs an explicit role/use rationale. REJECTED_STALE_HASH is a rejected evidence binding, not evidence that the source artwork is visually bad. Unknown invoice values are null, never zero.

`runtimeApproved:false` and unreceived owner feedback mean UNVERIFIED. They must not make every artwork fail, or prevent reporting completed extraction/artwork work. Keep a separate `artworkReadyForUse` result and scope; never promote runtime or owner acceptance from it. Every PASS records source SHA, derivative SHA, policy revision, intended size/use and evidence. World-scene review also binds composite hash, constituent hashes, registration revision, camera and contract hashes. Changing any relevant input invalidates that review, not unrelated assets.

## Gates by use

| Use | Applicable evidence | Criteria that do not apply |
|---|---|---|
| Opaque terrain | Correct age/biome material; registered topology, routes/crossings, clearings and natural appearance; mutable/static layer map | Transparent-object alpha matte, character rig |
| UI resources, skills, gear, portrait cards | Identity/colour, intact silhouette, readable actual-pixel samples on intended backgrounds, applicable alpha | World footprint, world camera, feet pivot, actor animation |
| Buildings/sites/towers | Identity/era/function, intact object, local extraction, real base/entrance/contact data, camera/scale/depth/occlusion and registered scene | Actor gait unless it contains an independently animated actor |
| Walls/props/construction kits | Requested pieces separately counted/cropped, modular joins/contact data, correct world use | One fictitious rectangle enclosing an entire sheet |
| People/mounts/vehicles/creatures | Correct frozen identity and equipment, usable anatomy/parts, contact/pivot, intended camera/scale; articulated pose/motion evidence where gameplay requires it | Treating a full-body painting or static idle as an articulated animation |

Source content and derivative content are separate. RGB/magenta originals without alpha are valid source candidates, not final transparent assets. Mark fine matte UNVERIFIED until extraction/review. Do not buy a replacement merely because source alpha is absent, a guide mark remains, or a small local edit is needed.

## Matte and actual-size review

Keep lossless native edge crops on black, white and neutral ground to detect removed material, false holes, colour contamination and bad edges. Also inspect actual intended UI/world size. Record diagnostic severity rather than requiring the same native-pixel perfection for an 18px HUD symbol and a large exported illustration. Subject integrity is always required; large material holes cannot be excused by thumbnail legibility. Strong wrong-colour shading visible at 18px also remains a failure.

Current hash-bound scoped results: Food/Wood/Stone v2 are artwork PASS for 18px resource-symbol canvases in the 28px rail; Offense v2 is artwork PASS at the reviewed 36/64px UI sizes. These retain minor native fringe warnings and are not approved for unrestricted enlarged export. Offense at 18px, all-purpose native matte quality, world integration and owner acceptance are UNVERIFIED. Do not redo these four just to erase an imperceptible diagnostic pixel. If their use, size or background changes materially, inspect that new scope.

Gold v2 is FAIL: coin sides read red at intended size. Hall v2 is FAIL: severe roof/front loss, visible holes and ghost edges. Food/wood/stone fine-fringe history remains in the old report; the current scope policy and hashes explain the bounded re-evaluation. The four passes do not conceal those old warnings or mean eleven finished assets.

Masks must distinguish connected backdrop, intentional object holes, foreground interior, real fine structures and a narrow edge region. `distanceTransform(alpha <= 16)` gives zero on foreground, so `distance <= 2` applied to opaque material is not an interior-protection test. Require representative roof/wall/material patches to remain opaque, inspect newly introduced interior holes and compare before/after object integrity. Avoid a fixed whole-object opaque-area ratio as the sole test: legitimate plinth removal can change area. See the reproducible [mask diagnosis](../../qa/full-asset-verifier-20261003/mask-distance-diagnosis.json).

## Registration without impossible camera promises

Retain the current shared world geometry, camera, legal footprints and connected routes. Measure physical ground landmarks, entrances and feet/contact pivots, not roof tips or arbitrary silhouette extrema. Four physical corners are appropriate only for a visible planar quadrilateral; use a natural contact polygon or pivot for an irregular quarry, tree, figure or vehicle. Show which landmarks are visible and which are inferred, with confidence and residuals.

A single 2D affine warp cannot create hidden faces, fix incompatible perspective/depth, rotate a body into an unpainted view, or turn arbitrary outline tips into a parallelogram. Do not repeat a futile exact-camera proof based on those tips. Estimate compatible placement from valid contact data, use controlled layer/ground separation and depth ordering, and inspect the assembled scene. Where the source truly cannot fit, document a local reconstruction/re-render or a versioned camera/contract revision proposal with before/after scene evidence. This clarification does not silently change IMPLEMENTATION-CONTRACT.json or authorize regeneration. A reviewed proposal must resolve any contract conflict before a registration PASS.

Rotating a landscape display/resizing the viewport is not permission to fake free 3D camera orbit from one painting. Every world object, terrain, overlay, path and hit area must still share the selected camera/world transform. Flat facades, pasted ground blocks, clipping and inconsistent facing remain defects even if metadata residuals pass.

## Day one and terrain dressing

Day one requires one active Hall and seventeen empty selectable build sites, with mutable Walls0. It does not require an empty valley: MASTER-PLAN permits immutable scenery, and the approved appearance includes inhabited outskirts. Preserve age-correct huts, farms, logs and vegetation explicitly mapped as noninteractive dressing outside legal sites, routes, crossing approaches and selectable/collectible roles. Separate/remove baked active structures, workers, resources, guide grids/marks and mutable gates/walls. A hut/log is not automatically a violation; occupying a legal footprint, confusing a selectable role or blocking a route is.

Do not fill pads with uniform opaque polygons or smear a removed crossing into the river. Use natural soil/vegetation/road treatment while retaining exact legal geography. The day-one scene and later populated composition require separate proofs; the five-producer placement image is a diagnostic, not day one. Match scale, framing, upper-left light, grounding, landscape phone legibility and the approved composition in scoped actual viewport comparisons.

## Frozen roster and complete scope

Use the adopted names in GAME-DATA-REFERENCE/IMPLEMENTATION-CONTRACT, not a generic asset ID. The heavy roster is Bone Crusher, Charioteer, War Elephant, Siege Knight, Cannon Crew, Steam Walker, Battle Tank and Hover Tank. Human infantry cannot fill the chariot/elephant/walker/tank roles. Preserve those images as possible crew/reference, but leave the required identities open. Resolve ambiguous Siege Knight form and other weapon mismatches explicitly. Tower family requires the appropriate mechanism and action as well as an age-appropriate shell; baked auras/active beams need independent FX.

Do not reduce the full eight-age linked campaign, three gameplay modes, hero classes, six functional equipment slots, eight biomes, support screens or offline/native requirements to match purchased art. Eight generic infantry images do not complete an eight-age heavy roster. Sparse scaffolding and a passing document benchmark remain separate from implemented play, visual review and native acceptance.

## Review-tool repair instructions for the executor

Expand read-only collection discovery/review joins to all current batches; carry historical verdicts by exact (batch, ID, source SHA). Missing rows become UNVERIFIED, not stale. Accept justified NOT_APPLICABLE. Import derivative review only when the current source/output/evidence hashes match. Keep review data across benchmark reruns rather than initializing all visual fields afresh. Compute scoped artwork readiness separately from required integration/owner gates; prevent boolean false from becoming a visual FAIL.

The current six safety fixtures pass, but the real old visual-note file is still unbound to eleven v2 derivative hashes and the current scene. Preserve it as history and publish a current, correctly bound review version. Keep stale/missing/change/wrong-path/wrong-batch/scene fixtures; add meaningful coverage/applicability/integrity checks. Do not weaken rejection of genuinely stale evidence just to increase the pass count.
