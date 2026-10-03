> **HISTORICAL SCOPED REVIEW:** Preserve this earlier90-source/v1 review and rejection evidence. Current eight-batch/v2 coverage and applicable criteria are in [ALL-BATCHES-ASSET-AUDIT-2026-10-03.md](ALL-BATCHES-ASSET-AUDIT-2026-10-03.md) and [ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md](ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md); do not apply all-purpose/world gates to bounded UI use, treat missing review as stale bytes, or reject every static outskirts prop. Current Hall/Gold/scene defects remain real; four current UI uses have bounded artwork PASS. Runtime and owner acceptance remain separate.

# Generated asset validation and recovery — 3 October 2026

**The purchases are not all wasted.** Of 90 collected images, **53 pass a scoped review of source identity/motif/material/silhouette**, and **82 are recovery candidates** for their intended role or an explicitly identified alternative role. Eight fail as complete assets for the requested use. These are verifier findings, not owner approval. No production cutouts, edited terrain or registered composites were produced in this audit, so **zero assets pass the complete runtime delivery gate**.

The 82 candidates are conditional, not 82 finished usable assets. They include substantial terrain repairs, two alternative-role candidates that leave their original requirements open, and earlier attempts superseded by better existing sources. The 90 outputs represent **85 distinct original asset IDs**, because five identities were bought again in batch 03; the 53 source-content PASS outputs cover 52 distinct IDs. Do not add attempts, alternative roles or future local crops to the count of fulfilled baseline requirements.

## Current local evidence

|Batch|Saved job suffix|Saved provider state|Collected originals|Collection errors|
|---|---|---|---:|---:|
|01|7379059066443661312|SUCCEEDED|30|0|
|02|2260718089937092608|SUCCEEDED|30|0|
|03|3389643852779356160|SUCCEEDED|30|0|
|04|6905547786872160256|QUEUED, saved 3 October at 12:13:29 Asia/Calcutta|0 local collection evidence|Not assessed|

These are saved local records, not live provider verification. The owner-reported four submitted/three collected counts are supported locally. No query, monitoring, collection or resubmission of batch 04 occurred.

All 90 originals decode at their recorded dimensions and match their collection SHA256. Independently hashing each echoed request associates it with exactly one manifest item, and its raw response image matches the saved original byte-for-byte: **90/90 correct associations**. The Warlock village and club-on-village are genuine generated responses, not a swapped filename or collector mismatch. All 90 lack native alpha; **56 actually require alpha**. The other 34 are opaque terrain images and do not need transparency.

|Collected-output classification|Count|Meaning|
|---|---:|---|
|PASS|0|Complete intended delivery checks passed; none yet|
|RECOVERABLE|82|Existing source has a specific recovery or alternative-use path, with stated remaining work|
|FAIL|8|Demonstrably unsuitable as the complete intended asset; retain original for references/material salvage|
|UNVERIFIED|0|None entirely unseen at overview/source-content scope; fine delivery gates remain UNVERIFIED for all|

Every image was inspected in a batch/category contact sheet; 14 originals were additionally opened at full detail, and five original terrains were annotated with contract geometry. **53 source-content PASS and 37 source-content FAIL** concern original identity/motif/material/silhouette, not complete asset delivery. A content defect can be RECOVERABLE: for example a fully visible club over an unwanted village can be segmented. Conversely a village with no Warlock body cannot supply the requested full-body identity.

Machine ledger: [VERIFIER-REVIEW-20261003.json](image-production/VERIFIER-REVIEW-20261003.json). Per-item evidence, review level, intended role, reason, operations and remaining gates are recorded there. Batch lists: [01](../../assets/production/production-01-20261003/VERIFIER-REVIEW-20261003.md), [02](../../assets/production/production-02-20261003/VERIFIER-REVIEW-20261003.md), [03](../../assets/production/production-03-20261003/VERIFIER-REVIEW-20261003.md).

## Why nothing was approving

1. **Collection is intentionally technical only.** `scripts/vertex-production.py` writes every output as `reviewStatus: UNVERIFIED`, every runtime flag as false, and batch visual status as UNVERIFIED. That default is correct until review; it is not a visual rejection.
2. **Review findings were disconnected from those records.** `assets/production/VISUAL-REVIEW-2026-10-03.md` contains executor findings for 16 distinct outputs across three batches. Four were explicit UNVERIFIED and twelve were FAIL. The collection reports still contain 90 UNVERIFIED rows. Some review text combines genuine wrong content with missing alpha, floor/shadow or a compound footprint; these need distinct delivery gates.
3. **The benchmark cannot import human review.** `scripts/benchmark.py:110–120` checks originals, then unconditionally emits content/composite UNVERIFIED and false runtime flags. Rerunning it does not execute a visual review or consume any review ledger. It also labels checks/asset rows by original ID without batch/hash, making replacement attempts ambiguous. This is missing review integration, not evidence of a provider approval outage.
4. **There are no derived delivery assets or accepted composites.** Production folders contain originals and provider metadata, without reviewed RGBA cutouts, measured registration or composites. Geometry-only `render-check.json` explicitly excludes visual acceptance. Fifty-six opaque originals need matte delivery work. Exact-magenta keying will fail on the many rose/gradient backdrops and can erase real object colors.
5. **Several prompts fight their own intended uses.** Batch 03 Tactical prompts say “Exactly one river crossing. No second bridge.” and later request “Two stone decks” on lanes 3 and 7. Several outputs have only one bridge; the conflict is a plausible cause, not proven provider internals. The common aerial camera instruction is also applied to UI emblems, encouraging oblique plaques. Full scene references and visible guide marks appear to have contaminated isolated assets and terrain. Medieval reference gear contradicts the mounted Knight's requested ancient kit.
6. **Real content/registration defects remain.** Guide dots, pad outlines, baked actors/buildings, extra crossings and camera/landmark drift occur in multiple terrains. Annotated comparisons demonstrate them. `src/client/main.js:85` still hardcodes batch 01 Kingdom images; this audit does not change executor source or route new candidates into runtime.

## Existing results to retain and recover

|Source|Verifier finding|Remaining operation|
|---|---|---|
|03 / skill-offense|**Source content PASS**: front-facing square plaque, crossed blades and rendered material. Keeping a square plaque is consistent with the requested skill silhouette.|Remove exterior key/background/shadow; keep plaque opaque. Read-only non-key bounds approximately `[158,163,866,865]`; not a finished matte. Compare all nine skills after normalizing oblique earlier plaques.|
|03 / townhall-stone|**Source content PASS**: photoreal timber/thatch/hide Hall, better than batch 01. Dirt apron and shadow are processing issues.|Recover Hall and chosen ground-contact island; remove loose exterior soil. Non-key bounds `[0,20,1024,1010]` show edge-connected apron/top-margin failure. Measure the actual base after matte; `[512,790]` is only the requested guide pivot.|
|03 / farm-stone, lumber-stone, quarry-stone, mine-stone|**Source content PASS**: recognizable Stone producer compounds, no visible people. Several farm sheds constitute one farm-yard object.|RGBA derivatives, internal-hole/shadow checks, measured footprint/pivot, then one actual town-size composite. Mine is a ground working, not a tall building.|
|01 / four resources|**Source content PASS**: four distinct readable identities.|Matte, decontaminate reflected magenta on gold and fine basket/rope gaps, then actual 18px UI/ground-pickup checks. Wood needs segmentation of a rose backdrop.|
|02 / six actual class figures|**Source content PASS** at recorded review scale. Warlock excluded.|Remove rose floor/shadow, preserve hair/fur/bowstring/attachments and verify anatomy/detail at original size. They are identity paintings, not rigs or animations.|
|03 / gear-stone-weapon|Original scene content fails isolation, but the complete club is visible.|Segment one flint club and discard the entire village and exterior shadow. Batch 02 needs overlap reconstruction; prefer this existing attempt. No third purchase prescribed.|
|01 / kingdom-terrain-iron|Mostly bare plots align closely with the contract; material can be recovered.|Remove visible borders/markers; validate all 18 sites and independent perimeter. Use it as a topology comparison, not a substitute era for other ages.|
|01 / tactical-terrain|**Source content PASS** for the natural two-crossing scene.|Overlay shows L3 against water/bridge side and R1 on rock. Repair deployment clearance/approaches; passing scenery does not pass registered battle geometry.|

Examples: [Offense original](../../assets/production/production-03-20261003/images/04-skill-offense.png), [Stone Hall original](../../assets/production/production-03-20261003/images/03-townhall-stone.png), [producer source sheet](../../qa/asset-audit-20261003/03-objects.jpg), [portrait source sheet](../../qa/asset-audit-20261003/02-portrait.jpg), [registration comparisons](../../qa/asset-audit-20261003/registration-pairs.jpg).

Two conditional alternative-role recoveries **do not fill the original requirements**: the Iron Hall's mechanical clock tower might serve a later-era civic decoration; the armored/barded mounted Knight might serve a later-era reference. Ancient Knight and appropriate Iron Hall remain open. No asset is globally reclassified as that alternative or silently renamed.

Eight complete-role rejections: batch 01 Stone Hall; batch 02 ancient Warlock; batch 03 Medieval bare Kingdom terrain, Tactical desert/snow/waste/ruins, and Defense waste. Do not delete these originals. Their rejected roles do not imply that every texture fragment is useless, nor authorize replacement purchases.

## Exact executor continuation

Use [RECOVERY-SOURCE-REGISTRY-20261003.json](image-production/RECOVERY-SOURCE-REGISTRY-20261003.json) as a **review candidate registry**, not runtime-approved artwork. It binds 85 identities to batch/hash evidence and resolves five repeat-attempt choices: prefer batch 03 Hall, Offense and club; prefer batch 01 Stone/Medieval Kingdom topology over the more obstructed second attempts. All runtime/owner flags remain false/UNVERIFIED. The three originally unnamed mode terrains retain provisional forest associations until complete biome-kit review; do not treat the old counting assumption as accepted content.

First make the simplest recovery concrete: Offense cutout, the four resources and one producer/Hall derivative. Preserve original/hash, give each derivative its own hash/source binding, inspect on black/white/neutral green, and record actual matte/registration results. Actual production image editing/segmentation is left to the executor under the owner's role boundary and applicable image-editing tool requirements. This verifier made no image-edit or image-generation calls.

For each isolated base, record ground vertices `q00,q10,q01,q11`, footprint `(fw,fh)` and measured ground pivot. Derive source axes `B=[(q10-q00)/fw, (q01-q00)/fh]`, compare the fourth corner to the affine prediction, and place with `D=A*inverse(B)` for the scene camera `A`, with translation anchored at the target world footprint. Do not infer a ground pivot from image centre, non-key bounding box or guessed CSS percentage. If an affine fit visibly distorts the roof/body or cannot fit the fourth point, the source needs reprojection/reconstruction and another visual review.

Keep exact contract cameras: Kingdom `[60,-10,25,35,170,165]`, Adventure `[53,-8,23,37,180,160]`, Tactical `[77,-12,27,46,270,110]`, Defense `[60,-8,20,35,270,100]`. Bridge footprint centres in source pixels: Kingdom `(1150,291.5)`; Adventure `(594.5,360.5)`; Tactical `(634,229)` and `(742,413)`. The Adventure plains annotation shows the bridge displaced even when several site pads align; one CSS translation cannot align both. Restore the derived land/water/crossing to the fixed contract geometry or produce an explicit reviewed contract revision; never silently remap cells to accommodate an attractive image.

Terrain repair must produce a clean derivative with the same source bounds and shared Kingdom landmarks across all eight ages. Remove guide dots/outlines/actors and independent mutable structures. Recheck actual empty site footprint vertices, legal approach cells, walkable bridge decks, both Tactical crossings/deployment ground and complete Defense lane. Then compose sparse Stone, developed Medieval and the three mode scenes beside the approved direction at source size and the specified landscape viewports. Browser states, touch/contrast, motion and hardware remain separate later gates.

Review integration belongs to the executor: join persisted verifier reviews on `(batch,id,sourceSHA256)`, keep collection reports as immutable technical provenance, expose each separate gate, reject stale hashes and preserve review across recollection/benchmark reruns. Never infer owner approval from verifier source acceptance. Resolve derived source selection explicitly rather than hardcoded batch 01 paths. Fix the contradictory crossing boilerplate before preparing any future requests; no provider-ready prompt/manifests were changed here.

## Changes and checks actually made

- Added this report, a canonical verifier ledger, three batch review ledgers/Markdown lists and a candidate source registry. They record scoped source acceptance and exact remaining operations.
- Added offline inspection/diagnostic/review helpers and evidence in `qa/asset-audit-20261003/`: one contact sheet per batch/category, direction comparison, five registration annotations, local snapshot and independent 90-request association check. These are viewing/annotation evidence, not edited production artwork or accepted composites.
- Ran only offline source hash/decode/association and audit-artifact consistency checks: [20 checks PASS](../../qa/asset-audit-20261003/validation.json). No broad game tests/builds, provider calls, new submissions, collection, game-code changes, delegation, cleanup, automation, device actions or publishing. Originals, raw responses, manifests, existing reviews, budget holds and locks are preserved. Four status/handoff files received a new audit pointer with every prior byte retained; the active lock hash was unchanged before/after those documentation updates.
- Remaining production processing and game integration are specified for the executor. **53 scoped source-content passes can now be distinguished from the default false flags; 82 recovery candidates do not become finished accepted assets until their explicit gates pass.**

Evidence snapshots are time-specific. Other executor work may change the tree after this review; join reviews by recorded source hashes and verify current files before adopting them.
