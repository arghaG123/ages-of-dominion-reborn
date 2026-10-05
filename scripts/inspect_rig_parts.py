import os
from PIL import Image
import numpy as np
from scipy import ndimage

rig_ids = [
    "rig-source-parts-barbarian",
    "rig-source-parts-ranger",
    "rig-source-parts-knight",
    "rig-source-parts-warlock",
    "rig-source-parts-mage",
    "rig-source-parts-paladin",
    "rig-source-parts-necromancer",
    "rig-source-parts-healer"
]

print("Analyzing 8 Rig Source Sheets...")

for rig_id in rig_ids:
    p = f"assets/high-res/final-native2k/{rig_id}.png"
    im = Image.open(p)
    arr = np.array(im)
    corners = [arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]]
    # Check if magenta
    is_magenta = all((c[0] > 180 and c[1] < 70 and c[2] > 180) for c in corners[:2])
    bg_color = np.median(corners, axis=0)
    
    # Distance from background color
    dist = np.sqrt(np.sum((arr.astype(float) - bg_color.astype(float))**2, axis=-1))
    # Threshold foreground
    thresh = 35.0 if not is_magenta else 60.0
    fg_mask = dist > thresh
    
    # Connected component labeling
    # Small morphological cleanup
    cleaned_mask = ndimage.binary_opening(fg_mask, structure=np.ones((5, 5)))
    labels, num_features = ndimage.label(cleaned_mask)
    
    # Measure parts larger than min area (e.g. 500 pixels)
    parts = []
    objects = ndimage.find_objects(labels)
    for idx, sl in enumerate(objects):
        if sl is None: continue
        part_mask = (labels[sl] == (idx + 1))
        area = part_mask.sum()
        if area > 1000: # Filter small noise
            ymin, ymax = sl[0].start, sl[0].stop
            xmin, xmax = sl[1].start, sl[1].stop
            parts.append({
                "part_idx": len(parts) + 1,
                "bbox": [int(xmin), int(ymin), int(xmax), int(ymax)],
                "width": int(xmax - xmin),
                "height": int(ymax - ymin),
                "area": int(area)
            })
    
    print(f"[{rig_id:28s}]: BG={bg_color.astype(int).tolist()} ({'magenta' if is_magenta else 'grey/scenic'}), Found {len(parts)} parts")
    for pt in parts[:6]:
        print(f"   part {pt['part_idx']:2d}: bbox={pt['bbox']}, w={pt['width']:3d}, h={pt['height']:3d}, area={pt['area']:6d}")
