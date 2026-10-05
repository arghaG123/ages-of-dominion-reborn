# Background removal: keep or regenerate audit — 4 October 2026

## Decision

The newest saved matte review is v4, not the v2 snapshot. I inspected the actual v4 2048px derivatives, the white/black/neutral-green detail composites, the 50px and 64px consumer composites, and the current Code mounted-review capture. At 64px, accept small contact shadows and faint floor hairlines when they do not change the role or silhouette. Do not accept large diorama/platform slabs, a scene fragment attached to the subject, a wrong role, or damage to anatomy. No new paid calls are authorized by this audit.

The current v4 checker was refreshed after the 18:03 consumer exports and appropriately keeps `setClean:false`; its per-ID `meets` list now includes gunpowder-heavy and future-ranged. The older prose banner/handoff still says their fixes are pending and still describes the motor/future-transport/future-heavy remnants as open without considering their 64px scale. This report adds that consumer-size judgment while preserving the native-detail residual descriptions.

## Per-ID consumer decisions

| ID | 64px evidence / severity | Decision |
|---|---|---|
| `troop-stone-melee` | The detail composite retains a broad, sharply rectangular rocky diorama around both boots. At 64px it still reads as ground attached to the unit. Tightening the cut previously damaged soles/shins. | **REGENERATE_CANDIDATE** for a standalone Stone melee figure. Preserve current connected-boot v4 output as the safer reference until a funded replacement is authorized. |
| `troop-stone-ranged` | A wide wooden platform and gravel shelf remain below the intact legs and boots. At consumer size it is a prominent base, not a subtle contact shadow. | **REGENERATE_CANDIDATE** for a standalone Stone ranged figure. Earlier wood keying damaged boot leather; preserve the intact-boot source derivative. |
| `troop-gunpowder-heavy` | New detail and consumer composites show the cobble plane removed; cannon barrel, carriage, and both wheels remain. A small blue contact mark beside a wheel is visible only at detail and reads as a minor shadow at 64px. | **KEEP** v4 for a single static unit. No further floor cut is justified by the display evidence. |
| `troop-future-ranged` | The new composites show one standing soldier, intact helmet, and no neighbor rectangle. A little pale ground remains immediately at the boots. | **KEEP** v4 for a static unit at current consumer size; the remaining contact patch is minor. Do not erase the boot edge chasing it. |
| `hero-mount-horse` | Hooves are present; filled grey plane is gone. A thin polygon edge remains in native detail. At 64px it does not dominate. Code's current mounted screenshot uses this one-pose image, with a painted rider. | **KEEP** as a static review mount. No gait claim: hooves are not separated and the source has only one pose. Keep art/background acceptance separate from the screenshot's rider scale, world placement, path and underlying schematic map. |
| `hero-mount-motor-transport` | Remaining grey ground at the left/bottom is visible on the neutral composite but is a small fringe at 64px; wheels remain. | **KEEP** for the current small static consumer. Do not bind as a freely composited/animated vehicle until a later larger-size pass confirms the fringe is harmless. |
| `hero-mount-future-transport` | Pale ground remains under the craft; the 64px composite reads primarily as the vehicle and thrusters, with a modest underbody patch. | **KEEP** for the current small static consumer; retain thruster glow and shadow. Recheck if rendered materially larger. |
| `troop-future-heavy` | Dark under-hull shadow and blue thruster glow remain. At 64px they read as a coherent hover shadow/glow, not a floor slab. | **KEEP** for the current small static consumer. Preserve glow; no tighter cut recommended. |
| `troop-modern-ranged` | A snow patch remains under a single prone sniper. It is visible at 64px and makes the image terrain-specific, but the soldier and rifle silhouette remain intact. | **LOCAL_REPAIR** only if the snow can be separated while preserving the prone body/rifle. Otherwise keep it as a snow-scene illustration, not a general transparent unit; no paid regeneration recommendation yet. |
| `troop-industrial-ranged` | The saved full-body/detail composites show a prone soldier, sandbag, rifle, residual pink smear and fragments of caption-sheet composition. It is not the selected standing ranged role. | **REGENERATE_CANDIDATE** for the standing Industrial ranged role. A local matte can remove detached label/smear only; it cannot change the pose or remove attached props without damaging the subject. |
| `troop-iron-melee` | Existing selected source is a stencil rather than the intended Legionary. | **REGENERATE_CANDIDATE** for the selected role; use the separately named authentic v3 Legionary substitution for bounded static review meanwhile. |
| `troop-industrial-heavy` | Existing selected source is a gunner rather than the intended Steam Walker. | **REGENERATE_CANDIDATE** for the selected role; use the separately named v3 Steam-Walker substitution for bounded static review meanwhile. |
| `knight-mounted-master` | Scenic medieval mounted painting does not depict the selected ancient knight card/world-unit role. | **KEEP_WITH_ROLE_REJECTION** as reference art; do not relabel. Any later replacement must explicitly request the ancient role and intended card/world framing. |

The eight rows already marked clean in the current v4 check (`troop-bronze-melee`, `troop-bronze-ranged`, `troop-iron-ranged`, `troop-iron-heavy`, `troop-gunpowder-melee`, `troop-gunpowder-ranged`, `troop-modern-melee`, `troop-future-melee`) were not reprocessed. Their status here is inherited as a bounded existing review, not a fresh exhaustive class or gameplay acceptance. Other automatically keyed/unreviewed rows remain **UNVERIFIED**. No blanket clean-set conclusion follows.

## If the owner later authorizes a bounded regeneration

These are acceptance briefs only. They do not authorize provider calls, define a new cost ceiling, or select a model/output size.

| Candidate role | Why local recovery is insufficient | Required camera and composition | Required matte/geometry/identity checks |
|---|---|---|---|
| Stone melee | Ground rock shares nearly the same color/luminance as tan boot leather; previous keys either preserve the large base or remove/fragment the sole. | One complete standing Stone melee fighter, full figure in frame, three-quarter front view; both boots visible and separated from the frame edge. | Alpha background; no plinth, rocks, captions, border, neighboring figure or floor sheet. Preserve both legs, boot silhouettes, hand-held weapon and correct Stone melee kit. Verify no clipped extrema and stable feet at 50/64px over white, black and neutral green. |
| Stone ranged | Wood/gravel platform is broad and attached under/around the intact boots; the tested key punched holes in boot leather. | One complete standing Stone ranged fighter with the intended ranged weapon, full figure in frame, same readable three-quarter camera and both boots visible. | Alpha background; no wood, gravel, captions, border or second pose. Correct ranged-role identity, intact weapon and both boots; no ground patch larger than a restrained contact shadow at 64px. |
| Industrial ranged | The painted subject is prone with a sandbag and rifle, so local masking cannot create the selected standing class/pose. | One standing Industrial-era ranged soldier, full figure, three-quarter front view, rifle held naturally, feet visible; one pose only. | Alpha background; no sandbag, caption sheet, pink/magenta fringe or collateral soldier. Industrial uniform/weapons must be distinct from modern/future kits. Check hand-to-rifle contact, anatomy, full silhouette and 50/64px read. |
| Iron melee (if the existing authentic v3 substitution later proves insufficient) | Selected source is a stencil, not a Legionary painting. | One full-body standing Iron Legionary, three-quarter view, weapon and shield readable, boots fully visible. | Correct Legionary identity, no second figure/stencil diagram/text, clean alpha, no floor, hands securely contacting equipment; 50/64px proof. Current authentic v3 substitution remains the keep option, so this is lower priority. |
| Industrial heavy (if the existing authentic v3 substitution later proves insufficient) | Selected source is a gunner rather than a Steam Walker. | One complete Steam Walker machine, three-quarter view, all feet/track/wheel contact points in frame and visibly attached to the chassis. | Correct Steam Walker identity, no gunner, labels, base, floor or adjacent machine; clean alpha and intact mechanical silhouette; 50/64px proof. Current authentic v3 substitution remains the keep option, so this is lower priority. |

For every future candidate, require source/output hashes, decoded native output, transparent-alpha channel inspection, full-resolution and 50/64px composites on white/black/neutral backgrounds, and explicit identity/limb/contact-point inspection. No crop may hide a missing foot, neighboring figure, caption, or role mismatch.

## Acceptance layers

| Layer | Result |
|---|---|
| Native source and v4 output files | Present locally; earlier hash/decode binding records are technical provenance only. |
| Matte/content at native detail | **FAIL** for Stone melee/ranged and Industrial ranged; residual environmental pixels for several other rows. |
| Intended 50/64px consumer | **PASS bounded KEEP** for gunpowder-heavy, future-ranged, horse, motor/future transport, future-heavy at small static scale. Stone slabs and Industrial wrong pose remain material failures. |
| Spatial/composite | Code mounted screenshot shows the horse/rider over a diagram grid, not the final natural Adventure environment. That's a scene/scale/composition issue, not evidence of a grey horse background. |
| Animation/rig | Horse is one image, no separated hooves or gait. Other actor rigs remain separately incomplete. |
| Runtime/package | Current APK hash refreshed as `04c662556e21f3ca6f25752c8f44427756481d59fc5e05949409bc118594de1a` (297,724,620 bytes); this only identifies the saved package. No install/device check. |
| Owner acceptance | **UNVERIFIED**. |

Evidence: `qa/image-v4-repair-20261004/actors/*_detail_white_black_green.png`, `*_consumer50.png`, `*_consumer64.png`; `qa/code-ready-20261004/followup/02-mounted-review.png`; current code package at `android/app/build/outputs/apk/release/app-release-unsigned.apk`.

## Bounded next work prompts (not dispatched)

### Image AI prompt

Continue only local, source-preserving work using this audit and the existing v4 prompt. First reconcile `qa/image-v4-repair-20261004/requirement-check-v4.json` against the newest v4 composites, specifically the now-removed Gunpowder cobbles, Future ranged neighbor, horse plane, motor/future transport floors, and Future heavy shadow. Keep all eight previously accepted rows untouched. Keep the connected-boot Stone melee and intact-boot Stone ranged derivatives if further cutting damages anatomy; record their prominent residual slabs as failures. Clean only detachable industrial caption/smear components if separable, but retain the explicit prone/wrong-role failure. Do not query providers, alter production sources, call/regenerate/retry, edit game/native code, build, query a device, use Git/storage, message another executor, or delegate. Do not claim the set clean. Return refreshed per-ID native/detail/64px classifications and exact changed-file list. Paid replacement candidates in this audit require a later separate bounded owner budget authorization; no generation is part of this prompt.

### Code AI prompt

Preserve current ready Code functionality and existing package/evidence. Use this audit's per-ID decisions when selecting current artwork. Keep the static v4 horse sample only as a review image; do not claim gait or final Adventure acceptance. Do not bind the Stone melee/ranged slabs or Industrial prone scene as general actors. The authentic Legionary and Steam-Walker substitutions remain role-specific static review plates; keep other wrong-role sources withheld. Separate a matte/fringe problem from code scaling, cropping, placement, path, and baked-scene issues in any next screenshots. Do not alter image-production/accounting files, submit paid work, or use a device. Device testing stays STOPPED. Continue already authorized ready Code tasks and report newly changed files with their own tests/build status; this prompt conveys no new paid, native, or device authority.
