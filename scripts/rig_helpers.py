import os, json, hashlib
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
OUTPUT_RIG_DIR = f'{ROOT}/assets/derivatives/rigs/v3'
QA_RIG_DIR = f'{ROOT}/qa/image-v3-repair-20261004/rigs'

os.makedirs(OUTPUT_RIG_DIR, exist_ok=True)
os.makedirs(QA_RIG_DIR, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def despill_magenta(arr):
    r, g, b = arr[:, :, 0].astype(float), arr[:, :, 1].astype(float), arr[:, :, 2].astype(float)
    mag_dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    alpha = np.clip((mag_dist - 65.0) / 75.0, 0.0, 1.0)
    spill = np.maximum(0.0, np.minimum(r - g, b - g))
    clean_r = np.clip(r - spill * 0.95, 0, 255).astype(np.uint8)
    clean_b = np.clip(b - spill * 0.95, 0, 255).astype(np.uint8)
    clean_g = np.clip(g, 0, 255).astype(np.uint8)
    clean_a = (alpha * 255.0).astype(np.uint8)
    return clean_r, clean_g, clean_b, clean_a

def despill_grey(arr, bg):
    diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=-1))
    chroma = np.std(arr.astype(float), axis=-1)
    cand_bg = (diff < 28.0) & (chroma < 15.0)
    
    # Distance transform to background
    fg_mask = ~cand_bg
    fg_mask = ndimage.binary_closing(fg_mask, structure=np.ones((5, 5)))
    dist_to_bg = ndimage.distance_transform_edt(fg_mask)
    alpha = np.clip(dist_to_bg / 2.2, 0.0, 1.0)
    
    clean_r = arr[:, :, 0]
    clean_g = arr[:, :, 1]
    clean_b = arr[:, :, 2]
    clean_a = (alpha * 255.0).astype(np.uint8)
    return clean_r, clean_g, clean_b, clean_a

def despill_olive(arr, bg=np.array([145.0, 178.0, 105.0])):
    diff = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=-1))
    # Also detect outer magenta boundary if present
    r, g, b = arr[:, :, 0].astype(float), arr[:, :, 1].astype(float), arr[:, :, 2].astype(float)
    is_mag = (r > 175) & (g < 75) & (b > 175)
    
    cand_bg = (diff < 32.0) | is_mag
    fg_mask = ~cand_bg
    fg_mask = ndimage.binary_closing(fg_mask, structure=np.ones((5, 5)))
    dist_to_bg = ndimage.distance_transform_edt(fg_mask)
    alpha = np.clip(dist_to_bg / 2.2, 0.0, 1.0)
    
    # Despill olive green tint from edges
    spill = np.maximum(0.0, g - (r + b) / 2.0)
    clean_g = np.clip(g - spill * 0.4, 0, 255).astype(np.uint8)
    clean_r = r.astype(np.uint8)
    clean_b = b.astype(np.uint8)
    clean_a = (alpha * 255.0).astype(np.uint8)
    return clean_r, clean_g, clean_b, clean_a

def extract_part(src_arr, bbox, despill_fn, pad=4):
    x1, y1, x2, y2 = bbox
    H, W, _ = src_arr.shape
    x1_pad = max(0, x1 - pad)
    y1_pad = max(0, y1 - pad)
    x2_pad = min(W, x2 + pad)
    y2_pad = min(H, y2 + pad)
    
    crop = src_arr[y1_pad:y2_pad, x1_pad:x2_pad]
    cr, cg, cb, ca = despill_fn(crop)
    
    rgba = np.dstack([cr, cg, cb, ca])
    return rgba, [x1_pad, y1_pad, x2_pad, y2_pad]

print("Rig processing framework loaded.")
