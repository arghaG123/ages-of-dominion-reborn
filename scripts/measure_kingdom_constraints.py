import os
import json
from PIL import Image
import numpy as np

print("Measuring Kingdom Terrain Constraints across all 8 Ages & Stone v4...")

# Load v2 layout candidate
cand_path = "qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json"
with open(cand_path, "r", encoding="utf-8") as f:
    cand = json.load(f)

sites = cand["geometry"]["sites"]
roads = cand["geometry"].get("roads", [])
camera = cand["camera"] # [60.0, -10.0, 25.0, 35.0, 170.0, 165.0]

# List terrain candidate files to inspect
terrain_files = {
    "stone_v4": "assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png",
    "stone_gen": "assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png",
    "bronze_gen": "assets/production/production-01-20261003/images/02-kingdom-terrain-bronze.png",
    "iron_gen": "assets/production/production-01-20261003/images/03-kingdom-terrain-iron.png",
    "medieval_gen": "assets/production/production-01-20261003/images/04-kingdom-terrain-medieval.png",
    "gunpowder_gen": "assets/production/production-01-20261003/images/05-kingdom-terrain-gunpowder.png",
    "industrial_gen": "assets/production/production-01-20261003/images/06-kingdom-terrain-industrial.png",
    "modern_gen": "assets/production/production-01-20261003/images/07-kingdom-terrain-modern.png",
    "future_gen": "assets/production/production-01-20261003/images/08-kingdom-terrain-future.png"
}

# Isometric transformation helper from world coordinates to source image coordinates
# Candidate uses sourceSize [1376, 768]
# Live high-res terrains are 5504x3072 or 1376x768
def project_world_to_pixel(wx, wy, img_w, img_h):
    # Using candidate camera parameters
    # Reference transform from candidate:
    # 1376x768 reference frame
    scale_x = img_w / 1376.0
    scale_y = img_h / 768.0
    # Isometric projection approximation based on camera angles
    # Center of world is around (5, 5)
    # Origin in screen space
    ox = 688.0 * scale_x
    oy = 384.0 * scale_y
    # Basis vectors
    vx_x = 95.0 * scale_x
    vx_y = 48.0 * scale_y
    vy_x = -95.0 * scale_x
    vy_y = 48.0 * scale_y
    
    px = ox + (wx - 5.0) * vx_x + (wy - 5.0) * vy_x
    py = oy + (wx - 5.0) * vx_y + (wy - 5.0) * vy_y
    return int(px), int(py)

terrain_audit_results = {}

for name, fpath in terrain_files.items():
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
    
    im = Image.open(fpath)
    w, h = im.size
    arr = np.array(im)
    
    # Analyze water / river distribution
    # River in isometric terrain typically has high Blue / Cyan or reflective contrast
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Water detector: blue dominant or green-blue water
    water_mask = (b > r + 15) & (b > 60)
    water_fraction = float(water_mask.mean())
    
    # Inspect terrain obstacles at pad sites
    site_conflicts = []
    
    for s in sites:
        sid = s["id"]
        rx, ry, rw, rh = s["rect"]
        # Center of site in world units
        scx = rx + rw / 2.0
        scy = ry + rh / 2.0
        
        px, py = project_world_to_pixel(scx, scy, w, h)
        
        # Check if projected site falls on water or high-frequency obstacle
        in_bounds = (0 <= px < w) and (0 <= py < h)
        if in_bounds:
            # Sample 20x20 neighborhood around center
            x1 = max(0, px - 15)
            x2 = min(w, px + 15)
            y1 = max(0, py - 15)
            y2 = min(h, py + 15)
            
            patch = arr[y1:y2, x1:x2]
            p_water = float(water_mask[y1:y2, x1:x2].mean())
            # Texture roughness / edge density
            p_std = float(np.std(patch))
            
            conflict_type = None
            if p_water > 0.2:
                conflict_type = "WATER_OVERLAP"
            elif p_std > 45.0:
                conflict_type = "BAKED_STRUCTURE_OR_OBSTACLE"
                
            if conflict_type:
                site_conflicts.append({
                    "siteId": sid,
                    "conflict": conflict_type,
                    "screenCoord": [px, py],
                    "waterRatio": p_water,
                    "localStd": p_std
                })

    # Summary verdict for this age
    terrain_audit_results[name] = {
        "file": fpath,
        "resolution": [w, h],
        "waterFraction": water_fraction,
        "siteConflictsCount": len(site_conflicts),
        "siteConflicts": site_conflicts,
        "bareTerrainFeasibility": "FAIL_REQUIRES_NEW_GENERATION" if len(site_conflicts) > 3 else "PARTIAL_OBSTACLES"
    }
    print(f"[{name:15s}]: Size={w}x{h}, Water={water_fraction*100:.1f}%, Site Conflicts={len(site_conflicts)}")

out_audit_path = "docs/plan/KINGDOM-REPAIR-CONSTRAINTS-2026-10-04.json"
with open(out_audit_path, "w", encoding="utf-8") as f:
    json.dump(terrain_audit_results, f, indent=2)

print(f"\nMeasurement complete. Results written to {out_audit_path}")
