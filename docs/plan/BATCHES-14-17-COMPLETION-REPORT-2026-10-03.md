# Batches 14–17 Execution & Collection Completion Report

**Date:** 2026-10-03  
**Role:** Image-Batch Executor  
**Authority:** Owner Four-Batch Directive (Batches 14, 15, 16, 17)  
**Status:** COMPLETE — ALL FOUR BATCHES SUBMITTED, TERMINAL SUCCEEDED, AND COLLECTED

---

## 1. Executive Summary

Per explicit owner instructions, the image-batch executor has prepared, submitted, monitored, and collected all four authorized batches: **`production-14`**, **`production-15`**, **`production-16`**, and **`production-17`**.

- **Total Requests Prepared & Submitted:** Exactly 120 new useful requests (30 per batch).
- **Total Outputs Collected:** Exactly 120 new production images downloaded to disk in `assets/production/production-{14..17}-20261003/images/`.
- **Collection Errors:** 0 errors across all 120 files. Technical status: **`PASS`** on all four batches.
- **Cumulative Production Originals:** 510 production images across Batches 01–17 (all 510 distinct SHA256 hashes).
- **Execution Protocol:** Strict single-active-job mutex maintained. The sequential pipeline rule ("submit authorized Batch $N+1$ *before* collecting Batch $N$") was enforced on every transition. Collection of Batch 17 was executed without initiating any Batch 18+.
- **Budget Compliance:** Reconciled liabilities for all 17 batches + $2.00 historical hold + $15.00 safety reserve = **$57.225 USD**, cleanly meeting the owner's **$60.00 USD target** ($2.775 USD surplus headroom) and well within the **$80.00 USD hard cap** ($22.775 USD headroom).

---

## 2. Batch Execution Ledger & Transitions

| Batch ID | Provider Job Resource ID | Submitted (UTC) | Terminal State | Collected (UTC) | Outputs | Errors | Prompt Tokens | Candidate Tokens |
|---|---|---|---|---|---|---|---|---|
| **production-14-20261003** | `projects/186933974004/locations/global/batchPredictionJobs/9013425926528040960` | 2026-10-03 13:50:01 | `JOB_STATE_SUCCEEDED` | 2026-10-03 14:03:47 | 30 | 0 | 38,969 | 33,600 |
| **production-15-20261003** | `projects/186933974004/locations/global/batchPredictionJobs/7110655083964006400` | 2026-10-03 14:03:22 | `JOB_STATE_SUCCEEDED` | 2026-10-03 14:13:22 | 30 | 0 | 37,770 | 33,600 |
| **production-16-20261003** | `projects/186933974004/locations/global/batchPredictionJobs/7070967112247803904` | 2026-10-03 14:13:03 | `JOB_STATE_SUCCEEDED` | 2026-10-03 14:50:16 | 30 | 0 | 37,779 | 33,724 |
| **production-17-20261003** | `projects/186933974004/locations/global/batchPredictionJobs/5827973615093547008` | 2026-10-03 14:49:54 | `JOB_STATE_SUCCEEDED` | 2026-10-03 15:22:43 | 30 | 0 | 37,649 | 33,600 |
| **Totals (14–17)** | — | — | — | — | **120** | **0** | **152,167** | **134,524** |

### Transition Verification:
1. **Batch 14 -> Batch 15:** Batch 14 reached `JOB_STATE_SUCCEEDED` at 13:50 UTC. Batch 15 was submitted at 14:03:22 UTC. Collection of Batch 14 commenced at 14:03:31 UTC and finished at 14:03:47 UTC. (Rule obeyed: 15 submitted *before* 14 collected).
2. **Batch 15 -> Batch 16:** Batch 15 reached `JOB_STATE_SUCCEEDED` at 14:09:29 UTC. Batch 16 was submitted at 14:13:03 UTC. Collection of Batch 15 commenced at 14:13:07 UTC and finished at 14:13:22 UTC. (Rule obeyed: 16 submitted *before* 15 collected).
3. **Batch 16 -> Batch 17:** Batch 16 reached `JOB_STATE_SUCCEEDED` at 14:46:05 UTC. Batch 17 was submitted at 14:49:54 UTC. Collection of Batch 16 commenced at 14:50:01 UTC and finished at 14:50:16 UTC. (Rule obeyed: 17 submitted *before* 16 collected).
4. **Batch 17 Termination:** Batch 17 reached `JOB_STATE_SUCCEEDED` at 15:22:22 UTC. Collection of Batch 17 commenced at 15:22:26 UTC and finished at 15:22:43 UTC. Batch 18 was **NOT** initiated.

---

## 3. Scope Delivery & Inventory Reconciliation

### A. 100% Canonical Equipment Coverage Achieved (128 Items Total)
The canonical equipment system defines 128 equipment items (8 ages × 4 hero classes × 6 equipment slots).
- Batches 01–13 requested and collected 33 equipment items (including `gear-industrial-boots` collected in Batch 13 position 30).
- Batches 14–17 requested and collected the remaining 95 equipment items:
  - Batch 14: 29 equipment items (positions 01–29)
  - Batch 15: 30 equipment items (positions 01–30: Future, Stone, Bronze, Iron)
  - Batch 16: 30 equipment items (positions 01–30: Iron, Medieval, Gunpowder, Industrial)
  - Batch 17: 6 equipment items (positions 01–06: Industrial weapons/armor)
- **Result:** Exactly 128 / 128 equipment IDs are present on disk with clean silhouettes and pure magenta backgrounds.

### B. Seven Evidenced Heavy / Siege Unit Identity Corrections
All 7 canonical unit corrections were requested in Batch 17 (positions 07–13) and collected:
1. `attacker-bronze-heavy` (Position 07): Bronze Charioteer with two horses and spearman crew.
2. `attacker-iron-heavy` (Position 08): Iron War Elephant with armored howdah and archer/mahout.
3. `attacker-gunpowder-heavy` (Position 09): Gunpowder Cannon Crew with wheeled bronze field cannon.
4. `attacker-industrial-heavy` (Position 10): Industrial Steam Walker combat automaton with riveted iron plates.
5. `attacker-modern-heavy` (Position 11): Modern Main Battle Tank with composite turret and tracked chassis.
6. `attacker-future-heavy` (Position 12): Future Hover Tank with repulsor skirt and plasma pulse cannon.
7. `tower-iron-splash` (Position 13): Iron Splash Siege Onager with counterweight arm and boulder basket.

### C. Seven Canonical Missing Artifacts
Requested in Batch 17 (positions 14–20) and collected:
1. `artifact-wolfamulet`: Wolf Fang Amulet
2. `artifact-bloodstone`: Bloodstone Pendant
3. `artifact-clover`: Four-Leaf Clover Talisman
4. `artifact-lens`: Scholar's Focusing Lens
5. `artifact-vitality`: Ring of Vitality
6. `artifact-swiftboots`: Swift Boots Charm
7. `artifact-codex`: Ancient Battle Codex

### D. Five Canonical Missing Spell Effects
Requested in Batch 17 (positions 21–25) and collected:
1. `spell-fireball`: Fireball explosion shockwave burst
2. `spell-slow`: Slow temporal cold ice/mud vortex
3. `spell-cure`: Holy healing radiant bloom aura
4. `spell-haste`: Haste velocity wind glyph
5. `spell-bless`: Divine blessing celestial halo crest

### E. Five Creature / Mount Harness Plates
Requested in Batch 17 (positions 26–30) and collected:
1. `mount-dire-wolf`: Armored Dire Wolf war mount
2. `mount-cave-bear`: Heavy War Cave Bear beast plate
3. `mount-warhorse`: Armored Warhorse Destrier saddle harness
4. `mount-motorcycle`: Combat Assault Motorcycle chassis plate
5. `mount-repulsor`: Repulsor Combat Skimmer Mount chassis

---

## 4. Pixel Review: Stone Day 1 Kingdom Composition Reference (v4)

**File:** `assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png`  
**Dimensions:** 1376 × 768 px (16:9 Landscape)  
**Format:** PNG, RGB, 24-bit  
**SHA256:** `5dfdc20e8724acf48781ceae15d00a35899c855a26408a8e7656f84165f23c76`  
**Spatial Guide Used:** `docs/plan/image-production/guides/kingdom-stone-day1-composition-v4.png` (SHA256: `468ee7a897eb934d965a26a44c8644bce1c1524468802d7531c354720cd0f014`)

### A. Architectural & Physical Identity Inspection
- **Town Hall Prominence:** Exactly ONE prominent, complete Stone Town Hall built from authentic Stone Age materials: timber frame, thatched roof, hide fastenings, rough stone footings, and wooden columns.
- **Roof Apex Framing:** In previous versions (v2/v3), the roof was clipped off at the top border. In v4, the entire thatched roof ridge, projecting diagonal cross-timbers, and roof gables are 100% visible inside the frame (vertical bounds $y \approx 40$ to $373$). Above the roof, clear hillside greenery and forest margins provide breathing room.
- **Grounding & Entrance:** The Town Hall sits firmly on the upper civic terrace with organic contact shadows, stone foundation footings, and a clear dirt/cobble entrance path. No floating, warping, or artificial ground island.
- **Clearings & Building Plots:** 17 empty, natural building clearings connected by soil paths. No artificial UI rectangles, plus marks, numbers, or neon grid lines. Clearings are unencumbered by unintended buildings or clutter.
- **Perimeter & Defenses:** Perimeter is completely unbuilt. No stone walls, no towers, and no gatehouse. The natural cliff perimeter and riverside slope form the natural boundaries.
- **Landscape Geography:** Clear river-right geography with rocky cliffs, green pines/deciduous trees, and an age-appropriate stepping-stone and log crossing in the lower-right foreground.
- **Lighting & Camera:** Coherent high aerial three-quarter strategy camera angle with warm upper-left sunlight and consistent soft shadows cast to the lower-right. No HUD elements, buttons, text, or watermarks.

### B. Display Framing Assessment Across Target Viewports
1. **1280 × 720 (16:9 HD Standard):**
   - **Status:** **PASS**
   - **Details:** Aspect matches generation ratio almost exactly (1.78 vs 1.79). 100% of Town Hall, all 17 plots, river, and crossing are visible without cropping.
2. **1180 × 820 (Tablet Landscape ~1.44:1):**
   - **Status:** **PASS**
   - **Details:** Width cropped by ~135 px on left and right. Civic terrace, Town Hall, interior plots, and central river crossing remain fully in-bounds. Outer wilderness margins trimmed cleanly.
3. **825 × 375 & 933 × 424 (Mobile Ultra-wide Landscape ~2.2:1):**
   - **Status:** **PASS (with Camera Anchoring)**
   - **Details:** Height is cropped by ~143 px. Pure symmetrical vertical centering (crop $y = 71..696$) would trim the top ~30 px of the roof timber peaks. However, in game camera framing anchored slightly towards the top ($y = 30..655$), the entire Town Hall roof ridge, the complete civic terrace, plots, and river crossing are preserved in-frame.

### C. Acceptance Gate Summary
- **Technical Collection:** **`PASS`** (valid decode, exact 1376×768 resolution, 0 errors).
- **Composition & Aesthetics:** **`PASS`** (resolves prior Hall clipping, provides clear plots, authentic Stone architecture, coherent river-right geography).
- **Runtime & Playable Delivery:** **`UNVERIFIED / PENDING SEPARATE RECOVERY`** (This image is a composition review reference. Extraction of terrain background, individual building sprites, and runtime coordinate registration remain separate technical deliverables for the coding/recovery phase).

---

## 5. Budget Ledger & Liability Reconciliation

### Measured Usage Across Batches 14–17:
- **Batch 14:** 38,969 prompt tokens, 33,600 candidate tokens
- **Batch 15:** 37,770 prompt tokens, 33,600 candidate tokens
- **Batch 16:** 37,779 prompt tokens, 33,724 candidate tokens
- **Batch 17:** 37,649 prompt tokens, 33,600 candidate tokens
- **Total New Tokens (14–17):** 152,167 input tokens, 134,524 candidate tokens

### Cumulative Usage Across Batches 01–17:
- **Total Input Tokens:** 985,482
- **Total Output Tokens:** 574,764
- **Total Tokens:** 1,560,246

### Financial Reconciliation Under Standard Gemini 3.1 Flash Image Tariff:
- Standard Rates: $0.50 / 1M input tokens, $60.00 / 1M image output tokens
- Token Standard Cost (all 17 batches): $(985,482 \times 0.50 / 10^6) + (574,764 \times 60.00 / 10^6) = \$0.493 + \$34.486 = \$34.979\text{ USD}$
- 15% Operational & GCS Storage Buffer: $\$34.979 \times 0.15 = \$5.247\text{ USD}$
- **Reconciled 17-Batch Work Liability:** **$40.225 USD** (Batches 01–13: $30.856 USD + Batches 14–17: $9.369 USD)
- **Historical Mock Reservation Hold:** **$2.000 USD**
- **Safety Reserve (Mandatory):** **$15.000 USD**
- **Total Protected Commitments:** **$57.225 USD**

### Budget Threshold Checks:
- **Owner Target ($60.00 USD):** $\$57.225 \le \$60.00$ (**MET** with **$2.775 USD** headroom).
- **Hard Cap ($80.00 USD):** $\$57.225 \le \$80.00$ (**MET** with **$22.775 USD** headroom).
- **Safety Reserve ($15.00 USD):** 100% preserved.

---

## 6. Shared Cloud & Local Mutex Lock State

- **Local Lock File:** `docs/plan/image-production/active-batch.lock.json`
- **Cloud Lock Object:** `gs://project-eaa4c1cc-8f19-4d24-9e6-aod-batch/production/active-batch.lock.json` (Generation: `1791041108322430`)
- **Lock State:**
  ```json
  {
    "batch_id": "production-17-20261003",
    "model": "gemini-3.1-flash-image",
    "project": "project-eaa4c1cc-8f19-4d24-9e6",
    "account": "arghawork3@gmail.com",
    "state": "JOB_STATE_SUCCEEDED",
    "workflow_state": "TERMINAL_COLLECTED",
    "requestedOutputs": 30,
    "reservedUSD": 6,
    "provider_job_name": "projects/186933974004/locations/global/batchPredictionJobs/5827973615093547008",
    "cloud_lock_generation": "1791041108322430",
    "owner_status": "PRODUCTION_ASSETS_UNVERIFIED",
    "assetApproval": "UNVERIFIED"
  }
  ```
- **Active / Unknown Jobs in GCP Project:** **0 active, 0 unknown.** All 17 production jobs and 2 historical test jobs are terminal.

---

## 7. Quality Gates & Test Verification

1. **`npm test`**: **41 / 41 PASS** (0 failures). Domain validation, movement predicates, save checks, coordinate round-tripping, combat rules, and 8-age equipment contracts all verified.
2. **`python scripts/review_gates.py`**: **PASS** (510 fresh rows, 0 stale, 510 published assets).
3. **`python scripts/discover-local-collections.py`**: **PASS** (510 originals on disk, 504 distinct IDs, 0 hash mismatches).
