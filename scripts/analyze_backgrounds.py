import os
import glob
from PIL import Image
import numpy as np

final_dir = "assets/high-res/final-native2k"
files = sorted(glob.glob(os.path.join(final_dir, "*.png")))

print(f"Analyzing {len(files)} candidate images...")

bg_types = {}

for f in files:
    name = os.path.basename(f)
    img = Image.open(f)
    arr = np.array(img)
    # Sample corners (top-left, top-right, bottom-left, bottom-right)
    corners = [
        arr[10, 10],
        arr[10, 2037],
        arr[2037, 10],
        arr[2037, 2037]
    ]
    # Check if magenta (R > 200, G < 60, B > 200)
    is_magenta = all((c[0] > 180 and c[1] < 70 and c[2] > 180) for c in corners[:2])
    # Check if grey (R, G, B close to each other, e.g. std < 15, and brightness 50..220)
    is_grey = all(np.std(c) < 15 and 40 < np.mean(c) < 220 for c in corners[:2])
    
    cat = "scenic/complex"
    if is_magenta:
        cat = "magenta"
    elif is_grey:
        cat = "grey"
    
    bg_types[name] = (cat, corners[0].tolist())

from collections import Counter
counts = Counter(v[0] for v in bg_types.values())
print("Background distribution:", counts)

for name, (cat, c) in bg_types.items():
    if "troop" in name or "mount" in name or "rig" in name:
        print(f"{name:35s}: {cat:15s} corner={c}")
