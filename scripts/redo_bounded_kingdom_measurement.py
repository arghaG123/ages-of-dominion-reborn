import os, json, hashlib
from PIL import Image
import numpy as np

ROOT = 'C:/dev/ages-of-dominion-reborn'
QA_DIR = f'{ROOT}/qa/offline-controls-repair-20261004'
os.makedirs(QA_DIR, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# Load Active Contract
c1_path = f'{ROOT}/docs/plan/IMPLEMENTATION-CONTRACT.json'
c1_data = json.load(open(c1_path))
c1_geo = c1_data['geometry']['kingdom']
c1_sha256 = compute_sha256(c1_path)

# Load Candidate-v2
c2_path = f'{ROOT}/qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json'
c2_data = json.load(open(c2_path))
c2_geo = c2_data['geometry']
c2_sha256 = compute_sha256(c2_path)

# Camera / Affine Matrix: [a, b, c, d, tx, ty]
# x_src = a * wx + c * wy + tx
# y_src = b * wx + d * wy + ty
M = [60.0, -10.0, 25.0, 35.0, 170.0, 165.0]
REF_W, REF_H = 1376.0, 768.0

# Determinant and inverse matrix
det = M[0] * M[3] - M[1] * M[2] # 60*35 - (-10)*25 = 2100 + 250 = 2350
inv_M = [
    M[3] / det,      # 35 / 2350
    -M[1] / det,     # 10 / 2350
    -M[2] / det,     # -25 / 2350
    M[0] / det       # 60 / 2350
]

def world_to_ref_pixel(wx, wy):
    px = M[0] * wx + M[2] * wy + M[4]
    py = M[1] * wx + M[3] * wy + M[5]
    return px, py

def ref_pixel_to_world(px, py):
    dx = px - M[4]
    dy = py - M[5]
    wx = inv_M[0] * dx + inv_M[2] * dy
    wy = inv_M[1] * dx + inv_M[3] * dy
    return wx, wy

# Terrain files
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

def analyze_contract_sites(contract_name, sites_list, bridges_list, terrain_name, img_path):
    im = Image.open(f'{ROOT}/{img_path}').convert('RGB')
    w, h = im.size
    scale_x = w / REF_W
    scale_y = h / REF_H
    arr = np.array(im, dtype=int)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    
    # Safe water classification (NO uint8 overflow):
    # River / water has blue dominance over red by at least 15 and sufficient brightness
    water_mask = (b > (r + 15)) & (b > 60)
    
    # Analyze sites
    site_measurements = []
    for s in sites_list:
        sid = s['id']
        rx, ry, rw, rh = s['rect']
        cx = rx + rw / 2.0
        cy = ry + rh / 2.0
        
        px_ref, py_ref = world_to_ref_pixel(cx, cy)
        px_img = int(px_ref * scale_x)
        py_img = int(py_ref * scale_y)
        
        # Calculate polygon corner projections
        corners_world = [
            (rx, ry),
            (rx + rw, ry),
            (rx + rw, ry + rh),
            (rx, ry + rh)
        ]
        corners_img = []
        for c_wx, c_wy in corners_world:
            c_px, c_py = world_to_ref_pixel(c_wx, c_wy)
            corners_img.append([int(c_px * scale_x), int(c_py * scale_y)])
            
        in_bounds = (0 <= px_img < w) and (0 <= py_img < h)
        patch_water_fraction = 0.0
        patch_roughness = 0.0
        
        if in_bounds:
            x1 = max(0, px_img - int(20 * scale_x))
            x2 = min(w, px_img + int(20 * scale_x))
            y1 = max(0, py_img - int(20 * scale_y))
            y2 = min(h, py_img + int(20 * scale_y))
            
            patch_water = water_mask[y1:y2, x1:x2]
            patch_water_fraction = float(patch_water.mean()) if patch_water.size > 0 else 0.0
            patch_rgb = arr[y1:y2, x1:x2]
            patch_roughness = float(np.std(patch_rgb)) if patch_rgb.size > 0 else 0.0
            
        conflict = None
        if not in_bounds:
            conflict = "OUT_OF_BOUNDS"
        elif patch_water_fraction > 0.15:
            conflict = f"WATER_OVERLAP ({patch_water_fraction*100:.1f}%)"
        elif patch_roughness > 45.0:
            conflict = f"HIGH_TEXTURE_ROUGHNESS_OBSTACLE ({patch_roughness:.1f})"
            
        site_measurements.append({
            'siteId': sid,
            'worldRect': [rx, ry, rw, rh],
            'worldCenter': [cx, cy],
            'projectedCenterRef': [round(px_ref, 2), round(py_ref, 2)],
            'projectedCenterImage': [px_img, py_img],
            'polygonCornersImage': corners_img,
            'inBounds': in_bounds,
            'waterFraction': round(patch_water_fraction, 4),
            'roughnessStd': round(patch_roughness, 2),
            'conflict': conflict
        })
        
    # Analyze bridges
    bridge_measurements = []
    for b_item in bridges_list:
        bid = b_item['id']
        bx, by, bw, bh = b_item['rect']
        bcx = bx + bw / 2.0
        bcy = by + bh / 2.0
        bpx_ref, bpy_ref = world_to_ref_pixel(bcx, bcy)
        bpx_img = int(bpx_ref * scale_x)
        bpy_img = int(bpy_ref * scale_y)
        bridge_measurements.append({
            'bridgeId': bid,
            'worldRect': [bx, by, bw, bh],
            'worldCenter': [bcx, bcy],
            'projectedCenterRef': [round(bpx_ref, 2), round(bpy_ref, 2)],
            'projectedCenterImage': [bpx_img, bpy_img]
        })
        
    return {
        'contractName': contract_name,
        'terrainName': terrain_name,
        'imageDimensions': [w, h],
        'totalWaterFraction': round(float(water_mask.mean()), 4),
        'sitesCount': len(sites_list),
        'conflictsCount': len([s for s in site_measurements if s['conflict'] is not None]),
        'sites': site_measurements,
        'bridges': bridge_measurements
    }

results = {
    'auditDate': '2026-10-04',
    'auditScope': 'Redo Bounded Kingdom Measurement with Exact Affine Projection & Polygon Clearances',
    'activeContract': {
        'path': 'docs/plan/IMPLEMENTATION-CONTRACT.json',
        'sha256': c1_sha256,
        'worldToSource': M,
        'referenceDimensions': [REF_W, REF_H],
        'townhallCenterWorld': [6.5, 0.75],
        'townhallCenterRefProjected': list(map(lambda v: round(v, 2), world_to_ref_pixel(6.5, 0.75))),
        'bridgeCenterWorld': [13.25, 7.4],
        'bridgeCenterRefProjected': list(map(lambda v: round(v, 2), world_to_ref_pixel(13.25, 7.4)))
    },
    'candidateV2Contract': {
        'path': 'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json',
        'sha256': c2_sha256,
        'camera': M,
        'townhallCenterWorld': [5.232, 5.0155],
        'townhallCenterRefProjected': list(map(lambda v: round(v, 2), world_to_ref_pixel(5.232, 5.0155))),
        'bridgeCenterWorld': [12.925, 7.625],
        'bridgeCenterRefProjected': list(map(lambda v: round(v, 2), world_to_ref_pixel(12.925, 7.625)))
    },
    'mathematicalDiscrepancyResolution': {
        'staleReportDiscrepancy': 'Old script ignored camera matrix and used invented (ox=688, oy=384, vx=95, vy=48) basis, projecting Town Hall to (708.57, 395.88). True affine projection of candidate-v2 Town Hall center [5.232, 5.0155] is exactly (609.31, 288.22), a difference of ~146 pixels.',
        'uint8OverflowFix': 'Converted pixel channels to int64 before difference: b.astype(int) > (r.astype(int) + 15), eliminating false positives from wrap-around on bright highlights.',
        'bridgeDiscrepancy': 'Contract A bridge projects to (1150.0, 291.5); Candidate-v2 bridge projects to (1136.13, 302.63). The claimed (1150, 300) was an unverified approximation.'
    },
    'perTerrainSurveys': {}
}

# Run surveys across all 9 terrain files for both Active Contract and Candidate-v2
for tname, tpath in terrain_files.items():
    if not os.path.exists(f'{ROOT}/{tpath}'): continue
    survey_c1 = analyze_contract_sites('ActiveContract_v1', c1_geo['sites'], c1_geo.get('bridges', []), tname, tpath)
    survey_c2 = analyze_contract_sites('Candidate_v2', c2_geo['sites'], c2_geo.get('bridges', []), tname, tpath)
    results['perTerrainSurveys'][tname] = {
        'activeContractSurvey': survey_c1,
        'candidateV2Survey': survey_c2
    }
    print(f"Surveyed {tname:15}: ActiveContract conflicts={survey_c1['conflictsCount']}/18, Candidate-v2 conflicts={survey_c2['conflictsCount']}/18, water={survey_c1['totalWaterFraction']*100:.1f}%")

# Bounded Recoverability Assessment (no smear/cloning/fake grass)
results['recoverabilityAssessment'] = {
    'stoneDay1Assessment': 'Candidate stone_v4 (production-14) contains baked stone buildings, palisade walls, and a fixed river path crossing multiple upper pads. Candidate stone_gen (production-01) is a natural terrain but has a winding river dividing east/west sectors.',
    'policyCompliance': 'Per owner directive: NO new paid generation, NO blur-smear/cloning/grass patching, NO adoption of failed 8 Kingdom/Stonev4 as accepted runtime art. Existing terrain files remain development references only.',
    'status': 'RECOVERABILITY_SURVEYED_HONEST_FAILURES_RECORDED',
    'consumerGuidanceForCodeAI': 'Code AI should render sparse Town Hall + 17 empty pads using procedural grid overlay and legal ground footprint bounds, without relying on baked terrain building illustrations as accepted art.'
}

out_report_path = f'{QA_DIR}/kingdom-bounded-measurement-report.json'
with open(out_report_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved calibrated Kingdom measurement report to {out_report_path}")
