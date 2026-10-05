# First 32 Native 4K Terrain Images — Continuation & Reconciliation Report

**Date:** 2026-10-04  
**Role:** Owner-Selected Image Generation Executor  
**Authority:** Owner Continuation Prompt (`docs/plan/IMAGE-AI-CONTINUE-REMAINING-4K-PROMPT-2026-10-04.txt`)  
**Run ID:** `run-02-20261004-010239` (linked to `run-01-20261003-172733`)  
**Status:** CONTINUATION RUN TERMINAL & RECONCILED — 16 CUMULATIVE NATIVE 4K PASS (5504x3072), 8 DEFERRED KINGDOM (LOCAL PACKS PREPARED, UNUSED ATTEMPTS PRESERVED), 1 FAILED CONSUMED (NO_IMAGE), 2 QUOTA STOPS (HTTP 429), 5 UNATTEMPTED (LOCAL PACKS VALIDATED, QUOTA PAUSED)  

---

## 1. Executive Summary

In accordance with owner directives (4 October 2026), the image executor continued the authorized first-32 native-4K terrain phase (`4K-FIRST-32`), reconciling all historical attempt journals, shared CAS locks, quota readiness, and budget holds without restarting or rebuying previously succeeded outputs.

- **Previous Run 01 Preserved & Reused:** All 12 successful native 4K outputs from `assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/` were verified on disk (hashes, native 5504×3072 px dimensions, comparison plates, and 4 responsive viewports intact) and reused without repurchase.
- **Run 01 Terminal Dispositions Reconciled:**
  - ID 17 (`tactical-terrain`): Consumed its single authorized attempt via a `finishReason: "NO_IMAGE"` text response; preserved as `CONSUMED_FAILED_NO_IMAGE` without retry.
  - ID 22 (`tactical-terrain-snow`): Received `HTTP 429` in Run 01; strictly excluded from paid calls in this continuation per explicit directive, preserving its exact disposition without resending.
- **Stage 1 (Kingdom Local Preparation & Blocker Audit):** Local packs were prepared and rasterized for all 8 Kingdom terrains (`kingdom-terrain-stone` through `future`). A rigorous physical geometry survey confirmed persistent, concrete registration conflicts (Hall scale 0.1312 vs 0.34 framing, 12 blocking door coverages across 17 pads, tablet P11 panel collision, 7.67px threshold-to-apron discontinuity). All 8 Kingdom IDs were individually deferred as `DEFERRED_PHYSICAL_REGISTRATION_BLOCKER` with concrete coordinate evidence, preserving their original generation attempt unused (0 paid calls made).
- **Stage 6 (Sequential 4K Live Generation):** The 10 never-attempted items were initiated sequentially with a mandatory **20-second inter-request pacing gap** against Vertex AI `gemini-3.1-flash-image` (native 4K 16:9, individual `generateContent` calls):
  - **4 Native 4K Outputs Successfully Generated (`PASS` Technical Status):**
    1. `tactical-terrain-waste` (order 23): 5504×3072 px, SHA `8159cb4d9126752f...`, 2485 in / 2520 out tokens ($0.1524 USD).
    2. `tactical-terrain-ruins` (order 24): 5504×3072 px, SHA `c96446ba9f8cdb2e...`, 2484 in / 2520 out tokens ($0.1524 USD).
    3. `defense-terrain` (order 25): 5504×3072 px, SHA `01c19c36e58c6e54...`, 2483 in / 2520 out tokens ($0.1524 USD).
    4. `defense-terrain-plains` (order 26): 5504×3072 px, SHA `7941ee34e62b2053...`, 2482 in / 2520 out tokens ($0.1524 USD).
    - Cumulative native 4K successful inventory now stands at **16 completed images** across Adventure, Tactical, and Defense modes.
  - **Quota Stop Enforced (`HTTP 429` on ID 27):**
    - Item 27 (`defense-terrain-hills`) received `HTTP 429: Too Many Requests` (Vertex AI per-minute project rate ceiling).
    - Strictly following owner policy (*"Stop provider work immediately on another 429, quota/billing failure or ambiguous outcome. No retries, fallback, repeated probing, extra purchases or reserve spending"*), the runner terminated provider calls immediately.
  - **5 Remaining Items Locally Prepared:** Complete pack files (`geometry.json`, `guide.png`, `base.png`, `mask_change.png`, `mask_keep.png`, `validation.json`, `request_meta.json`) for orders 28..32 (`defense-terrain-swamp`, `desert`, `snow`, `waste`, `ruins`) were rendered and validated locally outside provider spend, ready for execution when rate limits replenish.
- **Budget Compliance:**
  - Run 02 spend: 4 successful calls = 9,934 prompt tokens + 10,080 candidate tokens = **$0.6098 USD** actual API spend ($0.7013 USD reconciled with 15% buffer).
  - Cumulative protected exposure: **$60.0300 USD** ($57.225 baseline + $2.1037 Run 01 + $0.7013 Run 02).
  - Headroom below the **$80.00 USD hard cap is $19.9700 USD**.
  - **$15.00 USD safety reserve remains 100% untouched and protected.**
  - Invoices remain UNKNOWN; zero batch prediction jobs active/unknown.

---

## 2. Live Provider, Lock & Mutex Reconciliation

| Resource | Scope / Location | State at Start | State at Termination | Meaning / Notes |
|---|---|---|---|---|
| **Local Mutex** | `docs/plan/image-production/submission.mutex.json` | Absent | **CLEARED / ABSENT** | Acquired during run; safely released in `finally:` block upon quota stop. |
| **Cloud Lock** | `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` | Gen `1791049026269456` | **Gen `1791076076745874`** | State: `JOB_STATE_SUCCEEDED` / `TERMINAL_COLLECTED`. Succeeded: 4, Total Cost: $0.6098 USD. |
| **Local Lock** | `docs/plan/image-production/active-batch.lock.json` | Succeeded (Run 01) | **TERMINAL_COLLECTED** | Synchronized with cloud lock generation `1791076076745874`. |
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
D. Cumulative Protected Exposure & Headroom
----------------------------------------------------------------------------------------
Cumulative Protected Exposure ($57.225 + $2.1037 + $0.7013):            $60.030000 USD
Retained Historical Ledger Holds (17 x $6 + $2 + $15 + $9.12 + $2.85):  $130.970000 USD
Actual Billed Invoices:                                                 UNKNOWN (retained)
Variance Against $60.00 Target:                                         -$0.030000 USD
HEADROOM UNDER $80.00 HARD CAP (WITH $15 RESERVE FULLY PROTECTED):      $19.970000 USD
========================================================================================
```

---

## 4. Master 32-Item Reconciled Status Table

| # | ID | Mode | Spec | Status | Output Dimensions | SHA256 (First 16) | Tokens (In/Out) | Cost USD | Run / Provenance | Exact Output / Pack Path | Disposition & Review Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **01** | `kingdom-terrain-stone` | Kingdom | Stone | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-stone/` | Pack prepared & validated locally. Deferred: Hall scale 0.1312 vs 0.34, 12 blocking door coverages, P11 panel collision, 7.67px threshold gap. Original attempt unused. |
| **02** | `kingdom-terrain-bronze` | Kingdom | Bronze | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-bronze/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **03** | `kingdom-terrain-iron` | Kingdom | Iron | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-iron/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **04** | `kingdom-terrain-medieval` | Kingdom | Medieval | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-medieval/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **05** | `kingdom-terrain-gunpowder` | Kingdom | Gunpowder | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-gunpowder/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **06** | `kingdom-terrain-industrial` | Kingdom | Industrial | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-industrial/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **07** | `kingdom-terrain-modern` | Kingdom | Modern | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-modern/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **08** | `kingdom-terrain-future` | Kingdom | Future | DEFERRED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `packs/kingdom-terrain-future/` | Pack prepared & validated locally. Deferred: Unresolved common Kingdom physical registration conflicts. Original attempt unused. |
| **09** | `adventure-terrain` | Adventure | Forest | **SUCCEEDED** | 5504 × 3072 | `bac89323d80cc953...` | 2479 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **10** | `adventure-terrain-plains` | Adventure | Plains | **SUCCEEDED** | 5504 × 3072 | `05afa074262f1f3c...` | 2478 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-plains/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **11** | `adventure-terrain-hills` | Adventure | Hills | **SUCCEEDED** | 5504 × 3072 | `79e65680d4953559...` | 2477 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-hills/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **12** | `adventure-terrain-swamp` | Adventure | Swamp | **SUCCEEDED** | 5504 × 3072 | `f612975cfe39ee6c...` | 2481 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-swamp/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **13** | `adventure-terrain-desert` | Adventure | Desert | **SUCCEEDED** | 5504 × 3072 | `501e57f1631d04a0...` | 2482 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-desert/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **14** | `adventure-terrain-snow` | Adventure | Snow | **SUCCEEDED** | 5504 × 3072 | `86f64b1758272683...` | 2481 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-snow/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **15** | `adventure-terrain-waste` | Adventure | Waste | **SUCCEEDED** | 5504 × 3072 | `8ede49b9c7c679c6...` | 2480 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-waste/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **16** | `adventure-terrain-ruins` | Adventure | Ruins | **SUCCEEDED** | 5504 × 3072 | `3a4315fd7a0e52e8...` | 2479 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/adventure-terrain-ruins/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **17** | `tactical-terrain` | Tactical | Forest | **FAILED** | None | None | 2484 / 87 | $0.0015 | Run 01 Consumed | `run-01/packs/tactical-terrain/` | Vertex AI returned `NO_IMAGE` (text only). Single authorized attempt consumed; no retry per contract. |
| **18** | `tactical-terrain-plains` | Tactical | Plains | **SUCCEEDED** | 5504 × 3072 | `5916792b12a1d9cd...` | 2483 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/tactical-terrain-plains/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **19** | `tactical-terrain-hills` | Tactical | Hills | **SUCCEEDED** | 5504 × 3072 | `30c3aa2f29f8281d...` | 2482 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/tactical-terrain-hills/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **20** | `tactical-terrain-swamp` | Tactical | Swamp | **SUCCEEDED** | 5504 × 3072 | `95c293612f625fa0...` | 2486 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/tactical-terrain-swamp/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **21** | `tactical-terrain-desert` | Tactical | Desert | **SUCCEEDED** | 5504 × 3072 | `5f5206c89caa2e29...` | 2487 / 2520 | $0.1524 | Run 01 Reused | `run-01/packs/tactical-terrain-desert/output.png` | Technical PASS. Reused from Run 01; full pack, comparison plate, 4 viewports intact. |
| **22** | `tactical-terrain-snow` | Tactical | Snow | **QUOTA_STOP** | None | None | 0 / 0 | $0.0000 | Run 01 Reconciled | `run-01/packs/tactical-terrain-snow/` | HTTP 429 in Run 01. Excluded from paid calls in Run 02 per explicit owner directive; exact disposition preserved. |
| **23** | `tactical-terrain-waste` | Tactical | Waste | **SUCCEEDED** | 5504 × 3072 | `8159cb4d9126752f...` | 2485 / 2520 | $0.1524 | **Run 02 Generated** | `run-02/packs/tactical-terrain-waste/output.png` | **Technical PASS.** Full pack, comparison sheet, 4 responsive viewports generated. |
| **24** | `tactical-terrain-ruins` | Tactical | Ruins | **SUCCEEDED** | 5504 × 3072 | `c96446ba9f8cdb2e...` | 2484 / 2520 | $0.1524 | **Run 02 Generated** | `run-02/packs/tactical-terrain-ruins/output.png` | **Technical PASS.** Full pack, comparison sheet, 4 responsive viewports generated. |
| **25** | `defense-terrain` | Defense | Forest | **SUCCEEDED** | 5504 × 3072 | `01c19c36e58c6e54...` | 2483 / 2520 | $0.1524 | **Run 02 Generated** | `run-02/packs/defense-terrain/output.png` | **Technical PASS.** Full pack, comparison sheet, 4 responsive viewports generated. |
| **26** | `defense-terrain-plains` | Defense | Plains | **SUCCEEDED** | 5504 × 3072 | `7941ee34e62b2053...` | 2482 / 2520 | $0.1524 | **Run 02 Generated** | `run-02/packs/defense-terrain-plains/output.png` | **Technical PASS.** Full pack, comparison sheet, 4 responsive viewports generated. |
| **27** | `defense-terrain-hills` | Defense | Hills | **QUOTA_STOP** | None | None | 0 / 0 | $0.0000 | **Run 02 Attempted** | `run-02/packs/defense-terrain-hills/` | Vertex AI returned HTTP 429 (rate limit). Terminated provider calls per directive. Pack ready. |
| **28** | `defense-terrain-swamp` | Defense | Swamp | UNATTEMPTED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `run-02/packs/defense-terrain-swamp/` | Pack prepared & validated locally. Paused due to upstream quota stop. |
| **29** | `defense-terrain-desert` | Defense | Desert | UNATTEMPTED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `run-02/packs/defense-terrain-desert/` | Pack prepared & validated locally. Paused due to upstream quota stop. |
| **30** | `defense-terrain-snow` | Defense | Snow | UNATTEMPTED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `run-02/packs/defense-terrain-snow/` | Pack prepared & validated locally. Paused due to upstream quota stop. |
| **31** | `defense-terrain-waste` | Defense | Waste | UNATTEMPTED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `run-02/packs/defense-terrain-waste/` | Pack prepared & validated locally. Paused due to upstream quota stop. |
| **32** | `defense-terrain-ruins` | Defense | Ruins | UNATTEMPTED | None | None | 0 / 0 | $0.0000 | Run 02 Local Pack | `run-02/packs/defense-terrain-ruins/` | Pack prepared & validated locally. Paused due to upstream quota stop. |

---

## 5. Artifact & Pack Verification

All outputs from both runs are organized outside Git in durable staging directories:
- **Run 01:** `assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733/packs/<id>/`
- **Run 02:** `assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/<id>/`

### Detailed Verification of Run 02 Successful Outputs:
1. **`tactical-terrain-waste` (order 23):**
   - Output Image: `5504 × 3072 px` PNG (SHA256: `8159cb4d9126752f9bc8e1548e69d072efc464efc3547f872cffb462ff252ea9`).
   - Comparison Plate: `2752 × 768 px` side-by-side (geometry guide on left, downsampled output on right).
   - Viewport Crops: `vp_825x375.png`, `vp_933x424.png`, `vp_1180x820.png`, `vp_1280x720.png`.
   - Visual Attributes: Coherent volcanic wasteland basalt ground, dark ash earth, craggy fissures strictly confined to blocked zones, stream crossing decks at lanes 3 & 7 unobstructed, allied and enemy deployment zones fully preserved.
2. **`tactical-terrain-ruins` (order 24):**
   - Output Image: `5504 × 3072 px` PNG (SHA256: `c96446ba9f8cdb2ef62b66723ef5d28b18f3a38a9d9e48753ec910da1e56b4f7`).
   - Comparison Plate: `2752 × 768 px` side-by-side.
   - Viewport Crops: 4 target viewport resolutions.
   - Visual Attributes: Weathered stone flagstones, ancient crumbled masonry outside playfield, clear central stream crossings, deployment boundaries preserved.
3. **`defense-terrain` (order 25):**
   - Output Image: `5504 × 3072 px` PNG (SHA256: `01c19c36e58c6e54f02fa481e194851eb394f4fe97ee89f5bc74f9dff5ec70bb`).
   - Comparison Plate: `2752 × 768 px` side-by-side.
   - Viewport Crops: 4 target viewport resolutions.
   - Visual Attributes: Natural winding road lane with 29-vertex spline from lower-left spawn (0.5, 14.5) to upper-right gate (6.5, 0.5), eight empty tower pads (D1–D8) clear of baked buildings, natural temperate valley slopes with clear approaches.
4. **`defense-terrain-plains` (order 26):**
   - Output Image: `5504 × 3072 px` PNG (SHA256: `7941ee34e62b20538a7c2941df26ca34d9326eeb545ea88544d6c4e09cb9f2cb`).
   - Comparison Plate: `2752 × 768 px` side-by-side.
   - Viewport Crops: 4 target viewport resolutions.
   - Visual Attributes: Golden grassy steppe, winding lane clear and registered to guide, 8 tower pads unobstructed.

---

## 6. Local Kingdom Preparation & Geometric Blocker Audit

Local packs were generated for all 8 Kingdom terrains (`kingdom-terrain-stone` .. `future`) under `assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/kingdom-terrain-*/`.
Each pack contains:
- `geometry.json`: Full 14×11 matrix `[60, -10, 25, 35, 170, 165]`, sites, road, ridge, gate, river, and crossing data.
- `guide.png`: Clean 1376×768 geometry diagram.
- `base.png`: Bare plot-cleaned base from source candidate.
- `mask_change.png` and `mask_keep.png`: Binary transformation masks.
- `validation.json`: Formal mathematical audit detailing the following concrete physical blockers:
  1. **Hall Foundation Scale Disparity:** The active contract specifies `rect: [5, 0, 3, 1.5]`, which projects to a scale of `0.1312` (width ~470 px). Townhall sprite v3 is 1024×1024 px and requires uniform framing scale `0.34` (width ~750 px). Forcing scale 0.1312 shrinks the Hall into an ungrounded hut, while scale 0.34 expands the roof to y=40, colliding with the ridge boundary.
  2. **Entrance-to-Road Discontinuity:** The Townhall v3 entrance cobble is located at `(640.0, 291.26)`, whereas the contract road spine originates at `(644.6, 297.4)`, creating an unmeasured `7.67 px` physical gap.
  3. **14 Pairwise Mature Rectangle Overlaps (12 Blocking Door Occlusions):**
     - `P10` nearer body covers `P09` farther door.
     - `P06` nearer body covers `P05` farther door.
     - `P11` nearer body covers `P10` farther door.
     - `P02` nearer body covers `P01` farther door.
     - `P07` nearer body covers `P06` farther door.
     - `P08` nearer body covers `P11` farther door.
     - `P08` nearer body covers `P07` farther door.
     - `P03` nearer body covers `P02` farther door.
     - `P12` nearer body covers `P08` farther door.
     - `P17` nearer body covers `P15` farther door.
     - `P04` nearer body covers `P03` farther door.
     - `P16` nearer body covers `P13` farther door.
  4. **Tablet Viewport Panel Collision:** Build site `P11` extends `19.34 source pixels` beyond the open slide-panel boundary on 1180×820 tablet viewports.

**Disposition:** Because generating against these unresolved physical conflicts would produce ungrounded, unaligned backgrounds requiring later discarding, each Kingdom ID was individually deferred (`DEFERRED_PHYSICAL_REGISTRATION_BLOCKER`). Their original authorized attempts remain **100% unused (0 paid calls)**, preserving full budget and attempt authority for a coordinated geometry resolution.

---

## 7. Next Steps & Quota Protocol

1. **Vertex AI Rate Limit Replenishment:**
   - The generateContent endpoint per-minute rate limit (`HTTP 429`) typically resets after a rolling window (60–120 seconds).
   - Once reset, the remaining 6 Defense items (`defense-terrain-hills` [order 27] and `defense-terrain-swamp` through `ruins` [orders 28..32]) can be sequentially executed. Their local packs, guides, bases, and prompts are already 100% generated and validated in `run-02/packs/`.
2. **Estimated Spend for Remaining 6 Defense Items:**
   - 6 calls × ~$0.1524 USD = **~$0.9144 USD** (~$1.05 USD with 15% buffer).
   - Protected exposure will rise from $60.03 USD to **~$61.08 USD**, remaining **$18.92 USD below the $80.00 hard cap** with the **$15.00 safety reserve completely untouched**.
3. **Kingdom Geometry Coordination:**
   - When Code AI or the owner provides the coordinated civic terrace and foundation geometry resolving the Hall scale and mature door overlaps, the 8 preserved Kingdom attempts can be executed without exceeding budget or scope limits.
