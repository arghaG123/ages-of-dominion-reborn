import os
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = 'C:/dev/ages-of-dominion-reborn'

def analyze_image_layout(iid):
    p = f'{ROOT}/assets/high-res/final-native2k/{iid}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    # 4 corner sample
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    bg = np.median(corners, axis=0)
    
    diff = np.sqrt(np.sum((arr - bg)**2, axis=-1))
    chroma = np.std(arr, axis=-1)
    
    # Check if magenta
    if bg[0] > 180 and bg[1] < 70 and bg[2] > 180:
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        mag_dist = np.sqrt((r - 255)**2 + g**2 + (b - 255)**2)
        fg = mag_dist > 80.0
    elif bg[0] < 70 and bg[1] < 100 and bg[2] > 80: # Blue
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        blue_excess = b - np.maximum(r, g)
        fg = blue_excess < 30.0
    elif bg[0] > 180 and bg[1] > 100 and bg[2] > 160: # Pink
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        fg = diff > 40.0
    else: # Grey / neutral
        fg = (diff > 25.0) | (chroma > 12.0)
        
    labeled, num_feats = ndimage.label(fg)
    sizes = ndimage.sum(fg, labeled, range(1, num_feats + 1))
    
    print(f"\n--- {iid} (bg={bg.astype(int).tolist()}) ---")
    if len(sizes) == 0:
        print("No foreground detected!")
        return
        
    order = np.argsort(sizes)[::-1]
    for rank, idx in enumerate(order[:6]):
        comp = labeled == (idx + 1)
        ys, xs = np.where(comp)
        x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
        aspect = (x2 - x1) / max(1, (y2 - y1))
        print(f"  Rank {rank+1}: size={sizes[idx]:7.0f} ({sizes[idx]/(w*h)*100:4.1f}%), bbox=[{x1:4d},{y1:4d},{x2:4d},{y2:4d}], aspect={aspect:.2f}")

for t in [
    'troop-bronze-ranged',
    'troop-future-ranged',
    'troop-gunpowder-heavy',
    'troop-industrial-ranged',
    'troop-medieval-ranged',
    'troop-modern-ranged',
    'hero-mount-horse',
    'hero-mount-motor-transport',
    'hero-mount-future-transport',
    'knight-mounted-master'
]:
    analyze_image_layout(t)
