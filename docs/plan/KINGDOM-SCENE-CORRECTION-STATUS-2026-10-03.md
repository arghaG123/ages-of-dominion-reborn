> **Closing local refresh — 3 October 2026, approximately19:50 IST:** 01–15 now contain450 originals/445 IDs; all450 hashes match. Batch16 is saved PENDING/PROVIDER_ACTIVE, submitted19:43:03 IST; live state not queried. Current retained16-batch holds+mock/reserve sum113USD. Producer47.856USD reconciliation still covers01–13 only; invoices unknown. This supersedes420/15-pending/107USD snapshot below. Current candidate/gameplay findings and next prompt are unchanged. Planner QA/docs only.

> **Independent candidate audit — 3 October 2026, approximately19:45 IST:** Read [the current audit](KINGDOM-CANDIDATE-PLANNER-AUDIT-2026-10-03.md) and [next coding/recovery prompt](CODING-RECOVERY-POST-CANDIDATE-PROMPT-2026-10-03.txt). Fresh scoped verification:8 tests PASS; all18 candidate site centres pick at four landscape sizes; Hall/contract/guide hashes, uniform.34 envelope, road exclusion and saved package hashes PASS. Candidate remains NOT_OWNER_ACCEPTED: physical threshold/base survey incomplete, actual preview chrome92px differs from metadata112px,14 mature rectangle pairs overlap and tabletP11 partly sits under the panel. Current terrain/composite FAIL. New local evidence supersedes390/unsubmitted14/ungenerated-scene claims:01–14 collected420 originals/415 IDs with all hashes matching;15 saved PENDING/PROVIDER_ACTIVE at19:33:20 IST, live state not queried. Kingdomv4 already generated in14 against a different guide still labelled NOT_OWNER_ACCEPTED; input lacks Hallv3 image. Output improves Stone scene art but crossing/river spatial fidelity FAIL; preserve as reference, no automatic repurchase or runtime adoption. Saved benchmark537PASS/1budgetFAIL covers390; retained15-batch holds+mock/reserve sum107USD, producer47.856 reconciliation covers01–13 only; invoices unknown. Malformed battle-save and remote-melee probes expose incomplete Tactical legality; Defense/textured rigs/five War choices remain incomplete. Positive morale stays PENDING_OWNER_DECISION. Planner wrote QA/docs only; no provider/game/recovery/build/device/budget edits or executor delegation/messages. Historical text follows.

# Corrected Stone-Age Day 1 Kingdom Scene Status & Preparation Record
**Date**: 3 October 2026  
**Request ID**: `kingdom-stone-day1-composition-v4`  
**Status**: **GUIDE_READY_FOR_REVIEW_NOT_OWNER_ACCEPTED**  
**Document Ref**: `docs/plan/KINGDOM-SCENE-NEXT-BATCH-HANDOFF-2026-10-03.md`  
**Draft Manifest**: `docs/plan/image-production/batch-14-manifest-draft.json` (Position 30)  
**Draft Readiness**: `docs/plan/image-production/batch-14-readiness-draft.json`

---

## 1. Owner Directive & Constraint Verification

The owner explicitly instructed:
> *"Prepare one corrected Stone-age Day 1 Kingdom scene in the next available authorized batch.*  
> *If production14 is still unsubmitted, replace position30, gear-industrial-boots, with kingdom-stone-day1-composition-v4. Keep exactly30 useful requests. Preserve Industrial boots in the outstanding backlog. Never modify a submitted batch or start an additional batch14 under this instruction.*  
> *Read: C:\dev\ages-of-dominion-reborn\docs\plan\KINGDOM-SCENE-NEXT-BATCH-HANDOFF-2026-10-03.md*  
> *Before generation: Use a corrected, versioned spatial guide that accounts for the Hall’s physical foundation, entrance and full roof height. The previous layout clips a correctly sized Hall. Do not reuse that incompatible guide, shrink the Hall to hide clipping, or apply the rejected +193px translation. If the corrected guide is unavailable, keep this request pending.*  
> *Preserve the existing project/model, one-active-or-unknown rule, budget limits and stop-on-quota rules. Do not repeat collected batches."*

### Current Live & Local State Audit:
1. **`production-13` Live/Local State**:
   - Provider Job: `projects/186933974004/locations/global/batchPredictionJobs/2619440355568779264`
   - Terminal State: `JOB_STATE_SUCCEEDED`
   - All 30 outputs downloaded, hash-verified, and collected locally at `assets/production/production-13-20261003/images/`
   - Position 30 (`gear-industrial-boots`) was successfully generated and verified on disk at `assets/production/production-13-20261003/images/30-gear-industrial-boots.png`.
2. **`production-14` Submission Status**:
   - `production-14` is **unsubmitted**.
   - No Batch 14 provider job has been created or started.
   - Strict enforcement of *"Never modify a submitted batch or start an additional batch14 under this instruction"*: Batches 01–13 remain completely immutable; Batch 14 is held strictly unsubmitted.
3. **Backlog Integrity**:
   - `gear-industrial-boots` is already fulfilled and preserved on disk from Batch 13, and remains tracked in the full purchase inventory.
   - In the prepared unsubmitted Batch 14 draft (`batch-14-manifest-draft.json`), exactly 30 useful requests are maintained: Positions 01–29 hold unrequested equipment from Industrial, Modern, and Future eras, and Position 30 holds `kingdom-stone-day1-composition-v4`.

---

## 2. Spatial Guide Gate (Pre-Generation Prerequisite)

The owner instructed:
> *"Before generation: Use a corrected, versioned spatial guide that accounts for the Hall’s physical foundation, entrance and full roof height. The previous layout clips a correctly sized Hall. Do not reuse that incompatible guide, shrink the Hall to hide clipping, or apply the rejected +193px translation. If the corrected guide is unavailable, keep this request pending."*

### Spatial Guide Status:
1. **Historical Guide Clipping**: `guides/townhall-stone.png` places the full Hall roof extremity at `y = -185.23` (clipping 385,665 opaque pixels outside the 768px frame).
2. **Rejected Translation**: The diagnostic +193px downward shift was rejected because it exposes missing upper canvas terrain and clips lower foreground scenery.
3. **Rejected Heuristic Proposal**: The framing proposal at `qa/recovery-executor-20261003/stone-framing-proposal.json` remains marked `"status": "PROPOSAL_NOT_ACCEPTED"`; its 0.3288 footprint scale shrank the building artificially to force a fit.
4. **Review candidate now on disk**: `qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png` and `kingdom-stone-day1-composition-v4-guide.json`. Status **READY_FOR_REVIEW / NOT_OWNER_ACCEPTED**. It records the measured roof, plinth, entrance cobble, 18 sites, roads, crossing, and the missing terrace. The active contract and the batch manifests were not edited.
5. **Outcome**: `kingdom-stone-day1-composition-v4` stays ungenerated until the owner accepts this guide. Acceptance of the guide is separate from authorizing a batch to paint it.

---

## 3. Prepared Specification for Next Authorized Batch (Batch 14 Draft)

In `docs/plan/image-production/batch-14-manifest-draft.json`, Position 30 is prepared as follows:

```json
{
  "position": 30,
  "id": "kingdom-stone-day1-composition-v4",
  "kind": "kingdom-scene",
  "mode": "kingdom",
  "age": "stone",
  "aspect": "16:9",
  "prompt": "Create ONE landscape 16:9, high-detail strategy-game composition reference for Ages of Dominion: Stone Age Kingdom, Day 1. Use the corrected spatial guide for layout. Use the approved landscape Day 1 reference for composition and material finish only. Use the preserved Hall v3 for Stone architectural identity. Show exactly ONE completed building: a prominent Stone Town Hall made from timber, hide, thatch, flint and rough stone foundations. Place it naturally on the upper civic terrace. Preserve its proportions and show its complete roof, foundation and entrance approach. It must be visibly grounded, with coherent perspective and contact shadows—not tiny, floating, stretched or sitting on a pasted ground island. Show 17 empty, usable building clearings connected by natural soil paths. Keep their footprints and approaches free of buildings, actors, logs and material stacks. No outlined rectangles, signs, plus marks, labels or visible grid. The perimeter is unbuilt: no completed walls, defensive towers or built gate. Keep a readable perimeter route and future entrance area. Include a river on the right, an age-appropriate crossing, connected roads, rocky hills and richly textured forest margins, following the corrected guide. Decorative outskirts must stay outside reserved plots and routes. Use a coherent high aerial three-quarter camera, warm upper-left daylight and consistent short shadows. Render complete terrain around the Hall without clipping required sites or scenery. No medieval church, spires, cannon, steel architecture, mature city, extra active buildings, gameplay HUD, text, numbers, buttons, watermark or guide marks.",
  "styleReference": "02-kingdom-day1.jpg",
  "guide": "guides/kingdom-stone-day1-v4-pending.png",
  "requiredAlpha": false,
  "reviewStatus": "UNVERIFIED",
  "attempt": 4,
  "requestedOutputs": 1,
  "reviewCriteria": "Inspect actual pixels for Stone identity, one Hall/17 empty plots/unbuilt walls, civic prominence, natural grounding, consistent camera, clear routes and full framing. Check proposed display framing at 825x375, 933x424, 1180x820, and 1280x720. Record PASS/FAIL/UNVERIFIED with evidence. Do not declare a pass from successful generation alone.",
  "styleReferenceSHA256": "629dff52e46e85741604a37f59453c072b22ecdf56f71d50937a549e32a677bf",
  "promptSHA256": "fcfa51fa76d8dfad86a4ea110ec94ca6fa2be8a3b53f6a27e3ff6eec08db832d",
  "guideSHA256": null,
  "generationPrerequisiteStatus": "PENDING_ACCEPTED_SPATIAL_GUIDE"
}
```

### Reference Pipeline:
1. **Reference 1 (Spatial Guide)**: To be supplied by coding/recovery AI once measured and accepted (target filename: `guides/kingdom-stone-day1-v4-pending.png`).
2. **Reference 2 (Style & Material Finish)**: `design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/02-kingdom-day1.jpg` (SHA256: `629dff52e46e85741604a37f59453c072b22ecdf56f71d50937a549e32a677bf`).
3. **Reference 3 (Architectural Identity)**: Preserved Hall v3 `assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png` (SHA256: `f359a8b72100be8ad78eaf61eede19bc8b2db3bd0a1d071050a51edce22cc37c`).

---

## 4. Review Protocol After Collection

When generation is authorized and output collected:
1. **Pixel Inspection Criteria**:
   - **Stone Identity & Day 1 State**: Exactly 1 completed Stone Town Hall; 17 empty, usable clearings; walls level 0 (no completed walls, towers, or gate); no church, spires, cannons, or mature structures.
   - **Civic Prominence & Natural Grounding**: Dominant civic terrace; preserved Hall proportions; complete unclipped roof, foundation, and entrance approach; coherent perspective and contact shadows.
   - **Clear Map & Routes**: Footprints and path connections readable without guide marks, labels, or baked HUD. River-right and natural crossings intact.
2. **Display Framing Verifications**:
   - Proposed display framing must be evaluated at four contract landscape viewports:
     - `825×375` (Compact phone landscape)
     - `933×424` (Standard phone landscape)
     - `1180×820` (Tablet landscape)
     - `1280×720` (Standard HD 16:9 landscape)
   - Record **PASS / FAIL / UNVERIFIED** with pixel crop evidence.
   - Generation success does NOT constitute visual or runtime approval.
3. **Lifecycle Separation**:
   - This output is a **composition-review image**.
   - Playable runtime delivery still requires separate terrain and buildings, authoritative picking/registration, and browser verification.
   - All existing originals and repaired artwork are preserved; failures are not automatically regenerated.

---

## 5. Operational, Mutex, and Budget Summary

- **Provider Jobs Across GCP**: 0 active, 0 unknown across all 48 locations.
- **Production Batches Completed**: Batches 01–13 are 100% completed, terminal `JOB_STATE_SUCCEEDED`, and collected (390 originals intact).
- **Budget Reconciliation**:
  - Reconciled 13-batch liabilities: $30.87 USD ($30.856 USD buffered)
  - Historical mock hold: $2.00 USD
  - Safety reserve: $15.00 USD
  - Total committed: $47.856 USD
  - Remaining Target ($60 USD) headroom: $12.144 USD
  - Remaining Hard Cap ($80 USD) headroom: $32.144 USD
  - Projected Batch 14 commitment (when authorized): $47.856 + $6.00 = $53.856 USD (well within $60 target).
- **Compliance Status**:
  - `production-13` remains immutable.
  - `production-14` is NOT submitted and NOT started.
  - Request `kingdom-stone-day1-composition-v4` is prepared in `batch-14-manifest-draft.json` at Position 30 (30 useful requests total), with execution held pending the accepted spatial guide and owner batch authorization.
