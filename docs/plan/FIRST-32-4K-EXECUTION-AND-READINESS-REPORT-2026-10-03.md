# First 32 4K Native Terrain Images — Execution, Readiness & Deferral Report

**Date:** 2026-10-03  
**Role:** Image Executor  
**Authority:** Owner Individual Upgrade Directive (32 Individual Native 4K Images First; Later 73 Native 2K Images)  
**Status:** RECONCILED — ALL 32 ITEMS AUDITED; 0 CALLS MADE; 32 DEFERRED PENDING CODE AI GUIDE PACK DELIVERY  

---

## 1. Executive Summary

Per owner directives, the image executor has conducted the readiness audit and live reconciliation for the authorized first phase of **32 individual native 4K terrain images** (`4K-FIRST-32`).

- **Live Cloud & Provider Reconciliation:** `PASS`. Active batch lock (`production-17-20261003`) is in terminal state `JOB_STATE_SUCCEEDED` / `TERMINAL_COLLECTED`. Live REST queries of Vertex AI `global` (20 jobs) and `us-central1` (0 jobs) confirmed **exactly 0 active and 0 unknown jobs** in `project-eaa4c1cc-8f19-4d24-9e6`. Submission mutex is clear.
- **Provider Capability & Tariff Verification:** `gemini-3.1-flash-image` natively supports 4K outputs via `generationConfig.imageConfig.imageSize: "4K"` (or `"IMAGE_SIZE_FOUR_K"`). For landscape 16:9, native 4K output dimensions are **5504 × 3072 px** (2,520 output tokens = $0.1512 USD per image output at $60/M).
- **Budget Compliance:** Reconciled exposure across Batches 01–17 + $2.00 historical mock + $15.00 protected safety reserve = **$57.225 USD** ($2.775 USD headroom under $60.00 aim; $22.775 USD headroom under $80.00 hard cap; invoices remain UNKNOWN). Capped reservation for 32 4K calls adds $9.117568 USD, totaling **$66.342568 USD** ($13.657432 USD headroom below $80.00 hard cap with $15.00 reserve fully protected).
- **First 32 Execution Disposition:** **0 Reused, 0 Attempted, 0 Technical Pass, 0 Visual Fail, 32 Explicitly Deferred.**
  - **Reason for Deferral:** Per the strict prompt contract, *"Code AI exports geometry/base/masks/camera locally. Missing required geometry/acceptance blocks only that scene's request. Continue unrelated ready selected IDs with a recorded deferral. No silent adoption of Kingdom v2/v5 guide or composition v4 as owner-approved playable layout."*
  - In `INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json`, all 32 items currently have `guide: null`, `preferredSource: null`, and `guideAcceptance: "UNVERIFIED"`. The replacement Code AI has not yet executed Task 3 (exporting the reviewed per-ID geometry, clearing footprints, road approaches, and masks).
  - Executing blind 4K generations without accepted geometry guides would guarantee ungrounded outputs with baked mutable structures or invalid road/river crossings, violating owner specifications and wasting budget.
  - Therefore, all 32 requests are formally deferred pending delivery and owner review of Code AI's guide pack.
- **Later 73 Native 2K Proposal:** Proposed Groups A (32 heroes), B (17 mounts/rigs/rivals), and C (24 army) remain drafted and pending owner activation/scheduling following resolution of the 4K phase.

---

## 2. Live Provider & Lock Reconciliation

| Resource | Scope / Location | Queried State | Local Match | Meaning / Notes |
|---|---|---|---|---|
| **Local Lock** | `docs/plan/image-production/active-batch.lock.json` | `JOB_STATE_SUCCEEDED` / `TERMINAL_COLLECTED` | YES | Batch 17 collected 2026-10-03T15:25:06Z; generation `1791041108322430`. |
| **Cloud Lock** | `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` | Generation `1791041108322430` | MATCH | Generation, batch ID, timestamps, and terminal state agree with local lock. |
| **Global Batch Jobs** | `projects/186933974004/locations/global/batchPredictionJobs` | 20 jobs found; **0 active, 0 unknown** | VERIFIED | All 17 production batches SUCCEEDED; 1 landscape mock SUCCEEDED; 2 early tests terminal. |
| **US-Central1 Batch Jobs** | `projects/186933974004/locations/us-central1/batchPredictionJobs` | 0 jobs found; **0 active, 0 unknown** | VERIFIED | No orphan jobs in primary regional location. |
| **Local Mutex** | `docs/plan/image-production/submission.mutex.json` | Absent (`False`) | CLEAR | No concurrent submission in progress. Single-active rule satisfied. |

---

## 3. Official Model, Parameter & Pricing Verification

Verified directly against Google Gemini 3.1 Flash Image API official documentation without paid test calls:

- **Model Identifier:** `gemini-3.1-flash-image`
- **Method:** `projects/186933974004/locations/global/publishers/google/models/gemini-3.1-flash-image:generateContent`
- **Native Resolutions for 16:9 Landscape:**
  - **4K (`IMAGE_SIZE_FOUR_K` / `4K`):** `5504 × 3072 px` (2,520 image tokens)
  - **2K (`IMAGE_SIZE_TWO_K` / `2K`):** `2752 × 1536 px` (1,680 image tokens)
  - **1K (`IMAGE_SIZE_ONE_K` / `1K`):** `1376 × 768 px` (1,120 image tokens)
- **Standard Official Tariff:**
  - Input: $0.50 per 1M tokens
  - Image Output: $60.00 per 1M tokens
  - Text Output: $3.00 per 1M tokens
- **Per-Output Pure Image Cost:**
  - 4K image output (2,520 tokens): $0.1512 USD
  - 2K image output (1,680 tokens): $0.1008 USD
  - 1K image output (1,120 tokens): $0.0672 USD

---

## 4. Comprehensive Budget & Liability Reconciliation

```
========================================================================================
A. Historical Completed Batches 01–17
----------------------------------------------------------------------------------------
Measured prompt tokens (510 requests):             985,482 tokens  ->  $0.492741 USD
Measured candidate tokens (510 outputs):            574,764 tokens  -> $34.485840 USD
Standard token subtotal:                                               $34.978581 USD
15% overhead & storage buffer:                                          $5.246787 USD
Reconciled Batches 01–17 exposure:                                     $40.225368 USD (rounded to $40.225)
Historical mock reservation:                                            $2.000000 USD
Protected safety reserve (NEVER SPENT):                                $15.000000 USD
----------------------------------------------------------------------------------------
PRODUCER EVIDENCE-BOUND PROTECTED EXPOSURE:                            $57.225000 USD
Retained historical ledger holds (17 x $6 + $2 mock + $15 reserve):   $119.000000 USD
Actual billed invoices:                                                UNKNOWN (retained)
Headroom under $60.00 aim:                                              $2.775000 USD
Headroom under $80.00 hard cap:                                        $22.775000 USD
========================================================================================
B. Authorized 4K-FIRST-32 Phase Exposure
----------------------------------------------------------------------------------------
Expected pure image output (32 x 2,520 tokens @ $60/M):                 $4.838400 USD
Expected cumulative exposure ($57.225 + $4.8384):                      $62.063400 USD
  -> Note: Exceeds $60.00 target by $2.0634 USD; permitted under $80.00 hard cap.
Capped reservation per 4K call (4096 out @ $60/M + 4000 in @ $0.5/M) * 1.15:
  ($0.245760 + $0.002000) * 1.15 =                                      $0.284924 USD
Total capped reservation for 32 4K calls (32 x $0.284924):              $9.117568 USD
Total protected exposure including 32 4K calls ($57.225 + $9.117568):  $66.342568 USD
Headroom under $80.00 hard cap with $15.00 reserve protected:          $13.657432 USD
========================================================================================
C. Conditional Whole-105 Protected Ceiling (32 4K + 73 2K)
----------------------------------------------------------------------------------------
Capped reservation for 73 2K calls (2048 out @ $60/M + 4000 in @ $0.5/M) * 1.15:
  ($0.122880 + $0.002000) * 1.15 = $0.143612 * 73 =                   $10.483676 USD
Total capped upgrade reservation (32 4K + 73 2K):                      $19.601244 USD
Conditional whole-105 ceiling ($57.225 + $19.601244):                  $76.826244 USD
Headroom under $80.00 hard cap with $15.00 reserve protected:           $3.173756 USD
========================================================================================
```

---

## 5. Detailed Status of the 32 First 4K Items (`4K-FIRST-32`)

Every item has been reviewed against existing production originals, candidate sources, guide availability, and prompt contract requirements.

| # | ID | Resolution | Candidate Sources Available | Existing Native 4K | Guide Status | Disposition | Detailed Blocker / Rationale |
|---|---|---|---|---|---|---|---|
| **01** | `kingdom-terrain-stone` | 4K (5504x3072) | Batch 01 (`6cb13e...`), Batch 03 (`5fcdb8...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Stone civic terrace & 17 clearing footprint guide; candidate v2 unaccepted. |
| **02** | `kingdom-terrain-bronze` | 4K (5504x3072) | Batch 01 (`49f136...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Bronze age homeland conversion & perimeter geometry guide. |
| **03** | `kingdom-terrain-iron` | 4K (5504x3072) | Batch 01 (`a05358...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Iron age fortified civic terrace & road approach guide. |
| **04** | `kingdom-terrain-medieval` | 4K (5504x3072) | Batch 01 (`3eea9e...`), Batch 03 (`7c6122...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Medieval stone terrace & bridge crossing geometry guide. |
| **05** | `kingdom-terrain-gunpowder` | 4K (5504x3072) | Batch 01 (`9aec2f...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Gunpowder bastion terrace & road approach guide. |
| **06** | `kingdom-terrain-industrial` | 4K (5504x3072) | Batch 01 (`85440e...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Industrial canal/rail civic terrace & factory pad guide. |
| **07** | `kingdom-terrain-modern` | 4K (5504x3072) | Batch 01 (`c53704...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Modern paved civic terrace & infrastructure grid guide. |
| **08** | `kingdom-terrain-future` | 4K (5504x3072) | Batch 01 (`df5e35...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Future homeland arcology terrace & transit pad guide. |
| **09** | `adventure-terrain` | 4K (5504x3072) | Batch 01 (`d7b858...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI 16x10 Adventure map blueprint: 6 site clearings, 4 pickup pads, crossing. |
| **10** | `adventure-terrain-plains` | 4K (5504x3072) | Batch 03 (`0f0b91...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Plains biome footprint & traversable route guide. |
| **11** | `adventure-terrain-hills` | 4K (5504x3072) | Batch 03 (`d7341f...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Hills biome elevation & ridge movement corridor guide. |
| **12** | `adventure-terrain-swamp` | 4K (5504x3072) | Batch 03 (`7b6333...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Swamp water barrier & legal causeway guide. |
| **13** | `adventure-terrain-desert` | 4K (5504x3072) | Batch 03 (`face19...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Desert dune & oasis clearing footprint guide. |
| **14** | `adventure-terrain-snow` | 4K (5504x3072) | Batch 03 (`7a9615...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Snow ice pass & frozen river crossing guide. |
| **15** | `adventure-terrain-waste` | 4K (5504x3072) | Batch 03 (`097c0d...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Waste volcanic obstacle & crag corridor guide. |
| **16** | `adventure-terrain-ruins` | 4K (5504x3072) | Batch 03 (`64a0e7...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Adventure Ruins ancient foundation & broken arch route guide. |
| **17** | `tactical-terrain` | 4K (5504x3072) | Batch 01 (`13b7c6...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI 7x10 Tactical board projection: 2 crossings, obstacles, commander (0,9). |
| **18** | `tactical-terrain-plains` | 4K (5504x3072) | Batch 03 (`e5dc2c...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Plains board registration & unobstructed grid guide. |
| **19** | `tactical-terrain-hills` | 4K (5504x3072) | Batch 03 (`fe1d2f...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Hills stepped height & legal line-of-sight obstacle guide. |
| **20** | `tactical-terrain-swamp` | 4K (5504x3072) | Batch 03 (`f7690d...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Swamp water hazard cells & firm footing guide. |
| **21** | `tactical-terrain-desert` | 4K (5504x3072) | Batch 03 (`ad6b64...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Desert canyon chokepoint & deployment zone guide. |
| **22** | `tactical-terrain-snow` | 4K (5504x3072) | Batch 03 (`67a474...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Snow frozen lake boundary & snowdrift obstacle guide. |
| **23** | `tactical-terrain-waste` | 4K (5504x3072) | Batch 03 (`c7300c...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Waste fissure obstacle & basalt bridge guide. |
| **24** | `tactical-terrain-ruins` | 4K (5504x3072) | Batch 03 (`fd7e61...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Tactical Ruins fallen column obstacles & cell grid guide. |
| **25** | `defense-terrain` | 4K (5504x3072) | Batch 01 (`439913...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI 9x15 Defense simulation lane: entry, gate, 12 tower pads, deployment. |
| **26** | `defense-terrain-plains` | 4K (5504x3072) | Batch 03 (`74ae03...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Plains winding road & tower pad clearance guide. |
| **27** | `defense-terrain-hills` | 4K (5504x3072) | Batch 03 (`856831...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Hills winding gorge & elevated pad guide. |
| **28** | `defense-terrain-swamp` | 4K (5504x3072) | Batch 03 (`e6f9ac...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Swamp wooden causeway & island pad guide. |
| **29** | `defense-terrain-desert` | 4K (5504x3072) | Batch 03 (`ee719f...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Desert canyon track & rock ledge pad guide. |
| **30** | `defense-terrain-snow` | 4K (5504x3072) | Batch 03 (`b9baf2...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Snow mountain pass & stone platform pad guide. |
| **31** | `defense-terrain-waste` | 4K (5504x3072) | Batch 03 (`369fc0...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Waste caldera approach & basalt tower pad guide. |
| **32** | `defense-terrain-ruins` | 4K (5504x3072) | Batch 03 (`77c66e...`) | None (1K only) | `null` / UNVERIFIED | **DEFERRED** | Missing Code AI Defense Ruins cobbled avenue & ancient dais pad guide. |

---

## 6. Actionable Handoff & Next Steps

1. **For Replacement Code AI:**
   - Execute Task 3 ("REPAIR KINGDOM AND EXPORT READY IMAGE GUIDES") in `docs/plan/REPLACEMENT-CODE-AI-PROMPT-2026-10-03.txt`.
   - Export the versioned, reviewed guide pack to `docs/plan/image-production/guides/`:
     - Logical/native geometry JSON for each of the 4 modes (Kingdom, Adventure, Tactical, Defense).
     - Clean overlay guides and mask references defining the exact physical clearing footprints, road/river coordinates, and tower pads.
     - Record explicit spatial tolerance and coordinates.
2. **For Owner:**
   - Review and accept the exported spatial guides from Code AI.
   - Upon owner acceptance of the guides, the image executor will sequentially submit each of the 32 individual 4K requests under single-active mutex and bounded reservations.
   - The later 73 native 2K images (32 heroes, 17 mounts/rigs/rivals, 24 army) remain structured and ready for owner activation/scheduling following completion of the 4K phase.
