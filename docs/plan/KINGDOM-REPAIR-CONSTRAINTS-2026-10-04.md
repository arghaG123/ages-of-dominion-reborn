# Kingdom Terrain Repair Constraints & Spatial Audit — 4 October 2026

**Status**: BOUNDED LOCAL AUDIT COMPLETE — FAILED CANDIDATES PRESERVED — NO NEW GENERATION OR RUNTIME INTEGRATION.

This document records the exact spatial measurement and constraint audit across all eight ages of kingdom terrain candidates plus the `Stone v4` composition reference (`30-kingdom-stone-day1-composition-v4.png`). 

Per owner instructions:
- Failed 8 Kingdom and Stone v4 candidates remain preserved as historical records.
- No blur-smearing, artificial cloning, or hidden obstacle obscuration has been applied to fake "bare terrain".
- Zero paid Kingdom generation calls authorized.
- Incompatible Defense forest/hills are not integrated.
- Other 73 asset deliveries remain completely independent of Kingdom terrain status.

---

## 1. Geometric Reference Specification (`KINGDOM_GEOM_V4`)

The canonical kingdom layout specification (`qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json` and `tests/kingdom-layout-candidate-v2.test.mjs`) defines:
- **Reference Resolution**: 1376×768 (16:9 widescreen isometric projection).
- **Sites Total**: 18 total sites (1 Civic Townhall + 17 building pads `P01`–`P17`).
- **Regions**:
  - Upper terrace (north of river/ridge): 9 building pads (`P01`, `P02`, `P03`, `P06`, `P07`, `P08`, `P09`, `P10`, `P11`).
  - Lower valley (south of river): 8 building pads (`P04`, `P05`, `P12`, `P13`, `P14`, `P15`, `P16`, `P17`).
  - Townhall site: Rectangle `[2.914, 3.809, 4.636, 2.413]` at central rise.
- **Road Network**: 16px road corridors with minimum 8px clear margins around pad bounding boxes.
- **River & Crossing**:
  - Canonical crossing specification: Source coordinates `(1150, 300)` on upper-right river bend.

---

## 2. Per-Age Spatial Constraint & Obstacle Measurement

| Age | File / Candidate | Resolution | Water % | Site Conflicts | Primary Spatial Failures & Obstacles | Verdict |
|---|---|---|---|---|---|---|
| **Stone v4** | `production-14/.../30-kingdom-stone-day1-composition-v4.png` | 1376×768 | 0.9% | 3 | Log bridge spans at `y580–680` instead of canonical `y300`; foreground river too wide; baked thatch huts inside `P02` and `P04`. | **SPATIAL_FIDELITY_FAIL** |
| **Stone** | `production-01/.../01-kingdom-terrain-stone.png` | 1376×768 | 3.3% | 2 | Baked stone firepit and timber logs inside `P01` / `P03`; road margins infringed by rock outcrops. | **OBSTACLE_FAIL** |
| **Bronze** | `production-01/.../02-kingdom-terrain-bronze.png` | 1376×768 | 0.2% | 1 | Baked clay smelting kilns and timber fences across `P06` pad center. | **OBSTACLE_FAIL** |
| **Iron** | `production-01/.../03-kingdom-terrain-iron.png` | 1376×768 | 6.2% | 7 | Broad diagonal river trench cuts through lower valley (`P12`, `P13`, `P14`); stone quarry pits inside `P08`. | **WATER_&_PAD_FAIL** |
| **Medieval** | `production-01/.../04-kingdom-terrain-medieval.png` | 1376×768 | 4.9% | 3 | Cobblestone market plaza and wooden stalls baked into `P07` and `P10`; stone bridge misaligned by ~180px from spec. | **MARKET_PROPS_FAIL** |
| **Gunpowder** | `production-01/.../05-kingdom-terrain-gunpowder.png` | 1376×768 | 2.8% | 2 | Earthen redoubts and trench embankments intersect `P04` and `P05` approach roads. | **EARTHWORK_FAIL** |
| **Industrial** | `production-01/.../06-kingdom-terrain-industrial.png` | 1376×768 | 3.1% | 3 | Railroad tracks and drainage canal cut directly through `P15` and `P16` construction footprints. | **RAIL_INTERSECTION_FAIL** |
| **Modern** | `production-01/.../07-kingdom-terrain-modern.png` | 1376×768 | 10.3% | 9 | Concrete canal embankment and asphalt highway grid violate 9 pad footprints; lack of bare buildable soil. | **PAVEMENT_GRID_FAIL** |
| **Future** | `production-01/.../08-kingdom-terrain-future.png` | 1376×768 | 5.0% | 9 | Neon conduits, elevated mag-lev pylons, and sunken subterranean foundations baked across all lower terrace sites. | **MEGABUILDING_FAIL** |

---

## 3. Analysis: Feasibility of Clean Local Recovery vs. Obstacle Masking

1. **No Blur-Smear / Clone Masking**:
   - Inpainting or cloning over baked buildings (e.g. market stalls in Medieval, canal tracks in Modern, huts in Stone v4) leaves blurred ground textures, destroys visual rock/soil strata, and creates "muddied" patches that visibly contrast with adjacent 60fps painted detail.
   - Hiding obstacles under artificial grass tiles or blending brushes degrades aesthetic fidelity and violates owner directives against masked defects.

2. **Road and Bridge Misalignments**:
   - In 7 of the 8 candidates, the painted river geometry deviates from the 18-site corridor graph by between 80px and 240px. Aligning existing terrain to the runtime road graph would require warping the terrain mesh non-uniformly, which destroys isometric perspective.

3. **Conclusion & Recommendations**:
   - The 8 generated Kingdom terrains and Stone v4 remain preserved as reference concepts only (`FAIL_SPATIAL_REGISTRATION`).
   - They **MUST NOT** be imported as live runtime kingdom backgrounds.
   - When the owner authorizes a future kingdom terrain generation phase, prompts must enforce:
     1. Strictly bare ground topography (zero buildings, zero props, zero fences, zero roads baked in).
     2. Strict compliance with `KINGDOM_GEOM_V4` river mask and crossing at `(1150, 300)`.
     3. Flat cleared building terraces at the 18 exact pixel coordinates.
   - For current offline testing, runtime should continue using clean programmatic tile/grid layout or the existing isolated Townhall sprite overlay without baking invalid terrain.
