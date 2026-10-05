import os
from PIL import Image
import numpy as np

ROOT = 'C:/dev/ages-of-dominion-reborn'

# Let's inspect the bottom 300 pixels of the mounts to see the rectangular floor planes
for m in ['hero-mount-horse', 'hero-mount-motor-transport', 'hero-mount-future-transport']:
    p = f'{ROOT}/assets/high-res/final-native2k/{m}.png'
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    # Check bottom 400 rows: y from 1648 to 2048
    bot = arr[1600:2048, :]
    # std of color across rows
    print(f"{m}: bot 400 mean RGB = {bot.mean(axis=(0,1)).astype(int)}, min y with floor?")
    # Find floor plane: horizontal edges or flat ground rect
    gy, gx = np.gradient(arr.mean(axis=2))
    # where are strong horizontal lines near the bottom?
    h_lines = np.where(np.abs(gy[1600:2048, :]).mean(axis=1) > 5)[0]
    print(f"  Horizontal edge rows relative to 1600: {h_lines[:10]}")

