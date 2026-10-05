import os
from PIL import Image
import numpy as np
from scipy import ndimage

def clean_magenta_matte(im_path, despill_steam=False):
    im = Image.open(im_path).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    
    # Distance to pure magenta (255, 0, 255) in RGB
    mag_dist = np.sqrt((r - 255.0)**2 + (g - 0.0)**2 + (b - 255.0)**2)
    
    # Relative magenta excess
    mag_excess = np.maximum(0.0, np.minimum(r - g, b - g))
    
    # Background detection
    # Background has low mag_dist or high mag_excess and low g
    bg_mask = (mag_dist < 90.0) | ((mag_excess > 50.0) & (g < 60.0))
    
    # Refine alpha: smooth transition
    alpha = np.clip((mag_dist - 60.0) / 60.0, 0.0, 1.0)
    alpha[bg_mask] = 0.0
    
    # Fill holes in core foreground
    core_fg = alpha > 0.8
    core_fg_filled = ndimage.binary_fill_holes(core_fg)
    alpha = np.where(core_fg_filled, np.maximum(alpha, 1.0), alpha)
    
    # Despill: eliminate magenta spill across entire image where alpha > 0
    clean_r = r.copy()
    clean_g = g.copy()
    clean_b = b.copy()
    
    # Any residual pink fringe where min(r, b) > g
    spill = np.maximum(0.0, np.minimum(clean_r - clean_g, clean_b - clean_g))
    clean_r -= spill * 0.95
    clean_b -= spill * 0.95
    
    if despill_steam:
        # Extra steam despill: neutralize high brightness areas
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
    
    # Find bounding box and contact points
    opaque = rgba[:, :, 3] > 30
    ys, xs = np.where(opaque)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    
    # Contact point (bottom of feet)
    bot_y = int(ys.max())
    bot_xs = xs[ys >= (bot_y - 15)]
    contact_x = int(np.median(bot_xs))
    
    return Image.fromarray(rgba, 'RGBA'), bbox, [contact_x, bot_y]

im_legion, bbox1, contact1 = clean_magenta_matte('assets/production/production-07-20261003/images/09-troop-iron-melee.png')
print(f"Legionary: bbox={bbox1}, contact={contact1}")

im_walker, bbox2, contact2 = clean_magenta_matte('assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png', despill_steam=True)
print(f"Steam Walker: bbox={bbox2}, contact={contact2}")
