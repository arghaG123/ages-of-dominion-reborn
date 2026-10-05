import os
import glob
from PIL import Image
import numpy as np

os.makedirs("assets/derivatives/portraits", exist_ok=True)

# Let's inspect a few portraits to find optimal framing
test_portraits = [
    "portrait-ancient-barbarian",
    "portrait-medieval-knight",
    "portrait-powder-ranger",
    "portrait-mech-mage",
    "rival-identity-1",
    "rival-identity-5"
]

for name in test_portraits:
    img_path = f"assets/high-res/final-native2k/{name}.png"
    im = Image.open(img_path)
    # Most characters are vertically centered around y = 0.35 * H to 0.55 * H
    # A crop of 1152x1152 centered at x=1024, y=850 (clamped) captures head + shoulders + upper chest
    crop_size = 1152
    cx, cy = 1024, 850
    x1 = cx - crop_size // 2
    y1 = cy - crop_size // 2
    x2 = x1 + crop_size
    y2 = y1 + crop_size
    
    crop = im.crop((x1, y1, x2, y2)).resize((512, 512), Image.Resampling.LANCZOS)
    out_p = f"assets/derivatives/portraits/test_{name}.png"
    crop.save(out_p)
    print(f"Saved test crop {out_p}")
