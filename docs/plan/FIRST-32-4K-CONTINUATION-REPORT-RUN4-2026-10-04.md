# First 32 Native 4K Terrain Images — Continuation Run 04 Report

**Date:** 2026-10-04  
**Role:** Owner-Selected Image Generation Executor  
**Authority:** Owner Directive (*"When you getting 429 wait 60 sec then work. Also after each image generation give gap of 30 sec."*)  
**Run ID:** `run-04-20261004-013946` (linked to `run-01-20261003-172733`, `run-02-20261004-010239`, and `run-03-20261004-012700`)  
**Status:** **RUN TERMINAL & FULLY RECONCILED — ALL 5 REMAINING DEFENSE TERRAINS SUCCEEDED (22 CUMULATIVE NATIVE 4K PASS, 5504×3072)**  

---

## 1. Executive Summary

In strict accordance with the owner directive (*"When you getting 429 wait 60 sec then work. Also after each image generation give gap of 30 sec."*), Continuation Run 04 (`run-04-20261004-013946`) was executed live against Google Vertex AI `gemini-3.1-flash-image` (native 4K 16:9, individual `generateContent` calls):

1. **Order 28 (`defense-terrain-swamp`):**
   - Attempt 1: **SUCCESS** (33.7s). Dimensions: `5504×3072 px`, SHA: `380a0cc2343985d064cfb689a9fecb439c362145e69e06822c9597bb4c9f1311`. Cost: $0.1524 USD.
   - Pacing: 30-second post-generation gap enforced before next request.
2. **Order 29 (`defense-terrain-desert`):**
   - Attempt 1: Encountered `HTTP 429: Resource Exhausted`.
   - **Backoff Enforced:** Waited **60 seconds** as instructed by user.
   - Attempt 2: **SUCCESS** (32.6s). Dimensions: `5504×3072 px`, SHA: `7da55fccca84bc1334057861cb7061d368e7ec2747ce6c0bf8f9c162234058d8`. Cost: $0.1524 USD.
   - Pacing: 30-second post-generation gap enforced before next request.
3. **Order 30 (`defense-terrain-snow`):**
   - Attempt 1: **SUCCESS** (36.7s). Dimensions: `5504×3072 px`, SHA: `514ad172d646a9d1646271c632aa6c4644a56c429712a7fa5fa590b533e4bbd6`. Cost: $0.1524 USD.
   - Pacing: 30-second post-generation gap enforced before next request.
4. **Order 31 (`defense-terrain-waste`):**
   - Attempt 1: **SUCCESS** (33.7s). Dimensions: `5504×3072 px`, SHA: `c165d958c68f052db5c249a7a92fa88fc1b9e28935ebaa1df5ddf552f53443e4`. Cost: $0.1524 USD.
   - Pacing: 30-second post-generation gap enforced before next request.
5. **Order 32 (`defense-terrain-ruins`):**
   - Attempt 1: **SUCCESS** (38.2s). Dimensions: `5504×3072 px`, SHA: `71ecaf6c98b90bd933227a921d227bda078170c0c05fe9e623c21c7be770bc1b`. Cost: $0.1524 USD.

**Key Milestone:**
- **All 8 Defense terrain maps are 100% generated in native 4K.**
- **Cumulative native 4K successful inventory reached 22 images** across Adventure (8/8), Tactical (6/8 attempted, 1 NO_IMAGE consumed, 1 excluded 429), and Defense (8/8).
- **All 8 Kingdom terrains remain safely deferred** with documented physical registration blockers; 0 paid calls made, original attempts intact.
- **Budget Compliance:** Cumulative protected exposure is **$61.0818 USD**, leaving **$18.9182 USD headroom** under the **$80.00 USD hard cap**, with the **$15.00 USD safety reserve 100% untouched**.

---

## 2. Live Provider, Lock & Mutex Reconciliation

| Resource | Scope / Location | State at Start | State at Termination | Meaning / Notes |
|---|---|---|---|---|
| **Local Mutex** | `docs/plan/image-production/submission.mutex.json` | Absent | **CLEARED / ABSENT** | Acquired during run; safely released in `finally:` block. |
| **Cloud Lock** | `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` | Gen `1791077386642672` | **Gen `1791078463905795`** | State: `JOB_STATE_SUCCEEDED` / `TERMINAL_COLLECTED`. Succeeded: 5, Failed: 0, Total Cost: $0.7622 USD. |
| **Local Lock** | `docs/plan/image-production/active-batch.lock.json` | Succeeded (Run 03) | **TERMINAL_COLLECTED** | Synchronized with cloud lock generation `1791078463905795`. |
| **Global Batch Jobs** | `projects/186933974004/locations/global/batchPredictionJobs` | 20 terminal | **20 terminal; 0 active, 0 unknown** | Live verified via REST API. |
| **US-Central1 Batch Jobs** | `projects/186933974004/locations/us-central1/batchPredictionJobs` | 0 jobs | **0 jobs; 0 active, 0 unknown** | Live verified clean. |

---

## 3. Comprehensive Budget & Liability Reconciliation

```
========================================================================================
A. Historical Completed Batches 01–17
----------------------------------------------------------------------------------------
Standard token subtotal (985,482 in / 574,764 out):                     $34.978581 USD
15% overhead & storage buffer:                                           $5.246787 USD
Reconciled Batches 01–17 exposure:                                      $40.225368 USD ($40.225)
Historical mock reservation:                                             $2.000000 USD
Protected safety reserve (NEVER SPENT):                                 $15.000000 USD
----------------------------------------------------------------------------------------
Baseline Protected Exposure (Batches 01–17 + Mock + Reserve):           $57.225000 USD
========================================================================================
B. Interactive 4K Run 01 (`run-01-20261003-172733`)
----------------------------------------------------------------------------------------
Calls Attempted:                                                        13 calls
Successful 4K Outputs (12 x 2,520 tokens @ $60/M):                      $1.814400 USD
Failed Call Output (1 x 87 text tokens @ $3/M):                         $0.000261 USD
Measured Prompt Tokens (29,775 tokens @ $0.50/M):                       $0.014888 USD
----------------------------------------------------------------------------------------
Actual Run 01 API Cost:                                                  $1.829288 USD
Reconciled Run 01 Exposure with 15% Buffer:                              $2.103681 USD ($2.1037)
========================================================================================
C. Interactive 4K Continuation Run 02 (`run-02-20261004-010239`)
----------------------------------------------------------------------------------------
Calls Attempted:                                                        5 calls
Successful 4K Outputs (4 x 2,520 tokens @ $60/M):                       $0.604800 USD
Quota-Stopped Call Output (1 x HTTP 429, 0 tokens):                     $0.000000 USD
Measured Prompt Tokens (9,934 tokens @ $0.50/M):                        $0.004967 USD
----------------------------------------------------------------------------------------
Actual Run 02 API Cost:                                                  $0.609767 USD
Reconciled Run 02 Exposure with 15% Buffer:                              $0.701232 USD ($0.7013)
========================================================================================
D. Interactive 4K Continuation Run 03 (`run-03-20261004-012700`)
----------------------------------------------------------------------------------------
Calls Attempted:                                                        2 calls
Successful 4K Outputs (1 x 2,520 tokens @ $60/M):                       $0.151200 USD
Quota-Stopped Call Output (1 x HTTP 429, 0 tokens):                     $0.000000 USD
Measured Prompt Tokens (2,481 tokens @ $0.50/M):                        $0.001241 USD
----------------------------------------------------------------------------------------
Actual Run 03 API Cost:                                                  $0.152441 USD
Reconciled Run 03 Exposure with 15% Buffer:                              $0.175307 USD ($0.1753)
========================================================================================
E. Interactive 4K Continuation Run 04 (`run-04-20261004-013946`)
----------------------------------------------------------------------------------------
Calls Attempted:                                                        6 calls (5 items, 1 429-retry)
Successful 4K Outputs (5 x 2,520 tokens @ $60/M):                       $0.756000 USD
Measured Prompt Tokens (12,423 tokens @ $0.50/M):                       $0.006212 USD
----------------------------------------------------------------------------------------
Actual Run 04 API Cost:                                                  $0.762212 USD
Reconciled Run 04 Exposure with 15% Buffer:                              $0.876543 USD ($0.8765)
========================================================================================
F. Cumulative Protected Exposure & Headroom
----------------------------------------------------------------------------------------
Cumulative Protected Exposure ($57.225 + $2.1037 + $0.7013 + $0.1753 + $0.8765): $61.081800 USD
Retained Historical Ledger Holds:                                       $134.130000 USD
Actual Billed Invoices:                                                 UNKNOWN (retained)
Variance Against $60.00 Target:                                         -$1.081800 USD
HEADROOM UNDER $80.00 HARD CAP (WITH $15 RESERVE FULLY PROTECTED):      $18.918200 USD
========================================================================================
```

---

## 4. Master 32-Item Reconciled Status Table

| # | ID | Mode | Spec | Status | Output Dims | SHA256 (First 16) | Tokens (In/Out) | Cost USD | Run / Provenance | Exact Output / Pack Path | Disposition & Notes |
|:---:|---|---|---|---|:---:|:---:|:---:|:---:|---|---|---|
| **01** | `kingdom-terrain-stone` | kingdom | stone | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-stone/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **02** | `kingdom-terrain-bronze` | kingdom | bronze | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-bronze/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **03** | `kingdom-terrain-iron` | kingdom | iron | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-iron/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **04** | `kingdom-terrain-medieval` | kingdom | medieval | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-medieval/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **05** | `kingdom-terrain-gunpowder` | kingdom | gunpowder | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-gunpowder/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **06** | `kingdom-terrain-industrial` | kingdom | industrial | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-industrial/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **07** | `kingdom-terrain-modern` | kingdom | modern | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-modern/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **08** | `kingdom-terrain-future` | kingdom | future | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | 0 / 0 | $0.0000 | `run-02` | `.../packs/kingdom-terrain-future/` | Hall scale disparity (0.1312 vs 0.34), pad overlaps. 0 paid calls. Attempt preserved. |
| **09** | `adventure-terrain` | adventure | forest | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `bac89323d80cc953` | 2482 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain/output.png` | Technical PASS, viewports generated, verified on disk. |
| **10** | `adventure-terrain-plains` | adventure | plains | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `05afa074262f1f3c` | 2480 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-plains/output.png` | Technical PASS, viewports generated, verified on disk. |
| **11** | `adventure-terrain-hills` | adventure | hills | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `79e65680d4953559` | 2480 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-hills/output.png` | Technical PASS, viewports generated, verified on disk. |
| **12** | `adventure-terrain-swamp` | adventure | swamp | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `f612975cfe39ee6c` | 2481 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-swamp/output.png` | Technical PASS, viewports generated, verified on disk. |
| **13** | `adventure-terrain-desert` | adventure | desert | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `501e57f1631d04a0` | 2482 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-desert/output.png` | Technical PASS, viewports generated, verified on disk. |
| **14** | `adventure-terrain-snow` | adventure | snow | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `86f64b1758272683` | 2481 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-snow/output.png` | Technical PASS, viewports generated, verified on disk. |
| **15** | `adventure-terrain-waste` | adventure | waste | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `8ede49b9c7c679c6` | 2481 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-waste/output.png` | Technical PASS, viewports generated, verified on disk. |
| **16** | `adventure-terrain-ruins` | adventure | ruins | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `3a4315fd7a0e52e8` | 2480 / 2520 | $0.1524 | `run-01` | `.../run-01/.../adventure-terrain-ruins/output.png` | Technical PASS, viewports generated, verified on disk. |
| **17** | `tactical-terrain` | tactical | forest | `CONSUMED_FAILED_NO_IMAGE` | — | — | 2481 / 87 | $0.0015 | `run-01` | `.../run-01/.../tactical-terrain/` | Consumed attempt via NO_IMAGE text response. Not retried. |
| **18** | `tactical-terrain-plains` | tactical | plains | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `5916792b12a1d9cd` | 2483 / 2520 | $0.1524 | `run-01` | `.../run-01/.../tactical-terrain-plains/output.png` | Technical PASS, viewports generated, verified on disk. |
| **19** | `tactical-terrain-hills` | tactical | hills | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `30c3aa2f29f8281d` | 2483 / 2520 | $0.1524 | `run-01` | `.../run-01/.../tactical-terrain-hills/output.png` | Technical PASS, viewports generated, verified on disk. |
| **20** | `tactical-terrain-swamp` | tactical | swamp | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `95c293612f625fa0` | 2486 / 2520 | $0.1524 | `run-01` | `.../run-01/.../tactical-terrain-swamp/output.png` | Technical PASS, viewports generated, verified on disk. |
| **21** | `tactical-terrain-desert` | tactical | desert | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `5f5206c89caa2e29` | 2487 / 2520 | $0.1524 | `run-01` | `.../run-01/.../tactical-terrain-desert/output.png` | Technical PASS, viewports generated, verified on disk. |
| **22** | `tactical-terrain-snow` | tactical | snow | `EXCLUDED_PREVIOUS_429` | — | — | 0 / 0 | $0.0000 | `run-01` | `.../run-01/.../tactical-terrain-snow/` | Excluded from paid calls per explicit owner directive. |
| **23** | `tactical-terrain-waste` | tactical | waste | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `8159cb4d9126752f` | 2485 / 2520 | $0.1524 | `run-02` | `.../run-02/.../tactical-terrain-waste/output.png` | Technical PASS, viewports generated, verified on disk. |
| **24** | `tactical-terrain-ruins` | tactical | ruins | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `c96446ba9f8cdb2e` | 2484 / 2520 | $0.1524 | `run-02` | `.../run-02/.../tactical-terrain-ruins/output.png` | Technical PASS, viewports generated, verified on disk. |
| **25** | `defense-terrain` | defense | forest | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `01c19c36e58c6e54` | 2483 / 2520 | $0.1524 | `run-02` | `.../run-02/.../defense-terrain/output.png` | Technical PASS, viewports generated, verified on disk. |
| **26** | `defense-terrain-plains` | defense | plains | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `7941ee34e62b2053` | 2482 / 2520 | $0.1524 | `run-02` | `.../run-02/.../defense-terrain-plains/output.png` | Technical PASS, viewports generated, verified on disk. |
| **27** | `defense-terrain-hills` | defense | hills | **`PREVIOUS_SUCCEEDED_REUSED`** | 5504×3072 | `a5b979e6f3fc483a` | 2481 / 2520 | $0.1524 | `run-03` | `.../run-03/.../defense-terrain-hills/output.png` | Technical PASS, viewports generated, verified on disk. |
| **28** | `defense-terrain-swamp` | defense | swamp | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`380a0cc2343985d0`** | **2485 / 2520** | **$0.1524** | **`run-04`** | [`.../run-04/.../defense-terrain-swamp/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-swamp/output.png) | **NEW SUCCESS!** Native 4K, 4 viewports, comparison plate, verified on disk. |
| **29** | `defense-terrain-desert` | defense | desert | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`7da55fccca84bc13`** | **2486 / 2520** | **$0.1524** | **`run-04`** | [`.../run-04/.../defense-terrain-desert/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-desert/output.png) | **NEW SUCCESS!** 429 backoff 60s handled, native 4K, 4 viewports, verified on disk. |
| **30** | `defense-terrain-snow` | defense | snow | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`514ad172d646a9d1`** | **2485 / 2520** | **$0.1524** | **`run-04`** | [`.../run-04/.../defense-terrain-snow/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-snow/output.png) | **NEW SUCCESS!** Native 4K, 4 viewports, comparison plate, verified on disk. |
| **31** | `defense-terrain-waste` | defense | waste | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`c165d958c68f052d`** | **2484 / 2520** | **$0.1524** | **`run-04`** | [`.../run-04/.../defense-terrain-waste/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-waste/output.png) | **NEW SUCCESS!** Native 4K, 4 viewports, comparison plate, verified on disk. |
| **32** | `defense-terrain-ruins` | defense | ruins | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`71ecaf6c98b90bd9`** | **2483 / 2520** | **$0.1524** | **`run-04`** | [`.../run-04/.../defense-terrain-ruins/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-ruins/output.png) | **NEW SUCCESS!** Native 4K, 4 viewports, comparison plate, verified on disk. |

---

## 5. Technical, Spatial & Viewport Verification

All 22 successful images across Runs 01, 02, 03, and 04 pass rigorous technical checks:
- **Dimensions:** Native 4K landscape (`5504×3072 px`, exactly 16:9 aspect ratio).
- **Format:** Lossless RGB PNG, verified readable and non-corrupt.
- **Viewports:** All 22 packs contain 4 responsive crops derived from native 4K:
  - Phone compact: `825×375` (2.2:1 ultrawide landscape)
  - Phone standard: `933×424` (2.2:1 standard landscape)
  - Tablet 4:3: `1180×820` (1.44:1 tablet landscape)
  - Desktop standard: `1280×720` (16:9 landscape)
- **Side-by-Side Comparison:** Each pack contains `comparison.png` (`2752×768 px`) comparing the layout geometry guide to the Lanczos-downscaled generated terrain.

---

## 6. Summary of Blockers & Remaining Terrain Scope

1. **Defense & Adventure Scope Complete:**
   - Adventure mode terrain: 8/8 generated and verified (`PASS`).
   - Defense mode terrain: 8/8 generated and verified (`PASS`).
   - Tactical mode terrain: 6/8 generated and verified (`PASS`). ID 17 (`tactical-terrain`) consumed its single attempt via text `NO_IMAGE` response in Run 01; ID 22 (`tactical-terrain-snow`) hit HTTP 429 in Run 01 and was excluded from resending.
2. **Kingdom Terrains Physical Registration Blocker:**
   - Concrete geometry collisions in the active implementation contract remain unresolved (Hall scale disparity 0.1312 vs 0.34, 12 blocking door coverages across 17 pads, tablet P11 panel collision, entrance 7.67px discontinuity).
   - All 8 Kingdom IDs (`kingdom-terrain-stone` .. `future`) remain safely deferred with zero tokens spent and original authorized attempts 100% intact.
