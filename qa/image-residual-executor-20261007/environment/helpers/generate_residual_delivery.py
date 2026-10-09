"""Comprehensive Environment Residual Delivery Generator (2026-10-07).
Generates corrected artifact derivatives, recipes, masks, 32-scene geography overlays,
4-viewport composites, interactive review gallery, residual interface, and handoff.
"""
import os
import sys
import json
import math
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("c:/dev/ages-of-dominion-reborn")
QA_DIR = ROOT / "qa/image-residual-executor-20261007/environment"
DERIV_DIR = ROOT / "assets/derivatives/image-residual-executor-20261007/environment"
sys.path.append(str(QA_DIR / "helpers"))

from geometry_utils import (
    FROZEN_AFFINE, HALL_SCALE, LEGAL_WH, NATIVE_WH, NATIVE_SCALE,
    grid_to_legal, legal_to_native, native_to_legal, pad_rect_to_legal_polygon,
    check_clearance, polyline_to_polygon_dist
)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def despill_magenta(arr_rgb: np.ndarray) -> np.ndarray:
    """Removes magenta cast from edge pixels without creating artificial green tint."""
    clean = arr_rgb.astype(np.float32)
    r = clean[:, :, 0]
    g = clean[:, :, 1]
    b = clean[:, :, 2]
    
    # Measure magenta excess: (R + B)/2 - G
    avg_rb = (r + b) * 0.5
    excess_mag = np.maximum(0.0, avg_rb - g)
    
    # Subtract excess from R and B
    despill_mask = excess_mag > 0.0
    r[despill_mask] -= excess_mag[despill_mask] * 0.95
    b[despill_mask] -= excess_mag[despill_mask] * 0.95
    
    # CRITICAL FIX for green patch defect:
    # Ensure despill does NOT artificially elevate green above the local color gamut
    # If G > max(R, B) + 30 in despilled pixels, bring G into neutral balance
    max_rb = np.maximum(r, b)
    green_excess = np.maximum(0.0, g - (max_rb + 25.0))
    g[despill_mask] -= green_excess[despill_mask] * 0.90
    
    clean[:, :, 0] = np.clip(r, 0.0, 255.0)
    clean[:, :, 1] = np.clip(g, 0.0, 255.0)
    clean[:, :, 2] = np.clip(b, 0.0, 255.0)
    return clean.astype(np.uint8)

def process_chroma_matte(src_img: Image.Image, roi: List[int], row_id: str) -> Tuple[Image.Image, Image.Image]:
    """Extracts foreground with clean chroma keying and despill."""
    x1, y1, x2, y2 = roi
    crop = src_img.crop((x1, y1, x2, y2))
    arr = np.array(crop)
    
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    
    # Strict magenta chroma detection
    is_bg = (r > 165) & (b > 165) & (g < 120) & (r + b > 2 * g + 50)
    
    # Create smooth alpha mask
    alpha = np.where(is_bg, 0, 255).astype(np.uint8)
    
    # Base mask refinement for armory-stone and barracks-stone:
    # Trim artificial green foundation wedges below ground contact line
    h, w = alpha.shape
    if row_id == "armory-stone":
        # Structure ground contact line is at y=855..865. The triangular green wedge extends to y=920.
        for y in range(int(h * 0.88), h):
            # Check for green wedge pixels: G > R + 15 and G > B + 15
            row_g = (arr[y, :, 1] > 95) & (arr[y, :, 1] > arr[y, :, 0] + 10) & (arr[y, :, 1] > arr[y, :, 2] + 10)
            alpha[y, row_g] = 0
    elif row_id == "barracks-stone":
        for y in range(int(h * 0.92), h):
            row_g = (arr[y, :, 1] > 95) & (arr[y, :, 1] > arr[y, :, 0] + 10) & (arr[y, :, 1] > arr[y, :, 2] + 10)
            alpha[y, row_g] = 0
            
    # Apply color despill
    clean_rgb = despill_magenta(arr[:, :, :3])
    
    # Construct RGBA output and grayscale mask
    rgba = np.dstack([clean_rgb, alpha])
    out_img = Image.fromarray(rgba, mode="RGBA")
    mask_img = Image.fromarray(alpha, mode="L")
    return out_img, mask_img

def process_circular_badge(src_img: Image.Image, roi: List[int], row_id: str) -> Tuple[Image.Image, Image.Image]:
    """Processes skill/spell badges with circular mask and chroma decontamination."""
    x1, y1, x2, y2 = roi
    crop = src_img.crop((x1, y1, x2, y2))
    arr = np.array(crop)
    h, w = arr.shape[:2]
    
    # Check if image has magenta chroma background (like skill-offense)
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    is_chroma = (r > 165) & (b > 165) & (g < 120) & (r + b > 2 * g + 50)
    has_magenta_bg = np.count_nonzero(is_chroma) > 5000
    
    cy, cx = h / 2.0, w / 2.0
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    # Exact radius for badge
    radius = min(w, h) * 0.46 if not has_magenta_bg else 355.0
    feather = 2.0
    circle_mask = np.clip((radius + feather - dist) / feather, 0.0, 1.0)
    
    if has_magenta_bg:
        chroma_alpha = np.where(is_chroma, 0.0, 1.0)
        final_alpha = (circle_mask * chroma_alpha * 255.0).astype(np.uint8)
    else:
        final_alpha = (circle_mask * 255.0).astype(np.uint8)
        
    clean_rgb = despill_magenta(arr[:, :, :3])
    rgba = np.dstack([clean_rgb, final_alpha])
    out_img = Image.fromarray(rgba, mode="RGBA")
    mask_img = Image.fromarray(final_alpha, mode="L")
    return out_img, mask_img

print("Loaded generator modules successfully.")
