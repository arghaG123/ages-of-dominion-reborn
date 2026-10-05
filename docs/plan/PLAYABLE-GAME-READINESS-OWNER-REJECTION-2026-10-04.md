# Playable-game readiness and owner rejection — 4 October 2026

The current reborn implementation is a functional prototype with substantial rules and asset preparation. It has not delivered the playable, visually coherent game requested by the owner. The owner reports that the browser build is not playable and resembles the previous preview; this is current negative acceptance feedback, not a request to relax the target.

## How much is prepared and completed

There is no audited, weighted completion percentage. File counts, generated images, tests and APK size cannot supply one. No statement such as 70% or 90% complete is justified by the current evidence.

| Area | Preparation already present | Completed deliverable status |
|---|---|---|
| Rules and campaign state | Independently authored economy, construction, recruitment, route spending, Tactical rules, Defense stepping, equipment, skills, story and save/recovery source; earlier bounded technical evidence | Substantial functional foundation; full natural campaign and user usability are incomplete |
| Artwork | Generated sources, versioned crops/mattes, literal role interfaces and some suitable static consumers | Partial usable inventory; no assembled whole-game visual acceptance |
| Kingdom | Hall, pads, construction/picking and resource state over a painted terrain | FAIL visual delivery: extra baked development, mismatched empty-pad presentation and preliminary UI |
| Adventure | Legal routes, movement spending, fog/sites and mounted review samples | FAIL visual delivery: flat schematic region, line roads/circle markers; integrated painted world absent |
| Tactical | Legal turns/actions, unit cutouts, counts and settlement source | FAIL visual delivery: bare grid and coordinate button list instead of the terrain-rich combat view |
| Defense | Fixed-step simulation, waves/roles/deployment and tower/enemy plates | FAIL visual delivery: simple lane line on flat ground; coherent defense scene absent |
| Hero/Army/Forge | Partial Ranger assembly, era plates, gear slots and stat/action text | Prototype presentation; full bodies, equipment imagery and finished screen composition incomplete |
| Full linked play | Saved starter steps and selected battle/session starts | INCOMPLETE: saved manual pass omitted item equip, paused Siege/Endless, and did not play all eight ages |
| Preview package | Current saved unsigned package and historical closure/native-policy evidence | Build artifact exists; native/device launch and performance remain UNVERIFIED, device STOPPED |

Quantified acceptance: **0 of the 4 primary game experiences (Kingdom, Adventure, Tactical, Defense) demonstrates completion to the promised visual/playable-game standard.** This does not mean zero rules or artwork have been produced. The full connected campaign and eight-age journey are not demonstrated complete.

## Direct source and pixel evidence

Closing refresh: `src/client/main.js` changed concurrently to 20:39:18 on 4 October; `src/client/game.css` remains at 15:17:23. The newer main file adds consumer/card/review presentation, but the same schematic Adventure, Tactical and Defense methods and `baked-unaccepted` Kingdom flag remain. New consumer-matte QA files around 20:33 are asset comparisons, not evidence that a new complete scene renderer has shipped. Image also published a v5 partial interface with additional local crops/parts, explicitly `codeAIHandoffReady:false`; that is useful preparation and does not close the assembled-game gap. Concurrent executor work is preserved, and this report is a dated snapshot of the confirmed gaps.

The root `index.html` loads `src/client/main.js`, so the runtime itself contains this preliminary presentation. This is not explained solely by the existence of a separate design-preview directory.

- `clearWorld()` hides the terrain image. Adventure renders a plain rectangle, site polygons, line roads and circles; it does not assemble the promised natural region.
- Tactical renders a plain rectangle and grid polygons, then small unit cutouts. Legal moves are listed as buttons such as `Move sk-p to 2,8`; the visible battlefield lacks the mock's natural terrain, clear unit/status hierarchy and contextual command presentation.
- Defense draws the contract lane and plates on plain ground. The lane is a technical visualization, not the completed forest/fortification scene.
- Kingdom alone displays the old painted terrain, explicitly marked `baked-unaccepted`; its generated development is inconsistent with sparse Day 1.
- Shared CSS supplies a basic header, scrolling row of thirteen text tabs and generic Actions panel. It does not implement the mock's designed scene-specific HUD, initiative strip, equipment framing or contextual controls.

These are broad renderer and interaction-design gaps. Smaller matte repairs, a static horse swap or another passing rule test cannot close them.

Live follow-up after the owner's localhost clarification: the existing `scripts/serve.mjs` process listens on 4173. A temporary in-app browser opened `http://127.0.0.1:4173/` and confirmed the game title, saved Stone-age campaign, actual Adventure diagram and actual Defense flat-lane scene. Opening Actions reveals some real controls (Leave town, construction/upgrade actions, pending defense settlement), so it would also be inaccurate to say no mechanics exist. However Tactical with no active battle displays an empty grid and says "Choose a move, a spell, or wait" while exposing none of those actions. It fails to explain how to enter a battle. This is a directly observed usability defect. The temporary tab was restored to Kingdom with Actions collapsed, then closed; no gameplay command was issued. Existing campaign clocks ran normally while the page was open.

Current saved evidence:

| Runtime capture | Appearance target |
|---|---|
| [Kingdom Day 1](../../qa/code-ready-20261004/manual/03-kingdom-day1.png) | [Landscape Kingdom target](../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/02-kingdom-day1.jpg) |
| [Adventure mounted review](../../qa/code-ready-20261004/followup/02-mounted-review.png) | [Adventure target](../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/11-adventure-overview.jpg) |
| [Tactical runtime](../../qa/code-ready-20261004/manual/17-war-skirmish.png) | [Tactical target](../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/14-tactical-deployment.jpg) |
| [Defense runtime](../../qa/code-ready-20261004/manual/17-war-siege.png) | [Defense target](../../design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/18-defense-wave.jpg) |

Targets are visual references; their baked text/values/units are not playable runtime layers or accepted mechanics. Implemented data and rules must remain authoritative. Known target errors still require correction under FULL-IMPLEMENTATION-SPEC.

## What must happen next

Code's first delivery should be one coherent Stone-age playable loop with the requested game presentation: new campaign -> state-aware construction -> recruit -> direct, understandable Adventure travel -> manual Tactical fight -> result/loot/equip -> return -> Defense -> settlement -> save/reload. All actions need obvious controls and visible feedback in the real scene. A generic Actions list may remain an accessibility fallback, but cannot be the entire designed game interaction.

The same delivery must use suitable registered terrain/site/actor layers, a coherent camera/light/scale and the compact contextual HUD from the approved direction. Built/unbuilt state must agree with the pixels. A full mock JPEG with hotspots, a diagram plus a portrait, or modes that merely open do not satisfy this requirement.

Preserve working source and assets; address the renderer and interaction design in the current fresh implementation. Keep the complete eight-age/three-mode/supporting-system scope. A usable Stone loop is the next concrete proof, not a deletion of the rest of the game. Missing art affects only its roles; use suitable existing layers and versioned review proposals, and continue unrelated ready work. Do not silently change the active geometry or promote rejected sources.

After the first coherent loop, extend the same rendering/UI quality across other ages/classes and supporting screens, complete remaining natural journeys, and verify native/device only under renewed device authority.

The previous matte-focused prompts remain useful for their scoped repairs but gave too little priority to this product-level gap. [The corrected Code priority](CODE-AI-PLAYABLE-DESIGN-FIRST-2026-10-04.txt) must precede further claims of readiness. Image can continue its existing local recovery and three-role draft; this feedback authorizes no new paid calls.

## Verification limits and handoff

This planner read current local source/status, inspected saved runtime/reference pixels and observed the existing localhost runtime through a temporary browser tab. No fresh test suite, build, server start/stop, gameplay command, provider query/call, device, Git/storage operation, executor message or delegation occurred. Screen navigation and Actions-panel inspection confirmed the visual gaps and misleading idle Tactical message. This was not a full gameplay playtest, and no assertion that all buttons are broken follows. The owner's reported usability failure is recorded alongside these independently confirmed gaps.

Keep owner/visual/runtime/native/device/storage layers separate. The latest executor's 90-test count remains a dated report before its last rider edit, not a fresh verification in this audit. Do not convert the existence of rules or a built APK into game completion.
