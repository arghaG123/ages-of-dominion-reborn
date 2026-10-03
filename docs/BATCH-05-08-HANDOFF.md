# Batch Production Execution Report: Batches 04–08

**Date:** 3 October 2026  
**Role:** Batch Production Executor  
**Model:** `gemini-3.1-flash-image` (Vertex AI Global Batch, 1K resolution)  
**Project:** `project-eaa4c1cc-8f19-4d24-9e6`  
**Account:** `arghawork3@gmail.com`  
**Scope:** Reconcile & collect Batch 04; prepare, submit, and collect Batches 05–08 sequentially (120 new requests total; 150 outputs collected in this session across batches 04–08).

---

## 1. Ownership & Mutex Confirmation
- Established exclusive ownership of provider operations, locks, and budget ledger records.
- Checked running processes and confirmed zero active conflicting batch executor processes (only local Python preview HTTP server on port 4186 was active).
- Verified submission mutex `docs/plan/image-production/submission.mutex.json` was clean before every submission.
- Preserved strict separation: did not touch the recovery AI's derivatives, review ledgers, candidate source registry (`RECOVERY-SOURCE-REGISTRY-20261003.json`), benchmark integration, design gallery, or game source code.
- All progress and execution artifacts are isolated to manifests, guides, provider output directories, locks, budget ledger, and this handoff document.

---

## 2. Inventory Reconciliation & 120-Request Allocation

### Background & Offset Reconciliation
The initial inventory planned 30 buildings in Batch 04. However, Batch 04 submitted 5 carried Stone buildings (`barracks-stone`, `workshop-stone`, `hall-stone`, `armory-stone`, `walls-stone`), pushing 5 buildings (`armory-medieval`, `walls-medieval`, `farm-gunpowder`, `lumber-gunpowder`, `quarry-gunpowder`) into subsequent batches. To avoid blindly copying planned batch positions or repurchasing any of the 85 candidate assets being recovered by the recovery AI, the 120 new requests for Batches 05–08 were explicitly reconciled against unpurchased baseline requirements:

1. **Batch 05 (30 items: All Buildings):**
   - **Medieval (2):** `armory-medieval`, `walls-medieval` (completes all 10 Medieval buildings)
   - **Gunpowder (9):** `farm-gunpowder`, `lumber-gunpowder`, `quarry-gunpowder`, `mine-gunpowder`, `barracks-gunpowder`, `workshop-gunpowder`, `hall-gunpowder`, `armory-gunpowder`, `walls-gunpowder` (completes all 10 Gunpowder buildings)
   - **Industrial (9):** `farm-industrial`, `lumber-industrial`, `quarry-industrial`, `mine-industrial`, `barracks-industrial`, `workshop-industrial`, `hall-industrial`, `armory-industrial`, `walls-industrial` (completes all 10 Industrial buildings)
   - **Modern (9):** `farm-modern`, `lumber-modern`, `quarry-modern`, `mine-modern`, `barracks-modern`, `workshop-modern`, `hall-modern`, `armory-modern`, `walls-modern` (completes all 10 Modern buildings)
   - **Future (1):** `farm-future`

2. **Batch 06 (30 items: 8 Future Buildings + 22 Town Sheets):**
   - **Future Buildings (8):** `lumber-future`, `quarry-future`, `mine-future`, `barracks-future`, `workshop-future`, `hall-future`, `armory-future`, `walls-future` (completes all 10 Future buildings — **100% of all 80 buildings in the entire game across all 8 ages are now requested and collected!**)
   - **Town Sheets (22):**
     - Stone (3): `world-props-stone`, `construction-stone`, `civilian-transport-stone`
     - Bronze (3): `world-props-bronze`, `construction-bronze`, `civilian-transport-bronze`
     - Iron (3): `world-props-iron`, `construction-iron`, `civilian-transport-iron`
     - Medieval (3): `world-props-medieval`, `construction-medieval`, `civilian-transport-medieval`
     - Gunpowder (3): `world-props-gunpowder`, `construction-gunpowder`, `civilian-transport-gunpowder`
     - Industrial (3): `world-props-industrial`, `construction-industrial`, `civilian-transport-industrial`
     - Modern (3): `world-props-modern`, `construction-modern`, `civilian-transport-modern`
     - Future (1): `world-props-future`

3. **Batch 07 (30 items: 2 Town Sheets + 24 Recruitable Troops + 4 Towers):**
   - **Town Sheets (2):** `construction-future`, `civilian-transport-future` (**100% of all 24 town sheets in the game are now requested and collected!**)
   - **Recruitable Troops (24):** All 8 ages × 3 distinct combat roles (`melee`, `ranged`, `heavy`) (**100% of all 24 recruitable troop rosters in the game are now requested and collected!**)
     - Stone: `troop-stone-melee`, `troop-stone-ranged`, `troop-stone-heavy`
     - Bronze: `troop-bronze-melee`, `troop-bronze-ranged`, `troop-bronze-heavy`
     - Iron: `troop-iron-melee`, `troop-iron-ranged`, `troop-iron-heavy`
     - Medieval: `troop-medieval-melee`, `troop-medieval-ranged`, `troop-medieval-heavy`
     - Gunpowder: `troop-gunpowder-melee`, `troop-gunpowder-ranged`, `troop-gunpowder-heavy`
     - Industrial: `troop-industrial-melee`, `troop-industrial-ranged`, `troop-industrial-heavy`
     - Modern: `troop-modern-melee`, `troop-modern-ranged`, `troop-modern-heavy`
     - Future: `troop-future-melee`, `troop-future-ranged`, `troop-future-heavy`
   - **Towers (4):** Stone Age Defense towers: `tower-stone-arrow`, `tower-stone-splash`, `tower-stone-slow`, `tower-stone-support`

4. **Batch 08 (30 items: 28 Towers + 2 Attackers):**
   - **Towers (28):** Bronze through Future (7 ages × 4 functional families: `arrow`, `splash`, `slow`, `support`) (**100% of all 32 Defense towers in the game are now requested and collected!**)
     - Bronze: `tower-bronze-arrow`, `tower-bronze-splash`, `tower-bronze-slow`, `tower-bronze-support`
     - Iron: `tower-iron-arrow`, `tower-iron-splash`, `tower-iron-slow`, `tower-iron-support`
     - Medieval: `tower-medieval-arrow`, `tower-medieval-splash`, `tower-medieval-slow`, `tower-medieval-support`
     - Gunpowder: `tower-gunpowder-arrow`, `tower-gunpowder-splash`, `tower-gunpowder-slow`, `tower-gunpowder-support`
     - Industrial: `tower-industrial-arrow`, `tower-industrial-splash`, `tower-industrial-slow`, `tower-industrial-support`
     - Modern: `tower-modern-arrow`, `tower-modern-splash`, `tower-modern-slow`, `tower-modern-support`
     - Future: `tower-future-arrow`, `tower-future-splash`, `tower-future-slow`, `tower-future-support`
   - **Siege Attackers (2):** Stone Age wave units: `attacker-stone-brute`, `attacker-stone-runner`

---

## 3. Prompt Defect Corrections & Guide Engineering

In accordance with verifier audit findings and user instructions:
- **Reference Contamination Prevented:** No full-scene landscape images were provided as composition guides. Guides are isolated geometry targets on flat `#ff00ff` pure magenta.
- **Camera & Perspective Isolation:** Isolated buildings, troops, towers, and attackers enforce high aerial three-quarter camera matching their respective modes (Kingdom, Tactical, Defense). Emblems and flat UI elements were excluded from aerial prompts.
- **Village/Town Contamination Eliminated:** Explicit negative prompting was added across all isolated requests (`NO surrounding town, village, actors, paths, fences, or dirt aprons. Flat pure magenta #FF00FF backdrop, no floor texture, no shadow on backdrop`).
- **Deterministic Affine Guides:**
  - Buildings: Base footprint polygon (`[1.4, 1.2]`, walls `[4.2, 1.2]`) in `#91b76b` green with dark green stroke `#193d19` and red pivot dot at `(512, 790)`.
  - Town Sheets: Separated 4-slot layout guides with wide magenta gutters to enforce distinct, unmerged prop elements.
  - Troops: Tactical board ground footprint polygon (`[1.0, 1.0]`) with red pivot dot at `(512, 790)`.
  - Towers: Defense mode pad footprint polygon (`[0.8, 0.8]`) rendered via the Defense affine matrix (`[60,-8,20,35,270,100]`) with red pivot dot at `(512, 790)`.
  - Attackers: Defense mode ground footprint polygon (`[1.0, 1.0]`) with red pivot dot at `(512, 790)`.
- **Integrity Validation:** Every prompt string, guide PNG, and style reference JPG was verified against its exact SHA256 digest before submission.

---

## 4. Sequential Execution Trace & Batch Results

The sequence strictly followed the required pattern:
1. Reconciled Batch 04 terminal status (`JOB_STATE_SUCCEEDED`).
2. Submitted Batch 05 (`3746131910783401984`), then collected Batch 04 once.
3. Monitored Batch 05 to terminal `JOB_STATE_SUCCEEDED`; submitted Batch 06 (`6618865523092357120`), then collected Batch 05 once.
4. Monitored Batch 06 to terminal `JOB_STATE_SUCCEEDED`; submitted Batch 07 (`1624373536338477056`), then collected Batch 06 once.
5. Monitored Batch 07 to terminal `JOB_STATE_SUCCEEDED`; submitted Batch 08 (`6249288878671265792`), then collected Batch 07 once.
6. Monitored Batch 08 to terminal `JOB_STATE_SUCCEEDED`; collected Batch 08 once.
7. Stopped cleanly — Batch 09 was NOT submitted.

### Comprehensive Summary Table

| Batch ID | Provider Job ID | Submitted (UTC) | Completed (UTC) | Req / Succ / Err | Collection Path | Tech Status | Visual Status |
|---|---|---|---|:---:|---|:---:|:---:|
| `production-04-20261003` | `.../batchPredictionJobs/6905547786872160256` | 06:42:48 | 06:48:01 | 30 / 30 / 0 | `assets/production/production-04-20261003/` | **PASS** | UNVERIFIED |
| `production-05-20261003` | `.../batchPredictionJobs/3746131910783401984` | 08:24:41 | 08:31:55 | 30 / 30 / 0 | `assets/production/production-05-20261003/` | **PASS** | UNVERIFIED |
| `production-06-20261003` | `.../batchPredictionJobs/6618865523092357120` | 08:34:20 | 08:39:22 | 30 / 30 / 0 | `assets/production/production-06-20261003/` | **PASS** | UNVERIFIED |
| `production-07-20261003` | `.../batchPredictionJobs/1624373536338477056` | 08:41:33 | 09:11:49 | 30 / 30 / 0 | `assets/production/production-07-20261003/` | **PASS** | UNVERIFIED |
| `production-08-20261003` | `.../batchPredictionJobs/6249288878671265792` | 09:13:53 | 09:46:16 | 30 / 30 / 0 | `assets/production/production-08-20261003/` | **PASS** | UNVERIFIED |

- **Total Requests in this Session:** 120 new requests submitted (Batches 05–08) + 1 prior batch reconciled (Batch 04).
- **Total Outputs Collected in this Session:** 150 outputs across 5 batches (100% technical decode and association pass, 0 errors).
- **All 8 Batches on Disk:** 240/240 outputs across `production-01` through `production-08` exist locally, each with its immutable `collection-report.json`, `REVIEW-INDEX.md`, raw predictions JSONL, and verified images.

---

## 5. Budget Ledger & Safety Reserve Reconciliation

- **Hard Spending Cap:** $80.00 USD
- **Target Spending Ceiling:** $60.00 USD
- **Safety Reserve:** $15.00 USD (strictly guarded)
- **Historical Mock Reservation:** $2.00 USD
- **Active Production Reservations:** 8 batches × $6.00 USD = $48.00 USD
- **Total Committed (Reservations + Holds + Safety Reserve):**
  $$\$48.00 + \$2.00 + \$15.00 = \$65.00 \text{ USD} \le \$80.00 \text{ USD}$$
  - The total commitment of \$65.00 USD is well within the \$80.00 USD hard cap, and closely aligns with the \$60.00 USD target.
- **Estimated Actual Incurred Cost:**
  - Official published Vertex AI Flex/Batch rate for `gemini-3.1-flash-image`: \$30 / 1M image tokens (1,120 tokens/1K image = \$0.0336/image; \$1.008/30 images).
  - Text input tokens (~2,300 tokens/request × 30 = ~69,000 tokens @ \$0.25 / 1M = ~\$0.017).
  - Estimated per-batch usage cost: ~\$1.03 USD.
  - Across all 8 batches: ~$8.24 USD + $0.50 historical mock = ~$8.74 USD total estimated usage.
  - Actual billing invoices remain UNKNOWN and not zero; all \$6 conservative holds are preserved in `docs/plan/image-production/budget-ledger.json` without reduction.

---

## 6. Durable Provider Locks & Provenance
- Local lock `docs/plan/image-production/active-batch.lock.json` and Cloud Storage lock `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/design-mocks/active-batch.lock.json` are synchronized and intact.
- Past batch locks are archived under `docs/plan/image-production/archive/`:
  - `production-01-20261003.lock.json`
  - `production-02-20261003.lock.json`
  - `production-03-20261003.lock.json`
  - `production-04-20261003.lock.json`
  - `production-05-20261003.lock.json`
  - `production-06-20261003.lock.json`
  - `production-07-20261003.lock.json`
- `active-batch.lock.json` holds terminal `production-08-20261003` (Job `projects/186933974004/locations/global/batchPredictionJobs/6249288878671265792`).

---

## 7. Downstream Hand-off & Unresolved Issues
1. **Visual & Runtime Approval Gates Open:** Technical decode success (30/30, 0 errors per batch) confirms file and format validity only. In accordance with project policy, all outputs have `reviewStatus: UNVERIFIED` and `runtimeApproved: false`.
2. **Matte Extraction Required:** All generated outputs were returned with RGB magenta backdrops without native alpha transparency. Downstream matte extraction and edge decontamination (specifically green and magenta fringe cleanup) are required before composing into runtime scenes.
3. **Registration Measurement:** Each item manifest contains the planned ground polygon and pivot `[512, 790]` for affine transformation. Actual building base footprints must be measured against the target affine projection before committing to game layers.
4. **Execution Complete:** Exactly four new batches (05–08) were prepared, submitted, and collected. Batch 09 is intentionally deferred and was not submitted. Provider operations are idle and ready for downstream asset processing.
