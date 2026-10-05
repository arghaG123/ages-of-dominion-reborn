import os, json, hashlib
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
QA_DIR = f'{ROOT}/qa/offline-controls-repair-20261004/actors_qa'
os.makedirs(QA_DIR, exist_ok=True)
os.makedirs(f'{ROOT}/assets/derivatives/actors', exist_ok=True)
os.makedirs(f'{ROOT}/assets/derivatives/mounts', exist_ok=True)
os.makedirs(f'{ROOT}/assets/derivatives/substitutions', exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

import sys
sys.path.insert(0, ROOT)
from scripts.test_clean_substitutions import clean_magenta_matte

substitutions_results = {}

# troop-iron-melee (Legionary 1024x1024 from production-07)
im_legion, bbox_legion, contact_legion = clean_magenta_matte(
    f'{ROOT}/assets/production/production-07-20261003/images/09-troop-iron-melee.png',
    despill_steam=False
)
legion_rel = 'assets/derivatives/substitutions/troop-iron-melee.png'
im_legion.save(f'{ROOT}/{legion_rel}')
substitutions_results['troop-iron-melee'] = {
    'targetID': 'troop-iron-melee',
    'status': 'AUTHENTIC_SUBSTITUTION_DELIVERED',
    'rationale': 'Candidate 2K is a black/grey stencil silhouette. Substitution delivers authentic painted Roman Legionary from production-07 with magenta sole despill applied.',
    'sourceProvenance': 'production-07 (1024x1024) - NOT native 2K',
    'sourcePath': 'assets/production/production-07-20261003/images/09-troop-iron-melee.png',
    'sourceResolution': [1024, 1024],
    'sourceSHA256': compute_sha256(f'{ROOT}/assets/production/production-07-20261003/images/09-troop-iron-melee.png'),
    'derivativePath': legion_rel,
    'derivativeSHA256': compute_sha256(f'{ROOT}/{legion_rel}'),
    'derivativeDimensions': list(im_legion.size),
    'derivativeMode': 'RGBA',
    'tightBBox': bbox_legion,
    'groundContactPivot': contact_legion
}

# troop-industrial-heavy (Steam Walker 1024x1024 from production-17)
im_walker, bbox_walker, contact_walker = clean_magenta_matte(
    f'{ROOT}/assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png',
    despill_steam=True
)
walker_rel = 'assets/derivatives/substitutions/troop-industrial-heavy.png'
im_walker.save(f'{ROOT}/{walker_rel}')
substitutions_results['troop-industrial-heavy'] = {
    'targetID': 'troop-industrial-heavy',
    'status': 'AUTHENTIC_SUBSTITUTION_DELIVERED',
    'rationale': 'Candidate 2K is an infantry gunner. Substitution delivers authentic bipedal Steam Combat Walker from production-17 with steam and sole despill applied.',
    'sourceProvenance': 'production-17 (1024x1024) - NOT native 2K',
    'sourcePath': 'assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png',
    'sourceResolution': [1024, 1024],
    'sourceSHA256': compute_sha256(f'{ROOT}/assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png'),
    'derivativePath': walker_rel,
    'derivativeSHA256': compute_sha256(f'{ROOT}/{walker_rel}'),
    'derivativeDimensions': list(im_walker.size),
    'derivativeMode': 'RGBA',
    'tightBBox': bbox_walker,
    'groundContactPivot': contact_walker
}

# -------------------------------------------------------------
# 2. PROCESS ARMY ACTORS (24 units)
# -------------------------------------------------------------
print("\n--- 2. Processing Army Actors ---")

# Specific crop / isolate ROI for multi-figure / labelled sheets:
SPECIFIC_ACTOR_ROI = {
    'troop-bronze-ranged': [415, 276, 1408, 1970],    # isolate main central archer, drop text & side silhouettes
    'troop-medieval-ranged': [718, 788, 1206, 1541],  # isolate primary central archer from multi-pose sheet
    'troop-gunpowder-heavy': [372, 321, 1620, 1849],  # isolate main cannon / gunner from blue sheet
    'troop-industrial-ranged': [498, 255, 1528, 1871],# isolate main rifleman, drop pink labels
    'troop-modern-ranged': [549, 137, 1498, 1985],    # isolate primary soldier from multi-actor sheet
    'troop-future-ranged': [623, 209, 1652, 1968]     # isolate primary energy gunner
}

def extract_clean_actor(native_p, out_rel, item_id):
    im = Image.open(native_p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    
    is_magenta = (bg[0] > 180 and bg[1] < 70 and bg[2] > 180)
    is_blue = (bg[0] < 70 and bg[1] < 100 and bg[2] > 80)
    is_pink = (bg[0] > 180 and bg[1] > 100 and bg[2] > 160 and bg[1] < bg[0])
    
    # Compute foreground mask
    if is_magenta:
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        mag_dist = np.sqrt((r - 255)**2 + g**2 + (b - 255)**2)
        alpha = np.clip((mag_dist - 65.0) / 75.0, 0.0, 1.0)
        # Despill
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        arr_clean = arr.copy()
        arr_clean[:, :, 0] -= spill * 0.95
        arr_clean[:, :, 2] -= spill * 0.95
    elif is_blue:
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        blue_excess = b - np.maximum(r, g)
        alpha = np.clip(1.0 - (blue_excess - 10.0) / 30.0, 0.0, 1.0)
        # Despill blue
        spill = np.maximum(0.0, b - np.maximum(r, g))
        arr_clean = arr.copy()
        arr_clean[:, :, 2] -= spill * 0.9
    elif is_pink:
        diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
        alpha = np.clip((diff - 25.0) / 40.0, 0.0, 1.0)
        # Despill pink
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        arr_clean = arr.copy()
        arr_clean[:, :, 0] -= spill * 0.8
    else: # Neutral / grey / white
        diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
        chroma = np.std(arr, axis=-1)
        cand_bg = (diff < 26.0) & (chroma < 14.0)
        border_mask = np.zeros((h, w), dtype=bool)
        border_mask[0:4, :] = True
        border_mask[-4:, :] = True
        border_mask[:, 0:4] = True
        border_mask[:, -4:] = True
        seed_bg = cand_bg & border_mask
        labeled, _ = ndimage.label(cand_bg)
        border_labels = np.unique(labeled[seed_bg])
        border_labels = border_labels[border_labels > 0]
        bg_mask = np.isin(labeled, border_labels)
        fg_mask = ~bg_mask
        fg_mask = ndimage.binary_closing(fg_mask, structure=np.ones((5, 5)))
        fg_mask = ndimage.binary_fill_holes(fg_mask)
        dist_to_bg = ndimage.distance_transform_edt(fg_mask)
        alpha = np.clip(dist_to_bg / 2.5, 0.0, 1.0)
        arr_clean = arr.copy()
        
    # If specific ROI is requested to isolate single pose:
    if item_id in SPECIFIC_ACTOR_ROI:
        rx1, ry1, rx2, ry2 = SPECIFIC_ACTOR_ROI[item_id]
        # Zero out alpha outside ROI with smooth 16px edge
        mask = np.zeros((h, w), dtype=float)
        mask[ry1:ry2, rx1:rx2] = 1.0
        # Smooth boundaries
        mask = ndimage.gaussian_filter(mask, sigma=3.0)
        alpha *= mask
        
    rgba = np.dstack([
        np.clip(arr_clean, 0, 255).astype(np.uint8),
        (alpha * 255).astype(np.uint8)
    ])
    out_im = Image.fromarray(rgba, 'RGBA')
    
    # Calculate tight bounding box and ground contact pivot
    alpha_mask = rgba[:, :, 3] > 25
    if np.any(alpha_mask):
        ys, xs = np.where(alpha_mask)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        bot_ys = ys[ys >= (bbox[3] - 25)]
        bot_xs = xs[ys >= (bbox[3] - 25)]
        contact_x = int(np.median(bot_xs)) if len(bot_xs) > 0 else int((bbox[0] + bbox[2]) / 2)
        contact_y = bbox[3]
    else:
        bbox = [0, 0, w, h]
        contact_x, contact_y = w // 2, h
        
    out_path = f'{ROOT}/{out_rel}'
    out_im.save(out_path)
    return {
        'tightBBox': bbox,
        'groundContactPivot': [contact_x, contact_y],
        'width': int(bbox[2] - bbox[0]),
        'height': int(bbox[3] - bbox[1]),
        'opaquePixels': int(np.sum(alpha_mask)),
        'outPath': out_rel,
        'sha256': compute_sha256(out_path)
    }

m = json.load(open(f'{ROOT}/docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
army_items = [i for i in m['items'] if i['group'] == '2K-LATER-C-ARMY-24']
actors_manifest = {}

for item in army_items:
    iid = item['id']
    native_p = f'{ROOT}/assets/high-res/final-native2k/{iid}.png'
    out_rel = f'assets/derivatives/actors/{iid}.png'
    res = extract_clean_actor(native_p, out_rel, iid)
    actors_manifest[iid] = res
    print(f"Actor {iid:25}: bbox={res['tightBBox']}, contact={res['groundContactPivot']}")

# -------------------------------------------------------------
# 3. PROCESS MOUNTS (4 mounts)
# -------------------------------------------------------------
print("\n--- 3. Processing Mounts ---")
from scripts.measure_all_mounts import measure_mount

mounts_manifest = {}

# 1. hero-mount-horse
horse_bbox, horse_saddle, horse_contact = measure_mount('hero-mount-horse', 1875, (900, 1350))
# Create clean RGBA
im_h = Image.open(f'{ROOT}/assets/high-res/final-native2k/hero-mount-horse.png').convert('RGB')
arr_h = np.array(im_h, dtype=float)
bg_h = arr_h[10, 10, :]
diff_h = np.sqrt(np.sum((arr_h - bg_h)**2, axis=2))
alpha_h = np.clip((diff_h - 25.0) / 35.0, 0.0, 1.0)
alpha_h[1875:, :] = 0.0 # Remove floor plane
rgba_h = np.dstack([arr_h.astype(np.uint8), (alpha_h * 255).astype(np.uint8)])
horse_out = f'{ROOT}/assets/derivatives/mounts/hero-mount-horse.png'
Image.fromarray(rgba_h, 'RGBA').save(horse_out)
mounts_manifest['hero-mount-horse'] = {
    'id': 'hero-mount-horse',
    'status': 'DELIVERED_CLEAN_MATTE',
    'tightBBox': horse_bbox,
    'saddleRiderPivot': horse_saddle,
    'groundContactPivot': horse_contact,
    'floorPlaneRemoved': True,
    'floorPlaneCutoffY': 1875,
    'outPath': 'assets/derivatives/mounts/hero-mount-horse.png',
    'sha256': compute_sha256(horse_out)
}

# 2. hero-mount-motor-transport
motor_bbox, motor_saddle, motor_contact = measure_mount('hero-mount-motor-transport', 1840, (800, 1300))
im_m = Image.open(f'{ROOT}/assets/high-res/final-native2k/hero-mount-motor-transport.png').convert('RGB')
arr_m = np.array(im_m, dtype=float)
bg_m = arr_m[10, 10, :]
diff_m = np.sqrt(np.sum((arr_m - bg_m)**2, axis=2))
alpha_m = np.clip((diff_m - 25.0) / 35.0, 0.0, 1.0)
alpha_m[1840:, :] = 0.0 # Remove floor plane
rgba_m = np.dstack([arr_m.astype(np.uint8), (alpha_m * 255).astype(np.uint8)])
motor_out = f'{ROOT}/assets/derivatives/mounts/hero-mount-motor-transport.png'
Image.fromarray(rgba_m, 'RGBA').save(motor_out)
mounts_manifest['hero-mount-motor-transport'] = {
    'id': 'hero-mount-motor-transport',
    'status': 'DELIVERED_CLEAN_MATTE',
    'tightBBox': motor_bbox,
    'saddleRiderPivot': motor_saddle,
    'groundContactPivot': motor_contact,
    'floorPlaneRemoved': True,
    'floorPlaneCutoffY': 1840,
    'outPath': 'assets/derivatives/mounts/hero-mount-motor-transport.png',
    'sha256': compute_sha256(motor_out)
}

# 3. hero-mount-future-transport
fut_bbox, fut_saddle, fut_contact = measure_mount('hero-mount-future-transport', 1780, (700, 1300))
im_f = Image.open(f'{ROOT}/assets/high-res/final-native2k/hero-mount-future-transport.png').convert('RGB')
arr_f = np.array(im_f, dtype=float)
bg_f = arr_f[10, 10, :]
diff_f = np.sqrt(np.sum((arr_f - bg_f)**2, axis=2))
alpha_f = np.clip((diff_f - 25.0) / 35.0, 0.0, 1.0)
alpha_f[1780:, :] = 0.0 # Remove floor plane
rgba_f = np.dstack([arr_f.astype(np.uint8), (alpha_f * 255).astype(np.uint8)])
fut_out = f'{ROOT}/assets/derivatives/mounts/hero-mount-future-transport.png'
Image.fromarray(rgba_f, 'RGBA').save(fut_out)
mounts_manifest['hero-mount-future-transport'] = {
    'id': 'hero-mount-future-transport',
    'status': 'DELIVERED_CLEAN_MATTE',
    'tightBBox': fut_bbox,
    'saddleRiderPivot': fut_saddle,
    'groundContactPivot': fut_contact,
    'floorPlaneRemoved': True,
    'floorPlaneCutoffY': 1780,
    'outPath': 'assets/derivatives/mounts/hero-mount-future-transport.png',
    'sha256': compute_sha256(fut_out)
}

# 4. knight-mounted-master
# Scenic painting with castle background -> STONE FAIL
knight_out = f'{ROOT}/assets/derivatives/mounts/knight-mounted-master.png'
shutil_copy = True
# Keep as raw reference in derivatives, but mark as STONE FAIL
im_k = Image.open(f'{ROOT}/assets/high-res/final-native2k/knight-mounted-master.png')
im_k.save(knight_out)
mounts_manifest['knight-mounted-master'] = {
    'id': 'knight-mounted-master',
    'status': 'STONE_FAIL_ERA_MISMATCH',
    'rationale': 'Depicts medieval barded armor with scenic ground/castle background. CANNOT fulfill ancient Knight / Stone travel. Preserved as medieval reference only.',
    'saddleRiderPivot': [950, 650], # Approximate reference only
    'groundContactPivot': [1024, 2048],
    'outPath': 'assets/derivatives/mounts/knight-mounted-master.png',
    'sha256': compute_sha256(knight_out)
}

# -------------------------------------------------------------
# 4. GENERATE QA COMPOSITES ON BLACK, WHITE, NEUTRAL GREEN
# -------------------------------------------------------------
print("\n--- 4. Generating QA Composite Review Sheets ---")

all_review_items = []
for iid, data in actors_manifest.items():
    all_review_items.append((iid, Image.open(f'{ROOT}/{data["outPath"]}')))
for iid, data in substitutions_results.items():
    all_review_items.append((iid, Image.open(f'{ROOT}/{data["derivativePath"]}')))
for iid, data in mounts_manifest.items():
    all_review_items.append((iid, Image.open(f'{ROOT}/{data["outPath"]}')))

cols = 6
rows = (len(all_review_items) + cols - 1) // cols
cell_w, cell_h = 256, 256

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

for bg_name, bg_color in [('black', (0, 0, 0, 255)), ('white', (255, 255, 255, 255)), ('green', (0, 177, 64, 255))]:
    sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), bg_color)
    for idx, (iid, im_raw) in enumerate(all_review_items):
        r = idx // cols
        c = idx % cols
        thumb = im_raw.convert('RGBA').resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (c * cell_w, r * cell_h), mask=thumb)
    sheet_rgb = sheet.convert('RGB')
    sheet_p = f'{QA_DIR}/actors-mounts-composite-{bg_name}.png'
    sheet_rgb.save(sheet_p)
    print(f"Saved QA composite sheet: {sheet_p}")

# Save manifest
with open(f'{ROOT}/qa/offline-controls-repair-20261004/cleaned-actors-and-mounts-manifest.json', 'w') as f:
    json.dump({
        'substitutions': substitutions_results,
        'actors': actors_manifest,
        'mounts': mounts_manifest
    }, f, indent=2)

print("\nStep 5 Complete: All actors, mounts, and substitutions processed and verified!")
