# First 32 Native 4K Terrain Images — Tactical Retry Completion Report

**Date:** 2026-10-04  
**Role:** Owner-Selected Image Generation Executor  
**Authority:** Owner Directive (*"First try 2 tactical terrins"*)  
**Run ID:** `run-05-tactical-retry-20261004-015857` (linked to `run-01`, `run-02`, `run-03`, and `run-04`)  
**Status:** **RUN COMPLETE & TERMINAL — BOTH TACTICAL TERRAINS SUCCEEDED (24 CUMULATIVE NATIVE 4K PASS, 5504×3072)**  

---

## 1. Executive Summary

Upon explicit user authorization (*"First try 2 tactical terrins"*), the image generation executor initiated and completed a dedicated tactical retry run (`run-05-tactical-retry-20261004-015857`) against Google Vertex AI `gemini-3.1-flash-image` (native 4K 16:9, individual `generateContent` calls):

1. **Order 17 (`tactical-terrain` — Forest Tactical Map):**
   - Attempt 1: **SUCCESS** (36.0s). Dimensions: `5504×3072 px` (16:9).
   - SHA256: `6eadf55f2df8727b3e08f51dfb34aeb387f64ae89658ff9b1bfb904f4ecf990a`.
   - Tokens: 2,484 prompt in / 2,520 candidate out | Cost: **$0.1524 USD**.
   - Complete pack generated: master output, side-by-side comparison (`2752×768 px`), and 4 responsive viewport crops (`825×375`, `933×424`, `1180×820`, `1280×720`).
   - Pacing: 30-second post-generation gap enforced before next request.
2. **Order 22 (`tactical-terrain-snow` — Snow Tactical Map):**
   - Attempt 1: **SUCCESS** (36.3s). Dimensions: `5504×3072 px` (16:9).
   - SHA256: `c1b39f72f6ded4bb8a12eefc464bb72eebfc111dbba582e0ec187a55f9e2fb7a`.
   - Tokens: 2,486 prompt in / 2,520 candidate out | Cost: **$0.1524 USD**.
   - Complete pack generated: master output, side-by-side comparison (`2752×768 px`), and 4 responsive viewport crops (`825×375`, `933×424`, `1180×820`, `1280×720`).

**Major Milestones:**
- **Tactical Mode:** **8 / 8 Complete (100% PASS)** — All 8 tactical battlefield maps (`forest`, `plains`, `hills`, `swamp`, `desert`, `snow`, `waste`, `ruins`) are now generated and verified at native 4K resolution.
- **Adventure Mode:** **8 / 8 Complete (100% PASS)** — All 8 adventure world maps generated and verified.
- **Defense Mode:** **8 / 8 Complete (100% PASS)** — All 8 defense battlefield maps generated and verified.
- **Whole Battlefield Scope:** **ALL 24 MODE/BIOME BATTLEFIELD MAPS ARE 100% COMPLETE AT NATIVE 4K (`5504×3072 px`).**
- **Kingdom Mode:** 8 / 8 terrains remain deferred outside paid calls with documented physical geometry blockers in the active contract (Hall scale 0.1312 vs 0.34, 12 pad door occlusions, tablet P11 overlap); original authorized attempts preserved 100% unused.

---

## 2. Live Provider, Lock & Mutex Reconciliation

| Resource | Scope / Location | State at Start | State at Termination | Meaning / Notes |
|---|---|---|---|---|
| **Local Mutex** | `docs/plan/image-production/submission.mutex.json` | Absent | **CLEARED / ABSENT** | Acquired during run; safely released in `finally:` block. |
| **Cloud Lock** | `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` | Gen `1791078463905795` | **Gen `1791079249668169`** | State: `JOB_STATE_SUCCEEDED` / `TERMINAL_COLLECTED`. Succeeded: 2, Failed: 0, Total Cost: $0.3049 USD. |
| **Local Lock** | `docs/plan/image-production/active-batch.lock.json` | Succeeded (Run 04) | **TERMINAL_COLLECTED** | Synchronized with cloud lock generation `1791079249668169`. |
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
B. Interactive 4K Runs 01–04
----------------------------------------------------------------------------------------
Run 01 Reconciled Exposure with 15% Buffer:                              $2.103700 USD
Run 02 Reconciled Exposure with 15% Buffer:                              $0.701300 USD
Run 03 Reconciled Exposure with 15% Buffer:                              $0.175300 USD
Run 04 Reconciled Exposure with 15% Buffer:                              $0.876500 USD
----------------------------------------------------------------------------------------
Subtotal Runs 01–04 Protected Exposure:                                  $3.856800 USD
========================================================================================
C. Interactive 4K Tactical Retry Run (`run-05-tactical-retry-20261004-015857`)
----------------------------------------------------------------------------------------
Calls Attempted:                                                        2 calls
Successful 4K Outputs (2 x 2,520 tokens @ $60/M):                       $0.302400 USD
Measured Prompt Tokens (4,970 tokens @ $0.50/M):                        $0.002485 USD
----------------------------------------------------------------------------------------
Actual Tactical Retry API Cost:                                          $0.304885 USD
Reconciled Tactical Retry Exposure with 15% Buffer:                      $0.350618 USD ($0.3506)
========================================================================================
D. Cumulative Protected Exposure & Headroom
----------------------------------------------------------------------------------------
Cumulative Protected Exposure ($57.225 + $3.8568 + $0.3506):            $61.432400 USD
Retained Historical Ledger Holds:                                       $134.730000 USD
Actual Billed Invoices:                                                 UNKNOWN (retained)
Variance Against $60.00 Target:                                         -$1.432400 USD
HEADROOM UNDER $80.00 HARD CAP (WITH $15 RESERVE FULLY PROTECTED):      $18.567600 USD
========================================================================================
```

---

## 4. Master 32-Item Reconciled Status Table

| # | ID | Mode | Spec | Status | Output Dims | SHA256 (First 16) | Cost USD | Run / Provenance | Output / Pack Path | Notes |
|:---:|---|---|---|---|:---:|:---:|:---:|:---:|---|---|
| **01** | `kingdom-terrain-stone` | kingdom | stone | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-stone/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **02** | `kingdom-terrain-bronze` | kingdom | bronze | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-bronze/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **03** | `kingdom-terrain-iron` | kingdom | iron | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-iron/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **04** | `kingdom-terrain-medieval` | kingdom | medieval | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-medieval/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **05** | `kingdom-terrain-gunpowder` | kingdom | gunpowder | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-gunpowder/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **06** | `kingdom-terrain-industrial` | kingdom | industrial | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-industrial/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **07** | `kingdom-terrain-modern` | kingdom | modern | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-modern/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **08** | `kingdom-terrain-future` | kingdom | future | `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` | — | — | $0.00 | `run-02` | `.../packs/kingdom-terrain-future/` | Hall scale / pad collisions. 0 paid calls. Attempt preserved. |
| **09** | `adventure-terrain` | adventure | forest | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `bac89323d80cc953` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain/output.png) | Technical PASS, viewports generated, verified. |
| **10** | `adventure-terrain-plains` | adventure | plains | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `05afa074262f1f3c` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-plains/output.png) | Technical PASS, viewports generated, verified. |
| **11** | `adventure-terrain-hills` | adventure | hills | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `79e65680d4953559` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-hills/output.png) | Technical PASS, viewports generated, verified. |
| **12** | `adventure-terrain-swamp` | adventure | swamp | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `f612975cfe39ee6c` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-swamp/output.png) | Technical PASS, viewports generated, verified. |
| **13** | `adventure-terrain-desert` | adventure | desert | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `501e57f1631d04a0` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-desert/output.png) | Technical PASS, viewports generated, verified. |
| **14** | `adventure-terrain-snow` | adventure | snow | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `86f64b1758272683` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-snow/output.png) | Technical PASS, viewports generated, verified. |
| **15** | `adventure-terrain-waste` | adventure | waste | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `8ede49b9c7c679c6` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-waste/output.png) | Technical PASS, viewports generated, verified. |
| **16** | `adventure-terrain-ruins` | adventure | ruins | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `3a4315fd7a0e52e8` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/adventure-terrain-ruins/output.png) | Technical PASS, viewports generated, verified. |
| **17** | `tactical-terrain` | tactical | forest | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`6eadf55f2df8727b`** | **$0.1524** | **`run-05`** | [`.../run-05/.../tactical-terrain/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-05-tactical-retry-20261004-015857/packs/tactical-terrain/output.png) | **NEW PASS!** Native 4K, 4 viewports, comparison plate verified. |
| **18** | `tactical-terrain-plains` | tactical | plains | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `5916792b12a1d9cd` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/tactical-terrain-plains/output.png) | Technical PASS, viewports generated, verified. |
| **19** | `tactical-terrain-hills` | tactical | hills | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `30c3aa2f29f8281d` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/tactical-terrain-hills/output.png) | Technical PASS, viewports generated, verified. |
| **20** | `tactical-terrain-swamp` | tactical | swamp | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `95c293612f625fa0` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/tactical-terrain-swamp/output.png) | Technical PASS, viewports generated, verified. |
| **21** | `tactical-terrain-desert` | tactical | desert | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `5f5206c89caa2e29` | $0.1524 | `run-01` | [`.../run-01/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/tactical-terrain-desert/output.png) | Technical PASS, viewports generated, verified. |
| **22** | `tactical-terrain-snow` | tactical | snow | **`GENERATED_TECHNICAL_PASS`** | **5504×3072** | **`c1b39f72f6ded4bb`** | **$0.1524** | **`run-05`** | [`.../run-05/.../tactical-terrain-snow/output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-05-tactical-retry-20261004-015857/packs/tactical-terrain-snow/output.png) | **NEW PASS!** Native 4K, 4 viewports, comparison plate verified. |
| **23** | `tactical-terrain-waste` | tactical | waste | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `8159cb4d9126752f` | $0.1524 | `run-02` | [`.../run-02/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/tactical-terrain-waste/output.png) | Technical PASS, viewports generated, verified. |
| **24** | `tactical-terrain-ruins` | tactical | ruins | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `c96446ba9f8cdb2e` | $0.1524 | `run-02` | [`.../run-02/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/tactical-terrain-ruins/output.png) | Technical PASS, viewports generated, verified. |
| **25** | `defense-terrain` | defense | forest | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `01c19c36e58c6e54` | $0.1524 | `run-02` | [`.../run-02/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/defense-terrain/output.png) | Technical PASS, viewports generated, verified. |
| **26** | `defense-terrain-plains` | defense | plains | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `7941ee34e62b2053` | $0.1524 | `run-02` | [`.../run-02/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/defense-terrain-plains/output.png) | Technical PASS, viewports generated, verified. |
| **27** | `defense-terrain-hills` | defense | hills | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `a5b979e6f3fc483a` | $0.1524 | `run-03` | [`.../run-03/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-03-20261004-012700/packs/defense-terrain-hills/output.png) | Technical PASS, viewports generated, verified. |
| **28** | `defense-terrain-swamp` | defense | swamp | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `380a0cc2343985d0` | $0.1524 | `run-04` | [`.../run-04/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-swamp/output.png) | Technical PASS, viewports generated, verified. |
| **29** | `defense-terrain-desert` | defense | desert | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `7da55fccca84bc13` | $0.1524 | `run-04` | [`.../run-04/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-desert/output.png) | Technical PASS, viewports generated, verified. |
| **30** | `defense-terrain-snow` | defense | snow | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `514ad172d646a9d1` | $0.1524 | `run-04` | [`.../run-04/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-snow/output.png) | Technical PASS, viewports generated, verified. |
| **31** | `defense-terrain-waste` | defense | waste | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `c165d958c68f052d` | $0.1524 | `run-04` | [`.../run-04/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-waste/output.png) | Technical PASS, viewports generated, verified. |
| **32** | `defense-terrain-ruins` | defense | ruins | **`GENERATED_TECHNICAL_PASS`** | 5504×3072 | `71ecaf6c98b90bd9` | $0.1524 | `run-04` | [`.../run-04/.../output.png`](file:///c:/dev/ages-of-dominion-reborn/assets/high-res/interactive-4k-first32-20261003/run-04-20261004-013946/packs/defense-terrain-ruins/output.png) | Technical PASS, viewports generated, verified. |
