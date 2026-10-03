> **LATEST OWNER CORRECTION — planner/verifier only, 3 October 2026:** This chat creates the specification, execution instructions, acceptance criteria and reports. Another AI must execute image batches, game code, builds, collection and regeneration. Do not resume execution or delegate it from this chat. This supersedes previous implementation/production execution authorization interpreted for this chat. Approved landscape appearance direction, full scope and budget constraints persist. Read the current report at `docs/PLANNER-VERIFIER-HANDOFF.md`; older execution status below is historical.

> **CURRENT OWNER AUTHORITY — 3 October 2026:** generated landscape mock direction approved despite synchronization defects; fresh implementation and useful Vertex `gemini-3.1-flash-image` batches authorized. Whole game LANDSCAPE. Hard US$80/aim$60, useful30 per batch, one active/unknown in supplied project; once terminal submit next prepared useful batch BEFORE fetching previous. Old no-code/portrait/Flash-Lite/collect-before-next instructions below are HISTORICAL. Canonical complete spec: [FULL-IMPLEMENTATION-SPEC.md](FULL-IMPLEMENTATION-SPEC.md). Technical/asset/composite/game/native acceptance remain separate.

# Original landscape design plan — 3 October 2026

## Current decision and deliverables

The owner confirmed **Landscape — horizontal, wider than tall** in this new chat. Every game surface now follows landscape: entry/home, Kingdom in all eight ages, Adventure, Tactical, Defense and all supporting screens. This supersedes portrait-primary requirements and the previous automatic two-orientation proposal. The existing previews remain historical, rejected or unaccepted; they have not been converted or approved.

The owner requests an original plan and new Vertex-generated mocks comparable in finish to the supplied references. Existing artwork reuse is optional for this mock scope. Work remains design documentation and review; game source, dependency installation, native builds and device work remain outside authorization. Continue single-agent, with focused reference checks and no whole-gallery capture loops.

Prepared deliverables:

- This original composition, interface and review plan.
- `LANDSCAPE-MOCK-BATCH-30.json`: exactly thirty useful, individually specified prompts, each asking for one original 16:9 image. These are drafts, not provider requests already submitted.
- `VERTEX-MOCK-READINESS-2026-10-03.json`: sanitized fresh cloud and historical-job findings.

No new images exist yet. The owner supplied Vertex project `project-eaa4c1cc-8f19-4d24-9e6` and account `arghawork3@gmail.com`. That account is absent from local CLI credentials and cannot refresh a token. The existing CLI credential receives HTTP403 / IAM_PERMISSION_DENIED on both global and US-Central1 job metadata in the new project. Earlier configured-project metadata still returns BILLING_DISABLED. Existing operations remain UNKNOWN. A historical pending record and two records without terminal state require reconciliation. No paid inference, upload, provider fallback or billing/IAM change occurred.

## Visual direction

An inhabited, believable strategy world carries the screen. Terrain, buildings and figures share three-quarter depth, natural material texture, upper-left daylight, coherent shadows and a controlled atmospheric distance. Compact polished controls sit at the edges. Modernization means simpler, more legible silhouettes and restrained material frames while retaining the references' richness.

Directly inspected appearance evidence: the nineteen-reference contact sheet, full Medieval Kingdom reference03, Adventure `image_4f5e15d7.jpg` and Tactical `image_27abdc40.jpg`. The city reference places a commanding citadel above a dense radial settlement; Adventure ties a fortified town to roads, stone crossing, forest sites and travelling hero; Tactical uses close grounded formations on opposite banks. New compositions should preserve these relationships without adopting the samples' extra currencies, names, hexes or creature families.

Use a restrained dark material palette for interface chrome. Apply approximately60/30/10 to that chrome: dark slate foundation, quieter stone/metal structural surfaces and limited brass/accent highlights. Natural world imagery keeps its own material colors; the ratio must not turn the scene into opaque panels covering30% of the screen. Proposed tokens: canvas `#10171B`, surface `#263239`, brass `#C9A35B`, primary text `#F1E9D9`, secondary text `#C6CFCE`, selected cyan `#70B9C5`. Contrast must be measured on final textured surfaces; these proposals are not an audited pass.

Use an8px spacing rhythm with4px detail increments. Preserve the explicit resource exception: **18px symbols in a28px rail**. Typography follows16/20/25/31px at a1.25 scale, with12px only for compact badges and14px labels where space demands. Screen controls need48px touch targets even when their visible icon is smaller. Selected, pressed, unavailable, loading/error and success treatments belong to the component specification; raster mocks alone cannot prove them.

## Landscape composition and scaling

Author16:9 review images. Judge phone scale at **825×375** and **933×424**, then tablet **1180×820** and desktop **1280×720**. These are proposed new review targets, not executed checks. Safe insets come from the future host; reserve modest breathing room around edge controls. Larger aspect ratios reveal additional authored scenery or extend a controlled camera window. Shorter/wider screens cannot silently crop important plots, bridge approaches, formation counts or equipment slots.

For Kingdom, use broad geography rather than enlarging a tall crop: civic seat in the upper central distance, dense radial city across centre, near gate at the lower edge, river/crossing at right and believable outside farm belts. Aim for world scenery to occupy at least80% of the unoccluded play view. Keep the complete meaningful footprint visible at overview. Day1 has17 empty sites plus the separate Hall and independent perimeter; mature city density grows around those same locations.

For Tactical, logical7×10 does not dictate a tall screen. Trial a more diagonal world camera, approximately50–55° yaw and40° elevation, with allied and enemy banks reading left-to-right. This is a new proposed calibration, not measured reference geometry. Compare projected whole-board extents and actor silhouettes before freezing the camera. If the whole board is too small for accurate selection, use bounded focus/pan plus a reachable overview and contextual target list. Do not rotate only terrain or silently transpose coordinates. Commander remains(0,9).

When a phone is upright, the future application may show a simple rotate-to-landscape notice while retaining campaign state. Native orientation behavior, resizing and lifecycle preservation require a later implementation decision and verification. They are not implemented by this plan.

## Home and all eight Kingdom ages

Home uses a cinematic wide valley with original monumental architecture occupying the right two-thirds. A short brand title and Continue/New Game sit in the quieter left third. Settings and local saves remain small. No account, server selector or cloud controls. The same entry layout applies through all eight campaign ages; its scene treatment follows the current age, while a first launch can use the initial Stone campaign treatment. Mock01 calibrates Medieval material quality, not a decision to start a new game in Medieval.

Each Kingdom age retains geography and camera while changing the whole inhabited environment:

| Age | Scene treatment |
|---|---|
| Stone | Timber/thatch/hide/flint, dirt paths, sparse gathering and rough defenses; upper Hall has no Gothic castle |
| Bronze | Earth/plaster/early stone and bronze hardware, cultivated fields and early civic structures |
| Iron | Masonry, tiled roofs, iron equipment, ordered roads and formal fortifications |
| Medieval | Monumental keep, stone walls, timber/masonry neighborhoods, markets and courtyards |
| Gunpowder | Period civic manor, bastions, powder workshops, artillery yards and changed streets/roofs |
| Industrial | Brick/iron, factories, rails, pipes and restrained smoke that leaves targets readable |
| Modern | Concrete/glass, contemporary roads, utilities and transport across the whole city |
| Future | Advanced civic architecture and integrated power/transport in the same daylight valley; restrained technical accents |

Do not merely swap the central building or paint color over Medieval surroundings. Eight mature-age mocks plus a Stone starter make era continuity reviewable. Those paintings cannot establish exact per-instance building state or all eight home variants; future production must use independently layered terrain/buildings/actors after acceptance.

## Adventure, Tactical and Defense

Adventure preserves hidden16×10, six site clearings, four pickup pads, two guards and connected town/hero/stone-crossing corridors from the unaccepted map blueprint. Woods, water and cliffs exclude placements. The wide overview reads as one inhabited region with settlements, mines, dwellings and ruins at useful scale. Crossing focus and an on-foot site inspection are additional useful views of that proposed geography. Mounted/on-foot Gawain retains recognizable class, face, gear and proportions. Each inspected site opens a small contextual panel rather than a permanent large sidebar.

Tactical preserves square7×10 and commander(0,9), two crossing lanes, obstacle exclusions and six stack slots. Deployment and selected-action mocks show readable group sizes, opposed facing, contact shadows, separate health/count badges and a compact initiative/action grammar. Ruins and cliffs frame the usable arena. No campaign resource rail. Generated marks are appearance evidence; future coordinate projection and legality must be verified separately.

Defense preserves hidden9×15 and an authored winding approach to the same valley gate. Tower pads leave bends and approaches usable; towers/hero/army share the terrain camera. Four tower families and five attacker roles receive era-correct silhouettes. Owned entities deploy once without a new placement fee. Preparation and live-wave mocks show compact wave/core/pause/speed information and no resource HUD or temporary combat purse. Shared battle-result grammar communicates casualties, XP, campaign rewards and loot after combat; practice outcomes clearly retain their isolation.

## Icons and supporting surfaces

Resources are separate material silhouettes: provisions, logs, rock and coins. No dark navigation discs behind them, no second border and no tiny decorative details competing with their18px silhouette. Gold must remain distinct from Food; Stone must remain distinct from metallic gear. The thirty-position batch includes a purposeful icon style board with four resources, six navigation motifs, nine square skills and eight circular spells. It is not a transparent production atlas, exported sprite set or proof of phone legibility.

Navigation uses one slim brushed-metal rim around a clear object motif. Eight ages keep recognition and layout consistent, with restrained material evolution rather than unrelated pictograms. Skill/spell motifs remain semantically distinct and follow only the documented nine/eight identities. Final glyph size, alpha edges and accessibility names are later production requirements.

Hero centers a full body with Helmet/Weapon/Shield left and Chest/Greaves/Ring right. Forge uses an anvil/workshop stage; Army uses troops and a training yard. Inventory pairs a roomy item area with explicit comparison. Four quality treatments are Crude/Fine/Master/Relic, with no invented star scale. Story, quests, tutorial, Settings and save recovery each receive a landscape brief. Damaged saves remain distinct from empty saves; all six equipment positions are functional requirements. All eight classes, creature identities, ages and the linked three-mode campaign remain in MASTER-PLAN; thirty appearance studies do not replace that complete content scope.

## Thirty useful review positions

| Positions | Purpose |
|---|---|
|01|Home/entry material and wide composition calibration|
|02–10|Stone Day1 and eight mature Kingdom ages|
|11–13|Adventure overview, crossing focus, on-foot inspection|
|14–16|Tactical deployment, action and shared battle result|
|17–18|Defense preparation and live wave|
|19–24|Hero/equipment, skills, spells, Forge, Inventory and Army|
|25–29|Story, quests, tutorial, Settings and local-save recovery|
|30|Purposeful modern realistic icon direction board|

Every position has a full prompt and acceptance criteria in the JSON. No filler, speculative paid retry or separate calibration job. Home and the Medieval city are calibration members of this same30. Grouped style-board motifs are one useful requested image, not thirty extra calls. Request exactly one output per position; record actual output count separately if the provider differs.

## Cheapest suitable Vertex route and blockers

Official Google documents checked3 October2026 list `gemini-3.1-flash-lite-image` as GA, global, image input/output,16:9 and1K, with batch support. It is the least expensive suitable option among the evaluated Google image models for this review batch. Suitability here means documented capability; output fidelity remains untested.

| Candidate | Estimated image-output price |
|---|---|
|Gemini3.1 Flash-Lite Image, global batch|1120×$15/1M = **$0.0168** per1K image|
|Gemini3.1 Flash Image, global batch|1120×$30/1M = $0.0336 per1K image|
|Imagen4 Fast, documented per-image generation|$0.02 per image; no equivalent Gemini batch workflow established here|

Thirty Flash-Lite outputs total **$0.504 in image-output charges**. Text/input, storage, tax and currency conversion add to this; rejected successful generations still cost money. It is an estimate, not measured spend or a promise of30 successful images. Batch image output is currently limited to1K; do not use inherited4K parameters. Draft prompts are text-only; supplying appearance images later adds input charges and needs explicit request/provenance mapping.

Sources: [Google pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing), [Flash-Lite image model](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-lite-image), [batch capability/limits](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference).

Fresh probe: token refresh succeeds; global and US-Central1 job-list GETs both fail BILLING_DISABLED. Fifteen old job records were inspected; one is locally PENDING, two omit terminal state/resource names. Raw-art `.lock` files found: zero. The old `_calls.jsonl` exists. Missing file locks do not prove that provider jobs are terminal. These source files were read only, not altered or cleared. The readiness JSON records the pending resource and draft hash without credentials.

Next concrete resolution: the owner signs in locally with `gcloud auth login arghawork3@gmail.com`. Use request-specific account/project settings; do not change global CLI defaults. Billing/API availability of the supplied project is still unverified because metadata access was denied. After authentication, recheck remote metadata and reconcile historical records, source ledger, relevant bucket operation records and the shared workflow lock. Do not infer completion from age or timeout. Then persist a durable single-global lock and submission ledger BEFORE uploading/submitting, including manifest hash,30 IDs, model/region/project, timestamps and operation ID. This draft/readiness file is not that submission lock. Submit one batch only; no fallback, regeneration or supplemental requests while active/unknown. Collect terminal outputs/errors, verify association/dimensions/hashes and review all results before closing the lock. Failed/rejected positions can enter a later full useful30 batch; no automatic paid retry.

## Review and handoff

First inspect generated home, Medieval city, Adventure, Tactical and icons at actual phone scale, then the remaining outputs once the batch is terminal. Keep provider originals and record any review-only text overlays separately. Do not claim generated imagery proves plot counts, touch targets, contrast, animation, combat legality or a state-aware renderer. One generated composition may drift from another; compare continuity and mark failures explicitly.

Owner feedback is recorded by section as pending/revision-needed/accepted. Nothing currently has owner acceptance. A blueprint or prompt is not finished visual art. Coding remains gated after section review and a later explicit instruction. Preserve the original game and raw-art folders read-only.
