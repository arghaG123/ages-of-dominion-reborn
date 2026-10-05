import os
from PIL import Image
import numpy as np
from scipy import ndimage

def extract_grey_alpha(img_path, out_path):
    im = Image.open(img_path).convert("RGB")
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    # Sample corners
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    
    # Distance from bg
    dist = np.sqrt(np.sum((arr - bg)**2, axis=-1))
    chroma = np.std(arr, axis=-1)
    
    # A pixel is candidate background if close to bg in color and low chroma
    # E.g. dist < 22 and chroma < 10
    cand_bg = (dist < 25.0) & (chroma < 12.0)
    
    # Seed from borders
    border_mask = np.zeros((h, w), dtype=bool)
    border_mask[0:3, :] = True
    border_mask[-3:, :] = True
    border_mask[:, 0:3] = True
    border_mask[:, -3:] = True
    
    seed_bg = cand_bg & border_mask
    
    # Flood fill / connected component from border seeds
    # Label connected components of cand_bg
    labeled, num_features = ndimage.label(cand_bg)
    border_labels = np.unique(labeled[seed_bg])
    border_labels = border_labels[border_labels > 0]
    
    # Background mask is union of connected components touching the border seeds
    bg_mask = np.isin(labeled, border_labels)
    
    # Foreground is inverse of bg_mask
    fg_mask = ~bg_mask
    
    # Clean small isolated noise
    fg_mask = ndimage.binary_closing(fg_mask, structure=np.ones((5, 5)))
    fg_mask = ndimage.binary_fill_holes(fg_mask)
    
    # Edge feathering (soft transition)
    dist_to_bg = ndimage.distance_transform_edt(fg_mask)
    alpha = np.clip(dist_to_bg / 2.5, 0.0, 1.0)
    
    rgba = np.dstack([np.clip(arr, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    out_im = Image.fromarray(rgba, "RGBA")
    
    # Bounding box of foreground
    alpha_mask = rgba[:, :, 3] > 20
    if np.any(alpha_mask):
        ys, xs = np.where(alpha_mask)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    else:
        bbox = [0, 0, w, h]
        
    out_im.save(out_path)
    print(f"Grey extracted: {out_path}, bbox={bbox}, opaque_pixels={np.sum(alpha_mask)}")
    return bbox

extract_grey_alpha("assets/high-res/final-native2k/troop-bronze-melee.png", "assets/derivatives/test/test_bronze_melee.png")
extract_grey_alpha("assets/high-res/final-native2k/hero-mount-horse.png", "assets/derivatives/test/test_mount_horse.png")
extract_grey_alpha("assets/high-res/final-native2k/troop-future-melee.png", "assets/derivatives/test/test_future_melee.png")
