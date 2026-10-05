import os
from PIL import Image
import numpy as np

# Inspect old webp vs new native 2k candidates
for i in range(1, 7):
    old_p = f"c:/dev/ages-of-dominion/public/art/rival-{i}.webp"
    new_p = f"assets/high-res/final-native2k/rival-identity-{i}.png"
    print(f"--- RIVAL {i} ---")
    if os.path.exists(old_p):
        im_old = Image.open(old_p)
        print(f"Old rival-{i}.webp: size={im_old.size}, mode={im_old.mode}")
    if os.path.exists(new_p):
        im_new = Image.open(new_p)
        print(f"New rival-identity-{i}.png: size={im_new.size}, mode={im_new.mode}")
