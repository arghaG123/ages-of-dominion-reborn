import os
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'
rig_ids = [
    'rig-source-parts-knight',
    'rig-source-parts-ranger',
    'rig-source-parts-warlock',
    'rig-source-parts-mage',
    'rig-source-parts-paladin',
    'rig-source-parts-barbarian',
    'rig-source-parts-necromancer',
    'rig-source-parts-healer'
]

for rid in rig_ids:
    p = f'{ROOT}/assets/high-res/final-native2k/{rid}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    
    diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
    chroma = np.std(arr, axis=-1)
    
    # Check if magenta
    is_magenta = (bg[0] > 180 and bg[1] < 70 and bg[2] > 180)
    thresh = 50.0 if is_magenta else 25.0
    fg = diff > thresh
    
    labeled, num_features = ndimage.label(fg)
    sizes = ndimage.sum(fg, labeled, range(1, num_features + 1))
    
    print(f"\n==========================================")
    print(f"{rid} (bg={bg.astype(int).tolist()} magenta={is_magenta}):")
    print(f"Total features detected: {num_features}")
    
    # Filter features by size > 3000 pixels (actual anatomical pieces)
    large_indices = np.where(sizes > 3000)[0]
    print(f"Significant pieces (>3000 px): {len(large_indices)}")
    
    for idx in sorted(large_indices, key=lambda i: sizes[i], reverse=True)[:15]:
        comp = labeled == (idx + 1)
        ys, xs = np.where(comp)
        x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
        pw = x2 - x1
        ph = y2 - y1
        print(f"  Part {idx+1:2d}: size={sizes[idx]:7.0f}, bbox=[{x1:4d},{y1:4d},{x2:4d},{y2:4d}] ({pw}x{ph})")
