import os
from PIL import Image
import numpy as np

composite_troops = [
    "troop-iron-melee",
    "troop-industrial-heavy",
    "troop-bronze-ranged",
    "troop-gunpowder-heavy",
    "troop-modern-melee",
    "troop-modern-ranged",
    "troop-future-ranged"
]

for name in composite_troops:
    p = f"assets/high-res/final-native2k/{name}.png"
    im = Image.open(p)
    arr = np.array(im)
    print(f"=== {name} ===")
    print(f"Size: {im.size}, Mode: {im.mode}")
    print(f"Corners: TL={arr[5,5].tolist()}, TR={arr[5,-6].tolist()}, BL={arr[-6,5].tolist()}, BR={arr[-6,-6].tolist()}")
    print(f"Mean RGB: {arr.mean(axis=(0,1)).tolist()}")
    print(f"Min RGB: {arr.min(axis=(0,1)).tolist()}, Max RGB: {arr.max(axis=(0,1)).tolist()}")
