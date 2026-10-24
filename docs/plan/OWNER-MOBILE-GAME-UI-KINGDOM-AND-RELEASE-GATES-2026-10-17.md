# Binding mobile-game presentation, Kingdom and release correction — 17 October 2026

**Status: owner direction recorded; architecture/QA instructions strengthened; implementation remains INCOMPLETE.** This is the latest presentation and work-sequence correction. It is embedded in the [ONE current complete repair file](ONE-COMPLETE-REPAIR-AFTER-VERIFICATION-2026-10-17.txt). Give that file to the implementation AI; this document is its specification, not another competing executor prompt. The full original contract remains embedded unchanged after the current corrections.

## Owner direction and interpretation

The owner again observes large text buttons, captions under controls, unnecessary resource-name text, blurred Kingdom sites and a wall that does not belong to the scene. The intended product is a mobile strategy game with logically correct state and coherent finished imagery. The owner asks whether the Kingdom ground and wall can be generated together, asks for visual/functional completion before APK/mobile review, and assigns this AI architecture, verification, advisory and senior-QA responsibility.

The architect's decisions below implement that request: a compact icon-led game HUD; sharp source-bound Kingdom scene families with integrated wall states and truthful dynamic buildings; and a full desktop game completion/review gate before packaging and later mobile QA. This supersedes conflicting earlier label-heavy layout recipes and the older sequence requiring an APK before independent desktop content review. It adds no intermediate owner-preview approval gate. Final package identity is still independently checked after building, and device/owner acceptance remain later separate stages. No engine rewrite, mechanics change or spending increase is implied.

The owner's “30 to 40%” is an assessment of the current result, not an independently measured progress metric. Do not replace it with a completion percentage derived from tests, catalogs or leaf counts. Show which actual game experiences and required evidence are complete or incomplete.

## U01 — Resource HUD: icon plus amount

**Default:** four familiar local resource symbols with concise numeric amounts; no visible `food`, `wood`, `stone`, `gold` words beside the symbols. Keep the actual names and full values in accessible names and a reachable detail view. Amounts, prices, income and exact source mechanics remain unchanged. Do not remove useful numbers to make the HUD look cleaner.

Concrete repair targets: `src/client/main.js:resources()`, `src/client/resource-bar.js:resourceChipLabel/resourceAmountText/resourceBarLayout`, and `src/client/game.css:#resources`.

1. Use current reviewed resource PNGs from `reviewed-source-selection.json:delivery`. Keep the established bounded 18px symbol / 28px rail treatment, correct aspect and alpha. No emoji or text-name fallback is a finished accepted resource icon.
2. Remove the visible `res-name` node from the default chip. Keep e.g. `aria-label="Food 250"`; the decorative image has empty alt. Apply visual styles to one outer chip (`#resources > .resource-chip` or equivalent), not every nested span. Current `#resources span` styles also match nested names/amounts and create unnecessary little boxes. Inner amount copy has no separate button border/background/padding.
3. Keep compact values and an exact-value detail/accessible name. Verify zero, ordinary values, fractional stored production, large supported legal balances, affordability and reload. Display formatting must not modify stored arithmetic. Avoid misleading rounded-unit boundaries where a compact label implies a materially different balance; exact value remains reachable.
4. These are information chips. Do not give four tightly packed chips overlapping invisible 48px hit regions. Provide a separate 48×48 resource-details action or a genuinely owned, disjoint accessible interaction if individual chips open details. The detail sheet shows names, exact balances and actual production/caps, with a clear close/return.
5. No resource rail in Tactical/Defense/result contexts where the original contract excludes it. Save/error feedback must remain truthful under the asynchronous storage repair.

**Evidence:** actual default PNG shows four symbols and amounts with zero resource-name words; accessibility tree retains each name/full value; details are reachable by touch/keyboard; layout/insets and state arithmetic pass. Hiding text with clipped overflow is not this repair.

## U02 — Real game control components and asset binding

Keep semantic buttons and accessible controls internally. Replace their visual construction with intentional game components, independently authored within the current offline renderer. Do not make a new runtime/engine migration a prerequisite.

Suggested new names below are **PLANNED_NEW**, not assertions that they exist: `game-control.js`, `game-icons.json`, `GameIconButton`, `ResourceChip`, `EquipmentSocket`, `AbilityTile`, `PortraitChoice`, `ContextAction`, `InspectorSheet`.

Every icon control has: stable action ID; real command/navigation consumer; current local icon path/hash/role; accessible name; owned hit rectangle; pressed/selected/focused/disabled/unavailable state; a reversible concise explanation; and entry/return context. Preserve the existing command and input-ownership protections. Do not merely set `font-size:0`, hide text on a wide old rectangle, or replace a word with an arbitrary emoji.

Suggested component input: `GameIconButton({actionId, icon, accessibleName, selected, disabledReason, onActivate})`. Its visual child is the reviewed glyph; its semantic name is not a permanent visible caption. Preserve exactly one command per deliberate activation, stable focus through rerender and modal background rejection. If an unavailable action must explain its reason on focus, use a genuinely focusable explained unavailable state with activation rejected; a native disabled button plus hover-only title does not satisfy touch/keyboard explanation. Bind the reason to real core preconditions and keep core legality checks.

| Action | Distinct game symbol | Accessible meaning |
|---|---|---|
| Kingdom | Civic settlement/citadel silhouette | Kingdom; current/available state |
| Adventure | Compass/route symbol | Adventure and retained journey context |
| Hero | Current coherent hero portrait | Hero and selected class, without changing it |
| Army | Formation/banner group | Army and owned roster |
| War | War standard with crossed arms | War options; distinguish from single-stack Melee |
| Menu | Coherent overflow/menu emblem | Open menu; expanded state and close/return |
| Save/status | Journal/archive/check or pending/error state | Exact pending/saved/failed snapshot status; no false acknowledgement |

These are semantic design directions, not claims that finished icons already exist. Use the same bound source family in the actual HUD and selected-context teaching. Settings retains its own recognizable symbol within the secondary sheet. Do not call a button a different action just to reuse a superficially similar image.

Reuse suitable reviewed local imagery. Nine skill PNGs and eight spell PNGs already have rows in `src/data/consumer-catalog-20261007.json`; equipment is in `gear-icons-20261007.json`; resource art is in the reviewed source selection. Inspect actual pixels before binding. The current reviewed `delivery` object does not contain a complete navigation set: do not invent filenames or claim a lookup means an icon exists. Review existing local production/UI inventory; create a small coherent source-supported icon family only where needed, using the existing art/budget authority. Every needed glyph must be legible at its real intended size and match M30's material language.

Long press/focus may reveal a name or explanation without executing the action. Essential operations cannot depend on hover or long press alone. First-use tutorial/selected-item context teaches ambiguous symbols. Screen-reader and keyboard access remain complete; icon-led does not mean unexplained or inaccessible.

## U03 — Compact navigation with adequate touch targets

No permanent label below or inside each primary navigation icon in the ordinary roaming HUD. Use one coherent icon family and a clear active indicator. Preserve 48×48 CSS px owned targets, with separated hit regions and visible focus; the glyph can be about 24–28px. Touch accessibility does not require a large text tile.

Starting implementation decision: at most five primary roaming medallions for Kingdom, Adventure, Hero, Army and War. Put secondary destinations and save/recovery/settings/help in a real icon-menu sheet. A separate Save action/status may remain where justified, as a compact icon with truthful pending/committed/error feedback. The existing top Menu and bottom More must not expose duplicate permanent navigation slabs. Active Tactical/Defense sessions still have a clearly reachable resume action without silently abandoning them.

At 48px targets with 8px gaps, five buttons occupy 272px before optional outer padding; this is a starting layout, not a claimed measured fit. Reflow against the actual usable rectangle and safe insets. Keep HUD clusters close to screen edges while preserving scene landmarks and ≥80% meaningful closed-inspector Kingdom world. Do not shrink all text or the entire game to fit.

`main.js:render()` currently creates navigation with text from screen names and adds extra visible destinations when an inventory/session exists. Replace that visual path with a stable action/icon model and measured overflow behavior. Preserve actual destination and session rules. Do not let one new bag item unexpectedly add a new permanent wide button and destroy the phone composition.

## U04 — Screen-specific game presentation, not one button-list template

| Context | Required default composition | Text/action treatment |
|---|---|---|
| Home/class choice | M01 panoramic world and restrained menu; class choice uses actual coherent portraits | Short menu labels are appropriate here. No eight giant class-name rectangles beside the equipment screen. |
| Kingdom | Dominant sharp terrain, real Hall/buildings/sites/workers and material boundary when owned | Direct site/building selection; concise selected-object inspector; one contextual Build/Upgrade action with icon costs. No permanent list of every plot/building. |
| Adventure | Readable continuous world, grounded actor/site identity and committed travel | Select destination/site, preview route/cost, confirm/cancel; names/details appear for selection. No permanent explanatory paragraphs over travel. |
| Tactical | Grounded formations, initiative and selected actor/target | Move/Melee/Shoot/Defend/Wait/Spell use recognizable action icons; selection exposes concise details and legal/illegal reasons. Retreat still has a readable explicit confirmation. |
| Defense | Lane, threats, towers, hero/army and selected range dominate | Compact pause/speed/wave/ability icons; real counts/core/wave values remain visible. Inspection owns its input and cannot hide critical threats. |
| Hero | M19 material chamber, dominant complete figure and three bounded sockets per side | Slot/gear icon and rarity/state frame by default. Full slot/item name, stats, compare/equip/unequip in selected detail. No long `Weapon: … · Crude` text buttons framing the whole body. Worn appearance uses real body layers, never socket icons pasted onto anatomy. |
| Skills/spells | Actual square skill sigils and spell glyphs, with ranks/mana/eligibility badges | Selected node shows source-backed effects/offer/point/target details; no generic full-width list. Do not invent purchasable skill ranks or prerequisites. |
| Forge/inventory | M22 workshop/bench/hearth/selected object, and purposeful bag/equipment grid | Recipe/quality/cost comparison is contextual. Essential craft/equip confirmations remain concise. Large item art needs its own supported source detail, not a stretched bounded inventory icon. |
| Army | Roster/creature art, count/rank, selected stack and actual capacity | Recruit/reinforce details are contextual; retained entity IDs and roles remain correct across modes. |
| Story/quests | Journal/encounter materials, meaningful rival/chapter imagery and real progress | Narrative and choices are legitimate readable text. Avoid identical empty web cards and repeated implementation commentary. |
| Settings/help/recovery | Focused game-context sheet with deliberate return and focus | Names, explanations, error/recovery outcomes and confirmations remain readable. Do not remove necessary safety information for a purely icon-only appearance. |

All 30 M recipes and their required unmocked contexts remain binding. Purpose-specific design does not authorize removing features or replacing gameplay with painted UI.

## U05 — Separate player-facing product copy from implementation commentary

Audit `main.js:mountHeroChrome/heroKitCaption/paintForge/support screens/say` and related modules. Move source filenames/hashes, static-pose disclaimers, “kit unverified,” “no Enhance/Reforge/Socket,” source/runtime-policy explanations and acceptance/provenance labels into QA/diagnostic output. They are not permanent product copy. A broken art consumer stays a failed requirement; deleting its disclaimer alone cannot repair it or justify claiming it works.

Keep real gameplay quantities, meaningful names when selected, costs/prerequisites, tooltips/tutorial, narrative, combat feedback and truthful save/errors/recovery. Help/privacy contains relevant local/offline information; do not repeat it on ordinary screens. Define default/selected/detail/error copy for each component and inspect actual pixels. Accessible names and focus feedback must remain present when decorative visible captions are removed.

## U06 — One registered Kingdom scene family per age, including the wall

**Chosen repair route:** design the terrain and physical wall as one coherent Kingdom composition. Generate or conditionally edit the needed integrated wall/ground imagery together when existing usable sources cannot supply it within the authorized route. The wall must belong to the source scene's camera, light, materials, scale and ground. A line of procedural fence/slab stamps baked into a PNG still fails this decision.

Use one source-bound family per age, with matched `no-wall`, `scaffold`, `built-1` and `built-taller` states, plus exact same-source foreground occlusion where needed. Do not independently generate 32 unrelated pictures; they will not automatically register. Review existing useful sources first. Produce one correct family/master in the first needed age before deriving its dependent variants or scaling the failed method to other ages; then complete every remaining age without an owner-preview permission loop.

State contract:

- Walls level 0, no job: no finished material perimeter anywhere in the owned wall region.
- Active wall job: that age's actual scaffold/foundation at the registered boundary; no prematurely completed wall. During an upgrade, use the contract's job-state staging, without implying an already completed new height.
- Completed level 1: coherent integrated material wall/gate and true ground contact.
- Completed level 2 and higher: supported taller version of the same era family; existing game rules/costs/+180 gate/core HP per level stay unchanged. Do not invent extra wall levels, ownership, towers or damage mechanics from the picture.

Hall and all player buildings remain truthful independently rendered state-driven layers. All 17 owned sites start empty. Existing/new ground artwork must not bake those facilities, a second Hall or a completed owned city behind transparent hotspots. Nonfunctional ambient dressing cannot impersonate unowned facilities. Natural site clearings need texture/path context, not broad blur, parking rectangles, diagram outlines or one obvious cloned soil stamp repeated 17 times.

## U07 — Replace the blur rather than blur the plots again

Fresh native inspection shows the soft blotches in the displayed `kingdom-stone-ground.png` itself; they are not merely a phone-resolution symptom. The current catalog explicitly describes blending away baked empty-plot rectangles. Exact provenance for every latest blend operation is not established by that description. Historical preparation scripts contain blur/patch operations; do not falsely attribute an exact current recipe without its input/output binding.

Concrete executor procedure:

1. Resolve each actual `kingdomPainting()` phase path and catalog/source lineage; hash original, current derivative and actual displayed pixels. Preserve originals and rejected evidence.
2. Start from a suitable sharp source/master. Trace actual unwanted painted guides/facilities and their protected neighbours. A soft alpha boundary may blend an edge; it must not erase surface texture over the whole playable area.
3. Reconstruct only affected ground using real compatible texture/perspective or a necessary supported conditioned image edit, preserving paths, banks, bridge approaches and lighting. Stop reusing the broad blend method that creates the current haze. No broad blur, flat fill or smudged patch is an acceptable “natural clearing.”
4. Inspect native crops and intended phone output together with adjacent untouched ground: soil/grain/grass/stone scale, sharpness, contact shadows and repeated seams must agree. A Laplacian/edge number alone cannot pass natural texture; oversharpening/noise does not recreate missing content.
5. Overlay real Hall/buildings/scaffold and all current selectors, then inspect sparse, construction and mature fixture states. Do not approve an empty source that becomes incoherent when actual building height/footprints are drawn.
6. If missing source pixels require generation, use U08's constrained registered family and existing affordability controls. Reject an output with new moved paths or smeared “cleaned” pads before creating dependent wall states/crops.

## U08 — Exact source-bound geometry and generation/repair protocol

The current live Kingdom contract is `src/data/implementation-contract.json:geometry.kingdom`: stage `[1376,768]`, matrix `[60,-10,25,35,170,165]`, `townhall` rectangle `[5,0,3,1.5]`, P01–P17 exact site rectangles, road polyline, `right-crossing` rectangle/cells/approaches, blocked right bank and gate anchor `[7.7,10]`. Refresh the actual file/hash before using those values. Do not confuse the planning contract with the live one or reuse an obsolete guide SHA after pixels/geometry change.

1. Prepare one precise visual scene contract from the real footprint/road/deck/contact data. Include full building/actor vertical and ground extents, bank clearances, open gate approach and protected Hall space. Keep all saved site IDs and legal navigation geometry.
2. Trace a plausible visual boundary suited to the terrain, river, Hall, plots and intended advanced-mock hierarchy. The source contract does not supply a ready-made wall polyline. **Do not derive the finished wall by expanding the min/max plot bounding rectangle.** Design source-supported connected perimeter/gate/depth, test all reserved extents and preserve legal topology. A genuine geometric contradiction needs exact coordinates and a minimal reviewed correction; it cannot be hidden with a new picture or silent moved cells.
3. Prepare actual request-specific base/reference/guide/allowed-edit masks and protected regions, with source→stage→native transforms. Verify that every intended conditioning input is actually bound in the supported provider payload. A local mask filename is not evidence it was transmitted, and an API without supported mask/conditioning cannot be described as obeying one.
4. Choose existing compatible source/layer reconstruction first. Where needed, produce a source-bound clean terrain plus integrated built-wall counterpart in the same registered family. Generate/edit only the necessary missing pixels. Review its master before no-wall/scaffold/taller/front-mask derivatives, then review actual composites before binding all runtime ages.
5. Trace the returned actual terrain/deck/wall/ground-contact features; compare with protected logical geometry and measured footprints. Reject off-contract candidates. Do not warp the whole city, shrink figures to dots, move gameplay cells, paint sample stamps or blur around mismatches to force a checker PASS.
6. Record full source/request/response/native/derivative/hash/transform/catalog/consumer lineage. New production filenames/catalogs below are PLANNED_NEW; the executor selects a unique version namespace and updates references atomically after actual acceptance. Preserve rejected/source bytes without creating unrelated duplicate asset trees/backups.

**Reusable generation/edit instruction template** — instantiate from actual prepared files and one selected era/phase; this text is not a ready paid request:

> Create the required registered Kingdom scene for {AGE}, phase {BUILT_LEVEL_1}, using the transmitted {BASE_REFERENCE}, {EXACT_GUIDE} and supported {EDIT_REGIONS}. Match the base's camera, scale, upper-left scene lighting, lens/perspective, terrain materials and source-bound geometry. Preserve the actual reserved Hall, every P01–P17 ground footprint, all road/deck/approach/bank geometry and the open gate anchor. Render sharp natural prepared ground, paths and ambient dressing without baked owned buildings, a second Hall, plot diagrams, labels or HUD. The era-correct wall, corners, gate structure, footing and shadows are part of this same landscape, following the reviewed {BOUNDARY_POLYLINE_AND_GATE_REGION}; it must not look like a fence/slab pasted over the painting. Preserve a traversable open gate and crossing, all current contacts and the real vertical building envelope. Maintain consistent perspective/light/material along front, sides and back. Return one native candidate for the chosen phase; linked no-wall/scaffold/taller and foreground-occlusion derivatives must use this exact registered family. No free-layout city redesign, permanent blur, text, UI, decorative fake facilities, changed bridge or moved logical sites.

The executor must translate this template to the actual supported recorded provider interface, including any necessary supported resolution/aspect settings. No assumed guide obedience, unsupported mask API, new provider/model, 32-call obligation or automatic 4K purchase is created by prose. Failed conditioning affects the relevant request; continue independent ready local work.

## U09 — Same-family foreground occlusion and one render transform

An integrated background alone cannot put a wall in front of a passing actor/building. Derive any needed foreground occlusion from the **same exact scene pixels**, at the same stage position; this is depth compositing of the integrated painting, not a new fitted wall stamp. Back boundary/terrain, dynamic structures/actors and exact front occluders must share one native-to-stage transform and one viewport camera. Correct shadows, gate opening and foot contact remain visible.

Implement a versioned source-bound scene-family catalog (suggested PLANNED_NEW `kingdom-scene-families.json`) or equivalent existing schema. Each age contains actual phase paths/hashes/native dimensions/stage transforms, traced boundary/gate/bank/road data, compatible foreground masks/occluders, contact/placement references and relevant dependency versions. `kingdomPainting()` selects only state; the renderer handles layer/depth. Update build/closure discovery to enumerate every dynamic phase and occlusion dependency. Do not leave renamed `displaySHA256` fields bound to older pixels.

Verify a real actor passing behind/in front of the boundary at the open gate and a foreground building with correct near/far depth, at normal/phone view and after pan/resize/reload. No seam, hole, repeated double shadow, opaque matte or unclickable essential object. Alpha verification and source hashes are necessary; actual gameplay composite review decides the visual gate.

## U10 — Logical correctness and live placement acceptance

Keep Hall1, all **17** empty owned sites, Walls0 and original supplies/owned roster at New. Trace and test all 18 site selections plus actual Walls/gate at required view sizes. Direct picking and contextual accessible lists return the same stable ID. Reflow/focus/occlusion cannot select an unintended neighbour or make a legal site unreachable.

For each actual build: preview/cancel retains resources/site/jobs; confirm pays exact current costs once; scaffold/work reads the saved job; real completion renders the real age/level building; reload retains IDs/state; upgrade uses the adopted rules. Empty→building→built cannot be just painted variants with invisible state. Real building layers remain independent from terrain/wall selection. Old saves, current facility multiplicity/caps, income chronology and all downstream gameplay consequences remain compatible.

Record one natural early build/upgrade loop and labelled dense/mature/each-age fixtures. Fixture grants cannot close the natural progression/journey requirements. Check every site/building type/level/era source against its whole ground footprint and vertical frame/depth; do not accept a good empty landscape as evidence of a working city.

## U11 — Complete the eight-age world and whole-game scope

All eight ages retain the fixed layout and source-backed mechanics while adopting coherent materials and assets. Direction for the scene family, subject to adopted data and actual source review:

| Age | Consistent required treatment |
|---|---|
| Stone | Primitive timber/earth/thatch/stone and a believable palisade; no modern fence strips or medieval city baked into empty owned sites. |
| Bronze | Bronze-era timber/earth/masonry and appropriate fittings/transport; not a recolored Stone plate with a token bronze tint. |
| Iron | Iron-era timber/stone/iron reinforcement and source-backed roles; no firearm tower masquerading as Iron. |
| Medieval | Integrated masonry/timber boundary, gateway and civic scale; true source-supported depth and material. |
| Gunpowder | Period fortification/workshop/weapon/transport forms, with compatible broader bastion massing where the composition supports it. |
| Industrial | Era-specific production/transport/materials, coherent riveted metal/masonry where appropriate; no unchanged medieval city relabelled. |
| Modern | Modern ground/civic/defense/vehicle language, without inventory-symbol wall panels pasted on the city. |
| Future | Coherent advanced city/material/transport forms and integrated boundary, retaining adopted facilities/rules and actual saved states. |

This is an art-direction table, not permission to invent new facilities, roles or mechanics. Review actual complete composition, all 32 physical scenes and current art consumers. Every requirement in original 35, G01–G16, 96 steps, M01–M30, J01–J18, A01–A08, 32 class/kit rows, 192 slot decisions and every role/direction/clip remains mandatory. Retain the independent 17 October repair preface's storage, body, worn gear, role animation, scene fit, mechanics, natural journeys, layout, performance and package fixes. Latest presentation corrections do not narrow any of them.

## U12 — Gate A: complete desktop game and independent content verification

Finish every ready game/art/interaction/desktop repair and execute its real consumer first. Use the existing local source preview and isolated campaigns for iteration; production bundles/APKs are not needed to inspect a text button or a blurred terrain PNG. Preserve the original complete source of truth and use actual state/visible deltas, negative/cancel/reload/return cases.

Before APK packaging, the full desktop candidate must meet the original visual/functional/natural-simulation distinctions and U01–U11: actual M01–M30 counterparts, all required states, correct economy/campaign/three modes/five War flows, bodies/kits/worn gear/motion/scene footprints, J01–J18, browser-store safety/horizon, exact responsive/inset/focus/contrast and measured rendered performance. Source/native-only checks and preparation may proceed when independent; no premature packaging to substitute for unresolved content.

The planner/verifier independently compares the completed browser candidate and its current evidence to the mocks and adopted mechanics **before final APK packaging**. This is content verification of the complete game, not an interim owner-preview permission step. Executor repairs returned defects within authorized scope and rechecks dependencies; no partial dashboard/body/wall checkpoint is a complete candidate. An unperformed required assertion remains OPEN. No missing APK blocks source-level independent desktop review. Do not self-award independent acceptance.

## U13 — Gate B: final package from the verified snapshot

Only after Gate A's required pre-package content assertions pass, freeze one actual source/art/native snapshot, build `dist/`, sync Android `www/`, and build the offline preview APK. Verify every transitive/dynamic consumer, native manifest/dex/config identity, application IDs, zero permissions, CRC and exact delivered bytes/hash. Record package verification independently; static parity is not a new visual/functional acceptance shortcut.

**No routine APK build after every CSS/image/code checkpoint.** A technical package test is not progress toward art acceptance. A failed packaging/native build may be repaired and rebuilt; a substantive later source/art correction invalidates relevant evidence and requires rechecking before replacement packaging. “One final candidate” does not mean forbidding necessary fixes or keeping an invalid binary. Preserve required previous packages; no backup/deletion/Git authority is added.

The current verifier must check that packaged content is the same reviewed snapshot. A correct package cannot turn a failed desktop game into a passing one. Update status/handoff/build notes with exact current identities; never copy an older APK hash into a new status banner.

## U14 — Gate C: mobile QA, repairs and owner review

Device verification follows the completed desktop game and verified final APK. The existing later-stage device authorization remains conditional on those prerequisites; this planner does not operate devices or dispatch the executor. No repeat owner permission is needed solely because the already authorized later stage has now become ready.

Use the exact delivered candidate for actual touch/dense picking, safe insets/rotation, graphics/readability, audible Music/SFX, background/pause/resume/kill/save/restore/import/export/native chooser and measured device performance/permissions. Fix real returned mobile/native defects, rerun affected desktop/package checks, and produce the corrected exact candidate when necessary. Keep native/device acceptance separate from browser tests. Owner final review follows the complete repaired result; no AI awards owner acceptance.

## U15 — Existing budget, preservation and responsibility

This owner direction selects a concrete needed Kingdom/UI repair route. It does **not** increase the absolute **$100** exposure cap or automatically authorize 32 new full-scene purchases. The prior $80 allocation and targeted additional at-most-$20 for identified style/Healer fixes remain; released $15 is counted once. Classify each paid request's actual purpose and allowance. Do not assume unrelated geometry/scenery purchases can use targeted extra funds merely because total exposure is below $100. Reconcile invoices/liabilities/holds/UNKNOWN before spending; do not promise the remaining art fits.

Preserve the recorded provider/project/account/routing, one active/inflight UNKNOWN, owned mutex/CAS, write-ahead exact input binding, conservative reservations and receipts, ≥20 seconds after successful response completion, and definite429 ≥60 seconds or longer Retry-After. Default 1K batches are exactly30 genuinely independent useful rows; no filler or resolution/ID changes to bypass those rules. Necessary2K actors/rigs and proven4K scene patches follow the recorded progressive route after native review/physical tracing. The new scene-family method still needs the applicable supported/affordable request route. No repeated permission for already authorized affordable prepared repairs; genuine external limits affect their exact rows while other work continues.

The other AI implements, generates where necessary/authorized, verifies, repairs and packages. This AI acts as architect/verifier/advisor/senior QA and corrects specifications/returns defects; it does not spend, mutate production, build, operate devices, change Git/storage or dispatch implementation. Preserve dirty/concurrent work, original/native/raw art, required evidence, saves and packages. No duplicate asset tree/backup/cleanup is introduced.

## U16 — Concrete completion, not another checkpoint

For every original requirement and new U01–U16 child: identify actual input/source/consumer → implement → exercise the real visible/state outcome → cancel/illegal/reload/return → repair → recheck → close with matching current evidence. Every required child must pass. Counts, descriptions, filenames, asset READY metadata, icon presence and self-written PASS cannot close artistic or natural-play behavior.

At full-candidate handoff provide the playable candidate and current source/evidence identities, genuine reference/current/native-phone comparisons, actual motion/event/contact proof, complete natural/simulation/fixture-labelled journeys, real numeric/storage/fault results and honest remaining external-stage gates. Reports support that implemented result; writing them is not a substitute for it. Finish all independent ready implementation work before any genuine external-limit exception. State exact attempted repair/dependency/financial shortfall and preserved usable artifacts; never call an incomplete result finished.
