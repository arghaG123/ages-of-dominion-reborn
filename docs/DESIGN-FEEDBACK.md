> **Owner rejects current playable-game delivery — 4 October 2026:** Owner reports the browser runtime is not playable and still looks like the preview. [Readiness report](plan/PLAYABLE-GAME-READINESS-OWNER-REJECTION-2026-10-04.md) confirms schematic Adventure/Tactical/Defense and unaccepted Kingdom composition in current source/saved pixels; 0/4 main experiences demonstrates the promised finished standard. Core rules/assets are preparation, not game completion. [Corrected Code priority](plan/CODE-AI-PLAYABLE-DESIGN-FIRST-2026-10-04.txt): deliver one coherent visually faithful Stone-age UI play loop, then complete full scope. Image local work continues independently; no new paid authority. Device STOPPED. Concurrent records/history below preserved.

# Design feedback and revision record

## Version1 — rejected, 2 October 2026

The owner explicitly rejected the first 30-view static gallery. Its appearance was not good enough; drawn icons/backgrounds, broken portrait/tall presentation and Adventure/Tactical/Defence scenes did not follow the supplied mocks. This is substantive rejection, not a minor polish pass. Do not call version1 accepted or start game coding from it.

| Area | Recorded problem | Required revision evidence |
|---|---|---|
| Icons and frames | Drawn substitutes do not match rendered mock art; decorative treatment lacks the intended material/detail | Use matching existing rendered icon assets where suitable. Check whether a source already has a circular rim before adding another frame; no double rims. Show side-by-side reference and proposal. |
| Portrait/tall modes | Cropping and aspect/layout failures; controls/world do not stay in coherent proportions | Aspect-preserving art/world bounds, accessible targets, safe HUD and no overflow/cutoff in all 30 views. Check reference proportions, tall phone and landscape. |
| Kingdom/Settings | Baked resource rails and edge buttons remain under the proposed HUD; Day1 shows duplicate, drifting plus markers | Use one registered aspect-preserving image plane for reference-backed composition. HUD exclusions and any overlays must use that plane's transform, not unrelated frame percentages. No doubled rails, buttons or pads. |
| Adventure | Synthetic roads/river enter sky; wrong immersive landscape treatment | Real grounded landscape/roads/bridges/sites and correctly scaled party/route/fog treatment; avoid a diagram posed as terrain. |
| Tactical | Huge sky and tiny actors; wrong ground/camera/grid proportions | Ground dominates the battlefield, legible stack formations and subtle registered grid; preserve7×10 rules without letting geometry dictate wrong art. |
| Defence | Wrong landscape/path treatment versus mocks | Winding lane grounded in coherent terrain, proper gate/tower/actor scale, compact wave/ability tray and distinct era forms. |
| Hero | Full-body portrait cropped; equipment framing differs from requested presentation | Show the intended full character/grounded stage and all six real item positions; disclose any missing Shield/Ring or class art. |
| Forge | Reuses a giant Hero background instead of an item/forge stage | Distinct real forge/item-stand scene with selected item emphasis, inventory and genuine rendered material treatment. |
| Forge actions | Version1 shows Enhance despite the current plan treating enhancement as a later design track | Show actual planned Craft/quality/inspection actions; do not silently adopt extra upgrade mechanics from the mock or create inert promises. |
| Army | Reuses the same giant Hero background instead of selected-unit stage | Distinct selected current-era unit stage, real role/creature grouping and readable roster/stat placement. |
| Supporting surfaces | Repeated generic hall backdrop/context and weak ornament | Each screen needs its appropriate context/frame hierarchy rather than cloning one portrait/hall across unrelated features. |

The QA observations above identify specific defects behind the owner rejection. They do not imply that unmentioned sections were accepted. Every revised section remains pending review; all 30 views must be inspected, not just three representative captures.

## Version2 — in revision

Artist is revising design documentation only. Use existing artwork first; no paid images, fresh game code, dependencies or APK actions. Preserve version1 screenshots and metadata as before evidence. Record new after captures with view ID, frame mode, viewport and version. A gallery load/navigation test is separate from visual fidelity review.

Preliminary version2 captures improved some scene context but **still failed visual review**. Tactical terrain remained tiny with black caption/blank areas; Hero/Forge/Army exposed baked old UI underneath the proposed controls; tall Day1 cropped outer pads. These are open blockers, not approved compromises. Tactical ground must dominate at useful scale without caption artifacts. Hero/Forge/Army must have one clear UI layer. All17 Day1 pads must be visible in the default portrait/tall composition, with correct registration. Artist and QA are revising/checking before any freeze.

After QA checks the revised views, show the owner the corrected sections and references. Record exact requested further changes, acceptance or rejection per section. Until then the owner-feedback gate is unresolved and game implementation remains not started.

This record supersedes generic statements that all sections are merely awaiting their first review: feedback has occurred and version1 was rejected. It does not override the full product scope, 17-pad correction, exact 30-image/single-active policy or offline native constraints.

## Resumed correction pass — 2 October 2026

Design documentation only; old game and raw art untouched. Review page: `design-preview/review-corrections.html`; live gallery: `design-preview/index.html`; scoped CSS: `design-preview/revision.css`. Evidence is in `design-preview/evidence/resumed/` and capture tooling is `design-preview/check-revision.mjs` using installed Playwright/Chrome.

- Hero/Forge/Army use clean aspect-preserving source windows instead of the complete baked interface. Full Hero body and all six slots are shown in tall and landscape. Forge retains the sword/stand, six categories and Craft/inspection copy; no Enhance/Reforge/Sockets mechanics were added. Army keeps its selected-unit stage and larger roster cards.
- Adventure uses an explicitly bounded clean reference window; portrait centers the bridge/hero and landscape exposes the scene. Old inventory/footer/sidebar controls are excluded. Source linework remains below the final realistic target.
- Tactical excludes montage captions, score rail, joystick and action controls, enlarging the field. The supplied tile is still low resolution, and flank formations crop in portrait. This remains a visual blocker; no source processing or generation can be assumed authorized.
- Day 1 uses one contained registered plane with 17 transparent pad targets. All target rectangles lie within tall and landscape frames. Sampled edge masks/sky/foreground seams remain imperfect. Landscape shows the full portrait geography against an inspection backdrop; it is not a resolved wide city composition.
- Iron/Future are isolated hall material studies; no duplicate castle or implied completed era city. Skills/spells use labels while distinct ability artwork is missing. Resource labels replace unsuitable city-like resource medallions. Navigation medallions reuse existing art without a second disc.

Verification: 12 affected views captured in two frame modes, then only changed subsets recaptured. JS syntax and asset loading passed; no page/asset errors. Shell checks at375/768/1280 show no horizontal overflow. Literal review frames424x933 and820x462 differ from the shell's contained phone frame. Technical results are not visual acceptance or hardware tests. No complete30-view re-audit, image job, game test/build, dependency installation or APK action occurred.

Owner acceptance: every section remains PENDING. Show the side-by-side correction page and record owner feedback before implementation. Remaining fidelity gaps are disclosed there; do not call this a final visual pass.

## Owner feedback and unified-style revision — 2 October 2026

Owner feedback: icons do not fit across screens, including resources/skills/spells; Adventure/Tactical map placement is wrong; use portrait if necessary. The hero should travel mounted or on foot. Adventure/Tactical mocks are composition references, not a request for cartoon styling; the modes must synchronize with semi-realistic Kingdom.

Design-only response: `design-preview/review-unified.html` supersedes the earlier correction page. Existing `battle-back-plains.webp` supplies naturalistic terrain instead of copied cartoon maps/montage. Existing rendered actors supply a portrait Adventure travel pose/path study and a complete7-column×10-row Tactical board with stack groups/counts. Mounted/on-foot selection and a transform-only route demonstration are present; reduced motion completes immediately. Mounted art is explicitly a cavalry substitute for scale, not a completed mounted hero identity. No gameplay, pathfinding, movement cost/speed, walking gait or campaign state is implemented.

HUD uses32px navigation art within48px targets,40px main Kingdom action,20px resource symbols, screen-specific destination clusters and distinct Kingdom/Buildings graphics. Dedicated nine skill/eight spell assets are copied unchanged and hash-recorded in asset-provenance.json. Narrow landscape requests fall back to portrait; wide review frames expand correctly. War retains all five required options. Old source/raw art was only read; no game dependencies/builds/APKs or image jobs.

Technical evidence: `evidence/resumed/unified-hud-checks.json` records180 DOM HUD checks (30views×3widths×2requested frames), zero target clipping/overlap/size failures and zero shell overflow or page/asset errors. Travel pose switch, spatial movement and1ms reduced-motion duration verified. `unified-*-tall/landscape.png` are scoped visual captures; `unified-adventure-foot-tall.png` is the separate contained-phone pose capture. These are technical/layout checks, not all-screen visual acceptance or real hardware tests.

Remaining: full inhabited Adventure geography/roads/bridge/fog and camera registration; dedicated mounted/directional hero art; unit cutout/grounding/facing and tactical perspective refinement; Kingdom extension/mask seams; owner feedback on every section. Current mode composition is a material/layout study, not a final scene. No section accepted.

## New reference direction / new-chat handoff — 2 October 2026

Owner still cannot see resource symbols clearly; previous size/DOM checks did not establish legibility. Seven new reference files were saved unchanged and hash-verified in `docs/plan/references/owner-additions-2026-10-02/index.json`. Read that directory's `REVIEW-NOTES.md` for composition, scale, finish, HUD and scope interpretation. The new Adventure references require dense inhabited geography with connected roads/bridges, settlements, ruins/mines, varied forest/elevation/biomes, guards/treasure and a mounted/on-foot hero. Tactical references require grounded readable formations and richly authored terrain rather than the current empty-grass study. Freestanding material resource symbols should be clear at phone size. Image text/currencies/creatures/hexes do not silently change the planned rules. No design acceptance.

Owner asked to create and switch to a fresh chat before continuing plan/design work. All current details and next actions are saved in RESUME-HERE and the new reference note. Old game remains read-only; planning/previews only, single-agent scoped work; no image jobs or game implementation.


## Latest scoped revision — 3 October 2026

Review `design-preview/review-reference-direction.html` for Resources, Adventure and Tactical. The AVIF was browser-decoded and visually inspected. Phone resources now show grain/provisions, logs, rock and coins at32px height above names/amounts. Existing aerial forest/river/road and ruins/stone-bridge art replaces the empty-grass studies; settlements/sites/guards/treasure and six count/health-bearing formations are added as static scale studies. Precise reuse and remaining gaps: `docs/plan/REFERENCE-DIRECTION-2026-10-03.md`.

Nine scoped literal captures at375x825/424x933/820x462 and shell checks at375/768/1280 passed asset/JS, resource/count bounds and48px scene button checks; final selected pixels were reviewed. Resource text contrast is approximately9.0:1/7.1:1. The375px gallery shell contains a341px scene. This is neither a full30-view audit nor physical-device/visual acceptance.

Still missing: clean transparent resource objects, larger fortified/biome-rich Adventure region with stone bridge, matching aerial site/actor camera, class-correct mounted Gawain and directional gait, high-detail Tactical terrain registered to legal7x10 cells. Some provisional cells/poses overlap painted obstacles. Current previews improve density but still fall short of the new target. Every section remains pending/revision-needed. Old game/raw art preserved read-only; no game source, installs/builds/APKs, image jobs or billing changes. Single-agent work only.



## Latest owner correction — 3 October 2026

Owner REJECTED the latest assembly as still far from the beautiful real-game-looking mocks. Resource icons were too big; no resources are wanted in battles. Phones may rotate to provide Adventure/Tactical more space. Latest comparison: `design-preview/review-mock-comparison.html`; all26 supplied files: `design-preview/all-owner-mocks.html`; detailed updated contract: `docs/plan/ROTATION-AND-MOCK-COMPARISON-2026-10-03.md`.

Actual corrections:18px symbols in28px corner rail; no resource HUD in Tactical/Defense; auto portrait/landscape resize and edge-to-edge static review via `index.html?stage=1#adventure` / `#tactical`; smaller contextual controls; sharper unchanged raw Tactical ruins source. Seven scoped captures pass technical checks. These do not establish game-like finish: Adventure source/detail and both modes' camera, grounding, scale, facing and authored composition remain visual failures. Prior resource32px/rail72px and portrait-restriction claims are superseded. Owner acceptance/coding gate remains unresolved. No image job, game source, dependencies or APK work; single-agent only; old game/raw art preserved.


## Map-space blueprint continuation — 3 October 2026

Latest review: `design-preview/review-map-space.html`; specification: `docs/plan/MAP-SPACE-BLUEPRINT-2026-10-03.md`. The latest owner correction about planned terrain spots is now addressed as a concrete spatial proposal before scene replacement. Two actual owner mocks were directly compared. Adventure reserves six empty site clearings, four pickups, two guards, a hero start, connected roads/stone-crossing approaches and water/wood/cliff exclusions. Tactical reserves two decks/approaches, separate deployment and seven active ground anchors (commander plus six stack slots), with rock/wall/water exclusions. All scene layers share one per-mode source projection and root camera fit across portrait/landscape. Separate site/slot, route, selection and grid layers can be inspected independently.

Precise current-art camera, scale, facing, hoof/base and baked-shadow gaps are recorded; source pivot estimates remain uncertain, not adopted metadata. The512px forest terrain and low-camera6336px ruins panorama remain material evidence and do not supply this terrain. Whole owner mocks stay separate reference evidence. Existing scene previews were not silently replaced or accepted.

Static geometry checks and eight scoped browser cases passed (Adventure/Tactical at375x825,825x375,768x1024,1280x1024). Seven focused final captures were inspected. Evidence: `design-preview/evidence/map-space/checks.json`; checker `check-map-space.mjs`. Verified coordinate continuity/exclusions, bridge approaches, distinct slots/commander, shared pixel registration on resize, layer/detail switches,48px review controls, shell contrast and no asset/page/overflow errors. No game rules, finished-scene fidelity, physical device, full-gallery acceptance or owner approval established.

Owner feedback on this concrete blueprint is the next review step. High-detail authored terrain, compatible aerial sites/actors, final scale/facing/shadows/gaits and finished HUD remain unresolved. Prior scene assembly remains rejected; blueprint is proposed/unaccepted; all full-product sections and feedback-before-coding gate persist. HUD18px symbols/28px rail, no Tactical/Defense resource HUD, both orientations and full eight-age/three-mode campaign retained. Single-agent work only; old game/raw art read-only. No game source, dependencies, builds/APKs, image jobs, generator or billing changes; exact30/single-active and UNKNOWN/BILLING_DISABLED constraints remain.

## Landscape and original mock authorization — 3 October 2026

Owner selected “Landscape — horizontal, wider than tall” in the new chat. All screens and all eight ages follow this orientation. Original Vertex-created review art is requested; prior reuse requirement is optional for this scope. New plan and30 full briefs are prepared, not visually accepted. The supplied project/account is recorded in current status; local sign-in/access and historical-operation reconciliation block submission. No image output or design approval exists. Previous rejected previews remain rejected.

## Current result — thirty landscape mocks collected, 3 October 2026

Batch `landscape-mocks-20261003-efcd7a7e` is SUCCEEDED:30/30 successful requests, exactly30 landscape1376x768 JPEG outputs downloaded/matched/hash-verified; zero missing/duplicate/invalid files. Review index: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/REVIEW-INDEX.md`; overview `review-overview.jpg`; technical evidence `collection-report.json`; scoped findings `VISUAL-REVIEW.md`. Provider ran01:48:18–01:50:52 UTC (07:18:18–07:20:52 Asia/Calcutta).

Whole30 overview and five full-size images reviewed. Actual fidelity remains REVISION_NEEDED: invented home title/text; Medieval-looking Stone starter; cross-age camera/geography/material drift; duplicated/mismatched icon semantics; some device frames; incoherent hero/HUD identity. Others have overview-level review only. No owner acceptance or interactive/mobile/gameplay checks. Owner must see each relevant section before coding. No second batch planned/submitted, no automatic retry or provider fallback. Original outputs preserved; local/cloud lock retained with COLLECTED_REVIEW_READY status awaiting feedback. Old project/unknown jobs remain untouched under the explicit target-project exception. No game source/dependencies/build/APK/device changes.

