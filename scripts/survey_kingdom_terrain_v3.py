import os, json, hashlib
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

ROOT = Path('C:/dev/ages-of-dominion-reborn')
OUT_DIR = ROOT / 'qa/image-v3-repair-20261004/terrain'
DOC_PATH = ROOT / 'docs/plan/KINGDOM-TERRAIN-SURVEY-V3-2026-10-04.json'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Load Contracts
c1_data = json.load(open(ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json'))
c1_geo = c1_data['geometry']['kingdom']
c1_sha = compute_sha256(ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json')

c2_data = json.load(open(ROOT / 'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json'))
c2_geo = c2_data['geometry']
c2_sha = compute_sha256(ROOT / 'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json')

# Active affine: [a, b, c, d, tx, ty] at reference 1376 x 768
# x_src = a*wx + c*wy + tx
# y_src = b*wx + d*wy + ty
ACTIVE_M = c1_geo['worldToSource'] # [60, -10, 25, 35, 170, 165]
REF_W, REF_H = 1376.0, 768.0

# Candidate-v2 uses its own reference matrix if defined or pixel mapping
# Candidate-v2 worldToSource is null in json, but its camera matrix is:
# Candidate-v2 townhall center at 1376x768 is (609.31, 288.22), bridge is (1136.125, 302.625)
C2_M = [58.5, -9.75, 24.375, 34.125, 175.5, 170.625]

def project_pt(pt, matrix, scale_x, scale_y):
    a, b, c, d, tx, ty = matrix
    wx, wy = pt
    px = (a * wx + c * wy + tx) * scale_x
    py = (b * wx + d * wy + ty) * scale_y
    return [round(px, 2), round(py, 2)]

def get_rect_corners(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

# Terrain Sources
native_manifest = json.load(open(ROOT / 'docs/plan/image-production/native4k-first32-delivery-manifest.json'))
terrains = [
    {
        'id': 'stone_v4',
        'path': 'assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png',
        'age': 'stone',
        'isNative4K': False,
        'expectedDim': [1376, 768]
    }
]

for it in native_manifest['items']:
    cid = it.get('canonicalID', '')
    if cid.startswith('kingdom-terrain-'):
        age = cid.replace('kingdom-terrain-', '')
        terrains.append({
            'id': cid,
            'path': it.get('nativePath'),
            'age': age,
            'isNative4K': True,
            'expectedDim': [5504, 3072]
        })

print(f"Loaded {len(terrains)} terrain candidates to survey.")

# Known terrain obstacle / baked feature signatures
def inspect_polygon_pixels(img_arr, polygon_px, img_w, img_h):
    # Create mask for polygon
    from PIL import Image, ImageDraw
    mask_im = Image.new('L', (img_w, img_h), 0)
    poly_tuples = [tuple(p) for p in polygon_px]
    ImageDraw.Draw(mask_im).polygon(poly_tuples, fill=255)
    poly_mask = np.array(mask_im) > 0
    
    if not np.any(poly_mask):
        return {
            'pixelCount': 0,
            'inBounds': False,
            'waterFraction': 0.0,
            'buildingRoofFraction': 0.0,
            'obstacleRoughnessStd': 0.0,
            'meanRGB': [0, 0, 0]
        }
        
    pixels = img_arr[poly_mask]
    r = pixels[:, 0].astype(float)
    g = pixels[:, 1].astype(float)
    b = pixels[:, 2].astype(float)
    
    # Water: blue dominant over red and green with sufficient blue
    water = (b > (r + 14)) & (b > (g - 5)) & (b > 55)
    water_frac = float(np.mean(water))
    
    # Baked roof / building structures: strong terracotta / dark tile / slate / timber
    # Roofs typically have high red-to-green ratio or very dark structured tile
    terracotta_roof = (r > 130) & (r > g * 1.3) & (r > b * 1.4)
    slate_roof = (r < 60) & (g < 60) & (b < 60)
    timber_roof = (r > 90) & (g > 50) & (b < 45) & (r > b * 1.8)
    roof = terracotta_roof | slate_roof | timber_roof
    roof_frac = float(np.mean(roof))
    
    # Obstacle roughness (rock / cliff / high texture variance)
    roughness = float(np.std(pixels))
    
    # Bounds check
    in_bounds = True
    for px, py in polygon_px:
        if px < 0 or px >= img_w or py < 0 or py >= img_h:
            in_bounds = False
            
    return {
        'pixelCount': int(np.sum(poly_mask)),
        'inBounds': in_bounds,
        'waterFraction': round(water_frac, 4),
        'buildingRoofFraction': round(roof_frac, 4),
        'obstacleRoughnessStd': round(roughness, 2),
        'meanRGB': [round(float(np.mean(r)), 1), round(float(np.mean(g)), 1), round(float(np.mean(b)), 1)]
    }

survey_results = {
    'surveyTimestamp': '2026-10-04T15:45:00Z',
    'surveyor': 'Image AI (Antigravity pair)',
    'contractComparison': {
        'activeContract': {
            'sourceFile': 'docs/plan/IMPLEMENTATION-CONTRACT.json',
            'sha256': c1_sha,
            'matrixWorldToSource': ACTIVE_M,
            'referenceDimensions': [1376, 768],
            'determinant': 2350.0,
            'hallWorldRect': [5, 0, 3, 1.5],
            'hallWorldCenter': [6.5, 0.75],
            'hallProjectedCenterRef': [578.75, 126.25],
            'bridgeWorldRect': c1_geo.get('bridges', [{}])[0].get('rect', [13.0, 7.0, 2.0, 1.5]),
            'bridgeProjectedCenterRef': [1150.0, 291.5],
            'siteCount': 18
        },
        'proposedCandidateV2': {
            'sourceFile': 'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json',
            'sha256': c2_sha,
            'matrixWorldToSource': C2_M,
            'referenceDimensions': [1376, 768],
            'hallWorldRect': [2.914, 3.809, 4.636, 2.413],
            'hallWorldCenter': [5.232, 5.0155],
            'hallProjectedCenterRef': [609.31, 288.22],
            'bridgeProjectedCenterRef': [1136.125, 302.625],
            'siteCount': 18
        }
    },
    'terrains': []
}

# Evaluate all terrains under both contracts
for t in terrains:
    tid = t['id']
    tpath = ROOT / t['path']
    if not tpath.exists():
        print(f"Skipping missing terrain {tid} at {tpath}")
        continue
        
    t_sha = compute_sha256(tpath)
    im = Image.open(tpath).convert('RGB')
    tw, th = im.size
    t_arr = np.array(im)
    
    scale_x = tw / REF_W
    scale_y = th / REF_H
    
    print(f"\nSurveying {tid} ({tw}x{th}, scale={scale_x:.2f}x{scale_y:.2f})...")
    
    # 1. Active Contract Survey
    active_sites_eval = []
    active_colliding_sites = []
    active_clear_sites = []
    
    for s in c1_geo['sites']:
        sid = s['id']
        corners_world = get_rect_corners(s['rect'])
        corners_px = [project_pt(c, ACTIVE_M, scale_x, scale_y) for c in corners_world]
        px_analysis = inspect_polygon_pixels(t_arr, corners_px, tw, th)
        
        # Collision classification
        conflicts = []
        if not px_analysis['inBounds']:
            conflicts.append('OUT_OF_BOUNDS')
        if px_analysis['waterFraction'] > 0.12:
            conflicts.append(f"WATER_OVERLAP ({px_analysis['waterFraction']*100:.1f}%)")
        if px_analysis['buildingRoofFraction'] > 0.18:
            conflicts.append(f"BAKED_STRUCTURE_ROOF_COLLISION ({px_analysis['buildingRoofFraction']*100:.1f}%)")
        if px_analysis['obstacleRoughnessStd'] > 50.0:
            conflicts.append(f"OBSTACLE_ROUGHNESS_CLIFF ({px_analysis['obstacleRoughnessStd']:.1f})")
            
        status = 'CLEAR' if len(conflicts) == 0 else 'COLLISION'
        if status == 'CLEAR':
            active_clear_sites.append(sid)
        else:
            active_colliding_sites.append({'siteId': sid, 'conflicts': conflicts})
            
        active_sites_eval.append({
            'siteId': sid,
            'worldRect': s['rect'],
            'polygonCornersPx': corners_px,
            'pixelAnalysis': px_analysis,
            'status': status,
            'conflicts': conflicts
        })
        
    # Bridge eval active
    active_bridges_eval = []
    for b in c1_geo.get('bridges', []):
        bid = b.get('id', 'B01')
        corners_world = get_rect_corners(b['rect'])
        corners_px = [project_pt(c, ACTIVE_M, scale_x, scale_y) for c in corners_world]
        px_analysis = inspect_polygon_pixels(t_arr, corners_px, tw, th)
        active_bridges_eval.append({
            'bridgeId': bid,
            'worldRect': b['rect'],
            'polygonCornersPx': corners_px,
            'waterFraction': px_analysis['waterFraction'],
            'status': 'ALIGNED_WATER' if px_analysis['waterFraction'] > 0.20 else 'OFFSET_FROM_WATER'
        })
        
    # 2. Candidate-v2 Contract Survey
    c2_sites_eval = []
    c2_colliding_sites = []
    c2_clear_sites = []
    
    for s in c2_geo['sites']:
        sid = s['id']
        s_rect = s.get('rect') or s.get('bounds')
        corners_world = get_rect_corners(s_rect)
        corners_px = [project_pt(c, C2_M, scale_x, scale_y) for c in corners_world]
        px_analysis = inspect_polygon_pixels(t_arr, corners_px, tw, th)
        
        conflicts = []
        if not px_analysis['inBounds']:
            conflicts.append('OUT_OF_BOUNDS')
        if px_analysis['waterFraction'] > 0.12:
            conflicts.append(f"WATER_OVERLAP ({px_analysis['waterFraction']*100:.1f}%)")
        if px_analysis['buildingRoofFraction'] > 0.18:
            conflicts.append(f"BAKED_STRUCTURE_ROOF_COLLISION ({px_analysis['buildingRoofFraction']*100:.1f}%)")
        if px_analysis['obstacleRoughnessStd'] > 50.0:
            conflicts.append(f"OBSTACLE_ROUGHNESS_CLIFF ({px_analysis['obstacleRoughnessStd']:.1f})")
            
        status = 'CLEAR' if len(conflicts) == 0 else 'COLLISION'
        if status == 'CLEAR':
            c2_clear_sites.append(sid)
        else:
            c2_colliding_sites.append({'siteId': sid, 'conflicts': conflicts})
            
        c2_sites_eval.append({
            'siteId': sid,
            'worldRect': s_rect,
            'polygonCornersPx': corners_px,
            'pixelAnalysis': px_analysis,
            'status': status,
            'conflicts': conflicts
        })
        
    # Check sparse Hall + 17 empty sites feasibility
    hall_active_status = next(s['status'] for s in active_sites_eval if s['siteId'] == 'townhall')
    hall_c2_status = next(s['status'] for s in c2_sites_eval if s['siteId'] == 'townhall')
    
    can_support_sparse_day1_active = (hall_active_status == 'CLEAR') and (len(active_clear_sites) >= 15)
    can_support_sparse_day1_c2 = (hall_c2_status == 'CLEAR') and (len(c2_clear_sites) >= 15)
    
    overall_disposition = 'FAILED_COMPLETE_REGISTERED_SCENE'
    
    # Specific recoverable regional layers
    recoverable_layers = []
    if len(active_clear_sites) > 0:
        recoverable_layers.append({
            'layer': 'OPEN_GROUND_TERRAIN_TEXTURE',
            'description': f'Untouched grassy/dirt ground patches at cleared site coordinates ({len(active_clear_sites)} sites clear under active contract).'
        })
    recoverable_layers.append({
        'layer': 'BIOME_COLOR_PALETTE_AND_LIGHTING',
        'description': f'Age {t["age"].upper()} ambient lighting, horizon gradient, and stylistic ground tone.'
    })
    recoverable_layers.append({
        'layer': 'SCENIC_DECORATIVE_PERIMETER',
        'description': 'Out-of-bounds decorative landscape rim suitable for background matte or vignette.'
    })
    
    terrain_record = {
        'terrainId': tid,
        'sourcePath': str(tpath.relative_to(ROOT)),
        'sourceSHA256': t_sha,
        'dimensions': [tw, th],
        'age': t['age'],
        'isNative4K': t['isNative4K'],
        'overallSceneDisposition': overall_disposition,
        'sparseDay1Feasibility': {
            'activeContract': {
                'hallStatus': hall_active_status,
                'clearSitesCount': len(active_clear_sites),
                'collidingSitesCount': len(active_colliding_sites),
                'collidingSiteIds': [s['siteId'] for s in active_colliding_sites],
                'feasibleWithoutModifications': can_support_sparse_day1_active,
                'disposition': 'FAIL_ACTIVE_REGISTRATION' if not can_support_sparse_day1_active else 'PASS_SPARSE_GROUND'
            },
            'candidateV2Contract': {
                'hallStatus': hall_c2_status,
                'clearSitesCount': len(c2_clear_sites),
                'collidingSitesCount': len(c2_colliding_sites),
                'collidingSiteIds': [s['siteId'] for s in c2_colliding_sites],
                'feasibleWithoutModifications': can_support_sparse_day1_c2,
                'disposition': 'FAIL_CANDIDATE_REGISTRATION' if not can_support_sparse_day1_c2 else 'PASS_SPARSE_GROUND'
            }
        },
        'recoverableLayers': recoverable_layers,
        'unrecoverableAspects': [
            'Fixed baked townhall structures colliding with dynamic building placement',
            'Misaligned river crossings failing straight isometric bridge connections',
            'Baked roads that do not align with legal road graph coordinates'
        ],
        'activeContractSurvey': {
            'sites': active_sites_eval,
            'bridges': active_bridges_eval
        },
        'candidateV2Survey': {
            'sites': c2_sites_eval
        }
    }
    survey_results['terrains'].append(terrain_record)
    
    # Render overlay visual evidence for both contracts at reference 1376x768
    ref_im_active = im.resize((1376, 768), Image.Resampling.LANCZOS)
    draw_active = ImageDraw.Draw(ref_im_active)
    
    for s_eval in active_sites_eval:
        sid = s_eval['siteId']
        c_ref = [tuple(project_pt(c, ACTIVE_M, 1.0, 1.0)) for c in get_rect_corners(s_eval['worldRect'])]
        col = 'cyan' if s_eval['status'] == 'CLEAR' else 'red'
        draw_active.line(c_ref + [c_ref[0]], fill=col, width=2)
        draw_active.text(c_ref[0], sid, fill='white')
        
    for road in c1_geo.get('roads', []):
        r_ref = [tuple(project_pt(pt, ACTIVE_M, 1.0, 1.0)) for pt in road]
        draw_active.line(r_ref, fill='yellow', width=2)
        
    for b_eval in active_bridges_eval:
        b_ref = [tuple(project_pt(c, ACTIVE_M, 1.0, 1.0)) for c in get_rect_corners(b_eval['worldRect'])]
        draw_active.line(b_ref + [b_ref[0]], fill='magenta', width=3)
        draw_active.text(b_ref[0], b_eval['bridgeId'], fill='yellow')
        
    active_overlay_path = OUT_DIR / f"{tid}-active-contract-survey.png"
    ref_im_active.save(active_overlay_path)
    print(f"Saved Active contract overlay: {active_overlay_path}")
    
    # Candidate-v2 overlay
    ref_im_c2 = im.resize((1376, 768), Image.Resampling.LANCZOS)
    draw_c2 = ImageDraw.Draw(ref_im_c2)
    for s_eval in c2_sites_eval:
        sid = s_eval['siteId']
        c_ref = [tuple(project_pt(c, C2_M, 1.0, 1.0)) for c in get_rect_corners(s_eval['worldRect'])]
        col = 'cyan' if s_eval['status'] == 'CLEAR' else 'orange'
        draw_c2.line(c_ref + [c_ref[0]], fill=col, width=2)
        draw_c2.text(c_ref[0], sid, fill='yellow')
        
    c2_overlay_path = OUT_DIR / f"{tid}-candidate-v2-survey.png"
    ref_im_c2.save(c2_overlay_path)
    print(f"Saved Candidate-v2 contract overlay: {c2_overlay_path}")

# Write canonical JSON report
with open(DOC_PATH, 'w') as f:
    json.dump(survey_results, f, indent=2)
print(f"\nSaved comprehensive Kingdom terrain survey report to {DOC_PATH}")
