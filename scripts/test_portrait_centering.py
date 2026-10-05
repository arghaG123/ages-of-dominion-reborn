import os
import glob
from PIL import Image
import numpy as np

manifest_path = "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"
import json
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

heroes_and_rivals = [
    item for item in manifest["items"]
    if item["group"] == "2K-LATER-A-HERO-32" or "rival" in item["id"]
]

print(f"Total portrait candidates to analyze: {len(heroes_and_rivals)}")

for item in heroes_and_rivals[:8]:
    name = item["id"]
    p = f"assets/high-res/final-native2k/{name}.png"
    im = Image.open(p).convert("L")
    arr = np.array(im, dtype=float)
    
    # Compute Sobel / gradient magnitude
    gy, gx = np.gradient(arr)
    grad = np.sqrt(gx**2 + gy**2)
    
    # Focus on upper 65% of image for head/face
    upper_grad = grad[:int(0.65 * arr.shape[0]), :]
    
    # Horizontal profile (sum along rows in upper part)
    h_profile = upper_grad.sum(axis=0)
    # Vertical profile (sum along columns)
    v_profile = upper_grad.sum(axis=1)
    
    # Peak positions
    peak_x = np.argmax(h_profile)
    peak_y = np.argmax(v_profile)
    
    # Centroid of top 10% highest detail
    thresh = np.percentile(upper_grad, 90)
    ys, xs = np.where(upper_grad > thresh)
    cx = int(np.mean(xs))
    cy = int(np.mean(ys))
    
    print(f"{name:32s}: cx={cx:4d}, cy={cy:4d} (img size {arr.shape})")
