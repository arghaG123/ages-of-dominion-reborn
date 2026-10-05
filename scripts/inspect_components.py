import os
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'

targets = [
    'troop-bronze-ranged',
    'troop-future-ranged',
    'troop-gunpowder-heavy',
    'troop-industrial-ranged',
    'troop-medieval-ranged',
    'troop-modern-ranged',
    'hero-mount-horse',
    'hero-mount-future-transport',
    'hero-mount-motor-transport',
    'knight-mounted-master'
]

for t in targets:
    p = f'{ROOT}/assets/high-res/final-native2k/{t}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    corners = np.array([arr[10, 10], arr[10, -11], arr[-11, 10], arr[-11, -11]])
    bg = np.median(corners, axis=0)
    
    # Distance to bg
    dist = np.sqrt(np.sum((arr.astype(float) - bg)**2, axis=-1))
    chroma = np.std(arr.astype(float), axis=-1)
    fg_mask = (dist > 30.0) | (chroma > 15.0)
    
    # Label connected components
    labeled, num_features = ndimage.label(fg_mask)
    sizes = ndimage.sum(fg_mask, labeled, range(1, num_features + 1))
    
    print(f"\n=== {t} ===")
    print(f"Num features: {num_features}, Max size: {sizes.max() if len(sizes) > 0 else 0}")
    # Show largest 5 components with bounding boxes
    if len(sizes) > 0:
        top_idx = np.argsort(sizes)[::-1][:5]
        for idx in top_idx:
            comp_mask = labeled == (idx + 1)
            ys, xs = np.where(comp_mask)
            print(f"  Component {idx+1}: size={sizes[idx]:7.0f}, bbox=[{xs.min()},{ys.min()},{xs.max()},{ys.max()}]")
