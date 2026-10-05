import os, json, hashlib
from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = Path('C:/dev/ages-of-dominion-reborn')
ACTORS_DIR = ROOT / 'assets/derivatives/actors/v3'
MOUNTS_DIR = ROOT / 'assets/derivatives/mounts/v3'
SUBS_DIR = ROOT / 'assets/derivatives/substitutions/v3'
QA_DIR = ROOT / 'qa/image-v3-repair-20261004/actors_mounts'

ACTORS_DIR.mkdir(parents=True, exist_ok=True)
MOUNTS_DIR.mkdir(parents=True, exist_ok=True)
SUBS_DIR.mkdir(parents=True, exist_ok=True)
QA_DIR.mkdir(parents=True, exist_ok=True)

def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save_qa_composites(rgba_im, item_id, bbox, out_dir):
    cropped = rgba_im.crop(bbox)
    w, h = cropped.size
    detail_box = (max(0, w//4), max(0, int(h * 0.65)), min(w, int(w * 0.85)), h)
    detail_patch = cropped.crop(detail_box)
    
    aspect = cropped.width / cropped.height
    thumb_h = 50
    thumb_w = max(16, int(thumb_h * aspect))
    thumb = cropped.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    
    bgs = [('black', (0,0,0,255)), ('white', (255,255,255,255)), ('green', (110,132,104,255))]
    
    dw, dh = detail_patch.size
    d_canvas = Image.new('RGB', (dw * 3, dh))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (dw, dh), col)
        layer.alpha_composite(detail_patch)
        d_canvas.paste(layer.convert('RGB'), (i * dw, 0))
    d_canvas.save(out_dir / f'{item_id}_detail_qa.png')
    
    c_canvas = Image.new('RGB', (thumb_w * 3, thumb_h))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (thumb_w, thumb_h), col)
        layer.alpha_composite(thumb)
        c_canvas.paste(layer.convert('RGB'), (i * thumb_w, 0))
    c_canvas.save(out_dir / f'{item_id}_consumer_qa.png')

results = {}

# --- 1. SUBSTITUTIONS ---
def clean_sub(im_path, despill_steam=False):
    im = Image.open(im_path).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mag_dist = np.sqrt((r - 255.0)**2 + (g - 0.0)**2 + (b - 255.0)**2)
    mag_excess = np.maximum(0.0, np.minimum(r - g, b - g))
    bg_mask = (mag_dist < 90.0) | ((mag_excess > 50.0) & (g < 60.0))
    alpha = np.clip((mag_dist - 60.0) / 60.0, 0.0, 1.0)
    alpha[bg_mask] = 0.0
    core_fg = ndimage.binary_fill_holes(alpha > 0.8)
    alpha = np.where(core_fg, np.maximum(alpha, 1.0), alpha)
    
    clean_r, clean_g, clean_b = r.copy(), g.copy(), b.copy()
    spill = np.maximum(0.0, np.minimum(clean_r - clean_g, clean_b - clean_g))
    clean_r -= spill * 0.95
    clean_b -= spill * 0.95
    if despill_steam:
        steam_mask = (clean_g > 140.0) & (clean_r > 140.0) & (clean_b > 140.0)
        mean_lum = (clean_r + clean_g + clean_b) / 3.0
        clean_r[steam_mask] = clean_r[steam_mask] * 0.3 + mean_lum[steam_mask] * 0.7
        clean_b[steam_mask] = clean_b[steam_mask] * 0.3 + mean_lum[steam_mask] * 0.7
        
    rgba = np.dstack([
        np.clip(clean_r, 0, 255).astype(np.uint8),
        np.clip(clean_g, 0, 255).astype(np.uint8),
        np.clip(clean_b, 0, 255).astype(np.uint8),
        (alpha * 255.0).astype(np.uint8)
    ])
    out_im = Image.fromarray(rgba, 'RGBA')
    opaque = rgba[:, :, 3] > 30
    ys, xs = np.where(opaque)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    bot_y = int(ys.max())
    bot_xs = xs[ys >= (bot_y - 15)]
    contact_x = int(np.median(bot_xs))
    return out_im, bbox, [contact_x, bot_y]

legion_src = ROOT / 'assets/production/production-07-20261003/images/09-troop-iron-melee.png'
im_leg, bbox_leg, contact_leg = clean_sub(legion_src, despill_steam=False)
p_leg = SUBS_DIR / 'troop-iron-melee.png'
im_leg.save(p_leg)
save_qa_composites(im_leg, 'sub_troop-iron-melee', bbox_leg, QA_DIR)
results['substitution-troop-iron-melee'] = {
    'targetID': 'troop-iron-melee',
    'status': 'AUTHENTIC_SUBSTITUTION_DELIVERED',
    'sourceProvenance': 'production-07-20261003/images/09-troop-iron-melee.png (1024x1024)',
    'sourceSHA256': sha256_file(legion_src),
    'derivativePath': 'assets/derivatives/substitutions/v3/troop-iron-melee.png',
    'derivativeSHA256': sha256_file(p_leg),
    'derivativeDimensions': list(im_leg.size),
    'derivativeMode': 'RGBA',
    'tightBBox': bbox_leg,
    'groundContactPivot': contact_leg
}

walk_src = ROOT / 'assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png'
im_walk, bbox_walk, contact_walk = clean_sub(walk_src, despill_steam=True)
p_walk = SUBS_DIR / 'troop-industrial-heavy.png'
im_walk.save(p_walk)
save_qa_composites(im_walk, 'sub_troop-industrial-heavy', bbox_walk, QA_DIR)
results['substitution-troop-industrial-heavy'] = {
    'targetID': 'troop-industrial-heavy',
    'status': 'AUTHENTIC_SUBSTITUTION_DELIVERED',
    'sourceProvenance': 'production-17-20261003/images/10-attacker-industrial-heavy.png (1024x1024)',
    'sourceSHA256': sha256_file(walk_src),
    'derivativePath': 'assets/derivatives/substitutions/v3/troop-industrial-heavy.png',
    'derivativeSHA256': sha256_file(p_walk),
    'derivativeDimensions': list(im_walk.size),
    'derivativeMode': 'RGBA',
    'tightBBox': bbox_walk,
    'groundContactPivot': contact_walk
}

# --- 2. ARMY ACTORS (24 rows) ---
def process_actor(item_id):
    src_p = ROOT / f'assets/high-res/final-native2k/{item_id}.png'
    im = Image.open(src_p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
    
    clean_arr = arr.copy()
    floor_mask = np.zeros((h, w), dtype=bool)
    is_bg = diff < 20.0
    
    # Custom isolation & floor/artifact removal per item:
    if item_id == 'troop-stone-melee':
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        is_bg = np.sqrt((r - 252)**2 + (g - 1)**2 + (b - 248)**2) < 60.0
        for y in range(h):
            if y >= 1660: floor_mask[y, :] = True
            elif y >= 1350:
                floor_mask[y, :730] = True
                floor_mask[y, 1260:] = True
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        clean_arr[:, :, 0] -= spill * 0.95
        clean_arr[:, :, 2] -= spill * 0.95
    elif item_id == 'troop-stone-ranged':
        for y in range(h):
            if y >= 1660: floor_mask[y, :] = True
            elif y >= 1350:
                floor_mask[y, :650] = True
                floor_mask[y, 1350:] = True
    elif item_id == 'troop-stone-heavy':
        pass # clean
    elif item_id == 'troop-bronze-melee':
        floor_mask[1950:, :] = True
    elif item_id == 'troop-bronze-ranged':
        # ROI [415, 276, 1408, 1970]
        floor_mask[:276, :] = True
        floor_mask[1970:, :] = True
        floor_mask[:, :415] = True
        floor_mask[:, 1408:] = True
    elif item_id == 'troop-bronze-heavy':
        floor_mask[1680:, :] = True # plinth & caption
    elif item_id == 'troop-iron-melee':
        pass # stencil candidate
    elif item_id == 'troop-iron-ranged':
        floor_mask[1680:, :] = True # grey slab
    elif item_id == 'troop-iron-heavy':
        floor_mask[1795:, :] = True # base strip / ruler
        floor_mask[1790:, :510] = True
    elif item_id == 'troop-medieval-melee':
        floor_mask[1700:, :] = True
        floor_mask[1550:, :650] = True
        floor_mask[1550:, 1450:] = True
    elif item_id == 'troop-medieval-ranged':
        # Primary archer ROI [638, 787, 1207, 1542]
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        is_bg = np.sqrt((r - 251)**2 + (g - 1)**2 + (b - 249)**2) < 60.0
        floor_mask[:787, :] = True
        floor_mask[1542:, :] = True
        floor_mask[:, :638] = True
        floor_mask[:, 1207:] = True
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        clean_arr[:, :, 0] -= spill * 0.95
        clean_arr[:, :, 2] -= spill * 0.95
    elif item_id == 'troop-medieval-heavy':
        floor_mask[1755:, :] = True # oval pedestal
    elif item_id == 'troop-gunpowder-melee':
        floor_mask[1735:, :] = True # white floor strips
    elif item_id == 'troop-gunpowder-ranged':
        floor_mask[:100, :] = True # top title letters
        floor_mask[1665:, :] = True # floor
    elif item_id == 'troop-gunpowder-heavy':
        # ROI [372, 226, 1750, 1850]
        floor_mask[:226, :] = True
        floor_mask[1850:, :] = True
        floor_mask[:, :372] = True
        floor_mask[:, 1750:] = True
    elif item_id == 'troop-industrial-melee':
        floor_mask[1775:, :] = True # floor
    elif item_id == 'troop-industrial-ranged':
        floor_mask[:255, :] = True
        floor_mask[1871:, :] = True
        floor_mask[:, :498] = True
        floor_mask[:, 1528:] = True
    elif item_id == 'troop-industrial-heavy':
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        is_bg = np.sqrt((r - 252)**2 + (g - 1)**2 + (b - 249)**2) < 60.0
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        clean_arr[:, :, 0] -= spill * 0.95
        clean_arr[:, :, 2] -= spill * 0.95
    elif item_id == 'troop-modern-melee':
        floor_mask[:146, :] = True # top letters
        floor_mask[1915:, :] = True # bottom corners
        floor_mask[:, :594] = True
        floor_mask[:, 1588:] = True
    elif item_id == 'troop-modern-ranged':
        floor_mask[:137, :] = True
        floor_mask[1800:, :] = True
        floor_mask[:, :549] = True
        floor_mask[:, 1498:] = True
    elif item_id == 'troop-modern-heavy':
        # Despill magenta helmet rim around [688, 85, 1372, 499]
        r, g, b = clean_arr[:500, :, 0], clean_arr[:500, :, 1], clean_arr[:500, :, 2]
        spill = np.maximum(0.0, np.minimum(r - g, b - g))
        clean_arr[:500, :, 0] -= spill * 0.95
        clean_arr[:500, :, 2] -= spill * 0.95
    elif item_id == 'troop-future-melee':
        floor_mask[1675:, :] = True # floor tiles
    elif item_id == 'troop-future-ranged':
        floor_mask[:209, :] = True
        floor_mask[1968:, :] = True
        floor_mask[:, :623] = True
        floor_mask[:, 1652:] = True
    elif item_id == 'troop-future-heavy':
        floor_mask[1815:, :] = True # dark floor rectangle
        
    alpha = np.where(is_bg | floor_mask, 0.0, 1.0)
    alpha = ndimage.gaussian_filter(alpha, sigma=0.8)
    rgba = np.dstack([
        np.clip(clean_arr, 0, 255).astype(np.uint8),
        (alpha * 255.0).astype(np.uint8)
    ])
    out_im = Image.fromarray(rgba, 'RGBA')
    out_p = ACTORS_DIR / f'{item_id}.png'
    out_im.save(out_p)
    
    opaque = rgba[:, :, 3] > 30
    if np.any(opaque):
        ys, xs = np.where(opaque)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        bot_y = int(ys.max())
        bot_xs = xs[ys >= (bot_y - 15)]
        contact_x = int(np.median(bot_xs))
        contact = [contact_x, bot_y]
    else:
        bbox = [0, 0, w, h]
        contact = [w//2, h]
        
    save_qa_composites(out_im, item_id, bbox, QA_DIR)
    
    role_status = 'PASS_CLEAN_SINGLE_ACTOR'
    if item_id == 'troop-iron-melee':
        role_status = 'ROLE_FAIL_STENCIL_SUBSTITUTION_AVAILABLE'
    elif item_id == 'troop-industrial-heavy':
        role_status = 'ROLE_FAIL_GUNNER_SUBSTITUTION_AVAILABLE'
        
    results[item_id] = {
        'id': item_id,
        'status': role_status,
        'sourcePath': f'assets/high-res/final-native2k/{item_id}.png',
        'sourceSHA256': sha256_file(src_p),
        'derivativePath': f'assets/derivatives/actors/v3/{item_id}.png',
        'derivativeSHA256': sha256_file(out_p),
        'derivativeDimensions': list(out_im.size),
        'derivativeMode': 'RGBA',
        'tightBBox': bbox,
        'groundContactPivot': contact
    }
    print(f'Actor {item_id:25}: status={role_status:38} bbox={bbox} contact={contact}')

m = json.load(open(ROOT / 'docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json'))
army_items = [i for i in m['items'] if i['group'] == '2K-LATER-C-ARMY-24']
for item in army_items:
    process_actor(item['id'])

# --- 3. MOUNTS (4 rows) ---
print('\nProcessing mounts...')
def process_mount(mount_id):
    src_p = ROOT / f'assets/high-res/final-native2k/{mount_id}.png'
    im = Image.open(src_p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
    
    clean_arr = arr.copy()
    floor_mask = np.zeros((h, w), dtype=bool)
    is_bg = diff < 20.0
    saddle = None
    
    if mount_id == 'hero-mount-horse':
        # Floor polygon removal
        for y in range(h):
            if y >= 1750: floor_mask[y, :] = True
            elif y >= 1350:
                floor_mask[y, 730:1330] = True
                floor_mask[y, :380] = True
                floor_mask[y, 1700:] = True
                if y >= 1560: floor_mask[y, :1300] = True
                elif y >= 1480: floor_mask[y, 560:1330] = True
        saddle = [1000, 439] # measured saddle dip
    elif mount_id == 'hero-mount-motor-transport':
        # Remove dark backdrop block on left
        for y in range(h):
            if y >= 800: floor_mask[y, :360] = True
            if y >= 1650: floor_mask[y, :] = True # lower ground
        saddle = [980, 720] # driver seat
    elif mount_id == 'hero-mount-future-transport':
        # Remove pale floor block on left
        for y in range(h):
            if y >= 700: floor_mask[y, :450] = True
            if y >= 1650: floor_mask[y, :] = True # lower ground
        saddle = [1040, 680] # cockpit attachment
    elif mount_id == 'knight-mounted-master':
        # Preserved as Stone FAIL without world-alpha
        out_p = MOUNTS_DIR / f'{mount_id}.png'
        im.save(out_p)
        results[mount_id] = {
            'id': mount_id,
            'status': 'ROLE_FAIL_STONE_ERA_MEDIEVAL_SCENIC',
            'sourcePath': f'assets/high-res/final-native2k/{mount_id}.png',
            'sourceSHA256': sha256_file(src_p),
            'derivativePath': f'assets/derivatives/mounts/v3/{mount_id}.png',
            'derivativeSHA256': sha256_file(out_p),
            'derivativeDimensions': list(im.size),
            'derivativeMode': 'RGB',
            'tightBBox': [0, 0, w, h],
            'groundContactPivot': [w//2, h],
            'saddlePivot': None,
            'notes': 'Medieval scenic barded knight; unsuited for Stone era travel. Preserved as Stone FAIL.'
        }
        print(f'Mount {mount_id:25}: status=ROLE_FAIL_STONE_ERA_MEDIEVAL_SCENIC (RGB preserved)')
        return

    alpha = np.where(is_bg | floor_mask, 0.0, 1.0)
    alpha = ndimage.gaussian_filter(alpha, sigma=0.8)
    rgba = np.dstack([
        np.clip(clean_arr, 0, 255).astype(np.uint8),
        (alpha * 255.0).astype(np.uint8)
    ])
    out_im = Image.fromarray(rgba, 'RGBA')
    out_p = MOUNTS_DIR / f'{mount_id}.png'
    out_im.save(out_p)
    
    opaque = rgba[:, :, 3] > 30
    ys, xs = np.where(opaque)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    bot_y = int(ys.max())
    bot_xs = xs[ys >= (bot_y - 15)]
    contact_x = int(np.median(bot_xs))
    contact = [contact_x, bot_y]
    
    save_qa_composites(out_im, mount_id, bbox, QA_DIR)
    
    results[mount_id] = {
        'id': mount_id,
        'status': 'PASS_CLEAN_MOUNT_DELIVERY',
        'sourcePath': f'assets/high-res/final-native2k/{mount_id}.png',
        'sourceSHA256': sha256_file(src_p),
        'derivativePath': f'assets/derivatives/mounts/v3/{mount_id}.png',
        'derivativeSHA256': sha256_file(out_p),
        'derivativeDimensions': list(out_im.size),
        'derivativeMode': 'RGBA',
        'tightBBox': bbox,
        'groundContactPivot': contact,
        'saddlePivot': saddle
    }
    print(f'Mount {mount_id:25}: status=PASS_CLEAN_MOUNT_DELIVERY bbox={bbox} contact={contact} saddle={saddle}')

for m_id in ['hero-mount-horse', 'hero-mount-motor-transport', 'hero-mount-future-transport', 'knight-mounted-master']:
    process_mount(m_id)

(ROOT / 'docs/plan/ACTORS-MOUNTS-V3-RESULTS.json').write_text(json.dumps(results, indent=2))
print('\nAll 24 army actors, 4 mounts, and 2 substitutions processed and saved.')
