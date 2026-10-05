import os
from PIL import Image
import numpy as np

def extract_magenta_alpha(img_path, out_path):
    im = Image.open(img_path).convert("RGB")
    arr = np.array(im, dtype=float)
    
    # Magenta is high R, low G, high B
    # Distance in normalized color space
    # Key color ~ (255, 0, 250)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    
    # Magenta metric: high (r + b)/2 - g
    magenta_intensity = (r + b) / 2.0 - g
    
    # Distance to pure magenta (255, 0, 255)
    dist = np.sqrt((r - 255)**2 + (g - 0)**2 + (b - 255)**2)
    
    # Smooth alpha ramp
    # Below 60 is definitely magenta background (alpha = 0)
    # Above 140 is definitely foreground (alpha = 255)
    alpha = np.clip((dist - 60.0) / 70.0, 0.0, 1.0)
    
    # Defringe: remove magenta spill on edges where alpha < 1.0
    spill = np.clip((magenta_intensity - 30.0) / 100.0, 0.0, 1.0)
    # On fringe pixels, blend R and B towards G
    fringe_mask = (alpha > 0.05) & (alpha < 0.95)
    if np.any(fringe_mask):
        arr_defringed = arr.copy()
        # Reduce magenta tint
        arr_defringed[:, :, 0] = np.where(fringe_mask, np.minimum(r, g * 1.4 + 20), r)
        arr_defringed[:, :, 2] = np.where(fringe_mask, np.minimum(b, g * 1.4 + 20), b)
    else:
        arr_defringed = arr
        
    rgba = np.dstack([np.clip(arr_defringed, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    out_im = Image.fromarray(rgba, "RGBA")
    
    # Bounding box of non-transparent content
    alpha_mask = rgba[:, :, 3] > 20
    if np.any(alpha_mask):
        ys, xs = np.where(alpha_mask)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    else:
        bbox = [0, 0, im.width, im.height]
        
    out_im.save(out_path)
    print(f"Magenta extracted: {out_path}, bbox={bbox}, opaque_pixels={np.sum(alpha_mask)}")
    return bbox

os.makedirs("assets/derivatives/test", exist_ok=True)
extract_magenta_alpha("assets/high-res/final-native2k/troop-stone-melee.png", "assets/derivatives/test/test_stone_melee.png")
extract_magenta_alpha("assets/production/production-07-20261003/images/09-troop-iron-melee.png", "assets/derivatives/test/test_iron_melee_sub.png")
extract_magenta_alpha("assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png", "assets/derivatives/test/test_ind_heavy_sub.png")
