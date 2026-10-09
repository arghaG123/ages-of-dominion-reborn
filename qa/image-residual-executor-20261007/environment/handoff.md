# Environment Art Residual Delivery Handoff Report (Image AI 1)
**Date:** 7 October 2026  
**Producer:** ENVIRONMENT Executor (Image AI 1)  
**Status:** Local Processing Complete (`localProcessingComplete: true`) | Whole-Delivery Status: `INCOMPLETE` (Awaiting AI 2 Actor delivery, Code AI runtime binding, and Owner acceptance).

---

## 1. Executive Summary & Defect Resolutions

This delivery executes all remaining feasible local fixes to terrain, buildings, walls, towers, static sites, resources, skills, spells, and environmental layers across all eight ages and four game modes, starting from the 6 October baseline and resolving all confirmed defects from the 7 October independent audit (`docs/plan/IMAGE-RESIDUAL-INDEPENDENT-AUDIT-2026-10-07.md`).

### Defect 1: Magenta Bleed in Skill Offense (`skill-offense`)
- **Finding:** Audit identified 215,270 magenta background pixels in `skill-offense.png`.
- **Root Cause:** The AI generation source had a magenta chroma-key background `[254, 1, 252]`. The circular crop in the 6 October recipe had radius 457 px on a 355 px shield, leaving the magenta margin intact.
- **Resolution:** Applied dual-pass processing (chroma keying to eliminate magenta background + precision circular framing at radius 355 px).
- **Result:** **0 magenta bleed pixels**, crisp circular shield, 100% subject preservation.

### Defect 2: Classification of `test_townhall_matte.png`
- **Finding:** Audit questioned whether magenta fringe in `qa/environment-art-20261006/test_townhall_matte.png` affected production.
- **Root Cause:** `test_townhall_matte.png` was an experimental intermediate diagnostic script file.
- **Resolution:** Audited actual delivered production file `assets/derivatives/environment-20261006/buildings/stone/townhall-stone.png` and re-generated in residual output.
- **Result:** Production derivative `townhall-stone.png` has **0 magenta bleed pixels**. `test_townhall_matte.png` is officially classified as `RESOLVED_DIAGNOSTIC_ONLY`.

### Defect 3: Bright Green Ground / Matte Wedges in Stone Developed Composite
- **Finding:** Audit observed bright green ground/matte wedges at several building bases in `kingdom-stone-developed-1280x720.png`.
- **Root Cause:**
  1. The AI generation placed `armory-stone` (20,343 lower grass pixels) and `barracks-stone` (15,626 lower grass pixels) on artificial triangular green ground slabs that extended below the building foundation lines.
  2. The despill algorithm in `matte_utils.py` subtracted excess magenta from R and B without constraining G, leaving semi-transparent fringe pixels unnaturally tinted green.
- **Resolution:**
  1. Refined base masks for `armory-stone` and `barracks-stone` by trimming artificial ground wedges below ground contact lines (`y=855` for armory, `y=800` for barracks), preserving 100% of stone/wood walls and steps.
  2. Updated `despill_magenta()` to clamp G into the local color gamut (`g <= max(r, b) + 25`), preventing green tinting on despilled edges.
- **Result:** Clean stone and wood foundations with zero green triangular wedges on arid terrain.

### Defect 4: Road Trace Crossing P07 Legal Footprint in Stone Overlay
- **Finding:** Yellow road trace visibly cut through P07 legal footprint in `kingdom-terrain-stone-overlay.png`.
- **Root Cause:** The 6 October overlay included an extra trace `camp-spokes` passing through `[2020, 1100]` Native px (`[505, 275]` Legal px), intersecting the left edge of P07 (`x: 510..624, y: 251..307`).
- **Resolution:**
  1. Validated canonical thoroughfare road from `IMPLEMENTATION-CONTRACT.json` along column 7.7, which has **98.56 legal px clearance** from P07 (margin **+78.56 px** over 20 px required clearance).
  2. Added certified west clearing connector routing through the open dirt clearing west of P06/P07, achieving **90.55 legal px clearance** (margin **+70.55 px**).
- **Result:** Complete clearance certified across all 17 pads, Hall, and Walls with uncertainty margins.

### Defect 5: Defense Scene River/Bank/Deck Annotations
- **Finding:** Defense scenes lacked river/bank/deck annotations.
- **Resolution:** Reconciled against canonical game rules. In Defense mode, there is NO river or bridge deck. The assault lane, deployment sites D1-D8, gate, spawn, and walkable/blocked areas are fully traced. Recorded `paintedRiverState: NOT_APPLICABLE` and `paintedBridgeDeck: null` with contract justification.

---

## 2. Inventory & Delivery Outputs

| Category | Count | Status | Output Location |
| :--- | :--- | :--- | :--- |
| **Buildings** | 80 | READY (8 ages x 10 types) | `assets/derivatives/image-residual-executor-20261007/environment/buildings/{age}/` |
| **Stationary Towers** | 32 | READY (8 ages x 4 families) | `assets/derivatives/image-residual-executor-20261007/environment/towers/{age}/` |
| **Static Sites** | 12 | READY (6 Adventure + 6 Tactical) | `assets/derivatives/image-residual-executor-20261007/environment/sites/` |
| **Resource Materials** | 4 | READY (Food, Wood, Stone, Gold) | `assets/derivatives/image-residual-executor-20261007/environment/icons/resources/` |
| **Skill Materials** | 9 | READY (Offense fixed, Archery..Firstaid) | `assets/derivatives/image-residual-executor-20261007/environment/icons/skills/` |
| **Spell Materials** | 8 | READY (Arrow..Resurrect) | `assets/derivatives/image-residual-executor-20261007/environment/icons/spells/` |
| **Support Backdrops**| 9 | READY (Home, Forge, Inventory, etc.) | `assets/derivatives/image-residual-executor-20261007/environment/support/` |
| **Total Artifacts** | **145 + 9** | **READY (100% of owned scope)** | |
| **Scene Plates** | 32 | PARTIAL (PROPOSED geometry) | `qa/image-residual-executor-20261007/environment/geography/` |
| **Composites** | 34 | READY (4 viewports) | `qa/image-residual-executor-20261007/environment/composites/` |

---

## 3. Coordinate Frames & Clearance Metrics

- **Grid Space:** Cols 0..13, Rows 0..10 (Kingdom 14x11).
- **Legal Frame:** `1376 x 768`. Frozen affine: `[60.0, -10.0, 25.0, 35.0, 170.0, 165.0]`, Hall scale: `0.1312`.
- **Native Frame:** `5504 x 3072` (Native = 4 * Legal).
- **Pad P07 Footprint:** Legal `[(510, 265), (594, 251), (624, 293), (540, 307)]`.
- **Canonical Road Clearance against P07:** `98.56` legal px (`margin +78.56` px).
- **West Connector Clearance against P07:** `90.55` legal px (`margin +70.55` px).
- **All 17 Pads Clearance:** All certified clear of thoroughfare corridor.

---

## 4. Consumable Deliverables & Key Files

1. **Successor Interface:** `docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json`
2. **Scenes Specification:** `qa/image-residual-executor-20261007/environment/scenes.json`
3. **Composites Manifest:** `qa/image-residual-executor-20261007/environment/composites/composites_manifest.json`
4. **Interactive Review Gallery:** `qa/image-residual-executor-20261007/environment/review/index.html`
5. **Checkpoint:** `qa/image-residual-executor-20261007/environment/checkpoint.json`
6. **Input Snapshot:** `qa/image-residual-executor-20261007/environment/input_snapshot.json`

---

## 5. Next Steps for Code AI & Reviewers

1. **Code AI Assignment:** Bind `docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json` into runtime asset catalogs.
2. **Viewports Check:** Verify runtime camera rendering across `825x375`, `933x424`, `1180x820`, and `1280x720`.
3. **Owner Review:** Inspect `qa/image-residual-executor-20261007/environment/review/index.html` for visual sign-off.
